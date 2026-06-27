package harness

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/jrunic/koine/internal/cache"
)

// OpenCode é o adapter do harness para o OpenCode CLI.
//
// Materializa em ~/.cache/koine/opencode-configs/<slot>.json com array
// instructions listando paths absolutos de USUARIO, Hermes, escopo, índices.
//
// Cria symlink <pasta>/AGENTS.md → <pasta>/CONTEXTO.md.
// Seta OPENCODE_CONFIG=<json> e OPENCODE_DISABLE_CLAUDE_CODE=1.
// Emite aviso se ~/.config/opencode/AGENTS.md existir (mescla implícita do OpenCode).
// Modo bootstrap: JSON com USUARIO + Hermes apenas; sem symlink.
type OpenCode struct {
	// Agente é o nome da persona canônica (ex: "hermes").
	Agente string
	// PastaAbs é o diretório de trabalho absoluto — determina SlotID e alvo do symlink.
	PastaAbs string
}

// openCodeConfig é a estrutura do arquivo JSON que o OpenCode lê via OPENCODE_CONFIG.
type openCodeConfig struct {
	Schema       string   `json:"$schema"`
	Instructions []string `json:"instructions"`
}

// lookupStatOpenCodeGlobal é injetável para testes (mock de os.Stat).
var lookupStatOpenCodeGlobal = os.Stat

// ExportLookupStatOpenCodeGlobal expõe o hook para testes.
func ExportLookupStatOpenCodeGlobal() func(string) (os.FileInfo, error) {
	return lookupStatOpenCodeGlobal
}

// SetLookupStatOpenCodeGlobal permite injetar mock em testes.
func SetLookupStatOpenCodeGlobal(f func(string) (os.FileInfo, error)) {
	lookupStatOpenCodeGlobal = f
}

func (o *OpenCode) Nome() string { return "opencode" }

func (o *OpenCode) CaminhoArquivoContexto(cwd string) string {
	return filepath.Join(cwd, "AGENTS.md")
}

func (o *OpenCode) Renderizar(dados ContextoMontado) (Lancamento, error) {
	slotID := cache.SlotID(o.PastaAbs)
	configPath := cache.CaminhoArquivo("opencode-configs", slotID, "json")

	// aviso: ~/.config/opencode/AGENTS.md é mesclado pelo OpenCode em toda sessão
	globalPath := openCodeGlobalConfigPath()
	if _, err := lookupStatOpenCodeGlobal(globalPath); err == nil {
		fmt.Fprintf(os.Stderr,
			"aviso: %s detectado — será mesclado nesta sessão Koine. Para isolar completamente, mova ou renomeie o arquivo.\n",
			globalPath)
	}

	var instructions []string
	if dados.UsuarioPath != "" {
		instructions = append(instructions, dados.UsuarioPath)
	}
	instructions = append(instructions, dados.AgentePath)
	if dados.Bootstrap {
		// Bootstrap explícito: CONTEXTO.md vai direto em instructions
		// (não há symlink AGENTS.md → CONTEXTO.md em bootstrap, ver bloco final).
		if dados.ContextoPath != "" {
			instructions = append(instructions, dados.ContextoPath)
		}
	} else {
		if dados.EscopoPath != "" {
			instructions = append(instructions, dados.EscopoPath)
		}
		instructions = append(instructions, dados.IndicePaths...)
	}

	cfg := openCodeConfig{
		Schema:       "https://opencode.ai/config.json",
		Instructions: instructions,
	}
	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return Lancamento{}, fmt.Errorf("gerando config OpenCode: %w", err)
	}

	lancamento := Lancamento{
		ArquivosExternos: map[string][]byte{configPath: data},
		EnvVars: map[string]string{
			"OPENCODE_CONFIG":              configPath,
			"OPENCODE_DISABLE_CLAUDE_CODE": "1",
		},
	}

	if !dados.Bootstrap {
		linkPath := filepath.Join(o.PastaAbs, "AGENTS.md")
		lancamento.Symlinks = map[string]string{linkPath: dados.ContextoPath}
	}

	return lancamento, nil
}

// openCodeGlobalConfigPath retorna o path do AGENTS.md global do OpenCode.
func openCodeGlobalConfigPath() string {
	if v := os.Getenv("XDG_CONFIG_HOME"); v != "" {
		return filepath.Join(v, "opencode", "AGENTS.md")
	}
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "opencode", "AGENTS.md")
}

// Verifica em compile-time que OpenCode satisfaz Harness.
var _ Harness = (*OpenCode)(nil)
