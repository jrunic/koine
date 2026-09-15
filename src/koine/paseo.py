"""Rota de um cliente pelo canal do Paseo.

O Paseo spawna o comando do provider e passa a PRÓPRIA lista de argumentos.
Medido em 29/08/2026 na bancada Windows (Paseo 0.6.1): nem todo cliente é
alcançável, e os que são não são alcançáveis do mesmo jeito. Esta é a única
declaração da matriz — o `cli`, o `wrappers` e o comando de leitura perguntam
aqui, em vez de cada um carregar uma cópia que envelheceria sozinha.
"""
import os
import shutil
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Rota:
    """`extends`: builtin do Paseo que o entry do provider deve estender.

    `args`: argumentos que precedem os do Paseo — o subcomando que o cliente
    exige para falar o protocolo. O opencode exige; os outros dois, não.
    """
    extends: str
    args: tuple = field(default=())


def rota(cliente: str):
    # import local: os adapters importam este módulo no corpo deles, e uma
    # dependência no nível de módulo aqui fecharia o ciclo.
    from koine import adapters
    return adapters.get(cliente).PASEO


def com_rota() -> list[str]:
    """Clientes alcançáveis pelo Paseo, em ordem estável."""
    from koine import adapters
    return sorted(c for c in adapters.REGISTRY if rota(c) is not None)


def wrapper_de(cliente: str) -> str:
    return f"kn-{cliente}-paseo"


def entry_de(cliente: str) -> str:
    """Identificador do provider genérico no config do orquestrador.

    Prescrito aqui, não escolhido por quem configura: nome inventado diverge
    entre máquinas, e o dia em que uma ferramenta precisar ler ou consertar
    esse config encontra dois vocabulários para a mesma coisa.
    """
    return f"kn-{cliente}"


def entry_hermes_de(cliente: str) -> str:
    """Identificador do provider que força o Hermes por variável de ambiente."""
    return f"kn-{cliente}-hermes"


def _wrapper_em_padrao(nome: str) -> str | None:
    """Wrapper no diretório canônico de instalação (`~/.local/bin`).

    O Git Bash nem sempre herda o PATH completo do Windows; achar o wrapper
    no lugar onde o `instalar` o pôs dispensa alias em `.bashrc` (spec
    20260915-spec-paseo-windows-sem-variavel).
    """
    ext = ".bat" if os.name == "nt" else ""
    alvo = os.path.join(os.path.expanduser("~"), ".local", "bin", nome + ext)
    return alvo if os.path.isfile(alvo) else None


def matriz(*, which=shutil.which) -> dict:
    """Matriz por cliente com rota. `which` é costura da suíte."""
    dados = {}
    for cliente in com_rota():
        r = rota(cliente)
        wrapper = wrapper_de(cliente)
        caminho = which(wrapper) or _wrapper_em_padrao(wrapper)
        dados[cliente] = {
            "wrapper": wrapper_de(cliente),
            "provider": entry_de(cliente),
            "provider_hermes": entry_hermes_de(cliente),
            "extends": r.extends,
            "args": list(r.args),
            "existe": caminho is not None,
            "caminho": caminho,
        }
    return dados
