import os
import random
import re
import sqlite3
import sys
import time
import unicodedata
from collections import Counter, defaultdict

import discord
from discord.ext import commands

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.world_cup_players import WORLD_CUP_PLAYERS
    from data.world_cup_opponents import WORLD_CUP_OPPONENTS
    from update_db_copa import ensure_world_cup_schema
    from utils.hero_images import get_hero_attachment
except Exception:
    HEROES = {}
    WORLD_CUP_PLAYERS = {}
    WORLD_CUP_OPPONENTS = {}

    def ensure_world_cup_schema(cursor):
        return None

    def get_hero_attachment(hero_id, prefix="hero"):
        return None, None


POSITIONS = {
    "GOL": "Goleiro",
    "ZAG": "Zagueiro",
    "LAT": "Lateral",
    "VOL": "Volante",
    "MC": "Meio-campo",
    "MEI": "Meia ofensivo",
    "PE": "Ponta esquerda",
    "PD": "Ponta direita",
    "ATA": "Atacante",
}

FORMATIONS = {
    "4-3-3": {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MC": 1, "MEI": 1, "PE": 1, "PD": 1, "ATA": 1},
    "4-4-2": {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MC": 2, "MEI": 1, "ATA": 2},
    "4-2-3-1": {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 1, "PE": 1, "PD": 1, "ATA": 1},
    "3-5-2": {"GOL": 1, "ZAG": 3, "VOL": 2, "MC": 2, "MEI": 1, "ATA": 2},
    "5-3-2": {"GOL": 1, "ZAG": 3, "LAT": 2, "VOL": 1, "MC": 1, "MEI": 1, "ATA": 2},
}

FORMATION_TIPS = {
    "4-3-3": "equilibrio com ataque pelas pontas",
    "4-4-2": "simples, seguro e sem inventar moda",
    "4-2-3-1": "controle de meio e muita paciencia tatica",
    "3-5-2": "posse, pressao e um pouco de coragem",
    "5-3-2": "defesa forte para quem gosta de sofrer menos",
}

STAGE_ORDER = ["grupos", "oitavas", "quartas", "semi", "final"]
STAGE_LABELS = {
    "grupos": "Fase de grupos",
    "oitavas": "Oitavas",
    "quartas": "Quartas",
    "semi": "Semifinal",
    "final": "Final",
    "campeao": "Campeao",
    "eliminado": "Eliminado",
}
STAGE_REWARDS = {
    "grupos": 50,
    "oitavas": 100,
    "quartas": 200,
    "semi": 400,
    "finalista": 700,
    "campeao": 1200,
}
MATCH_REWARDS = {"V": 15, "E": 8, "D": 5}
MATCH_COOLDOWN = 6 * 60 * 60
COPA_SUMMON_COST = 800
BASE_RATES = {1: 50.0, 2: 25.0, 3: 19.0, 4: 5.0, 5: 1.0}
SOFT_PITY_4 = 15
SOFT_PITY_5 = 30
HARD_PITY_4 = 30
HARD_PITY_5 = 100

SPORTS_ORIGINS = {
    "Blue Lock",
    "Inazuma Eleven",
    "Haikyuu!!",
    "Kuroko no Basket",
    "Captain Tsubasa",
}

HERO_ID_ALIASES = {
    "alex_louis_strong": "alex_louis_armstrong",
    "alphonse_elric": "alphons_elric",
    "dabi_base": "dabi",
    "crocodile_base": "crocodile",
    "frieren_elf": "frieren",
    "ghoul": "suzuya_juuzou",
    "gojo_satoru": "satoru_gojo",
    "griffith_base": "griffith",
    "guts_berserk": "guts",
    "kaguya_otsutsuki_base": "kaguya_otsutsuki",
    "kurapika_hxh": "kurapika",
    "killua_zoldyck": "killua",
    "lelouch_geass": "lelouch",
    "mahito_base": "mahito",
    "naraku_base": "naraku",
    "okabe": "rintarou_okabe",
    "orochimaru_base": "orochimaru",
    "petelgeuse_base": "petelgeuse",
    "saitama_one": "saitama",
    "sheele": "schele",
    "shoyo_hinata": "hinata_shoyo_hq",
    "shoyo_hinata_hq": "hinata_shoyo_hq",
    "sinon_sao": "sinon",
    "sukuna_jujutsu": "sukuna",
    "tanjiro_demon": "tanjirou_kamado",
    "ulquiorra_base": "ulquiorra",
    "vash_stampede": "vash",
    "zeldris_base": "zeldris",
}

ROLE_WEIGHTS = {
    "GOL": {"goleiro": 0.58, "defesa": 0.18, "mental": 0.18, "passe": 0.06},
    "ZAG": {"defesa": 0.46, "mental": 0.19, "passe": 0.14, "ataque": 0.11, "velocidade": 0.10},
    "LAT": {"velocidade": 0.30, "defesa": 0.26, "passe": 0.20, "ataque": 0.14, "mental": 0.10},
    "VOL": {"defesa": 0.31, "passe": 0.28, "mental": 0.20, "ataque": 0.11, "velocidade": 0.10},
    "MC": {"passe": 0.36, "mental": 0.24, "defesa": 0.16, "ataque": 0.14, "velocidade": 0.10},
    "MEI": {"passe": 0.34, "ataque": 0.20, "mental": 0.20, "finalizacao": 0.16, "velocidade": 0.10},
    "PE": {"velocidade": 0.29, "ataque": 0.25, "finalizacao": 0.25, "passe": 0.11, "mental": 0.10},
    "PD": {"velocidade": 0.29, "ataque": 0.25, "finalizacao": 0.25, "passe": 0.11, "mental": 0.10},
    "ATA": {"finalizacao": 0.40, "ataque": 0.30, "velocidade": 0.14, "mental": 0.11, "passe": 0.05},
}

SHOP_ITEMS = {
    1: {"name": "Tema: Arquibancada Lotada", "cost": 180, "kind": "cosmetic", "type": "frame", "item": "token_moldura_arquibancada_lotada"},
    2: {"name": "Tema: Gramado Noturno", "cost": 180, "kind": "cosmetic", "type": "frame", "item": "token_moldura_gramado_noturno"},
    3: {"name": "Tema: Sala de Imprensa", "cost": 210, "kind": "cosmetic", "type": "frame", "item": "token_moldura_sala_de_imprensa"},
    4: {"name": "Tema: Taca Mundial", "cost": 260, "kind": "cosmetic", "type": "frame", "item": "token_moldura_taca_mundial"},
    5: {"name": "Titulo: Campeao de Lugnica", "cost": 160, "kind": "cosmetic", "type": "title", "item": "token_titulo_campeao_de_lugnica"},
    6: {"name": "Titulo: Lenda da Echo Cup", "cost": 220, "kind": "cosmetic", "type": "title", "item": "token_titulo_lenda_echo_cup"},
    7: {"name": "Titulo: Rei dos Ecos", "cost": 260, "kind": "cosmetic", "type": "title", "item": "token_titulo_rei_dos_ecos"},
    8: {"name": "Titulo: Maior Tecnico de Lugnica", "cost": 260, "kind": "cosmetic", "type": "title", "item": "token_titulo_maior_tecnico_de_lugnica"},
    9: {"name": "3 Tickets de Invocacao", "cost": 120, "kind": "tickets", "amount": 3},
    10: {"name": "25 Gems", "cost": 220, "kind": "gems", "amount": 25},
    11: {"name": "Maple, Pet Alce", "cost": 420, "kind": "pet", "pet_id": "maple_alce", "pet_name": "Maple", "rarity": 5},
    12: {"name": "Zayu, Pet Onca-Pintada", "cost": 420, "kind": "pet", "pet_id": "zayu_onca", "pet_name": "Zayu", "rarity": 5},
    13: {"name": "Clutch, Pet Aguia", "cost": 420, "kind": "pet", "pet_id": "clutch_aguia", "pet_name": "Clutch", "rarity": 5},
}


def now_ts():
    return int(time.time())


def normalize_text(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def stars_text(rarity):
    return "⭐" * max(1, int(rarity or 1))


def trim(text, limit=1024):
    text = str(text or "")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def add_inventory(cursor, user_id, item_name, qty=1):
    cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), item_name))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
    else:
        cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (str(user_id), item_name, qty))


def add_tickets(cursor, user_id, qty):
    cursor.execute(
        """
        INSERT OR IGNORE INTO summon_data
        (user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star, total_divine)
        VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        """,
        (str(user_id),),
    )
    cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (qty, str(user_id)))


def ensure_extra_tables(cursor):
    ensure_world_cup_schema(cursor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_cosmetics(
            user_id TEXT NOT NULL,
            cosmetic_id TEXT NOT NULL,
            type TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            purchased_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, cosmetic_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            pet_id TEXT,
            pet_name TEXT,
            rarity INTEGER,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
    """)


class TeamNameModal(discord.ui.Modal, title="Nome do time"):
    team_name = discord.ui.TextInput(
        label="Nome do seu time",
        placeholder="Ex.: TutoriUAU FC",
        min_length=3,
        max_length=40,
    )

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction):
        self.view_ref.team_name = str(self.team_name.value).strip()[:40]
        await interaction.response.edit_message(embed=self.view_ref.build_embed(), view=self.view_ref)


class LineupSlotModal(discord.ui.Modal, title="Escalar jogador"):
    slot = discord.ui.TextInput(label="Slot", placeholder="1 a 11", min_length=1, max_length=2)
    hero_instance_id = discord.ui.TextInput(label="ID do heroi na sua colecao", placeholder="Ex.: 123", min_length=1, max_length=12)
    position = discord.ui.TextInput(label="Posicao", placeholder="GOL, ZAG, LAT, VOL, MC, MEI, PE, PD ou ATA", min_length=2, max_length=3)

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction):
        ok, message = self.view_ref.set_slot(
            str(self.slot.value),
            str(self.hero_instance_id.value),
            str(self.position.value),
        )
        if not ok:
            return await interaction.response.send_message(message, ephemeral=True)
        await interaction.response.edit_message(embed=self.view_ref.build_embed(), view=self.view_ref)


class CaptainModal(discord.ui.Modal, title="Definir capitao"):
    hero_instance_id = discord.ui.TextInput(label="ID do heroi na escalação", placeholder="Ex.: 123", min_length=1, max_length=12)

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction):
        ok, message = self.view_ref.set_captain(str(self.hero_instance_id.value))
        if not ok:
            return await interaction.response.send_message(message, ephemeral=True)
        await interaction.response.edit_message(embed=self.view_ref.build_embed(), view=self.view_ref)


class FormationSelect(discord.ui.Select):
    def __init__(self, parent, row=0):
        options = [
            discord.SelectOption(label=formation, value=formation, description=FORMATION_TIPS[formation])
            for formation in FORMATIONS
        ]
        super().__init__(placeholder="Escolha a formacao", options=options, min_values=1, max_values=1, row=row)
        self.parent = parent

    async def callback(self, interaction):
        self.parent.formation = self.values[0]
        await interaction.response.edit_message(embed=self.parent.build_embed(), view=self.parent)


class CopaTeamBuilderView(discord.ui.View):
    def __init__(self, cog, ctx, team_name=None):
        super().__init__(timeout=600)
        self.cog = cog
        self.ctx = ctx
        self.team_name = team_name or f"{ctx.author.display_name} FC"
        self.formation = "4-3-3"
        self.captain_id = None
        self.lineup = {}
        self.message = None
        self.add_item(FormationSelect(self))
        self._load_existing()
        if team_name:
            self.team_name = str(team_name).strip()[:40]

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Esse painel e de outro tecnico. TutoriUAU apitou invasao de campo.",
                ephemeral=True,
            )
            return False
        return True

    def _load_existing(self):
        user_id = str(self.ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_extra_tables(cursor)
        cursor.execute("SELECT team_name, formation, captain_id FROM world_cup_teams WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            self.team_name = row[0] or self.team_name
            self.formation = row[1] or self.formation
            self.captain_id = str(row[2]) if row[2] else None
        cursor.execute(
            "SELECT slot, hero_instance_id, hero_id, position FROM world_cup_lineups WHERE user_id = ? ORDER BY slot",
            (user_id,),
        )
        for slot, instance_id, hero_id, position in cursor.fetchall():
            self.lineup[int(slot)] = {
                "instance_id": int(instance_id),
                "hero_id": hero_id,
                "position": position,
            }
        conn.commit()
        conn.close()

    def owned(self):
        return self.cog.owned_copa_heroes(self.ctx.author.id)

    def _owned_by_instance(self):
        return {int(row["instance_id"]): row for row in self.owned()}

    def build_embed(self):
        validation = self.cog.validate_lineup(self.ctx.author.id, self.formation, self.captain_id, self.lineup)
        embed = discord.Embed(
            title="Echo Cup - Criacao do Time",
            description=(
                f"**{self.team_name}**\n"
                f"Formacao: **{self.formation}** - {FORMATION_TIPS.get(self.formation, '')}\n"
                "TutoriUAU: monte os 11, escolha um goleiro e tente nao colocar atacante no gol. Eu ja vi."
            ),
            color=discord.Color.green() if validation[0] else discord.Color.orange(),
        )
        owned = self.owned()
        embed.add_field(name="Disponiveis", value=f"Herois da Copa na sua conta: **{len(owned)}**", inline=False)
        if self.lineup:
            lines = []
            for slot in range(1, 12):
                item = self.lineup.get(slot)
                if not item:
                    lines.append(f"`{slot:02}` vazio")
                    continue
                hero = WORLD_CUP_PLAYERS.get(item["hero_id"], {})
                cap = " (C)" if str(item["instance_id"]) == str(self.captain_id) else ""
                lines.append(f"`{slot:02}` **{hero.get('nome', item['hero_id'])}**{cap} - `{item['position']}` | ID `{item['instance_id']}`")
            embed.add_field(name="Escalacao", value=trim("\n".join(lines), 1024), inline=False)
        else:
            embed.add_field(name="Escalacao", value="Nenhum jogador escalado ainda. O campo esta dramaticamente vazio.", inline=False)

        if owned:
            preview = []
            for row in owned[:16]:
                hero = WORLD_CUP_PLAYERS.get(row["hero_id"], {})
                positions = "/".join(pos[0] for pos in hero.get("posicoes", [])[:3]) or "?"
                preview.append(f"`{row['instance_id']}` {hero.get('nome', row['hero_id'])} ({positions}) Lv {row['level']}")
            embed.add_field(name="IDs para escalar", value=trim("\n".join(preview), 1024), inline=False)
        embed.add_field(name="Validacao", value="Pronto para jogar." if validation[0] else "\n".join(validation[1]), inline=False)
        embed.set_footer(text="Use os botoes: nome, auto preencher, escalar slot, capitao e salvar.")
        return embed

    def set_slot(self, raw_slot, raw_instance, raw_position):
        try:
            slot = int(raw_slot)
            instance_id = int(raw_instance)
        except ValueError:
            return False, "Slot e ID precisam ser numeros."
        if slot < 1 or slot > 11:
            return False, "O slot precisa estar entre 1 e 11."
        position = str(raw_position or "").upper().strip()
        if position not in POSITIONS:
            return False, f"Posicao invalida. Use: {', '.join(POSITIONS)}."
        owned = self._owned_by_instance()
        row = owned.get(instance_id)
        if not row:
            return False, "Esse heroi nao pertence a voce ou nao tem ficha da Copa."
        self.lineup[slot] = {
            "instance_id": instance_id,
            "hero_id": row["hero_id"],
            "position": position,
        }
        return True, "Escalado."

    def set_captain(self, raw_instance):
        try:
            instance_id = int(raw_instance)
        except ValueError:
            return False, "O ID precisa ser numerico."
        if not any(int(item["instance_id"]) == instance_id for item in self.lineup.values()):
            return False, "O capitao precisa estar entre os 11 escalados."
        self.captain_id = str(instance_id)
        return True, "Capitao definido."

    def auto_fill(self):
        owned = self.owned()
        if len(owned) < 11:
            return False, "Voce precisa de pelo menos 11 herois com ficha da Copa."
        used = set()
        lineup = {}
        slot = 1
        for position, amount in FORMATIONS[self.formation].items():
            for _ in range(amount):
                best = None
                best_score = -1
                for row in owned:
                    if row["hero_id"] in used:
                        continue
                    score = self.cog.player_position_score(row["hero_id"], position)
                    score += int(row["rarity"] or 1) * 2 + int(row["level"] or 1) * 0.2
                    if score > best_score:
                        best = row
                        best_score = score
                if not best:
                    continue
                used.add(best["hero_id"])
                lineup[slot] = {"instance_id": int(best["instance_id"]), "hero_id": best["hero_id"], "position": position}
                slot += 1
        self.lineup = lineup
        if self.lineup and not self.captain_id:
            captain = max(self.lineup.values(), key=lambda item: self.cog.player_position_score(item["hero_id"], item["position"]))
            self.captain_id = str(captain["instance_id"])
        return True, "Time preenchido automaticamente."

    @discord.ui.button(label="Nome", style=discord.ButtonStyle.secondary, row=1)
    async def name_button(self, interaction, button):
        await interaction.response.send_modal(TeamNameModal(self))

    @discord.ui.button(label="Auto preencher", style=discord.ButtonStyle.primary, row=1)
    async def autofill_button(self, interaction, button):
        ok, message = self.auto_fill()
        if not ok:
            return await interaction.response.send_message(message, ephemeral=True)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Escalar slot", style=discord.ButtonStyle.secondary, row=1)
    async def slot_button(self, interaction, button):
        await interaction.response.send_modal(LineupSlotModal(self))

    @discord.ui.button(label="Capitao", style=discord.ButtonStyle.secondary, row=2)
    async def captain_button(self, interaction, button):
        await interaction.response.send_modal(CaptainModal(self))

    @discord.ui.button(label="Salvar time", style=discord.ButtonStyle.success, row=2)
    async def save_button(self, interaction, button):
        ok, errors = self.cog.validate_lineup(self.ctx.author.id, self.formation, self.captain_id, self.lineup)
        if not ok:
            return await interaction.response.send_message("Ainda falta ajustar:\n" + "\n".join(errors), ephemeral=True)
        self.cog.save_team(self.ctx.author.id, self.team_name, self.formation, self.captain_id, self.lineup)
        embed = self.cog.team_embed(self.ctx.author)
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()


class MatchFormationSelect(discord.ui.Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label=formation, value=formation, description=FORMATION_TIPS[formation])
            for formation in FORMATIONS
        ]
        super().__init__(placeholder="Ajustar formacao para o 2o tempo", min_values=1, max_values=1, options=options)
        self.view_ref = view

    async def callback(self, interaction):
        self.view_ref.formation = self.values[0]
        await interaction.response.edit_message(embed=self.view_ref.first_half_embed(), view=self.view_ref)


class SubstitutionModal(discord.ui.Modal, title="Substituicao da Copa"):
    slot = discord.ui.TextInput(label="Slot a trocar", placeholder="1 a 11", min_length=1, max_length=2)
    hero_instance_id = discord.ui.TextInput(label="Novo ID do heroi", placeholder="ID da sua colecao", min_length=1, max_length=12)
    position = discord.ui.TextInput(label="Posicao", placeholder="Opcional: GOL/ZAG/LAT/VOL/MC/MEI/PE/PD/ATA", required=False, max_length=3)

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction):
        ok, message = self.view_ref.substitute(str(self.slot.value), str(self.hero_instance_id.value), str(self.position.value or ""))
        if not ok:
            return await interaction.response.send_message(message, ephemeral=True)
        await interaction.response.edit_message(embed=self.view_ref.first_half_embed(), view=self.view_ref)


class CopaMatchView(discord.ui.View):
    def __init__(self, cog, ctx, match_state):
        super().__init__(timeout=600)
        self.cog = cog
        self.ctx = ctx
        self.state = match_state
        self.formation = match_state["formation"]
        self.lineup = dict(match_state["lineup"])
        self.finished = False
        self.add_item(MatchFormationSelect(self))

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Esse jogo e de outro tecnico. TutoriUAU mostrou o cartao amarelo.", ephemeral=True)
            return False
        return True

    def first_half_embed(self):
        embed = discord.Embed(
            title=f"Echo Cup - {self.state['stage_label']} - Intervalo",
            description=(
                f"**{self.state['team_name']}** {self.state['half_user']} x {self.state['half_opp']} **{self.state['opponent']['nome']}**\n"
                f"Formacao atual: **{self.formation}**\n\n"
                + "\n".join(self.state["first_log"])
            ),
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Banco de improviso",
            value="Antes do segundo tempo voce pode mudar a formacao ou fazer uma substituicao por ID. TutoriUAU: mexer no time e gratis; acertar e opcional.",
            inline=False,
        )
        return embed

    def substitute(self, raw_slot, raw_instance, raw_position):
        try:
            slot = int(raw_slot)
            instance_id = int(raw_instance)
        except ValueError:
            return False, "Slot e ID precisam ser numeros."
        if slot < 1 or slot > 11:
            return False, "Slot invalido."
        owned = {int(row["instance_id"]): row for row in self.cog.owned_copa_heroes(self.ctx.author.id)}
        row = owned.get(instance_id)
        if not row:
            return False, "Esse heroi nao pertence a voce ou nao tem ficha da Copa."
        if any(int(item["instance_id"]) == instance_id for item in self.lineup.values()):
            return False, "Esse heroi ja esta em campo."
        position = str(raw_position or "").upper().strip() or self.lineup.get(slot, {}).get("position", "ATA")
        if position not in POSITIONS:
            return False, f"Posicao invalida. Use: {', '.join(POSITIONS)}."
        self.lineup[slot] = {"instance_id": instance_id, "hero_id": row["hero_id"], "position": position}
        return True, "Substituicao feita."

    @discord.ui.button(label="Substituir", style=discord.ButtonStyle.secondary, row=2)
    async def substitute_button(self, interaction, button):
        await interaction.response.send_modal(SubstitutionModal(self))

    @discord.ui.button(label="Segundo tempo", style=discord.ButtonStyle.success, row=2)
    async def second_half_button(self, interaction, button):
        if self.finished:
            return await interaction.response.send_message("Essa partida ja terminou.", ephemeral=True)
        self.finished = True
        for child in self.children:
            child.disabled = True
        embed = self.cog.finish_match(self.ctx.author, self.state, self.lineup, self.formation)
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Sair", style=discord.ButtonStyle.danger, row=2)
    async def cancel_button(self, interaction, button):
        self.finished = True
        await interaction.response.edit_message(content="Partida encerrada sem registrar resultado. TutoriUAU guardou a prancheta.", embed=None, view=None)
        self.stop()


class Copa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_extra_tables(cursor)
        conn.commit()
        conn.close()

    def _connect(self):
        conn = sqlite3.connect("players.db")
        conn.row_factory = sqlite3.Row
        ensure_extra_tables(conn.cursor())
        return conn

    def _resolve_hero_id(self, hero_id):
        raw = str(hero_id or "").strip()
        if raw in WORLD_CUP_PLAYERS:
            return raw
        normalized = normalize_text(raw)
        mapped = HERO_ID_ALIASES.get(normalized, normalized)
        if mapped in WORLD_CUP_PLAYERS:
            return mapped
        for key, data in WORLD_CUP_PLAYERS.items():
            if normalize_text(data.get("nome")) == normalized:
                return key
        return None

    def _local_hero_file(self, hero_id, prefix="copa"):
        path, filename = get_hero_attachment(hero_id, prefix)
        return discord.File(path, filename=filename) if path else None

    def _is_active(self, cursor):
        cursor.execute("SELECT value FROM world_cup_settings WHERE key = 'active'")
        row = cursor.fetchone()
        return bool(row and str(row[0]) == "1")

    def sports_pool(self):
        pool = []
        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome":
                continue
            if hero_id not in WORLD_CUP_PLAYERS:
                continue
            if hero.get("divino") or hero.get("secreto"):
                continue
            if hero.get("origem") in SPORTS_ORIGINS:
                pool.append(hero_id)
        return pool

    def owned_copa_heroes(self, user_id):
        conn = sqlite3.connect("players.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        ensure_extra_tables(cursor)
        cursor.execute(
            """
            SELECT id AS instance_id, hero_id, rarity, stars, level
            FROM heroes
            WHERE user_id = ?
            ORDER BY rarity DESC, stars DESC, level DESC, id ASC
            """,
            (str(user_id),),
        )
        rows = []
        seen = set()
        for row in cursor.fetchall():
            hero_id = self._resolve_hero_id(row["hero_id"])
            if not hero_id or hero_id in seen:
                continue
            seen.add(hero_id)
            rows.append({
                "instance_id": int(row["instance_id"]),
                "hero_id": hero_id,
                "rarity": int(row["rarity"] or HEROES.get(hero_id, {}).get("raridade", 1)),
                "stars": int(row["stars"] or 1),
                "level": int(row["level"] or 1),
            })
        conn.close()
        return rows

    def player_position_score(self, hero_id, position):
        data = WORLD_CUP_PLAYERS.get(hero_id, {})
        weights = ROLE_WEIGHTS.get(position, ROLE_WEIGHTS["ATA"])
        score = sum(float(data.get(stat, 50)) * weight for stat, weight in weights.items())
        preferred = {pos[0] for pos in data.get("posicoes", [])}
        if position not in preferred:
            score *= 0.88
        return score

    def validate_lineup(self, user_id, formation, captain_id, lineup):
        errors = []
        if formation not in FORMATIONS:
            errors.append("Formacao invalida.")
        if len(lineup) != 11:
            errors.append("Escalacao precisa ter 11 jogadores.")
        if not any(item.get("position") == "GOL" for item in lineup.values()):
            errors.append("Precisa ter pelo menos um GOL.")
        if not captain_id:
            errors.append("Defina um capitao.")
        elif not any(str(item.get("instance_id")) == str(captain_id) for item in lineup.values()):
            errors.append("O capitao precisa estar entre os 11.")

        owned = {int(row["instance_id"]): row["hero_id"] for row in self.owned_copa_heroes(user_id)}
        hero_ids = []
        positions = Counter()
        for item in lineup.values():
            try:
                instance_id = int(item.get("instance_id"))
            except (TypeError, ValueError):
                errors.append("Ha jogador com ID invalido.")
                continue
            if instance_id not in owned:
                errors.append(f"Heroi ID {instance_id} nao pertence ao jogador.")
                continue
            if owned[instance_id] != item.get("hero_id"):
                errors.append(f"Heroi ID {instance_id} nao bate com a ficha salva.")
            hero_ids.append(item.get("hero_id"))
            position = item.get("position")
            if position not in POSITIONS:
                errors.append(f"Posicao invalida: {position}.")
            else:
                positions[position] += 1
        duplicates = [hero_id for hero_id, count in Counter(hero_ids).items() if count > 1]
        if duplicates:
            errors.append("Sem personagem repetido na escalação.")
        if formation in FORMATIONS:
            for position, required in FORMATIONS[formation].items():
                if positions[position] != required:
                    errors.append(f"{formation} exige {required}x {position}, atual {positions[position]}.")
            extra = [position for position, count in positions.items() if count and position not in FORMATIONS[formation]]
            if extra:
                errors.append(f"{formation} nao usa: {', '.join(extra)}.")
        return (not errors), errors[:8]

    def save_team(self, user_id, team_name, formation, captain_id, lineup):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_extra_tables(cursor)
        now = now_ts()
        cursor.execute(
            """
            INSERT INTO world_cup_teams(user_id, team_name, formation, captain_id, created_at, last_match)
            VALUES (?, ?, ?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                team_name = excluded.team_name,
                formation = excluded.formation,
                captain_id = excluded.captain_id
            """,
            (str(user_id), team_name, formation, str(captain_id), now),
        )
        cursor.execute("DELETE FROM world_cup_lineups WHERE user_id = ?", (str(user_id),))
        for slot, item in sorted(lineup.items()):
            cursor.execute(
                """
                INSERT INTO world_cup_lineups(user_id, slot, hero_instance_id, hero_id, position)
                VALUES (?, ?, ?, ?, ?)
                """,
                (str(user_id), int(slot), int(item["instance_id"]), item["hero_id"], item["position"]),
            )
        cursor.execute("INSERT OR IGNORE INTO world_cup_progress(user_id) VALUES (?)", (str(user_id),))
        conn.commit()
        conn.close()

    def load_team(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT team_name, formation, captain_id, last_match FROM world_cup_teams WHERE user_id = ?", (str(user_id),))
        team = cursor.fetchone()
        cursor.execute(
            "SELECT slot, hero_instance_id, hero_id, position FROM world_cup_lineups WHERE user_id = ? ORDER BY slot",
            (str(user_id),),
        )
        lineup = {
            int(row["slot"]): {
                "instance_id": int(row["hero_instance_id"]),
                "hero_id": self._resolve_hero_id(row["hero_id"]) or row["hero_id"],
                "position": row["position"],
            }
            for row in cursor.fetchall()
        }
        cursor.execute("SELECT * FROM world_cup_progress WHERE user_id = ?", (str(user_id),))
        progress = cursor.fetchone()
        conn.close()
        return team, lineup, progress

    def team_embed(self, user):
        team, lineup, progress = self.load_team(user.id)
        if not team:
            return discord.Embed(
                title="Echo Cup - Time",
                description="Voce ainda nao criou seu time. Use `echo copa iniciar`.",
                color=discord.Color.orange(),
            )
        ok, errors = self.validate_lineup(user.id, team["formation"], team["captain_id"], lineup)
        embed = discord.Embed(
            title=f"Echo Cup - {team['team_name']}",
            description=(
                f"Formacao: **{team['formation']}**\n"
                f"Status: **{'Pronto' if ok else 'Incompleto'}**\n"
                f"Echobet: **{(progress['points'] if progress else 0):,}**"
            ),
            color=discord.Color.green() if ok else discord.Color.orange(),
        )
        lines = []
        for slot in range(1, 12):
            item = lineup.get(slot)
            if not item:
                lines.append(f"`{slot:02}` vazio")
                continue
            data = WORLD_CUP_PLAYERS.get(item["hero_id"], {})
            captain = " (C)" if str(item["instance_id"]) == str(team["captain_id"]) else ""
            lines.append(f"`{slot:02}` **{data.get('nome', item['hero_id'])}**{captain} - `{item['position']}` | ID `{item['instance_id']}`")
        embed.add_field(name="Escalacao", value=trim("\n".join(lines), 1024), inline=False)
        if not ok:
            embed.add_field(name="Pendencias", value="\n".join(errors), inline=False)
        embed.set_footer(text="TutoriUAU: use `echo copa iniciar` de novo para editar sem drama.")
        return embed

    def _team_power(self, lineup, formation, captain_id=None, rng=None):
        rng = rng or random
        scores = []
        affinity_counter = Counter()
        for item in lineup.values():
            hero_id = item["hero_id"]
            data = WORLD_CUP_PLAYERS.get(hero_id, {})
            position_score = self.player_position_score(hero_id, item["position"])
            if str(item.get("instance_id")) == str(captain_id):
                position_score += 3
            scores.append(position_score)
            affinity_counter.update(data.get("afinidades", []))
        stat_component = sum(scores) / max(1, len(scores))
        affinity_component = 0
        for count in affinity_counter.values():
            if count >= 5:
                affinity_component += 8
            elif count >= 4:
                affinity_component += 5
            elif count >= 3:
                affinity_component += 3
            elif count >= 2:
                affinity_component += 1.5
        formation_bonus = {"4-3-3": 2, "4-4-2": 1, "4-2-3-1": 2.5, "3-5-2": 2, "5-3-2": 1.5}.get(formation, 0)
        skill_component = min(15, len([item for item in lineup.values() if WORLD_CUP_PLAYERS.get(item["hero_id"], {}).get("habilidade")]) * 1.1 + affinity_component)
        rng_component = rng.uniform(0, 100)
        return stat_component * 0.60 + rng_component * 0.25 + skill_component * 0.15 + formation_bonus

    def _opponent_lineup(self, opponent):
        lineup = {}
        all_ids = list(opponent.get("titulares", []))
        pool = [self._resolve_hero_id(hero_id) for hero_id in all_ids]
        pool = [hero_id for hero_id in pool if hero_id in WORLD_CUP_PLAYERS]
        if len(pool) < 11:
            for hero_id in self.sports_pool():
                if hero_id not in pool:
                    pool.append(hero_id)
                if len(pool) >= 11:
                    break
        positions = []
        formation = opponent.get("formacao")
        if formation not in FORMATIONS:
            formation = random.choice(list(FORMATIONS))
        for position, amount in FORMATIONS[formation].items():
            positions.extend([position] * amount)
        for index, hero_id in enumerate(pool[:11], start=1):
            position = positions[index - 1] if index <= len(positions) else "ATA"
            lineup[index] = {"instance_id": 900000 + index, "hero_id": hero_id, "position": position}
        return lineup, formation

    def _current_stage(self, progress):
        if not progress or progress["stage"] not in STAGE_ORDER:
            return "grupos"
        return progress["stage"]

    def _stage_opponent(self, user_id, progress, stage):
        opponents = list(WORLD_CUP_OPPONENTS.values())
        if not opponents:
            return {"nome": "Time Fantasma do TutoriUAU", "formacao": "4-4-2", "titulares": self.sports_pool()[:11], "reservas": []}
        run_id = int(progress["current_run"] if progress else 1)
        rng = random.Random(f"copa:{user_id}:{run_id}:opponents")
        rng.shuffle(opponents)
        if stage == "grupos":
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM world_cup_matches WHERE user_id = ? AND run_id = ? AND stage = 'grupos'",
                (str(user_id), run_id),
            )
            played = int(cursor.fetchone()[0])
            conn.close()
            return opponents[played % 3]
        stage_index = STAGE_ORDER.index(stage)
        return opponents[(3 + stage_index + run_id) % len(opponents)]

    def _simulate_half(self, user, opponent, user_lineup, opponent_lineup, formation, opponent_formation, score_user, score_opp, minute_start, minute_end, seed):
        rng = random.Random(seed)
        user_power = self._team_power(user_lineup, formation, captain_id=None, rng=rng)
        opp_power = self._team_power(opponent_lineup, opponent_formation, rng=rng)
        user_share = max(0.20, min(0.80, user_power / max(1, user_power + opp_power)))
        events = sorted(rng.sample(range(minute_start, minute_end + 1), k=rng.randint(5, 8)))
        log = []
        scorers = []
        for minute in events:
            side_user = rng.random() <= user_share
            actor_lineup = user_lineup if side_user else opponent_lineup
            defender_lineup = opponent_lineup if side_user else user_lineup
            actor = rng.choice(list(actor_lineup.values()))
            defender = rng.choice(list(defender_lineup.values()))
            actor_name = WORLD_CUP_PLAYERS.get(actor["hero_id"], {}).get("nome", actor["hero_id"])
            defender_name = WORLD_CUP_PLAYERS.get(defender["hero_id"], {}).get("nome", defender["hero_id"])
            team_name = user["team_name"] if side_user else opponent["nome"]
            event_roll = rng.random()
            minute_label = f"{minute}'"

            goal_chance = 0.28 + (user_share - 0.5) * (0.22 if side_user else -0.22)
            if minute >= 80 and side_user and score_user < score_opp and rng.random() < 0.20:
                score_user += 1
                scorers.append(actor["hero_id"])
                log.append(f"{minute_label} - Virada heroica! {actor_name} resolve na marra para o {team_name}.")
            elif event_roll < goal_chance:
                if side_user:
                    score_user += 1
                    scorers.append(actor["hero_id"])
                else:
                    score_opp += 1
                skill = WORLD_CUP_PLAYERS.get(actor["hero_id"], {}).get("habilidade", {}).get("nome", "talento")
                log.append(f"{minute_label} - GOOOL de {actor_name}! {skill} apareceu no gramado.")
            elif event_roll < goal_chance + 0.22:
                log.append(f"{minute_label} - {defender_name} salva a jogada. Defesa enorme, ego maior ainda.")
            elif event_roll < goal_chance + 0.34:
                card = "vermelho" if rng.random() < 0.18 else "amarelo"
                log.append(f"{minute_label} - Cartao {card} para {actor_name}. TutoriUAU: absolutamente sutil.")
            elif event_roll < goal_chance + 0.46:
                log.append(f"{minute_label} - Falta perigosa para {team_name}. A barreira tremeu, mas sobreviveu.")
            elif event_roll < goal_chance + 0.57:
                penalty_goal = rng.random() < (0.68 if side_user else 0.63)
                if penalty_goal:
                    if side_user:
                        score_user += 1
                        scorers.append(actor["hero_id"])
                    else:
                        score_opp += 1
                    log.append(f"{minute_label} - Penalti convertido por {actor_name}. Frio como planilha de RNG.")
                else:
                    log.append(f"{minute_label} - Penalti defendido! {defender_name} virou parede.")
            elif event_roll < goal_chance + 0.69:
                log.append(f"{minute_label} - Lesao temporaria em {actor_name}. Ele volta mancando e julgando o tecnico.")
            elif event_roll < goal_chance + 0.82:
                log.append(f"{minute_label} - Substituicao tática do {team_name}. Alguem fingiu que estava no plano.")
            else:
                log.append(f"{minute_label} - Falha bizarra de {actor_name}; {defender_name} agradece e segue vivo.")
        return score_user, score_opp, log, scorers

    def _prepare_match(self, user):
        team, lineup, progress = self.load_team(user.id)
        ok, errors = self.validate_lineup(user.id, team["formation"] if team else None, team["captain_id"] if team else None, lineup)
        if not team:
            return None, "Crie seu time com `echo copa iniciar` primeiro."
        if not ok:
            return None, "Seu time ainda nao esta pronto:\n" + "\n".join(errors)
        conn = self._connect()
        cursor = conn.cursor()
        active = self._is_active(cursor)
        conn.close()
        if not active:
            return None, "A Echo Cup ainda nao foi iniciada pela administracao. Use `echo copa` para ver o status."
        last_match = int(team["last_match"] or 0)
        wait = MATCH_COOLDOWN - (now_ts() - last_match)
        if wait > 0:
            hours = wait // 3600
            minutes = (wait % 3600) // 60
            return None, f"Sua proxima tentativa libera em **{hours}h {minutes}min**."

        stage = self._current_stage(progress)
        opponent = self._stage_opponent(user.id, progress, stage)
        opponent_lineup, opponent_formation = self._opponent_lineup(opponent)
        user_team = {"team_name": team["team_name"], "captain_id": team["captain_id"]}
        half_user, half_opp, first_log, scorers = self._simulate_half(
            user_team,
            opponent,
            lineup,
            opponent_lineup,
            team["formation"],
            opponent_formation,
            0,
            0,
            1,
            45,
            f"{user.id}:{now_ts()}:first",
        )
        state = {
            "team_name": team["team_name"],
            "formation": team["formation"],
            "captain_id": team["captain_id"],
            "lineup": lineup,
            "progress": dict(progress) if progress else None,
            "stage": stage,
            "stage_label": STAGE_LABELS[stage],
            "opponent": opponent,
            "opponent_lineup": opponent_lineup,
            "opponent_formation": opponent_formation,
            "half_user": half_user,
            "half_opp": half_opp,
            "first_log": first_log,
            "first_scorers": scorers,
        }
        return state, None

    def finish_match(self, user, state, lineup, formation):
        user_team = {"team_name": state["team_name"], "captain_id": state.get("captain_id")}
        final_user, final_opp, second_log, scorers = self._simulate_half(
            user_team,
            state["opponent"],
            lineup,
            state["opponent_lineup"],
            formation,
            state["opponent_formation"],
            state["half_user"],
            state["half_opp"],
            46,
            90,
            f"{user.id}:{now_ts()}:second:{formation}",
        )
        penalties = None
        penalty_result = None
        stage = state["stage"]
        if stage != "grupos" and final_user == final_opp:
            rng = random.Random(f"{user.id}:{now_ts()}:pen")
            user_power = self._team_power(lineup, formation, state.get("captain_id"), rng)
            opp_power = self._team_power(state["opponent_lineup"], state["opponent_formation"], rng=rng)
            user_pen = rng.randint(3, 5) + (1 if user_power > opp_power else 0)
            opp_pen = rng.randint(3, 5)
            if user_pen == opp_pen:
                user_pen += 1 if user_power >= opp_power else 0
                opp_pen += 1 if user_power < opp_power else 0
            penalties = (user_pen, opp_pen)
            penalty_result = "V" if user_pen > opp_pen else "D"

        if penalty_result:
            result = penalty_result
        elif final_user > final_opp:
            result = "V"
        elif final_user == final_opp:
            result = "E"
        else:
            result = "D"

        reward = MATCH_REWARDS[result] + final_user * 10
        stage_note, stage_reward = self._advance_progress(
            user.id,
            stage,
            state["opponent"]["nome"],
            result,
            final_user,
            final_opp,
            reward,
            scorers + state["first_scorers"],
        )
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE world_cup_teams SET last_match = ? WHERE user_id = ?", (now_ts(), str(user.id)))
        conn.commit()
        conn.close()

        title = f"Echo Cup - {STAGE_LABELS[stage]} - Resultado"
        score_line = f"**{state['team_name']}** {final_user} x {final_opp} **{state['opponent']['nome']}**"
        if penalties:
            score_line += f"\nPenaltis: {penalties[0]} x {penalties[1]}"
        embed = discord.Embed(
            title=title,
            description=score_line + "\n\n" + "\n".join(state["first_log"] + second_log),
            color=discord.Color.green() if result == "V" else discord.Color.red() if result == "D" else discord.Color.gold(),
        )
        embed.add_field(name="Recompensa da partida", value=f"+{reward:,} echobet", inline=True)
        if stage_reward:
            embed.add_field(name="Bonus de fase", value=f"+{stage_reward:,} echobet", inline=True)
        embed.add_field(name="Situacao", value=stage_note, inline=False)
        embed.set_footer(text="TutoriUAU: 60% estrategia, 25% caos, 15% anime gritando no momento certo.")
        return embed

    def _advance_progress(self, user_id, stage, opponent_name, result, goals_for, goals_against, match_reward, scorers):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO world_cup_progress(user_id) VALUES (?)", (str(user_id),))
        cursor.execute("SELECT * FROM world_cup_progress WHERE user_id = ?", (str(user_id),))
        progress = cursor.fetchone()
        cursor.execute("SELECT team_name FROM world_cup_teams WHERE user_id = ?", (str(user_id),))
        team_row = cursor.fetchone()
        team_name = team_row["team_name"] if team_row else str(user_id)
        run_id = int(progress["current_run"] or 1)
        wins = 1 if result == "V" else 0
        draws = 1 if result == "E" else 0
        losses = 1 if result == "D" else 0
        unbeaten = int(progress["unbeaten_streak"] or 0)
        unbeaten = unbeaten + 1 if result in {"V", "E"} else 0
        best_unbeaten = max(int(progress["best_unbeaten_streak"] or 0), unbeaten)

        cursor.execute(
            """
            INSERT INTO world_cup_matches(user_id, opponent_name, stage, user_score, opponent_score, result, created_at, run_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(user_id), opponent_name, stage, goals_for, goals_against, result, now_ts(), run_id),
        )
        for hero_id in scorers:
            cursor.execute(
                """
                INSERT INTO world_cup_player_stats(user_id, hero_id, goals, assists)
                VALUES (?, ?, 1, 0)
                ON CONFLICT(user_id, hero_id) DO UPDATE SET goals = goals + 1
                """,
                (str(user_id), hero_id),
            )

        stage_reward = 0
        next_stage = stage
        medals = 0
        note = "Campanha em andamento."
        if stage == "grupos":
            cursor.execute(
                "SELECT result, user_score, opponent_score FROM world_cup_matches WHERE user_id = ? AND run_id = ? AND stage = 'grupos'",
                (str(user_id), run_id),
            )
            matches = cursor.fetchall()
            if len(matches) >= 3:
                group_points = sum(3 if row["result"] == "V" else 1 if row["result"] == "E" else 0 for row in matches)
                goal_diff = sum(row["user_score"] - row["opponent_score"] for row in matches)
                if group_points >= 5 or (group_points >= 4 and goal_diff >= 0):
                    next_stage = "oitavas"
                    stage_reward = STAGE_REWARDS["grupos"]
                    note = "Voce passou da fase de grupos. O TutoriUAU fingiu surpresa."
                else:
                    next_stage = "eliminado"
                    stage_reward = STAGE_REWARDS["grupos"]
                    note = "Eliminado na fase de grupos. Doi, mas rende echobet de consolacao."
            else:
                note = f"Fase de grupos: {len(matches)}/3 jogos feitos."
        elif result == "V":
            index = STAGE_ORDER.index(stage)
            if stage == "final":
                next_stage = "campeao"
                stage_reward = STAGE_REWARDS["campeao"]
                medals = 1
                self._grant_champion_title(cursor, user_id)
                cursor.execute(
                    """
                    INSERT INTO world_cup_hall(user_id, team_name, title, stat_name, stat_value, created_at)
                    VALUES (?, ?, 'Campeao do Mundo', 'run_id', ?, ?)
                    """,
                    (str(user_id), team_name, str(run_id), now_ts()),
                )
                note = "CAMPEAO DO MUNDO! TutoriUAU esta confiante demais para quem nao entrou em campo."
            else:
                next_stage = STAGE_ORDER[index + 1]
                stage_reward = STAGE_REWARDS.get(next_stage, 0)
                note = f"Classificado para **{STAGE_LABELS[next_stage]}**."
        else:
            if stage == "final":
                stage_reward = STAGE_REWARDS["finalista"]
                note = "Vice-campeao. Quase gloria, muito drama e 700 echobet."
            else:
                stage_reward = STAGE_REWARDS.get(stage, 0)
                note = f"Eliminado em **{STAGE_LABELS[stage]}**."
            next_stage = "eliminado"

        best_stage = self._best_stage(progress["best_stage"], next_stage)
        cursor.execute(
            """
            UPDATE world_cup_progress
            SET stage = ?, points = points + ?, wins = wins + ?, draws = draws + ?, losses = losses + ?,
                goals_for = goals_for + ?, goals_against = goals_against + ?,
                best_stage = ?, medals = medals + ?, unbeaten_streak = ?, best_unbeaten_streak = ?
            WHERE user_id = ?
            """,
            (
                next_stage,
                match_reward + stage_reward,
                wins,
                draws,
                losses,
                goals_for,
                goals_against,
                best_stage,
                medals,
                unbeaten,
                best_unbeaten,
                str(user_id),
            ),
        )
        if next_stage in {"eliminado", "campeao"}:
            cursor.execute(
                "UPDATE world_cup_progress SET current_run = current_run + 1, stage = 'grupos' WHERE user_id = ?",
                (str(user_id),),
            )
        conn.commit()
        conn.close()
        return note, stage_reward

    def _best_stage(self, current, candidate):
        order = ["Fase de grupos", "Oitavas", "Quartas", "Semifinal", "Final", "Campeao"]
        label = STAGE_LABELS.get(candidate, current or "Fase de grupos")
        if label == "Eliminado":
            label = current or "Fase de grupos"
        try:
            return label if order.index(label) > order.index(current or "Fase de grupos") else current
        except ValueError:
            return label

    def _grant_champion_title(self, cursor, user_id):
        item = "token_titulo_campeao_do_mundo"
        add_inventory(cursor, user_id, item, 1)
        cursor.execute(
            "INSERT OR IGNORE INTO player_cosmetics(user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, 'title', 0, ?)",
            (str(user_id), item, now_ts()),
        )

    def _rarity_pool(self, rarity):
        pool = []
        for hero_id in self.sports_pool():
            hero = HEROES.get(hero_id, {})
            if int(hero.get("raridade", 1) or 1) == rarity:
                pool.append(hero_id)
        return pool

    def _roll_copa_rarity(self, pity_4, pity_5):
        if pity_5 >= HARD_PITY_5:
            return 5
        if pity_4 >= HARD_PITY_4:
            return 4
        chance_5 = BASE_RATES[5] + max(0, pity_5 - SOFT_PITY_5 + 1) * 0.05
        chance_4 = BASE_RATES[4] + max(0, pity_4 - SOFT_PITY_4 + 1) * 0.5
        roll = random.uniform(0, 100)
        if roll < chance_5:
            return 5
        if roll < chance_5 + chance_4:
            return 4
        lower = random.uniform(0, BASE_RATES[1] + BASE_RATES[2] + BASE_RATES[3])
        if lower < BASE_RATES[1]:
            return 1
        if lower < BASE_RATES[1] + BASE_RATES[2]:
            return 2
        return 3

    def _choose_copa_hero(self, rarity):
        rarity_order = [1, 2, 3, 4, 5] if rarity == 1 else [rarity, 3, 2, 4, 5]
        for target in rarity_order:
            pool = self._rarity_pool(target)
            if pool:
                hero_id = random.choice(pool)
                return hero_id, int(HEROES.get(hero_id, {}).get("raridade", target))
        pool = self.sports_pool()
        hero_id = random.choice(pool)
        return hero_id, int(HEROES.get(hero_id, {}).get("raridade", 3))

    def info_embed(self, user):
        conn = self._connect()
        cursor = conn.cursor()
        active = self._is_active(cursor)
        cursor.execute("SELECT value FROM world_cup_settings WHERE key = 'started_at'")
        started = cursor.fetchone()
        conn.close()
        embed = discord.Embed(
            title="Echo Cup - Copa do Mundo de Lugnica",
            description=(
                f"Status: **{'Ativa' if active else 'Fechada'}**\n"
                "Monte 11 herois, escolha formacao e dispute grupos, mata-mata e final.\n"
                "TutoriUAU: e futebol, mas com anime. Portanto a fisica pediu demissao."
            ),
            color=discord.Color.green() if active else discord.Color.dark_gray(),
        )
        embed.add_field(
            name="Fluxo",
            value=(
                "`echo copa iniciar` cria/edita seu time.\n"
                "`echo copa jogar` joga uma partida a cada 6 horas.\n"
                "`echo copa loja` e `echo copa resgatar <id>` gastam echobet.\n"
                "`echo copa ranking`, `historico`, `hall`, `banner`, `summon`, `heroi` completam o evento."
            ),
            inline=False,
        )
        embed.add_field(
            name="Formacoes",
            value="\n".join(f"`{name}` - {tip}" for name, tip in FORMATION_TIPS.items()),
            inline=False,
        )
        embed.add_field(
            name="Recompensas",
            value="Derrota 5 | Empate 8 | Vitoria 15 | Gol feito +10 echobet. Melhor fase tambem paga bonus.",
            inline=False,
        )
        if started and str(started[0] or "0") != "0":
            embed.set_footer(text=f"TutoriUAU: evento iniciado em <t:{started[0]}:f>.")
        else:
            embed.set_footer(text="TutoriUAU: esperando o apito administrativo.")
        return embed

    @commands.group(name="copa", aliases=["echocup", "worldcup"], invoke_without_command=True)
    async def copa_group(self, ctx):
        await ctx.send(embed=self.info_embed(ctx.author))

    @copa_group.command(name="iniciar", aliases=["criar", "editar"])
    async def copa_iniciar(self, ctx, *, nome: str = None):
        view = CopaTeamBuilderView(self, ctx, team_name=nome)
        message = await ctx.send(embed=view.build_embed(), view=view)
        view.message = message

    @copa_group.command(name="time", aliases=["meutime", "team"])
    async def copa_time(self, ctx):
        await ctx.send(embed=self.team_embed(ctx.author))

    @copa_group.command(name="jogar", aliases=["partida", "play"])
    async def copa_jogar(self, ctx):
        state, error = self._prepare_match(ctx.author)
        if error:
            return await ctx.send(error)
        view = CopaMatchView(self, ctx, state)
        await ctx.send(embed=view.first_half_embed(), view=view)

    @copa_group.command(name="loja", aliases=["shop"])
    async def copa_loja(self, ctx):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO world_cup_progress(user_id) VALUES (?)", (str(ctx.author.id),))
        cursor.execute("SELECT points FROM world_cup_progress WHERE user_id = ?", (str(ctx.author.id),))
        points = cursor.fetchone()["points"]
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="Loja da Echo Cup",
            description=f"Saldo: **{points:,} echobet**\nTutoriUAU: aposte com responsabilidade. Ou com personagens 5 estrelas, que e quase a mesma irresponsabilidade.",
            color=discord.Color.gold(),
        )
        lines = [f"`{item_id}` **{item['name']}** - {item['cost']:,} echobet" for item_id, item in SHOP_ITEMS.items()]
        embed.add_field(name="Itens", value=trim("\n".join(lines), 1024), inline=False)
        embed.set_footer(text="Use `echo copa resgatar <id>`.")
        await ctx.send(embed=embed)

    @copa_group.command(name="resgatar", aliases=["comprar", "buy"])
    async def copa_resgatar(self, ctx, item_id: int = None):
        if item_id not in SHOP_ITEMS:
            return await ctx.send("Use `echo copa loja` para ver os IDs.")
        item = SHOP_ITEMS[item_id]
        user_id = str(ctx.author.id)
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO world_cup_progress(user_id) VALUES (?)", (user_id,))
        cursor.execute("SELECT points FROM world_cup_progress WHERE user_id = ?", (user_id,))
        points = cursor.fetchone()["points"]
        if points < item["cost"]:
            conn.close()
            return await ctx.send(f"Echobet insuficiente. Voce tem **{points:,}** e precisa de **{item['cost']:,}**.")
        if item["kind"] == "cosmetic":
            add_inventory(cursor, user_id, item["item"], 1)
            cursor.execute(
                "INSERT OR IGNORE INTO player_cosmetics(user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, item["item"], item["type"], now_ts()),
            )
        elif item["kind"] == "tickets":
            add_tickets(cursor, user_id, item["amount"])
        elif item["kind"] == "gems":
            cursor.execute("UPDATE players SET gems = COALESCE(gems, 0) + ? WHERE user_id = ?", (item["amount"], user_id))
        elif item["kind"] == "pet":
            cursor.execute(
                "INSERT INTO pets(user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, ?, 1, 0)",
                (user_id, item["pet_id"], item["pet_name"], item["rarity"]),
            )
        cursor.execute("UPDATE world_cup_progress SET points = points - ? WHERE user_id = ?", (item["cost"], user_id))
        conn.commit()
        conn.close()
        await ctx.send(f"Compra concluida: **{item['name']}**. TutoriUAU carimbou o recibo e fingiu que leu os termos.")

    @copa_group.command(name="ranking", aliases=["rank", "classificacao"])
    async def copa_ranking(self, ctx):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.user_id, COALESCE(t.team_name, p.user_id) AS team_name, p.wins, p.draws, p.losses,
                   p.goals_for, p.goals_against, p.points, p.best_stage
            FROM world_cup_progress p
            LEFT JOIN world_cup_teams t ON t.user_id = p.user_id
            ORDER BY (p.wins * 3 + p.draws) DESC, (p.goals_for - p.goals_against) DESC, p.goals_for DESC
            LIMIT 15
            """
        )
        rows = cursor.fetchall()
        conn.close()
        embed = discord.Embed(title="Ranking Global - Echo Cup", color=discord.Color.blue())
        if not rows:
            embed.description = "Nenhum time pontuou ainda."
        else:
            lines = []
            for index, row in enumerate(rows, start=1):
                score = row["wins"] * 3 + row["draws"]
                gd = row["goals_for"] - row["goals_against"]
                lines.append(f"`{index:02}` **{row['team_name']}** - {score} pts | V/E/D {row['wins']}/{row['draws']}/{row['losses']} | SG {gd:+} | {row['best_stage']}")
            embed.description = "\n".join(lines)
        embed.set_footer(text="TutoriUAU: ranking global, ego local.")
        await ctx.send(embed=embed)

    @copa_group.command(name="historico", aliases=["history"])
    async def copa_historico(self, ctx):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT opponent_name, stage, user_score, opponent_score, result, created_at
            FROM world_cup_matches
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 5
            """,
            (str(ctx.author.id),),
        )
        rows = cursor.fetchall()
        conn.close()
        embed = discord.Embed(title="Ultimas partidas da Echo Cup", color=discord.Color.blurple())
        if not rows:
            embed.description = "Nenhuma partida registrada."
        else:
            embed.description = "\n".join(
                f"<t:{row['created_at']}:d> | **{STAGE_LABELS.get(row['stage'], row['stage'])}** vs {row['opponent_name']} | {row['user_score']} x {row['opponent_score']} | {row['result']}"
                for row in rows
            )
        await ctx.send(embed=embed)

    @copa_group.command(name="banner")
    async def copa_banner(self, ctx):
        pool = self.sports_pool()
        by_origin = Counter(HEROES.get(hero_id, {}).get("origem", "?") for hero_id in pool)
        embed = discord.Embed(
            title="Banner da Echo Cup",
            description=(
                f"Custo: **{COPA_SUMMON_COST:,} Gold** por summon.\n"
                "Taxas: 1⭐ 50% | 2⭐ 25% | 3⭐ 19% | 4⭐ 5% | 5⭐ 1%.\n"
                "Aqui so entram personagens de anime de esporte. TutoriUAU: finalmente um banner que sabe correr."
            ),
            color=discord.Color.green(),
        )
        embed.add_field(name="Origens", value="\n".join(f"**{origin}**: {count}" for origin, count in by_origin.items()), inline=False)
        await ctx.send(embed=embed)

    @copa_group.command(name="summon")
    async def copa_summon(self, ctx, amount: int = 1):
        amount = max(1, min(10, int(amount or 1)))
        pool = self.sports_pool()
        if not pool:
            return await ctx.send("O banner da Copa ainda nao tem herois elegiveis.")
        user_id = str(ctx.author.id)
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        if not player:
            conn.close()
            return await ctx.send("Use `echo iniciar` primeiro.")
        cost = COPA_SUMMON_COST * amount
        if int(player["gold"] or 0) < cost:
            conn.close()
            return await ctx.send(f"Ouro insuficiente. Custo: **{cost:,} Gold**.")
        cursor.execute(
            """
            INSERT OR IGNORE INTO summon_data(user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star, total_divine)
            VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            """,
            (user_id,),
        )
        cursor.execute("SELECT pity_4, pity_5 FROM summon_data WHERE user_id = ?", (user_id,))
        pity = cursor.fetchone()
        pity_4, pity_5 = int(pity["pity_4"] or 0), int(pity["pity_5"] or 0)
        cursor.execute("SELECT DISTINCT hero_id FROM heroes WHERE user_id = ?", (user_id,))
        owned = {self._resolve_hero_id(row[0]) or row[0] for row in cursor.fetchall()}
        results = []
        stats = Counter()
        for index in range(amount):
            pity_4 += 1
            pity_5 += 1
            rarity = self._roll_copa_rarity(pity_4, pity_5)
            if amount == 10 and index == 9 and not any(item["rarity"] >= 3 for item in results):
                rarity = 3
            hero_id, real_rarity = self._choose_copa_hero(rarity)
            if real_rarity >= 5:
                pity_5 = 0
                pity_4 = 0
            elif real_rarity == 4:
                pity_4 = 0
            results.append({"hero_id": hero_id, "rarity": real_rarity, "new": hero_id not in owned})
            owned.add(hero_id)
            stats[real_rarity] += 1
            cursor.execute(
                "INSERT INTO heroes(user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)",
                (user_id, hero_id, real_rarity),
            )
        cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (cost, user_id))
        cursor.execute(
            """
            UPDATE summon_data
            SET pity_4 = ?, pity_5 = ?, total_summons = total_summons + ?,
                total_1_star = total_1_star + ?, total_2_star = total_2_star + ?,
                total_3_star = total_3_star + ?, total_4_star = total_4_star + ?,
                total_5_star = total_5_star + ?
            WHERE user_id = ?
            """,
            (pity_4, pity_5, amount, stats[1], stats[2], stats[3], stats[4], stats[5], user_id),
        )
        conn.commit()
        conn.close()
        rarest = max(results, key=lambda item: item["rarity"])
        hero_file = self._local_hero_file(rarest["hero_id"], "copa_summon")
        embed = discord.Embed(
            title="Summon da Echo Cup",
            description=f"{ctx.author.mention} gastou **{cost:,} Gold** no banner esportivo.\n\n",
            color=discord.Color.green(),
        )
        for item in results:
            hero = HEROES.get(item["hero_id"], {})
            line = f"{stars_text(item['rarity'])} | {hero.get('emoji', '')} **{hero.get('nome', item['hero_id'])}**"
            if item["new"]:
                line += " [NEW]"
            embed.description += line + "\n"
        embed.set_footer(text=f"Pity 4⭐ {pity_4}/{HARD_PITY_4} | Pity 5⭐ {pity_5}/{HARD_PITY_5}")
        if hero_file:
            embed.set_image(url=f"attachment://{hero_file.filename}")
            await ctx.send(embed=embed, file=hero_file)
        else:
            await ctx.send(embed=embed)

    @copa_group.command(name="heroi", aliases=["hero"])
    async def copa_heroi(self, ctx, *, query: str = None):
        if not query:
            return await ctx.send("Use `echo copa heroi <nome ou id>`.")
        hero_id = self._resolve_hero_id(query)
        if not hero_id:
            return await ctx.send("Nao encontrei esse heroi na ficha da Copa.")
        data = WORLD_CUP_PLAYERS[hero_id]
        hero = HEROES.get(hero_id, {})
        embed = discord.Embed(
            title=f"{data.get('nome', hero.get('nome', hero_id))} - Ficha da Copa",
            description=f"{stars_text(hero.get('raridade', 1))} | {hero.get('origem', 'Origem desconhecida')}",
            color=discord.Color.green(),
        )
        positions = ", ".join(f"{pos[0]} ({pos[1]})" for pos in data.get("posicoes", []))
        embed.add_field(name="Posicoes", value=positions or "Sem posicao", inline=False)
        stats = ["ataque", "defesa", "passe", "velocidade", "finalizacao", "goleiro", "mental"]
        embed.add_field(name="Atributos", value="\n".join(f"**{stat.title()}**: {data.get(stat, 0)}" for stat in stats), inline=True)
        skill = data.get("habilidade", {})
        embed.add_field(name=skill.get("nome", "Habilidade"), value=skill.get("efeito", "Sem descricao."), inline=False)
        embed.set_footer(text="TutoriUAU: ficha esportiva. Nao tente usar isso como exame medico.")
        hero_file = self._local_hero_file(hero_id, "copa_heroi")
        if hero_file:
            embed.set_image(url=f"attachment://{hero_file.filename}")
            await ctx.send(embed=embed, file=hero_file)
        else:
            await ctx.send(embed=embed)

    @copa_group.command(name="hall")
    async def copa_hall(self, ctx):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT team_name, title, created_at
            FROM world_cup_hall
            WHERE title = 'Campeao do Mundo'
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        champions = cursor.fetchall()
        cursor.execute(
            """
            SELECT s.user_id, s.hero_id, s.goals, COALESCE(t.team_name, s.user_id) AS team_name
            FROM world_cup_player_stats s
            LEFT JOIN world_cup_teams t ON t.user_id = s.user_id
            ORDER BY s.goals DESC
            LIMIT 1
            """
        )
        scorer = cursor.fetchone()
        cursor.execute(
            """
            SELECT COALESCE(t.team_name, p.user_id) AS team_name, goals_for FROM world_cup_progress p
            LEFT JOIN world_cup_teams t ON t.user_id = p.user_id
            ORDER BY goals_for DESC
            LIMIT 1
            """
        )
        offensive = cursor.fetchone()
        cursor.execute(
            """
            SELECT COALESCE(t.team_name, p.user_id) AS team_name, best_unbeaten_streak FROM world_cup_progress p
            LEFT JOIN world_cup_teams t ON t.user_id = p.user_id
            ORDER BY best_unbeaten_streak DESC
            LIMIT 1
            """
        )
        streak = cursor.fetchone()
        conn.close()
        embed = discord.Embed(title="Hall da Echo Cup", color=discord.Color.purple())
        if champions:
            embed.add_field(
                name="Campeoes anteriores",
                value="\n".join(f"**{row['team_name']}** - <t:{row['created_at']}:d>" for row in champions),
                inline=False,
            )
        else:
            embed.add_field(name="Campeoes anteriores", value="Nenhum campeao registrado ainda.", inline=False)
        if scorer:
            hero = WORLD_CUP_PLAYERS.get(scorer["hero_id"], {})
            embed.add_field(name="Maior artilheiro", value=f"**{hero.get('nome', scorer['hero_id'])}** ({scorer['team_name']}) - {scorer['goals']} gols", inline=False)
        if offensive:
            embed.add_field(name="Time mais ofensivo", value=f"**{offensive['team_name']}** - {offensive['goals_for']} gols", inline=False)
        if streak:
            embed.add_field(name="Maior sequencia invicta", value=f"**{streak['team_name']}** - {streak['best_unbeaten_streak']} jogos", inline=False)
        embed.set_footer(text="TutoriUAU: placa de honra, poeira e estatistica.")
        await ctx.send(embed=embed)

    async def admin_dispatch(self, ctx, action=None, payload=None):
        action = str(action or "").lower()
        conn = self._connect()
        cursor = conn.cursor()
        if action in {"iniciar", "start", "abrir"}:
            cursor.execute("UPDATE world_cup_settings SET value = '1' WHERE key = 'active'")
            cursor.execute("UPDATE world_cup_settings SET value = ? WHERE key = 'started_at'", (str(now_ts()),))
            cursor.execute("UPDATE world_cup_settings SET value = '0' WHERE key = 'ended_at'")
            conn.commit()
            conn.close()
            return await ctx.send("Echo Cup iniciada. TutoriUAU apitou e ja culpou o RNG.")
        if action in {"encerrar", "end", "fechar"}:
            cursor.execute("UPDATE world_cup_settings SET value = '0' WHERE key = 'active'")
            cursor.execute("UPDATE world_cup_settings SET value = ? WHERE key = 'ended_at'", (str(now_ts()),))
            conn.commit()
            conn.close()
            return await ctx.send("Echo Cup encerrada. Os gramados foram devolvidos ao caos.")
        if action == "reset":
            target_id = re.sub(r"\D", "", str(payload or ""))
            if not target_id:
                conn.close()
                return await ctx.send("Uso: `echo adm copa reset @user`")
            for table in ["world_cup_teams", "world_cup_lineups", "world_cup_progress", "world_cup_matches", "world_cup_player_stats"]:
                cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (target_id,))
            conn.commit()
            conn.close()
            return await ctx.send(f"Progresso da Copa resetado para <@{target_id}>.")
        if action in {"echobet", "pontos"}:
            parts = str(payload or "").split()
            if len(parts) < 2:
                conn.close()
                return await ctx.send("Uso: `echo adm copa echobet @user <quantidade>`")
            target_id = re.sub(r"\D", "", parts[0])
            try:
                amount = int(parts[1])
            except ValueError:
                conn.close()
                return await ctx.send("Quantidade invalida.")
            cursor.execute("INSERT OR IGNORE INTO world_cup_progress(user_id) VALUES (?)", (target_id,))
            cursor.execute("UPDATE world_cup_progress SET points = points + ? WHERE user_id = ?", (amount, target_id))
            conn.commit()
            conn.close()
            return await ctx.send(f"{amount:,} echobet entregues para <@{target_id}>.")
        conn.close()
        await ctx.send("Uso: `echo adm copa iniciar|encerrar|reset @user|echobet @user <qtd>`")


async def setup(bot):
    await bot.add_cog(Copa(bot))
