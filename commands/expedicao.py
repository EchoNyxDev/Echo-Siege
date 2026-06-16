import json
import random
import sqlite3
import time
import os
import sys

import discord
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.equipamentos import EQUIPAMENTOS
    from data.heroes import HEROES
    from utils.gold_system import conceder_ouro_escalavel
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
    from utils.player_bonuses import apply_reward_bonuses
    from utils.rewards import average_hero_level, scale_combat_rewards
except Exception:
    EQUIPAMENTOS = {}
    HEROES = {}
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0): return gold, xp
    def average_hero_level(cursor, user_id, hero_ids=None): return 1
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50): return gold, xp
    def conceder_ouro_escalavel(*args, **kwargs): return 0
    def dar_xp_jogador(*args): return 0, 1
    def dar_xp_heroi(*args): return 0, 1


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
            placeholder="Convocar até 5 heróis para a jornada...",
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
        guild_id = str(ctx.guild.id) if ctx.guild else None
        
        hours, _, _, power = row[:4]
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_expedition_db(cursor)
        
        party_ids = json.loads(row[4] or "[]") if len(row) > 4 else []
        average_level = average_hero_level(cursor, user_id, party_ids)
        
        # Base de loot com base nas horas
        base_gold = int(hours * random.randint(260, 440) + power * hours * random.uniform(0.25, 0.45))
        base_xp = int(hours * random.randint(80, 150) + power * hours * 0.08)
        
        # Passando Ouro pelo Motor Central
        gold_ganho = conceder_ouro_escalavel(cursor, user_id, base_gold, average_level, guild_id, extra_mult=1.0)
        
        # Scaling de XP
        _, xp_ganho = scale_combat_rewards(0, base_xp, average_level)
        _, xp_ganho = apply_reward_bonuses(cursor, user_id, 0, xp_ganho)
        
        gems = random.randint(0, max(1, hours // 2))
        
        item_count = 1 + hours // 4
        found_items = []
        for _ in range(item_count):
            item = random.choice(MATERIALS)
            qty = random.randint(1, 2 + hours // 4)
            add_item(cursor, user_id, item, qty)
            found_items.append(f"📦 {qty}x {item.replace('_', ' ').title()}")

        equipment_pool = [eq_id for eq_id in EQUIPAMENTOS.keys() if eq_id != "id-nome"]
        if equipment_pool and random.random() < 0.20 + (hours * 0.03):
            eq_id = random.choice(equipment_pool)
            add_item(cursor, user_id, eq_id, 1)
            found_items.append(f"✨ 1x {EQUIPAMENTOS.get(eq_id, {}).get('nome', eq_id)}")

        # Distribuir XP para conta e heróis
        log_ups = ""
        ups_p, lvl_p = dar_xp_jogador(cursor, user_id, xp_ganho)
        if ups_p > 0: log_ups += f"🆙 **Sua Conta** subiu para o Nível {lvl_p}!\n"

        for hid in party_ids:
            ups, novo_lvl = dar_xp_heroi(cursor, int(hid), xp_ganho)
            if ups > 0:
                cursor.execute("SELECT hero_id FROM heroes WHERE id = ?", (int(hid),))
                h_row = cursor.fetchone()
                if h_row:
                    nome_heroi = HEROES.get(h_row[0], {}).get("nome", "Herói")
                    log_ups += f"🌟 **{nome_heroi.split(' (')[0]}** subiu para o Nível {novo_lvl}!\n"

        cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (gems, user_id))
        cursor.execute("DELETE FROM player_expeditions WHERE user_id = ?", (user_id,))
        
        add_stat(cursor, user_id, "expeditions_done", 1)
        add_stat(cursor, user_id, "expedition_hours", hours)
        
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🏕️ Expedição Concluída",
            description=f"Sua equipe retornou de uma exaustiva jornada de **{hours}h**.\nTutoriUAU: *'Milagre. Eu apostei que iam ser engolidos pela floresta.'*",
            color=discord.Color.green(),
        )
        embed.add_field(name="Recompensas", value=f"💰 **Ouro:** {gold_ganho:,}\n⭐ **XP:** {xp_ganho:,}\n💎 **Gemas:** {gems:,}", inline=True)
        embed.add_field(name="Itens e Espólios", value="\n".join(found_items) if found_items else "Nada de útil. Só terra nas botas.", inline=True)
        
        if log_ups:
            embed.add_field(name="Level Up!", value=log_ups, inline=False)
            
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
            title="🗺️ Expedição Iniciada",
            description=f"Duração planejada: **{hours}h**\nRetorno estimado: <t:{ends_at}:R>\nPoder da Patrulha: **{power:,}**\n\n*(Quanto maior o poder, maiores as chances de saque extra)*",
            color=discord.Color.dark_green(),
        )
        embed.add_field(name="Membros da Patrulha", value="\n".join(names), inline=False)
        embed.set_footer(text="TutoriUAU: Dei-lhes mapa, bússola e disse para não tocarem em objetos brilhantes e amaldiçoados.")
        await interaction.response.edit_message(embed=embed, view=None)

    @commands.command(name="expedicao", aliases=["expedição", "expedicoes", "expedições", "exp"])
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
                res = await self._claim(ctx, active)
                conn.close()
                return res
            conn.close()
            return await ctx.send(
                f"⏳ A sua equipa ainda está a explorar as terras selvagens numa expedição de **{active[0]}h**.\n"
                f"Retorno previsto: <t:{active[2]}:R>.\n\n"
                "TutoriUAU: *'Ficar a olhar para o portal de teletransporte não os fará andar mais rápido.'*"
            )

        try:
            hours = int(duracao or 0)
        except ValueError:
            hours = 0
            
        if hours not in ALLOWED_HOURS:
            conn.close()
            return await ctx.send("🧭 Para iniciar uma expedição, use: `echo expedicao 2`, `4`, `8` ou `12` (horas).")

        heroes = self._available_heroes(cursor, user_id)
        conn.close()
        
        if not heroes:
            return await ctx.send("❌ Precisas de ter heróis vivos para mandar em expedição. O teu fantasma não carrega loot.")
            
        embed = discord.Embed(
            title=f"🏕️ Seleção de Expedição - {hours}h",
            description="Escolha de 1 a 5 heróis abaixo. Enviar heróis mais fortes aumenta drasticamente a qualidade e quantidade do saque trazido das ruínas.",
            color=discord.Color.dark_green(),
        )
        await ctx.send(embed=embed, view=ExpeditionPartyView(self, ctx.author, hours, heroes))

async def setup(bot):
    await bot.add_cog(Expedicao(bot))