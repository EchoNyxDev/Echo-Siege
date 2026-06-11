import discord
from discord.ext import commands
import sqlite3
import random
import os
import sys
import json
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.enemies import ENEMIES
    from data.equipamentos import EQUIPAMENTOS
    from utils.combat import simular_combate_tatico
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
    from utils.skills import get_hero_skill_ids
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.rewards import average_party_level, scale_combat_rewards
    from utils.equipment import get_equipment_bonus
    from utils.affinity import apply_affinity_bonus
    from utils.player_bonuses import apply_reward_bonuses, apply_battle_hp_bonus
except ModuleNotFoundError:
    HEROES, ENEMIES, EQUIPAMENTOS = {}, {}, {}
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []
    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}
    def apply_affinity_bonus(party_data, heroes):
        return party_data
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0):
        return gold, xp
    def apply_battle_hp_bonus(cursor, user_id, party_data):
        return party_data
    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {"hp": 100, "atk": 10, "matk": 10, "def": 5, "spd": 10, "crt": 5, "level": level}
    def normalize_class(value):
        return str(value or "neutro").lower()
    def average_party_level(party):
        return 1
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50):
        return gold, xp

COOLDOWN_HORAS = 2
COOLDOWN_SEGUNDOS = COOLDOWN_HORAS * 3600


def cortar_texto(texto, limite=1000):
    texto = str(texto or "")
    return texto if len(texto) <= limite else texto[: limite - 3] + "..."


def carregar_aventuras():
    caminho = os.path.join(root_dir, "data", "adventures.json")
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def puxar_party_para_combate(user_id, user_name):
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
    p_data = cursor.fetchone()
    
    if not p_data or not p_data[0]:
        conn.close()
        return None
        
    cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
    team = cursor.fetchone()
    time_ids = [p_data[0]] + [x for x in (team if team else []) if x is not None]
    
    party_data = []
    for hid in time_ids:
        cursor.execute("SELECT hero_id, stars, level, equip_atk, equip_def, equip_livre FROM heroes WHERE id = ?", (int(hid),))
        hero = cursor.fetchone()
        if hero:
            h_id, stars, level, e_atk, e_def, e_livre = hero
            h_data = HEROES.get(h_id, {})
            
            equipment_bonuses = []
            for eq_name in [e_atk, e_def, e_livre]:
                if eq_name and eq_name in EQUIPAMENTOS:
                    equipment_bonuses.append(get_equipment_bonus(cursor, user_id, eq_name, EQUIPAMENTOS))

            stats = calculate_hero_stats(h_data, stars, level, equipment_bonuses)
            hp, atk, matk = stats["hp"], stats["atk"], stats["matk"]
            df, spd, crt = stats["def"], stats["spd"], stats["crt"]
            cl = normalize_class(h_data.get("classe", "neutro"))

            party_data.append({
                "id": str(hid), "hero_id": h_id, "nome": f"{h_data.get('nome', 'Herói')} ({user_name})", "classe": cl, "level": level,
                "hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt,
                "stats": {"hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt, "level": level},
                "habilidades": get_hero_skill_ids(h_data, stars, h_data.get("raridade", 0))
            })
            
    party_data = apply_affinity_bonus(party_data, HEROES)
    party_data = apply_battle_hp_bonus(cursor, user_id, party_data)
    conn.commit()
    conn.close()
    return party_data

class BotaoAventura(discord.ui.Button):
    def __init__(self, label, emoji, proximo_nodo, view_ref):
        super().__init__(style=discord.ButtonStyle.primary, label=cortar_texto(label, 76), emoji=emoji)
        self.proximo_nodo = proximo_nodo
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        await self.view_ref.ir_para_nodo(interaction, self.proximo_nodo)

class BotaoCombate(discord.ui.Button):
    def __init__(self, view_ref):
        super().__init__(style=discord.ButtonStyle.danger, label="Iniciar Combate!", emoji="⚔️")
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        await self.view_ref.resolver_combate(interaction)

class AdventureSession(discord.ui.View):
    def __init__(self, ctx, aventura_id, aventura_data, party_data):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.user = ctx.author
        self.aventura_id = aventura_id
        self.aventura = aventura_data
        self.party_data = party_data
        self.progress_level = average_party_level(party_data)
        self.nodos = aventura_data.get("nodos", {})
        self.nodo_atual_id = "start"
        self.passos = 0
        self.moral = 100
        self.perigo = 0
        self.diario = ["Contrato aceito. O TutoriUAU chamou isso de coragem; eu chamo de falta de opção."]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Esta não é a sua jornada, intrometido.", ephemeral=True)
            return False
        return True

    def fechar_contrato_na_guilda(self, cursor, uid):
        cursor.execute("SELECT m1_id, m2_id, m3_id FROM daily_quests WHERE user_id = ?", (uid,))
        row = cursor.fetchone()
        if row:
            m1, m2, m3 = row
            if self.aventura_id == m1: cursor.execute("UPDATE daily_quests SET m1_status = 1, active_mission = NULL WHERE user_id = ?", (uid,))
            elif self.aventura_id == m2: cursor.execute("UPDATE daily_quests SET m2_status = 1, active_mission = NULL WHERE user_id = ?", (uid,))
            elif self.aventura_id == m3: cursor.execute("UPDATE daily_quests SET m3_status = 1, active_mission = NULL WHERE user_id = ?", (uid,))

    def salvar_cooldown_e_loot(self, ouro, xp):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        uid = str(self.user.id)
        ouro, xp = apply_reward_bonuses(cursor, uid, ouro, xp)
        
        cursor.execute("UPDATE players SET last_adventure = ?, gold = gold + ? WHERE user_id = ?", (time.time(), ouro, uid))
        if xp > 0:
            dar_xp_jogador(cursor, uid, xp)
            for h in self.party_data:
                dar_xp_heroi(cursor, int(h["id"]), xp)
                
        self.fechar_contrato_na_guilda(cursor, uid)
        conn.commit()
        conn.close()

    def _estado_jornada(self):
        return (
            f"Moral: **{self.moral}/100** | Perigo: **{self.perigo}/100** | Passos: **{self.passos}**\n"
            f"Diário: {cortar_texto(self.diario[-1], 220)}"
        )

    def _evento_aleatorio(self):
        if random.random() > 0.38:
            return None
        eventos = [
            ("Uma névoa estranha cobriu a estrada. Perigo +8.", -2, 8),
            ("A party encontrou um marco antigo e descansou dois minutos. Moral +7.", 7, -2),
            ("Um mercador suspeito indicou um atalho. Perigo +5, moral +3. Péssimo, mas eficiente.", 3, 5),
            ("TutoriUAU apareceu numa plaquinha dizendo 'não toque'. Vocês tocaram. Perigo +6.", -3, 6),
            ("Um viajante agradecido dividiu provisões. Moral +5.", 5, 0),
        ]
        texto, moral_delta, perigo_delta = random.choice(eventos)
        self.moral = max(0, min(100, self.moral + moral_delta))
        self.perigo = max(0, min(100, self.perigo + perigo_delta))
        self.diario.append(texto)
        return texto

    async def resolver_combate(self, interaction: discord.Interaction):
        nodo_atual = self.nodos[self.nodo_atual_id]
        inimigos_ids = nodo_atual.get("inimigos", [])
        
        team_b = []
        for idx, i_id in enumerate(inimigos_ids):
            ini_base = ENEMIES.get(i_id, {})
            lvl_multi = 1.15 + (self.perigo / 180) + (self.passos * 0.04)
            b_stats = {
                "hp": int(ini_base.get("hp", 200) * lvl_multi),
                "atk": int(ini_base.get("atk", 30) * lvl_multi),
                "def": int(ini_base.get("def", 10) * lvl_multi),
                "matk": int(ini_base.get("matk", 0) * lvl_multi),
                "spd": ini_base.get("spd", 15), "crt": 5, 
                "habilidades": [ini_base.get("habilidade")] if ini_base.get("habilidade") else [],
                "classe": ini_base.get("tipo", "comum")
            }
            team_b.append({
                "id": f"B{idx}", "nome": ini_base.get("nome", "Monstro"), "classe": "comum",
                "hp": b_stats["hp"], "stats": b_stats, "habilidades": b_stats["habilidades"]
            })

        await interaction.response.edit_message(content="⚔️ **O combate começou! A vida pisca diante dos teus olhos...**", embed=None, view=None)
        
        vitoria, log_batalha = simular_combate_tatico(self.party_data, team_b)

        if vitoria:
            self.moral = min(100, self.moral + 8)
            self.perigo = max(0, self.perigo - 6)
            self.diario.append("Combate vencido. A party respirou como quem fingiu que estava tudo sob controle.")
        else:
            self.moral = max(0, self.moral - 18)
            self.perigo = min(100, self.perigo + 10)
            self.diario.append("Combate perdido. TutoriUAU anotou 'aprendizado' para não escrever 'tragédia'.")

        embed = discord.Embed(title="⚔️ Fim do Combate", description=self._estado_jornada(), color=discord.Color.green() if vitoria else discord.Color.red())
        embed.add_field(name="📜 Log da Batalha", value=cortar_texto(log_batalha, 1000), inline=False)
        
        self.clear_items()
        proximo = nodo_atual.get("win_next") if vitoria else nodo_atual.get("lose_next")
        
        if proximo and proximo in self.nodos:
            self.add_item(BotaoAventura("Continuar Jornada", "➡️", proximo, self))
            await interaction.message.edit(embed=embed, view=self)
        else:
            embed.set_footer(text="A aventura terminou de forma trágica ou mal programada.")
            self.salvar_cooldown_e_loot(0, 0)
            await interaction.message.edit(embed=embed, view=None)

    async def ir_para_nodo(self, interaction, nodo_id):
        self.nodo_atual_id = nodo_id
        nodo = self.nodos.get(nodo_id)
        self.clear_items()
        if nodo_id != "start":
            self.passos += 1
            evento = self._evento_aleatorio()
        else:
            evento = None

        tipo = nodo.get("tipo", "historia")
        embed = discord.Embed(title=f"🏕️ {self.aventura['nome']}", description=cortar_texto(nodo.get("texto", "..."), 850), color=discord.Color.dark_green())
        embed.add_field(name="Estado da Jornada", value=self._estado_jornada(), inline=False)
        if evento:
            embed.add_field(name="Evento de Caminho", value=evento, inline=False)

        if tipo == "historia":
            for op in nodo.get("opcoes", []):
                self.add_item(BotaoAventura(op.get("label", "Seguir"), op.get("emoji", "🔘"), op.get("next"), self))

        elif tipo == "combate":
            embed.color = discord.Color.red()
            embed.set_footer(text="Um confronto é inevitável. Que os deuses te ajudem.")
            self.add_item(BotaoCombate(self))

        elif tipo == "recompensa":
            embed.color = discord.Color.gold()
            performance = 1 + max(0, self.moral - 50) / 400
            risco_bonus = 1 + min(0.20, self.perigo / 500)
            ouro = int(nodo.get("gold", 0) * performance * risco_bonus)
            xp = int(nodo.get("xp", 0) * performance * risco_bonus)
            ouro, xp = scale_combat_rewards(ouro, xp, self.progress_level)
            
            recompensas_str = ""
            if ouro > 0: recompensas_str += f"💰 **{ouro} Gold**\n"
            if xp > 0: recompensas_str += f"⭐ **{xp} XP**\n"
            if not recompensas_str: recompensas_str = "Apenas poeira e o alívio de estar vivo."
            
            embed.add_field(name="Loot Obtido", value=recompensas_str, inline=False)
            embed.set_footer(text="Contrato fechado! Volte ao quadro da guilda (echo work) ou espere o cooldown (echo cd).")
            self.salvar_cooldown_e_loot(ouro, xp)

        try: await interaction.response.edit_message(embed=embed, view=self if tipo != "recompensa" else None)
        except: await interaction.message.edit(embed=embed, view=self if tipo != "recompensa" else None)

class AventuraRPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aventuras = carregar_aventuras()

    @commands.command(name="adventure", aliases=["adv", "aventura"])
    async def aventura_cmd(self, ctx):
        if not self.aventuras:
            return await ctx.send("❌ O Mestre de Jogo perdeu o grimório (`adventures.json` está vazio ou faltando).")

        uid = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        # Verifica se o cooldown permite viajar
        cursor.execute("SELECT last_adventure FROM players WHERE user_id = ?", (uid,))
        p_data = cursor.fetchone()
        
        tempo_passado = time.time() - (p_data[0] or 0)
        if tempo_passado < COOLDOWN_SEGUNDOS:
            conn.close()
            restante_m = int((COOLDOWN_SEGUNDOS - tempo_passado) / 60)
            return await ctx.send(f"⏳ Seus heróis ainda estão cuidando das feridas da última viagem. Aguarde **{restante_m} minutos**.")

        # Verifica se TEM UMA MISSÃO do quadro ativa
        cursor.execute("SELECT active_mission FROM daily_quests WHERE user_id = ?", (uid,))
        q_data = cursor.fetchone()
        conn.close()

        if not q_data or not q_data[0]:
            return await ctx.send("❌ **TutoriUAU:** Tu queres ir fazer o quê lá fora sem contrato? Vai ao `echo work` e assina um dos papéis antes de sair andando sem rumo.")

        missao_ativa_id = q_data[0]
        aventura_escolhida = self.aventuras.get(missao_ativa_id)

        if not aventura_escolhida:
            return await ctx.send("❌ Erro no contrato. Parece que o dev apagou esta aventura do arquivo JSON.")

        party_data = puxar_party_para_combate(ctx.author.id, ctx.author.name)
        if not party_data:
            return await ctx.send("❌ Precisas de um Líder de Esquadrão para sair em aventura (`echo main <ID>`).")

        view = AdventureSession(ctx, missao_ativa_id, aventura_escolhida, party_data)
        
        embed = discord.Embed(
            title=f"🏕️ Iniciando Contrato: {aventura_escolhida['nome']}",
            description="Os portões de Lugnica se fecham atrás de você. Seu destino foi traçado.",
            color=discord.Color.dark_green()
        )
        embed.set_footer(text="A gerar o mapa mundi...")
        
        msg = await ctx.send(embed=embed, view=view)
        
        class DummyInteraction:
            def __init__(self, m): self.message = m; self.response = self
            async def edit_message(self, **kwargs): await self.message.edit(**kwargs)
            
        await view.ir_para_nodo(DummyInteraction(msg), "start")

async def setup(bot):
    await bot.add_cog(AventuraRPG(bot))
