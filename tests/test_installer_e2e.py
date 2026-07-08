import http.server
import os
import shutil
import socketserver
import subprocess
import sys
import threading
from functools import partial

import pytest

from koine._version import __version__

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(sys.platform == "win32", reason="install.sh é Unix")
def test_install_sh_greenfield_contra_release_local(tmp_path):
    # 1. montar o pacote real
    out = str(tmp_path / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out, "--zip"], check=True, capture_output=True, text=True)
    # 2. servir como uma release: <base>/v<versao>/koine-<versao>.zip
    tag_dir = tmp_path / "www" / f"v{__version__}"
    tag_dir.mkdir(parents=True)
    shutil.copy(os.path.join(out, f"koine-{__version__}.zip"), str(tag_dir))
    handler = partial(http.server.SimpleHTTPRequestHandler,
                      directory=str(tmp_path / "www"))
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        home = str(tmp_path / "home")
        os.makedirs(home)
        # PATH: dir do interpretador da suíte (>=3.12) + sistema (curl)
        path = os.path.dirname(sys.executable) + os.pathsep + "/usr/bin:/bin"
        r = subprocess.run(
            ["bash", os.path.join(REPO, "scripts", "release", "install.sh")],
            env={"HOME": home, "PATH": path,
                 "KOINE_VERSAO": f"v{__version__}",
                 "KOINE_BASE_URL": f"http://127.0.0.1:{srv.server_address[1]}"},
            capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)
        assert r.returncode == 0, r.stderr + r.stdout
        # pacote extraído no local canônico
        assert os.path.exists(os.path.join(home, ".local/share/koine/dist/koine.pyz"))
        assert os.path.exists(os.path.join(home, ".local/share/koine/dist/vault/KOINE.md"))
        # e o `koine instalar` delegado rodou de verdade (vault + wrappers)
        assert os.path.exists(os.path.join(home, ".local/share/koine/KOINE.md"))
        assert os.path.exists(os.path.join(home, ".local/bin/kn-claude"))
        assert os.path.exists(os.path.join(home, ".local/bin/koine"))
        # pasta canônica de bootstrap (modo não-interativo → default silencioso)
        assert os.path.exists(os.path.join(home, "koine", "CONTEXTO.md"))
    finally:
        srv.shutdown()
        srv.server_close()
