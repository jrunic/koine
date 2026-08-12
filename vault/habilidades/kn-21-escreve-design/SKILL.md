---
name: kn-21-escreve-design
description: Escreve ou atualiza o DESIGN.md de uma marca do escopo atual — varre as fontes disponíveis (arquivos da pasta, manual de marca, site), preenche lacunas por entrevista cirúrgica, materializa na pasta-referências com frontmatter híbrido (Ficha Koine + schema @google/design.md) e valida com o linter oficial. Base das demais skills da dezena 2N.
id: 202608081000
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-21, design, marca, identidade-visual, design-md]
---

# kn-21-escreve-design

Materializa a **identidade visual de uma marca** do escopo atual em um `DESIGN.md` — o arquivo que descreve cores, tipografia, formas e tom visual em tokens legíveis por máquina. É a base da dezena `2N`: `/kn-22-gera-imagem` e `/kn-23-gera-marca-prelo` leem o arquivo que esta skill escreve.

Invoque quando o escopo passa a produzir material visual — apresentação, PDF, capa, avatar, site — e cada peça está sendo decidida do zero. Uma marca escrita uma vez remove a decisão de cor e fonte de todas as sessões seguintes.

Marca aqui não é só empresa: é qualquer identidade visual com vida própria — a empresa do usuário, um cliente do escopo, um produto, um canal de conteúdo, a marca pessoal.

---

## Pré-condições

- Sessão rodando em **pasta de trabalho com `CONTEXTO.md`** — o escopo sai daí (`escopo:` no frontmatter). Sem ele, redirecione para `/kn-02-mantem-catalogo` (Fluxo 3).
- Escopo resolve para `~/.config/koine/escopos/<slug>.md` com `pasta-referencias:` válida (`index.md` e `log.md` presentes). Se faltar, `/kn-02-mantem-catalogo` (Fluxo 2b) regulariza.
- **Node.js disponível** para o linter (`npx @google/design.md lint`). Sem Node, a skill roda até o fim e entrega o arquivo, mas **avise que a validação não rodou** — não finja que passou.
- O `@google/design.md` está em **versão alpha** e o schema pode mudar entre releases. O `npx` sem versão puxa a última publicada e precisa de rede a cada invocação. Se a validação começar a acusar erro em arquivo que passava, suspeite de drift do schema antes de suspeitar do arquivo — e fixe a versão que funciona (`npx @google/design.md@<versao> lint ...`).

---

## Conceitos referenciados

Carregue **antes** de operar:

- `~/.local/share/koine/conceitos/referencias.md` — a pasta-referências, a Ficha Koine, os contratos OKF (`index.md`, `log.md`).
- `~/.local/share/koine/conceitos/dominios.md` — para decidir o campo `dominios:` da marca.

---

## Onde o DESIGN.md mora

Na pasta-referências do escopo, em subpasta própria por marca:

```
<pasta-referencias>/marcas/<slug-marca>/
└── DESIGN.md
```

A subpasta existe porque a marca acumula payload: `/kn-23` escreve `prelo/` ao lado, e imagens geradas frequentemente ficam junto. Marca é o único caso da pasta-referências em que a subpasta é obrigatória, não estética.

O nome do arquivo é **`DESIGN.md`, sempre maiúsculo** — é contrato do schema, não preferência.

### Frontmatter híbrido — dois contratos no mesmo bloco

O DESIGN.md responde a dois leitores: o Koine (que o indexa como referência) e o `@google/design.md` (que o valida como sistema de design). Os dois cabem no mesmo YAML — verificado contra o linter, que ignora chaves que não conhece.

```yaml
---
# Ficha Koine — o que faz a marca aparecer no kn-indice
type: Marca
title: "<Nome da Marca>"
dominios: [<dom1>, <dom2>]
tags: [marca, design, <slug-marca>]

# Schema @google/design.md — o que o linter valida
version: alpha
name: <Nome da Marca>
description: "<uma linha densa; serve aos dois contratos>"
colors:
  primary: "<hex>"
typography:
  <token>:
    fontFamily: <string>
    fontSize: <px|rem>
---
```

Regras que valem para a convivência:

- `description` é **compartilhada** pelos dois contratos — escreva uma linha que sirva de resumo no índice *e* de descrição da marca. Não duplique com `descricao`.
- `name` (schema) e `title` (Ficha) carregam o mesmo nome legível. Manter os dois é redundância barata; omitir qualquer um quebra um dos leitores.
- **Nenhuma chave repetida.** YAML com chave duplicada faz o linter emitir warning de parse e o gerador de índice ler o valor errado. Antes de gravar, confira que cada chave aparece uma vez só.
- Cite `title` e `description` com aspas duplas — o gerador de índice lê o bloco como YAML e um valor não-citado com dois-pontos no meio derruba a referência do `kn-indice`.

---

## Detecção — cria vs atualiza

Resolva a pasta-referências e procure `marcas/<slug-marca>/DESIGN.md`:

- **Não existe** → Fluxo A (criar).
- **Existe** → mostre o arquivo atual e vá para o Fluxo B (atualizar). Não sobrescreva sem mostrar.

---

## Fluxo A — escrever a marca

### Rodada A1 — Varredura de fontes

Antes de perguntar qualquer coisa ao usuário, **procure o que já existe**. Pergunte só o que a varredura não respondeu — marca costuma estar documentada em algum lugar, e entrevistar sobre o que está escrito queima a paciência do usuário.

Varra nesta ordem, parando de perguntar conforme os tokens forem preenchendo:

1. **Arquivos da pasta de trabalho e da pasta-referências** — qualquer `*marca*`, `*identidade*`, `*visual*`, `*brand*`, além de CSS, `tailwind.config`, tokens de tema já existentes no projeto.
2. **Manual de marca** — PDF ou apresentação que o usuário aponte. Peça o caminho; leia.
3. **Site da marca** — se houver, leia o CSS servido e extraia paleta e famílias tipográficas reais.
4. **Entrevista** — só para o que sobrou.

Declare ao usuário o que encontrou e de onde, antes de avançar: *"Achei a paleta no CSS do site e a tipografia no manual; falta o tom visual e as regras de uso do logo."*

### Rodada A2 — Lacunas, uma por vez

Para cada token obrigatório ausente, pergunte **com o contexto do que já foi encontrado** — não uma bateria de perguntas soltas.

Obrigatórios de fato:

- `colors.primary` — a cor que a marca reivindica.
- Ao menos um token de `typography` — família e tamanho.

Fortemente recomendados, porque as skills irmãs os consomem:

- `colors.neutral` e um `on-*` de contraste — `/kn-23` precisa deles para o corpo de texto do PDF.
- **Tom visual em prosa** — duas ou três frases sobre o que a marca parece e o que ela evita. É o que `/kn-22` transforma em prompt de imagem; sem isso a geração vira genérica.

Não invente token ausente. Marca sem cor de erro definida não ganha uma cor de erro inventada — ganha a ausência registrada.

### Rodada A3 — Domínios

Liste os domínios disponíveis em `~/.config/koine/dominios/` e pergunte em quais a marca aparece. Sugestão default: o domínio de negócio do escopo. `[universal]` é o fallback seguro.

### Rodada A4 — Materialização

Monte o arquivo com o frontmatter híbrido acima e o corpo nas seções canônicas.

**Ordem canônica das seções** (o linter tem regra `section-order`; podem ser omitidas, mas não reordenadas):

`Overview` · `Colors` · `Typography` · `Layout` · `Elevation & Depth` · `Shapes` · `Components` · `Do's and Don'ts`

Tokens de componente válidos: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`. Outros passam com warning.

Para o que não estiver coberto aqui — referências `{token.path}`, variantes de componente, formatos aceitos de cor e dimensão — **consulte a spec, não improvise**:

```bash
npx @google/design.md spec --rules
```

Mostre o arquivo completo ao usuário antes de gravar.

### Rodada A5 — Validação

```bash
npx @google/design.md lint <pasta-referencias>/marcas/<slug>/DESIGN.md
```

- **Erro** bloqueia: corrija e rode de novo antes de entregar.
- **Warning** reporta, não bloqueia. O mais comum é `contrast-ratio` — uma combinação de cores da própria marca abaixo do mínimo WCAG AA. Não "conserte" alterando a cor da marca; relate ao usuário como fato sobre a identidade dele.
- **Node ausente** → entregue o arquivo e diga explicitamente que não validou.

### Rodada A6 — Contratos OKF

Depois de gravar:

1. **`index.md`** — linha para a marca, no agrupamento existente (ou seção `Marcas`, se o índice for por `type`).
2. **`log.md`** — append `AAAAMMDD — cria — marcas/<slug>/DESIGN.md — <motivo curto>`.

Mencione que o `kn-indice-<dom>.md` é regenerado na próxima invocação do `kn-agente` ou por `/kn-12-prepara-contexto` — não se edita à mão.

---

## Fluxo B — atualizar marca existente

Mostre o `DESIGN.md` atual e pergunte o que muda. Casos comuns: paleta revista, fonte trocada, componente novo, tom visual afinado depois de ver peças reais.

Aplique o delta preservando o que não muda, mostre diff resumido, **rode o linter de novo** e faça append em `log.md`: `AAAAMMDD — atualiza — marcas/<slug>/DESIGN.md — <campos>`.

Quando a mudança tocar `colors` ou `typography`, avise que o payload do prelo ficou defasado:

> "A paleta mudou. O `prelo/` desta marca foi gerado da versão anterior — rode `/kn-23-gera-marca-prelo` para regenerar."

---

## O que NÃO faz

- **Não gera imagem** — isso é `/kn-22-gera-imagem`.
- **Não escreve o payload do prelo** — isso é `/kn-23-gera-marca-prelo`. Esta skill produz a fonte; as outras derivam dela.
- **Não inventa token.** Cor, fonte ou regra ausente na marca fica ausente no arquivo. Lacuna declarada vale mais que preenchimento plausível — as skills irmãs vão propagar o que estiver escrito aqui.
- **Não cataloga marca de fora do escopo.** Marca de outro escopo se escreve em sessão daquele escopo.
- **Não escreve mais de uma marca por invocação.** Uma invocação, uma marca — a varredura e a entrevista são o que dão densidade ao arquivo.
- **Não substitui referência de organização.** Quem é o cliente, qual a relação, quem decide — isso é `/kn-11-mantem-referencia` com `type: Organizacao`. Aqui é só a identidade visual.

---

## Checkpoints

- Declare o que a varredura encontrou **antes** de entrevistar. Perguntar o que já está escrito é o erro mais caro desta skill.
- Mostre o arquivo completo antes de gravar.
- Linter roda sempre que houver Node; resultado é reportado como saiu — inclusive os warnings.
- Se o tom visual saiu genérico ("moderno e limpo"), **insista**. É o campo que mais decide a qualidade da imagem gerada pelo `/kn-22`, e o mais fácil de deixar vago.
- Se o escopo não tem material visual nenhum e o usuário está inventando a marca agora, diga isso em voz alta: escrever DESIGN.md é registrar identidade existente, não criá-la. Criar do zero é trabalho de design, e a skill pode conduzir — mas o usuário precisa saber que está decidindo, não documentando.
