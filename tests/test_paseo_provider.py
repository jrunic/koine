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
    assert novo["agents"]["providers"]["kn-opencode"]["command"] == [str(exe), "acp"]


def test_ja_canonico_e_inalterado(tmp_path):
    exe = tmp_path / "w"
    exe.write_text("x")
    exe.chmod(0o755)
    cfg = {"daemon": {"relay": {"enabled": False}},
           "agents": {"providers": {
               "kn-claude": {"extends": "claude", "command": [str(exe)]},
               "kn-claude-hermes": {"extends": "claude", "command": [str(exe)],
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
