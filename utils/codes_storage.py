import os
import sqlite3


CODES_DB_PATH = "players.db"
LEGACY_CODES_DB_PATH = "codes.db"


def ensure_codes_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            recompensa TEXT NOT NULL,
            created_at INTEGER DEFAULT 0,
            expires_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(codes)")
    code_columns = {row[1] for row in cursor.fetchall()}
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


def migrate_legacy_codes(cursor):
    cursor.execute("SELECT value FROM code_storage_meta WHERE key = 'legacy_codes_migrated'")
    if cursor.fetchone():
        return

    if not os.path.exists(LEGACY_CODES_DB_PATH):
        cursor.execute(
            "INSERT OR REPLACE INTO code_storage_meta (key, value) VALUES ('legacy_codes_migrated', 'missing')"
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
