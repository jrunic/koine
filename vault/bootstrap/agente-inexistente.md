# A pasta declara um agente que não existe

O `CONTEXTO.md` desta pasta declara um agente no campo `agente:` — ou o usuário
tem um agente default configurado —, mas **não existe arquivo para esse nome**.
A sessão subiu com o Hermes para não deixar o usuário parado.

Não é erro de digitação: ninguém acabou de digitar esse nome. Ele está gravado
num arquivo, e o motivo mais comum é que o agente foi renomeado ou apagado
depois de a pasta ter sido configurada.

O `CONTEXTO.md` **não foi tocado**.

## Instruções para o agente

**Hermes:** o usuário provavelmente não sabe que esse campo existe. Não peça a
ele que edite YAML, e não sugira "corrigir o frontmatter".

1. **Diga qual nome a pasta declara** e que ele não foi encontrado.
2. **Liste os agentes que existem**: os do usuário em `~/.config/koine/agentes/`
   e o Hermes, que vem com o Koine.
3. Pergunte qual deles a pasta deve usar daqui em diante.
4. **Grave pelo comando, nunca editando o arquivo à mão:**

   ```
   koine definir-agente <nome-escolhido>
   ```

   O comando preserva o resto do frontmatter e guarda o conteúdo anterior antes
   de gravar. Editar o YAML à mão é o que já fez usuários perderem a ficha do
   `CONTEXTO.md` inteira.

5. Se o usuário quiser **criar** um agente com esse nome em vez de escolher
   outro, conduza `/kn-03-cria-agente` e grave depois.

6. Se ele preferir seguir com o Hermes só nesta sessão, tudo bem: não grave
   nada. O aviso volta na próxima vez, e isso é intencional.
