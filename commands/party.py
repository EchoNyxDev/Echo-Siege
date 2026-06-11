import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import os
import sys

# Gambiarra para achar o heroes.py
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
except ModuleNotFoundError:
    HEROES = {}

# ==========================================
# FUNÇÕES DE APOIO
# ==========================================
def formatar_heroi_texto(hero_db_id):
    if not hero_db_id:
        return "Vazio"
        
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT hero_id, rarity, level FROM heroes WHERE id = ?", (int(hero_db_id),))
    hero = cursor.fetchone()
    conn.close()
    
    if not hero:
        return "Herói não encontrado"
        
    h_id, rarity, level = hero
    hero_data = HEROES.get(h_id, {})
    nome = hero_data.get("nome", "Bugado")
    emoji = hero_data.get("emoji", "❓")
    estrelas = "⭐" * rarity
    
    return f"{estrelas} {emoji} **{nome}** (Lvl {level})"


def formatar_pet_texto(pet_db_id):
    if not pet_db_id:
        return "Vazio"

    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT pet_id, pet_name, rarity, level FROM pets WHERE id = ?", (int(pet_db_id),))
    pet = cursor.fetchone()
    conn.close()
    if not pet:
        return "Pet não encontrado"
    pet_id, pet_name, rarity, level = pet
    try:
        from data.pets import PETS
    except Exception:
        PETS = {}
    pet_data = PETS.get(pet_id or "", {})
    nome = pet_name or pet_data.get("nome") or (pet_id or "Pet").replace("_", " ").title()
    emoji = pet_data.get("emoji", "🐾")
    return f"{emoji} **{nome}** | {'⭐' * (rarity or 1)} | Lv {level or 1}"

def gerar_embed_party(user: discord.User):
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT main_hero, main_pet FROM players WHERE user_id = ?", (str(user.id),))
    player = cursor.fetchone()
    main_hero = player[0] if player else None
    main_pet = player[1] if player and len(player) > 1 else None
    
    cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5, pet_slot FROM teams WHERE user_id = ?", (str(user.id),))
    team = cursor.fetchone()
    conn.close()

    if not team:
        team = (None, None, None, None, None)

    slot2, slot3, slot4, slot5, pet = team
    pet = pet or main_pet

    embed = discord.Embed(
        title=f"⚔️ Esquadrão de {user.name}",
        description=("Sua linha de frente para as Dungeons de Lugnica.\n"
                     "*Use os botões abaixo para colocar ou tirar membros do grupo.*"),
        color=discord.Color.dark_theme()
    )

    # Note que os emojis agora são neutros (sem prender o jogador a uma classe específica)
    embed.add_field(name="👑 Líder (Main)", value=formatar_heroi_texto(main_hero), inline=False)
    embed.add_field(name="👤 Slot 2", value=formatar_heroi_texto(slot2), inline=False)
    embed.add_field(name="👤 Slot 3", value=formatar_heroi_texto(slot3), inline=False)
    embed.add_field(name="👤 Slot 4", value=formatar_heroi_texto(slot4), inline=False)
    embed.add_field(name="👤 Slot 5", value=formatar_heroi_texto(slot5), inline=False)
    
    embed.add_field(name="🐾 Pet", value=formatar_pet_texto(pet), inline=False)

    embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
    embed.set_footer(text="TutoriUau • Para alterar o Líder, use 'echo main <ID>'. O resto você altera aqui.")
    return embed


# ==========================================
# LÓGICA DE EQUIPAR E VALIDAR
# ==========================================
async def equipar_heroi(interaction: discord.Interaction, user_id: int, slot_num: int, hero_db_id: int):
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    # Se ID for 0, limpa o slot
    if hero_db_id == 0:
        cursor.execute(f"UPDATE teams SET slot_{slot_num} = NULL WHERE user_id = ?", (str(user_id),))
        conn.commit()
        conn.close()
        return True, None

    # Verifica se o herói existe
    cursor.execute("SELECT hero_id FROM heroes WHERE id = ? AND user_id = ?", (hero_db_id, str(user_id)))
    hero = cursor.fetchone()

    if not hero:
        conn.close()
        return False, f"❌ Você não tem nenhum herói com o ID `{hero_db_id}`."

    # Verifica se já não está equipado (clonagem)
    cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
    main_hero = cursor.fetchone()[0]
    
    cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
    team = cursor.fetchone()
    
    equipados = [str(main_hero)] + [str(x) for x in team if x is not None]
    
    if str(hero_db_id) in equipados:
        conn.close()
        return False, "❌ Esse herói já está equipado no Líder ou em outro slot! Sem clones."

    # Equipa
    cursor.execute(f"UPDATE teams SET slot_{slot_num} = ? WHERE user_id = ?", (str(hero_db_id), str(user_id)))
    conn.commit()
    conn.close()
    return True, None


async def equipar_pet(interaction: discord.Interaction, user_id: int, pet_db_id: int):
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    if pet_db_id == 0:
        cursor.execute("UPDATE teams SET pet_slot = NULL WHERE user_id = ?", (str(user_id),))
        cursor.execute("UPDATE players SET main_pet = NULL WHERE user_id = ?", (str(user_id),))
        conn.commit()
        conn.close()
        return True, None
    cursor.execute("SELECT id FROM pets WHERE id = ? AND user_id = ?", (pet_db_id, str(user_id)))
    if not cursor.fetchone():
        conn.close()
        return False, f"❌ Você não tem nenhum pet com o ID `{pet_db_id}`."
    cursor.execute("UPDATE teams SET pet_slot = ? WHERE user_id = ?", (str(pet_db_id), str(user_id)))
    cursor.execute("UPDATE players SET main_pet = ? WHERE user_id = ?", (str(pet_db_id), str(user_id)))
    conn.commit()
    conn.close()
    return True, None


# ==========================================
# PAINEL 3: MODAL PARA DIGITAR ID MANUAL
# ==========================================
class EditSlotModal(discord.ui.Modal):
    def __init__(self, slot_num: int, user_id: int):
        super().__init__(title=f"ID Manual - Slot {slot_num}")
        self.slot_num = slot_num
        self.user_id = user_id
        
        self.hero_id_input = discord.ui.TextInput(
            label="ID do Herói (Número)",
            style=discord.TextStyle.short,
            placeholder="Ex: 15 (Digite 0 para esvaziar o slot)",
            required=True,
            max_length=5
        )
        self.add_item(self.hero_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        input_val = self.hero_id_input.value.strip()
        
        if not input_val.isdigit():
            await interaction.response.send_message("❌ O ID precisa ser um NÚMERO.", ephemeral=True)
            return
            
        sucesso, erro = await equipar_heroi(interaction, self.user_id, self.slot_num, int(input_val))
        
        if not sucesso:
            await interaction.response.send_message(erro, ephemeral=True)
            return

        # Volta pra tela principal
        novo_embed = gerar_embed_party(interaction.user)
        await interaction.response.edit_message(embed=novo_embed, view=PartyView(self.user_id))


# ==========================================
# PAINEL 2: DROPDOWN (MENU DE SELEÇÃO)
# ==========================================
class HeroSelectDropdown(discord.ui.Select):
    def __init__(self, user_id: int, slot_num: int):
        self.user_id = user_id
        self.slot_num = slot_num
        
        # Busca os heróis do jogador agrupados (para não poluir a lista com cópias)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MIN(id), hero_id, rarity, MAX(level) 
            FROM heroes 
            WHERE user_id = ? 
            GROUP BY hero_id 
            ORDER BY rarity DESC, MAX(level) DESC 
            LIMIT 24
        """, (str(user_id),))
        herois = cursor.fetchall()
        conn.close()

        options = [
            discord.SelectOption(label="[ Esvaziar Slot ]", value="0", description="Remove o herói do time", emoji="🗑️")
        ]

        for db_id, h_id, rarity, level in herois:
            h_data = HEROES.get(h_id, {})
            nome = h_data.get("nome", "Bugado")
            emoji = h_data.get("emoji", "❓")
            
            options.append(
                discord.SelectOption(
                    label=nome, 
                    value=str(db_id), 
                    description=f"Lvl {level} | {'⭐' * rarity}", 
                    emoji=emoji
                )
            )

        super().__init__(placeholder=f"Escolha um herói para o Slot {slot_num}...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selecionado_id = int(self.values[0])
        
        sucesso, erro = await equipar_heroi(interaction, self.user_id, self.slot_num, selecionado_id)
        
        if not sucesso:
            await interaction.response.send_message(erro, ephemeral=True)
            return

        # Volta pra tela principal
        novo_embed = gerar_embed_party(interaction.user)
        await interaction.response.edit_message(embed=novo_embed, view=PartyView(self.user_id))


class PetSelectDropdown(discord.ui.Select):
    def __init__(self, user_id: int):
        self.user_id = user_id
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, pet_id, pet_name, rarity, level
            FROM pets
            WHERE user_id = ?
            ORDER BY rarity DESC, level DESC, id ASC
            LIMIT 24
        """, (str(user_id),))
        pets = cursor.fetchall()
        conn.close()
        try:
            from data.pets import PETS
        except Exception:
            PETS = {}
        options = [discord.SelectOption(label="[ Remover Pet ]", value="0", description="Deixa o slot de pet vazio", emoji="🗑️")]
        for db_id, pet_id, pet_name, rarity, level in pets:
            pet_data = PETS.get(pet_id or "", {})
            nome = pet_name or pet_data.get("nome") or (pet_id or "Pet").replace("_", " ").title()
            options.append(discord.SelectOption(
                label=nome[:100],
                value=str(db_id),
                description=f"Lv {level or 1} | {'⭐' * (rarity or 1)}",
                emoji=pet_data.get("emoji", "🐾"),
            ))
        super().__init__(placeholder="Escolha o pet da party...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        sucesso, erro = await equipar_pet(interaction, self.user_id, int(self.values[0]))
        if not sucesso:
            return await interaction.response.send_message(erro, ephemeral=True)
        novo_embed = gerar_embed_party(interaction.user)
        await interaction.response.edit_message(embed=novo_embed, view=PartyView(self.user_id))

class ChooseHeroView(discord.ui.View):
    def __init__(self, user_id: int, slot_num: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.slot_num = slot_num
        
        # Adiciona o dropdown
        self.add_item(HeroSelectDropdown(user_id, slot_num))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="Digitar ID Manualmente", style=discord.ButtonStyle.secondary, emoji="⌨️")
    async def btn_manual(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditSlotModal(self.slot_num, self.user_id))

    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.danger, emoji="⬅️")
    async def btn_voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        novo_embed = gerar_embed_party(interaction.user)
        await interaction.response.edit_message(embed=novo_embed, view=PartyView(self.user_id))


class ChoosePetView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.add_item(PetSelectDropdown(user_id))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.danger, emoji="⬅️")
    async def btn_voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        novo_embed = gerar_embed_party(interaction.user)
        await interaction.response.edit_message(embed=novo_embed, view=PartyView(self.user_id))


# ==========================================
# PAINEL 1: VIEW PRINCIPAL DA PARTY
# ==========================================
class PartyView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Tira a mão! Essa party não é sua.", ephemeral=True)
            return False
        return True
        
    async def abrir_selecao(self, interaction: discord.Interaction, slot_num: int):
        embed_selecao = discord.Embed(
            title=f"Escolhendo Herói - Slot {slot_num}",
            description="Use a lista abaixo para selecionar quem vai ocupar essa posição, ou digite o ID manualmente.",
            color=discord.Color.blue()
        )
        view_selecao = ChooseHeroView(self.user_id, slot_num)
        await interaction.response.edit_message(embed=embed_selecao, view=view_selecao)

    @discord.ui.button(label="Slot 2", style=discord.ButtonStyle.primary, emoji="2️⃣")
    async def btn_slot2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.abrir_selecao(interaction, 2)

    @discord.ui.button(label="Slot 3", style=discord.ButtonStyle.primary, emoji="3️⃣")
    async def btn_slot3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.abrir_selecao(interaction, 3)

    @discord.ui.button(label="Slot 4", style=discord.ButtonStyle.primary, emoji="4️⃣")
    async def btn_slot4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.abrir_selecao(interaction, 4)

    @discord.ui.button(label="Slot 5", style=discord.ButtonStyle.primary, emoji="5️⃣")
    async def btn_slot5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.abrir_selecao(interaction, 5)

    @discord.ui.button(label="Pet", style=discord.ButtonStyle.success, emoji="🐾")
    async def btn_pet(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed_selecao = discord.Embed(
            title="Escolhendo Pet da Party",
            description="Selecione o pet que acompanha sua equipe. Ele também fica como `main_pet` do perfil.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed_selecao, view=ChoosePetView(self.user_id))

    @discord.ui.button(label="Limpar Time", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def btn_limpar(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE teams 
            SET slot_2 = NULL, slot_3 = NULL, slot_4 = NULL, slot_5 = NULL, pet_slot = NULL 
            WHERE user_id = ?
        """, (str(self.user_id),))
        cursor.execute("UPDATE players SET main_pet = NULL WHERE user_id = ?", (str(self.user_id),))
        conn.commit()
        conn.close()
        
        novo_embed = gerar_embed_party(interaction.user)
        await interaction.response.edit_message(embed=novo_embed, view=self)


# ==========================================
# COG PRINCIPAL
# ==========================================
class Party(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._verificar_db()

    def _verificar_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(teams)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if "pet_slot" not in colunas:
            cursor.execute("ALTER TABLE teams ADD COLUMN pet_slot TEXT")
            conn.commit()
        cursor.execute("PRAGMA table_info(players)")
        colunas_players = [coluna[1] for coluna in cursor.fetchall()]
        if "main_pet" not in colunas_players:
            cursor.execute("ALTER TABLE players ADD COLUMN main_pet TEXT")
            conn.commit()
        conn.close()

    @commands.command(name="party", aliases=["grupo", "time"])
    async def party_prefix(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM teams WHERE user_id = ?", (str(ctx.author.id),))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO teams (user_id) VALUES (?)", (str(ctx.author.id),))
            conn.commit()
        conn.close()

        embed = gerar_embed_party(ctx.author)
        view = PartyView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

    @app_commands.command(name="party", description="Gerencia o seu grupo de combate")
    async def party_slash(self, interaction: discord.Interaction):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM teams WHERE user_id = ?", (str(interaction.user.id),))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO teams (user_id) VALUES (?)", (str(interaction.user.id),))
            conn.commit()
        conn.close()

        embed = gerar_embed_party(interaction.user)
        view = PartyView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Party(bot))
