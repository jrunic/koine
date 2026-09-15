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
