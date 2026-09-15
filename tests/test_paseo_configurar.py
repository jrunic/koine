"""Escrita do config do Paseo (jd-task #880)."""
import json
import os

import pytest

from koine import paseo_configurar as pc


def test_home_posix_reusa_o_diagnostico(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    assert pc.home_para_escrita() == str(tmp_path)


def test_windows_sem_variavel_aborta(monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "win32")
    monkeypatch.delenv("PASEO_HOME", raising=False)
    with pytest.raises(pc.RecusaErro) as e:
        pc.home_para_escrita()
    assert e.value.motivo == "windows-sem-home"


def test_windows_com_variavel_aceita(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "win32")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    assert pc.home_para_escrita() == str(tmp_path)


def test_canal_ausente_vira_true():
    novo, alts = pc.mesclar({})
    assert novo["daemon"]["browserTools"]["enabled"] is True
    assert novo["daemon"]["mcp"]["injectIntoAgents"] is True
    chaves = {a.chave: a for a in alts}
    assert chaves["daemon.browserTools.enabled"].antes is None
    assert chaves["daemon.browserTools.enabled"].depois is True


def test_canal_false_vira_true():
    cfg = {"daemon": {"browserTools": {"enabled": False},
                      "mcp": {"injectIntoAgents": False}}}
    novo, alts = pc.mesclar(cfg)
    assert novo["daemon"]["browserTools"]["enabled"] is True
    assert any(a.chave == "daemon.mcp.injectIntoAgents" and a.antes is False
               for a in alts)


def test_canal_ja_true_nao_entra_nas_alteracoes():
    cfg = {"daemon": {"browserTools": {"enabled": True},
                      "mcp": {"injectIntoAgents": True}}}
    _, alts = pc.mesclar(cfg)
    assert not any(a.chave.startswith("daemon.browserTools") or
                   a.chave.startswith("daemon.mcp") for a in alts)
