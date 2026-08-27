import os

import pytest

from koine import escrita

MARCADOR = "<!-- gerado por kn-agente -->"


def test_arquivo_nosso_e_reconhecido(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text(MARCADOR + "\n# CLAUDE.md\n")
    assert escrita.e_nosso(str(p)) is True


def test_arquivo_com_assinatura_retrocompat_e_nosso(tmp_path):
    """Gerado pré-Fase-3 do Go: sem o marcador HTML, com a assinatura do
    template. Deixar de reconhecê-lo encheria a pasta de .bak."""
    p = tmp_path / "CLAUDE.md"
    p.write_text("# CLAUDE.md\n\nRegerar: `kn-agente hermes`\n")
    assert escrita.e_nosso(str(p)) is True


def test_arquivo_do_usuario_nao_e_nosso(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text("# minhas instruções\n")
    assert escrita.e_nosso(str(p)) is False


def test_arquivo_inexistente_nao_e_nosso(tmp_path):
    assert escrita.e_nosso(str(tmp_path / "nao-existe.md")) is False


def test_gravar_sobre_arquivo_do_usuario_faz_backup(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text("conteudo do usuario\n")

    escrita.gravar(str(p), "conteudo novo\n")

    assert p.read_text() == "conteudo novo\n"
    assert (tmp_path / "CLAUDE.md.bak").read_text() == "conteudo do usuario\n"


def test_backup_nao_sobrescreve_backup_anterior(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text("primeiro do usuario\n")
    escrita.gravar(str(p), "gerado 1\n")
    p.write_text("segundo do usuario\n")

    escrita.gravar(str(p), "gerado 2\n")

    assert (tmp_path / "CLAUDE.md.bak").read_text() == "primeiro do usuario\n"
    assert (tmp_path / "CLAUDE.md.bak.1").read_text() == "segundo do usuario\n"


def test_gravar_sobre_arquivo_nosso_nao_faz_backup(tmp_path):
    """Regeneração idempotente não pode encher a pasta de .bak."""
    p = tmp_path / "CLAUDE.md"
    p.write_text(MARCADOR + "\nvelho\n")

    escrita.gravar(str(p), MARCADOR + "\nnovo\n")

    assert not (tmp_path / "CLAUDE.md.bak").exists()
    assert p.read_text() == MARCADOR + "\nnovo\n"


def test_gravar_recusa_symlink(tmp_path):
    """Escrever atravessaria o symlink e destruiria o alvo — foi o bug latente
    corrigido nos wrappers da v0.4.0 e o guard do cruzamento codex↔opencode."""
    real = tmp_path / "real.md"
    real.write_text("do usuario\n")
    link = tmp_path / "CLAUDE.md"
    os.symlink(str(real), str(link))

    with pytest.raises(escrita.ConflitoErro):
        escrita.gravar(str(link), "novo\n")
    assert real.read_text() == "do usuario\n"


def test_gravar_recusa_diretorio(tmp_path):
    d = tmp_path / "CLAUDE.md"
    d.mkdir()
    with pytest.raises(escrita.ConflitoErro):
        escrita.gravar(str(d), "novo\n")


def test_gravar_cria_arquivo_novo_sem_backup(tmp_path):
    p = tmp_path / "CLAUDE.md"
    escrita.gravar(str(p), "novo\n")
    assert p.read_text() == "novo\n"
    assert sorted(os.listdir(tmp_path)) == ["CLAUDE.md"]


def test_arquivo_temporario_nunca_fica_na_pasta(tmp_path, monkeypatch):
    """Critério 7 da spec: escrita interrompida não deixa resíduo visível."""
    p = tmp_path / "CLAUDE.md"

    def explode(*a, **k):
        raise OSError("disco cheio")
    monkeypatch.setattr(escrita.os, "replace", explode)

    with pytest.raises(OSError):
        escrita.gravar(str(p), "novo\n")

    assert sorted(os.listdir(tmp_path)) == [], "sobrou resíduo na pasta"


def test_conflito_delega_para_escrita(tmp_path):
    """`conflito.py` continua sendo a porta do Go, mas a política é uma só:
    quem responde 'isto é meu?' passa a ser `escrita`. Sem isto, a divergência
    entre as duas superfícies volta pela porta dos fundos."""
    from koine import conflito
    assert conflito.ConflitoErro is escrita.ConflitoErro
    assert conflito.MARCADOR_KOINE == escrita.MARCADOR_KOINE


def test_arquivo_nosso_no_caminho_do_symlink_cede_o_lugar(tmp_path):
    """Caso real do cruzamento codex→opencode: o `kn-codex` deixa um AGENTS.md
    regular COM o nosso marcador, e a sessão seguinte precisa de um symlink no
    mesmo caminho. O arquivo tem que sair — no `gravar` ele seria apenas
    sobrescrito, mas aqui quem vai ocupar o lugar é um symlink, e `os.symlink`
    sobre arquivo existente estoura FileExistsError.

    Este é o ramo que a delegação por descuido apagaria: `preservar` pula o que
    é nosso, e pular aqui trocaria backup por quebra do launch."""
    from koine import conflito
    alvo = tmp_path / "CONTEXTO.md"
    alvo.write_text("# C\n")
    p = tmp_path / "AGENTS.md"
    p.write_text(MARCADOR + "\n# AGENTS.md\n")

    conflito.resolver_symlink_conflito(str(p), str(alvo))

    assert not p.exists(), "o caminho continua ocupado — os.symlink vai estourar"
