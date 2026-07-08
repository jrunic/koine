import io
import os
import subprocess
import sys

from koine import mensagens, skills


def test_detectar_harnesses_ordenado(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"; os.makedirs(bindir)
    for b in ("codex", "claude"):
        f = bindir / b; f.write_text("#!/bin/sh\n"); f.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bindir}:/usr/bin:/bin")
    assert skills.detectar_harnesses() == ["claude", "codex"]


def test_detectar_harnesses_vazio(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))  # PATH sem nada
    assert skills.detectar_harnesses() == []


def test_mensagem_orientativa_darwin_sem_node_sem_brew(monkeypatch):
    monkeypatch.setattr(mensagens, "_os_atual", lambda: "darwin")
    monkeypatch.setattr(mensagens, "_tem_binario", lambda n: False)
    m = mensagens.orientativa_sem_harness()
    assert "(nenhum cliente IA detectado no PATH)" in m
    assert "Node.js não encontrado" in m and "brew install node" in m
    assert "Homebrew não encontrado (macOS)" in m
    assert "Claude Code (Anthropic)" in m
    assert "rode `koine instalar` novamente" in m


def test_mensagem_orientativa_linux_com_node(monkeypatch):
    monkeypatch.setattr(mensagens, "_os_atual", lambda: "linux")
    monkeypatch.setattr(mensagens, "_tem_binario", lambda n: True)
    m = mensagens.orientativa_sem_harness()
    assert "Node.js não encontrado" not in m and "Homebrew" not in m


def test_mensagem_final_lista_os_5_clientes():
    m = mensagens.final_instalar()
    assert "Para começar sua primeira sessão com Hermes:" in m
    assert "kn-claude hermes koine" in m and "/kn-01-recebe-usuario" in m
    for cli in ("kn-agy", "kn-copilot", "kn-opencode", "kn-codex"):
        assert f"{cli} hermes koine" in m


# e2e não-interativo vs oráculo: PATH sem harness → os DOIS lados imprimem a
# orientativa; com harness (shim) → os DOIS listam detectados + dica não-interativa.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _instalar(cmd_extra, home, path):
    return subprocess.run(cmd_extra, env={"HOME": home, "USERPROFILE": home, "PATH": path},
                          capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)


def test_e2e_sem_harness_orientativa_nos_dois_lados(tmp_path):
    # BLOQUEIO do advisor (finding 2): NUNCA rodar o oráculo direto de dist/ —
    # o instalar Go cria symlinks kn-* AO LADO do binário e sujaria o repo
    # (que o `git add -A` do Step 5 commitaria). Copiar para bindir do tmp,
    # mesmo racional de _parity.instalar_go (docstring _parity.py:112-117).
    import shutil as _shutil
    gobin_dir = tmp_path / "gobin"; os.makedirs(gobin_dir)
    go_bin = str(gobin_dir / "kn-agente")
    _shutil.copy(os.environ["KOINE_GO_BIN"], go_bin)
    out = str(tmp_path / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"), "--out", out],
                   check=True, capture_output=True, text=True)
    pyz = os.path.join(out, "koine.pyz")
    path_min = "/usr/bin:/bin"
    hg = str(tmp_path / "hg"); os.makedirs(hg)
    hp = str(tmp_path / "hp"); os.makedirs(hp)
    r_go = _instalar([go_bin, "instalar"], hg, path_min)
    r_py = _instalar([sys.executable, pyz, "instalar"], hp, path_min)
    for r in (r_go, r_py):
        assert r.returncode == 0
        assert "(nenhum cliente IA detectado no PATH)" in r.stdout
        assert "Para começar sua primeira sessão com Hermes:" in r.stdout
    # linhas-chave idênticas Go×Py (módulo kn-agente→koine na dica de comando)
    assert "Depois de instalar um cliente" in r_go.stdout and \
           "Depois de instalar um cliente" in r_py.stdout


def test_e2e_com_harness_nao_interativo_lista_e_nao_instala(tmp_path):
    out = str(tmp_path / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"), "--out", out],
                   check=True, capture_output=True, text=True)
    pyz = os.path.join(out, "koine.pyz")
    bindir = tmp_path / "shim"; os.makedirs(bindir)
    f = bindir / "claude"; f.write_text("#!/bin/sh\n"); f.chmod(0o755)
    home = str(tmp_path / "home"); os.makedirs(home)
    r = _instalar([sys.executable, pyz, "instalar"], home, f"{bindir}:/usr/bin:/bin")
    assert r.returncode == 0
    assert "Detectados: claude" in r.stdout
    assert "Modo não-interativo" in r.stdout
    assert not os.path.exists(os.path.join(home, ".claude", "skills"))  # NÃO instalou


def test_instalar_com_deteccao_prompt_sim_e_nao(tmp_path, monkeypatch, capsys):
    from koine import cli
    bindir = tmp_path / "bin"; os.makedirs(bindir)
    for b in ("agy", "claude"):
        f = bindir / b; f.write_text("#!/bin/sh\n"); f.chmod(0o755)
    home = tmp_path / "home"; os.makedirs(home)
    monkeypatch.setenv("HOME", str(home)); monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("PATH", f"{bindir}:/usr/bin:/bin")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    # vault instalado é pré-requisito do instalar_habilidades — usa o do repo
    monkeypatch.setattr("koine.paths.vault_dir", lambda: os.path.join(REPO, "vault"))
    monkeypatch.setattr("sys.stdin", io.StringIO("s\nn\n"))
    cli._instalar_com_deteccao(None, True)
    out = capsys.readouterr().out
    assert "agy detectado → instalar skills kn-*? [S/n]:" in out
    assert "→ Pulado. Para instalar depois:" in out
    assert os.path.isdir(home / ".gemini" / "antigravity-cli" / "skills")      # agy: sim
    assert not os.path.exists(home / ".claude" / "skills")                     # claude: não
