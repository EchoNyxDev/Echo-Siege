import random

from data.nix_dialogues import NIX_RANDOM_LINES
from systems.nix_manager import add_fragments, current_mission, ensure_player_progress, is_event_active, log_event, now_ts


ACTIVITY_FRAGMENT_RULES = {
    "hunt": {"chance": 0.10, "min": 1, "max": 2},
    "adventure": {"chance": 0.15, "min": 2, "max": 3},
    "dungeon": {"chance": 1.00, "min": 5, "max": 7},
    "biblioteca_correct": {"chance": 0.35, "min": 1, "max": 1},
    "biblioteca_finish": {"chance": 1.00, "min": 2, "max": 4},
    "work": {"chance": 0.18, "min": 1, "max": 2},
    "cassino": {"chance": 0.05, "min": 1, "max": 2},
}


def award_activity_fragments(cursor, user_id, activity, difficulty=1, force=False):
    """Entrega fragmentos pequenos durante o evento sem bloquear o fluxo principal."""
    if not is_event_active(cursor):
        return {"amount": 0, "line": ""}

    rule = ACTIVITY_FRAGMENT_RULES.get(str(activity))
    if not rule:
        return {"amount": 0, "line": ""}

    chance = float(rule["chance"])
    if not force and random.random() > chance:
        return {"amount": 0, "line": ""}

    difficulty_bonus = max(0, min(3, int(difficulty or 1) // 12))
    amount = random.randint(int(rule["min"]), int(rule["max"])) + difficulty_bonus
    total = add_fragments(cursor, user_id, amount, activity)

    progress = ensure_player_progress(cursor, user_id)
    mission_id, mission = current_mission(progress)
    if mission:
        kind = mission.get("kind")
        if kind == "dungeon" and activity == "dungeon":
            cursor.execute(
                "UPDATE nix_event_progress SET mission_progress = 1, updated_at = ? WHERE user_id = ?",
                (now_ts(), str(user_id)),
            )
        elif kind == "fragmentos":
            cursor.execute(
                "UPDATE nix_event_progress SET updated_at = ? WHERE user_id = ?",
                (now_ts(), str(user_id)),
            )

    line = f"{random.choice(NIX_RANDOM_LINES)}\nFragmentos de Dados: **+{amount}** (saldo: **{total}**)."
    log_event(cursor, user_id, "activity_fragments", f"{activity}:{amount}")
    return {"amount": amount, "line": line}
