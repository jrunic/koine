package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/jrunic/koine/internal/cache"
	cfg "github.com/jrunic/koine/internal/config"
	"github.com/jrunic/koine/internal/contexto"
	"github.com/jrunic/koine/internal/harness"
)

func TestClienteDoBinario(t *testing.T) {
	casos := []struct {
		nome    string
		cliente string
		ok      bool
	}{
		{"kn-claude", "claude", true},
		{"kn-agy", "agy", true},
		{"kn-copilot", "copilot", true},
		{"kn-agente", "", false},
		{"kn-opencode", "opencode", true}, // Plano 3 — ativo
		{"kn-codex", "codex", true},
		{"claude", "", false},
		{"kn-desconhecido", "", false},
	}
	for _, tc := range casos {
		got, ok := clienteDoBinario(tc.nome)
		if ok != tc.ok || got != tc.cliente {
			t.Errorf("clienteDoBinario(%q) = (%q, %v), want (%q, %v)",
				tc.nome, got, ok, tc.cliente, tc.ok)
		}
	}
}

func TestRodarWrapper(t *testing.T) {
	dir := t.TempDir()

	// isola de ~/.config/koine real
	tmpCfg := t.TempDir()
	origCfg := cfg.ExportLookupConfigDir()
	cfg.SetLookupConfigDir(func() string { return filepath.Join(tmpCfg, "koine") })
	defer cfg.SetLookupConfigDir(origCfg)

	var calledCliente, calledPasta string
	var calledEnv map[string]string
	var calledArgs []string
	origLancar := lancarCliente
	lancarCliente = func(c, p string, env map[string]string, args []string) error {
		calledCliente = c
		calledPasta = p
		calledEnv = env
		calledArgs = args
		return nil
	}
	defer func() { lancarCliente = origLancar }()

	// dir sem CONTEXTO.md → bootstrap; escreve CLAUDE.md via embed real
	if err := rodarWrapper("claude", []string{"hermes", dir}); err != nil {
		t.Fatalf("rodarWrapper: %v", err)
	}
	if calledCliente != "claude" {
		t.Errorf("lancarCliente cliente = %q, want claude", calledCliente)
	}
	if calledPasta != dir {
		t.Errorf("lancarCliente pasta = %q, want %q", calledPasta, dir)
	}
	_ = calledEnv
	_ = calledArgs

	if _, err := os.Stat(filepath.Join(dir, "CLAUDE.md")); err != nil {
		t.Errorf("CLAUDE.md não encontrado em %s: %v", dir, err)
	}
}

func TestRodarWrapperCopilotBootstrap(t *testing.T) {
	dir := t.TempDir()

	// isola config dir
	tmpCfg := t.TempDir()
	origCfg := cfg.ExportLookupConfigDir()
	cfg.SetLookupConfigDir(func() string { return filepath.Join(tmpCfg, "koine") })
	defer cfg.SetLookupConfigDir(origCfg)

	// vault fake com hermes.md
	tmpVault := t.TempDir()
	os.MkdirAll(filepath.Join(tmpVault, "agentes"), 0o755)
	os.WriteFile(
		filepath.Join(tmpVault, "agentes", "hermes.md"),
		[]byte("---\nid: hermes-test\n---\n# Hermes\nAgente Koine de teste."),
		0o644,
	)
	origVault := contexto.ExportLookupVaultDir()
	contexto.SetLookupVaultDir(func() string { return tmpVault })
	defer contexto.SetLookupVaultDir(origVault)

	// isola cache dir
	tmpCache := t.TempDir()
	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpCache, "koine") })
	defer cache.SetLookupCacheDir(origCache)

	var calledCliente string
	var calledEnv map[string]string
	origLancar := lancarCliente
	lancarCliente = func(c, p string, env map[string]string, args []string) error {
		calledCliente = c
		calledEnv = env
		return nil
	}
	defer func() { lancarCliente = origLancar }()

	// dir sem CONTEXTO.md → bootstrap
	if err := rodarWrapper("copilot", []string{"hermes", dir}); err != nil {
		t.Fatalf("rodarWrapper copilot bootstrap: %v", err)
	}

	if calledCliente != "copilot" {
		t.Errorf("cliente = %q, want copilot", calledCliente)
	}

	bundleDir := calledEnv["COPILOT_CUSTOM_INSTRUCTIONS_DIRS"]
	if bundleDir == "" {
		t.Fatal("COPILOT_CUSTOM_INSTRUCTIONS_DIRS não setado")
	}

	// AGENTS.md deve ter sido materializado em disco
	agentsMD := filepath.Join(bundleDir, "AGENTS.md")
	if _, err := os.Stat(agentsMD); err != nil {
		t.Errorf("AGENTS.md não encontrado em %s: %v", agentsMD, err)
	}

	// bootstrap: sem symlink .github/ na pasta de trabalho
	if _, err := os.Stat(filepath.Join(dir, ".github")); err == nil {
		t.Error("bootstrap não deve criar .github/ na pasta de trabalho")
	}
}

func TestRodarWrapperOpenCodeBootstrap(t *testing.T) {
	dir := t.TempDir()

	tmpCfg := t.TempDir()
	origCfg := cfg.ExportLookupConfigDir()
	cfg.SetLookupConfigDir(func() string { return filepath.Join(tmpCfg, "koine") })
	defer cfg.SetLookupConfigDir(origCfg)

	tmpVault := t.TempDir()
	os.MkdirAll(filepath.Join(tmpVault, "agentes"), 0o755)
	os.WriteFile(
		filepath.Join(tmpVault, "agentes", "hermes.md"),
		[]byte("---\nid: hermes-test\n---\n# Hermes\nAgente Koine de teste."),
		0o644,
	)
	origVault := contexto.ExportLookupVaultDir()
	contexto.SetLookupVaultDir(func() string { return tmpVault })
	defer contexto.SetLookupVaultDir(origVault)

	tmpCache := t.TempDir()
	origCache := cache.ExportLookupCacheDir()
	cache.SetLookupCacheDir(func() string { return filepath.Join(tmpCache, "koine") })
	defer cache.SetLookupCacheDir(origCache)

	// mock stat global OpenCode → não existe
	origStat := harness.ExportLookupStatOpenCodeGlobal()
	harness.SetLookupStatOpenCodeGlobal(func(string) (os.FileInfo, error) {
		return nil, os.ErrNotExist
	})
	defer harness.SetLookupStatOpenCodeGlobal(origStat)

	var calledCliente string
	var calledEnv map[string]string
	origLancar := lancarCliente
	lancarCliente = func(c, p string, env map[string]string, args []string) error {
		calledCliente = c
		calledEnv = env
		return nil
	}
	defer func() { lancarCliente = origLancar }()

	// dir sem CONTEXTO.md → bootstrap
	if err := rodarWrapper("opencode", []string{"hermes", dir}); err != nil {
		t.Fatalf("rodarWrapper opencode bootstrap: %v", err)
	}

	if calledCliente != "opencode" {
		t.Errorf("cliente = %q, want opencode", calledCliente)
	}
	if calledEnv["OPENCODE_CONFIG"] == "" {
		t.Fatal("OPENCODE_CONFIG não setado")
	}
	if calledEnv["OPENCODE_DISABLE_CLAUDE_CODE"] != "1" {
		t.Errorf("OPENCODE_DISABLE_CLAUDE_CODE = %q, want \"1\"", calledEnv["OPENCODE_DISABLE_CLAUDE_CODE"])
	}

	// JSON config deve estar em disco
	configPath := calledEnv["OPENCODE_CONFIG"]
	if _, err := os.Stat(configPath); err != nil {
		t.Errorf("config JSON não encontrado em %s: %v", configPath, err)
	}

	// bootstrap: sem AGENTS.md na pasta de trabalho
	if _, err := os.Stat(filepath.Join(dir, "AGENTS.md")); err == nil {
		t.Error("bootstrap não deve criar AGENTS.md na pasta de trabalho")
	}
}

func TestRodarWrapperCodexBootstrap(t *testing.T) {
	dir := t.TempDir()

	// isola config dir (sem usuário → UsuarioPath vazio em bootstrap)
	tmpCfg := t.TempDir()
	origCfg := cfg.ExportLookupConfigDir()
	cfg.SetLookupConfigDir(func() string { return filepath.Join(tmpCfg, "koine") })
	defer cfg.SetLookupConfigDir(origCfg)

	// vault fake: KOINE.md + hermes.md (Codex inlina ambos no AGENTS.md)
	tmpVault := t.TempDir()
	os.MkdirAll(filepath.Join(tmpVault, "agentes"), 0o755)
	os.WriteFile(
		filepath.Join(tmpVault, "KOINE.md"),
		[]byte("---\nid: koine\n---\n# Koine\nSobre o Koine."),
		0o644,
	)
	os.WriteFile(
		filepath.Join(tmpVault, "agentes", "hermes.md"),
		[]byte("---\nid: hermes-test\n---\n# Hermes\nAgente Koine de teste."),
		0o644,
	)
	origVault := contexto.ExportLookupVaultDir()
	contexto.SetLookupVaultDir(func() string { return tmpVault })
	defer contexto.SetLookupVaultDir(origVault)

	var calledCliente string
	var calledArgs []string
	origLancar := lancarCliente
	lancarCliente = func(c, p string, env map[string]string, args []string) error {
		calledCliente = c
		calledArgs = args
		return nil
	}
	defer func() { lancarCliente = origLancar }()

	// dir sem CONTEXTO.md → bootstrap
	if err := rodarWrapper("codex", []string{"hermes", dir}); err != nil {
		t.Fatalf("rodarWrapper codex bootstrap: %v", err)
	}

	if calledCliente != "codex" {
		t.Errorf("cliente = %q, want codex", calledCliente)
	}

	// AGENTS.md materializado NO working dir (inline, não bundle de cache), com marker
	agentsPath := filepath.Join(dir, "AGENTS.md")
	data, err := os.ReadFile(agentsPath)
	if err != nil {
		t.Fatalf("AGENTS.md não materializado em %s: %v", agentsPath, err)
	}
	s := string(data)
	if !strings.HasPrefix(s, harness.MarkerKoine) {
		t.Errorf("AGENTS.md não começa com MarkerKoine:\n%.80s", s)
	}
	if !strings.Contains(s, "Agente Koine de teste.") {
		t.Errorf("AGENTS.md bootstrap deve inlinar o conteúdo do agente:\n%s", s)
	}
	if !strings.Contains(s, "/kn-02-mantem-catalogo") {
		t.Errorf("AGENTS.md bootstrap deve orientar criar o CONTEXTO.md:\n%s", s)
	}

	// ExtraArgs com o lift de project_doc_max_bytes
	if got := strings.Join(calledArgs, " "); got != "-c project_doc_max_bytes=1048576" {
		t.Errorf("ExtraArgs = %v, want [-c project_doc_max_bytes=1048576]", calledArgs)
	}
}

func TestRodarWrapperSubstituirPulaConflito(t *testing.T) {
	dir := t.TempDir()

	// CLAUDE.md pré-existente sem marker → conflito
	if err := os.WriteFile(filepath.Join(dir, "CLAUDE.md"),
		[]byte("# Arquivo existente sem marker\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	tmpCfg := t.TempDir()
	origCfg := cfg.ExportLookupConfigDir()
	cfg.SetLookupConfigDir(func() string { return filepath.Join(tmpCfg, "koine") })
	defer cfg.SetLookupConfigDir(origCfg)

	// vault fake: apenas hermes.md para ResolverBootstrap.
	// ClaudeCode.Renderizar usa vaultFS (embed.FS real) — não precisa criar template no disco.
	tmpVault := t.TempDir()
	os.MkdirAll(filepath.Join(tmpVault, "agentes"), 0o755)
	os.WriteFile(
		filepath.Join(tmpVault, "agentes", "hermes.md"),
		[]byte("---\nid: hermes-test\n---\n# Hermes\nAgente Koine de teste."),
		0o644,
	)
	origVault := contexto.ExportLookupVaultDir()
	contexto.SetLookupVaultDir(func() string { return tmpVault })
	defer contexto.SetLookupVaultDir(origVault)

	origLancar := lancarCliente
	lancarCliente = func(c, p string, env map[string]string, args []string) error { return nil }
	defer func() { lancarCliente = origLancar }()

	// sem --substituir → backup silencioso do arquivo do usuário + sucesso
	if err := rodarWrapper("claude", []string{"hermes", dir}); err != nil {
		t.Fatalf("sem --substituir esperado backup + sucesso, got erro: %v", err)
	}
	bak, err := os.ReadFile(filepath.Join(dir, "CLAUDE.md.bak"))
	if err != nil || !strings.Contains(string(bak), "Arquivo existente sem marker") {
		t.Errorf("esperado CLAUDE.md.bak preservando o arquivo original, got %q (err %v)", bak, err)
	}
	// o novo CLAUDE.md gerado deve ter o marker Koine
	novo, err := os.ReadFile(filepath.Join(dir, "CLAUDE.md"))
	if err != nil || !strings.HasPrefix(string(novo), harness.MarkerKoine) {
		t.Errorf("CLAUDE.md regenerado deve começar com MarkerKoine, got %q (err %v)", novo, err)
	}

	// com --substituir → sucesso (pula resolução, sobrescreve sem backup)
	if err := rodarWrapper("claude", []string{"hermes", dir, "--substituir"}); err != nil {
		t.Fatalf("com --substituir esperado sucesso: %v", err)
	}
}
