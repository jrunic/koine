from koine import agente


def test_posicional_vence_tudo():
    nome, fonte = agente.resolver_nome(posicional="atlas",
                                       fm_pasta={"agente": "leia"},
                                       default_usuario="hermes")
    assert (nome, fonte) == ("atlas", agente.POSICIONAL)


def test_pasta_vence_default():
    nome, fonte = agente.resolver_nome(posicional="", fm_pasta={"agente": "leia"},
                                       default_usuario="atlas")
    assert (nome, fonte) == ("leia", agente.PASTA)


def test_default_quando_a_pasta_nao_declara():
    nome, fonte = agente.resolver_nome(posicional="", fm_pasta={},
                                       default_usuario="atlas")
    assert (nome, fonte) == ("atlas", agente.DEFAULT)


def test_hermes_quando_nao_ha_nada():
    nome, fonte = agente.resolver_nome(posicional="", fm_pasta={},
                                       default_usuario="")
    assert (nome, fonte) == ("hermes", agente.FALLBACK)


def test_a_fonte_distingue_valores_iguais():
    """O discriminante do tratamento de agente inexistente é a FONTE, não o
    nome. Se os dois caminhos devolvessem o mesmo valor sem a fonte, o ramo de
    erro e o de recuperação ficariam indistinguíveis."""
    a = agente.resolver_nome(posicional="leia", fm_pasta={"agente": "leia"},
                             default_usuario="leia")
    b = agente.resolver_nome(posicional="", fm_pasta={"agente": "leia"},
                             default_usuario="leia")
    assert a[0] == b[0] == "leia"
    assert a[1] != b[1]


import os
import pathlib

import pytest

from koine import cli, contexto

VALIDO = """---
escopo: fixture
dominios: [tecnologia]
agente: {agente}
---

# Pasta

Corpo com uma linha longa o bastante para servir de discriminante quando o teste
precisa saber se um adapter embutiu o conteúdo ou só referenciou o caminho.
"""


def _pasta_valido(koine_home, agente_declarado):
    """Reusa a pasta de trabalho da seed: ela já tem o escopo `fixture`
    cadastrado no config, que é o que o ramo VALIDO exige."""
    d = pathlib.Path(koine_home["trab"])
    (d / "CONTEXTO.md").write_text(VALIDO.format(agente=agente_declarado),
                                   encoding="utf-8")
    return str(d)


def test_pasta_declarada_abre_com_o_agente_da_pasta(koine_home, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "hermes")
    cm = contexto.resolver("", pasta)
    assert cm.agente_path.endswith("hermes.md")


def test_bootstrap_ignora_o_agente_pedido(koine_home, tmp_path, monkeypatch):
    """Regressão: fora de VALIDO nada muda — é o Hermes que carrega a
    instrução de consertar a pasta."""
    monkeypatch.setenv("HOME", koine_home["home"])
    d = tmp_path / "boot"
    d.mkdir()
    (d / "CONTEXTO.md").write_text("---\nbootstrap: true\n---\n", encoding="utf-8")
    cm = contexto.resolver("atlas", str(d))
    assert cm.bootstrap is True
    assert cm.agente_path.endswith("hermes.md")


def test_agente_declarado_inexistente_abre_hermes_com_instrucao(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "fantasma")
    cm = contexto.resolver("", pasta)
    assert cm.agente_path.endswith("hermes.md")
    assert cm.instrucao_path, "sem instrução o usuário fica sem saída e sem erro"
    assert os.path.exists(cm.instrucao_path), "a instrução tem que existir no vault"
    assert cm.agente_ausente == "fantasma"


def test_posicional_inexistente_continua_dando_erro(koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "hermes")
    with pytest.raises(contexto.AgenteNaoEncontrado):
        contexto.resolver("hermse", pasta)


def test_todo_adapter_renderiza_a_instrucao(koine_home, monkeypatch):
    """Invariante declarado no CONTEXTO.md do repo: *adapter que renderiza
    contexto_path renderiza instrucao_path*. Esquecer o campo deixa o usuário
    sem saída E sem erro — a sessão sobe, e a orientação simplesmente não chega.

    A guarda é por CAMPO e sobre o REGISTRY inteiro, não por cenário: adapter
    novo entra na varredura sozinho, que é o momento em que o esquecimento é
    mais provável.
    """
    from koine import adapters

    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "fantasma")
    cm = contexto.resolver("", pasta)
    assert cm.instrucao_path, "pré-condição: o cenário tem que produzir instrução"

    def _entrega(saida, path):
        """Como o adapter entrega um arquivo: por caminho (@path) ou embutindo o
        conteúdo. O codex é inline; os outros referenciam.

        A busca por conteúdo usa uma linha do CORPO, não o começo do arquivo: o
        render rebaixa os títulos ao compor as seções, então casar os primeiros
        bytes acusaria "ausente" num adapter que renderiza corretamente — foi o
        que este helper fez na primeira versão.
        """
        if path in saida:
            return "caminho"
        corpo = [l.strip() for l in open(path, encoding="utf-8").read().splitlines()
                 if len(l.strip()) > 40 and not l.startswith("#")]
        if corpo and corpo[0] in saida:
            return "conteudo"
        return "ausente"

    for nome, mod in adapters.REGISTRY.items():
        lanc = mod.renderizar(cm)
        saida = "\n".join(list(lanc.arquivos_working_dir.values())
                          + list(lanc.arquivos_externos.values()))
        # o invariante é RELATIVO: a instrução chega da mesma forma que o
        # contexto chega. Exigir sempre o caminho reprovaria o codex, que é
        # inline por desenho — e "consertar" o teste seria perder a guarda.
        assert _entrega(saida, cm.instrucao_path) == _entrega(saida, cm.contexto_path), \
            f"adapter {nome} entrega o contexto mas não a instrução"
        assert _entrega(saida, cm.instrucao_path) != "ausente", \
            f"adapter {nome} não renderiza a instrução"


def test_zero_posicionais_resolve_pela_pasta(koine_home, monkeypatch):
    """Invocação dos providers remotos: nenhum posicional, a pasta resolve."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "hermes")
    monkeypatch.chdir(pasta)
    capturado = {}
    # SEAM obrigatório: o launch faz execvpe e mataria o pytest.
    monkeypatch.setattr("koine.launch.lancar",
                        lambda *a, **k: capturado.update(chamou=True) or 0)

    rc = cli.main(["claude"])

    assert rc == 0
    assert capturado.get("chamou"), "o launch não chegou a ser chamado"


def test_um_posicional_continua_sendo_agente(koine_home, monkeypatch):
    """`kn-claude <alias-de-pasta>` sozinho cai em agente inexistente, com a
    lista — regra fixa em vez de adivinhação."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "hermes")
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude", "nao-e-agente"]) != 0


def test_agente_declarado_inexistente_em_modo_interativo_segue_com_hermes(
        koine_home, monkeypatch):
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "fantasma")
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    assert cli.main(["claude"]) == 0


def test_agente_declarado_inexistente_sem_tty_aborta(koine_home, monkeypatch, capsys):
    """Sem TTY não há a quem perguntar e não há prompt: abrir Hermes em
    silêncio faria a sessão remota rodar com o agente errado sem ninguém
    perceber. É o caso do Paseo."""
    monkeypatch.setenv("HOME", koine_home["home"])
    pasta = _pasta_valido(koine_home, "fantasma")
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr("koine.launch.lancar", lambda *a, **k: 0)

    rc = cli.main(["claude"])

    assert rc != 0
    assert "fantasma" in capsys.readouterr().err
