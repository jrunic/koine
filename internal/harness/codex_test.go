package harness

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestCodexRenderizaNormal(t *testing.T) {
	tmpDir := t.TempDir()

	usuarioPath := filepath.Join(tmpDir, "walter.md")
	os.WriteFile(usuarioPath, []byte("---\nid: 1\n---\n# Walter\nPerfil do Walter."), 0o644)

	koinePath := filepath.Join(tmpDir, "KOINE.md")
	os.WriteFile(koinePath, []byte("---\nid: 9\n---\n# Koine\nSobre o Koine."), 0o644)

	agentePath := filepath.Join(tmpDir, "hermes.md")
	os.WriteFile(agentePath, []byte("---\nid: 2\n---\n# Hermes\nAgente Hermes."), 0o644)

	escopoPath := filepath.Join(tmpDir, "escopo.md")
	os.WriteFile(escopoPath, []byte("---\nid: 3\n---\n# Meu Negocio\nEscopo do negocio."), 0o644)

	indicePath := filepath.Join(tmpDir, "kn-indice-universal.md")
	os.WriteFile(indicePath, []byte("---\nid: 4\n---\n# Indice Universal\nEntradas universais."), 0o644)

	pastaAbs := filepath.Join(tmpDir, "workspace")
	os.MkdirAll(pastaAbs, 0o755)
	contextoPath := filepath.Join(pastaAbs, "CONTEXTO.md")
	os.WriteFile(contextoPath, []byte("---\nid: 5\n---\n# Contexto\nProjeto X em andamento."), 0o644)

	cx := &Codex{Agente: "hermes"}
	dados := ContextoMontado{
		UsuarioPath:  usuarioPath,
		KoineMDPath:  koinePath,
		AgentePath:   agentePath,
		EscopoPath:   escopoPath,
		IndicePaths:  []string{indicePath},
		ContextoPath: contextoPath,
	}

	lancamento, err := cx.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar: %v", err)
	}

	conteudo, ok := lancamento.ArquivosNoWorkingDir["AGENTS.md"]
	if !ok {
		t.Fatal("Lancamento não contém AGENTS.md em ArquivosNoWorkingDir")
	}
	s := string(conteudo)

	// MarkerKoine na primeira linha
	if !strings.HasPrefix(s, MarkerKoine+"\n") {
		t.Errorf("AGENTS.md não começa com MarkerKoine:\n%s", s[:80])
	}

	// Conteúdo inline (não paths) de cada seção
	for _, want := range []string{
		"## Usuário", "Perfil do Walter.",
		"## Koine", "Sobre o Koine.",
		"## Agente", "Agente Hermes.",
		"## Escopo", "Escopo do negocio.",
		"Entradas universais.",
		"Projeto X em andamento.", // snapshot do CONTEXTO
		"./CONTEXTO.md",           // prosa apontando o arquivo mutável
		"kn-codex hermes",         // instrução de regeneração
	} {
		if !strings.Contains(s, want) {
			t.Errorf("AGENTS.md não contém %q\n--- output ---\n%s", want, s)
		}
	}

	// Paths NÃO devem vazar (é inline, não @path)
	if strings.Contains(s, "@"+usuarioPath) || strings.Contains(s, usuarioPath) {
		t.Errorf("AGENTS.md vazou path do usuário (deveria ser inline):\n%s", s)
	}

	// ExtraArgs com a flag de limite
	if got := strings.Join(lancamento.ExtraArgs, " "); !strings.Contains(got, "-c project_doc_max_bytes=1048576") {
		t.Errorf("ExtraArgs sem flag de limite: %v", lancamento.ExtraArgs)
	}

	// Categorias não usadas vazias
	if len(lancamento.ArquivosExternos) != 0 {
		t.Error("ArquivosExternos deve estar vazio para Codex")
	}
	if len(lancamento.EnvVars) != 0 {
		t.Error("EnvVars deve estar vazio para Codex")
	}
	if len(lancamento.Symlinks) != 0 {
		t.Error("Symlinks deve estar vazio para Codex")
	}
}
