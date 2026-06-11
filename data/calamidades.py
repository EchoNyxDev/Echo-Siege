# ==========================================
# DICIONÁRIO DE RAIDS (INVASÕES À MURALHA)
# ==========================================
# Este arquivo contém os chefes de eventos globais.

RAID_BOSSES = {
    # ==========================================
    # BOSSES SEMANAIS (Aos Sábados)
    # ==========================================
    "goblin_xama_anciao_raid": {
        "nome": "Goblin Xamã Ancião (Invasão)", "tipo": "semanal",
        "hp": 100000, "atk": 500, "def": 800, "matk": 1500, "spd": 80, "crt": 10,
        "habilidade": "magia_em_massa",
        "imagem": ""
    },
    "goblin_berserk_raid": {
        "nome": "Goblin Berserk (Invasão)", "tipo": "semanal",
        "hp": 120000, "atk": 1800, "def": 600, "matk": 0, "spd": 90, "crt": 25,
        "habilidade": "furia_cega",
        "imagem": ""
    },
    "lobo_alfa_raid": {
        "nome": "Lobo Alfa (Invasão)", "tipo": "semanal",
        "hp": 110000, "atk": 1600, "def": 700, "matk": 0, "spd": 120, "crt": 20,
        "habilidade": "uivo_de_guerra",
        "imagem": ""
    },
    "rei_goblin_raid": {
        "nome": "Rei Goblin (Invasão)", "tipo": "semanal",
        "hp": 150000, "atk": 2000, "def": 1000, "matk": 0, "spd": 85, "crt": 15,
        "habilidade": "invocar_horda_goblin",
        "drops": {"adaga_do_rei": 5, "ticket_pet": 10},
        "imagem": ""
    },
    "cavaleiro_esqueleto_raid": {
        "nome": "Cavaleiro Esqueleto (Invasão)", "tipo": "semanal",
        "hp": 130000, "atk": 1700, "def": 1200, "matk": 0, "spd": 70, "crt": 10,
        "habilidade": "investida_mortal",
        "imagem": ""
    },
    "rei_sem_cabeca_raid": {
        "nome": "Rei Sem Cabeça (Invasão)", "tipo": "semanal",
        "hp": 160000, "atk": 1900, "def": 1300, "matk": 0, "spd": 75, "crt": 20,
        "habilidade": "dano_area_constante",
        "imagem": ""
    },
    "guardiao_da_cripta_raid": {
        "nome": "Guardião da Cripta (Invasão)", "tipo": "semanal",
        "hp": 180000, "atk": 2100, "def": 1400, "matk": 0, "spd": 60, "crt": 15,
        "habilidade": "prisao_das_almas",
        "imagem": ""
    },
    "harpia_rainha_raid": {
        "nome": "Harpia Rainha (Invasão)", "tipo": "semanal",
        "hp": 170000, "atk": 2000, "def": 1100, "matk": 0, "spd": 130, "crt": 15,
        "habilidade": "congelar_defensores",
        "imagem": ""
    },
    "golem_de_gelo_ancestral_raid": {
        "nome": "Golem de Gelo Ancestral (Invasão)", "tipo": "semanal",
        "hp": 220000, "atk": 2300, "def": 2500, "matk": 0, "spd": 40, "crt": 5,
        "habilidade": "terremoto_glacial",
        "imagem": ""
    },
    "yeti_anciao_raid": {
        "nome": "Yeti Ancião (Invasão)", "tipo": "semanal",
        "hp": 250000, "atk": 2400, "def": 2000, "matk": 0, "spd": 60, "crt": 25,
        "habilidade": "esmagar_muralha",
        "imagem": ""
    },
    "cerberus_raid": {
        "nome": "Cerberus (Invasão)", "tipo": "semanal",
        "hp": 240000, "atk": 2600, "def": 1800, "matk": 1000, "spd": 100, "crt": 15,
        "habilidade": "triplo_tornado_fogo",
        "imagem": ""
    },
    "arquiduque_demonio_raid": {
        "nome": "Arquiduque Demônio (Invasão)", "tipo": "semanal",
        "hp": 260000, "atk": 2800, "def": 2000, "matk": 1500, "spd": 90, "crt": 20,
        "habilidade": "contrato_infernal",
        "imagem": ""
    },
    "lorde_vampiro_raid": {
        "nome": "Lorde Vampiro (Invasão)", "tipo": "semanal",
        "hp": 280000, "atk": 3000, "def": 2200, "matk": 2500, "spd": 110, "crt": 25,
        "habilidade": "chuva_de_sangue",
        "imagem": ""
    },
    "eco_do_heroi_caido_raid": {
        "nome": "Eco do Herói Caído (Invasão)", "tipo": "semanal",
        "hp": 300000, "atk": 3200, "def": 2500, "matk": 0, "spd": 100, "crt": 20,
        "habilidade": "imunidade_magica",
        "imagem": ""
    },
    "eco_do_rei_sem_nome_raid": {
        "nome": "Eco do Rei Sem Nome (Invasão)", "tipo": "semanal",
        "hp": 320000, "atk": 3500, "def": 2600, "matk": 0, "spd": 95, "crt": 25,
        "habilidade": "silenciar_defensores",
        "imagem": ""
    },
    "eco_do_ultimo_sobrevivente_raid": {
        "nome": "Eco do Últ. Sobrevivente (Invasão)", "tipo": "semanal",
        "hp": 350000, "atk": 4000, "def": 2800, "matk": 0, "spd": 110, "crt": 30,
        "habilidade": "paralisia_global",
        "imagem": ""
    },

    # ==========================================
    # CALAMIDADES MENSAIS (Último dia do Mês)
    # ==========================================
    "dragao_do_caos": {
        "nome": "Dragão do Caos", "tipo": "mensal",
        "hp": 1000000, "atk": 5000, "def": 2500, "matk": 2000, "spd": 150, "crt": 20,
        "habilidades": ["sopro_do_caos", "tempestade_carmesim", "fim_dos_tempos"],
        "drops": {"escamas_de_dragao": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511017969457561734/08ade26edaa13c2d4280aa9e40801bea.jpg?ex=6a22e125&is=6a218fa5&hm=d0b35ed47a3c46d01a46a969e4bcfde296b3d424e9944e44d6ce2c78dc7e4478&"
    },
    "basilisco": {
        "nome": "Basilisco, o Rei das Serpentes", "tipo": "mensal",
        "hp": 400000, "atk": 3000, "def": 3500, "matk": 1000, "spd": 120, "crt": 10,
        "habilidades": ["olhar_petrificante", "veneno_ancestral", "pele_de_pedra"],
        "drops": {"olhos_de_serpente": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511018199901016064/bf963fe8191a261f24fca4f2e687a56b.jpg?ex=6a22e15c&is=6a218fdc&hm=646b2dcee73ea86ba42b06d0ae9f5df88dfef7e9ea5c3a1be6d7fe79edce5edd&"
    },
    "baku": {
        "nome": "Baku, o Comandante dos Pesadelos", "tipo": "mensal",
        "hp": 350000, "atk": 2000, "def": 2000, "matk": 3000, "spd": 110, "crt": 5,
        "habilidades": ["pesadelo_vivo", "sono_eterno", "devorador_de_sonhos"],
        "drops": {"boneco_amaldicoado": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511039621461708942/50ddfa68afdc12925fbd2fb3140fe8f7.jpg?ex=6a22f54f&is=6a21a3cf&hm=5d65e4d86f47df359755ec2ea3ff349b19ef53767af67e9423e01c2d92c97b9b&"
    },
    "ainsumonsuta": {
        "nome": "Ainsumonsutã, o Terror Glacial", "tipo": "mensal",
        "hp": 700000, "atk": 4000, "def": 5000, "matk": 3500, "spd": 90, "crt": 0,
        "habilidades": ["era_glacial", "tempestade_de_gelo", "coracao_congelado"],
        "drops": {"cetro_do_inverno": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511039886499643463/2e00a16b9c07c2364bcfce2c9b8e8f90.jpg?ex=6a22f58e&is=6a21a40e&hm=61f8b5d5a6c74f28dafbcfe772dad44a69e2bf6882afcab095093c165fdbcefa&"
    },
    "licht": {
        "nome": "Licht, o Rei Feiticeiro", "tipo": "mensal",
        "hp": 450000, "atk": 500, "def": 2500, "matk": 3500, "spd": 140, "crt": 15,
        "habilidades": ["necromancia_suprema", "toque_da_morte", "imunidade_fisica"],
        "drops": {"marca_do_invocador": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511040118364831825/c580360291fb96de08531326221e8f13.jpg?ex=6a22f5c5&is=6a21a445&hm=fa7ca8a3f25a15ea9ee22ba5c1b2ba51897c42e56d49040701e9553fe9db23a5&"
    },
    "lucifero": {
        "nome": "Lucifero, o Demônio da Espada", "tipo": "mensal",
        "hp": 300000, "atk": 8000, "def": 1500, "matk": 0, "spd": 180, "crt": 40,
        "habilidades": ["corte_dimensional", "mil_espadas", "forma_demoniaca"],
        "drops": {"espada_demoniaca": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511040319628640306/905bd75b0a733884917219d42cfc3e08.jpg?ex=6a22f5f5&is=6a21a475&hm=b3f31cdd5919f90f95d4f4947e84ec7c109de92ddacf2e0cddbe4d26115e4de6&"
    },
    "dantalian": {
        "nome": "Dantalian, o Demônio do Conhecimento", "tipo": "mensal",
        "hp": 550000, "atk": 3000, "def": 4000, "matk": 3000, "spd": 130, "crt": 10,
        "habilidades": ["biblioteca_proibida", "conhecimento_absoluto", "tomo_da_verdade"],
        "drops": {"tomo_do_conhecimento": 2},
        "imagem": "https://cdn.discordapp.com/attachments/1510866855378813060/1511040582548721894/33240a230951e2c45430b3e4f9551063.jpg?ex=6a22f634&is=6a21a4b4&hm=7a85cb844ec22216d8d1265654469d9c394c52b021a8f90e0f937b6e6e033e8a&"
    }
}