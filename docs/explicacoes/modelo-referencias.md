---
descricao: Por que o CLAUDE.md gerado pelo kn-agente usa @/ para referenciar arquivos em vez de copiar o conteúdo — fonte canônica, ciclo de atualização e o papel dos skills de catálogo
id: 202606202010
tipo: explicacao
status: ativo
tags: [explicacao, koine, modelo-b, claude-md, referencias, harness]
---

# Por que o CLAUDE.md usa referências e não cópias

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

O Modelo de Referências resolve isso com uma linha por fonte:

```
@/Users/<usuário>/.config/koine/usuario.md
@/Users/<usuário>/.koine/KOINE.md
@/Users/<usuário>/.koine/agentes/koine/AGENTE.md
@/Users/<usuário>/.config/koine/biblioteca-dominios/INDEX-universal.md
@CONTEXTO.md
```

O `CLAUDE.md` não contém informação — contém endereços. Quando o cliente IA abre a sessão, vai buscar cada arquivo no caminho indicado e monta o contexto na hora.

Há uma segunda garantia de atualização: o `CLAUDE.md` é gerado pelo `kn-agente` no momento em que o usuário inicia uma sessão de trabalho na pasta. Não é um arquivo criado uma vez e esquecido — é produzido sob demanda, refletindo o estado atual de todas as fontes no momento exato da sessão.

As duas propriedades juntas eliminam qualquer forma de desatualização: as fontes canônicas evoluem nos seus próprios arquivos, e o `CLAUDE.md` é sempre uma visão fresca delas, gerada no início de cada sessão.

## Quem garante que os arquivos existam

O Modelo de Referências pressupõe que cada caminho referenciado exista e esteja atualizado. Isso não é responsabilidade do usuário gerenciar manualmente — é o que os skills de catálogo do Koine fazem.

O onboarding e a manutenção do catálogo são conduzidos pelo próprio agente de IA, apoiado pelos skills `kn-*` distribuídos com a solução. O skill cria o `USUARIO.md` na primeira sessão, o skill registra um novo escopo, o skill captura conhecimento na base. É trabalho personalizado e assistido — o usuário responde perguntas, o agente materializa os arquivos nos lugares certos.

O ciclo fecha: os skills garantem que as fontes existam e estejam adequadas; as fontes alimentam o `CLAUDE.md`; o `CLAUDE.md` alimenta o agente que roda os skills.

## O que o `@` representa

O `CLAUDE.md` gerado pelo `kn-agente` usa `@` para pescar cada pedaço de informação que o agente precisa para aquela conversa — nem mais, nem menos. A metodologia do Koine garante que cada pedaço exista e seja adequado.

O `@` não é um atalho técnico. É a expressão de uma arquitetura onde contexto e conteúdo vivem separados: o conteúdo evolui nas suas fontes canônicas, o contexto os combina na medida exata da sessão.
