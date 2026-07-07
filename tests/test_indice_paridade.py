import os

from koine import indice
from tests import _parity


def test_indice_bate_com_go(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    # 1. Go gera os índices (efeito de `gerar`)
    _parity.gerar_go(koine_home["trab"], "hermes", koine_home["home"])
    go_idx = _ler(os.path.join(koine_home["refs"], "kn-indice-tecnologia.md"))

    # 2. Python gera o índice na mesma pasta-referências
    os.remove(os.path.join(koine_home["refs"], "kn-indice-tecnologia.md"))
    indice.gerar(koine_home["refs"], ["tecnologia"])
    py_idx = _ler(os.path.join(koine_home["refs"], "kn-indice-tecnologia.md"))

    assert _parity.normalize(py_idx) == _parity.normalize(go_idx)


def _ler(p):
    return open(p, encoding="utf-8").read()
