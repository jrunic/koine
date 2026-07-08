import os

from koine import cli, conflito


def test_fixture_gera_claude_md_valido(koine_home, monkeypatch):
    # self-test da fixture: o HOME semeado por seed.montar sustenta uma geração
    # completa (usuário + escopo + domínio + refs + CONTEXTO.md)
    monkeypatch.setenv("HOME", koine_home["home"])
    rc = cli.main(["gerar", "hermes", koine_home["trab"]])
    assert rc == 0
    out = open(os.path.join(koine_home["trab"], "CLAUDE.md"), encoding="utf-8").read()
    assert out.startswith(conflito.MARCADOR_KOINE)
    assert "@" in out  # tem linhas @path
