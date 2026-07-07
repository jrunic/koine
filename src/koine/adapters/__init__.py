from koine.adapters import claude

# registry cliente → (módulo do adapter). instalar (P2) itera isto para
# emitir um wrapper kn-<cliente> por adapter REGISTRADO. P1 registra só claude.
REGISTRY = {
    "claude": claude,
}


def get(cliente: str):
    if cliente not in REGISTRY:
        raise KeyError(f"cliente desconhecido: {cliente}")
    return REGISTRY[cliente]
