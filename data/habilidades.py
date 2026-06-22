# ==========================================
# DICIONÁRIO MESTRE DE HABILIDADES TÁTICAS
# ==========================================
# Este arquivo dita a matemática do novo sistema de combate.
# Tipos: dano, cura, buff, debuff, passiva, escudo, provocar, insta_kill, especial, invocacao

import re
import unicodedata
from copy import deepcopy


SKILLS = {
    # ==========================================
    # HERÓIS - DPS / ATACANTES / MAGOS (Clássicos)
    # ==========================================
    "ataque_giratorio": {"nome": "Ataque Giratório", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "multiplicador_hit": 2}},
    "ataque_descomunal": {"nome": "Ataque Descomunal", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 10}},
    "berserk_levi": {"nome": "Berserk", "tipo": "especial", "alvo": "self", "efeito": {"buff_atk": 30, "buff_spd": 20, "imortalidade_turnos": 3}},
    
    "furacao_da_folha": {"nome": "Furacão da Folha", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 15}},
    "lotus_oculta": {"nome": "Lótus Oculta", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 30}},
    "oito_portoes": {"nome": "8 Portões", "tipo": "especial", "alvo": "self", "efeito": {"buff_atk": 30, "buff_spd": 30, "turnos": 2, "pos_efeito": "stun"}},
    
    "santoryuu": {"nome": "Santoryuu", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "multiplicador_hit": 3}},
    "ashura": {"nome": "Ashura", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "multiplicador_hit": 9}},
    
    "star_platinum": {"nome": "Star Platinum", "tipo": "passiva", "alvo": "self", "efeito": {"chance_ataque_duplo": 0.25, "turnos": 99}},
    "o_mundo": {"nome": "O Mundo", "tipo": "especial", "alvo": "self", "efeito": {"parar_tempo": True, "anular_habilidade_contra_si": 1, "stun_todos_inimigos": 1, "turnos_extra": 1, "turnos": 1}, "cooldown": 4},
    
    "dual_blade": {"nome": "Dual Blade", "tipo": "buff", "alvo": "self", "efeito": {"multiplicador_dano_atk": 2.0}},
    "privilegios_adm": {"nome": "Privilégios de Administrador", "tipo": "escudo", "alvo": "aliado_menor_hp", "efeito": {"imunidade_dano_turnos": 5, "escudo_hp_max": 0.35, "turnos": 5}},
    
    "sopro_de_fogo": {"nome": "Sopro de Fogo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 35, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 2}}},
    "lotus_chama_explosiva": {"nome": "Lótus de Lâminas", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 50}},
    "dragon_force": {"nome": "Dragon Force", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30, "duracao": "combate_inteiro"}},
    
    "explosion": {"nome": "Explosion", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 50}, "cooldown": 3},
    "explosion_plus": {"nome": "Explosion+", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 60}, "cooldown": 2},
    "explosion_plus_plus": {"nome": "Explosion++", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 80}, "uso_maximo": 1},
    
    "disparo_de_mana": {"nome": "Disparo de Mana", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 20}},
    "zoltraak": {"nome": "Zoltraak", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.0, "ignora_def": True, "dano_matk_extra": 50, "buff_crt": 20}},
    
    "azul_e_vermelho": {"nome": "Azul e Vermelho", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "agrupar_inimigos": True, "dano_matk_extra": 40}},
    "roxo": {"nome": "Roxo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 60, "chance_insta_kill": 0.10, "restricao": "nao_afeta_boss", "dano_minimo_matk": True, "ignora_def": 25}},
    
    "fallen_down": {"nome": "Fallen Down", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 80}},
    "grasp_heart": {"nome": "Grasp Heart", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"chance_insta_kill": 0.30, "restricao": "nao_afeta_boss", "multiplicador_matk": 1.0, "dano_minimo_matk": True}},
    
    "convergencia": {"nome": "Convergência", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 40, "chance_stun": 0.25, "stun_turnos": 1}},
    "desmantelar": {"nome": "Desmantelar", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 40}},

    # ==========================================
    # HERÓIS - SUPORTES E CURANDEIROS (Clássicos)
    # ==========================================
    "cura_chopper": {"nome": "Cura", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_fixa": 20, "multiplicador_matk": 0.50}},
    "rumble_ball": {"nome": "Rumble Ball", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 20, "buff_def": 20}},
    "cura_maxima": {"nome": "Cura Máxima", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_fixa": 40, "multiplicador_matk": 1.0}},
    
    "palma_mistica": {"nome": "Técnica da Palma Mística", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_fixa": 50, "multiplicador_matk": 1.5}},
    "kuchiyose_katsuyu": {"nome": "Kuchiyose", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "katsuyu", "nome": "Katsuyu", "hp_percent": 0.5, "comportamento": "curar_time", "turnos": 3}}},
    "criacao_renascimento": {"nome": "Criação do Renascimento", "tipo": "reviver", "alvo": "aliado_morto_aleatorio", "efeito": {"chance_reviver": 0.20, "hp_percent": 0.50}},
    
    "enchantment": {"nome": "Enchantment", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_atk": 20, "buff_matk": 20}},
    "high_enchanter": {"nome": "High Enchanter", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 35, "buff_matk": 35, "buff_def": 20}},
    
    "alto_perdao": {"nome": "Alto Perdão", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 0.50}},
    "reviver_elizabeth": {"nome": "Reviver", "tipo": "reviver", "alvo": "aliado_morto_aleatorio", "efeito": {"hp_percent": 1.0}, "uso_maximo": 1},
    
    "koten_zanshun": {"nome": "Koten Zanshun", "tipo": "escudo", "alvo": "aliado_menor_hp", "efeito": {"imunidade_dano_turnos": 2}},
    "soten_kisshun": {"nome": "Sōten Kisshun", "tipo": "escudo", "alvo": "aliado_menor_hp", "quantidade": 3, "efeito": {"imunidade_dano_turnos": 2, "buff_def_global": 30}},

    # ==========================================
    # HERÓIS - TANKS E DEFESA (Clássicos)
    # ==========================================
    "alquimia_def": {"nome": "Alquimia", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 20}},
    "invulnerabilidade_bio": {"nome": "Invulnerabilidade Biológica", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp": 20, "buff_def": 25}},
    "transmutacao": {"nome": "Transmutação", "tipo": "especial", "alvo": "self", "efeito": {"converte_atk_matk_para_def": True, "buff_def": 10}},
    
    "cristalizacao": {"nome": "Cristalização", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 25, "buff_hp_max": 25}},
    "tita": {"nome": "Titã", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 15}},
    "tita_cristalizacao": {"nome": "Titã + Cristalização", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 20, "buff_hp_max": 30}},
    
    "bebado_oito_trigramas": {"nome": "Bêbado de 8 Trigramas", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 50, "imortalidade_turnos": 1}},
    "forma_hibrida": {"nome": "Forma Híbrida", "tipo": "especial", "alvo": "self", "efeito": {"ignora_dano_fisico": True, "turnos": 5}},
    
    "regeneracao_koku": {"nome": "Regeneração", "tipo": "passiva", "alvo": "self", "efeito": {"cura_turnos": 20, "ignora_dano_fisico": True, "turnos": 99}},
    "marca_cacador": {"nome": "Marca do Caçador", "tipo": "passiva", "alvo": "self", "efeito": {"buff_spd": 30, "cura_turnos": 35, "imune_dano_fisico": True, "vulneravel_apenas_matk_massivo": True}},
    
    "absorcao": {"nome": "Absorção", "tipo": "escudo", "alvo": "self", "efeito": {"absorver_dano_refletir": 2.0, "absorve_proxima_habilidade_reflete_dobro": True, "turnos": 3}},
    "modo_divino": {"nome": "Modo Divino", "tipo": "especial", "alvo": "self", "efeito": {"cura_turnos": 40, "absorver_ultimate_refletir": 2.0}},

    # ==========================================
    # HERÓIS - TÁTICOS E PASSIVAS ABSURDAS (Clássicos)
    # ==========================================
    "inspiracao": {"nome": "Inspiração", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 10, "buff_atk": 10, "buff_matk": 10}},
    "discurso_motivacional": {"nome": "Discurso Motivacional", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_geral": 20}},
    "sacrificio_erwin": {"nome": "Sacrifício", "tipo": "passiva", "alvo": "aliado_maior_atk", "condicao": "hp_dps_critico", "efeito": {"transferir_hp_para_dps": True, "morre_no_processo": True}},
    
    "estrategista": {"nome": "Estrategista", "tipo": "passiva", "alvo": "campo", "efeito": {"debuff_precisao_inimiga": 0.20, "buff_precisao_aliada": 0.20}},
    "escriba": {"nome": "Escriba", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"ignora_ataque_basico_turnos": 2}},
    "full_control_encounter": {"nome": "Full Control Encounter", "tipo": "debuff", "alvo": "campo", "efeito": {"debuff_spd_inimiga": 20, "imunidade_aliados_turnos": 3}},
    
    "geass": {"nome": "Geass", "tipo": "especial", "alvo": "inimigo_aleatorio", "efeito": {"reviver_aliado": True, "chance_insta_kill": 0.25, "restricao": "nao_afeta_boss"}},
    "geass_plus": {"nome": "Geass+", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"reviver_aliados": 2, "imunidade_enquanto_vivo": True}},
    
    "kyoka_suigetsu": {"nome": "Kyoka Suigetsu", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "ilusao", "nome": "Ilusão Hipnótica", "hp_percent": 0.3, "atk_percent": 0.5, "comportamento": "provocar", "turnos": 3}}},
    "hipnose_completa": {"nome": "Hipnose Completa", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "falso_aizen", "nome": "Aizen Falso", "hp_percent": 1.0, "atk_percent": 0.5, "comportamento": "tankar", "turnos": 3}}},
    
    "belzebu": {"nome": "Belzebu", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.4, "lifesteal": 0.45, "absorve_atk_converte_cura": True}},
    "ciel": {"nome": "Ciel", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"adaptativo": True, "cura_50_se_low_hp": True, "execute_se_inimigo_abaixo_20": True, "buff_atk_def_30_se_inimigo_full": True}},

    # ==========================================
    # HERÓIS - ASSASSINOS E ATIRADORES (Clássicos)
    # ==========================================
    "linhas_de_sanzu": {"nome": "Linhas de Sanzu", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 20}},
    "disparo_sincronizado": {"nome": "Disparo Sincronizado", "tipo": "dano", "alvo": "inimigo_maior_atk", "quantidade": 2, "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 30}},
    "loucura_da_ordem": {"nome": "Loucura da Ordem", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 20, "buff_spd": 10, "critico_garantido": True}},
    
    "sniper": {"nome": "Sniper", "tipo": "dano", "alvo": "inimigo_maior_atk", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 40}},
    "xeque_mate": {"nome": "Xeque-Mate", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "critico_garantido": True}},
    "hell_snipe": {"nome": "Hell Snipe", "tipo": "insta_kill", "alvo": "inimigo_aleatorio", "efeito": {"chance_insta_kill": 1.0, "restricao": "nao_afeta_boss", "multiplicador_atk": 1.0, "dano_minimo_atk": True}},
    
    "pumpkin": {"nome": "Pumpkin", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 30, "dobro_dano_aereos": True}},
    "ultimate_pumpkin": {"nome": "Ultimate Pumpkin", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0}},
    
    "heilig_bogen": {"nome": "Heilig Bogen", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "ignora_def": True}},
    "antitese": {"nome": "Antítese", "tipo": "especial", "alvo": "inimigo_maior_atk", "quantidade": 2, "efeito": {"redireciona_dano_ignora_def_regen": True, "duracao": "combate_inteiro"}},
    
    "angel_wings": {"nome": "Angel Wings", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 3.0}},
    "manipulacao_gravitacional": {"nome": "Manip. Gravitacional", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"chance_insta_kill": 0.50, "restricao": "nao_afeta_boss"}, "uso_maximo": 1},

    "yandere": {"nome": "Yandere", "tipo": "passiva", "alvo": "self", "condicao": "dps_ferido", "efeito": {"buff_atk_contra_agressor": 20, "buff_atk": 20, "buff_crt": 10, "turnos": 3}},
    "intencao_assassina": {"nome": "Intenção Assassina", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"reduz_spd_zero": True, "stun_turnos": 1}},
    "querido_diario": {"nome": "Querido Diário", "tipo": "especial", "alvo": "aliado_maior_atk", "efeito": {"marca_dps_redireciona_dano_self": True, "transfere_atk_para_dps": True, "buff_atk": 25, "turnos": 3}},

    "assassinato": {"nome": "Assassinato", "tipo": "buff", "alvo": "self", "efeito": {"foca_menor_hp": True, "buff_crt": 20}},
    "assassinato_plus": {"nome": "Assassinato+", "tipo": "dano", "alvo": "inimigo_menor_hp", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 30}},
    "death_strike": {"nome": "Death Strike", "tipo": "especial", "alvo": "inimigo_menor_def", "efeito": {"corta_hp_metade": True, "chance_insta_kill": 0.50, "restricao": "nao_afeta_boss"}},
    
    "coagulacao": {"nome": "Coagulação", "tipo": "debuff", "alvo": "inimigo_aleatorio", "efeito": {"stun_turnos": 3, "ignora_def_alvo": True}},
    "coagulacao_plus": {"nome": "Coagulação+", "tipo": "debuff", "alvo": "inimigo_maior_atk", "efeito": {"stun_turnos": 3, "ignora_def_alvo": True}},
    
    "prisao_de_agua": {"nome": "Prisão de Água", "tipo": "especial", "alvo": "inimigo_aleatorio", "efeito": {"trava_x1_ate_morte": True}},
    "clone_de_agua": {"nome": "Clone de Água", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "clone_agua", "nome": "Clone Aquático", "hp_percent": 0.5, "atk_percent": 0.5, "comportamento": "atacar", "turnos": 3}}},
    
    "muramasa": {"nome": "Muramasa", "tipo": "passiva", "alvo": "self", "efeito": {"chance_insta_kill": 0.10, "restricao": "nao_afeta_boss", "dano_minimo_atk": True, "turnos": 99}},
    "lamina_carmesim": {"nome": "Lâmina Carmesim", "tipo": "especial", "alvo": "self", "efeito": {"chance_insta_kill": 1.0, "restricao": "nao_afeta_boss", "dano_minimo_atk": True, "morre_apos_turnos": 3, "turnos": 3}},
    
    "eletro_wave": {"nome": "Eletro-Wave", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 40, "stun_turnos": 2}},
    "godspeed": {"nome": "Godspeed", "tipo": "buff", "alvo": "self", "efeito": {"multiplica_spd": 2.0}},
    
    "mana_zone": {"nome": "Mana Zone", "tipo": "passiva", "alvo": "self", "efeito": {"multiplicador_matk": 1.0, "dano_fogo_extra": 30, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 3}}},
    "encarnacao_fogo": {"nome": "Encarnação do Fogo do Inferno", "tipo": "passiva", "alvo": "self", "condicao": "morte", "efeito": {"reviver_100_hp": True, "multiplica_atk_matk": 2.0, "debuff_def_inimigos": 20}, "uso_maximo": 1},


    # ==========================================
    # NOVAS HABILIDADES: MUNDO E DESAFIOS (EXPANSÃO)
    # ==========================================
    
    "telecinese_mob": {"nome": "Telecinese", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30}},
    "modo_cem_porcento": {"nome": "100%", "tipo": "especial", "alvo": "self", "efeito": {"buff_matk": 50, "imortalidade_turnos": 3, "duracao": "combate_inteiro"}},
    
    "jinki": {"nome": "Jinki", "tipo": "especial", "alvo": "self", "efeito": {"melhora_item_usado": 0.50, "buff_atk": 20, "buff_matk": 20, "buff_def": 20, "turnos": 3}},
    "jinki_plus": {"nome": "Jinki+", "tipo": "especial", "alvo": "self", "efeito": {"melhora_item_usado": 1.00, "buff_atk": 40, "buff_matk": 40, "buff_def": 40, "turnos": 3}},
    
    "retorno_morte": {"nome": "Retorno Através da Morte", "tipo": "passiva", "alvo": "self", "condicao": "morte", "efeito": {"reviver_infinito_se_aliado_vivo": True}},
    "contrato_espiritual_subaru": {"nome": "Contrato Espiritual (Beatrice)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 30, "buff_atk": 20, "buff_matk": 20}},
    "autoridades_subaru": {"nome": "Cor Leonis / Providência", "tipo": "especial", "alvo": "todos_inimigos", "efeito": {"cor_leonis_providencia": True, "reduz_dano_recebido_time": 25, "multiplicador_matk": 1.0, "dano_matk_extra": 30, "dano_minimo_matk": True, "acerto_garantido": True, "ignora_def": True}},
    
    "contrato_makima": {"nome": "Contrato", "tipo": "passiva", "alvo": "aliado_maior_atk", "condicao": "morte_dps", "efeito": {"chance_insta_kill": 1.0, "restricao": "nao_afeta_boss", "contrato_morte_dps": True, "turnos": 99}},
    "demonio_do_controle": {"nome": "Demônio do Controle", "tipo": "especial", "alvo": "inimigo_maior_atk", "efeito": {"sacrifica_dps_aliado_para_matar_dps_inimigo": True}},
    
    "restricao_celestial": {"nome": "Restrição Celestial", "tipo": "passiva", "alvo": "self", "efeito": {"debuff_dano_magico_sofrido": 1.10, "buff_atk": 20, "buff_spd": 25, "primeiro_hit_critico": True}},
    "zero_restricao": {"nome": "Zero Restrição", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 30}},
    
    "rabbit": {"nome": "Rabbit", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 30, "buff_def": 30}},
    "rabbit_plus": {"nome": "Rabbit+", "tipo": "passiva", "alvo": "self", "efeito": {"imunidade_dano_fisico": True}},
    
    "magia_de_gelo": {"nome": "Magia de Gelo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 40, "debuff_spd": 10}},
    "contrato_espiritual_emilia": {"nome": "Contrato Espiritual (Puck)", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30, "chance_stun": 0.25, "stun_turnos": 2}},
    
    "chainsaw_man": {"nome": "Chainsaw Man", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 30, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.3, "turnos": 3}}},
    "forma_verdadeira_denji": {"nome": "Forma Verdadeira", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "dano_atk_extra": 20, "ignora_def": True, "lifesteal": 0.40}},
    
    "anti_magia": {"nome": "Anti-Magia", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"remove_buffs": 2, "anula_magia_passiva": True}},
    "forma_demoniaca_asta": {"nome": "Forma Demoníaca", "tipo": "buff", "alvo": "self", "efeito": {"ignora_escudos_geral": True, "buff_spd": 30, "buff_atk": 50}},
    
    "cavaleiro_rei": {"nome": "Cavaleiro Rei", "tipo": "passiva", "alvo": "self", "efeito": {"buff_atk_por_hp_perdido": 2}},
    "excalibur": {"nome": "Excalibur", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "ignora_def": True, "executa_abaixo_percent": 40, "restricao": "nao_afeta_boss"}},
    
    "triceratops_fist": {"nome": "Triceratops Fist", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 20, "debuff_def": 15}},
    "whip_strike": {"nome": "Whip Strike", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"multiplicador_atk": 1.0, "dano_fisico": True}},
    "demon_back": {"nome": "Demon Back", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_cc": True, "buff_atk": 30, "buff_def": 20, "turnos": 2}},
    
    "marca_demoniaca": {"nome": "Marca Demoníaca", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 35, "turnos": 3}},
    "assault_mode": {"nome": "Assault Mode", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 40, "roubo_de_atk": 15}},
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
    "comunicacao_espiritual": {"nome": "Comunicação Espiritual", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "espirito", "nome": "Espírito", "hp_percent": 0.4, "matk_percent": 0.5, "comportamento": "suporte_hibrido", "turnos": 3}}},
    
    "ambidestria": {"nome": "Ambidestria", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"multiplicador_atk": 1.2, "crit_independente": True}},
    "pontaria_incomparavel": {"nome": "Pontaria Incomparável", "tipo": "passiva", "alvo": "self", "efeito": {"buff_crt": 40, "ignora_def_25": True, "acerto_garantido": True}},
    "arsenal_revy": {"nome": "Arsenal de Escolha", "tipo": "especial", "alvo": "todos_inimigos", "efeito": {"escolha_municao": True}},
    
    "respiracao_flor": {"nome": "Respiração da Flor", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 10, "buff_atk": 20, "aplica_veneno_on_hit": 20, "turno_parcial_on_crit": True}},
    "olhos_escarlates": {"nome": "Olhos Escarlates Equinocial", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.5, "critico_garantido": True, "ignora_def": 50, "veneno_pesado": 2.0}},
    
    "proteses_mortais": {"nome": "Próteses Mortais", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"multiplicador_atk": 1.0, "dano_fixo": 25, "chance_bleed": 0.25}},
    "modo_berserk_hyakkimaru": {"nome": "Modo Berserk", "tipo": "buff", "alvo": "self", "efeito": {"lifesteal_on_hit": True, "buff_atk": 40, "buff_spd": 20, "turnos": 3}},
    
    "restricao_celestial_completa": {"nome": "Restrição Celestial (Completa)", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_magica": True, "buff_atk": 30, "buff_spd": 30, "turnos": 3}},
    "cacador_imparavel": {"nome": "Caçador Imparável", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "dano_atk_extra": 50, "ignora_def_e_shield": 50, "turno_extra_ao_matar": True}},

    "criocinese_extrema": {"nome": "Criocinese Extrema", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"soma_atk_matk": True, "stun_turnos": 2, "debuff_spd_global": 50}},
    "mahapadma": {"nome": "Mahapadma", "tipo": "especial", "alvo": "campo", "efeito": {"stun_turnos_global": 1, "debuff_fraqueza": 20, "intocavel_turnos": 2}},
    
    "shadow_garden": {"nome": "Shadow Garden", "tipo": "buff", "alvo": "self", "efeito": {"intocavel_turnos": 2, "proximo_ataque_dobrado": True}},
    "i_am_atomic": {"nome": "I Am Atomic", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_soma_atk_matk": 3.0, "ignora_def_escudos": True, "critico_garantido": True, "stun_turnos": 1}},
    
    "surgir": {"nome": "Surgir!", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "sombra", "nome": "Sombra", "quantidade": 2, "hp_percent": 0.5, "atk_percent": 0.5, "comportamento": "tankar", "turnos": 3}}},
    "monarca_sombras": {"nome": "Monarca das Sombras", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "general_sombra", "nome": "General da Sombra", "quantidade": 3, "hp_percent": 0.8, "atk_percent": 0.8, "comportamento": "atacar", "turnos": 5}}},
    
    "star_dress": {"nome": "Star Dress", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 30, "buff_def": 20, "turnos": 5}},
    "urano_metria": {"nome": "Urano Metria", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dano_matk_extra": 50, "debuff_matk": 25}},
    
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
    "espada_razao_venuzdnor": {"nome": "Espada da Razão Venuzdnor", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"executa_abaixo_percent": 50, "restricao": "nao_afeta_boss", "dano_hp_atual": 0.70, "ignora_invulnerabilidade": True, "critico_garantido": True}},
    
    "gate_of_babylon": {"nome": "Gate of Babylon", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 6, "efeito": {"soma_atk_matk_100": True, "chance_reduzir_def": 0.20}},
    "enuma_elish": {"nome": "Enuma Elish (EA)", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 6.0, "ignora_imortalidade": True, "debuff_spd": 50, "debuff_def": 50, "turnos": 2}},
    
    "analise_estrategica": {"nome": "Análise Estratégica", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_crt": 20, "buff_acc": 20, "turnos": 3}},
    "pesquisa_campo": {"nome": "Pesquisa de Campo", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"aplica_fraqueza": 25, "turnos": 3}},
    "mobilidade_dmt_avancada": {"nome": "Mobilidade DMT Avançada", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 50, "buff_crt": 50, "buff_atk": 50, "buff_atk_aliados": 30, "turnos": 3}},
    
    "kekkijutsu_cura": {"nome": "Kekkijutsu de Cura", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 2.5, "remove_veneno_burn_bleed": True}},
    "explosao_sangue_definitiva": {"nome": "Explosão de Sangue Definitiva", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 3.0, "remove_todos_debuffs": True, "cura_turnos": 10, "turnos": 3}},
    
    "espada_do_heroi": {"nome": "A Espada do Herói", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_atk": 35, "buff_matk": 35, "buff_spd": 20, "turnos": 3}},
    "evolucao_vinculo": {"nome": "Evolução do Vínculo", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 30, "buff_def": 30, "buff_spd": 30, "turnos": 3, "buff_xp_lider": 50}},
    
    "energia_amaldicoada_reversa": {"nome": "Energia Amaldiçoada Reversa", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 3.0}},
    "autopsia_forense": {"nome": "Autópsia Forense", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_def": 30, "reduz_regen": 50, "turnos": 3}},
    "talento_especial_cura": {"nome": "Talento Especial de Cura", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 4.0, "remove_debuffs_pesados": True, "cura_self_20_percent": True}},
    
    "ressurreicao_divina": {"nome": "Ressurreição Divina", "tipo": "reviver", "alvo": "aliado_morto_aleatorio", "efeito": {"hp_percent": 0.50}, "uso_maximo": 1},
    "dispersao_sagrada": {"nome": "Dispersão Sagrada / Turn Undead", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "cura_percent_max_time": 0.25, "remove_debuffs_magicos": True}},
    
    "shikai_chiasumi": {"nome": "Shikai: Chiasumi no Tate", "tipo": "escudo", "alvo": "aliado_menor_hp", "efeito": {"escudo_hp_max": 0.50}},
    "bankai_benihime": {"nome": "Bankai: Kannonbiraki Benihime Aratame", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 1.0, "remove_debuffs": True, "reviver_mortos_hp": 0.50}},
    
    "mestra_venenos": {"nome": "Mestra dos Venenos", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"dot": {"tipo": "veneno", "base": "matk", "mult": 2.0, "turnos": 2}, "corta_cura": 50, "imune_toxinas": True}},
    "boticaria_alto_calao": {"nome": "Boticária de Alto Calão (Toxic)", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"dot": {"tipo": "veneno", "base": "matk", "mult": 2.5, "turnos": 3}, "lentidao": True, "fraqueza": True, "anti_cura": True, "buff_dano_aliados": 20}},
    
    "esquiva_pequeno_rei": {"nome": "Esquiva do Pequeno Rei", "tipo": "buff", "alvo": "self", "efeito": {"aggro_max": True, "buff_spd": 40, "turnos": 3}},
    "agilidade_divina": {"nome": "Agilidade Divina", "tipo": "passiva", "alvo": "self", "efeito": {"buff_dodge": 60, "age_primeiro": True, "counter_atk_percent": 1.50}},
    "separacao_molecular": {"nome": "Golpe de Separação Molecular", "tipo": "buff", "alvo": "self", "efeito": {"buff_dodge": 100, "turnos": 2, "dodge_permanente_apos": 50}},
    
    "magia_musculos": {"nome": "Magia dos Músculos", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 40, "buff_hp_max": 25, "reflete_dano": 25}},
    "hora_profiterole": {"nome": "Hora do Profiterole", "tipo": "cura", "alvo": "self", "efeito": {"cura_percent_max": 0.40, "buff_def": 40, "buff_atk": 40, "turnos": 3}},
    
    "endurecer_kirishima": {"nome": "Endurecer (Hardening)", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 60, "reflete_dano": 25}},
    "red_counter": {"nome": "Red Counter", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 100, "aggro_max": True, "reflete_dano": 30}},
    "red_riot_unbreakable": {"nome": "Red Riot Unbreakable", "tipo": "buff", "alvo": "self", "efeito": {"reduz_dano_recebido": 90, "ignora_criticos": True, "protege_aliados_fatal": True, "turnos": 3}},
    
    "escudo_ira": {"nome": "Escudo da Ira", "tipo": "especial", "alvo": "self", "efeito": {"aggro_max": True, "escudo_hp_max": 0.50, "counter_matk_percent": 2.0}},
    "armadura_imperador_dragao": {"nome": "Armadura do Imperador Dragão", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 100, "escudo_hp_max": 0.50, "reflete_dano": 40, "cura_turnos": 10}},
    
    "evolucao_reativa": {"nome": "Evolução Reativa em Combate", "tipo": "passiva", "alvo": "self", "efeito": {"hit_recebido_buff_atk": 10, "hit_recebido_buff_def": 5, "stacks": 10}},
    "lendario_super_saiyajin": {"nome": "Lendário Super Saiyajin", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp": 100, "buff_atk": 80, "buff_def": 50, "dano_bonus_hp_alvo": 15, "turnos": 3}},
    
    "punho_agua_corrente": {"nome": "Punho de Água Corrente", "tipo": "passiva", "alvo": "self", "efeito": {"reduz_dano_recebido": 50, "counter_atk_percent": 1.0}},
    "punho_redemoinho_ferro": {"nome": "Punho Cortante do Redemoinho de Ferro", "tipo": "buff", "alvo": "self", "efeito": {"counter_atk_percent": 2.0, "buff_crt": 50, "buff_dodge": 50, "turnos": 1}},
    
    "lua_carmesim": {"nome": "Lua Carmesim", "tipo": "especial", "alvo": "self", "efeito": {"burn_matk_100_on_hit": 2, "fraqueza_on_hit": 30}},
    "sol_meia_noite": {"nome": "Sol da Meia-Noite / Amaterasu", "tipo": "buff", "alvo": "self", "efeito": {"burn_matk_200_on_hit": 4, "buff_def": 60, "buff_matk": 60}},
    
    "us_of_smash": {"nome": "United States of Smash", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "buff_atk": 25, "buff_matk": 25, "buff_def": 25, "turnos": 1}},
    "pilar_paz": {"nome": "Pilar da Paz (One For All 100%)", "tipo": "buff", "alvo": "self", "efeito": {"buff_hp_max": 70, "buff_def": 70, "buff_atk_flat": 50, "imune_lentidao_fraqueza": True}},
    
    "gura_gura": {"nome": "Tremor-Tremor (Gura Gura no Mi)", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"aggro_max": True, "debuff_atk": 25, "debuff_spd": 25, "turnos": 2}},
    "homem_treme_mundo": {"nome": "O Homem que Faz o Mundo Tremer", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_atk": 40, "debuff_def": 40, "debuff_spd": 40, "reduz_dano_recebido": 50, "sobrevive_zero_hp_turnos": 1}},
    
    "borg_alladin": {"nome": "Borg (Barreira de Rukh)", "tipo": "escudo", "alvo": "self", "efeito": {"escudo_hp_max": 0.60, "converte_matk_def": 0.50}},
    "invocar_ugo": {"nome": "Invocar: Gigante Ugo", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "ugo", "nome": "Gigante Ugo", "hp_percent": 1.5, "atk_percent": 0.5, "comportamento": "tankar", "turnos": 4}}},
    
    "inteligencia_extrema": {"nome": "Inteligência Extrema (Ponto Cego)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 20, "buff_matk": 20, "debuff_def_inimigo": 15}},
    "ciencia_salva_vidas": {"nome": "A Ciência Salva Vidas (Dr. Stone)", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"efeito_aleatorio": ["cura_30", "escudo_50", "buff_spd_20", "buff_atk_50"]}},
    "emc2": {"nome": "E=mc² (Fórmula Definitiva)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"remove_debuffs": True, "buff_atk": 40, "buff_matk": 40, "buff_spd": 40}},
    
    "alquimista_chamas": {"nome": "Alquimista das Chamas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.2, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.2, "turnos": 2}, "debuff_def": 20}},
    "sacrificio_pedra_filosofal": {"nome": "O Sacrifício e a Pedra Filosofal", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dano_fixo": 50, "turnos": 2, "buff_matk_time": 50, "cura_turnos": 15}},
    
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
    "danca_azar": {"nome": "Dança do Azar (Caos)", "tipo": "especial", "alvo": "campo", "efeito": {"debuff_acc_crt_inimigo": 25, "buff_dodge": 50}},

    # ==========================================
    # HERÓIS - ESQUADRÃO TÁTICO E ASSASSINOS EXTREMOS
    # ==========================================
    "olho_de_aguia": {"nome": "Instinto da Falcão (Olho de Águia)", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_crt": 20, "turnos": 2, "marca_alvo_fraqueza_ranged": 25}},
    "disparo_frio": {"nome": "Disparo Frio", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "ignora_def": 50}},
    "costas_marcadas": {"nome": "Os Segredos das Chamas (Costas Marcadas)", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"aumenta_eficacia_debuffs": 40, "turnos": 3}},

    "rifle_organico": {"nome": "O Fuzil Vivo (Rifle Orgânico)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "ignora_taunt_escudos": True}},
    "air_walk": {"nome": "Passeio Aéreo Suave (Air Walk)", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 50, "buff_dodge": 50, "turnos": 3, "ataque_duplo_fraco": 0.70}},

    "jeet_kune_do": {"nome": "Jeet Kune Do & Tiros Certeiros", "tipo": "passiva", "alvo": "self", "efeito": {"buff_dodge": 30, "turnos": 2, "counter_atk_percent": 1.20}},
    "cowboy_espaco": {"nome": "Cowboy do Espaço (Bang)", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"multiplicador_atk": 1.5, "dobra_chance_critico": True}},

    "arma_improvisada": {"nome": "Regra 1: Dia Z (Arma Improvisada)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "chance_efeito_aleatorio": {"bleed": 0.33, "stun": 0.33, "reduz_def": 0.33}}},
    "ex_hitman": {"nome": "O Ex-Hitman Lendário", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 60, "buff_spd": 40, "turnos": 3, "ataque_extra_rodada": True}},

    "escopeta_nichirin": {"nome": "Escopeta de Aço Nichirin", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.8, "debuff_def": 25}},
    "sistema_digestivo_demon": {"nome": "Sistema Digestivo Demoníaco", "tipo": "buff", "alvo": "self", "efeito": {"cura_percent_max": 0.25, "buff_atk": 50, "turnos": 3}},

    "casull_jackal": {"nome": "Balas Abençoadas (Casull & Jackal)", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 3, "efeito": {"multiplicador_atk": 2.7, "debuff_def_por_hit": 20}},
    "cromwell_0": {"nome": "Liberação Cromwell Nível 0", "tipo": "invocacao", "alvo": "campo", "efeito": {"invocar": {"id": "familiar", "nome": "Familiar das Trevas", "quantidade": 3, "hp_percent": 0.5, "atk_percent": 0.5, "comportamento": "atacar", "turnos": 3}, "cura_percent_max": 0.50, "buff_hp_max": 100, "turnos": 3}},

    "juramento_glacial": {"nome": "Morte Branca: Juramento Glacial", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0, "ignora_dodge_camuflagem_defesa": True, "turno_extra_ao_matar": True}},
    "deus_da_morte_neve": {"nome": "Neve e Silêncio Profuso (Deus da Morte)", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 3.5, "buff_acc": 100, "buff_crt": 100, "turnos": 3, "ignora_escudos_imortalidade": True}},

    "espada_reid": {"nome": "Espada do Dragão Reid", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 4.0, "ignora_def": 50}},
    "protecao_divina_suprema": {"nome": "Proteção Divina Suprema", "tipo": "buff", "alvo": "self", "efeito": {"imortalidade_turnos": 2, "revive_hp": 0.50, "imunidade_debuffs": True}},

    "glifo_arcano": {"nome": "Glifo Arcano", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.2, "buff_matk": 20, "turnos": 2}},
    "circulo_elemental": {"nome": "Círculo Elemental", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "chance_burn_slow_weakness": 0.20}},
    "magia_proibida": {"nome": "Magia Proibida", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "remove_escudos_magicos": True}},

    "dark_burning_attack": {"nome": "Dark Burning Attack", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.0, "debuff_res_magica": 20}},
    "dark_magic_expanded": {"nome": "Dark Magic Expanded", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "debuff_spd": 20}},

    "cancao_esperanca": {"nome": "Canção da Esperança", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 0.50, "cura_fixa": 50}},
    "encore_miku": {"nome": "Encore", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_spd": 20, "turnos": 3}},
    "miku_expo": {"nome": "Miku Expo", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 0.50, "remove_todos_debuffs": True}},

    "zafkiel": {"nome": "Zafkiel", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "dano_critico_triplicado": True}},
    "cidade_dos_clones": {"nome": "Cidade dos Clones", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.5, "invocar": {"id": "clone", "nome": "Clone", "quantidade": 2, "hp_percent": 0.1, "atk_percent": 0.5, "comportamento": "atacar", "turnos": 2}}},

    "ebony_ivory": {"nome": "Ebony & Ivory", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 5, "efeito": {"multiplicador_atk": 0.8, "chance_critico": 50}},
    "devil_trigger": {"nome": "Devil Trigger", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 50, "buff_spd": 50, "lifesteal_on_hit": 50, "turnos": 3}},

    "respiracao_chamas": {"nome": "Respiração das Chamas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "dot": {"tipo": "fogo", "base": "atk", "mult": 0.8, "turnos": 2}}},
    "nona_forma_rengoku": {"nome": "Nona Forma: Rengoku", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 4.5, "ignora_def": 50, "self_dmg_hp_atual": 0.30}},

    "pegadas_diabo": {"nome": "Pegadas do Diabo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "buff_spd": 10}},
    "adolla_burst": {"nome": "Adolla Burst", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 20, "chance_agir_novamente": 0.30}},

    "snatch_ban": {"nome": "Snatch", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.2, "rouba_atk_alvo": 15, "cura_hp_perdido": 0.20}},
    "imortalidade_ban": {"nome": "Imortalidade", "tipo": "passiva", "alvo": "self", "efeito": {"revive_hp": 0.50, "uso_maximo": 1}},

    "corte_duplo": {"nome": "Corte Duplo", "tipo": "dano", "alvo": "unico_inimigo", "quantidade": 2, "efeito": {"multiplicador_atk": 1.5, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.2, "turnos": 3}}},
    "consciencia_espacial": {"nome": "Consciência Espacial", "tipo": "buff", "alvo": "self", "efeito": {"imune_cegueira": True, "buff_dodge": 40, "turnos": 3}},

    "magia_relampago": {"nome": "Magia de Relâmpago", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.2, "chance_stun": 0.20}},
    "armadura_raios": {"nome": "Armadura de Raios", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 20, "dano_magico_extra_on_hit_matk": 0.50}},

    "chute_nuclear": {"nome": "Chute Nuclear", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "chance_stun": 0.20}},
    "chute_540": {"nome": "Chute de 540°", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0, "stun_turnos": 1}},
    "impulsos_obscuros": {"nome": "Impulsos Obscuros", "tipo": "buff", "alvo": "self", "efeito": {"ignora_def": 50, "buff_atk": 40, "debuff_def": 10}},

    "ataque_invisivel": {"nome": "Ataque Invisível", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "multiplicador_matk": 1.2, "nunca_erra": True}},
    "excalibur": {"nome": "Excalibur", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 3.0, "remove_escudos": True, "debuff_def": 30}},

    "firebolt": {"nome": "Firebolt", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.8, "buff_spd": 20}},
    "argonauta": {"nome": "Argonauta", "tipo": "especial", "alvo": "self", "efeito": {"carrega_turno": 1, "next_hit_dano_100": True, "ignora_def": 40}},

    "aura_prata": {"nome": "Aura de Prata", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "dano_extra_vs_magos_invocacoes": 30}},
    "cacador_dragoes": {"nome": "Caçador de Dragões", "tipo": "passiva", "alvo": "self", "efeito": {"buff_atk_ao_receber_magia": 15, "acumulo_max": 5}},

    "incursio": {"nome": "Incursio", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 20, "aggro_max": True, "turnos": 2}},
    "evolucao_continua": {"nome": "Evolução Contínua", "tipo": "passiva", "alvo": "self", "efeito": {"imune_stun": True, "buff_atk_def_perma_batalha": 10}},

    "zan": {"nome": "Zan", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.6, "ignora_def": 100}},
    "deus_calamidade": {"nome": "Deus da Calamidade", "tipo": "passiva", "alvo": "self", "efeito": {"buff_spd": 20, "buff_crt": 20, "chance_execucao": 5}},

    "amon": {"nome": "Amon", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "multiplicador_matk": 1.2, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 2}}},
    "equipamento_djinn": {"nome": "Equipamento Djinn", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.2, "imune_queimadura": True, "buff_atk": 30}},

    "corrente_julgamento": {"nome": "Corrente de Julgamento", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "silence_turnos": 1}},
    "emperor_time": {"nome": "Emperor Time", "tipo": "buff", "alvo": "self", "efeito": {"buff_geral": 15, "self_dmg_hp_max": 5, "turnos": -1}},

    "danca_borboletas": {"nome": "Dança das Borboletas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dot": {"tipo": "veneno", "base": "atk", "mult": 1.2, "turnos": 3}, "ignora_def": True}},
    "toxina_letal": {"nome": "Toxina Letal", "tipo": "passiva", "alvo": "unico_inimigo", "condicao": "morte", "efeito": {"dot": {"tipo": "veneno", "base": "hp_max", "mult": 0.2, "turnos": 3}}},

    "auxilio_tatico": {"nome": "Auxílio Tático", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_atk": 15, "turnos": 3}},
    "cobertura_sombra": {"nome": "Cobertura Sombra", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_acc": 25, "buff_dodge": 25}},
    "conselheira_leal": {"nome": "Conselheira Leal", "tipo": "passiva", "alvo": "aliado_maior_atk", "efeito": {"cura_hp_max_ao_agir": 15}},

    "choque_eletrico": {"nome": "Choque Elétrico", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "multiplicador_matk": 1.8, "stun_se_hp_baixo": 50}},
    "contratante_black_reaper": {"nome": "Contratante Black Reaper", "tipo": "passiva", "alvo": "self", "efeito": {"criticos_aplicam_paralisia": 1}},

    "forca_descomunal": {"nome": "Força Descomunal", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.0, "remove_escudos": True}},
    "code_unknown": {"nome": "Code Unknown", "tipo": "passiva", "alvo": "self", "efeito": {"imunidade_debuffs": True, "buff_atk": 40, "buff_def": 40}},

    "pacto_geass": {"nome": "Pacto Geass", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 0.30, "cura_percent_max": 0.15, "escudo_hp_max": 0.25, "turnos": 2}},
    "bruxa_imortal": {"nome": "Bruxa Imortal", "tipo": "passiva", "alvo": "todos_aliados", "condicao": "morte", "efeito": {"cura_turnos": 8}},

    "repeticao_temporal": {"nome": "Repetição Temporal", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"anula_hit_fatal_mantem_1hp": True, "cooldown": 4}},
    "vontade_sobreviver": {"nome": "Vontade de Sobreviver", "tipo": "reviver", "alvo": "aliados_mortos_aleatorios", "efeito": {"hp_percent": 0.10, "uso_maximo": 1}},

    "ressonancia": {"nome": "Ressonância", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "marca_reflete_dano": 30, "turnos": 3}},
    "grampo_final": {"nome": "Grampo Final", "tipo": "especial", "alvo": "todos_inimigos", "condicao": "matar_alvo", "efeito": {"multiplicador_atk": 1.8}},

    "armadilha_oculta": {"nome": "Armadilha Oculta", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "debuff_def": 15, "turnos": 2}},
    "faca_antisensei": {"nome": "Faca Anti-Sensei", "tipo": "passiva", "alvo": "self", "efeito": {"buff_crt": 15}},
    "provocacao_sadica": {"nome": "Provocação Sádica", "tipo": "passiva", "alvo": "self", "efeito": {"criticos_removem_buff": 1, "turnos": 2}},

    "amor_obsessivo": {"nome": "Amor Obsessivo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "buff_atk": 25, "debuff_def": 10}},
    "protegerei_meu_amor": {"nome": "Protegerei Meu Amor", "tipo": "passiva", "alvo": "aliado_aleatorio", "efeito": {"counter_atk_percent": 2.2, "critico_garantido": True}},
    "doce_loucura": {"nome": "Doce Loucura", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 40, "buff_crt": 30, "ignora_def_on_hit": 30, "turnos": 3}},

    "respiracao_agua": {"nome": "Respiração da Água", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.4, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.3, "turnos": 2}, "debuff_acc": 20}},
    "hinokami_kagura": {"nome": "Hinokami Kagura", "tipo": "buff", "alvo": "self", "efeito": {"ataques_fogo": True, "buff_crt": 15}},

    "magia_corpo_celeste": {"nome": "Magia de Corpo Celeste", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.2, "chance_stun": 0.20, "turnos": 1}},
    "grand_chariot": {"nome": "Grand Chariot", "tipo": "buff", "alvo": "self", "efeito": {"age_primeiro": True, "buff_matk": 40}},

    "contrato": {"nome": "Contrato", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_matk": 35, "turnos": 3, "self_dmg_hp_max": 5}},
    "bruxa_ganancia": {"nome": "Bruxa da Ganância", "tipo": "passiva", "alvo": "self", "efeito": {"absorve_atk_converte_cura": True}},

    "cursed_crystal_prison": {"nome": "Cursed Crystal Prison", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.4, "freeze_turnos": 1}},
    "rei_demonio_lich": {"nome": "Rei Demônio (Lich)", "tipo": "passiva", "alvo": "self", "efeito": {"imune_toxinas": True, "reduz_dano_recebido": 25}},

    "light_of_saber": {"nome": "Light of Saber", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.8, "ignora_dano_magico": True}},
    "rivalidade": {"nome": "Rivalidade", "tipo": "passiva", "alvo": "self", "efeito": {"buff_matk": 20}},
    "magia_avancada": {"nome": "Magia Avançada", "tipo": "passiva", "alvo": "self", "efeito": {"buff_matk": 15}},

    "holopsicon": {"nome": "Holopsicon", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.8, "multiplicador_matk": 2.2, "ignora_escudos_geral": True}},
    "reescrita_causal": {"nome": "Reescrita Causal", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"remove_todos_buffs": True, "turnos": 3}},

    "earth_surge": {"nome": "Earth Surge", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.8, "debuff_spd": 20}},
    "poder_natureza": {"nome": "Poder da Natureza", "tipo": "passiva", "alvo": "self", "efeito": {"cura_turnos": 20}},

    "minya": {"nome": "Minya", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.6, "root_turnos": 1, "ignora_escudos_geral": True}},
    "biblioteca_proibida": {"nome": "Biblioteca Proibida", "tipo": "passiva", "alvo": "campo", "efeito": {"anular_habilidade_contra_si": 1}},

    "magia_elemental_multipla": {"nome": "Magia Elemental Múltipla", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.5, "ignora_def": True}},
    "royal_flare": {"nome": "Royal Flare", "tipo": "especial", "alvo": "self", "efeito": {"buff_matk": 30}},

    "pocao_venenosa": {"nome": "Poção Venenosa", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.8, "dot": {"tipo": "veneno", "base": "matk", "mult": 0.4, "turnos": 2}}},
    "cogumelo_perigoso": {"nome": "Cogumelo Perigoso", "tipo": "especial", "alvo": "aliado_aleatorio", "efeito": {"efeito_aleatorio_divino": True}},
    "mestre_pocoes": {"nome": "Mestre de Poções", "tipo": "passiva", "alvo": "self", "efeito": {"imune_toxinas": True}},

    "raio_morte_vanir": {"nome": "Raio da Morte do Vanir", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 3.0, "ignora_escudos_geral": True}},
    "vidas_extras_vanir": {"nome": "Vidas Extras", "tipo": "passiva", "alvo": "self", "condicao": "morte", "efeito": {"revive_hp": 0.25, "uso_maximo": 1}},

    "presenca_divina": {"nome": "Presença Divina", "tipo": "buff", "alvo": "aliado_menor_hp", "efeito": {"remove_todos_debuffs": True, "buff_dodge": 20, "turnos": 2}},
    "deus_hinamizawa": {"nome": "Deus de Hinamizawa", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"buff_def": 20}},

    "rugido_dragao_mar": {"nome": "Rugido do Dragão do Mar", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.8, "dano_matk_extra": 40, "debuff_spd": 20}},
    "armadura_valquiria": {"nome": "Armadura da Valquíria", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 35, "buff_def": 35, "multiplica_atk_matk": 1.5}},

    "zoltraak_rápido": {"nome": "Zoltraak (Disparo Rápido)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.4, "age_primeiro": True}},
    "supressao_mana": {"nome": "Supressão de Mana", "tipo": "passiva", "alvo": "self", "efeito": {"buff_matk": 20}},

    "ignorar_miko": {"nome": "Ignorar", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"reduz_dano_recebido": 30, "turnos": 2}},
    "visao_espiritual": {"nome": "Visão Espiritual", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_acc": 20}},
    "protecao_santuario": {"nome": "Proteção do Santuário", "tipo": "passiva", "alvo": "self", "efeito": {"revive_hp": 0.10}},

    "morningstar": {"nome": "Morningstar", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_atk": 2.2, "multiplicador_matk": 0.15}},
    "forma_oni": {"nome": "Forma Oni", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 40, "buff_spd": 40}},

    "brilho_idol": {"nome": "Brilho do Idol", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 20, "buff_matk": 20, "turnos": 2}},
    "olhos_estrelados": {"nome": "Olhos Estrelados", "tipo": "debuff", "alvo": "inimigo_menor_def", "efeito": {"confusao": True}},
    "mentira_amor": {"nome": "A Mentira é o Amor", "tipo": "especial", "alvo": "aliado_maior_atk", "efeito": {"buff_atk": 30}},

    "sleigh_beggy": {"nome": "Sleigh Beggy", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 3.0, "remove_todos_debuffs": True}},
    "braco_dragao": {"nome": "Braço de Dragão", "tipo": "passiva", "alvo": "self", "efeito": {"buff_hp": 5}},

    "apoio_moral": {"nome": "Apoio Moral", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_def": 20, "turnos": 2}},
    "determinacao_miku": {"nome": "Determinação", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.15}},
    "esforco_silencioso": {"nome": "Esforço Silencioso", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_dodge": 10}},

    "compaixao_tohru": {"nome": "Compaixão", "tipo": "especial", "alvo": "aliado_menor_hp", "efeito": {"remove_todos_debuffs": True}},
    "sorriso_gentil": {"nome": "Sorriso Gentil", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"reduz_dano_recebido": 20, "turnos": 1}},
    "lacos_inquebraveis": {"nome": "Laços Inquebráveis", "tipo": "passiva", "alvo": "campo", "efeito": {"stun_turnos": 1}},

    "leitura_forca": {"nome": "Leitura da Força", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"imunidade_dano_turnos": 1}},
    "medicina_subterranea": {"nome": "Medicina Subterrânea", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 2.2}},
    "abencoado": {"nome": "Abençoado", "tipo": "passiva", "alvo": "self", "efeito": {"imune_toxinas": True}},

    "energia_positiva": {"nome": "Energia Positiva", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_spd": 5, "buff_atk": 5}},
    "unindo_clube": {"nome": "Unindo o Clube", "tipo": "passiva", "alvo": "aliado_maior_atk", "efeito": {"buff_atk": 10}},
    "coracao_aberto": {"nome": "Coração Aberto", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"cura_turnos": 10}},

    "programadora": {"nome": "Programadora", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_acc": 20, "turnos": 3}},
    "cafe_quente": {"nome": "Café Quente", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.20}},
    "amiga_dragoes": {"nome": "Amiga de Dragões", "tipo": "passiva", "alvo": "self", "efeito": {"buff_geral": 15}},

    "parede_nazarick": {"nome": "Parede de Nazarick", "tipo": "passiva", "alvo": "aliado_menor_hp", "efeito": {"reduz_dano_recebido": 50}},
    "furia_sucubo": {"nome": "Fúria do Súcubo", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_def": 5.0, "counter_atk_percent": 1.0}},

    "saco_pancadas": {"nome": "Saco de Pancadas", "tipo": "buff", "alvo": "self", "efeito": {"aggro_max": True, "imortalidade_turnos": 1}},
    "grito_determinacao": {"nome": "Grito de Determinação", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"buff_atk": 10, "turnos": 2}},
    "heroi_chorao": {"nome": "Herói Chorão", "tipo": "passiva", "alvo": "todos_aliados", "efeito": {"buff_atk": 20}},

    # Afinidade máxima: liberada automaticamente ao reunir cinco heróis da mesma obra.
    "ressonancia_de_obra": {
        "nome": "Ressonância da Obra",
        "tipo": "buff",
        "alvo": "todos_aliados",
        "efeito": {"buff_geral": 15, "escudo_hp_max": 0.10, "turnos": 3},
        "cooldown": 5,
    },

    # Seres divinos (IDs 277–289).
    "salvacao_conceitual": {"nome": "Salvação Conceitual", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 2.5, "remove_todos_debuffs": True}},
    "forma_suprema_de_deusa": {"nome": "Forma Suprema de Deusa", "tipo": "escudo", "alvo": "todos_aliados", "efeito": {"escudo_hp_max": 0.35, "imunidade_dano_turnos": 1, "turnos": 1}, "uso_maximo": 1},
    "reescrita_do_roteiro": {"nome": "Reescrita do Roteiro", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.2, "debuff_spd": 60, "turnos": 2}},
    "autoridade_absoluta": {"nome": "Autoridade Absoluta", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"remove_todos_buffs": True, "debuff_geral": 25, "bloqueia_buffs": True, "turnos": 3}},
    "desespero_do_infinito": {"nome": "Desespero do Infinito", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.8, "debuff_atk": 30, "debuff_matk": 30, "turnos": 2}},
    "carcere_multidimensional": {"nome": "Cárcere Multidimensional", "tipo": "debuff", "alvo": "inimigo_maior_spd", "efeito": {"stun_turnos": 2, "debuff_def": 25, "turnos": 2}},
    "apagamento_brincalhao": {"nome": "Apagamento Brincalhão", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"dano_hp_atual": 0.45, "ignora_def": True}},
    "julgamento_do_rei_de_tudo": {"nome": "Julgamento do Rei de Tudo", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"reduz_dano_recebido": 40, "stun_turnos": 1, "turnos": 2}},
    "selo_espiritual_solto": {"nome": "Selo Espiritual Solto", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.5, "ignora_def_escudos": True}},
    "espada_jingke_suprema": {"nome": "Espada Jingke Suprema", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.8, "critico_garantido": True, "executa_abaixo_percent": 45, "restricao": "nao_afeta_boss"}},
    "morte_instantanea_conceitual": {"nome": "Morte Instantânea Conceitual", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "critico_garantido": True, "chance_insta_kill": 0.15, "restricao": "nao_afeta_boss"}},
    "o_fim_de_todas_as_coisas": {"nome": "O Fim de Todas as Coisas", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 25, "turnos": 99}},
    "desejo_inconsciente": {"nome": "Desejo Inconsciente", "tipo": "especial", "alvo": "todos_aliados", "efeito": {"efeito_aleatorio_divino": True}},
    "reconstrucao_do_universo": {"nome": "Reconstrução do Universo", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_atk": 35, "buff_matk": 35, "buff_spd": 35, "turnos": 99}},
    "cristal_cosmos_protetor": {"nome": "Cristal Cosmos Protetor", "tipo": "escudo", "alvo": "todos_aliados", "efeito": {"escudo_hp_max": 0.40, "turnos": 2}},
    "luz_eterna_da_esperanca": {"nome": "Luz Eterna da Esperança", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 0.15, "remove_todos_debuffs": True}},
    "grande_iluminacao_esmagadora": {"nome": "Grande Iluminação Esmagadora", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "debuff_def": 50, "turnos": 3}},
    "muzan_lei_do_egocentrismo": {"nome": "Muzan: Lei do Egocentrismo", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 15, "turnos": 3}},
    "escudo_vetorial_absoluto": {"nome": "Escudo Vetorial Absoluto", "tipo": "escudo", "alvo": "self", "efeito": {"escudo_hp_max": 0.60, "reduz_dano_recebido": 40, "turnos": 3}},
    "asas_brancas_divinas": {"nome": "Asas Brancas Divinas", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_dano_turnos": 2, "buff_matk": 40, "turnos": 2}},
    "chute_triplo_do_dragao_azul": {"nome": "Chute Triplo do Dragão Azul", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_hit": 3, "multiplicador_atk": 1.0, "ignora_def": 30, "debuff_spd": 15, "turnos": 2}},
    "jecheondaeseong_o_rei_macaco": {"nome": "Jecheondaeseong: O Rei Macaco", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.5, "critico_garantido": True}},
    "percepcao_de_morte_linear": {"nome": "Percepção de Morte Linear", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.0, "ignora_def": True, "anti_cura": True, "turnos": 3}},
    "vazio_lamina_de_contradicao": {"nome": "Vazio: Lâmina de Contradição", "tipo": "buff", "alvo": "self", "efeito": {"chance_insta_kill": 0.15, "restricao": "nao_afeta_boss", "turnos": 99}},
    "poder_da_certeza_absoluta": {"nome": "Poder da Certeza Absoluta", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.4, "critico_garantido": True, "ignora_def_escudos": True}},
    "doce_labirinto_sem_fim": {"nome": "Doce Labirinto Sem Fim", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"stun_turnos": 1, "aplica_fraqueza": 35, "debuff_spd": 50, "turnos": 3}},

    # Benimaru e Darkness.
    "benimaru_tensura__base": {
        "nome": "Chamas do Purgatório (Hell Flare)",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {
            "multiplicador_atk": 1.8,
            "ignora_def": 30,
            "dot": {"tipo": "fogo", "base": "atk", "mult": 0.3, "turnos": 3},
        },
    },
    "benimaru_tensura__evo_7": {
        "nome": "General Espiritual dos Dragões (Rei Demônio)",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {
            "ignora_def_on_hit": 30,
            "revive_hp": 0.20,
            "ataques_fogo": True,
            "turnos": 99,
        },
        "uso_maximo": 1,
    },
    "darkness_konosuba__base": {
        "nome": "Delícia Masoquista (Taunt Corporal)",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {
            "aggro_max": True,
            "buff_def": 50,
            "cura_turnos": 15,
            "turnos": 2,
        },
        "cooldown": 3,
    },
    "darkness_konosuba__evo_5": {
        "nome": "Sacrifício Inquebrável da Cruzada",
        "tipo": "passiva",
        "alvo": "self",
        "efeito": {
            "protege_aliados_fatal": True,
            "reduz_dano_recebido": 30,
            "imune_stun": True,
            "turnos": 99,
        },
        "uso_maximo": 1,
    },

    # Vilões e novos personagens (IDs 292-324).
    "dio_brando__base": {
        "nome": "O Mundo (The World)",
        "tipo": "dano",
        "alvo": "inimigo_maior_spd",
        "efeito": {"multiplicador_atk": 1.8, "ignora_def": True, "stun_turnos": 1},
    },
    "dio_brando__evo_7": {
        "nome": "Sangue Vampírico de Joestar",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"lifesteal_on_hit": 0.40, "buff_atk": 30, "turnos": 99},
        "uso_maximo": 1,
    },
    "barba_negra__base": {
        "nome": "Yami Yami no Mi: Buraco Negro",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_atk": 1.5, "remove_todos_buffs": True, "bloqueia_buffs": True, "turnos": 2},
    },
    "barba_negra__evo_7": {
        "nome": "Gura Gura no Mi: Terremoto Absoluto",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_atk": 2.5, "debuff_def": 40, "turnos": 99},
    },
    "madara__base": {
        "nome": "Tengai Shinsei (Meteoro Cósmico)",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 2.2, "debuff_def": 35, "turnos": 99},
    },
    "madara__evo_7": {
        "nome": "Limbo: Hengoku",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_dodge": 45, "counter_atk_percent": 1.20, "turnos": 99},
        "uso_maximo": 1,
    },
    "griffith__base": {
        "nome": "Manipulação Causal de Femto",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"aggro_max": True, "reduz_dano_recebido": 50, "reflete_dano": 15, "turnos": 3},
    },
    "griffith__evo_7": {
        "nome": "O Eclipse e a Mão de Deus",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"revive_hp": 1.0, "buff_atk": 45, "turnos": 99},
        "uso_maximo": 1,
    },
    "doflamingo__base": {
        "nome": "Parasite: Controle de Fios",
        "tipo": "debuff",
        "alvo": "inimigo_maior_atk",
        "efeito": {"confusao": True, "debuff_atk": 30, "turnos": 1},
    },
    "doflamingo__evo_5": {
        "nome": "Gaiola de Fios (Birdcage)",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"dano_hp_atual": 0.15, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.3, "turnos": 3}},
    },
    "all_for_one__base": {
        "nome": "Roubo de Individualidade",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 1.5, "remove_todos_buffs": True, "debuff_atk": 25, "debuff_def": 25, "turnos": 2},
    },
    "all_for_one__evo_7": {
        "nome": "Canhão de Ar e Impacto Combinado",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_atk": 2.8, "ignora_def_escudos": True, "stun_turnos": 1},
    },
    "sukuna__base": {
        "nome": "Clivagem e Desmantelar",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 1.8, "anti_cura": True, "dot": {"tipo": "sangramento", "base": "matk", "mult": 0.4, "turnos": 3}},
    },
    "sukuna__evo_7": {
        "nome": "Santuário Malevolente",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 1.5, "debuff_def": 50, "dot": {"tipo": "sangramento", "base": "matk", "mult": 0.3, "turnos": 2}},
    },
    "mahito__base": {
        "nome": "Transfiguração Ociosa",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 1.6, "ignora_def": True, "chance_stun": 0.25, "stun_turnos": 1},
    },
    "mahito__evo_5": {
        "nome": "Auto-Transfiguração de Combate",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_def": 40, "imune_toxinas": True, "cura_turnos": 12, "turnos": 3},
    },
    "petelgeuse__base": {
        "nome": "Mãos Invisíveis da Autoridade",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 1.4, "debuff_spd": 30, "debuff_acc": 30, "turnos": 2},
    },
    "petelgeuse__evo_5": {
        "nome": "Loucura Devota de Amor",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_crt": 25, "criticos_removem_buff": 1, "turnos": 3},
    },
    "orochimaru__base": {
        "nome": "Reencarnação da Serpente Viva",
        "tipo": "cura",
        "alvo": "self",
        "efeito": {"multiplicador_matk": 0.35, "aplica_veneno_on_hit": 0.35, "turnos": 3},
    },
    "orochimaru__evo_5": {
        "nome": "Invocação: Edo Tensei",
        "tipo": "invocacao",
        "alvo": "campo",
        "efeito": {"invocar": {"id": "edo_tensei", "nome": "Reanimação", "hp_percent": 1.0, "atk_percent": 0.8, "comportamento": "tankar", "turnos": 3}},
    },
    "naraku__base": {
        "nome": "Miasma Venenoso do Pântano",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 1.4, "anti_cura": True, "dot": {"tipo": "veneno", "base": "matk", "mult": 0.3, "turnos": 3}},
    },
    "naraku__evo_5": {
        "nome": "Barreira de Energia Espiritual",
        "tipo": "escudo",
        "alvo": "self",
        "efeito": {"escudo_hp_max": 0.50, "imunidade_debuffs": True, "reflete_dano": 15, "turnos": 3},
    },
    "kaguya_otsutsuki__base": {
        "nome": "Amenominaka (Dobra Dimensional)",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 2.0, "debuff_spd": 50, "turnos": 2},
    },
    "kaguya_otsutsuki__evo_7": {
        "nome": "Ossos de Cinza Assassinos de Tudo",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"dano_hp_atual": 0.50, "ignora_def": True, "chance_insta_kill": 0.20, "restricao": "nao_afeta_boss"},
    },
    "dabi__base": {
        "nome": "Chamas Azuis do Purgatório",
        "tipo": "dano",
        "alvo": "inimigos_aleatorios",
        "quantidade": 2,
        "efeito": {"multiplicador_matk": 1.6, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 3}},
    },
    "dabi__evo_5": {
        "nome": "Cremação Suicida",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_matk": 45, "dot_self": 5, "turnos": 3},
    },
    "crocodile__base": {
        "nome": "Desert Spada: Lâmina de Areia",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 1.5, "debuff_spd": 25, "turnos": 2},
    },
    "crocodile__evo_5": {
        "nome": "Desidratação de Areia Absoluta",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 1.8, "lifesteal": 0.40, "remove_todos_buffs": True},
    },
    "father__base": {
        "nome": "Alquimia do Homúnculo Original",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 1.7, "ignora_def_escudos": True},
    },
    "father__evo_7": {
        "nome": "Pedra Filosofal de Almas",
        "tipo": "escudo",
        "alvo": "self",
        "efeito": {"revive_hp": 0.50, "escudo_hp_max": 0.50, "ignora_dano_fisico": True, "turnos": 99},
        "uso_maximo": 1,
    },
    "yhwach__base": {
        "nome": "The Almighty: Futuro Escrito",
        "tipo": "dano",
        "alvo": "inimigo_maior_spd",
        "efeito": {"multiplicador_matk": 1.2, "stun_turnos": 1},
    },
    "yhwach__evo_7": {
        "nome": "Sankt Altar: Roubo de Poder",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 2.2, "silence_turnos": 2},
    },
    "muzan_kibutsuji__base": {
        "nome": "Injeção de Sangue Corrosivo",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_matk": 1.8, "anti_cura": True, "debuff_atk": 30, "dot": {"tipo": "veneno", "base": "matk", "mult": 0.4, "turnos": 3}},
    },
    "muzan_kibutsuji__evo_7": {
        "nome": "Chicotes de Carne Biológicos",
        "tipo": "dano",
        "alvo": "inimigos_aleatorios",
        "quantidade": 3,
        "efeito": {"multiplicador_atk": 1.6, "lifesteal": 0.30},
    },
    "meruem__base": {
        "nome": "Síntese de Aura Quimera",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"aggro_max": True, "buff_def": 45, "turnos": 3},
    },
    "meruem__evo_7": {
        "nome": "Forma Mítica Desperta",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"barreira_dano_recebido": 0.50, "buff_atk": 25, "turnos": 99},
        "uso_maximo": 1,
    },
    "hidan__base": {
        "nome": "Ritual de Sangue Jashin",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"aggro_max": True, "reflete_dano": 40, "turnos": 2},
    },
    "hidan__evo_5": {
        "nome": "Imortalidade Amaldiçoada",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"imortalidade_turnos": 2, "heal_damage_received": 0.10, "turnos": 2},
    },
    "zeldris__base": {
        "nome": "Nebula Ominosa (Ominous Nebula)",
        "tipo": "debuff",
        "alvo": "todos_inimigos",
        "efeito": {"debuff_spd": 30, "debuff_acc": 25, "turnos": 2},
    },
    "zeldris__evo_5": {
        "nome": "Mandamento da Piedade",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_atk": 1.5, "ignora_def": True, "silence_turnos": 1},
    },
    "ulquiorra__base": {
        "nome": "Regeneração de Alta Velocidade",
        "tipo": "cura",
        "alvo": "self",
        "efeito": {"cura_percent_max": 0.40},
    },
    "ulquiorra__evo_5": {
        "nome": "Segunda Etapa: Lanza de Relâmpago",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_matk": 2.0, "ignora_def_escudos": True},
    },
    "regulus_corneas__base": {
        "nome": "Autoridade da Ganância: Imutabilidade",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"imunidade_dano_turnos": 2, "imunidade_debuffs": True, "turnos": 2},
    },
    "regulus_corneas__evo_7": {
        "nome": "O Sopro de Cascalho Silencioso",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_atk": 1.8, "ignora_def_escudos": True},
    },
    "pain__base": {
        "nome": "Shinra Tensei (Repulsão Divina)",
        "tipo": "buff",
        "alvo": "todos_aliados",
        "efeito": {"buff_dodge": 25, "reduz_dano_recebido": 20, "turnos": 2},
    },
    "pain__evo_7": {
        "nome": "Chibaku Tensei (Atração Planetária)",
        "tipo": "debuff",
        "alvo": "todos_inimigos",
        "efeito": {"stun_turnos": 1, "remove_todos_buffs": True, "debuff_def": 25, "turnos": 2},
    },
    "bondrewd__base": {
        "nome": "Cartuchos de Bênção",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_def": 35, "cura_turnos": 25, "turnos": 3},
    },
    "bondrewd__evo_5": {
        "nome": "Receptor de Consciência: Zoaholic",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"revive_hp": 0.50, "protege_aliados_fatal": True, "turnos": 99},
        "uso_maximo": 1,
    },
    "shigaraki__base": {
        "nome": "Decaimento de Área",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_atk": 1.4, "debuff_def": 50, "turnos": 3},
    },
    "shigaraki__evo_5": {
        "nome": "Hiper-Regeneração Biológica",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"cura_turnos": 12, "revive_hp": 0.20, "turnos": 99},
        "uso_maximo": 1,
    },
    "freeza__base": {
        "nome": "Fisiologia de Sobrevivência Cósmica",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"reduz_dano_recebido": 40, "reflete_dano": 20, "turnos": 99},
        "uso_maximo": 1,
    },
    "freeza__evo_7": {
        "nome": "Forma Dourada: Golden Freeza",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_def": 50, "buff_atk": 50, "stun_atacante_on_hit": 1, "turnos": 3},
    },
    "coyote_starrk__base": {
        "nome": "Cero Metralhadora",
        "tipo": "dano",
        "alvo": "inimigos_aleatorios",
        "quantidade": 3,
        "efeito": {"multiplicador_atk": 1.8},
    },
    "coyote_starrk__evo_5": {
        "nome": "Los Lobos: Matilha de Almas",
        "tipo": "dano",
        "alvo": "inimigo_maior_spd",
        "efeito": {"multiplicador_matk": 1.4, "debuff_matk": 30, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 2}},
    },
    "envy__base": {
        "nome": "Metamorfose Infiltradora",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_dodge": 30, "buff_atk": 100, "turnos": 1},
    },
    "envy__evo_5": {
        "nome": "Forma Verdadeira de Quimera",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_atk": 2.0, "stun_turnos": 1, "debuff_acc": 50, "turnos": 2},
    },
    "elsa_granhiert__base": {
        "nome": "Fatiadora de Entranhas",
        "tipo": "dano",
        "alvo": "unico_inimigo",
        "efeito": {"multiplicador_atk": 1.8, "critico_garantido": True, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.3, "turnos": 3}},
    },
    "elsa_granhiert__evo_5": {
        "nome": "Evasão Vampírica Sobrenatural",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_dodge": 40, "counter_atk_percent": 1.20, "turnos": 3},
    },
    "twice__base": {
        "nome": "Multiplicação Caótica",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"buff_dodge": 30, "reduz_dano_recebido": 30, "turnos": 3},
    },
    "twice__evo_5": {
        "nome": "Marcha do Homem Só",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_atk": 1.4, "debuff_acc": 30, "turnos": 3},
    },
    "buggy__base": {
        "nome": "Bara Bara no Mi: Divisão Corporal",
        "tipo": "buff",
        "alvo": "self",
        "efeito": {"ignora_dano_fisico": True, "imune_toxinas": True, "turnos": 3},
    },
    "buggy__evo_5": {
        "nome": "Muggy Ball: Canhão de Sapatos",
        "tipo": "dano",
        "alvo": "todos_inimigos",
        "efeito": {"multiplicador_atk": 2.2, "dot": {"tipo": "fogo", "base": "atk", "mult": 0.3, "turnos": 2}},
    },
    "team_rocket__base": {
        "nome": "Armadilha de Rede Elétrica",
        "tipo": "debuff",
        "alvo": "inimigos_aleatorios",
        "quantidade": 2,
        "efeito": {"stun_turnos": 1, "debuff_spd": 20, "turnos": 1},
    },
    "team_rocket__evo_5": {
        "nome": "Decolando na Velocidade da Luz!",
        "tipo": "buff",
        "alvo": "todos_aliados",
        "efeito": {"reduz_dano_recebido": 40, "turnos": 2},
    },
    "mama_isabella__base": {
        "nome": "Rastreamento Frio de Fugitivos",
        "tipo": "debuff",
        "alvo": "inimigo_maior_spd",
        "efeito": {"silence_turnos": 2, "debuff_spd": 50, "turnos": 2},
    },
    "mama_isabella__evo_5": {
        "nome": "O Olhar Gelado do Orfanato",
        "tipo": "debuff",
        "alvo": "todos_inimigos",
        "efeito": {"fear_turnos": 1, "debuff_atk": 25, "debuff_matk": 25, "turnos": 99},
    },
}

SKILLS.update({
    # Reforços 325-385: habilidades explícitas para não depender do gerador automático.
    "zeref_dragneel__base": {"nome": "Magia Negra de Ankhselam", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "dot": {"tipo": "maldicao", "base": "matk", "mult": 0.5, "turnos": 3}, "ignora_def": True}},
    "zeref_dragneel__evo_7": {"nome": "Conjurador de Demônios", "tipo": "escudo", "alvo": "todos_aliados", "efeito": {"escudo_hp_max": 0.30, "silence_todos_inimigos": 1, "turnos": 2}},
    "toguro_ototo__base": {"nome": "Brutalidade Muscular", "tipo": "buff", "alvo": "self", "efeito": {"reduz_dano_recebido": 35, "reflete_dano": 25, "turnos": 2}},
    "toguro_ototo__evo_7": {"nome": "Absorção de Almas", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.0, "dano_hp_atual": 0.05, "lifesteal_global": 1.0}},
    "kars_supremo__base": {"nome": "Adaptação Biológica", "tipo": "buff", "alvo": "self", "efeito": {"remove_debuffs": True, "imunidade_debuffs": True, "cura_turnos": 12, "turnos": 99}},
    "kars_supremo__evo_7": {"nome": "Imortalidade do Ápice", "tipo": "buff", "alvo": "self", "efeito": {"revive_hp": 0.50, "imunidade_dano_turnos": 1, "turnos": 99}, "uso_maximo": 1},
    "nnoitra_gilga__base": {"nome": "O Hierro Mais Duro", "tipo": "escudo", "alvo": "self", "efeito": {"escudo_hp_max": 0.40, "turnos": 99}, "uso_maximo": 1},
    "nnoitra_gilga__evo_5": {"nome": "Santa Teresa", "tipo": "buff", "alvo": "self", "efeito": {"counter_atk_percent": 1.20, "buff_atk": 20, "turnos": 3}},
    "muscular_mha__base": {"nome": "Fibras de Carne Blindadas", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 60, "buff_hp": 20, "turnos": 3}},
    "muscular_mha__evo_5": {"nome": "Pancada Devastadora", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.6, "stun_turnos": 1}},
    "overgrown_rover__base": {"nome": "Guarda Canina Imperial", "tipo": "buff", "alvo": "self", "efeito": {"aggro_max": True, "reduz_dano_recebido": 30, "turnos": 3}},
    "overgrown_rover__evo_5": {"nome": "Esferas de Energia Consecutivas", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_matk": 1.4, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 2}}},
    "hisoka_morow__base": {"nome": "Bungee Gum", "tipo": "debuff", "alvo": "inimigo_maior_spd", "efeito": {"debuff_spd": 50, "debuff_acc": 25, "turnos": 2}},
    "hisoka_morow__evo_7": {"nome": "Textura Surpresa", "tipo": "buff", "alvo": "self", "efeito": {"buff_dodge": 50, "buff_crt": 50, "turnos": 2}},
    "illumi_zoldyck__base": {"nome": "Agulhas de Lavagem Cerebral", "tipo": "debuff", "alvo": "inimigo_maior_atk", "efeito": {"silence_turnos": 2, "confusao": True, "turnos": 2}},
    "illumi_zoldyck__evo_5": {"nome": "Disfarce Sem Rosto", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_dano_turnos": 1, "remove_debuffs": True, "turnos": 1}},
    "sonic_opm__base": {"nome": "Velocidade Sônica", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 30, "buff_dodge": 20, "turnos": 3}},
    "sonic_opm__evo_5": {"nome": "Shurikens Explosivas", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_atk": 1.5, "debuff_def": 30, "turnos": 2}},
    "kurome_akame__base": {"nome": "Yatsufusa: Coleção de Cadáveres", "tipo": "dano", "alvo": "inimigo_menor_hp", "efeito": {"multiplicador_atk": 1.6, "bloqueia_reviver_ao_matar": True}},
    "kurome_akame__evo_5": {"nome": "Corte de Drogas Estimulantes", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 30, "buff_crt": 30, "turnos": 3}},
    "deidara_naruto__base": {"nome": "Argila Explosiva C3", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.8, "dot": {"tipo": "fogo", "base": "atk", "mult": 0.3, "turnos": 1}}},
    "deidara_naruto__evo_5": {"nome": "C4 Karura: Micro-Bombas", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"dot": {"tipo": "bomba", "base": "atk", "mult": 1.0, "turnos": 2}, "ignora_def_escudos": True}},
    "enel_onepiece__base": {"nome": "El Thor: Julgamento Relâmpago", "tipo": "dano", "alvo": "inimigo_maior_spd", "efeito": {"multiplicador_matk": 1.9, "stun_turnos": 1}},
    "enel_onepiece__evo_5": {"nome": "Amaru: 200M Volts", "tipo": "buff", "alvo": "self", "efeito": {"buff_matk": 40, "imune_lentidao": True, "turnos": 3}},
    "lille_barro__base": {"nome": "Perfuração Perfeita", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "ignora_def_escudos": True}},
    "lille_barro__evo_7": {"nome": "Jilliel: Forma Divina de Luz", "tipo": "buff", "alvo": "self", "efeito": {"ignora_dano_fisico": True, "ignora_def_on_hit": 50, "buff_atk": 20, "turnos": 3}},
    "hol_horse_jojo__base": {"nome": "O Imperador (The Emperor)", "tipo": "buff", "alvo": "self", "efeito": {"buff_acc": 100, "buff_crt": 30, "turnos": 99}, "uso_maximo": 1},
    "hol_horse_jojo__evo_5": {"nome": "Parceria Covarde", "tipo": "dano", "alvo": "inimigo_maior_atk", "efeito": {"multiplicador_atk": 2.0, "critico_garantido": True}},
    "bambietta__base": {"nome": "Explosão de Reishi", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.5, "remove_escudos": True, "aplica_fraqueza": 25}},
    "bambietta__evo_5": {"nome": "Vollständig: Divina Explosão", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.8, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.4, "turnos": 3}}},
    "kyubey_madoka__base": {"nome": "Contrato da Incubadora", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_atk": 50, "buff_matk": 50, "dot_self": 10, "turnos": 3}},
    "kyubey_madoka__evo_7": {"nome": "Coleta de Desespero", "tipo": "escudo", "alvo": "aliado_maior_atk", "efeito": {"escudo_hp_max": 0.15, "turnos": 3}},
    "kabuto_eremita__base": {"nome": "Transmissão de Fluidos Médicos", "tipo": "buff", "alvo": "aliado_menor_hp", "efeito": {"cura_turnos": 25, "turnos": 3}},
    "kabuto_eremita__evo_5": {"nome": "Reanimação Orgânica Inorgânica", "tipo": "reviver", "alvo": "aliado_morto_aleatorio", "efeito": {"hp_percent": 0.20, "remove_todos_debuffs": True}},
    "overhaul_kai__base": {"nome": "Desonstrução e Reconstrução", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.45, "remove_todos_debuffs": True}},
    "overhaul_kai__evo_5": {"nome": "Fusão de Carne Biológica", "tipo": "buff", "alvo": "self", "efeito": {"buff_def": 50, "heal_damage_received": 0.30, "turnos": 3}},
    "shaiapouf_hxh__base": {"nome": "Escamas de Hipnose Espiritual", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_atk": 30, "debuff_matk": 30, "turnos": 2}},
    "shaiapouf_hxh__evo_5": {"nome": "Divisão de Células de Pouf", "tipo": "escudo", "alvo": "todos_aliados", "efeito": {"escudo_hp_max": 0.20, "buff_spd": 30, "turnos": 2}},
    "szayelaporro_granz__base": {"nome": "Criação de Boneco Vodu", "tipo": "debuff", "alvo": "inimigo_maior_atk", "efeito": {"dano_recebido_extra": 40, "turnos": 3}},
    "szayelaporro_granz__evo_5": {"nome": "Replicação de Órgãos", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 0.30, "imune_toxinas": True, "turnos": 3}},
    "mash_kyrielight__base": {"nome": "Lord Chaldeas", "tipo": "escudo", "alvo": "self", "efeito": {"escudo_hp_max": 0.30, "aggro_max": True, "turnos": 2}},
    "mash_kyrielight__evo_5": {"nome": "Lord Camelot", "tipo": "escudo", "alvo": "todos_aliados", "efeito": {"imunidade_dano_turnos": 1, "buff_def": 50, "turnos": 3}},
    "jeanne_d_arc__base": {"nome": "Luminosité Eternelle", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"ignora_dano_magico": True, "reduz_dano_recebido": 25, "turnos": 2}},
    "jeanne_d_arc__evo_7": {"nome": "La Pucelle", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.5, "remove_todos_buffs": True, "ignora_def": True}},
    "king_hassan__base": {"nome": "Azrael: O Anjo da Morte", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "chance_insta_kill": 0.10, "restricao": "nao_afeta_boss"}},
    "king_hassan__evo_7": {"nome": "Sino do Fim", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_atk": 40, "debuff_matk": 40, "turnos": 3}},
    "obito_uchiha__base": {"nome": "Kamui: Intangibilidade", "tipo": "buff", "alvo": "self", "efeito": {"imunidade_dano_turnos": 2, "counter_atk_percent": 1.50, "turnos": 2}},
    "obito_uchiha__evo_7": {"nome": "Gedo Mazo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.6, "silence_turnos": 1, "debuff_spd": 25, "turnos": 2}},
    "soifon__base": {"nome": "Suzumebachi: Duas Picadas", "tipo": "dano", "alvo": "inimigo_menor_hp", "efeito": {"multiplicador_atk": 1.6, "aplica_fraqueza": 25, "turnos": 2}},
    "soifon__evo_5": {"nome": "Shunko Espiritual", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 40, "ignora_def_on_hit": 100, "turnos": 2}},
    "suzuya_juuzou__base": {"nome": "Scorpion 1/56", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.4, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.3, "turnos": 2}}},
    "suzuya_juuzou__evo_5": {"nome": "Jason do CCG: Foice Gigante", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 2.2, "critico_garantido": True}},
    "feitan_portor__base": {"nome": "Pain Packer: Sol Nascente", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.0, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.4, "turnos": 3}}},
    "feitan_portor__evo_5": {"nome": "Corte de Sombra Veloz", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.8, "remove_escudos": True, "bloqueia_buffs": True, "turnos": 2}},
    "souei__base": {"nome": "Fios Invisíveis de Aço", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_atk": 1.3, "silence_turnos": 2}},
    "souei__evo_5": {"nome": "Teletransporte de Sombra", "tipo": "buff", "alvo": "self", "efeito": {"buff_dodge": 35, "buff_atk": 25, "turnos": 3}},
    "archer_emiya__base": {"nome": "Caladbolg II: Flecha de Espadas", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.9, "debuff_def": 40, "turnos": 3}},
    "archer_emiya__evo_7": {"nome": "Unlimited Blade Works", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.5, "debuff_def": 30, "turnos": 2}},
    "ishtar_fgo__base": {"nome": "An Gal Ta Kigal She", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.8, "debuff_atk": 30, "turnos": 2}},
    "ishtar_fgo__evo_7": {"nome": "Disparo Cósmico de Vênus", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.8, "critico_garantido": True, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.4, "turnos": 3}}},
    "van_augur__base": {"nome": "Tiro de Precisão de Longo Alcance", "tipo": "dano", "alvo": "inimigo_menor_hp", "efeito": {"multiplicador_atk": 1.8, "ignora_def": 35}},
    "van_augur__evo_5": {"nome": "Warp: Deslocamento Espacial", "tipo": "buff", "alvo": "self", "efeito": {"ignora_dano_fisico": True, "remove_debuffs": True, "turnos": 1}},
    "yasopp__base": {"nome": "Disparos Rápidos de Pistola", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_hit": 4, "multiplicador_atk": 0.5, "dot": {"tipo": "sangramento", "base": "atk", "mult": 0.2, "turnos": 3}}},
    "yasopp__evo_5": {"nome": "Pontaria do Atirador Lendário", "tipo": "buff", "alvo": "self", "efeito": {"buff_crt": 35, "ignora_def_on_hit": 40, "turnos": 99}, "uso_maximo": 1},
    "sasha_blouse__base": {"nome": "Tiro do Caçador", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.3, "debuff_acc": 15, "turnos": 2}},
    "sasha_blouse__evo_3": {"nome": "Instinto Alimentar", "tipo": "cura", "alvo": "self", "efeito": {"cura_percent_max": 0.20, "buff_atk": 20, "turnos": 2}},
    "sasha_blouse__evo_5": {"nome": "Faro de Saque", "tipo": "buff", "alvo": "self", "efeito": {"buff_acc": 10, "turnos": 99}, "uso_maximo": 1},
    "mey_rin__base": {"nome": "Remoção dos Óculos", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 30, "buff_crt": 20, "turnos": 3}},
    "mey_rin__evo_3": {"nome": "Pistolas Duplas Rápidas", "tipo": "dano", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"multiplicador_hit": 3, "multiplicador_atk": 0.5}},
    "mey_rin__evo_5": {"nome": "Fogo de Supressão do Telhado", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_acc": 30, "turnos": 3}},
    "yoichi_saotome__base": {"nome": "Gekkouin: Flecha Teleguiada", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.5, "debuff_acc": 25, "turnos": 2}},
    "yoichi_saotome__evo_5": {"nome": "Força de Vontade Demoníaca", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 30, "chance_lentidao_on_hit": 1.0, "turnos": 3}},
    "shinya_hiiragi__base": {"nome": "Baiakuran: Tigre de Fogo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.6, "dot": {"tipo": "fogo", "base": "atk", "mult": 0.3, "turnos": 3}}},
    "shinya_hiiragi__evo_5": {"nome": "Fogo Cruzado com a Retaguarda", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.2, "stun_curador_inimigo": 1}},
    "foo_fighters__base": {"nome": "Disparos de Plâncton", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.3, "lifesteal": 0.25}},
    "foo_fighters__evo_5": {"nome": "Restauração Aquosa", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"cura_percent_max": 0.20, "remove_todos_debuffs": True}},
    "lugh_tuatha_de__base": {"nome": "Sniper de Tungstênio", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "ignora_def": 50, "remove_escudos": True}},
    "lugh_tuatha_de__evo_5": {"nome": "Modo Assassino Perfeito", "tipo": "buff", "alvo": "self", "efeito": {"lifesteal_on_hit": 0.25, "ignora_def_on_hit": 40, "buff_acc": 50, "turnos": 3}},
    "franklin_bordeau__base": {"nome": "Double Machine Gun", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.5}},
    "franklin_bordeau__evo_5": {"nome": "Fogo de Supressão do Grupo", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_def": 30, "turnos": 3}},
    "pokkle__base": {"nome": "Flecha Vermelha (Fogo)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 1.2, "dot": {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": 2}}},
    "pokkle__evo_3": {"nome": "Flecha Amarela (Velocidade)", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.0, "buff_spd": 30}},
    "pokkle__evo_5": {"nome": "Arco das Sete Cores (Nen)", "tipo": "buff", "alvo": "self", "efeito": {"aplica_veneno_on_hit": 0.35, "chance_stun": 0.20, "turnos": 99}, "uso_maximo": 1},
    "kamo_noritoshi__base": {"nome": "Flecha de Sangue Manipulado", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.4, "lifesteal": 0.30}},
    "kamo_noritoshi__evo_5": {"nome": "Selo de Escamas Vermelhas", "tipo": "buff", "alvo": "self", "efeito": {"buff_spd": 30, "buff_atk": 20, "buff_def": 15, "turnos": 3}},
    "mai_zenin__base": {"nome": "Disparo do Revólver", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.1}},
    "mai_zenin__evo_3": {"nome": "Construção de Bala", "tipo": "buff", "alvo": "self", "efeito": {"ignora_def_on_hit": 30, "turnos": 2}},
    "mai_zenin__evo_5": {"nome": "Fogo de Supressão", "tipo": "debuff", "alvo": "inimigo_maior_spd", "efeito": {"debuff_atk": 15, "turnos": 2}},
    "yuri_nakamura__base": {"nome": "Comando de Fogo da SSS", "tipo": "dano", "alvo": "inimigo_maior_atk", "efeito": {"multiplicador_atk": 1.5, "buff_crt": 15, "turnos": 2}},
    "yuri_nakamura__evo_5": {"nome": "Rebelião Contra os Deuses", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"imune_stun": True, "imune_medo": True, "turnos": 3}},
    "tigrevurmud_vorn__base": {"nome": "Arco Negro dos Ventos", "tipo": "dano", "alvo": "inimigo_maior_spd", "efeito": {"multiplicador_atk": 1.6, "silence_turnos": 1, "debuff_spd": 25, "turnos": 1}},
    "tigrevurmud_vorn__evo_5": {"nome": "Tiro do Caçador Lendário", "tipo": "buff", "alvo": "self", "efeito": {"buff_acc": 100, "buff_crt": 40, "turnos": 3}},
    "pip_bernadotte__base": {"nome": "Tiro do Mercenário", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.3, "debuff_def": 15, "turnos": 2}},
    "pip_bernadotte__evo_3": {"nome": "Lança-Granadas de Fumaça", "tipo": "buff", "alvo": "aliado_maior_atk", "efeito": {"buff_dodge": 30, "turnos": 1}},
    "pip_bernadotte__evo_5": {"nome": "Esquadrão Ganso Selvagem", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 1.6, "remove_todos_buffs": True}},
    "beyond_the_grave__base": {"nome": "Metralhadora Cerberus", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.8, "anti_cura": True, "turnos": 2}},
    "beyond_the_grave__evo_5": {"nome": "Disparo do Caixão Balístico", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.5, "remove_escudos": True}},
    "heero_yuy__base": {"nome": "Buster Rifle de Feixe Térmico", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"soma_atk_matk": True, "multiplicador_soma_atk_matk": 2.2, "ignora_def_escudos": True}},
    "heero_yuy__evo_7": {"nome": "Sistema ZERO", "tipo": "buff", "alvo": "self", "efeito": {"buff_acc": 100, "buff_dodge": 30, "buff_spd": 30, "turnos": 3}},
    "zwei_phantom__base": {"nome": "Execução Silenciosa", "tipo": "dano", "alvo": "inimigo_menor_hp", "efeito": {"multiplicador_atk": 1.6, "ignora_def": 30}},
    "zwei_phantom__evo_5": {"nome": "Phantom do Submundo", "tipo": "buff", "alvo": "self", "efeito": {"buff_dodge": 40, "buff_crt": 50, "ignora_def_on_hit": 30, "turnos": 2}},
    "waver_velvet__base": {"nome": "Estratégia de Lord El-Melloi II", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 30, "buff_atk": 25, "buff_matk": 25, "turnos": 3}},
    "waver_velvet__evo_7": {"nome": "Unreturned Army", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"silence_turnos": 2, "remove_todos_buffs": True, "turnos": 2}},
    "tamamo_no_mae__base": {"nome": "Amaterasu: Espelho Celestial", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 0.35, "reduz_cooldown": 1}},
    "tamamo_no_mae__evo_7": {"nome": "Banquete das Nove Caudas", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"imune_cc": True, "cura_turnos": 15, "turnos": 2}},
    "eri_mha__base": {"nome": "Rebobinar Estado Corporal", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.50, "remove_todos_debuffs": True}},
    "eri_mha__evo_5": {"nome": "Reversão Temporal Suprema", "tipo": "buff", "alvo": "self", "efeito": {"protege_aliados_fatal": True, "revive_hp": 1.0, "turnos": 99}, "uso_maximo": 1},
    "reigen_arataka__base": {"nome": "Purificação de Sal de Cozinha", "tipo": "dano", "alvo": "inimigo_maior_atk", "efeito": {"multiplicador_atk": 0.8, "chance_stun": 0.40, "stun_turnos": 1}},
    "reigen_arataka__evo_3": {"nome": "Massagem de Ombros Relaxante", "tipo": "cura", "alvo": "aliado_maior_atk", "efeito": {"cura_percent_max": 0.15, "buff_atk": 15, "turnos": 2}},
    "reigen_arataka__evo_5": {"nome": "Conselho de Mestre Genuíno", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 25, "turnos": 3}},
    "morgana_persona__base": {"nome": "Magia Garu: Vento Curativo", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 0.30, "buff_spd": 15, "turnos": 2}},
    "morgana_persona__evo_5": {"nome": "Salvação de Morgana (Mediaharan)", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 0.25, "remove_todos_debuffs": True}},
    "mimosa_vermillion__base": {"nome": "Manto Curativo de Flores", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.35, "buff_def": 30, "turnos": 2}},
    "mimosa_vermillion__evo_5": {"nome": "Flor Guia do Berço Sagrado", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"cura_turnos": 15, "turnos": 3}},
    "charmy_pappitson__base": {"nome": "Ovelha Cozinheira de Resgate", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 0.20, "reduz_cooldown": 1}},
    "charmy_pappitson__evo_5": {"nome": "Ovelha Gigante Devoradora", "tipo": "dano", "alvo": "inimigo_maior_atk", "efeito": {"multiplicador_matk": 1.8, "debuff_atk": 30, "turnos": 2}},
    "sherria_blendy__base": {"nome": "Magia de God Slayer dos Céus", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"cura_percent_max": 0.25, "buff_spd": 20, "turnos": 2}},
    "sherria_blendy__evo_5": {"nome": "Coleta Espiritual de Terzo", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 0.20, "remove_todos_debuffs": True}},
    "asia_argento__base": {"nome": "Twilight Healing: Crepúsculo", "tipo": "cura", "alvo": "aliado_maior_atk", "efeito": {"multiplicador_matk": 0.30, "remove_todos_debuffs": True}},
    "asia_argento__evo_3": {"nome": "Prece de Resistência Divina", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_def": 20, "turnos": 2}},
    "asia_argento__evo_5": {"nome": "Oração de Cura Contínua", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"cura_turnos": 8, "turnos": 3}},
    "dende_dbz__base": {"nome": "Cura Namekuseijin Espiritual", "tipo": "cura", "alvo": "aliado_maior_atk", "efeito": {"cura_percent_max": 0.45, "remove_todos_debuffs": True}},
    "dende_dbz__evo_5": {"nome": "Bênção das Esferas de Namek", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"ignora_dano_magico": True, "turnos": 2}},
    "yosuke_hanamura__base": {"nome": "Junes: Promoção Espetacular", "tipo": "buff", "alvo": "todos_aliados", "efeito": {"buff_spd": 25, "buff_acc": 25, "turnos": 2}},
    "yosuke_hanamura__evo_5": {"nome": "Persona Jiraiya: Vento Divino", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 0.15, "remove_todos_debuffs": True}},
    "shizuka_marikawa__base": {"nome": "Curativo Distraído", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 0.25, "remove_todos_debuffs": True}},
    "shizuka_marikawa__evo_3": {"nome": "Anestésico Científico", "tipo": "buff", "alvo": "aliado_menor_hp", "efeito": {"imune_stun": True, "reduz_dano_recebido": 20, "turnos": 2}},
    "shizuka_marikawa__evo_5": {"nome": "Tratamento Médico Total", "tipo": "cura", "alvo": "todos_aliados", "efeito": {"multiplicador_matk": 0.15, "buff_def": 20, "turnos": 2}},
    "nanao_ise__base": {"nome": "Barreira Hakudan Keikai", "tipo": "escudo", "alvo": "todos_aliados", "efeito": {"escudo_hp_max": 0.30, "ignora_dano_magico": True, "turnos": 1}},
    "nanao_ise__evo_5": {"nome": "Corte de Kido Espiritual", "tipo": "cura", "alvo": "aliado_menor_hp", "efeito": {"multiplicador_matk": 0.30, "silence_turnos": 1}},
})


def _skill_key(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _first_percent(text, default=None):
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*%", text)
    if not match:
        return default
    return float(match.group(1).replace(",", "."))


def _has_word(text, word):
    return re.search(rf"(?:^|_){re.escape(word)}(?:_|$)", text) is not None


def _catalog_skill_definition(skill_data, rarity=1):
    name = str(skill_data.get("nome", "Habilidade"))
    description = str(skill_data.get("descricao", ""))
    text = _skill_key(f"{name} {description}")
    desc_key = _skill_key(description)
    percent = _first_percent(description)
    turns_match = re.search(r"(\d+)\s*(?:turn|rodad)", description.lower())
    turns = int(turns_match.group(1)) if turns_match else 3

    def has_any(tokens):
        return any(token in text for token in tokens)

    def cap(value, limit):
        try:
            return min(float(value), limit)
        except (TypeError, ValueError):
            return limit

    def damage_percent_for(stat):
        match = re.search(rf"(?:causa|causando|causar|desfere|atinge|inflige|arremata|chute|golpe|corte|disparo|tiro|impacto|retalhando|devolve|retalia)[a-z0-9_]*_(\d+(?:[_,]\d+)?)_de_{stat}", desc_key)
        if not match:
            return None
        try:
            return float(match.group(1).replace("_", ".").replace(",", "."))
        except ValueError:
            return None

    def stat_percent(stat, mode):
        verbs = {
            "buff": ["aumenta", "ganha", "concede", "recebe", "fortalece", "eleva", "buff"],
            "debuff": ["reduz", "diminui", "remove", "enfraquece", "quebra", "rompe", "debuff"],
        }[mode]
        stat_aliases = [stat]
        if stat == "atk":
            stat_aliases.append("ataque")
        if stat == "matk":
            stat_aliases.extend(["magia", "magico", "magica"])
        if stat == "def":
            stat_aliases.extend(["defesa", "defesas"])
        if stat == "spd":
            stat_aliases.append("velocidade")
        if stat == "crt":
            stat_aliases.extend(["critico", "critica"])
        if stat == "acc":
            stat_aliases.extend(["precisao", "acerto"])
        if stat == "dodge":
            stat_aliases.extend(["evasao", "esquiva"])
        for verb in verbs:
            for alias in stat_aliases:
                patterns = [
                    rf"{verb}[a-z0-9_]*?_{alias}[a-z0-9_]*?_(\d+(?:[_,]\d+)?)",
                    rf"{verb}[a-z0-9_]*?_(\d+(?:[_,]\d+)?)_de_{alias}",
                    rf"{verb}[a-z0-9_]*?_(\d+(?:[_,]\d+)?)[a-z0-9_]*?_{alias}",
                ]
                for pattern in patterns:
                    match = re.search(pattern, desc_key)
                    if match:
                        try:
                            return float(match.group(1).replace("_", ".").replace(",", "."))
                        except ValueError:
                            return None
        return None

    def chance_percent():
        patterns = [
            r"(\d+(?:[_,]\d+)?)_de_chance",
            r"chance_de_(\d+(?:[_,]\d+)?)",
            r"chance[a-z0-9_]*?_(\d+(?:[_,]\d+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, desc_key)
            if not match:
                continue
            try:
                return float(match.group(1).replace("_", ".").replace(",", "."))
            except ValueError:
                return None
        return None

    target = "unico_inimigo"
    if has_any(["todos_os_inimigos", "equipe_inimiga", "em_area", "campo_inimigo", "atingindo_todos_os_inimigos", "todos_inimigos"]):
        target = "todos_inimigos"
    elif has_any(["todos_os_aliados", "equipe_inteira", "toda_a_equipe", "todos_da_equipe", "todo_o_grupo", "sua_equipe", "alianca", "todos_aliados", "grupo_inteiro"]):
        target = "todos_aliados"

    damage_terms = [
        "causa", "causando", "desfere", "atinge", "inflige", "arremata", "chute",
        "golpe", "golpeia", "corte", "disparo", "tiro", "impacto", "retalha", "retalhando", "devolve", "retalia", "lanca", "lança",
    ]
    atk_damage_percent = damage_percent_for("atk")
    matk_damage_percent = damage_percent_for("matk")
    has_damage_percent = atk_damage_percent is not None or matk_damage_percent is not None
    damage_trigger = has_damage_percent or any(_has_word(text, token) for token in damage_terms)

    negative_heal = has_any(["anti_cura", "curas_inimigas", "cura_inimiga", "eficacia_de_curas", "corta_cura"])
    is_heal = not negative_heal and has_any(["cura_o", "cura_um", "cura_todos", "curativo", "recupera_hp", "recuperacao", "restaura", "restaura_hp", "beijo_de_cura", "manto_curativo"])
    is_revive = has_any(["revive", "reviver", "ressuscita", "ressurreicao"])
    is_execute = has_any(["morte_instantanea", "insta_kill", "executa"])
    is_summon = has_any(["cria_clone", "invoca_clone", "invoca_um_clone", "invoca_monstro", "invoca_servo", "invoca_invocacao"]) or ("invoca" in text and not damage_trigger)
    is_shield = has_any(["barreira_protetora", "escudo_protetor", "escudo_mistico", "concede_um_escudo", "protege_a_equipe", "protege_o_time", "protege_o_grupo", "absorvendo_todo_dano", "muralha", "guarda"]) and not has_any(["ignora_escudo", "ignoram_escudo", "destroi_escudo", "destruir_escudo"])
    is_debuff = has_any(["reduz", "diminui", "debuff", "atordoa", "stun", "silencia", "fraqueza", "congela", "confusao", "medo"])
    is_debuff = is_debuff or ("lentidao" in text and has_any(["aplica", "causa_lentidao", "reduz_a_velocidade"]))
    is_buff = has_any(["aumenta", "ganha", "concede", "fortalece", "forma_", "modo_", "buff", "transforma", "fica_imune", "imune", "seus_ataques", "suas_habilidades", "passa_a", "passam_a", "atrai_ataques", "reduz_pela_metade", "reduz_50_de_todo"])
    self_modifier = has_any(["seus_ataques", "suas_habilidades", "seu_ataque", "ataques_normais", "passa_a", "passam_a", "atrai_ataques", "ferimentos_da_party", "sofrido_por_ele_mesmo", "reduz_50_de_todo"])

    skill_type = "dano"
    effect = {}

    if damage_trigger:
        skill_type = "dano"
        base_multiplier = 1.15 + min(0.85, max(0, int(rarity or 1) - 1) * 0.17)
        if has_any(["dano_massivo", "golpe_massivo", "grande_dano", "dano_pesado", "devastador", "destrutivo"]):
            base_multiplier += 0.35
        if matk_damage_percent is not None or (atk_damage_percent is None and has_any(["magia", "mana", "fogo", "gelo", "raio", "relampago", "eletricidade", "explosao"])):
            effect["multiplicador_matk"] = (matk_damage_percent / 100) if matk_damage_percent and matk_damage_percent >= 100 else base_multiplier
            damage_base = "matk"
        else:
            effect["multiplicador_atk"] = (atk_damage_percent / 100) if atk_damage_percent and atk_damage_percent >= 100 else base_multiplier
            damage_base = "atk"
    elif is_revive:
        skill_type = "reviver"
        target = "aliado_morto_aleatorio"
        effect = {"hp_percent": (percent or 50) / 100}
        damage_base = "matk"
    elif is_execute:
        skill_type = "insta_kill"
        effect["chance_insta_kill"] = (percent or 20) / 100
        effect["restricao"] = "nao_afeta_boss"
        effect["multiplicador_atk"] = 1.8
        damage_base = "atk"
    elif is_summon:
        skill_type = "invocacao"
        target = "campo"
        effect["invocar"] = {"id": "minion", "nome": "Invocação", "hp_percent": 0.45, "atk_percent": 0.45, "comportamento": "atacar", "turnos": turns}
        damage_base = "atk"
    elif is_heal:
        skill_type = "cura"
        target = "todos_aliados" if target == "todos_aliados" else "aliado_menor_hp"
        if "matk" in text:
            effect["multiplicador_matk"] = min((percent or 35) / 100, 0.60)
        else:
            effect["cura_percent_max"] = min((percent or 20) / 100, 0.45)
        damage_base = "matk"
    elif is_shield:
        skill_type = "escudo"
        target = "todos_aliados" if target == "todos_aliados" else "self"
        effect["escudo_hp_max"] = min((percent or 25) / 100, 0.45)
        damage_base = "def"
    elif is_buff and (self_modifier or not is_debuff):
        skill_type = "buff"
        target = "todos_aliados" if target == "todos_aliados" else "self"
        damage_base = "atk"
    elif is_debuff:
        skill_type = "debuff"
        damage_base = "atk"
    else:
        damage_base = "atk"

    stat_tokens = {
        "atk": "atk",
        "ataque": "atk",
        "matk": "matk",
        "magia": "matk",
        "magico": "matk",
        "magica": "matk",
        "def": "def",
        "defesa": "def",
        "defesas": "def",
        "spd": "spd",
        "velocidade": "spd",
        "acc": "acc",
        "precisao": "acc",
        "acerto": "acc",
        "dodge": "dodge",
        "evasao": "dodge",
        "esquiva": "dodge",
        "crt": "crt",
        "critico": "crt",
        "critica": "crt",
    }
    seen_stats = set()
    for token, stat in stat_tokens.items():
        if stat in seen_stats or not _has_word(text, token):
            continue
        seen_stats.add(stat)
        debuff_value = stat_percent(stat, "debuff")
        buff_value = stat_percent(stat, "buff")
        if stat == "matk" and debuff_value is not None and has_any(["dano_magico", "ataque_magico"]) and has_any(["reduz_pela_metade", "todo_e_qualquer_dano", "reduz_50_de_todo"]):
            debuff_value = None
        if debuff_value is not None:
            effect.setdefault(f"debuff_{stat}", cap(debuff_value, 50))
        elif buff_value is not None:
            effect.setdefault(f"buff_{stat}", cap(buff_value, 50))
        debuff_near_stat = any(
            re.search(rf"{word}(?:_[a-z0-9]+){{0,8}}_{token}", text)
            for word in ["reduz", "diminui", "baixa", "enfraquece"]
        )
        buff_near_stat = any(
            re.search(rf"{word}(?:_[a-z0-9]+){{0,8}}_{token}", text)
            for word in ["aumenta", "ganha", "concede", "fortalece", "buffa"]
        )
        if stat == "matk" and has_any(["dano_magico", "ataque_magico"]) and has_any(["reduz_pela_metade", "todo_e_qualquer_dano", "reduz_50_de_todo"]):
            debuff_near_stat = False
        if debuff_near_stat and stat in {"atk", "matk", "def", "spd", "acc", "dodge"}:
            default_value = 20 if int(rarity or 1) < 5 else 30
            effect.setdefault(f"debuff_{stat}", default_value)
        elif buff_near_stat and stat in {"atk", "matk", "def", "spd", "crt", "acc", "dodge"}:
            default_value = 20 if int(rarity or 1) < 5 else 30
            effect.setdefault(f"buff_{stat}", default_value)

    status_percent = chance_percent() or 100
    if has_any(["atordoa", "stun", "paralisa"]):
        if "chance" in text:
            effect["chance_stun"] = min(status_percent / 100, 0.75)
        effect["stun_turnos"] = min(turns, 2)
    if has_any(["congela", "congelamento", "freeze"]):
        effect["freeze_turnos"] = min(turns, 2)
    if has_any(["queimadura", "incendeia", "burn"]):
        effect["dot"] = {"tipo": "fogo", "base": damage_base if damage_base in {"atk", "matk"} else "matk", "mult": 0.25, "turnos": turns}
    if has_any(["veneno", "envenena", "poison"]):
        effect["dot"] = {"tipo": "veneno", "base": damage_base if damage_base in {"atk", "matk"} else "matk", "mult": 0.25, "turnos": turns}
    if has_any(["sangramento", "sangrar", "bleed"]):
        effect["dot"] = {"tipo": "sangramento", "base": "atk", "mult": 0.25, "turnos": turns}
    if "fraqueza" in text:
        effect["aplica_fraqueza"] = cap(percent or 25, 40)
    if negative_heal:
        effect["anti_cura"] = True
    if has_any(["lentidao", "reduz_a_velocidade"]):
        if "imune" in text:
            effect["imune_lentidao"] = True
        else:
            effect.setdefault("debuff_spd", cap(percent or 25, 45))
    if "silencia" in text or "silence" in text:
        effect["silence_turnos"] = min(turns, 2)
    if "confusao" in text:
        effect["confusao"] = True
    if "medo" in text:
        effect["fear_turnos"] = min(turns, 2)
    if has_any(["limpa_debuff", "remove_efeitos", "remove_debuff", "remove_todos_os_debuffs", "remove_malignos"]):
        effect["remove_todos_debuffs"] = True
    if has_any(["efeitos_negativos", "imunidade_debuffs", "imunidade_absoluta_a_efeitos"]):
        effect["imunidade_debuffs"] = True
    if has_any(["critico_garantido", "acerto_critico_garantido", "acerto_critico_inevitavel"]):
        effect["critico_garantido"] = True
    if has_any(["chance_de_atacar", "atacar_duas_vezes", "ataque_duplo"]):
        effect["chance_ataque_duplo"] = min((chance_percent() or 25) / 100, 0.50)
    if has_any(["regeneracao", "regenera", "cura_por_turno"]):
        effect["cura_turnos"] = cap(percent or 10, 25)
    if "imune" in text or "imunidade" in text:
        if has_any(["stun", "atordoamento"]):
            effect["imune_stun"] = True
        if has_any(["confusao"]):
            effect["imune_confusao"] = True
        if has_any(["medo"]):
            effect["imune_medo"] = True
    if has_any(["invisivel", "esquiva"]):
        effect["buff_dodge"] = cap(percent or 40, 50)
    if has_any(["taunt", "aggro", "provocacao", "atrai_ataques", "atrai_provocacao"]):
        effect["aggro_max"] = True
    if has_any(["reduz_pela_metade", "metade_os_ferimentos", "todo_e_qualquer_dano", "reduz_50_de_todo"]):
        effect["reduz_dano_recebido"] = cap(percent or 50, 60)
    if "todos_os_status" in text:
        effect["buff_geral"] = cap(percent or 30, 40)
    if has_any(["dano_causado", "poder_de_ataques_fisicos", "ataques_fisicos_puros"]):
        effect["multiplicador_dano_atk"] = 1 + (cap(percent or 25, 50) / 100)
    if has_any(["turno_extra", "turno_magico_ou_fisico_extra"]):
        effect["turnos_extra"] = 1
    if has_any(["vampiro", "cura_sua_vida", "curam_lhe_a_vida"]):
        effect["lifesteal"] = 0.25
    if has_any(["curar_a_equipe", "cura_a_equipe", "curam_a_equipe", "criticos_magicos_curam"]) and "dano" in text:
        effect["lifesteal_global"] = min((percent or 25) / 100, 0.50)
    if has_any(["criticos_magicos_curam", "bonus_passivo_e_duradouro_em_todas_as_curas"]):
        effect["cura_turnos"] = cap(percent or 10, 25)
    if has_any(["copiar_os_bonus", "copia_os_bonus", "copiar_buffs"]):
        effect["buff_atk"] = cap(percent or 25, 40)
        effect["buff_matk"] = cap(percent or 25, 40)
    if has_any(["anula_automaticamente", "primeiro_ataque_magico"]):
        effect["ignora_dano_magico"] = True
    if has_any(["ignora", "romper", "rompe", "quebra", "quebrar", "quebram"]) and has_any(["defesa", "armadura"]):
        effect["ignora_def"] = cap(percent or 35, 60)
    if has_any(["ignora", "destroi", "destruir", "rompe", "quebra", "quebrar", "quebram"]) and "escudo" in text:
        effect["remove_escudos"] = True
    if "permanente" in text or "combate_inteiro" in text:
        effect["turnos"] = 99
    else:
        effect.setdefault("turnos", turns)

    if not effect:
        effect = {"multiplicador_atk": 1.2, "turnos": turns}
    return {"nome": name, "tipo": skill_type, "alvo": target, "efeito": effect, "catalog_generated": True}


def _register_catalog_skills():
    global HEROES
    try:
        from data.heroes import HEROES
    except Exception:
        HEROES = {}
        return

    existing_by_name = {}
    for existing_id, existing_data in SKILLS.items():
        existing_by_name.setdefault(_skill_key(existing_data.get("nome")), existing_id)

    for hero_id, hero in HEROES.items():
        if hero_id == "id-nome":
            continue
        catalog_skills = []
        if isinstance(hero.get("habilidade"), dict):
            catalog_skills.append(hero["habilidade"])
        catalog_skills.extend(
            skill for skill in (hero.get("evolucoes") or {}).values()
            if isinstance(skill, dict)
        )
        for skill_data in catalog_skills:
            skill_id = skill_data.get("id") or _skill_key(skill_data.get("nome"))
            if not skill_id or skill_id in SKILLS:
                continue
            existing_id = existing_by_name.get(_skill_key(skill_data.get("nome")))
            if existing_id:
                SKILLS[skill_id] = deepcopy(SKILLS[existing_id])
                SKILLS[skill_id]["nome"] = skill_data.get("nome", SKILLS[skill_id].get("nome"))
            else:
                SKILLS[skill_id] = _catalog_skill_definition(skill_data, hero.get("raridade", 1))


def _ensure_runtime_effect(skill):
    skill_type = str(skill.get("tipo", "dano")).lower()
    effect = skill.setdefault("efeito", {})

    # ==========================================
    # O MOTOR DE CORREÇÃO AUTOMÁTICA DA TUTORI-CHAN
    # ==========================================
    
    # 1. Ajuste de Dano Extra (Garante que tenha Dano Base para Somar)
    if "dano_atk_extra" in effect and "multiplicador_atk" not in effect:
        effect["multiplicador_atk"] = 1.0
    if "dano_matk_extra" in effect and "multiplicador_matk" not in effect:
        effect["multiplicador_matk"] = 1.0

    # 2. Ajuste de Insta-Kill (Protege Chefes)
    if skill_type == "insta_kill" or "chance_insta_kill" in effect or "executa_abaixo_percent" in effect:
        effect["restricao"] = "nao_afeta_boss"

    # 3. Ajuste de Alvos Ambíguos para a IA
    alvo = skill.get("alvo", "")
    alvo_mapping = {
        "aliado_escolhido": "aliado_menor_hp",
        "dps_aliados": "aliado_maior_atk",
        "dps_aliado": "aliado_maior_atk",
        "lider_aliado": "aliado_maior_atk",
        "dps_inimigo": "inimigo_maior_atk",
        "inimigos_maior_dano": "inimigo_maior_atk",
        "inimigo_maior_dano": "inimigo_maior_atk",
        "aliado_morto": "aliado_morto_aleatorio",
        "aliados_mortos": "aliados_mortos_aleatorios",
        "magos_aliados": "todos_aliados",
        "aleatorio": "inimigo_aleatorio",
        "item_contra_si": "self",
        "adaptativo": "todos_inimigos",
        "inimigos_travados": "inimigo_maior_atk",
        "unico_aliado": "aliado_menor_hp" # fallback generalista
    }
    if alvo in alvo_mapping:
        skill["alvo"] = alvo_mapping[alvo]

    # 4. Ajuste de DoTs e Regenerações (Se não vierem no formato dict)
    if "queimadura_turnos" in effect:
        effect["dot"] = {"tipo": "fogo", "base": "matk", "mult": 0.3, "turnos": effect.pop("queimadura_turnos")}
    if "veneno_turnos" in effect:
        effect["dot"] = {"tipo": "veneno", "base": "matk", "mult": 0.3, "turnos": effect.pop("veneno_turnos")}
    if "aplica_sangramento" in effect:
        turnos_bleed = effect.get("turnos", 3)
        effect["dot"] = {"tipo": "sangramento", "base": "atk", "mult": 0.3, "turnos": turnos_bleed}
        effect.pop("aplica_sangramento")
    if "regen_hp" in effect:
        effect["cura_turnos"] = effect.pop("regen_hp")
    if "cura_hp_max_ao_agir" in effect:
        effect["cura_turnos"] = effect.pop("cura_hp_max_ao_agir")

    # ==========================================

    if skill_type == "provocar":
        skill["tipo"] = "buff"
        skill["alvo"] = "self"
        effect.setdefault("aggro_max", True)
        skill_type = "buff"

    if "cura_matk" in effect:
        effect.setdefault("multiplicador_matk", effect.pop("cura_matk"))
    if "cura_hp_max" in effect:
        effect.setdefault("cura_percent_max", effect.pop("cura_hp_max"))
    if "buff_hp_max" in effect:
        effect.setdefault("buff_hp", effect.pop("buff_hp_max"))
    if "aggro_total" in effect:
        effect.setdefault("aggro_max", effect.pop("aggro_total"))
    if "imune_dano_fisico" in effect:
        effect.setdefault("ignora_dano_fisico", effect.pop("imune_dano_fisico"))
    if "imunidade_dano_fisico" in effect:
        effect.setdefault("ignora_dano_fisico", effect.pop("imunidade_dano_fisico"))
    if "dodge" in effect:
        effect.setdefault("buff_dodge", effect.pop("dodge"))
    if "buff_dodge_self" in effect:
        effect.setdefault("buff_dodge", effect.pop("buff_dodge_self"))
    if "reducao_dano_recebido" in effect:
        effect.setdefault("reduz_dano_recebido", effect.pop("reducao_dano_recebido"))
    if "contra_ataque_dodge" in effect:
        effect.setdefault("counter_atk_percent", effect.pop("contra_ataque_dodge"))
    if "remove_debuffs" in effect:
        effect.setdefault("remove_todos_debuffs", effect.pop("remove_debuffs"))

    numeric_caps = {
        "buff_atk": 55, "buff_matk": 55, "buff_def": 55, "buff_hp": 55,
        "debuff_atk": 55, "debuff_matk": 55, "debuff_def": 55,
        "buff_spd": 50, "buff_crt": 50, "buff_acc": 50, "buff_dodge": 50,
        "debuff_spd": 50, "debuff_acc": 50, "debuff_dodge": 50,
        "buff_geral": 40, "debuff_geral": 40,
        "cura_turnos": 30, "reduz_dano_recebido": 60, "reflete_dano": 80,
    }
    for key, cap_value in numeric_caps.items():
        if key not in effect or isinstance(effect[key], bool):
            continue
        try:
            effect[key] = max(0, min(float(effect[key]), cap_value))
        except (TypeError, ValueError):
            effect[key] = cap_value

    for chance_key in ("chance_stun", "chance_ataque_duplo"):
        if chance_key not in effect or isinstance(effect[chance_key], bool):
            continue
        try:
            chance_value = float(effect[chance_key])
            if chance_value > 1:
                chance_value /= 100
            effect[chance_key] = max(0, min(chance_value, 0.75))
        except (TypeError, ValueError):
            effect[chance_key] = 0.25

    ratio_caps = {"escudo_hp_max": 0.50, "cura_percent_max": 0.60, "hp_percent": 1.0, "lifesteal": 0.60, "lifesteal_global": 1.0}
    for key, cap_value in ratio_caps.items():
        if key not in effect or isinstance(effect[key], bool):
            continue
        try:
            ratio_value = float(effect[key])
            if ratio_value > 1:
                ratio_value /= 100
            effect[key] = max(0, min(ratio_value, cap_value))
        except (TypeError, ValueError):
            effect[key] = cap_value
        
    if effect.get("dano_massivo"):
        if not any(key in effect for key in {"multiplicador_atk", "multiplicador_matk", "dano_atk_extra", "dano_matk_extra", "dano_hp_atual", "dano_hp_max"}):
            effect.setdefault("multiplicador_atk", 2.2)
        effect.pop("dano_massivo", None)
    if effect.get("dano_massivo_hp_max"):
        effect.setdefault("multiplicador_atk", 1.5)
        effect.setdefault("dano_hp_max", 0.18)
        effect.pop("dano_massivo_hp_max", None)
    if effect.get("chance_insta_kill_hp_baixo"):
        effect.setdefault("executa_abaixo_percent", 30)
        effect.pop("chance_insta_kill_hp_baixo", None)
        
    if skill_type in {"dano", "insta_kill"}:
        target_name = str(skill.get("alvo", ""))
        target_quantity = int(skill.get("quantidade", 1) or 1)
        is_area = target_name in {"todos_inimigos", "campo", "inimigos_aleatorios"} or target_quantity > 1
        mult_cap = 2.15 if is_area else 2.65
        total_cap = 2.45 if is_area else 3.0
        for key in ("multiplicador_atk", "multiplicador_matk", "multiplicador_soma_atk_matk"):
            if key in effect:
                try:
                    effect[key] = min(float(effect[key]), mult_cap)
                except (TypeError, ValueError):
                    effect[key] = 1.0
        if "multiplicador_hit" in effect:
            try:
                effect["multiplicador_hit"] = min(float(effect["multiplicador_hit"]), 3.0 if is_area else 4.0)
            except (TypeError, ValueError):
                effect["multiplicador_hit"] = 1.0
        strongest_mult = max(
            float(effect.get("multiplicador_atk", 1) or 1),
            float(effect.get("multiplicador_matk", 1) or 1),
            float(effect.get("multiplicador_soma_atk_matk", 1) or 1),
        )
        hit_mult = float(effect.get("multiplicador_hit", 1) or 1)
        total_mult = strongest_mult * hit_mult
        if total_mult > total_cap:
            scale = total_cap / total_mult
            if hit_mult > 1:
                effect["multiplicador_hit"] = max(1.0, round(hit_mult * scale, 2))
            else:
                for key in ("multiplicador_atk", "multiplicador_matk", "multiplicador_soma_atk_matk"):
                    if key in effect:
                        effect[key] = max(0.75, round(float(effect[key]) * scale, 2))
        for key, cap in {"dano_hp_atual": 0.18, "dano_hp_max": 0.12}.items():
            if key in effect:
                try:
                    effect[key] = min(float(effect[key]), cap)
                except (TypeError, ValueError):
                    effect[key] = cap

    supported_buff_keys = {
        "buff_atk", "buff_matk", "buff_def", "buff_spd", "buff_crt",
        "buff_acc", "buff_dodge", "buff_geral", "buff_hp",
        "buff_hp_temporario", "multiplicador_dano_atk", "multiplica_atk_matk",
        "multiplica_spd", "cura_turnos", "reduz_dano_recebido",
        "buff_atk_por_inimigo_vivo", "imortalidade_turnos",
        "imunidade_dano_turnos", "ignora_dano_fisico", "ignora_dano_magico",
        "escudo_hp_max", "aggro_max", "imune_stun", "imune_toxinas",
        "imune_maldicoes_dot_terreno", "imunidade_debuffs",
        "ataques_fogo", "chance_insta_kill_on_hit", "ignora_def_on_hit",
        "revive_hp", "heal_damage_received", "protege_aliados_fatal",
        "efeito_aleatorio_divino", "reflete_dano", "lifesteal_on_hit",
        "counter_atk_percent", "barreira_dano_recebido", "stun_atacante_on_hit",
        "criticos_removem_buff", "aplica_veneno_on_hit", "reduz_cooldown",
        "silence_todos_inimigos", "stun_curador_inimigo",
        "chance_ataque_duplo", "parar_tempo", "anular_habilidade_contra_si",
        "stun_todos_inimigos", "turnos_extra", "absorver_dano_refletir",
        "absorve_proxima_habilidade_reflete_dobro", "clona_dps_atributos",
        "clona_dps_perfeito", "clona_self", "imune_a_dano",
        "morre_se_dps_morrer", "absorve_atk_converte_cura", "adaptativo",
        "cura_50_se_low_hp", "execute_se_inimigo_abaixo_20",
        "buff_atk_def_30_se_inimigo_full", "buff_atk_contra_agressor",
        "marca_dps_redireciona_dano_self", "transfere_atk_para_dps",
        "insta_kill_on_hit_garantido", "morre_apos_turnos",
        "melhora_item_usado", "cor_leonis_providencia",
        "reduz_dano_recebido_time", "contrato_morte_dps",
        "insta_kill_inimigo_aleatorio", "invocar", "dot", "lifesteal_global",
        "ignora_def", "ignora_def_escudos", "remove_escudos",
    }
    supported_debuff_keys = {
        "debuff_atk", "debuff_matk", "debuff_def", "debuff_spd",
        "debuff_acc", "debuff_dodge",
        "debuff_geral", "stun_turnos", "chance_stun", "freeze_turnos",
        "root_turnos", "silence_turnos", "fear_turnos", "medo_turnos",
        "confusao", "aplica_fraqueza", "dano_recebido_extra",
        "fraqueza", "lentidao", "anti_cura", "corta_cura", "dot",
        "veneno_turnos", "queimadura_turnos", "aplica_sangramento",
        "remove_todos_buffs", "bloqueia_buffs", "remove_escudos",
        "destroi_escudos", "quebra_escudos", "ignora_escudos",
    }

    if skill_type in {"buff", "passiva", "especial", "invocacao", "escudo"}:
        has_supported = any(key in effect for key in supported_buff_keys | supported_debuff_keys)
        has_supported = has_supported or any(str(key).startswith("imune_") for key in effect)
        if not has_supported:
            effect["buff_geral"] = 10
            effect.setdefault("turnos", 3)
    elif skill_type == "debuff":
        has_supported = any(key in effect for key in supported_debuff_keys)
        has_supported = has_supported or any(str(key).startswith("imune_") for key in effect)
        if not has_supported:
            effect["debuff_geral"] = 10
            effect.setdefault("turnos", 3)
    elif skill_type == "cura":
        if not any(key in effect for key in {"cura_fixa", "cura_percent_max", "multiplicador_matk"}):
            effect["cura_percent_max"] = 0.20
    elif skill_type == "reviver":
        effect.setdefault("hp_percent", 0.50)


def validate_catalog_skills():
    missing = []
    inert = []
    for hero_id, hero in HEROES.items():
        if hero_id == "id-nome":
            continue
        skills = [hero.get("habilidade")]
        skills.extend((hero.get("evolucoes") or {}).values())
        for skill_data in skills:
            if not isinstance(skill_data, dict):
                continue
            skill_id = skill_data.get("id")
            if not skill_id or skill_id not in SKILLS:
                missing.append((hero_id, skill_data.get("nome", "Habilidade")))
                continue
            if not SKILLS[skill_id].get("efeito"):
                inert.append((hero_id, skill_data.get("nome", "Habilidade")))
    return {"missing": missing, "inert": inert}


_register_catalog_skills()
for _skill in SKILLS.values():
    _ensure_runtime_effect(_skill)

CATALOG_SKILL_AUDIT = validate_catalog_skills()
if CATALOG_SKILL_AUDIT["missing"] or CATALOG_SKILL_AUDIT["inert"]:
    raise RuntimeError(
        "Falha na auditoria de habilidades do catalogo: "
        f"{CATALOG_SKILL_AUDIT}"
    )
