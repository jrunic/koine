from tests import _parity


def test_go_gera_contra_fixture(koine_home):
    out = _parity.gerar_go(koine_home["trab"], "hermes", koine_home["home"])
    assert out.startswith("<!-- gerado por kn-agente -->")
    assert "@" in out  # tem linhas @path
