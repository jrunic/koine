"""Auto-guiar: pasta de sessão sem CONTEXTO.md válido.

Só o caminho de launch (`cli._rodar_cliente`) materializa/roteia. `gerar`/`mostrar`
tratam CONTEXTO ausente como erro amigável — não materializam nada. Ver spec
20260724-spec-bootstrap-pasta-sessao no projeto criar-koine.

O Python decide o ramo (onboarded vs não) — não terceiriza pro agente:
- onboarded → materializa um CONTEXTO.md bootstrap "configurar pasta" e deixa o
  fluxo bootstrap existente lançar Hermes conduzindo `/kn-02` Fluxo 3a;
- não-onboarded → NÃO roda /kn-01 numa pasta aleatória; o chamador redireciona
  ao setup canônico (`koine instalar` + `kn-<cliente> hermes koine`).
"""

import os

from koine import frontmatter

# Estados do CONTEXTO.md numa pasta de trabalho.
AUSENTE = "ausente"        # arquivo não existe → auto-guiar
VAZIO = "vazio"            # existe mas vazio/sem frontmatter → auto-guiar
INCOMPLETO = "incompleto"  # FM parseia, sem `escopo` e sem `bootstrap` → auto-guiar preservando
MALFORMADO = "malformado"  # YAML irreparável ou arquivo ilegível → erro+preserva
BOOTSTRAP = "bootstrap"    # `bootstrap: true` → fluxo bootstrap (inalterado)
VALIDO = "valido"          # `escopo:` presente → sessão normal (inalterado)

# CONTEXTO.md materializado para o ramo onboarded. Instrui Hermes a conduzir a
# criação do CONTEXTO real desta pasta via /kn-02 Fluxo 3a. Transitório: ao fim
# da entrevista o arquivo vira um CONTEXTO com escopo real. Sem marcador Koine de
# propósito — precisa começar em `---` para o frontmatter.ler reconhecer bootstrap.
CONTEXTO_CONFIGURA_PASTA = """---
bootstrap: true
---

# Bootstrap Koine — configurar pasta

Esta pasta ainda não tem contexto Koine. O usuário abriu uma sessão aqui e o
Koine detectou a ausência de um `CONTEXTO.md` configurado. O usuário já fez o
onboarding (tem perfil), mas esta pasta de trabalho é nova.

## Instruções para o agente

**Hermes:** estamos configurando uma pasta de trabalho nova. Inicie
imediatamente o skill `/kn-02-mantem-catalogo` no **Fluxo 3 (Pasta de
trabalho)**, sub-fluxo 3a (criar `CONTEXTO.md` novo). Não espere o usuário
invocar a skill — ele acabou de abrir a sessão e ainda não sabe que ela existe.

Conduza: inspecione a pasta, pergunte o **escopo** (liste os disponíveis em
`~/.config/koine/escopos/`), a **descrição** e os **domínios**. Ao final, esta
pasta terá um `CONTEXTO.md` real com escopo e domínios, e o usuário pode reabrir
a sessão com o agente operacional que quiser.
"""


def classificar(pasta: str) -> str:
    """Estado do CONTEXTO.md em `pasta`. Segue symlink na leitura (open); o
    guard de symlink/diretório na materialização fica no chamador."""
    ctx = os.path.join(pasta, "CONTEXTO.md")
    if not os.path.exists(ctx):
        return AUSENTE
    try:
        with open(ctx, encoding="utf-8") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        # ilegível/binário → trata como malformado: erro amigável, nunca clobber
        return MALFORMADO
    if not texto.strip():
        return VAZIO
    try:
        fm, _ = frontmatter.ler(texto)
    except frontmatter.FrontmatterInvalido:
        # YAML que nem o reparo salva → malformado: erro amigável, nunca clobber.
        # Frontmatter ruim é dado ruim numa pasta, não motivo para o Koine cair.
        return MALFORMADO
    return estado_do_fm(fm)


def estado_do_fm(fm: dict) -> str:
    """Estado de um CONTEXTO.md já parseado: BOOTSTRAP, VALIDO ou INCOMPLETO.

    Fonte única do critério. O launch (`classificar`) e o `koine validar` leem
    daqui — duas definições separadas divergem com o tempo, e aí a ferramenta
    que deveria avisar antes passa a discordar da que barra na hora."""
    if fm.get("bootstrap"):
        return BOOTSTRAP
    if fm.get("escopo"):
        return VALIDO
    # Arquivo do usuário, legível, só sem escopo. Foi erro fatal até a v0.6.0 e
    # travou um usuário em produção: a saída oferecida era editar YAML à mão.
    # Vira auto-guiar — sem tocar no arquivo, que é trabalho do usuário.
    return INCOMPLETO


def erro_frontmatter(pasta: str) -> frontmatter.FrontmatterInvalido | None:
    """Por que o CONTEXTO.md desta pasta é MALFORMADO: YAML irreparável (devolve
    o erro, com linha e coluna) ou arquivo ilegível/binário (devolve None).
    Só o caminho de erro paga essa releitura."""
    try:
        frontmatter.ler_arquivo(os.path.join(pasta, "CONTEXTO.md"))
    except frontmatter.FrontmatterInvalido as e:
        return e
    except OSError:
        return None
    return None


def usuario_onboarded(cfg: str) -> bool:
    """True se existe ao menos um arquivo de usuário na raiz de `~/.config/koine/`.
    Só arquivos de usuário (`<nome>.md`) vivem na raiz — escopos/dominios/agentes
    são subpastas. Ausência do dir → não-onboarded."""
    try:
        return any(f.endswith(".md") for f in os.listdir(cfg))
    except FileNotFoundError:
        return False


# Instrução lida pelo agente quando a pasta cai em INCOMPLETO. Mora no vault
# (asset versionado, revisável) em vez de ser gerada em runtime: o Koine não
# escreve nada na pasta do usuário nesse ramo.
INSTRUCAO_PASTA_INCOMPLETA = ("bootstrap", "pasta-incompleta.md")


def instrucao_pasta_incompleta(vault: str) -> str:
    return os.path.join(vault, *INSTRUCAO_PASTA_INCOMPLETA)


def instrucao_pasta_fora_do_koine(vault: str) -> str:
    """Instrução para sessão aberta por canal de máquina numa pasta sem contexto.

    O auto-guiar da v0.4.5 materializa um CONTEXTO.md de bootstrap, e isso é
    certo no terminal: lá o usuário fez `cd` de propósito. Por um orquestrador
    não vale o mesmo — as sondagens rodam com o cwd de onde o serviço subiu, e
    materializar escreveria na pasta de downloads de quem nunca pediu nada
    (medido em 29/08/2026). Aqui o Koine avisa e não toca em nada.
    """
    return os.path.join(vault, "bootstrap", "pasta-fora-do-koine.md")


def instrucao_agente_inexistente(data: str) -> str:
    """Instrução lida pelo agente quando a pasta (ou o default do usuário)
    declara um agente que não existe. Mesmo canal da pasta incompleta: o Koine
    não escreve nada para consertar — quem corrige é o agente, conversando."""
    return os.path.join(data, "bootstrap", "agente-inexistente.md")


def instrucao_escopo_inexistente(data: str) -> str:
    """Instrução lida pelo agente quando o `escopo:` declarado não existe.

    A pasta é VÁLIDA — ficha completa, campo preenchido —, e o que sumiu é o
    cadastro. Escopo renomeado ou apagado põe nesse estado TODAS as pastas que o
    declaravam, então a correção que interessa é no catálogo, não numa pasta.
    """
    return os.path.join(data, "bootstrap", "escopo-inexistente.md")


def instrucao_agente_do_canal_inexistente(data: str) -> str:
    """Irmã da `instrucao_agente_inexistente`, para quando o nome veio do
    CHAMADOR e não do arquivo da pasta — no canal de máquina, do entry do
    provider. A remediação é outra: `definir-agente` conserta o campo da pasta,
    e o aviso voltaria para sempre porque o defeito está na configuração do
    orquestrador."""
    return os.path.join(data, "bootstrap", "agente-do-canal-inexistente.md")


def bloco_do_contexto(pasta: str) -> str:
    """O bloco de frontmatter do CONTEXTO.md, COM os delimitadores — no formato
    em que voltará ao arquivo. Vazio quando não há bloco."""
    try:
        with open(os.path.join(pasta, "CONTEXTO.md"), encoding="utf-8",
                  newline="") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        return ""
    fatia = frontmatter.fatiar_publico(texto)
    return texto[:fatia.fim_do_bloco] if fatia else ""
