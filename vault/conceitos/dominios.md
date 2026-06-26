---
type: Concept
title: Domínios
description: Doutrina meta sobre o que é domínio no Koine — função, distinção em relação a escopo e tipo de referência, anatomia do arquivo, ciclo de vida
origem: koine-canonico
dominios: [metodologia]
tags: [conceito, dominio, metodologia, runtime]
---
# Conceito: Domínios

Doutrina sobre o que é domínio no Koine, lida pelas skills `/kn-02-mantem-catalogo` (fluxo dominio) e `/kn-11-mantem-referencia` quando precisam operar sobre domínios. Não é runtime universal — só é carregada sob demanda quando a skill relevante é invocada.

## O que é domínio

**Domínio é um filtro de utilidade ao agente em sessão.** Dentro de um escopo, agrupa referências catalogadas por quando faz sentido carregá-las no contexto do agente.

Domínio existe para resolver um problema concreto: à medida que a pasta-referências de um escopo cresce, carregar todas as referências em toda sessão infla o contexto e prejudica a operação do agente. Domínio dá granularidade — o `CONTEXTO.md` da pasta de trabalho declara quais domínios são relevantes para aquela sessão; só os `kn-indice-<slug-dominio>.md` desses domínios entram no CLAUDE.md gerado.

## Os três eixos ortogonais

Para evitar confusão, três eixos cumprem funções distintas no Koine:


| Eixo                    | Função                                                                                                           | Onde vive                              |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Escopo**              | Delimita uma área de atuação ou preocupação do usuário. Cada escopo tem sua pasta-referências independente. | `~/.config/koine/escopos/<slug-escopo>.md`    |
| **Domínio**            | Filtra referências por utilidade ao agente em sessão, dentro de um escopo.                                               | `~/.config/koine/dominios/<slug-dominio>.md`    |
| **Tipo de referência** | Categoria de natureza da referência (pessoa, organização, decisão, aprendizado, evento).                       | campo`type` no frontmatter de cada referência |

São ortogonais e combinam livremente:

- Uma sessão acontece **dentro de um escopo** (definido pelo `CONTEXTO.md` da pasta).
- O `CONTEXTO.md` **declara os domínios** relevantes para aquela sessão.
- Cada referência catalogada **tem um tipo** (campo `type`) e **pertence a um ou mais domínios** (campo `dominios:`).

Exemplo: uma referência `joao-silva.md` (`type: pessoa`) na pasta-referências de um escopo qualquer, com `dominios: [universal, negocio]`, aparece tanto no `kn-indice-universal.md` quanto no `kn-indice-negocio.md` daquele escopo.

## Domínios canônicos vs do usuário

Cada domínio tem campo `origem` no frontmatter:

- `origem: koine-canonico` — domínios distribuídos pelo método. Plantados em `~/.config/koine/dominios/` pelo `kn-agente instalar`. v1 entrega 4: `universal`, `negocio`, `tecnologia`, `pessoal`.
- `origem: usuario` — domínios criados pelo próprio usuário via `/kn-02-mantem-catalogo` (fluxo dominio), quando aparece uma área de utilidade que os canônicos não cobrem. Ex: `juridico` para um executivo que faz muita revisão de contrato; `clinico` para um profissional de saúde.

Não há hierarquia entre canônico e do usuário — em runtime são tratados igual. A distinção serve a evolução do método: domínios canônicos evoluem com o `kn-agente atualizar` (Onda 2+); domínios do usuário ficam intocados.

## Anatomia de um `<slug-dominio>.md`

Cada domínio tem dois conteúdos em camadas:

**Frontmatter** (Ficha Koine):

```yaml
---
type: Domain
title: <Nome>
description: <1 linha>
origem: koine-canonico | usuario
sinopse: <1-3 frases — embutido no kn-indice em runtime>
dominios: [metodologia]
tags: [...]
---
```

**Corpo denso** (lido por skills sob demanda):

- **O que cobre** — parágrafo expandindo a sinopse
- **Quando catalogar aqui** — heurística positiva
- **Quando NÃO cabe** — heurística negativa com redirecionamento para domínios vizinhos
- **Campos recomendados** — frontmatter típico de referências no domínio (além dos OKF universais)
- **Edge cases** — referências com múltiplos domínios, casos limite
- **Exemplos** — referências comentadas

Os 4 canônicos da v1 seguem essa estrutura — usar como template ao criar domínio novo.

## Sinopse runtime vs corpo denso

Distinção crítica:

- **Sinopse** (campo do frontmatter, 1-3 frases): única coisa do `<slug-dominio>.md` que vai em runtime. O gerador `kn-agente` extrai a sinopse e embute no header de cada `kn-indice-<slug-dominio>.md`. Carrega em toda sessão que declarar esse domínio.
- **Corpo denso**: lido apenas pelas skills sob demanda. Pode ser longo sem inflar runtime.

Implicação: a sinopse precisa carregar a essência ("o que cabe, o que não cabe") em poucas frases. Corpo expande detalhes.

## Múltiplos domínios é primeira-classe

Uma referência pode declarar `dominios: [a, b]` quando for útil em mais de uma categoria de sessão. Exemplos:

- Decisão técnica com impacto comercial: `dominios: [tecnologia, negocio]`.
- Sócio que é também cônjuge: `dominios: [universal, pessoal]`.
- Stakeholder externo com expertise técnica: `dominios: [negocio, tecnologia]`.

Não é exceção — é padrão esperado. Referências raramente cabem em só uma lente. O gerador inclui a referência no `kn-indice` de cada domínio declarado, sem duplicar o conteúdo.

## Como criar um domínio novo

Operação rara — só faz sentido quando aparece área de utilidade recorrente que os canônicos não cobrem. Fluxo (detalhado em `/kn-02-mantem-catalogo` fluxo dominio):

1. Identificar o "buraco" — referências sendo classificadas em domínios que não encaixam bem.
2. Entrevistar para extrair: sinopse curta, heurística cabe/não cabe, exemplos de referências que iriam ali.
3. Materializar `~/.config/koine/dominios/<slug-dominio>.md` com `origem: usuario`.
4. Re-classificar (manualmente) as referências existentes que pertencem ao novo domínio.

Resista a criar domínio para cada nuance — granularidade excessiva fragmenta os índices e dilui o sinal. Prefira começar com canônicos e só criar novo quando a dor for repetida.

## Como manter um domínio existente

- **Atualizar sinopse** quando a heurística cabe/não cabe se refinar.
- **Atualizar campos recomendados** quando padrões emergem na catalogação.
- **Adicionar edge cases** quando aparecem situações ambíguas resolvidas.
- **Nunca renomear arbitrariamente** — domínio é referenciado em frontmatter de N referências. Renomear força migração em massa.
- **Domínios canônicos** evoluem com o método; usuário não edita diretamente. Se quiser variante, cria domínio novo com `origem: usuario`.

## Para skills relacionadas

- `/kn-02-mantem-catalogo` (fluxo dominio) — usa este conceito para conduzir criação/edição de domínio.
- `/kn-11-mantem-referencia` — usa este conceito para guiar o usuário na escolha de quais domínios declarar no `dominios:` da referência que está catalogando.
