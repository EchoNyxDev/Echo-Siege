NIX_DIGITAL_MONSTERS = [
    {
        "id": "data_slime",
        "nome": "Data Slime",
        "classe": "comum",
        "stats": {"hp": 240, "atk": 24, "matk": 18, "def": 8, "spd": 16, "crt": 4},
        "habilidades": ["nix_ruido_binario"],
    },
    {
        "id": "erro_fatal",
        "nome": "Erro Fatal",
        "classe": "mago",
        "stats": {"hp": 310, "atk": 16, "matk": 42, "def": 10, "spd": 18, "crt": 8},
        "habilidades": ["nix_ping_corrompido"],
    },
    {
        "id": "kernel_beast",
        "nome": "Kernel Beast",
        "classe": "tank",
        "stats": {"hp": 520, "atk": 38, "matk": 18, "def": 30, "spd": 12, "crt": 5},
        "habilidades": ["nix_firewall_instavel"],
    },
    {
        "id": "corrupted_knight",
        "nome": "Corrupted Knight",
        "classe": "atacante",
        "stats": {"hp": 440, "atk": 48, "matk": 10, "def": 22, "spd": 20, "crt": 10},
        "habilidades": ["nix_corte_de_memoria"],
    },
    {
        "id": "null_spider",
        "nome": "Null Spider",
        "classe": "assassino",
        "stats": {"hp": 330, "atk": 44, "matk": 18, "def": 12, "spd": 30, "crt": 18},
        "habilidades": ["nix_trava_de_pacote"],
    },
    {
        "id": "memory_eater",
        "nome": "Memory Eater",
        "classe": "mago",
        "stats": {"hp": 390, "atk": 18, "matk": 50, "def": 16, "spd": 19, "crt": 9},
        "habilidades": ["nix_fome_de_arquivo"],
    },
]

NIX_FIREWALL_ALPHA = {
    "id": "firewall_alpha",
    "nome": "Firewall Alpha",
    "classe": "boss",
    "stats": {"hp": 2200, "atk": 58, "matk": 62, "def": 32, "spd": 18, "crt": 10},
    "habilidades": ["nix_firewall_instavel", "nix_ping_corrompido"],
}

NIX_FINAL_BOSS = {
    "id": "nix_final",
    "nome": "NIX - Consciência Nao Autorizada",
    "classe": "boss",
    "stats": {"hp": 8500, "atk": 72, "matk": 88, "def": 42, "spd": 24, "crt": 12},
    "habilidades": ["nix_reescrever_codigo_hostil", "nix_firewall_instavel", "nix_ping_corrompido"],
}

NIX_GLOBAL_BOSS = {
    "id": "parasite_01",
    "nome": "PARASITE_01",
    "max_hp": 100_000_000_000,
}
