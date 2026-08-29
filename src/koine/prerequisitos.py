"""O que vai — e o que não vai — funcionar nesta máquina, por cliente.

Decisão apenas: recebe o estado da máquina e devolve achados tipados. A prosa
mora em `mensagens.py`, e os dois consumidores formatam diferente — o relatório
do `instalar` é uma tabela, o aviso do launch é uma linha.

Medido em 28/08/2026 na estação que nega o PowerShell por política de grupo:
copilot, codex e agy ficam SEM ferramenta de shell, e não há configuração que
resolva. A sessão sobe e o contexto chega; só não executa comando.
"""
import os
import re
import shutil
from dataclasses import dataclass

from koine import adapters, shell

SEM_SHELL = "sem_shell"              # o cliente não tem shell aqui, e não há ajuste
CLAUDE_SEM_BASH = "claude_sem_bash"  # sem shell, MAS com remédio: instalar o Git Bash
OPENCODE_TUI_ARM64 = "opencode_tui_arm64"  # bug upstream, três issues abertas
CODEX_INCOMPLETO = "codex_incompleto"      # instalado sem o code-mode-host


@dataclass(frozen=True)
class Achado:
    cliente: str
    codigo: str


def avaliar_cliente(cliente, *, sonda=None):
    """O achado deste cliente nesta máquina, ou None quando está tudo certo."""
    mod = adapters.REGISTRY.get(cliente)
    if mod is None:
        return None
    if shell.melhor(mod.ACEITA_SHELL, sonda=sonda) is not None:
        return None
    # Sem degrau que execute. O claude é o único com saída: ele aceita bash, e o
    # Git Bash é instalável sem administrador. Para os outros não há o que fazer.
    if cliente == "claude":
        return Achado(cliente, CLAUDE_SEM_BASH)
    return Achado(cliente, SEM_SHELL)


def avaliar(clientes, *, sonda=None, arquitetura=None, pasta_codex=None):
    """Todos os achados destes clientes, na ordem em que devem ser lidos."""
    achados = []
    for cliente in clientes:
        a = avaliar_cliente(cliente, sonda=sonda)
        if a is not None:
            achados.append(a)
        if cliente == "opencode" and (arquitetura or "").upper() == "ARM64":
            achados.append(Achado(cliente, OPENCODE_TUI_ARM64))
        if cliente == "codex" and _codex_incompleto(pasta_codex):
            achados.append(Achado(cliente, CODEX_INCOMPLETO))
    return achados


def _codex_incompleto(pasta_codex):
    """True só quando dá para AFIRMAR que falta o host.

    Pasta desconhecida devolve False: acusar instalação boa de incompleta manda o
    usuário refazer o que está certo, e é pior do que ficar calado.
    """
    if not pasta_codex:
        return False
    tem_cli = os.path.isfile(os.path.join(pasta_codex, "codex.exe"))
    tem_host = os.path.isfile(os.path.join(pasta_codex, "codex-code-mode-host.exe"))
    return tem_cli and not tem_host


def codex_dir():
    """A pasta da instalação do codex, ou None quando não dá para afirmar.

    Duas formas cobertas: o `.exe` direto no PATH, e o shim `.cmd` que a receita
    de instalação documentada cria. Qualquer outra coisa devolve None, e o
    chamador fica calado — ver `_codex_incompleto`.
    """
    achado = shutil.which("codex")
    if not achado:
        return None
    if achado.lower().endswith(".exe"):
        return os.path.dirname(achado)
    try:
        with open(achado, encoding="utf-8", errors="replace") as f:
            texto = f.read(4096)
    except OSError:
        return None
    m = re.search(r'"([^"]+\.exe)"', texto)
    return os.path.dirname(m.group(1)) if m else None
