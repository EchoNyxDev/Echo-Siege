import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.receitas import RECEITAS
except ModuleNotFoundError:
    RECEITAS = {}

class ForjaSelect(discord.ui.Select):
    def __init__(self, view_ref):
        self.view_ref = view_ref
        options = []
        
        for r_id, r_data in RECEITAS.items():
            options.append(
                discord.SelectOption(
                    label=r_data["nome"],
                    value=r_id,
                    description=r_data["desc"][:100],
                    emoji=r_data["emoji"]
                )
            )
            
        super().__init__(
            placeholder="Selecione um projeto na bigorna...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view_ref.ctx.author.id:
            return await interaction.response.send_message("❌ Apenas o ferreiro que abriu a forja pode usar as ferramentas.", ephemeral=True)
            
        self.view_ref.receita_selecionada = self.values[0]
        self.view_ref.atualizar_botoes()
        await interaction.response.edit_message(embed=self.view_ref.gerar_embed(), view=self.view_ref)

class ForjaView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.receita_selecionada = None
        
        self.select = ForjaSelect(self)
        self.add_item(self.select)
        
        self.btn_forjar_1 = discord.ui.Button(label="Forjar 1x", style=discord.ButtonStyle.success, emoji="🔨", disabled=True)
        self.btn_forjar_1.callback = self.forjar_1x
        self.add_item(self.btn_forjar_1)

    def obter_inventario(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ?", (str(self.ctx.author.id),))
        inv = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return inv

    def checar_ingredientes(self, receita, inv, qtd_craft=1):
        for ing, qtd_necessaria in receita["ingredientes"].items():
            if inv.get(ing, 0) < (qtd_necessaria * qtd_craft):
                return False
        return True

    def atualizar_botoes(self):
        if not self.receita_selecionada:
            self.btn_forjar_1.disabled = True
            return
            
        inv = self.obter_inventario()
        receita = RECEITAS[self.receita_selecionada]
        
        pode_forjar = self.checar_ingredientes(receita, inv, 1)
        self.btn_forjar_1.disabled = not pode_forjar

    def gerar_embed(self):
        embed = discord.Embed(
            title="⚒️ A Forja Arcana",
            description="Transforme materiais inúteis em equipamentos, consumíveis e tickets.\n*TutoriUAU: Não, não podes forjar uma namorada aqui.*",
            color=discord.Color.dark_orange()
        )
        
        if not self.receita_selecionada:
            embed.add_field(name="Status", value="Aguardando a seleção de um projeto no menu abaixo...")
            return embed
            
        receita = RECEITAS[self.receita_selecionada]
        inv = self.obter_inventario()
        
        embed.title = f"⚒️ Projeto: {receita['emoji']} {receita['nome']}"
        embed.description = f"*{receita['desc']}*\n\n**Requisitos para Fabricação:**"
        
        txt_reqs = ""
        for ing, qtd in receita["ingredientes"].items():
            qtd_possui = inv.get(ing, 0)
            status = "✅" if qtd_possui >= qtd else "❌"
            nome_ing = ing.replace('_', ' ').title()
            txt_reqs += f"{status} **{nome_ing}**: {qtd_possui}/{qtd}\n"
            
        embed.add_field(name="Materiais Necessários", value=txt_reqs, inline=False)
        return embed

    async def executar_forja(self, interaction: discord.Interaction, qtd_craft: int):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("❌ Esta não é a tua bigorna.", ephemeral=True)
            
        receita = RECEITAS[self.receita_selecionada]
        uid = str(self.ctx.author.id)
        
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        # Dupla verificação de segurança (Transação)
        cursor.execute("SELECT item_name, quantity FROM inventory WHERE user_id = ?", (uid,))
        inv = {row[0]: row[1] for row in cursor.fetchall()}
        
        if not self.checar_ingredientes(receita, inv, qtd_craft):
            conn.close()
            return await interaction.response.send_message("❌ Não tens materiais suficientes para isto! Farmar mais um bocado.", ephemeral=True)
            
        # Consome os ingredientes
        for ing, qtd_necessaria in receita["ingredientes"].items():
            gasto_total = qtd_necessaria * qtd_craft
            cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_name = ?", (gasto_total, uid, ing))
            
        # Limpa itens que ficaram com quantidade zero ou menor
        cursor.execute("DELETE FROM inventory WHERE user_id = ? AND quantity <= 0", (uid,))
        
        # Adiciona o item criado
        item_id = self.receita_selecionada
        cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (uid, item_id))
        item_existe = cursor.fetchone()
        
        if item_existe:
            cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qtd_craft, item_existe[0]))
        else:
            cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (uid, item_id, qtd_craft))
            
        conn.commit()
        conn.close()
        
        self.atualizar_botoes()
        embed = self.gerar_embed()
        embed.add_field(name="🎉 SUCESSO!", value=f"Você forjou **{qtd_craft}x {receita['emoji']} {receita['nome']}** com sucesso! Eles já estão na sua mochila.", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)

    async def forjar_1x(self, interaction: discord.Interaction):
        await self.executar_forja(interaction, 1)

class Forja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="forja", aliases=["craft", "forjar", "fabricar"])
    async def forja_cmd(self, ctx):
        if not RECEITAS:
            return await ctx.send("❌ O livro de receitas foi perdido. Fale com o Dev (`data/receitas.py` está vazio).")
            
        view = ForjaView(ctx)
        view.atualizar_botoes()
        await ctx.send(embed=view.gerar_embed(), view=view)

    @app_commands.command(name="forja", description="Abre a forja para converter materiais (lixo) em itens úteis.")
    async def forja_slash(self, interaction: discord.Interaction):
        class MockCtx:
            def __init__(self, inter):
                self.author = inter.user
                self.guild = inter.guild
        
        ctx = MockCtx(interaction)
        view = ForjaView(ctx)
        view.atualizar_botoes()
        await interaction.response.send_message(embed=view.gerar_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Forja(bot))