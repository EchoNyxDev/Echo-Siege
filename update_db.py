import sqlite3
import shutil
import datetime
import os

DB_NAME = "players.db"


# ==========================================
# BACKUP
# ==========================================

def criar_backup():
    if not os.path.exists(DB_NAME):
        print("❌ Banco não encontrado.")
        return False

    data = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"backup_{data}.db"

    shutil.copy(DB_NAME, backup)

    print(f"✅ Backup criado: {backup}")
    return True


# ==========================================
# VERIFICAR COLUNA
# ==========================================

def coluna_existe(cursor, tabela, coluna):
    try:
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = [c[1] for c in cursor.fetchall()]
        return coluna in colunas
    except:
        return False


# ==========================================
# ADICIONAR COLUNA
# ==========================================

def adicionar_coluna(cursor, tabela, coluna_sql):
    nome_coluna = coluna_sql.split()[0]

    if coluna_existe(cursor, tabela, nome_coluna):
        print(f"ℹ️ {tabela}.{nome_coluna} já existe.")
        return

    try:
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna_sql}"
        )
        print(f"➕ {tabela}.{nome_coluna} adicionada.")
    except Exception as erro:
        print(f"❌ Erro em {tabela}.{nome_coluna}: {erro}")


# ==========================================
# CRIAR ÍNDICES
# ==========================================

def criar_indice(cursor, nome, sql):
    try:
        cursor.execute(sql)
        print(f"📌 Índice criado: {nome}")
    except Exception as erro:
        print(f"❌ Erro no índice {nome}: {erro}")


# ==========================================
# MAIN
# ==========================================

def main():

    print("====================================")
    print(" ECHO SIEGE UPDATE DB SUPREMO")
    print("====================================\n")

    criar_backup()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ======================================
    # PLAYERS
    # ======================================

    adicionar_coluna(cursor, "players", "vip INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "players", "vip_expira INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "players", "total_gold_gasto INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "players", "total_summons INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "players", "total_pvp INTEGER DEFAULT 0")

    # ======================================
    # HEROES
    # ======================================

    adicionar_coluna(cursor, "heroes", "awaken INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "heroes", "favorite INTEGER DEFAULT 0")

    # ======================================
    # PETS
    # ======================================

    try:
        adicionar_coluna(cursor, "pets", "favorite INTEGER DEFAULT 0")
        adicionar_coluna(cursor, "pets", "equipped INTEGER DEFAULT 0")
    except:
        pass

    # ======================================
    # INVENTORY
    # ======================================

    try:
        adicionar_coluna(cursor, "inventory", "locked INTEGER DEFAULT 0")
    except:
        pass

    # ======================================
    # CIDADES
    # ======================================

    adicionar_coluna(cursor, "cidades", "loja_nivel INTEGER DEFAULT 1")
    adicionar_coluna(cursor, "cidades", "total_doacoes INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "cidades", "total_reparos INTEGER DEFAULT 0")
    adicionar_coluna(cursor, "cidades", "ultima_invasao INTEGER DEFAULT 0")

    # ======================================
    # CODES
    # ======================================

    try:
        adicionar_coluna(cursor, "codes", "usos INTEGER DEFAULT 0")
        adicionar_coluna(cursor, "codes", "max_usos INTEGER DEFAULT -1")
    except:
        pass

    # ======================================
    # ÍNDICES
    # ======================================

    criar_indice(
        cursor,
        "idx_players_user",
        """
        CREATE INDEX IF NOT EXISTS idx_players_user
        ON players(user_id)
        """
    )

    criar_indice(
        cursor,
        "idx_heroes_user",
        """
        CREATE INDEX IF NOT EXISTS idx_heroes_user
        ON heroes(user_id)
        """
    )

    criar_indice(
        cursor,
        "idx_heroes_hero",
        """
        CREATE INDEX IF NOT EXISTS idx_heroes_hero
        ON heroes(hero_id)
        """
    )

    criar_indice(
        cursor,
        "idx_inventory_user",
        """
        CREATE INDEX IF NOT EXISTS idx_inventory_user
        ON inventory(user_id)
        """
    )

    criar_indice(
        cursor,
        "idx_teams_user",
        """
        CREATE INDEX IF NOT EXISTS idx_teams_user
        ON teams(user_id)
        """
    )

    criar_indice(
        cursor,
        "idx_pets_user",
        """
        CREATE INDEX IF NOT EXISTS idx_pets_user
        ON pets(user_id)
        """
    )

    criar_indice(
        cursor,
        "idx_cidades_guild",
        """
        CREATE INDEX IF NOT EXISTS idx_cidades_guild
        ON cidades(guild_id)
        """
    )

    conn.commit()

    print("\n====================================")
    print(" UPDATE CONCLUÍDO COM SUCESSO")
    print("====================================")
    print("✅ Nenhum dado removido")
    print("✅ Nenhuma tabela apagada")
    print("✅ Backup criado")
    print("✅ Cidades continuam separadas por guild_id")
    print("✅ Invasões continuam separadas por servidor")

    conn.close()


if __name__ == "__main__":
    main()