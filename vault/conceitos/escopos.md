---
type: Concept
title: Escopos
description: Doutrina meta sobre o que é escopo no Koine — função, distinção em relação a domínio e pasta de trabalho, anatomia do arquivo, ciclo de vida
origem: koine-canonico
dominios: [metodologia]
tags: [conceito, escopo, metodologia]
---
# Conceito: Escopos

Doutrina sobre o que é escopo no Koine, lida pelas skills `/kn-01-recebe-usuario` (criação do primeiro escopo) e `/kn-02-mantem-catalogo` (fluxo escopo) quando precisam operar sobre escopos. Carregada sob demanda — não vai em runtime universal.

## O que é escopo

**Escopo é uma área de atuação ou preocupação do usuário com identidade própria.** Cada escopo tem sua **pasta-referências** independente (onde mora a memória de longa duração) e seu próprio conjunto de pastas de trabalho.

Escopo serve duas funções:

1. **Delimitar contexto.** Referências catalogadas dentro de um escopo são naturalmente carregadas em sessões dentro dele — outras áreas do usuário ficam invisíveis. Reduz inflação de contexto e protege dados sensíveis (referências do escopo cliente A não vazam pra sessão do cliente B).
2. **Organizar a vida do usuário em compartimentos legíveis.** O usuário tem uma área onde passa a maior parte do tempo (o escopo "geral") e, conforme aparecem outras áreas com diferenciação clara, cria escopos adicionais.

## Os três eixos ortogonais (relembrando)

Detalhe completo em `~/.local/share/koine/conceitos/dominios.md`. Resumo:

- **Escopo** delimita áreas de atuação do usuário.
- **Domínio** filtra referências por utilidade ao agente em sessão, dentro de um escopo.
- **Tipo de referência** classifica a natureza interna de cada referência (pessoa, organização, decisão).

Sessão acontece dentro de um escopo (definido pelo `CONTEXTO.md` da pasta de trabalho); declara domínios relevantes; agente recebe referências daquele escopo filtradas por aqueles domínios.

## Anatomia de um `<slug-escopo>.md`

Frontmatter (Ficha Koine):

```yaml
---
type: Scope
title: <Nome do escopo>
description: <1 linha>
pasta-referencias: home:<rel> | abs:<path>
escopo-pai: <slug-escopo> | null    # Onda 2+
proprietario: <nome do usuário>
dominios: [metodologia]
tags: [escopo, <slug-escopo>]
---
```

Corpo narrativo descreve a dinâmica daquele escopo — quem são os stakeholders principais, qual o papel do usuário ali, qual a história e o foco operacional. **Esse corpo é carregado em toda sessão dentro do escopo** (via `@/` no CLAUDE.md gerado), entre o arquivo do agente e os índices de domínio. Dá ao agente o pano de fundo da relação antes de ele ver as referências catalogadas.

## Pasta-referências

Cada escopo aponta para uma pasta-referências via `pasta-referencias:` (tagged path: `home:<rel>` ou `abs:<path>`). Convenção default: `home:koine/<slug-escopo>/`.

A pasta-referências contém:

- `index.md` — contrato OKF (directory listing).
- `log.md` — contrato OKF (append-only log de mutações).
- `<slug>.md` — cada referência catalogada (uma por arquivo).
- `kn-indice-<slug-dominio>.md` — índices gerados pelo `kn-agente` agrupando referências por domínio.

Detalhe em `~/.local/share/koine/conceitos/referencias.md`.

## Múltiplas pastas de trabalho por escopo

Relação **1 escopo : N pastas de trabalho**. Um escopo contém múltiplas pastas onde o usuário efetivamente trabalha — projetos, repositórios, áreas de exploração. Cada pasta de trabalho tem seu próprio `CONTEXTO.md`.

A pasta-referências do escopo é compartilhada por todas as pastas de trabalho daquele escopo. Conhecimento catalogado em qualquer sessão alimenta a memória comum.

Não há convenção rígida sobre organização das pastas de trabalho — o usuário escolhe livremente onde colocá-las no filesystem (`~/code/<projeto>`, `~/docs/<área>`, etc).

## Transição entre escopos

Sem comando explícito. O escopo da sessão é deduzido do `CONTEXTO.md` da pasta de trabalho atual (campo `escopo:`). Para transitar de escopo, o usuário faz `cd` para uma pasta de trabalho de outro escopo. Idempotente, sem estado global de "escopo ativo".

Implicação: pastas de trabalho de escopos diferentes podem coexistir lado a lado no filesystem — o que define o escopo da sessão é o `CONTEXTO.md` local, não o caminho.

## Quando criar um escopo novo

Operação rara. Critérios:

- **Empresa onde o usuário atua** (próprias ou cliente principal recorrente).
- **Cliente recorrente significativo** com história longa e dinâmica própria.
- **Projeto grande/longo** com identidade clara e horizonte de meses ou anos.
- **Área/setor compartilhado com equipe** em ambiente corporativo (TI corporativa, área comercial, projeto cross-funcional).
- **Vida pessoal** — se o usuário decide misturar pessoal e profissional no mesmo ambiente Koine.

O primeiro escopo do usuário é o "geral" (onde passa a maior parte do tempo). Escopos adicionais entram quando a diferenciação é clara — não por afinidade tópica.

## Quando NÃO criar um escopo

Anti-padrões que fragmentam a vida do usuário sem ganho real:

- **Subprojeto dentro de um cliente** — vira pasta de trabalho dentro do escopo do cliente, não escopo novo.
- **Iniciativa curta** (semanas a 1-2 meses) — vira pasta de trabalho dentro do escopo geral, não escopo próprio.
- **Departamento dentro de uma área** — área já é escopo; departamento é granular demais.
- **Tópico de interesse pessoal** — não justifica escopo se não tem trabalho recorrente.

Granularidade excessiva fragmenta a memória e duplica referências comuns. Prefira poucos escopos amplos.

## Escopo-pai (Onda 2+)

Decisão arquitetural em aberto. Tese de design: `escopo-pai: <slug-escopo>` no frontmatter permite cadeia hierárquica — referências do escopo pai são carregadas em sessões do escopo filho. Útil para casos como ficha cadastral pessoal precisada em sessão profissional (passaporte em viagem corp).

Na Onda 1, fornecimento on-demand resolve: agente pede o dado pessoal quando precisa, usuário fornece naquela sessão.

## Para skills relacionadas

- `/kn-01-recebe-usuario` — usa este conceito para conduzir a criação do primeiro escopo durante o onboarding.
- `/kn-02-mantem-catalogo` (fluxo escopo) — usa este conceito para conduzir a criação e edição de escopos adicionais.
