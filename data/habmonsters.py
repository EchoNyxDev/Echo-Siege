# ==========================================
# DICIONÁRIO MESTRE DE HABILIDADES INIMIGAS
# ==========================================
# Este arquivo dita a inteligência artificial e os poderes dos monstros, bosses e calamidades.
# Como os inimigos lutam contra os heróis, os alvos "inimigos" para eles são os seus heróis.

MONSTER_SKILLS = {
    
    # ==========================================
    # DUNGEON 1 E 2: Goblins, Lobos e Mortos-Vivos
    # ==========================================
    "invocar_goblins": {"nome": "Chamado da Horda", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 30, "buff_spd": 20, "turnos": 3}},
    "dano_area_3_turnos": {"nome": "Maldição Espalhada", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.2, "dot": {"tipo": "maldicao", "dano_matk": 20, "turnos": 3}}},
    "prender_oponente": {"nome": "Prisão Tumular", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"stun_turnos": 2, "debuff_def": 30}},
    "imune_atk_fisico": {"nome": "Corpo Etéreo", "tipo": "passiva", "alvo": "self", "efeito": {"ignora_dano_fisico": True, "turnos": -1}},
    "necromancia_lentidao": {"nome": "Toque do Necromante", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_spd": 40, "chance_stun": 0.20, "turnos": 2}},

    # ==========================================
    # DUNGEON 3 E 4: Gelo e Demônios
    # ==========================================
    "congelar_dois_inimigos": {"nome": "Vento Glacial", "tipo": "debuff", "alvo": "inimigos_aleatorios", "quantidade": 2, "efeito": {"stun_turnos": 1, "debuff_spd": 20}},
    "stun_e_lentidao": {"nome": "Impacto Sísmico", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 1.5, "chance_stun": 1.0, "stun_turnos": 1, "debuff_spd": 30}},
    "reduz_defesa_geral": {"nome": "Aura de Quebra", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_def": 40, "turnos": 3}},
    "era_glacial": {"nome": "Era Glacial", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.5, "debuff_spd": 60, "stun_turnos": 1}},
    "tornado_de_fogo": {"nome": "Tornado de Fogo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "dot": {"tipo": "queimadura", "dano_matk": 50, "turnos": 2}}},
    "contrato_berserk": {"nome": "Contrato Berserk", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 50, "buff_spd": 30, "debuff_def": 20, "turnos": 3}},
    "sacrificio_de_sangue": {"nome": "Sacrifício de Sangue", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_matk": 2.0, "lifesteal": 1.0}},
    "ignorar_defesa_explosao": {"nome": "Explosão do Abismo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.0, "ignora_def": True}},
    "bloqueio_de_habilidade": {"nome": "Selo Demoníaco", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"silence_turnos": 2, "debuff_atk": 20}},

    # ==========================================
    # DUNGEON 5: Ecos do Abismo
    # ==========================================
    "ignorar_matk": {"nome": "Imunidade Arcana", "tipo": "passiva", "alvo": "self", "efeito": {"imune_magico": True, "turnos": -1}},
    "anular_atk": {"nome": "Presença Intimidadora", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"debuff_atk": 50, "debuff_matk": 50, "turnos": 2}},
    "desintegracao": {"nome": "Desintegração", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 3.0, "anti_cura": True, "turnos": 2}},
    "paralisia_em_massa": {"nome": "Paralisia em Massa", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"stun_turnos": 2, "debuff_spd": 50}},
    "aetherion": {"nome": "Aetherion", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 4.0, "ignora_imunidade_cc": True, "chance_stun": 0.50}},

    # ==========================================
    # INVASÕES SEMANAIS (RAID BOSSES)
    # ==========================================
    "magia_em_massa": {"nome": "Magia em Massa", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.8}},
    "furia_cega": {"nome": "Fúria Cega", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 70, "buff_spd": 30, "turnos": 3}},
    "uivo_de_guerra": {"nome": "Uivo de Guerra", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 40, "buff_spd": 40, "buff_crt": 20, "turnos": 3}},
    "invocar_horda_goblin": {"nome": "O Rei Ordena!", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.0, "chance_stun": 0.30}},
    "investida_mortal": {"nome": "Investida Mortal", "tipo": "dano", "alvo": "unico_inimigo", "efeito": {"multiplicador_atk": 3.5, "chance_insta_kill": 0.05, "ignora_def": True}},
    "dano_area_constante": {"nome": "Aura de Decadência", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.0, "dot": {"tipo": "trevas", "dano_matk": 100, "turnos": 3}}},
    "prisao_das_almas": {"nome": "Prisão das Almas", "tipo": "debuff", "alvo": "dps_aliado", "efeito": {"stun_turnos": 3, "debuff_atk": 50}},
    "congelar_defensores": {"nome": "Nevasca Congelante", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "stun_turnos": 1, "debuff_spd": 30}},
    "terremoto_glacial": {"nome": "Terremoto Glacial", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.5, "debuff_spd": 40, "debuff_def": 30}},
    "esmagar_muralha": {"nome": "Esmagar Defesas", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_atk": 2.0, "ignora_def": 50}},
    "triplo_tornado_fogo": {"nome": "Triplo Tornado de Fogo", "tipo": "dano", "alvo": "todos_inimigos", "quantidade": 3, "efeito": {"multiplicador_matk": 1.2, "dot": {"tipo": "queimadura", "dano_matk": 150, "turnos": 2}}},
    "contrato_infernal": {"nome": "Contrato Infernal", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 100, "buff_matk": 100, "lifesteal": 0.50, "turnos": 3}},
    "chuva_de_sangue": {"nome": "Chuva de Sangue", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.0, "lifesteal_global": 0.50}},
    "imunidade_magica": {"nome": "Espelho Mágico", "tipo": "passiva", "alvo": "self", "efeito": {"ignora_dano_magico": True}},
    "silenciar_defensores": {"nome": "Silêncio Real", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"silence_turnos": 2, "debuff_atk": 30}},
    "paralisia_global": {"nome": "Paralisia Global", "tipo": "debuff", "alvo": "todos_inimigos", "efeito": {"stun_turnos": 2, "debuff_spd": 60}},

    # ==========================================
    # CALAMIDADES MENSAIS (CHEFES SUPREMOS)
    # ==========================================
    "sopro_do_caos": {"nome": "Sopro do Caos", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_soma_atk_matk": 1.5, "debuff_geral": 20}},
    "tempestade_carmesim": {"nome": "Tempestade Carmesim", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.5, "dot": {"tipo": "sangramento", "dano_matk": 200, "turnos": 3}}},
    "fim_dos_tempos": {"nome": "O Fim dos Tempos", "tipo": "especial", "alvo": "todos_inimigos", "efeito": {"dano_hp_atual": 0.80, "stun_turnos": 1}},
    
    "olhar_petrificante": {"nome": "Olhar Petrificante", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"stun_turnos": 3, "debuff_def": 50}},
    "veneno_ancestral": {"nome": "Veneno Ancestral", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 1.5, "dot": {"tipo": "veneno", "dano_matk": 300, "turnos": 4}, "corta_cura": 50}},
    "pele_de_pedra": {"nome": "Pele de Pedra", "tipo": "passiva", "alvo": "self", "efeito": {"reduz_dano_recebido": 50, "ignora_criticos": True}},
    
    "pesadelo_vivo": {"nome": "Pesadelo Vivo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.0, "chance_medo": 0.50}},
    "sono_eterno": {"nome": "Sono Eterno", "tipo": "debuff", "alvo": "unico_inimigo", "efeito": {"stun_turnos": 4}},
    "devorador_de_sonhos": {"nome": "Devorador de Sonhos", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.5, "cura_percent_max": 0.15}},
    
    "tempestade_de_gelo": {"nome": "Tempestade de Gelo", "tipo": "dano", "alvo": "todos_inimigos", "efeito": {"multiplicador_matk": 2.0, "chance_freeze": 0.30}},
    "coracao_congelado": {"nome": "Coração Congelado", "tipo": "passiva", "alvo": "self", "efeito": {"imune_cc": True, "reflect_matk": 0.50}},
    
    "necromancia_suprema": {"nome": "Necromancia Suprema", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 50, "buff_matk": 50, "buff_spd": 50, "turnos": 4}},
    "toque_da_morte": {"nome": "Toque da Morte", "tipo": "insta_kill", "alvo": "unico_inimigo", "efeito": {"chance_insta_kill_hp_baixo": 0.50}},
    "imunidade_fisica": {"nome": "Imunidade Física", "tipo": "passiva", "alvo": "self", "efeito": {"ignora_dano_fisico": True}},
    
    "mil_espadas": {"nome": "Mil Espadas", "tipo": "dano", "alvo": "todos_inimigos", "quantidade": 5, "efeito": {"multiplicador_atk": 0.8, "ignora_def": 30}},
    "forma_demoniaca": {"nome": "Forma Demoníaca", "tipo": "buff", "alvo": "self", "efeito": {"buff_atk": 100, "buff_spd": 100, "turnos": 3}},
    
    "conhecimento_absoluto": {"nome": "Conhecimento Absoluto", "tipo": "passiva", "alvo": "self", "efeito": {"ignora_dodge_camuflagem_defesa": True, "buff_acc": 100}},
    "tomo_da_verdade": {"nome": "Tomo da Verdade", "tipo": "especial", "alvo": "todos_inimigos", "efeito": {"remove_todos_buffs": True, "silence_turnos": 2, "debuff_matk": 50}}
}