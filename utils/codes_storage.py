import os
import sqlite3


CODES_DB_PATH = "players.db"
LEGACY_CODES_DB_PATH = "codes.db"


def _table_exists(cursor, table):
    cursor.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    )
    return cursor.fetchone() is not None


def _table_columns(cursor, table):
    if not _table_exists(cursor, table):
        return set()
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _create_codes_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            recompensa TEXT NOT NULL,
            created_at INTEGER DEFAULT 0,
            expires_at INTEGER DEFAULT 0
        )
    """)


def _backup_name(cursor, base):
    candidate = base
    suffix = 1
    while _table_exists(cursor, candidate):
        suffix += 1
        candidate = f"{base}_{suffix}"
    return candidate


def _migrate_codigo_table(cursor, old_columns):
    backup = _backup_name(cursor, "codes_legacy_codigo")
    cursor.execute(f"ALTER TABLE codes RENAME TO {backup}")
    _create_codes_table(cursor)

    if "codigo" not in old_columns or "recompensa" not in old_columns:
        return

    created_expr = "COALESCE(created_at, 0)" if "created_at" in old_columns else "0"
    expires_expr = "COALESCE(expires_at, 0)" if "expires_at" in old_columns else "0"
    where_parts = ["codigo IS NOT NULL", "TRIM(codigo) != ''", "recompensa IS NOT NULL"]
    if "ativo" in old_columns:
        where_parts.append("COALESCE(ativo, 1) != 0")
    where_sql = "WHERE " + " AND ".join(where_parts)
    cursor.execute(
        f"""
        INSERT OR IGNORE INTO codes (code, recompensa, created_at, expires_at)
        SELECT UPPER(TRIM(codigo)), recompensa, {created_expr}, {expires_expr}
        FROM {backup}
        {where_sql}
        """
    )


def _migrate_legacy_redemptions(cursor):
    if not _table_exists(cursor, "code_resgates"):
        return

    columns = _table_columns(cursor, "code_resgates")
    if not {"user_id", "codigo"}.issubset(columns):
        return

    cursor.execute(
        """
        INSERT OR IGNORE INTO code_redemptions (code, user_id, redeemed_at)
        SELECT UPPER(TRIM(codigo)), user_id, CURRENT_TIMESTAMP
        FROM code_resgates
        WHERE codigo IS NOT NULL AND user_id IS NOT NULL
        """
    )


def ensure_codes_schema(cursor):
    code_columns = _table_columns(cursor, "codes")
    if code_columns and "code" not in code_columns:
        _migrate_codigo_table(cursor, code_columns)

    _create_codes_table(cursor)
    code_columns = _table_columns(cursor, "codes")
    if "created_at" not in code_columns:
        cursor.execute("ALTER TABLE codes ADD COLUMN created_at INTEGER DEFAULT 0")
    if "expires_at" not in code_columns:
        cursor.execute("ALTER TABLE codes ADD COLUMN expires_at INTEGER DEFAULT 0")
    cursor.execute("UPDATE codes SET expires_at = 0 WHERE expires_at IS NULL")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_redemptions (
            code TEXT NOT NULL,
            user_id TEXT NOT NULL,
            redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (code, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_storage_meta (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)
    _migrate_legacy_redemptions(cursor)


def migrate_legacy_codes(cursor):
    cursor.execute("SELECT value FROM code_storage_meta WHERE key = 'legacy_codes_import_v2'")
    row = cursor.fetchone()
    if row and row[0] == "done":
        return

    if not os.path.exists(LEGACY_CODES_DB_PATH):
        cursor.execute(
            "INSERT OR REPLACE INTO code_storage_meta (key, value) VALUES ('legacy_codes_migrated', 'missing')"
        )
        cursor.execute(
            "INSERT OR REPLACE INTO code_storage_meta (key, value) VALUES ('legacy_codes_import_v2', 'missing')"
        )
        return

    legacy = sqlite3.connect(LEGACY_CODES_DB_PATH)
    legacy_cursor = legacy.cursor()
    try:
        legacy_cursor.execute(
            "SELECT code, recompensa, COALESCE(created_at, 0), COALESCE(expires_at, 0) FROM codes"
        )
        for code, recompensa, created_at, expires_at in legacy_cursor.fetchall():
            cursor.execute(
                """
                INSERT OR IGNORE INTO codes (code, recompensa, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (code, recompensa, created_at or 0, expires_at or 0),
            )
    except sqlite3.OperationalError:
        pass

    try:
        legacy_cursor.execute("SELECT code, user_id, redeemed_at FROM code_redemptions")
        for code, user_id, redeemed_at in legacy_cursor.fetchall():
            cursor.execute(
                """
                INSERT OR IGNORE INTO code_redemptions (code, user_id, redeemed_at)
                VALUES (?, ?, ?)
                """,
                (code, user_id, redeemed_at),
            )
    except sqlite3.OperationalError:
        pass
    finally:
        legacy.close()
    cursor.execute(
        "INSERT OR REPLACE INTO code_storage_meta (key, value) VALUES ('legacy_codes_migrated', 'done')"
    )
    cursor.execute(
        "INSERT OR REPLACE INTO code_storage_meta (key, value) VALUES ('legacy_codes_import_v2', 'done')"
    )


def connect_codes_db():
    conn = sqlite3.connect(CODES_DB_PATH)
    cursor = conn.cursor()
    ensure_codes_schema(cursor)
    migrate_legacy_codes(cursor)
    conn.commit()
    return conn


def init_codes_db():
    conn = connect_codes_db()
    conn.close()
