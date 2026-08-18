---
descricao: Guia da /kn-13 — como preparar e conduzir uma sabatina para extrair um processo que só existe na cabeça de quem executa, e o que sai dela
id: 202608181900
tipo: guia
status: ativo
tags: [guia, kn-13, sabatina, entrevista, glossario, decisao, processo]
---

# Guia — Sabatinar um processo

Audiência: quem precisa entender como algo funciona de verdade antes de decidir o que fazer com aquilo. Vale para um plano técnico, mas vale igualmente para um processo que nunca foi escrito — a rotina de contratações, o fechamento do mês, o fluxo de aprovação que cada um executa de um jeito.

A sabatina é uma entrevista conduzida pelo agente. Você responde; ele pergunta uma coisa por vez, sempre com a recomendação dele junto, e confere o que você afirma contra um documento real.

## O que a torna diferente de uma conversa

Três coisas, e vale saber quais são antes de começar:

**Ele discorda.** Cada pergunta vem com o que o agente faria e por quê. Você concorda, recusa, ou traz o que ele não sabia — os três avançam. É de propósito: pergunta neutra devolve todo o trabalho para você.

**Ele confere.** Você declara na abertura contra o que ele vai checar o que você disser. Quando a sua descrição e o documento divergem, ele mostra a divergência. É esse o produto da sessão — quase sempre o processo real difere do processo que a gente descreve de memória.

**Ele grava enquanto conversa.** Termo resolvido entra no glossário no mesmo turno. Decisão que passa em três critérios vira registro com as alternativas recusadas. Nada fica para o fim.

## Antes de começar — escolher a fonte de evidência

É a única preparação que a sabatina exige, e é a que decide se a sessão vale.

A fonte é o artefato mais próximo do real que existir:

| Se o trabalho é | A fonte costuma ser |
|---|---|
| Um processo administrativo | a planilha de controle, ou o export do sistema |
| Uma rotina financeira | o extrato, o relatório do ERP, a conciliação do mês |
| Um fluxo contratual | os contratos assinados, ou o registro de tramitação |
| Uma operação com norma escrita | o procedimento vigente, ainda que desatualizado |
| Software | o código |

**Não existe nada escrito?** Isso é um achado, e a sabatina segue: ela vira a primeira formalização, e o agente confere a consistência do que você mesmo disse antes contra o que diz depois.

**A fonte está desatualizada?** Melhor ainda — a distância entre o documento e a prática é exatamente o que a sessão precisa encontrar.

Se a pasta trabalha sempre contra a mesma fonte, declare no `CONTEXTO.md` dela e a sabatina para de perguntar. Formato em [`CONTEXTO.md`](../referencias/contexto-md.md#fonte-de-evidência--convenção-da-kn-13).

## Como rodar

```
/kn-13-sabatina-plano
```

Não precisa de pasta configurada. A entrevista roda em qualquer lugar, inclusive numa pasta que você acabou de abrir — o que o estado da pasta muda é só onde o resultado é gravado.

A sessão abre perguntando a fonte de evidência, lê a fonte, e começa.

## A decisão que ela vai te pedir: alcance

Na primeira vez que um termo for resolvido, o agente pergunta:

> "Esse vocabulário vale só para este trabalho, ou vale para tudo que você faz neste escopo?"

É a única decisão estrutural da sessão, e a resposta vale para o resto dela.

| Alcance | Onde o glossário fica | Quando escolher |
|---|---|---|
| **Pasta** | `GLOSSARIO.md` na pasta de trabalho | O vocabulário é deste projeto. É o default seguro. |
| **Escopo** | `GLOSSARIO.md` na pasta-referências, apontado por uma seção no arquivo do escopo | O vocabulário é do cliente, da empresa, da área — outras pastas vão precisar dele. |

Na dúvida, escolha pasta. Promover depois é copiar um arquivo; despoluir um escopo cheio de termo que só servia a um projeto é bem pior.

Para decisões a pergunta se repete caso a caso, porque decisões são raras — no alcance de escopo elas viram referência catalogada `type: Decisao`, entrando no `index.md` e no `log.md` como qualquer outra.

## O que sai da sessão

- **Um glossário** com os termos que estavam ambíguos, cada um com uma definição de uma frase, os sinônimos a evitar e as ambiguidades que foram resolvidas no caminho.
- **As divergências encontradas** entre o que você descreveu e o que a fonte mostra.
- **Zero ou uma decisão registrada.** Zero é resultado normal e frequente: o registro só é oferecido quando a decisão é difícil de reverter, surpreendente para quem chegar depois, e resultado de uma alternativa real recusada por um motivo. Faltando um dos três, o agente não oferece.
- **Os riscos enumerados** e o que ficou em aberto.

A sabatina não escreve o diário da sessão. Isso é `/kn-99-encerra-sessao`, que continua sendo o fechamento.

## Quando não usar

- **Para catalogar o que você já entendeu** — isso é `/kn-11-mantem-referencia`. A sabatina é para descobrir, não para arquivar.
- **Para produzir texto.** Ela não escreve o procedimento por você; ela extrai o que precisa estar nele.
- **Quando você já decidiu e quer validação.** A sessão vai encontrar contradições, e isso só é útil para quem quer encontrá-las.

## Problemas comuns

| Sintoma | O que está acontecendo |
|---|---|
| A sessão parece uma entrevista simpática, nada foi contestado | Nenhuma fonte de evidência foi declarada, ou o agente não a leu. Diga qual é o arquivo e peça para ele conferir. |
| O agente oferece registrar decisão o tempo todo | Ele está registrando conclusão em vez de decisão. Lembre-o dos três critérios; o esperado é no máximo uma por sessão. |
| Os termos não estão sendo gravados | A gravação é no mesmo turno em que o termo é resolvido. Se acumulou, peça para gravar antes de seguir. |
| Você quer registrar no escopo mas o agente só grava na pasta | A pasta não declara escopo, ou o escopo não tem `pasta-referencias:` válida. Regularize com `/kn-02-mantem-catalogo`. |

## Referências

- [Habilidades](../referencias/habilidades.md#kn-13-sabatina-plano) — o que a skill é, inputs e outputs
- [`CONTEXTO.md`](../referencias/contexto-md.md) — onde declarar a fonte de evidência da pasta
- [Modelo de referências](../explicacoes/modelo-referencias.md) — por que o registro de escopo aparece em sessões futuras
