import hashlib
import os

from koine import paths


def slot_id(pasta_abs: str) -> str:
    """Identificador determinístico de 12 chars hex (SHA-256, 6 bytes) da pasta.

    Mesma pasta → mesmo slot. Sem timestamp — cache cresce em #pastas, não em #sessões.
    """
    return hashlib.sha256(pasta_abs.encode()).hexdigest()[:12]


def caminho_bundle(categoria: str, slot: str) -> str:
    return os.path.join(paths.cache_dir(), categoria, slot)


def caminho_arquivo(categoria: str, slot: str, extensao: str) -> str:
    return os.path.join(paths.cache_dir(), categoria, f"{slot}.{extensao}")
