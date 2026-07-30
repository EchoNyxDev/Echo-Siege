import random
from collections import Counter


SLOT_SYMBOLS = ["CEREJA", "LIMAO", "SINO", "ESTRELA", "DIAMANTE", "COROA"]
SLOT_WEIGHTS = [35, 25, 18, 12, 7, 3]
SLOT_PAYOUTS = {
    "CEREJA": 2,
    "LIMAO": 3,
    "SINO": 5,
    "ESTRELA": 10,
    "DIAMANTE": 25,
    "COROA": 100,
}


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
            "details": f"{' - '.join(reels)} | Jackpot + 100x",
        }

    if len(counts) == 1:
        symbol = reels[0]
        multiplier = SLOT_PAYOUTS[symbol]
        return {
            "reels": reels,
            "payout": int(bet * multiplier),
            "result": "win",
            "jackpot_win": False,
            "details": f"{' - '.join(reels)} | {multiplier}x",
        }

    if max(counts.values()) == 2:
        return {
            "reels": reels,
            "payout": max(1, int(bet * 0.5)),
            "result": "partial",
            "jackpot_win": False,
            "details": f"{' - '.join(reels)} | reembolso parcial",
        }

    return {
        "reels": reels,
        "payout": 0,
        "result": "loss",
        "jackpot_win": False,
        "details": f"{' - '.join(reels)} | sem combinação",
    }
