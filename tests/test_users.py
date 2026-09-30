"""Testes do gerenciador-usuarios-tui (CPF determinístico)."""
import json
import os
import sys
import tempfile

_TMP = tempfile.mkdtemp(prefix="gui_")
os.environ["GERENCIADOR_ARQUIVO"] = os.path.join(_TMP, "usuarios.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.users import cpf_valido, login, registrar, senha_valida, listar


def _dv(base: str) -> str:
    """Gera dígito verificador (algoritmo oficial) para 9/10 dígitos base."""
    soma = sum(int(c) * p for c, p in zip(base, range(len(base) + 1, 1, -1)))
    d = (soma * 10) % 11
    return "0" if d == 10 else str(d)


def make_cpf(base9: str) -> str:
    d1 = _dv(base9)
    d2 = _dv(base9 + d1)
    return base9 + d1 + d2


CPF_A = "52998224725"  # clássico válido
CPF_B = make_cpf("111444777")


def test_cpf_valido():
    assert cpf_valido(CPF_A)
    assert cpf_valido("529.982.247-25")
    assert cpf_valido(CPF_B)
    assert not cpf_valido("52998224726")       # DV errado
    assert not cpf_valido("111.111.111-11")    # repetido
    assert not cpf_valido("123")
    assert not cpf_valido("abc")


def test_senha_valida():
    assert senha_valida("Abc123!@#")
    assert not senha_valida("abc123!@#")
    assert not senha_valida("ABC123!@#")
    assert not senha_valida("Abcdef!@#")
    assert not senha_valida("Abc123456")


def test_cpfs_duplicados_e_validacoes():
    registrar("X", "Abc123!xyz", CPF_A)       # primeira — ok
    try:
        registrar("X2", "Abc123!xyz", CPF_A)   # CPF duplicado
        raise AssertionError("duplicado deveria falhar")
    except ValueError:
        pass
    try:
        registrar("Y", "fraca", CPF_B)         # senha fraca
        raise AssertionError("senha fraca deveria falhar")
    except ValueError:
        pass
    try:
        registrar("Z", "Abc123!xyz", "12345678901")  # CPF inválido
        raise AssertionError("cpf inválido deveria falhar")
    except ValueError:
        pass


def test_registrar_login_fluxo():
    registrar("Athos", "SenhaForte1!", CPF_B)
    u = login("Athos", "SenhaForte1!")
    assert u and u["nome"] == "Athos" and u["cpf"] == CPF_B
    assert login("Athos", "senha_errada") is None
    assert login("nao_existe", "SenhaForte1!") is None


def test_senha_nunca_em_claro():
    cpf3 = make_cpf("935411347")
    registrar("Outro", "OutraForte1!", cpf3)
    raw = open(os.environ["GERENCIADOR_ARQUIVO"], encoding="utf-8").read()
    assert "SenhaForte1!" not in raw and "OutraForte1!" not in raw
    data = json.loads(raw)
    assert all("senha_hash" in u and "salt" in u for u in data)
    assert len(listar()) >= 2


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"✅ {fn.__name__}")
    print(f"\n{len(fns)} testes passaram.")
