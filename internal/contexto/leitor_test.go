package contexto

import (
	"os"
	"path/filepath"
	"testing"

	cfg "github.com/jrunic/koine/internal/config"
)

// setupTmp cria árvore mínima e injeta lookups via var-hook (CONTEXTO.md §158).
// Devolve (trabalho, xdgCfg, cleanup). xdgCfg é a raiz da config (equivalente a
// XDG_CONFIG_HOME em runtime real); ConfigDir() vira xdgCfg/koine.
//
// Estrutura criada:
//
//	<tmp>/xdg-config/           ← xdgCfg
//	<tmp>/xdg-config/koine/     ← ConfigDir() injetado
//	<tmp>/xdg-config/koine/walter.md
//	<tmp>/xdg-config/koine/escopos/teste.md
//	<tmp>/vault/                ← VaultDir() injetado
//	<tmp>/ref/                  ← pasta-referências do escopo
//	<tmp>/trabalho/CONTEXTO.md  ← pasta de trabalho
func setupTmp(t *testing.T) (trabalho, xdgCfg string, cleanup func()) {
	t.Helper()
	tmp := t.TempDir()

	xdgCfg = filepath.Join(tmp, "xdg-config")
	koineDir := filepath.Join(xdgCfg, "koine")
	if err := os.MkdirAll(filepath.Join(koineDir, "escopos"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(koineDir, "dominios"), 0o755); err != nil {
		t.Fatal(err)
	}

	persona := "---\nnome: Walter\nidioma: pt-BR\npapel: mentee\ntimezone: America/Sao_Paulo\n---\n\n# Walter\n"
	if err := os.WriteFile(filepath.Join(koineDir, "walter.md"), []byte(persona), 0o644); err != nil {
		t.Fatal(err)
	}

	ref := filepath.Join(tmp, "ref")
	if err := os.MkdirAll(ref, 0o755); err != nil {
		t.Fatal(err)
	}

	escopo := "---\nnome: teste\npasta-referencias: abs:" + ref + "\nescopo-pai: \"\"\nproprietario: walter\n---\n\n# Teste\n"
	if err := os.WriteFile(filepath.Join(koineDir, "escopos", "teste.md"), []byte(escopo), 0o644); err != nil {
		t.Fatal(err)
	}

	trabalho = filepath.Join(tmp, "trabalho")
	if err := os.MkdirAll(trabalho, 0o755); err != nil {
		t.Fatal(err)
	}

	ctxData := "---\nescopo: teste\ndominios: [pessoas, entidades]\n---\n\n# Trabalho\n"
	if err := os.WriteFile(filepath.Join(trabalho, "CONTEXTO.md"), []byte(ctxData), 0o644); err != nil {
		t.Fatal(err)
	}

	vault := filepath.Join(tmp, "vault")
	if err := os.MkdirAll(vault, 0o755); err != nil {
		t.Fatal(err)
	}

	origCtxCfg := lookupConfigDir
	origCtxVault := lookupVaultDir
	origConfigCfg := cfg.ExportLookupConfigDir()
	lookupConfigDir = func() string { return koineDir }
	lookupVaultDir = func() string { return vault }
	cfg.SetLookupConfigDir(func() string { return koineDir })

	cleanup = func() {
		lookupConfigDir = origCtxCfg
		lookupVaultDir = origCtxVault
		cfg.SetLookupConfigDir(origConfigCfg)
	}
	return trabalho, xdgCfg, cleanup
}

func TestResolverHappyPath(t *testing.T) {
	trabalho, _, cleanup := setupTmp(t)
	defer cleanup()

	cm, err := Resolver("hermes", trabalho)
	if err != nil {
		t.Fatalf("Resolver: %v", err)
	}

	if filepath.Base(cm.UsuarioPath) != "walter.md" {
		t.Errorf("UsuarioPath %q não termina em walter.md", cm.UsuarioPath)
	}
	if filepath.Base(cm.AgentePath) != "hermes.md" {
		t.Errorf("AgentePath %q não termina em hermes.md", cm.AgentePath)
	}
	if filepath.Base(cm.EscopoPath) != "teste.md" {
		t.Errorf("EscopoPath %q não termina em teste.md", cm.EscopoPath)
	}
	if len(cm.IndicePaths) != 2 || filepath.Base(cm.IndicePaths[1]) != "kn-indice-entidades.md" {
		t.Errorf("IndicePaths inesperado: %v", cm.IndicePaths)
	}
	if filepath.Base(cm.ContextoPath) != "CONTEXTO.md" {
		t.Errorf("ContextoPath %q não termina em CONTEXTO.md", cm.ContextoPath)
	}
}

func TestResolverSemContexto(t *testing.T) {
	trabalho, _, cleanup := setupTmp(t)
	defer cleanup()
	os.Remove(filepath.Join(trabalho, "CONTEXTO.md"))

	_, err := Resolver("hermes", trabalho)
	if err == nil {
		t.Fatal("esperava erro de CONTEXTO.md ausente")
	}
	if !contemSubstring(err.Error(), "nenhum CONTEXTO.md") {
		t.Errorf("mensagem de erro não menciona ausência: %v", err)
	}
}

func TestResolverEscopoInexistente(t *testing.T) {
	trabalho, _, cleanup := setupTmp(t)
	defer cleanup()

	ctxData := "---\nescopo: nao-existe\ndominios: [pessoas]\n---\n"
	if err := os.WriteFile(filepath.Join(trabalho, "CONTEXTO.md"), []byte(ctxData), 0o644); err != nil {
		t.Fatal(err)
	}

	_, err := Resolver("hermes", trabalho)
	if err == nil {
		t.Fatal("esperava erro de escopo inexistente")
	}
}

func TestResolverAgentePrecedenciaConfig(t *testing.T) {
	trabalho, xdgCfg, cleanup := setupTmp(t)
	defer cleanup()

	// planta agente em ConfigDir()/agentes/ — deve ter precedência sobre vault
	agentesDir := filepath.Join(xdgCfg, "koine", "agentes")
	if err := os.MkdirAll(agentesDir, 0o755); err != nil {
		t.Fatal(err)
	}
	agentePath := filepath.Join(agentesDir, "hermes.md")
	if err := os.WriteFile(agentePath, []byte("---\nnome: hermes\n---\n\n# Hermes config\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	cm, err := Resolver("hermes", trabalho)
	if err != nil {
		t.Fatalf("Resolver: %v", err)
	}
	if cm.AgentePath != agentePath {
		t.Errorf("esperava AgentePath=%q, obteve %q", agentePath, cm.AgentePath)
	}
}

func TestResolverBootstrapSemUsuario(t *testing.T) {
	_, _, cleanup := setupTmp(t)
	defer cleanup()

	// remove o arquivo do usuário para simular instalação inicial
	koineDir := lookupConfigDir()
	entries, _ := os.ReadDir(koineDir)
	for _, e := range entries {
		if !e.IsDir() {
			os.Remove(filepath.Join(koineDir, e.Name()))
		}
	}

	cm, err := ResolverBootstrap()
	if err != nil {
		t.Fatalf("ResolverBootstrap: %v", err)
	}
	if !cm.Bootstrap {
		t.Error("Bootstrap deve ser true")
	}
	if cm.UsuarioPath != "" {
		t.Errorf("UsuarioPath deve ser vazio sem arquivo de usuario, obteve %q", cm.UsuarioPath)
	}
	if cm.KoineMDPath == "" {
		t.Error("KoineMDPath não deve ser vazio")
	}
	if cm.AgentePath == "" {
		t.Error("AgentePath não deve ser vazio")
	}
	if cm.EscopoPath != "" || len(cm.IndicePaths) != 0 || cm.ContextoPath != "" {
		t.Error("EscopoPath/IndicePaths/ContextoPath devem estar vazios no bootstrap")
	}
}

func TestResolverBootstrapComUsuario(t *testing.T) {
	_, _, cleanup := setupTmp(t)
	defer cleanup()

	cm, err := ResolverBootstrap()
	if err != nil {
		t.Fatalf("ResolverBootstrap: %v", err)
	}
	if !cm.Bootstrap {
		t.Error("Bootstrap deve ser true")
	}
	if filepath.Base(cm.UsuarioPath) != "walter.md" {
		t.Errorf("UsuarioPath %q não termina em walter.md", cm.UsuarioPath)
	}
	if filepath.Base(cm.AgentePath) != "hermes.md" {
		t.Errorf("AgentePath %q não termina em hermes.md", cm.AgentePath)
	}
}

func contemSubstring(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}
