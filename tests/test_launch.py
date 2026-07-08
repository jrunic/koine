import os
import pytest
from koine import launch


def test_lancar_unix_faz_chdir_e_exec(monkeypatch):
    capturado = {}
    monkeypatch.setattr(launch.shutil, "which", lambda c: "/fake/bin/claude")
    monkeypatch.setattr(launch.os, "chdir", lambda p: capturado.__setitem__("cwd", p))

    class _Parou(Exception):
        pass

    def fake_execvpe(file, args, env):
        capturado["file"] = file
        capturado["args"] = args
        raise _Parou()  # execvpe real substituiria o processo; simulamos a chamada

    monkeypatch.setattr(launch.os, "execvpe", fake_execvpe)
    monkeypatch.setattr(launch.sys, "platform", "darwin")
    with pytest.raises(_Parou):
        launch.lancar("claude", "/algum/pasta")
    assert capturado["cwd"] == "/algum/pasta"
    assert capturado["file"] == "claude"
    assert capturado["args"] == ["claude"]  # sem args extras p/ claude


def test_lancar_cliente_ausente_erra_amigavel(monkeypatch):
    monkeypatch.setattr(launch.shutil, "which", lambda c: None)
    with pytest.raises(launch.ClienteNaoEncontrado) as e:
        launch.lancar("claude", "/algum/pasta")
    assert "não encontrado no PATH" in str(e.value)
