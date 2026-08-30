from koine import cache


def test_slot_id_deterministico():
    a = cache.slot_id("/x/y")
    assert a == cache.slot_id("/x/y")
    assert len(a) == 12 and a != cache.slot_id("/x/z")


def test_caminho_bundle(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    b = cache.caminho_bundle("copilot-bundles", "abc")
    assert b.endswith("/.cache/koine/copilot-bundles/abc")


def test_caminho_arquivo(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    p = cache.caminho_arquivo("opencode-configs", "abc", "json")
    assert p.endswith("/.cache/koine/opencode-configs/abc.json")


def test_slot_de_sessao_separa_agentes_na_mesma_pasta():
    """O slot da SESSÃO é pasta + agente; o da PASTA continua sendo só a pasta.

    Os dois existem porque respondem perguntas diferentes: a foto da Ficha Koine
    é da pasta, e o contexto entregue ao cliente é da sessão. Confundi-los é o
    que fazia dois providers do mesmo workspace se sobrescreverem (jd-task #708).
    """
    a = cache.slot_sessao("/x/y", "hermes")
    assert a == cache.slot_sessao("/x/y", "hermes")
    assert len(a) == 12
    assert a != cache.slot_sessao("/x/y", "bruce"), "mesmo slot para agentes diferentes"
    assert a != cache.slot_sessao("/x/z", "hermes")
    assert a != cache.slot_id("/x/y"), "o slot da sessão não colide com o da pasta"


def test_slot_de_sessao_nao_colide_por_concatenacao():
    """`/x` + `y/hermes` e `/x/y` + `hermes` são sessões DIFERENTES.

    Sem separador que não ocorra nos dois campos, as duas concatenariam para a
    mesma string e dividiriam o cache — o defeito que este slot existe para não
    ter, reintroduzido pela porta dos fundos.
    """
    # o par tem que COLIDIR sob concatenação simples, senão o teste não mede
    # nada: "/x/y"+"ab" e "/x/ya"+"b" dão a MESMA string, "/x/yab".
    assert "/x/y" + "ab" == "/x/ya" + "b"
    assert cache.slot_sessao("/x/y", "ab") != cache.slot_sessao("/x/ya", "b")
