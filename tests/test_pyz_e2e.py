import os
import stat
import subprocess
import sys
from tests import _parity
from tests.fixtures import seed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp) -> str:
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def test_pyz_versao(tmp_path):
    pyz = _build(tmp_path)
    r = subprocess.run([sys.executable, pyz, "versao"], capture_output=True, text=True, check=True)
    assert "koine" in r.stdout.lower()


def test_pyz_sem_codigo_nativo(tmp_path):
    # restrição-âncora do port: nada de .pyd/.so/.dll cruza o AV do Aldo.
    import zipfile
    pyz = _build(tmp_path)
    with zipfile.ZipFile(pyz) as z:
        nativos = [n for n in z.namelist() if n.endswith((".pyd", ".so", ".dll"))]
    assert nativos == [], f"pyz carrega código nativo: {nativos}"


def test_pyz_claude_paridade(tmp_path, monkeypatch):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    go = _parity.gerar_go(fx["trab"], "hermes", fx["home"])
    os.remove(os.path.join(fx["trab"], "CLAUDE.md"))
    subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                   env={**os.environ, "HOME": fx["home"]}, check=True, capture_output=True, text=True)
    py = open(os.path.join(fx["trab"], "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)


def test_greenfield_instalar_do_pyz_e_rodar_wrapper(tmp_path):
    pyz = _build(tmp_path)                        # pacote de distribuição
    home = str(tmp_path / "home"); os.makedirs(home)
    bindir = os.path.join(home, "bin")

    # PATH MÍNIMO de propósito: /usr/bin/python3 no macOS é 3.9 e NÃO roda koine
    # (sintaxe 3.12+). O `instalar` roda via sys.executable (>=3.12) e o wrapper
    # BAKA esse interpretador absoluto — então ele funciona mesmo quando o único
    # `python3` do PATH é o 3.9. Este PATH mínimo prova esse comportamento (o
    # bug de `python3` puro pegaria o 3.9 e quebraria).
    path = "/usr/bin:/bin"

    # 1. instalar a partir do pyz (payload do vault está ao lado do pyz)
    subprocess.run([sys.executable, pyz, "instalar", "--bin", bindir, "--pyz", pyz, "--para", "claude"],
                   env={"HOME": home, "PATH": path}, check=True, capture_output=True, text=True)
    assert os.path.exists(os.path.join(home, ".local/share/koine/KOINE.md"))
    # skills instaladas no harness (co-requisito do onboarding)
    assert os.path.isdir(os.path.join(home, ".claude", "skills", "kn-12-prepara-contexto"))
    wrapper = os.path.join(bindir, "kn-claude")
    assert os.path.exists(wrapper) and (os.stat(wrapper).st_mode & stat.S_IXUSR)

    # 2. semear pasta de trabalho no HOME instalado e rodar o wrapper
    trab = seed.semear_trabalho(home)
    go = _parity.gerar_go(trab, "hermes", home)
    os.remove(os.path.join(trab, "CLAUDE.md"))
    subprocess.run([wrapper, "hermes", trab], env={"HOME": home, "PATH": path},
                   check=True, capture_output=True, text=True)
    py = open(os.path.join(trab, "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py) == _parity.normalize(go)

    # 3. onboarding: rodar o wrapper na PASTA CANÔNICA (CONTEXTO bootstrap)
    canon = os.path.join(home, "koine")
    go_b = _parity.gerar_go(canon, "hermes", home)
    os.remove(os.path.join(canon, "CLAUDE.md"))
    subprocess.run([wrapper, "hermes", canon], env={"HOME": home, "PATH": path},
                   check=True, capture_output=True, text=True)
    py_b = open(os.path.join(canon, "CLAUDE.md"), encoding="utf-8").read()
    assert _parity.normalize(py_b) == _parity.normalize(go_b)
