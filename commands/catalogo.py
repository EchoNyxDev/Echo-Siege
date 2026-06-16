import os
import sqlite3
import sys
import unicodedata

import discord
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data.heroes import HEROES

try:
    from utils.hero_images import get_hero_attachment
except Exception:
    get_hero_attachment = None

try:
    from utils.hero_stats import calculate_hero_stats
except Exception:
    calculate_hero_stats = None

try:
    from utils.skills import get_hero_skill_descriptions
except Exception:
    get_hero_skill_descriptions = None


CLASS_ALIASES = {
    "atacante": "atacante",
    "assassino": "assassino",
    "assassinos": "assassino",
    "mago": "mago",
    "magos": "mago",
    "suporte": "suporte",
    "suportes": "suporte",
    "tank": "tank",
    "tanque": "tank",
    "tanks": "tank",
    "atirador": "atirador",
    "atiradores": "atirador",
    "arqueiro": "atirador",
    "lider": "lider",
    "lideres": "lider",
    "leader": "lider",
}

CLASS_DISPLAY = {
    "atacante": "Atacante",
    "assassino": "Assassino",
    "mago": "Mago",
    "suporte": "Suporte",
    "tank": "Tank",
    "atirador": "Atirador",
    "lider": "Líder",
}

CLASS_EMOJIS = {
    "atacante": "👊",
    "assassino": "⚔️",
    "mago": "🔥",
    "suporte": "🩹",
    "tank": "🛡️",
    "atirador": "🏹",
    "lider": "📚",
}

PROFILE_MODES = {
    "perfil",
    "perfis",
    "ficha",
    "fichas",
    "profile",
    "profiles",
    "galeria",
}

TUTOR_PROFILE_COMMENTS = [
    "TutoriUAU: arraste para o lado e finja que leu tudo, eu acredito em você.",
    "TutoriUAU: status base é sem equipamento, sem buff e sem aquela matemática suspeita do combate.",
    "TutoriUAU: divinos não aparecem aqui. Eles têm assessoria de imprensa própria.",
    "TutoriUAU: se o retrato não apareceu, falta o JPG do herói na pasta certa. Eu só narro o caos.",
    "TutoriUAU: habilidade bonita é ótimo; habilidade funcionando no combate é melhor ainda.",
]


def _normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return texto.lower().strip()


def _classe_real(valor):
    return CLASS_ALIASES.get(_normalizar_texto(valor))


def _classe_heroi(hero):
    return _classe_real(hero.get("classe")) or _normalizar_texto(hero.get("classe")) or "outros"


def _estrelas(raridade):
    try:
        raridade = int(raridade or 1)
    except (TypeError, ValueError):
        raridade = 1
    return "⭐" * max(1, raridade)


def _trim(texto, limite=360):
    texto = str(texto or "").strip()
    if len(texto) <= limite:
        return texto
    return texto[: limite - 3].rstrip() + "..."


def _chunk_lines(linhas, limite=950):
    chunks = []
    atual = ""
    for linha in linhas:
        linha = str(linha or "").strip()
        candidato = f"{atual}\n\n{linha}".strip() if atual else linha
        if len(candidato) > limite and atual:
            chunks.append(atual)
            atual = linha
        else:
            atual = candidato
    if atual:
        chunks.append(atual)
    return chunks


def _catalog_heroes(include_divine=True):
    return {
        str(hero_id): hero
        for hero_id, hero in HEROES.items()
        if hero_id != "id-nome" and (include_divine or not hero.get("divino"))
    }


def _base_stats(hero):
    if calculate_hero_stats:
        return calculate_hero_stats(hero, stars=1, level=1, equipment_bonuses=None)
    return {
        "hp": int(hero.get("hp", 100) or 100),
        "atk": int(hero.get("atk", 10) or 10),
        "matk": int(hero.get("matk", 10) or 10),
        "def": int(hero.get("def", 5) or 5),
        "spd": int(hero.get("spd", 10) or 10),
        "crt": int(hero.get("crt", 5) or 5),
    }


def _skill_lines(hero):
    raridade = hero.get("raridade", 1)
    if get_hero_skill_descriptions:
        try:
            habilidades = get_hero_skill_descriptions(hero, stars=10, rarity=raridade)
        except Exception:
            habilidades = []
        linhas = []
        for habilidade in habilidades:
            nome = habilidade.get("nome") or "Habilidade"
            tipo = habilidade.get("tipo") or "Base"
            descricao = habilidade.get("descricao") or "Sem descrição cadastrada ainda."
            linhas.append(f"**{tipo} - {nome}**\n{_trim(descricao)}")
        if linhas:
            return linhas

    linhas = []
    base = hero.get("habilidade")
    if isinstance(base, dict):
        linhas.append(
            f"**Base - {base.get('nome', 'Habilidade')}**\n"
            f"{_trim(base.get('descricao') or 'Sem descrição cadastrada ainda.')}"
        )
    elif base:
        linhas.append(f"**Base - {base}**\nSem descrição cadastrada ainda.")

    for requisito, skill in sorted((hero.get("evolucoes") or {}).items(), key=lambda item: int(item[0])):
        if isinstance(skill, dict):
            nome = skill.get("nome", "Despertar")
            descricao = skill.get("descricao") or "Sem descrição cadastrada ainda."
        else:
            nome = str(skill)
            descricao = "Sem descrição cadastrada ainda."
        linhas.append(f"**{requisito} estrelas - {nome}**\n{_trim(descricao)}")

    return linhas or ["**Habilidade**\nAinda não cadastrada. TutoriUAU anotou no bloquinho dramático."]


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

        embed.set_footer(
            text=(
                f"✅ Possui • ❌ Não possui | Coleção: {self.obtidos}/{self.total} | "
                f"Página {self.page + 1}/{total_pages}"
            )
        )
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


class HeroProfileCatalogPaginator(discord.ui.View):
    def __init__(self, ctx, classe, heroes, owned_ids):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.classe = classe
        self.heroes = heroes
        self.owned_ids = owned_ids
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "profile_prev":
                    child.disabled = self.page == 0
                elif child.custom_id == "profile_next":
                    child.disabled = self.page >= len(self.heroes) - 1

    def build_payload(self):
        hero_id, hero = self.heroes[self.page]
        classe = _classe_heroi(hero)
        stats = _base_stats(hero)
        nome = hero.get("nome", hero_id)
        origem = hero.get("origem") or hero.get("anime") or "Origem não cadastrada"
        raridade = hero.get("raridade", 1)
        emoji_classe = CLASS_EMOJIS.get(classe, "✨")
        owned = hero_id in self.owned_ids

        embed = discord.Embed(
            title=f"{emoji_classe} {nome}",
            description=(
                f"{'✅ Você possui' if owned else '❌ Você ainda não possui'}\n"
                f"ID do catálogo: `{hero_id}`\n"
                f"Classe: **{CLASS_DISPLAY.get(classe, classe.title())}**\n"
                f"Origem: **{origem}**\n"
                f"Raridade base: **{_estrelas(raridade)}**"
            ),
            color=discord.Color.gold() if owned else discord.Color.blurple(),
        )

        embed.add_field(
            name="Status Base",
            value=(
                f"HP `{stats.get('hp', 0)}` • ATK `{stats.get('atk', 0)}` • MATK `{stats.get('matk', 0)}`\n"
                f"DEF `{stats.get('def', 0)}` • SPD `{stats.get('spd', 0)}%` • CRT `{stats.get('crt', 0)}%`"
            ),
            inline=False,
        )

        for indice, bloco in enumerate(_chunk_lines(_skill_lines(hero)), start=1):
            embed.add_field(
                name="Habilidades" if indice == 1 else f"Habilidades ({indice})",
                value=bloco,
                inline=False,
            )

        image_path = None
        filename = None
        if get_hero_attachment:
            image_path, filename = get_hero_attachment(hero_id, "catalogo")
        hero_file = discord.File(image_path, filename=filename) if image_path and filename else None
        if hero_file:
            embed.set_image(url=f"attachment://{filename}")
        else:
            embed.add_field(
                name="Retrato",
                value="Imagem ainda não encontrada em `assets/herois_img`. TutoriUAU jura que não comeu o JPG.",
                inline=False,
            )

        total = len(self.heroes)
        comentario = TUTOR_PROFILE_COMMENTS[self.page % len(TUTOR_PROFILE_COMMENTS)]
        embed.set_footer(text=f"Página {self.page + 1}/{total} • {comentario}")
        return embed, hero_file

    async def _edit_current_page(self, interaction):
        embed, hero_file = self.build_payload()
        kwargs = {"embed": embed, "view": self, "attachments": [hero_file] if hero_file else []}
        try:
            await interaction.response.edit_message(**kwargs)
        except TypeError:
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, emoji="◀️", custom_id="profile_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Use seu próprio catálogo, fiscal de vitrine.", ephemeral=True)
        self.page -= 1
        self.update_buttons()
        await self._edit_current_page(interaction)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.primary, emoji="▶️", custom_id="profile_next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Use seu próprio catálogo, fiscal de vitrine.", ephemeral=True)
        self.page += 1
        self.update_buttons()
        await self._edit_current_page(interaction)


class Catalogo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_player_heroes(self, user_id):
        try:
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("SELECT hero_id FROM heroes WHERE user_id = ?", (str(user_id),))
            resultados = cursor.fetchall()
            conn.close()
            return {str(r[0]) for r in resultados}
        except sqlite3.Error:
            return set()

    async def _send_profile_catalog(self, ctx, classe):
        classe_real = _classe_real(classe)
        if not classe_real:
            return await ctx.send(
                "❌ Classe inválida. Tente: atacante, mago, suporte, tank, líder, assassino ou atirador."
            )

        catalog_heroes = _catalog_heroes(include_divine=False)
        heroes = [
            (hero_id, hero)
            for hero_id, hero in catalog_heroes.items()
            if _classe_heroi(hero) == classe_real
        ]
        heroes.sort(key=lambda item: (-int(item[1].get("raridade", 1) or 1), item[1].get("nome", item[0])))

        if not heroes:
            return await ctx.send("❌ Nenhum herói encontrado nesta classe.")

        owned_ids = self.get_player_heroes(ctx.author.id)
        view = HeroProfileCatalogPaginator(ctx, classe_real, heroes, owned_ids)
        embed, hero_file = view.build_payload()
        if hero_file:
            await ctx.send(embed=embed, file=hero_file, view=view)
        else:
            await ctx.send(embed=embed, view=view)

    @commands.command(name="catalogoperfil", aliases=["catalogoficha", "galeriaherois", "galeriaheróis"])
    async def catalogo_perfil(self, ctx, classe: str = None):
        if not classe:
            return await ctx.send("Use `echo catalogo perfil <classe>` para abrir a vitrine completa de uma classe.")
        await self._send_profile_catalog(ctx, classe)

    @commands.command(name="catalogo", aliases=["catálogo", "catalog", "personagens"])
    async def catalogo(self, ctx, *args):
        if args and _normalizar_texto(args[0]) in PROFILE_MODES:
            if len(args) < 2:
                return await ctx.send("Use `echo catalogo perfil <classe>` para ver os perfis navegáveis.")
            return await self._send_profile_catalog(ctx, args[1])

        classe = args[0] if args else None
        herois_jogador = self.get_player_heroes(ctx.author.id)
        catalog_heroes = _catalog_heroes(include_divine=True)
        total = len(catalog_heroes)
        obtidos = sum(1 for hero_id in catalog_heroes if hero_id in herois_jogador)
        porcentagem = round((obtidos / total) * 100, 2) if total else 0

        if not classe:
            classes = {}
            for hero in catalog_heroes.values():
                classe_key = _classe_heroi(hero)
                nome = CLASS_DISPLAY.get(classe_key, classe_key.title())
                classes[nome] = classes.get(nome, 0) + 1

            embed = discord.Embed(
                title="📖 Catálogo de Heróis",
                description=(
                    f"✅ Possui | ❌ Não possui\n\n"
                    f"📚 Coleção: **{obtidos}/{total}** ({porcentagem}%)\n\n"
                    f"Use: `echo catalogo [classe]`\n"
                    f"Use: `echo catalogo perfil <classe>` para ver fichas completas navegáveis."
                ),
                color=discord.Color.blue(),
            )
            for nome, qtd in sorted(classes.items()):
                embed.add_field(name=nome, value=f"{qtd} heróis", inline=True)
            embed.set_footer(text="TutoriUAU • Complete sua coleção. Ou pelo menos finja com confiança.")
            return await ctx.send(embed=embed)

        classe_real = _classe_real(classe)
        if not classe_real:
            return await ctx.send(
                "❌ Classe inválida. Tente: atacante, mago, suporte, tank, líder, assassino ou atirador."
            )

        linhas = []
        for hero_id, hero in catalog_heroes.items():
            if _classe_heroi(hero) != classe_real:
                continue

            possui = hero_id in herois_jogador
            emoji = "✅" if possui else "❌"
            nome = "???" if hero.get("secreto") else hero.get("nome", hero_id)
            linhas.append(f"{emoji} **{nome}** {_estrelas(hero.get('raridade', 1))}")

        if not linhas:
            return await ctx.send("❌ Nenhum herói encontrado nesta classe.")

        view = CatalogoPaginator(
            ctx,
            f"📖 Catálogo - {CLASS_DISPLAY.get(classe_real, classe_real.title())}",
            linhas,
            obtidos,
            total,
        )
        await ctx.send(embed=view.generate_embed(), view=view)


async def setup(bot):
    await bot.add_cog(Catalogo(bot))
