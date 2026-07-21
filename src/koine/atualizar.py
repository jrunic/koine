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


def montar_urls(tag: str, versao: str) -> tuple[str, str]:
    base = (os.environ.get("KOINE_BASE_URL")
            or f"https://github.com/{REPO}/releases/download").rstrip("/")
    return f"{base}/{tag}/koine-{versao}.zip", f"{base}/{tag}/SHA256SUMS"


def baixar(url: str) -> bytes:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except (urllib.error.URLError, ssl.SSLError, OSError) as e:
        raise AtualizarErro(
            f"falha ao baixar {url} ({e}). Verifique a conexão ou o KOINE_BASE_URL; "
            "a instalação atual não foi tocada.") from e


def baixar_sums_opcional(sha_url: str) -> str | None:
    try:
        req = urllib.request.Request(sha_url, headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, ssl.SSLError, OSError):
        return None


def verificar_sha256(dados: bytes, sums_texto: str, asset: str) -> None:
    esperado = None
    for linha in sums_texto.splitlines():
        partes = linha.split()
        if len(partes) == 2 and partes[1].lstrip("*") == asset:
            esperado = partes[0].lower()
            break
    if esperado is None:
        raise AtualizarErro(f"{asset} ausente no SHA256SUMS")
    real = hashlib.sha256(dados).hexdigest()
    if real != esperado:
        raise AtualizarErro(
            f"hash divergente para {asset}: esperado {esperado}, obtido {real}. "
            "Download corrompido; instalação atual intacta.")


def _substituir_pyz(src: str, dst: str, tentativas: int = 50, intervalo: float = 0.2) -> None:
    """os.replace atômico do pyz. No Windows o processo pai pode ainda segurar o
    dst; reitera até liberar. No POSIX acerta de primeira. Sem trampolim batch."""
    for i in range(tentativas):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == tentativas - 1:
                raise
            time.sleep(intervalo)


def _refresh_skills(force: bool = False) -> None:
    """Instala/atualiza skills do vault novo em cada harness detectado.
    Idempotente; divergentes preservados salvo force. Falha por harness não aborta."""
    for h in skills.detectar_harnesses():
        try:
            criadas, _exist, div = skills.instalar_habilidades_detalhado(h, force=force)
            for n in criadas:
                print(f"    + {h}: {n}")
            if div:
                print(f"    ! {h}: divergentes preservadas (use --force): {', '.join(div)}")
        except (OSError, ValueError) as e:
            print(f"    aviso: skills de {h}: {e}", file=sys.stderr)


def aplicar(staging: str, alvo_pyz: str, bindir: str, versao: str, force: bool) -> None:
    """Fase de aplicação (não-transacional; recuperável re-rodando). Extrai o
    vault (shipped forçado, dominios do usuário preservados salvo force), troca o
    pyz, regenera wrappers baqueando o interpretador atual e refresca skills."""
    _instalar.extrair(os.path.join(staging, "vault"), versao,
                      force=force, atualizar_vault=True)
    _substituir_pyz(os.path.join(staging, "koine.pyz"), alvo_pyz)
    wrappers.gerar(bindir, alvo_pyz, sys.executable)
    print("Skills:")
    _refresh_skills(force=force)
    print(f"Koine atualizado para {versao}.")
