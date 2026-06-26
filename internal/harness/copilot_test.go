package harness

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/jrunic/koine/internal/cache"
)

func TestCopilotRenderizaNormal(t *testing.T) {
	tmpDir := t.TempDir()

	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "cache", "koine") })
	defer cache.SetLookupCacheDir(origCache)

	usuarioPath := filepath.Join(tmpDir, "walter.md")
	os.WriteFile(usuarioPath, []byte("---\nid: 1\n---\n# Walter\nPerfil."), 0o644)

	agentePath := filepath.Join(tmpDir, "hermes.md")
	os.WriteFile(agentePath, []byte("---\nid: 2\n---\n# Hermes\nAgente."), 0o644)

	escopoPath := filepath.Join(tmpDir, "escopo.md")
	os.WriteFile(escopoPath, []byte("---\nid: 3\n---\n# Meu Negocio\nEscopo."), 0o644)

	indicePath := filepath.Join(tmpDir, "kn-indice-universal.md")
	os.WriteFile(indicePath, []byte("---\nid: 4\n---\n# Índice Universal\nEntradas."), 0o644)

	pastaAbs := filepath.Join(tmpDir, "workspace")
	os.MkdirAll(pastaAbs, 0o755)

	cp := &Copilot{Agente: "hermes", PastaAbs: pastaAbs}
	dados := ContextoMontado{
		UsuarioPath:  usuarioPath,
		AgentePath:   agentePath,
		EscopoPath:   escopoPath,
		IndicePaths:  []string{indicePath},
		ContextoPath: filepath.Join(pastaAbs, "CONTEXTO.md"),
	}

	lancamento, err := cp.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar: %v", err)
	}

	slotID := cache.SlotID(pastaAbs)
	bundleDir := cache.CaminhoBundle("copilot-bundles", slotID)

	// AGENTS.md
	agentsPath := filepath.Join(bundleDir, "AGENTS.md")
	agentsMD, ok := lancamento.ArquivosExternos[agentsPath]
	if !ok {
		t.Fatalf("AGENTS.md ausente; keys: %v", keysOfExternal(lancamento.ArquivosExternos))
	}
	s := string(agentsMD)
	for _, want := range []string{"# Sessão Koine — Copilot", "## Usuário", "## Walter", "## Agente", "## Hermes"} {
		if !strings.Contains(s, want) {
			t.Errorf("AGENTS.md não contém %q\n--- output ---\n%s", want, s)
		}
	}

	// escopo.instructions.md
	escopoInstrPath := filepath.Join(bundleDir, ".github", "instructions", "escopo.instructions.md")
	escopoInstr, ok := lancamento.ArquivosExternos[escopoInstrPath]
	if !ok {
		t.Fatal("escopo.instructions.md ausente")
	}
	if !strings.HasPrefix(string(escopoInstr), "---\napplyTo: \"**\"") {
		t.Errorf("escopo.instructions.md não tem frontmatter Copilot:\n%s", string(escopoInstr))
	}

	// kn-indice-universal.instructions.md
	indiceInstrPath := filepath.Join(bundleDir, ".github", "instructions", "kn-indice-universal.instructions.md")
	if _, ok := lancamento.ArquivosExternos[indiceInstrPath]; !ok {
		t.Fatal("kn-indice-universal.instructions.md ausente")
	}

	// symlink
	linkPath := filepath.Join(pastaAbs, ".github", "copilot-instructions.md")
	alvo, ok := lancamento.Symlinks[linkPath]
	if !ok {
		t.Fatal("symlink ausente em Lancamento.Symlinks")
	}
	if alvo != dados.ContextoPath {
		t.Errorf("alvo do symlink = %q, want %q", alvo, dados.ContextoPath)
	}

	// env var
	if lancamento.EnvVars["COPILOT_CUSTOM_INSTRUCTIONS_DIRS"] != bundleDir {
		t.Errorf("COPILOT_CUSTOM_INSTRUCTIONS_DIRS = %q, want %q",
			lancamento.EnvVars["COPILOT_CUSTOM_INSTRUCTIONS_DIRS"], bundleDir)
	}

	// ArquivosNoWorkingDir deve estar vazio
	if len(lancamento.ArquivosNoWorkingDir) != 0 {
		t.Error("ArquivosNoWorkingDir deve estar vazio para Copilot")
	}
}

func TestCopilotRenderizaBootstrap(t *testing.T) {
	tmpDir := t.TempDir()

	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "cache", "koine") })
	defer cache.SetLookupCacheDir(origCache)

	agentePath := filepath.Join(tmpDir, "hermes.md")
	os.WriteFile(agentePath, []byte("---\nid: 2\n---\n# Hermes\nAgente Koine."), 0o644)

	pastaAbs := filepath.Join(tmpDir, "bootstrap-workspace")
	os.MkdirAll(pastaAbs, 0o755)

	cp := &Copilot{Agente: "hermes", PastaAbs: pastaAbs}
	dados := ContextoMontado{
		Bootstrap:  true,
		AgentePath: agentePath,
		// UsuarioPath vazio — sem ficha cadastral
	}

	lancamento, err := cp.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar bootstrap: %v", err)
	}

	slotID := cache.SlotID(pastaAbs)
	bundleDir := cache.CaminhoBundle("copilot-bundles", slotID)
	agentsPath := filepath.Join(bundleDir, "AGENTS.md")

	agentsMD, ok := lancamento.ArquivosExternos[agentsPath]
	if !ok {
		t.Fatal("AGENTS.md ausente em bootstrap")
	}
	s := string(agentsMD)
	if strings.Contains(s, "## Usuário") {
		t.Error("bootstrap sem UsuarioPath não deve conter seção Usuário")
	}
	if !strings.Contains(s, "## Hermes") {
		t.Error("bootstrap deve conter seção Hermes")
	}

	// sem symlink no bootstrap
	if len(lancamento.Symlinks) != 0 {
		t.Errorf("bootstrap não deve ter symlinks, got %v", lancamento.Symlinks)
	}

	// env var obrigatória mesmo no bootstrap
	if lancamento.EnvVars["COPILOT_CUSTOM_INSTRUCTIONS_DIRS"] == "" {
		t.Error("COPILOT_CUSTOM_INSTRUCTIONS_DIRS deve estar setado no bootstrap")
	}

	// apenas AGENTS.md em ArquivosExternos
	if len(lancamento.ArquivosExternos) != 1 {
		t.Errorf("bootstrap deve ter apenas AGENTS.md, got %d entradas", len(lancamento.ArquivosExternos))
	}
}

func TestCopilotNomeECaminho(t *testing.T) {
	cp := &Copilot{}
	if cp.Nome() != "copilot" {
		t.Errorf("Nome = %q, want copilot", cp.Nome())
	}
	got := cp.CaminhoArquivoContexto("/foo")
	want := "/foo/.github/copilot-instructions.md"
	if got != want {
		t.Errorf("CaminhoArquivoContexto = %q, want %q", got, want)
	}
}

func keysOfExternal(m map[string][]byte) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}
