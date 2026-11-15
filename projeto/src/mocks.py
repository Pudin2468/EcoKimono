from src.models import atleta, kimono

# Dicionário: a "etiqueta" é o id, e o conteúdo é a ficha do atleta
ATLETAS = {
	1: atleta(id=1, nome="Lucas", idade=14),
	2: atleta(id=2, nome="Ana", idade=11),
	3: atleta(id=3, nome="Pedro", idade=9),
}

KIMONO = [
	kimono(1, "M1", "azul", "pouco uso", 1),
	kimono(2, "A2", "branco", "novo", 2),
]