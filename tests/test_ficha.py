"""Escrita de frontmatter em disco — o único ponto do código que grava.

Regras que não se negociam: backup antes, nunca em não-regular, nunca no vault
instalado, e falhar em gravar jamais derruba a sessão.
"""
import os

from koine import ficha

TORTO = "---\nescopo: x\ndescricao: Vendas B2B: metas\n---\n\n# Corpo\n"
BOM = '---\nescopo: x\ndescricao: "Vendas B2B: metas"\n---\n\n# Corpo\n'


def _arquivo(base, conteudo, nome="CONTEXTO.md"):
    p = os.path.join(str(base), nome)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(conteudo)
    return p


def test_normaliza_e_deixa_backup(tmp_path):
    p = _arquivo(tmp_path, TORTO)
    assert ficha.normalizar_arquivo(p) == ["descricao"]
    assert open(p, encoding="utf-8").read() == BOM
    assert open(p + ".bak", encoding="utf-8").read() == TORTO


def test_arquivo_valido_nao_e_reescrito_nem_gera_backup(tmp_path):
    p = _arquivo(tmp_path, BOM)
    assert ficha.normalizar_arquivo(p) == []
    assert open(p, encoding="utf-8").read() == BOM   # conteúdo, não mtime
    assert not os.path.exists(p + ".bak")


def test_segunda_passada_nao_gera_novo_backup(tmp_path):
    p = _arquivo(tmp_path, TORTO)
    ficha.normalizar_arquivo(p)
    assert ficha.normalizar_arquivo(p) == []
    assert not os.path.exists(p + ".bak.1")


def test_backup_procura_nome_livre(tmp_path):
    p = _arquivo(tmp_path, TORTO)
    open(p + ".bak", "w").close()  # sobra de uma correção anterior
    ficha.normalizar_arquivo(p)
    assert os.path.exists(p + ".bak.1")


def test_crlf_preservado_byte_a_byte(tmp_path):
    p = _arquivo(tmp_path, TORTO.replace("\n", "\r\n"))
    assert ficha.normalizar_arquivo(p) == ["descricao"]
    with open(p, "rb") as f:
        bruto = f.read()
    assert b"\r\n" in bruto
    assert b"\n" not in bruto.replace(b"\r\n", b"")


def test_irreparavel_fica_intacto(tmp_path):
    ruim = "---\nchave:\n\t- item\n---\n"
    p = _arquivo(tmp_path, ruim)
    assert ficha.normalizar_arquivo(p) == []
    assert open(p, encoding="utf-8").read() == ruim
    assert not os.path.exists(p + ".bak")


def test_symlink_nunca_e_reescrito(tmp_path):
    alvo = _arquivo(tmp_path, TORTO, "real.md")
    link = os.path.join(str(tmp_path), "link.md")
    os.symlink(alvo, link)
    assert ficha.normalizar_arquivo(link) == []
    assert open(alvo, encoding="utf-8").read() == TORTO


def test_arquivo_inexistente_nao_estoura(tmp_path):
    assert ficha.normalizar_arquivo(os.path.join(str(tmp_path), "nada.md")) == []


def test_vault_instalado_nunca_e_normalizado(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    vault = tmp_path / ".local" / "share" / "koine" / "agentes"
    vault.mkdir(parents=True)
    p = _arquivo(vault, TORTO, "hermes.md")
    assert ficha.normalizar_arquivo(p) == []
    assert open(p, encoding="utf-8").read() == TORTO


def test_falha_de_escrita_nao_propaga(tmp_path, monkeypatch, capsys):
    p = _arquivo(tmp_path, TORTO)

    def explode(*a, **k):
        raise PermissionError("somente leitura")

    monkeypatch.setattr("koine.ficha._gravar", explode)
    assert ficha.normalizar_arquivo(p) == []   # degrada, não levanta
    assert "não consegui" in capsys.readouterr().err


def test_falha_de_escrita_avisa_uma_vez_por_arquivo(koine_home, monkeypatch, capsys):
    """O launch lê o mesmo CONTEXTO.md em três pontos. Se a escrita falha
    (arquivo somente-leitura — Windows corporativo), o usuário não pode levar
    três avisos idênticos empilhados."""
    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)
    ctx = os.path.join(koine_home["trab"], "CONTEXTO.md")
    with open(ctx, "w", encoding="utf-8") as f:
        f.write("---\nescopo: fixture\ndescricao: Vendas B2B: metas\n---\n")

    def explode(*a, **k):
        raise PermissionError("somente leitura")

    monkeypatch.setattr("koine.ficha._gravar", explode)
    assert cli.main(["claude", "hermes", koine_home["trab"]]) == 0
    assert capsys.readouterr().err.count("não consegui corrigir") == 1
