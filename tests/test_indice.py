import os

from koine import indice

REF_VALIDA = """---
title: Ref boa
description: Uma nota qualquer
dominios: [tecnologia]
---

# Corpo
"""

# Dois-pontos sem aspas: YAML inválido, mas reparável (bug reportado em produção). Desde a
# v0.5.2 a referência entra no índice em vez de sumir dele.
REF_REPARAVEL = """---
title: Ref com dois-pontos
description: Ferramenta instalada e funcional: gog v0.34.1, projeto x
dominios: [tecnologia]
---

# Corpo
"""

# TAB no lugar de espaço: nem o reparo salva — warn-and-skip (6a79dc3).
REF_QUEBRADA = """---
title: Ref ruim
dominios:
\t- tecnologia
---

# Corpo
"""


def test_frontmatter_reparavel_entra_no_indice(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    refs = tmp_path / "refs"
    refs.mkdir()
    (refs / "boa.md").write_text(REF_VALIDA, encoding="utf-8")
    (refs / "reparavel.md").write_text(REF_REPARAVEL, encoding="utf-8")

    indice.gerar(str(refs), ["tecnologia"])

    idx = (refs / "kn-indice-tecnologia.md").read_text(encoding="utf-8")
    assert "`boa.md`" in idx
    assert "`reparavel.md`" in idx
    # a description reparada foi lida inteira, com o dois-pontos preservado
    assert "gog v0.34.1" in idx
    # mas avisou que o arquivo merece aspas
    assert "reparavel.md" in capsys.readouterr().err


def test_frontmatter_irreparavel_nao_derruba_o_indice(tmp_path, monkeypatch, capsys):
    # HOME isolado → config_dir vazio → sinopse cai no fallback, sem crash.
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    refs = tmp_path / "refs"
    refs.mkdir()
    (refs / "boa.md").write_text(REF_VALIDA, encoding="utf-8")
    (refs / "ruim.md").write_text(REF_QUEBRADA, encoding="utf-8")

    # Não lança, mesmo com o arquivo malformado no meio do walk.
    indice.gerar(str(refs), ["tecnologia"])

    # A referência válida foi catalogada; a quebrada foi ignorada.
    idx = (refs / "kn-indice-tecnologia.md").read_text(encoding="utf-8")
    assert "`boa.md`" in idx
    assert "`ruim.md`" not in idx

    # Avisou qual arquivo corrigir, no stderr.
    err = capsys.readouterr().err
    assert "ruim.md" in err
    assert "frontmatter inválido" in err


def test_indice_gerado_tem_frontmatter_valido_com_dominio_exotico(
        tmp_path, monkeypatch):
    """O nome do domínio vem da lista do usuário: `dominios: ["vendas: b2b"]`
    é YAML válido e fazia o Koine gravar `dominio: vendas: b2b` — inválido —
    dentro de um arquivo gerado por ele mesmo."""
    from koine import frontmatter
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    refs = tmp_path / "refs"
    refs.mkdir()

    indice.gerar(str(refs), ["vendas: b2b"])

    gerado = next(p for p in os.listdir(str(refs)) if p.startswith("kn-indice-"))
    fm, reparos, _ = frontmatter.analisar(
        open(os.path.join(str(refs), gerado), encoding="utf-8").read())
    assert reparos == []          # o Koine não escreve YAML que precise de reparo
    assert fm["dominio"] == "vendas: b2b"
    assert fm["entradas"] == 0
