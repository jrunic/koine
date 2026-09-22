import subprocess

from koine import paseo_app as pa


def test_esta_rodando_true_quando_osascript_diz_true(monkeypatch):
    monkeypatch.setattr(pa.sys, "platform", "darwin")
    monkeypatch.setattr(
        pa.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="true\n"))
    assert pa.esta_rodando() is True


def test_esta_rodando_false_quando_osascript_diz_false(monkeypatch):
    monkeypatch.setattr(pa.sys, "platform", "darwin")
    monkeypatch.setattr(
        pa.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="false\n"))
    assert pa.esta_rodando() is False


def test_esta_rodando_false_fora_do_macos(monkeypatch):
    monkeypatch.setattr(pa.sys, "platform", "win32")
    assert pa.esta_rodando() is False


def test_encerrar_no_op_quando_ja_nao_esta_rodando(monkeypatch):
    monkeypatch.setattr(pa, "esta_rodando", lambda: False)
    chamou = []
    monkeypatch.setattr(pa.subprocess, "run", lambda *a, **k: chamou.append(a))
    assert pa.encerrar() is True
    assert chamou == []


def test_encerrar_manda_quit_e_espera_parar(monkeypatch):
    estados = iter([True, True, False])
    monkeypatch.setattr(pa, "esta_rodando", lambda: next(estados))
    monkeypatch.setattr(pa.time, "sleep", lambda s: None)
    chamadas = []
    monkeypatch.setattr(
        pa.subprocess, "run",
        lambda args, **k: chamadas.append(args) or
        subprocess.CompletedProcess(args, 0))
    assert pa.encerrar() is True
    assert any("quit app" in " ".join(c) for c in chamadas)


def test_abrir_usa_open_dash_a_no_macos(monkeypatch):
    monkeypatch.setattr(pa.sys, "platform", "darwin")
    chamadas = []
    monkeypatch.setattr(
        pa.subprocess, "run",
        lambda args, **k: chamadas.append(args) or
        subprocess.CompletedProcess(args, 0))
    assert pa.abrir() is True
    assert chamadas[-1] == ["open", "-a", pa.APP_MACOS]


def test_abrir_devolve_false_fora_do_macos(monkeypatch):
    monkeypatch.setattr(pa.sys, "platform", "win32")
    assert pa.abrir() is False


def test_aguardar_daemon_devolve_true_quando_servico_ok(monkeypatch):
    from koine import paseo_diagnostico as pd
    monkeypatch.setattr(pd, "home_do_paseo", lambda: "/x")
    monkeypatch.setattr(pd, "ler_config", lambda home: ({"daemon": {}}, None))
    monkeypatch.setattr(pd, "verificar_servico",
                        lambda cfg: pd.Verificacao("servico.escutando", pd.OK, "ok", {}))
    assert pa.aguardar_daemon(timeout=1, intervalo=0.01) is True


def test_aguardar_daemon_devolve_false_no_timeout(monkeypatch):
    from koine import paseo_diagnostico as pd
    monkeypatch.setattr(pd, "home_do_paseo", lambda: "/x")
    monkeypatch.setattr(pd, "ler_config", lambda home: (None, object()))
    assert pa.aguardar_daemon(timeout=0.05, intervalo=0.01) is False
