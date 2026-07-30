import os
import shutil
import sqlite3
from datetime import datetime

from systems.nix_manager import ensure_nix_schema, get_global_state
from utils.db import configure_sqlite_paths


configure_sqlite_paths()

DB_PATH = "players.db"
BACKUP_DIR = "backups"


def backup_database():
    if not os.path.exists(DB_PATH):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = os.path.join(BACKUP_DIR, f"players_before_nix_{stamp}.db")
    shutil.copy2(DB_PATH, target)
    return target


def main():
    backup_path = backup_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ensure_nix_schema(cursor)
    conn.commit()
    state = get_global_state(cursor)
    conn.close()

    print("Migracao NIX concluida.")
    if backup_path:
        print(f"Backup criado: {backup_path}")
    print(
        "Estado global:",
        f"ativo={state.get('ativo')}",
        f"fase={state.get('fase_global')}",
        f"corrupcao={state.get('corrupcao')}",
    )


if __name__ == "__main__":
    main()
