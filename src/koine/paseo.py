"""Rota de um cliente pelo canal do Paseo.

O Paseo spawna o comando do provider e passa a PRÓPRIA lista de argumentos.
Medido em 29/08/2026 na bancada Windows (Paseo 0.6.1): nem todo cliente é
alcançável, e os que são não são alcançáveis do mesmo jeito. Esta é a única
declaração da matriz — o `cli`, o `wrappers` e o comando de leitura perguntam
aqui, em vez de cada um carregar uma cópia que envelheceria sozinha.
"""
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
