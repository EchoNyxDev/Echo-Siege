import discord
from discord.ext import commands
import sqlite3
import os
import sys

# Gambiarra para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.equipamentos import EQUIPAMENTOS
    from data.heroes import HEROES
except ModuleNotFoundError:
    EQUIPAMENTOS = {}
    HEROES = {}

class Equipamentos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        # Adiciona os 3 slots de equipamento em CADA herói (Ataque, Defesa, Livre)
        cursor.execute("PRAGMA table_info(heroes)")
        colunas = [info[1] for info in cursor.fetchall()]
        
        if "equip_atk" not in colunas: cursor.execute("ALTER TABLE heroes ADD COLUMN equip_atk TEXT")
        if "equip_def" not in colunas: cursor.execute("ALTER TABLE heroes ADD COLUMN equip_def TEXT")
        if "equip_livre" not in colunas: cursor.execute("ALTER TABLE heroes ADD COLUMN equip_livre TEXT")
        
        conn.commit()
        conn.close()

    @commands.command(name="equipar")
    async def equipar_cmd(self, ctx, heroi_id: int = None, *, nome_item: str = None):
        if not heroi_id or not nome_item:
            return await ctx.send("❌ Uso correto: `echo equipar <ID_DO_HEROI> <nome_do_item>`\nExemplo: `echo equipar 15 espada de ferro`")
        
        # Flexibilidade para o jogador digitar com espaços ou com underlines
        nome_db = nome_item.strip().lower().replace(" ", "_")
        if nome_db not in EQUIPAMENTOS:
            encontrado = False
            for key, val in EQUIPAMENTOS.items():
                if val["nome"].lower() == nome_item.lower():
                    nome_db = key
                    encontrado = True
                    break
            if not encontrado:
                return await ctx.send(f"❌ O item `{nome_item}` não é um equipamento válido. Vá na loja conferir o nome.")

        eq_data = EQUIPAMENTOS[nome_db]

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        # 1. Verifica se o usuário tem o item na mochila
        cursor.execute("SELECT id, quantity FROM inventory WHERE user_id = ? AND item_name = ? AND quantity > 0", (str(ctx.author.id), nome_db))
        inv_item = cursor.fetchone()
        
        if not inv_item:
            conn.close()
            return await ctx.send(f"❌ Você não tem nenhuma **{eq_data['nome']}** na sua mochila! Vá comprar ou farmar.")

        # 2. Verifica se o herói existe
        cursor.execute("SELECT equip_atk, equip_def, equip_livre, hero_id FROM heroes WHERE id = ? AND user_id = ?", (heroi_id, str(ctx.author.id)))
        hero_data = cursor.fetchone()
        
        if not hero_data:
            conn.close()
            return await ctx.send(f"❌ Você não possui nenhum herói com o ID `{heroi_id}`.")

        eq_atk, eq_def, eq_livre, hero_base_id = hero_data
        nome_heroi = HEROES.get(hero_base_id, {}).get("nome", "Herói")

        # 3. Lógica dos 3 Slots (Atk, Def, Livre)
        slot_alvo = None
        if eq_data["tipo"] == "atk":
            if not eq_atk: slot_alvo = "equip_atk"
            elif not eq_livre: slot_alvo = "equip_livre"
        elif eq_data["tipo"] == "def":
            if not eq_def: slot_alvo = "equip_def"
            elif not eq_livre: slot_alvo = "equip_livre"
        elif eq_data["tipo"] == "livre":
            if not eq_livre: slot_alvo = "equip_livre"

        if not slot_alvo:
            conn.close()
            return await ctx.send(f"❌ O herói **{nome_heroi}** não tem mais espaço livre para itens do tipo `{eq_data['tipo'].upper()}`. Desequipe algo primeiro!")

        # 4. Remove do inventário
        if inv_item[1] <= 1:
            cursor.execute("DELETE FROM inventory WHERE id = ?", (inv_item[0],))
        else:
            cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (inv_item[0],))

        # 5. Equipa no Herói
        cursor.execute(f"UPDATE heroes SET {slot_alvo} = ? WHERE id = ?", (nome_db, heroi_id))
        
        conn.commit()
        conn.close()

        await ctx.send(f"✅ Sucesso! Você equipou **{eq_data['nome']}** no slot `{slot_alvo.replace('equip_', '').upper()}` do herói **{nome_heroi}**.")

    @commands.command(name="desequipar")
    async def desequipar_cmd(self, ctx, heroi_id: int = None, slot: str = None):
        if not heroi_id or not slot:
            return await ctx.send("❌ Uso correto: `echo desequipar <ID_DO_HEROI> <atk/def/livre>`")
        
        slot = slot.lower()
        if slot not in ["atk", "def", "livre"]:
            return await ctx.send("❌ O slot deve ser `atk`, `def` ou `livre`.")

        coluna_slot = f"equip_{slot}"

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT {coluna_slot}, hero_id FROM heroes WHERE id = ? AND user_id = ?", (heroi_id, str(ctx.author.id)))
        hero_data = cursor.fetchone()

        if not hero_data:
            conn.close()
            return await ctx.send(f"❌ Você não possui nenhum herói com o ID `{heroi_id}`.")

        item_equipado, hero_base_id = hero_data
        nome_heroi = HEROES.get(hero_base_id, {}).get("nome", "Herói")

        if not item_equipado:
            conn.close()
            return await ctx.send(f"❌ O herói **{nome_heroi}** não tem nada equipado no slot `{slot.upper()}`.")

        # Devolve para o inventário
        cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(ctx.author.id), item_equipado))
        inv_item = cursor.fetchone()
        
        if inv_item:
            cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (inv_item[0],))
        else:
            cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (str(ctx.author.id), item_equipado))

        # Limpa o slot
        cursor.execute(f"UPDATE heroes SET {coluna_slot} = NULL WHERE id = ?", (heroi_id,))

        conn.commit()
        conn.close()

        eq_data = EQUIPAMENTOS.get(item_equipado, {"nome": item_equipado})
        await ctx.send(f"🔓 Você removeu **{eq_data['nome']}** do herói **{nome_heroi}**. O item voltou para a sua mochila!")

    @commands.command(name="equipamentos", aliases=["equips"])
    async def ver_equips(self, ctx, heroi_id: int = None):
        if not heroi_id:
            return await ctx.send("❌ Informe o ID do herói para ver os equipamentos. Ex: `echo equips 15`")

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT equip_atk, equip_def, equip_livre, hero_id FROM heroes WHERE id = ? AND user_id = ?", (heroi_id, str(ctx.author.id)))
        hero_data = cursor.fetchone()
        conn.close()

        if not hero_data:
            return await ctx.send(f"❌ Você não possui nenhum herói com o ID `{heroi_id}`.")

        e_atk, e_def, e_livre, hero_base_id = hero_data
        hero_info = HEROES.get(hero_base_id, {})
        nome_heroi = hero_info.get("nome", "Herói")
        emoji_heroi = hero_info.get("emoji", "❓")

        def formatar_slot(nome_db):
            if not nome_db: return "Vazio"
            eq = EQUIPAMENTOS.get(nome_db, {})
            nome = eq.get("nome", nome_db)
            emoji = eq.get("emoji", "⚙️")
            
            stats = []
            if eq.get("atk", 0) > 0: stats.append(f"+{eq['atk']} ATK")
            if eq.get("matk", 0) > 0: stats.append(f"+{eq['matk']} MATK")
            if eq.get("def", 0) > 0: stats.append(f"+{eq['def']} DEF")
            
            return f"{emoji} **{nome}** ({', '.join(stats)})"

        embed = discord.Embed(
            title=f"🎒 Equipamentos: {emoji_heroi} {nome_heroi}",
            color=discord.Color.teal()
        )
        embed.add_field(name="⚔️ Slot de Ataque", value=formatar_slot(e_atk), inline=False)
        embed.add_field(name="🛡️ Slot de Defesa", value=formatar_slot(e_def), inline=False)
        embed.add_field(name="✨ Slot Livre", value=formatar_slot(e_livre), inline=False)
        
        embed.set_footer(text="Use 'echo equipar <ID> <Item>' ou 'echo desequipar <ID> <Slot>'")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Equipamentos(bot))