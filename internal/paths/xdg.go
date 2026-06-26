package paths

import (
	"os"
	"path/filepath"
)

// VaultDir retorna o diretório de vault do Koine.
// Readonly em runtime — conteúdo extraído pelo kn-agente instalar.
//
// Ordem de resolução (idêntica em Mac/Linux/Windows):
//  1. $XDG_DATA_HOME/koine/
//  2. ~/.local/share/koine/
func VaultDir() string {
	if v := os.Getenv("XDG_DATA_HOME"); v != "" {
		return filepath.Join(v, "koine")
	}
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".local", "share", "koine")
}

// ConfigDir retorna o diretório de config do mentee. Writeable.
// Contém persona, escopos e domínios.
//
// Ordem de resolução (idêntica em Mac/Linux/Windows):
//  1. $XDG_CONFIG_HOME/koine/
//  2. ~/.config/koine/
//
// Não usa os.UserConfigDir(): no Darwin a stdlib ignora XDG_CONFIG_HOME
// e retorna ~/Library/Application Support — desvio que quebra Syncthing
// cross-platform (Mac↔Linux). Path estruturalmente idêntico é requisito.
func ConfigDir() string {
	if v := os.Getenv("XDG_CONFIG_HOME"); v != "" {
		return filepath.Join(v, "koine")
	}
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "koine")
}

// CacheDir retorna o diretório de cache do Koine.
//
// Ordem de resolução (idêntica em Mac/Linux/Windows):
//  1. $XDG_CACHE_HOME/koine/
//  2. ~/.cache/koine/
func CacheDir() string {
	if v := os.Getenv("XDG_CACHE_HOME"); v != "" {
		return filepath.Join(v, "koine")
	}
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".cache", "koine")
}
