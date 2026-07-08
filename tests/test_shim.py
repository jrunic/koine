import os
import subprocess

from tests.fixtures import shim


def test_shim_sem_captura_env_preserva_comportamento(tmp_path):
    cap = str(tmp_path / "cap.txt")
    p = shim.instalar_shim(str(tmp_path / "bin"), "cli", cap)
    subprocess.run([p, "a", "b"], cwd=str(tmp_path), check=True)
    assert open(cap).read() == f"{tmp_path}\na\nb\n"


def test_shim_captura_env_opcional(tmp_path):
    cap = str(tmp_path / "cap.txt")
    capenv = str(tmp_path / "env.txt")
    p = shim.instalar_shim(str(tmp_path / "bin"), "cli", cap, captura_env=capenv)
    env = dict(os.environ, KOINE_TESTE_ENV="valor-x")
    subprocess.run([p, "a"], cwd=str(tmp_path), env=env, check=True)
    assert open(cap).read() == f"{tmp_path}\na\n"
    assert "KOINE_TESTE_ENV=valor-x" in open(capenv).read()
