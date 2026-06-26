---
type: Domain
title: Universal
description: Domínio canônico para refs sempre úteis ao agente, independente da natureza da sessão
origem: koine-canonico
sinopse: Refs sempre úteis ao agente, independente da natureza da sessão. Cabem aqui perfis-chave do escopo (sócios próximos, contatos centrais), organizações fundadoras, decisões estruturais que definem como o escopo funciona. Não cabem refs que só fazem sentido em sessões específicas (essas vão em `negocio`, `tecnologia` ou `pessoal`).
dominios: [metodologia]
tags: [dominio-canonico, universal]
---

# Domínio: Universal

## O que cobre

Refs cuja relevância atravessa qualquer sessão dentro do escopo. São os pontos cardeais do escopo — quem é central, qual a entidade que dá nome ao escopo, quais princípios fundadores guiam decisões. Carrega em toda sessão que declare este domínio em `CONTEXTO.md`.

## Quando catalogar aqui

- Perfis consultados em ≥80% das sessões do escopo (sócio próximo, cônjuge-sócio, gestor principal, parceiro central).
- Entidade-mãe (a organização que dá nome e identidade ao escopo — empregador, empresa principal, cliente que define o escopo).
- Parceiros estruturais consultados em quase qualquer decisão (banco principal, contador, advogado de confiança).
- Decisões estruturais que definem a "constituição" do escopo (modelo societário, princípios fundadores, missão).
- Vocabulário/glossário interno do escopo (termos próprios que aparecem o tempo todo).

## Quando NÃO cabe

- Refs ativadas apenas em tipos específicos de sessão → `negocio`, `tecnologia` ou `pessoal`.
- Refs episódicas (eventos pontuais, decisões táticas sem impacto duradouro).
- Refs raramente consultadas — mesmo importantes, se de baixa frequência, ficam em domínio mais específico para não inflar o índice `universal`.

## Campos recomendados (além dos OKF universais)

- `papel`: função ou relação com o escopo (ex: `sócio-fundador`, `entidade-mãe`).
- `vigente`: boolean — ainda ativo/válido (para decisões e relacionamentos que podem ter horizonte).
- `desde`: data ou período inicial (para decisões fundadoras e relacionamentos centrais).

## Edge cases

- **Ref relevante em ~90% das sessões mas não 100%**: ainda entra em `universal` (regra empírica). Abaixo de ~70%, especificar.
- **Decisão estrutural revista**: a ref permanece, atualiza-se com adendo no corpo + atualiza `vigente` se aplicável. Não duplica.
- **Mesma pessoa em dois papéis** (ex: sócio + cliente): se a relação fundadora é "sócio", entra em `universal`; o aspecto de cliente pode ser nota dentro do mesmo arquivo, sem duplicar em `negocio`.

## Exemplos

- `joao-silva.md` — sócio-fundador da empresa-mãe do escopo
- `banco-do-brasil.md` — principal parceiro bancário
- `decisao-modelo-societario.md` — decisão estrutural inicial
- `glossario.md` — vocabulário interno do escopo
