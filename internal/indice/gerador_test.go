package indice

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// setupDominios cria pasta de domínios-piloto e injeta via lookupFrameworkDir.
func setupDominios(t *testing.T, sinopses map[string]string) func() {
	t.Helper()
	dir := t.TempDir()
	for dom, sinopse := range sinopses {
		conteudo := "---\n" +
			"type: Domain\n" +
			"title: " + dom + "\n" +
			"origem: koine-canonico\n" +
			"sinopse: " + sinopse + "\n" +
			"---\n\n# Domínio: " + dom + "\n\n[corpo denso aqui...]\n"
		if err := os.WriteFile(filepath.Join(dir, dom+".md"), []byte(conteudo), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	original := lookupFrameworkDir
	lookupFrameworkDir = func() string { return dir }
	return func() { lookupFrameworkDir = original }
}

func TestGerarHappyPath(t *testing.T) {
	tmp := t.TempDir()

	restore := setupDominios(t, map[string]string{
		"pessoas":   "Pessoas relevantes ao escopo do mentorado.",
		"entidades": "Organizações relevantes ao escopo do mentorado.",
	})
	defer restore()

	must := func(name, content string) {
		t.Helper()
		full := filepath.Join(tmp, name)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}

	must("index.md", "---\ntipo: okf-index\n---\n# Index\n")
	must("log.md", "---\ntipo: okf-log\n---\n# Log\n")
	must("leonardo.md", "---\ntype: pessoa\ndescription: Diretor financeiro\ndominios: [pessoas]\n---\n# Leonardo\n")
	must("natasha.md", "---\ntype: pessoa\ndescription: Sócia médica\ndominios: [pessoas, entidades]\n---\n# Natasha\n")
	must("vida-imagem.md", "---\ntype: entidade\ndescription: Complexo de diagnóstico\ndominios: [entidades]\n---\n# Vida Imagem\n")
	// sanity de subpasta no happy path
	must("clientes/risoletta.md", "---\ntype: entidade\ndescription: Biscoitos artesanais\ndominios: [entidades]\n---\n# Risoletta\n")

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas", "entidades"}, &warns); err != nil {
		t.Fatalf("Gerar: %v", err)
	}

	pess, err := os.ReadFile(filepath.Join(tmp, "kn-indice-pessoas.md"))
	if err != nil {
		t.Fatal(err)
	}
	pessStr := string(pess)
	if !strings.Contains(pessStr, "## Domínio") {
		t.Errorf("kn-indice-pessoas.md sem seção Domínio:\n%s", pessStr)
	}
	if !strings.Contains(pessStr, "Pessoas relevantes ao escopo do mentorado") {
		t.Errorf("kn-indice-pessoas.md sem sinopse:\n%s", pessStr)
	}
	if !strings.Contains(pessStr, "## Entradas catalogadas no escopo") {
		t.Errorf("kn-indice-pessoas.md sem seção Entradas:\n%s", pessStr)
	}
	if !strings.Contains(pessStr, "`leonardo.md`") || !strings.Contains(pessStr, "`natasha.md`") {
		t.Errorf("kn-indice-pessoas.md faltando entradas:\n%s", pessStr)
	}

	ent, err := os.ReadFile(filepath.Join(tmp, "kn-indice-entidades.md"))
	if err != nil {
		t.Fatal(err)
	}
	entStr := string(ent)
	if !strings.Contains(entStr, "Organizações relevantes ao escopo do mentorado") {
		t.Errorf("kn-indice-entidades.md sem sinopse:\n%s", entStr)
	}
	if !strings.Contains(entStr, "`vida-imagem.md`") || !strings.Contains(entStr, "`natasha.md`") {
		t.Errorf("kn-indice-entidades.md faltando entradas:\n%s", entStr)
	}
	if !strings.Contains(entStr, "`clientes/risoletta.md`") {
		t.Errorf("kn-indice-entidades.md faltando entrada de subpasta:\n%s", entStr)
	}

	if warns.Len() != 0 {
		t.Errorf("warnings inesperados:\n%s", warns.String())
	}
}

func TestGerarAvisaSemFrontmatter(t *testing.T) {
	tmp := t.TempDir()
	restore := setupDominios(t, map[string]string{"pessoas": "Pessoas do escopo."})
	defer restore()

	if err := os.WriteFile(filepath.Join(tmp, "rascunho.md"), []byte("# sem frontmatter\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas"}, &warns); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(warns.String(), "rascunho.md") {
		t.Errorf("warnings sem rascunho.md:\n%s", warns.String())
	}
}

func TestGerarDominioAusente(t *testing.T) {
	tmp := t.TempDir()
	restore := setupDominios(t, map[string]string{})
	defer restore()

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas"}, &warns); err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile(filepath.Join(tmp, "kn-indice-pessoas.md"))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(data), "não plantado") {
		t.Errorf("kn-indice-pessoas.md sem fallback de domínio ausente:\n%s", data)
	}
	if !strings.Contains(warns.String(), "domínio \"pessoas\" não encontrado") {
		t.Errorf("warnings sem aviso de domínio ausente:\n%s", warns.String())
	}
}

func TestGerarDominioSemSinopse(t *testing.T) {
	tmp := t.TempDir()
	dir := t.TempDir()
	// cria domínio sem campo sinopse
	conteudo := "---\ntype: Domain\ntitle: pessoas\norigem: koine-canonico\n---\n\n# Pessoas\n"
	if err := os.WriteFile(filepath.Join(dir, "pessoas.md"), []byte(conteudo), 0o644); err != nil {
		t.Fatal(err)
	}
	original := lookupFrameworkDir
	lookupFrameworkDir = func() string { return dir }
	defer func() { lookupFrameworkDir = original }()

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas"}, &warns); err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile(filepath.Join(tmp, "kn-indice-pessoas.md"))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(data), "sem sinopse") {
		t.Errorf("kn-indice-pessoas.md sem fallback de sinopse ausente:\n%s", data)
	}
	if !strings.Contains(warns.String(), "sem campo `sinopse`") {
		t.Errorf("warnings sem aviso de sinopse ausente:\n%s", warns.String())
	}
}

func TestGerarVarrendoSubpastas(t *testing.T) {
	tmp := t.TempDir()
	restore := setupDominios(t, map[string]string{"pessoas": "Pessoas do escopo."})
	defer restore()

	must := func(rel, content string) {
		t.Helper()
		full := filepath.Join(tmp, rel)
		if err := os.MkdirAll(filepath.Dir(full), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(full, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}

	must("raiz.md", "---\ntype: pessoa\ndescription: Raiz\ndominios: [pessoas]\n---\n# Raiz\n")
	must("sub-a/alpha.md", "---\ntype: pessoa\ndescription: Alpha\ndominios: [pessoas]\n---\n# Alpha\n")
	must("sub-b/beta.md", "---\ntype: pessoa\ndescription: Beta\ndominios: [pessoas]\n---\n# Beta\n")

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas"}, &warns); err != nil {
		t.Fatalf("Gerar: %v", err)
	}

	data, err := os.ReadFile(filepath.Join(tmp, "kn-indice-pessoas.md"))
	if err != nil {
		t.Fatal(err)
	}
	s := string(data)
	esperados := []string{"`raiz.md`", "`sub-a/alpha.md`", "`sub-b/beta.md`"}
	for _, want := range esperados {
		if !strings.Contains(s, want) {
			t.Errorf("kn-indice-pessoas.md sem entrada %q:\n%s", want, s)
		}
	}
	if warns.Len() != 0 {
		t.Errorf("warnings inesperados:\n%s", warns.String())
	}
}

func TestGerarIgnoraOcultas(t *testing.T) {
	tmp := t.TempDir()
	restore := setupDominios(t, map[string]string{"pessoas": "Pessoas do escopo."})
	defer restore()

	// referência válida na raiz
	if err := os.WriteFile(filepath.Join(tmp, "valida.md"),
		[]byte("---\ntype: pessoa\ndescription: Válida\ndominios: [pessoas]\n---\n# Válida\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	// subpasta oculta com referência que NÃO deve entrar
	privado := filepath.Join(tmp, ".private")
	if err := os.MkdirAll(privado, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(privado, "secret.md"),
		[]byte("---\ntype: pessoa\ndescription: Secreta\ndominios: [pessoas]\n---\n# Secret\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas"}, &warns); err != nil {
		t.Fatalf("Gerar: %v", err)
	}

	data, err := os.ReadFile(filepath.Join(tmp, "kn-indice-pessoas.md"))
	if err != nil {
		t.Fatal(err)
	}
	s := string(data)
	if !strings.Contains(s, "`valida.md`") {
		t.Errorf("kn-indice-pessoas.md sem valida.md:\n%s", s)
	}
	if strings.Contains(s, "secret.md") || strings.Contains(s, ".private") {
		t.Errorf("kn-indice-pessoas.md indexou referência em pasta oculta:\n%s", s)
	}
}

func TestGerarDominioVazioComSinopse(t *testing.T) {
	tmp := t.TempDir()
	restore := setupDominios(t, map[string]string{"pessoas": "Pessoas do escopo."})
	defer restore()

	var warns bytes.Buffer
	if err := Gerar(tmp, []string{"pessoas"}, &warns); err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile(filepath.Join(tmp, "kn-indice-pessoas.md"))
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(data), "Nenhuma referência catalogada") {
		t.Errorf("kn-indice-pessoas.md sem mensagem de vazio:\n%s", data)
	}
}
