# src/koine/agente.py
"""Quem decide o agente da sessão — e de onde veio a decisão.

A fonte não é enfeite: o tratamento de agente inexistente bifurca por ela.
Posicional errado é dedo humano no teclado e recebe erro com a lista; valor
errado gravado num arquivo não tem o que redigitar, e recebe Hermes com a
instrução de corrigir. Sem devolver a fonte, os dois casos ficam
indistinguíveis no consumidor.
"""
import os

POSICIONAL = "posicional"
PASTA = "pasta"
DEFAULT = "default"
FALLBACK = "fallback"

CAMPO_PASTA = "agente"
CAMPO_DEFAULT = "agente-default"
HERMES = "hermes"


def resolver_nome(posicional: str, fm_pasta: dict,
                  default_usuario: str) -> tuple[str, str]:
    """(nome, fonte), na precedência da spec: posicional → pasta → default →
    hermes. Vale só em pasta VALIDO; os outros estados forçam Hermes antes de
    chegar aqui."""
    if posicional:
        return posicional, POSICIONAL
    declarado = (fm_pasta.get(CAMPO_PASTA) or "").strip()
    if declarado:
        return declarado, PASTA
    if default_usuario:
        return default_usuario, DEFAULT
    return HERMES, FALLBACK


def default_do_usuario(usuario_path: str, ler_fm) -> str:
    """Lê `agente-default:` do arquivo do usuário. Sem arquivo resolvível —
    nenhum, ou mais de um `.md` na raiz do config — não há default, e o
    fallback é Hermes SEM erro. Não inventar desempate aqui."""
    if not usuario_path or not os.path.exists(usuario_path):
        return ""
    try:
        fm, _ = ler_fm(usuario_path)
    except Exception:
        return ""
    return (fm.get(CAMPO_DEFAULT) or "").strip()


def agentes_operacionais(cfg: str) -> list[str]:
    """Nomes dos agentes do usuário em `config/agentes/` — nunca inclui
    Hermes, que mora no vault, não na config."""
    try:
        return sorted(f[:-3] for f in os.listdir(os.path.join(cfg, "agentes"))
                      if f.endswith(".md"))
    except FileNotFoundError:
        return []


def usuario_path(cfg: str) -> str:
    """Caminho do único `.md` na raiz de `cfg`, ou vazio se ausente/ambíguo.
    Mesma regra de `contexto._achar_usuario_opcional` — duplicada aqui porque
    lá é privada e este módulo não depende de `contexto` (evita ciclo)."""
    try:
        mds = [f for f in os.listdir(cfg) if f.endswith(".md")]
    except FileNotFoundError:
        return ""
    return os.path.join(cfg, mds[0]) if len(mds) == 1 else ""


def unico_sem_default(cfg: str, ler_fm) -> str:
    """Nome do agente, se este é o caso INEQUÍVOCO de default ausente: um
    único agente operacional, e nenhum default válido gravado. Vazio nos
    demais casos — 0 agentes (Hermes está certo), 2+ (ambíguo, não se
    adivinha) ou default já apontando para um agente que existe."""
    agentes = agentes_operacionais(cfg)
    if len(agentes) != 1:
        return ""
    default = default_do_usuario(usuario_path(cfg), ler_fm)
    return agentes[0] if default not in agentes else ""


def migrar_default_inequivoco(cfg: str) -> str:
    """Se o caso for inequívoco, grava sozinho e devolve o nome gravado;
    senão devolve "" sem tocar em nada.

    Existe porque `koine definir-agente --default` e a regra "primeiro
    agente vira default" só nasceram na v0.7.0 (28/08/2026, commit
    de79540) — quem criou o único agente antes disso nunca teve chance de
    ganhar o default automático, e `koine atualizar`/`instalar` nunca
    tocava na configuração do usuário para consertar isso depois. O
    sintoma: pasta sem `agente:` próprio abre com Hermes, silenciosamente,
    mesmo para quem tem um agente do dia a dia havia meses. Medido em
    produção em 21/09/2026 (usuária com 1 agente e 30+ pastas via /kn-14) —
    e reproduzido nesta própria instalação de desenvolvimento.
    """
    from koine import ficha, frontmatter as _fm
    nome = unico_sem_default(cfg, _fm.ler_arquivo)
    if not nome:
        return ""
    alvo = usuario_path(cfg)
    if alvo and ficha.definir_campo_arquivo(alvo, CAMPO_DEFAULT, nome):
        return nome
    return ""
