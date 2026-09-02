"""`koine validar` — varredura de frontmatter antes que ele estrague uma sessão.

Existe porque reparo na leitura conserta o sintoma sem que ninguém fique sabendo:
o arquivo no disco continua torto. Esta é a ferramenta para varrer as máquinas
que já escreveram YAML ruim (bug reportado em produção).
"""
import os

from koine import cli, validar

BOM = "---\nescopo: fixture\ndescricao: Tudo certo aqui\n---\n\n# ok\n"
REPARAVEL = "---\nescopo: fixture\ndescricao: Vendas B2B: acompanhamento\n---\n\n# ok\n"
IRREPARAVEL = "---\nchave:\n\t- item\n---\n\n# ruim\n"
ESCALAR = "---\ntexto solto sem chave\n---\n\n# ruim\n"


def _escrever(base, nome, conteudo):
    p = os.path.join(str(base), nome)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return p


# ---- varredura -------------------------------------------------------------

def test_arquivo_valido_nao_vira_achado(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", BOM)
    assert validar.varrer([str(tmp_path)]) == []


def test_reparavel_nomeia_chave_e_estado(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", REPARAVEL)
    (a,) = validar.varrer([str(tmp_path)])
    assert a.estado == validar.REPARAVEL
    assert a.chaves == ["descricao"]
    assert a.arquivo.endswith("CONTEXTO.md")


def test_irreparavel_traz_linha_e_coluna(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", IRREPARAVEL)
    (a,) = validar.varrer([str(tmp_path)])
    assert a.estado == validar.INVALIDO
    assert a.linha and a.coluna


def test_frontmatter_escalar_e_invalido(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", ESCALAR)
    (a,) = validar.varrer([str(tmp_path)])
    assert a.estado == validar.INVALIDO


def test_varre_subpastas_e_ignora_ocultos(tmp_path):
    _escrever(tmp_path, "escopos/comercial.md", REPARAVEL)
    _escrever(tmp_path, ".git/config.md", IRREPARAVEL)
    achados = validar.varrer([str(tmp_path)])
    assert [os.path.basename(a.arquivo) for a in achados] == ["comercial.md"]


def test_varredura_ignora_caminho_inexistente(tmp_path):
    assert validar.varrer([str(tmp_path / "nao-existe")]) == []


# ---- subcomando ------------------------------------------------------------

def test_comando_sem_achados_sai_zero(tmp_path, capsys):
    _escrever(tmp_path, "CONTEXTO.md", BOM)
    assert cli.main(["validar", str(tmp_path)]) == 0
    assert "nenhum problema" in capsys.readouterr().out.lower()


def test_comando_com_achados_sai_um_e_nomeia_arquivos(tmp_path, capsys):
    _escrever(tmp_path, "CONTEXTO.md", REPARAVEL)
    _escrever(tmp_path, "sub/outro.md", IRREPARAVEL)
    assert cli.main(["validar", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "CONTEXTO.md" in out and "outro.md" in out
    assert "descricao" in out


def test_comando_varre_a_config_por_padrao(tmp_path, monkeypatch, capsys):
    cfg = tmp_path / "config" / "koine"
    _escrever(cfg, "escopos/comercial.md", REPARAVEL)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    # sem argumento: varre a config do usuário + a pasta atual
    monkeypatch.chdir(tmp_path / "vazia" if (tmp_path / "vazia").exists()
                      else tmp_path)
    assert cli.main(["validar"]) == 1
    assert "comercial.md" in capsys.readouterr().out


def test_comando_varre_a_pasta_referencias_do_escopo(koine_home, monkeypatch, capsys):
    """Referência escrita pela /kn-11 vive fora da config, na pasta-referências
    do escopo. É a população onde a v0.4.6 quebrou — tem que entrar na varredura."""
    monkeypatch.setenv("HOME", koine_home["home"])
    _escrever(koine_home["refs"], "nota.md",
              "---\ntitle: Nota\ndescription: gog instalado: v0.34.1\n---\n\n# Nota\n")

    assert cli.main(["validar", koine_home["trab"]]) == 1
    assert "nota.md" in capsys.readouterr().out


# ---- correção em lote ------------------------------------------------------

def test_corrigir_normaliza_os_reparaveis(tmp_path, capsys):
    p = _escrever(tmp_path, "CONTEXTO.md", REPARAVEL)
    assert cli.main(["validar", "--corrigir", str(tmp_path)]) == 0
    assert 'descricao: "Vendas B2B: acompanhamento"' in \
        open(p, encoding="utf-8").read()
    assert os.path.exists(p + ".bak")
    assert "1 arquivo(s) corrigido" in capsys.readouterr().out


def test_corrigir_nao_toca_no_irreparavel_e_sai_um(tmp_path, capsys):
    p = _escrever(tmp_path, "CONTEXTO.md", IRREPARAVEL)
    assert cli.main(["validar", "--corrigir", str(tmp_path)]) == 1
    assert open(p, encoding="utf-8").read() == IRREPARAVEL
    assert "não consegue ler" in capsys.readouterr().out


def test_sem_a_flag_nada_e_escrito(tmp_path):
    p = _escrever(tmp_path, "CONTEXTO.md", REPARAVEL)
    assert cli.main(["validar", str(tmp_path)]) == 1
    assert open(p, encoding="utf-8").read() == REPARAVEL
    assert not os.path.exists(p + ".bak")


def test_corrigir_alcanca_a_pasta_de_referencias(koine_home, monkeypatch, capsys):
    """O que o launch deixa de propósito para cá: a base de conhecimento."""
    monkeypatch.setenv("HOME", koine_home["home"])
    ref = _escrever(koine_home["refs"], "nota.md",
                    '---\ntitle: Nota\ndescription: gog instalado: v0.34.1\n---\n')

    assert cli.main(["validar", "--corrigir", koine_home["trab"]]) == 0

    assert 'description: "gog instalado: v0.34.1"' in \
        open(ref, encoding="utf-8").read()
    assert "nota.md" in capsys.readouterr().out


# ---- ficha faltando: o estado que derruba a sessão -------------------------
# O `validar` nasceu cego para ele. Cinco pastas de um usuário real ficaram sem
# `escopo:` e o comando respondia "nenhum problema encontrado" — justo o estado
# que impede a sessão de abrir.

SEM_BLOCO = "# Minhas pendências\n\nConteúdo do usuário, sem frontmatter nenhum.\n"
SEM_ESCOPO = "---\ndescricao: gestao de pendencias\n---\n\n# Pendências\n"
BOOTSTRAP = "---\nbootstrap: true\n---\n\n# Bootstrap\n"


def test_contexto_sem_bloco_de_frontmatter_vira_achado(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", SEM_BLOCO)
    achados = validar.varrer([str(tmp_path)])
    assert [a.estado for a in achados] == [validar.SEM_FICHA]


def test_contexto_com_frontmatter_mas_sem_escopo_vira_achado(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", SEM_ESCOPO)
    assert [a.estado for a in validar.varrer([str(tmp_path)])] == [validar.SEM_FICHA]


def test_contexto_de_bootstrap_nao_vira_achado(tmp_path):
    """A pasta canônica durante o onboarding não tem escopo — e está certa
    assim. Alarme aqui seria falso positivo em toda instalação nova."""
    _escrever(tmp_path, "CONTEXTO.md", BOOTSTRAP)
    assert validar.varrer([str(tmp_path)]) == []


def test_arquivo_que_nao_e_contexto_nao_precisa_de_escopo(tmp_path):
    """Referência da /kn-11 não declara escopo — o critério é só do CONTEXTO.md."""
    _escrever(tmp_path, "refs/uma-referencia.md", "---\ntitle: Uma\n---\n\n# Uma\n")
    assert validar.varrer([str(tmp_path)]) == []


def test_relatorio_de_ficha_faltando_diz_o_que_fazer(tmp_path):
    _escrever(tmp_path, "CONTEXTO.md", SEM_BLOCO)
    texto = validar.relatorio(validar.varrer([str(tmp_path)]))
    assert "escopo:" in texto
    assert "hermes" in texto.lower()  # a saída é abrir sessão, não editar YAML


# Sem `escopo:` E com valor mal citado ao mesmo tempo. É o caso que dá poder ao
# teste do `--corrigir`: num arquivo só sem-ficha não há o que normalizar, então
# ele ficaria pendente mesmo sem o guard — o teste passaria por acidente.
SEM_ESCOPO_E_REPARAVEL = "---\ndescricao: Vendas B2B: metas\n---\n\n# Pendências\n"


def test_corrigir_nao_inventa_escopo(tmp_path):
    """`--corrigir` conserta valor mal citado. Escolher o escopo é do usuário —
    fica pendente, nunca chutado, e o arquivo não é reescrito no caminho."""
    p = _escrever(tmp_path, "CONTEXTO.md", SEM_ESCOPO_E_REPARAVEL)
    corrigidos, pendentes = validar.corrigir(validar.varrer([str(tmp_path)]))
    assert corrigidos == []
    assert [a.estado for a in pendentes] == [validar.SEM_FICHA]
    assert open(p, encoding="utf-8").read() == SEM_ESCOPO_E_REPARAVEL  # intocado
    assert not os.path.exists(p + ".bak")


def test_sem_ficha_tem_precedencia_sobre_reparavel(tmp_path):
    """Os dois problemas no mesmo arquivo: reporta o que impede a sessão de
    abrir. O valor mal citado aparece na varredura seguinte, depois que a ficha
    voltar — arrumar aspas num arquivo que nem abre sessão é ordem errada."""
    _escrever(tmp_path, "CONTEXTO.md", SEM_ESCOPO_E_REPARAVEL)
    assert [a.estado for a in validar.varrer([str(tmp_path)])] == [validar.SEM_FICHA]


def test_corrigir_nao_toca_arquivo_sem_frontmatter_nenhum(tmp_path):
    p = _escrever(tmp_path, "CONTEXTO.md", SEM_BLOCO)
    corrigidos, pendentes = validar.corrigir(validar.varrer([str(tmp_path)]))
    assert corrigidos == []
    assert [a.estado for a in pendentes] == [validar.SEM_FICHA]
    assert open(p, encoding="utf-8").read() == SEM_BLOCO


def test_validar_e_launch_concordam_sobre_a_mesma_pasta(tmp_path):
    """Critério único: o que o launch chama de `incompleto` é o que o validar
    acusa. Duas definições separadas divergem com o tempo — esta é a trava."""
    from koine import bootstrap
    for conteudo, incompleto in ((SEM_BLOCO, True), (SEM_ESCOPO, True),
                                 (BOOTSTRAP, False), (BOM, False)):
        _escrever(tmp_path, "CONTEXTO.md", conteudo)
        estado_launch = bootstrap.classificar(str(tmp_path))
        achados = validar.varrer([os.path.join(str(tmp_path), "CONTEXTO.md")])
        assert (estado_launch == bootstrap.INCOMPLETO) == incompleto
        assert bool([a for a in achados if a.estado == validar.SEM_FICHA]) == incompleto


def test_cmd_validar_sai_1_com_ficha_faltando(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    _escrever(tmp_path, "trab/CONTEXTO.md", SEM_BLOCO)
    assert cli.main(["validar", os.path.join(str(tmp_path), "trab")]) == 1
    assert "escopo:" in capsys.readouterr().out


# ---- a pasta-referências que não existe (jd-task #761) ---------------------

def _apontar_refs(koine_home, destino):
    """Reaponta o escopo da fixture para `destino`, sem criá-lo."""
    esc = os.path.join(koine_home["home"], ".config", "koine", "escopos", "fixture.md")
    with open(esc, "w", encoding="utf-8") as f:
        f.write("---\ntype: escopo\nnome: fixture\n"
                f"pasta-referencias: abs:{destino}\n---\n\n# fixture\n")
    return destino


def test_validar_enxerga_a_pasta_referencias_que_nao_existe(koine_home, monkeypatch,
                                                            capsys):
    """O estado que derrubou uma estação em produção, e que o validador não via.

    Known Folder Move: o `Documents` do perfil é redirecionado para o OneDrive
    corporativo e o caminho físico vira casca vazia. O escopo apontava para
    `home:Documents/...`, o `home:` do Koine só concatena, e a sessão morria com
    traceback (jd-task #761, 02/09/2026).

    O validador era cego: `refs_do_escopo` devolvia `None` quando a pasta não
    existia, e o relatório não dizia nada. Mesma forma do gap `SEM_FICHA` que a
    v0.6.1 fechou — o validador não enxergando o estado que fecha a sessão.
    """
    monkeypatch.setenv("HOME", koine_home["home"])
    sumida = _apontar_refs(koine_home,
                           os.path.join(koine_home["home"], "Documents", "CURSO IA"))
    assert cli.main(["validar", koine_home["trab"]]) == 1
    out = capsys.readouterr().out
    assert sumida in out, "o relatório precisa dizer QUAL caminho não existe"
    assert "OneDrive" in out, "sem a pista do redirecionamento, o diagnóstico não fecha"


def test_validar_nao_reclama_da_pasta_referencias_que_existe(koine_home, monkeypatch,
                                                             capsys):
    """Metade que dá poder à anterior: sem ela, um achado incondicional passaria."""
    monkeypatch.setenv("HOME", koine_home["home"])
    assert cli.main(["validar", koine_home["trab"]]) == 0
    assert "não existe" not in capsys.readouterr().out
