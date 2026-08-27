# src/koine/instantaneo.py
"""A foto da Ficha Koine — o bloco de frontmatter da última sessão que abriu bem.

Existe porque a ficha some: quem grava o `CONTEXTO.md` durante a sessão é o
cliente, com as ferramentas dele, e o Koine já foi substituído por `execvpe`.
Instrução é pedido e detecção chega depois do dano; a foto é o que torna a perda
recuperável sem o usuário ter que entender YAML.

Mora no cache, num slot por pasta — mesmo mecanismo dos bundles dos adapters.
Cache é descartável por definição: sem foto, o comportamento é o de antes.
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from koine import cache

CATEGORIA = "fichas"


@dataclass
class Foto:
    bloco: str
    quando: str


def _caminho(pasta_abs: str) -> str:
    return cache.caminho_arquivo(CATEGORIA,
                                 cache.slot_id(os.path.abspath(pasta_abs)), "json")


def guardar(pasta_abs: str, bloco: str) -> None:
    """Fotografa a ficha. Erro é silêncio: fotografar é serviço, não requisito —
    cache cheio ou sem permissão não pode derrubar a sessão do usuário."""
    if not bloco:
        return
    try:
        alvo = _caminho(pasta_abs)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        dados = {"bloco": bloco,
                 "quando": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "pasta": os.path.abspath(pasta_abs)}
        with open(alvo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except (OSError, ValueError):
        return


def recuperar(pasta_abs: str) -> Foto | None:
    """A foto desta pasta, ou None. Cache limpo → None → comportamento de antes."""
    try:
        with open(_caminho(pasta_abs), encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, ValueError):
        return None
    bloco = dados.get("bloco")
    if not bloco:
        return None
    return Foto(bloco=bloco, quando=dados.get("quando", ""))
