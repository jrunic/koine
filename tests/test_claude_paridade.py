from koine import contexto
from koine.adapters import claude
from tests import _parity


def test_claude_md_bate_com_go(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    go = _parity.gerar_go(koine_home["trab"], "hermes", koine_home["home"])
    cm = contexto.resolver("hermes", koine_home["trab"])
    py = claude.renderizar(cm).arquivos_working_dir["CLAUDE.md"]
    assert _parity.normalize(py) == _parity.normalize(go)
    assert py.startswith("<!-- gerado por kn-agente -->")  # marcador congelado
