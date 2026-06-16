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
    from utils.player_bonuses import apply_reward_bonuses
    from utils.rewards import scale_combat_rewards
    from utils.gold_system import conceder_ouro_escalavel
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
except Exception:
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0): return gold, xp
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50): return gold, xp
    def conceder_ouro_escalavel(*args, **kwargs): return 0
    def dar_xp_jogador(*args): return 0, 1
    def dar_xp_heroi(*args): return 0, 1

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
            last_action INTEGER DEFAULT 0,
            loot_xp INTEGER DEFAULT 0
        )
    """)
    add_column_if_missing(cursor, "player_labyrinth", "last_action", "INTEGER DEFAULT 0")
    add_column_if_missing(cursor, "player_labyrinth", "loot_xp", "INTEGER DEFAULT 0")
    
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

def get_equipped_party(cursor, user_id):
    """Obtém os IDs dos heróis que estão atualmente equipados na Party do jogador"""
    cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
    p_data = cursor.fetchone()
    if not p_data or not p_data[0]: return []
    
    cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
    team = cursor.fetchone()
    time_ids = [p_data[0]] + [x for x in (team if team else []) if x is not None]
    return time_ids

def party_power_and_level(cursor, user_id):
    """Calcula a força e o nível médio baseado na Party ativa"""
    time_ids = get_equipped_party(cursor, user_id)
    if not time_ids: return 0, 1
    
    power = 0
    levels = []
    for hid in time_ids:
        cursor.execute("SELECT rarity, stars, level FROM heroes WHERE id = ?", (int(hid),))
        hero = cursor.fetchone()
        if hero:
            rarity, stars, level = hero
            power += (rarity or 1) * (stars or 1) * ((level or 1) + 10)
            levels.append(level or 1)
            
    avg_level = sum(levels) // len(levels) if levels else 1
    return int(power), avg_level

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
        
        power, avg_level = party_power_and_level(cursor, user_id)
        if power <= 0:
            conn.close()
            return await ctx.send("❌ Você precisa ter um Herói Líder equipado (`echo main <ID>`) para entrar no labirinto. O TutoriUAU não deixa figurante virar estatística.")

        cursor.execute("SELECT depth, hp, loot_gold, loot_gems, last_action, loot_xp FROM player_labyrinth WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO player_labyrinth (user_id, depth, hp, loot_gold, loot_gems, started_at, last_action, loot_xp) VALUES (?, 0, 100, 0, 0, ?, 0, 0)", (user_id, int(time.time())))
            row = (0, 100, 0, 0, 0, 0)

        depth, hp, loot_gold, loot_gems, last_action, loot_xp = row
        guild_id = str(ctx.guild.id) if ctx.guild else None

        # ==========================================
        # RETIRADA TÁTICA (SAIR E COLETAR)
        # ==========================================
        if acao in ["sair", "coletar", "fugir"]:
            # Usando os novos motores escalonáveis
            final_gold = conceder_ouro_escalavel(cursor, user_id, loot_gold, avg_level, guild_id)
            
            _, final_xp = scale_combat_rewards(0, loot_xp, avg_level)
            _, final_xp = apply_reward_bonuses(cursor, user_id, 0, final_xp)
            
            log_ups = ""
            if final_xp > 0:
                ups_p, lvl_p = dar_xp_jogador(cursor, user_id, final_xp)
                if ups_p > 0: log_ups += f"\n🆙 **Sua Conta** subiu para o Nível {lvl_p}!"
                
                party_ids = get_equipped_party(cursor, user_id)
                for hid in party_ids:
                    h_ups, h_lvl = dar_xp_heroi(cursor, hid, final_xp)
                    if h_ups > 0: 
                        log_ups += f"\n🌟 Um herói de sua party subiu para o Nível {h_lvl}!"
            
            # O Gold já é salvo no conceder_ouro_escalavel, atualizamos o resto
            cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (loot_gems, user_id))
            cursor.execute("DELETE FROM player_labyrinth WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            msg = f"🚪 Você escapou do labirinto e as riquezas foram devidamente tributadas.\n💰 **{final_gold:,} Gold** | ⭐ **{final_xp:,} XP** | 💎 **{loot_gems:,} Gems**\n\n*TutoriUAU: fugir com lucro chama-se estratégia.*"
            if log_ups: msg += log_ups
            return await ctx.send(msg)

        if last_action and int(time.time()) - int(last_action or 0) < LABYRINTH_COOLDOWN:
            ready_at = int(last_action) + LABYRINTH_COOLDOWN
            conn.close()
            return await ctx.send(f"⏳ O labirinto está mudando suas paredes. O caminho se abrirá novamente <t:{ready_at}:R>. *TutoriUAU: até parede aleatória tem agenda.*")

        depth += 1
        room = "boss" if depth % 5 == 0 else random.choices(ROOM_TYPES, weights=[38, 22, 12, 16, 12], k=1)[0]
        difficulty = 90 + depth * 45
        title = f"🌀 Labirinto Infinito - Profundidade {depth}"
        desc = ""
        item_line = ""

        # ==========================================
        # EVENTOS DAS SALAS
        # ==========================================
        if room == "monstro":
            chance = power / max(1, power + difficulty)
            if random.random() < chance:
                gain = random.randint(180, 360) + depth * 55
                gain_xp = random.randint(80, 150) + depth * 30
                loot_gold += gain
                loot_xp += gain_xp
                desc = f"Monstro derrotado. +{gain:,} Gold e +{gain_xp:,} XP acumulados."
            else:
                damage = random.randint(12, 28) + depth // 2
                hp -= damage
                desc = f"O monstro era ágil e bateu primeiro. HP do grupo: **{max(0, hp)}/100**."
                
        elif room == "tesouro":
            gain = random.randint(250, 600) + depth * 40
            gain_xp = random.randint(50, 100) + depth * 15
            gems = 1 if random.random() < 0.35 else 0
            loot_gold += gain
            loot_xp += gain_xp
            loot_gems += gems
            
            item = random.choice(MATERIALS)
            add_item(cursor, user_id, item, 1)
            item_line = f"Item encontrado: **{item.replace('_', ' ').title()}**."
            desc = f"Tesouro aberto. +{gain:,} Gold e +{gain_xp:,} XP acumulados."
            if gems > 0: desc += f" E também +{gems} Gem!"
            
        elif room == "mercador":
            cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
            gold_now = (cursor.fetchone() or [0])[0] or 0
            if gold_now >= 300:
                cursor.execute("UPDATE players SET gold = gold - 300 WHERE user_id = ?", (user_id,))
                loot_gems += 2
                desc = "Um mercador suspeito vendeu 2 Gems por 300 Gold. Barganha? Crime? Ambos?"
            else:
                desc = "Um mercador apareceu, viu sua carteira vazia e foi embora em silêncio. Humilhante."
                
        elif room == "armadilha":
            damage = random.randint(8, 24) + depth
            hp -= damage
            desc = f"Armadilha ativada! Espinhos do chão. HP do grupo: **{max(0, hp)}/100**.\n*TutoriUAU: placas de 'não pise' existem por um motivo.*"
            
        elif room == "evento":
            roll = random.choice(["heal", "gold", "gems", "xp"])
            if roll == "heal":
                hp = min(100, hp + 25)
                desc = "Uma fonte brilhante curou a party em 25 HP. Beber líquidos de masmorras foi aprovado desta vez."
            elif roll == "gold":
                gain = random.randint(150, 500) + depth * 20
                loot_gold += gain
                desc = f"Evento aleatório rendeu +{gain:,} Gold acumulado."
            elif roll == "xp":
                gain_xp = random.randint(150, 400) + depth * 15
                loot_xp += gain_xp
                desc = f"O grupo estudou inscrições antigas na parede. +{gain_xp:,} XP acumulado."
            else:
                loot_gems += 1
                desc = "Evento aleatório rendeu +1 Gem. O labirinto piscou para você, bizarro."
                
        else: # BOSS ROOM
            boss_power = difficulty * 1.35
            if power * random.uniform(0.85, 1.25) >= boss_power:
                gain = random.randint(900, 1600) + depth * 120
                gain_xp = random.randint(400, 800) + depth * 80
                loot_gold += gain
                loot_xp += gain_xp
                loot_gems += 3
                add_stat(cursor, user_id, "labyrinth_bosses", 1)
                desc = f"**Chefe Derrotado!** +{gain:,} Gold e +{gain_xp:,} XP acumulados. A fera dropou +3 Gems."
            else:
                hp -= random.randint(28, 48)
                desc = f"O Chefe do andar esmagou a linha de frente. HP do grupo: **{max(0, hp)}/100**."

        add_stat(cursor, user_id, "labyrinth_rooms", 1)

        # ==========================================
        # MORTE NO LABIRINTO (PERDA DE SAQUE)
        # ==========================================
        if hp <= 0:
            safe_gold = int(loot_gold * 0.25)
            safe_gems = int(loot_gems * 0.25)
            safe_xp = int(loot_xp * 0.25)
            
            final_gold = conceder_ouro_escalavel(cursor, user_id, safe_gold, avg_level, guild_id)
            
            _, final_xp = scale_combat_rewards(0, safe_xp, avg_level)
            _, final_xp = apply_reward_bonuses(cursor, user_id, 0, final_xp)
            
            log_ups = ""
            if final_xp > 0:
                ups_p, lvl_p = dar_xp_jogador(cursor, user_id, final_xp)
                if ups_p > 0: log_ups += f"\n🆙 **Sua Conta** subiu para o Nível {lvl_p}!"
                party_ids = get_equipped_party(cursor, user_id)
                for hid in party_ids:
                    h_ups, h_lvl = dar_xp_heroi(cursor, hid, final_xp)
                    if h_ups > 0: log_ups += f"\n🌟 Um herói de sua party subiu para o Nível {h_lvl}!"

            cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (safe_gems, user_id))
            cursor.execute("DELETE FROM player_labyrinth WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            
            msg = f"☠️ O grupo caiu de exaustão nas profundezas. As equipes de resgate cobraram 75% do seu saque.\n💰 **{final_gold:,} Gold** | ⭐ **{final_xp:,} XP** | 💎 **{safe_gems:,} Gems**\n\n*TutoriUAU: morrer é ruim para o lucro, anotem.*"
            if log_ups: msg += log_ups
            return await ctx.send(msg)

        # Salva o estado se sobreviveu
        cursor.execute("UPDATE player_labyrinth SET depth = ?, hp = ?, loot_gold = ?, loot_gems = ?, last_action = ?, loot_xp = ? WHERE user_id = ?", (depth, hp, loot_gold, loot_gems, int(time.time()), loot_xp, user_id))
        conn.commit()
        conn.close()

        # Mostra o status atual
        embed = discord.Embed(title=title, description=desc, color=discord.Color.dark_purple())
        embed.add_field(name="📜 Tipo de Sala", value=room.title(), inline=True)
        embed.add_field(name="❤️ HP da Party", value=f"{hp}/100", inline=True)
        embed.add_field(name="🎒 Loot Acumulado", value=f"{loot_gold:,} Gold\n{loot_xp:,} XP\n{loot_gems} Gems", inline=True)
        if item_line:
            embed.add_field(name="Achado", value=item_line, inline=False)
            
        embed.set_footer(text="Use `echo labirinto` para adentrar na próxima sala ou `echo labirinto sair` para garantir o saque.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Labirinto(bot))