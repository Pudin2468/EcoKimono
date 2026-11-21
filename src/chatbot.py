"""Chatbot de dúvidas do EcoKimono (versão 1: por palavras-chave).

Como funciona: cada dúvida frequente tem uma lista de palavras-chave.
O bot conta quantas dessas palavras aparecem na pergunta e devolve a
resposta da dúvida com mais palavras em comum. Sem nenhuma, usa a
RESPOSTA_PADRAO (um bom bot admite quando não sabe).
"""
import unicodedata

# As palavras-chave ficam SEM acento e em minúsculas, porque a pergunta
# também passa por normalizar() antes da comparação.
FAQ = [
    {
        "palavras": ["doar", "doacao", "doo", "cadastrar", "cadastro", "anunciar"],
        "resposta": "Para doar, entre na sua conta de responsável, abra a página Kimonos "
                    "e clique em \"Doar um kimono\". Preencha os dados e envie uma foto "
                    "do kimono inteiro, de frente.",
    },
    {
        "palavras": ["pedir", "pegar", "receber", "conseguir", "reservar", "quero", "preciso"],
        "resposta": "Na página Kimonos, escolha um kimono disponível do tamanho certo e "
                    "clique em \"Pedir\". Ele fica reservado para você até a entrega. "
                    "Para pedir, é preciso entrar na conta de responsável.",
    },
    {
        "palavras": ["entrega", "entregar", "retirar", "retirada", "combinar", "confirmar"],
        "resposta": "A entrega acontece no treino. Na página Repasses aparece o contato "
                    "para combinar. Depois da entrega, quem doou ou quem recebeu clica em "
                    "\"Confirmar entrega\".",
    },
    {
        "palavras": ["tamanho", "tamanhos", "medida", "serve", "m0", "m1", "m2", "m3", "m4",
                     "a0", "a1", "a2", "a3", "a4"],
        "resposta": "Os tamanhos vão do M0 ao M4 (infantis) e do A0 ao A4 (adultos). "
                    "Na página Kimonos, cada kimono mostra o tamanho em destaque.",
    },
    {
        "palavras": ["login", "entrar", "conta", "senha", "logar"],
        "resposta": "Use o botão \"Entrar\" no topo da página. A conta é do responsável "
                    "pela criança, e só com ela dá para doar, pedir ou confirmar entregas.",
    },
    {
        "palavras": ["ibisocial", "instituicao", "parceira", "parceiro", "aulas", "treino", "onde"],
        "resposta": "O projeto é feito em parceria com a IBISOCIAL, instituição que "
                    "organiza as atividades de jiu-jitsu. É lá, no treino, que as "
                    "entregas são feitas.",
    },
    {
        "palavras": ["projeto", "ecokimono", "objetivo", "sobre", "funciona", "porque", "ods"],
        "resposta": "O EcoKimono ajuda famílias do jiu-jitsu a repassar kimonos e faixas "
                    "que ficaram pequenos. Assim gastamos menos recursos e mais crianças "
                    "continuam no tatame (ODS 12 e ODS 3).",
    },
]

RESPOSTA_PADRAO = ("Ainda não sei responder isso. Tente perguntar sobre como doar, "
                   "pedir um kimono, entrega, tamanhos ou a IBISOCIAL.")

TAMANHO_MAXIMO = 300   # perguntas maiores que isso são cortadas


def normalizar(texto):
    """Deixa minúsculo e tira acentos e pontuação: 'Doação?' vira 'doacao'."""
    sem_acento = unicodedata.normalize("NFD", texto.lower())
    letras = []
    for c in sem_acento:
        if unicodedata.category(c) == "Mn":     # acento solto (o NFD separa 'ç' em 'c' + acento)
            continue
        letras.append(c if c.isalnum() else " ")   # pontuação vira espaço
    return "".join(letras)


def responder(pergunta):
    """Escolhe a resposta cuja lista de palavras mais aparece na pergunta."""
    pergunta = (pergunta or "")[:TAMANHO_MAXIMO]
    palavras_da_pergunta = set(normalizar(pergunta).split())

    melhor_item, melhor_pontos = None, 0
    for item in FAQ:
        pontos = len(palavras_da_pergunta & set(item["palavras"]))   # palavras em comum
        if pontos > melhor_pontos:
            melhor_item, melhor_pontos = item, pontos

    return melhor_item["resposta"] if melhor_item else RESPOSTA_PADRAO


if __name__ == "__main__":
    # Teste rápido pelo terminal: python -m src.chatbot
    print("Chatbot EcoKimono (digite 'sair' para encerrar)")
    while True:
        pergunta = input("Você: ")
        if pergunta.strip().lower() == "sair":
            break
        print("Bot:", responder(pergunta))
