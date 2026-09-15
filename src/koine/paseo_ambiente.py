"""Resolvedor único do ambiente Paseo.

Contrato da spec 20260915-spec-paseo-windows-sem-variavel: PASEO_HOME é
override AUTORITATIVO e exclusivo (existe ou não config nele — nunca cai para
o local padrão); vazio equivale a ausente. Sem override, descobre o config nos
locais padrão; achando mais de um, aborta listando os candidatos.

Mentorado não cria variável de ambiente para o fluxo básico.
"""
import os
from dataclasses import dataclass, field


class RecusaErro(Exception):
    def __init__(self, motivo: str, mensagem: str):
        super().__init__(mensagem)
        self.motivo = motivo
        self.mensagem = mensagem


@dataclass(frozen=True)
class Home:
    """`origem`: "override" | "descoberto" | "padrao"."""
    caminho: str
    origem: str
    candidatos: list = field(default_factory=list)


def locais_padroes() -> list[str]:
    """Locais medidos onde o Paseo guarda config.json. Hoje um por plataforma."""
    return [os.path.join(os.path.expanduser("~"), ".paseo")]


def _tem_config(local: str) -> bool:
    return os.path.isfile(os.path.join(local, "config.json"))


def resolver_home() -> Home:
    override = (os.environ.get("PASEO_HOME") or "").strip()
    if override:
        return Home(override, "override", [override])
    achados = [c for c in locais_padroes() if _tem_config(c)]
    if len(achados) > 1:
        raise RecusaErro(
            "multiplos-configs",
            "há mais de um config do Paseo: " + ", ".join(achados) +
            ". Defina PASEO_HOME com o que você usa.")
    if achados:
        return Home(achados[0], "descoberto", achados)
    return Home(locais_padroes()[0], "padrao", [])
