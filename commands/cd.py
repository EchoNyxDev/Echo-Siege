import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import time
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))

class Cooldowns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def formatar_tempo(self, segundos_restantes):
        if segundos_restantes <= 0: return "✅ **Pronto agora!**"
        
        m, s = divmod(int(segundos_restantes), 60)
        h, m = divmod(m, 60)
        
        if h > 0: return f"⏳ Faltam **{h}h {m}m**"
        return f"⏳ Faltam **{m}m {s}s**"

    async def processar_cds(self, user: discord.User):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT last_hunt, last_adventure, last_arena, last_daily FROM players WHERE user_id = ?", (str(user.id),))
        p_data = cursor.fetchone()

        if not p_data:
            conn.close()
            return f"❌ {user.mention}, não encontrei seus registros. Use `echo iniciar` primeiro."

        last_hunt, last_adv, last_arena, last_daily = p_data
        
        # Puxa status do Work (As 3 missões)
        try:
            cursor.execute("SELECT date_str FROM daily_quests WHERE user_id = ?", (str(user.id),))
            work_data = cursor.fetchone()
        except sqlite3.OperationalError:
            work_data = None
        try:
            cursor.execute("SELECT last_action FROM player_labyrinth WHERE user_id = ?", (str(user.id),))
            lab_data = cursor.fetchone()
        except sqlite3.OperationalError:
            lab_data = None
        conn.close()

        tempo_agora = time.time()
        hoje_str = datetime.now(BRT).strftime("%Y-%m-%d")

        # Cálculos Matemáticos de cada Cooldown
        cd_hunt = (last_hunt or 0) + (30 * 60) - tempo_agora
        cd_adv = (last_adv or 0) + (120 * 60) - tempo_agora
        cd_arena = (last_arena or 0) + (60 * 60) - tempo_agora
        cd_lab = ((lab_data[0] if lab_data else 0) or 0) + (5 * 60) - tempo_agora

        # Status do Daily
        if str(last_daily) == hoje_str:
            status_daily = "⏳ Volta amanhã (Meia-noite)"
        else:
            status_daily = "✅ **Pronto agora!**"

        # Status do Work (Quests Diárias)
        if work_data and work_data[0] == hoje_str:
            status_work = "⏳ Contratos pegues (Renovam à meia-noite)"
        else:
            status_work = "✅ **Novos contratos disponíveis!**"

        embed = discord.Embed(
            title=f"⏱️ Relógio de Ponto: {user.name}",
            description="O estado atual da tua estamina e tempo de espera para atividades em Lugnica.",
            color=discord.Color.dark_teal()
        )

        embed.add_field(name="🌲 Caçada (Hunt)", value=self.formatar_tempo(cd_hunt), inline=True)
        embed.add_field(name="🏰 Torre (Arena)", value=self.formatar_tempo(cd_arena), inline=True)
        embed.add_field(name="🏕️ Aventura (Adv)", value=self.formatar_tempo(cd_adv), inline=True)
        embed.add_field(name="🌀 Labirinto", value=self.formatar_tempo(cd_lab), inline=True)
        
        embed.add_field(name="📜 Missões da Guilda (Work)", value=status_work, inline=False)
        embed.add_field(name="🎁 Recompensa Diária (Daily)", value=status_daily, inline=False)

        embed.set_footer(text="TutoriUau • Esperar faz parte de ser um mero mortal.")
        return embed

    @commands.command(name="cd", aliases=["cooldown", "cooldowns", "tempo"])
    async def cd_cmd(self, ctx):
        embed = await self.processar_cds(ctx.author)
        if isinstance(embed, discord.Embed): await ctx.send(embed=embed)
        else: await ctx.send(embed)

    @app_commands.command(name="cd", description="Vê os teus tempos de espera atuais.")
    async def cd_slash(self, interaction: discord.Interaction):
        embed = await self.processar_cds(interaction.user)
        if isinstance(embed, discord.Embed): await interaction.response.send_message(embed=embed)
        else: await interaction.response.send_message(embed)

async def setup(bot):
    await bot.add_cog(Cooldowns(bot))
