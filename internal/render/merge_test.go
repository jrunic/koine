package render

import (
	"strings"
	"testing"
)

func TestStripFrontmatter(t *testing.T) {
	casos := []struct {
		nome    string
		entrada string
		want    string
	}{
		{
			nome:    "com frontmatter",
			entrada: "---\nid: 1\n---\n# Título\nCorpo aqui.",
			want:    "# Título\nCorpo aqui.",
		},
		{
			nome:    "sem frontmatter",
			entrada: "# Título\nCorpo.",
			want:    "# Título\nCorpo.",
		},
		{
			nome:    "frontmatter sem corpo",
			entrada: "---\nid: 1\n---\n",
			want:    "",
		},
		{
			nome:    "frontmatter multiplos campos",
			entrada: "---\nid: 1\ntipo: adr\ntags: [a, b]\n---\n\n# Título\nCorpo.",
			want:    "\n# Título\nCorpo.",
		},
	}
	for _, tc := range casos {
		t.Run(tc.nome, func(t *testing.T) {
			got := string(StripFrontmatter([]byte(tc.entrada)))
			if got != tc.want {
				t.Errorf("StripFrontmatter:\n got: %q\nwant: %q", got, tc.want)
			}
		})
	}
}

func TestDemoverH1(t *testing.T) {
	casos := []struct {
		nome    string
		entrada string
		want    string
	}{
		{
			nome:    "H1 demovido",
			entrada: "# Walter\nConteúdo.",
			want:    "## Walter\nConteúdo.",
		},
		{
			nome:    "sem H1 — sem mudança",
			entrada: "## Seção\nConteúdo.",
			want:    "## Seção\nConteúdo.",
		},
		{
			nome:    "apenas primeiro H1 demovido",
			entrada: "# Primeiro\n# Segundo\n",
			want:    "## Primeiro\n# Segundo\n",
		},
	}
	for _, tc := range casos {
		t.Run(tc.nome, func(t *testing.T) {
			got := string(DemoverH1([]byte(tc.entrada)))
			if got != tc.want {
				t.Errorf("DemoverH1:\n got: %q\nwant: %q", got, tc.want)
			}
		})
	}
}

func TestMescarDocumentos(t *testing.T) {
	partes := []Parte{
		{
			Secao:    "Usuário",
			Conteudo: []byte("---\nid: 1\n---\n# Walter\nConteúdo do usuário."),
		},
		{
			Secao:    "Agente",
			Conteudo: []byte("---\nid: 2\n---\n# Hermes\nConteúdo do agente."),
		},
	}

	got := string(MescarDocumentos("Sessão Koine — Copilot", partes))

	for _, want := range []string{
		"# Sessão Koine — Copilot",
		"## Usuário",
		"## Walter",
		"Conteúdo do usuário.",
		"## Agente",
		"## Hermes",
		"Conteúdo do agente.",
	} {
		if !strings.Contains(got, want) {
			t.Errorf("output não contém %q\n--- output ---\n%s", want, got)
		}
	}

	if strings.Contains(got, "id: 1") || strings.Contains(got, "id: 2") {
		t.Error("frontmatter não foi removido do output")
	}
	if strings.Contains(got, "\n# Walter") || strings.Contains(got, "\n# Hermes") {
		t.Error("H1 não foi demovido para H2")
	}
}

func TestWraparInstructions(t *testing.T) {
	conteudo := []byte("---\nid: 1\n---\n# Meu Negocio\nConteúdo do escopo.")

	got := string(WraparInstructions(conteudo))

	if !strings.HasPrefix(got, "---\napplyTo: \"**\"\n---\n") {
		t.Errorf("não começa com frontmatter Copilot:\n%s", got)
	}
	if strings.Contains(got, "id: 1") {
		t.Error("frontmatter original não foi removido")
	}
	if strings.Contains(got, "\n# Meu") {
		t.Error("H1 não foi demovido")
	}
	if !strings.Contains(got, "## Meu") {
		t.Error("H1 não foi demovido para H2")
	}
}
