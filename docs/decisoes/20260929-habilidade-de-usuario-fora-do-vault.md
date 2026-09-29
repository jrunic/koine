---
id: 202609292100
tipo: decisao
status: aprovado
projeto: koine
escopo: repo:koine
plataforma: "*"
description: "ADR — skill própria do usuário mora em ~/.config/koine/habilidades/, fora do vault, com distribuição e guarda de propriedade próprias"
tags: [adr, koine, habilidades, skill-propria]
---

# ADR — Skill de usuário mora fora do vault, com distribuição própria

## Status

Aceito.

## Contexto

O Koine já dá ao usuário um mecanismo para criar um agente operacional
derivado (`kn-03-cria-agente`, gravado em `~/.config/koine/agentes/`), mas
nenhum equivalente para criar uma skill própria — um procedimento
reutilizável para um fluxo de trabalho recorrente que nenhuma skill shipped
cobre.

O vault (`~/.local/share/koine/`, extraído pelo `instalar`) é território do
produto: `instalar`/`atualizar` sobrescrevem o que está lá com o conteúdo da
release. Gravar skill de usuário dentro dele arriscaria perdê-la na próxima
atualização.

O mecanismo que hoje distribui as skills do vault para a pasta de skills de
cada cliente IA (`instalar_habilidades_detalhado`) só reconhece diretórios
cujo nome começa com `kn-` — filtro que existe para não confundir skill do
produto com qualquer outra coisa que apareça na pasta do vault. Skill de
usuário não pode usar o padrão `kn-<dois dígitos>-` (para não se confundir
com skill shipped do lado do usuário), então reusar o mesmo mecanismo sem
ajuste a excluiria por construção — e é essa mesma exclusão, hoje, que
protege a cópia de skill de usuário contra `instalar`/`atualizar`.

## Decisão

Skill de usuário vive em `~/.config/koine/habilidades/<nome>/SKILL.md` —
mesma árvore de configuração que já guarda `agentes/` e `escopos/`, nunca
tocada por `instalar`/`atualizar`. A distribuição para cada cliente IA
detectado usa uma rotina própria (`habilidade_usuario.distribuir`), que
reaproveita a lógica de comparação/troca de diretório do mecanismo do vault
(extraída para um módulo compartilhado, `dircopy.py`) mas com uma checagem
que o mecanismo do vault não precisa: antes de substituir o que já existe na
pasta do cliente, confirma que aquele diretório foi criado pelo Koine (marca
`origem: usuario` no frontmatter do `SKILL.md`) — recusa sobrescrever skill
de terceiro instalada por fora.

Um único comando do CLI (`koine criar-habilidade`) cria, valida e distribui
num só passo — a skill do vault que conduz a entrevista (`kn-05-cria-skill`)
nunca grava nem distribui por conta própria no modo binário; delega ao
comando. No modo skills (sem o binário `koine`), a skill grava o arquivo
canônico diretamente e orienta cópia manual para cada cliente.

## Consequências

- Skill de usuário sobrevive a `koine atualizar`/`instalar --force`, com o
  mesmo grau de proteção que já vale para `~/.config/koine/agentes/`.
- Nome de skill de usuário não pode usar o padrão `kn-<dois dígitos>-`,
  reservado ao catálogo do produto.
- Editar skill de usuário depois de criada é manual — não há fluxo de
  edição nesta versão.
- O arquivo canônico é `~/.config/koine/habilidades/<nome>/SKILL.md`; a
  cópia em cada cliente IA é derivada e sobrescrita a cada distribuição —
  editar a cópia em vez do canônico perde a mudança na próxima
  `koine criar-habilidade` do mesmo nome ou na próxima sessão que rodar a
  distribuição de novo.
