import copy
import json
import random
import unicodedata
from pathlib import Path

from data.enemies import ENEMIES
from data.missions import MISSIONS


CATALOG_VERSION = 2

TIER_INFO = {
    1: {"nome": "Comum", "nivel_min": 1, "nivel_max": 12, "gold": 420, "xp": 280},
    2: {"nome": "Rara", "nivel_min": 8, "nivel_max": 25, "gold": 900, "xp": 650},
    3: {"nome": "Épica", "nivel_min": 20, "nivel_max": 40, "gold": 1900, "xp": 1400},
    4: {"nome": "Lendária", "nivel_min": 35, "nivel_max": None, "gold": 4200, "xp": 3200},
}


def _without_accents(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _reward_nodes(adventure):
    return [
        node
        for node in adventure.get("nodos", {}).values()
        if node.get("tipo") == "recompensa"
    ]


def _combat_nodes(adventure):
    return [
        node
        for node in adventure.get("nodos", {}).values()
        if node.get("tipo") == "combate"
    ]


def _enemy_threat(enemy_id):
    enemy = ENEMIES.get(enemy_id, {})
    return (
        float(enemy.get("hp", 200) or 200) / 10
        + float(enemy.get("atk", 30) or 0) * 2
        + float(enemy.get("matk", 0) or 0) * 2
        + float(enemy.get("def", 10) or 0)
    )


def infer_adventure_tier(adventure):
    rewards = _reward_nodes(adventure)
    max_gold = max((int(node.get("gold", 0) or 0) for node in rewards), default=0)
    max_xp = max((int(node.get("xp", 0) or 0) for node in rewards), default=0)

    if max_gold <= 1200 and max_xp <= 1000:
        reward_tier = 1
    elif max_gold <= 3200 and max_xp <= 2500:
        reward_tier = 2
    elif max_gold <= 6500 and max_xp <= 5000:
        reward_tier = 3
    else:
        reward_tier = 4

    max_threat = max(
        (
            sum(_enemy_threat(enemy_id) for enemy_id in node.get("inimigos", []))
            for node in _combat_nodes(adventure)
        ),
        default=0,
    )
    if max_threat <= 1000:
        threat_tier = 1
    elif max_threat <= 2800:
        threat_tier = 2
    elif max_threat <= 6500:
        threat_tier = 3
    else:
        threat_tier = 4

    return max(reward_tier, threat_tier)


def _round_reward(value):
    value = max(1, int(round(value)))
    return max(5, int(round(value / 5.0) * 5))


def _normalize_rewards(adventure, tier):
    rewards = _reward_nodes(adventure)
    if not rewards:
        return adventure

    max_gold = max((int(node.get("gold", 0) or 0) for node in rewards), default=0)
    max_xp = max((int(node.get("xp", 0) or 0) for node in rewards), default=0)
    combat_bonus = 1.0 + min(0.25, len(_combat_nodes(adventure)) * 0.06)
    tier_data = TIER_INFO[tier]

    for node in rewards:
        raw_gold = int(node.get("gold", 0) or 0)
        raw_xp = int(node.get("xp", 0) or 0)

        if raw_gold > 0:
            path_ratio = 0.55 + 0.45 * (raw_gold / max(1, max_gold))
            node["gold"] = _round_reward(tier_data["gold"] * combat_bonus * path_ratio)
        if raw_xp > 0:
            path_ratio = 0.55 + 0.45 * (raw_xp / max(1, max_xp))
            node["xp"] = _round_reward(tier_data["xp"] * combat_bonus * path_ratio)

    return adventure


def _mission_tier(mission):
    rarity = _without_accents(mission.get("raridade"))
    return {
        "comum": 1,
        "rara": 2,
        "epica": 3,
        "lendaria": 4,
    }.get(rarity, 1)


def _convert_mission(mission_id, mission):
    event = mission.get("evento", {})
    options = []
    nodes = {}
    base_reward = mission.get("recompensa", {})

    for option_key, option in event.get("opcoes", {}).items():
        outcome_id = f"resultado_{option_key.lower()}"
        success = bool(option.get("sucesso"))
        multiplier = max(0.0, float(option.get("loot_mult", 1.0) or 0.0)) if success else 0.0
        options.append(
            {
                "label": option.get("label", f"Opção {option_key}"),
                "emoji": "🎲",
                "next": outcome_id,
            }
        )
        nodes[outcome_id] = {
            "tipo": "recompensa",
            "texto": option.get("texto", "O contrato chegou ao fim."),
            "gold": int((base_reward.get("gold", 0) or 0) * multiplier),
            "xp": int((base_reward.get("xp", 0) or 0) * multiplier),
        }

    nodes["start"] = {
        "tipo": "historia",
        "texto": f"{mission.get('desc', '')}\n\n{event.get('texto', '')}".strip(),
        "opcoes": options,
    }
    return {
        "nome": mission.get("nome", mission_id),
        "nodos": nodes,
        "_meta": {
            "source": "missions",
            "source_id": mission_id,
            "tier": _mission_tier(mission),
        },
    }


def _attach_metadata(adventure_id, adventure, source, tier):
    tier_data = TIER_INFO[tier]
    rewards = _reward_nodes(adventure)
    adventure["_meta"] = {
        **adventure.get("_meta", {}),
        "source": source,
        "source_id": adventure.get("_meta", {}).get("source_id", adventure_id),
        "tier": tier,
        "tier_name": tier_data["nome"],
        "level_min": tier_data["nivel_min"],
        "level_max": tier_data["nivel_max"],
        "max_gold": max((int(node.get("gold", 0) or 0) for node in rewards), default=0),
        "max_xp": max((int(node.get("xp", 0) or 0) for node in rewards), default=0),
        "combat_count": len(_combat_nodes(adventure)),
    }
    return adventure


def load_adventure_catalog(adventures_path=None):
    path = Path(adventures_path) if adventures_path else Path(__file__).resolve().parents[1] / "data" / "adventures.json"
    try:
        raw_adventures = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        raw_adventures = {}

    catalog = {}
    for adventure_id, raw_adventure in raw_adventures.items():
        adventure = copy.deepcopy(raw_adventure)
        tier = infer_adventure_tier(adventure)
        _normalize_rewards(adventure, tier)
        catalog[adventure_id] = _attach_metadata(adventure_id, adventure, "adventures", tier)

    for mission_id, raw_mission in MISSIONS.items():
        catalog_id = f"mission_{mission_id}"
        mission = _convert_mission(mission_id, copy.deepcopy(raw_mission))
        tier = mission["_meta"]["tier"]
        _normalize_rewards(mission, tier)
        catalog[catalog_id] = _attach_metadata(catalog_id, mission, "missions", tier)

    return catalog


def player_target_tier(player_level):
    level = max(1, int(player_level or 1))
    if level <= 7:
        return 1
    if level <= 19:
        return 2
    if level <= 34:
        return 3
    return 4


def _weighted_choice(candidates, target_tier, rng):
    weights = []
    for _, adventure in candidates:
        tier = adventure.get("_meta", {}).get("tier", 1)
        weights.append(5 if tier == target_tier else 2)
    return rng.choices(candidates, weights=weights, k=1)[0]


def select_daily_contracts(catalog, player_level, previous_ids=None, count=3, rng=None):
    if count <= 0:
        return []

    rng = rng or random.SystemRandom()
    target_tier = player_target_tier(player_level)
    minimum_tier = max(1, target_tier - 1)
    candidates = [
        (adventure_id, adventure)
        for adventure_id, adventure in catalog.items()
        if minimum_tier <= adventure.get("_meta", {}).get("tier", 1) <= target_tier
    ]

    previous = set(previous_ids or [])
    fresh = [entry for entry in candidates if entry[0] not in previous]
    if len(fresh) >= count:
        candidates = fresh
    if len(candidates) < count:
        candidates = list(catalog.items())

    selected = []
    available = list(candidates)
    sources = {
        adventure.get("_meta", {}).get("source")
        for _, adventure in available
    }

    for source in sorted(source for source in sources if source):
        if len(selected) >= count:
            break
        source_pool = [
            entry
            for entry in available
            if entry[1].get("_meta", {}).get("source") == source
        ]
        if source_pool:
            chosen = _weighted_choice(source_pool, target_tier, rng)
            selected.append(chosen[0])
            available.remove(chosen)

    while available and len(selected) < count:
        chosen = _weighted_choice(available, target_tier, rng)
        selected.append(chosen[0])
        available.remove(chosen)

    return selected
