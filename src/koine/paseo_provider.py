"""Entries de provider Koine no config do Paseo (jd-task #881)."""
import copy
import os
from dataclasses import dataclass

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
    for info in matriz.values():
        desejado_g = {
            "extends": info["extends"],
            "command": [info["caminho"], *info["args"]],
        }
        desejado_h = {
            "extends": info["extends"],
            "command": [info["caminho"], *info["args"]],
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
