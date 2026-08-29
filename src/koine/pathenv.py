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


ADICIONADO = "adicionado"
JA_ESTAVA = "ja_estava"
FALHOU = "falhou"

REG_EXPAND_SZ = 2   # winreg.REG_EXPAND_SZ, sem importar winreg fora do Windows
_CHAVE = "Environment"
_VALOR = "Path"


class RegistroUsuario:
    """Acesso ao HKCU\\Environment. Só existe no Windows; é a costura que a suíte
    substitui, e por isso o `import winreg` mora DENTRO dos métodos."""

    def ler(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CHAVE) as k:
                valor, tipo = winreg.QueryValueEx(k, _VALOR)
                return valor, tipo
        except FileNotFoundError:
            return None, None

    def gravar(self, valor, tipo):
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CHAVE, 0,
                            winreg.KEY_READ | winreg.KEY_WRITE) as k:
            winreg.SetValueEx(k, _VALOR, 0, tipo, valor)


def garantir(pasta, *, reg=None, expandir=os.path.expandvars, notificar=None):
    """Acrescenta a pasta ao PATH do usuário se faltar. Devolve o status.

    Nunca levanta: registro negado por política vira FALHOU, e o chamador cai na
    orientação manual. Derrubar a instalação por causa do PATH seria trocar um
    problema pequeno por um grande.
    """
    reg = reg if reg is not None else RegistroUsuario()
    notificar = notificar if notificar is not None else broadcast
    try:
        valor, tipo = reg.ler()
    except OSError:
        return FALHOU
    novo = compor(valor or "", pasta, expandir=expandir)
    if novo is None:
        return JA_ESTAVA
    try:
        # o tipo ORIGINAL volta; criando do zero, EXPAND_SZ
        reg.gravar(novo, tipo if tipo is not None else REG_EXPAND_SZ)
    except OSError:
        return FALHOU
    notificar()
    return ADICIONADO
