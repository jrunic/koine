"""Qual shell esta máquina consegue EXECUTAR, dentre os que o cliente aceita.

Presença não responde: na estação corporativa medida em 28/08/2026 o `pwsh.exe`
existe, está no PATH e é recusado pela política de grupo (erro 1260). Só a
tentativa de executar distingue os três desfechos que importam.

A sonda é injetável porque teste que depende do `pwsh` real da máquina de quem
roda a suíte não é reprodutível — o CI é POSIX-only.
"""
import os
import shutil
import subprocess
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

TIMEOUT = 15  # generoso: a partida do PowerShell 7 em máquina fria é lenta

_ARGS = {
    PWSH: ["-NoProfile", "-Command", "exit"],
    POWERSHELL: ["-NoProfile", "-Command", "exit"],
    BASH: ["-c", "exit"],
    CMD: ["/c", "exit"],
}


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


_CACHE = {}


def sondar(nome):
    # (invocacao, estado) para um degrau, memoizado POR PROCESSO.
    #
    # O processo do launch morre no execvpe, entao nao ha invalidacao a
    # resolver: dentro de um lancamento a maquina nao muda. O cache existe
    # porque ha DOIS consumidores — o adapter, que escolhe o shell, e o aviso
    # de pre-requisitos, que decide se fala — e sondar duas vezes custaria uma
    # segunda partida de PowerShell na maquina saudavel.
    if nome not in _CACHE:
        _CACHE[nome] = _sondar_agora(nome)
    return _CACHE[nome]


def limpar_cache():
    # Zera a memoizacao. Existe para o teste: sem isto o resultado de um cenario
    # vaza para o proximo e a suite passa a medir o cache.
    _CACHE.clear()


def _sondar_agora(nome):
    """(invocacao, estado) para um degrau. Executa; não olha só o disco.

    Timeout conta como RECUSADO, não como ausente: shell que não termina um
    `exit` não serve para o cliente, e a distinção que a orientação de
    pré-requisitos precisa é entre "instale isto" (AUSENTE) e "peça à TI"
    (RECUSADO).
    """
    invocacao = _resolver(nome)
    if invocacao is None:
        return nome, AUSENTE
    try:
        proc = subprocess.run([invocacao] + _ARGS[nome], timeout=TIMEOUT,
                              stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return invocacao, AUSENTE
    except (OSError, subprocess.SubprocessError):
        # o 1260 da política de grupo estoura na CRIAÇÃO do processo, então esta
        # reprovação é instantânea — só o degrau que executa paga a partida.
        return invocacao, RECUSADO
    return invocacao, (EXECUTOU if proc.returncode == 0 else RECUSADO)


def _resolver(nome):
    """Onde está o binário deste degrau, ou None.

    Para o bash o PATH não basta, e isso é medição: na bancada de 28/08/2026 o
    `where bash` falha (o PATH tem só a pasta `cmd` do Git) e mesmo assim Claude
    e OpenCode usam o bash — os dois sondam a instalação do Git sozinhos.
    """
    achado = shutil.which(nome)
    if achado:
        return achado
    if nome == BASH:
        for candidato in _bash_do_git():
            if os.path.isfile(candidato):
                return candidato
    return None


def _bash_do_git():
    """Lugares padrão do Git para Windows, do mais provável ao menos.

    O perfil vem primeiro porque é onde o instalador cai SEM administrador, que
    é a condição do público-alvo.
    """
    local = os.environ.get("LOCALAPPDATA", "")
    arquivos = os.environ.get("ProgramFiles", "")
    arquivos86 = os.environ.get("ProgramFiles(x86)", "")
    caminhos = []
    if local:
        caminhos.append(os.path.join(local, "Programs", "Git", "bin", "bash.exe"))
    for base in (arquivos, arquivos86):
        if base:
            caminhos.append(os.path.join(base, "Git", "bin", "bash.exe"))
    return caminhos


POWERSHELLS = (PWSH, POWERSHELL)


def powershell_executa(*, sonda=None):
    """Alguma das duas famílias de PowerShell roda nesta máquina?"""
    return melhor(POWERSHELLS, sonda=sonda) is not None


def diagnostico(aceitos, *, sonda=None):
    """Estado de CADA degrau, sem parar no primeiro que executa.

    É o contrato com a orientação de pré-requisitos: "não instalado" e
    "bloqueado pela política" pedem mensagens opostas ao usuário.
    """
    sonda = sonda or sondar
    saida = []
    for nome in ESCADA:
        if nome not in aceitos:
            continue
        invocacao, estado = sonda(nome)
        saida.append(Degrau(nome, invocacao, estado))
    return saida
