# ==========================================
# ESTRUTURA DAS DUNGEONS E ANDARES
# ==========================================

DUNGEONS = {
    "floresta_goblin": {
        "id": 1,
        "nome": "Floresta Goblin",
        "level_rec": "1-10",
        "andares": {
            1: {
                "inimigos": {"goblin_guerreiro": 8},
                "mini_boss": "goblin_veterano",
                "loot_gold": 100, "loot_xp_main": 30, "loot_xp_party": 10
            },
            2: {
                "inimigos": {"goblin_guerreiro": 5, "goblin_arqueiro": 3},
                "mini_boss": "goblin_berserk",
                "loot_gold": 150, "loot_xp_main": 35, "loot_xp_party": 10
            },
            3: {
                "inimigos": {"goblin_guerreiro": 3, "goblin_arqueiro": 2, "goblin_xama": 1},
                "mini_boss": "goblin_xama_anciao",
                "loot_gold": 200, "loot_xp_main": 40, "loot_xp_party": 10
            },
            4: {
                "inimigos": {"lobo_selvagem": 3},
                "mini_boss": "lobo_alfa",
                "loot_gold": 250, "loot_xp_main": 40, "loot_xp_party": 20
            },
            5: {
                "inimigos": {"trol": 1},
                "boss": "rei_goblin",
                "loot_gold": 500, "loot_xp_main": 50, "loot_xp_party": 50
            }
        }
    },
    
    "catacumbas": {
        "id": 2,
        "nome": "Catacumbas Esquecidas",
        "level_rec": "10-15",
        "andares": {
            1: {
                "inimigos": {"esqueleto": 10},
                "mini_boss": "cavaleiro_esqueleto",
                "loot_gold": 200, "loot_xp_main": 50, "loot_xp_party": 10
            },
            2: {
                "inimigos": {"esqueleto": 4, "zumbi": 6},
                "mini_boss": "rei_sem_cabeca",
                "loot_gold": 250, "loot_xp_main": 55, "loot_xp_party": 20
            },
            3: {
                "inimigos": {"ghoul": 5},
                "mini_boss": "guardiao_da_cripta",
                "loot_gold": 300, "loot_xp_main": 60, "loot_xp_party": 20
            },
            4: {
                "inimigos": {"poltergeist": 3},
                "mini_boss": "assombracao",
                "loot_gold": 500, "loot_xp_main": 70, "loot_xp_party": 20
            },
            5: {
                "inimigos": {"necromante": 1},
                "boss": "lich",
                "loot_gold": 750, "loot_xp_main": 100, "loot_xp_party": 25
            }
        }
    },

    "picos_congelados": {
        "id": 3,
        "nome": "Picos Congelados",
        "level_rec": "15-20",
        "andares": {
            1: {
                "inimigos": {"lobo_de_gelo": 15},
                "mini_boss": "urso_polar_gigante",
                "loot_gold": 300, "loot_xp_main": 100, "loot_xp_party": 20
            },
            2: {
                "inimigos": {"lobo_de_gelo": 10, "golem_de_gelo": 3},
                "mini_boss": "harpia_rainha",
                "loot_gold": 450, "loot_xp_main": 120, "loot_xp_party": 25
            },
            3: {
                "inimigos": {"harpia": 4, "golem_de_gelo": 5},
                "mini_boss": "golem_de_gelo_ancestral",
                "loot_gold": 600, "loot_xp_main": 120, "loot_xp_party": 40
            },
            4: {
                "inimigos": {"serpente_glacial": 3},
                "mini_boss": "yeti_anciao",
                "loot_gold": 800, "loot_xp_main": 150, "loot_xp_party": 50
            },
            5: {
                "inimigos": {"mago_de_gelo": 1, "serpente_glacial": 1},
                "boss": "dragao_de_gelo",
                "loot_gold": 1000, "loot_xp_main": 150, "loot_xp_party": 75
            }
        }
    },

    "fortaleza_demoniaca": {
        "id": 4,
        "nome": "Fortaleza Demoníaca",
        "level_rec": "20-35",
        "andares": {
            1: {
                "inimigos": {"demonio_menor": 20},
                "mini_boss": "cerberus",
                "loot_gold": 400, "loot_xp_main": 150, "loot_xp_party": 75
            },
            2: {
                "inimigos": {"vampiro": 15, "demonio_medio": 3},
                "mini_boss": "arquiduque_demonio",
                "loot_gold": 550, "loot_xp_main": 170, "loot_xp_party": 85
            },
            3: {
                "inimigos": {"mago_infernal": 1, "vampiro": 5, "demonio_medio": 1},
                "mini_boss": "lorde_vampiro",
                "loot_gold": 700, "loot_xp_main": 200, "loot_xp_party": 100
            },
            4: {
                "inimigos": {"demonio_medio": 20},
                "mini_boss": "general_do_abismo",
                "loot_gold": 1000, "loot_xp_main": 250, "loot_xp_party": 120
            },
            5: {
                "inimigos": {"vampiro_nobre": 1},
                "boss": "arquidemonio_belphegor",
                "loot_gold": 1500, "loot_xp_main": 300, "loot_xp_party": 150
            }
        }
    },

    "abismo_dos_ecos": {
        "id": 5,
        "nome": "Abismo dos Ecos",
        "level_rec": "35-50",
        "andares": {
            1: {
                "inimigos": {"eco_corrompido": 30},
                "mini_boss": "eco_do_heroi_caido",
                "loot_gold": 1000, "loot_xp_main": 200, "loot_xp_party": 100
            },
            2: {
                "inimigos": {"cavaleiro_fantasma": 1, "eco_corrompido": 20},
                "mini_boss": "eco_do_rei_sem_nome",
                "loot_gold": 1500, "loot_xp_main": 220, "loot_xp_party": 110
            },
            3: {
                "inimigos": {"mago_espectral": 1, "eco_corrompido": 10},
                "mini_boss": "eco_do_dragao_negro",
                "loot_gold": 2000, "loot_xp_main": 250, "loot_xp_party": 125
            },
            4: {
                "inimigos": {"cavaleiro_fantasma": 1, "mago_espectral": 1, "eco_corrompido": 5},
                "mini_boss": "eco_do_ultimo_sobrevivente",
                "loot_gold": 2500, "loot_xp_main": 300, "loot_xp_party": 150
            },
            5: {
                "inimigos": {"eco_corrompido": 50, "assassino_de_ecos": 1},
                "boss": "a_testemunha",
                "loot_gold": 3500, "loot_xp_main": 500, "loot_xp_party": 250
            }
        }
    }
}