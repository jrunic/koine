import json
import os
from koine import aliases


def test_carregar_ausente_devolve_vazio(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert aliases.carregar() == {"pastas": {}}


def test_adicionar_e_resolver_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    aliases.adicionar("koine", "koine", "home")
    a = aliases.carregar()
    assert a["pastas"]["koine"] == {"path": "koine", "from": "home"}
    assert aliases.resolver(a, "koine") == os.path.join(str(tmp_path), "koine")


def test_resolver_abs_e_ausente(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    a = {"pastas": {"x": {"path": "/abs/x", "from": "abs"}}}
    assert aliases.resolver(a, "x") == "/abs/x"
    assert aliases.resolver(a, "nao-existe") is None


def test_salvar_gera_json_parseavel(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    aliases.adicionar("koine", "koine", "home")
    dados = json.load(open(aliases.config_path()))
    assert dados["pastas"]["koine"]["from"] == "home"
