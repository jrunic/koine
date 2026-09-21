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

from koine import bootstrap, frontmatter, indice, paths, schema

REPARAVEL = "reparavel"  # YAML inválido que o Koine leu reparando o valor
INVALIDO = "invalido"    # nem o reparo salva: TAB, indentação, bloco não-mapa
SEM_FICHA = "sem-ficha"  # CONTEXTO.md sem `escopo:` — a sessão não abre nessa pasta
REFS_AUSENTE = "refs-ausente"  # o escopo aponta para pasta que não existe no disco
DESCRICAO_LONGA = "descricao-longa"  # cabe na referência, não cabe no índice
GLOSSARIO_SOLTO = "glossario-solto"    # na pasta-referências e fora do catálogo
AGENTE_SEM_DEFAULT = "agente-sem-default"  # tem agente(s), sem default resolvido

# A partir de quantas `description` longas o relatório resume em vez de listar.
# Medido na instalação de uma usuária em 10/09/2026: 156 das 167 referências
# (93%) estavam acima do teto. Relatório que acusa quase tudo não é acionável —
# e treina o usuário a pular a seção, que é o oposto do que ele existe para
# fazer. Abaixo do limiar a lista curta continua, porque ali ela se ataca de uma
# vez. `--todas` sempre lista.
LIMIAR_RESUMO = 10
MAIORES_NO_RESUMO = 10


@dataclass
class Achado:
    arquivo: str
    estado: str
    chaves: list[str] = field(default_factory=list)  # REPARAVEL: o que foi recitado
    motivo: str = ""                                 # INVALIDO: o que o YAML reclamou
    linha: int | None = None
    coluna: int | None = None


def varrer(caminhos: list[str], refs_indexadas: tuple = ()) -> list[Achado]:
    """Achados de todo `.md` sob `caminhos` (arquivo ou pasta). Arquivo válido
    não vira achado. Pasta oculta é ignorada (paridade com o walk do índice).

    `refs_indexadas` são as pastas-referências desta varredura — e só dentro
    delas a `description` alimenta um `kn-indice-<dom>.md`. Fora, ela não custa
    contexto nenhum, e acusá-la seria pedir trabalho por nada."""
    achados = []
    for alvo in caminhos:
        for arq in _arquivos(alvo):
            a = _analisar(arq, refs_indexadas)
            if a:
                achados.append(a)
    return sorted(achados, key=lambda a: a.arquivo)


def achado_agente_default(cfg: str) -> Achado | None:
    """Achado único (não por arquivo): o usuário tem agente(s) operacional(is)
    e o default não resolve para nenhum deles.

    Cross-file por natureza — compara `config/agentes/` contra o
    `agente-default` do arquivo do usuário —, por isso não cabe em `_analisar`
    (que só vê um arquivo por vez). `chaves` carrega os agentes existentes;
    `motivo` carrega o valor do default quando ele aponta para algo que não
    existe (vazio quando o default simplesmente não foi gravado).

    Mesmo critério de `agente.unico_sem_default`/`paseo_diagnostico.
    verificar_agente_default` — as três leem `agente.py`, para não divergir.
    """
    from koine import agente as _a
    agentes = _a.agentes_operacionais(cfg)
    if not agentes:
        return None
    default = _a.default_do_usuario(_a.usuario_path(cfg), frontmatter.ler_arquivo)
    if default in agentes:
        return None
    alvo = _a.usuario_path(cfg) or os.path.join(cfg, "<seu-arquivo-de-usuario>.md")
    return Achado(alvo, AGENTE_SEM_DEFAULT, chaves=agentes, motivo=default)


def refs_do_escopo(pasta: str, cfg: str) -> tuple[str | None, bool]:
    """Pasta-referências do escopo declarado no CONTEXTO.md de `pasta`.

    Devolve `(caminho, existe)`. Os dois estados eram colapsados num `None` só —
    "não deu para resolver" e "resolveu e não existe" —, e o segundo é
    exatamente o que derruba a sessão: `indice.gerar` escreve ali a cada launch.
    Quem colapsa não consegue reportar (jd-task #761).

    Tropeço de leitura continua devolvendo `(None, False)`: varredura não aborta
    por causa de uma pasta mal configurada.
    """
    try:
        fm, _, _ = frontmatter.analisar(
            open(os.path.join(pasta, "CONTEXTO.md"), encoding="utf-8").read())
        escopo = os.path.join(cfg, "escopos", f"{fm['escopo']}.md")
        efm, _, _ = frontmatter.analisar(open(escopo, encoding="utf-8").read())
        refs = paths.resolver_tagged(schema.Escopo.from_fm(efm).pasta_referencias)
    except (OSError, UnicodeDecodeError, KeyError, ValueError,
            frontmatter.FrontmatterInvalido):
        return None, False
    return refs, os.path.isdir(refs)


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


def _entra_em_indice(arq: str, refs_indexadas: tuple) -> bool:
    """Este arquivo vira linha de algum `kn-indice-<dom>.md`?

    Só a pasta-referências do escopo alimenta índice. Fora dela — config, pasta
    de trabalho, referência de alcance de pasta — a `description` não custa
    contexto, e acusá-la seria o falso positivo que a rc1 da v0.12.0 reprovou.
    """
    base = os.path.basename(arq)
    if base in indice.CONTRATOS_RAIZ or base.startswith("kn-indice-"):
        return False
    return any(os.path.commonpath([os.path.abspath(arq), os.path.abspath(r)])
               == os.path.abspath(r) for r in refs_indexadas)


def _analisar(arq: str, refs_indexadas: tuple = ()) -> Achado | None:
    try:
        with open(arq, encoding="utf-8") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        return None  # ilegível não é problema de frontmatter
    try:
        fm, reparos, _ = frontmatter.analisar(texto)
    except frontmatter.FrontmatterInvalido as e:
        return Achado(arq, INVALIDO, motivo=e.motivo, linha=e.linha, coluna=e.coluna)
    # A ficha faltando vem antes do valor mal citado: uma impede a sessão de
    # abrir, a outra só deixa o arquivo torto para outras ferramentas.
    if (os.path.basename(arq) == "CONTEXTO.md"
            and bootstrap.estado_do_fm(fm) == bootstrap.INCOMPLETO):
        return Achado(arq, SEM_FICHA)
    # Precedência: o que impede a sessão vem antes do que só encurta o índice.
    # Um achado por arquivo — quem tem aspas faltando E description longa ouve
    # sobre a primeira, e sobre a segunda na rodada seguinte. Limitação
    # declarada, não esquecimento.
    if reparos:
        return Achado(arq, REPARAVEL, chaves=reparos)
    # Antes da `description`: não entrar no índice é mais grave que entrar com a
    # linha cortada. O discriminante é `dominios:` e não a existência do bloco —
    # medido em 11/09/2026, arquivo sem frontmatter devolve `fm` VAZIO sem
    # levantar, e frontmatter sem `dominios:` fica igualmente fora do catálogo.
    if (os.path.basename(arq) == "GLOSSARIO.md"
            and not fm.get("dominios")
            and _entra_em_indice(arq, refs_indexadas)):
        return Achado(arq, GLOSSARIO_SOLTO)
    desc = fm.get("description", "") or ""
    if len(desc) > indice.LIMITE_DESCRICAO and _entra_em_indice(arq, refs_indexadas):
        return Achado(arq, DESCRICAO_LONGA, motivo=str(len(desc)))
    return None


def relatorio(achados: list[Achado], todas: bool = False) -> str:
    """Texto para o usuário — o mesmo que ele veria num aviso de sessão, só que
    reunido e antes de a sessão quebrar."""
    if not achados:
        return "Frontmatter: nenhum problema encontrado.\n"
    linhas = [f"Frontmatter: {len(achados)} arquivo(s) para corrigir.\n"]
    longas = [a for a in achados if a.estado == DESCRICAO_LONGA]
    resumir = not todas and len(longas) >= LIMIAR_RESUMO
    if resumir:
        linhas += _resumo_descricoes(longas)
    for a in achados:
        if resumir and a.estado == DESCRICAO_LONGA:
            continue
        if a.estado == REFS_AUSENTE:
            linhas.append(f"  ✗ {a.arquivo}")
            linhas.append("      o escopo desta pasta aponta para uma pasta-referências")
            linhas.append("      que não existe no disco:")
            linhas.append(f"        {a.motivo}")
            linhas.append("      A sessão abre, mas sem o índice das referências.")
            linhas.append("      Causa mais comum no Windows: `Documentos`, `Área de")
            linhas.append("      Trabalho` ou `Imagens` redirecionados para o OneDrive")
            linhas.append("      corporativo. O Explorer mostra a pasta no lugar antigo,")
            linhas.append("      e o caminho físico do perfil fica vazio — o escopo")
            linhas.append("      precisa apontar para o caminho real, dentro do OneDrive.")
        elif a.estado == SEM_FICHA:
            linhas.append(f"  ✗ {a.arquivo}")
            linhas.append("      sem `escopo:` no frontmatter — a Ficha Koine está")
            linhas.append("      faltando. A sessão não abre nesta pasta enquanto isso.")
            linhas.append("      Abra uma sessão aqui (`kn-<cliente> hermes <pasta>`) que o")
            linhas.append("      Hermes repõe a ficha preservando o que já está escrito.")
        elif a.estado == AGENTE_SEM_DEFAULT:
            linhas.append(f"  ⚠ {a.arquivo}")
            if a.motivo:
                linhas.append(f"      `agente-default` aponta para `{a.motivo}`, que não")
                linhas.append(f"      existe em {os.path.dirname(a.arquivo)}/agentes/.")
            elif len(a.chaves) == 1:
                linhas.append(f"      você tem 1 agente (`{a.chaves[0]}`) e nenhum")
                linhas.append("      `agente-default` gravado.")
            else:
                agentes = ", ".join(f"`{n}`" for n in a.chaves)
                linhas.append(f"      você tem {len(a.chaves)} agentes ({agentes}) e")
                linhas.append("      nenhum `agente-default` gravado.")
            linhas.append("      Pasta sem `agente:` próprio abre com Hermes até")
            linhas.append("      corrigir. Rode `koine definir-agente <nome> --default`.")
        elif a.estado == GLOSSARIO_SOLTO:
            linhas.append(f"  ⚠ {a.arquivo}")
            linhas.append("      este glossário está na pasta-referências mas não")
            linhas.append("      aparece no índice: falta o `dominios:` que o")
            linhas.append("      cataloga. Nada foi alterado, e a sessão continua")
            linhas.append("      funcionando — mas só quem souber que ele existe")
            linhas.append("      vai abri-lo. `/kn-15-mantem-glossario` regulariza.")
        elif a.estado == DESCRICAO_LONGA:
            linhas.append(f"  ⚠ {a.arquivo}")
            linhas.append(f"      a `description` tem {a.motivo} caracteres, e o")
            linhas.append(f"      índice mostra os primeiros {indice.LIMITE_DESCRICAO}.")
            linhas.append("      Nada foi alterado: o arquivo está inteiro, e a")
            linhas.append("      sessão continua funcionando. Encurte quando quiser")
            linhas.append("      que a linha do catálogo diga tudo por si.")
        elif a.estado == REPARAVEL:
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


def _resumo_descricoes(longas: list[Achado]) -> list[str]:
    """O bloco que substitui N linhas iguais por um número e as maiores.

    As maiores primeiro porque é onde o corte rende mais: numa `description` de
    1.874 caracteres o índice mostra 11% dela; numa de 250, 80%.
    """
    total = sum(int(a.motivo) for a in longas)
    linhas = [f"  ⚠ {len(longas)} referências com `description` acima de "
              f"{indice.LIMITE_DESCRICAO} caracteres",
              f"      Somam {total} caracteres, dos quais o índice mostra "
              f"{len(longas) * indice.LIMITE_DESCRICAO}.",
              "      Nada foi alterado: os arquivos estão inteiros e a sessão",
              "      continua funcionando. Encurtar é opcional — comece por estas,",
              "      onde rende mais (`--todas` lista o resto):"]
    maiores = sorted(longas, key=lambda a: -int(a.motivo))[:MAIORES_NO_RESUMO]
    linhas += [f"        {a.motivo:>5}  {a.arquivo}" for a in maiores]
    return linhas


def corrigir(achados: list[Achado]) -> tuple[list[Achado], list[Achado]]:
    """Normaliza os reparáveis. Devolve (corrigidos, pendentes) — pendente é o
    que o Koine não sabe consertar, e continua sendo decisão do usuário.

    `AGENTE_SEM_DEFAULT` só corrige no caso INEQUÍVOCO — 1 agente, `motivo`
    vazio (default nunca gravado, não apontando para algo que sumiu). Default
    torto ou 2+ agentes ficam pendentes: não há o que adivinhar."""
    from koine import agente as _a
    from koine import ficha
    corrigidos, pendentes = [], []
    for a in achados:
        if a.estado == REPARAVEL and ficha.normalizar_arquivo(a.arquivo):
            corrigidos.append(a)
        elif (a.estado == AGENTE_SEM_DEFAULT and len(a.chaves) == 1 and not a.motivo
              and ficha.definir_campo_arquivo(a.arquivo, _a.CAMPO_DEFAULT, a.chaves[0])):
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
