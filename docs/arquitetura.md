---
descricao: Mapa estrutural do repositório koine — módulos, fluxos e responsabilidade por arquivo
id: 202606201920
tipo: referencia
status: ativo
tags: [arquitetura, koine, python, cli]
---

# Arquitetura — koine

## Mapa de módulos

| Caminho | Responsabilidade |
|---|---|
| `src/koine/cli.py` | Entry point — subcomandos (`instalar`, `instalar-habilidades`, `gerar`, `mostrar`, `versao`) + despacho de wrappers (`koine <cliente> <agente> [pasta]`) |
| `src/koine/adapters/__init__.py` | `REGISTRY` cliente → módulo do adapter — fonte única para despacho e emissão de wrappers |
| `src/koine/adapters/claude.py` | Adapter Claude Code — renderiza `CLAUDE.md` com linhas `@/` (estilo ponteiro) |
| `src/koine/adapters/antigravity.py` | Adapter Antigravity (`agy`) — `GEMINI.md` com `@path` includes |
| `src/koine/adapters/copilot.py` | Adapter Copilot CLI — bundle em `~/.cache/koine/` + env var + symlink |
| `src/koine/adapters/opencode.py` | Adapter OpenCode — config JSON em cache + env vars |
| `src/koine/adapters/codex.py` | Adapter Codex CLI — `AGENTS.md` inline (conteúdo embutido) + `extra_args` |
| `src/koine/lancamento.py` | Dataclass `Lancamento` — contrato adapter → materialização |
| `src/koine/contexto.py` | Resolve o contexto (`ContextoMontado`) a partir de `<pasta>/CONTEXTO.md` local (sem cascata) + config do usuário |
| `src/koine/indice.py` | Varre a pasta-referências, agrupa por domínio, materializa `kn-indice-<dom>.md` |
| `src/koine/instalar.py` | Extrai o vault (payload ao lado do pyz) para `~/.local/share/koine/`; planta domínios em `~/.config/koine/`; idempotente |
| `src/koine/wrappers.py` | Gera `koine` + `kn-*` em `~/.local/bin/` com interpretador absoluto bakeado |
| `src/koine/skills.py` | Detecção de harnesses no PATH + instalação de skills `kn-*` por harness |
| `src/koine/conflito.py` | Marcador `<!-- gerado por kn-agente -->` + política de conflito (`regenera` / `.bak` / erro) |
| `src/koine/launch.py` | Lançamento do cliente IA (`execvpe`) com env/args do `Lancamento` |
| `src/koine/pasta.py` | Resolução de pasta em cascata (pwd, alias, path direto, fuzzy) |
| `src/koine/paths.py` | XDG dirs (`config_dir`, `vault_dir`, `cache_dir`) com fallback `~/.config` etc. |
| `src/koine/schema.py` | Dataclasses do frontmatter (usuário, escopo) |
| `src/koine/_vendor/` | PyYAML vendorizado (puro-Python, via `sys.path`) |
| `vault/` | Conteúdo distribuído — readonly em runtime; entrega via `koine instalar` |
| `scripts/build-pyz.py` | Monta `koine.pyz` (zipapp) e, com `--zip`, o `koine-<versao>.zip` (pyz + vault lado a lado) |
| `.github/workflows/release.yml` | pytest → build do zip → GitHub Release em push de tag |

## Fluxo principal — `kn-claude <agente> [pasta]`

```
cli.main([cliente, agente, pasta])
  └─ pasta.resolver(arg)               → path absoluto (alias/direto/fuzzy)
  └─ contexto + indice                 → ContextoMontado{paths...}
  └─ adapters.get(cliente).renderizar()→ Lancamento
  └─ _materializar(lanc, pasta)        → CLAUDE.md / bundle / symlinks (com política de conflito)
  └─ launch.lancar(cliente, pasta)     → execvpe no cliente IA
```

## Fluxo de instalação — `koine instalar`

```
koine-<versao>.zip (koine.pyz + vault/ lado a lado)
  └─ instalar.extrair(vault_src)
       ├─ ~/.local/share/koine/        ← vault (KOINE.md, agentes/, habilidades/, templates/)
       └─ ~/.config/koine/dominios/    ← domínios canônicos plantados
  └─ wrappers.gerar(bindir, pyz, sys.executable)  ← koine + kn-* em ~/.local/bin/
  └─ canonica.configurar()             ← pasta canônica ~/koine + alias + CONTEXTO.md bootstrap
  └─ skills (detecção no PATH + prompt) ← symlinks kn-* no harness
```

## Contrato adapter → materialização

Cada adapter expõe `renderizar(cm: ContextoMontado) -> Lancamento`:

```python
@dataclass
class Lancamento:
    arquivos_working_dir: dict  # rel → conteúdo
    arquivos_externos: dict     # abs → conteúdo (cache)
    symlinks: dict              # link → alvo
    env_vars: dict
    extra_args: list
```

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
```

## Decisões de design relevantes

- ADR [`20260620-cli-kn-agente-onda-1.md`](decisoes/20260620-cli-kn-agente-onda-1.md) — sintaxe de subcomandos
- ADR [`20260620-contexto-md-local-sem-cascata.md`](decisoes/20260620-contexto-md-local-sem-cascata.md) — resolução local-only
- ADR [`20260621-estrutura-config-koine.md`](decisoes/20260621-estrutura-config-koine.md) — estrutura de pastas, XDG, Hermes, modelo de 3 lugares
- ADR [`20260625-harness-lancamento-struct.md`](decisoes/20260625-harness-lancamento-struct.md) — contrato `Lancamento`
- ADRs históricos da era Go (`20260620-distribuicao-embed-e-instalar.md`, `20260626-golang-x-term-deteccao-terminal.md`) — registram decisões da v0.3.x; a semântica (instalar idempotente, detecção de TTY) sobrevive no port Python
