"""O `instalar` põe a própria pasta no PATH do usuário, no Windows.

Até aqui o Koine avisava e mandava editar as variáveis de ambiente à mão — que é
onde a instalação morria para quem não é técnico.
"""
import os

from koine import cli, pathenv, prerequisitos


def _vault():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault")


def _instalar(koine_home, monkeypatch):
    # `sys.platform="win32"` no macOS faz o shutil.which entrar no ramo Windows e
    # estourar em _winapi; quem chama o which direto é o codex_dir.
    monkeypatch.setattr(prerequisitos.shutil, "which", lambda n: None)
    monkeypatch.setenv("HOME", koine_home["home"])
    bindir = os.path.join(koine_home["home"], "bin")
    return cli.main(["instalar", "--vault", _vault(), "--bin", bindir,
                     "--pyz", os.path.join(koine_home["home"], "koine.pyz"),
                     "--nao-interativo", "--para", "nenhum"])


def test_instalar_no_windows_garante_o_path(koine_home, monkeypatch, capsys):
    visto = {}
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(pathenv, "garantir",
                        lambda pasta, **kw: visto.setdefault("pasta", pasta) or pathenv.ADICIONADO)
    assert _instalar(koine_home, monkeypatch) == 0
    assert visto["pasta"].endswith("bin")           # a pasta do --bin, não outra
    assert "PATH" in capsys.readouterr().out


def test_instalar_fora_do_windows_nao_toca_no_path(koine_home, monkeypatch):
    chamou = []
    monkeypatch.setattr(cli.sys, "platform", "darwin")
    monkeypatch.setattr(pathenv, "garantir", lambda pasta, **kw: chamou.append(pasta))
    assert _instalar(koine_home, monkeypatch) == 0
    assert chamou == []


def test_escrita_negada_nao_derruba_a_instalacao(koine_home, monkeypatch, capsys):
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(pathenv, "garantir", lambda pasta, **kw: pathenv.FALHOU)
    assert _instalar(koine_home, monkeypatch) == 0   # termina normalmente
    assert "sysdm.cpl" in capsys.readouterr().out
