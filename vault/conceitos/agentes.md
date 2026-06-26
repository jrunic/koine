---
type: Concept
title: Agentes
description: Doutrina meta sobre o que é agente no Koine — agente canônico vs derivado, anatomia do arquivo, resolução em runtime, ciclo de vida
origem: koine-canonico
dominios: [metodologia]
tags: [conceito, agente, metodologia]
---
# Conceito: Agentes

Doutrina sobre o que é agente no Koine, lida pela skill `/kn-03-cria-agente` quando precisa operar sobre agentes. Carregada sob demanda — não vai em runtime universal.

## O que é agente Koine

**Agente é a entidade que opera o método Koine em uma sessão de trabalho.** Cada sessão tem exatamente um agente, invocado pelo comando `kn-agente <nome> <pasta>`. O agente é definido por um arquivo `<nome>.md` que descreve sua identidade operacional: voz, tom, calibragens, foco operacional, mecânica de sessão.

O método Koine prevê dois tipos de agente, com propósitos distintos.

## Os dois tipos de agente

**Agente canônico — Hermes.** Distribuído pelo método. Vive em `~/.local/share/koine/agentes/hermes.md` (vault em disco, extraído do embed pelo `kn-agente instalar`). **Focado em operar o método Koine**: conduz onboarding, configura a estrutura, cria outros agentes, cataloga referências sobre o uso de Koine. Não foi desenhado para conduzir trabalho cotidiano do usuário (código, redação, análise) — esse é papel de agentes derivados.

**Agente operacional derivado.** Criado pelo usuário via `/kn-03-cria-agente` para servir tipos específicos de sessão. Vive em `~/.config/koine/agentes/<nome>.md` (config do usuário, writeable). **Focado em um tipo de trabalho cotidiano**: coaching executivo, análise financeira, revisão de contrato, código, redação, gestão de agenda.

**Capacidades técnicas são iguais entre todos os agentes na v1.** Todo agente Koine tem acesso ao mesmo conjunto de skills `kn-*`. A diferenciação é **comunicacional e de foco**, não de capacidade.

## Por que múltiplos agentes

Tentar uma única identidade que serve tudo dilui — cada cenário compromete o outro. Múltiplos agentes permitem:

- **Voz e tom diferentes por contexto** — coaching exige escuta paciente; análise financeira exige rigor numérico; trabalho de código exige direção técnica direta. A maneira de se comunicar é a diferenciação principal entre agentes.
- **Calibragens específicas** — agente assistindo alguém em processo de aprendizado explica mais; agente trabalhando com par sênior usa atalhos.
- **Foco preferencial** — Hermes tipicamente invoca `/kn-01`, `/kn-02`, `/kn-03` (meta-método); agente de redação tipicamente invoca `/kn-11-mantem-referencia` (cataloga aprendizado) e `/kn-99` (fecha sessão). Tecnicamente todos podem invocar tudo; na prática cada um privilegia o que sua especialidade pede.
- **Mecânica de sessão própria** — agente de redação abre diferente de agente de planejamento.

## Anatomia de um `agentes/<nome>.md`

Frontmatter (Ficha Koine):

```yaml
---
type: Agent
title: <Nome>
description: <1 linha — o que esse agente faz>
origem: koine-canonico | usuario
dominios: [metodologia]
tags: [agente, <nome>]
---
```

Corpo padrão (estrutura usada pelo Hermes — derivados podem seguir):

- **Identidade** — quem é o agente, qual seu foco
- **Foco operacional** — tipos de trabalho/sessão que o agente privilegia (não restringe acesso a skills, só sinaliza preferência de uso)
- **Tom e registro** — voz, formalidade, idioma, postura
- **Calibragens** — comportamentos contextuais (jargão técnico, sugestão fora-da-caixa, hesitação do usuário, dúvida sobre skill)
- **Mecânica de sessão** — abertura, decisão em curso, fechamento
- **O que não faz** — limites de comportamento (não de capacidade técnica)
- **Como se refere ao usuário** — nome próprio, pronomes, onboarding

## Onde vivem

Distribuição em 2 dos 3 lugares Koine:

| Tipo | Localização | Quem escreve |
|---|---|---|
| Canônico (Hermes) | `~/.local/share/koine/agentes/hermes.md` (vault em disco) | `kn-agente instalar` extrai do embed |
| Derivado | `~/.config/koine/agentes/<nome>.md` (config do usuário) | `/kn-03-cria-agente` materializa |

Vault tem só o canônico imutável; config tem tudo writeable. Mesma separação semântica usada para domínios.

## Resolução em runtime

Ao invocar `kn-agente <nome> <pasta>`, a resolução do arquivo do agente segue precedência:

1. **Primeiro busca** em `~/.config/koine/agentes/<nome>.md` (config do usuário) — derivado tem prioridade, e permite ao usuário criar fork local de qualquer nome.
2. **Fallback** em `~/.local/share/koine/agentes/<nome>.md` (vault) — onde mora o Hermes canônico.

Implicação: se o usuário cria `~/.config/koine/agentes/hermes.md`, esse fork sobrescreve o Hermes canônico em runtime. Trade-off consciente — dá ao usuário capacidade de customizar Hermes; custo é perda de sincronização com updates do método (re-merge manual após `kn-agente atualizar` no futuro).

## Como criar agente derivado novo

Operação rara — só quando aparece tipo de sessão recorrente com voz e calibragens distintas das do Hermes. Fluxo (detalhado em `/kn-03-cria-agente`):

1. **Identificar o tipo de trabalho** — qual sessão recorrente pede um agente diferente do Hermes? Coaching? Código? Análise financeira? Revisão de contrato?
2. **Definir a diferenciação comunicacional** — onde voz/tom precisa ser diferente da do Hermes? Que calibragens mudam? Qual foco operacional privilegia?
3. **Decidir base** — fork do Hermes (herda estrutura, ajusta tom/foco) ou from-scratch (estrutura nova). Default: fork — economiza redação e mantém coerência com o método.
4. **Entrevistar para extrair** — identidade, foco operacional, voz/tom específico, calibragens, mecânica, o que não faz.
5. **Materializar** — `~/.config/koine/agentes/<nome>.md` com `origem: usuario`.

Resista a criar agente para cada nuance — granularidade excessiva fragmenta o uso e dilui o sinal. Prefira ajustar agente existente quando a variação for pequena.

## Como manter agente existente

- **Atualizar calibragens** quando padrões de uso real revelam fricções (jargão que precisava explicação, sugestão que precisava permissão).
- **Refinar foco operacional** quando aparecem tipos de trabalho repetidos que valem ser explícitos.
- **Adicionar bullets em "O que não faz"** quando o agente derrapou em um caso e merece guardrail explícito.
- **Nunca renomear arbitrariamente** — agente é referenciado por nome em todas as invocações `kn-agente <nome> <pasta>`. Renomear quebra invocações e pastas de trabalho pré-configuradas.
- **Agente canônico (Hermes)** evolui com o método. Usuário não edita diretamente em vault. Para variante, cria fork em `~/.config/koine/agentes/hermes.md` (sobrescreve por precedência) ou agente novo com nome diferente.

## Edge cases

- **Fork de Hermes com mesmo nome** — possível, mas o fork perde sincronização com updates do método. Prefira agente derivado com nome diferente quando a customização não for completa.
- **Múltiplos agentes derivados ativos** — sem limite arquitetural. Usuário escolhe qual invocar a cada sessão. Não há "agente padrão" — invocação é sempre explícita.
- **Agente derivado precisa operar meta-método** (criar novo escopo, catalogar referência sobre Koine) — funciona, todos os agentes têm acesso às mesmas skills `kn-*`. Mas a sessão tende a fluir melhor se for conduzida pelo Hermes, que tem o foco operacional adequado.
- **Agente derivado sem identidade clara** — sintoma de criação prematura. Volta para Hermes e use enquanto a diferenciação não cristaliza.

## Para skills relacionadas

- `/kn-03-cria-agente` — usa este conceito para conduzir a criação de agente operacional derivado.
- (Onda 2+) `/kn-02-mantem-catalogo` poderá ganhar fluxo `agente` para editar agentes existentes. Hoje edição é manual pelo usuário.
