---
name: kn-05-cria-skill
description: Cria uma skill própria do usuário — entrevista o fluxo de trabalho recorrente, valida nome e descrição contra o contrato que os harnesses exigem, e materializa um SKILL.md fora do vault, distribuído a cada cliente IA detectado. Use quando o mesmo procedimento foi repetido pela segunda vez e nenhuma kn-NN shipped cobre o caso.
id: 202609292000
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-05, skill-propria, criar-habilidade]
---

# kn-05-cria-skill

Cria uma **skill própria do usuário** — um procedimento reutilizável,
invocável como `/<nome>`, para um fluxo de trabalho recorrente que nenhuma
skill shipped (`kn-NN`) cobre. Paralelo direto ao `kn-03-cria-agente`, mas
para skill em vez de agente.

---

## Pré-condições

- Nenhuma. Roda em qualquer sessão, com qualquer agente.

---

## Abertura — validação de necessidade

Antes de entrevistar, descubra se faz sentido criar skill nova. Pergunte:

> "Que fluxo de trabalho você quer transformar em skill? Me dê um exemplo
> concreto da última vez que você repetiu esses passos."

Confira contra as skills já disponíveis (`kn-NN` do vault, mais qualquer
skill de usuário já criada). Se o fluxo já é coberto, redirecione e encerre.
Se a diferenciação for pequena (só um detalhe muda de uma skill existente),
aponte o overhead de mais um procedimento para o usuário lembrar e pergunte
se procede assim mesmo.

---

## Rodada 1 — Identidade

1. **Nome (slug)** — kebab-case, minúsculo, sem o prefixo `kn-<dois
   dígitos>-` (reservado ao produto). Sugira automaticamente a partir do
   fluxo descrito (ex.: "organizar o inbox do Gmail" → `organiza-inbox`) e
   confirme com o usuário.
2. **Descrição em 1 linha** — o trigger técnico que o próprio usuário (ou
   você, numa sessão futura) vai usar para decidir quando invocar. Entre 1 e
   1024 caracteres. Evite genérico ("ajuda com e-mail") — prefira específico
   ("Arquiva e-mail de notificação automática, cria tarefa para o que exige
   resposta, deixa threads de cliente para revisão manual").

## Rodada 2 — Procedimento

Pergunte, passo a passo:

> "Quando alguém invocar essa skill, o que ela faz primeiro? E depois? O
> que ela nunca faz, mesmo que pareça relacionado?"

Extraia:

- **Quando invocar** — o gatilho concreto.
- **Passo a passo** — a sequência de ações, com decisões explícitas onde
  houver ramificação.
- **O que produz** — arquivo, mensagem, decisão registrada.
- **O que NÃO faz** — limite explícito, para não crescer sem controle
  depois.

Monte o corpo do `SKILL.md` (título `# <nome>` + as seções acima) e mostre o
texto completo para confirmação antes de materializar.

---

## Materialização

**Se `koine` está disponível no PATH** (modo binário — teste com `koine
versao`): grave o corpo confirmado num arquivo temporário e chame:

```
koine criar-habilidade <nome> --descricao "<descrição>" --corpo <caminho-do-arquivo-temporario>
```

O comando valida, grava a skill em `~/.config/koine/habilidades/<nome>/SKILL.md`
e distribui para cada cliente IA detectado nesta máquina — sem você fechar e
reabrir a sessão para ela aparecer. Leia a saída do comando: se um harness
aparecer como "aviso: já tem uma skill '<nome>' que não é do Koine", esse
cliente já tinha uma skill de terceiro com o mesmo nome — a distribuição não
sobrescreveu, e o usuário precisa escolher outro nome ou resolver a colisão
manualmente ali.

**Se `koine` não está disponível** (modo skills, `koine-skills.zip`): não há
comando para chamar. Valide você mesmo, na entrevista, que o nome casa
`^[a-z0-9]+(-[a-z0-9]+)*$`, não começa com `kn-<dois dígitos>-`, e que a
descrição tem entre 1 e 1024 caracteres. Grave o arquivo direto em
`~/.config/koine/habilidades/<nome>/SKILL.md` (crie a pasta se não existir),
com o mesmo frontmatter (`name`, `description`, `origem: usuario`). Depois,
diga ao usuário os passos de cópia manual para cada cliente que ele usa —
mesmo papel que a `/kn-12-prepara-contexto` cumpre para o `CLAUDE.md` nesse
modo. As pastas de skill por cliente:

- Claude Code: `~/.claude/skills/<nome>/`
- Antigravity: `~/.gemini/antigravity-cli/skills/<nome>/`
- Copilot CLI: `~/.copilot/skills/<nome>/`
- OpenCode: `~/.config/opencode/skills/<nome>/`
- Codex CLI: `~/.agents/skills/<nome>/`

---

## Confirmação final

Depois de materializar (por comando ou manualmente), retorne:

> "Skill `<nome>` criada. Para invocar: `/<nome>`. O arquivo canônico mora em
> `~/.config/koine/habilidades/<nome>/SKILL.md` — edite ali se quiser
> ajustar depois, nunca na cópia dentro da pasta do cliente IA (a próxima
> distribuição sobrescreve a cópia sem aviso)."

---

## O que NÃO faz

- **Não edita nem remove skill de usuário já criada** — rode `/kn-05-cria-skill`
  de novo com outro nome, ou edite o arquivo canônico à mão.
- **Não cria skill com múltiplos arquivos** (scripts auxiliares) — só o
  `SKILL.md` único, mesmo padrão das skills atuais do vault Koine.
- **Não publica nem compartilha** a skill para outros usuários Koine.
- **Não cataloga a criação como referência** — se valer a pena registrar a
  decisão de criar essa skill, sugira `/kn-11-mantem-referencia` separado.
