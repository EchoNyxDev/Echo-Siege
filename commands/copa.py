import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import random
import os
import sys
import json
import time
import re
import unicodedata
from collections import Counter

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.world_cup_players import WORLD_CUP_PLAYERS
    from data.world_cup_opponents import WORLD_CUP_OPPONENTS
    from utils.hero_images import get_hero_attachment
except Exception:
    HEROES = {}
    WORLD_CUP_PLAYERS = {}
    WORLD_CUP_OPPONENTS = {}
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
    "4-3-3": "Equilíbrio tático com ataque rápido pelas pontas",
    "4-4-2": "Formação clássica de segurança e posse central",
    "4-2-3-1": "Meio-campo denso com foco em passes de infiltração",
    "3-5-2": "Pressão total no ataque com zaga exposta",
    "5-3-2": "Muralha defensiva fechada para jogar no contra-ataque",
}

STAGE_ORDER = ["grupos", "oitavas", "quartas", "semi", "final"]
STAGE_LABELS = {
    "grupos": "Fase de Grupos",
    "oitavas": "Oitavas de Final",
    "quartas": "Quartas de Final",
    "semi": "Semifinal",
    "final": "Grande Final",
    "campeao": "Campeão do Mundo 🏆",
    "eliminado": "Eliminado",
}

STAGE_REWARDS = {
    "grupos": 100,
    "oitavas": 250,
    "quartas": 500,
    "semi": 1000,
    "finalista": 1500,
    "campeao": 3000,
}

MATCH_REWARDS = {"V": 100, "E": 45, "D": 20}
MATCH_COOLDOWN = 6 * 60 * 60  # 6 Horas de Cooldown por Campanha Completa
COPA_SUMMON_COST = 900
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

# ========================================================
# EVENTOS DE JOGO E TEXTOS DE LORE DE CAMPO
# ========================================================
EVENT_TEMPLATES = {
    "gol": [
        "⚽ **GOOOL!** {player} recebe um passe açucarado e fuzila no canto sem dar chances!",
        "⚽ **GOOOL!** {player} aciona sua técnica especial e manda uma bomba que estufa as redes!",
        "⚽ **GOOOL!** Após rebote caótico na área, {player} se estica todo e empurra para o fundo!"
    ],
    "defesa": [
        "🧤 **DEFESAÇA!** {defender} voa no ângulo para espalmar o chute perigoso de {attacker}!",
        "🧤 **PAREDE!** {defender} antecipa a jogada perfeitamente e rouba a bola de {attacker}!",
        "🧤 **MILAGRE!** {defender} salva em cima da linha o que seria o gol certo de {attacker}!"
    ],
    "amarelo": [
        "🟨 **CARTÃO AMARELO!** {player} chega atrasado na dividida e recebe a punição administrativa.",
        "🟨 **CARTÃO AMARELO!** {player} impede o contra-ataque puxando a túnica do adversário."
    ],
    "vermelho": [
        "🟥 **CARTÃO VERMELHO!** {player} entra de carrinho por trás com violência excessiva e é EXPULSO!"
    ],
    "lesao": [
        "🩹 **LESÃO TEMPORÁRIA!** {player} sente a musculatura após um arranque explosivo e manca em campo."
    ],
    "penalti_gol": [
        "🎯 **PÊNALTI!** {player} assume a responsabilidade e cobra com extrema frieza! **GOOOL!**"
    ],
    "penalti_defendido": [
        "🎯 **PÊNALTI PERDIDO!** {attacker} bate forte, mas {defender} defende espetacularmente!"
    ],
    "falta_perigosa": [
        "⚠️ **FALTA PERIGOSA!** {player} ajeita a bola com carinho... O chute colocado carimba a trave!"
    ],
    "virada_heroica": [
        "🔥 **MOMENTO ÉPICO!** {player} inflama seus companheiros na base do grito e do carisma!"
    ],
    "falha_bizarra": [
        "🫠 **FALHA BIZARRA!** {player} tenta recuar com o calcanhar, fura a bola e passa vergonha!"
    ],
    "substituicao": [
        "🔄 **MUDANÇA TÁTICA!** {player} altera seu posicionamento para tentar surpreender a defesa."
    ]
}

def now_ts():
    return int(time.time())

def normalize_text(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

def ensure_extra_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_teams (
            user_id TEXT PRIMARY KEY,
            team_name TEXT,
            formation TEXT,
            captain_id TEXT,
            created_at INTEGER DEFAULT 0,
            last_match INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_lineups (
            user_id TEXT,
            slot INTEGER,
            hero_instance_id INTEGER,
            hero_id TEXT,
            position TEXT,
            PRIMARY KEY (user_id, slot)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_progress (
            user_id TEXT PRIMARY KEY,
            points INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            best_stage TEXT DEFAULT 'Fase de grupos',
            current_run INTEGER DEFAULT 1,
            cooldown_end INTEGER DEFAULT 0,
            stage TEXT DEFAULT 'grupos',
            group_match_num INTEGER DEFAULT 0,
            p_points INTEGER DEFAULT 0,
            p_gf INTEGER DEFAULT 0,
            p_ga INTEGER DEFAULT 0,
            opp1_id TEXT, opp1_points INTEGER DEFAULT 0, opp1_gf INTEGER DEFAULT 0, opp1_ga INTEGER DEFAULT 0,
            opp2_id TEXT, opp2_points INTEGER DEFAULT 0, opp2_gf INTEGER DEFAULT 0, opp2_ga INTEGER DEFAULT 0,
            opp3_id TEXT, opp3_points INTEGER DEFAULT 0, opp3_gf INTEGER DEFAULT 0, opp3_ga INTEGER DEFAULT 0,
            medals INTEGER DEFAULT 0,
            unbeaten_streak INTEGER DEFAULT 0,
            best_unbeaten_streak INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(world_cup_progress)")
    cols = {row[1] for row in cursor.fetchall()}
    novas_colunas = {
        "group_match_num": "INTEGER DEFAULT 0",
        "p_points": "INTEGER DEFAULT 0",
        "p_gf": "INTEGER DEFAULT 0",
        "p_ga": "INTEGER DEFAULT 0",
        "opp1_id": "TEXT", "opp1_points": "INTEGER DEFAULT 0", "opp1_gf": "INTEGER DEFAULT 0", "opp1_ga": "INTEGER DEFAULT 0",
        "opp2_id": "TEXT", "opp2_points": "INTEGER DEFAULT 0", "opp2_gf": "INTEGER DEFAULT 0", "opp2_ga": "INTEGER DEFAULT 0",
        "opp3_id": "TEXT", "opp3_points": "INTEGER DEFAULT 0", "opp3_gf": "INTEGER DEFAULT 0", "opp3_ga": "INTEGER DEFAULT 0",
        "current_run": "INTEGER DEFAULT 1",
        "stage": "TEXT DEFAULT 'grupos'",
        "points": "INTEGER DEFAULT 0",
        "cooldown_end": "INTEGER DEFAULT 0"
    }
    for col, ddl in novas_colunas.items():
        if col not in cols:
            cursor.execute(f"ALTER TABLE world_cup_progress ADD COLUMN {col} {ddl}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            opponent_name TEXT,
            stage TEXT,
            user_score INTEGER,
            opponent_score INTEGER,
            result TEXT,
            created_at INTEGER,
            run_id INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_player_stats (
            user_id TEXT,
            hero_id TEXT,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, hero_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_cup_settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO world_cup_settings (key, value) VALUES ('active', '1')")
    cursor.execute("INSERT OR IGNORE INTO world_cup_settings (key, value) VALUES ('started_at', '0')")


# ==========================================
# PAINEL DA PRANCHETA (ESCALAÇÃO)
# ==========================================
class TeamNameModal(discord.ui.Modal, title="Nome da Equipe"):
    team_name = discord.ui.TextInput(
        label="Digite o nome do seu time",
        placeholder="Ex.: TutoriUAU FC",
        min_length=3,
        max_length=40,
    )

    def __init__(self, view):
        super().__init__()
        self.view_ref = view

    async def on_submit(self, interaction):
        self.view_ref.team_name = str(self.team_name.value).strip()[:40]
        self.view_ref.rebuild_ui()
        await interaction.response.edit_message(embed=self.view_ref.build_embed(), view=self.view_ref)


class EditCopaSlotSelect(discord.ui.Select):
    def __init__(self, builder, slot_num, heroes):
        self.builder = builder
        self.slot_num = slot_num
        self.user_id = builder.ctx.author.id
        
        options = [
            discord.SelectOption(label="[ Esvaziar Slot ]", value="0", description="Deixa a posição vaga", emoji="🗑️")
        ]
        
        # Pega apenas os 24 melhores heróis do usuário por Score na Posição ou Nível para não estourar o Discord
        pos = self.builder.get_slot_position(slot_num)
        heroes.sort(key=lambda r: builder.cog.player_position_score(r["hero_id"], pos) + r["level"], reverse=True)

        for row in heroes[:24]:
            instance_id = row["instance_id"]
            hero_id = row["hero_id"]
            lvl = row["level"]
            stars = row["stars"]
            h_data = WORLD_CUP_PLAYERS.get(hero_id, {})
            name = h_data.get("nome", hero_id)
            
            options.append(discord.SelectOption(
                label=f"{name} (ID: {instance_id})",
                value=str(instance_id),
                description=f"Lv {lvl} | {'★' * stars}",
                emoji=HEROES.get(hero_id, {}).get("emoji", "⚽")
            ))
            
        super().__init__(
            placeholder=f"Escolha o jogador para o Slot {slot_num} ({pos})...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        instance_id = int(self.values[0])
        position = self.builder.get_slot_position(self.slot_num)
        
        if instance_id == 0:
            self.builder.lineup.pop(self.slot_num, None)
        else:
            ok, msg = self.builder.set_slot(self.slot_num, instance_id, position)
            if not ok:
                return await interaction.response.send_message(msg, ephemeral=True)
                
        self.builder.rebuild_ui()
        await interaction.response.edit_message(embed=self.builder.build_embed(), view=self.builder)


class ChooseCopaSlotView(discord.ui.View):
    def __init__(self, builder, slot_num, heroes):
        super().__init__(timeout=180)
        self.builder = builder
        self.add_item(EditCopaSlotSelect(builder, slot_num, heroes))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.builder.ctx.author.id

    @discord.ui.button(label="Voltar", style=discord.ButtonStyle.danger, emoji="⬅️")
    async def btn_back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.builder.build_embed(), view=self.builder)


class SlotSelectionDropdown(discord.ui.Select):
    def __init__(self, builder):
        self.builder = builder
        options = []
        for slot in range(1, 12):
            pos = builder.get_slot_position(slot)
            item = builder.lineup.get(slot)
            status = "Vazio"
            if item:
                hero_data = WORLD_CUP_PLAYERS.get(item["hero_id"], {})
                status = f"{hero_data.get('nome', item['hero_id'])}"
                
            options.append(discord.SelectOption(
                label=f"Slot {slot:02d} ({pos})",
                value=str(slot),
                description=f"Atual: {status}"
            ))
            
        super().__init__(
            placeholder="Selecione o Slot que deseja escalar...",
            options=options,
            min_values=1,
            max_values=1,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        slot_num = int(self.values[0])
        owned_heroes = self.builder.owned()
        
        view_select = ChooseCopaSlotView(self.builder, slot_num, owned_heroes)
        
        pos = self.builder.get_slot_position(slot_num)
        embed = discord.Embed(
            title=f"Escalando o Slot {slot_num:02d} ({pos})",
            description=f"Selecione um dos seus heróis da Copa abaixo para assumir a posição de **{POSITIONS.get(pos, pos)}**.",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=view_select)


class CaptainSelectionDropdown(discord.ui.Select):
    def __init__(self, builder):
        self.builder = builder
        options = []
        for slot, item in sorted(builder.lineup.items()):
            hero_data = WORLD_CUP_PLAYERS.get(item["hero_id"], {})
            options.append(discord.SelectOption(
                label=f"{hero_data.get('nome', item['hero_id'])} ({item['position']})",
                value=str(item["instance_id"])
            ))
        if not options:
            options.append(discord.SelectOption(label="Nenhum jogador escalado", value="0", disabled=True))
            
        super().__init__(
            placeholder="Escolha quem vestirá a braçadeira de Capitão...",
            options=options,
            min_values=1,
            max_values=1,
            row=3
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "0":
            return
        self.builder.captain_id = self.values[0]
        self.builder.rebuild_ui()
        await interaction.response.edit_message(embed=self.builder.build_embed(), view=self.builder)


class FormationSelect(discord.ui.Select):
    def __init__(self, parent, row=0):
        options = [
            discord.SelectOption(label=formation, value=formation, description=FORMATION_TIPS[formation])
            for formation in FORMATIONS
        ]
        super().__init__(placeholder="Escolha a Formação Tática", options=options, min_values=1, max_values=1, row=row)
        self.parent = parent

    async def callback(self, interaction):
        self.parent.formation = self.values[0]
        self.parent.rebuild_ui()
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
        self._load_existing()
        self.rebuild_ui()

    async def interaction_check(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Essa prancheta não é sua.", ephemeral=True)
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
        conn.close()

    def owned(self):
        return self.cog.owned_copa_heroes(self.ctx.author.id)

    def get_slot_position(self, slot_num):
        form_slots = FORMATIONS.get(self.formation, FORMATIONS["4-3-3"])
        positions = []
        for pos, amount in form_slots.items():
            positions.extend([pos] * amount)
        return positions[slot_num - 1] if slot_num <= len(positions) else "ATA"

    def set_slot(self, slot_num, instance_id, position):
        owned_list = self.owned()
        owned_dict = {row["instance_id"]: row["hero_id"] for row in owned_list}
        
        if instance_id not in owned_dict:
            return False, "Este herói não pertence à sua conta para o torneio."
        
        # Remove clones de outros slots
        for s, item in list(self.lineup.items()):
            if item["instance_id"] == instance_id and s != slot_num:
                self.lineup.pop(s, None)
                
        self.lineup[slot_num] = {
            "instance_id": instance_id,
            "hero_id": owned_dict[instance_id],
            "position": position,
        }
        return True, "Escalado."

    def auto_fill(self):
        owned = self.owned()
        if len(owned) < 11:
            return False, "Você precisa ter pelo menos 11 heróis no catálogo esportivo (`echo copa summon`)."
            
        self.lineup = {}
        used_instances = set()
        form_slots = FORMATIONS.get(self.formation, FORMATIONS["4-3-3"])
        slot = 1
        
        for pos, amount in form_slots.items():
            for _ in range(amount):
                candidates = []
                for row in owned:
                    if row["instance_id"] in used_instances:
                        continue
                    score = self.cog.player_position_score(row["hero_id"], pos)
                    score += row["rarity"] * 5 + row["level"] * 0.1
                    candidates.append((score, row))
                    
                if candidates:
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    best_row = candidates[0][1]
                    self.lineup[slot] = {
                        "instance_id": best_row["instance_id"],
                        "hero_id": best_row["hero_id"],
                        "position": pos
                    }
                    used_instances.add(best_row["instance_id"])
                slot += 1
                
        if self.lineup:
            best_opt = max(self.lineup.values(), key=lambda i: self.cog.player_position_score(i["hero_id"], i["position"]))
            self.captain_id = str(best_opt["instance_id"])
            
        self.rebuild_ui()
        return True, "Auto-escalado com sucesso!"

    def rebuild_ui(self):
        for child in list(self.children):
            if isinstance(child, (CaptainSelectionDropdown, SlotSelectionDropdown, FormationSelect)):
                self.remove_item(child)
                
        self.add_item(SlotSelectionDropdown(self))
        self.add_item(FormationSelect(self, row=1))
        if self.lineup:
            self.add_item(CaptainSelectionDropdown(self))

    def build_embed(self):
        ok, errors = self.cog.validate_lineup(self.ctx.author.id, self.formation, self.captain_id, self.lineup)
        embed = discord.Embed(
            title="📋 Prancheta Tática da Copa",
            description=(
                f"Time: **{self.team_name}**\n"
                f"Esquema: **{self.formation}** — {FORMATION_TIPS[self.formation]}\n"
                f"Capitão: **{f'ID {self.captain_id}' if self.captain_id else 'Não Definido'}**\n"
            ),
            color=discord.Color.green() if ok else discord.Color.orange(),
        )
        
        lineup_text = ""
        for slot in range(1, 12):
            pos = self.get_slot_position(slot)
            item = self.lineup.get(slot)
            if item:
                h_data = WORLD_CUP_PLAYERS.get(item["hero_id"], {})
                cap_str = " 👑" if str(item["instance_id"]) == str(self.captain_id) else ""
                lineup_text += f"`{slot:02d}.` **{h_data.get('nome', item['hero_id'])}**{cap_str} - `{pos}` *(ID: {item['instance_id']})*\n"
            else:
                lineup_text += f"`{slot:02d}.` *Vago — Requer {pos}*\n"
                
        embed.add_field(name="Titulares Escalados", value=lineup_text, inline=False)
        
        if not ok:
            embed.add_field(name="⚠️ Pendências Táticas", value="\n".join(f"• {err}" for err in errors), inline=False)
        else:
            embed.add_field(name="✅ Validação", value="Tudo pronto para o pontapé inicial!", inline=False)
            
        embed.set_footer(text="TutoriUAU • Use os menus abaixo para organizar seu time.")
        return embed

    @discord.ui.button(label="Nome", style=discord.ButtonStyle.secondary, row=2)
    async def btn_name(self, interaction, button):
        await interaction.response.send_modal(TeamNameModal(self))

    @discord.ui.button(label="Auto Preencher", style=discord.ButtonStyle.primary, row=2)
    async def btn_autofill(self, interaction, button):
        ok, msg = self.auto_fill()
        if not ok:
            return await interaction.response.send_message(msg, ephemeral=True)
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Salvar Time", style=discord.ButtonStyle.success, row=2)
    async def btn_save(self, interaction, button):
        ok, errors = self.cog.validate_lineup(self.ctx.author.id, self.formation, self.captain_id, self.lineup)
        if not ok:
            return await interaction.response.send_message("❌ Corrija as pendências antes de salvar:\n" + "\n".join(errors), ephemeral=True)
            
        self.cog.save_team(self.ctx.author.id, self.team_name, self.formation, self.captain_id, self.lineup)
        await interaction.response.edit_message(content="⚽ **Estratégia salva!** O time está pronto para a rinha.", embed=self.cog.team_embed(self.ctx.author), view=None)
        self.stop()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger, row=2)
    async def btn_cancel(self, interaction, button):
        await interaction.response.edit_message(content="Alterações descartadas. O TutoriUAU queimou a prancheta.", embed=None, view=None)
        self.stop()


class MatchFormationSelect(discord.ui.Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label=formation, value=formation, description=FORMATION_TIPS[formation])
            for formation in FORMATIONS
        ]
        super().__init__(placeholder="Mudar Formação no 2º Tempo", min_values=1, max_values=1, options=options, row=0)
        self.view_ref = view

    async def callback(self, interaction):
        self.view_ref.formation = self.values[0]
        await interaction.response.edit_message(embed=self.view_ref.first_half_embed(), view=self.view_ref)


class SubstitutionModal(discord.ui.Modal, title="Substituição da Copa"):
    slot = discord.ui.TextInput(label="Slot a trocar", placeholder="1 a 11", min_length=1, max_length=2)
    hero_instance_id = discord.ui.TextInput(label="Novo ID do herói", placeholder="ID do banco", min_length=1, max_length=12)
    position = discord.ui.TextInput(label="Posição", placeholder="Opcional: GOL/ZAG/LAT/VOL/MC/MEI/PE/PD/ATA", required=False, max_length=3)

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
            await interaction.response.send_message("Esse jogo é de outro técnico. TutoriUAU mostrou o cartão amarelo.", ephemeral=True)
            return False
        return True

    def first_half_embed(self):
        embed = discord.Embed(
            title=f"Echo Cup - {self.state['stage_label']} - Intervalo",
            description=(
                f"**{self.state['team_name']}** {self.state['half_user']} x {self.state['half_opp']} **{self.state['opponent']['nome']}**\n"
                f"Formação atual: **{self.formation}**\n\n"
                + "\n".join(self.state["first_log"])
            ),
            color=discord.Color.gold(),
        )
        embed.add_field(
            name="Vestiário",
            value="Antes do segundo tempo você pode mudar a formação ou fazer uma substituição por ID.",
            inline=False,
        )
        return embed

    def substitute(self, raw_slot, raw_instance, raw_position):
        try:
            slot = int(raw_slot)
            instance_id = int(raw_instance)
        except ValueError:
            return False, "Slot e ID precisam ser números."
        if slot < 1 or slot > 11:
            return False, "Slot inválido."
        owned = {int(row["instance_id"]): row for row in self.cog.owned_copa_heroes(self.ctx.author.id)}
        row = owned.get(instance_id)
        if not row:
            return False, "Esse herói não pertence a você ou não tem ficha da Copa."
        if any(int(item["instance_id"]) == instance_id for item in self.lineup.values()):
            return False, "Esse herói já está em campo."
            
        pos_map = self.cog.get_formation_positions(self.formation)
        position = str(raw_position or "").upper().strip()
        if not position:
            position = pos_map[slot - 1] if slot <= len(pos_map) else "ATA"
            
        if position not in POSITIONS:
            return False, f"Posição inválida. Use: {', '.join(POSITIONS)}."
            
        self.lineup[slot] = {"instance_id": instance_id, "hero_id": row["hero_id"], "position": position}
        return True, "Substituição realizada."

    @discord.ui.button(label="Substituir", style=discord.ButtonStyle.secondary, row=2)
    async def substitute_button(self, interaction, button):
        await interaction.response.send_modal(SubstitutionModal(self))

    @discord.ui.button(label="Segundo tempo", style=discord.ButtonStyle.success, row=2)
    async def second_half_button(self, interaction, button):
        if self.finished:
            return await interaction.response.send_message("Essa partida já terminou.", ephemeral=True)
        self.finished = True
        for child in self.children:
            child.disabled = True
        embed = self.cog.finish_match(self.ctx.author, self.state, self.lineup, self.formation)
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Sair (Abandonar)", style=discord.ButtonStyle.danger, row=2)
    async def cancel_button(self, interaction, button):
        self.finished = True
        await interaction.response.edit_message(content="Você abandonou a partida no intervalo (W.O). TutoriUAU anotou a derrota automática.", embed=None, view=None)
        
        # Penaliza como derrota no banco de dados
        conn = self.cog._connect()
        cursor = conn.cursor()
        self.cog._advance_progress(
            self.ctx.author.id, self.state["stage"], self.state, "D", 0, 3, 0, []
        )
        conn.close()
        self.stop()


# ==========================================
# LÓGICA DO JOGO E COG
# ==========================================
class Copa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = self._connect()
        cursor = conn.cursor()
        ensure_extra_tables(cursor)
        conn.commit()
        conn.close()

    def _connect(self):
        conn = sqlite3.connect("players.db")
        conn.row_factory = sqlite3.Row
        return conn

    def _resolve_hero_id(self, hero_id):
        raw = str(hero_id or "").strip()
        if raw in WORLD_CUP_PLAYERS:
            return raw
        normalized = normalize_text(raw)
        for key, data in WORLD_CUP_PLAYERS.items():
            if normalize_text(data.get("nome")) == normalized or key == normalized:
                return key
        return None

    def _is_active(self, cursor):
        cursor.execute("SELECT value FROM world_cup_settings WHERE key = 'active'")
        row = cursor.fetchone()
        return bool(row and str(row[0]) == "1")

    def sports_pool(self):
        pool = []
        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome": continue
            if hero_id not in WORLD_CUP_PLAYERS: continue
            if hero.get("divino") or hero.get("secreto"): continue
            if hero.get("origem") in SPORTS_ORIGINS:
                pool.append(hero_id)
        return pool

    def owned_copa_heroes(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id AS instance_id, hero_id, rarity, stars, level
            FROM heroes
            WHERE user_id = ?
            ORDER BY level DESC, rarity DESC, stars DESC, id ASC
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

    def get_formation_positions(self, formation):
        form_slots = FORMATIONS.get(formation, FORMATIONS["4-3-3"])
        positions = []
        for pos, amount in form_slots.items():
            positions.extend([pos] * amount)
        return positions

    def player_position_score(self, hero_id, position):
        data = WORLD_CUP_PLAYERS.get(hero_id, {})
        weights = ROLE_WEIGHTS.get(position, ROLE_WEIGHTS["ATA"])
        score = sum(float(data.get(stat, 50)) * weight for stat, weight in weights.items())
        preferred = {pos[0] for pos in data.get("posicoes", [])}
        if position not in preferred:
            score *= 0.85
        return score

    def validate_lineup(self, user_id, formation, captain_id, lineup):
        errors = []
        if formation not in FORMATIONS:
            errors.append("Formação tática inválida.")
        if len(lineup) != 11:
            errors.append("A escalação precisa ter exatamente 11 titulares.")
        if not any(item.get("position") == "GOL" for item in lineup.values()):
            errors.append("Seu time precisa de pelo menos 1 Goleiro (GOL) em campo.")
        if not captain_id:
            errors.append("Defina um capitão para liderar o grupo.")
        elif not any(str(item.get("instance_id")) == str(captain_id) for item in lineup.values()):
            errors.append("O capitão escolhido não está escalado entre os 11 titulares.")

        owned = {int(row["instance_id"]): row["hero_id"] for row in self.owned_copa_heroes(user_id)}
        hero_ids = []
        positions = Counter()
        for slot, item in lineup.items():
            instance_id = item.get("instance_id")
            if instance_id not in owned:
                errors.append(f"O herói no Slot {slot} não pertence à sua conta.")
                continue
            hero_ids.append(item.get("hero_id"))
            positions[item.get("position")] += 1

        duplicates = [hero_id for hero_id, count in Counter(hero_ids).items() if count > 1]
        if duplicates:
            errors.append("Não é permitido escalar o mesmo personagem de forma repetida.")

        if formation in FORMATIONS:
            for position, required in FORMATIONS[formation].items():
                if positions[position] != required:
                    errors.append(f"A formação {formation} exige exatamente {required}x {position} (Atualmente: {positions[position]}).")
        return (not errors), errors

    def save_team(self, user_id, team_name, formation, captain_id, lineup):
        conn = self._connect()
        cursor = conn.cursor()
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
                description="Você ainda não criou seu time. Use `echo copa iniciar`.",
                color=discord.Color.orange(),
            )
        ok, errors = self.validate_lineup(user.id, team["formation"], team["captain_id"], lineup)
        embed = discord.Embed(
            title=f"Echo Cup - {team['team_name']}",
            description=(
                f"Formação: **{team['formation']}**\n"
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
            captain = " 👑" if str(item["instance_id"]) == str(team["captain_id"]) else ""
            lines.append(f"`{slot:02}` **{data.get('nome', item['hero_id'])}**{captain} - `{item['position']}`")
        embed.add_field(name="Escalação", value="\n".join(lines), inline=False)
        if not ok:
            embed.add_field(name="Pendências", value="\n".join(errors), inline=False)
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
                position_score *= 1.10
            scores.append(position_score)
            affinity_counter.update(data.get("afinidades", []))
            
        stat_component = sum(scores) / max(1, len(scores))
        affinity_component = 0
        for count in affinity_counter.values():
            if count >= 5: affinity_component += 10
            elif count >= 4: affinity_component += 6
            elif count >= 3: affinity_component += 3
            
        formation_bonus = {"4-3-3": 3, "4-4-2": 2, "4-2-3-1": 4, "3-5-2": 3, "5-3-2": 2}.get(formation, 0)
        rng_component = rng.uniform(0, 100)
        return stat_component * 0.65 + rng_component * 0.20 + affinity_component * 0.10 + formation_bonus

    def _opponent_lineup(self, opponent):
        lineup = {}
        all_ids = list(opponent.get("titulares", []))
        pool = [self._resolve_hero_id(hero_id) for hero_id in all_ids]
        pool = [hero_id for hero_id in pool if hero_id in WORLD_CUP_PLAYERS]
        if len(pool) < 11:
            for hero_id in self.sports_pool():
                if hero_id not in pool:
                    pool.append(hero_id)
                if len(pool) >= 11: break
        
        formation = opponent.get("formacao")
        if formation not in FORMATIONS:
            formation = random.choice(list(FORMATIONS))
            
        positions = self.get_formation_positions(formation)
        for index, hero_id in enumerate(pool[:11], start=1):
            position = positions[index - 1] if index <= len(positions) else "ATA"
            lineup[index] = {"instance_id": 990000 + index, "hero_id": hero_id, "position": position}
        return lineup, formation

    def _current_stage(self, progress):
        if not progress or progress["stage"] not in STAGE_ORDER:
            return "grupos"
        return progress["stage"]

    def _stage_opponent(self, user_id, progress, stage):
        opponents = list(WORLD_CUP_OPPONENTS.values())
        run_id = int(progress["current_run"] if progress else 1)
        rng = random.Random(f"copa:{user_id}:{run_id}:opponents")
        rng.shuffle(opponents)
        
        if stage == "grupos":
            match_num = int(progress["group_match_num"] if progress else 0)
            return opponents[match_num % len(opponents)]
            
        stage_index = STAGE_ORDER.index(stage)
        return opponents[(5 + stage_index + run_id) % len(opponents)]

    def _simulate_half(self, user, opponent, user_lineup, opponent_lineup, formation, opponent_formation, score_user, score_opp, minute_start, minute_end, seed):
        rng = random.Random(seed)
        user_power = self._team_power(user_lineup, formation, user.get("captain_id"), rng=rng)
        opp_power = self._team_power(opponent_lineup, opponent_formation, rng=rng)
        
        user_share = max(0.20, min(0.80, user_power / max(1, user_power + opp_power)))
        events = sorted(rng.sample(range(minute_start, minute_end + 1), k=rng.randint(4, 6)))
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
            
            tag_actor = f"🟢 **[SEU TIME] {actor_name}**" if side_user else f"🔴 **[ADVERSÁRIO] {actor_name}**"
            tag_defender = f"🟢 **[SEU TIME] {defender_name}**" if not side_user else f"🔴 **[ADVERSÁRIO] {defender_name}**"
            
            team_name = user["team_name"] if side_user else opponent["nome"]
            opp_team_name = opponent["nome"] if side_user else user["team_name"]
            
            # Ajuste de Probabilidades (Maior chance de gol se a diferença de poder for grande)
            goal_chance = 0.35 + (user_share - 0.5) * (0.30 if side_user else -0.30)
            
            event_roll = rng.random()
            if event_roll < goal_chance:
                is_penalty = rng.random() < 0.15
                event_type = "penalti_gol" if is_penalty else "gol"
            else:
                other_events = ["defesa", "amarelo", "vermelho", "lesao", "penalti_defendido", "falta_perigosa", "virada_heroica", "falha_bizarra", "substituicao"]
                weights = [0.35, 0.15, 0.02, 0.08, 0.08, 0.15, 0.05, 0.07, 0.05]
                event_type = rng.choices(other_events, weights=weights)[0]

            if event_type in ["gol", "penalti_gol"]:
                if side_user: score_user += 1
                else: score_opp += 1
                scorers.append(actor["hero_id"])
                
            template = rng.choice(EVENT_TEMPLATES[event_type])
            log.append(f"`{minute:02d}'` " + template.format(time=team_name.upper(), player=tag_actor, defender=tag_defender, attacker=tag_actor))

        return score_user, score_opp, log, scorers

    def _simular_partida_cpu(self, opp_a_key, opp_b_key, seed):
        rng = random.Random(seed)
        opp_a = WORLD_CUP_OPPONENTS[opp_a_key]
        opp_b = WORLD_CUP_OPPONENTS[opp_b_key]
        
        lineup_a, form_a = self._opponent_lineup(opp_a)
        lineup_b, form_b = self._opponent_lineup(opp_b)
        
        power_a = self._team_power(lineup_a, form_a, rng=rng)
        power_b = self._team_power(lineup_b, form_b, rng=rng)
        
        share_a = power_a / (power_a + power_b)
        goals_a = rng.choices([0, 1, 2, 3, 4], weights=[0.25, 0.40, 0.25, 0.08, 0.02])[0]
        goals_b = rng.choices([0, 1, 2, 3, 4], weights=[0.25, 0.40, 0.25, 0.08, 0.02])[0]
        
        if share_a > 0.55 and goals_a < goals_b:
            if rng.random() < 0.65: goals_a, goals_b = goals_b, goals_a
        elif share_a < 0.45 and goals_b < goals_a:
            if rng.random() < 0.65: goals_a, goals_b = goals_b, goals_a
            
        return goals_a, goals_b

    def _prepare_match(self, user):
        team, lineup, progress = self.load_team(user.id)
        ok, errors = self.validate_lineup(user.id, team["formation"] if team else None, team["captain_id"] if team else None, lineup)
        if not team:
            return None, "Crie seu time com `echo copa iniciar` primeiro."
        if not ok:
            return None, "Seu time de Copa não está pronto:\n" + "\n".join(f"• {e}" for e in errors)
        
        conn = self._connect()
        cursor = conn.cursor()
        active = self._is_active(cursor)
        conn.close()
        
        if not active:
            return None, "🏆 **A Echo Cup está fechada.** Aguarde os administradores abrirem o estádio."
            
        cooldown_end = progress["cooldown_end"] if progress else 0
        if cooldown_end and now_ts() < cooldown_end:
            wait = cooldown_end - now_ts()
            hours = wait // 3600
            minutes = (wait % 3600) // 60
            return None, f"⏳ **Sua campanha acabou!** Os jogadores estão no DM. Nova Copa disponível em **{hours}h {minutes}min**."

        stage = self._current_stage(progress)
        match_num = int(progress["group_match_num"] if progress else 0)
        opponents = list(WORLD_CUP_OPPONENTS.keys())
        
        if stage == "grupos" and match_num == 0:
            conn = self._connect()
            cursor = conn.cursor()
            rng = random.Random(f"copa:{user.id}:{now_ts()}:group")
            selected_opps = rng.sample(opponents, 3)
            cursor.execute("""
                UPDATE world_cup_progress 
                SET group_match_num = 0, p_points = 0, p_gf = 0, p_ga = 0,
                    opp1_id = ?, opp1_points = 0, opp1_gf = 0, opp1_ga = 0,
                    opp2_id = ?, opp2_points = 0, opp2_gf = 0, opp2_ga = 0,
                    opp3_id = ?, opp3_points = 0, opp3_gf = 0, opp3_ga = 0
                WHERE user_id = ?
            """, (selected_opps[0], selected_opps[1], selected_opps[2], str(user.id)))
            conn.commit()
            conn.close()
            _, _, progress = self.load_team(user.id)

        opponent_key = progress[f"opp{match_num + 1}_id"] if stage == "grupos" else None
        opponent = WORLD_CUP_OPPONENTS.get(opponent_key) if opponent_key else self._stage_opponent(user.id, progress, stage)
        
        opponent_lineup, opponent_formation = self._opponent_lineup(opponent)
        user_team = {"team_name": team["team_name"], "captain_id": team["captain_id"]}
        
        half_user, half_opp, first_log, scorers = self._simulate_half(
            user_team, opponent, lineup, opponent_lineup, team["formation"], opponent_formation,
            0, 0, 1, 45, f"{user.id}:{now_ts()}:first"
        )
        
        state = {
            "team_name": team["team_name"], "formation": team["formation"], "captain_id": team["captain_id"],
            "lineup": lineup, "progress": dict(progress) if progress else None,
            "stage": stage, "stage_label": STAGE_LABELS[stage], "opponent": opponent,
            "opponent_key": opponent_key or "knockout", "opponent_lineup": opponent_lineup,
            "opponent_formation": opponent_formation, "half_user": half_user, "half_opp": half_opp,
            "first_log": first_log, "first_scorers": scorers,
        }
        return state, None

    def finish_match(self, user, state, lineup, formation):
        user_team = {"team_name": state["team_name"], "captain_id": state.get("captain_id")}
        final_user, final_opp, second_log, scorers = self._simulate_half(
            user_team, state["opponent"], lineup, state["opponent_lineup"], formation, state["opponent_formation"],
            state["half_user"], state["half_opp"], 46, 90, f"{user.id}:{now_ts()}:second:{formation}"
        )
        
        penalties = None
        penalty_result = None
        stage = state["stage"]
        
        if stage != "grupos" and final_user == final_opp:
            rng = random.Random(f"{user.id}:{now_ts()}:penaltis")
            user_pen = rng.choices([3, 4, 5, 2], weights=[0.40, 0.40, 0.15, 0.05])[0]
            opp_pen = rng.choices([3, 4, 5, 2], weights=[0.40, 0.40, 0.15, 0.05])[0]
            if user_pen == opp_pen:
                user_pen += 1 if rng.random() < 0.52 else 0
                opp_pen += 1 if user_pen == opp_pen else 0
            penalties = (user_pen, opp_pen)
            penalty_result = "V" if user_pen > opp_pen else "D"

        if penalty_result: result = penalty_result
        elif final_user > final_opp: result = "V"
        elif final_user == final_opp: result = "E"
        else: result = "D"

        reward = MATCH_REWARDS[result] + final_user * 10
        stage_note, stage_reward, stand_table = self._advance_progress(
            user.id, stage, state, result, final_user, final_opp, reward, scorers + state["first_scorers"]
        )
        
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE world_cup_teams SET last_match = ? WHERE user_id = ?", (now_ts(), str(user.id)))
        conn.commit()
        conn.close()

        title = f"Echo Cup - {STAGE_LABELS[stage]}"
        score_line = f"⚽ **{state['team_name']}** {final_user} x {final_opp} **{state['opponent']['nome']}**"
        if penalties: score_line += f"\n🎯 **Disputa de Pênaltis:** {penalties[0]} x {penalties[1]}"
            
        embed = discord.Embed(
            title=title,
            description=score_line + "\n\n" + "\n".join(state["first_log"] + second_log),
            color=discord.Color.green() if result == "V" else discord.Color.red() if result == "D" else discord.Color.gold(),
        )
        embed.add_field(name="Recompensa da partida", value=f"🪙 **+{reward:,} echobet**", inline=True)
        if stage_reward: embed.add_field(name="Bônus de fase", value=f"🪙 **+{stage_reward:,} echobet**", inline=True)
        embed.add_field(name="Situação da Campanha", value=stage_note, inline=False)
        if stand_table: embed.add_field(name="📋 Tabela do Grupo", value=f"```{stand_table}```", inline=False)
        embed.set_footer(text="TutoriUAU: A tática supera o script de vez em quando.")
        return embed

    def _advance_progress(self, user_id, stage, state, result, goals_for, goals_against, match_reward, scorers):
        conn = self._connect()
        cursor = conn.cursor()
        
        progress = state.get("progress") or {}
        run_id = int(progress.get("current_run") or 1)
        match_num = int(progress.get("group_match_num") or 0)
        
        wins = 1 if result == "V" else 0
        draws = 1 if result == "E" else 0
        losses = 1 if result == "D" else 0
        unbeaten = int(progress.get("unbeaten_streak") or 0)
        unbeaten = unbeaten + 1 if result in {"V", "E"} else 0
        best_unbeaten = max(int(progress.get("best_unbeaten_streak") or 0), unbeaten)

        cursor.execute(
            """
            INSERT INTO world_cup_matches(user_id, opponent_name, stage, user_score, opponent_score, result, created_at, run_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(user_id), state["opponent"]["nome"], stage, goals_for, goals_against, result, now_ts(), run_id),
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
        note = "Campanha ativa."
        stand_table = ""

        if stage == "grupos":
            p_pts = 3 if result == "V" else 1 if result == "E" else 0
            p_gf = goals_for
            p_ga = goals_against
            opp1_p, opp1_gf, opp1_ga = 0, 0, 0
            opp2_p, opp2_gf, opp2_ga = 0, 0, 0
            opp3_p, opp3_gf, opp3_ga = 0, 0, 0
            
            cpu_seed = f"copa:{user_id}:{run_id}:cpu:{match_num}"
            if match_num == 0:
                o2_g, o3_g = self._simular_partida_cpu(progress["opp2_id"], progress["opp3_id"], cpu_seed)
                opp2_p = 3 if o2_g > o3_g else 1 if o2_g == o3_g else 0
                opp3_p = 3 if o3_g > o2_g else 1 if o2_g == o3_g else 0
                opp2_gf, opp2_ga = o2_g, o3_g
                opp3_gf, opp3_ga = o3_g, o2_g
                opp1_p, opp1_gf, opp1_ga = 0, goals_against, goals_for
            elif match_num == 1:
                o1_g, o3_g = self._simular_partida_cpu(progress["opp1_id"], progress["opp3_id"], cpu_seed)
                opp1_p = 3 if o1_g > o3_g else 1 if o1_g == o3_g else 0
                opp3_p = 3 if o3_g > o1_g else 1 if o1_g == o3_g else 0
                opp1_gf, opp1_ga = o1_g, o3_g
                opp3_gf, opp3_ga = o3_g, o1_g
                opp2_p, opp2_gf, opp2_ga = 0, goals_against, goals_for
            elif match_num == 2:
                o1_g, o2_g = self._simular_partida_cpu(progress["opp1_id"], progress["opp2_id"], cpu_seed)
                opp1_p = 3 if o1_g > o2_g else 1 if o1_g == o2_g else 0
                opp2_p = 3 if o2_g > o1_g else 1 if o1_g == o2_g else 0
                opp1_gf, opp1_ga = o1_g, o2_g
                opp2_gf, opp2_ga = o2_g, o1_g
                opp3_p, opp3_gf, opp3_ga = 0, goals_against, goals_for

            cursor.execute("""
                UPDATE world_cup_progress
                SET p_points = p_points + ?, p_gf = p_gf + ?, p_ga = p_ga + ?,
                    opp1_points = opp1_points + ?, opp1_gf = opp1_gf + ?, opp1_ga = opp1_ga + ?,
                    opp2_points = opp2_points + ?, opp2_gf = opp2_gf + ?, opp2_ga = opp2_ga + ?,
                    opp3_points = opp3_points + ?, opp3_gf = opp3_gf + ?, opp3_ga = opp3_ga + ?,
                    group_match_num = group_match_num + 1
                WHERE user_id = ?
            """, (p_pts, p_gf, p_ga, opp1_p, opp1_gf, opp1_ga, opp2_p, opp2_gf, opp2_ga, opp3_p, opp3_gf, opp3_ga, str(user_id)))
            
            cursor.execute("SELECT * FROM world_cup_progress WHERE user_id = ?", (str(user_id),))
            progress = cursor.fetchone()
            match_num = progress["group_match_num"]

            group_data = [
                {"nome": state["team_name"], "pontos": progress["p_points"], "gf": progress["p_gf"], "ga": progress["p_ga"]},
                {"nome": WORLD_CUP_OPPONENTS[progress["opp1_id"]]["nome"], "pontos": progress["opp1_points"], "gf": progress["opp1_gf"], "ga": progress["opp1_ga"]},
                {"nome": WORLD_CUP_OPPONENTS[progress["opp2_id"]]["nome"], "pontos": progress["opp2_points"], "gf": progress["opp2_gf"], "ga": progress["opp2_ga"]},
                {"nome": WORLD_CUP_OPPONENTS[progress["opp3_id"]]["nome"], "pontos": progress["opp3_points"], "gf": progress["opp3_gf"], "ga": progress["opp3_ga"]}
            ]
            group_data.sort(key=lambda t: (t["pontos"], t["gf"] - t["ga"], t["gf"]), reverse=True)
            
            stand_table = "Pos | Time                   | Pts | SG | GP\n"
            for pos, t in enumerate(group_data, 1):
                stand_table += f"{pos:02d}º | {t['nome'][:22]:<22} | {t['pontos']:>3} | {t['gf']-t['ga']:>2} | {t['gf']:>2}\n"

            if match_num >= 3:
                top_2 = [t["nome"] for t in group_data[:2]]
                if state["team_name"] in top_2:
                    next_stage = "oitavas"
                    stage_reward = STAGE_REWARDS["grupos"]
                    note = "🎉 **QUALIFICADO!** Seu time ficou no G2 e avançou de fase. Continue jogando livremente!"
                else:
                    next_stage = "grupos"
                    cursor.execute("UPDATE world_cup_progress SET cooldown_end = ? WHERE user_id = ?", (now_ts() + MATCH_COOLDOWN, str(user_id)))
                    note = f"❌ **ELIMINADO!** Seu time ficou em {group_data.index(next(x for x in group_data if x['nome'] == state['team_name'])) + 1}º colocado no grupo. Campanha encerrada. Cooldown ativado."
                
                cursor.execute("""
                    UPDATE world_cup_progress
                    SET group_match_num = 0, p_points = 0, p_gf = 0, p_ga = 0,
                        opp1_points = 0, opp1_gf = 0, opp1_ga = 0,
                        opp2_points = 0, opp2_gf = 0, opp2_ga = 0,
                        opp3_points = 0, opp3_gf = 0, opp3_ga = 0
                    WHERE user_id = ?
                """, (str(user_id),))
            else:
                note = f"Fase de grupos em andamento. Partida **{match_num}/3** jogada. Próxima rodada liberada imediatamente!"

        else:
            if result == "V":
                index = STAGE_ORDER.index(stage)
                if stage == "final":
                    next_stage = "grupos"
                    stage_reward = STAGE_REWARDS["campeao"]
                    medals = 1
                    self._grant_champion_title(cursor, user_id)
                    cursor.execute("UPDATE world_cup_progress SET cooldown_end = ? WHERE user_id = ?", (now_ts() + MATCH_COOLDOWN, str(user_id)))
                    note = "🏆 **CAMPEÃO DO MUNDO!** O troféu dourado é de Lugnica! Campanha vitoriosa encerrada. Cooldown ativado."
                else:
                    next_stage = STAGE_ORDER[index + 1]
                    stage_reward = STAGE_REWARDS.get(next_stage, 0)
                    note = f"🔥 **CLASSIFICADO!** Seu time avançou para as **{STAGE_LABELS[next_stage]}**. Jogue a próxima partida!"
            else:
                next_stage = "grupos"
                cursor.execute("UPDATE world_cup_progress SET cooldown_end = ? WHERE user_id = ?", (now_ts() + MATCH_COOLDOWN, str(user_id)))
                note = "❌ **ELIMINADO!** Seu time caiu no mata-mata. Fim de campanha. Cooldown ativado."

        best_stage = self._best_stage(progress.get("best_stage"), next_stage)
        cursor.execute(
            """
            UPDATE world_cup_progress
            SET stage = ?, points = points + ?, wins = wins + ?, draws = draws + ?, losses = losses + ?,
                goals_for = goals_for + ?, goals_against = goals_against + ?,
                best_stage = ?, medals = medals + ?, unbeaten_streak = ?, best_unbeaten_streak = ?
            WHERE user_id = ?
            """,
            (next_stage, match_reward + stage_reward, wins, draws, losses, goals_for, goals_against,
             best_stage, medals, unbeaten, best_unbeaten, str(user_id)),
        )
        if next_stage == "grupos" and stage != "final" and result == "D":
            cursor.execute("UPDATE world_cup_progress SET current_run = current_run + 1 WHERE user_id = ?", (str(user_id),))
            
        conn.commit()
        conn.close()
        return note, stage_reward, stand_table

    def _best_stage(self, current, candidate):
        order = ["Fase de grupos", "Oitavas", "Quartas", "Semifinal", "Final", "Campeao"]
        label = STAGE_LABELS.get(candidate, current or "Fase de grupos")
        if label == "Eliminado": label = current or "Fase de grupos"
        try: return label if order.index(label) > order.index(current or "Fase de grupos") else current
        except ValueError: return label

    def _grant_champion_title(self, cursor, user_id):
        item = "token_titulo_campeao_de_lugnica"
        cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (str(user_id), item))
        if cursor.fetchone():
            cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE user_id = ? AND item_name = ?", (str(user_id), item))
        else:
            cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (str(user_id), item))
        cursor.execute(
            "INSERT OR IGNORE INTO player_cosmetics(user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, 'title', 0, ?)",
            (str(user_id), item, now_ts()),
        )

    @commands.group(name="copa", aliases=["echocup", "worldcup"], invoke_without_command=True)
    async def copa_group(self, ctx):
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
                "Monte 11 herois, escolha a formação e dispute grupos, mata-mata e a glória mundial.\n"
                "TutoriUAU: é futebol, mas com anime. Portanto a física pediu demissão."
            ),
            color=discord.Color.green() if active else discord.Color.dark_gray(),
        )
        embed.add_field(
            name="Fluxo",
            value=(
                "`echo copa iniciar` cria e edita sua prancheta tática.\n"
                "`echo copa jogar` inicia a próxima partida da sua campanha.\n"
                "`echo copa loja` gaste seus ganhos (echobets).\n"
                "`echo copa ranking`, `historico`, `hall`, `banner`, `summon` completam o evento."
            ),
            inline=False,
        )
        if started and str(started[0] or "0") != "0":
            embed.set_footer(text=f"TutoriUAU: evento iniciado em <t:{started[0]}:f>.")
        else:
            embed.set_footer(text="TutoriUAU: esperando o apito administrativo.")
        await ctx.send(embed=embed)

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
        conn.close()
        
        # Import local to access SHOP_ITEMS if not global, wait, we have to define SHOP_ITEMS globally
        from data.world_cup_players import WORLD_CUP_PLAYERS # Import for safety if needed
        # We need SHOP_ITEMS defined in the file
        SHOP_ITEMS = {
            1: {"name": "Tema: Arquibancada Lotada", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_arquibancada_lotada"},
            2: {"name": "Tema: Gramado Noturno", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_gramado_noturno"},
            3: {"name": "Tema: Sala de Imprensa", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_sala_de_imprensa"},
            4: {"name": "Tema: Taca Mundial", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_taca_mundial"},
            5: {"name": "Titulo: Campeao de Lugnica", "cost": 160, "kind": "cosmetic", "type": "title", "item": "token_titulo_campeao_de_lugnica"},
            6: {"name": "Titulo: Lenda da Echo Cup", "cost": 220, "kind": "cosmetic", "type": "title", "item": "token_titulo_lenda_echo_cup"},
            7: {"name": "Titulo: Rei dos Ecos", "cost": 260, "kind": "cosmetic", "type": "title", "item": "token_titulo_rei_dos_ecos"},
            8: {"name": "Titulo: Maior Tecnico de Lugnica", "cost": 260, "kind": "cosmetic", "type": "title", "item": "token_titulo_maior_tecnico_de_lugnica"},
            9: {"name": "3 Tickets de Invocacao", "cost": 120, "kind": "tickets", "amount": 3},
            10: {"name": "25 Gems", "cost": 220, "kind": "gems", "amount": 25},
            11: {"name": "Maple, Pet Alce", "cost": 1000, "kind": "pet", "pet_id": "maple_alce", "pet_name": "Maple", "rarity": 5},
            12: {"name": "Zayu, Pet Onca-Pintada", "cost": 1000, "kind": "pet", "pet_id": "zayu_onca", "pet_name": "Zayu", "rarity": 5},
            13: {"name": "Clutch, Pet Aguia", "cost": 1000, "kind": "pet", "pet_id": "clutch_aguia", "pet_name": "Clutch", "rarity": 5},
        }
        
        embed = discord.Embed(
            title="Loja da Echo Cup",
            description=f"Saldo: **{points:,} echobet**\nTutoriUAU: aposte com responsabilidade.",
            color=discord.Color.gold(),
        )
        lines = [f"`{item_id}` **{item['name']}** - {item['cost']:,} echobet" for item_id, item in SHOP_ITEMS.items()]
        embed.add_field(name="Itens", value="\n".join(lines)[:1024], inline=False)
        embed.set_footer(text="Use `echo copa resgatar <id>`.")
        await ctx.send(embed=embed)

    @copa_group.command(name="resgatar", aliases=["comprar", "buy"])
    async def copa_resgatar(self, ctx, item_id: int = None):
        # We need SHOP_ITEMS defined here too
        SHOP_ITEMS = {
            1: {"name": "Tema: Arquibancada Lotada", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_arquibancada_lotada"},
            2: {"name": "Tema: Gramado Noturno", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_gramado_noturno"},
            3: {"name": "Tema: Sala de Imprensa", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_sala_de_imprensa"},
            4: {"name": "Tema: Taca Mundial", "cost": 500, "kind": "cosmetic", "type": "frame", "item": "token_moldura_taca_mundial"},
            5: {"name": "Titulo: Campeao de Lugnica", "cost": 160, "kind": "cosmetic", "type": "title", "item": "token_titulo_campeao_de_lugnica"},
            6: {"name": "Titulo: Lenda da Echo Cup", "cost": 220, "kind": "cosmetic", "type": "title", "item": "token_titulo_lenda_echo_cup"},
            7: {"name": "Titulo: Rei dos Ecos", "cost": 260, "kind": "cosmetic", "type": "title", "item": "token_titulo_rei_dos_ecos"},
            8: {"name": "Titulo: Maior Tecnico de Lugnica", "cost": 260, "kind": "cosmetic", "type": "title", "item": "token_titulo_maior_tecnico_de_lugnica"},
            9: {"name": "3 Tickets de Invocacao", "cost": 120, "kind": "tickets", "amount": 3},
            10: {"name": "25 Gems", "cost": 220, "kind": "gems", "amount": 25},
            11: {"name": "Maple, Pet Alce", "cost": 1000, "kind": "pet", "pet_id": "maple_alce", "pet_name": "Maple", "rarity": 5},
            12: {"name": "Zayu, Pet Onca-Pintada", "cost": 1000, "kind": "pet", "pet_id": "zayu_onca", "pet_name": "Zayu", "rarity": 5},
            13: {"name": "Clutch, Pet Aguia", "cost": 1000, "kind": "pet", "pet_id": "clutch_aguia", "pet_name": "Clutch", "rarity": 5},
        }
        
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
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item["item"]))
            if cursor.fetchone():
                cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE user_id = ? AND item_name = ?", (user_id, item["item"]))
            else:
                cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (user_id, item["item"]))
            cursor.execute(
                "INSERT OR IGNORE INTO player_cosmetics(user_id, cosmetic_id, type, active, purchased_at) VALUES (?, ?, ?, 0, ?)",
                (user_id, item["item"], item["type"], now_ts()),
            )
        elif item["kind"] == "tickets":
            cursor.execute("INSERT OR IGNORE INTO summon_data (user_id, summon_tickets) VALUES (?, 0)", (user_id,))
            cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (item["amount"], user_id))
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
        await ctx.send(f"Compra concluída: **{item['name']}**. TutoriUAU carimbou o recibo.")

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
        embed = discord.Embed(title="Últimas partidas da Echo Cup", color=discord.Color.blurple())
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
                "Aqui só entram personagens de anime de esporte. TutoriUAU aprova o atletismo."
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
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        if not player:
            conn.close()
            return await ctx.send("Use `echo iniciar` primeiro.")
        cost = COPA_SUMMON_COST * amount
        if int(player[0] or 0) < cost:
            conn.close()
            return await ctx.send(f"Ouro insuficiente. Custo: **{cost:,} Gold**.")
            
        cursor.execute(
            """
            INSERT OR IGNORE INTO summon_data(user_id, summon_tickets, shop_level, pity_4, pity_5, total_summons, total_1_star, total_2_star, total_3_star, total_4_star, total_5_star)
            VALUES (?, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
            """,
            (user_id,),
        )
        cursor.execute("SELECT pity_4, pity_5 FROM summon_data WHERE user_id = ?", (user_id,))
        pity = cursor.fetchone()
        pity_4, pity_5 = int(pity[0] or 0), int(pity[1] or 0)
        
        cursor.execute("SELECT DISTINCT hero_id FROM heroes WHERE user_id = ?", (user_id,))
        owned = {self._resolve_hero_id(row[0]) or row[0] for row in cursor.fetchall()}
        
        results = []
        stats = Counter()
        
        # Local random logic
        def roll_copa_rarity(pity_4, pity_5):
            if pity_5 >= HARD_PITY_5: return 5
            if pity_4 >= HARD_PITY_4: return 4
            chance_5 = BASE_RATES[5] + max(0, pity_5 - SOFT_PITY_5 + 1) * 0.05
            chance_4 = BASE_RATES[4] + max(0, pity_4 - SOFT_PITY_4 + 1) * 0.5
            roll = random.uniform(0, 100)
            if roll < chance_5: return 5
            if roll < chance_5 + chance_4: return 4
            lower = random.uniform(0, BASE_RATES[1] + BASE_RATES[2] + BASE_RATES[3])
            if lower < BASE_RATES[1]: return 1
            if lower < BASE_RATES[1] + BASE_RATES[2]: return 2
            return 3
            
        def rarity_pool(r):
            return [hid for hid in pool if int(HEROES.get(hid, {}).get("raridade", 1)) == r]

        for index in range(amount):
            pity_4 += 1
            pity_5 += 1
            rarity = roll_copa_rarity(pity_4, pity_5)
            if amount == 10 and index == 9 and not any(item["rarity"] >= 3 for item in results):
                rarity = 3
                
            r_pool = rarity_pool(rarity)
            if not r_pool:
                r_pool = rarity_pool(3) or pool
            hero_id = random.choice(r_pool)
            real_rarity = int(HEROES.get(hero_id, {}).get("raridade", 3))
            
            if real_rarity >= 5:
                pity_5 = 0; pity_4 = 0
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
        path, filename = get_hero_attachment(rarest["hero_id"], "copa_summon")
        hero_file = discord.File(path, filename=filename) if path else None
        
        embed = discord.Embed(
            title="Summon da Echo Cup",
            description=f"{ctx.author.mention} gastou **{cost:,} Gold** no banner esportivo.\n\n",
            color=discord.Color.green(),
        )
        for item in results:
            hero = HEROES.get(item["hero_id"], {})
            line = f"{'⭐' * max(1, item['rarity'])} | {hero.get('emoji', '')} **{hero.get('nome', item['hero_id'])}**"
            if item["new"]: line += " [NEW]"
            embed.description += line + "\n"
            
        embed.set_footer(text=f"Pity 4⭐ {pity_4}/{HARD_PITY_4} | Pity 5⭐ {pity_5}/{HARD_PITY_5}")
        if hero_file:
            embed.set_image(url=f"attachment://{hero_file.filename}")
            await ctx.send(embed=embed, file=hero_file)
        else:
            await ctx.send(embed=embed)

    @copa_group.command(name="heroi", aliases=["hero"])
    async def copa_heroi(self, ctx, *, query: str = None):
        if not query: return await ctx.send("Use `echo copa heroi <nome ou id>`.")
        hero_id = self._resolve_hero_id(query)
        if not hero_id: return await ctx.send("Nao encontrei esse heroi na ficha da Copa.")
        
        data = WORLD_CUP_PLAYERS[hero_id]
        hero = HEROES.get(hero_id, {})
        embed = discord.Embed(
            title=f"{data.get('nome', hero.get('nome', hero_id))} - Ficha da Copa",
            description=f"{'⭐' * max(1, hero.get('raridade', 1))} | {hero.get('origem', 'Origem desconhecida')}",
            color=discord.Color.green(),
        )
        positions = ", ".join(f"{pos[0]} ({pos[1]})" for pos in data.get("posicoes", []))
        embed.add_field(name="Posicoes", value=positions or "Sem posicao", inline=False)
        stats = ["ataque", "defesa", "passe", "velocidade", "finalizacao", "goleiro", "mental"]
        embed.add_field(name="Atributos", value="\n".join(f"**{stat.title()}**: {data.get(stat, 0)}" for stat in stats), inline=True)
        skill = data.get("habilidade", {})
        embed.add_field(name=skill.get("nome", "Habilidade"), value=skill.get("efeito", "Sem descricao."), inline=False)
        
        path, filename = get_hero_attachment(hero_id, "copa_heroi")
        hero_file = discord.File(path, filename=filename) if path else None
        
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
            "SELECT team_name, title, created_at FROM world_cup_hall WHERE title = 'Campeao do Mundo' ORDER BY created_at DESC LIMIT 5"
        )
        champions = cursor.fetchall()
        cursor.execute(
            "SELECT s.user_id, s.hero_id, s.goals, COALESCE(t.team_name, s.user_id) AS team_name FROM world_cup_player_stats s LEFT JOIN world_cup_teams t ON t.user_id = s.user_id ORDER BY s.goals DESC LIMIT 1"
        )
        scorer = cursor.fetchone()
        cursor.execute(
            "SELECT COALESCE(t.team_name, p.user_id) AS team_name, goals_for FROM world_cup_progress p LEFT JOIN world_cup_teams t ON t.user_id = p.user_id ORDER BY goals_for DESC LIMIT 1"
        )
        offensive = cursor.fetchone()
        cursor.execute(
            "SELECT COALESCE(t.team_name, p.user_id) AS team_name, best_unbeaten_streak FROM world_cup_progress p LEFT JOIN world_cup_teams t ON t.user_id = p.user_id ORDER BY best_unbeaten_streak DESC LIMIT 1"
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


async def setup(bot):
    await bot.add_cog(Copa(bot))