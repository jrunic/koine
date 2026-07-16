import os
import shutil
import subprocess
import sys


class ClienteNaoEncontrado(Exception):
    """O binário do cliente IA não está no PATH (shutil.which devolveu None).
    Carrega .cliente; a prosa amigável é montada pelo consumidor (mensagens)."""

    def __init__(self, cliente: str):
        self.cliente = cliente
        super().__init__(f"cliente {cliente!r} não encontrado no PATH")


class ClienteNaoExecutavel(Exception):
    """O binário do cliente FOI encontrado no PATH, mas o SO recusou executá-lo
    (ex.: Windows WinError 193 — não é um aplicativo Win32 válido). NÃO é erro
    de PATH. Carrega .cliente, .binpath e a exceção .erro de origem."""

    def __init__(self, cliente: str, binpath: str, erro: OSError):
        self.cliente = cliente
        self.binpath = binpath
        self.erro = erro
        super().__init__(f"cliente {cliente!r} encontrado em {binpath!r} não é executável: {erro}")


def lancar(cliente: str, pasta: str, env: dict | None = None, args: list | None = None):
    """Lança o cliente IA na pasta. Porta de lancarClienteImpl (Go).
    Unix: substitui o processo via execvpe (herda TTY). Windows: subprocess.run.
    `env`/`args` ficam na assinatura mas não são usados pelo claude (deferido p/ P4-P6).
    Levanta ClienteNaoEncontrado se o binário não estiver no PATH; no Windows,
    ClienteNaoExecutavel se o binário existir mas o CreateProcess recusar rodá-lo."""
    binpath = shutil.which(cliente)
    if binpath is None:
        raise ClienteNaoEncontrado(cliente)
    extra = list(args or [])
    ambiente = {**os.environ, **(env or {})}
    if sys.platform == "win32":
        # Deixe o cmd.exe resolver o cliente pelo NOME — reproduz exatamente o
        # que funciona quando o usuário digita `codex` no terminal. Passar o
        # binpath que o shutil.which escolheu é frágil: ele pode devolver uma
        # variante (shim, .py, arquitetura incompatível) que o CreateProcess
        # recusa com WinError 193, mesmo havendo um .cmd/.exe válido ao lado no
        # PATH. O `cmd /c` aplica a mesma resolução PATHEXT do shell interativo.
        try:
            return subprocess.run(["cmd", "/c", cliente, *extra],
                                  cwd=pasta, env=ambiente).returncode
        except OSError as e:
            # rede de segurança: cmd.exe ausente ou irrelevante. WinError 193 do
            # cliente em si já não chega aqui (vira errorlevel do cmd).
            raise ClienteNaoExecutavel(cliente, binpath, e) from e
    os.chdir(pasta)
    os.execvpe(cliente, [cliente, *extra], ambiente)  # NÃO retorna: substitui o processo
