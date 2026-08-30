import os
import sys

from koine import cache, render, shell
from koine import paseo as _paseo
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

MARCADOR = "<!-- gerado por kn-agente -->"
ARQUIVO = "CLAUDE.md"

# Degraus de shell que este cliente aceita, medido em 28/08/2026: bash/zsh, ou a
# ferramenta PowerShell nativa. O `cmd` nunca foi opcao para ele.
ACEITA_SHELL = (shell.PWSH, shell.POWERSHELL, shell.BASH)

# Rota pelo Paseo, medida em 29/08/2026: o spawn de sessão passa pelo comando
# do provider, com o cwd do workspace, e a lista de argumentos do Paseo chega
# inteira.
PASEO = _paseo.Rota(extends="claude")


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
    bundle = cache.caminho_bundle(
        "claude-bundles", cache.slot_sessao(cm.pasta_abs, render.agente_de(cm)))
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
        # `--add-dir` é VARIÁDICO: na forma separada ele engole todo token
        # seguinte que não comece com hífen. Medido em 30/08/2026 —
        # `--add-dir <b> auth status` tratou `auth`/`status` como
        # diretórios e o cliente caiu em modo sessão pedindo prompt. A
        # sessão do orquestrador não sofria (o 1º arg dele é flag); o
        # diagnóstico de autenticação sofria, e ficava inútil.
        extra_args=[f"--add-dir={bundle}"],
    )


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido, pelo `koine gerar`.

    Chega aqui só pelo `koine gerar`. O **modo skills** — o pacote sem
    Python — nunca alcança este código: quem escreve na pasta lá é a
    `/kn-12-prepara-contexto`, por `@path` e não por snapshot. Medido em
    30/08/2026; o docstring afirmava os dois desde o porte (jd-task #706).

    Mesmo conteúdo do bundle, de propósito: quem pede `gerar` quer o que a
    sessão veria, e um formato que dependesse de aprovação interativa por pasta
    seria justamente o que a entrega por canal existe para tirar do caminho.
    """
    return ARQUIVO, _render(cm)


def _render(cm: ContextoMontado) -> str:
    doc = render.documento_inline("Sessão Koine — Claude", cm)
    return MARCADOR + "\n" + doc + "\n\n" + render.prosa_sessao(cm, "kn-claude <agente> .")
