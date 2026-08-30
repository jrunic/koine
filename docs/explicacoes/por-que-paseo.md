---
descricao: Por que o Koine ganhou um caminho para orquestrador de sessões — o que muda quando o terminal deixa de ser o único lugar, e o que isso custa
id: 202608302000
tipo: explicacao
status: ativo
tags: [explicacao, koine, paseo, acesso-remoto, decisao]
---

# Por que um orquestrador de sessões

O Koine nasceu para o terminal. Você abre `kn-claude` numa pasta, e a sessão sobe com
o seu contexto. Isso resolve o problema que o produto existe para resolver — e amarra
o uso a uma cadeira.

Um **orquestrador de sessões** é um programa que sobe e administra sessões de agentes
por você: mantém uma lista, guarda o histórico, e oferece uma interface — de
computador e de celular — para entrar nelas. O Koine passou a ter um caminho para um
deles.

Este documento explica **por quê**, e o que isso custa. Se você quer o passo a passo,
o [tutorial de acesso pelo celular](../tutoriais/acesso-pelo-celular.md) é o lugar.

## O que muda

### A sessão deixa de morrer com a janela

No terminal, a sessão vive enquanto a janela vive. Fechou o notebook, acabou. Quem
trabalha em blocos interrompidos — e quase todo mundo trabalha — perde o fio a cada
interrupção, e paga de novo o custo de recontextualizar.

Com o orquestrador a sessão é um objeto: continua existindo, você sai e volta. **Essa
é a diferença que mais aparece no uso diário**, mais até do que o celular.

### O trabalho fica visível

Uma lista de sessões, cada uma na sua pasta, com o nome que você deu. No terminal
essa organização existe só na sua cabeça e na quantidade de abas abertas.

O modelo tem duas camadas — **projeto**, que agrupa, e **workspace**, que aponta para
uma pasta. É mais poder do que uma lista simples, e mais confusão: a pasta pertence
ao projeto, e quem não sabe disso cria workspace no lugar errado. Por isso o Koine
tem uma skill que resolve as duas camadas por baixo, em vez de deixar você aprender
o modelo antes de usá-lo.

### O celular vira um lugar de trabalho

Não para escrever código — para o que de fato acontece longe da mesa: pedir um
resumo, revisar uma decisão, tirar uma dúvida sobre um projeto que você conhece mas
não lembra o detalhe.

E aqui a interface física muda a natureza do uso: **ditar em português** é o que torna
o celular utilizável. Digitar num teclado de telefone uma pergunta com contexto é
trabalhoso o bastante para você desistir e deixar para depois. Falando, não é.

O Koine configura o ditado por padrão, com um modelo local — nada sai da sua máquina
para transcrever. E deixa a **fala desligada**, porque o único modelo gratuito
disponível responde em inglês; entregar metade de uma capacidade faz você tentar,
falhar e concluir que o produto é ruim. Quem quiser as duas pontas em português tem
o [caminho com serviço pago](../guias/voz-com-openai.md), que é escolha sua.

## O que não muda

**O mecanismo de contexto continua sendo o do Koine.** O orquestrador transporta a
sessão; ele não sabe nada sobre o seu perfil, o seu escopo ou a sua pasta. Um provider
apontado direto para o cliente de IA abre uma sessão genérica — que é exatamente o que
o Koine existe para evitar.

Por isso a instalação cria um wrapper por cliente, e o provider aponta para ele. A
diferença é invisível quando funciona, e é tudo quando não funciona.

## O que isso custa

Três coisas, e nenhuma é pequena:

**Uma dependência a mais.** O orquestrador é produto de terceiro, com ciclo próprio.
O contrato que o Koine usa — como o comando é invocado, como o ambiente chega — não é
API documentada: foi medido. Versão nova pode mudá-lo, e quem quebra é o Koine.

**Nem todo cliente atravessa.** Dois dos cinco que o Koine suporta não têm caminho
por aqui, pelo jeito como sobem. Não é configuração faltando, e não há o que ajustar.
Quem usa um deles continua no terminal — que segue funcionando igual, e não é um
prêmio de consolação: é o caminho principal.

**Configurar errado falha em silêncio.** É o custo que mais dói. Um provider apontado
para um cliente sem caminho fica com cara de saudável, abre sessão e responde — sem o
seu contexto. Nada avisa. Foi por isso que a configuração virou uma conversa guiada
em vez de um trecho de documentação para copiar: a chance de errar em silêncio é alta
demais para confiar em quem está lendo às pressas.

## Por que uma skill, e não um comando

Configurar isso é decisão, não execução. Quais clientes você vai usar de fato, se a
política da sua empresa permite alcançar seu computador pela internet, como você quer
agrupar as suas pastas — são perguntas com resposta diferente para cada pessoa.

Um comando teria que assumir tudo isso. Uma conversa pergunta, explica o que está em
jogo e faz o trabalho mecânico depois — que é a mesma razão pela qual o onboarding do
Koine é uma conversa e não um `koine init`.

## Continua lendo

- [Tutorial — acesso pelo celular](../tutoriais/acesso-pelo-celular.md): do zero até
  a primeira sessão no aparelho.
- [Guia — acesso remoto](../guias/acesso-remoto.md): o que a skill não pode fazer por
  você, e os casos de máquina compartilhada e troca de computador.
- [Referência — o que o Koine escreve](../referencias/paseo.md): a configuração
  exata, campo a campo.
