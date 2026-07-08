import argparse
import os
import pathlib
import sys

from koine import (
    adapters,
    canonica,
    contexto,
    frontmatter,
    indice,
    instalar as _instalar,
    paths,
    schema,
    skills,
    wrappers,
)
from koine._version import __version__

SUBCOMANDOS = {"versao", "instalar", "instalar-habilidades"}  # gerar/mostrar chegam em P3


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("uso: koine <cliente|subcomando> ...", file=sys.stderr)
        return 2

    primeiro = argv[0]
    if primeiro in SUBCOMANDOS:
        if primeiro == "versao":
            print(f"koine {__version__}")
            return 0
        if primeiro == "instalar":
            return _cmd_instalar(argv[1:])
        if primeiro == "instalar-habilidades":
            return _cmd_instalar_habilidades(argv[1:])
    if primeiro in adapters.REGISTRY:
        return _rodar_cliente(primeiro, argv[1:])

    print(f"desconhecido: {primeiro}", file=sys.stderr)
    return 2


def _cmd_instalar(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine instalar")
    p.add_argument("--vault", default=None)
    p.add_argument("--bin", default=None)
    p.add_argument("--pyz", default=None)
    p.add_argument("--force", action="store_true")
    ns = p.parse_args(args)

    vault_src = ns.vault or _localizar_vault()
    div = _instalar.extrair(vault_src, __version__, force=ns.force)
    if div and not ns.force:
        print("Arquivos divergentes (use --force):")
        for d in div:
            print("  !", d)
    bindir = ns.bin or _bin_padrao()
    pyz = ns.pyz or _pyz_padrao()
    # sys.executable = interpretador que rodou `instalar` (>=3.10 garantido);
    # bakear absoluto no wrapper evita `python3` puro pegar um Python antigo.
    wrappers.gerar(bindir, pyz, sys.executable)
    canonica.configurar(vault_src)
    print("Instalação concluída.")
    return 0


def _cmd_instalar_habilidades(args: list[str]) -> int:
    p = argparse.ArgumentParser(prog="koine instalar-habilidades")
    p.add_argument("--para", required=True)
    p.add_argument("--force", action="store_true")
    ns = p.parse_args(args)
    div = skills.instalar_habilidades(ns.para, force=ns.force)
    if div and not ns.force:
        print("Skills divergentes preservadas (use --force para sobrescrever):")
        for d in div:
            print("  !", d)
    else:
        print(f"Skills instaladas para {ns.para}.")
    return 0


def _localizar_vault() -> str:
    # 1. ao lado do argv0/pyz (payload de distribuição)
    base = os.path.dirname(os.path.abspath(sys.argv[0]))
    for cand in (os.path.join(base, "vault"), os.path.join(base, ".koine-bootstrap")):
        if os.path.isdir(cand):
            return cand
    # 2. dev: repo vault/ relativo a este arquivo (src/koine/cli.py → ../../vault)
    repo_vault = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "vault"))
    if os.path.isdir(repo_vault):
        return repo_vault
    raise SystemExit("vault não encontrado; use --vault <path>")


def _bin_padrao() -> str:
    return os.path.join(str(pathlib.Path.home()), ".local", "bin")


def _pyz_padrao() -> str:
    return os.path.abspath(sys.argv[0])


def _rodar_cliente(cliente: str, args: list[str]) -> int:
    agente, pasta = args[0], args[1]  # P1: pasta é direct-path
    ctx_path = os.path.join(pasta, "CONTEXTO.md")
    fm, _ = frontmatter.ler(open(ctx_path, encoding="utf-8").read())
    # bootstrap não tem escopo nem índices; contexto.resolver trata o ramo.
    if not fm.get("bootstrap"):
        # índices antes do render (o adapter os referencia)
        escopo_fm, _ = frontmatter.ler(
            open(os.path.join(paths.config_dir(), "escopos", f"{fm['escopo']}.md"),
                 encoding="utf-8").read())
        refs = paths.resolver_tagged(schema.Escopo.from_fm(escopo_fm).pasta_referencias)
        indice.gerar(refs, fm.get("dominios", []))

    cm = contexto.resolver(agente, pasta)
    conteudo = adapters.get(cliente).renderizar(cm)
    with open(os.path.join(pasta, "CLAUDE.md"), "w", encoding="utf-8") as f:
        f.write(conteudo)
    return 0
