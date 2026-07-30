import datetime
import random
import re
import sqlite3
import time

import discord
from discord.ext import commands

from data.casino_config import (
    BIG_WIN_LOG_THRESHOLD,
    BLACKJACK_TIMEOUT_SECONDS,
    CASINO_CURRENCY,
    CASINO_NAME,
    CHIP_PACKAGES,
    MAX_BET,
    MIN_BET,
)
from data.casino_dialogues import BUST_LINE, CLOSED_LINE, JACKPOT_LINE, LOSE_LINES, NO_CHIPS_LINE, OPEN_LINE, WIN_LINES
from data.casino_shop import CASINO_SHOP
from systems.blackjack_manager import (
    dealer_play,
    deserialize_hand,
    draw_card,
    draw_hand,
    format_hand_visual,
    hand_value,
    is_blackjack,
    serialize_hand,
)
from systems.casino_manager import (
    add_chips,
    add_daily_purchase,
    add_jackpot,
    add_stat,
    casino_is_active,
    chips_bought_today,
    claim_jackpot,
    count_purchases,
    ensure_casino_schema,
    get_balance,
    get_config,
    increase_active_bet,
    log_admin,
    now_ts,
    place_bet,
    record_history,
    remove_chips,
    settle_bet,
)
from systems.roulette_manager import normalize_bet_type, spin_roulette
from systems.slots_manager import format_slot_reels, slot_paytable_lines, spin_slots


def fmt(value):
    return f"{int(value or 0):,}".replace(",", ".")


def normalize_id(value):
    return str(value or "").strip().lower().replace(" ", "_")


def period_start(period):
    now = datetime.datetime.now()
    if period == "weekly":
        start = now - datetime.timedelta(days=now.weekday())
        return int(start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    if period == "monthly":
        return int(now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).timestamp())
    return 0


class CasinoTutorialView(discord.ui.View):
    def __init__(self, user, embeds):
        super().__init__(timeout=240)
        self.user = user
        self.embeds = embeds
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        self.btn_prev.disabled = self.page == 0
        self.btn_next.disabled = self.page >= len(self.embeds) - 1

    async def interaction_check(self, interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "Esse tutorial foi aberto por outra pessoa. Use `echo cassino tutorial` e ganhe sua própria apostila com julgamento embutido.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def btn_prev(self, interaction, button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary)
    async def btn_next(self, interaction, button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_users = set()
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_casino_schema(cursor)
        conn.commit()
        conn.close()

    def _connect(self):
        conn = sqlite3.connect("players.db")
        cursor = conn.cursor()
        ensure_casino_schema(cursor)
        return conn, cursor

    def _player_exists(self, cursor, user_id):
        cursor.execute("SELECT 1 FROM players WHERE user_id = ?", (str(user_id),))
        return cursor.fetchone() is not None

    def _shop_item_by_key(self, raw):
        if raw is None:
            return None, None
        key = normalize_id(raw)
        if key in CASINO_SHOP:
            return key, CASINO_SHOP[key]
        if str(raw).isdigit():
            index = int(raw) - 1
            keys = list(CASINO_SHOP.keys())
            if 0 <= index < len(keys):
                key = keys[index]
                return key, CASINO_SHOP[key]
        return None, None

    def _active_blackjack_session(self, cursor, user_id):
        cursor.execute("SELECT created_at FROM casino_blackjack_sessions WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return bool(row)

    async def _locked(self, ctx):
        user_id = str(ctx.author.id)
        if user_id in self.active_users:
            await ctx.send("Você já está em uma ação do cassino. A casa ama pressa, mas o banco odeia corrida duplicada.")
            return False
        self.active_users.add(user_id)
        return True

    def _unlock(self, user_id):
        self.active_users.discard(str(user_id))

    def _basic_embed(self, title, description, color=discord.Color.gold()):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="TutoriUAU: Fallen Angel, onde estatística vira entretenimento caro.")
        return embed

    def _slot_help_embed(self):
        embed = self._basic_embed(
            "🎰 Slot do Fallen Angel",
            (
                "`echo cassino slot <aposta>` gira três figuras.\n"
                "Duas figuras iguais já pagam prêmio. Três iguais pagam multiplicador alto. Três 👑 levam o jackpot."
            ),
            discord.Color.gold(),
        )
        embed.add_field(name="Tabela de Prêmios", value="\n".join(slot_paytable_lines()), inline=False)
        embed.add_field(
            name="Jackpot",
            value="Cada giro coloca **2% da aposta** no jackpot. O jackpot fica acumulado até alguém acertar três 👑.",
            inline=False,
        )
        return embed

    def _roulette_help_embed(self):
        embed = self._basic_embed(
            "🎡 Roleta do Fallen Angel",
            (
                "`echo cassino roleta <tipo> <aposta> [número]`\n\n"
                "A roleta usa números de **0 a 36**. O **0 é verde** e não conta como par/ímpar, baixo/alto, vermelho/preto."
            ),
            discord.Color.dark_red(),
        )
        embed.add_field(
            name="Apostas simples - pagam 2x",
            value=(
                "`vermelho` ou `preto`\n"
                "`par` ou `impar`\n"
                "`baixo` = 1 a 18\n"
                "`alto` = 19 a 36"
            ),
            inline=False,
        )
        embed.add_field(
            name="Número exato - paga 36x",
            value=(
                "Use `numero` e escolha um número de **0 a 36**.\n"
                "Exemplo: `echo cassino roleta numero 10 17` aposta 10 fichas no número 17."
            ),
            inline=False,
        )
        embed.add_field(
            name="Exemplos rápidos",
            value=(
                "`echo cassino roleta vermelho 25`\n"
                "`echo cassino roleta par 40`\n"
                "`echo cassino roleta alto 15`\n"
                "`echo cassino roleta numero 5 0`"
            ),
            inline=False,
        )
        embed.set_footer(text="TutoriUAU: 0 a 36. Se digitar 42, isso não é aposta, é pedido de socorro matemático.")
        return embed

    def _blackjack_embed(self, title, player_hand, dealer_hand, bet, status, payout=None, hide_dealer=False, color=None):
        embed = self._basic_embed(
            title,
            f"Aposta: **{fmt(bet)}** fichas\n{status}",
            color or discord.Color.dark_green(),
        )
        embed.add_field(
            name=f"Sua mão ({hand_value(player_hand)})",
            value=f"```{format_hand_visual(player_hand)}```",
            inline=False,
        )
        dealer_value = "?" if hide_dealer else hand_value(dealer_hand)
        embed.add_field(
            name=f"Dealer ({dealer_value})",
            value=f"```{format_hand_visual(dealer_hand, hide_first=hide_dealer)}```",
            inline=False,
        )
        if payout is not None:
            embed.add_field(name="Pagamento", value=f"**{fmt(payout)}** fichas", inline=True)
        embed.set_footer(text="TutoriUAU: pedir, parar, dobrar ou desistir. O dealer pisca pouco, mas julga muito.")
        return embed

    def _tutorial_embed(self, title, description, page, total, comment):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"TutoriUAU • Cassino {page}/{total} • {comment}")
        return embed

    def _casino_tutorial_pages(self):
        total = 6
        pages = []

        e1 = self._tutorial_embed(
            "Fallen Angel // Aula 1: O que é isso?",
            (
                f"O **{CASINO_NAME}** é o cassino oficial de Wolford.\n\n"
                f"A moeda daqui é **{CASINO_CURRENCY}**, separada do Gold. Você compra fichas com Gold, aposta fichas, "
                "ganha ou perde fichas, e só depois decide se vende de volta.\n\n"
                "Comando principal: `echo cassino`.\n"
                "Tutorial completo: `echo cassino tutorial`."
            ),
            1,
            total,
            "A casa sempre ganha, mas pelo menos agora ela explica o contrato.",
        )
        e1.add_field(
            name="Comandos básicos",
            value=(
                "`echo cassino saldo` - Mostra fichas, jackpot e estatísticas.\n"
                "`echo cassino comprar fichas <quantidade>` - Compra fichas com Gold.\n"
                "`echo cassino comprar <id da loja>` - Compra itens da loja do cassino.\n"
                "`echo cassino vender <fichas>` - Vende fichas por Gold.\n"
                "`echo cassino historico` - Mostra suas últimas apostas.\n"
                "`echo cassino ranking [categoria]` - Ranking da banca."
            ),
            inline=False,
        )
        e1.add_field(
            name="Limites",
            value=f"Aposta mínima: **{MIN_BET}** ficha.\nAposta máxima: **{fmt(MAX_BET)}** fichas.\nBlackjack expira em **10 minutos** se abandonar a mesa.",
            inline=False,
        )
        pages.append(e1)

        package_lines = [f"`{chips}` fichas = **{fmt(cost)} Gold**" for chips, cost in CHIP_PACKAGES.items()]
        e2 = self._tutorial_embed(
            "Fallen Angel // Aula 2: Comprar e vender fichas",
            (
                "Fichas são a trava de segurança da economia. Você não aposta Gold direto, porque alguém sempre tenta transformar "
                "uma brincadeira em crise monetária.\n\n"
                f"Taxa padrão: **100 Gold = 1 ficha**.\nVenda: **1 ficha = 50 Gold**.\nLimite diário de compra: **500 fichas**."
            ),
            2,
            total,
            "Comprar é fácil. Vender pela metade é a parte educativa.",
        )
        e2.add_field(name="Pacotes com desconto", value="\n".join(package_lines), inline=False)
        e2.add_field(
            name="Exemplos",
            value=(
                "`echo cassino comprar fichas 10` - compra 10 fichas por 1.000 Gold.\n"
                "`echo cassino comprar fichas 110` - compra pacote de 110 fichas por 10.000 Gold.\n"
                "`echo cassino vender 20` - vende 20 fichas por 1.000 Gold."
            ),
            inline=False,
        )
        pages.append(e2)

        e3 = self._tutorial_embed(
            "Fallen Angel // Aula 3: Jogos rápidos",
            (
                "Esses são os jogos de aposta imediata. Você manda o comando, a banca resolve, o histórico registra e o TutoriUAU comenta "
                "com o tato emocional de uma máquina registradora."
            ),
            3,
            total,
            "Se você chamar isso de investimento, eu vou tossir em binário.",
        )
        e3.add_field(
            name="Cara ou Coroa",
            value=(
                "`echo cassino cara <aposta>` ou `echo cassino coroa <aposta>`.\n"
                "Chance 50/50. Se vencer, recebe **2x** a aposta em pagamento bruto."
            ),
            inline=False,
        )
        e3.add_field(
            name="Slot",
            value=(
                "`echo cassino slot <aposta>`.\n"
                "Símbolos possuem pesos diferentes. Trincas pagam multiplicadores fortes; duas iguais também pagam prêmio.\n"
                "Cada giro alimenta o jackpot com 2% da aposta. Três **COROA** levam o jackpot."
            ),
            inline=False,
        )
        pages.append(e3)

        e4 = self._tutorial_embed(
            "Fallen Angel // Aula 4: Roleta e Blackjack",
            (
                "Aqui começa a mesa com pose. Roleta é aposta seca; blackjack permite decisão no meio da partida."
            ),
            4,
            total,
            "Matemática, sorte e escolhas ruins sentaram na mesma mesa.",
        )
        e4.add_field(
            name="Roleta",
            value=(
                "`echo cassino roleta <tipo> <aposta> [número]`\n"
                "Tipos: `vermelho`, `preto`, `par`, `impar`, `baixo`, `alto`, `numero`.\n"
                "A escolha por número vai de **0 a 36**.\n"
                "Vermelho/preto/par/ímpar/baixo/alto pagam **2x**. Número exato paga **36x**.\n"
                "Exemplo: `echo cassino roleta numero 10 17`."
            ),
            inline=False,
        )
        e4.add_field(
            name="Blackjack",
            value=(
                "`echo cassino blackjack <aposta>` inicia uma mão.\n"
                "`echo cassino pedir` compra carta.\n"
                "`echo cassino parar` enfrenta o dealer.\n"
                "`echo cassino dobrar` dobra a aposta, compra uma carta e para.\n"
                "`echo cassino desistir` encerra a mão e devolve metade da aposta.\n"
                "Blackjack natural paga **2,5x**; vitória normal paga **2x**; empate devolve a aposta. Com 5 cartas sem estourar, você vence automaticamente."
            ),
            inline=False,
        )
        pages.append(e4)

        e5 = self._tutorial_embed(
            "Fallen Angel // Aula 5: Loja, histórico e ranking",
            (
                "Ganhar ficha e não gastar é maturidade. Gastar em cosmético é personalidade. O sistema aceita os dois, mas julga em silêncio."
            ),
            5,
            total,
            "A loja vende glamour; autocontrole ficou fora de estoque.",
        )
        e5.add_field(
            name="Loja do Cassino",
            value=(
                "`echo cassino loja` mostra os prêmios.\n"
                "`echo cassino comprar <id> [quantidade]` compra um item pelo número/id da loja.\n"
                "`echo cassino comprar_item <id> [quantidade]` também funciona, caso você goste do caminho explícito.\n"
                "Tem títulos, temas de perfil, tickets, Gems, itens e pets exclusivos como **Dado Vivo** e **Mini Dealer**.\n"
                "Itens únicos só podem ser comprados uma vez; alguns itens têm limite semanal."
            ),
            inline=False,
        )
        e5.add_field(
            name="Controle e competição",
            value=(
                "`echo cassino historico [quantidade]` mostra até 15 apostas recentes.\n"
                "`echo cassino ranking fichas` mostra quem tem mais fichas.\n"
                "Outras categorias: `maior_vitoria`, `apostado`, `perdido`, `vitorias`."
            ),
            inline=False,
        )
        pages.append(e5)

        e6 = self._tutorial_embed(
            "Fallen Angel // Aula 6: Staff, segurança e boas práticas",
            (
                "O cassino tem logs, limites e comandos de controle para não virar uma máquina de imprimir caos.\n\n"
                "Apostas entram no histórico, grandes vitórias vão para log administrativo, compras ficam registradas e o blackjack fica preso ao jogador até acabar ou expirar."
            ),
            6,
            total,
            "Parabéns. Você leu o manual. Isso já te coloca acima de 73% dos aventureiros.",
        )
        e6.add_field(
            name="Comandos ADM",
            value=(
                "`echo adm cassino abrir` - Abre o cassino.\n"
                "`echo adm cassino fechar` - Fecha o cassino.\n"
                "`echo adm cassino jackpot` - Consulta o jackpot.\n"
                "`echo adm cassino jackpot <valor>` - Define o jackpot.\n"
                "`echo adm cassino jackpot add <valor>` - Soma fichas ao jackpot.\n"
                "`echo adm cassino dar_fichas @user <qtd>` - Dá fichas.\n"
                "`echo adm cassino remover_fichas @user <qtd>` - Remove fichas."
            ),
            inline=False,
        )
        e6.add_field(
            name="Dica do TutoriUAU",
            value=(
                "Use apostas pequenas para testar os jogos. Se perder tudo, isso não foi azar: foi o tutorial sendo ignorado em tempo real."
            ),
            inline=False,
        )
        pages.append(e6)
        return pages

    async def _expire_blackjack_if_needed(self, ctx, cursor, user_id):
        cursor.execute(
            "SELECT bet, player_hand, dealer_hand, created_at FROM casino_blackjack_sessions WHERE user_id = ?",
            (str(user_id),),
        )
        row = cursor.fetchone()
        if not row:
            return False
        bet, player_raw, dealer_raw, created_at = row
        if now_ts() - int(created_at or 0) <= BLACKJACK_TIMEOUT_SECONDS:
            return False

        settle_bet(
            cursor,
            user_id,
            "blackjack",
            int(bet),
            0,
            "abandono",
            "Sessão expirada por abandono.",
        )
        cursor.execute("DELETE FROM casino_blackjack_sessions WHERE user_id = ?", (str(user_id),))
        await ctx.send("Sua partida antiga de blackjack expirou. O dealer venceu por abandono. Frio? Sim. Contratual? Também.")
        return True

    @commands.group(name="cassino", aliases=["casino"], invoke_without_command=True)
    async def cassino_group(self, ctx):
        conn, cursor = self._connect()
        config = get_config(cursor)
        balance = get_balance(cursor, ctx.author.id) if self._player_exists(cursor, ctx.author.id) else 0
        conn.commit()
        conn.close()

        embed = self._basic_embed(
            f"{CASINO_NAME} // Cassino de Wolford",
            (
                f"Status: **{'Aberto' if config['active'] else 'Fechado'}**\n"
                f"Sua carteira: **{fmt(balance)}** fichas\n"
                f"Jackpot atual: **{fmt(config['jackpot'])}** fichas\n\n"
                "A moeda daqui é separada do Gold comum. Traduzindo: dá para controlar a economia antes que alguém tente financiar uma calamidade com caça-níquel."
            ),
        )
        embed.add_field(
            name="Carteira",
            value=(
                "`echo cassino saldo`\n"
                "`echo cassino comprar fichas <qtd>`\n"
                "`echo cassino vender <fichas>`"
            ),
            inline=True,
        )
        embed.add_field(
            name="Jogos",
            value=(
                "`echo cassino cara <aposta>` / `coroa <aposta>`\n"
                "`echo cassino slot <aposta>`\n"
                "`echo cassino roleta <tipo> <aposta> [número]`\n"
                "`echo cassino blackjack <aposta>`"
            ),
            inline=False,
        )
        embed.add_field(
            name="Extras",
            value="`tutorial`, `loja`, `comprar_item`, `historico`, `ranking`, `pedir`, `parar`, `dobrar`, `desistir`.",
            inline=False,
        )
        await ctx.send(embed=embed)

    @cassino_group.command(name="tutorial", aliases=["guia", "manual", "regras", "ajuda"])
    async def tutorial_cmd(self, ctx):
        embeds = self._casino_tutorial_pages()
        view = CasinoTutorialView(ctx.author, embeds)
        await ctx.send(embed=embeds[0], view=view)

    @cassino_group.command(name="saldo", aliases=["carteira", "fichas"])
    async def saldo_cmd(self, ctx):
        conn, cursor = self._connect()
        if not self._player_exists(cursor, ctx.author.id):
            conn.close()
            return await ctx.send("Use `echo iniciar` antes de tentar entrar no Fallen Angel. Até cassino exige RG.")
        config = get_config(cursor)
        balance = get_balance(cursor, ctx.author.id)
        bought = chips_bought_today(cursor, ctx.author.id)
        cursor.execute(
            """
            SELECT total_bet, total_won, total_lost, biggest_win, games_played
            FROM casino_players WHERE user_id = ?
            """,
            (str(ctx.author.id),),
        )
        total_bet, total_won, total_lost, biggest_win, games_played = cursor.fetchone()
        conn.commit()
        conn.close()

        embed = self._basic_embed(
            f"Carteira do {CASINO_NAME}",
            f"Saldo: **{fmt(balance)}** fichas\nJackpot: **{fmt(config['jackpot'])}** fichas",
        )
        embed.add_field(name="Hoje", value=f"Compradas: **{fmt(bought)}/{fmt(config['daily_buy_limit'])}**", inline=True)
        embed.add_field(name="Histórico", value=f"Jogos: **{fmt(games_played)}**\nApostado: **{fmt(total_bet)}**", inline=True)
        embed.add_field(name="Resultado", value=f"Lucro bruto: **{fmt(total_won)}**\nPerdas: **{fmt(total_lost)}**\nMaior vitória: **{fmt(biggest_win)}**", inline=False)
        await ctx.send(embed=embed)

    def _purchase_help_text(self):
        linhas = [f"`{chips}` fichas - **{fmt(cost)} Gold**" for chips, cost in CHIP_PACKAGES.items()]
        return (
            "**Comprar fichas:**\n"
            "`echo cassino comprar fichas <quantidade>`\n"
            + "\n".join(linhas)
            + "\n\n**Comprar item da loja:**\n"
            "`echo cassino comprar <id da loja> [quantidade]`\n"
            "`echo cassino comprar item <id da loja> [quantidade]`\n"
            "`echo cassino comprar_item <id da loja> [quantidade]`\n\n"
            "TutoriUAU: agora a palavra `fichas` existe para impedir o clássico 'comprei moeda quando queria um chapéu'."
        )

    async def _buy_chips(self, ctx, fichas):
        if fichas is None:
            linhas = [f"`{chips}` fichas - **{fmt(cost)} Gold**" for chips, cost in CHIP_PACKAGES.items()]
            return await ctx.send(
                "**Pacotes de fichas do Fallen Angel:**\n"
                + "\n".join(linhas)
                + "\n\nUse `echo cassino comprar fichas <quantidade>`.\nTutoriUAU: pacote maior dá desconto, não sabedoria."
            )
        try:
            fichas = int(fichas)
        except (TypeError, ValueError):
            return await ctx.send("A quantidade de fichas precisa ser um número. Exemplo: `echo cassino comprar fichas 110`.")
        if fichas <= 0:
            return await ctx.send("Compre uma quantidade positiva de fichas. Dívida emocional não conta.")

        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            if not casino_is_active(cursor):
                return await ctx.send(CLOSED_LINE)

            config = get_config(cursor)
            bought = chips_bought_today(cursor, user_id)
            if bought + fichas > config["daily_buy_limit"]:
                return await ctx.send(
                    f"Limite diário excedido. Você já comprou **{fmt(bought)}** e o limite é **{fmt(config['daily_buy_limit'])}** fichas."
                )

            cost = CHIP_PACKAGES.get(fichas, fichas * config["chip_buy_rate"])
            cursor.execute("SELECT gold FROM players WHERE user_id = ?", (user_id,))
            gold = int((cursor.fetchone() or [0])[0] or 0)
            if gold < cost:
                return await ctx.send(f"Gold insuficiente. Precisa de **{fmt(cost)} Gold** e você tem **{fmt(gold)}**.")

            cursor.execute("UPDATE players SET gold = gold - ? WHERE user_id = ?", (cost, user_id))
            add_chips(cursor, user_id, fichas, reason="compra_fichas")
            add_daily_purchase(cursor, user_id, fichas)
            add_stat(cursor, user_id, "casino_chips_bought", fichas)
            conn.commit()
            await ctx.send(f"Você comprou **{fmt(fichas)}** fichas por **{fmt(cost)} Gold**. {random.choice(WIN_LINES)}")
        finally:
            conn.close()
            self._unlock(user_id)

    @cassino_group.command(name="comprar", aliases=["comprarfichas", "buy"])
    async def comprar_cmd(self, ctx, *, entrada: str = None):
        if not entrada:
            return await ctx.send(self._purchase_help_text())

        parts = str(entrada).split()
        first = normalize_id(parts[0]) if parts else ""

        if normalize_id(ctx.invoked_with) == "comprarfichas":
            return await self._buy_chips(ctx, parts[0] if parts else None)

        if first in {"ficha", "fichas", "chip", "chips", "moeda", "moedas"}:
            amount = parts[1] if len(parts) >= 2 else None
            return await self._buy_chips(ctx, amount)

        if first in {"item", "itens", "loja", "shop", "resgatar"}:
            if len(parts) < 2:
                return await ctx.send("Use `echo cassino comprar item <id da loja> [quantidade]`.")
            quantity = int(parts[2]) if len(parts) >= 3 and str(parts[2]).isdigit() else 1
            return await self._buy_shop_item(ctx, parts[1], quantity)

        item_id, item = self._shop_item_by_key(parts[0])
        if item:
            quantity = int(parts[1]) if len(parts) >= 2 and str(parts[1]).isdigit() else 1
            return await self._buy_shop_item(ctx, parts[0], quantity)

        if str(parts[0]).isdigit():
            return await self._buy_chips(ctx, parts[0])

        return await ctx.send(
            "Não entendi a compra. Use `echo cassino comprar fichas <qtd>` para fichas ou "
            "`echo cassino comprar <id da loja>` para item."
        )

    @cassino_group.command(name="vender", aliases=["sell", "sacar"])
    async def vender_fichas_cmd(self, ctx, fichas: int = None):
        if fichas is None or fichas <= 0:
            return await ctx.send("Use `echo cassino vender <fichas>`. O caixa não lê pensamentos, ainda bem.")
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            config = get_config(cursor)
            if not remove_chips(cursor, user_id, fichas):
                return await ctx.send(NO_CHIPS_LINE)
            gold = fichas * config["chip_sell_rate"]
            cursor.execute("UPDATE players SET gold = gold + ? WHERE user_id = ?", (gold, user_id))
            log_admin(cursor, user_id, "casino_venda_fichas", f"-{fmt(fichas)} fichas | +{fmt(gold)} Gold")
            conn.commit()
            await ctx.send(f"Você vendeu **{fmt(fichas)}** fichas por **{fmt(gold)} Gold**. A casa comprou de volta com cara de quem ainda saiu ganhando.")
        finally:
            conn.close()
            self._unlock(user_id)

    async def _coinflip(self, ctx, choice, bet):
        if bet is None:
            return await ctx.send(f"Use `echo cassino {choice} <aposta>`.")
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            if await self._expire_blackjack_if_needed(ctx, cursor, user_id):
                conn.commit()
            if self._active_blackjack_session(cursor, user_id):
                return await ctx.send("Termine seu blackjack antes de apostar em outro jogo.")
            ok, value = place_bet(cursor, user_id, bet)
            if not ok:
                return await ctx.send(str(value))
            bet = value
            result_side = random.choice(["cara", "coroa"])
            won = result_side == choice
            payout = bet * 2 if won else 0
            settle_bet(cursor, user_id, "cara_ou_coroa", bet, payout, "win" if won else "loss", f"Escolha: {choice}. Caiu: {result_side}.", "coinflip_wins")
            conn.commit()
            line = random.choice(WIN_LINES if won else LOSE_LINES)
            await ctx.send(f"Moeda lançada: **{result_side.upper()}**.\nResultado: **{'vitória' if won else 'derrota'}** | Pagamento: **{fmt(payout)}** fichas.\n*{line}*")
        finally:
            conn.close()
            self._unlock(user_id)

    @cassino_group.command(name="cara")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cara_cmd(self, ctx, aposta: int = None):
        await self._coinflip(ctx, "cara", aposta)

    @cassino_group.command(name="coroa")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def coroa_cmd(self, ctx, aposta: int = None):
        await self._coinflip(ctx, "coroa", aposta)

    @cassino_group.command(name="slot", aliases=["slots", "cacaniquel", "caça-níquel"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slot_cmd(self, ctx, aposta: int = None):
        if aposta is None:
            return await ctx.send(embed=self._slot_help_embed())
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            if await self._expire_blackjack_if_needed(ctx, cursor, user_id):
                conn.commit()
            if self._active_blackjack_session(cursor, user_id):
                return await ctx.send("Termine seu blackjack antes de puxar a alavanca.")
            ok, value = place_bet(cursor, user_id, aposta)
            if not ok:
                return await ctx.send(str(value))
            aposta = value
            jackpot_add = max(1, int(aposta * 0.02))
            add_jackpot(cursor, jackpot_add)
            jackpot = get_config(cursor)["jackpot"]
            spin = spin_slots(aposta, jackpot)
            payout = spin["payout"]
            if spin["jackpot_win"]:
                claimed = claim_jackpot(cursor)
                payout = aposta * 150 + claimed
                add_stat(cursor, user_id, "casino_jackpots", 1)
                log_admin(cursor, user_id, "casino_jackpot", f"{fmt(claimed)} fichas no slot")
            settle_bet(cursor, user_id, "slot", aposta, payout, spin["result"], spin["details"], "slots_wins")
            conn.commit()
            line = JACKPOT_LINE if spin["jackpot_win"] else random.choice(WIN_LINES if payout > aposta else LOSE_LINES)
            embed = self._basic_embed(
                "🎰 Slot do Fallen Angel",
                f"```{format_slot_reels(spin['reels'])}```",
                discord.Color.gold() if payout > aposta else discord.Color.dark_gold(),
            )
            embed.add_field(name="Resultado", value=f"**{spin['result'].title()}**\n{spin['details']}", inline=True)
            embed.add_field(name="Pagamento", value=f"**{fmt(payout)}** fichas", inline=True)
            embed.add_field(name="Jackpot", value=f"Recebeu **{fmt(jackpot_add)}** ficha(s) neste giro.", inline=False)
            embed.set_footer(text=f"TutoriUAU: {line}")
            await ctx.send(embed=embed)
        finally:
            conn.close()
            self._unlock(user_id)

    @cassino_group.command(name="roleta", aliases=["roulette"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def roleta_cmd(self, ctx, tipo: str = None, aposta: int = None, numero: int = None):
        if not tipo or normalize_id(tipo) in {"ajuda", "help", "regras", "tutorial", "como"}:
            return await ctx.send(embed=self._roulette_help_embed())
        if aposta is None:
            return await ctx.send(embed=self._roulette_help_embed())
        tipo = normalize_bet_type(tipo)
        if tipo not in {"vermelho", "preto", "par", "impar", "baixo", "alto", "numero"}:
            return await ctx.send("Tipo de aposta inválido. Use `echo cassino roleta ajuda` para ver as opções e exemplos.")
        if tipo == "numero":
            if numero is None:
                return await ctx.send("Aposta em número exige um número de **0 a 36**. Exemplo: `echo cassino roleta numero 10 17`.")
            if not 0 <= int(numero) <= 36:
                return await ctx.send("O número da roleta precisa estar entre **0 e 36**.")
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            if await self._expire_blackjack_if_needed(ctx, cursor, user_id):
                conn.commit()
            if self._active_blackjack_session(cursor, user_id):
                return await ctx.send("Termine seu blackjack antes de girar a roleta.")
            ok, value = place_bet(cursor, user_id, aposta)
            if not ok:
                return await ctx.send(str(value))
            aposta = value
            result = spin_roulette(tipo, aposta, numero)
            if result["won"] and "numero" in result["details"]:
                add_stat(cursor, user_id, "casino_roulette_exact", 1)
            settle_bet(cursor, user_id, "roleta", aposta, result["payout"], result["result"], result["details"], "roulette_wins")
            conn.commit()
            line = random.choice(WIN_LINES if result["won"] else LOSE_LINES)
            color_icon = {"vermelho": "🔴", "preto": "⚫", "verde": "🟢"}.get(result["color"], "⚪")
            embed_color = discord.Color.green() if result["color"] == "verde" else (discord.Color.red() if result["color"] == "vermelho" else discord.Color.dark_grey())
            embed = self._basic_embed(
                "🎡 Roleta do Fallen Angel",
                f"A bolinha caiu em **{color_icon} {result['number']} ({result['color']})**.",
                embed_color,
            )
            embed.add_field(name="Sua aposta", value=f"`{tipo}` {fmt(aposta)} ficha(s){f' no número {numero}' if tipo == 'numero' else ''}", inline=False)
            embed.add_field(name="Resultado", value="**Vitória**" if result["won"] else "**Derrota**", inline=True)
            embed.add_field(name="Pagamento", value=f"**{fmt(result['payout'])}** fichas", inline=True)
            embed.set_footer(text=f"TutoriUAU: {line}")
            await ctx.send(embed=embed)
        finally:
            conn.close()
            self._unlock(user_id)

    @cassino_group.command(name="blackjack", aliases=["bj", "vinteum"])
    async def blackjack_cmd(self, ctx, aposta: int = None):
        if aposta is None:
            return await ctx.send("Use `echo cassino blackjack <aposta>`. Depois: `pedir`, `parar`, `dobrar` ou `desistir`.")
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            await self._expire_blackjack_if_needed(ctx, cursor, user_id)
            cursor.execute("SELECT 1 FROM casino_blackjack_sessions WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return await ctx.send("Você já está em uma partida de blackjack. Use `echo cassino pedir`, `parar`, `dobrar` ou `desistir`.")
            ok, value = place_bet(cursor, user_id, aposta)
            if not ok:
                return await ctx.send(str(value))
            aposta = value
            player_hand = draw_hand()
            dealer_hand = draw_hand()
            if is_blackjack(player_hand):
                if is_blackjack(dealer_hand):
                    payout = aposta
                    result = "push"
                    details = "Blackjack natural dos dois lados."
                    status = "Blackjack natural dos dois lados. Empate elegante, daqueles que fingem profundidade."
                else:
                    payout = int(aposta * 2.5)
                    result = "blackjack"
                    details = "Blackjack natural do jogador."
                    status = "Blackjack natural. Você entrou, sentou e humilhou a mesa antes do dealer terminar a pose."
                    add_stat(cursor, user_id, "casino_blackjack_natural", 1)
                settle_bet(cursor, user_id, "blackjack", aposta, payout, result, details, "blackjack_wins")
                conn.commit()
                return await ctx.send(embed=self._blackjack_embed(
                    "🃏 Blackjack - Resultado",
                    player_hand,
                    dealer_hand,
                    aposta,
                    status,
                    payout,
                    hide_dealer=False,
                    color=discord.Color.green() if payout > aposta else discord.Color.light_grey(),
                ))
            cursor.execute(
                """
                INSERT INTO casino_blackjack_sessions (user_id, bet, player_hand, dealer_hand, status, created_at)
                VALUES (?, ?, ?, ?, 'active', ?)
                """,
                (user_id, aposta, serialize_hand(player_hand), serialize_hand(dealer_hand), now_ts()),
            )
            conn.commit()
            embed = self._blackjack_embed(
                "🃏 Blackjack do Fallen Angel",
                player_hand,
                dealer_hand,
                aposta,
                "Mesa aberta. Chegue em 21, vença o dealer ou consiga 5 cartas sem estourar.",
                hide_dealer=True,
            )
            embed.add_field(
                name="Ações",
                value="`echo cassino pedir` | `parar` | `dobrar` | `desistir`",
                inline=False,
            )
            await ctx.send(embed=embed)
        finally:
            conn.close()
            self._unlock(user_id)

    async def _finish_blackjack(self, ctx, cursor, user_id, player_hand, dealer_hand, bet):
        dealer_hand = dealer_play(dealer_hand)
        player_value = hand_value(player_hand)
        dealer_value = hand_value(dealer_hand)
        if dealer_value > 21 or player_value > dealer_value:
            payout = bet * 2
            result = "win"
            line = random.choice(WIN_LINES)
            win_stat = "blackjack_wins"
        elif player_value == dealer_value:
            payout = bet
            result = "push"
            line = "Empate. A emoção passou, a carteira ficou no mesmo lugar. Quase poesia."
            win_stat = None
        else:
            payout = 0
            result = "loss"
            line = random.choice(LOSE_LINES)
            win_stat = None
        settle_bet(cursor, user_id, "blackjack", bet, payout, result, f"Jogador {player_value} vs Dealer {dealer_value}", win_stat)
        cursor.execute("DELETE FROM casino_blackjack_sessions WHERE user_id = ?", (str(user_id),))
        await ctx.send(embed=self._blackjack_embed(
            "🃏 Blackjack - Resultado",
            player_hand,
            dealer_hand,
            bet,
            f"Resultado: **{result}**. {line}",
            payout,
            hide_dealer=False,
            color=discord.Color.green() if payout > bet else (discord.Color.light_grey() if payout == bet else discord.Color.red()),
        ))

    async def _blackjack_action(self, ctx, action):
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            expired = await self._expire_blackjack_if_needed(ctx, cursor, user_id)
            if expired:
                conn.commit()
                return
            cursor.execute(
                "SELECT bet, player_hand, dealer_hand FROM casino_blackjack_sessions WHERE user_id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row:
                return await ctx.send("Você não tem blackjack ativo. Use `echo cassino blackjack <aposta>`.")
            bet, player_raw, dealer_raw = row
            bet = int(bet)
            player_hand = deserialize_hand(player_raw)
            dealer_hand = deserialize_hand(dealer_raw)

            if action == "desistir":
                payout = bet // 2
                settle_bet(cursor, user_id, "blackjack", bet, payout, "desistiu", "Jogador desistiu da mão e recuperou metade da aposta.")
                cursor.execute("DELETE FROM casino_blackjack_sessions WHERE user_id = ?", (user_id,))
                conn.commit()
                return await ctx.send(embed=self._blackjack_embed(
                    "🃏 Blackjack - Desistência",
                    player_hand,
                    dealer_hand,
                    bet,
                    "Você desistiu da mão e recuperou metade da aposta. O dealer agradeceu sem expressão facial, que é o jeito dele sorrir.",
                    payout,
                    hide_dealer=True,
                    color=discord.Color.light_grey(),
                ))

            if action == "dobrar":
                if len(player_hand) != 2:
                    return await ctx.send("Só dá para dobrar logo no começo da mão.")
                if not increase_active_bet(cursor, user_id, bet):
                    return await ctx.send("Fichas insuficientes para dobrar.")
                bet *= 2
                player_hand.append(draw_card())
                if hand_value(player_hand) > 21:
                    settle_bet(cursor, user_id, "blackjack", bet, 0, "bust", f"Estourou com {hand_value(player_hand)}.")
                    cursor.execute("DELETE FROM casino_blackjack_sessions WHERE user_id = ?", (user_id,))
                    conn.commit()
                    return await ctx.send(embed=self._blackjack_embed(
                        "🃏 Blackjack - Estourou",
                        player_hand,
                        dealer_hand,
                        bet,
                        BUST_LINE,
                        0,
                        hide_dealer=False,
                        color=discord.Color.red(),
                    ))
                await self._finish_blackjack(ctx, cursor, user_id, player_hand, dealer_hand, bet)
                conn.commit()
                return

            if action == "pedir":
                player_hand.append(draw_card())
                if hand_value(player_hand) > 21:
                    settle_bet(cursor, user_id, "blackjack", bet, 0, "bust", f"Estourou com {hand_value(player_hand)}.")
                    cursor.execute("DELETE FROM casino_blackjack_sessions WHERE user_id = ?", (user_id,))
                    conn.commit()
                    return await ctx.send(embed=self._blackjack_embed(
                        "🃏 Blackjack - Estourou",
                        player_hand,
                        dealer_hand,
                        bet,
                        BUST_LINE,
                        0,
                        hide_dealer=False,
                        color=discord.Color.red(),
                    ))
                if len(player_hand) >= 5:
                    payout = bet * 2
                    settle_bet(cursor, user_id, "blackjack", bet, payout, "five_card", "Cinco cartas sem estourar.")
                    cursor.execute("DELETE FROM casino_blackjack_sessions WHERE user_id = ?", (user_id,))
                    conn.commit()
                    return await ctx.send(embed=self._blackjack_embed(
                        "🃏 Blackjack - 5 Cartas",
                        player_hand,
                        dealer_hand,
                        bet,
                        "Cinco cartas sem estourar. Vitória automática, porque até a banca respeita esse malabarismo.",
                        payout,
                        hide_dealer=True,
                        color=discord.Color.green(),
                    ))
                cursor.execute(
                    "UPDATE casino_blackjack_sessions SET player_hand = ? WHERE user_id = ?",
                    (serialize_hand(player_hand), user_id),
                )
                conn.commit()
                return await ctx.send(embed=self._blackjack_embed(
                    "🃏 Blackjack - Sua vez",
                    player_hand,
                    dealer_hand,
                    bet,
                    "Carta comprada. Pode pedir de novo, parar, dobrar ou desistir.",
                    hide_dealer=True,
                ))

            if action == "parar":
                await self._finish_blackjack(ctx, cursor, user_id, player_hand, dealer_hand, bet)
                conn.commit()
                return
        finally:
            conn.close()
            self._unlock(user_id)

    @cassino_group.command(name="pedir", aliases=["hit"])
    async def blackjack_pedir_cmd(self, ctx):
        await self._blackjack_action(ctx, "pedir")

    @cassino_group.command(name="parar", aliases=["stand"])
    async def blackjack_parar_cmd(self, ctx):
        await self._blackjack_action(ctx, "parar")

    @cassino_group.command(name="dobrar", aliases=["double"])
    async def blackjack_dobrar_cmd(self, ctx):
        await self._blackjack_action(ctx, "dobrar")

    @cassino_group.command(name="desistir", aliases=["surrender"])
    async def blackjack_desistir_cmd(self, ctx):
        await self._blackjack_action(ctx, "desistir")

    @cassino_group.command(name="loja", aliases=["shop"])
    async def loja_cmd(self, ctx):
        conn, cursor = self._connect()
        balance = get_balance(cursor, ctx.author.id) if self._player_exists(cursor, ctx.author.id) else 0
        conn.commit()
        conn.close()
        embed = self._basic_embed("Loja do Fallen Angel", f"Seu saldo: **{fmt(balance)}** fichas")
        lines = []
        for index, (item_id, item) in enumerate(CASINO_SHOP.items(), start=1):
            limit = ""
            if item.get("limite"):
                limit = f" | limite {item['limite']} {item.get('periodo', '')}"
            unique = " | único" if not item.get("repetivel", True) else ""
            lines.append(f"`{index}`/`{item_id}` **{item['nome']}** - {fmt(item['preco'])} fichas{unique}{limit}")
        chunks = ["\n".join(lines[i:i + 8]) for i in range(0, len(lines), 8)]
        for idx, chunk in enumerate(chunks, start=1):
            embed.add_field(name="Itens" if idx == 1 else f"Itens {idx}", value=chunk, inline=False)
        embed.set_footer(text="Use `echo cassino comprar <id> [quantidade]` ou `echo cassino comprar_item <id> [quantidade]`. TutoriUAU: não vendemos bom senso.")
        await ctx.send(embed=embed)

    def _grant_shop_item(self, cursor, user_id, item):
        kind = item["tipo"]
        quantity = int(item.get("quantidade", 1))
        if kind in {"title", "frame"}:
            token = item["item_id"]
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, token))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE inventory SET quantity = quantity + 1 WHERE id = ?", (row[0],))
            else:
                cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, 1)", (user_id, token))
            cursor.execute(
                """
                INSERT OR IGNORE INTO player_cosmetics (user_id, cosmetic_id, type, active, purchased_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (user_id, token, "title" if kind == "title" else "frame", now_ts()),
            )
        elif kind == "tickets":
            cursor.execute("INSERT OR IGNORE INTO summon_data (user_id) VALUES (?)", (user_id,))
            cursor.execute("UPDATE summon_data SET summon_tickets = summon_tickets + ? WHERE user_id = ?", (quantity, user_id))
        elif kind == "gems":
            cursor.execute("UPDATE players SET gems = COALESCE(gems, 0) + ? WHERE user_id = ?", (quantity, user_id))
        elif kind == "pet":
            cursor.execute(
                "INSERT INTO pets (user_id, pet_id, pet_name, rarity, level, xp) VALUES (?, ?, ?, ?, 1, 0)",
                (user_id, item["pet_id"], item["pet_name"], int(item.get("raridade", 4))),
            )
        else:
            item_id = item["item_id"]
            cursor.execute("SELECT id FROM inventory WHERE user_id = ? AND item_name = ?", (user_id, item_id))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (quantity, row[0]))
            else:
                cursor.execute("INSERT INTO inventory (user_id, item_name, quantity) VALUES (?, ?, ?)", (user_id, item_id, quantity))

    async def _buy_shop_item(self, ctx, item_ref: str = None, quantidade: int = 1):
        item_id, item = self._shop_item_by_key(item_ref)
        if not item:
            return await ctx.send("Item inválido. Use `echo cassino loja` para ver a lista.")
        quantidade = max(1, int(quantidade or 1))
        if not item.get("repetivel", True):
            quantidade = 1
        user_id = str(ctx.author.id)
        if not await self._locked(ctx):
            return
        conn, cursor = self._connect()
        try:
            if not self._player_exists(cursor, user_id):
                return await ctx.send("Use `echo iniciar` primeiro.")
            if not casino_is_active(cursor):
                return await ctx.send(CLOSED_LINE)
            if not item.get("repetivel", True) and count_purchases(cursor, user_id, item_id, 0) > 0:
                return await ctx.send("Você já comprou esse item único. O cassino vende vício, não duplicata.")
            if item.get("limite"):
                start = period_start(item.get("periodo"))
                used = count_purchases(cursor, user_id, item_id, start)
                if used + quantidade > int(item["limite"]):
                    return await ctx.send(f"Limite do item atingido. Você já comprou **{used}/{item['limite']}** neste período.")
            total_price = int(item["preco"]) * quantidade
            if not remove_chips(cursor, user_id, total_price):
                return await ctx.send(NO_CHIPS_LINE)
            for _ in range(quantidade):
                self._grant_shop_item(cursor, user_id, item)
            cursor.execute(
                "INSERT INTO casino_purchases (user_id, item_id, price, quantity, purchased_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, item_id, int(item["preco"]), quantidade, now_ts()),
            )
            add_stat(cursor, user_id, "casino_shop_purchases", quantidade)
            log_admin(cursor, user_id, "casino_compra_loja", f"{quantidade}x {item_id} por {fmt(total_price)} fichas")
            conn.commit()
            await ctx.send(f"Compra concluída: **{quantidade}x {item['nome']}** por **{fmt(total_price)}** fichas. TutoriUAU carimbou o recibo com julgamento silencioso.")
        finally:
            conn.close()
            self._unlock(user_id)

    @cassino_group.command(name="comprar_item", aliases=["resgatar", "compraritem", "buyitem"])
    async def comprar_item_cmd(self, ctx, item_ref: str = None, quantidade: int = 1):
        await self._buy_shop_item(ctx, item_ref, quantidade)

    @cassino_group.command(name="historico", aliases=["histórico"])
    async def historico_cmd(self, ctx, limite: int = 10):
        limite = max(1, min(15, int(limite or 10)))
        conn, cursor = self._connect()
        cursor.execute(
            """
            SELECT game, bet, payout, result, details, created_at
            FROM casino_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (str(ctx.author.id), limite),
        )
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return await ctx.send("Nenhuma aposta registrada. A casa ainda não teve a honra de decepcionar você.")
        lines = [
            f"<t:{created}:R> `{game}` {result} | aposta {fmt(bet)} | pagou {fmt(payout)}\n{str(details or '')[:90]}"
            for game, bet, payout, result, details, created in rows
        ]
        embed = self._basic_embed("Histórico do Cassino", "\n\n".join(lines))
        await ctx.send(embed=embed)

    @cassino_group.command(name="ranking", aliases=["rank"])
    async def ranking_cmd(self, ctx, categoria: str = "fichas"):
        categoria = normalize_id(categoria)
        queries = {
            "fichas": ("Mais fichas", "SELECT user_id, chips FROM casino_players ORDER BY chips DESC LIMIT 10", "fichas"),
            "maior_vitoria": ("Maior vitória", "SELECT user_id, biggest_win FROM casino_players ORDER BY biggest_win DESC LIMIT 10", "fichas"),
            "apostado": ("Mais apostado", "SELECT user_id, total_bet FROM casino_players ORDER BY total_bet DESC LIMIT 10", "fichas"),
            "perdido": ("Mais perdido", "SELECT user_id, total_lost FROM casino_players ORDER BY total_lost DESC LIMIT 10", "fichas"),
            "vitorias": (
                "Mais vitórias",
                """
                SELECT cp.user_id, COALESCE(ps.value, 0)
                FROM casino_players cp
                LEFT JOIN player_stats ps ON ps.user_id = cp.user_id AND ps.stat = 'casino_wins'
                ORDER BY COALESCE(ps.value, 0) DESC
                LIMIT 10
                """,
                "vitórias",
            ),
        }
        if categoria not in queries:
            return await ctx.send("Categorias: `fichas`, `maior_vitoria`, `apostado`, `perdido`, `vitorias`.")
        title, query, unit = queries[categoria]
        conn, cursor = self._connect()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        lines = [f"**{idx}.** <@{user_id}> - **{fmt(value)} {unit}**" for idx, (user_id, value) in enumerate(rows, start=1) if value]
        embed = self._basic_embed(f"Ranking do Cassino - {title}", "\n".join(lines) if lines else "Nada registrado ainda.")
        await ctx.send(embed=embed)

    async def admin_dispatch(self, ctx, action=None, payload=None):
        action = normalize_id(action)
        conn, cursor = self._connect()
        try:
            if action in {"abrir", "open"}:
                cursor.execute("UPDATE casino_config SET active = 1, updated_at = ? WHERE id = 1", (now_ts(),))
                log_admin(cursor, ctx.author.id, "casino_admin_abrir", "Cassino aberto", ctx.author.id)
                conn.commit()
                return await ctx.send(OPEN_LINE)
            if action in {"fechar", "close"}:
                cursor.execute("UPDATE casino_config SET active = 0, updated_at = ? WHERE id = 1", (now_ts(),))
                log_admin(cursor, ctx.author.id, "casino_admin_fechar", "Cassino fechado", ctx.author.id)
                conn.commit()
                return await ctx.send(CLOSED_LINE)
            if action == "jackpot":
                parts = str(payload or "").split()
                if not parts:
                    config = get_config(cursor)
                    return await ctx.send(f"Jackpot atual: **{fmt(config['jackpot'])}** fichas.")
                if parts[0].lower() in {"add", "somar", "adicionar"} and len(parts) >= 2:
                    amount = int(parts[1])
                    add_jackpot(cursor, amount)
                    action_text = f"+{fmt(amount)}"
                else:
                    amount = int(parts[0])
                    cursor.execute("UPDATE casino_config SET jackpot = ?, updated_at = ? WHERE id = 1", (max(0, amount), now_ts()))
                    action_text = f"set {fmt(amount)}"
                log_admin(cursor, ctx.author.id, "casino_admin_jackpot", action_text, ctx.author.id)
                conn.commit()
                return await ctx.send(f"Jackpot atualizado: **{action_text}** fichas.")
            if action in {"dar_fichas", "dar", "give"}:
                parts = str(payload or "").split()
                if len(parts) < 2:
                    return await ctx.send("Uso: `echo adm cassino dar_fichas @user <quantidade>`")
                target_id = re.sub(r"\D", "", parts[0])
                amount = int(parts[1])
                if not target_id or amount <= 0:
                    return await ctx.send("Informe um usuário e uma quantidade positiva de fichas.")
                add_chips(cursor, target_id, amount, reason="admin_dar_fichas", admin_id=ctx.author.id)
                conn.commit()
                return await ctx.send(f"Entreguei **{fmt(amount)}** fichas para <@{target_id}>.")
            if action in {"remover_fichas", "remover", "remove"}:
                parts = str(payload or "").split()
                if len(parts) < 2:
                    return await ctx.send("Uso: `echo adm cassino remover_fichas @user <quantidade>`")
                target_id = re.sub(r"\D", "", parts[0])
                amount = int(parts[1])
                if not target_id or amount <= 0:
                    return await ctx.send("Informe um usuário e uma quantidade positiva de fichas.")
                if not remove_chips(cursor, target_id, amount):
                    return await ctx.send("Esse jogador não tem fichas suficientes.")
                log_admin(cursor, target_id, "casino_admin_remover_fichas", f"-{fmt(amount)} fichas", ctx.author.id)
                conn.commit()
                return await ctx.send(f"Removi **{fmt(amount)}** fichas de <@{target_id}>.")
            return await ctx.send(
                "Comandos: `abrir`, `fechar`, `jackpot [valor|add valor]`, "
                "`dar_fichas @user qtd`, `remover_fichas @user qtd`."
            )
        except ValueError:
            return await ctx.send("Valor inválido. O cassino aceita fichas, não poesia abstrata.")
        finally:
            conn.close()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"Calma. Tente de novo em **{error.retry_after:.1f}s**. TutoriUAU chamou isso de freio moral.")
        raise error


async def setup(bot):
    await bot.add_cog(Casino(bot))
