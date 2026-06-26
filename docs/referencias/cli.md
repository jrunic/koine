---
descricao: Referência dos comandos do binário kn-agente e dos wrappers de cliente IA
id: 202606261001
tipo: referencia
status: ativo
tags: [referencia, cli, kn-agente]
---

# Referência — CLI

## `kn-agente` — motor administrativo

### `kn-agente instalar [--force]`

Extrai o vault embutido para `~/.local/share/koine/`, planta domínios canônicos em `~/.config/koine/dominios/`, cria symlinks de cliente (`kn-claude`, `kn-agy`, `kn-copilot`, `kn-opencode`) no mesmo diretório do binário.

- Idempotente. Sem `--force`, detecta divergências e lista; não sobrescreve.
- Com `--force`: sobrescreve mesmo divergências.

### `kn-agente gerar <agente> [pasta]`

Gera o arquivo de contexto do cliente (`CLAUDE.md`, `GEMINI.md`, etc.) na pasta, sem abrir o cliente. Útil para debug.

- `<agente>` — nome do agente (`hermes` ou agente operacional do usuário).
- `[pasta]` — opcional; default é `pwd`.

### `kn-agente mostrar <agente> <pasta>`

Imprime em stdout o contexto resolvido — usuário, agente, escopo, índices, contexto local. Não escreve arquivo.

### `kn-agente versao` / `--versao`

Imprime versão e sai.

## Wrappers de cliente IA — `kn-<cliente> <agente> [pasta] [--substituir]`

Sintaxe canônica para abrir sessão de cliente IA com contexto Koine.

| Wrapper | Cliente lançado | Mecanismo |
|---|---|---|
| `kn-claude` | `claude` | `<pasta>/CLAUDE.md` com `@path` includes |
| `kn-agy` | `agy` | `<pasta>/GEMINI.md` com `@path` includes |
| `kn-copilot` | `copilot` | `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` apontando para bundle em `~/.cache/koine/copilot-bundles/<slot>/` + symlink `<pasta>/.github/copilot-instructions.md → <pasta>/CONTEXTO.md` |
| `kn-opencode` | `opencode` | `OPENCODE_CONFIG` apontando para JSON em `~/.cache/koine/opencode-configs/<slot>.json` + symlink `<pasta>/AGENTS.md → <pasta>/CONTEXTO.md` + `OPENCODE_DISABLE_CLAUDE_CODE=1` |

### Argumentos

- `<agente>` — nome do agente Koine (`hermes` ou agente operacional do usuário em `~/.config/koine/agentes/<nome>.md`).
- `[pasta]` — opcional. Resolução em cascata:
  1. `""` ou ausente → usa `pwd`.
  2. Alias em `~/.config/koine/aliases.json` → resolve para path canônico.
  3. Path direto (relativo ou absoluto) que exista → usa.
  4. Fuzzy match em pastas conhecidas → oferece menu (`fzf` se disponível, fallback numerado); oferece salvar alias.

### Flags

- `--substituir` — overwrite arquivos pré-existentes nos paths gerenciados pelo adapter (`CLAUDE.md`, `GEMINI.md`, symlinks). Sem a flag, conflitos abortam com mensagem clara.

### Modo bootstrap

Quando a pasta não tem `CONTEXTO.md`, o wrapper entra em **modo bootstrap**:

1. Detecta ausência de `CONTEXTO.md`.
2. Sempre usa `hermes` (independente do `<agente>` passado).
3. Gera contexto reduzido: usuário + KOINE.md + Hermes (sem escopo, sem índices).
4. Lança o cliente.

Hermes guia o usuário a criar o contexto via `/kn-02-mantem-catalogo` (fluxo contexto).

## Estrutura de configuração em runtime

```
~/.local/share/koine/           # vault readonly (XDG_DATA_HOME)
~/.config/koine/                # config do usuário (XDG_CONFIG_HOME)
  <nome>.md                     # arquivo do usuário
  escopos/<slug>.md
  dominios/<dom>.md
  agentes/<nome>.md
  aliases.json
~/.cache/koine/                 # cache descartável (XDG_CACHE_HOME)
  copilot-bundles/<slot>/
  opencode-configs/<slot>.json
```

XDG vars (`XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`) são respeitadas em todos os SOs (inclusive macOS e Windows). Ver ADR [`20260621-estrutura-config-koine.md`](../decisoes/20260621-estrutura-config-koine.md).
