import os

from koine import contexto


def test_resolve_bootstrap(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    # cria uma pasta com CONTEXTO bootstrap
    pasta = os.path.join(koine_home["home"], "canonica")
    os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(pasta, "CONTEXTO.md"), "w") as f:
        f.write("---\nbootstrap: true\n---\n\n# Bootstrap\n")
    cm = contexto.resolver("hermes", pasta)
    assert cm.bootstrap is True
    assert cm.koine_path.endswith("/KOINE.md")
    assert cm.agente_path.endswith("/agentes/hermes.md")
    assert cm.contexto_path.endswith("/CONTEXTO.md")
    assert cm.escopo_path == ""          # sem escopo em bootstrap
    assert cm.indice_paths == []          # sem índices
    # a fixture tem 1 arquivo de usuário → usuario_path preenchido
    assert cm.usuario_path.endswith("/teste.md")


def test_resolve_monta_paths(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    cm = contexto.resolver("hermes", koine_home["trab"])
    assert cm.usuario_path.endswith("/teste.md")
    assert cm.koine_path.endswith("/KOINE.md")
    assert cm.agente_path.endswith("/agentes/hermes.md")
    assert cm.escopo_path.endswith("/escopos/fixture.md")
    assert cm.contexto_path.endswith("/CONTEXTO.md")
    # um índice por domínio declarado, na pasta-referências
    assert any(p.endswith("kn-indice-tecnologia.md") for p in cm.indice_paths)
