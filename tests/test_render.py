from koine import render


def test_strip_frontmatter():
    casos = [
        ("---\nid: 1\n---\n# Título\nCorpo aqui.", "# Título\nCorpo aqui."),
        ("# Título\nCorpo.", "# Título\nCorpo."),
        ("---\nid: 1\n---\n", ""),
        ("---\nid: 1\ntipo: adr\ntags: [a, b]\n---\n\n# Título\nCorpo.", "\n# Título\nCorpo."),
    ]
    for entrada, want in casos:
        assert render.strip_frontmatter(entrada) == want


def test_demover_h1():
    assert render.demover_h1("# Walter\nConteúdo.") == "## Walter\nConteúdo."
    assert render.demover_h1("## Seção\nConteúdo.") == "## Seção\nConteúdo."


def test_dominio_de():
    assert render.dominio_de("/foo/kn-indice-universal.md") == "universal"


def test_wrapar_instructions():
    out = render.wrapar_instructions("---\nid: 1\n---\n# Título\nCorpo.")
    assert out == '---\napplyTo: "**"\n---\n\n## Título\nCorpo.'


def test_mescar_documentos():
    partes = [render.Parte("Usuário", "---\nid: 1\n---\n# Walter\nBio."),
              render.Parte("Koine", "# Koine\nManual.\n")]
    out = render.mescar_documentos("Sessão Koine — Codex", partes)
    esperado = ("# Sessão Koine — Codex\n\n"
                "## Usuário\n\n## Walter\nBio.\n\n"
                "## Koine\n\n## Koine\nManual.")
    assert out == esperado
