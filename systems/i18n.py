import asyncio
import hashlib
import json
import os
import re
import sqlite3
import threading
import time
from copy import deepcopy
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_LANGUAGE = "pt"
CACHE_VERSION = "2"
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

TRANSLATION_TIMEOUT = max(3.0, float(os.getenv("ECHO_TRANSLATION_TIMEOUT", "8")))
_DIAGNOSTICS_LOCK = threading.Lock()
_TRANSLATION_DIAGNOSTICS = {
    "provider": None,
    "last_error": None,
    "last_success": 0,
}


# Vocabulário usado para registrar aliases de comandos sem depender da rede.
# O tradutor HTTP continua responsável pelos diálogos e por palavras futuras.
COMMAND_TRANSLATIONS = {
    "aceitar": {"en": ("accept",), "es": ("aceptar",)},
    "adm": {"en": ("admin",), "es": ("admin",)},
    "ajuda": {"en": ("help", "commands"), "es": ("ayuda", "comandos")},
    "analisar": {"en": ("analyze",), "es": ("analizar",)},
    "adventure": {"en": ("adventure",), "es": ("aventura",)},
    "anime": {"en": ("anime",), "es": ("anime",)},
    "apoiar": {"en": ("support",), "es": ("apoyar",)},
    "aprimorar": {"en": ("upgrade",), "es": ("mejorar",)},
    "arena": {"en": ("arena", "tower"), "es": ("arena", "torre")},
    "arquivo": {"en": ("file", "archive"), "es": ("archivo",)},
    "arquivos": {"en": ("files", "archives"), "es": ("archivos",)},
    "atacar": {"en": ("attack",), "es": ("atacar",)},
    "atualiza": {"en": ("update", "patchnotes"), "es": ("actualizar", "parches")},
    "atualiza_thumb": {"en": ("update_thumb",), "es": ("actualizar_miniatura",)},
    "aventura": {"en": ("adventure",), "es": ("aventura",)},
    "abrir": {"en": ("open",), "es": ("abrir",)},
    "biblioteca": {"en": ("library",), "es": ("biblioteca",)},
    "blackjack": {"en": ("blackjack",), "es": ("blackjack",)},
    "backup": {"en": ("backup",), "es": ("respaldo",)},
    "banner": {"en": ("banner",), "es": ("banner",)},
    "boss": {"en": ("boss",), "es": ("jefe",)},
    "bug": {"en": ("bug", "report"), "es": ("bug", "reporte")},
    "caca": {"en": ("hunt",), "es": ("caza",)},
    "cacada": {"en": ("hunt",), "es": ("caceria",)},
    "calamidade": {"en": ("calamity",), "es": ("calamidad",)},
    "campeoes": {"en": ("champions",), "es": ("campeones",)},
    "cara": {"en": ("heads",), "es": ("cara",)},
    "cassino": {"en": ("casino",), "es": ("casino",)},
    "cd": {"en": ("cooldown", "cooldowns"), "es": ("esperas",)},
    "catalogo": {"en": ("catalog",), "es": ("catalogo",)},
    "catalogoperfil": {"en": ("catalogprofile",), "es": ("perfilcatalogo",)},
    "cidade": {"en": ("city",), "es": ("ciudad",)},
    "code": {"en": ("code",), "es": ("codigo",)},
    "codes": {"en": ("codes",), "es": ("codigos",)},
    "combate": {"en": ("combat",), "es": ("combate",)},
    "colecao": {"en": ("collection",), "es": ("coleccion",)},
    "comprar": {"en": ("buy", "purchase"), "es": ("comprar",)},
    "comprar_item": {"en": ("buyitem",), "es": ("comprarobjeto",)},
    "confrontar": {"en": ("confront",), "es": ("confrontar",)},
    "corrupcao": {"en": ("corruption",), "es": ("corrupcion",)},
    "conquistas": {"en": ("achievements",), "es": ("logros",)},
    "consertar": {"en": ("repair",), "es": ("reparar",)},
    "consumir": {"en": ("use", "consume"), "es": ("usar", "consumir")},
    "convite": {"en": ("invite",), "es": ("invitacion",)},
    "copa": {"en": ("worldcup",), "es": ("copa",)},
    "coroa": {"en": ("tails",), "es": ("cruz",)},
    "criar": {"en": ("create",), "es": ("crear",)},
    "criarcode": {"en": ("createcode",), "es": ("crearcode",)},
    "daily": {"en": ("daily",), "es": ("diario",)},
    "deletar": {"en": ("delete",), "es": ("eliminar",)},
    "descricao": {"en": ("description",), "es": ("descripcion",)},
    "desequipar": {"en": ("unequip",), "es": ("desequipar",)},
    "desistir": {"en": ("quit", "surrender"), "es": ("salir", "rendirse")},
    "dica": {"en": ("hint",), "es": ("pista",)},
    "diaria": {"en": ("daily",), "es": ("diaria",)},
    "doar": {"en": ("donate",), "es": ("donar",)},
    "dobrar": {"en": ("double",), "es": ("doblar",)},
    "dungeon": {"en": ("dungeon",), "es": ("mazmorra",)},
    "entrar": {"en": ("enter", "join"), "es": ("entrar", "unirse")},
    "entregar": {"en": ("complete", "submit"), "es": ("completar", "entregar")},
    "enfrentar": {"en": ("fight",), "es": ("pelear",)},
    "encerrar": {"en": ("end", "close"), "es": ("finalizar", "cerrar")},
    "equipamentos": {"en": ("equipment",), "es": ("equipamiento",)},
    "equipar": {"en": ("equip",), "es": ("equipar",)},
    "equiparpet": {"en": ("equippet",), "es": ("equiparmascota",)},
    "escolher": {"en": ("choose",), "es": ("elegir",)},
    "escolherheroi": {"en": ("choosehero",), "es": ("elegirheroe",)},
    "evento": {"en": ("event",), "es": ("evento",)},
    "eventos": {"en": ("events",), "es": ("eventos",)},
    "evoluir": {"en": ("evolve",), "es": ("evolucionar",)},
    "expedicao": {"en": ("expedition",), "es": ("expedicion",)},
    "explorar": {"en": ("explore",), "es": ("explorar",)},
    "fase": {"en": ("phase",), "es": ("fase",)},
    "fechar": {"en": ("close",), "es": ("cerrar",)},
    "final": {"en": ("ending", "final"), "es": ("final",)},
    "fragmentos": {"en": ("fragments",), "es": ("fragmentos",)},
    "forja": {"en": ("forge", "craft"), "es": ("forja", "fabricar")},
    "foto": {"en": ("image", "icon"), "es": ("foto", "icono")},
    "gemcomprar": {"en": ("gembuy",), "es": ("comprargemas",)},
    "gemshop": {"en": ("gemshop",), "es": ("tiendagemas",)},
    "give": {"en": ("give",), "es": ("dar",)},
    "guild": {"en": ("guild",), "es": ("gremio",)},
    "heroi": {"en": ("hero",), "es": ("heroe",)},
    "herois": {"en": ("heroes",), "es": ("heroes",)},
    "historico": {"en": ("history",), "es": ("historial",)},
    "hall": {"en": ("hall", "halloffame"), "es": ("salon",)},
    "help": {"en": ("help",), "es": ("ayuda",)},
    "hunt": {"en": ("hunt",), "es": ("cazar",)},
    "idioma": {"en": ("language",), "es": ("idioma",)},
    "iniciar": {"en": ("start",), "es": ("comenzar", "iniciar")},
    "investigar": {"en": ("investigate",), "es": ("investigar",)},
    "jogar": {"en": ("play",), "es": ("jugar",)},
    "labirinto": {"en": ("maze",), "es": ("laberinto",)},
    "language": {"en": ("language",), "es": ("idioma", "lenguaje")},
    "lider": {"en": ("leader",), "es": ("lider",)},
    "lista": {"en": ("list", "search"), "es": ("lista", "buscar")},
    "listar": {"en": ("list",), "es": ("listar",)},
    "loja": {"en": ("shop", "store"), "es": ("tienda",)},
    "lutar": {"en": ("fight",), "es": ("pelear",)},
    "melhorar": {"en": ("upgrade",), "es": ("mejorar",)},
    "main": {"en": ("main",), "es": ("principal",)},
    "membros": {"en": ("members",), "es": ("miembros",)},
    "missao": {"en": ("mission",), "es": ("mision", "misión")},
    "modo": {"en": ("mode",), "es": ("modo",)},
    "mochila": {"en": ("inventory", "backpack"), "es": ("inventario", "mochila")},
    "moldura": {"en": ("frame",), "es": ("marco",)},
    "negociar": {"en": ("negotiate",), "es": ("negociar",)},
    "nix": {"en": ("nix",), "es": ("nix",)},
    "pausar": {"en": ("pause",), "es": ("pausar",)},
    "pay": {"en": ("pay",), "es": ("pagar",)},
    "perdoar": {"en": ("forgive",), "es": ("perdonar",)},
    "parar": {"en": ("stand", "stop"), "es": ("parar", "plantarse")},
    "party": {"en": ("party", "team"), "es": ("equipo", "grupo")},
    "pedir": {"en": ("hit",), "es": ("pedir",)},
    "pedidos": {"en": ("requests",), "es": ("solicitudes",)},
    "perfil": {"en": ("profile",), "es": ("perfil",)},
    "pets": {"en": ("pets",), "es": ("mascotas",)},
    "protocolo": {"en": ("protocol",), "es": ("protocolo",)},
    "pvp": {"en": ("pvp",), "es": ("pvp",)},
    "raid": {"en": ("raid",), "es": ("incursion",)},
    "raid_spawn": {"en": ("raid_spawn",), "es": ("iniciar_incursion",)},
    "raid_timeskip": {"en": ("raid_timeskip",), "es": ("saltar_tiempo_incursion",)},
    "rank": {"en": ("rank", "leaderboard"), "es": ("clasificacion",)},
    "ranking": {"en": ("ranking", "leaderboard"), "es": ("clasificacion", "ranking")},
    "refinar": {"en": ("refine",), "es": ("refinar",)},
    "resgatar": {"en": ("claim", "redeem"), "es": ("reclamar", "canjear")},
    "reset": {"en": ("reset",), "es": ("reiniciar",)},
    "resolver": {"en": ("resolve",), "es": ("resolver",)},
    "reabrir": {"en": ("reopen",), "es": ("reabrir",)},
    "responder": {"en": ("answer",), "es": ("responder",)},
    "roleta": {"en": ("roulette",), "es": ("ruleta",)},
    "sair": {"en": ("leave", "exit"), "es": ("salir",)},
    "saldo": {"en": ("balance",), "es": ("saldo",)},
    "slot": {"en": ("slot", "slots"), "es": ("tragaperras",)},
    "stats": {"en": ("stats",), "es": ("estadisticas",)},
    "status": {"en": ("status",), "es": ("estado",)},
    "teste": {"en": ("test",), "es": ("prueba",)},
    "summon": {"en": ("summon",), "es": ("invocar",)},
    "ticketheroi": {"en": ("heroticket",), "es": ("ticketheroe",)},
    "time": {"en": ("team",), "es": ("equipo",)},
    "titulo": {"en": ("title",), "es": ("titulo",)},
    "tutorial": {"en": ("tutorial", "guide"), "es": ("tutorial", "guia")},
    "vender": {"en": ("sell",), "es": ("vender",)},
    "work": {"en": ("work",), "es": ("trabajar",)},
}


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
    raw = f"{CACHE_VERSION}\0{source_lang}\0{target_lang}\0{text}".encode("utf-8", errors="ignore")
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


def _record_translation_result(provider=None, error=None):
    with _DIAGNOSTICS_LOCK:
        if provider:
            _TRANSLATION_DIAGNOSTICS["provider"] = provider
            _TRANSLATION_DIAGNOSTICS["last_success"] = int(time.time())
            _TRANSLATION_DIAGNOSTICS["last_error"] = None
        elif error:
            _TRANSLATION_DIAGNOSTICS["last_error"] = str(error)[:500]


def _google_http_translate(text, target_lang, source_lang="pt"):
    query = urlencode(
        {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
    )
    request = Request(
        f"https://translate.googleapis.com/translate_a/single?{query}",
        headers={"User-Agent": "Mozilla/5.0 EchoSiege/1.0"},
    )
    with urlopen(request, timeout=TRANSLATION_TIMEOUT) as response:
        payload = json.loads(response.read().decode("utf-8"))
    chunks = payload[0] if payload and isinstance(payload[0], list) else []
    translated = "".join(str(chunk[0]) for chunk in chunks if chunk and chunk[0])
    return translated.strip() or None


def _mymemory_http_translate(text, target_lang, source_lang="pt"):
    source = "pt-BR" if source_lang == "pt" else source_lang
    target = {"en": "en-US", "es": "es-ES"}.get(target_lang, target_lang)
    query = urlencode({"q": text, "langpair": f"{source}|{target}"})
    request = Request(
        f"https://api.mymemory.translated.net/get?{query}",
        headers={"User-Agent": "EchoSiege/1.0"},
    )
    with urlopen(request, timeout=TRANSLATION_TIMEOUT) as response:
        payload = json.loads(response.read().decode("utf-8"))
    translated = (payload.get("responseData") or {}).get("translatedText")
    return str(translated).strip() if translated else None


def _provider_translate(text, target_lang, source_lang="pt"):
    errors = []
    try:
        from deep_translator import GoogleTranslator

        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        if translated:
            _record_translation_result(provider="deep-translator")
            return translated
    except Exception as exc:
        errors.append(f"deep-translator: {exc}")

    try:
        from googletrans import Translator

        translator = Translator()
        result = translator.translate(text, src=source_lang, dest=target_lang)
        translated = getattr(result, "text", None)
        if translated:
            _record_translation_result(provider="googletrans")
            return translated
    except Exception as exc:
        errors.append(f"googletrans: {exc}")

    for provider_name, provider in (
        ("google-http", _google_http_translate),
        ("mymemory-http", _mymemory_http_translate),
    ):
        try:
            translated = provider(text, target_lang, source_lang)
            if translated:
                _record_translation_result(provider=provider_name)
                return translated
        except Exception as exc:
            errors.append(f"{provider_name}: {exc}")

    _record_translation_result(error=" | ".join(errors) or "Nenhum provedor respondeu.")
    return None


def command_aliases_for(value, target_lang):
    key = normalize_key(value)
    data = COMMAND_TRANSLATIONS.get(key) or {}
    return tuple(data.get(target_lang) or ())


def preferred_command_alias(value, target_lang):
    aliases = command_aliases_for(value, target_lang)
    return aliases[0] if aliases else str(value)


def _translate_command_snippet(piece, target_lang):
    if not (piece.startswith("`") and piece.endswith("`")):
        return piece
    body = piece[1:-1]
    if not re.match(r"^echo\s+", body, flags=re.IGNORECASE):
        return piece

    def replace_word(match):
        word = match.group(0)
        if normalize_key(word) == "echo":
            return word
        return preferred_command_alias(word, target_lang)

    localized = re.sub(r"[A-Za-zÀ-ÿ_]+", replace_word, body)
    return f"`{localized}`"


def _translate_uncached(text, target_lang, source_lang="pt"):
    pieces = BLOCK_RE.split(str(text))
    translated_pieces = []
    for piece in pieces:
        if not piece:
            continue
        if BLOCK_RE.fullmatch(piece) or not piece.strip():
            translated_pieces.append(_translate_command_snippet(piece, target_lang))
            continue
        leading = piece[: len(piece) - len(piece.lstrip())]
        trailing = piece[len(piece.rstrip()) :]
        core = piece.strip()
        translated = _provider_translate(core, target_lang, source_lang)
        translated_pieces.append(f"{leading}{translated}{trailing}" if translated else piece)
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
    entries = []
    if data.get("title"):
        entries.append((data, "title", data["title"], 256))
    if data.get("description"):
        entries.append((data, "description", data["description"], 4096))
    for field in data.get("fields", []):
        if field.get("name"):
            entries.append((field, "name", field["name"], 256))
        if field.get("value"):
            entries.append((field, "value", field["value"], 1024))
    if data.get("footer", {}).get("text"):
        entries.append((data["footer"], "text", data["footer"]["text"], 2048))
    if data.get("author", {}).get("name"):
        entries.append((data["author"], "name", data["author"]["name"], 256))

    translated_values = await asyncio.gather(
        *(translate_text(value, target_lang) for _, _, value, _ in entries)
    )
    for (container, key, _, limit), translated in zip(entries, translated_values):
        container[key] = _truncate(translated, limit)

    return embed.__class__.from_dict(_fit_embed_total(data))


async def translate_view(view, target_lang):
    if view is None or target_lang in {"auto", "pt"}:
        return view
    if getattr(view, "_echo_i18n_language", None) == target_lang:
        return view

    entries = []
    for child in getattr(view, "children", []):
        label = getattr(child, "label", None)
        if label:
            entries.append((child, "label", label, 80))
        placeholder = getattr(child, "placeholder", None)
        if placeholder:
            entries.append((child, "placeholder", placeholder, 150))
        for option in getattr(child, "options", []) or []:
            if getattr(option, "label", None):
                entries.append((option, "label", option.label, 100))
            if getattr(option, "description", None):
                entries.append((option, "description", option.description, 100))

    results = await asyncio.gather(
        *(translate_text(value, target_lang) for _, _, value, _ in entries),
        return_exceptions=True,
    )
    for (container, attribute, _, limit), translated in zip(entries, results):
        if isinstance(translated, Exception):
            continue
        try:
            setattr(container, attribute, _truncate(translated, limit))
        except Exception:
            pass
    try:
        view._echo_i18n_language = target_lang
    except Exception:
        pass
    return view


async def _localize_payload_for_language(language, content=None, kwargs=None):
    kwargs = dict(kwargs or {})
    if language in {"auto", "pt"}:
        return content, kwargs

    content_task = asyncio.create_task(translate_text(content, language)) if content is not None else None
    embed_task = asyncio.create_task(translate_embed(kwargs["embed"], language)) if kwargs.get("embed") is not None else None
    embeds_task = (
        asyncio.gather(*(translate_embed(embed, language) for embed in kwargs["embeds"]))
        if kwargs.get("embeds")
        else None
    )
    view_task = asyncio.create_task(translate_view(kwargs["view"], language)) if kwargs.get("view") is not None else None

    tasks = [task for task in (content_task, embed_task, embeds_task, view_task) if task is not None]
    if tasks:
        await asyncio.gather(*tasks)
    if content_task is not None:
        content = _truncate(content_task.result(), 2000)
    if embed_task is not None:
        kwargs["embed"] = embed_task.result()
    if embeds_task is not None:
        kwargs["embeds"] = list(embeds_task.result())
    if view_task is not None:
        kwargs["view"] = view_task.result()
    return content, kwargs


async def localize_send_payload(ctx_or_user, content=None, kwargs=None):
    kwargs = dict(kwargs or {})
    user = getattr(ctx_or_user, "author", ctx_or_user)
    guild = getattr(ctx_or_user, "guild", None)
    language = resolve_user_language(user=user, guild=guild)
    try:
        return await _localize_payload_for_language(language, content, kwargs)
    except Exception as exc:
        _record_translation_result(error=f"payload: {exc}")
        return content, kwargs


async def localize_interaction_payload(interaction, content=None, kwargs=None):
    language = resolve_user_language(
        user=getattr(interaction, "user", None),
        guild=getattr(interaction, "guild", None),
        explicit_locale=getattr(interaction, "locale", None),
    )
    try:
        return await _localize_payload_for_language(language, content, kwargs)
    except Exception as exc:
        _record_translation_result(error=f"interaction payload: {exc}")
        return content, dict(kwargs or {})


def canonical_command_token(value):
    key = normalize_key(value)
    if key in COMMAND_TRANSLATIONS:
        return key
    for canonical, languages in COMMAND_TRANSLATIONS.items():
        for aliases in languages.values():
            if key in {normalize_key(alias) for alias in aliases}:
                return canonical
    return str(value or "").strip().lower()


def register_multilingual_command_aliases(bot):
    registered = {"en": 0, "es": 0, "skipped": 0}
    for command in list(bot.walk_commands()):
        container = command.parent.all_commands if command.parent else bot.all_commands
        source_tokens = [command.name, *list(getattr(command, "aliases", []) or [])]
        for language in ("en", "es"):
            candidates = []
            for source in source_tokens:
                candidates.extend(command_aliases_for(source, language))
            for alias in dict.fromkeys(candidates):
                alias = str(alias).strip().lower()
                if not alias or " " in alias or alias == command.name:
                    continue
                existing = container.get(alias)
                if existing is not None and existing is not command:
                    registered["skipped"] += 1
                    continue
                if existing is command:
                    continue
                container[alias] = command
                if alias not in command.aliases:
                    command.aliases.append(alias)
                registered[language] += 1
    return registered


_INTERACTION_HOOKS_INSTALLED = False


def install_discord_i18n_hooks():
    global _INTERACTION_HOOKS_INSTALLED
    if _INTERACTION_HOOKS_INSTALLED:
        return

    import discord

    response_cls = discord.InteractionResponse
    original_send = response_cls.send_message
    original_edit = response_cls.edit_message

    async def localize_call(response, args, kwargs):
        interaction = getattr(response, "_parent", None)
        if interaction is None:
            return args, kwargs
        args = list(args)
        had_content = bool(args) or "content" in kwargs
        content = args[0] if args else kwargs.pop("content", None)
        content, kwargs = await localize_interaction_payload(interaction, content, kwargs)
        if args:
            args[0] = content
        elif had_content:
            kwargs["content"] = content
        return tuple(args), kwargs

    async def send_message(response, *args, **kwargs):
        args, kwargs = await localize_call(response, args, kwargs)
        return await original_send(response, *args, **kwargs)

    async def edit_message(response, *args, **kwargs):
        args, kwargs = await localize_call(response, args, kwargs)
        return await original_edit(response, *args, **kwargs)

    response_cls.send_message = send_message
    response_cls.edit_message = edit_message
    _INTERACTION_HOOKS_INSTALLED = True


def translation_backend_status():
    with _DIAGNOSTICS_LOCK:
        provider = _TRANSLATION_DIAGNOSTICS.get("provider")
        error = _TRANSLATION_DIAGNOSTICS.get("last_error")
    if provider:
        return provider
    if error:
        return f"indisponível ({error[:120]})"
    return "google-http / mymemory-http (aguardando primeiro uso)"


def translation_diagnostics():
    with _DIAGNOSTICS_LOCK:
        return dict(_TRANSLATION_DIAGNOSTICS)
