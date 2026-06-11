import sqlite3
import time

import discord
from discord import app_commands
from discord.ext import commands


ACHIEVEMENTS = [
    {"id": "primeiros_passos", "name": "Primeiros Passos", "desc": "Use `echo iniciar` e vire oficialmente problema do servidor.", "metric": "started", "target": 1, "reward": {"gold": 300}},
    {"id": "perfil_arrumado", "name": "Foto no Crachá", "desc": "Defina um herói principal. O TutoriUAU gosta de saber quem culpar.", "metric": "has_main_hero", "target": 1, "reward": {"gold": 500}},
    {"id": "primeiro_pet", "name": "Responsável por Algo", "desc": "Tenha pelo menos 1 pet.", "metric": "pets_count", "target": 1, "reward": {"gems": 25}},
    {"id": "petshop_10", "name": "Coleira por Atacado", "desc": "Tenha 10 pets.", "metric": "pets_count", "target": 10, "reward": {"gems": 80, "items": {"ticket_pet": 1}}},
    {"id": "cacador_10", "name": "Caçador Iniciante", "desc": "Vença 10 caçadas.", "metric": "total_hunts", "target": 10, "reward": {"gold": 1000}},
    {"id": "cacador_50", "name": "Caçador Veterano", "desc": "Vença 50 caçadas. A fauna local mandou uma reclamação formal.", "metric": "total_hunts", "target": 50, "reward": {"gold": 3500, "tickets": 1}},
    {"id": "cacador_200", "name": "Problema Ecológico", "desc": "Vença 200 caçadas.", "metric": "total_hunts", "target": 200, "reward": {"gold": 12000, "gems": 150, "tickets": 2}},
    {"id": "colecao_10", "name": "Colecionador", "desc": "Tenha 10 heróis.", "metric": "heroes_count", "target": 10, "reward": {"gems": 25}},
    {"id": "colecao_50", "name": "Arquivo Vivo", "desc": "Tenha 50 heróis.", "metric": "heroes_count", "target": 50, "reward": {"gems": 100, "tickets": 2}},
    {"id": "colecao_100", "name": "Excel com Pernas", "desc": "Tenha 100 heróis. Isso já é planilha emocional.", "metric": "heroes_count", "target": 100, "reward": {"gems": 250, "items": {"ticket_heroi_raro": 1}}},
    {"id": "unique_25", "name": "Catálogo com Opinião", "desc": "Tenha 25 heróis diferentes.", "metric": "unique_heroes", "target": 25, "reward": {"gems": 120}},
    {"id": "summon_25", "name": "Chamado Constante", "desc": "Faça 25 summons.", "metric": "total_summons", "target": 25, "reward": {"tickets": 1}},
    {"id": "summon_100", "name": "O Banner Piscou", "desc": "Faça 100 summons.", "metric": "total_summons", "target": 100, "reward": {"gems": 120, "tickets": 2}},
    {"id": "summon_500", "name": "A Estatística Venceu", "desc": "Faça 500 summons. O gacha agradece e finge surpresa.", "metric": "total_summons", "target": 500, "reward": {"gems": 400, "items": {"ticket_escolha_heroi": 1}}},
    {"id": "quatro_estrelas_10", "name": "Brilho Quase Lendário", "desc": "Consiga 10 heróis 4 estrelas.", "metric": "total_4_star", "target": 10, "reward": {"gems": 80}},
    {"id": "cinco_estrelas", "name": "Brilho Lendário", "desc": "Consiga 1 herói 5 estrelas.", "metric": "total_5_star", "target": 1, "reward": {"gems": 60}},
    {"id": "cinco_estrelas_10", "name": "Assinante do Milagre", "desc": "Consiga 10 heróis 5 estrelas.", "metric": "total_5_star", "target": 10, "reward": {"gems": 300, "tickets": 3}},
    {"id": "arena_10", "name": "Subiu a Torre", "desc": "Alcance o andar 10 da arena.", "metric": "arena_record", "target": 10, "reward": {"gold": 2500}},
    {"id": "arena_50", "name": "Sem Teto Visível", "desc": "Alcance o andar 50 da arena.", "metric": "arena_record", "target": 50, "reward": {"gold": 12000, "gems": 150}},
    {"id": "arena_100", "name": "Elevador Quebrado", "desc": "Alcance o andar 100 da arena.", "metric": "arena_record", "target": 100, "reward": {"gems": 350, "items": {"token_moldura_arvore_glacial": 1}}},
    {"id": "pvp_10", "name": "Duelista", "desc": "Vença 10 duelos PvP.", "metric": "pvp_wins", "target": 10, "reward": {"gold": 3000, "gems": 30}},
    {"id": "pvp_perdedor_10", "name": "Aprendizado Horizontal", "desc": "Perca 10 duelos PvP. O chão também ensina.", "metric": "pvp_losses", "target": 10, "reward": {"gold": 1200}},
    {"id": "guild_membro", "name": "Contrato Social", "desc": "Entre em uma guilda.", "metric": "guild_member", "target": 1, "reward": {"gems": 40}},
    {"id": "guild_doador", "name": "Patrono da Guilda", "desc": "Doe 5.000 Gold para guildas.", "metric": "guild_contribution", "target": 5000, "reward": {"gems": 80}},
    {"id": "guild_banco_vivo", "name": "Caixa Eletrônico com Nome", "desc": "Doe 50.000 Gold para guildas.", "metric": "guild_contribution", "target": 50000, "reward": {"gems": 250, "items": {"token_titulo_patrocinador": 1}}},
    {"id": "daily_7", "name": "Calendário Funcional", "desc": "Faça 7 dias de daily em sequência.", "metric": "daily_streak", "target": 7, "reward": {"gems": 60}},
    {"id": "daily_30", "name": "Inimigo do Esquecimento", "desc": "Faça 30 dias de daily em sequência.", "metric": "daily_streak", "target": 30, "reward": {"gems": 250, "items": {"token_titulo_pontual_demais": 1}}},
    {"id": "mochila_25", "name": "Guarda-Treco Licenciado", "desc": "Tenha 25 itens somados na mochila.", "metric": "inventory_items", "target": 25, "reward": {"gold": 2500}},
    {"id": "mochila_100", "name": "Depósito Humano", "desc": "Tenha 100 itens somados na mochila.", "metric": "inventory_items", "target": 100, "reward": {"gems": 120}},
    {"id": "itens_unicos_20", "name": "Eu Vou Usar Depois", "desc": "Tenha 20 tipos diferentes de itens.", "metric": "inventory_unique", "target": 20, "reward": {"items": {"token_moldura_flores_cerejeira": 1}}},
    {"id": "rico_10k", "name": "Pequeno Burguês de Lugnica", "desc": "Tenha 10.000 Gold na carteira.", "metric": "gold_wallet", "target": 10000, "reward": {"gems": 30}},
    {"id": "rico_100k", "name": "Banqueiro do Isekai", "desc": "Tenha 100.000 Gold na carteira.", "metric": "gold_wallet", "target": 100000, "reward": {"gems": 180}},
    {"id": "gems_500", "name": "Brilho no Bolso", "desc": "Tenha 500 Gems.", "metric": "gems_wallet", "target": 500, "reward": {"gold": 5000}},
    {"id": "errou_comando_1", "name": "Digitação Criativa", "desc": "Erre 1 comando. Parabéns, você achou a parede invisível da interface.", "metric": "invalid_commands", "target": 1, "reward": {"gold": 100}, "secret": True},
    {"id": "errou_comando_10", "name": "QA Não Remunerado", "desc": "Erre 10 comandos. O TutoriUAU agradece esse teste de resistência.", "metric": "invalid_commands", "target": 10, "reward": {"gems": 25}, "secret": True},
    {"id": "errou_comando_50", "name": "Sintaxe? Nunca Vi", "desc": "Erre 50 comandos. Isso é talento ou teclado possuído, não sei.", "metric": "invalid_commands", "target": 50, "reward": {"gems": 100, "items": {"token_titulo_bug_ambulante": 1}}, "secret": True},
    {"id": "expedicao_1", "name": "Voltei com Poeira", "desc": "Conclua 1 expedição.", "metric": "expeditions_done", "target": 1, "reward": {"gold": 1000}},
    {"id": "expedicao_24h", "name": "Terceirização da Aventura", "desc": "Some 24 horas em expedições.", "metric": "expedition_hours", "target": 24, "reward": {"gems": 120, "items": {"ticket_pet": 1}}},
    {"id": "labirinto_10", "name": "Virou à Esquerda Demais", "desc": "Explore 10 salas do labirinto.", "metric": "labyrinth_rooms", "target": 10, "reward": {"gold": 3000}},
    {"id": "labirinto_boss_5", "name": "Síndico do Labirinto", "desc": "Derrote 5 bosses do labirinto.", "metric": "labyrinth_bosses", "target": 5, "reward": {"gems": 160, "items": {"token_moldura_minecraft": 1}}},
    {"id": "campeoes_5", "name": "IA Também Sente", "desc": "Vença 5 lutas na Torre dos Campeões.", "metric": "tower_wins", "target": 5, "reward": {"gems": 80}},
    {"id": "campeoes_rating_1200", "name": "Fantasma Competitivo", "desc": "Alcance 300 de Prestígio na Torre dos Campeões.", "metric": "tower_rating", "target": 300, "reward": {"gems": 120}},
    {"id": "guild_hunt_3", "name": "Chefe? Que Chefe?", "desc": "Participe de 3 caçadas de guilda.", "metric": "guild_hunts", "target": 3, "reward": {"gems": 90}},
    {"id": "comprador_gems_3", "name": "Cliente VIP da Aba Errada", "desc": "Compre 3 itens na loja de Gems.", "metric": "gemshop_purchases", "target": 3, "reward": {"gold": 4000}},
    {"id": "molduras_3", "name": "Cenógrafo do Próprio Perfil", "desc": "Tenha 3 temas permanentes de perfil.", "metric": "frames_owned", "target": 3, "reward": {"gems": 120}},
    {"id": "titulos_3", "name": "Nome Grande, Dano Questionável", "desc": "Tenha 3 títulos permanentes.", "metric": "titles_owned", "target": 3, "reward": {"gems": 120}},
    {"id": "resgatou_10", "name": "Clicador Profissional", "desc": "Resgate 10 conquistas.", "metric": "achievements_claimed", "target": 10, "reward": {"items": {"token_titulo_clicador": 1}}},
]


def ensure_achievement_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_achievements(
            user_id TEXT NOT NULL,
            achievement_id TEXT NOT NULL,
            claimed INTEGER DEFAULT 0,
            claimed_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, achievement_id)
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
    cursor.execute("PRAGMA table_info(players)")
    cols = {row[1] for row in cursor.fetchall()}
    for col, ddl in {
        "gems": "INTEGER DEFAULT 0",
        "total_hunts": "INTEGER DEFAULT 0",
        "arena_record": "INTEGER DEFAULT 0",
        "pvp_wins": "INTEGER DEFAULT 0",
        "pvp_losses": "INTEGER DEFAULT 0",
        "daily_streak": "INTEGER DEFAULT 0",
        "main_hero": "TEXT",
    }.items():
        if col not in cols:
            cursor.execute(f"ALTER TABLE players ADD COLUMN {col} {ddl}")


def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute(
        "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)",
        (str(user_id), stat),
    )
    cursor.execute(
        "UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?",
        (amount, str(user_id), stat),
    )


def one(cursor, query, params=(), default=0):
    try:
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else default
    except sqlite3.OperationalError:
        return default


def collect_metrics(cursor, user_id):
    user_id = str(user_id)
    stats = {
        row[0]: row[1]
        for row in cursor.execute("SELECT stat, value FROM player_stats WHERE user_id = ?", (user_id,)).fetchall()
    }
    return {
        "started": 1 if one(cursor, "SELECT COUNT(*) FROM players WHERE user_id = ?", (user_id,)) else 0,
        "has_main_hero": 1 if one(cursor, "SELECT COUNT(*) FROM players WHERE user_id = ? AND main_hero IS NOT NULL AND main_hero != ''", (user_id,)) else 0,
        "total_hunts": one(cursor, "SELECT total_hunts FROM players WHERE user_id = ?", (user_id,)),
        "arena_record": one(cursor, "SELECT arena_record FROM players WHERE user_id = ?", (user_id,)),
        "pvp_wins": one(cursor, "SELECT pvp_wins FROM players WHERE user_id = ?", (user_id,)),
        "pvp_losses": one(cursor, "SELECT pvp_losses FROM players WHERE user_id = ?", (user_id,)),
        "daily_streak": one(cursor, "SELECT daily_streak FROM players WHERE user_id = ?", (user_id,)),
        "gold_wallet": one(cursor, "SELECT gold FROM players WHERE user_id = ?", (user_id,)),
        "gems_wallet": one(cursor, "SELECT gems FROM players WHERE user_id = ?", (user_id,)),
        "heroes_count": one(cursor, "SELECT COUNT(*) FROM heroes WHERE user_id = ?", (user_id,)),
        "unique_heroes": one(cursor, "SELECT COUNT(DISTINCT hero_id) FROM heroes WHERE user_id = ?", (user_id,)),
        "pets_count": one(cursor, "SELECT COUNT(*) FROM pets WHERE user_id = ?", (user_id,)),
        "inventory_items": one(cursor, "SELECT COALESCE(SUM(quantity), 0) FROM inventory WHERE user_id = ?", (user_id,)),
        "inventory_unique": one(cursor, "SELECT COUNT(*) FROM inventory WHERE user_id = ? AND quantity > 0", (user_id,)),
        "total_summons": one(cursor, "SELECT total_summons FROM summon_data WHERE user_id = ?", (user_id,)),
        "total_4_star": one(cursor, "SELECT total_4_star FROM summon_data WHERE user_id = ?", (user_id,)),
        "total_5_star": one(cursor, "SELECT total_5_star FROM summon_data WHERE user_id = ?", (user_id,)),
        "guild_contribution": one(cursor, "SELECT contribution FROM player_guild_members WHERE user_id = ?", (user_id,)),
        "guild_member": 1 if one(cursor, "SELECT COUNT(*) FROM player_guild_members WHERE user_id = ?", (user_id,)) else 0,
        "invalid_commands": stats.get("invalid_commands", 0),
        "expeditions_done": stats.get("expeditions_done", 0),
        "expedition_hours": stats.get("expedition_hours", 0),
        "labyrinth_rooms": stats.get("labyrinth_rooms", 0),
        "labyrinth_bosses": stats.get("labyrinth_bosses", 0),
        "tower_wins": stats.get("tower_wins", 0),
        "tower_rating": one(cursor, "SELECT rating FROM champion_tower WHERE user_id = ?", (user_id,), 0),
        "guild_hunts": stats.get("guild_hunts", 0),
        "gemshop_purchases": stats.get("gemshop_purchases", 0),
        "frames_owned": one(cursor, "SELECT COUNT(*) FROM inventory WHERE user_id = ? AND item_name LIKE 'token_moldura_%' AND quantity > 0", (user_id,)),
        "titles_owned": one(cursor, "SELECT COUNT(*) FROM inventory WHERE user_id = ? AND item_name LIKE 'token_titulo_%' AND quantity > 0", (user_id,)),
        "achievements_claimed": one(cursor, "SELECT COUNT(*) FROM player_achievements WHERE user_id = ? AND claimed = 1", (user_id,)),
    }


def reward_text(reward):
    parts = []
    if reward.get("gold"):
        parts.append(f"{reward['gold']:,} Gold")
    if reward.get("gems"):
        parts.append(f"{reward['gems']:,} Gems")
    if reward.get("tickets"):
        parts.append(f"{reward['tickets']} Ticket(s)")
    if reward.get("items"):
        parts.extend(f"{qty}x {name.replace('_', ' ').title()}" for name, qty in reward["items"].items())
    return ", ".join(parts) if parts else "Sem recompensa. Só prestígio, que não paga boleto."


def grant_reward(cursor, user_id, reward):
    user_id = str(user_id)
    if reward.get("gold"):
        cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (reward["gold"], user_id))
    if reward.get("gems"):
        cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (reward["gems"], user_id))
    if reward.get("tickets"):
        cursor.execute(
            """
            INSERT OR IGNORE INTO summon_data
            (user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star)
            VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
            """,
            (user_id,),
        )
        cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (reward["tickets"], user_id))
    for item_name, qty in reward.get("items", {}).items():
        cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item_name))
        item = cursor.fetchone()
        if item:
            cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, item[0]))
        else:
            cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (user_id, item_name, qty))


class AchievementView(discord.ui.View):
    def __init__(self, cog, user: discord.User, embeds):
        super().__init__(timeout=180)
        self.cog = cog
        self.user = user
        self.embeds = embeds
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_btn.disabled = self.page == 0
        self.next_btn.disabled = self.page >= len(self.embeds) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Essa lista de conquistas não é sua. Fofoqueiro de progresso alheio.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Resgatar Recompensas", style=discord.ButtonStyle.success)
    async def claim_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.cog._claim(self.user)
        self.embeds = await self.cog._build_embeds(self.user)
        self.page = min(self.page, len(self.embeds) - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class Conquistas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_achievement_db(cursor)
        conn.commit()
        conn.close()

    def _evaluated(self, cursor, user_id):
        ensure_achievement_db(cursor)
        metrics = collect_metrics(cursor, user_id)
        cursor.execute("SELECT achievement_id FROM player_achievements WHERE user_id = ? AND claimed = 1", (str(user_id),))
        claimed = {row[0] for row in cursor.fetchall()}
        results = []
        for ach in ACHIEVEMENTS:
            value = metrics.get(ach["metric"], 0)
            done = value >= ach["target"]
            results.append({**ach, "value": value, "done": done, "claimed": ach["id"] in claimed})
        return results

    async def _build_embeds(self, user):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        achievements = self._evaluated(cursor, str(user.id))
        conn.commit()
        conn.close()

        visible_achievements = [ach for ach in achievements if not ach.get("secret") or ach["done"] or ach["claimed"]]
        secret_hidden = len(achievements) - len(visible_achievements)
        done_count = sum(1 for ach in achievements if ach["done"])
        claimed_count = sum(1 for ach in achievements if ach["claimed"])
        ready_count = sum(1 for ach in achievements if ach["done"] and not ach["claimed"])
        chunks = [visible_achievements[i:i + 5] for i in range(0, len(visible_achievements), 5)] or [[]]
        embeds = []
        for page, chunk in enumerate(chunks, start=1):
            lines = []
            for ach in chunk:
                if ach["claimed"]:
                    status = "resgatada"
                elif ach["done"]:
                    status = "pronta"
                else:
                    status = f"{ach['value']:,}/{ach['target']:,}"
                lines.append(f"**{ach['name']}** - `{status}`\n{ach['desc']}\nRecompensa: {reward_text(ach['reward'])}")
            embed = discord.Embed(
                title=f"Conquistas de {user.display_name}",
                description=(
                    f"Concluídas: **{done_count}/{len(achievements)}** | Resgatadas: **{claimed_count}** | "
                    f"Prontas: **{ready_count}** | Secretas ocultas: **{secret_hidden}**\n"
                    "TutoriUAU: algumas conquistas só aparecem quando você tropeça nelas. Design misterioso, não preguiça."
                ),
                color=discord.Color.green(),
            )
            embed.add_field(name=f"Página {page}/{len(chunks)}", value="\n\n".join(lines), inline=False)
            embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
            embeds.append(embed)
        return embeds

    async def _claim(self, user):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        achievements = self._evaluated(cursor, str(user.id))
        ready = [ach for ach in achievements if ach["done"] and not ach["claimed"]]
        if not ready:
            conn.close()
            return "Nenhuma conquista pronta. O TutoriUAU recomenda fazer algo heroico, ou pelo menos errar outro comando."

        for ach in ready:
            grant_reward(cursor, str(user.id), ach["reward"])
            cursor.execute(
                "INSERT OR REPLACE INTO player_achievements (user_id, achievement_id, claimed, claimed_at) VALUES (?, ?, 1, ?)",
                (str(user.id), ach["id"], int(time.time())),
            )
        conn.commit()
        conn.close()

        total_rewards = "\n".join(f"- **{ach['name']}**: {reward_text(ach['reward'])}" for ach in ready[:15])
        extra = "" if len(ready) <= 15 else f"\n...e mais {len(ready) - 15} conquistas. O botão trabalhou mais que muito NPC."
        return f"Conquistas resgatadas:\n{total_rewards}{extra}"

    async def _send_panel(self, target):
        user = target.author if hasattr(target, "author") else target.user
        embeds = await self._build_embeds(user)
        view = AchievementView(self, user, embeds)
        if hasattr(target, "send"):
            await target.send(embed=embeds[0], view=view)
        else:
            await target.response.send_message(embed=embeds[0], view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not isinstance(error, commands.CommandNotFound):
            return
        if not ctx.message or not ctx.message.content.lower().startswith("echo "):
            return
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_achievement_db(cursor)
        now = int(time.time())
        last = one(cursor, "SELECT value FROM player_stats WHERE user_id = ? AND stat = 'invalid_commands_last'", (str(ctx.author.id),), 0)
        if last and now - int(last) < 30:
            conn.close()
            return await ctx.send("Comando não encontrado. TutoriUAU: erro repetido rápido demais não conta como pesquisa científica.")
        add_stat(cursor, ctx.author.id, "invalid_commands", 1)
        cursor.execute(
            "INSERT OR REPLACE INTO player_stats (user_id, stat, value) VALUES (?, 'invalid_commands_last', ?)",
            (str(ctx.author.id), now),
        )
        total = one(cursor, "SELECT value FROM player_stats WHERE user_id = ? AND stat = 'invalid_commands'", (str(ctx.author.id),), 1)
        conn.commit()
        conn.close()
        await ctx.send("Comando não encontrado. TutoriUAU: isso aí ainda não existe, mas admirei a confiança.")

    @commands.group(name="conquistas", aliases=["conquista", "achievements"], invoke_without_command=True)
    async def conquistas_cmd(self, ctx):
        await self._send_panel(ctx)

    @conquistas_cmd.command(name="resgatar", aliases=["claim", "coletar"])
    async def resgatar_cmd(self, ctx):
        await ctx.send(await self._claim(ctx.author))

    @app_commands.command(name="conquistas", description="Mostra suas conquistas e permite resgatar recompensas.")
    async def conquistas_slash(self, interaction: discord.Interaction):
        await self._send_panel(interaction)


async def setup(bot):
    await bot.add_cog(Conquistas(bot))
