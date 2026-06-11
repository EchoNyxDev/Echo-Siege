import discord
from discord.ext import commands, tasks
import sqlite3
import random
import os
import sys
import datetime
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.calamidades import RAID_BOSSES
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
    from utils.combat import simular_combate_tatico
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
    from utils.skills import get_hero_skill_ids, resolve_skill_list
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.rewards import average_party_level, scale_combat_rewards
    from utils.equipment import get_equipment_bonus
    from utils.affinity import apply_affinity_bonus
    from utils.player_bonuses import apply_battle_hp_bonus
except ModuleNotFoundError:
    RAID_BOSSES, HEROES, EQUIPAMENTOS = {}, {}, {}
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []
    def resolve_skill_list(habilidades):
        return habilidades or []
    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}
    def apply_affinity_bonus(party_data, heroes):
        return party_data
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

BRT = datetime.timezone(datetime.timedelta(hours=-3))
ROLE_INVOCADOR_ID = 1512228151382511748 


def _table_columns(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        return {row[1] for row in cursor.fetchall()}
    except sqlite3.OperationalError:
        return set()


def _add_column_if_missing(cursor, table, column, ddl):
    if column not in _table_columns(cursor, table):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_invasion_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_config (
            guild_id TEXT PRIMARY KEY,
            raid_channel_id TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raid_registrations (
            user_id TEXT,
            raid_type TEXT,
            guild_id TEXT,
            PRIMARY KEY (user_id, guild_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_stats (
            id INTEGER PRIMARY KEY,
            hp INTEGER DEFAULT 100000,
            max_hp INTEGER DEFAULT 100000,
            moral INTEGER DEFAULT 100,
            suprimentos INTEGER DEFAULT 0,
            max_suprimentos INTEGER DEFAULT 5000,
            prosperidade INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cidades(
            guild_id TEXT PRIMARY KEY,
            nome TEXT DEFAULT 'Capital de Lugnica',
            hp INTEGER DEFAULT 100000,
            max_hp INTEGER DEFAULT 100000,
            moral INTEGER DEFAULT 100,
            suprimentos INTEGER DEFAULT 0,
            max_suprimentos INTEGER DEFAULT 5000,
            prosperidade INTEGER DEFAULT 0
        )
    """)
    _add_column_if_missing(cursor, "server_config", "guild_id", "TEXT")
    _add_column_if_missing(cursor, "server_config", "raid_channel_id", "TEXT")
    _add_column_if_missing(cursor, "raid_registrations", "guild_id", "TEXT DEFAULT 'global'")
    _add_column_if_missing(cursor, "raid_registrations", "raid_type", "TEXT DEFAULT 'diaria'")
    _add_column_if_missing(cursor, "cidades", "guild_id", "TEXT")
    cursor.execute("INSERT OR IGNORE INTO city_stats (id) VALUES (1)")

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
            
            equipment_bonuses = [
                get_equipment_bonus(cursor, user_id, eq_name, EQUIPAMENTOS)
                for eq_name in [e_atk, e_def, e_livre]
                if eq_name and eq_name in EQUIPAMENTOS
            ]
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
    conn.commit()
    conn.close()
    return party_data

class RaidRegisterView(discord.ui.View):
    def __init__(self, raid_type: str, guild_id: str):
        super().__init__(timeout=None)
        self.raid_type = raid_type
        self.guild_id = guild_id

    @discord.ui.button(label="Me Registrar para a Batalha!", style=discord.ButtonStyle.success, emoji="⚔️")
    async def btn_register(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        
        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        
        if not player or not player[0]:
            conn.close()
            return await interaction.response.send_message("❌ Equipe um Herói Líder com `echo main <ID>` antes!", ephemeral=True)

        try:
            cursor.execute("SELECT 1 FROM raid_registrations WHERE user_id = ? AND guild_id = ?", (user_id, self.guild_id))
            if cursor.fetchone():
                conn.close()
                return await interaction.response.send_message("⚠️ Você já está registrado para defender esta muralha!", ephemeral=True)
            cursor.execute("DELETE FROM raid_registrations WHERE user_id = ? AND (guild_id IS NULL OR guild_id = 'global')", (user_id,))
            cursor.execute("INSERT OR REPLACE INTO raid_registrations (user_id, raid_type, guild_id) VALUES (?, ?, ?)", (user_id, self.raid_type, self.guild_id))
            conn.commit()
            await interaction.response.send_message("✅ Seu esquadrão está posicionado nas muralhas deste servidor!", ephemeral=True)
        except sqlite3.IntegrityError:
            await interaction.response.send_message("⚠️ Você já está registrado para defender esta muralha!", ephemeral=True)
        finally:
            conn.close()

class Invasoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_raid_task = None
        self.active_msg = None
        self.current_raid_type = None
        self.current_channel = None
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        conn.commit()
        conn.close()

    def _clear_active_raid(self):
        self.active_raid_task = None
        self.current_raid_type = None
        self.current_channel = None

    def get_raid_channel(self, guild_id):
        """Agora procura o canal do servidor específico"""
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        try:
            cursor.execute("SELECT raid_channel_id FROM server_config WHERE guild_id = ?", (str(guild_id),))
            data = cursor.fetchone()
        except sqlite3.OperationalError:
            data = None
        conn.commit()
        conn.close()
        if data and data[0]:
            try:
                return self.bot.get_channel(int(data[0]))
            except (TypeError, ValueError):
                return None
        return None

    async def iniciar_fase_registro(self, channel, tipo_raid, is_manual=False, duration=600):
        if not channel or not getattr(channel, "guild", None):
            raise ValueError("Canal de invasão inválido ou sem servidor.")

        duration = 60 if int(duration or 600) <= 60 else 600
        guild_id_str = str(channel.guild.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        cursor.execute("DELETE FROM raid_registrations WHERE guild_id = ?", (guild_id_str,))
        conn.commit()
        conn.close()

        minutos = int(duration / 60)
        titulo = "💀 ALERTA DE INVASÃO!"
        desc = f"Uma horda quer varrer Lugnica deste mundo!\nTempo de registro: **{minutos} Minuto{'s' if minutos > 1 else ''}**."
        cor = discord.Color.dark_theme()

        embed = discord.Embed(title=titulo, description=desc, color=cor)
        embed.add_field(name="Tipo", value=tipo_raid.title(), inline=True)
        embed.add_field(name="Servidor", value=channel.guild.name, inline=True)
        embed.set_footer(text="TutoriUAU: aperte o botão para se registrar. Só olhar dramaticamente não conta.")
        view = RaidRegisterView(tipo_raid, guild_id_str)
        mention_role = channel.guild.get_role(ROLE_INVOCADOR_ID)
        content = mention_role.mention if mention_role else "🚨 **Invasão manual iniciada!**"
        msg = await channel.send(content=content, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(roles=True))
        
        self.active_msg = msg
        self.current_raid_type = tipo_raid
        self.current_channel = channel

        if is_manual:
            if self.active_raid_task: self.active_raid_task.cancel()
            self.active_raid_task = asyncio.create_task(self.esperar_e_executar(channel, tipo_raid, duration))
        return msg

    async def esperar_e_executar(self, channel, tipo_raid, duration):
        try:
            await asyncio.sleep(duration)
            await self.executar_batalha(channel, tipo_raid)
        except asyncio.CancelledError:
            pass

    async def executar_batalha(self, channel, tipo_raid):
        if self.active_msg:
            try: await self.active_msg.delete()
            except: pass
            self.active_msg = None

        guild_id_str = str(channel.guild.id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        cursor.execute("SELECT user_id FROM raid_registrations WHERE raid_type = ? AND guild_id = ?", (tipo_raid, guild_id_str))
        registrados = [row[0] for row in cursor.fetchall()]
        
        if not registrados:
            conn.close()
            self._clear_active_raid()
            return await channel.send(embed=discord.Embed(title="🌬️ Falso Alarme", description="Ninguém apareceu para defender.", color=discord.Color.light_grey()))

        # 1. MONTANDO A MEGA-ALIANÇA
        team_a = []
        for u_id in registrados:
            member = self.bot.get_user(int(u_id))
            nome_display = member.name if member else "Aliado"
            p_party = puxar_party_para_combate(u_id, nome_display)
            if p_party:
                team_a.extend(p_party)

        if not team_a:
            conn.close()
            self._clear_active_raid()
            return await channel.send("⚠️ Erro nas formações. Ninguém tem heróis válidos.")

        # 2. MONTANDO O MEGA-BOSS
        num_players = len(registrados)
        boss_pool = [
            boss_id for boss_id, boss_data in RAID_BOSSES.items()
            if tipo_raid in ("diaria", "raid") or boss_data.get("tipo") == tipo_raid
        ]
        if not boss_pool:
            boss_pool = list(RAID_BOSSES.keys())
        boss_id = random.choice(boss_pool)
        b_data = RAID_BOSSES[boss_id]
        
        team_b = [{
            "id": boss_id,
            "nome": f"🚨 {b_data['nome']} (Calamidade de {channel.guild.name})",
            "classe": "boss",
            "stats": {
                "hp": b_data.get("hp", 100000) * num_players,
                "atk": int(b_data.get("atk", 1000) * max(1, num_players * 0.5)),
                "def": int(b_data.get("def", 500) * max(1, num_players * 0.5)),
                "matk": int(b_data.get("matk", 0) * max(1, num_players * 0.5)),
                "spd": b_data.get("spd", 50),
                "crt": b_data.get("crt", 10)
            },
            "habilidades": resolve_skill_list(b_data.get("habilidades", [b_data.get("habilidade")] if "habilidade" in b_data else []))
        }]

        vitoria, log_batalha = simular_combate_tatico(team_a, team_b)

        embed_final = discord.Embed()
        if vitoria:
            reward_bases = {
                "diaria": (260, 90),
                "raid": (260, 90),
                "semanal": (650, 220),
                "mensal": (1400, 480),
            }
            base_gold, base_xp = reward_bases.get(tipo_raid, reward_bases["diaria"])
            gold_ganho, xp_ganho = scale_combat_rewards(
                base_gold,
                base_xp,
                average_party_level(team_a),
            )
            
            for u_id in registrados:
                cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (gold_ganho, u_id))
                dar_xp_jogador(cursor, u_id, xp_ganho)
                p_party = puxar_party_para_combate(u_id, "Temp")
                if p_party:
                    for h in p_party:
                        dar_xp_heroi(cursor, int(h["id"]), xp_ganho)
            
            # Tenta atualizar primeiro a cidade do servidor atual, e depois cai pro global caso haja bug
            cursor.execute("""
                INSERT OR IGNORE INTO cidades
                (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
                VALUES (?, 'Capital de Lugnica', 100000, 100000, 100, 0, 5000, 0)
            """, (guild_id_str,))
            try: cursor.execute("UPDATE cidades SET prosperidade = prosperidade + 5 WHERE guild_id = ?", (guild_id_str,))
            except sqlite3.OperationalError: pass
            cursor.execute("UPDATE city_stats SET prosperidade = prosperidade + 5 WHERE id = 1")
            
            embed_final.title = f"🏆 AMEAÇA EM {channel.guild.name.upper()} ERRADICADA!"
            embed_final.description = f"As fileiras unidas venceram.\n\nTodos os defensores locais receberam **{gold_ganho} Gold** e **{xp_ganho} XP**!"
            embed_final.color = discord.Color.green()
        else:
            dano_muralha = 25000
            cursor.execute("""
                INSERT OR IGNORE INTO cidades
                (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
                VALUES (?, 'Capital de Lugnica', 100000, 100000, 100, 0, 5000, 0)
            """, (guild_id_str,))
            try: cursor.execute("UPDATE cidades SET moral = moral - 10, hp = max(0, hp - ?) WHERE guild_id = ?", (dano_muralha, guild_id_str))
            except sqlite3.OperationalError: pass
            cursor.execute("UPDATE city_stats SET moral = moral - 10, hp = max(0, hp - ?) WHERE id = 1", (dano_muralha,))
            
            embed_final.title = "☠️ MASSACRE TOTAL!"
            embed_final.description = f"O inimigo dizimou a aliança deste servidor.\n\n🧱 **Dano na Muralha Local:** -{dano_muralha:,} HP"
            embed_final.color = discord.Color.red()

        conn.commit()
        conn.close()
        
        embed_final.add_field(name="📜 Log Tático Simplificado", value=log_batalha, inline=False)
        await channel.send(embed=embed_final)
        self._clear_active_raid()

    @commands.command(name="raid_spawn")
    async def trigger_manual_raid(self, ctx, tipo: str = "diaria", time_skip=None):
        if not ctx.guild:
            return await ctx.send("❌ Você deve usar este comando em um servidor.")
            
        canal = self.get_raid_channel(ctx.guild.id)
        if not canal:
            canal = ctx.channel
            
        skip_text = str(time_skip or "").lower().replace("_", "-").replace(" ", "-")
        duration = 60 if time_skip is True or skip_text in ["time-skip", "timeskip", "skip"] else 600
        await self.iniciar_fase_registro(canal, tipo, is_manual=True, duration=duration)
        await ctx.send(f"✅ Invasão **{tipo}** iniciada em {canal.mention}. Registro por **{duration // 60} minuto(s)**.")

    @commands.command(name="raid_timeskip")
    async def force_timeskip(self, ctx):
        if not self.active_raid_task or not self.current_channel or not self.current_raid_type:
            return await ctx.send("❌ Nenhuma invasão pendente.")
        self.active_raid_task.cancel()
        await self.executar_batalha(self.current_channel, self.current_raid_type)

async def setup(bot):
    await bot.add_cog(Invasoes(bot))
