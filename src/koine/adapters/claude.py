from datetime import datetime, timezone

from koine.contexto import ContextoMontado

MARCADOR = "<!-- gerado por kn-agente -->"


def renderizar(cm: ContextoMontado) -> str:
    if cm.bootstrap:
        return _render_bootstrap(cm)
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


def _render_bootstrap(cm: ContextoMontado) -> str:
    # Timestamp real (RFC3339 UTC), como o ramo não-bootstrap. O normalizador
    # de paridade congela o `em <ts>` mas preserva o `Z` → casa com o Go.
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    linhas = [
        MARCADOR,
        "# CLAUDE.md",
        f"*Gerado por kn-agente em {ts} — modo bootstrap. Não editar.*",
        "",
    ]
    if cm.usuario_path:
        linhas.append(f"@{cm.usuario_path}")
    linhas.append(f"@{cm.koine_path}")
    linhas.append(f"@{cm.agente_path}")
    linhas.append(f"@{cm.contexto_path}")
    return "\n".join(linhas) + "\n\n"
