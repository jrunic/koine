import json
import os
from koine import aliases, canonica
from tests import _parity

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = os.path.join(REPO, "vault")


def test_pasta_canonica_bate_com_go(tmp_path, monkeypatch):
    # Go: instalar não-interativo cria ~/koine + alias
    home_go = str(tmp_path / "go"); os.makedirs(home_go)
    _parity.instalar_go(home_go)

    # Python: configura a pasta canônica (vault_src = repo vault/)
    home_py = str(tmp_path / "py"); os.makedirs(home_py)
    monkeypatch.setenv("HOME", home_py)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    canonica.configurar(VAULT)

    # CONTEXTO.md byte-idêntico
    go_ctx = open(os.path.join(home_go, "koine", "CONTEXTO.md"), encoding="utf-8").read()
    py_ctx = open(os.path.join(home_py, "koine", "CONTEXTO.md"), encoding="utf-8").read()
    assert py_ctx == go_ctx

    # alias 'koine' equivalente (JSON parseado, não byte — Go ordena chaves de map)
    go_al = json.load(open(os.path.join(home_go, ".config/koine/aliases.json")))
    py_al = json.load(open(os.path.join(home_py, ".config/koine/aliases.json")))
    assert py_al["pastas"]["koine"] == go_al["pastas"]["koine"] == {"path": "koine", "from": "home"}
