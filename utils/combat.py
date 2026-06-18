import random
import math
import os
import sys

# Gambiarra de importação
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Mesclando as Habilidades de Heróis e Monstros
try:
    from data.habilidades import SKILLS
except ModuleNotFoundError:
    SKILLS = {}

try:
    from utils.skills import resolve_skill_id
except Exception:
    def resolve_skill_id(habilidade):
        if isinstance(habilidade, dict):
            habilidade = habilidade.get("id") or habilidade.get("nome")
        return str(habilidade).lower().replace(" ", "_") if habilidade else None
    
try:
    from data.habmonsters import MONSTER_SKILLS
    SKILLS.update(MONSTER_SKILLS)
except ModuleNotFoundError:
    pass


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


def choose_combat_skill(actor, skills=None, allies=None, enemies=None):
    """Escolhe entre todas as habilidades disponíveis, priorizando urgências."""
    skills = skills or SKILLS
    candidates = [
        skill_id
        for skill_id in getattr(actor, "habilidades", [])
        if skill_id in skills and skill_id not in getattr(actor, "cooldowns", {})
        and (
            not skills[skill_id].get("uso_maximo")
            or getattr(actor, "skill_uses", {}).get(skill_id, 0) < skills[skill_id]["uso_maximo"]
        )
    ]
    if not candidates:
        return None

    allies = list(allies or [])
    enemies = list(enemies or [])
    dead_allies = [ally for ally in allies if getattr(ally, "is_dead", False)]
    living_allies = [ally for ally in allies if not getattr(ally, "is_dead", False)]
    wounded_allies = [
        ally
        for ally in living_allies
        if getattr(ally, "max_hp", 1) > 0 and (ally.hp / ally.max_hp) <= 0.55
    ]

    revive_skills = [skill_id for skill_id in candidates if skills[skill_id].get("tipo") == "reviver"]
    if dead_allies and revive_skills:
        return random.choice(revive_skills)

    healing_skills = [skill_id for skill_id in candidates if skills[skill_id].get("tipo") == "cura"]
    if wounded_allies and healing_skills:
        return random.choice(healing_skills)

    useful = []
    for skill_id in candidates:
        skill = skills[skill_id]
        skill_type = skill.get("tipo")
        if skill_type == "reviver" and not dead_allies:
            continue
        if skill_type == "cura" and living_allies and not any(ally.hp < ally.max_hp for ally in living_allies):
            continue
        if skill_type in {"dano", "debuff", "insta_kill"} and not enemies:
            continue
        useful.append(skill_id)

    return random.choice(useful or candidates)


# ==========================================
# CLASSE DE ENTIDADE (Herói ou Monstro)
# ==========================================
class CombatEntity:
    def __init__(self, id_str, name, stats, is_enemy=False):
        self.id = id_str
        self.name = name
        self.is_enemy = is_enemy
        raw_stats = stats.get("stats", stats)
        
        # Estética de Combate (Bolinhas para separar os times)
        self.team_emoji = "🔴" if self.is_enemy else "🔵"
        self.clean_name = f"{self.team_emoji} {self.name.split(' (')[0]}"
        
        # Status Base
        self.level = max(1, int(stats.get("level", raw_stats.get("level", 1)) or 1))
        self.max_hp = max(1, raw_stats.get("hp", 100))
        self.hp = raw_stats.get("current_hp", self.max_hp)
        self.shield = 0 # Escudo Verdadeiro (Absorve Dano)
        
        self.base_atk = raw_stats.get("atk", 10)
        self.base_matk = raw_stats.get("matk", 10)
        self.base_def = raw_stats.get("def", 5)
        self.base_spd = max(1, raw_stats.get("spd", 10))
        self.base_crt = raw_stats.get("crt", 5)
        
        # Filtro de limpeza de Habilidades
        raw_skills = stats.get("habilidades", [])
        self.habilidades = []
        for s in raw_skills:
            skill_id = resolve_skill_id(s)
            if skill_id and skill_id not in self.habilidades:
                self.habilidades.append(skill_id)
                
        self.classe = stats.get("classe", "comum").lower()
        
        # Sistema de Turnos (Valor de Ação)
        self.action_value = 10000 / self.base_spd
        
        # Status Temporários
        self.buffs = []
        self.debuffs = []
        self.cooldowns = {}
        self.skill_uses = {}
        self.is_dead = (self.hp <= 0)
        self.cannot_revive = False
        
        # Sistema de Aggro (Provocação)
        if self.classe == "tank": self.base_aggro = 300
        elif self.classe in ["suporte", "curandeiro"]: self.base_aggro = 75
        elif self.classe in ["atirador", "mago", "assassino"]: self.base_aggro = 50
        else: self.base_aggro = 100

    def cap_outgoing_damage(self, amount, is_skill=True):
        if self.is_enemy or not is_skill:
            return amount

        max_offense = max(self.base_atk, self.base_matk, 1)
        soft_cap = 85 + (self.level * 18) + (max_offense * 1.65)
        if self.level >= 80:
            soft_cap *= 1.55
        elif self.level >= 50:
            soft_cap *= 1.35
        elif self.level >= 25:
            soft_cap *= 1.18
        return min(amount, soft_cap)

    def get_stat(self, stat_name):
        base = getattr(self, f"base_{stat_name}", 100 if stat_name == "acc" else 0)
        mult = 1.0
        flat = 0
        
        for b in self.buffs:
            if b.get("stat") == stat_name:
                mult += b.get("mult", 0)
                flat += b.get("flat", 0)
                
        for d in self.debuffs:
            if d.get("stat") == stat_name:
                mult -= d.get("mult", 0)
                
        return max(0, int(base * max(0.1, mult) + flat))

    def get_aggro(self):
        # Se tiver Taunt absoluto, puxa 100% da atenção
        if any(b.get("stat") == "taunt" for b in self.buffs):
            return 99999
            
        aggro = self.base_aggro
        for b in self.buffs:
            if b.get("stat") == "aggro": aggro *= b.get("mult", 2.0)
        for d in self.debuffs:
            if d.get("reduz_aggro"): aggro *= 0.1 # Miko Yotsuya
        return max(1, int(aggro))

    def take_damage(self, amount, source_atk, is_magic=False, ignore_def=False):
        if self.is_dead: return 0
        
        # Imunidades
        for b in self.buffs:
            if b.get("imune_all") or (not is_magic and b.get("imune_fisico")) or (is_magic and b.get("imune_magico")):
                return 0

        # Cálculo de Defesa
        current_def = self.get_stat("def")
        if ignore_def is True:
            current_def = 0
        elif isinstance(ignore_def, (int, float)) and ignore_def > 0:
            current_def *= max(0, 1 - min(100, float(ignore_def)) / 100)
        mitigation = max(0.15, 100 / (100 + current_def))
        
        # Cálculo de Fraqueza (Recebe mais dano)
        fraqueza_mult = 1.0
        for d in self.debuffs:
            if d.get("stat") == "fraqueza": fraqueza_mult += d.get("mult", 0.25)
            
        damage_reduction = 0.0
        for buff in self.buffs:
            damage_reduction = max(
                damage_reduction,
                min(0.90, float(buff.get("reduz_dano_recebido", 0)) / 100),
            )
        final_damage = max(1, int(amount * mitigation * fraqueza_mult * (1 - damage_reduction)))
        
        # Absorção por Escudo Verdadeiro
        if self.shield > 0:
            if final_damage >= self.shield:
                final_damage -= self.shield
                self.shield = 0
            else:
                self.shield -= final_damage
                return 0 # Escudo tancou tudo
        
        self.hp -= final_damage
        if self.hp <= 0:
            imortal = any(b.get("imortal") for b in self.buffs)
            if imortal:
                self.hp = 1
            else:
                revive_buff = next(
                    (
                        buff
                        for buff in self.buffs
                        if (buff.get("revive_hp") or buff.get("revive_hp_max"))
                        and not buff.get("_revive_used")
                    ),
                    None,
                )
                if revive_buff and not self.cannot_revive:
                    revive_buff["_revive_used"] = True
                    revive_percent = float(
                        revive_buff.get("revive_hp", revive_buff.get("revive_hp_max", 0.20))
                    )
                    self.hp = max(1, int(self.max_hp * revive_percent))
                    self.is_dead = False
                else:
                    self.hp = 0
                    self.is_dead = True

        if not self.is_dead:
            heal_percent = max(
                (
                    float(buff.get("heal_damage_received", 0))
                    for buff in self.buffs
                ),
                default=0,
            )
            if heal_percent > 0:
                self.heal(int(final_damage * heal_percent))
                
        return final_damage

    def heal(self, amount):
        if self.is_dead: return 0
        
        # Corta Cura e Anti-Cura
        corta_cura = 1.0
        for d in self.debuffs:
            if d.get("stat") == "anti_cura": return 0
            if d.get("stat") == "corta_cura": corta_cura = 0.5
            
        amount = int(amount * corta_cura)
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def is_stunned(self):
        return any(
            d.get("stun") or d.get("stat") in {"stun", "freeze", "root", "fear", "confusion"}
            for d in self.debuffs
        )

    def is_silenced(self):
        return any(d.get("stat") == "silence" for d in self.debuffs)

    def status_text(self):
        labels = {
            "stun": "Atordoado",
            "freeze": "Congelado",
            "root": "Preso",
            "fear": "Amedrontado",
            "confusion": "Confuso",
            "silence": "Silenciado",
            "weakness": "Fraqueza",
            "slow": "Lentidão",
            "burn": "Queimadura",
            "poison": "Veneno",
            "bleed": "Sangramento",
            "curse": "Maldição",
            "anti_heal": "Anti-cura",
            "healing_cut": "Cura reduzida",
        }
        active = []
        for effect in self.debuffs:
            status = effect.get("status") or effect.get("stat")
            label = labels.get(status)
            if label and label not in active:
                active.append(label)
        return ", ".join(active)

    def has_status_immunity(self, status):
        aliases = {
            "burn": {"burn", "queimadura", "fogo"},
            "poison": {"poison", "veneno", "toxina"},
            "bleed": {"bleed", "sangramento"},
            "freeze": {"freeze", "congelamento", "gelo"},
            "stun": {"stun", "freeze", "root", "cc"},
            "fear": {"fear", "medo"},
            "confusion": {"confusion", "confusao"},
            "curse": {"curse", "maldicao"},
            "weakness": {"weakness", "fraqueza"},
            "slow": {"slow", "lentidao"},
        }
        wanted = aliases.get(status, {status})
        for buff in self.buffs:
            if buff.get("imunidade_debuffs") or buff.get("imune_debuffs_cc_instakill"):
                return True
            if status in {"burn", "poison", "bleed"} and buff.get("imune_maldicoes_dot_terreno"):
                return True
            if status == "curse" and buff.get("imune_maldicoes_dot_terreno"):
                return True
            if status == "fear" and buff.get("imune_medo"):
                return True
            if status in {"stun", "freeze", "root"} and (
                buff.get("imune_cc") or buff.get("imunidade_cc") or buff.get("imune_stun")
            ):
                return True
            if status in {"burn", "poison", "bleed"} and buff.get("imune_toxinas"):
                return True
            if status in {"slow", "weakness"} and buff.get("imune_lentidao_fraqueza"):
                return True
            for key, value in buff.items():
                normalized = str(key).lower()
                if value and normalized.startswith("imune_") and any(token in normalized for token in wanted):
                    return True
        return False

    def add_status(self, status, turns=1, potency=0, ignore_immunity=False):
        if not ignore_immunity and self.has_status_immunity(status):
            return False

        turns = max(1, int(turns or 1))
        stat_by_status = {
            "stun": "stun",
            "freeze": "freeze",
            "root": "root",
            "fear": "fear",
            "confusion": "confusion",
            "silence": "silence",
            "weakness": "fraqueza",
            "slow": "spd",
            "anti_heal": "anti_cura",
            "healing_cut": "corta_cura",
        }
        stat = stat_by_status.get(status, "dot")
        existing = next(
            (
                effect
                for effect in self.debuffs
                if effect.get("status") == status
                or (
                    status in {"stun", "freeze", "root"}
                    and effect.get("stat") in {"stun", "freeze", "root"}
                )
            ),
            None,
        )
        if existing:
            existing["turnos"] = max(existing.get("turnos", 0), turns)
            if status in {"burn", "poison", "bleed", "curse"}:
                existing["dot"] = max(int(existing.get("dot", 0)), int(potency or 0))
            elif status == "weakness":
                existing["mult"] = max(float(existing.get("mult", 0)), float(potency or 0.25))
            elif status == "slow":
                existing["mult"] = max(float(existing.get("mult", 0)), float(potency or 0.25))
            return True

        effect = {"stat": stat, "status": status, "turnos": turns}
        if status in {"stun", "freeze", "root", "fear", "confusion"}:
            effect["stun"] = True
        elif status in {"burn", "poison", "bleed", "curse"}:
            effect["dot"] = max(1, int(potency or 1))
        elif status == "weakness":
            effect["mult"] = float(potency or 0.25)
        elif status == "slow":
            effect["mult"] = float(potency or 0.25)
        self.debuffs.append(effect)
        return True

    def remove_statuses(self, statuses=None):
        if not statuses:
            removed = len(self.debuffs)
            self.debuffs = []
            return removed
        statuses = set(statuses)
        old_count = len(self.debuffs)
        self.debuffs = [
            effect
            for effect in self.debuffs
            if effect.get("status") not in statuses and effect.get("stat") not in statuses
        ]
        return old_count - len(self.debuffs)

    def tick_effects(self):
        log_effects = []
        for d in self.debuffs:
            if "dot" in d:
                dmg = d["dot"]
                self.hp -= dmg # DoT é dano direto (True Damage)
                status = d.get("status", "dot")
                labels = {
                    "burn": "Queimadura",
                    "poison": "Veneno",
                    "bleed": "Sangramento",
                    "curse": "Maldição",
                }
                log_effects.append(
                    f"🔥 **{self.clean_name}** sofreu {dmg} de {labels.get(status, 'Dano Contínuo')}."
                )
                if self.hp <= 0 and not any(b.get("imortal") for b in self.buffs):
                    self.hp = 0
                    self.is_dead = True
                elif self.hp <= 0:
                    self.hp = 1
                
        for b in self.buffs:
            if "dot_self" in b and not self.is_dead:
                dmg = max(1, int(b["dot_self"]))
                self.hp -= dmg
                log_effects.append(
                    f"🔥 **{self.clean_name}** sofreu {dmg} de dano pelo próprio efeito."
                )
                if self.hp <= 0 and not any(buff.get("imortal") for buff in self.buffs):
                    self.hp = 0
                    self.is_dead = True
                elif self.hp <= 0:
                    self.hp = 1
            if "regen" in b and not self.is_dead:
                cura = self.heal(b["regen"])
                if cura > 0:
                    log_effects.append(f"💚 **{self.clean_name}** regenerou {cura} HP.")

        self.buffs = [b for b in self.buffs if self._decrement_turn(b)]
        self.debuffs = [d for d in self.debuffs if self._decrement_turn(d)]
        
        for skill in list(self.cooldowns.keys()):
            self.cooldowns[skill] -= 1
            if self.cooldowns[skill] <= 0:
                del self.cooldowns[skill]
                
        return log_effects

    def _decrement_turn(self, effect):
        if effect.get("turnos", 1) == -1: return True
        effect["turnos"] -= 1
        return effect["turnos"] > 0


def apply_status_effects(actor, target, effect, damage_dealt=0, critical=False):
    """Normaliza os formatos históricos de efeitos usados pelo catálogo."""
    if not effect:
        return []

    default_turns = max(1, int(effect.get("turnos", 2) or 2))
    self_immunity = {
        key: effect[key]
        for key in [
            "imune_cc",
            "imunidade_cc",
            "imune_stun",
            "imune_queimadura",
            "imune_toxinas",
            "imunidade_debuffs",
            "imune_debuffs_cc_instakill",
            "imune_lentidao_fraqueza",
            "imune_maldicoes_dot_terreno",
            "imune_medo",
        ]
        if effect.get(key)
    }
    if self_immunity:
        apply_status_protection(actor, self_immunity, default_turns)
    if target.is_dead:
        return []

    applied = []
    ignore_cc = bool(effect.get("ignora_imunidade_cc"))
    def add(status, turns=None, potency=0, chance=1.0, ignore_immunity=False):
        if chance is None:
            chance = 1.0
        chance = float(chance)
        if chance > 1:
            chance /= 100
        if random.random() > chance:
            return False
        if target.add_status(
            status,
            turns or default_turns,
            potency,
            ignore_immunity=ignore_immunity,
        ):
            applied.append(status)
            return True
        return False

    stun_turns = effect.get("stun_turnos") or effect.get("stun_turnos_global")
    if stun_turns:
        add("stun", stun_turns, chance=effect.get("chance_stun", 1.0), ignore_immunity=ignore_cc)
    elif effect.get("chance_stun"):
        add("stun", default_turns, chance=effect["chance_stun"], ignore_immunity=ignore_cc)
    if effect.get("stun_se_vivo") and not target.is_dead:
        add("stun", effect["stun_se_vivo"], ignore_immunity=ignore_cc)
    if effect.get("stun_se_hp_baixo") and target.hp <= target.max_hp * (effect["stun_se_hp_baixo"] / 100):
        add("stun", 1, ignore_immunity=ignore_cc)

    freeze_chance = effect.get("chance_freeze")
    if freeze_chance:
        add("freeze", default_turns, chance=freeze_chance, ignore_immunity=ignore_cc)
    if effect.get("freeze_turnos") or effect.get("congelamento_turnos"):
        add("freeze", effect.get("freeze_turnos") or effect.get("congelamento_turnos"), ignore_immunity=ignore_cc)
    if effect.get("root_turnos"):
        add("root", effect["root_turnos"], ignore_immunity=ignore_cc)
    if effect.get("silence_turnos"):
        add("silence", effect["silence_turnos"])
    if effect.get("fear_turnos") or effect.get("medo_turnos"):
        add("fear", effect.get("fear_turnos") or effect.get("medo_turnos"))
    if effect.get("confusao"):
        add("confusion", effect.get("turnos", 1))

    if effect.get("dano_recebido_extra") is not None:
        add("weakness", default_turns, min(0.90, float(effect.get("dano_recebido_extra") or 25) / 100))
    if effect.get("aplica_fraqueza") is not None:
        add("weakness", default_turns, float(effect.get("aplica_fraqueza") or 25) / 100)
    if effect.get("debuff_fraqueza") is not None:
        add("weakness", default_turns, float(effect.get("debuff_fraqueza") or 25) / 100)
    if effect.get("fraqueza"):
        add("weakness", default_turns, 0.25)

    slow_value = effect.get("debuff_spd")
    if slow_value:
        add("slow", default_turns, min(0.90, float(slow_value) / 100))
    global_slow = effect.get("debuff_spd_global")
    if global_slow:
        add("slow", default_turns, min(0.90, float(global_slow) / 100))
    legacy_slow = effect.get("debuff_spd_inimiga")
    if legacy_slow:
        add("slow", default_turns, min(0.90, float(legacy_slow) / 100))
    compound_def_slow = effect.get("debuff_def_spd_inimigo")
    if compound_def_slow:
        potency = min(0.90, float(compound_def_slow) / 100)
        target.debuffs.append({"stat": "def", "mult": potency, "turnos": default_turns})
        applied.append("def_down")
        add("slow", default_turns, potency)
    if effect.get("reduz_spd_zero"):
        add("slow", effect.get("turnos", 1), 0.90)
    if effect.get("lentidao") or effect.get("lentidao_turnos"):
        add("slow", effect.get("lentidao_turnos") or default_turns, 0.50)

    dot = effect.get("dot")
    if isinstance(dot, dict):
        dot_type = str(dot.get("tipo", "burn")).lower()
        status = "poison" if "venen" in dot_type else "bleed" if "sang" in dot_type else "burn"
        amount = dot.get("dano_matk", dot.get("dano_atk", dot.get("dano", 10)))
        add(status, dot.get("turnos", default_turns), amount)

    if effect.get("dot_matk"):
        raw = float(effect["dot_matk"])
        amount = actor.get_stat("matk") * (raw / 100 if raw > 5 else raw)
        add("poison", default_turns, amount)
    if effect.get("aplica_veneno_atk"):
        add("poison", default_turns, actor.get_stat("atk") * float(effect["aplica_veneno_atk"]))
    if effect.get("veneno_pesado"):
        add("poison", default_turns, actor.get_stat("matk") * float(effect["veneno_pesado"]))
    if effect.get("veneno_fatal_hp_max"):
        add("poison", default_turns, target.max_hp * float(effect["veneno_fatal_hp_max"]) / 100)
    if effect.get("veneno_turnos"):
        add("poison", effect["veneno_turnos"], max(5, actor.get_stat("matk") * 0.40))

    if effect.get("queimadura_fixa"):
        add("burn", default_turns, effect["queimadura_fixa"])
    if effect.get("queimadura_turnos"):
        add("burn", effect["queimadura_turnos"], max(5, actor.get_stat("matk") * 0.40))
    if effect.get("dot_burn_atk"):
        add("burn", default_turns, actor.get_stat("atk") * float(effect["dot_burn_atk"]))

    if effect.get("aplica_sangramento"):
        add("bleed", default_turns, max(5, actor.get_stat("atk") * 0.35))
    if effect.get("chance_sangramento"):
        add(
            "bleed",
            default_turns,
            max(5, actor.get_stat("atk") * 0.35),
            chance=effect["chance_sangramento"],
        )
    if effect.get("chance_bleed"):
        add(
            "bleed",
            default_turns,
            max(5, actor.get_stat("atk") * 0.35),
            chance=effect["chance_bleed"],
        )

    random_effects = effect.get("chance_efeito_aleatorio")
    if isinstance(random_effects, dict):
        roll = random.random()
        cumulative = 0.0
        for status_name, chance in random_effects.items():
            cumulative += float(chance)
            if roll <= cumulative:
                if status_name == "bleed":
                    add("bleed", default_turns, max(5, actor.get_stat("atk") * 0.35))
                elif status_name == "stun":
                    add("stun", 1, ignore_immunity=ignore_cc)
                elif status_name == "reduz_def":
                    target.debuffs.append({"stat": "def", "mult": 0.25, "turnos": default_turns})
                    applied.append("def_down")
                break

    elemental_chance = effect.get("chance_burn_slow_weakness")
    if elemental_chance:
        add("burn", default_turns, max(5, actor.get_stat("matk") * 0.35), chance=elemental_chance)
        add("slow", default_turns, 0.25, chance=elemental_chance)
        add("weakness", default_turns, 0.20, chance=elemental_chance)

    if effect.get("anti_cura"):
        add("anti_heal", default_turns)
    if effect.get("corta_cura"):
        add("healing_cut", default_turns)
    if effect.get("prolonga_stun_inimigo"):
        for status in target.debuffs:
            if status.get("stat") in {"stun", "freeze", "root"} or status.get("stun"):
                status["turnos"] = status.get("turnos", 1) + int(effect["prolonga_stun_inimigo"])
                applied.append("stun")
    if effect.get("remove_todos_buffs"):
        target.buffs = []
        applied.append("buffs_removidos")
    if effect.get("bloqueia_buffs"):
        target.debuffs.append({"stat": "bloqueia_buffs", "turnos": default_turns})
        applied.append("bloqueia_buffs")

    for effect_key, stat_name in [
        ("debuff_atk", "atk"),
        ("debuff_matk", "matk"),
        ("debuff_def", "def"),
        ("debuff_acc", "acc"),
    ]:
        value = effect.get(effect_key)
        if value:
            target.debuffs.append({
                "stat": stat_name,
                "mult": min(0.90, float(value) / 100),
                "turnos": default_turns,
            })
            applied.append(f"{stat_name}_down")
    if effect.get("debuff_geral"):
        value = min(0.90, float(effect["debuff_geral"]) / 100)
        for stat_name in ["atk", "matk", "def", "spd"]:
            target.debuffs.append({"stat": stat_name, "mult": value, "turnos": default_turns})
        applied.append("geral_down")

    return applied


def apply_status_protection(target, effect, turns=3):
    """Aplica imunidades e limpezas de status descritas nas habilidades."""
    if not effect or target.is_dead:
        return []

    changes = []
    if (
        effect.get("remove_debuffs")
        or effect.get("remove_todos_debuffs")
        or effect.get("remove_todos_debuffs_aliados")
        or effect.get("remove_debuffs_pesados")
        or effect.get("remove_debuffs_magicos")
    ):
        if target.remove_statuses():
            changes.append("purificado")
    else:
        removable = set()
        if effect.get("remove_veneno"):
            removable.add("poison")
        if effect.get("remove_burn_veneno"):
            removable.update({"burn", "poison"})
        if effect.get("remove_veneno_burn_bleed"):
            removable.update({"burn", "poison", "bleed"})
        if removable and target.remove_statuses(removable):
            changes.append("purificado")
        if effect.get("remove_1_debuff_aliados") and target.debuffs:
            target.debuffs.pop(0)
            changes.append("purificado")

    immunity = {"stat": "status_immunity", "turnos": max(1, int(turns or 3))}
    immunity_keys = [
        "imune_cc",
        "imunidade_cc",
        "imune_stun",
        "imune_queimadura",
        "imune_toxinas",
        "imunidade_debuffs",
        "imune_debuffs_cc_instakill",
        "imune_lentidao_fraqueza",
        "imune_maldicoes_dot_terreno",
        "imune_medo",
    ]
    for key in immunity_keys:
        if effect.get(key):
            immunity[key] = True
    for key, value in effect.items():
        if value and str(key).startswith("imune_"):
            immunity[key] = True
    if len(immunity) > 2:
        existing_immunity = next(
            (buff for buff in target.buffs if buff.get("stat") == "status_immunity"),
            None,
        )
        if existing_immunity:
            existing_immunity.update(immunity)
            existing_immunity["turnos"] = max(
                existing_immunity.get("turnos", 0),
                immunity["turnos"],
            )
        else:
            target.buffs.append(immunity)
        changes.append("imunidade")

    on_hit_keys = {
        key: effect[key]
        for key in [
            "aplica_veneno_on_hit",
            "burn_matk_100_on_hit",
            "burn_matk_200_on_hit",
            "dot_fogo",
            "chance_lentidao_on_hit",
            "fraqueza_on_hit",
            "marca_alvo_fraqueza_ranged",
            "chance_stun",
            "stun_turnos",
            "criticos_aplicam_paralisia",
            "ataques_fogo",
            "chance_medo_inimigos",
            "ataque_aplica_maldicao",
            "criticos_removem_buff",
            "chance_insta_kill_on_hit",
            "bloqueia_reviver_ao_matar",
            "ignora_def_on_hit",
        ]
        if effect.get(key) is not None
    }
    if on_hit_keys:
        existing_on_hit = next(
            (buff for buff in target.buffs if buff.get("stat") == "on_hit_status"),
            None,
        )
        if existing_on_hit:
            existing_on_hit.update(on_hit_keys)
            existing_on_hit["turnos"] = max(
                existing_on_hit.get("turnos", 0),
                max(1, int(turns or 3)),
            )
        else:
            target.buffs.append({
                "stat": "on_hit_status",
                "turnos": max(1, int(turns or 3)),
                **on_hit_keys,
            })
        changes.append("efeito ao atacar")

    persistent_keys = {
        key: effect[key]
        for key in [
            "revive_hp",
            "revive_hp_max",
            "heal_damage_received",
            "protege_aliados_fatal",
            "reflete_dano",
            "lifesteal_on_hit",
            "counter_atk_percent",
            "barreira_dano_recebido",
            "stun_atacante_on_hit",
        ]
        if effect.get(key) is not None
    }
    if persistent_keys:
        existing_special = next(
            (buff for buff in target.buffs if buff.get("stat") == "combat_special"),
            None,
        )
        if existing_special:
            existing_special.update(persistent_keys)
            existing_special["turnos"] = max(
                existing_special.get("turnos", 0),
                max(1, int(turns or 3)),
            )
        else:
            target.buffs.append({
                "stat": "combat_special",
                "turnos": max(1, int(turns or 3)),
                **persistent_keys,
            })
        changes.append("efeito persistente")

    if effect.get("dot_self"):
        self_dot = {
            "stat": "self_dot",
            "dot_self": max(1, int(effect["dot_self"])),
            "turnos": max(1, int(turns or 3)),
        }
        existing_self_dot = next(
            (buff for buff in target.buffs if buff.get("stat") == "self_dot"),
            None,
        )
        if existing_self_dot:
            existing_self_dot["dot_self"] = max(
                existing_self_dot.get("dot_self", 0),
                self_dot["dot_self"],
            )
            existing_self_dot["turnos"] = max(
                existing_self_dot.get("turnos", 0),
                self_dot["turnos"],
            )
        else:
            target.buffs.append(self_dot)
        changes.append("dano contínuo próprio")
    return changes


def apply_on_hit_statuses(actor, target, critical=False):
    if target.is_dead:
        return []
    applied = []
    for buff in actor.buffs:
        if buff.get("stat") != "on_hit_status":
            continue
        if buff.get("aplica_veneno_on_hit") is not None:
            chance = float(buff["aplica_veneno_on_hit"])
            if chance > 1:
                chance /= 100
            if random.random() <= chance and target.add_status(
                "poison", 3, max(5, actor.get_stat("atk") * 0.35)
            ):
                applied.append("poison")
        if buff.get("burn_matk_100_on_hit") is not None:
            if target.add_status(
                "burn",
                int(buff["burn_matk_100_on_hit"]),
                actor.get_stat("matk"),
            ):
                applied.append("burn")
        if buff.get("burn_matk_200_on_hit") is not None:
            if target.add_status(
                "burn",
                int(buff["burn_matk_200_on_hit"]),
                actor.get_stat("matk") * 2,
            ):
                applied.append("burn")
        if buff.get("dot_fogo") is not None:
            if target.add_status("burn", 2, max(1, int(buff["dot_fogo"]))):
                applied.append("burn")
        if buff.get("chance_lentidao_on_hit") is not None:
            slow_chance = float(buff["chance_lentidao_on_hit"])
            if slow_chance > 1:
                slow_chance /= 100
            if random.random() <= slow_chance and target.add_status(
                "slow", 2, 0.25
            ):
                applied.append("slow")
        weakness = buff.get("fraqueza_on_hit") or buff.get("marca_alvo_fraqueza_ranged")
        if weakness is not None and target.add_status(
            "weakness", 3, float(weakness) / 100
        ):
            applied.append("weakness")
        stun_chance = buff.get("chance_stun")
        if stun_chance is not None:
            stun_chance = float(stun_chance)
            if stun_chance > 1:
                stun_chance /= 100
        if stun_chance is not None and random.random() <= stun_chance:
            if target.add_status("stun", int(buff.get("stun_turnos", 1))):
                applied.append("stun")
        if critical and buff.get("criticos_aplicam_paralisia"):
            if target.add_status("stun", int(buff["criticos_aplicam_paralisia"])):
                applied.append("stun")
        if critical and buff.get("criticos_removem_buff") and target.buffs:
            remove_count = max(1, int(buff.get("criticos_removem_buff") or 1))
            del target.buffs[:remove_count]
            applied.append("buff_removido")
        if buff.get("ataques_fogo"):
            if target.add_status("burn", 2, max(5, actor.get_stat("matk") * 0.30)):
                applied.append("burn")
        fear_chance = buff.get("chance_medo_inimigos")
        if fear_chance is not None:
            fear_chance = float(fear_chance)
            if fear_chance > 1:
                fear_chance /= 100
            if random.random() <= fear_chance and target.add_status("fear", 1):
                applied.append("fear")
        curse_turns = buff.get("ataque_aplica_maldicao")
        if curse_turns is not None:
            if target.add_status(
                "curse",
                int(curse_turns),
                max(5, actor.get_stat("matk") * 0.30),
            ):
                applied.append("curse")
        execute_chance = buff.get("chance_insta_kill_on_hit")
        if execute_chance is not None:
            execute_chance = float(execute_chance)
            if execute_chance > 1:
                execute_chance /= 100
            if random.random() <= execute_chance:
                target.hp = 0
                target.is_dead = True
                if buff.get("bloqueia_reviver_ao_matar"):
                    target.cannot_revive = True
                applied.append("insta_kill")
    return applied


# ==========================================
# CÉREBRO DE COMBATE (O MOTOR)
# ==========================================
class CombatEngine:
    def __init__(self, team_a_data, team_b_data):
        self.team_a = [CombatEntity(f"A{i}", d["nome"], d, False) for i, d in enumerate(team_a_data)]
        self.team_b = [CombatEntity(f"B{i}", d["nome"], d, True) for i, d in enumerate(team_b_data)]
        self.log = []
        self.turn_limit = 150 

    def _get_alive(self, team):
        return [e for e in team if not e.is_dead]

    def _get_team(self, entity):
        return self.team_b if entity.is_enemy else self.team_a

    def _deal_damage(self, actor, target, amount, source_atk, is_magic=False, ignore_def=False):
        previous_hp = target.hp
        dodge = target.get_stat("dodge")
        acc = actor.get_stat("acc")
        if (dodge > 0 or acc < 100) and not ignore_def:
            accuracy_gap = max(0, 100 - acc) - max(0, acc - 100)
            dodge_chance = min(0.85, max(0.0, (dodge + accuracy_gap) / 100))
            if dodge_chance > 0 and random.random() < dodge_chance:
                counter_percent = max(
                    (
                        _as_ratio(buff.get("counter_atk_percent"))
                        for buff in target.buffs
                    ),
                    default=0,
                )
                if counter_percent > 0 and not actor.is_dead:
                    actor.take_damage(
                        max(1, int(target.get_stat("atk") * counter_percent)),
                        target.get_stat("atk"),
                        False,
                        True,
                    )
                return 0

        variance = random.uniform(0.90, 1.10 if actor.is_enemy else 1.07)
        damage = target.take_damage(max(1, int(amount * variance)), source_atk, is_magic, ignore_def)
        if damage > 0:
            reflect_percent = max(
                (
                    _as_ratio(buff.get("reflete_dano"))
                    for buff in target.buffs
                ),
                default=0,
            )
            if reflect_percent > 0 and not actor.is_dead:
                actor.take_damage(max(1, int(damage * reflect_percent)), source_atk, is_magic, True)

            lifesteal_percent = max(
                (
                    _as_ratio(buff.get("lifesteal_on_hit"), 0.40)
                    for buff in actor.buffs
                ),
                default=0,
            )
            if lifesteal_percent > 0 and not actor.is_dead:
                actor.heal(int(damage * lifesteal_percent))

            barrier_percent = max(
                (
                    _as_ratio(buff.get("barreira_dano_recebido"))
                    for buff in target.buffs
                ),
                default=0,
            )
            if barrier_percent > 0 and not target.is_dead:
                target.shield += max(1, int(damage * barrier_percent))

            stun_turns = max(
                (
                    int(buff.get("stun_atacante_on_hit", 0) or 0)
                    for buff in target.buffs
                ),
                default=0,
            )
            if stun_turns > 0 and not actor.is_dead:
                actor.add_status("stun", stun_turns)

        if not target.is_dead:
            return damage

        protector = next(
            (
                ally
                for ally in self._get_alive(self._get_team(target))
                if ally is not target
                and any(buff.get("protege_aliados_fatal") for buff in ally.buffs)
            ),
            None,
        )
        if not protector:
            return damage

        target.is_dead = False
        target.hp = max(1, previous_hp)
        protector.take_damage(max(1, damage), source_atk, is_magic, True)
        return 0

    def _get_target(self, actor, target_type, quantity=1, skill_type=None):
        enemy_team = self.team_b if not actor.is_enemy else self.team_a
        ally_team = self.team_a if not actor.is_enemy else self.team_b
        enemies = self._get_alive(enemy_team)
        allies = self._get_alive(ally_team)
        dead_allies = [e for e in ally_team if e.is_dead]
        quantity = max(1, int(quantity or 1))
        
        if target_type in {"self", "item_contra_si", "adaptativo", "aleatorio"}:
            return [actor]
        if target_type in ["aliado_morto", "aliados_mortos"]:
            return dead_allies[:1] if target_type == "aliado_morto" else dead_allies
        if target_type == "campo":
            if skill_type in {"debuff", "insta_kill"}:
                return enemies
            if skill_type == "dano":
                if quantity > 1:
                    return random.sample(enemies, min(quantity, len(enemies))) if enemies else []
                return enemies
            return allies
        if "inimigo" in target_type and not enemies:
            return []
        if ("aliado" in target_type or target_type == "self") and not allies:
            return []

        if target_type == "unico_inimigo":
            taunters = [e for e in enemies if any(b.get("stat") == "taunt" for b in e.buffs)]
            if taunters: return [random.choice(taunters)]
            
            total_aggro = sum(e.get_aggro() for e in enemies)
            roll = random.uniform(0, total_aggro)
            acumulado = 0
            for e in enemies:
                acumulado += e.get_aggro()
                if roll <= acumulado: return [e]
            return [random.choice(enemies)]
            
        elif target_type == "todos_inimigos":
            return enemies
        elif target_type == "inimigos_aleatorios":
            return random.sample(enemies, min(quantity, len(enemies)))
        elif target_type == "inimigos_maior_dano":
            return sorted(
                enemies,
                key=lambda entity: entity.get_stat("atk") + entity.get_stat("matk"),
                reverse=True,
            )[:quantity]
        elif target_type == "inimigos_travados":
            return random.sample(enemies, min(quantity, len(enemies)))
        elif target_type in ["unico_aliado", "aliado_escolhido"]:
            return [random.choice(allies)]
        elif target_type == "aliado_menor_hp":
            allies.sort(key=lambda x: x.hp / x.max_hp)
            return [allies[0]]
        elif target_type == "todos_aliados":
            return allies
        elif target_type == "lider_aliado":
            return [allies[0]]
        elif target_type in ["dps_aliado", "dps_aliados"]:
            allies.sort(key=lambda x: x.get_stat("atk") + x.get_stat("matk"), reverse=True)
            return allies[:quantity] if target_type == "dps_aliados" else [allies[0]]
        elif target_type == "magos_aliados":
            magos = [ally for ally in allies if ally.classe == "mago"]
            selected = magos or sorted(allies, key=lambda x: x.get_stat("matk"), reverse=True)
            return selected[:quantity]
        elif target_type in {"dps_inimigo", "inimigo_maior_dano"}:
            enemies.sort(key=lambda x: x.get_stat("atk") + x.get_stat("matk"), reverse=True)
            return [enemies[0]]
        elif target_type == "inimigo_maior_spd":
            return [max(enemies, key=lambda x: x.get_stat("spd"))]
        elif target_type == "inimigo_menor_def":
            return [min(enemies, key=lambda x: x.get_stat("def"))]
        elif target_type == "inimigo_menor_hp":
            return [min(enemies, key=lambda x: x.hp / x.max_hp)]
        elif "aleatorio" in target_type:
            if "aliado" in target_type: return [random.choice(allies)]
            return [random.choice(enemies)]
            
        return [random.choice(enemies)]

    def _execute_skill(self, actor, skill_id):
        # Fallback para silenciamento
        if actor.is_silenced():
            log_basico = self._execute_basic_attack(actor)
            return f"🤐 {actor.clean_name} está silenciado(a) e atacou normalmente!\n" + log_basico

        skill_data = SKILLS.get(skill_id)
        if not skill_data: return self._execute_basic_attack(actor)
        
        if "cooldown" in skill_data: actor.cooldowns[skill_id] = skill_data["cooldown"]
        actor.skill_uses[skill_id] = actor.skill_uses.get(skill_id, 0) + 1

        # Busca Quantidade Customizada de Alvos
        qtd_alvos = skill_data.get("quantidade", 1)
        targets = self._get_target(
            actor,
            skill_data.get("alvo", "unico_inimigo"),
            qtd_alvos,
            skill_data.get("tipo"),
        )
        targets = list(dict.fromkeys(targets))
            
        if not targets: return f"❓ **{actor.clean_name}** olhou em volta confuso(a)."

        efeito = skill_data.get("efeito", {})
        log_line = f"✨ **{actor.clean_name}** usou `[{skill_data['nome']}]`!"
        
        nomes_alvos = [t.clean_name for t in list(dict.fromkeys(targets))]
        todos_inimigos = self._get_alive(self.team_b if not actor.is_enemy else self.team_a)
        todos_aliados = self._get_alive(self.team_a if not actor.is_enemy else self.team_b)
        
        targets_str = ""
        if len(nomes_alvos) > 1 and len(nomes_alvos) == len(todos_inimigos) and "inimigo" in skill_data.get("alvo", ""):
            targets_str = "todo o campo inimigo"
        elif len(nomes_alvos) > 1 and len(nomes_alvos) == len(todos_aliados) and "aliado" in skill_data.get("alvo", ""):
            targets_str = "todos os aliados"
        elif len(nomes_alvos) > 1:
            targets_str = ", ".join(nomes_alvos[:-1]) + " e " + nomes_alvos[-1]
        else:
            targets_str = nomes_alvos[0]

        if skill_data["tipo"] in ["dano", "insta_kill"]:
            total_dmg = 0
            is_crit_any = False
            stunned = []
            mortos = []

            for target in targets:
                base_dmg = actor.get_stat("atk") + efeito.get("dano_atk_extra", 0)
                is_magic = False
                
                if "dano_matk_extra" in efeito or "multiplicador_matk" in efeito or "soma_atk_matk" in efeito:
                    base_dmg = actor.get_stat("matk") + efeito.get("dano_matk_extra", 0)
                    is_magic = True
                    
                if efeito.get("soma_atk_matk") or efeito.get("soma_atk_matk_buff") or efeito.get("soma_atk_matk_100"):
                    base_dmg = actor.get_stat("atk") + actor.get_stat("matk")
                
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
                if efeito.get("multiplica_atk_matk"): mult *= efeito.get("multiplica_atk_matk")
                if efeito.get("multiplicador_soma_atk_matk"): mult *= efeito.get("multiplicador_soma_atk_matk")
                
                is_crit = random.randint(1, 100) <= actor.get_stat("crt") or efeito.get("critico_garantido")
                if is_crit: 
                    mult *= 1.5
                    is_crit_any = True
                
                # Dano Baseado em HP
                dano_final = base_dmg * mult
                if "dano_fixo" in efeito:
                    dano_final += int(efeito["dano_fixo"])
                if "dano_hp_atual" in efeito:
                    dano_final += int(target.hp * efeito["dano_hp_atual"])
                if "dano_hp_max" in efeito:
                    dano_final += int(target.max_hp * _as_ratio(efeito["dano_hp_max"]))
                dano_final = actor.cap_outgoing_damage(dano_final, is_skill=True)
                
                persistent_ignore = max(
                    (
                        float(buff.get("ignora_def_on_hit", 0))
                        for buff in actor.buffs
                    ),
                    default=0,
                )
                ignore_def = efeito.get("ignora_def_escudos", False)
                if not ignore_def:
                    ignore_def = efeito.get("ignora_def", False)
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
                    target.shield = 0
                dmg_dealt = self._deal_damage(
                    actor,
                    target,
                    dano_final,
                    base_dmg,
                    is_magic,
                    ignore_def,
                )
                total_dmg += dmg_dealt
                
                t_name = target.clean_name
                statuses = apply_status_effects(actor, target, efeito, dmg_dealt, is_crit)
                statuses.extend(apply_on_hit_statuses(actor, target, is_crit))
                if any(status in {"stun", "freeze", "root"} for status in statuses):
                    if t_name not in stunned:
                        stunned.append(t_name)
                    
                # Insta Kill e Execuções
                trigger_kill = False
                if "chance_insta_kill" in efeito and random.random() <= efeito["chance_insta_kill"]: trigger_kill = True
                elif "executa_abaixo_50" in efeito and target.hp <= target.max_hp * 0.50: trigger_kill = True
                elif efeito.get("insta_kill_on_hit_garantido"): trigger_kill = True
                elif efeito.get("executa_abaixo_percent") and target.hp <= target.max_hp * (efeito["executa_abaixo_percent"] / 100):
                    trigger_kill = True
                
                if trigger_kill and not target.is_dead:
                    target.hp = 0
                    target.is_dead = True
                    if any(buff.get("bloqueia_reviver_ao_matar") for buff in actor.buffs):
                        target.cannot_revive = True
                    if t_name not in mortos: mortos.append(f"{t_name} (Insta-Kill)")
                elif target.is_dead:
                    if any(buff.get("bloqueia_reviver_ao_matar") for buff in actor.buffs):
                        target.cannot_revive = True
                    if t_name not in mortos: mortos.append(t_name)

            avg_dmg = int(total_dmg / len(targets)) if targets else 0
            crit_str = " (💥)" if is_crit_any else ""
            
            log_line += f"\n⚔️ Atingiu **{targets_str}** causando **{avg_dmg}** de dano{crit_str}."

            # Roubo de Vida / Lifesteal
            if "lifesteal" in efeito and total_dmg > 0:
                cura = actor.heal(int(total_dmg * efeito["lifesteal"]))
                log_line += f"\n🦇 Sugou **{cura} HP**!"
            if "lifesteal_global" in efeito and total_dmg > 0:
                cura = actor.heal(int(total_dmg * efeito["lifesteal_global"]))
                log_line += f"\n🦇 Devorou **{cura} HP** da arena!"

            if stunned: log_line += f"\n💫 **{', '.join(stunned)}** foi atordoado!"
            if mortos: log_line += f"\n☠️ **{', '.join(mortos)} caiu em batalha!**"
                
        elif skill_data["tipo"] in ["cura", "reviver"]:
            total_healed = 0
            for target in targets:
                if target.is_dead and not target.cannot_revive and (skill_data["tipo"] == "reviver" or "reviver" in str(efeito)):
                    target.is_dead = False
                    target.hp = int(target.max_hp * efeito.get("hp_percent", 0.5))
                    total_healed += target.hp
                elif not target.is_dead:
                    heal_amount = efeito.get("cura_fixa", 0)
                    if "cura_percent_max" in efeito: heal_amount += int(target.max_hp * efeito["cura_percent_max"])
                    if "cura_percent_max_time" in efeito: heal_amount += int(target.max_hp * efeito["cura_percent_max_time"])
                    if "multiplicador_matk" in efeito: heal_amount += int(actor.get_stat("matk") * efeito["multiplicador_matk"])
                    healed = target.heal(heal_amount)
                    total_healed += healed
            
                if "remove_debuffs" in efeito or "remove_todos_debuffs" in efeito:
                    target.debuffs = []
                apply_status_protection(target, efeito, efeito.get("turnos", 3))
                turnos = efeito.get("turnos", 3)
                buffs_blocked = any(debuff.get("stat") == "bloqueia_buffs" for debuff in target.debuffs)
                if not buffs_blocked:
                    if "buff_atk" in efeito:
                        target.buffs.append({"stat": "atk", "mult": efeito["buff_atk"] / 100.0, "turnos": turnos})
                    if "buff_matk" in efeito:
                        target.buffs.append({"stat": "matk", "mult": efeito["buff_matk"] / 100.0, "turnos": turnos})
                    if "buff_def" in efeito:
                        target.buffs.append({"stat": "def", "mult": efeito["buff_def"] / 100.0, "turnos": turnos})
                    if "buff_spd" in efeito:
                        target.buffs.append({"stat": "spd", "mult": efeito["buff_spd"] / 100.0, "turnos": turnos})
                    if "buff_acc" in efeito:
                        target.buffs.append({"stat": "acc", "flat": efeito["buff_acc"], "turnos": turnos})
                    if "buff_crt" in efeito:
                        target.buffs.append({"stat": "crt", "flat": efeito["buff_crt"], "turnos": turnos})
                if "reduz_cooldown" in efeito:
                    amount = max(1, int(efeito["reduz_cooldown"]))
                    for skill_id in list(target.cooldowns.keys()):
                        target.cooldowns[skill_id] -= amount
                        if target.cooldowns[skill_id] <= 0:
                            del target.cooldowns[skill_id]
            
            avg_heal = int(total_healed / len(targets)) if targets else 0
            log_line += f"\n💚 Restaurou **{targets_str}** em aprox. **{avg_heal} HP**."

        elif skill_data["tipo"] in ["buff", "debuff", "escudo", "especial", "passiva", "invocacao"]:
            if efeito.get("efeito_aleatorio_divino"):
                roll = random.choice(["cura", "escudo", "poder"])
                if roll == "cura":
                    for ally in targets:
                        ally.heal(ally.max_hp)
                    log_line += "\n✨ A realidade escolheu restaurar completamente o grupo."
                elif roll == "escudo":
                    for ally in targets:
                        ally.buffs.append({"stat": "imune", "imune_all": True, "turnos": 1})
                    log_line += "\n🛡️ A realidade tornou o grupo intocável nesta rodada."
                else:
                    for ally in targets:
                        for stat_name in ["atk", "matk", "def", "spd"]:
                            ally.buffs.append({"stat": stat_name, "mult": 0.40, "turnos": 3})
                    log_line += "\n🌌 A realidade fortaleceu violentamente todo o grupo."
                return log_line

            for target in targets:
                turnos = efeito.get("turnos", 3)
                if efeito.get("duracao") == "combate_inteiro" or turnos == -1: turnos = 99
                buffs_blocked = any(debuff.get("stat") == "bloqueia_buffs" for debuff in target.debuffs)
                
                # Buffs Ofensivos/Defensivos
                if "buff_atk" in efeito and not buffs_blocked: target.buffs.append({"stat": "atk", "mult": efeito["buff_atk"]/100.0, "turnos": turnos})
                if "buff_matk" in efeito and not buffs_blocked: target.buffs.append({"stat": "matk", "mult": efeito["buff_matk"]/100.0, "turnos": turnos})
                if "buff_def" in efeito and not buffs_blocked: target.buffs.append({"stat": "def", "mult": efeito["buff_def"]/100.0, "turnos": turnos})
                if "buff_spd" in efeito and not buffs_blocked: target.buffs.append({"stat": "spd", "mult": efeito["buff_spd"]/100.0, "turnos": turnos})
                if "buff_crt" in efeito and not buffs_blocked: target.buffs.append({"stat": "crt", "flat": efeito["buff_crt"], "turnos": turnos})
                if "buff_acc" in efeito and not buffs_blocked: target.buffs.append({"stat": "acc", "flat": efeito["buff_acc"], "turnos": turnos})
                if "buff_dodge" in efeito and not buffs_blocked: target.buffs.append({"stat": "dodge", "flat": efeito["buff_dodge"], "turnos": turnos})
                if "buff_geral" in efeito and not buffs_blocked:
                    for st in ["atk", "def", "spd", "matk"]: target.buffs.append({"stat": st, "mult": efeito["buff_geral"]/100.0, "turnos": turnos})
                if "buff_hp" in efeito:
                    ganho_hp = int(target.max_hp * (efeito["buff_hp"] / 100.0))
                    target.max_hp += ganho_hp
                    target.hp += ganho_hp
                if "buff_hp_temporario" in efeito:
                    ganho_hp = int(efeito["buff_hp_temporario"])
                    target.max_hp += ganho_hp
                    target.hp += ganho_hp
                if "multiplicador_dano_atk" in efeito:
                    target.buffs.append({"stat": "atk", "mult": efeito["multiplicador_dano_atk"] - 1, "turnos": turnos})
                if "multiplica_atk_matk" in efeito:
                    mult_extra = efeito["multiplica_atk_matk"] - 1
                    target.buffs.append({"stat": "atk", "mult": mult_extra, "turnos": turnos})
                    target.buffs.append({"stat": "matk", "mult": mult_extra, "turnos": turnos})
                if "multiplica_spd" in efeito:
                    target.buffs.append({"stat": "spd", "mult": efeito["multiplica_spd"] - 1, "turnos": turnos})
                if "cura_turnos" in efeito:
                    target.buffs.append({"stat": "regen", "regen": efeito["cura_turnos"], "turnos": turnos})
                if "reduz_dano_recebido" in efeito:
                    target.buffs.append({
                        "stat": "damage_reduction",
                        "reduz_dano_recebido": efeito["reduz_dano_recebido"],
                        "turnos": turnos,
                    })
                if "buff_atk_por_inimigo_vivo" in efeito and not buffs_blocked:
                    enemy_team = self.team_b if not actor.is_enemy else self.team_a
                    bonus = efeito["buff_atk_por_inimigo_vivo"] * len(self._get_alive(enemy_team))
                    target.buffs.append({"stat": "atk", "mult": bonus / 100.0, "turnos": turnos})
                if "reduz_cooldown" in efeito:
                    amount = max(1, int(efeito["reduz_cooldown"]))
                    for skill_id in list(target.cooldowns.keys()):
                        target.cooldowns[skill_id] -= amount
                        if target.cooldowns[skill_id] <= 0:
                            del target.cooldowns[skill_id]
                
                # Imunidades e Escudos Reais
                if "imortalidade_turnos" in efeito: target.buffs.append({"stat": "imortal", "imortal": True, "turnos": efeito["imortalidade_turnos"]})
                if "imunidade_dano_turnos" in efeito: target.buffs.append({"stat": "imune", "imune_all": True, "turnos": turnos})
                if "ignora_dano_fisico" in efeito: target.buffs.append({"stat": "imune", "imune_fisico": True, "turnos": turnos})
                if "ignora_dano_magico" in efeito: target.buffs.append({"stat": "imune", "imune_magico": True, "turnos": turnos})
                
                if "escudo_hp_max" in efeito:
                    if not buffs_blocked:
                        target.shield += int(target.max_hp * efeito["escudo_hp_max"])
                if "aggro_max" in efeito or "taunt" in str(efeito):
                    target.buffs.append({"stat": "taunt", "turnos": turnos})
                
                # Debuffs Ofensivos/Defensivos
                if "debuff_atk" in efeito: target.debuffs.append({"stat": "atk", "mult": efeito["debuff_atk"]/100.0, "turnos": turnos})
                if "debuff_matk" in efeito: target.debuffs.append({"stat": "matk", "mult": efeito["debuff_matk"]/100.0, "turnos": turnos})
                if "debuff_def" in efeito: target.debuffs.append({"stat": "def", "mult": efeito["debuff_def"]/100.0, "turnos": turnos})
                if "debuff_geral" in efeito:
                    for st in ["atk", "def", "spd", "matk"]: target.debuffs.append({"stat": st, "mult": efeito["debuff_geral"]/100.0, "turnos": turnos})
                if efeito.get("remove_todos_buffs"):
                    target.buffs = []
                if efeito.get("bloqueia_buffs"):
                    target.debuffs.append({"stat": "bloqueia_buffs", "turnos": turnos})
                
                if "reduz_aggro" in efeito: target.debuffs.append({"stat": "reduz_aggro", "turnos": turnos})
                if target.is_enemy != actor.is_enemy:
                    apply_status_effects(actor, target, efeito)
                else:
                    apply_status_protection(target, efeito, turnos)

            if efeito.get("stun_inimigo_principal"):
                enemy_team = self.team_b if not actor.is_enemy else self.team_a
                enemies = self._get_alive(enemy_team)
                if enemies:
                    max(enemies, key=lambda enemy: enemy.get_stat("atk") + enemy.get_stat("matk")).add_status(
                        "stun",
                        efeito["stun_inimigo_principal"],
                    )
            if efeito.get("silence_todos_inimigos"):
                enemy_team = self.team_b if not actor.is_enemy else self.team_a
                for enemy in self._get_alive(enemy_team):
                    enemy.add_status("silence", efeito["silence_todos_inimigos"])
            if efeito.get("stun_curador_inimigo"):
                enemy_team = self.team_b if not actor.is_enemy else self.team_a
                enemies = self._get_alive(enemy_team)
                healers = [enemy for enemy in enemies if enemy.classe in {"suporte", "curandeiro"}]
                if healers:
                    random.choice(healers).add_status("stun", efeito["stun_curador_inimigo"])

            # Logs Dinâmicos de Controle
            if "escudo_hp_max" in efeito: log_line += f"\n🛡️ Bastião impenetrável concedido a **{targets_str}**!"
            elif "silence_turnos" in efeito: log_line += f"\n🤐 **{targets_str}** foi silenciado(a)!"
            elif "anti_cura" in efeito: log_line += f"\n☠️ **{targets_str}** teve a cura anulada!"
            elif skill_data["tipo"] in ["buff", "passiva"]: log_line += f"\n📈 Os atributos de **{targets_str}** aumentaram."
            elif skill_data["tipo"] == "debuff": log_line += f"\n📉 Ameaça lançada sobre **{targets_str}**."
            else: log_line += f"\n🌀 O campo de batalha em volta de **{targets_str}** foi alterado."

        return log_line

    def _execute_basic_attack(self, actor):
        targets = self._get_target(actor, "unico_inimigo")
        if not targets: return ""
        target = targets[0]
        
        is_crit = random.randint(1, 100) <= actor.get_stat("crt")
        dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
        
        ignore_def = max(
            (
                float(buff.get("ignora_def_on_hit", 0))
                for buff in actor.buffs
            ),
            default=0,
        )
        dmg_dealt = self._deal_damage(
            actor,
            target,
            dmg,
            actor.get_stat("atk"),
            False,
            ignore_def,
        )
        apply_on_hit_statuses(actor, target, is_crit)
        crit_str = " (💥)" if is_crit else ""
        
        log_line = f"🗡️ **{actor.clean_name}** atacou **{target.clean_name}** causando **{dmg_dealt}**{crit_str} de dano."
        if target.is_dead:
            log_line += f"\n☠️ **{target.clean_name} caiu em batalha!**"
            
        return log_line

    def run_battle(self):
        battle_summary = []
        
        while self.turn_limit > 0:
            alive_a = self._get_alive(self.team_a)
            alive_b = self._get_alive(self.team_b)
            
            if not alive_a: return False, self._format_log(battle_summary, "☠️ DERROTA ESMAGADORA")
            if not alive_b: return True, self._format_log(battle_summary, "🏆 VITÓRIA GLORIOSA")

            all_alive = alive_a + alive_b
            all_alive.sort(key=lambda x: x.action_value)
            
            actor = all_alive[0]
            
            time_passed = actor.action_value
            for e in all_alive: e.action_value -= time_passed

            if not actor.is_stunned():
                allies = self.team_b if actor.is_enemy else self.team_a
                enemies = self.team_a if actor.is_enemy else self.team_b
                skill_id = choose_combat_skill(actor, SKILLS, allies, enemies)
                skill_usada = skill_id is not None
                if skill_usada:
                    action_log = self._execute_skill(actor, skill_id)
                
                if not skill_usada:
                    action_log = self._execute_basic_attack(actor)
                    
                if "✨" in action_log or "☠️" in action_log or "💥" in action_log or "🗡️" in action_log:
                    battle_summary.append(action_log)
            else:
                battle_summary.append(f"💫 **{actor.clean_name}** está atordoado e perdeu a vez.")

            dot_logs = actor.tick_effects()
            battle_summary.extend(dot_logs)

            actor.action_value += 10000 / max(1, actor.get_stat("spd"))
            self.turn_limit -= 1

        return False, self._format_log(battle_summary, "⏳ LIMITE DE TURNOS ALCANÇADO. EXAUSTÃO.")

    def _format_log(self, logs, title):
        if not logs: return f"{title}\nNenhuma ação notável aconteceu."
        
        if len(logs) > 8:
            final_log = "\n".join(logs[:3]) + "\n\n*(... a batalha foi intensa ...)*\n\n" + "\n".join(logs[-3:])
        else:
            final_log = "\n\n".join(logs)
            
        result = f"{title}\n\n{final_log}"
        
        if len(result) > 1024:
            result = result[:1021] + "..."
            
        return result

def simular_combate_tatico(team_a_dicts, team_b_dicts, return_state=False):
    engine = CombatEngine(team_a_dicts, team_b_dicts)
    vitoria, log_str = engine.run_battle()
    
    if return_state:
        state = {e.id: e.hp for e in engine.team_a if not e.is_dead}
        return vitoria, log_str, state
        
    return vitoria, log_str
