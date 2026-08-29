"""O `instalar` diz o que vai — e o que não vai — funcionar nesta máquina.

O problema aparece na PRIMEIRA SESSÃO, não na instalação: numa estação que nega
o PowerShell, copilot, codex e agy sobem e não executam comando nenhum. A
instalação é onde o usuário ainda está prestando atenção.
"""
import os

from koine import cli, prerequisitos, shell, skills


def _sonda(mapa):
    def s(nome):
        return nome, mapa.get(nome, shell.AUSENTE)
    return s


NEGADO = {shell.PWSH: shell.RECUSADO, shell.POWERSHELL: shell.RECUSADO,
          shell.BASH: shell.EXECUTOU, shell.CMD: shell.EXECUTOU}


def _vault():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault")


def _sem_codex(monkeypatch):
    """Forçar `sys.platform="win32"` no macOS faz o `shutil.which` entrar no ramo
    Windows e estourar em `_winapi`. Quem chama o which direto aqui é o
    `codex_dir`; nos testes ele responde "não achei", que é a verdade nesta
    máquina. Sem isto o teste morre por artefato de harness, não por defeito."""
    monkeypatch.setattr(prerequisitos.shutil, "which", lambda n: None)


def _instalar(koine_home, monkeypatch):
    _sem_codex(monkeypatch)
    monkeypatch.setenv("HOME", koine_home["home"])
    bindir = os.path.join(koine_home["home"], "bin")
    return cli.main(["instalar", "--vault", _vault(), "--bin", bindir,
                     "--pyz", os.path.join(koine_home["home"], "koine.pyz"),
                     "--nao-interativo", "--para", "nenhum"])


def test_instalar_no_windows_imprime_o_relatorio(koine_home, monkeypatch, capsys):
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(shell, "sondar", _sonda(NEGADO))
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: ["copilot"])
    assert _instalar(koine_home, monkeypatch) == 0
    saida = capsys.readouterr().out
    assert "Pré-requisitos" in saida
    assert "copilot" in saida


def test_instalar_fora_do_windows_nao_imprime_nada_disso(koine_home, monkeypatch, capsys):
    monkeypatch.setattr(cli.sys, "platform", "darwin")
    assert _instalar(koine_home, monkeypatch) == 0
    assert "Pré-requisitos" not in capsys.readouterr().out


def test_o_relatorio_nao_bloqueia_o_install(koine_home, monkeypatch):
    # Relatório que trava a instalação é pior que relatório nenhum.
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(shell, "sondar", _sonda(NEGADO))
    monkeypatch.setattr(skills, "detectar_harnesses", lambda: ["copilot", "codex"])
    assert _instalar(koine_home, monkeypatch) == 0
