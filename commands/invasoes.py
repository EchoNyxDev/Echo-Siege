import asyncio
import datetime
import os
import random
import sqlite3
import sys

import discord
from discord.ext import commands, tasks

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.calamidades import RAID_BOSSES
    from data.dungeons import DUNGEONS
    from data.enemies import ENEMIES
    from data.equipamentos import EQUIPAMENTOS
    from data.heroes import HEROES
    from utils.affinity import apply_affinity_bonus
    from utils.combat import simular_combate_tatico
    from utils.equipment import get_equipment_bonus
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.player_bonuses import apply_battle_hp_bonus
    from utils.rewards import average_party_level, scale_combat_rewards
    from utils.skills import get_hero_skill_ids, resolve_skill_list
    from utils.xp_system import dar_xp_heroi, dar_xp_jogador
except ModuleNotFoundError:
    RAID_BOSSES, DUNGEONS, ENEMIES, EQUIPAMENTOS, HEROES = {}, {}, {}, {}, {}

    def apply_affinity_bonus(party_data, heroes):
        return party_data

    def apply_battle_hp_bonus(cursor, user_id, party_data):
        return party_data

    def average_party_level(party):
        return 1

    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {"hp": 100, "atk": 10, "matk": 10, "def": 5, "spd": 10, "crt": 5, "level": level}

    def dar_xp_heroi(cursor, hero_db_id, xp):
        return None

    def dar_xp_jogador(cursor, user_id, xp):
        return None

    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}

    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []

    def normalize_class(value):
        return str(value or "neutro").lower()

    def resolve_skill_list(habilidades):
        return habilidades or []

    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50):
        return gold, xp


BRT = datetime.timezone(datetime.timedelta(hours=-3))
ROLE_INVOCADOR_ID = 1512228151382511748
CITY_STAT_CAP = 100

TYPE_ALIASES = {
    "diaria": "raid",
    "diária": "raid",
    "daily": "raid",
    "raid": "raid",
    "raids": "raid",
    "semanal": "boss",
    "weekly": "boss",
    "boss": "boss",
    "chefe": "boss",
    "mensal": "calamidade",
    "monthly": "calamidade",
    "calamidade": "calamidade",
    "calamity": "calamidade",
}

INVASION_TYPES = {
    "raid": {
        "label": "Raid Diária",
        "short": "raid",
        "schedule": "todos os dias às 13:00",
        "damage_hp": 2000,
        "damage_moral": 2,
        "victory_moral": 2,
        "prosperity": 2,
        "reward": (210, 70),
        "color": discord.Color.orange(),
        "description": "Monstros das dungeons avançam em ondas contra a muralha.",
        "defeat_title": "Raid rompeu a defesa!",
        "victory_title": "Raid repelida!",
    },
    "boss": {
        "label": "Boss Semanal",
        "short": "boss",
        "schedule": "todo sábado às 19:00",
        "damage_hp": 5000,
        "damage_moral": 5,
        "victory_moral": 10,
        "prosperity": 5,
        "reward": (520, 170),
        "color": discord.Color.red(),
        "description": "Um chefe de dungeon aparece para testar a cidade, porque paz era aparentemente opcional.",
        "defeat_title": "Boss venceu a defesa!",
        "victory_title": "Boss derrotado!",
    },
    "calamidade": {
        "label": "Calamidade Mensal",
        "short": "calamidade",
        "schedule": "último dia do mês às 22:00",
        "damage_hp": 10000,
        "damage_moral": 10,
        "victory_moral": 20,
        "prosperity": 10,
        "reward": (1100, 360),
        "color": discord.Color.dark_purple(),
        "description": "Uma ameaça mensal tenta transformar Lugnica em nota de rodapé histórica.",
        "defeat_title": "Calamidade devastou a muralha!",
        "victory_title": "Calamidade contida!",
    },
}


def normalize_invasion_type(value):
    key = str(value or "raid").lower().strip().replace("_", "-")
    key = key.replace("-", "")
    normalized_aliases = {alias.replace("-", ""): target for alias, target in TYPE_ALIASES.items()}
    return normalized_aliases.get(key)


def _table_info(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        return cursor.fetchall()
    except sqlite3.OperationalError:
        return []


def _table_columns(cursor, table):
    return {row[1] for row in _table_info(cursor, table)}


def _add_column_if_missing(cursor, table, column, ddl):
    if column not in _table_columns(cursor, table):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _create_raid_registrations(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS raid_registrations (
            user_id TEXT NOT NULL,
            raid_type TEXT NOT NULL DEFAULT 'raid',
            guild_id TEXT NOT NULL DEFAULT 'global',
            registered_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
        """
    )


def _ensure_raid_registrations(cursor):
    info = _table_info(cursor, "raid_registrations")
    if not info:
        _create_raid_registrations(cursor)
        return

    columns = {row[1] for row in info}
    pk_columns = [row[1] for row in sorted((row for row in info if row[5]), key=lambda row: row[5])]
    needs_rebuild = (
        not {"user_id", "raid_type", "guild_id", "registered_at"}.issubset(columns)
        or pk_columns != ["user_id", "guild_id"]
    )
    if not needs_rebuild:
        return

    cursor.execute("ALTER TABLE raid_registrations RENAME TO raid_registrations_old")
    _create_raid_registrations(cursor)
    old_columns = _table_columns(cursor, "raid_registrations_old")
    if "user_id" in old_columns:
        raid_type_expr = "COALESCE(raid_type, 'raid')" if "raid_type" in old_columns else "'raid'"
        guild_id_expr = "COALESCE(guild_id, 'global')" if "guild_id" in old_columns else "'global'"
        registered_at_expr = "COALESCE(registered_at, 0)" if "registered_at" in old_columns else "0"
        cursor.execute(
            f"""
            INSERT OR IGNORE INTO raid_registrations (user_id, raid_type, guild_id, registered_at)
            SELECT DISTINCT user_id, {raid_type_expr}, {guild_id_expr}, {registered_at_expr}
            FROM raid_registrations_old
            WHERE user_id IS NOT NULL
            """
        )
    cursor.execute("DROP TABLE raid_registrations_old")


def ensure_invasion_db(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS server_config (
            guild_id TEXT PRIMARY KEY,
            raid_channel_id TEXT
        )
        """
    )
    _add_column_if_missing(cursor, "server_config", "guild_id", "TEXT")
    _add_column_if_missing(cursor, "server_config", "raid_channel_id", "TEXT")

    _ensure_raid_registrations(cursor)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS city_stats (
            id INTEGER PRIMARY KEY,
            hp INTEGER DEFAULT 100000,
            max_hp INTEGER DEFAULT 100000,
            moral INTEGER DEFAULT 100,
            suprimentos INTEGER DEFAULT 0,
            max_suprimentos INTEGER DEFAULT 5000,
            prosperidade INTEGER DEFAULT 0
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cidades (
            guild_id TEXT PRIMARY KEY,
            nome TEXT DEFAULT 'Capital de Lugnica',
            hp INTEGER DEFAULT 100000,
            max_hp INTEGER DEFAULT 100000,
            moral INTEGER DEFAULT 100,
            suprimentos INTEGER DEFAULT 0,
            max_suprimentos INTEGER DEFAULT 5000,
            prosperidade INTEGER DEFAULT 0
        )
        """
    )
    for column, ddl in {
        "guild_id": "TEXT",
        "nome": "TEXT DEFAULT 'Capital de Lugnica'",
        "hp": "INTEGER DEFAULT 100000",
        "max_hp": "INTEGER DEFAULT 100000",
        "moral": "INTEGER DEFAULT 100",
        "suprimentos": "INTEGER DEFAULT 0",
        "max_suprimentos": "INTEGER DEFAULT 5000",
        "prosperidade": "INTEGER DEFAULT 0",
    }.items():
        _add_column_if_missing(cursor, "cidades", column, ddl)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS invasion_schedule_runs (
            guild_id TEXT NOT NULL,
            raid_type TEXT NOT NULL,
            scheduled_key TEXT NOT NULL,
            channel_id TEXT,
            created_at INTEGER DEFAULT 0,
            PRIMARY KEY (guild_id, raid_type, scheduled_key)
        )
        """
    )
    cursor.execute("INSERT OR IGNORE INTO city_stats (id) VALUES (1)")
    cursor.execute(
        "UPDATE city_stats SET moral = ? WHERE moral > ?",
        (CITY_STAT_CAP, CITY_STAT_CAP),
    )
    cursor.execute(
        "UPDATE city_stats SET prosperidade = ? WHERE prosperidade > ?",
        (CITY_STAT_CAP, CITY_STAT_CAP),
    )
    cursor.execute(
        "UPDATE cidades SET moral = ? WHERE moral > ?",
        (CITY_STAT_CAP, CITY_STAT_CAP),
    )
    cursor.execute(
        "UPDATE cidades SET prosperidade = ? WHERE prosperidade > ?",
        (CITY_STAT_CAP, CITY_STAT_CAP),
    )


def _ensure_city(cursor, guild_id):
    cursor.execute(
        """
        INSERT OR IGNORE INTO cidades
        (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
        VALUES (?, 'Capital de Lugnica', 100000, 100000, 100, 0, 5000, 0)
        """,
        (str(guild_id),),
    )
    cursor.execute(
        "UPDATE cidades SET moral = ? WHERE guild_id = ? AND moral > ?",
        (CITY_STAT_CAP, str(guild_id), CITY_STAT_CAP),
    )
    cursor.execute(
        "UPDATE cidades SET prosperidade = ? WHERE guild_id = ? AND prosperidade > ?",
        (CITY_STAT_CAP, str(guild_id), CITY_STAT_CAP),
    )


def _parse_level_range(value):
    raw = str(value or "1-10").replace(" ", "")
    try:
        left, right = raw.split("-", 1)
        return int(left), int(right)
    except (ValueError, TypeError):
        return 1, 10


def _enemy_skills(enemy_data):
    skills = []
    if enemy_data.get("habilidades"):
        skills.extend(enemy_data.get("habilidades") or [])
    if enemy_data.get("habilidade"):
        skills.append(enemy_data.get("habilidade"))
    return resolve_skill_list(skills)


def _party_metrics(team_a):
    total_hp = sum(int(hero.get("stats", {}).get("hp", 100) or 100) for hero in team_a)
    total_offense = sum(
        max(
            int(hero.get("stats", {}).get("atk", 10) or 10),
            int(hero.get("stats", {}).get("matk", 10) or 10),
        )
        for hero in team_a
    )
    total_def = sum(int(hero.get("stats", {}).get("def", 5) or 5) for hero in team_a)
    count = max(1, len(team_a))
    return {
        "count": count,
        "total_hp": max(100, total_hp),
        "total_offense": max(40, total_offense),
        "avg_def": max(5, total_def / count),
        "avg_level": max(1, int(average_party_level(team_a) or 1)),
    }


def _scale_enemy_stats(enemy_data, invasion_type, metrics, enemy_count=1):
    enemy_count = max(1, int(enemy_count or 1))
    kind = INVASION_TYPES[invasion_type]
    hp_factor = {"raid": 4.8, "boss": 12.0, "calamidade": 20.0}[invasion_type]
    damage_factor = {"raid": 0.08, "boss": 0.11, "calamidade": 0.14}[invasion_type]
    defense_factor = {"raid": 0.75, "boss": 1.00, "calamidade": 1.20}[invasion_type]

    jitter = random.uniform(0.94, 1.10)
    hp = int((metrics["total_offense"] * hp_factor / enemy_count) * jitter)
    offense = int((metrics["total_hp"] * damage_factor / enemy_count) * jitter)
    defense = int((metrics["avg_def"] * defense_factor) + (metrics["avg_level"] * 1.4))

    template_atk = int(enemy_data.get("atk", 0) or 0)
    template_matk = int(enemy_data.get("matk", 0) or 0)
    uses_magic = template_matk > template_atk

    return {
        "hp": max(80, hp),
        "atk": 0 if uses_magic else max(12, offense),
        "matk": max(12, offense) if uses_magic else max(0, int(template_matk * 0.35)),
        "def": max(5, min(650, defense)),
        "spd": max(5, min(55, int(enemy_data.get("spd", 12) or 12))),
        "crt": max(0, min(45, int(enemy_data.get("crt", 5) or 5))),
        "level": metrics["avg_level"],
    }


def _entity_from_enemy(enemy_id, enemy_data, invasion_type, metrics, enemy_count, suffix=""):
    name = enemy_data.get("nome", enemy_id)
    config = INVASION_TYPES[invasion_type]
    return {
        "id": f"{enemy_id}{suffix}",
        "nome": f"{name} ({config['label']})",
        "classe": enemy_data.get("tipo", "monstro"),
        "stats": _scale_enemy_stats(enemy_data, invasion_type, metrics, enemy_count),
        "habilidades": _enemy_skills(enemy_data),
    }


def _dungeon_candidates_for_level(avg_level):
    candidates = []
    for dungeon_id, dungeon in DUNGEONS.items():
        min_level, max_level = _parse_level_range(dungeon.get("level_rec"))
        midpoint = (min_level + max_level) / 2
        candidates.append((abs(midpoint - avg_level), dungeon_id, dungeon))
    candidates.sort(key=lambda item: item[0])
    return [dungeon for _, _, dungeon in candidates[:3]] or list(DUNGEONS.values())


def build_invasion_enemies(invasion_type, team_a, participants):
    metrics = _party_metrics(team_a)
    participants = max(1, int(participants or 1))

    if invasion_type == "raid":
        dungeons = _dungeon_candidates_for_level(metrics["avg_level"])
        dungeon = random.choice(dungeons)
        floor = random.choice(list((dungeon.get("andares") or {}).values()))
        pool = [
            enemy_id
            for enemy_id in (floor.get("inimigos") or {}).keys()
            if enemy_id in ENEMIES
        ]
        if not pool:
            pool = [enemy_id for enemy_id, data in ENEMIES.items() if data.get("tipo") == "comum"]
        enemy_count = max(2, min(6, participants + 2))
        selected_ids = random.choices(pool, k=enemy_count)
        return [
            _entity_from_enemy(enemy_id, ENEMIES[enemy_id], "raid", metrics, enemy_count, f"_{index}")
            for index, enemy_id in enumerate(selected_ids, start=1)
        ]

    if invasion_type == "boss":
        boss_ids = []
        for dungeon in DUNGEONS.values():
            for floor in (dungeon.get("andares") or {}).values():
                boss_id = floor.get("boss")
                if boss_id in ENEMIES:
                    boss_ids.append(boss_id)
        if not boss_ids:
            boss_ids = [enemy_id for enemy_id, data in ENEMIES.items() if data.get("tipo") == "boss"]
        boss_id = random.choice(boss_ids)
        return [_entity_from_enemy(boss_id, ENEMIES[boss_id], "boss", metrics, 1)]

    calamity_pool = [
        (boss_id, data)
        for boss_id, data in RAID_BOSSES.items()
        if data.get("tipo") in {"mensal", "calamidade"}
    ] or list(RAID_BOSSES.items())
    boss_id, boss_data = random.choice(calamity_pool)
    return [_entity_from_enemy(boss_id, boss_data, "calamidade", metrics, 1)]


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
    time_ids = [p_data[0]] + [hero_id for hero_id in (team if team else []) if hero_id is not None]

    party_data = []
    for hero_db_id in time_ids:
        cursor.execute(
            "SELECT hero_id, stars, level, equip_atk, equip_def, equip_livre FROM heroes WHERE id = ?",
            (int(hero_db_id),),
        )
        hero = cursor.fetchone()
        if not hero:
            continue

        h_id, stars, level, e_atk, e_def, e_livre = hero
        h_data = HEROES.get(h_id, {})
        equipment_bonuses = [
            get_equipment_bonus(cursor, user_id, eq_name, EQUIPAMENTOS)
            for eq_name in [e_atk, e_def, e_livre]
            if eq_name and eq_name in EQUIPAMENTOS
        ]
        stats = calculate_hero_stats(h_data, stars, level, equipment_bonuses)
        class_name = normalize_class(h_data.get("classe", "neutro"))
        skill_ids = get_hero_skill_ids(h_data, stars, h_data.get("raridade", 0))
        party_data.append(
            {
                "id": str(hero_db_id),
                "hero_id": h_id,
                "nome": f"{h_data.get('nome', 'Herói')} ({user_name})",
                "classe": class_name,
                "level": level,
                "stats": stats,
                "habilidades": skill_ids,
            }
        )

    party_data = apply_affinity_bonus(party_data, HEROES)
    party_data = apply_battle_hp_bonus(cursor, user_id, party_data)
    conn.commit()
    conn.close()
    return party_data


class RaidRegisterView(discord.ui.View):
    def __init__(self, raid_type, guild_id):
        super().__init__(timeout=None)
        self.raid_type = raid_type
        self.guild_id = str(guild_id)

    @discord.ui.button(label="Registrar defesa", style=discord.ButtonStyle.success, emoji="⚔️")
    async def btn_register(self, interaction, button):
        user_id = str(interaction.user.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)

        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        if not player or not player[0]:
            conn.close()
            return await interaction.response.send_message(
                "❌ Equipe um herói principal com `echo main <ID>` antes de defender a muralha.",
                ephemeral=True,
            )

        cursor.execute(
            "SELECT 1 FROM raid_registrations WHERE user_id = ? AND guild_id = ?",
            (user_id, self.guild_id),
        )
        if cursor.fetchone():
            conn.close()
            return await interaction.response.send_message(
                "⚠️ Você já registrou sua defesa neste servidor.",
                ephemeral=True,
            )

        cursor.execute(
            """
            INSERT INTO raid_registrations (user_id, raid_type, guild_id, registered_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, self.raid_type, self.guild_id, int(datetime.datetime.now(BRT).timestamp())),
        )
        conn.commit()
        conn.close()
        await interaction.response.send_message(
            "✅ Defesa registrada. TutoriUAU anotou: presença física opcional, responsabilidade emocional obrigatória.",
            ephemeral=True,
        )


class Invasoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_raids = {}
        self.active_raid_task = None
        self.active_msg = None
        self.current_raid_type = None
        self.current_channel = None
        self._init_db()
        self.invasion_scheduler.start()

    def cog_unload(self):
        self.invasion_scheduler.cancel()
        for state in list(self.active_raids.values()):
            task = state.get("task")
            if task:
                task.cancel()

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        conn.commit()
        conn.close()

    def _clear_active_raid(self, guild_id=None):
        if guild_id is None:
            self.active_raids.clear()
        else:
            self.active_raids.pop(str(guild_id), None)
        self.active_raid_task = None
        self.active_msg = None
        self.current_raid_type = None
        self.current_channel = None

    def get_raid_channel(self, guild_id):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        cursor.execute("SELECT raid_channel_id FROM server_config WHERE guild_id = ?", (str(guild_id),))
        data = cursor.fetchone()
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

        tipo_raid = normalize_invasion_type(tipo_raid)
        if not tipo_raid:
            raise ValueError("Tipo de invasão inválido. Use raid, boss ou calamidade.")

        duration = 60 if int(duration or 600) <= 60 else 600
        guild_id = str(channel.guild.id)
        config = INVASION_TYPES[tipo_raid]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        cursor.execute("DELETE FROM raid_registrations WHERE guild_id = ?", (guild_id,))
        conn.commit()
        conn.close()

        old_state = self.active_raids.get(guild_id)
        if old_state and old_state.get("task"):
            old_state["task"].cancel()

        minutes = duration // 60
        embed = discord.Embed(
            title=f"🚨 {config['label']} em andamento",
            description=(
                f"{config['description']}\n\n"
                f"Tempo de registro: **{minutes} minuto{'s' if minutes != 1 else ''}**.\n"
                "Clique no botão para defender este servidor."
            ),
            color=config["color"],
        )
        embed.add_field(name="Impacto se perder", value=f"-{config['damage_hp']:,} HP da muralha\n-{config['damage_moral']} moral", inline=True)
        embed.add_field(name="Moral se vencer", value=f"+{config['victory_moral']} moral", inline=True)
        embed.add_field(name="Agenda", value=config["schedule"], inline=False)
        embed.set_footer(text="TutoriUAU: se só assistir dramaticamente resolvesse, eu já teria zerado o jogo.")

        view = RaidRegisterView(tipo_raid, guild_id)
        mention_role = channel.guild.get_role(ROLE_INVOCADOR_ID)
        content = mention_role.mention if mention_role else f"⚔️ **{config['label']} iniciada!**"
        msg = await channel.send(
            content=content,
            embed=embed,
            view=view,
            allowed_mentions=discord.AllowedMentions(roles=True),
        )

        task = asyncio.create_task(self.esperar_e_executar(channel, tipo_raid, duration))
        self.active_raids[guild_id] = {"task": task, "message": msg, "type": tipo_raid, "channel": channel}
        self.active_raid_task = task
        self.active_msg = msg
        self.current_raid_type = tipo_raid
        self.current_channel = channel
        return msg

    async def esperar_e_executar(self, channel, tipo_raid, duration):
        try:
            await asyncio.sleep(duration)
            await self.executar_batalha(channel, tipo_raid)
        except asyncio.CancelledError:
            pass

    def _apply_city_result(self, cursor, guild_id, tipo_raid, victory):
        config = INVASION_TYPES[tipo_raid]
        _ensure_city(cursor, guild_id)
        if victory:
            cursor.execute(
                """
                UPDATE cidades
                SET moral = min(100, max(0, moral) + ?),
                    prosperidade = min(100, max(0, prosperidade) + ?)
                WHERE guild_id = ?
                """,
                (config["victory_moral"], config["prosperity"], str(guild_id)),
            )
            cursor.execute(
                """
                UPDATE city_stats
                SET moral = min(100, max(0, moral) + ?),
                    prosperidade = min(100, max(0, prosperidade) + ?)
                WHERE id = 1
                """,
                (config["victory_moral"], config["prosperity"]),
            )
        else:
            cursor.execute(
                """
                UPDATE cidades
                SET moral = max(0, min(100, moral) - ?),
                    hp = max(0, hp - ?)
                WHERE guild_id = ?
                """,
                (config["damage_moral"], config["damage_hp"], str(guild_id)),
            )
            cursor.execute(
                """
                UPDATE city_stats
                SET moral = max(0, min(100, moral) - ?),
                    hp = max(0, hp - ?)
                WHERE id = 1
                """,
                (config["damage_moral"], config["damage_hp"]),
            )

    async def _finish_no_defenders(self, channel, tipo_raid, cursor, guild_id):
        config = INVASION_TYPES[tipo_raid]
        self._apply_city_result(cursor, guild_id, tipo_raid, victory=False)
        embed = discord.Embed(
            title=config["defeat_title"],
            description=(
                "Ninguém registrou defesa a tempo.\n\n"
                f"🧱 Muralha: **-{config['damage_hp']:,} HP**\n"
                f"🧭 Moral: **-{config['damage_moral']}**"
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text="TutoriUAU: a muralha tentou defender sozinha. Spoiler: ela não assina ficha de personagem.")
        await channel.send(embed=embed)

    async def executar_batalha(self, channel, tipo_raid):
        tipo_raid = normalize_invasion_type(tipo_raid)
        if not tipo_raid:
            return await channel.send("❌ Tipo de invasão inválido.")

        guild_id = str(channel.guild.id)
        state = self.active_raids.get(guild_id, {})
        active_msg = state.get("message")
        if active_msg:
            try:
                await active_msg.delete()
            except discord.HTTPException:
                pass

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        cursor.execute(
            "SELECT user_id FROM raid_registrations WHERE raid_type = ? AND guild_id = ?",
            (tipo_raid, guild_id),
        )
        registrados = [row[0] for row in cursor.fetchall()]

        if not registrados:
            await self._finish_no_defenders(channel, tipo_raid, cursor, guild_id)
            cursor.execute("DELETE FROM raid_registrations WHERE guild_id = ?", (guild_id,))
            conn.commit()
            conn.close()
            self._clear_active_raid(guild_id)
            return

        team_a = []
        for user_id in registrados:
            user = self.bot.get_user(int(user_id))
            display_name = user.display_name if user else "Defensor"
            party = puxar_party_para_combate(user_id, display_name)
            if party:
                team_a.extend(party)

        if not team_a:
            await self._finish_no_defenders(channel, tipo_raid, cursor, guild_id)
            cursor.execute("DELETE FROM raid_registrations WHERE guild_id = ?", (guild_id,))
            conn.commit()
            conn.close()
            self._clear_active_raid(guild_id)
            return

        team_b = build_invasion_enemies(tipo_raid, team_a, len(registrados))
        vitoria, log_batalha = simular_combate_tatico(team_a, team_b)
        config = INVASION_TYPES[tipo_raid]

        embed = discord.Embed(color=discord.Color.green() if vitoria else discord.Color.red())
        if vitoria:
            base_gold, base_xp = config["reward"]
            gold_ganho, xp_ganho = scale_combat_rewards(base_gold, base_xp, average_party_level(team_a))
            for user_id in registrados:
                cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (gold_ganho, user_id))
                dar_xp_jogador(cursor, user_id, xp_ganho)
                party = puxar_party_para_combate(user_id, "Temp")
                if party:
                    for hero in party:
                        dar_xp_heroi(cursor, int(hero["id"]), xp_ganho)

            self._apply_city_result(cursor, guild_id, tipo_raid, victory=True)
            embed.title = f"✅ {config['victory_title']}"
            embed.description = (
                f"Os defensores de **{channel.guild.name}** venceram.\n\n"
                f"Recompensa por defensor: **{gold_ganho} Gold** e **{xp_ganho} XP**\n"
                f"🧭 Moral: **+{config['victory_moral']}**"
            )
        else:
            self._apply_city_result(cursor, guild_id, tipo_raid, victory=False)
            embed.title = f"☠️ {config['defeat_title']}"
            embed.description = (
                f"A defesa de **{channel.guild.name}** caiu.\n\n"
                f"🧱 Muralha: **-{config['damage_hp']:,} HP**\n"
                f"🧭 Moral: **-{config['damage_moral']}**"
            )

        enemies_text = "\n".join(f"• {enemy['nome']}" for enemy in team_b)
        embed.add_field(name="Ameaça", value=enemies_text[:1024], inline=False)
        embed.add_field(name="Log tático", value=log_batalha[:1024], inline=False)
        embed.set_footer(text="TutoriUAU: relatório entregue. A matemática sobreviveu, por enquanto.")

        cursor.execute("DELETE FROM raid_registrations WHERE guild_id = ?", (guild_id,))
        conn.commit()
        conn.close()
        await channel.send(embed=embed)
        self._clear_active_raid(guild_id)

    async def _trigger_scheduled_invasion(self, tipo_raid, scheduled_key):
        await self.bot.wait_until_ready()
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_invasion_db(cursor)
        cursor.execute("SELECT guild_id, raid_channel_id FROM server_config WHERE raid_channel_id IS NOT NULL")
        configs = cursor.fetchall()

        now_ts = int(datetime.datetime.now(BRT).timestamp())
        for guild_id, channel_id in configs:
            channel = None
            try:
                channel = self.bot.get_channel(int(channel_id))
            except (TypeError, ValueError):
                channel = None
            if not channel or not getattr(channel, "guild", None):
                continue

            cursor.execute(
                """
                INSERT OR IGNORE INTO invasion_schedule_runs
                (guild_id, raid_type, scheduled_key, channel_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(guild_id), tipo_raid, scheduled_key, str(channel_id), now_ts),
            )
            if cursor.rowcount == 0:
                continue
            conn.commit()
            try:
                await self.iniciar_fase_registro(channel, tipo_raid, is_manual=False, duration=600)
            except (discord.HTTPException, ValueError):
                continue

        conn.commit()
        conn.close()

    @tasks.loop(minutes=1)
    async def invasion_scheduler(self):
        now = datetime.datetime.now(BRT)
        if now.minute != 0:
            return

        if now.hour == 13:
            await self._trigger_scheduled_invasion("raid", f"raid:{now:%Y-%m-%d}")

        if now.weekday() == 5 and now.hour == 19:
            await self._trigger_scheduled_invasion("boss", f"boss:{now:%Y-%m-%d}")

        tomorrow = now.date() + datetime.timedelta(days=1)
        if tomorrow.day == 1 and now.hour == 22:
            await self._trigger_scheduled_invasion("calamidade", f"calamidade:{now:%Y-%m}")

    @invasion_scheduler.before_loop
    async def before_invasion_scheduler(self):
        await self.bot.wait_until_ready()

    @commands.command(name="raid_spawn")
    async def trigger_manual_raid(self, ctx, tipo: str = "raid", time_skip=None):
        if not ctx.guild:
            return await ctx.send("❌ Você deve usar este comando em um servidor.")

        tipo_raid = normalize_invasion_type(tipo)
        if not tipo_raid:
            return await ctx.send("Use `echo raid_spawn raid`, `echo raid_spawn boss` ou `echo raid_spawn calamidade`.")

        canal = self.get_raid_channel(ctx.guild.id) or ctx.channel
        skip_text = str(time_skip or "").lower().replace("_", "-").replace(" ", "-")
        duration = 60 if time_skip is True or skip_text in {"time-skip", "timeskip", "skip"} else 600
        await self.iniciar_fase_registro(canal, tipo_raid, is_manual=True, duration=duration)
        await ctx.send(
            f"✅ {INVASION_TYPES[tipo_raid]['label']} iniciada em {canal.mention}. "
            f"Registro por **{duration // 60} minuto(s)**."
        )

    @commands.command(name="raid_timeskip")
    async def force_timeskip(self, ctx):
        if not ctx.guild:
            return await ctx.send("❌ Use em um servidor.")

        guild_id = str(ctx.guild.id)
        state = self.active_raids.get(guild_id)
        if not state:
            return await ctx.send("❌ Nenhuma invasão pendente neste servidor.")

        task = state.get("task")
        if task:
            task.cancel()
        await self.executar_batalha(state["channel"], state["type"])


async def setup(bot):
    await bot.add_cog(Invasoes(bot))
