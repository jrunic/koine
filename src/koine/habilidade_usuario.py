# src/koine/habilidade_usuario.py
"""Skill de usuário: um SKILL.md próprio, fora do vault, que o usuário cria
para um fluxo de trabalho recorrente que nenhuma `kn-NN` shipped cobre.

Contrato de nome/descrição é o mesmo que o OpenCode exige das skills do
vault (`tests/test_vault_habilidades.py`) — centralizado aqui porque agora
tem dois consumidores (vault e usuário) e duplicar o regex arriscaria os
dois divergirem.
"""
import re

NOME_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NOME_RESERVADO = re.compile(r"^kn-\d{2}-")
DESCRICAO_MIN = 1
DESCRICAO_MAX = 1024


def nome_valido(nome: str) -> bool:
    return bool(NOME_VALIDO.match(nome))


def nome_reservado(nome: str) -> bool:
    """Bloco `kn-<dois dígitos>-` é do catálogo do produto — skill de usuário
    não pode usar essa forma, para não se confundir com skill shipped."""
    return bool(NOME_RESERVADO.match(nome))


def descricao_valida(descricao: str) -> bool:
    return DESCRICAO_MIN <= len(descricao) <= DESCRICAO_MAX


def validar(nome: str, descricao: str) -> str | None:
    """Mensagem de erro, ou None se nome e descrição passam no contrato de
    máquina. Não checa colisão com vault/skill existente — isso depende do
    disco e mora em `criar()`."""
    if not nome_valido(nome):
        return (f"nome inválido: {nome!r} — use só letras minúsculas, "
                "dígitos e hífen, sem começar ou terminar com hífen")
    if nome_reservado(nome):
        return (f"nome reservado ao produto: {nome!r} começa com "
                "kn-<dois dígitos>- — escolha outro nome")
    if not descricao_valida(descricao):
        return (f"descrição com {len(descricao)} caracteres — precisa ter "
                "entre 1 e 1024")
    return None
