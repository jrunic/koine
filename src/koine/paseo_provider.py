"""Entries de provider Koine no config do Paseo (jd-task #881)."""
import copy
import os
import sys
from dataclasses import dataclass

from koine.paseo import matriz as _matriz_real
from koine.paseo_configurar import RecusaErro, _obj
from koine.paseo_diagnostico import AUSENTE, busca


class EntryDelta:
    def __init__(self, ident: str, acao: str):
        self.id = ident
        self.acao = acao


def _aplicar_entry(existente: dict | None, desejado: dict, ident: str) -> tuple[dict, str]:
    if existente is None:
        return copy.deepcopy(desejado), "plantado"
    if not isinstance(existente, dict):
        raise RecusaErro("tipo", f"`agents.providers.{ident}` deveria ser objeto.")
    if "command" in existente and not isinstance(existente["command"], list):
        raise RecusaErro("tipo", f"`command` de {ident} deveria ser lista.")
    novo = copy.deepcopy(existente)
    mudou = False
    if novo.get("extends") != desejado["extends"]:
        novo["extends"] = desejado["extends"]
        mudou = True
    if novo.get("label") != desejado["label"]:
        novo["label"] = desejado["label"]
        mudou = True
    if novo.get("command") != desejado["command"]:
        novo["command"] = list(desejado["command"])
        mudou = True
    env = dict(novo.get("env") or {})
    if "env" in desejado:
        if env.get("KOINE_AGENTE") != desejado["env"].get("KOINE_AGENTE"):
            env["KOINE_AGENTE"] = desejado["env"]["KOINE_AGENTE"]
            mudou = True
        novo["env"] = env
    else:
        if "KOINE_AGENTE" in env:
            del env["KOINE_AGENTE"]
            mudou = True
        if env:
            novo["env"] = env
        elif "env" in novo:
            del novo["env"]
    return novo, ("atualizado" if mudou else "inalterado")


def mesclar_providers(cfg: dict, matriz: dict) -> tuple[dict, list]:
    novo = copy.deepcopy(cfg)
    agents = _obj(novo, "agents", "agents")
    providers = _obj(agents, "providers", "agents.providers")
    deltas = []
    for cliente, info in matriz.items():
        # O command do entry leva SÓ o caminho: o subcomando do protocolo é
        # injetado pelo launch (cli.py, prefixo da rota). Declará-lo aqui
        # também duplicava o `acp` no spawn — medido em campo, 15/09.
        desejado_g = {
            "extends": info["extends"],
            "label": f"Koine · {cliente}",
            "command": [info["caminho"]],
        }
        desejado_h = {
            "extends": info["extends"],
            "label": f"Koine · {cliente} Hermes",
            "command": [info["caminho"]],
            "env": {"KOINE_AGENTE": "hermes"},
        }
        for ident, desejado in (
            (info["provider"], desejado_g),
            (info["provider_hermes"], desejado_h),
        ):
            atual = providers[ident] if ident in providers else None
            entry, acao = _aplicar_entry(atual, desejado, ident)
            providers[ident] = entry
            deltas.append(EntryDelta(ident, acao))
    return novo, deltas


def _executavel(caminho: str) -> bool:
    if not caminho or not os.path.isfile(caminho):
        return False
    if sys.platform == "win32" and caminho.lower().endswith((".cmd", ".bat")):
        return True  # quem decide é o cmd.exe /c, não o bit POSIX
    return os.access(caminho, os.X_OK)


def preparar(cfg: dict, matriz: dict) -> tuple[dict, list]:
    if busca(cfg, "daemon.relay.enabled") is AUSENTE:
        raise RecusaErro(
            "sem-relay",
            "não há daemon.relay.enabled no config. Rode `koine paseo-configurar`.")
    faltam = [i["wrapper"] for i in matriz.values() if not i.get("caminho")]
    if faltam:
        raise RecusaErro(
            "wrapper-ausente",
            "wrappers ausentes: " + ", ".join(faltam) + ". Rode `koine instalar`.")
    mortos = [i["caminho"] for i in matriz.values() if not _executavel(i["caminho"])]
    if mortos:
        raise RecusaErro(
            "wrapper-morto",
            "wrapper não executável: " + ", ".join(mortos))
    return mesclar_providers(cfg, matriz)


def matriz():
    return _matriz_real()


@dataclass
class ResultadoProv:
    entries: list
    gravou: bool
    caminho: str
    dry_run: bool = False


def aplicar(*, dry_run=False, home=None):
    from koine import paseo_configurar as pc
    home = home or pc.home_para_escrita()
    caminho = pc.caminho_config(home)
    if not os.path.lexists(caminho):
        raise RecusaErro(
            "sem-arquivo",
            "não há config. Rode `koine paseo-configurar`.")
    atual, _ = pc._ler(caminho)
    if atual is None:
        raise RecusaErro(
            "sem-arquivo",
            "não há config. Rode `koine paseo-configurar`.")
    novo, deltas = preparar(atual, matriz())
    if all(d.acao == "inalterado" for d in deltas):
        return ResultadoProv(entries=deltas, gravou=False, caminho=caminho,
                             dry_run=dry_run)
    if dry_run:
        return ResultadoProv(entries=deltas, gravou=False, caminho=caminho,
                             dry_run=True)
    gravou, caminho, _, _ = pc.escrever(novo, dry_run=False, home=home)
    return ResultadoProv(entries=deltas, gravou=gravou, caminho=caminho,
                         dry_run=False)
