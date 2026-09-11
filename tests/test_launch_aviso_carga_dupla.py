"""O aviso de carga dupla, e as três formas de não avisar.

A pasta não recebe arquivo gerado desde a v0.7.0 — mas o `koine gerar` escreve,
com a marca `a pedido`, e a limpeza preserva quem a tem por desenho. O resultado
é a sessão carregando o bundle atual MAIS o snapshot parado (medido em
10/09/2026: 122 KB de cada lado).

O aviso não pode disparar sobre a forma `@path` que a `/kn-12-prepara-contexto`
escreve: lá o arquivo da pasta é a ÚNICA via de entrega do modo skills, e carrega
a mesma marca. Mandar o usuário remover aquilo quebraria as sessões dele.
"""
import os

from koine import cli, escrita

SNAPSHOT_INLINE = """<!-- gerado por kn-agente -->
<!-- gerado a pedido -->
# Sessão Koine — Claude

## Usuário

corpo
"""

FORMA_ATPATH = """<!-- gerado por kn-agente -->
<!-- gerado a pedido -->
# CLAUDE.md
*Gerado por kn-agente. Não editar.*

@/Users/alguem/.config/koine/usuario.md
"""

DO_USUARIO = """# CLAUDE.md

Minhas anotações.
"""


def test_snapshot_inline_e_reconhecido(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text(SNAPSHOT_INLINE, encoding="utf-8")

    assert escrita.e_snapshot_inline(str(p)) is True


def test_forma_atpath_do_modo_skills_nao_e_snapshot(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text(FORMA_ATPATH, encoding="utf-8")

    assert escrita.e_snapshot_inline(str(p)) is False


def test_arquivo_do_usuario_nao_e_snapshot(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text(DO_USUARIO, encoding="utf-8")

    assert escrita.e_snapshot_inline(str(p)) is False


def test_arquivo_ausente_nao_e_snapshot(tmp_path):
    assert escrita.e_snapshot_inline(str(tmp_path / "nao-existe.md")) is False


def _pasta_com(tmp_path, nome, conteudo):
    pasta = tmp_path / "trab"
    pasta.mkdir(exist_ok=True)
    alvo = pasta / nome
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(conteudo, encoding="utf-8")
    return str(pasta)


def test_avisa_quando_a_pasta_tem_snapshot_do_cliente(tmp_path, capsys):
    pasta = _pasta_com(tmp_path, "CLAUDE.md", SNAPSHOT_INLINE)

    cli.avisar_carga_dupla("claude", pasta)

    assert "CLAUDE.md" in capsys.readouterr().err


def test_nao_avisa_sobre_arquivo_de_outro_cliente(tmp_path, capsys):
    pasta = _pasta_com(tmp_path, "CLAUDE.md", SNAPSHOT_INLINE)

    cli.avisar_carga_dupla("opencode", pasta)

    assert capsys.readouterr().err == ""


def test_nao_avisa_sobre_a_forma_atpath(tmp_path, capsys):
    pasta = _pasta_com(tmp_path, "CLAUDE.md", FORMA_ATPATH)

    cli.avisar_carga_dupla("claude", pasta)

    assert capsys.readouterr().err == ""


def test_nao_avisa_em_pasta_limpa(tmp_path, capsys):
    pasta = str(tmp_path / "vazia")
    os.makedirs(pasta)

    cli.avisar_carga_dupla("claude", pasta)

    assert capsys.readouterr().err == ""
