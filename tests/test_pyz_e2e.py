import os
import subprocess
import sys
from tests import _parity
from tests.fixtures import seed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp) -> str:
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def test_pyz_versao(tmp_path):
    pyz = _build(tmp_path)
    r = subprocess.run([sys.executable, pyz, "versao"], capture_output=True, text=True, check=True)
    assert "koine" in r.stdout.lower()


def test_pyz_sem_codigo_nativo(tmp_path):
    # restrição-âncora do port: nada de .pyd/.so/.dll cruza o AV do Aldo.
    import zipfile
    pyz = _build(tmp_path)
    with zipfile.ZipFile(pyz) as z:
        nativos = [n for n in z.namelist() if n.endswith((".pyd", ".so", ".dll"))]
    assert nativos == [], f"pyz carrega código nativo: {nativos}"


def test_pyz_claude_paridade(tmp_path, monkeypatch):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    go = _parity.gerar_go(fx["trab"], "hermes", fx["home"])
    os.remove(os.path.join(fx["trab"], "CLAUDE.md"))
    subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                   env={**os.environ, "HOME": fx["home"]}, check=True, capture_output=True, text=True)
    py = open(os.path.join(fx["trab"], "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)
