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


def compor(valor, pasta, *, expandir=os.path.expandvars):
    """O valor novo do PATH, ou None quando não há nada a fazer.

    Só a NOSSA entrada é tocada: acrescenta quando falta, e colapsa duplicata
    dela. Entrada de terceiro — inclusive duplicata óbvia e `;;` no MEIO — fica
    byte a byte, porque a máquina não é nossa (decisão do Orlando, 28/08).
    """
    alvo = _normalizar(pasta, expandir)
    partes = valor.split(";")
    saida, vista = [], False
    for p in partes:
        if p and _normalizar(p, expandir) == alvo:
            if vista:
                continue          # duplicata NOSSA: colapsa
            vista = True
        saida.append(p)
    if vista and len(saida) == len(partes) and (not saida or saida[-1] != ""):
        return None               # já estava, sem duplicata nem cauda: nada a escrever
    # A cauda vazia sai nos DOIS caminhos, e é a ÚNICA exceção ao "não tocamos no
    # que é de terceiro": ela vira `;;` no próximo append de quem quer que seja, e
    # já é uma entrada "diretório atual". Duas regras para a mesma coisa produziria
    # o defeito por um dos lados.
    while saida and saida[-1] == "":
        saida.pop()
    if not vista:
        saida.append(pasta)
    return ";".join(saida)
