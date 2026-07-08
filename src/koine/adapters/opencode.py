import json
import os
import sys

from koine import cache
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

# Arquivo de contexto do OpenCode no working dir — entra via symlink, não
# via arquivos_working_dir (porta de CaminhoArquivoContexto do opencode.go).
ARQUIVO = "AGENTS.md"


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Porta de harness.OpenCode.Renderizar (opencode.go).

    Materializa ~/.cache/koine/opencode-configs/<slot>.json com array
    instructions (paths absolutos). Symlink <pasta>/AGENTS.md → CONTEXTO.md.
    Env OPENCODE_CONFIG + OPENCODE_DISABLE_CLAUDE_CODE=1. Bootstrap: contexto
    direto em instructions; sem symlink. Avisa se AGENTS.md global existe."""
    cfg_path = cache.caminho_arquivo("opencode-configs", cache.slot_id(cm.pasta_abs), "json")

    # aviso: ~/.config/opencode/AGENTS.md é mesclado pelo OpenCode em toda sessão
    global_path = _global_agents_md()
    if os.path.exists(global_path):
        print(f"aviso: {global_path} detectado — será mesclado nesta sessão Koine. "
              "Para isolar completamente, mova ou renomeie o arquivo.", file=sys.stderr)

    instructions = []
    if cm.usuario_path:
        instructions.append(cm.usuario_path)
    instructions.append(cm.agente_path)
    if cm.bootstrap:
        # Bootstrap explícito: CONTEXTO.md vai direto em instructions
        # (não há symlink AGENTS.md → CONTEXTO.md em bootstrap, ver bloco final).
        if cm.contexto_path:
            instructions.append(cm.contexto_path)
    else:
        if cm.escopo_path:
            instructions.append(cm.escopo_path)
        instructions.extend(cm.indice_paths)

    # paridade com json.MarshalIndent(cfg, "", "  ") do Go: indent 2, UTF-8 cru
    data = json.dumps({"$schema": "https://opencode.ai/config.json",
                       "instructions": instructions}, indent=2, ensure_ascii=False)
    lanc = Lancamento(
        arquivos_externos={cfg_path: data},
        env_vars={"OPENCODE_CONFIG": cfg_path, "OPENCODE_DISABLE_CLAUDE_CODE": "1"},
    )
    if not cm.bootstrap:
        lanc.symlinks = {os.path.join(cm.pasta_abs, ARQUIVO): cm.contexto_path}
    return lanc


def _global_agents_md() -> str:
    """Porta de openCodeGlobalConfigPath (opencode.go) — XDG_CONFIG_HOME honrado."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "opencode", "AGENTS.md")
