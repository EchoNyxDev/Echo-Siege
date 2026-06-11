def init_equipment_db(cursor):
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


def get_equipment_progress(cursor, user_id, item_name):
    init_equipment_db(cursor)
    cursor.execute(
        "SELECT level, refine, xp FROM equipment_upgrades WHERE user_id = ? AND item_name = ?",
        (str(user_id), item_name)
    )
    row = cursor.fetchone()
    if not row:
        return {"level": 0, "refine": 0, "xp": 0}
    return {"level": row[0] or 0, "refine": row[1] or 0, "xp": row[2] or 0}


def scale_equipment_stats(base_item, progress):
    level = progress.get("level", 0)
    refine = progress.get("refine", 0)
    mult = 1 + (level * 0.06) + (refine * 0.12)
    bonus = {}
    for stat in ["hp", "atk", "matk", "def", "spd", "crt"]:
        value = base_item.get(stat, 0)
        if value:
            scaled = int(value * mult)
            bonus[stat] = max(1, scaled) if value > 0 else min(-1, scaled)

    if refine >= 2 and base_item.get("tipo") == "atk":
        bonus["crt"] = bonus.get("crt", 0) + 3 + refine
    if refine >= 2 and base_item.get("tipo") == "def":
        bonus["hp"] = bonus.get("hp", 0) + 25 * refine
    if refine >= 4:
        bonus["spd"] = bonus.get("spd", 0) + 2
    return bonus


def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
    if not item_name or item_name not in equipamentos:
        return {}
    progress = get_equipment_progress(cursor, user_id, item_name)
    return scale_equipment_stats(equipamentos[item_name], progress)


def upgrade_cost(current_level):
    return 250 + (current_level * 150)


def refine_cost(current_refine):
    return 1200 + (current_refine * 900)
