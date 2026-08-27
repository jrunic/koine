from koine import frontmatter

BASE = """---
escopo: projeto-x
dominios: [tecnologia]
---

# Projeto X

Corpo que não pode ser tocado.
"""


def test_acrescenta_campo_preservando_o_resto():
    novo, mudou = frontmatter.definir_campo(BASE, "agente", "leia")
    assert mudou
    # por PARSE, não por substring: o campo tem que estar DENTRO do bloco.
    # `"agente: leia" in novo` ficaria verde com o campo caído no corpo.
    assert frontmatter.ler(novo)[0]["agente"] == "leia"
    assert frontmatter.ler(novo)[0]["escopo"] == "projeto-x"
    assert "dominios: [tecnologia]" in novo
    assert "Corpo que não pode ser tocado." in novo


def test_substitui_valor_existente_sem_duplicar():
    com_campo, _ = frontmatter.definir_campo(BASE, "agente", "leia")
    novo, mudou = frontmatter.definir_campo(com_campo, "agente", "atlas")
    assert mudou
    assert novo.count("agente:") == 1
    assert frontmatter.ler(novo)[0]["agente"] == "atlas"


def test_mesmo_valor_e_no_op_byte_a_byte():
    com_campo, _ = frontmatter.definir_campo(BASE, "agente", "leia")
    novo, mudou = frontmatter.definir_campo(com_campo, "agente", "leia")
    assert not mudou
    assert novo == com_campo


def test_sem_bloco_de_frontmatter_nao_inventa_ficha():
    """Arquivo sem `---` é pasta INCOMPLETO. Criar a ficha aqui seria o Koine
    escrevendo por conta própria — o que a v0.6.1 decidiu não fazer."""
    novo, mudou = frontmatter.definir_campo("# Só um título\n", "agente", "leia")
    assert not mudou
    assert novo == "# Só um título\n"


def test_preserva_crlf_e_comentario():
    texto = "---\r\n# comentário do usuário\r\nescopo: x\r\n---\r\n\r\ncorpo\r\n"
    novo, mudou = frontmatter.definir_campo(texto, "agente", "leia")
    assert mudou
    assert "# comentário do usuário" in novo
    assert frontmatter.ler(novo)[0]["agente"] == "leia"
    assert "\n" not in novo.replace("\r\n", ""), "nenhum LF solto criado"
    assert "\r\r" not in novo, "CR duplicado: o bloco termina com \\r pendurado"
