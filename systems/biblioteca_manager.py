import datetime
import json
import random
import re
import sqlite3
import time
import unicodedata
from collections import defaultdict

from data.biblioteca_shop import BIBLIOTECA_SHOP
from systems.biblioteca_rewards import completion_reward, question_points
from systems.biblioteca_session import SESSION_MODES, normalize_mode

try:
    from utils.xp_system import dar_xp_jogador
except Exception:
    def dar_xp_jogador(cursor, user_id, xp):
        cursor.execute("UPDATE players SET xp = COALESCE(xp, 0) + ? WHERE user_id = ?", (int(xp or 0), str(user_id)))


BIBLIOTECA_CURRENCY = "Páginas Perdidas"


def now_ts():
    return int(time.time())


def today_key():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def normalize_text(value):
    text = unicodedata.normalize("NFKD", str(value or "").lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def compact_text(value):
    return normalize_text(value).replace(" ", "")


def add_column_if_missing(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_biblioteca_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players(
            user_id TEXT PRIMARY KEY,
            gold INTEGER DEFAULT 0,
            gems INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
    """)
    for column, ddl in {
        "gold": "INTEGER DEFAULT 0",
        "gems": "INTEGER DEFAULT 0",
        "level": "INTEGER DEFAULT 1",
        "xp": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "players", column, ddl)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
    """)
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
    add_column_if_missing(cursor, "summon_data", "summon_tickets", "INTEGER DEFAULT 0")
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
        CREATE TABLE IF NOT EXISTS player_stats(
            user_id TEXT NOT NULL,
            stat TEXT NOT NULL,
            value INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, stat)
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_players(
            user_id TEXT PRIMARY KEY,
            paginas INTEGER DEFAULT 0,
            total_perguntas INTEGER DEFAULT 0,
            total_acertos INTEGER DEFAULT 0,
            total_erros INTEGER DEFAULT 0,
            maior_combo INTEGER DEFAULT 0,
            combo_atual INTEGER DEFAULT 0,
            ultima_diaria TEXT DEFAULT '',
            expedicoes INTEGER DEFAULT 0,
            temporada TEXT DEFAULT 'temporada_1',
            created_at INTEGER DEFAULT 0,
            updated_at INTEGER DEFAULT 0
        )
    """)
    for column, ddl in {
        "paginas": "INTEGER DEFAULT 0",
        "total_perguntas": "INTEGER DEFAULT 0",
        "total_acertos": "INTEGER DEFAULT 0",
        "total_erros": "INTEGER DEFAULT 0",
        "maior_combo": "INTEGER DEFAULT 0",
        "combo_atual": "INTEGER DEFAULT 0",
        "ultima_diaria": "TEXT DEFAULT ''",
        "expedicoes": "INTEGER DEFAULT 0",
        "temporada": "TEXT DEFAULT 'temporada_1'",
        "created_at": "INTEGER DEFAULT 0",
        "updated_at": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "biblioteca_players", column, ddl)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            pergunta_id TEXT,
            acertos INTEGER DEFAULT 0,
            erros INTEGER DEFAULT 0,
            combo INTEGER DEFAULT 0,
            dica_usada INTEGER DEFAULT 0,
            started_at INTEGER DEFAULT 0,
            expires_at INTEGER DEFAULT 0,
            question_ids TEXT DEFAULT '[]',
            answered_ids TEXT DEFAULT '[]',
            total_questions INTEGER DEFAULT 0,
            question_started_at INTEGER DEFAULT 0,
            points_earned INTEGER DEFAULT 0,
            finished_at INTEGER DEFAULT 0
        )
    """)
    for column, ddl in {
        "status": "TEXT DEFAULT 'active'",
        "pergunta_id": "TEXT",
        "acertos": "INTEGER DEFAULT 0",
        "erros": "INTEGER DEFAULT 0",
        "combo": "INTEGER DEFAULT 0",
        "dica_usada": "INTEGER DEFAULT 0",
        "started_at": "INTEGER DEFAULT 0",
        "expires_at": "INTEGER DEFAULT 0",
        "question_ids": "TEXT DEFAULT '[]'",
        "answered_ids": "TEXT DEFAULT '[]'",
        "total_questions": "INTEGER DEFAULT 0",
        "question_started_at": "INTEGER DEFAULT 0",
        "points_earned": "INTEGER DEFAULT 0",
        "finished_at": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "biblioteca_sessions", column, ddl)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_answers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id INTEGER DEFAULT 0,
            question_id TEXT NOT NULL,
            answer TEXT,
            correct INTEGER DEFAULT 0,
            difficulty INTEGER DEFAULT 1,
            points INTEGER DEFAULT 0,
            answered_at INTEGER DEFAULT 0,
            response_time INTEGER DEFAULT 0,
            hint_used INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_seen_questions(
            user_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            times_seen INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            last_seen INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, question_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_purchases(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchased_at INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_config(
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS biblioteca_custom_questions(
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_by TEXT,
            created_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO biblioteca_config (key, value) VALUES ('active', '1')")
    cursor.execute("INSERT OR IGNORE INTO biblioteca_config (key, value) VALUES ('season', 'temporada_1')")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_biblioteca_answers_user ON biblioteca_answers(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_biblioteca_answers_question ON biblioteca_answers(question_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_biblioteca_seen_user ON biblioteca_seen_questions(user_id)")


def biblioteca_is_active(cursor):
    ensure_biblioteca_schema(cursor)
    cursor.execute("SELECT value FROM biblioteca_config WHERE key = 'active'")
    row = cursor.fetchone()
    return str(row[0] if row else "1") == "1"


def get_config(cursor, key, default=""):
    ensure_biblioteca_schema(cursor)
    cursor.execute("SELECT value FROM biblioteca_config WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else default


def set_config(cursor, key, value):
    cursor.execute(
        "INSERT OR REPLACE INTO biblioteca_config (key, value) VALUES (?, ?)",
        (str(key), str(value)),
    )


def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute(
        "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)",
        (str(user_id), str(stat)),
    )
    cursor.execute(
        "UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?",
        (int(amount or 0), str(user_id), str(stat)),
    )


def max_stat(cursor, user_id, stat, value):
    cursor.execute(
        "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)",
        (str(user_id), str(stat)),
    )
    cursor.execute(
        "UPDATE player_stats SET value = max(value, ?) WHERE user_id = ? AND stat = ?",
        (int(value or 0), str(user_id), str(stat)),
    )


def ensure_player(cursor, user_id):
    ensure_biblioteca_schema(cursor)
    user_id = str(user_id)
    cursor.execute("INSERT OR IGNORE INTO players (user_id, gold, gems) VALUES (?, 0, 0)", (user_id,))
    cursor.execute(
        """
        INSERT OR IGNORE INTO biblioteca_players (user_id, created_at, updated_at)
        VALUES (?, ?, ?)
        """,
        (user_id, now_ts(), now_ts()),
    )
    cursor.execute("SELECT * FROM biblioteca_players WHERE user_id = ?", (user_id,))
    return row_to_dict(cursor, cursor.fetchone())


def row_to_dict(cursor, row):
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def safe_json_loads(raw, default):
    try:
        value = json.loads(raw or "")
        return value if isinstance(value, type(default)) else default
    except (TypeError, ValueError):
        return default


def load_questions(cursor=None):
    from data.biblioteca_questions import QUESTOES

    questions = dict(QUESTOES)
    if cursor is None:
        return questions
    try:
        cursor.execute("SELECT id, data FROM biblioteca_custom_questions WHERE active = 1")
        for question_id, raw in cursor.fetchall():
            data = json.loads(raw)
            if isinstance(data, dict) and data.get("pergunta") and data.get("resposta"):
                questions[str(question_id)] = data
    except (sqlite3.OperationalError, ValueError, TypeError):
        pass
    return questions


def get_question(question_id, cursor=None):
    return load_questions(cursor).get(str(question_id))


def check_answer(question, answer):
    if not question:
        return False, ""
    options = list(question.get("opcoes") or [])
    raw_answer = str(answer or "").strip()
    normalized = normalize_text(raw_answer)
    compact = compact_text(raw_answer)

    if options and compact in {"a", "b", "c", "d"}:
        index = "abcd".index(compact)
        if index < len(options):
            raw_answer = str(options[index])
            normalized = normalize_text(raw_answer)
            compact = compact_text(raw_answer)

    if question.get("tipo") == "verdadeiro_falso":
        truthy = {"v", "verdadeiro", "sim", "s", "true"}
        falsy = {"f", "falso", "nao", "n", "false"}
        if compact in truthy:
            normalized = "verdadeiro"
            compact = "verdadeiro"
        elif compact in falsy:
            normalized = "falso"
            compact = "falso"

    accepted = [question.get("resposta")]
    accepted.extend(question.get("aliases") or [])
    accepted_norm = {normalize_text(value) for value in accepted if str(value or "").strip()}
    accepted_compact = {compact_text(value) for value in accepted if str(value or "").strip()}
    return normalized in accepted_norm or compact in accepted_compact, str(question.get("resposta", ""))


def _seen_map(cursor, user_id):
    cursor.execute("SELECT question_id, times_seen FROM biblioteca_seen_questions WHERE user_id = ?", (str(user_id),))
    return {row[0]: int(row[1] or 0) for row in cursor.fetchall()}


def select_questions(cursor, user_id, mode, count):
    questions = load_questions(cursor)
    seen = _seen_map(cursor, user_id)
    rng = random.Random(f"biblioteca:{user_id}:{mode}:{today_key()}:{now_ts() // 60}")
    candidates = []
    for question_id, question in questions.items():
        difficulty = int(question.get("dificuldade", 1) or 1)
        if mode == "diaria" and difficulty > 4:
            continue
        if mode == "explorar" and difficulty > 4:
            continue
        candidates.append((question_id, question, seen.get(question_id, 0)))

    if not candidates:
        candidates = [(question_id, question, seen.get(question_id, 0)) for question_id, question in questions.items()]

    buckets = defaultdict(list)
    for question_id, question, times_seen in candidates:
        buckets[str(question.get("categoria", "Geral"))].append((question_id, question, times_seen))
    for bucket in buckets.values():
        rng.shuffle(bucket)
        bucket.sort(key=lambda item: (item[2], int(item[1].get("dificuldade", 1) or 1)))

    categories = list(buckets)
    rng.shuffle(categories)
    selected = []
    while len(selected) < count and categories:
        progressed = False
        for category in list(categories):
            bucket = buckets[category]
            if bucket:
                selected.append(bucket.pop(0)[0])
                progressed = True
                if len(selected) >= count:
                    break
            else:
                categories.remove(category)
        if not progressed:
            break

    if len(selected) < count:
        fallback = [item[0] for item in sorted(candidates, key=lambda item: (item[2], rng.random())) if item[0] not in selected]
        selected.extend(fallback[: count - len(selected)])
    return selected[:count]


def active_session(cursor, user_id):
    cursor.execute(
        "SELECT * FROM biblioteca_sessions WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
        (str(user_id),),
    )
    return row_to_dict(cursor, cursor.fetchone())


def _session_question_ids(session):
    return safe_json_loads(session.get("question_ids"), [])


def _session_answered_ids(session):
    return safe_json_loads(session.get("answered_ids"), [])


def start_session(cursor, user_id, mode):
    user_id = str(user_id)
    mode = normalize_mode(mode)
    if not biblioteca_is_active(cursor):
        return {"error": "A Biblioteca Perdida está fechada agora. TutoriUAU trancou a porta e levou a chave como se isso fosse cinema."}

    player = ensure_player(cursor, user_id)
    current = active_session(cursor, user_id)
    if current:
        question = get_question(current.get("pergunta_id"), cursor)
        return {"already": True, "session": current, "question": question}

    config = SESSION_MODES[mode]
    if config.get("daily") and player.get("ultima_diaria") == today_key():
        return {"error": "Você já fez a leitura diária de hoje. A Biblioteca ama rotina, mas não duplicata."}

    question_ids = select_questions(cursor, user_id, mode, int(config["questions"]))
    if not question_ids:
        return {"error": "Nenhuma pergunta disponível. Isso é irônico demais até para o TutoriUAU."}

    started = now_ts()
    if config.get("daily"):
        cursor.execute("UPDATE biblioteca_players SET ultima_diaria = ?, updated_at = ? WHERE user_id = ?", (today_key(), started, user_id))
    if mode == "expedicao":
        cursor.execute("UPDATE biblioteca_players SET expedicoes = expedicoes + 1 WHERE user_id = ?", (user_id,))

    cursor.execute(
        """
        INSERT INTO biblioteca_sessions(
            user_id, mode, status, pergunta_id, started_at, expires_at,
            question_ids, answered_ids, total_questions, question_started_at
        )
        VALUES (?, ?, 'active', ?, ?, ?, ?, '[]', ?, ?)
        """,
        (
            user_id,
            mode,
            question_ids[0],
            started,
            started + int(config["duration"]),
            json.dumps(question_ids),
            len(question_ids),
            started,
        ),
    )
    session_id = cursor.lastrowid
    cursor.execute("SELECT * FROM biblioteca_sessions WHERE id = ?", (session_id,))
    session = row_to_dict(cursor, cursor.fetchone())
    return {"session": session, "question": get_question(question_ids[0], cursor)}


def _mark_seen(cursor, user_id, question_id, correct):
    cursor.execute(
        """
        INSERT OR IGNORE INTO biblioteca_seen_questions(user_id, question_id, times_seen, correct_count, last_seen)
        VALUES (?, ?, 0, 0, 0)
        """,
        (str(user_id), str(question_id)),
    )
    cursor.execute(
        """
        UPDATE biblioteca_seen_questions
        SET times_seen = times_seen + 1,
            correct_count = correct_count + ?,
            last_seen = ?
        WHERE user_id = ? AND question_id = ?
        """,
        (1 if correct else 0, now_ts(), str(user_id), str(question_id)),
    )


def _advance_session(cursor, session, answered_ids, finished, status="complete"):
    question_ids = _session_question_ids(session)
    next_question_id = None
    if not finished:
        for question_id in question_ids:
            if question_id not in answered_ids:
                next_question_id = question_id
                break
    if finished or not next_question_id:
        cursor.execute(
            "UPDATE biblioteca_sessions SET status = ?, answered_ids = ?, pergunta_id = NULL, dica_usada = 0, finished_at = ? WHERE id = ?",
            (status, json.dumps(answered_ids), now_ts(), int(session["id"])),
        )
        return None
    cursor.execute(
        """
        UPDATE biblioteca_sessions
        SET answered_ids = ?, pergunta_id = ?, dica_usada = 0, question_started_at = ?
        WHERE id = ?
        """,
        (json.dumps(answered_ids), next_question_id, now_ts(), int(session["id"])),
    )
    return next_question_id


def grant_reward(cursor, user_id, reward):
    user_id = str(user_id)
    ensure_player(cursor, user_id)
    paginas = int(reward.get("paginas", 0) or 0)
    if paginas:
        cursor.execute("UPDATE biblioteca_players SET paginas = paginas + ?, updated_at = ? WHERE user_id = ?", (paginas, now_ts(), user_id))
        add_stat(cursor, user_id, "biblioteca_pages", paginas)
    if reward.get("gold"):
        cursor.execute("UPDATE players SET gold = COALESCE(gold, 0) + ? WHERE user_id = ?", (int(reward["gold"]), user_id))
    if reward.get("gems"):
        cursor.execute("UPDATE players SET gems = COALESCE(gems, 0) + ? WHERE user_id = ?", (int(reward["gems"]), user_id))
    if reward.get("xp"):
        dar_xp_jogador(cursor, user_id, int(reward["xp"]))
    if reward.get("tickets"):
        cursor.execute("INSERT OR IGNORE INTO summon_data (user_id) VALUES (?)", (user_id,))
        cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (int(reward["tickets"]), user_id))
    for item_name, qty in reward.get("items", {}).items():
        add_inventory(cursor, user_id, item_name, int(qty or 1))


def answer_session(cursor, user_id, answer):
    user_id = str(user_id)
    ensure_player(cursor, user_id)
    session = active_session(cursor, user_id)
    if not session:
        return {"error": "Você não tem uma leitura ativa. Use `echo biblioteca diaria` ou `echo biblioteca explorar`."}
    if now_ts() > int(session.get("expires_at") or 0):
        _advance_session(cursor, session, _session_answered_ids(session), True, "expired")
        add_stat(cursor, user_id, "biblioteca_timeouts", 1)
        return {"expired": True, "error": "O tempo da sessão acabou. A Biblioteca fechou o livro na sua cara, com educação duvidosa."}

    question_id = session.get("pergunta_id")
    question = get_question(question_id, cursor)
    if not question:
        _advance_session(cursor, session, _session_answered_ids(session), True, "broken")
        return {"error": "Essa pergunta sumiu do arquivo. TutoriUAU anotou como assombração de banco de dados."}

    correct, expected = check_answer(question, answer)
    difficulty = int(question.get("dificuldade", 1) or 1)
    hint_used = int(session.get("dica_usada") or 0)
    current_combo = int(session.get("combo") or 0)
    new_combo = current_combo + 1 if correct else 0
    points = question_points(difficulty, bool(hint_used), new_combo) if correct else 0
    answered_ids = _session_answered_ids(session)
    if question_id not in answered_ids:
        answered_ids.append(question_id)

    response_time = max(0, now_ts() - int(session.get("question_started_at") or now_ts()))
    cursor.execute(
        """
        INSERT INTO biblioteca_answers(
            user_id, session_id, question_id, answer, correct, difficulty,
            points, answered_at, response_time, hint_used
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, int(session["id"]), question_id, str(answer or "")[:400], 1 if correct else 0, difficulty, points, now_ts(), response_time, hint_used),
    )
    _mark_seen(cursor, user_id, question_id, correct)

    acertos = int(session.get("acertos") or 0) + (1 if correct else 0)
    erros = int(session.get("erros") or 0) + (0 if correct else 1)
    cursor.execute(
        """
        UPDATE biblioteca_sessions
        SET acertos = ?, erros = ?, combo = ?, points_earned = points_earned + ?
        WHERE id = ?
        """,
        (acertos, erros, new_combo, points, int(session["id"])),
    )
    cursor.execute(
        """
        UPDATE biblioteca_players
        SET paginas = paginas + ?,
            total_perguntas = total_perguntas + 1,
            total_acertos = total_acertos + ?,
            total_erros = total_erros + ?,
            combo_atual = ?,
            maior_combo = max(maior_combo, ?),
            updated_at = ?
        WHERE user_id = ?
        """,
        (points, 1 if correct else 0, 0 if correct else 1, new_combo, new_combo, now_ts(), user_id),
    )
    add_stat(cursor, user_id, "biblioteca_answers", 1)
    if correct:
        add_stat(cursor, user_id, "biblioteca_correct", 1)
        add_stat(cursor, user_id, "biblioteca_pages", points)
        max_stat(cursor, user_id, "biblioteca_best_combo", new_combo)
        if difficulty >= 5 and response_time <= 30:
            add_stat(cursor, user_id, "biblioteca_legendary_fast", 1)
    else:
        add_stat(cursor, user_id, "biblioteca_wrong", 1)

    total_questions = int(session.get("total_questions") or len(_session_question_ids(session)) or 1)
    max_errors = int(SESSION_MODES.get(session.get("mode"), {}).get("max_errors", 99))
    finished = len(answered_ids) >= total_questions or erros >= max_errors
    next_question_id = _advance_session(cursor, {**session, "acertos": acertos, "erros": erros}, answered_ids, finished)
    final_reward = None
    if finished:
        perfect = acertos == total_questions and erros == 0
        no_hint = not bool(cursor.execute(
            "SELECT 1 FROM biblioteca_answers WHERE session_id = ? AND hint_used = 1 LIMIT 1",
            (int(session["id"]),),
        ).fetchone())
        final_reward = completion_reward(session.get("mode"), acertos, erros, total_questions, perfect, no_hint)
        grant_reward(cursor, user_id, final_reward)
        add_stat(cursor, user_id, "biblioteca_sessions_done", 1)
        if perfect and session.get("mode") == "diaria":
            add_stat(cursor, user_id, "biblioteca_daily_perfect", 1)
        if no_hint and session.get("mode") == "diaria":
            add_stat(cursor, user_id, "biblioteca_daily_no_hint", 1)

    next_question = get_question(next_question_id, cursor) if next_question_id else None
    updated_session = {
        **session,
        "acertos": acertos,
        "erros": erros,
        "combo": new_combo,
        "answered_ids": json.dumps(answered_ids),
        "pergunta_id": next_question_id,
    }
    return {
        "correct": correct,
        "expected": expected,
        "question": question,
        "session": updated_session,
        "points": points,
        "finished": finished,
        "next_question": next_question,
        "next_question_id": next_question_id,
        "final_reward": final_reward,
    }


def use_hint(cursor, user_id):
    session = active_session(cursor, user_id)
    if not session:
        return {"error": "Você não tem uma leitura ativa para pedir dica."}
    if int(session.get("dica_usada") or 0):
        return {"error": "Você já usou dica nessa pergunta. O TutoriUAU não vai soprar duas vezes, ele tem postura teatral."}
    question = get_question(session.get("pergunta_id"), cursor)
    if not question:
        return {"error": "Pergunta não encontrada."}
    hint = build_hint(question)
    cursor.execute("UPDATE biblioteca_sessions SET dica_usada = 1 WHERE id = ?", (int(session["id"]),))
    add_stat(cursor, user_id, "biblioteca_hints_used", 1)
    return {"hint": hint, "question": question, "session": session}


def build_hint(question):
    answer = str(question.get("resposta", ""))
    options = list(question.get("opcoes") or [])
    if options and answer in options and len(options) >= 4:
        wrong = [option for option in options if normalize_text(option) != normalize_text(answer)]
        random.shuffle(wrong)
        remaining = [answer] + wrong[:1]
        return "Duas opções foram engolidas pelo arquivo. Foque em: " + ", ".join(f"**{item}**" for item in sorted(remaining))
    if question.get("tipo") == "verdadeiro_falso":
        return "Pense no enunciado literal. Pegadinha de anime adora confundir obra, poder e nome bonito."
    clean = answer.strip()
    if len(clean) <= 2:
        return "Resposta curta. O perigo mora justamente aí."
    return f"A resposta começa com **{clean[0]}** e tem **{len(clean.replace(' ', ''))}** letras sem contar espaços."


def abandon_session(cursor, user_id):
    session = active_session(cursor, user_id)
    if not session:
        return False
    cursor.execute(
        "UPDATE biblioteca_sessions SET status = 'abandoned', finished_at = ? WHERE id = ?",
        (now_ts(), int(session["id"])),
    )
    add_stat(cursor, user_id, "biblioteca_abandoned", 1)
    return True


def add_inventory(cursor, user_id, item_name, qty=1):
    qty = max(1, int(qty or 1))
    cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), str(item_name)))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (str(user_id), str(item_name), qty))


def period_start(period):
    now = datetime.datetime.now()
    if period == "weekly":
        start = now - datetime.timedelta(days=now.weekday())
        return int(start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    if period == "monthly":
        return int(now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
    return 0


def count_purchases(cursor, user_id, item_id, since_ts=0):
    cursor.execute(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM biblioteca_purchases
        WHERE user_id = ? AND item_id = ? AND purchased_at >= ?
        """,
        (str(user_id), str(item_id), int(since_ts or 0)),
    )
    row = cursor.fetchone()
    return int(row[0] or 0) if row else 0


def grant_shop_item(cursor, user_id, item):
    kind = item["tipo"]
    quantity = int(item.get("quantidade", 1) or 1)
    if kind in {"title", "frame"}:
        token = item["item_id"]
        add_inventory(cursor, user_id, token, 1)
        cursor.execute(
            """
            INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (str(user_id), token, "title" if kind == "title" else "frame", now_ts()),
        )
    elif kind == "tickets":
        cursor.execute("INSERT OR IGNORE INTO summon_data (user_id) VALUES (?)", (str(user_id),))
        cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (quantity, str(user_id)))
    elif kind == "gems":
        cursor.execute("UPDATE players SET gems = COALESCE(gems, 0) + ? WHERE user_id = ?", (quantity, str(user_id)))
    elif kind == "pet":
        cursor.execute(
            "INSERT INTO pets (user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, ?, 1, 0)",
            (str(user_id), item["pet_id"], item["pet_name"], int(item.get("raridade", 4))),
        )
    else:
        add_inventory(cursor, user_id, item["item_id"], quantity)


def shop_item_by_key(raw):
    if raw is None:
        return None, None
    key = normalize_text(raw).replace(" ", "_")
    if key in BIBLIOTECA_SHOP:
        return key, BIBLIOTECA_SHOP[key]
    if str(raw).strip().isdigit():
        index = int(str(raw).strip()) - 1
        keys = list(BIBLIOTECA_SHOP.keys())
        if 0 <= index < len(keys):
            key = keys[index]
            return key, BIBLIOTECA_SHOP[key]
    return None, None


def buy_shop_item(cursor, user_id, item_ref, quantity=1):
    user_id = str(user_id)
    ensure_player(cursor, user_id)
    item_id, item = shop_item_by_key(item_ref)
    if not item:
        return {"error": "Item inválido. Use `echo biblioteca loja` para ver as prateleiras, antes que elas vejam você."}
    quantity = max(1, int(quantity or 1))
    if not item.get("repetivel", True):
        quantity = 1
    if not item.get("repetivel", True) and count_purchases(cursor, user_id, item_id, 0) > 0:
        return {"error": "Você já comprou esse item único. Colecionar duplicata de título é só burocracia com glitter."}
    if item.get("limite"):
        start = period_start(item.get("periodo"))
        used = count_purchases(cursor, user_id, item_id, start)
        if used + quantity > int(item["limite"]):
            return {"error": f"Limite atingido: **{used}/{item['limite']}** neste período."}
    total_price = int(item["preco"]) * quantity
    cursor.execute("SELECT paginas FROM biblioteca_players WHERE user_id = ?", (user_id,))
    balance = int((cursor.fetchone() or [0])[0] or 0)
    if balance < total_price:
        return {"error": f"Páginas insuficientes. Você tem **{balance:,}** e precisa de **{total_price:,}**."}
    for _ in range(quantity):
        grant_shop_item(cursor, user_id, item)
    cursor.execute("UPDATE biblioteca_players SET paginas = paginas - ?, updated_at = ? WHERE user_id = ?", (total_price, now_ts(), user_id))
    cursor.execute(
        "INSERT INTO biblioteca_purchases (user_id, item_id, price, quantity, purchased_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, item_id, int(item["preco"]), quantity, now_ts()),
    )
    add_stat(cursor, user_id, "biblioteca_shop_purchases", quantity)
    return {"item_id": item_id, "item": item, "quantity": quantity, "price": total_price}


def player_status(cursor, user_id):
    player = ensure_player(cursor, user_id)
    active = active_session(cursor, user_id)
    cursor.execute(
        """
        SELECT COUNT(*), COALESCE(SUM(correct), 0)
        FROM biblioteca_answers
        WHERE user_id = ?
        """,
        (str(user_id),),
    )
    answered, correct = cursor.fetchone()
    return {"player": player, "active": active, "answered": int(answered or 0), "correct": int(correct or 0)}


def collection_by_category(cursor, user_id):
    questions = load_questions(cursor)
    cursor.execute("SELECT question_id, correct_count FROM biblioteca_seen_questions WHERE user_id = ?", (str(user_id),))
    seen = {row[0]: int(row[1] or 0) for row in cursor.fetchall()}
    data = defaultdict(lambda: {"total": 0, "seen": 0, "correct": 0})
    for question_id, question in questions.items():
        category = str(question.get("categoria", "Geral"))
        data[category]["total"] += 1
        if question_id in seen:
            data[category]["seen"] += 1
            if seen[question_id] > 0:
                data[category]["correct"] += 1
    return dict(sorted(data.items(), key=lambda item: item[0].casefold()))


def add_custom_question(cursor, created_by, payload):
    ensure_biblioteca_schema(cursor)
    if isinstance(payload, str):
        raw = payload.strip()
        if raw.startswith("{"):
            data = json.loads(raw)
        else:
            parts = [part.strip() for part in raw.split("|")]
            if len(parts) < 5:
                raise ValueError("Use JSON ou `id | categoria | dificuldade | pergunta | resposta | opcao1;opcao2;...`.")
            question_id, category, difficulty, question_text, answer = parts[:5]
            options = [item.strip() for item in parts[5].split(";") if item.strip()] if len(parts) >= 6 else []
            data = {
                "id": question_id,
                "tipo": "multipla_escolha" if options else "escrita",
                "categoria": category,
                "dificuldade": int(difficulty),
                "pergunta": question_text,
                "resposta": answer,
                "opcoes": options,
                "explicacao": "Pergunta customizada da Biblioteca Perdida.",
                "tags": ["custom"],
                "aliases": [answer],
                "imagem": None,
            }
    else:
        data = dict(payload)
    question_id = str(data.get("id") or data.get("question_id") or "").strip()
    if not question_id:
        question_id = "custom_" + compact_text(data.get("pergunta", ""))[:50]
    if not data.get("pergunta") or not data.get("resposta"):
        raise ValueError("A pergunta precisa ter `pergunta` e `resposta`.")
    data.setdefault("tipo", "multipla_escolha" if data.get("opcoes") else "escrita")
    data.setdefault("categoria", "Custom")
    data.setdefault("dificuldade", 1)
    data.setdefault("aliases", [data["resposta"]])
    cursor.execute(
        """
        INSERT OR REPLACE INTO biblioteca_custom_questions(id, data, active, created_by, created_at)
        VALUES (?, ?, 1, ?, ?)
        """,
        (question_id, json.dumps(data, ensure_ascii=False), str(created_by), now_ts()),
    )
    return question_id
