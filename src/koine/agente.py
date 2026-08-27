# src/koine/agente.py
"""Quem decide o agente da sessão — e de onde veio a decisão.

A fonte não é enfeite: o tratamento de agente inexistente bifurca por ela.
Posicional errado é dedo humano no teclado e recebe erro com a lista; valor
errado gravado num arquivo não tem o que redigitar, e recebe Hermes com a
instrução de corrigir. Sem devolver a fonte, os dois casos ficam
indistinguíveis no consumidor.
"""
import os

POSICIONAL = "posicional"
PASTA = "pasta"
DEFAULT = "default"
FALLBACK = "fallback"

CAMPO_PASTA = "agente"
CAMPO_DEFAULT = "agente-default"
HERMES = "hermes"


def resolver_nome(posicional: str, fm_pasta: dict,
                  default_usuario: str) -> tuple[str, str]:
    """(nome, fonte), na precedência da spec: posicional → pasta → default →
    hermes. Vale só em pasta VALIDO; os outros estados forçam Hermes antes de
    chegar aqui."""
    if posicional:
        return posicional, POSICIONAL
    declarado = (fm_pasta.get(CAMPO_PASTA) or "").strip()
    if declarado:
        return declarado, PASTA
    if default_usuario:
        return default_usuario, DEFAULT
    return HERMES, FALLBACK


def default_do_usuario(usuario_path: str, ler_fm) -> str:
    """Lê `agente-default:` do arquivo do usuário. Sem arquivo resolvível —
    nenhum, ou mais de um `.md` na raiz do config — não há default, e o
    fallback é Hermes SEM erro. Não inventar desempate aqui."""
    if not usuario_path or not os.path.exists(usuario_path):
        return ""
    try:
        fm, _ = ler_fm(usuario_path)
    except Exception:
        return ""
    return (fm.get(CAMPO_DEFAULT) or "").strip()
