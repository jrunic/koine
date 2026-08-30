# Esta pasta aponta para um escopo que não existe

O `CONTEXTO.md` desta pasta está correto e completo — tem a Ficha Koine, e o
campo `escopo:` está preenchido. O que falta é o **escopo em si**: não existe
arquivo cadastrado com esse nome.

A sessão subiu com o Hermes e **sem as referências do escopo**, para não deixar o
usuário parado.

Não é erro de digitação de agora: ninguém acabou de digitar esse nome. Ele está
gravado no arquivo, e o motivo mais comum é que o escopo foi **renomeado ou
apagado** depois de a pasta ter sido configurada — o que põe nesse mesmo estado
todas as outras pastas que o declaravam.

O `CONTEXTO.md` **não foi tocado**.

## Instruções para o agente

**Hermes:** diga isto ao usuário na primeira mensagem, sem rodeios — uma sessão
que sobe sem as referências e não avisa é indistinguível de uma sessão normal.

1. **Diga qual escopo a pasta declara** e que ele não foi encontrado.
2. **Liste os escopos cadastrados.** Se o nome certo estiver ali, é quase certo
   que foi renomeação: confirme com o usuário qual deles a pasta deve usar.
3. **Não peça a ele que edite YAML**, e não sugira "corrigir o frontmatter". A
   ficha do `CONTEXTO.md` já se perdeu assim antes.
4. Conduza `/kn-02-mantem-catalogo`, no fluxo de escopo:
   - escopo **renomeado** → o caminho é apontar a pasta para o nome novo;
   - escopo **apagado por engano** → recrie-o com o mesmo nome, e todas as
     pastas que o declaravam voltam de uma vez.
5. Se o usuário quiser **seguir só nesta sessão** sem resolver, tudo bem: não
   grave nada. O aviso volta na próxima vez, e isso é intencional.

Enquanto não estiver resolvido, você pode trabalhar aqui normalmente — o que
falta são as referências do escopo, não a capacidade de ler e escrever arquivos.
Só não invente o cadastro: não chute qual escopo era, e não crie um novo por
conta própria.
