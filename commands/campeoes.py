import json
import random
import sqlite3
import time
from datetime import datetime
import os
import sys

import discord
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
except Exception:
    HEROES = {}

try:
    from data.equipamentos import EQUIPAMENTOS
except Exception:
    EQUIPAMENTOS = {}

try:
    from utils.player_bonuses import apply_reward_bonuses
    from utils.rewards import scale_combat_rewards
    from utils.combat import simular_combate_tatico
    from utils.gold_system import conceder_ouro_escalavel
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
except Exception:
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0): return gold, xp
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50): return gold, xp
    def simular_combate_tatico(*args, **kwargs): return True, "Combate Fantasma"
    def conceder_ouro_escalavel(*args, **kwargs): return 0
    def dar_xp_jogador(*args): return 0, 1
    def dar_xp_heroi(*args): return 0, 1


BOT_NAMES = [
    "Eco de Felt", "Eco de Reinhard", "Eco de Emilia", "Eco de Subaru", "Eco de Rem",
    "Eco de Ram", "Eco de Garfiel", "Eco de Beatrice", "Eco de Julius", "Eco de Crusch",
    "Eco de Anastasia", "Eco de Priscilla", "Eco de Wilhelm", "Eco de Roswaal", "Eco de Otto",
    "Eco de Pandora", "Eco de Puck", "Eco de Elsa", "Eco de Frederica", "Eco de Heinkel",
]


def week_id():
    return datetime.utcnow().strftime("%Y-W%U")


def add_column_if_missing(cursor, table, column, ddl):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def ensure_tower_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS champion_tower(
            user_id TEXT PRIMARY KEY,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            rating INTEGER DEFAULT 0,
            weekly_score INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            week_id TEXT DEFAULT '',
            last_fight INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS champion_defense_teams(
            user_id TEXT PRIMARY KEY,
            display_name TEXT,
            hero_ids TEXT DEFAULT '[]',
            hero_names TEXT DEFAULT '[]',
            power INTEGER DEFAULT 0,
            is_bot INTEGER DEFAULT 0,
            updated_at INTEGER DEFAULT 0
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings(
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)
    for column, ddl in {
        "display_name": "TEXT",
        "hero_ids": "TEXT DEFAULT '[]'",
        "hero_names": "TEXT DEFAULT '[]'",
        "power": "INTEGER DEFAULT 0",
        "is_bot": "INTEGER DEFAULT 0",
        "updated_at": "INTEGER DEFAULT 0",
    }.items():
        add_column_if_missing(cursor, "champion_defense_teams", column, ddl)
    cursor.execute("SELECT value FROM bot_settings WHERE key = 'champion_prestige_v1'")
    if not cursor.fetchone():
        cursor.execute("""
            UPDATE champion_tower
            SET rating = MAX(0, COALESCE(wins, 0) * 10 - COALESCE(losses, 0) * 3)
        """)
        cursor.execute(
            "INSERT INTO bot_settings (key, value) VALUES ('champion_prestige_v1', 'done')"
        )


def add_stat(cursor, user_id, stat, amount=1):
    cursor.execute("INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, ?, 0)", (str(user_id), stat))
    cursor.execute("UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = ?", (amount, str(user_id), stat))


def hero_name(hero_id):
    data = HEROES.get(hero_id, {})
    return f"{data.get('emoji', '✨')} {data.get('nome', hero_id)}"


def parse_json_list(raw):
    try:
        data = json.loads(raw or "[]")
        return data if isinstance(data, list) else []
    except Exception:
        return []


def build_tactical_entity(hid, h_id, stars, level, e_atk, e_def, e_livre, user_name):
    """Constrói uma entidade de combate tático utilizando os atributos reais escalonados."""
    h_data = HEROES.get(h_id, {})
    base_hp = h_data.get("hp", 100); base_atk = h_data.get("atk", 10); base_matk = h_data.get("matk", 10)
    base_df = h_data.get("def", 5); base_spd = max(1, h_data.get("spd", 10)); base_crt = h_data.get("crt", 5)

    mult = 1.0 + (0.15 * (stars - 1))
    
    hp = int((base_hp * mult) + (base_hp * 0.15 * (level - 1)))
    atk = int((base_atk * mult) + (base_atk * 0.15 * (level - 1)))
    matk = int((base_matk * mult) + (base_matk * 0.15 * (level - 1)))
    df = int((base_df * mult) + (base_df * 0.15 * (level - 1)))
    spd = int(base_spd + (base_spd * 0.02 * (level - 1))) 
    crt = base_crt + (level // 10)

    cl = h_data.get("classe", "neutro").lower()
    if cl == "atacante": atk += (level - 1) * 3
    elif cl == "mago": matk += (level - 1) * 3
    elif cl == "suporte": hp += (level - 1) * 10
    elif cl == "tank": df += (level - 1) * 5
    elif cl == "atirador": crt += (level - 1) * 1
    elif cl == "assassino": spd += (level - 1) * 1
    elif cl in ["lider", "líder"]:
        atk += (level - 1); matk += (level - 1); df += (level - 1); spd += (level - 1); hp += (level - 1) * 5
    
    for eq_name in [e_atk, e_def, e_livre]:
        if eq_name and eq_name in EQUIPAMENTOS:
            eq = EQUIPAMENTOS[eq_name]
            atk += eq.get("atk", 0)
            matk += eq.get("matk", 0)
            df += eq.get("def", 0)
            hp += eq.get("hp", 0)

    hab_id = h_data.get("habilidade")
    return {
        "id": str(hid),
        "nome": f"{h_data.get('nome', 'Herói')} ({user_name})",
        "classe": cl,
        "hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt,
        "stats": {"hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt},
        "habilidades": [hab_id] if hab_id else []
    }


class ChampionDefenseSelect(discord.ui.Select):
    def __init__(self, cog, user_id, heroes):
        self.cog = cog
        self.user_id = user_id
        options = []
        for db_id, hero_id, rarity, level in heroes[:25]:
            options.append(discord.SelectOption(
                label=HEROES.get(hero_id, {}).get("nome", hero_id)[:100],
                value=str(db_id),
                description=f"Lv {level or 1} | {'⭐' * (rarity or 1)}",
                emoji=HEROES.get(hero_id, {}).get("emoji", "✨"),
            ))
        super().__init__(
            placeholder="Escolha até 5 heróis para defender sua Torre...",
            min_values=1,
            max_values=min(5, len(options)),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("Essa defesa não é sua. TutoriUAU bloqueou o contrato.", ephemeral=True)
        await self.cog._register_defense_selected(interaction, self.values)


class ChampionDefenseView(discord.ui.View):
    def __init__(self, cog, user, heroes):
        super().__init__(timeout=180)
        self.user = user
        self.add_item(ChampionDefenseSelect(cog, user.id, heroes))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Abra sua própria defesa. Segurança da Torre agradece.", ephemeral=True)
            return False
        return True


class Campeoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_tower_db(cursor)
        self._seed_bots(cursor)
        conn.commit()
        conn.close()

    def _ensure_player(self, cursor, user_id):
        wid = week_id()
        cursor.execute(
            "INSERT OR IGNORE INTO champion_tower (user_id, rating, week_id) VALUES (?, 0, ?)",
            (str(user_id), wid),
        )
        cursor.execute("SELECT week_id FROM champion_tower WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        if row and row[0] != wid:
            cursor.execute("UPDATE champion_tower SET weekly_score = 0, current_streak = 0, week_id = ? WHERE user_id = ?", (wid, str(user_id)))

    def _seed_bots(self, cursor):
        hero_pool = [hid for hid in HEROES.keys() if hid != "id-nome"] or ["heroi_treino"]
        for idx, name in enumerate(BOT_NAMES, start=1):
            bot_id = f"champion_bot_{idx:02d}"
            rng = random.Random(idx * 777)
            ids = rng.sample(hero_pool, min(5, len(hero_pool))) if len(hero_pool) >= 5 else hero_pool[:]
            names = [hero_name(hid) for hid in ids]
            power = int(260 + (idx ** 1.35) * 95)
            cursor.execute(
                """
                INSERT OR REPLACE INTO champion_defense_teams
                (user_id, display_name, hero_ids, hero_names, power, is_bot, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (bot_id, name, json.dumps(ids), json.dumps(names), power, int(time.time())),
            )

    def _current_party(self, cursor, user_id, user_name):
        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
        player = cursor.fetchone()
        if not player or not player[0]:
            return [], 0
        cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
        team = cursor.fetchone() or []
        db_ids = [player[0]] + [slot for slot in team if slot]
        
        party_data = []
        power = 0
        for db_id in db_ids[:5]:
            try:
                cursor.execute("SELECT hero_id, rarity, stars, level, equip_atk, equip_def, equip_livre FROM heroes WHERE id = ? AND user_id = ?", (int(db_id), str(user_id)))
                row = cursor.fetchone()
                if not row: continue
                hero_id, rarity, stars, level, e_atk, e_def, e_livre = row
            except sqlite3.OperationalError:
                cursor.execute("SELECT hero_id, rarity, stars, level FROM heroes WHERE id = ? AND user_id = ?", (int(db_id), str(user_id)))
                row = cursor.fetchone()
                if not row: continue
                hero_id, rarity, stars, level = row
                e_atk, e_def, e_livre = None, None, None

            power += (rarity or 1) * (stars or 1) * ((level or 1) + 16)
            entity = build_tactical_entity(db_id, hero_id, stars, level, e_atk, e_def, e_livre, user_name)
            party_data.append(entity)
            
        return party_data, int(power)

    def _get_opponent_party(self, cursor, user_id, opponent_id, opponent_name, hero_ids_raw, is_bot, power):
        party_data = []
        hero_ids = parse_json_list(hero_ids_raw)
        if is_bot:
            lvl = max(1, int(power / 100))
            for idx, h_id in enumerate(hero_ids):
                entity = build_tactical_entity(f"B{idx}", h_id, 3, lvl, None, None, None, opponent_name)
                party_data.append(entity)
        else:
            for db_id in hero_ids[:5]:
                try:
                    cursor.execute("SELECT hero_id, rarity, stars, level, equip_atk, equip_def, equip_livre FROM heroes WHERE id = ? AND user_id = ?", (int(db_id), str(opponent_id)))
                    row = cursor.fetchone()
                    if not row: continue
                    h_id, rarity, stars, level, e_atk, e_def, e_livre = row
                except sqlite3.OperationalError:
                    cursor.execute("SELECT hero_id, rarity, stars, level FROM heroes WHERE id = ? AND user_id = ?", (int(db_id), str(opponent_id)))
                    row = cursor.fetchone()
                    if not row: continue
                    h_id, rarity, stars, level = row
                    e_atk, e_def, e_livre = None, None, None

                entity = build_tactical_entity(db_id, h_id, stars, level, e_atk, e_def, e_livre, opponent_name)
                party_data.append(entity)
        return party_data

    def _available_heroes(self, cursor, user_id):
        cursor.execute("""
            SELECT id, hero_id, rarity, level
            FROM heroes
            WHERE user_id = ?
            ORDER BY level DESC, rarity DESC, id ASC
            LIMIT 25
        """, (str(user_id),))
        return cursor.fetchall()

    def _power_from_ids(self, cursor, user_id, hero_db_ids):
        ids = []
        names = []
        power = 0
        for raw_id in hero_db_ids[:5]:
            cursor.execute("SELECT hero_id, rarity, stars, level FROM heroes WHERE id = ? AND user_id = ?", (int(raw_id), str(user_id)))
            row = cursor.fetchone()
            if not row:
                continue
            hero_id, rarity, stars, level = row
            ids.append(str(raw_id))
            names.append(hero_name(hero_id))
            power += (rarity or 1) * (stars or 1) * ((level or 1) + 16)
        return ids, names, int(power)

    def _opponent(self, cursor, user_id, my_power):
        cursor.execute("""
            SELECT user_id, display_name, hero_ids, hero_names, power, is_bot
            FROM champion_defense_teams
            WHERE user_id != ? AND power > 0
        """, (str(user_id),))
        rows = cursor.fetchall()
        if not rows:
            self._seed_bots(cursor)
            cursor.execute("""
                SELECT user_id, display_name, hero_ids, hero_names, power, is_bot
                FROM champion_defense_teams
                WHERE user_id != ? AND power > 0
            """, (str(user_id),))
            rows = cursor.fetchall()
        rows.sort(key=lambda row: abs((row[4] or 0) - my_power))
        return random.choice(rows[: min(8, len(rows))])

    async def _defesa(self, ctx):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_tower_db(cursor)
        heroes = self._available_heroes(cursor, user_id)
        conn.close()
        if not heroes:
            return await ctx.send("Você precisa ter heróis para registrar defesa na Torre.")
        embed = discord.Embed(
            title="🛡️ Registrar Defesa da Torre dos Campeões",
            description="Escolha de 1 a 5 heróis para lutar em seu lugar quando outros jogadores enfrentarem sua formação.\n*(Eles usarão as armas e níveis que têm agora!)*",
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed, view=ChampionDefenseView(self, ctx.author, heroes))

    async def _register_defense_selected(self, interaction, hero_db_ids):
        user_id = str(interaction.user.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_tower_db(cursor)
        heroes, names, power = self._power_from_ids(cursor, user_id, hero_db_ids)
        if power <= 0:
            conn.close()
            return await interaction.response.send_message("Seleção inválida. Esses heróis não estão na sua conta.", ephemeral=True)
        self._ensure_player(cursor, user_id)
        cursor.execute(
            """
            INSERT OR REPLACE INTO champion_defense_teams
            (user_id, display_name, hero_ids, hero_names, power, is_bot, updated_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (user_id, interaction.user.display_name, json.dumps(heroes), json.dumps(names), power, int(time.time())),
        )
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="🛡️ Defesa da Torre Registrada",
            description="Essa equipe agora pode aparecer como oponente de outros jogadores e proteger o seu Prestígio na Torre.",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Equipe Fixada", value="\n".join(names), inline=False)
        embed.add_field(name="Poder de Defesa", value=f"{power:,}", inline=True)
        embed.set_footer(text="TutoriUAU: agora sua party trabalha enquanto você finge que supervisiona.")
        await interaction.response.edit_message(embed=embed, view=None)

    async def _ranking(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_tower_db(cursor)
        wid = week_id()
        cursor.execute("""
            SELECT user_id, weekly_score, rating, wins
            FROM champion_tower
            WHERE week_id = ?
            ORDER BY weekly_score DESC, rating DESC
            LIMIT 10
        """, (wid,))
        rows = cursor.fetchall()
        conn.close()
        lines = [
            f"**{idx}º** <@{uid}> - {score:,} pts semanais | {rating} Prestígio | {wins} vitórias"
            for idx, (uid, score, rating, wins) in enumerate(rows, start=1)
        ]
        embed = discord.Embed(
            title="Torre dos Campeões - Ranking Semanal",
            description="\n".join(lines) if lines else "Ninguém lutou esta semana. Paz mundial temporária, que tédio.",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="campeoes", aliases=["campeões", "torrecampeoes", "torre_campeoes"])
    async def campeoes_cmd(self, ctx, acao: str = None):
        acao = (acao or "").lower()
        if acao in ["rank", "ranking", "top"]:
            return await self._ranking(ctx)
        if acao in ["defesa", "defender", "registrar"]:
            return await self._defesa(ctx)

        user_id = str(ctx.author.id)
        now = int(time.time())
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_tower_db(cursor)
        self._seed_bots(cursor)
        self._ensure_player(cursor, user_id)
        
        my_party_data, my_power = self._current_party(cursor, user_id, ctx.author.display_name)
        if my_power <= 0 or not my_party_data:
            conn.close()
            return await ctx.send("❌ Monte uma party (`echo main <ID>`) antes de entrar na Torre dos Campeões.")
            
        cursor.execute("SELECT 1 FROM champion_defense_teams WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return await ctx.send("❌ Registre sua defesa primeiro com `echo campeoes defesa`. Sem defesa, sem ranking. O contrato é chato assim.")

        cursor.execute("SELECT last_fight FROM champion_tower WHERE user_id = ?", (user_id,))
        last = (cursor.fetchone() or [0])[0] or 0
        if now - last < 600:
            conn.close()
            return await ctx.send(f"⏳ A Torre dos Campeões libera outra luta para você <t:{last + 600}:R>.")

        opponent_id, opponent_name, enemy_ids_raw, enemy_names_raw, enemy_power, is_bot = self._opponent(cursor, user_id, my_power)
        enemy_party_data = self._get_opponent_party(cursor, user_id, opponent_id, opponent_name, enemy_ids_raw, is_bot, enemy_power)
        
        if not enemy_party_data:
            conn.close()
            return await ctx.send("❌ A defesa inimiga está vazia ou foi corrompida. Tente novamente.")

        # ==================================
        # COMBATE TÁTICO AUTOMÁTICO (Assíncrono)
        # ==================================
        vitoria, log_batalha = simular_combate_tatico(my_party_data, enemy_party_data)
        won = vitoria

        cursor.execute("SELECT rating, current_streak, best_streak FROM champion_tower WHERE user_id = ?", (user_id,))
        rating, current_streak, best_streak = cursor.fetchone()
        rating = max(0, int(rating or 0))
        
        guild_id_str = str(ctx.guild.id) if ctx.guild else None

        if won:
            reward_progress = max(1, 1 + (rating / 10))
            prestige_gain = min(18, max(8, 8 + int(enemy_power / 500)))
            rating += prestige_gain
            current_streak += 1
            best_streak = max(best_streak, current_streak)
            weekly_gain = min(45, 18 + int(enemy_power / 120))
            
            # Gold Escalável via Sistema Central
            base_gold = 140 + int(enemy_power / 60)
            gold = conceder_ouro_escalavel(cursor, user_id, base_gold, int(reward_progress), guild_id_str)
            
            # XP via Sistema de Progressão
            base_xp = 45 + int(enemy_power / 140)
            _, xp = scale_combat_rewards(0, base_xp, reward_progress)
            _, xp = apply_reward_bonuses(cursor, user_id, 0, xp)
            
            dar_xp_jogador(cursor, user_id, xp)
            for h in my_party_data:
                dar_xp_heroi(cursor, int(h["id"]), xp)
                
            gem_chance = min(0.04, 0.01 + current_streak * 0.003)
            gems = 1 if random.random() < gem_chance else 0
            
            if gems > 0:
                cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (gems, user_id))
                
            cursor.execute("""
                UPDATE champion_tower
                SET wins = wins + 1, rating = ?, weekly_score = weekly_score + ?, current_streak = ?, best_streak = ?, last_fight = ?
                WHERE user_id = ?
            """, (rating, weekly_gain, current_streak, best_streak, now, user_id))
            
            add_stat(cursor, user_id, "tower_wins", 1)
            
            gem_text = f" e +{gems} Gem rara" if gems else ""
            result = (
                f"Vitória! +{prestige_gain} Prestígio, +{weekly_gain:,} pontos semanais.\n"
                f"💰 **+{gold:,} Gold** | ⭐ **+{xp:,} XP**{gem_text}."
            )
            color = discord.Color.green()
        else:
            prestige_loss = min(3, rating)
            rating = max(0, rating - prestige_loss)
            cursor.execute("""
                UPDATE champion_tower
                SET losses = losses + 1, rating = ?, current_streak = 0, last_fight = ?
                WHERE user_id = ?
            """, (rating, now, user_id))
            result = (
                f"Derrota. -{prestige_loss} Prestígio.\n"
                "A defesa inimiga fez hora extra e a sua equipa foi varrida."
            )
            color = discord.Color.red()

        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="🏆 Torre dos Campeões",
            description=f"O Esquadrão enfrentou a defesa de **{opponent_name}**{' [BOT]' if is_bot else ''}.\n\n{result}",
            color=color,
        )
        
        my_names = [e["nome"].split(' (')[0] for e in my_party_data]
        my_team_text = "\n".join(my_names)[:650] or "Sem heróis"
        
        enemy_names = parse_json_list(enemy_names_raw)
        enemy_team_text = "\n".join(enemy_names)[:650] or "Sem heróis"
        
        embed.add_field(
            name=f"Sua Equipe",
            value=f"{my_team_text}",
            inline=True,
        )
        embed.add_field(
            name=f"Defensores"[:256],
            value=f"{enemy_team_text}",
            inline=True,
        )
        
        embed.add_field(name="Prestígio Atual", value=str(rating), inline=False)
        
        # Limita o Log tático para não quebrar os 1024 caracteres do Discord
        log_seguro = log_batalha[:950] + "\n[...]" if len(log_batalha) > 950 else log_batalha
        embed.add_field(name="📜 Log de Batalha (Motor Tático)", value=f"```\n{log_seguro}\n```", inline=False)
        
        embed.set_footer(text="TutoriUAU: A IA não pode mais cometer violência sem ata.")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Campeoes(bot))