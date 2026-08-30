import os

from koine import cache, render, shell
from koine import paseo as _paseo
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

MARCADOR = "<!-- gerado por kn-agente -->"
ARQUIVO = "AGENTS.md"
EXTRA_ARGS = ["-c", "project_doc_max_bytes=1048576"]

# Medido em 28/08/2026: usa PowerShell e SO PowerShell no Windows, e nao expoe
# chave para trocar. Onde a politica nega o powershell.exe, nao tem shell.
ACEITA_SHELL = (shell.PWSH, shell.POWERSHELL)

# Sem rota pelo Paseo. Medido em 29/08/2026: ele é invocado como servidor longo
# (`app-server`) a partir do cwd do DAEMON, antes de existir workspace — o
# wrapper roda e não tem pasta com que trabalhar, e o Koine nunca monta contexto.
PASEO = None


def _agente_de(cm) -> str:
    return os.path.splitext(os.path.basename(cm.agente_path))[0] if cm.agente_path else "hermes"


def renderizar(cm: ContextoMontado) -> Lancamento:
    """Bundle no cache + `-c model_instructions_file=<arquivo>`.

    O canal foi medido em 27/08/2026: a chave SOMA ao contexto em vez de
    substituir as instruções base. A via que NÃO serve é `CODEX_HOME` — a
    credencial mora na home do cliente, e redirecioná-la derruba a sessão com
    401 (mesma família do GROK_HOME).

    O arquivo é o mesmo documento inline de antes; o que muda é onde ele mora.
    """
    arquivo = os.path.join(
        cache.caminho_bundle("codex-bundles", cache.slot_id(cm.pasta_abs)), ARQUIVO)
    return Lancamento(
        arquivos_externos={arquivo: _render(cm)},
        # o valor varia por pasta e por isso NÃO cabe em EXTRA_ARGS, que o repo
        # declara como constante de módulo — vai por instância, no Lancamento
        extra_args=list(EXTRA_ARGS) + ["-c", f"model_instructions_file={arquivo}"],
    )


def renderizar_para_pasta(cm: ContextoMontado) -> tuple[str, str]:
    """Materialização a pedido, pelo `koine gerar`.

    Chega aqui só pelo `koine gerar`. O **modo skills** — o pacote sem
    Python — nunca alcança este código: quem escreve na pasta lá é a
    `/kn-12-prepara-contexto`, por `@path` e não por snapshot. Medido em
    30/08/2026; o docstring afirmava os dois desde o porte (jd-task #706).
    """
    return ARQUIVO, _render(cm)


def _render(cm: ContextoMontado) -> str:
    partes = []

    def add(secao, path):
        if path:
            with open(path, encoding="utf-8") as f:
                partes.append(render.Parte(secao, f.read()))

    add("Usuário", cm.usuario_path)
    add("Koine", cm.koine_path)
    add("Agente", cm.agente_path)
    if not cm.bootstrap:
        add("Escopo", cm.escopo_path)
        for ip in cm.indice_paths:
            add("Referências — " + render.dominio_de(ip), ip)
    # INLINE: a instrução tem de vir embutida, não referenciada — o codex não
    # segue @path (ver ADR do mecanismo B).
    add("Instrução do Koine para esta sessão", cm.instrucao_path)
    if cm.contexto_path:
        try:
            with open(cm.contexto_path, encoding="utf-8") as f:
                partes.append(render.Parte("Contexto da sessão (snapshot de ./CONTEXTO.md)", f.read()))
        except OSError:
            pass

    doc = render.mescar_documentos("Sessão Koine — Codex", partes)
    corpo = doc + "\n\n" + render.prosa_sessao(cm, f"kn-codex {_agente_de(cm)} .")
    return MARCADOR + "\n" + corpo

