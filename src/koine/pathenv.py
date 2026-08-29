"""A entrada do Koine no `Path` do usuário, no Windows.

Duas camadas, separadas de propósito: a LÓGICA (presença, composição) é pura e
roda em qualquer SO; o ACESSO AO REGISTRO é costurado, porque `winreg` não existe
fora do Windows e o CI é POSIX-only.

Nunca `setx`: ele trunca a variável em 1024 caracteres EM SILÊNCIO e grava
`REG_SZ`, destruindo as `%VAR%` não expandidas que o `Path` real carrega.
"""
import os


def _normalizar(caminho, expandir):
    """Forma canônica para COMPARAR — nunca para gravar.

    Expande as `%VAR%` porque o Path real carrega `%USERPROFILE%` sem expandir e
    a entrada que vamos acrescentar vem expandida; sem isto o instalador
    duplicaria a mesma pasta. Caixa e `\\` final também não distinguem no Windows.
    """
    return expandir(caminho).rstrip("\\/").lower()


def ja_tem(valor, pasta, *, expandir=os.path.expandvars):
    """A pasta já está neste valor de PATH?"""
    alvo = _normalizar(pasta, expandir)
    return any(_normalizar(p, expandir) == alvo for p in valor.split(";") if p)
