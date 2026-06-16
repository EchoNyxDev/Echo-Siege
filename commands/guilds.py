import os
import random
import re
import sqlite3
import sys
import time

import discord
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from utils.gold_system import conceder_ouro_escalavel
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
except ModuleNotFoundError:
    HEROES = {}
    def conceder_ouro_escalavel(*args, **kwargs): return 0
    def dar_xp_jogador(*args): return 0, 1
    def dar_xp_heroi(*args): return 0, 1


CREATE_GUILD_COST = 5000

GUILD_MISSIONS = {
    "caca": {
        "name": "Caçada da Guilda",
        "desc": "A guilda limpa monstros menores para juntar recursos.",
        "cost": 1000,
        "target": 5000,
        "duration": 12 * 3600,
        "reward_bank": 2500,
        "reward_xp": 120,
        "reward_score": 500,
        "member_gold": 400,
        "member_xp": 150,
        "member_gems": 0,
        "member_tickets": 0,
    },
    "dungeon": {
        "name": "Expedição Dimensional",
        "desc": "Uma masmorra instável aparece e todo mundo finge que isso é normal.",
        "cost": 2500,
        "target": 12000,
        "duration": 18 * 3600,
        "reward_bank": 5500,
        "reward_xp": 320,
        "reward_score": 1500,
        "member_gold": 900,
        "member_xp": 350,
        "member_gems": 2,
        "member_tickets": 0,
    },
    "boss": {
        "name": "Contrato de Subjugação",
        "desc": "A guilda paga para caçar um chefe específico. Péssima ideia, ótimas recompensas.",
        "cost": 5000,
        "target": 25000,
        "duration": 24 * 3600,
        "reward_bank": 11000,
        "reward_xp": 700,
        "reward_score": 4000,
        "member_gold": 1800,
        "member_xp": 800,
        "member_gems": 4,
        "member_tickets": 1,
    },
}

GUILD_HUNT_BOSSES = [
    {"name": "Behemoth de Lugnica", "hp": 18000, "cost": 2500, "reward_bank": 5000, "reward_member": 850, "score": 1600},
    {"name": "Hidra da Fronteira", "hp": 26000, "cost": 4200, "reward_bank": 8500, "reward_member": 1300, "score": 2800},
    {"name": "Arconte do Eclipse", "hp": 38000, "cost": 7000, "reward_bank": 14000, "reward_member": 2100, "score": 4600},
]


def init_guild_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guilds(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            owner_id TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            gold_bank INTEGER DEFAULT 0,
            raid_score INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(player_guilds)")
    cols = {row[1] for row in cursor.fetchall()}
    for col, ddl in {
        "description": "TEXT DEFAULT ''",
        "icon_url": "TEXT DEFAULT ''",
        "join_mode": "TEXT DEFAULT 'convite'",
    }.items():
        if col not in cols:
            cursor.execute(f"ALTER TABLE player_guilds ADD COLUMN {col} {ddl}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_members(
            guild_id INTEGER NOT NULL,
            user_id TEXT PRIMARY KEY,
            role TEXT DEFAULT 'member',
            contribution INTEGER DEFAULT 0,
            joined_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_raids(
            guild_id INTEGER PRIMARY KEY,
            boss_name TEXT NOT NULL,
            hp INTEGER NOT NULL,
            max_hp INTEGER NOT NULL,
            started_at INTEGER NOT NULL,
            ends_at INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_invites(
            guild_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            invited_by TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_applications(
            guild_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_missions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            mission_id TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            target INTEGER DEFAULT 0,
            started_by TEXT NOT NULL,
            started_at INTEGER DEFAULT 0,
            ends_at INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_mission_actions(
            guild_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            last_action INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_raid_actions(
            guild_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            last_action INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_hunts(
            guild_id INTEGER PRIMARY KEY,
            boss_name TEXT NOT NULL,
            hp INTEGER NOT NULL,
            max_hp INTEGER NOT NULL,
            reward_gold INTEGER DEFAULT 0,
            started_by TEXT NOT NULL,
            started_at INTEGER DEFAULT 0,
            ends_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_guild_hunt_actions(
            guild_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            last_action INTEGER DEFAULT 0,
            damage INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_stats(
            user_id TEXT NOT NULL,
            stat TEXT NOT NULL,
            value INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, stat)
        )
    """)


def get_equipped_party(cursor, user_id):
    """Puxa a Party real do jogador que está equipada no momento"""
    cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
    p_data = cursor.fetchone()
    if not p_data or not p_data[0]: return []
    
    cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
    team = cursor.fetchone()
    return [p_data[0]] + [x for x in (team if team else []) if x is not None]

def party_power_and_level(cursor, user_id):
    """Calcula a força e o nível médio baseado na Party ativa do jogador"""
    time_ids = get_equipped_party(cursor, user_id)
    if not time_ids: return 80, 1
    
    power = 0
    levels = []
    for hid in time_ids:
        cursor.execute("SELECT rarity, stars, level FROM heroes WHERE id = ?", (int(hid),))
        hero = cursor.fetchone()
        if hero:
            rarity, stars, level = hero
            power += (rarity or 1) * (stars or 1) * ((level or 1) + 16)
            levels.append(level or 1)
            
    avg_level = sum(levels) // len(levels) if levels else 1
    return int(power), avg_level


def add_tickets(cursor, user_id, amount):
    if amount <= 0:
        return
    cursor.execute(
        """
        INSERT OR IGNORE INTO summon_data
        (user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star)
        VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
        """,
        (str(user_id),),
    )
    cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (amount, str(user_id)))


def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute("INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)", (str(user_id), stat))
    cursor.execute("UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?", (amount, str(user_id), stat))


def hp_bar(current, maximum, size=18):
    maximum = max(1, int(maximum))
    current = max(0, int(current))
    filled = min(size, int(size * current / maximum))
    return "█" * filled + "░" * (size - filled)


def boss_phase(hp, max_hp):
    ratio = hp / max(1, max_hp)
    if ratio <= 0.25:
        return "Fúria Final"
    if ratio <= 0.50:
        return "Quebra de Guarda"
    if ratio <= 0.75:
        return "Pressão Crescente"
    return "Abertura"


class Guilds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        conn.commit()
        conn.close()

    def _extract_user_id(self, text):
        if not text:
            return None
        found = re.sub(r"\D", "", str(text))
        return found or None

    def _get_user_guild(self, cursor, user_id):
        cursor.execute("""
            SELECT g.id, g.name, g.owner_id, g.level, g.xp, g.gold_bank, g.raid_score,
                   m.role, m.contribution, g.description, g.icon_url, g.join_mode
            FROM player_guild_members m
            JOIN player_guilds g ON g.id = m.guild_id
            WHERE m.user_id = ?
        """, (str(user_id),))
        return cursor.fetchone()

    def _resolve_guild(self, cursor, target):
        if not target:
            return None
        target = target.strip()
        if target.isdigit():
            cursor.execute("SELECT id, name, owner_id, level, xp, gold_bank, raid_score, description, icon_url, join_mode FROM player_guilds WHERE id = ?", (int(target),))
        else:
            cursor.execute("SELECT id, name, owner_id, level, xp, gold_bank, raid_score, description, icon_url, join_mode FROM player_guilds WHERE lower(name) = lower(?)", (target,))
        return cursor.fetchone()

    def _can_manage(self, guild_row):
        role = guild_row[7] if guild_row else ""
        return role in ["leader", "officer"]

    async def _confirmar_sair(self, ctx, texto):
        await ctx.send(f"{texto}\nDigite `sair` em até 30 segundos para confirmar. O TutoriUAU colocou a trava porque clique nervoso existe.")

        def check(message):
            return (
                message.author.id == ctx.author.id
                and message.channel.id == ctx.channel.id
                and message.content.strip().lower() == "sair"
            )

        try:
            await self.bot.wait_for("message", check=check, timeout=30)
            return True
        except Exception:
            await ctx.send("Confirmação cancelada. Drama administrativo arquivado.")
            return False

    def _level_up_guild(self, cursor, guild_id):
        cursor.execute("SELECT level, xp FROM player_guilds WHERE id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row:
            return 1
        level, xp = row
        while xp >= level * 150:
            xp -= level * 150
            level += 1
        cursor.execute("UPDATE player_guilds SET level = ?, xp = ? WHERE id = ?", (level, xp, guild_id))
        return level

    def _guild_embed(self, guild):
        gid, name, owner_id, level, xp, bank, score, role, contribution, desc, icon, join_mode = guild
        embed = discord.Embed(
            title=f"Guilda {name}",
            description=desc or "Sem descrição. Líder, capricha. O vazio não recruta ninguém.",
            color=discord.Color.dark_gold(),
        )
        if icon:
            embed.set_thumbnail(url=icon)
        embed.add_field(name="ID", value=str(gid), inline=True)
        embed.add_field(name="Líder", value=f"<@{owner_id}>", inline=True)
        embed.add_field(name="Entrada", value="Aberta" if join_mode == "aberto" else "Por convite/aprovação", inline=True)
        embed.add_field(name="Nível", value=f"{level} ({xp}/{level * 150} XP)", inline=True)
        embed.add_field(name="Banco", value=f"{bank:,} Gold", inline=True)
        embed.add_field(name="Score", value=f"{score:,}", inline=True)
        embed.add_field(name="Sua função", value=role, inline=True)
        embed.add_field(name="Sua contribuição", value=f"{contribution or 0:,} Gold", inline=True)
        embed.set_footer(text="TutoriUAU • guild membros, doar, missao, raid, caca, ranking, foto, descricao, modo")
        return embed

    @commands.group(name="guild", aliases=["g"], invoke_without_command=True)
    async def guild_cmd(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        conn.close()
        if not guild:
            return await ctx.send(
                "Você ainda não está em guilda. Use `echo guild criar <nome>` por **5000 Gold** "
                "ou `echo guild entrar <id|nome>`. Sim, socializar agora tem taxa."
            )
        await ctx.send(embed=self._guild_embed(guild))

    @guild_cmd.command(name="criar")
    async def criar(self, ctx, *, nome: str = None):
        if not nome or len(nome.strip()) < 3:
            return await ctx.send("Use `echo guild criar <nome>` com pelo menos 3 caracteres.")
        nome = nome.strip()[:32]
        user_id = str(ctx.author.id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        if self._get_user_guild(cursor, user_id):
            conn.close()
            return await ctx.send("Você já está em uma guilda. Uma família disfuncional por vez, por favor.")

        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        if not player:
            conn.close()
            return await ctx.send("Use `echo iniciar` antes de fundar uma instituição duvidosa.")
        if (player[0] or 0) < CREATE_GUILD_COST:
            conn.close()
            return await ctx.send(f"Criar guilda custa **{CREATE_GUILD_COST:,} Gold**. Você tem **{player[0] or 0:,}**.")

        try:
            cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (CREATE_GUILD_COST, user_id))
            cursor.execute(
                "INSERT INTO player_guilds (name, owner_id, created_at, join_mode) VALUES (?, ?, ?, 'convite')",
                (nome, user_id, int(time.time())),
            )
            guild_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO player_guild_members (guild_id, user_id, role, joined_at) VALUES (?, ?, 'leader', ?)",
                (guild_id, user_id, int(time.time())),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return await ctx.send("Já existe uma guilda com esse nome. Criatividade falhou, tente outra.")
        conn.close()
        await ctx.send(f"Guilda **{nome}** criada por **{CREATE_GUILD_COST:,} Gold**. Você é o líder. O peso da responsabilidade combina com você. Talvez.")

    @guild_cmd.command(name="entrar")
    async def entrar(self, ctx, *, alvo: str = None):
        if not alvo:
            return await ctx.send("Use `echo guild entrar <id|nome>`.")

        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        if self._get_user_guild(cursor, user_id):
            conn.close()
            return await ctx.send("Você já está em uma guilda.")

        guild = self._resolve_guild(cursor, alvo)
        if not guild:
            conn.close()
            return await ctx.send("Guilda não encontrada.")

        gid, name, _, _, _, _, _, _, _, join_mode = guild
        cursor.execute("SELECT status FROM player_guild_invites WHERE guild_id = ? AND user_id = ?", (gid, user_id))
        invite = cursor.fetchone()
        if join_mode == "aberto" or (invite and invite[0] == "pending"):
            cursor.execute(
                "INSERT INTO player_guild_members (guild_id, user_id, role, joined_at) VALUES (?, ?, 'member', ?)",
                (gid, user_id, int(time.time())),
            )
            cursor.execute("UPDATE player_guild_invites SET status = 'accepted' WHERE guild_id = ? AND user_id = ?", (gid, user_id))
            conn.commit()
            conn.close()
            return await ctx.send(f"Você entrou na guilda **{name}**. Bem-vindo ao contrato social com buffs.")

        cursor.execute(
            "INSERT OR REPLACE INTO player_guild_applications (guild_id, user_id, status, created_at) VALUES (?, ?, 'pending', ?)",
            (gid, user_id, int(time.time())),
        )
        conn.commit()
        conn.close()
        await ctx.send(f"Pedido enviado para **{name}**. Agora aguarde o líder fingir que é ocupado.")

    @guild_cmd.command(name="convite", aliases=["convidar"])
    async def convite(self, ctx, membro: discord.Member = None):
        if not membro:
            return await ctx.send("Use `echo guild convite @usuário`.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild or not self._can_manage(guild):
            conn.close()
            return await ctx.send("Só líder/oficial pode enviar convite. Hierarquia: chata, porém funcional.")
        if self._get_user_guild(cursor, membro.id):
            conn.close()
            return await ctx.send("Esse jogador já está em uma guilda.")
        cursor.execute(
            "INSERT OR REPLACE INTO player_guild_invites (guild_id, user_id, invited_by, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (guild[0], str(membro.id), str(ctx.author.id), int(time.time())),
        )
        conn.commit()
        conn.close()
        await ctx.send(f"Convite enviado para {membro.mention}. Use `echo guild aceitar {guild[0]}` para entrar.")

    @guild_cmd.command(name="aceitar")
    async def aceitar(self, ctx, *, alvo: str = None):
        if not alvo:
            return await ctx.send("Use `echo guild aceitar <id da guilda>` ou, sendo líder, `echo guild aceitar @usuário`.")
        user_id = str(ctx.author.id)
        target_user_id = self._extract_user_id(alvo)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        my_guild = self._get_user_guild(cursor, user_id)

        if target_user_id and my_guild and self._can_manage(my_guild):
            cursor.execute(
                "SELECT status FROM player_guild_applications WHERE guild_id = ? AND user_id = ?",
                (my_guild[0], target_user_id),
            )
            app = cursor.fetchone()
            if not app or app[0] != "pending":
                conn.close()
                return await ctx.send("Não achei pedido pendente desse usuário para sua guilda.")
            if self._get_user_guild(cursor, target_user_id):
                conn.close()
                return await ctx.send("Esse usuário já entrou em outra guilda. Drama administrativo evitado.")
            cursor.execute(
                "INSERT INTO player_guild_members (guild_id, user_id, role, joined_at) VALUES (?, ?, 'member', ?)",
                (my_guild[0], target_user_id, int(time.time())),
            )
            cursor.execute("UPDATE player_guild_applications SET status = 'accepted' WHERE guild_id = ? AND user_id = ?", (my_guild[0], target_user_id))
            conn.commit()
            conn.close()
            return await ctx.send(f"<@{target_user_id}> foi aceito na guilda **{my_guild[1]}**.")

        if my_guild:
            conn.close()
            return await ctx.send("Você já está em uma guilda. Não dá para aceitar convite de outra.")
        guild = self._resolve_guild(cursor, alvo)
        if not guild:
            conn.close()
            return await ctx.send("Guilda não encontrada.")
        cursor.execute("SELECT status FROM player_guild_invites WHERE guild_id = ? AND user_id = ?", (guild[0], user_id))
        invite = cursor.fetchone()
        if not invite or invite[0] != "pending":
            conn.close()
            return await ctx.send("Você não tem convite pendente dessa guilda.")
        cursor.execute(
            "INSERT INTO player_guild_members (guild_id, user_id, role, joined_at) VALUES (?, ?, 'member', ?)",
            (guild[0], user_id, int(time.time())),
        )
        cursor.execute("UPDATE player_guild_invites SET status = 'accepted' WHERE guild_id = ? AND user_id = ?", (guild[0], user_id))
        conn.commit()
        conn.close()
        await ctx.send(f"Convite aceito. Você entrou em **{guild[1]}**.")

    @guild_cmd.command(name="pedidos")
    async def pedidos(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild or not self._can_manage(guild):
            conn.close()
            return await ctx.send("Só líder/oficial pode ver pedidos.")
        cursor.execute(
            "SELECT user_id, created_at FROM player_guild_applications WHERE guild_id = ? AND status = 'pending' ORDER BY created_at DESC LIMIT 15",
            (guild[0],),
        )
        rows = cursor.fetchall()
        conn.close()
        text = "\n".join(f"<@{uid}> - <t:{created}:R>" for uid, created in rows) or "Nenhum pedido pendente."
        await ctx.send(embed=discord.Embed(title=f"Pedidos de entrada - {guild[1]}", description=text, color=discord.Color.blue()))

    @guild_cmd.command(name="sair")
    async def sair(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        if guild[2] == str(ctx.author.id):
            conn.close()
            return await ctx.send("Líder não pode sair direto. Use `echo guild lider @usuário` para passar a liderança ou `echo guild deletar` para encerrar a guilda.")
        conn.close()
        if not await self._confirmar_sair(ctx, f"Você está prestes a sair da guilda **{guild[1]}**. Tem certeza?"):
            return
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        cursor.execute("DELETE FROM player_guild_members WHERE user_id = ?", (str(ctx.author.id),))
        conn.commit()
        conn.close()
        await ctx.send("Você saiu da guilda. O drama fica para a próxima reunião.")

    @guild_cmd.command(name="lider", aliases=["líder", "lideranca", "liderança", "transferir", "passarlideranca", "passar_lideranca"])
    async def transferir_lider(self, ctx, membro: discord.Member = None):
        if not membro:
            return await ctx.send("Use `echo guild lider @usuário` para passar a liderança.")
        if membro.id == ctx.author.id:
            return await ctx.send("Você já é você. O TutoriUAU conferiu duas vezes.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        if guild[2] != str(ctx.author.id):
            conn.close()
            return await ctx.send("Só o líder pode passar a liderança.")
        cursor.execute("SELECT role FROM player_guild_members WHERE guild_id = ? AND user_id = ?", (guild[0], str(membro.id)))
        if not cursor.fetchone():
            conn.close()
            return await ctx.send("Esse usuário não faz parte da sua guilda.")
        conn.close()
        if not await self._confirmar_sair(ctx, f"Você vai entregar a liderança da guilda **{guild[1]}** para {membro.mention}."):
            return
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        cursor.execute("UPDATE player_guilds SET owner_id = ? WHERE id = ?", (str(membro.id), guild[0]))
        cursor.execute("UPDATE player_guild_members SET role = 'leader' WHERE guild_id = ? AND user_id = ?", (guild[0], str(membro.id)))
        cursor.execute("UPDATE player_guild_members SET role = 'officer' WHERE guild_id = ? AND user_id = ?", (guild[0], str(ctx.author.id)))
        conn.commit()
        conn.close()
        await ctx.send(f"Liderança transferida para {membro.mention}. TutoriUAU registrou a troca de coroa e a provável fofoca.")

    @guild_cmd.command(name="deletar", aliases=["apagar", "excluir", "delete"])
    async def deletar_guilda(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        if guild[2] != str(ctx.author.id):
            conn.close()
            return await ctx.send("Só o líder pode deletar a guilda.")
        conn.close()
        if not await self._confirmar_sair(ctx, f"Você está prestes a deletar a guilda **{guild[1]}**. Banco, membros, raids e pedidos serão removidos."):
            return
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild_id = guild[0]
        for table in [
            "player_guild_members",
            "player_guild_invites",
            "player_guild_applications",
            "player_guild_missions",
            "player_guild_mission_actions",
            "player_guild_raids",
            "player_guild_raid_actions",
            "player_guild_hunts",
            "player_guild_hunt_actions",
        ]:
            cursor.execute(f"DELETE FROM {table} WHERE guild_id = ?", (guild_id,))
        cursor.execute("DELETE FROM player_guilds WHERE id = ?", (guild_id,))
        conn.commit()
        conn.close()
        await ctx.send(f"Guilda **{guild[1]}** deletada. TutoriUAU apagou a placa da sede e fingiu maturidade.")

    @guild_cmd.command(name="membros")
    async def membros(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        cursor.execute(
            "SELECT user_id, role, contribution FROM player_guild_members WHERE guild_id = ? ORDER BY role DESC, contribution DESC LIMIT 25",
            (guild[0],),
        )
        rows = cursor.fetchall()
        conn.close()
        text = "\n".join(f"<@{uid}> - **{role}** - {contrib or 0:,} Gold" for uid, role, contrib in rows)
        await ctx.send(embed=discord.Embed(title=f"Membros de {guild[1]}", description=text or "Sem membros.", color=discord.Color.blue()))

    @guild_cmd.command(name="foto", aliases=["icone", "icon"])
    async def foto(self, ctx, *, url: str = None):
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return await ctx.send("Use `echo guild foto <url da imagem>`.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild or not self._can_manage(guild):
            conn.close()
            return await ctx.send("Só líder/oficial pode mudar a foto.")
        cursor.execute("UPDATE player_guilds SET icon_url = ? WHERE id = ?", (url[:500], guild[0]))
        conn.commit()
        conn.close()
        await ctx.send("Foto da guilda atualizada. Agora sim, identidade visual. Quase profissional.")

    @guild_cmd.command(name="descricao", aliases=["descrição", "desc"])
    async def descricao(self, ctx, *, texto: str = None):
        if not texto:
            return await ctx.send("Use `echo guild descricao <texto>`.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild or not self._can_manage(guild):
            conn.close()
            return await ctx.send("Só líder/oficial pode mudar a descrição.")
        cursor.execute("UPDATE player_guilds SET description = ? WHERE id = ?", (texto[:300], guild[0]))
        conn.commit()
        conn.close()
        await ctx.send("Descrição atualizada. Marketing de guilda: iniciado.")

    @guild_cmd.command(name="modo")
    async def modo(self, ctx, modo: str = None):
        modo = (modo or "").lower()
        if modo not in ["aberto", "convite"]:
            return await ctx.send("Use `echo guild modo aberto` ou `echo guild modo convite`.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild or not self._can_manage(guild):
            conn.close()
            return await ctx.send("Só líder/oficial pode mudar o modo de entrada.")
        cursor.execute("UPDATE player_guilds SET join_mode = ? WHERE id = ?", (modo, guild[0]))
        conn.commit()
        conn.close()
        await ctx.send(f"Modo de entrada alterado para **{modo}**.")

    @guild_cmd.command(name="doar")
    async def doar(self, ctx, quantidade: int = None):
        if not quantidade or quantidade <= 0:
            return await ctx.send("Use `echo guild doar <quantidade>`.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (str(ctx.author.id),))
        player = cursor.fetchone()
        if not player or (player[0] or 0) < quantidade:
            conn.close()
            return await ctx.send("Ouro insuficiente.")
        guild_xp = quantidade // 100
        cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (quantidade, str(ctx.author.id)))
        cursor.execute("UPDATE player_guilds SET gold_bank = gold_bank + ?, xp = xp + ? WHERE id = ?", (quantidade, guild_xp, guild[0]))
        cursor.execute("UPDATE player_guild_members SET contribution = COALESCE(contribution, 0) + ? WHERE user_id = ?", (quantidade, str(ctx.author.id)))
        level = self._level_up_guild(cursor, guild[0])
        conn.commit()
        conn.close()
        await ctx.send(f"Doação registrada: **{quantidade:,} Gold**. Guilda no nível **{level}**. O banco agradece. Eu também, mas só por educação.")

    @guild_cmd.group(name="missao", aliases=["missão", "missoes", "missões", "missions"], invoke_without_command=True)
    async def missao(self, ctx, *args):
        if args:
            return await ctx.send("❌ Comando não reconhecido. Use `echo guild missao iniciar <nome>` ou `echo guild missao atacar`.")
            
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        now = int(time.time())
        cursor.execute(
            "SELECT mission_id, progress, target, ends_at FROM player_guild_missions WHERE guild_id = ? AND completed = 0 AND ends_at > ? ORDER BY id DESC LIMIT 1",
            (guild[0], now),
        )
        active = cursor.fetchone()
        conn.close()
        embed = discord.Embed(title=f"Missões da Guilda {guild[1]}", color=discord.Color.dark_gold())
        if active:
            mission = GUILD_MISSIONS.get(active[0], {})
            embed.description = f"Missão ativa: **{mission.get('name', active[0])}**\nProgresso: **{active[1]:,}/{active[2]:,}**\nTermina <t:{active[3]}:R>\nUse `echo guild missao atacar`."
        else:
            embed.description = "Nenhuma missão ativa. Líder/oficial pode iniciar uma com `echo guild missao iniciar <id>`.\nOportunidade de trabalho, que alegria."
        lines = []
        for mid, mission in GUILD_MISSIONS.items():
            lines.append(f"`{mid}` - **{mission['name']}** | Custo {mission['cost']:,} | Alvo {mission['target']:,}\n{mission['desc']}")
        embed.add_field(name="Disponíveis", value="\n\n".join(lines), inline=False)
        await ctx.send(embed=embed)

    @missao.command(name="iniciar")
    async def missao_iniciar(self, ctx, mission_id: str = None):
        mission_id = (mission_id or "").lower()
        if mission_id not in GUILD_MISSIONS:
            return await ctx.send("Missão inválida. Use `echo guild missao` para ver a lista de IDs corretos.")
        mission = GUILD_MISSIONS[mission_id]
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, ctx.author.id)
        if not guild or not self._can_manage(guild):
            conn.close()
            return await ctx.send("Só líder/oficial pode iniciar missão.")
        now = int(time.time())
        cursor.execute(
            "SELECT id FROM player_guild_missions WHERE guild_id = ? AND completed = 0 AND ends_at > ? LIMIT 1",
            (guild[0], now),
        )
        if cursor.fetchone():
            conn.close()
            return await ctx.send("Já existe uma missão ativa. Uma confusão por vez, campeão.")
        if guild[5] < mission["cost"]:
            conn.close()
            return await ctx.send(f"O banco da guilda precisa de **{mission['cost']:,} Gold**.")
        cursor.execute("UPDATE player_guilds SET gold_bank = gold_bank - ? WHERE id = ?", (mission["cost"], guild[0]))
        cursor.execute(
            """
            INSERT INTO player_guild_missions (guild_id, mission_id, progress, target, started_by, started_at, ends_at)
            VALUES (?, ?, 0, ?, ?, ?, ?)
            """,
            (guild[0], mission_id, mission["target"], str(ctx.author.id), now, now + mission["duration"]),
        )
        conn.commit()
        conn.close()
        await ctx.send(f"Missão **{mission['name']}** iniciada por **{mission['cost']:,} Gold**. Use `echo guild missao atacar` para contribuir.")

    @missao.command(name="atacar", aliases=["contribuir", "batalhar"])
    async def missao_atacar(self, ctx):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, user_id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
        now = int(time.time())
        cursor.execute(
            "SELECT id, mission_id, progress, target, ends_at FROM player_guild_missions WHERE guild_id = ? AND completed = 0 AND ends_at > ? ORDER BY id DESC LIMIT 1",
            (guild[0], now),
        )
        active = cursor.fetchone()
        if not active:
            conn.close()
            return await ctx.send("Nenhuma missão ativa.")
            
        cursor.execute("SELECT last_action FROM player_guild_mission_actions WHERE guild_id = ? AND user_id = ?", (guild[0], user_id))
        last = cursor.fetchone()
        if last and now - (last[0] or 0) < 900:
            conn.close()
            return await ctx.send("Aguarde um pouco antes de contribuir de novo. Até herói precisa beber água.")
            
        power, avg_level = party_power_and_level(cursor, user_id)
        gain = max(150, int(power * (1 + guild[3] * 0.04)))
        progress = min(active[3], active[2] + gain)
        
        cursor.execute("UPDATE player_guild_missions SET progress = ? WHERE id = ?", (progress, active[0]))
        cursor.execute(
            "INSERT OR REPLACE INTO player_guild_mission_actions (guild_id, user_id, last_action) VALUES (?, ?, ?)",
            (guild[0], user_id, now),
        )
        
        msg = f"{ctx.author.mention} contribuiu com **{gain:,}** de progresso.\nMissão: **{progress:,}/{active[3]:,}**"
        
        if progress >= active[3]:
            mission = GUILD_MISSIONS[active[1]]
            cursor.execute("UPDATE player_guild_missions SET completed = 1 WHERE id = ?", (active[0],))
            cursor.execute(
                "UPDATE player_guilds SET gold_bank = gold_bank + ?, xp = xp + ?, raid_score = raid_score + ? WHERE id = ?",
                (mission["reward_bank"], mission["reward_xp"], mission["reward_score"], guild[0]),
            )
            cursor.execute("SELECT user_id FROM player_guild_members WHERE guild_id = ?", (guild[0],))
            members = [row[0] for row in cursor.fetchall()]
            
            for uid in members:
                conceder_ouro_escalavel(cursor, uid, mission["member_gold"], avg_level, guild_id=str(guild[0]), extra_mult=1.0)
                dar_xp_jogador(cursor, uid, mission.get("member_xp", 100))
                p_ids = get_equipped_party(cursor, uid)
                for h in p_ids:
                    dar_xp_heroi(cursor, int(h), mission.get("member_xp", 100))
                
                if mission.get("member_gems", 0) > 0:
                    cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (mission["member_gems"], uid))
                add_tickets(cursor, uid, mission.get("member_tickets", 0))
                
            level = self._level_up_guild(cursor, guild[0])
            msg += (
                f"\n🎉 Missão concluída! Banco +**{mission['reward_bank']:,} Gold**, XP +**{mission['reward_xp']}**, "
                f"score +**{mission['reward_score']:,}**.\nOs membros receberam o pagamento de Ouro, XP e Tickets. Guilda agora nível **{level}**."
            )
            
        conn.commit()
        conn.close()
        await ctx.send(msg)

    @guild_cmd.command(name="raid", aliases=["batalha"])
    async def raid(self, ctx):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, user_id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda.")
            
        guild_id, name, _, level, _, bank, _, _, _, _, _, _ = guild
        now = int(time.time())
        cursor.execute("SELECT boss_name, hp, max_hp, ends_at FROM player_guild_raids WHERE guild_id = ?", (guild_id,))
        raid = cursor.fetchone()
        
        if not raid or raid[3] < now or raid[1] <= 0:
            if not self._can_manage(guild):
                conn.close()
                return await ctx.send("Não há raid ativa. Só líder/oficial pode abrir uma.")
            cost = 750 * level
            if bank < cost:
                conn.close()
                return await ctx.send(f"A guilda precisa de **{cost:,} Gold** no banco para abrir raid.")
            max_hp = 5000 + level * 1400
            cursor.execute("UPDATE player_guilds SET gold_bank = gold_bank - ? WHERE id = ?", (cost, guild_id))
            cursor.execute(
                "INSERT OR REPLACE INTO player_guild_raids (guild_id, boss_name, hp, max_hp, started_at, ends_at) VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, f"Chefe de Guilda Nv {level}", max_hp, max_hp, now, now + 86400),
            )
            conn.commit()
            conn.close()
            embed = discord.Embed(
                title=f"Raid da Guilda {name}",
                description=f"**Chefe de Guilda Nv {level}** surgiu com **{max_hp:,} HP**.\n{hp_bar(max_hp, max_hp)}",
                color=discord.Color.dark_red(),
            )
            embed.add_field(name="Custo", value=f"{cost:,} Gold do banco", inline=True)
            embed.add_field(name="Duração", value="<t:{}:R>".format(now + 86400), inline=True)
            embed.set_footer(text="TutoriUAU: use `echo guild raid` para atacar. Coordenação opcional, caos provável.")
            return await ctx.send(embed=embed)

        cursor.execute("SELECT last_action FROM player_guild_raid_actions WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        last = cursor.fetchone()
        if last and now - (last[0] or 0) < 1800:
            conn.close()
            return await ctx.send("Você já atacou essa raid recentemente. O chefe pediu intervalo sindical.")
            
        boss_name, hp, max_hp, _ = raid
        power, avg_level = party_power_and_level(cursor, user_id)
        crit = random.random() < min(0.35, 0.08 + level * 0.01)
        phase = boss_phase(hp, max_hp)
        phase_mult = 1.25 if phase == "Fúria Final" else 1.10 if phase == "Quebra de Guarda" else 1.0
        damage = max(250, int(power * random.uniform(0.85, 1.25) * (1 + level * 0.05) * phase_mult * (1.6 if crit else 1.0)))
        hp = max(0, hp - damage)
        
        cursor.execute("UPDATE player_guild_raids SET hp = ? WHERE guild_id = ?", (hp, guild_id))
        cursor.execute("UPDATE player_guilds SET raid_score = raid_score + ? WHERE id = ?", (damage, guild_id))
        cursor.execute(
            "INSERT OR REPLACE INTO player_guild_raid_actions (guild_id, user_id, last_action) VALUES (?, ?, ?)",
            (guild_id, user_id, now),
        )
        
        result_lines = [
            f"{ctx.author.mention} causou **{damage:,}** em **{boss_name}**{' com crítico' if crit else ''}.",
            f"Fase: **{phase}**",
        ]
        color = discord.Color.orange()
        
        if hp <= 0:
            reward = 800 + level * 180
            cursor.execute("SELECT user_id FROM player_guild_members WHERE guild_id = ?", (guild_id,))
            members = [row[0] for row in cursor.fetchall()]
            
            for uid in members:
                conceder_ouro_escalavel(cursor, uid, reward, avg_level, guild_id=str(guild_id), extra_mult=1.0)
                xp_reward = 200 + level * 50
                dar_xp_jogador(cursor, uid, xp_reward)
                p_ids = get_equipped_party(cursor, uid)
                for h in p_ids:
                    dar_xp_heroi(cursor, int(h), xp_reward)
                    
            cursor.execute("UPDATE player_guilds SET xp = xp + ?, raid_score = raid_score + ? WHERE id = ?", (level * 120, max_hp, guild_id))
            cursor.execute("DELETE FROM player_guild_raids WHERE guild_id = ?", (guild_id,))
            self._level_up_guild(cursor, guild_id)
            result_lines.append(f"Chefe derrotado! Todos os membros receberam sua parte da recompensa de XP e Ouro.")
            color = discord.Color.green()
            
        conn.commit()
        conn.close()
        
        embed = discord.Embed(title=f"Raid da Guilda - {boss_name}", description="\n".join(result_lines), color=color)
        embed.add_field(name="HP do Boss", value=f"{hp_bar(hp, max_hp)}\n**{hp:,}/{max_hp:,}**", inline=False)
        embed.add_field(name="Log", value=f"`Poder usado: {power:,}`\n`Dano final: {damage:,}`", inline=False)
        embed.set_footer(text="TutoriUAU: raid agora tem ata, barra e sofrimento mensurável.")
        await ctx.send(embed=embed)

    @guild_cmd.command(name="caca", aliases=["caça", "hunt", "cacada", "caçada"])
    async def caca_guilda(self, ctx):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        guild = self._get_user_guild(cursor, user_id)
        if not guild:
            conn.close()
            return await ctx.send("Você não está em guilda. Caçada coletiva sem coletivo vira passeio perigoso.")

        guild_id, name, _, level, _, bank, _, _, _, _, _, _ = guild
        now = int(time.time())
        cursor.execute("SELECT boss_name, hp, max_hp, reward_gold, ends_at FROM player_guild_hunts WHERE guild_id = ?", (guild_id,))
        hunt = cursor.fetchone()

        if not hunt or hunt[4] < now or hunt[1] <= 0:
            if not self._can_manage(guild):
                conn.close()
                return await ctx.send("Não há caçada de guilda ativa. Só líder/oficial pode liderar uma expedição contra boss.")
            boss = random.choice(GUILD_HUNT_BOSSES)
            cost = int(boss["cost"] * (1 + level * 0.08))
            if bank < cost:
                conn.close()
                return await ctx.send(f"A guilda precisa de **{cost:,} Gold** no banco para liderar essa caçada.")
            max_hp = int(boss["hp"] * (1 + level * 0.12))
            reward_member = int(boss["reward_member"] * (1 + level * 0.05))
            
            cursor.execute("UPDATE player_guilds SET gold_bank = gold_bank - ? WHERE id = ?", (cost, guild_id))
            cursor.execute(
                """
                INSERT OR REPLACE INTO player_guild_hunts
                (guild_id, boss_name, hp, max_hp, reward_gold, started_by, started_at, ends_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (guild_id, boss["name"], max_hp, max_hp, reward_member, user_id, now, now + 18 * 3600),
            )
            conn.commit()
            conn.close()
            embed = discord.Embed(
                title=f"Caçada de Guilda - {boss['name']}",
                description=f"A guilda **{name}** abriu uma expedição contra boss.\n{hp_bar(max_hp, max_hp)}",
                color=discord.Color.dark_gold(),
            )
            embed.add_field(name="Custo", value=f"{cost:,} Gold do banco", inline=True)
            embed.add_field(name="Recompensa por membro", value=f"{reward_member:,} Gold base + chance de Gems", inline=True)
            embed.add_field(name="Tempo limite", value=f"<t:{now + 18 * 3600}:R>", inline=True)
            embed.set_footer(text="TutoriUAU: use `echo guild caca` para atacar. Levar lanche é recomendado.")
            return await ctx.send(embed=embed)

        cursor.execute("SELECT last_action FROM player_guild_hunt_actions WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        last = cursor.fetchone()
        if last and now - (last[0] or 0) < 1200:
            conn.close()
            return await ctx.send("Você já atacou essa caçada recentemente. O boss pediu 20 minutos de paz, abusado.")

        boss_name, hp, max_hp, reward_member, _ = hunt
        power, avg_level = party_power_and_level(cursor, user_id)
        crit = random.random() < min(0.40, 0.10 + level * 0.012)
        phase = boss_phase(hp, max_hp)
        damage = max(220, int(power * random.uniform(1.1, 1.7) * (1 + level * 0.035) * (1.5 if crit else 1.0)))
        hp = max(0, hp - damage)
        
        cursor.execute("UPDATE player_guild_hunts SET hp = ? WHERE guild_id = ?", (hp, guild_id))
        cursor.execute("SELECT damage FROM player_guild_hunt_actions WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        old_damage = (cursor.fetchone() or [0])[0] or 0
        cursor.execute(
            """
            INSERT OR REPLACE INTO player_guild_hunt_actions (guild_id, user_id, last_action, damage)
            VALUES (?, ?, ?, ?)
            """,
            (guild_id, user_id, now, old_damage + damage),
        )
        cursor.execute("UPDATE player_guilds SET raid_score = raid_score + ? WHERE id = ?", (damage, guild_id))
        add_stat(cursor, user_id, "guild_hunts", 1)

        result_lines = [
            f"{ctx.author.mention} atacou **{boss_name}** e causou **{damage:,}**{' CRÍTICO' if crit else ''}.",
            f"Fase atual: **{phase}**",
        ]
        color = discord.Color.dark_gold()
        
        if hp <= 0:
            bank_reward = int(max_hp * 0.35)
            cursor.execute("SELECT user_id FROM player_guild_members WHERE guild_id = ?", (guild_id,))
            members = [row[0] for row in cursor.fetchall()]
            gem_bonus = 1 if random.random() < 0.18 else 0
            
            for uid in members:
                conceder_ouro_escalavel(cursor, uid, reward_member, avg_level, guild_id=str(guild_id), extra_mult=1.0)
                if gem_bonus > 0:
                    cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (gem_bonus, uid))
                xp_reward = level * 20
                dar_xp_jogador(cursor, uid, xp_reward)
                p_ids = get_equipped_party(cursor, uid)
                for h in p_ids:
                    dar_xp_heroi(cursor, int(h), xp_reward)
                    
            cursor.execute(
                "UPDATE player_guilds SET gold_bank = gold_bank + ?, xp = xp + ?, raid_score = raid_score + ? WHERE id = ?",
                (bank_reward, level * 160, max_hp, guild_id),
            )
            cursor.execute("DELETE FROM player_guild_hunts WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM player_guild_hunt_actions WHERE guild_id = ?", (guild_id,))
            new_level = self._level_up_guild(cursor, guild_id)
            
            result_lines.append(
                f"Boss derrotado! Cada membro recebeu recompensas valiosas de XP e Ouro{f' e **{gem_bonus} Gem rara**' if gem_bonus else ''}. "
                f"Banco +**{bank_reward:,} Gold**. Guilda nível **{new_level}**."
            )
            color = discord.Color.green()

        conn.commit()
        conn.close()
        embed = discord.Embed(title=f"Caçada de Guilda - {boss_name}", description="\n".join(result_lines), color=color)
        embed.add_field(name="HP do Boss", value=f"{hp_bar(hp, max_hp)}\n**{hp:,}/{max_hp:,}**", inline=False)
        embed.add_field(name="Seu avanço", value=f"Dano total registrado: **{old_damage + damage:,}**", inline=True)
        embed.add_field(name="Log", value=f"`Poder da party: {power:,}`\n`Dano desta ação: {damage:,}`", inline=True)
        embed.set_footer(text="TutoriUAU: caçada coletiva agora parece menos planilha e mais pancadaria organizada.")
        await ctx.send(embed=embed)

    @guild_cmd.command(name="ranking")
    async def ranking(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_guild_db(cursor)
        cursor.execute("""
            SELECT id, name, level, gold_bank, raid_score
            FROM player_guilds
            ORDER BY raid_score DESC, level DESC, gold_bank DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        text = "\n".join(
            f"**{i}º** `{gid}` **{name}** - Nv {level} | Score {score:,} | Banco {bank:,}"
            for i, (gid, name, level, bank, score) in enumerate(rows, 1)
        )
        await ctx.send(embed=discord.Embed(title="Ranking de Guildas", description=text or "Nenhuma guilda criada.", color=discord.Color.gold()))


async def setup(bot):
    await bot.add_cog(Guilds(bot))