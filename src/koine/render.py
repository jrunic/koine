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


def documento_inline(titulo: str, cm) -> str:
    """Todas as camadas do `cm` embutidas num documento só.

    Para o **modo skills**: sem wrapper não há env nem argumento para apontar
    bundle, então a pasta é a única via de entrega e o conteúdo tem que estar
    dentro do arquivo. É o mesmo princípio do adapter do codex, que já embute
    por não seguir `@path`.
    """
    partes = []

    def add(secao, path):
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                partes.append(Parte(secao, f.read()))
        except OSError:
            pass

    add("Usuário", cm.usuario_path)
    add("Koine", cm.koine_path)
    add("Agente", cm.agente_path)
    if not cm.bootstrap:
        add("Escopo", cm.escopo_path)
        for ip in cm.indice_paths:
            add("Referências — " + dominio_de(ip), ip)
    add("Instrução do Koine para esta sessão", cm.instrucao_path)
    add("Contexto da sessão (snapshot de ./CONTEXTO.md)", cm.contexto_path)
    return mescar_documentos(titulo, partes)


def prosa_sessao(cm, comando: str) -> str:
    """Instruções que acompanham todo documento inline.

    O corpo do `CONTEXTO.md` entregue por conteúdo é um SNAPSHOT: sem esta prosa
    o agente edita a cópia que leu, e o trabalho da sessão se perde. A fonte
    canônica é sempre o arquivo na pasta.
    """
    regen = (f"Este contexto é regenerado a cada sessão por `{comando}`. "
             "**Não o edite.**")
    if cm.bootstrap and not cm.contexto_path:
        return ("## Instruções desta sessão\n\n"
                "Esta pasta ainda não tem contexto Koine. Crie o `./CONTEXTO.md` desta "
                "pasta com `/kn-02-mantem-catalogo` (Fluxo 3) antes de iniciar o "
                "trabalho. " + regen + "\n")
    return ("## Instruções desta sessão\n\n"
            "O contexto mutável desta sessão vive em `./CONTEXTO.md` (no diretório "
            "atual). Leia e mantenha esse arquivo durante o trabalho — toda "
            "persistência de contexto entre sessões vai para ele. O conteúdo acima é "
            "um snapshot; a fonte canônica é o arquivo. " + regen + "\n")
