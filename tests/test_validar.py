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
