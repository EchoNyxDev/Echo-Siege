import random
from collections import Counter


SLOT_SYMBOLS = ["CEREJA", "LIMAO", "SINO", "ESTRELA", "DIAMANTE", "COROA"]
SLOT_EMOJIS = {
    "CEREJA": "🍒",
    "LIMAO": "🍋",
    "SINO": "🔔",
    "ESTRELA": "⭐",
    "DIAMANTE": "💎",
    "COROA": "👑",
}
SLOT_LABELS = {
    "CEREJA": "Cereja",
    "LIMAO": "Limão",
    "SINO": "Sino",
    "ESTRELA": "Estrela",
    "DIAMANTE": "Diamante",
    "COROA": "Coroa",
}
SLOT_WEIGHTS = [28, 24, 20, 16, 9, 3]
SLOT_PAYOUTS = {
    "CEREJA": 4,
    "LIMAO": 5,
    "SINO": 8,
    "ESTRELA": 14,
    "DIAMANTE": 35,
    "COROA": 150,
}
SLOT_PAIR_PAYOUTS = {
    "CEREJA": 1.0,
    "LIMAO": 1.1,
    "SINO": 1.2,
    "ESTRELA": 1.4,
    "DIAMANTE": 1.8,
    "COROA": 3.0,
}


def slot_symbol_text(symbol):
    return f"{SLOT_EMOJIS.get(symbol, '❔')} {SLOT_LABELS.get(symbol, symbol.title())}"


def format_slot_reels(reels):
    faces = [SLOT_EMOJIS.get(symbol, "❔") for symbol in reels]
    return (
        "╔════════════════╗\n"
        f"║  {faces[0]}  │  {faces[1]}  │  {faces[2]}  ║\n"
        "╚════════════════╝"
    )


def slot_paytable_lines():
    lines = [
        "Duas figuras iguais pagam de 1x a 3x, conforme a figura.",
        "Três figuras iguais pagam:",
    ]
    for symbol in SLOT_SYMBOLS:
        lines.append(f"{SLOT_EMOJIS[symbol]} {SLOT_LABELS[symbol]}: {SLOT_PAYOUTS[symbol]}x")
    return lines


def spin_slots(bet, jackpot=0, rng=None):
    rng = rng or random
    reels = rng.choices(SLOT_SYMBOLS, weights=SLOT_WEIGHTS, k=3)
    counts = Counter(reels)
    jackpot_win = reels == ["COROA", "COROA", "COROA"]

    if jackpot_win:
        payout = int(bet * SLOT_PAYOUTS["COROA"] + jackpot)
        return {
            "reels": reels,
            "payout": payout,
            "result": "jackpot",
            "jackpot_win": True,
            "details": "Três 👑 Coroas | Jackpot + 150x",
        }

    if len(counts) == 1:
        symbol = reels[0]
        multiplier = SLOT_PAYOUTS[symbol]
        return {
            "reels": reels,
            "payout": int(bet * multiplier),
            "result": "win",
            "jackpot_win": False,
            "details": f"{slot_symbol_text(symbol)} triplo | {multiplier}x",
        }

    if max(counts.values()) == 2:
        pair_symbol = next(symbol for symbol, amount in counts.items() if amount == 2)
        multiplier = SLOT_PAIR_PAYOUTS.get(pair_symbol, 1.0)
        return {
            "reels": reels,
            "payout": max(1, int(round(bet * multiplier))),
            "result": "partial",
            "jackpot_win": False,
            "details": f"Par de {slot_symbol_text(pair_symbol)} | {multiplier:g}x",
        }

    return {
        "reels": reels,
        "payout": 0,
        "result": "loss",
        "jackpot_win": False,
        "details": "Sem combinação premiada",
    }
