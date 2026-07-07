from datetime import datetime, timezone

from koine.contexto import ContextoMontado

MARCADOR = "<!-- gerado por kn-agente -->"


def renderizar(cm: ContextoMontado) -> str:
    # RFC3339 UTC, igual a time.Now().UTC().Format(time.RFC3339) do Go.
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    linhas = [
        MARCADOR,
        "# CLAUDE.md",
        f"*Gerado por kn-agente em {ts}. Não editar — regerar com `kn-claude .`.*",
        "",
        f"@{cm.usuario_path}",
        f"@{cm.koine_path}",
        f"@{cm.agente_path}",
        f"@{cm.escopo_path}",
    ]
    linhas += [f"@{p}" for p in cm.indice_paths]
    linhas.append(f"@{cm.contexto_path}")
    return "\n".join(linhas) + "\n"
