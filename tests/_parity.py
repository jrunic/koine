import os
import re
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


def parity(go_text: str, py_text: str) -> bool:
    return normalize(go_text) == normalize(py_text)
