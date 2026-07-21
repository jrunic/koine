# tests/test_atualizar_e2e.py
import http.server
import os
import re
import shutil
import socketserver
import subprocess
import sys
import threading
from functools import partial

import pytest

from koine._version import __version__

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _servir(www: str):
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=www)
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _build_zip(destino_out: str, src_repo: str = REPO):
    subprocess.run([sys.executable, os.path.join(src_repo, "scripts", "build-pyz.py"),
                    "--out", destino_out, "--zip"], check=True, capture_output=True, text=True)


def _repo_com_versao(tmp_path, nova_versao: str) -> str:
    """Copia o repo para tmp e reescreve _version — para gerar um zip de versão
    diferente e exercitar o upgrade real (User Story #1)."""
    dst = str(tmp_path / f"repo-{nova_versao}")
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(
        ".git", ".venv", "dist", "__pycache__"))
    vf = os.path.join(dst, "src", "koine", "_version.py")
    open(vf, "w").write(f'__version__ = "{nova_versao}"\n')
    return dst


@pytest.mark.skipif(sys.platform == "win32", reason="fase-1 in-process é POSIX; Windows tem handoff próprio")
def test_atualizar_noop_e_upgrade_real(tmp_path):
    # skill nova para provar refresh
    skill = os.path.join(REPO, "vault", "habilidades", "kn-99-teste")
    os.makedirs(skill, exist_ok=True)
    open(os.path.join(skill, "SKILL.md"), "w").write("# kn-99-teste\n")
    try:
        # base = versão atual instalada
        base_out = str(tmp_path / "base")
        _build_zip(base_out)
        # alvo = versão maior
        nova = "9.9.9"
        alvo_out = str(tmp_path / "alvo")
        _build_zip(alvo_out, _repo_com_versao(tmp_path, nova))

        # serve a release ALVO
        www = tmp_path / "www" / f"v{nova}"; www.mkdir(parents=True)
        shutil.copy(os.path.join(alvo_out, f"koine-{nova}.zip"), str(www))
        srv = _servir(str(tmp_path / "www"))

        home = tmp_path / "home"; home.mkdir()
        fakebin = tmp_path / "fakebin"; fakebin.mkdir()
        claude = fakebin / "claude"; claude.write_text("#!/bin/sh\n"); claude.chmod(0o755)
        path = os.path.dirname(sys.executable) + os.pathsep + str(fakebin) + os.pathsep + "/usr/bin:/bin"
        env = {"HOME": str(home), "PATH": path,
               "KOINE_BASE_URL": f"http://127.0.0.1:{srv.server_address[1]}"}

        # instala a BASE
        dist = home / ".local/share/koine/dist"; dist.mkdir(parents=True)
        subprocess.run([sys.executable, "-m", "zipfile", "-e",
                        os.path.join(base_out, f"koine-{__version__}.zip"), str(dist)], check=True)
        pyz = str(dist / "koine.pyz")
        subprocess.run([sys.executable, pyz, "instalar"], env=env,
                       stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True)

        # 1) no-op: pin na versão instalada, sem --force
        r = subprocess.run([sys.executable, pyz, "atualizar"],
                           env={**env, "KOINE_VERSAO": f"v{__version__}"},
                           capture_output=True, text=True)
        assert r.returncode == 0 and "já está na versão" in r.stdout

        # 2) upgrade real SEM --force: pin na versão maior (User Story #1)
        r = subprocess.run([sys.executable, pyz, "atualizar"],
                           env={**env, "KOINE_VERSAO": f"v{nova}"},
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr + r.stdout
        # pyz trocado → koine versao reporta a nova
        v = subprocess.run([sys.executable, pyz, "versao"], env=env,
                           capture_output=True, text=True).stdout
        assert nova in v
        # skill nova refrescada no harness detectado
        assert os.path.isdir(os.path.join(str(home), ".claude/skills/kn-99-teste"))
    finally:
        srv.shutdown(); srv.server_close()
        shutil.rmtree(skill, ignore_errors=True)
