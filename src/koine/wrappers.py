import os
import stat

from koine import adapters


def _is_windows() -> bool:
    return os.name == "nt"


def gerar(bindir: str, pyz_path: str) -> list[str]:
    """Cria um wrapper por adapter em adapters.REGISTRY. Windows: kn-<cli>.bat
    invocando `python`; Unix: kn-<cli> (sem extensão, shebang + +x) invocando
    `python3`. A escolha do interpretador é por plataforma — ver nota abaixo."""
    os.makedirs(bindir, exist_ok=True)
    interp = "python" if _is_windows() else "python3"
    criados = []
    for cliente in adapters.REGISTRY:
        if _is_windows():
            caminho = os.path.join(bindir, f"kn-{cliente}.bat")
            conteudo = f'@{interp} "{pyz_path}" {cliente} %*\r\n'
            with open(caminho, "w", newline="") as f:
                f.write(conteudo)
        else:
            caminho = os.path.join(bindir, f"kn-{cliente}")
            conteudo = f'#!/usr/bin/env bash\nexec {interp} "{pyz_path}" {cliente} "$@"\n'
            with open(caminho, "w") as f:
                f.write(conteudo)
            os.chmod(caminho, os.stat(caminho).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IRGRP | stat.S_IROTH)
        criados.append(caminho)
    return criados
