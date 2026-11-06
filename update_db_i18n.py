import sqlite3

from systems.i18n import ensure_i18n_schema
from utils.db import backup_databases, configure_sqlite_paths


def main():
    configure_sqlite_paths()
    backups = backup_databases(reason="before_i18n", min_interval_hours=0, force=True)

    conn = sqlite3.connect("players.db")
    try:
        cursor = conn.cursor()
        ensure_i18n_schema(cursor)
        conn.commit()
    finally:
        conn.close()

    print("Migracao de idiomas concluida.")
    if backups:
        print("Backup criado:", ", ".join(str(path) for path in backups))


if __name__ == "__main__":
    main()
