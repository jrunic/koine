"""Qual shell esta máquina consegue EXECUTAR, dentre os que o cliente aceita.

Presença não responde: na estação corporativa medida em 28/08/2026 o `pwsh.exe`
existe, está no PATH e é recusado pela política de grupo (erro 1260). Só a
tentativa de executar distingue os três desfechos que importam.

A sonda é injetável porque teste que depende do `pwsh` real da máquina de quem
roda a suíte não é reprodutível — o CI é POSIX-only.
"""
from dataclasses import dataclass

# desfechos de uma sondagem
EXECUTOU = "executou"
RECUSADO = "recusado"   # existe, e a máquina não deixou rodar
AUSENTE = "ausente"     # não foi encontrado

# degraus, na ordem de preferência declarada para Windows
PWSH = "pwsh"
POWERSHELL = "powershell"
BASH = "bash"
CMD = "cmd"
ESCADA = (PWSH, POWERSHELL, BASH, CMD)


@dataclass(frozen=True)
class Degrau:
    nome: str        # o degrau canônico
    invocacao: str   # como chamar: nome curto, ou caminho absoluto quando fora do PATH
    estado: str


def melhor(aceitos, *, sonda=None):
    """Primeiro degrau da ESCADA que o cliente aceita E a máquina executa."""
    sonda = sonda or sondar
    for nome in ESCADA:
        if nome not in aceitos:
            continue
        invocacao, estado = sonda(nome)
        if estado == EXECUTOU:
            return Degrau(nome, invocacao, estado)
    return None
