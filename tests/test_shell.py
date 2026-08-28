import subprocess

from koine import shell


def _sonda_falsa(mapa):
    """mapa: nome do degrau → estado. Invocação é o próprio nome."""
    def sonda(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return sonda


def test_melhor_escolhe_o_primeiro_degrau_que_executa():
    sonda = _sonda_falsa({shell.PWSH: shell.EXECUTOU, shell.BASH: shell.EXECUTOU})
    d = shell.melhor(shell.ESCADA, sonda=sonda)
    assert d.nome == shell.PWSH
    assert d.invocacao == "pwsh"


def test_melhor_pula_degrau_recusado():
    # é a estação corporativa: o pwsh existe, está no PATH e a política nega.
    sonda = _sonda_falsa({shell.PWSH: shell.RECUSADO,
                          shell.POWERSHELL: shell.RECUSADO,
                          shell.BASH: shell.EXECUTOU})
    assert shell.melhor(shell.ESCADA, sonda=sonda).nome == shell.BASH


def test_melhor_respeita_os_degraus_que_o_cliente_aceita():
    # o claude não aceita cmd; com tudo recusado menos cmd, não há degrau.
    sonda = _sonda_falsa({shell.CMD: shell.EXECUTOU})
    assert shell.melhor((shell.PWSH, shell.POWERSHELL, shell.BASH), sonda=sonda) is None
    assert shell.melhor(shell.ESCADA, sonda=sonda).nome == shell.CMD


def test_sondar_diz_executou_quando_o_processo_roda(monkeypatch):
    monkeypatch.setattr(shell.shutil, "which", lambda n: r"C:\x\pwsh.exe")
    monkeypatch.setattr(shell.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 0))
    assert shell.sondar(shell.PWSH) == (r"C:\x\pwsh.exe", shell.EXECUTOU)


def test_sondar_diz_recusado_quando_a_politica_nega(monkeypatch):
    # WinError 1260: "Este programa está bloqueado por uma política de grupo."
    erro = OSError("bloqueado")
    erro.winerror = 1260

    def explode(*a, **k):
        raise erro

    monkeypatch.setattr(shell.shutil, "which", lambda n: r"C:\x\pwsh.exe")
    monkeypatch.setattr(shell.subprocess, "run", explode)
    assert shell.sondar(shell.PWSH) == (r"C:\x\pwsh.exe", shell.RECUSADO)


def test_sondar_diz_recusado_quando_o_processo_sai_diferente_de_zero(monkeypatch):
    monkeypatch.setattr(shell.shutil, "which", lambda n: r"C:\x\pwsh.exe")
    monkeypatch.setattr(shell.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 1))
    assert shell.sondar(shell.PWSH)[1] == shell.RECUSADO


def test_sondar_diz_ausente_quando_nao_esta_no_path(monkeypatch):
    monkeypatch.setattr(shell.shutil, "which", lambda n: None)
    assert shell.sondar(shell.PWSH) == (shell.PWSH, shell.AUSENTE)


def test_sondar_diz_recusado_quando_o_processo_trava(monkeypatch):
    def trava(*a, **k):
        raise subprocess.TimeoutExpired(cmd="pwsh", timeout=shell.TIMEOUT)

    monkeypatch.setattr(shell.shutil, "which", lambda n: r"C:\x\pwsh.exe")
    monkeypatch.setattr(shell.subprocess, "run", trava)
    assert shell.sondar(shell.PWSH)[1] == shell.RECUSADO


def test_sondar_usa_os_argumentos_certos_por_familia(monkeypatch):
    vistos = {}

    def espia(argv, **k):
        vistos[argv[0]] = argv[1:]
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(shell.shutil, "which", lambda n: n)
    monkeypatch.setattr(shell.subprocess, "run", espia)
    for nome in (shell.PWSH, shell.POWERSHELL, shell.BASH, shell.CMD):
        shell.sondar(nome)
    assert vistos["pwsh"] == ["-NoProfile", "-Command", "exit"]
    assert vistos["powershell"] == ["-NoProfile", "-Command", "exit"]
    assert vistos["bash"] == ["-c", "exit"]
    assert vistos["cmd"] == ["/c", "exit"]
