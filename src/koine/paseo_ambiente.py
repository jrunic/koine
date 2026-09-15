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


# --- Executáveis e primitiva de execução -------------------------------

import shutil
import subprocess
import sys
from dataclasses import dataclass

FALLBACKS_DO_PASEO = {
    "win32": lambda: [os.path.join(
        os.environ.get("LOCALAPPDATA") or "", "Programs", "Paseo",
        "resources", "bin", "paseo.cmd")],
    "darwin": lambda: ["/Applications/Paseo.app/Contents/Resources/bin/paseo"],
}


def pastas_padrao_do_paseo() -> list[str]:
    """Diretórios de instalação padrão do Paseo, por plataforma (medidos).

    Windows medido na VM de bancada em 15/09/2026, instalação padrão:
    `%LOCALAPPDATA%\\Programs\\Paseo\\resources\\bin\\paseo.cmd`.
    """
    fab = FALLBACKS_DO_PASEO.get(sys.platform)
    return [p for p in (fab() if fab else []) if p]


@dataclass(frozen=True)
class Executavel:
    caminho: str
    origem: str  # "path" | "fallback"


def resolver_executavel(nome: str) -> Executavel | None:
    """PATH primeiro; depois os locais padrão. None = não achou em nenhum."""
    achado = shutil.which(nome)
    if achado:
        return Executavel(achado, "path")
    for pasta in pastas_padrao_do_paseo():
        alvo = pasta if nome == "paseo" else os.path.join(pasta, nome)
        if os.path.isfile(alvo):
            return Executavel(alvo, "fallback")
    return None


def executar(executavel: str, args: list[str], *, timeout: int = 15):
    """Primitiva única. No Windows, .cmd/.bat só executa por cmd.exe /c —
    caminho absoluto de batch não é chamada direta (launch desde a v0.4.2).
    Args em lista: o subprocess cuida do quoting de espaço no caminho."""
    if (sys.platform == "win32"
            and executavel.lower().endswith((".cmd", ".bat"))):
        cmd = ["cmd", "/c", executavel, *args]
    else:
        cmd = [executavel, *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
