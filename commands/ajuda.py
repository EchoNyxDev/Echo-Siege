import discord
from discord import app_commands
from discord.ext import commands


THUMB_TUTORI = "https://cdn.discordapp.com/attachments/1493317042760056987/1511161459168514058/TutoriUAU.png"
HELP_COMMENTS = [
    "Comece pelo básico. Eu imploro com a serenidade de quem já viu `echo sumon`.",
    "Gacha é esperança com recibo. Leia antes de gastar tudo, ou não. Eu só narro.",
    "Combate tem muito botão, mas pelo menos agora eles têm propósito.",
    "Economia do jogo: você ganha, gasta, reclama e repete. Sistema realista.",
    "Guilda é família escolhida, com banco, chefe e pequenas crises administrativas.",
]


def _split_field_value(value, limit=1024):
    value = str(value or "")
    if len(value) <= limit:
        return [value or "\u200b"]

    chunks = []
    current = ""
    for line in value.splitlines(keepends=True):
        while len(line) > limit:
            if current:
                chunks.append(current.rstrip())
                current = ""
            split_at = line.rfind(" ", 0, limit + 1)
            if split_at <= 0:
                split_at = limit
            chunks.append(line[:split_at].rstrip())
            line = line[split_at:].lstrip()

        if len(current) + len(line) > limit:
            chunks.append(current.rstrip())
            current = line
        else:
            current += line

    if current:
        chunks.append(current.rstrip())
    return [chunk or "\u200b" for chunk in chunks]


def _normalize_embed_fields(embed):
    original_fields = [
        (field.name, field.value, field.inline)
        for field in embed.fields
    ]
    embed.clear_fields()

    for name, value, inline in original_fields:
        chunks = _split_field_value(value)
        for index, chunk in enumerate(chunks):
            field_name = name if index == 0 else f"{name} (continuação {index + 1})"
            embed.add_field(
                name=field_name[:256],
                value=chunk,
                inline=inline,
            )
    return embed


class AjudaPaginator(discord.ui.View):
    def __init__(self, user: discord.User, embeds: list):
        super().__init__(timeout=180)
        self.user = user
        self.embeds = embeds
        self.page = 0
        self.update_buttons()

    def update_buttons(self):
        self.btn_prev.disabled = self.page == 0
        self.btn_next.disabled = self.page >= len(self.embeds) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "Ei. Essa apostila foi aberta por outra pessoa. Abre a sua com `echo ajuda`, jovem curioso.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, custom_id="help_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary, custom_id="help_next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class Ajuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    def _base_embed(self, user, titulo, descricao, pagina, total):
        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=discord.Color.brand_green(),
        )
        embed.set_thumbnail(url=THUMB_TUTORI)
        comentario = HELP_COMMENTS[pagina - 1] if pagina - 1 < len(HELP_COMMENTS) else "Use `echo tutorial` se quiser a aula completa. Coragem."
        embed.set_footer(text=f"TutoriUAU • Página {pagina}/{total} • {comentario}")
        return embed

    def criar_paginas_ajuda(self, user):
        total = 5
        pages = []

        e1 = self._base_embed(
            user,
            "TutoriUAU // Comandos Básicos",
            (
                f"Olá, {user.mention}. Respira. O bot tem coisa pra caramba, mas eu organizei "
                "tudo num resumo porque aparentemente sou o adulto responsável aqui.\n\n"
                "Prefixo padrão: `echo `. Exemplo: `echo perfil`."
            ),
            1,
            total,
        )
        e1.add_field(
            name="Conta, Perfil e Bolsa",
            value=(
                "`iniciar` - Cria sua conta e pega os presentes.\n"
                "`perfil` - Mostra sua ficha de jogador e progresso.\n"
                "Nível da conta dá bônus passivo de Gold/XP a cada 10 níveis, com teto saudável. Sim, agora serve para algo.\n"
                "`herói <ID|nome>` - Mostra detalhes do seu herói pelo ID ou a ficha base pelo nome.\n"
                "`anime <obra>` - Lista personagens de uma obra específica, tipo `echo anime Re:Zero`.\n"
                "`heróis` - Lista toda a sua coleção.\n"
                "`main <ID>` - Define o líder da Party.\n"
                "`mochila` - Mostra itens, tickets e drops guardados.\n"
                "`pets` - Lista seus pets.\n"
                "`equiparpet <ID>` - Equipa um companheiro na party."
            ),
            inline=False,
        )
        e1.add_field(
            name="Rotina e Sistema",
            value=(
                "`daily` - Recompensa diária (mantém a ofensiva para bônus).\n"
                "`cd` - Painel de tempos de espera dos modos de jogo.\n"
                "`atualiza [número]` - Lê as notas de atualização (patches).\n"
                "`codes [página]` - Consulta códigos e status de resgate.\n"
                "`tutorial` - A aula detalhada do TutoriUAU para iniciantes.\n"
                "`bug <texto>` / `queixa <texto>` - Manda ticket para a staff."
            ),
            inline=False,
        )
        pages.append(e1)

        e2 = self._base_embed(
            user,
            "TutoriUAU // Heróis, Gacha e Catálogo",
            "A seção onde você troca dinheiro imaginário por esperança. Às vezes funciona.",
            2,
            total,
        )
        e2.add_field(
            name="Invocação e Consulta",
            value=(
                "`summon <quantidade>` - Roda a roleta no banner comum.\n"
                "`summon especial <quantidade>` - Gacha no banner de destaques.\n"
                "`banner` / `banner especial` - Vê as taxas e os destaques atuais.\n"
                "`catálogo [classe]` - Lista todos os personagens que existem (ou os que te faltam).\n"
                "`anime <obra>` - Filtra o elenco por origem. TutoriUAU chama isso de Ctrl+F com autoestima."
            ),
            inline=False,
        )
        e2.add_field(
            name="Evolução e Party",
            value=(
                "`evoluir <ID>` - Gasta uma cópia solta para dar +1 Estrela ao herói.\n"
                "`party` - Menu interativo para arrumar seu esquadrão de 5 membros.\n"
                "`pvp @usuário` - Desafia alguém do seu servidor para combate.\n"
                "`pvp online` - Entra na fila de duelo global contra qualquer um.\n"
                "`pvp online status|sair` - Verifica a fila ou desiste da procura."
            ),
            inline=False,
        )
        pages.append(e2)

        e3 = self._base_embed(
            user,
            "TutoriUAU // Combate, Eventos e Rankings",
            "Aqui é onde seus personagens descobrem que a vida dói.",
            3,
            total,
        )
        e3.add_field(
            name="Modos de Jogo",
            value=(
                "`hunt` - Bate num monstro aleatório. Dá XP e Ouro. Rápido e prático.\n"
                "`dungeon <id> <área>` - Explora a masmorra escolhida.\n"
                "`adventure` - RPG imersivo com narrativa, escolhas e consequências.\n"
                "`arena` / `arena auto` - Torre de sobrevivência sem fim.\n"
                "`expedicao <2|4|8|12>` - Manda heróis AFK voltarem com loot.\n"
                "`labirinto` / `labirinto sair` - Desce nas salas RNG infinitas.\n"
                "`campeoes` / `campeoes defesa` / `campeoes ranking` - Duelos PvE Assíncronos.\n"
                "`work` - Pega os contratos diários na guilda."
            ),
            inline=False,
        )
        e3.add_field(
            name="Eventos e Ranking",
            value=(
                "`eventos` - Lista os eventos sazonais rolando no momento.\n"
                "`evento lutar|boss|dungeon|resgatar` - Interage com as atividades da season.\n"
                "`copa` - Painel da Echo Cup / Copa do Mundo de Wolford.\n"
                "`copa iniciar|time|jogar` - Cria o time, consulta a escalação e joga partidas.\n"
                "`copa loja|resgatar|ranking|hall` - Troca echobet e acompanha a classificação.\n"
                "`copa banner|summon|heroi|historico` - Banner esportivo, fichas da Copa e últimas partidas. O summon usa ticket antes de cobrar ouro.\n"
                "Invasões automáticas usam o canal do `adm set_iniciar`: raid 13:00, boss sábado 19:00 e calamidade no último dia do mês 22:00.\n"
                "`rank` / `rank global` - Mostra a nata dos jogadores e quem tem mais dinheiro/poder."
            ),
            inline=False,
        )
        pages.append(e3)

        e4 = self._base_embed(
            user,
            "TutoriUAU // Loja, Forja e Equipamentos",
            "O pilar econômico de Wolford. Fique forte ou fique pobre tentando.",
            4,
            total,
        )
        e4.add_field(
            name="Economia e Itens",
            value=(
                "`cidade` - Vê se a capital de Wolford está inteira ou em chamas.\n"
                "`loja` / `comprar <ID> <qtd>` - Gasta Ouro no comércio local.\n"
                "`gemshop` / `gemcomprar <ID>` - A loja VIP (comprada com Gemas).\n"
                "`forja` - Onde você transforma o lixo dos monstros em armas, consumíveis e tickets mágicos.\n"
                "`consumir <item>` - Bebe poções, rasga pergaminhos ou aciona tickets da sua mochila.\n"
                "`vender <item> [qtd|tudo]` - Livra-se do peso extra e ganha um troco.\n"
                "`doar <gold>` / `consertar <suprimentos>` / `melhorar` - Abastece, repara e evolui a muralha da cidade.\n"
                "`code <código>` - Usa códigos promocionais secretos.\n"
                "`moldura <nome>` / `titulo <nome>` - Veste seus cosméticos adquiridos."
            ),
            inline=False,
        )
        e4.add_field(
            name="Gestão de Armamentos",
            value=(
                "`equipar <ID herói> <item>` - Veste seu personagem.\n"
                "`desequipar <ID herói> <atk/def/livre>` - Tira o equipamento.\n"
                "`equips <ID herói>` - Vê a build atual do personagem.\n"
                "`equipinfo <item>` - Olha as stats de uma arma.\n"
                "`aprimorar <item>` / `refinar <item>` - Sistemas de evolução de armas."
            ),
            inline=False,
        )
        pages.append(e4)

        e5 = self._base_embed(
            user,
            "TutoriUAU // Guildas e Administração",
            "Sistema social. Porque aparentemente sofrer sozinho não era suficiente.",
            5,
            total,
        )
        e5.add_field(
            name="A Guilda",
            value=(
                "`guild` - Status geral da sua Guilda.\n"
                "`guild criar|entrar|sair|deletar` - O básico da administração civil.\n"
                "`guild convite|aceitar|pedidos` - Setor de RH.\n"
                "`guild foto|descrição|modo` - Maquiagem institucional.\n"
                "`guild doar` - Joga dinheiro no banco coletivo.\n"
                "`guild líder @usuário` - Transfere a responsabilidade.\n"
                "`guild missão` / `guild missão iniciar <id>` / `atacar` - Trabalho coletivo.\n"
                "`guild raid` / `guild caça` - Chefões gigantescos pro grupo bater junto.\n"
                "`guild ranking` - Medidor de ego entre facções."
            ),
            inline=False,
        )
        e5.add_field(
            name="Extras",
            value=(
                "`conquistas` / `conquistas resgatar` - Um tapinha nas costas por jogar muito.\n"
                "`adm ...` - Comandos restritos para o dono do bot. (Poder absoluto, etc)."
            ),
            inline=False,
        )
        pages.append(e5)

        for embed in pages:
            _normalize_embed_fields(embed)
        return pages

    @commands.command(name="help", aliases=["ajuda", "comandos"])
    async def help_prefix(self, ctx):
        embeds = self.criar_paginas_ajuda(ctx.author)
        view = AjudaPaginator(ctx.author, embeds)
        await ctx.send(embed=embeds[0], view=view)

    @app_commands.command(name="help", description="Mostra a lista de comandos resumida do Echo Siege.")
    async def help_slash(self, interaction: discord.Interaction):
        embeds = self.criar_paginas_ajuda(interaction.user)
        view = AjudaPaginator(interaction.user, embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(Ajuda(bot))
