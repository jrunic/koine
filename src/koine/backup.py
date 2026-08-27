# src/koine/backup.py
"""Onde o conteúdo substituído vai parar, e como ele é gravado.

Dono único da política de backup do Koine. Antes existia duplicada em
`conflito.py` (arquivo gerado na pasta de sessão) e em `ficha.py` (escrita de
frontmatter), com o comentário da segunda dizendo que copiava a primeira — uma
terceira cópia viraria drift.
"""
import os


def caminho_livre(base: str) -> str:
    """Primeiro nome livre da família `base`, `base.1`, `base.2`...

    `lexists` e não `exists`: symlink quebrado ocupa o nome, e gravar por cima
    dele escreveria no destino que não existe.
    """
    if not os.path.lexists(base):
        return base
    i = 1
    while os.path.lexists(f"{base}.{i}"):
        i += 1
    return f"{base}.{i}"
