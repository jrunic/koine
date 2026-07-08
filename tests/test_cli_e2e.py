import os

from koine import cli, conflito


def test_koine_claude_gera_claude_md_e_lanca(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])

    # seam: captura o launch sem substituir o processo (execvpe mataria o pytest)
    capturado = {}
    monkeypatch.setattr("koine.launch.lancar",
                        lambda cliente, pasta, **kw: capturado.update(cliente=cliente, pasta=pasta))
    rc = cli.main(["claude", "hermes", koine_home["trab"]])
    assert rc == 0
    assert capturado == {"cliente": "claude", "pasta": koine_home["trab"]}
    py = open(os.path.join(koine_home["trab"], "CLAUDE.md"), encoding="utf-8").read()
    # formato congelado: marcador na 1ª linha + @path das 4 camadas
    assert py.split("\n", 1)[0] == conflito.MARCADOR_KOINE
    for camada in (
        os.path.join(koine_home["cfg"], "teste.md"),
        os.path.join(koine_home["data"], "KOINE.md"),
        os.path.join(koine_home["data"], "agentes", "hermes.md"),
        os.path.join(koine_home["cfg"], "escopos", "fixture.md"),
    ):
        assert f"@{camada}" in py, f"camada ausente: {camada}"


def test_versao(capsys):
    assert cli.main(["versao"]) == 0
    assert "koine" in capsys.readouterr().out.lower()
