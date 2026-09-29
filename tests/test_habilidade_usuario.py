import os

import pytest

from koine import frontmatter, habilidade_usuario as hu, paths


def _home_isolada(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    for k in ("XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
        monkeypatch.delenv(k, raising=False)
    return home


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


def test_pasta_usuario_fica_dentro_do_config_dir(tmp_path, monkeypatch):
    _home_isolada(tmp_path, monkeypatch)
    assert hu.pasta_usuario() == os.path.join(paths.config_dir(), "habilidades")


def test_criar_grava_skill_md_com_frontmatter_correto(tmp_path, monkeypatch):
    _home_isolada(tmp_path, monkeypatch)

    caminho = hu.criar("organiza-inbox", "Organiza o inbox do Gmail", "Corpo da skill.")

    assert caminho == os.path.join(hu.pasta_usuario(), "organiza-inbox", "SKILL.md")
    fm, corpo = frontmatter.ler_arquivo(caminho)
    assert fm["name"] == "organiza-inbox"
    assert fm["description"] == "Organiza o inbox do Gmail"
    assert fm["origem"] == "usuario"
    assert corpo.strip() == "Corpo da skill."


def test_criar_recusa_nome_invalido(tmp_path, monkeypatch):
    _home_isolada(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="inválido"):
        hu.criar("Nome_Invalido", "descrição", "corpo")


def test_criar_recusa_colisao_com_vault(tmp_path, monkeypatch):
    # nome sem o prefixo kn-<dois dígitos>- — testa a colisão de nome com o
    # vault isoladamente da regra de nome reservado (Task 2)
    _home_isolada(tmp_path, monkeypatch)
    vault = tmp_path / "vault"
    (vault / "habilidades" / "organiza-inbox").mkdir(parents=True)
    monkeypatch.setattr(paths, "vault_dir", lambda: str(vault))

    with pytest.raises(ValueError, match="produto"):
        hu.criar("organiza-inbox", "descrição", "corpo")


def test_criar_recusa_colisao_com_skill_de_usuario_existente(tmp_path, monkeypatch):
    _home_isolada(tmp_path, monkeypatch)
    hu.criar("organiza-inbox", "primeira versão", "corpo 1")

    with pytest.raises(ValueError, match="já existe"):
        hu.criar("organiza-inbox", "segunda tentativa", "corpo 2")
