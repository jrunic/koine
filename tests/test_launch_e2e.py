import os
import subprocess
import sys
from tests.fixtures import seed, shim

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp):
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def test_launch_e2e_wrapper_lanca_claude_na_pasta(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    shimdir = str(tmp_path / "shim"); captura = str(tmp_path / "cap.txt")
    shim.instalar_shim(shimdir, "claude", captura)
    env = {**os.environ, "HOME": fx["home"], "PATH": shimdir + os.pathsep + os.environ["PATH"]}
    # o wrapper (pyz) gera CLAUDE.md e faz execvpe do shim `claude`
    r = subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0
    assert os.path.exists(os.path.join(fx["trab"], "CLAUDE.md"))   # gerou antes de lançar
    linhas = open(captura).read().splitlines()
    assert os.path.realpath(linhas[0]) == os.path.realpath(fx["trab"])  # cwd == pasta
    assert linhas[1:] == [""] or linhas[1:] == []                  # sem args extras p/ claude


def test_launch_e2e_cliente_ausente_falha_amigavel(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    # PATH sem `claude`
    env = {**os.environ, "HOME": fx["home"], "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                       env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert "não encontrado no PATH" in (r.stderr + r.stdout)
    assert os.path.exists(os.path.join(fx["trab"], "CLAUDE.md"))   # gerou mesmo sem lançar
