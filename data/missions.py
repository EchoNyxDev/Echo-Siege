# ==========================================
# DICIONÁRIO DE MISSÕES (ECHO WORK / ADVENTURE)
# ==========================================
# Raridades: Comum (60%), Rara (25%), Épica (10%), Lendária (5%)

MISSIONS = {
    # ---------------- COMUNS ----------------
    "m1": {
        "nome": "Escolta do Mercador Pão-Duro", "raridade": "Comum",
        "desc": "Um mercador precisa de escolta até a cidade vizinha, mas não quer pagar muito.",
        "recompensa": {"gold": 150, "xp": 50},
        "evento": {
            "texto": "A carroça chega a uma encruzilhada no bosque escuro. O que a party faz?",
            "opcoes": {
                "A": {"label": "Pelo atalho escuro", "sucesso": False, "texto": "Era uma emboscada! Vocês apanham, e o mercador foge sem pagar.", "loot_mult": 0},
                "B": {"label": "Pela estrada principal", "sucesso": True, "texto": "Viagem longa, mas segura. O mercador pagou o combinado.", "loot_mult": 1.0},
                "C": {"label": "Pelo rio raso", "sucesso": True, "texto": "A carroça atolou, mas acharam moedas no fundo do rio!", "loot_mult": 1.5}
            }
        }
    },
    "m2": {
        "nome": "Limpar o Porão da Taverna", "raridade": "Comum",
        "desc": "O taverneiro ouviu barulhos de ratos gigantes no porão.",
        "recompensa": {"gold": 100, "xp": 60},
        "evento": {
            "texto": "O porão está escuro e cheira a queijo velho. Vocês ouvem um chiado alto.",
            "opcoes": {
                "A": {"label": "Atacar o escuro", "sucesso": False, "texto": "Vocês destruíram os barris de vinho do taverneiro. Ele não pagou nada.", "loot_mult": 0},
                "B": {"label": "Jogar queijo", "sucesso": True, "texto": "Os ratos foram pro queijo e vocês os abateram facilmente.", "loot_mult": 1.0},
                "C": {"label": "Incendiar o porão", "sucesso": True, "texto": "Matou os ratos! A taverna quase queimou, mas o taverneiro pagou pelo susto.", "loot_mult": 0.8}
            }
        }
    },
    "m3": {
        "nome": "Colheita de Ervas Curativas", "raridade": "Comum",
        "desc": "O boticário precisa de Folhas de Prata da Colina dos Goblins.",
        "recompensa": {"gold": 120, "xp": 70},
        "evento": {
            "texto": "Encontraram a planta, mas um Goblin está dormindo em cima dela.",
            "opcoes": {
                "A": {"label": "Esgueirar e roubar", "sucesso": True, "texto": "Um roubo limpo! Entregaram as ervas intactas.", "loot_mult": 1.0},
                "B": {"label": "Acordar o Goblin", "sucesso": False, "texto": "Ele chamou o bando. Vocês fugiram sem as plantas.", "loot_mult": 0},
                "C": {"label": "Matar o Goblin", "sucesso": True, "texto": "Fácil. Ainda saquearam os bolsos do monstro dorminhoco.", "loot_mult": 1.3}
            }
        }
    },
    "m4": {
        "nome": "Gato Desaparecido", "raridade": "Comum",
        "desc": "A velhinha da praça perdeu seu gato 'Lorde Fofuxo'.",
        "recompensa": {"gold": 80, "xp": 40},
        "evento": {
            "texto": "Vocês acharam o gato no alto de um telhado, ele parece bravo.",
            "opcoes": {
                "A": {"label": "Subir no telhado", "sucesso": False, "texto": "O telhado quebrou, vocês caíram. O gato fugiu rindo.", "loot_mult": 0},
                "B": {"label": "Oferecer peixe", "sucesso": True, "texto": "O Lorde Fofuxo desceu pacificamente. A velhinha agradeceu.", "loot_mult": 1.0},
                "C": {"label": "Usar magia", "sucesso": True, "texto": "Vocês levitaram o gato. Ele vomitou, mas a missão foi cumprida.", "loot_mult": 0.9}
            }
        }
    },
    "m5": {
        "nome": "O Carteiro Atrasado", "raridade": "Comum",
        "desc": "Entregue uma carta urgente para o posto de guarda na fronteira.",
        "recompensa": {"gold": 130, "xp": 55},
        "evento": {
            "texto": "Uma ponte no caminho está quebrada. Como atravessar?",
            "opcoes": {
                "A": {"label": "Pular o vão", "sucesso": False, "texto": "Vocês caíram no rio e a carta dissolveu na água.", "loot_mult": 0},
                "B": {"label": "Dar a volta", "sucesso": True, "texto": "Atrasou um pouco, mas a entrega foi feita.", "loot_mult": 0.8},
                "C": {"label": "Consertar a ponte", "sucesso": True, "texto": "Perderam tempo, mas os moradores pagaram um extra pelo conserto!", "loot_mult": 1.4}
            }
        }
    },
    "m6": {
        "nome": "Espantalho Assombrado", "raridade": "Comum",
        "desc": "Um fazendeiro jura que seu espantalho ganha vida à noite.",
        "recompensa": {"gold": 160, "xp": 60},
        "evento": {
            "texto": "Meia-noite. O espantalho começa a se mexer no campo de milho.",
            "opcoes": {
                "A": {"label": "Atacar com Fogo", "sucesso": True, "texto": "O espantalho queimou! Era só um Poltergeist. A plantação sofreu um pouco.", "loot_mult": 0.8},
                "B": {"label": "Fugir de medo", "sucesso": False, "texto": "Vocês correram. O fazendeiro riu da cara de vocês.", "loot_mult": 0},
                "C": {"label": "Investigar de perto", "sucesso": True, "texto": "Eram apenas goblins usando o espantalho como disfarce! Vocês roubaram o loot deles.", "loot_mult": 1.5}
            }
        }
    },
    "m7": {
        "nome": "Ajudar na Forja", "raridade": "Comum",
        "desc": "O ferreiro precisa de ajuda para bombear o fole o dia todo.",
        "recompensa": {"gold": 100, "xp": 80},
        "evento": {
            "texto": "O trabalho é exaustivo. O ferreiro pede para aumentarem o ritmo.",
            "opcoes": {
                "A": {"label": "Bombear com tudo", "sucesso": True, "texto": "A espada ficou perfeita! Ele pagou com gosto.", "loot_mult": 1.2},
                "B": {"label": "Usar magia de vento", "sucesso": False, "texto": "Vocês sopraram as cinzas na cara dele. Foram expulsos.", "loot_mult": 0},
                "C": {"label": "Manter ritmo estável", "sucesso": True, "texto": "Trabalho honesto e pagamento justo.", "loot_mult": 1.0}
            }
        }
    },
    "m8": {
        "nome": "Patrulha Noturna", "raridade": "Comum",
        "desc": "Ajudar os guardas a patrulhar os muros da cidade.",
        "recompensa": {"gold": 140, "xp": 65},
        "evento": {
            "texto": "Vocês veem uma figura suspeita pulando o muro.",
            "opcoes": {
                "A": {"label": "Atirar uma flecha", "sucesso": False, "texto": "Era o filho do prefeito fugindo de casa! Problemas legais.", "loot_mult": 0},
                "B": {"label": "Gritar e prender", "sucesso": True, "texto": "Era um ladrão de galinhas. O guarda pagou a recompensa.", "loot_mult": 1.0},
                "C": {"label": "Seguir a figura", "sucesso": True, "texto": "Vocês acharam o esconderijo do ladrão e dividiram o loot dele com a guarda!", "loot_mult": 1.6}
            }
        }
    },
    "m9": {
        "nome": "O Buraco na Parede", "raridade": "Comum",
        "desc": "Tapar um buraco estranho que apareceu no orfanato.",
        "recompensa": {"gold": 90, "xp": 50},
        "evento": {
            "texto": "Ao olhar pelo buraco, vocês veem olhos brilhantes olhando de volta.",
            "opcoes": {
                "A": {"label": "Tapar rapidamente", "sucesso": True, "texto": "Trabalho rápido e sem perguntas. Tudo seguro.", "loot_mult": 1.0},
                "B": {"label": "Cutucar o olho", "sucesso": False, "texto": "Uma garra puxou a mão do herói. Fugiram para o hospital.", "loot_mult": 0},
                "C": {"label": "Quebrar a parede", "sucesso": True, "texto": "Era um ninho de slimes de ouro! Vocês mataram todos e lucraram.", "loot_mult": 1.8}
            }
        }
    },
    "m10": {
        "nome": "O Concurso de Bebidas", "raridade": "Comum",
        "desc": "Substituir um anão num concurso de bebidas na taverna.",
        "recompensa": {"gold": 200, "xp": 30},
        "evento": {
            "texto": "É a final. O adversário pede a bebida 'Fogo de Dragão'.",
            "opcoes": {
                "A": {"label": "Beber de uma vez", "sucesso": False, "texto": "Desmaiaram no primeiro gole. Vergonha total.", "loot_mult": 0},
                "B": {"label": "Trapacear", "sucesso": True, "texto": "Jogaram fora enquanto ele não olhava. Vitória suja, mas pagou.", "loot_mult": 1.0},
                "C": {"label": "Beber com técnica", "sucesso": True, "texto": "Agarraram-se à mesa e venceram. A taverna inteira aplaudiu!", "loot_mult": 1.2}
            }
        }
    },

    # ---------------- RARAS ----------------
    "m11": {
        "nome": "Caça ao Goblin Dourado", "raridade": "Rara",
        "desc": "Um Goblin feito de ouro puro foi visto nas colinas.",
        "recompensa": {"gold": 400, "xp": 150},
        "evento": {
            "texto": "O Goblin Dourado aparece! Ele é muito rápido e corre para uma caverna.",
            "opcoes": {
                "A": {"label": "Correr atrás", "sucesso": False, "texto": "Tropecaram em uma armadilha. Ele escapou.", "loot_mult": 0},
                "B": {"label": "Cercar a caverna", "sucesso": True, "texto": "Esperaram ele sair e pegaram-no de surpresa!", "loot_mult": 1.0},
                "C": {"label": "Atirar na perna", "sucesso": True, "texto": "Um tiro perfeito. Além da recompensa, arrancaram uma orelha de ouro!", "loot_mult": 1.5}
            }
        }
    },
    "m12": {
        "nome": "Resgate na Cripta", "raridade": "Rara",
        "desc": "Um aristocrata perdeu seu anel na Cripta dos Esquecidos.",
        "recompensa": {"gold": 350, "xp": 200},
        "evento": {
            "texto": "Vocês acham o anel, mas ele está no dedo de um Zumbi furioso.",
            "opcoes": {
                "A": {"label": "Cortar o dedo", "sucesso": True, "texto": "Cirúrgico. Pegaram o anel sem iniciar uma luta longa.", "loot_mult": 1.0},
                "B": {"label": "Lutar de frente", "sucesso": False, "texto": "O zumbi engoliu o anel e fugiu. Falha.", "loot_mult": 0},
                "C": {"label": "Usar fogo sagrado", "sucesso": True, "texto": "Zumbi virou pó. O anel ficou intacto e a cripta está segura.", "loot_mult": 1.2}
            }
        }
    },
    "m13": {
        "nome": "A Caravana de Cristal", "raridade": "Rara",
        "desc": "Proteja um carregamento de cristais de mana instáveis.",
        "recompensa": {"gold": 500, "xp": 180},
        "evento": {
            "texto": "A carroça passa por buracos e os cristais começam a brilhar, prestes a explodir.",
            "opcoes": {
                "A": {"label": "Pular da carroça", "sucesso": False, "texto": "A carroça explodiu. Vocês sobreviveram, mas o pagamento virou pó.", "loot_mult": 0},
                "B": {"label": "Dirigir devagar", "sucesso": True, "texto": "Atrasaram 2 dias, mas a carga chegou intacta.", "loot_mult": 0.8},
                "C": {"label": "Usar magia de gelo", "sucesso": True, "texto": "Congelaram os cristais! Chegaram rápido e ganharam um bônus da guilda magica.", "loot_mult": 1.4}
            }
        }
    },
    "m14": {
        "nome": "Caçadores de Trolls", "raridade": "Rara",
        "desc": "Eliminar um Troll das Cavernas que bloqueou a estrada principal.",
        "recompensa": {"gold": 450, "xp": 250},
        "evento": {
            "texto": "O Troll está dormindo com uma enorme clava na mão.",
            "opcoes": {
                "A": {"label": "Ataque furtivo", "sucesso": True, "texto": "Degolado no sono. Sem honra, mas eficiente.", "loot_mult": 1.0},
                "B": {"label": "Luta justa", "sucesso": False, "texto": "A clava dele acertou todos vocês. Acordaram no hospital.", "loot_mult": 0},
                "C": {"label": "Roubar a clava", "sucesso": True, "texto": "Roubaram a arma! Ele fugiu chorando e vocês venderam a clava.", "loot_mult": 1.5}
            }
        }
    },
    "m15": {
        "nome": "O Poço Envenenado", "raridade": "Rara",
        "desc": "A vila está doente. Descubram a causa no fundo do poço.",
        "recompensa": {"gold": 300, "xp": 300},
        "evento": {
            "texto": "No fundo, há um ninho de sapos venenosos.",
            "opcoes": {
                "A": {"label": "Jogar bomba", "sucesso": False, "texto": "O poço desabou. A vila agora não tem água e não quer pagar.", "loot_mult": 0},
                "B": {"label": "Lutar no poço", "sucesso": True, "texto": "Apanharam um pouco pro veneno, mas limparam a água.", "loot_mult": 1.0},
                "C": {"label": "Extrair o veneno", "sucesso": True, "texto": "Mataram os sapos e guardaram o veneno raro pra vender!", "loot_mult": 1.6}
            }
        }
    },
    "m16": {
        "nome": "Banquete do Nobre", "raridade": "Rara",
        "desc": "O Duque precisa de segurança durante seu banquete cheio de rivais.",
        "recompensa": {"gold": 600, "xp": 100},
        "evento": {
            "texto": "Vocês percebem que a bebida do Duque está borbulhando roxo.",
            "opcoes": {
                "A": {"label": "Gritar 'VENENO!'", "sucesso": True, "texto": "Causou pânico, mas o Duque viveu e pagou bem.", "loot_mult": 1.0},
                "B": {"label": "Trocar as taças", "sucesso": True, "texto": "O assassino bebeu o próprio veneno. Trabalho elegante. Pagamento triplo!", "loot_mult": 2.0},
                "C": {"label": "Deixar beber", "sucesso": False, "texto": "O Duque morreu. Vocês foram demitidos e investigados.", "loot_mult": 0}
            }
        }
    },
    "m17": {
        "nome": "O Livro Maldito", "raridade": "Rara",
        "desc": "Recuperar um livro que suga a alma de quem o lê.",
        "recompensa": {"gold": 400, "xp": 220},
        "evento": {
            "texto": "O livro está aberto no chão. Ele sussurra promessas de poder para a party.",
            "opcoes": {
                "A": {"label": "Ler só uma página", "sucesso": False, "texto": "O mago da party enlouqueceu. Tiveram que fugir para buscar ajuda.", "loot_mult": 0},
                "B": {"label": "Pegar de olhos fechados", "sucesso": True, "texto": "Feito às cegas, mas seguro. O cliente pagou o prometido.", "loot_mult": 1.0},
                "C": {"label": "Enrolar em chumbo", "sucesso": True, "texto": "Bloquearam a magia. O Bibliotecário ficou tão impressionado que deu um bônus.", "loot_mult": 1.3}
            }
        }
    },

    # ---------------- ÉPICAS ----------------
    "m18": {
        "nome": "O Despertar do Golem", "raridade": "Épica",
        "desc": "Um Golem Ancestral despertou e caminha em direção à capital.",
        "recompensa": {"gold": 1200, "xp": 500},
        "evento": {
            "texto": "A criatura tem 10 metros de altura. Suas pernas são puro granito.",
            "opcoes": {
                "A": {"label": "Atacar a cabeça", "sucesso": False, "texto": "Não conseguiram escalar. O Golem os pisoteou.", "loot_mult": 0},
                "B": {"label": "Destruir a junta da perna", "sucesso": True, "texto": "Ele caiu no chão e o exército terminou o serviço. Pagamento recebido.", "loot_mult": 1.0},
                "C": {"label": "Remover o núcleo", "sucesso": True, "texto": "Pularam no peito e arrancaram a gema mestre! Vendido por uma fortuna!", "loot_mult": 1.5}
            }
        }
    },
    "m19": {
        "nome": "O Ritual de Sangue", "raridade": "Épica",
        "desc": "Vampiros Nobres estão realizando um ritual na Fortaleza Demoníaca.",
        "recompensa": {"gold": 1500, "xp": 600},
        "evento": {
            "texto": "O ritual já começou. Um portal negro está se abrindo.",
            "opcoes": {
                "A": {"label": "Atacar os magos", "sucesso": True, "texto": "Portal fechado a tempo, mas quase morreram no processo.", "loot_mult": 1.0},
                "B": {"label": "Entrar no portal", "sucesso": False, "texto": "Foram parar no Abismo e tiveram que gastar o dinheiro para voltar.", "loot_mult": 0},
                "C": {"label": "Sabotar os símbolos", "sucesso": True, "texto": "A magia se voltou contra eles. O salão virou pó e vocês pegaram o loot intacto!", "loot_mult": 1.8}
            }
        }
    },
    "m20": {
        "nome": "Roubo no Castelo Flutuante", "raridade": "Épica",
        "desc": "Invadir as ruínas de um castelo voador e pegar o Ovo de Grifo.",
        "recompensa": {"gold": 1800, "xp": 450},
        "evento": {
            "texto": "A mãe Grifo chega bem na hora que pegam o ovo.",
            "opcoes": {
                "A": {"label": "Lutar com a Mãe", "sucesso": False, "texto": "Ela quase arrancou a cabeça do seu Líder. Fuga sem o ovo.", "loot_mult": 0},
                "B": {"label": "Fugir de asa-delta", "sucesso": True, "texto": "Fuga de cinema! A aterrissagem doeu, mas o ovo está a salvo.", "loot_mult": 1.0},
                "C": {"label": "Domar a Mãe", "sucesso": True, "texto": "Incrível! Além do ovo, o nobre pagou uma fortuna pelas penas que ela deixou cair.", "loot_mult": 1.6}
            }
        }
    },
    "m21": {
        "nome": "A Rebelião dos Mortos", "raridade": "Épica",
        "desc": "Uma cidade inteira virou zumbi em uma noite.",
        "recompensa": {"gold": 1400, "xp": 700},
        "evento": {
            "texto": "A horda de zumbis encurralou vocês na torre do sino.",
            "opcoes": {
                "A": {"label": "Pular pela janela", "sucesso": False, "texto": "Caíram em cima de zumbis. O resgate da guilda saiu caro.", "loot_mult": 0},
                "B": {"label": "Tocar o sino", "sucesso": True, "texto": "O som alto os desorientou. Deu tempo da cavalaria chegar.", "loot_mult": 1.0},
                "C": {"label": "Chuva de flechas de fogo", "sucesso": True, "texto": "Vocês limparam a praça sozinhos. Receberam o pagamento de heróis da cidade!", "loot_mult": 1.4}
            }
        }
    },
    "m22": {
        "nome": "O Leilão do Submundo", "raridade": "Épica",
        "desc": "Infiltre-se no mercado negro e recupere o Cajado do Arquimago.",
        "recompensa": {"gold": 2000, "xp": 400},
        "evento": {
            "texto": "O Cajado está no palco sendo leiloado. A segurança é pesada.",
            "opcoes": {
                "A": {"label": "Dar o maior lance", "sucesso": True, "texto": "Funcionou, mas gastaram quase toda a recompensa no lance.", "loot_mult": 0.5},
                "B": {"label": "Atacar de frente", "sucesso": False, "texto": "100 mercenários atiraram. A party inteira foi capturada.", "loot_mult": 0},
                "C": {"label": "Apagar as luzes", "sucesso": True, "texto": "No escuro, vocês roubaram o cajado e o cofre do leilão!", "loot_mult": 2.0}
            }
        }
    },
    "m23": {
        "nome": "O Labirinto Invisível", "raridade": "Épica",
        "desc": "Encontrar a saída do labirinto amaldiçoado do rei louco.",
        "recompensa": {"gold": 1300, "xp": 800},
        "evento": {
            "texto": "As paredes mudam de lugar. Vocês acham um baú e um botão vermelho.",
            "opcoes": {
                "A": {"label": "Apertar o botão", "sucesso": True, "texto": "O chão abriu e caíram na saída. Sobreviveram.", "loot_mult": 1.0},
                "B": {"label": "Abrir o baú", "sucesso": False, "texto": "Era um mímico! Engoliu o líder. Missão falhou.", "loot_mult": 0},
                "C": {"label": "Quebrar as paredes", "sucesso": True, "texto": "Na força bruta, destruíram o labirinto e acharam a sala do tesouro real!", "loot_mult": 1.5}
            }
        }
    },

    # ---------------- LENDÁRIAS ----------------
    "m24": {
        "nome": "O Retorno do Dragão do Caos", "raridade": "Lendária",
        "desc": "Uma Sombra do Dragão pousou no vulcão adormecido.",
        "recompensa": {"gold": 5000, "xp": 2000},
        "evento": {
            "texto": "O Dragão prepara um sopro que vai destruir toda a região.",
            "opcoes": {
                "A": {"label": "Fugir para as montanhas", "sucesso": False, "texto": "Covardes. A região queimou e vocês perderam prestígio.", "loot_mult": 0},
                "B": {"label": "Erguer escudos", "sucesso": True, "texto": "Suportaram o sopro por um milagre e a guilda finalizou a fera.", "loot_mult": 1.0},
                "C": {"label": "Refletir com magia", "sucesso": True, "texto": "Um ato heroico! O dragão engoliu o próprio fogo. Lendas foram escritas sobre vocês!", "loot_mult": 2.5}
            }
        }
    },
    "m25": {
        "nome": "A Coroa do Deus Caído", "raridade": "Lendária",
        "desc": "Recuperar a relíquia protegida pelo próprio Lucifero.",
        "recompensa": {"gold": 8000, "xp": 2500},
        "evento": {
            "texto": "Lucifero levanta a Espada Demoníaca e corta a dimensão em duas.",
            "opcoes": {
                "A": {"label": "Pular na fenda", "sucesso": False, "texto": "Ficaram presos no vazio por semanas.", "loot_mult": 0},
                "B": {"label": "Esquivar e roubar", "sucesso": True, "texto": "O Líder roubou a coroa e recuou. Trabalho fenomenal.", "loot_mult": 1.0},
                "C": {"label": "Aparar a espada", "sucesso": True, "texto": "INSANO! Defenderam o golpe de um Deus, roubaram a coroa e a espada dele rachou!", "loot_mult": 3.0}
            }
        }
    },
    "m26": {
        "nome": "A Invasão ao Submundo", "raridade": "Lendária",
        "desc": "Descer até os portões do inferno para fechar uma fissura.",
        "recompensa": {"gold": 6000, "xp": 1800},
        "evento": {
            "texto": "Cerberus e 10.000 demônios bloqueiam o portão final.",
            "opcoes": {
                "A": {"label": "Luta frontal", "sucesso": False, "texto": "Vocês não são um exército. Foram esmagados.", "loot_mult": 0},
                "B": {"label": "Colapsar o teto", "sucesso": True, "texto": "A caverna desabou sobre os demônios. Fissura fechada.", "loot_mult": 1.0},
                "C": {"label": "Desafiar Cerberus", "sucesso": True, "texto": "Domaram o cão gigante e o usaram para pisotear os demônios! Glória absoluta!", "loot_mult": 2.2}
            }
        }
    },
    "m27": {
        "nome": "O Eclipse de Sangue", "raridade": "Lendária",
        "desc": "Impedir que Licht realize o ritual de apagar o Sol.",
        "recompensa": {"gold": 7500, "xp": 2200},
        "evento": {
            "texto": "O Rei Feiticeiro suspende o orbe escuro no ar. O eclipse está quase completo.",
            "opcoes": {
                "A": {"label": "Atacar Licht", "sucesso": False, "texto": "Barreira perfeita. O feitiço de ricochete obliterou a party.", "loot_mult": 0},
                "B": {"label": "Destruir o Orbe", "sucesso": True, "texto": "O orbe quebrou, o sol voltou e Licht fugiu. Lugnica está salva.", "loot_mult": 1.0},
                "C": {"label": "Absorver o Orbe", "sucesso": True, "texto": "Loucura total! O Líder absorveu a energia, destruiu a barreira e ainda ficou com poderes sombrios residuais!", "loot_mult": 2.8}
            }
        }
    }
}