import os

from koine import instantaneo, paths

FICHA = "---\nescopo: projeto-x\ndominios: [tecnologia]\n---"


def test_guarda_e_devolve_a_ficha(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    pasta = str(tmp_path / "trab")

    instantaneo.guardar(pasta, FICHA)
    foto = instantaneo.recuperar(pasta)

    assert foto is not None
    assert foto.bloco == FICHA
    assert foto.quando, "sem a data o aviso não tem como dizer de quando é"


def test_a_foto_e_por_pasta(tmp_path, monkeypatch):
    """Com uma pasta só, uma implementação que guardasse foto GLOBAL passaria.
    Duas pastas com fichas diferentes é o que discrimina."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")

    instantaneo.guardar(a, "---\nescopo: alfa\n---")
    instantaneo.guardar(b, "---\nescopo: beta\n---")

    assert "alfa" in instantaneo.recuperar(a).bloco
    assert "beta" in instantaneo.recuperar(b).bloco


def test_sem_foto_devolve_none(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    assert instantaneo.recuperar(str(tmp_path / "nunca-vista")) is None


def test_guardar_de_novo_substitui_sem_acumular(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    pasta = str(tmp_path / "trab")

    instantaneo.guardar(pasta, "---\nescopo: velho\n---")
    instantaneo.guardar(pasta, "---\nescopo: novo\n---")

    assert "novo" in instantaneo.recuperar(pasta).bloco
    base = os.path.join(paths.cache_dir(), "fichas")
    assert len(os.listdir(base)) == 1, "uma foto por pasta, não um histórico"


def test_guardar_nunca_derruba_a_sessao(tmp_path, monkeypatch):
    """Fotografar é serviço, não requisito: erro vira silêncio."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    # patch estreito: `instantaneo.os` é o MESMO objeto módulo que todo mundo
    # importa — mexer nele quebraria qualquer outra chamada do teste.
    sem_permissao = tmp_path / "trancado"
    sem_permissao.mkdir()
    os.chmod(sem_permissao, 0o000)
    monkeypatch.setattr(instantaneo, "_caminho",
                        lambda p: str(sem_permissao / "sub" / "f.json"))
    try:
        instantaneo.guardar(str(tmp_path / "trab"), FICHA)   # não levanta
    finally:
        os.chmod(sem_permissao, 0o755)


from koine import ficha, frontmatter

CORPO = "# Projeto X\n\nCorpo que não pode ser tocado pela reposição.\n"


def test_repoe_quando_o_bloco_sumiu_inteiro(tmp_path):
    """Sub-caso (a): o arquivo ficou só com o corpo."""
    p = tmp_path / "CONTEXTO.md"
    p.write_text(CORPO, encoding="utf-8", newline="")

    assert ficha.repor_bloco(str(p), FICHA) is True

    texto = p.read_text()
    assert frontmatter.ler(texto)[0]["escopo"] == "projeto-x"
    assert "Corpo que não pode ser tocado" in texto
    assert os.path.exists(str(p) + ".bak")


def test_repoe_substituindo_bloco_parcial(tmp_path):
    """Sub-caso (b): sobrou um bloco sem `escopo:`. Substitui inteiro — merge
    exigiria decidir campo a campo o que é mais recente, e um campo gravado
    depois da foto é indistinguível de resíduo do arquivo comido."""
    p = tmp_path / "CONTEXTO.md"
    p.write_text("---\ndominios: [outro]\n---\n\n" + CORPO, encoding="utf-8", newline="")

    assert ficha.repor_bloco(str(p), FICHA) is True

    fm = frontmatter.ler(p.read_text())[0]
    assert fm["escopo"] == "projeto-x"
    assert fm.get("dominios") == ["tecnologia"], "o bloco parcial não sobrevive"
    assert "Corpo que não pode ser tocado" in p.read_text()
    assert "dominios: [outro]" in open(str(p) + ".bak").read(), "mas fica no .bak"


def test_round_trip_byte_identico_lf(tmp_path):
    """O teste que decide se o recorte do bloco está certo — em vez de
    argumentar sobre índices no papel."""
    from koine import bootstrap
    original = "---\nescopo: projeto-x\ndominios: [tecnologia]\n---\n\n" + CORPO
    p = tmp_path / "CONTEXTO.md"
    p.write_text(original, encoding="utf-8", newline="")
    bloco = bootstrap.bloco_do_contexto(str(tmp_path))

    p.write_text(CORPO, encoding="utf-8", newline="")     # a ficha some
    ficha.repor_bloco(str(p), bloco)

    assert open(p, "rb").read() == original.encode("utf-8")


def test_round_trip_byte_identico_crlf(tmp_path):
    """Mesmo round-trip em CRLF: é onde o `\\r` pendurado do `_fatiar` e o
    terminador da linha do `---` podem produzir arquivo misto."""
    from koine import bootstrap
    original = "---\r\nescopo: projeto-x\r\n---\r\n\r\n" + CORPO.replace("\n", "\r\n")
    p = tmp_path / "CONTEXTO.md"
    p.write_text(original, encoding="utf-8", newline="")
    bloco = bootstrap.bloco_do_contexto(str(tmp_path))

    p.write_text(CORPO.replace("\n", "\r\n"), encoding="utf-8", newline="")
    ficha.repor_bloco(str(p), bloco)

    bruto = open(p, "rb").read()
    assert bruto == original.encode("utf-8")
    assert b"\r\r" not in bruto


def test_repor_recusa_symlink(tmp_path):
    real = tmp_path / "real.md"
    real.write_text(CORPO, encoding="utf-8")
    link = tmp_path / "CONTEXTO.md"
    os.symlink(str(real), str(link))
    assert ficha.repor_bloco(str(link), FICHA) is False
    assert "escopo" not in real.read_text()


import pathlib

from koine import cli

VALIDO = """---
escopo: fixture
dominios: [tecnologia]
---

# Pasta

Uma linha de corpo com tamanho suficiente para servir de referência.
"""


def _pasta_valida(koine_home):
    d = pathlib.Path(koine_home["trab"])
    (d / "CONTEXTO.md").write_text(VALIDO, encoding="utf-8", newline="")
    return str(d)


def test_launch_valido_fotografa_a_ficha(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valida(koine_home)
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude"]) == 0

    foto = instantaneo.recuperar(pasta)
    assert foto is not None
    assert "escopo: fixture" in foto.bloco


def test_fotografar_nao_toca_o_contexto(koine_home, monkeypatch):
    """Fixture já normalizada de propósito: o launch lê com normalização
    ligada, e frontmatter torto faria a normalização escrever — escrita
    legítima que este teste acusaria como violação."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valida(koine_home)
    ctx = os.path.join(pasta, "CONTEXTO.md")
    antes, antes_mtime = open(ctx, "rb").read(), os.stat(ctx).st_mtime_ns
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    cli.main(["claude"])

    assert open(ctx, "rb").read() == antes
    assert os.stat(ctx).st_mtime_ns == antes_mtime
