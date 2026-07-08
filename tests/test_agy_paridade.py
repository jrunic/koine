import os
import subprocess
import sys

from tests import _parity
from tests.fixtures import seed, shim

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp) -> str:
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def test_agy_gemini_bate_com_go(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    home = fx["home"]
    trab = fx["trab"]
    shimdir = str(tmp_path / "shim")
    shim.instalar_shim(shimdir, "agy", str(tmp_path / "cap.txt"))
    # Go via kn-agy
    go = _parity.gerar_agy_go(trab, "hermes", home, shimdir)
    os.remove(os.path.join(trab, "GEMINI.md"))
    # Python via `koine agy` (subprocesso; shim `agy` PREPENDADO senão trava)
    path = shimdir + os.pathsep + os.environ["PATH"]
    r = subprocess.run([sys.executable, pyz, "agy", "hermes", trab],
                       env={**os.environ, "HOME": home, "PATH": path},
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    py = open(os.path.join(trab, "GEMINI.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)


def test_agy_gemini_bootstrap_bate_com_go(tmp_path):
    # cobre o ramo bootstrap do antigravity com byte-paridade (não só o unit).
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    home = fx["home"]
    canon = os.path.join(home, "koine")
    os.makedirs(canon, exist_ok=True)
    with open(os.path.join(canon, "CONTEXTO.md"), "w") as f:
        f.write("---\nbootstrap: true\n---\n\n# Bootstrap\n")
    shimdir = str(tmp_path / "shimb")
    shim.instalar_shim(shimdir, "agy", str(tmp_path / "capb.txt"))
    go = _parity.gerar_agy_go(canon, "hermes", home, shimdir)
    os.remove(os.path.join(canon, "GEMINI.md"))
    path = shimdir + os.pathsep + os.environ["PATH"]
    r = subprocess.run([sys.executable, pyz, "agy", "hermes", canon],
                       env={**os.environ, "HOME": home, "PATH": path},
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    py = open(os.path.join(canon, "GEMINI.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)


def test_instalar_emite_wrapper_kn_agy(tmp_path):
    pyz = _build(tmp_path)
    home = str(tmp_path / "home")
    os.makedirs(home)
    bindir = os.path.join(home, "bin")
    subprocess.run([sys.executable, pyz, "instalar", "--bin", bindir, "--pyz", pyz],
                   env={"HOME": home, "PATH": "/usr/bin:/bin"},
                   check=True, capture_output=True, text=True)
    assert os.path.exists(os.path.join(bindir, "kn-agy"))       # REGISTRY auto-emite
    assert os.path.exists(os.path.join(bindir, "kn-claude"))
