"""Propriedade e intenção são perguntas diferentes.

A 1ª linha diz que o arquivo é NOSSO — é o marcador congelado, contrato de
detecção com instalações antigas, inclusive as do binário Go. A 2ª diz que ele
foi PEDIDO. Trocar a primeira faria o Koine deixar de reconhecer os próprios
arquivos anteriores e tratá-los como do usuário, enchendo as pastas de .bak.
"""
import os

import pytest

from koine import escrita, estoque

MARCADOR = "<!-- gerado por kn-agente -->"


def test_arquivo_gerado_a_pedido_nao_e_removido_pela_limpeza(tmp_path):
    """Critério 6a: no modo skills a pasta é a ÚNICA via de entrega — não há
    wrapper para configurar ambiente. Um launch na mesma pasta não pode apagar
    o que o usuário mandou gerar."""
    p = tmp_path / "CLAUDE.md"
    p.write_text(MARCADOR + "\n" + escrita.MARCA_A_PEDIDO + "\n# CLAUDE.md\n")
    assert estoque.removivel(str(p)) is False


def test_arquivo_do_mecanismo_antigo_e_removivel(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text(MARCADOR + "\n# CLAUDE.md\n\n@/caminho/absoluto\n")
    assert estoque.removivel(str(p)) is True


def test_arquivo_do_usuario_nunca_e_removivel(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text("# minhas instruções\n")
    assert estoque.removivel(str(p)) is False


def test_propriedade_e_intencao_sao_perguntas_separadas(tmp_path):
    """Um arquivo a pedido continua sendo nosso — sobrescrever não pede .bak."""
    p = tmp_path / "CLAUDE.md"
    p.write_text(MARCADOR + "\n" + escrita.MARCA_A_PEDIDO + "\n# CLAUDE.md\n")
    assert escrita.e_nosso(str(p)) is True
    assert estoque.removivel(str(p)) is False


def test_a_marca_a_pedido_nunca_ocupa_a_primeira_linha(tmp_path):
    """O marcador da 1ª linha é congelado por declaração do repo."""
    conteudo = escrita.marcar_a_pedido(MARCADOR + "\n# CLAUDE.md\n")
    linhas = conteudo.splitlines()
    assert linhas[0] == MARCADOR
    assert linhas[1] == escrita.MARCA_A_PEDIDO


def test_marcar_a_pedido_e_idempotente(tmp_path):
    uma = escrita.marcar_a_pedido(MARCADOR + "\n# CLAUDE.md\n")
    duas = escrita.marcar_a_pedido(uma)
    assert uma == duas


def test_gerar_marca_o_arquivo_como_pedido(koine_home, monkeypatch):
    import pathlib

    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = koine_home["trab"]

    assert cli.main(["gerar", "hermes", pasta]) == 0

    linhas = pathlib.Path(pasta, "CLAUDE.md").read_text().splitlines()
    assert linhas[0] == MARCADOR
    assert linhas[1] == escrita.MARCA_A_PEDIDO
