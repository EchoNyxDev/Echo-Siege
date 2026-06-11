import discord
from discord import app_commands
from discord.ext import commands


THUMB_TUTORI = "https://cdn.discordapp.com/attachments/1493317042760056987/1511161459168514058/TutoriUAU.png"
IMG_AULA_1 = "https://cdn.discordapp.com/attachments/927749834155384853/1511854803574198486/Gemini_Generated_Image_6.jpg"
IMG_AULA_2 = "https://cdn.discordapp.com/attachments/927749834155384853/1511854803267878982/Gemini_Generated_Image_5.jpg"
IMG_AULA_3 = "https://cdn.discordapp.com/attachments/927749834155384853/1511854802936795267/Gemini_Generated_Image_2.jpg"
TUTORIAL_COMMENTS = [
    "Primeira aula: onde eu finjo que isso tudo é simples.",
    "Dinheiro, mochila e perfil. O trio que revela suas prioridades.",
    "Banner é uma palavra bonita para ansiedade estatística.",
    "Combate: agora com menos mistério e mais consequência.",
    "Equipamento e pet: porque até acessório quer planilha.",
    "Guilda é amizade com contrato, banco e opção de deletar tudo. Saudável.",
    "Ranking existe para motivar. E para humilhar com números.",
    "Parabéns, você leu. Isso já te coloca acima de uma parcela preocupante.",
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
                "Essa aula é particular. Eu já trabalho de graça, não vou dar plantão extra aqui.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary, custom_id="tutorial_prev")
    async def btn_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Próxima", style=discord.ButtonStyle.primary, custom_id="tutorial_next")
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
        comentario = TUTORIAL_COMMENTS[page - 1] if page - 1 < len(TUTORIAL_COMMENTS) else "Sim, isso cai na prova chamada 'não passar vergonha'."
        embed.set_footer(text=f"TutoriUAU • Aula {page}/{total} • {comentario}")
        return embed

    def criar_paginas(self, user):
        total = 8
        pages = []

        e1 = self._page(
            "Aula 1 // O que é Echo Siege?",
            (
                f"Senta aí, {user.mention}. Eu sou o **TutoriUAU**, seu NPC tutorial, fiscal de escolhas ruins "
                "e último fio de sanidade entre você e apertar botão sem ler.\n\n"
                "**Echo Siege** é um RPG de Discord: você invoca heróis, monta party, farma recursos, enfrenta "
                "monstros, sobe arena, entra em guilda, participa de eventos e tenta fingir que entende gacha.\n\n"
                "O fluxo básico é: `echo iniciar` -> `echo summon 5` -> `echo main <ID>` -> `echo party` -> começar a apanhar com propósito."
            ),
            1,
            total,
            discord.Color.dark_green(),
            IMG_AULA_1,
        )
        e1.add_field(name="Começo Rápido", value="Use `echo iniciar`, depois `echo summon 5`, depois `echo heróis`.", inline=False)
        e1.add_field(name="Quando se perder", value="Use `echo ajuda`. É o mapa. Você ainda vai ignorar, mas eu tentei.", inline=False)
        pages.append(e1)

        e2 = self._page(
            "Aula 2 // Perfil, Economia e Mochila",
            (
                "`echo perfil` mostra sua ficha. Os temas Cidade Noturna, Minecraft, Árvore Glacial e Flores de Cerejeira cobrem o fundo do card 16:9; avatar, dados e a imagem do herói principal são desenhados por cima.\n"
                "`echo mochila` mostra itens, drops e tickets. É onde ficam as coisas que você jura que vai usar depois.\n"
                "`echo daily` dá recompensa diária expandida; sequência alta rende itens, gems, tickets e até pet.\n"
                "`echo cd` mostra seus tempos de espera.\n\n"
                "`echo atualiza` abre somente os 10 patches mais recentes. Para arqueologia controlada, use `echo atualiza <número>`.\n"
                "`echo codes` mostra os codes disponíveis, recompensas e quais você já resgatou; `echo code <código>` faz o resgate.\n\n"
                "Ouro compra itens, paga sistemas e some misteriosamente quando você vê um banner bonito. "
                "Gems e tickets aparecem em eventos, conquistas e recompensas especiais."
            ),
            2,
            total,
            discord.Color.gold(),
        )
        e2.add_field(name="Venda de Drops", value="Drops de `hunt` podem ser vendidos com `echo vender <item> [quantidade|tudo]`.", inline=False)
        e2.add_field(name="Problemas", value="Se algo sumiu, use `echo bug <texto>`. Exemplo: `echo bug meu ticket desapareceu`.", inline=False)
        pages.append(e2)

        e3 = self._page(
            "Aula 3 // Heróis, Catálogo e Banners",
            (
                "`echo catálogo [classe]` mostra os personagens disponíveis. Útil para descobrir quem falta na sua coleção, "
                "também conhecida como poço sem fundo.\n\n"
                "`echo summon <quantidade>` usa o **banner comum**, com todos os personagens.\n"
                "`echo summon especial <quantidade>` usa o **banner especial semanal**, que muda todo sábado 00:00 e destaca "
                "3 heróis 5 estrelas e 5 heróis 4 estrelas dentro das respectivas raridades.\n"
                "Os dois banners usam a mesma chance de raridade: 4⭐ em 2,5% e 5⭐ em 0,3%. O especial não fabrica raridade; "
                "ele só empurra o sorteio para os destaques depois que a raridade já foi definida.\n"
                "Soft pity começa em 15 giros para 4⭐ e 30 para 5⭐. A etiqueta `[NEW]` aparece na primeira cópia de cada herói.\n"
                "`echo banner` mostra os banners ativos. TutoriUAU: probabilidades pequenas, decisões financeiras enormes."
            ),
            3,
            total,
            discord.Color.orange(),
            IMG_AULA_2,
        )
        e3.add_field(name="Evolução", value="Use `echo evoluir <ID>` para sacrificar uma cópia e aumentar estrelas. Cruel? Sim. Eficiente? Também.", inline=False)
        e3.add_field(name="Habilidades", value="Use `echo herói <ID>` para ver habilidade base e despertares.", inline=False)
        pages.append(e3)

        e4 = self._page(
            "Aula 4 // Party, Afinidade e Combate",
            (
                "`echo main <ID>` define o líder. `echo party` monta os outros slots.\n\n"
                "A **afinidade** é automática: personagens do mesmo anime na mesma party recebem bônus de status. "
                "Dois já ajudam, três começam a incomodar, cinco viram reunião de condomínio interdimensional.\n\n"
                "As habilidades agora são resolvidas pelo motor de combate: base, evolução, cura, buff, debuff, dano em área, "
                "reviver, congelamento, stun, medo, confusão, maldição, fraqueza, queimadura, veneno, sangramento, silêncio e outras graças que me fizeram revisar matemática em horário comercial.\n\n"
                "Quando um herói desbloqueia várias habilidades, ele escolhe entre todas as disponíveis. Cura e reviver olham a situação; o restante alterna para o Levi não esquecer dois terços do próprio currículo.\n"
                "Ao subir de nível, ganha 10 HP, 3 nos atributos restantes e completa 5 no atributo principal. SPD e CRT naturais param em 50%, e DEF nunca apaga todo o dano."
            ),
            4,
            total,
            discord.Color.red(),
        )
        e4.add_field(
            name="Modos",
            value=(
                "`hunt`, `dungeon`, `adventure`, `arena`, `pvp` e invasões usam a party preparada.\n"
                "`echo work` mostra contratos com risco, pagamento e resumo. `echo adventure` executa o contrato com moral, perigo, passos, eventos e escolhas.\n"
                "`echo expedicao 2/4/8/12` abre uma seleção de até 5 heróis para voltar depois com loot.\n"
                "`echo labirinto` abre salas aleatórias com cooldown: monstro, tesouro, mercador, armadilha, evento ou boss.\n"
                "`echo campeoes defesa` registra sua defesa, e `echo campeoes` enfrenta jogadores ou bots com donos identificados no log. A Torre usa Prestígio próprio, não o ELO do PvP."
            ),
            inline=False,
        )
        e4.add_field(
            name="Economia de Combate",
            value=(
                "Ouro e XP agora seguem uma curva de progresso: são menores no início e crescem conforme nível médio da party, "
                "andar, profundidade ou avanço do modo. Dez mil Gold continua possível; só deixou de cair do bolso do primeiro monstro."
            ),
            inline=False,
        )
        e4.add_field(
            name="PvP Online",
            value=(
                "`echo pvp online` entra numa fila global e procura alguém de ELO próximo, priorizando outro servidor. "
                "A batalha inteira, os botões e o log ficam no canal onde cada jogador entrou na fila. Se a dimensão estiver vazia, um bot de força compatível entra.\n"
                "Use `echo pvp online status` ou `echo pvp online sair`. TutoriUAU: finalmente uma luta que não invade sua caixa de mensagens."
            ),
            inline=False,
        )
        e4.add_field(name="Balanceamento", value="Herói nível 1 não deve apagar o universo com uma habilidade 3x. Se apagar, use `echo bug` antes que vire religião.", inline=False)
        pages.append(e4)

        e5 = self._page(
            "Aula 5 // Equipamentos e Pets",
            (
                "Equipamentos não são mais só '+10 ATK e seja feliz'. Agora têm raridade, conjunto, HP, ATK, MATK, DEF, SPD, CRT, "
                "nível e refino.\n\n"
                "`echo equipar <ID herói> <item>` equipa.\n"
                "`echo equipinfo <item>` mostra detalhes.\n"
                "`echo aprimorar <item> [vezes]` aumenta nível.\n"
                "`echo refinar <item>` usa uma cópia solta para melhorar refino.\n\n"
                "Pets vêm do Ticket de Pet na loja: compre, use `echo consumir ticket_pet`, veja com `echo pets` "
                "e equipe com `echo equiparpet <ID>` ou pelo `echo party`. Sim, até pet tem crachá."
            ),
            5,
            total,
            discord.Color.teal(),
        )
        e5.add_field(name="Dica do NPC", value="Refino pede cópia solta. Não adianta gritar comigo. Eu só narro o sofrimento.", inline=False)
        e5.add_field(
            name="Loja de Gems",
            value=(
                "`echo gemshop` abre a loja de Gems. Tem bônus permanentes de XP/Gold, modo automático da arena, "
                "tickets de herói/pet, Ticket de Escolha de Herói, temas de perfil e títulos.\n"
                "Cosméticos viram tokens permanentes na mochila. Use `echo moldura` e `echo titulo` para ativar."
                " Quando ativos, eles deixam o `echo perfil` com estética real. Finalmente moda com função."
            ),
            inline=False,
        )
        pages.append(e5)

        e6 = self._page(
            "Aula 6 // Guildas",
            (
                "Guildas são grupos de jogadores. Você pode criar uma por 5000 Gold com `echo guild criar <nome>`. "
                "Quem cria vira líder, porque foi quem pagou a conta. Capitalismo de fantasia, parabéns.\n\n"
                "Comandos principais: `guild entrar`, `guild convite`, `guild aceitar`, `guild membros`, `guild doar`, "
                "`guild foto`, `guild descrição`, `guild modo`, `guild missão`, `guild raid`, `guild caça` e `guild ranking`."
            ),
            6,
            total,
            discord.Color.dark_gold(),
        )
        e6.add_field(name="Missões de Guilda", value="O líder pode iniciar missões pagas que a guilda completa atacando/progredindo. Recompensas variam por missão.", inline=False)
        e6.add_field(name="Caçada de Guilda", value="Com `echo guild caça` ou `echo guild hunt`, líder/oficial abre uma expedição contra boss usando o banco. Membros atacam e todos ganham se o boss cair.", inline=False)
        e6.add_field(name="Entrada", value="Guilda aberta aceita direto. Guilda por convite exige pedido aceito ou convite do líder.", inline=False)
        e6.add_field(name="Saída e Liderança", value="`echo guild sair`, `echo guild líder @usuário` e `echo guild deletar` pedem confirmação digitando `sair`. Sim, até o caos precisa de recibo.", inline=False)
        pages.append(e6)

        e7 = self._page(
            "Aula 7 // Eventos, Arena, Rankings e Conquistas",
            (
                "`echo eventos` mostra feriados e eventos ativos: Natal, Ano Novo, Páscoa, Dia das Mães, Dia dos Pais, "
                "Dia das Crianças e outros surtos comemorativos.\n\n"
                "`echo evento lutar`, `boss`, `dungeon` e `resgatar` fazem você ganhar pontos, itens temáticos e recompensas.\n\n"
                "`echo arena` é infinita, com dificuldade e recompensa progressivas. `echo rank global` mostra quem está brilhando "
                "e quem claramente dorme pouco. No PvP, todo mundo começa com **0 ELO**; após a primeira luta entra na base **100** e passa a subir ou descer de verdade."
            ),
            7,
            total,
            discord.Color.purple(),
            IMG_AULA_3,
        )
        e7.add_field(
            name="Conquistas",
            value=(
                "Use `echo conquistas`. Agora tem página, botão de resgate e conquistas específicas demais, "
                "incluindo errar comando. TutoriUAU chama isso de QA comunitário involuntário."
            ),
            inline=False,
        )
        pages.append(e7)

        e8 = self._page(
            "Aula 8 // Administração, Bugs e Sobrevivência",
            (
                "Administradores têm comandos como `echo adm stats`, `echo adm logs abertos|resolvidos`, `echo adm resolver <ID> <mensagem>`, `echo adm gems @user quantidade`, `echo adm iniciar raid/boss/calamidade`, "
                "`echo adm iniciar raid/boss/calamidade time-skip`, `echo atualiza_thumb <url>`, `echo adm criarcode`, "
                "`echo adm criarcode temp <dias> <code> <recompensas>`, `echo adm delete code <code>`, `echo adm pay`, "
                "`echo adm tickets` e outros botões nucleares.\n\n"
                "Codes aceitam pacotes como `G1000 T3`: Gold e Tickets no mesmo resgate. Os temporários expiram sozinhos, porque até prêmio grátis precisa respeitar agenda.\n\n"
                "Jogadores podem registrar problemas com `echo bug <texto>` ou `echo queixa <texto>`. Isso salva user_id, ação, valor e data. "
                "Quando o administrador resolver, a resposta fica registrada e o jogador recebe uma mensagem direta. Burocracia, agora com final feliz opcional.\n\n"
                "Pronto. Você agora sabe o suficiente para jogar. Não necessariamente bem, mas isso nunca foi promessa contratual."
            ),
            8,
            total,
            discord.Color.dark_theme(),
        )
        e8.add_field(name="Resumo Final", value="Monte party, use afinidade, equipe itens, entre em guilda, participe de evento e pare de gastar tudo no primeiro banner. Ou gaste. Eu não sou seu contador.", inline=False)
        pages.append(e8)

        return pages

    @commands.command(name="tutorial")
    async def tutorial_prefix(self, ctx):
        embeds = self.criar_paginas(ctx.author)
        view = TutorialPaginator(ctx.author, embeds)
        await ctx.send(embed=embeds[0], view=view)

    @app_commands.command(name="tutorial", description="A aula completa do TutoriUAU sobre o Echo Siege.")
    async def tutorial_slash(self, interaction: discord.Interaction):
        embeds = self.criar_paginas(interaction.user)
        view = TutorialPaginator(interaction.user, embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(Tutorial(bot))
