import json
import os
import random
import re
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).parent
CHARADAS_PATH = BASE_DIR / "charadas.json"
RESPOSTAS_PATH = BASE_DIR / "respostas.json"
RECORDE_PATH = BASE_DIR / "recorde.json"

PALAVRAS_NUMERICAS = {
    "zero", "um", "uma", "dois", "duas", "tres", "três", "quatro",
    "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
    "treze", "catorze", "quatorze", "quinze", "dezesseis", "dezessete",
    "dezoito", "dezenove", "vinte", "trinta", "quarenta", "cinquenta",
    "sessenta", "setenta", "oitenta", "noventa", "cem", "mil",
}

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001FA00-\U0001FAFF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "]+",
    flags=re.UNICODE,
)

DICA_ICONES = ["🗿", "🐍", "☀️"]
DICA_TITULOS = ["Dica I", "Dica II", "Dica III"]
AGUARDANDO = "(silêncio das areias...)"
REVELANDO = "(aguardando...)"


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def extrair_palavras(texto: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-ÿ]+", texto)


def construir_vocabulario(charadas: list, respostas: list) -> set[str]:
    vocabulario = set()
    textos = []

    for item in charadas:
        textos.append(item["charada"])
        textos.extend(item["dicas"])

    for item in respostas:
        textos.append(item["resposta"])

    for texto in textos:
        for palavra in extrair_palavras(texto):
            vocabulario.add(normalizar(palavra))

    return vocabulario


def contem_emoji(texto: str) -> bool:
    return bool(EMOJI_PATTERN.search(texto))


def validar_entrada(texto: str, vocabulario: set[str]) -> tuple[bool, str]:
    if not texto or not texto.strip():
        return False, "A resposta não pode estar vazia."

    if re.search(r"\d", texto):
        return False, "Números e algarismos não são permitidos."

    if contem_emoji(texto):
        return False, "Emojis não são permitidos."

    palavras = extrair_palavras(texto)
    if not palavras:
        return False, "Use apenas palavras válidas."

    for palavra in palavras:
        normalizada = normalizar(palavra)
        if normalizada in PALAVRAS_NUMERICAS:
            return False, "Palavras numéricas não são permitidas."
        if normalizada not in vocabulario:
            return False, f"A palavra '{palavra}' não faz parte do vocabulário do jogo."

    return True, ""


def carregar_json(caminho: Path, padrao):
    if caminho.exists():
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return padrao


def salvar_json(caminho: Path, dados):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def carregar_dados():
    charadas = carregar_json(CHARADAS_PATH, [])
    respostas = carregar_json(RESPOSTAS_PATH, [])
    recorde = carregar_json(RECORDE_PATH, {"recorde": 0, "jogador": ""})
    return charadas, respostas, recorde


def atualizar_recorde(acertos: int, nome: str, recorde_atual: dict) -> dict:
    if acertos > recorde_atual.get("recorde", 0):
        novo_recorde = {"recorde": acertos, "jogador": nome}
        salvar_json(RECORDE_PATH, novo_recorde)
        return novo_recorde
    return recorde_atual


def renderizar_banner():
    print()
    print("🦁══════════════════════════════════════════════════════🐫")
    print("          🏛️   AS CHARADAS DA ESFINGE   🏛️")
    print("🐍══════════════════════════════════════════════════════🌴")
    print("                    🗿  ☀️  🐫  🌴  🦁")
    print()


def renderizar_placar(acertos: int, erros: int, recorde: dict):
    print(
        f"  🏆 Acertos: {acertos}  |  💀 Erros: {erros}  |  👑 Recorde: {recorde.get('recorde', 0)}",
        end="",
    )
    jogador_recorde = recorde.get("jogador", "")
    if jogador_recorde:
        print(f" ({jogador_recorde})", end="")
    print()
    print()


def renderizar_caixa_charada(texto: str):
    largura = 54
    print("  ╔" + "═" * largura + "╗")
    print("  ║ 🦁 CHARADA" + " " * (largura - 11) + "║")

    linhas = []
    palavras = texto.split()
    linha_atual = ""
    for palavra in palavras:
        candidato = f"{linha_atual} {palavra}".strip()
        if len(candidato) <= largura - 4:
            linha_atual = candidato
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)

    for linha in linhas:
        espacos = largura - len(linha) - 2
        print(f"  ║ {linha}{' ' * espacos} ║")

    print("  ╚" + "═" * largura + "╝")
    print()


def renderizar_dicas(dicas: list[str], reveladas: int):
    for indice in range(3):
        icone = DICA_ICONES[indice]
        titulo = DICA_TITULOS[indice]
        if indice < reveladas:
            conteudo = dicas[indice]
        elif indice == 0 and reveladas == 0:
            conteudo = AGUARDANDO
        else:
            conteudo = REVELANDO

        cabecalho = f"┌─ {icone} {titulo} "
        largura = 50
        cabecalho += "─" * (largura - len(cabecalho) + 1) + "┐"
        print(f"  {cabecalho}")

        espacos = largura - len(conteudo) - 2
        print(f"  │ {conteudo}{' ' * espacos} │")
        print(f"  └{'─' * largura}┘")
        print()


def tela_nome() -> str:
    limpar_tela()
    renderizar_banner()
    print("  🗿 Bem-vindo às areias do enigma, mortal.")
    print()
    while True:
        nome = input("  ☀️  Como te chamas, mortal? ").strip()
        if nome:
            return nome
        print("  🐍 A Esfinge exige que informes teu nome.")


def intro_esfinge(nome: str):
    limpar_tela()
    renderizar_banner()
    print(f"  🦁 Saudações, {nome}...")
    print()
    print("  Eu sou a guardiã das areias eternas, a Esfinge.")
    print("  Há milênios aguardo viajantes audazes diante das minhas charadas.")
    print()
    print("  Responde corretamente e avançarás pelas dunas do conhecimento.")
    print("  Erra três vezes... e serás devorado por mim.")
    print()
    print("  🐍 Ouve com atenção. Cada erro revelará um fragmento da verdade.")
    print("  🏛️  Apenas palavras do reino dos enigmas serão aceitas.")
    print()
    input("  🌴 Pressione Enter para começar...")


def obter_resposta_valida(vocabulario: set[str]) -> str:
    while True:
        resposta = input("  🗿 Tua resposta: ").strip()
        valida, mensagem = validar_entrada(resposta, vocabulario)
        if valida:
            return resposta
        print(f"  🐍 {mensagem}")


def jogar_charada(
    charada: dict,
    resposta_correta: str,
    vocabulario: set[str],
    acertos: int,
    erros_sessao: int,
    recorde: dict,
) -> tuple[bool, int, int]:
    tentativas = 3
    erros_charada = 0

    while tentativas > 0:
        limpar_tela()
        renderizar_banner()
        renderizar_placar(acertos, erros_sessao, recorde)
        renderizar_caixa_charada(charada["charada"])
        renderizar_dicas(charada["dicas"], erros_charada)
        print(f"  🐫 Tentativas restantes: {tentativas}")
        print()

        resposta = obter_resposta_valida(vocabulario)

        if normalizar(resposta) == normalizar(resposta_correta):
            print()
            print("  ☀️  CORRETO! A Esfinge assente com respeito...")
            input("  Pressione Enter para continuar...")
            return True, acertos + 1, erros_sessao

        erros_charada += 1
        erros_sessao += 1
        tentativas -= 1

        if tentativas > 0:
            print()
            print("  🐍 Errado! A Esfinge sussurra uma dica...")
            input("  Pressione Enter para tentar novamente...")

    limpar_tela()
    renderizar_banner()
    print()
    print("  🦁══════════════════════════════════════════════════════🐫")
    print()
    print("         Você foi devorado pela esfinge")
    print()
    print(f"  💀 Erros nesta sessão: {erros_sessao}")
    print()
    print("  🐍══════════════════════════════════════════════════════🌴")
    print()
    input("  Pressione Enter para recomeçar...")
    return False, acertos, erros_sessao


def executar_sessao():
    charadas, respostas, recorde = carregar_dados()
    vocabulario = construir_vocabulario(charadas, respostas)

    respostas_por_id = {item["id"]: item["resposta"] for item in respostas}
    ids = list(respostas_por_id.keys())
    random.shuffle(ids)

    charadas_por_id = {item["id"]: item for item in charadas}

    nome = tela_nome()
    intro_esfinge(nome)

    acertos = 0
    erros = 0

    for charada_id in ids:
        charada = charadas_por_id[charada_id]
        resposta = respostas_por_id[charada_id]
        acertou, acertos, erros = jogar_charada(
            charada, resposta, vocabulario, acertos, erros, recorde
        )

        if not acertou:
            recorde = atualizar_recorde(acertos, nome, recorde)
            return False

        recorde = atualizar_recorde(acertos, nome, recorde)

    limpar_tela()
    renderizar_banner()
    print()
    print(f"  🏛️  Parabéns, {nome}! Acertaste todas as charadas!")
    print(f"  👑 Acertos nesta sessão: {acertos}")
    print(f"  💀 Erros nesta sessão: {erros}")
    print(f"  🦁 Recorde: {recorde.get('recorde', 0)}")
    print()
    input("  Pressione Enter para jogar novamente...")
    return True


def main():
    while True:
        executar_sessao()


if __name__ == "__main__":
    main()
