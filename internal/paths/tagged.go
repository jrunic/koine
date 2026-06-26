package paths

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
)

// ResolverTagged resolve um tagged path para um path absoluto.
//
// Prefixos suportados:
//   - home:<rel>  — relativo a $HOME / %USERPROFILE%
//   - abs:<path>  — path absoluto literal
//
// Sem prefixo = erro; sem DWIM silencioso (ADR 20260621-estrutura-config-koine §3).
func ResolverTagged(tagged string) (string, error) {
	if strings.HasPrefix(tagged, "home:") {
		rel := strings.TrimPrefix(tagged, "home:")
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		return filepath.Join(home, filepath.FromSlash(rel)), nil
	}
	if strings.HasPrefix(tagged, "abs:") {
		path := strings.TrimPrefix(tagged, "abs:")
		if !filepath.IsAbs(path) {
			return "", errors.New("tagged path abs: requer path absoluto: " + path)
		}
		return filepath.FromSlash(path), nil
	}
	return "", errors.New("tagged path sem prefixo reconhecido (use home: ou abs:): " + tagged)
}
