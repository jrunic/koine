import os
from dataclasses import dataclass, field

from koine import agente as _agente
from koine import bootstrap as _bootstrap
from koine import frontmatter, paths, schema


class AgenteNaoEncontrado(Exception):
    """Nenhum arquivo de agente casa com o nome pedido. Carrega dados (nome +
    disponíveis); cli/mensagens decidem prosa e política. Padrão
    ClienteNaoEncontrado (launch.py)."""

    def __init__(self, agente: str, disponiveis: list[str]):
        self.agente = agente
        self.disponiveis = disponiveis
        super().__init__(agente)


class EscopoNaoEncontrado(Exception):
    """O CONTEXTO.md declara um `escopo:` que não existe em config/escopos.
    Dado do usuário, não defeito: erro nomeado em vez de FileNotFoundError cru."""

    def __init__(self, escopo: str, disponiveis: list[str]):
        self.escopo = escopo
        self.disponiveis = disponiveis
        super().__init__(escopo)


def resolver_escopo_path(cfg: str, slug: str) -> str:
    """Path do escopo, ou EscopoNaoEncontrado listando os cadastrados."""
    p = os.path.join(cfg, "escopos", f"{slug}.md")
    if os.path.exists(p):
        return p
    try:
        disp = sorted(f[:-3] for f in os.listdir(os.path.join(cfg, "escopos"))
                      if f.endswith(".md"))
    except FileNotFoundError:
        disp = []
    raise EscopoNaoEncontrado(slug, disp)


@dataclass
class ContextoMontado:
    usuario_path: str = ""
    koine_path: str = ""
    agente_path: str = ""
    escopo_path: str = ""
    indice_paths: list[str] = field(default_factory=list)
    contexto_path: str = ""
    # Instrução do Koine para ESTA sessão, quando o estado da pasta exige que o
    # agente conduza algo antes do trabalho (hoje: pasta sem `escopo:`). Vazio na
    # sessão normal. Todo adapter que renderiza contexto_path renderiza esta também.
    instrucao_path: str = ""
    bootstrap: bool = False
    # Nome que a pasta (ou o default do usuário) declarava e que não existe.
    # Vazio na sessão normal. Quem decide o que fazer com isso é o CHAMADOR:
    # `resolver` não conhece o modo, e a spec manda guiar no interativo e
    # abortar sem tty.
    agente_ausente: str = ""
    # pasta de trabalho absoluta — preenchida por cli._montar_cm; adapters com
    # bundle externo (copilot, opencode) derivam slot e alvo de symlink dela.
    pasta_abs: str = ""


def _achar_usuario(cfg: str) -> str:
    mds = [f for f in os.listdir(cfg) if f.endswith(".md")]
    if len(mds) != 1:
        raise ValueError(f"esperado 1 arquivo de usuário em {cfg}, achei {mds}")
    return os.path.join(cfg, mds[0])


def _achar_usuario_opcional(cfg: str) -> str:
    mds = [f for f in os.listdir(cfg) if f.endswith(".md")]
    return os.path.join(cfg, mds[0]) if len(mds) == 1 else ""


def _achar_agente(cfg: str, data: str, agente: str) -> str:
    """Resolve o path do agente casando o nome (ignorando caixa) contra os
    arquivos reais. Duas casas: agentes de usuário vivem em config/agentes
    (kn-03-cria-agente grava lá); o agente distribuído (hermes) vive em
    vault/agentes. Busca config primeiro (override do usuário), depois vault.

    Duas armadilhas resolvidas de uma vez:
    - diretório: sem olhar config, agente de usuário nunca é achado (só hermes);
    - caixa: o slug é lowercase (leia.md), mas o arg do CLI pode vir 'Leia'.
      Casar por caixa crua só resolve em FS case-insensitive (macOS/Windows),
      sumindo o agente silenciosamente em FS case-sensitive (Linux/OpenClaw)."""
    alvo = f"{agente}.md".lower()
    disponiveis: list[str] = []
    for base in (os.path.join(cfg, "agentes"), os.path.join(data, "agentes")):
        try:
            arquivos = os.listdir(base)
        except FileNotFoundError:
            continue
        for f in arquivos:
            if f.lower() == alvo:
                return os.path.join(base, f)
        disponiveis += [f[:-3] for f in arquivos if f.endswith(".md")]
    raise AgenteNaoEncontrado(agente, sorted(set(disponiveis)))


def resolver(agente: str, pasta: str, sem_contexto: bool = False) -> ContextoMontado:
    cfg, data = paths.config_dir(), paths.vault_dir()
    ctx_path = os.path.join(pasta, "CONTEXTO.md")
    if sem_contexto:
        # Canal de máquina: a pasta não tem contexto e NÃO será escrita. Mesma
        # forma do ramo de pasta incompleta — bootstrap com instrução do vault —
        # sem `contexto_path`, porque não há arquivo do usuário para mostrar (e
        # nos estados vazio/malformado o que há não ajudaria o agente).
        return ContextoMontado(
            bootstrap=True,
            usuario_path=_achar_usuario_opcional(cfg),
            koine_path=os.path.join(data, "KOINE.md"),
            agente_path=os.path.join(data, "agentes", "hermes.md"),
            instrucao_path=_bootstrap.instrucao_pasta_fora_do_koine(data),
        )
    fm, _ = frontmatter.ler_arquivo(ctx_path, normalizar_disco=True)

    if fm.get("bootstrap"):
        return ContextoMontado(
            bootstrap=True,
            usuario_path=_achar_usuario_opcional(cfg),
            koine_path=os.path.join(data, "KOINE.md"),
            agente_path=os.path.join(data, "agentes", "hermes.md"),
            contexto_path=ctx_path,
        )

    if not fm.get("escopo"):
        # CONTEXTO.md do usuário sem escopo: entra em modo bootstrap SEM tocar no
        # arquivo. O agente recebe a instrução do vault e o arquivo original —
        # quem completa o frontmatter é o Hermes, via /kn-02 Fluxo 3b.
        return ContextoMontado(
            bootstrap=True,
            usuario_path=_achar_usuario_opcional(cfg),
            koine_path=os.path.join(data, "KOINE.md"),
            agente_path=os.path.join(data, "agentes", "hermes.md"),
            contexto_path=ctx_path,
            instrucao_path=_bootstrap.instrucao_pasta_incompleta(data),
        )

    escopo_slug = fm["escopo"]
    doms = fm.get("dominios", [])

    esc_path = resolver_escopo_path(cfg, escopo_slug)
    efm, _ = frontmatter.ler_arquivo(esc_path, normalizar_disco=True)
    escopo = schema.Escopo.from_fm(efm)
    refs = paths.resolver_tagged(escopo.pasta_referencias)

    nome, fonte = _agente.resolver_nome(
        posicional=agente,
        fm_pasta=fm,
        default_usuario=_agente.default_do_usuario(
            _achar_usuario_opcional(cfg), frontmatter.ler_arquivo),
    )
    try:
        agente_path = _achar_agente(cfg, data, nome)
    except AgenteNaoEncontrado:
        if fonte == _agente.POSICIONAL:
            raise                    # dedo no teclado: erro com a lista
        # Valor errado num arquivo: não há o que redigitar. O que fazer depende
        # do MODO, e `resolver` não conhece o modo — quem bifurca é o chamador.
        return ContextoMontado(
            bootstrap=True,
            usuario_path=_achar_usuario_opcional(cfg),
            koine_path=os.path.join(data, "KOINE.md"),
            agente_path=os.path.join(data, "agentes", "hermes.md"),
            contexto_path=ctx_path,
            instrucao_path=_bootstrap.instrucao_agente_inexistente(data),
            agente_ausente=nome,
        )

    return ContextoMontado(
        usuario_path=_achar_usuario(cfg),
        koine_path=os.path.join(data, "KOINE.md"),
        agente_path=agente_path,
        escopo_path=esc_path,
        indice_paths=[os.path.join(refs, f"kn-indice-{d}.md") for d in doms],
        contexto_path=ctx_path,
    )
