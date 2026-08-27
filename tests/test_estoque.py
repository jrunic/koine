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


# ---- limpeza no launch -----------------------------------------------------

def _pasta(koine_home):
    return koine_home["trab"]


def test_launch_remove_o_arquivo_do_mecanismo_antigo(koine_home, monkeypatch):
    """Critério 6, e a régua do critério 3: a listagem da pasta ao final é a
    inicial MENOS os removíveis."""
    import pathlib

    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta(koine_home)
    pathlib.Path(pasta, "CLAUDE.md").write_text(MARCADOR + "\n@/caminho\n")
    meu = pathlib.Path(pasta, "notas.md")
    meu.write_text("minhas notas\n")
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude", "hermes", pasta]) == 0

    assert not pathlib.Path(pasta, "CLAUDE.md").exists()
    assert meu.read_text() == "minhas notas\n", "arquivo do usuário foi tocado"
    assert not pathlib.Path(pasta, "CLAUDE.md.bak").exists(), \
        "remoção de arquivo NOSSO não gera .bak — encheria a pasta a cada sessão"


def test_launch_nao_remove_arquivo_sem_marcador(koine_home, monkeypatch):
    import pathlib

    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta(koine_home)
    meu = pathlib.Path(pasta, "CLAUDE.md")
    meu.write_text("# instruções minhas, escritas à mão\n")
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude", "hermes", pasta]) == 0
    assert meu.read_text() == "# instruções minhas, escritas à mão\n"


def test_launch_nao_remove_o_que_o_gerar_materializou(koine_home, monkeypatch):
    """Critério 6a com os dois na MESMA pasta: gerar a pedido, lançar, e o
    arquivo continuar lá."""
    import pathlib

    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta(koine_home)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["gerar", "hermes", pasta]) == 0
    assert cli.main(["claude", "hermes", pasta]) == 0

    assert pathlib.Path(pasta, "CLAUDE.md").exists(), \
        "o launch apagou o que o usuário mandou gerar"


def test_symlink_e_reconhecido_por_caminho_E_alvo(koine_home):
    """A primeira versão da regra casava só pelo alvo — e removeria qualquer
    atalho do usuário apontando para o CONTEXTO.md."""
    import pathlib
    pasta = _pasta(koine_home)
    ctx = os.path.join(pasta, "CONTEXTO.md")

    nosso = pathlib.Path(pasta, "AGENTS.md")
    os.symlink(ctx, nosso)                  # caminho nosso + alvo nosso
    atalho = pathlib.Path(pasta, "notas.md")
    os.symlink(ctx, atalho)                 # alvo igual, caminho do usuário

    assert estoque.removivel_symlink(str(nosso), pasta) is True
    assert estoque.removivel_symlink(str(atalho), pasta) is False


def test_symlink_no_caminho_nosso_com_alvo_diferente_nao_e_removido(koine_home):
    """Mesmo caminho, alvo diferente: é do usuário."""
    import pathlib
    pasta = _pasta(koine_home)
    outro_alvo = pathlib.Path(pasta, "padroes.md")
    outro_alvo.write_text("x\n")
    link = pathlib.Path(pasta, "AGENTS.md")
    os.symlink(str(outro_alvo), link)

    assert estoque.removivel_symlink(str(link), pasta) is False


def test_launch_remove_o_symlink_do_mecanismo_antigo(koine_home, monkeypatch):
    import pathlib

    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta(koine_home)
    ctx = os.path.join(pasta, "CONTEXTO.md")
    link = pathlib.Path(pasta, ".github", "copilot-instructions.md")
    link.parent.mkdir()
    os.symlink(ctx, link)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["copilot", "hermes", pasta]) == 0

    assert not os.path.lexists(link)
    assert os.path.exists(ctx), "o alvo nunca é tocado: some o link, fica o arquivo"


def test_segunda_rodada_nao_remove_nada(koine_home, monkeypatch):
    """Critério 8: no-op. E prova de que o comando rodou de verdade."""
    import pathlib

    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta(koine_home)
    pathlib.Path(pasta, "CLAUDE.md").write_text(MARCADOR + "\n@/caminho\n")
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude", "hermes", pasta]) == 0
    depois_da_primeira = sorted(os.listdir(pasta))
    assert "CLAUDE.md" not in depois_da_primeira  # a primeira REMOVEU

    assert cli.main(["claude", "hermes", pasta]) == 0
    assert sorted(os.listdir(pasta)) == depois_da_primeira


def test_symlink_para_arquivo_nosso_fora_da_pasta_nao_e_removido(koine_home):
    """Atalho do usuário, no nosso nome, apontando para um arquivo que por acaso
    tem o nosso marcador — um gerado antigo guardado noutro lugar.

    Sem o guard de symlink em `removivel`, a leitura ATRAVESSA o link, encontra
    o marcador no alvo e remove o atalho do usuário. Mutação que a suíte não
    pegava até este teste existir."""
    import pathlib
    pasta = _pasta(koine_home)
    guardado = pathlib.Path(koine_home["home"], "copia-antiga.md")
    guardado.write_text(MARCADOR + "\n# CLAUDE.md\n")
    link = pathlib.Path(pasta, "AGENTS.md")
    os.symlink(str(guardado), link)

    assert estoque.removivel(str(link)) is False
    assert estoque.removivel_symlink(str(link), pasta) is False
    assert estoque.limpar(pasta) == []
    assert os.path.lexists(link)
