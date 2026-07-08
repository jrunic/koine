import os
import stat
from koine import wrappers


def test_gera_um_wrapper_por_adapter_registrado(tmp_path):
    bindir = str(tmp_path / "bin")
    pyz = "/opt/koine/koine.pyz"
    criados = wrappers.gerar(bindir, pyz)
    # P1: só claude no REGISTRY → só kn-claude
    assert criados == [os.path.join(bindir, "kn-claude")]


def test_wrapper_unix_usa_python3_e_e_executavel(tmp_path, monkeypatch):
    # Unix usa python3: /usr/bin/python não existe no macOS moderno (Apple
    # removeu em 12.3); só python3. Verificado empiricamente nesta sessão.
    monkeypatch.setattr(wrappers, "_is_windows", lambda: False)
    bindir = str(tmp_path / "bin")
    pyz = "/opt/koine/koine.pyz"
    (caminho,) = wrappers.gerar(bindir, pyz)
    conteudo = open(caminho).read()
    assert conteudo.startswith("#!/usr/bin/env bash")
    assert f'exec python3 "{pyz}" claude "$@"' in conteudo
    assert os.stat(caminho).st_mode & stat.S_IXUSR  # bit de execução


def test_wrapper_windows_bat_usa_python(tmp_path, monkeypatch):
    # Windows usa python: é o nome que a TI do Aldo instalou (gate provou
    # `python hello.py`). Não herda o python3 do Unix.
    monkeypatch.setattr(wrappers, "_is_windows", lambda: True)
    bindir = str(tmp_path / "bin")
    (caminho,) = wrappers.gerar(bindir, r"C:\koine\koine.pyz")
    assert caminho.endswith("kn-claude.bat")
    assert 'python "C:\\koine\\koine.pyz" claude %*' in open(caminho).read()
