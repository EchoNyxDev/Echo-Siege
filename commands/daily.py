import random
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

try:
    from data.pets import PETS
except Exception:
    PETS = {
        "slime_azul": {"nome": "Slime Azul", "raridade": 1, "is_gacha": True, "emoji": "🐾"},
        "dragao_bebe": {"nome": "Dragão Bebê", "raridade": 4, "is_gacha": True, "emoji": "🐲"},
    }


BRT = timezone(timedelta(hours=-3))

DAILY_CYCLE = [
    {"gold": 350, "gems": 5, "items": {"pocao_pequena": 1}, "comment": "Dia 1: compareceu. O mínimo, mas com brilho."},
    {"gold": 450, "gems": 8, "items": {"kit_reparos": 2}, "comment": "Dia 2: já é quase um relacionamento estável com o botão daily."},
    {"gold": 550, "gems": 10, "tickets": 1, "comment": "Dia 3: ticket na mão, esperança no coração e estatística rindo ao fundo."},
    {"gold": 650, "gems": 12, "items": {"pergaminho_de_xp": 1}, "comment": "Dia 4: XP extra, porque aprender sofrendo ainda conta."},
    {"gold": 750, "gems": 15, "items": {"ticket_pet": 1}, "comment": "Dia 5: um Ticket de Pet. Agora você pode ser julgado por uma criatura pequena."},
    {"gold": 900, "gems": 20, "items": {"pergaminho_de_ouro": 1}, "comment": "Dia 6: bônus de ouro. O capitalismo de fantasia está orgulhoso."},
    {"gold": 1200, "gems": 35, "tickets": 2, "items": {"token_titulo_pontual": 1}, "comment": "Dia 7: uma semana. O TutoriUAU está quase emocionado. Quase."},
    {"gold": 1300, "gems": 20, "items": {"pocao_media": 2}, "comment": "Dia 8: você voltou depois do prêmio semanal. Suspeito, mas aceito."},
    {"gold": 1450, "gems": 22, "tickets": 1, "comment": "Dia 9: calendário dominado. Agora falta dominar decisões financeiras."},
    {"gold": 1600, "gems": 25, "items": {"material_lendario_quase": 1}, "comment": "Dia 10: material estranho. Não pergunta, só guarda na mochila."},
    {"gold": 1800, "gems": 28, "items": {"ticket_pet": 1}, "comment": "Dia 11: outro pet talvez. Sua party virou creche tática."},
    {"gold": 2000, "gems": 32, "tickets": 2, "comment": "Dia 12: dois tickets. Se vier 1⭐, a culpa é da matemática, não minha."},
    {"gold": 2300, "gems": 40, "items": {"token_moldura_cidade_noturna": 1}, "comment": "Dia 13: tema Cidade Noturna. Estética por insistência."},
    {"gold": 3000, "gems": 75, "tickets": 3, "pet": True, "comment": "Dia 14: pet garantido. A ofensiva ficou alta o bastante para atrair responsabilidade."},
]


def ensure_daily_db(cursor):
    cursor.execute("PRAGMA table_info(players)")
    cols = {info[1] for info in cursor.fetchall()}
    for col, ddl in {
        "last_daily": "TEXT DEFAULT ''",
        "daily_streak": "INTEGER DEFAULT 0",
        "gems": "INTEGER DEFAULT 0",
        "gold": "INTEGER DEFAULT 0",
    }.items():
        if col not in cols:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} {ddl}")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            pet_id TEXT,
            pet_name TEXT,
            rarity INTEGER,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summon_data(
            user_id TEXT PRIMARY KEY,
            summon_tickets INTEGER DEFAULT 0,
            shop_level INTEGER DEFAULT 1,
            pity_4 INTEGER DEFAULT 0,
            pity_5 INTEGER DEFAULT 0,
            total_summons INTEGER DEFAULT 0,
            total_1_star INTEGER DEFAULT 0,
            total_2_star INTEGER DEFAULT 0,
            total_3_star INTEGER DEFAULT 0,
            total_4_star INTEGER DEFAULT 0,
            total_5_star INTEGER DEFAULT 0
        )
    """)


def add_item(cursor, user_id, item_name, qty):
    cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item_name))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (user_id, item_name, qty))


def add_tickets(cursor, user_id, amount):
    if amount <= 0:
        return
    cursor.execute(
        """
        INSERT OR IGNORE INTO summon_data
        (user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star)
        VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
        """,
        (user_id,),
    )
    cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (amount, user_id))


def escolher_pet():
    pool = [(pet_id, pet) for pet_id, pet in PETS.items() if pet.get("is_gacha", True)]
    if not pool:
        pool = list(PETS.items())
    pesos = [max(1, 7 - int(pet.get("raridade", 1))) for _, pet in pool]
    return random.choices(pool, weights=pesos, k=1)[0]


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_daily_db(cursor)
        conn.commit()
        conn.close()

    async def processar_daily(self, user: discord.User):
        hoje_obj = datetime.now(BRT).date()
        hoje_str = hoje_obj.strftime("%Y-%m-%d")
        user_id = str(user.id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_daily_db(cursor)
        cursor.execute("SELECT gold, last_daily, daily_streak FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        if not player:
            conn.close()
            return f"{user.mention}, use `echo iniciar` antes. O TutoriUAU não deposita daily em conta fantasma."

        _, last_daily_str, streak = player
        streak = streak or 0
        if last_daily_str == hoje_str:
            conn.close()
            return f"Você já pegou o daily de hoje, {user.mention}. Volta amanhã. O botão não vai se comover."

        if last_daily_str:
            try:
                diff = (hoje_obj - datetime.strptime(last_daily_str, "%Y-%m-%d").date()).days
                streak = streak + 1 if diff == 1 else 1
            except ValueError:
                streak = 1
        else:
            streak = 1

        reward = DAILY_CYCLE[(streak - 1) % len(DAILY_CYCLE)]
        gold = reward["gold"] + min(2500, streak * 45)
        gems = reward.get("gems", 0) + (10 if streak % 7 == 0 else 0)
        tickets = reward.get("tickets", 0)
        rewards_lines = [f"+{gold:,} Gold", f"+{gems:,} Gems"]

        cursor.execute(
            "UPDATE players SET gold = gold + ?, gems = gems + ?, last_daily = ?, daily_streak = ? WHERE user_id = ?",
            (gold, gems, hoje_str, streak, user_id),
        )
        add_tickets(cursor, user_id, tickets)
        if tickets:
            rewards_lines.append(f"+{tickets} Ticket(s) de Herói")

        for item_name, qty in reward.get("items", {}).items():
            add_item(cursor, user_id, item_name, qty)
            rewards_lines.append(f"+{qty}x {item_name.replace('_', ' ').title()}")

        pet_line = None
        if reward.get("pet") or (streak >= 30 and streak % 15 == 0):
            pet_id, pet = escolher_pet()
            pet_name = pet.get("nome", pet_id.replace("_", " ").title())
            rarity = pet.get("raridade", 1)
            cursor.execute(
                "INSERT INTO pets (user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, ?, 1, 0)",
                (user_id, pet_id, pet_name, rarity),
            )
            pet_line = f"{pet.get('emoji', '🐾')} **{pet_name}** ({'⭐' * rarity})"
            rewards_lines.append(f"+Pet: {pet_name} ({'⭐' * rarity})")

        conn.commit()
        conn.close()

        next_special = len(DAILY_CYCLE) - ((streak - 1) % len(DAILY_CYCLE))
        embed = discord.Embed(
            title="Daily Resgatado",
            description=f"**TutoriUAU:** {reward['comment']}\n\nOfensiva atual: **{streak} dia(s)**",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Recompensas", value="\n".join(rewards_lines), inline=False)
        if pet_line:
            embed.add_field(name="Pet atraído pela ofensiva", value=pet_line, inline=False)
        embed.add_field(
            name="Próximo marco",
            value=f"Faltam **{next_special}** daily(s) para fechar o ciclo especial de 14 dias.",
            inline=False,
        )
        embed.set_footer(text="TutoriUAU: perder a sequência reinicia o drama. Eu avisei, a UI avisou, o calendário avisou.")
        return embed

    @commands.command(name="daily", aliases=["diario", "diária", "diaria"])
    async def daily_cmd(self, ctx):
        resp = await self.processar_daily(ctx.author)
        if isinstance(resp, discord.Embed):
            await ctx.send(embed=resp)
        else:
            await ctx.send(resp)

    @app_commands.command(name="daily", description="Resgata sua recompensa diária expandida.")
    async def daily_slash(self, interaction: discord.Interaction):
        resp = await self.processar_daily(interaction.user)
        if isinstance(resp, discord.Embed):
            await interaction.response.send_message(embed=resp)
        else:
            await interaction.response.send_message(resp)


async def setup(bot):
    await bot.add_cog(Daily(bot))
