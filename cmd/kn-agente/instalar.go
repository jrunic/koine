package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"golang.org/x/term"

	"github.com/jrunic/koine/internal/instalar"
	"github.com/jrunic/koine/internal/paths"
)

// stdinReader é injetável para testes do prompt interativo.
var stdinReader io.Reader = os.Stdin

var instalarCmd = &cobra.Command{
	Use:   "instalar",
	Short: "Extrai vault do binário e cria symlinks de cliente IA",
	Long: `Extrai o vault embutido no binário para ` + "`$XDG_DATA_HOME/koine/`" + ` e planta
os arquivos de domínio em ` + "`$XDG_CONFIG_HOME/koine/dominios/`" + `.
Cria symlinks kn-claude → kn-agente no mesmo diretório do binário.

Sem --force, arquivos existentes com conteúdo divergente são listados mas não sobrescritos.

Se harnesses de IA forem detectados no PATH, oferece instalar as skills kn-* interativamente.
Use --para=<harness> para instalar skills sem prompt.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		force, _ := cmd.Flags().GetBool("force")
		para, _ := cmd.Flags().GetString("para")
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

		isInterativo := term.IsTerminal(int(os.Stdin.Fd()))
		if err := instalarComDeteccao(para, isInterativo); err != nil {
			fmt.Fprintf(os.Stderr, "aviso: skills: %v\n", err)
		}

		return nil
	},
}

// instalarComDeteccao detecta harnesses no PATH e instala skills com confirmação.
// Se para != "", instala diretamente sem prompt. Se não interativo, apenas informa.
func instalarComDeteccao(para string, interativo bool) error {
	fmt.Println("\nInstalando skills de harness:")

	if para != "" {
		return instalarEImprimir(para)
	}

	detectados := detectarHarnesses()
	if len(detectados) == 0 {
		fmt.Println("  (nenhum harness detectado no PATH)")
		fmt.Println("  → Instale um cliente IA e rode: kn-agente instalar-habilidades --para=<harness>")
		return nil
	}

	if !interativo {
		fmt.Println("  Detectados:", strings.Join(detectados, ", "))
		fmt.Println("  → Modo não-interativo. Para instalar skills: kn-agente instalar-habilidades --para=<harness>")
		return nil
	}

	reader := bufio.NewReader(stdinReader)
	for _, h := range detectados {
		fmt.Printf("  %s detectado → instalar skills kn-*? [S/n]: ", h)
		resp, _ := reader.ReadString('\n')
		resp = strings.TrimSpace(strings.ToLower(resp))
		if resp == "" || resp == "s" {
			if err := instalarEImprimir(h); err != nil {
				fmt.Fprintf(os.Stderr, "  aviso: %v\n", err)
			}
		} else {
			fmt.Printf("  → Pulado. Para instalar depois: kn-agente instalar-habilidades --para=%s\n", h)
		}
	}
	return nil
}

func init() {
	instalarCmd.Flags().Bool("force", false, "Sobrescreve arquivos divergentes sem confirmação")
	instalarCmd.Flags().String("para", "", "Instala skills para harness especificado sem prompt (suportados: "+listarSuportados()+")")
	rootCmd.AddCommand(instalarCmd)
}
