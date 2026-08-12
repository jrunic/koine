"""`koine validar` — varre frontmatter e reporta o que está torto no disco.

A leitura repara `descricao: Vendas B2B: metas` e segue a sessão (bug reportado em produção),
mas o arquivo continua inválido para qualquer outra ferramenta que o leia. Este
comando é a contrapartida: mostra o que foi lido no tapa e o que nem o reparo
salva, com arquivo, linha e coluna.

Diagnóstico por padrão, escrita só com `--corrigir` — e mesmo aí, apenas nos
reparáveis. O launch normaliza os arquivos de configuração sozinho; a pasta-
referências do usuário passa por aqui, onde ele pediu e vê a lista.
"""

import os
from dataclasses import dataclass, field

from koine import frontmatter, paths, schema

REPARAVEL = "reparavel"  # YAML inválido que o Koine leu reparando o valor
INVALIDO = "invalido"    # nem o reparo salva: TAB, indentação, bloco não-mapa


@dataclass
class Achado:
    arquivo: str
    estado: str
    chaves: list[str] = field(default_factory=list)  # REPARAVEL: o que foi recitado
    motivo: str = ""                                 # INVALIDO: o que o YAML reclamou
    linha: int | None = None
    coluna: int | None = None


def varrer(caminhos: list[str]) -> list[Achado]:
    """Achados de todo `.md` sob `caminhos` (arquivo ou pasta). Arquivo válido
    não vira achado. Pasta oculta é ignorada (paridade com o walk do índice)."""
    achados = []
    for alvo in caminhos:
        for arq in _arquivos(alvo):
            a = _analisar(arq)
            if a:
                achados.append(a)
    return sorted(achados, key=lambda a: a.arquivo)


def refs_do_escopo(pasta: str, cfg: str) -> str | None:
    """Pasta-referências do escopo declarado no CONTEXTO.md de `pasta`, se der
    para resolver. É lá que moram as referências da /kn-11 — a população onde a
    v0.4.6 quebrou —, e ela vive fora da config. Qualquer tropeço devolve None:
    varredura não aborta por causa de uma pasta mal configurada."""
    try:
        fm, _, _ = frontmatter.analisar(
            open(os.path.join(pasta, "CONTEXTO.md"), encoding="utf-8").read())
        escopo = os.path.join(cfg, "escopos", f"{fm['escopo']}.md")
        efm, _, _ = frontmatter.analisar(open(escopo, encoding="utf-8").read())
        refs = paths.resolver_tagged(schema.Escopo.from_fm(efm).pasta_referencias)
    except (OSError, UnicodeDecodeError, KeyError, ValueError,
            frontmatter.FrontmatterInvalido):
        return None
    return refs if os.path.isdir(refs) else None


def _arquivos(alvo: str):
    if os.path.isfile(alvo):
        if alvo.endswith(".md"):
            yield alvo
        return
    for raiz, subdirs, arqs in os.walk(alvo):
        subdirs[:] = [s for s in subdirs if not s.startswith(".")]
        for a in sorted(arqs):
            if a.endswith(".md"):
                yield os.path.join(raiz, a)


def _analisar(arq: str) -> Achado | None:
    try:
        with open(arq, encoding="utf-8") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        return None  # ilegível não é problema de frontmatter
    try:
        _, reparos, _ = frontmatter.analisar(texto)
    except frontmatter.FrontmatterInvalido as e:
        return Achado(arq, INVALIDO, motivo=e.motivo, linha=e.linha, coluna=e.coluna)
    return Achado(arq, REPARAVEL, chaves=reparos) if reparos else None


def relatorio(achados: list[Achado]) -> str:
    """Texto para o usuário — o mesmo que ele veria num aviso de sessão, só que
    reunido e antes de a sessão quebrar."""
    if not achados:
        return "Frontmatter: nenhum problema encontrado.\n"
    linhas = [f"Frontmatter: {len(achados)} arquivo(s) para corrigir.\n"]
    for a in achados:
        if a.estado == REPARAVEL:
            campos = ", ".join(f"`{c}`" for c in a.chaves)
            linhas.append(f"  ⚠ {a.arquivo}")
            linhas.append(f"      {campos} tem `:` sem aspas — o Koine lê, mas cite o valor:")
            linhas.append(f'        {a.chaves[0]}: "texto: com dois-pontos"')
        else:
            onde = f" (linha {a.linha}, coluna {a.coluna})" if a.linha else ""
            linhas.append(f"  ✗ {a.arquivo}{onde}")
            linhas.append(f"      {a.motivo}")
            linhas.append("      O Koine não consegue ler este frontmatter. Confira se há")
            linhas.append("      TAB no lugar de espaços e se toda linha é `chave: valor`.")
    return "\n".join(linhas) + "\n"


def corrigir(achados: list[Achado]) -> tuple[list[Achado], list[Achado]]:
    """Normaliza os reparáveis. Devolve (corrigidos, pendentes) — pendente é o
    que o Koine não sabe consertar, e continua sendo decisão do usuário."""
    from koine import ficha
    corrigidos, pendentes = [], []
    for a in achados:
        if a.estado == REPARAVEL and ficha.normalizar_arquivo(a.arquivo):
            corrigidos.append(a)
        else:
            pendentes.append(a)
    return corrigidos, pendentes


def relatorio_correcao(corrigidos: list[Achado], pendentes: list[Achado]) -> str:
    linhas = []
    if corrigidos:
        linhas.append(f"{len(corrigidos)} arquivo(s) corrigido(s) "
                      f"(originais em .bak):")
        linhas += [f"  ✓ {a.arquivo}" for a in corrigidos]
        linhas.append("")
    linhas.append(relatorio(pendentes).rstrip("\n") if pendentes
                  else "Nada pendente.")
    return "\n".join(linhas) + "\n"
