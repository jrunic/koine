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


def test_executavel_no_path_vence(monkeypatch, tmp_path):
    fallback = tmp_path / "Paseo" / "resources" / "bin" / "paseo.cmd"
    fallback.parent.mkdir(parents=True)
    fallback.write_text("@echo off", encoding="utf-8")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(amb.shutil, "which",
                        lambda n: "/no/path/paseo" if n == "paseo" else None)
    e = amb.resolver_executavel("paseo")
    assert e is not None
    assert e.origem == "path"


def test_executavel_no_fallback_e_aceito(monkeypatch, tmp_path):
    bin_dir = tmp_path / "Programs" / "Paseo" / "resources" / "bin"
    bin_dir.mkdir(parents=True)
    (bin_dir / "paseo.cmd").write_text("@echo off", encoding="utf-8")
    monkeypatch.setattr(amb.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(amb.shutil, "which", lambda _: None)
    e = amb.resolver_executavel("paseo")
    assert e.origem == "fallback"
    assert e.caminho.endswith("paseo.cmd")


def test_executavel_ausente_devolve_none(monkeypatch, tmp_path):
    monkeypatch.setattr(amb.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(amb.shutil, "which", lambda _: None)
    assert amb.resolver_executavel("paseo") is None


def _grava_chamada(destino):
    def fake_run(cmd, **kw):
        destino.append(cmd)
        class R:
            returncode, stdout, stderr = 0, "", ""
        return R()
    return fake_run


def test_windows_executa_cmd_bat_por_cmd_exe(monkeypatch):
    chamadas = []
    monkeypatch.setattr(amb.sys, "platform", "win32")
    monkeypatch.setattr(amb.subprocess, "run", _grava_chamada(chamadas))
    amb.executar(r"C:\um dir\Paseo\paseo.cmd", ["status", "--filtro", "com espaco"])
    assert chamadas[0][:3] == ["cmd", "/c", r"C:\um dir\Paseo\paseo.cmd"]
    assert chamadas[0][3:] == ["status", "--filtro", "com espaco"]


def test_posix_executa_direto(monkeypatch):
    chamadas = []
    monkeypatch.setattr(amb.sys, "platform", "darwin")
    monkeypatch.setattr(amb.subprocess, "run", _grava_chamada(chamadas))
    amb.executar("/usr/local/bin/paseo", ["status"])
    assert chamadas[0] == ["/usr/local/bin/paseo", "status"]
