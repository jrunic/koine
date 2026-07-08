import json
import os
from datetime import datetime, timezone

from koine import paths


def extrair(vault_src: str, versao: str, force: bool = False) -> list[str]:
    """Extrai vault_src → XDG. dominios/ vão para ConfigDir; templates/ e
    .gitkeep são pulados. Idempotente: idêntico pula; divergente sem force é
    reportado (retornado), não sobrescrito. Retorna lista de divergências."""
    vault_dir = paths.vault_dir()
    config_dir = paths.config_dir()
    os.makedirs(vault_dir, exist_ok=True)
    for sub in ("dominios", "escopos", "agentes"):
        os.makedirs(os.path.join(config_dir, sub), exist_ok=True)

    divergencias: list[str] = []
    for raiz, dirs, arqs in os.walk(vault_src):
        rel_dir = os.path.relpath(raiz, vault_src)
        rel_dir = "" if rel_dir == "." else rel_dir.replace(os.sep, "/")

        # cria dirs vazios do vault para casar o os.MkdirAll do Go
        if rel_dir and not rel_dir.startswith("templates") and not rel_dir.startswith("dominios"):
            os.makedirs(os.path.join(vault_dir, rel_dir), exist_ok=True)

        for a in arqs:
            if a == ".gitkeep":
                continue
            rel = f"{rel_dir}/{a}" if rel_dir else a
            if rel.startswith("templates/"):
                continue
            src = os.path.join(raiz, a)
            if rel.startswith("dominios/"):
                dest = os.path.join(config_dir, rel.replace("/", os.sep))
            else:
                dest = os.path.join(vault_dir, rel.replace("/", os.sep))
            _copiar(src, dest, force, divergencias)

    _gravar_meta(vault_dir, versao)
    return divergencias


def _copiar(src: str, dest: str, force: bool, divergencias: list[str]) -> None:
    with open(src, "rb") as f:
        data = f.read()
    if os.path.exists(dest):
        with open(dest, "rb") as f:
            if f.read() == data:
                return
        if not force:
            divergencias.append(dest)
            return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)


def _gravar_meta(vault_dir: str, versao: str) -> None:
    meta = {"versao": versao,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(vault_dir, ".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")
