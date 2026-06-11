import asyncio
import io
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
except ModuleNotFoundError:
    HEROES = {}

try:
    from data.pets import PETS
except ModuleNotFoundError:
    PETS = {}

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
    }
}

# ===================================================
# FUNÇÕES UTILITÁRIAS SEGURAS
# ===================================================
def clean_text(text):
    """Remove emojis para evitar que o Pillow desenhe quadrados []."""
    if not text: return ""
    return "".join(c for c in str(text) if unicodedata.category(c) not in ('So', 'Cs', 'Cn'))

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
        "token_titulo_pontual": "Pontual",
        "token_titulo_pontual_demais": "Pontual Demais",
        "token_titulo_bug_ambulante": "Bug Ambulante",
        "token_titulo_tutoriuau_aprovou": "TutoriUAU Aprovou",
        "token_titulo_patrocinador": "Patrocinador",
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


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        
        # Testar .jpg e .png
        for ext in [".jpg", ".png", ".jpeg"]:
            clean_name = filename.replace(".png", "").replace(".jpg", "")
            path = os.path.join(root_dir, "assets", category, f"{clean_name}{ext}")
            if os.path.isfile(path):
                try:
                    with open(path, "rb") as f:
                        return f.read()
                except OSError: pass
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
                ((40, 330, 390, 450), "ARENA DA TORRE", f"Andar {data['arena_record']}\nRank #{data['arena_rank']}"),
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
                    pet_text_clean = f"{n_form} - {r_form}★ | Lv {p_lvl or 1}"
            except: pass

        guild_text_clean = "Sem guilda. Lobo solitario."
        if guild:
            guild_text_clean = f"{clean_text(guild[0])} - Nv {guild[1] or 1} | {clean_text(guild[3])} | Score {guild[2] or 0:,}"

        conn.close()

        card_data = {
            "gold": gold or 0, "gems": gems or 0, "level": level or 1, "xp": xp or 0,
            "arena_record": arena_record or 0, "pvp_rating": pvp_rating or 0,
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

    @commands.command(name="heroi", aliases=["herói"])
    async def heroi_prefix(self, ctx, hero_db_id: int = None):
        if not hero_db_id: return await ctx.send("Faltou o ID. Exemplo: `echo heroi 15`.")

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT hero_id, rarity, stars, level, xp FROM heroes WHERE id = ? AND user_id = ?", (hero_db_id, str(ctx.author.id)))
        hero_db = cursor.fetchone()
        if not hero_db:
            conn.close()
            return await ctx.send("Herói não encontrado na sua conta.")

        hero_id, rarity, hero_stars, hero_level, hero_xp = hero_db
        hero = HEROES.get(hero_id, {})
        conn.close()

        embed = discord.Embed(
            title=f"{hero.get('emoji', '❔')} {hero.get('nome', hero_id)}",
            description=f"`ID {hero_db_id}` | Classe: **{hero.get('classe', 'Sem classe')}** | XP: **{hero_xp:,}**",
            color=discord.Color.gold(),
        )
        
        # Puxa a imagem LOCAL do herói
        local_path = os.path.join(root_dir, "assets", "herois_img", f"{hero_id}.jpg")
        hero_file = None
        if os.path.isfile(local_path):
            hero_file = discord.File(local_path, filename=f"{hero_id}.jpg")
            embed.set_image(url=f"attachment://{hero_id}.jpg")

        embed.add_field(name="Raridade", value=estrelas(rarity, hero_stars), inline=False)
        embed.set_footer(text="TutoriUAU: Colecionando bonecos, hein?")
        
        if hero_file: await ctx.send(embed=embed, file=hero_file)
        else: await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Perfil(bot))
