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

// resolverConflitos checa ArquivosNoWorkingDir e Symlinks do Lancamento por estados
// pré-existentes. Arquivo regular pré-existente que NÃO foi gerado pelo Koine é movido
// para um backup (.bak) e a sessão prossegue — sem perda, sem prompt. Estados ambíguos
// (diretório, symlink com alvo divergente) ainda retornam erro com sugestão de --substituir.
// ArquivosExternos (em ~/.cache/koine/) são ignorados: path controlado pelo adapter.
//
// `--substituir` faz o chamador pular esta função inteira (sobrescreve sem backup).
func resolverConflitos(lancamento harness.Lancamento, pastaAbs string) error {
	for rel := range lancamento.ArquivosNoWorkingDir {
		absPath := filepath.Join(pastaAbs, rel)
		if err := resolverArquivoConflito(absPath); err != nil {
			return err
		}
	}
	for linkPath, alvo := range lancamento.Symlinks {
		if err := resolverSymlinkConflito(linkPath, alvo); err != nil {
			return err
		}
	}
	return nil
}

// resolverArquivoConflito trata um path que será escrito como arquivo regular.
// Regras: não existe → OK; arquivo com marker Koine → OK (regeneração idempotente);
// arquivo regular sem marker → backup + OK; symlink → conflito; diretório → conflito.
func resolverArquivoConflito(absPath string) error {
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
	return fazerBackupComAviso(absPath) // arquivo do usuário → preserva em .bak e prossegue
}

// resolverSymlinkConflito trata um path que será criado como symlink com alvo alvoEsperado.
// Regras: não existe → OK; symlink com alvo correto → OK (no-op);
// symlink com alvo diferente → conflito; arquivo regular → backup + OK; diretório → conflito.
func resolverSymlinkConflito(linkPath, alvoEsperado string) error {
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
	return fazerBackupComAviso(linkPath) // arquivo regular onde symlink esperado → backup e prossegue
}

// fazerBackupComAviso move absPath para um nome de backup livre (.bak, .bak.1, ...) e
// imprime um aviso de uma linha em stderrWriter. Retorna erro só se o rename falhar.
func fazerBackupComAviso(absPath string) error {
	bak := caminhoBackupLivre(absPath)
	if err := os.Rename(absPath, bak); err != nil {
		return fmt.Errorf("backup de %s: %w", absPath, err)
	}
	fmt.Fprintf(stderrWriter, "aviso: %s existente (não gerado pelo Koine) salvo como %s — gerando contexto da sessão\n",
		filepath.Base(absPath), filepath.Base(bak))
	return nil
}

// caminhoBackupLivre retorna o primeiro nome de backup disponível para absPath:
// "<path>.bak", senão "<path>.bak.1", "<path>.bak.2", etc. — nunca sobrescreve um backup existente.
func caminhoBackupLivre(absPath string) string {
	bak := absPath + ".bak"
	if _, err := os.Lstat(bak); os.IsNotExist(err) {
		return bak
	}
	for i := 1; ; i++ {
		cand := fmt.Sprintf("%s.bak.%d", absPath, i)
		if _, err := os.Lstat(cand); os.IsNotExist(err) {
			return cand
		}
	}
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
