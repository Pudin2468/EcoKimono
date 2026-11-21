"""Testes do chatbot de dúvidas (rode com: python -m pytest -v)."""
import pytest
from src.chatbot import responder, normalizar, RESPOSTA_PADRAO
from app import app


# ---------- A lógica do bot ----------
def test_normalizar_tira_acento_maiuscula_e_pontuacao():
    assert normalizar("Doação?") == "doacao "
    assert normalizar("IBISOCIAL!").split() == ["ibisocial"]


@pytest.mark.parametrize("pergunta, trecho", [
    ("Como faço pra DOAR um kimono?", "Doar um kimono"),
    ("Quero pedir um kimono", "Pedir"),
    ("Como funciona a entrega?", "Confirmar entrega"),
    ("Qual tamanho serve no meu filho?", "M0 ao M4"),
    ("Esqueci como entrar na conta", "Entrar"),
    ("O que é a IBISOCIAL?", "IBISOCIAL"),
])
def test_responde_cada_duvida(pergunta, trecho):
    assert trecho in responder(pergunta)


def test_pergunta_desconhecida_usa_resposta_padrao():
    assert responder("Qual a previsão do tempo?") == RESPOSTA_PADRAO


def test_pergunta_vazia_ou_none_nao_quebra():
    assert responder("") == RESPOSTA_PADRAO
    assert responder(None) == RESPOSTA_PADRAO


# ---------- A página /duvidas ----------
@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    with app.test_client() as c:
        c.get("/duvidas")                            # abre a página: a sessão ganha o código csrf
        yield c


def csrf_de(cliente):
    with cliente.session_transaction() as sessao:
        return sessao["csrf"]


def test_pagina_abre(cliente):
    resposta = cliente.get("/duvidas")
    assert resposta.status_code == 200
    assert "Tire sua dúvida" in resposta.get_data(as_text=True)


def test_pergunta_pelo_javascript_recebe_json(cliente):
    resposta = cliente.post("/duvidas", data={"csrf": csrf_de(cliente), "pergunta": "como doar?"},
                            headers={"Accept": "application/json"})
    assert resposta.status_code == 200
    assert "Doar um kimono" in resposta.get_json()["resposta"]


def test_pergunta_sem_javascript_recebe_a_pagina(cliente):
    resposta = cliente.post("/duvidas", data={"csrf": csrf_de(cliente), "pergunta": "como doar?"})
    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert "como doar?" in html
    assert "Doar um kimono" in html


def test_pergunta_com_html_aparece_como_texto(cliente):
    resposta = cliente.post("/duvidas", data={"csrf": csrf_de(cliente),
                                              "pergunta": "<script>alert(1)</script>"})
    html = resposta.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html   # o Jinja troca < e > por &lt; e &gt;


def test_post_sem_csrf_e_recusado(cliente):
    resposta = cliente.post("/duvidas", data={"pergunta": "como doar?"})
    assert resposta.status_code == 400
