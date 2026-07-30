import datetime
import sqlite3
import time

from data.casino_config import DEFAULT_CASINO_CONFIG, MAX_BET, MIN_BET


def now_ts():
    return int(time.time())


def today_key():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def add_column_if_missing(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_casino_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players(
            user_id TEXT PRIMARY KEY,
            gold INTEGER DEFAULT 0,
            gems INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(players)")
    player_columns = {row[1] for row in cursor.fetchall()}
    for column, ddl in {
        "gold": "INTEGER DEFAULT 0",
        "gems": "INTEGER DEFAULT 0",
    }.items():
        if column not in player_columns:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {column} {ddl}")

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
    cursor.execute("PRAGMA table_info(summon_data)")
    summon_columns = {row[1] for row in cursor.fetchall()}
    if "summon_tickets" not in summon_columns:
        cursor.execute("ALTER TABLE summon_data ADD COLUMN summon_tickets INTEGER DEFAULT 0")
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
        CREATE TABLE IF NOT EXISTS casino_players (
            user_id TEXT PRIMARY KEY,
            chips INTEGER DEFAULT 0,
            total_bet INTEGER DEFAULT 0,
            total_won INTEGER DEFAULT 0,
            total_lost INTEGER DEFAULT 0,
            biggest_win INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            blackjack_wins INTEGER DEFAULT 0,
            coinflip_wins INTEGER DEFAULT 0,
            slots_wins INTEGER DEFAULT 0,
            roulette_wins INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0,
            updated_at INTEGER DEFAULT 0
        )
    """)
    for column, ddl in {
        "chips": "INTEGER DEFAULT 0",
        "total_bet": "INTEGER DEFAULT 0",
        "total_won": "INTEGER DEFAULT 0",
        "total_lost": "INTEGER DEFAULT 0",
        "biggest_win": "INTEGER DEFAULT 0",
        "games_played": "INTEGER DEFAULT 0",
        "blackjack_wins": "INTEGER DEFAULT 0",
        "coinflip_wins": "INTEGER DEFAULT 0",
        "slots_wins": "INTEGER DEFAULT 0",
        "roulette_wins": "INTEGER DEFAULT 0",
        "created_at": "INTEGER DEFAULT 0",
        "updated_at": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "casino_players", column, ddl)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            game TEXT NOT NULL,
            bet INTEGER NOT NULL,
            payout INTEGER DEFAULT 0,
            result TEXT NOT NULL,
            details TEXT,
            created_at INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchased_at INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            active INTEGER DEFAULT 1,
            jackpot INTEGER DEFAULT 0,
            chip_buy_rate INTEGER DEFAULT 100,
            chip_sell_rate INTEGER DEFAULT 50,
            daily_buy_limit INTEGER DEFAULT 500,
            updated_at INTEGER DEFAULT 0
        )
    """)
    for column, ddl in {
        "active": "INTEGER DEFAULT 1",
        "jackpot": "INTEGER DEFAULT 0",
        "chip_buy_rate": "INTEGER DEFAULT 100",
        "chip_sell_rate": "INTEGER DEFAULT 50",
        "daily_buy_limit": "INTEGER DEFAULT 500",
        "updated_at": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "casino_config", column, ddl)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_daily_limits (
            user_id TEXT PRIMARY KEY,
            chips_bought_today INTEGER DEFAULT 0,
            last_reset_date TEXT
        )
    """)
    for column, ddl in {
        "chips_bought_today": "INTEGER DEFAULT 0",
        "last_reset_date": "TEXT",
    }.items():
        add_column_if_missing(cursor, "casino_daily_limits", column, ddl)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_blackjack_sessions (
            user_id TEXT PRIMARY KEY,
            bet INTEGER NOT NULL,
            player_hand TEXT NOT NULL,
            dealer_hand TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL
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
        INSERT OR IGNORE INTO casino_config (
            id, active, jackpot, chip_buy_rate, chip_sell_rate, daily_buy_limit, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        DEFAULT_CASINO_CONFIG["active"],
        DEFAULT_CASINO_CONFIG["jackpot"],
        DEFAULT_CASINO_CONFIG["chip_buy_rate"],
        DEFAULT_CASINO_CONFIG["chip_sell_rate"],
        DEFAULT_CASINO_CONFIG["daily_buy_limit"],
        now_ts(),
    ))


def ensure_player(cursor, user_id):
    user_id = str(user_id)
    timestamp = now_ts()
    cursor.execute(
        "INSERT OR IGNORE INTO casino_players (user_id, created_at, updated_at) VALUES (?, ?, ?)",
        (user_id, timestamp, timestamp),
    )


def get_config(cursor):
    ensure_casino_schema(cursor)
    cursor.execute("SELECT active, jackpot, chip_buy_rate, chip_sell_rate, daily_buy_limit FROM casino_config WHERE id = 1")
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT OR IGNORE INTO casino_config (id, active, jackpot, chip_buy_rate, chip_sell_rate, daily_buy_limit, updated_at) VALUES (1, 1, 0, 100, 50, 500, ?)",
            (now_ts(),),
        )
        return dict(DEFAULT_CASINO_CONFIG)
    return {
        "active": int(row[0] or 0),
        "jackpot": int(row[1] or 0),
        "chip_buy_rate": int(row[2] or 100),
        "chip_sell_rate": int(row[3] or 50),
        "daily_buy_limit": int(row[4] or 500),
    }


def casino_is_active(cursor):
    return bool(get_config(cursor)["active"])


def get_balance(cursor, user_id):
    ensure_casino_schema(cursor)
    ensure_player(cursor, user_id)
    cursor.execute("SELECT chips FROM casino_players WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    return int(row[0] or 0) if row else 0


def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute(
        "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)",
        (str(user_id), str(stat)),
    )
    cursor.execute(
        "UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?",
        (int(amount), str(user_id), str(stat)),
    )


def set_stat_max(cursor, user_id, stat, value):
    cursor.execute(
        "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)",
        (str(user_id), str(stat)),
    )
    cursor.execute(
        "UPDATE player_stats SET value = max(value, ?) WHERE user_id = ? AND stat = ?",
        (int(value), str(user_id), str(stat)),
    )


def log_admin(cursor, user_id, action, value="", admin_id=None):
    cursor.execute(
        """
        INSERT INTO administrative_logs (user_id, action, value, admin_id, timestamp, status)
        VALUES (?, ?, ?, ?, ?, 'resolved')
        """,
        (str(user_id), str(action)[:80], str(value or "")[:900], str(admin_id) if admin_id else None, now_ts()),
    )


def add_chips(cursor, user_id, amount, reason="ajuste", admin_id=None):
    amount = int(amount)
    if amount <= 0:
        raise ValueError("A quantidade de fichas precisa ser positiva.")
    ensure_player(cursor, user_id)
    cursor.execute(
        "UPDATE casino_players SET chips = chips + ?, updated_at = ? WHERE user_id = ?",
        (amount, now_ts(), str(user_id)),
    )
    log_admin(cursor, user_id, f"casino_{reason}", f"+{amount} fichas", admin_id)


def remove_chips(cursor, user_id, amount):
    amount = int(amount)
    if amount <= 0:
        return False
    ensure_player(cursor, user_id)
    cursor.execute("SELECT chips FROM casino_players WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    if not row or int(row[0] or 0) < amount:
        return False
    cursor.execute(
        "UPDATE casino_players SET chips = chips - ?, updated_at = ? WHERE user_id = ?",
        (amount, now_ts(), str(user_id)),
    )
    return True


def validate_bet(cursor, user_id, bet):
    if not casino_is_active(cursor):
        return False, "O Fallen Angel está fechado."
    try:
        bet = int(bet)
    except (TypeError, ValueError):
        return False, "A aposta precisa ser um número inteiro."
    if bet < MIN_BET:
        return False, f"Aposta mínima: {MIN_BET} ficha."
    if bet > MAX_BET:
        return False, f"Aposta máxima: {MAX_BET:,} fichas."
    if get_balance(cursor, user_id) < bet:
        return False, "Fichas insuficientes."
    return True, bet


def place_bet(cursor, user_id, bet):
    ok, value = validate_bet(cursor, user_id, bet)
    if not ok:
        return False, value
    bet = int(value)
    if not remove_chips(cursor, user_id, bet):
        return False, "Fichas insuficientes."
    cursor.execute(
        """
        UPDATE casino_players
        SET total_bet = total_bet + ?, games_played = games_played + 1, updated_at = ?
        WHERE user_id = ?
        """,
        (bet, now_ts(), str(user_id)),
    )
    add_stat(cursor, user_id, "casino_games_played", 1)
    return True, bet


def increase_active_bet(cursor, user_id, amount):
    amount = int(amount)
    if not remove_chips(cursor, user_id, amount):
        return False
    cursor.execute(
        "UPDATE casino_players SET total_bet = total_bet + ?, updated_at = ? WHERE user_id = ?",
        (amount, now_ts(), str(user_id)),
    )
    return True


def _update_streaks(cursor, user_id, bet, payout):
    if payout > bet:
        add_stat(cursor, user_id, "casino_wins", 1)
        cursor.execute(
            "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, 'casino_loss_streak_current', 0)",
            (str(user_id),),
        )
        cursor.execute(
            "UPDATE player_stats SET value = 0 WHERE user_id = ? AND stat = 'casino_loss_streak_current'",
            (str(user_id),),
        )
    elif payout == 0:
        add_stat(cursor, user_id, "casino_loss_streak_current", 1)
        cursor.execute(
            "SELECT value FROM player_stats WHERE user_id = ? AND stat = 'casino_loss_streak_current'",
            (str(user_id),),
        )
        current = int((cursor.fetchone() or [0])[0] or 0)
        set_stat_max(cursor, user_id, "casino_loss_streak_best", current)


def settle_bet(cursor, user_id, game, bet, payout, result, details="", win_stat=None):
    user_id = str(user_id)
    bet = int(bet)
    payout = int(payout or 0)
    ensure_player(cursor, user_id)
    if payout > 0:
        cursor.execute(
            "UPDATE casino_players SET chips = chips + ? WHERE user_id = ?",
            (payout, user_id),
        )
    net = payout - bet
    won = max(0, net)
    lost = max(0, -net)
    cursor.execute(
        """
        UPDATE casino_players
        SET total_won = total_won + ?,
            total_lost = total_lost + ?,
            biggest_win = max(biggest_win, ?),
            updated_at = ?
        WHERE user_id = ?
        """,
        (won, lost, won, now_ts(), user_id),
    )
    if win_stat and payout > bet:
        cursor.execute(f"UPDATE casino_players SET {win_stat} = {win_stat} + 1 WHERE user_id = ?", (user_id,))
    _update_streaks(cursor, user_id, bet, payout)
    record_history(cursor, user_id, game, bet, payout, result, details)
    if won >= 10000:
        log_admin(cursor, user_id, "casino_vitoria_grande", f"{game}: +{won:,} fichas | {details}")


def record_history(cursor, user_id, game, bet, payout, result, details=""):
    cursor.execute(
        """
        INSERT INTO casino_history (user_id, game, bet, payout, result, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (str(user_id), str(game), int(bet), int(payout or 0), str(result), str(details or "")[:900], now_ts()),
    )


def add_jackpot(cursor, amount):
    amount = max(0, int(amount or 0))
    if amount:
        cursor.execute("UPDATE casino_config SET jackpot = jackpot + ?, updated_at = ? WHERE id = 1", (amount, now_ts()))


def claim_jackpot(cursor):
    config = get_config(cursor)
    jackpot = int(config["jackpot"] or 0)
    cursor.execute("UPDATE casino_config SET jackpot = 0, updated_at = ? WHERE id = 1", (now_ts(),))
    return jackpot


def reset_daily_limit_if_needed(cursor, user_id):
    today = today_key()
    cursor.execute(
        "INSERT OR IGNORE INTO casino_daily_limits (user_id, chips_bought_today, last_reset_date) VALUES (?, 0, ?)",
        (str(user_id), today),
    )
    cursor.execute("SELECT last_reset_date FROM casino_daily_limits WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    if not row or row[0] != today:
        cursor.execute(
            "UPDATE casino_daily_limits SET chips_bought_today = 0, last_reset_date = ? WHERE user_id = ?",
            (today, str(user_id)),
        )


def chips_bought_today(cursor, user_id):
    reset_daily_limit_if_needed(cursor, user_id)
    cursor.execute("SELECT chips_bought_today FROM casino_daily_limits WHERE user_id = ?", (str(user_id),))
    return int((cursor.fetchone() or [0])[0] or 0)


def add_daily_purchase(cursor, user_id, chips):
    reset_daily_limit_if_needed(cursor, user_id)
    cursor.execute(
        "UPDATE casino_daily_limits SET chips_bought_today = chips_bought_today + ? WHERE user_id = ?",
        (int(chips), str(user_id)),
    )


def count_purchases(cursor, user_id, item_id, since_ts=0):
    cursor.execute(
        """
        SELECT COALESCE(SUM(quantity), 0)
        FROM casino_purchases
        WHERE user_id = ? AND item_id = ? AND purchased_at >= ?
        """,
        (str(user_id), str(item_id), int(since_ts or 0)),
    )
    return int((cursor.fetchone() or [0])[0] or 0)
