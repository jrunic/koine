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
