---
id: 202606200940
tipo: decisao
status: aceito
description: ADR — Koine adota OKF v0.1 como formato canônico da base de conhecimento; frontmatter usa inglês para campos OKF-spec e PT-BR para extensões Koine
tags: [adr, koine, okf, frontmatter, arquitetura]
---

# ADR — OKF conformance e idioma do frontmatter

## Status

Aceito.

## Contexto

A base de conhecimento que cada escopo Koine materializa precisa ser portável, parseável por agentes externos, e interoperar com ferramentas de catalogação OKF-conformantes.

A convenção PT-BR do projeto privilegia frontmatter em português — `descricao`, `tipo`, `escopo`, etc.

A spec OKF v0.1 (https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md §4.1) declara `type` como campo **REQUIRED** e recomenda `title`, `description`, `resource`, `tags`, `timestamp` — todos em inglês.

Há tensão real entre as duas convenções.

## Decisão

**Koine adota OKF v0.1 como formato canônico da base de conhecimento.**

**Frontmatter usa inglês para campos da spec OKF e PT-BR para extensões Koine.**

Campos OKF-spec (inglês):

- `type` (REQUIRED por §9.2 da spec)
- `title`
- `description`
- `resource`
- `tags`
- `timestamp`

Extensões Koine (PT-BR):

- `escopo`
- `dominios`
- `origem` (em domínios — valores: `koine-canonico` / `usuario`)

Exemplo de concept document na base:

```yaml
---
type: Reference
title: Acme Corp — diretrizes de fornecedor
description: Resumo executivo das regras de homologação e SLA contratual.
tags: [fornecedor, contrato]
timestamp: 2026-06-24T10:30:00Z
escopo: acme-corp
dominios: [negocio]
---
```

Arquivos reservados OKF (§3.1) seguem nomenclatura da spec:

- `index.md` (não `INDEX.md`)
- `log.md`

Cross-linking (§5) prefere paths bundle-relative iniciados com `/`.

## Consequências

### Positivas

- Base de conhecimento Koine é OKF-conformante. Pode ser exportada/consumida por qualquer ferramenta OKF.
- A convenção PT-BR do projeto comporta uma exceção explícita para identificadores de wire-format consumidos por comunidade externa — OKF se encaixa.
- Distinção honesta: campos de wire-format (OKF) vs campos canônicos de domínio (Koine). PT-BR continua valendo em prosa, comandos, paths, comentários.

### Negativas

- Autor escrevendo concept à mão precisa lembrar de duas convenções (EN para spec, PT-BR para extensões).

### Implementação

- Skill `kn-02-mantem-referencia` materializa frontmatter no formato híbrido.
- Skill `kn-01-mantem-catalogo` (ramo escopo) materializa `index.md` + `log.md` no formato OKF.
- O `MANIFEST.json` interno do `kn-agente instalar` é independente do OKF — é metadata de versão do vault.
- Validador `kn-agente validar` checa conformidade OKF dos arquivos `.md` na base.

## Escopo

Esta ADR vincula **apenas o repositório `koine`** — define como o binário `kn-agente` materializa frontmatter e estrutura de arquivos na base de conhecimento dos usuários.

## Alternativas Consideradas

- **(rejeitada) PT-BR puro no frontmatter, não-conformante OKF.** Convenção PT-BR preservada integralmente mas Koine deixa de ser "Bundle OKF-conforme" — usuário exportar para outro consumidor OKF não funcionaria.
- **(rejeitada) Bilíngue redundante (`type:` e `tipo:` ambos).** Compatível com tudo mas frontmatter feio e overhead de manutenção.

## Referências

- Spec OKF v0.1 — https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
