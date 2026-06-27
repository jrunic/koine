package harness

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/jrunic/koine/internal/cache"
	"github.com/jrunic/koine/internal/render"
)

// Copilot é o adapter do harness para o GitHub Copilot CLI.
//
// Materializa em ~/.cache/koine/copilot-bundles/<slot>/:
//   - AGENTS.md — USUARIO + Hermes mesclados (frontmatter removido, H1→H2)
//   - .github/instructions/escopo.instructions.md
//   - .github/instructions/kn-indice-<dom>.instructions.md (por entrada em IndicePaths)
//
// Cria symlink <pasta>/.github/copilot-instructions.md → <pasta>/CONTEXTO.md.
// Seta COPILOT_CUSTOM_INSTRUCTIONS_DIRS apontando para o bundle.
// Modo bootstrap: apenas AGENTS.md + env var; sem symlink nem instructions.
type Copilot struct {
	// Agente é o nome da persona canônica (ex: "hermes").
	Agente string
	// PastaAbs é o diretório de trabalho absoluto — determina SlotID e alvo do symlink.
	PastaAbs string
}

func (c *Copilot) Nome() string {
	return "copilot"
}

func (c *Copilot) CaminhoArquivoContexto(cwd string) string {
	return filepath.Join(cwd, ".github", "copilot-instructions.md")
}

func (c *Copilot) Renderizar(dados ContextoMontado) (Lancamento, error) {
	slotID := cache.SlotID(c.PastaAbs)
	bundleDir := cache.CaminhoBundle("copilot-bundles", slotID)

	lancamento := Lancamento{
		ArquivosExternos: make(map[string][]byte),
		EnvVars: map[string]string{
			"COPILOT_CUSTOM_INSTRUCTIONS_DIRS": bundleDir,
		},
	}

	agentsMD, err := c.montarAgentsMD(dados)
	if err != nil {
		return Lancamento{}, err
	}
	lancamento.ArquivosExternos[filepath.Join(bundleDir, "AGENTS.md")] = agentsMD

	if dados.Bootstrap {
		if dados.ContextoPath != "" {
			conteudo, err := os.ReadFile(dados.ContextoPath)
			if err != nil {
				return Lancamento{}, fmt.Errorf("lendo CONTEXTO.md em bootstrap: %w", err)
			}
			instrPath := filepath.Join(bundleDir, ".github", "instructions", "bootstrap.instructions.md")
			lancamento.ArquivosExternos[instrPath] = render.WraparInstructions(conteudo)
		}
		return lancamento, nil
	}

	if dados.EscopoPath != "" {
		conteudo, err := os.ReadFile(dados.EscopoPath)
		if err != nil {
			return Lancamento{}, fmt.Errorf("lendo escopo: %w", err)
		}
		instrPath := filepath.Join(bundleDir, ".github", "instructions", "escopo.instructions.md")
		lancamento.ArquivosExternos[instrPath] = render.WraparInstructions(conteudo)
	}

	for _, indicePath := range dados.IndicePaths {
		conteudo, err := os.ReadFile(indicePath)
		if err != nil {
			return Lancamento{}, fmt.Errorf("lendo índice %s: %w", indicePath, err)
		}
		dom := dominioDe(indicePath)
		instrPath := filepath.Join(bundleDir, ".github", "instructions", "kn-indice-"+dom+".instructions.md")
		lancamento.ArquivosExternos[instrPath] = render.WraparInstructions(conteudo)
	}

	linkPath := filepath.Join(c.PastaAbs, ".github", "copilot-instructions.md")
	lancamento.Symlinks = map[string]string{
		linkPath: dados.ContextoPath,
	}

	return lancamento, nil
}

func (c *Copilot) montarAgentsMD(dados ContextoMontado) ([]byte, error) {
	var partes []render.Parte

	if dados.UsuarioPath != "" {
		conteudo, err := os.ReadFile(dados.UsuarioPath)
		if err != nil {
			return nil, fmt.Errorf("lendo usuario: %w", err)
		}
		partes = append(partes, render.Parte{Secao: "Usuário", Conteudo: conteudo})
	}

	conteudoAgente, err := os.ReadFile(dados.AgentePath)
	if err != nil {
		return nil, fmt.Errorf("lendo agente %s: %w", dados.AgentePath, err)
	}
	partes = append(partes, render.Parte{Secao: "Agente", Conteudo: conteudoAgente})

	return render.MescarDocumentos("Sessão Koine — Copilot", partes), nil
}

// dominioDe extrai o nome de domínio de um caminho de índice.
// Ex: /foo/kn-indice-universal.md → "universal"
func dominioDe(indicePath string) string {
	base := strings.TrimSuffix(filepath.Base(indicePath), ".md")
	return strings.TrimPrefix(base, "kn-indice-")
}

// Verifica em compile-time que Copilot satisfaz Harness.
var _ Harness = (*Copilot)(nil)
