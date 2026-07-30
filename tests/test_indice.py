import os

from koine import indice

REF_VALIDA = """---
title: Ref boa
description: Uma nota qualquer
dominios: [tecnologia]
---

# Corpo
"""

# Frontmatter inválido: valor não-citado com ": " no meio vira mapping YAML.
# É o que a kn-11 produz quando a description tem dois-pontos sem aspas.
REF_QUEBRADA = """---
title: Ref ruim
description: Ferramenta instalada e funcional: gog v0.34.1, projeto x
dominios: [tecnologia]
---

# Corpo
"""


def test_frontmatter_invalido_nao_derruba_o_indice(tmp_path, monkeypatch, capsys):
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
