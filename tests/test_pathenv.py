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


def test_compor_acrescenta_no_fim():
    assert pathenv.compor(r"C:\Windows", r"C:\bin", expandir=lambda s: s) == r"C:\Windows;C:\bin"


def test_compor_nao_produz_separador_duplo():
    # Medido na bancada em 28/08: o valor anterior terminava em `;` e o append
    # produziu `;;`. Entrada vazia é lida como DIRETÓRIO ATUAL por alguns
    # resolvedores — não é cosmético.
    assert pathenv.compor(r"C:\Windows;", r"C:\bin", expandir=lambda s: s) == r"C:\Windows;C:\bin"


def test_compor_devolve_None_quando_nao_ha_o_que_fazer():
    # Idempotência: segunda passada não muda nada, então não escreve nada.
    assert pathenv.compor(r"C:\Windows;C:\bin", r"C:\bin", expandir=lambda s: s) is None


def test_compor_deduplica_a_NOSSA_entrada():
    novo = pathenv.compor(r"C:\bin;C:\Windows;C:\bin", r"C:\bin", expandir=lambda s: s)
    assert novo == r"C:\bin;C:\Windows"


def test_compor_deduplica_a_nossa_entrada_em_forma_nao_expandida():
    def expandir(s):
        return s.replace("%U%", r"C:\Users\x")
    novo = pathenv.compor(r"%U%\bin;C:\Windows;C:\Users\x\bin", r"C:\Users\x\bin",
                          expandir=expandir)
    # a PRIMEIRA sobrevive, com a forma crua preservada
    assert novo == r"%U%\bin;C:\Windows"


def test_compor_deduplica_E_limpa_a_cauda_vazia_no_mesmo_passo():
    # O caso combinado: nossa entrada duplicada E valor terminando em `;`. Sem
    # isto, o caminho do dedupe deixaria a cauda vazia que o caminho do acréscimo
    # remove — duas regras para a mesma coisa, e a cauda vira `;;` no próximo
    # append de quem quer que seja.
    novo = pathenv.compor(r"C:\bin;C:\Windows;C:\bin;", r"C:\bin", expandir=lambda s: s)
    assert novo == r"C:\bin;C:\Windows"


def test_compor_NAO_toca_em_duplicata_de_TERCEIRO():
    # Critério negativo: a máquina não é nossa. A poluição medida na bancada
    # (system32 duplicado) fica exatamente onde está.
    valor = r"C:\Windows\system32;C:\Windows;C:\Windows\system32"
    assert pathenv.compor(valor, r"C:\bin", expandir=lambda s: s) == valor + r";C:\bin"


def test_compor_preserva_entrada_vazia_NO_MEIO():
    # `;;` no meio não é nosso para consertar — só a CAUDA sai, porque é ela que
    # vira `;;` no próximo append.
    valor = r"C:\Windows;;C:\outra"
    assert pathenv.compor(valor, r"C:\bin", expandir=lambda s: s) == valor + r";C:\bin"
