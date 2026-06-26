---
id: 202606200942
tipo: decisao
status: aceito
description: ADR — kn-agente resolve CONTEXTO.md apenas na pasta-alvo, sem subir na árvore e sem merge entre níveis
tags: [adr, koine, contexto, harness, arquitetura]
---

# ADR — `CONTEXTO.md` é local — sem cascata, sem merge

## Status

Aceito.

## Contexto

`kn-agente <agente> <pasta>` precisa de uma forma de descobrir **qual escopo** e **quais domínios** aplicar para a pasta de trabalho.

Versão inicial proposta previa cascata em 4 passos: (1) `.koine/escopo.yaml` na pasta atual, (2) subir buscando `CONTEXTO.md`, (3) `~/.config/koine/mapeamento-pastas.yaml` por glob, (4) fallback `universal`.

Cascata abre 4 ambiguidades:

1. Parar no primeiro `CONTEXTO.md` ou merge ao subir?
2. Teto da subida (`$HOME`? root?)?
3. CONTEXTO.md parcial (sem `escopo:` ou sem `dominios:`)?
4. Nenhum encontrado até a raiz?

## Decisão

**Implementação atual usa apenas resolução local:**

- `kn-agente <agente> <pasta>` exige `CONTEXTO.md` em `<pasta>` exata.
- **Sem subida** na árvore de diretórios.
- **Sem merge** entre níveis.
- **Sem fallback silencioso** para escopo/domínio default.

Ausência de `CONTEXTO.md` na pasta-alvo = **erro com instrução clara**:

```
Erro: nenhum CONTEXTO.md em <pasta>.
Rode /kn-01-mantem-catalogo (ramo contexto) aqui, ou aponte
para uma pasta que contenha CONTEXTO.md.
```

Subpasta que quer contexto da pasta-pai tem duas saídas:

1. Copiar (`cp`) o `CONTEXTO.md` da pasta-pai pra subpasta.
2. Rodar `kn-agente koine <pasta-pai>` em vez de `kn-agente koine <subpasta>`.

## Consequências

### Positivas

- `internal/contexto/leitor.go` simplifica drasticamente — leitura direta de `<pasta>/CONTEXTO.md`, sem árvore.
- Localidade explícita é tese Koine: pasta de trabalho é onde a sessão acontece; o contrato com o agente deve estar visível ali, não enterrado na hierarquia.
- Fail-loud é melhor que fail-silent. CLAUDE.md gerado com escopo errado leva agente burro silenciosamente; erro explícito força a correção.
- Cobertura suficiente para uso típico: cada pasta de trabalho tem seu CONTEXTO.md materializado explicitamente.

### Negativas

- Usuários que querem hierarquia de contexto precisam ser explícitos: copiam o `CONTEXTO.md` da pasta-pai, editam diferenças, ou usam `cd` para a pasta-pai antes de invocar.
- Possíveis pedidos legítimos por herança ficam para versões futuras.

### Implementação

- `internal/contexto/leitor.go` lê `<pasta>/CONTEXTO.md` apenas.
- Documentação no KOINE.md explicita: "CONTEXTO.md é local. Cada pasta de trabalho tem o seu."
- Mensagem de erro contém instrução acionável ("rode /kn-01-mantem-catalogo aqui").

## Escopo

Esta ADR vincula **apenas o binário `kn-agente` do repositório `koine`** — define como o harness resolve contexto da pasta de trabalho.

**Não vincula:**

- Mecanismos futuros de resolução por glob, wildcard de escopo (`escopos: ["*"]`), ou herança de escopo-pai. Ficam em aberto para versões futuras.

## Alternativas Consideradas

- **(rejeitada) Cascata acumulativa (merge ao subir).** Conflitos entre níveis viram bug silencioso.
- **(rejeitada) Primeiro encontrado vence, parando em `$HOME`.** Mais simples que merge mas ainda esconde de onde veio o resolved.
- **(rejeitada) Fallback silencioso para `universal`.** Rodar `kn-agente` em pasta sem CONTEXTO.md geraria CLAUDE.md sem contexto, agente burro.

## Referências

- ADR `20260620-cli-kn-agente-onda-1.md` — sintaxe do CLI
