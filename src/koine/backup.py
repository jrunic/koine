# src/koine/backup.py
"""Onde o conteúdo substituído vai parar, e como ele é gravado.

Dono único da política de backup do Koine. Antes existia duplicada em
`conflito.py` (arquivo gerado na pasta de sessão) e em `ficha.py` (escrita de
frontmatter), com o comentário da segunda dizendo que copiava a primeira — uma
terceira cópia viraria drift.
"""
import os
import shutil

from koine import paths


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


def destino(versao: str, categoria: str, rel: str) -> str:
    """Caminho do backup na árvore do cache.

    FORA de qualquer pasta que outra coisa enumere. Backup gravado ao lado do
    original, no vault, casa o filtro `kn-*` do instalador de skills e é copiado
    para o harness COMO SE FOSSE UMA SKILL — medido em 27/08/2026. No harness o
    efeito se repete pelo lado do cliente, que lista o diretório.

    `versao` é a versão que está ENTRANDO: a proveniência do conteúdo
    substituído é desconhecível por desenho.
    """
    return os.path.join(paths.cache_dir(), "backups", versao,
                        *categoria.split("/"), *rel.split("/"))


def guardar(origem: str, versao: str, categoria: str, rel: str) -> str:
    """Copia `origem` para a árvore de backups e devolve o caminho gravado.

    COPIA, não move — de propósito. Mover deixaria o usuário sem o artefato caso
    a substituição falhasse logo depois, que é o defeito do `.bak` órfão pago na
    v0.5.3 no caminho do frontmatter. Com cópia, o pior caso é um backup a mais.
    """
    alvo = caminho_livre(destino(versao, categoria, rel))
    os.makedirs(os.path.dirname(alvo), exist_ok=True)
    if os.path.isdir(origem):
        shutil.copytree(origem, alvo)
    else:
        shutil.copy2(origem, alvo)
    return alvo
