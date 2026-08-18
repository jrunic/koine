---
type: Reference
title: Formato de GLOSSARIO.md
description: Estrutura e regras do GLOSSARIO.md escrito pela sabatina — vocabulário de trabalho com definições enxutas, sinônimos a evitar, relações e ambiguidades resolvidas
dominios: [metodologia]
tags: [glossario, sabatina, kn-13, formato, vocabulario]
---

# Formato de `GLOSSARIO.md`

Vocabulário de um trabalho: os termos que as pessoas envolvidas usam, com um sentido só cada.

Existe para acabar com a conversa em que duas pessoas dizem a mesma palavra e querem dizer coisas diferentes — e para que a terceira, que chegou depois, não precise descobrir isso do zero.

Não é o `CONTEXTO.md`. O `CONTEXTO.md` diz o que é esta pasta de trabalho e como operar nela; o glossário diz o que as palavras significam. Audiências e ritmos diferentes: o contexto muda quando o trabalho muda, o glossário muda quando um termo é resolvido.

---

## Estrutura

```md
# Contratações

Como a área de compras recebe, prioriza e formaliza pedidos de contratação.

## Vocabulário

**Solicitação**:
Pedido de contratação enviado por uma área, antes de qualquer análise.
_Evitar_: requisição, demanda, chamado.

**Processo**:
Uma solicitação aceita, com número próprio, em análise ou em andamento.
_Evitar_: caso, pasta, contratação.

**Contrato**:
Documento assinado que encerra um processo. Um processo pode terminar sem contrato.
_Evitar_: instrumento, termo.

**Renovação**:
Processo cujo objeto é estender um contrato existente, sem nova disputa.
_Evitar_: prorrogação, aditivo — aditivo é outra coisa e muda valor.

## Relações

- Uma **Solicitação** vira no máximo um **Processo**.
- Um **Processo** termina com um **Contrato** ou com arquivamento.
- Uma **Renovação** é um **Processo** que nasce apontando para um **Contrato** existente.

## Diálogo de exemplo

> **Agente:** "Quando a área manda a solicitação, o processo já nasce?"
>
> **Dona do processo:** "Não. Só depois que compras confere se tem orçamento. Antes disso é solicitação, e ela pode morrer aí mesmo."

## Ambiguidades resolvidas

- "pendência" era usada tanto para o que já venceu quanto para o que ainda vai vencer — resolvido: pendência é só o vencido; o que ainda vai vencer é **previsto**.
```

---

## Regras

- **Seja opinativo.** Quando três palavras disputam o mesmo conceito, escolha uma e liste as outras como sinônimos a evitar. Glossário que aceita tudo não resolve nada.
- **Uma frase por definição.** Diga o que a coisa **é**, não o que ela faz. Se não couber em uma frase, provavelmente são dois termos.
- **Registre a ambiguidade, não só a resolução.** A seção de ambiguidades resolvidas é o que impede a discussão de recomeçar — ela guarda que houve confusão, e como foi decidida.
- **Mostre as relações.** Termos em negrito e cardinalidade quando ela for óbvia. É onde as contradições aparecem.
- **Escreva o diálogo.** Uma troca curta e real entre quem pergunta e quem sabe. Demonstra a fronteira entre dois conceitos melhor que qualquer definição.
- **Só o que é próprio deste trabalho.** Palavra que significa a mesma coisa em qualquer lugar não entra, mesmo que apareça o tempo todo. O glossário guarda o que é específico.
- **Agrupe sob subtítulos** quando agrupamentos naturais aparecerem. Se todos os termos pertencem à mesma área, lista plana basta.

---

## Onde mora

Dois lugares, conforme o alcance decidido na sabatina:

- **Alcance de pasta** — `GLOSSARIO.md` na própria pasta de trabalho. Vale para este trabalho.
- **Alcance de escopo** — `GLOSSARIO.md` na raiz da pasta-referências do escopo, apontado por uma seção no arquivo do escopo. Vale para tudo que o usuário faz naquele escopo.

Os dois podem coexistir. O da pasta é o mais específico e vence em caso de divergência — mas a divergência em si merece ser sinalizada ao usuário.

Criar sob demanda: só quando o primeiro termo for resolvido. Glossário vazio criado por precaução não é lido por ninguém.

---

## Atribuição

Adaptado de `mattpocock/skills/skills/engineering/grill-with-docs/CONTEXT-FORMAT.md` (commit `5fed805`).

Copyright 2026 Matt Pocock — Licença MIT.
