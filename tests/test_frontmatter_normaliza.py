"""Normalização de frontmatter no disco — bug reportado em produção (causa raiz).

A leitura já repara em memória (v0.5.2). Aqui o arquivo é consertado de fato,
com diff mínimo: só a linha citada muda, tudo mais sai byte a byte igual.
"""
import pytest

from koine import frontmatter
from koine._vendor import yaml


# ---- citação ---------------------------------------------------------------

def test_cita_com_aspas_duplas_por_padrao():
    # é o que os templates das skills e a documentação recomendam
    assert frontmatter._citar("Vendas B2B: metas") == '"Vendas B2B: metas"'


def test_cita_com_aspas_simples_quando_o_valor_tem_barra_invertida():
    # `descricao: C:\Users\usuario: pasta` — entre aspas duplas o YAML lê \U como
    # escape inválido; entre simples, barra invertida é literal
    assert frontmatter._citar(r"C:\Users\usuario: pasta") == r"'C:\Users\usuario: pasta'"


def test_cita_com_aspas_simples_quando_o_valor_tem_aspas_duplas():
    esperado = "'" + 'processo "top": da casa' + "'"
    assert frontmatter._citar('processo "top": da casa') == esperado


def test_apostrofo_e_duplicado_dentro_de_aspas_simples():
    assert frontmatter._citar(r"caixa d'água C:\pasta") == r"'caixa d''água C:\pasta'"


@pytest.mark.parametrize("valor", [
    "Vendas B2B: metas",
    r"C:\Users\usuario: pasta",
    'processo "top": da casa',
    "caixa d'água: 500 litros",
    r'misto "x" e \y: z',
])
def test_valor_citado_sempre_reparseia_identico(valor):
    assert yaml.safe_load(f"d: {frontmatter._citar(valor)}") == {"d": valor}


# ---- fatiamento ------------------------------------------------------------

def test_fatia_devolve_limites_do_bloco_no_texto_original():
    texto = "---\nescopo: x\n---\n\n# Corpo\n"
    fatia = frontmatter._fatiar(texto)
    assert texto[fatia.inicio:fatia.fim] == "escopo: x"
    assert fatia.corpo == "# Corpo\n"


def test_fatia_preserva_limites_em_crlf():
    texto = "---\r\nescopo: x\r\n---\r\n\r\n# Corpo\r\n"
    fatia = frontmatter._fatiar(texto)
    assert texto[fatia.inicio:fatia.fim] == "escopo: x\r"


def test_sem_frontmatter_nao_tem_fatia():
    assert frontmatter._fatiar("# Só corpo\n") is None
    assert frontmatter._fatiar("---\nsem fechamento\n") is None


# ---- decisão por linha -----------------------------------------------------

def test_decidir_aponta_indice_chave_e_linha_corrigida():
    bloco = 'descricao: "Vendas: meta"\nescopo: comercial: b2b'
    assert frontmatter._decidir(bloco.splitlines()) == [
        (1, "escopo", 'escopo: "comercial: b2b"')]


def test_decidir_ignora_estrutura_yaml():
    bloco = "dominios: [a, b]\ntags:\n  - x"
    assert frontmatter._decidir(bloco.splitlines()) == []


def test_decidir_nao_junta_nada():
    """A junção é de quem chama: o parser quer bloco achatado, o arquivo em
    disco quer o terminador original de cada linha."""
    bloco = "a: x: y\nb: z: w"
    decisoes = frontmatter._decidir(bloco.splitlines())
    assert [i for i, _, _ in decisoes] == [0, 1]
    assert all(isinstance(nova, str) and "\n" not in nova
               for _, _, nova in decisoes)


# ---- normalização de texto -------------------------------------------------

CASO_REAL = """---
tipo: contexto
descricao: Processo comercial: acompanhamento de vendas e metas
escopo: fixture
dominios: [tecnologia]
---

# Gestão comercial

Corpo com : dois-pontos soltos, que não é frontmatter e não deve ser tocado.
"""

CITADA = 'descricao: "Processo comercial: acompanhamento de vendas e metas"'


def test_normalizar_muda_apenas_a_linha_reparada():
    novo, chaves = frontmatter.normalizar(CASO_REAL)
    assert chaves == ["descricao"]
    antes, depois = CASO_REAL.split("\n"), novo.split("\n")
    assert len(antes) == len(depois)
    diferentes = [i for i, (a, d) in enumerate(zip(antes, depois)) if a != d]
    assert diferentes == [2]          # só a linha da descricao
    assert depois[2] == CITADA


def test_normalizar_preserva_crlf():
    crlf = CASO_REAL.replace("\n", "\r\n")
    novo, chaves = frontmatter.normalizar(crlf)
    assert chaves == ["descricao"]
    # nenhum LF solto sobrou: todo \n do resultado veio de um \r\n
    assert novo.count("\n") == novo.count("\r\n")
    assert novo == crlf.replace(
        "descricao: Processo comercial: acompanhamento de vendas e metas",
        CITADA)


def test_normalizar_e_idempotente():
    novo, _ = frontmatter.normalizar(CASO_REAL)
    outra, chaves = frontmatter.normalizar(novo)
    assert chaves == []
    assert outra == novo


def test_normalizar_nao_toca_arquivo_valido():
    valido = '---\nescopo: x\ndescricao: "Vendas: meta"\n---\n\n# ok\n'
    assert frontmatter.normalizar(valido) == (valido, [])


def test_normalizar_recusa_irreparavel():
    ruim = "---\nchave:\n\t- item\n---\n"
    assert frontmatter.normalizar(ruim) == (ruim, [])


def test_normalizar_recusa_frontmatter_escalar():
    escalar = "---\ntexto solto sem chave\n---\n"
    assert frontmatter.normalizar(escalar) == (escalar, [])


def test_normalizar_recusa_texto_sem_frontmatter():
    assert frontmatter.normalizar("# só corpo\n") == ("# só corpo\n", [])


def test_normalizado_reparseia_com_o_mesmo_conteudo():
    novo, _ = frontmatter.normalizar(CASO_REAL)
    original_fm, _ = frontmatter.ler(CASO_REAL)
    novo_fm, novo_corpo = frontmatter.ler(novo)
    assert novo_fm == original_fm
    assert "não deve ser tocado" in novo_corpo


# ---- acionamento no launch -------------------------------------------------

CONTEXTO_TORTO = ("---\nescopo: fixture\ndominios: [tecnologia]\n"
                  "descricao: Vendas B2B: metas\n---\n\n# Trabalho\n")
REF_TORTA = ("---\ntitle: Nota\ndescription: gog instalado: v0.34.1\n"
             "dominios: [tecnologia]\n---\n\n# Nota\n")


def test_launch_conserta_o_contexto_no_disco(koine_home, monkeypatch):
    import os
    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)
    ctx = os.path.join(koine_home["trab"], "CONTEXTO.md")
    with open(ctx, "w", encoding="utf-8") as f:
        f.write(CONTEXTO_TORTO)

    assert cli.main(["claude", "hermes", koine_home["trab"]]) == 0

    assert 'descricao: "Vendas B2B: metas"' in open(ctx, encoding="utf-8").read()
    assert os.path.exists(ctx + ".bak")


def test_launch_nao_reescreve_a_pasta_de_referencias(koine_home, monkeypatch):
    """A base de conhecimento do usuário não é reescrita sem ele pedir — o
    walker do índice visita todo .md do escopo, e isso viraria N arquivos
    mexidos e N .bak na primeira sessão. Trabalho do `validar --corrigir`."""
    import os
    from koine import cli
    monkeypatch.setenv("HOME", koine_home["home"])
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: None)
    ref = os.path.join(koine_home["refs"], "nota.md")
    with open(ref, "w", encoding="utf-8") as f:
        f.write(REF_TORTA)

    assert cli.main(["claude", "hermes", koine_home["trab"]]) == 0

    assert open(ref, encoding="utf-8").read() == REF_TORTA
    assert not os.path.exists(ref + ".bak")
