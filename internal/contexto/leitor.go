package contexto

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"

	"github.com/jrunic/koine/internal/config"
	"github.com/jrunic/koine/internal/harness"
	"github.com/jrunic/koine/internal/paths"
)

// lookupConfigDir e lookupVaultDir são injetáveis para testes — evitam os.Setenv (CONTEXTO.md §158).
var lookupConfigDir = paths.ConfigDir
var lookupVaultDir = paths.VaultDir

// CtxLocal representa o frontmatter de <pasta>/CONTEXTO.md.
// Campos mínimos para resolução; outros campos do frontmatter são ignorados.
type CtxLocal struct {
	Escopo   string   `yaml:"escopo"`
	Dominios []string `yaml:"dominios"`
}

// Resolver carrega CONTEXTO.md em <pasta>, resolve escopo e domínios,
// e devolve ContextoMontado com paths absolutos prontos para render.
//
// agente é o nome da persona canônica (ex: "hermes"). Procurada primeiro em
// ConfigDir()/agentes/<agente>.md; fallback VaultDir()/agentes/<agente>.md.
func Resolver(agente, pasta string) (harness.ContextoMontado, error) {
	contextoPath := filepath.Join(pasta, "CONTEXTO.md")

	if _, err := os.Stat(contextoPath); err != nil {
		if os.IsNotExist(err) {
			return harness.ContextoMontado{}, fmt.Errorf(
				"nenhum CONTEXTO.md em %s — rode /kn-02-mantem-catalogo (fluxo contexto) aqui ou aponte para pasta com CONTEXTO.md",
				pasta,
			)
		}
		return harness.ContextoMontado{}, err
	}

	ctx, err := lerCtxLocal(contextoPath)
	if err != nil {
		return harness.ContextoMontado{}, err
	}
	if ctx.Escopo == "" {
		return harness.ContextoMontado{}, fmt.Errorf("%s: campo `escopo:` ausente ou vazio", contextoPath)
	}
	if len(ctx.Dominios) == 0 {
		return harness.ContextoMontado{}, fmt.Errorf("%s: campo `dominios:` ausente ou vazio", contextoPath)
	}

	escopo, err := config.LerEscopo(ctx.Escopo)
	if err != nil {
		return harness.ContextoMontado{}, err
	}

	pastaRef, err := paths.ResolverTagged(escopo.PastaReferencias)
	if err != nil {
		return harness.ContextoMontado{}, fmt.Errorf("escopo %q: pasta-referencias: %w", ctx.Escopo, err)
	}

	usuarioPath, err := config.AcharCaminhoUsuario()
	if err != nil {
		return harness.ContextoMontado{}, err
	}

	indicePaths := make([]string, len(ctx.Dominios))
	for i, d := range ctx.Dominios {
		indicePaths[i] = filepath.Join(pastaRef, "kn-indice-"+d+".md")
	}

	agentePath := filepath.Join(lookupConfigDir(), "agentes", agente+".md")
	if _, err := os.Stat(agentePath); err != nil {
		if !os.IsNotExist(err) {
			return harness.ContextoMontado{}, err
		}
		agentePath = filepath.Join(lookupVaultDir(), "agentes", agente+".md")
	}

	escopoPath := filepath.Join(lookupConfigDir(), "escopos", ctx.Escopo+".md")
	if _, err := os.Stat(escopoPath); err != nil {
		if os.IsNotExist(err) {
			return harness.ContextoMontado{}, fmt.Errorf(
				"escopo %q declarado em CONTEXTO.md mas não encontrado em %s — rode /kn-02-mantem-catalogo (fluxo escopo)",
				ctx.Escopo, escopoPath,
			)
		}
		return harness.ContextoMontado{}, err
	}

	return harness.ContextoMontado{
		UsuarioPath:  usuarioPath,
		KoineMDPath:  filepath.Join(lookupVaultDir(), "KOINE.md"),
		AgentePath:   agentePath,
		EscopoPath:   escopoPath,
		IndicePaths:  indicePaths,
		ContextoPath: contextoPath,
	}, nil
}

// ResolverBootstrap retorna ContextoMontado mínimo (usuario + KOINE + Hermes)
// para uso em pastas sem CONTEXTO.md. Sempre usa hermes como agente.
// EscopoPath, IndicePaths e ContextoPath ficam vazios.
// Não falha se o arquivo do usuário não existir — retorna UsuarioPath vazio.
func ResolverBootstrap() (harness.ContextoMontado, error) {
	usuarioPath, _ := config.AcharCaminhoUsuario() // vazio se não encontrado; não bloqueia bootstrap
	return harness.ContextoMontado{
		Bootstrap:   true,
		UsuarioPath: usuarioPath,
		KoineMDPath: filepath.Join(lookupVaultDir(), "KOINE.md"),
		AgentePath:  filepath.Join(lookupVaultDir(), "agentes", "hermes.md"),
	}, nil
}

// PastaReferencias resolve apenas a pasta-referências do escopo (sem montar tudo).
// Útil para o gerador de índices.
func PastaReferencias(slug string) (string, error) {
	escopo, err := config.LerEscopo(slug)
	if err != nil {
		return "", err
	}
	return paths.ResolverTagged(escopo.PastaReferencias)
}

func lerCtxLocal(path string) (CtxLocal, error) {
	fm, _, err := config.LerFrontmatter(path)
	if err != nil {
		return CtxLocal{}, err
	}
	var c CtxLocal
	if err := yaml.Unmarshal(fm, &c); err != nil {
		return CtxLocal{}, fmt.Errorf("%s: frontmatter inválido: %w", path, err)
	}
	return c, nil
}
