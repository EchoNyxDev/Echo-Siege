import discord
from discord.ext import commands
import sqlite3
import os
import sys

# Gambiarra para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.monsters import HUNT_MONSTERS
except ModuleNotFoundError:
    HUNT_MONSTERS = {}

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
            description=f"Bem-vindo! A prosperidade da cidade define o que os mercadores trazem.\n💰 **Seu Ouro:** {self.gold_atual:,}\n\nPara comprar digite: `echo comprar <Número do Item> <Quantidade>`\nPara vender drops digite: `echo vender <nome do item>`",
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

async def setup(bot):
    await bot.add_cog(Loja(bot))