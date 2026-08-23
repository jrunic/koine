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
| `descricao` | string | Resumo curto do propósito da pasta. Cite entre aspas duplas. |
| `tipo` | string | Costume Koine: `contexto`. |
| `status` | string | `ativo`, `arquivado` etc. — informativo. |
| `tags` | lista | Tags adicionais para o usuário. |

### Valores com `:` precisam de aspas

O frontmatter é YAML, e nele um valor não-citado com dois-pontos-espaço no meio é inválido:

```yaml
descricao: Processo comercial: acompanhamento de vendas   # inválido
descricao: "Processo comercial: acompanhamento de vendas" # certo
```

O Koine repara esse caso na leitura e avisa no stderr — a sessão não quebra por causa de um dois-pontos. Mas o arquivo continua inválido para qualquer outra ferramenta que o leia, e `koine validar` aponta os arquivos nessa situação. TAB no lugar de espaço não tem reparo: o Koine recusa o arquivo nomeando linha e coluna.

## Corpo do arquivo

Tudo após o frontmatter é prosa livre. O agente IA carrega o conteúdo inteiro via `@CONTEXTO.md`. Útil para:

- Descrição do que é essa pasta de trabalho
- Padrões específicos desta pasta
- Pendências em curso
- Aprendizados emergentes durante as sessões (Hermes pode editar)
- Referências de alcance de pasta — arquivo solto na raiz, com o nome e uma linha de descrição
- A fonte de evidência da pasta (ver abaixo)

### Fonte de evidência — convenção da `/kn-13`

A `/kn-13-sabatina-plano` confere o que o usuário afirma contra uma fonte real, e pergunta qual é na abertura da sessão. Quando a pasta trabalha sempre contra a mesma fonte, declará-la no corpo do `CONTEXTO.md` evita repetir a pergunta a cada sabatina:

```md
## Fonte de evidência

`planilha-contratacoes.xlsx` nesta pasta — o registro real dos processos, exportado do sistema toda segunda.
```

Não é campo de frontmatter e não é obrigatória: é prosa que o agente lê. Sem ela, a `/kn-13` pergunta; com ela, confirma em uma linha e segue.

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

## Comportamento se faltar `CONTEXTO.md` — ou se ele estiver sem `escopo:`

`kn-<cliente> <agente> <pasta>` em pasta sem `CONTEXTO.md` entra em **modo bootstrap**:

1. Gera contexto reduzido: usuário + KOINE.md + Hermes
2. Lança o cliente IA
3. Hermes guia a criação do `CONTEXTO.md` via `/kn-02-mantem-catalogo` (Fluxo 3a)

Pasta cujo `CONTEXTO.md` **existe e é legível, mas não declara `escopo:`** também
é auto-guiada — e aí o Koine **não toca nesse arquivo**: ele é trabalho do usuário.
A pasta recebe só o arquivo do harness, como em qualquer sessão. A sessão recebe a instrução do vault mais o arquivo original, e
Hermes conduz o **Fluxo 3b** (atualizar existente), acrescentando o escopo e
preservando o conteúdo.

Só YAML irreparável (ou arquivo ilegível) continua sendo erro — com arquivo,
linha e coluna, e sem tocar no arquivo.

Detalhes: ADR [`20260620-contexto-md-local-sem-cascata.md`](../decisoes/20260620-contexto-md-local-sem-cascata.md).

## Resolução de escopos e domínios

- `escopo: <slug>` é resolvido para `~/.config/koine/escopos/<slug>.md`. Se não existir, erro explícito.
- Cada item em `dominios: [...]` é resolvido para `<pasta-referencias>/kn-indice-<dom>.md`, onde `<pasta-referencias>` vem do campo homônimo dentro do arquivo do escopo. O arquivo do índice é gerado dinamicamente pelo `kn-agente` a cada invocação.

## Não há cascata

`kn-agente` lê `CONTEXTO.md` apenas na pasta-alvo. Não sobe a árvore de diretórios; não faz merge entre níveis. Subpasta que quer contexto da pasta-pai tem duas saídas:

1. Copiar `CONTEXTO.md` da pasta-pai para a subpasta.
2. Rodar `kn-<cliente> <agente> <pasta-pai>` em vez da subpasta.

ADR de referência: [`20260620-contexto-md-local-sem-cascata.md`](../decisoes/20260620-contexto-md-local-sem-cascata.md).
