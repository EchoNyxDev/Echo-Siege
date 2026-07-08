import discord
from discord.ext import commands
import json
import sqlite3
import re
import os
import random
import sys
import time
import unicodedata

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
    from data.pets import PETS
    from data.calamidades import RAID_BOSSES
    from data.habilidades import SKILLS
    from data.habmonsters import MONSTER_SKILLS
    from utils.codes_storage import connect_codes_db, init_codes_db
    from utils.db import backup_databases, list_database_backups
    from utils.skills import get_hero_skill_ids
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.combat import choose_ai_combat_skill
    from commands.pvp import PvpBattleView, _cortar_texto
    SKILLS.update(MONSTER_SKILLS)
except ModuleNotFoundError:
    HEROES = {}
    EQUIPAMENTOS = {}
    PETS = {}
    RAID_BOSSES = {}
    SKILLS = {}
    MONSTER_SKILLS = {}
    PvpBattleView = None
    def _cortar_texto(texto, limite=1024):
        return str(texto)[:limite]
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []
    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {"hp": 100, "atk": 10, "matk": 10, "def": 5, "spd": 10, "crt": 5, "level": level}
    def normalize_class(value):
        return str(value or "neutro").lower()
    def choose_ai_combat_skill(actor, skills=None, allies=None, enemies=None, skill_chance=0.62):
        available = [skill_id for skill_id in actor.habilidades if skill_id in (skills or {}) and skill_id not in actor.cooldowns]
        return random.choice(available) if available and random.random() <= skill_chance else None
    def connect_codes_db():
        return sqlite3.connect("players.db")
    def init_codes_db():
        pass
    def backup_databases(*args, **kwargs):
        return []
    def list_database_backups(*args, **kwargs):
        return []

try:
    from data.banners import save_manual_banner
except ModuleNotFoundError:
    save_manual_banner = None

# Lista de IDs dos Administradores
ADM_USERS = [
    657990219689099264,
    768671545790693437
]

def normalize_hero_name(value):
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")

def ensure_admin_logs_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS administrative_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            value TEXT,
            admin_id TEXT,
            timestamp INTEGER DEFAULT 0,
            status TEXT DEFAULT 'open',
            resolution TEXT DEFAULT '',
            resolved_by TEXT,
            resolved_at INTEGER DEFAULT 0
        )
    """)
    cursor.execute("PRAGMA table_info(administrative_logs)")
    columns = {row[1] for row in cursor.fetchall()}
    for column, ddl in {
        "status": "TEXT DEFAULT 'open'",
        "resolution": "TEXT DEFAULT ''",
        "resolved_by": "TEXT",
        "resolved_at": "INTEGER DEFAULT 0",
    }.items():
        if column not in columns:
            cursor.execute(f"ALTER TABLE administrative_logs ADD COLUMN {column} {ddl}")

class BannerHeroSelect(discord.ui.Select):
    def __init__(self, builder, rarity, row):
        self.builder = builder
        self.rarity = rarity
        pool = builder.pools[rarity]
        page = builder.pages[rarity]
        start = page * builder.PAGE_SIZE
        page_ids = pool[start:start + builder.PAGE_SIZE]
        selected = set(builder.selected[rarity])
        options = []
        for hero_id in page_ids:
            hero = HEROES[hero_id]
            description = (
                f"{str(hero.get('classe', 'sem classe')).title()} • "
                f"{hero.get('origem', 'Origem desconhecida')}"
            )[:100]
            options.append(
                discord.SelectOption(
                    label=str(hero.get("nome", hero_id))[:100],
                    value=hero_id,
                    description=description,
                    default=hero_id in selected,
                )
            )

        total_pages = builder.page_count(rarity)
        placeholder = (
            f"{rarity}⭐ • página {page + 1}/{total_pages} • "
            f"{len(selected)}/{builder.LIMITS[rarity]} escolhidos"
        )
        super().__init__(
            placeholder=placeholder,
            min_values=0,
            max_values=min(builder.LIMITS[rarity], len(options)),
            options=options,
            row=row,
        )

    async def callback(self, interaction):
        await self.builder.apply_page_selection(
            interaction,
            self.rarity,
            list(self.values),
        )

class BannerHeroSearchModal(discord.ui.Modal, title="Buscar herói para o banner"):
    rarity = discord.ui.TextInput(
        label="Raridade",
        placeholder="Digite 4 ou 5",
        min_length=1,
        max_length=1,
    )
    hero_name = discord.ui.TextInput(
        label="Nome ou ID do herói",
        placeholder="Ex.: Levi ou levi_ackerman",
        min_length=2,
        max_length=100,
    )

    def __init__(self, builder):
        super().__init__()
        self.builder = builder

    async def on_submit(self, interaction):
        try:
            rarity = int(str(self.rarity.value).strip())
        except ValueError:
            rarity = 0
        if rarity not in self.builder.LIMITS:
            return await interaction.response.send_message(
                "A raridade precisa ser `4` ou `5`.",
                ephemeral=True,
            )

        query = normalize_hero_name(self.hero_name.value)
        pool = self.builder.pools[rarity]
        exact = [
            hero_id
            for hero_id in pool
            if query in {
                normalize_hero_name(hero_id),
                normalize_hero_name(HEROES[hero_id].get("nome")),
            }
        ]
        matches = exact or [
            hero_id
            for hero_id in pool
            if query in normalize_hero_name(hero_id)
            or query in normalize_hero_name(HEROES[hero_id].get("nome"))
        ]
        if not matches:
            return await interaction.response.send_message(
                f"Não encontrei um herói {rarity}⭐ com esse nome.",
                ephemeral=True,
            )
        if len(matches) > 1:
            names = ", ".join(HEROES[hero_id].get("nome", hero_id) for hero_id in matches[:10])
            return await interaction.response.send_message(
                f"Encontrei mais de um resultado: **{names}**. Pesquise pelo nome completo ou ID.",
                ephemeral=True,
            )

        hero_id = matches[0]
        added, message = self.builder.toggle_hero(rarity, hero_id)
        if added:
            self.builder.pages[rarity] = pool.index(hero_id) // self.builder.PAGE_SIZE
        self.builder.rebuild_selects()
        await interaction.response.send_message(message, ephemeral=True)
        if self.builder.message:
            await self.builder.message.edit(
                embed=self.builder.build_embed(),
                view=self.builder,
            )

class BannerBuilderView(discord.ui.View):
    PAGE_SIZE = 25
    LIMITS = {5: 3, 4: 5}

    def __init__(self, author_id):
        super().__init__(timeout=900)
        self.author_id = int(author_id)
        self.message = None
        self.pools = {
            rarity: sorted(
                (
                    hero_id
                    for hero_id, hero in HEROES.items()
                    if hero_id != "id-nome"
                    and int(hero.get("raridade", 0) or 0) == rarity
                    and not hero.get("divino")
                    and not hero.get("secreto")
                ),
                key=lambda hero_id: HEROES[hero_id].get("nome", hero_id).casefold(),
            )
            for rarity in self.LIMITS
        }
        self.selected = {5: [], 4: []}
        self.pages = {5: 0, 4: 0}
        self.rebuild_selects()

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Este painel pertence ao administrador que o abriu.",
                ephemeral=True,
            )
            return False
        return True

    def page_count(self, rarity):
        return max(1, (len(self.pools[rarity]) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)

    def current_page_ids(self, rarity):
        start = self.pages[rarity] * self.PAGE_SIZE
        return self.pools[rarity][start:start + self.PAGE_SIZE]

    def _featured_text(self, rarity):
        chosen = self.selected[rarity]
        lines = []
        for index in range(self.LIMITS[rarity]):
            if index < len(chosen):
                hero_id = chosen[index]
                hero = HEROES[hero_id]
                lines.append(
                    f"`{index + 1}.` {hero.get('emoji', '')} "
                    f"**{hero.get('nome', hero_id)}** • {hero.get('classe', 'sem classe')}"
                )
            else:
                lines.append(f"`{index + 1}.` Vaga livre")
        return "\n".join(lines)

    def build_embed(self):
        embed = discord.Embed(
            title="Criador de Banner Especial",
            description=(
                "Selecione **3 heróis 5⭐** e **5 heróis 4⭐**. "
                "O banner publicado dura sete dias exatos e substitui o especial atual.\n\n"
                "Os menus mostram 25 heróis por página. A busca também adiciona ou remove "
                "um personagem pelo nome ou ID."
            ),
            color=discord.Color.magenta(),
        )
        embed.add_field(
            name=f"Destaques 5⭐ • {len(self.selected[5])}/3",
            value=self._featured_text(5),
            inline=False,
        )
        embed.add_field(
            name=f"Destaques 4⭐ • {len(self.selected[4])}/5",
            value=self._featured_text(4),
            inline=False,
        )
        ready = all(
            len(self.selected[rarity]) == limit
            for rarity, limit in self.LIMITS.items()
        )
        embed.add_field(
            name="Publicação",
            value=(
                "Tudo pronto. O botão **Publicar por 7 dias** está liberado."
                if ready
                else "Preencha todas as vagas para liberar a publicação."
            ),
            inline=False,
        )
        embed.set_footer(
            text=(
                "TutoriUAU: curadoria é o nome elegante para escolher "
                "quem vai destruir a economia emocional dos jogadores."
            )
        )
        return embed

    def rebuild_selects(self):
        for child in list(self.children):
            if isinstance(child, BannerHeroSelect):
                self.remove_item(child)

        if self.pools[5]:
            self.add_item(BannerHeroSelect(self, 5, row=0))
        if self.pools[4]:
            self.add_item(BannerHeroSelect(self, 4, row=1))

        self.previous_5.disabled = self.pages[5] <= 0
        self.next_5.disabled = self.pages[5] >= self.page_count(5) - 1
        self.previous_4.disabled = self.pages[4] <= 0
        self.next_4.disabled = self.pages[4] >= self.page_count(4) - 1
        self.publish.disabled = not all(
            len(self.selected[rarity]) == limit
            for rarity, limit in self.LIMITS.items()
        )

    def toggle_hero(self, rarity, hero_id):
        selected = self.selected[rarity]
        hero_name = HEROES[hero_id].get("nome", hero_id)
        if hero_id in selected:
            selected.remove(hero_id)
            return False, f"**{hero_name}** foi removido dos destaques {rarity}⭐."
        if len(selected) >= self.LIMITS[rarity]:
            return False, (
                f"As {self.LIMITS[rarity]} vagas {rarity}⭐ já estão preenchidas. "
                "Remova alguém antes de adicionar outro herói."
            )
        selected.append(hero_id)
        return True, f"**{hero_name}** foi adicionado aos destaques {rarity}⭐."

    async def apply_page_selection(self, interaction, rarity, values):
        page_ids = set(self.current_page_ids(rarity))
        preserved = [
            hero_id
            for hero_id in self.selected[rarity]
            if hero_id not in page_ids
        ]
        candidate = preserved + [
            hero_id
            for hero_id in self.current_page_ids(rarity)
            if hero_id in values
        ]
        if len(candidate) > self.LIMITS[rarity]:
            await interaction.response.send_message(
                f"Você pode escolher somente {self.LIMITS[rarity]} heróis {rarity}⭐.",
                ephemeral=True,
            )
            return

        self.selected[rarity] = candidate
        self.rebuild_selects()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )

    async def change_page(self, interaction, rarity, direction):
        self.pages[rarity] = max(
            0,
            min(
                self.page_count(rarity) - 1,
                self.pages[rarity] + direction,
            ),
        )
        self.rebuild_selects()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )

    @discord.ui.button(label="5⭐ Anterior", style=discord.ButtonStyle.secondary, row=2)
    async def previous_5(self, interaction, button):
        await self.change_page(interaction, 5, -1)

    @discord.ui.button(label="5⭐ Próxima", style=discord.ButtonStyle.secondary, row=2)
    async def next_5(self, interaction, button):
        await self.change_page(interaction, 5, 1)

    @discord.ui.button(label="4⭐ Anterior", style=discord.ButtonStyle.secondary, row=3)
    async def previous_4(self, interaction, button):
        await self.change_page(interaction, 4, -1)

    @discord.ui.button(label="4⭐ Próxima", style=discord.ButtonStyle.secondary, row=3)
    async def next_4(self, interaction, button):
        await self.change_page(interaction, 4, 1)

    @discord.ui.button(label="Buscar", emoji="🔎", style=discord.ButtonStyle.primary, row=4)
    async def search(self, interaction, button):
        await interaction.response.send_modal(BannerHeroSearchModal(self))

    @discord.ui.button(label="Limpar", emoji="🧹", style=discord.ButtonStyle.secondary, row=4)
    async def clear(self, interaction, button):
        self.selected = {5: [], 4: []}
        self.rebuild_selects()
        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger, row=4)
    async def cancel(self, interaction, button):
        for child in self.children:
            child.disabled = True
        embed = self.build_embed()
        embed.title = "Criação de banner cancelada"
        embed.description = (
            "Nenhuma alteração foi publicada. TutoriUAU picotou o rascunho "
            "com uma solenidade completamente desnecessária."
        )
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(
        label="Publicar por 7 dias",
        emoji="✅",
        style=discord.ButtonStyle.success,
        row=4,
        disabled=True,
    )
    async def publish(self, interaction, button):
        if save_manual_banner is None:
            return await interaction.response.send_message(
                "O módulo de banners não está disponível.",
                ephemeral=True,
            )
        try:
            banner = save_manual_banner(
                HEROES,
                self.selected[5],
                self.selected[4],
                created_by=interaction.user.id,
            )
        except (ValueError, sqlite3.Error) as exc:
            return await interaction.response.send_message(
                f"Não consegui publicar o banner: `{exc}`",
                ephemeral=True,
            )

        for child in self.children:
            child.disabled = True
        embed = self.build_embed()
        embed.title = "Banner especial publicado"
        embed.description = (
            f"**{banner['name']}** está ativo por sete dias.\n"
            f"Período: {banner['period_label']}\n\n"
            "Depois da expiração, o banner automático volta sozinho caso "
            "nenhum outro seja criado."
        )
        embed.color = discord.Color.green()
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

class AdminCombatDummyUser:
    def __init__(self, name):
        self.id = 0
        self.name = name
        self.display_name = name
        self.mention = f"**{name}**"
        self.bot = True


class AdminCombatAddHeroModal(discord.ui.Modal, title="Adicionar herói ao teste"):
    hero_query = discord.ui.TextInput(
        label="Nome ou ID do herói",
        placeholder="Ex: Levi, sinbad, natsu_dragneel...",
        max_length=80,
    )

    def __init__(self, setup_view):
        super().__init__()
        self.setup_view = setup_view

    async def on_submit(self, interaction: discord.Interaction):
        ok, message = self.setup_view.add_hero(str(self.hero_query.value))
        await interaction.response.send_message(message, ephemeral=True)
        if ok and self.setup_view.message:
            await self.setup_view.message.edit(embed=self.setup_view.build_embed(), view=self.setup_view)


class AdminCombatTestSetupView(discord.ui.View):
    MAX_HEROES = 5

    def __init__(self, cog, ctx):
        super().__init__(timeout=300)
        self.cog = cog
        self.ctx = ctx
        self.heroes = []
        self.message = None
        self._sync_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Esse laboratório é de outro admin. TutoriUAU guardou a prancheta.", ephemeral=True)
            return False
        return True

    def _sync_buttons(self):
        for child in self.children:
            if getattr(child, "custom_id", None) == "start_debug_combat":
                child.disabled = not self.heroes
            if getattr(child, "custom_id", None) == "add_debug_hero":
                child.disabled = len(self.heroes) >= self.MAX_HEROES

    def _find_hero(self, query):
        query_norm = normalize_hero_name(query)
        if not query_norm:
            return None, None

        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome":
                continue
            if query_norm in {normalize_hero_name(hero_id), normalize_hero_name(hero.get("nome", hero_id))}:
                return hero_id, hero

        for hero_id, hero in HEROES.items():
            if hero_id == "id-nome":
                continue
            name_norm = normalize_hero_name(hero.get("nome", hero_id))
            if query_norm in name_norm or query_norm in normalize_hero_name(hero_id):
                return hero_id, hero
        return None, None

    def _build_test_hero(self, hero_id, hero):
        stats = calculate_hero_stats(hero, stars=1, level=1, equipment_bonuses=[])
        skill_ids = get_hero_skill_ids(hero, stars=99, rarity=hero.get("raridade", 1))
        return {
            "id": f"debug_{len(self.heroes) + 1}_{hero_id}",
            "hero_id": hero_id,
            "nome": f"{hero.get('nome', hero_id)} [Teste]",
            "classe": normalize_class(hero.get("classe", "neutro")),
            "level": 1,
            "hp": stats["hp"],
            "atk": stats["atk"],
            "matk": stats["matk"],
            "def": stats["def"],
            "spd": stats["spd"],
            "crt": stats["crt"],
            "stats": stats,
            "habilidades": skill_ids,
        }

    def add_hero(self, query):
        if len(self.heroes) >= self.MAX_HEROES:
            return False, "O teste aceita no máximo 5 heróis. Até laboratório precisa de limite, infelizmente."

        hero_id, hero = self._find_hero(query)
        if not hero:
            return False, f"Não encontrei **{query}** no catálogo."

        test_hero = self._build_test_hero(hero_id, hero)
        self.heroes.append(test_hero)
        self._sync_buttons()
        skills = ", ".join(SKILLS.get(skill_id, {}).get("nome", skill_id) for skill_id in test_hero["habilidades"]) or "nenhuma habilidade"
        return True, f"Adicionado: **{hero.get('nome', hero_id)}** Lv 1 base com habilidades liberadas: {skills}."

    def build_embed(self):
        self._sync_buttons()
        embed = discord.Embed(
            title="ADM Combate Teste",
            description=(
                "Monte até **5 heróis base Lv 1** contra uma calamidade com HP original e dano nerfado.\n"
                "Ela ataca de volta em escala Lv 1, para testar cura, revive, status e dano sem virar massacre instantâneo."
            ),
            color=discord.Color.dark_teal(),
        )
        if self.heroes:
            lines = []
            for index, hero in enumerate(self.heroes, start=1):
                skill_names = [SKILLS.get(skill_id, {}).get("nome", skill_id) for skill_id in hero.get("habilidades", [])]
                lines.append(
                    f"**{index}. {hero['nome']}** | ATK {hero['stats']['atk']} / MATK {hero['stats']['matk']} / HP {hero['stats']['hp']}\n"
                    f"Habilidades: {_cortar_texto(', '.join(skill_names) or 'nenhuma', 220)}"
                )
            embed.add_field(name="Equipe de Teste", value=_cortar_texto("\n\n".join(lines), 1024), inline=False)
        else:
            embed.add_field(name="Equipe de Teste", value="Nenhum herói selecionado ainda.", inline=False)
        embed.set_footer(text="TutoriUAU: escolha cobaias, aperte iniciar, descubra qual habilidade quebrou a matemática.")
        return embed

    @discord.ui.button(label="Adicionar Herói", style=discord.ButtonStyle.primary, custom_id="add_debug_hero")
    async def add_hero_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdminCombatAddHeroModal(self))

    @discord.ui.button(label="Iniciar Teste", style=discord.ButtonStyle.success, custom_id="start_debug_combat")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.heroes:
            return await interaction.response.send_message("Adicione pelo menos um herói antes. Testar o vazio é filosofia, não QA.", ephemeral=True)

        pool = [(boss_id, data) for boss_id, data in RAID_BOSSES.items() if data.get("tipo") in {"mensal", "calamidade"}]
        if not pool:
            return await interaction.response.send_message("Não encontrei calamidades cadastradas para usar como sparring de treino.", ephemeral=True)

        boss_id, boss_data = random.choice(pool)
        battle = AdminCombatTestBattleView(self.ctx, list(self.heroes), boss_id, boss_data)
        battle.add_message(interaction.message)
        await battle.processar_fila(interaction)

    @discord.ui.button(label="Limpar", style=discord.ButtonStyle.secondary)
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.heroes.clear()
        self._sync_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="Combate teste cancelado. TutoriUAU guardou os jalecos.", embed=None, view=None)


class AdminCombatSkillSelect(discord.ui.Select):
    def __init__(self, battle_view, skills):
        options = []
        for skill_id in skills[:25]:
            skill = SKILLS.get(skill_id, {})
            label = skill.get("nome", skill_id)[:100]
            description = f"{skill.get('tipo', 'habilidade')} | {skill.get('alvo', 'alvo')}"[:100]
            options.append(discord.SelectOption(label=label, value=skill_id, description=description))
        super().__init__(
            placeholder="Escolha a habilidade para testar...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.battle_view = battle_view

    async def callback(self, interaction: discord.Interaction):
        async with self.battle_view.action_lock:
            if not await self.battle_view._validate_admin_turn(interaction):
                return
            actor = self.battle_view.current_actor
            skill_id = self.values[0]
            if skill_id in actor.cooldowns:
                return await interaction.response.send_message("Essa habilidade está em recarga neste teste.", ephemeral=True)
            self.battle_view.log_display.append(self.battle_view._executar_habilidade(actor, skill_id))
            await self.battle_view.processar_fila(interaction)


class AdminCombatBasicButton(discord.ui.Button):
    def __init__(self, battle_view):
        super().__init__(label="Ataque Básico", style=discord.ButtonStyle.secondary)
        self.battle_view = battle_view

    async def callback(self, interaction: discord.Interaction):
        async with self.battle_view.action_lock:
            if not await self.battle_view._validate_admin_turn(interaction):
                return
            self.battle_view.log_display.append(self.battle_view._ataque_basico(self.battle_view.current_actor))
            await self.battle_view.processar_fila(interaction)


class AdminCombatExitButton(discord.ui.Button):
    def __init__(self, battle_view):
        super().__init__(label="Sair", style=discord.ButtonStyle.danger)
        self.battle_view = battle_view

    async def callback(self, interaction: discord.Interaction):
        if not await self.battle_view._validate_admin_turn(interaction, allow_any_turn=True):
            return
        await self.battle_view.encerrar(interaction, "Simulação encerrada manualmente.")


class AdminCombatControls(discord.ui.View):
    def __init__(self, battle_view):
        super().__init__(timeout=None)
        self.battle_view = battle_view
        actor = battle_view.current_actor
        available_skills = [
            skill_id
            for skill_id in (actor.habilidades if actor else [])
            if skill_id in SKILLS and skill_id not in actor.cooldowns
        ]
        if available_skills:
            self.add_item(AdminCombatSkillSelect(battle_view, available_skills))
        self.add_item(AdminCombatBasicButton(battle_view))
        self.add_item(AdminCombatExitButton(battle_view))


class AdminCombatTestBattleView(PvpBattleView if PvpBattleView else discord.ui.View):
    def __init__(self, ctx, heroes, calamity_id, calamity_data):
        self.ctx = ctx
        self.calamity_id = calamity_id
        self.calamity_data = calamity_data
        opponent = AdminCombatDummyUser(calamity_data.get("nome", calamity_id))
        def nerf_stat(value, divisor, minimum, maximum):
            return max(minimum, min(maximum, int((value or 0) / divisor)))

        calamity_skills = list(calamity_data.get("habilidades") or [])
        if calamity_data.get("habilidade"):
            calamity_skills.append(calamity_data["habilidade"])
        calamity_skills = [skill_id for skill_id in calamity_skills if skill_id in SKILLS]
        enemy_raw = {
            "id": calamity_id,
            "nome": f"{calamity_data.get('nome', calamity_id)} [Teste]",
            "classe": "calamidade",
            "stats": {
                "hp": int(calamity_data.get("hp", 500000) or 500000),
                "atk": nerf_stat(calamity_data.get("atk", 0), 220, 8, 30),
                "matk": nerf_stat(calamity_data.get("matk", 0), 220, 8, 30),
                "def": nerf_stat(calamity_data.get("def", 0), 180, 4, 25),
                "spd": nerf_stat(calamity_data.get("spd", 0), 12, 6, 18),
                "crt": nerf_stat(calamity_data.get("crt", 0), 5, 0, 8),
                "level": 1,
            },
            "habilidades": calamity_skills,
        }
        super().__init__(None, ctx.channel, ctx.author, opponent, heroes, [enemy_raw], online=False)
        for enemy in self.team_b:
            enemy.habilidades = calamity_skills
            enemy.cap_outgoing_damage = lambda amount, is_skill=True: min(amount, 75) if is_skill else amount
        self.log_display = [
            f"Teste iniciado contra {self.team_b[0].clean_name}. HP original mantido, atributos ofensivos Lv 1 e habilidades com dano limitado."
        ]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Só o admin que abriu o teste pode clicar aqui.", ephemeral=True)
            return False
        return True

    async def _validate_admin_turn(self, interaction, allow_any_turn=False):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Esse teste pertence a outro admin.", ephemeral=True)
            return False
        if self.finalizado:
            await interaction.response.send_message("Essa simulação já terminou.", ephemeral=True)
            return False
        if not allow_any_turn and (not self.current_actor or self.current_actor.is_enemy):
            await interaction.response.send_message("Ainda não é turno de um herói de teste.", ephemeral=True)
            return False
        return True

    def _build_controls(self):
        return AdminCombatControls(self)

    async def _atualizar_mensagem(self, interaction=None):
        self._restart_timeout()
        actor_name = self.current_actor.clean_name if self.current_actor else "aguardando"
        target = self.team_b[0]
        embed = discord.Embed(
            title="ADM Combate Teste",
            description=f"Turno de **{actor_name}**. Escolha exatamente o que quer testar.",
            color=discord.Color.dark_teal(),
        )
        embed.add_field(name="Heróis de Teste", value=_cortar_texto(self._barra_time(self.team_a)), inline=True)
        embed.add_field(name="Calamidade de Teste", value=_cortar_texto(self._barra_time(self.team_b)), inline=True)
        embed.add_field(
            name="HP do Alvo",
            value=(
                f"**{target.hp:,}/{target.max_hp:,}**\n"
                f"ATK {target.get_stat('atk'):,} | MATK {target.get_stat('matk'):,} | DEF {target.get_stat('def'):,}"
            ),
            inline=False,
        )
        embed.add_field(name="Log de Teste", value=f"```{_cortar_texto(chr(10).join(self.log_display[-8:]), 1000)}```", inline=False)
        embed.set_footer(text="TutoriUAU: isso aqui é um laboratório. Se explodir, pelo menos agora temos log.")

        controls = self._build_controls()
        if interaction:
            try:
                await interaction.response.edit_message(embed=embed, view=controls)
            except discord.errors.InteractionResponded:
                await interaction.message.edit(embed=embed, view=controls)
        elif self.messages:
            await self.messages[0].edit(embed=embed, view=controls)
        else:
            message = await self.ctx.send(embed=embed, view=controls)
            self.add_message(message)

    async def processar_fila(self, interaction=None):
        while not self.finalizado:
            vivos_a = self._get_alive(self.team_a)
            vivos_b = self._get_alive(self.team_b)
            if not vivos_a:
                return await self.encerrar(interaction, "Todos os heróis de teste caíram. Isso não deveria acontecer, mas o universo é criativo.")
            if not vivos_b:
                return await self.encerrar(interaction, "A calamidade de teste foi derrotada.")

            all_alive = vivos_a + vivos_b
            self.turn_queue = [entity for entity in self.turn_queue if not entity.is_dead]
            if not self.turn_queue:
                self.turn_queue = sorted(all_alive, key=lambda entity: (entity.get_stat("spd"), 0 if entity.is_enemy else 1), reverse=True)

            actor = self.turn_queue.pop(0)
            estava_atordoado = actor.is_stunned()
            dot_logs = actor.tick_effects()
            self.log_display.extend(dot_logs)
            self.log_display.extend(self._sincronizar_clones())

            if actor.is_dead:
                continue
            if actor.is_enemy:
                if estava_atordoado:
                    self.log_display.append(f"{actor.clean_name} está atordoada e perdeu a vez.")
                    continue
                skill_id = choose_ai_combat_skill(actor, SKILLS, self.team_b, self.team_a, skill_chance=0.45)
                if skill_id and not actor.is_silenced():
                    self.log_display.append(self._executar_habilidade(actor, skill_id))
                else:
                    self.log_display.append(self._ataque_basico(actor))
                continue
            if estava_atordoado:
                self.log_display.append(f"{actor.clean_name} está atordoado e perdeu a vez.")
                continue

            self.current_actor = actor
            await self._atualizar_mensagem(interaction)
            return

    async def encerrar(self, interaction=None, motivo="Simulação encerrada."):
        if self.finalizado:
            return
        self.finalizado = True
        self._cancel_timeout()
        embed = discord.Embed(
            title="ADM Combate Teste Encerrado",
            description=motivo,
            color=discord.Color.orange(),
        )
        embed.add_field(name="Últimos acontecimentos", value=f"```{_cortar_texto(chr(10).join(self.log_display[-10:]), 1000)}```", inline=False)
        embed.set_footer(text="TutoriUAU: relatório encerrado. Nenhuma calamidade real foi ferida. Tecnicamente.")
        if interaction:
            try:
                await interaction.response.edit_message(embed=embed, view=None)
            except discord.errors.InteractionResponded:
                await interaction.message.edit(embed=embed, view=None)
        for message in list(self.messages):
            if interaction and message.id == interaction.message.id:
                continue
            try:
                await message.edit(embed=embed, view=None)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

    async def on_timeout(self):
        if not self.finalizado:
            await self.encerrar(None, "Simulação encerrada por inatividade.")


class Adm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()
        self._init_codes_db()
        self.bot.add_check(self.verificar_exilados)

    async def _open_banner_builder(self, ctx):
        view = BannerBuilderView(ctx.author.id)
        if len(view.pools[5]) < view.LIMITS[5] or len(view.pools[4]) < view.LIMITS[4]:
            return await ctx.send(
                "O catálogo não possui heróis elegíveis suficientes para montar o banner. "
                "São necessários 3 heróis 5⭐ e 5 heróis 4⭐."
            )
        message = await ctx.send(embed=view.build_embed(), view=view)
        view.message = message

    def cog_unload(self):
        self.bot.remove_check(self.verificar_exilados)

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ban_list(
            user_id TEXT PRIMARY KEY
        )
        """)
        ensure_admin_logs_schema(cursor)
        conn.commit()
        conn.close()

    def _init_codes_db(self):
        conn = connect_codes_db()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            recompensa TEXT NOT NULL,
            created_at INTEGER DEFAULT 0,
            expires_at INTEGER DEFAULT 0
        )
        """)
        cursor.execute("PRAGMA table_info(codes)")
        code_columns = {row[1] for row in cursor.fetchall()}
        if "created_at" not in code_columns:
            cursor.execute("ALTER TABLE codes ADD COLUMN created_at INTEGER DEFAULT 0")
        if "expires_at" not in code_columns:
            cursor.execute("ALTER TABLE codes ADD COLUMN expires_at INTEGER DEFAULT 0")
            
        cursor.execute("UPDATE codes SET expires_at = 0 WHERE expires_at IS NULL")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_redemptions (
            code TEXT NOT NULL,
            user_id TEXT NOT NULL,
            redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (code, user_id)
        )
        """)
        conn.commit()
        conn.close()

    def _formatar_recompensa_code(self, recompensa):
        recompensa = recompensa.strip()
        recompensa_upper = recompensa.upper()

        if re.fullmatch(r"G\d+", recompensa_upper):
            valor = int(recompensa_upper[1:])
            if valor <= 0: return None, "O valor de Gold precisa ser maior que zero."
            return f"G{valor}", f"{valor} Gold"

        if re.fullmatch(r"T\d+", recompensa_upper):
            valor = int(recompensa_upper[1:])
            if valor <= 0: return None, "O valor de Tickets precisa ser maior que zero."
            return f"T{valor}", f"{valor} Summon Ticket(s)"

        recompensa_id = recompensa.lower().replace(" ", "_")
        if not re.fullmatch(r"[a-z0-9_]+", recompensa_id):
            return None, "Use `G1000`, `T10`, ou um ID com letras/numeros/underscore, tipo `levi_ackerman`."

        if recompensa_id in HEROES:
            nome = HEROES[recompensa_id].get("nome", recompensa_id)
            return recompensa_id, f"Herói: {nome}"

        nome_item = EQUIPAMENTOS.get(recompensa_id, {}).get("nome", recompensa_id.replace("_", " ").title())
        return recompensa_id, f"Item: {nome_item}"

    def _formatar_recompensas_code(self, recompensas):
        normalizadas = []
        descricoes = []
        for recompensa in str(recompensas or "").split():
            normalizada, descricao = self._formatar_recompensa_code(recompensa)
            if not normalizada:
                return None, descricao
            normalizadas.append(normalizada)
            descricoes.append(descricao)
        if not normalizadas:
            return None, "Informe ao menos uma recompensa."
        return " ".join(normalizadas), " + ".join(descricoes)

    async def _criar_code(self, ctx, codigo, recompensa, valid_days=None):
        if not codigo or not recompensa:
            return await ctx.send(
                "⚠ Uso: `echo adm criarcode <CODE> <recompensas>` ou "
                "`echo adm criarcode temp <dias> <CODE> <recompensas>`"
            )

        codigo = codigo.strip().upper()
        if not re.fullmatch(r"[A-Z0-9_-]+", codigo):
            return await ctx.send("❌ O nome do code só pode ter letras, números, `_` ou `-`.")

        recompensa_normalizada, descricao = self._formatar_recompensas_code(recompensa)
        if not recompensa_normalizada:
            return await ctx.send(f"❌ Recompensa inválida. {descricao}")

        created_at = int(time.time())
        expires_at = 0
        if valid_days is not None:
            try:
                valid_days = int(valid_days)
            except (TypeError, ValueError):
                return await ctx.send("❌ A duração do code temporário precisa ser um número de dias.")
            if valid_days <= 0:
                return await ctx.send("❌ O code temporário precisa durar pelo menos 1 dia.")
            expires_at = created_at + (valid_days * 86400)

        conn = connect_codes_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO codes (code, recompensa, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (codigo, recompensa_normalizada, created_at, expires_at),
            )
            conn.commit()
        except Exception as e:
            return await ctx.send(f"❌ Erro ao criar código: {e}")
        finally:
            conn.close()

        validade = f"válido por **{valid_days} dia(s)**" if valid_days is not None else "permanente"
        await ctx.send(
            f"✅ Código **{codigo}** criado/atualizado, {validade}!\n"
            f"Recompensas: **{descricao}** (`{recompensa_normalizada}`)."
        )

    async def _deletar_code(self, ctx, codigo):
        codigo = str(codigo or "").strip().upper()
        if not codigo:
            return await ctx.send("⚠ Uso: `echo adm delete code <NOME-DO-CODE>`")

        conn = connect_codes_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM codes WHERE code = ?", (codigo,))
        deleted = cursor.rowcount
        cursor.execute("DELETE FROM code_redemptions WHERE code = ?", (codigo,))
        conn.commit()
        conn.close()

        if not deleted:
            return await ctx.send(f"❌ O code **{codigo}** não existe ou já foi invalidado.")
        await ctx.send(f"🗑️ Code **{codigo}** invalidado. TutoriUAU carimbou: não vale mais nem com jeitinho.")

    async def _delete_character(self, ctx, target_id, raw_name):
        if not target_id or not raw_name:
            return await ctx.send("⚠ Uso: `echo adm delechar @usuário <nome-do-personagem>`")

        requested_name = normalize_hero_name(raw_name)
        catalog_matches = {
            hero_id
            for hero_id, hero_data in HEROES.items()
            if hero_id != "id-nome"
            and requested_name in {
                normalize_hero_name(hero_id),
                normalize_hero_name(hero_data.get("nome", hero_id)),
            }
        }
        if not catalog_matches:
            return await ctx.send(
                f"❌ Não encontrei **{raw_name.strip()}** no catálogo. "
                "TutoriUAU conferiu duas vezes e culpou a ortografia na terceira."
            )

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(heroes)")
            hero_columns = {row[1] for row in cursor.fetchall()}
            equipment_columns = [
                column
                for column in ("equip_atk", "equip_def", "equip_livre")
                if column in hero_columns
            ]
            selected_columns = ["id", "hero_id", "rarity", "stars", "level"] + equipment_columns
            placeholders = ",".join("?" for _ in catalog_matches)
            cursor.execute(
                f"""
                SELECT {', '.join(selected_columns)}
                FROM heroes
                WHERE user_id = ? AND hero_id IN ({placeholders})
                """,
                (str(target_id), *sorted(catalog_matches)),
            )
            owned_rows = cursor.fetchall()
            if not owned_rows:
                return await ctx.send(
                    f"❌ <@{target_id}> não possui **{raw_name.strip()}**. "
                    "Não dá para apagar o que já não está lá; o vazio venceu."
                )

            owned_hero_ids = {row[1] for row in owned_rows}
            if len(owned_hero_ids) > 1:
                choices = ", ".join(
                    HEROES.get(hero_id, {}).get("nome", hero_id)
                    for hero_id in sorted(owned_hero_ids)
                )
                return await ctx.send(f"❌ O nome ficou ambíguo entre: **{choices}**. Use o nome completo.")

            def deletion_priority(row):
                canonical = int(HEROES.get(row[1], {}).get("raridade", row[2] or 1) or 1)
                rarity_is_wrong = int(row[2] or 0) != canonical
                return (0 if rarity_is_wrong else 1, int(row[3] or 1), int(row[4] or 1), -int(row[0]))

            selected = min(owned_rows, key=deletion_priority)
            hero_db_id, hero_id, stored_rarity, hero_stars, hero_level = selected[:5]
            equipped_items = [item for item in selected[5:] if item]
            hero_data = HEROES.get(hero_id, {})
            hero_name = hero_data.get("nome", hero_id)
            canonical_rarity = int(hero_data.get("raridade", stored_rarity or 1) or 1)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    item_name TEXT,
                    quantity INTEGER DEFAULT 1
                )
            """)
            for item_name in equipped_items:
                cursor.execute(
                    "SELECT id FROM inventory WHERE user_id = ? AND item_name = ? ORDER BY id LIMIT 1",
                    (str(target_id), item_name),
                )
                inventory_row = cursor.fetchone()
                if inventory_row:
                    cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (inventory_row[0],))
                else:
                    cursor.execute(
                        "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)",
                        (str(target_id), item_name),
                    )

            cursor.execute(
                "UPDATE players SET main_hero = NULL WHERE user_id = ? AND CAST(main_hero AS TEXT) = ?",
                (str(target_id), str(hero_db_id)),
            )
            removed_from_main = cursor.rowcount > 0

            cursor.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'teams'")
            removed_from_party = False
            if cursor.fetchone():
                for slot in ("slot_2", "slot_3", "slot_4", "slot_5"):
                    cursor.execute(
                        f"UPDATE teams SET {slot} = NULL WHERE user_id = ? AND CAST({slot} AS TEXT) = ?",
                        (str(target_id), str(hero_db_id)),
                    )
                    removed_from_party = removed_from_party or cursor.rowcount > 0

            cursor.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'champion_defense_teams'"
            )
            defense_reset = False
            if cursor.fetchone():
                cursor.execute(
                    "SELECT hero_ids FROM champion_defense_teams WHERE user_id = ?",
                    (str(target_id),),
                )
                defense_row = cursor.fetchone()
                try:
                    defense_ids = [str(value) for value in json.loads(defense_row[0] or "[]")] if defense_row else []
                except (TypeError, ValueError, json.JSONDecodeError):
                    defense_ids = []
                if str(hero_db_id) in defense_ids:
                    cursor.execute("DELETE FROM champion_defense_teams WHERE user_id = ?", (str(target_id),))
                    defense_reset = True

            cursor.execute(
                "DELETE FROM heroes WHERE id = ? AND user_id = ?",
                (hero_db_id, str(target_id)),
            )
            if cursor.rowcount != 1:
                raise sqlite3.DatabaseError("o personagem mudou antes da exclusão")

            ensure_admin_logs_schema(cursor)
            now = int(time.time())
            cursor.execute(
                """
                INSERT INTO administrative_logs
                (user_id, action, value, admin_id, timestamp, status, resolution, resolved_by, resolved_at)
                VALUES (?, 'delete_character', ?, ?, ?, 'resolved', ?, ?, ?)
                """,
                (
                    str(target_id),
                    f"{hero_name} | hero_db_id={hero_db_id}",
                    str(ctx.author.id),
                    now,
                    f"Personagem removido por {ctx.author} via echo adm delechar.",
                    str(ctx.author.id),
                    now,
                ),
            )
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            return await ctx.send(f"❌ Não consegui apagar o personagem: `{exc}`")
        finally:
            conn.close()

        cleanup = []
        if removed_from_main:
            cleanup.append("herói principal limpo")
        if removed_from_party:
            cleanup.append("slots da party limpos")
        if defense_reset:
            cleanup.append("defesa dos Campeões removida")
        if equipped_items:
            cleanup.append(f"{len(equipped_items)} equipamento(s) devolvido(s)")
        cleanup_text = f"\nAjustes: {', '.join(cleanup)}." if cleanup else ""
        copies_text = (
            "\nHavia mais de uma cópia; removi a de raridade incorreta ou, na ausência disso, a menos evoluída."
            if len(owned_rows) > 1
            else ""
        )
        await ctx.send(
            f"🗑️ **{hero_name}** (`ID {hero_db_id}`, {'⭐' * canonical_rarity}, Lv {hero_level}) "
            f"foi removido de <@{target_id}>.{copies_text}{cleanup_text}\n"
            "TutoriUAU registrou a intervenção antes que alguém dissesse que foi magia."
        )

    def _normalizar_item_admin(self, item_name):
        text = unicodedata.normalize("NFKD", str(item_name or ""))
        text = "".join(char for char in text if not unicodedata.combining(char))
        text = re.sub(r"[^a-zA-Z0-9_ -]+", "", text)
        text = re.sub(r"\s+", "_", text.strip().lower())
        return text

    async def _delete_item(self, ctx, target_id, raw_item):
        if not target_id or not raw_item:
            return await ctx.send("⚠ Uso: `echo adm deletar item @usuário <nome-do-item>`")

        item_query = str(raw_item).strip()
        normalized_query = self._normalizar_item_admin(item_query)
        if not normalized_query:
            return await ctx.send("❌ Informe o nome do item para apagar. O vazio já foi nerfado.")

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, item_name, quantity FROM inventory WHERE user_id = ?",
            (str(target_id),),
        )
        rows = cursor.fetchall()

        matches = []
        for item_id, item_name, quantity in rows:
            stored_norm = self._normalizar_item_admin(item_name)
            if item_name == item_query or stored_norm == normalized_query:
                matches.append((item_id, item_name, quantity))

        if not matches:
            partial = [
                (item_id, item_name, quantity)
                for item_id, item_name, quantity in rows
                if normalized_query in self._normalizar_item_admin(item_name)
            ]
            if len(partial) == 1:
                matches = partial

        if not matches:
            conn.close()
            return await ctx.send(
                f"❌ Não encontrei **{item_query}** na mochila de <@{target_id}>. "
                "TutoriUAU: ou o item não existe, ou está disfarçado com outro ID."
            )

        removed_total = sum(max(0, int(quantity or 0)) for _, _, quantity in matches)
        removed_names = ", ".join(f"{quantity}x `{item_name}`" for _, item_name, quantity in matches)
        cursor.executemany("DELETE FROM inventory WHERE id = ?", [(item_id,) for item_id, _, _ in matches])
        conn.commit()
        conn.close()

        await ctx.send(
            f"🗑️ Removi **{removed_total}** item(ns) da mochila de <@{target_id}>: {removed_names}.\n"
            "TutoriUAU: faxina administrativa concluída. O item bugado foi escoltado para fora."
        )

    def _nivel_loja_por_prosperidade(self, prosperidade):
        if prosperidade >= 100: return 4
        if prosperidade >= 75: return 3
        if prosperidade >= 50: return 2
        return 1

    def _prosperidade_para_nivel_loja(self, nivel):
        return {1: 0, 2: 50, 3: 75, 4: 100}.get(nivel, 100)

    def _sync_shop_level_for_guild_members(self, cursor, guild, nivel, extra_user_id=None):
        if not guild:
            cursor.execute("UPDATE summon_data SET shop_level = ?", (nivel,))
            return None

        member_ids = {str(getattr(guild, "owner_id", "") or "")}
        member_ids.update(str(member.id) for member in getattr(guild, "members", []) if not member.bot)
        if extra_user_id:
            member_ids.add(str(extra_user_id))
        member_ids = [member_id for member_id in member_ids if member_id]
        if not member_ids:
            return 0

        placeholders = ",".join("?" for _ in member_ids)
        cursor.execute(
            f"UPDATE summon_data SET shop_level = ? WHERE user_id IN ({placeholders})",
            (nivel, *member_ids),
        )
        return cursor.rowcount

    async def _melhorar_loja(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        if ctx.guild:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cidades(
                guild_id TEXT PRIMARY KEY,
                nome TEXT DEFAULT 'Capital de Wolford',
                hp INTEGER DEFAULT 100000, max_hp INTEGER DEFAULT 100000,
                moral INTEGER DEFAULT 100, suprimentos INTEGER DEFAULT 0,
                max_suprimentos INTEGER DEFAULT 5000, prosperidade INTEGER DEFAULT 0
            )
            """)
            cursor.execute("""
                INSERT OR IGNORE INTO cidades
                (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
                VALUES (?, 'Capital de Wolford', 100000, 100000, 100, 0, 5000, 0)
            """, (str(ctx.guild.id),))
            cursor.execute("SELECT prosperidade FROM cidades WHERE guild_id = ?", (str(ctx.guild.id),))
            prosperidade_atual = cursor.fetchone()[0] or 0
        else:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS city_stats (
                id INTEGER PRIMARY KEY,
                hp INTEGER DEFAULT 100000, max_hp INTEGER DEFAULT 100000,
                moral INTEGER DEFAULT 100, suprimentos INTEGER DEFAULT 0,
                max_suprimentos INTEGER DEFAULT 5000, prosperidade INTEGER DEFAULT 0
            )
            """)
            cursor.execute("INSERT OR IGNORE INTO city_stats (id) VALUES (1)")
            cursor.execute("SELECT prosperidade FROM city_stats WHERE id = 1")
            prosperidade_atual = cursor.fetchone()[0] or 0
        nivel_atual = self._nivel_loja_por_prosperidade(prosperidade_atual)

        if nivel_atual >= 4:
            conn.close()
            return await ctx.send("A loja já está no nível máximo: **4 (Wolford Dourada)**.")

        novo_nivel = nivel_atual + 1
        nova_prosperidade = self._prosperidade_para_nivel_loja(novo_nivel)

        if ctx.guild:
            cursor.execute(
                "UPDATE cidades SET prosperidade = ? WHERE guild_id = ?",
                (nova_prosperidade, str(ctx.guild.id)),
            )
        else:
            cursor.execute("UPDATE city_stats SET prosperidade = ? WHERE id = 1", (nova_prosperidade,))

        sincronizados = self._sync_shop_level_for_guild_members(cursor, ctx.guild, novo_nivel, ctx.author.id)
        conn.commit()
        conn.close()

        sync_text = ""
        if sincronizados is None:
            sync_text = " Gacha sincronizado globalmente."
        elif sincronizados > 0:
            sync_text = f" Gacha sincronizado para **{sincronizados}** jogador(es) deste servidor."
        await ctx.send(
            f"🏪 Loja melhorada de **Nível {nivel_atual}** para **Nível {novo_nivel}**. "
            f"Prosperidade ajustada para **{nova_prosperidade}/100**.{sync_text}\n"
            "TutoriUAU: agora sobe degrau por degrau, como uma escada normal. Revolucionário."
        )

    async def verificar_exilados(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM ban_list WHERE user_id = ?", (str(ctx.author.id),))
        banned = cursor.fetchone()
        conn.close()
        
        if banned:
            await ctx.send("🚫 **EXILADO!** Você foi banido de Wolford pelos Deuses e suas invocações não têm mais poder aqui.")
            return False
        return True

    def _one(self, cursor, query, params=(), default=0):
        try:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row[0] if row and row[0] is not None else default
        except sqlite3.OperationalError:
            return default

    async def _stats_embed(self, ctx):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        now = int(time.time())
        day_ago = now - 86400

        total_players = self._one(cursor, "SELECT COUNT(*) FROM players")
        active_day = self._one(
            cursor,
            """
            SELECT COUNT(*) FROM players
            WHERE MAX(COALESCE(last_hunt, 0), COALESCE(last_adventure, 0), COALESCE(last_dungeon, 0), COALESCE(last_arena, 0)) >= ?
            """,
            (day_ago,),
        )
        summons = self._one(cursor, "SELECT COALESCE(SUM(total_summons), 0) FROM summon_data")
        current_gold = self._one(cursor, "SELECT COALESCE(SUM(gold), 0) FROM players")
        guild_gold = self._one(cursor, "SELECT COALESCE(SUM(gold_bank), 0) FROM player_guilds")
        estimated_spent = (summons or 0) * 1000
        estimated_generated = (current_gold or 0) + (guild_gold or 0) + estimated_spent
        dungeons = self._one(cursor, "SELECT COUNT(*) FROM players WHERE COALESCE(last_dungeon, 0) > 0")

        try:
            cursor.execute("""
                SELECT h.hero_id, COUNT(*) AS total
                FROM players p
                JOIN heroes h ON h.id = CAST(p.main_hero AS INTEGER)
                WHERE p.main_hero IS NOT NULL
                GROUP BY h.hero_id
                ORDER BY total DESC
                LIMIT 1
            """)
            hero_row = cursor.fetchone()
        except sqlite3.OperationalError:
            hero_row = None
        hero_text = "Sem dados"
        if hero_row:
            hero_text = f"{HEROES.get(hero_row[0], {}).get('nome', hero_row[0])} ({hero_row[1]} usos)"

        try:
            cursor.execute("""
                SELECT pt.pet_id, COUNT(*) AS total
                FROM players p
                JOIN pets pt ON pt.id = CAST(p.main_pet AS INTEGER)
                WHERE p.main_pet IS NOT NULL
                GROUP BY pt.pet_id
                ORDER BY total DESC
                LIMIT 1
            """)
            pet_row = cursor.fetchone()
        except sqlite3.OperationalError:
            pet_row = None
        pet_text = "Sem dados"
        if pet_row:
            pet_text = f"{PETS.get(pet_row[0], {}).get('nome', pet_row[0])} ({pet_row[1]} usos)"

        try:
            cursor.execute("""
                SELECT name, level, raid_score
                FROM player_guilds
                ORDER BY raid_score DESC, level DESC, gold_bank DESC
                LIMIT 1
            """)
            guild_row = cursor.fetchone()
        except sqlite3.OperationalError:
            guild_row = None
        guild_text = f"{guild_row[0]} - Nv {guild_row[1]} | Score {guild_row[2]:,}" if guild_row else "Sem guildas"
        conn.close()

        embed = discord.Embed(
            title="ADM Stats // Painel do TutoriUAU",
            description="Números do reino. Ouro antigo é estimado porque ninguém colocou contador no começo. Excelente decisão, zero consequências.",
            color=discord.Color.dark_teal(),
        )
        embed.add_field(name="Jogadores", value=f"Total: **{total_players:,}**\nAtivos 24h: **{active_day:,}**", inline=True)
        embed.add_field(name="Summons feitos", value=f"**{summons:,}**", inline=True)
        embed.add_field(name="Economia", value=f"Ouro gerado estimado: **{estimated_generated:,}**\nOuro gasto estimado: **{estimated_spent:,}**", inline=False)
        embed.add_field(name="Dungeons feitas", value=f"**{dungeons:,}** jogadores com dungeon registrada", inline=True)
        embed.add_field(name="Herói mais usado", value=hero_text, inline=True)
        embed.add_field(name="Pet mais usado", value=pet_text, inline=True)
        embed.add_field(name="Guilda mais forte", value=guild_text, inline=False)
        return embed

    async def _show_admin_logs(self, ctx, target_id=None, status_filter=None):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_admin_logs_schema(cursor)
        if target_id and status_filter:
            cursor.execute(
                """
                SELECT id, user_id, action, value, admin_id, timestamp,
                       COALESCE(status, 'open'), resolution, resolved_by, resolved_at
                FROM administrative_logs
                WHERE user_id = ? AND COALESCE(status, 'open') = ?
                ORDER BY id DESC LIMIT 10
                """,
                (target_id, status_filter),
            )
        elif target_id:
            cursor.execute(
                """
                SELECT id, user_id, action, value, admin_id, timestamp,
                       COALESCE(status, 'open'), resolution, resolved_by, resolved_at
                FROM administrative_logs
                WHERE user_id = ?
                ORDER BY CASE COALESCE(status, 'open') WHEN 'open' THEN 0 ELSE 1 END, id DESC
                LIMIT 10
                """,
                (target_id,),
            )
        elif status_filter:
            cursor.execute(
                """
                SELECT id, user_id, action, value, admin_id, timestamp,
                       COALESCE(status, 'open'), resolution, resolved_by, resolved_at
                FROM administrative_logs
                WHERE COALESCE(status, 'open') = ?
                ORDER BY id DESC LIMIT 10
                """,
                (status_filter,),
            )
        else:
            cursor.execute("""
                SELECT id, user_id, action, value, admin_id, timestamp,
                       COALESCE(status, 'open'), resolution, resolved_by, resolved_at
                FROM administrative_logs
                ORDER BY CASE COALESCE(status, 'open') WHEN 'open' THEN 0 ELSE 1 END, id DESC
                LIMIT 10
            """)
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        if not rows:
            return await ctx.send("Nenhum log administrativo encontrado. Milagre ou esquecimento, ainda não decidi.")
        lines = []
        for log_id, uid, action, value, admin_id, ts, status, resolution, resolved_by, resolved_at in rows:
            admin = f" por <@{admin_id}>" if admin_id else ""
            when = f"<t:{ts}:R>" if ts else "sem data"
            status_text = "ABERTO" if status == "open" else "RESOLVIDO"
            line = f"`#{log_id}` **[{status_text}]** <@{uid}> - **{action}**{admin} - {when}\n{value or 'Sem valor.'}"
            if status == "resolved":
                resolved_when = f"<t:{resolved_at}:R>" if resolved_at else "sem data"
                line += f"\nResposta de <@{resolved_by}> ({resolved_when}): {resolution or 'Sem mensagem.'}"
            lines.append(line)
        embed = discord.Embed(
            title="Logs Administrativos",
            description="\n\n".join(lines)[:4000],
            color=discord.Color.orange(),
        )
        embed.set_footer(text="TutoriUAU: use `echo adm resolver <ID> <mensagem>` para fechar uma solicitação.")
        await ctx.send(embed=embed)

    async def _manual_admin_log(self, ctx, target_id, raw_text):
        if not target_id or not raw_text:
            return await ctx.send("Uso: `echo adm log @usuário <ação> | <valor>`")
        if "|" in raw_text:
            action, value = [part.strip() for part in raw_text.split("|", 1)]
        else:
            action, value = "registro_manual", raw_text.strip()
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_admin_logs_schema(cursor)
        cursor.execute(
            """
            INSERT INTO administrative_logs
            (user_id, action, value, admin_id, timestamp, status)
            VALUES (?, ?, ?, ?, ?, 'open')
            """,
            (target_id, action[:80], value[:900], str(ctx.author.id), int(time.time())),
        )
        conn.commit()
        conn.close()
        await ctx.send(f"Log registrado para <@{target_id}>. Papelada feita. Odeio que isso funcione.")

    async def _resolve_admin_log(self, ctx, raw_log_id, resolution):
        if not raw_log_id or not raw_log_id.isdigit() or not resolution:
            return await ctx.send("Uso: `echo adm resolver <ID> <mensagem para o jogador>`")

        log_id = int(raw_log_id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_admin_logs_schema(cursor)
        cursor.execute(
            "SELECT user_id, action, value, COALESCE(status, 'open') FROM administrative_logs WHERE id = ?",
            (log_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return await ctx.send(f"Não encontrei o log **#{log_id}**. Nem toda papelada merece existir, mas essa nem chegou a nascer.")

        user_id, action, value, status = row
        if status == "resolved":
            conn.close()
            return await ctx.send(f"O log **#{log_id}** já está resolvido.")

        resolution = resolution.strip()[:1500]
        resolved_at = int(time.time())
        cursor.execute(
            """
            UPDATE administrative_logs
            SET status = 'resolved', resolution = ?, resolved_by = ?, resolved_at = ?
            WHERE id = ?
            """,
            (resolution, str(ctx.author.id), resolved_at, log_id),
        )
        conn.commit()
        conn.close()

        notified = False
        try:
            player = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
            notice = discord.Embed(
                title=f"Sua solicitação #{log_id} foi resolvida",
                description=resolution,
                color=discord.Color.green(),
            )
            notice.add_field(name="Solicitação", value=(value or action or "Sem descrição.")[:1024], inline=False)
            notice.set_footer(text=f"Resposta enviada por {ctx.author.display_name}. TutoriUAU arquivou a papelada com surpreendente competência.")
            await player.send(embed=notice)
            notified = True
        except (discord.Forbidden, discord.NotFound, discord.HTTPException, ValueError):
            notified = False

        delivery = "O jogador recebeu a resposta por mensagem direta." if notified else "Não consegui enviar DM ao jogador, mas a resolução ficou salva no painel."
        await ctx.send(f"Log **#{log_id}** marcado como resolvido. {delivery}")

    async def _reopen_admin_log(self, ctx, raw_log_id):
        if not raw_log_id or not raw_log_id.isdigit():
            return await ctx.send("Uso: `echo adm reabrir <ID>`")
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_admin_logs_schema(cursor)
        cursor.execute(
            """
            UPDATE administrative_logs
            SET status = 'open', resolution = '', resolved_by = NULL, resolved_at = 0
            WHERE id = ?
            """,
            (int(raw_log_id),),
        )
        changed = cursor.rowcount
        conn.commit()
        conn.close()
        if not changed:
            return await ctx.send("Esse log não existe.")
        await ctx.send(f"Log **#{int(raw_log_id)}** reaberto. O TutoriUAU tirou a pasta do arquivo morto.")

    @commands.group(name="adm", invoke_without_command=True)
    async def adm(self, ctx, action: str = None, arg1: str = None, *, arg2: str = None):
        if ctx.author.id not in ADM_USERS:
            await ctx.send("❌ Acesso negado. Você não tem permissão para usar ferramentas dos Deuses.")
            return

        if not action:
            await ctx.send("⚠ Comandos ADM disponíveis:\n"
                           "`echo adm set_iniciar` (Define o canal de invasão no Servidor)\n"
                           "`echo adm iniciar raid/boss/calamidade` [Opcional: `time-skip`]\n"
                           "`echo adm timeskip` (Pula a espera de 10 min de uma invasão ativa)\n"
                           "`echo adm abencoar_servidor` (Dá Ouro e Tickets para todos no servidor!)\n"
                           "`echo adm hakai @usuário` | `echo adm exilar @usuário` | `echo adm perdoar @usuário`\n"
                           "`echo adm pay @usuário <quant>` | `echo adm gems @usuário <quant>` | `echo adm tickets @usuário <quant>`\n"
                           "`echo adm criarcode <code> <G1000 T3 heroi item>`\n"
                           "`echo adm criarcode temp <dias> <code> <recompensas>`\n"
                           "`echo adm delete code <code>`\n"
                           "`echo adm backup criar|listar` (Backup manual do banco)\n"
                           "`echo adm combate teste` (Laboratório de dano/habilidades contra calamidade nerfada)\n"
                           "`echo adm criar banner` (Editor do banner especial por 7 dias)\n"
                           "`echo adm copa iniciar|encerrar|reset @user|echobet @user <qtd>` (Controle da Echo Cup)\n"
                           "`echo adm melhorar loja` (Sobe a loja em 1 nível para testes)\n"
                           "`echo adm reset cidade` (Reseta Wolford)\n"
                           "`echo adm hack @usuário <id_do_heroi>` (Nível Max + 7 Estrelas)\n"
                           "`echo adm give @usuário <id_heroi_ou_item>` (Dá um herói ou item)\n"
                           "`echo adm deletar item @usuário <item>` (Remove item bugado da mochila)\n"
                           "`echo adm delechar @usuário <nome-do-personagem>` (Apaga uma cópia específica)\n"
                           "`echo adm stats` (Painel geral do jogo)\n"
                           "`echo adm logs [@usuário]` | `echo adm log @usuário <ação> | <valor>`\n"
                           "`echo adm resolver <ID> <mensagem>` | `echo adm reabrir <ID>`\n"
                           "**Cortar Tempos de Espera:**\n"
                           "`echo adm hunt [@usuário]` | `echo adm adventure [@usuário]`\n"
                           "`echo adm work [@usuário]` | `echo adm arena [@usuário]`")
            return

        action = action.lower()
        target_id = re.sub(r'\D', '', arg1) if arg1 else None

        if action == "copa":
            copa_cog = self.bot.get_cog("Copa")
            if not copa_cog or not hasattr(copa_cog, "admin_dispatch"):
                return await ctx.send("O sistema da Echo Cup ainda não carregou.")
            return await copa_cog.admin_dispatch(ctx, arg1, arg2)

        if (
            action in ["criarbanner", "bannercriar"]
            or (
                action in ["criar", "create"]
                and (arg1 or "").lower() in ["banner", "especial"]
            )
        ):
            return await self._open_banner_builder(ctx)

        if action == "stats":
            return await ctx.send(embed=await self._stats_embed(ctx))

        if action == "logs":
            raw_filter = (arg1 or "").lower()
            status_filter = None
            if raw_filter in ["aberto", "abertos", "open"]:
                status_filter = "open"
                target_id = None
            elif raw_filter in ["resolvido", "resolvidos", "resolved"]:
                status_filter = "resolved"
                target_id = None
            return await self._show_admin_logs(ctx, target_id, status_filter)

        if action == "log":
            return await self._manual_admin_log(ctx, target_id, arg2)

        if action in ["resolver", "resolve", "resolvido"]:
            return await self._resolve_admin_log(ctx, arg1, arg2)

        if action in ["reabrir", "reopen"]:
            return await self._reopen_admin_log(ctx, arg1)

        if action in ["delechar", "deletechar", "delchar", "apagarheroi"]:
            return await self._delete_character(ctx, target_id, arg2)

        if action in ["deletaritem", "deleteitem", "delitem", "apagaritem"]:
            return await self._delete_item(ctx, target_id, arg2)

        if action in ["deletar", "delete", "remover", "apagar"] and (arg1 or "").lower() in ["item", "itens"]:
            partes = str(arg2 or "").strip().split(maxsplit=1)
            if not partes:
                return await self._delete_item(ctx, None, None)
            item_target_id = re.sub(r"\D", "", partes[0])
            item_name = partes[1] if len(partes) > 1 else None
            return await self._delete_item(ctx, item_target_id, item_name)

        if action in ["combate", "combat"] and (arg1 or "").lower() in ["teste", "test", "debug"]:
            view = AdminCombatTestSetupView(self, ctx)
            message = await ctx.send(embed=view.build_embed(), view=view)
            view.message = message
            return

        if action in ["combateteste", "combate_teste", "testcombat"]:
            view = AdminCombatTestSetupView(self, ctx)
            message = await ctx.send(embed=view.build_embed(), view=view)
            view.message = message
            return

        if action in ["backup", "dbbackup", "banco"]:
            modo = (arg1 or "listar").lower()
            if modo in ["criar", "create", "forcar", "forçar", "agora", "now"]:
                backups = backup_databases(reason=f"adm_{ctx.author.id}", force=True)
                if not backups:
                    return await ctx.send("Nenhum backup foi criado. TutoriUAU olhou a pasta e ficou desconfiado.")
                linhas = "\n".join(f"`{path.name}`" for path in backups)
                return await ctx.send(f"✅ Backup manual criado:\n{linhas}")

            backups = list_database_backups(limit=10)
            if not backups:
                return await ctx.send("Nenhum backup encontrado ainda. Use `echo adm backup criar` antes de brincar com dinamite.")
            linhas = []
            for path in backups:
                size_kb = max(1, int(path.stat().st_size / 1024))
                when = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(path.stat().st_mtime))
                linhas.append(f"`{path.name}` - {size_kb} KB - {when}")
            return await ctx.send("📦 **Backups recentes do banco:**\n" + "\n".join(linhas[:10]))

        # ================== RAIDS POR SERVIDOR ==================
        if action in ["set_iniciar", "set_invasao", "setcanal"]:
            if not ctx.guild:
                return await ctx.send("❌ Este comando deve ser usado dentro de um servidor.")
                
            canal = ctx.message.channel_mentions[0] if ctx.message.channel_mentions else ctx.channel
            
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id TEXT PRIMARY KEY,
                raid_channel_id TEXT
            )
            """)
            cursor.execute("PRAGMA table_info(server_config)")
            colunas_config = {row[1] for row in cursor.fetchall()}
            if "guild_id" not in colunas_config:
                cursor.execute("ALTER TABLE server_config ADD COLUMN guild_id TEXT")
            if "raid_channel_id" not in colunas_config:
                cursor.execute("ALTER TABLE server_config ADD COLUMN raid_channel_id TEXT")
            
            cursor.execute("DELETE FROM server_config WHERE guild_id = ?", (str(ctx.guild.id),))
            cursor.execute(
                "INSERT OR REPLACE INTO server_config (guild_id, raid_channel_id) VALUES (?, ?)",
                (str(ctx.guild.id), str(canal.id)),
            )
            conn.commit()
            conn.close()
            
            await ctx.send(f"📢 **Canal de Invasões Definido!**\nAs Raids e Calamidades neste servidor acontecerão em {canal.mention}.")

        elif action == "abencoar_servidor":
            if not ctx.guild:
                return await ctx.send("❌ Use em um servidor para abençoar a plebe.")
            
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            
            membros_ids = [str(m.id) for m in ctx.guild.members if not m.bot]
            if not membros_ids:
                return await ctx.send("Nenhum mortal encontrado.")
                
            placeholders = ','.join('?' for _ in membros_ids)
            
            cursor.execute(f"UPDATE players SET gold = gold + 2000 WHERE user_id IN ({placeholders})", membros_ids)
            cursor.execute(f"UPDATE summon_data SET summon_tickets = summon_tickets + 3 WHERE user_id IN ({placeholders})", membros_ids)
            
            conn.commit()
            conn.close()
            
            await ctx.send("✨ **BENÇÃO DIVINA!** Os deuses sorriram para este servidor.\nTodos os mortais receberam **2000 Gold** e **3 Tickets de Invocação**!")

        # ================== COOLDOWNS ==================
        elif action in ["hunt", "adventure", "arena"]:
            alvo = target_id if target_id else str(ctx.author.id)
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE players SET last_{action} = 0 WHERE user_id = ?", (alvo,))
            conn.commit()
            conn.close()
            await ctx.send(f"⏳ O tempo de espera de **{action.upper()}** foi cortado para <@{alvo}>! Pode jogar novamente.")

        elif action == "work":
            alvo = target_id if target_id else str(ctx.author.id)
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_quests WHERE user_id = ?", (alvo,))
            conn.commit()
            conn.close()
            await ctx.send(f"📜 As missões diárias (Work) foram resetadas para <@{alvo}>! O TutoriUAU já tem novos contratos.")

        # ================== INICIAR RAID ==================
        elif action == "iniciar":
            if not ctx.guild:
                return await ctx.send("❌ Use este comando dentro de um servidor.")

            tipo_map = {
                "raid": "raid",
                "boss": "boss",
                "calamidade": "calamidade",
                "diaria": "raid",
                "diária": "raid",
                "semanal": "boss",
                "mensal": "calamidade",
                "chefe": "boss",
            }
            tipo_raid = tipo_map.get((arg1 or "").lower())
            if not tipo_raid:
                return await ctx.send("⚠ Uso correto: `echo adm iniciar <raid | boss | calamidade> [time-skip]`")

            skip_arg = (arg2 or "").lower().replace("_", "-").replace(" ", "-")
            is_skip = skip_arg in ["time-skip", "timeskip"]
            invasoes_cog = self.bot.get_cog("Invasoes")
            if invasoes_cog and hasattr(invasoes_cog, "iniciar_fase_registro"):
                canal = invasoes_cog.get_raid_channel(ctx.guild.id) or ctx.channel
                duration = 60 if is_skip else 600
                try:
                    await invasoes_cog.iniciar_fase_registro(canal, tipo_raid, is_manual=True, duration=duration)
                except Exception as exc:
                    return await ctx.send(f"❌ Não consegui iniciar a invasão: `{exc}`")
                return await ctx.send(f"✅ Evento **{arg1}** iniciado em {canal.mention}. Registro por **{duration // 60} minuto(s)**.")

            raid_cmd = self.bot.get_command("raid_spawn")
            if not raid_cmd:
                return await ctx.send("❌ O sistema de invasões não está carregado.")

            await ctx.invoke(raid_cmd, tipo=tipo_raid, time_skip=is_skip)

        elif action in ["timeskip", "time-skip"] or arg1 in ["time-skip", "timeskip"]:
            cmd = self.bot.get_command("raid_timeskip")
            if cmd: await ctx.invoke(cmd)

        # ================== PUNIÇÕES ==================
        elif action == "hakai":
            if not target_id: return await ctx.send("⚠ Uso: `echo adm hakai @usuário`")
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            for tabela in ["players", "heroes", "pets", "inventory", "dungeon_progress", "teams", "summon_data"]:
                cursor.execute(f"DELETE FROM {tabela} WHERE user_id = ?", (target_id,))
            conn.commit()
            conn.close()
            await ctx.send(f"💥 **HAKAI!** Todos os registros e a existência de <@{target_id}> foram apagados.")

        elif action == "exilar":
            if not target_id: return await ctx.send("⚠ Uso: `echo adm exilar @usuário`")
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            for tabela in ["players", "heroes", "pets", "inventory", "dungeon_progress", "teams", "summon_data"]:
                cursor.execute(f"DELETE FROM {tabela} WHERE user_id = ?", (target_id,))
            cursor.execute("INSERT OR IGNORE INTO ban_list (user_id) VALUES (?)", (target_id,))
            conn.commit()
            conn.close()
            await ctx.send(f"⛓️ **EXÍLIO DECLARADO!** <@{target_id}> foi banido permanentemente.")

        elif action == "perdoar":
            if not target_id: return await ctx.send("⚠ Uso: `echo adm perdoar @usuário`")
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ban_list WHERE user_id = ?", (target_id,))
            conn.commit()
            conn.close()
            await ctx.send(f"🕊️ **PERDÃO DIVINO!** <@{target_id}> foi removido da lista de exilados.")

        # ================== DAR RECURSOS ==================
        elif action == "pay":
            if not target_id or arg2 is None:
                return await ctx.send("⚠ Uso: `echo adm pay @usuário <quantia>`")
            try: amount = int(arg2)
            except (TypeError, ValueError): return await ctx.send("❌ O valor precisa ser um número!")
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (amount, target_id))
            conn.commit()
            conn.close()
            await ctx.send(f"✅ **{amount} Gold** injetados para <@{target_id}>.")

        elif action == "tickets":
            if not target_id or arg2 is None:
                return await ctx.send("⚠ Uso: `echo adm tickets @usuário <quantia>`")
            try: amount = int(arg2)
            except (TypeError, ValueError): return await ctx.send("❌ O valor precisa ser um número!")
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (amount, target_id))
            conn.commit()
            conn.close()
            await ctx.send(f"🎫 **{amount} Summon Tickets** dados para <@{target_id}>.")

        elif action == "gems":
            if not target_id or arg2 is None:
                return await ctx.send("⚠ Uso: `echo adm gems @usuário <quantia>`")
            try: amount = int(arg2)
            except (TypeError, ValueError): return await ctx.send("❌ O valor precisa ser um número!")
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE players SET gems = gems + ? WHERE user_id = ?", (amount, target_id))
            conn.commit()
            conn.close()
            await ctx.send(f"💎 **{amount} Gems** entregues para <@{target_id}>. TutoriUAU anotou a intervenção divina.")

        elif action == "give":
            if not target_id or not arg2: 
                return await ctx.send("⚠ Uso: `echo adm give @usuário <id_do_heroi_ou_item>`")
            
            codigo_id = arg2.strip().lower().replace(" ", "_")
            
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            
            if codigo_id in HEROES:
                cursor.execute("INSERT INTO heroes (user_id, hero_id, rarity, stars, level, xp) VALUES (?, ?, ?, 1, 1, 0)", (target_id, codigo_id, HEROES[codigo_id].get("raridade", 1)))
                nome_formatado = HEROES[codigo_id].get('nome')
                tipo = "Herói"
            else:
                cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (target_id, codigo_id))
                item_existe = cursor.fetchone()
                if item_existe:
                    cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (item_existe[0],))
                else:
                    cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (target_id, codigo_id))
                
                nome_formatado = EQUIPAMENTOS.get(codigo_id, {}).get("nome", codigo_id.replace("_", " ").title())
                tipo = "Item"

            conn.commit()
            conn.close()
            await ctx.send(f"🎁 **Interferência Divina!** <@{target_id}> recebeu o {tipo} **{nome_formatado}**!")

        elif action == "criarcode":
            if (arg1 or "").lower() == "temp":
                partes = str(arg2 or "").split()
                if len(partes) < 3:
                    return await ctx.send(
                        "⚠ Uso: `echo adm criarcode temp <dias> <CODE> <recompensas>`\n"
                        "Exemplo: `echo adm criarcode temp 10 TUTORICHAN G1000 T3`"
                    )
                dias, codigo = partes[0], partes[1]
                recompensas = " ".join(partes[2:])
                await self._criar_code(ctx, codigo, recompensas, valid_days=dias)
            else:
                await self._criar_code(ctx, arg1, arg2)

        elif action in ["delete", "deletar", "remover"] and (arg1 or "").lower() in ["code", "codigo", "código"]:
            await self._deletar_code(ctx, arg2)

        elif action == "melhorar" and (arg1 or "").lower() == "loja":
            await self._melhorar_loja(ctx)

        # ================== RESET CIDADE E HACK ==================
        elif action == "reset" and arg1 == "cidade":
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE city_stats 
                SET hp = 100000, max_hp = 100000, moral = 100, suprimentos = 0, max_suprimentos = 5000, prosperidade = 0 
                WHERE id = 1
            """)
            if ctx.guild:
                cursor.execute("""
                    INSERT OR IGNORE INTO cidades
                    (guild_id, nome, hp, max_hp, moral, suprimentos, max_suprimentos, prosperidade)
                    VALUES (?, 'Capital de Wolford', 100000, 100000, 100, 0, 5000, 0)
                """, (str(ctx.guild.id),))
                cursor.execute("""
                    UPDATE cidades
                    SET hp = 100000, max_hp = 100000, moral = 100,
                        suprimentos = 0, max_suprimentos = 5000, prosperidade = 0
                    WHERE guild_id = ?
                """, (str(ctx.guild.id),))
            conn.commit()
            conn.close()
            await ctx.send("♻️ **WOLFORD RESETADA!** A muralha voltou ao zero.")

        elif action == "hack":
            if not target_id or not arg2: 
                return await ctx.send("⚠ Uso correto: `echo adm hack @usuário <ID_DO_HEROI_NO_BANCO>`")
            try: hero_db_id = int(arg2)
            except ValueError: return await ctx.send("❌ O ID do herói precisa ser um número.")
            
            conn = sqlite3.connect("players.db")
            cursor = conn.cursor()
            cursor.execute("SELECT hero_id FROM heroes WHERE id = ? AND user_id = ?", (hero_db_id, target_id))
            if not cursor.fetchone():
                conn.close()
                return await ctx.send(f"❌ O herói de ID `{hero_db_id}` não foi encontrado.")
            
            cursor.execute("UPDATE heroes SET level = 100, stars = 7, xp = 10000 WHERE id = ?", (hero_db_id,))
            conn.commit()
            conn.close()
            await ctx.send(f"👾 **HACK ATIVADO!** O herói ID `{hero_db_id}` alcançou o **Nível 100** e **7✦**!")

async def setup(bot):
    await bot.add_cog(Adm(bot))
