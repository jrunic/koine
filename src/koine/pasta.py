import os
import shutil
import subprocess
import sys

from koine import aliases

MAX_PROFUNDIDADE = 7

PASTAS_IGNORADAS = {"node_modules", "vendor", "__pycache__", "target",
                    "build", "dist", "venv", "coverage", "Library"}


class ResolucaoErro(Exception):
    pass


def resolver(arg: str) -> str:
    """Porta de pasta.Resolver (resolucao.go).
    Ordem: "" → cwd | alias exato → path | path direto → abs | fuzzy+menu."""
    if arg == "":
        return os.getcwd()
    alvo = aliases.resolver(aliases.carregar(), arg)
    if alvo is not None:
        return alvo
    if os.path.isdir(arg):
        return os.path.abspath(arg)
    filtrados = fuzzy_filter(arg, listar_candidatos())
    try:
        escolha = escolher_menu(filtrados)
    except ResolucaoErro as e:
        raise ResolucaoErro(f"'{arg}' não resolveu para nenhuma pasta: {e}") from e
    oferecer_salvar_alias(arg, escolha)
    return escolha


def listar_candidatos() -> list:
    """Walk de $HOME até MAX_PROFUNDIDADE; poda dotdirs e PASTAS_IGNORADAS.
    Pasta-referências de escopo fica FORA do universo (decisão 2026-06-22)."""
    home = os.path.expanduser("~")
    result = []
    for raiz, dirs, _ in os.walk(home, onerror=lambda e: None):
        rel = os.path.relpath(raiz, home)
        prof = 0 if rel == "." else rel.count(os.sep) + 1
        if prof >= MAX_PROFUNDIDADE:
            dirs[:] = []
        # sorted: WalkDir do Go visita em ordem lexical; os.walk é arbitrário —
        # a ordem determina numeração do menu e resultado do fzf (finding 3)
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in PASTAS_IGNORADAS)
        if raiz != home:
            result.append(raiz)
    return result


def fuzzy_filter(arg: str, candidatos: list) -> list:
    palavras = [p for p in arg.strip().lower().split("-") if p]
    matched = []
    for c in candidatos:
        partes = os.path.basename(c).lower().split("-")
        if any(pw == dp for pw in palavras for dp in partes):
            matched.append(c)
    return matched


def escolher_menu(candidatos: list) -> str:
    if not candidatos:
        raise ResolucaoErro("nenhuma pasta candidata encontrada")
    if len(candidatos) == 1:
        return candidatos[0]
    fzf = shutil.which("fzf")
    if fzf:
        return _escolher_fzf(fzf, candidatos)
    return _escolher_numerado(candidatos)


def _escolher_fzf(fzf: str, candidatos: list) -> str:
    # stdout capturado, stderr HERDADO (a TUI do fzf desenha no stderr —
    # espelho do cmd.Stderr = os.Stderr do Go; capture_output mataria a TUI)
    r = subprocess.run([fzf, "--prompt=Pasta> ", "--height=40%"],
                       input="\n".join(candidatos), stdout=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise ResolucaoErro("fzf cancelado")
    escolha = r.stdout.strip()
    if not escolha:
        raise ResolucaoErro("nenhuma pasta selecionada")
    return escolha


def _escolher_numerado(candidatos: list) -> str:
    for i, c in enumerate(candidatos, 1):
        print(f"{i:3d}) {c}")
    print("Número: ", end="", flush=True)
    linha = sys.stdin.readline()
    if not linha:
        raise ResolucaoErro("entrada cancelada")
    try:
        n = int(linha.strip())
    except ValueError:
        raise ResolucaoErro("seleção inválida")
    if not 1 <= n <= len(candidatos):
        raise ResolucaoErro("seleção inválida")
    return candidatos[n - 1]


def oferecer_salvar_alias(arg: str, escolha: str) -> None:
    print(f"Salvar '{arg}' → '{escolha}' em aliases.json? [S/n] ", end="", flush=True)
    linha = sys.stdin.readline()
    if not linha:
        return
    if linha.strip().lower() == "n":
        return
    home = os.path.expanduser("~")
    from_, rel = "abs", escolha
    if escolha.startswith(home + os.sep):
        from_, rel = "home", escolha[len(home) + 1:]
    try:
        aliases.adicionar(arg, rel, from_)
    except (OSError, ValueError) as e:
        # ValueError cobre json.JSONDecodeError (aliases.json corrompido) —
        # o Go converte qualquer erro em aviso (resolucao.go:208-210)
        print(f"aviso: não foi possível salvar alias: {e}", file=sys.stderr)
    else:
        print(f"Alias '{arg}' salvo.")
