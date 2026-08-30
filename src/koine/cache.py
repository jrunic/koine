import hashlib
import os

from koine import paths


def slot_id(pasta_abs: str) -> str:
    """Identificador determinístico de 12 chars hex (SHA-256, 6 bytes) da pasta.

    Mesma pasta → mesmo slot. Sem timestamp — cache cresce em #pastas, não em #sessões.
    """
    return hashlib.sha256(pasta_abs.encode()).hexdigest()[:12]


def slot_sessao(pasta_abs: str, agente: str) -> str:
    """Slot do que a SESSÃO entrega: pasta **e** agente.

    O `slot_id` identifica a pasta, e é o certo para o que é da pasta — a foto da
    Ficha Koine. Para o contexto entregue ao cliente ele é errado: dois providers
    do mesmo workspace (o genérico e o que força um agente) escreviam nos mesmos
    arquivos, e o último a rodar governava a sessão do outro.

    Não é corrida teórica. Medido em 30/08/2026 dirigindo o servidor ACP do
    opencode: com o processo DE PÉ, ele lê o arquivo de `instructions` a cada
    sessão nova — sessão 1 leu um conteúdo, sessão 2 leu o que foi escrito
    depois. O sintoma era o agente errado, sem erro nenhum (jd-task #708).

    O separador é `\0` de propósito: não ocorre em caminho nem em nome de
    agente, então nenhum par distinto colide por concatenação.
    """
    return hashlib.sha256(f"{pasta_abs}\0{agente}".encode()).hexdigest()[:12]


def caminho_bundle(categoria: str, slot: str) -> str:
    return os.path.join(paths.cache_dir(), categoria, slot)


def caminho_arquivo(categoria: str, slot: str, extensao: str) -> str:
    return os.path.join(paths.cache_dir(), categoria, f"{slot}.{extensao}")
