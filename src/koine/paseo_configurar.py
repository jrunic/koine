"""Escrita do config do Paseo — conjunto fechado (jd-task #880)."""
import json
import os
import shutil
import sys
from dataclasses import dataclass

from koine.paseo_diagnostico import home_do_paseo


class RecusaErro(Exception):
    def __init__(self, motivo: str, mensagem: str):
        super().__init__(mensagem)
        self.motivo = motivo
        self.mensagem = mensagem


@dataclass(frozen=True)
class Alteracao:
    chave: str
    antes: object
    depois: object


@dataclass
class Resultado:
    alteracoes: list[Alteracao]
    gravou: bool
    caminho: str
    dry_run: bool = False


def home_para_escrita() -> str:
    """Home onde ESTE comando pode gravar.

    Windows sem PASEO_HOME aborta: o default do produto ali não foi medido.
    Gravar em ~/.paseo fantasma é o defeito que a spec recusa.
    """
    if sys.platform == "win32" and "PASEO_HOME" not in os.environ:
        raise RecusaErro(
            "windows-sem-home",
            "neste sistema não medi onde o Paseo guarda o config. "
            "Defina PASEO_HOME ou rode em macOS/Linux.")
    return home_do_paseo()


def caminho_config(home: str) -> str:
    return os.path.join(home, "config.json")


def _obj(pai: dict, nome: str, caminho: str) -> dict:
    if nome not in pai:
        pai[nome] = {}
    if not isinstance(pai[nome], dict):
        raise RecusaErro(
            "tipo",
            f"`{caminho}` deveria ser objeto JSON e é {type(pai[nome]).__name__}.")
    return pai[nome]


def _forcar_true(cfg: dict, partes: list[str], alteracoes: list) -> None:
    atual = cfg
    caminho = []
    for parte in partes[:-1]:
        caminho.append(parte)
        atual = _obj(atual, parte, ".".join(caminho))
    ultima = partes[-1]
    chave = ".".join(partes)
    if ultima not in atual:
        atual[ultima] = True
        alteracoes.append(Alteracao(chave, None, True))
        return
    valor = atual[ultima]
    if not isinstance(valor, bool):
        raise RecusaErro(
            "tipo",
            f"`{chave}` deveria ser boolean e é {type(valor).__name__}.")
    if valor is not True:
        atual[ultima] = True
        alteracoes.append(Alteracao(chave, valor, True))


def mesclar(cfg: dict) -> tuple[dict, list[Alteracao]]:
    """Devolve (cópia mesclada, alterações). Não grava."""
    import copy
    novo = copy.deepcopy(cfg)
    alts: list[Alteracao] = []
    _forcar_true(novo, ["daemon", "browserTools", "enabled"], alts)
    _forcar_true(novo, ["daemon", "mcp", "injectIntoAgents"], alts)
    return novo, alts
