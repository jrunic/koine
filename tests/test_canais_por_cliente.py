"""Camada determinística do critério 1 da spec da #587.

O que este arquivo prova: o `Lancamento` de cada adapter carrega o canal que a
medição de 27/08/2026 provou entregar, e o conteúdo vai junto. O que ele NÃO
prova — e nenhum teste automatizado pode — é que o cliente carregou: isso é a
prova viva, com chamada real de LLM, fora da suíte.
"""
import json
import os

import pytest

from koine import adapters
from koine.contexto import ContextoMontado

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
    "claude": {"env": ["CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD"], "args": ["--add-dir"]},
    "agy": {"env": [], "args": ["--add-dir"]},
    "codex": {"env": [], "args": ["-c"]},
    "copilot": {"env": ["COPILOT_CUSTOM_INSTRUCTIONS_DIRS"], "args": []},
    "opencode": {"env": ["OPENCODE_CONFIG"], "args": []},
}

# Como o CONTEXTO.md chega em cada canal. Os dois modos são legítimos e a
# diferença é do canal, não do adapter: o opencode recebe uma lista de caminhos
# absolutos que ele mesmo abre — e ali a referência é MELHOR que a cópia, porque
# o arquivo é lido vivo. Onde o canal entrega arquivos, o conteúdo vai junto.
ENTREGA_CONTEXTO = {
    "claude": "conteudo", "agy": "conteudo", "codex": "conteudo",
    "copilot": "conteudo", "opencode": "referencia",
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
        assert arg in lanc.extra_args, f"{nome}: falta {arg}"


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
        if camada == "koine" and nome in ("copilot", "opencode"):
            # Nem o bundle do Copilot nem o config do OpenCode levaram o KOINE.md
            # desde o Go. É gap de CONTEÚDO, não de canal: fora do escopo desta
            # spec, que muda o canal e não o texto. Registrado aqui para não
            # passar por decisão.
            continue
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
    monkeypatch.setattr("koine.cli._montar_cm", lambda a, p: cm)
    cli.main(["codex", "hermes", pasta])

    assert any("model_instructions_file=" in a for a in capturado["args"]), \
        "o argumento do adapter não chegou ao cliente"


def test_opencode_config_continua_json_valido(cm_e_pasta):
    cm, _ = cm_e_pasta
    lanc = adapters.REGISTRY["opencode"].renderizar(cm)
    cfg = json.loads(next(iter(lanc.arquivos_externos.values())))
    assert cm.contexto_path in cfg["instructions"]
