"""Projeto/workspace do Paseo por pasta — código, não conversa.

Os três chamadores (koine instalar, /kn-01 Rodada 3, /kn-14) resolvem
sempre a mesma operação para a mesma pasta: garantir que existe projeto e
workspace apontando para ela, sem duplicar se já existir. Antes disso era
instrução em prosa na kn-14, interpretada de novo a cada sessão.

100% sobre `--json` dos subcomandos do `paseo` CLI — nunca parseia texto
pensado para humano.
"""
import json
import os
import subprocess


def achar_projeto(pasta: str, projetos: list[dict]) -> dict | None:
    """Projeto cujo `path` resolve para `pasta` (comparação por caminho
    absoluto — o CLI pode devolver o path como foi cadastrado, não
    normalizado)."""
    alvo = os.path.abspath(pasta)
    for p in projetos:
        if os.path.abspath(p["path"]) == alvo:
            return p
    return None


def achar_workspace(nome_projeto: str, pasta: str,
                    workspaces: list[dict]) -> dict | None:
    """Workspace do projeto `nome_projeto` apontando para `pasta`.

    `workspace ls --json` traz o NOME do projeto no campo `project`, não o
    `projectId` — cruzar por id exigiria um segundo lookup. Casar por nome
    é suficiente aqui porque `garantir()` sempre resolve o projeto primeiro
    e usa o `name` dele, não um nome inventado à parte.
    """
    alvo = os.path.abspath(pasta)
    for w in workspaces:
        if w["project"] == nome_projeto and os.path.abspath(w["cwd"]) == alvo:
            return w
    return None


def achar_projeto_por_nome(nome: str, projetos: list[dict]) -> dict | None:
    """Projeto cujo `name` casa exatamente com `nome`.

    Diferente de `achar_projeto` (casamento por path, 1 projeto por pasta):
    um projeto do Paseo agrupa workspaces de VÁRIAS pastas — medido em
    `paseo project ls`/`workspace ls` desta máquina, ex. "Grupo Aldo" hospeda
    workspaces de duas pastas distintas. A /kn-14 usa esta função quando o
    usuário está agrupando uma pasta nova sob um projeto já existente."""
    for p in projetos:
        if p["name"] == nome:
            return p
    return None


def _rodar(args: list[str], *, timeout: int = 20):
    """Roda `paseo <args>` e devolve o JSON parseado do stdout, ou None.

    Mesma primitiva de resolução de executável que `paseo_diagnostico.
    _rodar_paseo` — None significa "não deu para fazer", nunca "lista
    vazia" (que é um resultado válido do CLI)."""
    from koine import paseo_ambiente
    exe = paseo_ambiente.resolver_executavel("paseo")
    if exe is None:
        return None
    try:
        r = paseo_ambiente.executar(exe.caminho, args, timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
