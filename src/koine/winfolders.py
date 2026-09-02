"""Known folders do Windows — onde `Documentos`, `Área de Trabalho` e `Imagens`
realmente estão para este usuário.

Existe porque `home:` concatena, e com Known Folder Move o caminho concatenado
aponta para uma casca vazia: o conteúdo foi para dentro do OneDrive corporativo.
O registro é a única fonte que sabe o destino (jd-task #762).

Cobre as três que o KFM move. Música, vídeos e downloads têm valor no registro e
ficam de fora de propósito — o KFM não as move por padrão, e cada nome coberto é
mais superfície para envelhecer.
"""
import os
import sys

# Nome do segmento no caminho tagged -> nome do valor no registro. Os dois lados
# diferem, e supor que são iguais é o erro que este mapa existe para evitar.
KNOWN = {
    "documents": "Personal",
    "desktop": "Desktop",
    "pictures": "My Pictures",
}

_CHAVE = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"


class RegistroUsuario:
    """Leitura de `HKCU\\...\\User Shell Folders`. Só existe no Windows; é a
    costura que a suíte substitui, e por isso o `import winreg` mora DENTRO do
    método — mesma forma do `pathenv.RegistroUsuario`."""

    def ler(self, valor: str):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _CHAVE) as k:
                bruto, _tipo = winreg.QueryValueEx(k, valor)
                return bruto
        except FileNotFoundError:
            return None


def resolver(segmento: str, *, reg=None, expandir=os.path.expandvars,
             windows=None) -> str | None:
    """Caminho real da known folder que `segmento` nomeia, ou `None`.

    `None` significa "não há resposta melhor que a concatenação" — fora do
    Windows, para segmento que não é known folder coberta, e para qualquer
    tropeço de leitura. Nunca levanta: falha de registro não pode derrubar uma
    sessão por causa de um caminho.

    O valor vem `REG_EXPAND_SZ`, com `%USERPROFILE%` **não expandido** (medido em
    02/09/2026) — expandir é obrigatório, não zelo.
    """
    e_windows = sys.platform == "win32" if windows is None else windows
    if not e_windows:
        return None
    nome = KNOWN.get(segmento.strip().lower())
    if nome is None:
        return None
    try:
        bruto = (reg if reg is not None else RegistroUsuario()).ler(nome)
    except (OSError, ImportError):
        # ImportError junto: `winreg` não existe em Python sem Windows, e a
        # promessa de "nunca levanta" é absoluta. Mesmo motivo do `pathenv`.
        return None
    return expandir(bruto) if bruto else None
