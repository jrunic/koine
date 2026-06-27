package main

import (
	"bytes"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	koine "github.com/jrunic/koine"
)

func injetarHomeEConfig(t *testing.T) (home, config string) {
	t.Helper()
	home = t.TempDir()
	config = filepath.Join(home, ".config", "koine")
	if err := os.MkdirAll(config, 0o755); err != nil {
		t.Fatal(err)
	}
	origHome := lookupHomeInstall
	origConfig := lookupConfigDirInstall
	origStdin := stdinReader
	origStderr := stderrWriter
	t.Cleanup(func() {
		lookupHomeInstall = origHome
		lookupConfigDirInstall = origConfig
		stdinReader = origStdin
		stderrWriter = origStderr
	})
	lookupHomeInstall = func() (string, error) { return home, nil }
	lookupConfigDirInstall = func() string { return config }
	return
}

func TestPastaCanonica_NovaPasta_CriaTudo(t *testing.T) {
	home, _ := injetarHomeEConfig(t)
	stdinReader = strings.NewReader("\n") // Enter aceita default
	resultado, err := configurarPastaCanonica(koine.VaultFS, true)
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	pastaEsperada := filepath.Join(home, "koine")
	if resultado != pastaEsperada {
		t.Errorf("pasta = %q, want %q", resultado, pastaEsperada)
	}
	if _, err := os.Stat(pastaEsperada); err != nil {
		t.Errorf("pasta não criada: %v", err)
	}
	ctxPath := filepath.Join(pastaEsperada, "CONTEXTO.md")
	conteudo, err := os.ReadFile(ctxPath)
	if err != nil {
		t.Errorf("CONTEXTO.md não criado: %v", err)
	}
	if !strings.Contains(string(conteudo), "bootstrap: true") {
		t.Errorf("CONTEXTO.md sem bootstrap: true: %s", conteudo)
	}
}

func TestPastaCanonica_PathCustom(t *testing.T) {
	home, _ := injetarHomeEConfig(t)
	stdinReader = strings.NewReader("~/work/koine\n")
	resultado, err := configurarPastaCanonica(koine.VaultFS, true)
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	pastaEsperada := filepath.Join(home, "work", "koine")
	if resultado != pastaEsperada {
		t.Errorf("pasta = %q, want %q", resultado, pastaEsperada)
	}
}

func TestPastaCanonica_NaoInterativo_AceitaDefault(t *testing.T) {
	home, _ := injetarHomeEConfig(t)
	resultado, err := configurarPastaCanonica(koine.VaultFS, false)
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	pastaEsperada := filepath.Join(home, "koine")
	if resultado != pastaEsperada {
		t.Errorf("pasta = %q, want %q", resultado, pastaEsperada)
	}
}

func TestPastaCanonica_CtxIdenticoEmbedu_Idempotente(t *testing.T) {
	injetarHomeEConfig(t)
	stdinReader = strings.NewReader("\n")
	if _, err := configurarPastaCanonica(koine.VaultFS, true); err != nil {
		t.Fatal(err)
	}
	stdinReader = strings.NewReader("\n")
	if _, err := configurarPastaCanonica(koine.VaultFS, true); err != nil {
		t.Fatalf("segunda chamada deveria ser silenciosa: %v", err)
	}
}

func TestPastaCanonica_CtxPersonalizado_PreservaPorPadrao(t *testing.T) {
	home, _ := injetarHomeEConfig(t)
	pasta := filepath.Join(home, "koine")
	if err := os.MkdirAll(pasta, 0o755); err != nil {
		t.Fatal(err)
	}
	ctx := filepath.Join(pasta, "CONTEXTO.md")
	conteudoPersonalizado := "---\nescopo: meu-escopo\ndominios: [universal]\n---\n"
	if err := os.WriteFile(ctx, []byte(conteudoPersonalizado), 0o644); err != nil {
		t.Fatal(err)
	}

	stdinReader = strings.NewReader("\n\n") // path default + Enter (recusa sobrescrita)
	if _, err := configurarPastaCanonica(koine.VaultFS, true); err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	conteudoAtual, _ := os.ReadFile(ctx)
	if string(conteudoAtual) != conteudoPersonalizado {
		t.Errorf("conteúdo personalizado foi sobrescrito! atual: %s", conteudoAtual)
	}
}

func TestPastaCanonica_RegistraAlias(t *testing.T) {
	_, configDir := injetarHomeEConfig(t)
	stdinReader = strings.NewReader("\n")
	if _, err := configurarPastaCanonica(koine.VaultFS, true); err != nil {
		t.Fatal(err)
	}
	aliasesPath := filepath.Join(configDir, "aliases.json")
	data, err := os.ReadFile(aliasesPath)
	if err != nil {
		t.Fatalf("aliases.json não criado: %v", err)
	}
	if !strings.Contains(string(data), `"koine"`) {
		t.Errorf("alias 'koine' ausente: %s", data)
	}
}

func TestPastaCanonica_AliasConflitoOutroPath_AvisaEMantem(t *testing.T) {
	_, configDir := injetarHomeEConfig(t)

	preExistente := `{"pastas":{"koine":{"path":"/algum/outro/path","from":"abs"}}}`
	if err := os.WriteFile(filepath.Join(configDir, "aliases.json"), []byte(preExistente), 0o644); err != nil {
		t.Fatal(err)
	}

	stdinReader = strings.NewReader("\n")
	var buf bytes.Buffer
	var _ io.Writer = &buf
	stderrWriter = &buf

	if _, err := configurarPastaCanonica(koine.VaultFS, true); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(buf.String(), "alias 'koine' já aponta") {
		t.Errorf("warning ausente: %s", buf.String())
	}
	data, _ := os.ReadFile(filepath.Join(configDir, "aliases.json"))
	if !strings.Contains(string(data), "/algum/outro/path") {
		t.Errorf("alias antigo foi sobrescrito: %s", data)
	}
}
