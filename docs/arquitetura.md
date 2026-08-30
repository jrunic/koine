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
| `src/koine/adapters/claude.py` | Adapter Claude Code — bundle em cache + `--add-dir` + variável de diretórios adicionais |
| `src/koine/adapters/antigravity.py` | Adapter Antigravity (`agy`) — bundle em cache + `--add-dir` |
| `src/koine/adapters/copilot.py` | Adapter Copilot CLI — bundle de `*.instructions.md` + `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` |
| `src/koine/adapters/opencode.py` | Adapter OpenCode — config JSON em cache, com `instructions` apontando para o documento composto + env vars |
| `src/koine/adapters/codex.py` | Adapter Codex CLI — arquivo inline em cache + `-c model_instructions_file=` |
| `src/koine/lancamento.py` | Dataclass `Lancamento` — contrato adapter → materialização |
| `src/koine/contexto.py` | Resolve o contexto (`ContextoMontado`) a partir de `<pasta>/CONTEXTO.md` local (sem cascata) + config do usuário |
| `src/koine/indice.py` | Varre a pasta-referências, agrupa por domínio, materializa `kn-indice-<dom>.md` |
| `src/koine/instalar.py` | Extrai o vault (payload ao lado do pyz) para `~/.local/share/koine/`; planta domínios em `~/.config/koine/`; idempotente |
| `src/koine/wrappers.py` | Gera `koine` + `kn-*` em `~/.local/bin/` com interpretador absoluto bakeado |
| `src/koine/skills.py` | Detecção de harnesses no PATH + instalação de skills `kn-*` por harness |
| `src/koine/escrita.py` | Política única de escrita na pasta do usuário — marcador, `.bak`, troca atômica |
| `src/koine/estoque.py` | O que o mecanismo anterior deixou na pasta, e o que pode sair |
| `src/koine/conflito.py` | Porta do `conflito.go`; delega a política para `escrita.py` |
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
  └─ estoque.limpar(pasta)             → remove o que o mecanismo anterior deixou
  └─ adapters.get(cliente).renderizar()→ Lancamento
  └─ _materializar(lanc, pasta)        → bundle no cache (a pasta não recebe nada)
  └─ launch.lancar(cliente, pasta)     → execvpe no cliente IA, com env e args do canal
```

## Fluxo de instalação — `koine instalar`

```
koine-<versao>.zip (koine.pyz + vault/ lado a lado)
  └─ instalar.extrair(vault_src)
       ├─ ~/.local/share/koine/        ← vault (KOINE.md, agentes/, habilidades/, templates/)
       └─ ~/.config/koine/dominios/    ← domínios canônicos plantados
  └─ wrappers.gerar(bindir, pyz, sys.executable)  ← koine + kn-* em ~/.local/bin/
  └─ canonica.configurar()             ← pasta canônica ~/koine + alias + CONTEXTO.md bootstrap
  └─ skills (detecção no PATH + prompt) ← cópia dos kn-* no harness
```

## Contrato adapter → materialização

Cada adapter expõe **duas** operações:

- `renderizar(cm) -> Lancamento` — a entrega da sessão, pelo canal do cliente. A
  pasta do usuário não recebe nada.
- `renderizar_para_pasta(cm) -> (arquivo, conteúdo)` — a materialização a pedido
  (`koine gerar`, modo skills), onde a pasta é a **única** via de entrega porque
  não há wrapper para configurar ambiente.

```python
@dataclass
class Lancamento:
    arquivos_working_dir: dict  # rel → conteúdo
    arquivos_externos: dict     # abs → conteúdo (cache)
    symlinks: dict              # link → alvo
    env_vars: dict
    extra_args: list
```

Todo adapter que renderiza `cm.contexto_path` renderiza também
`cm.instrucao_path` quando ele estiver preenchido — é por esse campo que o Koine
entrega ao agente uma instrução de sessão (hoje: pasta sem `escopo:`). Nos adapters de conteúdo embutido (claude, antigravity, codex) entra como mais
uma seção; nos de bundle por arquivo (copilot) como mais um `.instructions.md`;
no opencode, como mais uma seção do documento que o `instructions` aponta. Adapter que esquecer o campo deixa o usuário sem saída na pasta
incompleta, sem erro nenhum.

Desde a entrega por canal, `arquivos_working_dir` e `symlinks` ficam vazios em
todo adapter no launch — o que sobra na pasta é o `CONTEXTO.md` do usuário. Os
dois campos seguem no contrato porque o `_materializar` é genérico e porque o
modo bootstrap ainda materializa o `CONTEXTO.md` (que é do **launch**, não do
adapter).

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
