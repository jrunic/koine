from koine import agente


def test_posicional_vence_tudo():
    nome, fonte = agente.resolver_nome(posicional="atlas",
                                       fm_pasta={"agente": "leia"},
                                       default_usuario="hermes")
    assert (nome, fonte) == ("atlas", agente.POSICIONAL)


def test_pasta_vence_default():
    nome, fonte = agente.resolver_nome(posicional="", fm_pasta={"agente": "leia"},
                                       default_usuario="atlas")
    assert (nome, fonte) == ("leia", agente.PASTA)


def test_default_quando_a_pasta_nao_declara():
    nome, fonte = agente.resolver_nome(posicional="", fm_pasta={},
                                       default_usuario="atlas")
    assert (nome, fonte) == ("atlas", agente.DEFAULT)


def test_hermes_quando_nao_ha_nada():
    nome, fonte = agente.resolver_nome(posicional="", fm_pasta={},
                                       default_usuario="")
    assert (nome, fonte) == ("hermes", agente.FALLBACK)


def test_a_fonte_distingue_valores_iguais():
    """O discriminante do tratamento de agente inexistente é a FONTE, não o
    nome. Se os dois caminhos devolvessem o mesmo valor sem a fonte, o ramo de
    erro e o de recuperação ficariam indistinguíveis."""
    a = agente.resolver_nome(posicional="leia", fm_pasta={"agente": "leia"},
                             default_usuario="leia")
    b = agente.resolver_nome(posicional="", fm_pasta={"agente": "leia"},
                             default_usuario="leia")
    assert a[0] == b[0] == "leia"
    assert a[1] != b[1]


import os
import pathlib

import pytest

from koine import contexto

VALIDO = """---
escopo: fixture
dominios: [tecnologia]
agente: {agente}
---

# Pasta
"""


def _pasta_valido(koine_home, agente_declarado):
    """Reusa a pasta de trabalho da seed: ela já tem o escopo `fixture`
    cadastrado no config, que é o que o ramo VALIDO exige."""
    d = pathlib.Path(koine_home["trab"])
    (d / "CONTEXTO.md").write_text(VALIDO.format(agente=agente_declarado),
                                   encoding="utf-8")
    return str(d)


def test_pasta_declarada_abre_com_o_agente_da_pasta(koine_home, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "hermes")
    cm = contexto.resolver("", pasta)
    assert cm.agente_path.endswith("hermes.md")


def test_bootstrap_ignora_o_agente_pedido(koine_home, tmp_path, monkeypatch):
    """Regressão: fora de VALIDO nada muda — é o Hermes que carrega a
    instrução de consertar a pasta."""
    monkeypatch.setenv("HOME", koine_home["home"])
    d = tmp_path / "boot"
    d.mkdir()
    (d / "CONTEXTO.md").write_text("---\nbootstrap: true\n---\n", encoding="utf-8")
    cm = contexto.resolver("atlas", str(d))
    assert cm.bootstrap is True
    assert cm.agente_path.endswith("hermes.md")
