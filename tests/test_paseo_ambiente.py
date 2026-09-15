"""Resolvedor do ambiente Paseo (spec 20260915-spec-paseo-windows-sem-variavel)."""
import os

import pytest

from koine import paseo_ambiente as amb


def _monta(tmp_path, com_config=True):
    home = tmp_path / ".paseo"
    home.mkdir(parents=True, exist_ok=True)
    if com_config:
        (home / "config.json").write_text("{}", encoding="utf-8")
    return str(home)


def test_override_e_autoritativo_mesmo_sem_config(tmp_path, monkeypatch):
    alvo = str(tmp_path / "override")
    monkeypatch.setenv("PASEO_HOME", alvo)
    h = amb.resolver_home()
    assert h.caminho == alvo
    assert h.origem == "override"


def test_override_vazio_equivale_a_ausente(tmp_path, monkeypatch):
    _monta(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("PASEO_HOME", "")
    h = amb.resolver_home()
    assert h.origem != "override"
    assert h.caminho.endswith(".paseo")


def test_sem_override_usa_config_existente(tmp_path, monkeypatch):
    _monta(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PASEO_HOME", raising=False)
    h = amb.resolver_home()
    assert h.origem == "descoberto"
    assert os.path.isfile(os.path.join(h.caminho, "config.json"))


def test_sem_config_cai_no_padrao(tmp_path, monkeypatch):
    _monta(tmp_path, com_config=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PASEO_HOME", raising=False)
    h = amb.resolver_home()
    assert h.origem == "padrao"
    assert h.caminho == os.path.join(str(tmp_path), ".paseo")


def test_multiplos_candidates_abortam(monkeypatch):
    monkeypatch.delenv("PASEO_HOME", raising=False)
    monkeypatch.setattr(amb, "locais_padroes",
                        lambda: ["/a/.paseo", "/b/.paseo"])
    monkeypatch.setattr(amb.os.path, "isfile", lambda p: p.endswith("config.json"))
    with pytest.raises(amb.RecusaErro) as e:
        amb.resolver_home()
    assert e.value.motivo == "multiplos-configs"
    assert "/a/.paseo" in e.value.mensagem and "/b/.paseo" in e.value.mensagem
