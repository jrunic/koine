from dataclasses import dataclass, field


@dataclass
class Lancamento:
    """Tudo que o adapter quer materializar no filesystem e no ambiente do
    processo filho. Porta de internal/harness/interface.go (Lancamento).

    Adapters simples (claude, antigravity) preenchem só arquivos_working_dir.
    Adapters com bundle externo (copilot, opencode) preenchem arquivos_externos,
    symlinks e env_vars."""

    arquivos_working_dir: dict = field(default_factory=dict)  # rel → conteúdo (str)
    arquivos_externos: dict = field(default_factory=dict)     # abs → conteúdo (str)
    symlinks: dict = field(default_factory=dict)              # link_abs → alvo
    env_vars: dict = field(default_factory=dict)              # nome → valor
    extra_args: list = field(default_factory=list)
