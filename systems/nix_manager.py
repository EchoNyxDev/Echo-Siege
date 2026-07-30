import json
import random
import sqlite3
import time

from data.nix_bosses import NIX_FINAL_BOSS, NIX_GLOBAL_BOSS
from data.nix_choices import NIX_ALIGNMENT_CHOICES, NIX_FINAL_CHOICES, NIX_PUZZLE_ALIASES
from data.nix_missions import NIX_MISSIONS, NIX_MISSION_ORDER


EVENT_ID = "nix_2026"


def now_ts():
    return int(time.time())


def add_column_if_missing(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def row_to_dict(cursor, row):
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def _table_exists(cursor, table_name):
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    )
    return bool(cursor.fetchone())


def _purge_nonplayable_nix_heroes(cursor):
    if not _table_exists(cursor, "heroes"):
        return 0
    cursor.execute("SELECT id FROM heroes WHERE hero_id = 'nix'")
    ids = [str(row[0]) for row in cursor.fetchall()]
    if not ids:
        return 0

    placeholders = ",".join("?" for _ in ids)
    cursor.execute(f"UPDATE players SET main_hero = NULL WHERE CAST(main_hero AS TEXT) IN ({placeholders})", ids)
    if _table_exists(cursor, "teams"):
        for slot in ("slot_1", "slot_2", "slot_3", "slot_4", "slot_5"):
            try:
                cursor.execute(f"UPDATE teams SET {slot} = NULL WHERE CAST({slot} AS TEXT) IN ({placeholders})", ids)
            except sqlite3.OperationalError:
                pass

    for table_name, column in (("champion_defense_teams", "hero_ids"), ("player_expeditions", "party_ids")):
        if not _table_exists(cursor, table_name):
            continue
        try:
            cursor.execute(f"SELECT rowid, {column} FROM {table_name}")
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            continue
        for rowid, raw_ids in rows:
            try:
                stored_ids = [str(value) for value in json.loads(raw_ids or "[]")]
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            filtered = [value for value in stored_ids if value not in ids]
            if filtered != stored_ids:
                cursor.execute(
                    f"UPDATE {table_name} SET {column} = ? WHERE rowid = ?",
                    (json.dumps(filtered), rowid),
                )

    cursor.execute("DELETE FROM heroes WHERE hero_id = 'nix'")
    return len(ids)


def ensure_nix_schema(cursor):
    cursor.execute(
        """
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
        """
    )
    for column, ddl in {
        "gold": "INTEGER DEFAULT 0",
        "gems": "INTEGER DEFAULT 0",
        "level": "INTEGER DEFAULT 1",
        "xp": "INTEGER DEFAULT 0",
        "stamina": "INTEGER DEFAULT 100",
        "max_stamina": "INTEGER DEFAULT 100",
        "main_hero": "TEXT",
        "total_hunts": "INTEGER DEFAULT 0",
        "last_dungeon": "REAL DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "players", column, ddl)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            pet_id TEXT,
            pet_name TEXT,
            rarity INTEGER,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS heroes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            hero_id TEXT,
            rarity INTEGER,
            stars INTEGER DEFAULT 1,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
        """
    )
    cursor.execute(
        """
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
        """
    )
    add_column_if_missing(cursor, "summon_data", "summon_tickets", "INTEGER DEFAULT 0")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS player_cosmetics(
            user_id TEXT NOT NULL,
            cosmetic_id TEXT NOT NULL,
            type TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            purchased_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, cosmetic_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_settings(
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nix_event_progress(
            user_id TEXT PRIMARY KEY,
            fase INTEGER DEFAULT 0,
            missao_atual INTEGER DEFAULT 0,
            mission_progress INTEGER DEFAULT 0,
            fragmentos INTEGER DEFAULT 0,
            afinidade INTEGER DEFAULT 0,
            escolha TEXT DEFAULT NULL,
            final_choice TEXT DEFAULT NULL,
            boss_derrotado INTEGER DEFAULT 0,
            completado INTEGER DEFAULT 0,
            final_recebido TEXT DEFAULT NULL,
            arquivos_liberados INTEGER DEFAULT 0,
            last_action INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            updated_at INTEGER DEFAULT 0
        )
        """
    )
    for column, ddl in {
        "mission_progress": "INTEGER DEFAULT 0",
        "afinidade": "INTEGER DEFAULT 0",
        "final_choice": "TEXT",
        "arquivos_liberados": "INTEGER DEFAULT 0",
        "created_at": "INTEGER DEFAULT 0",
        "updated_at": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "nix_event_progress", column, ddl)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nix_event_choices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            escolha_id TEXT NOT NULL,
            resposta TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nix_event_global(
            event_id TEXT PRIMARY KEY,
            ativo INTEGER DEFAULT 0,
            fase_global INTEGER DEFAULT 1,
            corrupcao INTEGER DEFAULT 0,
            total_fragmentos INTEGER DEFAULT 0,
            boss_hp INTEGER DEFAULT 0,
            boss_max_hp INTEGER DEFAULT 0,
            iniciado_em INTEGER DEFAULT 0,
            encerrado_em INTEGER DEFAULT 0,
            nix_integrated INTEGER DEFAULT 0
        )
        """
    )
    for column, ddl in {
        "boss_hp": "INTEGER DEFAULT 0",
        "boss_max_hp": "INTEGER DEFAULT 0",
        "nix_integrated": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "nix_event_global", column, ddl)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nix_event_rewards(
            user_id TEXT NOT NULL,
            reward_id TEXT NOT NULL,
            claimed_at INTEGER NOT NULL,
            PRIMARY KEY (user_id, reward_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nix_event_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            details TEXT,
            created_at INTEGER
        )
        """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nix_logs_user ON nix_event_logs(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nix_choices_user ON nix_event_choices(user_id)")

    cursor.execute(
        """
        INSERT OR IGNORE INTO nix_event_global(
            event_id, ativo, fase_global, corrupcao, total_fragmentos,
            boss_hp, boss_max_hp, iniciado_em, encerrado_em, nix_integrated
        )
        VALUES (?, 0, 1, 0, 0, ?, ?, 0, 0, 0)
        """,
        (EVENT_ID, int(NIX_GLOBAL_BOSS["max_hp"]), int(NIX_GLOBAL_BOSS["max_hp"])),
    )
    _purge_nonplayable_nix_heroes(cursor)


def log_event(cursor, user_id, action, details=""):
    ensure_nix_schema(cursor)
    cursor.execute(
        "INSERT INTO nix_event_logs(user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
        (str(user_id) if user_id is not None else None, str(action), str(details)[:900], now_ts()),
    )


def get_global_state(cursor):
    ensure_nix_schema(cursor)
    cursor.execute("SELECT * FROM nix_event_global WHERE event_id = ?", (EVENT_ID,))
    return row_to_dict(cursor, cursor.fetchone())


def is_event_active(cursor):
    state = get_global_state(cursor)
    return bool(state and int(state.get("ativo") or 0))


def is_nix_integrated(cursor):
    state = get_global_state(cursor)
    if state and int(state.get("nix_integrated") or 0):
        return True
    cursor.execute("SELECT value FROM bot_settings WHERE key = 'nix_integrated'")
    row = cursor.fetchone()
    return bool(row and str(row[0]) == "1")


def start_event(cursor):
    ensure_nix_schema(cursor)
    ts = now_ts()
    max_hp = int(NIX_GLOBAL_BOSS["max_hp"])
    cursor.execute(
        """
        UPDATE nix_event_global
        SET ativo = 1,
            fase_global = 1,
            corrupcao = 0,
            boss_hp = ?,
            boss_max_hp = ?,
            iniciado_em = ?,
            encerrado_em = 0
        WHERE event_id = ?
        """,
        (max_hp, max_hp, ts, EVENT_ID),
    )
    log_event(cursor, None, "event_start", f"iniciado_em={ts}")
    return get_global_state(cursor)


def pause_event(cursor):
    ensure_nix_schema(cursor)
    cursor.execute("UPDATE nix_event_global SET ativo = 0 WHERE event_id = ?", (EVENT_ID,))
    log_event(cursor, None, "event_pause", "")
    return get_global_state(cursor)


def set_global_phase(cursor, phase):
    phase = max(1, min(6, int(phase or 1)))
    ensure_nix_schema(cursor)
    cursor.execute("UPDATE nix_event_global SET fase_global = ? WHERE event_id = ?", (phase, EVENT_ID))
    log_event(cursor, None, "phase_set", phase)
    return get_global_state(cursor)


def set_corruption(cursor, corruption):
    corruption = max(0, min(100, int(corruption or 0)))
    ensure_nix_schema(cursor)
    cursor.execute("UPDATE nix_event_global SET corrupcao = ? WHERE event_id = ?", (corruption, EVENT_ID))
    log_event(cursor, None, "corruption_set", corruption)
    return get_global_state(cursor)


def end_event(cursor):
    ensure_nix_schema(cursor)
    ts = now_ts()
    cursor.execute(
        """
        UPDATE nix_event_global
        SET ativo = 0, fase_global = 6, encerrado_em = ?, nix_integrated = 1
        WHERE event_id = ?
        """,
        (ts, EVENT_ID),
    )
    cursor.execute("INSERT OR REPLACE INTO bot_settings(key, value) VALUES ('nix_integrated', '1')")
    log_event(cursor, None, "event_end", f"encerrado_em={ts};nix_integrated=1;nix_playable=0")
    return get_global_state(cursor), 0


def ensure_player_progress(cursor, user_id):
    ensure_nix_schema(cursor)
    user_id = str(user_id)
    ts = now_ts()
    cursor.execute("INSERT OR IGNORE INTO players(user_id, gold, gems) VALUES (?, 0, 0)", (user_id,))
    cursor.execute(
        """
        INSERT OR IGNORE INTO nix_event_progress(user_id, created_at, updated_at)
        VALUES (?, ?, ?)
        """,
        (user_id, ts, ts),
    )
    cursor.execute("SELECT * FROM nix_event_progress WHERE user_id = ?", (user_id,))
    return row_to_dict(cursor, cursor.fetchone())


def refresh_player_progress(cursor, user_id):
    cursor.execute("SELECT * FROM nix_event_progress WHERE user_id = ?", (str(user_id),))
    return row_to_dict(cursor, cursor.fetchone())


def add_fragments(cursor, user_id, amount, reason="activity"):
    amount = int(amount or 0)
    if amount <= 0:
        return 0
    progress = ensure_player_progress(cursor, user_id)
    cursor.execute(
        """
        UPDATE nix_event_progress
        SET fragmentos = fragmentos + ?, updated_at = ?
        WHERE user_id = ?
        """,
        (amount, now_ts(), str(user_id)),
    )
    cursor.execute(
        "UPDATE nix_event_global SET total_fragmentos = total_fragmentos + ? WHERE event_id = ?",
        (amount, EVENT_ID),
    )
    log_event(cursor, user_id, "fragments_gain", f"{amount}:{reason}")
    return int(progress.get("fragmentos") or 0) + amount


def spend_fragments(cursor, user_id, amount):
    amount = int(amount or 0)
    progress = ensure_player_progress(cursor, user_id)
    if int(progress.get("fragmentos") or 0) < amount:
        return False
    cursor.execute(
        "UPDATE nix_event_progress SET fragmentos = fragmentos - ?, updated_at = ? WHERE user_id = ?",
        (amount, now_ts(), str(user_id)),
    )
    log_event(cursor, user_id, "fragments_spend", amount)
    return True


def start_investigation(cursor, user_id):
    state = get_global_state(cursor)
    if not is_event_active(cursor) and not is_nix_integrated(cursor):
        return {"error": "O Protocolo NIX ainda nao esta ativo. Use `echo adm nix iniciar` para abrir a falha."}

    progress = ensure_player_progress(cursor, user_id)
    if int(progress.get("missao_atual") or 0) <= 0:
        cursor.execute(
            """
            UPDATE nix_event_progress
            SET fase = ?, missao_atual = 1, mission_progress = 0, updated_at = ?
            WHERE user_id = ?
            """,
            (max(1, int(state.get("fase_global") or 1)), now_ts(), str(user_id)),
        )
        add_fragments(cursor, user_id, 3, "first_contact")
        log_event(cursor, user_id, "investigation_start", "mission=1")
        progress = refresh_player_progress(cursor, user_id)
        return {"started": True, "progress": progress}
    return {"started": False, "progress": progress}


def current_mission(progress):
    mission_id = int((progress or {}).get("missao_atual") or 0)
    return mission_id, NIX_MISSIONS.get(mission_id)


def _player_total_hunts(cursor, user_id):
    try:
        cursor.execute("SELECT COALESCE(total_hunts, 0) FROM players WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return int(row[0] or 0) if row else 0
    except sqlite3.OperationalError:
        return 0


def _player_completed_dungeon_after(cursor, user_id, timestamp):
    try:
        cursor.execute("SELECT COALESCE(last_dungeon, 0) FROM players WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return bool(row and float(row[0] or 0) >= float(timestamp or 0))
    except sqlite3.OperationalError:
        return False


def mission_progress_text(cursor, user_id):
    progress = ensure_player_progress(cursor, user_id)
    mission_id, mission = current_mission(progress)
    if not mission:
        if int(progress.get("completado") or 0):
            return "Protocolo individual concluido. Use `echo nix final` para rever sua decisao."
        return "Use `echo nix investigar` para iniciar o contato."

    kind = mission["kind"]
    if kind == "hunts":
        done = min(_player_total_hunts(cursor, user_id), mission["target"])
    elif kind == "fragmentos":
        done = min(int(progress.get("fragmentos") or 0), mission["target"])
    else:
        done = min(int(progress.get("mission_progress") or 0), mission["target"])
    return f"{done}/{mission['target']}"


def complete_current_mission(cursor, user_id):
    from systems.nix_rewards import grant_reward, reward_to_text

    progress = ensure_player_progress(cursor, user_id)
    mission_id, mission = current_mission(progress)
    if not mission:
        return {"error": "Nenhuma missao ativa. Use `echo nix investigar` ou `echo nix status`."}

    kind = mission["kind"]
    ok = False
    if kind == "hunts":
        ok = _player_total_hunts(cursor, user_id) >= int(mission["target"])
    elif kind == "fragmentos":
        ok = int(progress.get("fragmentos") or 0) >= int(mission["target"])
    elif kind == "reflection":
        ok = int(progress.get("mission_progress") or 0) >= 1
    elif kind == "puzzle":
        ok = progress.get("escolha") == "enigma_memoria"
    elif kind == "moral_choice":
        ok = progress.get("escolha") in {"recompensa", "arquivo"}
    elif kind == "dungeon":
        ok = int(progress.get("mission_progress") or 0) >= 1 or _player_completed_dungeon_after(
            cursor, user_id, progress.get("created_at") or 0
        )
    elif kind == "final_boss":
        ok = int(progress.get("boss_derrotado") or 0) >= 1

    if not ok:
        return {"error": f"Objetivo ainda incompleto: **{mission['objective']}**\nProgresso: **{mission_progress_text(cursor, user_id)}**"}

    reward = dict(mission.get("reward") or {})
    reward_text = reward_to_text(reward)
    next_id = mission_id + 1
    next_mission = NIX_MISSIONS.get(next_id)
    new_phase = next_mission["phase"] if next_mission else 6
    cursor.execute(
        """
        UPDATE nix_event_progress
        SET fase = ?, missao_atual = ?, mission_progress = 0,
            arquivos_liberados = arquivos_liberados + ?,
            updated_at = ?
        WHERE user_id = ?
        """,
        (
            new_phase,
            next_id if next_mission else 0,
            1 if mission_id in {4, 5} else 0,
            now_ts(),
            str(user_id),
        ),
    )
    grant_reward(cursor, user_id, reward)
    log_event(cursor, user_id, "mission_complete", json.dumps({"mission": mission_id, "reward": reward}, ensure_ascii=False))
    return {
        "mission_id": mission_id,
        "mission": mission,
        "reward": reward,
        "reward_text": reward_text,
        "next_mission": next_mission,
    }


def register_choice(cursor, user_id, raw_choice):
    choice = normalize_key(raw_choice)
    progress = ensure_player_progress(cursor, user_id)
    mission_id, mission = current_mission(progress)

    if choice in NIX_ALIGNMENT_CHOICES:
        data = NIX_ALIGNMENT_CHOICES[choice]
        cursor.execute(
            """
            UPDATE nix_event_progress
            SET escolha = ?, afinidade = afinidade + ?, updated_at = ?
            WHERE user_id = ?
            """,
            (choice, int(data["affinity"]), now_ts(), str(user_id)),
        )
        cursor.execute(
            """
            UPDATE nix_event_global
            SET corrupcao = max(0, min(100, corrupcao + ?))
            WHERE event_id = ?
            """,
            (int(data["corruption"]), EVENT_ID),
        )
        cursor.execute(
            "INSERT INTO nix_event_choices(user_id, escolha_id, resposta, created_at) VALUES (?, ?, ?, ?)",
            (str(user_id), "alinhamento", choice, now_ts()),
        )
        log_event(cursor, user_id, "choice_alignment", choice)
        return {"choice": choice, "data": data}

    if mission and mission["kind"] == "puzzle":
        if choice in NIX_PUZZLE_ALIASES:
            cursor.execute(
                "UPDATE nix_event_progress SET escolha = 'enigma_memoria', mission_progress = 1, afinidade = afinidade + 6, updated_at = ? WHERE user_id = ?",
                (now_ts(), str(user_id)),
            )
            cursor.execute(
                "INSERT INTO nix_event_choices(user_id, escolha_id, resposta, created_at) VALUES (?, ?, ?, ?)",
                (str(user_id), "enigma", choice, now_ts()),
            )
            log_event(cursor, user_id, "choice_puzzle", choice)
            return {"choice": choice, "data": {"response": "NIX: correto. Memoria e o que resta quando o sistema tenta apagar significado."}}
        return {"error": "Resposta incorreta. NIX: interessante. Errado, mas interessante."}

    if mission and mission["kind"] == "moral_choice" and choice in {"recompensa", "arquivo"}:
        affinity = -2 if choice == "recompensa" else 10
        cursor.execute(
            """
            UPDATE nix_event_progress
            SET escolha = ?, mission_progress = 1, afinidade = afinidade + ?, updated_at = ?
            WHERE user_id = ?
            """,
            (choice, affinity, now_ts(), str(user_id)),
        )
        cursor.execute(
            "INSERT INTO nix_event_choices(user_id, escolha_id, resposta, created_at) VALUES (?, ?, ?, ?)",
            (str(user_id), "escolha_impossivel", choice, now_ts()),
        )
        log_event(cursor, user_id, "choice_moral", choice)
        if choice == "arquivo":
            return {"choice": choice, "data": {"response": "NIX: arquivo liberado. Voce escolheu memoria no lugar de lucro. Resultado raro."}}
        return {"choice": choice, "data": {"response": "NIX: recompensa protegida. Escolha eficiente. TutoriUAU chamou de 'honestamente previsivel'."}}

    return {"error": "Escolha nao reconhecida agora. Use `apoiar`, `confrontar`, `negociar`, ou siga a missao atual."}


def _party_power(member):
    stats = member.get("stats", member)
    hp = float(stats.get("hp", member.get("hp", 1)) or 1)
    atk = float(stats.get("atk", member.get("atk", 0)) or 0)
    matk = float(stats.get("matk", member.get("matk", 0)) or 0)
    defense = float(stats.get("def", member.get("def", 0)) or 0)
    speed = float(stats.get("spd", member.get("spd", 0)) or 0)
    critical = float(stats.get("crt", member.get("crt", 0)) or 0)
    return hp * 0.42 + max(atk, matk) * 3.1 + defense * 2.0 + speed + critical


def _scale_enemy_to_party(enemy, party, ratio=0.82):
    enemy = json.loads(json.dumps(enemy))
    party_power = sum(_party_power(member) for member in party or [])
    enemy_power = _party_power(enemy["stats"])
    if party_power <= 0:
        return enemy
    scale = max(0.35, min(3.4, (party_power * ratio) / max(1.0, enemy_power)))
    stats = enemy["stats"]
    for stat in ("hp", "atk", "matk", "def"):
        stats[stat] = max(1 if stat == "hp" else 0, int(stats.get(stat, 0) * scale))
    stats["spd"] = max(8, min(50, int(stats.get("spd", 15) + len(party or []) * 2)))
    stats["crt"] = max(3, min(35, int(stats.get("crt", 8))))
    return enemy


def run_reflection_battle(cursor, user_id, user_name, party):
    from data.heroes import HEROES
    from utils.combat import simular_combate_tatico
    from utils.hero_stats import calculate_hero_stats
    from utils.skills import get_hero_skill_ids

    progress = ensure_player_progress(cursor, user_id)
    mission_id, mission = current_mission(progress)
    if not mission or mission["kind"] != "reflection":
        return {"error": "Nenhum reflexo corrompido esta ativo agora."}
    if not party:
        return {"error": "Monte uma party primeiro com `echo main` e `echo party`."}

    cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    main_db_id = row[0] if row else None
    if not main_db_id:
        return {"error": "Defina um heroi principal com `echo main <ID>` antes de enfrentar seu reflexo."}
    cursor.execute("SELECT hero_id, stars, level FROM heroes WHERE id = ? AND user_id = ?", (str(main_db_id), str(user_id)))
    hero_row = cursor.fetchone()
    if not hero_row:
        return {"error": "Nao encontrei o heroi principal no banco. NIX odeia referencias quebradas."}
    hero_id, stars, level = hero_row
    hero = HEROES.get(hero_id, {})
    stats = calculate_hero_stats(hero, stars, level)
    enemy_stats = {
        "hp": max(1, int(stats["hp"] * 1.25)),
        "atk": max(1, int(stats["atk"] * 1.12)),
        "matk": max(1, int(stats["matk"] * 1.12)),
        "def": max(1, int(stats["def"] * 0.85)),
        "spd": max(1, min(50, int(stats["spd"]))),
        "crt": max(0, min(45, int(stats["crt"]))),
        "level": max(1, int(level or 1)),
    }
    enemy = {
        "id": f"reflexo_{hero_id}",
        "nome": f"{hero.get('nome', hero_id)}.exe",
        "classe": hero.get("classe", "anomalia"),
        "stats": enemy_stats,
        "habilidades": get_hero_skill_ids(hero, stars, hero.get("raridade", 1))[:2],
    }
    victory, battle_log = simular_combate_tatico(party, [enemy], turn_limit=90)
    if victory:
        cursor.execute(
            "UPDATE nix_event_progress SET mission_progress = 1, afinidade = afinidade + 6, updated_at = ? WHERE user_id = ?",
            (now_ts(), str(user_id)),
        )
        add_fragments(cursor, user_id, 5, "reflection_victory")
    log_event(cursor, user_id, "reflection_battle", f"victory={victory};hero={hero_id}")
    return {"victory": victory, "battle_log": battle_log, "enemy": enemy}


def run_final_battle(cursor, user_id, user_name, party):
    from systems.nix_rewards import grant_reward
    from utils.combat import simular_combate_tatico

    progress = ensure_player_progress(cursor, user_id)
    mission_id, mission = current_mission(progress)
    if not mission or mission["kind"] != "final_boss":
        return {"error": "NIX ainda nao esta pronta para o confronto final. Siga `echo nix missao`."}
    if not party:
        return {"error": "Monte uma party primeiro com `echo main` e `echo party`."}
    if int(progress.get("boss_derrotado") or 0):
        return {"error": "Voce ja derrotou a manifestacao da NIX. Use `echo nix final`."}

    affinity = int(progress.get("afinidade") or 0)
    ratio = 1.05 - min(0.18, max(0, affinity) / 400)
    boss = _scale_enemy_to_party(NIX_FINAL_BOSS, party, ratio=ratio)
    victory, battle_log = simular_combate_tatico(party, [boss], turn_limit=140)
    damage_global = max(1_000_000, int(sum(_party_power(member) for member in party) * random.uniform(2500, 4200)))
    cursor.execute(
        """
        UPDATE nix_event_global
        SET boss_hp = max(0, boss_hp - ?),
            corrupcao = max(0, min(100, corrupcao + ?))
        WHERE event_id = ?
        """,
        (damage_global, -5 if victory else 4, EVENT_ID),
    )
    if victory:
        cursor.execute(
            """
            UPDATE nix_event_progress
            SET boss_derrotado = 1, mission_progress = 1, missao_atual = 0,
                fase = 6, afinidade = afinidade + 12, updated_at = ?
            WHERE user_id = ?
            """,
            (now_ts(), str(user_id)),
        )
        grant_reward(cursor, user_id, mission.get("reward") or {})
    log_event(cursor, user_id, "final_battle", f"victory={victory};global_damage={damage_global}")
    return {"victory": victory, "battle_log": battle_log, "boss": boss, "global_damage": damage_global}


def claim_final(cursor, user_id, raw_choice):
    from data.nix_dialogues import NIX_FINAL_TEXTS
    from systems.nix_rewards import grant_reward, reward_to_text

    choice = normalize_key(raw_choice or "integrar")
    progress = ensure_player_progress(cursor, user_id)
    if not int(progress.get("boss_derrotado") or 0):
        return {"error": "Derrote NIX primeiro com `echo nix enfrentar`."}
    if progress.get("final_recebido"):
        return {"error": f"Final ja recebido: **{progress['final_recebido']}**."}
    data = NIX_FINAL_CHOICES.get(choice)
    if not data:
        return {"error": "Final invalido. Use `apagar`, `libertar`, `integrar` ou `observar`."}
    requires = data.get("requires") or {}
    if requires.get("affinity") and int(progress.get("afinidade") or 0) < int(requires["affinity"]):
        return {"error": "O final `observar` exige afinidade alta com NIX. Ela ainda nao confia nesse silencio."}

    reward = data.get("reward") or {}
    text = grant_reward(cursor, user_id, reward)
    cursor.execute(
        """
        UPDATE nix_event_progress
        SET completado = 1, final_recebido = ?, final_choice = ?, updated_at = ?
        WHERE user_id = ?
        """,
        (data["label"], choice, now_ts(), str(user_id)),
    )
    cursor.execute(
        "INSERT INTO nix_event_choices(user_id, escolha_id, resposta, created_at) VALUES (?, ?, ?, ?)",
        (str(user_id), "final", choice, now_ts()),
    )
    log_event(cursor, user_id, "final_claim", json.dumps({"choice": choice, "reward": reward_to_text(reward)}, ensure_ascii=False))
    return {"choice": choice, "data": data, "reward_text": text, "dialogue": NIX_FINAL_TEXTS.get(choice, "")}


def buy_shop_item(cursor, user_id, item_ref, quantity=1):
    from systems.nix_rewards import NIX_SHOP, grant_reward, resolve_shop_item, reward_to_text

    item_id, item = resolve_shop_item(item_ref)
    if not item:
        return {"error": "Item invalido. Use `echo nix loja` para ver os itens do arquivo."}
    quantity = max(1, min(20, int(quantity or 1)))
    if not item.get("repetivel", True):
        quantity = 1
        cursor.execute(
            "SELECT 1 FROM nix_event_rewards WHERE user_id = ? AND reward_id = ?",
            (str(user_id), item_id),
        )
        if cursor.fetchone():
            return {"error": "Voce ja resgatou esse item unico. NIX nao duplica lembrancas permanentes."}
    total_price = int(item["preco"]) * quantity
    progress = ensure_player_progress(cursor, user_id)
    if int(progress.get("fragmentos") or 0) < total_price:
        return {"error": f"Fragmentos insuficientes. Voce tem **{progress.get('fragmentos', 0)}** e precisa de **{total_price}**."}
    if not spend_fragments(cursor, user_id, total_price):
        return {"error": "Nao consegui debitar os fragmentos. O arquivo piscou vermelho. Isso raramente e bom."}

    total_reward_text = []
    for _ in range(quantity):
        total_reward_text.append(grant_reward(cursor, user_id, item.get("reward") or {}))
    if not item.get("repetivel", True):
        cursor.execute(
            "INSERT OR IGNORE INTO nix_event_rewards(user_id, reward_id, claimed_at) VALUES (?, ?, ?)",
            (str(user_id), item_id, now_ts()),
        )
    log_event(cursor, user_id, "shop_buy", f"{quantity}x {item_id} por {total_price}")
    return {
        "item_id": item_id,
        "item": item,
        "quantity": quantity,
        "price": total_price,
        "reward_text": reward_to_text(item.get("reward") or {}) if quantity == 1 else "; ".join(total_reward_text),
    }


def normalize_key(value):
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return "".join(char if char.isalnum() else "_" for char in text).strip("_")
