import os
import pytest
from koine import pasta


def test_resolver_vazio_e_pwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert pasta.resolver("") == os.getcwd()


def test_resolver_path_direto(tmp_path):
    d = tmp_path / "sub"; d.mkdir()
    assert pasta.resolver(str(d)) == os.path.abspath(str(d))


def test_resolver_alias(tmp_path, monkeypatch):
    home = str(tmp_path); monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    from koine import aliases
    os.makedirs(os.path.join(home, "koine"))
    aliases.adicionar("koine", "koine", "home")     # ~/koine
    assert pasta.resolver("koine") == os.path.join(home, "koine")


def test_resolver_nao_encontrado_erra_deferido(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    with pytest.raises(pasta.ResolucaoInterativaRequerida):
        pasta.resolver("nao-existe-como-alias-nem-path")
