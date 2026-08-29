"""O launch avisa quando o cliente que está subindo não tem shell aqui.

O relatório da instalação é lido uma vez; o problema acontece NA SESSÃO,
possivelmente meses depois. Avisa e NÃO bloqueia: a sessão sem shell ainda
entrega contexto e leitura de arquivos, e recusar a abrir tiraria do usuário
mais do que a política tirou.

Protocolo anti-trava do repo: teste in-process de launch EXIGE a costura em
`launch.lancar` — sem ela o `execvpe` mata o pytest.
"""
from koine import cli, launch, prerequisitos, shell


def _sonda(mapa):
    def s(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return s


# NEGADO tem bash: é a estação com Git Bash instalado.
NEGADO = {shell.PWSH: shell.RECUSADO, shell.POWERSHELL: shell.RECUSADO,
          shell.BASH: shell.EXECUTOU, shell.CMD: shell.EXECUTOU}
SEM_BASH = {shell.PWSH: shell.RECUSADO, shell.POWERSHELL: shell.RECUSADO,
            shell.CMD: shell.EXECUTOU}
SAUDAVEL = {shell.PWSH: shell.EXECUTOU, shell.CMD: shell.EXECUTOU}


def _preparar(koine_home, monkeypatch, mapa, plataforma="win32"):
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr(cli.sys, "platform", plataforma)
    monkeypatch.setattr(shell, "sondar", _sonda(mapa))
    # `sys.platform="win32"` no macOS faz o shutil.which entrar no ramo Windows
    # e estourar em _winapi; quem chama o which direto é o codex_dir.
    monkeypatch.setattr(prerequisitos.shutil, "which", lambda n: None)
    return koine_home["trab"]


def test_launch_de_cliente_sem_shell_avisa_e_SOBE(koine_home, monkeypatch, capsys):
    lancado = {}
    monkeypatch.setattr(launch, "lancar",
                        lambda c, p, **kw: lancado.setdefault("cliente", c))
    trab = _preparar(koine_home, monkeypatch, NEGADO)
    assert cli.main(["copilot", "hermes", trab]) == 0
    assert lancado["cliente"] == "copilot"     # não bloqueou
    assert "sem shell" in capsys.readouterr().err


def test_launch_de_cliente_com_shell_nao_avisa(koine_home, monkeypatch, capsys):
    monkeypatch.setattr(launch, "lancar", lambda c, p, **kw: None)
    trab = _preparar(koine_home, monkeypatch, SAUDAVEL)
    cli.main(["copilot", "hermes", trab])
    assert "sem shell" not in capsys.readouterr().err


def test_launch_do_claude_sem_git_bash_avisa_com_o_remedio(koine_home, monkeypatch, capsys):
    # O claude sem bash TAMBÉM não tem shell — e é o único caso com saída
    # acionável. A primeira redação do plano filtrava só o SEM_SHELL e deixava
    # este caso mudo, contra o critério da própria spec.
    monkeypatch.setattr(launch, "lancar", lambda c, p, **kw: None)
    trab = _preparar(koine_home, monkeypatch, SEM_BASH)
    assert cli.main(["claude", "hermes", trab]) == 0
    assert "Git Bash" in capsys.readouterr().err


def test_launch_do_claude_com_git_bash_nao_avisa(koine_home, monkeypatch, capsys):
    monkeypatch.setattr(launch, "lancar", lambda c, p, **kw: None)
    trab = _preparar(koine_home, monkeypatch, NEGADO)
    cli.main(["claude", "hermes", trab])
    assert "Git Bash" not in capsys.readouterr().err


def test_launch_fora_do_windows_nao_avisa(koine_home, monkeypatch, capsys):
    monkeypatch.setattr(launch, "lancar", lambda c, p, **kw: None)
    trab = _preparar(koine_home, monkeypatch, SEM_BASH, plataforma="darwin")
    cli.main(["copilot", "hermes", trab])
    err = capsys.readouterr().err
    assert "sem shell" not in err and "Git Bash" not in err
