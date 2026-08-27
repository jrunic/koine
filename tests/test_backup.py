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


from koine import paths


def test_guardar_arquivo_copia_para_a_arvore_de_backups(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    origem = tmp_path / "SKILL.md"
    origem.write_text("conteudo do usuario")

    destino = backup.guardar(str(origem), "0.7.0", "vault", "habilidades/kn-99/SKILL.md")

    assert open(destino).read() == "conteudo do usuario"
    assert origem.exists(), "o original NÃO é movido — cópia, para nunca ficar órfão"
    esperado = os.path.join(paths.cache_dir(), "backups", "0.7.0",
                            "vault", "habilidades", "kn-99", "SKILL.md")
    assert destino == esperado


def test_guardar_diretorio_copia_a_arvore(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    origem = tmp_path / "kn-99-encerra-sessao"
    origem.mkdir()
    (origem / "SKILL.md").write_text("velha")

    destino = backup.guardar(str(origem), "0.7.0", "harness/claude", "kn-99-encerra-sessao")

    assert open(os.path.join(destino, "SKILL.md")).read() == "velha"
    assert origem.is_dir()


def test_guardar_duas_vezes_nao_destroi_o_primeiro(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    origem = tmp_path / "SKILL.md"
    origem.write_text("primeira versao")
    um = backup.guardar(str(origem), "0.7.0", "vault", "habilidades/kn-99/SKILL.md")
    origem.write_text("segunda versao")
    dois = backup.guardar(str(origem), "0.7.0", "vault", "habilidades/kn-99/SKILL.md")

    assert um != dois
    assert open(um).read() == "primeira versao"
    assert open(dois).read() == "segunda versao"
