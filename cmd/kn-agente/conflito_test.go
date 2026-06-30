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

func TestResolverConflitosArquivoNaoExiste(t *testing.T) {
	dir := t.TempDir()
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("conteudo")},
	}
	if err := resolverConflitos(lancamento, dir); err != nil {
		t.Fatalf("arquivo ausente não deve gerar conflito: %v", err)
	}
}

func TestResolverConflitosArquivoComMarker(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "CLAUDE.md"),
		[]byte(harness.MarkerKoine+"\n# CLAUDE.md antigo\n"), 0o644)
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("novo conteudo")},
	}
	if err := resolverConflitos(lancamento, dir); err != nil {
		t.Fatalf("arquivo com marker deve ser OK (regeneração idempotente): %v", err)
	}
	// arquivo com marker NÃO deve gerar backup
	if _, err := os.Lstat(filepath.Join(dir, "CLAUDE.md.bak")); !os.IsNotExist(err) {
		t.Error("arquivo com marker não deveria ter sido copiado para .bak")
	}
}

func TestResolverConflitosArquivoSemMarkerFazBackup(t *testing.T) {
	dir := t.TempDir()
	original := []byte("# Arquivo Manual\nSem marker Koine.")
	os.WriteFile(filepath.Join(dir, "CLAUDE.md"), original, 0o644)
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("conteudo")},
	}
	if err := resolverConflitos(lancamento, dir); err != nil {
		t.Fatalf("arquivo sem marker deve ser resolvido com backup, não erro: %v", err)
	}
	// o arquivo original foi preservado em .bak com o conteúdo intacto
	bak, err := os.ReadFile(filepath.Join(dir, "CLAUDE.md.bak"))
	if err != nil {
		t.Fatalf("backup .bak não foi criado: %v", err)
	}
	if string(bak) != string(original) {
		t.Errorf("conteúdo do backup divergiu: got %q, want %q", bak, original)
	}
	// o path original ficou livre para materialização
	if _, err := os.Lstat(filepath.Join(dir, "CLAUDE.md")); !os.IsNotExist(err) {
		t.Error("CLAUDE.md original deveria ter sido movido para .bak (path livre)")
	}
}

func TestResolverConflitosBackupNumeradoNaoSobrescreve(t *testing.T) {
	dir := t.TempDir()
	os.WriteFile(filepath.Join(dir, "CLAUDE.md"), []byte("novo manual"), 0o644)
	os.WriteFile(filepath.Join(dir, "CLAUDE.md.bak"), []byte("backup antigo"), 0o644)
	lancamento := harness.Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": []byte("conteudo")},
	}
	if err := resolverConflitos(lancamento, dir); err != nil {
		t.Fatalf("esperado backup numerado, não erro: %v", err)
	}
	// .bak antigo intacto
	antigo, _ := os.ReadFile(filepath.Join(dir, "CLAUDE.md.bak"))
	if string(antigo) != "backup antigo" {
		t.Errorf(".bak existente foi sobrescrito: %q", antigo)
	}
	// novo backup foi para .bak.1
	novo, err := os.ReadFile(filepath.Join(dir, "CLAUDE.md.bak.1"))
	if err != nil || string(novo) != "novo manual" {
		t.Errorf("esperado CLAUDE.md.bak.1 com 'novo manual', got %q (err %v)", novo, err)
	}
}

func TestResolverConflitosSymlinkCorreto(t *testing.T) {
	dir := t.TempDir()
	linkPath := filepath.Join(dir, "AGENTS.md")
	alvo := filepath.Join(dir, "CONTEXTO.md")
	os.Symlink(alvo, linkPath)
	lancamento := harness.Lancamento{
		Symlinks: map[string]string{linkPath: alvo},
	}
	if err := resolverConflitos(lancamento, dir); err != nil {
		t.Fatalf("symlink correto deve ser OK: %v", err)
	}
}

func TestResolverConflitosSymlinkComAlvoDiferente(t *testing.T) {
	dir := t.TempDir()
	linkPath := filepath.Join(dir, "AGENTS.md")
	os.Symlink("/outro/alvo", linkPath)
	lancamento := harness.Lancamento{
		Symlinks: map[string]string{linkPath: filepath.Join(dir, "CONTEXTO.md")},
	}
	err := resolverConflitos(lancamento, dir)
	if err == nil {
		t.Fatal("symlink com alvo diferente deve retornar conflito")
	}
	if !strings.Contains(err.Error(), "--substituir") {
		t.Errorf("mensagem deve mencionar --substituir: %v", err)
	}
}

func TestResolverConflitosArquivoNoLugarDeSymlinkFazBackup(t *testing.T) {
	dir := t.TempDir()
	linkPath := filepath.Join(dir, "AGENTS.md")
	os.WriteFile(linkPath, []byte("arquivo manual sem marker"), 0o644)
	lancamento := harness.Lancamento{
		Symlinks: map[string]string{linkPath: filepath.Join(dir, "CONTEXTO.md")},
	}
	if err := resolverConflitos(lancamento, dir); err != nil {
		t.Fatalf("arquivo regular onde symlink esperado deve virar backup, não erro: %v", err)
	}
	bak, err := os.ReadFile(filepath.Join(dir, "AGENTS.md.bak"))
	if err != nil || string(bak) != "arquivo manual sem marker" {
		t.Errorf("esperado AGENTS.md.bak preservando o arquivo original, got %q (err %v)", bak, err)
	}
}
