"""Onde o Windows guarda de verdade Documentos, Área de Trabalho e Imagens.

Com Known Folder Move — padrão de tenant Microsoft 365 — as três apontam para
dentro do OneDrive e o caminho antigo no perfil vira casca vazia. O registro é a
única fonte que sabe disso (jd-task #762, medido em produção em 02/09/2026).
"""
from koine import winfolders


class RegFalso:
    """Costura no lugar do registro real, para rodar em qualquer plataforma."""

    def __init__(self, valores):
        self.valores = valores
        self.pedidos = []

    def ler(self, valor):
        self.pedidos.append(valor)
        return self.valores.get(valor)


def test_documents_le_o_valor_Personal_e_expande():
    """O nome lógico no registro NÃO é o nome da pasta: Documentos é `Personal`,
    Imagens é `My Pictures`. Medido em Windows PT-BR, 02/09/2026."""
    reg = RegFalso({"Personal": "%USERPROFILE%\\OneDrive - ACME\\Documents"})
    achado = winfolders.resolver("Documents", reg=reg, windows=True,
                                 expandir=lambda s: s.replace("%USERPROFILE%", "C:\\u"))
    assert achado == "C:\\u\\OneDrive - ACME\\Documents"
    assert reg.pedidos == ["Personal"]


def test_fora_do_windows_nao_consulta_nada():
    reg = RegFalso({"Personal": "qualquer"})
    assert winfolders.resolver("Documents", reg=reg, windows=False) is None
    assert reg.pedidos == [], "não pode nem tocar no registro fora do Windows"


def test_segmento_que_nao_e_known_folder_coberta():
    reg = RegFalso({"Personal": "qualquer"})
    assert winfolders.resolver("projetos", reg=reg, windows=True) is None
    assert winfolders.resolver("Downloads", reg=reg, windows=True) is None, \
        "downloads tem valor no registro e está FORA de propósito"


def test_casamento_ignora_caixa_porque_caminho_no_windows_ignora():
    reg = RegFalso({"Personal": "C:\\real"})
    assert winfolders.resolver("documents", reg=reg, windows=True,
                               expandir=lambda s: s) == "C:\\real"
    assert winfolders.resolver("DOCUMENTS", reg=reg, windows=True,
                               expandir=lambda s: s) == "C:\\real"


def test_registro_que_explode_nao_levanta():
    class RegQueExplode:
        def ler(self, valor):
            raise OSError("acesso negado pela política")
    assert winfolders.resolver("Documents", reg=RegQueExplode(), windows=True) is None
