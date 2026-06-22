import sqlite3
import time

from utils.db import backup_databases, configure_sqlite_paths


def add_column(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_world_cup_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_teams(
            user_id TEXT PRIMARY KEY,
            team_name TEXT,
            formation TEXT,
            captain_id TEXT,
            created_at INTEGER DEFAULT 0,
            last_match INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_lineups(
            user_id TEXT NOT NULL,
            slot INTEGER NOT NULL,
            hero_instance_id INTEGER NOT NULL,
            hero_id TEXT NOT NULL,
            position TEXT NOT NULL,
            PRIMARY KEY (user_id, slot)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_progress(
            user_id TEXT PRIMARY KEY,
            stage TEXT DEFAULT 'grupos',
            points INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            best_stage TEXT DEFAULT 'Fase de grupos',
            medals INTEGER DEFAULT 0
        )
    """)
    add_column(cursor, "world_cup_progress", "current_run", "INTEGER DEFAULT 1")
    add_column(cursor, "world_cup_progress", "unbeaten_streak", "INTEGER DEFAULT 0")
    add_column(cursor, "world_cup_progress", "best_unbeaten_streak", "INTEGER DEFAULT 0")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_matches(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            opponent_name TEXT NOT NULL,
            stage TEXT NOT NULL,
            user_score INTEGER DEFAULT 0,
            opponent_score INTEGER DEFAULT 0,
            result TEXT NOT NULL,
            created_at INTEGER DEFAULT 0
        )
    """)
    add_column(cursor, "world_cup_matches", "run_id", "INTEGER DEFAULT 1")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_player_stats(
            user_id TEXT NOT NULL,
            hero_id TEXT NOT NULL,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, hero_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_settings(
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_hall(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            team_name TEXT,
            title TEXT,
            stat_name TEXT,
            stat_value TEXT,
            created_at INTEGER DEFAULT 0
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO world_cup_settings (key, value) VALUES ('active', '0')")
    cursor.execute("INSERT OR IGNORE INTO world_cup_settings (key, value) VALUES ('started_at', '0')")
    cursor.execute("INSERT OR IGNORE INTO world_cup_settings (key, value) VALUES ('ended_at', '0')")


def main():
    configure_sqlite_paths()
    backups = backup_databases(reason="before_copa_update", force=True)
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    ensure_world_cup_schema(cursor)
    conn.commit()
    conn.close()

    print("Tabelas da Copa criadas/atualizadas com seguranca.")
    if backups:
        print("Backups criados antes da migracao:")
        for path in backups:
            print(f"- {path}")
    else:
        print("Nenhum backup novo foi necessario.")
    print(f"Finalizado em {int(time.time())}.")


if __name__ == "__main__":
    main()
