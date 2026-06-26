---
id: 202606200944
tipo: decisao
status: aceito
description: ADR — Vault Koine é distribuído via go:embed dentro do binário kn-agente; subcomando instalar extrai vault e planta domínios em ~/.config/koine; instalar-habilidades symlinka skills no harness
tags: [adr, koine, distribuicao, embed, instalar, arquitetura]
---

# ADR — Distribuição via `go:embed` + `kn-agente instalar`

## Status

Aceito.

## Contexto

O conteúdo do vault Koine (`KOINE.md`, `agentes/koine/AGENTE.md`, skills `kn-*`, biblioteca de domínios) precisa chegar na máquina do usuário e ficar acessível em `~/.koine/` e `~/.config/koine/`.

Alternativas para entrega:

1. **Git clone** do repo `jrunic/koine` para `~/.koine/`. Requer git, requer auth GitHub (ou repo público), updates via `git pull` manual.
2. **`go:embed`** do vault dentro do binário. Subcomando extrai pra disk. Update = baixar novo binário.
3. **Tarball + HTTP download.** Binário busca tarball do release. Requer rede no install.

Adicionalmente, skills `kn-*` precisam ser descobertas pelo Claude Code, que lê de `~/.claude/skills/` — não de `~/.koine/habilidades/`. Tem que haver passo de integração com o harness.

## Decisão

**Vault Koine é embutido no binário via `go:embed`.**

**`kn-agente instalar`** extrai recursivamente:

- `~/.koine/` ← vault embed (KOINE.md, AGENTE.md, skills `kn-*`, templates).
- `~/.config/koine/biblioteca-dominios/` ← cópia dos 4 YAMLs seed + INDEX-`<dom>`.md, com `origem: koine-canonico` no frontmatter.

**Em runtime, `kn-agente` lê domínios apenas de `~/.config/koine/biblioteca-dominios/`.** Vault não é union path em runtime — é só fonte de delivery.

**Usuário é dono dos domínios após instalação.** Pode editar `universal.yaml`, criar novos via `kn-01-mantem-catalogo` (ramo dominio), deletar. Categorias "curado pelo método" e "criado por mim" são distinção apenas conceitual (via campo `origem:`), não estrutural.

**`kn-agente instalar` é idempotente:**

- Primeira invocação (sem `~/.koine/` existente) → extração completa.
- Re-invocação sem `--force` → compara `embed.FS` com disco, printa:
  - Versão instalada (de `~/.koine/.meta.json`) e versão a instalar (do binário).
  - Lista de arquivos modificados localmente (perderão mudanças se prosseguir).
  - Orienta uso de `--force`.
- Com `--force` → sobrescreve, atualiza `.meta.json`.

**`kn-agente mostrar-padrao <dominio>`** lê do embed e imprime o YAML/INDEX original do domínio. Permite ao usuário:

- Recuperar versão original se editou e arrependeu.
- Diffar versão local vs original que veio no release.
- Servir de fonte pra merge futuro (quando `kn-agente atualizar` precisar reconciliar).

**Skills no harness:** subcomando separado `kn-agente instalar-habilidades --para=<harness>` symlinka `~/.koine/habilidades/kn-*` em `~/.claude/skills/` ou equivalente em outros harnesses.

Flag `--para` é **obrigatória** e validada contra lista finita.

**Assinatura `.exe` Windows** fica fora do escopo do primeiro release (a decisão depende de validação empírica do contexto corp do usuário — SmartScreen vs AppLocker exigem soluções diferentes).

## Consequências

### Positivas

- **Cenário Windows corp atendido.** Binário sem dependências (sem git, sem GitHub auth, sem download secundário) maximiza chance de passar AppLocker/SmartScreen.
- **Onboarding limpo.** "Executou o programa e ele se instalou" comunica solidez de produto.
- **Modelo de update coerente** (`kn-agente atualizar` futuro). Único caminho para atualizar método.
- **Um path, uma verdade em runtime.** Sem lógica de union ou colisão entre vault e config.
- **Usuário tem ownership real** dos domínios em `~/.config/koine/`.
- **Conformidade XDG.** `~/.koine/` é readonly em fluxo Koine (não em fato — usuário pode editar, mas não é mexido por Koine).

### Negativas

- **Binário cresce ~5-15 MB** para acomodar o vault (texto puro, comprime bem).
- **Update do método** vai ser "baixar novo binário + `kn-agente instalar --force`" — não é ainda automático.
- **Usuário editando `universal.yaml`** perde edição em update sem `--force`; com `--force` sem confirmar lista de divergências, perde silencioso. Print de divergências é defesa mas requer atenção.

### Implementação

- `//go:embed vault/*` no main package.
- `cmd/kn-agente/instalar.go` extrai recursivamente respeitando estrutura.
- `~/.koine/.meta.json` registra `versao`, `instalado_em`, `binario_sha`.
- Comparação byte-a-byte com `embed.FS` para detecção de divergências.
- `cmd/kn-agente/instalar-habilidades.go` symlinka per harness (no primeiro release: `~/.claude/skills/kn-*`).
- `kn-agente mostrar-padrao` lê do embed, sem fallback para disco.

## Escopo

Esta ADR vincula **apenas o binário `kn-agente` e o vault embarcado** no repositório `koine`.

**Não vincula:**

- Mecanismos de update remoto (`kn-agente atualizar`), que entram em ADR futuro.
- Assinatura de binários Windows, que entra em ADR futuro após validação empírica.
- Outros harnesses (`copilot`, `gemini`), que entram em ADRs separados.

## Alternativas Consideradas

- **(rejeitada) Git clone direto.** Usuário precisa git instalado, repo público ou auth GitHub. Updates manuais. Dois artefatos (binário + repo).
- **(rejeitada) Tarball HTTP no install.** Requer rede no install. Vulnerável a falhas de DNS/CDN. Tarball pode entrar em `atualizar` futuramente, mas install inicial fica offline-capable.
- **(rejeitada) Symlink `~/.koine/biblioteca-dominios/` ↔ `~/.config/koine/biblioteca-dominios/`.** Resolveria duplicação mas complica modelo mental (qual é o "real"?).
- **(rejeitada) Instalar habilidades automaticamente em `instalar`.** Mistura preocupações. Multi-harness futuro fica complicado.

## Referências

- ADR `20260620-cli-kn-agente-onda-1.md` — subcomandos
- ADR `20260620-okf-conformance-e-frontmatter.md` — frontmatter dos domínios
- Documentação `go:embed` — https://pkg.go.dev/embed
