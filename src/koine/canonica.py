import os
from pathlib import Path

from koine import aliases


def configurar(vault_src: str) -> str:
    """Configura a pasta canônica ~/koine (modo não-interativo): cria a pasta,
    registra o alias 'koine'→home:koine e materializa o CONTEXTO.md bootstrap
    do vault. Idempotente. Devolve o path da pasta canônica."""
    home = str(Path.home())
    pasta = os.path.join(home, "koine")
    os.makedirs(pasta, exist_ok=True)

    # alias 'koine' (só registra se ainda não existe; não sobrescreve divergente)
    a = aliases.carregar()
    if "koine" not in a["pastas"]:
        aliases.adicionar("koine", "koine", "home")

    # CONTEXTO.md bootstrap: ausente → materializa; existente → preserva (não-interativo)
    destino = os.path.join(pasta, "CONTEXTO.md")
    if not os.path.exists(destino):
        with open(os.path.join(vault_src, "bootstrap", "CONTEXTO.md"), encoding="utf-8") as f:
            conteudo = f.read()
        with open(destino, "w", encoding="utf-8") as f:
            f.write(conteudo)
    return pasta
