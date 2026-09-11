import os

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
    base = os.path.basename(indice_path)
    if base.endswith(".md"):
        base = base[:-3]
    if base.startswith("kn-indice-"):
        base = base[len("kn-indice-"):]
    return base


_PREFIXO_ENTRADA = "- `"


def _caminho_da_entrada(linha: str) -> str:
    """O path relativo dentro da linha do índice, ou vazio se não for entrada."""
    if not linha.startswith(_PREFIXO_ENTRADA):
        return ""
    resto = linha[len(_PREFIXO_ENTRADA):]
    fim = resto.find("`")
    return resto[:fim] if fim > 0 else ""


def secoes_de_indice(indice_paths: list) -> list:
    """As seções de referências de UMA sessão, com a repetição resolvida.

    Cada `kn-indice-<dom>.md` está certo sozinho — e continua: o arquivo em
    disco lista tudo que é daquele domínio, porque quem o abre espera o catálogo
    completo dele. O custo aparece quando dois índices entram no MESMO documento:
    medido em 10/09/2026, 20 entradas declaravam dois domínios e viajavam
    duplicadas, 16.253 bytes por sessão.

    A entrada é descrita no PRIMEIRO índice em que aparece — ordem do `dominios:`
    da pasta, que já é a ordem em que eles entram no documento. Nas seguintes ela
    vira referência cruzada: não some, porque sumir esconderia do agente que a
    referência pertence àquele domínio, que é informação de método.

    Ponto único de propósito. São TRÊS os caminhos de montagem (o documento
    inline comum, o do codex e o copilot, que emite um arquivo por índice), e
    corrigir só onde se olhou foi o defeito que a jd-task #706 achou.
    """
    partes, vistos = [], {}
    for ip in indice_paths:
        dom = dominio_de(ip)
        try:
            with open(ip, encoding="utf-8") as f:
                texto = f.read()
        except OSError:
            continue
        saida = []
        for linha in texto.split("\n"):
            rel = _caminho_da_entrada(linha)
            if rel and rel in vistos:
                saida.append(f"- `{rel}` — descrita em *Referências — "
                             f"{vistos[rel]}*")
                continue
            if rel:
                vistos[rel] = dom
            saida.append(linha)
        partes.append(Parte("Referências — " + dom, "\n".join(saida)))
    return partes


def agente_de(cm) -> str:
    """Nome do agente que a sessão realmente vai usar, sem extensão.

    Sai do path resolvido, não do nome pedido: é o que faz `kn-<cliente> hermes`
    e o provider que força `hermes` por variável dividirem o mesmo slot — são a
    mesma sessão, e separá-las duplicaria o cache sem motivo.
    """
    if not cm.agente_path:
        return "hermes"
    return os.path.splitext(os.path.basename(cm.agente_path))[0]


def dado_da_instrucao(cm) -> str:
    """O nome concreto que falta nesta sessão, para acompanhar a instrução.

    A instrução do vault é prosa fixa e manda o agente dizer QUAL escopo (ou
    qual agente) a pasta declara. Ele não teria como: o nome mora no frontmatter
    do `CONTEXTO.md`, que o render remove, e o snapshot entrega só o corpo.
    Medido em 30/08/2026, na prova viva da #709 — a instrução chegava e o dado
    não.
    """
    if cm.escopo_ausente:
        return ("> **Escopo declarado por esta pasta e não encontrado:** "
                f"`{cm.escopo_ausente}`")
    if cm.agente_ausente:
        return ("> **Agente pedido para esta sessão e não encontrado:** "
                f"`{cm.agente_ausente}`")
    return ""


def add_instrucao(partes: list, cm) -> None:
    """Seção da instrução do Koine, com o dado da sessão colado no topo."""
    if not cm.instrucao_path:
        return
    try:
        with open(cm.instrucao_path, encoding="utf-8") as f:
            texto = f.read()
    except OSError:
        return
    dado = dado_da_instrucao(cm)
    partes.append(Parte("Instrução do Koine para esta sessão",
                        f"{dado}\n\n{texto}" if dado else texto))


def documento_inline(titulo: str, cm) -> str:
    """Todas as camadas do `cm` embutidas num documento só.

    Para quem entrega por CONTEÚDO: o conteúdo tem que estar dentro do arquivo,
    porque não há env nem argumento apontando um bundle. É o mesmo princípio do
    adapter do codex, que já embute por não seguir `@path`.
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
        partes.extend(secoes_de_indice(cm.indice_paths))
    add_instrucao(partes, cm)
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
        # Ramo canal-only: no `resolver`, o único retorno de bootstrap SEM
        # `contexto_path` é o `sem_contexto`, e o chamador único dele é o launch
        # por canal de máquina. Ali a instrução do vault manda EXPLICITAMENTE não
        # escrever `CONTEXTO.md` — materializar configuração numa pasta que
        # ninguém escolheu é o defeito que o canal existe para não repetir. A
        # prosa mandava o contrário, no mesmo documento (jd-task #706).
        if cm.instrucao_path:
            return ("## Instruções desta sessão\n\n"
                    "Esta pasta ainda não tem contexto Koine, e **nada foi escrito "
                    "nela**. Siga a instrução do Koine acima: não crie o "
                    "`./CONTEXTO.md` por conta própria nem chute escopo e domínio. "
                    + regen + "\n")
        # Sem instrução não há a quem deferir — `ContextoMontado` montado à mão,
        # por teste ou por chamador futuro. Orienta sem contradizer ninguém.
        return ("## Instruções desta sessão\n\n"
                "Esta pasta ainda não tem contexto Koine. Crie o `./CONTEXTO.md` desta "
                "pasta com `/kn-02-mantem-catalogo` (Fluxo 3) antes de iniciar o "
                "trabalho. " + regen + "\n")
    return ("## Instruções desta sessão\n\n"
            "O contexto mutável desta sessão vive em `./CONTEXTO.md` (no diretório "
            "atual). Leia e mantenha esse arquivo durante o trabalho — toda "
            "persistência de contexto entre sessões vai para ele. O conteúdo acima é "
            "um snapshot; a fonte canônica é o arquivo. " + regen + "\n")
