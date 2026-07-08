---
descricao: Contexto técnico do repositório koine — stack, padrões, estrutura e como contribuir
id: 202606201915
tipo: contexto
status: ativo
tags: [contexto, koine, python, cli]
---

# CONTEXTO.md — Koine

## Propósito

Koine é uma CLI Python que injeta contexto multi-camada (usuário, agente, referências, contexto da pasta) em harnesses de IA terminal — Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode, Codex CLI.

Este documento orienta quem desenvolve o repositório. Para a visão de produto e instalação, ver [`README.md`](README.md). Para decisões arquiteturais, ver [`docs/decisoes/`](docs/decisoes/).

## Stack

- **Linguagem:** Python 3.12+ (stdlib-only em runtime; sem código nativo — nada de `.pyd`/`.so`/`.dll`)
- **CLI:** `argparse` (stdlib)
- **YAML:** PyYAML vendorizado em `src/koine/_vendor/` (puro-Python)
- **Testes:** pytest
- **Distribuição:** zipapp (`koine.pyz`) + payload `vault/` no zip de release
- **Release:** GitHub Actions (`release.yml`) — pytest, build do zip, publicação em GitHub Releases

## Estrutura do código

```
src/koine/              — pacote da aplicação
  cli.py                — entry point (subcomandos + despacho de wrappers)
  adapters/             — um módulo por cliente IA + REGISTRY (claude, antigravity, codex, copilot, opencode)
  contexto.py           — resolução do contexto (CONTEXTO.md local, sem cascata)
  render.py             — merge de seções para adapters de bundle/inline
  instalar.py           — extração do vault → XDG
  indice.py             — gerador de kn-indice-<dom>.md
  cache.py              — bundles descartáveis em ~/.cache/koine/
  pasta.py              — resolução de pasta em cascata (alias, direto, fuzzy)
  aliases.py            — CRUD de ~/.config/koine/aliases.json
  paths.py              — XDG dirs (config_dir, vault_dir, cache_dir)
  conflito.py           — marcador `<!-- gerado por kn-agente -->` + política de .bak
  launch.py             — lançamento do cliente IA (execvpe)
  wrappers.py           — geração dos wrappers kn-* com interpretador bakeado
  schema.py             — dataclasses do frontmatter (usuário, escopo)
  _vendor/              — PyYAML vendorizado (via sys.path)
vault/                  — conteúdo distribuído ao lado do koine.pyz no zip de release
  KOINE.md
  agentes/hermes.md
  conceitos/
  habilidades/kn-NN-*/
  dominios/
  templates/
scripts/
  build-pyz.py          — monta koine.pyz (+ --zip para o pacote de distribuição)
  release/              — install.sh / install.ps1 / install.bat
  skills-mode/          — zip do modo skills (ambientes que bloqueiam até o Python)
tests/                  — pytest (unit + e2e via subprocess do pyz e dos wrappers)
.github/workflows/      — release.yml
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
- **Funções/vars Python:** snake_case (PEP 8)
- **Classes:** PascalCase
- **Constantes:** UPPER_SNAKE
- **Comandos CLI:** PT-BR (ex: `instalar`, `mostrar`, `gerar`, `versao`)
- **Flags CLI:** PT-BR (ex: `--para`); `--force` mantido em inglês por convenção técnica

### Linguagem

- **Código:** inglês nos identificadores onde a convenção da comunidade pede; domínio em PT-BR quando o conceito é do método (ex.: `Lancamento`, `conflito`)
- **Comentários:** PT-BR
- **Commits:** conventional commits, em inglês
- **Slugs/pastas/comandos/flags:** PT-BR

### Testes

- **Framework:** pytest
- **Runner:** `.venv/bin/pytest -q`
- **Pasta:** `tests/` (fixtures compartilhadas em `tests/fixtures/`)
- **Isolamento:** HOME isolado por fixture (`seed.montar`) + limpeza de `XDG_*` via `conftest._isola_xdg` (autouse). Subprocessos recebem env explícito.

### Build/Run

```bash
python3 -m venv .venv && .venv/bin/pip install pytest   # setup
.venv/bin/python -m koine <args>                        # rodar do fonte
.venv/bin/python scripts/build-pyz.py --zip             # koine.pyz + zip de distribuição
.venv/bin/pytest -q                                     # suíte
```

### Release

Push de tag `v*` dispara `.github/workflows/release.yml`: pytest → build do `koine-<versao>.zip` (pyz + vault) → GitHub Release com installers (`install.sh`, `install.ps1`, `install.bat`) e `koine-skills.zip`.

## Restrições técnicas

- **Stdlib primeiro.** Nova biblioteca externa requer ADR; dependência de runtime só vendorizada puro-Python (padrão `_vendor/`).
- **Zero código nativo no pyz** — restrição-âncora da distribuição (AV corporativo bloqueia `.pyd`/`.so`/`.dll`). Guardada por teste (`test_pyz_sem_codigo_nativo`).
- **XDG direto com fallback** — usar `XDG_CONFIG_HOME`/`XDG_DATA_HOME`/`XDG_CACHE_HOME` com fallback `~/.config/koine/` etc. em todos os SOs (inclusive macOS e Windows). Detalhes: ADR `20260621-estrutura-config-koine.md`.
- **`koine instalar` é idempotente** — sem `--force`, detecta divergências e imprime, não sobrescreve silenciosamente.
- **CONTEXTO.md local-only** — koine não sobe na árvore, sem merge, sem cascata. Ausência = modo bootstrap. ADR `20260620-contexto-md-local-sem-cascata.md`.
- **Vault é readonly em runtime** — extraído do payload de distribuição pelo `koine instalar` para `~/.local/share/koine/`. Usuário é dono de `~/.config/koine/`.
- **Marcador congelado** — `<!-- gerado por kn-agente -->` na 1ª linha de arquivos gerados; é o contrato de detecção de conflito com instalações antigas e não muda.
- **Não commitar binários** — `dist/` e artefatos locais já cobertos pelo `.gitignore`.

## Decisões locais divergentes (técnicas)

- **PyYAML vendorizado, não pip-instalado** — o pyz precisa ser autocontido numa máquina que só tem o interpretador; `src/koine/_vendor/` entra no `sys.path` do pacote.
- **Wrappers kn-\* bakeiam o interpretador absoluto** — `python3` puro no PATH pode ser um Python antigo (macOS: 3.9); o `instalar` grava `sys.executable` no wrapper.

## Como contribuir

1. Issue ou discussão antes de mudança não-trivial.
2. Branch a partir de `main`.
3. Commits em conventional commits, mensagens em inglês.
4. `.venv/bin/pytest -q` verde antes de abrir PR.
5. PR descreve motivação + mudança + plano de teste.
6. Para mudança arquitetural (interface pública, layout de pastas, decisões de módulo), abrir ADR em `docs/decisoes/`.

## Referências

- [`README.md`](README.md) — visão de produto, instalação, exemplo de uso
- [`docs/decisoes/`](docs/decisoes/) — ADRs
- [`docs/referencias/`](docs/referencias/) — schema do `CONTEXTO.md`, comandos CLI
- [`CHANGELOG.md`](CHANGELOG.md) — releases
