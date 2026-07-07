---
name: kn-12-prepara-contexto
description: Gera CLAUDE.md e índices kn-indice-<dominio>.md na pasta de trabalho sem o binário kn-agente — replica a resolução de contexto e a geração de artefatos do wrapper. Invocada ao fim do /kn-01-recebe-usuario e ad-hoc para regenerar após catalogar referências. Modo skills, Claude Code.
id: 202607071600
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-12, prepara-contexto, harness, claude-code, modo-skills, dual-mode]
---

# kn-12-prepara-contexto

Gera, **sem o binário `kn-agente`**, os dois artefatos que o wrapper produziria na pasta de trabalho: os índices `kn-indice-<dominio>.md` na pasta-referências do escopo, e o `CLAUDE.md` da pasta de trabalho com os `@path` do contexto canônico. É o motor do **modo skills** — no modo binário, quem faz isso é o `kn-agente`.

Produz artefato **equivalente** ao do binário. É essa paridade que faz os dois modos coexistirem sem conflito.

## Quando roda

- Chamada pela `/kn-01-recebe-usuario` ao final do onboarding, para a primeira pasta de trabalho.
- Ad-hoc, quando o usuário catalogou referências (via `/kn-11`) e quer regenerar os índices e o `CLAUDE.md` da pasta atual.

## Pré-condições

- Sessão aberta numa **pasta de trabalho com `CONTEXTO.md`** que declara um escopo real (não bootstrap).
- Conteúdo Koine instalado em disco (via `instalar-koine.bat` ou guia): `~/.local/share/koine/KOINE.md`, `~/.local/share/koine/agentes/`, `~/.config/koine/escopos/`, `~/.config/koine/dominios/`.

Se o `CONTEXTO.md` tiver `bootstrap: true`, **não rode** — a pasta ainda não tem escopo; direcione para `/kn-01-recebe-usuario`.

## Etapa 1 — Resolução de contexto (replica a ordem do wrapper)

Resolva, **nesta ordem** — cada passo alimenta o seguinte (espelha `contexto.Resolver`):

1. **Descubra o HOME.** Rode `echo $HOME` (Unix) — em Windows, `echo %USERPROFILE%`. Guarde como `HOME`. Todos os `@path` do `CLAUDE.md` serão absolutos a partir daqui.
2. **Leia o `CONTEXTO.md`** da pasta corrente. Do frontmatter, extraia **dois** campos: `escopo:` (slug, string) e `dominios:` (lista). Ambos são obrigatórios fora de bootstrap — se qualquer um faltar ou estiver vazio, **pare e reporte** (o binário erra igual). Os **domínios declarados são exatamente essa lista `dominios:` do CONTEXTO.md** — não derivam do escopo nem das referências.
3. **Resolva o arquivo de escopo:** `HOME/.config/koine/escopos/<slug-escopo>.md`. Dele leia **apenas** `pasta-referencias:` — um *tagged path* que aceita **só** dois prefixos: `home:<rel>` → `HOME/<rel>`, ou `abs:<path>` → `<path>` literal (tem que ser absoluto). **Path sem prefixo é erro** — não adivinhe. (O escopo não tem campo `dominios:`; não o procure lá.)
4. **Localize o arquivo do usuário:** o único `.md` na raiz de `HOME/.config/koine/`.
5. **Resolva o agente:** o nome do agente da sessão. Precedência: se existir `HOME/.config/koine/agentes/<agente>.md`, use-o; senão `HOME/.local/share/koine/agentes/<agente>.md`.
6. **Monte os paths de índice:** um por domínio declarado, na ordem da lista `dominios:` do CONTEXTO.md — `<pasta-referencias>/kn-indice-<dominio>.md`.

Se qualquer arquivo obrigatório faltar (escopo, usuário, KOINE.md, agente), **pare e reporte** exatamente qual — não gere artefato parcial.

## Etapa 2 — Geração

### Índices `kn-indice-<dominio>.md`

Gere um índice para **cada domínio da lista `dominios:` do CONTEXTO.md** (resolvida na Etapa 1) — e **só** para esses. Referência cujo `dominios` não casa com nenhum domínio declarado não gera índice novo (ver edge case). Para cada domínio declarado:

1. Varra a `pasta-referencias` recursivamente. Ignore diretórios que começam com `.`. Na raiz da pasta, ignore `index.md`, `log.md` e arquivos que já começam com `kn-indice-`.
2. Para cada `.md`, leia o frontmatter. Se não tiver frontmatter, registre para o aviso final e pule.
3. Se o campo `dominios:` da referência **contém** o domínio corrente, inclua a entrada: o `path` relativo à `pasta-referencias` (com `/`) e a `description` do frontmatter.
4. Ordene as entradas por `path` ascendente (ordenação estável, idêntica à do binário).
5. Leia a `sinopse` do domínio em `HOME/.config/koine/dominios/<dominio>.md` (campo `sinopse:` do frontmatter). Se o arquivo não existir ou não tiver `sinopse`, use o texto de fallback (ver formato).
6. Materialize `<pasta-referencias>/kn-indice-<dominio>.md` no formato exato abaixo.

**Formato exato do índice** (idêntico ao `escreverIndice` do binário):

```
---
tipo: indice
dominio: <dominio>
gerado: <timestamp UTC RFC3339>
entradas: <N>
---

## Domínio

<sinopse>
## Entradas catalogadas no escopo

- `<path>` — <description>
- `<path>` — <description>
```

- Se `description` for vazia: `- \`<path>\`` (sem o `— `).
- Se não houver entradas: em vez da lista, escreva `_Nenhuma referência catalogada neste domínio._`.
- Fallback de sinopse ausente: `_Domínio \`<dominio>\` não plantado. Rode \`kn-agente instalar\` ou \`/kn-02-mantem-catalogo\` (fluxo dominio)._`

### Arquivo `CLAUDE.md` da pasta de trabalho

Materialize `<pasta-de-trabalho>/CLAUDE.md` no formato exato abaixo — primeira linha é o marcador, seguido do corpo:

```
<!-- gerado por kn-agente -->
# CLAUDE.md
*Gerado por kn-agente em <timestamp UTC RFC3339>. Não editar — regerar com `/kn-12-prepara-contexto`.*

@<HOME/.config/koine/<usuario>.md>
@<HOME/.local/share/koine/KOINE.md>
@<AgentePath resolvido na Etapa 1.5>
@<HOME/.config/koine/escopos/<slug-escopo>.md>
@<pasta-referencias>/kn-indice-<dom1>.md
@<pasta-referencias>/kn-indice-<dom2>.md
@<pasta-de-trabalho>/CONTEXTO.md
```

- Uma linha `@<...>/kn-indice-<dom>.md` por domínio declarado, na ordem dos domínios.
- Todos os `@path` são **absolutos** (começam com o `HOME` real).
- O marcador `<!-- gerado por kn-agente -->` é obrigatório e idêntico — é o que a detecção de conflito procura.

## Determinismo (obrigatório)

- **`description` é copiada verbatim** do frontmatter da referência. Proibido parafrasear, resumir, traduzir ou reescrever.
- **Ordenação estável:** entradas por `path` ascendente; domínios na ordem em que o escopo os declara.
- Não invente entradas, domínios nem descrições.

## Auto-auditoria (rode ao final e reporte)

1. **Cobertura:** conte os `.md` elegíveis na `pasta-referencias`. Confirme que cada um foi **indexado** (entrou em ≥1 índice) **ou** **reportado** (sem frontmatter, ou `dominios` não casou com nenhum domínio declarado). A soma tem que bater. Liste os não-casados.
2. **Verbatim:** confirme que cada `description` no índice é idêntica à do frontmatter de origem.
3. **Resolução de `@path`:** confirme que cada `@path` escrito no `CLAUDE.md` aponta para um arquivo que existe em disco.

Reporte o resultado das três checagens ao usuário. Qualquer falha é explicitada — nunca silenciada.

## O que NÃO faz

- **Não edita** referências, escopo, domínios, arquivo do usuário nem agente — só gera índices e `CLAUDE.md`.
- **Não lança** o cliente IA — o usuário abre `claude` na pasta.
- **Não sobe** na árvore de diretórios — opera só na pasta corrente e na pasta-referências do escopo dela.
- **Não roda** em pasta bootstrap (`bootstrap: true`) — direciona para `/kn-01`.
