---
type: Domain
title: Pessoal
description: Domínio canônico para refs úteis em sessões sobre vida pessoal — opcional, útil em escopos multi-vida ou cross-escopo
origem: koine-canonico
sinopse: Refs úteis em sessões sobre vida pessoal — opcional, mais comum em escopos multi-vida (usuário que mistura trabalho e pessoal num mesmo ambiente). Cabem aqui família, saúde individual, documentos civis (passaporte, CNH), finanças pessoais separadas de negócio. Útil principalmente cross-escopo - declarar `pessoal` em sessão profissional quando precisa puxar dados pessoais (ex - viagem corp precisando passaporte).
dominios: [metodologia]
tags: [dominio-canonico, pessoal]
---

# Domínio: Pessoal

## O que cobre

Refs sobre a vida pessoal do usuário — família próxima, saúde individual, documentos civis, finanças e ativos pessoais separados de negócio. Domínio opcional: usuários corporativos puros (que separam pessoal e profissional em ambientes Koine distintos) podem não precisar dele na v1.

Utilidade principal: **cross-escopo**. Quando uma sessão profissional precisa de dado pessoal (ex: planejamento de viagem corp precisando dados de passaporte), o `CONTEXTO.md` daquela pasta declara `dominios: [universal, negocio, pessoal]` e o agente recebe os dados pessoais necessários.

## Quando catalogar aqui

- Família próxima: cônjuge, filhos, pais.
- Saúde individual: médicos, planos de saúde, medicamentos contínuos, condições relevantes.
- Documentos civis: passaporte, CNH, RG, CPF, certidões.
- Finanças pessoais: contas, investimentos pessoais separados de PJ, dependentes para IR.
- Imóveis pessoais (residência, casa de família).
- Compromissos pessoais recorrentes (ritual familiar, consulta médica anual).

## Quando NÃO cabe

- Sócios/parceiros profissionais que também são amigos → privilegiar a relação principal: `negocio` ou `universal`.
- Dados pessoais de outros (não-usuário) que aparecem em contexto profissional → `negocio`.
- Refs sobre lazer puro (filmes, livros consumidos) — Koine não é nota-pessoal-genérica; só catalogar se houver utilidade recorrente em sessões.

## Campos recomendados (além dos OKF universais)

- `relacao`: relação com o usuário (`cônjuge`, `filho`, `pai`, `mãe`, `médico`, `documento`).
- `data-relevante`: aniversário, validade de documento, próximo vencimento.
- `sensivel`: boolean — `true` para CPF, RG, dados bancários, dados clínicos. Sinaliza ao agente que não deve transcrever em logs ou compartilhar fora da sessão.

## Edge cases

- **Membro da família que também é sócio** (ex: esposa-sócia): `dominios: [pessoal, universal]` — relação familiar é também relação fundadora do escopo.
- **Médico-amigo**: privilegiar relação principal (provavelmente médico → `pessoal`; se for sócio que virou médico ocasional, manter em `negocio`/`universal`).
- **Documento pessoal usado em contexto corp** (ex: passaporte em viagem corp): permanece em `pessoal`; o escopo profissional declara `pessoal` no `CONTEXTO.md` quando precisa.
- **Ref com campo `sensivel: true`**: agente respeita restrição — usa o dado dentro da sessão mas não enumera/transcreve fora dela.

## Exemplos

- `maria-silva.md` — cônjuge
- `medico-cardiologista.md` — médico do plano de saúde
- `passaporte.md` — documento civil (sensível)
- `plano-saude-familia.md` — plano coletivo familiar
