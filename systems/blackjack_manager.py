import json
import random


CARD_RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["♠", "♥", "♦", "♣"]


def card_rank(card):
    text = str(card or "").strip()
    if text in CARD_RANKS:
        return text
    if text and text[-1] in CARD_SUITS:
        return text[:-1]
    if len(text) > 1 and text[:-1] in CARD_RANKS:
        return text[:-1]
    if text.startswith("10"):
        return "10"
    if text[:1] in {"A", "J", "Q", "K"}:
        return text[:1]
    if text[:1].isdigit():
        return text[:1]
    return text


def draw_card(rng=None):
    rng = rng or random
    return f"{rng.choice(CARD_RANKS)}{rng.choice(CARD_SUITS)}"


def draw_hand(size=2, rng=None):
    return [draw_card(rng) for _ in range(size)]


def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        rank = card_rank(card)
        if rank == "A":
            aces += 1
            total += 11
        elif rank in {"J", "Q", "K"}:
            total += 10
        else:
            total += int(rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21


def serialize_hand(hand):
    return json.dumps(list(hand), ensure_ascii=False)


def deserialize_hand(raw):
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return [str(card) for card in data]


def format_hand(hand, hide_first=False):
    visible = ["??" if hide_first and index == 0 else card for index, card in enumerate(hand)]
    suffix = "?" if hide_first else str(hand_value(hand))
    return f"{' | '.join(visible)} ({suffix})"


def _card_lines(card, hidden=False):
    if hidden:
        return [
            "┌─────┐",
            "│░░░░░│",
            "│░ ? ░│",
            "│░░░░░│",
            "└─────┘",
        ]
    text = str(card or "?")
    suit = text[-1] if text and text[-1] in CARD_SUITS else " "
    rank = card_rank(text) or "?"
    left = rank[:2].ljust(2)
    right = rank[:2].rjust(2)
    return [
        "┌─────┐",
        f"│{left}   │",
        f"│  {suit}  │",
        f"│   {right}│",
        "└─────┘",
    ]


def format_hand_visual(hand, hide_first=False):
    hand = list(hand or [])
    if not hand:
        return "Sem cartas."
    rows = [""] * 5
    for index, card in enumerate(hand):
        lines = _card_lines(card, hidden=hide_first and index == 0)
        for row_index, line in enumerate(lines):
            rows[row_index] += ("" if not rows[row_index] else " ") + line
    value = "?" if hide_first else str(hand_value(hand))
    return "\n".join(rows + [f"Valor: {value}"])


def dealer_play(dealer_hand, rng=None):
    dealer_hand = list(dealer_hand)
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(draw_card(rng))
    return dealer_hand
