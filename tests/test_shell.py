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


def test_bash_e_procurado_na_instalacao_do_git_quando_falta_no_path(monkeypatch, tmp_path):
    # instalação sem administrador: o Git cai no perfil do usuário.
    git_bin = tmp_path / "Local" / "Programs" / "Git" / "bin"
    git_bin.mkdir(parents=True)
    bash = git_bin / "bash.exe"
    bash.write_text("")

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.delenv("ProgramFiles", raising=False)
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.setattr(shell.shutil, "which", lambda n: None)
    monkeypatch.setattr(shell.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 0))

    invocacao, estado = shell.sondar(shell.BASH)
    assert estado == shell.EXECUTOU
    assert invocacao == str(bash)   # caminho ABSOLUTO, que é o que o opencode aceita


def test_bash_no_path_vence_a_busca_no_git(monkeypatch):
    monkeypatch.setattr(shell.shutil, "which", lambda n: r"C:\path\bash.exe")
    monkeypatch.setattr(shell.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 0))
    assert shell.sondar(shell.BASH)[0] == r"C:\path\bash.exe"


def test_sem_bash_em_lugar_nenhum_o_degrau_e_ausente(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "vazio"))
    monkeypatch.delenv("ProgramFiles", raising=False)
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.setattr(shell.shutil, "which", lambda n: None)
    assert shell.sondar(shell.BASH)[1] == shell.AUSENTE


def test_powershell_executa_e_verdadeiro_com_qualquer_das_duas_familias():
    assert shell.powershell_executa(sonda=_sonda_falsa({shell.PWSH: shell.EXECUTOU}))
    assert shell.powershell_executa(sonda=_sonda_falsa({shell.POWERSHELL: shell.EXECUTOU}))


def test_powershell_executa_e_falso_quando_as_duas_sao_recusadas():
    sonda = _sonda_falsa({shell.PWSH: shell.RECUSADO,
                          shell.POWERSHELL: shell.RECUSADO,
                          shell.BASH: shell.EXECUTOU})
    assert not shell.powershell_executa(sonda=sonda)


def test_diagnostico_devolve_o_motivo_de_cada_degrau():
    sonda = _sonda_falsa({shell.PWSH: shell.RECUSADO, shell.BASH: shell.EXECUTOU})
    estados = {d.nome: d.estado for d in shell.diagnostico(shell.ESCADA, sonda=sonda)}
    assert estados == {shell.PWSH: shell.RECUSADO,
                       shell.POWERSHELL: shell.AUSENTE,
                       shell.BASH: shell.EXECUTOU,
                       shell.CMD: shell.AUSENTE}
