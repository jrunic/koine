---
type: Concept
title: Glossário
description: Doutrina do glossário no Koine — o que é, os dois alcances, como se mantém um termo e o formato do arquivo
origem: koine-canonico
dominios: [metodologia]
tags: [conceito, glossario, vocabulario, metodologia]
---

# Conceito: Glossário

Doutrina sobre o glossário no Koine, lida pelas skills que o mantêm — a
`/kn-15-mantem-glossario` (porta própria), a `/kn-13-sabatina-plano` (que afia o
vocabulário enquanto entrevista) e a `/kn-99-encerra-sessao` (que pergunta por ele
no fechamento). Carregada sob demanda — não vai em runtime universal.

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

## Como se mantém um termo

Liga quando um termo precisa ser resolvido. O gatilho é a conversa, não o disco.

**Antes da primeira pergunta**, procure um glossário e leia se existir:

- `GLOSSARIO.md` na própria pasta de trabalho.
- `GLOSSARIO.md` na pasta-referências do escopo, quando a pasta declara escopo. A pasta-referências vem de `pasta-referencias:` no arquivo do escopo, em `~/.config/koine/escopos/<slug>.md`.

Os dois podem existir ao mesmo tempo. O da pasta é o mais específico e vence em caso de divergência — mas divergência entre os dois é ela mesma um achado, e você sinaliza.

### Comportamentos

**Confrontar.** Quando o usuário usar um termo de um jeito que contradiz o glossário, sinalize no mesmo turno, antes de seguir:

> "O glossário define 'pendência' como o que já venceu e não foi pago. Você acabou de usar para o que ainda vai vencer. São a mesma coisa ou são duas?"

**Afiar.** Quando o termo for vago ou estiver carregando dois sentidos, proponha o preciso:

> "Você falou 'solicitação' duas vezes. Uma era o pedido que a área faz, a outra era o documento que vai para o jurídico. Qual dos dois fica com o nome?"

**Testar a fronteira com cenário concreto.** Quando a relação entre dois conceitos estiver sendo discutida, invente um caso específico que force a decisão:

> "Chega um pedido de renovação de um contrato que vence em 40 dias, e a área pede urgência. Isso entra na fila normal ou abre exceção? Quem decide, e o que muda no prazo?"

**Gravar na hora.** Termo resolvido é termo gravado no mesmo turno. Não acumule para o fim: o que se acumula se perde, e o glossário meio-escrito na sua cabeça não sobrevive ao fim da sessão.

### Checkpoint de alcance

Na primeira vez que um termo for resolvido, pergunte onde o glossário mora:

> "Vou gravar isso. Esse vocabulário vale só para este trabalho, ou vale para tudo que você faz neste escopo? (a) só aqui; (b) para o escopo todo."

A resposta vale para os termos seguintes da mesma sessão — não repita a pergunta a cada termo. Na dúvida, **alcance de pasta**: promover depois é trivial, e despoluir o escopo é caro.

- **Alcance de pasta** → `GLOSSARIO.md` na própria pasta de trabalho, criado sob demanda no primeiro termo.
- **Alcance de escopo** → `GLOSSARIO.md` na raiz da pasta-referências do escopo, criado sob demanda. Não é uma referência catalogada: não leva Ficha Koine e não entra em `index.md` nem nos índices de domínio.

Formato dos dois nas seções abaixo, a partir de `## Estrutura`.

**Ao criar o glossário de escopo pela primeira vez**, acrescente ao arquivo do escopo (`~/.config/koine/escopos/<slug>.md`) uma seção apontando o caminho:

```md
## Glossário

Vocabulário deste escopo em `<pasta-referencias>/GLOSSARIO.md`. Consulte quando um termo do trabalho parecer ambíguo.
```

O arquivo do escopo é carregado em toda sessão, então isso faz o glossário existir para quem não invocou a sabatina — sem que o conteúdo inteiro seja pago em todo prompt. Se a seção já existir, não duplique.

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
