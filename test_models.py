import pytest
from src.models import statusitem, kimono, repasse, criar_repasse, concluir_repasse
from src.mocks import ATLETAS
from src.storage import kimono_para_dict, dict_para_kimono, salvar_kimonos, carregar_kimonos

# --------------------------------------------------------------

def test_kimono_nasce_disponivel():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	assert k.status == statusitem.DISPONIVEL

def test_reservar_mudar_status():
	k = kimono(1, "M1", "preto", "novo", 1)
	k.reservar()
	assert k.status == statusitem.RESERVADO

def test_reservar_duas_vezes_erro():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	k.reservar()
	with pytest.raises(ValueError):
		k.reservar()
		
def test_entregar_sem_reservar_erro():
	k = kimono(1, "M1", "preto", "novo", 1)
	with pytest.raises(ValueError):
		k.entregar()
		
def test_caminho_certo():
	k = kimono(1, "M1", "preto", "novo", 1)
	k.reservar()
	k.entregar()
	assert k.status == statusitem.ENTREGUE
	
def test_entregar_duas_vezes_erro():
	k = kimono(1, "M1", "preto", "novo", 1)
	k.reservar()
	k.entregar()
	with pytest.raises(ValueError):
		k.entregar()

# --------------------------------------------------------------
		
# define dados de repasse
def test_repassar_dados():
	r = repasse(1, 1, 1, 2)
	assert r.destinatario_id == 2
	
def test_criar_repasse():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	r = criar_repasse(1, k, 2, ATLETAS)
	assert r.destinatario_id == 2
	assert k.status == statusitem.RESERVADO
	
def test_repasse_para_mesma_pessoa():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	with pytest.raises(ValueError):
		criar_repasse(1, k, 1, ATLETAS)
	assert k.status == statusitem.DISPONIVEL

def test_repasse_duas_vezes():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	criar_repasse(1, k, 2, ATLETAS)
	with pytest.raises(ValueError):
		criar_repasse(1, k, 3, ATLETAS)

def test_concluir_repasse():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	r = criar_repasse(1, k, 2, ATLETAS)
	concluir_repasse(r, k)
	assert k.status == statusitem.ENTREGUE

def test_concluir_repasse_de_outro_kimono():
	k1 = kimono(1, "M1", "azul", "pouco uso", 1)
	k2 = kimono(2, "M1", "azul", "pouco uso", 1)
	r = criar_repasse(1, k1, 2, ATLETAS)
	with pytest.raises(ValueError):
		concluir_repasse(r, k2)
	assert k2.status == statusitem.DISPONIVEL

def test_concluir_repasse_sem_reservar():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	assert k.status == statusitem.DISPONIVEL
	r = repasse(1, 1, 1, 2)
	with pytest.raises(ValueError):
		concluir_repasse(r, k)
	assert k.status == statusitem.DISPONIVEL

def test_repasse_para_atleta_inexistente():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	with pytest.raises(ValueError):
		criar_repasse(1, k, 99, ATLETAS)
	assert k.status == statusitem.DISPONIVEL

# --------------------------------------------------------------

def test_kimono_ida_e_volta():
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	k.reservar()
	copia = dict_para_kimono(kimono_para_dict(k))
	assert copia == k

def test_salvar_e_carregar(tmp_path):
	caminho = tmp_path / "kimonos.json"
	k = kimono(1, "M1", "azul", "pouco uso", 1)
	k.reservar()
	salvar_kimonos([k], caminho)
	assert carregar_kimonos(caminho) == [k]

