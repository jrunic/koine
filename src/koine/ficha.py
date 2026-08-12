"""Escrita de frontmatter em disco — o único ponto do código que grava Ficha
Koine em arquivo do usuário.

A leitura repara em memória (bug reportado em produção), mas o arquivo continua torto para
qualquer outra ferramenta e o usuário nunca fica sabendo. Aqui o conserto é
feito de verdade, sob três regras: backup antes de escrever, nunca tocar no que
não é arquivo regular nosso, e falhar em gravar jamais derrubar a sessão.
"""

import os
import sys

from koine import frontmatter, paths

# Paths já reportados neste processo — o launch lê o mesmo CONTEXTO.md em três
# pontos e o escopo em dois. Quando a correção dá certo a repetição some sozinha
# (a segunda leitura acha o arquivo válido), mas quando a escrita falha — arquivo
# somente-leitura, o caso do Windows corporativo — o mesmo aviso sairia empilhado.
_reportados: set[str] = set()


def normalizar_arquivo(path: str) -> list[str]:
    """Conserta o frontmatter de `path` no disco. Devolve as chaves corrigidas;
    lista vazia significa que nada foi escrito — arquivo já válido, irreparável,
    fora do nosso alcance, ou escrita que falhou."""
    if not _pode_escrever(path):
        return []
    try:
        with open(path, encoding="utf-8", newline="") as f:
            texto = f.read()   # newline="" preserva CRLF na leitura
    except (OSError, UnicodeDecodeError):
        return []
    novo, chaves = frontmatter.normalizar(texto)
    if not chaves:
        return []
    try:
        _backup(path, texto)
        _gravar(path, novo)
    except OSError as e:
        _reportar(path, f"aviso: não consegui corrigir o frontmatter de {path} "
                        f"({e}). A sessão segue — o Koine lê o arquivo "
                        f"reparando em memória.")
        return []
    campos = ", ".join(f"`{c}`" for c in chaves)
    _reportar(path, f"aviso: em {path}, o valor de {campos} tinha `:` sem "
                    f"aspas — corrigido. Original em "
                    f"{os.path.basename(path)}.bak")
    return chaves


def _reportar(path: str, mensagem: str) -> None:
    chave = os.path.abspath(path)
    if chave in _reportados:
        return
    _reportados.add(chave)
    print(mensagem, file=sys.stderr)


def _pode_escrever(path: str) -> bool:
    """Arquivo regular, fora do vault instalado. O vault é readonly em runtime
    (quem o escreve é o `koine instalar`) e symlink seria escrita atravessada."""
    if os.path.islink(path) or not os.path.isfile(path):
        return False
    try:
        vault = os.path.realpath(paths.vault_dir())
    except OSError:
        return True
    return not os.path.realpath(path).startswith(vault + os.sep)


def _backup(path: str, texto: str) -> None:
    """`.bak` livre, mesma política do conflito.py: nunca sobrescreve backup."""
    destino, n = path + ".bak", 0
    while os.path.exists(destino):
        n += 1
        destino = f"{path}.bak.{n}"
    with open(destino, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


def _gravar(path: str, texto: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
