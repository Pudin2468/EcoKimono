"""Contas dos responsáveis (quem faz login no EcoKimono).

Regra de ouro: a senha NUNCA é guardada como texto. Guardamos só o "hash":
uma versão embaralhada que não dá para desfazer. No login, embaralhamos a
senha digitada e comparamos os dois embaralhados.

Este arquivo não importa o models.py nem o mocks.py (evita o import circular).
"""
from dataclasses import dataclass, field
from werkzeug.security import generate_password_hash, check_password_hash


@dataclass
class usuario:
    id: int
    nome: str
    email: str
    senha_hash: str                                   # senha embaralhada, nunca o texto
    atletas_ids: list = field(default_factory=list)   # números dos atletas pelos quais responde


# Senha das contas de demonstração (mostre ao professor!). Em um site real,
# cada pessoa criaria a própria senha.
SENHA_DEMO = "ecokimono123"

USUARIOS = [
    usuario(1, "Marcos", "marcos@exemplo.com",
            generate_password_hash(SENHA_DEMO), [1]),
    usuario(2, "Carla", "carla@exemplo.com",
            generate_password_hash(SENHA_DEMO), [2, 3]),
]

# Hash de mentira, usado quando o e-mail não existe: assim o tempo de resposta é
# o mesmo e ninguém descobre quais e-mails estão cadastrados.
_HASH_FALSO = generate_password_hash("senha-que-ninguem-tem")


def achar_usuario_por_id(usuario_id):
    """Devolve o usuário com esse número, ou None."""
    for u in USUARIOS:
        if u.id == usuario_id:
            return u
    return None


def autenticar(email, senha):
    """Confere e-mail e senha. Devolve o usuário se estiver certo, senão None."""
    email = (email or "").strip().lower()             # ignora espaços e maiúsculas
    achado = None
    for u in USUARIOS:
        if u.email == email:
            achado = u
    if achado is None:
        check_password_hash(_HASH_FALSO, senha or "")  # gasta o mesmo tempo
        return None
    if check_password_hash(achado.senha_hash, senha or ""):
        return achado
    return None
