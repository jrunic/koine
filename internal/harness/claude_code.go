package harness

import (
	"bytes"
	"fmt"
	"io/fs"
	"path/filepath"
	"text/template"
	"time"
)

// ClaudeCode é o adapter do harness para o Claude Code CLI.
type ClaudeCode struct {
	// VaultFS é o filesystem do embed (pacote raiz). Injetado pelo chamador.
	VaultFS fs.FS
	// Agente é o nome da persona canônica (ex: "hermes"). Injetado pelo chamador.
	Agente string
}

func (c *ClaudeCode) Nome() string {
	return "claude-code"
}

func (c *ClaudeCode) CaminhoArquivoContexto(cwd string) string {
	return filepath.Join(cwd, "CLAUDE.md")
}

type renderData struct {
	ContextoMontado
	Timestamp string
	Agente    string
}

func (c *ClaudeCode) Renderizar(dados ContextoMontado) (Lancamento, error) {
	if c.VaultFS == nil {
		return Lancamento{}, fmt.Errorf("ClaudeCode.VaultFS não inicializado")
	}
	tmplPath := "vault/templates/claude.md.tmpl"
	if dados.Bootstrap {
		tmplPath = "vault/templates/claude-bootstrap.md.tmpl"
	}
	tmplBytes, err := fs.ReadFile(c.VaultFS, tmplPath)
	if err != nil {
		return Lancamento{}, fmt.Errorf("lendo template: %w", err)
	}

	tmpl, err := template.New("claude.md").Parse(string(tmplBytes))
	if err != nil {
		return Lancamento{}, fmt.Errorf("parse template: %w", err)
	}

	rd := renderData{
		ContextoMontado: dados,
		Timestamp:       time.Now().UTC().Format(time.RFC3339),
		Agente:          c.Agente,
	}

	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, rd); err != nil {
		return Lancamento{}, fmt.Errorf("execute template: %w", err)
	}
	conteudo := append([]byte(MarkerKoine+"\n"), buf.Bytes()...)
	return Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"CLAUDE.md": conteudo},
	}, nil
}

// Verifica em compile-time que ClaudeCode satisfaz Harness.
var _ Harness = (*ClaudeCode)(nil)
