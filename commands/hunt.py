import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random
import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.monsters import HUNT_MONSTERS
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
    from utils.combat import simular_combate_tatico
    # IMPORTANDO O NOVO MOTOR DE XP E OURO
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
    from utils.gold_system import conceder_ouro_escalavel
    
    from utils.skills import get_hero_skill_ids
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.rewards import average_party_level, scale_combat_rewards
    from utils.equipment import get_equipment_bonus
    from utils.affinity import apply_affinity_bonus
    from utils.player_bonuses import apply_reward_bonuses, apply_battle_hp_bonus
except ModuleNotFoundError:
    HUNT_MONSTERS, HEROES, EQUIPAMENTOS = {}, {}, {}

COOLDOWN_MINUTOS = 30
TEMPO_RECUPERACAO_SEGUNDOS = COOLDOWN_MINUTOS * 60

class Hunt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._verificar_banco_dados()

    def _verificar_banco_dados(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(players)")
        colunas = [info[1] for info in cursor.fetchall()]
        
        novas_colunas = {
            "last_hunt": "REAL DEFAULT 0",
            "total_hunts": "INTEGER DEFAULT 0",
            "stamina": "INTEGER DEFAULT 100",
            "max_stamina": "INTEGER DEFAULT 100"
        }
        for col, tipo in novas_colunas.items():
            if col not in colunas:
                cursor.execute(f"ALTER TABLE players ADD COLUMN {col} {tipo}")
                
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
        """)
        conn.commit()
        conn.close()

    def puxar_party_para_combate(self, user_id, user_name):
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
                
                skill_ids = get_hero_skill_ids(h_data, stars, h_data.get("raridade", 0))
                
                party_data.append({
                    "id": str(hid),
                    "hero_id": h_id,
                    "nome": f"{h_data.get('nome', 'Herói')} ({user_name})",
                    "classe": cl,
                    "level": level,
                    "stats": {"hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt, "level": level},
                    "habilidades": skill_ids
                })
                
        party_data = apply_affinity_bonus(party_data, HEROES)
        party_data = apply_battle_hp_bonus(cursor, user_id, party_data)
        conn.close()
        return party_data

    async def processar_hunt(self, user: discord.User, guild_id: str = None):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT gold, last_hunt, total_hunts FROM players WHERE user_id = ?", (str(user.id),))
        player_data = cursor.fetchone()

        if not player_data:
            conn.close()
            return f"❌ {user.mention}, inicie sua conta primeiro usando `echo iniciar`."
            
        gold_atual, last_hunt, total_hunts = player_data
        
        tempo_atual = time.time()
        tempo_passado = tempo_atual - (last_hunt or 0)
        if tempo_passado < TEMPO_RECUPERACAO_SEGUNDOS:
            tempo_restante = int((TEMPO_RECUPERACAO_SEGUNDOS - tempo_passado) / 60)
            conn.close()
            return f"⏳ Cansado(a)? Seus heróis ainda estão se recuperando da última caçada. Volte em **{tempo_restante} minutos**."

        team_a = self.puxar_party_para_combate(user.id, user.name)
        if not team_a:
            conn.close()
            return "❌ Você não pode ir caçar sozinho. Equipe um Herói Líder com `echo main <ID>`."

        nivel_medio_party = average_party_level(team_a)

        monstros_possiveis = [k for k, v in HUNT_MONSTERS.items() if v["nivel_min"] <= nivel_medio_party <= v["nivel_max"]]
        if not monstros_possiveis: monstros_possiveis = [k for k, v in HUNT_MONSTERS.items() if v["nivel_max"] == 999]

        pesos = [HUNT_MONSTERS[m]["raridade"] for m in monstros_possiveis]
        monstro_escolhido = random.choices(monstros_possiveis, weights=pesos, k=1)[0]
        m_data = HUNT_MONSTERS[monstro_escolhido]

        team_b = [{
            "id": monstro_escolhido,
            "nome": m_data["nome"],
            "classe": "monstro",
            "stats": {
                "hp": m_data["hp_base"],
                "atk": m_data["atk_base"],
                "def": m_data["def_base"],
                "matk": 0, "spd": 20, "crt": 5
            },
            "habilidades": []
        }]

        vitoria, log_batalha = simular_combate_tatico(team_a, team_b)

        if not vitoria:
            cursor.execute("UPDATE players SET last_hunt = ? WHERE user_id = ?", (tempo_atual, str(user.id)))
            conn.commit()
            conn.close()
            embed = discord.Embed(
                title="🌲 Caçada Fracassada",
                description=f"A sua party apanhou feio de um **{m_data['nome']}** e teve que fugir para a cidade correndo!\n*(Nenhuma recompensa ganha)*",
                color=discord.Color.red()
            )
            embed.add_field(name="📜 Log", value=log_batalha, inline=False)
            return embed

        # Recompensas Escalonadas (Usando os novos motores + utils antigos)
        gold_ganho = conceder_ouro_escalavel(cursor, user.id, m_data["gold_base"], nivel_medio_party, guild_id)
        
        xp_base = int((m_data["xp_base"] + (nivel_medio_party * 5)) * random.uniform(0.9, 1.15))
        _, xp_ganho = scale_combat_rewards(0, xp_base, nivel_medio_party)
        _, xp_ganho = apply_reward_bonuses(cursor, user.id, 0, xp_ganho)
        
        # GARANTIA DE DROP: 100% de chance de vir o item material do monstro!
        item_dropado = m_data["drop"] 

        # O Ouro já foi debitado na função conceder_ouro_escalavel, atualiza apenas os stats de caça
        cursor.execute("UPDATE players SET last_hunt = ?, total_hunts = total_hunts + 1 WHERE user_id = ?", (tempo_atual, str(user.id)))

        log_ups = ""
        
        ups_p, lvl_p = dar_xp_jogador(cursor, user.id, xp_ganho)
        if ups_p > 0:
            log_ups += f"🆙 **Sua Conta** subiu para o Nível {lvl_p}!\n"

        for h in team_a:
            ups, novo_lvl = dar_xp_heroi(cursor, int(h["id"]), xp_ganho)
            if ups > 0:
                log_ups += f"🌟 **{h['nome'].split(' (')[0]}** subiu para o Nível {novo_lvl}!\n"

        if item_dropado:
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(user.id), item_dropado))
            item_existe = cursor.fetchone()
            if item_existe: cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (item_existe[0],))
            else: cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (str(user.id), item_dropado))

        conn.commit()
        conn.close()

        item_nome_formatado = item_dropado.replace("_", " ").title() if item_dropado else ""
        
        embed = discord.Embed(
            title="🌲 Caçada Concluída!",
            description=f"A sua party abateu um **{m_data['nome']}** com sucesso!",
            color=discord.Color.green()
        )
        embed.add_field(name="📜 Combate", value=log_batalha, inline=False)
        
        recompensas_str = f"💰 **Ouro:** {gold_ganho}\n⭐ **XP:** {xp_ganho}"
        if item_dropado: recompensas_str += f"\n📦 **Item Extraído:** 1x {item_nome_formatado}"
            
        embed.add_field(name="Recompensas", value=recompensas_str, inline=False)
        if log_ups: embed.add_field(name="Level Up!", value=log_ups, inline=False)
        
        return embed

    @commands.command(name="hunt", aliases=["caçar", "cacar", "caçada"])
    async def hunt_prefix(self, ctx):
        guild_id = str(ctx.guild.id) if ctx.guild else None
        res = await self.processar_hunt(ctx.author, guild_id)
        await ctx.send(embed=res) if isinstance(res, discord.Embed) else await ctx.send(res)

    @app_commands.command(name="hunt", description="Envia a sua party para caçar na floresta.")
    async def hunt_slash(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id) if interaction.guild else None
        res = await self.processar_hunt(interaction.user, guild_id)
        await interaction.response.send_message(embed=res) if isinstance(res, discord.Embed) else await interaction.response.send_message(res)

async def setup(bot):
    await bot.add_cog(Hunt(bot))