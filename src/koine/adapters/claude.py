import os
import sys

from koine import cache, render, shell
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

MARCADOR = "<!-- gerado por kn-agente -->"
ARQUIVO = "CLAUDE.md"


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Bundle no cache + `--add-dir`, com o CLAUDE.md do bundle INLINE.

    O mecanismo anterior — `CLAUDE.md` na pasta com `@/caminho/absoluto` — não
    entrega fora do terminal: import externo só expande em pasta aprovada, e a
    aprovação é um booleano por pasta que só o diálogo interativo escreve. Pasta
    nova aberta remotamente nunca é aprovada, e a sessão sobe sem contexto e sem
    erro. Medido em 27/08/2026 com ferramentas desligadas.

    Por isso o conteúdo vai embutido, não referenciado: o `@path` continuaria
    sendo texto morto dentro do bundle.
    """
    bundle = cache.caminho_bundle("claude-bundles", cache.slot_id(cm.pasta_abs))
    env = {"CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD": "1"}
    if sys.platform == "win32" and not shell.powershell_executa():
        # Medido em 28/08/2026: com Git Bash instalado o Claude ainda carrega a
        # ferramenta PowerShell, e onde a política nega o powershell.exe ela não
        # pode funcionar. A sessão só não quebra enquanto o modelo preferir o
        # Bash — desligar tira a escolha errada da mesa. O caminho contrário
        # (ligar) não é nosso: onde o PowerShell roda, o default do cliente vale.
        env["CLAUDE_CODE_USE_POWERSHELL_TOOL"] = "0"
    return Lancamento(
        arquivos_externos={os.path.join(bundle, ARQUIVO): _render(cm)},
        env_vars=env,
        extra_args=["--add-dir", bundle],
    )


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido (`koine gerar`, modo skills).

    Mesmo conteúdo do bundle, de propósito: no modo skills a pasta é a única via
    de entrega, e um formato que depende de aprovação interativa por pasta seria
    justamente o que esta mudança existe para tirar do caminho.
    """
    return ARQUIVO, _render(cm)


def _render(cm: ContextoMontado) -> str:
    doc = render.documento_inline("Sessão Koine — Claude", cm)
    return MARCADOR + "\n" + doc + "\n\n" + render.prosa_sessao(cm, "kn-claude <agente> .")
