package cache

import (
	"crypto/sha256"
	"fmt"
	"path/filepath"

	"github.com/jrunic/koine/internal/paths"
)

// lookupCacheDir é injetável para testes — evita os.Setenv (padrão do repo).
var lookupCacheDir = paths.CacheDir

// SlotID retorna identificador determinístico de 12 chars hex baseado em SHA-256(pastaAbs).
// Mesma pasta → mesmo slot. Sem timestamp — cache cresce em #pastas, não em #sessões.
func SlotID(pastaAbs string) string {
	h := sha256.Sum256([]byte(pastaAbs))
	return fmt.Sprintf("%x", h[:6]) // 6 bytes = 12 hex chars
}

// CaminhoBundle retorna o diretório do bundle para (categoria, slotID).
// Ex: CaminhoBundle("copilot-bundles", id) → ~/.cache/koine/copilot-bundles/<id>
func CaminhoBundle(categoria, slotID string) string {
	return filepath.Join(lookupCacheDir(), categoria, slotID)
}

// CaminhoArquivo retorna o path de config única para (categoria, slotID, extensao).
// Ex: CaminhoArquivo("opencode-configs", id, "json") → ~/.cache/koine/opencode-configs/<id>.json
func CaminhoArquivo(categoria, slotID, extensao string) string {
	return filepath.Join(lookupCacheDir(), categoria, slotID+"."+extensao)
}
