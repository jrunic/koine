import subprocess

import pytest

from koine import paseo_app as pa


@pytest.fixture(autouse=True)
def _permite_exercitar_paseo_app(monkeypatch):
    """Este arquivo testa a mecânica interna de `paseo_app` diretamente — o
    marcador de bloqueio de sessão (`tests/conftest.py`, incidente de
    22-24/09/2026) existe durante a suíte inteira. Aqui, com `subprocess.run`
    mockado à parte em cada teste, queremos o caminho real por trás do
    marcador — os testes que exercitam o PRÓPRIO marcador (abaixo)
    sobrescrevem isto de volta."""
    monkeypatch.setattr(pa, "_bloqueado_por_teste", lambda: False)


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


def _explode(*a, **k):
    raise AssertionError("subprocess.run não deveria ter sido chamado — "
                         "o marcador de bloqueio deveria ter cortado antes")


def test_esta_rodando_false_quando_bloqueado_por_teste(monkeypatch):
    """Achado do incidente de 22-24/09/2026: testes e2e sobem o pyz como
    PROCESSO FILHO — um interpretador novo, sem monkeypatch nenhum do
    pytest alcançando ele. O marcador de arquivo (`tests/conftest.py`) é o
    único sinal que qualquer processo filho, em qualquer máquina, enxerga
    igual — por isso o gate é por arquivo, não por variável de ambiente."""
    monkeypatch.setattr(pa, "_bloqueado_por_teste", lambda: True)
    monkeypatch.setattr(pa.sys, "platform", "darwin")
    monkeypatch.setattr(pa.subprocess, "run", _explode)
    assert pa.esta_rodando() is False


def test_abrir_false_quando_bloqueado_por_teste(monkeypatch):
    monkeypatch.setattr(pa, "_bloqueado_por_teste", lambda: True)
    monkeypatch.setattr(pa.sys, "platform", "darwin")
    monkeypatch.setattr(pa.subprocess, "run", _explode)
    assert pa.abrir() is False


def test_encerrar_no_op_quando_bloqueado_por_teste(monkeypatch):
    """encerrar() não precisa do próprio check — ele já chama esta_rodando()
    primeiro, que corta pelo marcador antes de qualquer subprocess.run."""
    monkeypatch.setattr(pa, "_bloqueado_por_teste", lambda: True)
    monkeypatch.setattr(pa.sys, "platform", "darwin")
    monkeypatch.setattr(pa.subprocess, "run", _explode)
    assert pa.encerrar() is True


def test_marcador_bloqueio_e_um_caminho_fixo_em_disco():
    """Fixo e absoluto — nunca derivado de TMPDIR/HOME, que podem faltar no
    env{} custom que muitos testes e2e constroem do zero para o filho."""
    assert pa.MARCADOR_BLOQUEIO == "/tmp/.koine-testes-bloqueiam-paseo"
