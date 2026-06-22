import os
import sqlite3
import sys
import time

import discord
from discord import app_commands
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from data.events import get_active_events, get_next_events
from utils.combat import simular_combate_tatico
from utils.rewards import scale_combat_rewards
from utils.xp_system import dar_xp_heroi, dar_xp_jogador


def init_event_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_progress(
            user_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            kills INTEGER DEFAULT 0,
            boss_kills INTEGER DEFAULT 0,
            dungeon_clears INTEGER DEFAULT 0,
            last_action INTEGER DEFAULT 0,
            reward_claims INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, event_id)
        )
    """)
    cursor.execute("PRAGMA table_info(players)")
    cols = {row[1] for row in cursor.fetchall()}
    if "gems" not in cols:
        cursor.execute("ALTER TABLE players ADD COLUMN gems INTEGER DEFAULT 0")


def add_inventory(cursor, user_id, item_name, quantity):
    if quantity <= 0:
        return
    cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item_name))
    item = cursor.fetchone()
    if item:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity, item[0]))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (user_id, item_name, quantity))


def add_tickets(cursor, user_id, quantity):
    if quantity <= 0:
        return
    cursor.execute(
        """
        INSERT OR IGNORE INTO summon_data
        (user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star)
        VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
        """,
        (user_id,),
    )
    cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (quantity, user_id))


class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_event_db(cursor)
        conn.commit()
        conn.close()

    def _active_event(self):
        active = get_active_events()
        return active[0] if active else None

    def _events_embed(self):
        active = get_active_events()
        upcoming = get_next_events(limit=3)
        embed = discord.Embed(title="Eventos de Lugnica", color=discord.Color.purple())
        if active:
            lines = [f"**{event['name']}** ate {event['end'].strftime('%d/%m/%Y')} | Item: `{event['item']}`" for event in active]
            embed.add_field(name="Ativos", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="Ativos", value="Nenhum evento ativo agora.", inline=False)
        embed.add_field(
            name="Proximos",
            value="\n".join(f"**{event['name']}**: {event['start'].strftime('%d/%m/%Y')}" for event in upcoming) or "Sem calendario.",
            inline=False,
        )
        embed.add_field(
            name="Echo Cup / Copa do Mundo",
            value=(
                "`echo copa` - resumo do evento e das regras.\n"
                "`echo copa iniciar` - cria seu time com 11 herois da sua conta.\n"
                "`echo copa jogar` - simula grupos e mata-mata, uma tentativa a cada 6 horas.\n"
                "`echo copa loja` / `echo copa resgatar <id>` - gasta echobet em temas, titulos, tickets e pets.\n"
                "`echo copa ranking` / `echo copa hall` - classificacao global e mural dos melhores.\n"
                "`echo copa banner` / `echo copa summon` - banner esportivo com ticket ou custo reduzido em ouro."
            ),
            inline=False,
        )
        embed.set_footer(text="Use echo evento lutar, echo evento boss, echo evento dungeon, echo evento resgatar ou echo copa.")
        return embed

    def _progress(self, cursor, user_id, event_id):
        cursor.execute(
            """
            INSERT OR IGNORE INTO event_progress (user_id, event_id)
            VALUES (?, ?)
            """,
            (user_id, event_id),
        )
        cursor.execute(
            """
            SELECT points, kills, boss_kills, dungeon_clears, last_action, reward_claims
            FROM event_progress
            WHERE user_id = ? AND event_id = ?
            """,
            (user_id, event_id),
        )
        return cursor.fetchone()

    def _enemy_for(self, event, mode, avg_level):
        scale = max(1, avg_level)
        if mode == "boss":
            return {
                "nome": event["boss"],
                "classe": "boss",
                "level": scale,
                "stats": {
                    "hp": 900 + scale * 90,
                    "atk": 50 + scale * 9,
                    "matk": 45 + scale * 8,
                    "def": 25 + scale * 4,
                    "spd": 14 + scale // 5,
                    "crt": 8,
                    "level": scale,
                },
                "habilidades": ["ataque_giratorio", "sopro_de_fogo"],
            }
        if mode == "dungeon":
            return {
                "nome": event["dungeon"],
                "classe": "elite",
                "level": scale,
                "stats": {
                    "hp": 650 + scale * 65,
                    "atk": 40 + scale * 7,
                    "matk": 40 + scale * 7,
                    "def": 20 + scale * 3,
                    "spd": 16 + scale // 6,
                    "crt": 7,
                    "level": scale,
                },
                "habilidades": ["disparo_de_mana"],
            }
        return {
            "nome": event["monster"],
            "classe": "comum",
            "level": scale,
            "stats": {
                "hp": 260 + scale * 35,
                "atk": 24 + scale * 5,
                "matk": 20 + scale * 4,
                "def": 10 + scale * 2,
                "spd": 12 + scale // 8,
                "crt": 5,
                "level": scale,
            },
            "habilidades": ["ataque_giratorio"],
        }

    def _grant(self, cursor, user_id, event, mode, party_ids, avg_level):
        reward = dict(event["rewards"][mode])
        reward["gold"], reward["xp"] = scale_combat_rewards(
            reward.get("gold", 0),
            reward.get("xp", 0),
            avg_level,
        )
        cursor.execute("UPDATE players SET gold = gold + ?, gems = gems + ? WHERE user_id = ?", (reward.get("gold", 0), reward.get("gems", 0), user_id))
        add_tickets(cursor, user_id, reward.get("tickets", 0))
        add_inventory(cursor, user_id, event["item"], reward.get("item_qty", 0))
        dar_xp_jogador(cursor, user_id, reward.get("xp", 0))
        for hero_db_id in party_ids:
            dar_xp_heroi(cursor, int(hero_db_id), reward.get("xp", 0))
        return reward

    async def _run_mode(self, ctx, mode):
        event = self._active_event()
        if not event:
            upcoming = get_next_events(limit=1)
            if not upcoming:
                return await ctx.send("Nenhum evento ativo no momento.")
            nxt = upcoming[0]
            return await ctx.send(f"Nenhum evento ativo. Proximo: **{nxt['name']}** em {nxt['start'].strftime('%d/%m/%Y')}.")

        hunt_cog = self.bot.get_cog("Hunt")
        if not hunt_cog:
            return await ctx.send("O sistema de party da hunt ainda nao carregou. Tente novamente em instantes.")

        party = hunt_cog.puxar_party_para_combate(ctx.author.id, ctx.author.name)
        if not party:
            return await ctx.send("Monte uma party primeiro com `echo main` e `echo party`.")

        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_event_db(cursor)
        progress = self._progress(cursor, user_id, event["id"])
        last_action = progress[4] or 0
        cooldown = 600 if mode == "monster" else 1200
        now = int(time.time())
        if now - last_action < cooldown:
            conn.close()
            remaining = int((cooldown - (now - last_action)) / 60) + 1
            return await ctx.send(f"Aguarde **{remaining} min** para outra acao de evento.")

        avg_level = int(sum(member.get("level", 1) for member in party) / max(1, len(party)))
        enemy = self._enemy_for(event, mode, avg_level)
        victory, battle_log = simular_combate_tatico(party, [enemy])

        cursor.execute(
            "UPDATE event_progress SET last_action = ? WHERE user_id = ? AND event_id = ?",
            (now, user_id, event["id"]),
        )

        if not victory:
            conn.commit()
            conn.close()
            embed = discord.Embed(title=f"Evento - {event['name']}", description=f"Derrota contra **{enemy['nome']}**.\n\n{battle_log}", color=discord.Color.red())
            return await ctx.send(embed=embed)

        party_ids = [member["id"] for member in party]
        reward = self._grant(cursor, user_id, event, mode, party_ids, avg_level)
        points_col = {"monster": "kills", "boss": "boss_kills", "dungeon": "dungeon_clears"}[mode]
        cursor.execute(
            f"UPDATE event_progress SET points = points + ?, {points_col} = {points_col} + 1 WHERE user_id = ? AND event_id = ?",
            (reward.get("points", 0), user_id, event["id"]),
        )
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title=f"Evento - {event['name']}",
            description=f"Vitoria contra **{enemy['nome']}**.\n\n{battle_log}",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Recompensas",
            value=(
                f"+{reward.get('points', 0)} pontos de evento\n"
                f"+{reward.get('gold', 0):,} Gold\n"
                f"+{reward.get('xp', 0)} XP\n"
                f"+{reward.get('item_qty', 0)}x {event['item']}"
            ),
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(name="eventos", aliases=["events"])
    async def eventos_cmd(self, ctx):
        await ctx.send(embed=self._events_embed())

    @commands.group(name="evento", aliases=["event"], invoke_without_command=True)
    async def evento_group(self, ctx):
        await ctx.send(embed=self._events_embed())

    @evento_group.command(name="lutar", aliases=["hunt", "monstro"])
    async def evento_lutar(self, ctx):
        await self._run_mode(ctx, "monster")

    @evento_group.command(name="boss", aliases=["chefe"])
    async def evento_boss(self, ctx):
        await self._run_mode(ctx, "boss")

    @evento_group.command(name="dungeon", aliases=["masmorra"])
    async def evento_dungeon(self, ctx):
        await self._run_mode(ctx, "dungeon")

    @evento_group.command(name="resgatar", aliases=["claim", "bau", "baú"])
    async def evento_resgatar(self, ctx, quantidade: int = 1):
        event = self._active_event()
        if not event:
            return await ctx.send("Nenhum evento ativo para resgatar recompensas.")
        quantidade = max(1, min(10, quantidade))
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        init_event_db(cursor)
        progress = self._progress(cursor, user_id, event["id"])
        points = progress[0] or 0
        chest = event["rewards"]["chest"]
        cost = chest["cost"] * quantidade
        if points < cost:
            conn.close()
            return await ctx.send(f"Voce precisa de **{cost} pontos** para resgatar {quantidade} bau(s). Pontos atuais: **{points}**.")

        cursor.execute(
            "UPDATE event_progress SET points = points - ?, reward_claims = reward_claims + ? WHERE user_id = ? AND event_id = ?",
            (cost, quantidade, user_id, event["id"]),
        )
        reward = {
            "gold": chest.get("gold", 0) * quantidade,
            "gems": chest.get("gems", 0) * quantidade,
            "tickets": chest.get("tickets", 0) * quantidade,
            "item_qty": chest.get("item_qty", 0) * quantidade,
        }
        cursor.execute("UPDATE players SET gold = gold + ?, gems = gems + ? WHERE user_id = ?", (reward["gold"], reward["gems"], user_id))
        add_tickets(cursor, user_id, reward["tickets"])
        add_inventory(cursor, user_id, event["item"], reward["item_qty"])
        conn.commit()
        conn.close()
        await ctx.send(
            f"Bau de evento resgatado x{quantidade}: **{reward['gold']:,} Gold**, **{reward['gems']} Gems**, "
            f"**{reward['tickets']} Ticket(s)** e **{reward['item_qty']}x {event['item']}**."
        )

    @app_commands.command(name="eventos", description="Mostra eventos ativos e proximos.")
    async def eventos_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self._events_embed())


async def setup(bot):
    await bot.add_cog(Eventos(bot))
