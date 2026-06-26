package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/jrunic/koine/internal/harness"
)

func TestParseSubstituir(t *testing.T) {
	filtered, ok := parseSubstituir([]string{"hermes", "/pasta", "--substituir"})
	if !ok {
		t.Fatal("--substituir não detectado")
	}
	if len(filtered) != 2 || filtered[0] != "hermes" || filtered[1] != "/pasta" {
		t.Errorf("args filtrados = %v, want [hermes /pasta]", filtered)
	}

	filtered2, ok2 := parseSubstituir([]string{"hermes", "/pasta"})
	if ok2 {
		t.Error("--substituir não deve ser detectado sem a flag")
	}
	if len(filtered2) != 2 {
		t.Errorf("sem flag: args = %v, want [hermes /pasta]", filtered2)
	}
}

func TestVerificarConflitosArquivoNaoExiste(t *testing.T) {
	dir := t.TempDir()
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("conteudo")},
	}
	if err := verificarConflitos(lancamento, dir); err != nil {
		t.Fatalf("arquivo ausente não deve gerar conflito: %v", err)
	}
}

func TestVerificarConflitosArquivoComMarker(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "CLAUDE.md"),
		[]byte(harness.MarkerKoine+"\n# CLAUDE.md antigo\n"), 0o644)
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("novo conteudo")},
	}
	if err := verificarConflitos(lancamento, dir); err != nil {
		t.Fatalf("arquivo com marker deve ser OK (regeneração idempotente): %v", err)
	}
}

func TestVerificarConflitosArquivoSemMarker(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "CLAUDE.md"),
		[]byte("# Arquivo Manual\nSem marker Koine."), 0o644)
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("conteudo")},
	}
	err := verificarConflitos(lancamento, dir)
	if err == nil {
		t.Fatal("arquivo sem marker deve gerar conflito")
	}
	if !strings.Contains(err.Error(), "--substituir") {
		t.Errorf("mensagem de erro deve mencionar --substituir: %v", err)
	}
}

func TestVerificarConflitosSymlinkCorreto(t *testing.T) {
	dir := t.TempDir()
	linkPath := filepath.Join(dir, "AGENTS.md")
	alvo := filepath.Join(dir, "CONTEXTO.md")
	os.Symlink(alvo, linkPath)
	lancamento := harness.Lancamento{
		Symlinks: map[string]string{linkPath: alvo},
	}
	if err := verificarConflitos(lancamento, dir); err != nil {
		t.Fatalf("symlink correto deve ser OK: %v", err)
	}
}

func TestVerificarConflitosSymlinkComAlvoDiferente(t *testing.T) {
	dir := t.TempDir()
	linkPath := filepath.Join(dir, "AGENTS.md")
	os.Symlink("/outro/alvo", linkPath)
	lancamento := harness.Lancamento{
		Symlinks: map[string]string{linkPath: filepath.Join(dir, "CONTEXTO.md")},
	}
	err := verificarConflitos(lancamento, dir)
	if err == nil {
		t.Fatal("symlink com alvo diferente deve retornar conflito")
	}
	if !strings.Contains(err.Error(), "--substituir") {
		t.Errorf("mensagem deve mencionar --substituir: %v", err)
	}
}

func TestVerificarConflitosArquivoNoLugarDeSymlink(t *testing.T) {
	dir := t.TempDir()
	linkPath := filepath.Join(dir, "AGENTS.md")
	os.WriteFile(linkPath, []byte("arquivo manual sem marker"), 0o644)
	lancamento := harness.Lancamento{
		Symlinks: map[string]string{linkPath: filepath.Join(dir, "CONTEXTO.md")},
	}
	err := verificarConflitos(lancamento, dir)
	if err == nil {
		t.Fatal("arquivo regular onde symlink esperado deve ser conflito")
	}
}
