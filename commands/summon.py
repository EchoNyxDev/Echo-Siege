import os
import random
import sqlite3
import sys

import discord
from discord import app_commands
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.banners import get_banner, get_common_banner, get_special_banner
    from utils.hero_images import get_hero_attachment
except ModuleNotFoundError:
    HEROES = {"id-fallback": {"nome": "Bug de Sistema", "emoji": "?", "raridade": 1, "imagem": ""}}

    def get_common_banner(heroes, today=None):
        return {"type": "comum", "name": "Banner Comum", "period_label": "permanente", "featured_5": [], "featured_4": [], "featured_5_rate": 0, "featured_4_rate": 0}

    def get_special_banner(heroes, today=None):
        return get_common_banner(heroes, today)

    def get_banner(heroes, banner_type="comum", today=None):
        return get_common_banner(heroes, today)

    def get_hero_attachment(hero_id, prefix="hero"):
        return None, None


CUSTO_SUMMON = 1000
HERO_POOL = {1: [], 2: [], 3: [], 4: [], 5: []}
DIVINE_POOL = []
BASE_RATES = {1: 50.0, 2: 25.0, 3: 19.0, 4: 5.0, 5: 1.0}
DIVINE_RATE_PERCENT = 0.01
SOFT_PITY_STEP_4 = 0.5
SOFT_PITY_STEP_5 = 0.05

DIVINE_ANNOUNCEMENT_ROLE_ID = 1515443815362854963

for hero_id, data in HEROES.items():
    if hero_id == "id-nome":
        continue
    rarity = data.get("raridade", 1)
    if data.get("divino") or rarity >= 7:
        DIVINE_POOL.append(hero_id)
        continue
    if rarity in HERO_POOL:
        HERO_POOL[rarity].append(hero_id)


SHOP_CONFIGS = {
    1: {"name": "Loja 1", "rates": BASE_RATES, "pity_4": 15, "hard_pity_4": 30, "pity_5": 30, "hard_pity_5": 100},
    2: {"name": "Loja 2", "rates": BASE_RATES, "pity_4": 15, "hard_pity_4": 30, "pity_5": 30, "hard_pity_5": 100},
    3: {"name": "Loja 3", "rates": BASE_RATES, "pity_4": 15, "hard_pity_4": 30, "pity_5": 30, "hard_pity_5": 100},
    4: {"name": "Lugnica Dourada", "rates": BASE_RATES, "pity_4": 15, "hard_pity_4": 30, "pity_5": 30, "hard_pity_5": 100},
}


def normalize_banner_type(value):
    value = str(value or "comum").lower()
    if value in ["especial", "special", "semanal", "weekly", "destaque"]:
        return "especial"
    return "comum"


class Summon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _effective_config(self, shop_level, banner_type):
        config = SHOP_CONFIGS.get(shop_level, SHOP_CONFIGS[1])
        return {**config, "rates": dict(config["rates"])}

    def _local_hero_file(self, hero_id, prefix="summon"):
        path, filename = get_hero_attachment(hero_id, prefix)
        return discord.File(path, filename=filename) if path else None

    def _sortear_raridade(self, config, pity_4, pity_5):
        if DIVINE_POOL and random.uniform(0, 100) < DIVINE_RATE_PERCENT:
            return 7
        if pity_5 >= config["hard_pity_5"]:
            return 5
        if pity_4 >= config["hard_pity_4"]:
            return 4

        rates = config["rates"]
        chance_5 = rates[5]
        chance_4 = rates[4]
        if pity_5 >= config["pity_5"]:
            chance_5 += (pity_5 - config["pity_5"] + 1) * SOFT_PITY_STEP_5
        if pity_4 >= config["pity_4"]:
            chance_4 += (pity_4 - config["pity_4"] + 1) * SOFT_PITY_STEP_4

        roll = random.uniform(0, 100)
        if roll < chance_5:
            return 5
        if roll < chance_5 + chance_4:
            return 4

        lower_roll = random.uniform(0, rates[1] + rates[2] + rates[3])
        if lower_roll < rates[1]:
            return 1
        if lower_roll < rates[1] + rates[2]:
            return 2
        return 3

    def _sortear_heroi(self, rarity, banner):
        if rarity == 7 and DIVINE_POOL:
            return random.choice(DIVINE_POOL)
        if banner["type"] == "especial":
            if rarity == 5 and banner["featured_5"] and random.random() <= banner["featured_5_rate"]:
                return random.choice(banner["featured_5"])
            if rarity == 4 and banner["featured_4"] and random.random() <= banner["featured_4_rate"]:
                return random.choice(banner["featured_4"])

        if HERO_POOL.get(rarity):
            return random.choice(HERO_POOL[rarity])
        return next(iter(HEROES.keys()), "erro")

    def _format_featured(self, ids):
        if not ids:
            return "Nenhum destaque disponível. O vazio olhou de volta."
        lines = []
        for hero_id in ids:
            hero = HEROES.get(hero_id, {})
            lines.append(f"{hero.get('emoji', '?')} **{hero.get('nome', hero_id)}**")
        return "\n".join(lines)

    def _single_banner_embed(self, banner):
        source_label = {
            "manual": "Curadoria administrativa",
            "automatic": "Seleção automática diversificada",
            "permanent": "Banner permanente",
        }.get(banner.get("source"), "Seleção especial")
        embed = discord.Embed(
            title=f"{banner['name']} ({banner['type']})",
            description=(
                f"{banner.get('description', '')}\n\n"
                f"Origem: **{source_label}**\n"
                f"Período: **{banner['period_label']}**"
            ),
            color=discord.Color.gold() if banner["type"] == "comum" else discord.Color.magenta(),
        )
        if banner["type"] == "especial":
            embed.add_field(
                name="Destaques 5 estrelas",
                value=f"{self._format_featured(banner['featured_5'])}\nChance entre os 5⭐ sorteados: **{int(banner['featured_5_rate'] * 100)}%**",
                inline=False,
            )
            embed.add_field(
                name="Destaques 4 estrelas",
                value=f"{self._format_featured(banner['featured_4'])}\nChance entre os 4⭐ sorteados: **{int(banner['featured_4_rate'] * 100)}%**",
                inline=False,
            )
        else:
            embed.add_field(
                name="Como funciona",
                value="O banner comum usa todos os personagens do catálogo, sem destaque. Frio, democrático e levemente cruel.",
                inline=False,
            )
        embed.add_field(
            name="Taxas base",
            value="1⭐ 50% | 2⭐ 25% | 3⭐ 19% | 4⭐ 5% | 5⭐ 1%\nDivino: 0,01% e nunca entra em destaque.",
            inline=False,
        )
        embed.set_footer(text="TutoriUAU • Um giro de 10 garante pelo menos um herói 3⭐ ou superior.")
        return embed

    def banner_embed(self, banner_type=None):
        if banner_type:
            return self._single_banner_embed(get_banner(HEROES, banner_type))

        common = get_common_banner(HEROES)
        special = get_special_banner(HEROES)
        special_source = (
            "selecionado pela administração"
            if special.get("source") == "manual"
            else "gerado automaticamente com classes diversificadas"
        )
        embed = discord.Embed(
            title="Banners de Lugnica",
            description="Tem o banner comum e tem o especial ativo. A diferença? Um é esperança comum, o outro é esperança com glitter.",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Comum", value=f"**{common['name']}** - todos os personagens.\nUse `echo summon <quantidade>`.", inline=False)
        embed.add_field(
            name="Especial Ativo",
            value=(
                f"**{special['name']}** - {special['period_label']}\n"
                f"Banner {special_source}.\n"
                f"3 destaques 5⭐ e 5 destaques 4⭐ com chance aumentada dentro da mesma raridade.\n"
                "Use `echo banner especial` ou `echo summon especial <quantidade>`."
            ),
            inline=False,
        )
        return embed

    def banner_payload(self, banner_type=None):
        normalized_type = normalize_banner_type(banner_type) if banner_type else None
        embed = self.banner_embed(normalized_type)
        banner = (
            get_banner(HEROES, normalized_type)
            if normalized_type
            else get_special_banner(HEROES)
        )
        featured = banner.get("featured_5") or banner.get("featured_4") or []
        hero_file = self._local_hero_file(featured[0], prefix="banner") if featured else None
        if hero_file:
            embed.set_image(url=f"attachment://{hero_file.filename}")
        return embed, hero_file

    async def process_summon(self, user: discord.User, amount: int, banner_type="comum"):
        banner_type = normalize_banner_type(banner_type)
        if amount <= 0:
            return "Use pelo menos 1 summon. Zero summons é só você encarando o vazio."
        if amount > 10:
            return "O limite por vez é 10 summons. O Discord tem limites. Diferente da sua vontade de gastar."

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT summon_tickets, shop_level, pity_4, pity_5 FROM summon_data WHERE user_id = ?",
            (str(user.id),),
        )
        summon_data = cursor.fetchone()
        if not summon_data:
            conn.close()
            return f"{user.mention}, use `echo iniciar` antes de invocar."

        tickets, shop_level, pity_4, pity_5 = summon_data
        tickets_usados = min(amount, tickets)
        paid_summons = amount - tickets_usados
        total_custo = CUSTO_SUMMON * paid_summons

        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (str(user.id),))
        player_data = cursor.fetchone()
        if not player_data:
            conn.close()
            return f"{user.mention}, use `echo iniciar` primeiro."

        gold_atual = player_data[0] or 0
        if gold_atual < total_custo:
            conn.close()
            return f"Ouro insuficiente. Você precisa de **{total_custo:,} Gold** e tem **{gold_atual:,} Gold**."

        config = self._effective_config(shop_level, banner_type)
        banner = get_banner(HEROES, banner_type)
        resultados = []
        stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 7: 0}
        cursor.execute("SELECT DISTINCT hero_id FROM heroes WHERE user_id = ?", (str(user.id),))
        owned_heroes = {row[0] for row in cursor.fetchall()}

        for pull_index in range(amount):
            pity_4 += 1
            pity_5 += 1
            guarantee_3_plus = (
                amount == 10
                and pull_index == amount - 1
                and not any(result["raridade"] >= 3 for result in resultados)
            )
            rarity = self._sortear_raridade(config, pity_4, pity_5)
            if guarantee_3_plus and rarity < 3:
                rarity = 3

            if rarity >= 5:
                pity_5 = 0
                pity_4 = 0
            elif rarity == 4:
                pity_4 = 0

            hero_id = self._sortear_heroi(rarity, banner)
            is_new = hero_id not in owned_heroes
            resultados.append({"hero_id": hero_id, "raridade": rarity, "is_new": is_new})
            owned_heroes.add(hero_id)
            stats[rarity] += 1

        if total_custo > 0:
            cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (total_custo, str(user.id)))

        for item in resultados:
            cursor.execute(
                """
                INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp)
                VALUES (?, ?, ?, 1, 1, 0)
                """,
                (str(user.id), item["hero_id"], item["raridade"]),
            )

        cursor.execute(
            """
            UPDATE summon_data
            SET summon_tickets = summon_tickets - ?,
                pity_4 = ?,
                pity_5 = ?,
                total_summons = total_summons + ?,
                total_1_star = total_1_star + ?,
                total_2_star = total_2_star + ?,
                total_3_star = total_3_star + ?,
                total_4_star = total_4_star + ?,
                total_5_star = total_5_star + ?,
                total_divine = COALESCE(total_divine, 0) + ?
            WHERE user_id = ?
            """,
            (
                tickets_usados,
                pity_4,
                pity_5,
                amount,
                stats[1],
                stats[2],
                stats[3],
                stats[4],
                stats[5],
                stats[7],
                str(user.id),
            ),
        )
        conn.commit()
        conn.close()

        rarest = max(resultados, key=lambda r: r["raridade"])
        spent = []
        if tickets_usados:
            spent.append(f"{tickets_usados} Ticket(s)")
        if total_custo:
            spent.append(f"{total_custo:,} Gold")
        if not spent:
            spent.append("nada, e isso é suspeito")

        embed = discord.Embed(
            title=f"Summon de Lugnica - {banner['name']}",
            description=f"{user.mention} usou **{' e '.join(spent)}**.\nBanner: **{banner['type']}**\n\n",
            color=discord.Color.magenta() if banner_type == "especial" else discord.Color.gold(),
        )

        hero_file = self._local_hero_file(rarest["hero_id"])
        if hero_file:
            embed.set_image(url=f"attachment://{hero_file.filename}")

        featured_ids = set(banner.get("featured_5", []) + banner.get("featured_4", []))
        for resultado in resultados:
            hero = HEROES.get(resultado["hero_id"], {})
            nome = hero.get("nome", "Herói Desconhecido")
            emoji = hero.get("emoji", "?")
            stars = "⭐" * resultado["raridade"]
            featured = " [DESTAQUE]" if resultado["hero_id"] in featured_ids else ""
            new_label = " [NEW]" if resultado.get("is_new") else ""
            line = f"{stars} | {emoji} {nome}{featured}{new_label}"
            embed.description += f"**{line}**\n" if resultado["raridade"] >= 4 else f"{line}\n"

        embed.set_footer(
            text=(
                f"Pity 4⭐: {pity_4}/{config['hard_pity_4']} (soft {config['pity_4']}) | "
                f"Pity 5⭐: {pity_5}/{config['hard_pity_5']} (soft {config['pity_5']})"
            )
        )
        divine_results = [result for result in resultados if result["raridade"] >= 7]
        return embed, hero_file, divine_results

    def _divine_announcement(self, user, result):
        hero = HEROES.get(result["hero_id"], {})
        role_mention = (
            f"<@&{DIVINE_ANNOUNCEMENT_ROLE_ID}> "
            if DIVINE_ANNOUNCEMENT_ROLE_ID
            else ""
        )
        embed = discord.Embed(
            title="🌌 UM SER DIVINO DESCEU",
            description=(
                f"{user.mention} rompeu as probabilidades e encontrou "
                f"**{hero.get('nome', 'um ser desconhecido')}**.\n\n"
                "TutoriUAU: 0,01%. Eu conferi duas vezes porque também achei ofensivo."
            ),
            color=discord.Color.from_rgb(255, 215, 80),
        )
        hero_file = self._local_hero_file(result["hero_id"], prefix="divino")
        if hero_file:
            embed.set_image(url=f"attachment://{hero_file.filename}")
        return role_mention, embed, hero_file

    async def _send_divine_announcements(self, sender, user, results):
        for result in results:
            content, embed, hero_file = self._divine_announcement(user, result)
            kwargs = {
                "content": content or None,
                "embed": embed,
                "allowed_mentions": discord.AllowedMentions(roles=True, users=True),
            }
            if hero_file:
                kwargs["file"] = hero_file
            await sender(**kwargs)

    def _parse_prefix_args(self, args):
        banner_type = "comum"
        amount = 1
        for arg in args:
            lowered = str(arg).lower()
            if lowered.isdigit():
                amount = int(lowered)
            elif lowered in ["especial", "special", "semanal", "weekly", "destaque", "comum"]:
                banner_type = normalize_banner_type(lowered)
        return amount, banner_type

    @commands.command(name="summon")
    async def summon_prefix(self, ctx, *args):
        amount, banner_type = self._parse_prefix_args(args)
        resposta = await self.process_summon(ctx.author, amount, banner_type)
        if isinstance(resposta, tuple):
            embed, hero_file, divine_results = resposta
            if hero_file:
                await ctx.send(embed=embed, file=hero_file)
            else:
                await ctx.send(embed=embed)
            await self._send_divine_announcements(ctx.send, ctx.author, divine_results)
        elif isinstance(resposta, discord.Embed):
            await ctx.send(embed=resposta)
        else:
            await ctx.send(resposta)

    @commands.command(name="banner", aliases=["banners", "destaque"])
    async def banner_prefix(self, ctx, tipo: str = None):
        embed, hero_file = self.banner_payload(tipo)
        if hero_file:
            await ctx.send(embed=embed, file=hero_file)
        else:
            await ctx.send(embed=embed)

    @app_commands.command(name="summon", description="Invoca heróis no banner comum ou especial.")
    @app_commands.describe(quantidade="Quantos heróis deseja invocar? Máximo 10.", banner="comum ou especial")
    @app_commands.choices(
        banner=[
            app_commands.Choice(name="Comum", value="comum"),
            app_commands.Choice(name="Especial ativo", value="especial"),
        ]
    )
    async def summon_slash(self, interaction: discord.Interaction, quantidade: int = 1, banner: str = "comum"):
        resposta = await self.process_summon(interaction.user, quantidade, banner)
        if isinstance(resposta, tuple):
            embed, hero_file, divine_results = resposta
            if hero_file:
                await interaction.response.send_message(embed=embed, file=hero_file)
            else:
                await interaction.response.send_message(embed=embed)
            await self._send_divine_announcements(
                interaction.followup.send,
                interaction.user,
                divine_results,
            )
        elif isinstance(resposta, discord.Embed):
            await interaction.response.send_message(embed=resposta)
        else:
            await interaction.response.send_message(resposta)

    @app_commands.command(name="banner", description="Mostra os banners atuais.")
    @app_commands.describe(tipo="comum ou especial")
    @app_commands.choices(
        tipo=[
            app_commands.Choice(name="Todos", value="todos"),
            app_commands.Choice(name="Comum", value="comum"),
            app_commands.Choice(name="Especial ativo", value="especial"),
        ]
    )
    async def banner_slash(self, interaction: discord.Interaction, tipo: str = "todos"):
        embed, hero_file = self.banner_payload(None if tipo == "todos" else tipo)
        if hero_file:
            await interaction.response.send_message(embed=embed, file=hero_file)
        else:
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Summon(bot))
