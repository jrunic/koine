"""O que vai — e o que não vai — funcionar nesta máquina, por cliente.

Decisão apenas: recebe o estado da máquina e devolve achados tipados. A prosa
mora em `mensagens.py`, e os dois consumidores formatam diferente — o relatório
do `instalar` é uma tabela, o aviso do launch é uma linha.

Medido em 28/08/2026 na estação que nega o PowerShell por política de grupo:
copilot, codex e agy ficam SEM ferramenta de shell, e não há configuração que
resolva. A sessão sobe e o contexto chega; só não executa comando.
"""
from dataclasses import dataclass

from koine import adapters, shell

SEM_SHELL = "sem_shell"              # o cliente não tem shell aqui, e não há ajuste
CLAUDE_SEM_BASH = "claude_sem_bash"  # sem shell, MAS com remédio: instalar o Git Bash


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
