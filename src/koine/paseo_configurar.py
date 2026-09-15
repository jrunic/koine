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
