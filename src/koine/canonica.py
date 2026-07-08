import os
import sys
from pathlib import Path

from koine import aliases


def configurar(vault_src: str, interativo: bool = False) -> str:
    """Configura a pasta canônica (porta de configurarPastaCanonica, instalar.go):
    prompt-com-default se interativo (default ~/koine), cria a pasta, registra o
    alias 'koine' (3 casos) e materializa o CONTEXTO.md bootstrap do vault
    (4 casos). Idempotente. Devolve o path absoluto da pasta canônica."""
    home = str(Path.home())
    pasta = os.path.join(home, "koine")
    if interativo:
        print("Onde fica sua pasta canônica para sessões com Hermes? [~/koine]: ",
              end="", flush=True)
        resp = sys.stdin.readline().strip()
        if resp:
            pasta = _expandir_path(resp, home)
    else:
        print("Pasta canônica: ~/koine (default, modo não-interativo)")

    os.makedirs(pasta, exist_ok=True)
    print(f"✓ Pasta canônica em {pasta}")
    try:
        _registrar_alias(pasta, home)
    except (OSError, ValueError) as e:
        # degradação graciosa igual ao Go (instalar.go:161-163): alias falhou
        # não aborta a instalação
        print(f"aviso: alias: {e}", file=sys.stderr)
    _materializar_contexto(vault_src, pasta, interativo)
    return pasta


def _expandir_path(p: str, home: str) -> str:
    """Porta de expandirPath (instalar.go): ~, ~/, ~\\, relativo → abs."""
    if p == "~":
        return home
    if p.startswith("~/") or p.startswith("~\\"):
        return os.path.join(home, p[2:].replace("\\", os.sep))
    return os.path.abspath(p)


def _registrar_alias(pasta: str, home: str) -> None:
    """Porta de registrarAliasCanonico: já correto → ✓; divergente → aviso e
    mantém; ausente → registra (home-relative se sob HOME)."""
    a = aliases.carregar()
    existente = a["pastas"].get("koine")
    if existente:
        resolvido = existente["path"]
        if existente["from"] == "home":
            resolvido = os.path.join(home, existente["path"])
        if resolvido == pasta:
            print("✓ Alias 'koine' já está correto")
            return
        print(f"aviso: alias 'koine' já aponta para {resolvido} — mantendo. "
              f"Para mudar, edite {aliases.config_path()}", file=sys.stderr)
        return
    from_, rel = "abs", pasta
    if pasta.startswith(home + os.sep):
        from_, rel = "home", pasta[len(home) + 1:]
    aliases.adicionar("koine", rel, from_)
    print("✓ Alias 'koine' registrado")


def _materializar_contexto(vault_src: str, pasta: str, interativo: bool) -> None:
    """Porta de materializarContextoBootstrap: ausente → escreve; idêntico →
    informa; divergente não-interativo → preserva com aviso; divergente
    interativo → [Y/n] (bootstrap) ou [y/N] (personalizado)."""
    with open(os.path.join(vault_src, "bootstrap", "CONTEXTO.md"), encoding="utf-8") as f:
        embed = f.read()
    destino = os.path.join(pasta, "CONTEXTO.md")
    if not os.path.exists(destino):
        with open(destino, "w", encoding="utf-8") as f:
            f.write(embed)
        return
    with open(destino, encoding="utf-8") as f:
        atual = f.read()
    if atual == embed:
        print("✓ CONTEXTO.md já está em modo bootstrap (idêntico ao embed)")
        return
    if not interativo:
        # texto do Go com kn-agente→koine (regra global do port)
        print(f"aviso: {destino} existe (modo não-interativo, preservando). "
              "Para atualizar, rode koine instalar interativamente.", file=sys.stderr)
        return
    if "bootstrap: true" in atual:
        print("CONTEXTO.md em modo bootstrap detectado (conteúdo difere da versão atual). "
              "Atualizar? [Y/n]: ", end="", flush=True)
        resp = sys.stdin.readline().strip().lower()
        sobrescrever = resp in ("", "s", "y")
    else:
        print("CONTEXTO.md já personalizado. Sobrescrever com versão bootstrap? [y/N]: ",
              end="", flush=True)
        resp = sys.stdin.readline().strip().lower()
        sobrescrever = resp in ("s", "y")
    if sobrescrever:
        with open(destino, "w", encoding="utf-8") as f:
            f.write(embed)
    else:
        print("✓ CONTEXTO.md preservado")
