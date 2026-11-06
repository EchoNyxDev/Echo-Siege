import asyncio
import hashlib
import re
import sqlite3
from copy import deepcopy


DEFAULT_LANGUAGE = "pt"
SUPPORTED_LANGUAGES = {
    "auto": "Automático",
    "pt": "Português (Brasil)",
    "en": "English",
    "es": "Español",
}

LANGUAGE_ALIASES = {
    "auto": "auto",
    "automatico": "auto",
    "automático": "auto",
    "default": "auto",
    "padrao": "auto",
    "padrão": "auto",
    "pt": "pt",
    "br": "pt",
    "ptbr": "pt",
    "pt_br": "pt",
    "pt-br": "pt",
    "portugues": "pt",
    "português": "pt",
    "en": "en",
    "eng": "en",
    "english": "en",
    "ingles": "en",
    "inglês": "en",
    "es": "es",
    "esp": "es",
    "spanish": "es",
    "espanhol": "es",
    "espanol": "es",
    "español": "es",
}

BLOCK_RE = re.compile(
    r"(```.*?```|`[^`]*`|https?://\S+|<a?:\w+:\d+>|<[@#!&]?\d+>)",
    re.DOTALL,
)


def _truncate(value, limit):
    value = str(value or "")
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 3)].rstrip() + "..."


def _embed_text_size(data):
    total = len(str(data.get("title") or "")) + len(str(data.get("description") or ""))
    total += len(str(data.get("footer", {}).get("text") or ""))
    total += len(str(data.get("author", {}).get("name") or ""))
    for field in data.get("fields", []):
        total += len(str(field.get("name") or "")) + len(str(field.get("value") or ""))
    return total


def _fit_embed_total(data, limit=6000):
    overflow = _embed_text_size(data) - limit
    if overflow <= 0:
        return data

    candidates = [field for field in reversed(data.get("fields", []))]
    for field in candidates:
        if overflow <= 0:
            break
        value = str(field.get("value") or "")
        removable = max(0, len(value) - 80)
        cut = min(overflow, removable)
        if cut:
            field["value"] = _truncate(value, len(value) - cut)
            overflow = _embed_text_size(data) - limit

    if overflow > 0 and data.get("description"):
        description = str(data["description"])
        data["description"] = _truncate(description, max(80, len(description) - overflow))
    return data


def ensure_i18n_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS player_settings(
            user_id TEXT PRIMARY KEY,
            language TEXT DEFAULT 'auto'
        )
        """
    )
    cursor.execute("PRAGMA table_info(player_settings)")
    columns = {row[1] for row in cursor.fetchall()}
    if "language" not in columns:
        cursor.execute("ALTER TABLE player_settings ADD COLUMN language TEXT DEFAULT 'auto'")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS translation_cache(
            cache_key TEXT PRIMARY KEY,
            source_lang TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            source_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
        """
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_translation_cache_lang ON translation_cache(target_lang)")


def normalize_language(value):
    key = normalize_key(value)
    return LANGUAGE_ALIASES.get(key)


def normalize_key(value):
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("-", "_")
    return "".join(char if char.isalnum() or char == "_" else "_" for char in text).strip("_")


def language_from_locale(locale):
    raw = str(locale or "").lower().replace("_", "-")
    if raw.startswith("en"):
        return "en"
    if raw.startswith("es"):
        return "es"
    if raw.startswith("pt"):
        return "pt"
    return DEFAULT_LANGUAGE


def _connect():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    ensure_i18n_schema(cursor)
    return conn, cursor


def set_user_language(user_id, language):
    lang = normalize_language(language)
    if not lang:
        return None
    conn, cursor = _connect()
    try:
        cursor.execute(
            """
            INSERT INTO player_settings(user_id, language)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
            """,
            (str(user_id), lang),
        )
        conn.commit()
    finally:
        conn.close()
    return lang


def get_stored_language(user_id):
    conn, cursor = _connect()
    try:
        cursor.execute("SELECT language FROM player_settings WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return normalize_language(row[0]) if row and row[0] else "auto"
    finally:
        conn.close()


def resolve_user_language(user=None, guild=None, explicit_locale=None):
    user_id = getattr(user, "id", None) if user is not None else None
    stored = get_stored_language(user_id) if user_id else "auto"
    if stored and stored != "auto":
        return stored

    locale = explicit_locale or getattr(user, "locale", None) or getattr(guild, "preferred_locale", None)
    return language_from_locale(locale)


def _cache_key(text, target_lang, source_lang="pt"):
    raw = f"{source_lang}\0{target_lang}\0{text}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def _read_cache(text, target_lang, source_lang="pt"):
    key = _cache_key(text, target_lang, source_lang)
    conn, cursor = _connect()
    try:
        cursor.execute(
            "SELECT translated_text FROM translation_cache WHERE cache_key = ?",
            (key,),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def _write_cache(text, translated, target_lang, source_lang="pt"):
    key = _cache_key(text, target_lang, source_lang)
    conn, cursor = _connect()
    try:
        cursor.execute(
            """
            INSERT OR REPLACE INTO translation_cache(
                cache_key, source_lang, target_lang, source_text, translated_text
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (key, source_lang, target_lang, text, translated),
        )
        conn.commit()
    finally:
        conn.close()


def _provider_translate(text, target_lang, source_lang="pt"):
    try:
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception:
        pass

    try:
        from googletrans import Translator

        translator = Translator()
        result = translator.translate(text, src=source_lang, dest=target_lang)
        return getattr(result, "text", None)
    except Exception:
        return None


def _translate_uncached(text, target_lang, source_lang="pt"):
    pieces = BLOCK_RE.split(str(text))
    translated_pieces = []
    for piece in pieces:
        if not piece:
            continue
        if BLOCK_RE.fullmatch(piece) or not piece.strip():
            translated_pieces.append(piece)
            continue
        translated = _provider_translate(piece, target_lang, source_lang)
        translated_pieces.append(translated if translated else piece)
    return "".join(translated_pieces)


def translate_text_sync(text, target_lang, source_lang="pt"):
    if text is None:
        return None
    target_lang = normalize_language(target_lang) or DEFAULT_LANGUAGE
    if target_lang in {"auto", source_lang, DEFAULT_LANGUAGE}:
        return str(text)

    original = str(text)
    if not original.strip():
        return original

    cached = _read_cache(original, target_lang, source_lang)
    if cached is not None:
        return cached

    translated = _translate_uncached(original, target_lang, source_lang)
    if translated and translated != original:
        _write_cache(original, translated, target_lang, source_lang)
    return translated or original


async def translate_text(text, target_lang, source_lang="pt"):
    return await asyncio.to_thread(translate_text_sync, text, target_lang, source_lang)


async def translate_embed(embed, target_lang):
    if embed is None or target_lang in {"auto", "pt"}:
        return embed

    data = deepcopy(embed.to_dict())
    if data.get("title"):
        data["title"] = _truncate(await translate_text(data["title"], target_lang), 256)
    if data.get("description"):
        data["description"] = _truncate(await translate_text(data["description"], target_lang), 4096)

    for field in data.get("fields", []):
        if field.get("name"):
            field["name"] = _truncate(await translate_text(field["name"], target_lang), 256)
        if field.get("value"):
            field["value"] = _truncate(await translate_text(field["value"], target_lang), 1024)

    if data.get("footer", {}).get("text"):
        data["footer"]["text"] = _truncate(await translate_text(data["footer"]["text"], target_lang), 2048)
    if data.get("author", {}).get("name"):
        data["author"]["name"] = _truncate(await translate_text(data["author"]["name"], target_lang), 256)

    return embed.__class__.from_dict(_fit_embed_total(data))


async def localize_send_payload(ctx_or_user, content=None, kwargs=None):
    kwargs = dict(kwargs or {})
    user = getattr(ctx_or_user, "author", ctx_or_user)
    guild = getattr(ctx_or_user, "guild", None)
    language = resolve_user_language(user=user, guild=guild)
    if language in {"auto", "pt"}:
        return content, kwargs

    if content is not None:
        content = _truncate(await translate_text(content, language), 2000)

    if kwargs.get("embed") is not None:
        kwargs["embed"] = await translate_embed(kwargs["embed"], language)

    if kwargs.get("embeds"):
        kwargs["embeds"] = [await translate_embed(embed, language) for embed in kwargs["embeds"]]

    return content, kwargs


def translation_backend_status():
    try:
        import deep_translator  # noqa: F401

        return "deep-translator"
    except Exception:
        pass
    try:
        import googletrans  # noqa: F401

        return "googletrans"
    except Exception:
        return None
