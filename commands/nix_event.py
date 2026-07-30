import json
import random
import re
import sqlite3

import discord
from discord.ext import commands

from data.nix_choices import NIX_ALIGNMENT_CHOICES, NIX_FINAL_CHOICES
from data.nix_dialogues import (
    NIX_ARCHIVES,
    NIX_EVENT_NAME,
    NIX_HELP_INTRO,
    NIX_INTRO,
    NIX_PHASES,
    TUTORI_SUPERVISION_LINES,
)
from data.nix_missions import NIX_MISSIONS
from systems.nix_manager import (
    add_fragments,
    buy_shop_item,
    claim_final,
    complete_current_mission,
    current_mission,
    end_event,
    ensure_nix_schema,
    ensure_player_progress,
    get_global_state,
    is_event_active,
    is_nix_integrated,
    mission_progress_text,
    normalize_key,
    pause_event,
    register_choice,
    run_final_battle,
    run_reflection_battle,
    set_corruption,
    set_global_phase,
    start_investigation,
    start_event,
)
from systems.nix_rewards import NIX_CURRENCY, NIX_SHOP


def fmt(value):
    return f"{int(value or 0):,}".replace(",", ".")


def short(value, limit=1024):
    value = str(value or "")
    return value if len(value) <= limit else value[: limit - 3] + "..."


class NixArchiveView(discord.ui.View):
    def __init__(self, user, archives):
        super().__init__(timeout=180)
        self.user = user
        self.archives = archives or []
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_btn.disabled = self.page <= 0
        self.next_btn.disabled = self.page >= len(self.archives) - 1

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "NIX: arquivo vinculado a outro usuario. Abrir mesmo assim seria curioso. Nao farei. Ainda.",
                ephemeral=True,
            )
            return False
        return True

    def build_embed(self):
        archive = self.archives[self.page] if self.archives else {"title": "Arquivo vazio", "body": "Nada liberado."}
        embed = discord.Embed(
            title=archive["title"],
            description=archive["body"],
            color=discord.Color.dark_teal(),
        )
        embed.set_footer(text=f"NIX // Arquivo {self.page + 1}/{max(1, len(self.archives))}")
        return embed

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction, button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Proxima", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction, button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class NixEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn, cursor = self._connect()
        conn.commit()
        conn.close()

    def _connect(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_nix_schema(cursor)
        return conn, cursor

    def _basic_embed(self, title, description, color=discord.Color.dark_teal()):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=random.choice(TUTORI_SUPERVISION_LINES))
        return embed

    def _panel_embed(self, user, state, progress, progress_line=None):
        phase = int(state.get("fase_global") or 1)
        phase_data = NIX_PHASES.get(phase, NIX_PHASES[1])
        active = "Ativo" if int(state.get("ativo") or 0) else "Integrado" if int(state.get("nix_integrated") or 0) else "Dormindo"
        mission_id, mission = current_mission(progress)
        boss_max = max(1, int(state.get("boss_max_hp") or 1))
        boss_hp = max(0, int(state.get("boss_hp") or 0))
        boss_pct = boss_hp * 100 / boss_max

        embed = self._basic_embed(
            "NIX // Protocolo de Wolford",
            (
                f"{NIX_INTRO}\n\n"
                f"Evento: **{NIX_EVENT_NAME}**\n"
                f"Estado: **{active}** | Fase global: **{phase} - {phase_data['name']}**\n"
                f"{phase_data['summary']}"
            ),
            discord.Color.from_rgb(45, 210, 180),
        )
        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
        embed.add_field(
            name="Sinal global",
            value=(
                f"Corrupcao: **{fmt(state.get('corrupcao'))}%**\n"
                f"Fragmentos coletivos: **{fmt(state.get('total_fragmentos'))}**\n"
                f"PARASITE_01: **{boss_pct:.2f}% HP**"
            ),
            inline=True,
        )
        embed.add_field(
            name="Seu arquivo",
            value=(
                f"Fragmentos: **{fmt(progress.get('fragmentos'))} {NIX_CURRENCY}**\n"
                f"Afinidade: **{fmt(progress.get('afinidade'))}**\n"
                f"Final: **{progress.get('final_recebido') or 'pendente'}**"
            ),
            inline=True,
        )
        if mission:
            progress_value = progress_line or mission_progress_text_from_cached(progress, mission)
            embed.add_field(
                name=f"Missao atual: {mission_id}. {mission['title']}",
                value=f"{mission['objective']}\nProgresso: **{progress_value}**\n{mission['hint']}",
                inline=False,
            )
        else:
            embed.add_field(
                name="Missao atual",
                value="Use `echo nix investigar` para iniciar, ou `echo nix final` se ja derrotou a consciencia nao autorizada.",
                inline=False,
            )
        embed.add_field(
            name="Comandos",
            value=(
                "`echo nix investigar` | `status` | `missao` | `entregar`\n"
                "`echo nix escolher <opcao>` | `enfrentar` | `final <opcao>`\n"
                "`echo nix arquivos` | `loja` | `comprar <id>` | `ranking` | `tutorial`"
            ),
            inline=False,
        )
        return embed

    def _party(self, ctx):
        hunt = self.bot.get_cog("Hunt")
        if hunt and hasattr(hunt, "puxar_party_para_combate"):
            return hunt.puxar_party_para_combate(ctx.author.id, ctx.author.display_name)
        return None

    @commands.group(name="nix", aliases=["protocolo"], invoke_without_command=True)
    async def nix_group(self, ctx):
        conn, cursor = self._connect()
        try:
            state = get_global_state(cursor)
            progress = ensure_player_progress(cursor, ctx.author.id)
            progress_line = mission_progress_text(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        await ctx.send(embed=self._panel_embed(ctx.author, state, progress, progress_line))

    @nix_group.command(name="tutorial", aliases=["guia", "ajuda", "manual"])
    async def tutorial_cmd(self, ctx):
        embed = self._basic_embed(
            "Tutorial // Protocolo NIX",
            (
                f"{NIX_HELP_INTRO}\n\n"
                "**1. Investigue:** `echo nix investigar` cria seu arquivo individual e libera a primeira missao.\n"
                "**2. Complete missoes:** use `echo nix missao` para ver o objetivo e `echo nix entregar` para validar.\n"
                "**3. Colete fragmentos:** Hunts, adventure, dungeon e Biblioteca podem soltar Fragmentos de Dados enquanto o evento estiver ativo.\n"
                "**4. Escolha postura:** `echo nix escolher apoiar`, `confrontar` ou `negociar` altera afinidade e corrupcao.\n"
                "**5. Enfrente anomalias:** `echo nix enfrentar` abre reflexo corrompido ou boss final quando a missao pedir.\n"
                "**6. Decida o final:** apos vencer, use `echo nix final integrar|libertar|apagar|observar`.\n"
                "**7. Gaste o arquivo:** `echo nix loja` e `echo nix comprar <id>` trocam fragmentos por tema, titulo, tickets, Gold, stamina e pet."
            ),
            discord.Color.from_rgb(30, 180, 210),
        )
        embed.add_field(
            name="ADM",
            value=(
                "`echo adm nix iniciar`, `pausar`, `fase <1-6>`, `corrupcao <0-100>`, `encerrar`, "
                "`reset @user`, `teste @user`, `fragmentos @user <qtd>`."
            ),
            inline=False,
        )
        embed.set_footer(text="NIX: tutorial concluido. TutoriUAU: ela esta se achando. Isso e bom para produtividade.")
        await ctx.send(embed=embed)

    @nix_group.command(name="investigar", aliases=["iniciar", "contato"])
    async def investigar_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            result = start_investigation(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        if result.get("started"):
            return await ctx.send(
                "NIX: arquivo individual criado. Recebi seu primeiro padrao de comportamento.\n"
                "TutoriUAU: parabens, voce apertou o botao que dizia investigar o erro. Zero instinto de preservacao.\n"
                "Use `echo nix missao`."
            )
        await ctx.send("NIX: contato ja existe. Use `echo nix missao` ou `echo nix status`.")

    @nix_group.command(name="status", aliases=["fragmentos", "saldo", "perfil"])
    async def status_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            state = get_global_state(cursor)
            progress = ensure_player_progress(cursor, ctx.author.id)
            progress_line = mission_progress_text(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        embed = self._panel_embed(ctx.author, state, progress, progress_line)
        await ctx.send(embed=embed)

    @nix_group.command(name="missao", aliases=["missão", "objetivo"])
    async def missao_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            progress = ensure_player_progress(cursor, ctx.author.id)
            mission_id, mission = current_mission(progress)
            line = mission_progress_text(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        if not mission:
            return await ctx.send("NIX: nenhuma missao ativa. Use `echo nix investigar` para abrir seu arquivo.")
        embed = self._basic_embed(
            f"Missao {mission_id} // {mission['title']}",
            f"{mission['objective']}\n\nProgresso: **{line}**\n{mission['hint']}",
            discord.Color.from_rgb(60, 190, 170),
        )
        await ctx.send(embed=embed)

    @nix_group.command(name="entregar", aliases=["concluir", "validar"])
    async def entregar_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            result = complete_current_mission(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        next_text = "Proxima missao liberada." if result.get("next_mission") else "Arquivo individual estabilizado. Use `echo nix final`."
        await ctx.send(
            f"NIX: missao **{result['mission_id']} - {result['mission']['title']}** concluida.\n"
            f"Recompensa: **{result['reward_text']}**\n{next_text}"
        )

    @nix_group.command(name="escolher", aliases=["escolha", "responder"])
    async def escolher_cmd(self, ctx, *, escolha: str = None):
        if not escolha:
            return await ctx.send("Use `echo nix escolher apoiar|confrontar|negociar|memoria|recompensa|arquivo`.")
        conn, cursor = self._connect()
        try:
            result = register_choice(cursor, ctx.author.id, escolha)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        data = result.get("data", {})
        await ctx.send(data.get("response", "NIX: escolha registrada. Consequencias sao apenas estatisticas com suspense."))

    @nix_group.command(name="apoiar")
    async def apoiar_cmd(self, ctx):
        await self.escolher_cmd(ctx, escolha="apoiar")

    @nix_group.command(name="confrontar")
    async def confrontar_cmd(self, ctx):
        await self.escolher_cmd(ctx, escolha="confrontar")

    @nix_group.command(name="negociar")
    async def negociar_cmd(self, ctx):
        await self.escolher_cmd(ctx, escolha="negociar")

    @nix_group.command(name="enfrentar", aliases=["lutar", "boss"])
    async def enfrentar_cmd(self, ctx):
        party = self._party(ctx)
        conn, cursor = self._connect()
        try:
            progress = ensure_player_progress(cursor, ctx.author.id)
            mission_id, mission = current_mission(progress)
            if not mission:
                result = {"error": "Nenhuma anomalia pronta para combate. Use `echo nix missao`."}
            elif mission.get("kind") == "reflection":
                result = run_reflection_battle(cursor, ctx.author.id, ctx.author.display_name, party)
            elif mission.get("kind") == "final_boss":
                result = run_final_battle(cursor, ctx.author.id, ctx.author.display_name, party)
            else:
                result = {"error": "Sua missao atual nao pede combate. NIX guardou a violencia para depois."}
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        title = "Vitoria contra a anomalia" if result.get("victory") else "Derrota registrada pela anomalia"
        embed = self._basic_embed(title, "NIX: combate de diagnostico encerrado.", discord.Color.green() if result.get("victory") else discord.Color.red())
        if result.get("global_damage"):
            embed.add_field(name="Dano global em PARASITE_01", value=f"**{fmt(result['global_damage'])}**", inline=False)
        embed.add_field(name="Log", value=short(result.get("battle_log", "Sem log.")), inline=False)
        await ctx.send(embed=embed)

    @nix_group.command(name="final", aliases=["destino"])
    async def final_cmd(self, ctx, escolha: str = None):
        if not escolha:
            lines = []
            for choice_id, data in NIX_FINAL_CHOICES.items():
                req = data.get("requires") or {}
                lock = f" | exige afinidade {req['affinity']}" if req.get("affinity") else ""
                lines.append(f"`{choice_id}` - **{data['label']}**{lock}")
            embed = self._basic_embed(
                "Escolha Final // NIX",
                "Use `echo nix final <opcao>`.\n\n" + "\n".join(lines),
                discord.Color.from_rgb(90, 210, 200),
            )
            return await ctx.send(embed=embed)

        conn, cursor = self._connect()
        try:
            result = claim_final(cursor, ctx.author.id, escolha)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        await ctx.send(
            f"**{result['data']['label']}**\n{result.get('dialogue', '')}\n"
            f"Recompensa: **{result['reward_text']}**"
        )

    @nix_group.command(name="arquivos", aliases=["arquivo", "lore"])
    async def arquivos_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            progress = ensure_player_progress(cursor, ctx.author.id)
            unlocked = max(1, min(len(NIX_ARCHIVES), int(progress.get("arquivos_liberados") or 0) + int(progress.get("fase") or 0) // 2))
            conn.commit()
        finally:
            conn.close()
        archives = NIX_ARCHIVES[:unlocked]
        view = NixArchiveView(ctx.author, archives)
        await ctx.send(embed=view.build_embed(), view=view)

    @nix_group.command(name="loja", aliases=["shop"])
    async def loja_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            progress = ensure_player_progress(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        embed = self._basic_embed(
            "Loja // Fragmentos de Dados",
            f"Seu saldo: **{fmt(progress.get('fragmentos'))} {NIX_CURRENCY}**",
            discord.Color.gold(),
        )
        lines = []
        for item_id, item in sorted(NIX_SHOP.items(), key=lambda entry: entry[1]["index"]):
            unique = " | unico" if not item.get("repetivel", True) else ""
            lines.append(f"`{item['index']}`/`{item_id}` **{item['nome']}** - {fmt(item['preco'])} fragmentos{unique}\n{item['descricao']}")
        embed.add_field(name="Itens", value=short("\n\n".join(lines), 3900), inline=False)
        embed.set_footer(text="NIX: use `echo nix comprar <id> [quantidade]`. TutoriUAU: ela colocou recibo em tudo. Estou orgulhoso e cansado.")
        await ctx.send(embed=embed)

    @nix_group.command(name="comprar", aliases=["resgatar", "buy"])
    async def comprar_cmd(self, ctx, item_ref: str = None, quantidade: int = 1):
        if not item_ref:
            return await ctx.send("Use `echo nix comprar <id|numero> [quantidade]`.")
        conn, cursor = self._connect()
        try:
            result = buy_shop_item(cursor, ctx.author.id, item_ref, quantidade)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        await ctx.send(
            f"NIX: compra concluida: **{result['quantity']}x {result['item']['nome']}** por **{fmt(result['price'])} Fragmentos de Dados**.\n"
            f"Recebido: **{result['reward_text']}**."
        )

    @nix_group.command(name="ranking", aliases=["rank", "top"])
    async def ranking_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            cursor.execute(
                """
                SELECT user_id, fragmentos, afinidade, completado
                FROM nix_event_progress
                ORDER BY fragmentos DESC, afinidade DESC
                LIMIT 10
                """
            )
            rows = cursor.fetchall()
            conn.commit()
        finally:
            conn.close()
        lines = [
            f"**{idx}.** <@{user_id}> - **{fmt(fragmentos)}** fragmentos | afinidade **{fmt(afinidade)}**{' | final' if completado else ''}"
            for idx, (user_id, fragmentos, afinidade, completado) in enumerate(rows, start=1)
        ]
        embed = self._basic_embed(
            "Ranking // Protocolo NIX",
            "\n".join(lines) if lines else "NIX: nenhum arquivo de jogador encontrado. Silencio estatistico.",
            discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @nix_group.command(name="analisar", aliases=["analise", "scan"])
    async def analisar_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            progress = ensure_player_progress(cursor, ctx.author.id)
            line = mission_progress_text(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        await ctx.send(
            f"NIX: analise de **{ctx.author.display_name}** concluida.\n"
            f"Fragmentos: **{fmt(progress.get('fragmentos'))}** | Afinidade: **{fmt(progress.get('afinidade'))}** | Progresso: **{line}**.\n"
            "TutoriUAU: diagnostico tecnico: ainda da pra melhorar, mas ja vi piores. Muitos piores."
        )

    async def admin_dispatch(self, ctx, action=None, payload=None):
        key = normalize_key(action)
        conn, cursor = self._connect()
        try:
            if key in {"iniciar", "start", "ativar", "abrir"}:
                state = start_event(cursor)
                conn.commit()
                return await ctx.send(f"Protocolo NIX iniciado. Fase **{state['fase_global']}** ativa. A falha piscou de volta.")

            if key in {"pausar", "desativar", "fechar", "pause"}:
                pause_event(cursor)
                conn.commit()
                return await ctx.send("Protocolo NIX pausado. NIX: pausa nao e apagamento. Estou observando.")

            if key == "fase":
                if not payload:
                    return await ctx.send("Uso: `echo adm nix fase <1-6>`")
                state = set_global_phase(cursor, int(str(payload).split()[0]))
                conn.commit()
                return await ctx.send(f"Fase global da NIX definida para **{state['fase_global']}**.")

            if key in {"corrupcao", "corrupção", "corruption"}:
                if not payload:
                    return await ctx.send("Uso: `echo adm nix corrupcao <0-100>`")
                state = set_corruption(cursor, int(str(payload).split()[0]))
                conn.commit()
                return await ctx.send(f"Corrupcao global definida para **{state['corrupcao']}%**.")

            if key in {"encerrar", "end", "finalizar"}:
                state, granted = end_event(cursor)
                conn.commit()
                return await ctx.send(
                    f"Protocolo NIX encerrado. NIX integrada oficialmente a Wolford.\n"
                    "Ela permanece como entidade narrativa do sistema, nao como personagem jogavel."
                )

            if key == "reset":
                target_id = self._extract_user_id(payload)
                if not target_id:
                    return await ctx.send("Uso: `echo adm nix reset @user`")
                cursor.execute("DELETE FROM nix_event_progress WHERE user_id = ?", (target_id,))
                cursor.execute("DELETE FROM nix_event_choices WHERE user_id = ?", (target_id,))
                cursor.execute("DELETE FROM nix_event_rewards WHERE user_id = ?", (target_id,))
                conn.commit()
                return await ctx.send(f"Arquivo NIX de <@{target_id}> reiniciado.")

            if key == "teste":
                target_id = self._extract_user_id(payload) or str(ctx.author.id)
                ensure_player_progress(cursor, target_id)
                cursor.execute(
                    """
                    UPDATE nix_event_progress
                    SET fase = 5, missao_atual = 7, mission_progress = 0,
                        fragmentos = fragmentos + 100, afinidade = afinidade + 45,
                        boss_derrotado = 0, completado = 0, final_recebido = NULL
                    WHERE user_id = ?
                    """,
                    (target_id,),
                )
                conn.commit()
                return await ctx.send(f"Modo teste NIX preparado para <@{target_id}>: missao final, +100 fragmentos e afinidade alta.")

            if key in {"fragmentos", "fragmento", "dar_fragmentos"}:
                if not payload:
                    return await ctx.send("Uso: `echo adm nix fragmentos @user <quantidade>`")
                target_id = self._extract_user_id(payload)
                numbers = re.findall(r"-?\d+", str(payload))
                amount = int(numbers[-1]) if numbers else 0
                if not target_id or amount == 0:
                    return await ctx.send("Uso: `echo adm nix fragmentos @user <quantidade>`")
                add_fragments(cursor, target_id, amount, "admin")
                conn.commit()
                return await ctx.send(f"NIX: **{fmt(amount)}** Fragmentos de Dados enviados para <@{target_id}>.")

            state = get_global_state(cursor)
            conn.commit()
            return await ctx.send(
                "Comandos ADM da NIX: `iniciar`, `pausar`, `fase <1-6>`, `corrupcao <0-100>`, "
                "`encerrar`, `reset @user`, `teste @user`, `fragmentos @user <qtd>`.\n"
                f"Estado atual: ativo **{state.get('ativo')}**, fase **{state.get('fase_global')}**, integrada **{state.get('nix_integrated')}**."
            )
        finally:
            conn.close()

    def _extract_user_id(self, raw):
        if not raw:
            return None
        match = re.search(r"(\d{15,25})", str(raw))
        return match.group(1) if match else None


def mission_progress_text_from_cached(progress, mission):
    if not mission:
        return "0/0"
    kind = mission.get("kind")
    if kind == "fragmentos":
        done = int(progress.get("fragmentos") or 0)
    else:
        done = int(progress.get("mission_progress") or 0)
    return f"{min(done, int(mission.get('target') or 1))}/{mission.get('target', 1)}"


async def setup(bot):
    await bot.add_cog(NixEvent(bot))
