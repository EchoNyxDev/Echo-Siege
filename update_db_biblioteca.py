import sqlite3

from systems.biblioteca_manager import ensure_biblioteca_schema, load_questions, get_config
from utils.db import PLAYERS_DB_PATH, backup_databases, configure_sqlite_paths


def main():
    configure_sqlite_paths()
    backups = backup_databases(reason="biblioteca_update", force=True)

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    ensure_biblioteca_schema(cursor)
    total_questions = len(load_questions(cursor))
    active = get_config(cursor, "active", "1")
    season = get_config(cursor, "season", "temporada_1")
    conn.commit()
    conn.close()

    print("Atualizacao da Biblioteca Perdida concluida.")
    print(f"Banco usado: {PLAYERS_DB_PATH}")
    if backups:
        print("Backup criado:")
        for backup in backups:
            print(f"- {backup}")
    else:
        print("Nenhum backup foi criado porque nao havia banco para copiar.")
    print(f"Configuracao: ativo={active} | temporada={season} | perguntas={total_questions}")


if __name__ == "__main__":
    main()
