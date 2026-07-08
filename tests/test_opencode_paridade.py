import json
import os
import subprocess
import sys

import pytest

from koine.cache import slot_id
from tests import _parity
from tests.fixtures import seed, shim

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp) -> str:
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def _env_var(dump: str, nome: str) -> list:
    return [l for l in dump.splitlines() if l.startswith(nome + "=")]


def _env_py(home: str, shimdir: str) -> dict:
    # XDG_* herdado desviaria paths.cache_dir() do <home>/.cache do teste
    env = {k: v for k, v in os.environ.items() if not k.startswith("XDG_")}
    env.update(HOME=home, PATH=shimdir + os.pathsep + os.environ["PATH"])
    return env


@pytest.mark.skipif(sys.platform == "win32", reason="readlink")
def test_opencode_config_bate_com_go(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    home = fx["home"]
    trab = fx["trab"]
    cfg_path = os.path.join(home, ".cache", "koine", "opencode-configs",
                            slot_id(trab) + ".json")
    link = os.path.join(trab, "AGENTS.md")
    shimdir = str(tmp_path / "shim")
    capenv = str(tmp_path / "env.txt")
    shim.instalar_shim(shimdir, "opencode", str(tmp_path / "cap.txt"),
                       captura_env=capenv)
    snapshot_trab = sorted(os.listdir(trab))
    # Go via kn-opencode
    _parity.rodar_wrapper_go("opencode", trab, "hermes", home, shimdir)
    cfg_go = open(cfg_path, encoding="utf-8").read()
    alvo_go = os.readlink(link)
    env_go = open(capenv).read()  # salvar ANTES do rerun Python (o shim sobrescreve)
    os.remove(cfg_path)
    os.remove(link)
    # Python via `koine opencode`
    r = subprocess.run([sys.executable, pyz, "opencode", "hermes", trab],
                       env=_env_py(home, shimdir),
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    cfg_py = open(cfg_path, encoding="utf-8").read()
    assert cfg_py == cfg_go  # JSON byte-idêntico (config não tem timestamp)
    assert json.loads(cfg_py)["$schema"] == "https://opencode.ai/config.json"
    assert os.readlink(link) == alvo_go == os.path.join(trab, "CONTEXTO.md")
    env_py = open(capenv).read()
    assert _env_var(env_py, "OPENCODE_CONFIG") == \
           _env_var(env_go, "OPENCODE_CONFIG") == \
           [f"OPENCODE_CONFIG={cfg_path}"]
    assert _env_var(env_py, "OPENCODE_DISABLE_CLAUDE_CODE") == \
           _env_var(env_go, "OPENCODE_DISABLE_CLAUDE_CODE") == \
           ["OPENCODE_DISABLE_CLAUDE_CODE=1"]
    # working dir: só o symlink AGENTS.md apareceu
    assert sorted(os.listdir(trab)) == sorted(snapshot_trab + ["AGENTS.md"])


def test_opencode_bootstrap_bate_com_go(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    home = fx["home"]
    # pasta NOVA com CONTEXTO bootstrap — não muta o trab semeado
    trab = os.path.join(home, "koine")
    os.makedirs(trab, exist_ok=True)
    with open(os.path.join(trab, "CONTEXTO.md"), "w", encoding="utf-8") as f:
        f.write("---\nbootstrap: true\n---\n\n# Bootstrap\n")
    cfg_path = os.path.join(home, ".cache", "koine", "opencode-configs",
                            slot_id(trab) + ".json")
    link = os.path.join(trab, "AGENTS.md")
    shimdir = str(tmp_path / "shimb")
    shim.instalar_shim(shimdir, "opencode", str(tmp_path / "capb.txt"))
    # Go
    _parity.rodar_wrapper_go("opencode", trab, "hermes", home, shimdir)
    cfg_go = open(cfg_path, encoding="utf-8").read()
    assert not os.path.lexists(link)  # bootstrap: sem symlink
    os.remove(cfg_path)
    # Python
    r = subprocess.run([sys.executable, pyz, "opencode", "hermes", trab],
                       env=_env_py(home, shimdir),
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert open(cfg_path, encoding="utf-8").read() == cfg_go
    assert not os.path.lexists(link)
    instructions = json.loads(cfg_go)["instructions"]
    assert instructions[-1].endswith("CONTEXTO.md")  # contexto direto em instructions


def test_instalar_emite_wrapper_kn_opencode(tmp_path):
    pyz = _build(tmp_path)
    home = str(tmp_path / "home")
    os.makedirs(home)
    bindir = os.path.join(home, "bin")
    subprocess.run([sys.executable, pyz, "instalar", "--bin", bindir, "--pyz", pyz],
                   env={"HOME": home, "PATH": "/usr/bin:/bin"},
                   check=True, capture_output=True, text=True)
    assert os.path.exists(os.path.join(bindir, "kn-opencode"))
