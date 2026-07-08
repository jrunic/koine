import os
from datetime import datetime, timezone

from koine import frontmatter, paths, schema

# Contratos OKF ignorados apenas na raiz da pasta-referências.
_CONTRATOS_RAIZ = ("index.md", "log.md")


def gerar(pasta_refs: str, dominios: list[str]) -> None:
    """Materializa kn-indice-<dom>.md para cada domínio declarado.

    Reproduz internal/indice/gerador.go: varre pasta_refs, agrupa refs por
    domínio declarado no frontmatter, ordena por path relativo e escreve o
    header (tipo/dominio/gerado/entradas) + sinopse + entradas catalogadas.
    """
    entradas: dict[str, list[tuple[str, str]]] = {d: [] for d in dominios}
    for raiz, subdirs, arqs in os.walk(pasta_refs):
        # não descer em diretórios ocultos (paridade com fs.SkipDir do Go)
        subdirs[:] = [s for s in subdirs if not s.startswith(".")]
        for a in sorted(arqs):
            if not a.endswith(".md"):
                continue
            full = os.path.join(raiz, a)
            rel = os.path.relpath(full, pasta_refs).replace(os.sep, "/")
            # contratos OKF só são ignorados na raiz
            if "/" not in rel and (a in _CONTRATOS_RAIZ or a.startswith("kn-indice-")):
                continue
            fm, _ = frontmatter.ler(open(full, encoding="utf-8").read())
            for d in fm.get("dominios", []) or []:
                if d in entradas:
                    entradas[d].append((rel, fm.get("description", "") or ""))

    cfg = paths.config_dir()
    for d in dominios:
        sinopse = _ler_sinopse(cfg, d)
        itens = sorted(entradas[d], key=lambda e: e[0])
        _escrever(os.path.join(pasta_refs, f"kn-indice-{d}.md"), d, sinopse, itens)


def _ler_sinopse(cfg: str, dom: str) -> str:
    path = os.path.join(cfg, "dominios", f"{dom}.md")
    if not os.path.exists(path):
        return (
            f"_Domínio `{dom}` não plantado. Rode `kn-agente instalar` ou "
            f"`/kn-02-mantem-catalogo` (fluxo dominio)._"
        )
    dfm, _ = frontmatter.ler(open(path, encoding="utf-8").read())
    sinopse = schema.Dominio.from_fm(dfm).sinopse
    if not sinopse:
        return f"_Domínio `{dom}` sem sinopse — corrija o frontmatter de {path}._"
    return sinopse


def _escrever(path, dom, sinopse, itens):
    linhas = [
        "---",
        "tipo: indice",
        f"dominio: {dom}",
        f"gerado: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"entradas: {len(itens)}",
        "---",
        "",
        "## Domínio",
        "",
        sinopse,
        "## Entradas catalogadas no escopo",
        "",
    ]
    if not itens:
        linhas.append("_Nenhuma referência catalogada neste domínio._")
    else:
        for rel, desc in itens:
            linhas.append(f"- `{rel}` — {desc}" if desc else f"- `{rel}`")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
