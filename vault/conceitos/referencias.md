---
type: Concept
title: Referências
description: Doutrina meta sobre referências catalogadas no Koine — função, distinção agregado/unidade, anatomia da pasta-referências, Ficha Koine, tipos, ciclo de vida
origem: koine-canonico
dominios: [metodologia]
tags: [conceito, referencia, metodologia, pasta-referencias, okf]
---

# Conceito: Referências

Doutrina sobre referências no Koine, lida pela skill `/kn-11-mantem-referencia` quando precisa catalogar ou atualizar conhecimento. Carregada sob demanda — não vai em runtime universal.

## O que é referência

**Referência é uma unidade discreta de conhecimento catalogada com identidade própria** dentro do escopo do usuário. Cada referência é um arquivo `.md` que dá ao agente — em sessões futuras — o contexto necessário para tratar aquele item (pessoa, organização, decisão, aprendizado, evento) como entidade conhecida.

Referência é a memória de longa duração do usuário no Koine. Diferente do diário (registro do que aconteceu numa sessão) e do CONTEXTO.md (estado da pasta de trabalho atual), referências sobrevivem além da sessão e atravessam pastas de trabalho dentro do mesmo escopo.

## Alcance de uma referência

Toda referência tem **alcance** — quantas pastas de trabalho do escopo a consomem. Dois alcances possíveis:

- **Alcance de escopo** — referência útil a mais de uma pasta de trabalho do escopo. Mora na **pasta-referências do escopo**. Aparece no `kn-indice-<dom>.md` carregado por toda sessão dentro do escopo que declare o domínio correspondente. Catalogada por `/kn-11-mantem-referencia`.
- **Alcance de pasta** — referência útil apenas a uma pasta de trabalho. Mora **na raiz da própria pasta de trabalho** como `.md` solto, listada em `CONTEXTO.md` (nome do arquivo + descrição). Não entra em nenhum `kn-indice-*`; o agente vê pelo `@/` do CONTEXTO.md em runtime. Materializada por `/kn-99-encerra-sessao` (despacho normal) ou por `/kn-11` quando o usuário invocar diretamente.

**Não é tipo nem domínio diferente** — é a **mesma referência**, com localização diferente baseada no alcance. Move-se de uma localização para outra se o alcance mudar (ex: nasce local, vira de escopo quando outra pasta de trabalho passa a precisar).

**Quem decide o alcance.** O agente em sessão **não sabe** quantas outras pastas de trabalho do escopo existem nem o que elas precisam — pergunta ao usuário: *"Esta referência se aplica a outras pastas de trabalho deste escopo?"*. Default seguro quando dúvida: **alcance de pasta** (menos invasivo; promover para escopo depois é trivial; reverter um `kn-indice-*` poluído é caro).

**Frase vs arquivo.** Para alcance de pasta, prefira **uma linha em CONTEXTO.md** quando a referência cabe em 1-2 frases. Crie `<slug>.md` separado apenas quando o material for denso (checklist, várias seções, lista longa, conteúdo que se beneficia de estrutura própria). Arquivo separado fica na raiz da pasta + linha em CONTEXTO.md apontando.

## Dois sentidos: conjunto e unidade

O termo "referências" tem dois sentidos resolvidos por contexto:

- **Conjunto (plural)** — a **pasta-referências** do escopo, onde mora o catálogo navegável. Equivalente a uma biblioteca.
- **Unidade (singular)** — cada `.md` catalogado dentro do conjunto (ex: `ana-paula.md`, `decisao-fornecedor-principal.md`). É o que `/kn-11-mantem-referencia` cria e atualiza.

Quando este conceito diz "referência" no singular, é unidade. "Pasta-referências" ou "referências do escopo" no plural é o conjunto.

## Os três eixos ortogonais (relembrando)

Detalhe em `~/.local/share/koine/conceitos/dominios.md`. A referência se posiciona nos três eixos:

- Vive **dentro de um escopo** (na pasta-referências dele).
- Declara um ou mais **domínios** no frontmatter (`dominios: [...]`) — filtros de quando carregar.
- Tem um **tipo** (`type: ...`) — categoria de natureza interna.

Um sócio próximo dentro de um escopo profissional pode ser uma referência com `type: pessoa` e `dominios: [universal, negocio]` — pessoa por natureza, universal+negocio por utilidade.

## Anatomia da pasta-referências

A pasta apontada por `pasta-referencias:` no escopo é a **raiz de um OKF** — contém os contratos universais na raiz e as referências organizadas como fizer sentido para o usuário:

```
<pasta-referencias>/
├── index.md                       # contrato OKF (directory listing)
├── log.md                         # contrato OKF (append-only de mutações)
├── kn-indice-<slug-dominio>.md    # gerado pelo kn-agente, um por domínio declarado
├── <slug>.md                      # referências na raiz
└── <subpasta>/                    # subpastas livres, organizadas pelo usuário
    └── <slug>.md
```

- `index.md` e `log.md` são **contratos OKF** — sempre presentes na raiz, mantidos pela skill `/kn-11`.
- `kn-indice-<slug-dominio>.md` são **derivados** — regenerados pelo `kn-agente` a cada invocação a partir do frontmatter das referências; nunca editados à mão. Ficam na raiz.
- `<slug>.md` são as **unidades** — uma por arquivo, identificadas por slug em kebab-case. Podem viver na raiz ou em subpastas.

Subpastas são esperadas — pasta-referências pode crescer para centenas de itens, e organizar por categoria ajuda a navegação humana. O domínio (via frontmatter) faz o filtro programático; a subpasta faz o filtro visual. São complementares, não duplicadas.

## Ficha Koine universal de uma referência

Toda referência declara no frontmatter, no mínimo:

```yaml
---
type: <Pessoa | Organizacao | Decisao | Aprendizado | Evento | ...>
title: <Nome legível>
description: <1 linha — aparece no kn-indice>
dominios: [<um ou mais slugs de domínio>]
tags: [<keywords livres>]
---
```

- **`type`** — natureza interna da referência (capitalizado, singular). Define a Ficha Koine esperada para o conteúdo.
- **`title`** — nome legível.
- **`description`** — 1 linha — extraída pelo `kn-agente` e injetada no `kn-indice-<slug-dominio>.md` correspondente.
- **`dominios`** — lista de domínios em que a referência aparece. Múltiplos é primeira-classe.
- **`tags`** — keywords adicionais para busca.

O domínio em que a referência está classificada (`<slug-dominio>.md`) pode declarar **campos recomendados** adicionais — ler o domínio antes de catalogar.

## Tipos de referência

Categorias canônicas (não exaustivas — usuário pode introduzir novos `type` conforme aparecem padrões):

- **`Pessoa`** — perfil humano relevante ao escopo (sócio, cliente, contato, parceiro).
- **`Organizacao`** — empresa, instituição, órgão (cliente, parceiro, fornecedor, regulador).
- **`Decisao`** — decisão tomada com motivação registrada (decisão estrutural, decisão tática consequente). Equivalente a ADR no domínio de software.
- **`Aprendizado`** — lição extraída de incidente, projeto, conversa — generaliza além do episódio.
- **`Evento`** — ocorrência datada com impacto registrável (lançamento, reunião pivotal, marco contratual).

`type` molda o conteúdo esperado no corpo do arquivo, não o lugar onde mora. Múltiplas pessoas, organizações e decisões coexistem no mesmo plano da pasta-referências — domínio (não `type`) faz o filtro de utilidade.

## Múltiplos domínios na mesma referência

Padrão esperado, não exceção. Referências raramente cabem em só uma lente:

- Decisão técnica com impacto comercial → `dominios: [tecnologia, negocio]`.
- Sócio que é também cônjuge → `dominios: [universal, pessoal]`.
- Stakeholder externo com expertise técnica → `dominios: [negocio, tecnologia]`.

O gerador inclui a referência no `kn-indice` de cada domínio declarado, sem duplicar conteúdo. Uma única fonte de verdade — a entrada aparece em N listas.

## `index.md` e `log.md` — contratos OKF

- **`index.md`** — directory listing legível por humano e agente. Estrutura mínima: título, descrição do escopo, lista de referências agrupadas (por `type` ou domínio principal). Atualizado pela skill `/kn-11` quando uma referência é criada ou removida.
- **`log.md`** — append-only de mutações. Cada entrada: data, ação (cria/atualiza/remove), slug afetado, motivo curto. Permite reconstruir a evolução da memória do escopo sem depender do git.

Os dois contratos são **mantidos pela skill `/kn-11`** — não escrever à mão. A automação garante consistência (slug existe no `index.md` se e somente se há `<slug>.md` na pasta).

## `kn-indice-<slug-dominio>.md` — derivados

Para cada domínio declarado no `CONTEXTO.md` da pasta de trabalho, o `kn-agente` gera um arquivo `kn-indice-<slug-dominio>.md` na pasta-referências. Estrutura:

- **`## Framework do domínio`** — sinopse extraída do `<slug-dominio>.md` correspondente.
- **`## Entradas catalogadas no escopo`** — lista `* path/relativo.md — description` em ordem alfabética por slug.

Esse arquivo é o que o CLAUDE.md gerado carrega via `@/` — não o `<slug-dominio>.md` cru, não cada referência. O agente vê título + descrição de cada referência catalogada e lê o arquivo completo apenas quando precisa.

Implicação: a `description` da Ficha Koine é o que decide se o agente vai puxar a referência ou não. Investir em descrições densas paga dividendos.

## Como catalogar uma referência nova

Operação cotidiana. Fluxo detalhado em `/kn-11-mantem-referencia`:

1. **Entrevistar** — extrair os dados essenciais do conhecimento (quem/o quê, motivação, contexto, ligações com outras referências).
2. **Decidir `type` e `dominios`** — guiada pelos `<slug-dominio>.md` (campos recomendados) e por este conceito.
3. **Materializar `<slug>.md`** — frontmatter completo + corpo na estrutura típica do `type`.
4. **Atualizar `index.md` e `log.md`** — automaticamente.
5. **(implícito) Próxima invocação do `kn-agente`** regenera o `kn-indice-<slug-dominio>.md` correspondente.

Slug em kebab-case derivado do título. Slugs colidentes recebem sufixo discriminador (`leonardo-slhessarenko.md` vs `leonardo-cunha.md`).

## Como atualizar uma referência existente

- Edição direta do `<slug>.md` é permitida (à mão ou via `/kn-11` em modo update).
- Toda mudança de conteúdo deve ser refletida em `log.md` (entrada com motivo curto).
- Renomear slug é caro — atualiza referências cruzadas em outros `.md`. Só renomear quando o slug original ficou enganoso.
- Decisões revisadas: preferir adendo no corpo + atualizar campo `vigente` (quando aplicável), sem duplicar arquivo.

## Anti-padrões

- **Diário disfarçado de referência.** Registro do que aconteceu na sessão é diário, não referência. Referência generaliza além do episódio.
- **Referência sem `description` densa.** Description fraca degrada o `kn-indice`; agente passa direto.
- **Subpasta como substituto de domínio.** Subpasta organiza visualmente; domínio filtra para o agente. Não use subpasta esperando que ela filtre o que entra no `kn-indice` — quem decide isso é o campo `dominios:` do frontmatter.
- **Mesmo conceito em dois arquivos** porque "encaixa em domínios diferentes". É **uma** referência com `dominios: [a, b]`.
- **Catalogar tudo.** Se o conhecimento não vai ser consultado em sessão futura, não vira referência. Granularidade excessiva dilui o sinal.

## Para skills relacionadas

- `/kn-11-mantem-referencia` — usa este conceito para conduzir a catalogação cotidiana.
- `/kn-01-recebe-usuario` — usa este conceito ao montar o bundle OKF inicial do primeiro escopo durante o onboarding.
- `/kn-02-mantem-catalogo` (fluxo escopo) — usa este conceito ao materializar uma pasta-referências para escopo novo (criar `index.md`, `log.md` vazios).
- `/kn-99-encerra-sessao` — pode invocar `/kn-11` quando o fechamento da sessão exigir catalogar algo que emergiu.
