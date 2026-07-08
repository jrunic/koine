import hashlib
import os
import re
import shutil
import subprocess

# Linhas que variam entre execuções e NÃO são divergência real.
# Congeladas fora da comparação. Ampliar SÓ com evidência empírica.
_TIMESTAMP = re.compile(r"em \d{4}-\d{2}-\d{2}[ T][\d:]+")
_REGEN = re.compile(r"regerar com [^\n]*")
# Header do kn-indice-<dom>.md: `gerado: <ISO8601>Z` (RFC3339 UTC).
# Formato distinto do `em <ts>` do CLAUDE.md — normalizar separadamente.
_INDICE_GERADO = re.compile(r"gerado: [^\n]*")


def normalize(text: str) -> str:
    text = _TIMESTAMP.sub("em <TS>", text)
    text = _REGEN.sub("regerar com <CMD>", text)
    text = _INDICE_GERADO.sub("gerado: <TS>", text)
    return text


def gerar_go(pasta: str, agente: str, home: str) -> str:
    """Roda o binário Go e devolve o CLAUDE.md gerado."""
    go_bin = os.environ.get("KOINE_GO_BIN", "kn-agente")
    env = {**os.environ, "HOME": home}
    subprocess.run(
        [go_bin, "gerar", agente, pasta],
        env=env, check=True, capture_output=True, text=True,
    )
    with open(os.path.join(pasta, "CLAUDE.md"), encoding="utf-8") as f:
        return f.read()


def gerar_go_arg(arg: str, agente: str, home: str, destino: str) -> str:
    """Roda `gerar <agente> <arg>` (arg cru, p/ o Go resolver alias) e lê
    <destino>/CLAUDE.md — o destino resolvido, não o arg."""
    go_bin = os.environ.get("KOINE_GO_BIN", "kn-agente")
    subprocess.run(
        [go_bin, "gerar", agente, arg],
        env={**os.environ, "HOME": home}, check=True,
        capture_output=True, text=True,
    )
    with open(os.path.join(destino, "CLAUDE.md"), encoding="utf-8") as f:
        return f.read()


def gerar_agy_go(pasta: str, agente: str, home: str, shim_path_dir: str) -> str:
    """Renderiza GEMINI.md pelo Go via o wrapper kn-agy: copia o oráculo para um
    arquivo `kn-agy` (o Go decide o cliente pelo basename) e roda com um shim
    `agy` PREPENDADO no PATH (o wrapper lança o cliente após gerar). Lê GEMINI.md."""
    go_bin = os.environ.get("KOINE_GO_BIN", "kn-agente")
    bindir = os.path.join(home, "_gobin_agy")
    os.makedirs(bindir, exist_ok=True)
    knagy = os.path.join(bindir, "kn-agy")
    if not os.path.exists(knagy):
        shutil.copy(go_bin, knagy)
        os.chmod(knagy, 0o755)
    path = shim_path_dir + os.pathsep + "/usr/bin:/bin"   # shim `agy` PREPENDADO
    subprocess.run(
        [knagy, agente, pasta], env={"HOME": home, "PATH": path},
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        check=True, timeout=30,
    )
    with open(os.path.join(pasta, "GEMINI.md"), encoding="utf-8") as f:
        return f.read()


def mostrar_go(pasta: str, agente: str, home: str) -> str:
    """stdout de `kn-agente mostrar <agente> <pasta>` num HOME isolado."""
    go_bin = os.environ.get("KOINE_GO_BIN", "kn-agente")
    r = subprocess.run(
        [go_bin, "mostrar", agente, pasta],
        env={"HOME": home, "PATH": "/usr/bin:/bin"},
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True,
    )
    return r.stdout


def parity(go_text: str, py_text: str) -> bool:
    return normalize(go_text) == normalize(py_text)


def instalar_go(home: str) -> None:
    """Roda o `instalar` do Go num HOME isolado, com efeitos colaterais contidos.

    Copia o binário para <home>/_gobin (symlinks caem lá, não no repo) e usa
    PATH mínimo (nenhum harness detectado) + stdin fechado (não-interativo).
    """
    go_bin = os.environ.get("KOINE_GO_BIN", "kn-agente")
    bindir = os.path.join(home, "_gobin")
    os.makedirs(bindir, exist_ok=True)
    dst = os.path.join(bindir, "kn-agente")
    shutil.copy(go_bin, dst)
    os.chmod(dst, 0o755)
    subprocess.run(
        [dst, "instalar"],
        env={"HOME": home, "PATH": "/usr/bin:/bin"},
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True,
    )


def instalar_habilidades_go(home: str, harness: str) -> None:
    """Roda o `instalar-habilidades --para=<harness>` do Go num HOME isolado.
    Requer que `instalar_go(home)` tenha rodado antes (popula o vault)."""
    go_bin = os.environ.get("KOINE_GO_BIN", "kn-agente")
    bindir = os.path.join(home, "_gobin")
    os.makedirs(bindir, exist_ok=True)
    dst = os.path.join(bindir, "kn-agente")
    if not os.path.exists(dst):
        shutil.copy(go_bin, dst)
        os.chmod(dst, 0o755)
    subprocess.run(
        [dst, "instalar-habilidades", "--para", harness],
        env={"HOME": home, "PATH": "/usr/bin:/bin"},
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True,
    )


def arvore(base: str) -> dict:
    """{caminho-relativo: sha256} de todos os arquivos sob base. {} se ausente."""
    out = {}
    if not os.path.isdir(base):
        return out
    for raiz, _, arqs in os.walk(base):
        for a in arqs:
            p = os.path.join(raiz, a)
            with open(p, "rb") as f:
                out[os.path.relpath(p, base)] = hashlib.sha256(f.read()).hexdigest()
    return out
