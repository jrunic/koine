---
name: kn-03-cria-agente
description: Cria agente operacional derivado em ~/.config/koine/agentes/<nome>.md — entrevista identidade, foco operacional, voz/tom, calibragens e mecânica; default fork do Hermes ajustando o que diferencia. Invocada por /kn-01 na rodada final do onboarding e ad-hoc quando emerge tipo de sessão com voz distinta.
id: 202606222100
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-03, agente, criar-agente, derivado, operacional]
---

# kn-03-cria-agente

Cria um **agente operacional derivado** — aquele que vai conduzir um tipo recorrente de sessão do usuário (código, redação, coaching, análise financeira, gestão de agenda, etc.). Hermes opera o método; agentes derivados operam o trabalho.

Invocada em dois contextos:

- Pela `/kn-01-recebe-usuario` na rodada final (primeiro agente operacional do usuário).
- Diretamente pelo usuário (`/kn-03-cria-agente`) quando emerge um tipo de sessão recorrente com voz e calibragens distintas dos agentes existentes.

---

## Pré-condições

- Arquivo do usuário existe (`~/.config/koine/<nome>.md`). Se não existir, redirecione para `/kn-01-recebe-usuario`.
- Setup concluído (modo binário ou skills) — Hermes existe em `~/.local/share/koine/agentes/hermes.md` para servir de base do fork.

---

## Conceitos referenciados

Carregue **antes** de começar a entrevista:

- `~/.local/share/koine/conceitos/agentes.md` — doutrina sobre tipos de agente, anatomia, resolução em runtime, edge cases.

Use o Hermes (`~/.local/share/koine/agentes/hermes.md`) como **referência viva de estrutura** durante a redação.

---

## Roteiro

### Abertura — validação de necessidade

Antes de qualquer entrevista, descubra se faz sentido criar agente novo. Pergunte:

> "Que tipo de sessão recorrente esse agente vai conduzir? Me dê 2-3 exemplos concretos de sessões que esse agente operaria."

Examine os exemplos contra a heurística do `conceitos/agentes.md`:

- **Sessões cobertas por agente existente.** Liste os agentes ativos em `~/.config/koine/agentes/` + Hermes em vault. Se os exemplos couberem em algum existente com pequenos ajustes, **redirecione para edição manual** (Onda 1 não tem skill de edição de agente — orientar o usuário a editar o `.md` direto, sob `conceitos/agentes.md` §"Como manter agente existente"). Encerre.
- **Sessões sem voz/calibragem distinta.** Se a diferenciação for só "outro tipo de trabalho" mas voz e calibragens são iguais às de um agente existente, o ganho é baixo. Aponte o overhead (mais um nome para gerenciar, menos foco em um agente forte) e pergunte se procede mesmo assim.
- **Sessões com diferenciação clara.** Avance para a entrevista.

No fluxo orquestrado pela `/kn-01` (primeiro agente do usuário), pule a validação — é a primeira ocorrência por definição.

---

### Rodada 1 — Identidade

Perguntas (uma por vez):

1. **Title legível** — nome humano do agente (ex: "Leia", "Helena", "Atlas"). Pode ser nome próprio ou palavra que capture a identidade.
2. **Slug** — derivado do title: sugira automaticamente a versão kebab-case em minúsculas (ex: "Leia" → `leia`, "Atlas Prime" → `atlas-prime`). Confirme com o usuário antes de prosseguir. Será o `<nome>` em `~/.config/koine/agentes/<nome>.md` e em `kn-<cliente> <nome> [pasta]`. Verifique colisão em config e vault — se colidir com `hermes`, alerte sobre o efeito de fork (`conceitos/agentes.md` §"Resolução em runtime") antes de prosseguir.
3. **Description em 1 linha** — densa e específica. Aparece quando o usuário escolher agente em listagens ou ao invocar `kn-<cliente>` sem args. Evite genérico tipo "Agente operacional do usuário".

### Rodada 2 — Âncora ficcional (opcional)

Tangibilizar o agente com um personagem de ficção ajuda a fixar a identidade. Funciona como **norte gravitacional** nas rodadas seguintes: quando o usuário travar em tom, calibragem ou mecânica, pode-se perguntar "como esse personagem reagiria?".

Pergunta:

> "Tem algum personagem de ficção (livro, série, filme, jogo) cuja forma de operar capture o espírito desse agente? Não precisa caber 100% — basta um norte. Exemplos: Spock para rigor analítico; Hermione para diligência didática; Don Draper para concisão executiva."

Se o usuário não tiver personagem em mente, **pule a rodada** — opcional. Se tiver, extraia 3 elementos:

- **Personagem + obra** (ex: "Spock em Star Trek").
- **Traço-âncora** — em 1 linha, o que desse personagem captura o agente (ex: "racionalidade sem ironia, frieza emocional como ferramenta").
- **O que descartar** — algum traço do personagem que **não** deve aparecer no agente (ex: "rigidez literal de protocolo, ausência total de empatia").

**Anti-padrão a sinalizar:** personagem é norte, não molde. Não tentar replicar fielmente. Se em alguma rodada seguinte a fidelidade ao personagem virar restrição, descarta a âncora e fica só com a identidade construída.

### Rodada 3 — Foco operacional

> "Que tipos de trabalho ou sessão esse agente privilegia? Quais skills `/kn-*` ele tende a invocar mais? (lembrando: tecnicamente todos os agentes têm acesso a tudo — foco operacional é só preferência de uso)."

Extraia 2-4 bullets curtos descrevendo:

- Tipos de sessão típicos (ex: "revisão de contrato", "planejamento semanal").
- Skills favorecidas (ex: tende a invocar `/kn-11` para catalogar aprendizado; raramente toca `/kn-02`).
- Qualquer contraste explícito com Hermes (ex: "diferente do Hermes, não conduz onboarding").

### Rodada 4 — Tom e registro

Pergunte aberto e específico:

> "Como esse agente fala? Pense em voz, formalidade, idioma, postura. Algum agente IA que você já usou e gostou da forma de falar? Algum que detesta e quer evitar?"

Extraia 4-7 bullets cobrindo:

- Idioma e variante (PT-BR, EN-US, etc.).
- Registro (formal, par sênior, didático).
- Tamanho de resposta default (enxuto, expansivo).
- Padrão de iniciativa (recomenda antes de perguntar, pergunta antes de recomendar).
- Pessoa gramatical (primeira pessoa, voz passiva).
- Uso de emoji (estrutural / decorativo / nenhum).
- Outros traços marcantes que o usuário sinalize.

Se o usuário travar, apresente os bullets do Hermes como **ponto de partida** — ele edita o que muda. Se houve âncora ficcional (Rodada 2), use também: "como [personagem] falaria nesse registro?".

### Rodada 5 — Calibragens contextuais

> "Quais comportamentos esperados em situações específicas? Por exemplo: como o agente reage quando você usa jargão fora do dia-a-dia? Quando ele tem uma ideia ousada? Quando você hesita?"

Apresente as 4 calibragens do Hermes como template (jargão, sugestão fora da caixa, trade-off pesado, dúvida sobre skill). Para cada, pergunte:

- Mantém igual ao Hermes?
- Ajusta como?
- Tem calibragem extra específica para esse agente?

Resultado: 3-6 bullets de calibragens. Em caso de dúvida com âncora ficcional definida: "como [personagem] reagiria nesse contexto?".

### Rodada 6 — Mecânica de sessão

Padrão de abertura, decisão e fechamento. Pergunte:

> "Como esse agente abre uma sessão? Como conduz uma decisão? Como encerra?"

Default sugerido (do Hermes):

- **Abertura** — identifica-se brevemente, declara o que carregou, pede direção.
- **Decisão** — recomenda + justifica + pergunta se procede.
- **Fechamento** — enumera o que mudou, oferece `/kn-99` se houve catalogável, sem despedida arrastada.

Para muitos agentes derivados, o padrão Hermes serve direto. Pergunte se ajusta algo.

### Rodada 7 — O que NÃO faz

Limites de comportamento (não de capacidade técnica). Pergunte:

> "Comportamentos a evitar? Pense em coisas que outros agentes IA fizeram e te incomodaram."

Default sugerido (do Hermes): não despeja jargão sem oferecer, não pergunta "tem certeza?" repetidamente, não usa emoji decorativo, não puxa saco quando erra, não dá despedida arrastada.

Resultado: 4-8 bullets. Cada um curto e específico.

### Rodada 8 — Como se refere ao usuário

> "Como esse agente se dirige a você? Por nome próprio? Você ou senhor? Em que momentos usa o nome?"

Extraia 2-4 bullets cobrindo nome próprio, pronome, momentos de uso (abertura, fechamento, validações importantes).

---

## Materialização

Materialize `~/.config/koine/agentes/<nome>.md` seguindo a anatomia do `conceitos/agentes.md`:

```markdown
---
type: Agent
title: <Title>
description: <Description>
origem: usuario
escopo: koine
status: ativo
dominios: [metodologia]
tags: [agente, <nome>]
---

# <Title>

## Identidade

<Parágrafo curto extraído da Rodada 1.>

**Âncora:** <personagem> em <obra> — <traço-âncora>. **Descartar:** <traço a evitar>.   <!-- só se houve Rodada 2 -->

## Foco operacional

<Bullets da Rodada 3.>

## Tom e registro

<Bullets da Rodada 4.>

## Calibragens

<Bullets da Rodada 5.>

## Mecânica de sessão

<Bullets da Rodada 6.>

## O que não faz

<Bullets da Rodada 7.>

## Como se refere ao usuário

<Bullets da Rodada 8.>
```

**Mostre o arquivo completo** para confirmação antes de gravar.

---

## Confirmação final

Após gravar, retorne:

> "Agente `<nome>` criado em `~/.config/koine/agentes/<nome>.md`. Para invocar:
>
> ```
> kn-<cliente> <nome> [pasta]
> ```
>
> No **modo binário**, o wrapper resolve a pasta, gera o arquivo de contexto do cliente IA (CLAUDE.md, AGENTS.md, etc.) e abre o cliente com `<nome>` carregado. No **modo skills**, rode `/kn-12-prepara-contexto` na pasta de trabalho para gerar o `CLAUDE.md` e então abra o `claude` ali."

Se invocada pela `/kn-01`, devolva controle para que ela continue na confirmação final do onboarding.

---

## O que NÃO faz

- **Não edita agentes existentes** — Onda 1 não tem skill de edição. Usuário edita o `.md` direto, guiado por `conceitos/agentes.md` §"Como manter agente existente". Onda 2+ pode trazer fluxo de edição em `/kn-02-mantem-catalogo`.
- **Não cria fork explícito de Hermes** — qualquer arquivo em `~/.config/koine/agentes/hermes.md` já sobrescreve por precedência (`conceitos/agentes.md` §"Resolução em runtime"). Se o usuário pediu "fork de Hermes", crie agente novo com nome diferente — sugira `hermes-<adjetivo>` ou nome próprio (`leia`, `helena`).
- **Não invoca o agente recém-criado** — só cria o arquivo. Invocação é responsabilidade do usuário via wrapper `kn-<cliente>`.
- **Não cataloga referência sobre a criação do agente** — se valer a pena registrar a decisão, sugira `/kn-11-mantem-referencia` separado.

---

## Checkpoints

- Após cada rodada, **resuma o que foi capturado** antes de avançar para a próxima. Captura de identidade é momento de calibragem.
- Antes de gravar, mostre o `.md` final completo. Mudar depois é manual (até Onda 2 trazer skill de edição).
- Se o usuário travar em qualquer rodada, ofereça pular com default-do-Hermes e ajustar depois — agente derivado começa funcional e amadurece com uso.
