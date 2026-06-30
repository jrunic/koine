---
descricao: Referência dos comandos do binário kn-agente e dos wrappers de cliente IA
id: 202606261001
tipo: referencia
status: ativo
tags: [referencia, cli, kn-agente]
---

# Referência — CLI

## `kn-agente` — motor administrativo

### `kn-agente instalar [--force] [--para=<harness>]`

Comando único de configuração inicial. Executa as fases:

1. **Extração do vault** — embed `vault/` → `~/.local/share/koine/`
2. **Plantio de domínios canônicos** — `~/.config/koine/dominios/` (universal, negocio, tecnologia, pessoal)
3. **Symlinks de cliente** — `kn-claude`, `kn-agy`, `kn-copilot`, `kn-opencode`, `kn-codex` no mesmo diretório do binário
4. **Pasta canônica + alias** — prompt-com-default (default `~/koine`); cria pasta; registra alias `koine` em `~/.config/koine/aliases.json`; gera `<pasta>/CONTEXTO.md` com `bootstrap: true` a partir do embed `vault/bootstrap/CONTEXTO.md`
5. **Skills de harness** — detecta clientes IA no PATH; para cada detectado, prompt `Y/n` para instalar skills `kn-*`. Se zero detectados, exibe orientação completa (Node.js, Homebrew em macOS, lista dos 5 clientes IA com comandos por OS)

Flags:

- `--force` — sobrescreve arquivos divergentes do embed sem prompt.
- `--para=<harness>` — instala skills do harness especificado sem prompt (suportados: `claude`, `agy`, `copilot`, `opencode`, `codex`).

Idempotente em todas as fases. Em modo não-interativo (stdin sem TTY), aceita defaults sem prompts.

Modo não-interativo é detectado via `golang.org/x/term`.

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

Dois caminhos disparam carregamento reduzido (sem escopo nem domínios):

**1. Bootstrap implícito** — pasta sem `CONTEXTO.md`:

1. Wrapper detecta ausência do arquivo.
2. Sempre usa `hermes` (independente do `<agente>` passado).
3. Gera contexto reduzido: usuário + KOINE.md + Hermes.
4. Lança o cliente.

Hermes guia o usuário a criar o contexto via `/kn-02-mantem-catalogo` (fluxo contexto).

**2. Bootstrap explícito** — `CONTEXTO.md` com `bootstrap: true` no cabeçalho:

1. `Resolver` lê o arquivo e detecta o flag.
2. Bypassa validação de escopo/dominios obrigatórios.
3. Carrega contexto reduzido + **inclui o corpo do CONTEXTO.md** (com instruções para Hermes).
4. Força agente Hermes (emite warning se `<agente>` solicitado era outro).
5. Lança o cliente.

Este caminho é usado pelo `kn-agente instalar` para a pasta canônica `~/koine` — o `CONTEXTO.md` gerado instrui Hermes a iniciar `/kn-01-recebe-usuario` automaticamente. Ao final do onboarding, `/kn-01` reescreve o `CONTEXTO.md` substituindo `bootstrap: true` pelo escopo `koine` real, e o caminho de bootstrap explícito deixa de disparar.

Ver ADR `20260627-bootstrap-flag-em-contexto-md.md`.

### `kn-agente instalar-habilidades --para=<harness>`

Caminho administrativo separado para instalar (symlinkar) skills `kn-*` no harness alvo. Útil quando você instalou um cliente IA **depois** do `kn-agente instalar` inicial e quer adicionar as skills sem re-rodar a instalação inteira.

Harnesses suportados:
- `claude` → `~/.claude/skills/`
- `agy` → `~/.gemini/antigravity-cli/skills/`
- `copilot` → `~/.copilot/skills/`
- `opencode` → `~/.config/opencode/skills/`

`kn-agente instalar` chama esta lógica internamente; uso direto é só para casos pontuais.

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
