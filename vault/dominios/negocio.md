---
type: Domain
title: Negócio
description: Domínio canônico para refs úteis em sessões sobre processos, projetos e decisões de negócio
origem: koine-canonico
sinopse: Refs úteis em sessões sobre processos, projetos e decisões de negócio. Cabem aqui stakeholders externos, parceiros, decisões financeiras, contratos, processos operacionais, métricas de negócio. Não cabem detalhes técnicos de código/sistemas (vão em `tecnologia`) ou vida pessoal (vai em `pessoal`).
dominios: [metodologia]
tags: [dominio-canonico, negocio]
---

# Domínio: Negócio

## O que cobre

Refs ativadas em sessões sobre como o escopo gera valor e se sustenta — comercial, financeiro, operacional, contratual. O mundo das relações de mercado, processos repetíveis, decisões econômicas e métricas que governam o negócio.

## Quando catalogar aqui

- Stakeholders externos: clientes, fornecedores, parceiros comerciais, investidores.
- Decisões financeiras: investimentos, modelo de precificação, mudanças de fluxo de caixa.
- Contratos e acordos vigentes ou referenciais.
- Processos operacionais documentados (vendas, atendimento, fechamento contábil).
- Métricas-chave do negócio (KPIs, indicadores acompanhados em ciclo regular).
- Projetos com escopo temporal definido (lançamentos, campanhas, transições).

## Quando NÃO cabe

- Decisões técnicas de implementação → `tecnologia`.
- Perfis exclusivamente pessoais (família, médicos, amigos sem vínculo profissional) → `pessoal`.
- Refs estruturais consultadas em qualquer sessão (sócio fundador, missão) → `universal`.

## Campos recomendados (além dos OKF universais)

- `relacao`: tipo de vínculo (`cliente`, `fornecedor`, `parceiro`, `investidor`, `concorrente`).
- `status`: `ativo`, `pausado`, `encerrado`, `prospect`.
- `desde`: começo do relacionamento ou vigência.
- `valor` ou `volume`: ordem de grandeza financeira (quando aplicável).

## Edge cases

- **Decisão técnica com impacto comercial** (ex: "usar AWS por custo"): `dominios: [negocio, tecnologia]`.
- **Stakeholder também técnico** (ex: CTO parceiro): `dominios: [negocio, tecnologia]`.
- **Cliente que vira sócio**: muda papel — mover para `universal` se a relação ficou estruturante; senão atualizar `relacao` e seguir em `negocio`.
- **Projeto interno (não negócio direto)** mas operacional: cabe em `negocio` se for processo/iniciativa repetível ou com impacto econômico mensurável.

## Exemplos

- `cliente-acme-corp.md` — cliente principal do escopo
- `contrato-fornecedor-logistica.md` — contrato vigente
- `decisao-precificacao-2026.md` — decisão financeira do ciclo
- `processo-fechamento-contabil.md` — processo operacional repetível
