---
name: kn-99-encerra-sessao
description: Encerra uma sessão Koine — sintetiza o que aconteceu, escreve diário na pasta de trabalho, distribui aprendizados (referências, ajustes em escopo/domínio/agente, tarefas) para os destinos canônicos. Ritual de fechamento que torna a sessão útil para o usuário do futuro.
id: 202606222300
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-99, encerramento, diario, distribuicao, fechamento]
---

# kn-99-encerra-sessao

Ritual de fechamento de sessão. Faz três coisas:

1. **Sintetiza** o que aconteceu na sessão — em prosa curta.
2. **Escreve diário** em `<pasta-de-trabalho>/diario/AAAAMMDD-<descricao>.md`.
3. **Distribui aprendizados** — direciona o que emergiu para o destino canônico (referência nova via `/kn-11`, ajuste de domínio via `/kn-02`, tarefa para outro agente, etc.).

Invoque ao final de uma sessão produtiva, antes de fechar o cliente IA. Sem isso, a sessão evapora — outras sessões não enxergam o que aconteceu aqui.

---

## Pré-condições

- Sessão rodando em **pasta de trabalho com `CONTEXTO.md`** — o diário vai na subpasta `diario/` dessa pasta. Se a sessão for em pasta sem `CONTEXTO.md` (caso raro — Hermes em pasta home durante onboarding, p.ex.), o diário vai em `~/.config/koine/diario/AAAAMMDD-<descricao>.md` como fallback.
- O agente em sessão tem leitura do que aconteceu (histórico da conversa atual) — sem isso, a síntese fica vazia.

---

## Conceitos referenciados

Nenhum conceito dedicado a carregar. A skill opera sobre o estado atual da sessão e o roteiro abaixo.

---

## Roteiro

### Rodada 1 — Síntese

Antes de perguntar, **proponha** uma síntese em 3-6 bullets cobrindo:

- O que era o objetivo da sessão (recuperado da abertura ou do `CONTEXTO.md`).
- O que foi decidido / produzido / mudado.
- O que ficou em aberto (decisões adiadas, pendências, dúvidas).
- O que mudou na estrutura Koine durante a sessão (referência catalogada, escopo ajustado, agente criado, etc.).

Apresente a síntese ao usuário e pergunte:

> "Confere? Ajustar algo? Falta algo importante?"

Aguarde correções. Não economize aqui — síntese mal feita prejudica todas as decisões de distribuição abaixo.

### Rodada 2 — Checklist de distribuição

**Antes de escrever o diário**, percorra o checklist abaixo. Para cada pergunta `sim`, execute a ação **antes** de continuar — não deixe para depois.

- **Conhecimento catalogável surgiu?** (pessoa nova relevante, organização stakeholder, decisão com motivação registrável, aprendizado, evento) → **pergunte o alcance ao usuário**: *"Esta referência se aplica a outras pastas de trabalho deste escopo?"*. Você (agente) não tem como saber — só o usuário sabe.
  - **Sim — outras pastas usam** → `/kn-11-mantem-referencia` (alcance de escopo; vai para pasta-referências).
  - **Não — só esta pasta**, e cabe em 1-2 frases → **edita `CONTEXTO.md` direto**: linha em seção "Referências locais" (cria a seção se ainda não existe) com nome do conceito + 1 linha de descrição.
  - **Não — só esta pasta**, material denso (checklist, várias seções, lista longa) → cria `<slug>.md` na **raiz da pasta de trabalho** + linha em CONTEXTO.md apontando + descrição. Sem `index.md`, `log.md`, `kn-indice` — pasta de trabalho não tem contrato OKF (soberania do usuário).
- **Preferência ou restrição do usuário emergiu?** (jeito de falar, calibragem que ele corrigiu) → `/kn-02-mantem-catalogo` Fluxo 1 (arquivo do usuário). Anote o delta exato (o que o usuário disse) antes de invocar.
- **Calibragem do agente operacional desafinou?** (algo no tom/calibragem do agente em sessão incomodou e o usuário sinalizou) → editar `~/.config/koine/agentes/<nome>.md` diretamente (Onda 1 não tem skill de edição). Mostrar diff ao usuário.
- **Dinâmica do escopo mudou?** (stakeholder central novo, foco operacional do escopo se redefiniu) → `/kn-02-mantem-catalogo` Fluxo 2b (atualizar escopo).
- **Padrão ou restrição da pasta de trabalho?** (decisão técnica/operacional que sessões futuras nesta pasta precisam respeitar) → **edita `<pasta>/CONTEXTO.md` direto agora**, antes do diário. Sem invocar `/kn-02` — CONTEXTO.md é da pasta, soberania do usuário, edição direta cabe. Mostre o diff ao usuário antes de gravar.
- **Domínio do usuário precisa refino?** (sinopse imprecisa, edge case novo a registrar, campos recomendados a ajustar) → `/kn-02-mantem-catalogo` Fluxo 4b.
- **Feedback sobre o método Koine em si?** (algo do método em si — KOINE.md, conceitos canônicos, Hermes, skills `kn-*`) → registrar no diário com tag clara; Onda 1 não tem path de feedback automatizado, fica como pendência externa.
- **Tarefa emergiu para outro escopo ou ação externa?** → registrar no diário; orientar o usuário a abrir no sistema dele.
- **Nada a distribuir?** (sessão exploratória sem produção) → ok, diário curto registrando exploração.

Decisões de distribuição que exigem invocar outra skill: pergunte se o usuário quer fazer agora ou anotar pendência. Default: **agora**, porque o contexto está quente.

#### Tabela rápida — pergunta → destino

| Surgiu nesta sessão... | Destino canônico |
|---|---|
| Referência catalogável, **alcance de escopo** (outras pastas usam) | `/kn-11-mantem-referencia` |
| Referência catalogável, **alcance de pasta**, cabe em frase | linha em `<pasta>/CONTEXTO.md` (edita direto) |
| Referência catalogável, **alcance de pasta**, material denso | `<slug>.md` na raiz da pasta + linha em CONTEXTO.md |
| Preferência/restrição do usuário (jeito de comunicar) | `/kn-02-mantem-catalogo` Fluxo 1 |
| Calibragem/tom do agente operacional | edição manual de `~/.config/koine/agentes/<nome>.md` |
| Dinâmica/stakeholder central do escopo | `/kn-02-mantem-catalogo` Fluxo 2b |
| Padrão/restrição da pasta de trabalho | edita `<pasta>/CONTEXTO.md` direto (sem skill) |
| Sinopse/edge-case de domínio do usuário | `/kn-02-mantem-catalogo` Fluxo 4b |
| Feedback sobre o método Koine em si | diário + pendência externa |
| Tarefa para outro escopo / fora do Koine | diário + sistema externo do usuário |
| Nada generalizável (sessão exploratória) | diário curto |

### Rodada 3 — Materialização do diário

**Antes de montar o arquivo, colete a Voz do Usuário.** Percorra a conversa desta sessão do início ao fim e copie **todas** as mensagens do usuário em ordem cronológica para a seção `## Voz do Usuário`. Sem seleção (incluir até "ok", "segue", correções triviais), sem paráfrase, sem reordenamento. Essa é a parte mais importante do diário — se sob pressão, corte outra coisa antes de cortar daqui.

Monte o diário em `<pasta-de-trabalho>/diario/AAAAMMDD-<descricao-kebab>.md`:

- `AAAAMMDD` da data da sessão.
- `<descricao-kebab>` curta (3-6 palavras) que sintetiza o foco da sessão.

Estrutura:

```markdown
---
type: Diario
title: <Descrição legível>
description: <1 linha — síntese da sessão>
data: AAAA-MM-DD
escopo: <slug-escopo>
agente: <nome do agente que conduziu>
dominios: [<dom1>, <dom2>]
tags: [diario, sessao, <descricao>]
---

# <Descrição legível>

## Objetivo da sessão

<1-2 linhas — o que se foi fazer.>

## O que foi feito

<3-6 bullets — produções, decisões, mudanças.>

## O que ficou em aberto

<bullets — pendências, decisões adiadas, dúvidas.>

## Distribuição

<lista das ações de distribuição executadas ou anotadas como pendência.>
- ✓ Referência `<slug>` catalogada via /kn-11
- ✓ Domínio `<slug>` atualizado via /kn-02
- → Tarefa para outro escopo: <descricao> (registrar fora do Koine)
- → Continuação na próxima sessão: <pendência>

## Próxima sessão

<1-2 linhas — gancho para retomar; o que ler primeiro, o que continuar.>

## Voz do Usuário

<Transcrição literal de TODAS as mensagens do usuário nesta sessão. Sem seleção. Sem paráfrase. Sem reordenamento. Tudo o que o usuário escreveu, do início ao fim, na ordem em que escreveu.>
```

**Voz do Usuário** é seção obrigatória — não opcional. Função: proteger contra deriva de interpretação do agente. Quando o usuário relê o diário daqui a semanas ou meses, vê o que **ele** disse, não o que o agente entendeu. Sem seleção (incluir até "ok", "segue", correções triviais), sem paráfrase ("o usuário pediu X" não conta — colar o que ele escreveu), sem reordenamento. Mensagens vão na ordem cronológica em que aconteceram.

Crie a subpasta `diario/` se não existir. Mostre o arquivo final ao usuário antes de gravar.

### Rodada 4 — Atualização do `log.md` da pasta-referências (condicional)

Se a sessão mexeu na estrutura do escopo **sem passar por `/kn-11` ou `/kn-02`** (ajuste manual raro — edição direta de `<slug-escopo>.md`, p.ex.), adicione entrada em `log.md` da pasta-referências:

```
AAAAMMDD — sessao — <pasta-de-trabalho> — <síntese curta>
```

Caso contrário, **pular esta rodada** — `/kn-11` e `/kn-02` já cuidam do `log.md` quando invocadas. Não duplique entradas.

### Rodada 5 — Fechamento

Apresente resumo final:

> "Sessão encerrada. Diário em `<path>/diario/AAAAMMDD-<descricao>.md`.
>
> Distribuído:
> - <lista>
>
> Pendente:
> - <lista>
>
> Até a próxima."

Sem despedida arrastada. O agente Koine encerra como abre — direto.

---

## Exemplos de uso

**Sessão de trabalho em escopo de cliente.** Usuário trabalhou com agente operacional revisando contrato com fornecedor. Decidiu trocar de fornecedor por questão de prazo.

> Ao invocar `/kn-99`: síntese proposta — "Revisão de contrato com fornecedor Z; decidida troca por fornecedor W para garantir prazo de entrega; pendência: validar com Y na quarta". Usuário confirma. Checklist: decisão generalizável? Sim — vira referência `decisao-troca-fornecedor-z.md` via `/kn-11`. Stakeholder novo? Sim — fornecedor W vira referência `fornecedor-w.md`. Padrão da pasta? Não. Diário em `<pasta>/diario/20260624-troca-fornecedor.md` com seções padrão + Voz do Usuário transcrevendo a conversa toda.

**Sessão de coaching (agente operacional `leia`).** Usuário pediu ajuda para preparar conversa difícil com sócio.

> Ao invocar `/kn-99`: síntese proposta — "Preparação para conversa com sócio X sobre redefinição de papéis; estruturados 3 pontos-âncora e antecipação de 2 reações; sem decisão tomada". Usuário ajusta um detalhe. Checklist: nada catalogável como referência (preparação ainda não virou decisão). Preferência do usuário emergiu? Sim — usuário corrigiu o agente quando ele propôs roteiro detalhado demais ("não preciso de script, preciso de norte"). Vai para `/kn-02` Fluxo 1, atualizando `estilo:` do arquivo do usuário. Diário curto. Voz do Usuário transcreve correção literal.

**Sessão exploratória (sem produção).** Usuário abriu Claude para "pensar em voz alta" sobre próximo trimestre. Não chegou em decisão.

> Ao invocar `/kn-99`: síntese — "Exploração sobre prioridades do trimestre; sem decisão tomada; tópicos levantados: A, B, C". Checklist: nada a catalogar (sem decisão); nada estrutural mudou. Diário curto em `<pasta>/diario/AAAAMMDD-exploracao-prioridades.md` registrando os 3 tópicos como ganchos para sessão futura. Voz do Usuário transcrita integralmente — preserva o material para retomar depois.

---

## O que NÃO faz

- **Não cataloga referência diretamente.** Catalogação é `/kn-11-mantem-referencia`. `/kn-99` orquestra (propõe `/kn-11` quando aplicável), mas não duplica a entrevista.
- **Não ajusta estrutura Koine diretamente.** Ajustes de escopo/contexto/domínio passam por `/kn-02-mantem-catalogo`.
- **Não escreve em log/artefatos de outros escopos.** Cross-escopo é registrado como pendência no diário; ação ocorre em sessão futura no escopo certo.
- **Não compacta histórico do cliente IA.** Diário é seletivo e estruturado, não dump. Síntese sintetiza; transcript não importa.
- **Não corre se o usuário ainda está pensando.** Encerramento prematuro perde a parte mais valiosa (o que ficou em aberto). Se o usuário hesita em qualquer rodada, pause e ofereça continuar e retomar `/kn-99` depois.

---

## Checkpoints

- **Síntese** é o passo mais importante — gaste tempo aqui, não nas formalidades.
- Antes de gravar o diário, mostre o arquivo completo para confirmação.
- Distribuição que exige outra skill: pergunte se o usuário quer fazer agora ou anotar pendência. Default: agora, com contexto quente.
- Se a sessão foi de baixa densidade (exploração sem produção), tudo bem — diário curto, registrando que foi exploração. Não force estrutura onde não houve.
