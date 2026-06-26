package harness

import (
	"bytes"
	"fmt"
	"io/fs"
	"path/filepath"
	"text/template"
	"time"
)

// Antigravity é o adapter do harness para o Antigravity CLI (binário: agy).
// Gera GEMINI.md com sintaxe @path — idêntica ao Claude Code.
type Antigravity struct {
	// VaultFS é o filesystem do embed (pacote raiz). Injetado pelo chamador.
	VaultFS fs.FS
	// Agente é o nome da persona canônica (ex: "hermes"). Injetado pelo chamador.
	Agente string
}

func (a *Antigravity) Nome() string {
	return "antigravity"
}

func (a *Antigravity) CaminhoArquivoContexto(cwd string) string {
	return filepath.Join(cwd, "GEMINI.md")
}

func (a *Antigravity) Renderizar(dados ContextoMontado) (Lancamento, error) {
	if a.VaultFS == nil {
		return Lancamento{}, fmt.Errorf("Antigravity.VaultFS não inicializado")
	}
	tmplPath := "vault/templates/gemini.md.tmpl"
	if dados.Bootstrap {
		tmplPath = "vault/templates/gemini-bootstrap.md.tmpl"
	}
	tmplBytes, err := fs.ReadFile(a.VaultFS, tmplPath)
	if err != nil {
		return Lancamento{}, fmt.Errorf("lendo template: %w", err)
	}

	tmpl, err := template.New("gemini.md").Parse(string(tmplBytes))
	if err != nil {
		return Lancamento{}, fmt.Errorf("parse template: %w", err)
	}

	rd := struct {
		ContextoMontado
		Timestamp string
		Agente    string
	}{
		ContextoMontado: dados,
		Timestamp:       time.Now().UTC().Format(time.RFC3339),
		Agente:          a.Agente,
	}

	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, rd); err != nil {
		return Lancamento{}, fmt.Errorf("execute template: %w", err)
	}
	conteudo := append([]byte(MarkerKoine+"\n"), buf.Bytes()...)
	return Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"GEMINI.md": conteudo},
	}, nil
}

// Verifica em compile-time que Antigravity satisfaz Harness.
var _ Harness = (*Antigravity)(nil)
