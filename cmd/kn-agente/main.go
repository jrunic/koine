package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

var versao = "0.1.0"

var rootCmd = &cobra.Command{
	Use:   "kn-agente",
	Short: "Motor administrativo do Koine — instalar, mostrar, validar",
	Long: `kn-agente é o motor administrativo do Koine.

Para invocar um agente IA, use o wrapper do cliente:
  kn-claude <agente> [pasta]`,
	Args: cobra.NoArgs,
	Run: func(cmd *cobra.Command, args []string) {
		cmd.Help()
	},
}

var versaoCmd = &cobra.Command{
	Use:   "versao",
	Short: "Exibe versão do kn-agente",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("kn-agente %s\n", versao)
	},
}

func init() {
	rootCmd.PersistentFlags().BoolP("versao", "v", false, "Exibe versão do kn-agente")
	rootCmd.PersistentPreRunE = func(cmd *cobra.Command, args []string) error {
		if v, _ := cmd.Root().PersistentFlags().GetBool("versao"); v {
			fmt.Printf("kn-agente %s\n", versao)
			os.Exit(0)
		}
		return nil
	}
	rootCmd.AddCommand(versaoCmd)
}

func main() {
	nomeBin := filepath.Base(os.Args[0])
	if cliente, ok := clienteDoBinario(nomeBin); ok {
		if err := rodarWrapper(cliente, os.Args[1:]); err != nil {
			fmt.Fprintln(os.Stderr, "erro:", err)
			os.Exit(1)
		}
		return
	}
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
