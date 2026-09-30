"""Gerenciador de Usuários TUI — regras de negócio (testáveis)."""
import hashlib
import json
import os
import base64
import secrets

# Arquivo de dados: sobrescrevível via ambiente (testes/máquinas variadas)
ENV_ARQUIVO = "GERENCIADOR_ARQUIVO"
PBKDF2_ITERATIONS = 100_000


def arquivo_dados() -> str:
    return os.environ.get(ENV_ARQUIVO, os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "usuarios.json"))


def _load() -> list:
    path = arquivo_dados()
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(users: list) -> None:
    path = arquivo_dados()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    os.replace(tmp, path)


def cpf_valido(cpf: str) -> bool:
    """Valida CPF pelos dígitos verificadores (algoritmo oficial)."""
    cpf = "".join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(cpf[num]) * peso
                   for num, peso in enumerate(range(i + 1, 1, -1)))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[i]):
            return False
    return True


def senha_valida(senha: str) -> bool:
    """Mín: minúscula, maiúscula, número e caractere especial."""
    return (any(c.islower() for c in senha)
            and any(c.isupper() for c in senha)
            and any(c.isdigit() for c in senha)
            and any(c in "!@#$%^&*()-_+=<>?/{}[]|~" for c in senha))


def _hash_senha(senha: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, PBKDF2_ITERATIONS)
    return base64.b64encode(dk).decode()


def registrar(nome: str, senha: str, cpf: str) -> str:
    """Registra usuário. Senha nunca vai ao disco em claro (PBKDF2+salt)."""
    if not nome.strip():
        raise ValueError("Nome vazio.")
    if not cpf_valido(cpf):
        raise ValueError("CPF inválido.")
    if not senha_valida(senha):
        raise ValueError("Senha inválida: use maiúscula, minúscula, número "
                         "e caractere especial.")
    cpf = "".join(filter(str.isdigit, cpf))
    users = _load()
    if any(u["cpf"] == cpf for u in users):
        raise ValueError("CPF já registrado.")
    salt = secrets.token_bytes(16)
    users.append({
        "nome": nome,
        "senha_hash": _hash_senha(senha, salt),
        "salt": base64.b64encode(salt).decode(),
        "cpf": cpf,
    })
    _save(users)
    return nome


def login(nome: str, senha: str) -> dict | None:
    """Autentica; devolve os dados (sem hash) ou None."""
    for u in _load():
        if u["nome"] != nome:
            continue
        salt = base64.b64decode(u["salt"])
        if secrets.compare_digest(u["senha_hash"], _hash_senha(senha, salt)):
            return {"nome": u["nome"], "cpf": u["cpf"]}
    return None


def listar() -> list:
    return [{"nome": u["nome"], "cpf": u["cpf"]} for u in _load()]
