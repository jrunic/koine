from tests._parity import normalize, parity

GO = "# CLAUDE.md\n*Gerado por kn-agente em 2026-07-07 10:00. regerar com `kn-agente x .`.*\n@/a\n@/b\n"


def test_normalizer_ignora_timestamp():
    outro_ts = GO.replace("10:00", "23:59")
    assert normalize(GO) == normalize(outro_ts)


def test_normalizer_ignora_linha_de_regeneracao():
    outro_cmd = GO.replace("kn-agente x .", "kn-claude .")
    assert normalize(GO) == normalize(outro_cmd)


def test_normalizer_pega_diferenca_real_de_conteudo():
    corpo = GO.replace("@/b", "@/c")
    assert normalize(GO) != normalize(corpo)


def test_stub_que_ecoa_go_reporta_paridade():
    py_stub = GO  # stub: devolve exatamente os bytes do Go
    assert parity(GO, py_stub) is True
