from datetime import date, timedelta


def easter_date(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def nth_weekday(year, month, weekday, n):
    current = date(year, month, 1)
    while current.weekday() != weekday:
        current += timedelta(days=1)
    return current + timedelta(days=7 * (n - 1))


EVENT_TEMPLATES = {
    "ano_novo": {
        "name": "Ano Novo Dimensional",
        "anchor": ("fixed", 1, 1),
        "before": 0,
        "after": 7,
        "item": "fogos_do_ano_novo",
        "monster": "Eco Festivo",
        "boss": "Dragao dos Recomecos",
        "dungeon": "Torre dos Fogos",
    },
    "pascoa": {
        "name": "Pascoa Encantada",
        "anchor": ("easter",),
        "before": 3,
        "after": 7,
        "item": "ovo_de_pascoa",
        "monster": "Coelho Arcano",
        "boss": "Guardiao dos Ovos Eternos",
        "dungeon": "Jardim de Chocolate",
    },
    "dia_maes": {
        "name": "Dia das Maes de Lugnica",
        "anchor": ("nth_weekday", 5, 6, 2),
        "before": 3,
        "after": 4,
        "item": "flor_das_maes",
        "monster": "Espinho Carinhoso",
        "boss": "Matriarca da Floresta",
        "dungeon": "Bosque do Afeto",
    },
    "dia_pais": {
        "name": "Dia dos Pais de Lugnica",
        "anchor": ("nth_weekday", 8, 6, 2),
        "before": 3,
        "after": 4,
        "item": "medalha_dos_pais",
        "monster": "Sentinela Teimoso",
        "boss": "Patriarca de Aco",
        "dungeon": "Fortaleza da Heranca",
    },
    "dia_criancas": {
        "name": "Dia das Criancas",
        "anchor": ("fixed", 10, 12),
        "before": 3,
        "after": 5,
        "item": "brinquedo_magico",
        "monster": "Boneco Travesso",
        "boss": "Rei dos Brinquedos",
        "dungeon": "Parque dos Ecos",
    },
    "natal": {
        "name": "Natal das Dimensoes",
        "anchor": ("fixed", 12, 25),
        "before": 7,
        "after": 7,
        "item": "estrela_natalina",
        "monster": "Duende Perdido",
        "boss": "Krampus do Vazio",
        "dungeon": "Oficina Congelada",
    },
}


def event_anchor(template, year):
    kind = template["anchor"][0]
    if kind == "fixed":
        _, month, day = template["anchor"]
        return date(year, month, day)
    if kind == "easter":
        return easter_date(year)
    if kind == "nth_weekday":
        _, month, weekday, n = template["anchor"]
        return nth_weekday(year, month, weekday, n)
    raise ValueError(f"Unknown event anchor: {kind}")


def event_window(event_id, year):
    template = EVENT_TEMPLATES[event_id]
    anchor = event_anchor(template, year)
    return anchor - timedelta(days=template["before"]), anchor + timedelta(days=template["after"])


def build_event(event_id, year):
    template = EVENT_TEMPLATES[event_id]
    start, end = event_window(event_id, year)
    return {
        "id": f"{event_id}_{year}",
        "base_id": event_id,
        "name": template["name"],
        "start": start,
        "end": end,
        "item": template["item"],
        "monster": template["monster"],
        "boss": template["boss"],
        "dungeon": template["dungeon"],
        "rewards": {
            "monster": {"points": 12, "gold": 180, "xp": 60, "item_qty": 1},
            "boss": {"points": 35, "gold": 650, "xp": 180, "tickets": 1, "item_qty": 3},
            "dungeon": {"points": 55, "gold": 950, "xp": 260, "gems": 10, "item_qty": 5},
            "chest": {"cost": 100, "gold": 1200, "tickets": 1, "gems": 15, "item_qty": 8},
        },
    }


def get_active_events(today=None):
    today = today or date.today()
    active = []
    for event_id in EVENT_TEMPLATES:
        for year in [today.year - 1, today.year, today.year + 1]:
            event = build_event(event_id, year)
            if event["start"] <= today <= event["end"]:
                active.append(event)
    return sorted(active, key=lambda e: e["end"])


def get_next_events(today=None, limit=3):
    today = today or date.today()
    upcoming = []
    for event_id in EVENT_TEMPLATES:
        for year in [today.year, today.year + 1]:
            event = build_event(event_id, year)
            if event["end"] >= today:
                upcoming.append(event)
    upcoming.sort(key=lambda e: e["start"])
    return upcoming[:limit]
