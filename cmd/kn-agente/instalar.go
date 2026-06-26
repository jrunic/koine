package main

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"

	"github.com/jrunic/koine/internal/instalar"
	"github.com/jrunic/koine/internal/paths"
)

var instalarCmd = &cobra.Command{
	Use:   "instalar",
	Short: "Extrai vault do binário e cria symlinks de cliente IA",
	Long: `Extrai o vault embutido no binário para ` + "`$XDG_DATA_HOME/koine/`" + ` e planta
os arquivos de domínio em ` + "`$XDG_CONFIG_HOME/koine/dominios/`" + `.
Cria symlinks kn-claude → kn-agente no mesmo diretório do binário.

Sem --force, arquivos existentes com conteúdo divergente são listados mas não sobrescritos.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		force, _ := cmd.Flags().GetBool("force")
		opts := instalar.Opcoes{Force: force}

		fmt.Printf("Instalando vault em %s\n", paths.VaultDir())
		fmt.Printf("Plantando domínios em %s/dominios\n", paths.ConfigDir())

		if err := instalar.Instalar(vaultFS, versao, opts); err != nil {
			return fmt.Errorf("instalar: %w", err)
		}
		fmt.Println("Instalação concluída.")

		fmt.Println("\nCriando symlinks de cliente IA:")
		if err := instalar.CriarSymlinks(opts); err != nil {
			fmt.Fprintf(os.Stderr, "aviso: symlinks: %v\n", err)
		}
		return nil
	},
}

func init() {
	instalarCmd.Flags().Bool("force", false, "Sobrescreve arquivos divergentes sem confirmação")
	rootCmd.AddCommand(instalarCmd)
}
