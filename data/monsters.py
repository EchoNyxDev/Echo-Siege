# ==========================================
# DICIONÁRIO DE MONSTROS PARA O SISTEMA DE HUNT
# ==========================================

# Raridades: 
# 50 = Comum (Aparece muito)
# 30 = Incomum
# 15 = Raro
# 5  = Épico/Chefe de Caça (Loot muito maior)

HUNT_MONSTERS = {
    # ================= NÍVEL 1 a 15 =================
    "slime_verde": {
        "nome": "Slime Verde", "nivel_min": 1, "nivel_max": 15, "raridade": 50,
        "hp_base": 80, "atk_base": 15, "def_base": 5, 
        "gold_base": 30, "xp_base": 15, "drop": "gosma_verde"
    },
    "rato_gigante": {
        "nome": "Rato Gigante Mutante", "nivel_min": 1, "nivel_max": 15, "raridade": 50,
        "hp_base": 100, "atk_base": 20, "def_base": 8, 
        "gold_base": 35, "xp_base": 18, "drop": "rabo_de_rato"
    },
    "goblin_batedor": {
        "nome": "Goblin Batedor", "nivel_min": 3, "nivel_max": 15, "raridade": 30,
        "hp_base": 150, "atk_base": 35, "def_base": 15, 
        "gold_base": 50, "xp_base": 30, "drop": "adaga_enferrujada"
    },
    "lobo_selvagem": {
        "nome": "Lobo Selvagem Faminto", "nivel_min": 5, "nivel_max": 15, "raridade": 30,
        "hp_base": 200, "atk_base": 45, "def_base": 20, 
        "gold_base": 65, "xp_base": 40, "drop": "pele_de_lobo"
    },
    "rei_slime": {
        "nome": "Rei Slime", "nivel_min": 5, "nivel_max": 15, "raridade": 5,
        "hp_base": 450, "atk_base": 60, "def_base": 30, 
        "gold_base": 150, "xp_base": 100, "drop": "coroa_de_gosma"
    },

    # ================= NÍVEL 16 a 35 =================
    "orc_guerreiro": {
        "nome": "Orc Guerreiro", "nivel_min": 16, "nivel_max": 35, "raridade": 50,
        "hp_base": 400, "atk_base": 80, "def_base": 50, 
        "gold_base": 100, "xp_base": 60, "drop": "dente_de_orc"
    },
    "esqueleto_mago": {
        "nome": "Esqueleto Mago", "nivel_min": 16, "nivel_max": 35, "raridade": 50,
        "hp_base": 250, "atk_base": 120, "def_base": 20, 
        "gold_base": 120, "xp_base": 75, "drop": "po_de_osso"
    },
    "aranha_gigante": {
        "nome": "Aranha Teia-de-Aço", "nivel_min": 20, "nivel_max": 35, "raridade": 30,
        "hp_base": 500, "atk_base": 100, "def_base": 60, 
        "gold_base": 140, "xp_base": 90, "drop": "seda_de_aranha"
    },
    "lagarto_fogo": {
        "nome": "Lagarto de Fogo", "nivel_min": 25, "nivel_max": 35, "raridade": 15,
        "hp_base": 650, "atk_base": 150, "def_base": 80, 
        "gold_base": 200, "xp_base": 120, "drop": "escama_quente"
    },
    "chefe_orc": {
        "nome": "Chefe da Tribo Orc", "nivel_min": 25, "nivel_max": 35, "raridade": 5,
        "hp_base": 1200, "atk_base": 200, "def_base": 120, 
        "gold_base": 400, "xp_base": 250, "drop": "machado_do_chefe"
    },

    # ================= NÍVEL 36 a 60 =================
    "troll_cavernas": {
        "nome": "Troll das Cavernas", "nivel_min": 36, "nivel_max": 60, "raridade": 50,
        "hp_base": 1500, "atk_base": 180, "def_base": 100, 
        "gold_base": 250, "xp_base": 180, "drop": "sangue_de_troll"
    },
    "golem_pedra": {
        "nome": "Golem de Pedra", "nivel_min": 36, "nivel_max": 60, "raridade": 30,
        "hp_base": 2500, "atk_base": 150, "def_base": 300, 
        "gold_base": 300, "xp_base": 200, "drop": "nucleo_de_pedra"
    },
    "minotauro": {
        "nome": "Minotauro Furioso", "nivel_min": 40, "nivel_max": 60, "raridade": 30,
        "hp_base": 2000, "atk_base": 300, "def_base": 150, 
        "gold_base": 350, "xp_base": 220, "drop": "chifre_de_minotauro"
    },
    "wyvern": {
        "nome": "Wyvern dos Ventos", "nivel_min": 45, "nivel_max": 60, "raridade": 15,
        "hp_base": 1800, "atk_base": 400, "def_base": 120, 
        "gold_base": 450, "xp_base": 300, "drop": "asa_de_wyvern"
    },
    "sucubo": {
        "nome": "Súcubo da Ilusão", "nivel_min": 50, "nivel_max": 60, "raridade": 5,
        "hp_base": 3000, "atk_base": 500, "def_base": 200, 
        "gold_base": 800, "xp_base": 500, "drop": "essencia_da_ilusao"
    },

    # ================= NÍVEL 61 a 100+ =================
    "cavaleiro_morte": {
        "nome": "Cavaleiro da Morte", "nivel_min": 61, "nivel_max": 999, "raridade": 50,
        "hp_base": 5000, "atk_base": 600, "def_base": 400, 
        "gold_base": 600, "xp_base": 400, "drop": "espada_quebrada_sombria"
    },
    "quimera": {
        "nome": "Quimera Mutante", "nivel_min": 65, "nivel_max": 999, "raridade": 30,
        "hp_base": 7500, "atk_base": 800, "def_base": 500, 
        "gold_base": 800, "xp_base": 550, "drop": "cauda_de_leao"
    },
    "dragao_menor": {
        "nome": "Dragão Menor", "nivel_min": 70, "nivel_max": 999, "raridade": 15,
        "hp_base": 12000, "atk_base": 1200, "def_base": 800, 
        "gold_base": 1200, "xp_base": 800, "drop": "escama_menor"
    },
    "behemoth": {
        "nome": "Behemoth", "nivel_min": 80, "nivel_max": 999, "raridade": 5,
        "hp_base": 25000, "atk_base": 2000, "def_base": 1500, 
        "gold_base": 2500, "xp_base": 1500, "drop": "chifre_ancestral"
    },
    "dragao_anciao_rei": {
        "nome": "Rei Dragão Ancião (Mítico)", "nivel_min": 90, "nivel_max": 999, "raridade": 1,
        "hp_base": 50000, "atk_base": 4000, "def_base": 3000, 
        "gold_base": 10000, "xp_base": 5000, "drop": "coracao_de_dragao"
    }
}