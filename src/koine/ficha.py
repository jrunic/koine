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

from koine import backup as _backup_mod

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
    # A permissão é checada aqui, e não descoberta pelo `_gravar` estourando: o
    # backup vem antes da escrita, então a falha tardia deixava um `.bak` órfão
    # — e, como o arquivo seguia torto, mais um a cada sessão. Visto na VM
    # AppLocker com `attrib +R`, que é o que máquina corporativa produz.
    if not os.access(path, os.W_OK):
        _reportar(path, f"aviso: {path} está somente-leitura — o frontmatter "
                        f"segue torto no disco. A sessão continua; o Koine lê o "
                        f"arquivo reparando em memória.")
        # sem isto o reparo em memória avisaria em seguida, mandando citar o
        # valor entre aspas — conselho impossível num arquivo somente-leitura
        frontmatter.silenciar_aviso(path)
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
    """Arquivo regular, gravável, fora do vault instalado. O vault é readonly em
    runtime (quem o escreve é o `koine instalar`) e symlink seria escrita
    atravessada.

    A permissão é checada aqui, e não descoberta pelo `_gravar` estourando: o
    backup vem antes da escrita, então a falha tardia deixava um `.bak` órfão —
    e, como o arquivo seguia torto, mais um a cada sessão. Visto na VM
    AppLocker com `attrib +R`, que é o que máquina corporativa produz."""
    if os.path.islink(path) or not os.path.isfile(path):
        return False
    try:
        vault = os.path.realpath(paths.vault_dir())
    except OSError:
        return True
    return not os.path.realpath(path).startswith(vault + os.sep)


def _backup(path: str, texto: str) -> None:
    """`.bak` livre ao lado do arquivo. A política do nome mora em koine.backup."""
    destino = _backup_mod.caminho_livre(path + ".bak")
    with open(destino, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


def _gravar(path: str, texto: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


def definir_campo_arquivo(path: str, chave: str, valor: str) -> bool:
    """Grava `chave: valor` no frontmatter de `path`. True se escreveu.

    Reusa as proteções do normalizar em vez de abrir um segundo caminho de
    escrita ao lado: `_pode_escrever` (arquivo regular, fora do vault, não
    symlink), permissão checada ANTES do backup (senão sobra `.bak` órfão —
    medido na VM AppLocker com `attrib +R`), e `newline=""` ponta a ponta para
    não trocar CRLF por LF no arquivo do usuário.
    """
    if not _pode_escrever(path):
        return False
    try:
        with open(path, encoding="utf-8", newline="") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        return False

    novo, mudou = frontmatter.definir_campo(texto, chave, valor)
    if not mudou:
        return False
    if not os.access(path, os.W_OK):
        _reportar(path, f"aviso: {path} está somente-leitura — não consegui "
                        f"gravar `{chave}: {valor}`.")
        return False
    try:
        _backup(path, texto)
        _gravar(path, novo)
    except OSError as e:
        _reportar(path, f"aviso: não consegui gravar `{chave}` em {path} ({e}).")
        return False
    return True


def repor_bloco(path: str, bloco: str) -> bool:
    """Devolve ao arquivo o bloco de frontmatter fotografado. True se escreveu.

    EXCEÇÃO NOMEADA à regra de não fabricar ficha. `frontmatter.definir_campo`
    recusa arquivo sem bloco de propósito — criar ficha ali seria o Koine
    inventando estado que ele decidiu não inventar (v0.6.1). Aqui não há
    invenção: o conteúdo é cópia literal do que o próprio arquivo tinha na
    última sessão que abriu bem. `definir_campo` continua recusando; a exceção
    mora aqui e em nenhum outro lugar.

    Bloco parcial é SUBSTITUÍDO, não mesclado — o que estava lá fica no `.bak`.
    """
    if not bloco or not _pode_escrever(path):
        return False
    try:
        with open(path, encoding="utf-8", newline="") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        return False
    if not os.access(path, os.W_OK):
        _reportar(path, f"aviso: {path} está somente-leitura — não consegui "
                        "repor a ficha.")
        return False

    fatia = frontmatter.fatiar_publico(texto)
    if fatia is None:
        # sub-caso (a): sem bloco. O corpo começa no início do arquivo, e o
        # terminador vem do BLOCO fotografado — é ele que dita o estilo do
        # frontmatter que está voltando.
        term = "\r\n" if "\r\n" in bloco else "\n"
        novo = bloco + term + term + texto.lstrip("\r\n")
    else:
        # sub-caso (b): bloco parcial, substituído inteiro
        novo = bloco + texto[fatia.fim_do_bloco:]

    try:
        _backup(path, texto)
        _gravar(path, novo)
    except OSError as e:
        _reportar(path, f"aviso: não consegui repor a ficha de {path} ({e}).")
        return False
    return True
