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


class RegistroFalso:
    """Duplo do HKCU\\Environment. Guarda valor E tipo — o tipo é metade do que
    esta tarefa protege: `setx` grava REG_SZ e destrói as %VAR%."""

    EXPAND_SZ = 2
    SZ = 1

    def __init__(self, valor=None, tipo=None, negar_escrita=False):
        self.valor, self.tipo = valor, tipo
        self.negar_escrita = negar_escrita
        self.escritas = []

    def ler(self):
        if self.valor is None:
            return None, None
        return self.valor, self.tipo

    def gravar(self, valor, tipo):
        if self.negar_escrita:
            raise PermissionError("acesso negado pela política")
        self.valor, self.tipo = valor, tipo
        self.escritas.append((valor, tipo))


def test_garantir_acrescenta_e_preserva_o_tipo():
    reg = RegistroFalso(r"C:\Windows", RegistroFalso.EXPAND_SZ)
    st = pathenv.garantir(r"C:\bin", reg=reg, expandir=lambda s: s, notificar=lambda: True)
    assert st == pathenv.ADICIONADO
    assert reg.valor == r"C:\Windows;C:\bin"
    assert reg.tipo == RegistroFalso.EXPAND_SZ      # o tipo original volta


def test_garantir_e_idempotente_e_nao_escreve_de_novo():
    reg = RegistroFalso(r"C:\Windows", RegistroFalso.EXPAND_SZ)
    for _ in range(3):
        st = pathenv.garantir(r"C:\bin", reg=reg, expandir=lambda s: s, notificar=lambda: True)
    assert st == pathenv.JA_ESTAVA
    assert len(reg.escritas) == 1                   # escreveu UMA vez em três
    assert reg.valor == r"C:\Windows;C:\bin"


def test_garantir_cria_o_valor_quando_nao_existe():
    reg = RegistroFalso()
    st = pathenv.garantir(r"C:\bin", reg=reg, expandir=lambda s: s, notificar=lambda: True)
    assert st == pathenv.ADICIONADO
    assert reg.valor == r"C:\bin"
    assert reg.tipo == pathenv.REG_EXPAND_SZ        # cria como EXPAND_SZ


def test_escrita_negada_degrada_e_nao_levanta():
    # Estação onde até o registro é negado: a instalação TERMINA.
    reg = RegistroFalso(r"C:\Windows", RegistroFalso.EXPAND_SZ, negar_escrita=True)
    st = pathenv.garantir(r"C:\bin", reg=reg, expandir=lambda s: s, notificar=lambda: True)
    assert st == pathenv.FALHOU


def test_broadcast_usa_SendMessageTimeoutW_e_nao_o_bloqueante(monkeypatch):
    # SendMessage bloqueante pendura o instalador quando uma janela não responde
    # — é a família do shell órfão que esta frota já pagou.
    chamadas = {}

    class FakeUser32:
        def SendMessageTimeoutW(self, *a):
            chamadas["args"] = a
            return 1

    monkeypatch.setattr(pathenv, "_user32", lambda: FakeUser32())
    assert pathenv.broadcast() is True
    assert chamadas["args"][1] == pathenv.WM_SETTINGCHANGE


def test_broadcast_que_falha_nao_levanta(monkeypatch):
    # Best-effort: a escrita continua válida, e a mensagem manda reabrir o terminal.
    def explode():
        raise OSError("sem user32 aqui")

    monkeypatch.setattr(pathenv, "_user32", explode)
    assert pathenv.broadcast() is False


def test_garantir_degrada_quando_a_CAMADA_de_registro_nao_existe():
    # A docstring do `garantir` promete "nunca levanta" — e ele levantava:
    # ModuleNotFoundError é ImportError, não OSError. Achado pela suíte ao rodar
    # o instalar com sys.platform forçado a win32 fora do Windows, mas a promessa
    # é absoluta e vale para qualquer Python sem winreg.
    class RegistroQuebrado:
        def ler(self):
            raise ModuleNotFoundError("No module named 'winreg'")

        def gravar(self, valor, tipo):
            raise AssertionError("não devia chegar aqui")

    assert pathenv.garantir(r"C:\bin", reg=RegistroQuebrado(),
                            expandir=lambda s: s, notificar=lambda: True) == pathenv.FALHOU


def test_limpar_a_cauda_de_uma_pasta_JA_PRESENTE_nao_e_ADICIONADO():
    # Achado pelo fixture real da bancada: o Path da conta restrita já tem a
    # nossa pasta E termina em `;`. O `compor` devolve valor novo (a cauda sai),
    # mas dizer "acrescentado ao PATH" seria mentira — ela já estava.
    reg = RegistroFalso(r"C:\Windows;C:\bin;", RegistroFalso.EXPAND_SZ)
    st = pathenv.garantir(r"C:\bin", reg=reg, expandir=lambda s: s, notificar=lambda: True)
    assert st == pathenv.JA_ESTAVA
    assert reg.valor == r"C:\Windows;C:\bin"      # escreveu, limpando a cauda
