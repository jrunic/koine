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

# binário de detecção no PATH — no Koine, nome do harness == nome do binário
# (espelha binarioHarness de instalar_habilidades.go)
BINARIO_HARNESS = {h: h for h in HARNESS_SKILLS}


def detectar_harnesses() -> list[str]:
    """Porta de detectarHarnesses: harnesses cujo binário está no PATH,
    em ordem alfabética."""
    return sorted(h for h, b in BINARIO_HARNESS.items() if shutil.which(b))


def _arvore(base: str) -> dict:
    out = {}
    for raiz, _, arqs in os.walk(base):
        for a in arqs:
            p = os.path.join(raiz, a)
            with open(p, "rb") as f:
                out[os.path.relpath(p, base)] = f.read()
    return out


def instalar_habilidades_detalhado(
        harness: str, force: bool = False) -> tuple[list[str], list[str], list[str]]:
    """Copia os dirs kn-* de VaultDir()/habilidades para a pasta de skills do
    harness (~/<rel>). COPIA (não symlink: Windows exige admin).
    Idempotente e NÃO-destrutivo: dir idêntico é pulado; divergente é
    REPORTADO e preservado, salvo `force=True`.
    Retorna (criadas, existentes, divergentes) — espelha
    instalarHabilidadesParaHarness do Go (criados/jaExistiam), com o eixo
    extra de divergentes que o mecanismo de cópia introduz."""
    rel = HARNESS_SKILLS.get(harness)
    if rel is None:
        raise ValueError(f"harness {harness!r} não suportado ({', '.join(sorted(HARNESS_SKILLS))})")
    dest_dir = os.path.join(str(Path.home()), *rel.split("/"))
    os.makedirs(dest_dir, exist_ok=True)
    origem = os.path.join(paths.vault_dir(), "habilidades")
    if not os.path.isdir(origem):
        raise FileNotFoundError(f"{origem} — rode `koine instalar` primeiro")

    criadas, existentes, divergentes = [], [], []
    for nome in sorted(os.listdir(origem)):
        src = os.path.join(origem, nome)
        if not os.path.isdir(src) or not nome.startswith("kn-"):
            continue
        dst = os.path.join(dest_dir, nome)
        if os.path.isdir(dst):
            if _arvore(src) == _arvore(dst):
                existentes.append(nome)        # idêntico → pula
                continue
            if not force:
                divergentes.append(nome)       # divergente → reporta, NÃO destrói
                continue
            shutil.rmtree(dst)                 # só com force
            shutil.copytree(src, dst)
            criadas.append(nome)
            continue
        shutil.copytree(src, dst)
        criadas.append(nome)
    return criadas, existentes, divergentes


def instalar_habilidades(harness: str, force: bool = False) -> list[str]:
    """Delegação para instalar_habilidades_detalhado preservando a assinatura
    original: retorna só a lista de skills DIVERGENTES não sobrescritas."""
    _, _, divergentes = instalar_habilidades_detalhado(harness, force=force)
    return divergentes
