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


def test_alias_resolve_no_gerar(koine_home, monkeypatch):
    from koine import aliases
    home = koine_home["home"]; monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    canon = os.path.join(home, "koine"); os.makedirs(canon, exist_ok=True)
    with open(os.path.join(canon, "CONTEXTO.md"), "w") as f:
        f.write("---\nbootstrap: true\n---\n\n# Bootstrap\n")
    aliases.adicionar("koine", "koine", "home")                 # alias koine → ~/koine
    go = _parity.gerar_go_arg("koine", "hermes", home, canon)   # Go resolve o alias → ~/koine
    if os.path.exists(os.path.join(canon, "CLAUDE.md")):
        os.remove(os.path.join(canon, "CLAUDE.md"))
    rc = cli.main(["gerar", "hermes", "koine"])                 # Python resolve o alias
    assert rc == 0
    py = open(os.path.join(canon, "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)       # mesmo destino, mesmo conteúdo
