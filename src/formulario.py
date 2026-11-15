"""Validação do formulário "Doar um kimono".

Regra de ouro: nunca confie no que vem do navegador. O navegador também confere
(required, type="tel"...), mas alguém pode burlar isso. Por isso conferimos aqui de novo.

Este arquivo não importa o Flask: só recebe os dados e devolve (dados, erros).
"""
import re

# Opções aceitas. O formulário mostra estas listas e o servidor só aceita estas.
TAMANHOS = ["M0", "M1", "M2", "M3", "M4", "A0", "A1", "A2", "A3", "A4"]
CORES = ["branco", "azul", "preto", "cinza", "verde", "amarelo",
        "laranja", "vermelho", "rosa", "roxo", "marrom"]

# Letras (com acento), separadas por espaço, apóstrofo ou hífen. Sem números.
_NOME = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$")


def normalizar_telefone(texto):
    """Deixa só os números. Aceita +55, parênteses, traços e espaços.
    Devolve os 10 ou 11 dígitos (DDD + número), ou None se não for um telefone válido."""
    numeros = re.sub(r"\D", "", texto or "")
    if numeros.startswith("55") and len(numeros) in (12, 13):
        numeros = numeros[2:]                       # tira o código do Brasil
    if len(numeros) not in (10, 11):
        return None
    ddd = numeros[:2]
    if ddd[0] == "0" or ddd[1] == "0":              # DDD vai de 11 a 99
        return None
    if len(numeros) == 11 and numeros[2] != "9":    # celular começa com 9
        return None
    if len(numeros) == 10 and numeros[2] == "9":    # fixo não começa com 9
        return None
    return numeros


def formatar_telefone(numeros):
    """'11912345678' -> '(11) 91234-5678'"""
    if not numeros:
        return ""
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"


def validar_kimono(form):
    """Confere os campos de texto. Devolve (dados, erros).
    - dados: os valores já limpos (só confiáveis se erros estiver vazio)
    - erros: dicionário {campo: mensagem}; vazio quer dizer que está tudo certo"""
    erros = {}
    dados = {}

    nome = " ".join((form.get("nome") or "").split())          # tira espaços repetidos
    if not nome:
        erros["nome"] = "Informe o nome."
    elif len(nome) < 2 or len(nome) > 60 or not _NOME.match(nome):
        erros["nome"] = "Use só letras, de 2 a 60 caracteres."
    dados["nome"] = nome

    texto_idade = (form.get("idade") or "").strip()
    if not texto_idade:
        erros["idade"] = "Informe a idade."
    elif not texto_idade.isdigit() or not (3 <= int(texto_idade) <= 99):
        erros["idade"] = "A idade deve ser um número de 3 a 99."
    dados["idade"] = int(texto_idade) if texto_idade.isdigit() and 3 <= int(texto_idade) <= 99 else None

    tamanho = (form.get("tamanho") or "").strip().upper()
    if tamanho not in TAMANHOS:
        erros["tamanho"] = "Escolha um tamanho da lista."
    dados["tamanho"] = tamanho

    cor = (form.get("cor") or "").strip().lower()
    if cor not in CORES:
        erros["cor"] = "Escolha uma cor da lista."
    dados["cor"] = cor

    tempo = " ".join((form.get("tempo_de_uso") or "").split())
    if not tempo:
        erros["tempo_de_uso"] = "Campo obrigatório."
    elif len(tempo) < 2 or len(tempo) > 40:
        erros["tempo_de_uso"] = "Use de 2 a 40 caracteres. Exemplo: 1 ano e meio."
    dados["tempo_de_uso"] = tempo

    telefone = normalizar_telefone(form.get("telefone"))
    if not (form.get("telefone") or "").strip():
        erros["telefone"] = "Informe um telefone para contato."
    elif telefone is None:
        erros["telefone"] = "Telefone inválido. Use DDD + número, por exemplo (11) 91234-5678."
    dados["telefone"] = telefone

    return dados, erros
