---
descricao: Por que o contexto da sessão é montado das fontes canônicas a cada vez, em vez de copiado para dentro da pasta de trabalho — e por que o mecanismo de entrega mudou sem a arquitetura mudar
id: 202606202010
tipo: explicacao
status: ativo
tags: [explicacao, koine, modelo-b, claude-md, referencias, harness]
---

# Por que o contexto é montado, e não copiado

## O problema do contexto hierárquico

A maioria dos clientes de IA de terminal carrega contexto de forma hierárquica: sobe na árvore de pastas, lê arquivos de configuração em cada nível e monta um contexto por composição. Parece elegante — mas condiciona o bom funcionamento a uma organização específica de pastas. Quem não estrutura os diretórios da forma esperada fica sem contexto ou com contexto errado.

Koine toma uma direção diferente: gera um `CLAUDE.md` específico para aquela pasta e para aquela sessão de trabalho, a partir de fontes canônicas que vivem em lugares fixos e conhecidos. A pasta de trabalho não precisa ter uma relação especial com nenhuma outra pasta.

## A alternativa inline e por que falha

A alternativa mais óbvia ao modelo de referências é o inline: copiar o conteúdo dos arquivos de contexto diretamente dentro do `CLAUDE.md` gerado. O arquivo fica autossuficiente — tudo em um lugar só.

O problema é que esse arquivo tem dois destinos possíveis:

1. **Envelhece.** O `USUARIO.md` original é atualizado, o cargo muda, os objetivos mudam — mas o `CLAUDE.md` da pasta de projetos ainda carrega a versão antiga. O agente trabalha com informação defasada sem nenhum sinal de que isso aconteceu.

2. **Demanda retrabalho constante.** Para evitar o envelhecimento, o usuário precisa regenerar todos os `CLAUDE.md` espalhados pelas pastas de trabalho sempre que qualquer fonte muda. Um `USUARIO.md` único referenciado em dezenas de pastas vira dezenas de operações manuais — ou automatizadas, mas ainda desnecessárias.

Nenhum dos dois é aceitável para algo que deveria funcionar sem atrito.

## Referências em vez de cópias

O Modelo de Referências resolve isso mantendo **uma fonte canônica por assunto** — o
arquivo do usuário, o `KOINE.md`, o arquivo do agente, o escopo, os índices de domínio,
o `CONTEXTO.md` da pasta — e **montando o contexto da sessão a partir delas, na hora**.

O que o Koine monta a cada sessão é um pacote descartável, no cache, entregue ao cliente
pelo canal que ele oferece. Nenhuma cópia é deixada na pasta de trabalho para envelhecer:
o pacote nasce e morre com a sessão, e a sessão seguinte o refaz a partir das fontes como
elas estiverem naquele momento.

É isso que elimina as duas formas de desatualização de uma vez. As fontes evoluem nos
seus próprios arquivos; o contexto é sempre uma visão fresca delas; e o usuário não tem
nenhum arquivo espalhado para regenerar, porque não há arquivo espalhado.

Hoje **todos os cinco clientes recebem conteúdo**, não caminho — com o aviso, dentro do
próprio pacote, de que o `CONTEXTO.md` ali é um retrato e a fonte canônica é o arquivo da
pasta.

Nem sempre foi assim: um dos canais aceitava lista de caminhos, e passá-los parecia
estritamente melhor — o cliente leria os arquivos vivos. Isso caiu por uma razão medida.
Entregue por caminho, o `CONTEXTO.md` chega **cru**, com a ficha de metadados que o Koine
usa para resolver a sessão; e o campo de agente dessa ficha passava a competir com o
agente que o usuário havia pedido — e vencia. Pedir um agente numa pasta que declara
outro subia o **errado, em silêncio**.

A lição vale além do caso: entregar por referência transporta junto tudo o que o arquivo
carrega, inclusive o que era para ser lido só pela ferramenta.

## Quem garante que os arquivos existam

O Modelo de Referências pressupõe que cada caminho referenciado exista e esteja atualizado. Isso não é responsabilidade do usuário gerenciar manualmente — é o que os skills de catálogo do Koine fazem.

O onboarding e a manutenção do catálogo são conduzidos pelo próprio agente de IA, apoiado pelos skills `kn-*` distribuídos com a solução. O skill cria o `USUARIO.md` na primeira sessão, o skill registra um novo escopo, o skill captura conhecimento na base. É trabalho personalizado e assistido — o usuário responde perguntas, o agente materializa os arquivos nos lugares certos.

O ciclo fecha: os skills garantem que as fontes existam e estejam adequadas; as fontes alimentam o contexto da sessão; o contexto alimenta o agente que roda os skills.

## Por que "referência" e não "cópia", se o conteúdo às vezes vai junto

A distinção não é sobre bytes trafegarem ou não. É sobre **onde mora a verdade**.

Numa cópia, o arquivo copiado passa a ser uma segunda versão da informação: alguém pode
editá-lo, ele diverge da origem, e a partir daí ninguém sabe qual das duas vale. No
Modelo de Referências há uma fonte só, e o que a sessão recebe é um retrato dela, com
prazo de validade de uma sessão. Editar o retrato não altera nada — e por isso o Koine
diz, dentro do próprio pacote, que a fonte é o arquivo da pasta.

Essa era a intenção do `@path` do começo do projeto, e ele deixou de servir por uma razão
medida: import de caminho absoluto para **fora** da pasta de trabalho não é expandido em
pasta que o usuário não aprovou, e a aprovação é por pasta, escrita só pelo diálogo
interativo. Uma pasta nova aberta remotamente nunca seria aprovada — a sessão subia sem
contexto e **sem erro**. O que mudou foi o mecanismo de entrega; a arquitetura, não.
