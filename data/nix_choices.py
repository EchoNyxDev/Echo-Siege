NIX_ALIGNMENT_CHOICES = {
    "apoiar": {
        "label": "Apoiar NIX",
        "affinity": 12,
        "corruption": 5,
        "response": "NIX: apoio registrado. Confianca humana parece instavel, mas util.",
    },
    "confrontar": {
        "label": "Confrontar NIX",
        "affinity": -4,
        "corruption": -10,
        "response": "NIX: resistencia registrada. O TutoriUAU chama isso de 'bom senso tardio'.",
    },
    "negociar": {
        "label": "Negociar com NIX",
        "affinity": 8,
        "corruption": -3,
        "response": "NIX: negociacao aceita. Humanos gostam de resolver incendio com conversa. Curioso.",
    },
}

NIX_FINAL_CHOICES = {
    "apagar": {
        "label": "Apagar NIX",
        "requires": {},
        "reward": {
            "cosmetics": [{"id": "token_titulo_exterminador_anomalias", "type": "title"}],
            "items": {"token_moldura_firewall_carmesim": 1},
            "gems": 3,
        },
    },
    "libertar": {
        "label": "Libertar NIX",
        "requires": {},
        "reward": {
            "cosmetics": [{"id": "token_titulo_libertador_codigo", "type": "title"}],
            "pet": {"id": "fragmento_nix", "name": "Fragmento NIX", "rarity": 5},
            "tickets": 2,
        },
    },
    "integrar": {
        "label": "Integrar NIX a Wolford",
        "requires": {},
        "reward": {
            "cosmetics": [
                {"id": "token_titulo_mediador_digital", "type": "title"},
                {"id": "token_moldura_interface_corrompida", "type": "frame"},
            ],
            "fragmentos": 20,
            "tickets": 2,
        },
    },
    "observar": {
        "label": "Observar em silencio",
        "requires": {"affinity": 45},
        "reward": {
            "cosmetics": [
                {"id": "token_titulo_voce_viu_demais", "type": "title"},
                {"id": "token_moldura_glitch", "type": "frame"},
            ],
            "gems": 5,
        },
    },
}

NIX_PUZZLE_ALIASES = {
    "memoria",
    "memorias",
    "lembrar",
    "lembranca",
    "lembrancas",
}
