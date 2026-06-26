package schema

// Escopo representa o frontmatter de ~/.config/koine/escopos/<slug>.md.
//
// Arquivo segue Selo de Jocasta: frontmatter YAML (delimitado por ---) com
// dados estruturados + corpo markdown narrativo. Leitor extrai o frontmatter.
type Escopo struct {
	Nome             string `yaml:"nome"`
	PastaReferencias string `yaml:"pasta-referencias"` // tagged path: home:<rel> | abs:<path>
	EscopoPai        string `yaml:"escopo-pai"`        // slug do escopo pai, ou ""
	Proprietario     string `yaml:"proprietario"`
}
