package main

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// helpers de injeção para os testes desta suite

func injetarVaultEHome(t *testing.T) (vaultDir, homeDir string) {
	t.Helper()
	vaultDir = t.TempDir()
	homeDir = t.TempDir()

	origVault := lookupVaultDirHab
	origHome := lookupUserHomeDirHab
	t.Cleanup(func() {
		lookupVaultDirHab = origVault
		lookupUserHomeDirHab = origHome
	})
	lookupVaultDirHab = func() string { return vaultDir }
	lookupUserHomeDirHab = func() (string, error) { return homeDir, nil }
	return
}

func criarSkillFake(t *testing.T, habilidadesDir, nome string) string {
	t.Helper()
	dir := filepath.Join(habilidadesDir, nome)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "SKILL.md"), []byte("# skill"), 0o644); err != nil {
		t.Fatal(err)
	}
	return dir
}

// --- instalarHabilidadesParaHarness ---

func TestInstalarHabilidadesParaHarness_CriaSymlink(t *testing.T) {
	vaultDir, homeDir := injetarVaultEHome(t)
	habilidadesDir := filepath.Join(vaultDir, "habilidades")
	skillSrc := criarSkillFake(t, habilidadesDir, "kn-01-recebe-usuario")

	criados, jaExistiam, err := instalarHabilidadesParaHarness("claude")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if len(criados) != 1 || criados[0] != "kn-01-recebe-usuario" {
		t.Errorf("criados = %v, want [kn-01-recebe-usuario]", criados)
	}
	if len(jaExistiam) != 0 {
		t.Errorf("jaExistiam = %v, want []", jaExistiam)
	}

	dst := filepath.Join(homeDir, ".claude", "skills", "kn-01-recebe-usuario")
	info, err := os.Lstat(dst)
	if err != nil {
		t.Fatalf("symlink não criado em %s: %v", dst, err)
	}
	if info.Mode()&os.ModeSymlink == 0 {
		t.Fatal("esperado symlink, encontrado arquivo/dir regular")
	}
	alvo, _ := os.Readlink(dst)
	if alvo != skillSrc {
		t.Errorf("alvo do symlink = %q, want %q", alvo, skillSrc)
	}
}

func TestInstalarHabilidadesParaHarness_Idempotente(t *testing.T) {
	vaultDir, _ := injetarVaultEHome(t)
	criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

	if _, _, err := instalarHabilidadesParaHarness("claude"); err != nil {
		t.Fatalf("primeira chamada: %v", err)
	}
	if _, _, err := instalarHabilidadesParaHarness("claude"); err != nil {
		t.Fatalf("segunda chamada (idempotente): %v", err)
	}
}

func TestInstalarHabilidadesParaHarness_SegundaChamadaReportaJaExistia(t *testing.T) {
	vaultDir, _ := injetarVaultEHome(t)
	criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

	instalarHabilidadesParaHarness("claude") // primeira
	_, jaExistiam, err := instalarHabilidadesParaHarness("claude")
	if err != nil {
		t.Fatalf("segunda chamada: %v", err)
	}
	if len(jaExistiam) != 1 || jaExistiam[0] != "kn-01-recebe-usuario" {
		t.Errorf("jaExistiam = %v, want [kn-01-recebe-usuario]", jaExistiam)
	}
}

func TestInstalarHabilidadesParaHarness_HarnessInvalido(t *testing.T) {
	injetarVaultEHome(t)
	_, _, err := instalarHabilidadesParaHarness("inexistente")
	if err == nil {
		t.Fatal("esperado erro para harness desconhecido, got nil")
	}
}

func TestInstalarHabilidadesParaHarness_IgnoraNaoKn(t *testing.T) {
	vaultDir, homeDir := injetarVaultEHome(t)
	habilidadesDir := filepath.Join(vaultDir, "habilidades")
	criarSkillFake(t, habilidadesDir, "kn-01-recebe-usuario")
	criarSkillFake(t, habilidadesDir, "outro-dir-ignorado") // sem prefixo kn-

	criados, _, err := instalarHabilidadesParaHarness("claude")
	if err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}
	if len(criados) != 1 {
		t.Errorf("criados = %v, esperado só kn-01", criados)
	}
	dst := filepath.Join(homeDir, ".claude", "skills", "outro-dir-ignorado")
	if _, err := os.Lstat(dst); err == nil {
		t.Error("diretório sem prefixo kn- não deveria ter sido linkado")
	}
}

func TestInstalarHabilidadesParaHarness_TodosOsHarnesses(t *testing.T) {
	destinos := map[string]string{
		"claude":   ".claude/skills",
		"agy":      ".gemini/antigravity-cli/skills",
		"copilot":  ".copilot/skills",
		"opencode": ".config/opencode/skills",
	}
	for harness, rel := range destinos {
		t.Run(harness, func(t *testing.T) {
			vaultDir, homeDir := injetarVaultEHome(t)
			criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

			criados, _, err := instalarHabilidadesParaHarness(harness)
			if err != nil {
				t.Fatalf("harness %s: %v", harness, err)
			}
			if len(criados) != 1 {
				t.Fatalf("harness %s: criados = %v", harness, criados)
			}
			dst := filepath.Join(homeDir, filepath.FromSlash(rel), "kn-01-recebe-usuario")
			if _, err := os.Lstat(dst); err != nil {
				t.Errorf("harness %s: symlink não encontrado em %s", harness, dst)
			}
		})
	}
}

// --- detectarHarnesses ---

func TestDetectarHarnesses_ClaudeNoPath(t *testing.T) {
	orig := lookupPathFunc
	defer func() { lookupPathFunc = orig }()
	lookupPathFunc = func(name string) (string, error) {
		if name == "claude" {
			return "/usr/bin/claude", nil
		}
		return "", errors.New("not found")
	}

	got := detectarHarnesses()
	if len(got) != 1 || got[0] != "claude" {
		t.Fatalf("detectarHarnesses() = %v, want [claude]", got)
	}
}

func TestDetectarHarnesses_Nenhum(t *testing.T) {
	orig := lookupPathFunc
	defer func() { lookupPathFunc = orig }()
	lookupPathFunc = func(name string) (string, error) {
		return "", errors.New("not found")
	}

	got := detectarHarnesses()
	if len(got) != 0 {
		t.Fatalf("detectarHarnesses() = %v, want []", got)
	}
}

func TestDetectarHarnesses_Ordenado(t *testing.T) {
	orig := lookupPathFunc
	defer func() { lookupPathFunc = orig }()
	lookupPathFunc = func(name string) (string, error) {
		return "/usr/bin/" + name, nil // todos encontrados
	}

	got := detectarHarnesses()
	if len(got) != 4 {
		t.Fatalf("esperado 4 harnesses, got %v", got)
	}
	for i := 1; i < len(got); i++ {
		if got[i] < got[i-1] {
			t.Errorf("resultado não está ordenado: %v", got)
		}
	}
}

// --- instalarComDeteccao ---

func TestInstalarComDeteccao_NaoInterativoNaoInstala(t *testing.T) {
	vaultDir, homeDir := injetarVaultEHome(t)
	criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

	origPath := lookupPathFunc
	defer func() { lookupPathFunc = origPath }()
	lookupPathFunc = func(name string) (string, error) {
		if name == "claude" {
			return "/usr/bin/claude", nil
		}
		return "", errors.New("not found")
	}

	if err := instalarComDeteccao("", false); err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}

	dst := filepath.Join(homeDir, ".claude", "skills", "kn-01-recebe-usuario")
	if _, err := os.Lstat(dst); err == nil {
		t.Error("modo não-interativo sem --para não deveria criar symlinks")
	}
}

func TestInstalarComDeteccao_ComParaIgnoraInterativo(t *testing.T) {
	vaultDir, homeDir := injetarVaultEHome(t)
	criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

	if err := instalarComDeteccao("claude", false); err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}

	dst := filepath.Join(homeDir, ".claude", "skills", "kn-01-recebe-usuario")
	if _, err := os.Lstat(dst); err != nil {
		t.Errorf("--para deve criar symlink mesmo em modo não-interativo: %v", err)
	}
}

func TestInstalarComDeteccao_NenhumHarnessDetectado(t *testing.T) {
	injetarVaultEHome(t)

	origPath := lookupPathFunc
	defer func() { lookupPathFunc = origPath }()
	lookupPathFunc = func(name string) (string, error) {
		return "", errors.New("not found")
	}

	if err := instalarComDeteccao("", true); err != nil {
		t.Fatalf("zero harnesses não deve retornar erro: %v", err)
	}
}

func TestInstalarComDeteccao_InterativoConfirma(t *testing.T) {
	vaultDir, homeDir := injetarVaultEHome(t)
	criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

	origPath := lookupPathFunc
	origStdin := stdinReader
	defer func() {
		lookupPathFunc = origPath
		stdinReader = origStdin
	}()
	lookupPathFunc = func(name string) (string, error) {
		if name == "claude" {
			return "/usr/bin/claude", nil
		}
		return "", errors.New("not found")
	}
	stdinReader = strings.NewReader("s\n")

	if err := instalarComDeteccao("", true); err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}

	dst := filepath.Join(homeDir, ".claude", "skills", "kn-01-recebe-usuario")
	if _, err := os.Lstat(dst); err != nil {
		t.Errorf("confirmação 's' deveria criar symlink: %v", err)
	}
}

func TestInstalarComDeteccao_InterativoRecusa(t *testing.T) {
	vaultDir, homeDir := injetarVaultEHome(t)
	criarSkillFake(t, filepath.Join(vaultDir, "habilidades"), "kn-01-recebe-usuario")

	origPath := lookupPathFunc
	origStdin := stdinReader
	defer func() {
		lookupPathFunc = origPath
		stdinReader = origStdin
	}()
	lookupPathFunc = func(name string) (string, error) {
		if name == "claude" {
			return "/usr/bin/claude", nil
		}
		return "", errors.New("not found")
	}
	stdinReader = strings.NewReader("n\n")

	if err := instalarComDeteccao("", true); err != nil {
		t.Fatalf("erro inesperado: %v", err)
	}

	dst := filepath.Join(homeDir, ".claude", "skills", "kn-01-recebe-usuario")
	if _, err := os.Lstat(dst); err == nil {
		t.Error("recusa 'n' não deveria criar symlink")
	}
}
