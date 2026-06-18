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
                "inimigos": {"goblin_guerreiro": [4, 7]},
                "mini_boss": "goblin_veterano",
                "boss_minions": {"goblin_guerreiro": [2, 3]},
                "loot_gold": 100, "loot_xp_main": 30, "loot_xp_party": 10
            },
            2: {
                "inimigos": {"goblin_guerreiro": [4, 6], "goblin_arqueiro": [2, 4]},
                "mini_boss": "goblin_berserk",
                "boss_minions": {"goblin_arqueiro": [1, 2], "goblin_guerreiro": [2, 2]},
                "loot_gold": 150, "loot_xp_main": 35, "loot_xp_party": 10
            },
            3: {
                "inimigos": {"goblin_guerreiro": [3, 5], "goblin_arqueiro": [2, 3], "goblin_xama": [1, 2]},
                "mini_boss": "goblin_xama_anciao",
                "boss_minions": {"goblin_xama": [1, 2], "goblin_guerreiro": [3, 4]},
                "loot_gold": 200, "loot_xp_main": 40, "loot_xp_party": 10
            },
            4: {
                "inimigos": {"lobo_selvagem": [3, 5], "goblin_arqueiro": [1, 3]},
                "mini_boss": "lobo_alfa",
                "boss_minions": {"lobo_selvagem": [2, 4]},
                "loot_gold": 250, "loot_xp_main": 40, "loot_xp_party": 20
            },
            5: {
                "inimigos": {"trol": [1, 2], "lobo_selvagem": [2, 4]},
                "boss": "rei_goblin",
                "boss_minions": {"goblin_veterano": [2, 3], "goblin_xama_anciao": [1, 1], "lobo_alfa": [1, 1]},
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
                "inimigos": {"esqueleto": [6, 10]},
                "mini_boss": "cavaleiro_esqueleto",
                "boss_minions": {"esqueleto": [3, 5]},
                "loot_gold": 200, "loot_xp_main": 50, "loot_xp_party": 10
            },
            2: {
                "inimigos": {"esqueleto": [3, 6], "zumbi": [4, 7]},
                "mini_boss": "rei_sem_cabeca",
                "boss_minions": {"zumbi": [3, 4]},
                "loot_gold": 250, "loot_xp_main": 55, "loot_xp_party": 20
            },
            3: {
                "inimigos": {"ghoul": [4, 6], "zumbi": [2, 4]},
                "mini_boss": "guardiao_da_cripta",
                "boss_minions": {"ghoul": [2, 3], "esqueleto": [2, 4]},
                "loot_gold": 300, "loot_xp_main": 60, "loot_xp_party": 20
            },
            4: {
                "inimigos": {"poltergeist": [3, 5], "ghoul": [2, 3]},
                "mini_boss": "assombracao",
                "boss_minions": {"poltergeist": [2, 3]},
                "loot_gold": 500, "loot_xp_main": 70, "loot_xp_party": 20
            },
            5: {
                "inimigos": {"necromante": [1, 2], "cavaleiro_esqueleto": [1, 2], "poltergeist": [2, 4]},
                "boss": "lich",
                "boss_minions": {"necromante": [2, 2], "cavaleiro_esqueleto": [2, 3], "rei_sem_cabeca": [1, 1]},
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
                "inimigos": {"lobo_de_gelo": [8, 12]},
                "mini_boss": "urso_polar_gigante",
                "boss_minions": {"lobo_de_gelo": [4, 6]},
                "loot_gold": 300, "loot_xp_main": 100, "loot_xp_party": 20
            },
            2: {
                "inimigos": {"lobo_de_gelo": [6, 9], "golem_de_gelo": [2, 4]},
                "mini_boss": "harpia_rainha",
                "boss_minions": {"harpia": [3, 5]},
                "loot_gold": 450, "loot_xp_main": 120, "loot_xp_party": 25
            },
            3: {
                "inimigos": {"harpia": [4, 6], "golem_de_gelo": [4, 6]},
                "mini_boss": "golem_de_gelo_ancestral",
                "boss_minions": {"golem_de_gelo": [3, 4], "mago_de_gelo": [1, 2]},
                "loot_gold": 600, "loot_xp_main": 120, "loot_xp_party": 40
            },
            4: {
                "inimigos": {"serpente_glacial": [3, 5], "harpia": [2, 4]},
                "mini_boss": "yeti_anciao",
                "boss_minions": {"lobo_de_gelo": [4, 6]},
                "loot_gold": 800, "loot_xp_main": 150, "loot_xp_party": 50
            },
            5: {
                "inimigos": {"mago_de_gelo": [2, 3], "serpente_glacial": [2, 4], "golem_de_gelo_ancestral": [1, 1]},
                "boss": "dragao_de_gelo",
                "boss_minions": {"urso_polar_gigante": [1, 2], "harpia_rainha": [1, 1], "mago_de_gelo": [2, 3]},
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
                "inimigos": {"demonio_menor": [12, 18]},
                "mini_boss": "cerberus",
                "boss_minions": {"demonio_menor": [6, 8]},
                "loot_gold": 400, "loot_xp_main": 150, "loot_xp_party": 75
            },
            2: {
                "inimigos": {"vampiro": [8, 12], "demonio_medio": [2, 4]},
                "mini_boss": "arquiduque_demonio",
                "boss_minions": {"demonio_medio": [3, 4]},
                "loot_gold": 550, "loot_xp_main": 170, "loot_xp_party": 85
            },
            3: {
                "inimigos": {"mago_infernal": [2, 4], "vampiro": [5, 8], "demonio_medio": [2, 3]},
                "mini_boss": "lorde_vampiro",
                "boss_minions": {"vampiro": [4, 6], "mago_infernal": [1, 2]},
                "loot_gold": 700, "loot_xp_main": 200, "loot_xp_party": 100
            },
            4: {
                "inimigos": {"demonio_medio": [10, 15], "mago_infernal": [3, 5]},
                "mini_boss": "general_do_abismo",
                "boss_minions": {"demonio_medio": [4, 6], "vampiro_nobre": [1, 1]},
                "loot_gold": 1000, "loot_xp_main": 250, "loot_xp_party": 120
            },
            5: {
                "inimigos": {"vampiro_nobre": [2, 4], "cerberus": [1, 2], "general_do_abismo": [1, 1]},
                "boss": "arquidemonio_belphegor",
                "boss_minions": {"general_do_abismo": [1, 2], "lorde_vampiro": [1, 2], "mago_infernal": [3, 4]},
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
                "inimigos": {"eco_corrompido": [15, 25]},
                "mini_boss": "eco_do_heroi_caido",
                "boss_minions": {"eco_corrompido": [8, 12]},
                "loot_gold": 1000, "loot_xp_main": 200, "loot_xp_party": 100
            },
            2: {
                "inimigos": {"cavaleiro_fantasma": [2, 4], "eco_corrompido": [10, 18]},
                "mini_boss": "eco_do_rei_sem_nome",
                "boss_minions": {"cavaleiro_fantasma": [3, 5]},
                "loot_gold": 1500, "loot_xp_main": 220, "loot_xp_party": 110
            },
            3: {
                "inimigos": {"mago_espectral": [2, 4], "eco_corrompido": [8, 14]},
                "mini_boss": "eco_do_dragao_negro",
                "boss_minions": {"mago_espectral": [2, 4]},
                "loot_gold": 2000, "loot_xp_main": 250, "loot_xp_party": 125
            },
            4: {
                "inimigos": {"cavaleiro_fantasma": [3, 5], "mago_espectral": [2, 4], "assassino_de_ecos": [1, 2]},
                "mini_boss": "eco_do_ultimo_sobrevivente",
                "boss_minions": {"assassino_de_ecos": [2, 3], "cavaleiro_fantasma": [2, 3]},
                "loot_gold": 2500, "loot_xp_main": 300, "loot_xp_party": 150
            },
            5: {
                "inimigos": {"eco_corrompido": [20, 30], "assassino_de_ecos": [3, 5], "eco_do_heroi_caido": [1, 2]},
                "boss": "a_testemunha",
                "boss_minions": {"eco_do_ultimo_sobrevivente": [1, 1], "eco_do_dragao_negro": [1, 1], "mago_espectral": [3, 5]},
                "loot_gold": 3500, "loot_xp_main": 500, "loot_xp_party": 250
            }
        }
    }
}