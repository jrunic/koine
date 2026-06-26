---
descricao: Por que Koine separa em quatro camadas independentes — contexto histórico, alternativa rejeitada e o modelo mental de contexto cirúrgico
id: 202606201950
tipo: explicacao
status: ativo
tags: [explicacao, koine, arquitetura, camadas, harness, habilidades, base-de-conhecimento]
---

# Por que Koine separa em quatro camadas

## O problema que originou a separação

A adoção de agentes de IA como ferramenta de trabalho real passou por uma migração silenciosa: das interfaces de chat na nuvem — onde o agente não acessa seus arquivos, não roda seus utilitários, não conhece seu ambiente — para os clientes de terminal, que rodam na máquina do usuário e têm acesso a tudo isso.

Essa migração elimina o copiar e colar. O agente passa a fazer o trabalho, não a sugerir o trabalho.

Tentativas anteriores de estruturar esse modelo costumavam acoplar harness, habilidades, base de conhecimento e organização do filesystem em um único pacote. Adotá-las exigia também adotar a taxonomia de pastas de quem desenhou o sistema. Para um novo usuário com anos de organização própria, isso significava duas tarefas distintas: aprender a usar IA no terminal *e* migrar o sistema de arquivos para o padrão exigido.

Esses são dois problemas diferentes. Condicionar o segundo ao primeiro cria um backlog antes do usuário sequer começar.

## A alternativa que ficou de fora

Esteve na mesa uma solução intermediária: manter o acoplamento ao sistema de arquivos, mas oferecer ferramentas de migração que ajudassem o usuário a chegar na estrutura esperada — com alguma flexibilidade ao longo do caminho.

O problema dessa abordagem é estrutural: ela ainda condiciona "usar IA" à resolução de "organizar o sistema de arquivos". São problemas com horizontes de tempo e naturezas diferentes. Alguém que quer experimentar um agente na segunda-feira não deveria precisar reorganizar dois anos de pastas antes disso. Na prática, quem tenta fazer os dois ao mesmo tempo termina com um backlog de migração e sem adoção real de nenhum dos dois.

## A separação em camadas como resposta

Koine resolve isso separando o que o agente precisa saber de como o usuário organiza os arquivos.

Para trabalhar bem, um agente de IA precisa de seis tipos de informação:

- **Usuário** — quem está à frente: nome, função, empresa, estilo de comunicação, objetivos
- **Agente** — qual o papel, o nome, como se comunica, o que não faz
- **Ambiente** — como o ambiente de trabalho está organizado, onde ficam as ferramentas e habilidades
- **Conhecimento** — quais arquivos de referência existem, o que guardam, a quais escopos e domínios pertencem
- **Contexto** — do que se trata esta pasta de trabalho específica
- **Habilidades** — quais skills estão disponíveis e onde ficam

Koine distribui essas seis categorias em quatro camadas que podem evoluir de forma independente:

| Camada | O que entrega | Pode ser trocada ou expandida? |
|---|---|---|
| **Harness** | O executável que monta o contexto e aciona o cliente IA | Sim — Onda 1: Claude Code; Onda 2: Copilot CLI |
| **Habilidades** | As skills `kn-*` que guiam o agente em tarefas específicas | Sim — criar, adaptar ou importar sem tocar nas outras |
| **Base de conhecimento** | Os arquivos de referência do usuário, organizados por escopo e domínio | Sim — cresce e evolui sem afetar o harness |
| **Sistema de arquivos** | A organização das pastas de trabalho do usuário | Deliberadamente ausente — Koine não impõe nada aqui |

A quarta camada — sistema de arquivos — é a que desaparece como requisito. Koine não impõe estrutura de pastas. O usuário declara o contexto de uma pasta qualquer, e o harness monta o que o agente precisa saber a partir das outras três camadas.

## Por que a independência entre camadas importa

A memória de contexto de um agente de IA é pequena. Cada token usado para carregar informação que não é relevante à tarefa atual é um token que não existe para o trabalho propriamente dito.

Koine garante que essa memória seja preenchida com o que importa — e só com o que importa. A separação em camadas é o mecanismo: cada camada sabe o que é seu, carrega só o que é seu, e não interfere nas outras.

Quando o usuário troca de harness, as habilidades não mudam. Quando cria uma nova skill, a base de conhecimento não é afetada. Quando a base cresce, o contexto da pasta de trabalho permanece cirúrgico.

O resultado é um agente que, ao abrir uma pasta, sabe exatamente quem você é, o que você sabe, quais ferramentas tem disponíveis e o que essa pasta representa — sem saber nada além disso.
