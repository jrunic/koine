import subprocess

import pytest

from koine import paseo_app_windows as paw


@pytest.fixture(autouse=True)
def _permite_exercitar_paseo_app_windows(monkeypatch):
    """Mesmo padrão de tests/test_paseo_app.py: o marcador de bloqueio de
    sessão existe durante a suíte inteira; aqui queremos exercitar o
    caminho real por trás dele, com `subprocess.run` costurado à parte em
    cada teste."""
    monkeypatch.setattr(paw, "_bloqueado_por_teste", lambda: False)


def test_esta_rodando_true_quando_tasklist_lista_o_processo(monkeypatch):
    monkeypatch.setattr(paw.sys, "platform", "win32")
    saida = ('"Paseo.exe","11632","Console","2","164.096 K"\n')
    monkeypatch.setattr(
        paw.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=saida))
    assert paw.esta_rodando() is True


def test_esta_rodando_false_quando_tasklist_nao_lista_nada(monkeypatch):
    monkeypatch.setattr(paw.sys, "platform", "win32")
    saida = ("INFORMAÇÕES: nenhuma tarefa em execução correspondente aos "
             "critérios especificados.\n")
    monkeypatch.setattr(
        paw.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=saida))
    assert paw.esta_rodando() is False


def test_esta_rodando_false_fora_do_windows(monkeypatch):
    monkeypatch.setattr(paw.sys, "platform", "darwin")
    assert paw.esta_rodando() is False


def test_encerrar_no_op_quando_ja_nao_esta_rodando(monkeypatch):
    monkeypatch.setattr(paw, "esta_rodando", lambda: False)
    chamou = []
    monkeypatch.setattr(paw.subprocess, "run", lambda *a, **k: chamou.append(a))
    assert paw.encerrar() is True
    assert chamou == []


def test_encerrar_chama_taskkill_sem_forcar_quando_desktop_managed_true(
        monkeypatch):
    from koine import paseo_diagnostico as pd
    estados = iter([True, True, False])
    monkeypatch.setattr(paw, "esta_rodando", lambda: next(estados))
    monkeypatch.setattr(pd, "desktop_managed", lambda: True)
    monkeypatch.setattr(paw.time, "sleep", lambda s: None)
    chamadas = []
    monkeypatch.setattr(
        paw.subprocess, "run",
        lambda args, **k: chamadas.append(args) or
        subprocess.CompletedProcess(args, 0))
    assert paw.encerrar() is True
    assert chamadas[-1] == ["taskkill", "/IM", paw.APP_EXE]
    assert "/F" not in chamadas[-1]


def test_encerrar_recusa_quando_desktop_managed_false(monkeypatch):
    """desktopManaged: false com o app rodando — cenário sem medição real
    (spec, assumption 7): taskkill /IM mede TODOS os processos com esse
    nome de imagem, e matar por nome quando o app não gerencia o daemon
    mataria os dois sem diferenciar. O módulo se recusa e não chama
    taskkill nenhum."""
    from koine import paseo_diagnostico as pd
    monkeypatch.setattr(paw, "esta_rodando", lambda: True)
    monkeypatch.setattr(pd, "desktop_managed", lambda: False)
    chamou = []
    monkeypatch.setattr(paw.subprocess, "run", lambda *a, **k: chamou.append(a))
    assert paw.encerrar() is False
    assert chamou == []


def test_encerrar_recusa_quando_desktop_managed_ilegivel(monkeypatch):
    """Default seguro para campo ausente/ilegível (None): mesmo caminho
    cauteloso do valor False explícito (spec, Decisões de Implementação)."""
    from koine import paseo_diagnostico as pd
    monkeypatch.setattr(paw, "esta_rodando", lambda: True)
    monkeypatch.setattr(pd, "desktop_managed", lambda: None)
    chamou = []
    monkeypatch.setattr(paw.subprocess, "run", lambda *a, **k: chamou.append(a))
    assert paw.encerrar() is False
    assert chamou == []


def test_abrir_usa_start_b_no_windows(monkeypatch):
    monkeypatch.setattr(paw.sys, "platform", "win32")
    monkeypatch.setattr(paw, "_resolver_app",
                        lambda: r"C:\Users\x\AppData\Local\Programs\Paseo\Paseo.exe")
    chamadas = []
    monkeypatch.setattr(
        paw.subprocess, "run",
        lambda args, **k: chamadas.append(args) or
        subprocess.CompletedProcess(args, 0))
    assert paw.abrir() is True
    assert chamadas[-1] == [
        "cmd", "/c", "start", "/B", "",
        r"C:\Users\x\AppData\Local\Programs\Paseo\Paseo.exe"]


def test_abrir_ignora_desktop_managed_e_sempre_roda(monkeypatch):
    """abrir() é incondicional nas duas plataformas (spec, achado 1 da
    revisão dev-10): antes da primeira abertura o campo sempre lê False —
    gatear aqui bloquearia toda instalação, sempre."""
    from koine import paseo_diagnostico as pd
    monkeypatch.setattr(paw.sys, "platform", "win32")
    monkeypatch.setattr(paw, "_resolver_app", lambda: "Paseo.exe")
    monkeypatch.setattr(pd, "desktop_managed",
                        lambda: (_ for _ in ()).throw(
                            AssertionError("abrir() não deveria consultar")))
    monkeypatch.setattr(
        paw.subprocess, "run",
        lambda args, **k: subprocess.CompletedProcess(args, 0))
    assert paw.abrir() is True


def test_abrir_false_quando_app_nao_encontrado(monkeypatch):
    monkeypatch.setattr(paw.sys, "platform", "win32")
    monkeypatch.setattr(paw, "_resolver_app", lambda: None)
    assert paw.abrir() is False


def test_abrir_false_fora_do_windows(monkeypatch):
    monkeypatch.setattr(paw.sys, "platform", "darwin")
    assert paw.abrir() is False
