from flask import Flask, render_template, request, redirect, flash
from src.mocks import KIMONO, ATLETAS
from src.models import criar_repasse, concluir_repasse

app = Flask(__name__)
app.secret_key = "ecokimono-chave-teste"
REPASSES = []

@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/kimonos")
def lista_kimonos():
    return render_template("lista.html", kimonos=KIMONO)

@app.route("/repasses")
def lista_repasse():
    kimono_por_id = {}
    for k in KIMONO:
        kimono_por_id[k.id] = k
    return render_template("repasses.html", kimonos=kimono_por_id, atletas=ATLETAS, repasses=REPASSES)

@app.route("/kimonos/<int:kimono_id>/repassar", methods=["GET", "POST"])   
def repassar(kimono_id):
    kimono_achado = None
    for k in KIMONO:
        if k.id == kimono_id:
            kimono_achado = k
    if request.method == "POST":
        escolhido =int( request.form["destinatario_id"])
        try:
            ficha = criar_repasse(len(REPASSES) + 1, kimono_achado, escolhido, ATLETAS)
        except ValueError as erro:
            flash(str(erro), "erro")
            return redirect(f"/kimonos/{kimono_id}/repassar")
        REPASSES.append(ficha)
        return redirect("/repasses")
    return render_template("repassar.html", kimono=kimono_achado, atletas=ATLETAS.values())

@app.route("/repasses/<int:repasse_id>/concluir", methods=["POST"])
def concluir(repasse_id):
    for ficha in REPASSES:
        if ficha.id == repasse_id:
            
    return redirect("/repasses")