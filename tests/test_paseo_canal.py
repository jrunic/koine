"""Invariantes do canal de invocação por máquina (jd-task #703).

O Paseo spawna o comando do provider e passa a PRÓPRIA lista de argumentos, de
um cwd que nem sempre é pasta de trabalho. As três formas de quebrar isso foram
medidas na bancada Windows em 29/08/2026, e cada uma tem teste aqui.
"""
import os
import shutil

import pytest

from koine import cli

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _preparar_pasta_valida(tmp_path, monkeypatch, agente_da_pasta="sheldon"):
    """HOME isolado com dois agentes e uma pasta de trabalho que declara um deles.

    Dois agentes é o mínimo para o teste DISCRIMINAR: com um só, "veio o agente
    certo" e "veio o único que existe" são indistinguíveis.
    """
    home = tmp_path / "home"
    cfg = home / ".config" / "koine"
    data = home / ".local" / "share" / "koine"
    (cfg / "escopos").mkdir(parents=True)
    (cfg / "agentes").mkdir()
    (data / "agentes").mkdir(parents=True)
    (data / "bootstrap").mkdir()
    (home / "refs").mkdir()
    shutil.copy(os.path.join(REPO, "vault", "KOINE.md"), data / "KOINE.md")
    shutil.copy(os.path.join(REPO, "vault", "agentes", "hermes.md"),
                data / "agentes" / "hermes.md")
    for instr in ("pasta-incompleta.md", "agente-inexistente.md",
                  "pasta-fora-do-koine.md"):
        origem = os.path.join(REPO, "vault", "bootstrap", instr)
        if os.path.exists(origem):
            shutil.copy(origem, data / "bootstrap" / instr)
    (cfg / "teste.md").write_text(
        "---\ntype: usuario\nnome: Teste\n---\n\n# Teste\n", encoding="utf-8")
    (cfg / "escopos" / "fixture.md").write_text(
        "---\ntype: escopo\nnome: fixture\n"
        f"pasta-referencias: abs:{home / 'refs'}\n---\n\n# fixture\n", encoding="utf-8")
    (cfg / "agentes" / "sheldon.md").write_text(
        "---\ntype: Agent\ntitle: Sheldon\nescopo: fixture\n---\n\n# Sheldon\n",
        encoding="utf-8")
    trab = tmp_path / "trabalho"
    trab.mkdir()
    (trab / "CONTEXTO.md").write_text(
        "---\ntype: contexto\nescopo: fixture\n"
        f"agente: {agente_da_pasta}\n---\n\n# Trabalho\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.chdir(trab)
    return trab


def _espiar_agente(original, capturado):
    def espiao(agente, pasta):
        capturado["agente"] = agente
        return original(agente, pasta)
    return espiao


@pytest.fixture
def sem_launch(monkeypatch):
    """Seam obrigatória: o launch faz execvpe e mataria o pytest."""
    capturado = {}
    monkeypatch.setattr(
        cli.launch, "lancar",
        lambda c, p, env=None, args=None: capturado.update(cwd=p, args=args or []))
    return capturado


# --- a gramática do canal --------------------------------------------------

def test_a_flag_de_canal_nao_vaza_para_o_cliente(sem_launch, tmp_path, monkeypatch):
    """Sem consumir a flag antes, `_separar_args` a trata como flag do cliente
    — todo token com hífen é do cliente naquela gramática — e ela chega ao
    processo lançado."""
    _preparar_pasta_valida(tmp_path, monkeypatch)
    cli.main(["claude", "--canal-paseo", "--", "--model", "x-1"])
    assert "--canal-paseo" not in sem_launch["args"]


def test_o_separador_e_o_que_impede_o_valor_de_virar_pasta(sem_launch, tmp_path,
                                                           monkeypatch):
    """O defeito medido em 29/08: `--model x-1` se parte. A flag vai para o
    cliente e `x-1` — que não começa com hífen — é lido como PASTA.

    As duas metades importam. A primeira mostra o comportamento certo COM o
    separador; a segunda mostra que sem ele o comando quebra, que é o que torna
    o separador load-bearing no wrapper e não enfeite. Sem a segunda metade,
    este teste passaria com e sem a correção — e não provaria nada.
    """
    trab = _preparar_pasta_valida(tmp_path, monkeypatch)
    assert cli.main(["claude", "--canal-paseo", "--", "--model", "x-1"]) == 0
    assert sem_launch["args"][-2:] == ["--model", "x-1"]
    assert sem_launch["cwd"] == str(trab)

    # sem o separador: `x-1` vira posicional, é lido como AGENTE e não existe
    sem_launch.clear()
    assert cli.main(["claude", "--canal-paseo", "--model", "x-1"]) == 1
    assert sem_launch == {}, "não deveria ter chegado ao launch"


# --- o agente por variável -------------------------------------------------

def test_a_variavel_de_agente_vence_o_da_pasta_no_canal(sem_launch, tmp_path, monkeypatch):
    capturado = {}
    monkeypatch.setattr(cli, "_montar_cm", _espiar_agente(cli._montar_cm, capturado))
    _preparar_pasta_valida(tmp_path, monkeypatch)
    monkeypatch.setenv("KOINE_AGENTE", "hermes")
    cli.main(["claude", "--canal-paseo", "--"])
    assert capturado["agente"] == "hermes"


def test_sem_a_variavel_a_pasta_resolve(sem_launch, tmp_path, monkeypatch):
    capturado = {}
    monkeypatch.setattr(cli, "_montar_cm", _espiar_agente(cli._montar_cm, capturado))
    _preparar_pasta_valida(tmp_path, monkeypatch)
    monkeypatch.delenv("KOINE_AGENTE", raising=False)
    cli.main(["claude", "--canal-paseo", "--"])
    assert capturado["agente"] == ""  # 0 posicionais: quem resolve é a pasta


def test_a_variavel_vazia_conta_como_ausente(sem_launch, tmp_path, monkeypatch, capsys):
    """As sondagens do Paseo entregam a variável de forma INCONSISTENTE — medido
    em 29/08: dentro de um único `provider diagnostic`, duas invocações com ela e
    três sem. Ausência é caminho normal, nunca erro."""
    capturado = {}
    monkeypatch.setattr(cli, "_montar_cm", _espiar_agente(cli._montar_cm, capturado))
    _preparar_pasta_valida(tmp_path, monkeypatch)
    monkeypatch.setenv("KOINE_AGENTE", "")
    assert cli.main(["claude", "--canal-paseo", "--"]) == 0
    assert capturado["agente"] == ""


def test_a_variavel_e_ignorada_fora_do_canal(sem_launch, tmp_path, monkeypatch):
    """Variável de ambiente que muda o agente em QUALQUER invocação alteraria o
    terminal de forma invisível, e variável esquecida no perfil é o tipo de
    estado que ninguém encontra."""
    capturado = {}
    monkeypatch.setattr(cli, "_montar_cm", _espiar_agente(cli._montar_cm, capturado))
    _preparar_pasta_valida(tmp_path, monkeypatch)
    monkeypatch.setenv("KOINE_AGENTE", "hermes")
    cli.main(["claude"])
    assert capturado["agente"] == ""


# --- pasta não configurada: avisa, não escreve -----------------------------

ESTADOS_NAO_CONFIGURADOS = ["ausente", "vazio", "incompleto", "malformado"]


def _pasta_no_estado(tmp_path, monkeypatch, estado):
    trab = _preparar_pasta_valida(tmp_path, monkeypatch)
    ctx = trab / "CONTEXTO.md"
    if estado == "ausente":
        ctx.unlink()
    elif estado == "vazio":
        ctx.write_text("", encoding="utf-8")
    elif estado == "incompleto":
        ctx.write_text("---\ntype: contexto\n---\n\n# T\n", encoding="utf-8")
    elif estado == "malformado":
        ctx.write_text("---\n[: : :\n---\n\n# T\n", encoding="utf-8")
    return trab


@pytest.mark.parametrize("estado", ESTADOS_NAO_CONFIGURADOS)
def test_no_canal_nada_e_escrito_na_pasta(sem_launch, tmp_path, monkeypatch, estado):
    """O defeito medido em 29/08/2026: as sondagens do Paseo rodam com o cwd do
    DAEMON, e o Koine materializou um CONTEXTO.md de bootstrap dentro da pasta
    de downloads do usuário. 930 bytes, na primeira sondagem."""
    trab = _pasta_no_estado(tmp_path, monkeypatch, estado)
    # conteúdo, não só nome: em três dos quatro estados o CONTEXTO.md JÁ existe,
    # e o auto-guiar o sobrescreve sem mudar a listagem. Um teste por nome
    # passaria em `vazio`, `incompleto` e `malformado` com e sem a correção.
    antes = {p.name: p.read_bytes() for p in trab.iterdir()}
    cli.main(["claude", "--canal-paseo", "--", "--version"])
    assert {p.name: p.read_bytes() for p in trab.iterdir()} == antes


@pytest.mark.parametrize("estado", ESTADOS_NAO_CONFIGURADOS)
def test_no_canal_a_pasta_nao_configurada_recebe_instrucao(sem_launch, tmp_path,
                                                           monkeypatch, estado):
    """Não escrever não pode virar silêncio: sessão que sobe sem contexto e sem
    erro é o defeito que a entrega por canal existe para matar."""
    capturado = {}
    monkeypatch.setattr(cli, "_materializar",
                        lambda lanc, pasta: capturado.update(lanc=lanc))
    _pasta_no_estado(tmp_path, monkeypatch, estado)
    assert cli.main(["claude", "--canal-paseo", "--"]) == 0
    entregue = "\n".join(capturado["lanc"].arquivos_externos.values())
    assert "pasta ainda não é uma pasta de trabalho Koine" in entregue


@pytest.mark.parametrize("estado", ESTADOS_NAO_CONFIGURADOS)
def test_fora_do_canal_o_comportamento_do_terminal_nao_muda(tmp_path, monkeypatch,
                                                            estado, capsys):
    """A política é POR CANAL. No terminal o usuário fez `cd` de propósito, e o
    auto-guiar da v0.4.5 continua valendo — inclusive o erro do malformado."""
    monkeypatch.setattr(cli.launch, "lancar", lambda c, p, env=None, args=None: None)
    trab = _pasta_no_estado(tmp_path, monkeypatch, estado)
    cli.main(["claude"])
    if estado in ("ausente", "vazio"):
        assert (trab / "CONTEXTO.md").exists(), "o terminal ainda auto-guia"
