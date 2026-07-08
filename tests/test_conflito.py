import os
import sys

import pytest

from koine import conflito


def test_symlink_nao_existe_ok(tmp_path):
    conflito.resolver_symlink_conflito(str(tmp_path / "l"), "/alvo")  # não levanta


@pytest.mark.skipif(sys.platform == "win32", reason="symlink")
def test_symlink_alvo_correto_noop(tmp_path):
    link = str(tmp_path / "l"); os.symlink("/alvo", link)
    conflito.resolver_symlink_conflito(link, "/alvo")  # no-op, não levanta


@pytest.mark.skipif(sys.platform == "win32", reason="symlink")
def test_symlink_alvo_divergente_erro(tmp_path):
    link = str(tmp_path / "l"); os.symlink("/outro", link)
    with pytest.raises(conflito.ConflitoErro):
        conflito.resolver_symlink_conflito(link, "/alvo")


def test_arquivo_regular_vira_bak_com_aviso(tmp_path, capsys):
    p = str(tmp_path / "l"); open(p, "w").write("do usuário")
    conflito.resolver_symlink_conflito(p, "/alvo")
    assert not os.path.exists(p)
    assert open(p + ".bak").read() == "do usuário"
    assert "salvo como" in capsys.readouterr().err


def test_bak_nunca_sobrescreve_bak(tmp_path):
    p = str(tmp_path / "l"); open(p, "w").write("v2"); open(p + ".bak", "w").write("v1")
    conflito.resolver_symlink_conflito(p, "/alvo")
    assert open(p + ".bak").read() == "v1" and open(p + ".bak.1").read() == "v2"


def test_diretorio_erro(tmp_path):
    d = str(tmp_path / "l"); os.makedirs(d)
    with pytest.raises(conflito.ConflitoErro):
        conflito.resolver_symlink_conflito(d, "/alvo")


@pytest.mark.skipif(sys.platform == "win32", reason="symlink")
def test_arquivo_conflito_symlink_erro_preserva_alvo(tmp_path):
    alvo = tmp_path / "CONTEXTO.md"; alvo.write_text("do usuário")
    p = str(tmp_path / "AGENTS.md"); os.symlink(str(alvo), p)
    with pytest.raises(conflito.ConflitoErro):
        conflito.resolver_arquivo_conflito(p)
    assert alvo.read_text() == "do usuário"  # nada escreveu através do symlink


def test_arquivo_conflito_diretorio_erro(tmp_path):
    d = str(tmp_path / "AGENTS.md"); os.makedirs(d)
    with pytest.raises(conflito.ConflitoErro):
        conflito.resolver_arquivo_conflito(d)


def test_arquivo_conflito_ausente_ok(tmp_path):
    conflito.resolver_arquivo_conflito(str(tmp_path / "novo.md"))  # não existe → OK


def test_arquivo_com_marcador_koine_regenera_sem_bak(tmp_path):
    p = tmp_path / "CLAUDE.md"
    p.write_text(conflito.MARCADOR_KOINE + "\n# CLAUDE.md\ncorpo\n")
    conflito.resolver_arquivo_conflito(str(p))       # não levanta
    assert p.read_text().startswith(conflito.MARCADOR_KOINE)  # intocado
    assert not os.path.exists(str(p) + ".bak")       # e não faz backup


def test_arquivo_assinatura_retrocompat_regenera_sem_bak(tmp_path):
    # CLAUDE.md/GEMINI.md gerados pré-Fase-3 do Go: sem marcador HTML, com a
    # assinatura do template (conflito.go:139-140)
    p = tmp_path / "CLAUDE.md"
    p.write_text("# CLAUDE.md\n*Gerado em 2026-06-20. Regerar: `kn-agente hermes .`*\n")
    conflito.resolver_arquivo_conflito(str(p))
    assert not os.path.exists(str(p) + ".bak")


def test_arquivo_sem_marcador_vira_bak_com_aviso(tmp_path, capsys):
    p = tmp_path / "AGENTS.md"
    p.write_text("conteúdo do usuário")
    conflito.resolver_arquivo_conflito(str(p))
    assert not os.path.exists(str(p))
    assert (tmp_path / "AGENTS.md.bak").read_text() == "conteúdo do usuário"
    assert "salvo como" in capsys.readouterr().err


def test_arquivo_bak_nunca_sobrescreve_bak(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text("v2")
    (tmp_path / "AGENTS.md.bak").write_text("v1")
    conflito.resolver_arquivo_conflito(str(p))
    assert (tmp_path / "AGENTS.md.bak").read_text() == "v1"
    assert (tmp_path / "AGENTS.md.bak.1").read_text() == "v2"


def test_materializar_faz_backup_de_arquivo_do_usuario(tmp_path, capsys):
    # integração no fluxo de wrapper: _materializar preserva o arquivo do
    # usuário em .bak e escreve o novo (gerar/mostrar ficam FORA — paridade Go)
    from koine import cli
    from koine.lancamento import Lancamento
    (tmp_path / "CLAUDE.md").write_text("anotações do usuário")
    lanc = Lancamento(arquivos_working_dir={
        "CLAUDE.md": conflito.MARCADOR_KOINE + "\n# novo\n"})
    cli._materializar(lanc, str(tmp_path))
    assert (tmp_path / "CLAUDE.md.bak").read_text() == "anotações do usuário"
    assert (tmp_path / "CLAUDE.md").read_text().startswith(conflito.MARCADOR_KOINE)
    assert "salvo como" in capsys.readouterr().err


def test_arquivo_gerado_pelo_go_regenera_sem_bak(koine_home):
    # idempotência cruzada: CLAUDE.md nascido do ORÁCULO Go é reconhecido pelo
    # marker-check do Python — regenera sem .bak
    from tests import _parity
    fx = koine_home
    _parity.gerar_go(fx["trab"], "hermes", fx["home"])
    p = os.path.join(fx["trab"], "CLAUDE.md")
    conflito.resolver_arquivo_conflito(p)
    assert os.path.exists(p)
    assert not os.path.exists(p + ".bak")
