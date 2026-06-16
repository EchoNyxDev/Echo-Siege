import json
import os
import random
import sqlite3
import time
from collections import defaultdict
from datetime import date, timedelta


BANNER_DB_PATH = os.environ.get("ECHO_BANNER_DB", "players.db")
MANUAL_BANNER_DURATION = 7 * 24 * 60 * 60

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
        if hero_id != "id-nome"
        and data.get("raridade", 1) == rarity
        and not data.get("divino")
        and not data.get("secreto")
    ]


def _connect_banner_db(db_path=None):
    conn = sqlite3.connect(db_path or BANNER_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS special_banner_config(
            singleton INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            featured_5 TEXT NOT NULL,
            featured_4 TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            created_by TEXT
        )
        """
    )
    conn.commit()
    return conn


def _timestamp(value=None):
    if value is None:
        return int(time.time())
    if hasattr(value, "timestamp"):
        return int(value.timestamp())
    return int(value)


def _validate_featured(heroes, hero_ids, rarity, required):
    hero_ids = list(dict.fromkeys(str(hero_id) for hero_id in hero_ids))
    if len(hero_ids) != required:
        raise ValueError(f"O banner exige exatamente {required} heróis {rarity}⭐.")

    invalid = []
    for hero_id in hero_ids:
        hero = heroes.get(hero_id)
        if (
            not hero
            or hero_id == "id-nome"
            or int(hero.get("raridade", 0) or 0) != rarity
            or hero.get("divino")
            or hero.get("secreto")
        ):
            invalid.append(hero_id)
    if invalid:
        raise ValueError(
            f"Heróis inválidos para os destaques {rarity}⭐: {', '.join(invalid)}"
        )
    return hero_ids


def save_manual_banner(
    heroes,
    featured_5,
    featured_4,
    created_by=None,
    name="Seleção dos Deuses",
    now=None,
    db_path=None,
):
    featured_5 = _validate_featured(heroes, featured_5, 5, 3)
    featured_4 = _validate_featured(heroes, featured_4, 4, 5)
    created_at = _timestamp(now)
    expires_at = created_at + MANUAL_BANNER_DURATION

    conn = _connect_banner_db(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO special_banner_config(
                singleton, name, featured_5, featured_4,
                created_at, expires_at, created_by
            )
            VALUES (1, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(name or "Seleção dos Deuses").strip()[:100],
                json.dumps(featured_5),
                json.dumps(featured_4),
                created_at,
                expires_at,
                str(created_by) if created_by is not None else None,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return get_active_manual_banner(
        heroes,
        now=created_at,
        db_path=db_path,
    )


def get_active_manual_banner(heroes, now=None, db_path=None):
    now_ts = _timestamp(now)
    try:
        conn = _connect_banner_db(db_path)
        try:
            row = conn.execute(
                """
                SELECT name, featured_5, featured_4,
                       created_at, expires_at, created_by
                FROM special_banner_config
                WHERE singleton = 1
                """
            ).fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return None

    if not row or int(row[4] or 0) <= now_ts:
        return None

    try:
        featured_5 = _validate_featured(heroes, json.loads(row[1]), 5, 3)
        featured_4 = _validate_featured(heroes, json.loads(row[2]), 4, 5)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

    created_at = int(row[3])
    expires_at = int(row[4])
    return {
        "id": f"especial_manual_{created_at}",
        "type": "especial",
        "source": "manual",
        "name": row[0],
        "period_label": f"<t:{created_at}:f> até <t:{expires_at}:f>",
        "featured_5": featured_5,
        "featured_4": featured_4,
        "featured_5_rate": 0.75,
        "featured_4_rate": 0.65,
        "created_at": created_at,
        "expires_at": expires_at,
        "created_by": row[5],
        "resets_at": expires_at,
        "description": (
            "Banner especial criado pela administração. As taxas de 4⭐ e 5⭐ "
            "não mudam; o destaque só influencia qual herói aparece depois "
            "que a raridade já foi sorteada."
        ),
    }


def get_common_banner(heroes, today=None):
    today = today or date.today()
    return {
        "id": "comum",
        "type": "comum",
        "source": "permanent",
        "name": "Banner Comum",
        "period_label": "permanente",
        "featured_5": [],
        "featured_4": [],
        "featured_5_rate": 0.0,
        "featured_4_rate": 0.0,
        "resets_at": None,
        "description": (
            "Todos os personagens disponíveis entram no mesmo caldeirão. "
            "Sim, é estatística. Não, ela não tem pena."
        ),
    }


def current_saturday(today=None):
    today = today or date.today()
    days_since_saturday = (today.weekday() - 5) % 7
    return today - timedelta(days=days_since_saturday)


def _diverse_sample(heroes, rarity, amount, rng):
    by_class = defaultdict(list)
    for hero_id in rarity_ids(heroes, rarity):
        hero_class = str(heroes[hero_id].get("classe") or "sem_classe")
        by_class[hero_class].append(hero_id)

    for hero_ids in by_class.values():
        rng.shuffle(hero_ids)

    class_order = list(by_class)
    rng.shuffle(class_order)
    selected = []
    while len(selected) < amount and class_order:
        next_round = []
        for hero_class in class_order:
            pool = by_class[hero_class]
            if pool and len(selected) < amount:
                selected.append(pool.pop())
            if pool:
                next_round.append(hero_class)
        class_order = next_round
        rng.shuffle(class_order)
    return selected


def get_automatic_special_banner(heroes, today=None):
    today = today or date.today()
    start = current_saturday(today)
    next_reset = start + timedelta(days=7)
    seed = int(start.strftime("%Y%m%d"))
    rng = random.Random(seed)

    return {
        "id": f"especial_{start.strftime('%Y%m%d')}",
        "type": "especial",
        "source": "automatic",
        "name": SPECIAL_BANNER_NAMES[seed % len(SPECIAL_BANNER_NAMES)],
        "period_label": f"{start.strftime('%d/%m/%Y')} até {next_reset.strftime('%d/%m/%Y')}",
        "featured_5": _diverse_sample(heroes, 5, 3, rng),
        "featured_4": _diverse_sample(heroes, 4, 5, rng),
        "featured_5_rate": 0.75,
        "featured_4_rate": 0.65,
        "resets_at": next_reset,
        "description": (
            "Banner semanal automático com classes diversificadas. As chances "
            "de 4⭐ e 5⭐ continuam iguais; quando a raridade vem, os destaques "
            "têm prioridade."
        ),
    }


def get_special_banner(heroes, today=None, now=None, db_path=None):
    manual = get_active_manual_banner(heroes, now=now, db_path=db_path)
    return manual or get_automatic_special_banner(heroes, today=today)


def get_banner(heroes, banner_type="comum", today=None, now=None, db_path=None):
    if str(banner_type or "").lower() in ["especial", "special", "semanal", "weekly"]:
        return get_special_banner(
            heroes,
            today=today,
            now=now,
            db_path=db_path,
        )
    return get_common_banner(heroes, today)
