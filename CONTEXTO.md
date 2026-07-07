---
descricao: Contexto técnico do repositório koine — stack, padrões, estrutura e como contribuir
id: 202606201915
tipo: contexto
status: ativo
tags: [contexto, koine, go, cli]
---

# CONTEXTO.md — Koine

## Propósito

Koine é uma CLI Go que injeta contexto multi-camada (usuário, agente, referências, contexto da pasta) em harnesses de IA terminal — Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode.

Este documento orienta quem desenvolve o repositório. Para a visão de produto e instalação, ver [`README.md`](README.md). Para decisões arquiteturais, ver [`docs/decisoes/`](docs/decisoes/) (após Task 10 da migração).

## Stack

- **Linguagem:** Go 1.26+
- **CLI framework:** Cobra (`github.com/spf13/cobra`)
- **YAML:** `gopkg.in/yaml.v3`
- **Templates:** `text/template` (stdlib)
- **Embed:** `embed` (stdlib)
- **Logging:** `log/slog` (stdlib)
- **Testes:** `testing` (stdlib)
- **Release:** GitHub Actions + cross-compile (macOS arm64/amd64, Windows amd64, Linux amd64)

## Estrutura do código

```
cmd/kn-agente/          — entry point CLI (main.go + subcomandos)
internal/
  harness/              — interface Harness + adapters por cliente IA
  config/               — leitor de ~/.config/koine/
  contexto/             — parser de CONTEXTO.md local (sem cascata)
  render/               — renderização do arquivo de contexto do harness
  instalar/             — extração do vault embed
  indice/               — gerador de kn-indice-<dom>.md
  cache/                — bundles descartáveis em ~/.cache/koine/
  pasta/                — resolução de pasta em cascata (alias, direto, fuzzy)
  aliases/              — CRUD de ~/.config/koine/aliases.json
  paths/                — XDG dirs (ConfigDir, VaultDir, CacheDir)
  schema/               — structs YAML
vault/                  — conteúdo embed no binário (via //go:embed)
  KOINE.md
  agentes/hermes.md
  conceitos/
  habilidades/kn-NN-*/
  dominios/
  templates/
.github/workflows/      — release.yml com matriz cross-compile
docs/
  decisoes/             — ADRs
  tutoriais/            — Diátaxis
  guias/                — Diátaxis
  referencias/          — Diátaxis
  explicacoes/          — Diátaxis
```

## Padrões técnicos

### Naming

- **Arquivos/pastas/slugs:** kebab-case
- **Funções/vars Go:** camelCase (convenção Go)
- **Tipos/structs:** PascalCase
- **Constantes:** UPPER_SNAKE
- **Comandos CLI:** PT-BR (ex: `instalar`, `mostrar`, `validar`)
- **Flags CLI:** PT-BR (ex: `--para`, `--versao`); `--force` mantido em inglês por convenção técnica
- **Módulo Go:** `github.com/jrunic/koine`

### Linguagem

- **Código:** inglês (convenção Go)
- **Comentários:** PT-BR
- **Commits:** conventional commits, em inglês
- **Slugs/pastas/comandos/flags:** PT-BR

### Testes

- **Framework:** `testing` (stdlib — sem testify, gomock ou similares sem ADR)
- **Runner:** `go test ./...`
- **Pasta:** testes ao lado do código (`<pkg>_test.go`)
- **Isolamento:** var de pacote injetável (`var lookup… = fn`) em vez de `os.Setenv` em código de produção

### Build/Run

```bash
go mod tidy                          # setup
go build -o kn-agente ./cmd/kn-agente
go run  ./cmd/kn-agente <args>
go test ./...
```

### Lint/Format

```bash
go fmt ./...
go vet ./...
```

### Release

Push de tag dispara `.github/workflows/release.yml`. Binários cross-compile publicados em GitHub Releases.

## Restrições técnicas

- **Stdlib primeiro.** Nova biblioteca externa requer ADR.
- **`os.UserConfigDir()` / `os.UserCacheDir()` PROIBIDOS** — no Darwin ignoram `XDG_CONFIG_HOME` e retornam `~/Library/Application Support/`. Usar `os.Getenv("XDG_CONFIG_HOME")` direto com fallback `~/.config/koine/`. Idem para Cache e Data. Detalhes: ADR `20260621-estrutura-config-koine.md`.
- **`embed.FS` via `assets.go` na raiz do módulo** — `//go:embed vault` só é válido onde `vault/` é subdiretório do arquivo Go. Pacote raiz (`package koine` em `assets.go`) exporta `VaultFS embed.FS`; subpacotes recebem como `fs.FS` injetado.
- **`kn-agente instalar` é idempotente** — sem `--force`, detecta divergências e imprime, não sobrescreve silenciosamente.
- **CONTEXTO.md local-only** — kn-agente não sobe na árvore, sem merge, sem cascata. Ausência = modo bootstrap. ADR `20260620-contexto-md-local-sem-cascata.md`.
- **Vault é readonly em runtime** — extraído de `embed.FS` pelo `kn-agente instalar` para `~/.local/share/koine/`. Usuário é dono de `~/.config/koine/`.
- **Não commitar binários** — `dist/`, `*.exe`, `kn-agente` já cobertos pelo `.gitignore`.

## Decisões locais divergentes (técnicas)

- **Testes sem framework** — stdlib `testing` apenas. testify é comum na comunidade Go mas stdlib é suficiente para o escopo atual e reduz dependências.
- **Injeção via var de pacote para isolar testes de XDG** — funções que dependem de `paths.ConfigDir()` em runtime usam `var lookup… = func() string { return paths.ConfigDir() }` como hook; testes sobrescrevem a var com `t.TempDir()`. Padrão adotado em `internal/aliases`, `internal/pasta`, `internal/contexto`, `internal/indice`, `internal/cache`. Evita `os.Setenv` em código de produção.

## Como contribuir

1. Issue ou discussão antes de mudança não-trivial.
2. Branch a partir de `main`.
3. Commits em conventional commits, mensagens em inglês.
4. `go fmt ./... && go vet ./... && go test ./...` verde antes de abrir PR.
5. PR descreve motivação + mudança + plano de teste.
6. Para mudança arquitetural (interface pública, layout de pastas, decisões de pacote), abrir ADR em `docs/decisoes/`.

## Referências

- [`README.md`](README.md) — visão de produto, instalação, exemplo de uso
- [`docs/decisoes/`](docs/decisoes/) — ADRs
- [`docs/referencias/`](docs/referencias/) — schema do `CONTEXTO.md`, comandos CLI
- [`CHANGELOG.md`](CHANGELOG.md) — releases
