import os
import stat

from koine import adapters


def _is_windows() -> bool:
    return os.name == "nt"


def gerar(bindir: str, pyz_path: str, interpretador: str | None = None) -> list[str]:
    """Cria o wrapper administrativo `koine` + um wrapper por adapter em
    adapters.REGISTRY (Windows: <nome>.bat; Unix: <nome> sem extensão, +x).

    `interpretador`: caminho absoluto do interpretador Python a invocar. Deve
    ser o `sys.executable` de quem rodou `instalar` — que é garantidamente
    >=3.10 (senão o próprio `instalar` teria falhado ao importar koine). Isso
    evita o bug de `python3` puro resolver para um Python antigo do sistema
    (ex.: 3.9 no macOS), que não roda a sintaxe 3.12+ do koine.

    Sem `interpretador`, cai no fallback por plataforma (`python`/`python3`).
    O interpretador é sempre citado (pode conter espaços; nome puro também
    resolve via PATH quando citado).

    Upgrade Go→Python: caminho ocupado por symlink cujo alvo é o binário
    `kn-agente` (artefato da instalação Go, não dado do usuário) é substituído.
    Symlink para outro alvo ou diretório é preservado com aviso. Arquivo
    regular só é regenerado se contém `koine.pyz` (wrapper de instalação
    anterior, gerado por nós); qualquer outro arquivo é preservado com aviso."""
    os.makedirs(bindir, exist_ok=True)
    interp = interpretador or ("python" if _is_windows() else "python3")
    criados = []
    nomes = [("koine", None)] + [(f"kn-{c}", c) for c in adapters.REGISTRY]
    for nome, cliente in nomes:
        arg = f"{cliente} " if cliente else ""
        if _is_windows():
            caminho = os.path.join(bindir, f"{nome}.bat")
            if not _liberar_caminho(caminho):
                continue
            with open(caminho, "w", newline="") as f:
                f.write(f'@"{interp}" "{pyz_path}" {arg}%*\r\n')
        else:
            caminho = os.path.join(bindir, nome)
            if not _liberar_caminho(caminho):
                continue
            with open(caminho, "w") as f:
                f.write(f'#!/usr/bin/env bash\nexec "{interp}" "{pyz_path}" {arg}"$@"\n')
            os.chmod(caminho, os.stat(caminho).st_mode
                     | stat.S_IXUSR | stat.S_IXGRP | stat.S_IRGRP | stat.S_IROTH)
        criados.append(caminho)
    return criados


def _liberar_caminho(caminho: str) -> bool:
    """True se o caminho está livre para receber o wrapper. Nunca escreve
    através de symlink (escreveria no ALVO — corromperia o binário Go)."""
    if not os.path.lexists(caminho):
        return True
    if os.path.islink(caminho):
        alvo = os.readlink(caminho)
        if os.path.basename(alvo) in ("kn-agente", "kn-agente.exe"):
            os.remove(caminho)  # atalho da instalação Go → substitui (upgrade)
            return True
        print(f"  ! {caminho} preservado (symlink para {alvo} — não é instalação Koine)")
        return False
    if os.path.isdir(caminho):
        print(f"  ! {caminho} preservado (é um diretório)")
        return False
    # arquivo regular: só é "nosso" se contém koine.pyz (wrapper gerado por
    # instalação anterior). Qualquer outro conteúdo é do usuário — preserva.
    # Divergência DECLARADA vs Go: o Go preservava QUALQUER arquivo regular
    # com "! já existe (use --force)"; aqui o wrapper nosso regenera (upgrade
    # limpo, sem --force) e só o arquivo alheio é preservado com aviso.
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            if "koine.pyz" in f.read():
                return True  # wrapper de instalação anterior → regenera
    except OSError:
        pass
    print(f"  ! {caminho} preservado (arquivo existente não gerado pelo Koine)")
    return False
