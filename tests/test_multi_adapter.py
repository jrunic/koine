import os

from koine import cli


def test_agy_escreve_gemini_nao_claude(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)  # não lança
    for nome in ("CLAUDE.md", "GEMINI.md"):
        p = os.path.join(trab, nome)
        if os.path.exists(p):
            os.remove(p)
    rc = cli.main(["agy", "hermes", trab])
    assert rc == 0
    assert os.path.exists(os.path.join(trab, "GEMINI.md"))       # adapter agy
    assert not os.path.exists(os.path.join(trab, "CLAUDE.md"))   # NÃO CLAUDE
    conteudo = open(os.path.join(trab, "GEMINI.md"), encoding="utf-8").read()
    assert conteudo.splitlines()[1] == "# GEMINI.md"


def test_claude_ainda_escreve_claude(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)
    rc = cli.main(["claude", "hermes", trab])
    assert rc == 0
    assert os.path.exists(os.path.join(trab, "CLAUDE.md"))       # regressão
