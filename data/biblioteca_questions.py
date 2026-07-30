import os
import random
import re
import unicodedata


try:
    from data.heroes import HEROES
except Exception:
    HEROES = {}


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HERO_IMAGE_DIR = os.path.join(ROOT_DIR, "assets", "herois_img")


def _norm(text):
    text = unicodedata.normalize("NFKD", str(text or "").lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _aliases(*values):
    result = []
    seen = set()
    for value in values:
        raw = str(value or "").strip()
        normalized = _norm(raw)
        for candidate in {raw, normalized, raw.replace("_", " ")}:
            candidate = str(candidate or "").strip()
            if candidate and candidate.lower() not in seen:
                seen.add(candidate.lower())
                result.append(candidate)
    return result


def _stable_options(opcoes, pergunta, resposta):
    if not opcoes:
        return []
    result = []
    seen = set()
    for option in opcoes:
        option = str(option or "").strip()
        key = _norm(option)
        if option and key not in seen:
            seen.add(key)
            result.append(option)
    if resposta and _norm(resposta) not in seen:
        result.append(str(resposta).strip())

    seed_text = f"{pergunta}|{resposta}|{'|'.join(result)}"
    seed = sum((index + 1) * ord(char) for index, char in enumerate(seed_text))
    rng = random.Random(seed)
    rng.shuffle(result)
    return result


def _question(
    tipo,
    categoria,
    dificuldade,
    pergunta,
    resposta,
    opcoes=None,
    explicacao="",
    tags=None,
    aliases=None,
    imagem=None,
):
    return {
        "tipo": tipo,
        "categoria": categoria,
        "dificuldade": int(dificuldade),
        "pergunta": pergunta,
        "opcoes": _stable_options(opcoes, pergunta, resposta),
        "resposta": resposta,
        "explicacao": explicacao,
        "tags": tags or [],
        "aliases": aliases or _aliases(resposta),
        "imagem": imagem,
    }


QUESTOES = {
    "naruto_001": _question(
        "multipla_escolha",
        "Naruto",
        1,
        "Quem é o líder do Time 7 no começo de Naruto?",
        "Kakashi Hatake",
        ["Iruka Umino", "Kakashi Hatake", "Might Guy", "Asuma Sarutobi"],
        "Kakashi é o jounin responsável por Naruto, Sasuke e Sakura.",
        ["anime", "naruto", "personagem"],
        _aliases("Kakashi Hatake", "Kakashi"),
    ),
    "naruto_002": _question(
        "escrita",
        "Naruto",
        1,
        "Qual técnica é uma esfera de chakra giratória usada por Naruto?",
        "Rasengan",
        explicacao="O Rasengan foi criado pelo Quarto Hokage e se tornou uma das técnicas principais do Naruto.",
        tags=["anime", "naruto", "habilidade"],
        aliases=_aliases("Rasengan"),
    ),
    "naruto_003": _question(
        "verdadeiro_falso",
        "Naruto",
        2,
        "Levi Ackerman é um Titã Cambiante.",
        "Falso",
        ["Verdadeiro", "Falso"],
        "Levi é de Attack on Titan, mas não é Titã Cambiante.",
        ["anime", "pegadinha"],
        _aliases("falso", "não", "nao", "f"),
    ),
    "one_piece_001": _question(
        "multipla_escolha",
        "One Piece",
        1,
        "Qual é o sonho de Monkey D. Luffy?",
        "Ser o Rei dos Piratas",
        ["Ser Hokage", "Ser o Rei dos Piratas", "Virar Shinigami", "Encontrar as Esferas do Dragão"],
        "Luffy quer encontrar o One Piece e se tornar o Rei dos Piratas.",
        ["anime", "one piece"],
        _aliases("Ser o Rei dos Piratas", "rei dos piratas"),
    ),
    "one_piece_002": _question(
        "adivinhe_personagem",
        "One Piece",
        1,
        "Sou espadachim, faço parte dos Chapéus de Palha e uso três espadas. Quem sou eu?",
        "Roronoa Zoro",
        explicacao="Zoro é o espadachim dos Chapéus de Palha e usa o estilo Santoryu.",
        tags=["anime", "one piece", "personagem"],
        aliases=_aliases("Roronoa Zoro", "Zoro"),
    ),
    "one_piece_003": _question(
        "emoji",
        "One Piece",
        2,
        "Qual anime combina com estes emojis: 🏴‍☠️ 👒 🌊?",
        "One Piece",
        explicacao="Piratas, chapéu de palha e mar apontam para One Piece.",
        tags=["anime", "emoji"],
        aliases=_aliases("One Piece"),
    ),
    "bleach_001": _question(
        "multipla_escolha",
        "Bleach",
        1,
        "Qual destes personagens pertence a Bleach?",
        "Rukia Kuchiki",
        ["Megumi Fushiguro", "Rukia Kuchiki", "Asuna Yuuki", "Power"],
        "Rukia é uma Shinigami central em Bleach.",
        ["anime", "bleach"],
        _aliases("Rukia Kuchiki", "Rukia"),
    ),
    "bleach_002": _question(
        "habilidade",
        "Bleach",
        3,
        "De qual personagem é a habilidade Bankai: Senbonzakura Kageyoshi?",
        "Byakuya Kuchiki",
        explicacao="Senbonzakura Kageyoshi é o Bankai de Byakuya.",
        tags=["anime", "bleach", "habilidade"],
        aliases=_aliases("Byakuya Kuchiki", "Byakuya"),
    ),
    "dragon_ball_001": _question(
        "multipla_escolha",
        "Dragon Ball",
        1,
        "Qual raça guerreira é conhecida por ficar mais forte após batalhas quase fatais?",
        "Saiyajins",
        ["Namekuseijins", "Saiyajins", "Androides", "Shinigamis"],
        "Os Saiyajins possuem o conceito de Zenkai, ficando mais fortes após recuperações extremas.",
        ["anime", "dragon ball"],
        _aliases("Saiyajins", "saiyans", "saiyajin"),
    ),
    "dragon_ball_002": _question(
        "complete_nome",
        "Dragon Ball",
        1,
        "Complete o nome: Son ____",
        "Goku",
        explicacao="Son Goku é o protagonista de Dragon Ball.",
        tags=["anime", "dragon ball"],
        aliases=_aliases("Goku", "Son Goku"),
    ),
    "jojo_001": _question(
        "multipla_escolha",
        "JoJo",
        2,
        "Em JoJo, como são chamadas as manifestações espirituais de poder usadas por muitos personagens?",
        "Stands",
        ["Quirks", "Stands", "Bankais", "Nens"],
        "Stands são a principal mecânica de batalha a partir de Stardust Crusaders.",
        ["anime", "jojo", "habilidade"],
        _aliases("Stands", "stand"),
    ),
    "jojo_002": _question(
        "habilidade",
        "JoJo",
        3,
        "Qual Stand de Dio Brando é famoso por parar o tempo?",
        "The World",
        ["Star Platinum", "The World", "Killer Queen", "Gold Experience"],
        "The World é o Stand de Dio e sua habilidade mais famosa é parar o tempo.",
        ["anime", "jojo", "habilidade"],
        _aliases("The World", "O Mundo", "Za Warudo"),
    ),
    "death_note_001": _question(
        "adivinhe_anime",
        "Anime",
        1,
        "Um jovem encontra um caderno capaz de matar pessoas. Qual é o anime?",
        "Death Note",
        explicacao="O Death Note mata pessoas quando o nome delas é escrito seguindo suas regras.",
        tags=["anime", "adivinhe anime"],
        aliases=_aliases("Death Note"),
    ),
    "one_punch_001": _question(
        "escrita",
        "Anime",
        1,
        "Qual é o nome do protagonista de One Punch Man?",
        "Saitama",
        explicacao="Saitama é o herói que derrota inimigos com um soco.",
        tags=["anime", "personagem"],
        aliases=_aliases("Saitama"),
    ),
    "aot_001": _question(
        "multipla_escolha",
        "Attack on Titan",
        1,
        "Em Attack on Titan, quem é conhecido pela habilidade absurda com lâminas e equipamento de manobra?",
        "Levi Ackerman",
        ["Eren Yeager", "Levi Ackerman", "Reiner Braun", "Armin Arlert"],
        "Levi é considerado um dos soldados mais fortes da humanidade.",
        ["anime", "attack on titan"],
        _aliases("Levi Ackerman", "Levi"),
        {"tipo": "hero", "hero_id": "levi_ackerman"},
    ),
    "fullmetal_001": _question(
        "multipla_escolha",
        "Fullmetal Alchemist",
        2,
        "Qual é a lei central da alquimia em Fullmetal Alchemist?",
        "Troca equivalente",
        ["Troca equivalente", "Poder da amizade", "Contrato de sangue", "Desejo absoluto"],
        "A alquimia funciona com o princípio da troca equivalente.",
        ["anime", "fullmetal"],
        _aliases("Troca equivalente", "equivalent exchange"),
    ),
    "hunter_001": _question(
        "multipla_escolha",
        "Hunter x Hunter",
        2,
        "Como se chama o sistema de energia usado em Hunter x Hunter?",
        "Nen",
        ["Chakra", "Nen", "Ki", "Mana"],
        "Nen é a técnica de manipulação da aura em Hunter x Hunter.",
        ["anime", "hunter x hunter", "habilidade"],
        _aliases("Nen"),
    ),
    "jujutsu_001": _question(
        "multipla_escolha",
        "Jujutsu Kaisen",
        2,
        "Qual personagem é conhecido pela Expansão de Domínio chamada Vazio Ilimitado?",
        "Satoru Gojo",
        ["Yuji Itadori", "Satoru Gojo", "Megumi Fushiguro", "Kento Nanami"],
        "Vazio Ilimitado é a expansão de domínio de Gojo.",
        ["anime", "jujutsu", "habilidade"],
        _aliases("Satoru Gojo", "Gojo"),
        {"tipo": "hero", "hero_id": "satoru_gojo"},
    ),
    "demon_slayer_001": _question(
        "multipla_escolha",
        "Demon Slayer",
        1,
        "Qual personagem carrega uma caixa com sua irmã transformada em oni?",
        "Tanjiro Kamado",
        ["Zenitsu Agatsuma", "Tanjiro Kamado", "Inosuke Hashibira", "Giyu Tomioka"],
        "Tanjiro carrega Nezuko em uma caixa durante parte da jornada.",
        ["anime", "demon slayer"],
        _aliases("Tanjiro Kamado", "Tanjiro"),
    ),
    "fate_001": _question(
        "multipla_escolha",
        "Fate",
        3,
        "Em Fate, qual classe de servo normalmente luta com espada?",
        "Saber",
        ["Caster", "Assassin", "Saber", "Rider"],
        "Saber é a classe tradicional de usuários de espada.",
        ["anime", "fate", "classe"],
        _aliases("Saber"),
    ),
    "rezero_001": _question(
        "escrita",
        "Re:Zero",
        2,
        "Qual é o nome da habilidade de Subaru que o faz retornar após morrer?",
        "Retorno pela Morte",
        explicacao="Return by Death, em português Retorno pela Morte, reinicia Subaru após sua morte.",
        tags=["anime", "rezero", "habilidade"],
        aliases=_aliases("Retorno pela Morte", "Return by Death", "retorno da morte"),
    ),
    "black_clover_001": _question(
        "multipla_escolha",
        "Black Clover",
        1,
        "Qual protagonista de Black Clover nasceu sem magia?",
        "Asta",
        ["Yuno", "Asta", "Noelle", "Yami"],
        "Asta não possui mana, mas usa anti-magia.",
        ["anime", "black clover"],
        _aliases("Asta"),
    ),
    "overlord_001": _question(
        "adivinhe_personagem",
        "Overlord",
        2,
        "Sou um governante morto-vivo, líder de Nazarick e meu nome começa com Ainz. Quem sou eu?",
        "Ainz Ooal Gown",
        explicacao="Ainz Ooal Gown é o protagonista de Overlord.",
        tags=["anime", "overlord"],
        aliases=_aliases("Ainz Ooal Gown", "Ainz", "Momonga"),
        imagem={"tipo": "hero", "hero_id": "ainz_gown"},
    ),
    "chainsaw_001": _question(
        "multipla_escolha",
        "Chainsaw Man",
        2,
        "Qual personagem se transforma no Chainsaw Man?",
        "Denji",
        ["Aki", "Denji", "Power", "Makima"],
        "Denji se funde a Pochita e ganha poderes de motosserra.",
        ["anime", "chainsaw man"],
        _aliases("Denji"),
    ),
    "sao_001": _question(
        "multipla_escolha",
        "Sword Art Online",
        1,
        "Qual é o apelido do protagonista Kirigaya Kazuto?",
        "Kirito",
        ["Kirito", "Klein", "Heathcliff", "Eugeo"],
        "Kirito é o nome de jogador de Kazuto.",
        ["anime", "sao"],
        _aliases("Kirito"),
    ),
    "konosuba_001": _question(
        "multipla_escolha",
        "KonoSuba",
        2,
        "Qual personagem de KonoSuba é obcecada por Explosão?",
        "Megumin",
        ["Aqua", "Megumin", "Darkness", "Wiz"],
        "Megumin dedica sua magia à Explosão.",
        ["anime", "konosuba", "habilidade"],
        _aliases("Megumin"),
    ),
    "persona_001": _question(
        "multipla_escolha",
        "Persona",
        2,
        "Em Persona 5, qual é o codinome do protagonista nos Phantom Thieves?",
        "Joker",
        ["Crow", "Joker", "Skull", "Fox"],
        "O protagonista de Persona 5 usa o codinome Joker.",
        ["jogo", "persona"],
        _aliases("Joker"),
    ),
    "pokemon_001": _question(
        "multipla_escolha",
        "Jogos",
        1,
        "Qual destes é um Pokémon inicial da primeira geração?",
        "Bulbasaur",
        ["Lucario", "Bulbasaur", "Eevee", "Mewtwo"],
        "Bulbasaur é um dos iniciais de Kanto.",
        ["jogo", "pokemon"],
        _aliases("Bulbasaur"),
    ),
    "zelda_001": _question(
        "multipla_escolha",
        "Jogos",
        1,
        "Na série The Legend of Zelda, qual é o nome mais comum do herói jogável?",
        "Link",
        ["Zelda", "Link", "Ganon", "Epona"],
        "Link é o herói mais recorrente da franquia.",
        ["jogo", "zelda"],
        _aliases("Link"),
    ),
    "final_fantasy_001": _question(
        "multipla_escolha",
        "Jogos",
        2,
        "Qual personagem de Final Fantasy VII usa uma espada gigante chamada Buster Sword?",
        "Cloud Strife",
        ["Squall Leonhart", "Cloud Strife", "Tidus", "Noctis"],
        "Cloud Strife é associado à Buster Sword.",
        ["jogo", "final fantasy"],
        _aliases("Cloud Strife", "Cloud"),
    ),
    "logic_001": _question(
        "logica",
        "Lógica",
        1,
        "Tenho páginas, guardo conhecimento e posso ficar perdido. O que sou?",
        "Livro",
        explicacao="Um livro guarda conhecimento em páginas. O TutoriUAU disse que essa era de aquecimento.",
        tags=["lógica", "biblioteca"],
        aliases=_aliases("Livro", "um livro"),
    ),
    "logic_002": _question(
        "ordem",
        "Lógica",
        2,
        "Organize do menor para o maior: A) 3, B) 1, C) 4, D) 2.",
        "B D A C",
        ["A B C D", "B D A C", "D B A C", "B A D C"],
        "A ordem crescente é 1, 2, 3, 4, ou seja: B, D, A, C.",
        ["lógica", "ordem"],
        _aliases("B D A C", "BDAC", "B,D,A,C"),
    ),
    "echo_001": _question(
        "multipla_escolha",
        "Echo Siege",
        1,
        "Qual comando mostra sua ficha de jogador no Echo Siege?",
        "echo perfil",
        ["echo perfil", "echo summon", "echo hunt", "echo loja"],
        "O perfil mostra dados do jogador, herói principal, pet, ranking e visual.",
        ["echo siege", "comando"],
        _aliases("echo perfil", "perfil"),
    ),
    "echo_002": _question(
        "multipla_escolha",
        "Echo Siege",
        1,
        "Qual comando abre a mochila de itens?",
        "echo mochila",
        ["echo party", "echo mochila", "echo arena", "echo anime"],
        "A mochila guarda consumíveis, tickets, drops e tokens.",
        ["echo siege", "comando"],
        _aliases("echo mochila", "mochila"),
    ),
    "echo_003": _question(
        "multipla_escolha",
        "Echo Siege",
        2,
        "Qual comando organiza os heróis do grupo principal?",
        "echo party",
        ["echo party", "echo perfil", "echo daily", "echo code"],
        "O comando party organiza a equipe usada em vários modos.",
        ["echo siege", "comando"],
        _aliases("echo party", "party"),
    ),
    "echo_004": _question(
        "multipla_escolha",
        "Echo Siege",
        2,
        "Qual moeda exclusiva pertence ao cassino Fallen Angel?",
        "Ficha do Cassino",
        ["Páginas Perdidas", "Echobet", "Ficha do Cassino", "Fragmento Divino"],
        "O cassino usa Fichas do Cassino, separadas do Gold.",
        ["echo siege", "cassino"],
        _aliases("Ficha do Cassino", "fichas do cassino", "ficha"),
    ),
    "echo_005": _question(
        "multipla_escolha",
        "Echo Siege",
        2,
        "Qual moeda exclusiva pertence à Biblioteca Perdida?",
        "Páginas Perdidas",
        ["Páginas Perdidas", "Fichas do Cassino", "Echobet", "Gemas Azuis"],
        "A Biblioteca usa Páginas Perdidas para sua loja exclusiva.",
        ["echo siege", "biblioteca"],
        _aliases("Páginas Perdidas", "paginas perdidas", "página perdida"),
    ),
    "echo_006": _question(
        "verdadeiro_falso",
        "Echo Siege",
        1,
        "O comando `echo ajuda` mostra um resumo dos comandos disponíveis.",
        "Verdadeiro",
        ["Verdadeiro", "Falso"],
        "O `echo ajuda` é o resumo paginado do TutoriUAU.",
        ["echo siege", "comando"],
        _aliases("verdadeiro", "sim", "v"),
    ),
    "echo_007": _question(
        "multipla_escolha",
        "Echo Siege",
        2,
        "Qual comando consulta personagens por obra/anime?",
        "echo anime",
        ["echo anime", "echo pet", "echo forja", "echo bug"],
        "`echo anime <obra>` lista personagens de uma origem específica.",
        ["echo siege", "catalogo"],
        _aliases("echo anime", "anime"),
    ),
    "echo_008": _question(
        "multipla_escolha",
        "Echo Siege",
        2,
        "Qual comando permite informar problemas para a staff?",
        "echo bug",
        ["echo bug", "echo arena", "echo daily", "echo equipar"],
        "`echo bug <texto>` registra problemas e queixas para a equipe.",
        ["echo siege", "admin"],
        _aliases("echo bug", "bug", "queixa"),
    ),
}


ECHO_HERO_IDS = [
    "levi_ackerman", "rock_lee", "aang", "ainz_gown", "akame", "all_might",
    "albedo_overlord", "asta", "aqua_konosuba", "archer_emiya", "byakuya_kuchiki",
    "dio_brando", "eren_yeager", "freeza", "goku", "gojo_satoru", "ichigo_kurosaki",
    "itachi_uchiha", "kirito", "luffy", "madara_uchiha", "megumin", "mikasa_ackerman",
    "naruto_uzumaki", "rimuru_tempest", "roronoa_zoro", "saitama", "saber_artoria",
    "sasuke_uchiha", "subaru_natsuki", "tanjiro_kamado", "yami_sukehiro",
]


CLASS_OPTIONS = ["Atacante", "Assassino", "Mago", "Suporte", "Tank", "Atirador", "Líder"]


def _hero_option_pool(field, fallback):
    values = []
    for hero in HEROES.values():
        value = str(hero.get(field, "")).strip()
        if value and value not in values:
            values.append(value)
    return values or fallback


def _make_options(answer, pool, seed_text, total=4):
    answer = str(answer or "").strip()
    normalized_answer = _norm(answer)
    options_pool = []
    seen = {normalized_answer}
    for item in pool:
        item = str(item or "").strip()
        key = _norm(item)
        if item and key not in seen:
            seen.add(key)
            options_pool.append(item)
    seed = sum(ord(char) for char in str(seed_text))
    rng = random.Random(seed)
    rng.shuffle(options_pool)
    options = [answer] + options_pool[: max(0, total - 1)]
    while len(options) < total:
        options.append(f"Arquivo Corrompido {len(options)}")
    return options[:total]


def _valid_hero_ids():
    result = []
    for hero_id, hero in HEROES.items():
        if hero_id == "id-nome":
            continue
        if hero.get("divino") or hero.get("secreto"):
            continue
        result.append(hero_id)
    return result


def _skill_name(skill):
    if isinstance(skill, dict):
        return str(skill.get("nome", "")).strip()
    return str(skill or "").strip()


def _evolution_entries(hero):
    evolutions = hero.get("evolucoes") or hero.get("evoluções") or hero.get("evolucao") or {}
    if not isinstance(evolutions, dict):
        return []
    entries = []
    for stars, data in evolutions.items():
        try:
            stars = int(stars)
        except (TypeError, ValueError):
            continue
        name = _skill_name(data)
        if name:
            entries.append((stars, name, data if isinstance(data, dict) else {}))
    return sorted(entries, key=lambda item: item[0])


def _rarity_label(rarity):
    return f"{max(1, min(7, int(rarity or 1)))}⭐"


def _rarity_aliases(rarity):
    rarity = max(1, min(7, int(rarity or 1)))
    return _aliases(_rarity_label(rarity), str(rarity), f"{rarity} estrelas", f"{rarity} estrela")


def _hero_has_image(hero_id):
    return os.path.isfile(os.path.join(HERO_IMAGE_DIR, f"{hero_id}.jpg"))


def _add_echo_hero_questions():
    origin_pool = _hero_option_pool("origem", ["Naruto", "One Piece", "Bleach", "Dragon Ball"])
    valid_ids = _valid_hero_ids()
    name_pool = [str(HEROES[hero_id].get("nome", hero_id)) for hero_id in valid_ids]
    skill_pool = []
    skill_owners = {}
    for pool_hero_id in valid_ids:
        pool_hero = HEROES[pool_hero_id]
        pool_name = str(pool_hero.get("nome", pool_hero_id))
        skill_names = [_skill_name(pool_hero.get("habilidade"))]
        skill_names.extend(name for _, name, _ in _evolution_entries(pool_hero))
        for skill_name in skill_names:
            if not skill_name:
                continue
            skill_pool.append(skill_name)
            skill_owners.setdefault(_norm(skill_name), set()).add(pool_name)

    ordered_ids = []
    for hero_id in ECHO_HERO_IDS:
        if hero_id not in ordered_ids:
            ordered_ids.append(hero_id)
    for hero_id in sorted(valid_ids):
        if hero_id == "id-nome" or hero_id in ordered_ids:
            continue
        ordered_ids.append(hero_id)

    for index, hero_id in enumerate(ordered_ids, start=1):
        hero = HEROES.get(hero_id)
        if not hero:
            continue
        name = str(hero.get("nome", hero_id.replace("_", " ").title()))
        origin = str(hero.get("origem", "Origem desconhecida"))
        hero_class = str(hero.get("classe", "Atacante")).title()
        rarity = int(hero.get("raridade", 1) or 1)
        image = {"tipo": "hero", "hero_id": hero_id} if _hero_has_image(hero_id) else None
        difficulty = min(5, max(1, rarity))
        base_skill = _skill_name(hero.get("habilidade"))
        rarity_answer = _rarity_label(rarity)

        if image:
            QUESTOES[f"echo_img_{index:03d}_{hero_id}"] = _question(
                "imagem_personagem",
                "Personagens",
                min(4, max(1, difficulty)),
                "Quem é o personagem exibido neste arquivo recuperado da Biblioteca?",
                name,
                explicacao=f"Este arquivo mostra {name}, de {origin}.",
                tags=["echo siege", "imagem", "personagem"],
                aliases=_aliases(name, hero_id),
                imagem=image,
            )
        QUESTOES[f"echo_class_{index:03d}_{hero_id}"] = _question(
            "multipla_escolha",
            "Echo Siege",
            min(3, max(1, difficulty)),
            f"No Echo Siege, qual é a classe de {name}?",
            hero_class,
            _make_options(hero_class, CLASS_OPTIONS, hero_id),
            f"No catálogo do Echo Siege, {name} está como classe {hero_class}.",
            ["echo siege", "classe", "personagem"],
            _aliases(hero_class),
            image,
        )
        QUESTOES[f"echo_rarity_{index:03d}_{hero_id}"] = _question(
            "multipla_escolha",
            "Echo Siege",
            min(4, max(2, difficulty)),
            f"No Echo Siege, qual é a raridade base de {name}?",
            rarity_answer,
            _make_options(rarity_answer, [_rarity_label(value) for value in range(1, 6)], f"rarity:{hero_id}"),
            f"{name} é um personagem de raridade base {rarity_answer}.",
            ["echo siege", "raridade", "personagem"],
            _rarity_aliases(rarity),
            image,
        )
        QUESTOES[f"echo_origin_{index:03d}_{hero_id}"] = _question(
            "multipla_escolha",
            "Echo Siege",
            min(3, max(1, difficulty)),
            f"No Echo Siege, qual é a origem/obra de {name}?",
            origin,
            _make_options(origin, origin_pool, hero_id),
            f"{name} pertence à origem {origin}.",
            ["echo siege", "origem", "anime"],
            _aliases(origin),
            image,
        )
        if base_skill:
            QUESTOES[f"echo_skill_{index:03d}_{hero_id}"] = _question(
                "multipla_escolha",
                "Habilidades",
                min(5, max(2, difficulty + 1)),
                f"Qual destas é a habilidade base de {name} no Echo Siege?",
                base_skill,
                _make_options(base_skill, skill_pool, f"skill:{hero_id}"),
                f"A habilidade base de {name} é {base_skill}.",
                ["echo siege", "habilidade", "personagem"],
                _aliases(base_skill),
                image,
            )
            if len(skill_owners.get(_norm(base_skill), [])) == 1:
                QUESTOES[f"echo_skill_owner_{index:03d}_{hero_id}"] = _question(
                    "multipla_escolha",
                    "Habilidades",
                    min(5, max(3, difficulty + 1)),
                    f"Qual personagem do Echo Siege usa a habilidade {base_skill}?",
                    name,
                    _make_options(name, name_pool, f"owner:{hero_id}:{base_skill}"),
                    f"{base_skill} pertence a {name}.",
                    ["echo siege", "habilidade", "personagem"],
                    _aliases(name, hero_id),
                    image,
                )
        for evo_stars, evo_name, _ in _evolution_entries(hero):
            answer = _rarity_label(evo_stars)
            QUESTOES[f"echo_evo_{index:03d}_{hero_id}_{evo_stars}"] = _question(
                "multipla_escolha",
                "Habilidades",
                min(5, max(4, difficulty)),
                f"Em qual evolução/estrela {name} desbloqueia {evo_name}?",
                answer,
                _make_options(answer, [_rarity_label(value) for value in [1, 3, 5, 7]], f"evo:{hero_id}:{evo_stars}"),
                f"{name} desbloqueia {evo_name} em {answer}.",
                ["echo siege", "evolução", "habilidade"],
                _rarity_aliases(evo_stars),
                image,
            )


_add_echo_hero_questions()
