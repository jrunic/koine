package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestMaterializarArquivosExternos(t *testing.T) {
	dir := t.TempDir()

	arquivos := map[string][]byte{
		filepath.Join(dir, "sub", "arquivo.txt"):       []byte("conteudo-a"),
		filepath.Join(dir, "sub", "deep", "outro.txt"): []byte("conteudo-b"),
	}

	if err := materializarArquivosExternos(arquivos); err != nil {
		t.Fatalf("materializarArquivosExternos: %v", err)
	}

	for path, want := range arquivos {
		got, err := os.ReadFile(path)
		if err != nil {
			t.Errorf("arquivo %s não encontrado: %v", path, err)
			continue
		}
		if string(got) != string(want) {
			t.Errorf("arquivo %s: got %q, want %q", path, got, want)
		}
	}
}

func TestCriarSymlinksLancamento(t *testing.T) {
	dir := t.TempDir()

	alvo := filepath.Join(dir, "CONTEXTO.md")
	os.WriteFile(alvo, []byte("conteudo"), 0o644)

	link := filepath.Join(dir, ".github", "copilot-instructions.md")
	symlinks := map[string]string{link: alvo}

	if err := criarSymlinksLancamento(symlinks); err != nil {
		t.Fatalf("criarSymlinksLancamento: %v", err)
	}

	target, err := os.Readlink(link)
	if err != nil {
		t.Fatalf("os.Readlink(%s): %v", link, err)
	}
	if target != alvo {
		t.Errorf("symlink alvo = %q, want %q", target, alvo)
	}
}

func TestCriarSymlinksLancamentoIdempotente(t *testing.T) {
	dir := t.TempDir()

	alvo := filepath.Join(dir, "CONTEXTO.md")
	os.WriteFile(alvo, []byte("conteudo"), 0o644)

	link := filepath.Join(dir, ".github", "copilot-instructions.md")
	symlinks := map[string]string{link: alvo}

	// primeira vez
	if err := criarSymlinksLancamento(symlinks); err != nil {
		t.Fatalf("primeira chamada: %v", err)
	}
	// segunda vez — deve sobrescrever silenciosamente
	if err := criarSymlinksLancamento(symlinks); err != nil {
		t.Fatalf("segunda chamada (idempotente): %v", err)
	}

	target, err := os.Readlink(link)
	if err != nil {
		t.Fatalf("os.Readlink: %v", err)
	}
	if target != alvo {
		t.Errorf("symlink alvo após idempotente = %q, want %q", target, alvo)
	}
}
