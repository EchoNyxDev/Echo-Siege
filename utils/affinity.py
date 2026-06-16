from collections import Counter

try:
    from data.heroes import normalize_origin
except Exception:
    def normalize_origin(origin):
        return str(origin or "").strip()


GROUP_AFFINITY_SKILL_ID = "ressonancia_de_obra"


def _bonus_por_quantidade(qtd):
    if qtd >= 5:
        return 0.20
    if qtd >= 4:
        return 0.15
    if qtd >= 3:
        return 0.10
    if qtd >= 2:
        return 0.05
    return 0.0


def apply_affinity_bonus(party_data, heroes):
    origens = []
    for member in party_data:
        hero_id = member.get("hero_id")
        origem = normalize_origin(heroes.get(hero_id, {}).get("origem"))
        if origem:
            origens.append(origem)

    contagem = Counter(origens)
    for index, member in enumerate(party_data):
        hero_id = member.get("hero_id")
        origem = normalize_origin(heroes.get(hero_id, {}).get("origem"))
        quantidade = contagem.get(origem, 0)
        bonus = _bonus_por_quantidade(contagem.get(origem, 0))
        member["affinity_bonus"] = bonus
        member["affinity_origin"] = origem
        member["affinity_count"] = quantidade
        member["affinity_group_skill"] = quantidade >= 5
        if bonus <= 0:
            continue

        for container in [member, member.get("stats", {})]:
            for stat in ["hp", "atk", "matk", "def"]:
                if stat in container:
                    container[stat] = int(container[stat] * (1 + bonus))

        if quantidade >= 5 and index == 0:
            habilidades = member.setdefault("habilidades", [])
            if GROUP_AFFINITY_SKILL_ID not in habilidades:
                habilidades.append(GROUP_AFFINITY_SKILL_ID)

    return party_data
