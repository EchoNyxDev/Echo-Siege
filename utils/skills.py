import re
import unicodedata

try:
    from data.habilidades import SKILLS
except Exception:
    SKILLS = {}

try:
    from data.habmonsters import MONSTER_SKILLS
    SKILLS.update(MONSTER_SKILLS)
except Exception:
    pass


MANUAL_SKILL_ALIASES = {
    "8_portoes": "oito_portoes",
    "ataque_giratorio": "ataque_giratorio",
    "bebado_de_oito_trigramas": "bebado_oito_trigramas",
    "cura": "cura_chopper",
    "cura_maxima": "cura_maxima",
    "encarnacao_do_fogo_do_inferno": "encarnacao_fogo",
    "lotus_de_laminas_chama_explosiva": "lotus_chama_explosiva",
    "privilegios_de_administrador": "privilegios_adm",
    "regeneracao": "regeneracao_koku",
    "tecnica_da_palma_mistica": "palma_mistica",
}


def normalizar_id(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def _montar_indice():
    indice = {}
    for skill_id, skill_data in SKILLS.items():
        indice[normalizar_id(skill_id)] = skill_id
        indice[normalizar_id(skill_data.get("nome", skill_id))] = skill_id
    indice.update(MANUAL_SKILL_ALIASES)
    return indice


SKILL_NAME_TO_ID = _montar_indice()


def _registrar_fallback_skill(candidato, habilidade):
    if not isinstance(habilidade, dict):
        return None

    skill_id = normalizar_id(candidato)
    if not skill_id:
        return None

    if skill_id in SKILLS:
        return skill_id

    texto = normalizar_id(f"{habilidade.get('nome', '')} {habilidade.get('descricao', '')}")
    alvo = "unico_inimigo"
    tipo = "dano"
    efeito = {"multiplicador_atk": 1.2}

    if "todos" in texto or "area" in texto or "campo" in texto:
        alvo = "todos_inimigos"
    if "matk" in texto or "mag" in texto or "mana" in texto or "fogo" in texto:
        efeito = {"multiplicador_matk": 1.2}
    if "duas" in texto or "2" in texto:
        efeito["multiplicador_hit"] = 2
    if "tres" in texto or "3" in texto:
        efeito["multiplicador_hit"] = 3
    if "nove" in texto or "9" in texto:
        efeito["multiplicador_hit"] = 9
    if "cura" in texto or "curando" in texto:
        tipo = "cura"
        alvo = "todos_aliados" if ("todos" in texto or "equipe" in texto or "party" in texto) else "aliado_menor_hp"
        efeito = {"cura_percent_max": 0.20}
    if "reviv" in texto or "ressuscit" in texto:
        tipo = "reviver"
        alvo = "aliado_morto"
        efeito = {"hp_percent": 0.50}
    if "aumenta" in texto or "aumentando" in texto or "buff" in texto or "fortalece" in texto:
        tipo = "buff"
        alvo = "self"
        efeito = {}
        if "atk" in texto:
            efeito["buff_atk"] = 20
        if "matk" in texto or "mag" in texto:
            efeito["buff_matk"] = 20
        if "def" in texto or "defesa" in texto:
            efeito["buff_def"] = 20
        if "spd" in texto or "veloc" in texto:
            efeito["buff_spd"] = 20
        if not efeito:
            efeito = {"buff_geral": 10}
    if "stun" in texto or "atordo" in texto or "paralis" in texto:
        tipo = "debuff"
        alvo = "unico_inimigo"
        efeito = {"stun_turnos": 1}
    if "provoca" in texto or "aggro" in texto:
        tipo = "buff"
        alvo = "self"
        efeito = {"aggro_max": True, "turnos": 2}

    SKILLS[skill_id] = {
        "nome": habilidade.get("nome", candidato),
        "tipo": tipo,
        "alvo": alvo,
        "efeito": efeito,
        "fallback": True,
    }
    SKILL_NAME_TO_ID[skill_id] = skill_id
    SKILL_NAME_TO_ID[normalizar_id(habilidade.get("nome", candidato))] = skill_id
    return skill_id


def resolve_skill_id(habilidade):
    if isinstance(habilidade, dict):
        candidato = habilidade.get("id") or habilidade.get("skill_id") or habilidade.get("nome")
    else:
        candidato = habilidade

    if not candidato:
        return None

    candidato_id = normalizar_id(candidato)
    skill_id = SKILL_NAME_TO_ID.get(candidato_id, candidato_id if candidato_id in SKILLS else None)
    if skill_id:
        return skill_id
    return _registrar_fallback_skill(candidato, habilidade)


def resolve_skill_list(habilidades):
    resolvidas = []
    for habilidade in habilidades or []:
        skill_id = resolve_skill_id(habilidade)
        if skill_id and skill_id not in resolvidas:
            resolvidas.append(skill_id)
    return resolvidas


def get_hero_skill_ids(hero_data, stars=1, rarity=None):
    habilidades = []
    base = hero_data.get("habilidade") if hero_data else None
    if base:
        habilidades.append(base)

    rarity = hero_data.get("raridade", 0) if rarity is None and hero_data else rarity
    try:
        total_stars = int(rarity or 0) + int(stars or 1) - 1
    except (TypeError, ValueError):
        total_stars = int(rarity or 0)

    for required_stars, skill in (hero_data.get("evolucoes", {}) if hero_data else {}).items():
        try:
            required_stars = int(required_stars)
        except (TypeError, ValueError):
            continue
        if total_stars >= required_stars:
            habilidades.append(skill)

    return resolve_skill_list(habilidades)


def get_hero_skill_descriptions(hero_data, stars=1, rarity=None):
    if not hero_data:
        return []

    descricoes = []
    base = hero_data.get("habilidade")
    if base:
        skill_id = resolve_skill_id(base)
        descricoes.append({
            "tipo": "Base",
            "nome": base.get("nome", skill_id or "Habilidade") if isinstance(base, dict) else str(base),
            "descricao": base.get("descricao", "") if isinstance(base, dict) else "",
            "combat_id": skill_id,
            "ativa": True,
        })

    rarity = hero_data.get("raridade", 0) if rarity is None else rarity
    try:
        total_stars = int(rarity or 0) + int(stars or 1) - 1
    except (TypeError, ValueError):
        total_stars = int(rarity or 0)

    for required_stars, skill in (hero_data.get("evolucoes", {}) or {}).items():
        try:
            required_stars_int = int(required_stars)
        except (TypeError, ValueError):
            continue

        ativa = total_stars >= required_stars_int
        skill_id = resolve_skill_id(skill)
        descricoes.append({
            "tipo": f"{required_stars_int} estrelas",
            "nome": skill.get("nome", skill_id or "Despertar") if isinstance(skill, dict) else str(skill),
            "descricao": skill.get("descricao", "") if isinstance(skill, dict) else "",
            "combat_id": skill_id,
            "ativa": ativa,
        })

    return descricoes
