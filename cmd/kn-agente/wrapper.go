package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/jrunic/koine/internal/harness"
	"github.com/jrunic/koine/internal/indice"
	"github.com/jrunic/koine/internal/pasta"
)

// clientesSuportados mapeia sufixo do binário → ativo na onda atual.
var clientesSuportados = map[string]bool{
	"claude":   true,
	"agy":      true, // Antigravity CLI
	"copilot":  true, // Onda 2 — Plano 2
	"opencode": true, // Onda 2 — Plano 3
	"codex":    true, // inline AGENTS.md + -c project_doc_max_bytes
}

// clienteDoBinario extrai o cliente do nome do binário (ex: kn-claude → "claude").
// Retorna ("", false) se não for wrapper conhecido e ativo nesta onda.
func clienteDoBinario(nome string) (string, bool) {
	if !strings.HasPrefix(nome, "kn-") || nome == "kn-agente" {
		return "", false
	}
	sufixo := strings.TrimPrefix(nome, "kn-")
	ativo, ok := clientesSuportados[sufixo]
	if !ok {
		return "", false
	}
	if !ativo {
		fmt.Fprintf(os.Stderr, "cliente %q ainda não suportado nesta versão do Koine\n", sufixo)
		return "", false
	}
	return sufixo, true
}

// lancarCliente é injetável para testes.
var lancarCliente = func(c, p string, env map[string]string, args []string) error {
	return lancarClienteImpl(c, p, env, args)
}

// rodarWrapper é o fluxo completo do wrapper de cliente IA:
// resolve pasta → resolve contexto → gera índices → seleciona adapter →
// renderiza → verifica conflitos → materializa (local + externo + symlinks) → lança cliente.
func rodarWrapper(cliente string, args []string) error {
	args, substituir := parseSubstituir(args)
	if len(args) < 1 {
		return fmt.Errorf("uso: kn-%s <agente> [pasta]", cliente)
	}
	agente := args[0]
	pastaArg := ""
	if len(args) >= 2 {
		pastaArg = args[1]
	}

	pastaAbs, err := pasta.Resolver(pastaArg)
	if err != nil {
		return fmt.Errorf("resolver pasta: %w", err)
	}

	cm, agenteEfetivo, err := resolverContextoParaWrapper(agente, pastaAbs)
	if err != nil {
		return err
	}

	if !cm.Bootstrap {
		pastaRef := derivarPastaRef(cm)
		domsDeclarados := derivarDominios(cm)
		if pastaRef != "" {
			if err := indice.Gerar(pastaRef, domsDeclarados, os.Stderr); err != nil {
				return fmt.Errorf("gerador de índices: %w", err)
			}
		}
	}

	adapter := adapterParaCliente(cliente, agenteEfetivo, pastaAbs)
	lancamento, err := adapter.Renderizar(cm)
	if err != nil {
		return err
	}

	if !substituir {
		if err := verificarConflitos(lancamento, pastaAbs); err != nil {
			return err
		}
	}

	if err := materializarArquivosLocais(pastaAbs, lancamento.ArquivosNoWorkingDir); err != nil {
		return err
	}
	if err := materializarArquivosExternos(lancamento.ArquivosExternos); err != nil {
		return err
	}
	if err := criarSymlinksLancamento(lancamento.Symlinks); err != nil {
		return err
	}

	return lancarCliente(cliente, pastaAbs, lancamento.EnvVars, lancamento.ExtraArgs)
}

// adapterParaCliente retorna o adapter Harness adequado para o cliente IA.
func adapterParaCliente(cliente, agente, pastaAbs string) harness.Harness {
	switch cliente {
	case "agy":
		return &harness.Antigravity{VaultFS: vaultFS, Agente: agente}
	case "copilot":
		return &harness.Copilot{Agente: agente, PastaAbs: pastaAbs}
	case "opencode":
		return &harness.OpenCode{Agente: agente, PastaAbs: pastaAbs}
	case "codex":
		return &harness.Codex{Agente: agente}
	default: // "claude"
		return &harness.ClaudeCode{VaultFS: vaultFS, Agente: agente}
	}
}
