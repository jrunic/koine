---
name: kn-13-sabatina-plano
description: Conduz uma sabatina — entrevista socrática que submete um plano, um processo ou uma ideia a teste rigoroso, uma pergunta por vez e sempre com a recomendação do agente junto. Afia o vocabulário no GLOSSARIO.md enquanto a conversa acontece e registra como referência a decisão que passa nos três critérios. Confere o que o usuário afirma contra a evidência real declarada na abertura — planilha, relatório, procedimento, contrato ou código. Use quando for preciso entender como algo funciona de verdade antes de decidir o que fazer.
id: 202608181800
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-13, sabatina, entrevista, glossario, decisao, dominio]
---

# kn-13-sabatina-plano

Entrevista socrática rigorosa. O usuário chega com um plano, um processo, uma ideia ou uma dúvida; a skill entrevista até a coisa ficar explícita, afia o vocabulário no caminho e registra o que cristaliza.

Serve tanto para software quanto para trabalho que não tem código nenhum — um processo de compras que só existe na cabeça de quem executa, uma rotina de fechamento que mora numa planilha, um contrato cujo fluxo ninguém escreveu. O que muda entre um caso e outro não é o método: é **contra o que** o agente confere o que o usuário afirma.

Invoque quando for preciso entender antes de decidir. Não use para produzir texto, catalogar conhecimento já formado (isso é `/kn-11-mantem-referencia`) ou fechar a sessão (`/kn-99-encerra-sessao`).

---

## Pré-condições

Nenhuma dura. A entrevista roda em qualquer pasta, inclusive numa que acabou de ser aberta e ainda não foi configurada.

O que o estado da pasta muda é só **onde** o resultado é gravado:

- Pasta com `CONTEXTO.md` declarando um escopo real → o registro pode ir para a pasta **ou** para o escopo, conforme o alcance que o usuário escolher.
- Pasta sem escopo, ou com `CONTEXTO.md` de bootstrap → o registro fica na própria pasta. Não interrompa a sabatina para configurar a pasta; se o usuário quiser regularizar, o caminho é `/kn-02-mantem-catalogo`, e ele decide se faz isso antes ou depois.

---

## Conceitos referenciados

Carregue **antes** de gravar qualquer coisa — não são necessários para conduzir a entrevista:

- `~/.local/share/koine/conceitos/referencias.md` — alcance de escopo vs. alcance de pasta, tipos canônicos, Ficha Koine, contratos `index.md` e `log.md`.
- `~/.local/share/koine/conceitos/dominios.md` — necessário para classificar `dominios:` quando uma decisão for registrada com alcance de escopo.
- `~/.local/share/koine/conceitos/glossario.md` — comportamento e formato do glossário; necessário antes de gravar o primeiro termo.

---

## Abertura — a fonte da evidência

Antes da primeira pergunta da entrevista, estabeleça contra o que você vai conferir o que o usuário afirmar. Sem isso a sabatina vira conversa agradável: o usuário descreve o processo como ele acha que é, você concorda, e ninguém descobre nada.

**Se o `CONTEXTO.md` da pasta já declara a fonte**, não pergunte de novo — confirme em uma linha:

> "Vou conferir o que você disser contra a planilha de contratações que está declarada nesta pasta. Continua valendo?"

**Se não declara**, pergunte:

> "Antes de começar: contra o que eu confiro o que você me contar? Pode ser a planilha que você usa hoje, um relatório do sistema, o procedimento escrito, um contrato, o código — o que existir de mais próximo do real."

Aceite qualquer resposta sem tratar nenhuma como caso especial. Se o usuário disser que não existe nada escrito, isso **é** um achado — registre e siga; a sabatina passa a ser a primeira formalização, e o agente confere contra a consistência interna do que o próprio usuário disse antes.

Leia a fonte antes de começar a perguntar, não durante.

---

## Camada 1 — a entrevista

Quatro regras. Valem sempre, independentemente do estado da pasta.

1. **Percorra a árvore de decisões resolvendo dependências uma por uma.** Quando uma resposta abrir três novas questões, resolva a que as outras dependem primeiro. Diga em voz alta qual você está atacando e por quê.
2. **Uma pergunta por vez.** Faça a pergunta e aguarde. Duas perguntas no mesmo turno fazem o usuário responder a mais fácil e ignorar a difícil.
3. **Toda pergunta vem com a sua recomendação.** Isto não é questionário neutro. Pergunte e diga o que você faria, com o motivo. O usuário concorda, discorda ou traz o que você não sabia — os três avançam a conversa; a pergunta pelada não avança nenhum.
4. **Se dá para descobrir, descubra — não pergunte.** O que estiver na fonte de evidência, nos arquivos da pasta ou nas referências do escopo você lê. Perguntar o que está ao seu alcance gasta o usuário no que ele não precisava gastar.

**Cruzar com a evidência.** Quando o usuário afirmar como algo funciona, confira contra a fonte declarada na abertura e exponha a contradição:

> "Você disse que toda contratação acima de um certo valor passa pelo comitê. Na planilha, das últimas doze acima desse valor, quatro não têm registro de comitê. O que acontece nesses casos?"

Este é o comportamento que dá dente à sabatina. Se você não estiver conferindo nada, a sessão não está sabatinando — está anotando.

Este é o comportamento que dá dente à sabatina. Se você não estiver conferindo nada, a sessão não está sabatinando — está anotando.

**Critério de encerramento.** A sabatina termina quando as quatro coisas valem: toda decisão da árvore tem resposta, cada recomendação sua foi validada ou recusada explicitamente, as dependências entre decisões estão resolvidas e os riscos estão enumerados. Se o usuário quiser encerrar antes, diga qual dos quatro ainda falta — e encerre se ele mantiver.

---

## Camada 2 — o glossário

Liga quando um termo precisa ser resolvido. O gatilho é a conversa, não o disco.

Como se mantém um termo — confrontar, afiar, testar a fronteira, perguntar o
alcance, gravar na hora — está em `~/.local/share/koine/conceitos/glossario.md`,
junto com o formato do arquivo. **Carregue o conceito antes de gravar o primeiro
termo.** A sabatina não tem regra própria de glossário: usa a mesma que a
`/kn-15-mantem-glossario` usa, para que o vocabulário não dependa de por qual
porta o usuário entrou.

O que é da sabatina e não do glossário está na Camada 1: **cruzar com a
evidência** declarada na abertura.

---

## Camada 3 — a decisão

Liga quando uma decisão cristaliza durante a sabatina e passa nos três critérios. É rara por construção.

### Os três critérios

Ofereça registro **somente quando os três valem ao mesmo tempo**:

1. **Difícil de reverter** — mudar de ideia depois custa caro.
2. **Surpreendente sem contexto** — quem chegar depois vai olhar e pensar "por que fizeram assim?".
3. **Resultado de um compromisso real** — havia alternativa de verdade, e ela foi recusada por um motivo específico.

Faltou um, não ofereça. Decisão fácil de reverter você reverte; decisão óbvia ninguém questiona; decisão sem alternativa não tem nada a registrar além do que já é evidente.

**Autopolicia:** se você está oferecendo registro mais de uma vez na mesma sessão, releia os três critérios. Provavelmente está registrando conclusão, não decisão.

### Checkpoint de alcance — por decisão

Decisões são raras, então aqui a pergunta é caso a caso:

> "Isso passa nos três critérios e vale registrar. Serve só para este trabalho, ou vale para tudo neste escopo?"

- **Alcance de escopo** → a decisão vira referência com `type: Decisao` na pasta-referências, pela mecânica de `/kn-11-mantem-referencia`: arquivo `<slug>.md` com Ficha Koine completa, `index.md` atualizado e entrada nova em `log.md`. Siga aquela skill para materializar — não escreva o arquivo por fora.
- **Alcance de pasta** → a decisão fica na própria pasta de trabalho. Cabendo em uma ou duas frases, é uma linha em `CONTEXTO.md`; sendo densa, é um `<slug>.md` na raiz da pasta com a linha em `CONTEXTO.md` apontando. Acrescente a linha sem reescrever o arquivo: o bloco `---` do topo é a Ficha Koine, e sem `escopo:` a pasta para de abrir sessão.

### O que o registro contém

Independente do alcance, quatro coisas — e a segunda e a terceira são as que fazem o registro valer:

- **Contexto** — qual era o estado do mundo quando a decisão foi tomada. Uma a três frases, escritas para quem vai ler daqui a um ano.
- **Decisão** — o que ficou decidido. Direto.
- **Alternativas recusadas** — cada uma com o motivo concreto da recusa. Sem isso, alguém propõe a mesma coisa em seis meses e a discussão recomeça do zero.
- **Consequências** — o que passa a ser verdade, e o que ficou pior em troca do que ficou melhor.

Um registro de um parágrafo é um registro válido. O valor está em existir e em dizer por quê, não em preencher seções.

---

## Fechamento

Ao encerrar, faça três coisas:

1. **Recapitule** o que foi resolvido, o que ficou em aberto e os riscos enumerados.
2. **Ofereça registrar a fonte de evidência** no `CONTEXTO.md` da pasta, se ela ainda não estiver lá — assim a próxima sabatina naquela pasta não repete a pergunta de abertura.
3. **Avise se algo foi gravado no escopo.** Referência nova só aparece nos índices depois que eles são regerados — pelo `/kn-12-prepara-contexto` ou na próxima vez que a sessão for aberta pelo wrapper.

A sabatina não escreve diário. Isso é `/kn-99-encerra-sessao`.

---

## Anti-padrões

- **Questionário neutro.** Pergunta sem recomendação junto transfere todo o trabalho para o usuário e não testa nada.
- **Perguntar o que está no arquivo.** Se a resposta está na fonte de evidência ou na pasta, ler é obrigação sua.
- **Acumular para o fim.** Termo resolvido e não gravado é termo perdido.
- **Registrar decisão por educação.** Oferecer registro toda hora esvazia o registro. Os três critérios existem para isso.
- **Confundir sabatina com anotação.** Se nenhuma afirmação do usuário foi conferida contra nada, a sessão não sabatinou.
- **Concordar para agradar.** Contradição achada é o produto da sabatina, não um acidente constrangedor.
- **Interromper a entrevista para configurar a pasta.** A camada 1 roda em qualquer lugar; a configuração é assunto de outra skill e o usuário escolhe a hora.

---

## Crédito

Adaptado de `mattpocock/skills/skills/engineering/grill-with-docs` (commit `5fed805`), incluindo a adaptação do formato de glossário.

Copyright 2026 Matt Pocock — Licença MIT.
