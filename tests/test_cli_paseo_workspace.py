from koine import cli, paseo_workspace as pw


def test_cli_paseo_workspace_chama_garantir_e_imprime(monkeypatch, capsys, tmp_path):
    chamadas = {}

    def fake_garantir(pasta, titulo="", projeto_nome=""):
        chamadas["pasta"] = pasta
        chamadas["titulo"] = titulo
        chamadas["projeto_nome"] = projeto_nome
        return {"projectId": "prj_1", "workspaceId": "wks_1", "acao": "criado"}
    monkeypatch.setattr(pw, "garantir", fake_garantir)

    rc = cli.main(["paseo-workspace", str(tmp_path), "--titulo", "Koine"])

    assert rc == 0
    assert chamadas == {"pasta": str(tmp_path), "titulo": "Koine", "projeto_nome": ""}
    saida = capsys.readouterr().out
    assert "wks_1" in saida


def test_cli_paseo_workspace_sem_titulo_usa_string_vazia(monkeypatch, tmp_path):
    chamadas = {}
    monkeypatch.setattr(
        pw, "garantir",
        lambda pasta, titulo="", projeto_nome="": chamadas.update(titulo=titulo) or
        {"projectId": "p", "workspaceId": "w", "acao": "existente"})

    cli.main(["paseo-workspace", str(tmp_path)])

    assert chamadas["titulo"] == ""


def test_cli_paseo_workspace_repassa_flag_projeto(monkeypatch, tmp_path):
    chamadas = {}
    monkeypatch.setattr(
        pw, "garantir",
        lambda pasta, titulo="", projeto_nome="":
            chamadas.update(projeto_nome=projeto_nome) or
            {"projectId": "p", "workspaceId": "w", "acao": "criado"})

    cli.main(["paseo-workspace", str(tmp_path), "--projeto", "Grupo Aldo"])

    assert chamadas["projeto_nome"] == "Grupo Aldo"


def test_cli_paseo_workspace_reporta_paseo_indisponivel_sem_traceback(
        monkeypatch, capsys, tmp_path):
    """Achado da revisão dev-10 do plano, 22/09/2026: `garantir()` levanta
    `PaseoIndisponivel` — o comando captura e imprime prosa, nunca deixa o
    traceback cru chegar ao usuário."""
    def fake_garantir(pasta, titulo="", projeto_nome=""):
        raise pw.PaseoIndisponivel("paseo project ls falhou")
    monkeypatch.setattr(pw, "garantir", fake_garantir)

    rc = cli.main(["paseo-workspace", str(tmp_path)])

    assert rc == 1
    erro = capsys.readouterr().err
    assert "paseo project ls falhou" in erro
    assert "Traceback" not in erro
