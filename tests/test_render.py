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


IDX_UNIVERSAL = """---
tipo: indice
dominio: universal
entradas: 2
---

## Domínio

Sinopse de universal.
## Entradas catalogadas no escopo

- `compartilhada.md` — vale para os dois
- `so-universal.md` — só aqui
"""

IDX_TECNOLOGIA = """---
tipo: indice
dominio: tecnologia
entradas: 2
---

## Domínio

Sinopse de tecnologia.
## Entradas catalogadas no escopo

- `compartilhada.md` — vale para os dois
- `so-tecnologia.md` — só aqui
"""


def _dois_indices(tmp_path):
    (tmp_path / "kn-indice-universal.md").write_text(IDX_UNIVERSAL, encoding="utf-8")
    (tmp_path / "kn-indice-tecnologia.md").write_text(IDX_TECNOLOGIA, encoding="utf-8")
    return [str(tmp_path / "kn-indice-universal.md"),
            str(tmp_path / "kn-indice-tecnologia.md")]


def test_secoes_entrada_repetida_e_descrita_uma_vez(tmp_path):
    partes = render.secoes_de_indice(_dois_indices(tmp_path))
    corpo = "\n".join(p.conteudo for p in partes)

    assert corpo.count("— vale para os dois") == 1


def test_secoes_entrada_repetida_ganha_referencia_cruzada(tmp_path):
    partes = render.secoes_de_indice(_dois_indices(tmp_path))
    tecnologia = [p for p in partes if p.secao.endswith("tecnologia")][0]

    assert "`compartilhada.md`" in tecnologia.conteudo
    assert "universal" in tecnologia.conteudo


def test_secoes_nenhuma_entrada_some(tmp_path):
    partes = render.secoes_de_indice(_dois_indices(tmp_path))
    corpo = "\n".join(p.conteudo for p in partes)

    for ref in ("compartilhada.md", "so-universal.md", "so-tecnologia.md"):
        assert f"`{ref}`" in corpo
    linhas = [l for l in corpo.split("\n") if l.startswith("- `")]
    assert len(linhas) == 4  # 3 descritivas + 1 referência cruzada


def test_secoes_uma_por_indice_com_o_dominio_no_nome(tmp_path):
    partes = render.secoes_de_indice(_dois_indices(tmp_path))

    assert [p.secao for p in partes] == ["Referências — universal",
                                         "Referências — tecnologia"]


def test_secoes_indice_ilegivel_nao_derruba(tmp_path):
    partes = render.secoes_de_indice([str(tmp_path / "nao-existe.md")])

    assert partes == []
