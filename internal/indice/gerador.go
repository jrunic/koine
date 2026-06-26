package indice

import (
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"gopkg.in/yaml.v3"

	"github.com/jrunic/koine/internal/config"
	"github.com/jrunic/koine/internal/paths"
)

// FrontmatterRef extrai apenas o que precisamos de cada referência catalogada.
type FrontmatterRef struct {
	Description string   `yaml:"description"`
	Dominios    []string `yaml:"dominios"`
}

// Entrada é uma linha do kn-indice-<dom>.md.
type Entrada struct {
	Path        string
	Description string
}

// Gerar varre pastaRef e materializa kn-indice-<dom>.md para cada domínio em domsDeclarados.
// O header de cada kn-indice embute o corpo do framework do domínio
// (lido de ConfigDir()/dominios/<dom>.md), seguido da lista de entradas catalogadas.
//
// Erros não-fatais (arquivo sem frontmatter, framework ausente) são emitidos em warnings.
func Gerar(pastaRef string, domsDeclarados []string, warnings io.Writer) error {
	porDominio := make(map[string][]Entrada)
	for _, d := range domsDeclarados {
		porDominio[d] = nil
	}

	var semFM []string
	err := filepath.WalkDir(pastaRef, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			if path == pastaRef {
				return nil
			}
			if strings.HasPrefix(d.Name(), ".") {
				return fs.SkipDir
			}
			return nil
		}
		name := d.Name()
		if !strings.HasSuffix(name, ".md") {
			return nil
		}
		rel, _ := filepath.Rel(pastaRef, path)
		rel = filepath.ToSlash(rel)
		// contratos OKF só são ignorados na raiz
		if !strings.Contains(rel, "/") {
			if name == "index.md" || name == "log.md" || strings.HasPrefix(name, "kn-indice-") {
				return nil
			}
		}
		fm, _, err := config.LerFrontmatter(path)
		if err != nil {
			semFM = append(semFM, rel)
			return nil
		}
		var ref FrontmatterRef
		if err := yaml.Unmarshal(fm, &ref); err != nil {
			fmt.Fprintf(warnings, "frontmatter inválido em %s: %v\n", rel, err)
			return nil
		}
		for _, dom := range ref.Dominios {
			if _, ok := porDominio[dom]; !ok {
				continue
			}
			porDominio[dom] = append(porDominio[dom], Entrada{Path: rel, Description: ref.Description})
		}
		return nil
	})
	if err != nil {
		return fmt.Errorf("varrer pasta-referências %s: %w", pastaRef, err)
	}

	for dom, entradas := range porDominio {
		sort.Slice(entradas, func(i, j int) bool { return entradas[i].Path < entradas[j].Path })
		sinopse := lerSinopse(dom, warnings)
		if err := escreverIndice(pastaRef, dom, sinopse, entradas); err != nil {
			return err
		}
	}

	if len(semFM) > 0 {
		fmt.Fprintf(warnings, "arquivos sem frontmatter OKF em %s:\n", pastaRef)
		sort.Strings(semFM)
		for _, n := range semFM {
			fmt.Fprintf(warnings, "  - %s\n", n)
		}
	}
	return nil
}

// lookupFrameworkDir permite override em testes sem tocar no XDG real.
var lookupFrameworkDir = func() string { return filepath.Join(paths.ConfigDir(), "dominios") }

func lerSinopse(dom string, warnings io.Writer) string {
	path := filepath.Join(lookupFrameworkDir(), dom+".md")
	if _, err := os.Stat(path); err != nil {
		fmt.Fprintf(warnings, "domínio %q não encontrado em %s (rode `kn-agente instalar` ou /kn-02 fluxo dominio)\n", dom, path)
		return fmt.Sprintf("_Domínio `%s` não plantado. Rode `kn-agente instalar` ou `/kn-02-mantem-catalogo` (fluxo dominio)._", dom)
	}
	d, err := config.LerDominioPath(path)
	if err != nil {
		fmt.Fprintf(warnings, "domínio %q em %s: %v\n", dom, path, err)
		return fmt.Sprintf("_Domínio `%s` em %s não pôde ser lido._", dom, path)
	}
	if d.Sinopse == "" {
		fmt.Fprintf(warnings, "domínio %q em %s sem campo `sinopse` no frontmatter\n", dom, path)
		return fmt.Sprintf("_Domínio `%s` sem sinopse — corrija o frontmatter de %s._", dom, path)
	}
	return d.Sinopse
}

func escreverIndice(pastaRef, dom, sinopse string, entradas []Entrada) error {
	dest := filepath.Join(pastaRef, "kn-indice-"+dom+".md")
	var sb strings.Builder
	fmt.Fprintf(&sb, "---\n")
	fmt.Fprintf(&sb, "tipo: indice\n")
	fmt.Fprintf(&sb, "dominio: %s\n", dom)
	fmt.Fprintf(&sb, "gerado: %s\n", time.Now().UTC().Format(time.RFC3339))
	fmt.Fprintf(&sb, "entradas: %d\n", len(entradas))
	fmt.Fprintf(&sb, "---\n\n")

	fmt.Fprintf(&sb, "## Domínio\n\n")
	fmt.Fprintf(&sb, "%s\n", sinopse)

	fmt.Fprintf(&sb, "## Entradas catalogadas no escopo\n\n")
	if len(entradas) == 0 {
		fmt.Fprintf(&sb, "_Nenhuma referência catalogada neste domínio._\n")
	} else {
		for _, e := range entradas {
			if e.Description != "" {
				fmt.Fprintf(&sb, "- `%s` — %s\n", e.Path, e.Description)
			} else {
				fmt.Fprintf(&sb, "- `%s`\n", e.Path)
			}
		}
	}
	return os.WriteFile(dest, []byte(sb.String()), 0o644)
}
