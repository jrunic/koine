package harness

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"

	"github.com/jrunic/koine/internal/render"
)

// Codex é o adapter do harness para o OpenAI Codex CLI (binário: codex).
//
// Diferente de Claude/Antigravity (que usam @path includes nativos), o Codex
// NÃO resolve @path como include — ele injeta o texto literal do AGENTS.md e o
// agente decidiria ler os paths via tool call (best-effort). Por isso o adapter
// embute o CONTEÚDO inline no AGENTS.md (injeção garantida do texto literal).
//
// Para bundles acima de 32 KiB (project_doc_max_bytes default), o adapter passa
// -c project_doc_max_bytes=1048576 via ExtraArgs — override user-level, sem trust.
//
// CONTEXTO.md permanece arquivo separado no working dir; o adapter inclui um
// snapshot inline + prosa instruindo o agente a manter ./CONTEXTO.md.
type Codex struct {
	// Agente é o nome da persona canônica (ex: "hermes"), usado na nota de regeneração.
	Agente string
}

// codexProjectDocMaxBytes eleva o limite de instruções do Codex (default 32 KiB)
// para acomodar bundles Koine grandes (múltiplos índices).
const codexProjectDocMaxBytes = "1048576"

func (c *Codex) Nome() string {
	return "codex"
}

func (c *Codex) CaminhoArquivoContexto(cwd string) string {
	return filepath.Join(cwd, "AGENTS.md")
}

func (c *Codex) Renderizar(dados ContextoMontado) (Lancamento, error) {
	corpo, err := c.montarAgentsMD(dados)
	if err != nil {
		return Lancamento{}, err
	}
	conteudo := append([]byte(MarkerKoine+"\n"), corpo...)
	return Lancamento{
		ArquivosNoWorkingDir: map[string][]byte{"AGENTS.md": conteudo},
		ExtraArgs:            []string{"-c", "project_doc_max_bytes=" + codexProjectDocMaxBytes},
	}, nil
}

// montarAgentsMD concatena as seções imutáveis inline + snapshot do CONTEXTO +
// prosa de instrução. Em bootstrap, omite escopo/índices e orienta a criar CONTEXTO.md.
func (c *Codex) montarAgentsMD(dados ContextoMontado) ([]byte, error) {
	var partes []render.Parte

	add := func(secao, path string) error {
		if path == "" {
			return nil
		}
		b, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("lendo %s (%s): %w", secao, path, err)
		}
		partes = append(partes, render.Parte{Secao: secao, Conteudo: b})
		return nil
	}

	if err := add("Usuário", dados.UsuarioPath); err != nil {
		return nil, err
	}
	if err := add("Koine", dados.KoineMDPath); err != nil {
		return nil, err
	}
	if err := add("Agente", dados.AgentePath); err != nil {
		return nil, err
	}
	if !dados.Bootstrap {
		if err := add("Escopo", dados.EscopoPath); err != nil {
			return nil, err
		}
		for _, ip := range dados.IndicePaths {
			if err := add("Referências — "+dominioDe(ip), ip); err != nil {
				return nil, err
			}
		}
	}
	if dados.ContextoPath != "" {
		if b, err := os.ReadFile(dados.ContextoPath); err == nil {
			partes = append(partes, render.Parte{Secao: "Contexto da sessão (snapshot de ./CONTEXTO.md)", Conteudo: b})
		}
	}

	doc := render.MescarDocumentos("Sessão Koine — Codex", partes)

	var buf bytes.Buffer
	buf.Write(doc)
	buf.WriteString("\n\n")
	buf.WriteString(c.prosaInstrucao(dados))
	return buf.Bytes(), nil
}

// prosaInstrucao retorna o bloco final que orienta o agente sobre o arquivo mutável
// e a regeneração. Varia entre modo normal e bootstrap (sem CONTEXTO.md).
func (c *Codex) prosaInstrucao(dados ContextoMontado) string {
	regen := fmt.Sprintf("Este `AGENTS.md` é regenerado a cada sessão por `kn-codex %s .`. **Não o edite.**", c.Agente)
	if dados.Bootstrap && dados.ContextoPath == "" {
		return "## Instruções desta sessão\n\n" +
			"Esta pasta ainda não tem contexto Koine. Crie o `./CONTEXTO.md` desta pasta " +
			"com `/kn-02-mantem-catalogo` (Fluxo 3) antes de iniciar o trabalho. " +
			regen + "\n"
	}
	return "## Instruções desta sessão\n\n" +
		"O contexto mutável desta sessão vive em `./CONTEXTO.md` (no diretório atual). " +
		"Leia e mantenha esse arquivo durante o trabalho — toda persistência de contexto " +
		"entre sessões vai para ele. O conteúdo acima é um snapshot; a fonte canônica é o arquivo. " +
		regen + "\n"
}

// Verifica em compile-time que Codex satisfaz Harness.
var _ Harness = (*Codex)(nil)
