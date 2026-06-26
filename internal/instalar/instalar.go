package instalar

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/jrunic/koine/internal/paths"
)

// Meta registra metadados de instalação em VaultDir()/.meta.json.
type Meta struct {
	Versao    string `json:"versao"`
	Timestamp string `json:"timestamp"`
}

// Opcoes controla o comportamento do Instalar.
type Opcoes struct {
	Force bool
}

// Instalar extrai vault do embed para VaultDir() e planta sementes de domínios em ConfigDir().
//
// vault é o embed.FS com prefixo "vault/"; versao é a string de versão do binário.
// Exclui vault/templates/ e vault/dominios/ do destino em VaultDir() (decisões 2 e 7 do ADR).
// Planta vault/dominios/<dom>.md direto em ConfigDir()/dominios/<dom>.md.
func Instalar(vaultFS fs.FS, versao string, opts Opcoes) error {
	vaultDir := paths.VaultDir()
	configDir := paths.ConfigDir()

	if err := os.MkdirAll(vaultDir, 0o755); err != nil {
		return fmt.Errorf("criar vault dir: %w", err)
	}
	if err := os.MkdirAll(filepath.Join(configDir, "dominios"), 0o755); err != nil {
		return fmt.Errorf("criar config/dominios: %w", err)
	}
	if err := os.MkdirAll(filepath.Join(configDir, "escopos"), 0o755); err != nil {
		return fmt.Errorf("criar config/escopos: %w", err)
	}
	if err := os.MkdirAll(filepath.Join(configDir, "agentes"), 0o755); err != nil {
		return fmt.Errorf("criar config/agentes: %w", err)
	}

	var divergencias []string

	err := fs.WalkDir(vaultFS, "vault", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel := strings.TrimPrefix(path, "vault/")
		if rel == "" {
			return nil // raiz do vault
		}

		// Domínios: planta em ConfigDir()/dominios/ (não em VaultDir())
		if strings.HasPrefix(rel, "dominios/") {
			if d.IsDir() {
				return nil
			}
			dest := filepath.Join(configDir, filepath.FromSlash(rel))
			return copiarArquivo(vaultFS, path, dest, opts.Force, &divergencias)
		}

		// templates: embed-only, não extrai para disco
		if strings.HasPrefix(rel, "templates/") {
			return nil
		}

		// .gitkeep: artefato de repositório, não extrai
		if d.Name() == ".gitkeep" {
			return nil
		}

		dest := filepath.Join(vaultDir, filepath.FromSlash(rel))
		if d.IsDir() {
			return os.MkdirAll(dest, 0o755)
		}
		return copiarArquivo(vaultFS, path, dest, opts.Force, &divergencias)
	})
	if err != nil {
		return fmt.Errorf("extraindo vault: %w", err)
	}

	if len(divergencias) > 0 && !opts.Force {
		fmt.Println("Arquivos com conteúdo divergente do binário (use --force para sobrescrever):")
		for _, d := range divergencias {
			fmt.Println("  !", d)
		}
	}

	return gravarMeta(vaultDir, versao)
}

func copiarArquivo(vaultFS fs.FS, src, dest string, force bool, divergencias *[]string) error {
	data, err := fs.ReadFile(vaultFS, src)
	if err != nil {
		return err
	}

	if _, err := os.Stat(dest); err == nil {
		existing, _ := os.ReadFile(dest)
		if string(existing) == string(data) {
			return nil // idêntico, sem ação
		}
		if !force {
			*divergencias = append(*divergencias, dest)
			return nil
		}
	}

	if err := os.MkdirAll(filepath.Dir(dest), 0o755); err != nil {
		return err
	}
	return os.WriteFile(dest, data, 0o644)
}

// CriarSymlinks cria symlinks kn-<cliente> → binário atual no mesmo diretório do executável.
// Onda 1: apenas kn-claude.
func CriarSymlinks(opts Opcoes) error {
	exePath, err := os.Executable()
	if err != nil {
		return fmt.Errorf("localizar binário: %w", err)
	}
	exePath, err = filepath.EvalSymlinks(exePath)
	if err != nil {
		return fmt.Errorf("resolver path do binário: %w", err)
	}

	dir := filepath.Dir(exePath)
	links := []string{"kn-claude", "kn-agy", "kn-copilot", "kn-opencode"} // Onda 1 + Antigravity + Copilot + OpenCode

	for _, name := range links {
		dest := filepath.Join(dir, name)
		if info, err := os.Lstat(dest); err == nil {
			if info.Mode()&os.ModeSymlink != 0 {
				if target, err := os.Readlink(dest); err == nil && target == exePath {
					fmt.Printf("  ✓ %s já existe e está correto\n", name)
					continue
				}
			}
			if !opts.Force {
				fmt.Printf("  ! %s já existe (use --force para sobrescrever)\n", dest)
				continue
			}
			os.Remove(dest)
		}
		if err := os.Symlink(exePath, dest); err != nil {
			fmt.Printf("  ! não foi possível criar %s: %v\n", dest, err)
			fmt.Printf("    Crie manualmente: ln -sf %s %s\n", exePath, dest)
		} else {
			fmt.Printf("  ✓ %s → %s\n", name, exePath)
		}
	}
	return nil
}

func gravarMeta(vaultDir, versao string) error {
	meta := Meta{
		Versao:    versao,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
	}
	data, err := json.MarshalIndent(meta, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(vaultDir, ".meta.json"), append(data, '\n'), 0o644)
}
