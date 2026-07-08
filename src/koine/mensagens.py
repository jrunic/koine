"""Mensagens de onboarding do `instalar`.

Porta de cmd/kn-agente/mensagem_orientativa.go (integral, byte-fiel — exceto
a troca declarada `kn-agente instalar` → `koine instalar` no rodapé) e da
mensagem final de cmd/kn-agente/instalar.go:73-86.
"""

import platform
import shutil


def _os_atual() -> str:
    # espelha runtime.GOOS (lookupOS do Go)
    return {"Darwin": "darwin", "Linux": "linux", "Windows": "windows"}.get(
        platform.system(), platform.system().lower())


def _tem_binario(nome: str) -> bool:
    return shutil.which(nome) is not None


def orientativa_sem_harness() -> str:
    """Porta 1:1 de mensagemOrientativaSemHarness: cabeçalho + bloco Node
    (se ausente; texto por OS) + bloco Brew (darwin sem brew) + 4 blocos de
    cliente + rodapé."""
    os_ = _os_atual()
    node_ausente = not _tem_binario("node")
    brew_ausente = os_ == "darwin" and not _tem_binario("brew")

    partes = [
        "  (nenhum cliente IA detectado no PATH)\n",
        "\n",
        "  Koine funciona junto com um cliente IA terminal. Antes de\n",
        "  escolher um cliente, confira os pré-requisitos:\n",
        "\n",
    ]
    if node_ausente:
        partes.append(_bloco_node_ausente(os_))
        partes.append("\n")
    if brew_ausente:
        partes.append(_bloco_brew_ausente())
        partes.append("\n")
    partes.append("  Clientes IA suportados (escolha um):\n")
    partes.append("\n")
    partes.append(_bloco_cliente_claude(os_))
    partes.append("\n")
    partes.append(_bloco_cliente_antigravity(os_))
    partes.append("\n")
    partes.append(_bloco_cliente_copilot(os_))
    partes.append("\n")
    partes.append(_bloco_cliente_opencode(os_))
    partes.append("\n")
    partes.append("  Depois de instalar um cliente, rode `koine instalar` novamente —\n")
    partes.append("  ele detecta automaticamente.\n")
    return "".join(partes)


def _bloco_node_ausente(os_: str) -> str:
    b = [
        "  ⚠️  Node.js não encontrado\n",
        "\n",
        "     Vários clientes IA são instalados via npm (Claude Code, Copilot).\n",
        "     Como instalar:\n",
    ]
    if os_ == "darwin":
        b.append("       brew install node    (recomendado em macOS)\n")
        b.append("       ou baixe de https://nodejs.org/\n")
    elif os_ == "linux":
        b.append("       via gerenciador do seu sistema (apt, dnf, pacman, apk)\n")
        b.append("       ou baixe de https://nodejs.org/\n")
    elif os_ == "windows":
        b.append("       baixe e instale de https://nodejs.org/\n")
    else:
        b.append("       https://nodejs.org/\n")
    b.append("\n")
    b.append("     Documentação:  https://nodejs.org/\n")
    return "".join(b)


def _bloco_brew_ausente() -> str:
    return (
        "  💡 Homebrew não encontrado (macOS)\n"
        "\n"
        "     Gerenciador de pacotes recomendado no macOS — instala muitos\n"
        "     clientes IA com um comando.\n"
        "     Como instalar:\n"
        "       /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n"
        "\n"
        "     Documentação:  https://brew.sh/\n"
    )


def _bloco_cliente_claude(os_: str) -> str:
    b = ["  • Claude Code (Anthropic)\n"]
    if os_ == "darwin":
        b.append("    Como instalar:  brew install --cask claude-code\n")
        b.append("                    (ou: npm install -g @anthropic-ai/claude-code)\n")
    else:
        b.append("    Como instalar:  npm install -g @anthropic-ai/claude-code\n")
    b.append("    Docs:           https://docs.claude.com/en/docs/claude-code/setup\n")
    return "".join(b)


def _bloco_cliente_antigravity(os_: str) -> str:
    b = ["  • Antigravity (Google)\n"]
    if os_ == "windows":
        b.append("    Como instalar:  irm https://antigravity.google/cli/install.ps1 | iex\n")
    else:
        b.append("    Como instalar:  curl -fsSL https://antigravity.google/cli/install.sh | bash\n")
    b.append("    Docs:           https://antigravity.google/docs/cli-install\n")
    return "".join(b)


def _bloco_cliente_copilot(os_: str) -> str:
    b = ["  • GitHub Copilot CLI\n"]
    if os_ == "darwin":
        b.append("    Como instalar:  brew install --cask copilot-cli\n")
        b.append("                    (ou: npm install -g @github/copilot)\n")
    else:
        b.append("    Como instalar:  npm install -g @github/copilot\n")
    b.append("    Docs:           https://docs.github.com/copilot/copilot-cli\n")
    return "".join(b)


def _bloco_cliente_opencode(os_: str) -> str:
    b = ["  • OpenCode\n"]
    if os_ == "windows":
        b.append("    Como instalar:  npm install -g opencode-ai\n")
    else:
        b.append("    Como instalar:  curl -fsSL https://opencode.ai/install | bash\n")
    b.append("    Docs:           https://opencode.ai/docs\n")
    return "".join(b)


def final_instalar() -> str:
    # porta de instalar.go:72-83 (mensagem final do onboarding)
    return (
        "\nPara começar sua primeira sessão com Hermes:\n\n"
        "  kn-claude hermes koine\n\n"
        "Dentro da sessão, rode: /kn-01-recebe-usuario\n\n"
        "Se você usa outro cliente, troque o prefixo:\n"
        "  Antigravity:  kn-agy hermes koine\n"
        "  Copilot CLI:  kn-copilot hermes koine\n"
        "  OpenCode:     kn-opencode hermes koine\n"
        "  Codex CLI:    kn-codex hermes koine\n")
