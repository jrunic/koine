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
