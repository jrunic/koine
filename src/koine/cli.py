import os
import sys

from koine import adapters, contexto, frontmatter, indice, paths, schema
from koine._version import __version__

SUBCOMANDOS = {"versao"}  # instalar/gerar/mostrar chegam em P2/P3


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
    if primeiro in adapters.REGISTRY:
        return _rodar_cliente(primeiro, argv[1:])

    print(f"desconhecido: {primeiro}", file=sys.stderr)
    return 2


def _rodar_cliente(cliente: str, args: list[str]) -> int:
    agente, pasta = args[0], args[1]  # P1: pasta é direct-path
    ctx_path = os.path.join(pasta, "CONTEXTO.md")
    fm, _ = frontmatter.ler(open(ctx_path, encoding="utf-8").read())
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
