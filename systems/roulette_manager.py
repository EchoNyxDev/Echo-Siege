import random
import unicodedata


RED_NUMBERS = {
    1, 3, 5, 7, 9, 12, 14, 16, 18,
    19, 21, 23, 25, 27, 30, 32, 34, 36,
}


def normalize_bet_type(value):
    text = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    aliases = {
        "red": "vermelho",
        "black": "preto",
        "even": "par",
        "odd": "impar",
        "baixo": "baixo",
        "low": "baixo",
        "alto": "alto",
        "high": "alto",
        "numero": "numero",
        "number": "numero",
        "n": "numero",
    }
    return aliases.get(text, text)


def number_color(number):
    if number == 0:
        return "verde"
    return "vermelho" if number in RED_NUMBERS else "preto"


def spin_roulette(bet_type, bet, chosen_number=None, rng=None):
    rng = rng or random
    bet_type = normalize_bet_type(bet_type)
    number = rng.randint(0, 36)
    color = number_color(number)

    won = False
    multiplier = 0

    if bet_type in {"vermelho", "preto"}:
        won = color == bet_type
        multiplier = 2
    elif bet_type == "par":
        won = number != 0 and number % 2 == 0
        multiplier = 2
    elif bet_type == "impar":
        won = number % 2 == 1
        multiplier = 2
    elif bet_type == "baixo":
        won = 1 <= number <= 18
        multiplier = 2
    elif bet_type == "alto":
        won = 19 <= number <= 36
        multiplier = 2
    elif bet_type == "numero":
        if chosen_number is None:
            raise ValueError("Aposta em número exige um número de 0 a 36.")
        chosen_number = int(chosen_number)
        if not 0 <= chosen_number <= 36:
            raise ValueError("O número da roleta precisa estar entre 0 e 36.")
        won = number == chosen_number
        multiplier = 36
    else:
        raise ValueError("Tipo de aposta inválido. Use vermelho, preto, par, impar, baixo, alto ou numero.")

    return {
        "number": number,
        "color": color,
        "won": won,
        "payout": int(bet * multiplier) if won else 0,
        "result": "win" if won else "loss",
        "details": f"Roleta caiu em {number} ({color}). Aposta: {bet_type}{' ' + str(chosen_number) if bet_type == 'numero' else ''}.",
    }
