import os

from koine import instantaneo, paths

FICHA = "---\nescopo: projeto-x\ndominios: [tecnologia]\n---"


def test_guarda_e_devolve_a_ficha(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    pasta = str(tmp_path / "trab")

    instantaneo.guardar(pasta, FICHA)
    foto = instantaneo.recuperar(pasta)

    assert foto is not None
    assert foto.bloco == FICHA
    assert foto.quando, "sem a data o aviso não tem como dizer de quando é"


def test_a_foto_e_por_pasta(tmp_path, monkeypatch):
    """Com uma pasta só, uma implementação que guardasse foto GLOBAL passaria.
    Duas pastas com fichas diferentes é o que discrimina."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")

    instantaneo.guardar(a, "---\nescopo: alfa\n---")
    instantaneo.guardar(b, "---\nescopo: beta\n---")

    assert "alfa" in instantaneo.recuperar(a).bloco
    assert "beta" in instantaneo.recuperar(b).bloco


def test_sem_foto_devolve_none(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    assert instantaneo.recuperar(str(tmp_path / "nunca-vista")) is None


def test_guardar_de_novo_substitui_sem_acumular(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    pasta = str(tmp_path / "trab")

    instantaneo.guardar(pasta, "---\nescopo: velho\n---")
    instantaneo.guardar(pasta, "---\nescopo: novo\n---")

    assert "novo" in instantaneo.recuperar(pasta).bloco
    base = os.path.join(paths.cache_dir(), "fichas")
    assert len(os.listdir(base)) == 1, "uma foto por pasta, não um histórico"


def test_guardar_nunca_derruba_a_sessao(tmp_path, monkeypatch):
    """Fotografar é serviço, não requisito: erro vira silêncio."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    # patch estreito: `instantaneo.os` é o MESMO objeto módulo que todo mundo
    # importa — mexer nele quebraria qualquer outra chamada do teste.
    sem_permissao = tmp_path / "trancado"
    sem_permissao.mkdir()
    os.chmod(sem_permissao, 0o000)
    monkeypatch.setattr(instantaneo, "_caminho",
                        lambda p: str(sem_permissao / "sub" / "f.json"))
    try:
        instantaneo.guardar(str(tmp_path / "trab"), FICHA)   # não levanta
    finally:
        os.chmod(sem_permissao, 0o755)
