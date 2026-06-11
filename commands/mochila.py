import discord
from discord.ext import commands
from discord import app_commands
import sqlite3


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
        embed.set_footer(text="TutoriUau • Se eu fosse você, venderia tudo isso por Ouro.")

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

async def setup(bot):
    await bot.add_cog(Mochila(bot))
