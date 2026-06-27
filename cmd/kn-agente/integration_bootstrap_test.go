package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestIntegracao_BootstrapExplicito_GerarIncluiContexto verifica que
// após simular uma instalação (criar arquivos necessários), kn-agente
// gerar hermes <pasta> produz CLAUDE.md contendo referência @<CONTEXTO.md>.
func TestIntegracao_BootstrapExplicito_GerarIncluiContexto(t *testing.T) {
	tmpHome := t.TempDir()
	vaultDir := filepath.Join(tmpHome, ".local", "share", "koine")
	configDir := filepath.Join(tmpHome, ".config", "koine")
	if err := os.MkdirAll(filepath.Join(vaultDir, "agentes"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(configDir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(vaultDir, "KOINE.md"), []byte("# KOINE"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(vaultDir, "agentes", "hermes.md"), []byte("# Hermes"), 0o644); err != nil {
		t.Fatal(err)
	}

	// criar pasta de trabalho com CONTEXTO.md bootstrap
	pasta := filepath.Join(tmpHome, "koine")
	if err := os.MkdirAll(pasta, 0o755); err != nil {
		t.Fatal(err)
	}
	ctx := filepath.Join(pasta, "CONTEXTO.md")
	conteudoCtx := "---\nbootstrap: true\n---\n# Bootstrap\nHermes inicie /kn-01.\n"
	if err := os.WriteFile(ctx, []byte(conteudoCtx), 0o644); err != nil {
		t.Fatal(err)
	}

	// injetar lookups
	t.Setenv("HOME", tmpHome)
	t.Setenv("XDG_DATA_HOME", filepath.Join(tmpHome, ".local", "share"))
	t.Setenv("XDG_CONFIG_HOME", filepath.Join(tmpHome, ".config"))

	// executar caminho administrativo gerar (que renderiza com ClaudeCode adapter)
	if err := executar("hermes", pasta, nil); err != nil {
		t.Fatalf("executar: %v", err)
	}

	saida, err := os.ReadFile(filepath.Join(pasta, "CLAUDE.md"))
	if err != nil {
		t.Fatalf("CLAUDE.md não gerado: %v", err)
	}
	if !strings.Contains(string(saida), "@"+ctx) {
		t.Errorf("CLAUDE.md não contém @%s; saída:\n%s", ctx, saida)
	}
}
