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


class PaseoIndisponivel(Exception):
    """O `paseo` CLI não respondeu (daemon fora do ar, binário ausente,
    timeout, saída não-JSON) num passo de `garantir()`. Achado da revisão
    dev-10 do plano, 22/09/2026: sem isto, `garantir()` estourava
    `TypeError` com traceback cru quando o daemon caía no meio da operação
    — o consumidor (CLI, `_cmd_instalar`) decide a prosa amigável a partir
    daqui, nunca a partir de um `None` inesperado."""


def garantir(pasta: str, titulo: str = "", projeto_nome: str = "") -> dict:
    """Garante projeto+workspace para `pasta`. Idempotente nos três estados
    (nada existe / projeto sem workspace / os dois existem).

    Sem `projeto_nome`: resolve/cria o projeto por PATH desta pasta (uso
    1:1 — pasta canônica do `koine instalar`, Rodada 3 do `/kn-01`).
    `titulo`, se dado, vira o nome visível do projeto (renomeia se
    divergir).

    Com `projeto_nome`: resolve/cria o projeto por NOME em vez de por path
    — é o caso de várias pastas agrupadas sob o mesmo projeto (`/kn-14`,
    achado da revisão dev-10: um projeto do Paseo hospeda workspaces de
    pastas diferentes, medido em `paseo project ls`/`workspace ls` desta
    máquina). Quando dado, `projeto_nome` prevalece sobre `titulo`.

    Levanta `PaseoIndisponivel` se qualquer chamada ao `paseo` CLI
    devolver `None` — nunca deixa a ausência de resposta virar
    `TypeError` mais adiante.

    Devolve {"projectId", "workspaceId", "acao": "criado" | "existente"}.
    """
    abspasta = os.path.abspath(pasta)
    projetos = _rodar(["project", "ls", "--json"])
    if projetos is None:
        raise PaseoIndisponivel("paseo project ls falhou")

    if projeto_nome:
        projeto = achar_projeto_por_nome(projeto_nome, projetos)
    else:
        projeto = achar_projeto(pasta, projetos)
    projeto_e_novo = projeto is None

    if projeto is None:
        projeto = _rodar(["project", "create", abspasta, "--json"])
        if projeto is None:
            raise PaseoIndisponivel("paseo project create falhou")
        nome_final = projeto_nome or titulo
        if nome_final:
            r = _rodar(["project", "rename", projeto["projectId"], nome_final,
                        "--json"])
            if r is None:
                raise PaseoIndisponivel("paseo project rename falhou")
            projeto["name"] = nome_final
    elif titulo and not projeto_nome and projeto["name"] != titulo:
        r = _rodar(["project", "rename", projeto["projectId"], titulo, "--json"])
        if r is None:
            raise PaseoIndisponivel("paseo project rename falhou")
        projeto["name"] = titulo

    workspace = None
    if not projeto_e_novo:
        workspaces = _rodar(["workspace", "ls", "--json"])
        if workspaces is None:
            raise PaseoIndisponivel("paseo workspace ls falhou")
        workspace = achar_workspace(projeto["name"], pasta, workspaces)

    if workspace is None:
        workspace = _rodar(["workspace", "create", "--path", abspasta,
                            "--project", projeto["projectId"],
                            "--isolation", "local", "--json"])
        if workspace is None:
            raise PaseoIndisponivel("paseo workspace create falhou")
        acao = "criado"
    else:
        acao = "existente"

    return {"projectId": projeto["projectId"], "workspaceId": workspace["workspaceId"],
            "acao": acao}
