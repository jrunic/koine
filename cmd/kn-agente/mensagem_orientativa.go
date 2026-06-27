package main

import (
	"runtime"
	"strings"
)

// lookupOS é injetável para testes. Retorna runtime.GOOS por default.
var lookupOS = func() string { return runtime.GOOS }

// mensagemOrientativaSemHarness retorna texto multilinha orientando o usuário
// quando nenhum cliente IA é detectado no PATH.
//
// Estrutura:
// - Cabeçalho indicando ausência de clientes
// - Blocos condicionais de pré-requisitos (Node sempre; Brew só em macOS)
// - Lista dos 4 clientes IA com comando de instalação adaptado por OS
// - Rodapé orientando próximo passo
func mensagemOrientativaSemHarness() string {
	os := lookupOS()
	nodeAusente := !temBinario("node")
	brewAusente := os == "darwin" && !temBinario("brew")

	var b strings.Builder
	b.WriteString("  (nenhum cliente IA detectado no PATH)\n")
	b.WriteString("\n")
	b.WriteString("  Koine funciona junto com um cliente IA terminal. Antes de\n")
	b.WriteString("  escolher um cliente, confira os pré-requisitos:\n")
	b.WriteString("\n")

	if nodeAusente {
		b.WriteString(blocoNodeAusente(os))
		b.WriteString("\n")
	}

	if brewAusente {
		b.WriteString(blocoBrewAusente())
		b.WriteString("\n")
	}

	b.WriteString("  Clientes IA suportados (escolha um):\n")
	b.WriteString("\n")
	b.WriteString(blocoClienteClaude(os))
	b.WriteString("\n")
	b.WriteString(blocoClienteAntigravity(os))
	b.WriteString("\n")
	b.WriteString(blocoClienteCopilot(os))
	b.WriteString("\n")
	b.WriteString(blocoClienteOpenCode(os))
	b.WriteString("\n")
	b.WriteString("  Depois de instalar um cliente, rode `kn-agente instalar` novamente —\n")
	b.WriteString("  ele detecta automaticamente.\n")

	return b.String()
}

// temBinario checa se o binário está no PATH via lookupPathFunc (injetável).
func temBinario(nome string) bool {
	_, err := lookupPathFunc(nome)
	return err == nil
}

func blocoNodeAusente(os string) string {
	var b strings.Builder
	b.WriteString("  ⚠️  Node.js não encontrado\n")
	b.WriteString("\n")
	b.WriteString("     Vários clientes IA são instalados via npm (Claude Code, Copilot).\n")
	b.WriteString("     Como instalar:\n")
	switch os {
	case "darwin":
		b.WriteString("       brew install node    (recomendado em macOS)\n")
		b.WriteString("       ou baixe de https://nodejs.org/\n")
	case "linux":
		b.WriteString("       via gerenciador do seu sistema (apt, dnf, pacman, apk)\n")
		b.WriteString("       ou baixe de https://nodejs.org/\n")
	case "windows":
		b.WriteString("       baixe e instale de https://nodejs.org/\n")
	default:
		b.WriteString("       https://nodejs.org/\n")
	}
	b.WriteString("\n")
	b.WriteString("     Documentação:  https://nodejs.org/\n")
	return b.String()
}

func blocoBrewAusente() string {
	return "  💡 Homebrew não encontrado (macOS)\n" +
		"\n" +
		"     Gerenciador de pacotes recomendado no macOS — instala muitos\n" +
		"     clientes IA com um comando.\n" +
		"     Como instalar:\n" +
		"       /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n" +
		"\n" +
		"     Documentação:  https://brew.sh/\n"
}

func blocoClienteClaude(os string) string {
	var b strings.Builder
	b.WriteString("  • Claude Code (Anthropic)\n")
	switch os {
	case "darwin":
		b.WriteString("    Como instalar:  brew install --cask claude-code\n")
		b.WriteString("                    (ou: npm install -g @anthropic-ai/claude-code)\n")
	default:
		b.WriteString("    Como instalar:  npm install -g @anthropic-ai/claude-code\n")
	}
	b.WriteString("    Docs:           https://docs.claude.com/en/docs/claude-code/setup\n")
	return b.String()
}

func blocoClienteAntigravity(os string) string {
	var b strings.Builder
	b.WriteString("  • Antigravity (Google)\n")
	switch os {
	case "windows":
		b.WriteString("    Como instalar:  irm https://antigravity.google/cli/install.ps1 | iex\n")
	default:
		b.WriteString("    Como instalar:  curl -fsSL https://antigravity.google/cli/install.sh | bash\n")
	}
	b.WriteString("    Docs:           https://antigravity.google/docs/cli-install\n")
	return b.String()
}

func blocoClienteCopilot(os string) string {
	var b strings.Builder
	b.WriteString("  • GitHub Copilot CLI\n")
	switch os {
	case "darwin":
		b.WriteString("    Como instalar:  brew install --cask copilot-cli\n")
		b.WriteString("                    (ou: npm install -g @github/copilot)\n")
	default:
		b.WriteString("    Como instalar:  npm install -g @github/copilot\n")
	}
	b.WriteString("    Docs:           https://docs.github.com/copilot/copilot-cli\n")
	return b.String()
}

func blocoClienteOpenCode(os string) string {
	var b strings.Builder
	b.WriteString("  • OpenCode\n")
	switch os {
	case "windows":
		b.WriteString("    Como instalar:  npm install -g opencode-ai\n")
	default:
		b.WriteString("    Como instalar:  curl -fsSL https://opencode.ai/install | bash\n")
	}
	b.WriteString("    Docs:           https://opencode.ai/docs\n")
	return b.String()
}
