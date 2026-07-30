import json
import random


CARD_RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def draw_card(rng=None):
    rng = rng or random
    return rng.choice(CARD_RANKS)


def draw_hand(size=2, rng=None):
    return [draw_card(rng) for _ in range(size)]


def hand_value(hand):
    total = 0
    aces = 0
    for card in hand:
        if card == "A":
            aces += 1
            total += 11
        elif card in {"J", "Q", "K"}:
            total += 10
        else:
            total += int(card)
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


def dealer_play(dealer_hand, rng=None):
    dealer_hand = list(dealer_hand)
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(draw_card(rng))
    return dealer_hand
