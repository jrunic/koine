"""Leitura do bundle que o launch materializou no cache.

Depois da #587 a pasta do usuário não recebe mais arquivo gerado — o contexto
vai para um bundle por pasta, no cache. Todo teste que antes abria
`<pasta>/CLAUDE.md` passa a ler daqui.
"""
import os

from koine import cache

CATEGORIA = {
    "claude": "claude-bundles",
    "agy": "agy-bundles",
    "codex": "codex-bundles",
    "copilot": "copilot-bundles",
}


def caminho(cliente: str, pasta: str, home: str = "") -> str:
    """`home` explícito para os e2e: eles rodam o produto em SUBPROCESSO, com
    outro HOME — resolver pelo ambiente do pytest apontaria para o cache errado.
    """
    if home:
        return os.path.join(home, ".cache", "koine", CATEGORIA[cliente],
                            cache.slot_id(pasta))
    return cache.caminho_bundle(CATEGORIA[cliente], cache.slot_id(pasta))


def conteudo(cliente: str, pasta: str, home: str = "") -> str:
    """Tudo que o bundle daquele cliente entrega, concatenado.

    Concatena porque a pergunta dos testes é sempre 'esta camada chegou?' — e o
    canal do copilot entrega vários arquivos, não um.
    """
    base = caminho(cliente, pasta, home)
    partes = []
    for raiz, _, arquivos in os.walk(base):
        for a in sorted(arquivos):
            with open(os.path.join(raiz, a), encoding="utf-8") as f:
                partes.append(f.read())
    return "\n".join(partes)
