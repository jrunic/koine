# tests/fixtures/shim.py
import os
import stat


def instalar_shim(bindir: str, nome: str, captura: str) -> str:
    """Cria um shim executável <bindir>/<nome> que grava cwd + args em <captura>
    (uma linha: cwd\\n, depois os args) e sai 0. Simula o cliente IA lançado."""
    os.makedirs(bindir, exist_ok=True)
    p = os.path.join(bindir, nome)
    with open(p, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(f'{{ pwd; printf "%s\\n" "$@"; }} > "{captura}"\n')
    os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return p
