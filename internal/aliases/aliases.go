package aliases

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/jrunic/koine/internal/paths"
)

// lookupConfigDir é injetável para testes — evita os.Setenv (padrão CONTEXTO.md).
var lookupConfigDir = paths.ConfigDir

// Entrada representa um alias de pasta.
type Entrada struct {
	Path string `json:"path"` // relativo a Home ou absoluto
	From string `json:"from"` // "home" | "abs"
}

// Aliases é o conteúdo de ~/.config/koine/aliases.json.
type Aliases struct {
	Pastas map[string]Entrada `json:"pastas"`
}

// ConfigPath retorna o caminho canônico do aliases.json.
func ConfigPath() string {
	return filepath.Join(lookupConfigDir(), "aliases.json")
}

// Carregar lê aliases.json. Retorna estrutura vazia se o arquivo não existir.
func Carregar() (Aliases, error) {
	data, err := os.ReadFile(ConfigPath())
	if os.IsNotExist(err) {
		return Aliases{Pastas: map[string]Entrada{}}, nil
	}
	if err != nil {
		return Aliases{}, fmt.Errorf("ler aliases: %w", err)
	}
	var a Aliases
	if err := json.Unmarshal(data, &a); err != nil {
		return Aliases{}, fmt.Errorf("parsear aliases: %w", err)
	}
	if a.Pastas == nil {
		a.Pastas = map[string]Entrada{}
	}
	return a, nil
}

// Salvar grava aliases.json.
func Salvar(a Aliases) error {
	if err := os.MkdirAll(filepath.Dir(ConfigPath()), 0o755); err != nil {
		return err
	}
	data, err := json.MarshalIndent(a, "", "  ")
	if err != nil {
		return fmt.Errorf("serializar aliases: %w", err)
	}
	return os.WriteFile(ConfigPath(), append(data, '\n'), 0o644)
}

// Resolver resolve chave para path absoluto. Retorna ("", false) se não encontrado.
func Resolver(a Aliases, chave string) (string, bool) {
	e, ok := a.Pastas[chave]
	if !ok {
		return "", false
	}
	switch e.From {
	case "home":
		home, err := os.UserHomeDir()
		if err != nil {
			return "", false
		}
		return filepath.Join(home, e.Path), true
	case "abs":
		return e.Path, true
	default:
		return "", false
	}
}

// Adicionar persiste nova entrada (lê + modifica + salva).
func Adicionar(chave, path, from string) error {
	a, err := Carregar()
	if err != nil {
		return err
	}
	a.Pastas[chave] = Entrada{Path: path, From: from}
	return Salvar(a)
}
