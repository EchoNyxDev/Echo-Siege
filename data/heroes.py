import re
import unicodedata


HEROES = {


"levi_ackerman": {

    "nome": "Levi Ackerman",

    "origem": "Attack on Titan",

    "emoji": "👊",
    "imagem": "",

    "classe": "Atacante",
    "raridade": 1,
    "max_star": 7,

    "hp": 70,
    "atk": 35,
    "matk": 0,
    "def": 12,
    "spd": 30,
    "crt": 25,

    "habilidade": {
        "nome": "Ataque Giratório",
        "descricao": "Ataca duas vezes o mesmo alvo"
    },

     "evolucoes": {

            3: {
                "nome": "Ataque Descomunal",
                "descricao": "Aumenta em 10 o ATK"
               },

           5: {
                "nome": "Berserk",
                "descricao": "Aumenta em 30 o ATK e 20 SPD, caso o HP zere continua lutando em campo de batalha sem sofrer dano por 3 turnos"
            }

        },

},
# =========================2


"rock_lee": {

    "nome": "Rock Lee",

    "origem": "Naruto",

    "emoji": "👊",
    "imagem": "",

    "classe": "Atacante",
    "raridade": 2,
    "max_star": 7,

    "hp": 70,
    "atk": 40,
    "matk": 0,
    "def": 15,
    "spd": 35,
    "crt": 10,

    "habilidade": {
        "nome": "Furacão da Folha",
        "descricao": "Desfere um golpe poderoso causando ATK+15"
    },

    "evolucoes": {

            3: {
                "nome": "Lótus Oculta",
                "descricao": "Causa um golpe poderoso causando ATK+30"
            },

            5: {
                "nome": "8 Portões",
                "descricao": "Aumenta em 30 a SPD e ATK, dura 2 turnos e fica stunnado após isso"
            }

        },

},
# =========================3


"roronoa_zoro": {

    "nome": "Roronoa Zoro",

    "origem": "One Piece",

    "emoji": "👊",
    "imagem": "",

    "classe": "Atacante",
    "raridade": 3,
    "max_star": 7,

    "hp": 90,
    "atk": 40,
    "matk": 0,
    "def": 15,
    "spd": 30,
    "crt": 20,

    "habilidade": {
        "nome": "Santoryuu",
        "descricao": "Ataca 3 vezes o mesmo alvo"
    },

    "evolucoes": {

            5: {
                "nome": "Ashura",
                "descricao": "Ataca 9 vezes um alvo"
            }

        },

},
# =========================4


"jotaro_joestar": {

    "nome": "Jotaro Joestar",

    "origem": "JoJo",

    "emoji": "👊",
    "imagem": "",

    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,

    "hp": 100,
    "atk": 45,
    "matk": 0,
    "def": 20,
    "spd": 15,
    "crt": 15,

    "habilidade": {
        "nome": "Star Platinum",
        "descricao": "Possui 25% de chance de atacar novamente"
    },

    "evolucoes": {

            5: {
                "nome": "O Mundo",
                "descricao": "Para o tempo, anulando qualquer habilidade causada contra si 1 vez"
            }

        },

},
# =========================5


"kirito": {

    "nome": "Kirito",

    "origem": "Sword art Online",

    "emoji": "👊",
    "imagem": "",

    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,

    "hp": 100,
    "atk": 60,
    "matk": 20,
    "def": 20,
    "spd": 50,
    "crt": 35,

    "habilidade": {
        "nome": "Dual Blade",
        "descricao": "Dobra o dano de seu ATK"
    },

    "evolucoes": {

            7: {
                "nome": "Privilégios de Administrador",
                "descricao": "Pode cancelar o dano causado por um alvo durante 5 turnos"
            }

        },

},
# =========================6


"mereoleona": {

    "nome": "Mereoleona",

    "origem": "Black Clover",

    "emoji": "👊",
    "imagem": "",

    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,

    "hp": 100,
    "atk": 60,
    "matk": 40,
    "def": 20,
    "spd": 20,
    "crt": 10,

    "habilidade": {
        "nome": "Mana Zone",
        "descricao": "Seus golpes passam a causar +30 de dano de fogo, causa burn passivo referente a 10 MATK por turno"
    },

    "evolucoes": {

            7: {
                "nome": "Encarnação do Fogo do Inferno",
                "descricao": "Ao morrer uma vez, revive com HP total, dobra o ATK e MATK e aplica debuff em todos os inimigos reduzindo a defesa em 20"
            }

        },

},
# =========================7


"natsu": {

    "nome": "Natsu",

    "origem": "Fairy Tail",

    "emoji": "🔥",
    "imagem": "",

    "classe": "Mago",
    "raridade": 1,
    "max_star": 7,

    "hp": 60,
    "atk": 15,
    "matk": 30,
    "def": 10,
    "spd": 15,
    "crt": 0,

    "habilidade": {
        "nome": "Sopro de Fogo",
        "descricao": "Causa dano em área referente a 35 MATK e aplicando burn, inimigos sofrem 10 MATK por turno durante 2 turnos"
    },

    "evolucoes": {

            3: {
                "nome": "Lótus de Lâminas: Chama Explosiva",
                "descricao": "Rajadas de lâminas de fogo, causa dano em área referente a 50 MATK"
            },

            5: {
                "nome": "Dragon Force",
                "descricao": "Entra em seu modo de dragão verdadeiro. Buffa o MATK base em 30 até o fim do combate"
            }

        },


},
# =========================8


"megumin": {

    "nome": "Megumin",

    "origem": "KonoSuba",

    "emoji": "🔥",
    "imagem": "",

    "classe": "Mago",
    "raridade": 2,
    "max_star": 7,

    "hp": 50,
    "atk": 0,
    "matk": 40,
    "def": 12,
    "spd": 10,
    "crt": 30,

    "habilidade": {
        "nome": "Explosion",
        "descricao": "Causa dano massivo, um golpe único causando 50 MATK, não pode mais usar essa habilidade por 3 turnos"
    },

    "evolucoes": {

            3: {
                "nome": "Explosion+",
                "descricao": "Sua habilidade base recebe o buff, acrescentando 10 MATK ao dano e diminuindo 1 turno no CD"
            },

            5: {
                "nome": "Explosion++",
                "descricao": "Sua habilidade base recebe o buff, acrescentando 30 MATK ao dano, golpe único por batalha"
            }

        },


},
# =========================9


"frieren": {

    "nome": "Frieren",

    "origem": "Sousou no Frieren",

    "emoji": "🔥",
    "imagem": "",

    "classe": "Mago",
    "raridade": 3,
    "max_star": 7,

    "hp": 65,
    "atk": 0,
    "matk": 45,
    "def": 15,
    "spd": 10,
    "crt": 35,

    "habilidade": {
        "nome": "Disparo de Mana",
        "descricao": "Dano em área, causando MATK + 20 em todos os inimigos"
    },

    "evolucoes": {

            5: {
                "nome": "Zoltraak",
                "descricao": "Ignore defesa, causando 50 MATK e aumentando em 20 o CRT"
            }

        },


},
# =========================10


"satoru_gojo": {

    "nome": "Satoru Gojo",

    "origem": "Jujutsu Kaisen",

    "emoji": "🔥",
    "imagem": "",

    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,

    "hp": 80,
    "atk": 20,
    "matk": 50,
    "def": 20,
    "spd": 25,
    "crt": 10,

    "habilidade": {
        "nome": "Azul e Vermelho",
        "descricao": "Agrupa todos os inimigos em um único ponto e causa dano massivo, MATK + 40"
    },

    "evolucoes": {

            5: {
                "nome": "Roxo",
                "descricao": "Causa dano massivo em um único inimigo, possui 10% de chance para Insta-kill, 60 + MATK"
            }

        },


},
# =========================11


"ainz_gown": {

    "nome": "Ainz Ooal Gown",

    "origem": "Overlord",

    "emoji": "🔥",
    "imagem": "",

    "classe": "Mago",
    "raridade": 5,
    "max_star": 7,

    "hp": 100,
    "atk": 0,
    "matk": 80,
    "def": 20,
    "spd": 15,
    "crt": 30,

    "habilidade": {
        "nome": "Fallen Down",
        "descricao": "Causa dano massivo em área, aplicando 80 MATK a todos os inimigos"
    },

    "evolucoes": {

            7: {
                "nome": "Grasp Heart",
                "descricao": "Esmaga o coração do alvo, tendo 30% de chace de matar instantaneamente o alvo"
            }

        },


},
# =========================12


"tony_chopper": {

    "nome": "Tony Tony Chopper",

    "origem": "one Piece",

    "emoji": "🩹",
    "imagem": "",

    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,

    "hp": 70,
    "atk": 20,
    "matk": 10,
    "def": 30,
    "spd": 15,
    "crt": 10,

    "habilidade": {
        "nome": "Cura",
        "descricao": "Aplica cura em todos os aliados, curando 30 pontos de HP"
    },

    "evolucoes": {

            3: {
                "nome": "Rumble Ball",
                "descricao": "Entra em um modo mais versátil, aumentando seu dano de ataque e defesa em 20"
            },

            5: {
                "nome": "Cura máxima",
                "descricao": "Cura todos os aliados em 80 pontos"
            }

        },


},
# =========================13


"tsunade": {

    "nome": "Tsunade",

    "origem": "Naruto",

    "emoji": "🩹",
    "imagem": "",

    "classe": "Suporte",
    "raridade": 2,
    "max_star": 7,

    "hp": 100,
    "atk": 20,
    "matk": 20,
    "def": 30,
    "spd": 10,
    "crt": 5,

    "habilidade": {
        "nome": "Técnica da Palma Mística",
        "descricao": "Cura um alvo em 40 pontos"
    },

    "evolucoes": {

            3: {
                "nome": "Kuchiyose",
                "descricao": "Invoca seu pet, causando cura constante em campo de batalha, curando 20 pontos por turno"
            },

            5: {
                "nome": "Criação do Renascimento",
                "descricao": "Reviv um aliado com 50% de HP"
            }

        },


},
# =========================14


"wendy_marvell": {

    "nome": "Wendy Marvell",

    "origem": "Fairy Tail",

    "emoji": "🩹",
    "imagem": "",

    "classe": "Suporte",
    "raridade": 3,
    "max_star": 7,

    "hp": 100,
    "atk": 30,
    "matk": 40,
    "def": 20,
    "spd": 20,
    "crt": 10,

    "habilidade": {
        "nome": "Enchantment",
        "descricao": "Aumenta o dano de um aliado em 20 ATK OU MATK"
    },

    "evolucoes": {

            5: {
                "nome": "High Enchanter",
                "descricao": "Aumenta o dano de todos os aliados em 35 ATK ou MATK, aumenta a DEF do DPS em 20"
            }

        },


},
# =========================15


"elizabeth_liones": {

    "nome": "Elizabeth Liones",

    "origem": "Nanatsu no Taizai",

    "emoji": "🩹",
    "imagem": "",

    "classe": "Suporte",
    "raridade": 4,
    "max_star": 7,

    "hp": 110,
    "atk": 30,
    "matk": 40,
    "def": 20,
    "spd": 10,
    "crt": 5,

    "habilidade": {
        "nome": "Alto Perdão",
        "descricao": "Cura todos os membros da party em 50%"
    },

    "evolucoes": {

            5: {
                "nome": "Reviver",
                "descricao": "Revive o primeiro aliado morto com 100% de HP, 1 vez por combate"
            }

        },


},
# =========================16


"orihime_inoue": {

    "nome": "Orihime Inoue",

    "origem": "Bleach",

    "emoji": "🩹",
    "imagem": "",

    "classe": "Suporte",
    "raridade": 5,
    "max_star": 7,

    "hp": 120,
    "atk": 10,
    "matk": 30,
    "def": 40,
    "spd": 10,
    "crt": 0,

    "habilidade": {
        "nome": "Koten Zanshun",
        "descricao": "Nega completamente o dano causado em um aliado por 2 turnos"
    },

    "evolucoes": {

            7: {
                "nome": "Sōten Kisshun",
                "descricao": "Cria um escudo em três DPS que anula completamente o dano causado por 2 turnos. Aumenta a defesa de todos os aliados em 30"
            }

        },



},
# =========================17


"alphons_elric": {

    "nome": "Alphonse Elric",

    "origem": "Fullmetal Alchimist",

    "emoji": "🛡️",
    "imagem": "",

    "classe": "Tank",
    "raridade": 1,
    "max_star": 7,

    "hp": 100,
    "atk": 20,
    "matk": 15,
    "def": 30,
    "spd": 5,
    "crt": 10,

    "habilidade": {
        "nome": "Alquimia",
        "descricao": "Aumenta a DEF em 20"
    },

    "evolucoes": {

            3: {
                "nome": "Invulnerabilidade Biológica",
                "descricao": "Entra em modo de defesa, aumentando o HP em 20 e a DEF em 25"
            },

            5: {
                "nome": "Transmutação",
                "descricao": "Converte ATK + MATK em DEF + 10"
            }

        },


},
# =========================18


"annie_leonhart": {

    "nome": "Annie Leonhart",

    "origem": "Attack on Titan",

    "emoji": "🛡️",
    "imagem": "",

    "classe": "Tank",
    "raridade": 2,
    "max_star": 7,

    "hp": 120,
    "atk": 25,
    "matk": 0,
    "def": 35,
    "spd": 10,
    "crt": 0,

    "habilidade": {
        "nome": "Cristalização",
        "descricao": "Aumenta a DEF e o HP em 25"
    },

    "evolucoes": {

            3: {
                "nome": "Titã",
                "descricao": "Aumenta todos os atributos em 15"
            },

            5: {
                "nome": "Titã + Cristalização",
                "descricao": "Aumenta todos os atributos em 20, e acrescenta + 30hp"
            }

        },


},
# =========================19


"kaidou": {

    "nome": "Kaidou",

    "origem": "One Piece",

    "emoji": "🛡️",
    "imagem": "",

    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,

    "hp": 120,
    "atk": 30,
    "matk": 0,
    "def": 50,
    "spd": 20,
    "crt": 0,

    "habilidade": {
        "nome": "Bêbado de Oito Trigramas",
        "descricao": "Aumenta DEF em 50, pode continuar lutando por 1 turno caso seu HP zere"
    },

    "evolucoes": {

            5: {
                "nome": "Forma Híbrida",
                "descricao": "Entra em sua forma híbrida com dragão, passa a ignorar dano físico por 5 turnos."
            }

        },


},
# =========================20


"kokushibo": {

    "nome": "Kokushibo",

    "origem": "Kimetsu no Yaiba",

    "emoji": "🛡️",
    "imagem": "",

    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,

    "hp": 110,
    "atk": 40,
    "matk": 25,
    "def": 30,
    "spd": 30,
    "crt": 20,

    "habilidade": {
        "nome": "Regeneração",
        "descricao": "Cura passivamente 20hp por turno, só pode ser morto por dano mágico"
    },

    "evolucoes": {

            5: {
                "nome": "Marca do Caçador",
                "descricao": "Aumenta sua SPD em 30, passa a curar 35 por turno e só pode ser morto por dano mágico massivo"
            }

        },



},
# =========================21


"maple": {

    "nome": "Maple",

    "origem": "Bofuri",

    "emoji": "🛡️",
    "imagem": "",

    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,

    "hp": 150,
    "atk": 10,
    "matk": 10,
    "def": 60,
    "spd": 10,
    "crt": 0,

    "habilidade": {
        "nome": "Absorção",
        "descricao": "Absorve completamente o dano de uma habilidade causada e devolve contra o oponente."
    },

    "evolucoes": {

            5: {
                "nome": "Modo Divino",
                "descricao": "Passa a curar 40 hp por turno. Absorve uma ultimate e devolve dobrado o dano contra o oponente"
            }

        },


},
# =========================22


"erwin_smith": {

    "nome": "Erwin Smith",

    "origem": "Attack on Titan",

    "emoji": "📚",
    "imagem": "",

    "classe": "Líder",
    "raridade": 1,
    "max_star": 7,

    "hp": 65,
    "atk": 10,
    "matk": 0,
    "def": 20,
    "spd": 25,
    "crt": 10,

    "habilidade": {
        "nome": "Inspiração",
        "descricao": "Aumenta a DEF e ATK/MATK de todos os aliados em 10"
    },

    "evolucoes": {

            3: {
                "nome": "Discurso Motivacional",
                "descricao": "Buff geral, aumenta em 20 todos os atributos de um único aliado"
            },

            5: {
                "nome": "Sacrifício",
                "descricao": "Quando o DPS estiver perto da morte, Erwin se sacrifica em seu lugar, fazendo com que o HP dele seja transferido ao DPS"
            }

        },


},
# =========================23


"shiroe": {

    "nome": "Shiroe",

    "origem": "Log Horizon",

    "emoji": "📚",
    "imagem": "",

    "classe": "Líder",
    "raridade": 2,
    "max_star": 7,

    "hp": 60,
    "atk": 20,
    "matk": 20,
    "def": 20,
    "spd": 10,
    "crt": 10,

    "habilidade": {
        "nome": "Estrategista",
        "descricao": "Administra o campo de batalha, inimigos passam a errar com mais frequência ataques e aumenta as chances de ataques dos aliados"
    },

    "evolucoes": {

            3: {
                "nome": "Escriba",
                "descricao": "Aumenta a evasão da equipe, fazendo com que todos passem a ignorar ataques básicos por 2 turnos"
            },

            5: {
                "nome": "Full Control Encounter",
                "descricao": "Passa a prever as ações dos oponentes, diminuindo o SPD inimigo geral em 20, e fazendo com que aliados não possam serem acertados por 3 turnos"
            }

        },


},
# =========================24


"lelouch": {

    "nome": "Lelouch Lamperouge",

    "origem": "Code Geass",

    "emoji": "📚",
    "imagem": "",

    "classe": "Líder",
    "raridade": 3,
    "max_star": 7,

    "hp": 70,
    "atk": 15,
    "matk": 0,
    "def": 30,
    "spd": 20,
    "crt": 10,

    "habilidade": {
        "nome": "Geass",
        "descricao": "Pode dar uma ordem absoluta a um aliado, fazendo com que ele reviva caso esteja caído, ou pode dar uma ordem a um inimigo com chance de 10% de Insta-kill"
    },

    "evolucoes": {

            5: {
                "nome": "Geass+",
                "descricao": "Revive até dois aliados, enquanto Lelouch estiver vivo, estes não podem tomar dano."
            }

        },


},
# =========================25


"sousuke_aizen": {

    "nome": "Sousuke Aizen",

    "origem": "Bleach",

    "emoji": "📚",
    "imagem": "",

    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,

    "hp": 80,
    "atk": 35,
    "matk": 20,
    "def": 10,
    "spd": 40,
    "crt": 10,

    "habilidade": {
        "nome": "Kyoka Suigetsu",
        "descricao": "Cria uma ilusão do DPS em campo de batalha, como se houvessem 2, a cópia possui os mesmos atributos, porém sua vida é setada em 30"
    },

    "evolucoes": {

            5: {
                "nome": "Hipnose completa",
                "descricao": "Cria uma réplica perfeita do DPS, com todos os seus atributos. A cópia não pode tomar dano, porém será morta caso o DPS caia também"
            }

        },



},
# =========================26


"rimuru_tempest": {

    "nome": "Rimuru Tempest",

    "origem": "Tensei Shitara Slime Datta Ken",

    "emoji": "📚",
    "imagem": "",

    "classe": "Líder",
    "raridade": 5,
    "max_star": 7,

    "hp": 100,
    "atk": 40,
    "matk": 40,
    "def": 30,
    "spd": 35,
    "crt": 20,

    "habilidade": {
        "nome": "Belzebu",
        "descricao": "Absorve ATK inimigo em converte em HP aliado"
    },

    "evolucoes": {

            7: {
                "nome": "Ciel",
                "descricao": "Evolução Adaptativa, concede buff ou debuff do que mais estiver precisando no momento. Caso os aliados estejam com vida baixa, cura todos em 50%. Caso os inimigos esteja com vida abaixo de 20, causa um dano massivo em área finalizando o combate. Caso os inimigos estejam com muita vida, aumenta a DEF e ATK de todos os aliados em 30"
            }

        },



},
# =========================27


"death_kid": {

    "nome": "Death the Kid",

    "origem": "Soul Eater",

    "emoji": "🏹",
    "imagem": "",

    "classe": "Atirador",
    "raridade": 1,
    "max_star": 7,

    "hp": 65,
    "atk": 35,
    "matk": 10,
    "def": 10,
    "spd": 20,
    "crt": 30,

    "habilidade": {
        "nome": "Linhas de Sanzu",
        "descricao": "Buffa a chance de dano crítico em 20%"
    },

    "evolucoes": {

            3: {
                "nome": "Disparo Sincronizado",
                "descricao": "Atinge dois inimigos que tenham causado mais dano no turno, causando ATK + 30"
            },

            5: {
                "nome": "Loucura da Ordem",
                "descricao": "Buff no ATK de +20, Buff na SPD de +10 e garante um ataque crítico"
            }

        },


},
# =========================28


"sinon": {

    "nome": "Sinon",

    "origem": "Sword art Online",

    "emoji": "🏹",
    "imagem": "",

    "classe": "Atirador",
    "raridade": 2,
    "max_star": 7,

    "hp": 70,
    "atk": 40,
    "matk": 0,
    "def": 10,
    "spd": 30,
    "crt": 30,

    "habilidade": {
        "nome": "Sniper",
        "descricao": "Atinge o inimigo que tenha causado maior dano no turno, causando ATK + 40"
    },

    "evolucoes": {

            3: {
                "nome": "Xeque-Mate",
                "descricao": "Causa dano massivo em um único inimigo, crítico garantido"
            },

            5: {
                "nome": "Hell Snipe",
                "descricao": "Abate uma tropa inimiga aleatória."
            }

        },


},
# =========================29


"mine": {

    "nome": "Mine",

    "origem": "Akame ga Kill",

    "emoji": "🏹",
    "imagem": "",

    "classe": "Atirador",
    "raridade": 3,
    "max_star": 7,

    "hp": 75,
    "atk": 40,
    "matk": 20,
    "def": 10,
    "spd": 35,
    "crt": 35,

    "habilidade": {
        "nome": "Pumpkin",
        "descricao": "Causa dano massivo em área, afetando todos os inimigos causando ATK + 30, dobra o dano em tropas aéreas"
    },

    "evolucoes": {

            5: {
                "nome": "Ultimate Pumpkin",
                "descricao": "Causa dano massivo a um único inimigo, ATK × 3"
            }

        },


},
# =========================30


"uryu_ishida": {

    "nome": "Uryu Ishida",

    "origem": "Bleach",

    "emoji": "🏹",
    "imagem": "",

    "classe": "Atirador",
    "raridade": 4,
    "max_star": 7,

    "hp": 75,
    "atk": 45,
    "matk": 30,
    "def": 10,
    "spd": 30,
    "crt": 40,

    "habilidade": {
        "nome": "Heilig Bogen",
        "descricao": "Utilizando seu arco espiritual causa dano verdadeiro, ignora DEF inimiga"
    },

    "evolucoes": {

            5: {
                "nome": "Antítese",
                "descricao": "Trava o alvo em dois inimigos até o fim do combate, ignora DEF e ignora Regeneração"
            }

        },



},
# =========================31


"vash": {

    "nome": "Vash",

    "origem": "Trigun",

    "emoji": "🏹",
    "imagem": "",

    "classe": "Atirador",
    "raridade": 5,
    "max_star": 7,

    "hp": 90,
    "atk": 50,
    "matk": 30,
    "def": 15,
    "spd": 30,
    "crt": 50,

    "habilidade": {
        "nome": "Angel Wings",
        "descricao": "seus tiros causam dano massivo em área, causando ATK × 3 a todos os inimigos"
    },

    "evolucoes": {

            7: {
                "nome": "Manipulação Gravitacional e Dimensional",
                "descricao": "50% de chance de Insta-kill em um único inimigo uma vez por combate"
            }

        },


},
# =========================32


"yuno_gasai": {

    "nome": "Yuno Gasai",

    "origem": "Mirai Nikki",

    "emoji": "⚔️",
    "imagem": "",

    "classe": "Assassino",
    "raridade": 1,
    "max_star": 7,

    "hp": 90,
    "atk": 35,
    "matk": 0,
    "def": 20,
    "spd": 35,
    "crt": 20,

    "habilidade": {
        "nome": "Yandere",
        "descricao": "Caso o DPS do time seja ferido, passa a focar completamente em quem o feriu, aumentando seu dano em 20 contra o alvo"
    },

    "evolucoes": {

            3: {
                "nome": "Intenção Assassina",
                "descricao": "Diminui a SPD de um inimigo, fazendo com que ele não possa atacar por 1 turno"
            },

            5: {
                "nome": "Querido Diário",
                "descricao": "Marca o DPS aliado, qualquer dano que ele tomar é revertido contra si mesma, também transfere seu ATK total para o ATK dele"
            }

        },



},
# =========================33


"yor_forger": {

    "nome": "Yor Forger",

    "origem": "Spy X Family",

    "emoji": "⚔️",
    "imagem": "",

    "classe": "Assassino",
    "raridade": 2,
    "max_star": 7,

    "hp": 95,
    "atk": 40,
    "matk": 0,
    "def": 40,
    "spd": 35,
    "crt": 20,

    "habilidade": {
        "nome": "Assassinato",
        "descricao": "Foca a tropa mais fraca inimiga, aumentando o CRT em 20"
    },

    "evolucoes": {

            3: {
                "nome": "Assassinato +",
                "descricao": "Habilidade recebe buff, onde a tropa inimiga mais fraca passa a sofrer +30 ATK"
            },

            5: {
                "nome": "Death Strike",
                "descricao": "Um único golpe no inimigo com menor DEF, reduz 50 do HP total"
            }

        },

},
# =========================34


"stain": {

    "nome": "Stain",

    "origem": "Boku no Hero",

    "emoji": "⚔️",
    "imagem": "",

    "classe": "Assassino",
    "raridade": 3,
    "max_star": 7,

    "hp": 90,
    "atk": 40,
    "matk": 20,
    "def": 20,
    "spd": 35,
    "crt": 30,

    "habilidade": {
        "nome": "Coagulação",
        "descricao": "Afeta um inimigo aleatório, no qual impede que ele ataque ou se defenda por 3 turnos"
    },

    "evolucoes": {


            5: {
                "nome": "Coagulação+",
                "descricao": "Afeta o DPS inimigo, impedindo ele de se defender ou atacar por 3 turnos"
            }

        },


},
# =========================35


"zabuza_momochi": {

    "nome": "Zabuza Momochi",

    "origem": "Naruto",

    "emoji": "⚔️",
    "imagem": "",

    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,

    "hp": 100,
    "atk": 30,
    "matk": 30,
    "def": 15,
    "spd": 25,
    "crt": 25,

    "habilidade": {
        "nome": "Técnica da Prisão de Água",
        "descricao": "Envolve um único aleatório em uma prisão. Inimigo alvo entra em um x1 contra Zabuza, não podendo fugir ou atacar outros oponentes, o mesmo se aplica a Zabuza, até que um dos dois morra"
},

    "evolucoes": {


            5: {
                "nome": "Clone de Água",
                "descricao": "Cria um clone perfeito de água de si mesmo, possui todos os seus atributos, porém possui metade de seu HP"
            }

        },


},
# =========================36


"akame": {

    "nome": "Akame",

    "origem": "Akame ga Kill",

    "emoji": "⚔️",
    "imagem": "",

    "classe": "Assassino",
    "raridade": 5,
    "max_star": 7,

    "hp": 100,
    "atk": 60,
    "matk": 10,
    "def": 20,
    "spd": 40,
    "crt": 40,

    "habilidade": {
        "nome": "Muramasa",
        "descricao": "Sua espada possui chance de 10% de um Insta-kill a todo golpe causado a 1 inimigo"
    },

    "evolucoes": {


            7: {
                "nome": "Lâmina Carmesim",
                "descricao": "Ao banhar a Muramasa com seu próprio sangue, garante um Insta-kill caso acerte 1 inimigo (não podendo afetar boss, mini-boss ou calamidade), em contrapartida cai em batalha após 3 turnos"
            }

        },


},
# =========================37


"killua": {

    "nome": "Killua Zoldyck",

    "origem": "Hunter X Hunter",

    "emoji": "⚔️",
    "imagem": "",

    "classe": "Assassino",
    "raridade": 5,
    "max_star": 7,

    "hp": 100,
    "atk": 50,
    "matk": 25,
    "def": 10,
    "spd": 40,
    "crt": 40,

    "habilidade": {
        "nome": "Eletro-Wave",
        "descricao": "Golpe massivo eletro a 1 inimigo, debilita o mesmo fazendo com que ele não se mova por 2 turnos e causa ATK + 40"
    },

    "evolucoes": {

            5: {
                "nome": "Godspeed",
                "descricao": "Dobra sua SPD atual"
            }

        },

},

# =========================38
"mob_psycho": {
    "nome": "Mob",
    "origem": "Mob Psycho 100",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 70, "atk": 10, "matk": 55, "def": 15, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Telecinese",
        "descricao": "Aumenta seu poder mágico, + 30 MATK"
    },
    "evolucoes": {
        5: {
            "nome": "100%",
            "descricao": "Libera todo seu poder, aumenta o MATK em 50 até o fim do combate, mesmo se o seu HP zerar, não cai por 3 turnos, continua atacando."
        }
    }
},
# =========================39
"rudo_surebrac": {
    "nome": "Rudo Surebrac",
    "origem": "Gachiakuta",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 4,
    "max_star": 7,
    "hp": 100, "atk": 45, "matk": 20, "def": 30, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Jinki",
        "descricao": "Melhora um item usado contra si, os atributos do item são melhorados em 50%."
    },
    "evolucoes": {
        5: {
            "nome": "Jinki+",
            "descricao": "Melhora um item usado contra si, os atributos do item são melhorados em 100%."
        }
    }
},
# =========================40
"itadori_yuji": {
    "nome": "Itadori Yuji",
    "origem": "Jujutsu Kaisen",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 55, "matk": 30, "def": 25, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Convergência",
        "descricao": "Golpe sanguíneo, possui 25% de chance de paralisar o alvo, causa 40 + MATK."
    },
    "evolucoes": {
        7: {
            "nome": "Desmantelar",
            "descricao": "Causa dano em área, golpe de dano físico, causa cerca de 40 + ATK."
        }
    }
},
# =========================41
"natsuki_subaru": {
    "nome": "Natsuki Subaru",
    "origem": "Re:Zero",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 2,
    "max_star": 7,
    "hp": 100, "atk": 10, "matk": 5, "def": 40, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Retorno Através da Morte",
        "descricao": "Enquanto um aliado estiver vivo, continua sempre revivendo."
    },
    "evolucoes": {
        3: {
            "nome": "Contrato Espiritual",
            "descricao": "Possui um contrato com Beatrice, possuindo seu arsenal de magias. Aumenta a DEF geral em 30, e o ATK e MATK geral em 20."
        },
        5: {
            "nome": "Cor Leonis / Providência Invisível",
            "descricao": "Cor Leonis diminui o dano sofrido em 25% dividindo-o com aliados. Mão Invisível causa 30 + MATK com acerto garantido, ignorando DEF."
        }
    }
},
# =========================42
"makima": {
    "nome": "Makima",
    "origem": "Chainsaw Man",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 5,
    "max_star": 7,
    "hp": 90, "atk": 30, "matk": 50, "def": 30, "spd": 25, "crt": 25,
    "habilidade": {
        "nome": "Contrato",
        "descricao": "Faz um contrato com o DPS do time. Caso o DPS morra, ele também leva consigo um inimigo aleatório."
    },
    "evolucoes": {
        7: {
            "nome": "Demônio do Controle",
            "descricao": "Ao sacrificar o DPS aliado, consegue eliminar o DPS inimigo em um ritual."
        }
    }
},
# =========================43
"maki_zenin": {
    "nome": "Maki Zenin",
    "origem": "Jujutsu Kaisen",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 110, "atk": 45, "matk": 0, "def": 20, "spd": 40, "crt": 30,
    "habilidade": {
        "nome": "Restrição Celestial",
        "descricao": "Em troca de sofrer 10% a mais de dano mágico, aumenta seu ATK em 20, sua SPD em 25 e concede o primeiro ataque como crítico."
    },
    "evolucoes": {
        5: {
            "nome": "Zero Restrição",
            "descricao": "Aumenta todos os atributos físicos e de velocidade em 30."
        }
    }
},
# =========================44
"mirko": {
    "nome": "Mirko",
    "origem": "Boku no Hero Academia",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 120, "atk": 45, "matk": 0, "def": 40, "spd": 30, "crt": 0,
    "habilidade": {
        "nome": "Rabbit",
        "descricao": "Aumenta sua SPD e DEF em 30."
    },
    "evolucoes": {
        5: {
            "nome": "Rabbit+",
            "descricao": "Melhoria da habilidade, passa a ignorar dano físico, podendo ser afetada somente por dano mágico."
        }
    }
},
# =========================45
"emilia": {
    "nome": "Emilia",
    "origem": "Re:Zero",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 65, "atk": 15, "matk": 45, "def": 20, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Magia de Gelo",
        "descricao": "Seus ataques causam 40 + MATK e reduzem a SPD geral dos inimigos em 10."
    },
    "evolucoes": {
        5: {
            "nome": "Contrato Espiritual (Puck)",
            "descricao": "Aumenta seu MATK em 30, e passa a ter chance de 25% de stunnar (congelar) inimigos alvos por 2 turnos."
        }
    }
},
# =========================46
"denji": {
    "nome": "Denji",
    "origem": "Chainsaw Man",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 40, "matk": 10, "def": 20, "spd": 30, "crt": 20,
    "habilidade": {
        "nome": "Chainsaw Man",
        "descricao": "Avança girando as motosserras. Causa 30 + ATK em um inimigo e aplica Sangramento (30% do ATK) por três turnos."
    },
    "evolucoes": {
        5: {
            "nome": "Forma Verdadeira",
            "descricao": "Libera o Homem-Motosserra completo. Ignora 35% de DEF. Cura 40% do dano causado. Causa o dobro do seu ATK + 20 de dano."
        }
    }
},
# =========================47
"asta": {
    "nome": "Asta",
    "origem": "Black Clover",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 100, "atk": 50, "matk": 0, "def": 30, "spd": 20, "crt": 15,
    "habilidade": {
        "nome": "Anti-Magia",
        "descricao": "Remove 2 buffs do alvo. Mais forte contra Magos, anula uma habilidade inimiga de forma passiva."
    },
    "evolucoes": {
        5: {
            "nome": "Forma Demoníaca",
            "descricao": "Ignora completamente escudos. Ganha 30 de SPD e +50 de ATK."
        }
    }
},
# =========================48
"arthur_boyle": {
    "nome": "Arthur Boyle",
    "origem": "Fire Force",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 120, "atk": 60, "matk": 30, "def": 20, "spd": 40, "crt": 25,
    "habilidade": {
        "nome": "Cavaleiro Rei",
        "descricao": "Quanto menor sua vida, maior o dano. Aumenta 2 em ATK a cada 1 de HP perdido."
    },
    "evolucoes": {
        7: {
            "nome": "Excalibur",
            "descricao": "Golpe único massivo, ignora DEF, possui 40% de chance de executar inimigos com HP abaixo de 30% e causa dano massivo (HP máximo + ATK)."
        }
    }
},
# =========================49
"baki_hanma": {
    "nome": "Baki Hanma",
    "origem": "Baki",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 2,
    "max_star": 7,
    "hp": 70, "atk": 30, "matk": 0, "def": 30, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Triceratops Fist",
        "descricao": "Reduz DEF do alvo em 15% e causa 20 + ATK de dano físico."
    },
    "evolucoes": {
        3: {
            "nome": "Whip Strike",
            "descricao": "Acerta duas vezes o alvo com ataques físicos imprevisíveis."
        },
        5: {
            "nome": "Demon Back",
            "descricao": "Ativa por dois turnos, fica imune a controle, ganha +30 no ATK geral e aumenta a DEF em 20."
        }
    }
},
# =========================50
"meliodas": {
    "nome": "Meliodas",
    "origem": "Nanatsu no Taizai",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 2,
    "max_star": 7,
    "hp": 70, "atk": 35, "matk": 25, "def": 10, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Marca Demoníaca",
        "descricao": "Recebe +35% de ATK por 3 turnos."
    },
    "evolucoes": {
        3: {
            "nome": "Assault Mode",
            "descricao": "Rouba 15% do ATK do alvo e desfere um golpe massivo de 40 + ATK."
        },
        5: {
            "nome": "Demon King Form",
            "descricao": "Cura 50% do HP total, recebe +20 em DEF e SPD, e passa a ignorar DEF."
        }
    }
},
# =========================51
"thorfinn": {
    "nome": "Thorfinn",
    "origem": "Vinland Saga",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 1,
    "max_star": 7,
    "hp": 65, "atk": 30, "matk": 0, "def": 20, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Combate Desarmado",
        "descricao": "+15% de esquiva por 2 turnos, recebe um buff passivo de 20% de loot em hunt."
    },
    "evolucoes": {
        3: {
            "nome": "Luta com Adagas",
            "descricao": "Desfere 2 golpes de 120% da força base."
        },
        5: {
            "nome": "Eu Não Tenho Inimigos",
            "descricao": "Remove todos os debuffs dos aliados e recebe redução de dano de 40% por 2 turnos."
        }
    }
},
# =========================52
"escanor": {
    "nome": "Escanor",
    "origem": "Nanatsu no Taizai",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 120, "atk": 50, "matk": 50, "def": 20, "spd": 20, "crt": 20,
    "habilidade": {
        "nome": "Sunshine",
        "descricao": "Ganha +20% de dano por turno, acumula até 5 vezes. Causa um golpe somando ATK e MATK em um único inimigo."
    },
    "evolucoes": {
        7: {
            "nome": "The One Ultimate",
            "descricao": "Imune a morte no turno (retém 1 HP). Ignora DEF e causa (ATK + MATK) x 2. Após o turno, Escanor perde 25% do HP máximo."
        }
    }
},
# =========================53
"guts": {
    "nome": "Guts",
    "origem": "Berserk",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 100, "atk": 50, "matk": 20, "def": 30, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Dragon Slayer",
        "descricao": "Um balanço lateral destrutivo que causa ATK + MATK em até 3 alvos simultâneos."
    },
    "evolucoes": {
        5: {
            "nome": "Armadura Berserker",
            "descricao": "Recebe +100 HP extra temporário, aumenta o ATK em 60%, a SPD em 15 e a DEF em 30, mas perde 5% do HP por turno."
        }
    }
},
# =========================54
"yami_sukehiro": {
    "nome": "Yami Sukehiro",
    "origem": "Black Clover",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 100, "atk": 45, "matk": 35, "def": 25, "spd": 30, "crt": 20,
    "habilidade": {
        "nome": "Magia das Trevas",
        "descricao": "Reduz precisão do alvo em 20%. Causa um corte infundido em sombras (MATK + ATK)."
    },
    "evolucoes": {
        5: {
            "nome": "Corte Dimensional",
            "descricao": "25% chance de Ruptura (+30% dano extra sofrido). Ignora DEF e escudos com acerto garantido (Soma ATK e MATK + 50%)."
        }
    }
},
# =========================55
"kurosaki_ichigo": {
    "nome": "Ichigo Kurosaki",
    "origem": "Bleach",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 75, "matk": 20, "def": 20, "spd": 40, "crt": 30,
    "habilidade": {
        "nome": "Hollow Form",
        "descricao": "Aumenta para 40% a SPD e aumenta em 50% o ATK por 3 turnos."
    },
    "evolucoes": {
        7: {
            "nome": "True Bankai",
            "descricao": "Garante o primeiro ataque crítico. Dobra o status base de ATK e, se matar o alvo, Ichigo ganha um turno extra."
        }
    }
},
# =========================56
"saitama": {
    "nome": "Saitama",
    "origem": "One Punch Man",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 120, "atk": 95, "matk": 0, "def": 40, "spd": 40, "crt": 40,
    "habilidade": {
        "nome": "Golpes Normais Consecutivos",
        "descricao": "Desfere 5 golpes de 100% de força. Cada golpe individual possui +10% de chance de ser crítico."
    },
    "evolucoes": {
        7: {
            "nome": "Soco Sério",
            "descricao": "Ignora DEF, Imortalidade e Invulnerabilidade. Dano garantido de ATK x 5. Se o alvo não morrer, fica atordoado por 2 turnos."
        }
    }
},
# =========================57
"himiko_toga": {
    "nome": "Himiko Toga",
    "origem": "Boku no Hero Academia",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 3,
    "max_star": 7,
    "hp": 60, "atk": 20, "matk": 20, "def": 20, "spd": 20, "crt": 20,
    "habilidade": {
        "nome": "Cópia de Individualidade",
        "descricao": "Copia aleatoriamente uma habilidade inimiga e a utiliza contra ele."
    },
    "evolucoes": {
        5: {
            "nome": "Transformação Completa",
            "descricao": "Copia todos os status de um inimigo aleatório, assim como o seu arsenal de habilidades."
        }
    }
},
# =========================58
"ayano_tateyama": {
    "nome": "Ayano Tateyama",
    "origem": "Mekakucity Actors",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 30, "matk": 30, "def": 20, "spd": 35, "crt": 25,
    "habilidade": {
        "nome": "Olhos que Favorecem",
        "descricao": "Ayano prevê os movimentos inimigos. Aumenta passivamente a SPD em 20% e CRT em 30%."
    },
    "evolucoes": {
        3: {
            "nome": "Projeção de Memórias",
            "descricao": "Invade as memórias do alvo. Ele fica imune a dano no turno, mas o próximo ataque aliado contra ele causa Dano em Dobro."
        },
        5: {
            "nome": "Comunicação Espiritual",
            "descricao": "Invoca um Espírito por 3 turnos que causa dano automático e cura o aliado mais ferido no fim do turno."
        }
    }
},
# =========================59
"revy_atiradora": {
    "nome": "Revy",
    "origem": "Black Lagoon",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 2,
    "max_star": 7,
    "hp": 60, "atk": 35, "matk": 0, "def": 20, "spd": 25, "crt": 25,
    "habilidade": {
        "nome": "Ambidestria",
        "descricao": "2 ataques consecutivos com as Cutlasses, cada tiro causa 120% de dano e possui chance independente de crítico."
    },
    "evolucoes": {
        3: {
            "nome": "Pontaria Incomparável",
            "descricao": "Recebe 40% de CRT, Ignora 25% da DEF e seus tiros não podem mais errar o alvo."
        },
        5: {
            "nome": "Arsenal de Escolha",
            "descricao": "Permite disparar munição perfurante, explosiva ou incendiária dependendo da necessidade tática."
        }
    }
},
# =========================60
"kanao_tsuyuri": {
    "nome": "Kanao Tsuyuri",
    "origem": "Demon Slayer",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 3,
    "max_star": 7,
    "hp": 70, "atk": 40, "matk": 20, "def": 10, "spd": 40, "crt": 30,
    "habilidade": {
        "nome": "Respiração da Flor",
        "descricao": "Se criticar, ganha um turno extra parcial. Recebe +10% de CRT e +20 de ATK, além de aplicar Veneno (20 MATK/3 turnos)."
    },
    "evolucoes": {
        5: {
            "nome": "Olhos Escarlates Equinocial",
            "descricao": "O primeiro ataque crítico garantido ignora 50% da DEF e inflige Veneno pesado (MATK x 2)."
        }
    }
},
# =========================61
"hyakkimaru": {
    "nome": "Hyakkimaru",
    "origem": "Dororo",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 45, "matk": 0, "def": 10, "spd": 40, "crt": 25,
    "habilidade": {
        "nome": "Próteses Mortais",
        "descricao": "Golpeia 3 vezes com as espadas protéticas (25 + MATK). Cada hit tem 25% de chance de aplicar Sangramento (20 dano/3 turnos)."
    },
    "evolucoes": {
        5: {
            "nome": "Modo Berserk",
            "descricao": "Recupera HP sempre que causa dano. Aumenta ATK em 40% e SPD em 20% durante 3 turnos."
        }
    }
},
# =========================62
"toji_fushiguro": {
    "nome": "Toji Fushiguro",
    "origem": "Jujutsu Kaisen",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 110, "atk": 50, "matk": 0, "def": 15, "spd": 35, "crt": 35,
    "habilidade": {
        "nome": "Restrição Celestial (Completa)",
        "descricao": "Imunidade absoluta a debuffs mágicos. Aumenta em 30% a sua SPD e ATK por 3 turnos."
    },
    "evolucoes": {
        5: {
            "nome": "Caçador Imparável",
            "descricao": "Se matar o alvo ganha um novo turno. Ignora 50% da DEF e escudos de mana, além de somar +50 no dano geral."
        }
    }
},
# =========================63
"esdeath": {
    "nome": "Esdeath",
    "origem": "Akame ga Kill",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 5,
    "max_star": 7,
    "hp": 100, "atk": 50, "matk": 60, "def": 20, "spd": 35, "crt": 40,
    "habilidade": {
        "nome": "Criocinese Extrema",
        "descricao": "Congela o alvo por 2 turnos, diminui a SPD inimiga geral em 50% e causa o somatório de ATK + MATK."
    },
    "evolucoes": {
        7: {
            "nome": "Mahapadma",
            "descricao": "Congela o próprio tempo! Inimigos perdem 1 turno. Esdeath aplica Fraqueza (dano sofrido +20%) e fica intocável por 2 turnos."
        }
    }
},
# =========================64
"cid_kagenou": {
    "nome": "Cid Kagenou (Shadow)",
    "origem": "The Eminence in Shadow",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 5,
    "max_star": 7,
    "hp": 120, "atk": 65, "matk": 45, "def": 20, "spd": 35, "crt": 30,
    "habilidade": {
        "nome": "Shadow Garden",
        "descricao": "Funde-se nas sombras, ocultando-se de ataques (Intocável por 2 turnos). O primeiro ataque ao sair causa Dano Dobrado."
    },
    "evolucoes": {
        7: {
            "nome": "I Am Atomic",
            "descricao": "Ignora DEF e Escudos com acerto crítico garantido. Causa (ATK + MATK) x 3 em todos os oponentes, atordoando sobreviventes por 1 turno."
        }
    }
},
# =========================65
"sung_jin_woo": {
    "nome": "Sung Jin Woo",
    "origem": "Solo Leveling",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 5,
    "max_star": 7,
    "hp": 100, "atk": 50, "matk": 50, "def": 20, "spd": 30, "crt": 30,
    "habilidade": {
        "nome": "Surgir!",
        "descricao": "Invoca 2 Soldados das Sombras (com 50% dos status do Sung). Eles puxam o Aggro inimigo e atacam passivamente."
    },
    "evolucoes": {
        7: {
            "nome": "Monarca das Sombras",
            "descricao": "Invoca Igris, Beru e Iron (100% de ATK/DEF e 50% HP). Se morrer, revive uma única vez com os atributos dobrados por 2 turnos."
        }
    }
},
# =========================66
"lucy_heartfilia": {
    "nome": "Lucy Heartfilia",
    "origem": "Fairy Tail",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 3,
    "max_star": 7,
    "hp": 65, "atk": 10, "matk": 45, "def": 10, "spd": 20, "crt": 15,
    "habilidade": {
        "nome": "Star Dress",
        "descricao": "Transforma-se, ganhando +30% de MATK e +20% de DEF durante 5 turnos contínuos."
    },
    "evolucoes": {
        5: {
            "nome": "Urano Metria",
            "descricao": "Conjura as estrelas! Reduz o MATK dos inimigos em 25% e causa um devastador (MATK + 50) em todos no campo."
        }
    }
},
# =========================67
"roxy_migurdia": {
    "nome": "Roxy Migurdia",
    "origem": "Mushoku Tensei",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 2,
    "max_star": 7,
    "hp": 60, "atk": 0, "matk": 40, "def": 15, "spd": 10, "crt": 10,
    "habilidade": {
        "nome": "Magia de Água King-Tier",
        "descricao": "Conjura jatos d'água. Recebe +20 de MATK no turno e tem 20% de chance de infligir Lentidão."
    },
    "evolucoes": {
        3: {
            "nome": "Lâmina de Água",
            "descricao": "Executa 3 disparos mágicos (100% MATK cada) que possuem +15% de chance de Crítico independentes."
        },
        5: {
            "nome": "Canhão de Água Comprimido",
            "descricao": "Disparo massivo: Ignora 30% da DEF mágica, diminui a SPD inimiga em 20% e causa 180% do MATK."
        }
    }
},
# =========================68
"shuna": {
    "nome": "Shuna",
    "origem": "Tensei Shitara Slime Datta Ken",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 1,
    "max_star": 7,
    "hp": 55, "atk": 15, "matk": 40, "def": 15, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Magia Sagrada",
        "descricao": "Magia pura. Causa 150% do MATK (Dano ainda maior em mortos-vivos e demônios em áreas específicas)."
    },
    "evolucoes": {
        3: {
            "nome": "Devoção Protetora",
            "descricao": "Remove todos os debuffs do esquadrão aliado e fortalece a DEF geral em 30%."
        },
        5: {
            "nome": "Expurgo das Almas",
            "descricao": "Destrói os buffs de status inimigos e causa um dano global de 150% de MATK em toda a front."
        }
    }
},
# =========================69
"julius_novachrono": {
    "nome": "Julius Novachrono",
    "origem": "Black Clover",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 70, "atk": 5, "matk": 60, "def": 20, "spd": 40, "crt": 20,
    "habilidade": {
        "nome": "Magia de Tempo: Chrono Anastasis",
        "descricao": "Rouba o tempo do oponente. Reduz a Ação/SPD do alvo em 50% e golpeia com 120% de MATK."
    },
    "evolucoes": {
        5: {
            "nome": "Cápsula do Tempo",
            "descricao": "Aprisiona no fluxo temporal. Congela 1 inimigo por 2 turnos, ignorando qualquer passiva de imunidade a controle."
        }
    }
},
# =========================70
"merlin_pecado": {
    "nome": "Merlin",
    "origem": "Nanatsu no Taizai",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 75, "atk": 0, "matk": 70, "def": 10, "spd": 20, "crt": 20,
    "habilidade": {
        "nome": "Infinity",
        "descricao": "Paralisa a duração mágica: Estende todos os buffs da sua equipe em +2 turnos e os debuffs inimigos em +2 turnos."
    },
    "evolucoes": {
        5: {
            "nome": "Absolute Cancel",
            "descricao": "A magia perfeita. Remove TODOS os buffs do inimigo, apaga TODOS os debuffs dos aliados e causa 200% do MATK como Dano Global."
        }
    }
},
# =========================71
"anos_voldigoad": {
    "nome": "Anos Voldigoad",
    "origem": "Maou Gakuin no Futekigousha",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 60, "matk": 60, "def": 30, "spd": 30, "crt": 30,
    "habilidade": {
        "nome": "Olhos Mágicos da Destruição",
        "descricao": "Ao olhar para o inimigo, dissolve qualquer escudo mágico, ignora defesa base e causa 300% de MATK bruto."
    },
    "evolucoes": {
        7: {
            "nome": "Espada da Razão Venuzdnor",
            "descricao": "A lógica não se aplica. Ignora invulnerabilidade, sempre crita e drena instantaneamente 70% do HP dos inimigos (ou Insta-Kill se HP < 50%)."
        }
    }
},
# =========================72
"gilgamesh": {
    "nome": "Gilgamesh",
    "origem": "Fate/Stay Night",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 55, "matk": 65, "def": 25, "spd": 30, "crt": 35,
    "habilidade": {
        "nome": "Gate of Babylon",
        "descricao": "Dispara o tesouro divino: 6 ataques somando 100% de (MATK + ATK) por golpe, acertando inimigos de forma aleatória."
    },
    "evolucoes": {
        7: {
            "nome": "Enuma Elish (EA)",
            "descricao": "A espada que dividiu o mundo! Dano de 600% MATK em área, ignorando imortalidade. Sobreviventes perdem 50% de SPD e DEF."
        }
    }
},
# =========================73
"hange_zoe": {
    "nome": "Hange Zoe",
    "origem": "Attack on Titan",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "hp": 60, "atk": 20, "matk": 0, "def": 30, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Análise Estratégica",
        "descricao": "Revela falhas na guarda adversária. Todos os aliados recebem +20% de Chance de Crítico e +20% de Precisão."
    },
    "evolucoes": {
        3: {
            "nome": "Pesquisa de Campo",
            "descricao": "Marca os oponentes aplicando o debuff de Fraqueza, aumentando todo o dano que eles recebem em +25% por 3 turnos."
        },
        5: {
            "nome": "Mobilidade DMT Avançada",
            "descricao": "Hange ganha +50% de SPD/CRT/ATK, e bufando passivamente os golpes dos aliados em +30 de ATK por 3 turnos."
        }
    }
},
# =========================74
"nezuko_kamado": {
    "nome": "Nezuko",
    "origem": "Demon Slayer",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 30, "matk": 30, "def": 20, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Kekkijutsu de Cura",
        "descricao": "Usa sangue para queimar venenos. Cura um aliado em 250% do MATK e remove Queimaduras, Sangramentos ou Venenos."
    },
    "evolucoes": {
        5: {
            "nome": "Explosão de Sangue Definitiva",
            "descricao": "Poder purificador! Cura toda a equipe, remove absolutamente TODOS os debuffs e aplica Regeneração passiva por 3 turnos."
        }
    }
},
# =========================75
"raphtalia": {
    "nome": "Raphtalia",
    "origem": "The Rising of the Shield Hero",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 3,
    "max_star": 7,
    "hp": 85, "atk": 40, "matk": 10, "def": 20, "spd": 40, "crt": 10,
    "habilidade": {
        "nome": "A Espada do Herói",
        "descricao": "Juramento de batalha. Raphtalia encanta o Herói Líder, concedendo-lhe +35% de ATK/MATK e 20% de SPD por 3 rodadas."
    },
    "evolucoes": {
        5: {
            "nome": "Evolução do Vínculo",
            "descricao": "Motiva a equipe toda! +30% ATK/DEF/SPD em área por 3 turnos. (Buffa o ganho final de XP do Líder em 50%)."
        }
    }
},
# =========================76
"shoko_ieiri": {
    "nome": "Shoko Ieiri",
    "origem": "Jujutsu Kaisen",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 10, "matk": 20, "def": 15, "spd": 5, "crt": 10,
    "habilidade": {
        "nome": "Energia Amaldiçoada Reversa",
        "descricao": "Fluxo de cura direcionado que restaura o HP de um alvo em 300% do MATK."
    },
    "evolucoes": {
        3: {
            "nome": "Autópsia Forense",
            "descricao": "Analisa o corpo de um inimigo abatido, deduzindo táticas para reduzir a DEF dos restantes em 30% e cortando a regeneração deles pela metade."
        },
        5: {
            "nome": "Talento Especial de Cura",
            "descricao": "Cura global monstruosa de 400% MATK em toda a equipe, limpa debuffs pesados e Shoko recupera 20% de si mesma no processo."
        }
    }
},
# =========================77
"aqua_konosuba": {
    "nome": "Aqua",
    "origem": "KonoSuba",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 4,
    "max_star": 7,
    "hp": 100, "atk": 10, "matk": 45, "def": 20, "spd": 10, "crt": 15,
    "habilidade": {
        "nome": "Ressurreição Divina",
        "descricao": "Magia da Deusa! Revive completamente um aliado abatido trazendo-o de volta com 50% de HP (1 vez por combate)."
    },
    "evolucoes": {
        5: {
            "nome": "Dispersão Sagrada / Turn Undead",
            "descricao": "300% de MATK como luz divina (extra em mortos-vivos). Em seguida, dissolve feitiços nocivos dos aliados e cura 25% da vida geral do grupo."
        }
    }
},
# =========================78
"kisuke_urahara": {
    "nome": "Kisuke Urahara",
    "origem": "Bleach",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 50, "matk": 35, "def": 40, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Shikai: Chiasumi no Tate",
        "descricao": "Cria um escudo impenetrável de pura energia espiritual (Benihime), equivalente a 50% do HP máximo de quem o recebe."
    },
    "evolucoes": {
        7: {
            "nome": "Bankai: Kannonbiraki Benihime Aratame",
            "descricao": "O poder de reestruturar! Cura completamente a party, remove debuffs, conserta armaduras quebradas e ressuscita membros ou summons abatidos!"
        }
    }
},
# =========================79
"maomao": {
    "nome": "Maomao",
    "origem": "Kusuriya no Hitorigoto",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 5,
    "max_star": 7,
    "hp": 100, "atk": 20, "matk": 30, "def": 40, "spd": 10, "crt": 10,
    "habilidade": {
        "nome": "Mestra dos Venenos",
        "descricao": "Imune a toxinas e debuffs. Aplica um Veneno letal que inflige 200% do MATK passivamente por 2 turnos, e corta a cura do alvo para 50%."
    },
    "evolucoes": {
        7: {
            "nome": "Boticária de Alto Calão (Toxic)",
            "descricao": "Coquetel Mortal: Aplica simultaneamente Veneno, Lentidão, Fraqueza e Anti-Cura em um inimigo. Em compensação, os aliados bebem tônicos e ganham 20% de HP máximo convertido em dano físico/mágico."
        }
    }
},
# =========================80
"bojji": {
    "nome": "Bojji",
    "origem": "Ousama Ranking",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 2,
    "max_star": 7,
    "hp": 90, "atk": 30, "matk": 0, "def": 10, "spd": 50, "crt": 10,
    "habilidade": {
        "nome": "Esquiva do Pequeno Rei",
        "descricao": "Puxa a atenção (Aggro) de todos os monstros no campo e utiliza sua leitura para elevar a própria SPD em 40%."
    },
    "evolucoes": {
        3: {
            "nome": "Agilidade Divina",
            "descricao": "Garante 60% de chance de esquivar de qualquer golpe, age sempre primeiro, e se esquivar, contra-ataca os pontos fracos com 150% do ATK."
        },
        5: {
            "nome": "Golpe de Separação Molecular",
            "descricao": "Puxa o agro global e fica inteiramente imune a dano (100% Dodge temporário) por 2 turnos. Após isso, sua esquiva base aumenta para 50%."
        }
    }
},
# =========================81
"mash_burnedead": {
    "nome": "Mash Burnedead",
    "origem": "Mashle",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "hp": 100, "atk": 45, "matk": 0, "def": 45, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Magia dos Músculos",
        "descricao": "Tenciona a carne! Eleva a DEF em 40%, seu HP em 25% e passa a rebater com os punhos nus 25% de todo dano que toma."
    },
    "evolucoes": {
        5: {
            "nome": "Hora do Profiterole",
            "descricao": "Pausa para comer um Profiterole. Cura instantaneamente 40% do HP e turbina a DEF e o ATK em 40% por 3 contusivos turnos."
        }
    }
},
# =========================82
"kirishima_eijiro": {
    "nome": "Eijiro Kirishima",
    "origem": "Boku no Hero Academia",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 1,
    "max_star": 7,
    "hp": 100, "atk": 10, "matk": 10, "def": 50, "spd": 5, "crt": 10,
    "habilidade": {
        "nome": "Endurecer (Hardening)",
        "descricao": "O corpo vira rocha maciça! Melhora em 60% a sua DEF e reflete 25% do impacto recebido nos atacantes."
    },
    "evolucoes": {
        3: {
            "nome": "Red Counter",
            "descricao": "Endurecimento aprimorado. Recebe +100% de DEF, força todos a atacá-lo, e o reflexo de dano escala para 30%."
        },
        5: {
            "nome": "Red Riot Unbreakable",
            "descricao": "O auge da tenacidade. Reduz o dano sofrido em incríveis 90%, ignora golpes críticos, e toma automaticamente qualquer golpe fatal apontado a um aliado."
        }
    }
},
# =========================83
"naofumi": {
    "nome": "Naofumi Iwatani",
    "origem": "The Rising of the Shield Hero",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,
    "hp": 130, "atk": 10, "matk": 45, "def": 60, "spd": 10, "crt": 20,
    "habilidade": {
        "nome": "Escudo da Ira",
        "descricao": "Ameaça os inimigos chamando o foco total. Seu escudo absorve o equivalente a 50% de seu HP máximo e responde ataques diretos com o dobro de MATK."
    },
    "evolucoes": {
        7: {
            "nome": "Armadura do Imperador Dragão",
            "descricao": "Bloqueio Absoluto. Dobra sua altíssima DEF (100%), cria escudo extra de 50% de HP, reflete 40% de dano sombrio e injeta regeneração constante de 10% por turno."
        }
    }
},
# =========================84
"brolly": {
    "nome": "Broly",
    "origem": "Dragon Ball",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 115, "atk": 55, "matk": 20, "def": 40, "spd": 15, "crt": 10,
    "habilidade": {
        "nome": "Evolução Reativa em Combate",
        "descricao": "O saiyajin brutal absorve os golpes para ficar mais forte. Cada soco que recebe aumenta +10% de ATK e +5% de DEF (podendo somar até 10 stacks)."
    },
    "evolucoes": {
        5: {
            "nome": "Lendário Super Saiyajin",
            "descricao": "O poder máximo que foge de controle! +100% de capacidade de HP, +80% de aumento de ATK brutal, +50% de DEF, com golpes arrancando nacos de 50% do HP base inimigo."
        }
    }
},
# =========================85
"garou": {
    "nome": "Garou",
    "origem": "One Punch Man",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 120, "atk": 50, "matk": 25, "def": 40, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Punho de Água Corrente, Rocha Esmagadora",
        "descricao": "Domínio técnico de artes marciais. Anula suavemente 50% do dano de impactos diretos e imediatamente rebate com 100% de seu próprio ataque."
    },
    "evolucoes": {
        5: {
            "nome": "Punho Cortante do Redemoinho de Ferro",
            "descricao": "Postura devastadora. Para cada ataque tentado contra Garou, ele devolve com DANO DOBRADO por 1 rodada. Sua capacidade de esquiva e CRT também sobem em 50%."
        }
    }
},
# =========================86
"benimaru_shinmou": {
    "nome": "Benimaru Shinmou",
    "origem": "Fire Force",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,
    "hp": 125, "atk": 50, "matk": 50, "def": 45, "spd": 30, "crt": 20,
    "habilidade": {
        "nome": "Lua Carmesim",
        "descricao": "Moldura mágica ardente igual ao seu MATK. Inimigos agressores pegam Fogo (Burn de MATK/2 turnos) e Fraqueza (+30% dano extra recebido)."
    },
    "evolucoes": {
        7: {
            "nome": "Sol da Meia-Noite / Amaterasu",
            "descricao": "Todos os oponentes entram em combustão ao tentar feri-lo, torrando a vida em MATKx2 por 4 turnos. A aura de Benimaru também o cede +60% de DEF e MATK extras."
        }
    }
},
# =========================87
"all_might": {
    "nome": "All Might",
    "origem": "Boku no Hero Academia",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "hp": 110, "atk": 50, "matk": 0, "def": 40, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "United States of Smash",
        "descricao": "Tudo numa mão só! Soco de 250% ATK contra um alvo, inspirando o usuário a ganhar bônus simultâneo de +25% de ATK/MATK e DEF na mesma rodada."
    },
    "evolucoes": {
        5: {
            "nome": "Pilar da Paz (One For All 100%)",
            "descricao": "Força imparável (+70% de HP Máximo e DEF, além de +50 limpos de Ataque). Como o símbolo da justiça, ele ignora efeitos paralisantes como Lentidão e Fraqueza."
        }
    }
},
# =========================88
"barba_branca": {
    "nome": "Edward Newgate (Barba Branca)",
    "origem": "One Piece",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,
    "hp": 150, "atk": 40, "matk": 40, "def": 35, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Tremor-Tremor (Gura Gura no Mi)",
        "descricao": "Racha o espaço! Atrai obrigatoriamente a atenção global. Ao socar o ar, afeta o esquadrão rival enfraquecendo a ofensa (-25% ATK) e aplicando Lentidão."
    },
    "evolucoes": {
        7: {
            "nome": "O Homem que Faz o Mundo Tremer",
            "descricao": "Massacre: Inimigos tomam debuff massivo (-40% ATK, DEF e SPD). O colosso marinho absorve metade do dano (Dano/2) e se recusa a morrer, lutando por mais 1 turno mesmo com HP no zero."
        }
    }
},
# =========================89
"alladin": {
    "nome": "Alladin",
    "origem": "Magi",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,
    "hp": 135, "atk": 35, "matk": 40, "def": 40, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Borg (Barreira de Rukh)",
        "descricao": "Cria um isolamento mágico que suporta danos até 60% do seu vasto HP, e passivamente converte sobras do MATK em uma parede sólida de DEF."
    },
    "evolucoes": {
        7: {
            "nome": "Invocar: Gigante Ugo",
            "descricao": "Traz Ugo à arena para defender. Ugo possui 150 de HP próprio para reter todo o Aggro inimigo e distribui escudos no valor de 50% de HP para proteger seus pequenos aliados (+50% DEF Geral)."
        }
    }
},
# =========================90
"senku_ishigami": {
    "nome": "Senku Ishigami",
    "origem": "Dr. Stone",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 2,
    "max_star": 7,
    "hp": 60, "atk": 20, "matk": 0, "def": 20, "spd": 15, "crt": 5,
    "habilidade": {
        "nome": "Inteligência Extrema (Ponto Cego)",
        "descricao": "Usa a ciência para perfurar defesas teóricas. Todos os amigos ganham +20% em ofensiva (ATK/MATK) e o inimigo escolhido sofre com -15% de DEF."
    },
    "evolucoes": {
        3: {
            "nome": "A Ciência Salva Vidas (Dr. Stone)",
            "descricao": "Produz ferramentas que sortearão efeitos: Curativos (30 HP), Escudos Anti-Impacto (50 proteção), Pólvora pra mobilidade (+20% SPD) ou Ácidos letais (+50% ATK)."
        },
        5: {
            "nome": "E=mc² (Fórmula Definitiva)",
            "descricao": "Calcula a rota da vitória: Anula um feitiço nefasto (Debuff) de cada guerreiro amigo, garantindo um disparo em seus status (+40% de ATK, MATK e SPD de uma vez)."
        }
    }
},
# =========================91
"roy_mustang": {
    "nome": "Roy Mustang",
    "origem": "Fullmetal Alchemist",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 3,
    "max_star": 7,
    "hp": 70, "atk": 10, "matk": 50, "def": 20, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Alquimista das Chamas",
        "descricao": "Estala os dedos. 220% de Fogo e Morte (MATK). A temperatura deforma a armadura do alvo (-20% DEF) e incendeia seus turnos a 20 de dano mágico fixo contínuo."
    },
    "evolucoes": {
        5: {
            "nome": "O Sacrifício e a Pedra Filosofal",
            "descricao": "Abre o portão proibido! O campo arde num inferno onde todos os adversários levam 50 de Dano Fixo por 2 turnos, e a party do Coronel ganha 50% mais Força Mágica + Cura rápida (15%)."
        }
    }
},
# =========================92
"light_yagami": {
    "nome": "Light Yagami",
    "origem": "Death Note",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 50, "atk": 15, "matk": 10, "def": 20, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Death Note (Execução Programada)",
        "descricao": "Escreve um nome calmamente. Marca a vítima e, exatamente 3 turnos após a canetada, o coração cede e leva embora 50% de sua vida como Dano Verdadeiro irredutível."
    },
    "evolucoes": {
        5: {
            "nome": "Kira, o Shinigami Humano",
            "descricao": "Expande o caderno para ditar sentenças amplas: Marca dois adversários simultâneos, fazendo com que sua resistência seja drenada e sofram 35% mais dano pelo resto do combate."
        }
    }
},
# =========================93
"johan_liebert": {
    "nome": "Johan Liebert",
    "origem": "Monster",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 1,
    "max_star": 7,
    "hp": 60, "atk": 20, "matk": 0, "def": 25, "spd": 10, "crt": 5,
    "habilidade": {
        "nome": "Manipulação Psicológica",
        "descricao": "Um sussurro capaz de distorcer mentes. Planta a dúvida no oponente, causando 30% de chance de fazê-lo agredir a própria equipe."
    },
    "evolucoes": {
        3: {
            "nome": "O Sociopata Perfeito",
            "descricao": "Seu simples olhar desestabiliza a linha de frente inimiga, afundando o moral de todos e cortando seus ATK, DEF e SPD num limiar de 20%."
        },
        5: {
            "nome": "O Verdadeiro Monstro do Fim",
            "descricao": "O terror se alastra. Os inimigos sucumbem ao puro Medo, forçando-os a errar a metade de seus botes (50% Perda de Precisão) e aplicar apenas 60% da sua força normal (Dano -40%)."
        }
    }
},
# =========================94
"chrollo_lucilfer": {
    "nome": "Chrollo Lucilfer",
    "origem": "Hunter x Hunter",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 5,
    "max_star": 7,
    "hp": 100, "atk": 50, "matk": 30, "def": 20, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "The Sun and Moon (Sol e Lua)",
        "descricao": "Sela os corpos dos adversários em batalha com pólvora de Nen. Quando um alvo marcado vai a óbito, ele detona instantaneamente causando estilhaços mágicos (200% MATK) nos parceiros próximos."
    },
    "evolucoes": {
        7: {
            "nome": "Skill Hunter (Livro de Roubos)",
            "descricao": "Folheia as táticas! Analisa e furta uma habilidade do inimigo e a casta em sua versão otimizada durante os próximos 3 turnos (Bosses entregam uma versão equilibrada)."
        }
    }
},
# =========================95
"kamina": {
    "nome": "Kamina",
    "origem": "Gurren Lagann",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 5,
    "max_star": 7,
    "hp": 90, "atk": 45, "matk": 0, "def": 20, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Discurso Tengen Toppa",
        "descricao": "Quem você acha que nós somos?! Impulsiona o time até os céus, bufando TODOS os amigos com +50% ATK, +40% da resiliência (DEF) e um gás de +35% de Agilidade (SPD)."
    },
    "evolucoes": {
        7: {
            "nome": "Fusão de Almas (Gurren Lagann)",
            "descricao": "Nunca recua, nunca se rende. As emoções incendeiam, turbinando as estatísticas em 50% em TODOS OS ATRIBUTOS da equipe! Todos ficam Imunes ao Status de Medo e ganham alívio curativo (20% HP)."
        }
    }
},
# =========================96
"joseph_joestar": {
    "nome": "Joseph Joestar",
    "origem": "JoJo's Bizarre Adventure",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 30, "matk": 10, "def": 20, "spd": 10, "crt": 10,
    "habilidade": {
        "nome": "Hermit Purple (Espírito Oculto)",
        "descricao": "Puxa fotos do futuro com o stand de videira. Antecipa as ciladas oponentes e joga 30% a mais na barra de Esquiva dos companheiros."
    },
    "evolucoes": {
        3: {
            "nome": "Ondas Concentradas (Hamon)",
            "descricao": "Injeta a força vital do sol nos pulmões. Reforça o time curando as impurezas de Veneno e reabastecendo 20 HP, mais suporte leve (+20% DEF)."
        },
        5: {
            "nome": "Sua próxima frase será...!",
            "descricao": "Clarividência das Ruas. Prende o próximo inimigo pelo ego, anulando por completo seu ataque ofensivo e deixando o grupo eufórico com +50% no Acerto Crítico (CRT) para retaliação."
        }
    }
},
# =========================97
"shikamaru": {
    "nome": "Shikamaru Nara",
    "origem": "Naruto",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 70, "atk": 15, "matk": 40, "def": 10, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Possessão das Sombras (Kagemane)",
        "descricao": "O gênio relaxado conecta suas sombras ao peão-alvo. O monstro é amarrado por 1 turno completo e perde dolorosos 50% em sua mobilidade (SPD)."
    },
    "evolucoes": {
        5: {
            "nome": "Estratégia Magistral (QI 200)",
            "descricao": "Dez passos à frente de quem luta no tabuleiro. Amigos recebem um bônus pesado de 35% nos Criticals, Agilidade e Precisão, e os oponentes perdem a estrutura tática com decaimento de 25% em SPD/DEF."
        }
    }
},
# =========================98
"usopp": {
    "nome": "Usopp",
    "origem": "One Piece",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 1,
    "max_star": 7,
    "hp": 50, "atk": 40, "matk": 0, "def": 10, "spd": 30, "crt": 25,
    "habilidade": {
        "nome": "Tiro de 1000 Léguas da Pop Green",
        "descricao": "Saca a funda num disparo curvo que destrói em 180% de ATK e tem surpresa de botar o alvo para nanar atordoado (Stun: 40%)."
    },
    "evolucoes": {
        3: {
            "nome": "Rei dos Atiradores: Sogeking",
            "descricao": "Veste a máscara e a coragem em seu coração sobe: Precisão alça aos 30%, CRT a 50%, e a próxima semente será duplamente mortal (Dano x 2)."
        },
        5: {
            "nome": "O Herói Falsificado (God Usopp)",
            "descricao": "Fama Divina! O panteão o teme e seus amigos riem: Os parceiros de bando ganham furtivos +25% de Esconder-se (Esquiva) e de Acerto Fatal. A mentira dele ainda tem 20% de Chance de paralisar o campo com intimidação."
        }
    }
},
# =========================99
"kobeni": {
    "nome": "Kobeni",
    "origem": "Chainsaw Man",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 1,
    "max_star": 7,
    "hp": 50, "atk": 20, "matk": 20, "def": 10, "spd": 15, "crt": 15,
    "habilidade": {
        "nome": "Contrato Obscuro com o Demônio",
        "descricao": "Surta de pânico e assina por desespero! Um tiro no escuro pode render: Módica Cura (20), Acréscimo no Dano, Um buff esquivo, ou mais chance no Crítico (+20 points)."
    },
    "evolucoes": {
        3: {
            "nome": "Kobeni's Car",
            "descricao": "Corre de medo... e capota o seu próprio carro (220% de acerto ATK no espaço em Área). Inimigos tem 30% de engolir um STUN para processar a cena que viram."
        },
        5: {
            "nome": "Dança do Azar (Caos)",
            "descricao": "O azar dela passa por osmose para todos os que a assustam: A precisão da trupe inimiga e sua capacidade fatal esvaem (-25% Precisão/Crit), e ela escorrega e sai ilesa com o dobro de Esquiva (50%)."
        }
    }
},
# =========================100
"riza_hawkeye": {
    "nome": "Riza Hawkeye",
    "origem": "Fullmetal Alchemist",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 2,
    "max_star": 7,
    "hp": 60, "atk": 45, "matk": 0, "def": 20, "spd": 30, "crt": 25,
    "habilidade": {
        "nome": "Instinto da Falcão (Olho de Águia)",
        "descricao": "Mira focada no calcanhar de Aquiles. Indica aberturas táticas onde sua equipe ganha bônus de agressividade de +20% no Critical Rating."
    },
    "evolucoes": {
        3: {
            "nome": "Disparo Frio",
            "descricao": "Carga explosiva balística focada (250% ATK do cano pra ponta). Bala que desconsidera e fura as placas defensivas rasgando em 50% o limiar da DEF do alvo."
        },
        5: {
            "nome": "Os Segredos das Chamas (Costas Marcadas)",
            "descricao": "Posiciona a Alquimia de chamas selada num único infeliz escolhido. Daquele tiro em diante o alvo receberá brutais 40% a mais na somatória das penalidades."
        }
    }
},
# =========================101
"lady_nagant": {
    "nome": "Lady Nagant",
    "origem": "Boku no Hero Academia",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 3,
    "max_star": 7,
    "hp": 75, "atk": 50, "matk": 0, "def": 20, "spd": 35, "crt": 30,
    "habilidade": {
        "nome": "O Fuzil Vivo (Rifle Orgânico)",
        "descricao": "Converte a própria trança na munição. Causa o absurdo peso de 250% de ATK de longa-distância. Um tiro absoluto que ignora tanques protetores e habilidades de Provocação (Taunt)."
    },
    "evolucoes": {
        5: {
            "nome": "Passeio Aéreo Suave (Air Walk)",
            "descricao": "Pisando nos céus com sua Quirck secundária para atirar como fantasma. Puxa +50% nas evasões (Esquiva) e na mobilidade (SPD). Além de bater o gatilho duplamente em um turno!"
        }
    }
},
# =========================102
"spike_spiegel": {
    "nome": "Spike Spiegel",
    "origem": "Cowboy Bebop",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 45, "matk": 0, "def": 20, "spd": 30, "crt": 30,
    "habilidade": {
        "nome": "Jeet Kune Do & Tiros Certeiros",
        "descricao": "Dançando sobre água: See You Space Cowboy. Uma tática de +30% na barra de Dodge; Quando desvia de um míssil/golpe agressivo, Spike retalha no impulso sem pena."
    },
    "evolucoes": {
        5: {
            "nome": "Cowboy de Espaço (Bang)",
            "descricao": "A velha rotina da caça recompensa... Três batidas seguidas no Jericó: Cada disparo dá 150% do seu limite, acompanhado de duplicação total das garantias de Tiro no Olho (+Dbl de Chance Crítica)."
        }
    }
},
# =========================103
"sakamoto": {
    "nome": "Sakamoto",
    "origem": "Sakamoto Days",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 60, "matk": 0, "def": 40, "spd": 40, "crt": 35,
    "habilidade": {
        "nome": "Regra 1: Dia Z (Arma Improvisada)",
        "descricao": "Gordinho mortal pega uma caneta/carrinho pra ferir: São batidos 220% de Dano Físico. Seu truque esconde de modo roleta aleatória a aplicação de Bleed (Sangramento), Stun ou rachadura das barreiras (Redução de DEF)."
    },
    "evolucoes": {
        5: {
            "nome": "O Ex-Hitman Lendário",
            "descricao": "Quando a coisa aperta, ele emagrece num Flash... Magia do profissional esguio! Recebe 60% de acertos fatais, e 40% na agilidade motora - ele agora faz suas faxinas em duplo nos turnos."
        }
    }
},
# =========================104
"genya_shinazugawa": {
    "nome": "Genya Shinazugawa",
    "origem": "Demon Slayer",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 50, "matk": 20, "def": 10, "spd": 20, "crt": 40,
    "habilidade": {
        "nome": "Escopeta de Aço Nichirin",
        "descricao": "Seja empurrado para trás do tiro explosivo! Atinge brutalmente com 280% de seu modesto ataque, tirando além da vida o equilíbrio do capanga (Reduz em 25% a linha da DEF inimiga)."
    },
    "evolucoes": {
        5: {
            "nome": "Sistema Digestivo Demoníaco",
            "descricao": "Morde e assimila o monstro! Arranca traços vitais (Atributos Gerais) do desafiante por meio de um contra-absorver: Restaura sua carcaça ferida em curativo (+25% HP) e ganha fôlego massivo por 3 turnos (ATK em 50%)."
        }
    }
},
# =========================105
"alucard": {
    "nome": "Alucard",
    "origem": "Hellsing",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 60, "matk": 40, "def": 20, "spd": 50, "crt": 40,
    "habilidade": {
        "nome": "Balas Abençoadas (Casull & Jackal)",
        "descricao": "A risada do Vampiro precede as armas. Tripla descarga furiosa com peso de chumbo misturado à maldição (270% de Ataque nos inimigos por cada hit cego que varre 20% do que resta das proteções de DEF das presas)."
    },
    "evolucoes": {
        7: {
            "nome": "Liberação Cromwell Nível 0",
            "descricao": "O rio de Almas Mortas... Jorra sombras dos devorados, criando clones fumaçados com capacidade em metade (50%) dos seus estigmas de Guerra. Alucard chupa a essência, enchendo o próprio poço em 50% e estourando tanto HP quanto ATK dobrados num limite de sangue de três longos turnos."
        }
    }
},
# =========================106
"simo_hayha": {
    "nome": "Simo Hayha",
    "origem": "Shuumatsu no Valkyrie",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 70, "matk": 40, "def": 20, "spd": 50, "crt": 50,
    "habilidade": {
        "nome": "Morte Branca: Juramento Glacial",
        "descricao": "Olho no telescópio, morte sem retorno! Uma mira afiada e imutável que jamais encontra a palavra ERRO: Passa por cima de esquivadores, Camuflados do radar ou escudeiros medievais no absurdo peso de 300% (ATK). Se a poeira baixar e a caça tombar, o atirador tem aval automático de novo recarregamento e turno extra."
    },
    "evolucoes": {
        7: {
            "nome": "Neve e Silêncio Profuso (Deus da Morte)",
            "descricao": "Uma chuva de flores brancas que esconde as balas mais assustadoras dos mortais. O caçador de 3 turnos detona sem parar. Garante precisão mágica nos 100% de Acertos/Crit e dispara um pente varredor em todo o cenário a frente, matando as barreiras e imortalidade por um cano flamejante escalado de 350% em picos de ataque base."
        }
    }
},
# =========================107
"reinhard_van_astrea": {
    "nome": "Reinhard Van Astrea",
    "origem": "Re:Zero",
    "emoji": "👊",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "imagem": "",

    "hp": 140,
    "atk": 95,
    "matk": 20,
    "def": 45,
    "spd": 40,
    "crt": 20,

    "habilidade": {
        "nome": "Espada do Dragão Reid",
        "descricao": "Causa dano massivo de 400% ATK ignorando 50% da defesa."
    },

    "evolucoes": {
        7: {
            "nome": "Proteção Divina Suprema",
            "descricao": "Recebe Imortalidade por 2 turnos. Se morrer, revive uma vez. Não pode ser afetado por debuff ou efeitos de status negativos, imune a lentidão, medo, congelamento, fraqueza, queimadura e insta-kill."
        }
    }
},
# =========================108
"qifrey": {
    "nome": "Qifrey",
    "origem": "Witch Hat Atelier",
    "emoji": "✨",
    "classe": "Mago",
    "raridade": 2,
    "max_star": 7,
    "imagem": "",

    "hp": 80,
    "atk": 10,
    "matk": 50,
    "def": 15,
    "spd": 25,
    "crt": 5,

    "habilidade": {
        "nome": "Glifo Arcano",
        "descricao": "Causa MATK+20."
    },

    "evolucoes": {
        3: {
            "nome": "Círculo Elemental",
            "descricao": "Atinge todos os inimigos com MATK + 50"
        },
        5: {
            "nome": "Magia Proibida",
            "descricao": "Grande explosão mágica, causa 300% de MATK e atinge todos os inimigos."
        }
    }
},
# =========================109
"dark_magician_girl": {
    "nome": "Dark Magician Girl",
    "origem": "Yu-Gi-Oh!",
    "emoji": "✨",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "imagem": "",

    "hp": 100,
    "atk": 20,
    "matk": 75,
    "def": 20,
    "spd": 30,
    "crt": 10,

    "habilidade": {
        "nome": "Dark Burning Attack",
        "descricao": "Explosão mágica poderosa, causa 200% de MATK"
    },

    "evolucoes": {
        5: {
            "nome": "Dark Magic Expanded",
            "descricao": "Atinge todos os inimigos, causando 300% de MATK e aplica lentidão."
        }
    }
},
# =========================110
"hatsune_miku": {
    "nome": "Hatsune Miku",
    "origem": "Vocaloid",
    "emoji": "🩹",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "imagem": "",

    "hp": 110,
    "atk": 5,
    "matk": 35,
    "def": 15,
    "spd": 35,
    "crt": 5,

    "habilidade": {
        "nome": "Canção da Esperança",
        "descricao": "Cura um aliado, +50HP"
    },

    "evolucoes": {
        3: {
            "nome": "Encore",
            "descricao": "Aumenta SPD dos aliados, +20"
        },
        5: {
            "nome": "Miku Expo",
            "descricao": "Cura toda a equipe, 50% do HP geral"
        }
    }
},
# =========================111
"tokisaki_kurumi": {
    "nome": "Tokisaki Kurumi",
    "origem": "Date A Live",
    "emoji": "🏹",
    "classe": "Atirador",
    "raridade": 5,
    "max_star": 7,
    "imagem": "",

    "hp": 120,
    "atk": 85,
    "matk": 30,
    "def": 25,
    "spd": 55,
    "crt": 30,

    "habilidade": {
        "nome": "Zafkiel",
        "descricao": "Dano crítico altíssimo, seu crítico possui dano triplicado."
    },

    "evolucoes": {
        7: {
            "nome": "Cidade dos Clones",
            "descricao": "Ataca múltiplos inimigos, causa 500% de dano geral."
        }
    }
},
# =========================112
"dante": {
    "nome": "Dante",
    "origem": "Devil May Cry",
    "emoji": "🏹",
    "classe": "Atirador",
    "raridade": 5,
    "max_star": 7,
    "imagem": "",

    "hp": 100,
    "atk": 60,
    "matk": 15,
    "def": 25,
    "spd": 40,
    "crt": 20,

    "habilidade": {
        "nome": "Ebony & Ivory",
        "descricao": "Rajada de tiros críticos. Da 5 ataques, cada ataque possui 50% de chance de crítico."
    },

    "evolucoes": {
        7: {
            "nome": "Devil Trigger",
            "descricao": "Aumenta ATK e SPD em 50 ambos."
        }
    }
},
# =========================113
"rengoku_kyojuro": {
    "nome": "Kyojuro Rengoku",
    "origem": "Demon Slayer",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 65, "matk": 0, "def": 25, "spd": 40, "crt": 30,
    "habilidade": {
        "nome": "Respiração das Chamas",
        "descricao": "Causa dano massivo de ATK + 40 e aplica debuff de queimadura."
    },
    "evolucoes": {
        7: {
            "nome": "Nona Forma: Rengoku",
            "descricao": "Dano massivo único (ATK x 3), mas o usuário perde 30% do HP atual."
        }
    }
},
# =========================114
"shinra_kusakabe": {
    "nome": "Shinra Kusakabe",
    "origem": "Fire Force",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 55, "matk": 20, "def": 20, "spd": 45, "crt": 20,
    "habilidade": {
        "nome": "Pegadas do Diabo",
        "descricao": "Um chute em alta velocidade que causa ATK + 30 e aumenta sua própria SPD em 10."
    },
    "evolucoes": {
        5: {
            "nome": "Adolla Burst",
            "descricao": "Concede 30% de chance de atacar novamente no mesmo turno e buffa SPD em 20."
        }
    }
},
# =========================115
"ban_pecado": {
    "nome": "Ban",
    "origem": "Nanatsu no Taizai",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,
    "hp": 130, "atk": 45, "matk": 0, "def": 30, "spd": 35, "crt": 25,
    "habilidade": {
        "nome": "Snatch",
        "descricao": "Rouba 15 de ATK de um inimigo e cura a si mesmo em 20 HP."
    },
    "evolucoes": {
        7: {
            "nome": "Imortalidade",
            "descricao": "Caso seu HP chegue a 0, revive instantaneamente com 50% de HP (1x por batalha)."
        }
    }
},
# =========================116
"inosuke_hashibira": {
    "nome": "Inosuke Hashibira",
    "origem": "Demon Slayer",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 3,
    "max_star": 7,
    "hp": 85, "atk": 45, "matk": 0, "def": 15, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Corte Duplo",
        "descricao": "Ataca duas vezes aleatoriamente, causando ATK + 15 por acerto."
    },
    "evolucoes": {
        5: {
            "nome": "Consciência Espacial",
            "descricao": "Passa a ignorar debuffs de cegueira e aumenta a chance de esquiva."
        }
    }
},
# =========================117
"luck_voltia": {
    "nome": "Luck Voltia",
    "origem": "Black Clover",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 80, "atk": 50, "matk": 30, "def": 15, "spd": 55, "crt": 25,
    "habilidade": {
        "nome": "Magia de Relâmpago",
        "descricao": "Ataque fulminante que tem 20% de chance de atordoar (Stun) o alvo por 1 turno."
    },
    "evolucoes": {
        5: {
            "nome": "Armadura de Raios",
            "descricao": "Aumenta SPD em 20 e os ataques passam a causar dano mágico adicional."
        }
    }
},
# =========================118
"mikey_manjiro": {
    "nome": "Manjiro Sano (Mikey)",
    "origem": "Tokyo Revengers",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 1,
    "max_star": 7,
    "hp": 75, "atk": 55, "matk": 0, "def": 10, "spd": 35, "crt": 25,
    "habilidade": {
        "nome": "Chute Nuclear",
        "descricao": "Causa um dano físico altíssimo no alvo (ATK + 35)."
    },
    "evolucoes": {
        3: {
            "nome": "Chute de 540°",
            "descricao": "Nocauteia um alvo, stunnando ele por 1 turno e causando ATK + 45"
        },

        5: {
            "nome": "Impulsos Obscuros",
            "descricao": "Ignora 50% da defesa do alvo, mas o próprio personagem perde 10 de DEF."
        }
    }
},

# =========================119
"saber_artoria": {
    "nome": "Artoria Pendragon (Saber)",
    "origem": "Fate/Stay Night",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 110, "atk": 70, "matk": 40, "def": 30, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Ataque Invisível",
        "descricao": "Causa dano de ATK + MATK a um inimigo com 100% de precisão (não pode errar)."
    },
    "evolucoes": {
        7: {
            "nome": "Excalibur",
            "descricao": "Dano massivo em área, limpando escudos e defesas inimigas (ATK x3 em todos)."
        }
    }
},
# =========================120
"bell_cranel": {
    "nome": "Bell Cranel",
    "origem": "DanMachi",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 85, "atk": 45, "matk": 25, "def": 20, "spd": 45, "crt": 25,
    "habilidade": {
        "nome": "Firebolt",
        "descricao": "Magia de execução rápida que causa MATK + 25 sem gastar o turno completamente."
    },
    "evolucoes": {
        5: {
            "nome": "Argonauta",
            "descricao": "Acumula força por 1 turno e libera o dobro de dano no turno seguinte."
        }
    }
},
# =========================121
"ragna_crimson": {
    "nome": "Ragna",
    "origem": "Ragna Crimson",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 95, "atk": 60, "matk": 0, "def": 25, "spd": 30, "crt": 20,
    "habilidade": {
        "nome": "Aura de Prata",
        "descricao": "Causa 30% a mais de dano contra monstros e debilita inimigos mágicos."
    },
    "evolucoes": {
        5: {
            "nome": "Caçador de Dragões",
            "descricao": "Seu ATK aumenta toda vez que recebe dano mágico."
        }
    }
},
# =========================122
"tatsumi_akame": {
    "nome": "Tatsumi",
    "origem": "Akame ga Kill",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "hp": 95, "atk": 40, "matk": 0, "def": 30, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Incursio",
        "descricao": "Invoca a armadura evolutiva, aumentando a DEF em 20 durante o combate."
    },
    "evolucoes": {
        5: {
            "nome": "Evolução Contínua",
            "descricao": "Ganha imunidade a atordoamentos e recebe +10 em ATK/DEF."
        }
    }
},
# =========================123
"yato_god": {
    "nome": "Yato",
    "origem": "Noragami",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 80, "atk": 55, "matk": 20, "def": 15, "spd": 50, "crt": 30,
    "habilidade": {
        "nome": "Zan",
        "descricao": "Corte dimensional que ignora completamente a DEF do oponente."
    },
    "evolucoes": {
        5: {
            "nome": "Deus da Calamidade",
            "descricao": "Aumenta a SPD e o CRT em 20%. Chance de 5% de causar morte instantânea."
        }
    }
},
# =========================124
"alibaba_saluja": {
    "nome": "Alibaba Saluja",
    "origem": "Magi",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 3,
    "max_star": 7,
    "hp": 85, "atk": 45, "matk": 30, "def": 15, "spd": 30, "crt": 15,
    "habilidade": {
        "nome": "Amon",
        "descricao": "Envolve sua espada em fogo, causando ATK + MATK em um inimigo."
    },
    "evolucoes": {
        5: {
            "nome": "Equipamento Djinn",
            "descricao": "Dano em área e garante imunidade a efeitos de queimadura."
        }
    }
},
# =========================125
"kurapika": {
    "nome": "Kurapika",
    "origem": "Hunter x Hunter",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 85, "atk": 50, "matk": 20, "def": 20, "spd": 45, "crt": 25,
    "habilidade": {
        "nome": "Corrente de Julgamento",
        "descricao": "Prende o oponente, causando dano e bloqueando uso de habilidades por 1 turno."
    },
    "evolucoes": {
        5: {
            "nome": "Emperor Time",
            "descricao": "Aumenta todos os atributos em 15%, mas perde 5% do HP a cada turno."
        }
    }
},
# =========================126
"shinobu_kocho": {
    "nome": "Shinobu Kocho",
    "origem": "Demon Slayer",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 4,
    "max_star": 7,
    "hp": 75, "atk": 35, "matk": 0, "def": 15, "spd": 60, "crt": 35,
    "habilidade": {
        "nome": "Dança das Borboletas",
        "descricao": "Aplica um veneno fortíssimo que causa dano passivo (DOT) ignorando defesa por 3 turnos."
    },
    "evolucoes": {
        5: {
            "nome": "Toxina Letal",
            "descricao": "Se Shinobu for derrotada, o inimigo recebe um debuff de envenenamento fatal contínuo."
        }
    }
},
# =========================127
"ninym_ralei": {
    "nome": "Ninym Ralei",
    "origem": "Tensai Ouji",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 25, "matk": 10, "def": 15, "spd": 35, "crt": 10,
    "habilidade": {
        "nome": "Auxílio Tático",
        "descricao": "Concede +15 de ATK ao aliado com o maior ATK do time."
    },
    "evolucoes": {
        3: {
            "nome": "Cobertura Sombra",
            "descricao": "Aumenta a precisão e evasão de todos os aliados."
        },
        5: {
            "nome": "Conselheira Leal",
            "descricao": "Cura 15% de HP do Líder da equipe em cada turno que agir."
        }
    }
},
# =========================128
"hei_darker": {
    "nome": "Hei",
    "origem": "Darker than Black",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 50, "matk": 30, "def": 15, "spd": 50, "crt": 25,
    "habilidade": {
        "nome": "Choque Elétrico",
        "descricao": "Causa dano misto (ATK + MATK) e atordoa alvos que já estejam feridos."
    },
    "evolucoes": {
        5: {
            "nome": "Contratante Black Reaper",
            "descricao": "Ataques críticos paralisam o inimigo garantidamente por 1 turno."
        }
    }
},
# =========================129
"izayoi_sakamaki": {
    "nome": "Izayoi Sakamaki",
    "origem": "Mondaiji",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 105, "atk": 70, "matk": 0, "def": 25, "spd": 45, "crt": 20,
    "habilidade": {
        "nome": "Força Descomunal",
        "descricao": "Destrói barreiras inimigas e causa ATK + 50 ignorando modificadores."
    },
    "evolucoes": {
        7: {
            "nome": "Code Unknown",
            "descricao": "É imune a magia de debuff ou efeitos de morte instantânea."
        }
    }
},
# =========================130
"cc_code": {
    "nome": "C.C.",
    "origem": "Code Geass",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 4,
    "max_star": 7,
    "hp": 100, "atk": 10, "matk": 20, "def": 25, "spd": 25, "crt": 5,
    "habilidade": {
        "nome": "Pacto Geass",
        "descricao": "Restaura HP e confere uma barreira mágica a um aliado escolhido."
    },
    "evolucoes": {
        5: {
            "nome": "Bruxa Imortal",
            "descricao": "Curará passivamente a equipe após o seu HP zerar (Buff contínuo após a queda)."
        }
    }
},
# =========================131
"rika_furude": {
    "nome": "Rika Furude",
    "origem": "Higurashi",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 3,
    "max_star": 7,
    "hp": 65, "atk": 10, "matk": 10, "def": 15, "spd": 20, "crt": 5,
    "habilidade": {
        "nome": "Repetição Temporal",
        "descricao": "Cancela as ações inimigas do último turno se o dano for letal a um aliado."
    },
    "evolucoes": {
        5: {
            "nome": "Vontade de Sobreviver",
            "descricao": "Revive todos os aliados caídos com 10% de HP 1 vez por missão."
        }
    }
},
# =========================132
"nobara_kugisaki": {
    "nome": "Nobara Kugisaki",
    "origem": "Jujutsu Kaisen",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 3,
    "max_star": 7,
    "hp": 75, "atk": 45, "matk": 25, "def": 15, "spd": 30, "crt": 25,
    "habilidade": {
        "nome": "Ressonância",
        "descricao": "Causa dano e marca o inimigo; parte do dano recebido por Nobara reflete no marcado."
    },
    "evolucoes": {
        5: {
            "nome": "Grampo Final",
            "descricao": "Seu golpe final no oponente explode, causando dano em área nos inimigos restantes."
        }
    }
},
# =========================133
"karma_akabane": {
    "nome": "Karma Akabane",
    "origem": "Assassination Classroom",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 35, "matk": 0, "def": 10, "spd": 40, "crt": 25,
    "habilidade": {
        "nome": "Armadilha Oculta",
        "descricao": "Causa dano e diminui a defesa do oponente em 15 por 2 turnos."
    },
    "evolucoes": {
        3: {
            "nome": "Faca Anti-Sensei",
            "descricao": "Aumenta o CRT em 15% contra inimigos de raridade maior."
        },
        5: {
            "nome": "Provocação Sádica",
            "descricao": "Reduz o ataque do alvo após desferir um acerto crítico."
        }
    }
},
# =========================134
"satou_matsuzka": {
    "nome": "Satou",
    "origem": "Happy Sugar Life",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 2,
    "max_star": 7,
    "hp": 110, "atk": 40, "matk": 0, "def": 20, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Amor obssessivo",
        "descricao": "Ataca um inimigo causando ATK+25 e reduz sua DEF em 10 por 2 turnos. Foca 1 único inimigo até o fim do combate"
    },
    "evolucoes": {
        3: {
            "nome": "Protegerei Meu Amor",
            "descricao": "Marca um aliado aleatório, caso ele seja atacado, contra-ataca automaticamente quem o feriu causando ATK+45, se o inimigo estiver com fraqueza, causa um dano crítico garantido."
        },
        5: {
            "nome": "Doce Loucura",
            "descricao": "Entra em frenesi por 3 turno, recebendo +40 SPD, +30 CRT e ignora 30% da DEF do alvo"
        }
    }
},
# =========================135
"tanjirou_kamado": {
    "nome": "Tanjirou Kamado",
    "origem": "Demon Slayer",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 95, "atk": 50, "matk": 10, "def": 20, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Respiração da Água",
        "descricao": "Dano contínuo fluido que diminui a precisão do oponente em 20%."
    },
    "evolucoes": {
        5: {
            "nome": "Hinokami Kagura",
            "descricao": "Transforma os ataques em dano de fogo massivo e aumenta CRT em 15%."
        }
    }
},
# =========================136
"jellal_fernandes": {
    "nome": "Jellal Fernandes",
    "origem": "Fairy Tail",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 5,
    "max_star": 7,
    "hp": 90, "atk": 0, "matk": 70, "def": 25, "spd": 40, "crt": 25,
    "habilidade": {
        "nome": "Magia de Corpo Celeste",
        "descricao": "Evoca meteoros, causando dano mágico em área altíssimo."
    },
    "evolucoes": {
        7: {
            "nome": "Grand Chariot",
            "descricao": "Pode agir primeiro no turno garantidamente e causar MATK + 40."
        }
    }
},
# =========================137
"echidna": {
    "nome": "Echidna",
    "origem": "Re:Zero",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 85, "atk": 0, "matk": 55, "def": 15, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Contrato",
        "descricao": "Buffa imensamente o MATK da equipe, mas drena 5% de HP deles em troca."
    },
    "evolucoes": {
        5: {
            "nome": "Bruxa da Ganância",
            "descricao": "Absorve magias inimigas, convertendo dano em MP/Cura."
        }
    }
},
# =========================138
"wiz_konosuba": {
    "nome": "Wiz",
    "origem": "KonoSuba",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 3,
    "max_star": 7,
    "hp": 90, "atk": 0, "matk": 45, "def": 20, "spd": 20, "crt": 10,
    "habilidade": {
        "nome": "Cursed Crystal Prison",
        "descricao": "Causa dano de Gelo e tem chance de congelar o oponente por 1 turno."
    },
    "evolucoes": {
        5: {
            "nome": "Rei Demônio (Lich)",
            "descricao": "Magias de cura dão dano nela, mas imune a efeitos de morte."
        }
    }
},
# =========================139
"yunyun": {
    "nome": "Yunyun",
    "origem": "KonoSuba",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 0, "matk": 40, "def": 10, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Light of Saber",
        "descricao": "Disparo mágico preciso e forte contra alvo único."
    },
    "evolucoes": {
        3: {
            "nome": "Rivalidade",
            "descricao": "Aumenta o MATK em 20 se houver outro Mago no time."
        },
        5: {
            "nome": "Magia Avançada",
            "descricao": "Seus ataques passam a acertar até 2 oponentes próximos."
        }
    }
},
# =========================140
"altair_creators": {
    "nome": "Altair",
    "origem": "Re:Creators",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 5,
    "max_star": 7,
    "hp": 100, "atk": 20, "matk": 65, "def": 25, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Holopsicon",
        "descricao": "Invoca lâminas que causam dano físico e mágico combinados em área."
    },
    "evolucoes": {
        7: {
            "nome": "Reescrita Causal",
            "descricao": "Muda a propriedade de imunidade de um inimigo, tornando-o fraco a tudo."
        }
    }
},
# =========================141
"mare_bello_fiore": {
    "nome": "Mare Bello Fiore",
    "origem": "Overlord",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 25, "matk": 55, "def": 25, "spd": 30, "crt": 15,
    "habilidade": {
        "nome": "Earth Surge",
        "descricao": "Dano de área massivo (Terremoto) que abaixa a SPD dos inimigos afetados."
    },
    "evolucoes": {
        5: {
            "nome": "Poder da Natureza",
            "descricao": "Curará o aliado com menor HP com as sobras do dano causado."
        }
    }
},
# =========================142
"beatrice": {
    "nome": "Beatrice",
    "origem": "Re:Zero",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 75, "atk": 0, "matk": 60, "def": 15, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Minya",
        "descricao": "Dispara cristais roxos que imobilizam e perfuram escudos mágicos."
    },
    "evolucoes": {
        5: {
            "nome": "Biblioteca Proibida",
            "descricao": "Anula 1 habilidade de área inimiga por batalha."
        }
    }
},
# =========================143
"patchouli_knowledge": {
    "nome": "Patchouli Knowledge",
    "origem": "Touhou Project",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 70, "atk": 0, "matk": 65, "def": 10, "spd": 15, "crt": 15,
    "habilidade": {
        "nome": "Magia Elemental Múltipla",
        "descricao": "Altera seu elemento com base na fraqueza do inimigo para dano crítico constante."
    },
    "evolucoes": {
        5: {
            "nome": "Royal Flare",
            "descricao": "Seu Ultimate causa 30% a mais de dano, mas custa o próximo turno."
        }
    }
},
# =========================144
"sucy_manbavaran": {
    "nome": "Sucy Manbavaran",
    "origem": "Little Witch Academia",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 0, "matk": 35, "def": 15, "spd": 20, "crt": 5,
    "habilidade": {
        "nome": "Poção Venenosa",
        "descricao": "Lança um frasco tóxico que causa dano em área e aplica DOT por 2 turnos."
    },
    "evolucoes": {
        3: {
            "nome": "Gogumelo Perigoso",
            "descricao": "Pode curar ou dar dano em um aliado aleatoriamente, dobrando MATK temporário."
        },
        5: {
            "nome": "Mestre de Poções",
            "descricao": "O envenenamento agora ignora defesas inimigas."
        }
    }
},
# =========================145
"vanir_konosuba": {
    "nome": "Vanir",
    "origem": "KonoSuba",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 85, "atk": 30, "matk": 50, "def": 25, "spd": 30, "crt": 20,
    "habilidade": {
        "nome": "Raio da Morte do Vanir",
        "descricao": "Disparo perfurante poderoso que ignora escudos protetores."
    },
    "evolucoes": {
        5: {
            "nome": "Vidas Extras",
            "descricao": "Possui 1 revive automático com 25% do HP."
        }
    }
},
# =========================146
"hanyuu_furude": {
    "nome": "Furude Hanyuu",
    "origem": "Higurashi",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 3,
    "max_star": 7,
    "hp": 75, "atk": 0, "matk": 30, "def": 15, "spd": 25, "crt": 5,
    "habilidade": {
        "nome": "Presença Divina",
        "descricao": "Purifica status negativos e aumenta a evasão de um aliado."
    },
    "evolucoes": {
        5: {
            "nome": "Deus de Hinamizawa",
            "descricao": "A equipe ganha bônus defensivo se a batalha durar mais de 3 turnos."
        }
    }
},
# =========================147
"noelle_silva": {
    "nome": "Noelle Silva",
    "origem": "Black Clover",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 10, "matk": 45, "def": 20, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Rugido do Dragão do Mar",
        "descricao": "Poderosa rajada de água contra um inimigo único (MATK + 40)."
    },
    "evolucoes": {
        5: {
            "nome": "Armadura da Valquíria",
            "descricao": "Aumenta imensamente a SPD e DEF, passando a usar ataques mistos (ATK+MATK)."
        }
    }
},
# =========================148
"fern_sousou": {
    "nome": "Fern",
    "origem": "Sousou no Frieren",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 3,
    "max_star": 7,
    "hp": 85, "atk": 0, "matk": 50, "def": 25, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Zoltraak (Disparo Rápido)",
        "descricao": "Dispara magia básica numa velocidade absurda, agindo antes do inimigo."
    },
    "evolucoes": {
        5: {
            "nome": "Supressão de Mana",
            "descricao": "Seu primeiro ataque na batalha causa o dobro de dano bônus."
        }
    }
},
# =========================149
"miko_yotsuya": {
    "nome": "Miko Yotsuya",
    "origem": "Mieruko-chan",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "hp": 55, "atk": 0, "matk": 10, "def": 10, "spd": 15, "crt": 0,
    "habilidade": {
        "nome": "Ignorar",
        "descricao": "Causa o inimigo perder a atenção nos aliados, abaixando o Aggro do time."
    },
    "evolucoes": {
        3: {
            "nome": "Visão Espiritual",
            "descricao": "Aumenta a precisão de todos os ataques mágicos aliados."
        },
        5: {
            "nome": "Proteção do Santuário",
            "descricao": "Fornece um escudo de luz que previne 1 hit fatal contra ela."
        }
    }
},
# =========================150
"rem_rezero": {
    "nome": "Rem",
    "origem": "Re:Zero",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 3,
    "max_star": 7,
    "hp": 85, "atk": 45, "matk": 20, "def": 20, "spd": 30, "crt": 15,
    "habilidade": {
        "nome": "Morningstar",
        "descricao": "Gira a sua arma pesada atingindo até 2 inimigos. Pode curar com magia da água."
    },
    "evolucoes": {
        5: {
            "nome": "Forma Oni",
            "descricao": "Aumenta ATK e SPD em 40%, porém perde controle (alvos aleatórios)."
        }
    }
},
# =========================151
"ai_hoshino": {
    "nome": "Ai Hoshino",
    "origem": "Oshi no Ko",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "hp": 50, "atk": 0, "matk": 15, "def": 5, "spd": 25, "crt": 5,
    "habilidade": {
        "nome": "Brilho do Idol",
        "descricao": "Encanta os aliados, subindo ATK e MATK temporariamente."
    },
    "evolucoes": {
        3: {
            "nome": "Olhos Estrelados",
            "descricao": "Causa confusão no oponente com menor DEF."
        },
        5: {
            "nome": "A Mentira é o Amor",
            "descricao": "Transfere os próprios buffs para o DPS e se esconde do Aggro."
        }
    }
},
# =========================152
"chise_hatori": {
    "nome": "Chise Hatori",
    "origem": "Mahoutsukai no Yome",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 0, "matk": 45, "def": 15, "spd": 20, "crt": 5,
    "habilidade": {
        "nome": "Sleigh Beggy",
        "descricao": "Recupera muito HP do time absorvendo a mana ao seu redor."
    },
    "evolucoes": {
        5: {
            "nome": "Braço de Dragão",
            "descricao": "Ao atacar fisicamente, amaldiçoa o oponente e aumenta a própria vida máxima."
        }
    }
},
# =========================153
"miku_nakano": {
    "nome": "Miku Nakano",
    "origem": "Gotoubun no Hanayome",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "hp": 55, "atk": 0, "matk": 5, "def": 10, "spd": 10, "crt": 0,
    "habilidade": {
        "nome": "Apoio Moral",
        "descricao": "Aumenta ligeiramente a defesa de um aliado."
    },
    "evolucoes": {
        3: {
            "nome": "Determinação",
            "descricao": "Cura um aliado em 15%."
        },
        5: {
            "nome": "Esforço Silencioso",
            "descricao": "Buffa toda a equipe com 10% de evasão."
        }
    }
},
# =========================154
"tohru_honda": {
    "nome": "Tohru Honda",
    "origem": "Fruits Basket",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "hp": 60, "atk": 0, "matk": 5, "def": 15, "spd": 15, "crt": 0,
    "habilidade": {
        "nome": "Compaixão",
        "descricao": "Remove todos os debuffs do aliado mais próximo da morte."
    },
    "evolucoes": {
        3: {
            "nome": "Sorriso Gentil",
            "descricao": "Reduz o dano recebido pelo time no próximo turno."
        },
        5: {
            "nome": "Laços Inquebráveis",
            "descricao": "Transforma inimigos atordoados em oponentes pacíficos por mais 1 turno."
        }
    }
},
# =========================155
"nanachi_abyss": {
    "nome": "Nanachi",
    "origem": "Made in Abyss",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 2,
    "max_star": 7,
    "hp": 70, "atk": 15, "matk": 25, "def": 10, "spd": 30, "crt": 10,
    "habilidade": {
        "nome": "Leitura da Força",
        "descricao": "Avisa o próximo ataque do boss, concedendo chance garantida de defesa."
    },
    "evolucoes": {
        3: {
            "nome": "Medicina Subterrânea",
            "descricao": "Cura HP baseada nos itens do cenário e no MATK de Nanachi."
        },
        5: {
            "nome": "Abençoado",
            "descricao": "Imunidade a maldições e efeitos de campo."
        }
    }
},
# =========================156
"yui_yuigahama": {
    "nome": "Yui Yuigahama",
    "origem": "Oregairu",
    "emoji": "🩹",
    "imagem": "",
    "classe": "Suporte",
    "raridade": 1,
    "max_star": 7,
    "hp": 55, "atk": 5, "matk": 0, "def": 10, "spd": 20, "crt": 5,
    "habilidade": {
        "nome": "Energia Positiva",
        "descricao": "Garante +5 de SPD e ATK para todo o time."
    },
    "evolucoes": {
        3: {
            "nome": "Unindo o Clube",
            "descricao": "Aumenta o dano do Líder em 10%."
        },
        5: {
            "nome": "Coração Aberto",
            "descricao": "Cura todos em 10 HP ao fim de cada turno."
        }
    }
},
# =========================157
"kobayashi": {
    "nome": "Kobayashi",
    "origem": "Miss Kobayashi's Dragon Maid",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 1,
    "max_star": 7,
    "hp": 60, "atk": 10, "matk": 0, "def": 10, "spd": 15, "crt": 0,
    "habilidade": {
        "nome": "Programadora",
        "descricao": "Analisa o oponente e aumenta a precisão da equipe em 20%."
    },
    "evolucoes": {
        3: {
            "nome": "Café Quente",
            "descricao": "Restaura 20% de HP para o aliado mais fadigado."
        },
        5: {
            "nome": "Amiga de Dragões",
            "descricao": "Dobro de buff em aliados que não sejam humanos."
        }
    }
},
# =========================158
"albedo_overlord": {
    "nome": "Albedo",
    "origem": "Overlord",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 5,
    "max_star": 7,
    "hp": 140, "atk": 45, "matk": 20, "def": 60, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Parede de Nazarick",
        "descricao": "Absorve todo o dano direcionado ao aliado com menor HP e reduz esse dano em 50%."
    },
    "evolucoes": {
        7: {
            "nome": "Fúria do Súcubo",
            "descricao": "Converte a defesa total em poder de ataque para um golpe massivo em retaliação."
        }
    }
},
# =========================159
"takemichi_hanagaki": {
    "nome": "Takemichi Hanagaki",
    "origem": "Tokyo Revengers",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 1,
    "max_star": 7,
    "hp": 90, "atk": 10, "matk": 0, "def": 15, "spd": 10, "crt": 0,
    "habilidade": {
        "nome": "Saco de Pancadas",
        "descricao": "Puxa todo o Aggro inimigo e se recusa a cair no mesmo turno."
    },
    "evolucoes": {
        3: {
            "nome": "Grito de Determinação",
            "descricao": "Buffa a moral e ATK dos aliados após apanhar."
        },
        5: {
            "nome": "Herói Chorão",
            "descricao": "Enquanto tiver 1 HP, não pode morrer por ataques normais, inspirando o time."
        }
    }
},
# =========================160
"alexander_anderson": {
    "nome": "Alexander Anderson",
    "origem": "Hellsing",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 110, "atk": 50, "matk": 0, "def": 30, "spd": 25, "crt": 15,
    "habilidade": {
        "nome": "Regeneração Monstruosa",
        "descricao": "Cura 15% de seu HP a cada turno e ataca com baionetas."
    },
    "evolucoes": {
        5: {
            "nome": "Prego de Helena",
            "descricao": "Transforma-se, aumentando DEF em 40 e incendiando a área contra monstros."
        }
    }
},
# =========================161
"tengen_uzui": {
    "nome": "Tengen Uzui",
    "origem": "Demon Slayer",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 105, "atk": 45, "matk": 0, "def": 25, "spd": 50, "crt": 20,
    "habilidade": {
        "nome": "Respiração do Som",
        "descricao": "Ataques com explosivos que dão dano em área e absorvem dano passivo."
    },
    "evolucoes": {
        5: {
            "nome": "Partitura Musical",
            "descricao": "Lê os movimentos inimigos. Aumenta esquiva da party toda em 30%."
        }
    }
},
# =========================162
"iron_tager": {
    "nome": "Iron Tager",
    "origem": "BlazBlue",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "hp": 120, "atk": 55, "matk": 0, "def": 40, "spd": 10, "crt": 10,
    "habilidade": {
        "nome": "Gigantic Tager Driver",
        "descricao": "Agarra o oponente causando dano altíssimo e quebrando escudos."
    },
    "evolucoes": {
        5: {
            "nome": "Magnétismo Cyborg",
            "descricao": "Atrai ataques direcionados a magos e atiradores para si mesmo."
        }
    }
},
# =========================163
"aoi_todo": {
    "nome": "Aoi Todo",
    "origem": "Jujutsu Kaisen",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "hp": 90, "atk": 45, "matk": 10, "def": 30, "spd": 30, "crt": 20,
    "habilidade": {
        "nome": "Boogie Woogie",
        "descricao": "Troca de lugar com um aliado ou inimigo, anulando 1 golpe letal."
    },
    "evolucoes": {
        5: {
            "nome": "Amigo de Batalha (Brother)",
            "descricao": "Luta melhor em dupla, bufando a eficácia do DPS aliado em 25%."
        }
    }
},
# =========================164
"alex_louis_armstrong": {
    "nome": "Alex Louis Armstrong",
    "origem": "Fullmetal Alchemist",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 115, "atk": 50, "matk": 20, "def": 45, "spd": 20, "crt": 15,
    "habilidade": {
        "nome": "Alquimia Artística Forte",
        "descricao": "Cria barreiras de terra para a equipe e esmaga o chão causando dano físico."
    },
    "evolucoes": {
        5: {
            "nome": "Orgulho de Família",
            "descricao": "Flexiona os músculos! Reduz o ataque dos inimigos ao redor pelo brilho excessivo."
        }
    }
},
# =========================165
"kenshiro": {
    "nome": "Kenshiro",
    "origem": "Hokuto no Ken",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 120, "atk": 70, "matk": 0, "def": 30, "spd": 40, "crt": 40,
    "habilidade": {
        "nome": "Omae Wa Mou Shindeiru",
        "descricao": "Golpes em pontos vitais. Dano garantido que explode o inimigo internamente 1 turno depois."
    },
    "evolucoes": {
        7: {
            "nome": "Hokuto Shinken Ougi",
            "descricao": "Causa Insta-Kill (Morte Súbita) num inimigo comum ou dano absurdo em Boss."
        }
    }
},
# =========================166
"diane_serpente": {
    "nome": "Diane",
    "origem": "Nanatsu no Taizai",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 4,
    "max_star": 7,
    "hp": 120, "atk": 50, "matk": 20, "def": 35, "spd": 20, "crt": 15,
    "habilidade": {
        "nome": "Gideon (Creation)",
        "descricao": "Ergue o solo como escudos e esmaga os inimigos do outro lado da arena."
    },
    "evolucoes": {
        5: {
            "nome": "Dança de Drole",
            "descricao": "Quanto mais turnos passarem, mais sua DEF e ATK aumentam (até +50%)."
        }
    }
},
# =========================167
"might_guy": {
    "nome": "Might Guy",
    "origem": "Naruto",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 5,
    "max_star": 7,
    "hp": 105, "atk": 65, "matk": 0, "def": 25, "spd": 55, "crt": 25,
    "habilidade": {
        "nome": "Asa do Pavão / Tigre Diurno",
        "descricao": "Combos brutais de Taijutsu causando ATK + 40."
    },
    "evolucoes": {
        7: {
            "nome": "Oitavo Portão: Elefante/Yagai",
            "descricao": "Dano catastrófico que dobra a SPD e ATK. O usuário morre 3 turnos após ativação."
        }
    }
},
# =========================168
"isaac_netero": {
    "nome": "Isaac Netero",
    "origem": "Hunter x Hunter",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 5,
    "max_star": 7,
    "hp": 100, "atk": 60, "matk": 0, "def": 30, "spd": 70, "crt": 30,
    "habilidade": {
        "nome": "Guanyin Bodhisattva de 100 Tipos",
        "descricao": "Um ataque impossível de esquivar (100% Hit Rate) com ATK + 50."
    },
    "evolucoes": {
        7: {
            "nome": "Rosa Miniatura (Zero Mão)",
            "descricao": "Em caso de morte, causa um dano explosivo massivo destruindo o inimigo junto."
        }
    }
},
# =========================169
"kuwabara_kazuma": {
    "nome": "Kazuma Kuwabara",
    "origem": "Yu Yu Hakusho",
    "emoji": "🛡️",
    "imagem": "",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "hp": 95, "atk": 45, "matk": 10, "def": 25, "spd": 20, "crt": 15,
    "habilidade": {
        "nome": "Rei Ken (Espada Espiritual)",
        "descricao": "Ataque com longo alcance que também permite defender golpes para seus amigos."
    },
    "evolucoes": {
        5: {
            "nome": "Jigen Tou (Espada Dimensional)",
            "descricao": "Ganha o poder de cortar qualquer escudo, atravessando defesas mágicas inimigas."
        }
    }
},
# =========================170
"zero_two": {
    "nome": "Zero Two",
    "origem": "Darling in the FranXX",
    "emoji": "👊",
    "imagem": "",
    "classe": "Atacante",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 60, "matk": 0, "def": 20, "spd": 40, "crt": 30,
    "habilidade": {
        "nome": "Sangue de Klaxosaur",
        "descricao": "Ganha +10 de Ataque a cada aliado morto em batalha."
    },
    "evolucoes": {
        5: {
            "nome": "Pilotagem Estrelizia",
            "descricao": "Se houver um Suporte na equipe, dobra o dano nos primeiros 2 turnos."
        }
    }
},
# =========================171
"izaya_orihara": {
    "nome": "Izaya Orihara",
    "origem": "Durarara!!",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 3,
    "max_star": 7,
    "hp": 70, "atk": 25, "matk": 0, "def": 15, "spd": 45, "crt": 20,
    "habilidade": {
        "nome": "Manipulação",
        "descricao": "Faz com que dois inimigos se ataquem e ignora todo Aggro de si mesmo."
    },
    "evolucoes": {
        5: {
            "nome": "Observador Humano",
            "descricao": "Aumenta a precisão e crítico de toda a equipe permanentemente."
        }
    }
},
# =========================172
"norman_tpn": {
    "nome": "Norman",
    "origem": "The Promised Neverland",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 2,
    "max_star": 7,
    "hp": 65, "atk": 15, "matk": 0, "def": 15, "spd": 25, "crt": 10,
    "habilidade": {
        "nome": "Estratégia Superior",
        "descricao": "Prevê a ação inimiga, diminuindo o dano recebido no próximo turno em 30%."
    },
    "evolucoes": {
        3: {
            "nome": "Análise Rápida",
            "descricao": "Anula 1 debuff em aliados."
        },
        5: {
            "nome": "William Minerva",
            "descricao": "Comanda as tropas atiradoras para causar +20% de dano."
        }
    }
},
# =========================173
"sora_ngnl": {
    "nome": "Sora",
    "origem": "No Game No Life",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 75, "atk": 10, "matk": 20, "def": 20, "spd": 35, "crt": 30,
    "habilidade": {
        "nome": "Plano Perfeito",
        "descricao": "Manipula o turno: se aliado errar, tem chance de repetir o ataque."
    },
    "evolucoes": {
        5: {
            "nome": "Kuuhaku (Junto a Shiro)",
            "descricao": "Sinergia: Se Shiro estiver viva, todos os golpes do time nunca erram (Precisão 100%)."
        }
    }
},
# =========================174
"shiro_ngnl": {
    "nome": "Shiro",
    "origem": "No Game No Life",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 70, "atk": 5, "matk": 30, "def": 15, "spd": 40, "crt": 35,
    "habilidade": {
        "nome": "Cálculo Lógico",
        "descricao": "Prevê perfeitamente as trajetórias inimigas. Aumenta Evasão do time em 40%."
    },
    "evolucoes": {
        5: {
            "nome": "Kuuhaku (Junto a Sora)",
            "descricao": "Sinergia: Se Sora estiver vivo, os acertos críticos do time sobem 30%."
        }
    }
},
# =========================175
"reinhard_von_lohengramm": {
    "nome": "Reinhard von Lohengramm",
    "origem": "Legend of the Galactic Heroes",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 5,
    "max_star": 7,
    "hp": 95, "atk": 30, "matk": 40, "def": 30, "spd": 35, "crt": 15,
    "habilidade": {
        "nome": "Comando de Frota Imperial",
        "descricao": "Chama bombardeios do espaço. Dano em área em toda a equipe inimiga."
    },
    "evolucoes": {
        7: {
            "nome": "Gênio Militar Invencível",
            "descricao": "A equipe ganha bônus de ATK e DEF multiplicados pelo número de aliados vivos."
        }
    }
},
# =========================176
"makishima_shogo": {
    "nome": "Makishima Shogo",
    "origem": "Psycho-Pass",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 3,
    "max_star": 7,
    "hp": 75, "atk": 40, "matk": 0, "def": 15, "spd": 35, "crt": 20,
    "habilidade": {
        "nome": "Criminoso Assintomático",
        "descricao": "Não pode ser alvejado por habilidades automáticas de inimigos."
    },
    "evolucoes": {
        5: {
            "nome": "Mente Maquiavélica",
            "descricao": "Causa status de Sangramento e diminui a precisão dos inimigos em 20%."
        }
    }
},
# =========================177
"william_moriarty": {
    "nome": "William James Moriarty",
    "origem": "Moriarty the Patriot",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 80, "atk": 25, "matk": 30, "def": 20, "spd": 35, "crt": 25,
    "habilidade": {
        "nome": "Consultor Criminal",
        "descricao": "Aplica uma marca no líder inimigo; todo dano da equipe contra o líder aumenta 40%."
    },
    "evolucoes": {
        5: {
            "nome": "Lorde do Crime",
            "descricao": "Concede bônus contínuo de roubo de vida a toda a equipe de assassinos."
        }
    }
},
# =========================178
"osamu_dazai": {
    "nome": "Osamu Dazai",
    "origem": "Bungo Stray Dogs",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 85, "atk": 35, "matk": 0, "def": 20, "spd": 40, "crt": 20,
    "habilidade": {
        "nome": "Indigno de Ser Humano",
        "descricao": "Anula 100% de efeitos de habilidades mágicas e buffs dos oponentes."
    },
    "evolucoes": {
        5: {
            "nome": "Gênio da Agência",
            "descricao": "No limite da morte, ativa um plano de contingência curando o DPS do time ao máximo."
        }
    }
},
# =========================179
"houtarou_oreki": {
    "nome": "Houtarou Oreki",
    "origem": "Hyouka",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 1,
    "max_star": 7,
    "hp": 60, "atk": 5, "matk": 5, "def": 10, "spd": 10, "crt": 10,
    "habilidade": {
        "nome": "Conservação de Energia",
        "descricao": "Ele não faz nada. Mas a equipe gasta menos mana/MP enquanto ele viver."
    },
    "evolucoes": {
        3: {
            "nome": "Dedução Lógica",
            "descricao": "Revela a fraqueza oculta do inimigo."
        },
        5: {
            "nome": "Eu Não Faço O Que Não Preciso",
            "descricao": "Anula turnos inimigos que seriam ataques desnecessários."
        }
    }
},
# =========================180
"king_nanatsu": {
    "nome": "King",
    "origem": "Nanatsu no Taizai",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 4,
    "max_star": 7,
    "hp": 80, "atk": 00, "matk": 60, "def": 20, "spd": 35, "crt": 25,
    "habilidade": {
        "nome": "Chastiefol: Bumblebee",
        "descricao": "Lança uma chuva de lanças mágicas causando dano a alvos aleatórios."
    },
    "evolucoes": {
        5: {
            "nome": "Rei das Fadas",
            "descricao": "Pode usar Chastiefol: Girassol para curar a equipe após causar dano mágico."
        }
    }
},
# =========================181
"ayanokoji_kiyotaka": {
    "nome": "Ayanokoji Kiyotaka",
    "origem": "Classroom of the Elite",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "hp": 90, "atk": 40, "matk": 0, "def": 30, "spd": 45, "crt": 10,
    "habilidade": {
        "nome": "Obra-Prima da Sala Branca",
        "descricao": "Manipula o campo, reduzindo em 30% todas as qualidades dos oponentes em segredo."
    },
    "evolucoes": {
        5: {
            "nome": "Pessoas são Ferramentas",
            "descricao": "Sacrifica um pouco do HP de um aliado menor para maximizar o ATK da equipe principal."
        }
    }
},
# =========================182
"mami_tomoe": {
    "nome": "Mami Tomoe",
    "origem": "Madoka Magica",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 4,
    "max_star": 7,
    "hp": 75, "atk": 0, "matk": 60, "def": 15, "spd": 35, "crt": 30,
    "habilidade": {
        "nome": "Tiro de Mosquete Mágico",
        "descricao": "Invoca dezenas de armas de fogo atirando simultaneamente em todos os inimigos."
    },
    "evolucoes": {
        5: {
            "nome": "Tiro Finale",
            "descricao": "Dano concentrado num único oponente, ignora debuffs de proteção e imobiliza o alvo."
        }
    }
},
# =========================183
"chelsea_akame": {
    "nome": "Chelsea",
    "origem": "Akame ga Kill",
    "emoji": "⚔️",
    "imagem": "",
    "classe": "Assassino",
    "raridade": 3,
    "max_star": 7,
    "hp": 70, "atk": 45, "matk": 20, "def": 15, "spd": 45, "crt": 35,
    "habilidade": {
        "nome": "Gaia Foundation (Transformação)",
        "descricao": "Fica camuflada dos inimigos (ignora dano no primeiro turno) e ataca na retaguarda."
    },
    "evolucoes": {
        5: {
            "nome": "Golpe de Agulha Assassino",
            "descricao": "Perfura um ponto vital, causando bônus massivo de Crítico."
        }
    }
},
# =========================184
"train_heartnet": {
    "nome": "Train Heartnet",
    "origem": "Black Cat",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 4,
    "max_star": 7,
    "hp": 85, "atk": 55, "matk": 0, "def": 20, "spd": 50, "crt": 35,
    "habilidade": {
        "nome": "Hades",
        "descricao": "Dispara balas especiais que quebram defesas e diminuem a SPD do alvo."
    },
    "evolucoes": {
        5: {
            "nome": "Black Cat",
            "descricao": "O 13º Membro de Chronos. Ganha precisão garantida e ataques causam Insta-Kill em minions."
        }
    }
},
# =========================185
"the_end": {
    "nome": "The End",
    "origem": "Metal Gear Solid 3",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 5,
    "max_star": 7,
    "hp": 80, "atk": 65, "matk": 0, "def": 15, "spd": 30, "crt": 50,
    "habilidade": {
        "nome": "Camuflagem e Espera",
        "descricao": "Fica invisível por 1 turno e seu tiro subsequente causa Dano x 3."
    },
    "evolucoes": {
        7: {
            "nome": "Velho Sniper da Floresta",
            "descricao": "Cura usando luz do sol (Fotossíntese) e reduz permanentemente o HP máximo do oponente."
        }
    }
},
# =========================186
"sinbad": {
    "nome": "Sinbad",
    "origem": "Magi",
    "emoji": "✨",
    "imagem": "",
    "classe": "Mago",
    "raridade": 5,
    "max_star": 7,
    "hp": 120, "atk": 50, "matk": 60, "def": 25, "spd": 40, "crt": 35,
    "habilidade": {
        "nome": "Baal, Valefor e Focalor",
        "descricao": "Efeito aleatório: Baal causa 300% de MATK e aplica queimadura, causando 30 MATK por 3 turnos. Valefor congela todos os inimigos por 2 turnos. Focalor diminui. SPD inimiga geral em 50% e aplica Fraqueza, fazendo com que inimigos sofram 70%+ de dano."
    },
    "evolucoes": {
        5: {
            "nome": "Zepar, Vepar, Furfur e Crocell",
            "descricao": "Sinbad usa os quatro Djinns simultaneamente, causando uma tempestade elemental. Causa 500% MATK em área, aplica Burn causando 40MATK por 3 turnos, congela todos os inimigos por 3 turnos, reduz a precisão inimiga fazendo com que eles tenham 25% chance de errar golpes e diminui a DEF inimiga em 50%."
        }
    }
},
# =========================187
"guido_mista": {
    "nome": "Guido Mista",
    "origem": "JoJo's Bizarre Adventure",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 3,
    "max_star": 7,
    "hp": 75, "atk": 45, "matk": 20, "def": 15, "spd": 35, "crt": 30,
    "habilidade": {
        "nome": "Sex Pistols",
        "descricao": "Controla a bala no ar para acertar oponentes escondidos."
    },
    "evolucoes": {
        5: {
            "nome": "Evitar o Número 4",
            "descricao": "Redireciona balas atiradas de volta para si mesmo, sacrificando HP por Crítico Garantido em até 6 alvos."
        }
    }
},
# =========================188
"tanya_degurechaff": {
    "nome": "Tanya Degurechaff",
    "origem": "Youjo Senki",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 4,
    "max_star": 7,
    "hp": 80, "atk": 40, "matk": 50, "def": 20, "spd": 40, "crt": 25,
    "habilidade": {
        "nome": "Elenium Type 95",
        "descricao": "Rajada mágica explosiva (Dano Físico + Dano Mágico) perfurando a frente inimiga."
    },
    "evolucoes": {
        5: {
            "nome": "Orar ao Ser X",
            "descricao": "Aumenta o MATK para níveis letais, limpando o campo com bombardeio de feitiços de guerra."
        }
    }
},
# =========================189
"najenda": {
    "nome": "Najenda",
    "origem": "Akame ga Kill",
    "emoji": "📚",
    "imagem": "",
    "classe": "Líder",
    "raridade": 3,
    "max_star": 7,
    "hp": 85, "atk": 35, "matk": 0, "def": 25, "spd": 30, "crt": 15,
    "habilidade": {
        "nome": "Comandante da Night Raid",
        "descricao": "Melhora as estatísticas de ataque de todos os Assassinos e Atacantes do time."
    },
    "evolucoes": {
        5: {
            "nome": "Coração de Chefe",
            "descricao": "Concede bônus de resistência quando o HP do time cai abaixo de 30%."
        }
    }
},
# =========================190
"yoko_littner": {
    "nome": "Yoko Littner",
    "origem": "Gurren Lagann",
    "emoji": "🏹",
    "imagem": "",
    "classe": "Atirador",
    "raridade": 3,
    "max_star": 7,
    "hp": 80, "atk": 50, "matk": 0, "def": 15, "spd": 35, "crt": 30,
    "habilidade": {
        "nome": "Rifle de Franco-Atirador Subterrâneo",
        "descricao": "Dano focado de alta potência. Destrói escudos baseados em defesa."
    },
    "evolucoes": {
        5: {
            "nome": "Precisão Escaldante",
            "descricao": "Seu acerto crítico garante uma quebra de armadura permanente no alvo (DEF -20)."
        }
    }
},
# =========================191
"toph": {
    "nome": "Toph",
    "origem": "Avatar",
    "emoji": "🪨",
    "classe": "Tank",
    "raridade": 3,
    "max_star": 7,
    "imagem": "",

    "hp": 260,
    "atk": 35,
    "matk": 0,
    "def": 65,
    "spd": 20,
    "crt": 5,

    "habilidade": {
        "nome": "Muralha de Pedra",
        "descricao": "Aumenta DEF."
    },

    "evolucoes": {
        5: {
            "nome": "Metal Dobragem",
            "descricao": "Provoca todos os inimigos."
        }
    }
},
# =========================192
"goblin_slayer": {
    "nome": "Goblin Slayer",
    "origem": "Goblin Slayer",
    "emoji": "🛡️",
    "classe": "Tank",
    "raridade": 2,
    "max_star": 7,
    "imagem": "",

    "hp": 220,
    "atk": 45,
    "matk": 0,
    "def": 55,
    "spd": 25,
    "crt": 5,

    "habilidade": {
        "nome": "Caçador de Goblins",
        "descricao": "Provoca o inimigo."
    },

    "evolucoes": {
        3: {
            "nome": "Armadilha Preparada",
            "descricao": "Reduz SPD inimiga."
        },
        5: {
            "nome": "Veterano Experiente",
            "descricao": "Aumenta DEF drasticamente."
        }
    }
},
# =========================193
"yugi_muto": {
    "nome": "Yugi Muto",
    "origem": "Yu-Gi-Oh!",
    "emoji": "🎴",
    "classe": "Líder",
    "raridade": 4,
    "max_star": 7,
    "imagem": "",

    "hp": 190,
    "atk": 45,
    "matk": 45,
    "def": 35,
    "spd": 30,
    "crt": 15,

    "habilidade": {
        "nome": "Coração das Cartas",
        "descricao": "Buffa toda a equipe."
    },

    "evolucoes": {
        5: {
            "nome": "Exodia",
            "descricao": "Ataque devastador."
        }
    }
},
# =========================194
"joker": {
    "nome": "Joker",
    "origem": "Persona",
    "emoji": "🎭",
    "classe": "Assassino",
    "raridade": 5,
    "max_star": 7,
    "imagem": "",

    "hp": 180,
    "atk": 90,
    "matk": 40,
    "def": 20,
    "spd": 60,
    "crt": 35,

    "habilidade": {
        "nome": "Arsène",
        "descricao": "Grande dano crítico."
    },

    "evolucoes": {
        7: {
            "nome": "All-Out Attack",
            "descricao": "Atinge todos os inimigos."
        }
    }
},
# =========================195
"gabimaru": {
    "nome": "Gabimaru",
    "origem": "Hell's Paradise",
    "emoji": "🔥",
    "classe": "Assassino",
    "raridade": 3,
    "max_star": 7,
    "imagem": "",

    "hp": 170,
    "atk": 70,
    "matk": 15,
    "def": 20,
    "spd": 50,
    "crt": 20,

    "habilidade": {
        "nome": "Ninjutsu de Fogo",
        "descricao": "Dano físico e mágico."
    },

    "evolucoes": {
        5: {
            "nome": "Gabimaru do Vazio",
            "descricao": "Recebe bônus massivo de SPD."
        }
    }
},
# =========================196
"mumen_rider": {
    "nome": "Mumen Rider",
    "origem": "One Punch Man",
    "emoji": "🩹",
    "classe": "Assassino",
    "raridade": 1,
    "max_star": 7,
    "imagem": "",

    "hp": 60,
    "atk": 15,
    "matk": 0,
    "def": 10,
    "spd": 20,
    "crt": 10,

    "habilidade": {
        "nome": "Justice Bike",
        "descricao": "Mumen avança para proteger um aliado. Escolhe um aliado com o menor HP, tirando si mesmo. Recebe todo dano recebido por ele por 2 turnos, aumentando a DEF em 30%."
    },

    "evolucoes": {
        3: {
            "nome": "Justice Crash",
            "descricao": "(Puxa o agro inimigo, reduzindo o ATK em 20%, a precisão inimiga em 30%."
        },
        5: {
            "nome": "Justice Flash",
            "descricao": "Cura todos os aliados em 20%, recebe 25% de SPD por 3 turnos e fica imune a Debuffs, puxa o agro para si."
        }
    }
},
    # =========================197
    "sokka": {
        "nome": "Sokka",
        "origem": "Avatar: A Lenda de Aang",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 1,
        "max_star": 7,
        "hp": 95,
        "atk": 25,
        "matk": 0,
        "def": 18,
        "spd": 15,
        "crt": 5,
        "habilidade": {
            "nome": "Plano do Bumerangue",
            "descricao": "Arremessa seu bumerangue confiável. Causa 120% de dano físico e retorna após 1 turno, causando o dobro do dano pelas costas do inimigo."
        },
        "evolucoes": {
            3: {
                "nome": "Espada de Espaço",
                "descricao": "Sokka empunha sua espada feita de meteorito. Seus ataques ganham +20 de penetração de armadura e reduzem a DEF do alvo em 15%."
            },
            5: {
                "nome": "Líder Cético",
                "descricao": "Sua descrença em magia o torna imune a debuffs mágicos. Concede +15% de precisão e velocidade a toda a equipe."
            }
        }
    },

    # =========================198
    "leorio": {
        "nome": "Leorio",
        "origem": "Hunter x Hunter",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 110,
        "atk": 15,
        "matk": 10,
        "def": 20,
        "spd": 12,
        "crt": 5,
        "habilidade": {
            "nome": "Soco de Impacto Distante",
            "descricao": "Leorio soca o chão, projetando seu soco através de um portal sob o inimigo. Causa 150% de ATK e ignora a linha de frente inimiga."
        },
        "evolucoes": {
            3: {
                "nome": "Maleta de Emergência",
                "descricao": "Cura um aliado ferido em 250% do seu poder mágico e remove efeitos de sangramento e veneno."
            },
            5: {
                "nome": "Determinação Médica",
                "descricao": "Leorio se recusa a ver seus amigos morrerem. Aumenta a eficácia de todas as curas da equipe em 25%."
            }
        }
    },

    # =========================199
    "magna_swing": {
        "nome": "Magna Swing",
        "origem": "Black Clover",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 1,
        "max_star": 7,
        "hp": 90,
        "atk": 35,
        "matk": 20,
        "def": 12,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Besta de Fogo Flamejante",
            "descricao": "Dispara bolas de fogo explosivas usando seu taco de beisebol de fogo. Aplica Queimadura por 3 turnos, causando dano por turno."
        },
        "evolucoes": {
            3: {
                "nome": "Manto de Fogo Dinâmico",
                "descricao": "Ativa um manto que aumenta seu ATK em 20% e queima inimigos que o atacarem corpo a corpo."
            },
            5: {
                "nome": "Soul Chain Death Match",
                "descricao": "Conecta sua alma à do inimigo com maior poder. Divide o HP de ambos igualmente e remove todos os buffs do alvo."
            }
        }
    },

    # =========================200
    "sein": {
        "nome": "Sein",
        "origem": "Frieren: Beyond Journey's End",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 105,
        "atk": 10,
        "matk": 35,
        "def": 15,
        "spd": 14,
        "crt": 5,
        "habilidade": {
            "nome": "Sopro de Alívio",
            "descricao": "Usa magia de cura avançada para restaurar 30% do HP do aliado mais ferido e remover qualquer atordoamento (Stun)."
        },
        "evolucoes": {
            3: {
                "nome": "Bênção da Deusa",
                "descricao": "Concede um escudo sagrado a um aliado equivalente a 20% de sua vida máxima, aumentando sua DEF em 30%."
            },
            5: {
                "nome": "Despertar do Vício",
                "descricao": "Sua paixão por jogos e fumo o acalma sob pressão. Cura todo o grupo passivamente em 5% do HP máximo no início de cada rodada."
            }
        }
    },

    # =========================201
    "power": {
        "nome": "Power",
        "origem": "Chainsaw Man",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 1,
        "max_star": 7,
        "hp": 95,
        "atk": 38,
        "matk": 0,
        "def": 14,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Foice de Sangue",
            "descricao": "Power molda seu próprio sangue em uma foice letal. Causa 140% de dano físico e aplica Sangramento pesado por 3 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Martelo de Sangue Gigante",
                "descricao": "Molda um martelo colossal que esmaga o alvo, ignorando escudos protetores e aplicando atordoamento por 1 turno."
            },
            5: {
                "nome": "Rainha do Sangue",
                "descricao": "Sua conexão com o sangue alheio a cura em 35% de todo o dano causado por sangramento ativo na arena."
            }
        }
    },

    # =========================202
    "lotte_yanson": {
        "nome": "Lotte Yanson",
        "origem": "Little Witch Academia",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 100,
        "atk": 8,
        "matk": 32,
        "def": 18,
        "spd": 11,
        "crt": 5,
        "habilidade": {
            "nome": "Canção das Fadas",
            "descricao": "Sintoniza com os espíritos locais, reduzindo a velocidade dos inimigos em 15% e aumentando a resistência mágica do grupo."
        },
        "evolucoes": {
            3: {
                "nome": "Sussurro Espiritual",
                "descricao": "Cura todos os aliados com uma névoa mágica que recupera 15% do HP máximo deles ao longo de 2 turnos."
            },
            5: {
                "nome": "Simpatia das Lanternas",
                "descricao": "Invoca lanternas mágicas que concedem imunidade a silenciamento e aumentam a chance crítica do líder em 20%."
            }
        }
    },

    # =========================203
    "lubbock": {
        "nome": "Lubbock",
        "origem": "Akame ga Kill",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 2,
        "max_star": 7,
        "hp": 105,
        "atk": 42,
        "matk": 0,
        "def": 16,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Crosstail: Fios Cortantes",
            "descricao": "Espalha fios imperceptíveis que prendem até 3 inimigos. Causa 130% de ATK e reduz a SPD deles em 30% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Armadura de Fios",
                "descricao": "Usa fios para criar uma blindagem oculta. Ganha +35% de DEF e 20% de esquiva por 3 rodadas."
            },
            5: {
                "nome": "Lança Quebra-Coração",
                "descricao": "Reúne os fios para perfurar diretamente o peito do inimigo. Ignora completamente a defesa e causa dano triplo em acertos críticos."
            }
        }
    },

    # =========================204
    "schele": {
        "nome": "Schele",
        "origem": "Akame ga Kill",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 2,
        "max_star": 7,
        "hp": 95,
        "atk": 46,
        "def": 12,
        "matk": 0,
        "spd": 24,
        "crt": 20,
        "habilidade": {
            "nome": "Extase: Corte do Julgamento",
            "descricao": "Usa sua tesoura gigante para fatiar o inimigo. Causa 180% de ATK e possui 25% de chance de executar inimigos abaixo de 30% de HP."
        },
        "evolucoes": {
            3: {
                "nome": "Clarão Ofuscante",
                "descricao": "A tesoura reflete uma luz cegante. Reduz a precisão (accuracy) de todos os inimigos em 40% por 2 turnos."
            },
            5: {
                "nome": "Sacrifício Silencioso",
                "descricao": "Ao sofrer dano fatal, concede imunidade absoluta e um turno extra imediato para o aliado com maior ATK da sua equipe."
            }
        }
    },

    # =========================205
    "katara": {
        "nome": "Katara",
        "origem": "Avatar: A Lenda de Aang",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 115,
        "atk": 12,
        "matk": 40,
        "def": 22,
        "spd": 16,
        "crt": 5,
        "habilidade": {
            "nome": "Fluxo Curativo de Lugnica",
            "descricao": "Usa água pura para curar a equipe. Cura 15% do HP máximo de todos e remove queimaduras e sangramentos."
        },
        "evolucoes": {
            3: {
                "nome": "Chicote de Gelo",
                "descricao": "Arremessa um chicote de água congelada que causa 120% de dano mágico e reduz a velocidade do alvo à metade."
            },
            5: {
                "nome": "Dobra de Sangue Lunar",
                "descricao": "Sob a lua cheia, Katara assume o controle do inimigo com maior ATK, forçando-o a atacar seus próprios aliados por 1 turno."
            }
        }
    },

    # =========================206
    "beta": {
        "nome": "Beta",
        "origem": "Eminence in Shadow",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 110,
        "atk": 20,
        "matk": 38,
        "def": 20,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Escrita Tática de Combate",
            "descricao": "Anota as fraquezas dos inimigos. Concede +20% de chance crítica e +15% de ATK/MATK para o líder do grupo por 3 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Manto de Slime Protetor",
                "descricao": "Cria barreiras de slime para a equipe que absorvem dano equivalente a 15% do HP máximo por 2 turnos."
            },
            5: {
                "nome": "Adoração do Sombra",
                "descricao": "Sua fé cega em Shadow a inspira. Cura o grupo inteiro em 10% de HP sempre que um aliado desferir um golpe crítico."
            }
        }
    },

    # =========================207
    "gamma": {
        "nome": "Gamma",
        "origem": "Eminence in Shadow",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 2,
        "max_star": 7,
        "hp": 120,
        "atk": 30,
        "matk": 25,
        "def": 24,
        "spd": 8,
        "crt": 5,
        "habilidade": {
            "nome": "Desastre Desajeitado",
            "descricao": "Gamma tropeça e deixa sua espada cair acidentalmente sobre o inimigo. Causa 250% de ATK físico, mas há 10% de chance de ela atordoar a si mesma."
        },
        "evolucoes": {
            3: {
                "nome": "Monopólio da Mitsugoshi",
                "descricao": "Sua genialidade comercial rende frutos. Aumenta os drops e o ouro recebido em caçadas em 30% passivamente."
            },
            5: {
                "nome": "Fúria do Erro Calculado",
                "descricao": "Ao cometer um erro ou errar um ataque, Gamma entra em frenesi. Dobra sua velocidade e seu ataque por 2 turnos."
            }
        }
    },

    # =========================208
    "sayaka_miki": {
        "nome": "Sayaka Miki",
        "origem": "Madoka Magica",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 140,
        "atk": 25,
        "matk": 15,
        "def": 35,
        "spd": 16,
        "crt": 5,
        "habilidade": {
            "nome": "Regeneração Acelerada",
            "descricao": "Sayaka foca sua magia para ignorar a dor. Atrai o perigo (provocação) e recupera 15% de seu HP máximo ao final de cada turno por 3 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Chuva de Lâminas",
                "descricao": "Invoca e arremessa múltiplas espadas. Causa 130% de ATK em área e reduz o ATK dos atingidos em 20%."
            },
            5: {
                "nome": "Oktavia von Seckendorff",
                "descricao": "Seu desespero a transforma. Ao chegar a 0 HP, revive uma vez com 100% dos atributos ampliados por 3 turnos antes de cair em definitivo."
            }
        }
    },

    # =========================209
    "sakura_haruno": {
        "nome": "Sakura Haruno",
        "origem": "Naruto",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 30,
        "matk": 20,
        "def": 20,
        "spd": 15,
        "crt": 10,
        "habilidade": {
            "nome": "Palma Mística",
            "descricao": "Usa chakra médico concentrado para fechar as feridas de um aliado. Cura 40% do HP do alvo e cancela efeitos de sangramento."
        },
        "evolucoes": {
            3: {
                "nome": "Impacto da Flor de Cerejeira",
                "descricao": "Concentra chakra no punho e esmaga o solo. Causa 150% de ATK físico a todos os inimigos e atordoa o alvo principal."
            },
            5: {
                "nome": "Selo de Força de uma Centena",
                "descricao": "Ativa o Byakugou. Fica completamente imune a debuffs e recupera 10% de HP máximo no início de cada rodada."
            }
        }
    },

    # =========================210
    "ram_rezero": {
        "nome": "Ram",
        "origem": "Re:Zero",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 105,
        "atk": 15,
        "matk": 38,
        "def": 18,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Magia de Vento: El Fula",
            "descricao": "Conjura rajadas de vento cortantes que empurram os inimigos. Causa 120% de MATK e reduz a SPD do alvo em 25% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Sarcasmo Afiado",
                "descricao": "Suas palavras ácidas desestabilizam o inimigo. Reduz o ataque físico e mágico do alvo em 30% por 3 turnos."
            },
            5: {
                "nome": "Benção do Vento Divino",
                "descricao": "Amplifica o elemento vento. Aliados recebem +30% de velocidade de ação e o herói principal recebe um bônus de 20% de evasão."
            }
        }
    },

    # =========================211
    "bulat": {
        "nome": "Bulat",
        "origem": "Akame ga Kill",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 160,
        "atk": 45,
        "matk": 0,
        "def": 55,
        "spd": 14,
        "crt": 5,
        "habilidade": {
            "nome": "Incursio: Defesa Blindada",
            "descricao": "Veste a armadura lendária. Concede provocação total aos inimigos, aumenta sua DEF em 50% e fica imune a atordoamento por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Lança Imperial Neuntote",
                "descricao": "Desfere um golpe avassalador que quebra a barreira inimiga. Causa 220% de ATK e ignora 40% da defesa física."
            }
        }
    },

    # =========================212
    "leone": {
        "nome": "Leone",
        "origem": "Akame ga Kill",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 150,
        "atk": 50,
        "matk": 0,
        "def": 45,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Lionelle: Forma Bestial",
            "descricao": "Ativa seu Teigu de fusão animal. Ganha +30% de HP máximo, +25% de ATK e passa a regenerar 8% de HP por turno durante a batalha."
        },
        "evolucoes": {
            5: {
                "nome": "Regeneração Feral de Leone",
                "descricao": "Sua vitalidade lupina impede a morte. Cura 50% do HP máximo de forma instantânea quando o HP cai abaixo de 20% (1 vez por luta)."
            }
        }
    },

    # =========================213
    "shura_kirigakure": {
        "nome": "Shura Kirigakure",
        "origem": "Ao no Exorcist",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 115,
        "atk": 55,
        "matk": 25,
        "def": 25,
        "spd": 20,
        "crt": 12,
        "habilidade": {
            "nome": "Lâmina da Serpente de Presas",
            "descricao": "Saca sua espada demoníaca e ataca com golpes ágeis e venenosos. Causa 150% de ATK e aplica Veneno Mágico por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Barreira das Oito Serpentes",
                "descricao": "Cria um escudo espiritual de serpentes que absorve dano mágico e contra-ataca atacantes com 100% de MATK."
            }
        }
    },

    # =========================214
    "rukia_kuchiki": {
        "nome": "Rukia Kuchiki",
        "origem": "Bleach",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 100,
        "atk": 15,
        "matk": 58,
        "def": 20,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Sode no Shirayuki: Primeira Dança",
            "descricao": "Cria um círculo de gelo que congela a terra. Causa 140% de MATK a todos os inimigos e reduz a velocidade deles em 30%."
        },
        "evolucoes": {
            5: {
                "nome": "Hakka no Togame: Bankai",
                "descricao": "Libera seu frio absoluto. Congela todos os inimigos por 1 turno completo e ignora escudos mágicos ativos."
            }
        }
    },

    # =========================215
    "aki_hayakawa": {
        "nome": "Aki Hayakawa",
        "origem": "Chainsaw Man",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 52,
        "matk": 20,
        "def": 18,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Contrato do Demônio Fox: Kon!",
            "descricao": "Faz o sinal de 'Kon' e invoca a cabeça gigante do demônio raposa. Devora o inimigo causando 250% de ATK que ignora defesa física."
        },
        "evolucoes": {
            5: {
                "nome": "Contrato com o Demônio do Futuro",
                "descricao": "Seus olhos enxergam milissegundos no futuro. Concede +30% de esquiva e garante que seus ataques nunca errem."
            }
        }
    },

    # =========================216
    "delta": {
        "nome": "Delta",
        "origem": "Eminence in Shadow",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 58,
        "matk": 0,
        "def": 15,
        "spd": 35,
        "crt": 20,
        "habilidade": {
            "nome": "Caçada Selvagem de Delta",
            "descricao": "Avança rasgando tudo com suas garras e dentes. Causa 5 golpes consecutivos de 50% de ATK e aplica Sangramento Crítico por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Espada de Ferro Gigante",
                "descricao": "Molda uma massa colossal de slime preto e esmaga a linha inimiga. Causa 220% de dano físico e quebra escudos de mana."
            }
        }
    },

    # =========================217
    "stark": {
        "nome": "Stark",
        "origem": "Frieren: Beyond Journey's End",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 130,
        "atk": 60,
        "matk": 0,
        "def": 35,
        "spd": 16,
        "crt": 15,
        "habilidade": {
            "nome": "Corte Destruidor de Stark",
            "descricao": "Stark arremessa toda a força de seu machado pesado no solo, abrindo fendas na terra. Causa 200% de ATK a um inimigo distante."
        },
        "evolucoes": {
            5: {
                "nome": "Golpe das Chamas de Trovão",
                "descricao": "Executa uma rotação com o machado que incendeia o alvo. Causa dano físico massivo e reduz a precisão inimiga em 30%."
            }
        }
    },

    # =========================218
    "edward_elric": {
        "nome": "Edward Elric",
        "origem": "Fullmetal Alchemist",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 50,
        "matk": 35,
        "def": 28,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Espada Automail e Pilares",
            "descricao": "Edward transmuta seu braço de metal e ergue pilares de pedra sob o inimigo. Causa 150% de ATK e atordoa o oponente por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Transmutação Alquímica Suprema",
                "descricao": "Desconstrói o equipamento inimigo. Reduz a DEF e o ATK do oponente em 40% durante o resto do combate."
            }
        }
    },

    # =========================219
    "gon_freecss": {
        "nome": "Gon Freecss",
        "origem": "Hunter x Hunter",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 56,
        "matk": 10,
        "def": 25,
        "spd": 20,
        "crt": 15,
        "habilidade": {
            "nome": "Jajanken: Pedra!",
            "descricao": "Concentra o Nen em seu punho direito. Passa 1 turno carregando e no próximo desfere um soco que causa 350% de ATK que ignora defesas."
        },
        "evolucoes": {
            5: {
                "nome": "Voto de Sacrifício Extremo",
                "descricao": "Gon assume sua forma adulta ao custo de sua energia vital. Concede +100% de ATK por 3 turnos, mas perde 20% de HP máximo por turno."
            }
        }
    },

    # =========================220
    "megumi_fushiguro": {
        "nome": "Megumi Fushiguro",
        "origem": "Jujutsu Kaisen",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 25,
        "matk": 48,
        "def": 20,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Dez Sombras: Cães Divinos",
            "descricao": "Evoca seus shikigamis de sombras que caçam os inimigos. Causa 130% de MATK e drena 15% de energia (atrasa o cooldown do alvo)."
        },
        "evolucoes": {
            5: {
                "nome": "Quimera Jardim das Sombras",
                "descricao": "Ativa sua Expansão de Domínio. Todos os aliados ganham +30% de esquiva e Megumi passa a invocar múltiplos clones de sombra por turno."
            }
        }
    },

    # =========================221
    "kazuma_satou": {
        "nome": "Kazuma Satou",
        "origem": "KonoSuba",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 30,
        "matk": 25,
        "def": 18,
        "spd": 20,
        "crt": 25,
        "habilidade": {
            "nome": "Steal: Roubo de Calcinha",
            "descricao": "Kazuma usa sua sorte absurda para roubar o item chave do oponente. Desestabiliza o alvo, atordoando-o por 1 turno e roubando seu buff ativo."
        },
        "evolucoes": {
            5: {
                "nome": "Drenar Toque Profano",
                "descricao": "Aprende a técnica de drenar energia de mortos-vivos. Suga 150 de HP e 50 de mana do alvo e distribui igualmente aos aliados."
            }
        }
    },

    # =========================222
    "chariot": {
        "nome": "Shiny Chariot",
        "origem": "Little Witch Academia",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 52,
        "matk": 30,
        "def": 22,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Cetro Brilhante: Flecha de Luz",
            "descricao": "Dispara flechas reluzentes do seu cetro místico. Causa 160% de ATK mágico e impede os alvos de se esquivarem por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Shiny Arc de Chariot",
                "descricao": "Um disparo estelar devastador que purifica as forças malignas. Causa 250% de ATK em área e remove buffs de todos os inimigos."
            }
        }
    },

    # =========================223
    "akko_kagari": {
        "nome": "Akko Kagari",
        "origem": "Little Witch Academia",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 3,
        "max_star": 7,
        "hp": 95,
        "atk": 15,
        "matk": 52,
        "def": 16,
        "spd": 16,
        "crt": 10,
        "habilidade": {
            "nome": "Metamorfose Inesperada",
            "descricao": "Akko tenta uma magia de transformação mas erra de leve. Transforma um inimigo aleatório em um animal indefeso (reduz ATK/DEF dele em 50%) por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Selo Reluzente Desperto",
                "descricao": "Sua fé e crença criam milagres. Concede imunidade a debuffs de controle para a equipe e aumenta o poder mágico de todos em 30%."
            }
        }
    },

    # =========================224
    "morgiana": {
        "nome": "Morgiana",
        "origem": "Magi",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 58,
        "matk": 0,
        "def": 30,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Chute de Impacto de Fanalis",
            "descricao": "Usa a força monstruosa de suas pernas para esmagar os inimigos. Causa 180% de ATK físico e derruba o alvo na ordem de turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Amol: Correntes Flamejantes",
                "descricao": "Usa as algemas de seus tempos de escravidão com o poder do Djinn. Prende e incendeia até 2 alvos por 2 turnos."
            }
        }
    },

    # =========================225
    "midoriya": {
        "nome": "Izuku Midoriya",
        "origem": "Boku no Hero Academia",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 54,
        "matk": 0,
        "def": 25,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Delaware Smash: 100%",
            "descricao": "Desfere uma rajada de vento massiva estalando os dedos. Causa 220% de ATK físico, mas causa 15% de dano residual ao próprio Midoriya."
        },
        "evolucoes": {
            5: {
                "nome": "One For All: Full Cowl 20%",
                "descricao": "Distribui o poder pelo corpo sem quebrar ossos. Concede +30% de velocidade de ação permanente e aumenta o ATK físico em 35%."
            }
        }
    },

    # =========================226
    "ray": {
        "nome": "Ray",
        "origem": "The Promised Neverland",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 30,
        "matk": 30,
        "def": 20,
        "spd": 20,
        "crt": 15,
        "habilidade": {
            "nome": "Estratégia do Ponto Cego",
            "descricao": "Identifica a falha tática do oponente. Aumenta a chance crítica de todos os aliados em 20% e reduz a precisão inimiga em 25%."
        },
        "evolucoes": {
            5: {
                "nome": "Sacrifício Planejado",
                "descricao": "Ray se posiciona para levar o golpe fatal por um aliado de ataque (DPS), concedendo-lhe um escudo de fogo protetor no processo."
            }
        }
    },

    # =========================227
    "rin_okumura": {
        "nome": "Rin Okumura",
        "origem": "Ao no Exorcist",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 65,
        "matk": 35,
        "def": 30,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Chamas Azuis de Satã",
            "descricao": "Saca a espada Kurikara e libera suas chamas azuis infernais. Causa 180% de ATK misto (físico + mágico) e aplica Queimadura que ignora DEF."
        },
        "evolucoes": {
            5: {
                "nome": "Chamas da Erradicação de Rin",
                "descricao": "Desfere um corte espiritual ardente. Causa 300% de dano verdadeiro a inimigos da categoria demônio e mortos-vivos."
            }
        }
    },

    # =========================228
    "arthur_a_angel": {
        "nome": "Arthur A. Angel",
        "origem": "Ao no Exorcist",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 62,
        "matk": 10,
        "def": 32,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Espada Caliburn do Paladino",
            "descricao": " Arthur usa sua espada consciente para desferir golpes milagrosos. Causa 160% de ATK e impede o alvo de usar buffs de proteção."
        },
        "evolucoes": {
            5: {
                "nome": "Julgamento Angelical",
                "descricao": "Evoca uma cruz de energia sagrada. Causa 250% de ATK ao inimigo com maior poder e o silencia por 1 turno completo."
            }
        }
    },

    # =========================229
    "zuko": {
        "nome": "Zuko",
        "origem": "Avatar: A Lenda de Aang",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 60,
        "matk": 30,
        "def": 24,
        "spd": 20,
        "crt": 12,
        "habilidade": {
            "nome": "Dobra de Fogo Suprema",
            "descricao": "Dispara rajadas consecutivas de chamas ardentes com golpes de artes marciais. Causa 160% de ATK e aplica Queimadura Pesada por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Redirecionamento de Raios",
                "descricao": "Quando Zuko ou um aliado recebe dano mágico elemental, ele absorve 50% desse dano e contra-ataca com uma descarga elétrica de 200% de ATK."
            }
        }
    },

    # =========================230
    "yuno_grinberryall": {
        "nome": "Yuno Grinberryall",
        "origem": "Black Clover",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 20,
        "matk": 72,
        "def": 22,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Magia de Vento: Espada de Zephyr",
            "descricao": "Molda o vento em uma espada condensada de mana pura. Causa 190% de MATK, quebrando qualquer barreira de proteção ativa no alvo."
        },
        "evolucoes": {
            5: {
                "nome": "Spirit Dive: Forma Sylph",
                "descricao": "Fusão completa com o espírito do vento. Aumenta sua SPD em 50% e faz com que todas as suas magias de área tenham 30% de chance de atordoar."
            }
        }
    },

    # =========================231
    "kenpachi_zaraki": {
        "nome": "Kenpachi Zaraki",
        "origem": "Bleach",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 150,
        "atk": 75,
        "matk": 0,
        "def": 30,
        "spd": 16,
        "crt": 10,
        "habilidade": {
            "nome": "Remoção do Tapa-Olho",
            "descricao": "Zaraki remove seu limitador de energia espiritual, gerando uma pressão de esmagamento. Aumenta seu ATK em 50% e sua chance crítica em 30% por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Nozarashi: Bankai Espantoso",
                "descricao": "Assume sua forma demoníaca de Bankai. Seus ataques normais causam dano verdadeiro que afeta todos os inimigos simultaneamente."
            }
        }
    },

    # =========================232
    "alpha": {
        "nome": "Alpha",
        "origem": "Eminence in Shadow",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 125,
        "atk": 55,
        "matk": 45,
        "def": 30,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Liderança das Sombras de Alpha",
            "descricao": "Sua ordem no campo de batalha organiza as táticas. Concede +30% de DEF e +25% de ATK/MATK para toda a equipe por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Corte de Slime Sagrado",
                "descricao": "Usa sua espada infundida com mana negra e pura. Causa 220% de dano mágico que ignora imunidades e debulha as defesas mágicas inimigas."
            }
        }
    },

    # =========================233
    "grey_fullbuster": {
        "nome": "Grey Fullbuster",
        "origem": "Fairy Tail",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 30,
        "matk": 68,
        "def": 28,
        "spd": 20,
        "crt": 10,
        "habilidade": {
            "nome": "Ice Make: Lança-Gelo",
            "descricao": "Cria e dispara uma saraivada de lanças de gelo afiadas. Causa 160% de MATK e reduz a SPD do alvo em 35% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Magia de Devil Slayer do Gelo",
                "descricao": "Infunde suas magias com gelo demoníaco. Suas magias passam a causar congelamento (Stun) e causam dano dobrado em demônios."
            }
        }
    },

    # =========================234
    "erza_scarlet": {
        "nome": "Erza Scarlet",
        "origem": "Fairy Tail",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 155,
        "atk": 48,
        "matk": 20,
        "def": 50,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Reequipar: Armadura Imperatriz",
            "descricao": "Erza muda sua armadura para suportar as ameaças. Atrai provocação de todos e recebe imunidade a atordoamentos e controle de grupo por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Armadura de Nakagami",
                "descricao": "Veste a armadura que quebra as leis da magia. Seu próximo ataque ignora completamente as resistências do alvo e o bane temporariamente."
            }
        }
    },

    # =========================235
    "siegfried": {
        "nome": "Siegfried",
        "origem": "Fate/Apocrypha",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 170,
        "atk": 40,
        "matk": 10,
        "def": 60,
        "spd": 12,
        "crt": 5,
        "habilidade": {
            "nome": "Armor of Fafnir: Pele de Dragão",
            "descricao": "O lendário herói ativa sua imunidade dracônica. Reduz todo dano recebido em 50% e fica imune a ataques de sangramento ou críticos."
        },
        "evolucoes": {
            5: {
                "nome": "Balmung: Fantasma Nobre",
                "descricao": "Grita 'Balmung' e libera uma rajada semicircular de energia luminosa azul. Causa 220% de MATK em área que esmaga os inimigos."
            }
        }
    },

    # =========================236
    "tamaki_kotatsu": {
        "nome": "Tamaki Kotatsu",
        "origem": "Fire Force",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 100,
        "atk": 62,
        "matk": 15,
        "def": 20,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Forma de Gato de Fogo",
            "descricao": "Gera caudas e orelhas de fogo que aumentam sua agilidade. Ganha +35% de SPD e faz com que seus ataques apliquem Queimadura por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Sorte Desajeitada e Sedutora",
                "descricao": "Sua falta de jeito atordoa e confunde o alvo na hora do ataque. Reduz a precisão do oponente em 40% e o imobiliza por 1 turno."
            }
        }
    },

    # =========================237
    "diana_cavendish": {
        "nome": "Diana Cavendish",
        "origem": "Little Witch Academia",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 20,
        "matk": 70,
        "def": 24,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Magia Imperial Cavendish",
            "descricao": "Conjura um feitiço avançado de dissipação. Causa 180% de MATK e remove instantaneamente todos os buffs ativos na equipe inimiga."
        },
        "evolucoes": {
            5: {
                "nome": "Invocação da Fênix de Luz",
                "descricao": "Usa a magia lendária para invocar a ave espiritual. Cura todos os aliados em 25% do HP e causa queimadura em área nos oponentes."
            }
        }
    },

    # =========================238
    "medaka_kurokami": {
        "nome": "Medaka Kurokami",
        "origem": "Medaka Box",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 58,
        "matk": 35,
        "def": 30,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "The End: Copiar Perfeição",
            "descricao": "Medaka observa a habilidade do inimigo e a replica com 120% da força original. Copia o buff do alvo e o atordoa de choque."
        },
        "evolucoes": {
            7: {
                "nome": "War God Mode: Forma Divina",
                "descricao": "Seu cabelo fica rosa e seus olhos vermelhos. Entra em modo deus da guerra, recebendo imunidade absoluta e +50% de ATK por 2 turnos."
            }
        }
    },

    # =========================239
    "bakugou": {
        "nome": "Katsuki Bakugou",
        "origem": "Boku no Hero Academia",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 68,
        "matk": 20,
        "def": 20,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Explosão de Impulso Traseiro",
            "descricao": "Dispara explosões severas das palmas de suas mãos. Causa 180% de ATK físico, quebrando escudos de terra e atordoando o alvo."
        },
        "evolucoes": {
            5: {
                "nome": "Howitzer Impact: Tornado Explosivo",
                "descricao": "Gira gerando um tornado de calor e explode em área. Causa 260% de ATK a todos os inimigos e queima as frentes de defesa."
            }
        }
    },

    # =========================240
    "todoroki": {
        "nome": "Shouto Todoroki",
        "origem": "Boku no Hero Academia",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 25,
        "matk": 72,
        "def": 24,
        "spd": 20,
        "crt": 12,
        "habilidade": {
            "nome": "Meio-Quente Meio-Frio",
            "descricao": "Congela e depois incendeia o alvo. Causa 180% de MATK, deixando o oponente atordoado por 1 turno e queimado por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Prominence Burn local / Punho de Fogo",
                "descricao": "Libera uma parede gigante de calor. Causa 250% de MATK em área e anula qualquer buff de gelo ou escudo do time oponente."
            }
        }
    },

    # =========================241
    "kakashi_hatake": {
        "nome": "Kakashi Hatake",
        "origem": "Naruto",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 55,
        "matk": 45,
        "def": 25,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Chidori: Espada de Relâmpago",
            "descricao": "Kakashi concentra relâmpagos na mão e perfura o alvo. Causa 200% de dano que ignora completamente a defesa e atordoa o oponente."
        },
        "evolucoes": {
            5: {
                "nome": "Kamui: Distorção Espacial",
                "descricao": "Usa seu Mangekyou Sharingan para distorcer o espaço. Concede imunidade total por 1 turno e envia o ataque do inimigo de volta contra ele."
            }
        }
    },

    # =========================242
    "aura_bella_fiore": {
        "nome": "Aura Bella Fiore",
        "origem": "Overlord",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 25,
        "matk": 55,
        "def": 28,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Domadora de Feras de Nazarick",
            "descricao": "Invoca feras espirituais que atacam e defendem o mestre. Aumenta a velocidade de toda a equipe em 25% e cura em 15%."
        },
        "evolucoes": {
            5: {
                "nome": "Sopro de Perturbação Mental",
                "descricao": "Dispara flechas com fragrâncias que afetam a mente. Deixa os inimigos confusos, forçando-os a atacar seus próprios aliados por 1 turno."
            }
        }
    },

    # =========================243
    "yu_narukami": {
        "nome": "Yu Narukami",
        "origem": "Persona",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 52,
        "matk": 48,
        "def": 26,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Izanagi: Espada do Relâmpago",
            "descricao": "Yu convoca seu Persona Izanagi para eletrocutar o solo. Causa 150% de ATK e MATK combinados, com 35% de chance de paralisar (Stun)."
        },
        "evolucoes": {
            5: {
                "nome": "Izanagi-no-Okami: Verdade Divina",
                "descricao": "Desperta seu Persona supremo. Causa 300% de dano mágico em área que ignora resistências do oponente e purifica debuffs aliados."
            }
        }
    },

    # =========================244
    "makoto_yuki": {
        "nome": "Makoto Yuki",
        "origem": "Persona",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 50,
        "matk": 50,
        "def": 25,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Orpheus: Harpa de Fogo",
            "descricao": "Makoto atira em sua cabeça com o Evoker e invoca Orpheus. Causa 160% de MATK elemental de fogo e cura um aliado em 20% do HP."
        },
        "evolucoes": {
            5: {
                "nome": "Messiah: Redenção Universal",
                "descricao": "Invoca o Messias. Ressuscita um aliado derrotado com 50% de HP e concede imunidade a ataques normais para a equipe por 1 turno."
            }
        }
    },

    # =========================245
    "kyoko_sakura": {
        "nome": "Kyoko Sakura",
        "origem": "Madoka Magica",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 65,
        "matk": 10,
        "def": 22,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Lança Modular Extensível",
            "descricao": "Desfere golpes rápidos e em cadeia usando sua lança que se divide. Causa 170% de ATK físico e reduz a defesa do alvo em 30%."
        },
        "evolucoes": {
            5: {
                "nome": "Barreira de Rosas de Cristal",
                "descricao": "Cria uma parede geométrica impenetrável. Protege a equipe, redirecionando 50% de todo o dano recebido para a barreira cristalina."
            }
        }
    },

    # =========================246
    "okita_souji": {
        "nome": "Okita Souji",
        "origem": "Fate/Grand Order",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 100,
        "atk": 72,
        "matk": 0,
        "def": 18,
        "spd": 36,
        "crt": 25,
        "habilidade": {
            "nome": "Corte de Três Passos de Okita",
            "descricao": "Okita cruza o espaço instantaneamente ignorando a física. Desfere um golpe de 220% de ATK que ignora a esquiva e causa crítico garantido."
        },
        "evolucoes": {
            5: {
                "nome": "Tuberculose Frágil (Contradição)",
                "descricao": "Seu ponto fraco vira foco. Entra em estado de precisão extrema que dobra o dano de seus acertos críticos por 2 turnos."
            }
        }
    },

    # =========================247
    "kurama": {
        "nome": "Kurama",
        "origem": "Yu Yu Hakusho",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 25,
        "matk": 70,
        "def": 25,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Rose Whip: Chicote de Rosas",
            "descricao": "Transmuta uma rosa em um chicote espinhoso que rasga a pele. Causa 150% de MATK e aplica Sangramento Crítico por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Yoko Kurama: Raposa Demônio",
                "descricao": "Assume sua forma demoníaca ancestral de Yoko Kurama. Invoca plantas carnívoras que prendem os inimigos, sugando 20% do HP deles."
            }
        }
    },

    # =========================248
    "emma": {
        "nome": "Emma",
        "origem": "The Promised Neverland",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 45,
        "matk": 45,
        "def": 28,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Esperança Inabalável de Emma",
            "descricao": "Sua persistência impede a guilda de cair. Concede regeneração de 10% do HP e remove o debuff de medo de todos os aliados."
        },
        "evolucoes": {
            5: {
                "nome": "Promessa de Fuga Perfeita",
                "descricao": "Traça uma rota infalível de escape. Concede +40% de esquiva (dodge) e +30% de velocidade de ação para todos os aliados por 2 turnos."
            }
        }
    },

    # =========================249
    "mephisto_pheles": {
        "nome": "Mephisto Pheles",
        "origem": "Ao no Exorcist",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 40,
        "matk": 75,
        "def": 30,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Barreira do Espaço e do Tempo",
            "descricao": "Controla a dimensão ao redor da arena. Congela 1 inimigo por 2 turnos e acelera a velocidade da sua equipe em 30%."
        },
        "evolucoes": {
            7: {
                "nome": "Transformação do Cão Demônio",
                "descricao": "Mephisto assume sua forma lúdica de cachorrinho. Fica imune a ataques físicos e mágico-ofensivos por 3 turnos, curando o líder do time."
            }
        }
    },

    # =========================250
    "aang": {
        "nome": "Aang",
        "origem": "Avatar: A Lenda de Aang",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 45,
        "matk": 80,
        "def": 35,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Estado Avatar Supremo",
            "descricao": "Aang une os 4 elementos, girando esferas de vento, pedra, fogo e água. Causa 220% de MATK em área a todos os oponentes."
        },
        "evolucoes": {
            7: {
                "nome": "Dobra de Energia Sagrada",
                "descricao": "Remove permanentemente os buffs de todos os oponentes e silencia (silence) as habilidades mágicas inimigas por 2 turnos completos."
            }
        }
    },

    # =========================251
    "goku": {
        "nome": "Son Goku",
        "origem": "Dragon Ball",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 60,
        "matk": 35,
        "def": 35,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Super Saiyajin Divino",
            "descricao": "Sua força ultrapassa os limites dos mortais. Aumenta seu ATK em 50%, sua velocidade em 30% e fica imune a atordoamento por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Instinto Superior Completo (MUI)",
                "descricao": "Concede +100% de esquiva absoluta por 2 turnos. Sempre que desviar de um ataque, contra-ataca com um soco físico de 250% de ATK."
            }
        }
    },

    # =========================252
    "vegeta": {
        "nome": "Vegeta",
        "origem": "Dragon Ball",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 88,
        "matk": 30,
        "def": 38,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Final Flash Destruidor",
            "descricao": "Vegeta dispara uma rajada massiva de energia dourada. Causa 280% de ATK mágico e reduz a DEF dos inimigos em 40% por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Ultra Ego: Força pelo Sofrimento",
                "descricao": "Sua força cresce conforme apanha. Para cada 10% de HP perdido na batalha, aumenta seu poder físico (ATK) em 25%."
            }
        }
    },

    # =========================253
    "epsilon": {
        "nome": "Epsilon",
        "origem": "Eminence in Shadow",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 30,
        "matk": 75,
        "def": 28,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Sinfonia de Slime Curativa",
            "descricao": "Ajusta perfeitamente seu manto de slime para regenerar. Cura todos os aliados em 35% do MATK e remove debuffs de atributos."
        },
        "evolucoes": {
            7: {
                "nome": "Corte de Precisão Extrema (Epsilon)",
                "descricao": "Dispara lâminas finíssimas de slime que causam 200% de MATK que ignora escudos mágicos e reduz permanentemente o ATK inimigo em 20%."
            }
        }
    },

    # =========================254
    "merlin_fate": {
        "nome": "Merlin (Fate)",
        "origem": "Fate/Grand Order",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 20,
        "matk": 82,
        "def": 26,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Garden of Avalon: Jardim Iluminado",
            "descricao": "O mago das flores espalha ilusões protetoras. Concede barreira à equipe que recupera 15% do HP máximo por turno por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Criação de Heróis Suprema",
                "descricao": "Aumenta drasticamente os atributos físicos e a chance de acerto crítico do líder aliado em 50% por 3 rodadas."
            }
        }
    },

    # =========================255
    "medusa": {
        "nome": "Medusa (Rider)",
        "origem": "Fate/Stay Night",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 78,
        "matk": 30,
        "def": 22,
        "spd": 42,
        "crt": 20,
        "habilidade": {
            "nome": "Pegasus: Bellerophon",
            "descricao": "Invoca a montaria alada mística e atropela o campo inimigo. Causa 240% de ATK misto em área e reduz a velocidade inimiga em 50%."
        },
        "evolucoes": {
            7: {
                "nome": "Cybele: Olhar Petrificante",
                "descricao": "Remove sua venda mágica. Aplica paralisia total (Stun) a todos os oponentes por 1 turno e reduz a defesa mágica deles a zero."
            }
        }
    },

    # =========================256
    "astolfo": {
        "nome": "Astolfo",
        "origem": "Fate/Apocrypha",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 65,
        "matk": 40,
        "def": 26,
        "spd": 40,
        "crt": 25,
        "habilidade": {
            "nome": "Trap of Argalia: Toque de Derrubada",
            "descricao": "Ataca usando sua lança de ouro de longo alcance. Causa 160% de ATK e derruba as pernas do inimigo (Stun garantido de 1 turno)."
        },
        "evolucoes": {
            7: {
                "nome": "Hippogriff: Voo Transdimensional",
                "descricao": "Monta em seu Hipogrifo, desaparecendo do campo. Fica intocável por 2 turnos e reaparece causando 250% de ATK físico de surpresa."
            }
        }
    },

    # =========================257
    "maki_oze": {
        "nome": "Maki Oze",
        "origem": "Fire Force",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 165,
        "atk": 60,
        "matk": 30,
        "def": 55,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Manipulação de Chamas de Maki",
            "descricao": "Maki absorve as labaredas ao redor para moldar barreiras. Cria um escudo de chama de 30% do HP para todos os aliados."
        },
        "evolucoes": {
            7: {
                "nome": "Unidade de Choque Sputter e Flare",
                "descricao": "Usa seus mascotes de fogo para repelir. Reduz em 90% o dano recebido por ataques de fogo ou debuffs de queima sofridos pela equipe."
            }
        }
    },

    # =========================258
    "giorno_giovanna": {
        "nome": "Giorno Giovanna",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 55,
        "matk": 55,
        "def": 28,
        "spd": 26,
        "crt": 12,
        "habilidade": {
            "nome": "Gold Experience: Criação de Vida",
            "descricao": "Cria pequenos animais de objetos. Concede cura de 30% do HP para um aliado ferido e reflete 30% do dano recebido por ele."
        },
        "evolucoes": {
            7: {
                "nome": "Gold Experience Requiem (GER)",
                "descricao": "Nega a causalidade do inimigo. Anula completamente a última ação ofensiva do oponente e aplica dano verdadeiro pesado ao agressor."
            }
        }
    },

    # =========================259
    "johnny_joestar": {
        "nome": "Johnny Joestar",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 105,
        "atk": 78,
        "matk": 20,
        "def": 20,
        "spd": 32,
        "crt": 30,
        "habilidade": {
            "nome": "Tusk Act 2: Unha Giratória",
            "descricao": "Dispara unhas com rotação aurea de alta precisão. Causa 180% de ATK físico com 50% de chance crítica e persegue alvos invisíveis."
        },
        "evolucoes": {
            7: {
                "nome": "Tusk Act 4: Rotação Infinita",
                "descricao": "Dispara o giro infinito que ignora completamente barreiras, imortalidade e escudos mágicos. Causa dano contínuo destrutivo por 3 turnos."
            }
        }
    },

    # =========================260
    "josuke_higashikata": {
        "nome": "Josuke Higashikata",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 50,
        "matk": 62,
        "def": 30,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Crazy Diamond: Restauração Crítica",
            "descricao": "Restaura instantaneamente o HP de um aliado ferido a 100% (recupera sua estrutura corporal) e limpa todos os seus debuffs de status."
        },
        "evolucoes": {
            7: {
                "nome": "Reversão Furiosa de Matéria",
                "descricao": "Reverte o dano sofrido pela equipe. Converte 40% do dano total recebido pela guilda na última rodada em cura instantânea."
            }
        }
    },

    # =========================261
    "kumagawa_misogi": {
        "nome": "Kumagawa Misogi",
        "origem": "Medaka Box",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 50,
        "matk": 70,
        "def": 30,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Book Maker: Parafusos Gigantes",
            "descricao": "Apunhala o oponente com parafusos gigantes de desespero. Reduz o ATK, DEF, SPD e ELO do inimigo ao nível mínimo (1) por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "All Fiction: Apagar a Realidade",
                "descricao": " Kumagawa 'apaga' o próprio dano sofrido. Cancela as feridas de sua equipe (cura 50% de HP) e desfaz a última morte de aliado."
            }
        }
    },

    # =========================262
    "naruto_uzumaki": {
        "nome": "Naruto Uzumaki",
        "origem": "Naruto",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 78,
        "matk": 65,
        "def": 32,
        "spd": 28,
        "crt": 12,
        "habilidade": {
            "nome": "Modo Sábio dos Seis Caminhos",
            "descricao": "Ganha o chakra da Kurama e das Bestas. Concede +40% de ATK e MATK para toda a equipe, curando-os em 10% por turno."
        },
        "evolucoes": {
            7: {
                "nome": "Rasenshuriken de Lava / Magnetismo",
                "descricao": "Dispara um Rasenshuriken infundido com lava e selos magnéticos. Causa 280% de dano mágico em área e paralisa todos por 1 turno."
            }
        }
    },

    # =========================263
    "sasuke_uchiha": {
        "nome": "Sasuke Uchiha",
        "origem": "Naruto",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 82,
        "matk": 55,
        "def": 25,
        "spd": 38,
        "crt": 20,
        "habilidade": {
            "nome": "Chidori Kagutsuchi: Chamas Negras",
            "descricao": "Infunde seu chidori com as chamas negras do Amaterasu. Causa 220% de ATK físico e aplica queimadura eterna que não pode ser curada."
        },
        "evolucoes": {
            7: {
                "nome": "Amenotejikara: Troca de Posição",
                "descricao": "Sasuke usa o Rinnegan para trocar de lugar com o inimigo antes de ser atacado, redirecionando o dano de volta para a equipe dele."
            }
        }
    },

    # =========================264
    "shalltear_bloodfallen": {
        "nome": "Shalltear Bloodfallen",
        "origem": "Overlord",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 160,
        "atk": 70,
        "matk": 50,
        "def": 52,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Lança de Espinhos Sangrentos",
            "descricao": "Shalltear usa sua lança vampírica sagrada. Causa 180% de ATK físico e drena o dano causado para curar a si mesma em 100% desse valor."
        },
        "evolucoes": {
            7: {
                "nome": "Einherjar: Duplicata de Sangue",
                "descricao": "Invoca um clone perfeito de si mesma feito de sangue que possui 100% de seu ATK/DEF e atrai todas as provocações inimigas."
            }
        }
    },

    # =========================265
    "homura_akemi": {
        "nome": "Homura Akemi",
        "origem": "Madoka Magica",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 105,
        "atk": 80,
        "matk": 40,
        "def": 22,
        "spd": 44,
        "crt": 25,
        "habilidade": {
            "nome": "Parada Temporal Zafkiel local",
            "descricao": "Gira o escudo do tempo congelando o fluxo. Todos os inimigos perdem a ação do turno e Homura desfere 3 tiros físicos críticos grátis."
        },
        "evolucoes": {
            7: {
                "nome": "Akuma Homura: Lúcifer Desperto",
                "descricao": "Assume sua forma de demônio que altera as leis da física. Reduz o ATK, DEF e a precisão de todos os oponentes em 40% durante toda a luta."
            }
        }
    },

    # =========================266
    "adao": {
        "nome": "Adão",
        "origem": "Record of Ragnarok",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 82,
        "matk": 0,
        "def": 32,
        "spd": 35,
        "crt": 20,
        "habilidade": {
            "nome": "Olhos do Senhor: Reflexo Divino",
            "descricao": "Adão desvia perfeitamente do ataque físico do oponente e o desfere de volta contra o agressor com o dobro do poder."
        },
        "evolucoes": {
            7: {
                "nome": "Amor Paterno Inabalável",
                "descricao": "Se recusa a cair pelos seus filhos. Ao chegar a 0 HP, continua lutando com 1 HP, imunidade a debuffs e +50% de ATK por 2 rodadas."
            }
        }
    },

    # =========================267
    "qin_shi_huang": {
        "nome": "Qin Shi Huang",
        "origem": "Record of Ragnarok",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 65,
        "matk": 45,
        "def": 42,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Dobra da Armadura do Imperador",
            "descricao": "Usa sua técnica de Chi You para absorver o dano sofrido por ele ou aliados, acumulando energia para contra-atacar em dobro."
        },
        "evolucoes": {
            7: {
                "nome": "Estrela do Céu de Qin Shi Huang",
                "descricao": "Enxerga as estrelas de energia vital (pontos fracos) dos inimigos. Todos os oponentes perdem 40% de DEF e sofrem 30% mais dano físico."
            }
        }
    },

    # =========================268
    "jack_estripador": {
        "nome": "Jack o Estripador",
        "origem": "Record of Ragnarok",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 74,
        "matk": 35,
        "def": 24,
        "spd": 32,
        "crt": 25,
        "habilidade": {
            "nome": "Vexação de Londres: Armadilha",
            "descricao": "Atira facas, vidros e fiação infundidas com a bênção divina do toque. Causa 180% de ATK e aplica Sangramento Crítico por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Querida Londres Sombria",
                "descricao": "Cria uma névoa densa. Oculta (ocultação) o seu grupo por 2 turnos, aumentando a evasão de todos os aliados em 35%."
            }
        }
    },

    # =========================269
    "saiki_kusuo": {
        "nome": "Saiki Kusuo",
        "origem": "Saiki Kusuo no Psi-nan",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 30,
        "matk": 85,
        "def": 30,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Telepatia de Controle Mental",
            "descricao": "Infiltra a mente inimiga de forma invasiva. Controla 1 inimigo por 1 turno e o força a usar sua habilidade principal contra a própria equipe."
        },
        "evolucoes": {
            7: {
                "nome": "Remoção dos Limitadores Rosas",
                "descricao": "Saiki remove os pinos limitadores em sua cabeça. Libera uma fenda psíquica que causa 350% de dano verdadeiro massivo em área."
            }
        }
    },

    # =========================270
    "asuna": {
        "nome": "Asuna Yuuki",
        "origem": "Sword Art Online",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 76,
        "matk": 20,
        "def": 24,
        "spd": 38,
        "crt": 22,
        "habilidade": {
            "nome": "Flashing Penetrator: Estocada Rápida",
            "descricao": "Desfere estocadas cirúrgicas com sua espada ropiera fina. Causa 5 hits de 40% de ATK físico que ignoram completamente a esquiva inimiga."
        },
        "evolucoes": {
            7: {
                "nome": "Asa da Criação: Deusa Stacia",
                "descricao": "Assume sua forma divina de deusa Stacia. Seus ataques ignoram a defesa inimiga e ela pode criar fendas no solo que imobilizam os oponentes."
            }
        }
    },

    # =========================271
    "alice": {
        "nome": "Alice Zuberg",
        "origem": "Sword Art Online",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 160,
        "atk": 55,
        "matk": 45,
        "def": 52,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Espada de Oliveira Fragrante",
            "descricao": "Divide sua espada de ouro em milhares de pétalas cortantes. Cria uma barreira mágica em área que reduz em 40% o dano mágico recebido."
        },
        "evolucoes": {
            7: {
                "nome": "Corte de Fusão de Luz Sagrada",
                "descricao": "Concentra o feixe luminoso solar em um golpe de espada direto. Causa 220% de dano físico e destrói escudos do inimigo."
            }
        }
    },

    # =========================272
    "shion": {
        "nome": "Shion",
        "origem": "Tensei Shitara Slime Datta Ken",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 65,
        "matk": 30,
        "def": 35,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Cozinha Divina de Shion (Culinária)",
            "descricao": "Sua comida de gosto horrível, mas propriedades regenerativas, reescreve a realidade. Cura a equipe inteira em 30% do HP."
        },
        "evolucoes": {
            7: {
                "nome": "Goriki: Machado Hercúleo Gigante",
                "descricao": "Desfere um golpe vertical violento com seu machado gigante. Causa 250% de ATK e quebra permanentemente 50% da defesa do oponente."
            }
        }
    },

    # =========================273
    "milim_nava": {
        "nome": "Milim Nava",
        "origem": "Tensei Shitara Slime Datta Ken",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 90,
        "matk": 45,
        "def": 30,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Buster Dracônico de Milim",
            "descricao": "Milim dispara um feixe colossal de energia pura das palmas das mãos. Causa 280% de ATK físico a um oponente e esmaga sua retaguarda."
        },
        "evolucoes": {
            7: {
                "nome": "Forma Mítica do Rei Dragão",
                "descricao": "Ativa sua armadura divina de chifre. Concede imunidade total e dobra o seu ataque (ATK) nos 2 primeiros turnos do combate."
            }
        }
    },

    # =========================274
    "beatrice_umineko": {
        "nome": "Beatrice",
        "origem": "Umineko no Naku Koro ni",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 25,
        "matk": 100,
        "def": 28,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Magia Vermelha da Verdade",
            "descricao": "Pronuncia uma verdade vermelha absoluta impossível de negar. Causa 240% de MATK e ignora completamente escudos e defesas mágicas."
        },
        "evolucoes": {
            7: {
                "nome": "Invocação das Borboletas de Ouro",
                "descricao": "Invoca nuvens de borboletas de ouro que devoram a mente dos oponentes. Causa dano mágico contínuo massivo e silencia a equipe inimiga."
            }
        }
    },

    # =========================275
    "hiei": {
        "nome": "Hiei",
        "origem": "Yu Yu Hakusho",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 105,
        "atk": 82,
        "matk": 40,
        "def": 20,
        "spd": 46,
        "crt": 25,
        "habilidade": {
            "nome": "Chamas Negras do Dragão das Trevas",
            "descricao": "Dispara um dragão de fogo negro infernal que devora o alvo. Causa 220% de MATK e aplica Queimadura que esvazia o HP do inimigo."
        },
        "evolucoes": {
            7: {
                "nome": "Espada de Fogo do Dragão Negro",
                "descricao": "Hiei absorve o dragão negro em sua lâmina. Seus ataques normais causam dano físico e mágico crítico duplo ignorando a evasão."
            }
        }
    },

    # =========================276
    "yusuke_urameshi": {
        "nome": "Yusuke Urameshi",
        "origem": "Yu Yu Hakusho",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 80,
        "matk": 40,
        "def": 28,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Leigan: Disparo Espiritual",
            "descricao": "Aponta o dedo indicador e dispara uma esfera de energia espiritual concentrada. Causa 150% de ATK e derruba as barreiras defensivas do alvo."
        },
        "evolucoes": {
            7: {
                "nome": "Despertar Mazoku: Sangue Demoníaco",
                "descricao": "O sangue ancestral demoníaco desperta em suas veias. Recupera 50% de HP ao receber dano fatal e recebe +50% de ATK e velocidade de ação."
            }
        }
    },
    # =========================277
    "madoka_kaname": {
        "nome": "Madoka Kaname",
        "origem": "Madoka Magica",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 7,
        "max_star": 7,
        "hp": 680,
        "atk": 30,
        "matk": 295,
        "def": 45,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Salvação Conceitual",
            "descricao": "Madoka usa sua essência divina para curar a equipe inteira em 450% do seu MATK e limpar instantaneamente todos os debuffs ativos."
        },
        "evolucoes": {
            7: {
                "nome": "Forma Suprema de Deusa",
                "atk": 15,
                "spd": 10,
                "descricao": "Desperta a Deusa Madoka. Sempre que um aliado receber um golpe fatal, ela impede a sua morte e concede-lhe um escudo indestrutível por 2 turnos (Uma vez por combate)."
            }
        }
    },

    # =========================278
    "featherine": {
        "nome": "Featherine Augustus Aurora",
        "origem": "Umineko no Naku Koro ni",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 7,
        "max_star": 7,
        "hp": 675,
        "atk": 35,
        "matk": 305,
        "def": 40,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Reescrita do Roteiro",
            "descricao": "Featherine manipula as páginas da existência. Causa 520% de MATK em um único alvo e atrasa o seu turno para o fim da fila de ação."
        },
        "evolucoes": {
            7: {
                "nome": "Autoridade Absoluta",
                "atk": 25,
                "spd": 5,
                "descricao": "Nega a interferência do adversário. Remove todos os buffs do time inimigo e os impede de ganhar novos buffs ou escudos por 6 turnos inteiros."
            }
        }
    },

    # =========================279
    "anti_espiral": {
        "nome": "Anti-Espiral",
        "origem": "Tengen Toppa Gurren Lagann",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 7,
        "max_star": 7,
        "hp": 590,
        "atk": 50,
        "matk": 98,
        "def": 50,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Desespero do Infinito",
            "descricao": "Lança uma onda de anti-matéria destrutiva. Causa 480% de MATK em área e reduz o ATK físico e mágico de todos os atingidos em 50% por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Cárcere Multidimensional",
                "descricao": "Prende a mente do alvo com maior SPD em um labirinto mental. O alvo fica atordoado (Stun) por 3 turnos e perde 60% de sua defesa máxima.",
                "atk": 20,
                "spd": 8
            }
        }
    },

    # =========================280
    "zenoh": {
        "nome": "Zenoh",
        "origem": "Dragon Ball Super",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 7,
        "max_star": 7,
        "hp": 500,
        "atk": 80,
        "matk": 90,
        "def": 45,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Apagamento Brincalhão",
            "descricao": "Apaga fisicamente o alvo de forma infantil. Causa dano massivo baseado em 45% do HP atual do oponente, ignorando toda e qualquer defesa ativa."
        },
        "evolucoes": {
            7: {
                "nome": "Julgamento do Rei de Tudo",
                "atk": 30,
                "spd": 5,
                "descricao": "Seu olhar de tédio assusta a arena. Atordoa o oponente principal por 3 turno e reduz o dano total que a sua equipe sofre em 60% por 2 rodadas."
            }
        }
    },

    # =========================281
    "wang_ling": {
        "nome": "Wang Ling",
        "origem": "The Daily Life of the Immortal King",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 7,
        "max_star": 7,
        "hp": 565,
        "atk": 305,
        "matk": 45,
        "def": 35,
        "spd": 40,
        "crt": 25,
        "habilidade": {
            "nome": "Selo Espiritual Solto",
            "descricao": "Wang Ling trinca o seu selo de contenção para desferir um soco sísmico. Causa 450% de ATK que ignora escudos e armaduras."
        },
        "evolucoes": {
            7: {
                "nome": "Espada Jingke Suprema",
                "atk": 40,
                "spd": 15,
                "descricao": "Wang Ling invoca sua espada consciente. Causa dano crítico inevitável e executa instantaneamente alvos com menos de 50% de vida máxima."
            }
        }
    },

    # =========================282
    "yogiri_takatou": {
        "nome": "Yogiri Takatou",
        "origem": "My Instant Death Ability is So Overpowered",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 7,
        "max_star": 7,
        "hp": 560,
        "atk": 300,
        "matk": 0,
        "def": 30,
        "spd": 45,
        "crt": 25,
        "habilidade": {
            "nome": "Morte Instantânea Conceitual",
            "descricao": "Yogiri dita o fim do alvo. Desfere um golpe de 400% de ATK de acerto crítico garantido que possui 40% de chance de matar instantaneamente."
        },
        "evolucoes": {
            7: {
                "nome": "O Fim de Todas as Coisas",
                "atk": 50,
                "spd": 20,
                "descricao": "Seu poder mata até mesmo conceitos de ressurreição. Inimigos derrotados por Yogiri não podem ser revividos de forma alguma durante o combate."
            }
        }
    },

    # =========================283
    "haruhi_suzumiya": {
        "nome": "Haruhi Suzumiya",
        "origem": "The Melancholy of Haruhi Suzumiya",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 7,
        "max_star": 7,
        "hp": 470,
        "atk": 50,
        "matk": 85,
        "def": 35,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Desejo Inconsciente",
            "descricao": "Sua mente cria realidades sem perceber. Ativa um efeito aleatório muito forte: cura total do grupo, dano de área massivo ou imunidade à rodada."
        },
        "evolucoes": {
            7: {
                "nome": "Reconstrução do Universo",
                "atk": 20,
                "spd": 10,
                "descricao": "A deusa reconstrói as leis físicas locais. Concede de forma permanente +100% de ATK, MATK e SPD para todo o grupo de combate."
            }
        }
    },

    # =========================284
    "sailor_cosmos": {
        "nome": "Sailor Cosmos",
        "origem": "Sailor Moon",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 7,
        "max_star": 7,
        "hp": 685,
        "atk": 25,
        "matk": 92,
        "def": 70,
        "spd": 38,
        "crt": 15,
        "habilidade": {
            "nome": "Cristal Cosmos Protetor",
            "descricao": "Cria um campo de força cósmico brilhante. Todos os aliados ganham um escudo equivalente a 80% do HP máximo de Cosmos por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Luz Eterna da Esperança",
                "atk": 15,
                "spd": 12,
                "descricao": "Sua luz purifica a maldade dimensional. Limpa todos os debuffs aliados e cura a equipe em 50% do HP máximo no início de cada ação."
            }
        }
    },

    # =========================285
    "hajun": {
        "nome": "Hajun",
        "origem": "Dies Irae",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 7,
        "max_star": 7,
        "hp": 495,
        "atk": 108,
        "matk": 20,
        "def": 50,
        "spd": 28,
        "crt": 18,
        "habilidade": {
            "nome": "Grande Iluminação Esmagadora",
            "descricao": "Um golpe carregado de puro ódio que quebra qualquer estrutura. Causa 420% de ATK e reduz a DEF física e mágica do alvo em 50% por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Muzan: Lei do Egocentrismo",
                "atk": 45,
                "spd": 8,
                "descricao": "Seu narcisismo distorce o universo. Ganha +50% de ATK adicional para cada oponente vivo presente no campo de batalha."
            }
        }
    },

    # =========================286
    "accelerator": {
        "nome": "Accelerator",
        "origem": "Toaru Majutsu no Index",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 7,
        "max_star": 7,
        "hp": 680,
        "atk": 90,
        "matk": 90,
        "def": 58,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Escudo Vetorial Absoluto",
            "descricao": "Calcula e desvia o fluxo físico e mágico. Reflete 60% de todo o dano físico e mágico recebido de volta para quem o atacou."
        },
        "evolucoes": {
            7: {
                "nome": "Asas Brancas Divinas",
                "atk": 300,
                "spd": 20,
                "descricao": "Desperta as asas de energia pura. Fica completamente intocável (imunidade a tudo) por 4 turnos e aumenta seu MATK em 200%."
            }
        }
    },

    # =========================287
    "jin_mori": {
        "nome": "Jin Mori",
        "origem": "The God of High School",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 7,
        "max_star": 7,
        "hp": 555,
        "atk": 200,
        "matk": 30,
        "def": 50,
        "spd": 42,
        "crt": 50,
        "habilidade": {
            "nome": "Chute Triplo do Dragão Azul",
            "descricao": "Desfere três chutes sequenciais velocíssimos com fúria. Cada chute ignora 50% da defesa e reduz a velocidade (SPD) do alvo em 30%."
        },
        "evolucoes": {
            7: {
                "nome": "Jecheondaeseong: O Rei Macaco",
                "atk": 500,
                "spd": 20,
                "descricao": "Assume sua forma divina de herdeiro dos céus. Invoca seu báculo Yeoui causando 350% de ATK em área de acerto crítico garantido."
            }
        }
    },

    # =========================288
    "ryougi_shiki": {
        "nome": "Ryougi Shiki",
        "origem": "Kara no Kyoukai",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 7,
        "max_star": 7,
        "hp": 450,
        "atk": 195,
        "matk": 20,
        "def": 28,
        "spd": 46,
        "crt": 50,
        "habilidade": {
            "nome": "Percepção de Morte Linear",
            "descricao": "Shiki enxerga as linhas de morte no corpo do oponente. Desfere um corte inevitável que ignora 100% de defesa e reduz a cura recebida pelo alvo à metade."
        },
        "evolucoes": {
            7: {
                "nome": "Vazio: Lâmina de Contradição",
                "atk": 40,
                "spd": 25,
                "descricao": "Sua conexão com o vazio a torna mortal. Seus ataques normais passam a ter 30% de chance de executar inimigos normais instantaneamente."
            }
        }
    },

    # =========================289
    "lambdadelta": {
        "nome": "Lambdadelta",
        "origem": "Umineko no Naku Koro ni",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 7,
        "max_star": 7,
        "hp": 365,
        "atk": 30,
        "matk": 140,
        "def": 32,
        "spd": 34,
        "crt": 18,
        "habilidade": {
            "nome": "Poder da Certeza Absoluta",
            "descricao": "Sua magia é matematicamente garantida. Seus ataques mágicos nunca erram o alvo e sempre causam dano máximo, ignorando evasões ou barreiras."
        },
        "evolucoes": {
            7: {
                "nome": "Doce Labirinto Sem Fim",
                "atk": 300,
                "spd": 15,
                "descricao": "Prende o oponente em um redemoinho açucarado. Deixa o alvo preso (Stun) por 1 turno e aplica o debuff de fraqueza e lentidão severa por 3 turnos."
            }
        }
    },
# =========================290
    "benimaru_tensura": {
        "nome": "Benimaru",
        "origem": "Tensei Shitara Slime Datta Ken",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 82,
        "matk": 50,
        "def": 28,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Chamas do Purgatório (Hell Flare)",
            "descricao": "Benimaru condensa calor absoluto em uma cúpula de fogo negro. Causa 180% de ATK e aplica Queimadura de Chamas Negras em área que ignora 30% da DEF mágica."
        },
        "evolucoes": {
            7: {
                "nome": "General Espiritual dos Dragões (Rei Demônio)",
                "descricao": "Benimaru desperta como lorde demônio e comandante supremo. Seus ataques físicos passam a ignorar 30% da defesa do alvo e ele ressurge uma vez com 20% de HP envolto em chamas imperiais."
            }
        }
    },
# =========================291
    "darkness_konosuba": {
        "nome": "Darkness",
        "origem": "KonoSuba",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 160,
        "atk": 15,
        "matk": 0,
        "def": 65,
        "spd": 12,
        "crt": 5,
        "habilidade": {
            "nome": "Delícia Masoquista (Taunt Corporal)",
            "descricao": "Darkness provoca os oponentes de forma vergonhosa. Aplica provocação absoluta (Taunt) em todos os inimigos, aumenta sua DEF em 50% e cura-se em 15% de todo o dano que receber por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Sacrifício Inquebrável da Cruzada",
                "descricao": "O auge da resistência física e mental da família Dustiness. Darkness redireciona 100% do dano de golpes fatais destinados a aliados para si mesma com 30% de mitigação adicional. Ela torna-se imune a atordoamento (Stun)."
            }
        }
    },
    # =========================292
    "dio_brando": {
        "nome": "Dio Brando",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 70,
        "matk": 45,
        "def": 28,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "O Mundo (The World)",
            "descricao": "Dio paralisa o fluxo temporal. Impede o oponente mais veloz de agir por 1 turno e desfere um golpe de 180% de ATK que ignora a defesa física."
        },
        "evolucoes": {
            7: {
                "nome": "Sangue Vampírico de Joestar",
                "descricao": "Seu corpo regenera sugando os fortes. Se o HP cair abaixo de 30%, rouba instantaneamente 40% do HP do inimigo mais saudável e ganha +30% de ATK."
            }
        }
    },

    # =========================293
    "barba_negra": {
        "nome": "Barba Negra",
        "origem": "One Piece",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 145,
        "atk": 80,
        "matk": 40,
        "def": 35,
        "spd": 15,
        "crt": 10,
        "habilidade": {
            "nome": "Yami Yami no Mi: Buraco Negro",
            "descricao": "Gera uma gravidade infinita de escuridão que suga tudo. Causa 150% de ATK em área, limpa todos os buffs dos inimigos e impede-os de receber novos bônus por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Gura Gura no Mi: Terremoto Absoluto",
                "descricao": "Dispara ondas de choque que quebram o ar. Causa 250% de ATK em área e reduz permanentemente a defesa (DEF) de todos os inimigos em 40%."
            }
        }
    },

    # =========================294
    "madara": {
        "nome": "Madara Uchiha",
        "origem": "Naruto",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 85,
        "matk": 60,
        "def": 30,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Tengai Shinsei (Meteoro Cósmico)",
            "descricao": "Invoca meteoros colossais que rasgam a atmosfera. Causa 220% de MATK em área e quebra permanentemente 35% da defesa mágica da equipe inimiga."
        },
        "evolucoes": {
            7: {
                "nome": "Limbo: Hengoku",
                "descricao": "Invoca clones invisíveis em outra dimensão. Concede a Madara +45% de esquiva (dodge) absoluta e desfere contra-ataques físicos de 120% automaticamente ao desviar."
            }
        }
    },

    # =========================295
    "griffith": {
        "nome": "Griffith",
        "origem": "Berserk",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 75,
        "matk": 55,
        "def": 28,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Manipulação Causal de Femto",
            "descricao": "Griffith dobra o espaço ao seu redor. Atrai todos os ataques inimigos para si (Taunt), mas reduz todo o dano recebido em 50% e reflete debuffs."
        },
        "evolucoes": {
            7: {
                "nome": "O Eclipse e a Mão de Deus",
                "descricao": "Sacrifica seus próprios soldados por poder. Sempre que um aliado é derrotado na arena, Griffith recupera 100% de seu HP e ganha +45% de ATK definitivo."
            }
        }
    },

    # =========================296
    "doflamingo": {
        "nome": "Donquixote Doflamingo",
        "origem": "One Piece",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 60,
        "matk": 35,
        "def": 24,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Parasite: Controle de Fios",
            "descricao": "Lança fios parasitas no sistema nervoso do adversário. Controla o inimigo com maior ATK, forçando-o a atacar seus próprios aliados por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Gaiola de Fios (Birdcage)",
                "descricao": "Cria uma cúpula de fios cortantes sobre a arena. Causa 15% do HP atual de todos os inimigos como dano contínuo (DoT) a cada rodada."
            }
        }
    },

    # =========================297
    "all_for_one": {
        "nome": "All For One",
        "origem": "Boku no Hero Academia",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 82,
        "matk": 65,
        "def": 32,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Roubo de Individualidade",
            "descricao": "Drena a força existencial do alvo. Causa 150% de MATK, rouba 25% do ATK e da DEF do oponente por 2 turnos e transfere os buffs dele para si."
        },
        "evolucoes": {
            7: {
                "nome": "Canhão de Ar e Impacto Combinado",
                "descricao": "Une dezenas de individualidades em um punho deformado. Desfere um impacto de 280% de ATK que destrói barreiras e atordoa o alvo por 1 turno."
            }
        }
    },

    # =========================298
    "sukuna": {
        "nome": "Ryomen Sukuna",
        "origem": "Jujutsu Kaisen",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 60,
        "matk": 75,
        "def": 28,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Clivagem e Desmantelar",
            "descricao": "Aplica cortes invisíveis e severos. Causa 180% de MATK e aplica Sangramento pesado por 3 turnos, reduzindo a eficácia de curas do alvo em 50%."
        },
        "evolucoes": {
            7: {
                "nome": "Santuário Malevolente",
                "descricao": "Expande seu domínio fatiando a arena inteira. Causa 150% de MATK em todos os inimigos por rodada durante 2 turnos, reduzindo a DEF deles pela metade."
            }
        }
    },

    # =========================299
    "mahito": {
        "nome": "Mahito",
        "origem": "Jujutsu Kaisen",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 35,
        "matk": 68,
        "def": 22,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Transfiguração Ociosa",
            "descricao": "Muda o formato da alma do inimigo com o toque. Causa 160% de MATK que ignora a defesa física e possui 25% de chance de petrificar/atordoar por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Auto-Transfiguração de Combate",
                "descricao": "Deforma e endurece seu próprio corpo. Ganha +40% de DEF, imunidade completa a debuffs de veneno/sangramento e recupera 12% de HP por turno."
            }
        }
    },

    # =========================300
    "petelgeuse": {
        "nome": "Petelgeuse Romanee-Conti",
        "origem": "Re:Zero",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 15,
        "matk": 55,
        "def": 18,
        "spd": 16,
        "crt": 10,
        "habilidade": {
            "nome": "Mãos Invisíveis da Autoridade",
            "descricao": "Invoca braços negros indetectáveis que espancam a vítima. Causa 140% de MATK e reduz a SPD e a precisão do oponente em 30% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Loucura Devota de Amor",
                "descricao": "Sua insanidade o torna implacável. Seus ataques mágicos ganham +25% de chance crítica e, se causarem crítico, removem 1 buff do oponente."
            }
        }
    },

    # =========================301
    "orochimaru": {
        "nome": "Orochimaru",
        "origem": "Naruto",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 40,
        "matk": 65,
        "def": 25,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Reencarnação da Serpente Viva",
            "descricao": "Transfere sua consciência para evitar a morte. Cura-se em 35% de seu MATK e aplica veneno pesado no oponente que o atacou física ou magicamente."
        },
        "evolucoes": {
            5: {
                "nome": "Invocação: Edo Tensei",
                "descricao": "Ressuscita combatentes do passado. Invoca um lacaio de terra com 50% de seus atributos que aplica provocação absoluta (Taunt) nos inimigos."
            }
        }
    },

    # =========================302
    "naraku": {
        "nome": "Naraku",
        "origem": "InuYasha",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 30,
        "matk": 68,
        "def": 28,
        "spd": 20,
        "crt": 10,
        "habilidade": {
            "nome": "Miasma Venenoso do Pântano",
            "descricao": "Libera uma fumaça ácida letal e corrosiva. Causa 140% de MATK a todos os oponentes e aplica Veneno Crítico (anula cura) por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Barreira de Energia Espiritual",
                "descricao": "Gera um escudo impenetrável de energia escura. Absorve todo o dano recebido até um limite de 50% de seu HP máximo e reflete efeitos negativos."
            }
        }
    },

    # =========================303
    "kaguya_otsutsuki": {
        "nome": "Kaguya Otsutsuki",
        "origem": "Naruto",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 40,
        "matk": 85,
        "def": 32,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Amenominaka (Dobra Dimensional)",
            "descricao": "Transporta o combate para dimensões de gravidade ou magma. Causa 200% de MATK em área e reduz a SPD de todos os inimigos em 50%."
        },
        "evolucoes": {
            7: {
                "nome": "Ossos de Cinza Assassinos de Tudo",
                "descricao": "Dispara estacas cinzentas que corroem as células ao toque. Causa dano verdadeiro massivo e possui 20% de chance de execução instantânea."
            }
        }
    },

    # =========================304
    "dabi": {
        "nome": "Dabi",
        "origem": "Boku no Hero Academia",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 25,
        "matk": 70,
        "def": 20,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Chamas Azuis do Purgatório",
            "descricao": "Libera labaredas azuis que queimam com intensidade extrema. Causa 160% de MATK a até 2 oponentes e aplica Queimadura Pesada por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Cremação Suicida",
                "descricao": "Eleva as chamas além do suportado pelo seu próprio corpo. Ganha +45% de MATK por 3 turnos, mas perde 5% do HP atual ao final de cada rodada."
            }
        }
    },

    # =========================305
    "crocodile": {
        "nome": "Crocodile",
        "origem": "One Piece",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 30,
        "matk": 62,
        "def": 24,
        "spd": 20,
        "crt": 12,
        "habilidade": {
            "nome": "Desert Spada: Lâmina de Areia",
            "descricao": "Dispara lâminas de areia cortante cavando fendas no solo. Causa 150% de MATK e reduz a velocidade de ação de todos os alvos em 25%."
        },
        "evolucoes": {
            5: {
                "nome": "Desidratação de Areia Absoluta",
                "descricao": "Suga a umidade do corpo do inimigo. Causa 180% de MATK, absorve 40% do dano causado como cura e remove os buffs de velocidade do alvo."
            }
        }
    },

    # =========================306
    "father": {
        "nome": "Father",
        "origem": "Fullmetal Alchemist",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 30,
        "matk": 80,
        "def": 32,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Alquimia do Homúnculo Original",
            "descricao": "Reescreve a matéria ao redor sem esforço ou círculos. Causa 170% de MATK a todos os oponentes, ignorando escudos mágicos ou de terra."
        },
        "evolucoes": {
            7: {
                "nome": "Pedra Filosofal de Almas",
                "descricao": "Usa as almas da pedra para anular a morte. Se o seu HP for zerado, consome a pedra para reviver com 50% de HP e barreira física total."
            }
        }
    },

    # =========================307
    "yhwach": {
        "nome": "Yhwach",
        "origem": "Bleach",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 60,
        "matk": 82,
        "def": 28,
        "spd": 26,
        "crt": 18,
        "habilidade": {
            "nome": "The Almighty: Futuro Escrito",
            "descricao": "Observa e altera as possibilidades futuras. Cancela completamente a próxima ação ofensiva do inimigo mais rápido e aumenta seu próprio MATK em 30%."
        },
        "evolucoes": {
            7: {
                "nome": "Sankt Altar: Roubo de Poder",
                "descricao": "Rouba as habilidades ativas e o poder do oponente. Causa 220% de MATK e silencia o alvo (impede o uso de magias) por 2 turnos."
            }
        }
    },

    # =========================308
    "muzan_kibutsuji": {
        "nome": "Muzan Kibutsuji",
        "origem": "Demon Slayer",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 60,
        "matk": 75,
        "def": 32,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Injeção de Sangue Corrosivo",
            "descricao": "Injeta seu sangue tóxico e celular no alvo. Causa 180% de MATK, aplica Veneno Crítico (anula curas) por 3 turnos e reduz o ATK do inimigo em 30%."
        },
        "evolucoes": {
            7: {
                "nome": "Chicotes de Carne Biológicos",
                "descricao": "Gera apêndices espinhosos ultra velozes. Ataca até 3 oponentes de forma simultânea por rodada e cura-se em 30% de todo o dano causado."
            }
        }
    },

    # =========================309
    "meruem": {
        "nome": "Meruem",
        "origem": "Hunter x Hunter",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 195,
        "atk": 70,
        "matk": 20,
        "def": 50,
        "spd": 28,
        "crt": 10,
        "habilidade": {
            "nome": "Síntese de Aura Quimera",
            "descricao": "Meruem absorve energia fortificando a sua carcaça natural. Atrai provocação de todos (Taunt) e aumenta a sua DEF física e mágica em 45% por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Forma Mítica Desperta",
                "descricao": "Seu corpo assume asas e canhões de fótons. Se sofrer dano crítico, absorve 50% do impacto convertendo-o em barreira protetora para o próximo hit."
            }
        }
    },

    # =========================310
    "hidan": {
        "nome": "Hidan",
        "origem": "Naruto",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 150,
        "atk": 42,
        "matk": 15,
        "def": 38,
        "spd": 14,
        "crt": 10,
        "habilidade": {
            "nome": "Ritual de Sangue Jashin",
            "descricao": "Hidan lambe o sangue do inimigo e desenha o círculo no chão. Atrai ataques (Taunt) e reflete 40% de todo o dano recebido de volta ao agressor por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Imortalidade Amaldiçoada",
                "descricao": "Seu corpo simplesmente se recusa a morrer. Sempre que sofrer um golpe que seria fatal, permanece ativo com exatamente 1 HP por 2 rodadas."
            }
        }
    },

    # =========================311
    "zeldris": {
        "nome": "Zeldris",
        "origem": "Nanatsu no Taizai",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 160,
        "atk": 55,
        "matk": 25,
        "def": 48,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Nebula Ominosa (Ominous Nebula)",
            "descricao": "Cria um vórtice de vácuo gravitacional absoluto. Atrai e provoca todos os oponentes, anula ataques à distância e reduz a SPD deles em 30% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Mandamento da Piedade",
                "descricao": "Castiga a traição ou a fuga. Inimigos que tentarem recuar ou usar habilidades de fuga sofrem 150% de dano verdadeiro e são silenciados por 1 turno."
            }
        }
    },

    # =========================312
    "ulquiorra": {
        "nome": "Ulquiorra Cifer",
        "origem": "Bleach",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 155,
        "atk": 58,
        "matk": 35,
        "def": 42,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Regeneração de Alta Velocidade",
            "descricao": "Foca seus recursos espirituais na recomposição instantânea de feridas. Cura-se em 40% de todo o seu HP perdido de forma imediata."
        },
        "evolucoes": {
            5: {
                "nome": "Segunda Etapa: Lanza de Relámpago",
                "descricao": "Gera e arremessa sua lança de energia verde condensada. Desfere um impacto de 200% de MATK em área que quebra barreiras e escudos."
            }
        }
    },

    # =========================313
    "regulus_corneas": {
        "nome": "Regulus Corneas",
        "origem": "Re:Zero",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 180,
        "atk": 60,
        "matk": 30,
        "def": 58,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Autoridade da Ganância: Imutabilidade",
            "descricao": "Regulus para o seu tempo pessoal, blindando-se do universo. Concede imunidade absoluta a qualquer dano, debuff ou morte instantânea por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "O Sopro de Cascalho Silencioso",
                "descricao": "Arremessa pequenas pedras paradas no tempo. Desfere um ataque físico de 180% que ignora 100% da defesa e escudos do inimigo."
            }
        }
    },

    # =========================314
    "pain": {
        "nome": "Pain (Tendo)",
        "origem": "Naruto",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 175,
        "atk": 55,
        "matk": 45,
        "def": 52,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Shinra Tensei (Repulsão Divina)",
            "descricao": "Repele violentamente qualquer perigo físico ou mágico. Desvia os ataques em área sofridos por si ou aliados e joga os inimigos para o fim da fila de ação."
        },
        "evolucoes": {
            7: {
                "nome": "Chibaku Tensei (Atração Planetária)",
                "descricao": "Cria um núcleo de atração gravitacional massiva. Prende e atordoa (Stun) todos os inimigos por 1 turno inteiro, destruindo defesas e escudos."
            }
        }
    },

    # =========================315
    "bondrewd": {
        "nome": "Bondrewd",
        "origem": "Made in Abyss",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 150,
        "atk": 48,
        "matk": 30,
        "def": 45,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Cartuchos de Bênção",
            "descricao": "Consome um cartucho para neutralizar os efeitos da maldição. Restaura 25% de seu HP máximo e aumenta a sua defesa em 35% por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Receptor de Consciência: Zoaholic",
                "descricao": "Seu espírito divide-se por corpos. Se Bondrewd for derrotado, ele transfere sua consciência para o herói aliado mais saudável, mantendo a luta ativa."
            }
        }
    },

    # =========================316
    "shigaraki": {
        "nome": "Tomura Shigaraki",
        "origem": "Boku no Hero Academia",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 145,
        "atk": 62,
        "matk": 25,
        "def": 40,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Decaimento de Área",
            "descricao": "Desintegra o solo e a matéria física ao tocar. Causa 140% de ATK e reduz a defesa do inimigo em 50% por 3 turnos devido ao desgaste."
        },
        "evolucoes": {
            5: {
                "nome": "Hiper-Regeneração Biológica",
                "descricao": "Sua carne desintegrada reconstrói-se instantaneamente. Passa a recuperar 12% de seu HP máximo ao início de cada rodada de combate na arena."
            }
        }
    },

    # =========================317
    "freeza": {
        "nome": "Freeza",
        "origem": "Dragon Ball Z",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 180,
        "atk": 75,
        "matk": 35,
        "def": 48,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Fisiologia de Sobrevivência Cósmica",
            "descricao": "Sua carcaça resiste mesmo a fatiamentos ou vácuo. Reduz todo dano físico sofrido em 40% e reflete 20% do impacto físico recebido."
        },
        "evolucoes": {
            7: {
                "nome": "Forma Dourada: Golden Freeza",
                "descricao": "Ativa sua forma dourada mítica de puro orgulho. Aumenta sua DEF e seu ATK em 50% por 3 turnos e paralisa atacantes fisicamente."
            }
        }
    },

    # =========================318
    "coyote_starrk": {
        "nome": "Coyote Starrk",
        "origem": "Bleach",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 65,
        "matk": 40,
        "def": 24,
        "spd": 35,
        "crt": 25,
        "habilidade": {
            "nome": "Cero Metralhadora",
            "descricao": "Dispara incontáveis Ceros azuis em rajadas de suas pistolas duplas. Causa 180% de ATK físico a até 3 inimigos de forma aleatória."
        },
        "evolucoes": {
            5: {
                "nome": "Los Lobos: Matilha de Almas",
                "descricao": "Invoca lobos que caçam de forma autônoma. Os lobos explodem ao toque causando dano contínuo e drenando a energia mágica do inimigo mais rápido."
            }
        }
    },

    # =========================319
    "envy": {
        "nome": "Envy",
        "origem": "Fullmetal Alchemist",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 45,
        "matk": 15,
        "def": 20,
        "spd": 30,
        "crt": 20,
        "habilidade": {
            "nome": "Metamorfose Infiltradora",
            "descricao": "Envy copia a aparência de um aliado inimigo. Fica Oculto (esquiva aumentada) por 1 turno e seu próximo golpe causa o dobro do dano tático."
        },
        "evolucoes": {
            5: {
                "nome": "Forma Verdadeira de Quimera",
                "descricao": "Assume sua forma colossal e asquerosa de homúnculo. Causa 200% de ATK, atordoa o oponente atingido e reduz a precisão dele pela metade."
            }
        }
    },

    # =========================320
    "elsa_granhiert": {
        "nome": "Elsa Granhiert",
        "origem": "Re:Zero",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 100,
        "atk": 72,
        "matk": 0,
        "def": 18,
        "spd": 38,
        "crt": 25,
        "habilidade": {
            "nome": "Fatiadora de Entranhas",
            "descricao": "Elsa avança mirando diretamente no estômago do alvo. Causa 180% de ATK e aplica Sangramento Crítico inevitável por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Evasão Vampírica Sobrenatural",
                "descricao": "Sua flexibilidade felina evita os golpes. Concede +40% de esquiva (dodge) absoluta e desfere contra-ataques físicos de 120% automaticamente ao desviar."
            }
        }
    },

    # =========================321
    "twice": {
        "nome": "Twice",
        "origem": "Boku no Hero Academia",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 95,
        "atk": 50,
        "matk": 10,
        "def": 16,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Multiplicação Caótica",
            "descricao": "Cria clones idênticos e falantes para confundir o inimigo. Concede +30% de esquiva (dodge) e divide o dano sofrido com as duplicatas."
        },
        "evolucoes": {
            5: {
                "nome": "Marcha do Homem Só",
                "descricao": "Gera uma horda imparável de clones em massa. Todos os inimigos perdem 30% de precisão e sofrem 140% de ATK físico por rodada de ação."
            }
        }
    },

    # =========================322
    "buggy": {
        "nome": "Buggy, o Palhaço",
        "origem": "One Piece",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 42,
        "matk": 0,
        "def": 20,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Bara Bara no Mi: Divisão Corporal",
            "descricao": "Buggy separa seus membros no ar. Fica completamente imune a cortes, perfurações e efeitos de sangramento físico por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Muggy Ball: Canhão de Sapatos",
                "descricao": "Dispara micro-bombas altamente destrutivas de seu sapato. Causa 220% de ATK físico em área e aplica Queimadura por 2 turnos."
            }
        }
    },

    # =========================323
    "team_rocket": {
        "nome": "Equipe Rocket",
        "origem": "Pokémon",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 35,
        "matk": 25,
        "def": 18,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Armadilha de Rede Elétrica",
            "descricao": "Jessie, James e Meowth preparam uma armadilha mecânica. Causa paralisia (Stun) de 1 turno em até 2 oponentes e drena 20% do ouro deles."
        },
        "evolucoes": {
            5: {
                "nome": "Decolando na Velocidade da Luz!",
                "descricao": "Em situações desesperadoras, fogem de balão. Reduz todo o dano recebido pelo esquadrão em 40% por 2 rodadas completas."
            }
        }
    },

    # =========================324
    "mama_isabella": {
        "nome": "Isabella (Mama)",
        "origem": "The Promised Neverland",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 55,
        "matk": 25,
        "def": 22,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Rastreamento Frio de Fugitivos",
            "descricao": "Encontra o paradeiro exato de quem tenta fugir. Silencia o inimigo mais veloz por 2 turnos e reduz a SPD dele à metade."
        },
        "evolucoes": {
            5: {
                "nome": "O Olhar Gelado do Orfanato",
                "descricao": "Sua postura fria e calculista apavora a equipe oponente. Todos os inimigos sofrem debuff de medo permanente (causam 25% a menos de dano)."
            }
        }
    },
    # =========================325
    "zeref_dragneel": {
        "nome": "Zeref Dragneel",
        "origem": "Fairy Tail",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 20,
        "matk": 82,
        "def": 26,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Magia Negra de Ankhselam",
            "descricao": "Zeref libera uma onda de morte inevitável que drena a vida. Causa 150% de MATK em área e aplica um DoT (Dano por Turno) de 80 de dano verdadeiro que ignora 100% de defesa por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Conjurador de Demônios",
                "descricao": "Invoca uma horda de demônios do Livro de Zeref. Distribui um escudo de escuridão para todos os aliados equivalente a 30% do HP de Zeref e silencia as magias inimigas por 1 turno."
            }
        }
    },

    # =========================326
    "toguro_ototo": {
        "nome": "Toguro Ototo (100%)",
        "origem": "Yu Yu Hakusho",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 185,
        "atk": 70,
        "matk": 0,
        "def": 55,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Brutalidade Muscular",
            "descricao": "Toguro expande seus músculos ao limite extremo de 100%. Reduz o dano de ataques críticos recebidos a zero e reflete 25% de todo o dano de investidas corpo a corpo por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Absorção de Almas",
                "descricao": "Sua mera presença colossal drena energia dos fracos. Suga passivamente 5% do HP atual de todos os oponentes a cada turno para regenerar o seu próprio HP."
            }
        }
    },

    # =========================327
    "kars_supremo": {
        "nome": "Kars (Forma Suprema)",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 180,
        "atk": 65,
        "matk": 30,
        "def": 50,
        "spd": 32,
        "crt": 12,
        "habilidade": {
            "nome": "Adaptação Biológica",
            "descricao": "Kars adapta suas células ao ataque recebido. Sempre que sofre um debuff (como queima ou veneno), ele o remove instantaneamente e ganha imunidade contra esse status pelo resto do combate."
        },
        "evolucoes": {
            7: {
                "nome": "Imortalidade do Ápice",
                "descricao": "Se o HP de Kars for zerado, ele revive uma única vez com 50% de HP e ganha imunidade total a qualquer tipo de dano por 1 turno completo."
            }
        }
    },

    # =========================328
    "nnoitra_gilga": {
        "nome": "Nnoitra Gilga",
        "origem": "Bleach",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 155,
        "atk": 58,
        "matk": 0,
        "def": 48,
        "spd": 16,
        "crt": 10,
        "habilidade": {
            "nome": "O Hierro Mais Duro",
            "descricao": "Sua pele espiritual de Quinta Espada resiste ao desgaste de cortes de espadas. Cria um escudo físico gigantesco permanente equivalente a 40% de sua vida máxima."
        },
        "evolucoes": {
            5: {
                "nome": "Santa Teresa",
                "descricao": "Saca seus quatro braços extras de combate. Desfere um contra-ataque físico violento de 120% de dano sempre que um inimigo quebrar o seu escudo protetor."
            }
        }
    },

    # =========================329
    "muscular_mha": {
        "nome": "Muscular",
        "origem": "Boku no Hero Academia",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 140,
        "atk": 52,
        "matk": 0,
        "def": 38,
        "spd": 14,
        "crt": 8,
        "habilidade": {
            "nome": "Fibras de Carne Blindadas",
            "descricao": "Cobre o corpo com milhares de fibras musculares expostas. Aumenta sua DEF física em 60% e o seu HP máximo em 20% durante 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Pancada Devastadora",
                "descricao": "Usa o peso de seus músculos blindados para esmagar o solo. Causa 160% de ATK e atordoa (Stun) o alvo principal por 1 turno."
            }
        }
    },

    # =========================330
    "overgrown_rover": {
        "nome": "Overgrown Rover",
        "origem": "One Punch Man",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 165,
        "atk": 35,
        "matk": 55,
        "def": 45,
        "spd": 22,
        "crt": 5,
        "habilidade": {
            "nome": "Guarda Canina Imperial",
            "descricao": "O cachorro gigante protege as frentes da associação. Recebe provocação total (Taunt) e reduz em 30% o dano de ataques em área recebidos pelos seus aliados."
        },
        "evolucoes": {
            5: {
                "nome": "Esferas de Energia Consecutivas",
                "descricao": "Dispara rajadas de calor concentrado da boca. Causa 140% de MATK a alvos aleatórios e aplica Queimadura por 2 turnos."
            }
        }
    },

    # =========================331
    "hisoka_morow": {
        "nome": "Hisoka Morow",
        "origem": "Hunter x Hunter",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 74,
        "matk": 40,
        "def": 24,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Bungee Gum",
            "descricao": "Hisoka anexa sua goma elástica e grudenta no oponente mais rápido, atrasando o turno de ação dele em 50% por 2 turnos e roubando sua velocidade."
        },
        "evolucoes": {
            7: {
                "nome": "Textura Surpresa",
                "descricao": "Engana os sentidos do inimigo ficando oculto (invisível/esquiva de 50% extra) por 2 turnos. Seu primeiro ataque saindo da ocultação causa dano crítico triplicado."
            }
        }
    },

    # =========================332
    "illumi_zoldyck": {
        "nome": "Illumi Zoldyck",
        "origem": "Hunter x Hunter",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 65,
        "matk": 30,
        "def": 22,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Agulhas de Lavagem Cerebral",
            "descricao": "Insere agulhas hipnóticas na cabeça da vítima. Silencia o oponente por 2 turnos e o força a usar um ataque básico contra a sua própria equipe."
        },
        "evolucoes": {
            5: {
                "nome": "Disfarce Sem Rosto",
                "descricao": "Altera sua estrutura facial para se mesclar às sombras. Fica imune a qualquer ataque direcionado por 1 turno e limpa as ameaças voltadas a si."
            }
        }
    },

    # =========================333
    "sonic_opm": {
        "nome": "Speed-o'-Sound Sonic",
        "origem": "One Punch Man",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 95,
        "atk": 52,
        "matk": 10,
        "def": 18,
        "spd": 44,
        "crt": 18,
        "habilidade": {
            "nome": "Velocidade Sônica",
            "descricao": "Move-se tão rápido que cria miragens. Concede +30% de SPD e +20% de evasão (dodge) para si mesmo durante 3 rodadas de ação."
        },
        "evolucoes": {
            5: {
                "nome": "Shurikens Explosivas",
                "descricao": "Arremessa uma chuva de projéteis velozes. Causa 150% de ATK físico na retaguarda inimiga e quebra as defesas dos atiradores oponentes."
            }
        }
    },

    # =========================334
    "kurome_akame": {
        "nome": "Kurome",
        "origem": "Akame ga Kill",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 68,
        "matk": 0,
        "def": 20,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Yatsufusa: Coleção de Cadáveres",
            "descricao": "Ao desferir o golpe de misericórdia e derrotar um inimigo, ressuscita-o instantaneamente como um fantasma aliado com 30% de HP para lutar sob seu controle."
        },
        "evolucoes": {
            5: {
                "nome": "Corte de Drogas Estimulantes",
                "descricao": "Consome pílulas corporais que aumentam os batimentos cardíacos. Concede turno extra de ataque imediato após desferir um golpe crítico."
            }
        }
    },

    # =========================335
    "deidara_naruto": {
        "nome": "Deidara",
        "origem": "Naruto",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 62,
        "matk": 40,
        "def": 20,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Argila Explosiva C3",
            "descricao": "Molda pássaros de argila que explodem sob o oponente. Causa 180% de dano em área após 1 turno de preparação (efeito bomba-relógio)."
        },
        "evolucoes": {
            5: {
                "nome": "C4 Karura: Micro-Bombas",
                "descricao": "Libera uma nuvem invisível de bombas celulares. Causa dano contínuo (DoT) massivo de 100 de dano verdadeiro que ignora qualquer tipo de escudo ou barreira mágica por 2 turnos."
            }
        }
    },

    # =========================336
    "enel_onepiece": {
        "nome": "Enel",
        "origem": "One Piece",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 30,
        "matk": 78,
        "def": 22,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "El Thor: Julgamento Relâmpago",
            "descricao": "Dispara um feixe colossal de eletricidade diretamente do céu sobre a retaguarda inimiga. Causa 190% de MATK e paralisa (Stun) o alvo por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Amaru: 200M Volts",
                "descricao": "Assume sua forma gigante de eletricidade viva. Aumenta o dano de todas as suas magias de raio em 40% e fica completamente imune a lentidão."
            }
        }
    },

    # =========================337
    "lille_barro": {
        "nome": "Lille Barro",
        "origem": "Bleach",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 82,
        "matk": 30,
        "def": 24,
        "spd": 30,
        "crt": 20,
        "habilidade": {
            "nome": "Perfuração Perfeita",
            "descricao": "Dispara seu rifle cuja bala não viaja o espaço, simplesmente se materializa no alvo. Causa 180% de ATK, ignora 100% de defesa física e destrói escudos."
        },
        "evolucoes": {
            7: {
                "nome": "Jilliel: Forma Divina de Luz",
                "descricao": "Assume a forma de um anjo de luz sagrada. Fica imune a ataques físicos normais e seus disparos causam dano duplo em oponentes da classe Tank."
            }
        }
    },

    # =========================338
    "hol_horse_jojo": {
        "nome": "Hol Horse",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 48,
        "matk": 10,
        "def": 18,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "O Imperador (The Emperor)",
            "descricao": "Sua arma é o seu próprio Stand, permitindo controlar a trajetória das balas. Seus ataques nunca erram e possuem +30% de chance crítica."
        },
        "evolucoes": {
            5: {
                "nome": "Parceria Covarde",
                "descricao": "Ataca pelas costas enquanto o inimigo está distraído. Causa dano físico dobrado (200% de ATK) em alvos atordoados ou sob efeito de provocação."
            }
        }
    },

    # =========================339
    "bambietta": {
        "nome": "Bambietta Basterbine",
        "origem": "Bleach",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 35,
        "matk": 68,
        "def": 20,
        "spd": 26,
        "crt": 12,
        "habilidade": {
            "nome": "Explosão de Reishi",
            "descricao": "Transforma tudo o que seu disparo toca em uma bomba ativa. Se o oponente tentar usar um escudo, a defesa explode na cara dele causando dano reverso de 150%."
        },
        "evolucoes": {
            5: {
                "nome": "Vollständig: Divina Explosão",
                "descricao": "Libera asas de reishi que bombardeiam a arena inteira. Causa 180% de MATK em área e aplica Queimadura Pesada geral em todos os inimigos."
            }
        }
    },

    # =========================340
    "kyubey_madoka": {
        "nome": "Kyubey",
        "origem": "Madoka Magica",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 10,
        "matk": 75,
        "def": 30,
        "spd": 24,
        "crt": 5,
        "habilidade": {
            "nome": "Contrato da Incubadora",
            "descricao": "Concede um pacto obscuro de poder. Oferece um buff massivo de +50% de ATK e MATK para o líder aliado, mas consome 10% do HP do alvo a cada final de turno."
        },
        "evolucoes": {
            7: {
                "nome": "Coleta de Desespero",
                "descricao": "Sempre que um aliado recebe dano, Kyubey armazena a energia e a converte em escudos protetores equivalentes a 15% do HP do aliado ferido para o herói principal."
            }
        }
    },

    # =========================341
    "kabuto_eremita": {
        "nome": "Kabuto Yakushi (Eremita)",
        "origem": "Naruto",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 140,
        "atk": 30,
        "matk": 72,
        "def": 35,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Transmissão de Fluidos Médicos",
            "descricao": "Usa enzimas de cura avançadas derivadas de seu corpo de cobra. Regenera 25% de HP do aliado mais fraco a cada turno por 3 turnos inteiros."
        },
        "evolucoes": {
            5: {
                "nome": "Reanimação Orgânica Inorgânica",
                "descricao": "Controla a própria terra e corpos ao redor. Remove todos os debuffs negativos da equipe e ressuscita um herói derrotado com 20% de seu HP máximo."
            }
        }
    },

    # =========================342
    "overhaul_kai": {
        "nome": "Overhaul (Kai Chisaki)",
        "origem": "Boku no Hero Academia",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 135,
        "atk": 50,
        "matk": 68,
        "def": 32,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Desonstrução e Reconstrução",
            "descricao": "Chisaki desintegra e reconstrói o corpo de um aliado. Limpa completamente todos os debuffs do alvo e o cura em 45% do HP instantaneamente."
        },
        "evolucoes": {
            5: {
                "nome": "Fusão de Carne Biológica",
                "descricao": "Funde-se a um aliado para se blindar. Concede a si mesmo +50% de DEF e aumenta em 30% a eficiência de qualquer cura que ele aplicar na arena."
            }
        }
    },

    # =========================343
    "shaiapouf_hxh": {
        "nome": "Shaiapouf",
        "origem": "Hunter x Hunter",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 125,
        "atk": 25,
        "matk": 76,
        "def": 28,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Escamas de Hipnose Espiritual",
            "descricao": "Espalha poeira brilhante de suas asas de borboleta quimera. Reduz o ataque físico (ATK) e mágico (MATK) de todos os oponentes na arena em 30% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Divisão de Células de Pouf",
                "descricao": "Divide seu corpo em milhares de mini-clones. Envolve toda a sua equipe em escudos de poeira e concede +30% de velocidade de ação para os aliados."
            }
        }
    },

    # =========================344
    "szayelaporro_granz": {
        "nome": "Szayelaporro Granz",
        "origem": "Bleach",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 30,
        "matk": 65,
        "def": 22,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Criação de Boneco Vodu",
            "descricao": "Cria uma cópia física do oponente para torturar os órgãos. Sempre que o herói líder aliado for atacado, o inimigo marcado pelo vodu sofre 40% do dano de forma tática."
        },
        "evolucoes": {
            5: {
                "nome": "Replicação de Órgãos",
                "descricao": "Suas drogas e avanços científicos regeneram feridas e membros perdidos. Cura um aliado em 30% do MATK e o torna imune a sangramento e veneno por 3 rodadas."
            }
        }
    },
    # =========================345
    "mash_kyrielight": {
        "nome": "Mash Kyrielight",
        "origem": "Fate/Grand Order",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 160,
        "atk": 35,
        "matk": 20,
        "def": 55,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Lord Chaldeas",
            "descricao": "Mash ergue o escudo colossal da Távola Redonda. Atrai provocação de todos os oponentes (Taunt) e ganha um escudo protetor de 30% de seu HP máximo por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Lord Camelot",
                "descricao": "Manifesta o castelo espiritual intocável. Concede imunidade a danos físicos e mágicos para o herói principal aliado por 1 turno e aumenta a DEF de todos em 50% por 3 turnos."
            }
        }
    },

    # =========================346
    "jeanne_d_arc": {
        "nome": "Jeanne d'Arc",
        "origem": "Fate/Apocrypha",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 180,
        "atk": 45,
        "matk": 30,
        "def": 60,
        "spd": 16,
        "crt": 5,
        "habilidade": {
            "nome": "Luminosité Eternelle",
            "descricao": "Jeanne finca sua bandeira no chão, criando uma barreira de luz sagrada. Concede imunidade total contra danos mágicos e de área para a equipe por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "La Pucelle",
                "atk": 35,
                "spd": 10,
                "descricao": "Libera chamas purificadoras de sua alma. Causa 250% de MATK verdadeiro em área que anula buffs inimigos, mas consome 20% do HP atual de Jeanne."
            }
        }
    },

    # =========================347
    "king_hassan": {
        "nome": "King Hassan",
        "origem": "Fate/Grand Order",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 170,
        "atk": 82,
        "matk": 35,
        "def": 45,
        "spd": 24,
        "crt": 20,
        "habilidade": {
            "nome": "Azrael: O Anjo da Morte",
            "descricao": "O Velho da Montanha desfere um golpe de espada gigante lento e solene. Causa 220% de ATK e possui 10% de chance de executar o oponente instantaneamente."
        },
        "evolucoes": {
            7: {
                "nome": "Sino do Fim",
                "atk": 40,
                "spd": 15,
                "descricao": "Sempre que o sino do abismo badala, o destino é selado. Reduz o ataque de todos os oponentes em 40% por 3 turnos, impedindo-os de reviver se forem derrotados."
            }
        }
    },

    # =========================348
    "obito_uchiha": {
        "nome": "Obito Uchiha",
        "origem": "Naruto",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 165,
        "atk": 80,
        "matk": 50,
        "def": 35,
        "spd": 38,
        "crt": 15,
        "habilidade": {
            "nome": "Kamui: Intangibilidade",
            "descricao": "Obito distorce seu corpo físico para outra dimensão. Fica completamente imune a qualquer ataque direcionado por 2 turnos e desfere contra-ataques automáticos de 150% de ATK."
        },
        "evolucoes": {
            7: {
                "nome": "Gedo Mazo",
                "atk": 30,
                "spd": 20,
                "descricao": "Invoca os canhões de alma da estátua colossal. Causa 260% de ATK em área e drena a energia inimiga (atrasa as habilidades e recargas de todos em 2 rodadas)."
            }
        }
    },

    # =========================349
    "soifon": {
        "nome": "Soifon",
        "origem": "Bleach",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 72,
        "matk": 10,
        "def": 20,
        "spd": 38,
        "crt": 25,
        "habilidade": {
            "nome": "Suzumebachi: Duas Picadas",
            "descricao": "Marca o inimigo na primeira estocada. Causa 160% de ATK e, se conseguir acertar o mesmo alvo na rodada seguinte, causará dano crítico triplicado garantido."
        },
        "evolucoes": {
            5: {
                "nome": "Shunko Espiritual",
                "descricao": "Ativa seu combate de vento espiritual de alto nível. Concede +40% de SPD e faz com que seus ataques básicos ignorem completamente a defesa do oponente por 2 turnos."
            }
        }
    },

    # =========================350
    "suzuya_juuzou": {
        "nome": "Suzuya Juuzou",
        "origem": "Tokyo Ghoul",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 52,
        "matk": 0,
        "def": 18,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Scorpion 1/56",
            "descricao": "Atira múltiplas facas de arremesso de forma acrobática. Causa 140% de ATK físico e aplica Sangramento por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Jason do CCG: Foice Gigante",
                "descricao": "Corta os inimigos de forma insana e imprevisível. Causa 220% de ATK físico e garante acerto crítico contra inimigos que já possuam debuffs."
            }
        }
    },

    # =========================351
    "feitan_portor": {
        "nome": "Feitan Portor",
        "origem": "Hunter x Hunter",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 70,
        "matk": 25,
        "def": 22,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Pain Packer: Sol Nascente",
            "descricao": "Entra em modo de contra-ataque térmico. Quanto menor for o HP atual de Feitan, mais destrutivo e abrasador será seu próximo golpe mágico de fogo em área (até 300% de MATK)."
        },
        "evolucoes": {
            5: {
                "nome": "Corte de Sombra Veloz",
                "descricao": "Desfere golpes rápidos e imperceptíveis de sua lâmina oculta no guarda-chuva. Causa 180% de ATK físico e impede os inimigos de ativarem barreiras."
            }
        }
    },

    # =========================352
    "souei": {
        "nome": "Souei",
        "origem": "Tensei Shitara Slime Datta Ken",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 48,
        "matk": 20,
        "def": 20,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Fios Invisíveis de Aço",
            "descricao": "Souei prende e retalha os oponentes à distância. Causa 130% de ATK físico à retaguarda oponente e silencia magos por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Teletransporte de Sombra",
                "descricao": "Souei ataca de surpresa saindo das sombras com seus clones. Ganha +35% de esquiva (dodge) absoluta e desfere um golpe de 200% de ATK."
            }
        }
    },
    # =========================353
    "archer_emiya": {
        "nome": "Archer (EMIYA)",
        "origem": "Fate/Stay Night",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 70,
        "matk": 40,
        "def": 24,
        "spd": 28,
        "crt": 20,
        "habilidade": {
            "nome": "Caladbolg II: Flecha de Espadas",
            "descricao": "Dispara sua espada modificada como projétil rotativo concentrado de energia. Causa 190% de ATK e quebra 40% da defesa física do oponente por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Unlimited Blade Works",
                "atk": 30,
                "spd": 10,
                "descricao": "Invoca a sua realidade paralela cheia de espadas infinitas. Todos os oponentes perdem 30% de DEF e sofrem dano de chuva de espadas de 150% de ATK por 2 turnos."
            }
        }
    },

    # =========================354
    "ishtar_fgo": {
        "nome": "Ishtar",
        "origem": "Fate/Grand Order",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 145,
        "atk": 35,
        "matk": 82,
        "def": 30,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "An Gal Ta Kigal She",
            "descricao": "Dispara joias de mana do céu montada em seu arco místico gigante. Causa 180% de MATK em área na retaguarda oponente e reduz o ATK deles em 30%."
        },
        "evolucoes": {
            7: {
                "nome": "Disparo Cósmico de Vênus",
                "atk": 25,
                "spd": 15,
                "descricao": "Abre um portal estelar direto e esmaga o campo inimigo. Causa 280% de MATK em área de acerto crítico garantido, aplicando Queimadura Pesada geral."
            }
        }
    },

    # =========================355
    "van_augur": {
        "nome": "Van Augur",
        "origem": "One Piece",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 75,
        "matk": 0,
        "def": 20,
        "spd": 32,
        "crt": 25,
        "habilidade": {
            "nome": "Tiro de Precisão de Longo Alcance",
            "descricao": "Ataca com seu fuzil Senriku de distâncias extremas. Causa 180% de ATK que ignora a esquiva e penetra 35% de defesa física do alvo."
        },
        "evolucoes": {
            5: {
                "nome": "Warp: Deslocamento Espacial",
                "descricao": "Teleporta a si mesmo e a um aliado para longe do perigo. Concede imunidade a ataques normais e remove provocações ativas por 1 turno."
            }
        }
    },

    # =========================356
    "yasopp": {
        "nome": "Yasopp",
        "origem": "One Piece",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 72,
        "matk": 0,
        "def": 22,
        "spd": 30,
        "crt": 20,
        "habilidade": {
            "nome": "Disparos Rápidos de Pistola",
            "descricao": "Desfere múltiplos disparos em cadeia na retaguarda. Causa 4 hits rápidos de 50% de ATK físico e aplica Sangramento contínuo por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Pontaria do Atirador Lendário",
                "descricao": "Seu instinto de tiro é absoluto. Aumenta sua taxa crítica (Crt) em 35% e ignora 40% da defesa física do oponente por toda a luta."
            }
        }
    },

    # =========================357
    "sasha_blouse": {
        "nome": "Sasha Blouse",
        "origem": "Shingeki no Kyojin",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 2,
        "max_star": 7,
        "hp": 100,
        "atk": 42,
        "matk": 0,
        "def": 16,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Tiro do Caçador",
            "descricao": "Dispara flechas certeiras de caça florestal. Causa 130% de ATK físico e reduz a esquiva do oponente em 15% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Instinto Alimentar",
                "descricao": "Sasha consome uma batata quente e ganha energia feroz. Cura-se em 20% de HP e aumenta seu ATK em 20% por 2 turnos."
            },
            5: {
                "nome": "Faro de Saque",
                "descricao": "Sasha garante que os recursos do inimigo sejam aproveitados. Aumenta os ganhos de Ouro e Comida em caçadas em 20% passivamente."
            }
        }
    },

    # =========================358
    "mey_rin": {
        "nome": "Mey-Rin",
        "origem": "Black Butler",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 2,
        "max_star": 7,
        "hp": 95,
        "atk": 46,
        "matk": 5,
        "def": 14,
        "spd": 22,
        "crt": 18,
        "habilidade": {
            "nome": "Remoção dos Óculos",
            "descricao": "Mey-Rin retira seus óculos, revelando sua pontaria absurda de franco-atiradora. Ganha +30% de ATK e +20% de Crt por 3 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Pistolas Duplas Rápidas",
                "descricao": "Dispara em rajadas frenéticas de duas mãos. Causa 3 hits de 50% de ATK físico direto na retaguarda inimiga."
            },
            5: {
                "nome": "Fogo de Supressão do Telhado",
                "descricao": "Atira de cima do telhado do castelo Phantomhive. Reduz a precisão (accuracy) de todos os inimigos na arena em 30%."
            }
        }
    },

    # =========================359
    "yoichi_saotome": {
        "nome": "Yoichi Saotome",
        "origem": "Owari no Seraph",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 50,
        "matk": 22,
        "def": 16,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Gekkouin: Flecha Teleguiada",
            "descricao": "Dispara seu arco demoníaco verde. Causa 150% de ATK e expõe alvos ocultos ou invisíveis na arena por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Força de Vontade Demoníaca",
                "descricao": "Yoichi supera a possessão espiritual. Ganha +30% de ATK e todos os seus disparos reduzem a SPD inimiga em 25% por 2 rodadas."
            }
        }
    },

    # =========================360
    "shinya_hiiragi": {
        "nome": "Shinya Hiiragi",
        "origem": "Owari no Seraph",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 65,
        "matk": 35,
        "def": 18,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Baiakuran: Tigre de Fogo",
            "descricao": "Dispara projéteis de energia que se convertem em tigres brancos de chama ao impacto. Causa 160% de ATK e aplica Queimadura Pesada em área."
        },
        "evolucoes": {
            5: {
                "nome": "Fogo Cruzado com a Retaguarda",
                "descricao": "Organiza uma linha de disparos pesados com sua equipe. Causa 220% de ATK físico à retaguarda oponente e atordoa o curador inimigo por 1 turno."
            }
        }
    },

    # =========================361
    "foo_fighters": {
        "nome": "Foo Fighters",
        "origem": "JoJo's Bizarre Adventure",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 115,
        "atk": 45,
        "matk": 25,
        "def": 22,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Disparos de Plâncton",
            "descricao": "Dispara tiros biológicos das pontas de seus dedos. Causa 130% de ATK físico e cura a si mesma em 25% do dano causado."
        },
        "evolucoes": {
            5: {
                "nome": "Restauração Aquosa",
                "descricao": "F.F. consome água armazenada para se consertar rapidamente. Cura todo o grupo em 20% de seu HP máximo e remove debuffs de queimadura."
            }
        }
    },

    # =========================362
    "lugh_tuatha_de": {
        "nome": "Lugh Tuatha Dé",
        "origem": "The World's Finest Assassin",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 70,
        "matk": 45,
        "def": 22,
        "spd": 28,
        "crt": 20,
        "habilidade": {
            "nome": "Sniper de Tungstênio",
            "descricao": "Usa magia gravitacional e aceleração para disparar projéteis em altíssima velocidade. Causa 180% de ATK que ignora 100% de escudos e 50% da defesa."
        },
        "evolucoes": {
            5: {
                "nome": "Modo Assassino Perfeito",
                "descricao": "Lugh usa sua inteligência artificial tática. Seus ataques não podem ser bloqueados ou refletidos e ele cura-se em 25% do dano que causar."
            }
        }
    },

    # =========================363
    "franklin_bordeau": {
        "nome": "Franklin Bordeau",
        "origem": "Hunter x Hunter",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 125,
        "atk": 55,
        "matk": 10,
        "def": 25,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Double Machine Gun",
            "descricao": "Atira balas de Nen em alta cadência através de suas pontas de dedos decepadas. Causa 150% de ATK em área na arena inimiga."
        },
        "evolucoes": {
            5: {
                "nome": "Fogo de Supressão do Grupo",
                "descricao": "Suas rajadas pesadas estraçalham defesas. Reduz a DEF de toda a equipe inimiga em 30% por 3 turnos."
            }
        }
    },

    # =========================364
    "pokkle": {
        "nome": "Pokkle",
        "origem": "Hunter x Hunter",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 2,
        "max_star": 7,
        "hp": 95,
        "atk": 40,
        "matk": 25,
        "def": 15,
        "spd": 25,
        "crt": 10,
        "habilidade": {
            "nome": "Flecha Vermelha (Fogo)",
            "descricao": "Dispara uma flecha de Nen incandescente. Causa 120% de dano mágico e aplica Queimadura por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Flecha Amarela (Velocidade)",
                "descricao": "Dispara uma flecha ultra veloz que causa 100% de dano e concede turno extra imediato com 50% de chance."
            },
            5: {
                "nome": "Arco das Sete Cores (Nen)",
                "descricao": "Sorteia um efeito elemental aleatório adicional a cada ataque básico de Pokkle (sangramento, veneno ou paralisia)."
            }
        }
    },

    # =========================365
    "kamo_noritoshi": {
        "nome": "Kamo Noritoshi",
        "origem": "Jujutsu Kaisen",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 48,
        "matk": 30,
        "def": 20,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Flecha de Sangue Manipulado",
            "descricao": "Dispara flechas teleguiadas banhadas em seu próprio sangue de feiticeiro. Causa 140% de ATK e drena 30% da vida para si."
        },
        "evolucoes": {
            5: {
                "nome": "Selo de Escamas Vermelhas",
                "descricao": "Kamo acelera seu fluxo sanguíneo aumentando seu metabolismo. Concede +30% de SPD, +20% de ATK e +15% de DEF por 3 turnos."
            }
        }
    },

    # =========================366
    "mai_zenin": {
        "nome": "Mai Zen'in",
        "origem": "Jujutsu Kaisen",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 1,
        "max_star": 7,
        "hp": 90,
        "atk": 22,
        "matk": 5,
        "def": 12,
        "spd": 16,
        "crt": 8,
        "habilidade": {
            "nome": "Disparo do Revólver",
            "descricao": "Dispara um tiro simples com sua arma curta. Causa 110% de Atk físico de recarga rápida."
        },
        "evolucoes": {
            3: {
                "nome": "Construção de Bala",
                "descricao": "Cria uma bala de metal perfeita do nada sacrificando sua mana. Seu próximo ataque ignora 30% da DEF inimiga."
            },
            5: {
                "nome": "Fogo de Supressão",
                "descricao": "Dispara tiros rápidos de cobertura. Reduz o ATK do inimigo mais veloz em 15% por 2 turnos."
            }
        }
    },

    # =========================367
    "yuri_nakamura": {
        "nome": "Yuri Nakamura",
        "origem": "Angel Beats!",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 52,
        "matk": 15,
        "def": 18,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Comando de Fogo da SSS",
            "descricao": "Yuri lidera e abre fogo de submetralhadora contra o inimigo mais perigoso. Causa 150% de ATK e aumenta a taxa crítica de todos os atiradores aliados em 15% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Rebelião Contra os Deuses",
                "descricao": "Yuri se recusa a aceitar o destino cruel e lidera o front de combate. Concede imunidade a efeitos de paralisia e medo para todo o grupo de combate por 3 rodadas."
            }
        }
    },

    # =========================368
    "tigrevurmud_vorn": {
        "nome": "Tigrevurmud Vorn",
        "origem": "Madan no Ou to Vanadis",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 68,
        "matk": 35,
        "def": 24,
        "spd": 22,
        "crt": 18,
        "habilidade": {
            "nome": "Arco Negro dos Ventos",
            "descricao": "Dispara uma flecha infundida com a força do tornado. Causa 160% de ATK, empurra o alvo para trás na ordem de turnos e silencia magos por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Tiro do Caçador Lendário",
                "descricao": "A precisão do arco negro é milagrosa. Seus ataques sempre acertam e causam dano crítico dobrado contra inimigos da classe Boss ou Calamidade."
            }
        }
    },

    # =========================369
    "pip_bernadotte": {
        "nome": "Pip Bernadotte",
        "origem": "Hellsing",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 2,
        "max_star": 7,
        "hp": 105,
        "atk": 44,
        "matk": 10,
        "def": 18,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Tiro do Mercenário",
            "descricao": "Dispara seu rifle de assalto taticamente. Causa 130% de ATK e reduz a DEF física do inimigo em 15% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Lança-Granadas de Fumaça",
                "descricao": "Dispara granadas de cobertura. Oculta o herói principal aliado (aumenta esquiva em 30%) por 1 turno."
            },
            5: {
                "nome": "Esquadrão Ganso Selvagem",
                "descricao": "Invoca fogo cruzado coordenado de sua milícia. Causa 160% de ATK em área e cancela as recargas de contra-ataque inimigas."
            }
        }
    },

    # =========================370
    "beyond_the_grave": {
        "nome": "Beyond the Grave",
        "origem": "Gungrave",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 130,
        "atk": 72,
        "matk": 10,
        "def": 35,
        "spd": 15,
        "crt": 10,
        "habilidade": {
            "nome": "Metralhadora Cerberus",
            "descricao": "Dispara rajadas maciças de suas imensas pistolas. Causa 180% de ATK e anula temporariamente qualquer efeito de regeneração e cura ativa no alvo por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Disparo do Caixão Balístico",
                "descricao": "Grave usa o caixão que carrega nas costas para lançar granadas pesadas. Causa 250% de ATK em área e destrói escudos protetores de terra."
            }
        }
    },

    # =========================371
    "heero_yuy": {
        "nome": "Heero Yuy",
        "origem": "Mobile Suit Gundam Wing",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 155,
        "atk": 85,
        "matk": 40,
        "def": 35,
        "spd": 25,
        "crt": 12,
        "habilidade": {
            "nome": "Buster Rifle de Feixe Térmico",
            "descricao": "Heero dispara uma rajada massiva de energia térmica em linha reta. Causa 220% de dano misto (físico + mágico) que ignora escudos protetores."
        },
        "evolucoes": {
            7: {
                "nome": "Sistema ZERO",
                "atk": 30,
                "spd": 20,
                "descricao": "Ativa o computador de combate que calcula todas as possibilidades futuras. Concede +100% de precisão, +30% de esquiva e garante um ataque extra por rodada durante 3 turnos."
            }
        }
    },

    # =========================372
    "zwei_phantom": {
        "nome": "Zwei",
        "origem": "Phantom: Requiem for the Phantom",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 54,
        "matk": 0,
        "def": 18,
        "spd": 28,
        "crt": 20,
        "habilidade": {
            "nome": "Execução Silenciosa",
            "descricao": "Zwei foca no ponto fraco do inimigo mais exposto de menor HP. Causa 160% de ATK físico à retaguarda oponente e ignora 30% de sua defesa física."
        },
        "evolucoes": {
            5: {
                "nome": "Phantom do Submundo",
                "descricao": "Fica ocultado (invisibilidade parcial/esquiva de 40%) por 2 turnos. Desfere um acerto crítico garantido de 250% de ATK ao sair das sombras."
            }
        }
    },
    # =========================373
    "waver_velvet": {
        "nome": "Waver Velvet",
        "origem": "Fate/Zero",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 160,
        "atk": 25,
        "matk": 78,
        "def": 42,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Estratégia de Lord El-Melloi II",
            "descricao": "Traça a linha de defesa e ataque perfeita analisando os fluxos de mana. Concede +30% de DEF, +25% de ATK/MATK para toda a equipe por 3 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Unreturned Army",
                "atk": 15,
                "spd": 10,
                "descricao": "Prende os inimigos em uma barreira tática impenetrável. Silencia (Silence) todos os magos oponentes por 2 turnos e remove todos os seus buffs ativos."
            }
        }
    },

    # =========================374
    "tamamo_no_mae": {
        "nome": "Tamamo no Mae",
        "origem": "Fate/Extra",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 165,
        "atk": 20,
        "matk": 82,
        "def": 38,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Amaterasu: Espelho Celestial",
            "descricao": "Usa seu espelho sagrado para refletir e curar deuses e homens. Cura todos os aliados em 35% do seu MATK e reduz o cooldown das habilidades de todos em 1 turno."
        },
        "evolucoes": {
            7: {
                "nome": "Banquete das Nove Caudas",
                "atk": 10,
                "spd": 15,
                "descricao": "Libera a força ancestral da raposa de sol. Concede imunidade completa a debuffs de controle para a equipe e recupera 15% de HP máximo por rodada por 2 turnos."
            }
        }
    },

    # =========================375
    "eri_mha": {
        "nome": "Eri",
        "origem": "Boku no Hero Academia",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 10,
        "matk": 65,
        "def": 25,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Rebobinar Estado Corporal",
            "descricao": "Eri usa seu chifre de energia para retroceder o tempo orgânico do corpo. Limpa todos os debuffs do alvo e o cura em 50% do HP de forma instantânea."
        },
        "evolucoes": {
            5: {
                "nome": "Reversão Temporal Suprema",
                "descricao": "Salva um aliado do esquecimento orgânico. Se o herói principal sofrer dano fatal nesta rodada, a energia de Eri retrocede seu HP para 100% (1 vez por combate)."
            }
        }
    },

    # =========================376
    "reigen_arataka": {
        "nome": "Reigen Arataka",
        "origem": "Mob Psycho 100",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 100,
        "atk": 12,
        "matk": 8,
        "def": 15,
        "spd": 20,
        "crt": 12,
        "habilidade": {
            "nome": "Purificação de Sal de Cozinha",
            "descricao": "Atira punhados de sal refinado direto nos olhos do inimigo mais perigoso. Causa 80% de Atk, mas tem 40% de chance de atordoar (Stun) o oponente."
        },
        "evolucoes": {
            3: {
                "nome": "Massagem de Ombros Relaxante",
                "descricao": "Alivia a tensão muscular e espiritual de um herói de ataque aliado. Cura 15% do HP do alvo e aumenta seu ATK em 15% por 2 turnos."
            },
            5: {
                "nome": "Conselho de Mestre Genuíno",
                "descricao": "Sua lábia motivadora reergue o espírito da guilda. Aumenta a resistência mental e a DEF mágica de toda a equipe em 25% por 3 turnos."
            }
        }
    },

    # =========================377
    "morgana_persona": {
        "nome": "Morgana (Mona)",
        "origem": "Persona 5",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 15,
        "matk": 48,
        "def": 18,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Magia Garu: Vento Curativo",
            "descricao": "Morgana evoca rajadas suaves de vento e cura um aliado em 30% do MATK, aumentando sua SPD em 15% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Salvação de Morgana (Mediaharan)",
                "descricao": "Cura toda a equipe em 25% do MATK de Morgana e remove instantaneamente os efeitos negativos de paralisia e choque."
            }
        }
    },

    # =========================378
    "mimosa_vermillion": {
        "nome": "Mimosa Vermillion",
        "origem": "Black Clover",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 12,
        "matk": 62,
        "def": 24,
        "spd": 22,
        "crt": 5,
        "habilidade": {
            "nome": "Manto Curativo de Flores",
            "descricao": "Ergue um ninho de vinhas de flores protetoras ao redor do aliado mais ferido. Recupera 35% de seu HP e concede +30% de DEF mágica por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Flor Guia do Berço Sagrado",
                "descricao": "Uma grande flor desabrocha no centro do mapa. Restaura 15% do HP máximo de todos os aliados no início de cada ação por 3 rodadas completas."
            }
        }
    },

    # =========================379
    "charmy_pappitson": {
        "nome": "Charmy Pappitson",
        "origem": "Black Clover",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 120,
        "atk": 25,
        "matk": 42,
        "def": 22,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Ovelha Cozinheira de Resgate",
            "descricao": "Invoca ovelhas de algodão que servem refeições mágicas divinas. Cura todos os aliados em 20% do seu MATK e acelera as recargas de turnos das classes de ataque."
        },
        "evolucoes": {
            5: {
                "nome": "Ovelha Gigante Devoradora",
                "descricao": "Charmy entra em modo de fúria quando alguém mexe em sua comida. Invoca um impacto de lobo de algodão gigante que causa 180% de MATK e rouba 30% do ATK inimigo."
            }
        }
    },

    # =========================380
    "sherria_blendy": {
        "nome": "Sherria Blendy",
        "origem": "Fairy Tail",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 14,
        "matk": 54,
        "def": 20,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Magia de God Slayer dos Céus",
            "descricao": "Cura divina purificadora com o vento negro sagrado. Restaura 25% de HP máximo do alvo aliado e concede +20% de velocidade de ação (SPD) por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Coleta Espiritual de Terzo",
                "descricao": "Usa a essência divina do céu para reenergizar a party. Cura toda a equipe em 20% de MATK e limpa debuffs de sangramento e envenenamento."
            }
        }
    },

    # =========================381
    "asia_argento": {
        "nome": "Asia Argento",
        "origem": "High School DxD",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 100,
        "atk": 8,
        "matk": 38,
        "def": 18,
        "spd": 16,
        "crt": 5,
        "habilidade": {
            "nome": "Twilight Healing: Crepúsculo",
            "descricao": "Asia foca sua oração sincera para conjurar uma luz dourada. Cura o herói principal da equipe em 30% do MATK e remove debuffs mágicos."
        },
        "evolucoes": {
            3: {
                "nome": "Prece de Resistência Divina",
                "descricao": "Sua reza sincera ergue a determinação dos aliados. Concede +20% de defesa física e mágica por 2 turnos."
            },
            5: {
                "nome": "Oração de Cura Contínua",
                "descricao": "A luz sagrada protege a equipe. Recupera 8% do HP máximo de todos os aliados de forma contínua no início de cada rodada."
            }
        }
    },

    # =========================382
    "dende_dbz": {
        "nome": "Dende",
        "origem": "Dragon Ball Z",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 115,
        "atk": 10,
        "matk": 55,
        "def": 25,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Cura Namekuseijin Espiritual",
            "descricao": "Dende canaliza energia espiritual restauradora sobre as feridas. Cura instantaneamente 45% do HP do herói líder e remove qualquer efeito ativo de veneno."
        },
        "evolucoes": {
            5: {
                "nome": "Bênção das Esferas de Namek",
                "descricao": "Dende evoca a aura protetora de Shenlong. Concede imunidade completa a danos mágicos de fogo, gelo ou raio por 2 turnos inteiros."
            }
        }
    },

    # =========================383
    "yosuke_hanamura": {
        "nome": "Yosuke Hanamura",
        "origem": "Persona 4",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 30,
        "matk": 44,
        "def": 18,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Junes: Promoção Espetacular",
            "descricao": "Yosuke usa sua energia dinâmica de gerente para motivar. Aumenta a velocidade de ação (SPD) e a precisão de todos os aliados em 25% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Persona Jiraiya: Vento Divino",
                "descricao": "Conjura ciclones que varrem os perigos da equipe. Cura toda a equipe em 15% do MATK e limpa efeitos de redução de velocidade."
            }
        }
    },

    # =========================384
    "shizuka_marikawa": {
        "nome": "Shizuka Marikawa",
        "origem": "Highschool of the Dead",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 95,
        "atk": 5,
        "matk": 32,
        "def": 14,
        "spd": 12,
        "crt": 5,
        "habilidade": {
            "nome": "Curativo Distraído",
            "descricao": "Aplica um curativo de forma atrapalhada. Cura um aliado aleatório em 25% do MATK e remove sangramentos."
        },
        "evolucoes": {
            3: {
                "nome": "Anestésico Científico",
                "descricao": "Aplica um sedativo para neutralizar dores de combate. Concede imunidade a efeitos de choque e reduz em 20% o dano físico sofrido."
            },
            5: {
                "nome": "Tratamento Médico Total",
                "descricao": "Sua bondade reergue os aliados caídos. Cura toda a equipe em 15% de MATK e aumenta a DEF de todos em 20% por 2 rodadas."
            }
        }
    },

    # =========================385
    "nanao_ise": {
        "nome": "Nanao Ise",
        "origem": "Bleach",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 15,
        "matk": 52,
        "def": 24,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Barreira Hakudan Keikai",
            "descricao": "Nanao cria uma barreira protetora quadrilateral de kido. Protege a equipe, absorvendo todo dano mágico recebido nesta rodada por até 30% do HP de Nanao."
        },
        "evolucoes": {
            5: {
                "nome": "Corte de Kido Espiritual",
                "descricao": "Usa técnicas de aprisionamento médico de alta patente. Cura um aliado em 30% do MATK de Nanao e silencia as habilidades ativas inimigas por 1 turno."
            }
        }
    },
    # =========================386
    "yoruichi_shihoin": {
        "nome": "Yoruichi Shihoin",
        "origem": "Bleach",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 85,
        "matk": 45,
        "def": 20,
        "spd": 55,
        "crt": 25,
        "habilidade": {
            "nome": "Shunko: Trovão",
            "descricao": "Funde magia com combate físico. Causa 160% de ATK ao alvo e ganha um buff que aumenta sua velocidade (SPD) em 30% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Deusa do Relâmpago",
                "descricao": "Transforma-se em pura eletricidade. Seus ataques ganham acerto crítico garantido e ignoram completamente os escudos físicos do inimigo."
            }
        }
    },

    # =========================387
    "kenshin_himura": {
        "nome": "Kenshin Himura",
        "origem": "Rurouni Kenshin",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 88,
        "matk": 0,
        "def": 22,
        "spd": 48,
        "crt": 30,
        "habilidade": {
            "nome": "Amakakeru Ryu no Hirameki",
            "descricao": "A técnica suprema do saque rápido. Causa 180% de ATK em um único inimigo e aplica sangramento pesado por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Battousai, o Retalhador",
                "descricao": "Seus instintos assassinos despertam. Seus ataques normais passam a ignorar 40% da defesa do oponente e reduzem a eficácia de curas inimigas."
            }
        }
    },

    # =========================388
    "sojiro_hoshina": {
        "nome": "Sojiro Hoshina",
        "origem": "Kaiju No. 8",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 75,
        "matk": 0,
        "def": 18,
        "spd": 45,
        "crt": 20,
        "habilidade": {
            "nome": "Estilo Hoshina: Lâminas Gêmeas",
            "descricao": "Avança com agilidade absurda retalhando tudo. Causa 140% de ATK e aumenta seu próprio ataque (ATK) em 25% por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Liberação de Combate Total",
                "descricao": "Hoshina libera todo o potencial do seu traje. Fica imune à lentidão e tem 30% de chance de atacar o inimigo duas vezes na mesma rodada."
            }
        }
    },

    # =========================389
    "rob_lucci": {
        "nome": "Rob Lucci",
        "origem": "One Piece",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 115,
        "atk": 80,
        "matk": 0,
        "def": 28,
        "spd": 40,
        "crt": 15,
        "habilidade": {
            "nome": "Rokuougan",
            "descricao": "Desfere um impacto de choque interno de curta distância. Causa 150% de ATK ignorando 100% da armadura e destrói escudos ativos do inimigo."
        },
        "evolucoes": {
            5: {
                "nome": "Despertar do Leopardo",
                "descricao": "Assume sua forma híbrida de pura agressão. Ganha regeneração de 15% do HP máximo por turno e aumenta seu ATK em 30% permanentemente."
            }
        }
    },

    # =========================390
    "zeno_zoldyck": {
        "nome": "Zeno Zoldyck",
        "origem": "Hunter x Hunter",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 95,
        "matk": 50,
        "def": 25,
        "spd": 50,
        "crt": 25,
        "habilidade": {
            "nome": "Dragon Dive",
            "descricao": "Invoca uma chuva de dragões dourados de Nen a partir do céu. Causa 220% de ATK em área atingindo todos os inimigos, com 25% de chance de atordoar (stun) por 1 turno."
        },
        "evolucoes": {
            7: {
                "nome": "Mestre Assassino Experiente",
                "descricao": "Analisa o alvo e dita a morte. Fica invisível (esquiva de 100%) por 1 turno, e seu ataque seguinte causa dano destrutivo triplicado."
            }
        }
    },

    # =========================391
    "yuzuriha": {
        "nome": "Yuzuriha",
        "origem": "Hell's Paradise",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 60,
        "matk": 20,
        "def": 15,
        "spd": 42,
        "crt": 18,
        "habilidade": {
            "nome": "Fios Ninja e Secreção",
            "descricao": "Prende e manipula o alvo com fios ocultos revestidos de toxina. Causa 110% de ATK, aplica veneno por 3 turnos e reduz a velocidade do alvo em 20%."
        },
        "evolucoes": {
            3: {
                "nome": "Dança Kunoichi Ágil",
                "descricao": "Aumenta a sua agilidade em combate. Concede passivamente +25% de evasão (dodge) para evitar ataques inimigos diretos."
            },
            5: {
                "nome": "Mestra dos Venenos Letais",
                "descricao": "Seu veneno atinge o sistema nervoso. Inimigos envenenados por Yuzuriha têm o dano reduzido em 30%."
            }
        }
    },

    # =========================392
    "yujiro_hanma": {
        "nome": "Yujiro Hanma",
        "origem": "Baki",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 160,
        "atk": 110,
        "matk": 0,
        "def": 45,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Costas de Demônio",
            "descricao": "Tensiona as costas formando o rosto de um demônio sorridente. Causa 250% de ATK em um único inimigo, ignorando a defesa, com acerto crítico garantido."
        },
        "evolucoes": {
            7: {
                "nome": "A Criatura Mais Forte da Terra",
                "descricao": "Sua força absoluta aterroriza até exércitos. Reflete 50% de qualquer dano de ataque corpo a corpo recebido e ganha +50% de ATK de forma permanente."
            }
        }
    },

    # =========================393
    "sanji": {
        "nome": "Sanji",
        "origem": "One Piece",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 130,
        "atk": 85,
        "matk": 0,
        "def": 30,
        "spd": 42,
        "crt": 20,
        "habilidade": {
            "nome": "Diable Jambe",
            "descricao": "Atrita a perna no chão até incendiar o membro. Causa 160% de ATK e aplica queimadura contínua no inimigo por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Ifrit Jambe",
                "descricao": "As chamas atingem o calor azul extremo de plasma. Seus chutes passam a ignorar 40% da defesa física e têm 30% de chance de atordoar (Stun)."
            }
        }
    },

    # =========================394
    "choso": {
        "nome": "Choso",
        "origem": "Jujutsu Kaisen",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 125,
        "atk": 75,
        "matk": 30,
        "def": 32,
        "spd": 25,
        "crt": 10,
        "habilidade": {
            "nome": "Sangue Perfurante",
            "descricao": "Condensa o sangue e o dispara em velocidade supersônica. Causa 140% de ATK, aplica sangramento e reduz a velocidade (SPD) do alvo em 25% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Supernova de Sangue",
                "descricao": "Manipula orbes de sangue para detonar ao redor do alvo. Seus ataques normais afetam a área inteira e quebram escudos mágicos inimigos."
            }
        }
    },

    # =========================395
    "kafka_hibino": {
        "nome": "Kafka Hibino",
        "origem": "Kaiju No. 8",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 140,
        "atk": 92,
        "matk": 0,
        "def": 38,
        "spd": 28,
        "crt": 12,
        "habilidade": {
            "nome": "Soco Kaiju",
            "descricao": "Transforma os braços em tecido de monstro para desferir um impacto sônico. Causa 190% de ATK, quebra escudos de terra e tem 30% de chance de atordoar (stun)."
        },
        "evolucoes": {
            5: {
                "nome": "Transformação Kaiju Completa",
                "descricao": "Ao invés de morrer ao receber um golpe letal, transforma-se no Kaiju #8, recuperando 100% de HP e ganhando força destrutiva massiva por 3 turnos."
            }
        }
    },

    # =========================396
    "ippo_makunouchi": {
        "nome": "Ippo Makunouchi",
        "origem": "Hajime no Ippo",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 2,
        "max_star": 7,
        "hp": 120,
        "atk": 65,
        "matk": 0,
        "def": 30,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Dempsey Roll",
            "descricao": "Balança o corpo em forma de oito e avança batendo. Causa 130% de ATK. Seus socos implacáveis batem duas vezes e atordoam (stun) o alvo por 1 turno."
        },
        "evolucoes": {
            3: {
                "nome": "Foco Feroz",
                "descricao": "O peso do treinamento não o deixa cair. Ippo ganha imunidade absoluta contra atordoamento (Stun) e medo."
            },
            5: {
                "nome": "Gazelle Punch",
                "descricao": "Ippo agacha e salta projetando todo o corpo no queixo do adversário. Seu próximo ataque ignorará completamente a defesa física do alvo."
            }
        }
    },

    # =========================397
    "seras_victoria": {
        "nome": "Seras Victoria",
        "origem": "Hellsing",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 70,
        "matk": 15,
        "def": 20,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Canhão Harkonnen",
            "descricao": "Dispara projéteis anti-tanque urânio de 30mm. Dispara seu canhão e causa 150% de ATK em todos os inimigos, reduzindo a defesa deles em 25% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Vampira Desperta",
                "descricao": "O sangue no campo de batalha a fortalece. Seus ataques recuperam HP igual a 30% do dano causado (Lifesteal) e ela ganha +25% de velocidade."
            }
        }
    },

    # =========================398
    "daisuke_jigen": {
        "nome": "Daisuke Jigen",
        "origem": "Lupin III",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 60,
        "matk": 0,
        "def": 15,
        "spd": 35,
        "crt": 25,
        "habilidade": {
            "nome": "Saque Rápido de Magnum",
            "descricao": "Saca o revólver num piscar de olhos. Causa 120% de ATK no inimigo. O tiro é infalível e possui acerto crítico garantido (ignora a evasão)."
        },
        "evolucoes": {
            3: {
                "nome": "Tiro Furador de Armadura",
                "descricao": "Sua mira acha os pontos fracos dos coletes balísticos. Suas balas passam a ignorar 30% de qualquer armadura ou barreira inimiga."
            },
            5: {
                "nome": "Bala Ricochete Milagrosa",
                "descricao": "Jigen atira em objetos do cenário para atingir a retaguarda. Seus ataques atingem até 2 alvos a mais com 80% do dano base da arma."
            }
        }
    },

    # =========================399
    "cross_marian": {
        "nome": "Cross Marian",
        "origem": "D.Gray-man",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 88,
        "matk": 60,
        "def": 25,
        "spd": 30,
        "crt": 25,
        "habilidade": {
            "nome": "Judgement: Balas do Julgamento",
            "descricao": "Dispara balas teleguiadas amaldiçoadas que perseguem o pecador até o fim do mundo. Causa 200% de ATK, ignorando 100% de escudos, defesas e evasão do inimigo."
        },
        "evolucoes": {
            7: {
                "nome": "Grave of Maria: Controle Cadavérico",
                "descricao": "Invoca a magia do cadáver de Maria que canta. Silencia (impede magias) todos os oponentes da arena por 2 turnos e reduz o poder de ataque deles em 30%."
            }
        }
    },

    # =========================400
    "reze": {
        "nome": "Reze",
        "origem": "Chainsaw Man",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 80,
        "matk": 30,
        "def": 22,
        "spd": 38,
        "crt": 20,
        "habilidade": {
            "nome": "Explosão Bomba",
            "descricao": "Lança pedaços de si mesma como bombas em área. Causa 170% de ATK em todos os inimigos e aplica queimadura pesada por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Híbrida Demônio Bomba",
                "descricao": "Quando derrotada, puxa o próprio pino no pescoço. Revive uma vez com 50% de HP e explode ao retornar causando 200% de ATK suicida no inimigo que a matou."
            }
        }
    },

    # =========================401
    "hyakunosuke_ogata": {
        "nome": "Hyakunosuke Ogata",
        "origem": "Golden Kamuy",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 1,
        "max_star": 7,
        "hp": 85,
        "atk": 55,
        "matk": 0,
        "def": 12,
        "spd": 25,
        "crt": 20,
        "habilidade": {
            "nome": "Tiro Focado de Sniper",
            "descricao": "Ajusta a mira pacientemente para finalizar os fracos. Causa 110% de ATK ignorando 30% da defesa física do oponente, e foca no inimigo de menor HP."
        },
        "evolucoes": {
            3: {
                "nome": "Foco Estóico Frio",
                "descricao": "Ogata não treme sob pressão. Ganha um buff permanente de +20% na taxa de precisão."
            },
            5: {
                "nome": "Headshot Perfeito",
                "descricao": "A letalidade de um soldado sem alma. Seus ataques possuem 20% de chance de executar instantaneamente (Insta Kill) alvos com menos de 20% do HP."
            }
        }
    },

    # =========================402
    "tsukasa_shishio": {
        "nome": "Tsukasa Shishio",
        "origem": "Dr. Stone",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 3,
        "max_star": 7,
        "hp": 130,
        "atk": 75,
        "matk": 0,
        "def": 35,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Força Primata Mais Forte",
            "descricao": "Lidera o front com poder e carisma brutais. Causa 140% de ATK no inimigo e concede um buff que aumenta o ataque (ATK) de todos os aliados de linha de frente em 20% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "O Império da Força Jovem",
                "descricao": "A sua visão atrai as mentes puras de seus guerreiros. Enquanto Tsukasa viver, a equipe recebe imunidade total a efeitos de atordoamento (Stun) e paralisia."
            }
        }
    },

    # =========================403
    "rintarou_okabe": {
        "nome": "Rintarou Okabe",
        "origem": "Steins;Gate",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 1,
        "max_star": 7,
        "hp": 80,
        "atk": 10,
        "matk": 15,
        "def": 15,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Reading Steiner",
            "descricao": "Usa seu telefone mágico para ver linhas do tempo alternativas. Antecipa o perigo e concede um buff que aumenta a evasão de todos os aliados em 25% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Telefone Micro-ondas (Nome Provisório)",
                "descricao": "A ciência louca interfere no espaço-tempo. Uma vez por batalha, zera completamente os tempos de recarga (cooldowns) das magias da sua equipe."
            },
            5: {
                "nome": "El Psy Kongroo",
                "descricao": "Ele viaja no tempo para desfazer a tragédia. Impede a primeira morte de um aliado na rodada, devolvendo 10% do HP do alvo ferido instantaneamente."
            }
        }
    },

    # =========================404
    "l_lawliet": {
        "nome": "L Lawliet",
        "origem": "Death Note",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 12,
        "matk": 25,
        "def": 20,
        "spd": 35,
        "crt": 5,
        "habilidade": {
            "nome": "Análise de Fraquezas",
            "descricao": "L não luta com os punhos. Ele descobre todas as falhas mentais do inimigo. Reduz a defesa e a velocidade (SPD) do inimigo com maior ataque em 40% por 3 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Deduzir a Tática Inimiga",
                "descricao": "O brilhante detetive avisa o grupo por onde o inimigo irá atacar. Concede +15% de Chance de Crítico para toda a equipe aliada."
            },
            5: {
                "nome": "Um Passo à Frente do Assassino",
                "descricao": "L prepara uma isca genial. A equipe ganha um escudo invisível que anula automaticamente o primeiro debuff pesado (veneno/sangramento/stun) que receberem."
            }
        }
    },

    # =========================405
    "koro_sensei": {
        "nome": "Koro-sensei",
        "origem": "Assassination Classroom",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 70,
        "matk": 60,
        "def": 40,
        "spd": 85,
        "crt": 15,
        "habilidade": {
            "nome": "Movimento Veloz Mach 20",
            "descricao": "Move-se rapidamente e cuida dos seus alunos de forma tentacular. Causa 150% de ATK a todos os inimigos e concede um escudo equivalente a 25% de HP para a equipe."
        },
        "evolucoes": {
            7: {
                "nome": "Defesa Absoluta de Esfera de Energia",
                "descricao": "Ao sofrer um dano letal, encolhe-se dentro de uma esfera cristalina indestrutível. Fica invulnerável a todos os ataques por 1 turno e cura 50% do HP de todos os seus alunos aliados na arena."
            }
        }
    },

    # =========================406
    "luffy": {
        "nome": "Monkey D. Luffy",
        "origem": "One Piece",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 160,
        "atk": 90,
        "matk": 0,
        "def": 45,
        "spd": 35,
        "crt": 20,
        "habilidade": {
            "nome": "Haki do Rei (Haoshoku Haki)",
            "descricao": "Dispara uma onda massiva de Haki de intimidação imperial. Causa 140% de ATK em todos os inimigos com 40% de chance de atordoar (stun) a equipe inimiga inteira por 1 turno."
        },
        "evolucoes": {
            7: {
                "nome": "Despertar: Gear 5 (Deus do Sol Nika)",
                "descricao": "Ao cair em batalha, desperta o tambor da libertação. Revive com 100% de HP, ganha +50% em todos os status, e seus ataques de borracha deformam a realidade, ignorando defesas e escudos."
            }
        }
    },

    # =========================407
    "rin_tohsaka": {
        "nome": "Rin Tohsaka",
        "origem": "Fate/stay night",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 20,
        "matk": 70,
        "def": 20,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Joias Mágicas Gandr",
            "descricao": "Dispara joias acumuladas com magia amaldiçoada condensada. Causa 140% de MATK e reduz o ataque do inimigo em 25% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Mestra Herdeira das Joias Tohsaka",
                "descricao": "A linhagem de Tohsaka transforma dor em recursos. Seus críticos mágicos curam 15% do HP máximo de toda a equipe devido à redistribuição de mana."
            }
        }
    },

    # =========================408
    "lina_inverse": {
        "nome": "Lina Inverse",
        "origem": "Slayers",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 15,
        "matk": 85,
        "def": 18,
        "spd": 25,
        "crt": 20,
        "habilidade": {
            "nome": "Conjuração do Drag Slave",
            "descricao": "O feitiço que assusta até dragões. Causa 220% de MATK em todos os inimigos, arrasando a arena e destruindo os escudos mágicos ativos oponentes."
        },
        "evolucoes": {
            5: {
                "nome": "Giga Slave (Invocação das Trevas)",
                "descricao": "Um feitiço perigoso que usa o poder do Lorde dos Pesadelos. O seu próximo dano mágico é elevado para a potência absurda de 300% de MATK, mas ela ficará silenciada no turno seguinte."
            }
        }
    },

    # =========================409
    "pikachu": {
        "nome": "Pikachu",
        "origem": "Pokémon",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 2,
        "max_star": 7,
        "hp": 85,
        "atk": 30,
        "matk": 55,
        "def": 15,
        "spd": 40,
        "crt": 10,
        "habilidade": {
            "nome": "Choque do Trovão",
            "descricao": "Libera uma descarga de eletricidade estática. Causa 120% de MATK e tem 35% de chance de atordoar (stun/paralisar) o alvo por 1 turno."
        },
        "evolucoes": {
            3: {
                "nome": "Agilidade Eletrizante",
                "descricao": "Corre de forma confusa deixando rastros de luz. Concede um bônus que aumenta a sua própria velocidade (SPD) e evasão em 20%."
            },
            5: {
                "nome": "Explosão de Trovão Supremo",
                "descricao": "Concentra as energias da chuva elétrica. O choque aumenta a potência para 160% de MATK e eleva a chance de Atordoar para colossais 50%."
            }
        }
    },

    # =========================410
    "tatsuya_shiba": {
        "nome": "Tatsuya Shiba",
        "origem": "Mahouka",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 60,
        "matk": 95,
        "def": 35,
        "spd": 45,
        "crt": 25,
        "habilidade": {
            "nome": "Material Burst de Decomposição",
            "descricao": "Decompõe a massa de matéria do alvo e converte em energia letal. Causa 250% de MATK, ignorando completamente imunidades, escudos e as defesas mágicas do alvo."
        },
        "evolucoes": {
            7: {
                "nome": "Magia de Regrowth (Recreação)",
                "descricao": "Lê os dados da magia base e reverte o universo local a instantes atrás. Restaura instantaneamente 100% de todo o HP perdido de um aliado alvo ou si mesmo no turno."
            }
        }
    },

    # =========================411
    "evangeline": {
        "nome": "Evangeline A.K. McDowell",
        "origem": "UQ Holder",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 135,
        "atk": 35,
        "matk": 80,
        "def": 30,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Nevasca do Gelo Eterno",
            "descricao": "A deusa vampiresca imortal sopra uma nevasca congelante do submundo glacial. Causa 170% de MATK em todos os inimigos e tem 30% de chance de congelar (stun) por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Magia Das Trevas (Absorção Absoluta)",
                "descricao": "Magia Erabotea se mescla com magia de vampiro. Ela absorve energias direcionadas a si, convertendo 30% do MATK mágico do oponente em bônus para si mesma por 3 turnos."
            }
        }
    },

    # =========================412
    "ira_gamagori": {
        "nome": "Ira Gamagori",
        "origem": "Kill la Kill",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 170,
        "atk": 50,
        "matk": 0,
        "def": 60,
        "spd": 15,
        "crt": 5,
        "habilidade": {
            "nome": "Shackle Regalia em Guarda",
            "descricao": "Entra em postura inabalável fechada nas suas vestes. Atrai provocação de todos os inimigos (Taunt) e ganha escudo que absorve e reduz o dano sofrido em 40% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Scourge Regalia: A Fúria",
                "descricao": "Ao abrir a sua vestimenta cheia de farpas, o chicote de aço se solta brutalmente. Causa 150% de ATK em área devolvendo em choque massivo o dano recebido enquanto defendia."
            }
        }
    },

    # =========================413
    "reiner_braun": {
        "nome": "Reiner Braun",
        "origem": "Shingeki no Kyojin",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 180,
        "atk": 55,
        "matk": 0,
        "def": 70,
        "spd": 14,
        "crt": 5,
        "habilidade": {
            "nome": "A Pele de Titã Encouraçado",
            "descricao": "Endurece a pele na forma do famoso Titã blindado de Marley. Ganha um escudo impenetrável de 35% do seu HP Máximo e recebe imunidade a sangramento por 3 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Investida Esmagadora de Gigante",
                "descricao": "Corre em alta velocidade arremessando toda sua carcaça dura na muralha inimiga. Causa 160% de ATK, destrói escudos físicos e atordoa o alvo principal na porrada."
            }
        }
    },

    # =========================414
    "wobbuffet": {
        "nome": "Wobbuffet",
        "origem": "Pokémon",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 1,
        "max_star": 7,
        "hp": 160,
        "atk": 0,
        "matk": 0,
        "def": 40,
        "spd": 5,
        "crt": 0,
        "habilidade": {
            "nome": "Counter: Devolver na Mesma Moeda",
            "descricao": "Sua postura é 100% defensiva pura. Reflete 100% do dano recebido de volta ao inimigo que o atacou com o dobro de força kármica (absorve dano refletir)."
        },
        "evolucoes": {
            3: {
                "nome": "Destiny Bond (Ligação Fatal)",
                "descricao": "Ao morrer por golpe do inimigo, desfere uma maldição de punição cármica suprema, executando com 50% de chance o inimigo responsável."
            },
            5: {
                "nome": "Safeguard: Escudo Sagrado Místico",
                "descricao": "Usa seu corpo macio como isolante psíquico para a sua party aliada. Protege o grupo dando imunidade absoluta a efeitos negativos (Debuffs) por 2 turnos."
            }
        }
    },

    # =========================415
    "jinbe": {
        "nome": "Jinbe",
        "origem": "One Piece",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 175,
        "atk": 65,
        "matk": 30,
        "def": 60,
        "spd": 20,
        "crt": 10,
        "habilidade": {
            "nome": "Karatê de Água: Bloqueio Marítimo",
            "descricao": "Suga a umidade do ar. Concede um escudo à equipe que absorve danos elementais de fogo e cura as feridas de combate aliadas em 15% do HP máximo de todos os heróis."
        },
        "evolucoes": {
            5: {
                "nome": "Vagabond Drill (Tritão)",
                "descricao": "Seu soco de água vibra direto no interior líquido do alvo, furando peles grossas. Desfere 170% de ATK e atinge ignorando totalmente todas as defesas de blindagem do alvo."
            }
        }
    },

    # =========================416
    "superalloy_darkshine": {
        "nome": "Superalloy Darkshine",
        "origem": "One Punch Man",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 200,
        "atk": 70,
        "matk": 0,
        "def": 90,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Brilho Muscular Deslumbrante",
            "descricao": "Tensiona seus músculos banhados a óleo para repelir ferro e balas. Atrai provocação (Taunt) absoluta e fica imune a qualquer ataque que não seja um acerto crítico por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Tackle Duplo Sombrio Místico",
                "descricao": "Usa suas duas toneladas de carne endurecida para obliterar com o ombro as defesas da frente. Avança atropelando tudo e causa dano físico crítico massivo de 200% de ATK empurrando o alvo no relógio de batalha."
            }
        }
    },

    # =========================417
    "retsu_unohana": {
        "nome": "Retsu Unohana",
        "origem": "Bleach",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 5,
        "max_star": 7,
        "hp": 160,
        "atk": 90,
        "matk": 70,
        "def": 35,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Minazuki: Shikai Esquadrão Médico",
            "descricao": "Libera a cura esbranquiçada de sua raia espiritual na quadra e envolve toda a tropa. Cura 35% do HP máximo de todos os aliados e limpa todos os efeitos maldosos de veneno e sangramento."
        },
        "evolucoes": {
            7: {
                "nome": "Minazuki: Bankai da Morte Original",
                "descricao": "O lado Kenpachi assassino sangrento aflora a essência do combate em feridas eternas. Seus ataques normais passam a curar a equipe em 50% do dano brutal causado às defesas oponentes."
            }
        }
    },

    # =========================418
    "hotaru_tomoe": {
        "nome": "Hotaru Tomoe",
        "origem": "Sailor Moon",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 125,
        "atk": 15,
        "matk": 75,
        "def": 30,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Cura Através da Destruição Escura",
            "descricao": "Sua luz estelar sombria destrói para reconstruir as vidas feridas em campo. Sacrifica 20% do próprio HP para reviver um aliado morto e curar todos os outros aliados vivos com escudo místico em 25%."
        },
        "evolucoes": {
            5: {
                "nome": "O Silêncio de Saturno Escudo",
                "descricao": "O gládio letal da morte repousa como muralha cósmica de contenção inquebrável. Aplica um escudo de 30% do HP Máximo de Hotaru na party inteira que silencia por 1 turno quem se atrever a atacar as barreiras de luz."
            }
        }
    },

    # =========================419
    "recovery_girl": {
        "nome": "Recovery Girl",
        "origem": "Boku no Hero Academia",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 105,
        "atk": 5,
        "matk": 45,
        "def": 20,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Beijo de Cura Médica Acelerada",
            "descricao": "Força a super regeneração natural orgânica e exaustiva a funcionar às pressas! Restaura 40% do HP de um aliado selecionado e anula instantaneamente os debuffs cruéis como lentidão ou atordoamento no grupo."
        },
        "evolucoes": {
            3: {
                "nome": "Experiência de Suporte da U.A.",
                "descricao": "Seus conselhos aos feridos são inestimáveis e cruciais. Concede um buff de +15% bônus passivo e duradouro em todas as curas que o grupo inteiro desferir."
            },
            5: {
                "nome": "Repouso Forçado Autorizado!",
                "descricao": "Gritando para repousar de vez, remove todos os debuffs do aliado curado instantaneamente e concede uma recuperação menor (10% HP) a cada começo da rodada seguinte."
            }
        }
    },

    # =========================420
    "akiko_yosano": {
        "nome": "Akiko Yosano",
        "origem": "Bungo Stray Dogs",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 40,
        "matk": 40,
        "def": 22,
        "spd": 25,
        "crt": 10,
        "habilidade": {
            "nome": "Thou Shalt Not Die (Você Não Vai Morrer)",
            "descricao": "Cura drástica e letal. Cura totalmente a equipe inteira em 50% do HP e, se uma morte tiver ocorrido na rodada presente, ela ressuscita esse infeliz aliado estripado com 50% de vida curando os sangramentos!"
        },
        "evolucoes": {
            5: {
                "nome": "Medicina Agressiva Cortante e Furiosa",
                "descricao": "Abusa da brutalidade de cura sacando o cutelo e o machado cirúrgico para a batalha infernal. Ela ataca os inimigos causando um golpe letal de 120% ATK físico de área no esquadrão, aplicando sangramento massivo."
            }
        }
    },
    # =========================421
    "hyoma_chigiri_bl": {
        "nome": "Hyoma Chigiri",
        "origem": "Blue Lock",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 65,
        "matk": 10,
        "def": 18,
        "spd": 45,
        "crt": 15,
        "habilidade": {
            "nome": "Aceleração Extrema",
            "descricao": "Causa 140% de ATK e ganha um bônus de +25% de SPD por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Fórmula do Velocista",
                "descricao": "Seu sprint é imparável. Aumenta o dano causado em 30% contra inimigos com SPD menor que a sua."
            }
        }
    },

    # =========================422
    "isagi_yoichi_bl": {
        "nome": "Yoichi Isagi",
        "origem": "Blue Lock",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 60,
        "matk": 20,
        "def": 25,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Metavisão e Consciência",
            "descricao": "Analisa o campo perfeitamente. Concede +40% de precisão e evasão (dodge) para toda a sua equipe por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Chute Direto Perfeito",
                "descricao": "Isagi prevê o momento exato do gol. Seu ataque seguinte causa 200% de ATK e ignora defesas físicas do oponente."
            }
        }
    },

    # =========================423
    "rensuke_kunigami_bl": {
        "nome": "Rensuke Kunigami",
        "origem": "Blue Lock",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 3,
        "max_star": 7,
        "hp": 115,
        "atk": 70,
        "matk": 0,
        "def": 25,
        "spd": 20,
        "crt": 12,
        "habilidade": {
            "nome": "Poder do Herói",
            "descricao": "Desfere um chute físico brutal. Causa 150% de ATK e possui 20% de chance de atordoar (Stun) o alvo principal."
        },
        "evolucoes": {
            5: {
                "nome": "Esmagamento Físico",
                "descricao": "Kunigami adota uma postura mais violenta. Seus ataques normais passam a quebrar 30% da armadura do inimigo."
            }
        }
    },

    # =========================424
    "meguru_bachira_bl": {
        "nome": "Meguru Bachira",
        "origem": "Blue Lock",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 72,
        "matk": 10,
        "def": 20,
        "spd": 42,
        "crt": 20,
        "habilidade": {
            "nome": "Drible do Monstro",
            "descricao": "Finta os adversários com movimentos caóticos. Causa 160% de ATK e reduz a velocidade de ação de 2 inimigos em 30%."
        },
        "evolucoes": {
            5: {
                "nome": "Estado de Flow Instintivo",
                "descricao": "O monstro desperta. Passa a ignorar provocações (Taunt) e ganha +30% de chance de acerto crítico na arena."
            }
        }
    },

    # =========================425
    "shoei_barou_bl": {
        "nome": "Shoei Barou",
        "origem": "Blue Lock",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 78,
        "matk": 0,
        "def": 28,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "O Rei da Quadra",
            "descricao": "Barou atropela tudo pela frente. Causa 180% de ATK físico e aumenta seu próprio ataque em 20% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Ego do Vilão Devorador",
                "descricao": "Quanto mais sua party sofre, mais ele brilha. Causa dano extra se algum aliado tiver sido ferido nesta rodada."
            }
        }
    },

    # =========================426
    "reo_mikage_bl": {
        "nome": "Reo Mikage",
        "origem": "Blue Lock",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 35,
        "matk": 55,
        "def": 22,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Cópia Versátil Camaleão",
            "descricao": "Copia técnicas de suporte. Cura 25% do HP máximo de toda a equipe e aumenta a defesa do grupo em 15%."
        },
        "evolucoes": {
            5: {
                "nome": "Sinergia de Gênio",
                "descricao": "Reo refina suas cópias táticas. Passa a copiar os bônus (buffs) de ataque do inimigo de maior poder e aplicá-los à sua party."
            }
        }
    },

    # =========================427
    "seichiro_nagi_bl": {
        "nome": "Seichiro Nagi",
        "origem": "Blue Lock",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 85,
        "matk": 10,
        "def": 25,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Recepção de Gênio do Espaço",
            "descricao": "Domina o campo controlando ataques aéreos. Causa 220% de ATK e ignora 50% da blindagem defensiva oponente."
        },
        "evolucoes": {
            7: {
                "nome": "Contra-Ataque Criativo Nulo",
                "descricao": "A sua intuição preguiçosa é mortal. Sempre que recebe um ataque físico, revida automaticamente causando 150% de ATK no agressor."
            }
        }
    },

    # =========================428
    "kenyu_yukimiya_bl": {
        "nome": "Kenyu Yukimiya",
        "origem": "Blue Lock",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 45,
        "matk": 10,
        "def": 15,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Drible de Gyro Cortante",
            "descricao": "Seus movimentos geram ilusões visuais. Causa 110% de ATK e reduz a precisão (cegueira) do alvo em 20% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Imperador Solitário",
                "descricao": "Aumenta a própria velocidade (SPD) e adiciona +15% de chance de acerto crítico nos ataques."
            },
            5: {
                "nome": "Corte Vertical Decisivo",
                "descricao": "Foca-se puramente no alvo, fazendo os seus próximos ataques ignorarem 30% da armadura física permanentemente."
            }
        }
    },

    # =========================429
    "itoshi_rin_bl": {
        "nome": "Itoshi Rin",
        "origem": "Blue Lock",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 82,
        "matk": 30,
        "def": 25,
        "spd": 35,
        "crt": 25,
        "habilidade": {
            "nome": "Marionetista do Campo Frio",
            "descricao": "Força os oponentes a exporem fraquezas. Causa 190% de ATK focado na retaguarda e reduz a DEF deles em 40%."
        },
        "evolucoes": {
            7: {
                "nome": "Estado de Fluxo Destrutivo (Flow)",
                "descricao": "Seu ego nojento assume. Dispara projéteis que causam dano verdadeiro em área, atingindo e quebrando qualquer escudo inimigo."
            }
        }
    },

    # =========================430
    "ryusei_shidou_bl": {
        "nome": "Ryusei Shidou",
        "origem": "Blue Lock",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 90,
        "matk": 10,
        "def": 28,
        "spd": 34,
        "crt": 20,
        "habilidade": {
            "nome": "Extrema Volúpia de Chute",
            "descricao": "Desfere chutes acrobáticos em qualquer ângulo sem olhar. Causa 230% de ATK e possui acerto garantido mesmo contra inimigos furtivos."
        },
        "evolucoes": {
            7: {
                "nome": "Demônio da Grande Área (ZG Drive)",
                "descricao": "Entra em transe de destruição total. Seus golpes passam a dar dano em área com 50% de impacto e ele cura 10% do HP a cada abate."
            }
        }
    },

    # =========================431
    "tabito_karasu_bl": {
        "nome": "Tabito Karasu",
        "origem": "Blue Lock",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 2,
        "max_star": 7,
        "hp": 95,
        "atk": 35,
        "matk": 20,
        "def": 20,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Análise do Corvo Tático",
            "descricao": "Localiza os pontos fracos. Marca o inimigo com menor DEF, reduzindo a defesa e velocidade dele em 25%."
        },
        "evolucoes": {
            3: {
                "nome": "Finta de Pressão Fria",
                "descricao": "Aumenta a precisão de todos os aliados da party em 15% por 2 rodadas completas."
            },
            5: {
                "nome": "Galinheiro das Sombras",
                "descricao": "As suas táticas elevam o grupo. Concede um buff contínuo de +20% de ATK físico para a sua equipe enquanto ele estiver vivo na arena."
            }
        }
    },

    # =========================432
    "oliver_aiku_bl": {
        "nome": "Oliver Aiku",
        "origem": "Blue Lock",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 150,
        "atk": 40,
        "matk": 0,
        "def": 60,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Muralha Sentinela Diamante",
            "descricao": "Lê os movimentos defensivos e salta na trajetória. Atrai provocação (Taunt) e reduz em 40% todo o dano recebido nesta rodada."
        },
        "evolucoes": {
            5: {
                "nome": "Defesa Aérea Suprema Absoluta",
                "descricao": "Protege todos à sua volta. Cria escudos protetores para a party inteira equivalentes a 25% de seu HP máximo e os torna imunes a atordoamento."
            }
        }
    },

    # =========================433
    "julian_loki_bl": {
        "nome": "Julian Loki",
        "origem": "Blue Lock",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 88,
        "matk": 10,
        "def": 25,
        "spd": 65,
        "crt": 20,
        "habilidade": {
            "nome": "Velocidade Deus Divina",
            "descricao": "Dispara numa velocidade imperceptível. Causa 200% de ATK e ganha um turno extra imediato, sem permitir reações inimigas."
        },
        "evolucoes": {
            7: {
                "nome": "Luz Francesa Intocável Veloz",
                "descricao": "Sua esquiva supera qualquer lei física. Concede +100% de evasão ativa por 1 turno e seus ataques cortam as curas do inimigo."
            }
        }
    },

    # =========================434
    "itoshi_sae_bl": {
        "nome": "Itoshi Sae",
        "origem": "Blue Lock",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 30,
        "matk": 85,
        "def": 28,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Futebol Lindo e Estético",
            "descricao": "Usa cálculos mágicos no campo de batalha. Causa 180% de MATK em área a todos os inimigos e reduz a SPD deles em 30% por 2 turnos."
        },
        "evolucoes": {
            7: {
                "nome": "Gênio Cirúrgico da Magia Nova",
                "descricao": "Tudo acontece no tempo que ele quer. Restaura completamente as recargas de magias (cooldowns) do seu líder aliado ao custo de mana."
            }
        }
    },

    # =========================435
    "noel_noa_bl": {
        "nome": "Noel Noa",
        "origem": "Blue Lock",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 80,
        "matk": 50,
        "def": 40,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Racionalidade Mecânica Fria",
            "descricao": "Apenas o poder lógico importa na guerra de Lugnica. Concede +50% de ATK para toda a equipe e os torna imunes a efeitos de controle (CC)."
        },
        "evolucoes": {
            7: {
                "nome": "Ambidestria Computada Lógica",
                "descricao": "Nenhum movimento é desperdiçado. O seu próximo ataque no 3º turno de batalha causa absurdos 300% de ATK com dano verdadeiro inevitável."
            }
        }
    },

    # =========================436
    "michael_kaiser_bl": {
        "nome": "Michael Kaiser",
        "origem": "Blue Lock",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 86,
        "matk": 20,
        "def": 25,
        "spd": 32,
        "crt": 30,
        "habilidade": {
            "nome": "Kaiser Impact Furioso",
            "descricao": "O tiro mais veloz e egoísta. Causa 250% de ATK físico concentrado em um único alvo da retaguarda, ignorando 100% de sua defesa de escudos."
        },
        "evolucoes": {
            7: {
                "nome": "Predador Rei Coroado Egoísta",
                "descricao": "Sua glória ofusca a todos. Sempre que derrotar um oponente, ele rouba o ATK do defunto, ganhando +25% de ATK extra pelo resto da luta."
            }
        }
    },

    # =========================437
    "lavinho_bl": {
        "nome": "Lavinho",
        "origem": "Blue Lock",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 78,
        "matk": 10,
        "def": 20,
        "spd": 48,
        "crt": 20,
        "habilidade": {
            "nome": "Drible Rítmico de Ginga",
            "descricao": "Foca nos ritmos loucos do corpo a corpo brasileiro. Causa 160% de ATK em ziguezague e confunde o alvo (ataca um aliado) por 1 turno."
        },
        "evolucoes": {
            5: {
                "nome": "Dançarino de Borboleta Gato",
                "descricao": "Ganhou agilidade felina. Aumenta a própria evasão em 50% e os seus contra-ataques agora curam-lhe a vida por um pouco."
            }
        }
    },

    # =========================438
    "bunny_iglesias_bl": {
        "nome": "Bunny Iglesias",
        "origem": "Blue Lock",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 85,
        "atk": 25,
        "matk": 0,
        "def": 15,
        "spd": 15,
        "crt": 5,
        "habilidade": {
            "nome": "Salto do Coelho Estiloso",
            "descricao": "Impulsiona as pernas para um ataque direto. Causa 210% de ATK no oponente mais próximo."
        },
        "evolucoes": {
            7: {
                "nome": "Estripador Leve de Defesas",
                "descricao": "Sua dedicação esmaga pedras. Ignora DEF e escudo, atacando diretamente na vida."
            }
        }
    },

    # =========================439
    "chris_prince_bl": {
        "nome": "Chris Prince",
        "origem": "Blue Lock",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 165,
        "atk": 50,
        "matk": 0,
        "def": 60,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Perfect Body Musculatura",
            "descricao": "Tensiona cada músculo em postura rígida. Atrai todos os ataques (Taunt), ganha escudos massivos e fica imune a atordoamento e silêncio."
        },
        "evolucoes": {
            5: {
                "nome": "O Herói Físico de 7 Estrelas",
                "descricao": "Sua perfeição biológica beira o grotesco. Cura 20% do seu próprio HP máximo ao final de cada turno que atuar como escudo do time."
            }
        }
    },

    # =========================440
    "marc_snuffy_bl": {
        "nome": "Marc Snuffy",
        "origem": "Blue Lock",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 55,
        "matk": 40,
        "def": 45,
        "spd": 28,
        "crt": 10,
        "habilidade": {
            "nome": "Estratégia Defensiva Máxima",
            "descricao": "Aplica o seu intelecto táctico supremo no campo. Aumenta a defesa geral (DEF) da equipa em 40% e anula os golpes críticos recebidos."
        },
        "evolucoes": {
            7: {
                "nome": "O Cérebro de Alexandria Escudo",
                "descricao": "Nada escapa à sua proteção. Concede instantaneamente um escudo místico e impenetrável sempre que o aliado mais fraco for atacado por magia."
            }
        }
    },

    # =========================441
    "don_lorenzo_bl": {
        "nome": "Don Lorenzo",
        "origem": "Blue Lock",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 150,
        "atk": 45,
        "matk": 0,
        "def": 58,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Drible Zumbi Sombrio",
            "descricao": "Lorenzo se contorce impedindo a passagem. Atrai aggro (Taunt) e reduz agressivamente o ataque do oponente que lhe bater em 30%."
        },
        "evolucoes": {
            5: {
                "nome": "O Devorador de Gênios Ladrão",
                "descricao": "Absorve os atributos inimigos. Rouba silenciosamente 20% do ATK e SPD do inimigo mais forte e repassa isso para si permanentemente."
            }
        }
    },

    # =========================442
    "charles_chevalier_bl": {
        "nome": "Charles Chevalier",
        "origem": "Blue Lock",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 15,
        "matk": 58,
        "def": 20,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Passe Preciso Mágico de Cura",
            "descricao": "Cruza curas exatas ignorando barreiras. Restaura 30% do poder de MATK na forma de HP para os dois aliados mais feridos do esquadrão."
        },
        "evolucoes": {
            5: {
                "nome": "Cálculo de Sinergia Ofensiva",
                "descricao": "Sua cura não apenas fecha feridas, mas levanta a moral. Aumenta em 25% o ATK e a taxa crítica do líder do grupo por 2 rodadas completas."
            }
        }
    },

    # =========================443
    "vivian_hugo_bl": {
        "nome": "Vivian Hugo",
        "origem": "Blue Lock",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 65,
        "matk": 70,
        "def": 35,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Aura da Nova Geração (New Gen 11)",
            "descricao": "Sua presença esmagadora dita o ritmo absoluto do jogo. Aumenta a velocidade de ação (SPD) e o ATK de todos os aliados em 40% e anula os buffs ativos dos inimigos."
        },
        "evolucoes": {
            7: {
                "nome": "Maestria Tática do Campo",
                "descricao": "A visão de um gênio de elite mundial. Anula automaticamente o primeiro ataque mágico em área que a sua party receber e concede 25% de cura de HP máximo como retaliação tática."
            }
        }
    },

    # =========================444
    "endou_mamoru_in": {
        "nome": "Endou Mamoru",
        "origem": "Inazuma Eleven",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 165,
        "atk": 35,
        "matk": 40,
        "def": 65,
        "spd": 15,
        "crt": 5,
        "habilidade": {
            "nome": "Mão Celestial (God Hand)",
            "descricao": "Cria uma muralha colossal de pura determinação e magia divina. Bloqueia completamente o primeiro ataque físico ou mágico fatal direcionado à equipe."
        },
        "evolucoes": {
            7: {
                "nome": "Majin The Hand: Mão Demoníaca",
                "descricao": "Invoca o demônio dourado de energia atrás de si. Além de defender a equipa inteira de magias, reflete 40% do dano das Calamidades e Chefes de volta."
            }
        }
    },

    # =========================445
    "gouenji_shuuya_in": {
        "nome": "Gouenji Shuuya",
        "origem": "Inazuma Eleven",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 82,
        "matk": 25,
        "def": 25,
        "spd": 26,
        "crt": 18,
        "habilidade": {
            "nome": "Furacão de Fogo de Ataque",
            "descricao": "Gouenji gira envolto em chamas vivas para chutar. Causa 200% de ATK físico a um único inimigo e inflige uma Queimadura severa de longo prazo."
        },
        "evolucoes": {
            7: {
                "nome": "Fogo Cruzado Fera",
                "descricao": "Seu fogo não pode ser apagado. Seus ataques normais passam a ignorar as resistências e armaduras mágicas de gelo ou água do oponente."
            }
        }
    },

    # =========================446
    "kiyama_hiroto_in": {
        "nome": "Kiyama Hiroto",
        "origem": "Inazuma Eleven",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 20,
        "matk": 76,
        "def": 22,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Ryuusei Blade (Lâmina Meteoro)",
            "descricao": "Hiroto descarrega chuvas de estrelas cadentes mágicas. Causa 160% de MATK em área na arena inimiga inteira e reduz a defesa de todos."
        },
        "evolucoes": {
            5: {
                "nome": "Supernova Alienígena Extrema",
                "descricao": "Concentre a força do universo inteiro em um alvo. Causa um dano mágico massivo colossal focado que derrete e pulveriza o inimigo com mais vida."
            }
        }
    },

    # =========================447
    "kidou_yuuto_in": {
        "nome": "Kidou Yuuto",
        "origem": "Inazuma Eleven",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 45,
        "matk": 55,
        "def": 28,
        "spd": 32,
        "crt": 10,
        "habilidade": {
            "nome": "Pinguins Imperiais Nº2 Ofensivo",
            "descricao": "Comanda pinguins malucos mágicos do subsolo que mordem a linha inimiga. Causa 180% de ATK em área e tem chance de atordoar alvos fracos."
        },
        "evolucoes": {
            5: {
                "nome": "Illusion Ball de Defesa",
                "descricao": "Cria ilusões óticas usando magia de zona de campo. Concede impressionantes +40% de evasão (Dodge) mágica para a sua party inteira por 2 rodadas."
            }
        }
    },

    # =========================448
    "fubuki_shirou_in": {
        "nome": "Fubuki Shirou",
        "origem": "Inazuma Eleven",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 50,
        "matk": 40,
        "def": 52,
        "spd": 28,
        "crt": 15,
        "habilidade": {
            "nome": "Chão de Gelo Glacial",
            "descricao": "Fubuki desliza espalhando gelo espesso na arena. Causa 150% de ATK nos oponentes e aplica uma lentidão brutal de 50% de SPD na retaguarda."
        },
        "evolucoes": {
            7: {
                "nome": "Vendaval Eterno (Atsuya)",
                "descricao": "Atsuya assume a liderança do corpo. Troca sua postura de Tank para Atacante, buffa todos os status em 50."
            }
        }
    },

    # =========================449
    "rococo_urupa_in": {
        "nome": "Rococo Urupa",
        "origem": "Inazuma Eleven",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 170,
        "atk": 45,
        "matk": 30,
        "def": 62,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Mão de X Escudo Vermelho",
            "descricao": "Bloqueia e agarra tudo com força magnética de energia pura. Atrai ataques para si (Taunt) e reduz pela metade os ferimentos da party nesta rodada."
        },
        "evolucoes": {
            7: {
                "nome": "X Blast: O Contra-Ataque do Abismo",
                "descricao": "Rococo não só defende como destrói quem ataca. Devolve os ataques mágicos dos inimigos em forma de um feixe de 250% de MATK instantâneo."
            }
        }
    },

    # =========================450
    "kazemaru_ichirouta_in": {
        "nome": "Kazemaru Ichirouta",
        "origem": "Inazuma Eleven",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 62,
        "matk": 15,
        "def": 18,
        "spd": 46,
        "crt": 15,
        "habilidade": {
            "nome": "Deslize de Vento Veloz",
            "descricao": "Cria tufões de vento correndo por baixo das pernas do inimigo. Causa 140% de ATK e concede aumento de 30% em sua própria agilidade (SPD)."
        },
        "evolucoes": {
            5: {
                "nome": "Dança do Deus do Vento",
                "descricao": "Transforma brisa em lâminas tempestuosas. Seus golpes básicos passam a aplicar hemorragia cortante (Sangramento) contínua nos adversários lentos."
            }
        }
    },

    # =========================451
    "fudou_akio_in": {
        "nome": "Fudou Akio",
        "origem": "Inazuma Eleven",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 50,
        "matk": 30,
        "def": 22,
        "spd": 26,
        "crt": 15,
        "habilidade": {
            "nome": "Estratégia Suja da Royal Academy",
            "descricao": "Usa táticas que beiram a infração de regras. Cegue os inimigos com artifícios de campo, reduzindo a precisão em 30% de até 3 inimigos de forma covarde."
        },
        "evolucoes": {
            5: {
                "nome": "Sacrifício Pelo Poder Sujo",
                "descricao": "Aumenta drasticamente o ataque físico de todos da equipe, ao custo de baixar ligeiramente as defesas do seu próprio time na frente de batalha."
            }
        }
    },

    # =========================452
    "tobitaka_seiya_in": {
        "nome": "Tobitaka Seiya",
        "origem": "Inazuma Eleven",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 2,
        "max_star": 7,
        "hp": 95,
        "atk": 25,
        "matk": 10,
        "def": 30,
        "spd": 12,
        "crt": 5,
        "habilidade": {
            "nome": "Sopro do Demônio Defesa (Shinkuuma)",
            "descricao": "Chuta o ar e invoca sucções vácuas densas que atraem e mitigam flechas ou fogo inimigo atraindo o aggro levemente."
        },
        "evolucoes": {
            3: {
                "nome": "Bravura do Ex-Gangster Calejado",
                "descricao": "Seu histórico na rua não o deixa temer pancada. Ganha um aumento sólido e duradouro na DEF física natural da sua ficha tática."
            },
            5: {
                "nome": "Vácuo Místico Espiritual Mágico",
                "descricao": "Além de golpes físicos, ele aprende a blindar magia. O Shinkuuma agora absorve e anula 1 feitiço mágico destrutivo por duelo sem sofrer arranhões."
            }
        }
    },

    # =========================453
    "matsukaze_tenma_in": {
        "nome": "Matsukaze Tenma",
        "origem": "Inazuma Eleven",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 52,
        "matk": 48,
        "def": 25,
        "spd": 32,
        "crt": 12,
        "habilidade": {
            "nome": "Brisa Suave Veloz (Soyokaze Step)",
            "descricao": "Avança criando redemoinhos de vento suave ao redor de sua party. Concede +30% de SPD e +20% de evasão ativa a todos por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Vento Mach: Mach Wind Divino",
                "descricao": "Sua liderança inspira chutar tempestades. Causa 180% de ATK ignorando magia e limpa de vez todos os debuffs aplicados ao próprio esquadrão."
            }
        }
    },

    # =========================454
    "tsurugi_kyousuke_in": {
        "nome": "Tsurugi Kyousuke",
        "origem": "Inazuma Eleven",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 80,
        "matk": 20,
        "def": 24,
        "spd": 28,
        "crt": 18,
        "habilidade": {
            "nome": "Queda Mortal da Espada (Death Drop)",
            "descricao": "Chuta de cabeça para baixo gerando auras negras imponentes. Causa 170% de ATK e aplica sangramento perfurante pesado e cruel nos defensores."
        },
        "evolucoes": {
            5: {
                "nome": "Espadachim Santo Lancelot Desperto",
                "descricao": "Invoca o Cavaleiro Lancelot no campo. Seus golpes adquirem peso místico e causam dano físico em área massivo esmagando a defesa do boss."
            }
        }
    },

    # =========================455
    "fei_rune_in": {
        "nome": "Fei Rune",
        "origem": "Inazuma Eleven",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 25,
        "matk": 60,
        "def": 20,
        "spd": 32,
        "crt": 10,
        "habilidade": {
            "nome": "Coelho Saltitante Suave (Bouncer Rabbit)",
            "descricao": "Fei invoca coelhinhos energéticos que batem nas cabeças aliadas para os revigorar. Cura os guerreiros em 30% do MATK levemente."
        },
        "evolucoes": {
            5: {
                "nome": "Mixi Max Tyrano Temporal Extremo",
                "descricao": "Ele une magia temporal à cura de grupo. Acelera drasticamente a velocidade de ação (SPD) de toda a equipe a curar."
            }
        }
    },

    # =========================456
    "shindou_takuto_in": {
        "nome": "Shindou Takuto",
        "origem": "Inazuma Eleven",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 18,
        "matk": 68,
        "def": 18,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Batuta Divina Tática (Kami no Takuto)",
            "descricao": "Shindou rege a arena orquestrando com as mãos no ar. Causa 130% de MATK a todos os inimigos e atordoa (Stun) o infeliz alvo de menor DEF."
        },
        "evolucoes": {
            5: {
                "nome": "Fortissimo Destruidor Pianista",
                "descricao": "As notas musicais ganham o peso de bigornas caindo do teto. Suas magias sonoras passam a estilhaçar e ignorar as defesas mágicas ativas do oponente."
            }
        }
    },

    # =========================457
    "zanark_avalonic_in": {
        "nome": "Zanark Avalonic",
        "origem": "Inazuma Eleven",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 86,
        "matk": 30,
        "def": 30,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Super Catch de Desastre Absoluto",
            "descricao": "Zanark condensa energia caótica em um impacto vulcânico no alvo. Causa 220% de ATK brutal esmagando 40% da DEF do alvo por longos 2 turnos infernais."
        },
        "evolucoes": {
            7: {
                "nome": "Great Max na Mim Sangue Puro",
                "descricao": "A anomalia temporal liberta a sua fúria real sem os selos vermelhos. Sempre que seu HP cai abaixo de 30%, seu ATK salta em absurdos +50%."
            }
        }
    },

    # =========================458
    "kageyama_tobio_hq": {
        "nome": "Kageyama Tobio",
        "origem": "Haikyuu!!",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 35,
        "matk": 60,
        "def": 24,
        "spd": 32,
        "crt": 10,
        "habilidade": {
            "nome": "O Levantador Genial Preciso",
            "descricao": "Posiciona os aliados com precisão cirúrgica impecável. Concede um buff letal massivo de +50% no poder de ataques físicos puros de todos do grupo."
        },
        "evolucoes": {
            5: {
                "nome": "Arremesso do Rei Solitário Ciente",
                "descricao": "Ele entende agora como não ser um rei solitário de ditador cruel. Amplia as taxas de crítico e cura levemente todos os aliados da party que acertarem hits cruciais."
            }
        }
    },

    # =========================459
    "ushijima_wakatoshi_hq": {
        "nome": "Ushijima Wakatoshi",
        "origem": "Haikyuu!!",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 90,
        "matk": 0,
        "def": 35,
        "spd": 20,
        "crt": 18,
        "habilidade": {
            "nome": "O Canhão Cortante Canhoto Imbatível",
            "descricao": "Ushijima desfere um golpe esmagador na diagonal da linha esquerda em força bruta pura e simples cruel. Causa 230% de ATK em pancada focada blindada de destrói escudos."
        },
        "evolucoes": {
            7: {
                "nome": "O Orgulho Absoluto Mítico de Shiratorizawa",
                "descricao": "Sua força assusta a guarda de qualquer inimigo em campo no bloqueio frontal. Seus ataques normais passam e atordoam defensores covardes no local por medo total do arremate."
            }
        }
    },

    # =========================460
    "miya_atsumu_hq": {
        "nome": "Miya Atsumu",
        "origem": "Haikyuu!!",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 48,
        "matk": 55,
        "def": 25,
        "spd": 34,
        "crt": 15,
        "habilidade": {
            "nome": "Saque Híbrido Enganoso Duplo",
            "descricao": "Altera o peso da investida no último segundo da queda. Reduz drasticamente a precisão da retaguarda oponente e causa confusão nas trincheiras atiradoras dos alvos alheios."
        },
        "evolucoes": {
            5: {
                "nome": "O Maestro das Raposas Místicas",
                "descricao": "Acelera as peças certas do seu tabuleiro de xadrez na quadra sem esforço extra nenhum de mana bônus. Concede SPD permanente e segura a toda a sua equipe enquanto ele ditar os tempos e movimentos rítmicos."
            }
        }
    },

    # =========================461
    "hinata_shoyo_hq": {
        "nome": "Hinata Shoyo",
        "origem": "Haikyuu!!",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 95,
        "atk": 65,
        "matk": 10,
        "def": 18,
        "spd": 48,
        "crt": 18,
        "habilidade": {
            "nome": "Isca Suprema Veloz Saltitante",
            "descricao": "Corre de um lado para o outro atraindo os olhares de predadores perigosos do campo alheio para fora de foco. Aumenta massivamente a taxa de chance crítica da equipe em generosos +30% limpos e ágeis."
        },
        "evolucoes": {
            5: {
                "nome": "Ataque Rápido Divino Acelerado Cortante",
                "descricao": "As pernas funcionam como molas inatingíveis pelos radares lentos. Concede, mediante esforço físico extremo garantido, um turno mágico ou físico extra imediatamente após desferir o último ataque e salto celestial nas frentes."
            }
        }
    },

    # =========================462
    "sakusa_kiyoomi_hq": {
        "nome": "Sakusa Kiyoomi",
        "origem": "Haikyuu!!",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 75,
        "matk": 20,
        "def": 22,
        "spd": 28,
        "crt": 30,
        "habilidade": {
            "nome": "Disparo Efeito Rotativo Chicote Severo",
            "descricao": "Gira os punhos e articulações absurdas disparando ataques repulsivos que enganam as luvas de prata do oponente blindado frontal. Causa 170% de ATK e ignora cruelmente 40% da defesa física nula do bloqueador cego."
        },
        "evolucoes": {
            5: {
                "nome": "O Jogador Mestre Precavido e Higiênico Lento",
                "descricao": "Sua aversão a toxinas afia o seu sistema imunológico até o limite absoluto intransponível no inferno de sangue mágico. Fica total e eternamente imune contra envenenamento e sangramento de monstros ou fendas podres."
            }
        }
    },

    # =========================463
    "bokuto_kotaro_hq": {
        "nome": "Bokuto Kotaro",
        "origem": "Haikyuu!!",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 125,
        "atk": 82,
        "matk": 0,
        "def": 28,
        "spd": 24,
        "crt": 20,
        "habilidade": {
            "nome": "Corte de Impacto Diagonal Brutal Furioso",
            "descricao": "Bate rasgando espaços cegos onde corujas não caem normalmente sem rasgar teias no vazio cósmico. Causa um dano físico altíssimo focado que totaliza 180% de ATK bruto e também ignora a mágica defensiva."
        },
        "evolucoes": {
            5: {
                "nome": "Estrela Emo da Depressão de Ás",
                "descricao": "Oscila entre tristeza e deus. Quando o seu vigor atinge níveis fracos por ataques inimigos sujos e seu HP cai de verdade e severamente para baixo dos 50%, ele acorda enfurecido curando partes e garantindo +ATK passivo limpo e constante na luta."
            }
        }
    },

    # =========================464
    "hoshiumi_korai_hq": {
        "nome": "Hoshiumi Korai",
        "origem": "Haikyuu!!",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 98,
        "atk": 68,
        "matk": 10,
        "def": 18,
        "spd": 44,
        "crt": 22,
        "habilidade": {
            "nome": "O Pequeno Gigante Planador Flutuante Célere",
            "descricao": "Hoshiumi salta acima das redes montanhosas parando o tempo no ar como gaivota solta no temporal mágico. Causa 140% de ATK e ganha generosos buffs críticos nos seus hits mortais de arremesso aéreo curvo veloz."
        },
        "evolucoes": {
            5: {
                "nome": "Absoluta Versatilidade Técnica Global de Campo",
                "descricao": "Domina de forma genial todas as áreas obscuras da partida limpa. Ele cura sua vida de forma de vampiro em porcentagens seguras sempre que arrancar sangue ou ouro do monstro e chefe atingido na cabeça das nuvens cegas."
            }
        }
    },

    # =========================465
    "kozume_kenma_hq": {
        "nome": "Kozume Kenma",
        "origem": "Haikyuu!!",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 3,
        "max_star": 7,
        "hp": 90,
        "atk": 25,
        "matk": 55,
        "def": 20,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Análise Cérebro Analítico Gamer do Gato Oculto",
            "descricao": "Joga a vida como simulador sem suar a testa, diminuindo o processamento e a CPU mental dos orcs ou deuses oponentes burros. Reduz de forma agressiva a SPD e o ATK inimigo em 30% em combates pesados no barro tático."
        },
        "evolucoes": {
            5: {
                "nome": "Estratégia Camuflagem Nível Boss Mestre do Teclado",
                "descricao": "Atribui códigos bônus de furtividade hacker ao grupo aliado ignorado pelas bestas de Lugnica. Concede Evasão aprimorada (+Dodge) para manter seu teclado limpo de poeira cósmica."
            }
        }
    },

    # =========================466
    "kuroo_tetsuro_hq": {
        "nome": "Kuroo Tetsuro",
        "origem": "Haikyuu!!",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 135,
        "atk": 40,
        "matk": 20,
        "def": 45,
        "spd": 22,
        "crt": 5,
        "habilidade": {
            "nome": "O Bloqueio Leitura Negra do Gato Sujo Astuto Mestre",
            "descricao": "Lê o ombro do demônio, saltando antes de magia ou punho fechar nos peitos frágeis dos magos velhos da base alheia no mato de espinhos cruzados. Atrai ameaça total do campo provocando todos para os braços fortes e escudos de mana brancos do seu casaco real."
        },
        "evolucoes": {
            5: {
                "nome": "Muralha Felina Chumbo Maciço Invencível do Sol Negro",
                "descricao": "A dor de uma farpa é nula. Mitiga o primeiro impacto destrutivo violento no round até zero, provando que gato de telhado sobrevive a pedrada mágica limpa."
            }
        }
    },

    # =========================467
    "yaku_morisuke_hq": {
        "nome": "Yaku Morisuke",
        "origem": "Haikyuu!!",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 2,
        "max_star": 7,
        "hp": 110,
        "atk": 20,
        "matk": 15,
        "def": 40,
        "spd": 25,
        "crt": 5,
        "habilidade": {
            "nome": "Recepção Guardião Líbero de Sangue Sujo da Zaga Final de Batalha",
            "descricao": "Coloca a cara na terra pelo grupo e salva o atirador pego de surpresa. Redireciona danos severos ao chão e cura danos físicos rasos que sofre do monstro tonto feio."
        },
        "evolucoes": {
            3: {
                "nome": "Manchete de Ferro",
                "descricao": "Aumenta a DEF permanentemente e ignora veneno."
            },
            5: {
                "nome": "A Limpeza Espiritual Silenciosa Rara de Pés Descalços Heróicos",
                "descricao": "Sua persistência desfaz magias de silêncio e atordoamentos passivamente, libertando as pedras do controle arcano bruto impiedoso em Lugnica suja."
            }
        }
    },

    # =========================468
    "akashi_seijuro_knb": {
        "nome": "Akashi Seijuro",
        "origem": "Kuroko no Basket",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 55,
        "matk": 65,
        "def": 28,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Olho do Imperador",
            "descricao": "Akashi prevê o futuro dos movimentos do oponente. Reduz a velocidade de ação (SPD) e a evasão de todos os inimigos em 30% por 2 turnos, e atordoa (Stun) o inimigo de maior ATK por 1 turno."
        },
        "evolucoes": {
            7: {
                "nome": "O Zone Absoluto",
                "descricao": "Sua ordem é absoluta e inspira temor e eficiência. Aumenta o ATK e a SPD de toda a sua equipe em 40% por 3 turnos, ignorando qualquer redução de atributos aplicada pelos adversários."
            }
        }
    },

    # =========================469
    "aomine_daiki_knb": {
        "nome": "Aomine Daiki",
        "origem": "Kuroko no Basket",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 90,
        "matk": 10,
        "def": 22,
        "spd": 52,
        "crt": 25,
        "habilidade": {
            "nome": "Arremesso Sem Forma",
            "descricao": "Desfere golpes de ângulos biomecanicamente impossíveis. Causa 180% de ATK no inimigo com menor HP, ignorando 50% de sua defesa com acerto crítico garantido."
        },
        "evolucoes": {
            7: {
                "nome": "O Ápice da Velocidade Feral (Zone)",
                "descricao": "O monstro desperta sua verdadeira forma instintiva. Ganha +50% de SPD e +30% de chance crítica (CRT) por 3 turnos. Seus ataques contínuos causam Sangramento Pesado."
            }
        }
    },

    # =========================470
    "kagami_taiga_knb": {
        "nome": "Kagami Taiga",
        "origem": "Kuroko no Basket",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 125,
        "atk": 82,
        "matk": 15,
        "def": 26,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Meteor Jam",
            "descricao": "Kagami salta além dos bloqueios e esmaga seus oponentes. Causa 160% de ATK físico em área a todos os inimigos e quebra instantaneamente escudos mágicos ativos."
        },
        "evolucoes": {
            5: {
                "nome": "Poder do Pulo Supremo (Zone)",
                "descricao": "Entra profundamente na zona concentrada. Aumenta seu próprio ATK em 45% e torna-se imune a atordoamento (Stun) e medo durante o resto do combate."
            }
        }
    },

    # =========================471
    "murasakibara_atsushi_knb": {
        "nome": "Murasakibara Atsushi",
        "origem": "Kuroko no Basket",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 170,
        "atk": 50,
        "matk": 0,
        "def": 60,
        "spd": 16,
        "crt": 5,
        "habilidade": {
            "nome": "Martelo Destruidor (Thor's Hammer)",
            "descricao": "Gira e usa sua força titânica para repelir invasores. Causa 150% de ATK em até dois alvos simultâneos e reduz a velocidade de ação (SPD) deles em 20% por 2 turnos."
        },
        "evolucoes": {
            5: {
                "nome": "Muralha Absoluta de Yosen",
                "descricao": "Assume uma defesa passiva intransponível. Atrai o aggro (Taunt) de todos os ataques físicos inimigos e aumenta sua própria DEF em 60% por 2 rodadas."
            }
        }
    },

    # =========================472
    "midorima_shintaro_knb": {
        "nome": "Midorima Shintaro",
        "origem": "Kuroko no Basket",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 80,
        "matk": 35,
        "def": 24,
        "spd": 22,
        "crt": 35,
        "habilidade": {
            "nome": "Arremesso de 3 Pontos Impecável",
            "descricao": "Calcula a trajetória milimétrica perfeita desde a sua base. Causa 170% de ATK físico diretamente à retaguarda inimiga com 100% de precisão (nunca erra)."
        },
        "evolucoes": {
            5: {
                "nome": "Confiança Máxima de Oha Asa",
                "descricao": "Sua sorte astrológica cega é convertida em letalidade. Ganha acerto crítico inevitável a cada ataque básico, causando 50% de dano extra em inimigos com escudos."
            }
        }
    },

    # =========================473
    "kise_ryota_knb": {
        "nome": "Kise Ryota",
        "origem": "Kuroko no Basket",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 35,
        "matk": 80,
        "def": 25,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Cópia Perfeita (Perfect Copy)",
            "descricao": "Kise analisa instantaneamente e reflete a essência do inimigo. Causa 150% de MATK em área a todos os oponentes e concede um buff coletivo de +20% de dano à sua party."
        },
        "evolucoes": {
            5: {
                "nome": "Perfect Copy + Zone",
                "descricao": "Sua cópia transcende o original. O uso de suas habilidades mágicas rouba passivamente os atributos do inimigo, reduzindo o ATK e DEF do alvo em 30% por 2 turnos."
            }
        }
    },

    # =========================474
    "kuroko_tetsuya_knb": {
        "nome": "Kuroko Tetsuya",
        "origem": "Kuroko no Basket",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 90,
        "atk": 15,
        "matk": 50,
        "def": 18,
        "spd": 28,
        "crt": 10,
        "habilidade": {
            "nome": "Direcionamento Indireto (Misdirection)",
            "descricao": "Apaga a própria presença e a dos aliados importantes. Reduz o aggro (ameaça) do líder da equipe para zero por 2 turnos, e aumenta a precisão geral do grupo em 25%."
        },
        "evolucoes": {
            5: {
                "nome": "Ignite Pass Kai",
                "descricao": "Acelera os passes concentrando magia defensiva. Aplica um reforço de ataque invisível: O próximo golpe físico ou mágico de qualquer aliado causará o dobro (2.0x) do dano final."
            }
        }
    },

    # =========================475
    "himuro_tatsuya_knb": {
        "nome": "Himuro Tatsuya",
        "origem": "Kuroko no Basket",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 3,
        "max_star": 7,
        "hp": 102,
        "atk": 70,
        "matk": 10,
        "def": 20,
        "spd": 36,
        "crt": 20,
        "habilidade": {
            "nome": "Arremesso de Miragem (Mirage Shot)",
            "descricao": "Executa um ataque duplo enganoso na visão inimiga. Causa 140% de ATK que ignora 40% da defesa física, e cancela mecânicas de contra-ataque do alvo."
        },
        "evolucoes": {
            5: {
                "nome": "Finta Elegante Assassina",
                "descricao": "Sua perfeição fluida frustra os defensores brutos. Aumenta a própria evasão em 30% e aplica lentidão garantida (-20% SPD) em quem tentar atacá-lo de perto."
            }
        }
    },

    # =========================476
    "imayoshi_shoichi_knb": {
        "nome": "Imayoshi Shoichi",
        "origem": "Kuroko no Basket",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 2,
        "max_star": 7,
        "hp": 95,
        "atk": 35,
        "matk": 45,
        "def": 18,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Leitura Psicológica Tática",
            "descricao": "Usa a guerra de nervos para quebrar o espírito adversário. Reduz o MATK e o ATK do inimigo mais forte do campo em 35% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Passe Intimidante Oculto",
                "descricao": "Comanda o time de forma sádica e inteligente. Reduz passivamente a esquiva (dodge) de todos os inimigos em 20%."
            },
            5: {
                "nome": "O Capitão Cruel de Touou",
                "descricao": "O esquadrão sob sua tutela cínica recusa-se a recuar. A equipe recebe +25% de resistência mágica e imunidade total contra silenciamento por 3 rodadas."
            }
        }
    },

    # =========================477
    "takao_kazunari_knb": {
        "nome": "Takao Kazunari",
        "origem": "Kuroko no Basket",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 100,
        "atk": 20,
        "matk": 40,
        "def": 20,
        "spd": 32,
        "crt": 10,
        "habilidade": {
            "nome": "Olho de Falcão (Hawk Eye)",
            "descricao": "Sua visão periférica divina elimina quaisquer pontos cegos do time. Remove debuffs de cegueira da equipe instantaneamente e aumenta o ATK de todos em 20% por 2 turnos."
        },
        "evolucoes": {
            3: {
                "nome": "Passe Rápido Pelas Costas",
                "descricao": "Seus reflexos garantem tempo de resposta imediato. Concede a si mesmo ou a um aliado 20% de chance de agir duas vezes seguidas em um turno extra."
            },
            5: {
                "nome": "Sincronia do Atirador Sombrio",
                "descricao": "Age como a dupla fundamental para a linha de trás. Aumenta de forma permanente a taxa crítica (CRT) de todos os Atiradores do seu esquadrão em 30%."
            }
        }
    },

    # =========================478
    "ozora_tsubasa_tsb": {
        "nome": "Ozora Tsubasa",
        "origem": "Captain Tsubasa",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 65,
        "matk": 55,
        "def": 30,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Chute de Folha Seca",
            "descricao": "Um disparo genial onde a bola sobe e cai verticalmente, rasgando as defesas. Causa 160% de MATK (Dano Mágico Esportivo) e ignora 40% da armadura do alvo principal."
        },
        "evolucoes": {
            7: {
                "nome": "A Bola é Sua Amiga",
                "descricao": "Sua aura de protagonista inspira a todos ao redor. Sempre que Tsubasa atacar, ele curará toda a sua party em 15% do seu MATK e fornecerá +30% de defesa geral por 1 turno."
            }
        }
    },

    # =========================479
    "wakabayashi_genzo_tsb": {
        "nome": "Wakabayashi Genzo",
        "origem": "Captain Tsubasa",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 5,
        "max_star": 7,
        "hp": 180,
        "atk": 35,
        "matk": 20,
        "def": 75,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Goleiro Super Genial (SGGK)",
            "descricao": "A sua confiança na zona defensiva permite bloquear impactos impossíveis. Cria um escudo para toda a equipe equivalente a 35% do seu próprio HP e reflete ataques mágicos ou de atiradores."
        },
        "evolucoes": {
            7: {
                "nome": "Defesa Absoluta de Fora da Área",
                "descricao": "Lendas contam que ele rejeita danos massivos com as próprias mãos. Reduz 50% de todo e qualquer dano mágico ou físico sofrido por ele mesmo de maneira permanente."
            }
        }
    },

    # =========================480
    "hyuga_kojiro_tsb": {
        "nome": "Kojiro Hyuga",
        "origem": "Captain Tsubasa",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 140,
        "atk": 88,
        "matk": 10,
        "def": 32,
        "spd": 22,
        "crt": 18,
        "habilidade": {
            "nome": "Chute do Tigre (Tiger Shot)",
            "descricao": "Um ataque puramente físico e animalesco que espalha destruição em linha reta. Causa 200% de ATK focado num alvo, com 30% de chance de aplicar atordoamento (Stun) brutal pelo impacto sonoro."
        },
        "evolucoes": {
            5: {
                "nome": "Neo Chute do Tigre",
                "descricao": "Aperfeiçoa sua técnica bruta para aniquilar defesas robustas. Seu chute passa a romper permanentemente 40% da defesa inimiga e causa repulsão, diminuindo a SPD do alvo."
            }
        }
    },

    # =========================481
    "misaki_taro_tsb": {
        "nome": "Misaki Taro",
        "origem": "Captain Tsubasa",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 115,
        "atk": 35,
        "matk": 55,
        "def": 25,
        "spd": 28,
        "crt": 12,
        "habilidade": {
            "nome": "Passes do Companheiro de Ouro",
            "descricao": "Fornece o apoio tático ideal desarmando defesas abertas de forma suave. Cura o aliado com HP mais baixo em 30% do seu MATK e ainda concede +20% de ATK a ele."
        },
        "evolucoes": {
            5: {
                "nome": "Sincronia Perfeita de Seleção",
                "descricao": "Lê instintivamente as estratégias do líder do time de olhos vendados. Aumenta a velocidade (SPD) de toda a aliança em 25% e remove efeitos malignos de confusão e medo."
            }
        }
    },

    # =========================482
    "schneider_karl_heinz_tsb": {
        "nome": "Karl Heinz Schneider",
        "origem": "Captain Tsubasa",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 90,
        "matk": 30,
        "def": 28,
        "spd": 26,
        "crt": 20,
        "habilidade": {
            "nome": "Chute de Fogo (Fire Shot)",
            "descricao": "O jovem imperador alemão arremata deixando rastros colossais de calor no piso. Causa 180% de ATK e aplica Queimadura severa que extrai 50 de dano por turno ao longo de 3 rodadas."
        },
        "evolucoes": {
            7: {
                "nome": "A Soberania do Imperador Alemão",
                "descricao": "O seu sangue frio perante os defensores coroa sua técnica. Suas habilidades ignoram ativamente 50% de resistências elementares inimigas e destroem por completo barreiras protetoras (escudos mágicos)."
            }
        }
    },
    # =========================483
    "ken_kaneki": {
        "nome": "Ken Kaneki",
        "origem": "Tokyo Ghoul",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 115,
        "atk": 88,
        "matk": 20,
        "def": 25,
        "spd": 46,
        "crt": 20,
        "habilidade": {
            "nome": "Kagune Rinkaku",
            "descricao": "Desfere golpes brutais com seus tentáculos. Causa 180% de ATK e ignora 40% da defesa do oponente, recuperando 20% do dano causado como cura de HP."
        },
        "evolucoes": {
            7: {
                "nome": "Rei de Um Olho Só",
                "descricao": "Assume a fúria suprema. Concede imunidade a atordoamentos, aumenta a SPD em 40% e faz com que seus ataques apliquem Sangramento Letal (reduz curas do inimigo)."
            }
        }
    },

    # =========================484
    "nagisa_shiota": {
        "nome": "Nagisa Shiota",
        "origem": "Assassination Classroom",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 55,
        "matk": 0,
        "def": 18,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Infiltração Silenciosa",
            "descricao": "Esconde sua sede de sangue até o momento exato. Causa 130% de ATK focado no inimigo com menor HP e reduz a evasão do alvo em 15%."
        },
        "evolucoes": {
            3: {
                "nome": "Ataque da Serpente",
                "descricao": "Sua aura paralisa a espinha do oponente. Seus ataques normais passam a ter 20% de chance de aplicar atordoamento de choque (Stun) por 1 turno."
            },
            5: {
                "nome": "Assassino Natural",
                "descricao": "O sorriso que antecede a morte. Concede +30% de chance crítica (Crt) e seus golpes críticos ignoram completamente escudos mágicos ativos."
            }
        }
    },

    # =========================485
    "afro_samurai": {
        "nome": "Afro Samurai",
        "origem": "Afro Samurai",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 82,
        "matk": 0,
        "def": 22,
        "spd": 42,
        "crt": 22,
        "habilidade": {
            "nome": "Corte do Vingador",
            "descricao": "Avança retalhando com sua katana impiedosa. Causa 160% de ATK físico e ganha +25% de taxa de evasão no turno seguinte."
        },
        "evolucoes": {
            5: {
                "nome": "Dono da Bandana Número Um",
                "descricao": "Sua lenda aterroriza o inimigo. Elimina 30% da armadura passiva dos oponentes que focarem nele e concede turno extra ao derrotar um inimigo."
            }
        }
    },

    # =========================486
    "shin_asakura": {
        "nome": "Shin Asakura",
        "origem": "Sakamoto Days",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 85,
        "matk": 10,
        "def": 20,
        "spd": 48,
        "crt": 25,
        "habilidade": {
            "nome": "Leitura Mental de Batalha",
            "descricao": "Prevê a jogada adversária antes de atacar. Desfere um golpe de 200% de ATK com 100% de precisão, ignorando bônus de evasão do alvo."
        },
        "evolucoes": {
            7: {
                "nome": "Combate Profético",
                "descricao": "Sincroniza a equipe lendo as táticas inimigas. Aumenta a velocidade de toda a sua party em 35% e anula os acertos críticos dos inimigos na rodada."
            }
        }
    },

    # =========================487
    "ryuko_matoi": {
        "nome": "Ryuko Matoi",
        "origem": "Kill la Kill",
        "emoji": "⚔️",
        "imagem": "",
        "classe": "assassino",
        "raridade": 5,
        "max_star": 7,
        "hp": 120,
        "atk": 90,
        "matk": 15,
        "def": 28,
        "spd": 44,
        "crt": 20,
        "habilidade": {
            "nome": "Lâmina Tesoura Decapitadora",
            "descricao": "Ataca brutalmente com sua tesoura vermelha gigante. Causa 220% de ATK físico a um inimigo, rasgando escudos de defesa terrestres."
        },
        "evolucoes": {
            7: {
                "nome": "Sincronização Senketsu",
                "descricao": "Sangue e tecido se fundem perfeitamente. Concede lifesteal contínuo (cura 25% do dano causado) e aumenta seu ATK em 40% de forma irreversível na arena."
            }
        }
    },

    # =========================488
    "ohma_tokita": {
        "nome": "Ohma Tokita",
        "origem": "Kengan Ashura",
        "emoji": "👊",
        "imagem": "",
        "classe": "atacante",
        "raridade": 4,
        "max_star": 7,
        "hp": 125,
        "atk": 82,
        "matk": 0,
        "def": 28,
        "spd": 32,
        "crt": 15,
        "habilidade": {
            "nome": "Estilo Niko: Redirecionamento",
            "descricao": "Desvia a força do ataque oponente e a devolve num impacto. Causa 150% de ATK e reflete 30% do dano físico que Ohma sofrer no mesmo turno."
        },
        "evolucoes": {
            5: {
                "nome": "Avanço (Advance)",
                "descricao": "Força os batimentos cardíacos ao limite. Aumenta sua velocidade e ATK físico em 45%, mas consome 5% do seu HP atual a cada ataque."
            }
        }
    },

    # =========================489
    "kikyo_inuyasha": {
        "nome": "Kikyo",
        "origem": "InuYasha",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 74,
        "matk": 40,
        "def": 20,
        "spd": 25,
        "crt": 15,
        "habilidade": {
            "nome": "Flecha Sagrada Purificadora",
            "descricao": "Dispara uma flecha carregada de energia celestial. Causa 180% de MATK na retaguarda e remove todos os buffs do alvo atingido."
        },
        "evolucoes": {
            5: {
                "nome": "Alma Estilhaçada",
                "descricao": "As almas brilhantes defendem seu mestre. Concede a Kikyo imunidade a magias sombrias/maldições e garante acerto crítico contra demônios."
            }
        }
    },

    # =========================490
    "reborn_khr": {
        "nome": "Reborn",
        "origem": "Katekyo Hitman Reborn",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 110,
        "atk": 86,
        "matk": 10,
        "def": 22,
        "spd": 36,
        "crt": 30,
        "habilidade": {
            "nome": "Bala da Última Vontade",
            "descricao": "O Hitman dispara seu tiro lendário. Atira no líder aliado, curando-o e garantindo que o próximo ataque do aliado cause o dobro de dano."
        },
        "evolucoes": {
            7: {
                "nome": "O Arcobaleno do Sol",
                "descricao": "Tiro letal nas frestas defensivas. Seus disparos normais ignoram 50% de blindagens (escudos físicos) e possuem 30% de chance de atordoar (Stun)."
            }
        }
    },

    # =========================491
    "rip_van_winkle": {
        "nome": "Rip Van Winkle",
        "origem": "Hellsing",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 100,
        "atk": 70,
        "matk": 20,
        "def": 18,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Tiro Teleguiado da Caçadora",
            "descricao": "A bala mágica de seu mosquete ricocheteia mudando de direção. Causa 150% de ATK em até 3 alvos simultâneos e possui 100% de precisão (não erra)."
        },
        "evolucoes": {
            5: {
                "nome": "Sádica de Botas Altas",
                "descricao": "O sangue no campo a excita. Aumenta sua taxa de crítico em 25% e aplica um debuff que reduz as curas dos oponentes atingidos."
            }
        }
    },

    # =========================492
    "kino_traveler": {
        "nome": "Kino",
        "origem": "Kino's Journey",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 95,
        "atk": 58,
        "matk": 0,
        "def": 16,
        "spd": 30,
        "crt": 15,
        "habilidade": {
            "nome": "Disparo Frio dos Persuasores",
            "descricao": "Usa seus dois revólveres taticamente. Causa 130% de ATK, atacando o inimigo com menor defesa e ignorando qualquer bônus de evasão do alvo."
        },
        "evolucoes": {
            3: {
                "nome": "Reflexos de Viajante",
                "descricao": "A constante estrada o mantém em alerta. Ganha +20% de esquiva contra qualquer ataque físico corpo-a-corpo."
            },
            5: {
                "nome": "Tiro Surpresa de Canhão",
                "descricao": "Muda para o canhão tático de mão. O próximo ataque crítico desorienta o alvo, deixando-o atordoado por 1 turno."
            }
        }
    },

    # =========================493
    "gene_starwind": {
        "nome": "Gene Starwind",
        "origem": "Outlaw Star",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 75,
        "matk": 40,
        "def": 25,
        "spd": 22,
        "crt": 20,
        "habilidade": {
            "nome": "Arma Caster (Projétil Mágico)",
            "descricao": "Usa munições numeradas raras e místicas. Causa 180% de ATK elemental (fogo, raio ou gelo) com efeitos secundários garantidos (queimação ou lentidão)."
        },
        "evolucoes": {
            5: {
                "nome": "Cápsula de Vácuo Negro",
                "descricao": "Dispara um tiro proibido que consome as defesas da arena. Reduz a resistência mágica de todos os inimigos em 35% durante toda a rodada."
            }
        }
    },

    # =========================494
    "yukio_okumura": {
        "nome": "Yukio Okumura",
        "origem": "Ao no Exorcist",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 65,
        "matk": 35,
        "def": 24,
        "spd": 28,
        "crt": 18,
        "habilidade": {
            "nome": "Disparos de Calibre Sagrado",
            "descricao": "Fuzila os demônios com balas abençoadas. Causa 160% de ATK híbrido e causa dano duplo (320%) em inimigos do tipo Mago ou Morto-Vivo."
        },
        "evolucoes": {
            5: {
                "nome": "Sangue Adormecido do Rei",
                "descricao": "A chama azul desperta temporariamente. Quando sua vida cai abaixo de 40%, todos os disparos recebem bônus de fogo massivo e eleva sua SPD em 30%."
            }
        }
    },

    # =========================495
    "henrietta_gg": {
        "nome": "Henrietta",
        "origem": "Gunslinger Girl",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 45,
        "matk": 0,
        "def": 15,
        "spd": 24,
        "crt": 10,
        "habilidade": {
            "nome": "Fogo Fiel de Metralhadora",
            "descricao": "Esvazia o carregador contra a linha de frente. Causa múltiplos pequenos acertos que somam 120% de ATK e diminuem o ATK inimigo no turno."
        },
        "evolucoes": {
            3: {
                "nome": "Condicionamento Mecânico",
                "descricao": "Ignora a dor. Transforma a perda de HP em bônus, ganhando +5% de ATK para cada 10% de vida perdida no combate."
            },
            5: {
                "nome": "Proteção Fraternal",
                "descricao": "Dispara ferozmente para proteger seu parceiro. Ganha chance crítica garantida se atacar o mesmo inimigo que o Líder aliado."
            }
        }
    },

    # =========================496
    "masked_sniper": {
        "nome": "Masked Sniper",
        "origem": "High-Rise Invasion",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 3,
        "max_star": 7,
        "hp": 100,
        "atk": 62,
        "matk": 0,
        "def": 20,
        "spd": 22,
        "crt": 25,
        "habilidade": {
            "nome": "Tiro Ricocheteador do Telhado",
            "descricao": "Um tiro arquitetado em ricochete. Causa 150% de ATK físico. Ignora as defesas de alvo posicionado e possui +20% de perfuração."
        },
        "evolucoes": {
            3: {
                "nome": "Controle da Máscara",
                "descricao": "Imunidade completa contra debuffs mentais de intimidação e controle mental."
            },
            5: {
                "nome": "Defeito de Hardware Mestre",
                "descricao": "Quando sua máscara sofre defeito, suas restrições morais se soltam. Dobra a chance de infligir Instakill contra alvos abaixo de 20% de HP."
            }
        }
    },

    # =========================497
    "hajime_nagumo": {
        "nome": "Hajime Nagumo",
        "origem": "Arifureta",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 90,
        "matk": 45,
        "def": 35,
        "spd": 32,
        "crt": 25,
        "habilidade": {
            "nome": "Donner & Schlag: Chuva de Balas",
            "descricao": "Dispara revólveres de canhões alquímicos massivos. Causa 220% de ATK híbrido e quebra permanentemente os escudos mágicos do oponente."
        },
        "evolucoes": {
            7: {
                "nome": "Alquimia de Combate Ilimitada",
                "descricao": "Come carne de monstros e conserta suas próprias peças. Ganha regeneração constante e pode paralisar inimigos (Stun) com projéteis modificados."
            }
        }
    },

    # =========================498
    "kite_hxh": {
        "nome": "Kite",
        "origem": "Hunter x Hunter",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 88,
        "matk": 55,
        "def": 28,
        "spd": 34,
        "crt": 20,
        "habilidade": {
            "nome": "Roleta do Palhaço Louco",
            "descricao": "Invoca a sua roleta de Nen e sorteia uma arma absurda ao acaso. Pode desferir desde 150% de ATK em área (foice) até 300% focados (rifle)."
        },
        "evolucoes": {
            7: {
                "nome": "O Número da Sobrevivência (Três)",
                "descricao": "Se for receber um golpe letal absoluto, a roleta garante a arma da reencarnação, revivendo-o com 30% de HP em outra posição da arena."
            }
        }
    },

    # =========================499
    "wolfwood_trigun": {
        "nome": "Nicholas D. Wolfwood",
        "origem": "Trigun",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 120,
        "atk": 78,
        "matk": 10,
        "def": 30,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Arma Punisher: Destruição em Cruz",
            "descricao": "Libera todas as armas escondidas em sua cruz gigante. Causa 180% de ATK em área cobrindo as frentes inimigas com explosões pesadas."
        },
        "evolucoes": {
            5: {
                "nome": "Pastor de Sangue Frio",
                "descricao": "Toma poções curativas do mercado negro. Sempre que realizar um acerto crítico, ele cura 15% de seu HP e ignora sangramentos."
            }
        }
    },

    # =========================500
    "ryo_saeba": {
        "nome": "Ryo Saeba",
        "origem": "City Hunter",
        "emoji": "🏹",
        "imagem": "",
        "classe": "atirador",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 72,
        "matk": 0,
        "def": 20,
        "spd": 30,
        "crt": 35,
        "habilidade": {
            "nome": "Tiro Limpo de 357 Magnum",
            "descricao": "O lendário Sweeper tira a poeira e fuzila com um tiro impecável. Causa 170% de ATK com 100% de chance de perfurar armaduras de tanks."
        },
        "evolucoes": {
            5: {
                "nome": "Foco do Sweeper Implacável",
                "descricao": "Muda para a sua personalidade focada no trabalho duro. Ganha precisão absoluta e anula contra-ataques inimigos no seu turno de atirar."
            }
        }
    },

    # =========================501
    "makarov_dreyar": {
        "nome": "Makarov Dreyar",
        "origem": "Fairy Tail",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 50,
        "matk": 85,
        "def": 35,
        "spd": 18,
        "crt": 10,
        "habilidade": {
            "nome": "Magia Lendária: Fairy Law",
            "descricao": "Concentra o feitiço de eliminação absoluta das trevas. Causa 250% de MATK em todos os inimigos e limpa todos os debuffs negativos da própria guilda."
        },
        "evolucoes": {
            7: {
                "nome": "Modo Titã",
                "descricao": "Cresce de forma massiva transformando-se num gigante (Tank-Líder). Dobra o próprio HP e defende os atiradores e suportes do grupo passivamente."
            }
        }
    },

    # =========================502
    "hashirama_senju": {
        "nome": "Hashirama Senju",
        "origem": "Naruto",
        "emoji": "📚",
        "imagem": "",
        "classe": "líder",
        "raridade": 5,
        "max_star": 7,
        "hp": 150,
        "atk": 75,
        "matk": 80,
        "def": 40,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "Mokuton: Floresta Profunda",
            "descricao": "Bate as palmas gerando árvores colossais que esmagam e perfuram. Causa 200% de MATK em área e enraiza (Stun) até 2 inimigos por 1 turno."
        },
        "evolucoes": {
            7: {
                "nome": "Deus Shinobi: Regeneração Passiva",
                "descricao": "Suas células possuem vida infinita. Restaura passivamente 15% do HP máximo de Hashirama a cada turno sem precisar lançar selos."
            }
        }
    },

    # =========================503
    "schwi_dola": {
        "nome": "Schwi Dola",
        "origem": "No Game No Life",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 105,
        "atk": 15,
        "matk": 72,
        "def": 25,
        "spd": 35,
        "crt": 10,
        "habilidade": {
            "nome": "Ataque Zero Absoluto",
            "descricao": "Compila e dispara energia de seus canhões flutuantes. Causa 160% de MATK e reduz o ATK dos alvos atingidos em 20% com análise robótica."
        },
        "evolucoes": {
            5: {
                "nome": "Sincronização Ex-Machina",
                "descricao": "Pode copiar a propriedade elemental da magia do oponente. Adquire 40% a mais de defesa mágica contra o último ataque recebido."
            }
        }
    },

    # =========================504
    "judar": {
        "nome": "Judar",
        "origem": "Magi",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 25,
        "matk": 78,
        "def": 20,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Lanças do Caos e Gelo",
            "descricao": "Controla os rukh negros para gerar pontas de gelo amaldiçoadas. Causa 170% de MATK e aplica congelamento mágico (Stun leve)."
        },
        "evolucoes": {
            5: {
                "nome": "Magia Oculta de Al-Thamen",
                "descricao": "Converte dor em mana profunda. Se seu HP estiver abaixo de 50%, todas as suas magias custam zero de energia (ignora cooldown) e o dano de área duplica."
            }
        }
    },

    # =========================505
    "gildarts_clive": {
        "nome": "Gildarts Clive",
        "origem": "Fairy Tail",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 140,
        "atk": 90,
        "matk": 85,
        "def": 35,
        "spd": 18,
        "crt": 15,
        "habilidade": {
            "nome": "Magia de Colisão: Crash!",
            "descricao": "Tudo o que Gildarts toca se fragmenta em pó mágico. Causa 250% de dano misto e oblitera permanentemente todos os escudos e barreiras dos inimigos."
        },
        "evolucoes": {
            7: {
                "nome": "Rugido Esmagador do Ás de Fairy Tail",
                "descricao": "Força mágica e opressiva. Reduz o ataque físico e a vontade de luta (precisão) do inimigo de maior poder na arena."
            }
        }
    },

    # =========================506
    "ultear_milkovich": {
        "nome": "Ultear Milkovich",
        "origem": "Fairy Tail",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 20,
        "matk": 70,
        "def": 28,
        "spd": 26,
        "crt": 10,
        "habilidade": {
            "nome": "Magia do Tempo: Arco do Tempo",
            "descricao": "Manipula o tempo orgânico e inorgânico. Causa 140% de MATK e reverte feridas de um aliado, devolvendo parte de seu HP perdido."
        },
        "evolucoes": {
            5: {
                "nome": "O Feitiço Proibido Last Ages",
                "descricao": "Sacrifica seu próprio tempo de vida para salvar o time. Concede turnos extras e revive membros caídos ao custo de 80% do próprio HP atual."
            }
        }
    },

    # =========================507
    "makoto_misumi": {
        "nome": "Makoto Misumi",
        "origem": "Tsukimichi",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 125,
        "atk": 50,
        "matk": 95,
        "def": 30,
        "spd": 22,
        "crt": 15,
        "habilidade": {
            "nome": "Expansão de Domínio Arqueiro (Mana Pura)",
            "descricao": "Concentra mana absoluta como um arco e atira devastação. Causa 220% de MATK e afunda as defesas de alvos em retaguarda."
        },
        "evolucoes": {
            7: {
                "nome": "Poder Descontrolado dos Deuses",
                "descricao": "Sua ausência de limite assusta o campo. Ignora qualquer refletor de magia ou defesa elemental por 3 turnos seguidos."
            }
        }
    },

    # =========================508
    "irene_belserion": {
        "nome": "Irene Belserion",
        "origem": "Fairy Tail",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 30,
        "matk": 92,
        "def": 32,
        "spd": 28,
        "crt": 12,
        "habilidade": {
            "nome": "Deus Sema: Magia Cósmica",
            "descricao": "Irene arranca um meteoro dos céus com encantamentos puros. Causa 240% de MATK em toda a arena inimiga, alterando a geografia e a velocidade inimiga."
        },
        "evolucoes": {
            7: {
                "nome": "Rainha dos Dragões Desperta",
                "descricao": "Transforma-se na fêmea de dragão fundadora. Causa dano físico e mágico insano por 2 turnos e fica imune a controles elementais."
            }
        }
    },

    # =========================509
    "dorothy_unsworth": {
        "nome": "Dorothy Unsworth",
        "origem": "Black Clover",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 110,
        "atk": 15,
        "matk": 80,
        "def": 25,
        "spd": 20,
        "crt": 10,
        "habilidade": {
            "nome": "Magia dos Sonhos: Glamour World",
            "descricao": "Arremessa o inimigo para o mundo dos sonhos de Dorothy. O alvo perde o seu próximo turno e sofre 150% de MATK baseado nos pensamentos dela."
        },
        "evolucoes": {
            5: {
                "nome": "Ditadora Absoluta dos Sonhos",
                "descricao": "Dentro de seu sonho, ela é invencível. Aumenta a efetividade de seus debuffs e atordoamentos em 50% contra magos inimigos."
            }
        }
    },

    # =========================510
    "satella": {
        "nome": "Satella",
        "origem": "Re:Zero",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 145,
        "atk": 35,
        "matk": 100,
        "def": 38,
        "spd": 24,
        "crt": 15,
        "habilidade": {
            "nome": "Mãos Obscuras da Bruxa da Inveja",
            "descricao": "Onda massiva de trevas e possessão mental. Causa 200% de MATK e amaldiçoa todos os inimigos, reduzindo drasticamente todas as curas feitas a eles."
        },
        "evolucoes": {
            7: {
                "nome": "Amor Obsessivo que Supera a Morte",
                "descricao": "Manipula o tempo a favor de quem ela ama. Retorna o Líder aliado do túmulo com 100% do HP ao custo de consumir seu próprio dano ofensivo por 1 rodada."
            }
        }
    },

    # =========================511
    "ange_ushiromiya": {
        "nome": "Ange Ushiromiya",
        "origem": "Umineko no Naku Koro ni",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 25,
        "matk": 78,
        "def": 24,
        "spd": 22,
        "crt": 12,
        "habilidade": {
            "nome": "As Sete Estacas do Purgatório",
            "descricao": "Invoca as estacas voadoras das trevas com autoridade. Causa 150% de MATK e reduz a velocidade e precisão do oponente."
        },
        "evolucoes": {
            5: {
                "nome": "Bruxa da Ressurreição",
                "descricao": "Suas teorias sobrepostas desafiam a dor. Torna-se capaz de reviver e anular feitiços ilusórios das entidades inimigas."
            }
        }
    },

    # =========================512
    "elias_ainsworth": {
        "nome": "Elias Ainsworth",
        "origem": "Mahoutsukai no Yome",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 135,
        "atk": 45,
        "matk": 88,
        "def": 30,
        "spd": 20,
        "crt": 10,
        "habilidade": {
            "nome": "Feitiço de Espinhos da Natureza",
            "descricao": "Usa fadas arcaicas e raízes mágicas colossais. Causa 190% de MATK e embaraça (root) até 2 oponentes travando suas evasões."
        },
        "evolucoes": {
            7: {
                "nome": "O Pilum Murialis Desperto",
                "descricao": "Sua verdadeira essência monstruosa se solta. Seus danos mágicos ganham propriedade assustadora (medo passivo) e sua DEF sobe em 40%."
            }
        }
    },

    # =========================513
    "arcueid_brunestud": {
        "nome": "Arcueid Brunestud",
        "origem": "Tsukihime",
        "emoji": "🔥",
        "imagem": "",
        "classe": "mago",
        "raridade": 5,
        "max_star": 7,
        "hp": 130,
        "atk": 70,
        "matk": 90,
        "def": 35,
        "spd": 32,
        "crt": 20,
        "habilidade": {
            "nome": "Garras Vampíricas da Verdade Mística",
            "descricao": "Cria um corte de magia astral física pesada baseada no peso da lua. Causa 230% de MATK e regenera a si mesma em 30%."
        },
        "evolucoes": {
            7: {
                "nome": "Brunestud do Milênio: Marble Phantasm",
                "descricao": "Engana as leis da terra. Desliga os bônus de terreno do inimigo e aumenta em 50% todo o seu dano híbrido (físico e mágico) em campo limpo."
            }
        }
    },

    # =========================514
    "winry_rockbell": {
        "nome": "Winry Rockbell",
        "origem": "Fullmetal Alchemist",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 2,
        "max_star": 7,
        "hp": 90,
        "atk": 18,
        "matk": 5,
        "def": 16,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Chave de Porca de Reparo",
            "descricao": "Arremessa sua chave inglesa para atordoar ou consertar feridas. Cura um aliado em 25% de HP ou atordoa inimigos corpo a corpo surpresos."
        },
        "evolucoes": {
            3: {
                "nome": "Ajuste de Automail Veloz",
                "descricao": "Seus consertos são precisos. Restaura a estamina (SPD) de seu atacante principal, removendo lentidão instantaneamente."
            },
            5: {
                "nome": "Mecânica Master de Amestris",
                "descricao": "Dobra a eficácia dos escudos e curas físicas concedidas à equipe através de seus remendos mecânicos heroicos."
            }
        }
    },

    # =========================515
    "tohka_yatogami": {
        "nome": "Tohka Yatogami",
        "origem": "Date A Live",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 125,
        "atk": 65,
        "matk": 50,
        "def": 28,
        "spd": 24,
        "crt": 12,
        "habilidade": {
            "nome": "Sandalphon (Espada da Pureza)",
            "descricao": "Brandir a grande espada dissipa miasmas. Protege a equipe em área anulando 30% do próximo dano bruto em grupo recebido."
        },
        "evolucoes": {
            5: {
                "nome": "Halvanhelev (Quebrador de Espíritos)",
                "descricao": "Sua onda de proteção destrói as barreiras defensivas ativas dos oponentes, curando ligeiramente o líder com as frações da magia quebrada."
            }
        }
    },

    # =========================516
    "hestia": {
        "nome": "Hestia",
        "origem": "DanMachi",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 5,
        "matk": 45,
        "def": 20,
        "spd": 18,
        "crt": 5,
        "habilidade": {
            "nome": "Benção Loli-Deusa",
            "descricao": "Concede um buff caloroso de chamas sagradas a um aliado da família Hestia ou ao líder principal, aumentando em 30% seus atributos totais."
        },
        "evolucoes": {
            3: {
                "nome": "Fogo do Lar Eterno",
                "descricao": "A aura divina cura os aliados de forma contínua em 10% a cada rodada enquanto ela estiver viva e segurando as batatas-fritas."
            },
            5: {
                "nome": "Campainha Protetora do Sino",
                "descricao": "Grita ensurdecedoramente se tocarem em seu herói favorito. Aplica silenciamento mágico e paralisia no inimigo ofensor."
            }
        }
    },

    # =========================517
    "kokkoro": {
        "nome": "Kokkoro",
        "origem": "Princess Connect! Re:Dive",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 105,
        "atk": 25,
        "matk": 50,
        "def": 18,
        "spd": 22,
        "crt": 10,
        "habilidade": {
            "nome": "Espíritos da Cura: Aurora",
            "descricao": "Kokkoro guia os espíritos guardiões que abençoam a equipe. Cura o grupo em 25% de seu poder mágico e aumenta o ATK deles sutilmente."
        },
        "evolucoes": {
            3: {
                "nome": "Canção Protetora da Elfa",
                "descricao": "Sua voz acalma corações cansados. Concede escudo que absorve veneno e fogo e anula magias de paralisação temporária."
            },
            5: {
                "nome": "Proteção Sagrada Amethyst",
                "descricao": "Rende a si mesma como isca viva num pico de heroísmo, recebendo debuffs do aliado mais próximo e refletindo purificação."
            }
        }
    },

    # =========================518
    "chika_fujiwara": {
        "nome": "Chika Fujiwara",
        "origem": "Kaguya-sama",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 85,
        "atk": 10,
        "matk": 15,
        "def": 14,
        "spd": 20,
        "crt": 5,
        "habilidade": {
            "nome": "Dança Caótica da Secretaria",
            "descricao": "Começa uma dança estúpida na arena e confunde os zagueiros oponentes, garantindo +15% de velocidade de ação para sua equipe."
        },
        "evolucoes": {
            3: {
                "nome": "Papel de Investigadora Tola",
                "descricao": "Usa um chapéu de detetive revelando armadilhas do jogo. Anula buffs de furtividade e esquiva invisíveis da mesa inimiga."
            },
            5: {
                "nome": "Treinadora de Atletas Chorões",
                "descricao": "Ameaça e força treinos desnecessários com o líder do time. Aumenta os ataques básicos dele em 25% em desespero por agradá-la."
            }
        }
    },

    # =========================519
    "iruma_suzuki": {
        "nome": "Iruma Suzuki",
        "origem": "Mairimashita! Iruma-kun",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 3,
        "max_star": 7,
        "hp": 110,
        "atk": 15,
        "matk": 40,
        "def": 25,
        "spd": 45,
        "crt": 10,
        "habilidade": {
            "nome": "Defesa Passiva: Desvio Absoluto",
            "descricao": "Seu instinto de autopreservação não pode ser bloqueado. Dodge (esquiva) automática de 50% de qualquer ataque, puxando o foco do ataque alheio."
        },
        "evolucoes": {
            3: {
                "nome": "Aura Cativante Desajeitada",
                "descricao": "Sua gentileza paralisa a mente do inimigo de agir por raiva. Aplica apaziguamento (Reduz 20% do ATK inimigo global)."
            },
            5: {
                "nome": "Anel da Gula Arcana",
                "descricao": "Usa Ali-san para devorar as ameaças da arena. Consome magias destrutivas ativas atiradas contra ele e as transforma em HP extra."
            }
        }
    },

    # =========================520
    "yui_hirasawa": {
        "nome": "Yui Hirasawa",
        "origem": "K-On!",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 1,
        "max_star": 7,
        "hp": 80,
        "atk": 5,
        "matk": 20,
        "def": 12,
        "spd": 15,
        "crt": 5,
        "habilidade": {
            "nome": "Tocar Castanholas Aleatoriamente",
            "descricao": "Yui anima as fileiras de forma preguiçosa. Concede uma leve e passiva regeneração de 10% do HP para quem está descansando."
        },
        "evolucoes": {
            3: {
                "nome": "Acordes Genuínos de Guitarra",
                "descricao": "Ela finalmente encontra a sintonia do baixo e da guitarra! Anima e cancela o efeito de Silenciamento mágico do esquadrão."
            },
            5: {
                "nome": "A Sagrada Hora do Chá",
                "descricao": "Serve bolo e chá sob a pancadaria pesada inimiga. Ignora estamina, curando a exaustão total e concedendo imunidade ao tempo frio ou ardente."
            }
        }
    },

    # =========================521
    "ristarte": {
        "nome": "Ristarte",
        "origem": "Cautious Hero",
        "emoji": "🩹",
        "imagem": "",
        "classe": "suporte",
        "raridade": 4,
        "max_star": 7,
        "hp": 115,
        "atk": 10,
        "matk": 68,
        "def": 24,
        "spd": 22,
        "crt": 5,
        "habilidade": {
            "nome": "Cura Divina Exagerada da Deusa Tensa",
            "descricao": "Recita mantras em desespero e enche o time de HP, curando 40% do dano sofrido com propriedades santificantes pesadas que limpam veneno bruto."
        },
        "evolucoes": {
            5: {
                "nome": "Portal Divino de Emergência Rápida",
                "descricao": "Ao sofrer dano fatal total que aniquilaria o atacante de sua equipe, abre um portal instantâneo salvando-o e deixando um boneco substituto no alvo de punição."
            }
        }
    },

    # =========================522
    "genos": {
        "nome": "Genos",
        "origem": "One Punch Man",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 140,
        "atk": 75,
        "matk": 25,
        "def": 40,
        "spd": 35,
        "crt": 15,
        "habilidade": {
            "nome": "Armadura de Ciborgue Demoníaco",
            "descricao": "Sua placa de contenção protege as chamas de núcleo. Sofre penalidades de dano contínuo em si mesmo, mas emite escudo protetor ao redor da guilda."
        },
        "evolucoes": {
            5: {
                "nome": "Incineração Extrema",
                "descricao": "Dispara canhões de fogo maciço num ato suicida em caso de quebra de guarda. Se sua DEF for penetrada, contra-ataca a retaguarda em 200% de queima profunda."
            }
        }
    },

    # =========================523
    "elfman_strauss": {
        "nome": "Elfman Strauss",
        "origem": "Fairy Tail",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 145,
        "atk": 55,
        "matk": 0,
        "def": 45,
        "spd": 15,
        "crt": 5,
        "habilidade": {
            "nome": "Take Over: Fera da Terra (Beast Soul)",
            "descricao": "O homem másculo se recusa a cair por golpes baixos. Assuma a frente da defesa e atrai a fúria física do ataque absorvendo até 30% em mitigação."
        },
        "evolucoes": {
            3: {
                "nome": "Ataque Furioso de Escamas",
                "descricao": "Seu braço transmutado estala de poder. Permite romper blocos físicos quando defende a si mesmo ou revida."
            },
            5: {
                "nome": "Defesa de Rei das Feras Maciças",
                "descricao": "Garante uma carapaça espinhosa. Todo atacante que tentar perfurá-lo será apunhalado e receberá redução de SPD tático permanente."
            }
        }
    },

    # =========================524
    "fat_gum": {
        "nome": "Fat Gum",
        "origem": "Boku no Hero Academia",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 4,
        "max_star": 7,
        "hp": 180,
        "atk": 45,
        "matk": 0,
        "def": 55,
        "spd": 12,
        "crt": 5,
        "habilidade": {
            "nome": "Absorção de Fibras de Gordura",
            "descricao": "Corpo esférico e elástico que atrai impactos brutais. Todos os ataques focados em seu time são atirados nele e sua defesa os absorve convertendo em cargas elásticas."
        },
        "evolucoes": {
            5: {
                "nome": "Lançamento da Lança Acumulada Brutal",
                "descricao": "Quando a sua gordura protetora se esvai completamente e seu HP ficar crível, solta de volta em um soco colossal e emagrecido toda a força condensada de 3 turnos recebidos."
            }
        }
    },

    # =========================525
    "yasutora_sado": {
        "nome": "Yasutora Sado (Chad)",
        "origem": "Bleach",
        "emoji": "🛡️",
        "imagem": "",
        "classe": "tank",
        "raridade": 3,
        "max_star": 7,
        "hp": 150,
        "atk": 50,
        "matk": 10,
        "def": 42,
        "spd": 18,
        "crt": 8,
        "habilidade": {
            "nome": "Brazo Derecha de Gigante",
            "descricao": "Protege os indefesos com seu escudo armadurado de espírito blindado do braço direito. Absorve golpes cortantes e garante mitigação limpa de frestas abertas da equipe."
        },
        "evolucoes": {
            3: {
                "nome": "Resiliência Absoluta Inquieta",
                "descricao": "Mesmo nocauteado, Chad ergue-se para fechar barreiras. Fica imune a efeitos de medo que reduziriam sua defesa."
            },
            5: {
                "nome": "Brazo Izquierda del Diablo",
                "descricao": "Seu braço esquerdo canaliza poder de ataque bruto num contra-ataque. Seu bloqueio seguido pode arremessar as linhas de choque, quebrando defesas passivas."
            }
        }
    }
}

CLASS_EMOJIS = {
    "atacante": "👊",
    "assassino": "⚔️",
    "mago": "🔥",
    "suporte": "🩹",
    "tank": "🛡️",
    "atirador": "🏹",
    "lider": "📚",
}

DIVINE_HERO_IDS = {
    "madoka_kaname",
    "featherine",
    "anti_espiral",
    "zenoh",
    "wang_ling",
    "yogiri_takatou",
    "haruhi_suzumiya",
    "sailor_cosmos",
    "hajun",
    "accelerator",
    "jin_mori",
    "ryougi_shiki",
    "lambdadelta",
}

ORIGIN_ALIASES = {
    "avatar": "Avatar: A Lenda de Aang",
    "avatar_a_lenda_de_aang": "Avatar: A Lenda de Aang",
    "sousou_no_frieren": "Frieren: Beyond Journey's End",
    "frieren_beyond_journey_s_end": "Frieren: Beyond Journey's End",
    "eminence_in_shadow": "The Eminence in Shadow",
    "the_eminence_in_shadow": "The Eminence in Shadow",
    "boku_no_hero": "Boku no Hero Academia",
    "boku_no_hero_academia": "Boku no Hero Academia",
    "kimetsu_no_yaiba": "Demon Slayer",
    "demon_slayer": "Demon Slayer",
    "jojo": "JoJo's Bizarre Adventure",
    "jojo_s_bizarre_adventure": "JoJo's Bizarre Adventure",
    "sword_art_online": "Sword Art Online",
    "hunter_x_hunter": "Hunter x Hunter",
    "fullmetal_alchimist": "Fullmetal Alchemist",
    "fullmetal_alchemist": "Fullmetal Alchemist",
    "gurren_lagann": "Tengen Toppa Gurren Lagann",
    "tengen_toppa_gurren_lagann": "Tengen Toppa Gurren Lagann",
    "shuumatsu_no_valkyrie": "Record of Ragnarok",
    "record_of_ragnarok": "Record of Ragnarok",
    "dragon_ball_super": "Dragon Ball",
    "dragon_ball_z": "Dragon Ball",
}


BALANCE_RARITY_MULTIPLIERS = {
    1: 1.00,
    2: 1.13,
    3: 1.28,
    4: 1.45,
    5: 1.65,
}

BALANCE_CLASS_PROFILES = {
    "atacante": {"hp": 80, "atk": 44, "matk": 18, "def": 18, "spd": 26, "crt": 14},
    "assassino": {"hp": 72, "atk": 44, "matk": 22, "def": 17, "spd": 32, "crt": 20},
    "mago": {"hp": 70, "atk": 16, "matk": 46, "def": 16, "spd": 20, "crt": 12},
    "suporte": {"hp": 75, "atk": 14, "matk": 22, "def": 18, "spd": 19, "crt": 7},
    "tank": {"hp": 115, "atk": 30, "matk": 20, "def": 38, "spd": 14, "crt": 8},
    "atirador": {"hp": 75, "atk": 43, "matk": 32, "def": 17, "spd": 25, "crt": 18},
    "lider": {"hp": 82, "atk": 35, "matk": 30, "def": 22, "spd": 24, "crt": 12},
}


def _clamp_stat(value, floor, cap):
    value = int(value or 0)
    return max(int(floor), min(int(cap), value))


def _balance_hero_stats(hero):
    if hero.get("divino"):
        return

    hero_class = hero.get("classe")
    rarity = int(hero.get("raridade", 1) or 1)
    profile = BALANCE_CLASS_PROFILES.get(hero_class)
    multiplier = BALANCE_RARITY_MULTIPLIERS.get(rarity)
    if not profile or not multiplier:
        return

    for stat_name, base_value in profile.items():
        raw_value = int(hero.get(stat_name, 0) or 0)
        if raw_value <= 0 and stat_name in {"atk", "matk"}:
            continue

        target = base_value * multiplier
        floor_ratio = 0.68 if stat_name in {"atk", "matk"} else 0.72
        cap_ratio = 1.22
        if stat_name == "hp":
            cap_ratio = 1.18
        if stat_name in {"spd", "crt"}:
            cap_ratio = 1.15
        if hero_class == "suporte":
            if stat_name == "hp":
                cap_ratio = min(cap_ratio, 1.08)
            elif stat_name == "def":
                cap_ratio = min(cap_ratio, 1.00)
            elif stat_name == "matk":
                cap_ratio = min(cap_ratio, 1.12)
            elif stat_name == "spd":
                cap_ratio = min(cap_ratio, 1.00)

        floor = round(target * floor_ratio)
        cap = round(target * cap_ratio)
        if stat_name in {"spd", "crt"}:
            cap = min(50, cap)
        hero[stat_name] = _clamp_stat(raw_value, floor, cap)


def _normalization_key(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def normalize_origin(origin):
    clean_origin = str(origin or "").strip()
    return ORIGIN_ALIASES.get(_normalization_key(clean_origin), clean_origin)


def normalize_class(hero_class):
    key = _normalization_key(hero_class)
    aliases = {
        "leader": "lider",
        "lideres": "lider",
        "curandeiro": "suporte",
        "tanque": "tank",
        "shooter": "atirador",
        "mage": "mago",
        "assassin": "assassino",
        "attacker": "atacante",
    }
    return aliases.get(key, key)


def _normalize_catalog():
    for hero_id, hero in HEROES.items():
        if hero_id == "id-nome":
            continue

        hero_class = normalize_class(hero.get("classe"))
        if hero_class in CLASS_EMOJIS:
            hero["classe"] = hero_class
            hero["emoji"] = CLASS_EMOJIS[hero_class]

        hero["origem"] = normalize_origin(hero.get("origem"))
        hero["imagem"] = f"assets/herois_img/{hero_id}.jpg"

        base_skill = hero.get("habilidade")
        if isinstance(base_skill, dict):
            base_skill["id"] = f"{hero_id}__base"

        for required_stars, evolution in (hero.get("evolucoes") or {}).items():
            if isinstance(evolution, dict):
                evolution["id"] = f"{hero_id}__evo_{required_stars}"

        if hero_id in DIVINE_HERO_IDS or int(hero.get("raridade", 0) or 0) >= 7:
            hero["raridade"] = 7
            hero["max_star"] = 7
            hero["divino"] = True
            hero["secreto"] = True

        _balance_hero_stats(hero)


_normalize_catalog()

print("Arquivo carregado com sucesso!")
print(len(HEROES))
