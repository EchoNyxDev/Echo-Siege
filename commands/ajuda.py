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
                "tudo porque aparentemente sou o adulto responsável aqui.\n\n"
                "Coloque `echo ` antes dos comandos de texto. Nos slash commands, reze para o Discord colaborar."
            ),
            1,
            total,
        )
        e1.add_field(
            name="Conta, Perfil e Bolsa",
            value=(
                "`iniciar` - Cria sua conta e pega os presentes iniciais.\n"
                "`perfil` - Mostra sua ficha; temas ativos trocam o fundo e títulos destacam seu nome.\n"
                "`herói <ID>` - Mostra raridade base, evolução, status de combate, equipamentos e habilidades.\n"
                "`heróis` - Lista sua coleção de heróis.\n"
                "`main <ID>` - Define o herói principal.\n"
                "`mochila` - Mostra seus itens, tickets e drops.\n"
                "`pets` - Mostra seus pets atuais.\n"
                "`equiparpet <ID>` - Define o pet que acompanha sua party."
            ),
            inline=False,
        )
        e1.add_field(
            name="Rotina",
            value=(
                "`daily` - Recompensa diária expandida, com sequência, itens, gems, tickets e pet.\n"
                "`cd` - Mostra seus tempos de espera.\n"
                "`atualiza` - Mostra os 10 patches mais recentes.\n"
                "`atualiza <número>` - Abre diretamente um patch antigo ou atual.\n"
                "`codes [página]` - Lista codes, recompensas e seu status de resgate.\n"
                "`tutorial` - A aula grande do TutoriUAU, com menos piedade e mais detalhes.\n"
                "`bug <texto>` / `queixa <texto>` - Registra um problema para a administração."
            ),
            inline=False,
        )
        pages.append(e1)

        e2 = self._base_embed(
            user,
            "TutoriUAU // Heróis, Gacha e Catálogo",
            "A seção onde você troca dinheiro imaginário por esperança. Às vezes funciona. Não espalha.",
            2,
            total,
        )
        e2.add_field(
            name="Invocação",
            value=(
                "`summon <quantidade>` - Invoca no banner comum com todos os personagens.\n"
                "`summon especial <quantidade>` - Invoca no banner especial ativo.\n"
                "`banner` - Mostra o banner comum e o especial.\n"
                "`banner especial` - Mostra os destaques atuais e a origem da seleção.\n"
                "`catálogo [classe]` - Mostra personagens disponíveis por classe.\n"
                "Taxas de raridade são iguais nos dois banners; o especial favorece apenas os personagens em destaque.\n"
                "Seres divinos têm **0,01%** de chance, não entram em destaques e aparecem como `???` no catálogo.\n"
                "Giros de 10 garantem pelo menos um personagem 3⭐ ou superior.\n"
                "A etiqueta `[NEW]` marca a primeira cópia de um herói na sua coleção.\n"
                "Os retratos são carregados do pacote local do bot. TutoriUAU confiscou os links que trocavam o rosto dos personagens."
            ),
            inline=False,
        )
        e2.add_field(
            name="Evolução e Party",
            value=(
                "`evoluir <ID>` - Consome uma cópia livre do mesmo herói e aumenta seu estágio de evolução.\n"
                "`party` - Monta sua equipe de combate.\n"
                "`afinidade` não é comando: 2/3/4/5 heróis da mesma obra ganham 5%/10%/15%/20% nos status principais.\n"
                "Com 5 da mesma obra, o líder também libera a habilidade coletiva **Ressonância da Obra**.\n"
                "`pvp @usuário` - Desafia alguém do servidor para uma luta em turnos.\n"
                "`pvp online` - Fila global; batalha, botões e log ficam inteiros no canal do comando.\n"
                "`pvp online status|sair` - Consulta ou abandona a fila; bots equilibrados preenchem horários vazios."
            ),
            inline=False,
        )
        pages.append(e2)

        e3 = self._base_embed(
            user,
            "TutoriUAU // Combate, Eventos e Rankings",
            "Aqui é onde seus personagens descobrem que a vida não é só pose bonita em banner.",
            3,
            total,
        )
        e3.add_field(
            name="Modos de Jogo",
            value=(
                "`hunt` - Caçada rápida para ouro, XP e drops vendáveis.\n"
                "`dungeon <id> <área>` - Exploração com progressão.\n"
                "`perfil` - Também mostra a Dungeon e a Área atualmente liberadas para você não se perder no mapa imaginário.\n"
                "`adventure` - RPG de contrato com escolhas, moral, perigo, eventos e combate.\n"
                "`arena` - Torre infinita com dificuldade e recompensas progressivas.\n"
                "`arena auto` - Arena automática, se comprou o perk na loja de Gems.\n"
                "`expedicao <2|4|8|12>` - Abre seleção de até 5 heróis para voltar depois com loot.\n"
                "`labirinto` - Sala aleatória com CD: monstro, tesouro, mercador, armadilha, evento ou boss.\n"
                "`labirinto sair` - Sai e salva o loot acumulado.\n"
                "`campeoes` - Torre PvE com Prestígio próprio, separado do ELO do PvP.\n"
                "`campeoes defesa` - Registra sua party defensiva na Torre dos Campeões.\n"
                "`campeoes ranking` - Ranking semanal por pontos e Prestígio da Torre.\n"
                "Status como congelamento, stun, fraqueza, queimadura, veneno e sangramento aparecem durante o combate.\n"
                "`work` - Quadro de contratos com risco, pagamento e seleção diária.\n"
                "Ouro e XP começam modestos e crescem com nível, andar, profundidade ou progresso do modo."
            ),
            inline=False,
        )
        e3.add_field(
            name="Eventos e Ranking",
            value=(
                "`eventos` - Mostra eventos sazonais ativos e próximos.\n"
                "`evento lutar` - Enfrenta monstro temático.\n"
                "`evento boss` - Enfrenta chefe do evento.\n"
                "`evento dungeon` - Faz dungeon temática.\n"
                "`evento resgatar [qtd]` - Troca pontos por recompensa.\n"
                "`rank [global]` - Ranking local ou global com várias categorias."
            ),
            inline=False,
        )
        pages.append(e3)

        e4 = self._base_embed(
            user,
            "TutoriUAU // Loja, Itens e Equipamentos",
            "A parte econômica. Também conhecida como: por que você está pobre mesmo depois da caçada.",
            4,
            total,
        )
        e4.add_field(
            name="Loja e Inventário",
            value=(
                "`cidade` - Mostra Lugnica e sua prosperidade.\n"
                "`loja` - Mostra itens disponíveis.\n"
                "`comprar <ID> <quantidade>` - Compra item.\n"
                "`gemshop` / `gemcomprar <ID>` - Loja de Gems com bônus, temas, títulos e tickets.\n"
                "`moldura` / `titulo` - Ativa temas de fundo ou títulos permanentes no perfil.\n"
                "`ticket_herói` / `escolher_herói <id>` - Usa Ticket de Herói Raro ou Ticket de Escolha.\n"
                "`consumir <item>` - Usa consumível, ticket de pet/herói ou registra token cosmético.\n"
                "`vender <item> [quantidade|tudo]` - Vende drops de caçada.\n"
                "`codes [página]` - Consulta os codes disponíveis e já resgatados.\n"
                "`code <código>` - Resgata códigos. Um uso por jogador, sem malandragem."
            ),
            inline=False,
        )
        e4.add_field(
            name="Equipamentos",
            value=(
                "`equipar <ID herói> <item>` - Equipa arma/armadura.\n"
                "`desequipar <ID herói> <atk/def/livre>` - Remove equipamento.\n"
                "`equips <ID herói>` - Mostra equipamentos do herói.\n"
                "`equipinfo <item>` - Mostra bônus, nível e refino.\n"
                "`aprimorar <item> [vezes]` - Sobe o nível do equipamento.\n"
                "`refinar <item>` - Refina usando uma cópia solta."
            ),
            inline=False,
        )
        pages.append(e4)

        e5 = self._base_embed(
            user,
            "TutoriUAU // Guildas, Conquistas e ADM",
            "Sistema social. Porque aparentemente sofrer sozinho não era suficiente.",
            5,
            total,
        )
        e5.add_field(
            name="Guildas",
            value=(
                "`guild` - Mostra sua guilda.\n"
                "`guild criar <nome>` - Cria guilda por 5000 Gold.\n"
                "`guild entrar <id|nome>` - Entra ou pede entrada.\n"
                "`guild convite @usuário` - Líder envia convite.\n"
                "`guild aceitar @usuário|id` - Aceita pedido ou convite.\n"
                "`guild foto <url>` / `guild descrição <texto>` / `guild modo aberto|convite` - Configuração.\n"
                "`guild doar <quantia>` - Doa ouro.\n"
                "`guild sair` - Sai da guilda com confirmação digitando `sair`.\n"
                "`guild líder @usuário` - Transfere liderança com confirmação.\n"
                "`guild deletar` - Líder deleta a guilda com confirmação.\n"
                "`guild missão` / `guild missão iniciar <id>` / `guild missão atacar` - Missões.\n"
                "`guild raid` - Batalha contra chefe da guilda.\n"
                "`guild caça` / `guild hunt` - Caçada de Guilda liderada contra boss.\n"
                "`guild ranking` - Ranking de guildas."
            ),
            inline=False,
        )
        e5.add_field(
            name="Conquistas e Administração",
            value=(
                "`conquistas` - Mostra metas concluídas e pendentes, com botão de resgate.\n"
                "`conquistas resgatar` - Recebe recompensas disponíveis.\n"
                "`adm stats` - Painel administrativo do jogo.\n"
                "`adm gems @usuário <quantia>` - Dá Gems para um jogador.\n"
                "`adm criarcode <code> <recompensas>` - Cria code permanente, inclusive com vários prêmios.\n"
                "`adm criarcode temp <dias> <code> <recompensas>` - Cria code com vencimento.\n"
                "`adm delete code <code>` - Invalida um code imediatamente.\n"
                "`adm criar banner` - Abre o editor interativo de destaques por sete dias.\n"
                "`adm delechar @usuário <nome>` - Apaga uma cópia do personagem e limpa vínculos quebrados.\n"
                "`atualiza_thumb <url>` - Troca a imagem do mural de atualizações.\n"
                "`adm logs [@usuário|abertos|resolvidos]` - Filtra registros de bugs/queixas.\n"
                "`adm resolver <ID> <mensagem>` - Resolve e envia a resposta ao jogador por DM.\n"
                "`adm reabrir <ID>` - Reabre uma solicitação resolvida.\n"
                "`adm log @usuário <ação> | <valor>` - Cria registro manual."
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

    @app_commands.command(name="help", description="Mostra a lista de comandos do Echo Siege.")
    async def help_slash(self, interaction: discord.Interaction):
        embeds = self.criar_paginas_ajuda(interaction.user)
        view = AjudaPaginator(interaction.user, embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(Ajuda(bot))
