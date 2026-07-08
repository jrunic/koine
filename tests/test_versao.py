import os
import re

import pytest

from koine._version import __version__

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_versao_unica_pyproject_e_pacote():
    src = open(os.path.join(REPO, "pyproject.toml"), encoding="utf-8").read()
    m = re.search(r'^version = "([^"]+)"$', src, re.M)
    assert m, "pyproject.toml sem campo version"
    assert m.group(1) == __version__


def test_changelog_tem_secao_da_versao_de_release():
    # espelho local do gate do workflow (awk sobre `## [<versao>]`)
    if "-" in __version__:
        pytest.skip("versão de desenvolvimento — gate só vale para release")
    log = open(os.path.join(REPO, "CHANGELOG.md"), encoding="utf-8").read()
    assert f"## [{__version__}]" in log
