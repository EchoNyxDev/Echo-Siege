import discord
from discord import app_commands
from discord.ext import commands

# Lista de Administradores (Substitua pelos IDs reais da sua equipe)
ADM_USERS = [
    768671545790693437,
    657990219689099264
]

# ==========================================
# IMAGENS E TEXTOS DA APOSTILA
# ==========================================
THUMB_TUTORI = "https://cdn.discordapp.com/attachments/1493317042760056987/1511161459168514058/TutoriUAU.png"
IMG_AULA_1 = "https://cdn.discordapp.com/attachments/927749834155384853/1511854803574198486/Gemini_Generated_Image_6.jpg"
IMG_AULA_2 = "https://cdn.discordapp.com/attachments/927749834155384853/1511854803267878982/Gemini_Generated_Image_5.jpg"
IMG_AULA_3 = "https://cdn.discordapp.com/attachments/927749834155384853/1511854802936795267/Gemini_Generated_Image_2.jpg"

TUTORIAL_COMMENTS = [
    "Primeira aula: onde eu finjo que isso tudo é simples.",
    "Mochila e Forja: porque reciclar lixo é a alma do RPG.",
    "Gacha e Equipamentos: a matemática te odeia, aceite.",
    "Combate: vá trabalhar, seus bonecos não vão se upar sozinhos.",
    "Guilda: amizade com contrato, banco e cobranças.",
    "Ranking: onde o seu ego vai para ser amassado.",
    "Bugs: reclamar é um direito, eu resolver é outra história.",
    "Setor VIP: Só não aperte o botão vermelho sem ler."
]

class TutorialPaginator(discord.ui.View):
    def __init__(self, user: discord.User, embeds: list):
        super().__init__(timeout=240)
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
                "❌ Essa aula é particular. Eu já trabalho de graça, não vou dar plantão extra aqui. Use `echo tutorial` você mesmo.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, emoji="◀️", custom_id="tutorial_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary, emoji="▶️", custom_id="tutorial_next")
    async def btn_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class Tutorial(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _page(self, title, description, page, total, color=discord.Color.blurple(), image=None):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_thumbnail(url=THUMB_TUTORI)
        if image:
            embed.set_image(url=image)
        comentario = TUTORIAL_COMMENTS[page - 1] if page - 1 < len(TUTORIAL_COMMENTS) else "Sim, isso cai na prova."
        embed.set_footer(text=f"TutoriUAU • Aula {page}/{total} • {comentario}")
        return embed

    def criar_paginas(self, user):
        is_admin = user.id in ADM_USERS
        total = 8 if is_admin else 7
        pages = []

        # ========================================================
        # AULA 1
        # ========================================================
        e1 = self._page(
            "Aula 1 // O que é Echo Siege?",
            (
                f"Senta aí, {user.mention}. Eu sou o **TutoriUAU**, seu NPC tutorial, fiscal de escolhas ruins "
                "e último fio de sanidade entre você e apertar botão sem ler.\n\n"
                "**Echo Siege** é um RPG de Discord: você invoca heróis, monta party, forja itens, "
                "enfrenta monstros colossais e tenta fingir que entende de economia.\n\n"
                "O fluxo básico para não passar vergonha é: `echo iniciar` -> `echo summon 5` -> `echo main <ID>` -> `echo party` -> começar a apanhar com propósito."
            ),
            1, total, discord.Color.dark_green(), IMG_AULA_1
        )
        e1.add_field(name="Começo Rápido", value="Crie a conta, puxe o gacha e organize seu time com `echo party`.", inline=False)
        e1.add_field(name="Quando se perder", value="Use `echo ajuda`. É o resumo rápido de tudo. Você vai ignorar, mas eu tentei.", inline=False)
        pages.append(e1)

        # ========================================================
        # AULA 2
        # ========================================================
        e2 = self._page(
            "Aula 2 // Economia, Mochila e Forja",
            (
                "Sua vida financeira e de itens em Lugnica. Lixo vira luxo se você tiver paciência.\n\n"
                "`echo perfil` - Mostra quem você é, quanto tem e se seus cosméticos estão equipados.\n"
                "`echo mochila` - Seu inventário. Onde os pedaços de monstros e tickets mágicos ficam guardados.\n"
                "`echo forja` - A mágica acontece aqui! Transforme restos de monstros e fragmentos de aventura em **Poções, Armas Lendárias e Tickets de Gacha**.\n"
                "`echo consumir <item>` - Bebe poções, ativa buffs de pergaminhos ou rasga tickets da mochila para usar.\n"
                "`echo vender <item>` - Joga fora o que a forja não aceitou e ganha uns trocados.\n"
                "`echo daily` - Seu salário diário. Pegue todo dia para ganhar tickets bônus.\n"
                "`echo cd` - O seu relógio de ponto. Mostra a estamina e pausas."
            ),
            2, total, discord.Color.gold()
        )
        pages.append(e2)

        # ========================================================
        # AULA 3
        # ========================================================
        e3 = self._page(
            "Aula 3 // Heróis, Gacha e Equipamentos",
            (
                "Onde você torra seu dinheiro em troca de esperança.\n\n"
                "`echo catálogo` - Mostra todos os heróis que existem (e esfrega na sua cara os que você não tem).\n"
                "`echo summon <qtd>` - Roleta no banner comum.\n"
                "`echo summon especial <qtd>` - Roleta nos destaques da semana.\n"
                "*Nota do TutoriUAU: A cada 10 giros vem pelo menos um 3★ ou superior. A matemática te odeia, não reclame comigo.*\n\n"
                "**Fortalecendo seus bonecos:**\n"
                "`echo evoluir <ID>` - Sacrifica uma cópia solta para fortalecer o herói em 1 Estrela (★).\n"
                "`echo herói <ID>` - Ficha de combate completa dele.\n"
                "`echo equipar <ID> <Item>` - Dá armas e relíquias para ele não ir pra rinha pelado.\n"
                "`echo pets` / `echo equiparpet <ID>` - Animais de estimação que dão buffs cabulosos na party."
            ),
            3, total, discord.Color.orange(), IMG_AULA_2
        )
        pages.append(e3)

        # ========================================================
        # AULA 4
        # ========================================================
        e4 = self._page(
            "Aula 4 // Sangue, Suor e Lágrimas",
            (
                "Seus bonecos não vão se upar sozinhos. Bote eles para trabalhar:\n\n"
                "`echo hunt` - Farm rápido. Vai ali, bate no bicho, pega ouro e volta.\n"
                "`echo dungeon` - Progressão clássica por andares.\n"
                "`echo work` - Pegue contratos na Guilda de Aventureiros.\n"
                "`echo adventure` - Execute o contrato. Histórias interativas, moral, risco e escolhas que podem matar a equipe ou te enriquecer.\n"
                "`echo expedicao` - Farm AFK. Mande eles explorarem enquanto você dorme.\n"
                "`echo arena` e `echo labirinto` - Torres de sobrevivência infinitas e RNG.\n\n"
                "**PvP e Duelos:**\n"
                "`echo campeoes` - Duelos contra a defesa dos outros. Use `campeoes defesa` para não passar vergonha.\n"
                "`echo pvp online` - Fila global de pancadaria. Se cair com um bot maluco, reze."
            ),
            4, total, discord.Color.red()
        )
        e4.add_field(name="Afinidade (Sinergia)", value="Coloque heróis do mesmo universo no time! 2/3/4/5 heróis da mesma obra ganham buffs absurdos. Com 5, eles ganham Ressonância.", inline=False)
        e4.add_field(
            name="Cidade, Muralha e Invasões",
            value=(
                "`echo cidade` mostra HP da muralha, moral, prosperidade e suprimentos do servidor.\n"
                "`echo doar <gold>` transforma ouro em suprimentos para obras. Sim, imposto medieval com interface.\n"
                "`echo consertar <suprimentos>` repara a muralha; `echo melhorar` aumenta o HP máximo dela.\n"
                "`echo loja` vende Kit de Reparos; `echo comprar 3 <qtd>` aplica suprimentos direto na cidade.\n"
                "Invasões automáticas usam o canal definido pela staff: Raid todo dia 13:00, Boss sábado 19:00 e Calamidade no último dia do mês 22:00.\n"
                "Quando o aviso aparecer, clique para registrar sua party. TutoriUAU avisa: olhar a muralha cair não conta como participação."
            ),
            inline=False,
        )
        pages.append(e4)

        # ========================================================
        # AULA 5
        # ========================================================
        e5 = self._page(
            "Aula 5 // Guildas (Capitalismo Social)",
            (
                "Apoio em grupo, cobranças em dobro.\n\n"
                "`echo guild criar <nome>` - Custa 5k. Ser líder é caro.\n"
                "`echo guild entrar <nome>` - Para os reles mortais.\n"
                "`echo guild doar` - Encha o cofre da guilda para pagar coisas legais.\n"
                "`echo guild missao` - O líder gasta ouro do banco e todo mundo trabalha junto batendo no alvo para ganhar recompensas massivas.\n"
                "`echo guild raid` ou `guild caça` - Chefões colossais! O grupo inteiro espanca a mesma criatura até ela dropar coisas lendárias.\n"
                "`echo guild foto|desc|modo` - Maquiagem corporativa.\n"
                "`echo guild sair` - Para fugir das obrigações da sua família disfuncional."
            ),
            5, total, discord.Color.dark_gold()
        )
        pages.append(e5)

        # ========================================================
        # AULA 6
        # ========================================================
        e6 = self._page(
            "Aula 6 // Ego e Recompensas",
            (
                "`echo rank local` ou `global` - Para medir ego. Veja quem tem mais ELO no PvP, andares na Torre ou quem roubou mais Ouro.\n\n"
                "`echo eventos` - Quando é feriado, eu solto eventos sazonais. Use `evento lutar` e `evento resgatar` para farmar cosméticos e itens que nunca mais voltam.\n\n"
                "`echo conquistas` - Um tapinha nas costas por jogar demais. Tem botão de resgate que dá Gems e Ouro.\n\n"
                "`echo codes` - Lista os códigos promocionais que o Dev soltou. Se achar um ativo, digite `echo code <código>` e corra para o abraço."
            ),
            6, total, discord.Color.purple(), IMG_AULA_3
        )
        pages.append(e6)

        # ========================================================
        # AULA 7
        # ========================================================
        e7 = self._page(
            "Aula 7 // Bugs e Sobrevivência",
            (
                "Seu herói nível 1 deletou o universo com uma habilidade quebrada? O gacha comeu o seu ouro e não te deu os bonecos? Caiu num buraco negro no meio do labirinto?\n\n"
                "🛡️ **Use `echo bug <descrição detalhada do problema>`** ou `echo queixa <texto>`.\n\n"
                "A denúncia vai direto para a base secreta da staff. Eles podem te responder diretamente na sua DM para resolver a sua vida, ou apenas consertar tudo nas sombras.\n\n"
                "*TutoriUAU avisa:* Se você usar o sistema de bugs para fazer piadinha, eu garanto que a próxima calamidade vai focar no seu perfil com precisão cirúrgica."
            ),
            7, total, discord.Color.teal()
        )
        pages.append(e7)

        # ========================================================
        # AULA 8 (SÓ PARA ADMINS)
        # ========================================================
        if is_admin:
            e8 = self._page(
                "Aula 8 // Área VIP (Administração)",
                (
                    "Ah, você tem a chave do servidor. Tente não explodir nada.\n\n"
                    "**Comandos Nucleares:**\n"
                    "`echo adm stats` - Painel geral do bot.\n"
                    "`echo adm logs abertos` - Verifica as queixas dos plebeus.\n"
                    "`echo adm resolver <ID> <msg>` - Avisa o jogador na DM e fecha o ticket.\n"
                    "`echo adm criarcode <nome> <recompensa>` - Cria promoções (Ex: G1000 T5).\n"
                    "`echo adm set_iniciar` - Define o canal das invasões automáticas.\n"
                    "`echo adm iniciar raid/boss/calamidade [time-skip]` - Começa a confusão no servidor; com time-skip, o registro cai para 1 minuto.\n"
                    "`echo adm hack @user <ID>` - Sobe o herói para nível 100 e 7 Estrelas.\n"
                    "`echo adm delechar @user <nome>` - Apaga clones bugados e limpa defesas quebradas.\n"
                    "`echo adm pay` ou `adm tickets` - Fraudes financeiras legais.\n"
                    "`echo adm hakai @user` - Manda alguém para o além permanentemente.\n\n"
                    "Parabéns. O poder absoluto corrompe absolutamente. Divirta-se."
                ),
                8, total, discord.Color.dark_theme()
            )
            pages.append(e8)

        return pages

    @commands.command(name="tutorial")
    async def tutorial_prefix(self, ctx):
        embeds = self.criar_paginas(ctx.author)
        view = TutorialPaginator(ctx.author, embeds)
        await ctx.send(embed=embeds[0], view=view)

    @app_commands.command(name="tutorial", description="A aula completa (e direta ao ponto) do TutoriUAU.")
    async def tutorial_slash(self, interaction: discord.Interaction):
        embeds = self.criar_paginas(interaction.user)
        view = TutorialPaginator(interaction.user, embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(Tutorial(bot))
