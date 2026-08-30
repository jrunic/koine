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
                  "pasta-fora-do-koine.md", "escopo-inexistente.md",
                  "agente-do-canal-inexistente.md"):
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
    def espiao(agente, pasta, canal=False):
        capturado["agente"] = agente
        return original(agente, pasta, canal=canal)
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

    Desde a #709 o dano da segunda metade mudou de forma: o canal não derruba
    mais por agente inexistente, então a sessão SOBE — com o Hermes e o aviso —
    e o que se vê é a flag chegando ao cliente sem o valor, arrancado dela.
    """
    trab = _preparar_pasta_valida(tmp_path, monkeypatch)
    assert cli.main(["claude", "--canal-paseo", "--", "--model", "x-1"]) == 0
    assert sem_launch["args"][-2:] == ["--model", "x-1"]
    assert sem_launch["cwd"] == str(trab)

    # sem o separador: `x-1` vira posicional, é lido como AGENTE
    sem_launch.clear()
    assert cli.main(["claude", "--canal-paseo", "--model", "x-1"]) == 0
    assert sem_launch["args"][-1] == "--model", "o valor foi arrancado da flag"


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


# --- pasta VÁLIDA cujo escopo ou agente não existe (jd-task #709) -----------
#
# Os quatro estados acima são de BOOTSTRAP: o CONTEXTO.md não serve. Aqui o
# arquivo serve — tem ficha, tem `escopo:` — e o que não existe é aquilo que ele
# aponta. Cai depois da classificação, e por isso escapou do canal: derrubava.

def _quebrar_escopo(trab):
    (trab / "CONTEXTO.md").write_text(
        "---\ntype: contexto\nescopo: fantasma\nagente: sheldon\n---\n\n# T\n",
        encoding="utf-8")


def _entregue(capturado):
    return "\n".join(capturado["lanc"].arquivos_externos.values())


@pytest.fixture
def espiar_lancamento(monkeypatch):
    cap = {}
    monkeypatch.setattr(cli, "_materializar", lambda lanc, pasta: cap.update(lanc=lanc))
    return cap


def test_no_canal_escopo_inexistente_sobe_avisando(sem_launch, espiar_lancamento,
                                                   tmp_path, monkeypatch):
    """Escopo renomeado ou apagado põe toda pasta que o declarava neste estado.
    No canal, sair com código não-zero é beco sem saída: sobe com a instrução."""
    trab = _preparar_pasta_valida(tmp_path, monkeypatch)
    _quebrar_escopo(trab)
    assert cli.main(["claude", "--canal-paseo", "--"]) == 0
    assert "cwd" in sem_launch, "a sessão precisa ter subido"
    entregue = _entregue(espiar_lancamento)
    assert "escopo que não existe" in entregue
    assert "fantasma" in entregue, "o nome do escopo sumido tem que chegar ao agente"


def test_no_canal_escopo_inexistente_nao_escreve_na_pasta(sem_launch, tmp_path,
                                                          monkeypatch):
    """Bytes, não nomes: o CONTEXTO.md já existe, e um teste por nome passaria
    com e sem a correção."""
    trab = _preparar_pasta_valida(tmp_path, monkeypatch)
    _quebrar_escopo(trab)
    antes = {p.name: p.read_bytes() for p in trab.iterdir()}
    cli.main(["claude", "--canal-paseo", "--"])
    assert {p.name: p.read_bytes() for p in trab.iterdir()} == antes


def test_no_canal_a_variavel_com_agente_inexistente_sobe_avisando(
        sem_launch, espiar_lancamento, tmp_path, monkeypatch):
    """Quem escreve KOINE_AGENTE no entry é a /kn-04 — errar o nome é plausível,
    e o sintoma seria um provider que não abre, sem dizer por quê."""
    _preparar_pasta_valida(tmp_path, monkeypatch)
    monkeypatch.setenv("KOINE_AGENTE", "fantasma")
    assert cli.main(["claude", "--canal-paseo", "--"]) == 0
    assert "cwd" in sem_launch
    entregue = _entregue(espiar_lancamento)
    assert "provider desta sessão pede um agente que não existe" in entregue
    # O NOME, não só a prosa: a instrução manda o agente dizer qual nome falta, e
    # ele mora no frontmatter — que o render remove. A prova viva da #709 pegou a
    # instrução chegando sem o dado.
    assert "fantasma" in entregue
    # A correção é no ENTRY do provider, não no CONTEXTO.md: `definir-agente`
    # conserta o campo da pasta e o aviso voltaria para sempre.
    assert "koine definir-agente" not in entregue


def test_no_canal_o_agente_declarado_na_pasta_nao_derruba(sem_launch, tmp_path,
                                                          monkeypatch):
    """A guarda por `isatty` fecha a sessão quando não há terminal — e no canal
    NUNCA há, embora haja gente do outro lado (o celular). O aviso chega pela
    instrução; derrubar é que era o silêncio."""
    trab = _preparar_pasta_valida(tmp_path, monkeypatch, agente_da_pasta="fantasma")
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    assert cli.main(["claude", "--canal-paseo", "--"]) == 0
    assert "cwd" in sem_launch


def test_fora_do_canal_o_escopo_inexistente_continua_derrubando(tmp_path, monkeypatch,
                                                                capsys):
    """Pronto-quando 3: no terminal há um humano, e o erro alto com a lista dos
    escopos cadastrados continua sendo a resposta certa."""
    monkeypatch.setattr(cli.launch, "lancar", lambda c, p, env=None, args=None: None)
    trab = _preparar_pasta_valida(tmp_path, monkeypatch)
    _quebrar_escopo(trab)
    assert cli.main(["claude"]) == 1
    err = capsys.readouterr().err
    assert "fantasma" in err and "fixture" in err, "a lista dos cadastrados é o que cura"


def test_fora_do_canal_o_agente_declarado_sem_tty_continua_derrubando(tmp_path,
                                                                      monkeypatch):
    """A guarda do terminal não é afrouxada: sessão não-interativa fora do canal
    (um `--print`, um script) segue abortando em vez de rodar com o agente errado."""
    monkeypatch.setattr(cli.launch, "lancar", lambda c, p, env=None, args=None: None)
    _preparar_pasta_valida(tmp_path, monkeypatch, agente_da_pasta="fantasma")
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)
    assert cli.main(["claude"]) == 1


@pytest.mark.parametrize("cliente", ["claude", "opencode"])
def test_a_prosa_nao_contradiz_a_instrucao_do_canal(sem_launch, espiar_lancamento,
                                                    tmp_path, monkeypatch, cliente):
    """Duas vozes no mesmo documento, mandando o contrário uma da outra.

    A instrução `pasta-fora-do-koine.md` diz, com todas as letras, que nada foi
    escrito aqui e que o agente NÃO deve escrever `CONTEXTO.md` por conta
    própria — porque as sondagens do orquestrador rodam do cwd do serviço. A
    `prosa_sessao`, no mesmo arquivo, mandava criá-lo "desta pasta".

    Esse ramo da prosa é canal-only: no `resolver`, o único retorno de bootstrap
    SEM `contexto_path` é o `sem_contexto`, cujo chamador único é o launch do
    canal. Ou seja, ele contradizia sempre.

    As DUAS asserções importam: só a ausência passaria com a prosa inteira
    removida, e aí o agente perderia o aviso de snapshot junto.
    """
    _pasta_no_estado(tmp_path, monkeypatch, "ausente")
    assert cli.main([cliente, "--canal-paseo", "--"]) == 0
    entregue = _entregue(espiar_lancamento)
    assert "Crie o `./CONTEXTO.md`" not in entregue, "a prosa manda o contrário da instrução"
    assert "não crie o `./CONTEXTO.md` por conta própria" in entregue


# --- o prefixo de subcomando da rota ---------------------------------------

def test_a_rota_do_opencode_injeta_o_subcomando_antes_de_tudo(sem_launch, tmp_path,
                                                              monkeypatch):
    """O servidor de protocolo do opencode é um SUBCOMANDO: tem que ser o
    primeiro argumento, antes de qualquer coisa que o orquestrador passe."""
    _preparar_pasta_valida(tmp_path, monkeypatch)
    cli.main(["opencode", "--canal-paseo", "--", "--porta", "1"])
    assert sem_launch["args"][0] == "acp"
    assert sem_launch["args"][-2:] == ["--porta", "1"]


def test_cliente_com_rota_sem_subcomando_nao_ganha_prefixo(sem_launch, tmp_path,
                                                           monkeypatch):
    _preparar_pasta_valida(tmp_path, monkeypatch)
    cli.main(["claude", "--canal-paseo", "--", "--model", "x-1"])
    assert "acp" not in sem_launch["args"]


def test_o_prefixo_vale_tambem_na_pasta_sem_contexto(sem_launch, tmp_path, monkeypatch):
    """A sondagem do orquestrador roda do cwd dele, que é justamente uma pasta
    sem contexto — se o prefixo não valesse nesse ramo, o cliente subiria no
    modo errado exatamente onde o provider é avaliado."""
    _pasta_no_estado(tmp_path, monkeypatch, "ausente")
    cli.main(["opencode", "--canal-paseo", "--"])
    assert sem_launch["args"][0] == "acp"


def test_fora_do_canal_o_opencode_nao_ganha_o_subcomando(sem_launch, tmp_path,
                                                         monkeypatch):
    """No terminal `kn-opencode` sobe a interface, não o servidor de protocolo."""
    _preparar_pasta_valida(tmp_path, monkeypatch)
    cli.main(["opencode"])
    assert "acp" not in sem_launch["args"]


# --- a matriz legível por comando ------------------------------------------

def test_paseo_info_devolve_a_matriz_em_json(capsys):
    """É o contrato com a skill que escreve os providers: ela lê o nome do
    wrapper e o `extends` daqui, em vez de carregar uma cópia da tabela que
    envelheceria sozinha quando entrasse cliente novo."""
    import json
    assert cli.main(["paseo-info", "--json"]) == 0
    dados = json.loads(capsys.readouterr().out)
    assert dados["claude"] == {"wrapper": "kn-claude-paseo",
                               "provider": "kn-claude",
                               "provider_hermes": "kn-claude-hermes",
                               "extends": "claude", "args": []}
    assert dados["opencode"]["extends"] == "acp"
    assert dados["opencode"]["args"] == ["acp"]
    assert "codex" not in dados and "agy" not in dados


def test_paseo_info_em_texto_lista_os_mesmos_clientes(capsys):
    assert cli.main(["paseo-info"]) == 0
    saida = capsys.readouterr().out
    for cliente in ("claude", "copilot", "opencode"):
        assert cliente in saida
    assert "codex" not in saida


# --- a forma do --add-dir --------------------------------------------------

def test_add_dir_usa_a_forma_com_igual(tmp_path, monkeypatch):
    """`--add-dir` é VARIÁDICO no Claude Code: com a forma separada
    (`--add-dir <bundle>`) ele engole todo token seguinte que não comece com
    hífen. Medido na bancada em 30/08/2026 — `claude --add-dir <b> auth status`
    tratou `auth` e `status` como diretórios, ficou sem subcomando e caiu em
    modo sessão, pedindo prompt.

    Sessão do orquestrador não sofria porque o primeiro argumento dele é uma
    flag. O diagnóstico de autenticação sofria, e o campo `Auth:` do provider
    ficava inútil. A forma `--add-dir=<bundle>` termina a lista.
    """
    from koine import adapters
    from koine.contexto import ContextoMontado
    def w(n, t):
        p = tmp_path / n
        p.write_text(t, encoding="utf-8")
        return str(p)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    cm = ContextoMontado(usuario_path=w("u.md", "# U"), koine_path=w("k.md", "# K"),
                         agente_path=w("h.md", "# H"), escopo_path=w("e.md", "# E"),
                         indice_paths=[], contexto_path=w("CONTEXTO.md", "# C"),
                         pasta_abs=str(tmp_path))
    for nome in ("claude", "agy"):
        args = adapters.REGISTRY[nome].renderizar(cm).extra_args
        assert len(args) == 1, f"{nome}: {args}"
        assert args[0].startswith("--add-dir="), f"{nome}: {args}"


def test_paseo_info_prescreve_os_identificadores_dos_entries(capsys):
    """O identificador do provider não pode ser escolha do agente.

    Decisão do Orlando, 30/08/2026: se a skill inventar o nome, dois mentorados
    ficam com identificadores diferentes para a mesma coisa — e o dia em que
    isso virar código (um `koine` que lê ou conserta o config do orquestrador)
    encontra divergência sem regra. Mesma razão do wrapper: o Koine prescreve, a
    skill lê.
    """
    import json
    assert cli.main(["paseo-info", "--json"]) == 0
    dados = json.loads(capsys.readouterr().out)
    assert dados["claude"]["provider"] == "kn-claude"
    assert dados["claude"]["provider_hermes"] == "kn-claude-hermes"
    assert dados["opencode"]["provider"] == "kn-opencode"
    assert dados["opencode"]["provider_hermes"] == "kn-opencode-hermes"
