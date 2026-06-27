package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
	"golang.org/x/term"

	"github.com/jrunic/koine/internal/aliases"
	"github.com/jrunic/koine/internal/instalar"
	"github.com/jrunic/koine/internal/paths"
)

// stdinReader é injetável para testes do prompt interativo.
var stdinReader io.Reader = os.Stdin

// lookupHomeInstall e lookupConfigDirInstall são injetáveis para testes
// (evitam os.Setenv, seguindo padrão do projeto).
var lookupHomeInstall = os.UserHomeDir
var lookupConfigDirInstall = paths.ConfigDir

// stderrWriter é injetável para testes — destino de warnings (default os.Stderr).
var stderrWriter io.Writer = os.Stderr

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

		fmt.Println("\nConfigurando pasta canônica:")
		if _, err := configurarPastaCanonica(vaultFS, isInterativo); err != nil {
			fmt.Fprintf(os.Stderr, "aviso: pasta canônica: %v\n", err)
		}

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

// configurarPastaCanonica conduz a fase "pasta canônica":
// prompt-com-default, cria pasta, registra alias 'koine', gera CONTEXTO.md
// a partir do embed vault/bootstrap/CONTEXTO.md.
//
// Retorna o path absoluto da pasta canônica configurada.
func configurarPastaCanonica(vaultFS fs.FS, interativo bool) (string, error) {
	home, err := lookupHomeInstall()
	if err != nil {
		return "", fmt.Errorf("home dir: %w", err)
	}
	defaultPath := filepath.Join(home, "koine")

	pastaAbs := defaultPath
	if interativo {
		fmt.Printf("Onde fica sua pasta canônica para sessões com Hermes? [~/koine]: ")
		reader := bufio.NewReader(stdinReader)
		resp, _ := reader.ReadString('\n')
		resp = strings.TrimSpace(resp)
		if resp != "" {
			pastaAbs, err = expandirPath(resp, home)
			if err != nil {
				return "", err
			}
		}
	} else {
		fmt.Println("Pasta canônica: ~/koine (default, modo não-interativo)")
	}

	// 1. Criar pasta (idempotente)
	if err := os.MkdirAll(pastaAbs, 0o755); err != nil {
		return "", fmt.Errorf("criar pasta canônica: %w", err)
	}
	fmt.Printf("✓ Pasta canônica em %s\n", pastaAbs)

	// 2. Registrar alias 'koine' (lógica de conflito no caller)
	if err := registrarAliasCanonico(pastaAbs, home); err != nil {
		fmt.Fprintf(stderrWriter, "aviso: alias: %v\n", err)
	}

	// 3. Gerar CONTEXTO.md a partir do embed
	if err := materializarContextoBootstrap(vaultFS, pastaAbs, interativo); err != nil {
		return "", fmt.Errorf("gerar CONTEXTO.md: %w", err)
	}

	return pastaAbs, nil
}

// expandirPath resolve ~, ~/, ~\, paths relativos via filepath.Abs.
func expandirPath(p, home string) (string, error) {
	if p == "~" {
		return home, nil
	}
	if strings.HasPrefix(p, "~/") || strings.HasPrefix(p, "~\\") {
		resto := strings.ReplaceAll(p[2:], "\\", string(filepath.Separator))
		return filepath.Join(home, resto), nil
	}
	return filepath.Abs(p)
}

// registrarAliasCanonico registra 'koine' → pastaAbs em aliases.json.
// Se já existe e aponta para outro path, avisa e mantém. Se mesmo path, no-op.
func registrarAliasCanonico(pastaAbs, home string) error {
	restaurar := aliases.SetConfigDirForTesting(lookupConfigDirInstall())
	defer restaurar()

	a, err := aliases.Carregar()
	if err != nil {
		return err
	}
	if existente, ok := a.Pastas["koine"]; ok {
		resolvido := existente.Path
		if existente.From == "home" {
			resolvido = filepath.Join(home, existente.Path)
		}
		if resolvido == pastaAbs {
			fmt.Println("✓ Alias 'koine' já está correto")
			return nil
		}
		fmt.Fprintf(stderrWriter,
			"aviso: alias 'koine' já aponta para %s — mantendo. Para mudar, edite %s\n",
			resolvido, aliases.ConfigPath(),
		)
		return nil
	}

	from := "abs"
	relPath := pastaAbs
	if strings.HasPrefix(pastaAbs, home+string(filepath.Separator)) {
		from = "home"
		relPath = strings.TrimPrefix(pastaAbs, home+string(filepath.Separator))
	}
	if err := aliases.Adicionar("koine", relPath, from); err != nil {
		return err
	}
	fmt.Println("✓ Alias 'koine' registrado")
	return nil
}

// materializarContextoBootstrap copia vault/bootstrap/CONTEXTO.md → <pasta>/CONTEXTO.md
// com tratamento de idempotência conforme estado atual do arquivo.
func materializarContextoBootstrap(vaultFS fs.FS, pastaAbs string, interativo bool) error {
	embedConteudo, err := fs.ReadFile(vaultFS, "vault/bootstrap/CONTEXTO.md")
	if err != nil {
		return fmt.Errorf("ler embed: %w", err)
	}
	destino := filepath.Join(pastaAbs, "CONTEXTO.md")

	atual, err := os.ReadFile(destino)
	if os.IsNotExist(err) {
		return os.WriteFile(destino, embedConteudo, 0o644)
	}
	if err != nil {
		return err
	}

	if bytes.Equal(atual, embedConteudo) {
		fmt.Println("✓ CONTEXTO.md já está em modo bootstrap (idêntico ao embed)")
		return nil
	}

	temBootstrap := strings.Contains(string(atual), "bootstrap: true")

	if !interativo {
		fmt.Fprintf(stderrWriter,
			"aviso: %s existe (modo não-interativo, preservando). Para atualizar, rode kn-agente instalar interativamente.\n",
			destino,
		)
		return nil
	}

	reader := bufio.NewReader(stdinReader)
	var sobrescrever bool
	if temBootstrap {
		fmt.Print("CONTEXTO.md em modo bootstrap detectado (conteúdo difere da versão atual). Atualizar? [Y/n]: ")
		resp, _ := reader.ReadString('\n')
		resp = strings.TrimSpace(strings.ToLower(resp))
		sobrescrever = (resp == "" || resp == "s" || resp == "y")
	} else {
		fmt.Print("CONTEXTO.md já personalizado. Sobrescrever com versão bootstrap? [y/N]: ")
		resp, _ := reader.ReadString('\n')
		resp = strings.TrimSpace(strings.ToLower(resp))
		sobrescrever = (resp == "s" || resp == "y")
	}

	if sobrescrever {
		return os.WriteFile(destino, embedConteudo, 0o644)
	}
	fmt.Println("✓ CONTEXTO.md preservado")
	return nil
}

func init() {
	instalarCmd.Flags().Bool("force", false, "Sobrescreve arquivos divergentes sem confirmação")
	instalarCmd.Flags().String("para", "", "Instala skills para harness especificado sem prompt (suportados: "+listarSuportados()+")")
	rootCmd.AddCommand(instalarCmd)
}
