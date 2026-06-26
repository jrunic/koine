package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/spf13/cobra"

	"github.com/jrunic/koine/internal/paths"
)

var harnessSuportados = map[string]string{
	"claude": ".claude/skills",
}

var instalarHabilidadesCmd = &cobra.Command{
	Use:   "instalar-habilidades",
	Short: "Symlinka skills kn-* do vault na pasta de skills do harness alvo",
	RunE: func(cmd *cobra.Command, args []string) error {
		para, _ := cmd.Flags().GetString("para")
		if para == "" {
			return fmt.Errorf("--para é obrigatório (suportados: %s)", listarSuportados())
		}
		rel, ok := harnessSuportados[para]
		if !ok {
			return fmt.Errorf("--para=%q não suportado (suportados: %s)", para, listarSuportados())
		}

		home, err := os.UserHomeDir()
		if err != nil {
			return err
		}
		destDir := filepath.Join(home, rel)
		if err := os.MkdirAll(destDir, 0o755); err != nil {
			return fmt.Errorf("criar %s: %w", destDir, err)
		}

		habilidadesDir := filepath.Join(paths.VaultDir(), "habilidades")
		entries, err := os.ReadDir(habilidadesDir)
		if err != nil {
			return fmt.Errorf("ler %s: %w (rode `kn-agente instalar` primeiro)", habilidadesDir, err)
		}

		var criados, jaExistiam []string
		for _, e := range entries {
			if !e.IsDir() || !strings.HasPrefix(e.Name(), "kn-") {
				continue
			}
			src := filepath.Join(habilidadesDir, e.Name())
			dst := filepath.Join(destDir, e.Name())

			if info, err := os.Lstat(dst); err == nil {
				if info.Mode()&os.ModeSymlink != 0 {
					target, _ := os.Readlink(dst)
					if target == src {
						jaExistiam = append(jaExistiam, e.Name())
						continue
					}
				}
				return fmt.Errorf("%s já existe e não é symlink para o vault — remova manualmente", dst)
			}
			if err := os.Symlink(src, dst); err != nil {
				return fmt.Errorf("symlink %s → %s: %w", dst, src, err)
			}
			criados = append(criados, e.Name())
		}

		sort.Strings(criados)
		sort.Strings(jaExistiam)
		fmt.Printf("Destino: %s\n", destDir)
		if len(criados) > 0 {
			fmt.Println("Symlinks criados:")
			for _, n := range criados {
				fmt.Println("  +", n)
			}
		}
		if len(jaExistiam) > 0 {
			fmt.Println("Já existiam (sem ação):")
			for _, n := range jaExistiam {
				fmt.Println("  =", n)
			}
		}
		if len(criados)+len(jaExistiam) == 0 {
			fmt.Println("Nenhuma skill kn-* encontrada em", habilidadesDir)
		}
		return nil
	},
}

func listarSuportados() string {
	keys := make([]string, 0, len(harnessSuportados))
	for k := range harnessSuportados {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return strings.Join(keys, ", ")
}

func init() {
	instalarHabilidadesCmd.Flags().String("para", "", "Harness alvo (suportados: "+listarSuportados()+")")
	_ = instalarHabilidadesCmd.MarkFlagRequired("para")
	rootCmd.AddCommand(instalarHabilidadesCmd)
}
