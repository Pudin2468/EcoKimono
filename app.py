import os
import secrets
from functools import wraps

from flask import (Flask, render_template, request, redirect, flash,
                    session, abort, g, jsonify)
from src.chatbot import responder
from src.mocks import KIMONO, ATLETAS
from src.models import criar_repasse, concluir_repasse, kimono as Kimono, atleta as Atleta
from src.usuarios import autenticar, achar_usuario_por_id
from src.formulario import validar_kimono, formatar_telefone, TAMANHOS, CORES
from src.fotos import abrir_foto, gravar_foto

app = Flask(__name__)
# A chave assina o "crachá" (cookie) do login. Em produção, defina a variável
# ECOKIMONO_SECRET com um texto longo e secreto; o texto abaixo é só para testes.
app.secret_key = os.environ.get("ECOKIMONO_SECRET", "ecokimono-chave-teste-trocar")
app.config["SESSION_COOKIE_HTTPONLY"] = True      # JavaScript não consegue ler o crachá
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"     # outro site não manda o crachá junto
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024        # recusa envios maiores que 5 MB
app.config["UPLOAD_DIR"] = os.path.join(app.static_folder, "uploads")   # onde ficam as fotos

REPASSES = []                                     # caixa de fichas de repasse (começa vazia)


# ---------- Ajudantes ----------
def achar_kimono(kimono_id):
    """Procura o kimono pelo número. Devolve o kimono, ou None se não existir."""
    for k in KIMONO:
        if k.id == kimono_id:
            return k
    return None


def caminho_seguro(destino):
    """Só aceita endereços DO PRÓPRIO SITE (começam com uma barra só).
    Evita que um link malicioso mande a pessoa para outro site depois do login."""
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return "/kimonos"


# ---------- Login: quem é a pessoa? ----------
@app.before_request
def carregar_usuario():
    """Antes de cada página: olha o crachá (sessão) e descobre quem está logado."""
    g.usuario = achar_usuario_por_id(session.get("usuario_id"))


@app.before_request
def conferir_csrf():
    """Todo formulário POST precisa trazer o código secreto da sessão.
    Isso impede que outro site faça a pessoa pedir kimono sem querer (CSRF)."""
    if request.method == "POST":
        enviado = request.form.get("csrf", "")
        esperado = session.get("csrf", "")
        if not esperado or not secrets.compare_digest(enviado, esperado):
            abort(400)


@app.context_processor
def dados_para_as_paginas():
    """Deixa 'usuario' e 'csrf_token' disponíveis em TODOS os templates."""
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return {"usuario": getattr(g, "usuario", None), "csrf_token": session["csrf"],
            "mostrar_telefone": formatar_telefone}   # deixa 11912345678 bonito: (11) 91234-5678


def login_obrigatorio(funcao):
    """Etiqueta @login_obrigatorio: se não estiver logado, vai para /login e,
    depois de entrar, volta para a página que tentava abrir."""
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if g.usuario is None:
            flash("Entre na sua conta para continuar.", "erro")
            return redirect("/login?proximo=" + request.path)
        return funcao(*args, **kwargs)
    return protegida


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pessoa = autenticar(request.form.get("email"), request.form.get("senha"))
        if pessoa is None:
            # mesma frase para e-mail errado e senha errada: não ensina nada a um invasor
            flash("E-mail ou senha incorretos.", "erro")
            return redirect("/login?proximo=" + caminho_seguro(request.form.get("proximo")))
        proximo = caminho_seguro(request.form.get("proximo"))
        session.clear()                            # crachá novo a cada login
        session["usuario_id"] = pessoa.id
        flash(f"Bem-vindo(a), {pessoa.nome}!", "ok")
        return redirect(proximo)
    return render_template("login.html", proximo=caminho_seguro(request.args.get("proximo")))


@app.route("/sair", methods=["POST"])
def sair():
    session.clear()
    flash("Você saiu da sua conta.", "ok")
    return redirect("/")


# ---------- Páginas ----------
@app.route("/")
def inicio():
    return render_template("inicio.html")


@app.route("/kimonos")
def lista_kimonos():
    return render_template("lista.html", kimonos=KIMONO, atletas=ATLETAS)


@app.route("/kimonos/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo_kimono():
    """Cadastro de um kimono para doação (só responsável logado)."""
    valores, erros = {}, {}

    if request.method == "POST":
        dados, erros = validar_kimono(request.form)       # confere os campos de texto
        valores = request.form                            # para devolver o que a pessoa já digitou
        imagem = None
        try:
            imagem = abrir_foto(request.files.get("foto"))   # confere a foto de verdade
        except ValueError as erro:
            erros["foto"] = str(erro)

        if not erros:
            # a criança que doa vira um atleta deste responsável (ou usa o que já existe com o mesmo nome)
            doador = None
            for numero in g.usuario.atletas_ids:
                if numero in ATLETAS and ATLETAS[numero].nome.casefold() == dados["nome"].casefold():
                    doador = ATLETAS[numero]
                    doador.idade = dados["idade"]         # a idade pode ter mudado
            if doador is None:
                doador = Atleta(max(ATLETAS) + 1, dados["nome"], dados["idade"])
                ATLETAS[doador.id] = doador
                g.usuario.atletas_ids.append(doador.id)

            novo = Kimono(
                id=max(k.id for k in KIMONO) + 1 if KIMONO else 1,
                tamanho=dados["tamanho"],
                cor=dados["cor"],
                estado_de_conservacao="Não informado",
                doador=doador.id,
                foto=gravar_foto(imagem, app.config["UPLOAD_DIR"]),   # só grava se está tudo certo
                tempo_de_uso=dados["tempo_de_uso"],
                telefone=dados["telefone"],
            )
            KIMONO.append(novo)
            flash("Kimono cadastrado! Ele já aparece na lista.", "ok")
            return redirect("/kimonos")

        return render_template("nova.html", erros=erros, valores=valores,
                                tamanhos=TAMANHOS, cores=CORES), 400

    return render_template("nova.html", erros=erros, valores=valores,
                            tamanhos=TAMANHOS, cores=CORES)


@app.route("/repasses")
def lista_repasse():
    # estante com etiquetas: o número do kimono aponta para o kimono
    kimono_por_id = {}
    for k in KIMONO:
        kimono_por_id[k.id] = k
    return render_template("repasses.html", kimonos=kimono_por_id, atletas=ATLETAS, repasses=REPASSES)


@app.route("/kimonos/<int:kimono_id>/repassar", methods=["GET", "POST"])
@login_obrigatorio
def repassar(kimono_id):
    kimono_achado = achar_kimono(kimono_id)
    # só os atletas deste responsável (cada um enxerga apenas os seus)
    meus_atletas = [ATLETAS[i] for i in g.usuario.atletas_ids if i in ATLETAS]

    if request.method == "POST":
        if kimono_achado is None:
            flash("Esse kimono não existe.", "erro")
            return redirect("/kimonos")

        try:
            escolhido = int(request.form["destinatario_id"])   # o formulário manda texto: vira número
        except (KeyError, ValueError):
            flash("Escolha o atleta que vai receber.", "erro")
            return redirect(f"/kimonos/{kimono_id}/repassar")

        # a página só mostra os atletas do responsável, mas alguém pode forjar o pedido:
        # por isso conferimos de novo aqui, no servidor
        if escolhido not in g.usuario.atletas_ids:
            abort(403)

        try:
            ficha = criar_repasse(len(REPASSES) + 1, kimono_achado, escolhido, ATLETAS)
        except ValueError as erro:                         # regras do models.py (mesma pessoa, status errado...)
            flash(str(erro), "erro")
            return redirect(f"/kimonos/{kimono_id}/repassar")

        REPASSES.append(ficha)                             # só guarda se não deu erro
        flash("Pedido feito! O kimono está reservado.", "ok")
        return redirect("/repasses")

    return render_template("repassar.html", kimono=kimono_achado, atletas=meus_atletas)


@app.route("/repasses/<int:repasse_id>/concluir", methods=["POST"])   # só POST: entregar muda o estado
@login_obrigatorio
def concluir(repasse_id):
    for ficha in REPASSES:                                 # procura a ficha com esse número
        if ficha.id == repasse_id:
            # só quem participa do repasse (responsável de quem doa ou de quem recebe) confirma
            if (ficha.doador_id not in g.usuario.atletas_ids
                    and ficha.destinatario_id not in g.usuario.atletas_ids):
                abort(403)
            kimono_da_ficha = achar_kimono(ficha.kimono_id)
            try:
                concluir_repasse(ficha, kimono_da_ficha)   # RESERVADO -> ENTREGUE (com as regras)
            except ValueError as erro:
                flash(str(erro), "erro")
            else:
                flash("Entrega confirmada! Obrigado por repassar.", "ok")
            break                                          # achou a ficha: para de procurar
    else:                                                  # o for terminou sem achar nenhuma
        flash("Repasse não encontrado.", "erro")
    return redirect("/repasses")


# ---------- Chatbot de dúvidas ----------
@app.route("/duvidas", methods=["GET", "POST"])
def duvidas():
    """Página do chatbot. O app.js envia a pergunta sem recarregar a página e
    recebe JSON. Sem JavaScript, o formulário funciona do jeito normal."""
    if request.method == "POST":
        pergunta = request.form.get("pergunta", "").strip()
        resposta = responder(pergunta)
        if request.accept_mimetypes.best == "application/json":   # pedido feito pelo app.js
            return jsonify({"resposta": resposta})
        return render_template("duvidas.html", pergunta=pergunta, resposta=resposta)
    return render_template("duvidas.html")


# ---------- Páginas de erro ----------
@app.errorhandler(404)
def nao_achou(e):
    return render_template("erro.html"), 404


@app.errorhandler(403)
def sem_permissao(e):
    return render_template("erro.html", titulo="Sem permissão",
                            mensagem="Você não tem permissão para fazer isso."), 403


@app.errorhandler(413)
def arquivo_grande(e):
    return render_template("erro.html", titulo="Arquivo grande demais",
                            mensagem="A foto pode ter no máximo 5 MB. Escolha uma menor e tente de novo."), 413


@app.errorhandler(400)
def pedido_invalido(e):
    return render_template("erro.html", titulo="Pedido inválido",
                            mensagem="Não foi possível concluir. Volte, recarregue a página e tente de novo."), 400
