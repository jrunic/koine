---
id: 202606271400
tipo: decisao
status: aceito
description: ADR — schema do CONTEXTO.md ganha campo opcional `bootstrap: bool` para sinalizar modo bootstrap explícito gerado por kn-agente instalar
tags: [adr, koine, contexto, schema, bootstrap, onboarding]
---

# ADR — Flag `bootstrap` no schema do CONTEXTO.md

## Status

Aceito.

## Contexto

`kn-agente instalar` cria uma pasta canônica para sessões com Hermes
(meta-trabalho com o método Koine). Essa pasta precisa de um arquivo
`CONTEXTO.md` para que `kn-claude hermes koine` (e equivalentes) abra
a sessão no fluxo "normal" do agente — não no modo bootstrap implícito
(que dispara quando o `CONTEXTO.md` está ausente).

Porém, o usuário recém-instalado ainda não tem escopo nem domínios
configurados. Precisamos de um estado intermediário onde:

1. O `CONTEXTO.md` exista (para o adapter carregar contexto normal).
2. O agente saiba que está em onboarding inicial e inicie `/kn-01`.
3. A validação de schema atual (`escopo` e `dominios` obrigatórios) seja
   bypassada para esse caso específico.

Alternativas consideradas:

- **Escopo seed `koine-onboarding`**: planta um escopo extra em
  `~/.config/koine/escopos/` + CONTEXTO.md aponta para ele. Mistura
  arquivos técnicos com arquivos do usuário; complica transição.
- **Confiar em prompt**: bootstrap implícito atual já existe; podemos
  enriquecer o conteúdo carregado para Hermes "decidir" iniciar `/kn-01`.
  Não-determinístico — depende do modelo lembrar; sem estado em código.
- **Flag no schema (escolhida)**: campo opcional `bootstrap: bool` em
  CONTEXTO.md. Quando presente e true, `Resolver()` bypassa validação
  de escopo/dominios. Determinístico, estado em código.

## Decisão

Adicionar campo opcional `bootstrap: bool` ao schema do `CONTEXTO.md`.
Semântica:

- Campo ausente ou `bootstrap: false` → comportamento atual; `escopo`
  e `dominios` obrigatórios; `Resolver()` valida normalmente.
- Campo `bootstrap: true` → `Resolver()` bypassa validação de escopo
  e dominios; retorna `ContextoMontado{Bootstrap: true, ContextoPath:
  <path>}` com `EscopoPath` e `IndicePaths` vazios. Agente forçado para
  Hermes; warning no stderr se invocação pediu agente diferente.

Schema retrocompatível: arquivos atuais sem o campo continuam funcionando.

## Consequências

- **Modo bootstrap explícito** é caminho determinístico para onboarding.
  `kn-agente instalar` gera `<pasta-canonica>/CONTEXTO.md` com este flag.
- **Adapters** precisam tratar `ContextoMontado{Bootstrap: true,
  ContextoPath: != ""}` — incluir o corpo do CONTEXTO.md no contexto
  carregado pelo cliente IA.
- **`/kn-01-recebe-usuario`** ao final do onboarding reescreve o
  CONTEXTO.md substituindo `bootstrap: true` por `escopo: koine` +
  `dominios: [...]` reais. A pasta canônica vira escopo permanente
  de meta-trabalho Koine.
- **Bootstrap implícito** (CONTEXTO.md ausente) permanece como caminho
  válido para pastas ad-hoc sem configuração.

## Referências

- Spec B1: `20260627-spec-instalar-pasta-canonica-bootstrap.md`
- ADR `20260620-contexto-md-local-sem-cascata.md` — CONTEXTO.md é local-only
- ADR `20260621-estrutura-config-koine.md` decisão 5 — Ficha Koine universal
