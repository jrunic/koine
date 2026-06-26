package pasta

import (
	"bufio"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/jrunic/koine/internal/aliases"
)

// lookupAliases, lookupCandidatos e lookupHomeDir são injetáveis para testes
// (CONTEXTO.md §158).
var lookupAliases = func() (aliases.Aliases, error) { return aliases.Carregar() }
var lookupCandidatos = listarCandidatos
var lookupHomeDir = os.UserHomeDir

// maxProfundidade limita o walk de $HOME — pastas mais profundas que isso são
// puladas. Valor escolhido empiricamente: cobre o uso típico do Orlando
// (~/jedi-brain/<tipo>/<projeto>/<subpasta>) com folga.
const maxProfundidade = 7

// pastasIgnoradas — basenames cujo conteúdo é cache/build/artefato e nunca
// faz sentido como pasta de trabalho. Lista é dado, não código — extender
// conforme necessidade.
var pastasIgnoradas = map[string]bool{
	"node_modules": true,
	"vendor":       true,
	"__pycache__":  true,
	"target":       true,
	"build":        true,
	"dist":         true,
	"venv":         true,
	"coverage":     true,
	"Library":      true, // macOS
}

// Resolver resolve arg para path absoluto.
// Ordem: "" → pwd | alias exato → path direto → fuzzy+menu.
func Resolver(arg string) (string, error) {
	if arg == "" {
		return os.Getwd()
	}

	a, err := lookupAliases()
	if err != nil {
		return "", err
	}

	// (1) alias exato
	if p, ok := aliases.Resolver(a, arg); ok {
		return p, nil
	}

	// (2) path direto
	if info, err := os.Stat(arg); err == nil && info.IsDir() {
		return filepath.Abs(arg)
	}

	// (3) fuzzy + menu interativo
	candidatos := lookupCandidatos()
	filtrados := fuzzyFilter(arg, candidatos)
	escolha, err := escolherMenu(filtrados)
	if err != nil {
		return "", fmt.Errorf("'%s' não resolveu para nenhuma pasta: %w", arg, err)
	}

	oferecerSalvarAlias(arg, escolha)
	return escolha, nil
}

// listarCandidatos varre $HOME e retorna pastas elegíveis como pasta de
// trabalho para o fuzzy. Skip agressivo de dotfiles e build dirs comuns;
// limite de profundidade controla custo do walk em homes grandes.
//
// Pasta-referências dos escopos NÃO entra no universo — é memória de longa
// duração, raramente alvo direto de `kn-claude` (decisão da sessão da Leia,
// 2026-06-22).
func listarCandidatos() []string {
	home, err := lookupHomeDir()
	if err != nil {
		return nil
	}
	var result []string
	_ = filepath.WalkDir(home, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil // ignora dir inacessível (permission denied etc.)
		}
		if !d.IsDir() {
			return nil
		}
		if path == home {
			return nil
		}
		rel, _ := filepath.Rel(home, path)
		if profundidade(rel) > maxProfundidade {
			return fs.SkipDir
		}
		name := d.Name()
		if strings.HasPrefix(name, ".") || pastasIgnoradas[name] {
			return fs.SkipDir
		}
		result = append(result, path)
		return nil
	})
	return result
}

// profundidade retorna o número de componentes de path em rel
// (rel relativo a $HOME). "." e "" devolvem 0.
func profundidade(rel string) int {
	if rel == "." || rel == "" {
		return 0
	}
	return strings.Count(rel, string(filepath.Separator)) + 1
}

// fuzzyFilter retorna candidatos cujo basename compartilha ao menos uma
// palavra (split por "-") com arg.
func fuzzyFilter(arg string, candidatos []string) []string {
	palavras := strings.Split(strings.ToLower(strings.TrimSpace(arg)), "-")
	var matched []string
	for _, c := range candidatos {
		base := strings.ToLower(filepath.Base(c))
		partes := strings.Split(base, "-")
	outer:
		for _, pw := range palavras {
			if pw == "" {
				continue
			}
			for _, dp := range partes {
				if pw == dp {
					matched = append(matched, c)
					break outer
				}
			}
		}
	}
	return matched
}

// escolherMenu apresenta menu fzf (se disponível) ou numerado.
// Com 1 candidato, retorna diretamente.
func escolherMenu(candidatos []string) (string, error) {
	switch len(candidatos) {
	case 0:
		return "", fmt.Errorf("nenhuma pasta candidata encontrada")
	case 1:
		return candidatos[0], nil
	}
	if fzfPath, err := exec.LookPath("fzf"); err == nil {
		return escolherFzf(fzfPath, candidatos)
	}
	return escolherNumerado(candidatos)
}

func escolherFzf(fzfPath string, candidatos []string) (string, error) {
	cmd := exec.Command(fzfPath, "--prompt=Pasta> ", "--height=40%")
	cmd.Stdin = strings.NewReader(strings.Join(candidatos, "\n"))
	cmd.Stderr = os.Stderr
	out, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("fzf cancelado")
	}
	escolha := strings.TrimSpace(string(out))
	if escolha == "" {
		return "", fmt.Errorf("nenhuma pasta selecionada")
	}
	return escolha, nil
}

func escolherNumerado(candidatos []string) (string, error) {
	for i, c := range candidatos {
		fmt.Fprintf(os.Stdout, "%3d) %s\n", i+1, c)
	}
	fmt.Fprint(os.Stdout, "Número: ")
	scanner := bufio.NewScanner(os.Stdin)
	if !scanner.Scan() {
		return "", fmt.Errorf("entrada cancelada")
	}
	var n int
	if _, err := fmt.Sscanf(scanner.Text(), "%d", &n); err != nil || n < 1 || n > len(candidatos) {
		return "", fmt.Errorf("seleção inválida")
	}
	return candidatos[n-1], nil
}

// oferecerSalvarAlias pergunta se deve persistir arg → pasta em aliases.json.
func oferecerSalvarAlias(arg, pasta string) {
	fmt.Fprintf(os.Stdout, "Salvar '%s' → '%s' em aliases.json? [S/n] ", arg, pasta)
	scanner := bufio.NewScanner(os.Stdin)
	if !scanner.Scan() {
		return
	}
	resp := strings.TrimSpace(scanner.Text())
	if resp == "n" || resp == "N" {
		return
	}

	from, rel := "abs", pasta
	if home, err := os.UserHomeDir(); err == nil && strings.HasPrefix(pasta, home+string(filepath.Separator)) {
		rel = strings.TrimPrefix(pasta, home+string(filepath.Separator))
		from = "home"
	}
	if err := aliases.Adicionar(arg, rel, from); err != nil {
		fmt.Fprintf(os.Stderr, "aviso: não foi possível salvar alias: %v\n", err)
	} else {
		fmt.Fprintf(os.Stdout, "Alias '%s' salvo.\n", arg)
	}
}
