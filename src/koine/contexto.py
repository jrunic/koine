import os
from dataclasses import dataclass, field

from koine import frontmatter, paths, schema


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

    agente_path = os.path.join(data, "agentes", f"{agente}.md")

    return ContextoMontado(
        usuario_path=_achar_usuario(cfg),
        koine_path=os.path.join(data, "KOINE.md"),
        agente_path=agente_path,
        escopo_path=escopo_path,
        indice_paths=[os.path.join(refs, f"kn-indice-{d}.md") for d in doms],
        contexto_path=ctx_path,
    )
