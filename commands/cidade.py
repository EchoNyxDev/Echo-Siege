import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

CITY_STAT_CAP = 100

class Cidade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cidades(
            guild_id TEXT PRIMARY KEY,
            nome TEXT DEFAULT 'Capital de Lugnica',
            hp INTEGER DEFAULT 100000,
            max_hp INTEGER DEFAULT 100000,
            moral INTEGER DEFAULT 100,
            suprimentos INTEGER DEFAULT 0,
            max_suprimentos INTEGER DEFAULT 5000,
            prosperidade INTEGER DEFAULT 0
        )
        """)
        self._clamp_city_caps(cursor)
        
        try:
            cursor.execute("ALTER TABLE server_config ADD COLUMN guild_id TEXT")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    def _clamp_city_caps(self, cursor):
        cursor.execute("UPDATE cidades SET moral = ? WHERE moral > ?", (CITY_STAT_CAP, CITY_STAT_CAP))
        cursor.execute("UPDATE cidades SET prosperidade = ? WHERE prosperidade > ?", (CITY_STAT_CAP, CITY_STAT_CAP))
        try:
            cursor.execute("UPDATE city_stats SET moral = ? WHERE moral > ?", (CITY_STAT_CAP, CITY_STAT_CAP))
            cursor.execute("UPDATE city_stats SET prosperidade = ? WHERE prosperidade > ?", (CITY_STAT_CAP, CITY_STAT_CAP))
        except sqlite3.OperationalError:
            pass

    # ==========================================
    # LAZY INITIALIZATION: Puxa ou Cria a Cidade
    # ==========================================
    def get_or_create_city(self, guild_id):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade, nome FROM cidades WHERE guild_id = ?", (str(guild_id),))
        city = cursor.fetchone()
        
        if not city:
            cursor.execute("""
                INSERT INTO cidades (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
                VALUES (?, 'Capital de Lugnica', 100000, 100000, 100, 0, 5000, 0)
            """, (str(guild_id),))
            conn.commit()

        self._clamp_city_caps(cursor)
        conn.commit()
        cursor.execute("SELECT hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade, nome FROM cidades WHERE guild_id = ?", (str(guild_id),))
        city = cursor.fetchone()
            
        conn.close()
        return city

    async def process_cidade(self, guild_id, guild_name):
        city = self.get_or_create_city(guild_id)
        hp, max_hp, moral, sup, max_sup, prosp, nome_cidade = city

        # ==========================================
        # CALCULANDO STATUS DA MORAL
        # ==========================================
        if moral > 70:
            moral_status = "🟩 Alta (+10% Gold e XP)"
        elif moral >= 50:
            moral_status = "🟨 Estável (Sem Buffs)"
        elif moral >= 25:
            moral_status = "🟧 Baixa (-10% Gold e XP)"
        elif moral > 0:
            moral_status = "🟥 Crítica (-20% Gold e XP)"
        else:
            moral_status = "☠️ REBELIÃO (A cidade entrou em colapso)"

        # ==========================================
        # CALCULANDO NÍVEL DA LOJA (PROSPERIDADE)
        # ==========================================
        if prosp >= 100:
            loja_nv = "Lugnica Dourada (+20% XP/Gold)"
        elif prosp >= 75:
            loja_nv = "Nível 3 (+15% XP/Gold)"
        elif prosp >= 50:
            loja_nv = "Nível 2 (+10% XP/Gold)"
        elif prosp >= 25:
            loja_nv = "Nível 1 (+5% XP/Gold)"
        else:
            loja_nv = "Básica (0% Buff)"

        # ==========================================
        # MONTANDO O EMBED
        # ==========================================
        embed = discord.Embed(
            title=f"🏰 {nome_cidade} ({guild_name})",
            description="Status atual da principal linha de defesa contra as invasões interdimensionais deste servidor.",
            color=discord.Color.gold()
        )

        embed.add_field(name="🛡️ Muralhas", value=f"**HP:** {hp}/{max_hp}", inline=True)
        embed.add_field(name="📦 Suprimentos", value=f"**Total:** {sup}/{max_sup}", inline=True)
        embed.add_field(name="", value="", inline=False)
        
        embed.add_field(name="✨ Prosperidade", value=f"**Pontos:** {prosp}/100\n**Comércio:** {loja_nv}", inline=True)
        embed.add_field(name="👥 Moral do Povo", value=f"**Pontos:** {moral}/100\n**Status:** {moral_status}", inline=True)

        embed.set_footer(text="TutoriUAU • Se a muralha cair, a culpa é sua. Só pra constar.")
        return embed

    @commands.command(name="cidade")
    async def cidade_prefix(self, ctx):
        if not ctx.guild:
            return await ctx.send("❌ **TutoriUAU:** Tu achas que existe muralha no chat privado? Usa isso num servidor de verdade!")
            
        embed = await self.process_cidade(ctx.guild.id, ctx.guild.name)
        await ctx.send(embed=embed)

    @app_commands.command(name="cidade", description="Mostra os status globais da capital deste servidor.")
    async def cidade_slash(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Comando apenas para servidores.", ephemeral=True)
            
        embed = await self.process_cidade(interaction.guild.id, interaction.guild.name)
        await interaction.response.send_message(embed=embed)

    # ==========================================
    # SISTEMA DE DOAÇÃO DE OURO -> SUPRIMENTOS
    # ==========================================
    @commands.command(name="doar")
    async def doar_ouro(self, ctx, quantidade: int = 0):
        if not ctx.guild:
            return await ctx.send("❌ Você precisa estar num servidor para doar para a cidade local.")
            
        if quantidade < 1000:
            return await ctx.send("❌ Você acha que a cidade se sustenta com esmolas? Doe pelo menos **1000 Gold** (rende 500 Suprimentos).")

        guild_id = str(ctx.guild.id)
        # Garante que a cidade existe
        self.get_or_create_city(guild_id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (str(ctx.author.id),))
        player = cursor.fetchone()

        if not player or player[0] < quantidade:
            conn.close()
            return await ctx.send(f"💸 Você não tem {quantidade} de Gold, seu liso. Vá farmar nas dungeons primeiro.")

        suprimentos_gerados = quantidade // 2

        cursor.execute("SELECT suprimentos, max_suprimentos FROM cidades WHERE guild_id = ?", (guild_id,))
        sup_atual, max_sup = cursor.fetchone()

        novo_sup = sup_atual + suprimentos_gerados
        if novo_sup > max_sup:
            suprimentos_gerados = max_sup - sup_atual
            novo_sup = max_sup
            if suprimentos_gerados <= 0:
                conn.close()
                return await ctx.send("📦 O armazém da cidade já está **LOTADO** de suprimentos. Guarde seu dinheiro pra outra coisa.")
            
            quantidade_gasta = suprimentos_gerados * 2
        else:
            quantidade_gasta = quantidade

        cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (quantidade_gasta, str(ctx.author.id)))
        cursor.execute("UPDATE cidades SET suprimentos = ? WHERE guild_id = ?", (novo_sup, guild_id))
        
        conn.commit()
        conn.close()

        await ctx.send(f"📦 Muito bem, {ctx.author.mention}. Você doou **{quantidade_gasta} Gold** e a guilda local gerou **{suprimentos_gerados} Suprimentos** para as obras.")

    # ==========================================
    # SISTEMA DE CONSERTO DA MURALHA
    # ==========================================
    @commands.command(name="consertar", aliases=["reparar", "reparos", "muralha"])
    async def consertar_muralha(self, ctx, suprimentos_usados: int = 0):
        if not ctx.guild: return await ctx.send("❌ Precisa estar num servidor.")
            
        if suprimentos_usados < 500:
            return await ctx.send("❌ Use no mínimo **500 Suprimentos** de cada vez (Restaura 10.000 HP). Pare de remendar com fita adesiva.")

        guild_id = str(ctx.guild.id)
        self.get_or_create_city(guild_id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT hp, max_hp, suprimentos FROM cidades WHERE guild_id = ?", (guild_id,))
        hp, max_hp, sup_atual = cursor.fetchone()

        if sup_atual < suprimentos_usados:
            conn.close()
            return await ctx.send(f"📦 O armazém só tem **{sup_atual} Suprimentos**. Não dá pra gastar {suprimentos_usados}. Façam doações!")

        if hp >= max_hp:
            conn.close()
            return await ctx.send("🛡️ A muralha daqui já está impecável! Quer consertar o que já tá perfeito?")

        hp_restaurado = suprimentos_usados * 20
        novo_hp = hp + hp_restaurado

        if novo_hp > max_hp:
            hp_restaurado = max_hp - hp
            novo_hp = max_hp
            suprimentos_reais = hp_restaurado // 20
        else:
            suprimentos_reais = suprimentos_usados

        cursor.execute("UPDATE cidades SET hp = ?, suprimentos = suprimentos - ? WHERE guild_id = ?", (novo_hp, suprimentos_reais, guild_id))
        conn.commit()
        conn.close()

        await ctx.send(f"🧱 {ctx.author.mention} liderou as obras nas muralhas locais! Gastamos **{suprimentos_reais} Suprimentos** e a cidade recuperou **{hp_restaurado} HP**.")

    # ==========================================
    # SISTEMA DE MELHORIA DA MURALHA (+MAX HP)
    # ==========================================
    @commands.command(name="melhorar", aliases=["evoluircidade", "evoluir_cidade", "melhorarcidade", "melhorar_cidade"])
    async def melhorar_muralha(self, ctx):
        if not ctx.guild: return await ctx.send("❌ Precisa estar num servidor.")
        custo = 2500
        guild_id = str(ctx.guild.id)
        
        self.get_or_create_city(guild_id)

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT hp, max_hp, suprimentos FROM cidades WHERE guild_id = ?", (guild_id,))
        hp, max_hp, sup_atual = cursor.fetchone()

        if sup_atual < custo:
            conn.close()
            return await ctx.send(f"❌ Para subir o nível da muralha local precisamos de **{custo} Suprimentos**. Atualmente temos apenas {sup_atual}.")

        novo_max = max_hp + 10000
        novo_hp = hp + 10000

        cursor.execute("UPDATE cidades SET hp = ?, max_hp = ?, suprimentos = suprimentos - ? WHERE guild_id = ?", (novo_hp, novo_max, custo, guild_id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🆙 MURALHA APRIMORADA!",
            description=f"Graças à ordem de {ctx.author.mention}, a engenharia do servidor {ctx.guild.name} avançou um nível!",
            color=discord.Color.green()
        )
        embed.add_field(name="Custo da Obra", value=f"-{custo} Suprimentos", inline=True)
        embed.add_field(name="Novo Status", value=f"**HP Máximo:** {novo_max:,}\n*(+10.000 HP Adicionado)*", inline=True)
        embed.set_footer(text="TutoriUAU • Finalmente vocês fizeram algo minimamente útil por aqui.")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Cidade(bot))
