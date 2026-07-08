import os

from koine import cli, contexto
from koine.adapters import claude
from tests import _parity


def _pasta_bootstrap(home):
    pasta = os.path.join(home, "koine")
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "CONTEXTO.md"), "w") as f:
        f.write("---\nbootstrap: true\n---\n\n# Bootstrap\n")
    return pasta


def test_bootstrap_claude_bate_com_go(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_bootstrap(koine_home["home"])
    go = _parity.gerar_go(pasta, "hermes", koine_home["home"])
    cm = contexto.resolver("hermes", pasta)
    py = claude.renderizar(cm)
    assert _parity.normalize(py) == _parity.normalize(go)
    assert py.startswith("<!-- gerado por kn-agente -->")
    assert "modo bootstrap" in py


def test_cli_bootstrap_e2e(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_bootstrap(koine_home["home"])
    go = _parity.gerar_go(pasta, "hermes", koine_home["home"])
    os.remove(os.path.join(pasta, "CLAUDE.md"))
    rc = cli.main(["claude", "hermes", pasta])
    assert rc == 0
    py = open(os.path.join(pasta, "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)
