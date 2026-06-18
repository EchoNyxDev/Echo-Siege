import discord
from discord.ext import commands
import sqlite3
import random
import os
import sys
import time
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from data.heroes import HEROES
    from data.enemies import ENEMIES
    from data.habilidades import SKILLS
    from data.equipamentos import EQUIPAMENTOS
    from utils.combat import CombatEntity, _as_ratio, apply_on_hit_statuses, apply_status_effects, apply_status_protection, choose_ai_combat_skill, choose_combat_skill
    from utils.xp_system import dar_xp_jogador, dar_xp_heroi
    from utils.skills import get_hero_skill_ids
    from utils.hero_stats import calculate_hero_stats, normalize_class
    from utils.rewards import arena_floor_rewards
    from utils.equipment import get_equipment_bonus
    from utils.affinity import apply_affinity_bonus
    from utils.player_bonuses import apply_reward_bonuses, has_arena_auto, apply_battle_hp_bonus
except ModuleNotFoundError:
    HEROES, ENEMIES, EQUIPAMENTOS, SKILLS = {}, {}, {}, {}
    def get_hero_skill_ids(hero_data, stars=1, rarity=None):
        habilidade = hero_data.get("habilidade") if hero_data else None
        return [habilidade] if habilidade else []
    def get_equipment_bonus(cursor, user_id, item_name, equipamentos):
        return equipamentos.get(item_name, {}) if item_name in equipamentos else {}
    def apply_affinity_bonus(party_data, heroes):
        return party_data
    def apply_reward_bonuses(cursor, user_id, gold=0, xp=0):
        return gold, xp
    def has_arena_auto(cursor, user_id):
        return False
    def apply_battle_hp_bonus(cursor, user_id, party_data):
        return party_data
    def apply_status_effects(actor, target, effect, damage_dealt=0, critical=False):
        return []
    def apply_status_protection(target, effect, turns=3):
        return []
    def apply_on_hit_statuses(actor, target, critical=False):
        return []
    def _as_ratio(value, default_when_true=0.0):
        if value is True:
            return float(default_when_true)
        if value in (None, False):
            return 0.0
        try:
            ratio = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, ratio / 100 if ratio > 1 else ratio)
    def choose_combat_skill(actor, skills=None, allies=None, enemies=None):
        available = [skill_id for skill_id in actor.habilidades if skill_id in (skills or {}) and skill_id not in actor.cooldowns]
        return random.choice(available) if available else None
    def choose_ai_combat_skill(actor, skills=None, allies=None, enemies=None, skill_chance=0.62):
        return choose_combat_skill(actor, skills, allies, enemies) if random.random() <= skill_chance else None
    def calculate_hero_stats(hero_data, stars=1, level=1, equipment_bonuses=None):
        return {"hp": 100, "atk": 10, "matk": 10, "def": 5, "spd": 10, "crt": 5, "level": level}
    def normalize_class(value):
        return str(value or "neutro").lower()
    def arena_floor_rewards(floor):
        return 8, 5

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
# VIEW DO COMBATE DA ARENA
# ==========================================
class ArenaBattleView(discord.ui.View):
    def __init__(self, ctx, party_data):
        super().__init__(timeout=600) # 10 min
        self.ctx = ctx
        self.party_data = party_data
        
        self.andar_atual = 1
        self.andar_maximo = None
        self.gold_acumulado = 0
        self.xp_acumulado = 0
        
        self.team_a = [CombatEntity(f"A{i}", d["nome"], d, False) for i, d in enumerate(party_data)]
        self.team_b = []
        
        self.log_display = ["🏰 **Os portões se fecham.** A arena exige sangue."]
        self.current_actor = None
        self.message = None
        self.turn_queue = [] # NOVA FILA DE TURNOS (Round-Robin Justo)

    async def iniciar_andar(self, interaction=None):
        inimigos_comuns = [k for k, v in ENEMIES.items() if v.get("tipo", "comum") == "comum"]
        if not inimigos_comuns: inimigos_comuns = ["goblin_guerreiro"]
        
        ini_id = random.choice(inimigos_comuns)
        ini_base = ENEMIES.get(ini_id, {})
        
        # Progressao infinita: cresce firme, mas sem saltos que matem runs boas de repente.
        hp_calc = 180 + int((self.andar_atual ** 1.24) * 42)
        atk_calc = 24 + int((self.andar_atual ** 1.12) * 6)
        def_calc = 10 + int((self.andar_atual ** 1.08) * 3)
        spd_calc = 12 + min(80, self.andar_atual // 6)
        crt_calc = min(45, 5 + (self.andar_atual // 12))
        
        boss_stats = {
            "hp": hp_calc,
            "atk": atk_calc,
            "def": def_calc,
            "matk": atk_calc,
            "spd": spd_calc if 'spd_calc' in locals() else spd_calc,
            "crt": crt_calc, 
            "habilidades": [ini_base.get("habilidade")] if ini_base.get("habilidade") else [],
            "classe": ini_base.get("tipo", "comum")
        }
        
        self.team_b = [CombatEntity("B0", f"Gladiador {ini_base.get('nome', 'Inimigo')} (Lv {self.andar_atual})", boss_stats, True)]
        self.log_display.append(f"⚔️ **Andar {self.andar_atual}:** {self.team_b[0].clean_name} surgiu nas sombras!")
        
        self.turn_queue = [] # Reseta a fila ao mudar de andar
        await self.processar_fila(interaction)

    def _get_alive(self, team):
        return [e for e in team if not e.is_dead]

    def _get_target_aggro(self, vivos):
        total_aggro = sum(e.get_aggro() for e in vivos)
        roll = random.uniform(0, total_aggro)
        acumulado = 0
        for e in vivos:
            acumulado += e.get_aggro()
            if roll <= acumulado: return e
        return vivos[0]

    def _roll_damage_variance(self, actor, amount):
        high = 1.10 if actor.is_enemy else 1.07
        return max(1, int(amount * random.uniform(0.90, high)))

    def _gerar_timeline(self, todos_vivos):
        if not hasattr(self, 'turn_queue'):
            self.turn_queue = []
            
        fila = [e for e in self.turn_queue if not e.is_dead]
        
        # Se a fila atual tiver menos de 4 personagens, pegamos do próximo round para preencher a visualização
        if len(fila) < 4:
            proximo_round = sorted(todos_vivos, key=lambda x: (x.get_stat("spd"), 0 if x.is_enemy else 1), reverse=True)
            for e in proximo_round:
                if not e.is_dead:
                    fila.append(e)
                    if len(fila) >= 4:
                        break
        
        nomes = [e.clean_name for e in fila[:4]]
        return " ⏭️ ".join(nomes)

    async def _atualizar_mensagem(self, interaction):
        embed = discord.Embed(title=f"🏰 Torre da Arena - Andar {self.andar_atual}", color=discord.Color.blue())
        
        aliados_txt = "\n".join([f"{e.clean_name}: **{e.hp}/{e.max_hp}**" for e in self.team_a])
        inimigos_txt = "\n".join([f"{e.clean_name}: **{e.hp}/{e.max_hp}**" for e in self.team_b])
        
        embed.add_field(name="Sua Equipe", value=aliados_txt, inline=True)
        embed.add_field(name="Inimigo", value=inimigos_txt, inline=True)
        
        todos_vivos = self._get_alive(self.team_a) + self._get_alive(self.team_b)
        embed.add_field(name="Fila de Ação", value=self._gerar_timeline(todos_vivos), inline=False)
        
        log_txt = "\n".join(self.log_display[-6:])
        embed.add_field(name="📜 Acontecimentos", value=f"```{log_txt}```", inline=False)

        if self.current_actor and not self.current_actor.is_enemy:
            embed.description = f"🟢 **SEU TURNO!** O que **{self.current_actor.clean_name}** deve fazer?"
        else:
            embed.description = "⏳ Oponentes a processar..."
        
        if interaction:
            try: await interaction.response.edit_message(embed=embed, view=self)
            except discord.errors.InteractionResponded: await interaction.message.edit(embed=embed, view=self)
        else:
            self.message = await self.ctx.send(embed=embed, view=self)

    # ==========================================
    # LÓGICA DE HABILIDADES
    # ==========================================
    def _executar_habilidade(self, actor, skill_id):
        if actor.is_silenced():
            target = self._get_target_aggro(self._get_alive(self.team_b if not actor.is_enemy else self.team_a))
            dealt = target.take_damage(self._roll_damage_variance(actor, actor.get_stat("atk")), actor.get_stat("atk"))
            return f"🤐 {actor.clean_name} está silenciado e atacou {target.clean_name} por **{dealt}**."

        s_data = SKILLS.get(skill_id)
        if not s_data: 
            target = self._get_target_aggro(self._get_alive(self.team_b if not actor.is_enemy else self.team_a))
            is_crit = random.randint(1, 100) <= actor.get_stat("crt")
            dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
            dealt = target.take_damage(self._roll_damage_variance(actor, dmg), actor.get_stat("atk"))
            crit_str = " (💥)" if is_crit else ""
            return f"🗡️ {actor.clean_name} atacou {target.clean_name} por **{dealt}**{crit_str}."

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
        elif ("aleatorio" in alvo_req) and inimigos: targets = [random.choice(inimigos)]
        
        if not targets:
            if alvo_req != "self": targets = inimigos
            if not targets: return f"❓ {actor.clean_name} falhou a magia. Nenhum alvo."

        log_line = f"✨ **{actor.clean_name}** usou `[{s_data['nome']}]`!"
        
        total_dmg = 0
        total_healed = 0
        mortos = []
        stunned = []
        
        for t in targets:
            if tipo in ["dano", "insta_kill", "especial"] and t.is_enemy != actor.is_enemy:
                is_magic = "matk" in str(efeito)
                base = actor.get_stat("matk") if is_magic else actor.get_stat("atk")
                if efeito.get("soma_atk_matk") or efeito.get("soma_atk_matk_buff") or efeito.get("soma_atk_matk_100"):
                    base = actor.get_stat("atk") + actor.get_stat("matk")
                dano_bruto = base + efeito.get("dano_atk_extra", 0) + efeito.get("dano_matk_extra", 0)
                
                mult = efeito.get("multiplicador_hit", 1) * efeito.get("multiplicador_atk", 1.0) * efeito.get("multiplicador_matk", 1.0)
                if efeito.get("multiplica_atk_matk"): mult *= efeito.get("multiplica_atk_matk")
                if efeito.get("multiplicador_soma_atk_matk"): mult *= efeito.get("multiplicador_soma_atk_matk")
                
                is_crit = random.randint(1, 100) <= actor.get_stat("crt") or efeito.get("critico_garantido", False)
                if is_crit: mult *= 1.5
                
                dano_final = dano_bruto * mult
                if "dano_fixo" in efeito:
                    dano_final += int(efeito["dano_fixo"])
                if "dano_hp_atual" in efeito:
                    dano_final += int(t.hp * _as_ratio(efeito["dano_hp_atual"]))
                if "dano_hp_max" in efeito:
                    dano_final += int(t.max_hp * _as_ratio(efeito["dano_hp_max"]))
                dano_final = actor.cap_outgoing_damage(dano_final, is_skill=True)
                dano_final = self._roll_damage_variance(actor, dano_final)

                ignore_def = efeito.get("ignora_def_escudos", False) or efeito.get("ignora_def", False)
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

                dealt = t.take_damage(dano_final, base, is_magic=is_magic, ignore_def=ignore_def)
                total_dmg += dealt
                
                statuses = apply_status_effects(actor, t, efeito, dealt)
                statuses.extend(apply_on_hit_statuses(actor, t, is_crit))
                if any(status in {"stun", "freeze", "root"} for status in statuses):
                    stunned.append(t.clean_name)
                    
                if ("chance_insta_kill" in efeito and random.random() <= efeito["chance_insta_kill"]) or efeito.get("insta_kill_on_hit_garantido"):
                    if not t.is_dead:
                        t.hp = 0; t.is_dead = True
                        mortos.append(t.clean_name)
                elif t.is_dead:
                    mortos.append(t.clean_name)

            if tipo in ["cura", "reviver", "especial"] and t.is_enemy == actor.is_enemy:
                if t.is_dead and (tipo == "reviver" or "reviver_aliado" in str(efeito)):
                    t.is_dead = False
                    t.hp = int(t.max_hp * efeito.get("hp_percent", 0.5))
                    total_healed += t.hp
                elif not t.is_dead:
                    cura = efeito.get("cura_fixa", 0)
                    if "cura_percent_max" in efeito: cura += int(t.max_hp * efeito["cura_percent_max"])
                    if "multiplicador_matk" in efeito: cura += int(actor.get_stat("matk") * efeito["multiplicador_matk"])
                    if cura == 0 and tipo == "cura": cura = int(actor.get_stat("matk") * 0.5) 
                    total_healed += t.heal(cura)
                apply_status_protection(t, efeito, efeito.get("turnos", 3))
                
            if tipo in ["buff", "escudo", "passiva", "especial"] and not t.is_dead:
                turnos = efeito.get("turnos", 3)
                if efeito.get("duracao") == "combate_inteiro": turnos = 99
                
                if "buff_atk" in efeito: t.buffs.append({"stat": "atk", "mult": efeito["buff_atk"]/100.0, "turnos": turnos})
                if "buff_matk" in efeito: t.buffs.append({"stat": "matk", "mult": efeito["buff_matk"]/100.0, "turnos": turnos})
                if "buff_def" in efeito: t.buffs.append({"stat": "def", "mult": efeito["buff_def"]/100.0, "turnos": turnos})
                if "buff_spd" in efeito: t.buffs.append({"stat": "spd", "mult": efeito["buff_spd"]/100.0, "turnos": turnos})
                if "buff_crt" in efeito: t.buffs.append({"stat": "crt", "flat": efeito["buff_crt"], "turnos": turnos})
                if "buff_geral" in efeito:
                    for st in ["atk", "def", "spd", "matk"]: t.buffs.append({"stat": st, "mult": efeito["buff_geral"]/100.0, "turnos": turnos})
                
                if "imortalidade_turnos" in efeito: t.buffs.append({"stat": "imortal", "imortal": True, "turnos": efeito["imortalidade_turnos"]})
                if "imunidade_dano_turnos" in efeito: t.buffs.append({"stat": "imune", "imune_all": True, "turnos": turnos})
                if "ignora_dano_fisico" in efeito: t.buffs.append({"stat": "imune", "imune_fisico": True, "turnos": turnos})
                if "ignora_dano_magico" in efeito: t.buffs.append({"stat": "imune", "imune_magico": True, "turnos": turnos})
                apply_status_protection(t, efeito, turnos)
                
            if tipo in ["debuff", "especial"] and t.is_enemy != actor.is_enemy and not t.is_dead:
                turnos = efeito.get("turnos", 2)
                if "debuff_def" in efeito: t.debuffs.append({"stat": "def", "mult": efeito["debuff_def"]/100.0, "turnos": turnos})
                if "zera_defesa_inimiga" in efeito: t.debuffs.append({"stat": "def", "mult": 1.0, "turnos": turnos})
                if "reduz_spd_zero" in efeito: t.debuffs.append({"stat": "spd", "mult": 0.99, "turnos": 1})
                apply_status_effects(actor, t, efeito)

        alvos_nome = ", ".join([t.clean_name for t in targets]) if len(targets) <= 2 else "o campo inimigo" if "inimigo" in alvo_req else "os aliados"
        
        if tipo in ["dano", "insta_kill"] or total_dmg > 0:
            avg = total_dmg // len(targets) if targets else 0
            log_line += f"\n⚔️ Atingiu **{alvos_nome}** por **{avg}** de dano!"
            if stunned: log_line += f"\n💫 **{', '.join(stunned)}** atordoado!"
            if mortos: log_line += f"\n☠️ **{', '.join(mortos)}** caiu!"
        elif tipo == "cura" or total_healed > 0:
            avg = total_healed // len(targets) if targets else 0
            log_line += f"\n💚 Curou **{alvos_nome}** em aprox. **{avg} HP**!"
        elif tipo in ["buff", "escudo", "passiva"]:
            log_line += f"\n🛡️ O status de **{alvos_nome}** aumentou!"
        elif tipo == "debuff":
            log_line += f"\n🌀 Ameaça lançada sobre **{alvos_nome}**!"
        elif tipo == "reviver":
            log_line += f"\n👼 O milagre da vida agiu em **{alvos_nome}**!"

        return log_line

    def _ia_inimigo_agir(self, actor):
        vivos_a = self._get_alive(self.team_a)
        if not vivos_a: return ""
        
        skill_usar = choose_ai_combat_skill(actor, SKILLS, self.team_b, self.team_a)
                
        if skill_usar:
            return self._executar_habilidade(actor, skill_usar)
            
        target = self._get_target_aggro(vivos_a)
        is_crit = random.randint(1, 100) <= actor.get_stat("crt")
        dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
        dealt = target.take_damage(self._roll_damage_variance(actor, dmg), actor.get_stat("atk"))
        apply_on_hit_statuses(actor, target, is_crit)
        crit = " (💥)" if is_crit else ""
        return f"🗡️ {actor.clean_name} atacou {target.clean_name} por **{dealt}**{crit}."

    # ==========================================
    # GESTÃO DE TURNOS
    # ==========================================
    async def processar_fila(self, interaction):
        self.clear_items()
        
        while True:
            vivos_a = self._get_alive(self.team_a)
            vivos_b = self._get_alive(self.team_b)
            
            if not vivos_a: return await self.fim_de_jogo(interaction, venceu=False)
            if not vivos_b: return await self.andar_limpo(interaction)

            all_alive = vivos_a + vivos_b
            
            # Limpa personagens que morreram da fila de espera
            if hasattr(self, 'turn_queue'):
                self.turn_queue = [e for e in self.turn_queue if not e.is_dead]
            else:
                self.turn_queue = []

            # SE A FILA ACABOU (Fim do Round), gera um novo round baseado em Velocidade
            if not self.turn_queue:
                self.turn_queue = sorted(all_alive, key=lambda x: (x.get_stat("spd"), 0 if x.is_enemy else 1), reverse=True)

            # Pega o próximo da fila! Ele não volta pra fila neste round.
            actor = self.turn_queue.pop(0)

            # DoTs e Redução de Cooldown acontecem apenas no turno do personagem
            estava_atordoado = actor.is_stunned()
            dot_logs = actor.tick_effects()
            self.log_display.extend(dot_logs)

            if estava_atordoado:
                self.log_display.append(f"💫 {actor.clean_name} está atordoado e perdeu a vez!")
                continue 

            self.current_actor = actor

            if actor.is_enemy:
                log_acao = self._ia_inimigo_agir(actor)
                self.log_display.append(log_acao)
                continue 
            else:
                # TURNO DO JOGADOR
                self.add_item(ButtonAtacar(self))
                
                available_skills = [
                    skill_id
                    for skill_id in actor.habilidades
                    if skill_id in SKILLS and skill_id not in actor.cooldowns
                ]
                has_skill = bool(available_skills)
                skill_nome = "Habilidade"
                if len(available_skills) == 1:
                    skill_nome = SKILLS[available_skills[0]].get("nome", "Habilidade")
                elif len(available_skills) > 1:
                    skill_nome = f"Habilidade ({len(available_skills)} opções)"
                
                self.add_item(ButtonHabilidade(self, skill_nome, not has_skill))
                self.add_item(ButtonDefender(self))
                
                await self._atualizar_mensagem(interaction)
                return 

    async def andar_limpo(self, interaction):
        self.clear_items()
        
        floor_gold, floor_xp = arena_floor_rewards(self.andar_atual)
        self.gold_acumulado += floor_gold
        self.xp_acumulado += floor_xp
        
        for h in self._get_alive(self.team_a):
            h.heal(int(h.max_hp * 0.15))
            
        embed = discord.Embed(
            title="✅ Andar Limpo!",
            description=f"Vitória! Vocês descansaram 15% do HP.\n\n💰 Loot atual: **{self.gold_acumulado} Gold** | ⭐ **{self.xp_acumulado} XP**\n\n**Atenção:** Se avançar e morreR, vai perder 75% de todo o loot acumulado. Deseja continuar subindo ou recuar com o loot seguro?",
            color=discord.Color.green()
        )
        view = ArenaClearView(self)
        await interaction.response.edit_message(embed=embed, view=view)

    async def fim_de_jogo(self, interaction, venceu=False):
        self.clear_items()
        
        if not venceu:
            self.gold_acumulado = int(self.gold_acumulado * 0.25)
            self.xp_acumulado = int(self.xp_acumulado * 0.25)
            
        self.salvar_progresso()
        
        titulo = "🏆 Retirada Vitoriosa da Torre!" if venceu else "☠️ A Party foi Aniquilada..."
        cor = discord.Color.gold() if venceu else discord.Color.red()
        
        embed = discord.Embed(title=titulo, color=cor)
        embed.add_field(name="Andar Alcançado", value=f"**{self.andar_atual - 1 if not venceu else self.andar_atual}**", inline=True)
        
        nome_recompensa = "Recompensas Resgatadas" if venceu else "Recompensas (Penalidade de 75%)"
        embed.add_field(name=nome_recompensa, value=f"💰 {self.gold_acumulado} Gold\n⭐ {self.xp_acumulado} XP", inline=True)
        
        try: await interaction.response.edit_message(embed=embed, view=None)
        except: await interaction.message.edit(embed=embed, view=None)

    def salvar_progresso(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        uid = str(self.ctx.author.id)
        
        andar_alcancado = self.andar_atual - 1
        cursor.execute("SELECT arena_record FROM players WHERE user_id = ?", (uid,))
        rec = cursor.fetchone()
        
        if rec and andar_alcancado > rec[0]:
            cursor.execute("UPDATE players SET arena_record = ? WHERE user_id = ?", (andar_alcancado, uid))

        self.gold_acumulado, self.xp_acumulado = apply_reward_bonuses(cursor, uid, self.gold_acumulado, self.xp_acumulado)
        cursor.execute("UPDATE players SET gold = gold + ?, last_arena = ? WHERE user_id = ?", (self.gold_acumulado, time.time(), uid))
        
        dar_xp_jogador(cursor, uid, self.xp_acumulado)
        for h in self.party_data:
            dar_xp_heroi(cursor, int(h["id"]), self.xp_acumulado)
            
        conn.commit()
        conn.close()

    async def on_timeout(self):
        self.salvar_progresso()
        try: await self.message.edit(content="⏳ **Batalha expirada por inatividade.** O grupo recuou e o loot foi salvo.", view=None)
        except: pass

class ButtonAtacar(discord.ui.Button):
    def __init__(self, battle_view):
        super().__init__(style=discord.ButtonStyle.danger, label="Atacar", emoji="🗡️")
        self.view_ref = battle_view

    async def callback(self, interaction: discord.Interaction):
        actor = self.view_ref.current_actor
        target = self.view_ref._get_target_aggro(self.view_ref._get_alive(self.view_ref.team_b))
        
        is_crit = random.randint(1, 100) <= actor.get_stat("crt")
        dmg = actor.get_stat("atk") * (1.5 if is_crit else 1.0)
        dealt = target.take_damage(self.view_ref._roll_damage_variance(actor, dmg), actor.get_stat("atk"))
        crit = " (💥)" if is_crit else ""
        
        self.view_ref.log_display.append(f"🗡️ {actor.clean_name} atacou {target.clean_name} por **{dealt}**{crit}.")
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

class ArenaClearView(discord.ui.View):
    def __init__(self, battle_view):
        super().__init__(timeout=600)
        self.view_ref = battle_view

    @discord.ui.button(label="Continuar Subindo", style=discord.ButtonStyle.danger, emoji="🚪")
    async def btn_continuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.view_ref.andar_atual += 1
        await self.view_ref.iniciar_andar(interaction)

    @discord.ui.button(label="Recuar e Salvar Loot", style=discord.ButtonStyle.success, emoji="🏃")
    async def btn_recuar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.view_ref.salvar_progresso()
        embed = discord.Embed(
            title="🏃 Retirada Estratégica!",
            description=f"A sua equipe fugiu com os bolsos cheios.\n\n💰 **+{self.view_ref.gold_acumulado} Gold**\n⭐ **+{self.view_ref.xp_acumulado} XP**",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class Arena(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _arena_auto(self, ctx, party_data_base):
        user_id = str(ctx.author.id)
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        if not has_arena_auto(cursor, user_id):
            conn.close()
            return await ctx.send("Você ainda não comprou o **Modo Automático da Arena** na loja de Gems. TutoriUAU: automação sem licença vira estágio.")

        power = sum((h.get("stats", {}).get("hp", 0) // 6) + h.get("stats", {}).get("atk", 0) + h.get("stats", {}).get("matk", 0) + h.get("stats", {}).get("def", 0) for h in party_data_base)
        andar = 0
        while True:
            andar += 1
            dificuldade = 180 + int((andar ** 1.18) * 55)
            if power * random.uniform(0.72, 1.18) < dificuldade:
                andar -= 1
                break
            if andar >= 80:
                break

        andar = max(1, andar)
        gold = 0
        xp = 0
        for floor in range(1, andar + 1):
            floor_gold, floor_xp = arena_floor_rewards(floor)
            gold += floor_gold
            xp += floor_xp
        gold, xp = apply_reward_bonuses(cursor, user_id, gold, xp)
        gold = int(gold * 0.70)
        xp = int(xp * 0.70)

        cursor.execute("SELECT arena_record FROM players WHERE user_id = ?", (user_id,))
        rec = cursor.fetchone()
        if rec and andar > (rec[0] or 0):
            cursor.execute("UPDATE players SET arena_record = ? WHERE user_id = ?", (andar, user_id))
        cursor.execute("UPDATE players SET gold = gold + ?, last_arena = ? WHERE user_id = ?", (gold, time.time(), user_id))
        dar_xp_jogador(cursor, user_id, xp)
        for h in party_data_base:
            dar_xp_heroi(cursor, int(h["id"]), xp)
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="Arena Automática",
            description=(
                f"A IA do TutoriUAU levou sua party até o andar **{andar}**.\n"
                "Ela apertou botões por você e trouxe **70%** das recompensas. Automação com imposto do TutoriUAU."
            ),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Recompensas", value=f"+{gold:,} Gold\n+{xp:,} XP", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="arena", aliases=["torre"])
    async def arena_cmd(self, ctx, modo: str = None):
        user_id = str(ctx.author.id)
        
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        cursor.execute("SELECT last_arena FROM players WHERE user_id = ?", (user_id,))
        p_data = cursor.fetchone()
        conn.close()

        if p_data:
            last_arena = p_data[0] or 0
            tempo_passado = time.time() - last_arena
            if tempo_passado < 3600:
                restante = int((3600 - tempo_passado) / 60)
                return await ctx.send(f"⏳ A Torre abrirá novamente para você em **{restante} minutos**.")

        party_data_base = puxar_party_para_combate(ctx.author.id, ctx.author.name)
        if not party_data_base: return await ctx.send("❌ Equipe um Herói Líder com `echo main <ID>` antes de entrar na Arena.")

        if (modo or "").lower() in ["auto", "automatico", "automático"]:
            return await self._arena_auto(ctx, party_data_base)

        view_batalha = ArenaBattleView(ctx, party_data_base)
        msg = await ctx.send("🏰 **Carregando a Torre da Arena Tática...**")
        view_batalha.message = msg
        await view_batalha.iniciar_andar()

async def setup(bot):
    await bot.add_cog(Arena(bot))
