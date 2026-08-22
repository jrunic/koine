---
descricao: Contexto técnico do repositório koine — stack, padrões, estrutura e como contribuir
id: 202606201915
tipo: contexto
status: ativo
tags: [contexto, koine, python, cli]
projeto: koine
escopo: repo:koine
plataforma: "*"
---

# CONTEXTO.md — Koine
## Onde o trabalho acontece

**O trabalho de desenvolvimento acontece fora deste repositório**, nos documentos
internos do autor — é lá que a sessão abre (`jd-claude <agente> criar-koine`).

| Artefato | Lar canônico |
|---|---|
| Roadmap de ciclos, spec, plano | fora deste repositório |
| Arquivo de apoio de tarefa, diário de sessão | fora deste repositório |
| Discussão de negócio, modelo de domínio, glossário | fora deste repositório |
| **Código, testes, migrations** | **este repositório** |
| **Documentação do produto** (Diátaxis) | **este repositório**, `docs/81-referencia/` |
| **ADR de contrato da ferramenta** | **este repositório**, `docs/81-referencia/decisoes/` |
| **README, CHANGELOG** | **este repositório** |

**Razão:** spec, plano, roadmap e diário são documentos operacionais internos —
nomeiam contexto que não pertence a um repositório aberto. O repositório carrega
o que a audiência dele precisa.

**As skills leem esta seção** em vez de inferir por visibilidade. Repositório
que não declara deixa a skill sem informação, e sem informação ela erra.

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
- **Frontmatter ruim é dado ruim, não motivo para o produto não subir** — quem escreve `CONTEXTO.md`/escopo/referência é usuário comum descrevendo o próprio trabalho em português, e `descricao: Vendas B2B: metas` é a forma natural de escrever. `frontmatter.ler` parseia estrito e, só em erro, recita as linhas `chave: valor` que sozinhas não parseiam (por linha — o que já era válido não é tocado) e avisa no stderr. O que não tem reparo vira `FrontmatterInvalido` com arquivo/linha/coluna e **cada consumidor decide a política** (degradar, pular o arquivo, abortar) — a lib devolve o erro nomeado, não escolhe pelo chamador. Leitura de frontmatter a partir de caminho usa `frontmatter.ler_arquivo`, nunca `open().read()` solto. A escrita de frontmatter tem **um ponto só** (`ficha.normalizar_arquivo`): backup `.bak` livre antes de gravar, nunca em symlink nem no vault instalado, `newline=""` ponta a ponta para não trocar CRLF por LF, e falha de escrita degrada para o reparo em memória em vez de derrubar a sessão. O launch normaliza os arquivos de configuração que carrega (`ler_arquivo(normalizar_disco=True)`); a pasta-referências do usuário só por `koine validar --corrigir`. Arquivo que o Koine gera (índice) monta o frontmatter por `frontmatter.compor`, nunca concatenando linha à mão — nome de domínio vem da lista do usuário e pode ter `:`.
- **Vault é readonly em runtime** — extraído do payload de distribuição pelo `koine instalar` para `~/.local/share/koine/`. Usuário é dono de `~/.config/koine/`.
- **Marcador congelado** — `<!-- gerado por kn-agente -->` na 1ª linha de arquivos gerados; é o contrato de detecção de conflito com instalações antigas e não muda.
- **O `name` da skill é contrato de máquina, e a falha dele é silenciosa** — o OpenCode só reconhece a skill se o `name` do frontmatter casar o nome do diretório (`^[a-z0-9]+(-[a-z0-9]+)*$`) e a `description` couber em 1..1024 caracteres. Violação não dá erro: a skill some da lista de disponíveis, o que é bem pior de diagnosticar do que uma exceção. Guardado por `tests/test_vault_habilidades.py` sobre o vault inteiro. Vale para toda skill nova.
- **Skill do vault chega ao harness por cópia, não por symlink** — symlink no Windows exige privilégio de administrador que o público-alvo não tem. A documentação já mentiu sobre isso duas vezes (catálogo e mapa de arquitetura, herança do Go); ao descrever a instalação, dizer cópia.
- **Não commitar binários** — `dist/` e artefatos locais já cobertos pelo `.gitignore`.
- **SSL do Python falha em qualquer SO → fallback curl do sistema** — o OpenSSL da stdlib pode não verificar o cert: no Windows por não buscar o CA intermediário via AIA, no macOS por faltar o bundle de CA. O curl do SO usa o trust store nativo (Schannel/Keychain/CA bundle) e funciona onde o urllib falha. `atualizar` usa esse fallback em `resolver_versao`/`baixar`/sums desde a v0.4.7 (antes era win32-only; a v0.4.6 travava no macOS). Máquina já travada se recupera reinstalando via `install.sh` (100% curl) — `KOINE_VERSAO=... koine atualizar` NÃO resolve (morre igual no download).
- **Mudança que afeta Windows valida em VM AppLocker antes de release** — self-update (`atualizar`), launch e wrappers. O CI é **POSIX-only e não pega bug Windows-only**: na v0.4.3 o handoff finalizava com o pyz alvo baixado, que pode não ter `--finalizar` → finalizar com cópia do pyz atual. Lab reutilizável: Win11 ARM Enterprise (CrystalFetch + Fusion) com AppLocker escopado a um usuário restrito; o roteiro de montagem fica nos documentos internos do autor, fora deste repositório.

## Família `kn-2N` espelha o `jd-cria-design` do brain

As três skills de marca (`kn-21`/`kn-22`/`kn-23`) são a versão portável do skill interno `jd-cria-design` do Jedi Brain: mesma doutrina, dependências públicas (`npx @google/design.md`, `imagio`, `prelo`) e destinos em pasta-referências de escopo em vez de taxonomia do brain.

As duas famílias compartilham o mapeamento `DESIGN.md → tokens do prelo`. **Mudança no `MAPA-TOKENS.md` do `jd-cria-design` toca a `kn-23` também** — e vice-versa. Não há mecanismo de sincronia; é conferência manual quando o vocabulário de tokens do prelo mudar.

Estavam em sincronia em 2026-08-09, quando o prelo v1.1.0 moveu a estrutura CSS para a ferramenta e ambas passaram a emitir `tokens.css`.

**Versões mínimas das ferramentas externas:**

- `prelo` ≥ **1.2.0** para a `/kn-24-gera-pdf` — resolve caminho relativo contra a pasta do `.md`. Abaixo dela a skill não funciona sem contorno, e o contorno passou a ser nocivo: reescrever link relativo para absoluto faz o prelo gravar o caminho da máquina de origem dentro do PDF.
- `prelo` ≥ **1.2.1** para logo de marca na `/kn-23-gera-marca-prelo` — a cópia de `images/` na instalação entrou nessa versão. Antes dela a imagem ficava para trás e a regra CSS apontava para o vazio.

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
