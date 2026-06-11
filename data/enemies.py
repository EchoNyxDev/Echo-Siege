# ==========================================
# DICIONÁRIO DE INIMIGOS E BOSSES
# ==========================================

ENEMIES = {
    # ==========================================
    # DUNGEON 1: FLORESTA GOBLIN (Nv 1-10)
    # ==========================================
    "goblin_guerreiro": {
        "nome": "Goblin Guerreiro", "tipo": "comum",
        "hp": 100, "atk": 30, "def": 10, "matk": 0, "spd": 10, "crt": 5, "imagem": ""
    },
    "goblin_arqueiro": {
        "nome": "Goblin Arqueiro", "tipo": "comum",
        "hp": 150, "atk": 35, "def": 25, "matk": 0, "spd": 15, "crt": 10, "imagem": ""
    },
    "goblin_xama": {
        "nome": "Goblin Xamã", "tipo": "comum",
        "hp": 200, "atk": 20, "def": 30, "matk": 40, "spd": 12, "crt": 5, "imagem": ""
    },
    "lobo_selvagem": {
        "nome": "Lobo Selvagem", "tipo": "comum",
        "hp": 300, "atk": 45, "def": 35, "matk": 0, "spd": 20, "crt": 15, "imagem": ""
    },
    "trol": {
        "nome": "Trol", "tipo": "comum",
        "hp": 400, "atk": 60, "def": 40, "matk": 0, "spd": 5, "crt": 5, "imagem": ""
    },
    # Mini-Bosses D1
    "goblin_veterano": {
        "nome": "Goblin Veterano", "tipo": "mini_boss",
        "hp": 300, "atk": 50, "def": 20, "matk": 0, "spd": 12, "crt": 10, "imagem": ""
    },
    "goblin_berserk": {
        "nome": "Goblin Berserk", "tipo": "mini_boss",
        "hp": 450, "atk": 60, "def": 25, "matk": 0, "spd": 15, "crt": 20, "imagem": ""
    },
    "goblin_xama_anciao": {
        "nome": "Goblin Xamã Ancião", "tipo": "mini_boss",
        "hp": 550, "atk": 20, "def": 30, "matk": 65, "spd": 14, "crt": 5, "imagem": ""
    },
    "lobo_alfa": {
        "nome": "Lobo Alfa", "tipo": "mini_boss",
        "hp": 600, "atk":70, "def": 40, "matk": 0, "spd": 25, "crt": 20, "imagem": ""
    },
    # Boss Final D1
    "rei_goblin": {
        "nome": "Rei Goblin", "tipo": "boss",
        "hp": 1000, "atk": 80, "def": 50, "matk": 0, "spd": 15, "crt": 10,
        "habilidade": "invocar_goblins",
        "imagem": ""
    },

    # ==========================================
    # DUNGEON 2: CATACUMBAS ESQUECIDAS (Nv 10-15)
    # ==========================================
    "esqueleto": {
        "nome": "Esqueleto", "tipo": "comum",
        "hp": 400, "atk": 55, "def": 20, "matk": 0, "spd": 12, "crt": 5, "imagem": ""
    },
    "zumbi": {
        "nome": "Zumbi", "tipo": "comum",
        "hp": 500, "atk": 60, "def": 25, "matk": 0, "spd": 5, "crt": 0, "imagem": ""
    },
    "ghoul": {
        "nome": "Ghoul", "tipo": "comum",
        "hp": 600, "atk": 70, "def": 30, "matk": 0, "spd": 18, "crt": 15, "imagem": ""
    },
    "poltergeist": {
        "nome": "Poltergeist", "tipo": "comum",
        "hp": 700, "atk": 0, "def": 35, "matk": 70, "spd": 20, "crt": 5, "imagem": ""
    },
    "necromante": {
        "nome": "Necromante", "tipo": "comum",
        "hp": 800, "atk": 15, "def": 40, "matk": 85, "spd": 10, "crt": 5, "imagem": ""
    },
    # Mini-Bosses D2
    "cavaleiro_esqueleto": {
        "nome": "Cavaleiro Esqueleto", "tipo": "mini_boss",
        "hp": 700, "atk": 60, "def": 40, "matk": 0, "spd": 15, "crt": 15, "imagem": ""
    },
    "rei_sem_cabeca": {
        "nome": "Rei sem Cabeça", "tipo": "mini_boss",
        "hp": 950, "atk": 90, "def": 45, "matk": 0, "spd": 10, "crt": 20,
        "habilidade": "dano_area_3_turnos", "imagem": ""
    },
    "guardiao_da_cripta": {
        "nome": "Guardião da Cripta", "tipo": "mini_boss",
        "hp": 1200, "atk": 110, "def": 50, "matk": 0, "spd": 8, "crt": 10,
        "habilidade": "prender_oponente", "imagem": ""
    },
    "assombracao": {
        "nome": "Assombração", "tipo": "mini_boss",
        "hp": 1500, "atk": 0, "def": 60, "matk": 120, "spd": 25, "crt": 10,
        "habilidade": "imune_atk_fisico", "imagem": ""
    },
    # Boss Final D2
    "lich": {
        "nome": "Lich", "tipo": "boss",
        "hp": 2500, "atk": 50, "def": 100, "matk": 200, "spd": 15, "crt": 15,
        "habilidade": "necromancia_lentidao", "imagem": ""
    },

    # ==========================================
    # DUNGEON 3: PICOS CONGELADOS (Nv 15-20)
    # ==========================================
    "lobo_de_gelo": {
        "nome": "Lobo de Gelo", "tipo": "comum",
        "hp": 900, "atk": 70, "def": 40, "matk": 0, "spd": 22, "crt": 15, "imagem": ""
    },
    "golem_de_gelo": {
        "nome": "Golem de Gelo", "tipo": "comum",
        "hp": 1200, "atk": 65, "def": 40, "matk": 0, "spd": 5, "crt": 5, "imagem": ""
    },
    "harpia": {
        "nome": "Harpia", "tipo": "comum",
        "hp": 1500, "atk": 80, "def": 50, "matk": 0, "spd": 30, "crt": 10, "imagem": ""
    },
    "serpente_glacial": {
        "nome": "Serpente Glacial", "tipo": "comum",
        "hp": 2000, "atk": 100, "def": 60, "matk": 0, "spd": 20, "crt": 20, "imagem": ""
    },
    "mago_de_gelo": {
        "nome": "Mago de Gelo", "tipo": "comum",
        "hp": 2100, "atk": 20, "def": 60, "matk": 150, "spd": 15, "crt": 10, "imagem": ""
    },
    # Mini-Bosses D3
    "urso_polar_gigante": {
        "nome": "Urso Polar Gigante", "tipo": "mini_boss",
        "hp": 1100, "atk": 120, "def": 55, "matk": 0, "spd": 10, "crt": 15, "imagem": ""
    },
    "harpia_rainha": {
        "nome": "Harpia Rainha", "tipo": "mini_boss",
        "hp": 1400, "atk": 130, "def": 60, "matk": 0, "spd": 35, "crt": 15,
        "habilidade": "congelar_dois_inimigos", "imagem": ""
    },
    "golem_de_gelo_ancestral": {
        "nome": "Golem de Gelo Ancestral", "tipo": "mini_boss",
        "hp": 2000, "atk": 190, "def": 110, "matk": 0, "spd": 5, "crt": 5,
        "habilidade": "stun_e_lentidao", "imagem": ""
    },
    "yeti_anciao": {
        "nome": "Yeti Ancião", "tipo": "mini_boss",
        "hp": 3000, "atk": 220, "def": 150, "matk": 0, "spd": 10, "crt": 25,
        "habilidade": "reduz_defesa_geral", "imagem": ""
    },
    # Boss Final D3
    "dragao_de_gelo": {
        "nome": "Dragão de Gelo", "tipo": "boss",
        "hp": 5000, "atk": 350, "def": 200, "matk": 300, "spd": 25, "crt": 20,
        "habilidade": "era_glacial", "imagem": ""
    },

    # ==========================================
    # DUNGEON 4: FORTALEZA DEMONÍACA (Nv 20-35)
    # ==========================================
    "demonio_menor": {
        "nome": "Demônio Menor", "tipo": "comum",
        "hp": 1500, "atk": 60, "def": 40, "matk": 0, "spd": 15, "crt": 5, "imagem": ""
    },
    "vampiro": {
        "nome": "Vampiro", "tipo": "comum",
        "hp": 1700, "atk": 65, "def": 40, "matk": 50, "spd": 25, "crt": 15, "imagem": ""
    },
    "demonio_medio": {
        "nome": "Demônio Médio", "tipo": "comum",
        "hp": 2000, "atk": 80, "def": 50, "matk": 0, "spd": 18, "crt": 10, "imagem": ""
    },
    "mago_infernal": {
        "nome": "Mago Infernal", "tipo": "comum",
        "hp": 3000, "atk": 30, "def": 60, "matk": 100, "spd": 15, "crt": 10, "imagem": ""
    },
    "vampiro_nobre": {
        "nome": "Vampiro Nobre", "tipo": "comum",
        "hp": 4000, "atk": 150, "def": 60, "matk": 100, "spd": 30, "crt": 20, "imagem": ""
    },
    # Mini-Bosses D4
    "cerberus": {
        "nome": "Cerberus", "tipo": "mini_boss",
        "hp": 2000, "atk": 200, "def": 150, "matk": 50, "spd": 25, "crt": 15,
        "habilidade": "tornado_de_fogo", "imagem": ""
    },
    "arquiduque_demonio": {
        "nome": "Arquiduque Demônio", "tipo": "mini_boss",
        "hp": 2500, "atk": 250, "def": 200, "matk": 0, "spd": 20, "crt": 20,
        "habilidade": "contrato_berserk", "imagem": ""
    },
    "lorde_vampiro": {
        "nome": "Lorde Vampiro", "tipo": "mini_boss",
        "hp": 3500, "atk": 300, "def": 300, "matk": 150, "spd": 40, "crt": 25,
        "habilidade": "sacrificio_de_sangue", "imagem": ""
    },
    "general_do_abismo": {
        "nome": "General do Abismo", "tipo": "mini_boss",
        "hp": 5000, "atk": 400, "def": 300, "matk": 0, "spd": 20, "crt": 15,
        "habilidade": "ignorar_defesa_explosao", "imagem": ""
    },
    # Boss Final D4
    "arquidemonio_belphegor": {
        "nome": "Arquidemônio Belphegor", "tipo": "boss",
        "hp": 10000, "atk": 500, "def": 500, "matk": 300, "spd": 40, "crt": 20,
        "habilidade": "bloqueio_de_habilidade", "imagem": ""
    },

    # ==========================================
    # DUNGEON 5: ABISMO DOS ECOS (Nv 35-50)
    # ==========================================
    "eco_corrompido": {
        "nome": "Eco Corrompido", "tipo": "comum",
        "hp": 5000, "atk": 130, "def": 90, "matk": 0, "spd": 20, "crt": 10, "imagem": ""
    },
    "cavaleiro_fantasma": {
        "nome": "Cavaleiro Fantasma", "tipo": "comum",
        "hp": 6000, "atk": 150, "def": 100, "matk": 0, "spd": 15, "crt": 15, "imagem": ""
    },
    "mago_espectral": {
        "nome": "Mago Espectral", "tipo": "comum",
        "hp": 7000, "atk": 50, "def": 110, "matk": 200, "spd": 18, "crt": 10, "imagem": ""
    },
    "assassino_de_ecos": {
        "nome": "Assassino de Ecos", "tipo": "comum",
        "hp": 10000, "atk": 500, "def": 150, "matk": 0, "spd": 60, "crt": 40, "imagem": ""
    },
    # Mini-Bosses D5
    "eco_do_heroi_caido": {
        "nome": "Eco do Herói Caído", "tipo": "mini_boss",
        "hp": 4000, "atk": 300, "def": 200, "matk": 0, "spd": 30, "crt": 20,
        "habilidade": "ignorar_matk", "imagem": ""
    },
    "eco_do_rei_sem_nome": {
        "nome": "Eco do Rei Sem Nome", "tipo": "mini_boss",
        "hp": 5000, "atk": 500, "def": 300, "matk": 0, "spd": 25, "crt": 25,
        "habilidade": "anular_atk", "imagem": ""
    },
    "eco_do_dragao_negro": {
        "nome": "Eco do Dragão Negro", "tipo": "mini_boss",
        "hp": 8500, "atk": 600, "def": 700, "matk": 400, "spd": 35, "crt": 20,
        "habilidade": "desintegracao", "imagem": ""
    },
    "eco_do_ultimo_sobrevivente": {
        "nome": "Eco do Último Sobrevivente", "tipo": "mini_boss",
        "hp": 12000, "atk": 1000, "def": 700, "matk": 0, "spd": 40, "crt": 30,
        "habilidade": "paralisia_em_massa", "imagem": ""
    },
    # Boss Final D5
    "a_testemunha": {
        "nome": "A Testemunha", "tipo": "boss",
        "hp": 20000, "atk": 1500, "def": 1000, "matk": 1000, "spd": 50, "crt": 25,
        "habilidade": "aetherion", "imagem": ""
    }
}