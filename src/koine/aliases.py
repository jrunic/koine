import json
import os
from pathlib import Path

from koine import paths


def config_path() -> str:
    return os.path.join(paths.config_dir(), "aliases.json")


def carregar() -> dict:
    p = config_path()
    if not os.path.exists(p):
        return {"pastas": {}}
    with open(p, encoding="utf-8") as f:
        dados = json.load(f)
    dados.setdefault("pastas", {})
    return dados


def salvar(a: dict) -> None:
    os.makedirs(os.path.dirname(config_path()), exist_ok=True)
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(a, f, indent=2)
        f.write("\n")


def resolver(a: dict, chave: str) -> str | None:
    e = a.get("pastas", {}).get(chave)
    if not e:
        return None
    if e["from"] == "home":
        return os.path.join(str(Path.home()), e["path"])
    if e["from"] == "abs":
        return e["path"]
    return None


def adicionar(chave: str, path: str, from_: str) -> None:
    a = carregar()
    a["pastas"][chave] = {"path": path, "from": from_}
    salvar(a)
