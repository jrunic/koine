package pasta

import (
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"

	"github.com/jrunic/koine/internal/aliases"
)

func TestResolverVazio(t *testing.T) {
	got, err := Resolver("")
	if err != nil {
		t.Fatalf("Resolver vazio: %v", err)
	}
	wd, _ := os.Getwd()
	if got != wd {
		t.Errorf("Resolver('') = %q, want cwd %q", got, wd)
	}
}

func TestResolverPathDireto(t *testing.T) {
	dir := t.TempDir()
	got, err := Resolver(dir)
	if err != nil {
		t.Fatalf("Resolver path direto: %v", err)
	}
	if got != dir {
		t.Errorf("Resolver(%q) = %q, want %q", dir, got, dir)
	}
}

func TestResolverAlias(t *testing.T) {
	dir := t.TempDir()
	orig := lookupAliases
	lookupAliases = func() (aliases.Aliases, error) {
		return aliases.Aliases{Pastas: map[string]aliases.Entrada{
			"meu-proj": {Path: dir, From: "abs"},
		}}, nil
	}
	defer func() { lookupAliases = orig }()

	got, err := Resolver("meu-proj")
	if err != nil {
		t.Fatalf("Resolver alias: %v", err)
	}
	if got != dir {
		t.Errorf("Resolver('meu-proj') = %q, want %q", got, dir)
	}
}

func TestFuzzyFilter(t *testing.T) {
	candidatos := []string{
		"/home/walter/koine/vida-imagem",
		"/home/walter/koine/market4u",
		"/home/walter/koine/geral",
	}
	got := fuzzyFilter("vida", candidatos)
	if len(got) != 1 || got[0] != candidatos[0] {
		t.Errorf("fuzzyFilter('vida') = %v, want [%s]", got, candidatos[0])
	}
}

func TestFuzzyFilterSemMatch(t *testing.T) {
	candidatos := []string{"/home/walter/koine/geral"}
	got := fuzzyFilter("xyz", candidatos)
	if len(got) != 0 {
		t.Errorf("fuzzyFilter('xyz') = %v, want []", got)
	}
}

func TestFuzzyFilterMultiplasOcorrencias(t *testing.T) {
	candidatos := []string{
		"/home/walter/koine/vida-imagem",
		"/home/walter/koine/vida-diagnostico",
		"/home/walter/koine/geral",
	}
	got := fuzzyFilter("vida", candidatos)
	if len(got) != 2 {
		t.Errorf("fuzzyFilter('vida') = %v, want 2 resultados", got)
	}
}

// withFakeHome injeta lookupHomeDir apontando para um tmp dir.
func withFakeHome(t *testing.T) string {
	t.Helper()
	tmp := t.TempDir()
	orig := lookupHomeDir
	lookupHomeDir = func() (string, error) { return tmp, nil }
	t.Cleanup(func() { lookupHomeDir = orig })
	return tmp
}

// mkdirs cria todas as pastas listadas relativas a base.
func mkdirs(t *testing.T, base string, rels ...string) {
	t.Helper()
	for _, r := range rels {
		if err := os.MkdirAll(filepath.Join(base, r), 0o755); err != nil {
			t.Fatal(err)
		}
	}
}

// asContains verifica se cada path esperado (relativo a base) está em got.
func assertContemRelativos(t *testing.T, got []string, base string, esperados ...string) {
	t.Helper()
	set := make(map[string]bool, len(got))
	for _, g := range got {
		rel, _ := filepath.Rel(base, g)
		set[filepath.ToSlash(rel)] = true
	}
	for _, e := range esperados {
		if !set[e] {
			sorted := make([]string, 0, len(set))
			for k := range set {
				sorted = append(sorted, k)
			}
			sort.Strings(sorted)
			t.Errorf("listarCandidatos sem %q. obtidos: %v", e, sorted)
		}
	}
}

func assertNaoContemRelativos(t *testing.T, got []string, base string, proibidos ...string) {
	t.Helper()
	for _, g := range got {
		rel, _ := filepath.Rel(base, g)
		relSlash := filepath.ToSlash(rel)
		for _, p := range proibidos {
			if relSlash == p || strings.HasPrefix(relSlash, p+"/") {
				t.Errorf("listarCandidatos incluiu pasta proibida %q (esperado pular %q)", relSlash, p)
			}
		}
	}
}

func TestListarCandidatosWalk(t *testing.T) {
	home := withFakeHome(t)

	mkdirs(t, home,
		"pasta-a",
		"pasta-b/sub-pasta",
		"projeto/src",
		"node_modules/pkg",
		".git/objects",
		"Library/Caches",
	)

	got := listarCandidatos()

	assertContemRelativos(t, got, home,
		"pasta-a",
		"pasta-b",
		"pasta-b/sub-pasta",
		"projeto",
		"projeto/src",
	)
	assertNaoContemRelativos(t, got, home,
		"node_modules",
		".git",
		"Library",
	)
}

func TestListarCandidatosLimiteProfundidade(t *testing.T) {
	home := withFakeHome(t)

	// cria pasta a 8 níveis (deve ser pulada — limite é 7)
	depth8 := filepath.Join("l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8")
	// pasta a 7 níveis (deve entrar)
	depth7 := filepath.Join("a1", "a2", "a3", "a4", "a5", "a6", "a7")
	mkdirs(t, home, depth8, depth7)

	got := listarCandidatos()

	// l7 entra; l8 não. Caminho até l7 deve estar; l8 ausente.
	caminhoL7 := filepath.Join("l1", "l2", "l3", "l4", "l5", "l6", "l7")
	assertContemRelativos(t, got, home, caminhoL7, depth7)

	for _, g := range got {
		rel, _ := filepath.Rel(home, g)
		if filepath.ToSlash(rel) == filepath.ToSlash(depth8) {
			t.Errorf("pasta a 8 níveis deveria ser pulada: %q", rel)
		}
	}
}

// TestListarCandidatosDotfiles confere que basenames começando com "."
// são pulados via fs.SkipDir (caminho rápido, sem necessidade de descer).
func TestListarCandidatosDotfiles(t *testing.T) {
	home := withFakeHome(t)
	mkdirs(t, home, ".config/koine", ".ssh", "projeto")

	got := listarCandidatos()

	assertContemRelativos(t, got, home, "projeto")
	assertNaoContemRelativos(t, got, home, ".config", ".ssh")
}

func BenchmarkListarCandidatos(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_ = listarCandidatos()
	}
}
