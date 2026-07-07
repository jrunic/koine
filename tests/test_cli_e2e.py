import os

from koine import cli
from tests import _parity


def test_koine_claude_gera_claude_md_igual_ao_go(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    go = _parity.gerar_go(koine_home["trab"], "hermes", koine_home["home"])
    os.remove(os.path.join(koine_home["trab"], "CLAUDE.md"))

    rc = cli.main(["claude", "hermes", koine_home["trab"]])
    assert rc == 0
    py = open(os.path.join(koine_home["trab"], "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)


def test_versao(capsys):
    assert cli.main(["versao"]) == 0
    assert "koine" in capsys.readouterr().out.lower()
