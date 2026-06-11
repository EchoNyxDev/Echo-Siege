import sqlite3


def ensure_perk_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_perks(
            user_id TEXT NOT NULL,
            perk_id TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            purchased_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, perk_id)
        )
    """)


def get_perk_level(cursor, user_id, perk_id):
    try:
        ensure_perk_table(cursor)
        cursor.execute("SELECT level FROM player_perks WHERE user_id = ? AND perk_id = ?", (str(user_id), perk_id))
        row = cursor.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0


def apply_reward_bonuses(cursor, user_id, gold=0, xp=0):
    gold_level = get_perk_level(cursor, user_id, "gold_bonus")
    xp_level = get_perk_level(cursor, user_id, "xp_bonus")
    if gold and gold_level:
        gold = int(gold * (1 + 0.05 * gold_level))
    if xp and xp_level:
        xp = int(xp * (1 + 0.05 * xp_level))
    return gold, xp


def has_arena_auto(cursor, user_id):
    return get_perk_level(cursor, user_id, "arena_auto") > 0


def ensure_battle_bonus_columns(cursor):
    cursor.execute("PRAGMA table_info(players)")
    cols = {row[1] for row in cursor.fetchall()}
    if "battle_hp_bonus" not in cols:
        cursor.execute("ALTER TABLE players ADD COLUMN battle_hp_bonus INTEGER DEFAULT 0")


def consume_battle_hp_bonus(cursor, user_id):
    try:
        ensure_battle_bonus_columns(cursor)
        cursor.execute("SELECT battle_hp_bonus FROM players WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        bonus = int(row[0] or 0) if row else 0
        if bonus > 0:
            cursor.execute("UPDATE players SET battle_hp_bonus = 0 WHERE user_id = ?", (str(user_id),))
        return bonus
    except sqlite3.OperationalError:
        return 0


def apply_battle_hp_bonus(cursor, user_id, party_data):
    bonus = consume_battle_hp_bonus(cursor, user_id)
    if bonus <= 0 or not party_data:
        return party_data
    for hero in party_data:
        if "stats" in hero:
            hero["stats"]["hp"] = hero["stats"].get("hp", 0) + bonus
        if "hp" in hero:
            hero["hp"] = hero.get("hp", 0) + bonus
    return party_data
