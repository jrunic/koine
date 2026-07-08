import os

from koine import cache, render
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

# Arquivo de contexto do Copilot no working dir — entra via symlink, não
# via arquivos_working_dir (porta de CaminhoArquivoContexto do copilot.go).
ARQUIVO = os.path.join(".github", "copilot-instructions.md")


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Porta de harness.Copilot.Renderizar (copilot.go).

    Materializa o bundle em ~/.cache/koine/copilot-bundles/<slot>/:
    AGENTS.md (Usuário? + Agente) e .github/instructions/*.instructions.md.
    Cria symlink <pasta>/.github/copilot-instructions.md → CONTEXTO.md e seta
    COPILOT_CUSTOM_INSTRUCTIONS_DIRS. Bootstrap: só AGENTS.md + env
    (+ bootstrap.instructions.md se houver CONTEXTO.md); sem symlink."""
    bundle = cache.caminho_bundle("copilot-bundles", cache.slot_id(cm.pasta_abs))
    instr = os.path.join(bundle, ".github", "instructions")
    lanc = Lancamento(
        arquivos_externos={os.path.join(bundle, "AGENTS.md"): _montar_agents_md(cm)},
        env_vars={"COPILOT_CUSTOM_INSTRUCTIONS_DIRS": bundle},
    )

    if cm.bootstrap:
        if cm.contexto_path:
            lanc.arquivos_externos[os.path.join(instr, "bootstrap.instructions.md")] = \
                render.wrapar_instructions(_ler(cm.contexto_path))
        return lanc

    if cm.escopo_path:
        lanc.arquivos_externos[os.path.join(instr, "escopo.instructions.md")] = \
            render.wrapar_instructions(_ler(cm.escopo_path))
    for ip in cm.indice_paths:
        dom = render.dominio_de(ip)
        lanc.arquivos_externos[os.path.join(instr, f"kn-indice-{dom}.instructions.md")] = \
            render.wrapar_instructions(_ler(ip))

    lanc.symlinks = {os.path.join(cm.pasta_abs, ARQUIVO): cm.contexto_path}
    return lanc


def _montar_agents_md(cm: ContextoMontado) -> str:
    # só Usuário (se houver) + Agente — NÃO leva Koine/escopo/índices (copilot.go)
    partes = []
    if cm.usuario_path:
        partes.append(render.Parte("Usuário", _ler(cm.usuario_path)))
    partes.append(render.Parte("Agente", _ler(cm.agente_path)))
    return render.mescar_documentos("Sessão Koine — Copilot", partes)


def _ler(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()
