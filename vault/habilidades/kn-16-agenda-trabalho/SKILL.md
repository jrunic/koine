---
name: kn-16-agenda-trabalho
description: Agenda trabalho recorrente no Paseo com --cwd da pasta de trabalho e timezone explícito — a tela grava a âncora do projeto. Use para criar ou corrigir agendamento. Precisa do Paseo no ar (/kn-04).
id: 202609142900
projeto: koine
tipo: habilidade
status: ativo
tags: [habilidade, koine, paseo, agendamento, cotidiano]
---

# kn-16 — Agenda trabalho

Cria ou corrige um agendamento no Paseo para a **pasta de trabalho**, não para a
âncora do projeto. A tela preenche o cwd errado; esta skill sempre passa `--cwd`.

## Antes

```
paseo status
```

Se não responder, pare e mande `/kn-04-conecta-o-paseo`.

A pasta tem de ter `CONTEXTO.md` com `escopo:`. Sem isso a sessão agendada sobe vazia.

## Conversar

O quê, a cadência, **qual pasta**, e o fuso **IANA** (pergunte; não invente). O default
da CLI é UTC.

Provider: rode `koine paseo-info --json` e use o campo `provider` (genérico). Não
invente nome; não use `-hermes` por default.

## Criar

`--cwd` absoluto. `--cron` + `--timezone`. **Não use `--every` sozinho** — cai em UTC.

Prompt em aspas simples, sem crase.

```
paseo schedule create 'o trabalho' --provider <provider-do-info> --cwd /caminho/absoluto/da/pasta --cron '0 9 * * 1' --timezone <IANA-do-usuario>
```

## Se já nasceu pela tela

A tela gravou o cwd do projeto. Corrija:

```
paseo schedule ls
paseo schedule update <id> --cwd /caminho/absoluto/da/pasta
```

Não deixe um agendamento criado pela tela como está.
