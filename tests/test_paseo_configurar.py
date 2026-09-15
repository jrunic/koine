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


def test_version_ausente_planta_1():
    novo, alts = pc.mesclar({})
    assert novo["version"] == 1
    assert any(a.chave == "version" and a.depois == 1 for a in alts)


def test_version_existente_nao_mexe():
    novo, alts = pc.mesclar({"version": 2})
    assert novo["version"] == 2
    assert not any(a.chave == "version" for a in alts)


def test_relay_ausente_vira_false():
    novo, alts = pc.mesclar({})
    assert novo["daemon"]["relay"]["enabled"] is False
    assert any(a.chave == "daemon.relay.enabled" and a.depois is False for a in alts)


def test_relay_true_nao_mexe():
    cfg = {"daemon": {"relay": {"enabled": True}}}
    novo, _ = pc.mesclar(cfg)
    assert novo["daemon"]["relay"]["enabled"] is True


def test_stt_ausente_planta_parakeet():
    novo, _ = pc.mesclar({})
    stt = novo["features"]["dictation"]["stt"]
    assert stt["provider"] == "local"
    assert stt["model"] == "parakeet-tdt-0.6b-v3-int8"


def test_stt_existente_nao_completa_model():
    cfg = {"features": {"dictation": {"stt": {"provider": "openai"}}}}
    with pytest.raises(pc.RecusaErro) as e:
        pc.mesclar(cfg)
    assert e.value.motivo == "tipo"


def test_stt_completo_nao_mexe():
    cfg = {"features": {"dictation": {"stt": {
        "provider": "openai", "model": "outro"}}}}
    novo, alts = pc.mesclar(cfg)
    assert novo["features"]["dictation"]["stt"]["provider"] == "openai"
    assert not any(a.chave.startswith("features.dictation") for a in alts)


def test_voicemode_ausente_planta_false():
    novo, _ = pc.mesclar({})
    assert novo["features"]["voiceMode"]["enabled"] is False


def test_voicemode_true_nao_mexe():
    cfg = {"features": {"voiceMode": {"enabled": True}}}
    novo, _ = pc.mesclar(cfg)
    assert novo["features"]["voiceMode"]["enabled"] is True


def test_listen_sobrevive():
    cfg = {"daemon": {"listen": "127.0.0.1:9999"}}
    novo, _ = pc.mesclar(cfg)
    assert novo["daemon"]["listen"] == "127.0.0.1:9999"


def test_providers_sobrevivem():
    cfg = {"agents": {"providers": {"jd-tech": {}}}}
    novo, _ = pc.mesclar(cfg)
    assert "jd-tech" in novo["agents"]["providers"]


def test_daemon_null_aborta():
    with pytest.raises(pc.RecusaErro) as e:
        pc.mesclar({"daemon": None})
    assert e.value.motivo == "tipo"


def test_features_string_aborta():
    with pytest.raises(pc.RecusaErro) as e:
        pc.mesclar({"features": "x"})
    assert e.value.motivo == "tipo"
