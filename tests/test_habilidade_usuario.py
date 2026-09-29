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


from koine import skills


def test_distribuir_copia_para_harness_detectado(tmp_path, monkeypatch):
    home = _home_isolada(tmp_path, monkeypatch)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: home))
    hu.criar("organiza-inbox", "descrição", "corpo")

    criadas, atualizadas, ignoradas = hu.distribuir("organiza-inbox", ["claude"])

    assert criadas == ["claude"]
    assert atualizadas == []
    assert ignoradas == []
    destino = home / ".claude" / "skills" / "organiza-inbox" / "SKILL.md"
    assert destino.exists()


def test_distribuir_e_idempotente_na_segunda_chamada(tmp_path, monkeypatch):
    home = _home_isolada(tmp_path, monkeypatch)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: home))
    hu.criar("organiza-inbox", "descrição", "corpo")
    hu.distribuir("organiza-inbox", ["claude"])

    criadas, atualizadas, ignoradas = hu.distribuir("organiza-inbox", ["claude"])

    assert criadas == atualizadas == ignoradas == []


def test_distribuir_atualiza_quando_conteudo_diverge(tmp_path, monkeypatch):
    home = _home_isolada(tmp_path, monkeypatch)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: home))
    hu.criar("organiza-inbox", "descrição v1", "corpo v1")
    hu.distribuir("organiza-inbox", ["claude"])
    # usuário roda de novo e muda a descrição/corpo — precisa recriar o
    # arquivo canônico antes (mesma pasta, mesmo nome, conteúdo novo)
    caminho = os.path.join(hu.pasta_usuario(), "organiza-inbox", "SKILL.md")
    fm = {"name": "organiza-inbox", "description": "descrição v2", "origem": "usuario"}
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(frontmatter.compor(fm) + "\n\ncorpo v2\n")

    criadas, atualizadas, ignoradas = hu.distribuir("organiza-inbox", ["claude"])

    assert atualizadas == ["claude"]
    destino = home / ".claude" / "skills" / "organiza-inbox" / "SKILL.md"
    assert "descrição v2" in destino.read_text()


def test_distribuir_ignora_harness_com_skill_de_terceiro(tmp_path, monkeypatch):
    home = _home_isolada(tmp_path, monkeypatch)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: home))
    hu.criar("organiza-inbox", "descrição", "corpo")
    alheio = home / ".claude" / "skills" / "organiza-inbox"
    alheio.mkdir(parents=True)
    (alheio / "SKILL.md").write_text(
        "---\nname: organiza-inbox\ndescription: skill de terceiro\n---\n\ncorpo alheio\n")

    criadas, atualizadas, ignoradas = hu.distribuir("organiza-inbox", ["claude"])

    assert ignoradas == ["claude"]
    assert criadas == atualizadas == []
    assert "corpo alheio" in alheio.joinpath("SKILL.md").read_text()


def test_koine_instalar_nao_toca_a_copia_de_skill_de_usuario_no_harness(
        tmp_path, monkeypatch):
    """Guarda de regressão: `instalar_habilidades_detalhado` só itera o que
    EXISTE no vault (`os.listdir(vault_dir()/habilidades)`) — skill de
    usuário nunca mora lá, então nunca entra no laço, e o filtro
    `startswith('kn-')` nem chega a ser consultado para ela. A proteção
    quebraria se o mecanismo ganhasse semântica de "poda" (remover do
    harness o que não existe mais no vault) — este teste avisa se isso
    acontecer sem essa distinção ser revisitada."""
    home = _home_isolada(tmp_path, monkeypatch)
    monkeypatch.setattr(skills.Path, "home", staticmethod(lambda: home))
    hu.criar("organiza-inbox", "descrição", "corpo do usuário")
    hu.distribuir("organiza-inbox", ["claude"])
    destino = home / ".claude" / "skills" / "organiza-inbox" / "SKILL.md"
    conteudo_antes = destino.read_text()

    vault_falso = tmp_path / "vault-falso"
    (vault_falso / "habilidades" / "kn-99-encerra-sessao").mkdir(parents=True)
    (vault_falso / "habilidades" / "kn-99-encerra-sessao" / "SKILL.md").write_text("x")
    monkeypatch.setattr(paths, "vault_dir", lambda: str(vault_falso))

    skills.instalar_habilidades_detalhado("claude", "0.0.1")

    assert destino.read_text() == conteudo_antes
