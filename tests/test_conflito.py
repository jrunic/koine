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
