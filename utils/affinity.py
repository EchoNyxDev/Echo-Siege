from collections import Counter


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
        origem = heroes.get(hero_id, {}).get("origem")
        if origem:
            origens.append(origem)

    contagem = Counter(origens)
    for member in party_data:
        hero_id = member.get("hero_id")
        origem = heroes.get(hero_id, {}).get("origem")
        bonus = _bonus_por_quantidade(contagem.get(origem, 0))
        member["affinity_bonus"] = bonus
        member["affinity_origin"] = origem
        if bonus <= 0:
            continue

        for container in [member, member.get("stats", {})]:
            for stat in ["hp", "atk", "matk", "def"]:
                if stat in container:
                    container[stat] = int(container[stat] * (1 + bonus))

    return party_data
