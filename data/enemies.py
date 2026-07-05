# ==========================================
# DICIONÁRIO DE INIMIGOS E BOSSES
# ==========================================

ENEMIES = {
    # ==========================================
    # DUNGEON 1: FLORESTA GOBLIN (Nv 1-10)
    # ==========================================
    "goblin_guerreiro": {
        "nome": "Goblin Guerreiro", "tipo": "comum",
        "hp": 180, "atk": 35, "def": 20, "matk": 0, "spd": 15, "crt": 5, "imagem": ""
    },
    "goblin_arqueiro": {
        "nome": "Goblin Arqueiro", "tipo": "comum",
        "hp": 140, "atk": 45, "def": 15, "matk": 0, "spd": 25, "crt": 15, "imagem": ""
    },
    "goblin_xama": {
        "nome": "Goblin Xamã", "tipo": "comum",
        "hp": 160, "atk": 20, "def": 30, "matk": 55, "spd": 20, "crt": 5, "imagem": ""
    },
    "lobo_selvagem": {
        "nome": "Lobo Selvagem", "tipo": "comum",
        "hp": 250, "atk": 55, "def": 35, "matk": 0, "spd": 30, "crt": 15, "imagem": ""
    },
    "trol": {
        "nome": "Trol", "tipo": "comum",
        "hp": 900, "atk": 90, "def": 50, "matk": 0, "spd": 10, "crt": 5, "imagem": ""
    },
    # Mini-Bosses D1
    "goblin_veterano": {
        "nome": "Goblin Veterano", "tipo": "mini_boss",
        "hp": 600, "atk": 65, "def": 30, "matk": 0, "spd": 22, "crt": 10, "imagem": ""
    },
    "goblin_berserk": {
        "nome": "Goblin Berserk", "tipo": "mini_boss",
        "hp": 800, "atk": 85, "def": 25, "matk": 0, "spd": 25, "crt": 20, "imagem": ""
    },
    "goblin_xama_anciao": {
        "nome": "Goblin Xamã Ancião", "tipo": "mini_boss",
        "hp": 700, "atk": 20, "def": 35, "matk": 100, "spd": 24, "crt": 5, "imagem": ""
    },
    "lobo_alfa": {
        "nome": "Lobo Alfa", "tipo": "mini_boss",
        "hp": 1000, "atk": 110, "def": 45, "matk": 0, "spd": 35, "crt": 20, "imagem": ""
    },
    # Boss Final D1
    "rei_goblin": {
        "nome": "Rei Goblin", "tipo": "boss",
        "hp": 2500, "atk": 130, "def": 60, "matk": 0, "spd": 25, "crt": 10,
        "habilidade": "invocar_goblins",
        "imagem": ""
    },

    # ==========================================
    # DUNGEON 2: CATACUMBAS ESQUECIDAS (Nv 10-15)
    # ==========================================
    "esqueleto": {
        "nome": "Esqueleto", "tipo": "comum",
        "hp": 550, "atk": 90, "def": 40, "matk": 0, "spd": 20, "crt": 5, "imagem": ""
    },
    "zumbi": {
        "nome": "Zumbi", "tipo": "comum",
        "hp": 800, "atk": 75, "def": 60, "matk": 0, "spd": 10, "crt": 0, "imagem": ""
    },
    "ghoul": {
        "nome": "Ghoul", "tipo": "comum",
        "hp": 700, "atk": 110, "def": 35, "matk": 0, "spd": 35, "crt": 20, "imagem": ""
    },
    "poltergeist": {
        "nome": "Poltergeist", "tipo": "comum",
        "hp": 500, "atk": 0, "def": 35, "matk": 130, "spd": 45, "crt": 5, "imagem": ""
    },
    "necromante": {
        "nome": "Necromante", "tipo": "comum",
        "hp": 800, "atk": 25, "def": 40, "matk": 150, "spd": 25, "crt": 5, "imagem": ""
    },
    # Mini-Bosses D2
    "cavaleiro_esqueleto": {
        "nome": "Cavaleiro Esqueleto", "tipo": "mini_boss",
        "hp": 2000, "atk": 160, "def": 80, "matk": 0, "spd": 25, "crt": 15, "imagem": ""
    },
    "rei_sem_cabeca": {
        "nome": "Rei sem Cabeça", "tipo": "mini_boss",
        "hp": 2500, "atk": 200, "def": 75, "matk": 0, "spd": 20, "crt": 20,
        "habilidade": "dano_area_3_turnos", "imagem": ""
    },
    "guardiao_da_cripta": {
        "nome": "Guardião da Cripta", "tipo": "mini_boss",
        "hp": 3000, "atk": 220, "def": 100, "matk": 0, "spd": 15, "crt": 10,
        "habilidade": "prender_oponente", "imagem": ""
    },
    "assombracao": {
        "nome": "Assombração", "tipo": "mini_boss",
        "hp": 2200, "atk": 0, "def": 60, "matk": 250, "spd": 40, "crt": 10,
        "habilidade": "imune_atk_fisico", "imagem": ""
    },
    # Boss Final D2
    "lich": {
        "nome": "Lich", "tipo": "boss",
        "hp": 10000, "atk": 50, "def": 150, "matk": 400, "spd": 35, "crt": 15,
        "habilidade": "necromancia_lentidao", "imagem": ""
    },

    # ==========================================
    # DUNGEON 3: PICOS CONGELADOS (Nv 15-20)
    # ==========================================
    "lobo_de_gelo": {
        "nome": "Lobo de Gelo", "tipo": "comum",
        "hp": 1000, "atk": 160, "def": 60, "matk": 0, "spd": 50, "crt": 15, "imagem": ""
    },
    "golem_de_gelo": {
        "nome": "Golem de Gelo", "tipo": "comum",
        "hp": 2500, "atk": 140, "def": 200, "matk": 0, "spd": 10, "crt": 5, "imagem": ""
    },
    "harpia": {
        "nome": "Harpia", "tipo": "comum",
        "hp": 1200, "atk": 190, "def": 60, "matk": 0, "spd": 60, "crt": 10, "imagem": ""
    },
    "serpente_glacial": {
        "nome": "Serpente Glacial", "tipo": "comum",
        "hp": 1800, "atk": 100, "def": 80, "matk": 210, "spd": 40, "crt": 20, "imagem": ""
    },
    "mago_de_gelo": {
        "nome": "Mago de Gelo", "tipo": "comum",
        "hp": 1500, "atk": 30, "def": 70, "matk": 250, "spd": 30, "crt": 10, "imagem": ""
    },
    # Mini-Bosses D3
    "urso_polar_gigante": {
        "nome": "Urso Polar Gigante", "tipo": "mini_boss",
        "hp": 4000, "atk": 300, "def": 120, "matk": 0, "spd": 20, "crt": 15, "imagem": ""
    },
    "harpia_rainha": {
        "nome": "Harpia Rainha", "tipo": "mini_boss",
        "hp": 3500, "atk": 350, "def": 80, "matk": 0, "spd": 65, "crt": 15,
        "habilidade": "congelar_dois_inimigos", "imagem": ""
    },
    "golem_de_gelo_ancestral": {
        "nome": "Golem de Gelo Ancestral", "tipo": "mini_boss",
        "hp": 6000, "atk": 250, "def": 300, "matk": 0, "spd": 15, "crt": 5,
        "habilidade": "stun_e_lentidao", "imagem": ""
    },
    "yeti_anciao": {
        "nome": "Yeti Ancião", "tipo": "mini_boss",
        "hp": 7000, "atk": 400, "def": 180, "matk": 0, "spd": 25, "crt": 25,
        "habilidade": "reduz_defesa_geral", "imagem": ""
    },
    # Boss Final D3
    "dragao_de_gelo": {
        "nome": "Dragão de Gelo", "tipo": "boss",
        "hp": 15000, "atk": 450, "def": 300, "matk": 400, "spd": 40, "crt": 20,
        "habilidade": "era_glacial", "imagem": ""
    },

    # ==========================================
    # DUNGEON 4: FORTALEZA DEMONÍACA (Nv 20-35)
    # ==========================================
    "demonio_menor": {
        "nome": "Demônio Menor", "tipo": "comum",
        "hp": 2200, "atk": 280, "def": 150, "matk": 0, "spd": 35, "crt": 5, "imagem": ""
    },
    "vampiro": {
        "nome": "Vampiro", "tipo": "comum",
        "hp": 2000, "atk": 320, "def": 120, "matk": 250, "spd": 60, "crt": 15, "imagem": ""
    },
    "demonio_medio": {
        "nome": "Demônio Médio", "tipo": "comum",
        "hp": 4500, "atk": 400, "def": 200, "matk": 0, "spd": 30, "crt": 10, "imagem": ""
    },
    "mago_infernal": {
        "nome": "Mago Infernal", "tipo": "comum",
        "hp": 2500, "atk": 50, "def": 120, "matk": 450, "spd": 45, "crt": 10, "imagem": ""
    },
    "vampiro_nobre": {
        "nome": "Vampiro Nobre", "tipo": "comum",
        "hp": 5000, "atk": 500, "def": 180, "matk": 400, "spd": 65, "crt": 20, "imagem": ""
    },
    # Mini-Bosses D4
    "cerberus": {
        "nome": "Cerberus", "tipo": "mini_boss",
        "hp": 8000, "atk": 600, "def": 300, "matk": 150, "spd": 55, "crt": 15,
        "habilidade": "tornado_de_fogo", "imagem": ""
    },
    "arquiduque_demonio": {
        "nome": "Arquiduque Demônio", "tipo": "mini_boss",
        "hp": 10000, "atk": 750, "def": 350, "matk": 0, "spd": 40, "crt": 20,
        "habilidade": "contrato_berserk", "imagem": ""
    },
    "lorde_vampiro": {
        "nome": "Lorde Vampiro", "tipo": "mini_boss",
        "hp": 12000, "atk": 800, "def": 400, "matk": 700, "spd": 70, "crt": 25,
        "habilidade": "sacrificio_de_sangue", "imagem": ""
    },
    "general_do_abismo": {
        "nome": "General do Abismo", "tipo": "mini_boss",
        "hp": 15000, "atk": 1000, "def": 500, "matk": 0, "spd": 45, "crt": 15,
        "habilidade": "ignorar_defesa_explosao", "imagem": ""
    },
    # Boss Final D4
    "arquidemonio_belphegor": {
        "nome": "Arquidemônio Belphegor", "tipo": "boss",
        "hp": 35000, "atk": 1500, "def": 800, "matk": 1200, "spd": 55, "crt": 20,
        "habilidade": "bloqueio_de_habilidade", "imagem": ""
    },

    # ==========================================
    # DUNGEON 5: ABISMO DOS ECOS (Nv 35-50)
    # ==========================================
    "eco_corrompido": {
        "nome": "Eco Corrompido", "tipo": "comum",
        "hp": 8000, "atk": 550, "def": 300, "matk": 0, "spd": 50, "crt": 10, "imagem": ""
    },
    "cavaleiro_fantasma": {
        "nome": "Cavaleiro Fantasma", "tipo": "comum",
        "hp": 12000, "atk": 700, "def": 500, "matk": 0, "spd": 45, "crt": 15, "imagem": ""
    },
    "mago_espectral": {
        "nome": "Mago Espectral", "tipo": "comum",
        "hp": 9000, "atk": 150, "def": 250, "matk": 800, "spd": 60, "crt": 10, "imagem": ""
    },
    "assassino_de_ecos": {
        "nome": "Assassino de Ecos", "tipo": "comum",
        "hp": 7000, "atk": 1000, "def": 200, "matk": 0, "spd": 100, "crt": 40, "imagem": ""
    },
    # Mini-Bosses D5
    "eco_do_heroi_caido": {
        "nome": "Eco do Herói Caído", "tipo": "mini_boss",
        "hp": 15000, "atk": 1200, "def": 500, "matk": 1200, "spd": 65, "crt": 20,
        "habilidade": "ignorar_matk", "imagem": ""
    },
    "eco_do_rei_sem_nome": {
        "nome": "Eco do Rei Sem Nome", "tipo": "mini_boss",
        "hp": 20000, "atk": 1500, "def": 700, "matk": 0, "spd": 55, "crt": 25,
        "habilidade": "anular_atk", "imagem": ""
    },
    "eco_do_dragao_negro": {
        "nome": "Eco do Dragão Negro", "tipo": "mini_boss",
        "hp": 25000, "atk": 1800, "def": 1000, "matk": 1500, "spd": 70, "crt": 20,
        "habilidade": "desintegracao", "imagem": ""
    },
    "eco_do_ultimo_sobrevivente": {
        "nome": "Eco do Último Sobrevivente", "tipo": "mini_boss",
        "hp": 30000, "atk": 2200, "def": 1200, "matk": 0, "spd": 75, "crt": 30,
        "habilidade": "paralisia_em_massa", "imagem": ""
    },
    # Boss Final D5
    "a_testemunha": {
        "nome": "A Testemunha", "tipo": "boss",
        "hp": 80000, "atk": 3000, "def": 2000, "matk": 3000, "spd": 85, "crt": 25,
        "habilidade": "aetherion", "imagem": ""
    },

    # ==========================================
    # INIMIGOS DE AVENTURAS E EVENTOS
    # ==========================================
    # Bestas e Monstros Comuns
    "slime": {"nome": "Slime", "tipo": "comum", "hp": 250, "atk": 50, "def": 20, "matk": 0, "spd": 15, "crt": 5},
    "slime_toxico": {"nome": "Slime Tóxico", "tipo": "comum", "hp": 400, "atk": 70, "def": 30, "matk": 0, "spd": 20, "crt": 5},
    "slime_gigante": {"nome": "Slime Gigante Mutante", "tipo": "boss", "hp": 1800, "atk": 170, "def": 90, "matk": 60, "spd": 18, "crt": 5},
    "rato_mutante": {"nome": "Rato Mutante", "tipo": "comum", "hp": 300, "atk": 80, "def": 20, "matk": 0, "spd": 40, "crt": 10},
    "aranha_gigante": {"nome": "Aranha Gigante", "tipo": "comum", "hp": 600, "atk": 100, "def": 50, "matk": 0, "spd": 35, "crt": 15},
    "lagarto_gigante": {"nome": "Lagarto Gigante", "tipo": "comum", "hp": 1000, "atk": 120, "def": 70, "matk": 0, "spd": 30, "crt": 10},
    "lagarto_fogo": {"nome": "Lagarto de Fogo", "tipo": "comum", "hp": 1200, "atk": 150, "def": 80, "matk": 80, "spd": 35, "crt": 12},
    "homem_arvore": {"nome": "Homem Árvore", "tipo": "comum", "hp": 1500, "atk": 110, "def": 120, "matk": 0, "spd": 15, "crt": 5},
    "troll_das_neves": {"nome": "Troll das Neves", "tipo": "comum", "hp": 2000, "atk": 160, "def": 150, "matk": 0, "spd": 20, "crt": 5},
    
    # Construtos e Golems
    "golem_pedra": {"nome": "Golem de Pedra", "tipo": "comum", "hp": 2500, "atk": 140, "def": 200, "matk": 0, "spd": 10, "crt": 5, "habilidade": "imune_atk_fisico"},
    "golem_cristal": {"nome": "Golem de Cristal", "tipo": "comum", "hp": 3000, "atk": 180, "def": 150, "matk": 0, "spd": 25, "crt": 15},
    "golem_ferro": {"nome": "Golem de Ferro", "tipo": "comum", "hp": 4000, "atk": 250, "def": 300, "matk": 0, "spd": 15, "crt": 5},
    "gargula_ferro": {"nome": "Gárgula de Ferro", "tipo": "comum", "hp": 2800, "atk": 200, "def": 180, "matk": 0, "spd": 40, "crt": 10},
    
    # Criaturas do Mar
    "zumbi_aquatico": {"nome": "Zumbi Aquático", "tipo": "comum", "hp": 800, "atk": 85, "def": 40, "matk": 0, "spd": 20, "crt": 5},
    "kraken_jovem": {"nome": "Kraken Jovem", "tipo": "mini_boss", "hp": 5000, "atk": 280, "def": 150, "matk": 100, "spd": 35, "crt": 10},
    "espectro_agua": {"nome": "Espectro D'água", "tipo": "comum", "hp": 1800, "atk": 0, "def": 80, "matk": 220, "spd": 45, "crt": 5, "habilidade": "imune_atk_fisico"},
    
    # Cultistas, Bandidos e Mercenários
    "cavaleiro": {"nome": "Cavaleiro Corrupto", "tipo": "comum", "hp": 1200, "atk": 130, "def": 100, "matk": 0, "spd": 25, "crt": 5},
    "mercenario": {"nome": "Mercenário", "tipo": "comum", "hp": 900, "atk": 150, "def": 60, "matk": 0, "spd": 40, "crt": 15},
    "mercenario_mago": {"nome": "Mercenário Mago", "tipo": "comum", "hp": 700, "atk": 25, "def": 40, "matk": 180, "spd": 30, "crt": 5},
    "lider_bandido": {"nome": "Líder Bandido", "tipo": "mini_boss", "hp": 2500, "atk": 220, "def": 120, "matk": 0, "spd": 45, "crt": 20},
    "cultista_fanatico": {"nome": "Cultista Fanático", "tipo": "comum", "hp": 800, "atk": 160, "def": 50, "matk": 80, "spd": 35, "crt": 15},
    "mago_sombrio": {"nome": "Mago Sombrio", "tipo": "comum", "hp": 1100, "atk": 20, "def": 60, "matk": 250, "spd": 30, "crt": 10},
    "assassino_elite": {"nome": "Assassino de Elite", "tipo": "mini_boss", "hp": 3000, "atk": 350, "def": 100, "matk": 0, "spd": 80, "crt": 35},
    "nobre_corrupto": {"nome": "Nobre Corrupto", "tipo": "mini_boss", "hp": 1500, "atk": 80, "def": 150, "matk": 0, "spd": 20, "crt": 5},
    "guarda_elite": {"nome": "Guarda de Elite", "tipo": "comum", "hp": 2800, "atk": 180, "def": 250, "matk": 0, "spd": 30, "crt": 10},
    "goblin_assassino": {"nome": "Goblin Assassino", "tipo": "comum", "hp": 700, "atk": 160, "def": 30, "matk": 0, "spd": 60, "crt": 25},
    
    # Magos Específicos
    "mago_aprendiz": {"nome": "Mago Aprendiz", "tipo": "comum", "hp": 600, "atk": 20, "def": 30, "matk": 140, "spd": 25, "crt": 5},
    "arquimago_corrupto": {"nome": "Arquimago Corrupto", "tipo": "boss", "hp": 8000, "atk": 60, "def": 180, "matk": 500, "spd": 45, "crt": 15, "habilidade": "magia_em_massa"},
    "sumo_sacerdote_olho": {"nome": "Sumo Sacerdote do Olho", "tipo": "boss", "hp": 12000, "atk": 100, "def": 250, "matk": 650, "spd": 50, "crt": 10, "habilidade": "sacrificio_de_sangue"},
    
    # Espirítos, Sombras e Ecos Específicos
    "espectro": {"nome": "Espectro", "tipo": "comum", "hp": 2200, "atk": 0, "def": 100, "matk": 250, "spd": 50, "crt": 10, "habilidade": "imune_atk_fisico"},
    "espirito_glacial": {"nome": "Espírito Glacial", "tipo": "comum", "hp": 1800, "atk": 0, "def": 80, "matk": 240, "spd": 45, "crt": 10},
    "reflexo_sombrio": {"nome": "Reflexo Sombrio", "tipo": "comum", "hp": 2800, "atk": 250, "def": 120, "matk": 250, "spd": 55, "crt": 20},
    "clone_assassino": {"nome": "Clone Assassino", "tipo": "mini_boss", "hp": 4500, "atk": 400, "def": 150, "matk": 0, "spd": 90, "crt": 30},
    "clone_sombrio": {"nome": "Clone Sombrio", "tipo": "mini_boss", "hp": 5000, "atk": 300, "def": 200, "matk": 300, "spd": 60, "crt": 15},
    "trol_sombrio": {"nome": "Trol Sombrio", "tipo": "comum", "hp": 5500, "atk": 350, "def": 250, "matk": 0, "spd": 25, "crt": 5},
    "demonio_abissal": {"nome": "Demônio Abissal", "tipo": "mini_boss", "hp": 12000, "atk": 500, "def": 350, "matk": 450, "spd": 55, "crt": 15},
    
    # Chefes Épicos das Aventuras
    "besta_nevoa": {"nome": "Besta da Névoa", "tipo": "mini_boss", "hp": 7000, "atk": 380, "def": 200, "matk": 0, "spd": 65, "crt": 20},
    "besta_nevoa_furiosa": {"nome": "Besta da Névoa (Furiosa)", "tipo": "boss", "hp": 10000, "atk": 550, "def": 250, "matk": 0, "spd": 80, "crt": 30, "habilidade": "contrato_berserk"},
    "wyvern_tempestuoso": {"nome": "Wyvern Tempestuoso", "tipo": "boss", "hp": 15000, "atk": 700, "def": 300, "matk": 400, "spd": 90, "crt": 25, "habilidade": "tornado_de_fogo"},
    "rei_cristal": {"nome": "Rei de Cristal", "tipo": "boss", "hp": 22000, "atk": 800, "def": 800, "matk": 0, "spd": 35, "crt": 10, "habilidade": "reduz_defesa_geral"},
    "cerebro_arcano": {"nome": "Cérebro Arcano", "tipo": "boss", "hp": 18000, "atk": 0, "def": 500, "matk": 900, "spd": 65, "crt": 15, "habilidade": "aetherion"},
    "guardiao_realidade": {"nome": "Guardião da Realidade", "tipo": "boss", "hp": 30000, "atk": 900, "def": 600, "matk": 900, "spd": 75, "crt": 20, "habilidade": "paralisia_em_massa"},
    "lorde_cavaleiro_negro": {"nome": "General de Ferro Negro", "tipo": "boss", "hp": 28000, "atk": 1000, "def": 1200, "matk": 0, "spd": 45, "crt": 15, "habilidade": "esmagar_muralha"},
    "tita_magma": {"nome": "Titã de Magma", "tipo": "boss", "hp": 40000, "atk": 1200, "def": 1000, "matk": 600, "spd": 30, "crt": 10, "habilidade": "terremoto_glacial"},
    "lider_assassino_corvo": {"nome": "Corvo Negro", "tipo": "boss", "hp": 16000, "atk": 1100, "def": 350, "matk": 0, "spd": 120, "crt": 45, "habilidade": "investida_mortal"},
    
    # Divindades e Entidades Cósmicas
    "heroi_corrompido_deus": {"nome": "Cópia Distorcida do Herói", "tipo": "boss", "hp": 45000, "atk": 1600, "def": 800, "matk": 1600, "spd": 100, "crt": 30, "habilidade": "desintegracao"},
    "falso_deus_parasita": {"nome": "Falso Deus Parasita", "tipo": "boss", "hp": 55000, "atk": 1400, "def": 1000, "matk": 2000, "spd": 85, "crt": 20, "habilidade": "sopro_do_caos"},
    "rei_demonio": {"nome": "Rei Demônio Ancestral", "tipo": "boss", "hp": 75000, "atk": 2500, "def": 1500, "matk": 2000, "spd": 90, "crt": 25, "habilidade": "fim_dos_tempos"},
    "arquivista_supremo": {"nome": "O Arquivista do Tempo", "tipo": "boss", "hp": 90000, "atk": 2000, "def": 2000, "matk": 3000, "spd": 110, "crt": 20, "habilidade": "aetherion"}
}
