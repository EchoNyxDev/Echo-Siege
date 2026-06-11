import discord
from discord.ext import commands
import sqlite3
import os
import sys
import random
import time

# Gambiarra para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
except ModuleNotFoundError:
    HEROES = {}

try:
    from data.monsters import HUNT_MONSTERS
except ModuleNotFoundError:
    HUNT_MONSTERS = {}

try:
    from data.pets import PETS
except Exception:
    PETS = {
        "slime_azul": {"nome": "Slime Azul", "raridade": 1, "is_gacha": True},
        "golem_de_pedra": {"nome": "Golem de Pedra", "raridade": 2, "is_gacha": True},
        "lobo_sombrio": {"nome": "Lobo Sombrio", "raridade": 3, "is_gacha": True},
        "fada_da_luz": {"nome": "Fada da Luz", "raridade": 3, "is_gacha": True},
        "dragao_bebe": {"nome": "Dragão Bebê", "raridade": 4, "is_gacha": True},
    }

# ==========================================
# CATÁLOGO DE ITENS DA LOJA
# ==========================================
SHOP_ITEMS = {
    # NÍVEL 1
    1: {"nome": "Poção Pequena", "desc": "Cura 100 de HP", "preco": 200, "nivel": 1, "db_name": "pocao_pequena", "emoji": "🧪"},
    2: {"nome": "Poção de Energia", "desc": "Zera o CD das Caçadas", "preco": 300, "nivel": 1, "db_name": "pocao_energia", "emoji": "⚡"},
    3: {"nome": "Kit de Reparos", "desc": "+50 Suprimentos para a muralha", "preco": 100, "nivel": 1, "db_name": "kit_reparos", "emoji": "🔨"},
    
    # NÍVEL 2
    4: {"nome": "Poção Média", "desc": "Cura 250 HP", "preco": 400, "nivel": 2, "db_name": "pocao_media", "emoji": "🍷"},
    5: {"nome": "Espada de Ferro", "desc": "+10 ATK", "preco": 500, "nivel": 2, "db_name": "espada_de_ferro", "emoji": "🗡️"},
    6: {"nome": "Cajado Arcano", "desc": "+10 MATK", "preco": 500, "nivel": 2, "db_name": "cajado_arcano", "emoji": "🦯"},
    7: {"nome": "Armadura de Couro", "desc": "+15 DEF", "preco": 500, "nivel": 2, "db_name": "armadura_de_couro", "emoji": "🦺"},
    8: {"nome": "Pergaminho de XP", "desc": "+25% XP na próxima caçada", "preco": 1000, "nivel": 2, "db_name": "pergaminho_de_xp", "emoji": "📜"},
    9: {"nome": "Pergaminho de Ouro", "desc": "+25% Gold na próxima caçada", "preco": 1000, "nivel": 2, "db_name": "pergaminho_de_ouro", "emoji": "📜"},
    
    # NÍVEL 3
    10: {"nome": "Lâmina Encantada", "desc": "+30 ATK", "preco": 2500, "nivel": 3, "db_name": "lamina_encantada", "emoji": "⚔️"},
    11: {"nome": "Tomo dos Sábios", "desc": "+30 MATK", "preco": 2500, "nivel": 3, "db_name": "tomo_dos_sabios", "emoji": "📘"},
    12: {"nome": "Escudo do Guardião", "desc": "+30 DEF", "preco": 2500, "nivel": 3, "db_name": "escudo_do_guardiao", "emoji": "🛡️"},
    13: {"nome": "Ticket de Pet", "desc": "Sorteia um pet aleatório", "preco": 2000, "nivel": 3, "db_name": "ticket_pet", "emoji": "🐾"},
    
    # NÍVEL 4 (LUGNICA DOURADA)
    14: {"nome": "Espada Imperial", "desc": "+75 ATK", "preco": 10000, "nivel": 4, "db_name": "espada_imperial", "emoji": "👑"},
    15: {"nome": "Coroa Arcana", "desc": "+75 MATK", "preco": 10000, "nivel": 4, "db_name": "coroa_arcana", "emoji": "💠"},
    16: {"nome": "Armadura Real", "desc": "+75 DEF", "preco": 10000, "nivel": 4, "db_name": "armadura_real", "emoji": "🛡️"},
    17: {"nome": "Relógio de Lugnica", "desc": "+20% XP e Gold Passivo", "preco": 15000, "nivel": 4, "db_name": "relogio_de_lugnica", "emoji": "⏳"},
    18: {"nome": "Bilhete Dourado", "desc": "Garante um herói 3⭐ ou superior", "preco": 10000, "nivel": 4, "db_name": "bilhete_dourado", "emoji": "🎟️"}
}

DROP_SELL_VALUES = {}
for monster_data in HUNT_MONSTERS.values():
    drop_id = monster_data.get("drop")
    if drop_id:
        DROP_SELL_VALUES[drop_id] = max(5, int(monster_data.get("gold_base", 10) * 0.45))


def normalizar_item(nome):
    return (nome or "").strip().lower().replace(" ", "_")


def nome_item_bonito(item_id):
    for item in SHOP_ITEMS.values():
        if item.get("db_name") == item_id:
            return item.get("nome", item_id.replace("_", " ").title())
    return item_id.replace("_", " ").title()


def garantir_tabela_pets(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            pet_id TEXT,
            pet_name TEXT,
            rarity INTEGER,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(pets)")
    colunas = {info[1] for info in cursor.fetchall()}
    novas_colunas = {
        "pet_id": "TEXT",
        "pet_name": "TEXT",
        "rarity": "INTEGER",
        "level": "INTEGER DEFAULT 1",
        "xp": "INTEGER DEFAULT 0",
    }
    for coluna, tipo in novas_colunas.items():
        if coluna not in colunas:
            cursor.execute(f"ALTER TABLE pets ADD COLUMN {coluna} {tipo}")


def escolher_pet_gacha():
    pool = [(pet_id, pet) for pet_id, pet in PETS.items() if pet.get("is_gacha", True)]
    if not pool:
        pool = list(PETS.items())

    pesos_por_raridade = {1: 55, 2: 25, 3: 13, 4: 5, 5: 2}
    pesos = [pesos_por_raridade.get(pet.get("raridade", 1), 1) for _, pet in pool]
    return random.choices(pool, weights=pesos, k=1)[0]


def garantir_coluna(cursor, tabela, coluna, ddl):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = {info[1] for info in cursor.fetchall()}
    if coluna not in colunas:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {ddl}")


def garantir_cosmeticos(cursor):
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


def consumir_item_inventario(cursor, user_id, item_name, qty=1):
    cursor.execute("SELECT id, quantity FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), item_name))
    item = cursor.fetchone()
    if not item or item[1] < qty:
        return False
    if item[1] == qty:
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item[0],))
    else:
        cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (qty, item[0]))
    return True


def escolher_heroi_raro():
    pool = [
        (hero_id, hero)
        for hero_id, hero in HEROES.items()
        if hero_id != "id-nome" and hero.get("raridade", 1) >= 4
    ]
    if not pool:
        pool = [(hero_id, hero) for hero_id, hero in HEROES.items() if hero_id != "id-nome"]
    pesos = [1 if hero.get("raridade", 1) >= 5 else 4 for _, hero in pool]
    return random.choices(pool, weights=pesos, k=1)[0]


class HeroChoiceSelect(discord.ui.Select):
    def __init__(self, cog, user_id, heroes):
        self.cog = cog
        self.user_id = user_id
        options = []
        for hero_id, hero in heroes[:25]:
            rarity = hero.get("raridade", 1)
            options.append(discord.SelectOption(
                label=hero.get("nome", hero_id)[:100],
                value=hero_id,
                description=f"{'⭐' * rarity} | {hero.get('classe', 'Sem Classe')}",
                emoji=hero.get("emoji", "✨"),
            ))
        super().__init__(placeholder="Escolha o herói do Ticket de Escolha...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Esse ticket não é seu. TutoriUAU confiscou a mão curiosa.", ephemeral=True)
        await self.cog._finalizar_escolha_heroi(interaction, self.values[0])


class HeroSearchModal(discord.ui.Modal):
    def __init__(self, cog, user):
        super().__init__(title="Pesquisar Herói")
        self.cog = cog
        self.user = user
        self.query = discord.ui.TextInput(label="Nome ou parte do nome", placeholder="Ex: Rem, Levi, Goku...", max_length=40)
        self.add_item(self.query)

    async def on_submit(self, interaction: discord.Interaction):
        embed, view = self.cog._hero_choice_panel(self.user, self.query.value)
        await interaction.response.edit_message(embed=embed, view=view)


class HeroChoiceView(discord.ui.View):
    def __init__(self, cog, user, heroes, query=""):
        super().__init__(timeout=180)
        self.cog = cog
        self.user = user
        if heroes:
            self.add_item(HeroChoiceSelect(cog, user.id, heroes))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Abra seu próprio Ticket de Escolha. O catálogo não é self-service alheio.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Pesquisar", style=discord.ButtonStyle.secondary, emoji="🔎")
    async def pesquisar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HeroSearchModal(self.cog, self.user))

# ==========================================
# PAGINADOR DA LOJA
# ==========================================
class LojaPaginator(discord.ui.View):
    def __init__(self, ctx, nome_loja, gold_atual, itens_texto_lista, items_per_page=6):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.nome_loja = nome_loja
        self.gold_atual = gold_atual
        self.itens_texto_lista = itens_texto_lista
        self.items_per_page = items_per_page
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "btn_prev":
                    child.disabled = self.page == 0
                elif child.custom_id == "btn_next":
                    child.disabled = (self.page + 1) * self.items_per_page >= len(self.itens_texto_lista)

    def generate_embed(self):
        embed = discord.Embed(
            title=f"🏪 Mercado de Lugnica - {self.nome_loja}",
            description=f"Bem-vindo! A prosperidade da cidade define o que os mercadores trazem.\n💰 **Seu Ouro:** {self.gold_atual:,}\n\nPara comprar digite: `echo comprar <Número do Item> <Quantidade>`\nPara usar consumíveis digite: `echo consumir <nome do item>`",
            color=discord.Color.gold()
        )
        
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        chunk = self.itens_texto_lista[start:end]
        
        embed.add_field(name="Itens Disponíveis", value="".join(chunk) if chunk else "Sem itens.", inline=False)
        
        total_pages = max(1, (len(self.itens_texto_lista) + self.items_per_page - 1) // self.items_per_page)
        embed.set_footer(text=f"Página {self.page + 1}/{total_pages} • Sua chance no Gacha muda conforme o nível da loja.")
        return embed

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, emoji="◀️", custom_id="btn_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Só quem abriu a loja pode folhear.", ephemeral=True)
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.primary, emoji="▶️", custom_id="btn_next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Só quem abriu a loja pode folhear.", ephemeral=True)
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)


class Loja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _hero_choice_panel(self, user, query=""):
        query_norm = (query or "").strip().lower()
        heroes = []
        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome":
                continue
            nome = hero.get("nome", hero_id)
            if query_norm and query_norm not in nome.lower() and query_norm not in hero_id.lower():
                continue
            heroes.append((hero_id, hero))
        heroes.sort(key=lambda item: (item[1].get("raridade", 1), item[1].get("nome", item[0])), reverse=True)
        embed = discord.Embed(
            title="Ticket de Escolha de Herói",
            description=(
                "Escolha um herói no menu abaixo. Use **Pesquisar** para filtrar por nome.\n"
                "O ticket só é gasto quando você confirma uma escolha."
            ),
            color=discord.Color.gold(),
        )
        linhas = [
            f"{hero.get('emoji', '✨')} **{hero.get('nome', hero_id)}** | {'⭐' * hero.get('raridade', 1)} | `{hero_id}`"
            for hero_id, hero in heroes[:10]
        ]
        embed.add_field(name="Prévia do catálogo", value="\n".join(linhas) if linhas else "Nenhum herói encontrado.", inline=False)
        embed.set_footer(text=f"TutoriUAU: mostrando {min(len(heroes), 25)}/{len(heroes)} resultado(s).")
        return embed, HeroChoiceView(self, user, heroes, query_norm)

    async def _finalizar_escolha_heroi(self, interaction, hero_id):
        user_id = str(interaction.user.id)
        if hero_id not in HEROES or hero_id == "id-nome":
            return await interaction.response.send_message("Herói inválido. O catálogo tossiu.", ephemeral=True)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        if not consumir_item_inventario(cursor, user_id, "ticket_escolha_heroi", 1):
            conn.close()
            return await interaction.response.send_message("Você não tem mais `ticket_escolha_heroi`.", ephemeral=True)
        hero = HEROES[hero_id]
        rarity = hero.get("raridade", 1)
        cursor.execute(
            "INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)",
            (user_id, hero_id, rarity),
        )
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="Herói Escolhido",
            description=f"{hero.get('emoji', '✨')} **{hero.get('nome', hero_id)}** ({'⭐' * rarity}) entrou na sua coleção.",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    def _obter_nivel_loja(self, guild_id):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT prosperidade FROM cidades WHERE guild_id = ?", (str(guild_id),))
            resultado = cursor.fetchone()
        except sqlite3.OperationalError:
            resultado = None
        conn.close()
        
        prosp = resultado[0] if resultado else 0
        
        if prosp >= 100: return 4, "Lugnica Dourada"
        elif prosp >= 75: return 3, "Nível 3"
        elif prosp >= 50: return 2, "Nível 2"
        else: return 1, "Nível 1 (Básica)"

    def _sincronizar_gacha(self, user_id, nivel_loja):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE summon_data SET shop_level = ? WHERE user_id = ?", (nivel_loja, str(user_id)))
        conn.commit()
        conn.close()

    @commands.command(name="loja", aliases=["shop", "mercado"])
    async def loja_cmd(self, ctx):
        if not ctx.guild: return await ctx.send("❌ Use em um servidor.")
        
        user_id = str(ctx.author.id)
        nivel_loja, nome_loja = self._obter_nivel_loja(ctx.guild.id)
        
        self._sincronizar_gacha(user_id, nivel_loja)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
        player_data = cursor.fetchone()
        conn.close()

        if not player_data:
            return await ctx.send("❌ Você precisa dar `echo iniciar` antes de querer comprar fiado.")

        gold_atual = player_data[0]

        lista_de_textos_itens = []
        for item_id, item_data in SHOP_ITEMS.items():
            if item_data["nivel"] <= nivel_loja:
                preco = item_data["preco"]
                desc = item_data["desc"]
                if nivel_loja == 4 and item_id == 4:
                    preco = 250
                    desc = "Cura 150 HP (Max 3) *[Desconto Dourado]*"
                
                lista_de_textos_itens.append(f"`{item_id}` {item_data['emoji']} **{item_data['nome']}** — {preco:,} Gold\n└ *{desc}*\n\n")

        view = LojaPaginator(ctx, nome_loja, gold_atual, lista_de_textos_itens)
        await ctx.send(embed=view.generate_embed(), view=view)

    @commands.command(name="comprar", aliases=["buy"])
    async def comprar_cmd(self, ctx, item_id: int = None, quantidade: int = 1):
        if not ctx.guild: return await ctx.send("❌ Use em um servidor.")
            
        if not item_id or item_id not in SHOP_ITEMS:
            return await ctx.send("❌ Informe um número de item válido! Veja os itens usando `echo loja`.")

        if quantidade < 1:
            return await ctx.send("❌ Você quer comprar ar? Quantidade deve ser pelo menos 1.")

        nivel_loja, _ = self._obter_nivel_loja(ctx.guild.id)
        item_data = SHOP_ITEMS[item_id]

        if item_data["nivel"] > nivel_loja:
            return await ctx.send(f"❌ O mercado local ainda não possui esse item. Aumente a Prosperidade da cidade para desbloquear a loja **Nível {item_data['nivel']}**.")

        preco_unitario = item_data["preco"]
        if nivel_loja == 4 and item_id == 4:
            preco_unitario = 250

        preco_total = preco_unitario * quantidade

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (str(ctx.author.id),))
        player_data = cursor.fetchone()

        if not player_data:
            conn.close()
            return await ctx.send("❌ Você precisa dar `echo iniciar` primeiro.")

        gold_atual = player_data[0]

        if gold_atual < preco_total:
            conn.close()
            return await ctx.send(f"💸 Tá faltando moeda! Você precisa de **{preco_total:,} Gold**, mas só tem **{gold_atual:,} Gold**.")

        cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (preco_total, str(ctx.author.id)))

        if item_id == 3:
            suprimentos = 50 * quantidade
            try: cursor.execute("UPDATE cidades SET suprimentos = suprimentos + ? WHERE guild_id = ?", (suprimentos, str(ctx.guild.id)))
            except sqlite3.OperationalError: pass
            cursor.execute("UPDATE city_stats SET suprimentos = suprimentos + ? WHERE id = 1", (suprimentos,))
            
            msg_sucesso = f"🔨 Compra realizada! Você comprou **{quantidade}x Kit(s) de Reparos** e aplicou diretamente nas muralhas (+{suprimentos} Suprimentos)."
        else:
            db_name = item_data["db_name"]
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(ctx.author.id), db_name))
            item_existe = cursor.fetchone()
            
            if item_existe:
                cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantidade, item_existe[0]))
            else:
                cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (str(ctx.author.id), db_name, quantidade))
            
            msg_sucesso = f"🛒 Compra realizada! Você comprou **{quantidade}x {item_data['nome']}** por {preco_total:,} Gold.\n*Verifique usando `echo mochila` e use com `echo consumir <nome>`.*"

        conn.commit()
        conn.close()

        await ctx.send(msg_sucesso)

    @commands.command(name="vender", aliases=["sell"])
    async def vender_cmd(self, ctx, *, entrada: str = None):
        if not entrada:
            return await ctx.send("❌ Uso correto: `echo vender <item> [quantidade|tudo]`")

        partes = entrada.strip().rsplit(" ", 1)
        if len(partes) == 2 and (partes[1].isdigit() or partes[1].lower() in ["tudo", "all"]):
            nome_item, quantidade = partes
        else:
            nome_item, quantidade = entrada.strip(), "1"

        item_id = normalizar_item(nome_item)
        if item_id not in DROP_SELL_VALUES:
            return await ctx.send("❌ Esse item não é um material de caça vendável. Apenas drops de `echo hunt` entram no sistema de venda.")

        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, quantity FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item_id))
        item = cursor.fetchone()
        if not item or item[1] <= 0:
            conn.close()
            return await ctx.send(f"❌ Você não tem **{nome_item_bonito(item_id)}** na mochila.")

        qtd_atual = item[1]
        if str(quantidade).lower() in ["tudo", "all"]:
            qtd_vender = qtd_atual
        else:
            try:
                qtd_vender = int(quantidade)
            except ValueError:
                conn.close()
                return await ctx.send("❌ A quantidade precisa ser um número ou `tudo`.")

        if qtd_vender < 1:
            conn.close()
            return await ctx.send("❌ A quantidade precisa ser pelo menos 1.")
        if qtd_vender > qtd_atual:
            conn.close()
            return await ctx.send(f"❌ Você só tem **{qtd_atual}x {nome_item_bonito(item_id)}**.")

        valor_unitario = DROP_SELL_VALUES[item_id]
        total = valor_unitario * qtd_vender

        if qtd_vender == qtd_atual:
            cursor.execute("DELETE FROM inventory WHERE id = ?", (item[0],))
        else:
            cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (qtd_vender, item[0]))

        cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (total, user_id))
        conn.commit()
        conn.close()

        await ctx.send(f"💰 Venda concluída! Você vendeu **{qtd_vender}x {nome_item_bonito(item_id)}** por **{total:,} Gold**.")

    # ==========================================
    # SISTEMA DE CONSUMO
    # ==========================================
    @commands.command(name="consumir", aliases=["usar", "use"])
    async def consumir_cmd(self, ctx, *, nome_item: str = None):
        if not nome_item:
            return await ctx.send("❌ Diga o que quer consumir! Ex: `echo consumir pocao de energia`")

        nome_formatado = nome_item.lower().replace(" ", "_").strip()
        
        # Mapeando nomes comuns que jogadores digitam para o ID no banco de dados
        aliases = {
            "pocao_pequena": "pocao_pequena", "poção_pequena": "pocao_pequena",
            "pocao_de_energia": "pocao_energia", "poção_de_energia": "pocao_energia", "pocao_energia": "pocao_energia",
            "pocao_media": "pocao_media", "poção_média": "pocao_media",
            "pergaminho_de_xp": "pergaminho_de_xp", "pergaminho_xp": "pergaminho_de_xp",
            "pergaminho_de_ouro": "pergaminho_de_ouro", "pergaminho_ouro": "pergaminho_de_ouro",
            "ticket_de_pet": "ticket_pet", "ticket_pet": "ticket_pet",
            "ticket_heroi_raro": "ticket_heroi_raro", "ticket_de_heroi_raro": "ticket_heroi_raro",
            "ticket_escolha_heroi": "ticket_escolha_heroi", "ticket_de_escolha_de_heroi": "ticket_escolha_heroi",
            "bilhete_dourado": "bilhete_dourado",
            "kit_de_reparos": "kit_reparos", "kit_reparos": "kit_reparos",
            "relogio_de_lugnica": "relogio_de_lugnica", "relogio_lugnica": "relogio_de_lugnica"
        }
        
        db_name = aliases.get(nome_formatado, nome_formatado)
        
        # Trava equipamentos
        if db_name in ["espada_de_ferro", "cajado_arcano", "armadura_de_couro", "lamina_encantada", "tomo_dos_sabios", "escudo_do_guardiao", "espada_imperial", "coroa_arcana", "armadura_real"]:
            return await ctx.send("🛡️ Isso é um equipamento! Você não pode comer uma espada. Use `echo equipar <ID_Heroi> <Nome_do_Item>`.")
            
        if db_name == "relogio_de_lugnica":
            return await ctx.send("⏳ O Relógio de Lugnica é um item passivo! Apenas tê-lo na mochila já te garante os bônus.")

        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, quantity FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, db_name))
        item = cursor.fetchone()
        
        if not item or item[1] < 1:
            conn.close()
            return await ctx.send(f"❌ Você não tem `{nome_item}` na mochila.")
            
        item_table_id = item[0]
        qtd = item[1]
        msg_sucesso = ""
        
        # Aplicação dos efeitos
        if db_name == "pocao_energia":
            try: cursor.execute("UPDATE players SET last_hunt = 0, last_adventure = 0 WHERE user_id = ?", (user_id,))
            except sqlite3.OperationalError: pass
            msg_sucesso = "⚡ Glup, glup! Você bebeu a Poção de Energia. Seus tempos de espera de Caçada e Aventura foram zerados!"
            
        elif db_name in ["pocao_pequena", "pocao_media"]:
            cura = 100 if db_name == "pocao_pequena" else 250
            garantir_coluna(cursor, "players", "battle_hp_bonus", "INTEGER DEFAULT 0")
            cursor.execute("UPDATE players SET battle_hp_bonus = battle_hp_bonus + ? WHERE user_id = ?", (cura, user_id))
            msg_sucesso = f"🍷 Poção guardada para combate! Sua próxima batalha recebe **+{cura} HP** por herói."
            
        elif db_name == "kit_reparos":
            try: cursor.execute("UPDATE cidades SET suprimentos = suprimentos + 50 WHERE guild_id = ?", (str(ctx.guild.id),))
            except: pass
            cursor.execute("UPDATE city_stats SET suprimentos = suprimentos + 50 WHERE id = 1")
            msg_sucesso = "🔨 Você enviou um Kit de Reparos para Lugnica! +50 Suprimentos adicionados às defesas."

        elif db_name == "pergaminho_de_xp":
            try: cursor.execute("ALTER TABLE players ADD COLUMN buff_xp INTEGER DEFAULT 0")
            except sqlite3.OperationalError: pass
            cursor.execute("UPDATE players SET buff_xp = buff_xp + 1 WHERE user_id = ?", (user_id,))
            msg_sucesso = "📜 Você ativou o Pergaminho de XP! Sua próxima ação de ganho de experiência renderá 25% a mais."
            
        elif db_name == "pergaminho_de_ouro":
            try: cursor.execute("ALTER TABLE players ADD COLUMN buff_gold INTEGER DEFAULT 0")
            except sqlite3.OperationalError: pass
            cursor.execute("UPDATE players SET buff_gold = buff_gold + 1 WHERE user_id = ?", (user_id,))
            msg_sucesso = "📜 Você ativou o Pergaminho de Ouro! Sua próxima ação renderá 25% mais Ouro."
            
        elif db_name == "ticket_pet":
            garantir_tabela_pets(cursor)
            pet_id, pet_data = escolher_pet_gacha()
            pet_nome = pet_data.get("nome", pet_id.replace("_", " ").title())
            raridade = pet_data.get("raridade", 1)
            cursor.execute(
                "INSERT INTO pets (user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, ?, 1, 0)",
                (user_id, pet_id, pet_nome, raridade)
            )
            msg_sucesso = f"🐾 Magia de invocação! Você usou o Ticket e atraiu **{pet_nome}** ({'⭐' * raridade})!"

        elif db_name == "ticket_heroi_raro":
            h_id, h_data = escolher_heroi_raro()
            raridade = h_data.get("raridade", 4)
            cursor.execute(
                "INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)",
                (user_id, h_id, raridade),
            )
            msg_sucesso = f"🎟️ Ticket de Herói Raro usado! Você recebeu {h_data.get('emoji', '✨')} **{h_data.get('nome', h_id)}** ({'⭐' * raridade})."

        elif db_name == "ticket_escolha_heroi":
            conn.close()
            embed, view = self._hero_choice_panel(ctx.author)
            return await ctx.send(embed=embed, view=view)

        elif db_name.startswith("token_moldura_") or db_name.startswith("token_titulo_"):
            garantir_cosmeticos(cursor)
            tipo = "frame" if db_name.startswith("token_moldura_") else "title"
            cursor.execute(
                "INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, db_name, tipo, int(time.time())),
            )
            cursor.execute(
                "UPDATE player_cosmetics SET active = 0 WHERE user_id = ? AND type = ?",
                (user_id, tipo),
            )
            cursor.execute(
                "UPDATE player_cosmetics SET active = 1 WHERE user_id = ? AND cosmetic_id = ?",
                (user_id, db_name),
            )
            conn.commit()
            conn.close()
            comando = "moldura" if tipo == "frame" else "titulo"
            visual = "Tema de perfil" if tipo == "frame" else "Título"
            return await ctx.send(
                f"🎨 {visual} ativado. O token continua permanente na mochila; "
                f"use `echo {comando}` para trocar ou remover quando quiser."
            )
                
        elif db_name == "bilhete_dourado":
            herois_validos = [h_id for h_id, h_data in HEROES.items() if h_data.get("raridade", 1) >= 3]
            if herois_validos:
                h_id = random.choice(herois_validos)
                h_data = HEROES[h_id]
                cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", 
                              (user_id, h_id, h_data.get("raridade", 1)))
                msg_sucesso = f"🎟️ O Bilhete Dourado brilhou intensamente! Você invocou o Herói Raro **{h_data['nome']} ({'⭐' * h_data['raridade']})**!"
            else:
                msg_sucesso = "🎟️ O Bilhete Dourado brilhou... Mas o catálogo de heróis não pôde responder."
                
        else:
            conn.close()
            return await ctx.send(f"❌ O item `{nome_item}` existe, mas não parece ser comestível ou utilizável de forma direta.")
            
        # Remove o item usado do inventário
        if qtd > 1:
            cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (item_table_id,))
        else:
            cursor.execute("DELETE FROM inventory WHERE id = ?", (item_table_id,))
            
        conn.commit()
        conn.close()
        
        await ctx.send(msg_sucesso)

async def setup(bot):
    await bot.add_cog(Loja(bot))
