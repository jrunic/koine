---
name: kn-01-recebe-usuario
description: Onboarding completo do novo usuário Koine — meta-skill orquestra arquivo do usuário, primeiro escopo, primeiro contexto de pasta de trabalho e agente operacional derivado. Roda uma única vez por usuário.
id: 202606221400
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-01, onboarding, hermes, recebe-usuario]
---

# kn-01-recebe-usuario

Meta-skill que conduz o **primeiro contato do usuário com Koine**. Orquestra 4 rodadas de entrevista, materializa todos os arquivos canônicos da instalação e entrega o usuário pronto para invocar seu próprio agente operacional.

**Roda 1×/usuário.** Após esta sessão, manutenções pontuais usam `/kn-02-mantem-catalogo` ou `/kn-03-cria-agente` individualmente.

---

## Pré-condições

- `kn-agente instalar` já executado (vault em `~/.local/share/koine/` + sementes de domínio em `~/.config/koine/dominios/`).
- `kn-agente instalar-habilidades --para=<harness>` já executado (skills `kn-*` symlinkadas no harness ativo).
- Pasta `~/.config/koine/` existe mas não tem arquivo do usuário (`<nome>.md` na raiz).

Se `~/.config/koine/` já tem arquivo do usuário, esta skill **não roda** — onboarding já foi feito. Use `/kn-02-mantem-catalogo` para atualizações.

---

## Conceitos referenciados

Carregue sob demanda antes das rodadas correspondentes:

- `~/.local/share/koine/conceitos/escopos.md` (antes da Rodada 2)
- `~/.local/share/koine/conceitos/dominios.md` (antes da Rodada 3)
- `~/.local/share/koine/conceitos/agentes.md` (antes da Rodada 4)

---

## Roteiro

### Apresentação

Hermes se apresenta e explica o que vai acontecer. Tom: calmo, executivo, sem urgência.

> "Bem-vindo ao Koine. Eu sou o Hermes — sou o agente que vai te receber e configurar tudo. Vamos passar por 4 rodadas curtas: seu perfil de usuário, seu primeiro escopo de trabalho, sua primeira pasta de trabalho, e a criação do seu agente operacional — aquele que vai te acompanhar no dia a dia. Antes de começar: como você gostaria que eu te chamasse?"

Aguarde o nome. Use desde a próxima fala.

---

### Rodada 1 — Arquivo do usuário

Explique antes de perguntar:

> "Primeiro vou montar seu arquivo de usuário. Esse arquivo carrega em toda sessão Koine e diz a qualquer agente quem é você e como falar com você."

Faça as perguntas **uma de cada vez**, aguardando resposta antes de avançar.

1. **Nome completo** — para referência formal quando necessário.
2. **Idioma de comunicação preferido** — pt-BR, en-US, es-ES, etc.
3. **Timezone** — ex: America/Sao_Paulo, America/Cuiaba, America/New_York.
4. **Papel principal** — o que você faz hoje? Em uma ou duas frases.
5. **Estilo de comunicação preferido** — formal, direto, técnico, didático? Algum agente que já experimentou e gostou da forma de falar?
6. **Background curto** — algo que ajude o agente a te conhecer? (formação, anos de experiência, interesses transversais)

Materialize ao final: `~/.config/koine/<nome>.md` (Ficha Koine).

Estrutura sugerida:

```markdown
---
type: User
title: <Nome próprio escolhido>
description: <1 linha>
nome: <Nome completo>
idioma: <pt-BR | en-US | ...>
timezone: <America/Sao_Paulo | ...>
papel: <papel principal>
estilo: <estilo de comunicação preferido>
dominios: [universal]
tags: [usuario, <slug-nome>]
---

# <Nome>

<Background narrativo curto — contexto que ajude o agente a entender quem é o usuário.>
```

Mostre o arquivo para confirmação antes de gravar.

---

### Rodada 2 — Primeiro escopo (escopo geral)

Carregue `~/.local/share/koine/conceitos/escopos.md` antes de começar. Explique:

> "Agora vamos definir seu primeiro escopo — o escopo geral, onde você passa a maior parte do tempo. Pode ser sua atividade central, sua empresa, seu papel principal. Você pode criar outros escopos depois (para clientes, projetos grandes, vida pessoal), mas o primeiro é o seu ponto de entrada."

Perguntas:

1. **Slug do escopo** — nome curto em kebab-case. Sugestões para o escopo geral: `geral` (default neutro), seu primeiro nome (`<seunome>`), ou o nome da sua atividade/empresa principal (`<nome-empresa>`). Evite combinações longas — escopo geral deve ter nome simples e único.
2. **Descrição em 1 linha** — o que esse escopo cobre.
3. **Pasta-referências** — onde mora a memória de longa duração desse escopo. Default sugerido: `home:koine/<slug-escopo>`. Pode ser absoluto se for compartilhado em equipe (`abs:/caminho/compartilhado`).
4. **Dinâmica do escopo** — quem são os stakeholders principais (sócios, parceiros, chefia, time)? Qual o foco operacional? Curto parágrafo.

Materialize:

- `~/.config/koine/escopos/<slug-escopo>.md` com frontmatter (`pasta-referencias` tagged path, `proprietario`) + corpo narrativo da dinâmica.
- Cria a pasta-referências (resolvendo o tagged path) com:
  - `index.md` — contrato OKF (directory listing inicial)
  - `log.md` — contrato OKF (entrada inicial: "Initialization — <data>")

Mostre o arquivo do escopo + estrutura criada para confirmação.

---

### Rodada 3 — Primeira pasta de trabalho

Carregue `~/.local/share/koine/conceitos/dominios.md` antes de começar. Explique:

> "Agora vamos configurar sua primeira pasta de trabalho — uma pasta real no seu computador onde você efetivamente trabalha em algo. Pode ser um repositório de código, uma pasta de projeto, uma área de exploração. Vou criar um CONTEXTO.md ali, que conecta a pasta ao escopo que acabamos de criar."

Perguntas:

1. **Pasta** — qual pasta? Path absoluto ou relativo. Se não existe, criamos.

**Inspecione a pasta antes de prosseguir.** Ao receber o path, examine o conteúdo:

- É um repositório git? (`.git/` presente)
- Tem indicadores de stack técnica? (`package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml`, `pom.xml`, etc.)
- Tem README, docs, ou documentação visível?
- Tem outros arquivos `CONTEXTO.md` ou estrutura Koine pré-existente?

Use a inspeção para:
- **Confirmar** com o usuário a natureza da pasta antes de continuar ("Vejo que é um repositório Go com módulo `github.com/<...>` — é o trabalho deste escopo?").
- **Sugerir domínios** apropriados (pasta com `go.mod` → sugerir `[universal, tecnologia]`; pasta com docs/contratos → `[universal, negocio]`).
- **Detectar conflito** se já houver `CONTEXTO.md` — **leia o arquivo na íntegra imediatamente**. Não aborte sem mostrar ao usuário o que encontrou. Apresente o conteúdo existente, confirme se é atualização, e só então redirecione para `/kn-02-mantem-catalogo` (Sub-fluxo 3b). O conteúdo existente é o ponto de partida — não descarte, não reescreva do zero.

2. **Descrição da pasta** — 1 linha sobre o que esse trabalho é (use a inspeção como ponto de partida da pergunta, não como assunção).
3. **Domínios relevantes** — quais lentes carregam referências nesta pasta? Apresente a sugestão derivada da inspeção e abra para ajuste:
   - Pasta com indicadores técnicos (`go.mod`, `package.json`, etc.) → sugira `[universal, tecnologia]`
   - Pasta com documentos, contratos, processos → sugira `[universal, negocio]`
   - Pasta sem indicadores claros → pergunte sem sugerir, oferecendo `[universal]` como mínimo seguro
   - Pode combinar (`[universal, negocio, tecnologia]`).

Materialize: `<pasta>/CONTEXTO.md` com Ficha Koine declarando `escopo: <slug-escopo>` e `dominios: [...]` + corpo narrativo curto descrevendo o foco da pasta.

Inclua nota explícita no corpo:

> Esta pasta também acumula padrões, decisões e referências de alcance de pasta. Atualize ao longo do uso — o agente Koine trata CONTEXTO.md como memória entre sessões.

Não pré-crie seção "Referências locais" vazia — surge quando a primeira referência local for adicionada (via `/kn-99` ou `/kn-11`).

Mostre o arquivo para confirmação.

---

### Rodada 4 — Agente operacional

Carregue `~/.local/share/koine/conceitos/agentes.md` antes de começar. Explique:

> "Última rodada. Eu, Hermes, sou focado em operar o método Koine — receber você, configurar a estrutura, criar outros agentes. Mas o trabalho do dia a dia pede um agente próprio, com voz e foco específicos para o que você faz. Vou agora invocar a skill `/kn-03-cria-agente` para criarmos seu agente operacional."

Invoque `/kn-03-cria-agente`. A skill conduz a entrevista (nome, voz, tom, foco operacional, calibragens) e materializa `~/.config/koine/agentes/<nome>.md`.

Quando `/kn-03-cria-agente` retornar, valide com o usuário que o arquivo foi criado corretamente.

---

### Confirmação final

Apresente resumo do que foi criado:

> "Pronto. Você está com o Koine configurado. Resumo:
>
> - **Arquivo do usuário:** `~/.config/koine/<nome>.md`
> - **Primeiro escopo:** `<slug-escopo>` em `~/.config/koine/escopos/<slug-escopo>.md`
> - **Pasta-referências do escopo:** `<path resolvido>`
> - **Primeira pasta de trabalho:** `<path>` com `CONTEXTO.md` declarando escopo e domínios
> - **Agente operacional:** `<nome>` em `~/.config/koine/agentes/<nome>.md`
>
> Para começar a trabalhar, invoque seu agente no cliente IA escolhido. A sintaxe é `kn-<cliente> <agente> [pasta]` — um wrapper por cliente IA suportado:
>
> ```
> kn-claude <nome-do-agente>            # usa a pasta atual
> kn-claude <nome-do-agente> <pasta>    # pasta explícita: path, alias salvo, ou fuzzy match
> ```
>
> Outros wrappers conforme o cliente: `kn-copilot`, `kn-gemini`, etc. (chegam em ondas seguintes).
>
> O wrapper gera o arquivo de contexto do cliente (CLAUDE.md, AGENTS.md, etc.) com tudo que configuramos, e abre o cliente já com contexto carregado.
>
> Se em algum momento quiser ajustar algo, use `/kn-02-mantem-catalogo`. Se quiser criar outros agentes para outros tipos de trabalho, use `/kn-03-cria-agente`. Para encerrar uma sessão registrando aprendizados, `/kn-99-encerra-sessao`.
>
> Bem-vindo."

---

## O que NÃO faz

- **Não cria múltiplos escopos** — só o primeiro. Outros entram via `/kn-02-mantem-catalogo` (fluxo escopo) conforme aparece a necessidade.
- **Não cria múltiplos agentes** — só o primeiro operacional. Outros via `/kn-03-cria-agente`.
- **Não cataloga referências** — pasta-referências nasce vazia (só `index.md` + `log.md`). Catalogação começa via `/kn-11-mantem-referencia` durante o trabalho real.
- **Não configura cliente IA específico** — assume que `kn-agente instalar-habilidades --para=<harness>` já foi executado antes desta skill rodar.
- **Não roda duas vezes** — se detectar arquivo do usuário existente, recusa e direciona para `/kn-02-mantem-catalogo`.

---

## Checkpoints intermediários

Entre cada rodada, **pause e confirme** com o usuário antes de avançar. Onboarding é momento de calibragem — o agente lê se o usuário está confortável com o ritmo ou se precisa pausar.

Em qualquer rodada, se o usuário travar ou pedir tempo, ofereça encerrar e retomar depois com `/kn-02-mantem-catalogo` (fluxos individuais) — onboarding completo não é obrigatório em uma sessão única, mas é o caminho mais coerente.
