import io
import os

import pytest

from koine import aliases, canonica


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    home = tmp_path / "home"; os.makedirs(home)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    vault = tmp_path / "vault"; os.makedirs(vault / "bootstrap")
    (vault / "bootstrap" / "CONTEXTO.md").write_text(
        "---\nbootstrap: true\n---\n\n# CONTEXTO.md\nEmbed v2.\n", encoding="utf-8")
    return str(home), str(vault)


def test_interativo_prompt_default(ambiente, monkeypatch, capsys):
    home, vault = ambiente
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))          # aceita default
    p = canonica.configurar(vault, interativo=True)
    assert p == os.path.join(home, "koine")
    assert "Onde fica sua pasta canônica para sessões com Hermes? [~/koine]: " \
        in capsys.readouterr().out


def test_interativo_path_customizado_com_til(ambiente, monkeypatch):
    home, vault = ambiente
    monkeypatch.setattr("sys.stdin", io.StringIO("~/sessoes\n"))
    p = canonica.configurar(vault, interativo=True)
    assert p == os.path.join(home, "sessoes")
    assert os.path.isdir(p) and os.path.exists(os.path.join(p, "CONTEXTO.md"))


def test_nao_interativo_informa_default(ambiente, capsys):
    home, vault = ambiente
    canonica.configurar(vault, interativo=False)
    assert "Pasta canônica: ~/koine (default, modo não-interativo)" in capsys.readouterr().out


def test_alias_ja_correto(ambiente, capsys):
    home, vault = ambiente
    aliases.adicionar("koine", "koine", "home")
    canonica.configurar(vault, interativo=False)
    assert "✓ Alias 'koine' já está correto" in capsys.readouterr().out


def test_alias_divergente_mantem_com_aviso(ambiente, capsys):
    home, vault = ambiente
    aliases.adicionar("koine", "outra", "home")
    canonica.configurar(vault, interativo=False)
    err = capsys.readouterr().err
    assert "aviso: alias 'koine' já aponta para" in err and "mantendo" in err
    assert aliases.carregar()["pastas"]["koine"]["path"] == "outra"


def test_contexto_identico_informa(ambiente, capsys):
    home, vault = ambiente
    canonica.configurar(vault, interativo=False)
    canonica.configurar(vault, interativo=False)                  # 2ª rodada: idêntico
    assert "✓ CONTEXTO.md já está em modo bootstrap (idêntico ao embed)" \
        in capsys.readouterr().out


def test_contexto_divergente_nao_interativo_preserva(ambiente, capsys):
    home, vault = ambiente
    canonica.configurar(vault, interativo=False)
    destino = os.path.join(home, "koine", "CONTEXTO.md")
    with open(destino, "a", encoding="utf-8") as f:
        f.write("\ncustom\n")
    canonica.configurar(vault, interativo=False)
    assert "preservando" in capsys.readouterr().err
    assert "custom" in open(destino, encoding="utf-8").read()


def test_contexto_bootstrap_divergente_interativo_atualiza_default(ambiente, monkeypatch, capsys):
    home, vault = ambiente
    canonica.configurar(vault, interativo=False)
    destino = os.path.join(home, "koine", "CONTEXTO.md")
    with open(destino, "a", encoding="utf-8") as f:
        f.write("\nvelho\n")                                       # ainda tem bootstrap: true
    monkeypatch.setattr("sys.stdin", io.StringIO("\n\n"))          # prompt pasta + prompt Y/n
    canonica.configurar(vault, interativo=True)
    assert "Atualizar? [Y/n]" in capsys.readouterr().out
    assert "velho" not in open(destino, encoding="utf-8").read()


def test_contexto_personalizado_interativo_default_preserva(ambiente, monkeypatch, capsys):
    home, vault = ambiente
    os.makedirs(os.path.join(home, "koine"))
    destino = os.path.join(home, "koine", "CONTEXTO.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("---\ntype: contexto\n---\n# Meu\n")
    monkeypatch.setattr("sys.stdin", io.StringIO("\n\n"))
    canonica.configurar(vault, interativo=True)
    out = capsys.readouterr().out
    assert "Sobrescrever com versão bootstrap? [y/N]" in out
    assert "✓ CONTEXTO.md preservado" in out
    assert "# Meu" in open(destino, encoding="utf-8").read()
