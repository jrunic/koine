import os
import pathlib

from koine import backup


def test_caminho_livre_devolve_o_base_quando_nao_existe(tmp_path):
    base = str(tmp_path / "SKILL.md.bak")
    assert backup.caminho_livre(base) == base


def test_caminho_livre_numera_a_partir_do_1(tmp_path):
    base = str(tmp_path / "SKILL.md.bak")
    pathlib.Path(base).write_text("primeiro")
    assert backup.caminho_livre(base) == base + ".1"
    pathlib.Path(base + ".1").write_text("segundo")
    assert backup.caminho_livre(base) == base + ".2"


def test_caminho_livre_ve_symlink_quebrado(tmp_path):
    """lexists, não exists: symlink apontando para o nada OCUPA o nome, e
    gravar por cima dele escreveria no destino inexistente."""
    base = str(tmp_path / "SKILL.md.bak")
    os.symlink(str(tmp_path / "nao-existe"), base)
    assert backup.caminho_livre(base) == base + ".1"
