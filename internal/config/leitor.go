package config

import (
	"bytes"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"

	"github.com/jrunic/koine/internal/paths"
	"github.com/jrunic/koine/internal/schema"
)

var delim = []byte("---")

// lookupConfigDir é injetável para testes — evita os.Setenv (CONTEXTO.md §158).
var lookupConfigDir = paths.ConfigDir

// LerFrontmatter abre path e separa o bloco YAML delimitado por `---` do corpo markdown.
// Retorna (frontmatter, corpo, erro). Ambos sem os delimitadores.
// Arquivo deve começar com `---\n`; ausência do bloco de abertura = erro.
func LerFrontmatter(path string) ([]byte, []byte, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, nil, err
	}
	raw = bytes.TrimPrefix(raw, []byte("\xef\xbb\xbf")) // BOM UTF-8

	if !bytes.HasPrefix(raw, append(delim, '\n')) {
		return nil, nil, fmt.Errorf("%s: não começa com bloco frontmatter (---)", path)
	}
	// Pula o primeiro `---\n`
	rest := raw[4:]
	idx := bytes.Index(rest, append([]byte("\n"), append(delim, '\n')...))
	if idx < 0 {
		// Tenta --- ao fim do arquivo sem newline final
		idx = bytes.Index(rest, append([]byte("\n"), delim...))
		if idx < 0 {
			return nil, nil, fmt.Errorf("%s: bloco frontmatter não fechado", path)
		}
		fm := rest[:idx]
		return fm, nil, nil
	}
	fm := rest[:idx]
	body := rest[idx+1+len(delim)+1:] // pula \n---\n
	return fm, body, nil
}

// AcharCaminhoUsuario retorna o path absoluto do único .md na raiz de ConfigDir().
// Fonte canônica da convenção de identificação de persona — usada por LerUsuario e
// por internal/contexto para obter o path sem re-parsear o conteúdo.
func AcharCaminhoUsuario() (string, error) {
	dir := lookupConfigDir()
	entries, err := os.ReadDir(dir)
	if err != nil {
		return "", fmt.Errorf("config dir %s: %w", dir, err)
	}
	var candidatos []string
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".md") {
			candidatos = append(candidatos, filepath.Join(dir, e.Name()))
		}
	}
	switch len(candidatos) {
	case 0:
		return "", fmt.Errorf("nenhum arquivo .md encontrado em %s — execute kn-agente instalar", dir)
	case 1:
		return candidatos[0], nil
	default:
		return "", fmt.Errorf("múltiplos arquivos .md em %s (%v) — remova os extras ou use kn-agente instalar", dir, candidatos)
	}
}

// LerUsuario lê o único .md na raiz de ConfigDir() e parseia como schema.Usuario.
func LerUsuario() (*schema.Usuario, error) {
	path, err := AcharCaminhoUsuario()
	if err != nil {
		return nil, err
	}
	return LerUsuarioPath(path)
}

// LerUsuarioPath lê um path explícito de persona (variante para testes e render).
func LerUsuarioPath(path string) (*schema.Usuario, error) {
	fm, _, err := LerFrontmatter(path)
	if err != nil {
		return nil, err
	}
	var u schema.Usuario
	if err := yaml.Unmarshal(fm, &u); err != nil {
		return nil, fmt.Errorf("%s: frontmatter inválido: %w", path, err)
	}
	return &u, nil
}

// LerEscopo lê ConfigDir()/escopos/<slug>.md e parseia em schema.Escopo.
func LerEscopo(slug string) (*schema.Escopo, error) {
	path := filepath.Join(lookupConfigDir(), "escopos", slug+".md")
	fm, _, err := LerFrontmatter(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, fmt.Errorf("escopo %q não encontrado em %s", slug, filepath.Dir(path))
		}
		return nil, err
	}
	var e schema.Escopo
	if err := yaml.Unmarshal(fm, &e); err != nil {
		return nil, fmt.Errorf("%s: frontmatter inválido: %w", path, err)
	}
	return &e, nil
}

// LerEscopoPath lê um path explícito de escopo (variante para testes e render).
func LerEscopoPath(path string) (*schema.Escopo, error) {
	fm, _, err := LerFrontmatter(path)
	if err != nil {
		return nil, err
	}
	var e schema.Escopo
	if err := yaml.Unmarshal(fm, &e); err != nil {
		return nil, fmt.Errorf("%s: frontmatter inválido: %w", path, err)
	}
	return &e, nil
}

// LerDominio lê ConfigDir()/dominios/<dom>.md e parseia frontmatter em schema.Dominio.
func LerDominio(dom string) (*schema.Dominio, error) {
	path := filepath.Join(lookupConfigDir(), "dominios", dom+".md")
	fm, _, err := LerFrontmatter(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, fmt.Errorf("dominio %q não encontrado em %s", dom, filepath.Dir(path))
		}
		return nil, err
	}
	var d schema.Dominio
	if err := yaml.Unmarshal(fm, &d); err != nil {
		return nil, fmt.Errorf("%s: frontmatter inválido: %w", path, err)
	}
	return &d, nil
}

// LerDominioPath — variante para testes.
func LerDominioPath(path string) (*schema.Dominio, error) {
	fm, _, err := LerFrontmatter(path)
	if err != nil {
		return nil, err
	}
	var d schema.Dominio
	if err := yaml.Unmarshal(fm, &d); err != nil {
		return nil, fmt.Errorf("%s: frontmatter inválido: %w", path, err)
	}
	return &d, nil
}
