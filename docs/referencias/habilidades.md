---
descricao: Referência das 5 skills kn-* distribuídas no vault — propósito, trigger, quando invocar, o que produz
id: 202606280002
tipo: referencia
status: ativo
tags: [referencia, habilidades, skills, kn]
---

# Referência — Habilidades

## Visão geral

Koine distribui **5 skills** no vault (`vault/habilidades/kn-NN-*/SKILL.md`), instaladas em `~/.local/share/koine/habilidades/` pelo `koine instalar` e symlinkadas no harness ativo (ex: `~/.claude/skills/`).

Skills `kn-*` são **invocadas em sessões com Hermes** — o agente que opera o método Koine, presente na pasta canônica `~/koine` (alias `koine`). Agentes operacionais derivados (criados via `/kn-03-cria-agente`) normalmente **não** invocam skills `kn-*` — eles focam em trabalho real, não em manutenção do método.

> **Nota sobre paths:** este documento usa `~/` como atalho para HOME. Em Windows, `~` expande para `%USERPROFILE%` (ex: `~/.local/share/koine/` → `C:\Users\<você>\.local\share\koine\`). Convenção definida em ADR `20260621-estrutura-config-koine.md` (decisão 1 — XDG puro em todos os SOs).

## Numeração

Bloco numérico significa categoria de uso:

| Bloco | Categoria | Frequência |
|---|---|---|
| `kn-01` a `kn-09` | Jornada inicial + manutenção da estrutura Koine | Raro |
| `kn-11` a `kn-89` | Operações cotidianas durante o trabalho | Frequente |
| `kn-99` | Fechamento de sessão | Sempre por último |

Espaço entre blocos permite adicionar skills futuras sem renumeração cascata.

## Tabela compacta

| Skill | Trigger | Frequência | Propósito |
|---|---|---|---|
| **kn-01-recebe-usuario** | `/kn-01-recebe-usuario` | 1× por usuário | Onboarding inicial — configura arquivo do usuário, primeiro escopo, primeira pasta de trabalho, primeiro agente operacional |
| **kn-02-mantem-catalogo** | `/kn-02-mantem-catalogo` | Quando precisa criar/ajustar | Manutenção pontual da estrutura — 4 fluxos individuais (arquivo do usuário, escopo, contexto de pasta, domínio) |
| **kn-03-cria-agente** | `/kn-03-cria-agente` | Quando emerge tipo de sessão recorrente com voz distinta | Criar agente operacional derivado especializado em um tipo de trabalho |
| **kn-11-mantem-referencia** | `/kn-11-mantem-referencia` | Frequente — durante o trabalho real | Catalogar conhecimento (pessoa, decisão, aprendizado, evento) na pasta-referências do escopo atual |
| **kn-99-encerra-sessao** | `/kn-99-encerra-sessao` | Sempre, ao final da sessão | Sintetizar a sessão, escrever diário, distribuir aprendizados para os destinos canônicos |

---

## `kn-01-recebe-usuario`

**Roda 1× por usuário** — primeira sessão com Koine.

Meta-skill que conduz o primeiro contato do usuário com Koine. Orquestra 4 rodadas de entrevista, materializa todos os arquivos canônicos da instalação inicial e entrega o usuário pronto para invocar seu próprio agente operacional.

**Inputs:**
- Pasta canônica criada pelo `koine instalar` com `CONTEXTO.md` contendo `bootstrap: true`
- Sessão aberta com Hermes nessa pasta

**Outputs:**
- `~/.config/koine/<primeiro-nome>.md` (arquivo do usuário)
- `~/.config/koine/escopos/<apelido>.md` (primeiro escopo)
- `<pasta-de-trabalho>/CONTEXTO.md` (primeira pasta de trabalho real)
- `~/.config/koine/agentes/<nome>.md` (primeiro agente operacional)
- `~/.config/koine/escopos/koine.md` (escopo permanente da pasta canônica)
- `<pasta-canonica>/CONTEXTO.md` reescrito sem `bootstrap: true`

**Skills relacionadas:**
- `/kn-03-cria-agente` — invocada na Rodada 4 para criar o primeiro agente
- `/kn-02-mantem-catalogo` — para atualizações posteriores

**SKILL.md:** `~/.local/share/koine/habilidades/kn-01-recebe-usuario/SKILL.md`

---

## `kn-02-mantem-catalogo`

**Roda quando precisa criar ou ajustar uma peça isolada** da estrutura Koine.

Skill de manutenção. Quatro fluxos individuais que o usuário invoca quando precisa criar ou ajustar algo sem passar pelo onboarding inteiro de novo.

**Quando invocar:**
- Ganhou um novo cliente → criar novo escopo
- Abriu um novo projeto dentro de um escopo → criar nova pasta de trabalho com `CONTEXTO.md`
- Estilo de comunicação mudou → atualizar arquivo do usuário
- Apareceu área de atuação não coberta pelos domínios canônicos → criar domínio novo

**Inputs:**
- Onboarding inicial já completo (`/kn-01-recebe-usuario` rodado)
- Escolha do fluxo (1-4)

**Outputs (dependem do fluxo escolhido):**
- Fluxo 1 (arquivo do usuário) — atualiza `~/.config/koine/<nome>.md`
- Fluxo 2 (escopo) — cria/atualiza `~/.config/koine/escopos/<apelido>.md` + pasta de referências
- Fluxo 3 (contexto) — cria/atualiza `<pasta>/CONTEXTO.md` em nova pasta de trabalho
- Fluxo 4 (domínio) — cria `~/.config/koine/dominios/<dom>.md`

**Skills relacionadas:**
- `/kn-01-recebe-usuario` (pré-requisito)
- `/kn-03-cria-agente` (criação de agente é skill separada, não fluxo aqui)

**SKILL.md:** `~/.local/share/koine/habilidades/kn-02-mantem-catalogo/SKILL.md`

---

## `kn-03-cria-agente`

**Roda quando emerge tipo de sessão recorrente** com voz e calibragens distintas dos agentes existentes.

Cria um agente operacional derivado especializado em um tipo de trabalho (código, redação, coaching, análise financeira, gestão de agenda, etc.). Hermes opera o método; agentes derivados operam o trabalho.

**Quando invocar:**
- Pela `/kn-01-recebe-usuario` na rodada final (primeiro agente operacional)
- Diretamente quando você percebe que precisa de um agente novo com identidade própria

**Inputs:**
- Arquivo do usuário existente
- Compreensão do tipo de sessão que o agente conduzirá

**Outputs:**
- `~/.config/koine/agentes/<nome>.md` com 8 seções (identidade, âncora ficcional opcional, foco operacional, tom e registro, calibragens, mecânica de sessão, o que não faz, como se refere ao usuário)

**Processo (8 sub-rodadas):**
1. Identidade — nome humano, slug, descrição
2. Âncora ficcional (opcional) — personagem que captura o espírito
3. Foco operacional — tipos de sessão, skills favorecidas
4. Tom e registro — formal/direto/exploratório, idioma, tamanho
5. Calibragens — comportamento em situações específicas
6. Mecânica de sessão — abertura, decisão, fechamento
7. O que NÃO faz — limites de comportamento
8. Como se refere ao usuário — nome próprio, pronome, momentos de uso

**Skills relacionadas:**
- `/kn-01-recebe-usuario` (invoca na Rodada 4)
- `/kn-02-mantem-catalogo` (Onda 2+ pode trazer fluxo de edição)

**SKILL.md:** `~/.local/share/koine/habilidades/kn-03-cria-agente/SKILL.md`

---

## `kn-11-mantem-referencia`

**Skill mais frequente do dia-a-dia** — invocada durante o trabalho real quando aparece conhecimento que vale guardar para sessões futuras.

Cataloga ou atualiza referência na pasta-referências do escopo da sessão atual. Cada referência catalogada é um item que sessões futuras vão enxergar via `kn-indice-<dominio>.md` no contexto do agente.

**Quando invocar:**
- Apareceu pessoa nova relevante ao escopo
- Decisão foi tomada com motivação registrável
- Aprendizado generalizável surgiu
- Evento de impacto aconteceu
- Organização stakeholder entrou em cena

**Não use para:** anotação solta — isso é diário (`/kn-99-encerra-sessao`).

**Inputs:**
- Sessão ativa num escopo (com `CONTEXTO.md` válido)
- Slug da referência (gera ou atualiza)

**Outputs:**
- `<pasta-referencias>/<slug>.md` — arquivo da referência catalogada
- `<pasta-referencias>/index.md` atualizado
- `<pasta-referencias>/log.md` atualizado

**Skills relacionadas:**
- `/kn-99-encerra-sessao` (alternativa para anotações soltas)

**SKILL.md:** `~/.local/share/koine/habilidades/kn-11-mantem-referencia/SKILL.md`

---

## `kn-99-encerra-sessao`

**Última skill da sessão.** Ritual de fechamento que torna a sessão útil para o usuário do futuro.

Encerra uma sessão Koine — sintetiza o que aconteceu, escreve diário na pasta de trabalho, distribui aprendizados (referências, ajustes em escopo/domínio/agente, tarefas) para os destinos canônicos.

**Quando invocar:**
- Sempre ao final da sessão, antes de sair

**Inputs:**
- Sessão substantiva (conteúdo a sintetizar)

**Outputs:**
- `<pasta-de-trabalho>/diario/AAAAMMDD-<descricao>.md` (diário da sessão)
- Distribuição de aprendizados:
  - Referência nova → via `/kn-11-mantem-referencia`
  - Ajuste de escopo/domínio → via `/kn-02-mantem-catalogo`
  - Tarefa para outro agente ou usuário → registrada

**Skills relacionadas:**
- `/kn-11-mantem-referencia` (invocada para referências individuais)
- `/kn-02-mantem-catalogo` (invocada para ajustes na estrutura)

**SKILL.md:** `~/.local/share/koine/habilidades/kn-99-encerra-sessao/SKILL.md`

---

## Onde os SKILL.md vivem

Após `koine instalar`:

```
~/.local/share/koine/habilidades/
├── kn-01-recebe-usuario/SKILL.md
├── kn-02-mantem-catalogo/SKILL.md
├── kn-03-cria-agente/SKILL.md
├── kn-11-mantem-referencia/SKILL.md
└── kn-99-encerra-sessao/SKILL.md
```

E symlinks no harness ativo (ex: Claude Code):

```
~/.claude/skills/
├── kn-01-recebe-usuario → ~/.local/share/koine/habilidades/kn-01-recebe-usuario
├── kn-02-mantem-catalogo → ~/.local/share/koine/habilidades/kn-02-mantem-catalogo
└── (...)
```

Cliente IA descobre skills automaticamente.

## Referências

- [Tutorial — Onboarding completo](../tutoriais/onboarding-completo.md)
- [CLI](./cli.md) — comandos `koine` e wrappers
- ADR `20260621-estrutura-config-koine.md` (decisão 13) — família `kn-NN` com bloco numérico semântico
