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
