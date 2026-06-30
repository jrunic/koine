---
descricao: Mapa estrutural do repositório koine — módulos, pacotes, fluxos e responsabilidade por arquivo
id: 202606201920
tipo: referencia
status: ativo
tags: [arquitetura, koine, go, kn-agente]
---

# Arquitetura — koine

## Mapa de pacotes

| Caminho | Responsabilidade |
|---|---|
| `cmd/kn-agente/main.go` | Entry point — define root Cobra, registra subcomandos, injeta `versao` em build-time |
| `internal/harness/interface.go` | Interface `Harness` + struct `ContextoMontado` — contrato entre o carregador e o renderizador |
| `internal/harness/claude_code.go` | Adapter Claude Code — implementa `Harness`, renderiza `CLAUDE.md` com linhas `@/` |
| `internal/config/leitor.go` | Lê `~/.config/koine/usuario.yaml` e `escopos/<slug>.yaml` |
| `internal/contexto/leitor.go` | Lê `<pasta>/CONTEXTO.md` local (sem cascata); erros explícitos se ausente |
| `internal/render/claude_code.go` | Renderização do template `claude.md.tmpl` para Claude Code |
| `internal/instalar/instalar.go` | Extrai `embed.FS` para `~/.koine/`; planta domínios seed em `~/.config/koine/`; idempotente |
| `internal/indice/gerador.go` | Varre `<base>/*.md`, agrupa por domínio, materializa `kn-indice-<dom>.md` |
| `internal/schema/usuario.go` | Struct YAML de `~/.config/koine/usuario.yaml` |
| `internal/schema/escopo.go` | Struct YAML de `~/.config/koine/escopos/<slug>.yaml` |
| `vault/` | Conteúdo embed — readonly em runtime; entrega via `kn-agente instalar` |
| `vault/KOINE.md` | Método Koine essencial (~200 linhas) |
| `vault/agentes/koine/AGENTE.md` | Agente canônico Koine — não customizável na Onda 1 |
| `vault/habilidades/kn-01-mantem-catalogo/` | Meta-skill de setup (usuario, escopo, contexto, dominio) |
| `vault/habilidades/kn-02-mantem-referencia/` | Captura de conhecimento na base OKF |
| `vault/habilidades/kn-99-encerra-sessao/` | Fechamento de sessão — diário + log.md |
| `vault/biblioteca-dominios-seed/` | 4 YAMLs seed (universal, pessoas, entidades, metodologia) + INDEX |
| `vault/templates/claude.md.tmpl` | Template `text/template` para geração do CLAUDE.md |
| `.github/workflows/release.yml` | Cross-compile + GitHub Release em push de tag |

## Fluxo principal — `kn-agente koine <pasta>`

```
main.go
  └─ rootCmd.Run(args=[koine, <pasta>])
       └─ contexto.Ler(<pasta>)          → ContextoMD{escopo, dominios}
       └─ config.Ler()                   → Usuario, Escopo{base}
       └─ indice.Gerar(base, dominios)   → kn-indice-<dom>.md
       └─ ContextoMontado{paths...}
       └─ harness.ClaudeCode.Renderizar() → CLAUDE.md
```

## Fluxo de instalação — `kn-agente instalar`

```
embed.FS (vault/*) embarcado no binário
  └─ instalar.Extrair()
       ├─ ~/.koine/               ← vault completo
       └─ ~/.config/koine/
            └─ biblioteca-dominios/  ← cópias dos seed YAMLs (origem: koine-canonico)
```

## Interface `Harness`

Abstrai o cliente IA alvo. Adapters atuais: Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode, Codex CLI.

```go
type Harness interface {
    Nome() string
    CaminhoArquivoContexto(cwd string) string
    Renderizar(dados ContextoMontado) ([]byte, error)
}
```

## Estrutura de configuração em runtime

```
~/.koine/                              # vault readonly (vem do release)
~/.config/koine/
  usuario.yaml                         # perfil do usuário
  usuario.md                           # narrativo (referenciado em CLAUDE.md)
  escopos/<slug>.yaml                  # registro de escopos
  biblioteca-dominios/<dom>.yaml       # domínios do usuário
  biblioteca-dominios/INDEX-<dom>.md
```

## Decisões de design relevantes

- ADR [`20260620-cli-kn-agente-onda-1.md`](decisoes/20260620-cli-kn-agente-onda-1.md) — sintaxe de subcomandos e `--versao`
- ADR [`20260620-contexto-md-local-sem-cascata.md`](decisoes/20260620-contexto-md-local-sem-cascata.md) — resolução local-only
- ADR [`20260620-distribuicao-embed-e-instalar.md`](decisoes/20260620-distribuicao-embed-e-instalar.md) — `go:embed` + idempotência
- ADR [`20260620-okf-conformance-e-frontmatter.md`](decisoes/20260620-okf-conformance-e-frontmatter.md) — frontmatter OKF nos arquivos da base
- ADR [`20260621-estrutura-config-koine.md`](decisoes/20260621-estrutura-config-koine.md) — estrutura de pastas, XDG, Hermes, modelo de 3 lugares
- ADR [`20260625-harness-lancamento-struct.md`](decisoes/20260625-harness-lancamento-struct.md) — interface `Harness` retorna `Lancamento`
