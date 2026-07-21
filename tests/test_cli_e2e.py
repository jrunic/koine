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


def test_atualizar_falha_rede_retorna_1(monkeypatch):
    from koine import cli, atualizar
    def boom(force=False):
        raise atualizar.AtualizarErro("sem rede")
    monkeypatch.setattr(atualizar, "preparar", boom)
    assert cli.main(["atualizar"]) == 1


def test_atualizar_windows_finaliza_com_codigo_atual(monkeypatch, tmp_path):
    """No Windows o finalizador roda uma CÓPIA do pyz atual (tem --finalizar), não
    o pyz alvo baixado (que pode não ter, ex.: downgrade p/ 0.4.2 sem 'atualizar')."""
    import os
    from koine import cli, atualizar
    staging = str(tmp_path / "stg"); os.makedirs(staging)
    alvo = str(tmp_path / "dist" / "koine.pyz")
    os.makedirs(os.path.dirname(alvo)); open(alvo, "w").write("PYZ-ATUAL")

    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(atualizar, "preparar", lambda force=False: (staging, "0.4.2"))
    monkeypatch.setattr(cli, "_pyz_padrao", lambda: alvo)
    monkeypatch.setattr(cli, "_bin_padrao", lambda: str(tmp_path / "bin"))
    monkeypatch.setattr(cli.paths, "cache_dir", lambda: str(tmp_path / "cache"))

    cap = {}

    class FakePopen:
        def __init__(self, args, **kw):
            cap["pyz"] = args[1]

    monkeypatch.setattr(cli.subprocess, "Popen", FakePopen)

    assert cli.main(["atualizar"]) == 0
    assert os.path.basename(cap["pyz"]) == "finalizador.pyz"
    assert open(cap["pyz"]).read() == "PYZ-ATUAL"  # cópia do atual, não o alvo
