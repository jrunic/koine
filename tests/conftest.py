import os

import pytest
from tests.fixtures import seed


@pytest.fixture(autouse=True)
def _isola_xdg(monkeypatch):
    # Runners CI (GitHub Actions ubuntu) exportam XDG_CONFIG_HOME etc.
    # paths.py e o oráculo Go honram XDG_* ANTES de HOME; sem esta limpeza,
    # XDG_* herdado vaza para o processo do teste e para todo subprocesso
    # montado com {**os.environ, "HOME": <fixture>}, resolvendo config no
    # HOME real do runner em vez do HOME isolado. Testes que precisam de
    # XDG_* setam explicitamente via monkeypatch (roda após esta fixture).
    for k in list(os.environ):
        if k.startswith("XDG_"):
            monkeypatch.delenv(k, raising=False)


@pytest.fixture
def koine_home(tmp_path):
    return seed.montar(str(tmp_path))
