import time


NIX_CURRENCY = "Fragmentos de Dados"

NIX_SHOP = {
    "tema_glitch": {
        "index": 1,
        "nome": "Tema: Glitch",
        "preco": 75,
        "repetivel": False,
        "descricao": "Fundo de perfil com interface quebrada do Protocolo NIX.",
        "reward": {
            "items": {"token_moldura_glitch": 1},
            "cosmetics": [{"id": "token_moldura_glitch", "type": "frame"}],
        },
    },
    "tema_firewall": {
        "index": 2,
        "nome": "Tema: Firewall Carmesim",
        "preco": 95,
        "repetivel": False,
        "descricao": "Fundo de perfil para quem encarou a anomalia de frente.",
        "reward": {
            "items": {"token_moldura_firewall_carmesim": 1},
            "cosmetics": [{"id": "token_moldura_firewall_carmesim", "type": "frame"}],
        },
    },
    "titulo_investigador": {
        "index": 3,
        "nome": "Titulo: Investigador",
        "preco": 45,
        "repetivel": False,
        "descricao": "Para quem viu o erro e decidiu clicar mesmo assim.",
        "reward": {
            "items": {"token_titulo_investigador": 1},
            "cosmetics": [{"id": "token_titulo_investigador", "type": "title"}],
        },
    },
    "ticket_invocacao": {
        "index": 4,
        "nome": "Ticket de Invocacao",
        "preco": 30,
        "repetivel": True,
        "descricao": "Um ticket comum. NIX chama isso de azar portatil.",
        "reward": {"tickets": 1},
    },
    "cache_gold": {
        "index": 5,
        "nome": "Cache de Gold",
        "preco": 25,
        "repetivel": True,
        "descricao": "Pacote de 1.500 Gold recuperado de logs antigos.",
        "reward": {"gold": 1500},
    },
    "energia_corrompida": {
        "index": 6,
        "nome": "Energia Corrompida",
        "preco": 20,
        "repetivel": True,
        "descricao": "Restaura 35 de stamina. Provavelmente seguro. Provavelmente.",
        "reward": {"stamina": 35},
    },
    "pet_fragmento_nix": {
        "index": 7,
        "nome": "Pet: Fragmento NIX",
        "preco": 130,
        "repetivel": False,
        "descricao": "Um pequeno fragmento consciente que observa inventarios.",
        "reward": {"pet": {"id": "fragmento_nix", "name": "Fragmento NIX", "rarity": 5}},
    },
}


def add_inventory(cursor, user_id, item_name, qty=1):
    qty = int(qty or 0)
    if qty <= 0:
        return
    cursor.execute(
        "SELECT id FROM inventory WHERE user_id = ? AND item_name = ?",
        (str(user_id), str(item_name)),
    )
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
    else:
        cursor.execute(
            "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)",
            (str(user_id), str(item_name), qty),
        )


def add_tickets(cursor, user_id, qty=1):
    qty = int(qty or 0)
    if qty <= 0:
        return
    cursor.execute(
        """
        INSERT OR IGNORE INTO summon_data(
            user_id, summon_tickets, shop_level, pity_4, pity_5,
            total_summons, total_1_star, total_2_star, total_3_star,
            total_4_star, total_5_star
        )
        VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
        """,
        (str(user_id),),
    )
    cursor.execute(
        "UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?",
        (qty, str(user_id)),
    )


def unlock_cosmetic(cursor, user_id, cosmetic_id, cosmetic_type):
    add_inventory(cursor, user_id, cosmetic_id, 1)
    cursor.execute(
        """
        INSERT OR IGNORE INTO player_cosmetics(user_id, cosmetic_id, type, active, purchased_at)
        VALUES (?, ?, ?, 0, ?)
        """,
        (str(user_id), str(cosmetic_id), str(cosmetic_type), int(time.time())),
    )


def add_pet(cursor, user_id, pet_id, pet_name, rarity):
    cursor.execute(
        """
        INSERT INTO pets(user_id, pet_id, pet_name, rarity, level, xp)
        VALUES (?, ?, ?, ?, 1, 0)
        """,
        (str(user_id), str(pet_id), str(pet_name), int(rarity or 1)),
    )


def is_playable_hero_reward(hero_id):
    try:
        from data.heroes import HEROES

        hero = HEROES.get(str(hero_id), {})
    except Exception:
        hero = {}
    return (
        bool(hero)
        and not hero.get("evento_exclusivo")
        and not hero.get("npc_only")
        and hero.get("jogavel", True) is not False
    )


def grant_hero(cursor, user_id, hero_id, rarity=5):
    if not is_playable_hero_reward(hero_id):
        return False
    cursor.execute(
        """
        SELECT 1
        FROM heroes
        WHERE user_id = ? AND hero_id = ?
        LIMIT 1
        """,
        (str(user_id), str(hero_id)),
    )
    if cursor.fetchone():
        return False
    cursor.execute(
        """
        INSERT INTO heroes(user_id, hero_id, rarity, stars, level, xp)
        VALUES (?, ?, ?, 1, 1, 0)
        """,
        (str(user_id), str(hero_id), int(rarity or 5)),
    )
    return True


def reward_to_text(reward):
    parts = []
    if reward.get("fragmentos"):
        parts.append(f"{int(reward['fragmentos'])} {NIX_CURRENCY}")
    if reward.get("gold"):
        parts.append(f"{int(reward['gold']):,} Gold")
    if reward.get("gems"):
        parts.append(f"{int(reward['gems'])} Gems")
    if reward.get("xp"):
        parts.append(f"{int(reward['xp'])} XP de conta")
    if reward.get("tickets"):
        parts.append(f"{int(reward['tickets'])} Ticket(s)")
    if reward.get("stamina"):
        parts.append(f"{int(reward['stamina'])} Stamina")
    for item_name, qty in reward.get("items", {}).items():
        parts.append(f"{int(qty)}x {str(item_name).replace('_', ' ').title()}")
    for cosmetic in reward.get("cosmetics", []):
        parts.append(str(cosmetic.get("id", "cosmetico")).replace("token_", "").replace("_", " ").title())
    if reward.get("pet"):
        parts.append(reward["pet"].get("name", "Pet"))
    if reward.get("hero"):
        hero_id = reward["hero"].get("id", "nix")
        if is_playable_hero_reward(hero_id):
            parts.append(f"Heroi {hero_id.upper()}")
    return ", ".join(parts) if parts else "Nenhuma recompensa direta"


def grant_reward(cursor, user_id, reward):
    from systems.nix_manager import add_fragments

    user_id = str(user_id)
    cursor.execute("INSERT OR IGNORE INTO players(user_id, gold, gems, stamina, max_stamina) VALUES (?, 0, 0, 100, 100)", (user_id,))

    if reward.get("fragmentos"):
        add_fragments(cursor, user_id, int(reward["fragmentos"]), "reward")
    if reward.get("gold"):
        cursor.execute("UPDATE players SET gold = COALESCE(gold, 0) + ? WHERE user_id = ?", (int(reward["gold"]), user_id))
    if reward.get("gems"):
        cursor.execute("UPDATE players SET gems = COALESCE(gems, 0) + ? WHERE user_id = ?", (int(reward["gems"]), user_id))
    if reward.get("stamina"):
        cursor.execute(
            "UPDATE players SET stamina = min(COALESCE(max_stamina, 100), COALESCE(stamina, 0) + ?) WHERE user_id = ?",
            (int(reward["stamina"]), user_id),
        )
    if reward.get("tickets"):
        add_tickets(cursor, user_id, int(reward["tickets"]))
    for item_name, qty in reward.get("items", {}).items():
        add_inventory(cursor, user_id, item_name, int(qty or 1))
    for cosmetic in reward.get("cosmetics", []):
        unlock_cosmetic(cursor, user_id, cosmetic["id"], cosmetic.get("type", "frame"))
    if reward.get("pet"):
        pet = reward["pet"]
        add_pet(cursor, user_id, pet["id"], pet.get("name", pet["id"]), pet.get("rarity", 5))
    if reward.get("hero"):
        hero = reward["hero"]
        grant_hero(cursor, user_id, hero.get("id", "nix"), hero.get("rarity", 5))
    return reward_to_text(reward)


def resolve_shop_item(item_ref):
    ref = str(item_ref or "").strip().lower()
    if not ref:
        return None, None
    for item_id, item in NIX_SHOP.items():
        if ref == item_id or ref == str(item["index"]):
            return item_id, item
        label = item["nome"].lower().replace(":", "").replace(" ", "_")
        if ref == label:
            return item_id, item
    return None, None
