from koine import contexto


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
