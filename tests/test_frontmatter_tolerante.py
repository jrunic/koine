"""Frontmatter escrito à mão por gente comum não derruba o Koine.

Regressão do bug reportado em produção: `descricao: Vendas B2B: acompanhamento e metas`
(dois-pontos sem aspas) matava o launch com ScannerError cru. Cobre as três
classes: reparável, irreparável e não-mapa.
"""
import os

import pytest

from koine import bootstrap, cli, frontmatter

# Caso reportado em produção, reduzido ao essencial.
CASO_REAL = """---
tipo: contexto
descricao: Processo comercial recorrente: acompanhamento de vendas e metas
escopo: fixture
dominios: [tecnologia]
---

# Gestão comercial
"""

# Uma linha VÁLIDA com dois-pontos citado convivendo com uma linha quebrada:
# o reparo não pode tocar na primeira.
MISTO = """---
descricao: "Vendas: meta e funil"
escopo: comercial: b2b
---

# Corpo
"""


# ---- reparo ---------------------------------------------------------------

def test_repara_dois_pontos_sem_aspas():
    fm, corpo = frontmatter.ler(CASO_REAL)
    assert fm["descricao"] == (
        "Processo comercial recorrente: acompanhamento de vendas e metas")
    assert fm["escopo"] == "fixture"
    assert corpo.startswith("# Gestão")


def test_reparo_nao_toca_linha_valida_do_mesmo_bloco():
    fm, _ = frontmatter.ler(MISTO)
    # a linha válida sobrevive sem aspas parasitas no valor
    assert fm["descricao"] == "Vendas: meta e funil"
    assert fm["escopo"] == "comercial: b2b"


def test_repara_aspas_desbalanceadas():
    fm, _ = frontmatter.ler('---\ndescricao: "processo "top" da casa"\n---\n')
    assert "top" in fm["descricao"]


def test_repara_preserva_apostrofo():
    fm, _ = frontmatter.ler("---\ndescricao: caixa d'água: 500 litros\n---\n")
    assert fm["descricao"] == "caixa d'água: 500 litros"


def test_repara_nao_quebra_listas_e_blocos():
    doc = ("---\ndescricao: Vendas: meta\ndominios: [tecnologia, negocio]\n"
           "tags:\n  - a\n  - b\n---\n")
    fm, _ = frontmatter.ler(doc)
    assert fm["dominios"] == ["tecnologia", "negocio"]
    assert fm["tags"] == ["a", "b"]


def test_analisar_nomeia_as_chaves_reparadas():
    _, reparos, _ = frontmatter.analisar(CASO_REAL)
    assert reparos == ["descricao"]
    _, reparos, _ = frontmatter.analisar("---\nescopo: fixture\n---\n")
    assert reparos == []


# ---- irreparável e não-mapa ------------------------------------------------

def test_irreparavel_levanta_com_linha_e_coluna():
    with pytest.raises(frontmatter.FrontmatterInvalido) as e:
        frontmatter.ler("---\nchave:\n\t- item\n---\n")
    assert e.value.linha and e.value.coluna


def test_frontmatter_escalar_nao_estoura_attributeerror():
    # yaml.safe_load devolve str: `or {}` não pega, fm.get() dava AttributeError
    with pytest.raises(frontmatter.FrontmatterInvalido):
        frontmatter.ler("---\ntexto solto sem chave\n---\n")


def test_erro_de_arquivo_nomeia_o_caminho(tmp_path):
    p = tmp_path / "CONTEXTO.md"
    p.write_text("---\nchave:\n\t- item\n---\n", encoding="utf-8")
    with pytest.raises(frontmatter.FrontmatterInvalido) as e:
        frontmatter.ler_arquivo(str(p))
    assert str(p) in str(e.value)


def test_linha_reportada_e_a_do_arquivo(tmp_path):
    p = tmp_path / "CONTEXTO.md"
    # linha 1 = ---, 2 = tipo, 3 = chave, 4 = tab
    p.write_text("---\ntipo: contexto\nchave:\n\t- item\n---\n", encoding="utf-8")
    with pytest.raises(frontmatter.FrontmatterInvalido) as e:
        frontmatter.ler_arquivo(str(p))
    assert e.value.linha == 4


# ---- contrato preservado ---------------------------------------------------

def test_sem_frontmatter_continua_devolvendo_vazio():
    fm, corpo = frontmatter.ler("# Só corpo\n")
    assert fm == {} and corpo == "# Só corpo\n"


def test_bloco_vazio_continua_devolvendo_vazio():
    fm, _ = frontmatter.ler("---\n---\n\n# Corpo\n")
    assert fm == {}


# ---- aviso -----------------------------------------------------------------

def test_reparo_avisa_uma_vez_por_arquivo(tmp_path, capsys):
    p = tmp_path / "CONTEXTO.md"
    p.write_text(CASO_REAL, encoding="utf-8")
    frontmatter.ler_arquivo(str(p))
    frontmatter.ler_arquivo(str(p))  # o launch relê o mesmo arquivo 3x
    err = capsys.readouterr().err
    assert err.count("CONTEXTO.md") == 1
    assert "descricao" in err


# ---- integração: o Koine continua rodando ----------------------------------

def test_classificar_aceita_contexto_reparavel(tmp_path):
    (tmp_path / "CONTEXTO.md").write_text(CASO_REAL, encoding="utf-8")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.VALIDO


def test_classificar_degrada_irreparavel_sem_crashar(tmp_path):
    (tmp_path / "CONTEXTO.md").write_text(
        "---\nchave:\n\t- item\n---\n# corpo\n", encoding="utf-8")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.MALFORMADO


def test_classificar_degrada_frontmatter_escalar(tmp_path):
    (tmp_path / "CONTEXTO.md").write_text(
        "---\ntexto solto sem chave\n---\n# corpo\n", encoding="utf-8")
    assert bootstrap.classificar(str(tmp_path)) == bootstrap.MALFORMADO


# ---- launch: o comando que o usuário rodou ------------------------------------

def test_launch_sobe_com_contexto_reparavel(koine_home, monkeypatch, capsys):
    """`kn-<cliente> <agente> <pasta>` com o CONTEXTO.md do caso reportado: o cliente IA
    abre, o contexto é montado, e o usuário só vê um aviso."""
    monkeypatch.setenv("HOME", koine_home["home"])
    cap = {}
    monkeypatch.setattr("koine.launch.lancar",
                        lambda cliente, pasta, **kw: cap.update(pasta=pasta))
    trab = koine_home["trab"]
    with open(os.path.join(trab, "CONTEXTO.md"), "w", encoding="utf-8") as f:
        f.write(CASO_REAL)

    assert cli.main(["claude", "hermes", trab]) == 0
    assert cap == {"pasta": trab}
    # materializou o contexto do cliente, com o CONTEXTO.md referenciado
    assert "CONTEXTO.md" in open(
        os.path.join(trab, "CLAUDE.md"), encoding="utf-8").read()
    assert "sem aspas" in capsys.readouterr().err


def test_launch_irreparavel_nomeia_linha_e_preserva(koine_home, monkeypatch, capsys):
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)
    trab = koine_home["trab"]
    original = "---\nchave:\n\t- item\n---\n\n# trabalho do usuário\n"
    with open(os.path.join(trab, "CONTEXTO.md"), "w", encoding="utf-8") as f:
        f.write(original)

    assert cli.main(["claude", "hermes", trab]) == 1
    err = capsys.readouterr().err
    assert "frontmatter inválido" in err and "linha 3" in err  # a linha do TAB
    # nunca clobber: o arquivo do usuário fica como estava
    assert open(os.path.join(trab, "CONTEXTO.md"), encoding="utf-8").read() == original


def test_reparo_em_arquivo_crlf_nao_engole_o_retorno_de_carro():
    """Windows escreve CRLF — a plataforma onde o bug foi reportado. Sem
    splitlines, o \\r sobrava no fim do valor e entrava dentro das aspas."""
    crlf = CASO_REAL.replace("\n", "\r\n")
    fm, _ = frontmatter.ler(crlf)
    assert fm["descricao"] == (
        "Processo comercial recorrente: acompanhamento de vendas e metas")
    assert not fm["descricao"].endswith("\r")
    assert fm["escopo"] == "fixture"
