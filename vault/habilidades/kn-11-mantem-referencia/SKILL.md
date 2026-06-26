---
name: kn-11-mantem-referencia
description: Cataloga ou atualiza referência na pasta-referências do escopo da sessão atual. Operação cotidiana — invocada durante o trabalho real quando aparece conhecimento que vale guardar para sessões futuras. Detecta cria vs atualiza pelo slug; materializa <slug>.md + atualiza index.md e log.md.
id: 202606222200
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-11, referencia, catalogo, cotidiano, okf]
---

# kn-11-mantem-referencia

Cataloga conhecimento na **pasta-referências do escopo da sessão atual** — o lugar onde mora a memória de longa duração do usuário naquele escopo. É a skill mais frequente do dia-a-dia: cada referência catalogada é um item que sessões futuras vão enxergar via `kn-indice-<dominio>.md` no contexto do agente.

Invoque quando emerge algo que vale guardar além desta sessão: uma pessoa nova relevante ao escopo, uma decisão tomada com motivação registrável, um aprendizado generalizável, um evento de impacto, uma organização stakeholder. Não use para anotação solta — isso é diário (`/kn-99-encerra-sessao`).

---

## Pré-condições

- Sessão rodando em **pasta de trabalho com `CONTEXTO.md`** — o escopo é deduzido daí (`escopo:` no frontmatter). Se não houver `CONTEXTO.md`, redirecione para `/kn-02-mantem-catalogo` (Fluxo 3) para criar a pasta de trabalho antes.
- Escopo declarado em `CONTEXTO.md` resolve para `~/.config/koine/escopos/<slug>.md` e tem `pasta-referencias:` válida com `index.md` e `log.md` (contratos OKF). Se faltar, redirecione para `/kn-02-mantem-catalogo` (Fluxo 2b) para regularizar.

---

## Conceitos referenciados

Carregue **antes** de operar:

- `~/.local/share/koine/conceitos/referencias.md` — doutrina completa: agregado/unidade, anatomia da pasta-referências, Ficha Koine universal, tipos canônicos, multi-domínio, contratos OKF, ciclo de vida.
- `~/.local/share/koine/conceitos/dominios.md` — necessário para decidir o campo `dominios:` da referência.

---

## Roteiro

### Abertura — captura inicial

Pergunte o que está sendo catalogado:

> "O que vamos catalogar? Pode ser livre — pessoa, decisão, aprendizado, evento, organização. Me conta o essencial e a gente estrutura junto."

Aguarde a captura inicial em prosa livre. Não force estrutura ainda — escute.

A partir dessa captura, **proponha o `type`** (Pessoa, Organizacao, Decisao, Aprendizado, Evento, ou outro se nada encaixar) e o slug candidato (kebab-case do título). Confirme com o usuário antes de avançar.

### Checkpoint de alcance

Antes de continuar, **pergunte o alcance**:

> "Esta referência se aplica a outras pastas de trabalho deste escopo? (a) sim — outras pastas usam, vai para a pasta-referências do escopo; (b) não — só esta pasta."

`/kn-11` é a skill canônica para alcance de **escopo**. Se a resposta for (b), aviso e redirecionamento:

> "Para alcance de pasta, o canal natural é `/kn-99-encerra-sessao` ao final da sessão (que escreve direto no CONTEXTO.md desta pasta) ou pedir ao agente em sessão. Quer que eu cumpra aqui mesmo (alcance de pasta com `/kn-11`) ou prefere deixar para o `/kn-99`?"

Se o usuário pedir que `/kn-11` cumpra mesmo assim:

- Material cabe em 1-2 frases → **edita `<pasta>/CONTEXTO.md` direto** (linha em seção "Referências locais") em vez de criar arquivo. Sem pasta-referências, sem `index.md`/`log.md`/`kn-indice` (não cabem alcance de pasta).
- Material denso → cria `<slug>.md` na raiz da pasta de trabalho + linha em CONTEXTO.md apontando + descrição.

Fim da skill nessas duas vias — pula as Rodadas A2–A5 (não são pasta-referências).

Se a resposta for (a) **alcance de escopo**, segue o Fluxo A normal (Rodadas A1–A5) ou Fluxo B (atualizar) conforme detecção.

---

### Detecção — cria vs atualiza

Resolva a pasta-referências do escopo (lendo `pasta-referencias:` no escopo e aplicando tagged path). Procure o slug:

- **`<slug>.md` não existe em nenhum nível** → fluxo de criação (Rodada 1+).
- **`<slug>.md` existe na raiz ou em subpasta** → fluxo de atualização (mostre o arquivo encontrado, pergunte se é o mesmo conceito; se sim, avance pro fluxo de atualização; se for homônimo distinto, ajuste o slug com sufixo discriminador — ex: `joao-silva-fornecedor.md` vs `joao-silva-cliente.md`).

---

## Fluxo A — criar referência nova

### Rodada A1 — Identidade

1. **Title** — nome legível.
2. **Description em 1 linha** — denso. Vai aparecer no `kn-indice-<dominio>.md` e decide se o agente futuro puxa a referência ou passa direto. Investir em description densa paga dividendos.
3. **Localização na pasta-referências** — raiz ou subpasta. Default: raiz. Sugira subpasta apenas se já houver subpastas no mesmo padrão (ex: `clientes/`, `decisoes/`) e a referência encaixar; ou se o usuário pedir. Subpasta organiza visualmente; **não substitui domínio** (que é o filtro programático).

### Rodada A2 — Domínios

Antes de perguntar, **carregue `conceitos/dominios.md`** (se ainda não carregou). Liste os domínios disponíveis em `~/.config/koine/dominios/`. Pergunte:

> "Em quais domínios essa referência aparece? Múltiplos é primeira-classe — referências raramente cabem em uma só lente."

Apresente sugestão derivada do `type` e do conteúdo:

- `type: Pessoa` em escopo profissional → tipicamente `[universal, negocio]` ou `[negocio]` dependendo da centralidade.
- `type: Decisao` técnica → tipicamente `[tecnologia]` ou `[universal, tecnologia]` se estrutural.
- `type: Aprendizado` → o(s) domínio(s) da prática à qual o aprendizado se aplica.

Aguarde confirmação ou ajuste. `[universal]` é o fallback seguro quando dúvida.

### Rodada A3 — Corpo

Estrutura típica por `type` — apresente o template e conduza a entrevista para preencher:

- **Pessoa** — papel/relação com o escopo; trajetória curta; vínculos com outras referências; modo de contato; notas idiossincráticas relevantes ao trato.
- **Organizacao** — natureza; relação com o escopo; pessoas-chave (links para outras refs); contexto histórico relevante.
- **Decisao** — situação que motivou; opções consideradas; decisão tomada; razões; consequências previstas; revisões posteriores.
- **Aprendizado** — episódio gerador (1-2 frases, não confundir com diário); lição generalizada; aplicabilidade; antipadrão evitado.
- **Evento** — data; o que aconteceu; impacto registrável; relações.

Se o `type` não for canônico, peça ao usuário 3-5 seções que façam sentido para o caso.

### Rodada A4 — Campos recomendados do domínio

Para cada domínio declarado, leia `~/.config/koine/dominios/<dom>.md` §"Campos recomendados" e pergunte cada campo aplicável. Ex: domínio `universal` sugere `papel`, `vigente`, `desde`.

Não force — se um campo não fizer sentido, pule.

### Rodada A5 — Materialização

Monte o `<slug>.md`:

```markdown
---
type: <Pessoa | Organizacao | Decisao | Aprendizado | Evento | ...>
title: <Title>
description: <1 linha densa>
dominios: [<dom1>, <dom2>]
tags: [<keywords livres>]
<campos recomendados do domínio>
---

# <Title>

<corpo conforme estrutura típica do type>
```

Mostre o arquivo completo para confirmação antes de gravar.

Se o usuário indicou subpasta que ainda não existe, **crie a subpasta** (equivalente a `mkdir -p`) antes de gravar o `<slug>.md`. Subpasta nova é evento normal — não pede confirmação extra.

Após gravar `<localizacao>/<slug>.md`:

1. **Atualizar `index.md`** da pasta-referências — adicionar linha agrupando por `type` ou seção pré-existente. Se o `index.md` tiver seções por `type`, manter o padrão; senão, inserir em ordem alfabética simples.
2. **Atualizar `log.md`** — append `AAAAMMDD — cria — <slug> — <motivo curto>`.

Mencione ao usuário que o `kn-indice-<dom>.md` correspondente será regenerado na próxima invocação do `kn-agente` (não precisa fazer manualmente).

---

## Fluxo B — atualizar referência existente

### Rodada B1 — Mostrar e identificar delta

Mostre o `<slug>.md` atual ao usuário. Pergunte:

> "O que vamos atualizar?"

Comum:

- Mudança de campo do frontmatter (ex: `vigente: false`, `desde: ...`).
- Adicionar/remover domínio.
- Adicionar adendo no corpo (decisão revisada, novo episódio reforçando o aprendizado).
- Renomear slug — **caro, evitar**: quebra referências cruzadas em outros `.md`. Só renomear quando o slug original ficou enganoso; confirme explicitamente.

### Rodada B2 — Materialização

Aplique o delta. Mostre diff resumido. Mantenha estrutura existente — preserve o que não muda.

Após gravar:

1. **`index.md`** — atualizar só se o `title` ou agrupamento mudou.
2. **`log.md`** — append `AAAAMMDD — atualiza — <slug> — <campos|motivo curto>`.

Se a atualização mexeu em `description` ou `dominios` (campos lidos pelo gerador), mencione ao usuário que o `kn-indice-<dom>.md` correspondente será regenerado na próxima invocação do `kn-agente` — automático.

---

## Fluxo C — remover referência

Operação rara mas válida (ex: referência criada por engano, conceito deixou de existir).

Confirmação explícita antes de qualquer ação destrutiva. Padrão "Ação Documentada": gere script com `rm <slug>.md` + os deltas em `index.md`/`log.md`; usuário executa. Não rode `rm` direto.

`log.md` ganha entrada: `AAAAMMDD — remove — <slug> — <motivo>`.

Alerta: se a referência é citada em outros `.md` da pasta-referências (`grep` por slug), liste as ocorrências antes de remover — pode haver necessidade de ajuste em cascata.

---

## O que NÃO faz

- **Não cria escopo, pasta de trabalho, domínio, agente nem arquivo do usuário** — isso é `/kn-02-mantem-catalogo` e `/kn-03-cria-agente`.
- **Não substitui o diário da sessão.** Diário é o registro do que aconteceu na sessão (escrito por `/kn-99-encerra-sessao` na pasta `diario/` da pasta de trabalho). Referência generaliza além do episódio. Se o usuário tenta catalogar coisa muito episódica, sugira o diário.
- **Não regenera `kn-indice-<dom>.md`** — isso é trabalho do `kn-agente` na próxima invocação, automático.
- **Não opera fora do escopo da sessão atual.** Para catalogar em outro escopo, abrir sessão na pasta de trabalho daquele escopo (ou criar uma pasta com `CONTEXTO.md` apontando para ele). Cross-escopo é fricção deliberada.
- **Não cataloga em massa.** Uma invocação, uma referência. Catalogação em lote é antipadrão — dilui sinal e quebra a entrevista que dá densidade à `description`.
- **Não cria arquivo separado para o que cabe em uma frase.** Se a referência cabe em 1-2 linhas, prefira **uma linha em CONTEXTO.md** (alcance de pasta) ou **uma description densa** (alcance de escopo, que entra no `kn-indice`). Arquivo separado é para material denso (checklist, várias seções, lista longa) que se beneficia de estrutura própria.
- **Não cataloga como referência de escopo o que serve a uma única pasta de trabalho.** Default seguro em dúvida: alcance de pasta. Promover para escopo depois é trivial; reverter um `kn-indice-*` poluído é caro.

---

## Checkpoints

- Antes de qualquer materialização, **mostre o arquivo completo** (cria) ou **diff resumido** (atualiza) para confirmação.
- Para remoção, confirmação explícita + Ação Documentada.
- Se a captura inicial parece episódica demais (sem generalização possível), questione: "Isso vai te servir em sessão futura ou é diário desta sessão?". Diário não vira referência.
- Se a `description` saiu fraca, **insista em refinar** — é o que o agente futuro vai ler antes de decidir se puxa a referência. Description fraca degrada o `kn-indice`.
