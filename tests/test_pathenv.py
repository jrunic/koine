from koine import pathenv


def test_reconhece_a_pasta_ja_presente():
    assert pathenv.ja_tem(r"C:\Windows;C:\Users\x\.local\bin", r"C:\Users\x\.local\bin",
                          expandir=lambda s: s)


def test_reconhece_a_pasta_em_forma_NAO_expandida():
    # Medido na bancada: o Path real carrega %USERPROFILE% sem expandir. Comparar
    # cru acrescentaria uma segunda entrada para a MESMA pasta.
    def expandir(s):
        return s.replace("%USERPROFILE%", r"C:\Users\x")

    assert pathenv.ja_tem(r"C:\Windows;%USERPROFILE%\.local\bin", r"C:\Users\x\.local\bin",
                          expandir=expandir)


def test_comparacao_ignora_caixa_e_barra_final():
    # O Windows é case-insensitive, e a entrada pode ou não terminar em `\`.
    assert pathenv.ja_tem("c:\\users\\x\\.local\\bin\\", r"C:\Users\X\.local\bin",
                          expandir=lambda s: s)


def test_pasta_ausente_nao_e_reconhecida():
    assert not pathenv.ja_tem(r"C:\Windows;C:\outra", r"C:\Users\x\.local\bin",
                              expandir=lambda s: s)


def test_entrada_vazia_no_path_nao_confunde():
    # `;;` produz entrada vazia, que alguns resolvedores leem como diretório atual.
    assert not pathenv.ja_tem(r"C:\Windows;;C:\outra", r"C:\Users\x\.local\bin",
                              expandir=lambda s: s)
