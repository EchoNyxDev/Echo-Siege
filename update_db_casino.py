import sqlite3

from systems.casino_manager import ensure_casino_schema, get_config
from utils.db import PLAYERS_DB_PATH, backup_databases, configure_sqlite_paths


def main():
    configure_sqlite_paths()
    backups = backup_databases(reason="casino_update", force=True)

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    ensure_casino_schema(cursor)
    config = get_config(cursor)
    conn.commit()
    conn.close()

    print("Atualizacao do Cassino de Wolford concluida.")
    print(f"Banco usado: {PLAYERS_DB_PATH}")
    if backups:
        print("Backup criado:")
        for backup in backups:
            print(f"- {backup}")
    else:
        print("Nenhum backup foi criado porque nao havia banco para copiar.")
    print(
        "Configuracao: "
        f"ativo={config['active']} | jackpot={config['jackpot']} | "
        f"compra={config['chip_buy_rate']} Gold/ficha | venda={config['chip_sell_rate']} Gold/ficha | "
        f"limite diario={config['daily_buy_limit']} fichas"
    )


if __name__ == "__main__":
    main()
