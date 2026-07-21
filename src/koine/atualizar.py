# src/koine/atualizar.py
import hashlib
import os
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

from koine import instalar as _instalar, mensagens, skills, wrappers
from koine._version import __version__

REPO = "jrunic/koine"


class AtualizarErro(Exception):
    """Falha de rede/resolução/verificação, com mensagem pronta ao usuário."""


def resolver_versao() -> tuple[str, str]:
    """(tag, versao). KOINE_VERSAO fixa a tag; senão segue o redirect de
    releases/latest no github. Não baixa o pacote."""
    pin = os.environ.get("KOINE_VERSAO")
    if pin:
        tag = pin if pin.startswith("v") else f"v{pin}"
        return tag, tag[1:]
    url = f"https://github.com/{REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            final = resp.geturl()
    except (urllib.error.URLError, ssl.SSLError, OSError) as e:
        raise AtualizarErro(
            f"não foi possível resolver a última versão pelo github ({e}). "
            "Fixe a versão: KOINE_VERSAO=vX.Y.Z koine atualizar") from e
    tag = final.rstrip("/").rsplit("/", 1)[-1]
    if not tag.startswith("v"):
        raise AtualizarErro(
            f"resposta inesperada de releases/latest: {final!r}. "
            "Fixe a versão: KOINE_VERSAO=vX.Y.Z koine atualizar")
    return tag, tag[1:]
