import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random
import os
import sys

# Gambiarra para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
    from data.receitas import RECEITAS
except ModuleNotFoundError:
    HEROES, EQUIPAMENTOS, RECEITAS = {}, {}, {}


def check_and_add_columns(cursor):
    """Garante que a tabela players tem as colunas de buffs para os pergaminhos"""
    cursor.execute("PRAGMA table_info(players)")
    colunas = [col[1] for col in cursor.fetchall()]
    
    if "buff_gold" not in colunas:
        cursor.execute("ALTER TABLE players ADD COLUMN buff_gold INTEGER DEFAULT 0")
    if "buff_xp" not in colunas:
        cursor.execute("ALTER TABLE players ADD COLUMN buff_xp INTEGER DEFAULT 0")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_pets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            pet_name TEXT NOT NULL,
            rarity INTEGER DEFAULT 1
        )
    """)


def cosmetic_label(cosmetic_id):
    labels = {
        "token_moldura_cidade_noturna": "Tema Cidade Noturna",
        "token_moldura_minecraft": "Tema Minecraft",
        "token_moldura_arvore_glacial": "Tema Árvore Glacial",
        "token_moldura_flores_cerejeira": "Tema Flores de Cerejeira",
    }
    return labels.get(
        cosmetic_id,
        str(cosmetic_id or "").replace("token_", "").replace("_", " ").title(),
    )


class Mochila(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Verifica as tabelas de buffs ao carregar o bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        check_and_add_columns(cursor)
        conn.commit()
        conn.close()

    async def process_mochila(self, user: discord.User):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        # Verifica se o jogador iniciou
        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (str(user.id),))
        if not cursor.fetchone():
            conn.close()
            return f"❌ {user.mention}, você nem nasceu em Lugnica ainda. Dá `echo iniciar`."

        # Busca itens do inventário
        cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ? AND quantity > 0", (str(user.id),))
        itens = cursor.fetchall()
        
        # Busca Tickets na tabela de summon_data
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

        # Mostra os Tickets de Gacha
        if tickets > 0:
            texto_itens += f"🎫 **Tickets de Invocação:** {tickets}\n"
            mochila_vazia = False

        # Formata os itens normais
        for nome_item, quantidade in itens:
            # Substitui os underlines por espaços e capitaliza pra ficar bonito (ex: escamas_de_dragao -> Escamas De Dragao)
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
        if isinstance(resposta, discord.Embed):
            await ctx.send(embed=resposta)
        else:
            await ctx.send(resposta)

    @app_commands.command(name="mochila", description="Olhe os itens que você guardou e esqueceu de usar.")
    async def mochila_slash(self, interaction: discord.Interaction):
        resposta = await self.process_mochila(interaction.user)
        if isinstance(resposta, discord.Embed):
            await interaction.response.send_message(embed=resposta)
        else:
            await interaction.response.send_message(resposta)

    # ==========================================
    # NOVO COMANDO: CONSUMIR ITENS DA FORJA
    # ==========================================
    @commands.command(name="consumir", aliases=["usar"])
    async def consumir_cmd(self, ctx, *, nome_item: str = None):
        if not nome_item:
            return await ctx.send("❌ Use `echo consumir <nome_do_item>`. (Ex: `echo consumir pocao de energia`)")

        item_formatado = nome_item.lower().replace(" ", "_")
        user_id = str(ctx.author.id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        # Verifica se o jogador tem o item
        cursor.execute("SELECT id, quantity FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item_formatado))
        item_db = cursor.fetchone()

        if not item_db or item_db[1] <= 0:
            conn.close()
            return await ctx.send(f"❌ Você não tem `{nome_item.title()}` na mochila. Ilusão de ótica não enche a barriga.")

        # ==========================================
        # LÓGICA DE EFEITOS DOS ITENS
        # ==========================================
        mensagem_efeito = ""
        cor_embed = discord.Color.green()
        consumiu = True

        if item_formatado == "pocao_energia":
            cursor.execute("UPDATE players SET last_hunt = 0, last_adventure = 0 WHERE user_id = ?", (user_id,))
            mensagem_efeito = "⚡ A poção queimou a sua garganta, mas os seus músculos vibraram! **Seus tempos de recarga (Caçada e Aventura) foram zerados.**"
        
        elif item_formatado == "pergaminho_de_xp":
            cursor.execute("UPDATE players SET buff_xp = COALESCE(buff_xp, 0) + 1 WHERE user_id = ?", (user_id,))
            mensagem_efeito = "📜 Você leu o pergaminho e sentiu o cérebro expandir. **+25% de XP na sua próxima ação concluída.**"
            
        elif item_formatado == "pergaminho_de_ouro":
            cursor.execute("UPDATE players SET buff_gold = COALESCE(buff_gold, 0) + 1 WHERE user_id = ?", (user_id,))
            mensagem_efeito = "📜 Símbolos brilhantes indicam sorte financeira. **+25% de Ouro garantido na sua próxima ação concluída.**"

        elif item_formatado == "kit_reparos":
            # Tenta reparar a cidade, se não estiver numa guilda/cidade, dá ouro direto.
            cursor.execute("SELECT guild_id FROM player_guild_members WHERE user_id = ?", (user_id,))
            g_data = cursor.fetchone()
            if g_data:
                try: cursor.execute("UPDATE cidades SET prosperidade = prosperidade + 25, moral = moral + 10 WHERE guild_id = ?", (g_data[0],))
                except sqlite3.OperationalError: pass
                cursor.execute("UPDATE city_stats SET prosperidade = prosperidade + 25, moral = moral + 10 WHERE id = 1")
                mensagem_efeito = "🔨 Você usou o kit para remendar as defesas da sua Cidade. **Prosperidade e Moral aumentaram.**"
            else:
                cursor.execute("UPDATE players SET gold = gold + 500 WHERE user_id = ?", (user_id,))
                mensagem_efeito = "🔨 Sem uma guilda para consertar, você vendeu as peças do kit por **500 Gold**."

        elif item_formatado == "ticket_pet":
            pets = ["Lobo Filhote", "Slime Doméstico", "Corvo de Rapina", "Gato Fantasma"]
            pet_ganho = random.choice(pets)
            cursor.execute("INSERT INTO player_pets (user_id, pet_name, rarity) VALUES (?, ?, 3)", (user_id, pet_ganho))
            mensagem_efeito = f"🐾 O ticket brilhou e invocou um companheiro: **{pet_ganho} (Raro)**!"

        elif item_formatado == "passe_contrabandista":
            pets_lendarios = ["Fênix Menor", "Dragão de Bolso", "Cérbero Filhote", "Sombra Rastejante"]
            pet_ganho = random.choice(pets_lendarios)
            cursor.execute("INSERT INTO player_pets (user_id, pet_name, rarity) VALUES (?, ?, 5)", (user_id, pet_ganho))
            cor_embed = discord.Color.gold()
            mensagem_efeito = f"🎫 Você entregou o passe a um contrabandista sombrio e ele te deu um ovo misterioso...\nO ovo chocou: **{pet_ganho} (LENDÁRIO)**!"

        elif item_formatado == "bilhete_dourado":
            # Puxa heróis Raros (3 estrelas ou mais)
            herois_raros = [hid for hid, h in HEROES.items() if h.get("raridade", 1) >= 3 and hid != "id-nome"]
            if herois_raros:
                h_id = random.choice(herois_raros)
                h_data = HEROES[h_id]
                raridade = h_data.get("raridade", 3)
                cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (user_id, h_id, raridade))
                cor_embed = discord.Color.gold()
                mensagem_efeito = f"🎟️ O Bilhete Dourado emitiu uma luz ofuscante!\nVocê invocou: **{h_data.get('emoji', '✨')} {h_data.get('nome', 'Herói')} ({raridade}★)**!"
            else:
                consumiu = False
                mensagem_efeito = "❌ Erro no Gacha: O Panteão de heróis raros está vazio."

        elif item_formatado == "amuleto_hibrido_eterno":
            # Puxa APENAS Heróis Míticos (5 estrelas)
            herois_miticos = [hid for hid, h in HEROES.items() if h.get("raridade", 1) == 5 and hid != "id-nome"]
            if herois_miticos:
                h_id = random.choice(herois_miticos)
                h_data = HEROES[h_id]
                cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, 5, 1, 1, 0)", (user_id, h_id))
                cor_embed = discord.Color.purple()
                mensagem_efeito = f"🌌 O Amuleto rachou e rasgou o espaço-tempo...\nUma lenda atendeu ao seu chamado: **{h_data.get('emoji', '✨')} {h_data.get('nome', 'Herói')} (MÍTICO 5★)**!!!"
            else:
                consumiu = False
                mensagem_efeito = "❌ Erro no Panteão: Não há deuses ou lendas cadastrados (Nenhum herói de 5★ encontrado no sistema)."

        else:
            consumiu = False
            mensagem_efeito = f"❌ O item `{nome_item.title()}` não pode ser consumido. Provavelmente é material de forja ou equipamento (use `echo equipar <ID> <nome_do_item>`)."

        # ==========================================
        # FINALIZAÇÃO
        # ==========================================
        if consumiu:
            cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (item_db[0],))
            cursor.execute("DELETE FROM inventory WHERE quantity <= 0")
            
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🎒 Inventário (Ação)",
            description=mensagem_efeito,
            color=cor_embed
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mochila(bot))