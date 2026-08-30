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


def test_incompleto_com_foto_tem_a_ficha_de_volta(koine_home, monkeypatch, capsys):
    """A asserção NÃO pode ser "a sessão abriu": pasta INCOMPLETO também abre,
    com Hermes. O que discrimina é o arquivo no disco."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valida(koine_home)
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)
    cli.main(["claude"])                       # 1ª sessão: fotografa

    ctx = pathlib.Path(pasta, "CONTEXTO.md")
    ctx.write_text("# Pasta\n\nO agente comeu a ficha.\n", encoding="utf-8")

    assert cli.main(["claude"]) == 0           # 2ª sessão: repõe

    texto = ctx.read_text()
    assert frontmatter.ler(texto)[0]["escopo"] == "fixture", "a ficha voltou"
    assert "O agente comeu a ficha." in texto, "o corpo ficou"
    assert os.path.exists(str(ctx) + ".bak")
    assert "ficha" in capsys.readouterr().err.lower()


def test_reposicao_cura_a_sessao_tambem_nao_so_o_disco(koine_home, monkeypatch):
    """Curar o arquivo e abrir a sessão como incompleta seria meio conserto: o
    usuário receberia o Hermes com instrução de consertar uma pasta que já está
    consertada. A asserção é sobre o cm que chega ao adapter."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valida(koine_home)
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)
    cli.main(["claude"])                       # fotografa

    pathlib.Path(pasta, "CONTEXTO.md").write_text("# Pasta\n\nsem ficha\n",
                                                  encoding="utf-8")
    from koine import contexto as _ctx
    capturado = {}
    original = _ctx.resolver
    monkeypatch.setattr(_ctx, "resolver",
                        lambda a, p, **kw: capturado.setdefault(
                            "cm", original(a, p, **kw)))

    cli.main(["claude"])

    cm = capturado["cm"]
    assert not cm.bootstrap, "a sessão ainda subiu em modo bootstrap"
    assert cm.escopo_path, "a sessão não recebeu o escopo da ficha reposta"


def test_incompleto_sem_foto_segue_como_antes(koine_home, monkeypatch):
    """Regressão: sem foto, o caminho de hoje — Hermes com a instrução, e nada
    inventado no arquivo."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = str(pathlib.Path(koine_home["trab"]))
    ctx = pathlib.Path(pasta, "CONTEXTO.md")
    ctx.write_text("# Pasta\n\nSem ficha e sem foto.\n", encoding="utf-8")
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude"]) == 0
    assert ctx.read_text() == "# Pasta\n\nSem ficha e sem foto.\n"


def test_mostrar_anuncia_a_foto_sem_repor(koine_home, monkeypatch, capsys):
    """Verificação não escreve. Mas a ferramenta que avisa antes não pode dar a
    entender que a sessão não vai abrir, quando o launch vai curar."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valida(koine_home)
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)
    cli.main(["claude"])                       # fotografa

    ctx = pathlib.Path(pasta, "CONTEXTO.md")
    ctx.write_text("# Pasta\n\nsem ficha\n", encoding="utf-8")
    antes = ctx.read_bytes()
    capsys.readouterr()

    cli.main(["mostrar"])

    saida = capsys.readouterr()
    assert "ficha" in (saida.out + saida.err).lower()
    assert ctx.read_bytes() == antes, "mostrar NÃO pode escrever"


# ---- quem escreve a ficha, fotografa (#671) --------------------------------

def _apagar_ficha(path):
    """Simula o que o agente faz no fim da sessão: reescreve o CONTEXTO.md sem
    o bloco. É o bug de produção que a #605 existe para curar."""
    with open(path, encoding="utf-8", newline="") as f:
        texto = f.read()
    corpo = texto.split("---", 2)[2].lstrip("\r\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(corpo)


def test_definir_agente_sobrevive_a_perda_da_ficha(koine_home, monkeypatch):
    """A sequência medida no aceite do ciclo de 27/08:

    launch (fotografa) → definir-agente (grava e NÃO fotografava) → a ficha some
    → o launch seguinte repõe a foto ANTIGA, sem o `agente:`.

    O campo não está no `.bak` — o `.bak` guarda o arquivo já sem ficha. A linha
    se perde de verdade, e o usuário não tem de onde tirá-la."""
    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)
    pasta = koine_home["trab"]
    ctx = os.path.join(pasta, "CONTEXTO.md")

    assert cli.main(["claude", "hermes", pasta]) == 0      # fotografa
    assert cli.main(["definir-agente", "hermes", pasta]) == 0
    assert "agente: hermes" in open(ctx, encoding="utf-8").read()

    _apagar_ficha(ctx)
    assert cli.main(["claude", "hermes", pasta]) == 0      # repõe

    reposta = open(ctx, encoding="utf-8").read()
    assert "agente: hermes" in reposta, \
        "a reposição reverteu em silêncio o que o `definir-agente` gravou"


def test_definir_agente_em_pasta_incompleta_nao_fotografa(koine_home, monkeypatch):
    """Guarda contra a cura virar doença: fotografar ficha SEM `escopo:` faria a
    reposição devolver um bloco que continua incompleto — o launch seguinte
    repetiria a reposição, com um `.bak` novo a cada sessão."""
    from koine import cli, instantaneo as inst
    monkeypatch.setenv("HOME", koine_home["home"])
    nova = os.path.join(koine_home["home"], "trab-incompleta")
    os.makedirs(nova, exist_ok=True)
    with open(os.path.join(nova, "CONTEXTO.md"), "w", encoding="utf-8") as f:
        f.write("---\ndescricao: sem escopo\n---\n\n# Pendências\n")

    cli.main(["definir-agente", "hermes", nova])

    assert inst.recuperar(nova) is None, "guardou foto de ficha incompleta"


def test_a_foto_do_definir_agente_preserva_crlf(koine_home, monkeypatch):
    """Arquivo do usuário em CRLF: nem a gravação nem a reposição podem trocar
    as quebras de linha. É a armadilha que já custou uma correção na #605."""
    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)
    pasta = koine_home["trab"]
    ctx = os.path.join(pasta, "CONTEXTO.md")
    with open(ctx, encoding="utf-8", newline="") as f:
        texto = f.read()
    with open(ctx, "w", encoding="utf-8", newline="") as f:
        f.write(texto.replace("\n", "\r\n"))

    assert cli.main(["claude", "hermes", pasta]) == 0
    assert cli.main(["definir-agente", "hermes", pasta]) == 0
    _apagar_ficha(ctx)
    assert cli.main(["claude", "hermes", pasta]) == 0

    bruto = open(ctx, "rb").read()
    assert b"agente: hermes" in bruto
    assert b"\r\n" in bruto, "as quebras CRLF do usuário viraram LF"
    assert b"\r\r\n" not in bruto, "sobrou \\r pendurado"


def test_só_o_contexto_md_vira_foto(tmp_path, monkeypatch):
    """Fotografar é consequência de escrever A FICHA — não de escrever qualquer
    arquivo que por acaso esteja numa pasta que tem `CONTEXTO.md`.

    O caso que discrimina: `koine validar --corrigir` normaliza um arquivo
    QUALQUER dentro de uma pasta de sessão. Sem o guard de nome, isso fotografa
    a ficha da pasta — uma foto que ninguém validou como sessão que abriu bem.
    """
    from koine import ficha, instantaneo as inst
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    pasta = tmp_path / "sessao"
    pasta.mkdir()
    (pasta / "CONTEXTO.md").write_text(
        "---\ntype: contexto\nescopo: fixture\n---\n\n# Pasta\n", encoding="utf-8")
    # o arquivo alheio declara `escopo:` — é o que faz a condição de VALIDO
    # passar e deixa SÓ o guard de nome entre ele e a foto
    outro = pasta / "notas.md"
    outro.write_text("---\nescopo: fixture\ndescricao: Vendas B2B: metas\n---\n\n# Notas\n",
                     encoding="utf-8")

    ficha.normalizar_arquivo(str(outro))   # é o que o `validar --corrigir` faz

    assert inst.recuperar(str(pasta)) is None, \
        "escrever um arquivo qualquer fotografou a ficha da pasta"
