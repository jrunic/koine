package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/jrunic/koine/internal/harness"
)

// parseSubstituir remove "--substituir" de args e retorna (args filtrados, true se presente).
// Aceita a flag em qualquer posição nos args.
func parseSubstituir(args []string) ([]string, bool) {
	var filtered []string
	substituir := false
	for _, a := range args {
		if a == "--substituir" {
			substituir = true
		} else {
			filtered = append(filtered, a)
		}
	}
	return filtered, substituir
}

// verificarConflitos checa ArquivosNoWorkingDir e Symlinks do Lancamento
// por estados pré-existentes incompatíveis. Retorna erro descritivo com sugestão de --substituir.
// ArquivosExternos (em ~/.cache/koine/) são ignorados: path controlado pelo adapter.
func verificarConflitos(lancamento harness.Lancamento, pastaAbs string) error {
	for rel := range lancamento.ArquivosNoWorkingDir {
		absPath := filepath.Join(pastaAbs, rel)
		if err := checarArquivoConflito(absPath); err != nil {
			return err
		}
	}
	for linkPath, alvo := range lancamento.Symlinks {
		if err := checarSymlinkConflito(linkPath, alvo); err != nil {
			return err
		}
	}
	return nil
}

// checarArquivoConflito verifica um path que será escrito como arquivo regular.
// Regras: não existe → OK; arquivo com marker Koine → OK; arquivo sem marker → conflito;
// symlink → conflito; diretório → conflito.
func checarArquivoConflito(absPath string) error {
	info, err := os.Lstat(absPath)
	if os.IsNotExist(err) {
		return nil
	}
	if err != nil {
		return fmt.Errorf("verificando %s: %w", absPath, err)
	}
	if info.Mode()&os.ModeSymlink != 0 {
		return erroConflito(absPath, "é um symlink — esperava arquivo regular")
	}
	if info.IsDir() {
		return erroConflito(absPath, "é um diretório")
	}
	if temMarkerKoine(absPath) {
		return nil // regeneração idempotente
	}
	return erroConflito(absPath, "arquivo existente não foi gerado por kn-agente")
}

// checarSymlinkConflito verifica um path que será criado como symlink com alvo alvoEsperado.
// Regras: não existe → OK; symlink com alvo correto → OK (no-op);
// symlink com alvo diferente → conflito; arquivo regular → conflito; diretório → conflito.
func checarSymlinkConflito(linkPath, alvoEsperado string) error {
	info, err := os.Lstat(linkPath)
	if os.IsNotExist(err) {
		return nil
	}
	if err != nil {
		return fmt.Errorf("verificando %s: %w", linkPath, err)
	}
	if info.Mode()&os.ModeSymlink != 0 {
		alvoAtual, err := os.Readlink(linkPath)
		if err != nil {
			return fmt.Errorf("lendo symlink %s: %w", linkPath, err)
		}
		if alvoAtual == alvoEsperado {
			return nil // symlink correto — no-op
		}
		return erroConflito(linkPath, fmt.Sprintf("symlink aponta para %q, esperado %q", alvoAtual, alvoEsperado))
	}
	if info.IsDir() {
		return erroConflito(linkPath, "é um diretório")
	}
	return erroConflito(linkPath, "é um arquivo regular — esperava symlink")
}

// temMarkerKoine lê a primeira linha de absPath e verifica presença de MarkerKoine.
// Compatibilidade retroativa: CLAUDE.md/GEMINI.md gerados antes da Fase 3 não têm o marker
// HTML, mas contêm a assinatura do template ("Regerar: `kn-agente"). São tratados como Koine.
func temMarkerKoine(absPath string) bool {
	data, err := os.ReadFile(absPath)
	if err != nil {
		return false
	}
	s := string(data)
	firstLine := strings.SplitN(s, "\n", 2)[0]
	if firstLine == harness.MarkerKoine {
		return true
	}
	// retrocompatibilidade com arquivos gerados pré-Fase-3
	return strings.Contains(s, "Regerar: `kn-agente")
}

func erroConflito(path, motivo string) error {
	return fmt.Errorf("conflito em %s: %s — use --substituir para forçar", path, motivo)
}
