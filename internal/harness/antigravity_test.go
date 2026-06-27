package harness

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"testing/fstest"

	koine "github.com/jrunic/koine"
)

func TestAntigravityRenderizaNormal(t *testing.T) {
	fakeFS := fstest.MapFS{
		"vault/templates/gemini.md.tmpl": {
			Data: []byte("# GEMINI.md\n*Regerar: `kn-agy {{.Agente}} .`*\n\n@{{.UsuarioPath}}\n@{{.KoineMDPath}}\n@{{.AgentePath}}\n@{{.EscopoPath}}\n{{range .IndicePaths}}@{{.}}\n{{end}}@{{.ContextoPath}}\n"),
		},
	}

	ag := &Antigravity{VaultFS: fakeFS, Agente: "hermes"}

	dados := ContextoMontado{
		UsuarioPath:  "/home/walter/.config/koine/walter.md",
		KoineMDPath:  "/home/walter/.local/share/koine/KOINE.md",
		AgentePath:   "/home/walter/.local/share/koine/agentes/hermes.md",
		EscopoPath:   "/home/walter/.config/koine/escopos/meu-negocio.md",
		IndicePaths:  []string{"/home/walter/koine/ref/kn-indice-pessoas.md"},
		ContextoPath: "/home/walter/trabalho/CONTEXTO.md",
	}

	lancamento, err := ag.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar: %v", err)
	}

	conteudo, ok := lancamento.ArquivosNoWorkingDir["GEMINI.md"]
	if !ok {
		t.Fatal("Lancamento não contém GEMINI.md em ArquivosNoWorkingDir")
	}
	s := string(conteudo)

	for _, want := range []string{
		"@/home/walter/.config/koine/walter.md",
		"@/home/walter/.local/share/koine/KOINE.md",
		"@/home/walter/.local/share/koine/agentes/hermes.md",
		"@/home/walter/.config/koine/escopos/meu-negocio.md",
		"@/home/walter/koine/ref/kn-indice-pessoas.md",
		"@/home/walter/trabalho/CONTEXTO.md",
		"kn-agy hermes .",
	} {
		if !strings.Contains(s, want) {
			t.Errorf("output não contém %q\n--- output ---\n%s", want, s)
		}
	}

	if len(lancamento.ArquivosExternos) != 0 {
		t.Error("ArquivosExternos deve estar vazio para Antigravity")
	}
	if len(lancamento.EnvVars) != 0 {
		t.Error("EnvVars deve estar vazio para Antigravity")
	}
	if len(lancamento.Symlinks) != 0 {
		t.Error("Symlinks deve estar vazio para Antigravity")
	}
}

func TestAntigravityRenderizaBootstrap(t *testing.T) {
	fakeFS := fstest.MapFS{
		"vault/templates/gemini-bootstrap.md.tmpl": {
			Data: []byte("> Crie CONTEXTO.md com /kn-02-mantem-catalogo.\n\n{{if .UsuarioPath}}@{{.UsuarioPath}}\n{{end}}@{{.KoineMDPath}}\n@{{.AgentePath}}\n"),
		},
	}

	ag := &Antigravity{VaultFS: fakeFS, Agente: "hermes"}

	dados := ContextoMontado{
		Bootstrap:   true,
		UsuarioPath: "/home/walter/.config/koine/walter.md",
		KoineMDPath: "/home/walter/.local/share/koine/KOINE.md",
		AgentePath:  "/home/walter/.local/share/koine/agentes/hermes.md",
	}

	lancamento, err := ag.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar (bootstrap): %v", err)
	}

	conteudo, ok := lancamento.ArquivosNoWorkingDir["GEMINI.md"]
	if !ok {
		t.Fatal("Lancamento não contém GEMINI.md")
	}
	s := string(conteudo)

	if !strings.Contains(s, "@/home/walter/.config/koine/walter.md") {
		t.Errorf("bootstrap deve conter UsuarioPath\n--- output ---\n%s", s)
	}
	if strings.Contains(s, "escopos/") || strings.Contains(s, "kn-indice-") {
		t.Errorf("bootstrap não deve conter escopo/índices\n--- output ---\n%s", s)
	}
}

func TestAntigravity_BootstrapExplicito_IncluiContextoPath(t *testing.T) {
	a := &Antigravity{VaultFS: koine.VaultFS, Agente: "hermes"}
	tmpCtx := filepath.Join(t.TempDir(), "CONTEXTO.md")
	if err := os.WriteFile(tmpCtx, []byte("---\nbootstrap: true\n---\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	dados := ContextoMontado{
		Bootstrap:    true,
		KoineMDPath:  "/vault/KOINE.md",
		AgentePath:   "/vault/agentes/hermes.md",
		ContextoPath: tmpCtx,
	}
	lanc, err := a.Renderizar(dados)
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	saida := string(lanc.ArquivosNoWorkingDir["GEMINI.md"])
	if !strings.Contains(saida, "@"+tmpCtx) {
		t.Errorf("GEMINI.md não contém @%s; saída:\n%s", tmpCtx, saida)
	}
}

func TestAntigravityNomeECaminho(t *testing.T) {
	ag := &Antigravity{}
	if ag.Nome() != "antigravity" {
		t.Errorf("Nome = %q, want antigravity", ag.Nome())
	}
	if got := ag.CaminhoArquivoContexto("/foo"); got != "/foo/GEMINI.md" {
		t.Errorf("CaminhoArquivoContexto = %q, want /foo/GEMINI.md", got)
	}
}
