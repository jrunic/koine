---
name: kn-02-mantem-catalogo
description: Manutenção pontual da estrutura Koine — quatro fluxos individuais (arquivo do usuário, escopo, contexto de pasta de trabalho, domínio do usuário). Detecta cria vs atualiza pelo estado em disco. Substitui rodadas individuais do onboarding quando precisar ajustar algo isolado.
id: 202606222000
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-02, catalogo, manutencao, escopo, dominio, contexto, usuario]
---

# kn-02-mantem-catalogo

Skill de manutenção da estrutura Koine no `~/.config/koine/`. Quatro fluxos individuais que o usuário invoca quando precisa criar ou ajustar uma peça isolada — sem passar pelo onboarding inteiro de novo.

Use após o onboarding (`/kn-01-recebe-usuario`). Cobre o que muda na vida do usuário ao longo do tempo: ganha-se um novo cliente (escopo novo), abre-se um novo projeto dentro de um cliente (pasta de trabalho nova), o estilo de comunicação muda (arquivo do usuário), aparece uma área de atuação não coberta pelos canônicos (domínio novo).

---

## Pré-condições

- `/kn-01-recebe-usuario` já executado em algum momento — arquivo do usuário existe em `~/.config/koine/<nome>.md`. Se não existir, redirecione para `/kn-01-recebe-usuario` em vez de operar aqui.

---

## Conceitos referenciados

Carregue sob demanda **somente o conceito do fluxo escolhido** — não pré-carregue todos.

- Fluxo escopo → `~/.local/share/koine/conceitos/escopos.md`
- Fluxo contexto → `~/.local/share/koine/conceitos/escopos.md` + `~/.local/share/koine/conceitos/dominios.md`
- Fluxo domínio → `~/.local/share/koine/conceitos/dominios.md`
- Fluxo usuário → não tem conceito dedicado; usa o próprio arquivo do usuário existente como referência de estilo.

---

## Abertura — escolha do fluxo

Pergunte direto:

> "Qual fluxo? (1) Arquivo do usuário, (2) Escopo, (3) Pasta de trabalho (CONTEXTO), (4) Domínio."

Aguarde a escolha e despache para o fluxo correspondente. Cada fluxo abaixo é independente — termina e fecha a sessão.

---

## Fluxo 1 — Arquivo do usuário

Atualiza `~/.config/koine/<nome>.md` (criação é responsabilidade de `/kn-01`).

**Detecção de estado.** Localize o arquivo do usuário existente (único `.md` na raiz de `~/.config/koine/`). Se houver zero ou mais de um, abortar e direcionar para `/kn-01-recebe-usuario`.

**Description densa.** Se o usuário pedir para mudar `description`, lembre: description é a 1-linha que aparece em listagens e seleção (skills listam usuários, escopos, domínios, agentes pela description). Densa e específica > genérica.

**Entrevista de delta.** **Leia o arquivo do usuário na íntegra antes de qualquer pergunta.** Mostre o conteúdo ao usuário para confirmar que você leu. Só então pergunte:

> "Que campos quer ajustar? (idioma, timezone, papel, estilo, background, ou algum campo novo)"

Aguarde a lista de mudanças. Para cada campo, pergunte o valor novo. Não pré-suponha quais campos mudaram.

**Materialização.** Reescreva o arquivo preservando frontmatter inalterado nos campos não-tocados; aplique deltas; mostre diff resumido para confirmação antes de gravar.

---

## Fluxo 2 — Escopo

Cria escopo novo ou atualiza existente.

**Carregue `conceitos/escopos.md`** antes de continuar — doutrina sobre quando criar escopo, quando NÃO criar, anatomia.

**Detecção de cria vs atualiza.** Pergunte:

> "Vamos criar um escopo novo ou ajustar um existente?"

### Sub-fluxo 2a — criar escopo novo

Antes das perguntas, **valide o critério** com o usuário usando a heurística do `conceitos/escopos.md` (§"Quando criar um escopo novo"). Se o caso parecer mais um projeto curto ou subprojeto, redirecione para o Fluxo 3 (pasta de trabalho dentro de escopo existente) em vez de criar escopo.

Perguntas (uma por vez):

1. **Slug** — nome curto em kebab-case. Único — verifique colisão em `~/.config/koine/escopos/`.
2. **Descrição em 1 linha** — densa e específica (vai aparecer em listagens quando o usuário escolher escopo em outras skills). Evite genérico tipo "Escopo geral do usuário".
3. **Pasta-referências** — tagged path; default `home:koine/<slug-escopo>`.
4. **Dinâmica do escopo** — parágrafo curto descrevendo stakeholders, papel do usuário ali, foco operacional.

**Materialização:**

- `~/.config/koine/escopos/<slug>.md` com frontmatter (Ficha Koine, `pasta-referencias` tagged, `proprietario`, `escopo-pai: null`) + corpo narrativo.
- Cria a pasta-referências resolvendo o tagged path. Planta os contratos OKF na raiz:
  - `index.md` — directory listing inicial (vazio, com header indicando o escopo).
  - `log.md` — entrada inicial `AAAAMMDD — escopo criado via /kn-02 (fluxo escopo)`.

Mostre os 3 arquivos materializados para confirmação final.

### Sub-fluxo 2b — atualizar escopo existente

Liste os escopos atuais (lendo `~/.config/koine/escopos/*.md`). Pergunte qual ajustar.

**Leia o arquivo do escopo escolhido na íntegra antes de qualquer pergunta.** Mostre o conteúdo ao usuário para confirmar que você leu. Só então pergunte o delta:

> "Que parte ajustar? (descrição, pasta-referências, dinâmica, ou outro campo)"

**Cuidado especial com `pasta-referencias`.** Mudar o tagged path **não move o conteúdo**. Se o usuário quer relocar a pasta no filesystem, oriente a mover manualmente (Ação Documentada — gerar script) e só depois ajustar o tagged path no escopo.

Materialize com diff resumido. Adicione entrada no `log.md` da pasta-referências: `AAAAMMDD — escopo atualizado via /kn-02 — <campos>`.

---

## Fluxo 3 — Pasta de trabalho (CONTEXTO.md)

Cria `CONTEXTO.md` em pasta de trabalho nova ou ajusta existente.

**Carregue `conceitos/escopos.md` + `conceitos/dominios.md`** antes de continuar.

**Detecção de cria vs atualiza.** Pergunte o path da pasta. Inspecione: se já tem `CONTEXTO.md`, é atualiza; senão, é cria.

### Sub-fluxo 3a — criar CONTEXTO.md novo

**Inspecione a pasta** (mesma lógica de `/kn-01` Rodada 3):

- Repositório git? Stack técnica? Docs? Estrutura pré-existente?

Use a inspeção para sugerir domínios e abrir a conversa com base no real.

Perguntas:

1. **Escopo** — liste os escopos disponíveis em `~/.config/koine/escopos/`; usuário escolhe. Se nenhum encaixar, redirecionar para Fluxo 2a (criar escopo) antes.
2. **Descrição da pasta** — 1 linha; use a inspeção como ponto de partida.
3. **Domínios relevantes** — apresente sugestão derivada da inspeção, abra para ajuste. `[universal]` é o mínimo seguro.

**Materialização:** `<pasta>/CONTEXTO.md` com Ficha Koine (`escopo:`, `dominios: [...]`) + corpo narrativo curto. Inclua nota explícita: *"Esta pasta também acumula padrões, decisões e referências de alcance de pasta. Atualize ao longo do uso — o agente Koine trata CONTEXTO.md como memória entre sessões."* Não pré-crie seção "Referências locais" vazia — surge quando a primeira referência local for adicionada. Mostre para confirmação.

### Sub-fluxo 3b — atualizar CONTEXTO.md existente

**Leia o CONTEXTO.md existente na íntegra antes de qualquer pergunta.** O conteúdo existente é o ponto de partida — não descarte, não reescreva do zero. Mostre o arquivo atual ao usuário para confirmar que você leu. Só então pergunte o delta:

> "Que parte ajustar? (descrição, escopo, domínios, corpo)"

**Mudar `escopo:` é raro e impactante** — significa que a pasta migra de área de atuação. Confirme o motivo antes; revisa também se domínios fazem sentido no escopo novo.

**Adicionar domínio** é a operação mais comum aqui (aparece área de utilidade que não era declarada). Adicionar é seguro; remover deve perguntar "tem certeza?" — referências catalogadas naquele domínio param de aparecer no contexto desta pasta.

Materialize com diff. Não há `log.md` por pasta de trabalho — mudanças vivem no git da pasta (se houver) ou no diário da própria sessão.

---

## Fluxo 4 — Domínio

Cria domínio do usuário (`origem: usuario`) ou atualiza existente.

**Carregue `conceitos/dominios.md`** antes de continuar.

**Detecção de cria vs atualiza.** Pergunte:

> "Vamos criar um domínio novo ou ajustar um existente?"

### Sub-fluxo 4a — criar domínio do usuário

Antes das perguntas, **valide a necessidade**. Domínios canônicos (`universal`, `negocio`, `tecnologia`, `pessoal`) cobrem a maioria dos casos. Pergunte:

> "Que tipo de referência você está tentando catalogar que não cabe bem em `universal`, `negocio`, `tecnologia` ou `pessoal`? Me dê 2-3 exemplos concretos."

Se os exemplos couberem nos canônicos, oriente classificação ali e encerre. Domínio novo só faz sentido com dor recorrente.

Perguntas:

1. **Slug** — kebab-case. Verifique colisão em `~/.config/koine/dominios/`.
2. **Title** — nome legível.
3. **Description em 1 linha** — densa (aparece em listagens quando o usuário escolher domínio em `/kn-11` e em outras skills).
4. **Sinopse** — 1-3 frases que vão para runtime via `kn-indice`. Carrega a essência do "cabe / não cabe" em frases curtas.
5. **Corpo denso** — sob entrevista, monte as 5 seções canônicas: O que cobre / Quando catalogar aqui / Quando NÃO cabe / Campos recomendados / Edge cases / Exemplos.

**Materialização:** `~/.config/koine/dominios/<slug>.md` com Ficha Koine (`type: Domain`, `origem: usuario`, `sinopse: ...`) + corpo. Mostre para confirmação.

### Sub-fluxo 4b — atualizar domínio existente

Liste os domínios atuais (`~/.config/koine/dominios/*.md`). Pergunte qual ajustar.

**Leia o arquivo do domínio escolhido na íntegra antes de qualquer pergunta.** Mostre o conteúdo ao usuário para confirmar que você leu.

**Distinção crítica — canônico vs usuário.** Inspecione `origem:` no frontmatter:

- `origem: koine-canonico` — **não editar diretamente**. Domínios canônicos evoluem com `kn-agente atualizar` (Onda 2+). Ofereça: criar variante do usuário (`origem: usuario`) com slug próximo, ou abrir tarefa para ajustar o canônico no método.
- `origem: usuario` — editar livremente.

Para domínio do usuário, pergunte o delta. **Mudar sinopse afeta runtime** (é embutida no header de todo `kn-indice` daquele domínio na próxima invocação do `kn-agente`). Confirmação extra.

Materialize com diff. Renomear slug é caro — quebra referências cruzadas; só renomear quando o slug original ficou enganoso.

---

## O que NÃO faz

- **Não cria arquivo do usuário** — só atualiza. Criação é exclusivamente do `/kn-01-recebe-usuario`.
- **Não cataloga referências** — isso é `/kn-11-mantem-referencia`. Aqui só se mantém a estrutura.
- **Não cria agentes operacionais** — isso é `/kn-03-cria-agente`.
- **Não edita domínios canônicos** — sempre redireciona para variante do usuário.
- **Não encerra sessão** — fecha o fluxo e devolve controle. Encerramento é `/kn-99-encerra-sessao`.
- **Não roda múltiplos fluxos numa invocação** — uma invocação, um fluxo. Se o usuário precisa de mais, invoque `/kn-02` de novo.

---

## Checkpoints

- Antes de gravar qualquer arquivo, **mostre o conteúdo final** (cria) ou **diff resumido** (atualiza) e peça confirmação.
- Para criações que materializam múltiplos artefatos (Sub-fluxo 2a cria 3 arquivos), liste todos antes de gravar.
- Para mudanças destrutivas (remover domínio de CONTEXTO.md, mudar escopo de uma pasta, alterar sinopse de domínio), confirmação explícita.
