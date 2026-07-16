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


def test_lancar_windows_resolve_via_cmd_por_nome(monkeypatch):
    """Windows: lança via `cmd /c <cliente>` pelo NOME (não pelo binpath do
    which) — deixa o cmd.exe escolher a variante executável e evita WinError 193
    quando o which devolve um shim/variante que o CreateProcess recusa."""
    capturado = {}
    # which devolve uma variante qualquer — irrelevante para o comando montado
    monkeypatch.setattr(launch.shutil, "which", lambda c: r"C:\some\codex.EXE")
    monkeypatch.setattr(launch.sys, "platform", "win32")

    def fake_run(cmd, **_kw):
        capturado["cmd"] = cmd
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(launch.subprocess, "run", fake_run)
    launch.lancar("codex", r"C:\pasta", args=["-c", "x=1"])
    assert capturado["cmd"] == ["cmd", "/c", "codex", "-c", "x=1"]


def test_lancar_windows_oserror_vira_cliente_nao_executavel(monkeypatch):
    """Se o subprocess.run levantar OSError (ex.: WinError 193), vira exceção
    tipada carregando cliente+binpath — o consumidor decide a apresentação."""
    monkeypatch.setattr(launch.shutil, "which", lambda c: r"C:\some\codex.exe")
    monkeypatch.setattr(launch.sys, "platform", "win32")

    def boom(cmd, **_kw):
        raise OSError(193, "não é um aplicativo Win32 válido")

    monkeypatch.setattr(launch.subprocess, "run", boom)
    with pytest.raises(launch.ClienteNaoExecutavel) as e:
        launch.lancar("codex", r"C:\pasta")
    assert e.value.cliente == "codex"
    assert e.value.binpath == r"C:\some\codex.exe"


def test_lancar_cliente_ausente_erra_amigavel(monkeypatch):
    monkeypatch.setattr(launch.shutil, "which", lambda c: None)
    with pytest.raises(launch.ClienteNaoEncontrado) as e:
        launch.lancar("claude", "/algum/pasta")
    assert e.value.cliente == "claude"
