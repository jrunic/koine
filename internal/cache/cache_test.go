package cache

import (
	"path/filepath"
	"testing"
)

func TestSlotIDDeterministico(t *testing.T) {
	const pasta = "/home/walter/meu-projeto"
	id1 := SlotID(pasta)
	id2 := SlotID(pasta)
	if id1 != id2 {
		t.Errorf("SlotID não determinístico: %q != %q", id1, id2)
	}
	if len(id1) != 12 {
		t.Errorf("SlotID len = %d, want 12", len(id1))
	}
}

func TestSlotIDDistinto(t *testing.T) {
	id1 := SlotID("/home/walter/proj-a")
	id2 := SlotID("/home/walter/proj-b")
	if id1 == id2 {
		t.Error("SlotID de pastas distintas não pode ser igual")
	}
}

func TestCaminhoBundle(t *testing.T) {
	tmpDir := t.TempDir()
	orig := ExportLookupCacheDir()
	SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "koine") })
	defer SetLookupCacheDir(orig)

	got := CaminhoBundle("copilot-bundles", "abc123456789")
	want := filepath.Join(tmpDir, "koine", "copilot-bundles", "abc123456789")
	if got != want {
		t.Errorf("CaminhoBundle = %q, want %q", got, want)
	}
}

func TestCaminhoArquivo(t *testing.T) {
	tmpDir := t.TempDir()
	orig := ExportLookupCacheDir()
	SetLookupCacheDir(func() string { return filepath.Join(tmpDir, "koine") })
	defer SetLookupCacheDir(orig)

	got := CaminhoArquivo("opencode-configs", "abc123456789", "json")
	want := filepath.Join(tmpDir, "koine", "opencode-configs", "abc123456789.json")
	if got != want {
		t.Errorf("CaminhoArquivo = %q, want %q", got, want)
	}
}
