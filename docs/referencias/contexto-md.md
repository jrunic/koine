---
descricao: Schema do CONTEXTO.md local — frontmatter, campos obrigatórios, exemplos
id: 202606261002
tipo: referencia
status: ativo
tags: [referencia, contexto, frontmatter, ficha-koine]
---

# Referência — `CONTEXTO.md`

Arquivo que vive em cada pasta de trabalho. Informa ao Koine **qual escopo** e **quais domínios** aplicar nessa pasta.

## Frontmatter

YAML delimitado por `---` no topo do arquivo.

### Obrigatórios

| Campo | Tipo | Descrição |
|---|---|---|
| `escopo` | string | Slug do escopo registrado em `~/.config/koine/escopos/<slug>.md`. |
| `dominios` | lista de strings | Domínios cujos índices serão incluídos no contexto. Cada nome deve existir em `~/.config/koine/dominios/<nome>.md`. |

### Opcionais

| Campo | Tipo | Descrição |
|---|---|---|
| `descricao` | string | Resumo curto do propósito da pasta. |
| `tipo` | string | Costume Koine: `contexto`. |
| `status` | string | `ativo`, `arquivado` etc. — informativo. |
| `tags` | lista | Tags adicionais para o usuário. |

## Corpo do arquivo

Tudo após o frontmatter é prosa livre. O agente IA carrega o conteúdo inteiro via `@CONTEXTO.md`. Útil para:

- Descrição do que é essa pasta de trabalho
- Padrões específicos desta pasta
- Pendências em curso
- Aprendizados emergentes durante as sessões (Hermes pode editar)

## Exemplo

```markdown
---
escopo: piloto
dominios: [universal, tecnologia]
tipo: contexto
status: ativo
---

# Projeto piloto

Pasta de teste do Koine no macOS. Cliente IA padrão: Claude Code.

## Padrões locais

- Comentários em Markdown sempre em PT-BR
- Commits em conventional commits (inglês)

## Pendências

- Validar instalação em Windows quando tiver a VM pronta
```

## Comportamento se faltar `CONTEXTO.md`

`kn-<cliente> hermes <pasta>` em pasta sem `CONTEXTO.md` entra em **modo bootstrap**:

1. Gera contexto reduzido: usuário + KOINE.md + Hermes
2. Lança o cliente IA
3. Hermes guia a criação do `CONTEXTO.md` via `/kn-02-mantem-catalogo` (fluxo contexto)

Detalhes: ADR [`20260620-contexto-md-local-sem-cascata.md`](../decisoes/20260620-contexto-md-local-sem-cascata.md).

## Resolução de escopos e domínios

- `escopo: <slug>` é resolvido para `~/.config/koine/escopos/<slug>.md`. Se não existir, erro explícito.
- Cada item em `dominios: [...]` é resolvido para `<pasta-referencias>/kn-indice-<dom>.md`, onde `<pasta-referencias>` vem do campo homônimo dentro do arquivo do escopo. O arquivo do índice é gerado dinamicamente pelo `kn-agente` a cada invocação.

## Não há cascata

`kn-agente` lê `CONTEXTO.md` apenas na pasta-alvo. Não sobe a árvore de diretórios; não faz merge entre níveis. Subpasta que quer contexto da pasta-pai tem duas saídas:

1. Copiar `CONTEXTO.md` da pasta-pai para a subpasta.
2. Rodar `kn-<cliente> <agente> <pasta-pai>` em vez da subpasta.

ADR de referência: [`20260620-contexto-md-local-sem-cascata.md`](../decisoes/20260620-contexto-md-local-sem-cascata.md).
