import discord
from discord.ext import commands
import sqlite3
import os
import sys
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils.adventure_catalog import (
    CATALOG_VERSION,
    TIER_INFO,
    load_adventure_catalog,
    select_daily_contracts,
)


def carregar_chaves_aventuras():
    adventures = load_adventure_catalog()
    return list(adventures.keys()), adventures

def cortar(texto, limite=180):
    texto = str(texto or "").replace("\n", " ").strip()
    return texto if len(texto) <= limite else texto[: limite - 1] + "..."

def obter_tier_aventura(adv):
    return int(adv.get("_meta", {}).get("tier", 1))

def resumo_aventura(adv_id, adv):
    nodos = adv.get("nodos", {})
    start = nodos.get("start", {})
    meta = adv.get("_meta", {})
    tier = obter_tier_aventura(adv)
    tier_data = TIER_INFO[tier]
    ouro = int(meta.get("max_gold", 0))
    xp = int(meta.get("max_xp", 0))
    level_max = tier_data["nivel_max"]
    faixa = f"{tier_data['nivel_min']}+" if level_max is None else f"{tier_data['nivel_min']}-{level_max}"
    origem = "Missão da Guilda" if meta.get("source") == "missions" else "Aventura narrativa"
    gancho = cortar(start.get("texto", adv.get("nome", adv_id)), 150)
    return (
        f"Risco: **{tier_data['nome']}** | Nível recomendado: **{faixa}**\n"
        f"Até **{ouro:,} Gold / {xp:,} XP** | {origem}\n{gancho}"
    )

class GuildBoardView(discord.ui.View):
    def __init__(self, ctx, m1, m2, m3, m1_st, m2_st, m3_st, adv_data):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.uid = str(ctx.author.id)
        
        # Cria botões dinamicamente baseados no status da missão
        # 0 = Disponível, 1 = Concluída (ou Falhada)
        
        b1 = discord.ui.Button(label="Aceitar Contrato 1", style=discord.ButtonStyle.primary, disabled=(m1_st != 0))
        b1.callback = self.make_callback(m1)
        self.add_item(b1)
        
        b2 = discord.ui.Button(label="Aceitar Contrato 2", style=discord.ButtonStyle.primary, disabled=(m2_st != 0))
        b2.callback = self.make_callback(m2)
        self.add_item(b2)
        
        b3 = discord.ui.Button(label="Aceitar Contrato 3", style=discord.ButtonStyle.primary, disabled=(m3_st != 0))
        b3.callback = self.make_callback(m3)
        self.add_item(b3)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    def make_callback(self, mission_id):
        async def callback(interaction: discord.Interaction):
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            
            # Verifica se já há uma missão ativa
            cursor.execute("SELECT active_mission FROM daily_quests WHERE user_id = ?", (self.uid,))
            row = cursor.fetchone()
            if row and row[0]:
                conn.close()
                return await interaction.response.send_message("❌ **TutoriUAU:** Você já pegou um contrato! Termina a sua `echo adventure` ativa antes de vir me encher o saco por mais papéis.", ephemeral=True)
            
            cursor.execute("UPDATE daily_quests SET active_mission = ? WHERE user_id = ?", (mission_id, self.uid))
            conn.commit()
            conn.close()
            
            nome = carregar_chaves_aventuras()[1].get(mission_id, {}).get("nome", mission_id)
            await interaction.response.edit_message(content=f"📜 **Contrato Assinado:** **{nome}** entrou no diário da party. Use `echo adventure` para sair da cidade e resolver o problema.", view=None, embed=None)
        return callback


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_quests(
            user_id TEXT PRIMARY KEY,
            date_str TEXT,
            m1_id TEXT, m1_status INTEGER DEFAULT 0,
            m2_id TEXT, m2_status INTEGER DEFAULT 0,
            m3_id TEXT, m3_status INTEGER DEFAULT 0,
            active_mission TEXT DEFAULT NULL
        )
        """)
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(daily_quests)")}
        if "catalog_version" not in columns:
            cursor.execute("ALTER TABLE daily_quests ADD COLUMN catalog_version INTEGER DEFAULT 1")
        conn.commit()
        conn.close()

    @commands.command(name="work", aliases=["trabalhar", "guilda", "missoes", "missões", "contratos"])
    async def work_cmd(self, ctx):
        keys, all_advs = carregar_chaves_aventuras()
        if len(keys) < 3:
            return await ctx.send("❌ **TutoriUAU:** O mural de missões está vazio. Avisa pro Dev acordar pra vida e programar mais aventuras no JSON.")

        hoje_str = datetime.now(BRT).strftime("%Y-%m-%d")
        uid = str(ctx.author.id)
        
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT date_str, m1_id, m1_status, m2_id, m2_status, m3_id, m3_status, active_mission, catalog_version FROM daily_quests WHERE user_id = ?", (uid,))
        dados = cursor.fetchone()

        cursor.execute("SELECT level FROM players WHERE user_id = ?", (uid,))
        p_lvl_data = cursor.fetchone()
        player_level = p_lvl_data[0] if p_lvl_data else 1

        needs_catalog_refresh = dados and int(dados[8] or 1) < CATALOG_VERSION and not dados[7]
        if not dados or dados[0] != hoje_str or needs_catalog_refresh:
            anteriores = [mission_id for mission_id in (dados[1], dados[3], dados[5])] if dados else []
            sorteadas = select_daily_contracts(all_advs, player_level, anteriores)
            cursor.execute("""
                INSERT INTO daily_quests (
                    user_id, date_str, m1_id, m1_status, m2_id, m2_status,
                    m3_id, m3_status, active_mission, catalog_version
                )
                VALUES (?, ?, ?, 0, ?, 0, ?, 0, NULL, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                date_str=excluded.date_str, m1_id=excluded.m1_id, m1_status=0,
                m2_id=excluded.m2_id, m2_status=0, m3_id=excluded.m3_id,
                m3_status=0, active_mission=NULL, catalog_version=excluded.catalog_version
            """, (uid, hoje_str, sorteadas[0], sorteadas[1], sorteadas[2], CATALOG_VERSION))
            conn.commit()
            
            cursor.execute("SELECT date_str, m1_id, m1_status, m2_id, m2_status, m3_id, m3_status, active_mission, catalog_version FROM daily_quests WHERE user_id = ?", (uid,))
            dados = cursor.fetchone()

        conn.close()

        _, m1, m1_st, m2, m2_st, m3, m3_st, ativa, _ = dados

        concluidas = sum(1 for st in [m1_st, m2_st, m3_st] if st != 0)
        embed = discord.Embed(
            title="📋 Quadro de Contratos de Lugnica",
            description=(
                f"**TutoriUAU:** \"Aqui estão os trabalhos disponíveis pro teu nível ({player_level}). Leia pelo menos duas linhas e depois finja que foi estratégia.\"\n"
                f"Contratos concluídos hoje: **{concluidas}/3**"
            ),
            color=discord.Color.orange()
        )
        
        # Adicionando a miniatura da Tutori-chan
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1493317042760056987/1513198454300606674/Tutori-chan.png?ex=6a26db61&is=6a2589e1&hm=d1fc19e4ac97c020cc6be2b440f928ae3e1b186c0d5afe7e46609f6d89146df1&")

        def status_str(st, mid):
            if ativa == mid: return "🏃 **[ATIVO NO MOMENTO]**"
            if st == 0: return "🟢 [Disponível]"
            return "✅ [Concluída/Fechada]"

        embed.add_field(name=f"1. {all_advs[m1]['nome']}", value=f"{status_str(m1_st, m1)}\n{resumo_aventura(m1, all_advs[m1])}", inline=False)
        embed.add_field(name=f"2. {all_advs[m2]['nome']}", value=f"{status_str(m2_st, m2)}\n{resumo_aventura(m2, all_advs[m2])}", inline=False)
        embed.add_field(name=f"3. {all_advs[m3]['nome']}", value=f"{status_str(m3_st, m3)}\n{resumo_aventura(m3, all_advs[m3])}", inline=False)

        if ativa:
            embed.set_footer(text="Você já tem um contrato ativo. Use `echo adventure` para entrar na cena e resolver essa péssima decisão.")
            await ctx.send(embed=embed)
        else:
            embed.set_footer(text="Botões curtos para celular, textos longos para quem ainda sabe ler. TutoriUAU equilibrou o caos.")
            view = GuildBoardView(ctx, m1, m2, m3, m1_st, m2_st, m3_st, all_advs)
            await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Work(bot))
