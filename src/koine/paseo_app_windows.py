"""Detectar, encerrar e abrir o app desktop do Paseo no Windows.

Mecânica medida em VM Windows com AppLocker (24-25/09/2026, ata
01-discussoes/20260925-onboarding-paseo-windows-mecanica-app-desktop.md):
tasklist/taskkill/start, tudo via cmd — nunca PowerShell, a política da
estação corporativa que motiva este módulo nega PowerShell por padrão.

Diferente do macOS (paseo_app.py), o processo do app e o processo do
daemon podem ser INDISTINGUÍVEIS POR NOME — ambos aparecem como
"Paseo.exe" na tasklist quando o app gerencia o daemon (desktopManaged:
true). Por isso `encerrar()` só age quando `paseo_diagnostico.
desktop_managed()` lê True NA HORA da chamada — nunca herdado de leitura
anterior (spec 20260925-spec-koine-onboarding-paseo-windows.md). `abrir()`
é incondicional: gatear a abertura pelo mesmo campo bloquearia toda
primeira instalação, porque antes de qualquer coisa rodar o campo sempre
lê False (medido — ata 20260925-desktopmanaged-e-dinamico-nao-estatico.md).

Mesmo marcador de bloqueio de teste que paseo_app.py usa (incidente de
22-24/09/2026: testes e2e sobem o koine.pyz como processo filho real, que
nenhum monkeypatch do pytest alcança).
"""
import os
import subprocess
import sys
import time

from koine.paseo_app import MARCADOR_BLOQUEIO

APP_EXE = "Paseo.exe"


def _bloqueado_por_teste() -> bool:
    return os.path.exists(MARCADOR_BLOQUEIO)


def esta_rodando() -> bool:
    """True se o app desktop está em execução."""
    if sys.platform != "win32" or _bloqueado_por_teste():
        return False
    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {APP_EXE}"],
            capture_output=True, text=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return False
    return r.returncode == 0 and APP_EXE in r.stdout


def encerrar(*, tentativas: int = 20, intervalo: float = 0.5) -> bool:
    """Encerra sem forçar (`taskkill` sem `/F`) — SÓ quando
    `paseo_diagnostico.desktop_managed()` lê True NA HORA desta chamada
    (nunca herdado). True se encerrou ou já não estava rodando; False se
    recusou por desktopManaged não-True, ou se não confirmou o
    encerramento a tempo. Quando devolve False por recusa, não chamou
    `taskkill` nenhum — o app segue rodando intocado."""
    if not esta_rodando():
        return True
    from koine import paseo_diagnostico as pd
    if pd.desktop_managed() is not True:
        return False
    try:
        subprocess.run(["taskkill", "/IM", APP_EXE],
                       capture_output=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return False
    for _ in range(tentativas):
        if not esta_rodando():
            return True
        time.sleep(intervalo)
    return False


FALLBACKS_DO_APP = {
    "win32": lambda: [os.path.join(
        os.environ.get("LOCALAPPDATA") or "", "Programs", "Paseo", APP_EXE)],
}


def _resolver_app() -> str | None:
    """PATH primeiro (raro — o app não costuma estar lá), depois o local
    de instalação padrão medido nesta VM. Tabela própria — separada da
    que `paseo_ambiente` usa para o CLI `paseo.cmd`, que é um binário
    diferente (spec, Decisões de Implementação)."""
    import shutil
    achado = shutil.which(APP_EXE)
    if achado:
        return achado
    for candidato in FALLBACKS_DO_APP.get(sys.platform, lambda: [])():
        if candidato and os.path.isfile(candidato):
            return candidato
    return None


def abrir() -> bool:
    """Abre o app desktop. INCONDICIONAL — não lê `desktopManaged` (o
    campo sempre lê False antes de qualquer abertura; gatear aqui
    bloquearia toda primeira instalação, sempre — spec 20260925). Usa
    `start /B` para não travar o processo chamador: `start` puro, com a
    própria linha de saída redirecionada, mediu travar o `.bat` chamador
    por mais de 10 minutos esperando o app fechar (ata de mecânica,
    24/09/2026), mesmo o app tendo aberto de verdade."""
    if sys.platform != "win32" or _bloqueado_por_teste():
        return False
    exe = _resolver_app()
    if exe is None:
        return False
    try:
        r = subprocess.run(["cmd", "/c", "start", "/B", "", exe],
                           capture_output=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return False
    return r.returncode == 0
