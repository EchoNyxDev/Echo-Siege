import discord
from discord.ext import commands
import sqlite3
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data.heroes import HEROES

class CatalogoPaginator(discord.ui.View):
    def __init__(self, ctx, title, linhas, obtidos, total, items_per_page=15):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.title_str = title
        self.linhas = linhas
        self.obtidos = obtidos
        self.total = total
        self.items_per_page = items_per_page
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "prev":
                    child.disabled = self.page == 0
                elif child.custom_id == "next":
                    child.disabled = (self.page + 1) * self.items_per_page >= len(self.linhas)

    def generate_embed(self):
        embed = discord.Embed(title=self.title_str, color=discord.Color.green())
        
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        chunk = self.linhas[start:end]
        
        embed.description = "\n".join(chunk)
        total_pages = max(1, (len(self.linhas) + self.items_per_page - 1) // self.items_per_page)
        
        embed.set_footer(text=f"🟢 Possui • ⚫ Não Possui | Coleção: {self.obtidos}/{self.total} | Página {self.page + 1}/{total_pages}")
        return embed

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, emoji="◀️", custom_id="prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Use seu próprio `echo catalogo`.", ephemeral=True)
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.primary, emoji="▶️", custom_id="next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Use seu próprio `echo catalogo`.", ephemeral=True)
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)


class Catalogo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_player_heroes(self, user_id):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT hero_id FROM heroes WHERE user_id = ?", (str(user_id),))
        resultados = cursor.fetchall()
        conn.close()
        return {r[0] for r in resultados}

    @commands.command(name="catalogo", aliases=["catálogo", "catalog", "personagens"])
    async def catalogo(self, ctx, classe: str = None):
        herois_jogador = self.get_player_heroes(ctx.author.id)
        total = len(HEROES)
        obtidos = sum(1 for hero_id in HEROES if hero_id in herois_jogador)
        porcentagem = round((obtidos / total) * 100, 2) if total else 0

        # =====================================
        # RESUMO GERAL
        # =====================================
        if not classe:
            classes = {}
            for hero_id, hero in HEROES.items():
                c = hero.get("classe", "Outros")
                classes[c] = classes.get(c, 0) + 1

            embed = discord.Embed(
                title="📖 Catálogo de Heróis",
                description=(f"🟢 Possui | ⚫ Não Possui\n\n"
                             f"📚 Coleção: **{obtidos}/{total}** ({porcentagem}%)\n\n"
                             f"Use: `echo catalogo [classe]`"),
                color=discord.Color.blue()
            )
            for nome, qtd in classes.items():
                embed.add_field(name=nome, value=f"{qtd} Heróis", inline=True)
            embed.set_footer(text="TutoriUAU • Complete sua coleção!")
            return await ctx.send(embed=embed)

        # =====================================
        # FILTRO POR CLASSE (PAGINADO)
        # =====================================
        classe = classe.lower()
        aliases = {
            "lider": "lider", "lideres": "lider", "líder": "lider",
            "atacante": "atacante", "assassino": "assassino",
            "mago": "mago", "suporte": "suporte",
            "tank": "tank", "atirador": "atirador"
        }
        
        classe_real = aliases.get(classe)
        if not classe_real:
            return await ctx.send("❌ Classe inválida. Tente: atacante, mago, suporte, tank, lider, assassino, atirador.")

        linhas = []
        for hero_id, hero in HEROES.items():
            if hero.get("classe", "").lower() != classe_real:
                continue

            possui = hero_id in herois_jogador
            emoji = "🟢" if possui else "⚫"
            nome = hero.get("nome", hero_id)
            raridade = hero.get("raridade", 1)
            estrelas = "⭐" * raridade
            linhas.append(f"{emoji} **{nome}** {estrelas}")

        if not linhas:
            return await ctx.send("❌ Nenhum herói encontrado nesta classe.")

        # Inicia a View de Paginação
        view = CatalogoPaginator(ctx, f"📖 Catálogo - {classe_real.title()}", linhas, obtidos, total)
        await ctx.send(embed=view.generate_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Catalogo(bot))
