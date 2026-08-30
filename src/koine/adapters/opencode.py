import json
import os
import sys

from koine import cache, render, shell
from koine import paseo as _paseo
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

# Arquivo do OpenCode na pasta do usuário — hoje só no `koine gerar`. No
# launch a pasta não recebe nada: o config do bundle entrega tudo.
ARQUIVO = "AGENTS.md"
MARCADOR = "<!-- gerado por kn-agente -->"

# Degraus que a chave `shell` do OpenCode aceita, medido em 28/08/2026: `bash`
# funciona e `powershell` é tentado (falha com uv_spawn onde a política nega, em
# vez de ser ignorado). A doc do produto aceita "absolute path or a short name".
ACEITA_SHELL = (shell.PWSH, shell.POWERSHELL, shell.BASH, shell.CMD)

# Rota pelo Paseo, medida em 29/08/2026. Pelo builtin NÃO funciona: o
# gerenciador de servidor do OpenCode é singleton, inicializado no arranque do
# daemon com as configurações do builtin, e o `command` do provider é
# rejeitado — o daemon registra "already initialized with different runtime
# settings". A rota é o protocolo genérico, com o subcomando que sobe o
# servidor.
PASEO = _paseo.Rota(extends="acp", args=("acp",))


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Documento único no cache + `instructions` apontando só para ele.

    ATÉ 29/08/2026 este adapter era o ÚNICO a entregar os arquivos CRUS, por
    caminho absoluto: sem `strip_frontmatter` e sem rótulo de camada. Os outros
    quatro compõem um documento com `render.documento_inline`, que remove o
    frontmatter e nomeia cada seção. A divergência produzia dois defeitos com uma
    causa só (jd-task #704, medida na bancada Windows):

    1. A **Ficha Koine** da pasta ia junto, e o `agente:` dela — que é metadado
       do launcher, já consumido no launch — virava a única afirmação explícita
       de identidade no texto. Pedir `hermes` numa pasta que declara
       `agente: sheldon` subia **Sheldon**, sem erro e sem aviso.
    2. Sem o rótulo `## Agente`, o arquivo do agente chegava (medido: o modelo
       confirma tê-lo lido) e mesmo assim **não era adotado como identidade** —
       sem a ficha para copiar, o modelo respondia o codinome da sessão.

    O CONTEXTO.md passa a chegar por CONTEÚDO, como no copilot. A leitura viva
    que este adapter tinha de singular é o que carregava a ficha para dentro do
    prompt; a `prosa_sessao` cobre o que ela dava, dizendo ao agente que o
    arquivo da pasta é a fonte canônica e que o texto acima é snapshot.

    Mantém: config em ~/.cache/koine/opencode-configs/<slot>.json, env
    OPENCODE_CONFIG + OPENCODE_DISABLE_CLAUDE_CODE=1, aviso de AGENTS.md global,
    e o melhor shell que a máquina executa no Windows (escadinha em shell.py).
    """
    slot = cache.slot_id(cm.pasta_abs)
    cfg_path = cache.caminho_arquivo("opencode-configs", slot, "json")
    doc_path = cache.caminho_arquivo("opencode-configs", slot, "md")

    # aviso: ~/.config/opencode/AGENTS.md é mesclado pelo OpenCode em toda sessão
    global_path = _global_agents_md()
    if os.path.exists(global_path):
        print(f"aviso: {global_path} detectado — será mesclado nesta sessão Koine. "
              "Para isolar completamente, mova ou renomeie o arquivo.", file=sys.stderr)

    cfg = {"$schema": "https://opencode.ai/config.json", "instructions": [doc_path]}
    if sys.platform == "win32":
        # O default do OpenCode varia por versão e, na estação que bloqueia o
        # PowerShell, derruba a ferramenta de shell com `uv_spawn`. Em vez de
        # fixar `cmd` para todo mundo — o que rebaixava a máquina saudável —, o
        # Koine grava o melhor degrau que ESTA máquina executa.
        escolhido = shell.melhor(ACEITA_SHELL)
        if escolhido is not None:
            cfg["shell"] = escolhido.invocacao

    # paridade com json.MarshalIndent(cfg, "", "  ") do Go: indent 2, UTF-8 cru
    data = json.dumps(cfg, indent=2, ensure_ascii=False)
    return Lancamento(
        arquivos_externos={cfg_path: data, doc_path: _render(cm)},
        env_vars={"OPENCODE_CONFIG": cfg_path, "OPENCODE_DISABLE_CLAUDE_CODE": "1"},
    )


def _render(cm: ContextoMontado) -> str:
    doc = render.documento_inline("Sessão Koine — OpenCode", cm)
    return MARCADOR + "\n" + doc + "\n\n" + render.prosa_sessao(cm, "kn-opencode <agente> .")


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido, pelo `koine gerar`.

    Chega aqui só pelo `koine gerar`. O **modo skills** — o pacote sem
    Python — nunca alcança este código: quem escreve na pasta lá é a
    `/kn-12-prepara-contexto`, por `@path` e não por snapshot. Medido em
    30/08/2026; o docstring afirmava os dois desde o porte (jd-task #706).

    INLINE: sem wrapper não há OPENCODE_CONFIG, e o `instructions` do config é
    justamente o que aponta para os arquivos. Sobra o AGENTS.md da pasta.

    MESMO corpo do launch, e não uma segunda montagem: era a duplicação que
    deixava este caminho sem a `prosa_sessao` — o launch a ganhou na #704 e a
    cópia daqui ficou para trás (jd-task #706).
    """
    return ARQUIVO, _render(cm)


def _global_agents_md() -> str:
    """Porta de openCodeGlobalConfigPath (opencode.go) — XDG_CONFIG_HOME honrado."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "opencode", "AGENTS.md")
