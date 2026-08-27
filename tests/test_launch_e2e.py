import os
import subprocess
import sys
from tests.fixtures import bundle, seed, shim

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
    # o wrapper (pyz) monta o bundle e faz execvpe do shim `claude`
    r = subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0
    # montou o bundle antes de lançar, e não sujou a pasta do usuário
    assert "Usuário de fixture." in bundle.conteudo("claude", fx["trab"], fx["home"])
    assert not os.path.exists(os.path.join(fx["trab"], "CLAUDE.md"))
    linhas = open(captura).read().splitlines()
    assert os.path.realpath(linhas[0]) == os.path.realpath(fx["trab"])  # cwd == pasta
    # os args do cliente agora carregam o canal do adapter
    assert linhas[1] == "--add-dir"


def test_launch_e2e_cliente_ausente_falha_amigavel(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    # PATH sem `claude`
    env = {**os.environ, "HOME": fx["home"], "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                       env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert "não encontrado no PATH" in (r.stderr + r.stdout)
    # montou o bundle mesmo sem conseguir lançar
    assert "Usuário de fixture." in bundle.conteudo("claude", fx["trab"], fx["home"])
