package main

import (
	"os"

	"github.com/spf13/cobra"
)

var mostrarCmd = &cobra.Command{
	Use:   "mostrar <agente> <pasta>",
	Short: "Imprime o contexto resolvido em stdout (sem escrever CLAUDE.md)",
	Args:  cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		return executar(args[0], args[1], os.Stdout)
	},
}

func init() {
	rootCmd.AddCommand(mostrarCmd)
}
