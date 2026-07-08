import os

from koine import skills
from tests import _parity

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT = os.path.join(REPO, "vault")


def _skills_tree(base: str) -> dict:
    """{nome-do-skill: arvore-de-arquivos}, comparando o DIR INTEIRO (não só
    SKILL.md). Segue symlinks (Go) ou lê cópias (Python) — _parity.arvore abre
    os arquivos, então resolve o symlink do Go transparentemente."""
    out = {}
    if not os.path.isdir(base):
        return out
    for nome in sorted(os.listdir(base)):
        d = os.path.join(base, nome)
        if os.path.isdir(d):
            out[nome] = _parity.arvore(d)
    return out


def test_skills_claude_bate_com_go(tmp_path, monkeypatch):
    # Go: instalar (popula vault) + instalar-habilidades --para=claude
    home_go = str(tmp_path / "go"); os.makedirs(home_go)
    _parity.instalar_go(home_go)
    _parity.instalar_habilidades_go(home_go, "claude")

    # Python: instalar (popula vault) + skills.instalar_habilidades("claude")
    home_py = str(tmp_path / "py"); os.makedirs(home_py)
    monkeypatch.setenv("HOME", home_py)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    from koine import instalar
    instalar.extrair(VAULT, "0.4.0-dev")
    div = skills.instalar_habilidades("claude")
    assert div == []                                # install limpo: nada divergente

    go = _skills_tree(os.path.join(home_go, ".claude", "skills"))
    py = _skills_tree(os.path.join(home_py, ".claude", "skills"))
    assert set(py) == set(go)                       # mesmo conjunto de kn-*
    assert py == go                                 # mesma ÁRVORE por skill (não só SKILL.md)
    assert set(py)                                  # não-vazio


def test_divergente_preservado_e_reportado(tmp_path, monkeypatch):
    # O caminho que o happy-path mascara: usuário editou um skill instalado.
    home = str(tmp_path); monkeypatch.setenv("HOME", home)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    from koine import instalar
    instalar.extrair(VAULT, "0.4.0-dev")
    skills.instalar_habilidades("claude")           # instala
    # usuário adultera um SKILL.md instalado
    alvo = os.path.join(home, ".claude/skills/kn-01-recebe-usuario/SKILL.md")
    open(alvo, "w").write("EDITADO PELO USUÁRIO")
    div = skills.instalar_habilidades("claude")     # sem force
    assert "kn-01-recebe-usuario" in div            # reportado
    assert open(alvo).read() == "EDITADO PELO USUÁRIO"  # PRESERVADO (não destruído)
    # com force, sobrescreve
    skills.instalar_habilidades("claude", force=True)
    assert open(alvo).read() != "EDITADO PELO USUÁRIO"


def test_harness_desconhecido_erra(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    import pytest
    with pytest.raises(ValueError):
        skills.instalar_habilidades("inexistente")
