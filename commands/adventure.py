import discord
from discord.ext import commands
import sqlite3
import random
import os
import sys
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
    from utils.rewards import scale_combat_rewards
    from utils.adventure_catalog import load_adventure_catalog
    from utils.affinity import apply_affinity_bonus
    from utils.equipment import get_equipment_bonus
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.player_bonuses import apply_battle_hp_bonus
    from utils.skills import get_hero_skill_ids
except ModuleNotFoundError:
    HEROES, ENEMIES, EQUIPAMENTOS = {}, {}, {}
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50): return gold, xp
    def load_adventure_catalog(): return {}
    def apply_affinity_bonus(party_data, heroes): return party_data
    def get_equipment_bonus(cursor, user_id, item_name, equipamentos): return {}
    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {
            "hp": hero_data.get("hp", 100), "atk": hero_data.get("atk", 10),
            "matk": hero_data.get("matk", 10), "def": hero_data.get("def", 5),
            "spd": hero_data.get("spd", 10), "crt": hero_data.get("crt", 5),
        }
    def normalize_class(value): return str(value or "neutro").lower()
    def apply_battle_hp_bonus(cursor, user_id, party_data): return party_data
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        skill_id = hero_data.get("habilidade")
        return [skill_id] if skill_id else []

COOLDOWN_HORAS = 2
COOLDOWN_SEGUNDOS = COOLDOWN_HORAS * 3600

def cortar_texto(texto, limite=1000):
    texto = str(texto or "")
    return texto if len(texto) <= limite else texto[: limite - 3] + "..."

def carregar_aventuras():
    return load_adventure_catalog()


def _combat_power(member):
    stats = member.get("stats", member)
    hp = float(stats.get("hp", member.get("hp", 1)) or 1)
    atk = float(stats.get("atk", member.get("atk", 0)) or 0)
    matk = float(stats.get("matk", member.get("matk", 0)) or 0)
    defense = float(stats.get("def", member.get("def", 0)) or 0)
    speed = float(stats.get("spd", member.get("spd", 0)) or 0)
    critical = float(stats.get("crt", member.get("crt", 0)) or 0)
    return hp * 0.45 + max(atk, matk) * 3 + defense * 2 + speed + critical


def balance_adventure_encounter(enemies, party, tier):
    if not enemies or not party:
        return enemies

    party_power = sum(_combat_power(member) for member in party)
    enemy_power = sum(_combat_power(member) for member in enemies)
    target_ratio = {1: 0.82, 2: 0.96, 3: 1.08, 4: 1.22}.get(int(tier or 1), 0.96)
    target_power = party_power * target_ratio * random.uniform(0.94, 1.06)
    scale = max(0.25, min(2.25, target_power / max(1.0, enemy_power)))

    for enemy in enemies:
        stats = enemy["stats"]
        for stat in ("hp", "atk", "matk", "def"):
            minimum = 1 if stat == "hp" else 0
            stats[stat] = max(minimum, int(round(stats.get(stat, 0) * scale)))
        enemy.update({key: stats[key] for key in ("hp", "atk", "matk", "def")})

    return enemies

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
                    equipment_bonuses.append(
                        get_equipment_bonus(cursor, user_id, eq_name, EQUIPAMENTOS)
                    )

            stats = calculate_hero_stats(h_data, stars, level, equipment_bonuses)
            hp, atk, matk = stats["hp"], stats["atk"], stats["matk"]
            df, spd, crt = stats["def"], stats["spd"], stats["crt"]
            cl = normalize_class(h_data.get("classe", "neutro"))
            skills = get_hero_skill_ids(h_data, stars, h_data.get("raridade", 0))

            party_data.append({
                "id": str(hid), "hero_id": h_id,
                "nome": f"{h_data.get('nome', 'Herói')} ({user_name})", "classe": cl,
                "level": level,
                "hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt,
                "stats": {
                    "hp": hp, "atk": atk, "matk": matk, "def": df,
                    "spd": spd, "crt": crt, "level": level,
                },
                "habilidades": skills,
            })

    party_data = apply_affinity_bonus(party_data, HEROES)
    party_data = apply_battle_hp_bonus(cursor, user_id, party_data)
    conn.commit()
    conn.close()
    return party_data

class BotaoAventura(discord.ui.Button):
    def __init__(self, op_dict, view_ref):
        label = cortar_texto(op_dict.get("label", "Seguir"), 76)
        emoji = op_dict.get("emoji", "🔘")
        super().__init__(style=discord.ButtonStyle.primary, label=label, emoji=emoji)
        self.op_dict = op_dict
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        chance = self.op_dict.get("chance_sucesso", 1.0)
        
        # Teste de Sorte (RNG)
        if random.random() <= chance:
            proximo = self.op_dict.get("next")
        else:
            proximo = self.op_dict.get("next_falha", self.op_dict.get("next"))
            
        await self.view_ref.ir_para_nodo(interaction, proximo)

class BotaoCombate(discord.ui.Button):
    def __init__(self, view_ref):
        super().__init__(style=discord.ButtonStyle.danger, label="Iniciar Combate!", emoji="⚔️")
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        await self.view_ref.resolver_combate(interaction)

class AdventureSession(discord.ui.View):
    def __init__(self, ctx, aventura_id, aventura_data, party_data, progress_level):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.user = ctx.author
        self.aventura_id = aventura_id
        self.aventura = aventura_data
        self.party_data = party_data
        self.progress_level = progress_level
        self.nodos = aventura_data.get("nodos", {})
        self.tier = int(aventura_data.get("_meta", {}).get("tier", 1))
        self.nodo_atual_id = "start"
        self.moral = 100
        self.perigo = 0

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

    def salvar_cooldown_e_loot(self, ouro, xp, drops_obtidos=None):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        uid = str(self.user.id)
        
        cursor.execute("UPDATE players SET last_adventure = ?, gold = gold + ? WHERE user_id = ?", (time.time(), ouro, uid))
        if xp > 0:
            dar_xp_jogador(cursor, uid, xp)
            for h in self.party_data:
                dar_xp_heroi(cursor, int(h["id"]), xp)
                
        # Deposita Itens Novos na Mochila do Jogador
        if drops_obtidos:
            for item in drops_obtidos:
                cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (uid, item))
                row = cursor.fetchone()
                if row:
                    cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (row[0],))
                else:
                    cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (uid, item))
                
        self.fechar_contrato_na_guilda(cursor, uid)
        conn.commit()
        conn.close()

    async def resolver_combate(self, interaction: discord.Interaction):
        nodo_atual = self.nodos[self.nodo_atual_id]
        inimigos_ids = nodo_atual.get("inimigos", [])
        
        team_b = []
        for idx, i_id in enumerate(inimigos_ids):
            ini_base = ENEMIES.get(i_id, {})
            danger_mult = 1.0 + (self.perigo / 500)
            b_stats = {
                "hp": int(ini_base.get("hp", 200) * danger_mult),
                "atk": int(ini_base.get("atk", 30) * danger_mult),
                "def": int(ini_base.get("def", 10) * danger_mult),
                "matk": int(ini_base.get("matk", 0) * danger_mult),
                "spd": ini_base.get("spd", 15), "crt": 5, 
                "habilidades": [ini_base.get("habilidade")] if ini_base.get("habilidade") else [],
                "classe": ini_base.get("tipo", "comum")
            }
            team_b.append({
                "id": f"B{idx}", "nome": ini_base.get("nome", "Monstro"), "classe": "comum",
                "hp": b_stats["hp"], "stats": b_stats, "habilidades": b_stats["habilidades"]
            })

        balance_adventure_encounter(team_b, self.party_data, self.tier)
        await interaction.response.edit_message(content="⚔️ **O combate começou! A vida pisca diante dos teus olhos...**", embed=None, view=None)
        
        vitoria, log_batalha = simular_combate_tatico(self.party_data, team_b)

        embed = discord.Embed(title="⚔️ Fim do Combate", description="A poeira abaixou...", color=discord.Color.green() if vitoria else discord.Color.red())
        embed.add_field(name="📜 Log da Batalha", value=cortar_texto(log_batalha, 1000), inline=False)
        
        self.clear_items()
        proximo = nodo_atual.get("win_next") if vitoria else nodo_atual.get("lose_next")
        
        if proximo and proximo in self.nodos:
            self.add_item(BotaoAventura({"label": "Continuar Jornada", "emoji": "➡️", "next": proximo}, self))
            await interaction.message.edit(embed=embed, view=self)
        else:
            embed.set_footer(text="A aventura terminou de forma trágica ou mal programada.")
            self.salvar_cooldown_e_loot(0, 0)
            await interaction.message.edit(embed=embed, view=None)

    async def ir_para_nodo(self, interaction, nodo_id):
        self.nodo_atual_id = nodo_id
        nodo = self.nodos.get(nodo_id)
        self.clear_items()

        tipo = nodo.get("tipo", "historia")
        embed = discord.Embed(title=f"🏕️ {self.aventura['nome']}", description=cortar_texto(nodo.get("texto", "..."), 850), color=discord.Color.dark_green())

        if tipo == "historia":
            for op in nodo.get("opcoes", []):
                self.add_item(BotaoAventura(op, self))

        elif tipo == "combate":
            embed.color = discord.Color.red()
            embed.set_footer(text="Um confronto é inevitável. Que os deuses te ajudem.")
            self.add_item(BotaoCombate(self))

        elif tipo == "recompensa":
            # Aplica mudanças de moral e perigo vindas da narrativa
            if "moral_change" in nodo:
                self.moral = max(0, min(100, self.moral + nodo["moral_change"]))
            if "perigo_change" in nodo:
                self.perigo = max(0, min(100, self.perigo + nodo["perigo_change"]))
                
            embed.color = discord.Color.gold()
            
            # Moral alta e Perigo alto aumentam o LOOT no final
            performance = 1 + max(0, self.moral - 50) / 400
            risco_bonus = 1 + min(0.20, self.perigo / 500)
            
            ouro = int(nodo.get("gold", 0) * performance * risco_bonus)
            xp = int(nodo.get("xp", 0) * performance * risco_bonus)
            ouro, xp = scale_combat_rewards(ouro, xp, self.progress_level)
            
            # Processa o RNG dos Drops de Itens Raros
            drops_dict = nodo.get("drops", {})
            drops_obtidos = []
            for item_name, chance in drops_dict.items():
                if random.random() <= chance:
                    drops_obtidos.append(item_name)
            
            recompensas_str = ""
            if ouro > 0: recompensas_str += f"💰 **{ouro} Gold**\n"
            if xp > 0: recompensas_str += f"⭐ **{xp} XP**\n"
            for item in drops_obtidos:
                recompensas_str += f"📦 **1x {item.replace('_', ' ').title()}**\n"
                
            if not recompensas_str: recompensas_str = "Apenas poeira e o alívio de estar vivo."
            
            embed.add_field(name="Loot Obtido", value=recompensas_str, inline=False)
            embed.set_footer(text="Contrato fechado! Volte ao quadro da guilda (echo work) ou espere o cooldown (echo cd).")
            
            self.salvar_cooldown_e_loot(ouro, xp, drops_obtidos)

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
        cursor.execute("SELECT last_adventure, level FROM players WHERE user_id = ?", (uid,))
        p_data = cursor.fetchone()
        
        tempo_passado = time.time() - (p_data[0] or 0)
        if tempo_passado < COOLDOWN_SEGUNDOS:
            conn.close()
            restante_m = int((COOLDOWN_SEGUNDOS - tempo_passado) / 60)
            return await ctx.send(f"⏳ Seus heróis ainda estão cuidando das feridas da última viagem. Aguarde **{restante_m} minutos**.")

        player_lvl = p_data[1] or 1

        # Verifica se TEM UMA MISSÃO do quadro ativa
        cursor.execute("SELECT active_mission FROM daily_quests WHERE user_id = ?", (uid,))
        q_data = cursor.fetchone()
        conn.close()

        if not q_data or not q_data[0]:
            return await ctx.send("❌ **TutoriUAU:** Tu quer ir fazer o quê lá fora sem contrato? Vai ao `echo work` e assina um dos papéis antes de sair andando sem rumo.")

        missao_ativa_id = q_data[0]
        aventura_escolhida = self.aventuras.get(missao_ativa_id)

        if not aventura_escolhida:
            return await ctx.send("❌ Erro no contrato. Parece que o dev apagou esta aventura do arquivo JSON.")

        party_data = puxar_party_para_combate(ctx.author.id, ctx.author.name)
        if not party_data:
            return await ctx.send("❌ Precisa de um Líder de Esquadrão para sair em aventura (`echo main <ID>`).")

        view = AdventureSession(ctx, missao_ativa_id, aventura_escolhida, party_data, player_lvl)
        
        embed = discord.Embed(
            title=f"🏕️ Iniciando Contrato: {aventura_escolhida['nome']}",
            description="Os portões de Lugnica fecham-se às tuas costas. O teu destino foi traçado.",
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
