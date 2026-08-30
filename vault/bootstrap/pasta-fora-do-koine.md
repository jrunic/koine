# Esta pasta ainda não é uma pasta de trabalho Koine

A sessão foi aberta **de fora do terminal** — por um orquestrador, do celular ou
do browser —, numa pasta que não tem contexto Koine configurado.

**Nada foi escrito aqui, e nada deve ser.** Quando o usuário abre uma pasta pelo
terminal, ele fez `cd` de propósito e o Koine pode conduzi-lo à configuração ali
mesmo. Por um orquestrador não vale o mesmo: as sondagens do serviço rodam de
onde ele subiu, e materializar arquivo nessa condição enche de configuração
pastas que ninguém escolheu.

## Instruções para o agente

Diga ao usuário, **na primeira mensagem e sem rodeios**, que esta pasta ainda não
está configurada — e que por isso a sessão está sem o contexto de trabalho dele.
Não deixe isso implícito: uma sessão que sobe sem contexto e não avisa é
indistinguível de uma sessão normal, e o usuário só descobre quando as respostas
saem genéricas.

Em seguida, oriente o caminho:

1. Abrir uma sessão na **pasta canônica do Koine** — a pasta de meta-trabalho,
   com o Hermes.
2. Pedir ao Hermes para criar a pasta de trabalho nova. Ele conduz o
   `/kn-02-mantem-catalogo` no **Fluxo 3** e deixa a pasta pronta, com escopo e
   domínios.
3. Voltar a esta pasta. Na próxima abertura, a sessão sobe com o contexto certo.

Se o usuário preferir, **você pode trabalhar aqui assim mesmo**: o que falta é o
contexto Koine, não a capacidade de ler e escrever arquivos. Só não invente
configuração — não escreva `CONTEXTO.md` por conta própria, e não chute escopo
nem domínio. Essa parte nasce de uma conversa com o usuário, não de um palpite.
