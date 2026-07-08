import hashlib
import os
import re

# Linhas que variam entre execuções e NÃO são divergência real.
# Congeladas fora da comparação. Ampliar SÓ com evidência empírica.
_TIMESTAMP = re.compile(r"em \d{4}-\d{2}-\d{2}[ T][\d:]+")
_REGEN = re.compile(r"regerar com [^\n]*")
# Header do kn-indice-<dom>.md: `gerado: <ISO8601>Z` (RFC3339 UTC).
# Formato distinto do `em <ts>` do CLAUDE.md — normalizar separadamente.
_INDICE_GERADO = re.compile(r"gerado: [^\n]*")


def normalize(text: str) -> str:
    text = _TIMESTAMP.sub("em <TS>", text)
    text = _REGEN.sub("regerar com <CMD>", text)
    text = _INDICE_GERADO.sub("gerado: <TS>", text)
    return text


def conteudos(base: str) -> dict:
    """{caminho-relativo: conteúdo normalizado} de todos os arquivos sob base.
    {} se ausente. Normalizado (timestamps congelados) — diff legível ao divergir,
    ao contrário da comparação por hash."""
    out = {}
    if not os.path.isdir(base):
        return out
    for raiz, _, arqs in os.walk(base):
        for a in arqs:
            p = os.path.join(raiz, a)
            with open(p, encoding="utf-8") as f:
                out[os.path.relpath(p, base)] = normalize(f.read())
    return out


def arvore(base: str) -> dict:
    """{caminho-relativo: sha256} de todos os arquivos sob base. {} se ausente."""
    out = {}
    if not os.path.isdir(base):
        return out
    for raiz, _, arqs in os.walk(base):
        for a in arqs:
            p = os.path.join(raiz, a)
            with open(p, "rb") as f:
                out[os.path.relpath(p, base)] = hashlib.sha256(f.read()).hexdigest()
    return out
