import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("ECHO_DATA_DIR", ROOT_DIR)).resolve()
BACKUP_DIR = Path(os.environ.get("ECHO_BACKUP_DIR", DATA_DIR / "backups" / "auto")).resolve()

PLAYERS_DB_PATH = Path(os.environ.get("ECHO_PLAYERS_DB", DATA_DIR / "players.db")).resolve()
CODES_DB_PATH = Path(os.environ.get("ECHO_CODES_DB", DATA_DIR / "codes.db")).resolve()

_ORIGINAL_CONNECT = sqlite3.connect
_PATCHED = False


def resolve_db_path(database):
    if isinstance(database, os.PathLike):
        database = os.fspath(database)
    if not isinstance(database, str):
        return database

    normalized = database.replace("\\", "/").strip()
    if normalized in {"players.db", "./players.db"}:
        return str(PLAYERS_DB_PATH)
    if normalized in {"codes.db", "./codes.db"}:
        return str(CODES_DB_PATH)
    return database


def configure_sqlite_paths():
    global _PATCHED
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    _seed_database(PLAYERS_DB_PATH, ROOT_DIR / "players.db")
    _seed_database(CODES_DB_PATH, ROOT_DIR / "codes.db")
    if _PATCHED:
        return

    def connect(database, *args, **kwargs):
        database = resolve_db_path(database)
        kwargs.setdefault("timeout", 20.0)
        return _ORIGINAL_CONNECT(database, *args, **kwargs)

    sqlite3.connect = connect
    _PATCHED = True


def _seed_database(target, source):
    target = Path(target)
    source = Path(source)
    if target == source or target.exists() or not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _latest_backup_age_seconds(prefix):
    if not BACKUP_DIR.exists():
        return None
    backups = sorted(BACKUP_DIR.glob(f"{prefix}_*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not backups:
        return None
    return datetime.now(timezone.utc).timestamp() - backups[0].stat().st_mtime


def _backup_sqlite_file(source, prefix, reason):
    source = Path(source)
    if not source.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    destination = BACKUP_DIR / f"{prefix}_{_timestamp()}_{reason}.db"
    source_conn = _ORIGINAL_CONNECT(str(source), timeout=20.0)
    dest_conn = _ORIGINAL_CONNECT(str(destination), timeout=20.0)
    try:
        source_conn.backup(dest_conn)
    finally:
        dest_conn.close()
        source_conn.close()
    return destination


def _copy_non_sqlite_file(source, prefix, reason):
    source = Path(source)
    if not source.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    destination = BACKUP_DIR / f"{prefix}_{_timestamp()}_{reason}.db"
    shutil.copy2(source, destination)
    return destination


def prune_backups(max_backups=30):
    if not BACKUP_DIR.exists():
        return []
    removed = []
    for prefix in ["players", "codes"]:
        backups = sorted(BACKUP_DIR.glob(f"{prefix}_*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
        for old in backups[max_backups:]:
            old.unlink(missing_ok=True)
            removed.append(old)
    return removed


def backup_databases(reason="auto", min_interval_hours=6, force=False, max_backups=30):
    configure_sqlite_paths()
    reason = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in str(reason or "auto"))[:32]
    min_age = max(0, float(min_interval_hours or 0)) * 3600
    created = []

    players_age = _latest_backup_age_seconds("players")
    if force or players_age is None or players_age >= min_age:
        backup = _backup_sqlite_file(PLAYERS_DB_PATH, "players", reason)
        if backup:
            created.append(backup)

    if CODES_DB_PATH.exists():
        codes_age = _latest_backup_age_seconds("codes")
        if force or codes_age is None or codes_age >= min_age:
            backup = _copy_non_sqlite_file(CODES_DB_PATH, "codes", reason)
            if backup:
                created.append(backup)

    prune_backups(max_backups=max_backups)
    return created


def list_database_backups(limit=10):
    if not BACKUP_DIR.exists():
        return []
    backups = sorted(BACKUP_DIR.glob("*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    return backups[: max(1, int(limit or 10))]
