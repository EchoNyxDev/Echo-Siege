import json
import random
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from data.biblioteca_categories import BIBLIOTECA_CATEGORIES, DIFFICULTY_EMOJIS, DIFFICULTY_LABELS
from data.biblioteca_dialogues import (
    ACERTO_LINES,
    COMBO_LINES,
    DICA_LINES,
    ERRO_LINES,
    NIX_LINES,
    PERFEITO_LINE,
    TUTORI_BIBLIOTECA_INTRO,
)
from data.biblioteca_shop import BIBLIOTECA_SHOP
from systems.biblioteca_manager import (
    BIBLIOTECA_CURRENCY,
    abandon_session,
    active_session,
    add_custom_question,
    biblioteca_is_active,
    buy_shop_item,
    ensure_biblioteca_schema,
    ensure_player,
    get_config,
    get_question,
    load_questions,
    now_ts,
    player_status,
    collection_by_category,
    set_config,
    start_session,
    use_hint,
    answer_session,
    normalize_text,
)
from systems.biblioteca_ranking import fetch_ranking, ranking_categories
from systems.biblioteca_rewards import reward_to_text
from systems.biblioteca_session import SESSION_MODES
from utils.hero_images import get_hero_attachment


def fmt(value):
    return f"{int(value or 0):,}".replace(",", ".")


def short(value, limit=1024):
    value = str(value or "")
    return value if len(value) <= limit else value[: limit - 3] + "..."


def decode_list(raw):
    try:
        value = json.loads(raw or "[]")
        return value if isinstance(value, list) else []
    except (TypeError, ValueError):
        return []


class BibliotecaLinesPaginator(discord.ui.View):
    def __init__(self, user, title, lines, color=discord.Color.dark_purple(), per_page=12):
        super().__init__(timeout=180)
        self.user = user
        self.title = title
        self.lines = lines or ["Nada encontrado."]
        self.color = color
        self.per_page = per_page
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_btn.disabled = self.page == 0
        self.next_btn.disabled = (self.page + 1) * self.per_page >= len(self.lines)

    def build_embed(self):
        total_pages = max(1, (len(self.lines) + self.per_page - 1) // self.per_page)
        start = self.page * self.per_page
        chunk = self.lines[start:start + self.per_page]
        embed = discord.Embed(title=self.title, description=short("\n".join(chunk), 3900), color=self.color)
        embed.set_footer(text=f"NIX // Página {self.page + 1}/{total_pages} // A prateleira e grande porque alguem achou 2.098 perguntas uma boa ideia.")
        return embed

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Essa coleção foi aberta por outra pessoa. Use `echo biblioteca colecao` e ganhe sua própria poeira.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction, button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary)
    async def next_btn(self, interaction, button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class Biblioteca(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_biblioteca_schema(cursor)
        conn.commit()
        conn.close()

    def _connect(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_biblioteca_schema(cursor)
        return conn, cursor

    def _basic_embed(self, title, description, color=discord.Color.dark_teal()):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="NIX: Biblioteca sob minha curadoria. TutoriUAU supervisiona e finge que nao esta orgulhoso.")
        return embed

    def _panel_embed(self, user, player, active=None):
        status = "Aberta" if active else "Fechada"
        embed = self._basic_embed(
            "Biblioteca Perdida de Wolford",
            (
                f"{TUTORI_BIBLIOTECA_INTRO}\n\n"
                f"Status: **{status}**\n"
                f"Seu saldo: **{fmt(player.get('paginas', 0))} {BIBLIOTECA_CURRENCY}**\n"
                "Responda perguntas, identifique personagens pelas imagens do arquivo local e troque páginas por prêmios."
            ),
            discord.Color.dark_purple(),
        )
        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
        embed.add_field(
            name="Sessões",
            value=(
                "`echo biblioteca diaria` - 10 perguntas, uma vez por dia.\n"
                "`echo biblioteca explorar` - leitura curta e repetível.\n"
                "`echo biblioteca expedicao` - 15 perguntas; 3 erros encerram."
            ),
            inline=False,
        )
        embed.add_field(
            name="Durante a leitura",
            value=(
                "`echo biblioteca responder <resposta>` - aceita texto ou A/B/C/D.\n"
                "`echo biblioteca dica` - reduz a recompensa da pergunta.\n"
                "`echo biblioteca desistir` - encerra a sessão ativa."
            ),
            inline=False,
        )
        embed.add_field(
            name="Extras",
            value="`status`, `ranking`, `colecao`, `loja`, `comprar <id>` e `tutorial`.",
            inline=False,
        )
        return embed

    def _question_attachment(self, question):
        image = question.get("imagem") if question else None
        if isinstance(image, dict) and image.get("tipo") == "hero":
            path, filename = get_hero_attachment(image.get("hero_id"), "biblioteca")
            if path:
                return discord.File(path, filename=filename)
        return None

    def _question_embed(self, session, question, result_text=None):
        mode = SESSION_MODES.get(session.get("mode"), {"label": "Leitura"})
        answered = len(decode_list(session.get("answered_ids")))
        total = int(session.get("total_questions") or 1)
        current_number = min(total, answered + 1)
        difficulty = int(question.get("dificuldade", 1) or 1)
        category = str(question.get("categoria", "Geral"))
        category_data = BIBLIOTECA_CATEGORIES.get(category, {})
        cat_prefix = category_data.get("emoji", "📚")
        diff = f"{DIFFICULTY_EMOJIS.get(difficulty, '📄')} {DIFFICULTY_LABELS.get(difficulty, 'Arquivo')}"
        expires_at = int(session.get("expires_at") or now_ts())

        embed = discord.Embed(
            title=f"Biblioteca Perdida • {mode['label']} • {current_number}/{total}",
            description=short(str(question.get("pergunta", "Pergunta corrompida.")), 1800),
            color=discord.Color.dark_purple(),
        )
        if result_text:
            embed.add_field(name="Resultado anterior", value=short(result_text), inline=False)
        embed.add_field(name="Categoria", value=f"{cat_prefix} {category}", inline=True)
        embed.add_field(name="Dificuldade", value=diff, inline=True)
        embed.add_field(name="Tempo", value=f"Termina <t:{expires_at}:R>", inline=True)

        options = list(question.get("opcoes") or [])
        if options:
            letters = "ABCD"
            lines = [f"**{letters[index]})** {option}" for index, option in enumerate(options[:4])]
            embed.add_field(name="Alternativas", value="\n".join(lines), inline=False)
            embed.add_field(name="Responder", value="Use `echo biblioteca responder A` ou escreva a resposta.", inline=False)
        else:
            embed.add_field(name="Responder", value="Use `echo biblioteca responder <sua resposta>`.", inline=False)

        hint = "Use `echo biblioteca dica` se aceitar metade das páginas desta pergunta."
        embed.set_footer(text=f"NIX: {hint}")
        return embed

    async def _send_question(self, ctx, session, question, result_text=None):
        embed = self._question_embed(session, question, result_text)
        file = self._question_attachment(question)
        if file:
            embed.set_image(url=f"attachment://{file.filename}")
            return await ctx.send(embed=embed, file=file)
        return await ctx.send(embed=embed)

    async def _start_mode(self, ctx, mode):
        conn, cursor = self._connect()
        try:
            result = start_session(cursor, ctx.author.id, mode)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        prefix = "Você já tem uma sessão ativa. O livro ficou aberto, e isso é quase responsabilidade." if result.get("already") else "Sessão iniciada. O arquivo fez barulho de página antiga, que é basicamente trilha sonora."
        await self._send_question(ctx, result["session"], result["question"], prefix)

    @commands.group(name="biblioteca", aliases=["biblio", "library"], invoke_without_command=True)
    async def biblioteca_group(self, ctx):
        conn, cursor = self._connect()
        try:
            player = ensure_player(cursor, ctx.author.id)
            active = biblioteca_is_active(cursor)
            conn.commit()
        finally:
            conn.close()
        await ctx.send(embed=self._panel_embed(ctx.author, player, active))

    @biblioteca_group.command(name="entrar", aliases=["inicio", "start"])
    async def entrar_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            player = ensure_player(cursor, ctx.author.id)
            active = biblioteca_is_active(cursor)
            conn.commit()
        finally:
            conn.close()
        await ctx.send(embed=self._panel_embed(ctx.author, player, active))

    @biblioteca_group.command(name="tutorial", aliases=["guia", "manual", "ajuda"])
    async def tutorial_cmd(self, ctx):
        embed = self._basic_embed(
            "Tutorial da Biblioteca Perdida",
            (
                "**Fluxo simples:** `entrar` para ver o painel, `diaria` ou `explorar` para abrir uma sessão, "
                "`responder` para avançar e `loja` para gastar suas Páginas Perdidas.\n\n"
                "**Tipos de pergunta:** múltipla escolha, verdadeiro/falso, resposta escrita, ordem lógica, habilidade, emoji e imagem de personagem. "
                "Nas alternativas, A/B/C/D funciona. Em texto aberto, acento não precisa ser perfeito.\n\n"
                "**Dicas:** `echo biblioteca dica` ajuda, mas corta a recompensa daquela pergunta. Conhecimento assistido ainda é conhecimento, só que com recibo.\n\n"
                "**Expedição:** `echo biblioteca expedicao` é a versão longa. Errou três vezes, o arquivo te expulsa com elegância duvidosa."
            ),
            discord.Color.dark_purple(),
        )
        embed.add_field(
            name="Comandos úteis",
            value=(
                "`status` mostra progresso.\n"
                "`colecao` mostra categorias vistas e acertadas.\n"
                "`ranking paginas|acertos|combo|precisao` mostra os melhores.\n"
                "`comprar <id>` compra itens da loja."
            ),
            inline=False,
        )
        embed.set_footer(text="TutoriUAU: parabéns, você abriu o tutorial dentro do tutorial. Metalinguagem com poeira.")
        await ctx.send(embed=embed)

    @biblioteca_group.command(name="diaria", aliases=["diária", "daily"])
    async def diaria_cmd(self, ctx):
        await self._start_mode(ctx, "diaria")

    @biblioteca_group.command(name="explorar", aliases=["exploracao", "exploração", "explore"])
    async def explorar_cmd(self, ctx):
        await self._start_mode(ctx, "explorar")

    @biblioteca_group.command(name="expedicao", aliases=["expedição", "expedition"])
    async def expedicao_cmd(self, ctx):
        await self._start_mode(ctx, "expedicao")

    @biblioteca_group.command(name="responder", aliases=["resposta", "answer", "r"])
    async def responder_cmd(self, ctx, *, resposta: str = None):
        if not resposta:
            return await ctx.send("Use `echo biblioteca responder <resposta>`. Exemplo: `echo biblioteca responder A`.")
        conn, cursor = self._connect()
        try:
            result = answer_session(cursor, ctx.author.id, resposta)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])

        if result["correct"]:
            combo = int(result["session"].get("combo") or 0)
            line = random.choice(ACERTO_LINES)
            combo_line = COMBO_LINES.get(combo)
            result_text = f"✅ **Correto!** +{fmt(result['points'])} Páginas Perdidas.\n{line}"
            if combo_line:
                result_text += f"\n**Combo {combo}:** {combo_line}"
        else:
            result_text = f"❌ **Errado.** Resposta certa: **{result['expected']}**.\n{random.choice(ERRO_LINES)}"
            explanation = result["question"].get("explicacao")
            if explanation:
                result_text += f"\n{explanation}"

        if result.get("nix_fragments"):
            result_text += f"\n`NIX` Fragmentos de Dados: **+{result['nix_fragments']}**."

        if result.get("finished"):
            reward = result.get("final_reward") or {}
            total = int(result["session"].get("total_questions") or 1)
            perfect = int(result["session"].get("acertos") or 0) == total and int(result["session"].get("erros") or 0) == 0
            embed = self._basic_embed(
                "Sessão encerrada na Biblioteca",
                result_text,
                discord.Color.green() if result["correct"] else discord.Color.orange(),
            )
            embed.add_field(
                name="Resumo",
                value=(
                    f"Acertos: **{result['session'].get('acertos', 0)}/{total}**\n"
                    f"Erros: **{result['session'].get('erros', 0)}**\n"
                    f"Combo final: **{result['session'].get('combo', 0)}**"
                ),
                inline=True,
            )
            embed.add_field(name="Bônus de conclusão", value=reward_to_text(reward), inline=False)
            if perfect:
                embed.add_field(name="Perfeito", value=PERFEITO_LINE, inline=False)
            embed.set_footer(text=f"NIX: {random.choice(NIX_LINES)}")
            return await ctx.send(embed=embed)

        return await self._send_question(ctx, result["session"], result["next_question"], result_text)

    @biblioteca_group.command(name="dica", aliases=["hint"])
    async def dica_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            result = use_hint(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        embed = self._basic_embed("Dica da Biblioteca", f"{random.choice(DICA_LINES)}\n\n{result['hint']}", discord.Color.gold())
        await ctx.send(embed=embed)

    @biblioteca_group.command(name="desistir", aliases=["sair", "abandonar"])
    async def desistir_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            ok = abandon_session(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        if not ok:
            return await ctx.send("Você não tem sessão ativa para abandonar.")
        await ctx.send("Sessão encerrada. TutoriUAU marcou como retirada estratégica, porque 'fugi do livro' fica feio no relatório.")

    @biblioteca_group.command(name="status", aliases=["saldo", "perfil"])
    async def status_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            status = player_status(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        player = status["player"]
        total = int(player.get("total_perguntas") or 0)
        acertos = int(player.get("total_acertos") or 0)
        precision = (acertos * 100 / total) if total else 0
        embed = self._basic_embed(
            f"Status da Biblioteca • {ctx.author.display_name}",
            f"Saldo: **{fmt(player.get('paginas', 0))} {BIBLIOTECA_CURRENCY}**",
            discord.Color.dark_purple(),
        )
        embed.add_field(name="Arquivo", value=f"Perguntas: **{fmt(total)}**\nAcertos: **{fmt(acertos)}**\nPrecisão: **{precision:.1f}%**", inline=True)
        embed.add_field(name="Combo", value=f"Atual: **{fmt(player.get('combo_atual', 0))}**\nRecorde: **{fmt(player.get('maior_combo', 0))}**", inline=True)
        if status["active"]:
            session = status["active"]
            embed.add_field(
                name="Sessão ativa",
                value=f"Modo: **{SESSION_MODES.get(session.get('mode'), {}).get('label', session.get('mode'))}**\nTermina <t:{int(session.get('expires_at') or now_ts())}:R>",
                inline=False,
            )
        embed.set_thumbnail(url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        await ctx.send(embed=embed)

    @biblioteca_group.command(name="ranking", aliases=["rank", "top"])
    async def ranking_cmd(self, ctx, categoria: str = "paginas"):
        conn, cursor = self._connect()
        try:
            categoria, title, unit, rows = fetch_ranking(cursor, categoria)
            conn.commit()
        finally:
            conn.close()
        lines = []
        for index, row in enumerate(rows, start=1):
            user_id, value = row[0], row[1]
            if value:
                lines.append(f"**{index}.** <@{user_id}> - **{value} {unit}**")
        embed = self._basic_embed(
            f"Ranking da Biblioteca • {title}",
            "\n".join(lines) if lines else "Ainda não há dados suficientes. A prateleira julgou todo mundo igualmente vazio.",
            discord.Color.gold(),
        )
        embed.set_footer(text=f"Categorias: {ranking_categories()}. TutoriUAU: precisão exige 20 respostas para evitar gênio de uma pergunta só.")
        await ctx.send(embed=embed)

    @biblioteca_group.command(name="colecao", aliases=["coleção", "collection"])
    async def colecao_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            data = collection_by_category(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        lines = []
        for category, info in data.items():
            total = max(1, info["total"])
            seen_percent = info["seen"] * 100 / total
            lines.append(f"**{category}**: vistas **{info['seen']}/{info['total']}** ({seen_percent:.1f}%) | acertadas **{info['correct']}**")
        view = BibliotecaLinesPaginator(ctx.author, "Coleção de Arquivos da Biblioteca", lines)
        await ctx.send(embed=view.build_embed(), view=view)

    @biblioteca_group.command(name="loja", aliases=["shop"])
    async def loja_cmd(self, ctx):
        conn, cursor = self._connect()
        try:
            player = ensure_player(cursor, ctx.author.id)
            conn.commit()
        finally:
            conn.close()
        embed = self._basic_embed(
            "Loja da Biblioteca Perdida",
            f"Seu saldo: **{fmt(player.get('paginas', 0))} {BIBLIOTECA_CURRENCY}**",
            discord.Color.gold(),
        )
        lines = []
        for index, (item_id, item) in enumerate(BIBLIOTECA_SHOP.items(), start=1):
            limit = f" | limite {item['limite']} {item.get('periodo', '')}" if item.get("limite") else ""
            unique = " | único" if not item.get("repetivel", True) else ""
            lines.append(f"`{index}`/`{item_id}` **{item['nome']}** - {fmt(item['preco'])} páginas{unique}{limit}")
        embed.add_field(name="Itens", value=short("\n".join(lines)), inline=False)
        embed.set_footer(text="Use `echo biblioteca comprar <id> [quantidade]`. TutoriUAU: todo conhecimento vira loja em algum momento.")
        await ctx.send(embed=embed)

    @biblioteca_group.command(name="comprar", aliases=["buy", "resgatar"])
    async def comprar_cmd(self, ctx, item_ref: str = None, quantidade: int = 1):
        conn, cursor = self._connect()
        try:
            result = buy_shop_item(cursor, ctx.author.id, item_ref, quantidade)
            conn.commit()
        finally:
            conn.close()
        if result.get("error"):
            return await ctx.send(result["error"])
        await ctx.send(
            f"Compra concluída: **{result['quantity']}x {result['item']['nome']}** por **{fmt(result['price'])} Páginas Perdidas**. "
            "TutoriUAU carimbou o recibo e fingiu que não viu a empolgação."
        )

    async def admin_dispatch(self, ctx, action=None, payload=None):
        action_key = normalize_text(action).replace(" ", "_")
        conn, cursor = self._connect()
        try:
            if action_key in {"ativar", "abrir", "on"}:
                set_config(cursor, "active", "1")
                conn.commit()
                return await ctx.send("Biblioteca Perdida ativada. TutoriUAU abriu a porta com dramática falta de necessidade.")
            if action_key in {"desativar", "fechar", "off"}:
                set_config(cursor, "active", "0")
                conn.commit()
                return await ctx.send("Biblioteca Perdida desativada. As estantes vão fingir mistério até segunda ordem.")
            if action_key == "temporada":
                season = str(payload or "").strip()
                if not season:
                    return await ctx.send("Uso: `echo adm biblioteca temporada <nome>`")
                set_config(cursor, "season", season[:80])
                conn.commit()
                return await ctx.send(f"Temporada da Biblioteca definida como **{season[:80]}**.")
            if action_key == "listar":
                questions = load_questions(cursor)
                category_filter = normalize_text(payload)
                counts = {}
                for question in questions.values():
                    category = str(question.get("categoria", "Geral"))
                    if category_filter and category_filter not in normalize_text(category):
                        continue
                    counts[category] = counts.get(category, 0) + 1
                lines = [f"**{cat}**: {total}" for cat, total in sorted(counts.items(), key=lambda item: item[0].casefold())]
                embed = self._basic_embed(
                    "Perguntas da Biblioteca",
                    f"Total filtrado: **{sum(counts.values()):,}**\nTotal geral: **{len(questions):,}**",
                    discord.Color.dark_purple(),
                )
                embed.add_field(name="Categorias", value=short("\n".join(lines) or "Nada encontrado."), inline=False)
                return await ctx.send(embed=embed)
            if action_key == "testar":
                question_id = str(payload or "").strip()
                question = get_question(question_id, cursor)
                if not question:
                    return await ctx.send("Pergunta não encontrada. Use `echo adm biblioteca listar` para farejar o arquivo.")
                fake_session = {
                    "mode": "explorar",
                    "answered_ids": "[]",
                    "total_questions": 1,
                    "expires_at": now_ts() + 600,
                }
                return await self._send_question(ctx, fake_session, question, f"Teste ADM da pergunta `{question_id}`.")
            if action_key == "adicionar":
                if not payload:
                    return await ctx.send("Uso: `echo adm biblioteca adicionar id | categoria | dificuldade | pergunta | resposta | opcao1;opcao2;...`")
                try:
                    question_id = add_custom_question(cursor, ctx.author.id, payload)
                    conn.commit()
                except (ValueError, json.JSONDecodeError) as exc:
                    return await ctx.send(f"Não consegui adicionar: `{exc}`")
                return await ctx.send(f"Pergunta customizada **{question_id}** adicionada à Biblioteca.")
            if action_key == "remover":
                question_id = str(payload or "").strip()
                if not question_id:
                    return await ctx.send("Uso: `echo adm biblioteca remover <id_custom>`")
                cursor.execute("UPDATE biblioteca_custom_questions SET active = 0 WHERE id = ?", (question_id,))
                changed = cursor.rowcount
                conn.commit()
                if not changed:
                    return await ctx.send("Não encontrei pergunta customizada ativa com esse ID. Perguntas base ficam no arquivo do bot.")
                return await ctx.send(f"Pergunta customizada **{question_id}** removida.")
            return await ctx.send(
                "Comandos ADM da Biblioteca: `ativar`, `desativar`, `listar [categoria]`, `testar <id>`, "
                "`adicionar <dados>`, `remover <id_custom>`, `temporada <nome>`."
            )
        finally:
            conn.close()

    @app_commands.command(name="biblioteca", description="Mostra o painel da Biblioteca Perdida.")
    async def biblioteca_slash(self, interaction: discord.Interaction):
        conn, cursor = self._connect()
        try:
            player = ensure_player(cursor, interaction.user.id)
            active = biblioteca_is_active(cursor)
            conn.commit()
        finally:
            conn.close()
        await interaction.response.send_message(embed=self._panel_embed(interaction.user, player, active))


async def setup(bot):
    await bot.add_cog(Biblioteca(bot))
