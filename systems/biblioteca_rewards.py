QUESTION_POINTS = {
    1: 2,
    2: 4,
    3: 7,
    4: 11,
    5: 18,
}

MODE_COMPLETION_REWARDS = {
    "diaria": {"paginas": 18, "gold": 550, "xp": 35, "items": {}},
    "explorar": {"paginas": 10, "gold": 320, "xp": 22, "items": {}},
    "expedicao": {"paginas": 35, "gold": 900, "xp": 60, "items": {"fragmento_biblioteca": 1}},
}


def question_points(difficulty, used_hint=False, combo=0):
    base = QUESTION_POINTS.get(max(1, min(5, int(difficulty or 1))), 2)
    if used_hint:
        base = max(1, int(base * 0.5))
    if combo >= 10:
        base = int(base * 1.75)
    elif combo >= 8:
        base = int(base * 1.5)
    elif combo >= 5:
        base = int(base * 1.25)
    elif combo >= 3:
        base = int(base * 1.1)
    return max(1, base)


def completion_reward(mode, acertos, erros, total, perfect=False, no_hint=False):
    reward = dict(MODE_COMPLETION_REWARDS.get(mode, MODE_COMPLETION_REWARDS["explorar"]))
    reward["items"] = dict(reward.get("items", {}))
    total = max(1, int(total or 1))
    accuracy = acertos / total
    reward["paginas"] = int(reward.get("paginas", 0) * max(0.35, accuracy))
    reward["gold"] = int(reward.get("gold", 0) * max(0.4, accuracy))
    reward["xp"] = int(reward.get("xp", 0) * max(0.4, accuracy))

    if perfect:
        reward["paginas"] += 20 if mode == "diaria" else 12
        reward["gold"] += 600
        reward["items"]["selo_resposta_perfeita"] = reward["items"].get("selo_resposta_perfeita", 0) + 1
    if no_hint and acertos >= max(5, total // 2):
        reward["paginas"] += 8
    if erros >= 3 and mode == "expedicao":
        reward["paginas"] = max(5, int(reward["paginas"] * 0.65))
    return reward


def reward_to_text(reward):
    parts = []
    if reward.get("paginas"):
        parts.append(f"{reward['paginas']:,} Páginas Perdidas")
    if reward.get("gold"):
        parts.append(f"{reward['gold']:,} Gold")
    if reward.get("gems"):
        parts.append(f"{reward['gems']:,} Gems")
    if reward.get("xp"):
        parts.append(f"{reward['xp']:,} XP de conta")
    if reward.get("tickets"):
        parts.append(f"{reward['tickets']} Ticket(s)")
    for item, qty in reward.get("items", {}).items():
        parts.append(f"{qty}x {item.replace('_', ' ').title()}")
    return ", ".join(parts) if parts else "Sem recompensa extra"
