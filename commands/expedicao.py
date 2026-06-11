import json
import random
import sqlite3
import time

import discord
from discord.ext import commands

try:
    from data.equipamentos import EQUIPAMENTOS
except Exception:
    EQUIPAMENTOS = {}

try:
    from data.heroes import HEROES
except Exception:
    HEROES = {}

try:
    from utils.player_bonuses import apply_reward_bonuses
    from utils.rewards import average_hero_level, scale_combat_rewards
except Exception:
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0):
        return gold, xp
    def average_hero_level(cursor, user_id, hero_ids=None):
        return 1
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50):
        return gold, xp


ALLOWED_HOURS = {2, 4, 8, 12}
MATERIALS = ["fragmento_dimensional", "poeira_de_mana", "ferro_antigo", "cristal_torto", "mapa_rasgado"]


def add_column_if_missing(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_expedition_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_expeditions(
            user_id TEXT PRIMARY KEY,
            hours INTEGER NOT NULL,
            started_at INTEGER NOT NULL,
            ends_at INTEGER NOT NULL,
            party_power INTEGER DEFAULT 0,
            party_ids TEXT DEFAULT '[]'
        )
    """)
    add_column_if_missing(cursor, "player_expeditions", "party_ids", "TEXT DEFAULT '[]'")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_stats(
            user_id TEXT NOT NULL,
            stat TEXT NOT NULL,
            value INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, stat)
        )
    """)


def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute("INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)", (str(user_id), stat))
    cursor.execute("UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?", (amount, str(user_id), stat))


def add_item(cursor, user_id, item_name, qty=1):
    cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), item_name))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (str(user_id), item_name, qty))


def hero_label(hero_id):
    hero = HEROES.get(hero_id, {})
    return f"{hero.get('emoji', '✨')} {hero.get('nome', hero_id)}"


def selected_party_power(cursor, user_id, hero_db_ids):
    if not hero_db_ids:
        return 0, []
    power = 0
    names = []
    for raw_id in hero_db_ids[:5]:
        cursor.execute("SELECT hero_id, rarity, stars, level FROM heroes WHERE id = ? AND user_id = ?", (int(raw_id), str(user_id)))
        row = cursor.fetchone()
        if not row:
            continue
        hero_id, rarity, stars, level = row
        power += (rarity or 1) * (stars or 1) * ((level or 1) + 12)
        names.append(hero_label(hero_id))
    return int(power), names


class ExpeditionSelect(discord.ui.Select):
    def __init__(self, cog, user_id, hours, heroes):
        self.cog = cog
        self.user_id = user_id
        self.hours = hours
        options = []
        for db_id, hero_id, rarity, level in heroes[:25]:
            options.append(discord.SelectOption(
                label=HEROES.get(hero_id, {}).get("nome", hero_id)[:100],
                value=str(db_id),
                description=f"Lv {level or 1} | {'⭐' * (rarity or 1)}",
                emoji=HEROES.get(hero_id, {}).get("emoji", "✨"),
            ))
        super().__init__(
            placeholder="Escolha até 5 heróis para a expedição...",
            min_values=1,
            max_values=min(5, len(options)),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Essa expedição não é sua. TutoriUAU viu a mão boba.", ephemeral=True)
        await self.cog._start_selected(interaction, self.hours, self.values)


class ExpeditionPartyView(discord.ui.View):
    def __init__(self, cog, user, hours, heroes):
        super().__init__(timeout=180)
        self.user = user
        if heroes:
            self.add_item(ExpeditionSelect(cog, user.id, hours, heroes))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Abra sua própria expedição. O seguro não cobre carona interdimensional.", ephemeral=True)
            return False
        return True


class Expedicao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_expedition_db(cursor)
        conn.commit()
        conn.close()

    def _available_heroes(self, cursor, user_id):
        cursor.execute("""
            SELECT id, hero_id, rarity, level
            FROM heroes
            WHERE user_id = ?
            ORDER BY level DESC, rarity DESC, id ASC
            LIMIT 25
        """, (str(user_id),))
        return cursor.fetchall()

    async def _claim(self, ctx, row):
        user_id = str(ctx.author.id)
        hours, _, _, power = row[:4]
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_expedition_db(cursor)
        base_gold = int(hours * random.randint(260, 440) + power * hours * random.uniform(0.25, 0.45))
        base_xp = int(hours * random.randint(80, 150) + power * hours * 0.08)
        party_ids = json.loads(row[4] or "[]") if len(row) > 4 else []
        average_level = average_hero_level(cursor, user_id, party_ids)
        base_gold, base_xp = scale_combat_rewards(
            base_gold,
            base_xp,
            average_level,
        )
        gold, xp = apply_reward_bonuses(cursor, user_id, base_gold, base_xp)
        gems = random.randint(0, max(1, hours // 2))
        item_count = 1 + hours // 4
        found_items = []
        for _ in range(item_count):
            item = random.choice(MATERIALS)
            qty = random.randint(1, 2 + hours // 4)
            add_item(cursor, user_id, item, qty)
            found_items.append(f"{qty}x {item.replace('_', ' ').title()}")

        equipment_pool = [eq_id for eq_id in EQUIPAMENTOS.keys() if eq_id != "id-nome"]
        if equipment_pool and random.random() < 0.20 + (hours * 0.03):
            eq_id = random.choice(equipment_pool)
            add_item(cursor, user_id, eq_id, 1)
            found_items.append(f"1x {EQUIPAMENTOS.get(eq_id, {}).get('nome', eq_id)}")

        cursor.execute("UPDATE players SET gold = gold + ?, gems = gems + ?, xp = xp + ? WHERE user_id = ?", (gold, gems, xp, user_id))
        cursor.execute("DELETE FROM player_expeditions WHERE user_id = ?", (user_id,))
        add_stat(cursor, user_id, "expeditions_done", 1)
        add_stat(cursor, user_id, "expedition_hours", hours)
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="Expedição Concluída",
            description=f"Sua equipe voltou depois de **{hours}h**. TutoriUAU conferiu: trouxeram loot e poucas explicações.",
            color=discord.Color.green(),
        )
        embed.add_field(name="Recompensas", value=f"+{gold:,} Gold\n+{xp:,} XP\n+{gems:,} Gems", inline=True)
        embed.add_field(name="Itens e materiais", value="\n".join(found_items) if found_items else "Nada. Só histórias longas.", inline=True)
        return await ctx.send(embed=embed)

    async def _start_selected(self, interaction, hours, hero_db_ids):
        user_id = str(interaction.user.id)
        now = int(time.time())
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_expedition_db(cursor)
        cursor.execute("SELECT user_id FROM player_expeditions WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            return await interaction.response.send_message("Você já tem uma expedição em andamento.", ephemeral=True)
        power, names = selected_party_power(cursor, user_id, hero_db_ids)
        if power <= 0:
            conn.close()
            return await interaction.response.send_message("Seleção inválida. Esses heróis não estão na sua conta.", ephemeral=True)
        ends_at = now + hours * 3600
        cursor.execute(
            "INSERT INTO player_expeditions (user_id, hours, started_at, ends_at, party_power, party_ids) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, hours, now, ends_at, power, json.dumps([str(x) for x in hero_db_ids[:5]])),
        )
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="Expedição Iniciada",
            description=f"Duração: **{hours}h**\nRetorno: <t:{ends_at}:R>\nPoder enviado: **{power:,}**",
            color=discord.Color.dark_green(),
        )
        embed.add_field(name="Equipe enviada", value="\n".join(names), inline=False)
        embed.set_footer(text="TutoriUAU: mandei lanche, mapa e uma recomendação para não tocar em objeto brilhante.")
        await interaction.response.edit_message(embed=embed, view=None)

    @commands.command(name="expedicao", aliases=["expedição", "expedicoes", "expedições"])
    async def expedicao_cmd(self, ctx, duracao: str = None):
        user_id = str(ctx.author.id)
        now = int(time.time())
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_expedition_db(cursor)
        cursor.execute("SELECT hours, started_at, ends_at, party_power, party_ids FROM player_expeditions WHERE user_id = ?", (user_id,))
        active = cursor.fetchone()

        if active:
            if now >= active[2] or (duracao or "").lower() in ["coletar", "resgatar", "claim"]:
                conn.close()
                return await self._claim(ctx, active)
            conn.close()
            return await ctx.send(
                f"Sua equipe ainda está em expedição de **{active[0]}h**. Volta <t:{active[2]}:R>.\n"
                "TutoriUAU: ficar olhando o portal não acelera a viagem."
            )

        try:
            hours = int(duracao or 0)
        except ValueError:
            hours = 0
        if hours not in ALLOWED_HOURS:
            conn.close()
            return await ctx.send("Use `echo expedicao 2`, `4`, `8` ou `12`.")

        heroes = self._available_heroes(cursor, user_id)
        conn.close()
        if not heroes:
            return await ctx.send("Você precisa ter heróis para mandar em expedição. O vazio não busca loot.")
        embed = discord.Embed(
            title=f"Selecionar Equipe da Expedição - {hours}h",
            description="Escolha de 1 a 5 heróis. Mais poder aumenta as recompensas e reduz a chance de voltarem só com poeira.",
            color=discord.Color.dark_green(),
        )
        await ctx.send(embed=embed, view=ExpeditionPartyView(self, ctx.author, hours, heroes))


async def setup(bot):
    await bot.add_cog(Expedicao(bot))
