---
descricao: O que é Koine e por que existe — contexto de produto, motivação, posicionamento
id: 202606201921
tipo: referencia
status: ativo
tags: [contexto, koine, produto]
---

# Contexto — Koine

## O que é

Koine é uma CLI que injeta contexto multi-camada (usuário, agente, referências, contexto da pasta de trabalho) em harnesses de IA terminal — Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode, Codex CLI.

O nome vem do grego κοινή (koiné) — a "língua comum" do mundo helenístico, inteligível por todos. O objetivo é que qualquer usuário, independente de stack ou empresa, possa operar com agentes de IA que "já sabem" o contexto relevante.

## Por que existe

Agentes de IA terminal abrem cada sessão zeradas. O usuário precisa repetir, a cada turno, quem é, o que está fazendo, em que projeto trabalha, qual padrão da casa, qual contexto da pasta. Repetir contexto consome tempo, polui prompts e degrada qualidade da resposta.

Koine separa quatro camadas que costumam vir embaralhadas em sistemas de "memória de agente":

1. **Harness** (`kn-agente`) — baixa e configura, sem depender de Git ou autenticação adicional
2. **Habilidades** (skills `kn-*`) — ações assistidas pelo agente, não pelo usuário direto
3. **Base de conhecimento** — bundle OKF-conforme, propriedade do usuário
4. **Sistema de arquivos** — recomendado, não obrigatório

O usuário adota em escada: instala o harness, roda as skills, a base nasce. Não precisa entender o que é `CLAUDE.md` ou `go:embed` para começar.

## Formato OKF

A base de conhecimento segue o Open Knowledge Format (OKF v0.1, Google). Frontmatter em inglês para campos OKF-spec; extensões em PT-BR. Detalhes: ADR [`20260620-okf-conformance-e-frontmatter.md`](decisoes/20260620-okf-conformance-e-frontmatter.md).

## Posicionamento

Koine não é um chatbot, um assistente genérico ou um substituto de agente IA. É a **infraestrutura de contexto** que faz o agente IA "já saber" quem o usuário é, o que faz e onde está trabalhando — sem exigir que o usuário configure nada além de responder perguntas guiadas pelas skills.
