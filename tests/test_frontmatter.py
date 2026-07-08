from koine import frontmatter

DOC = '''---
title: "Ref A"
description: "Nota com dois-pontos: exemplo e travessão — real"
dominios: [tecnologia]
plataforma: "*"
---

# Corpo
Texto.
'''


def test_le_campos_incluindo_exoticos():
    fm, corpo = frontmatter.ler(DOC)
    assert fm["title"] == "Ref A"
    assert fm["plataforma"] == "*"
    assert "dois-pontos" in fm["description"]
    assert fm["dominios"] == ["tecnologia"]
    assert corpo.startswith("# Corpo")


def test_sem_frontmatter_devolve_vazio():
    fm, corpo = frontmatter.ler("# Só corpo\n")
    assert fm == {}
    assert corpo == "# Só corpo\n"
