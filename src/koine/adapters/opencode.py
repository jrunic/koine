import json
import os
import sys

from koine import cache, render, shell
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

# Arquivo do OpenCode na pasta do usuário — hoje só no `gerar` (modo skills). No
# launch a pasta não recebe nada: o config do bundle entrega tudo.
ARQUIVO = "AGENTS.md"
MARCADOR = "<!-- gerado por kn-agente -->"

# Degraus que a chave `shell` do OpenCode aceita, medido em 28/08/2026: `bash`
# funciona e `powershell` é tentado (falha com uv_spawn onde a política nega, em
# vez de ser ignorado). A doc do produto aceita "absolute path or a short name".
ACEITA_SHELL = (shell.PWSH, shell.POWERSHELL, shell.BASH, shell.CMD)


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Porta de harness.OpenCode.Renderizar (opencode.go).

    Materializa ~/.cache/koine/opencode-configs/<slot>.json com array
    instructions (paths absolutos). Symlink <pasta>/AGENTS.md → CONTEXTO.md.
    Env OPENCODE_CONFIG + OPENCODE_DISABLE_CLAUDE_CODE=1. Bootstrap: contexto
    direto em instructions; sem symlink. Avisa se AGENTS.md global existe.
    Em Windows declara o melhor shell que a máquina executa (escadinha em shell.py)."""
    cfg_path = cache.caminho_arquivo("opencode-configs", cache.slot_id(cm.pasta_abs), "json")

    # aviso: ~/.config/opencode/AGENTS.md é mesclado pelo OpenCode em toda sessão
    global_path = _global_agents_md()
    if os.path.exists(global_path):
        print(f"aviso: {global_path} detectado — será mesclado nesta sessão Koine. "
              "Para isolar completamente, mova ou renomeie o arquivo.", file=sys.stderr)

    instructions = []
    if cm.usuario_path:
        instructions.append(cm.usuario_path)
    # ordem canônica dos outros três adapters: usuário, Koine, agente, escopo,
    # índices. O KOINE.md faltava aqui desde o opencode.go.
    if cm.koine_path:
        instructions.append(cm.koine_path)
    instructions.append(cm.agente_path)
    if cm.instrucao_path:
        instructions.append(cm.instrucao_path)
    if not cm.bootstrap:
        if cm.escopo_path:
            instructions.append(cm.escopo_path)
        instructions.extend(cm.indice_paths)
    # O CONTEXTO.md entra por REFERÊNCIA — e aqui isso é melhor que a cópia: o
    # canal do opencode é uma lista de caminhos absolutos que o cliente abre, e
    # o arquivo é lido vivo, não como snapshot. Antes chegava por symlink na
    # pasta do usuário, que sai de cena.
    if cm.contexto_path:
        instructions.append(cm.contexto_path)

    cfg = {"$schema": "https://opencode.ai/config.json", "instructions": instructions}
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
    lanc = Lancamento(
        arquivos_externos={cfg_path: data},
        env_vars={"OPENCODE_CONFIG": cfg_path, "OPENCODE_DISABLE_CLAUDE_CODE": "1"},
    )
    return lanc


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido (`koine gerar`, modo skills).

    INLINE: sem wrapper não há OPENCODE_CONFIG, e o `instructions` do config é
    justamente o que aponta para os arquivos. Sobra o AGENTS.md da pasta.
    """
    return ARQUIVO, MARCADOR + "\n" + render.documento_inline(
        "Sessão Koine — OpenCode", cm) + "\n"


def _global_agents_md() -> str:
    """Porta de openCodeGlobalConfigPath (opencode.go) — XDG_CONFIG_HOME honrado."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "opencode", "AGENTS.md")
