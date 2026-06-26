package aliases

import (
	"os"
	"path/filepath"
	"testing"
)

// withTmpConfig injeta dir temporário via var-hook (sem os.Setenv).
func withTmpConfig(t *testing.T) func() {
	t.Helper()
	tmp := t.TempDir()
	orig := lookupConfigDir
	lookupConfigDir = func() string { return tmp }
	return func() { lookupConfigDir = orig }
}

func TestCarregarVazio(t *testing.T) {
	restore := withTmpConfig(t)
	defer restore()

	a, err := Carregar()
	if err != nil {
		t.Fatalf("Carregar: %v", err)
	}
	if len(a.Pastas) != 0 {
		t.Errorf("esperava mapa vazio, obteve %v", a.Pastas)
	}
}

func TestSalvarECarregar(t *testing.T) {
	restore := withTmpConfig(t)
	defer restore()

	original := Aliases{Pastas: map[string]Entrada{
		"geral": {Path: "koine/geral", From: "home"},
	}}
	if err := Salvar(original); err != nil {
		t.Fatalf("Salvar: %v", err)
	}
	lido, err := Carregar()
	if err != nil {
		t.Fatalf("Carregar após Salvar: %v", err)
	}
	e, ok := lido.Pastas["geral"]
	if !ok || e.Path != "koine/geral" || e.From != "home" {
		t.Errorf("entrada 'geral' incorreta: %+v", e)
	}
}

func TestResolverHome(t *testing.T) {
	home, _ := os.UserHomeDir()
	a := Aliases{Pastas: map[string]Entrada{
		"proj": {Path: "koine/proj", From: "home"},
	}}
	got, ok := Resolver(a, "proj")
	if !ok {
		t.Fatal("Resolver retornou false para alias existente")
	}
	want := filepath.Join(home, "koine/proj")
	if got != want {
		t.Errorf("Resolver = %q, want %q", got, want)
	}
}

func TestResolverAbs(t *testing.T) {
	a := Aliases{Pastas: map[string]Entrada{
		"abs": {Path: "/tmp/projeto", From: "abs"},
	}}
	got, ok := Resolver(a, "abs")
	if !ok || got != "/tmp/projeto" {
		t.Errorf("Resolver abs = %q, %v", got, ok)
	}
}

func TestResolverNaoEncontrado(t *testing.T) {
	a := Aliases{Pastas: map[string]Entrada{}}
	_, ok := Resolver(a, "nao-existe")
	if ok {
		t.Error("Resolver deveria retornar false para chave inexistente")
	}
}

func TestAdicionar(t *testing.T) {
	restore := withTmpConfig(t)
	defer restore()

	if err := Adicionar("novo", "koine/novo", "home"); err != nil {
		t.Fatalf("Adicionar: %v", err)
	}
	a, _ := Carregar()
	e, ok := a.Pastas["novo"]
	if !ok || e.Path != "koine/novo" || e.From != "home" {
		t.Errorf("entrada 'novo' não persistida: %+v", a.Pastas)
	}
}
