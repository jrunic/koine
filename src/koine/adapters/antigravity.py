import os

from koine import cache, render
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

MARCADOR = "<!-- gerado por kn-agente -->"
ARQUIVO = "GEMINI.md"


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Bundle no cache + `--add-dir`: o cliente lê o GEMINI.md do diretório
    adicionado. Medido em 27/08/2026, discriminado por dois nonces.

    Conteúdo INLINE pelo mesmo motivo do adapter do claude: `@path` para fora da
    pasta é texto morto.
    """
    bundle = cache.caminho_bundle("agy-bundles", cache.slot_id(cm.pasta_abs))
    return Lancamento(
        arquivos_externos={os.path.join(bundle, ARQUIVO): _render(cm)},
        extra_args=["--add-dir", bundle],
    )


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido (`koine gerar`, modo skills)."""
    return ARQUIVO, _render(cm)


def _render(cm: ContextoMontado) -> str:
    doc = render.documento_inline("Sessão Koine — Antigravity", cm)
    return MARCADOR + "\n" + doc + "\n\n" + render.prosa_sessao(cm, "kn-agy <agente> .")
