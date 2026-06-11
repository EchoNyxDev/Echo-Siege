from discord.ext import commands
from discord import app_commands
import discord
import sqlite3
import typing
import os
import sys

# Gambiarra infalível do TutoriUau pra achar a pasta 'data' sem crashar, socorro.
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
except ModuleNotFoundError:
    print("TUTORIUAU AVISO: Cadê o arquivo heroes.py na pasta data/?")
    HEROES = {}

class Iniciar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def iniciar_jogador(self, user, force=False):

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM players WHERE user_id = ?",
            (str(user.id),)
        )

        jogador = cursor.fetchone()

        # =========================
        # já existe
        # =========================
        if jogador and not force:
            conn.close()

            embed = discord.Embed(
                title="TUTORIUAU // SISTEMA",
                description=(
                    f"Ei, {user.mention}...\n\n"
                    "Você já iniciou sua jornada em Lugnica.\n"
                    "Eu lembro de você.\n"
                    "Infelizmente."
                ),
                color=discord.Color.red()
            )

            embed.set_footer(text="TutoriUau • Sempre observando. Sempre julgando.")

            return False, embed

        # =========================
        # cria jogador
        # =========================
        if not jogador:

            # players
            cursor.execute("""
                INSERT INTO players
                (user_id, gold, level, xp, main_hero)
                VALUES (?, ?, ?, ?, ?)
            """, (
                str(user.id),
                700,
                1,
                0,
                None
            ))

            # summon_data (NOVO SISTEMA UNIFICADO)
            cursor.execute("""
                INSERT INTO summon_data
                (user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons,
                 total_1_star, total_2_star, total_3_star, total_4_star, total_5_star)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(user.id),
                5,   # summon_tickets (OS 5 SUMMONS GRÁTIS AQUI!)
                1,   # shop_level
                0,   # pity_4
                0,   # pity_5
                0,   # total_summons
                0,   # 1*
                0,   # 2*
                0,   # 3*
                0,   # 4*
                0    # 5*
            ))

            conn.commit()

        conn.close()

        # =========================
        # EMBED PRINCIPAL
        # =========================

        embed = discord.Embed(
            title="TUTORIUAU // BOOT SEQUENCE COMPLETO",
            description=(
                f"**Um TutoriUau selvagem apareceu!**\n\n"
                f"Olá {user.mention}\n\n"
                "Bem-vindo a **Lugnica**!\n\n"
                "Eu sou o TutoriUau,\n"
                "uma entidade tutorial extremamente qualificada e não remunerada.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "VOCÊ SABE ONDE ESTÁ?\n\n"
                "Não?\n\n"
                "Ótimo.\n"
                "Isso facilita MUITO o meu trabalho.\n\n"
                "*tosse em modo profissional questionável*\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "LORE (VERSÃO QUE EU FUI OBRIGADO A RESUMIR)\n\n"
                "Este reino chamado Lugnica é uma fronteira instável entre dimensões.\n"
                "Ecos de outras realidades vazam constantemente aqui.\n\n"
                "Heróis são invocados para conter isso.\n"
                "Ou piorar tudo. Depende muito de quem puxa o summon.\n\n"
                "Eu poderia explicar melhor… mas meu contrato não cobre terapia existencial.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "RESUMO IMPORTANTE (LEIA ISSO OU SOFRA DEPOIS)\n\n"
                "• Você agora é um Invocador\n"
                "• Vai proteger Lugnica de invasões\n"
                "• Vai perder bastante antes de entender qualquer coisa\n"
                "• E mesmo assim vai continuar jogando (motivo desconhecido)\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "PRESENTE DE BOAS-VINDAS\n\n"
                "💰 700 Gold (dinheiro fictício, mas com autoestima)\n"
                "✨ 5x SummonUAU (use com responsabilidade… ou não)\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "PRÓXIMO PASSO\n\n"
                "Tá se coçando pra sair clicando em tudo, né?\n\n"
                "Então vai logo!\n\n"
                "`echo summon 5`\n"
                "ou\n"
                "`/summon`\n\n"
                "Depois volte aqui utilizando `echo tutorial`\n"
            ),
            color=discord.Color.from_rgb(135, 206, 250)
        )

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1493317042760056987/1511161459168514058/TutoriUAU.png"
        )

        return True, embed

    # PREFIX
    @commands.command(name="iniciar")
    async def iniciar_prefix(self, ctx):
        sucesso, mensagem = await self.iniciar_jogador(ctx.author)
        if isinstance(mensagem, discord.Embed):
            await ctx.send(embed=mensagem)
        else:
            await ctx.send(mensagem)

    # SLASH
    @app_commands.command(
        name="iniciar",
        description="Comece sua aventura em Lugnica"
    )
    async def iniciar_slash(self, interaction):
        sucesso, mensagem = await self.iniciar_jogador(interaction.user)
        if isinstance(mensagem, discord.Embed):
            await interaction.response.send_message(embed=mensagem)
        else:
            await interaction.response.send_message(mensagem)

async def setup(bot):
    await bot.add_cog(Iniciar(bot))