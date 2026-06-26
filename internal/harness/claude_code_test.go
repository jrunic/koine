package harness

import (
	"strings"
	"testing"
	"testing/fstest"
)

func TestClaudeCodeRenderiza(t *testing.T) {
	fakeFS := fstest.MapFS{
		"vault/templates/claude.md.tmpl": {
			Data: []byte("# CLAUDE.md\n*Gerado em {{.Timestamp}}. Regerar: `kn-agente {{.Agente}} .`*\n\n@{{.UsuarioPath}}\n@{{.KoineMDPath}}\n@{{.AgentePath}}\n@{{.EscopoPath}}\n{{range .IndicePaths}}@{{.}}\n{{end}}@{{.ContextoPath}}\n"),
		},
	}

	cc := &ClaudeCode{VaultFS: fakeFS, Agente: "hermes"}

	dados := ContextoMontado{
		UsuarioPath:  "/home/walter/.config/koine/walter.md",
		KoineMDPath:  "/home/walter/.local/share/koine/KOINE.md",
		AgentePath:   "/home/walter/.local/share/koine/agentes/hermes.md",
		EscopoPath:   "/home/walter/.config/koine/escopos/meu-negocio.md",
		IndicePaths:  []string{"/home/walter/koine/teste/kn-indice-pessoas.md"},
		ContextoPath: "/home/walter/trabalho/CONTEXTO.md",
	}

	lancamento, err := cc.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar: %v", err)
	}
	s := string(lancamento.ArquivosNoWorkingDir["CLAUDE.md"])

	if !strings.HasPrefix(s, MarkerKoine) {
		t.Errorf("CLAUDE.md deve começar com MarkerKoine\n--- output ---\n%s", s)
	}

	checks := []string{
		"@/home/walter/.config/koine/walter.md",
		"@/home/walter/.local/share/koine/KOINE.md",
		"@/home/walter/.local/share/koine/agentes/hermes.md",
		"@/home/walter/.config/koine/escopos/meu-negocio.md",
		"@/home/walter/koine/teste/kn-indice-pessoas.md",
		"@/home/walter/trabalho/CONTEXTO.md",
		"kn-agente hermes .",
	}
	for _, want := range checks {
		if !strings.Contains(s, want) {
			t.Errorf("output não contém %q\n--- output ---\n%s", want, s)
		}
	}

	// verifica ordem: agente antes de escopo, escopo antes de índices
	posAgente := strings.Index(s, "@/home/walter/.local/share/koine/agentes/hermes.md")
	posEscopo := strings.Index(s, "@/home/walter/.config/koine/escopos/meu-negocio.md")
	posIndice := strings.Index(s, "@/home/walter/koine/teste/kn-indice-pessoas.md")
	if posAgente >= posEscopo || posEscopo >= posIndice {
		t.Errorf("ordem incorreta no CLAUDE.md — esperado agente < escopo < índices\n--- output ---\n%s", s)
	}
	if strings.Contains(s, "/dominios/") {
		t.Errorf("CLAUDE.md não deve referenciar /dominios/ diretamente — framework é embutido no kn-indice\n--- output ---\n%s", s)
	}
}

func TestRenderizarBootstrapGeraCLAUDEMD(t *testing.T) {
	fakeFS := fstest.MapFS{
		"vault/templates/claude-bootstrap.md.tmpl": {
			Data: []byte("# CLAUDE.md\n*bootstrap — Não editar.*\n\n> Crie CONTEXTO.md com /kn-02-mantem-catalogo.\n\n{{if .UsuarioPath}}@{{.UsuarioPath}}\n{{end}}@{{.KoineMDPath}}\n@{{.AgentePath}}\n"),
		},
	}

	cc := &ClaudeCode{VaultFS: fakeFS, Agente: "hermes"}

	dados := ContextoMontado{
		Bootstrap:   true,
		UsuarioPath: "/home/walter/.config/koine/walter.md",
		KoineMDPath: "/home/walter/.local/share/koine/KOINE.md",
		AgentePath:  "/home/walter/.local/share/koine/agentes/hermes.md",
	}

	lancamento, err := cc.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar (bootstrap): %v", err)
	}
	s := string(lancamento.ArquivosNoWorkingDir["CLAUDE.md"])

	for _, want := range []string{
		"@/home/walter/.config/koine/walter.md",
		"@/home/walter/.local/share/koine/KOINE.md",
		"@/home/walter/.local/share/koine/agentes/hermes.md",
		"kn-02-mantem-catalogo",
	} {
		if !strings.Contains(s, want) {
			t.Errorf("bootstrap output não contém %q\n--- output ---\n%s", want, s)
		}
	}

	// não deve conter @-includes de escopo, índices ou CONTEXTO.md
	for _, notWant := range []string{"@/home/walter/.config/koine/escopos", "kn-indice-", "@/home/walter/trabalho/CONTEXTO.md"} {
		if strings.Contains(s, notWant) {
			t.Errorf("bootstrap output não deve conter %q\n--- output ---\n%s", notWant, s)
		}
	}
}

func TestRenderizarBootstrapSemUsuario(t *testing.T) {
	fakeFS := fstest.MapFS{
		"vault/templates/claude-bootstrap.md.tmpl": {
			Data: []byte("{{if .UsuarioPath}}@{{.UsuarioPath}}\n{{end}}@{{.KoineMDPath}}\n@{{.AgentePath}}\n"),
		},
	}

	cc := &ClaudeCode{VaultFS: fakeFS, Agente: "hermes"}

	dados := ContextoMontado{
		Bootstrap:   true,
		KoineMDPath: "/vault/KOINE.md",
		AgentePath:  "/vault/agentes/hermes.md",
	}

	lancamento, err := cc.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar (bootstrap sem usuario): %v", err)
	}
	s := string(lancamento.ArquivosNoWorkingDir["CLAUDE.md"])

	if strings.Contains(s, "@\n") || strings.HasPrefix(s, "@\n") {
		t.Errorf("output não deve conter linha '@' isolada sem path\n--- output ---\n%s", s)
	}
	if !strings.Contains(s, "@/vault/KOINE.md") {
		t.Errorf("output deve conter @KoineMDPath\n--- output ---\n%s", s)
	}
}

func TestClaudeCodeNomeECaminho(t *testing.T) {
	cc := &ClaudeCode{}
	if cc.Nome() != "claude-code" {
		t.Errorf("Nome = %q, want claude-code", cc.Nome())
	}
	if got := cc.CaminhoArquivoContexto("/foo"); got != "/foo/CLAUDE.md" {
		t.Errorf("CaminhoArquivoContexto = %q, want /foo/CLAUDE.md", got)
	}
}
