# src/koine/saida.py
"""Saída de texto que não derruba o comando por causa do encoding do terminal.

No Windows, o Python escreve no console por WriteConsoleW e qualquer caractere
passa. Quando o stdout NÃO é console — redirecionado para arquivo, num pipe, ou
sob tarefa agendada — o encoding vira o do locale (`cp1252` em pt-BR), e o
primeiro `✓` das mensagens levanta UnicodeEncodeError: o comando morre com
traceback no lugar do trabalho. Medido em produção na bancada Windows em
27/08/2026, com o `install.bat` rodando por tarefa agendada.

A correção é a mínima que resolve: manter o encoding do ambiente (quem for ler
o arquivo depois lê no encoding que espera) e trocar só a política de erro para
`replace`. Símbolo sem correspondência vira `?`; acento continua acento; nada
aborta.
"""
import sys


def _utf8(fluxo) -> bool:
    enc = (getattr(fluxo, "encoding", "") or "").lower().replace("-", "").replace("_", "")
    return enc in ("utf8", "utf8sig")


def preparar(*fluxos) -> None:
    """Torna os fluxos tolerantes a caractere não representável. Idempotente,
    e silenciosa quando o fluxo não suporta reconfigure (fluxo substituído em
    teste, redirecionamento exótico) — a saída é o meio, nunca o motivo de uma
    falha."""
    for fluxo in fluxos or (sys.stdout, sys.stderr):
        reconfigure = getattr(fluxo, "reconfigure", None)
        if reconfigure is None or _utf8(fluxo):
            continue
        try:
            reconfigure(errors="replace")
        except (ValueError, OSError, AttributeError):
            pass
