import os
import shutil
import subprocess
import sys

import pytest

from koine import cache
from koine.adapters import copilot
from koine.contexto import ContextoMontado
from tests import _parity
from tests.fixtures import seed, shim

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp) -> str:
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def _slot(p: str) -> str:
    return cache.slot_id(p)


def _env_var(dump: str, nome: str) -> list:
    return [l for l in dump.splitlines() if l.startswith(nome + "=")]


def _env_sem_xdg(home: str, shimdir: str) -> dict:
    # XDG_* herdado desviaria paths.cache_dir() do <home>/.cache do teste
    env = {k: v for k, v in os.environ.items() if not k.startswith("XDG_")}
    env.update(HOME=home, PATH=shimdir + os.pathsep + os.environ["PATH"])
    return env


def test_copilot_renderizar_cru(tmp_path):
    # camada CRUA, in-process, sem normalize — o Lancamento como o adapter emite
    def w(n, t):
        p = str(tmp_path / n)
        open(p, "w").write(t)
        return p

    cm = ContextoMontado(usuario_path=w("u.md", "# U\nx"), koine_path=w("k.md", "# K\nx"),
                         agente_path=w("hermes.md", "# H\nx"),
                         escopo_path=w("e.md", "---\nid: 1\n---\n# E\nx"),
                         indice_paths=[], contexto_path=w("CONTEXTO.md", "# C\nx"),
                         pasta_abs=str(tmp_path))
    lanc = copilot.renderizar(cm)
    bundle = cache.caminho_bundle("copilot-bundles", cache.slot_id(str(tmp_path)))
    assert lanc.arquivos_working_dir == {}  # nada no working dir
    assert lanc.env_vars == {"COPILOT_CUSTOM_INSTRUCTIONS_DIRS": bundle}
    assert set(lanc.arquivos_externos) == {
        os.path.join(bundle, "AGENTS.md"),
        os.path.join(bundle, ".github", "instructions", "escopo.instructions.md"),
    }
    # AGENTS.md do copilot.go NÃO leva marcador — 1ª linha é o título mesclado
    agents = lanc.arquivos_externos[os.path.join(bundle, "AGENTS.md")]
    assert agents.splitlines()[0] == "# Sessão Koine — Copilot"
    assert lanc.symlinks == {
        os.path.join(str(tmp_path), ".github", "copilot-instructions.md"): cm.contexto_path}


@pytest.mark.skipif(sys.platform == "win32", reason="readlink")
def test_copilot_bundle_bate_com_go(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    home = fx["home"]
    trab = fx["trab"]
    bundle = os.path.join(home, ".cache", "koine", "copilot-bundles", _slot(trab))
    link = os.path.join(trab, ".github", "copilot-instructions.md")
    shimdir = str(tmp_path / "shim")
    capenv = str(tmp_path / "env.txt")
    shim.instalar_shim(shimdir, "copilot", str(tmp_path / "cap.txt"), captura_env=capenv)
    snapshot_trab = sorted(os.listdir(trab))
    # Go via kn-copilot
    _parity.rodar_wrapper_go("copilot", trab, "hermes", home, shimdir)
    conteudos_go = _parity.conteudos(bundle)
    alvo_go = os.readlink(link)
    env_go = open(capenv).read()  # salvar ANTES do rerun Python (o shim sobrescreve)
    shutil.rmtree(bundle)
    os.remove(link)
    # Python via `koine copilot`
    r = subprocess.run([sys.executable, pyz, "copilot", "hermes", trab],
                       env=_env_sem_xdg(home, shimdir),
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert _parity.conteudos(bundle) == conteudos_go  # bundle idêntico, diff legível
    assert os.readlink(link) == alvo_go == os.path.join(trab, "CONTEXTO.md")
    env_py = open(capenv).read()
    assert _env_var(env_py, "COPILOT_CUSTOM_INSTRUCTIONS_DIRS") == \
           _env_var(env_go, "COPILOT_CUSTOM_INSTRUCTIONS_DIRS") == \
           [f"COPILOT_CUSTOM_INSTRUCTIONS_DIRS={bundle}"]  # env Go×Py×esperado
    # working dir limpo: o Lancamento Go do copilot tem ArquivosNoWorkingDir vazio
    assert sorted(os.listdir(trab)) == sorted(snapshot_trab + [".github"])


def test_copilot_bootstrap_bate_com_go(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    home = fx["home"]
    canon = os.path.join(home, "koine")
    os.makedirs(canon, exist_ok=True)
    with open(os.path.join(canon, "CONTEXTO.md"), "w") as f:
        f.write("---\nbootstrap: true\n---\n\n# Bootstrap\n")
    bundle = os.path.join(home, ".cache", "koine", "copilot-bundles", _slot(canon))
    link = os.path.join(canon, ".github", "copilot-instructions.md")
    shimdir = str(tmp_path / "shimb")
    shim.instalar_shim(shimdir, "copilot", str(tmp_path / "capb.txt"))
    _parity.rodar_wrapper_go("copilot", canon, "hermes", home, shimdir)
    conteudos_go = _parity.conteudos(bundle)
    # bootstrap: só AGENTS.md + bootstrap.instructions.md; sem escopo/índices
    assert set(conteudos_go) == {
        "AGENTS.md",
        os.path.join(".github", "instructions", "bootstrap.instructions.md"),
    }
    assert not os.path.lexists(link)  # bootstrap NÃO cria symlink
    shutil.rmtree(bundle)
    r = subprocess.run([sys.executable, pyz, "copilot", "hermes", canon],
                       env=_env_sem_xdg(home, shimdir),
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert _parity.conteudos(bundle) == conteudos_go
    assert not os.path.lexists(link)


def test_instalar_emite_wrapper_kn_copilot(tmp_path):
    pyz = _build(tmp_path)
    home = str(tmp_path / "home")
    os.makedirs(home)
    bindir = os.path.join(home, "bin")
    subprocess.run([sys.executable, pyz, "instalar", "--bin", bindir, "--pyz", pyz],
                   env={"HOME": home, "PATH": "/usr/bin:/bin"},
                   check=True, capture_output=True, text=True)
    assert os.path.exists(os.path.join(bindir, "kn-copilot"))
