import sqlite3


def add_column(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


conn = sqlite3.connect("players.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players(
    user_id TEXT PRIMARY KEY,
    gold INTEGER DEFAULT 0,
    gems INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    stamina INTEGER DEFAULT 100,
    max_stamina INTEGER DEFAULT 100,
    main_hero TEXT
)
""")

for column, ddl in {
    "gold": "INTEGER DEFAULT 0",
    "gems": "INTEGER DEFAULT 0",
    "level": "INTEGER DEFAULT 1",
    "xp": "INTEGER DEFAULT 0",
    "stamina": "INTEGER DEFAULT 100",
    "max_stamina": "INTEGER DEFAULT 100",
    "main_hero": "TEXT",
    "last_hunt": "REAL DEFAULT 0",
    "total_hunts": "INTEGER DEFAULT 0",
    "last_adventure": "REAL DEFAULT 0",
    "last_dungeon": "REAL DEFAULT 0",
    "last_arena": "REAL DEFAULT 0",
    "arena_record": "INTEGER DEFAULT 0",
    "pvp_rating": "INTEGER DEFAULT 0",
    "pvp_wins": "INTEGER DEFAULT 0",
    "pvp_losses": "INTEGER DEFAULT 0",
    "buff_xp": "INTEGER DEFAULT 0",
    "buff_gold": "INTEGER DEFAULT 0",
    "main_pet": "TEXT",
    "battle_hp_bonus": "INTEGER DEFAULT 0",
    "last_daily": "TEXT DEFAULT ''",
    "daily_streak": "INTEGER DEFAULT 0",
}.items():
    add_column(cursor, "players", column, ddl)

cursor.execute("""
    UPDATE players
    SET pvp_rating = 0
    WHERE COALESCE(pvp_wins, 0) = 0
      AND COALESCE(pvp_losses, 0) = 0
      AND COALESCE(pvp_rating, 0) = 1000
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS heroes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    hero_id TEXT,
    rarity INTEGER,
    stars INTEGER DEFAULT 1,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    equip_atk TEXT,
    equip_def TEXT,
    equip_livre TEXT
)
""")

for column, ddl in {
    "equip_atk": "TEXT",
    "equip_def": "TEXT",
    "equip_livre": "TEXT",
}.items():
    add_column(cursor, "heroes", column, ddl)

cursor.execute("""
CREATE TABLE IF NOT EXISTS pets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    pet_id TEXT,
    pet_name TEXT,
    rarity INTEGER,
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    item_name TEXT,
    quantity INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dungeon_progress(
    user_id TEXT PRIMARY KEY,
    dungeon_id INTEGER DEFAULT 1,
    highest_area INTEGER DEFAULT 1
)
""")

for column, ddl in {
    "highest_dungeon": "INTEGER DEFAULT 1",
    "highest_area": "INTEGER DEFAULT 1",
}.items():
    add_column(cursor, "dungeon_progress", column, ddl)

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams(
    user_id TEXT PRIMARY KEY,
    slot_1 TEXT,
    slot_2 TEXT,
    slot_3 TEXT,
    slot_4 TEXT,
    slot_5 TEXT
)
""")
add_column(cursor, "teams", "pet_slot", "TEXT")

cursor.execute("""
CREATE TABLE IF NOT EXISTS summon_data(
    user_id TEXT PRIMARY KEY,
    summon_tickets INTEGER DEFAULT 0,
    shop_level INTEGER DEFAULT 1,
    pity_4 INTEGER DEFAULT 0,
    pity_5 INTEGER DEFAULT 0,
    total_summons INTEGER DEFAULT 0,
    total_1_star INTEGER DEFAULT 0,
    total_2_star INTEGER DEFAULT 0,
    total_3_star INTEGER DEFAULT 0,
    total_4_star INTEGER DEFAULT 0,
    total_5_star INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS equipment_upgrades(
    user_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    level INTEGER DEFAULT 0,
    refine INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_name)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_settings(
    user_id TEXT PRIMARY KEY,
    language TEXT DEFAULT 'auto'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bot_settings(
    key TEXT PRIMARY KEY,
    value TEXT DEFAULT ''
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS server_config(
    guild_id TEXT PRIMARY KEY,
    raid_channel_id TEXT
)
""")
add_column(cursor, "server_config", "guild_id", "TEXT")
add_column(cursor, "server_config", "raid_channel_id", "TEXT")

cursor.execute("""
CREATE TABLE IF NOT EXISTS raid_registrations(
    user_id TEXT,
    raid_type TEXT,
    guild_id TEXT,
    PRIMARY KEY (user_id, guild_id)
)
""")
add_column(cursor, "raid_registrations", "raid_type", "TEXT DEFAULT 'diaria'")
add_column(cursor, "raid_registrations", "guild_id", "TEXT DEFAULT 'global'")

cursor.execute("""
CREATE TABLE IF NOT EXISTS city_stats(
    id INTEGER PRIMARY KEY,
    hp INTEGER DEFAULT 100000,
    max_hp INTEGER DEFAULT 100000,
    moral INTEGER DEFAULT 100,
    suprimentos INTEGER DEFAULT 0,
    max_suprimentos INTEGER DEFAULT 5000,
    prosperidade INTEGER DEFAULT 0
)
""")
cursor.execute("INSERT OR IGNORE INTO city_stats (id) VALUES (1)")

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
add_column(cursor, "cidades", "guild_id", "TEXT")
add_column(cursor, "cidades", "nome", "TEXT DEFAULT 'Capital de Lugnica'")
add_column(cursor, "cidades", "hp", "INTEGER DEFAULT 100000")
add_column(cursor, "cidades", "max_hp", "INTEGER DEFAULT 100000")
add_column(cursor, "cidades", "moral", "INTEGER DEFAULT 100")
add_column(cursor, "cidades", "suprimentos", "INTEGER DEFAULT 0")
add_column(cursor, "cidades", "max_suprimentos", "INTEGER DEFAULT 5000")
add_column(cursor, "cidades", "prosperidade", "INTEGER DEFAULT 0")

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

for column, ddl in {
    "description": "TEXT DEFAULT ''",
    "icon_url": "TEXT DEFAULT ''",
    "join_mode": "TEXT DEFAULT 'convite'",
}.items():
    add_column(cursor, "player_guilds", column, ddl)

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
CREATE TABLE IF NOT EXISTS player_achievements(
    user_id TEXT NOT NULL,
    achievement_id TEXT NOT NULL,
    claimed INTEGER DEFAULT 0,
    claimed_at INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, achievement_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS event_progress(
    user_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    points INTEGER DEFAULT 0,
    kills INTEGER DEFAULT 0,
    boss_kills INTEGER DEFAULT 0,
    dungeon_clears INTEGER DEFAULT 0,
    last_action INTEGER DEFAULT 0,
    reward_claims INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, event_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS administrative_logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    value TEXT,
    admin_id TEXT,
    timestamp INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',
    resolution TEXT DEFAULT '',
    resolved_by TEXT,
    resolved_at INTEGER DEFAULT 0
)
""")
add_column(cursor, "administrative_logs", "status", "TEXT DEFAULT 'open'")
add_column(cursor, "administrative_logs", "resolution", "TEXT DEFAULT ''")
add_column(cursor, "administrative_logs", "resolved_by", "TEXT")
add_column(cursor, "administrative_logs", "resolved_at", "INTEGER DEFAULT 0")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_stats(
    user_id TEXT NOT NULL,
    stat TEXT NOT NULL,
    value INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, stat)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_perks(
    user_id TEXT NOT NULL,
    perk_id TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    purchased_at INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, perk_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_cosmetics(
    user_id TEXT NOT NULL,
    cosmetic_id TEXT NOT NULL,
    type TEXT NOT NULL,
    active INTEGER DEFAULT 0,
    purchased_at INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, cosmetic_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_expeditions(
    user_id TEXT PRIMARY KEY,
    hours INTEGER NOT NULL,
    started_at INTEGER NOT NULL,
    ends_at INTEGER NOT NULL,
    party_power INTEGER DEFAULT 0,
    party_ids TEXT DEFAULT '[]'
)
""")
add_column(cursor, "player_expeditions", "party_ids", "TEXT DEFAULT '[]'")

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_labyrinth(
    user_id TEXT PRIMARY KEY,
    depth INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 100,
    loot_gold INTEGER DEFAULT 0,
    loot_gems INTEGER DEFAULT 0,
    started_at INTEGER DEFAULT 0,
    last_action INTEGER DEFAULT 0
)
""")
add_column(cursor, "player_labyrinth", "last_action", "INTEGER DEFAULT 0")

cursor.execute("""
CREATE TABLE IF NOT EXISTS champion_tower(
    user_id TEXT PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    weekly_score INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    week_id TEXT DEFAULT '',
    last_fight INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS champion_defense_teams(
    user_id TEXT PRIMARY KEY,
    display_name TEXT,
    hero_ids TEXT DEFAULT '[]',
    hero_names TEXT DEFAULT '[]',
    power INTEGER DEFAULT 0,
    is_bot INTEGER DEFAULT 0,
    updated_at INTEGER DEFAULT 0
)
""")
for column, ddl in {
    "display_name": "TEXT",
    "hero_ids": "TEXT DEFAULT '[]'",
    "hero_names": "TEXT DEFAULT '[]'",
    "power": "INTEGER DEFAULT 0",
    "is_bot": "INTEGER DEFAULT 0",
    "updated_at": "INTEGER DEFAULT 0",
}.items():
    add_column(cursor, "champion_defense_teams", column, ddl)

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

conn.commit()
conn.close()

print("Banco pronto para o Echo Siege.")
