---
name: kn-15-mantem-glossario
description: Cria ou atualiza o glossário do seu trabalho — os termos que vocês usam, cada um com um sentido só. Conversa curta que afia o vocabulário e grava na hora, sem a entrevista completa da sabatina. Use quando a mesma coisa estiver sendo chamada de dois jeitos, ou para registrar um termo que acabou de ser resolvido.
id: 202609111900
projeto: koine
tipo: habilidade
status: ativo
tags: [habilidade, koine, glossario, vocabulario, cotidiano]
---

# kn-15 — Mantém o glossário

Atravessa o vocabulário de um trabalho e grava: cada termo com um sentido só, os
sinônimos que ficam de fora, e as fronteiras entre conceitos que se confundem.

É a porta curta. Quando o que se precisa é **entender um processo** antes de
decidir, a skill é a `/kn-13-sabatina-plano` — ela afia o vocabulário no caminho,
pelo mesmo comportamento, e vai muito além dele.

## Quando roda

- Um termo acabou de ser resolvido na conversa ("não é balcão, é recepção") e
  precisa ficar gravado.
- A mesma coisa está sendo chamada de dois jeitos entre sessões.
- O usuário quer sentar e fazer o glossário de um escopo do zero.
- Invocada pela `/kn-99-encerra-sessao` quando o vocabulário oscilou na sessão.

## Pré-condições

Nenhuma dura. Roda em qualquer pasta.

O estado da pasta muda só **onde** o resultado é gravado — e isso é decidido pelo
alcance, não pelo estado: pasta que declara escopo real pode gravar nos dois
lugares; pasta sem escopo grava nela mesma.

## Conceitos referenciados

Carregue **antes** de gravar qualquer coisa:

- `~/.local/share/koine/conceitos/glossario.md` — o comportamento (confrontar,
  afiar, testar a fronteira, checkpoint de alcance, gravar na hora) e o formato do
  arquivo. É o mesmo que a sabatina usa.
- `~/.local/share/koine/conceitos/dominios.md` — necessário para o frontmatter
  quando o alcance for de escopo.

## Abertura

**Procure o glossário antes da primeira pergunta**, nos dois lugares que o
conceito define, e diga o que achou:

> "Achei o glossário deste escopo, com 14 termos. Vou trabalhar em cima dele."

> "Não achei glossário nem na pasta nem no escopo. Vamos começar um."

**Não peça fonte de evidência.** Isso é da sabatina: aqui o assunto é como as
pessoas chamam as coisas, e quem sabe é o usuário.

## Condução

Uma pergunta por vez, com a sua recomendação junto — as duas regras da entrevista
que valem aqui. O resto do comportamento está no conceito; siga-o.

**Partindo de um termo já resolvido** (o caso da `/kn-99`): confirme o sentido em
uma pergunta, pergunte o alcance, grave. Não transforme em entrevista.

**Partindo do zero**: peça ao usuário três a cinco termos que ele usa todo dia no
trabalho daquela pasta, e atravesse um por um. Pare quando os termos que restam
forem óbvios para qualquer pessoa de fora — glossário não é dicionário.

## Gravação

Formato, alcance e onde mora: tudo no conceito. Duas regras que não podem falhar:

- **Acréscimo, nunca reescrita.** Grave o termo novo sem reescrever o arquivo. Ao
  tocar o `CONTEXTO.md` da pasta, o bloco `---` do topo é a Ficha Koine — sem
  `escopo:` a pasta para de abrir sessão.
- **Nada é gravado sem o usuário ver.** Mostre o que vai entrar, e grave depois do
  aceite. Se ele recusar, não insista e não grave nada.

## O que NÃO faz

- **Não entrevista processo.** Isso é `/kn-13-sabatina-plano`.
- **Não cataloga conhecimento formado.** Isso é `/kn-11-mantem-referencia`.
- **Não fecha a sessão.** Isso é `/kn-99-encerra-sessao`.
- **Não inventa termo que o usuário não usa.** Glossário é o vocabulário dele.
