def progression_multiplier(progress, reference=50, floor=0.28):
    """Curva econômica baixa no início e acelerada conforme o progresso."""
    progress = max(1.0, float(progress or 1))
    reference = max(1.0, float(reference or 50))
    ratio = progress / reference
    if ratio <= 1:
        return floor + (1.0 - floor) * (ratio ** 1.6)
    return 1.0 + 0.45 * ((ratio - 1.0) ** 1.2)


def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50):
    multiplier = progression_multiplier(progress, reference)

    def scale(value):
        value = int(value or 0)
        if value <= 0:
            return value
        return max(1, int(round(value * multiplier)))

    return scale(gold), scale(xp)


def arena_floor_rewards(floor):
    floor = max(1, int(floor or 1))
    gold = 6 + int(2.4 * (floor ** 1.32))
    xp = 4 + int(1.35 * (floor ** 1.27))
    return gold, xp


def average_party_level(party):
    levels = [max(1, int(member.get("level", 1) or 1)) for member in party or []]
    return sum(levels) / len(levels) if levels else 1


def average_hero_level(cursor, user_id, hero_ids=None):
    params = [str(user_id)]
    query = "SELECT AVG(level) FROM heroes WHERE user_id = ?"
    clean_ids = [str(hero_id) for hero_id in (hero_ids or []) if str(hero_id).isdigit()]
    if clean_ids:
        placeholders = ",".join("?" for _ in clean_ids)
        query += f" AND id IN ({placeholders})"
        params.extend(clean_ids)
    cursor.execute(query, params)
    row = cursor.fetchone()
    return max(1.0, float((row or [1])[0] or 1))
