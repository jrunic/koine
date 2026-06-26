package render

import (
	"bytes"
	"strings"
)

// StripFrontmatter remove o bloco YAML de frontmatter inicial (---\n...\n---\n).
// Se não houver frontmatter ou estiver malformado, retorna o conteúdo inalterado.
func StripFrontmatter(content []byte) []byte {
	s := string(content)
	if !strings.HasPrefix(s, "---\n") {
		return content
	}
	rest := s[4:] // pula "---\n"
	idx := strings.Index(rest, "\n---")
	if idx < 0 {
		return content // frontmatter não fechado
	}
	after := rest[idx+4:] // pula "\n---"
	if strings.HasPrefix(after, "\n") {
		after = after[1:] // pula newline após fechamento
	}
	return []byte(after)
}

// DemoverH1 converte o primeiro H1 (# Título) em H2 (## Título).
// Subsequentes H1 no mesmo documento não são tocados.
func DemoverH1(content []byte) []byte {
	lines := strings.Split(string(content), "\n")
	for i, line := range lines {
		if strings.HasPrefix(line, "# ") {
			lines[i] = "#" + line // "# Foo" → "## Foo"
			break
		}
	}
	return []byte(strings.Join(lines, "\n"))
}

// Parte é uma seção de um documento mesclado: nome da seção + conteúdo bruto do arquivo.
// StripFrontmatter e DemoverH1 são aplicados automaticamente em MescarDocumentos.
type Parte struct {
	Secao    string
	Conteudo []byte
}

// MescarDocumentos concatena múltiplas partes em um único Markdown estruturado.
//
//	# <titulo>
//
//	## <partes[0].Secao>
//	<corpo sem frontmatter, H1 demovido>
//
//	## <partes[1].Secao>
//	...
func MescarDocumentos(titulo string, partes []Parte) []byte {
	var buf bytes.Buffer
	buf.WriteString("# " + titulo + "\n\n")
	for _, p := range partes {
		buf.WriteString("## " + p.Secao + "\n\n")
		body := StripFrontmatter(p.Conteudo)
		body = DemoverH1(body)
		buf.Write(bytes.TrimRight(body, "\n"))
		buf.WriteString("\n\n")
	}
	return bytes.TrimRight(buf.Bytes(), "\n")
}

// WraparInstructions produz conteúdo para um arquivo `.instructions.md` do Copilot CLI.
// Adiciona frontmatter `applyTo: "**"`, remove frontmatter original e demove H1→H2.
func WraparInstructions(conteudo []byte) []byte {
	body := StripFrontmatter(conteudo)
	body = DemoverH1(body)
	var buf bytes.Buffer
	buf.WriteString("---\napplyTo: \"**\"\n---\n\n")
	buf.Write(bytes.TrimLeft(body, "\n"))
	return buf.Bytes()
}
