"""As decisões do `instalar` cabem na linha de comando.

O modo era **inferido** por `sys.stdin.isatty()`, e inferência é o que produz o
estrago: rodar o `instalar` de automação DENTRO de um terminal interativo faz o
comando parar num prompt e ficar pendurado sem erro. O contorno era `< NUL`, que
é obscuro e específico de plataforma.
"""
import os

import pytest

from koine import cli


def _vault(koine_home):
    """O vault do repo, que é o que o `instalar` extrai."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault")


def _instalar(koine_home, monkeypatch, *args, tty=True):
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("sys.stdin.isatty", lambda: tty)
    bindir = os.path.join(koine_home["home"], "bin")
    return cli.main(["instalar", "--vault", _vault(koine_home), "--bin", bindir,
                     "--pyz", os.path.join(koine_home["home"], "koine.pyz"), *args])


def test_nao_interativo_vence_o_isatty(koine_home, monkeypatch, capsys):
    """A flag decide, o terminal não. Sem ela, com `isatty` verdadeiro, o
    comando pararia no prompt da pasta canônica — e é assim que automação
    trava."""
    def explode():
        raise AssertionError("leu stdin: o modo interativo não foi desligado")
    monkeypatch.setattr("sys.stdin.readline", explode)

    assert _instalar(koine_home, monkeypatch, "--nao-interativo", tty=True) == 0
    assert "modo não-interativo" in capsys.readouterr().out


def test_pasta_canonica_por_flag_nao_pergunta(koine_home, monkeypatch, capsys):
    def explode():
        raise AssertionError("perguntou a pasta canônica tendo recebido a flag")
    monkeypatch.setattr("sys.stdin.readline", explode)
    alvo = os.path.join(koine_home["home"], "minha-pasta")

    assert _instalar(koine_home, monkeypatch, "--pasta-canonica", alvo,
                     "--nao-interativo", tty=True) == 0

    assert os.path.isdir(alvo)
    assert alvo in capsys.readouterr().out


def test_contexto_canonico_sobrescrever(koine_home, monkeypatch):
    """Sem a flag, CONTEXTO.md divergente é preservado no não-interativo — e não
    havia como pedir a atualização sem um humano no teclado."""
    import pathlib
    alvo = os.path.join(koine_home["home"], "canon")
    os.makedirs(alvo, exist_ok=True)
    ctx = pathlib.Path(alvo, "CONTEXTO.md")
    ctx.write_text("---\nbootstrap: true\n---\n\n# meu, divergente\n", encoding="utf-8")

    assert _instalar(koine_home, monkeypatch, "--pasta-canonica", alvo,
                     "--contexto-canonico", "sobrescrever", "--nao-interativo") == 0

    assert "# meu, divergente" not in ctx.read_text(encoding="utf-8")


def test_contexto_canonico_preservar_em_terminal_interativo(koine_home, monkeypatch):
    """O outro lado: com TTY, sem a flag, isto seria um prompt."""
    import pathlib
    def explode():
        raise AssertionError("perguntou tendo recebido a flag")
    monkeypatch.setattr("sys.stdin.readline", explode)
    alvo = os.path.join(koine_home["home"], "canon2")
    os.makedirs(alvo, exist_ok=True)
    ctx = pathlib.Path(alvo, "CONTEXTO.md")
    ctx.write_text("---\nbootstrap: true\n---\n\n# meu, divergente\n", encoding="utf-8")

    assert _instalar(koine_home, monkeypatch, "--pasta-canonica", alvo,
                     "--contexto-canonico", "preservar", "--para", "nenhum",
                     tty=True) == 0

    assert "# meu, divergente" in ctx.read_text(encoding="utf-8")


def test_para_nenhum_nao_instala_skill_nem_pergunta(koine_home, monkeypatch, capsys):
    def explode():
        raise AssertionError("perguntou sobre harness tendo recebido --para nenhum")
    monkeypatch.setattr("sys.stdin.readline", explode)
    monkeypatch.setattr("koine.skills.detectar_harnesses", lambda: ["claude", "codex"])

    assert _instalar(koine_home, monkeypatch, "--para", "nenhum",
                     "--pasta-canonica", os.path.join(koine_home["home"], "canon3"),
                     tty=True) == 0

    saida = capsys.readouterr()
    assert not os.path.exists(os.path.join(koine_home["home"], ".claude", "skills"))
    # o pulo tem que ser DELIBERADO: sem esta asserção, um `nenhum` que cai no
    # ramo de harness desconhecido também "não instala" — mas avisando que o
    # harness não existe, que é conselho errado para quem pediu para pular
    assert "Pulado por --para nenhum" in saida.out
    assert "aviso: skills" not in saida.err


def test_para_todos_instala_em_todos_os_detectados(koine_home, monkeypatch):
    def explode():
        raise AssertionError("perguntou tendo recebido --para todos")
    monkeypatch.setattr("sys.stdin.readline", explode)
    monkeypatch.setattr("koine.skills.detectar_harnesses", lambda: ["claude", "codex"])

    assert _instalar(koine_home, monkeypatch, "--para", "todos",
                     "--pasta-canonica", os.path.join(koine_home["home"], "canon4"),
                     tty=True) == 0

    assert os.path.isdir(os.path.join(koine_home["home"], ".claude", "skills"))
    assert os.path.isdir(os.path.join(koine_home["home"], ".agents", "skills"))


def test_para_desconhecido_falha_alto(koine_home, monkeypatch, capsys):
    """Valor errado não pode virar 'nenhum harness' em silêncio."""
    assert _instalar(koine_home, monkeypatch, "--para", "inexistente",
                     "--nao-interativo") == 1
    assert "inexistente" in capsys.readouterr().err
