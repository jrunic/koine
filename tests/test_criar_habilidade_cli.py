import os

from koine import cli, skills


def _home_isolada(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: home))
    return home


def test_criar_habilidade_grava_e_distribui_para_harness_detectado(
        tmp_path, monkeypatch, capsys):
    home = _home_isolada(tmp_path, monkeypatch)
    corpo = tmp_path / "corpo.md"
    corpo.write_text("Passo 1. Passo 2.")
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: ["claude"])

    codigo = cli.main(["criar-habilidade", "organiza-inbox",
                       "--descricao", "Organiza o inbox do Gmail",
                       "--corpo", str(corpo)])

    assert codigo == 0
    saida = capsys.readouterr().out
    assert "organiza-inbox" in saida
    assert "claude" in saida
    destino = home / ".claude" / "skills" / "organiza-inbox" / "SKILL.md"
    assert destino.exists()
    assert "Passo 1. Passo 2." in destino.read_text()


def test_criar_habilidade_recusa_nome_reservado(tmp_path, monkeypatch, capsys):
    _home_isolada(tmp_path, monkeypatch)
    corpo = tmp_path / "corpo.md"
    corpo.write_text("corpo")
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: [])

    codigo = cli.main(["criar-habilidade", "kn-05-outro-nome",
                       "--descricao", "descrição",
                       "--corpo", str(corpo)])

    assert codigo == 1
    assert "reservado" in capsys.readouterr().err.lower()


def test_criar_habilidade_sem_harness_detectado_ainda_grava_o_canonico(
        tmp_path, monkeypatch, capsys):
    _home_isolada(tmp_path, monkeypatch)
    corpo = tmp_path / "corpo.md"
    corpo.write_text("corpo")
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: [])

    codigo = cli.main(["criar-habilidade", "organiza-inbox",
                       "--descricao", "descrição",
                       "--corpo", str(corpo)])

    assert codigo == 0
    from koine import paths
    destino = os.path.join(paths.config_dir(), "habilidades",
                           "organiza-inbox", "SKILL.md")
    assert os.path.exists(destino)
