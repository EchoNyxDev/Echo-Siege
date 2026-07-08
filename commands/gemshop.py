import random
import sqlite3
import time
import unicodedata
import discord
from discord.ext import commands
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
except Exception:
    HEROES = {}

try:
    from data.pets import PETS
except Exception:
    PETS = {}

GEM_ITEMS = {
    1: {"name": "Modo Automático da Arena", "price": 350, "kind": "perk", "perk": "arena_auto", "max_level": 1, "desc": "Desbloqueia automação para arena. O bot joga, você assume a culpa."},
    2: {"name": "Bônus Permanente de XP", "price": 180, "kind": "perk", "perk": "xp_bonus", "max_level": 5, "desc": "+5% XP permanente por nível."},
    3: {"name": "Bônus Permanente de Ouro", "price": 180, "kind": "perk", "perk": "gold_bonus", "max_level": 5, "desc": "+5% Gold permanente por nível."},
    4: {"name": "Ticket de Herói Raro", "price": 140, "kind": "item", "item": "ticket_heroi_raro", "qty": 1, "desc": "Sorteia um herói 4⭐ ou 5⭐."},
    5: {"name": "Ticket de Pet", "price": 90, "kind": "item", "item": "ticket_pet", "qty": 1, "desc": "Vai para a mochila e pode ser usado com `echo consumir ticket_pet`."},
    6: {"name": "Ticket de Escolha de Herói", "price": 900, "kind": "item", "item": "ticket_escolha_heroi", "qty": 1, "desc": "Permite escolher qualquer herói pelo ID do catálogo."},
    7: {"name": "Tema: Cidade Noturna", "price": 180, "kind": "cosmetic", "type": "frame", "item": "token_moldura_cidade_noturna", "desc": "Substitui o fundo do perfil por uma cidade iluminada à noite."},
    8: {"name": "Tema: Minecraft", "price": 220, "kind": "cosmetic", "type": "frame", "item": "token_moldura_minecraft", "desc": "Substitui o fundo do perfil por um cenário em blocos."},
    9: {"name": "Tema: Árvore Glacial", "price": 260, "kind": "cosmetic", "type": "frame", "item": "token_moldura_arvore_glacial", "desc": "Substitui o fundo do perfil por uma árvore congelada."},
    10: {"name": "Tema: Flores de Cerejeira", "price": 260, "kind": "cosmetic", "type": "frame", "item": "token_moldura_flores_cerejeira", "desc": "Substitui o fundo do perfil por flores de cerejeira."},
    11: {"name": "Título: Pontual Demais", "price": 160, "kind": "cosmetic", "type": "title", "item": "token_titulo_pontual_demais", "desc": "Título permanente para quem respeita o daily como religião."},
    12: {"name": "Título: Bug Ambulante", "price": 180, "kind": "cosmetic", "type": "title", "item": "token_titulo_bug_ambulante", "desc": "Para quem erra comandos com consistência artística."},
    13: {"name": "Título: TutoriUAU Aprovou", "price": 250, "kind": "cosmetic", "type": "title", "item": "token_titulo_tutoriuau_aprovou", "desc": "Aprovou, mas colocou observações no rodapé."},
    14: {"name": "Título: Patrocinador", "price": 300, "kind": "cosmetic", "type": "title", "item": "token_titulo_patrocinador", "desc": "O banco da guilda conhece seu nome."},
}

COSMETIC_LABELS = {
    "token_moldura_cidade_noturna": "Tema Cidade Noturna",
    "token_moldura_minecraft": "Tema Minecraft",
    "token_moldura_arvore_glacial": "Tema Árvore Glacial",
    "token_moldura_flores_cerejeira": "Tema Flores de Cerejeira",
    "token_moldura_arquibancada_lotada": "Tema Arquibancada Lotada",
    "token_moldura_gramado_noturno": "Tema Gramado Noturno",
    "token_moldura_sala_de_imprensa": "Tema Sala de Imprensa",
    "token_moldura_taca_mundial": "Tema Taça Mundial",
    "token_titulo_pontual": "Pontual",
    "token_titulo_pontual_demais": "Pontual Demais",
    "token_titulo_bug_ambulante": "Bug Ambulante",
    "token_titulo_tutoriuau_aprovou": "TutoriUAU Aprovou",
    "token_titulo_patrocinador": "Patrocinador",
    "token_titulo_clicador": "Clicador Profissional",
    "token_titulo_campeao_de_lugnica": "Campeão de Wolford",
    "token_titulo_lenda_echo_cup": "Lenda da Echo Cup",
    "token_titulo_rei_dos_ecos": "Rei dos Ecos",
    "token_titulo_maior_tecnico_de_lugnica": "Maior Técnico de Wolford",
    "token_titulo_campeao_do_mundo": "Campeão do Mundo",
}

LEGACY_FRAME_MIGRATIONS = {
    "token_moldura_presenca": "token_moldura_cidade_noturna",
    "token_moldura_labirinto": "token_moldura_minecraft",
    "token_moldura_torre": "token_moldura_arvore_glacial",
    "token_moldura_bolsa_cheia": "token_moldura_flores_cerejeira",
}

def migrate_legacy_frames(cursor):
    for old_id, new_id in LEGACY_FRAME_MIGRATIONS.items():
        cursor.execute("SELECT user_id, COALESCE(SUM(quantity), 0) FROM inventory WHERE item_name = ? GROUP BY user_id", (old_id,))
        for user_id, quantity in cursor.fetchall():
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ? ORDER BY id LIMIT 1", (user_id, new_id))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity, existing[0]))
            else:
                cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (user_id, new_id, quantity))
        cursor.execute("DELETE FROM inventory WHERE item_name = ?", (old_id,))

        cursor.execute("SELECT user_id, active, purchased_at FROM player_cosmetics WHERE cosmetic_id = ?", (old_id,))
        for user_id, active, purchased_at in cursor.fetchall():
            cursor.execute("""
                INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at)
                VALUES (?, ?, 'frame', 0, ?)
            """, (user_id, new_id, purchased_at or 0))
            if active:
                cursor.execute("UPDATE player_cosmetics SET active = 0 WHERE user_id = ? AND type = 'frame'", (user_id,))
                cursor.execute("UPDATE player_cosmetics SET active = 1 WHERE user_id = ? AND cosmetic_id = ?", (user_id, new_id))
        cursor.execute("DELETE FROM player_cosmetics WHERE cosmetic_id = ?", (old_id,))


def ensure_gemshop_db(cursor):
    cursor.execute("PRAGMA table_info(players)")
    cols = {row[1] for row in cursor.fetchall()}
    if "gems" not in cols:
        cursor.execute("ALTER TABLE players ADD COLUMN gems INTEGER DEFAULT 0")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_perks(
            user_id TEXT NOT NULL,
            perk_id TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            purchased_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, perk_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_cosmetics(
            user_id TEXT NOT NULL,
            cosmetic_id TEXT NOT NULL,
            type TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            purchased_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, cosmetic_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_stats(
            user_id TEXT NOT NULL,
            stat TEXT NOT NULL,
            value INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, stat)
        )
    """)
    migrate_legacy_frames(cursor)


def add_item(cursor, user_id, item_name, qty=1):
    cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), item_name))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (str(user_id), item_name, qty))

def consume_item(cursor, user_id, item_name, qty=1):
    cursor.execute("SELECT id, quantity FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), item_name))
    row = cursor.fetchone()
    if not row or row[1] < qty:
        return False
    if row[1] == qty:
        cursor.execute("DELETE FROM inventory WHERE id = ?", (row[0],))
    else:
        cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (qty, row[0]))
    return True

def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute("INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)", (str(user_id), stat))
    cursor.execute("UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?", (amount, str(user_id), stat))

def cosmetic_label(cosmetic_id):
    return COSMETIC_LABELS.get(cosmetic_id, cosmetic_id.replace("token_", "").replace("_", " ").title())

def normalize_cosmetic_arg(raw, cosmetic_type):
    token = unicodedata.normalize("NFKD", (raw or "").strip().lower())
    token = "".join(char for char in token if not unicodedata.combining(char))
    token = token.replace("tema:", "").strip().replace(" ", "_")
    if token.startswith("token_"):
        return token
    prefix = "token_moldura_" if cosmetic_type == "frame" else "token_titulo_"
    return prefix + token

def choose_rare_hero():
    pool = [(hero_id, data) for hero_id, data in HEROES.items() if hero_id != "id-nome" and data.get("raridade", 1) >= 4]
    if not pool:
        pool = [(hero_id, data) for hero_id, data in HEROES.items() if hero_id != "id-nome"]
    weights = [1 if data.get("raridade", 1) >= 5 else 4 for _, data in pool]
    return random.choices(pool, weights=weights, k=1)[0]


class GemShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_gemshop_db(cursor)
        conn.commit()
        conn.close()

    def _shop_embed(self, user, gems):
        embed = discord.Embed(
            title="💎 Loja de Gemas VIP",
            description=(
                f"Sua Carteira de Gems: **{gems:,}** 💎\n"
                "TutoriUAU: *Aqui vendemos poder permanente, cosmético permanente e arrependimento temporário.*"
            ),
            color=discord.Color.magenta(),
        )
        lines = []
        for item_id, item in GEM_ITEMS.items():
            extra = f" *(Máx Lvl {item['max_level']})*" if item["kind"] == "perk" else ""
            lines.append(f"`{item_id}` **{item['name']}** — {item['price']:,} Gems{extra}\n└ {item['desc']}")
            
        embed.add_field(name="Buffs e Vantagens", value="\n\n".join(lines[:3]), inline=False)
        embed.add_field(name="Tickets e Summons", value="\n\n".join(lines[3:6]), inline=False)
        embed.add_field(name="Cosméticos e Temas", value="\n\n".join(lines[6:]), inline=False)
        
        embed.set_footer(text="Use `echo gemcomprar <ID>`. Temas viram tokens na mochila para equipar com `echo moldura <nome>`.")
        return embed

    @commands.command(name="gemshop", aliases=["lojagems", "loja_gems", "loja_gemas", "gemas"])
    async def gemshop_cmd(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_gemshop_db(cursor)
        cursor.execute("SELECT gems FROM players WHERE user_id = ?", (str(ctx.author.id),))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if not row:
            return await ctx.send("Use `echo iniciar` antes de tentar comprar brilho engarrafado.")
        await ctx.send(embed=self._shop_embed(ctx.author, row[0] or 0))

    @commands.command(name="gemcomprar", aliases=["comprargem", "comprar_gems"])
    async def gemcomprar_cmd(self, ctx, item_id: int = None):
        if item_id not in GEM_ITEMS:
            return await ctx.send("❌ Use `echo gemshop` para ver os IDs. A realidade é dura.")
            
        item = GEM_ITEMS[item_id]
        user_id = str(ctx.author.id)
        
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_gemshop_db(cursor)
        
        cursor.execute("SELECT gems FROM players WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return await ctx.send("❌ Use `echo iniciar` primeiro.")
            
        gems = row[0] or 0
        if gems < item["price"]:
            conn.close()
            return await ctx.send(f"💸 Gems insuficientes. Você tem **{gems:,}** e precisa de **{item['price']:,}**.")

        # Lógica de compra
        if item["kind"] == "perk":
            cursor.execute("SELECT level FROM player_perks WHERE user_id = ? AND perk_id = ?", (user_id, item["perk"]))
            perk = cursor.fetchone()
            current = perk[0] if perk else 0
            
            if current >= item["max_level"]:
                conn.close()
                return await ctx.send("❌ Esse bônus já está no nível máximo. Até o poder tem limite.")
                
            if perk:
                cursor.execute("UPDATE player_perks SET level = level + 1, purchased_at = ? WHERE user_id = ? AND perk_id = ?", (int(time.time()), user_id, item["perk"]))
            else:
                cursor.execute("INSERT INTO player_perks (user_id, perk_id, level, purchased_at) VALUES (?, ?, 1, ?)", (user_id, item["perk"], int(time.time())))
            result = f"📈 Perk **{item['name']}** comprado. Nível atual: **{current + 1}/{item['max_level']}**."
            
        elif item["kind"] == "cosmetic":
            cursor.execute("SELECT 1 FROM player_cosmetics WHERE user_id = ? AND cosmetic_id = ?", (user_id, item["item"]))
            if cursor.fetchone():
                conn.close()
                return await ctx.send("❌ Você já possui esse cosmético. Comprar de novo seria só ostentação com bug.")
                
            # Dá o item no inventário e já destranca nos cosmeticos permanentemente
            add_item(cursor, user_id, item["item"], 1)
            cursor.execute(
                "INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, item["item"], item["type"], int(time.time())),
            )
            result = f"🖼️ Cosmético **{item['name']}** comprado! Token permanente adicionado à mochila. Use `echo moldura {item['item'].replace('token_moldura_', '').replace('_', ' ')}` para equipar."
            
        else:
            add_item(cursor, user_id, item["item"], item.get("qty", 1))
            result = f"🎒 Item **{item['name']}** comprado e enviado para a mochila."

        # Desconta Gems e finaliza
        cursor.execute("UPDATE players SET gems = gems - ? WHERE user_id = ?", (item["price"], user_id))
        add_stat(cursor, user_id, "gemshop_purchases", 1)
        conn.commit()
        conn.close()
        
        await ctx.send(f"✅ {result}\n*TutoriUAU: compra registrada. O recibo emocional é por sua conta.*")

    async def _equip_cosmetic(self, ctx, cosmetic_type, raw):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_gemshop_db(cursor)
        
        if not raw or raw.lower() in ["lista", "listar", "ver"]:
            cursor.execute("SELECT cosmetic_id, active FROM player_cosmetics WHERE user_id = ? AND type = ? ORDER BY purchased_at DESC", (user_id, cosmetic_type))
            rows = cursor.fetchall()
            conn.close()
            if not rows:
                return await ctx.send("❌ Você não possui cosméticos desse tipo.")
            lines = [f"{'✅ ATIVO | ' if active else '📦 '} `{cosmetic_id.replace('token_moldura_', '').replace('token_titulo_', '')}` - **{cosmetic_label(cosmetic_id)}**" for cosmetic_id, active in rows]
            return await ctx.send("**Seus Cosméticos:**\n" + "\n".join(lines) + f"\n\nPara equipar use: `echo {'moldura' if cosmetic_type == 'frame' else 'titulo'} <nome>`")

        if raw.lower() in ["remover", "limpar", "padrao", "padrão"]:
            cursor.execute("UPDATE player_cosmetics SET active = 0 WHERE user_id = ? AND type = ?", (user_id, cosmetic_type))
            conn.commit()
            conn.close()
            return await ctx.send("✅ Cosmético removido. Visual padrão restaurado. Minimalismo ou falta de orçamento?")

        cosmetic_id = normalize_cosmetic_arg(raw, cosmetic_type)
        cursor.execute("SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ? AND quantity > 0", (user_id, cosmetic_id))
        
        if cursor.fetchone():
            cursor.execute(
                "INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, cosmetic_id, cosmetic_type, int(time.time())),
            )
            
        cursor.execute("SELECT 1 FROM player_cosmetics WHERE user_id = ? AND cosmetic_id = ? AND type = ?", (user_id, cosmetic_id, cosmetic_type))
        if not cursor.fetchone():
            conn.close()
            return await ctx.send(f"❌ Você não possui o token `{cosmetic_id}`. Compre na GemShop primeiro.")
            
        cursor.execute("UPDATE player_cosmetics SET active = 0 WHERE user_id = ? AND type = ?", (user_id, cosmetic_type))
        cursor.execute("UPDATE player_cosmetics SET active = 1 WHERE user_id = ? AND cosmetic_id = ?", (user_id, cosmetic_id))
        conn.commit()
        conn.close()
        
        await ctx.send(f"✅ Cosmético ativo: **{cosmetic_label(cosmetic_id)}**. Tente usar `echo perfil` para ver a magia.")

    @commands.command(name="moldura", aliases=["frame", "tema"])
    async def moldura_cmd(self, ctx, *, token: str = None):
        await self._equip_cosmetic(ctx, "frame", token)

    @commands.command(name="titulo", aliases=["title"])
    async def titulo_cmd(self, ctx, *, token: str = None):
        await self._equip_cosmetic(ctx, "title", token)

    @commands.command(name="ticketheroi", aliases=["ticket_heroi", "ticket_herói", "usar_ticket_heroi"])
    async def ticket_heroi_cmd(self, ctx):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_gemshop_db(cursor)
        if not consume_item(cursor, user_id, "ticket_heroi_raro", 1):
            conn.close()
            return await ctx.send("❌ Você não tem `ticket_heroi_raro`. O TutoriUAU procurou na mochila e encontrou apenas poeira.")
            
        hero_id, hero = choose_rare_hero()
        rarity = hero.get("raridade", 4)
        cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, hero_id, rarity))
        conn.commit()
        conn.close()
        await ctx.send(f"✨ Ticket usado! O portal mágico se abriu e você recebeu {hero.get('emoji', '✨')} **{hero.get('nome', hero_id)}** ({'⭐' * rarity}).")

    @commands.command(name="escolherheroi", aliases=["escolher_heroi", "escolher_herói", "selecionarheroi"])
    async def escolher_heroi_cmd(self, ctx, *, hero_id: str = None):
        if not hero_id:
            return await ctx.send("❌ Use `echo escolherheroi <nome_do_heroi>`. Consulte os nomes no catálogo.")
            
        hero_id = hero_id.strip().lower().replace(" ", "_")
        
        # Flexibilidade para digitar o nome com espaços ou buscar no dict
        encontrado_id = None
        if hero_id in HEROES and hero_id != "id-nome":
            encontrado_id = hero_id
        else:
            for k, v in HEROES.items():
                if k == "id-nome": continue
                if v.get("nome", "").lower().replace(" ", "_") == hero_id:
                    encontrado_id = k
                    break
                    
        if not encontrado_id:
            return await ctx.send("❌ Herói não encontrado. Confira o nome exato no `echo catalogo`.")
            
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_gemshop_db(cursor)
        
        if not consume_item(cursor, user_id, "ticket_escolha_heroi", 1):
            conn.close()
            return await ctx.send("❌ Você não tem o cobiçado `ticket_escolha_heroi`.")
            
        hero = HEROES[encontrado_id]
        rarity = hero.get("raridade", 1)
        cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, encontrado_id, rarity))
        conn.commit()
        conn.close()
        
        await ctx.send(f"👑 Escolha Divina registrada! {hero.get('emoji', '✨')} **{hero.get('nome', encontrado_id)}** ({'⭐' * rarity}) entrou para sua coleção.")

async def setup(bot):
    await bot.add_cog(GemShop(bot))
