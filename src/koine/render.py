from dataclasses import dataclass


@dataclass
class Parte:
    secao: str
    conteudo: str


def strip_frontmatter(content: str) -> str:
    if not content.startswith("---\n"):
        return content
    rest = content[4:]
    idx = rest.find("\n---")
    if idx < 0:
        return content
    after = rest[idx + 4:]
    if after.startswith("\n"):
        after = after[1:]
    return after


def demover_h1(content: str) -> str:
    linhas = content.split("\n")
    for i, l in enumerate(linhas):
        if l.startswith("# "):
            linhas[i] = "#" + l
            break
    return "\n".join(linhas)


def wrapar_instructions(conteudo: str) -> str:
    """Produz conteúdo para um `.instructions.md` do Copilot CLI.

    Adiciona frontmatter `applyTo: "**"`, remove frontmatter original e demove H1→H2.
    """
    body = demover_h1(strip_frontmatter(conteudo)).lstrip("\n")
    return '---\napplyTo: "**"\n---\n\n' + body


def mescar_documentos(titulo: str, partes: list) -> str:
    buf = f"# {titulo}\n\n"
    for p in partes:
        buf += f"## {p.secao}\n\n"
        corpo = demover_h1(strip_frontmatter(p.conteudo))
        buf += corpo.rstrip("\n") + "\n\n"
    return buf.rstrip("\n")


def dominio_de(indice_path: str) -> str:
    import os
    base = os.path.basename(indice_path)
    if base.endswith(".md"):
        base = base[:-3]
    if base.startswith("kn-indice-"):
        base = base[len("kn-indice-"):]
    return base
