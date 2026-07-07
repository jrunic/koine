import os
from koine import paths


def test_vault_dir_respeita_xdg(monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", "/x/data")
    assert paths.vault_dir() == os.path.join("/x/data", "koine")


def test_vault_dir_fallback_home(monkeypatch):
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", "/h")
    assert paths.vault_dir() == os.path.join("/h", ".local", "share", "koine")


def test_config_dir_fallback_home(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", "/h")
    assert paths.config_dir() == os.path.join("/h", ".config", "koine")


def test_tagged_home(monkeypatch):
    monkeypatch.setenv("HOME", "/h")
    assert paths.resolver_tagged("home:refs") == os.path.join("/h", "refs")


def test_tagged_sem_prefixo_e_erro():
    import pytest
    with pytest.raises(ValueError):
        paths.resolver_tagged("refs")
