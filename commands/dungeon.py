import discord
from discord.ext import commands
import sqlite3
import re
import os
import sys
import random
import time
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.dungeons import DUNGEONS
    from data.enemies import ENEMIES
    from data.heroes import HEROES
    from data.equipamentos import EQUIPAMENTOS
    from data.habilidades import SKILLS
    from utils.combat import CombatEntity, _as_ratio, apply_on_hit_statuses, apply_status_effects, apply_status_protection, choose_ai_combat_skill, choose_combat_skill
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
    from utils.skills import get_hero_skill_ids, resolve_skill_list
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.rewards import scale_combat_rewards
    from utils.equipment import get_equipment_bonus
    from utils.affinity import apply_affinity_bonus
    from utils.player_bonuses import apply_reward_bonuses, apply_battle_hp_bonus
except ModuleNotFoundError:
    DUNGEONS, ENEMIES, HEROES, EQUIPAMENTOS, SKILLS = {}, {}, {}, {}, {}
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []
    def resolve_skill_list(habilidades):
        return habilidades or []
    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}
    def apply_affinity_bonus(party_data, heroes):
        return party_data
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0):
        return gold, xp
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
    def choose_ai_combat_skill(actor, skills=None, allies=None, enemies=None, skill_chance=0.62):
        return choose_combat_skill(actor, skills, allies, enemies) if random.random() <= skill_chance else None
    def _as_ratio(value, default_when_true=0.0):
        if value is True:
            return float(default_when_true)
        if value in (None, False):
            return 0.0
        try:
            ratio = float(value)
        except (TypeError, ValueError):
            return 0.0
        if ratio > 1:
            ratio /= 100
        return max(0.0, ratio)
    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {"hp": 100, "atk": 10, "matk": 10, "def": 5, "spd": 10, "crt": 5, "level": level}
    def normalize_class(value):
        return str(value or "neutro").lower()
    def scale_combat_rewards(gold=0, xp=0, progress=1, reference=50):
        return gold, xp

COOLDOWN_DUNGEON = 1800 # 30 minutos em segundos


def _party_average_level(party_data):
    levels = []
    for member in party_data or []:
        if hasattr(member, "level"):
            levels.append(int(getattr(member, "level", 1) or 1))
        elif isinstance(member, dict):
            stats = member.get("stats", {})
            levels.append(int(member.get("level", stats.get("level", 1)) or 1))
    return sum(levels) / len(levels) if levels else 1


def scale_dungeon_enemy_stats(enemy_data, dungeon_id, area, party_data, is_boss=False):
    progress = max(1, ((int(dungeon_id) - 1) * 5) + int(area))
    avg_level = _party_average_level(party_data)
    hp_mult = 1.0 + (progress * 0.10) + min(0.75, avg_level * 0.008)
    atk_mult = 1.0 + (progress * 0.07) + min(0.55, avg_level * 0.005)
    def_mult = 1.0 + (progress * 0.06) + min(0.45, avg_level * 0.004)
    if is_boss:
        hp_mult *= 1.35
        atk_mult *= 1.15
        def_mult *= 1.12

    return {
        "hp": max(1, int((enemy_data.get("hp", 100) or 100) * hp_mult)),
        "atk": max(0, int((enemy_data.get("atk", 10) or 0) * atk_mult)),
        "def": max(0, int((enemy_data.get("def", 5) or 0) * def_mult)),
        "matk": max(0, int((enemy_data.get("matk", 0) or 0) * atk_mult)),
        "spd": max(1, min(65, int((enemy_data.get("spd", 15) or 15) + progress * 0.35))),
        "crt": max(0, min(45, int((enemy_data.get("crt", 5) or 5) + progress * 0.25))),
        "level": max(1, int(avg_level)),
    }


def build_dungeon_enemy_raw(enemy_id, index, dungeon_id, area, party_data, is_boss=False, summoned=False):
    enemy_data = ENEMIES.get(enemy_id, {})
    suffix = "Invocado" if summoned else str(index)
    return {
        "id": f"{enemy_id}_{index}_{int(time.time() * 1000) % 100000}" if summoned else f"{enemy_id}_{index}",
        "nome": f"{enemy_data.get('nome', enemy_id)} {suffix}",
        "classe": enemy_data.get("tipo", "boss" if is_boss else "comum"),
        "stats": scale_dungeon_enemy_stats(enemy_data, dungeon_id, area, party_data, is_boss=is_boss),
        "habilidades": [enemy_data.get("habilidade")] if enemy_data.get("habilidade") else [],
    }


def puxar_party_para_combate(user_id, user_name):
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
    p_data = cursor.fetchone()
    
    if not p_data or not p_data[0]:
        conn.close()
        return None
        
    cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
    team = cursor.fetchone()
    time_ids = [p_data[0]] + [x for x in (team if team else []) if x is not None]
    
    party_data = []
    
    for hid in time_ids:
        cursor.execute("SELECT hero_id, stars, level, equip_atk, equip_def, equip_livre FROM heroes WHERE id = ?", (int(hid),))
        hero = cursor.fetchone()
        if hero:
            h_id, stars, level, e_atk, e_def, e_livre = hero
            h_data = HEROES.get(h_id, {})
            
            equipment_bonuses = []
            for eq_name in [e_atk, e_def, e_livre]:
                if eq_name and eq_name in EQUIPAMENTOS:
                    equipment_bonuses.append(get_equipment_bonus(cursor, user_id, eq_name, EQUIPAMENTOS))

            stats = calculate_hero_stats(h_data, stars, level, equipment_bonuses)
            hp, atk, matk = stats["hp"], stats["atk"], stats["matk"]
            df, spd, crt = stats["def"], stats["spd"], stats["crt"]
            cl = normalize_class(h_data.get("classe", "neutro"))

            skill_ids = get_hero_skill_ids(h_data, stars, h_data.get("raridade", 0))
            party_data.append({
                "id": str(hid),
                "hero_id": h_id,
                "nome": f"{h_data.get('nome', 'Herói')} ({user_name})",
                "classe": cl,
                "level": level,
                "hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt,
                "stats": {"hp": hp, "atk": atk, "matk": matk, "def": df, "spd": spd, "crt": crt, "level": level},
                "habilidades": skill_ids
            })
            
    party_data = apply_affinity_bonus(party_data, HEROES)
    party_data = apply_battle_hp_bonus(cursor, user_id, party_data)
    conn.commit()
    conn.close()
    return party_data

# ==========================================
# MOTOR DE COMBATE INTERATIVO PARA DUNGEONS
# ==========================================
class DungeonBattleView(discord.ui.View):
    def __init__(self, ctx, party_data, team_b_raw, boss_id, andar_data, dungeon_id, andar, moral, prosp, d_cog, is_boss_phase=False):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.party_data = party_data
        
        self.boss_id = boss_id
        self.andar_data = andar_data
        self.dungeon_id = dungeon_id
        self.andar = andar
        self.moral = moral
        self.prosp = prosp
        self.d_cog = d_cog
        self.is_boss_phase = is_boss_phase
        
        self.team_a = [CombatEntity(f"A{i}", d["nome"], d, False) for i, d in enumerate(party_data)]
        self.team_b = [CombatEntity(e["id"], e["nome"], e["stats"], True) for e in team_b_raw]
        
        for i, e in enumerate(team_b_raw): self.team_b[i].habilidades = resolve_skill_list(e.get("habilidades", []))

        fase_nome = "O Chefe da Área" if is_boss_phase else "A Horda de Monstros"
        self.log_display = [f"🌲 **Exploração Iniciada!** {fase_nome} avança contra vocês."]
        self.current_actor = None
        self.message = None
        self.turn_queue = []

    def _get_alive(self, team): return [e for e in team if not e.is_dead]
    
    def _get_target_aggro(self, vivos):
        total_aggro = sum(e.get_aggro() for e in vivos)
        roll = random.uniform(0, total_aggro)
        acumulado = 0
        for e in vivos:
            acumulado += e.get_aggro()
            if roll <= acumulado: return e
        return vivos[0]

    def _roll_damage_variance(self, actor, amount):
        low = 0.90 if actor.is_enemy else 0.94
        high = 1.10 if actor.is_enemy else 1.07
        return max(1, int(amount * random.uniform(low, high)))

    def _summon_enemies(self, actor, effect):
        enemy_id = effect.get("invoca_inimigo") or effect.get("summon_enemy")
        if not actor.is_enemy or not enemy_id:
            return []

        alive_enemies = self._get_alive(self.team_b)
        if len(alive_enemies) >= 8:
            return []

        amount = min(3, max(1, int(effect.get("quantidade_invocada", 1) or 1)))
        amount = min(amount, 8 - len(alive_enemies))
        summoned = []
        for _ in range(amount):
            raw = build_dungeon_enemy_raw(
                enemy_id,
                len(self.team_b) + 1,
                self.dungeon_id,
                self.andar,
                self.team_a,
                is_boss=False,
                summoned=True,
            )
            entity = CombatEntity(raw["id"], raw["nome"], raw["stats"], True)
            entity.habilidades = resolve_skill_list(raw.get("habilidades", []))
            self.team_b.append(entity)
            summoned.append(entity.clean_name)
        return summoned

    def _gerar_timeline(self, todos_vivos):
        if not hasattr(self, 'turn_queue'): self.turn_queue = []
        fila = [e for e in self.turn_queue if not e.is_dead]
        
        if len(fila) < 4:
            proximo_round = sorted(todos_vivos, key=lambda x: (x.get_stat("spd"), 0 if x.is_enemy else 1), reverse=True)
            for e in proximo_round:
                if not e.is_dead:
                    fila.append(e)
                    if len(fila) >= 4: break
        
        nomes = [e.clean_name for e in fila[:4]]
        return " ⏭️ ".join(nomes)

    async def _atualizar_mensagem(self, interaction):
        embed = discord.Embed(title=f"⚔️ Masmorra D{self.dungeon_id} - Área {self.andar}", color=discord.Color.red() if self.is_boss_phase else discord.Color.blue())
        
        aliados_txt = "\n".join([f"{e.clean_name}: **{e.hp}/{e.max_hp}**" for e in self.team_a])
        inimigos_txt = "\n".join([f"{e.clean_name}: **{e.hp}/{e.max_hp}**" for e in self.team_b])
        
        embed.add_field(name="Sua Equipe", value=aliados_txt, inline=True)
        embed.add_field(name="Inimigos" if not self.is_boss_phase else "O Chefe", value=inimigos_txt, inline=True)
        
        todos_vivos = self._get_alive(self.team_a) + self._get_alive(self.team_b)
        embed.add_field(name="Fila de Ação", value=self._gerar_timeline(todos_vivos), inline=False)
        
        log_txt = "\n".join(self.log_display[-6:])
        embed.add_field(name="📜 Acontecimentos", value=f"```{log_txt}```", inline=False)

        if self.current_actor and not self.current_actor.is_enemy:
            embed.description = f"🟢 **SEU TURNO!** O que **{self.current_actor.clean_name}** deve fazer?"
        else: embed.description = "⏳ Oponentes a processar..."
        
        if interaction:
            try: await interaction.response.edit_message(embed=embed, view=self)
            except discord.errors.InteractionResponded: await interaction.message.edit(embed=embed, view=self)
        else:
            self.message = await self.ctx.send(embed=embed, view=self)

    # Lógica Simplificada de Habilidades
    def _executar_habilidade(self, actor, skill_id):
        if actor.is_silenced():
            target = self._get_target_aggro(self._get_alive(self.team_b if not actor.is_enemy else self.team_a))
            dealt = target.take_damage(actor.get_stat("atk"), actor.get_stat("atk"))
            return f"🤐 {actor.clean_name} está silenciado e improvisou um ataque por **{dealt}**."

        s_data = SKILLS.get(skill_id)
        if not s_data: 
            target = self._get_target_aggro(self._get_alive(self.team_b if not actor.is_enemy else self.team_a))
            is_crit = random.randint(1, 100) <= actor.get_stat("crt")
            dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
            dealt = target.take_damage(dmg, actor.get_stat("atk"))
            return f"🗡️ {actor.clean_name} improvisou um ataque por **{dealt}**."

        if "cooldown" in s_data: actor.cooldowns[skill_id] = s_data["cooldown"]
        actor.skill_uses[skill_id] = actor.skill_uses.get(skill_id, 0) + 1
        actor.last_skill_id = skill_id
        
        tipo = s_data.get("tipo", "dano")
        alvo_req = s_data.get("alvo", "unico_inimigo")
        efeito = s_data.get("efeito", {})
        
        time_aliado = self.team_a if not actor.is_enemy else self.team_b
        inimigos = self._get_alive(self.team_b if not actor.is_enemy else self.team_a)
        aliados = self._get_alive(time_aliado)
        aliados_mortos = [a for a in time_aliado if a.is_dead]
        
        targets = []
        if alvo_req == "aliado_morto": targets = aliados_mortos[:1]
        elif alvo_req == "aliados_mortos": targets = aliados_mortos
        elif "inimigo" in alvo_req or "campo" in alvo_req: targets = inimigos
        elif "aliado" in alvo_req: targets = aliados
        elif alvo_req == "self": targets = [actor]
        
        if alvo_req == "unico_inimigo" and inimigos: targets = [self._get_target_aggro(inimigos)]
        elif alvo_req == "unico_aliado" and aliados: targets = [random.choice(aliados)]
        elif alvo_req == "aliado_menor_hp" and aliados: targets = [min(aliados, key=lambda x: x.hp)]
        elif alvo_req in ["dps_aliado", "dps_aliados"] and aliados: targets = [max(aliados, key=lambda x: x.get_stat("atk") + x.get_stat("matk"))]
        elif "aleatorio" in alvo_req and inimigos:
            quantidade = min(len(inimigos), max(1, int(s_data.get("quantidade", 1) or 1)))
            targets = random.sample(inimigos, quantidade)
        
        if not targets: return f"❓ {actor.clean_name} conjurou ao vazio."

        log_line = f"✨ **{actor.clean_name}** usou `[{s_data['nome']}]`!"
        total_dmg, total_healed = 0, 0
        summoned_names = []
        
        for t in targets:
            if tipo in ["dano", "insta_kill", "especial"] and t.is_enemy != actor.is_enemy:
                is_magic = "matk" in str(efeito)
                base = actor.get_stat("matk") if is_magic else actor.get_stat("atk")
                if efeito.get("soma_atk_matk") or efeito.get("soma_atk_matk_buff") or efeito.get("soma_atk_matk_100"):
                    base = actor.get_stat("atk") + actor.get_stat("matk")

                dano = base + efeito.get("dano_atk_extra", 0) + efeito.get("dano_matk_extra", 0)
                mult = efeito.get("multiplicador_hit", 1) * efeito.get("multiplicador_atk", 1.0) * efeito.get("multiplicador_matk", 1.0)
                if efeito.get("dano_massivo") and not any(
                    key in efeito
                    for key in (
                        "multiplicador_atk",
                        "multiplicador_matk",
                        "multiplicador_soma_atk_matk",
                        "dano_atk_extra",
                        "dano_matk_extra",
                        "dano_hp_atual",
                        "dano_hp_max",
                    )
                ):
                    mult *= 2.2
                if efeito.get("multiplica_atk_matk"):
                    mult *= efeito.get("multiplica_atk_matk")
                if efeito.get("multiplicador_soma_atk_matk"):
                    mult *= efeito.get("multiplicador_soma_atk_matk")

                is_crit = random.randint(1, 100) <= actor.get_stat("crt") or efeito.get("critico_garantido", False)
                if is_crit:
                    mult *= 1.5

                dano = dano * mult
                if "dano_fixo" in efeito:
                    dano += int(efeito["dano_fixo"])
                if "dano_hp_atual" in efeito:
                    dano += int(t.hp * _as_ratio(efeito["dano_hp_atual"]))
                if "dano_hp_max" in efeito:
                    dano += int(t.max_hp * _as_ratio(efeito["dano_hp_max"]))
                if hasattr(actor, "cap_outgoing_damage"):
                    dano = actor.cap_outgoing_damage(dano, is_skill=True)
                dano = self._roll_damage_variance(actor, dano)

                persistent_ignore = max(
                    (float(buff.get("ignora_def_on_hit", 0)) for buff in actor.buffs),
                    default=0,
                )
                ignore_def = efeito.get("ignora_def_escudos", False) or efeito.get("ignora_def", False)
                if ignore_def is not True:
                    ignore_def = max(float(ignore_def or 0), persistent_ignore)
                if any(
                    efeito.get(key)
                    for key in [
                        "ignora_def_escudos",
                        "ignora_escudos",
                        "ignora_def_e_shield",
                        "remove_escudos",
                        "destroi_escudos",
                        "quebra_escudos",
                    ]
                ):
                    t.shield = 0

                dealt = t.take_damage(dano, base, is_magic=is_magic, ignore_def=ignore_def)
                total_dmg += dealt
                
                apply_status_effects(actor, t, efeito, dealt)
                apply_on_hit_statuses(actor, t, is_crit)
                if ("chance_insta_kill" in efeito and random.random() <= efeito["chance_insta_kill"]) or efeito.get("insta_kill_on_hit_garantido"):
                    if not t.is_dead:
                        t.hp = 0
                        t.is_dead = True
                if not summoned_names:
                    summoned_names.extend(self._summon_enemies(actor, efeito))
            elif tipo == "cura" and t.is_enemy == actor.is_enemy:
                cura = efeito.get("cura_fixa", int(actor.get_stat("matk") * 0.5))
                total_healed += t.heal(cura)
                apply_status_protection(t, efeito, efeito.get("turnos", 3))
            elif tipo in ["buff", "escudo", "passiva", "especial"] and t.is_enemy == actor.is_enemy and not t.is_dead:
                turnos = efeito.get("turnos", 2)
                if "buff_atk" in efeito: t.buffs.append({"stat": "atk", "mult": efeito["buff_atk"] / 100.0, "turnos": turnos})
                if "buff_matk" in efeito: t.buffs.append({"stat": "matk", "mult": efeito["buff_matk"] / 100.0, "turnos": turnos})
                if "buff_def" in efeito or tipo == "escudo": t.buffs.append({"stat": "def", "mult": efeito.get("buff_def", 50) / 100.0, "turnos": turnos})
                if "buff_spd" in efeito: t.buffs.append({"stat": "spd", "mult": efeito["buff_spd"] / 100.0, "turnos": turnos})
                if "escudo_hp_max" in efeito: t.shield += int(t.max_hp * efeito["escudo_hp_max"])
                if "imunidade_dano_turnos" in efeito: t.buffs.append({"stat": "imune", "imune_all": True, "turnos": turnos})
                if "ignora_dano_fisico" in efeito: t.buffs.append({"stat": "imune", "imune_fisico": True, "turnos": turnos})
                if "ignora_dano_magico" in efeito: t.buffs.append({"stat": "imune", "imune_magico": True, "turnos": turnos})
                apply_status_protection(t, efeito, turnos)
                if not summoned_names:
                    summoned_names.extend(self._summon_enemies(actor, efeito))
            elif tipo in ["debuff", "especial"] and t.is_enemy != actor.is_enemy and not t.is_dead:
                turnos = efeito.get("turnos", 2)
                if "debuff_atk" in efeito: t.debuffs.append({"stat": "atk", "mult": efeito["debuff_atk"] / 100.0, "turnos": turnos})
                if "debuff_matk" in efeito: t.debuffs.append({"stat": "matk", "mult": efeito["debuff_matk"] / 100.0, "turnos": turnos})
                if "debuff_def" in efeito: t.debuffs.append({"stat": "def", "mult": efeito["debuff_def"] / 100.0, "turnos": turnos})
                apply_status_effects(actor, t, efeito)

        if total_dmg > 0: log_line += f"\n⚔️ Causou aprox. **{total_dmg // len(targets)}** de dano!"
        elif total_healed > 0: log_line += f"\n💚 Curou aprox. **{total_healed // len(targets)} HP**!"
        if summoned_names:
            log_line += f"\n🐺 Reforços chegaram: **{', '.join(summoned_names[:3])}**."
        return log_line

    def _ia_inimigo_agir(self, actor):
        vivos_a = self._get_alive(self.team_a)
        if not vivos_a: return ""
        
        skill_usar = choose_ai_combat_skill(actor, SKILLS, self.team_b, self.team_a)
        if skill_usar: return self._executar_habilidade(actor, skill_usar)
            
        target = self._get_target_aggro(vivos_a)
        is_crit = random.randint(1, 100) <= actor.get_stat("crt")
        dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
        dealt = target.take_damage(dmg, actor.get_stat("atk"))
        apply_on_hit_statuses(actor, target, is_crit)
        crit = " (💥)" if is_crit else ""
        return f"🗡️ {actor.clean_name} atacou {target.clean_name} por **{dealt}**{crit}."

    async def processar_fila(self, interaction):
        self.clear_items()
        
        while True:
            vivos_a, vivos_b = self._get_alive(self.team_a), self._get_alive(self.team_b)
            if not vivos_a: return await self.fim_de_jogo(interaction, False)
            if not vivos_b: return await self.andar_limpo(interaction)

            all_alive = vivos_a + vivos_b
            if hasattr(self, 'turn_queue'): self.turn_queue = [e for e in self.turn_queue if not e.is_dead]
            else: self.turn_queue = []

            if not self.turn_queue:
                self.turn_queue = sorted(all_alive, key=lambda x: (x.get_stat("spd"), 0 if x.is_enemy else 1), reverse=True)

            actor = self.turn_queue.pop(0)
            estava_atordoado = actor.is_stunned()
            dot_logs = actor.tick_effects()
            self.log_display.extend(dot_logs)

            if estava_atordoado:
                self.log_display.append(f"💫 {actor.clean_name} está atordoado!")
                continue 

            self.current_actor = actor

            if actor.is_enemy:
                self.log_display.append(self._ia_inimigo_agir(actor))
                continue 
            else:
                self.add_item(ButtonAtacar(self))
                available_skills = [
                    skill_id
                    for skill_id in actor.habilidades
                    if skill_id in SKILLS and skill_id not in actor.cooldowns
                ]
                has_skill = bool(available_skills)
                sk_nome = "Habilidade"
                if len(available_skills) == 1:
                    sk_nome = SKILLS[available_skills[0]].get("nome", "Habilidade")
                elif len(available_skills) > 1:
                    sk_nome = f"Habilidade ({len(available_skills)} opções)"
                
                self.add_item(ButtonHabilidade(self, sk_nome, not has_skill))
                self.add_item(ButtonDefender(self))
                
                await self._atualizar_mensagem(interaction)
                return 

    async def andar_limpo(self, interaction):
        self.clear_items()
        
        # Se foi a Horda, e tem Chefe, transita para a View do Chefe!
        if not self.is_boss_phase and self.boss_id:
            boss_nome = ENEMIES.get(self.boss_id, {}).get("nome", "Chefe")
            embed = discord.Embed(title="⚠️ O CHAMADO DA MORTE", description=f"Vocês trucidaram a horda, mas o **{boss_nome}** despertou!\nVocês recuperaram 10% do HP descansando rapidamente.", color=discord.Color.orange())
            
            # Cura parcial de descanso
            for a in self._get_alive(self.team_a): a.heal(int(a.max_hp * 0.10))
            
            view = BossEncounterView(self.ctx.author.id, self.team_a, self.boss_id, self.andar_data, self.dungeon_id, self.andar, self.moral, self.prosp, self.d_cog, self.ctx)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            # Se era o chefe ou a área não tinha chefe, FIM DE DUNGEON COM VITÓRIA!
            resultado, lvl_up_msg = self.d_cog.processar_vitoria(self.ctx.author.id, self.andar_data, self.moral, self.prosp, self.dungeon_id, self.andar)
            embed = discord.Embed(title="✅ EXPLORAÇÃO CONCLUÍDA!", description=resultado + lvl_up_msg, color=discord.Color.green())
            await interaction.response.edit_message(embed=embed, view=None)

    async def fim_de_jogo(self, interaction, venceu=False):
        self.clear_items()
        embed = discord.Embed(title="☠️ DERROTA NA MASMORRA!", description="Seu time foi aniquilado. Vocês fugiram sem conseguir completar a exploração.", color=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=None)


class ButtonAtacar(discord.ui.Button):
    def __init__(self, battle_view):
        super().__init__(style=discord.ButtonStyle.danger, label="Atacar", emoji="🗡️")
        self.view_ref = battle_view

    async def callback(self, interaction: discord.Interaction):
        actor = self.view_ref.current_actor
        target = self.view_ref._get_target_aggro(self.view_ref._get_alive(self.view_ref.team_b))
        is_crit = random.randint(1, 100) <= actor.get_stat("crt")
        dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
        dealt = target.take_damage(dmg, actor.get_stat("atk"))
        self.view_ref.log_display.append(f"🗡️ {actor.clean_name} atacou {target.clean_name} por **{dealt}**.")
        await self.view_ref.processar_fila(interaction)

class ButtonHabilidade(discord.ui.Button):
    def __init__(self, battle_view, label, disabled):
        super().__init__(style=discord.ButtonStyle.primary, label=label, emoji="✨", disabled=disabled)
        self.view_ref = battle_view

    async def callback(self, interaction: discord.Interaction):
        actor = self.view_ref.current_actor
        s_id = choose_combat_skill(actor, SKILLS, self.view_ref.team_a, self.view_ref.team_b)
        if not s_id:
            return await interaction.response.send_message(
                "Todas as habilidades deste herói estão em recarga.",
                ephemeral=True,
            )
        log_msg = self.view_ref._executar_habilidade(actor, s_id)
        self.view_ref.log_display.append(log_msg)
        await self.view_ref.processar_fila(interaction)

class ButtonDefender(discord.ui.Button):
    def __init__(self, battle_view):
        super().__init__(style=discord.ButtonStyle.secondary, label="Defender", emoji="🛡️")
        self.view_ref = battle_view

    async def callback(self, interaction: discord.Interaction):
        actor = self.view_ref.current_actor
        actor.buffs.append({"stat": "def", "mult": 0.5, "turnos": 1}) 
        cura = actor.heal(int(actor.max_hp * 0.10))
        self.view_ref.log_display.append(f"🛡️ {actor.clean_name} defendeu e recuperou **{cura} HP**.")
        await self.view_ref.processar_fila(interaction)


# ==========================================
# VIEW DE TRANSIÇÃO PARA O CHEFE
# ==========================================
class BossEncounterView(discord.ui.View):
    def __init__(self, user_id, team_a, boss_id, andar_data, dungeon_id, andar, moral, prosp, d_cog, ctx):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.team_a = team_a
        self.boss_id = boss_id
        self.andar_data = andar_data
        self.dungeon_id = dungeon_id
        self.andar = andar
        self.moral = moral
        self.prosp = prosp
        self.d_cog = d_cog
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == str(self.user_id)

    @discord.ui.button(label="Enfrentar Chefe!", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def btn_enfrentar(self, interaction: discord.Interaction, button: discord.ui.Button):
        team_b_raw = [build_dungeon_enemy_raw(self.boss_id, 1, self.dungeon_id, self.andar, self.team_a, is_boss=True)]
        team_b_raw[0]["nome"] = f"👑 {team_b_raw[0]['nome']}"

        # Cria a view do combate interativo agora contra o boss
        view_boss = DungeonBattleView(self.ctx, [], team_b_raw, self.boss_id, self.andar_data, self.dungeon_id, self.andar, self.moral, self.prosp, self.d_cog, is_boss_phase=True)
        view_boss.team_a = self.team_a # Passa o time do jogador já surrado/curado
        
        await view_boss.processar_fila(interaction)

    @discord.ui.button(label="Recuar com o Loot Parcial", style=discord.ButtonStyle.secondary, emoji="🏃")
    async def btn_recuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        base_gold = int(self.andar_data.get("loot_gold", 0) * 0.3)
        progress = max(1, ((int(self.dungeon_id) - 1) * 10) + (int(self.andar) * 2))
        base_gold, _ = scale_combat_rewards(base_gold, 0, progress)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (base_gold, str(self.user_id)))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🏃 Retirada Tática",
            description=f"Vocês não quiseram arriscar a vida contra o chefe. Fugiram com **+{base_gold} Gold** dos monstros menores.",
            color=discord.Color.light_grey()
        )
        await interaction.response.edit_message(embed=embed, view=None)

# ==========================================
# COG PRINCIPAL DE DUNGEON
# ==========================================
class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        # Adicionando controle de cooldown no DB
        try: cursor.execute("ALTER TABLE players ADD COLUMN last_dungeon REAL DEFAULT 0")
        except sqlite3.OperationalError: pass
        conn.commit()
        conn.close()

    def processar_vitoria(self, user_id, andar_data, moral, prosp, d_id, a_id):
        base_gold = andar_data.get("loot_gold", 0)
        base_xp_main = andar_data.get("loot_xp_main", 0)
        base_xp_party = andar_data.get("loot_xp_party", 0)
        
        mult_cidade = 1.0
        if moral > 70: mult_cidade += 0.10
        elif moral <= 25: mult_cidade -= 0.10
        if prosp >= 100: mult_cidade += 0.20
        elif prosp >= 50: mult_cidade += 0.10

        final_gold = int(base_gold * mult_cidade)
        final_xp_main = int(base_xp_main * mult_cidade)
        final_xp_party = int(base_xp_party * mult_cidade)
        progress = max(1, ((int(d_id) - 1) * 10) + (int(a_id) * 2))
        final_gold, final_xp_main = scale_combat_rewards(
            final_gold,
            final_xp_main,
            progress,
        )
        _, final_xp_party = scale_combat_rewards(
            0,
            final_xp_party,
            progress,
        )

        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        final_gold, final_xp_main = apply_reward_bonuses(cursor, user_id, final_gold, final_xp_main)
        _, final_xp_party = apply_reward_bonuses(cursor, user_id, 0, final_xp_party)
        cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (final_gold, str(user_id)))
        
        cursor.execute("SELECT main_hero FROM players WHERE user_id = ?", (str(user_id),))
        main = cursor.fetchone()
        cursor.execute("SELECT slot_2, slot_3, slot_4, slot_5 FROM teams WHERE user_id = ?", (str(user_id),))
        team = cursor.fetchone()
        
        lvl_up_log = ""
        
        ups_p, lvl_p = dar_xp_jogador(cursor, user_id, final_xp_main)
        if ups_p > 0: lvl_up_log += f"\n🆙 **Sua Conta** subiu para o Nível {lvl_p}!"
        
        if main and main[0]:
            ups, novo_lvl = dar_xp_heroi(cursor, main[0], final_xp_main)
            if ups > 0: lvl_up_log += f"\n🌟 O seu Líder subiu para o Nível {novo_lvl}!"
        
        if team:
            for hid in team:
                if hid:
                    ups, novo_lvl = dar_xp_heroi(cursor, hid, final_xp_party)
                    if ups > 0: lvl_up_log += f"\n✨ Um Aliado subiu para o Nível {novo_lvl}!"

        cursor.execute("SELECT highest_dungeon, highest_area FROM dungeon_progress WHERE user_id = ?", (str(user_id),))
        prog = cursor.fetchone()
        if prog:
            max_d, max_a = prog
            if d_id == max_d and a_id == max_a:
                nova_area = max_a + 1
                nova_dg = max_d
                if nova_area > 5:
                    nova_area = 1
                    nova_dg += 1
                cursor.execute("UPDATE dungeon_progress SET highest_dungeon = ?, highest_area = ? WHERE user_id = ?", (nova_dg, nova_area, str(user_id)))

        conn.commit()
        conn.close()

        return f"🏆 **ÁREA CONCLUÍDA!**\n💰 **+{final_gold} Gold**\n⭐ **+{final_xp_main} XP (Líder)**", lvl_up_log

    @commands.command(name="dungeon", aliases=["d", "explorar", "d1", "d2", "d3", "d4", "d5"])
    async def explorar(self, ctx, *args):
        # 1. VERIFICAÇÃO DE COOLDOWN (30 Minutos)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT last_dungeon FROM players WHERE user_id = ?", (str(ctx.author.id),))
        ld_data = cursor.fetchone()
        
        if ld_data and ld_data[0]:
            tempo_passado = time.time() - ld_data[0]
            if tempo_passado < COOLDOWN_DUNGEON:
                conn.close()
                minutos_restantes = int((COOLDOWN_DUNGEON - tempo_passado) / 60)
                return await ctx.send(f"⏳ **TutoriUAU:** Calma aí, maratonista! Você precisa esperar **{minutos_restantes} minutos** antes de entrar em outra Dungeon.")

        invoked = ctx.invoked_with.lower()
        full_text = f"{invoked} {' '.join(args)}"
        numeros = re.findall(r'\d+', full_text)

        if len(numeros) < 2: 
            conn.close()
            return await ctx.send("⚔️ Uso correto: `echo d1 a1`")

        dungeon_id = int(numeros[0])
        andar = int(numeros[1])

        cursor.execute("SELECT highest_dungeon, highest_area FROM dungeon_progress WHERE user_id = ?", (str(ctx.author.id),))
        prog = cursor.fetchone()
        
        if not prog:
            cursor.execute("INSERT INTO dungeon_progress (user_id, highest_dungeon, highest_area) VALUES (?, 1, 1)", (str(ctx.author.id),))
            conn.commit()
            max_d, max_a = 1, 1
        else: max_d, max_a = prog

        if dungeon_id > max_d or (dungeon_id == max_d and andar > max_a):
            conn.close()
            return await ctx.send(f"✋ **Opa, opa! Alto lá!** Deve limpar a D{max_d}-A{max_a} primeiro.")

        dungeon_key = next((key for key, data in DUNGEONS.items() if data.get("id") == dungeon_id), None)
        if not dungeon_key: 
            conn.close()
            return await ctx.send("❌ Dungeon não encontrada.")

        dungeon_data = DUNGEONS[dungeon_key]
        if andar not in dungeon_data["andares"]: 
            conn.close()
            return await ctx.send("❌ Andar inexistente.")

        andar_data = dungeon_data["andares"][andar]
        
        # OBTÉM A CIDADE DO SERVIDOR (Lazy Init Local)
        guild_id = str(ctx.guild.id) if ctx.guild else "0"
        cursor.execute("SELECT moral, prosperidade FROM cidades WHERE guild_id = ?", (guild_id,))
        city_stats = cursor.fetchone()
        
        # SE ENTRAR NA DUNGEON, SETA O COOLDOWN AGORA
        cursor.execute("UPDATE players SET last_dungeon = ? WHERE user_id = ?", (time.time(), str(ctx.author.id)))
        conn.commit()
        conn.close()

        moral = city_stats[0] if city_stats else 100
        prosp = city_stats[1] if city_stats else 0

        team_a_data = puxar_party_para_combate(ctx.author.id, ctx.author.name)
        if not team_a_data: return await ctx.send("❌ Equipe um Herói Líder com `echo main <ID>` antes de explorar!")

        # GERA A HORDA DE INIMIGOS MENORES
        team_b_raw = []
        c = 1
        for in_id, quantidade in andar_data.get("inimigos", {}).items():
            for _ in range(quantidade):
                team_b_raw.append(build_dungeon_enemy_raw(in_id, c, dungeon_id, andar, team_a_data))
                c += 1

        boss_id = andar_data.get("mini_boss") or andar_data.get("boss")
        
        # INICIA A VIEW INTERATIVA
        view_batalha = DungeonBattleView(ctx, team_a_data, team_b_raw, boss_id, andar_data, dungeon_id, andar, moral, prosp, self, is_boss_phase=False)
        msg = await ctx.send("⚔️ **Entrando na Masmorra...**")
        view_batalha.message = msg
        await view_batalha.processar_fila(None) # Dispara o primeiro turno

async def setup(bot):
    await bot.add_cog(Dungeon(bot))
