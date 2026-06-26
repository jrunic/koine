package harness

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/jrunic/koine/internal/cache"
)

// keysOfExternal reutilizada de copilot_test.go (mesmo pacote)

func TestOpenCodeRenderizaNormal(t *testing.T) {
	tmpDir := t.TempDir()

	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "cache", "koine") })
	defer cache.SetLookupCacheDir(origCache)

	// mock stat global → não existe (sem aviso)
	origStat := ExportLookupStatOpenCodeGlobal()
	SetLookupStatOpenCodeGlobal(func(string) (os.FileInfo, error) { return nil, os.ErrNotExist })
	defer SetLookupStatOpenCodeGlobal(origStat)

	usuarioPath := filepath.Join(tmpDir, "walter.md")
	agentePath := filepath.Join(tmpDir, "hermes.md")
	escopoPath := filepath.Join(tmpDir, "escopo.md")
	indicePath := filepath.Join(tmpDir, "kn-indice-universal.md")
	contextoPath := filepath.Join(tmpDir, "workspace", "CONTEXTO.md")
	pastaAbs := filepath.Join(tmpDir, "workspace")
	os.MkdirAll(pastaAbs, 0o755)

	oc := &OpenCode{Agente: "hermes", PastaAbs: pastaAbs}
	dados := ContextoMontado{
		UsuarioPath:  usuarioPath,
		AgentePath:   agentePath,
		EscopoPath:   escopoPath,
		IndicePaths:  []string{indicePath},
		ContextoPath: contextoPath,
	}

	lancamento, err := oc.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar: %v", err)
	}

	slotID := cache.SlotID(pastaAbs)
	configPath := cache.CaminhoArquivo("opencode-configs", slotID, "json")

	// ArquivosExternos deve conter o JSON
	data, ok := lancamento.ArquivosExternos[configPath]
	if !ok {
		t.Fatalf("config JSON ausente; keys: %v", keysOfExternal(lancamento.ArquivosExternos))
	}

	var cfg openCodeConfig
	if err := json.Unmarshal(data, &cfg); err != nil {
		t.Fatalf("JSON inválido: %v\n%s", err, string(data))
	}
	if cfg.Schema != "https://opencode.ai/config.json" {
		t.Errorf("$schema = %q, want https://opencode.ai/config.json", cfg.Schema)
	}
	// instructions: usuario, agente, escopo, indice (nessa ordem)
	wantInstructions := []string{usuarioPath, agentePath, escopoPath, indicePath}
	if len(cfg.Instructions) != len(wantInstructions) {
		t.Fatalf("instructions len = %d, want %d: %v", len(cfg.Instructions), len(wantInstructions), cfg.Instructions)
	}
	for i, want := range wantInstructions {
		if cfg.Instructions[i] != want {
			t.Errorf("instructions[%d] = %q, want %q", i, cfg.Instructions[i], want)
		}
	}

	// EnvVars
	if lancamento.EnvVars["OPENCODE_CONFIG"] != configPath {
		t.Errorf("OPENCODE_CONFIG = %q, want %q", lancamento.EnvVars["OPENCODE_CONFIG"], configPath)
	}
	if lancamento.EnvVars["OPENCODE_DISABLE_CLAUDE_CODE"] != "1" {
		t.Error("OPENCODE_DISABLE_CLAUDE_CODE deve ser \"1\"")
	}

	// Symlinks: <pasta>/AGENTS.md → <pasta>/CONTEXTO.md
	linkPath := filepath.Join(pastaAbs, "AGENTS.md")
	alvo, ok := lancamento.Symlinks[linkPath]
	if !ok {
		t.Fatal("symlink AGENTS.md ausente")
	}
	if alvo != contextoPath {
		t.Errorf("alvo symlink = %q, want %q", alvo, contextoPath)
	}

	// ArquivosNoWorkingDir deve estar vazio
	if len(lancamento.ArquivosNoWorkingDir) != 0 {
		t.Error("ArquivosNoWorkingDir deve estar vazio para OpenCode")
	}
}

func TestOpenCodeRenderizaBootstrap(t *testing.T) {
	tmpDir := t.TempDir()

	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "cache", "koine") })
	defer cache.SetLookupCacheDir(origCache)

	origStat := ExportLookupStatOpenCodeGlobal()
	SetLookupStatOpenCodeGlobal(func(string) (os.FileInfo, error) { return nil, os.ErrNotExist })
	defer SetLookupStatOpenCodeGlobal(origStat)

	agentePath := filepath.Join(tmpDir, "hermes.md")
	pastaAbs := filepath.Join(tmpDir, "bootstrap-workspace")
	os.MkdirAll(pastaAbs, 0o755)

	oc := &OpenCode{Agente: "hermes", PastaAbs: pastaAbs}
	dados := ContextoMontado{
		Bootstrap:  true,
		AgentePath: agentePath,
		// UsuarioPath vazio
	}

	lancamento, err := oc.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar bootstrap: %v", err)
	}

	// apenas um arquivo externo (JSON)
	if len(lancamento.ArquivosExternos) != 1 {
		t.Errorf("bootstrap deve ter apenas config JSON, got %d entradas", len(lancamento.ArquivosExternos))
	}

	// JSON deve conter apenas agentePath (sem UsuarioPath)
	for _, data := range lancamento.ArquivosExternos {
		var cfg openCodeConfig
		if err := json.Unmarshal(data, &cfg); err != nil {
			t.Fatalf("JSON inválido: %v", err)
		}
		for _, instr := range cfg.Instructions {
			if strings.Contains(instr, "walter") {
				t.Errorf("bootstrap sem UsuarioPath não deve incluir usuario nas instructions")
			}
		}
		found := false
		for _, instr := range cfg.Instructions {
			if instr == agentePath {
				found = true
			}
		}
		if !found {
			t.Errorf("instructions deve conter agentePath=%q: %v", agentePath, cfg.Instructions)
		}
	}

	// bootstrap: sem symlink
	if len(lancamento.Symlinks) != 0 {
		t.Errorf("bootstrap não deve ter symlinks, got %v", lancamento.Symlinks)
	}

	// env vars obrigatórias
	if lancamento.EnvVars["OPENCODE_CONFIG"] == "" {
		t.Error("OPENCODE_CONFIG deve estar setado no bootstrap")
	}
	if lancamento.EnvVars["OPENCODE_DISABLE_CLAUDE_CODE"] != "1" {
		t.Error("OPENCODE_DISABLE_CLAUDE_CODE deve ser \"1\" no bootstrap")
	}
}

func TestOpenCodeRenderizaAvisoGlobal(t *testing.T) {
	tmpDir := t.TempDir()

	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "cache", "koine") })
	defer cache.SetLookupCacheDir(origCache)

	// simula que ~/.config/opencode/AGENTS.md existe
	origStat := ExportLookupStatOpenCodeGlobal()
	SetLookupStatOpenCodeGlobal(func(string) (os.FileInfo, error) { return nil, nil })
	defer SetLookupStatOpenCodeGlobal(origStat)

	pastaAbs := filepath.Join(tmpDir, "workspace")
	os.MkdirAll(pastaAbs, 0o755)

	oc := &OpenCode{Agente: "hermes", PastaAbs: pastaAbs}
	dados := ContextoMontado{
		Bootstrap:  true,
		AgentePath: filepath.Join(tmpDir, "hermes.md"),
	}

	// deve executar sem erro (aviso vai para stderr, não é erro)
	_, err := oc.Renderizar(dados)
	if err != nil {
		t.Fatalf("Renderizar com global config: %v", err)
	}
}

func TestOpenCodeNomeECaminho(t *testing.T) {
	oc := &OpenCode{}
	if oc.Nome() != "opencode" {
		t.Errorf("Nome = %q, want opencode", oc.Nome())
	}
	got := oc.CaminhoArquivoContexto("/foo")
	want := "/foo/AGENTS.md"
	if got != want {
		t.Errorf("CaminhoArquivoContexto = %q, want %q", got, want)
	}
}
