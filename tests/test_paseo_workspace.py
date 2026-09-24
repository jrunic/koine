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


def _costura_rodar(monkeypatch, respostas: dict):
    """respostas: {tuple(args): resultado}. args casado pelo prefixo."""
    chamadas = []

    def fake(args, **k):
        chamadas.append(list(args))
        for prefixo, resultado in respostas.items():
            if list(args)[:len(prefixo)] == list(prefixo):
                return resultado
        raise AssertionError(f"chamada não esperada: {args}")
    monkeypatch.setattr(pw, "_rodar", fake)
    return chamadas


def test_garantir_estado_nada_existe_cria_os_dois(monkeypatch):
    chamadas = _costura_rodar(monkeypatch, {
        ("project", "ls"): [],
        ("project", "create"): {"projectId": "prj_1", "name": "koine",
                                "kind": "non_git", "path": "/x/koine"},
        ("project", "rename"): {"projectId": "prj_1", "name": "Koine"},
        ("workspace", "create"): {"workspaceId": "wks_1", "project": "Koine",
                                  "name": "Manter Koine", "isolation": "local",
                                  "cwd": "/x/koine"},
    })
    r = pw.garantir("/x/koine", titulo="Koine")
    assert r == {"projectId": "prj_1", "workspaceId": "wks_1", "acao": "criado"}
    # não consultou workspace ls: projeto acabou de nascer, não pode ter workspace
    assert not any(c[:2] == ["workspace", "ls"] for c in chamadas)


def test_garantir_estado_projeto_sem_workspace_so_cria_o_workspace(monkeypatch):
    chamadas = _costura_rodar(monkeypatch, {
        ("project", "ls"): [{"projectId": "prj_1", "name": "Koine",
                             "kind": "non_git", "path": "/x/koine"}],
        ("workspace", "ls"): [],
        ("workspace", "create"): {"workspaceId": "wks_1", "project": "Koine",
                                  "name": "Manter Koine", "isolation": "local",
                                  "cwd": "/x/koine"},
    })
    r = pw.garantir("/x/koine", titulo="Koine")
    assert r["acao"] == "criado"
    assert not any(c[:2] == ["project", "create"] for c in chamadas)


def test_garantir_estado_os_dois_existem_e_no_op(monkeypatch):
    chamadas = _costura_rodar(monkeypatch, {
        ("project", "ls"): [{"projectId": "prj_1", "name": "Koine",
                             "kind": "non_git", "path": "/x/koine"}],
        ("workspace", "ls"): [{"workspaceId": "wks_1", "project": "Koine",
                               "name": "Manter Koine", "isolation": "local",
                               "cwd": "/x/koine"}],
    })
    r = pw.garantir("/x/koine", titulo="Koine")
    assert r == {"projectId": "prj_1", "workspaceId": "wks_1", "acao": "existente"}
    assert not any(c[:2] == ["project", "create"] for c in chamadas)
    assert not any(c[:2] == ["workspace", "create"] for c in chamadas)


def test_garantir_rodar_duas_vezes_e_idempotente(monkeypatch):
    """Critério de sucesso da spec: rodar duas vezes seguidas para a mesma
    pasta é no-op na segunda."""
    respostas = {
        ("project", "ls"): [{"projectId": "prj_1", "name": "Koine",
                             "kind": "non_git", "path": "/x/koine"}],
        ("workspace", "ls"): [{"workspaceId": "wks_1", "project": "Koine",
                               "name": "Manter Koine", "isolation": "local",
                               "cwd": "/x/koine"}],
    }
    _costura_rodar(monkeypatch, respostas)
    primeira = pw.garantir("/x/koine", titulo="Koine")
    _costura_rodar(monkeypatch, respostas)
    segunda = pw.garantir("/x/koine", titulo="Koine")
    assert primeira == segunda == {"projectId": "prj_1", "workspaceId": "wks_1",
                                   "acao": "existente"}


def test_garantir_com_projeto_nome_pendura_workspace_em_projeto_existente(monkeypatch):
    """Achado da revisão dev-10 do PLANO, 22/09/2026: projeto agrupa
    pastas — a /kn-14 passa `projeto_nome` para pendurar a pasta nova num
    projeto que já existe (casado por NOME, não pelo path desta pasta)."""
    chamadas = _costura_rodar(monkeypatch, {
        ("project", "ls"): [{"projectId": "prj_1", "name": "Grupo Aldo",
                             "kind": "non_git", "path": "/x/aldo-a"}],
        ("workspace", "ls"): [],
        ("workspace", "create"): {"workspaceId": "wks_2", "project": "Grupo Aldo",
                                  "name": "Aldo B", "isolation": "local",
                                  "cwd": "/x/aldo-b"},
    })
    r = pw.garantir("/x/aldo-b", projeto_nome="Grupo Aldo")
    assert r == {"projectId": "prj_1", "workspaceId": "wks_2", "acao": "criado"}
    assert not any(c[:2] == ["project", "create"] for c in chamadas)
    assert not any(c[:2] == ["project", "rename"] for c in chamadas)


def test_garantir_com_projeto_nome_ausente_cria_o_projeto_com_esse_nome(monkeypatch):
    chamadas = _costura_rodar(monkeypatch, {
        ("project", "ls"): [],
        ("project", "create"): {"projectId": "prj_9", "name": "aldo-c",
                                "kind": "non_git", "path": "/x/aldo-c"},
        ("project", "rename"): {"projectId": "prj_9", "name": "Grupo Aldo Novo"},
        ("workspace", "create"): {"workspaceId": "wks_9", "project": "Grupo Aldo Novo",
                                  "name": "aldo-c", "isolation": "local",
                                  "cwd": "/x/aldo-c"},
    })
    r = pw.garantir("/x/aldo-c", projeto_nome="Grupo Aldo Novo")
    assert r["acao"] == "criado"
    renomeou = [c for c in chamadas if c[:2] == ["project", "rename"]]
    assert renomeou and renomeou[0][3] == "Grupo Aldo Novo"


def test_garantir_levanta_paseo_indisponivel_quando_project_ls_falha(monkeypatch):
    monkeypatch.setattr(pw, "_rodar", lambda *a, **k: None)
    import pytest
    with pytest.raises(pw.PaseoIndisponivel):
        pw.garantir("/x/koine", titulo="Koine")


def test_garantir_levanta_paseo_indisponivel_quando_workspace_create_falha(monkeypatch):
    def fake(args, **k):
        if list(args)[:2] == ["project", "ls"]:
            return [{"projectId": "prj_1", "name": "Koine", "kind": "non_git",
                     "path": "/x/koine"}]
        if list(args)[:2] == ["workspace", "ls"]:
            return []
        return None  # workspace create falha (daemon caiu no meio)
    monkeypatch.setattr(pw, "_rodar", fake)
    import pytest
    with pytest.raises(pw.PaseoIndisponivel):
        pw.garantir("/x/koine", titulo="Koine")
