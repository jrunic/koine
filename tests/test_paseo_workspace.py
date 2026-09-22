from koine import paseo_workspace as pw


def test_achar_projeto_casa_por_path_absoluto():
    projetos = [
        {"projectId": "prj_1", "name": "Rotina", "kind": "non_git", "path": "/x/rotina"},
        {"projectId": "prj_2", "name": "Koine", "kind": "non_git", "path": "/x/koine"},
    ]
    achado = pw.achar_projeto("/x/koine", projetos)
    assert achado["projectId"] == "prj_2"


def test_achar_projeto_ausente_devolve_none():
    assert pw.achar_projeto("/x/inexistente", []) is None


def test_achar_workspace_casa_por_projeto_e_cwd():
    """workspace ls --json traz o NOME do projeto, não o id — achado da
    revisão dev-10, 22/09/2026: casar por nome, não por projectId."""
    workspaces = [
        {"workspaceId": "wks_1", "project": "Rotina", "name": "Rotina",
         "isolation": "local", "cwd": "/x/rotina"},
        {"workspaceId": "wks_2", "project": "Koine", "name": "Manter Koine",
         "isolation": "local", "cwd": "/x/koine"},
    ]
    achado = pw.achar_workspace("Koine", "/x/koine", workspaces)
    assert achado["workspaceId"] == "wks_2"


def test_achar_workspace_mesmo_nome_de_projeto_cwd_diferente_nao_casa():
    workspaces = [
        {"workspaceId": "wks_1", "project": "Koine", "name": "Outra pasta",
         "isolation": "local", "cwd": "/x/outra"},
    ]
    assert pw.achar_workspace("Koine", "/x/koine", workspaces) is None


def test_achar_projeto_por_nome_casa_por_name():
    """Achado da revisão dev-10 do PLANO, 22/09/2026: projeto agrupa
    workspaces de pastas diferentes (ex.: "Grupo Aldo" hospeda workspaces de
    duas pastas distintas) — a /kn-14 precisa resolver por NOME, não por
    path de uma pasta só."""
    projetos = [
        {"projectId": "prj_1", "name": "Grupo Aldo", "kind": "non_git",
         "path": "/x/aldo-a"},
    ]
    achado = pw.achar_projeto_por_nome("Grupo Aldo", projetos)
    assert achado["projectId"] == "prj_1"


def test_achar_projeto_por_nome_ausente_devolve_none():
    assert pw.achar_projeto_por_nome("Inexistente", []) is None


import json


def test_rodar_devolve_json_parseado(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel("/usr/local/bin/paseo", "path"))
    saida = json.dumps([{"projectId": "prj_1"}])
    monkeypatch.setattr(
        amb, "executar",
        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": saida})())
    assert pw._rodar(["project", "ls", "--json"]) == [{"projectId": "prj_1"}]


def test_rodar_devolve_none_sem_executavel(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel", lambda n: None)
    assert pw._rodar(["project", "ls", "--json"]) is None


def test_rodar_devolve_none_em_saida_nao_zero(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel("/usr/local/bin/paseo", "path"))
    monkeypatch.setattr(
        amb, "executar",
        lambda *a, **k: type("R", (), {"returncode": 1, "stdout": ""})())
    assert pw._rodar(["project", "ls", "--json"]) is None


def test_rodar_devolve_none_em_json_invalido(monkeypatch):
    from koine import paseo_ambiente as amb
    monkeypatch.setattr(amb, "resolver_executavel",
                        lambda n: amb.Executavel("/usr/local/bin/paseo", "path"))
    monkeypatch.setattr(
        amb, "executar",
        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "não é json"})())
    assert pw._rodar(["project", "ls", "--json"]) is None
