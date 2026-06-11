import random
from datetime import date, timedelta


SPECIAL_BANNER_NAMES = [
    "Ruptura de Sábado",
    "Contrato Estelar",
    "Fenda dos Escolhidos",
    "Chamado da Semana",
    "Eco Lendário",
]


def rarity_ids(heroes, rarity):
    return [
        hero_id
        for hero_id, data in heroes.items()
        if hero_id != "id-nome" and data.get("raridade", 1) == rarity
    ]


def get_common_banner(heroes, today=None):
    today = today or date.today()
    return {
        "id": "comum",
        "type": "comum",
        "name": "Banner Comum",
        "period_label": "permanente",
        "featured_5": [],
        "featured_4": [],
        "featured_5_rate": 0.0,
        "featured_4_rate": 0.0,
        "resets_at": None,
        "description": "Todos os personagens disponíveis entram no mesmo caldeirão. Sim, é estatística. Não, ela não tem pena.",
    }


def current_saturday(today=None):
    today = today or date.today()
    days_since_saturday = (today.weekday() - 5) % 7
    return today - timedelta(days=days_since_saturday)


def get_special_banner(heroes, today=None):
    today = today or date.today()
    start = current_saturday(today)
    next_reset = start + timedelta(days=7)
    seed = int(start.strftime("%Y%m%d"))
    rng = random.Random(seed)

    five_pool = rarity_ids(heroes, 5)
    four_pool = rarity_ids(heroes, 4)
    featured_5 = rng.sample(five_pool, min(3, len(five_pool))) if five_pool else []
    featured_4 = rng.sample(four_pool, min(5, len(four_pool))) if four_pool else []

    return {
        "id": f"especial_{start.strftime('%Y%m%d')}",
        "type": "especial",
        "name": SPECIAL_BANNER_NAMES[seed % len(SPECIAL_BANNER_NAMES)],
        "period_label": f"{start.strftime('%d/%m/%Y')} até {next_reset.strftime('%d/%m/%Y')}",
        "featured_5": featured_5,
        "featured_4": featured_4,
        "featured_5_rate": 0.75,
        "featured_4_rate": 0.65,
        "resets_at": next_reset,
        "description": "Banner semanal separado: as chances de 4⭐/5⭐ continuam iguais; quando a raridade vem, os destaques têm prioridade.",
    }


def get_banner(heroes, banner_type="comum", today=None):
    if str(banner_type or "").lower() in ["especial", "special", "semanal", "weekly"]:
        return get_special_banner(heroes, today)
    return get_common_banner(heroes, today)
