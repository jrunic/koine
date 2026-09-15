"""Escrita do config do Paseo (jd-task #880)."""
import hashlib
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


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def test_json_ilegivel_aborta(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    p = os.path.join(str(tmp_path), "config.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write("{nao json")
    with pytest.raises(pc.RecusaErro) as e:
        pc.aplicar()
    assert e.value.motivo == "ilegivel"
    assert open(p, encoding="utf-8").read() == "{nao json"


def test_dry_run_de_recusa_nao_grava(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    p = os.path.join(str(tmp_path), "config.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write("{nao json")
    with pytest.raises(pc.RecusaErro):
        pc.aplicar(dry_run=True)
    assert open(p, encoding="utf-8").read() == "{nao json"
    assert not os.path.isfile(p + ".bak")


def test_symlink_aborta(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    alvo = tmp_path / "alvo.json"
    alvo.write_text("{}", encoding="utf-8")
    os.symlink(str(alvo), os.path.join(str(tmp_path), "config.json"))
    with pytest.raises(pc.RecusaErro) as e:
        pc.aplicar()
    assert e.value.motivo == "symlink"


def test_diretorio_aborta(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    os.mkdir(os.path.join(str(tmp_path), "config.json"))
    with pytest.raises(pc.RecusaErro) as e:
        pc.aplicar()
    assert e.value.motivo == "diretorio"


def test_grava_e_faz_bak(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    p = os.path.join(str(tmp_path), "config.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"daemon": {"listen": "127.0.0.1:9"}}, f)
    r = pc.aplicar()
    assert r.gravou is True
    assert os.path.isfile(p + ".bak")
    novo = json.loads(open(p, encoding="utf-8").read())
    assert novo["daemon"]["listen"] == "127.0.0.1:9"
    assert novo["daemon"]["browserTools"]["enabled"] is True
    assert not os.path.isfile(p + ".tmp")


def test_segunda_vez_nao_grava(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    pc.aplicar()
    p = os.path.join(str(tmp_path), "config.json")
    h = _sha(p)
    bak = p + ".bak"
    hbak = _sha(bak) if os.path.isfile(bak) else None
    r = pc.aplicar()
    assert r.gravou is False
    assert r.alteracoes == []
    assert _sha(p) == h
    if hbak is not None:
        assert _sha(bak) == hbak


def test_dry_run_nao_grava(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    r = pc.aplicar(dry_run=True)
    assert r.gravou is False
    assert r.dry_run is True
    assert r.alteracoes
    assert not os.path.isfile(os.path.join(str(tmp_path), "config.json"))
    assert not os.path.isfile(os.path.join(str(tmp_path), "config.json.bak"))


def test_preserva_crlf(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    p = os.path.join(str(tmp_path), "config.json")
    with open(p, "wb") as f:
        f.write(b'{"version": 1}\r\n')
    pc.aplicar()
    bruto = open(p, "rb").read()
    assert b"\r\n" in bruto


def test_nasce_arquivo_e_pasta(tmp_path, monkeypatch):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    home = tmp_path / "novo"
    monkeypatch.setenv("PASEO_HOME", str(home))
    r = pc.aplicar()
    assert r.gravou is True
    assert os.path.isfile(os.path.join(str(home), "config.json"))


def test_cli_dry_run_json_nao_grava(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    from koine import cli
    assert cli.main(["paseo-configurar", "--dry-run", "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    assert saida["gravou"] is False
    assert saida["dry_run"] is True
    assert any(a["chave"] == "daemon.browserTools.enabled" for a in saida["alteracoes"])
    assert not os.path.isfile(os.path.join(str(tmp_path), "config.json"))


def test_cli_recusa_ilegivel(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    p = os.path.join(str(tmp_path), "config.json")
    open(p, "w", encoding="utf-8").write("{x")
    from koine import cli
    assert cli.main(["paseo-configurar"]) == 1
    err = capsys.readouterr().err
    assert "JSON inválido" in err


def test_cli_tabela_lista_chave(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pc.sys, "platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    from koine import cli
    assert cli.main(["paseo-configurar"]) == 0
    out = capsys.readouterr().out
    assert "daemon.browserTools.enabled" in out
