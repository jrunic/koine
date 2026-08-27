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


import os
import time

from koine import ficha


def _pasta(tmp_path, conteudo=BASE):
    p = tmp_path / "CONTEXTO.md"
    p.write_text(conteudo, encoding="utf-8", newline="")
    return str(p)


def test_grava_no_arquivo_e_faz_backup(tmp_path):
    path = _pasta(tmp_path)
    assert ficha.definir_campo_arquivo(path, "agente", "leia") is True
    assert frontmatter.ler(open(path).read())[0]["agente"] == "leia"
    assert os.path.exists(path + ".bak"), "o conteúdo anterior tem que sobrar"
    assert "agente:" not in open(path + ".bak").read()


def test_mesmo_valor_nao_toca_o_arquivo(tmp_path):
    """Pasta de usuário pode estar em git ou sincronizada: reescrever a cada
    launch sujaria a árvore. mtime E conteúdo, não só conteúdo."""
    path = _pasta(tmp_path)
    ficha.definir_campo_arquivo(path, "agente", "leia")
    antes_bytes = open(path, "rb").read()
    antes_mtime = os.stat(path).st_mtime_ns
    time.sleep(0.01)

    assert ficha.definir_campo_arquivo(path, "agente", "leia") is False

    assert open(path, "rb").read() == antes_bytes
    assert os.stat(path).st_mtime_ns == antes_mtime
    assert not os.path.exists(path + ".bak.1"), "no-op não gera backup novo"


def test_recusa_arquivo_sem_ficha(tmp_path):
    path = _pasta(tmp_path, "# sem frontmatter\n")
    assert ficha.definir_campo_arquivo(path, "agente", "leia") is False
    assert open(path).read() == "# sem frontmatter\n"


def test_recusa_symlink(tmp_path):
    """Escrita através de symlink alcança o alvo — mesma proteção do normalizar."""
    real = tmp_path / "real.md"
    real.write_text(BASE, encoding="utf-8")
    link = tmp_path / "CONTEXTO.md"
    os.symlink(str(real), str(link))
    assert ficha.definir_campo_arquivo(str(link), "agente", "leia") is False
    assert "agente:" not in real.read_text()
