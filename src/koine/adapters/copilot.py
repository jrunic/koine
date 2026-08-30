import os

from koine import cache, render, shell
from koine import paseo as _paseo
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

# Arquivo do Copilot na pasta do usuário — hoje só no `gerar` (modo skills). No
# launch a pasta não recebe nada: o bundle entrega tudo.
ARQUIVO = os.path.join(".github", "copilot-instructions.md")
MARCADOR = "<!-- gerado por kn-agente -->"

# Medido em 28/08/2026: usa PowerShell e SO PowerShell no Windows, e nao expoe
# chave para trocar. Onde a politica nega o powershell.exe, nao tem shell.
ACEITA_SHELL = (shell.PWSH, shell.POWERSHELL)

# Rota pelo Paseo, medida em 29/08/2026: mesma forma do claude — o Paseo o
# invoca com `--acp`, do cwd do workspace.
PASEO = _paseo.Rota(extends="copilot")


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Porta de harness.Copilot.Renderizar (copilot.go).

    Materializa o bundle em ~/.cache/koine/copilot-bundles/<slot>/, com TODAS
    as camadas em .github/instructions/*.instructions.md. Cria symlink
    <pasta>/.github/copilot-instructions.md → CONTEXTO.md e seta
    COPILOT_CUSTOM_INSTRUCTIONS_DIRS. Bootstrap: usuário + agente + env
    (+ bootstrap.instructions.md se houver CONTEXTO.md); sem symlink.

    O KOINE.md entra aqui desde a v0.7.1: o bundle nunca o levou (herança do
    copilot.go), e sem ele o agente sabia quem é o usuário e em que pasta está,
    mas não sabia o que é o Koine — em 3682 bytes, ~3% do input da sessão.

    O bundle NÃO tem AGENTS.md: medido em 27/08 com discriminante na mesma
    execução, o canal COPILOT_CUSTOM_INSTRUCTIONS_DIRS entrega os
    `*.instructions.md` e ignora o AGENTS.md. Usuário e agente moravam nele —
    isto é, não chegavam à sessão. Arquivo que o cliente não lê só engana quem
    for depurar."""
    bundle = cache.caminho_bundle("copilot-bundles", cache.slot_id(cm.pasta_abs))
    instr = os.path.join(bundle, ".github", "instructions")
    lanc = Lancamento(env_vars={"COPILOT_CUSTOM_INSTRUCTIONS_DIRS": bundle})

    if cm.usuario_path:
        lanc.arquivos_externos[os.path.join(instr, "usuario.instructions.md")] = \
            render.wrapar_instructions(_ler(cm.usuario_path))
    if cm.koine_path:
        lanc.arquivos_externos[os.path.join(instr, "koine.instructions.md")] = \
            render.wrapar_instructions(_ler(cm.koine_path))
    lanc.arquivos_externos[os.path.join(instr, "agente.instructions.md")] = \
        render.wrapar_instructions(_ler(cm.agente_path))

    if cm.instrucao_path:
        lanc.arquivos_externos[os.path.join(instr, "instrucao.instructions.md")] = \
            render.wrapar_instructions(_ler(cm.instrucao_path))

    # O CONTEXTO.md vai por CONTEÚDO, no bundle. Antes chegava por symlink na
    # pasta do usuário — e symlink na pasta é justamente o que sai de cena.
    if cm.contexto_path:
        lanc.arquivos_externos[os.path.join(instr, "contexto.instructions.md")] = \
            render.wrapar_instructions(_ler(cm.contexto_path))
    if cm.bootstrap:
        return lanc

    if cm.escopo_path:
        lanc.arquivos_externos[os.path.join(instr, "escopo.instructions.md")] = \
            render.wrapar_instructions(_ler(cm.escopo_path))
    for ip in cm.indice_paths:
        dom = render.dominio_de(ip)
        lanc.arquivos_externos[os.path.join(instr, f"kn-indice-{dom}.instructions.md")] = \
            render.wrapar_instructions(_ler(ip))

    return lanc


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido (`koine gerar`, modo skills).

    Aqui o conteúdo vai INLINE: sem wrapper não há
    COPILOT_CUSTOM_INSTRUCTIONS_DIRS para apontar o bundle, e o
    `.github/copilot-instructions.md` é a única via que sobra.
    """
    return ARQUIVO, MARCADOR + "\n" + render.documento_inline(
        "Sessão Koine — Copilot", cm) + "\n"


def _ler(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()
