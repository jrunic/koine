package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"

	"github.com/jrunic/koine/internal/contexto"
	"github.com/jrunic/koine/internal/harness"
	"github.com/jrunic/koine/internal/indice"
	"github.com/jrunic/koine/internal/pasta"
)

var gerarCmd = &cobra.Command{
	Use:   "gerar <agente> [pasta]",
	Short: "Gera CLAUDE.md sem abrir o cliente IA (uso administrativo)",
	Args:  cobra.RangeArgs(1, 2),
	RunE:  rodarGerar,
}

func init() {
	rootCmd.AddCommand(gerarCmd)
}

// rodarGerar gera CLAUDE.md em <pasta> (ou pwd se omitida).
func rodarGerar(cmd *cobra.Command, args []string) error {
	agente := args[0]
	pastaArg := ""
	if len(args) >= 2 {
		pastaArg = args[1]
	}
	pastaAbs, err := pasta.Resolver(pastaArg)
	if err != nil {
		return fmt.Errorf("resolver pasta: %w", err)
	}
	return executar(agente, pastaAbs, nil)
}

// executar é o caminho administrativo (subcomando gerar + mostrar).
// Sempre usa ClaudeCode — não seleciona adapter por cliente IA.
// Se out != nil, escreve em out (mostrar). Se nil, escreve em <pastaAbs>/CLAUDE.md.
func executar(agente, pastaAbs string, out io.Writer) error {
	cm, agenteEfetivo, err := resolverContextoParaWrapper(agente, pastaAbs)
	if err != nil {
		return err
	}

	if !cm.Bootstrap {
		pastaRef := derivarPastaRef(cm)
		domsDeclarados := derivarDominios(cm)
		if pastaRef != "" {
			if err := indice.Gerar(pastaRef, domsDeclarados, os.Stderr); err != nil {
				return fmt.Errorf("gerador de índices: %w", err)
			}
		}
	}

	cc := &harness.ClaudeCode{VaultFS: vaultFS, Agente: agenteEfetivo}
	lancamento, err := cc.Renderizar(cm)
	if err != nil {
		return err
	}
	saida := lancamento.ArquivosNoWorkingDir["CLAUDE.md"]

	if out != nil {
		_, err := out.Write(saida)
		return err
	}

	destino := cc.CaminhoArquivoContexto(pastaAbs)
	if err := os.WriteFile(destino, saida, 0o644); err != nil {
		return fmt.Errorf("escrevendo %s: %w", destino, err)
	}
	fmt.Printf("Escrito %s (%d bytes)\n", destino, len(saida))
	return nil
}

// resolverContextoParaWrapper resolve o contexto montado com detecção de bootstrap.
// Retorna (cm, agenteEfetivo, err). Compartilhado por executar e rodarWrapper.
func resolverContextoParaWrapper(agente, pastaAbs string) (harness.ContextoMontado, string, error) {
	if _, statErr := os.Stat(filepath.Join(pastaAbs, "CONTEXTO.md")); os.IsNotExist(statErr) {
		fmt.Fprintf(os.Stderr,
			"kn-agente: CONTEXTO.md ausente em %s — modo bootstrap: carregando Hermes (em vez de %q) para guiar a criação do contexto\n",
			pastaAbs, agente)
		cm, err := contexto.ResolverBootstrap()
		return cm, "hermes", err
	}
	cm, err := contexto.Resolver(agente, pastaAbs)
	if err != nil {
		return cm, agente, err
	}
	// Bootstrap explícito: agente foi forçado para Hermes no Resolver; refletir no agenteEfetivo
	// para o adapter usar "hermes" como identidade nos arquivos gerados.
	if cm.Bootstrap {
		return cm, "hermes", nil
	}
	return cm, agente, nil
}

// materializarArquivosLocais escreve ArquivosNoWorkingDir em pastaAbs.
// Cria diretórios pai se necessário.
func materializarArquivosLocais(pastaAbs string, arquivos map[string][]byte) error {
	for rel, conteudo := range arquivos {
		dest := filepath.Join(pastaAbs, rel)
		if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
			return fmt.Errorf("criar dir para %s: %w", rel, err)
		}
		if err := os.WriteFile(dest, conteudo, 0o644); err != nil {
			return fmt.Errorf("escrevendo %s: %w", dest, err)
		}
	}
	return nil
}

// materializarArquivosExternos escreve ArquivosExternos em paths absolutos.
// Cria diretórios pai se necessário.
func materializarArquivosExternos(arquivos map[string][]byte) error {
	for absPath, conteudo := range arquivos {
		if err := os.MkdirAll(filepath.Dir(absPath), 0o755); err != nil {
			return fmt.Errorf("criar dir para %s: %w", absPath, err)
		}
		if err := os.WriteFile(absPath, conteudo, 0o644); err != nil {
			return fmt.Errorf("escrevendo %s: %w", absPath, err)
		}
	}
	return nil
}

// criarSymlinksLancamento cria os symlinks declarados em Lancamento.Symlinks.
// Remove o destino se já existir — Fase 3 adicionará detecção de conflito.
func criarSymlinksLancamento(symlinks map[string]string) error {
	for link, alvo := range symlinks {
		if err := os.MkdirAll(filepath.Dir(link), 0o755); err != nil {
			return fmt.Errorf("criar dir para symlink %s: %w", link, err)
		}
		os.Remove(link) // no-op se não existe; Fase 3 adicionará conflito check
		if err := os.Symlink(alvo, link); err != nil {
			return fmt.Errorf("criar symlink %s → %s: %w", link, alvo, err)
		}
	}
	return nil
}

func derivarPastaRef(cm harness.ContextoMontado) string {
	if len(cm.IndicePaths) == 0 {
		return ""
	}
	return filepath.Dir(cm.IndicePaths[0])
}

func derivarDominios(cm harness.ContextoMontado) []string {
	out := make([]string, 0, len(cm.IndicePaths))
	for _, p := range cm.IndicePaths {
		base := strings.TrimSuffix(filepath.Base(p), ".md")
		out = append(out, strings.TrimPrefix(base, "kn-indice-"))
	}
	return out
}
