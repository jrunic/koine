---
descricao: Referência dos comandos do CLI koine e dos wrappers de cliente IA
id: 202606261001
tipo: referencia
status: ativo
tags: [referencia, cli, kn-agente]
---

# Referência — CLI

## `koine` — motor administrativo

### `koine instalar [--force] [--para=<harness>]`

Comando único de configuração inicial. Executa as fases:

1. **Extração do vault** — `vault/` do zip de distribuição (ao lado do `koine.pyz`) → `~/.local/share/koine/`
2. **Plantio de domínios canônicos** — `~/.config/koine/dominios/` (universal, negocio, tecnologia, pessoal)
3. **Wrappers de cliente** — `koine` + `kn-*` em `~/.local/bin/`, invocando o Python detectado na instalação
4. **Pasta canônica + alias** — prompt-com-default (default `~/koine`); cria pasta; registra alias `koine` em `~/.config/koine/aliases.json`; gera `<pasta>/CONTEXTO.md` com `bootstrap: true` a partir de `vault/bootstrap/CONTEXTO.md`
5. **Skills de harness** — detecta clientes IA no PATH; para cada detectado, prompt `Y/n` para instalar skills `kn-*`. Se zero detectados, exibe orientação completa (Node.js, Homebrew em macOS, lista dos 5 clientes IA com comandos por OS)

Flags:

- `--force` — sobrescreve arquivos divergentes do vault sem prompt.
- `--para=<harness>` — instala skills do harness especificado sem prompt (suportados: `claude`, `agy`, `copilot`, `opencode`, `codex`).

Idempotente em todas as fases. Em modo não-interativo (stdin sem TTY, detectado via `sys.stdin.isatty()`), aceita defaults sem prompts.

### `koine atualizar [--force]`

Self-update para a última release. Fases:

1. **Resolução da versão** — segue o redirect de `releases/latest` do github; ou usa a tag fixada em `KOINE_VERSAO`. No-op quando já na versão-alvo (a menos de `--force`).
2. **Download + verificação** — baixa `koine-<versao>.zip` e `SHA256SUMS` (do github ou de `KOINE_BASE_URL`) e valida o hash antes de aplicar.
3. **Aplicação** — reaproveita o caminho de instalação: refresca o vault shipped preservando os `dominios` do usuário, regenera os wrappers e reinstala skills nos harnesses detectados.
4. **Auto-troca do pyz** — in-process no POSIX; no Windows delega a um processo-filho da versão nova (stdio em log em `~/.cache/koine/atualizar.log`), sem trampolim `.bat`/`.ps1`.

Execução 100% Python — nenhum `.bat`/`.ps1`/powershell — para políticas que bloqueiam executáveis e powershell.

Flags:

- `--force` — reinstala mesmo quando já na versão-alvo.

Variáveis de ambiente:

- `KOINE_VERSAO=vX.Y.Z` — fixa a versão-alvo (pula a resolução `latest`).
- `KOINE_BASE_URL=<url>` — espelho de onde baixar o zip/`SHA256SUMS`, para ambientes com github bloqueado.

No Windows, se o download direto do github falhar por cadeia de certificado incompleta (o OpenSSL da stdlib não busca o CA intermediário via AIA), o download cai automaticamente para o `curl.exe` do sistema (Schannel, faz AIA); persistindo a falha, a mensagem orienta rodar Windows Update ou usar `KOINE_BASE_URL`.

### `koine gerar <agente> [pasta]`

Gera o arquivo de contexto do cliente (`CLAUDE.md`, `GEMINI.md`, etc.) na pasta, sem abrir o cliente. Útil para debug.

- `<agente>` — nome do agente (`hermes` ou agente operacional do usuário).
- `[pasta]` — opcional; default é `pwd`.

### `koine mostrar <agente> <pasta>`

Imprime em stdout o contexto resolvido — usuário, agente, escopo, índices, contexto local. Não escreve arquivo.

### `koine versao`

Imprime versão e sai.

## Wrappers de cliente IA — `kn-<cliente> <agente> [pasta]`

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

### Conflitos em arquivos gerenciados

Ao materializar (`CLAUDE.md`, `GEMINI.md`, symlinks):

- Arquivo gerado pelo Koine (marcador `<!-- gerado por kn-agente -->` na 1ª linha) → regenerado sem backup.
- Arquivo do usuário → preservado como `<nome>.bak` (nunca sobrescreve um `.bak` existente) com aviso em stderr.
- Symlink apontando para outro alvo, ou diretório no lugar do arquivo → aborta com mensagem clara.

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

Este caminho é usado pelo `koine instalar` para a pasta canônica `~/koine` — o `CONTEXTO.md` gerado instrui Hermes a iniciar `/kn-01-recebe-usuario` automaticamente. Ao final do onboarding, `/kn-01` reescreve o `CONTEXTO.md` substituindo `bootstrap: true` pelo escopo `koine` real, e o caminho de bootstrap explícito deixa de disparar.

Ver ADR `20260627-bootstrap-flag-em-contexto-md.md`.

### `koine instalar-habilidades --para=<harness>`

Caminho administrativo separado para instalar (symlinkar) skills `kn-*` no harness alvo. Útil quando você instalou um cliente IA **depois** do `koine instalar` inicial e quer adicionar as skills sem re-rodar a instalação inteira.

Harnesses suportados:
- `claude` → `~/.claude/skills/`
- `agy` → `~/.gemini/antigravity-cli/skills/`
- `copilot` → `~/.copilot/skills/`
- `opencode` → `~/.config/opencode/skills/`

`koine instalar` chama esta lógica internamente; uso direto é só para casos pontuais.

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
