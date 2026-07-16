import os
import shutil
import subprocess
import sys


class ClienteNaoEncontrado(Exception):
    """O binário do cliente IA não está no PATH."""


def lancar(cliente: str, pasta: str, env: dict | None = None, args: list | None = None):
    """Lança o cliente IA na pasta. Porta de lancarClienteImpl (Go).
    Unix: substitui o processo via execvpe (herda TTY). Windows: subprocess.run.
    `env`/`args` ficam na assinatura mas não são usados pelo claude (deferido p/ P4-P6).
    Levanta ClienteNaoEncontrado se o binário não estiver no PATH."""
    binpath = shutil.which(cliente)
    if binpath is None:
        raise ClienteNaoEncontrado(
            f"cliente {cliente!r} não encontrado no PATH — instale e tente novamente")
    extra = list(args or [])
    ambiente = {**os.environ, **(env or {})}
    if sys.platform == "win32":
        # .bat/.cmd não são executáveis Win32 — CreateProcess exige cmd.exe /c
        if binpath.lower().endswith((".bat", ".cmd")):
            cmd = ["cmd", "/c", binpath, *extra]
        else:
            cmd = [binpath, *extra]
        return subprocess.run(cmd, cwd=pasta, env=ambiente).returncode
    os.chdir(pasta)
    os.execvpe(cliente, [cliente, *extra], ambiente)  # NÃO retorna: substitui o processo
