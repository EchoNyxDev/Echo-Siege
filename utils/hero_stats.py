import unicodedata


NATURAL_SPD_CAP = 50
NATURAL_CRT_CAP = 50


def normalize_class(value):
    text = unicodedata.normalize("NFKD", str(value or "neutro"))
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
    """Calcula a progressão única usada por todos os modos de combate."""
    stars = max(1, int(stars or 1))
    level = max(1, int(level or 1))
    gained_levels = level - 1
    star_multiplier = 1.0 + (0.15 * (stars - 1))
    hero_class = normalize_class(hero_data.get("classe", "neutro"))

    stats = {
        "hp": int(hero_data.get("hp", 100) * star_multiplier),
        "atk": int(hero_data.get("atk", 10) * star_multiplier),
        "matk": int(hero_data.get("matk", 10) * star_multiplier),
        "def": int(hero_data.get("def", 5) * star_multiplier),
        "spd": int(max(1, hero_data.get("spd", 10)) * star_multiplier),
        "crt": int(hero_data.get("crt", 5) * star_multiplier),
    }

    per_level = {"hp": 10, "atk": 3, "matk": 3, "def": 3, "spd": 3, "crt": 3}
    class_main_stat = {
        "atacante": "atk",
        "mago": "matk",
        "tank": "def",
        "atirador": "crt",
        "assassino": "spd",
    }.get(hero_class)
    if class_main_stat:
        per_level[class_main_stat] = 5
    elif hero_class == "suporte":
        per_level["hp"] += 5
    elif hero_class == "lider":
        for stat in ("atk", "matk", "def", "spd", "crt"):
            per_level[stat] += 1
        per_level["hp"] += 1

    for stat, gain in per_level.items():
        stats[stat] += gain * gained_levels

    # O crescimento natural para chance/velocidade para em 50. Equipamentos
    # e efeitos de combate ainda podem ultrapassar esse teto.
    stats["spd"] = min(NATURAL_SPD_CAP, stats["spd"])
    stats["crt"] = min(NATURAL_CRT_CAP, stats["crt"])

    for bonus in equipment_bonuses or []:
        for stat in stats:
            stats[stat] += int(bonus.get(stat, 0) or 0)

    stats["level"] = level
    return stats
