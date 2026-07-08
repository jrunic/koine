import os

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


def test_ambiente_de_teste_sem_xdg():
    # Guarda de recorrência: runners CI (GitHub Actions ubuntu) exportam XDG_*.
    # paths.py e o Go honram XDG_* ANTES de HOME, então qualquer XDG_* visível
    # em os.environ vaza para subprocessos ({**os.environ, "HOME": ...}) e
    # quebra o isolamento por HOME dos fixtures. conftest._isola_xdg limpa.
    assert not [k for k in os.environ if k.startswith("XDG_")]
