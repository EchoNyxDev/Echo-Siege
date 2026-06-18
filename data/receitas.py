RECEITAS = {
    # ================= CONSUMÍVEIS BÁSICOS =================
    "pocao_energia": {
        "nome": "Poção de Energia",
        "emoji": "⚡",
        "desc": "Zera o tempo de espera (CD) de Caçadas e Aventuras.",
        "ingredientes": {
            "gosma_verde": 3,
            "poeira_de_mana": 2
        }
    },
    "pergaminho_de_xp": {
        "nome": "Pergaminho de XP",
        "emoji": "📜",
        "desc": "+25% de XP ganho na próxima ação.",
        "ingredientes": {
            "fio_de_mana": 3,
            "po_de_osso": 2,
            "mapa_rasgado": 1
        }
    },
    "pergaminho_de_ouro": {
        "nome": "Pergaminho de Ouro",
        "emoji": "📜",
        "desc": "+25% de Ouro ganho na próxima ação.",
        "ingredientes": {
            "moeda_antiga": 3,
            "gema_opaca": 2,
            "fio_de_mana": 1
        }
    },
    "kit_reparos": {
        "nome": "Kit de Reparos",
        "emoji": "🔨",
        "desc": "Recupera 50 Suprimentos para a Muralha da Cidade.",
        "ingredientes": {
            "ferro_antigo": 4,
            "pedra_do_labirinto": 2,
            "pele_de_lobo": 2
        }
    },

    # ================= TICKETS E GACHA =================
    "ticket_pet": {
        "nome": "Ticket de Pet",
        "emoji": "🐾",
        "desc": "Usado para invocar um novo Pet companheiro aleatório.",
        "ingredientes": {
            "fragmento_dimensional": 5,
            "cristal_torto": 3,
            "chave_torta": 1
        }
    },
    "bilhete_dourado": {
        "nome": "Bilhete Dourado",
        "emoji": "🎟️",
        "desc": "Invocação 100% garantida de um herói Raro (3⭐ ou superior).",
        "ingredientes": {
            "coracao_de_dragao": 1,
            "fragmento_dimensional": 10,
            "fio_de_mana": 15
        }
    },
    "passe_contrabandista": {
        "nome": "Passe de Contrabandista",
        "emoji": "🎫",
        "desc": "Um item ilícito super valioso. Dá acesso aos pets mais raros.",
        "ingredientes": {
            "moeda_arkenor": 5,
            "pedra_do_labirinto": 10,
            "cristal_ressonante": 2
        }
    },

    # ================= EQUIPAMENTOS COMUNS (EARLY GAME) =================
    "lamina_encantada": {
        "nome": "Lâmina Encantada",
        "emoji": "⚔️",
        "desc": "Equipamento (Arma): +30 ATK",
        "ingredientes": {
            "ferro_antigo": 10,
            "fio_de_mana": 5,
            "nucleo_de_pedra": 1
        }
    },
    "tomo_dos_sabios": {
        "nome": "Tomo dos Sábios",
        "emoji": "📘",
        "desc": "Equipamento (Arma): +30 MATK",
        "ingredientes": {
            "mapa_rasgado": 8,
            "poeira_de_mana": 10,
            "essencia_da_ilusao": 1
        }
    },
    "escudo_do_guardiao": {
        "nome": "Escudo do Guardião",
        "emoji": "🛡️",
        "desc": "Equipamento (Defesa): +30 DEF",
        "ingredientes": {
            "pedra_do_labirinto": 15,
            "ferro_antigo": 5,
            "pele_de_lobo": 5
        }
    },

    # ================= EQUIPAMENTOS ÉPICOS (MID GAME) =================
    "espada_imperial": {
        "nome": "Espada Imperial",
        "emoji": "👑",
        "desc": "Equipamento (Arma): +75 ATK. Forjada pelos anões.",
        "ingredientes": {
            "token_de_borin": 1,
            "ferro_antigo": 20,
            "nucleo_gelo_puro": 1
        }
    },
    "coroa_arcana": {
        "nome": "Coroa Arcana",
        "emoji": "💠",
        "desc": "Equipamento (Arma): +75 MATK. Antigo adorno dos magos prisioneiros.",
        "ingredientes": {
            "essencia_de_mana": 5,
            "cristal_de_mana_bruta": 3,
            "chave_arcana_prisao": 1
        }
    },
    "armadura_real": {
        "nome": "Armadura Real",
        "emoji": "🛡️",
        "desc": "Equipamento (Defesa): +75 DEF. Feita com as escamas dos céus e a névoa das feras.",
        "ingredientes": {
            "escama_tempestuosa": 2,
            "presa_da_nevoa": 2,
            "ferro_antigo": 30
        }
    },

    # ================= EQUIPAMENTOS MÍTICOS / LENDÁRIOS (END GAME) =================
    "lamina_eterna": {
        "nome": "Lâmina Eterna",
        "emoji": "🗡️",
        "desc": "Arma Mítica: +120 ATK, +40 MATK, +20 DEF. Absorve a vida ao redor.",
        "ingredientes": {
            "lamina_encantada": 1,        # Precisa sacrificar uma arma para forjar esta
            "nucleo_cristal_vivo": 2,
            "nucleo_de_slime": 5
        }
    },
    "espada_dimensional": {
        "nome": "Espada Dimensional",
        "emoji": "🌌",
        "desc": "Arma Absoluta: +150 ATK, +150 MATK. Forjada com o próprio tecido do multiverso.",
        "ingredientes": {
            "nexus_dimensional": 1,
            "espelho_primordial": 2,
            "fragmento_cristal_sombrio": 5
        }
    },
    "armadura_magma": {
        "nome": "Armadura de Magma",
        "emoji": "🌋",
        "desc": "Defesa Absoluta: +30 ATK, +150 DEF. Queima qualquer um que ousar encostar.",
        "ingredientes": {
            "coracao_de_magma": 1,
            "runa_glacial": 2,          # Utiliza choque térmico extremo para forjar
            "ferro_antigo": 15
        }
    },

    # ================= ACESSÓRIOS SUPREMOS =================
    "amuleto_hibrido_eterno": {
        "nome": "Pingente dos Ecos Eternos",
        "emoji": "✨",
        "desc": "Acessório: Um item misterioso que converte o caos num milagre.",
        "ingredientes": {
            "ecos_eternos": 1,
            "perola_das_mares": 1,
            "flor_eterna": 3
        }
    }
}
