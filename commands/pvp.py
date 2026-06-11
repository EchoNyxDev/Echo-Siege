import discord
from discord.ext import commands
import asyncio
import math
import os
import random
import re
import sqlite3
import sys
import time
import unicodedata

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.habilidades import SKILLS
    from data.equipamentos import EQUIPAMENTOS
    from utils.combat import CombatEntity, apply_on_hit_statuses, apply_status_effects, apply_status_protection, choose_combat_skill
    from utils.skills import get_hero_skill_ids
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.equipment import get_equipment_bonus
    from utils.affinity import apply_affinity_bonus
    from utils.player_bonuses import apply_battle_hp_bonus
except ModuleNotFoundError as e:
    print(f"Erro de importacao no PvP: {e}")
    HEROES, SKILLS, EQUIPAMENTOS = {}, {}, {}
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []
    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}
    def apply_affinity_bonus(party_data, heroes):
        return party_data
    def apply_battle_hp_bonus(cursor, user_id, party_data):
        return party_data
    def apply_status_effects(actor, target, effect, damage_dealt=0, critical=False):
        return []
    def apply_status_protection(target, effect, turns=3):
        return []
    def apply_on_hit_statuses(actor, target, critical=False):
        return []
    def choose_combat_skill(actor, skills=None, allies=None, enemies=None):
        available = [skill_id for skill_id in actor.habilidades if skill_id in (skills or {}) and skill_id not in actor.cooldowns]
        return random.choice(available) if available else None
    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {"hp": 100, "atk": 10, "matk": 10, "def": 5, "spd": 10, "crt": 5, "level": level}
    def normalize_class(value):
        return str(value or "neutro").lower()


def _cortar_texto(texto, limite=1024):
    if len(texto) <= limite:
        return texto
    return texto[:limite - 3] + "..."


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower()


def _normalizar_id(texto):
    texto = _normalizar(texto)
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


SKILL_NAME_TO_ID = {}
for _skill_id, _skill_data in SKILLS.items():
    SKILL_NAME_TO_ID[_normalizar_id(_skill_id)] = _skill_id
    SKILL_NAME_TO_ID[_normalizar_id(_skill_data.get("nome", _skill_id))] = _skill_id


ONLINE_PVP_BOTS = [
    ("Sentinela de Felt", 80, 101),
    ("Escudeiro de Crusch", 100, 202),
    ("Discípulo de Wilhelm", 120, 303),
    ("Maga da Biblioteca", 145, 404),
    ("Cavaleiro do Gelo", 170, 505),
    ("Caçadora Carmesim", 200, 606),
    ("Arauto de Lugnica", 235, 707),
    ("Mercenário do Abismo", 275, 808),
    ("Guardião de Nazarick", 320, 909),
    ("Espadachim Sem Nome", 370, 1010),
    ("Oráculo da Torre", 430, 1111),
    ("Eco do Fim", 500, 1212),
]


class OnlinePvpBot:
    def __init__(self, name, rating, seed):
        self.id = -(seed + 10_000)
        self.name = name
        self.display_name = name
        self.mention = f"**{name} [BOT]**"
        self.rating = int(rating)
        self.seed = seed
        self.bot = True


class PvpAcceptView(discord.ui.View):
    def __init__(self, challenger: discord.User, challenged: discord.User, cog_ref):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.challenged = challenged
        self.cog = cog_ref

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.challenged.id:
            await interaction.response.send_message("Apenas o desafiado pode aceitar ou recusar!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aceitar Duelo", style=discord.ButtonStyle.danger)
    async def btn_accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content=f"{self.challenged.mention} aceitou o duelo. Preparando a arena...",
            view=None,
            embed=None
        )
        await self.cog.executar_pvp(interaction.channel, self.challenger, self.challenged)

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.secondary)
    async def btn_decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content=f"{self.challenged.mention} recusou o duelo.",
            view=None,
            embed=None
        )


class PvpBattleView(discord.ui.View):
    def __init__(self, cog, channel, p1, p2, team_p1, team_p2, online=False):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel = channel
        self.p1 = p1
        self.p2 = p2
        self.online = online
        self.team_a = [CombatEntity(f"A{i}", d["nome"], d, False) for i, d in enumerate(team_p1)]
        self.team_b = [CombatEntity(f"B{i}", d["nome"], d, True) for i, d in enumerate(team_p2)]
        self.owner_by_side = {"A": p1.id, "B": p2.id}
        self.turn_queue = []
        self.current_actor = None
        self.message = None
        self.messages = []
        self.public_messages = []
        self.log_display = ["O duelo começou. A ordem dos turnos segue a velocidade dos heróis."]
        self.finalizado = False
        self.action_lock = asyncio.Lock()
        self.timeout_task = asyncio.create_task(self._timeout_after_inactivity())

    async def _timeout_after_inactivity(self):
        try:
            await asyncio.sleep(900)
        except asyncio.CancelledError:
            return
        await self.on_timeout()

    def _cancel_timeout(self):
        task = self.timeout_task
        self.timeout_task = None
        if task and not task.done() and task is not asyncio.current_task():
            task.cancel()

    def _restart_timeout(self):
        self._cancel_timeout()
        if not self.finalizado:
            self.timeout_task = asyncio.create_task(self._timeout_after_inactivity())

    def abort(self):
        self.finalizado = True
        self._cancel_timeout()

    def add_message(self, message):
        if message and all(existing.id != message.id for existing in self.messages):
            self.messages.append(message)
        if not self.message:
            self.message = message

    def add_public_message(self, message):
        if message and all(existing.id != message.id for existing in self.public_messages):
            self.public_messages.append(message)

    def _get_alive(self, team):
        return [e for e in team if not e.is_dead]

    def _team_do_actor(self, actor):
        return self.team_b if actor.is_enemy else self.team_a

    def _inimigos_do_actor(self, actor):
        return self.team_a if actor.is_enemy else self.team_b

    def _owner_do_actor(self, actor):
        return self.owner_by_side["B" if actor.is_enemy else "A"]

    def _get_target_aggro(self, vivos):
        total_aggro = sum(e.get_aggro() for e in vivos)
        roll = random.uniform(0, total_aggro)
        acumulado = 0
        for e in vivos:
            acumulado += e.get_aggro()
            if roll <= acumulado:
                return e
        return vivos[0]

    def _gerar_timeline(self):
        todos_vivos = self._get_alive(self.team_a) + self._get_alive(self.team_b)
        fila = [e for e in self.turn_queue if not e.is_dead]

        if len(fila) < 5:
            for e in sorted(todos_vivos, key=lambda x: (x.get_stat("spd"), 0 if x.is_enemy else 1), reverse=True):
                if not e.is_dead:
                    fila.append(e)
                if len(fila) >= 5:
                    break

        return " -> ".join(e.clean_name for e in fila[:5]) or "Sem turnos"

    def _barra_time(self, team):
        linhas = []
        for e in team:
            estado = "KO" if e.is_dead else f"{e.hp}/{e.max_hp}"
            status = f" | {e.status_text()}" if not e.is_dead and e.status_text() else ""
            linhas.append(f"{e.clean_name}: **{estado}**{status}")
        return "\n".join(linhas) or "Sem equipe"

    def _build_controls(self):
        controls = PvpMirrorView(self)
        controls.add_item(PvpAttackButton(self))

        available_skills = [
            skill_id
            for skill_id in (self.current_actor.habilidades if self.current_actor else [])
            if skill_id in SKILLS and skill_id not in self.current_actor.cooldowns
        ]
        has_skill = bool(available_skills)
        disabled_skill = True
        skill_label = "Habilidade"
        if len(available_skills) == 1:
            disabled_skill = False
            skill_label = SKILLS[available_skills[0]].get("nome", "Habilidade")
        elif len(available_skills) > 1:
            disabled_skill = False
            skill_label = f"Habilidade ({len(available_skills)} opções)"

        controls.add_item(PvpSkillButton(self, _cortar_texto(skill_label, 80), disabled_skill))
        controls.add_item(PvpDefendButton(self))
        controls.add_item(PvpSurrenderButton(self))
        return controls

    async def _atualizar_mensagem(self, interaction=None):
        self._restart_timeout()
        dono = self.p2 if self.current_actor and self.current_actor.is_enemy else self.p1
        embed = discord.Embed(
            title="Duelo PvP em Turnos",
            description=f"Turno de {dono.mention}: **{self.current_actor.clean_name}**",
            color=discord.Color.dark_red()
        )
        embed.add_field(name=self.p1.display_name, value=_cortar_texto(self._barra_time(self.team_a)), inline=True)
        embed.add_field(name=self.p2.display_name, value=_cortar_texto(self._barra_time(self.team_b)), inline=True)
        embed.add_field(name="Fila de ação", value=_cortar_texto(self._gerar_timeline()), inline=False)
        embed.add_field(name="Acontecimentos", value=f"```{_cortar_texto(chr(10).join(self.log_display[-7:]), 1000)}```", inline=False)
        embed.set_footer(text="Somente o dono do herói do turno consegue clicar.")
        interaction_message_id = None
        if interaction:
            interaction_message_id = interaction.message.id
            try:
                await interaction.response.edit_message(embed=embed, view=self._build_controls())
            except discord.errors.InteractionResponded:
                await interaction.message.edit(embed=embed, view=self._build_controls())
        for message in list(self.messages):
            if message.id == interaction_message_id:
                continue
            try:
                await message.edit(content=None, embed=embed, view=self._build_controls())
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                self.messages.remove(message)
        if not self.messages and self.channel:
            message = await self.channel.send(embed=embed, view=self._build_controls())
            self.add_message(message)

    def _buscar_alvos(self, actor, alvo_req):
        time_aliado = self._team_do_actor(actor)
        inimigos = self._get_alive(self._inimigos_do_actor(actor))
        aliados = self._get_alive(time_aliado)
        aliados_mortos = [a for a in time_aliado if a.is_dead]

        if not inimigos and ("inimigo" in alvo_req or "campo" in alvo_req):
            return []
        if not aliados and ("aliado" in alvo_req or alvo_req == "self"):
            return []

        if alvo_req == "self":
            return [actor]
        if alvo_req == "aliado_morto":
            return aliados_mortos[:1]
        if alvo_req == "aliados_mortos":
            return aliados_mortos
        if alvo_req == "unico_inimigo":
            return [self._get_target_aggro(inimigos)]
        if alvo_req == "todos_inimigos" or "campo" in alvo_req:
            return inimigos
        if alvo_req == "unico_aliado":
            return [random.choice(aliados)]
        if alvo_req == "aliado_menor_hp":
            return [min(aliados, key=lambda x: x.hp / x.max_hp)]
        if alvo_req == "todos_aliados":
            return aliados
        if alvo_req == "dps_aliado":
            return [max(aliados, key=lambda x: x.get_stat("atk") + x.get_stat("matk"))]
        if "aliado" in alvo_req:
            return [random.choice(aliados)]
        if "inimigo" in alvo_req:
            return [self._get_target_aggro(inimigos)]
        if "aleatorio" in alvo_req:
            return [random.choice(inimigos)]
        return [self._get_target_aggro(inimigos)]

    def _executar_habilidade(self, actor, skill_id):
        if actor.is_silenced():
            return f"{actor.clean_name} está silenciado e atacou normalmente. " + self._ataque_basico(actor)

        s_data = SKILLS.get(skill_id)
        if not s_data:
            return self._ataque_basico(actor)

        if "cooldown" in s_data:
            actor.cooldowns[skill_id] = s_data["cooldown"]

        tipo = s_data.get("tipo", "dano")
        efeito = s_data.get("efeito", {})
        targets = self._buscar_alvos(actor, s_data.get("alvo", "unico_inimigo"))
        if not targets:
            return f"{actor.clean_name} tentou agir, mas não encontrou alvo."

        log_line = f"{actor.clean_name} usou [{s_data.get('nome', skill_id)}]!"
        total_dmg = 0
        total_heal = 0
        mortos = []
        stunned = []

        for target in targets:
            if tipo in ["dano", "insta_kill", "especial"] and target.is_enemy != actor.is_enemy:
                is_magic = "matk" in str(efeito)
                base = actor.get_stat("matk") if is_magic else actor.get_stat("atk")
                dano = base + efeito.get("dano_atk_extra", 0) + efeito.get("dano_matk_extra", 0)
                mult = efeito.get("multiplicador_hit", 1) * efeito.get("multiplicador_atk", 1.0) * efeito.get("multiplicador_matk", 1.0)
                if efeito.get("dano_massivo"):
                    mult *= 2.5
                if efeito.get("multiplica_atk_matk"):
                    mult *= efeito.get("multiplica_atk_matk")
                if random.randint(1, 100) <= actor.get_stat("crt") or efeito.get("critico_garantido", False):
                    mult *= 1.5

                dano_final = actor.cap_outgoing_damage(dano * mult, is_skill=True)
                dealt = target.take_damage(dano_final, base, is_magic=is_magic, ignore_def=efeito.get("ignora_def", False))
                total_dmg += dealt

                statuses = apply_status_effects(actor, target, efeito, dealt)
                statuses.extend(apply_on_hit_statuses(actor, target))
                if any(status in {"stun", "freeze", "root"} for status in statuses):
                    stunned.append(target.clean_name)
                if ("chance_insta_kill" in efeito and random.random() <= efeito["chance_insta_kill"]) or efeito.get("insta_kill_on_hit_garantido"):
                    if not target.is_dead:
                        target.hp = 0
                        target.is_dead = True
                if target.is_dead:
                    mortos.append(target.clean_name)

            if tipo in ["cura", "reviver", "especial"] and target.is_enemy == actor.is_enemy:
                if target.is_dead and (tipo == "reviver" or "reviver_aliado" in str(efeito)):
                    target.is_dead = False
                    target.hp = int(target.max_hp * efeito.get("hp_percent", 0.5))
                    total_heal += target.hp
                elif not target.is_dead:
                    cura = efeito.get("cura_fixa", 0)
                    if "cura_percent_max" in efeito:
                        cura += int(target.max_hp * efeito["cura_percent_max"])
                    if "multiplicador_matk" in efeito:
                        cura += int(actor.get_stat("matk") * efeito["multiplicador_matk"])
                    if cura == 0 and tipo == "cura":
                        cura = int(actor.get_stat("matk") * 0.5)
                    total_heal += target.heal(cura)
                apply_status_protection(target, efeito, efeito.get("turnos", 3))

            if tipo in ["buff", "escudo", "passiva", "especial"] and not target.is_dead:
                turnos = efeito.get("turnos", 3)
                if efeito.get("duracao") == "combate_inteiro":
                    turnos = 99
                if "buff_atk" in efeito:
                    target.buffs.append({"stat": "atk", "mult": efeito["buff_atk"] / 100.0, "turnos": turnos})
                if "buff_matk" in efeito:
                    target.buffs.append({"stat": "matk", "mult": efeito["buff_matk"] / 100.0, "turnos": turnos})
                if "buff_def" in efeito:
                    target.buffs.append({"stat": "def", "mult": efeito["buff_def"] / 100.0, "turnos": turnos})
                if "buff_spd" in efeito:
                    target.buffs.append({"stat": "spd", "mult": efeito["buff_spd"] / 100.0, "turnos": turnos})
                if "buff_crt" in efeito:
                    target.buffs.append({"stat": "crt", "flat": efeito["buff_crt"], "turnos": turnos})
                if "imortalidade_turnos" in efeito:
                    target.buffs.append({"stat": "imortal", "imortal": True, "turnos": efeito["imortalidade_turnos"]})
                if "imunidade_dano_turnos" in efeito or "ignora_dano_fisico" in efeito:
                    target.buffs.append({"stat": "imune", "imune_all": True, "turnos": turnos})
                apply_status_protection(target, efeito, turnos)

            if tipo in ["debuff", "especial"] and target.is_enemy != actor.is_enemy and not target.is_dead:
                turnos = efeito.get("turnos", 2)
                if "debuff_def" in efeito:
                    target.debuffs.append({"stat": "def", "mult": efeito["debuff_def"] / 100.0, "turnos": turnos})
                apply_status_effects(actor, target, efeito)

        if total_dmg:
            log_line += f" Causou {total_dmg} de dano total."
        if total_heal:
            log_line += f" Recuperou {total_heal} HP total."
        if stunned:
            log_line += f" Atordoou: {', '.join(stunned)}."
        if mortos:
            log_line += f" Caiu: {', '.join(mortos)}."
        return log_line

    def _ataque_basico(self, actor):
        inimigos = self._get_alive(self._inimigos_do_actor(actor))
        if not inimigos:
            return ""

        target = self._get_target_aggro(inimigos)
        is_crit = random.randint(1, 100) <= actor.get_stat("crt")
        dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
        dealt = target.take_damage(dmg, actor.get_stat("atk"))
        apply_on_hit_statuses(actor, target, is_crit)
        crit = " CRITICO" if is_crit else ""
        log = f"{actor.clean_name} atacou {target.clean_name} por {dealt}{crit}."
        if target.is_dead:
            log += f" {target.clean_name} caiu."
        return log

    async def processar_fila(self, interaction=None):
        while not self.finalizado:
            vivos_a = self._get_alive(self.team_a)
            vivos_b = self._get_alive(self.team_b)

            if not vivos_a:
                return await self.finalizar(self.p2, self.p1, interaction)
            if not vivos_b:
                return await self.finalizar(self.p1, self.p2, interaction)

            all_alive = vivos_a + vivos_b
            self.turn_queue = [e for e in self.turn_queue if not e.is_dead]
            if not self.turn_queue:
                self.turn_queue = sorted(all_alive, key=lambda x: (x.get_stat("spd"), 0 if x.is_enemy else 1), reverse=True)

            actor = self.turn_queue.pop(0)
            estava_atordoado = actor.is_stunned()
            dot_logs = actor.tick_effects()
            self.log_display.extend(dot_logs)

            if actor.is_dead:
                continue
            if estava_atordoado:
                self.log_display.append(f"{actor.clean_name} esta atordoado e perdeu a vez.")
                continue

            self.current_actor = actor
            owner = self.p2 if actor.is_enemy else self.p1
            if getattr(owner, "bot", False):
                skill_id = choose_combat_skill(
                    actor,
                    SKILLS,
                    self._team_do_actor(actor),
                    self._inimigos_do_actor(actor),
                )
                if skill_id and not actor.is_silenced():
                    self.log_display.append(self._executar_habilidade(actor, skill_id))
                else:
                    self.log_display.append(self._ataque_basico(actor))
                continue

            await self._atualizar_mensagem(interaction)
            return

    async def finalizar(self, vencedor, perdedor, interaction=None, motivo="vitoria"):
        if self.finalizado:
            return
        self.finalizado = True
        self._cancel_timeout()
        self.clear_items()
        if self.online:
            self.cog._finish_online_users(self.p1, self.p2)

        if getattr(self.p1, "bot", False) or getattr(self.p2, "bot", False):
            human = self.p2 if getattr(self.p1, "bot", False) else self.p1
            bot = self.p1 if getattr(self.p1, "bot", False) else self.p2
            elo = self.cog.atualizar_elo_bot(human.id, vencedor.id == human.id, bot.rating)
        else:
            elo = self.cog.atualizar_elo(vencedor.id, perdedor.id)
        winner_change = f"{elo['winner_change']:+d}"
        loser_change = f"{elo['loser_change']:+d}"
        placement_note = ""
        if elo["winner_placement"] or elo["loser_placement"]:
            placement_note = "\n\n*Primeira partida detectada: a colocação começa na base 100 antes do resultado.*"
        titulo = "Vitória no PvP" if motivo == "vitoria" else "Desistência no PvP"
        embed = discord.Embed(
            title=titulo,
            description=(
                f"{vencedor.mention} venceu {perdedor.mention}.\n\n"
                f"**Vencedor:** {elo['winner_old']} -> {elo['winner_new']} ({winner_change})\n"
                f"**Perdedor:** {elo['loser_old']} -> {elo['loser_new']} ({loser_change})"
                f"{placement_note}"
            ),
            color=discord.Color.gold()
        )
        embed.add_field(name="Últimos acontecimentos", value=f"```{_cortar_texto(chr(10).join(self.log_display[-8:]), 1000)}```", inline=False)

        interaction_message_id = None
        if interaction:
            interaction_message_id = interaction.message.id
            try:
                await interaction.response.edit_message(embed=embed, view=None)
            except discord.errors.InteractionResponded:
                await interaction.message.edit(embed=embed, view=None)
        for message in list(self.messages):
            if message.id == interaction_message_id:
                continue
            try:
                await message.edit(content=None, embed=embed, view=None)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        for message in list(self.public_messages):
            try:
                await message.edit(content=None, embed=embed, view=None)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        if not self.messages and self.channel:
            await self.channel.send(embed=embed)

    async def on_timeout(self):
        if self.finalizado:
            return
        self.finalizado = True
        self._cancel_timeout()
        self.clear_items()
        if self.online:
            self.cog._finish_online_users(self.p1, self.p2)
        for message in list(self.messages):
            try:
                await message.edit(
                    content="Duelo encerrado por inatividade. Sem alteração de ELO.",
                    embed=None,
                    view=None,
                )
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        for message in list(self.public_messages):
            try:
                await message.edit(
                    content="Duelo PvP Online encerrado por inatividade. Sem alteração de ELO.",
                    embed=None,
                    view=None,
                )
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass


class PvpActionButton(discord.ui.Button):
    def __init__(self, battle_view, **kwargs):
        super().__init__(**kwargs)
        self.view_ref = battle_view

    async def _validar_turno(self, interaction):
        if self.view_ref.finalizado:
            await interaction.response.send_message("Este duelo já terminou.", ephemeral=True)
            return False
        actor = self.view_ref.current_actor
        if not actor:
            await interaction.response.send_message("O duelo ainda não está pronto.", ephemeral=True)
            return False
        if interaction.user.id != self.view_ref._owner_do_actor(actor):
            await interaction.response.send_message("Não é o seu turno.", ephemeral=True)
            return False
        return True


class PvpAttackButton(PvpActionButton):
    def __init__(self, battle_view):
        super().__init__(battle_view, style=discord.ButtonStyle.danger, label="Atacar")

    async def callback(self, interaction):
        if self.view_ref.action_lock.locked():
            return await interaction.response.send_message("A ação anterior ainda está sendo processada.", ephemeral=True)
        async with self.view_ref.action_lock:
            if not await self._validar_turno(interaction):
                return
            actor = self.view_ref.current_actor
            self.view_ref.log_display.append(self.view_ref._ataque_basico(actor))
            await self.view_ref.processar_fila(interaction)


class PvpSkillButton(PvpActionButton):
    def __init__(self, battle_view, label, disabled):
        super().__init__(battle_view, style=discord.ButtonStyle.primary, label=label, disabled=disabled)

    async def callback(self, interaction):
        if self.view_ref.action_lock.locked():
            return await interaction.response.send_message("A ação anterior ainda está sendo processada.", ephemeral=True)
        async with self.view_ref.action_lock:
            if not await self._validar_turno(interaction):
                return
            actor = self.view_ref.current_actor
            skill_id = choose_combat_skill(
                actor,
                SKILLS,
                self.view_ref._team_do_actor(actor),
                self.view_ref._inimigos_do_actor(actor),
            )
            if not skill_id:
                return await interaction.response.send_message(
                    "Todas as habilidades deste herói estão em recarga.",
                    ephemeral=True,
                )
            self.view_ref.log_display.append(self.view_ref._executar_habilidade(actor, skill_id))
            await self.view_ref.processar_fila(interaction)


class PvpDefendButton(PvpActionButton):
    def __init__(self, battle_view):
        super().__init__(battle_view, style=discord.ButtonStyle.secondary, label="Defender")

    async def callback(self, interaction):
        if self.view_ref.action_lock.locked():
            return await interaction.response.send_message("A ação anterior ainda está sendo processada.", ephemeral=True)
        async with self.view_ref.action_lock:
            if not await self._validar_turno(interaction):
                return
            actor = self.view_ref.current_actor
            actor.buffs.append({"stat": "def", "mult": 0.5, "turnos": 1})
            cura = actor.heal(int(actor.max_hp * 0.08))
            self.view_ref.log_display.append(f"{actor.clean_name} defendeu e recuperou {cura} HP.")
            await self.view_ref.processar_fila(interaction)


class PvpSurrenderButton(PvpActionButton):
    def __init__(self, battle_view):
        super().__init__(battle_view, style=discord.ButtonStyle.secondary, label="Desistir")

    async def callback(self, interaction):
        if self.view_ref.action_lock.locked():
            return await interaction.response.send_message("A ação anterior ainda está sendo processada.", ephemeral=True)
        async with self.view_ref.action_lock:
            if not await self._validar_turno(interaction):
                return
            perdedor = self.view_ref.p2 if self.view_ref.current_actor.is_enemy else self.view_ref.p1
            vencedor = self.view_ref.p1 if self.view_ref.current_actor.is_enemy else self.view_ref.p2
            await self.view_ref.finalizar(vencedor, perdedor, interaction, motivo="desistencia")


class PvpMirrorView(discord.ui.View):
    """Uma interface por mensagem, todas apontando para a mesma batalha."""

    def __init__(self, battle_view):
        super().__init__(timeout=None)
        self.battle_view = battle_view


class PvP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.online_queue = {}
        self.online_tasks = {}
        self.active_online_users = set()
        self._init_db()

    def cog_unload(self):
        for task in self.online_tasks.values():
            task.cancel()
        self.online_tasks.clear()
        self.online_queue.clear()
        self.active_online_users.clear()

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(players)")
        colunas = [info[1] for info in cursor.fetchall()]

        if "pvp_wins" not in colunas:
            cursor.execute("ALTER TABLE players ADD COLUMN pvp_wins INTEGER DEFAULT 0")
        if "pvp_losses" not in colunas:
            cursor.execute("ALTER TABLE players ADD COLUMN pvp_losses INTEGER DEFAULT 0")
        if "pvp_rating" not in colunas:
            cursor.execute("ALTER TABLE players ADD COLUMN pvp_rating INTEGER DEFAULT 0")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings(
                key TEXT PRIMARY KEY,
                value TEXT DEFAULT ''
            )
        """)
        cursor.execute("SELECT value FROM bot_settings WHERE key = 'pvp_seed_100_v2'")
        if not cursor.fetchone():
            cursor.execute("""
                UPDATE players
                SET pvp_rating = 100
                WHERE COALESCE(pvp_wins, 0) + COALESCE(pvp_losses, 0) > 0
            """)
            cursor.execute("""
                UPDATE players
                SET pvp_rating = 0
                WHERE COALESCE(pvp_wins, 0) + COALESCE(pvp_losses, 0) = 0
            """)
            cursor.execute("INSERT INTO bot_settings (key, value) VALUES ('pvp_seed_100_v2', 'done')")

        cursor.execute("""
            UPDATE players
            SET pvp_rating = 0
            WHERE COALESCE(pvp_wins, 0) = 0
              AND COALESCE(pvp_losses, 0) = 0
              AND COALESCE(pvp_rating, 0) = 1000
        """)

        conn.commit()
        conn.close()

    def _hero_columns(self, cursor):
        cursor.execute("PRAGMA table_info(heroes)")
        return {info[1] for info in cursor.fetchall()}

    def _resolver_habilidade(self, habilidade):
        if isinstance(habilidade, dict):
            candidato = habilidade.get("id") or habilidade.get("nome")
        else:
            candidato = habilidade

        if not candidato:
            return None

        candidato_id = _normalizar_id(str(candidato))
        return SKILL_NAME_TO_ID.get(candidato_id, candidato_id)

    def puxar_party_para_combate(self, user_id, user_name):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        hero_cols = self._hero_columns(cursor)

        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
        p_data = cursor.fetchone()
        if not p_data or not p_data[0]:
            conn.close()
            return None

        cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
        team = cursor.fetchone()
        time_ids = [p_data[0]] + [x for x in (team if team else []) if x is not None]
        party_data = []

        select_cols = "hero_id, stars, level"
        if {"equip_atk", "equip_def", "equip_livre"}.issubset(hero_cols):
            select_cols += ", equip_atk, equip_def, equip_livre"

        for hid in time_ids:
            cursor.execute(f"SELECT {select_cols} FROM heroes WHERE id = ?", (int(hid),))
            hero = cursor.fetchone()
            if not hero:
                continue

            h_id, stars, level = hero[:3]
            equips = hero[3:] if len(hero) > 3 else []
            h_data = HEROES.get(h_id, {})

            equipment_bonuses = []
            for eq_name in equips:
                if eq_name and eq_name in EQUIPAMENTOS:
                    equipment_bonuses.append(get_equipment_bonus(cursor, user_id, eq_name, EQUIPAMENTOS))

            stats = calculate_hero_stats(h_data, stars, level, equipment_bonuses)
            hp, atk, matk = stats["hp"], stats["atk"], stats["matk"]
            df, spd, crt = stats["def"], stats["spd"], stats["crt"]
            cl_norm = normalize_class(h_data.get("classe", "neutro"))

            skill_ids = get_hero_skill_ids(h_data, stars, h_data.get("raridade", 0))
            party_data.append({
                "id": str(hid),
                "hero_id": h_id,
                "nome": f"{h_data.get('nome', 'Herói')} ({user_name})",
                "classe": cl_norm,
                "level": level,
                "hp": hp,
                "atk": atk,
                "matk": matk,
                "def": df,
                "spd": spd,
                "crt": crt,
                "stats": {"hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt, "level": level},
                "habilidades": skill_ids
            })

        party_data = apply_affinity_bonus(party_data, HEROES)
        party_data = apply_battle_hp_bonus(cursor, user_id, party_data)
        conn.commit()
        conn.close()
        return party_data

    def atualizar_elo(self, vencedor_id, perdedor_id):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT pvp_rating, pvp_wins, pvp_losses FROM players WHERE user_id = ?", (str(vencedor_id),))
        winner_row = cursor.fetchone() or (0, 0, 0)
        cursor.execute("SELECT pvp_rating, pvp_wins, pvp_losses FROM players WHERE user_id = ?", (str(perdedor_id),))
        loser_row = cursor.fetchone() or (0, 0, 0)

        winner_old = int(winner_row[0] or 0)
        loser_old = int(loser_row[0] or 0)
        winner_first_match = int(winner_row[1] or 0) + int(winner_row[2] or 0) == 0
        loser_first_match = int(loser_row[1] or 0) + int(loser_row[2] or 0) == 0
        winner_base = 100 if winner_first_match else winner_old
        loser_base = 100 if loser_first_match else loser_old

        expected_winner = 1 / (1 + math.pow(10, (loser_base - winner_base) / 400))
        delta = round(24 * (1 - expected_winner))
        delta = max(6, min(24, delta))

        winner_new = winner_base + delta
        loser_floor = 100 if loser_first_match else 0
        loser_new = max(loser_floor, loser_base - delta)

        cursor.execute(
            "UPDATE players SET pvp_wins = pvp_wins + 1, pvp_rating = ? WHERE user_id = ?",
            (winner_new, str(vencedor_id))
        )
        cursor.execute(
            "UPDATE players SET pvp_losses = pvp_losses + 1, pvp_rating = ? WHERE user_id = ?",
            (loser_new, str(perdedor_id))
        )
        conn.commit()
        conn.close()

        return {
            "winner_old": winner_old,
            "winner_new": winner_new,
            "loser_old": loser_old,
            "loser_new": loser_new,
            "winner_change": winner_new - winner_old,
            "loser_change": loser_new - loser_old,
            "winner_placement": winner_first_match,
            "loser_placement": loser_first_match,
            "delta": delta,
        }

    def atualizar_elo_bot(self, user_id, venceu, bot_rating):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pvp_rating, pvp_wins, pvp_losses FROM players WHERE user_id = ?",
            (str(user_id),),
        )
        row = cursor.fetchone() or (0, 0, 0)
        human_old = int(row[0] or 0)
        first_match = int(row[1] or 0) + int(row[2] or 0) == 0
        human_base = 100 if first_match else human_old
        expected = 1 / (1 + math.pow(10, (int(bot_rating) - human_base) / 400))
        raw_delta = round(24 * ((1 if venceu else 0) - expected))
        delta = max(6, min(24, abs(raw_delta)))
        if venceu:
            human_new = human_base + abs(delta)
            cursor.execute(
                "UPDATE players SET pvp_wins = pvp_wins + 1, pvp_rating = ? WHERE user_id = ?",
                (human_new, str(user_id)),
            )
            result = {
                "winner_old": human_old,
                "winner_new": human_new,
                "loser_old": int(bot_rating),
                "loser_new": int(bot_rating),
                "winner_change": human_new - human_old,
                "loser_change": 0,
            }
        else:
            floor = 100 if first_match else 0
            human_new = max(floor, human_base - abs(delta))
            cursor.execute(
                "UPDATE players SET pvp_losses = pvp_losses + 1, pvp_rating = ? WHERE user_id = ?",
                (human_new, str(user_id)),
            )
            result = {
                "winner_old": int(bot_rating),
                "winner_new": int(bot_rating),
                "loser_old": human_old,
                "loser_new": human_new,
                "winner_change": 0,
                "loser_change": human_new - human_old,
            }
        conn.commit()
        conn.close()
        result.update({
            "winner_placement": first_match,
            "loser_placement": first_match,
            "delta": abs(delta),
        })
        return result

    def _player_rating(self, user_id):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pvp_rating FROM players WHERE user_id = ?",
            (str(user_id),),
        )
        row = cursor.fetchone()
        conn.close()
        return int(row[0] or 0) if row else 0

    def _closest_bot(self, rating):
        name, bot_rating, seed = min(
            ONLINE_PVP_BOTS,
            key=lambda profile: abs(profile[1] - max(100, int(rating or 0))),
        )
        return OnlinePvpBot(name, bot_rating, seed)

    def _build_bot_party(self, bot, reference_party):
        pool = [hero_id for hero_id in HEROES if hero_id != "id-nome"]
        if not pool or not reference_party:
            return []
        rng = random.Random(bot.seed + int(bot.rating))
        selected = rng.sample(pool, min(len(reference_party), 5, len(pool)))
        party = []
        for index, hero_id in enumerate(selected):
            template = reference_party[index % len(reference_party)]
            hero = HEROES.get(hero_id, {})
            variance = rng.uniform(0.90, 1.08)
            stats = {}
            for stat in ["hp", "atk", "matk", "def", "spd", "crt"]:
                base = int(template.get(stat, template.get("stats", {}).get(stat, 10)) or 10)
                stats[stat] = max(1, int(base * variance))
            skills = get_hero_skill_ids(hero, 3, hero.get("raridade", 1))
            party.append({
                "id": f"bot_{bot.seed}_{index}",
                "hero_id": hero_id,
                "nome": f"{hero.get('nome', hero_id)} ({bot.name})",
                "classe": _normalizar(hero.get("classe", "neutro")),
                "level": max(1, int(template.get("level", 1))),
                **stats,
                "stats": {**stats, "level": max(1, int(template.get("level", 1)))},
                "habilidades": skills,
            })
        return party

    def _cancel_queue_task(self, user_id):
        task = self.online_tasks.pop(int(user_id), None)
        if task and not task.done():
            task.cancel()

    def _remove_from_queue(self, user_id):
        self.online_queue.pop(int(user_id), None)
        self._cancel_queue_task(user_id)

    def _finish_online_users(self, *participants):
        for participant in participants:
            if not getattr(participant, "bot", False):
                self.active_online_users.discard(int(participant.id))

    def _find_online_opponent(self, entry):
        candidates = []
        waited = max(0, time.time() - entry["joined_at"])
        tolerance = min(180, 35 + int(waited * 4))
        for candidate in self.online_queue.values():
            if candidate["user"].id == entry["user"].id:
                continue
            distance = abs(candidate["rating"] - entry["rating"])
            if distance > tolerance:
                continue
            other_server = candidate["guild_id"] != entry["guild_id"]
            candidates.append((0 if other_server else 1, distance, candidate["joined_at"], candidate))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
        return candidates[0][3]

    async def _bot_match_after(self, user_id, delay=15):
        try:
            await asyncio.sleep(delay)
            entry = self.online_queue.get(int(user_id))
            if not entry:
                return
            bot = self._closest_bot(entry["rating"])
            self.online_queue.pop(int(user_id), None)
            self.online_tasks.pop(int(user_id), None)
            entry["public_message"] = await entry["channel"].send(
                f"🤖 Nenhum jogador apareceu a tempo. **{bot.display_name}** entrou na fila com "
                f"**{bot.rating} ELO**. TutoriUAU jura que ele não leu seu histórico."
            )
            await self._start_online_match(entry, bot)
        except asyncio.CancelledError:
            return

    async def _join_online_queue(self, ctx):
        user_id = ctx.author.id
        if user_id in self.active_online_users:
            return await ctx.send("Você já está em uma batalha online. Termine essa antes de abrir outra dimensão.")
        if user_id in self.online_queue:
            entry = self.online_queue[user_id]
            position = sorted(
                self.online_queue.values(),
                key=lambda item: item["joined_at"],
            ).index(entry) + 1
            return await ctx.send(
                f"Você já está na fila global, posição aproximada **#{position}**. "
                "Use `echo pvp online sair` para cancelar."
            )

        party = self.puxar_party_para_combate(ctx.author.id, ctx.author.display_name)
        if not party:
            return await ctx.send("Monte uma party válida e defina o herói principal antes de entrar no PvP Online.")

        entry = {
            "user": ctx.author,
            "channel": ctx.channel,
            "guild_id": ctx.guild.id if ctx.guild else 0,
            "guild_name": ctx.guild.name if ctx.guild else "Mensagem direta",
            "rating": self._player_rating(ctx.author.id),
            "joined_at": time.time(),
            "party": party,
        }
        opponent = self._find_online_opponent(entry)
        if opponent:
            self._remove_from_queue(opponent["user"].id)
            entry["public_message"] = await ctx.send(
                f"⚔️ Adversário encontrado: **{opponent['user'].display_name}** "
                f"({opponent['rating']} ELO). A batalha completa acontecerá neste canal."
            )
            opponent["public_message"] = await opponent["channel"].send(
                f"⚔️ Adversário encontrado: **{ctx.author.display_name}** "
                f"({entry['rating']} ELO). A batalha completa acontecerá neste canal."
            )
            return await self._start_online_match(opponent, entry)

        self.online_queue[user_id] = entry
        self.online_tasks[user_id] = asyncio.create_task(self._bot_match_after(user_id))
        await ctx.send(
            f"🌐 Você entrou na fila global com **{entry['rating']} ELO**.\n"
            "Estou procurando alguém de força próxima, priorizando outro servidor. "
            "Se a fila ficar vazia, um bot compatível entra em cerca de 15 segundos.\n"
            "Use `echo pvp online sair` para cancelar."
        )

    async def _start_online_match(self, first_entry, second):
        p1 = first_entry["user"]
        team_p1 = first_entry["party"]
        if isinstance(second, OnlinePvpBot):
            p2 = second
            team_p2 = self._build_bot_party(p2, team_p1)
            entries = [first_entry]
        else:
            p2 = second["user"]
            team_p2 = second["party"]
            entries = [first_entry, second]

        if not team_p1 or not team_p2:
            return await first_entry["channel"].send("Não consegui montar as duas equipes. A partida foi cancelada sem alterar ELO.")

        view = PvpBattleView(self, None, p1, p2, team_p1, team_p2, online=True)
        for entry in entries:
            battle_message = entry.get("public_message")
            if not battle_message:
                battle_message = await entry["channel"].send(
                    f"⚔️ Preparando a batalha de **{p1.display_name} vs {p2.display_name}**..."
                )
            view.add_message(battle_message)
        self.active_online_users.add(int(p1.id))
        if not getattr(p2, "bot", False):
            self.active_online_users.add(int(p2.id))
        await view.processar_fila()

    async def executar_pvp(self, channel, p1: discord.User, p2: discord.User):
        team_p1 = self.puxar_party_para_combate(p1.id, p1.name)
        team_p2 = self.puxar_party_para_combate(p2.id, p2.name)

        if not team_p1 or not team_p2:
            return await channel.send("Um dos jogadores não tem party válida. Duelo cancelado.")

        view = PvpBattleView(self, channel, p1, p2, team_p1, team_p2)
        view.add_message(await channel.send("Carregando duelo PvP..."))
        await view.processar_fila()

    @commands.command(name="pvp", aliases=["x1", "duelo"])
    async def pvp_cmd(self, ctx, *, alvo: str = None):
        normalized = _normalizar(alvo or "").strip()
        if normalized.startswith("online"):
            action = normalized.removeprefix("online").strip()
            if action in {"sair", "cancelar", "cancel", "leave"}:
                if ctx.author.id not in self.online_queue:
                    return await ctx.send("Você não está na fila global. O TutoriUAU conferiu duas vezes, dramaticamente.")
                self._remove_from_queue(ctx.author.id)
                return await ctx.send("Você saiu da fila do PvP Online. Nenhum ELO foi ferido no processo.")
            if action in {"status", "fila"}:
                entry = self.online_queue.get(ctx.author.id)
                if not entry:
                    return await ctx.send("Você não está na fila. Use `echo pvp online` para entrar.")
                waited = int(time.time() - entry["joined_at"])
                return await ctx.send(
                    f"Você está na fila há **{waited}s**, procurando rival próximo de **{entry['rating']} ELO**."
                )
            return await self._join_online_queue(ctx)

        membro = ctx.message.mentions[0] if ctx.message.mentions else None
        if not membro:
            return await ctx.send(
                "Use `echo pvp @usuário` para duelo local ou `echo pvp online` para buscar alguém na fila global."
            )
        if membro.id == ctx.author.id:
            return await ctx.send("Você não pode desafiar a si mesmo.")
        if membro.bot:
            return await ctx.send("Escolha um jogador humano para o duelo.")

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()

        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(ctx.author.id),))
        p1_db = cursor.fetchone()
        if not p1_db or not p1_db[0]:
            conn.close()
            return await ctx.send("Você precisa ter iniciado o jogo e definido um Herói Líder (`echo main <ID>`).")

        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(membro.id),))
        p2_db = cursor.fetchone()
        conn.close()

        if not p2_db or not p2_db[0]:
            return await ctx.send(f"{membro.name} ainda não tem uma party configurada para lutar.")

        embed = discord.Embed(
            title="Desafio PvP lançado",
            description=(
                f"{ctx.author.mention} desafiou {membro.mention}.\n\n"
                f"{membro.mention}, aceita uma batalha em turnos valendo ELO?"
            ),
            color=discord.Color.dark_red()
        )
        view = PvpAcceptView(ctx.author, membro, self)
        await ctx.send(content=membro.mention, embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(PvP(bot))
