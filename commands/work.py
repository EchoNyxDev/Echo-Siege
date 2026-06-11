import discord
from discord.ext import commands
import sqlite3
import random
import os
import sys
import json
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

def carregar_chaves_aventuras():
    caminho = os.path.join(root_dir, "data", "adventures.json")
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            advs = json.load(f)
            return list(advs.keys()), advs
    except FileNotFoundError:
        return [], {}


def cortar(texto, limite=180):
    texto = str(texto or "").replace("\n", " ").strip()
    return texto if len(texto) <= limite else texto[: limite - 1] + "..."


def resumo_aventura(adv_id, adv):
    nodos = adv.get("nodos", {})
    start = nodos.get("start", {})
    combates = [n for n in nodos.values() if n.get("tipo") == "combate"]
    recompensas = [n for n in nodos.values() if n.get("tipo") == "recompensa"]
    inimigos = sum(len(n.get("inimigos", [])) for n in combates)
    ouro = max([n.get("gold", 0) for n in recompensas] or [0])
    xp = max([n.get("xp", 0) for n in recompensas] or [0])
    risco = "Baixo"
    if inimigos >= 3 or ouro >= 1000:
        risco = "Alto"
    elif inimigos >= 1 or ouro >= 500:
        risco = "Médio"
    gancho = cortar(start.get("texto", adv.get("nome", adv_id)), 150)
    return f"Risco: **{risco}** | Melhor pagamento: **{ouro:,} Gold / {xp:,} XP**\n{gancho}"

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
        
        cursor.execute("SELECT date_str, m1_id, m1_status, m2_id, m2_status, m3_id, m3_status, active_mission FROM daily_quests WHERE user_id = ?", (uid,))
        dados = cursor.fetchone()

        # Roda os contratos diários se for um dia novo ou não tiver registo
        if not dados or dados[0] != hoje_str:
            sorteadas = random.sample(keys, 3)
            cursor.execute("""
                INSERT INTO daily_quests (user_id, date_str, m1_id, m1_status, m2_id, m2_status, m3_id, m3_status, active_mission)
                VALUES (?, ?, ?, 0, ?, 0, ?, 0, NULL)
                ON CONFLICT(user_id) DO UPDATE SET
                date_str=excluded.date_str, m1_id=excluded.m1_id, m1_status=0,
                m2_id=excluded.m2_id, m2_status=0, m3_id=excluded.m3_id, m3_status=0, active_mission=NULL
            """, (uid, hoje_str, sorteadas[0], sorteadas[1], sorteadas[2]))
            conn.commit()
            
            cursor.execute("SELECT date_str, m1_id, m1_status, m2_id, m2_status, m3_id, m3_status, active_mission FROM daily_quests WHERE user_id = ?", (uid,))
            dados = cursor.fetchone()

        conn.close()

        _, m1, m1_st, m2, m2_st, m3, m3_st, ativa = dados

        concluidas = sum(1 for st in [m1_st, m2_st, m3_st] if st != 0)
        embed = discord.Embed(
            title="📋 Quadro de Contratos de Lugnica",
            description=(
                "**TutoriUAU:** \"Escolha um contrato, leia pelo menos duas linhas e depois finja que foi estratégia.\"\n"
                f"Contratos concluídos hoje: **{concluidas}/3**"
            ),
            color=discord.Color.orange()
        )
        
        # Adicionando a nova miniatura da Tutori-chan
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
