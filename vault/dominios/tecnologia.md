---
type: Domain
title: Tecnologia
description: Domínio canônico para refs úteis em sessões sobre código, sistemas e arquitetura técnica
origem: koine-canonico
sinopse: Refs úteis em sessões sobre código, sistemas e arquitetura técnica. Cabem aqui decisões técnicas, padrões de implementação, libs e stacks escolhidos, parceiros técnicos, problemas resolvidos. Não cabem decisões de negócio sobre o produto (vão em `negocio`) ou perfis não-técnicos sem relação com sistema (vão em `negocio` ou `pessoal`).
dominios: [metodologia]
tags: [dominio-canonico, tecnologia]
---

# Domínio: Tecnologia

## O que cobre

Refs ativadas em sessões sobre como as coisas são construídas e operam tecnicamente — código, arquitetura, infraestrutura, padrões de implementação, dependências técnicas. O mundo da execução técnica do escopo.

## Quando catalogar aqui

- Decisões técnicas (escolha de stack, padrões arquiteturais, ADRs do produto, trade-offs documentados).
- Padrões de implementação repetidos no escopo (convenções de código, organização de pastas, formatos de log).
- Bibliotecas, frameworks e ferramentas escolhidos, com motivo da escolha.
- Parceiros técnicos (devs externos, agências de desenvolvimento, vendors de SaaS técnico).
- Problemas resolvidos com técnica documentada (memória institucional de troubleshooting).
- Infraestrutura: servidores, ambientes, dependências externas relevantes.

## Quando NÃO cabe

- Decisões sobre o produto enquanto negócio (precificação, posicionamento) → `negocio`.
- Stakeholders sem relação técnica → `negocio`.
- Documentos pessoais ou de vida fora do escopo técnico → `pessoal`.

## Campos recomendados (além dos OKF universais)

- `categoria-tecnica`: `stack`, `ferramenta`, `arquitetura`, `infra`, `padrao`, `troubleshooting`.
- `vigente`: boolean — ainda em uso? (libs descontinuadas mantém ref histórica com `vigente: false`).
- `versao` ou `data-decisao`: para decisões com horizonte temporal.
- `substituido-por`: slug de ref nova que substitui esta (quando aplicável).

## Edge cases

- **Padrão usado em vários sistemas**: ref única em `tecnologia`; outros docs referenciam por slug.
- **Refatoração arquitetural**: nova ref de decisão; antiga atualiza `vigente: false` e `substituido-por`. Não apaga — memória histórica é valiosa.
- **Decisão técnica com componente comercial** (ex: escolher SaaS pago por custo): `dominios: [tecnologia, negocio]`.
- **Bug raro mas com solução documentada**: cabe — `tecnologia` é também memória de troubleshooting.

## Exemplos

- `decisao-stack-go.md` — escolha de linguagem do produto
- `padrao-handler-http.md` — padrão de implementação documentado
- `lib-x-substituiu-y.md` — decisão de troca de dependência
- `infra-aws-regiao-saopaulo.md` — escolha de infra com motivo
