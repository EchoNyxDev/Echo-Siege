import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
except ModuleNotFoundError:
    HEROES = {}
    EQUIPAMENTOS = {}

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

def cosmetic_label(cosmetic_id):
    labels = {
        "token_moldura_cidade_noturna": "Tema Cidade Noturna",
        "token_moldura_minecraft": "Tema Minecraft",
        "token_moldura_arvore_glacial": "Tema Árvore Glacial",
        "token_moldura_flores_cerejeira": "Tema Flores de Cerejeira",
    }
    return labels.get(cosmetic_id, str(cosmetic_id or "").replace("token_", "").replace("_", " ").title())

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
        "pet_id": "TEXT", "pet_name": "TEXT", "rarity": "INTEGER", 
        "level": "INTEGER DEFAULT 1", "xp": "INTEGER DEFAULT 0",
    }
    for coluna, tipo in novas_colunas.items():
        if coluna not in colunas:
            cursor.execute(f"ALTER TABLE pets ADD COLUMN {coluna} {tipo}")

def escolher_pet_gacha():
    pool = [(pet_id, pet) for pet_id, pet in PETS.items() if pet.get("is_gacha", True)]
    if not pool: pool = list(PETS.items())
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
    if not item or item[1] < qty: return False
    if item[1] == qty: cursor.execute("DELETE FROM inventory WHERE id = ?", (item[0],))
    else: cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (qty, item[0]))
    return True

def escolher_heroi_raro():
    pool = [(hero_id, hero) for hero_id, hero in HEROES.items() if hero_id != "id-nome" and hero.get("raridade", 1) >= 4]
    if not pool: pool = [(hero_id, hero) for hero_id, hero in HEROES.items() if hero_id != "id-nome"]
    pesos = [1 if hero.get("raridade", 1) >= 5 else 4 for _, hero in pool]
    return random.choices(pool, weights=pesos, k=1)[0]

# ==========================================
# INTERFACE DO TICKET DE ESCOLHA
# ==========================================
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
                emoji=hero.get("emoji", "✨")
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

    @discord.ui.button(label="Pesquisar Herói", style=discord.ButtonStyle.secondary, emoji="🔎")
    async def pesquisar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HeroSearchModal(self.cog, self.user))

# ==========================================
# CLASSE PRINCIPAL
# ==========================================
class Mochila(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_mochila(self, user: discord.User):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (str(user.id),))
        if not cursor.fetchone():
            conn.close()
            return f"❌ {user.mention}, você nem nasceu em Lugnica ainda. Dá `echo iniciar`."

        cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (str(user.id),))
        itens = cursor.fetchall()
        
        cursor.execute("SELECT summon_tickets FROM summon_data WHERE user_id = ?", (str(user.id),))
        summon_data = cursor.fetchone()
        tickets = summon_data[0] if summon_data else 0

        try:
            cursor.execute("SELECT cosmetic_id, type FROM player_cosmetics WHERE user_id = ? AND active = 1", (str(user.id),))
            active_cosmetics = cursor.fetchall()
        except sqlite3.OperationalError:
            active_cosmetics = []

        conn.close()

        embed = discord.Embed(
            title=f"🎒 Mochila de {user.name}",
            description="Vamos ver quantas tranqueiras você está carregando.",
            color=discord.Color.dark_gold()
        )

        mochila_vazia = True
        texto_itens = ""

        if tickets > 0:
            texto_itens += f"🎫 **Tickets de Invocação:** {tickets}\n"
            mochila_vazia = False

        for nome_item, quantidade in itens:
            nome_formatado = nome_item.replace("_", " ").title()
            texto_itens += f"📦 **{nome_formatado}:** {quantidade}\n"
            mochila_vazia = False

        if active_cosmetics:
            texto_itens += "\n🎨 **Cosméticos Ativos:**\n"
            for cosmetic_id, cosmetic_type in active_cosmetics:
                tipo = "Tema" if cosmetic_type == "frame" else "Título"
                texto_itens += f"• {tipo}: **{cosmetic_label(cosmetic_id)}**\n"
            mochila_vazia = False

        if mochila_vazia:
            embed.add_field(name="Itens", value="Literalmente nada. Uma teia de aranha e o vazio existencial. Vai caçar monstro!", inline=False)
        else:
            embed.add_field(name="Inventário", value=texto_itens, inline=False)

        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
        embed.set_footer(text="TutoriUau • Se eu fosse você, venderia tudo isso por Ouro. | Use: echo consumir <item>")
        return embed

    @commands.command(name="mochila", aliases=["inv", "inventario", "inventário", "bolsa"])
    async def mochila_prefix(self, ctx):
        resposta = await self.process_mochila(ctx.author)
        if isinstance(resposta, discord.Embed): await ctx.send(embed=resposta)
        else: await ctx.send(resposta)

    @app_commands.command(name="mochila", description="Olhe os itens que você guardou e esqueceu de usar.")
    async def mochila_slash(self, interaction: discord.Interaction):
        resposta = await self.process_mochila(interaction.user)
        if isinstance(resposta, discord.Embed): await interaction.response.send_message(embed=resposta)
        else: await interaction.response.send_message(resposta)

    # Lógica Visual do Ticket de Escolha
    def _hero_choice_panel(self, user, query=""):
        query_norm = (query or "").strip().lower()
        heroes = []
        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome": continue
            nome = hero.get("nome", hero_id)
            if query_norm and query_norm not in nome.lower() and query_norm not in hero_id.lower(): continue
            heroes.append((hero_id, hero))
            
        heroes.sort(key=lambda item: (item[1].get("raridade", 1), item[1].get("nome", item[0])), reverse=True)
        
        embed = discord.Embed(
            title="🎫 Ticket de Escolha de Herói",
            description=("Escolha um herói no menu abaixo. Use **Pesquisar** para filtrar por nome.\n"
                         "O ticket só é gasto quando você confirma a escolha."),
            color=discord.Color.gold(),
        )
        linhas = [f"{h.get('emoji', '✨')} **{h.get('nome', h_id)}** | {'⭐' * h.get('raridade', 1)} | `{h_id}`" for h_id, h in heroes[:10]]
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
        cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, hero_id, rarity))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✨ Herói Escolhido",
            description=f"A invocação direta foi concluída!\n{hero.get('emoji', '✨')} **{hero.get('nome', hero_id)}** ({'⭐' * rarity}) entrou na sua coleção.",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    # ==========================================
    # COMANDO CONSUMIR 
    # ==========================================
    @commands.command(name="consumir", aliases=["usar", "use"])
    async def consumir_cmd(self, ctx, *, nome_item: str = None):
        if not nome_item:
            return await ctx.send("❌ Diga o que quer consumir! Ex: `echo consumir pocao de energia`")

        nome_formatado = nome_item.lower().replace(" ", "_").strip()
        
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
            "relogio_de_lugnica": "relogio_de_lugnica", "relogio_lugnica": "relogio_de_lugnica",
            "passe_contrabandista": "passe_contrabandista",
            "amuleto_hibrido_eterno": "amuleto_hibrido_eterno", "pingente_dos_ecos_eternos": "amuleto_hibrido_eterno"
        }
        
        db_name = aliases.get(nome_formatado, nome_formatado)
        
        # --- TRAVA DINÂMICA DE EQUIPAMENTOS ---
        if db_name in EQUIPAMENTOS:
            return await ctx.send("🛡️ Isso é um equipamento (Arma/Armadura/Relíquia)! Você não pode consumi-lo. Use `echo equipar <ID_Heroi> <Nome_do_Item>`.")
            
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
        cor_embed = discord.Color.green()
        consumiu = True
        
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
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO cidades
                    (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
                    VALUES (?, 'Capital de Lugnica', 100000, 100000, 100, 0, 5000, 0)
                """, (str(ctx.guild.id),))
                cursor.execute(
                    "UPDATE cidades SET suprimentos = min(max_suprimentos, suprimentos + 50) WHERE guild_id = ?",
                    (str(ctx.guild.id),),
                )
            except Exception:
                pass
            cursor.execute("UPDATE city_stats SET suprimentos = min(max_suprimentos, suprimentos + 50) WHERE id = 1")
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
            cursor.execute("INSERT INTO pets (user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, ?, 1, 0)", (user_id, pet_id, pet_nome, raridade))
            msg_sucesso = f"🐾 Magia de invocação! Você usou o Ticket e atraiu **{pet_nome}** ({'⭐' * raridade})!"

        elif db_name == "passe_contrabandista":
            pets_lendarios = ["Fênix Menor", "Dragão de Bolso", "Cérbero Filhote", "Sombra Rastejante"]
            pet_ganho = random.choice(pets_lendarios)
            garantir_tabela_pets(cursor)
            cursor.execute("INSERT INTO pets (user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, 5, 1, 0)", (user_id, pet_ganho.lower().replace(" ", "_"), pet_ganho))
            cor_embed = discord.Color.gold()
            msg_sucesso = f"🎫 Você entregou o passe a um contrabandista sombrio e ele te deu um ovo misterioso...\nO ovo chocou: **{pet_ganho} (LENDÁRIO)**!"

        elif db_name == "ticket_heroi_raro":
            h_id, h_data = escolher_heroi_raro()
            raridade = h_data.get("raridade", 4)
            cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, h_id, raridade))
            msg_sucesso = f"🎟️ Ticket de Herói Raro usado! Você recebeu {h_data.get('emoji', '✨')} **{h_data.get('nome', h_id)}** ({'⭐' * raridade})."

        elif db_name == "bilhete_dourado":
            herois_validos = [h_id for h_id, h_data in HEROES.items() if h_data.get("raridade", 1) >= 3 and h_id != "id-nome"]
            if herois_validos:
                h_id = random.choice(herois_validos)
                h_data = HEROES[h_id]
                cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, h_id, h_data.get("raridade", 3)))
                cor_embed = discord.Color.gold()
                msg_sucesso = f"🎟️ O Bilhete Dourado brilhou intensamente! Você invocou o Herói Raro {h_data.get('emoji', '✨')} **{h_data['nome']} ({'⭐' * h_data.get('raridade', 3)})**!"
            else:
                consumiu = False
                msg_sucesso = "🎟️ O Bilhete Dourado brilhou... Mas o catálogo de heróis falhou em responder."

        elif db_name == "amuleto_hibrido_eterno":
            herois_miticos = [hid for hid, h in HEROES.items() if h.get("raridade", 1) >= 5 and hid != "id-nome"]
            if herois_miticos:
                h_id = random.choice(herois_miticos)
                h_data = HEROES[h_id]
                cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, h_id, h_data.get("raridade", 5)))
                cor_embed = discord.Color.purple()
                msg_sucesso = f"🌌 O Amuleto rachou e rasgou o espaço-tempo...\nUma lenda atendeu ao seu chamado: **{h_data.get('emoji', '✨')} {h_data.get('nome', 'Herói')} (MÍTICO)**!!!"
            else:
                consumiu = False
                msg_sucesso = "❌ Erro no Panteão: Nenhum herói mítico encontrado no sistema para invocação."

        elif db_name == "ticket_escolha_heroi":
            conn.close()
            embed, view = self._hero_choice_panel(ctx.author)
            return await ctx.send(embed=embed, view=view)

        elif db_name.startswith("token_moldura_") or db_name.startswith("token_titulo_"):
            garantir_cosmeticos(cursor)
            tipo = "frame" if db_name.startswith("token_moldura_") else "title"
            cursor.execute("INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, ?, 0, ?)", (user_id, db_name, tipo, int(time.time())))
            cursor.execute("UPDATE player_cosmetics SET active = 0 WHERE user_id = ? AND type = ?", (user_id, tipo))
            cursor.execute("UPDATE player_cosmetics SET active = 1 WHERE user_id = ? AND cosmetic_id = ?", (user_id, db_name))
            comando = "moldura" if tipo == "frame" else "titulo"
            visual = "Tema de perfil" if tipo == "frame" else "Título"
            msg_sucesso = f"🎨 {visual} ativado. O token continua permanente na mochila; use `echo {comando}` para trocar ou remover quando quiser."
            
        else:
            consumiu = False
            msg_sucesso = f"❌ O item `{nome_item.title()}` não pode ser consumido. Provavelmente é material de forja (use `echo forja`)."
            
        if consumiu:
            if qtd > 1: cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (item_table_id,))
            else: cursor.execute("DELETE FROM inventory WHERE id = ?", (item_table_id,))
            
        conn.commit()
        conn.close()
        
        await ctx.send(embed=discord.Embed(title="🎒 Inventário (Ação)", description=msg_sucesso, color=cor_embed))

async def setup(bot):
    await bot.add_cog(Mochila(bot))
