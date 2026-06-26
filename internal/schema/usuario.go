package schema

// Usuario representa o frontmatter de ~/.config/koine/<nome>.md (persona operacional do mentee).
//
// Arquivo segue Selo de Jocasta: frontmatter YAML (delimitado por ---) com
// dados estruturados + corpo markdown narrativo. Leitor extrai o frontmatter.
type Usuario struct {
	Nome     string `yaml:"nome"`
	Idioma   string `yaml:"idioma"`
	Papel    string `yaml:"papel"`
	Timezone string `yaml:"timezone"`
}
