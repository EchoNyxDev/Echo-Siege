import sqlite3

import discord
from discord import app_commands
from discord.ext import commands


def ensure_rank_schema(cursor):
    cursor.execute("PRAGMA table_info(players)")
    cols = {row[1] for row in cursor.fetchall()}
    needed = {
        "pvp_rating": "INTEGER DEFAULT 0",
        "pvp_wins": "INTEGER DEFAULT 0",
        "pvp_losses": "INTEGER DEFAULT 0",
        "arena_record": "INTEGER DEFAULT 0",
        "gold": "INTEGER DEFAULT 0",
        "level": "INTEGER DEFAULT 1",
    }
    for col, ddl in needed.items():
        if col not in cols:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} {ddl}")
    cursor.execute("""
        UPDATE players
        SET pvp_rating = 0
        WHERE COALESCE(pvp_wins, 0) = 0
          AND COALESCE(pvp_losses, 0) = 0
          AND COALESCE(pvp_rating, 0) = 1000
    """)


class RankPaginator(discord.ui.View):
    CATEGORIES = {
        "pvp": "PvP",
        "arena": "Arena",
        "ouro": "Ouro",
        "nivel": "Nível",
        "summon": "Summons",
        "colecao": "Coleção",
        "guildas": "Guildas",
        "campeoes": "Campeões",
    }

    def __init__(self, ctx, is_global=False):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.is_global = is_global
        self.category = "pvp"
        self.page = 0
        self.items_per_page = 10
        self.data = []
        self.update_data()

    def _query_rows(self, cursor):
        if self.category == "pvp":
            cursor.execute(
                "SELECT user_id, pvp_rating, pvp_wins FROM players ORDER BY pvp_rating DESC, pvp_wins DESC LIMIT 200"
            )
        elif self.category == "arena":
            cursor.execute("SELECT user_id, arena_record FROM players ORDER BY arena_record DESC LIMIT 200")
        elif self.category == "ouro":
            cursor.execute("SELECT user_id, gold FROM players ORDER BY gold DESC LIMIT 200")
        elif self.category == "nivel":
            cursor.execute("SELECT user_id, level, xp FROM players ORDER BY level DESC, xp DESC LIMIT 200")
        elif self.category == "summon":
            cursor.execute(
                """
                SELECT user_id, total_summons, total_5_star
                FROM summon_data
                ORDER BY total_summons DESC, total_5_star DESC
                LIMIT 200
                """
            )
        elif self.category == "colecao":
            cursor.execute(
                """
                SELECT user_id, COUNT(*) AS total, MAX(level) AS max_level
                FROM heroes
                GROUP BY user_id
                ORDER BY total DESC, max_level DESC
                LIMIT 200
                """
            )
        elif self.category == "guildas":
            cursor.execute(
                """
                SELECT id, name, level, raid_score, gold_bank
                FROM player_guilds
                ORDER BY raid_score DESC, level DESC, gold_bank DESC
                LIMIT 200
                """
            )
        elif self.category == "campeoes":
            cursor.execute(
                """
                SELECT user_id, rating, wins, weekly_score
                FROM champion_tower
                ORDER BY rating DESC, wins DESC, weekly_score DESC
                LIMIT 200
                """
            )
        return cursor.fetchall()

    def update_data(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        try:
            ensure_rank_schema(cursor)
            rows = self._query_rows(cursor)
        except sqlite3.OperationalError:
            rows = []
        conn.commit()
        conn.close()

        if self.category != "guildas" and not self.is_global and self.ctx.guild:
            member_ids = {str(member.id) for member in self.ctx.guild.members}
            rows = [row for row in rows if str(row[0]) in member_ids]

        self.data = rows
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "btn_prev":
                    child.disabled = self.page == 0
                elif child.custom_id == "btn_next":
                    child.disabled = (self.page + 1) * self.items_per_page >= len(self.data)

    def generate_embed(self):
        scope = "Global" if self.is_global else (self.ctx.guild.name if self.ctx.guild else "Local")
        categoria = self.CATEGORIES.get(self.category, self.category)
        embed = discord.Embed(
            title=f"Ranking {scope} - {categoria}",
            description="Os melhores registros atuais do Echo Siege.",
            color=discord.Color.gold(),
        )

        start = self.page * self.items_per_page
        chunk = self.data[start : start + self.items_per_page]
        lines = []

        for pos, row in enumerate(chunk, start + 1):
            if self.category == "pvp":
                lines.append(f"**{pos}** <@{row[0]}> - **{row[1]} ELO** ({row[2]} vitórias)")
            elif self.category == "arena":
                lines.append(f"**{pos}** <@{row[0]}> - **Andar {row[1]}**")
            elif self.category == "ouro":
                lines.append(f"**{pos}** <@{row[0]}> - **{row[1]:,} Gold**")
            elif self.category == "nivel":
                lines.append(f"**{pos}** <@{row[0]}> - **Nível {row[1]}** ({row[2]} XP)")
            elif self.category == "summon":
                lines.append(f"**{pos}** <@{row[0]}> - **{row[1]} summons** ({row[2]} 5⭐)")
            elif self.category == "colecao":
                lines.append(f"**{pos}** <@{row[0]}> - **{row[1]} heróis** (maior nível {row[2] or 1})")
            elif self.category == "guildas":
                lines.append(f"**{pos}** `{row[0]}` **{row[1]}** - Lv {row[2]} | Score {row[3]:,} | Banco {row[4]:,}")
            elif self.category == "campeoes":
                lines.append(f"**{pos}** <@{row[0]}> - **{row[1]} Prestígio** ({row[2]} vitórias | {row[3]:,} pts semanais)")

        embed.add_field(
            name=categoria,
            value="\n".join(lines) if lines else "Ainda não há dados para esta categoria.",
            inline=False,
        )
        total_pages = max(1, (len(self.data) + self.items_per_page - 1) // self.items_per_page)
        embed.set_footer(text=f"Página {self.page + 1}/{total_pages} • TutoriUAU: ranking mede progresso, não autoestima. Em teoria.")
        return embed

    @discord.ui.select(
        placeholder="Escolha o ranking...",
        options=[
            discord.SelectOption(label="PvP", value="pvp", description="Maior ELO e vitórias."),
            discord.SelectOption(label="Arena", value="arena", description="Maior andar alcancado."),
            discord.SelectOption(label="Ouro", value="ouro", description="Jogadores mais ricos."),
            discord.SelectOption(label="Nível", value="nivel", description="Maior nível de conta."),
            discord.SelectOption(label="Summons", value="summon", description="Mais invocações e 5 estrelas."),
            discord.SelectOption(label="Coleção", value="colecao", description="Mais heróis na conta."),
            discord.SelectOption(label="Guildas", value="guildas", description="Guildas mais competitivas."),
            discord.SelectOption(label="Campeões", value="campeoes", description="Maior prestígio na Torre dos Campeões."),
        ],
        custom_id="select_category",
    )
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Apenas quem abriu o ranking pode trocar a categoria.", ephemeral=True)
        self.category = select.values[0]
        self.update_data()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, custom_id="btn_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Apenas quem abriu o ranking pode mudar a página.", ephemeral=True)
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.primary, custom_id="btn_next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Apenas quem abriu o ranking pode mudar a página.", ephemeral=True)
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.generate_embed(), view=self)


class Rank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rank", aliases=["ranking", "top", "leaderboard"])
    async def rank_cmd(self, ctx, escopo: str = "local"):
        is_global = escopo.lower() in ["global", "g", "todos"]
        if not is_global and not ctx.guild:
            return await ctx.send("Use `echo rank global` fora de servidores.")
        view = RankPaginator(ctx, is_global=is_global)
        await ctx.send(embed=view.generate_embed(), view=view)

    @app_commands.command(name="rank", description="Mostra o ranking do jogo.")
    @app_commands.describe(escopo="local ou global")
    @app_commands.choices(
        escopo=[
            app_commands.Choice(name="Servidor Atual", value="local"),
            app_commands.Choice(name="Global", value="global"),
        ]
    )
    async def rank_slash(self, interaction: discord.Interaction, escopo: str = "local"):
        class MockCtx:
            def __init__(self, inter):
                self.author = inter.user
                self.guild = inter.guild

        is_global = escopo == "global"
        if not is_global and not interaction.guild:
            return await interaction.response.send_message("Use o ranking global fora de servidores.", ephemeral=True)
        ctx = MockCtx(interaction)
        view = RankPaginator(ctx, is_global=is_global)
        await interaction.response.send_message(embed=view.generate_embed(), view=view)


async def setup(bot):
    await bot.add_cog(Rank(bot))
