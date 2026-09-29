from koine import habilidade_usuario as hu


def test_nome_valido_aceita_kebab_case_simples():
    assert hu.nome_valido("organiza-inbox")


def test_nome_valido_rejeita_maiuscula():
    assert not hu.nome_valido("Organiza-Inbox")


def test_nome_valido_rejeita_underscore():
    assert not hu.nome_valido("organiza_inbox")


def test_nome_reservado_ao_produto_bloco_kn_nn():
    assert hu.nome_reservado("kn-05-cria-skill")
    assert hu.nome_reservado("kn-99-encerra-sessao")


def test_nome_kn_sem_dois_digitos_nao_e_reservado():
    # o prefixo kn- sozinho não é reservado — só kn-<dois digitos>-
    assert not hu.nome_reservado("kn-organiza-inbox")


def test_descricao_dentro_do_limite():
    assert hu.descricao_valida("x" * 1024)
    assert hu.descricao_valida("x")


def test_descricao_fora_do_limite():
    assert not hu.descricao_valida("")
    assert not hu.descricao_valida("x" * 1025)


def test_validar_devolve_none_quando_tudo_certo():
    assert hu.validar("organiza-inbox", "Organiza o inbox do Gmail") is None


def test_validar_recusa_nome_invalido():
    erro = hu.validar("Organiza_Inbox", "descrição válida")
    assert erro is not None
    assert "organiza_inbox" in erro.lower() or "nome" in erro.lower()


def test_validar_recusa_nome_reservado():
    erro = hu.validar("kn-05-outro-nome", "descrição válida")
    assert erro is not None
    assert "reservado" in erro.lower()


def test_validar_recusa_descricao_vazia():
    erro = hu.validar("organiza-inbox", "")
    assert erro is not None
