import discord
from discord import app_commands
from discord.ext import commands

from systems.i18n import (
    SUPPORTED_LANGUAGES,
    get_stored_language,
    normalize_key,
    normalize_language,
    resolve_user_language,
    set_user_language,
    translation_backend_status,
)


class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _status_embed(self, user, guild=None):
        stored = get_stored_language(user.id)
        active = resolve_user_language(user=user, guild=guild)
        backend = translation_backend_status()
        embed = discord.Embed(
            title="Idioma // Wolford",
            description=(
                "Escolha como o bot deve falar com você.\n\n"
                "`echo language auto` tenta usar o idioma do Discord quando disponível.\n"
                "`echo language pt|en|es` fixa português, inglês ou espanhol."
            ),
            color=discord.Color.teal(),
        )
        embed.add_field(name="Configurado", value=f"**{SUPPORTED_LANGUAGES.get(stored, stored)}**", inline=True)
        embed.add_field(name="Usando agora", value=f"**{SUPPORTED_LANGUAGES.get(active, active)}**", inline=True)
        embed.add_field(
            name="Tradução automática",
            value=(
                f"Motor ativo: **{backend}**."
                if backend
                else "Motor ausente neste ambiente. O bot continua em PT-BR até o Discloud instalar as dependências."
            ),
            inline=False,
        )
        embed.add_field(
            name="Aliases multilíngues",
            value=(
                "A ajuda aceita `echo help`, `echo commands` e `echo ayuda`. "
                "Na NIX, também funcionam exemplos como `echo nix mission`, `echo nix fight`, "
                "`echo nix shop`, `echo nix misión`, `echo nix pelear` e `echo nix tienda`."
            ),
            inline=False,
        )
        embed.set_footer(
            text=(
                "NIX: idioma salvo. TutoriUAU: ela aprendeu sotaque antes de aprender a pedir licença."
            )
        )
        return embed

    @commands.command(name="language", aliases=["idioma", "linguagem", "lang", "lenguaje"])
    async def language_prefix(self, ctx, idioma: str = None):
        action = normalize_key(idioma)
        if idioma is None or action in {"status", "estado", "info"}:
            return await ctx.send(embed=self._status_embed(ctx.author, ctx.guild))

        if action in {"test", "teste", "prueba"}:
            return await ctx.send(
                "A tradução está funcionando. Comandos, botões, títulos, descrições e mensagens devem acompanhar seu idioma."
            )

        normalized = normalize_language(idioma)
        if not normalized:
            valid = ", ".join(f"`{key}`" for key in ("auto", "pt", "en", "es"))
            return await ctx.send(f"Idioma inválido. Use {valid}.")

        set_user_language(ctx.author.id, normalized)
        label = SUPPORTED_LANGUAGES[normalized]
        await ctx.send(
            f"Idioma atualizado para **{label}**.\n"
            "NIX: preferência gravada. TutoriUAU: oficialmente bilíngue por pressão do roteiro."
        )

    @app_commands.command(name="language", description="Define o idioma das respostas do bot.")
    @app_commands.describe(idioma="auto, pt, en ou es")
    async def language_slash(self, interaction: discord.Interaction, idioma: str = "auto"):
        normalized = normalize_language(idioma)
        if not normalized:
            return await interaction.response.send_message(
                "Idioma inválido. Use `auto`, `pt`, `en` ou `es`.",
                ephemeral=True,
            )
        set_user_language(interaction.user.id, normalized)
        await interaction.response.send_message(
            f"Idioma atualizado para **{SUPPORTED_LANGUAGES[normalized]}**.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Language(bot))
