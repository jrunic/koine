import os

from koine import render
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

MARCADOR = "<!-- gerado por kn-agente -->"
ARQUIVO = "AGENTS.md"
EXTRA_ARGS = ["-c", "project_doc_max_bytes=1048576"]


def _agente_de(cm) -> str:
    return os.path.splitext(os.path.basename(cm.agente_path))[0] if cm.agente_path else "hermes"


def renderizar(cm: ContextoMontado) -> Lancamento:
    return Lancamento(arquivos_working_dir={ARQUIVO: _render(cm)},
                      extra_args=list(EXTRA_ARGS))


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
    if cm.contexto_path:
        try:
            with open(cm.contexto_path, encoding="utf-8") as f:
                partes.append(render.Parte("Contexto da sessão (snapshot de ./CONTEXTO.md)", f.read()))
        except OSError:
            pass

    doc = render.mescar_documentos("Sessão Koine — Codex", partes)
    corpo = doc + "\n\n" + _prosa_instrucao(cm)
    return MARCADOR + "\n" + corpo


def _prosa_instrucao(cm) -> str:
    regen = (f"Este `AGENTS.md` é regenerado a cada sessão por `kn-codex {_agente_de(cm)} .`. "
             "**Não o edite.**")
    if cm.bootstrap and not cm.contexto_path:
        return ("## Instruções desta sessão\n\n"
                "Esta pasta ainda não tem contexto Koine. Crie o `./CONTEXTO.md` desta pasta "
                "com `/kn-02-mantem-catalogo` (Fluxo 3) antes de iniciar o trabalho. " + regen + "\n")
    return ("## Instruções desta sessão\n\n"
            "O contexto mutável desta sessão vive em `./CONTEXTO.md` (no diretório atual). "
            "Leia e mantenha esse arquivo durante o trabalho — toda persistência de contexto "
            "entre sessões vai para ele. O conteúdo acima é um snapshot; a fonte canônica é o arquivo. "
            + regen + "\n")
