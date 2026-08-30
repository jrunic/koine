# O provider desta sessão pede um agente que não existe

Esta sessão foi aberta **de fora do terminal** — por um orquestrador, do celular
ou do browser. O provider que a abriu declara qual agente usar, e **não existe
arquivo para esse nome**.

A sessão subiu com o Hermes para não deixar o usuário parado.

O que está errado **não é o `CONTEXTO.md` desta pasta**: é a configuração do
provider, que fica na máquina onde o orquestrador roda. Nada aqui foi tocado, e
consertar a pasta não resolveria — o mesmo aviso voltaria na sessão seguinte, em
qualquer pasta que esse provider abrisse.

## Instruções para o agente

**Hermes:** diga isto ao usuário na primeira mensagem.

1. **Diga qual nome o provider pede** e que ele não foi encontrado.
2. **Liste os agentes que existem** — os dele e o Hermes, que vem com o Koine.
3. Explique onde está o defeito: **na configuração do provider**, não nesta
   pasta. Se ele quiser o agente que o nome sugere, o caminho é criá-lo com
   `/kn-03-cria-agente`; se quiser outro, o caminho é corrigir o provider.
4. **A correção do provider se faz no terminal da máquina onde o orquestrador
   roda**, não daqui: uma sessão Koine na pasta canônica, conduzindo
   `/kn-04-conecta-o-paseo`. Ela reescreve os providers e confere os nomes.
5. Se ele preferir seguir com o Hermes por enquanto, tudo bem — é para isso que
   a sessão subiu em vez de falhar.

Não tente editar a configuração do orquestrador a partir daqui, e não escreva
nada no `CONTEXTO.md` para compensar: o campo `agente:` da pasta é outra coisa, e
mexer nele deixaria dois nomes divergentes para consertar depois.
