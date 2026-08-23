# Pasta de trabalho sem escopo declarado

O usuário abriu uma sessão numa pasta que **já tem um `CONTEXTO.md`**, mas o
frontmatter desse arquivo não declara `escopo:`. Sem escopo o Koine não sabe a
que área de atuação a pasta pertence, e por isso não consegue carregar as
referências certas.

O `CONTEXTO.md` da pasta **não foi tocado** — o conteúdo que está lá é do
usuário e deve ser preservado.

## Instruções para o agente

**Hermes:** o usuário não pediu por isso e provavelmente não sabe o que é
frontmatter. Não peça a ele que edite YAML.

1. **Leia `./CONTEXTO.md` na íntegra** antes de qualquer pergunta. É o ponto de
   partida — não descarte, não reescreva do zero.
2. Inicie o skill `/kn-02-mantem-catalogo` no **Fluxo 3 (Pasta de trabalho)**,
   **sub-fluxo 3b (atualizar `CONTEXTO.md` existente)**. Não espere o usuário
   invocar a skill.
3. O delta é estreito: falta o **escopo** (liste os disponíveis em
   `~/.config/koine/escopos/` e deixe o usuário escolher) e, se ainda não
   houver, os **domínios**. Todo o resto do arquivo permanece como está.
4. Materialize com diff e confirme antes de gravar.

Ao final, a pasta terá um `CONTEXTO.md` com escopo real, o conteúdo original
preservado, e o usuário poderá reabrir a sessão com o agente que quiser.
