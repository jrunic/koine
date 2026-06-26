package schema

// Dominio representa o frontmatter de ~/.config/koine/dominios/<dom>.md.
//
// Arquivo segue Ficha Koine: frontmatter YAML (delimitado por ---) com dados
// estruturados + corpo markdown narrativo. O corpo é denso (documentação
// completa para skills); o campo `sinopse` é o que o gerador de kn-indice
// embute em runtime no header de cada kn-indice-<dom>.md.
type Dominio struct {
	Type        string `yaml:"type"`
	Title       string `yaml:"title"`
	Description string `yaml:"description"`
	Origem      string `yaml:"origem"`  // koine-canonico | usuario
	Sinopse     string `yaml:"sinopse"` // 1-3 frases — embutido no kn-indice em runtime
}
