import asyncio
import io
import json
import os
import sqlite3
import sys
import time
import unicodedata
import traceback
import aiohttp
import discord
from discord.ext import commands

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except Exception:
    Image = ImageDraw = ImageFont = ImageFilter = None

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from utils.hero_images import get_hero_attachment, get_hero_image_path
except ModuleNotFoundError:
    HEROES = {}

    def get_hero_attachment(hero_id, prefix="hero"):
        return None, None

    def get_hero_image_path(hero_id):
        return None

try:
    from data.pets import PETS
except ModuleNotFoundError:
    PETS = {}

try:
    from data.equipamentos import EQUIPAMENTOS
    from utils.equipment import get_equipment_bonus
    from utils.hero_stats import calculate_hero_stats
    from utils.skills import get_hero_skill_descriptions
except ModuleNotFoundError:
    EQUIPAMENTOS = {}

    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}

    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        stats = {
            stat: int(hero_data.get(stat, default))
            for stat, default in {
                "hp": 100,
                "atk": 10,
                "matk": 10,
                "def": 5,
                "spd": 10,
                "crt": 5,
            }.items()
        }
        stats["level"] = int(level or 1)
        return stats

    def get_hero_skill_descriptions(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        if not habilidade:
            return []
        return [{
            "tipo": "Base",
            "nome": habilidade.get("nome", "Habilidade") if isinstance(habilidade, dict) else str(habilidade),
            "descricao": habilidade.get("descricao", "") if isinstance(habilidade, dict) else "",
            "ativa": True,
        }]

# ===================================================
# SISTEMA DE CACHE DO AVATAR (Única coisa da internet)
# ===================================================
IMAGE_CACHE = {}
CACHE_EXPIRY = {}

# ===================================================
# CAMINHOS LOCAIS 100% OFFLINE (INSTANTÂNEOS)
# ===================================================
PROFILE_BACKGROUND_FILES = {
    "token_moldura_cidade_noturna": os.path.join(root_dir, "assets", "profile_themes", "cidade_noturna.png"),
    "token_moldura_minecraft": os.path.join(root_dir, "assets", "profile_themes", "minecraft.png"),
    "token_moldura_arvore_glacial": os.path.join(root_dir, "assets", "profile_themes", "arvore_glacial.png"),
    "token_moldura_flores_cerejeira": os.path.join(root_dir, "assets", "profile_themes", "flores_cerejeira.png"),
    "token_moldura_arquibancada_lotada": os.path.join(root_dir, "assets", "profile_themes", "arquibancada_lotada.png"),
    "token_moldura_gramado_noturno": os.path.join(root_dir, "assets", "profile_themes", "gramado_noturno.png"),
    "token_moldura_sala_de_imprensa": os.path.join(root_dir, "assets", "profile_themes", "sala_de_imprensa.png"),
    "token_moldura_taca_mundial": os.path.join(root_dir, "assets", "profile_themes", "taça_2026.png"),
}

# ===================================================
# DICIONÁRIO DE TEMAS (CORES E FONTES ÚNICAS)
# ===================================================
THEMES = {
    "default": {
        "panel_fill": (15, 18, 25, 130),
        "panel_outline": (60, 65, 80, 180),
        "title": (255, 255, 255, 255),
        "sub": (180, 190, 200, 255),
        "label": (130, 150, 170, 255),
        "value": (255, 255, 255, 255),
        "small": (210, 220, 230, 255),
        "font_file": "Roboto-Bold.ttf"
    },
    "token_moldura_cidade_noturna": {
        "panel_fill": (5, 0, 20, 130),
        "panel_outline": (0, 255, 255, 160), 
        "title": (0, 255, 255, 255),
        "sub": (255, 100, 255, 255),
        "label": (255, 0, 255, 255),
        "value": (255, 255, 255, 255),
        "small": (220, 255, 255, 255),
        "font_file": "Orbitron-Bold.ttf"
    },
    "token_moldura_minecraft": {
        "panel_fill": (0, 0, 0, 140),
        "panel_outline": (85, 255, 85, 180), 
        "title": (85, 255, 85, 255),
        "sub": (170, 170, 170, 255),
        "label": (85, 255, 255, 255), 
        "value": (255, 255, 85, 255), 
        "small": (255, 255, 255, 255),
        "font_file": "VT323-Regular.ttf"
    },
    "token_moldura_arvore_glacial": {
        "panel_fill": (0, 15, 30, 120),
        "panel_outline": (120, 200, 255, 150),
        "title": (220, 240, 255, 255),
        "sub": (160, 210, 255, 255),
        "label": (100, 180, 255, 255),
        "value": (255, 255, 255, 255),
        "small": (220, 240, 255, 255),
        "font_file": "Cinzel-Bold.ttf"
    },
    "token_moldura_flores_cerejeira": {
        "panel_fill": (30, 5, 15, 110),
        "panel_outline": (255, 160, 200, 150),
        "title": (255, 210, 230, 255),
        "sub": (255, 170, 190, 255),
        "label": (255, 150, 180, 255),
        "value": (255, 255, 255, 255),
        "small": (255, 230, 240, 255),
        "font_file": "PlayfairDisplay-Bold.ttf"
    },
    "token_moldura_arquibancada_lotada": {
        "panel_fill": (4, 18, 18, 145),
        "panel_outline": (80, 220, 160, 170),
        "title": (235, 255, 245, 255),
        "sub": (150, 235, 190, 255),
        "label": (120, 220, 170, 255),
        "value": (255, 255, 255, 255),
        "small": (220, 245, 235, 255),
        "font_file": "Roboto-Bold.ttf"
    },
    "token_moldura_gramado_noturno": {
        "panel_fill": (0, 8, 20, 150),
        "panel_outline": (110, 190, 255, 160),
        "title": (215, 240, 255, 255),
        "sub": (140, 210, 255, 255),
        "label": (100, 180, 255, 255),
        "value": (255, 255, 255, 255),
        "small": (220, 235, 255, 255),
        "font_file": "Roboto-Bold.ttf"
    },
    "token_moldura_sala_de_imprensa": {
        "panel_fill": (18, 18, 22, 155),
        "panel_outline": (235, 235, 235, 135),
        "title": (255, 255, 255, 255),
        "sub": (225, 225, 225, 255),
        "label": (170, 200, 230, 255),
        "value": (255, 255, 255, 255),
        "small": (230, 230, 230, 255),
        "font_file": "Roboto-Bold.ttf"
    },
    "token_moldura_taca_mundial": {
        "panel_fill": (28, 18, 4, 145),
        "panel_outline": (255, 210, 90, 180),
        "title": (255, 235, 160, 255),
        "sub": (255, 210, 120, 255),
        "label": (255, 200, 90, 255),
        "value": (255, 255, 255, 255),
        "small": (255, 238, 190, 255),
        "font_file": "Cinzel-Bold.ttf"
    }
}

# ===================================================
# FUNÇÕES UTILITÁRIAS SEGURAS
# ===================================================
def clean_text(text):
    """Remove emojis para evitar que o Pillow desenhe quadrados []."""
    if not text: return ""
    return "".join(c for c in str(text) if unicodedata.category(c) not in ('So', 'Cs', 'Cn'))

def normalize_lookup(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return "".join(char.lower() if char.isalnum() else " " for char in text).strip()

def estrelas(rarity, stars=1):
    rarity = int(rarity or 1)
    stars = int(stars or 1)
    return ("⭐" * rarity) + ("✦" * max(0, stars - 1))

def chunk_lines(lines, limit=950):
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    return chunks

def cosmetic_label(cosmetic_id):
    labels = {
        "token_moldura_cidade_noturna": "Cidade Noturna",
        "token_moldura_minecraft": "Minecraft",
        "token_moldura_arvore_glacial": "Árvore Glacial",
        "token_moldura_flores_cerejeira": "Flores de Cerejeira",
        "token_moldura_arquibancada_lotada": "Arquibancada Lotada",
        "token_moldura_gramado_noturno": "Gramado Noturno",
        "token_moldura_sala_de_imprensa": "Sala de Imprensa",
        "token_moldura_taca_mundial": "Taça Mundial",
        "token_titulo_pontual": "Pontual",
        "token_titulo_pontual_demais": "Pontual Demais",
        "token_titulo_bug_ambulante": "Bug Ambulante",
        "token_titulo_tutoriuau_aprovou": "TutoriUAU Aprovou",
        "token_titulo_patrocinador": "Patrocinador",
        "token_titulo_campeao_de_lugnica": "Campeão de Lugnica",
        "token_titulo_lenda_echo_cup": "Lenda da Echo Cup",
        "token_titulo_rei_dos_ecos": "Rei dos Ecos",
        "token_titulo_maior_tecnico_de_lugnica": "Maior Técnico de Lugnica",
        "token_titulo_campeao_do_mundo": "Campeão do Mundo",
    }
    return labels.get(cosmetic_id, str(cosmetic_id or "").replace("token_", "").replace("_", " ").title())

def get_active_cosmetic(cursor, user_id, cosmetic_type):
    try:
        cursor.execute(
            "SELECT cosmetic_id FROM player_cosmetics WHERE user_id = ? AND type = ? AND active = 1",
            (str(user_id), cosmetic_type),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.OperationalError:
        return None

def _trim(text, limit=40):
    text = str(text or "")
    return text if len(text) <= limit else text[: max(0, limit - 1)] + "..."

def _font_system_fallback(size, bold=False):
    if ImageFont is None: return None
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try: return ImageFont.truetype(path, size)
        except Exception: continue
    return ImageFont.load_default()

def _get_font(font_filename, size):
    font_path = os.path.join(root_dir, "assets", "fonts", font_filename)
    try:
        if os.path.isfile(font_path):
            return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"[ERRO FONTE] {e}")
    return _font_system_fallback(size, bold=True)

def _fit_cover(image, size):
    image = image.convert("RGB")
    target_w, target_h = size
    ratio = max(target_w / image.width, target_h / image.height)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", 1)
    image = image.resize(new_size, resample)
    left = (image.width - target_w) // 2
    top = (image.height - target_h) // 2
    return image.crop((left, top, left + target_w, top + target_h))

def _draw_panel(draw, box, fill=(4, 7, 12, 190), outline=(255, 255, 255, 100), radius=15, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_text_safe(draw, xy, text, font, fill, stroke_width=0, stroke_fill=None):
    """Garante que o Pillow não faça o bot crashar silenciosamente se a fonte não suportar bordas."""
    try:
        draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    except (AttributeError, NotImplementedError):
        # Se a fonte falhar com a borda, desenha sem borda.
        draw.text(xy, text, font=font, fill=fill)
    except Exception as e:
        print(f"[ERRO TEXTO] Falha ao desenhar '{text}': {e}")


class HeroisPaginator(discord.ui.View):
    def __init__(self, user, embeds):
        super().__init__(timeout=180)
        self.user = user
        self.embeds = embeds
        self.page = 0
        self._update_buttons()

    def _update_buttons(self):
        self.previous.disabled = self.page <= 0
        self.next.disabled = self.page >= len(self.embeds) - 1

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "Essa coleção pertence a outro invocador. Use `echo herois` para abrir a sua.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction, button):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary)
    async def next(self, interaction, button):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class EvoluirAllConfirmView(discord.ui.View):
    def __init__(self, cog, ctx):
        super().__init__(timeout=90)
        self.cog = cog
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Essa pilha de sacrifícios não é sua. Abra a própria fila de clonagem.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirmar Evolução All", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.cog._executar_evoluir_all(self.ctx.author)
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Evolução em massa cancelada. As cópias respiram aliviadas.", embed=None, view=None)


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._sync_catalog_rarities()

    def _sync_catalog_rarities(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'heroes'")
            if not cursor.fetchone():
                return
            for hero_id, hero_data in HEROES.items():
                if hero_id == "id-nome":
                    continue
                canonical_rarity = max(1, int(hero_data.get("raridade", 1) or 1))
                cursor.execute(
                    """
                    UPDATE heroes
                    SET rarity = ?
                    WHERE hero_id = ? AND COALESCE(rarity, 0) != ?
                    """,
                    (canonical_rarity, hero_id, canonical_rarity),
                )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
        finally:
            conn.close()

    def _rank_position(self, cursor, user_id, column):
        try:
            cursor.execute(f"SELECT {column} FROM players WHERE user_id = ?", (str(user_id),))
            row = cursor.fetchone()
            value = row[0] if row and row[0] is not None else 0
            cursor.execute(f"SELECT COUNT(*) + 1 FROM players WHERE COALESCE({column}, 0) > ?", (value,))
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return "?"

    async def _fetch_avatar(self, url):
        """Baixa apenas o Avatar usando Cache para velocidade."""
        if not url: return None
        now = time.time()
        if url in IMAGE_CACHE and now < CACHE_EXPIRY.get(url, 0):
            return IMAGE_CACHE[url]
            
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(url), headers=headers, timeout=5) as response:
                    if response.status == 200:
                        data = await response.read()
                        IMAGE_CACHE[url] = data
                        CACHE_EXPIRY[url] = now + 7200
                        return data
        except Exception: pass
        return None

    def _get_local_image(self, category, filename):
        """Lê imagens da máquina instantaneamente."""
        if not filename: return None

        if category == "herois_img":
            path = get_hero_image_path(filename)
            if path:
                try:
                    with open(path, "rb") as image_file:
                        return image_file.read()
                except OSError:
                    pass
        return None

    async def _profile_card(self, user, data):
        if Image is None or ImageDraw is None:
            print("[ERRO PERFIL] Pillow não instalado!")
            return None

        try:
            frame_id = data.get("frame")
            theme = THEMES.get(frame_id, THEMES["default"])
            
            # Lê as imagens offline e apenas o avatar online
            bg_bytes = None
            background_path = PROFILE_BACKGROUND_FILES.get(frame_id)
            if background_path and os.path.isfile(background_path):
                try:
                    with open(background_path, "rb") as background_file:
                        bg_bytes = background_file.read()
                except OSError:
                    bg_bytes = None
            hero_bytes = self._get_local_image("herois_img", data.get("hero_id"))
            avatar_bytes = await self._fetch_avatar(user.display_avatar.url if user.display_avatar else None)

            canvas_size = (1200, 675)
            
            # Base do Canvas (Escuro Padrão)
            card = Image.new("RGBA", canvas_size, (15, 18, 22, 255))
            
            if bg_bytes:
                bg_img = _fit_cover(Image.open(io.BytesIO(bg_bytes)), canvas_size).convert("RGBA")
                card.alpha_composite(bg_img)
                # Escurece levemente o fundo para a leitura ser perfeita
                card.alpha_composite(Image.new("RGBA", canvas_size, (0, 0, 0, 70)))

            draw = ImageDraw.Draw(card)
            
            font_filename = theme.get("font_file", "Roboto-Bold.ttf")
            f_title = _get_font(font_filename, 48)
            f_sub   = _get_font(font_filename, 26)
            f_label = _get_font(font_filename, 20)
            f_value = _get_font(font_filename, 28)
            f_small = _get_font(font_filename, 22)
            
            s_heavy = {"stroke_width": 2, "stroke_fill": (0, 0, 0, 255)}
            s_light = {"stroke_width": 1, "stroke_fill": (0, 0, 0, 255)}

            p_fill = theme["panel_fill"]
            p_outline = theme["panel_outline"]

            # CABEÇALHO
            _draw_panel(draw, (40, 40, 1160, 170), fill=p_fill, outline=p_outline, radius=20)
            
            if avatar_bytes:
                try:
                    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                    avatar = avatar.resize((100, 100), getattr(getattr(Image, "Resampling", Image), "LANCZOS", 1))
                    mask = Image.new("L", (100, 100), 0)
                    ImageDraw.Draw(mask).ellipse((0, 0, 99, 99), fill=255)
                    card.paste(avatar, (60, 55), mask)
                    draw.ellipse((58, 53, 162, 157), outline=p_outline, width=3)
                except Exception as e:
                    print(f"[ERRO PERFIL AVATAR] {e}")

            user_name_clean = clean_text(user.display_name)
            title_label = clean_text(cosmetic_label(data.get("title"))) if data.get("title") else "Aventureiro"
            
            draw_text_safe(draw, (190, 50), _trim(user_name_clean, 25), f_title, theme['title'], **s_heavy)
            draw_text_safe(draw, (195, 110), f"Titulo: {title_label}", f_sub, theme['sub'], **s_light)
            
            draw_text_safe(draw, (930, 50), f"Nivel {data['level']}", f_title, theme['title'], **s_heavy)
            draw_text_safe(draw, (930, 110), f"PvP {data['pvp_rating']} ELO", f_sub, theme['sub'], **s_light)

            # STATUS BOXES (Layout otimizado com respiro)
            stat_boxes = [
                ((40, 190, 390, 310), "CARTEIRA", f"{data['gold']:,} Gold\n{data['gems']:,} Gems"),
                ((410, 190, 750, 310), "RANKING", f"Ouro #{data['gold_rank']}\nNivel #{data['level_rank']}"),
                (
                    (40, 330, 390, 450),
                    "PROGRESSO PVE",
                    f"Arena: Andar {data['arena_record']}\nDungeon: D{data['dungeon_id']} - Área {data['dungeon_area']}",
                ),
                ((410, 330, 750, 450), "GUILDA", _trim(data["guild_text_clean"], 60)),
                (
                    (40, 470, 750, 590),
                    "EQUIPAMENTO PESSOAL",
                    f"Pet: {_trim(data['pet_text_clean'], 50)}\n"
                    f"Tema: {cosmetic_label(frame_id) if frame_id else 'Padrao'}",
                ),
            ]
            
            for box, label, value in stat_boxes:
                _draw_panel(draw, box, fill=p_fill, outline=p_outline, radius=15)
                draw_text_safe(draw, (box[0] + 20, box[1] + 15), clean_text(label), f_label, theme['label'], **s_heavy)
                for index, line in enumerate(str(value).splitlines()[:3]):
                    draw_text_safe(draw, (box[0] + 20, box[1] + 50 + index * 28), clean_text(_trim(line, 45)), f_small, theme['small'], **s_light)

            # HEROI PRINCIPAL BOX
            hero_box = (770, 190, 1160, 590)
            _draw_panel(draw, hero_box, fill=p_fill, outline=p_outline, radius=20)
            draw_text_safe(draw, (790, 205), "HEROI PRINCIPAL", f_label, theme['label'], **s_heavy)
            
            if hero_bytes:
                try:
                    hero_portrait = _fit_cover(Image.open(io.BytesIO(hero_bytes)), (350, 350)).convert("RGBA")
                    portrait_mask = Image.new("L", hero_portrait.size, 0)
                    ImageDraw.Draw(portrait_mask).rounded_rectangle((0, 0, hero_portrait.width - 1, hero_portrait.height - 1), radius=15, fill=255)
                    card.paste(hero_portrait, (790, 220), portrait_mask)
                    
                    portrait_overlay = Image.new("RGBA", (350, 70), (0, 0, 0, 190))
                    card.alpha_composite(portrait_overlay, (790, 500))
                    
                    draw_text_safe(draw, (810, 510), _trim(data['hero_name_clean'], 20), f_value, theme['value'], **s_heavy)
                    draw_text_safe(draw, (810, 545), f"Raridade: {data['hero_rarity']} Estrelas | Nivel {data['hero_level']}", f_small, theme['small'], **s_light)
                except Exception as e:
                    print(f"[ERRO PERFIL] Falha Herói Imagem: {e}")
                    hero_bytes = None
                    
            if not hero_bytes:
                # Ficha Minimalista substituta
                _draw_panel(draw, (790, 240, 1140, 570), fill=(0, 0, 0, 180), outline=p_outline, radius=15, width=1)
                draw_text_safe(draw, (810, 260), "IMAGEM NAO ENCONTRADA", f_sub, (180,180,180,255), **s_light)
                draw_text_safe(draw, (810, 320), f"Nome: {_trim(data['hero_name_clean'], 18)}", f_value, theme['value'], **s_heavy)
                draw_text_safe(draw, (810, 370), f"Serie: {_trim(data['hero_origem_clean'], 20)}", f_sub, theme['sub'], **s_light)
                draw_text_safe(draw, (810, 420), f"Nivel: {data['hero_level']}", f_sub, theme['sub'], **s_light)
                draw_text_safe(draw, (810, 470), f"Raridade: {data['hero_rarity']} Estrelas", f_sub, theme['sub'], **s_light)

            buffer = io.BytesIO()
            card.convert("RGB").save(buffer, format="PNG", optimize=True)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print("[ERRO FATAL NO PERFIL] Ocorreu uma exceção não tratada ao desenhar o cartão:")
            traceback.print_exc()
            return None

    @commands.command(name="perfil")
    async def perfil_prefix(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        
        try: cursor.execute("ALTER TABLE players ADD COLUMN pvp_rating INTEGER DEFAULT 1000")
        except: pass
        
        cursor.execute("""
            SELECT gold, gems, level, xp, main_hero, main_pet, arena_record, pvp_rating
            FROM players WHERE user_id = ?
        """, (str(ctx.author.id),))
        player = cursor.fetchone()
        
        if not player:
            conn.close()
            return await ctx.send("❌ Jogador não encontrado. Use `echo iniciar`.")

        gold, gems, level, xp, main_hero, main_pet, arena_record, pvp_rating = player
        
        gold_rank = self._rank_position(cursor, ctx.author.id, "gold")
        level_rank = self._rank_position(cursor, ctx.author.id, "level")
        arena_rank = self._rank_position(cursor, ctx.author.id, "arena_record")

        try:
            cursor.execute(
                "SELECT highest_dungeon, highest_area FROM dungeon_progress WHERE user_id = ?",
                (str(ctx.author.id),),
            )
            dungeon_progress = cursor.fetchone()
        except sqlite3.Error:
            dungeon_progress = None
        dungeon_id, dungeon_area = dungeon_progress or (1, 1)
        
        active_title = get_active_cosmetic(cursor, ctx.author.id, "title")
        active_frame = get_active_cosmetic(cursor, ctx.author.id, "frame")

        try:
            cursor.execute("""
                SELECT g.name, g.level, g.raid_score, m.role
                FROM player_guild_members m
                JOIN player_guilds g ON g.id = m.guild_id
                WHERE m.user_id = ?
            """, (str(ctx.author.id),))
            guild = cursor.fetchone()
        except: guild = None

        hero_name_clean = "Nenhum Heroi"
        hero_origem_clean = "Desconhecida"
        hero_level = 1
        hero_rarity = 1
        hero_id_clean = None
        
        if main_hero:
            try:
                cursor.execute("SELECT hero_id, rarity, level, stars FROM heroes WHERE id = ? AND user_id = ?", (int(main_hero), str(ctx.author.id)))
                hero_row = cursor.fetchone()
                if hero_row:
                    h_id, rarity, h_lvl, h_stars = hero_row
                    hero_base = HEROES.get(h_id, {})
                    hero_id_clean = h_id
                    hero_name_clean = clean_text(hero_base.get('nome', h_id))
                    hero_origem_clean = clean_text(hero_base.get('origem', 'Desconhecida'))
                    hero_rarity = rarity
                    hero_level = h_lvl
            except: pass

        pet_text_clean = "Nenhum Pet."
        if main_pet:
            try:
                cursor.execute("SELECT pet_id, pet_name, rarity, level FROM pets WHERE id = ? AND user_id = ?", (int(main_pet), str(ctx.author.id)))
                pet_row = cursor.fetchone()
                if pet_row:
                    p_id, p_name, rarity, p_lvl = pet_row
                    pet_base = PETS.get(p_id or "", {})
                    n_form = clean_text(p_name or pet_base.get('nome', p_id))
                    r_form = rarity or pet_base.get('raridade', 1)
                    pet_text_clean = f"{n_form} - {r_form}⭐ | Lv {p_lvl or 1}"
            except: pass

        guild_text_clean = "Sem guilda. Lobo solitario."
        if guild:
            guild_text_clean = f"{clean_text(guild[0])} - Nv {guild[1] or 1} | {clean_text(guild[3])} | Score {guild[2] or 0:,}"

        conn.close()

        card_data = {
            "gold": gold or 0, "gems": gems or 0, "level": level or 1, "xp": xp or 0,
            "arena_record": arena_record or 0, "pvp_rating": pvp_rating or 0,
            "dungeon_id": dungeon_id or 1, "dungeon_area": dungeon_area or 1,
            "gold_rank": gold_rank, "level_rank": level_rank, "arena_rank": arena_rank,
            "title": active_title, "frame": active_frame,
            "guild_text_clean": guild_text_clean, "pet_text_clean": pet_text_clean,
            "hero_name_clean": hero_name_clean, "hero_origem_clean": hero_origem_clean,
            "hero_level": hero_level, "hero_rarity": hero_rarity, "hero_id": hero_id_clean,
        }
        
        # CHAMA O RENDERIZADOR
        card_buffer = await self._profile_card(ctx.author, card_data)

        if card_buffer:
            # SUCESSO: MANDA SÓ A IMAGEM! Embed Limpo.
            embed = discord.Embed(color=discord.Color.from_rgb(18, 20, 26))
            filename = f"perfil_{ctx.author.id}.png"
            profile_file = discord.File(card_buffer, filename=filename)
            embed.set_image(url=f"attachment://{filename}")
            await ctx.send(embed=embed, file=profile_file)
        else:
            # FALHA: MANDA TEXTO PURO.
            embed = discord.Embed(title=f"Perfil de {ctx.author.display_name}", description="[ERRO] Imagem falhou. Mostrando texto.", color=discord.Color.red())
            embed.add_field(name="Carteira", value=f"Ouro: {gold:,} | Gemas: {gems:,}")
            embed.add_field(name="Herói", value=hero_name_clean, inline=False)
            embed.add_field(name="Dungeon", value=f"D{dungeon_id} - Área {dungeon_area}", inline=False)
            await ctx.send(embed=embed)


    @commands.command(name="herois", aliases=["heróis"])
    async def herois_prefix(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, hero_id, rarity, level, stars
            FROM heroes
            WHERE user_id = ?
            ORDER BY rarity DESC, level DESC, stars DESC, id ASC
            """,
            (str(ctx.author.id),),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return await ctx.send(f"{ctx.author.mention}, você ainda não tem heróis. Use `echo summon`.")

        grouped_by_hero = {}
        for db_id, hero_id, rarity, level, hero_stars in rows:
            entry = grouped_by_hero.setdefault(
                hero_id,
                {
                    "best": (db_id, hero_id, rarity or 1, level or 1, hero_stars or 1),
                    "count": 0,
                },
            )
            entry["count"] += 1
            current = entry["best"]
            if (level or 1, hero_stars or 1, rarity or 1, -db_id) > (
                current[3],
                current[4],
                current[2],
                -current[0],
            ):
                entry["best"] = (db_id, hero_id, rarity or 1, level or 1, hero_stars or 1)

        grouped = [
            (*entry["best"], entry["count"])
            for entry in grouped_by_hero.values()
        ]
        grouped.sort(key=lambda row: (row[2], row[3], row[4], -row[0]), reverse=True)

        embeds = []
        page_size = 10
        total_pages = (len(grouped) + page_size - 1) // page_size
        for page, start in enumerate(range(0, len(grouped), page_size), start=1):
            lines = []
            for db_id, hero_id, rarity, level, max_stars, count in grouped[start:start + page_size]:
                hero = HEROES.get(hero_id, {})
                dupe = f" ({count}x)" if count > 1 else ""
                lines.append(f"`ID {db_id}` {estrelas(rarity, max_stars)} {hero.get('emoji', '❔')} **{hero.get('nome', hero_id)}** - Lv {level}{dupe}")

            embed = discord.Embed(title=f"Heróis de {ctx.author.display_name}", color=discord.Color.blue())
            embed.add_field(name=f"Página {page}/{total_pages}", value="\n".join(lines), inline=False)
            embeds.append(embed)

        await ctx.send(embed=embeds[0], view=HeroisPaginator(ctx.author, embeds))

    @commands.command(name="main")
    async def main_prefix(self, ctx, hero_id: int = None):
        if not hero_id: return await ctx.send("Informe o ID do herói.")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT hero_id FROM heroes WHERE id = ? AND user_id = ?", (hero_id, str(ctx.author.id)))
        hero = cursor.fetchone()
        if not hero:
            conn.close()
            return await ctx.send("Herói não encontrado.")

        cursor.execute("UPDATE players SET main_hero = ? WHERE user_id = ?", (str(hero_id), str(ctx.author.id)))
        conn.commit()
        conn.close()
        data = HEROES.get(hero[0], {})
        await ctx.send(f"👑 **{data.get('nome', 'Herói')}** agora é seu herói principal.")

    def _busy_hero_ids(self, cursor, user_id):
        busy = set()

        def add(raw_id):
            if raw_id is not None:
                busy.add(str(raw_id))

        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            add(row[0])

        cursor.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'teams'")
        if cursor.fetchone():
            cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (user_id,))
            for slot_id in cursor.fetchone() or []:
                add(slot_id)

        for table_name, id_column in (
            ("champion_defense_teams", "hero_ids"),
            ("player_expeditions", "party_ids"),
        ):
            cursor.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table_name,))
            if not cursor.fetchone():
                continue
            cursor.execute(f"SELECT {id_column} FROM {table_name} WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            try:
                stored_ids = json.loads(row[0] or "[]") if row else []
            except (TypeError, ValueError, json.JSONDecodeError):
                stored_ids = []
            for stored_id in stored_ids:
                add(stored_id)

        return busy

    def _planejar_evoluir_all(self, cursor, user_id):
        cursor.execute("PRAGMA table_info(heroes)")
        hero_columns = {row[1] for row in cursor.fetchall()}
        equipment_columns = [
            column
            for column in ("equip_atk", "equip_def", "equip_livre")
            if column in hero_columns
        ]
        selected_columns = ["id", "hero_id", "rarity", "stars", "level"] + equipment_columns
        cursor.execute(
            f"SELECT {', '.join(selected_columns)} FROM heroes WHERE user_id = ?",
            (user_id,),
        )
        rows = cursor.fetchall()
        busy_ids = self._busy_hero_ids(cursor, user_id)

        grouped = {}
        for row in rows:
            grouped.setdefault(row[1], []).append(row)

        plan = []
        for hero_id, copies in grouped.items():
            if len(copies) < 2:
                continue
            hero_data = HEROES.get(hero_id, {})
            max_stage = max(1, int(hero_data.get("max_star", 7) or 7))
            target = max(copies, key=lambda row: (int(row[3] or 1), int(row[4] or 1), int(row[2] or 1), -int(row[0])))
            target_id = int(target[0])
            current_stage = max(1, int(target[3] or 1))
            if current_stage >= max_stage:
                continue

            donors = []
            for row in copies:
                donor_id = int(row[0])
                if donor_id == target_id or str(donor_id) in busy_ids:
                    continue
                if any(item for item in row[5:] if item):
                    continue
                donors.append(row)
            donors.sort(key=lambda row: (int(row[3] or 1), int(row[4] or 1), -int(row[0])))
            consume = donors[: max(0, max_stage - current_stage)]
            if not consume:
                continue

            new_stage = min(max_stage, current_stage + len(consume))
            plan.append({
                "target_id": target_id,
                "hero_id": hero_id,
                "name": hero_data.get("nome", hero_id),
                "rarity": max(1, int(hero_data.get("raridade", target[2] or 1) or 1)),
                "old_stage": current_stage,
                "new_stage": new_stage,
                "max_stage": max_stage,
                "donor_ids": [int(row[0]) for row in consume],
            })
        return plan

    async def _prompt_evoluir_all(self, ctx):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        plan = self._planejar_evoluir_all(cursor, user_id)
        conn.close()
        if not plan:
            return await ctx.send("Nenhuma evolução automática disponível. TutoriUAU conferiu as cópias e só achou apego emocional ou burocracia.")

        total_donors = sum(len(item["donor_ids"]) for item in plan)
        lines = [
            f"`ID {item['target_id']}` **{item['name']}**: {item['old_stage']}⭐ -> {item['new_stage']}⭐ ({len(item['donor_ids'])} cópia(s))"
            for item in plan[:12]
        ]
        if len(plan) > 12:
            lines.append(f"...e mais **{len(plan) - 12}** evolução(ões).")

        embed = discord.Embed(
            title="Evoluir All - Confirmação",
            description=(
                f"Vou evoluir **{len(plan)}** herói(s) e sacrificar **{total_donors}** cópia(s) livres.\n"
                "Não uso herói na party, defesa dos Campeões, expedição ou com equipamento."
            ),
            color=discord.Color.orange(),
        )
        embed.add_field(name="Prévia", value="\n".join(lines)[:1024], inline=False)
        embed.set_footer(text="TutoriUAU: botão vermelho. Sempre leia antes de apertar o botão vermelho.")
        await ctx.send(embed=embed, view=EvoluirAllConfirmView(self, ctx))

    def _executar_evoluir_all(self, user):
        user_id = str(user.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            plan = self._planejar_evoluir_all(cursor, user_id)
            if not plan:
                conn.rollback()
                return discord.Embed(
                    title="Evoluir All",
                    description="Nada para evoluir agora. As cópias sumiram, ficaram ocupadas ou o destino mudou.",
                    color=discord.Color.red(),
                )

            evolved = 0
            consumed = 0
            for item in plan:
                cursor.execute(
                    "UPDATE heroes SET rarity = ?, stars = ? WHERE id = ? AND user_id = ?",
                    (item["rarity"], item["new_stage"], item["target_id"], user_id),
                )
                if cursor.rowcount != 1:
                    continue
                for donor_id in item["donor_ids"]:
                    cursor.execute("DELETE FROM heroes WHERE id = ? AND user_id = ?", (donor_id, user_id))
                    consumed += cursor.rowcount
                evolved += 1

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats(
                    user_id TEXT NOT NULL,
                    stat TEXT NOT NULL,
                    value INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, stat)
                )
            """)
            cursor.execute(
                "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, 'hero_evolutions', 0)",
                (user_id,),
            )
            cursor.execute(
                "UPDATE player_stats SET value = value + ? WHERE user_id = ? AND stat = 'hero_evolutions'",
                (consumed, user_id),
            )
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            return discord.Embed(title="Evoluir All falhou", description=f"Não consegui concluir: `{exc}`", color=discord.Color.red())
        finally:
            conn.close()

        lines = [
            f"`ID {item['target_id']}` **{item['name']}**: {item['old_stage']}⭐ -> {item['new_stage']}⭐"
            for item in plan[:12]
        ]
        if len(plan) > 12:
            lines.append(f"...e mais **{len(plan) - 12}**.")
        embed = discord.Embed(
            title="Evoluir All concluído",
            description=f"**{evolved}** herói(s) evoluídos. **{consumed}** cópia(s) sacrificadas.",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Resultado", value="\n".join(lines)[:1024], inline=False)
        embed.set_footer(text="TutoriUAU: produção em massa de estrelas. Sindicatos mágicos foram consultados superficialmente.")
        return embed

    @commands.command(name="evoluir", aliases=["evolucao", "evolução"])
    async def evoluir_prefix(self, ctx, hero_db_id: str = None):
        if not hero_db_id:
            return await ctx.send("Informe o ID do herói principal da evolução. Exemplo: `echo evoluir 15`.")

        if str(hero_db_id).lower() in {"all", "todos", "tudo"}:
            return await self._prompt_evoluir_all(ctx)

        try:
            hero_db_id = int(hero_db_id)
        except (TypeError, ValueError):
            return await ctx.send("Use um ID numérico ou `echo evoluir all` para evoluir em massa.")

        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("PRAGMA table_info(heroes)")
            hero_columns = {row[1] for row in cursor.fetchall()}
            equipment_columns = [
                column
                for column in ("equip_atk", "equip_def", "equip_livre")
                if column in hero_columns
            ]
            selected_columns = ["id", "hero_id", "rarity", "stars", "level"] + equipment_columns
            cursor.execute(
                f"SELECT {', '.join(selected_columns)} FROM heroes WHERE id = ? AND user_id = ?",
                (hero_db_id, user_id),
            )
            target = cursor.fetchone()
            if not target:
                conn.rollback()
                return await ctx.send("Esse ID não pertence a nenhum herói da sua conta.")

            _, hero_id, stored_rarity, current_stage, hero_level = target[:5]
            target_equipment = [item for item in target[5:] if item]
            hero_data = HEROES.get(hero_id, {})
            hero_name = hero_data.get("nome", hero_id)
            canonical_rarity = max(1, int(hero_data.get("raridade", stored_rarity or 1) or 1))
            current_stage = max(1, int(current_stage or 1))
            max_stage = max(1, int(hero_data.get("max_star", 7) or 7))

            if current_stage >= max_stage:
                conn.rollback()
                return await ctx.send(
                    f"**{hero_name}** já está no estágio máximo **{current_stage}/{max_stage}**. "
                    "TutoriUAU tentou colocar mais brilho, mas o universo recusou."
                )

            cursor.execute(
                f"""
                SELECT {', '.join(selected_columns)}
                FROM heroes
                WHERE user_id = ? AND hero_id = ? AND id != ?
                """,
                (user_id, hero_id, hero_db_id),
            )
            duplicates = cursor.fetchall()
            if not duplicates:
                conn.rollback()
                return await ctx.send(
                    f"Você precisa de outra cópia de **{hero_name}** para evoluir o `ID {hero_db_id}`. "
                    "A amizade ajuda, mas o sistema exige papelada duplicada."
                )

            busy_reasons = {}

            def mark_busy(raw_id, reason):
                if raw_id is None:
                    return
                key = str(raw_id)
                busy_reasons.setdefault(key, []).append(reason)

            cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (user_id,))
            main_row = cursor.fetchone()
            if main_row:
                mark_busy(main_row[0], "herói principal")

            cursor.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'teams'")
            if cursor.fetchone():
                cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (user_id,))
                team_row = cursor.fetchone()
                for slot_id in team_row or []:
                    mark_busy(slot_id, "party")

            for table_name, id_column, reason in (
                ("champion_defense_teams", "hero_ids", "defesa dos Campeões"),
                ("player_expeditions", "party_ids", "expedição"),
            ):
                cursor.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                    (table_name,),
                )
                if not cursor.fetchone():
                    continue
                cursor.execute(f"SELECT {id_column} FROM {table_name} WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                try:
                    stored_ids = json.loads(row[0] or "[]") if row else []
                except (TypeError, ValueError, json.JSONDecodeError):
                    stored_ids = []
                for stored_id in stored_ids:
                    mark_busy(stored_id, reason)

            safe_duplicates = []
            blocked_details = []
            for duplicate in duplicates:
                duplicate_id = duplicate[0]
                duplicate_equipment = [item for item in duplicate[5:] if item]
                reasons = list(busy_reasons.get(str(duplicate_id), []))
                if duplicate_equipment:
                    reasons.append("equipamentos")
                if reasons:
                    blocked_details.append(f"`ID {duplicate_id}`: {', '.join(dict.fromkeys(reasons))}")
                    continue
                safe_duplicates.append(duplicate)

            if not safe_duplicates:
                conn.rollback()
                details = "\n".join(blocked_details[:8])
                return await ctx.send(
                    f"Você possui cópia de **{hero_name}**, mas nenhuma está livre para sacrifício.\n"
                    f"{details}\n"
                    "Retire a cópia da party/defesa, espere a expedição ou desequipe os itens. "
                    "TutoriUAU se recusa a triturar patrimônio sem aviso."
                )

            donor = min(
                safe_duplicates,
                key=lambda row: (int(row[3] or 1), int(row[4] or 1), -int(row[0])),
            )
            donor_id = int(donor[0])
            donor_stage = max(1, int(donor[3] or 1))
            donor_level = max(1, int(donor[4] or 1))
            new_stage = current_stage + 1

            target_bonuses = [
                get_equipment_bonus(cursor, user_id, item_name, EQUIPAMENTOS)
                for item_name in target_equipment
            ]
            old_stats = calculate_hero_stats(
                hero_data,
                stars=current_stage,
                level=hero_level,
                equipment_bonuses=target_bonuses,
            )
            new_stats = calculate_hero_stats(
                hero_data,
                stars=new_stage,
                level=hero_level,
                equipment_bonuses=target_bonuses,
            )
            old_skills = get_hero_skill_descriptions(
                hero_data,
                stars=current_stage,
                rarity=canonical_rarity,
            )
            new_skills = get_hero_skill_descriptions(
                hero_data,
                stars=new_stage,
                rarity=canonical_rarity,
            )
            active_before = {
                (skill.get("tipo"), skill.get("nome"))
                for skill in old_skills
                if skill.get("ativa")
            }
            unlocked = [
                skill
                for skill in new_skills
                if skill.get("ativa") and (skill.get("tipo"), skill.get("nome")) not in active_before
            ]

            cursor.execute(
                "UPDATE heroes SET rarity = ?, stars = ? WHERE id = ? AND user_id = ?",
                (canonical_rarity, new_stage, hero_db_id, user_id),
            )
            if cursor.rowcount != 1:
                raise sqlite3.DatabaseError("o herói principal mudou durante a evolução")

            cursor.execute(
                "DELETE FROM heroes WHERE id = ? AND user_id = ?",
                (donor_id, user_id),
            )
            if cursor.rowcount != 1:
                raise sqlite3.DatabaseError("a cópia de evolução não pôde ser consumida")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats(
                    user_id TEXT NOT NULL,
                    stat TEXT NOT NULL,
                    value INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, stat)
                )
            """)
            cursor.execute(
                "INSERT OR IGNORE INTO player_stats (user_id, stat, value) VALUES (?, 'hero_evolutions', 0)",
                (user_id,),
            )
            cursor.execute(
                "UPDATE player_stats SET value = value + 1 WHERE user_id = ? AND stat = 'hero_evolutions'",
                (user_id,),
            )
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            return await ctx.send(f"Não consegui concluir a evolução: `{exc}`")
        finally:
            conn.close()

        embed = discord.Embed(
            title=f"✨ Evolução concluída — {hero_name}",
            description=(
                f"O `ID {hero_db_id}` avançou do estágio **{current_stage}/{max_stage}** "
                f"para **{new_stage}/{max_stage}**.\n"
                f"A cópia `ID {donor_id}` (estágio {donor_stage}, nível {donor_level}) foi consumida."
            ),
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Raridade Base",
            value=f"{'⭐' * canonical_rarity} — a raridade original não muda com a evolução.",
            inline=False,
        )
        embed.add_field(
            name="Atributos",
            value=(
                f"HP: **{old_stats.get('hp', 0):,} → {new_stats.get('hp', 0):,}** | "
                f"ATK: **{old_stats.get('atk', 0):,} → {new_stats.get('atk', 0):,}**\n"
                f"MATK: **{old_stats.get('matk', 0):,} → {new_stats.get('matk', 0):,}** | "
                f"DEF: **{old_stats.get('def', 0):,} → {new_stats.get('def', 0):,}**"
            ),
            inline=False,
        )
        if unlocked:
            embed.add_field(
                name="Nova Habilidade Despertada",
                value="\n".join(
                    f"✅ **{skill.get('nome', 'Habilidade')}** — "
                    f"{_trim(skill.get('descricao') or 'Sem descrição.', 700)}"
                    for skill in unlocked
                )[:1024],
                inline=False,
            )
        else:
            embed.add_field(
                name="Despertar",
                value="Nenhuma habilidade nova neste estágio, mas os atributos foram fortalecidos.",
                inline=False,
            )
        embed.set_footer(text="TutoriUAU: uma cópia entrou, números maiores saíram. Alquimia de planilha.")
        await ctx.send(embed=embed)

    def _find_catalog_hero(self, query):
        query_norm = normalize_lookup(query)
        if not query_norm:
            return None, None

        candidates = []
        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome":
                continue
            hero_name = hero.get("nome", hero_id)
            lookup_names = {
                normalize_lookup(hero_id.replace("_", " ")),
                normalize_lookup(hero_name),
            }
            if query_norm in lookup_names:
                return hero_id, hero
            if any(query_norm in name or name in query_norm for name in lookup_names):
                candidates.append((hero_id, hero))

        if not candidates:
            return None, None
        candidates.sort(key=lambda item: (len(item[1].get("nome", item[0])), item[1].get("nome", item[0])))
        return candidates[0]

    async def _send_catalog_hero(self, ctx, hero_id, hero):
        rarity = max(1, int(hero.get("raridade", 1) or 1))
        max_evolution = max(1, int(hero.get("max_star", max(5, rarity)) or max(5, rarity)))
        stats = calculate_hero_stats(hero, stars=1, level=1, equipment_bonuses=[])
        skills = get_hero_skill_descriptions(hero, stars=max_evolution, rarity=rarity)

        embed = discord.Embed(
            title=f"{hero.get('emoji', '')} {hero.get('nome', hero_id)}",
            description=(
                f"`{hero_id}` | Ficha base do catalogo\n"
                f"Classe: **{hero.get('classe', 'Sem classe')}** | "
                f"Origem: **{hero.get('origem', 'Desconhecida')}**"
            ),
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Raridade",
            value=f"Base: **{'⭐' * rarity}** | Evolucao maxima: **{max_evolution}**",
            inline=False,
        )
        embed.add_field(
            name="Status Base",
            value=(
                f"HP: **{stats.get('hp', 0):,}** | ATK: **{stats.get('atk', 0):,}**\n"
                f"MATK: **{stats.get('matk', 0):,}** | DEF: **{stats.get('def', 0):,}**\n"
                f"SPD: **{stats.get('spd', 0):,}** | CRT: **{stats.get('crt', 0):,}%**"
            ),
            inline=False,
        )

        skill_lines = []
        for skill in skills:
            label = skill.get("tipo", "Habilidade")
            description = _trim(skill.get("descricao") or "Descricao ainda nao cadastrada.", 850)
            skill_lines.append(f"**{label} - {skill.get('nome', 'Habilidade')}**\n{description}")

        if skill_lines:
            for index, chunk in enumerate(chunk_lines(skill_lines, limit=1000)):
                embed.add_field(
                    name="Habilidades" if index == 0 else "Habilidades (continuacao)",
                    value=chunk,
                    inline=False,
                )
        else:
            embed.add_field(name="Habilidades", value="Nenhuma habilidade cadastrada.", inline=False)

        embed.set_footer(text="TutoriUAU: ficha base, sem buff de usuario, sem drama de mochila, sem desculpa.")
        local_path, filename = get_hero_attachment(hero_id, prefix="catalogo")
        hero_file = discord.File(local_path, filename=filename) if local_path else None
        if hero_file:
            embed.set_image(url=f"attachment://{filename}")
            await ctx.send(embed=embed, file=hero_file)
        else:
            await ctx.send(embed=embed)

    @commands.command(name="heroi", aliases=["herói"])
    async def heroi_prefix(self, ctx, *, hero_ref: str = None):
        if not hero_ref:
            return await ctx.send("Faltou o ID ou nome. Exemplos: `echo heroi 15` ou `echo heroi Freeza`.")

        if not str(hero_ref).strip().isdigit():
            hero_id, hero = self._find_catalog_hero(hero_ref)
            if not hero:
                return await ctx.send("Nao encontrei esse heroi no catalogo. TutoriUAU procurou ate debaixo do sofa digital.")
            return await self._send_catalog_hero(ctx, hero_id, hero)

        hero_db_id = int(str(hero_ref).strip())

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(heroes)")
        hero_columns = {row[1] for row in cursor.fetchall()}
        equipment_columns = [
            column
            for column in ("equip_atk", "equip_def", "equip_livre")
            if column in hero_columns
        ]
        selected_columns = ["hero_id", "rarity", "stars", "level", "xp"] + equipment_columns
        cursor.execute(
            f"SELECT {', '.join(selected_columns)} FROM heroes WHERE id = ? AND user_id = ?",
            (hero_db_id, str(ctx.author.id)),
        )
        hero_db = cursor.fetchone()
        if not hero_db:
            conn.close()
            return await ctx.send("Herói não encontrado na sua conta.")

        hero_id, stored_rarity, hero_stars, hero_level, hero_xp = hero_db[:5]
        equipped_items = [item for item in hero_db[5:] if item]
        hero = HEROES.get(hero_id, {})
        rarity = max(1, int(hero.get("raridade", stored_rarity or 1) or 1))
        hero_stars = max(1, int(hero_stars or 1))
        hero_level = max(1, int(hero_level or 1))
        hero_xp = max(0, int(hero_xp or 0))

        if rarity != int(stored_rarity or 0):
            cursor.execute("UPDATE heroes SET rarity = ? WHERE id = ?", (rarity, hero_db_id))

        equipment_bonuses = [
            get_equipment_bonus(cursor, ctx.author.id, item_name, EQUIPAMENTOS)
            for item_name in equipped_items
        ]
        stats = calculate_hero_stats(
            hero,
            stars=hero_stars,
            level=hero_level,
            equipment_bonuses=equipment_bonuses,
        )
        skills = get_hero_skill_descriptions(hero, stars=hero_stars, rarity=rarity)
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title=f"{hero.get('emoji', '❔')} {hero.get('nome', hero_id)}",
            description=(
                f"`ID {hero_db_id}` | Classe: **{hero.get('classe', 'Sem classe')}** | "
                f"Origem: **{hero.get('origem', 'Desconhecida')}**\n"
                f"Nível: **{hero_level}** | XP atual: **{hero_xp:,}**"
            ),
            color=discord.Color.gold(),
        )
        
        local_path, filename = get_hero_attachment(hero_id, prefix="ficha")
        hero_file = discord.File(local_path, filename=filename) if local_path else None
        if hero_file:
            embed.set_image(url=f"attachment://{filename}")

        max_evolution = max(hero_stars, int(hero.get("max_star", 7) or 7))
        evolution_marks = f" {'✦' * (hero_stars - 1)}" if hero_stars > 1 else ""
        embed.add_field(
            name="Raridade e Evolução",
            value=(
                f"Raridade base: **{'⭐' * rarity}**\n"
                f"Evolução: **estágio {hero_stars}/{max_evolution}{evolution_marks}**"
            ),
            inline=False,
        )
        embed.add_field(
            name="Status de Combate",
            value=(
                f"❤️ HP: **{stats.get('hp', 0):,}** | ⚔️ ATK: **{stats.get('atk', 0):,}**\n"
                f"🔮 MATK: **{stats.get('matk', 0):,}** | 🛡️ DEF: **{stats.get('def', 0):,}**\n"
                f"💨 SPD: **{stats.get('spd', 0):,}** | 🎯 CRT: **{stats.get('crt', 0):,}%**"
            ),
            inline=False,
        )

        if equipped_items:
            equipment_labels = [
                EQUIPAMENTOS.get(item_name, {}).get("nome", item_name.replace("_", " ").title())
                for item_name in equipped_items
            ]
            embed.add_field(name="Equipamentos", value="\n".join(f"• {name}" for name in equipment_labels), inline=False)

        skill_lines = []
        for skill in skills:
            status = "✅" if skill.get("ativa") else "🔒"
            label = skill.get("tipo", "Habilidade")
            description = _trim(skill.get("descricao") or "Descrição ainda não cadastrada.", 850)
            skill_lines.append(f"{status} **{label} — {skill.get('nome', 'Habilidade')}**\n{description}")

        if skill_lines:
            for index, chunk in enumerate(chunk_lines(skill_lines, limit=1000)):
                field_name = "Habilidades" if index == 0 else "Habilidades (continuação)"
                embed.add_field(name=field_name, value=chunk, inline=False)
        else:
            embed.add_field(
                name="Habilidades",
                value="Nenhuma habilidade cadastrada. O TutoriUAU encontrou um currículo em branco e ficou pessoalmente ofendido.",
                inline=False,
            )

        embed.set_footer(text="TutoriUAU: agora a ficha mostra números e habilidades. Tecnologia avançadíssima.")
        
        if hero_file: await ctx.send(embed=embed, file=hero_file)
        else: await ctx.send(embed=embed)

    @commands.command(name="anime", aliases=["obra", "origem"])
    async def anime_prefix(self, ctx, *, query: str = None):
        if not query:
            return await ctx.send("Use `echo anime <nome da obra>`. Exemplo: `echo anime Re:Zero`.")

        query_norm = normalize_lookup(query)
        matches = []
        exact_origin = None
        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome":
                continue
            origin = hero.get("origem", "Desconhecida")
            origin_norm = normalize_lookup(origin)
            if origin_norm == query_norm:
                exact_origin = origin
            if query_norm in origin_norm or origin_norm in query_norm:
                matches.append((hero_id, hero))

        if exact_origin:
            matches = [
                (hero_id, hero)
                for hero_id, hero in matches
                if normalize_lookup(hero.get("origem", "")) == normalize_lookup(exact_origin)
            ]

        if not matches:
            return await ctx.send("Nao encontrei personagens dessa obra. TutoriUAU abriu a wiki mental e ela deu 404.")

        matches.sort(key=lambda item: (item[1].get("origem", ""), item[1].get("nome", item[0])))
        title_origin = exact_origin or query
        comments = [
            "TutoriUAU: elenco reunido. Agora tente nao montar uma party juridicamente questionavel.",
            "TutoriUAU: pagina dois, porque claro que anime nunca tem so cinco personagens.",
            "TutoriUAU: se voce decorou todos esses nomes, parabens e talvez descanse.",
            "TutoriUAU: afinidade comecou como sistema e virou album de figurinhas com magia.",
        ]

        embeds = []
        per_page = 12
        for page, start in enumerate(range(0, len(matches), per_page), start=1):
            chunk = matches[start:start + per_page]
            embed = discord.Embed(
                title=f"Personagens de {title_origin}",
                color=discord.Color.blurple(),
            )
            lines = []
            for hero_id, hero in chunk:
                rarity = max(1, int(hero.get("raridade", 1) or 1))
                lines.append(
                    f"`{hero_id}` {hero.get('emoji', '')} **{hero.get('nome', hero_id)}** "
                    f"| {hero.get('classe', 'Sem classe')} | {'⭐' * rarity}"
                )
            embed.description = "\n".join(lines)
            total_pages = (len(matches) + per_page - 1) // per_page
            embed.set_footer(text=f"Pagina {page}/{total_pages} - {comments[(page - 1) % len(comments)]}")
            embeds.append(embed)

        view = HeroisPaginator(ctx.author, embeds) if len(embeds) > 1 else None
        await ctx.send(embed=embeds[0], view=view)

async def setup(bot):
    await bot.add_cog(Perfil(bot))
