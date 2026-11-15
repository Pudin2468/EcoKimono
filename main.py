from src.models import statusitem, mudar_status, kimono
from src.mocks import ATLETAS

kimono_teste = kimono(
	id = 1,
	tamanho = "M1",
	cor = "azul",
	estado_de_conservacao = "pouco uso",
	doador = 1,
	status = statusitem.DISPONIVEL
)

print(kimono_teste.status.value)

kimono_teste.reservar()
try:
	kimono_teste.status = mudar_status(kimono_teste.status, statusitem.RESERVADO)
except ValueError as erro:
	print("Mudança bloqueada")
	print(erro)
else:
	print("Mudança feita. O programa continua")
print(kimono_teste.status.value)

kimono_teste.entregar()
print(kimono_teste.status.value)


try:
	print(ATLETAS[1])
except KeyError as erro:
	print(f"Não existe o atleta nº{erro}")
