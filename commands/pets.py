import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.pets import PETS
except Exception:
    PETS = {}


def garantir_tabela_pets(cursor):
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
    cursor.execute("PRAGMA table_info(pets)")
    colunas = {info[1] for info in cursor.fetchall()}
    novas_colunas = {
        "pet_id": "TEXT",
        "pet_name": "TEXT",
        "rarity": "INTEGER",
        "level": "INTEGER DEFAULT 1",
        "xp": "INTEGER DEFAULT 0",
    }
    for coluna, tipo in novas_colunas.items():
        if coluna not in colunas:
            cursor.execute(f"ALTER TABLE pets ADD COLUMN {coluna} {tipo}")


def quebrar_linhas(linhas, limite=1000):
    blocos = []
    atual = ""
    for linha in linhas:
        if len(atual) + len(linha) + 1 > limite:
            blocos.append(atual)
            atual = linha
        else:
            atual = f"{atual}\n{linha}" if atual else linha
    if atual:
        blocos.append(atual)
    return blocos


class Pets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        garantir_tabela_pets(cursor)
        cursor.execute("PRAGMA table_info(players)")
        colunas = {info[1] for info in cursor.fetchall()}
        if "main_pet" not in colunas:
            cursor.execute("ALTER TABLE players ADD COLUMN main_pet TEXT")
        cursor.execute("PRAGMA table_info(teams)")
        colunas_teams = {info[1] for info in cursor.fetchall()}
        if "pet_slot" not in colunas_teams:
            cursor.execute("ALTER TABLE teams ADD COLUMN pet_slot TEXT")
        conn.commit()
        conn.close()

    async def process_pets(self, user: discord.User):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        garantir_tabela_pets(cursor)
        conn.commit()

        cursor.execute("PRAGMA table_info(players)")
        colunas_players = {info[1] for info in cursor.fetchall()}
        if "main_pet" not in colunas_players:
            cursor.execute("ALTER TABLE players ADD COLUMN main_pet TEXT")
            conn.commit()

        cursor.execute("SELECT gold, main_pet FROM players WHERE user_id = ?", (str(user.id),))
        player = cursor.fetchone()
        if not player:
            conn.close()
            return f"❌ {user.mention}, use `echo iniciar` antes."
        main_pet = str(player[1]) if player[1] else None

        cursor.execute("""
            SELECT id, pet_id, pet_name, rarity, level, xp
            FROM pets
            WHERE user_id = ?
            ORDER BY rarity DESC, level DESC, id ASC
        """, (str(user.id),))
        pets = cursor.fetchall()
        conn.close()

        if not pets:
            return f"🐾 {user.mention}, você ainda não tem pets. Compre um **Ticket de Pet** na loja e use `echo consumir ticket_pet`."

        embed = discord.Embed(
            title=f"🐾 Pets de {user.name}",
            description=f"Total: **{len(pets)}**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)

        linhas = []
        for db_id, pet_id, pet_name, rarity, level, xp in pets:
            pet_data = PETS.get(pet_id or "", {})
            nome = pet_name or pet_data.get("nome") or (pet_id or "pet_desconhecido").replace("_", " ").title()
            raridade = rarity or pet_data.get("raridade", 1)
            emoji = pet_data.get("emoji", "🐾")
            equipado = " | equipado" if main_pet == str(db_id) else ""
            linhas.append(f"`ID: {db_id}` {emoji} **{nome}** | {'⭐' * raridade} | Lv {level or 1} | XP {xp or 0}{equipado}")

        for idx, bloco in enumerate(quebrar_linhas(linhas), start=1):
            titulo = "Coleção" if idx == 1 else f"Coleção {idx}"
            embed.add_field(name=titulo, value=bloco, inline=False)

        embed.set_footer(text="Use `echo equiparpet <ID>` para escolher quem acompanha sua party.")
        return embed

    @commands.command(name="pets", aliases=["pet"])
    async def pets_prefix(self, ctx):
        resposta = await self.process_pets(ctx.author)
        if isinstance(resposta, discord.Embed):
            await ctx.send(embed=resposta)
        else:
            await ctx.send(resposta)

    @commands.command(name="equiparpet", aliases=["petmain", "pet_equipar"])
    async def equipar_pet_prefix(self, ctx, pet_id_banco: int = None):
        if not pet_id_banco:
            return await ctx.send("Use `echo equiparpet <ID do pet>`. Sim, pet também tem burocracia.")

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        garantir_tabela_pets(cursor)
        cursor.execute("PRAGMA table_info(players)")
        colunas = {info[1] for info in cursor.fetchall()}
        if "main_pet" not in colunas:
            cursor.execute("ALTER TABLE players ADD COLUMN main_pet TEXT")

        cursor.execute(
            "SELECT pet_id, pet_name, rarity FROM pets WHERE id = ? AND user_id = ?",
            (pet_id_banco, str(ctx.author.id)),
        )
        pet = cursor.fetchone()
        if not pet:
            conn.close()
            return await ctx.send("Esse pet não existe na sua coleção. O TutoriUAU checou a coleira e não achou nada.")

        cursor.execute("UPDATE players SET main_pet = ? WHERE user_id = ?", (str(pet_id_banco), str(ctx.author.id)))
        cursor.execute("INSERT OR IGNORE INTO teams (user_id) VALUES (?)", (str(ctx.author.id),))
        cursor.execute("UPDATE teams SET pet_slot = ? WHERE user_id = ?", (str(pet_id_banco), str(ctx.author.id)))
        conn.commit()
        conn.close()

        nome = pet[1] or PETS.get(pet[0] or "", {}).get("nome") or (pet[0] or "Pet").replace("_", " ").title()
        await ctx.send(f"**{nome}** agora acompanha sua party. Ele provavelmente entende mais de estratégia que você.")

    @app_commands.command(name="pets", description="Veja todos os seus pets atuais.")
    async def pets_slash(self, interaction: discord.Interaction):
        resposta = await self.process_pets(interaction.user)
        if isinstance(resposta, discord.Embed):
            await interaction.response.send_message(embed=resposta)
        else:
            await interaction.response.send_message(resposta)


async def setup(bot):
    await bot.add_cog(Pets(bot))
