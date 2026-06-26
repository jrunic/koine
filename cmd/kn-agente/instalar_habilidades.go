package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"

	"github.com/spf13/cobra"

	"github.com/jrunic/koine/internal/paths"
)

// harnessSuportados mapeia nome do harness → path relativo ao HOME da pasta de skills.
var harnessSuportados = map[string]string{
	"claude":   ".claude/skills",
	"agy":      ".gemini/antigravity-cli/skills",
	"copilot":  ".copilot/skills",
	"opencode": ".config/opencode/skills",
}

// binarioHarness mapeia nome do harness → binário de detecção no PATH.
var binarioHarness = map[string]string{
	"claude":   "claude",
	"agy":      "agy",
	"copilot":  "copilot",
	"opencode": "opencode",
}

// lookupVaultDirHab e lookupUserHomeDirHab são injetáveis para testes.
var lookupVaultDirHab = paths.VaultDir
var lookupUserHomeDirHab = os.UserHomeDir

// lookupPathFunc é injetável para testes de detecção de harness.
var lookupPathFunc = exec.LookPath

var instalarHabilidadesCmd = &cobra.Command{
	Use:   "instalar-habilidades",
	Short: "Symlinka skills kn-* do vault na pasta de skills do harness alvo",
	RunE: func(cmd *cobra.Command, args []string) error {
		para, _ := cmd.Flags().GetString("para")

		home, err := lookupUserHomeDirHab()
		if err != nil {
			return err
		}
		rel, ok := harnessSuportados[para]
		if !ok {
			return fmt.Errorf("--para=%q não suportado (suportados: %s)", para, listarSuportados())
		}
		fmt.Printf("Destino: %s\n", filepath.Join(home, rel))

		criados, jaExistiam, err := instalarHabilidadesParaHarness(para)
		if err != nil {
			return err
		}

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
			fmt.Println("Nenhuma skill kn-* encontrada em", filepath.Join(lookupVaultDirHab(), "habilidades"))
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

// instalarHabilidadesParaHarness symlinka skills kn-* do vault no diretório de
// skills do harness alvo. Retorna listas de skills criados e já existentes.
// Idempotente: symlinks corretos são silenciosamente ignorados.
func instalarHabilidadesParaHarness(harness string) (criados, jaExistiam []string, err error) {
	rel, ok := harnessSuportados[harness]
	if !ok {
		return nil, nil, fmt.Errorf("%q não suportado (suportados: %s)", harness, listarSuportados())
	}
	home, err := lookupUserHomeDirHab()
	if err != nil {
		return nil, nil, fmt.Errorf("home dir: %w", err)
	}
	destDir := filepath.Join(home, rel)
	if err := os.MkdirAll(destDir, 0o755); err != nil {
		return nil, nil, fmt.Errorf("criar %s: %w", destDir, err)
	}
	habilidadesDir := filepath.Join(lookupVaultDirHab(), "habilidades")
	entries, err := os.ReadDir(habilidadesDir)
	if err != nil {
		return nil, nil, fmt.Errorf("ler %s: %w (rode `kn-agente instalar` primeiro)", habilidadesDir, err)
	}
	for _, e := range entries {
		if !e.IsDir() || !strings.HasPrefix(e.Name(), "kn-") {
			continue
		}
		src := filepath.Join(habilidadesDir, e.Name())
		dst := filepath.Join(destDir, e.Name())
		if info, statErr := os.Lstat(dst); statErr == nil {
			if info.Mode()&os.ModeSymlink != 0 {
				if target, _ := os.Readlink(dst); target == src {
					jaExistiam = append(jaExistiam, e.Name())
					continue
				}
			}
			return nil, nil, fmt.Errorf("%s já existe e não é symlink para o vault — remova manualmente", dst)
		}
		if linkErr := os.Symlink(src, dst); linkErr != nil {
			return nil, nil, fmt.Errorf("symlink %s → %s: %w", dst, src, linkErr)
		}
		criados = append(criados, e.Name())
	}
	sort.Strings(criados)
	sort.Strings(jaExistiam)
	return criados, jaExistiam, nil
}

// detectarHarnesses retorna harnesses cujo binário está no PATH, em ordem alfabética.
func detectarHarnesses() []string {
	var detectados []string
	for harness, bin := range binarioHarness {
		if _, err := lookupPathFunc(bin); err == nil {
			detectados = append(detectados, harness)
		}
	}
	sort.Strings(detectados)
	return detectados
}

// instalarEImprimir instala skills para um harness e imprime o resultado formatado.
// Usado tanto por instalarComDeteccao (instalar.go) quanto por testes.
func instalarEImprimir(harness string) error {
	criados, jaExistiam, err := instalarHabilidadesParaHarness(harness)
	if err != nil {
		return err
	}
	home, _ := lookupUserHomeDirHab()
	fmt.Printf("  Skills para %s (%s):\n", harness, filepath.Join(home, harnessSuportados[harness]))
	for _, n := range criados {
		fmt.Println("    +", n)
	}
	for _, n := range jaExistiam {
		fmt.Println("    =", n)
	}
	if len(criados)+len(jaExistiam) == 0 {
		fmt.Println("    (nenhuma skill kn-* encontrada em vault)")
	}
	return nil
}

func init() {
	instalarHabilidadesCmd.Flags().String("para", "", "Harness alvo (suportados: "+listarSuportados()+")")
	_ = instalarHabilidadesCmd.MarkFlagRequired("para")
	rootCmd.AddCommand(instalarHabilidadesCmd)
}
