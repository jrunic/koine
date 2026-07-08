import os
import stat

from koine import adapters


def _is_windows() -> bool:
    return os.name == "nt"


def gerar(bindir: str, pyz_path: str, interpretador: str | None = None) -> list[str]:
    """Cria um wrapper por adapter em adapters.REGISTRY (Windows: kn-<cli>.bat;
    Unix: kn-<cli> sem extensão, shebang + +x).

    `interpretador`: caminho absoluto do interpretador Python a invocar. Deve
    ser o `sys.executable` de quem rodou `instalar` — que é garantidamente
    >=3.10 (senão o próprio `instalar` teria falhado ao importar koine). Isso
    evita o bug de `python3` puro resolver para um Python antigo do sistema
    (ex.: 3.9 no macOS), que não roda a sintaxe 3.12+ do koine.

    Sem `interpretador`, cai no fallback por plataforma (`python`/`python3`).
    O interpretador é sempre citado (pode conter espaços; nome puro também
    resolve via PATH quando citado)."""
    os.makedirs(bindir, exist_ok=True)
    interp = interpretador or ("python" if _is_windows() else "python3")
    criados = []
    for cliente in adapters.REGISTRY:
        if _is_windows():
            caminho = os.path.join(bindir, f"kn-{cliente}.bat")
            conteudo = f'@"{interp}" "{pyz_path}" {cliente} %*\r\n'
            with open(caminho, "w", newline="") as f:
                f.write(conteudo)
        else:
            caminho = os.path.join(bindir, f"kn-{cliente}")
            conteudo = f'#!/usr/bin/env bash\nexec "{interp}" "{pyz_path}" {cliente} "$@"\n'
            with open(caminho, "w") as f:
                f.write(conteudo)
            os.chmod(caminho, os.stat(caminho).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IRGRP | stat.S_IROTH)
        criados.append(caminho)
    return criados
