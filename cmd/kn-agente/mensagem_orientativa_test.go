package main

import (
	"errors"
	"strings"
	"testing"
)

// mockarLookups injeta lookupOS e lookupPathFunc para um cenário específico.
// Retorna função de restauração via t.Cleanup.
func mockarLookups(t *testing.T, os string, nodeAusente, brewAusente bool) {
	t.Helper()
	origOS := lookupOS
	origPath := lookupPathFunc
	t.Cleanup(func() {
		lookupOS = origOS
		lookupPathFunc = origPath
	})
	lookupOS = func() string { return os }
	lookupPathFunc = func(name string) (string, error) {
		switch name {
		case "node":
			if nodeAusente {
				return "", errors.New("not found")
			}
			return "/usr/local/bin/node", nil
		case "brew":
			if brewAusente {
				return "", errors.New("not found")
			}
			return "/opt/homebrew/bin/brew", nil
		}
		return "/usr/local/bin/" + name, nil
	}
}

func TestMensagemOrientativa_DarwinCompleto(t *testing.T) {
	// macOS com Node e Brew → sem blocos de pré-req
	mockarLookups(t, "darwin", false, false)
	msg := mensagemOrientativaSemHarness()

	if strings.Contains(msg, "Node.js não encontrado") {
		t.Error("não deveria ter bloco Node (Node está presente)")
	}
	if strings.Contains(msg, "Homebrew não encontrado") {
		t.Error("não deveria ter bloco Homebrew (Brew está presente)")
	}
	// Mas deve listar os 4 clientes
	for _, cliente := range []string{"Claude Code", "Antigravity", "Copilot CLI", "OpenCode"} {
		if !strings.Contains(msg, cliente) {
			t.Errorf("cliente %q ausente na lista", cliente)
		}
	}
	// macOS deve mostrar variante brew para Claude
	if !strings.Contains(msg, "brew install --cask claude-code") {
		t.Error("variante brew para Claude ausente em macOS")
	}
}

func TestMensagemOrientativa_DarwinSemNode(t *testing.T) {
	mockarLookups(t, "darwin", true, false)
	msg := mensagemOrientativaSemHarness()

	if !strings.Contains(msg, "Node.js não encontrado") {
		t.Error("bloco Node ausente quando Node faltando")
	}
	if strings.Contains(msg, "Homebrew não encontrado") {
		t.Error("não deveria ter bloco Homebrew (Brew presente)")
	}
	if !strings.Contains(msg, "brew install node") {
		t.Error("instrução de instalação de Node via brew ausente em macOS")
	}
}

func TestMensagemOrientativa_DarwinSemNodeSemBrew(t *testing.T) {
	mockarLookups(t, "darwin", true, true)
	msg := mensagemOrientativaSemHarness()

	if !strings.Contains(msg, "Node.js não encontrado") {
		t.Error("bloco Node ausente")
	}
	if !strings.Contains(msg, "Homebrew não encontrado") {
		t.Error("bloco Homebrew ausente")
	}
	if !strings.Contains(msg, "https://brew.sh") {
		t.Error("link brew.sh ausente")
	}
}

func TestMensagemOrientativa_LinuxSemNode(t *testing.T) {
	mockarLookups(t, "linux", true, false) // brew flag irrelevante em linux
	msg := mensagemOrientativaSemHarness()

	if !strings.Contains(msg, "Node.js não encontrado") {
		t.Error("bloco Node ausente")
	}
	if strings.Contains(msg, "Homebrew não encontrado") {
		t.Error("Linux NÃO deve mostrar bloco Homebrew")
	}
	// Linux deve sugerir gerenciador genérico
	if !strings.Contains(msg, "apt") || !strings.Contains(msg, "dnf") {
		t.Error("orientação Linux genérica (apt/dnf) ausente")
	}
	// Linux NÃO deve mostrar variante brew para Claude
	if strings.Contains(msg, "brew install --cask claude-code") {
		t.Error("Linux NÃO deve mostrar variante brew para Claude")
	}
}

func TestMensagemOrientativa_WindowsComNode(t *testing.T) {
	mockarLookups(t, "windows", false, true) // brew flag irrelevante
	msg := mensagemOrientativaSemHarness()

	if strings.Contains(msg, "Node.js não encontrado") {
		t.Error("não deveria ter bloco Node (Node presente)")
	}
	if strings.Contains(msg, "Homebrew não encontrado") {
		t.Error("Windows NÃO deve mostrar bloco Homebrew")
	}
	// Windows: Antigravity deve mostrar variante PowerShell
	if !strings.Contains(msg, "irm https://antigravity.google/cli/install.ps1") {
		t.Error("variante PowerShell de Antigravity ausente em Windows")
	}
}

func TestMensagemOrientativa_TerminaComProximoPasso(t *testing.T) {
	mockarLookups(t, "darwin", false, false)
	msg := mensagemOrientativaSemHarness()
	if !strings.Contains(msg, "rode `kn-agente instalar` novamente") {
		t.Error("mensagem final orientando próximo passo ausente")
	}
}
