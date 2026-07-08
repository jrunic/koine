import os

import pytest

from koine import cli
from tests import _parity


def test_mostrar_bate_com_go(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    go = _parity.mostrar_go(trab, "hermes", koine_home["home"])
    rc = cli.main(["mostrar", "hermes", trab])
    py = capsys.readouterr().out
    assert rc == 0
    assert _parity.normalize(py) == _parity.normalize(go)


def test_gerar_escreve_em_paridade(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    go = _parity.gerar_go(trab, "hermes", koine_home["home"])
    os.remove(os.path.join(trab, "CLAUDE.md"))
    rc = cli.main(["gerar", "hermes", trab])
    out = capsys.readouterr().out
    assert rc == 0
    py = open(os.path.join(trab, "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)
    assert out.startswith("Escrito ") and "bytes)" in out    # formato do Go


def test_mostrar_nao_resolve_alias(koine_home, monkeypatch, tmp_path):
    # Discriminante: Go mostrar trata o arg como PATH, não alias. De um cwd sem
    # ./koine, `mostrar hermes koine` deve tratar 'koine' como path relativo
    # inexistente e ERRAR — provando que NÃO resolve o alias (que apontaria ~/koine).
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.chdir(tmp_path)                 # cwd vazio, sem ./koine
    with pytest.raises(FileNotFoundError):      # CONTEXTO.md de ./koine não existe
        cli.main(["mostrar", "hermes", "koine"])
