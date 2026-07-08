import os
import shutil
from pathlib import Path

from koine import paths

HARNESS_SKILLS = {
    "claude": ".claude/skills",
    "agy": ".gemini/antigravity-cli/skills",
    "copilot": ".copilot/skills",
    "opencode": ".config/opencode/skills",
    "codex": ".agents/skills",
}


def _arvore(base: str) -> dict:
    out = {}
    for raiz, _, arqs in os.walk(base):
        for a in arqs:
            p = os.path.join(raiz, a)
            with open(p, "rb") as f:
                out[os.path.relpath(p, base)] = f.read()
    return out


def instalar_habilidades(harness: str, force: bool = False) -> list[str]:
    """Copia os dirs kn-* de VaultDir()/habilidades para a pasta de skills do
    harness (~/<rel>). COPIA (não symlink: Windows exige admin).
    Idempotente e NÃO-destrutivo: dir idêntico é pulado; divergente é
    REPORTADO (retornado) e preservado, salvo `force=True`.
    Retorna a lista de skills DIVERGENTES não sobrescritas."""
    rel = HARNESS_SKILLS.get(harness)
    if rel is None:
        raise ValueError(f"harness {harness!r} não suportado ({', '.join(sorted(HARNESS_SKILLS))})")
    dest_dir = os.path.join(str(Path.home()), *rel.split("/"))
    os.makedirs(dest_dir, exist_ok=True)
    origem = os.path.join(paths.vault_dir(), "habilidades")
    if not os.path.isdir(origem):
        raise FileNotFoundError(f"{origem} — rode `koine instalar` primeiro")

    divergencias = []
    for nome in sorted(os.listdir(origem)):
        src = os.path.join(origem, nome)
        if not os.path.isdir(src) or not nome.startswith("kn-"):
            continue
        dst = os.path.join(dest_dir, nome)
        if os.path.isdir(dst):
            if _arvore(src) == _arvore(dst):
                continue                       # idêntico → pula
            if not force:
                divergencias.append(nome)      # divergente → reporta, NÃO destrói
                continue
            shutil.rmtree(dst)                 # só com force
        shutil.copytree(src, dst)
    return divergencias
