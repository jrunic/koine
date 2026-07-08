import os
from koine import aliases


class ResolucaoInterativaRequerida(Exception):
    """arg não resolveu por alias nem path; fuzzy+menu é interativo (deferido)."""


def resolver(arg: str) -> str:
    """Porta não-interativa de pasta.Resolver (Go). Ordem:
    "" → cwd | alias exato → path | path direto → abspath.
    Sem match → ResolucaoInterativaRequerida (ramo fuzzy/menu deferido)."""
    if arg == "":
        return os.getcwd()
    alvo = aliases.resolver(aliases.carregar(), arg)
    if alvo is not None:
        return alvo
    if os.path.isdir(arg):
        return os.path.abspath(arg)
    raise ResolucaoInterativaRequerida(
        f"'{arg}' não resolveu para alias nem pasta existente — "
        f"resolução fuzzy/interativa ainda não portada")
