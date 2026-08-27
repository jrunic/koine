# src/koine/atualizar.py
import hashlib
import os
import ssl
import subprocess
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


def _resolver_versao_curl(url: str) -> str | None:
    """Fallback do resolver_versao via curl do sistema. O OpenSSL do Python
    (stdlib) pode não achar o CA (macOS sem bundle; Windows sem AIA); o curl
    usa o trust store do SO (Keychain/Schannel), então resolve onde o urllib
    falha. Segue o redirect de releases/latest e devolve a URL final, ou None
    se o curl estiver ausente/falhar."""
    try:
        r = subprocess.run(
            ["curl", "-fsSLSI", "-o", os.devnull, "-w", "%{url_effective}", url],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def resolver_versao() -> tuple[str, str]:
    """(tag, versao). KOINE_VERSAO fixa a tag; senão segue o redirect de
    releases/latest no github. Não baixa o pacote."""
    pin = os.environ.get("KOINE_VERSAO")
    if pin:
        tag = pin if pin.startswith("v") else f"v{pin}"
        return tag, tag[1:]
    url = f"https://github.com/{REPO}/releases/latest"
    final = None
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            final = resp.geturl()
    except (urllib.error.URLError, ssl.SSLError, OSError) as e:
        final = _resolver_versao_curl(url)
        if final is None:
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


def _baixar_curl(url: str) -> bytes | None:
    """Fallback via curl do sistema, em qualquer plataforma. O OpenSSL do Python
    (stdlib) pode não verificar o cert: no macOS quando falta o bundle de CA, no
    Windows quando não busca o CA intermediário via AIA. O curl usa o trust store
    do SO (Keychain no macOS, Schannel no Windows, CA bundle no Linux), então
    funciona onde o urllib falha. Devolve os bytes, ou None se o curl estiver
    ausente/falhar (aí o chamador orienta)."""
    try:
        r = subprocess.run(["curl", "-fsSL", url], capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 and r.stdout else None


def baixar(url: str) -> bytes:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except (urllib.error.URLError, ssl.SSLError, OSError) as e:
        dados = _baixar_curl(url)
        if dados is not None:
            return dados
        raise AtualizarErro(
            f"falha ao baixar {url} ({e}). A verificação SSL do Python falhou e o "
            "curl do sistema não resolveu (ausente ou também sem certificados). "
            "Reinstale via install.sh (usa o curl do SO) ou aponte KOINE_BASE_URL "
            "para um espelho. A instalação atual não foi tocada.") from e


def baixar_sums_opcional(sha_url: str) -> str | None:
    try:
        req = urllib.request.Request(sha_url, headers={"User-Agent": "koine-atualizar"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, ssl.SSLError, OSError):
        dados = _baixar_curl(sha_url)
        if dados is not None:
            return dados.decode("utf-8")
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


def _refresh_skills(versao: str) -> None:
    """Atualiza as skills do vault novo em cada harness detectado. A política é
    do módulo de skills — aqui não há mais decisão a tomar. Falha por harness
    não aborta."""
    for h in skills.detectar_harnesses():
        try:
            criadas, _exist, atualizadas = skills.instalar_habilidades_detalhado(h, versao)
            for n in criadas:
                print(f"    + {h}: {n}")
            for n, bak in atualizadas:
                print(f"    ~ {h}: {n} — sua versão anterior em {bak}")
        except (OSError, ValueError) as e:
            print(f"    aviso: skills de {h}: {e}", file=sys.stderr)


def aplicar(staging: str, alvo_pyz: str, bindir: str, versao: str, force: bool) -> None:
    """Fase de aplicação (não-transacional; recuperável re-rodando). Extrai o
    vault (shipped atualizado com backup no cache, domínios do usuário
    preservados salvo force), troca o pyz, regenera wrappers baqueando o
    interpretador atual e refresca skills."""
    trocas, _preservados = _instalar.extrair(os.path.join(staging, "vault"), versao,
                                             force=force)
    for dest, bak in trocas:
        print(f"    ~ {os.path.basename(dest)} — sua versão anterior em {bak}")
    _substituir_pyz(os.path.join(staging, "koine.pyz"), alvo_pyz)
    wrappers.gerar(bindir, alvo_pyz, sys.executable)
    print("Skills:")
    _refresh_skills(versao)
    print(f"Koine atualizado para {versao}.")


def preparar(force: bool = False) -> tuple[str | None, str]:
    """Resolve versão; no-op (sem baixar) se já estamos nela; senão baixa +
    verifica + extrai para staging. Devolve (staging, versao) — staging=None no
    no-op. `versao` sempre volta (evita re-derivar do pyz)."""
    tag, versao = resolver_versao()
    if versao == __version__ and not force:
        print(mensagens.atualizar_ja_recente(versao))
        return None, versao
    zip_url, sha_url = montar_urls(tag, versao)
    asset = f"koine-{versao}.zip"
    dados = baixar(zip_url)
    sums = baixar_sums_opcional(sha_url)
    if sums is not None:
        verificar_sha256(dados, sums, asset)
    else:
        print(f"aviso: {asset} sem SHA256SUMS na origem — seguindo sem verificação.")
    staging = tempfile.mkdtemp(prefix="koine-upd-")
    zip_path = os.path.join(staging, asset)
    with open(zip_path, "wb") as f:
        f.write(dados)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(staging)
    os.remove(zip_path)
    return staging, versao
