import os
from dataclasses import dataclass, field

from koine import frontmatter, paths, schema


class AgenteNaoEncontrado(Exception):
    """Nenhum arquivo de agente casa com o nome pedido. Carrega dados (nome +
    disponíveis); cli/mensagens decidem prosa e política. Padrão
    ClienteNaoEncontrado (launch.py)."""

    def __init__(self, agente: str, disponiveis: list[str]):
        self.agente = agente
        self.disponiveis = disponiveis
        super().__init__(agente)


@dataclass
class ContextoMontado:
    usuario_path: str = ""
    koine_path: str = ""
    agente_path: str = ""
    escopo_path: str = ""
    indice_paths: list[str] = field(default_factory=list)
    contexto_path: str = ""
    bootstrap: bool = False
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


def resolver(agente: str, pasta: str) -> ContextoMontado:
    cfg, data = paths.config_dir(), paths.vault_dir()
    ctx_path = os.path.join(pasta, "CONTEXTO.md")
    fm, _ = frontmatter.ler(open(ctx_path, encoding="utf-8").read())

    if fm.get("bootstrap"):
        return ContextoMontado(
            bootstrap=True,
            usuario_path=_achar_usuario_opcional(cfg),
            koine_path=os.path.join(data, "KOINE.md"),
            agente_path=os.path.join(data, "agentes", "hermes.md"),
            contexto_path=ctx_path,
        )

    escopo_slug = fm["escopo"]
    doms = fm.get("dominios", [])

    escopo_path = os.path.join(cfg, "escopos", f"{escopo_slug}.md")
    efm, _ = frontmatter.ler(open(escopo_path, encoding="utf-8").read())
    escopo = schema.Escopo.from_fm(efm)
    refs = paths.resolver_tagged(escopo.pasta_referencias)

    agente_path = _achar_agente(cfg, data, agente)

    return ContextoMontado(
        usuario_path=_achar_usuario(cfg),
        koine_path=os.path.join(data, "KOINE.md"),
        agente_path=agente_path,
        escopo_path=escopo_path,
        indice_paths=[os.path.join(refs, f"kn-indice-{d}.md") for d in doms],
        contexto_path=ctx_path,
    )
