import os
import shutil
from pathlib import Path

from koine import backup, paths

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
        harness: str, versao: str) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """Copia os dirs kn-* de VaultDir()/habilidades para a pasta de skills do
    harness (~/<rel>). COPIA (não symlink: Windows exige admin).

    Idempotente: dir idêntico é pulado; **divergente é ATUALIZADO**, com o
    anterior guardado na árvore de backups do cache. Devolve
    (criadas, existentes, atualizadas), onde `atualizadas` é [(nome, backup)].

    `versao` é a que está entrando — no `atualizar`, o pyz em execução ainda é o
    antigo, então ler `__version__` aqui gravaria o backup na pasta errada.
    """
    rel = HARNESS_SKILLS.get(harness)
    if rel is None:
        raise ValueError(f"harness {harness!r} não suportado ({', '.join(sorted(HARNESS_SKILLS))})")
    dest_dir = os.path.join(str(Path.home()), *rel.split("/"))
    os.makedirs(dest_dir, exist_ok=True)
    origem = os.path.join(paths.vault_dir(), "habilidades")
    if not os.path.isdir(origem):
        raise FileNotFoundError(f"{origem} — rode `koine instalar` primeiro")

    criadas, existentes, atualizadas = [], [], []
    for nome in sorted(os.listdir(origem)):
        src = os.path.join(origem, nome)
        if not os.path.isdir(src) or not nome.startswith("kn-"):
            continue
        dst = os.path.join(dest_dir, nome)
        if os.path.isdir(dst):
            if _arvore(src) == _arvore(dst):
                existentes.append(nome)        # idêntico → pula
                continue
            bak = backup.guardar(dst, versao, f"harness/{harness}", nome)
            _trocar_dir(src, dst)
            atualizadas.append((nome, bak))
            continue
        shutil.copytree(src, dst)
        criadas.append(nome)
    return criadas, existentes, atualizadas


def _trocar_dir(src: str, dst: str) -> None:
    """Monta a árvore nova ao lado e troca no fim.

    O nome temporário começa com ponto de propósito: não casa o filtro `kn-*`,
    então nem o instalador nem o cliente o enxergam como skill enquanto existe.
    """
    pai = os.path.dirname(dst)
    tmp = os.path.join(pai, "." + os.path.basename(dst) + ".koine-novo")
    if os.path.lexists(tmp):
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    shutil.rmtree(dst)
    os.replace(tmp, dst)


def instalar_habilidades(harness: str, versao: str) -> list[tuple[str, str]]:
    """Delegação que devolve só as skills atualizadas, com o backup de cada uma."""
    _, _, atualizadas = instalar_habilidades_detalhado(harness, versao)
    return atualizadas
