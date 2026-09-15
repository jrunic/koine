"""Entries kn-* no config do Paseo (jd-task #881)."""
import hashlib
import json
import os

import pytest

from koine import paseo_provider as pp


def _info(caminho, args=(), extends="claude"):
    return {
        "wrapper": "kn-claude-paseo",
        "provider": "kn-claude",
        "provider_hermes": "kn-claude-hermes",
        "extends": extends,
        "args": list(args),
        "existe": caminho is not None,
        "caminho": caminho,
    }


def test_planta_generico_e_hermes(tmp_path):
    exe = tmp_path / "kn-claude-paseo"
    exe.write_text("#!/bin/sh\n")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}}}
    novo, deltas = pp.mesclar_providers(cfg, {"claude": _info(str(exe))})
    g = novo["agents"]["providers"]["kn-claude"]
    h = novo["agents"]["providers"]["kn-claude-hermes"]
    assert g["command"] == [str(exe)]
    assert g["extends"] == "claude"
    assert "KOINE_AGENTE" not in g.get("env", {})
    assert h["env"]["KOINE_AGENTE"] == "hermes"
    assert h["command"] == [str(exe)]
    acoes = {d.id: d.acao for d in deltas}
    assert acoes["kn-claude"] == "plantado"
    assert acoes["kn-claude-hermes"] == "plantado"


def test_terceiro_sobrevive(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": {"jd-tech": {"extends": "claude"}}}}
    novo, _ = pp.mesclar_providers(cfg, {"claude": _info(str(exe))})
    assert novo["agents"]["providers"]["jd-tech"]["extends"] == "claude"


def test_remove_koine_agente_do_generico(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": {"kn-claude": {
               "extends": "claude", "command": [str(exe)],
               "env": {"KOINE_AGENTE": "hermes", "OUTRO": "1"}}}}}
    novo, deltas = pp.mesclar_providers(cfg, {"claude": _info(str(exe))})
    env = novo["agents"]["providers"]["kn-claude"].get("env", {})
    assert "KOINE_AGENTE" not in env
    assert env.get("OUTRO") == "1"
    assert any(d.id == "kn-claude" and d.acao == "atualizado" for d in deltas)


def test_opencode_args_no_command(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    info = _info(str(exe), args=("acp",), extends="acp")
    info["provider"] = "kn-opencode"
    info["provider_hermes"] = "kn-opencode-hermes"
    cfg = {"daemon": {"relay": {"enabled": False}}}
    novo, _ = pp.mesclar_providers(cfg, {"opencode": info})
    # o subcomando do protocolo é do launch, não do entry — carregá-lo aqui
    # duplicava o `acp` no spawn (medido no Grupo Aldo, 15/09/2026)
    assert novo["agents"]["providers"]["kn-opencode"]["command"] == [str(exe)]


def test_ja_canonico_e_inalterado(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": {
               "kn-claude": {"extends": "claude", "command": [str(exe)],
                             "label": "Koine · claude"},
               "kn-claude-hermes": {"extends": "claude", "command": [str(exe)],
                                    "label": "Koine · claude Hermes",
                                    "env": {"KOINE_AGENTE": "hermes"}}}}}
    _, deltas = pp.mesclar_providers(cfg, {"claude": _info(str(exe))})
    assert {d.acao for d in deltas} == {"inalterado"}


def test_path_mudou_atualiza(tmp_path):
    exe = tmp_path / "w2"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": {
               "kn-claude": {"extends": "claude", "command": ["/old/w"]}}}}
    _, deltas = pp.mesclar_providers(cfg, {"claude": _info(str(exe))})
    assert any(d.id == "kn-claude" and d.acao == "atualizado" for d in deltas)


def test_sem_relay_aborta():
    with pytest.raises(pp.RecusaErro) as e:
        pp.preparar({}, {"claude": _info("/x")})
    assert e.value.motivo == "sem-relay"


def test_wrapper_ausente_aborta():
    cfg = {"daemon": {"relay": {"enabled": False}}}
    info = _info(None)
    info["existe"] = False
    with pytest.raises(pp.RecusaErro) as e:
        pp.preparar(cfg, {"claude": info})
    assert e.value.motivo == "wrapper-ausente"


def test_wrapper_diretorio_aborta(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    cfg = {"daemon": {"relay": {"enabled": False}}}
    with pytest.raises(pp.RecusaErro) as e:
        pp.preparar(cfg, {"claude": _info(str(d))})
    assert e.value.motivo == "wrapper-morto"


def test_providers_lista_aborta(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": []}}
    with pytest.raises(pp.RecusaErro) as e:
        pp.preparar(cfg, {"claude": _info(str(exe))})
    assert e.value.motivo == "tipo"


def test_command_string_aborta(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": {"kn-claude": {"command": "/usr/bin/x"}}}}
    with pytest.raises(pp.RecusaErro) as e:
        pp.preparar(cfg, {"claude": _info(str(exe))})
    assert e.value.motivo == "tipo"


def test_aplicar_grava_e_doctor_completo(tmp_path, monkeypatch):
    monkeypatch.setattr("koine.paseo_configurar.sys.platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False},
                      "browserTools": {"enabled": True},
                      "mcp": {"injectIntoAgents": True}}}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(pp, "matriz", lambda: {"claude": _info(str(exe))})
    r = pp.aplicar()
    assert r.gravou is True
    from koine.paseo_diagnostico import verificar_providers
    d = json.loads(p.read_text(encoding="utf-8"))
    monkeypatch.setattr("koine.paseo_diagnostico._prescritos",
                        lambda: ["kn-claude", "kn-claude-hermes"])
    monkeypatch.setattr("koine.paseo_diagnostico._disponiveis", lambda: None)
    v = verificar_providers(d)
    assert v.dado["estado"] == "completo"


def test_aplicar_sem_arquivo_aborta(tmp_path, monkeypatch):
    monkeypatch.setattr("koine.paseo_configurar.sys.platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    monkeypatch.setattr(pp, "matriz", lambda: {"claude": _info("/bin/true")})
    with pytest.raises(pp.RecusaErro) as e:
        pp.aplicar()
    assert e.value.motivo == "sem-arquivo"


def test_aplicar_segunda_vez_nao_grava(tmp_path, monkeypatch):
    monkeypatch.setattr("koine.paseo_configurar.sys.platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"daemon": {"relay": {"enabled": False}}}),
                 encoding="utf-8")
    monkeypatch.setattr(pp, "matriz", lambda: {"claude": _info(str(exe))})
    pp.aplicar()
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    r = pp.aplicar()
    assert r.gravou is False
    assert hashlib.sha256(p.read_bytes()).hexdigest() == h


def test_aplicar_dry_run_nao_grava(tmp_path, monkeypatch):
    monkeypatch.setattr("koine.paseo_configurar.sys.platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    p = tmp_path / "config.json"
    bruto = json.dumps({"daemon": {"relay": {"enabled": False}}})
    p.write_text(bruto, encoding="utf-8")
    monkeypatch.setattr(pp, "matriz", lambda: {"claude": _info(str(exe))})
    r = pp.aplicar(dry_run=True)
    assert r.gravou is False
    assert r.dry_run is True
    assert p.read_text(encoding="utf-8") == bruto


def test_cli_json_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("koine.paseo_configurar.sys.platform", "darwin")
    monkeypatch.setenv("PASEO_HOME", str(tmp_path))
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    (tmp_path / "config.json").write_text(json.dumps(
        {"daemon": {"relay": {"enabled": False}}}), encoding="utf-8")
    monkeypatch.setattr(pp, "matriz", lambda: {"claude": _info(str(exe))})
    from koine import cli
    assert cli.main(["paseo-provider", "--json"]) == 0
    saida = json.loads(capsys.readouterr().out)
    ids = {e["id"] for e in saida["entries"]}
    assert "kn-claude" in ids and "kn-claude-hermes" in ids
    assert saida["gravou"] is True


# --- .bat/.cmd no Windows não depende do bit POSIX (spec 20260915) ---------

def test_executavel_bat_no_windows_nao_precisa_de_bit_x(tmp_path, monkeypatch):
    alvo = tmp_path / "kn-claude-paseo.bat"
    alvo.write_text("@echo off", encoding="utf-8")
    monkeypatch.setattr(pp.sys, "platform", "win32")
    assert pp._executavel(str(alvo)) is True


def test_executavel_posix_continua_exigindo_x(tmp_path):
    alvo = tmp_path / "kn-claude-paseo"
    alvo.write_text("#!/bin/sh\n", encoding="utf-8")
    os.chmod(alvo, 0o644)
    assert pp._executavel(str(alvo)) is False
    os.chmod(alvo, 0o755)
    assert pp._executavel(str(alvo)) is True


# --- label e acp para o Paseo 0.8.0 (diário do Patrick, 15/09) ------------

def _info_claude():
    return {"extends": "claude", "args": [], "caminho": "/x/kn-claude-paseo",
            "wrapper": "kn-claude-paseo", "provider": "kn-claude",
            "provider_hermes": "kn-claude-hermes"}


def test_entry_tem_label():
    novo, _ = pp.mesclar_providers({}, {"claude": _info_claude()})
    provs = novo["agents"]["providers"]
    assert provs["kn-claude"]["label"] == "Koine · claude"
    assert provs["kn-claude-hermes"]["label"] == "Koine · claude Hermes"


def test_opencode_nao_duplica_acp():
    # a rota MANTÉM o args: o launch é quem injeta o subcomando (cli.py).
    # O entry não pode carregar também — daí a duplicação medida no Grupo Aldo.
    from koine.adapters import opencode
    assert opencode.PASEO.args == ("acp",)
    info = {"extends": opencode.PASEO.extends,
            "args": list(opencode.PASEO.args),
            "caminho": "/x/kn-opencode-paseo", "wrapper": "kn-opencode-paseo",
            "provider": "kn-opencode", "provider_hermes": "kn-opencode-hermes"}
    novo, _ = pp.mesclar_providers({}, {"opencode": info})
    assert novo["agents"]["providers"]["kn-opencode"]["command"] == ["/x/kn-opencode-paseo"]


def test_label_divergente_do_koine_e_corrigido():
    cfg = {"agents": {"providers": {"kn-claude": {
        "extends": "claude", "command": ["/velho"], "label": "coisa antiga"}}}}
    novo, deltas = pp.mesclar_providers(cfg, {"claude": _info_claude()})
    assert novo["agents"]["providers"]["kn-claude"]["label"] == "Koine · claude"
    assert any(d.id == "kn-claude" and d.acao == "atualizado" for d in deltas)
