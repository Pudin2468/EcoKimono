from dataclasses import asdict
from src.models import atleta, kimono, repasse, statusitem, criar_repasse, concluir_repasse
import json

# Transforma ficha em dicionario
def kimono_para_dict(k):            # IDA: ficha vira dicionario
    d = asdict(k)
    d["status"] = k.status.value
    return d

def dict_para_kimono(d):            # VOLTA: dicionario vira ficha
    d["status"] = statusitem(d["status"])
    return kimono(**d)


def salvar_kimonos(kimonos, caminho):                   # kimonos = lista de fichas
    dados = []                                          # lista de dicionarios vazia
    for k in kimonos:                                   # Para cada ficha da lista transforma em dicionario e guarda
        dados.append(kimono_para_dict(k))
    with open(caminho, "w", encoding="utf-8") as arq:   # Abre para escrever ("w")
        json.dump(dados, arq, indent=2)                 # Escreve a lista no arquivo


def carregar_kimonos(caminho):
    with open(caminho, "r", encoding="utf-8") as arq:   # Abre para ler ("r")
        dados = json.load(arq)                          # Le o texto e devolve a lista de dicionarios
    kimonos = []                                        # Lista de fichas vazia
    for d in dados:
        kimonos.append(dict_para_kimono(d))             # Para cada dicionario lido transforma em ficha e retorna
    return kimonos