"""Detectar, encerrar e abrir o app desktop do Paseo.

Medido só para macOS nesta rodada (assumption nomeada na spec) — Windows
fica com `esta_rodando`/`abrir` devolvendo False/False, nunca lançando, até
alguém medir o mecanismo equivalente lá.

Encerrar é sempre "quit" (AppleScript, evento de encerramento normal do
app), nunca kill de processo — o app tem estado próprio (sessões, cache) e
matar à força é o tipo de atalho que esta spec existe para evitar.
"""
import subprocess
import sys
import time

APP_MACOS = "Paseo"


def esta_rodando() -> bool:
    """True se o app desktop está em execução."""
    if sys.platform != "darwin":
        return False
    try:
        r = subprocess.run(
            ["osascript", "-e",
             f'tell application "System Events" to (name of processes) '
             f'contains "{APP_MACOS}"'],
            capture_output=True, text=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return False
    return r.returncode == 0 and r.stdout.strip() == "true"


def encerrar(*, tentativas: int = 20, intervalo: float = 0.5) -> bool:
    """Encerra de forma limpa (quit, não kill). True se encerrou ou já não
    estava rodando; False se não confirmou o encerramento a tempo."""
    if not esta_rodando():
        return True
    try:
        subprocess.run(["osascript", "-e", f'quit app "{APP_MACOS}"'],
                       capture_output=True, timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return False
    for _ in range(tentativas):
        if not esta_rodando():
            return True
        time.sleep(intervalo)
    return False


def abrir() -> bool:
    """Abre o app desktop. True se o comando de abrir foi aceito — não
    espera o daemon responder (ver `aguardar_daemon`)."""
    if sys.platform != "darwin":
        return False
    try:
        r = subprocess.run(["open", "-a", APP_MACOS], capture_output=True,
                           timeout=10)
    except (subprocess.TimeoutExpired, OSError):
        return False
    return r.returncode == 0


def aguardar_daemon(*, timeout: int = 60, intervalo: float = 2.0) -> bool:
    """Espera o daemon do Paseo responder, até `timeout` segundos. Usa o
    mesmo diagnóstico que `koine paseo-doctor` usa para o serviço."""
    from koine import paseo_diagnostico as pd
    fim = time.time() + timeout
    while time.time() < fim:
        home = pd.home_do_paseo()
        cfg, _ = pd.ler_config(home)
        if cfg is not None and pd.verificar_servico(cfg).situacao == pd.OK:
            return True
        time.sleep(intervalo)
    return False
