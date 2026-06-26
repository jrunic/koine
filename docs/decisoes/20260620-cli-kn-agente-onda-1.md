---
id: 202606200941
tipo: decisao
status: aceito
description: ADR — Sintaxe canônica do CLI kn-agente — posicional para ação default, subcomandos PT-BR, --versao como flag universal
tags: [adr, koine, cli, kn-agente, arquitetura]
---

# ADR — CLI `kn-agente` — sintaxe inicial

## Status

Aceito.

## Contexto

`kn-agente` é o binário que lê configurações e contexto, e materializa o arquivo de contexto do cliente IA (`CLAUDE.md` no primeiro adapter).

Precisa expor verbos para: gerar contexto, mostrar debug, validar, instalar vault, instalar habilidades em harness, mostrar versão original de domínio, mostrar versão do binário.

Duas tensões de design:

1. **Subcomandos vs flag-modes.** Cobra suporta ambos.
2. **Idioma dos verbos.** PT-BR (padrão do projeto) vs inglês (convenção Go community).

## Decisão

**Sintaxe canônica:**

```
kn-agente <agente> <pasta>                         # default: escreve CLAUDE.md em <pasta>
kn-agente mostrar <agente> <pasta>                 # imprime contexto resolvido em stdout
kn-agente validar <pasta>                          # valida frontmatter OKF da base do escopo
kn-agente instalar                                 # extrai vault embed + planta domínios em ~/.config/koine/
kn-agente instalar --force                         # sobrescreve mesmo com divergências locais
kn-agente instalar-habilidades --para=<harness>    # symlinka kn-* no harness destino
kn-agente mostrar-padrao <dominio>                 # imprime versão original do domínio (do embed)
kn-agente --versao                                 # versão + commit + build date
```

**Regras:**

- Ação principal (gerar CLAUDE.md) é **default**, sem subcomando — `kn-agente <agente> <pasta>`.
- Verbos auxiliares são **subcomandos PT-BR**: `mostrar`, `validar`, `instalar`, `instalar-habilidades`, `mostrar-padrao`.
- `--versao` é **flag universal** (não subcomando), preenchida pelo campo `Version` do Cobra.
- `<agente>` é obrigatório no default e em `mostrar` (no primeiro release, único valor aceito é `koine`).
- `--para=<harness>` é **flag obrigatória** em `instalar-habilidades`. Valores aceitos são finitos (no primeiro release, apenas `--para=claude`); valor desconhecido retorna erro com lista de valores válidos.

## Consequências

### Positivas

- Usuário digita `kn-agente koine .` toda vez que quer regenerar CLAUDE.md na pasta atual — gesto curto, memorizável.
- `validar` sem `<agente>` reflete honestamente que valida estrutura OKF, não renderização.
- `--versao` segue convenção universal (git, kubectl, gh) — afinidade imediata para quem conhece outras CLIs.
- Subcomandos PT-BR honram a convenção do projeto sem custo de aprendizado externo significativo.

### Negativas

- `instalar` é o único subcomando que **escreve fora de `~/.koine/`** (também escreve em `~/.config/koine/biblioteca-dominios/` e `~/.claude/skills/` via `instalar-habilidades`). Viola invariante "instalar só toca vault" mas é justificado: propósito é deixar o usuário pronto pra usar, não só ter arquivos no disco.
- Quando família de agentes crescer (`koine-tech`, `koine-dev` no futuro), usuário precisará explicitar `koine` em cada invocação. Aceitável — o hábito do par `kn-agente koine` já estará formado.

### Implementação

- Cobra root command + 5 subcommands (`mostrar`, `validar`, `instalar`, `instalar-habilidades`, `mostrar-padrao`).
- Root command exige 2 args posicionais (agente, pasta) no modo default.
- Flag global `--versao` preenchida via `cobra.Command{Version: ...}`.
- Validação de `--para` em `instalar-habilidades` com lista finita (`claude` no primeiro release).

## Escopo

Esta ADR vincula **apenas o binário `kn-agente` do repositório `koine`**.

**Não vincula:**

- Subcomandos futuros (`atualizar`, `auditar`), que entrarão por ADRs subsequentes se forem decisões não-óbvias.

## Alternativas Consideradas

- **(rejeitada) Tudo via flag-mode** (`kn-agente <agente> <pasta> --mostrar`). Mais minimalista mas trata `validar` (sem agente) como caso especial.
- **(rejeitada) Verbos em inglês.** Convergência com Cobra/Go é estética; padrão PT-BR do projeto é prioridade.
- **(rejeitada) `kn-agente` assume `koine` se omitido.** Mais terso mas perde sinal explícito quando família de agentes crescer.

## Referências

- ADR `20260620-distribuicao-embed-e-instalar.md` — semântica de `instalar` e `instalar-habilidades`
