import os
import stat
import subprocess
import sys

from koine import conflito
from tests.fixtures import seed, shim

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _build(tmp) -> str:
    out = str(tmp / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out], check=True, capture_output=True, text=True)
    return os.path.join(out, "koine.pyz")


def _assert_claude_md(conteudo: str, home: str) -> None:
    """Formato congelado do CLAUDE.md gerado: marcador na 1ª linha + @path
    das 4 camadas (usuário, KOINE, agente, escopo)."""
    assert conteudo.split("\n", 1)[0] == conflito.MARCADOR_KOINE
    for camada in (
        os.path.join(home, ".config", "koine", "teste.md"),
        os.path.join(home, ".local", "share", "koine", "KOINE.md"),
        os.path.join(home, ".local", "share", "koine", "agentes", "hermes.md"),
        os.path.join(home, ".config", "koine", "escopos", "fixture.md"),
    ):
        assert f"@{camada}" in conteudo, f"camada ausente: {camada}"


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


def test_pyz_claude_gera_claude_md(tmp_path):
    pyz = _build(tmp_path)
    fx = seed.montar(str(tmp_path / "fx"))
    # shim `claude` PREPENDADO ao PATH real (esta máquina tem claude real → sem prepend, trava)
    shimdir = str(tmp_path / "shim")
    shim.instalar_shim(shimdir, "claude", str(tmp_path / "cap.txt"))
    path = shimdir + os.pathsep + os.environ["PATH"]
    subprocess.run([sys.executable, pyz, "claude", "hermes", fx["trab"]],
                   env={**os.environ, "HOME": fx["home"], "PATH": path},
                   check=True, capture_output=True, text=True,
                   stdin=subprocess.DEVNULL, timeout=60)
    py = open(os.path.join(fx["trab"], "CLAUDE.md"), encoding="utf-8").read()
    _assert_claude_md(py, fx["home"])


def test_zip_de_distribuicao_pyz_e_vault_lado_a_lado(tmp_path):
    # o installer extrai este zip e o `instalar` localiza o vault AO LADO do pyz
    import zipfile
    from koine._version import __version__
    out = str(tmp_path / "dist")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build-pyz.py"),
                    "--out", out, "--zip"], check=True, capture_output=True, text=True)
    zpath = os.path.join(out, f"koine-{__version__}.zip")
    assert os.path.exists(zpath)
    with zipfile.ZipFile(zpath) as z:
        nomes = set(z.namelist())
    assert "koine.pyz" in nomes
    assert "vault/KOINE.md" in nomes
    assert "vault/agentes/hermes.md" in nomes
    assert not any(n.endswith((".pyd", ".so", ".dll")) for n in nomes)


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
    # shim `claude` PREPENDADO: os spawns do wrapper (2 e 3) lançam o cliente após gerar.
    shimdir = os.path.join(home, "shim")
    shim.instalar_shim(shimdir, "claude", os.path.join(home, "cap.txt"))
    path_launch = shimdir + os.pathsep + path

    # 1. instalar a partir do pyz (payload do vault está ao lado do pyz)
    # stdin=DEVNULL: sem ele, pytest num terminal real herdaria o TTY e o
    # `instalar` (isatty → interativo) abriria prompt e travaria a suíte.
    subprocess.run([sys.executable, pyz, "instalar", "--bin", bindir, "--pyz", pyz, "--para", "claude"],
                   env={"HOME": home, "PATH": path}, check=True, capture_output=True, text=True,
                   stdin=subprocess.DEVNULL, timeout=60)
    assert os.path.exists(os.path.join(home, ".local/share/koine/KOINE.md"))
    # skills instaladas no harness (co-requisito do onboarding)
    assert os.path.isdir(os.path.join(home, ".claude", "skills", "kn-12-prepara-contexto"))
    wrapper = os.path.join(bindir, "kn-claude")
    assert os.path.exists(wrapper) and (os.stat(wrapper).st_mode & stat.S_IXUSR)

    # 2. semear pasta de trabalho no HOME instalado e rodar o wrapper
    trab = seed.semear_trabalho(home)
    subprocess.run([wrapper, "hermes", trab], env={"HOME": home, "PATH": path_launch},
                   check=True, capture_output=True, text=True,
                   stdin=subprocess.DEVNULL, timeout=60)
    py = open(os.path.join(trab, "CLAUDE.md"), encoding="utf-8").read()
    _assert_claude_md(py, home)

    # 3. onboarding: rodar o wrapper na PASTA CANÔNICA (CONTEXTO bootstrap)
    canon = os.path.join(home, "koine")
    subprocess.run([wrapper, "hermes", canon], env={"HOME": home, "PATH": path_launch},
                   check=True, capture_output=True, text=True,
                   stdin=subprocess.DEVNULL, timeout=60)
    py_b = open(os.path.join(canon, "CLAUDE.md"), encoding="utf-8").read()
    assert py_b.split("\n", 1)[0] == conflito.MARCADOR_KOINE
    assert "modo bootstrap" in py_b
    assert f"@{os.path.join(home, '.local', 'share', 'koine', 'KOINE.md')}" in py_b
    assert f"@{os.path.join(home, '.local', 'share', 'koine', 'agentes', 'hermes.md')}" in py_b
    assert f"@{os.path.join(canon, 'CONTEXTO.md')}" in py_b
