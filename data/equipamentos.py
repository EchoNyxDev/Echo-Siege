# ==========================================
# DICIONÁRIO DE EQUIPAMENTOS
# ==========================================
# Tipos: "atk" (Armas), "def" (Armaduras) ou "livre" (Acessórios/Relíquias)

EQUIPAMENTOS = {
    # --- ATAQUE (ARMAS) ---
    "espada_de_ferro": {"nome": "Espada de Ferro", "tipo": "atk", "atk": 10, "matk": 0, "def": 0, "emoji": "🗡️"},
    "cajado_arcano": {"nome": "Cajado Arcano", "tipo": "atk", "atk": 0, "matk": 10, "def": 0, "emoji": "🦯"},
    "lamina_encantada": {"nome": "Lâmina Encantada", "tipo": "atk", "atk": 30, "matk": 0, "def": 0, "emoji": "⚔️"},
    "tomo_dos_sabios": {"nome": "Tomo dos Sábios", "tipo": "atk", "atk": 0, "matk": 30, "def": 0, "emoji": "📘"},
    "espada_imperial": {"nome": "Espada Imperial", "tipo": "atk", "atk": 75, "matk": 0, "def": 0, "emoji": "👑"},
    "coroa_arcana": {"nome": "Coroa Arcana", "tipo": "atk", "atk": 0, "matk": 75, "def": 0, "emoji": "💠"},
    "lamina_eterna": {"nome": "Lâmina Eterna", "tipo": "atk", "atk": 120, "matk": 40, "def": 20, "emoji": "🗡️"}, # Drop de Invasão/Aventura
    "espada_dimensional": {"nome": "Espada Dimensional", "tipo": "atk", "atk": 150, "matk": 150, "def": 0, "emoji": "🌌"}, # Craftável na Forja

    # --- DEFESA (ARMADURAS) ---
    "armadura_de_couro": {"nome": "Armadura de Couro", "tipo": "def", "atk": 0, "matk": 0, "def": 15, "emoji": "🦺"},
    "escudo_do_guardiao": {"nome": "Escudo do Guardião", "tipo": "def", "atk": 0, "matk": 0, "def": 30, "emoji": "🛡️"},
    "armadura_real": {"nome": "Armadura Real", "tipo": "def", "atk": 0, "matk": 0, "def": 75, "emoji": "🛡️"},
    "armadura_magma": {"nome": "Armadura de Magma", "tipo": "def", "atk": 30, "matk": 0, "def": 150, "emoji": "🌋"}, # Craftável na Forja

    # --- LIVRE (ACESSÓRIOS E RELÍQUIAS DAS AVENTURAS) ---
    "anel_vitalidade_sombria": {"nome": "Anel da Vitalidade Sombria", "tipo": "livre", "hp": 300, "atk": 0, "def": 10, "emoji": "💍"},
    "amuleto_da_serenidade": {"nome": "Amuleto da Serenidade", "tipo": "livre", "matk": 30, "def": 30, "hp": 100, "emoji": "📿"},
    "medalha_da_guarda": {"nome": "Medalha da Guarda", "tipo": "livre", "def": 40, "hp": 200, "emoji": "🎖️"},
    "bussola_espectral": {"nome": "Bússola Espectral", "tipo": "livre", "spd": 40, "atk": 20, "emoji": "🧭"},
    "amuleto_lobo": {"nome": "Amuleto do Lobo Guardião", "tipo": "livre", "atk": 40, "spd": 25, "emoji": "🐺"},
    "lanterna_vigia": {"nome": "Lanterna do Vigia Eterno", "tipo": "livre", "matk": 50, "def": 25, "emoji": "🏮"},
    "grimorio_aprendiz": {"nome": "Grimório do Aprendiz", "tipo": "livre", "matk": 60, "spd": 10, "emoji": "📖"},
    "relicario_olho": {"nome": "Relicário do Olho Escarlate", "tipo": "livre", "matk": 100, "hp": -150, "emoji": "👁️"}, # Muito poder, tira vida
    "mascara_corvo": {"nome": "Máscara do Corvo Negro", "tipo": "livre", "crt": 20, "spd": 35, "emoji": "🎭"},
    "coroa_julgamento": {"nome": "Coroa do Julgamento", "tipo": "livre", "matk": 120, "def": 50, "emoji": "👑"}
}