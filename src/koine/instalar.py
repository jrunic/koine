import json
import os
import tempfile
from datetime import datetime, timezone

from koine import backup, paths


def extrair(vault_src: str, versao: str,
            force: bool = False) -> tuple[list[tuple[str, str]], list[str]]:
    """Extrai vault_src → XDG. Devolve (trocas, preservados).

    A decisão é propriedade do TIPO do artefato, não do chamador:
      - shipped  → divergente SEMPRE atualiza, com o anterior guardado no cache
      - dominios → do usuário; preservado e reportado, salvo force

    `versao` é a que está entrando, e é ela que nomeia a pasta do backup.
    O parâmetro `atualizar_vault` deixou de existir: forçar o vault era
    justamente a divergência entre `instalar` e `atualizar` que esta mudança
    fecha.
    """
    vault_dir = paths.vault_dir()
    config_dir = paths.config_dir()
    os.makedirs(vault_dir, exist_ok=True)
    for sub in ("dominios", "escopos", "agentes"):
        os.makedirs(os.path.join(config_dir, sub), exist_ok=True)

    trocas: list[tuple[str, str]] = []
    preservados: list[str] = []
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
                _copiar_do_usuario(src, dest, force, preservados)
            else:
                dest = os.path.join(vault_dir, rel.replace("/", os.sep))
                _copiar_shipped(src, dest, versao, rel, trocas)

    _gravar_meta(vault_dir, versao)
    return trocas, preservados


def _copiar_shipped(src: str, dest: str, versao: str, rel: str,
                    trocas: list[tuple[str, str]]) -> None:
    with open(src, "rb") as f:
        data = f.read()
    if os.path.exists(dest):
        with open(dest, "rb") as f:
            if f.read() == data:
                return
        bak = backup.guardar(dest, versao, "vault", rel)
        trocas.append((dest, bak))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    _gravar_atomico(dest, data)


def _copiar_do_usuario(src: str, dest: str, force: bool,
                       preservados: list[str]) -> None:
    with open(src, "rb") as f:
        data = f.read()
    if os.path.exists(dest):
        with open(dest, "rb") as f:
            if f.read() == data:
                return
        if not force:
            preservados.append(dest)
            return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    _gravar_atomico(dest, data)


def _gravar_atomico(dest: str, data: bytes) -> None:
    """Grava por arquivo temporário + os.replace. Falha na escrita deixa o
    destino como estava, nunca truncado."""
    d = os.path.dirname(dest)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".koine-tmp-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, dest)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _gravar_meta(vault_dir: str, versao: str) -> None:
    meta = {"versao": versao,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(vault_dir, ".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")
