import random
import sqlite3
import time

import discord
from discord.ext import commands

try:
    from utils.player_bonuses import apply_reward_bonuses
    from utils.rewards import scale_combat_rewards
except Exception:
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0):
        return gold, xp
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50):
        return gold, xp


ROOM_TYPES = ["monstro", "tesouro", "mercador", "armadilha", "evento"]
MATERIALS = ["pedra_do_labirinto", "fio_de_mana", "chave_torta", "moeda_antiga", "gema_opaca"]
LABYRINTH_COOLDOWN = 300


def add_column_if_missing(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_labyrinth_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_labyrinth(
            user_id TEXT PRIMARY KEY,
            depth INTEGER DEFAULT 0,
            hp INTEGER DEFAULT 100,
            loot_gold INTEGER DEFAULT 0,
            loot_gems INTEGER DEFAULT 0,
            started_at INTEGER DEFAULT 0,
            last_action INTEGER DEFAULT 0
        )
    """)
    add_column_if_missing(cursor, "player_labyrinth", "last_action", "INTEGER DEFAULT 0")
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


def party_power(cursor, user_id):
    cursor.execute("""
        SELECT rarity, stars, level
        FROM heroes
        WHERE user_id = ?
        ORDER BY level DESC, rarity DESC
        LIMIT 5
    """, (str(user_id),))
    rows = cursor.fetchall()
    return sum((rarity or 1) * (stars or 1) * ((level or 1) + 10) for rarity, stars, level in rows)


class Labirinto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_labyrinth_db(cursor)
        conn.commit()
        conn.close()

    @commands.command(name="labirinto", aliases=["maze"])
    async def labirinto_cmd(self, ctx, acao: str = None):
        user_id = str(ctx.author.id)
        acao = (acao or "avancar").lower()
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_labyrinth_db(cursor)
        power = party_power(cursor, user_id)
        if power <= 0:
            conn.close()
            return await ctx.send("Você precisa de uma party para entrar no labirinto. O TutoriUAU não deixa figurante virar estatística.")

        cursor.execute("SELECT depth, hp, loot_gold, loot_gems, last_action FROM player_labyrinth WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO player_labyrinth (user_id, depth, hp, loot_gold, loot_gems, started_at, last_action) VALUES (?, 0, 100, 0, 0, ?, 0)", (user_id, int(time.time())))
            row = (0, 100, 0, 0, 0)

        depth, hp, loot_gold, loot_gems, last_action = row
        if acao in ["sair", "coletar", "fugir"]:
            gold, _ = apply_reward_bonuses(cursor, user_id, loot_gold, 0)
            cursor.execute("UPDATE players SET gold = gold + ?, gems = gems + ? WHERE user_id = ?", (gold, loot_gems, user_id))
            cursor.execute("DELETE FROM player_labyrinth WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return await ctx.send(f"Você saiu do labirinto com **{gold:,} Gold** e **{loot_gems:,} Gems**. TutoriUAU: fugir com lucro chama estratégia.")

        if last_action and int(time.time()) - int(last_action or 0) < LABYRINTH_COOLDOWN:
            ready_at = int(last_action) + LABYRINTH_COOLDOWN
            conn.close()
            return await ctx.send(f"O labirinto muda de posição de novo <t:{ready_at}:R>. TutoriUAU: até parede aleatória tem agenda.")

        depth += 1
        room = "boss" if depth % 5 == 0 else random.choices(ROOM_TYPES, weights=[38, 22, 12, 16, 12], k=1)[0]
        difficulty = 90 + depth * 45
        title = f"Labirinto - Sala {depth}"
        desc = ""
        item_line = ""

        if room == "monstro":
            chance = power / max(1, power + difficulty)
            if random.random() < chance:
                gain = random.randint(180, 360) + depth * 55
                gain, _ = scale_combat_rewards(gain, 0, depth, reference=25)
                loot_gold += gain
                desc = f"Monstro derrotado. +{gain:,} Gold acumulado."
            else:
                damage = random.randint(12, 28) + depth // 2
                hp -= damage
                desc = f"O monstro bateu primeiro. HP do grupo: **{max(0, hp)}/100**."
        elif room == "tesouro":
            gain = random.randint(250, 600) + depth * 40
            gain, _ = scale_combat_rewards(gain, 0, depth, reference=25)
            gems = 1 if random.random() < 0.35 else 0
            loot_gold += gain
            loot_gems += gems
            item = random.choice(MATERIALS)
            add_item(cursor, user_id, item, 1)
            item_line = f"Item encontrado: **{item.replace('_', ' ').title()}**."
            desc = f"Tesouro aberto. +{gain:,} Gold acumulado e +{gems} Gem."
        elif room == "mercador":
            cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
            gold_now = (cursor.fetchone() or [0])[0] or 0
            if gold_now >= 300:
                cursor.execute("UPDATE players SET gold = gold - 300 WHERE user_id = ?", (user_id,))
                loot_gems += 2
                desc = "Mercador suspeito vendeu 2 Gems por 300 Gold. Barganha? Crime? Ambos?"
            else:
                desc = "Mercador apareceu, viu sua carteira e foi embora em silêncio. Humilhante."
        elif room == "armadilha":
            damage = random.randint(8, 24) + depth
            hp -= damage
            desc = f"Armadilha ativada. HP do grupo: **{max(0, hp)}/100**. TutoriUAU: placas de 'não pise' existem por motivo."
        elif room == "evento":
            roll = random.choice(["heal", "gold", "gems"])
            if roll == "heal":
                hp = min(100, hp + 25)
                desc = "Fonte estranha curou a party em 25 HP. Beber líquido brilhante: aprovado desta vez."
            elif roll == "gold":
                gain = random.randint(150, 500)
                gain, _ = scale_combat_rewards(gain, 0, depth, reference=25)
                loot_gold += gain
                desc = f"Evento aleatório rendeu +{gain:,} Gold acumulado."
            else:
                loot_gems += 1
                desc = "Evento aleatório rendeu +1 Gem. O labirinto piscou para você, estranho."
        else:
            boss_power = difficulty * 1.35
            if power * random.uniform(0.85, 1.25) >= boss_power:
                gain = random.randint(900, 1600) + depth * 120
                gain, _ = scale_combat_rewards(gain, 0, depth, reference=25)
                loot_gold += gain
                loot_gems += 3
                add_stat(cursor, user_id, "labyrinth_bosses", 1)
                desc = f"Boss derrotado! +{gain:,} Gold e +3 Gems acumulados."
            else:
                hp -= random.randint(28, 48)
                desc = f"Boss venceu a troca. HP do grupo: **{max(0, hp)}/100**."

        add_stat(cursor, user_id, "labyrinth_rooms", 1)
        if hp <= 0:
            safe_gold = int(loot_gold * 0.25)
            safe_gems = int(loot_gems * 0.25)
            cursor.execute("UPDATE players SET gold = gold + ?, gems = gems + ? WHERE user_id = ?", (safe_gold, safe_gems, user_id))
            cursor.execute("DELETE FROM player_labyrinth WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return await ctx.send(f"Party caiu no labirinto. Você salvou só **{safe_gold:,} Gold** e **{safe_gems} Gems**. TutoriUAU: morrer é ruim para o lucro, anotem.")

        cursor.execute("UPDATE player_labyrinth SET depth = ?, hp = ?, loot_gold = ?, loot_gems = ?, last_action = ? WHERE user_id = ?", (depth, hp, loot_gold, loot_gems, int(time.time()), user_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(title=title, description=desc, color=discord.Color.dark_purple())
        embed.add_field(name="Tipo de sala", value=room.title(), inline=True)
        embed.add_field(name="HP da party", value=f"{hp}/100", inline=True)
        embed.add_field(name="Loot acumulado", value=f"{loot_gold:,} Gold\n{loot_gems} Gems", inline=True)
        if item_line:
            embed.add_field(name="Achado", value=item_line, inline=False)
        embed.set_footer(text="Use `echo labirinto` para avançar ou `echo labirinto sair` para salvar o loot.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Labirinto(bot))
