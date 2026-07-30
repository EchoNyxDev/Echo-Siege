SESSION_MODES = {
    "diaria": {
        "label": "Leitura Diária",
        "questions": 10,
        "duration": 20 * 60,
        "max_errors": 99,
        "daily": True,
        "description": "Um pacote diário de enigmas, fichas e perguntas do arquivo.",
    },
    "explorar": {
        "label": "Exploração",
        "questions": 8,
        "duration": 15 * 60,
        "max_errors": 99,
        "daily": False,
        "description": "Sessão curta para farmar Páginas Perdidas e testar memória.",
    },
    "expedicao": {
        "label": "Expedição do Arquivo",
        "questions": 15,
        "duration": 30 * 60,
        "max_errors": 3,
        "daily": False,
        "description": "Sequência longa. Três erros encerram a expedição.",
    },
}

MODE_ALIASES = {
    "daily": "diaria",
    "diária": "diaria",
    "dia": "diaria",
    "explore": "explorar",
    "exploração": "explorar",
    "exploracao": "explorar",
    "expedition": "expedicao",
    "expedição": "expedicao",
}


def normalize_mode(mode):
    mode = str(mode or "explorar").strip().lower()
    return MODE_ALIASES.get(mode, mode if mode in SESSION_MODES else "explorar")
