from enum import Enum
from dataclasses import dataclass


class statusitem(Enum):
	DISPONIVEL = "DISPONIVEL"
	RESERVADO = "RESERVADO"
	ENTREGUE = "ENTREGUE"


TRANSICOES = {
	statusitem.DISPONIVEL: [statusitem.RESERVADO],
	statusitem.RESERVADO: [statusitem.ENTREGUE],
	statusitem.ENTREGUE: [],
}
def mudar_status(atual, novo):
	permitidos = TRANSICOES[atual]
	if novo in permitidos:
		return novo
	else:
		raise ValueError(f"Não pode ir de {atual.value} para {novo.value}")


@dataclass
class atleta:
	id: int
	nome: str
	idade: int

@dataclass
class kimono:
	id: int
	tamanho: str
	cor: str
	estado_de_conservacao: str
	doador: int  # número (id) do atleta que doou
	status: statusitem = statusitem.DISPONIVEL
	# campos do cadastro com foto (têm valor padrão, então o código antigo continua funcionando)
	foto: str = ""            # caminho da foto dentro de static, ex.: "uploads/ab12.jpg"
	tempo_de_uso: str = ""    # texto livre, ex.: "1 ano e meio"
	telefone: str = ""        # só os números, ex.: "11912345678"

	# muda o próprio status
	def reservar(self):
		self.status = mudar_status(self.status, statusitem.RESERVADO)

	def entregar(self):
		self.status = mudar_status(self.status, statusitem.ENTREGUE)
		
@dataclass
class repasse:
	id: int
	kimono_id: int
	doador_id: int
	destinatario_id: int
	
# teste de repasse
def criar_repasse(id, kimono, destinatario_id, atletas):
	# O destinatario precisa existir
	if destinatario_id not in atletas:
		raise ValueError("Atleta nao existe")
	# O doador e o destinatario nao podem ser a mesma pessoa
	if kimono.doador == destinatario_id:
		raise ValueError ("Não pode doar para si mesmo")
	kimono.reservar()
	# Se passar pela regra, preenche e retorna a ficha
	return repasse(id, kimono.id, kimono.doador, destinatario_id)
	
def concluir_repasse(recibo, kimono):
	# O recibo precisa ser do mesmo kimono
	if recibo.kimono_id != kimono.id:
		raise ValueError("Esse repasse nao é do desse kimono")
	kimono.entregar()
	return kimono
