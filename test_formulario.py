"""Testes das validações do formulário de doação (rode com: python -m pytest -v)."""
import pytest
from src.formulario import validar_kimono, normalizar_telefone, formatar_telefone

# Um formulário todo certo, para ir estragando um campo de cada vez nos testes
CERTO = {
    "nome": "Lucas Silva", "idade": "12", "tamanho": "M1", "cor": "azul",
    "tempo_de_uso": "1 ano e meio", "telefone": "(11) 91234-5678",
}


def com(**mudancas):
    """Cópia do formulário certo com alguns campos trocados."""
    return {**CERTO, **mudancas}


def test_formulario_certo_nao_tem_erros():
    dados, erros = validar_kimono(CERTO)
    assert erros == {}
    assert dados["nome"] == "Lucas Silva"
    assert dados["idade"] == 12
    assert dados["telefone"] == "11912345678"        # só números


def test_tempo_de_uso_vazio_e_obrigatorio():
    for vazio in ["", "   ", None]:
        _, erros = validar_kimono(com(tempo_de_uso=vazio))
        assert erros["tempo_de_uso"] == "Campo obrigatório."


def test_tempo_de_uso_e_texto_limpo():
    dados, erros = validar_kimono(com(tempo_de_uso="  6    meses  "))
    assert erros == {}
    assert dados["tempo_de_uso"] == "6 meses"         # espaços repetidos saem


def test_tempo_de_uso_muito_longo():
    _, erros = validar_kimono(com(tempo_de_uso="a" * 41))
    assert "tempo_de_uso" in erros


@pytest.mark.parametrize("nome", ["", "A", "Lucas123", "<script>", "Lu_cas", "x" * 61])
def test_nome_invalido(nome):
    _, erros = validar_kimono(com(nome=nome))
    assert "nome" in erros


@pytest.mark.parametrize("nome", ["Ana", "João Pedro", "D'Ávila", "Maria-Clara", "Zoë Müller"])
def test_nome_valido(nome):
    _, erros = validar_kimono(com(nome=nome))
    assert "nome" not in erros


@pytest.mark.parametrize("idade", ["", "abc", "2", "100", "-5", "12.5", "1e1"])
def test_idade_invalida(idade):
    _, erros = validar_kimono(com(idade=idade))
    assert "idade" in erros


@pytest.mark.parametrize("tamanho", ["", "G", "M9", "A5", "m1 "])
def test_tamanho_so_da_lista(tamanho):
    _, erros = validar_kimono(com(tamanho=tamanho))
    if tamanho.strip().upper() == "M1":               # "m1 " vira "M1": aceito
        assert "tamanho" not in erros
    else:
        assert "tamanho" in erros


def test_cor_so_da_lista():
    _, erros = validar_kimono(com(cor="dourado"))
    assert "cor" in erros
    _, erros = validar_kimono(com(cor="Azul"))        # maiúscula é aceita
    assert "cor" not in erros


@pytest.mark.parametrize("texto, esperado", [
    ("(11) 91234-5678", "11912345678"),
    ("11 91234 5678", "11912345678"),
    ("+55 11 91234-5678", "11912345678"),
    ("5511912345678", "11912345678"),
    ("(21) 2345-6789", "2123456789"),                 # fixo, 10 dígitos
])
def test_telefone_valido(texto, esperado):
    assert normalizar_telefone(texto) == esperado


@pytest.mark.parametrize("texto", [
    "", "abc", "12345", "(11) 1234-5678-9", "(00) 91234-5678",
    "(11) 81234-5678",                                # celular precisa começar com 9
    "(11) 9234-5678",                                 # fixo não começa com 9
    "(01) 91234-5678",
])
def test_telefone_invalido(texto):
    assert normalizar_telefone(texto) is None


def test_telefone_obrigatorio_e_invalido_dao_mensagens_diferentes():
    _, erros = validar_kimono(com(telefone=""))
    assert erros["telefone"] == "Informe um telefone para contato."
    _, erros = validar_kimono(com(telefone="123"))
    assert "inválido" in erros["telefone"]


def test_formatar_telefone():
    assert formatar_telefone("11912345678") == "(11) 91234-5678"
    assert formatar_telefone("2123456789") == "(21) 2345-6789"
    assert formatar_telefone("") == ""


def test_varios_erros_de_uma_vez():
    _, erros = validar_kimono({})
    assert set(erros) == {"nome", "idade", "tamanho", "cor", "tempo_de_uso", "telefone"}
