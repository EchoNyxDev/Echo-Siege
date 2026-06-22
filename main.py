from discord.ext import commands, tasks
import discord
import os

from dotenv import load_dotenv
from utils.db import backup_databases, configure_sqlite_paths

configure_sqlite_paths()
import database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError(
        "DISCORD_TOKEN não foi encontrado no arquivo .env"
    )

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="echo ",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"{bot.user} online!")
    created = backup_databases(reason="startup", min_interval_hours=1)
    if created:
        print("Backup de banco criado:", ", ".join(str(path) for path in created))
    if not automatic_database_backup.is_running():
        automatic_database_backup.start()


@tasks.loop(hours=6)
async def automatic_database_backup():
    created = backup_databases(reason="auto", min_interval_hours=6)
    if created:
        print("Backup automatico de banco:", ", ".join(str(path) for path in created))

async def load_commands():
    await bot.load_extension("commands.iniciar")
    await bot.load_extension("commands.summon")
    await bot.load_extension("commands.perfil")
    await bot.load_extension("commands.adm")
    await bot.load_extension("commands.tutorial")
    await bot.load_extension("commands.atualizacoes")
    await bot.load_extension("commands.cidade")
    await bot.load_extension("commands.ajuda")
    await bot.load_extension("commands.party")
    await bot.load_extension("commands.mochila")
    await bot.load_extension("commands.dungeon")
    await bot.load_extension("commands.invasoes")
    await bot.load_extension("commands.hunt")
    await bot.load_extension("commands.adventure")
    await bot.load_extension("commands.pvp")
    await bot.load_extension("commands.arena")
    await bot.load_extension("commands.loja")
    await bot.load_extension("commands.gemshop")
    await bot.load_extension("commands.pets")
    await bot.load_extension("commands.equipamentos")
    await bot.load_extension("commands.guilds")
    await bot.load_extension("commands.expedicao")
    await bot.load_extension("commands.labirinto")
    await bot.load_extension("commands.campeoes")
    await bot.load_extension("commands.conquistas")
    await bot.load_extension("commands.eventos")
    await bot.load_extension("commands.copa")
    await bot.load_extension("commands.logs")
    await bot.load_extension("commands.rank")
    await bot.load_extension("commands.daily")
    await bot.load_extension("commands.cd")
    await bot.load_extension("commands.work")
    await bot.load_extension("commands.catalogo")
    await bot.load_extension("commands.codes")
    await bot.load_extension("commands.forja")

@bot.event
async def setup_hook():
    await load_commands()
    await bot.tree.sync()

bot.run(TOKEN)
