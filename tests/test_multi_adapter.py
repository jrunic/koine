import os

from koine import cli


def _bundle_do(lanc_externos):
    return [os.path.basename(p) for p in lanc_externos]


def test_agy_entrega_gemini_nao_claude(koine_home, monkeypatch):
    """O adapter certo é escolhido pelo cliente — a regressão que este teste
    guarda é `kn-agy` entregando o arquivo do Claude. O que mudou é ONDE: o
    arquivo vive no bundle do cache, e a pasta não recebe nada."""
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    capturado = {}
    monkeypatch.setattr("koine.cli._materializar",
                        lambda lanc, pasta: capturado.update(lanc=lanc))
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)

    assert cli.main(["agy", "hermes", trab]) == 0

    nomes = _bundle_do(capturado["lanc"].arquivos_externos)
    assert nomes == ["GEMINI.md"]
    assert not os.path.exists(os.path.join(trab, "GEMINI.md"))
    assert not os.path.exists(os.path.join(trab, "CLAUDE.md"))


def test_claude_entrega_claude_md_no_bundle(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    capturado = {}
    monkeypatch.setattr("koine.cli._materializar",
                        lambda lanc, pasta: capturado.update(lanc=lanc))
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)

    assert cli.main(["claude", "hermes", trab]) == 0

    assert _bundle_do(capturado["lanc"].arquivos_externos) == ["CLAUDE.md"]
    assert not os.path.exists(os.path.join(trab, "CLAUDE.md"))


def test_launch_nao_deixa_arquivo_novo_na_pasta(koine_home, monkeypatch):
    """A régua do critério 3 da spec: listagem antes e depois, não a ausência de
    um nome específico — com o nome, o mesmo defeito volta com outro arquivo."""
    monkeypatch.setenv("HOME", koine_home["home"])
    trab = koine_home["trab"]
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)
    antes = sorted(os.listdir(trab))

    for cliente in ("claude", "agy", "codex", "copilot", "opencode"):
        assert cli.main([cliente, "hermes", trab]) == 0
        assert sorted(os.listdir(trab)) == antes, f"{cliente} sujou a pasta"
