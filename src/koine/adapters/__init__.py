from koine.adapters import antigravity, claude, codex

# registry cliente → (módulo do adapter). instalar itera isto para
# emitir um wrapper kn-<cliente> por adapter REGISTRADO.
REGISTRY = {
    "claude": claude,
    "agy": antigravity,
    "codex": codex,
}


def get(cliente: str):
    if cliente not in REGISTRY:
        raise KeyError(f"cliente desconhecido: {cliente}")
    return REGISTRY[cliente]
