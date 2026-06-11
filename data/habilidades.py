# ==========================================
# DICIONÁRIO MESTRE DE HABILIDADES TÁTICAS
# ==========================================
# Este arquivo dita a matemática do novo sistema de combate.
# Tipos: dano, cura, buff, debuff, passiva, escudo, provocar, insta_kill, especial, invocacao

SKILLS = {
    # ==========================================
    # HERÓIS - DPS / ATACANTES / MAGOS (Clássicos)
    # ==========================================
    "ataque_giratorio": {"nome": "Ataque Giratório", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_hit": 2}},
    "ataque_descomunal": {"nome": "Ataque Descomunal", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 10}},
    "berserk_levi": {"nome": "Berserk", "tipo": "especial", "alvo": "self", "efeito": {"buff_atk": 30, "buff_spd": 20, "imortalidade_turnos": 3}},
    
    "furacao_da_folha": {"nome": "Furacão da Folha", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 15}},
    "lotus_oculta": {"nome": "Lótus Oculta", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 30}},
    "oito_portoes": {"nome": "8 Portões", "tipo": "especial", "alvo": "self", "efeito": {"buff_atk": 30, "buff_spd": 30, "turnos": 2, "pos_efeito": "stun"}},
    
    "santoryuu": {"nome": "Santoryuu", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_hit": 3}},
    "ashura": {"nome": "Ashura", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_hit": 9}},
    
    "star_platinum": {"nome": "Star Platinum", "tipo": "passiva", "alvo": "self", "efeito": {"chance_ataque_duplo": 0.25}},
    "o_mundo": {"nome": "O Mundo", "tipo": "especial", "alvo": "self", "efeito": {"parar_tempo": True, "anular_habilidade_contra_si": 1}},
    
    "dual_blade": {"nome": "Dual Blade", "tipo": "buff", "alvo": "self", "efeito": {"multiplicador_dano_atk": 2.0}},
    "privilegios_adm": {"nome": "Privilégios de Administrador", "tipo": "escudo", "alvo": "aliado_escolhido", "efeito": {"imunidade_dano_turnos": 5}},
    
    "sopro_de_fogo": {"nome": "Sopro de Fogo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_matk_extra": 35, "dot": {"tipo": "fogo", "dano_matk": 10, "turnos": 2}}},
    "lotus_chama_explosiva": {"nome": "Lótus de Lâminas", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_matk_extra": 50}},
    "dragon_force": {"nome": "Dragon Force", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30, "duracao": "combate_inteiro"}},
    
    "explosion": {"nome": "Explosion", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_matk_extra": 50}, "cooldown": 3},
    "explosion_plus": {"nome": "Explosion+", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_matk_extra": 60}, "cooldown": 2},
    "explosion_plus_plus": {"nome": "Explosion++", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_matk_extra": 80}, "uso_maximo": 1},
    
    "disparo_de_mana": {"nome": "Disparo de Mana", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_matk_extra": 20}},
    "zoltraak": {"nome": "Zoltraak", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"ignora_def": True, "dano_matk_extra": 50, "buff_crt": 20}},
    
    "azul_e_vermelho": {"nome": "Azul e Vermelho", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"agrupar_inimigos": True, "dano_matk_extra": 40}},
    "roxo": {"nome": "Roxo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_matk_extra": 60, "chance_insta_kill": 0.10}},
    
    "fallen_down": {"nome": "Fallen Down", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_matk_extra": 80}},
    "grasp_heart": {"nome": "Grasp Heart", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"chance_insta_kill": 0.30}},
    
    "convergencia": {"nome": "Convergência", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_matk_extra": 40, "chance_stun": 0.25, "stun_turnos": 1}},
    "desmantelar": {"nome": "Desmantelar", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_atk_extra": 40}},

    # ==========================================
    # HERÓIS - SUPORTES E CURANDEIROS (Clássicos)
    # ==========================================
    "cura_chopper": {"nome": "Cura", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_fixa": 20}},
    "rumble_ball": {"nome": "Rumble Ball", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 20, "buff_def": 20}},
    "cura_maxima": {"nome": "Cura Máxima", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_fixa": 40}},
    
    "palma_mistica": {"nome": "Técnica da Palma Mística", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_fixa": 50}},
    "kuchiyose_katsuyu": {"nome": "Kuchiyose", "tipo": "invocacao", "alvo": "campo", "efeito": {"cura_turnos": 20}},
    "criacao_renascimento": {"nome": "Criação do Renascimento", "tipo": "reviver", "alvo": "aliado_morto", "efeito": {"chance_reviver": 0.20, "hp_percent": 0.50}},
    
    "enchantment": {"nome": "Enchantment", "tipo": "buff", "alvo": "unico_aliado", "efeito": {"escolha_buff": {"atk": 20, "matk": 20}}},
    "high_enchanter": {"nome": "High Enchanter", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"escolha_buff": {"atk": 35, "matk": 35}, "buff_def_dps": 20}},
    
    "alto_perdao": {"nome": "Alto Perdão", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 0.50}},
    "reviver_elizabeth": {"nome": "Reviver", "tipo": "reviver", "alvo": "aliado_morto", "efeito": {"hp_percent": 1.0}, "uso_maximo": 1},
    
    "koten_zanshun": {"nome": "Koten Zanshun", "tipo": "escudo", "alvo": "unico_aliado", "efeito": {"imunidade_dano_turnos": 2}},
    "soten_kisshun": {"nome": "Sōten Kisshun", "tipo": "escudo", "alvo": "dps_aliados", "quantidade": 3, "efeito": {"imunidade_dano_turnos": 2, "buff_def_global": 30}},

    # ==========================================
    # HERÓIS - TANKS E DEFESA (Clássicos)
    # ==========================================
    "alquimia_def": {"nome": "Alquimia", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 20}},
    "invulnerabilidade_bio": {"nome": "Invulnerabilidade Biológica", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp": 20, "buff_def": 25}},
    "transmutacao": {"nome": "Transmutação", "tipo": "especial", "alvo": "self", "efeito": {"converte_atk_matk_para_def": True, "def_bonus": 10}},
    
    "cristalizacao": {"nome": "Cristalização", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 25, "buff_hp": 25}},
    "tita": {"nome": "Titã", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 15}},
    "tita_cristalizacao": {"nome": "Titã + Cristalização", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 20, "buff_hp": 30}},
    
    "bebado_oito_trigramas": {"nome": "Bêbado de 8 Trigramas", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 50, "imortalidade_turnos": 1}},
    "forma_hibrida": {"nome": "Forma Híbrida", "tipo": "especial", "alvo": "self", "efeito": {"ignora_dano_fisico": True, "turnos": 5}},
    
    "regeneracao_koku": {"nome": "Regeneração", "tipo": "passiva", "alvo": "self", "efeito": {"cura_turnos": 20, "imune_dano_fisico": True}},
    "marca_cacador": {"nome": "Marca do Caçador", "tipo": "passiva", "alvo": "self", "efeito": {"buff_spd": 30, "cura_turnos": 35, "imune_dano_fisico": True, "vulneravel_apenas_matk_massivo": True}},
    
    "absorcao": {"nome": "Absorção", "tipo": "escudo", "alvo": "self", "efeito": {"absorver_dano_refletir": 1.0}},
    "modo_divino": {"nome": "Modo Divino", "tipo": "especial", "alvo": "self", "efeito": {"cura_turnos": 40, "absorver_ultimate_refletir": 2.0}},

    # ==========================================
    # HERÓIS - TÁTICOS E PASSIVAS ABSURDAS (Clássicos)
    # ==========================================
    "inspiracao": {"nome": "Inspiração", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 10, "buff_atk": 10, "buff_matk": 10}},
    "discurso_motivacional": {"nome": "Discurso Motivacional", "tipo": "buff", "alvo": "unico_aliado", "efeito": {"buff_geral": 20}},
    "sacrificio_erwin": {"nome": "Sacrifício", "tipo": "passiva", "alvo": "dps_aliado", "condicao": "hp_dps_critico", "efeito": {"transferir_hp_para_dps": True, "morre_no_processo": True}},
    
    "estrategista": {"nome": "Estrategista", "tipo": "passiva", "alvo": "campo", "efeito": {"debuff_precisao_inimiga": 0.20, "buff_precisao_aliada": 0.20}},
    "escriba": {"nome": "Escriba", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"ignora_ataque_basico_turnos": 2}},
    "full_control_encounter": {"nome": "Full Control Encounter", "tipo": "debuff", "alvo": "campo", "efeito": {"debuff_spd_inimiga": 20, "imunidade_aliados_turnos": 3}},
    
    "geass": {"nome": "Geass", "tipo": "especial", "alvo": "aleatorio", "efeito": {"escolha": {"reviver_aliado": True, "chance_insta_kill_inimigo": 0.25}}},
    "geass_plus": {"nome": "Geass+", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"reviver_aliados": 2, "imunidade_enquanto_vivo": True}},
    
    "kyoka_suigetsu": {"nome": "Kyoka Suigetsu", "tipo": "invocacao", "alvo": "campo", "efeito": {"clona_dps_atributos": True, "hp_fixo": 30}},
    "hipnose_completa": {"nome": "Hipnose Completa", "tipo": "invocacao", "alvo": "campo", "efeito": {"clona_dps_perfeito": True, "imune_a_dano": True, "morre_se_dps_morrer": True}},
    
    "belzebu": {"nome": "Belzebu", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"absorve_atk_converte_cura": True}},
    "ciel": {"nome": "Ciel", "tipo": "especial", "alvo": "campo", "efeito": {"adaptativo": True, "cura_50_se_low_hp": True, "execute_se_inimigo_abaixo_20": True, "buff_atk_def_30_se_inimigo_full": True}},

    # ==========================================
    # HERÓIS - ASSASSINOS E ATIRADORES (Clássicos)
    # ==========================================
    "linhas_de_sanzu": {"nome": "Linhas de Sanzu", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 20}},
    "disparo_sincronizado": {"nome": "Disparo Sincronizado", "tipo": "dano", "alvo": "inimigos_maior_dano", "quantidade": 2, "efeito": {"dano_atk_extra": 30}},
    "loucura_da_ordem": {"nome": "Loucura da Ordem", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 20, "buff_spd": 10, "critico_garantido": True}},
    
    "sniper": {"nome": "Sniper", "tipo": "dano", "alvo": "inimigo_maior_dano", "efeito": {"dano_atk_extra": 40}},
    "xeque_mate": {"nome": "Xeque-Mate", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_massivo": True, "critico_garantido": True}},
    "hell_snipe": {"nome": "Hell Snipe", "tipo": "insta_kill", "alvo": "inimigo_aleatorio", "efeito": {"chance_insta_kill": 1.0}},
    
    "pumpkin": {"nome": "Pumpkin", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_atk_extra": 30, "dobro_dano_aereos": True}},
    "ultimate_pumpkin": {"nome": "Ultimate Pumpkin", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0}},
    
    "heilig_bogen": {"nome": "Heilig Bogen", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"ignora_def": True}},
    "antitese": {"nome": "Antítese", "tipo": "especial", "alvo": "inimigos_travados", "quantidade": 2, "efeito": {"redireciona_dano_ignora_def_regen": True, "duracao": "combate_inteiro"}},
    
    "angel_wings": {"nome": "Angel Wings", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 3.0}},
    "manipulacao_gravitacional": {"nome": "Manip. Gravitacional", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"chance_insta_kill": 0.50}, "uso_maximo": 1},

    "yandere": {"nome": "Yandere", "tipo": "passiva", "alvo": "self", "condicao": "dps_ferido", "efeito": {"buff_atk_contra_agressor": 20}},
    "intencao_assassina": {"nome": "Intenção Assassina", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"reduz_spd_zero": True, "stun_turnos": 1}},
    "querido_diario": {"nome": "Querido Diário", "tipo": "especial", "alvo": "dps_aliado", "efeito": {"marca_dps_redireciona_dano_self": True, "transfere_atk_para_dps": True}},

    "assassinato": {"nome": "Assassinato", "tipo": "buff", "alvo": "self", "efeito": {"foca_menor_hp": True, "buff_crt": 20}},
    "assassinato_plus": {"nome": "Assassinato+", "tipo": "dano", "alvo": "inimigo_menor_hp", "efeito": {"dano_atk_extra": 30}},
    "death_strike": {"nome": "Death Strike", "tipo": "especial", "alvo": "inimigo_menor_def", "efeito": {"corta_hp_metade": True, "insta_kill_se_hp_menor_50": True}},
    
    "coagulacao": {"nome": "Coagulação", "tipo": "debuff", "alvo": "inimigo_aleatorio", "efeito": {"stun_turnos": 3, "ignora_def_alvo": True}},
    "coagulacao_plus": {"nome": "Coagulação+", "tipo": "debuff", "alvo": "dps_inimigo", "efeito": {"stun_turnos": 3, "ignora_def_alvo": True}},
    
    "prisao_de_agua": {"nome": "Prisão de Água", "tipo": "especial", "alvo": "inimigo_aleatorio", "efeito": {"trava_x1_ate_morte": True}},
    "clone_de_agua": {"nome": "Clone de Água", "tipo": "invocacao", "alvo": "campo", "efeito": {"clona_self": True, "hp_percent": 0.50}},
    
    "muramasa": {"nome": "Muramasa", "tipo": "passiva", "alvo": "self", "efeito": {"chance_insta_kill_on_hit": 0.10}},
    "lamina_carmesim": {"nome": "Lâmina Carmesim", "tipo": "especial", "alvo": "self", "efeito": {"insta_kill_on_hit_garantido": True, "morre_apos_turnos": 3}},
    
    "eletro_wave": {"nome": "Eletro-Wave", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 40, "stun_turnos": 2}},
    "godspeed": {"nome": "Godspeed", "tipo": "buff", "alvo": "self", "efeito": {"multiplica_spd": 2.0}},
    
    "mana_zone": {"nome": "Mana Zone", "tipo": "passiva", "alvo": "self", "efeito": {"dano_fogo_extra": 30, "dot_fogo": 10}},
    "encarnacao_fogo": {"nome": "Encarnação do Fogo do Inferno", "tipo": "passiva", "alvo": "self", "condicao": "morte", "efeito": {"reviver_100_hp": True, "multiplica_atk_matk": 2.0, "debuff_def_inimigos": 20}, "uso_maximo": 1},


    # ==========================================
    # NOVAS HABILIDADES: MUNDO E DESAFIOS (EXPANSÃO)
    # ==========================================
    
    "telecinese_mob": {"nome": "Telecinese", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30}},
    "modo_cem_porcento": {"nome": "100%", "tipo": "especial", "alvo": "self", "efeito": {"buff_matk": 50, "imortalidade_turnos": 3, "duracao": "combate_inteiro"}},
    
    "jinki": {"nome": "Jinki", "tipo": "especial", "alvo": "item_contra_si", "efeito": {"melhora_item_usado": 0.50}},
    "jinki_plus": {"nome": "Jinki+", "tipo": "especial", "alvo": "item_contra_si", "efeito": {"melhora_item_usado": 1.00}},
    
    "retorno_morte": {"nome": "Retorno Através da Morte", "tipo": "passiva", "alvo": "self", "condicao": "morte", "efeito": {"reviver_infinito_se_aliado_vivo": True}},
    "contrato_espiritual_subaru": {"nome": "Contrato Espiritual (Beatrice)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 30, "buff_atk": 20, "buff_matk": 20}},
    "autoridades_subaru": {"nome": "Cor Leonis / Providência", "tipo": "especial", "alvo": "adaptativo", "efeito": {"se_defesa": {"compartilha_dano_aliado_reduz_25": True}, "se_ataque": {"dano_matk_extra": 30, "acerto_garantido": True, "ignora_def": True}}},
    
    "contrato_makima": {"nome": "Contrato", "tipo": "passiva", "alvo": "dps_aliado", "condicao": "morte_dps", "efeito": {"insta_kill_inimigo_aleatorio": True}},
    "demonio_do_controle": {"nome": "Demônio do Controle", "tipo": "especial", "alvo": "dps_inimigo", "efeito": {"sacrifica_dps_aliado_para_matar_dps_inimigo": True}},
    
    "restricao_celestial": {"nome": "Restrição Celestial", "tipo": "passiva", "alvo": "self", "efeito": {"debuff_dano_magico_sofrido": 1.10, "buff_atk": 20, "buff_spd": 25, "primeiro_hit_critico": True}},
    "zero_restricao": {"nome": "Zero Restrição", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 30}},
    
    "rabbit": {"nome": "Rabbit", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 30, "buff_def": 30}},
    "rabbit_plus": {"nome": "Rabbit+", "tipo": "passiva", "alvo": "self", "efeito": {"imunidade_dano_fisico": True}},
    
    "magia_de_gelo": {"nome": "Magia de Gelo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_matk_extra": 40, "debuff_spd": 10}},
    "contrato_espiritual_emilia": {"nome": "Contrato Espiritual (Puck)", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30, "chance_stun": 0.25, "stun_turnos": 2}},
    
    "chainsaw_man": {"nome": "Chainsaw Man", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 30, "dot": {"tipo": "sangramento", "dano_atk": 30, "turnos": 3}}},
    "forma_verdadeira_denji": {"nome": "Forma Verdadeira", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "dano_atk_extra": 20, "ignora_def": True, "lifesteal": 0.40}},
    
    "anti_magia": {"nome": "Anti-Magia", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"remove_buffs": 2, "anula_magia_passiva": True}},
    "forma_demoniaca_asta": {"nome": "Forma Demoníaca", "tipo": "buff", "alvo": "self", "efeito": {"ignora_escudos_geral": True, "buff_spd": 30, "buff_atk": 50}},
    
    "cavaleiro_rei": {"nome": "Cavaleiro Rei", "tipo": "passiva", "alvo": "self", "efeito": {"buff_atk_por_hp_perdido": 2}},
    "excalibur": {"nome": "Excalibur", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_massivo_hp_max": True, "ignora_def": True, "chance_insta_kill_hp_baixo": 0.40}},
    
    "triceratops_fist": {"nome": "Triceratops Fist", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 20, "debuff_def": 15}},
    "whip_strike": {"nome": "Whip Strike", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"dano_fisico": True}},
    "demon_back": {"nome": "Demon Back", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_cc": True, "buff_atk": 30, "buff_def": 20, "turnos": 2}},
    
    "marca_demoniaca": {"nome": "Marca Demoníaca", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 35, "turnos": 3}},
    "assault_mode": {"nome": "Assault Mode", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 40, "roubo_de_atk": 15}},
    "demon_king_form": {"nome": "Demon King Form", "tipo": "buff", "alvo": "self", "efeito": {"cura_percent_max": 0.50, "buff_def": 20, "buff_spd": 20, "ignora_def_passiva": True}},
    
    "combate_desarmado": {"nome": "Combate Desarmado", "tipo": "buff", "alvo": "self", "efeito": {"buff_dodge": 15, "turnos": 2, "loot_bonus": 20}},
    "luta_adagas": {"nome": "Luta com Adagas", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"multiplicador_atk": 1.2}},
    "sem_inimigos": {"nome": "Eu Não Tenho Inimigos", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"remove_debuffs": True, "reducao_dano_recebido": 40, "turnos": 2}},
    
    "sunshine": {"nome": "Sunshine", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"soma_atk_matk": True, "buff_dano_por_turno": 20, "acumulo_max": 5}},
    "the_one_ultimate": {"nome": "The One Ultimate", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"ignora_def": True, "multiplicador_soma_atk_matk": 2.0, "imortalidade_turnos": 1, "self_dmg_pos_turno": 0.25}},
    
    "dragon_slayer_guts": {"nome": "Dragon Slayer", "tipo": "dano", "alvo": "campo", "quantidade": 3, "efeito": {"soma_atk_matk": True}},
    "armadura_berserker": {"nome": "Armadura Berserker", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp_temporario": 100, "buff_atk": 60, "buff_spd": 15, "buff_def": 30, "dot_self": 5}},
    
    "magia_trevas_yami": {"nome": "Magia das Trevas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"soma_atk_matk": True, "debuff_precisao": 20}},
    "corte_dimensional": {"nome": "Corte Dimensional", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"soma_atk_matk_buff": 50, "ignora_def_escudos": True, "acerto_garantido": True, "chance_ruptura": 0.25}},
    
    "hollow_form": {"nome": "Hollow Form", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 40, "buff_atk": 50, "turnos": 3}},
    "true_bankai": {"nome": "True Bankai", "tipo": "buff", "alvo": "self", "efeito": {"critico_garantido_1_hit": True, "dobra_atk": True, "turno_extra_ao_matar": True}},
    
    "socos_normais": {"nome": "Golpes Normais Consecutivos", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 5, "efeito": {"multiplicador_atk": 1.0, "bonus_crit_hit": 10}},
    "soco_serio": {"nome": "Soco Sério", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 5.0, "ignora_tudo": True, "stun_se_vivo": 2}},

    "copia_individualidade": {"nome": "Cópia de Individualidade", "tipo": "especial", "alvo": "inimigo_aleatorio", "efeito": {"copia_skill": True}},
    "transformacao_toga": {"nome": "Transformação Completa", "tipo": "especial", "alvo": "inimigo_aleatorio", "efeito": {"copia_tudo": True}},
    
    "olhos_favorecem": {"nome": "Olhos que Favorecem", "tipo": "passiva", "alvo": "self", "efeito": {"buff_spd": 20, "buff_crt": 30}},
    "projecao_memorias": {"nome": "Projeção de Memórias", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"imune_dano_1_turno": True, "dano_dobrado_prox_hit": True}},
    "comunicacao_espiritual": {"nome": "Comunicação Espiritual", "tipo": "invocacao", "alvo": "campo", "efeito": {"dano_automatico": True, "cura_menor_hp_fim_turno": True, "turnos": 3}},
    
    "ambidestria": {"nome": "Ambidestria", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"multiplicador_atk": 1.2, "crit_independente": True}},
    "pontaria_incomparavel": {"nome": "Pontaria Incomparável", "tipo": "passiva", "alvo": "self", "efeito": {"buff_crt": 40, "ignora_def_25": True, "acerto_garantido": True}},
    "arsenal_revy": {"nome": "Arsenal de Escolha", "tipo": "especial", "alvo": "adaptativo", "efeito": {"escolha_municao": True}},
    
    "respiracao_flor": {"nome": "Respiração da Flor", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 10, "buff_atk": 20, "aplica_veneno_on_hit": 20, "turno_parcial_on_crit": True}},
    "olhos_escarlates": {"nome": "Olhos Escarlates Equinocial", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"critico_garantido": True, "ignora_def": 50, "veneno_pesado": 2.0}},
    
    "proteses_mortais": {"nome": "Próteses Mortais", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"dano_fixo": 25, "dano_matk_extra": 0, "chance_bleed": 0.25}},
    "modo_berserk_hyakkimaru": {"nome": "Modo Berserk", "tipo": "buff", "alvo": "self", "efeito": {"lifesteal_on_hit": True, "buff_atk": 40, "buff_spd": 20, "turnos": 3}},
    
    "restricao_celestial_completa": {"nome": "Restrição Celestial (Completa)", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_magica": True, "buff_atk": 30, "buff_spd": 30, "turnos": 3}},
    "cacador_imparavel": {"nome": "Caçador Imparável", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_atk_extra": 50, "ignora_def_e_shield": 50, "turno_extra_ao_matar": True}},

    "criocinese_extrema": {"nome": "Criocinese Extrema", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"soma_atk_matk": True, "stun_turnos": 2, "debuff_spd_global": 50}},
    "mahapadma": {"nome": "Mahapadma", "tipo": "especial", "alvo": "campo", "efeito": {"stun_turnos_global": 1, "debuff_fraqueza": 20, "intocavel_turnos": 2}},
    
    "shadow_garden": {"nome": "Shadow Garden", "tipo": "buff", "alvo": "self", "efeito": {"intocavel_turnos": 2, "proximo_ataque_dobrado": True}},
    "i_am_atomic": {"nome": "I Am Atomic", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_soma_atk_matk": 3.0, "ignora_def_escudos": True, "critico_garantido": True, "stun_turnos": 1}},
    
    "surgir": {"nome": "Surgir!", "tipo": "invocacao", "alvo": "campo", "efeito": {"invoca_sombras": 2, "hp_percent_sombras": 0.50, "taunt_sombras": True}},
    "monarca_sombras": {"nome": "Monarca das Sombras", "tipo": "invocacao", "alvo": "campo", "efeito": {"invoca_generais": 3, "revive_self_dobrado": 2}},
    
    "star_dress": {"nome": "Star Dress", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30, "buff_def": 20, "turnos": 5}},
    "urano_metria": {"nome": "Urano Metria", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_matk_extra": 50, "debuff_matk": 25}},
    
    "magia_agua_roxy": {"nome": "Magia de Água King-Tier", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 20, "chance_lentidao_on_hit": 0.20}},
    "lamina_agua": {"nome": "Lâmina de Água", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"multiplicador_matk": 1.0, "bonus_crit_hit": 15}},
    "canhao_agua": {"nome": "Canhão de Água Comprimido", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.8, "ignora_def_magica": 30, "debuff_spd": 20}},
    
    "magia_sagrada_shuna": {"nome": "Magia Sagrada", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.5, "dano_bonus_undead": True}},
    "devocao_protetora": {"nome": "Devoção Protetora", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"remove_debuffs": True, "buff_def": 30}},
    "expurgo_almas": {"nome": "Expurgo das Almas", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "remove_buffs_inimigos": True}},
    
    "chrono_anastasis": {"nome": "Magia de Tempo: Chrono Anastasis", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.2, "debuff_spd": 50}},
    "capsula_tempo": {"nome": "Cápsula do Tempo", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"stun_turnos": 2, "ignora_imunidade_cc": True}},

    # ==========================================
    # NOVAS HABILIDADES: MUNDO E DESAFIOS (EXPANSÃO)
    # ==========================================
    "infinity": {"nome": "Infinity", "tipo": "especial", "alvo": "campo", "efeito": {"estende_buffs_aliados": 2, "estende_debuffs_inimigos": 2}},
    "absolute_cancel": {"nome": "Absolute Cancel", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.0, "remove_todos_buffs": True, "remove_todos_debuffs_aliados": True}},
    
    "olhos_magicos_destruicao": {"nome": "Olhos Mágicos da Destruição", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 3.0, "ignora_def": True, "destroi_escudos": True}},
    "espada_razao_venuzdnor": {"nome": "Espada da Razão Venuzdnor", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"dano_hp_atual": 0.70, "ignora_invulnerabilidade": True, "critico_garantido": True, "executa_abaixo_50": True}},
    
    "gate_of_babylon": {"nome": "Gate of Babylon", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 6, "efeito": {"soma_atk_matk_100": True, "chance_reduzir_def": 0.20}},
    "enuma_elish": {"nome": "Enuma Elish (EA)", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 6.0, "ignora_imortalidade": True, "debuff_spd": 50, "debuff_def": 50, "turnos": 2}},
    
    "analise_estrategica": {"nome": "Análise Estratégica", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_crt": 20, "buff_acc": 20, "turnos": 3}},
    "pesquisa_campo": {"nome": "Pesquisa de Campo", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"aplica_fraqueza": 25, "turnos": 3}},
    "mobilidade_dmt_avancada": {"nome": "Mobilidade DMT Avançada", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 50, "buff_crt": 50, "buff_atk": 50, "buff_atk_aliados": 30, "turnos": 3}},
    
    "kekkijutsu_cura": {"nome": "Kekkijutsu de Cura", "tipo": "cura", "alvo": "unico_aliado", "efeito": {"multiplicador_matk": 2.5, "remove_veneno_burn_bleed": True}},
    "explosao_sangue_definitiva": {"nome": "Explosão de Sangue Definitiva", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 3.0, "remove_todos_debuffs": True, "regeneracao_hp": 10, "turnos": 3}},
    
    "espada_do_heroi": {"nome": "A Espada do Herói", "tipo": "buff", "alvo": "lider_aliado", "efeito": {"buff_atk": 35, "buff_matk": 35, "buff_spd": 20, "turnos": 3}},
    "evolucao_vinculo": {"nome": "Evolução do Vínculo", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 30, "buff_def": 30, "buff_spd": 30, "turnos": 3, "buff_xp_lider": 50}},
    
    "energia_amaldicoada_reversa": {"nome": "Energia Amaldiçoada Reversa", "tipo": "cura", "alvo": "unico_aliado", "efeito": {"multiplicador_matk": 3.0}},
    "autopsia_forense": {"nome": "Autópsia Forense", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_def": 30, "reduz_regen": 50, "turnos": 3}},
    "talento_especial_cura": {"nome": "Talento Especial de Cura", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 4.0, "remove_debuffs_pesados": True, "cura_self_20_percent": True}},
    
    "ressurreicao_divina": {"nome": "Ressurreição Divina", "tipo": "reviver", "alvo": "aliado_morto", "efeito": {"hp_percent": 0.50}, "uso_maximo": 1},
    "dispersao_sagrada": {"nome": "Dispersão Sagrada / Turn Undead", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "cura_percent_max_time": 0.25, "remove_debuffs_magicos": True}},
    
    "shikai_chiasumi": {"nome": "Shikai: Chiasumi no Tate", "tipo": "escudo", "alvo": "unico_aliado", "efeito": {"escudo_hp_max": 0.50}},
    "bankai_benihime": {"nome": "Bankai: Kannonbiraki Benihime Aratame", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 1.0, "remove_debuffs": True, "reviver_mortos_hp": 0.50}},
    
    "mestra_venenos": {"nome": "Mestra dos Venenos", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"dot_matk": 200, "turnos": 2, "corta_cura": 50, "imune_toxinas": True}},
    "boticaria_alto_calao": {"nome": "Boticária de Alto Calão (Toxic)", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"dot_matk": 250, "turnos": 3, "lentidao": True, "fraqueza": True, "anti_cura": True, "buff_dano_aliados": 20}},
    
    "esquiva_pequeno_rei": {"nome": "Esquiva do Pequeno Rei", "tipo": "buff", "alvo": "self", "efeito": {"aggro_max": True, "buff_spd": 40, "turnos": 3}},
    "agilidade_divina": {"nome": "Agilidade Divina", "tipo": "passiva", "alvo": "self", "efeito": {"dodge": 60, "age_primeiro": True, "counter_atk_percent": 1.50}},
    "separacao_molecular": {"nome": "Golpe de Separação Molecular", "tipo": "buff", "alvo": "self", "efeito": {"dodge": 100, "turnos": 2, "dodge_permanente_apos": 50}},
    
    "magia_musculos": {"nome": "Magia dos Músculos", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 40, "buff_hp_max": 25, "reflete_dano": 25}},
    "hora_profiterole": {"nome": "Hora do Profiterole", "tipo": "cura", "alvo": "self", "efeito": {"cura_percent_max": 0.40, "buff_def": 40, "buff_atk": 40, "turnos": 3}},
    
    "endurecer_kirishima": {"nome": "Endurecer (Hardening)", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 60, "reflete_dano": 25}},
    "red_counter": {"nome": "Red Counter", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 100, "aggro_max": True, "reflete_dano": 30}},
    "red_riot_unbreakable": {"nome": "Red Riot Unbreakable", "tipo": "buff", "alvo": "self", "efeito": {"reduz_dano_recebido": 90, "ignora_criticos": True, "protege_aliados_fatal": True, "turnos": 3}},
    
    "escudo_ira": {"nome": "Escudo da Ira", "tipo": "especial", "alvo": "self", "efeito": {"aggro_max": True, "escudo_hp_max": 0.50, "counter_matk_percent": 2.0}},
    "armadura_imperador_dragao": {"nome": "Armadura do Imperador Dragão", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 100, "escudo_hp_max": 0.50, "reflete_dano": 40, "regen_hp": 10}},
    
    "evolucao_reativa": {"nome": "Evolução Reativa em Combate", "tipo": "passiva", "alvo": "self", "efeito": {"hit_recebido_buff_atk": 10, "hit_recebido_buff_def": 5, "stacks": 10}},
    "lendario_super_saiyajin": {"nome": "Lendário Super Saiyajin", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp": 100, "buff_atk": 80, "buff_def": 50, "dano_bonus_hp_alvo": 15, "turnos": 3}},
    
    "punho_agua_corrente": {"nome": "Punho de Água Corrente", "tipo": "passiva", "alvo": "self", "efeito": {"reduz_dano_recebido": 50, "counter_atk_percent": 1.0}},
    "punho_redemoinho_ferro": {"nome": "Punho Cortante do Redemoinho de Ferro", "tipo": "buff", "alvo": "self", "efeito": {"counter_atk_percent": 2.0, "buff_crt": 50, "buff_dodge": 50, "turnos": 1}},
    
    "lua_carmesim": {"nome": "Lua Carmesim", "tipo": "especial", "alvo": "self", "efeito": {"burn_matk_100_on_hit": 2, "fraqueza_on_hit": 30}},
    "sol_meia_noite": {"nome": "Sol da Meia-Noite / Amaterasu", "tipo": "buff", "alvo": "self", "efeito": {"burn_matk_200_on_hit": 4, "buff_def": 60, "buff_matk": 60}},
    
    "us_of_smash": {"nome": "United States of Smash", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "buff_atk": 25, "buff_matk": 25, "buff_def": 25, "turnos": 1}},
    "pilar_paz": {"nome": "Pilar da Paz (One For All 100%)", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp_max": 70, "buff_def": 70, "buff_atk_flat": 50, "imune_lentidao_fraqueza": True}},
    
    "gura_gura": {"nome": "Tremor-Tremor (Gura Gura no Mi)", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"aggro_max": True, "debuff_atk": 25, "lentidao_turnos": 2}},
    "homem_treme_mundo": {"nome": "O Homem que Faz o Mundo Tremer", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_atk": 40, "debuff_def": 40, "debuff_spd": 40, "reduz_dano_recebido": 50, "sobrevive_zero_hp_turnos": 1}},
    
    "borg_alladin": {"nome": "Borg (Barreira de Rukh)", "tipo": "escudo", "alvo": "self", "efeito": {"escudo_hp_max": 0.60, "converte_matk_def": 0.50}},
    "invocar_ugo": {"nome": "Invocar: Gigante Ugo", "tipo": "invocacao", "alvo": "campo", "efeito": {"ugo_hp": 150, "aggro_max": True, "escudos_aliados_hp_max": 0.50, "buff_def_time": 50}},
    
    "inteligencia_extrema": {"nome": "Inteligência Extrema (Ponto Cego)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 20, "buff_matk": 20, "debuff_def_inimigo": 15}},
    "ciencia_salva_vidas": {"nome": "A Ciência Salva Vidas (Dr. Stone)", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"efeito_aleatorio": ["cura_30", "escudo_50", "buff_spd_20", "buff_atk_50"]}},
    "emc2": {"nome": "E=mc² (Fórmula Definitiva)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"remove_debuffs": True, "buff_atk": 40, "buff_matk": 40, "buff_spd": 40}},
    
    "alquimista_chamas": {"nome": "Alquimista das Chamas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.2, "queimadura_fixa": 20, "turnos": 2, "debuff_def": 20}},
    "sacrificio_pedra_filosofal": {"nome": "O Sacrifício e a Pedra Filosofal", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_fixo": 50, "turnos": 2, "buff_matk_time": 50, "regen_hp_time": 15}},
    
    "death_note": {"nome": "Death Note (Execução Programada)", "tipo": "especial", "alvo": "unico_inimigo", "efeito": {"marca_morte": True, "turnos_espera": 3, "dano_verdadeiro_hp_atual": 0.50}},
    "kira_shinigami": {"nome": "Kira, o Shinigami Humano", "tipo": "especial", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"marca_morte": True, "dano_recebido_extra": 35, "duracao": "combate_inteiro"}},
    
    "manipulacao_psicologica": {"nome": "Manipulação Psicológica", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"chance_atacar_aliado": 0.30}},
    "sociopata_perfeito": {"nome": "O Sociopata Perfeito", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_atk": 20, "debuff_def": 20, "debuff_spd": 20}},
    "monstro_do_fim": {"nome": "O Verdadeiro Monstro do Fim", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_precisao": 50, "reduz_dano_causado": 40}},
    
    "sun_and_moon": {"nome": "The Sun and Moon (Sol e Lua)", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"marca_explosiva": True, "explosao_ao_morrer_matk": 2.0}},
    "skill_hunter": {"nome": "Skill Hunter (Livro de Roubos)", "tipo": "especial", "alvo": "unico_inimigo", "efeito": {"rouba_habilidade": True, "turnos": 3}},
    
    "discurso_tengen_toppa": {"nome": "Discurso Tengen Toppa", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 50, "buff_def": 40, "buff_spd": 35, "turnos": 2}},
    "fusao_almas_gurren": {"nome": "Fusão de Almas (Gurren Lagann)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_geral": 50, "imune_medo": True, "cura_percent_max": 0.20}},
    
    "hermit_purple": {"nome": "Hermit Purple (Espírito Oculto)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_dodge": 30, "turnos": 2}},
    "ondas_concentradas_hamon": {"nome": "Ondas Concentradas (Hamon)", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"remove_veneno": True, "cura_fixa": 20, "buff_def": 20}},
    "proxima_frase_joseph": {"nome": "Sua Próxima Frase Será...!", "tipo": "especial", "alvo": "unico_inimigo", "efeito": {"cancela_acao_ofensiva": True, "buff_crt_time": 50}},
    
    "kagemane": {"nome": "Possessão das Sombras (Kagemane)", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"stun_turnos": 1, "debuff_spd": 50}},
    "estrategia_magistral": {"nome": "Estratégia Magistral (QI 200)", "tipo": "especial", "alvo": "campo", "efeito": {"buff_crt_acc_spd_time": 35, "debuff_def_spd_inimigo": 25}},
    
    "tiro_1000_leguas": {"nome": "Tiro de 1000 Léguas da Pop Green", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "chance_stun": 0.40}},
    "rei_atiradores_sogeking": {"nome": "Rei dos Atiradores: Sogeking", "tipo": "buff", "alvo": "self", "efeito": {"buff_acc": 30, "buff_crt": 50, "proximo_ataque_dobrado": True}},
    "god_usopp": {"nome": "O Herói Falsificado (God Usopp)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_dodge": 25, "buff_crt": 25, "chance_medo_inimigos": 0.20}},
    
    "contrato_demonio_kobeni": {"nome": "Contrato Obscuro com o Demônio", "tipo": "especial", "alvo": "self", "efeito": {"efeito_aleatorio": ["cura_20", "buff_dano_30", "buff_dodge_30", "buff_crt_20"]}},
    "kobeni_car": {"nome": "Kobeni's Car", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.2, "chance_stun": 0.30}},
    "danca_azar": {"nome": "Dança do Azar (Caos)", "tipo": "especial", "alvo": "campo", "efeito": {"debuff_acc_crt_inimigo": 25, "buff_dodge_self": 50}},

    # ==========================================
    # HERÓIS - ESQUADRÃO TÁTICO E ASSASSINOS EXTREMOS
    # ==========================================
    "olho_de_aguia": {"nome": "Instinto da Falcão (Olho de Águia)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_crt": 20, "turnos": 2, "marca_alvo_fraqueza_ranged": 25}},
    "disparo_frio": {"nome": "Disparo Frio", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "ignora_def": 50}},
    "costas_marcadas": {"nome": "Os Segredos das Chamas (Costas Marcadas)", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"aumenta_eficacia_debuffs": 40, "turnos": 3}},

    "rifle_organico": {"nome": "O Fuzil Vivo (Rifle Orgânico)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "ignora_taunt_escudos": True}},
    "air_walk": {"nome": "Passeio Aéreo Suave (Air Walk)", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 50, "buff_dodge": 50, "turnos": 3, "ataque_duplo_fraco": 0.70}},

    "jeet_kune_do": {"nome": "Jeet Kune Do & Tiros Certeiros", "tipo": "passiva", "alvo": "self", "efeito": {"buff_dodge": 30, "turnos": 2, "contra_ataque_dodge": 1.20}},
    "cowboy_espaco": {"nome": "Cowboy do Espaço (Bang)", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"multiplicador_atk": 1.5, "dobra_chance_critico": True}},

    "arma_improvisada": {"nome": "Regra 1: Dia Z (Arma Improvisada)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "chance_efeito_aleatorio": {"bleed": 0.33, "stun": 0.33, "reduz_def": 0.33}}},
    "ex_hitman": {"nome": "O Ex-Hitman Lendário", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 60, "buff_spd": 40, "turnos": 3, "ataque_extra_rodada": True}},

    "escopeta_nichirin": {"nome": "Escopeta de Aço Nichirin", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.8, "debuff_def": 25}},
    "sistema_digestivo_demon": {"nome": "Sistema Digestivo Demoníaco", "tipo": "buff", "alvo": "self", "efeito": {"cura_percent_max": 0.25, "buff_atk": 50, "turnos": 3}},

    "casull_jackal": {"nome": "Balas Abençoadas (Casull & Jackal)", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"multiplicador_atk": 2.7, "debuff_def_por_hit": 20}},
    "cromwell_0": {"nome": "Liberação Cromwell Nível 0", "tipo": "invocacao", "alvo": "campo", "efeito": {"invoca_clones_50_status": 3, "cura_percent_max": 0.50, "buff_hp_atk": 100, "turnos": 3}},

    "juramento_glacial": {"nome": "Morte Branca: Juramento Glacial", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0, "ignora_dodge_camuflagem_defesa": True, "turno_extra_ao_matar": True}},
    "deus_da_morte_neve": {"nome": "Neve e Silêncio Profuso (Deus da Morte)", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 3.5, "buff_acc_crt_100": True, "turnos": 3, "ignora_escudos_imortalidade": True}},

    "espada_reid": {"nome": "Espada do Dragão Reid", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 4.0, "ignora_def": 50}},
    "protecao_divina_suprema": {"nome": "Proteção Divina Suprema", "tipo": "buff", "alvo": "self", "efeito": {"imortalidade_turnos": 2, "revive_hp": 0.50, "imunidade_debuffs": True}},

    "glifo_arcano": {"nome": "Glifo Arcano", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.2, "buff_matk": 20, "turnos": 2}},
    "circulo_elemental": {"nome": "Círculo Elemental", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "chance_burn_slow_weakness": 0.20}},
    "magia_proibida": {"nome": "Magia Proibida", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "remove_escudos_magicos": True}},

    "dark_burning_attack": {"nome": "Dark Burning Attack", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.0, "debuff_res_magica": 20}},
    "dark_magic_expanded": {"nome": "Dark Magic Expanded", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "lentidao_turnos": 2}},

    "cancao_esperanca": {"nome": "Canção da Esperança", "tipo": "cura", "alvo": "unico_aliado", "efeito": {"multiplicador_matk": 0.50, "cura_fixa": 50}},
    "encore_miku": {"nome": "Encore", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_spd": 20, "turnos": 3}},
    "miku_expo": {"nome": "Miku Expo", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_percent_max_time": 0.50, "remove_1_debuff_aliados": True}},

    "zafkiel": {"nome": "Zafkiel", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "dano_critico_triplicado": True}},
    "cidade_dos_clones": {"nome": "Cidade dos Clones", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk_dividido": 5.0, "invoca_clones": 2, "clones_dano_50": True, "turnos": 2}},

    "ebony_ivory": {"nome": "Ebony & Ivory", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 5, "efeito": {"multiplicador_atk": 0.8, "chance_critico": 50}},
    "devil_trigger": {"nome": "Devil Trigger", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 50, "buff_spd": 50, "lifesteal": 50, "turnos": 3}},

    "respiracao_chamas": {"nome": "Respiração das Chamas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "dot_burn_atk": 0.80, "turnos": 2}},
    "nona_forma_rengoku": {"nome": "Nona Forma: Rengoku", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 4.5, "ignora_def": 50, "self_dmg_hp_atual": 0.30}},

    "pegadas_diabo": {"nome": "Pegadas do Diabo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "buff_spd": 10}},
    "adolla_burst": {"nome": "Adolla Burst", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 20, "chance_agir_novamente": 0.30}},

    "snatch_ban": {"nome": "Snatch", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.2, "rouba_atk_alvo": 15, "cura_hp_perdido": 0.20}},
    "imortalidade_ban": {"nome": "Imortalidade", "tipo": "passiva", "alvo": "self", "efeito": {"revive_hp_max": 0.50, "uso_maximo": 1}},

    "corte_duplo": {"nome": "Corte Duplo", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"multiplicador_atk": 1.5, "chance_sangramento": 0.20}},
    "consciencia_espacial": {"nome": "Consciência Espacial", "tipo": "buff", "alvo": "self", "efeito": {"imune_cegueira": True, "buff_dodge": 40, "turnos": 3}},

    "magia_relampago": {"nome": "Magia de Relâmpago", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.2, "chance_stun": 0.20}},
    "armadura_raios": {"nome": "Armadura de Raios", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 20, "dano_magico_extra_on_hit_matk": 0.50}},

    "chute_nuclear": {"nome": "Chute Nuclear", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "chance_stun": 0.20}},
    "chute_540": {"nome": "Chute de 540°", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0, "stun_turnos": 1}},
    "impulsos_obscuros": {"nome": "Impulsos Obscuros", "tipo": "buff", "alvo": "self", "efeito": {"ignora_def": 50, "buff_atk": 40, "debuff_def_self": 10}},

    "ataque_invisivel": {"nome": "Ataque Invisível", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "multiplicador_matk": 1.2, "nunca_erra": True}},
    "excalibur": {"nome": "Excalibur", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 3.0, "remove_escudos": True, "debuff_def": 30}},

    "firebolt": {"nome": "Firebolt", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.8, "buff_spd_pos_uso": 20}},
    "argonauta": {"nome": "Argonauta", "tipo": "especial", "alvo": "self", "efeito": {"carrega_turno": 1, "next_hit_dano_100": True, "ignora_def": 40}},

    "aura_prata": {"nome": "Aura de Prata", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "dano_extra_vs_magos_invocacoes": 30}},
    "cacador_dragoes": {"nome": "Caçador de Dragões", "tipo": "passiva", "alvo": "self", "efeito": {"buff_atk_ao_receber_magia": 15, "acumulo_max": 5}},

    "incursio": {"nome": "Incursio", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 20, "aggro_max": True, "turnos": 2}},
    "evolucao_continua": {"nome": "Evolução Contínua", "tipo": "passiva", "alvo": "self", "efeito": {"imune_stun": True, "buff_atk_def_perma_batalha": 10}},

    "zan": {"nome": "Zan", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.6, "ignora_def": 100}},
    "deus_calamidade": {"nome": "Deus da Calamidade", "tipo": "passiva", "alvo": "self", "efeito": {"buff_spd": 20, "buff_crt": 20, "chance_execucao": 5}},

    "amon": {"nome": "Amon", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "multiplicador_matk": 1.2, "queimadura_turnos": 2}},
    "equipamento_djinn": {"nome": "Equipamento Djinn", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.2, "imune_queimadura": True, "buff_atk": 30}},

    "corrente_julgamento": {"nome": "Corrente de Julgamento", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "silence_turnos": 1}},
    "emperor_time": {"nome": "Emperor Time", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 15, "self_dmg_hp_max": 5, "turnos": -1}},

    "danca_borboletas": {"nome": "Dança das Borboletas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"aplica_veneno_atk": 1.2, "turnos": 3, "ignora_def": True}},
    "toxina_letal": {"nome": "Toxina Letal", "tipo": "passiva", "alvo": "unico_inimigo", "condicao": "morte", "efeito": {"veneno_fatal_hp_max": 20, "turnos": 3}},

    "auxilio_tatico": {"nome": "Auxílio Tático", "tipo": "buff", "alvo": "dps_aliado", "efeito": {"buff_atk": 15, "turnos": 3}},
    "cobertura_sombra": {"nome": "Cobertura Sombra", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_acc": 25, "buff_dodge": 25}},
    "conselheira_leal": {"nome": "Conselheira Leal", "tipo": "passiva", "alvo": "lider_aliado", "efeito": {"cura_hp_max_ao_agir": 15}},

    "choque_eletrico": {"nome": "Choque Elétrico", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "multiplicador_matk": 1.8, "stun_se_hp_baixo": 50}},
    "contratante_black_reaper": {"nome": "Contratante Black Reaper", "tipo": "passiva", "alvo": "self", "efeito": {"criticos_aplicam_paralisia": 1}},

    "forca_descomunal": {"nome": "Força Descomunal", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0, "remove_escudos_buffs_def": True}},
    "code_unknown": {"nome": "Code Unknown", "tipo": "passiva", "alvo": "self", "efeito": {"imune_debuffs_cc_instakill": True, "buff_atk": 40, "buff_def": 40}},

    "pacto_geass": {"nome": "Pacto Geass", "tipo": "cura", "alvo": "unico_aliado", "efeito": {"cura_matk": 0.30, "cura_hp_max": 0.15, "escudo_hp_max": 0.25, "turnos": 2}},
    "bruxa_imortal": {"nome": "Bruxa Imortal", "tipo": "passiva", "alvo": "todos_aliados", "condicao": "morte", "efeito": {"cura_perma_hp_max": 8}},

    "repeticao_temporal": {"nome": "Repetição Temporal", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"anula_hit_fatal_mantem_1hp": True, "cooldown": 4}},
    "vontade_sobreviver": {"nome": "Vontade de Sobreviver", "tipo": "reviver", "alvo": "aliados_mortos", "efeito": {"hp_percent": 0.10, "uso_maximo": 1}},

    "ressonancia": {"nome": "Ressonância", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "marca_reflete_dano": 30, "turnos": 3}},
    "grampo_final": {"nome": "Grampo Final", "tipo": "especial", "alvo": "todos_inimigos", "condicao": "matar_alvo", "efeito": {"explosao_area_atk": 1.8}},

    "armadilha_oculta": {"nome": "Armadilha Oculta", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "debuff_def": 15, "turnos": 2}},
    "faca_antisensei": {"nome": "Faca Anti-Sensei", "tipo": "passiva", "alvo": "self", "efeito": {"buff_crt_vs_raridade_alta": 15}},
    "provocacao_sadica": {"nome": "Provocação Sádica", "tipo": "passiva", "alvo": "self", "efeito": {"criticos_reduzem_atk_alvo": 20, "turnos": 2}},

    "amor_obsessivo": {"nome": "Amor Obsessivo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "buff_atk_self": 25, "debuff_def_alvo": 10, "foca_alvo_ate_morte": True}},
    "protegerei_meu_amor": {"nome": "Protegerei Meu Amor", "tipo": "passiva", "alvo": "aliado_aleatorio", "efeito": {"marca_protecao": True, "contra_ataque_atk": 2.2, "critico_vs_enfraquecidos": True}},
    "doce_loucura": {"nome": "Doce Loucura", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 40, "buff_crt": 30, "ignora_def": 30, "turnos": 3}},

    "respiracao_agua": {"nome": "Respiração da Água", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.4, "aplica_sangramento": True, "turnos": 2, "debuff_acc": 20}},
    "hinokami_kagura": {"nome": "Hinokami Kagura", "tipo": "buff", "alvo": "self", "efeito": {"ataques_fogo": True, "buff_crt": 15, "dano_extra_vs_queimados": 30}},

    "magia_corpo_celeste": {"nome": "Magia de Corpo Celeste", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.2, "chance_stun": 0.20, "turnos": 1}},
    "grand_chariot": {"nome": "Grand Chariot", "tipo": "buff", "alvo": "self", "efeito": {"age_primeiro_turn_1": True, "buff_matk_ofensivo": 40}},

    "contrato": {"nome": "Contrato", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_matk": 35, "turnos": 3, "perde_hp_max": 5}},
    "bruxa_ganancia": {"nome": "Bruxa da Ganância", "tipo": "passiva", "alvo": "self", "efeito": {"absorve_dano_magico_para_cura": 40}},

    "cursed_crystal_prison": {"nome": "Cursed Crystal Prison", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.4, "chance_freeze": 0.35, "turnos": 1}},
    "rei_demonio_lich": {"nome": "Rei Demônio (Lich)", "tipo": "passiva", "alvo": "self", "efeito": {"imune_instakill": True, "cura_causa_dano": True, "reduz_dano_magico_sofrido": 25}},

    "light_of_saber": {"nome": "Light of Saber", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.8, "ignora_def_magica": 20}},
    "rivalidade": {"nome": "Rivalidade", "tipo": "passiva", "alvo": "self", "efeito": {"buff_matk_com_outro_mago": 20}},
    "magia_avancada": {"nome": "Magia Avançada", "tipo": "passiva", "alvo": "self", "efeito": {"habilidades_atingem_mais_alvos": 2}},

    "holopsicon": {"nome": "Holopsicon", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.8, "multiplicador_matk": 2.2, "ignora_escudos": True}},
    "reescrita_causal": {"nome": "Reescrita Causal", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"remove_resistencias_imunidades": True, "turnos": 3}},

    "earth_surge": {"nome": "Earth Surge", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.8, "debuff_spd": 20}},
    "poder_natureza": {"nome": "Poder da Natureza", "tipo": "passiva", "alvo": "self", "efeito": {"converte_dano_para_cura_menor_hp": 20}},

    "minya": {"nome": "Minya", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.6, "root_turnos": 1, "ignora_escudos_magicos": True}},
    "biblioteca_proibida": {"nome": "Biblioteca Proibida", "tipo": "passiva", "alvo": "campo", "efeito": {"anula_primeira_aoe_inimiga": True}},

    "magia_elemental_multipla": {"nome": "Magia Elemental Múltipla", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.5, "ataca_fraqueza_elemental": True}},
    "royal_flare": {"nome": "Royal Flare", "tipo": "especial", "alvo": "self", "efeito": {"buff_dano_ult": 30, "perde_proxima_acao": True}},

    "pocao_venenosa": {"nome": "Poção Venenosa", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.8, "veneno_turnos": 2}},
    "cogumelo_perigoso": {"nome": "Cogumelo Perigoso", "tipo": "especial", "alvo": "aliado_aleatorio", "efeito": {"chance_cura_ou_dano": True, "se_curar_matk_dobrado": 1}},
    "mestre_pocoes": {"nome": "Mestre de Poções", "tipo": "passiva", "alvo": "self", "efeito": {"veneno_ignora_def_res": True}},

    "raio_morte_vanir": {"nome": "Raio da Morte do Vanir", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 3.0, "ignora_escudos_barreiras": True}},
    "vidas_extras_vanir": {"nome": "Vidas Extras", "tipo": "passiva", "alvo": "self", "condicao": "morte", "efeito": {"revive_hp": 0.25, "uso_maximo": 1}},

    "presenca_divina": {"nome": "Presença Divina", "tipo": "buff", "alvo": "unico_aliado", "efeito": {"remove_debuffs": True, "buff_dodge": 20, "turnos": 2}},
    "deus_hinamizawa": {"nome": "Deus de Hinamizawa", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"apos_turno_3_buff_def": 20}},

    "rugido_dragao_mar": {"nome": "Rugido do Dragão do Mar", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.8, "dano_matk_extra": 40, "empurra_fim_fila": True}},
    "armadura_valquiria": {"nome": "Armadura da Valquíria", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 35, "buff_def": 35, "ataques_somam_atk_matk": True}},

    "zoltraak_rápido": {"nome": "Zoltraak (Disparo Rápido)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.4, "prioridade_alta_acao": True}},
    "supressao_mana": {"nome": "Supressão de Mana", "tipo": "passiva", "alvo": "self", "efeito": {"primeiro_ataque_dano_dobrado": True}},

    "ignorar_miko": {"nome": "Ignorar", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"reduz_aggro": 30, "turnos": 2}},
    "visao_espiritual": {"nome": "Visão Espiritual", "tipo": "buff", "alvo": "magos_aliados", "efeito": {"buff_acc": 20}},
    "protecao_santuario": {"nome": "Proteção do Santuário", "tipo": "passiva", "alvo": "self", "efeito": {"sobrevive_hit_fatal_1hp": True}},

    "morningstar": {"nome": "Morningstar", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_atk": 2.2, "cura_aliado_matk": 0.15}},
    "forma_oni": {"nome": "Forma Oni", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 40, "buff_spd": 40, "alvos_aleatorios": True}},

    "brilho_idol": {"nome": "Brilho do Idol", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 20, "buff_matk": 20, "turnos": 2}},
    "olhos_estrelados": {"nome": "Olhos Estrelados", "tipo": "debuff", "alvo": "inimigo_menor_def", "efeito": {"confusao": True}},
    "mentira_amor": {"nome": "A Mentira é o Amor", "tipo": "especial", "alvo": "dps_aliado", "efeito": {"transfere_buffs_para_dps": True, "aggro_zero_self": 2}},

    "sleigh_beggy": {"nome": "Sleigh Beggy", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 3.0, "remove_burn_veneno": True}},
    "braco_dragao": {"nome": "Braço de Dragão", "tipo": "passiva", "alvo": "self", "efeito": {"ataque_aplica_maldicao": 2, "buff_hp_max_on_hit": 5, "acumulo_max": 5}},

    "apoio_moral": {"nome": "Apoio Moral", "tipo": "buff", "alvo": "unico_aliado", "efeito": {"buff_def": 20, "turnos": 2}},
    "determinacao_miku": {"nome": "Determinação", "tipo": "cura", "alvo": "unico_aliado", "efeito": {"cura_percent_max": 0.15}},
    "esforco_silencioso": {"nome": "Esforço Silencioso", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_dodge": 10}},

    "compaixao_tohru": {"nome": "Compaixão", "tipo": "especial", "alvo": "aliado_menor_hp", "efeito": {"remove_debuffs": True}},
    "sorriso_gentil": {"nome": "Sorriso Gentil", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"reduz_dano_recebido": 20, "turnos": 1}},
    "lacos_inquebraveis": {"nome": "Laços Inquebráveis", "tipo": "passiva", "alvo": "campo", "efeito": {"prolonga_stun_inimigo": 1}},

    "leitura_forca": {"nome": "Leitura da Força", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"block_automatico_ataque_chefe": True}},
    "medicina_subterranea": {"nome": "Medicina Subterrânea", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 2.2}},
    "abencoado": {"nome": "Abençoado", "tipo": "passiva", "alvo": "self", "efeito": {"imune_maldicoes_dot_terreno": True}},

    "energia_positiva": {"nome": "Energia Positiva", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_spd": 5, "buff_atk": 5}},
    "unindo_clube": {"nome": "Unindo o Clube", "tipo": "passiva", "alvo": "lider_aliado", "efeito": {"buff_dano_causado": 10}},
    "coracao_aberto": {"nome": "Coração Aberto", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"regen_hp_fixo_turno": 10}},

    "programadora": {"nome": "Programadora", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_acc": 20, "turnos": 3}},
    "cafe_quente": {"nome": "Café Quente", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.20}},
    "amiga_dragoes": {"nome": "Amiga de Dragões", "tipo": "passiva", "alvo": "self", "efeito": {"buffs_dobrados_nao_humanos": True}},

    "parede_nazarick": {"nome": "Parede de Nazarick", "tipo": "passiva", "alvo": "aliado_menor_hp", "efeito": {"redireciona_dano_para_si": True, "reduz_esse_dano": 50}},
    "furia_sucubo": {"nome": "Fúria do Súcubo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_def": 5.0, "counter_apos_tankar": True}},

    "saco_pancadas": {"nome": "Saco de Pancadas", "tipo": "buff", "alvo": "self", "efeito": {"aggro_total": True, "imortal_turno_ativo": True}},
    "grito_determinacao": {"nome": "Grito de Determinação", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"receber_dano_buff_atk": 10, "turnos": 2}},
    "heroi_chorao": {"nome": "Herói Chorão", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"em_1_hp_imune_atk_normal": True, "buff_dano_time": 20}}
}