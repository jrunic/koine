"""Camada determinística do critério 1 da spec da #587.

O que este arquivo prova: o `Lancamento` de cada adapter carrega o canal que a
medição de 27/08/2026 provou entregar, e o conteúdo vai junto. O que ele NÃO
prova — e nenhum teste automatizado pode — é que o cliente carregou: isso é a
prova viva, com chamada real de LLM, fora da suíte.
"""
import json
import os
import shutil

import pytest

from koine import adapters, cli
from koine.contexto import ContextoMontado

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Uma linha única por camada: asserção sobre cabeçalho que o próprio adapter
# escreve passaria com o arquivo de origem vazio.
LINHAS = {
    "usuario": "Linha unica da camada usuario.",
    "koine": "Linha unica da camada koine.",
    "agente": "Linha unica da camada agente.",
    "escopo": "Linha unica da camada escopo.",
    "indice": "Linha unica da camada indice.",
    "contexto": "Linha unica do CONTEXTO.md desta fixture.",
}

# Canais medidos em 27/08/2026 (kn-agente-integracao-clientes.md §Canais).
CANAIS = {
    # `--add-dir=` com igual: a forma separada é variádica e engole o token
    # seguinte quando ele não começa com hífen (medido em 30/08/2026).
    "claude": {"env": ["CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD"], "args": ["--add-dir="]},
    "agy": {"env": [], "args": ["--add-dir="]},
    "codex": {"env": [], "args": ["-c"]},
    "copilot": {"env": ["COPILOT_CUSTOM_INSTRUCTIONS_DIRS"], "args": []},
    "opencode": {"env": ["OPENCODE_CONFIG"], "args": []},
}

# Como o CONTEXTO.md chega em cada canal. Desde 29/08/2026 é CONTEÚDO nos cinco.
# Até então o opencode entregava por REFERÊNCIA — uma lista de caminhos absolutos
# que ele mesmo abre — e este comentário afirmava que a referência era MELHOR,
# "porque o arquivo é lido vivo". A medição da #704 desmentiu: ler o arquivo do
# usuário cru é o que leva a Ficha Koine para dentro do prompt, e o `agente:`
# dela vence o agente pedido. A leitura viva valia menos do que custava.
ENTREGA_CONTEXTO = {
    "claude": "conteudo", "agy": "conteudo", "codex": "conteudo",
    "copilot": "conteudo", "opencode": "conteudo",
}


@pytest.fixture
def cm_e_pasta(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    pasta = tmp_path / "trabalho"
    pasta.mkdir()

    def w(nome, camada):
        p = tmp_path / nome
        p.write_text(f"# {camada}\n{LINHAS[camada]}\n", encoding="utf-8")
        return str(p)

    ctx = pasta / "CONTEXTO.md"
    # ficha real: o launch classifica a pasta antes de chamar o adapter
    ctx.write_text("---\ntype: contexto\nescopo: fixture\n---\n\n"
                   f"# Pasta\n{LINHAS['contexto']}\n", encoding="utf-8")
    cm = ContextoMontado(
        usuario_path=w("u.md", "usuario"), koine_path=w("k.md", "koine"),
        agente_path=w("hermes.md", "agente"), escopo_path=w("e.md", "escopo"),
        indice_paths=[w("kn-indice-tecnologia.md", "indice")],
        contexto_path=str(ctx), pasta_abs=str(pasta))
    return cm, str(pasta)


def _entregue(lanc, cm) -> str:
    """O que o canal leva: conteúdo dos arquivos externos MAIS o conteúdo dos
    arquivos que ele referencia por caminho absoluto — que é o que o cliente vai
    abrir. Resolver a referência é o que torna os dois modos comparáveis."""
    partes = list(lanc.arquivos_externos.values())
    for texto in list(lanc.arquivos_externos.values()) + list(lanc.extra_args):
        for tok in texto.replace('"', " ").replace(",", " ").split():
            tok = tok.split("=")[-1].strip()
            if os.path.isabs(tok) and os.path.isfile(tok):
                with open(tok, encoding="utf-8") as f:
                    partes.append(f.read())
    return "\n".join(partes)


# Parametrizado, não em laço: com laço, a falha de um cliente esconde a dos
# outros — e a mutação de poder não consegue provar que o teste discrimina.
@pytest.mark.parametrize("nome", sorted(CANAIS))
def test_cada_cliente_entrega_pelo_canal_medido(cm_e_pasta, nome):
    cm, _ = cm_e_pasta
    lanc = adapters.REGISTRY[nome].renderizar(cm)
    for var in CANAIS[nome]["env"]:
        assert var in lanc.env_vars, f"{nome}: falta {var}"
    for arg in CANAIS[nome]["args"]:
        assert any(a == arg or a.startswith(arg) for a in lanc.extra_args), \
            f"{nome}: falta {arg}"


@pytest.mark.parametrize("nome", sorted(CANAIS))
def test_nenhum_adapter_escreve_na_pasta_no_launch(cm_e_pasta, nome):
    """Critério 3. Roda nos DOIS estados: a materialização do CONTEXTO bootstrap
    é do LAUNCH, não do adapter, e não pode ser confundida com escrita de
    adapter."""
    import dataclasses
    cm, _ = cm_e_pasta
    cm_boot = dataclasses.replace(cm, bootstrap=True, escopo_path="", indice_paths=[])
    for atual in (cm, cm_boot):
        lanc = adapters.REGISTRY[nome].renderizar(atual)
        assert lanc.arquivos_working_dir == {}, f"{nome} escreve na pasta"
        assert lanc.symlinks == {}, f"{nome} cria symlink na pasta"


@pytest.mark.parametrize("nome", sorted(ENTREGA_CONTEXTO))
def test_o_contexto_da_pasta_chega(cm_e_pasta, nome):
    """Com o symlink removido, o CONTEXTO.md tem que chegar pelo canal — senão a
    mudança troca 'entrega errada' por 'não entrega'."""
    cm, _ = cm_e_pasta
    lanc = adapters.REGISTRY[nome].renderizar(cm)
    assert LINHAS["contexto"] in _entregue(lanc, cm), \
        f"{nome}: o CONTEXTO.md não chega ({ENTREGA_CONTEXTO[nome]})"


@pytest.mark.parametrize("nome", sorted(CANAIS))
def test_todas_as_camadas_chegam(cm_e_pasta, nome):
    """env e args certos não provam que o CONTEÚDO foi junto."""
    cm, _ = cm_e_pasta
    entregue = _entregue(adapters.REGISTRY[nome].renderizar(cm), cm)
    for camada, marca in LINHAS.items():
        assert marca in entregue, f"{nome}: camada {camada} não chega"


def test_nada_do_bundle_mora_dentro_da_pasta_do_usuario(cm_e_pasta):
    """O bundle é derivado e mora no cache. Escrever no cwd por outro caminho
    seria a mesma poluição com outro nome — e o critério 3 mede por listagem."""
    cm, pasta = cm_e_pasta
    for nome in adapters.REGISTRY:
        lanc = adapters.REGISTRY[nome].renderizar(cm)
        for absp in lanc.arquivos_externos:
            assert not os.path.abspath(absp).startswith(os.path.abspath(pasta) + os.sep), \
                f"{nome}: escreve {absp} dentro da pasta do usuário"


def test_todo_adapter_tem_as_duas_operacoes(cm_e_pasta):
    """Contrato: entregar por canal E materializar na pasta a pedido. Adapter
    novo entra na varredura sozinho."""
    cm, _ = cm_e_pasta
    for nome in adapters.REGISTRY:
        arquivo, conteudo = adapters.REGISTRY[nome].renderizar_para_pasta(cm)
        assert arquivo and conteudo, f"{nome}: sem operação para o modo skills"


def test_extra_args_com_valor_dinamico_chegam_ao_cliente(cm_e_pasta, monkeypatch):
    """O codex precisa de `-c model_instructions_file=<caminho do slot>`, que
    varia por pasta e não cabe numa constante de módulo. Sem o plumbing, o
    adapter declara e ninguém entrega — a forma do defeito do Copilot, agora nos
    argumentos."""
    from koine import cli
    cm, pasta = cm_e_pasta
    capturado = {}
    monkeypatch.setattr("koine.launch.lancar",
                        lambda cliente, p=None, env=None, args=None: capturado.update(
                            args=args or []) or 0)
    monkeypatch.chdir(pasta)
    monkeypatch.setattr("koine.cli._montar_cm", lambda a, p, canal=False: cm)
    cli.main(["codex", "hermes", pasta])

    assert any("model_instructions_file=" in a for a in capturado["args"]), \
        "o argumento do adapter não chegou ao cliente"


def test_opencode_config_continua_json_valido(cm_e_pasta):
    """O `instructions` aponta para o documento COMPOSTO no cache, não mais para
    os arquivos crus. A troca é a correção da #704; o que este teste guarda é o
    contrato do canal: JSON válido, com `instructions` de caminho absoluto que
    existe entre os arquivos que o adapter materializa."""
    cm, _ = cm_e_pasta
    lanc = adapters.REGISTRY["opencode"].renderizar(cm)
    cfg = json.loads(next(iter(lanc.arquivos_externos.values())))
    assert cm.contexto_path not in cfg["instructions"], \
        "o CONTEXTO.md cru voltou ao instructions — a Ficha Koine vaza de novo"
    for caminho in cfg["instructions"]:
        assert os.path.isabs(caminho)
        assert caminho in lanc.arquivos_externos


@pytest.mark.parametrize("nome", sorted(CANAIS))
def test_a_ficha_da_pasta_nao_compete_com_o_agente_pedido(cm_e_pasta, nome):
    """A Ficha Koine é metadado do LAUNCHER, não conteúdo para o modelo.

    O `agente:` dela diz qual agente a PASTA declara por default, e o launch já
    o consumiu quando o adapter roda. Entregue ao modelo, ele vira a única
    afirmação explícita de identidade no texto — e vence o agente que o usuário
    PEDIU. Medido em 29/08/2026 na bancada Windows (jd-task #704): pasta com
    `agente: sheldon`, sessão aberta com `hermes`, e os cinco clientes deveriam
    dar Hermes. Só o opencode dava Sheldon — o único que entregava o arquivo
    cru, sem `strip_frontmatter`.
    """
    cm, pasta = cm_e_pasta
    with open(os.path.join(pasta, "CONTEXTO.md"), "w", encoding="utf-8") as f:
        f.write("---\ntype: contexto\nescopo: fixture\nagente: sheldon\n---\n\n"
                f"# Pasta\n{LINHAS['contexto']}\n")
    entregue = _entregue(adapters.REGISTRY[nome].renderizar(cm), cm)
    assert "agente: sheldon" not in entregue, (
        f"{nome}: a Ficha Koine da pasta chega ao modelo e compete com o agente pedido")


# Frase da `render.prosa_sessao` na variante de pasta configurada. Asserção sobre
# a FRASE, não sobre a chamada: o que protege o usuário é o texto chegar, e um
# adapter que montasse a prosa de outro jeito continuaria correto.
PROSA = "a fonte canônica é o arquivo"

# Os dois caminhos pelos quais o conteúdo do CONTEXTO.md sai como SNAPSHOT.
CAMINHOS = ["launch", "pasta"]


def _corpo(nome, cm, caminho):
    ad = adapters.REGISTRY[nome]
    if caminho == "launch":
        return "\n".join(ad.renderizar(cm).arquivos_externos.values())
    return ad.renderizar_para_pasta(cm)[1]


@pytest.mark.parametrize("caminho", CAMINHOS)
@pytest.mark.parametrize("nome", sorted(CANAIS))
def test_o_snapshot_do_contexto_nunca_viaja_sem_a_prosa(cm_e_pasta, nome, caminho):
    """Irmão do invariante da Ficha Koine, no outro sentido.

    Todo canal entrega o CONTEXTO.md por CONTEÚDO desde 29/08/2026 — o que o
    agente lê é uma CÓPIA. Sem a prosa que diz isso, ele edita a cópia e o
    trabalho da sessão se perde no fechamento; é o mesmo desfecho do defeito de
    produção da v0.6.1, quando a /kn-99 comia a Ficha Koine.

    Medido em 30/08/2026 (jd-task #706): faltava em três dos dez pares — o
    copilot nos DOIS caminhos (e o launch dele é o default desde a v0.7.0) e o
    opencode na pasta. A tarefa nomeava só o modo skills; a execução dos dois
    caminhos é que achou o launch do copilot.
    """
    cm, _ = cm_e_pasta
    assert PROSA in _corpo(nome, cm, caminho), (
        f"{nome}/{caminho}: o snapshot do CONTEXTO.md chega sem dizer que é snapshot")


# --- dois agentes na MESMA pasta não podem dividir o mesmo cache (#708) -----

def _com_agente(cm, tmp_path, nome, marca):
    """Cópia do cm apontando para outro arquivo de agente, mesma pasta."""
    import copy
    p = tmp_path / f"{nome}.md"
    p.write_text(f"# {nome}\n{marca}\n", encoding="utf-8")
    outro = copy.copy(cm)
    outro.agente_path = str(p)
    return outro


@pytest.mark.parametrize("nome", sorted(CANAIS))
def test_dois_agentes_na_mesma_pasta_nao_se_sobrescrevem(cm_e_pasta, tmp_path, nome):
    """A corrida que produzia o agente errado, sem erro (jd-task #708).

    O `kn-<cliente>` e o `kn-<cliente>-hermes` do mesmo workspace escreviam nos
    MESMOS arquivos de cache, porque o slot vinha só da pasta. Medido em
    30/08/2026, dirigindo o servidor ACP do opencode: ele lê o arquivo de
    instruções **por sessão**, com o processo de pé — então a sessão lê o que o
    ÚLTIMO provider escreveu, não o que o provider dela escreveu.

    Não é exclusividade do opencode: o que estava errado é o slot, e os quatro
    adapters com bundle o compartilhavam. Nos outros a janela entre escrever e
    ler é menor, o que os fazia acertar por sorte de tempo — não por desenho.
    """
    cm_a, _ = cm_e_pasta
    cm_b = _com_agente(cm_a, tmp_path, "bruce", "SOU-O-BRUCE")
    ad = adapters.REGISTRY[nome]

    escrito_a = dict(ad.renderizar(cm_a).arquivos_externos)
    escrito_b = dict(ad.renderizar(cm_b).arquivos_externos)

    colididos = sorted(set(escrito_a) & set(escrito_b))
    assert not colididos, (
        f"{nome}: {len(colididos)} arquivo(s) de cache compartilhados entre dois "
        f"agentes da mesma pasta — o último a rodar governa a sessão do outro")


# --- pasta-referências inacessível não derruba a sessão (jd-task #761) ------

def _cenario_refs(tmp_path, monkeypatch, refs_path, dominios="[tecnologia]"):
    """HOME isolado com um escopo apontando para `refs_path` e domínio declarado.

    O domínio é obrigatório para o teste ter poder: sem ele o `indice.gerar` não
    escreve arquivo nenhum, a guarda nunca é exercida e o teste passa em falso —
    é a quinta forma de teste sem poder.
    """
    home = tmp_path / "home"
    cfg, data = home / ".config" / "koine", home / ".local" / "share" / "koine"
    (cfg / "escopos").mkdir(parents=True)
    (cfg / "agentes").mkdir()
    (data / "agentes").mkdir(parents=True)
    (data / "bootstrap").mkdir()
    shutil.copy(os.path.join(REPO, "vault", "KOINE.md"), data / "KOINE.md")
    shutil.copy(os.path.join(REPO, "vault", "agentes", "hermes.md"),
                data / "agentes" / "hermes.md")
    (cfg / "teste.md").write_text("---\ntype: usuario\nnome: T\n---\n\n# T\n",
                                  encoding="utf-8")
    (cfg / "escopos" / "fixture.md").write_text(
        "---\ntype: escopo\nnome: fixture\n"
        f"pasta-referencias: abs:{refs_path}\n---\n\n# fixture\n", encoding="utf-8")
    trab = tmp_path / "trabalho"
    trab.mkdir()
    (trab / "CONTEXTO.md").write_text(
        f"---\ntype: contexto\nescopo: fixture\ndominios: {dominios}\n---\n\n# T\n",
        encoding="utf-8")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.chdir(trab)
    return trab


@pytest.fixture
def _sem_launch(monkeypatch):
    cap = {}
    monkeypatch.setattr("koine.launch.lancar",
                        lambda c, p, env=None, args=None: cap.update(cwd=p))
    return cap


@pytest.mark.parametrize("canal", [[], ["--canal-paseo", "--"]])
def test_pasta_referencias_inacessivel_nao_derruba_a_sessao(tmp_path, monkeypatch,
                                                            capsys, _sem_launch, canal):
    """O defeito de produção: `indice.gerar` ESCREVE na pasta-referências a cada
    launch, e `_escrever` abre o arquivo sem tratar `OSError`. Pasta em nuvem que
    o processo não alcança derrubava a sessão com traceback de Python.

    Degrada nos DOIS canais, de propósito: no terminal há um humano, e ele
    também prefere sessão sem índice a traceback.
    """
    _cenario_refs(tmp_path, monkeypatch, str(tmp_path / "OneDrive-que-sumiu"))
    assert cli.main(["claude"] + canal) == 0
    assert "cwd" in _sem_launch, "a sessão precisa ter subido"
    err = capsys.readouterr().err
    assert "OneDrive-que-sumiu" in err, "o aviso tem que dizer QUAL caminho falhou"
