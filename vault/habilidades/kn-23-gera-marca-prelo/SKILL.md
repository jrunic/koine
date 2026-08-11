---
name: kn-23-gera-marca-prelo
description: Deriva o payload de marca do prelo (tokens.css + config.json + fonts) a partir do DESIGN.md escrito por /kn-21, para que PDF gerado do Markdown saia na identidade visual da marca. Mapeia tokens do DESIGN para o vocabulário do prelo, baixa as fontes nos pesos que a marca usa e emite o comando de instalação. Não instala.
id: 202608091100
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-23, prelo, pdf, marca, tokens, design]
---

# kn-23-gera-marca-prelo

Traduz a marca escrita em `DESIGN.md` para o formato que o **prelo** — conversor de Markdown em PDF — entende. Depois disso, qualquer `.md` do escopo vira PDF na identidade da marca com um comando.

Rode uma vez por marca, e de novo sempre que o DESIGN.md mudar cor ou tipografia.

---

## O que esta skill emite — e o que não

O prelo monta o CSS do documento em três camadas, nesta ordem:

| Camada | Arquivo | Dono |
|---|---|---|
| Estrutura | `templates/base.css` | **o prelo** — versionado com a ferramenta |
| Tokens | `<marca>/tokens.css` | **a marca** — o que esta skill escreve |
| Extras | `<marca>/extra.css` | a marca, opcional — regra que só ela tem |

Esta skill escreve **apenas a camada de tokens**: um bloco `:root` com valores. Nunca CSS estrutural — seletor, regra de tabela, comportamento de `blockquote` pertencem ao prelo e chegam pelo upgrade da ferramenta. Marca que carrega estrutura própria é um fork silencioso que nunca mais recebe melhoria.

Payload completo:

```
<pasta-referencias>/marcas/<slug>/prelo/
├── tokens.css      ← bloco :root
├── config.json     ← name, googleFontsUrl, page, footer, fonts[]
├── fonts/*.woff2   ← as faces que os tokens realmente pedem
├── images/*        ← opcional — logo, marca d'água; referenciadas pelo extra.css
└── extra.css       ← opcional, do usuário; a skill preserva, nunca gera
```

**Imagem própria da marca** (logo, marca d'água) vive em `images/` e se referencia por caminho relativo no CSS: `url(images/logo.png)` resolve contra a pasta da marca, não contra o documento. Requer prelo ≥ 1.2.1 — a cópia de `images/` na instalação entrou nessa versão.

Não confunda as duas origens: imagem do **documento** resolve contra a pasta do `.md`; imagem da **marca** resolve contra a pasta da marca. São coisas distintas e não se misturam.

A skill não gera `images/` — quem coloca logo ali é o usuário, junto com o `extra.css` que a usa. Ambos são preservados na regeneração.

---

## Pré-condições

- **`prelo` instalado** e no PATH. Verifique com `prelo --help`. Se faltar, o caminho está em `github.com/jrunic/prelo` — informe, não instale por conta própria. Requer Node.js 22+.
- **`DESIGN.md` da marca existe** em `<pasta-referencias>/marcas/<slug>/DESIGN.md`. Se não existe, pare: `/kn-21-escreve-design` primeiro. Não há como derivar tokens de marca que não foi escrita.

### Localizar o repositório do prelo

O download de fontes usa um script que vive no repo, não no PATH. Resolva pelo próprio comando instalado:

```bash
dirname "$(readlink -f "$(command -v prelo)")"
```

O `prelo` no PATH é um symlink para o `cli.js` do repo — o diretório pai é a raiz. Se o comando não resolver (instalação por outro caminho), pergunte ao usuário onde o repo está.

---

## Roteiro

### Rodada 1 — Ler o subconjunto de impressão

Leia o `DESIGN.md` e extraia **só o que existe em papel**: `colors` e `typography` (famílias e pesos).

Ignore o resto — componentes de UI, elevation, navegação, shapes de tela. Um PDF não tem botão nem estado de hover. Puxar esses tokens para o payload só cria valores que nada pinta.

### Rodada 2 — Mapear os tokens

O que cada token pinta e qual o default quando ausente é do prelo — consulte `docs/81-referencia/referencias/tokens.md` no repo. O mapeamento **de onde o valor vem no DESIGN.md** é desta skill:

| Token | Fonte no DESIGN.md | Se ausente |
|---|---|---|
| `--fonte-corpo` | `typography.<body-*>.fontFamily` | omitir |
| `--fonte-titulo` | `typography.<headline-*\|display>.fontFamily` | omitir (herda o default do prelo) |
| `--cor-texto` | `colors.on-surface` | omitir |
| `--cor-texto-suave` | `colors.neutral` | omitir |
| `--cor-muted` | `colors.on-surface-muted` → `colors.neutral` | omitir |
| `--cor-titulo-forte` | `colors.primary` | omitir |
| `--cor-titulo-medio` | `colors.primary-light` → `colors.secondary` | omitir |
| `--cor-link` | `colors.primary-light` → `colors.secondary` → `colors.primary` | omitir |
| `--cor-borda` | `colors.neutral-border` | omitir |
| `--cor-fundo-suave` | `colors.surface-variant` | omitir |
| `--cor-fundo-zebra` | `colors.surface-variant` clareado ~4% | omitir |
| `--cor-alerta` | `colors.error` | **omitir** — o prelo degrada `.alert` para a cor de texto |
| `--cor-ok` | `colors.success` | **omitir** — idem `.ok` |

**Omitir é a ação correta, não uma falha.** Ausência de token no prelo é degradação graciosa, e a marca mínima do guia oficial tem quatro linhas. Emitir os 24 tokens com valores default só polui o arquivo e esconde o que a marca de fato decidiu.

**Nunca invente cor de estado.** Marca sem `error` não ganha um vermelho plausível — ganha `.alert` na cor do texto.

#### Tamanhos não se copiam

`--tam-*` são de **impressão**. A escala do DESIGN.md é de tela — `headline-lg: 48px` é confortável num monitor e absurdo em A4. Deixe os defaults do prelo (h1 24 / h2 18 / h3 15 / h4 13 / corpo 14 / mono 12).

Exceção única: marca claramente editorial e leve, onde 1–2px a menos no corpo acompanham a identidade. Se mexer, diga ao usuário que mexeu e por quê.

#### Pesos se copiam

Ao contrário dos tamanhos, `--peso-*` carregam identidade — uma marca editorial em Inter 200/300 tem de sair ultraleve no PDF também.

| Token | Fonte no DESIGN.md |
|---|---|
| `--peso-corpo` | `typography.<body-*>.fontWeight` |
| `--peso-titulo` | `typography.<headline-*>.fontWeight` |
| `--peso-titulo-forte` | peso do maior título / `typography.display.fontWeight` |
| `--peso-label` | `typography.<label-*>.fontWeight` |

Legibilidade de impressão é decisão da marca, não da skill. Se o resultado ficar leve demais para papel, **relate** — não corrija por conta própria.

### Rodada 3 — Fontes, acopladas aos pesos

Cada peso declarado nos `--peso-*` precisa existir como face baixada. Sem isso o Chromium **sintetiza** a face: o negrito sai falso e visivelmente pior que o real. Esse é o defeito mais comum do payload, e ele é silencioso.

1. Componha a `googleFontsUrl` com a união dos pesos usados, por família de título e de corpo.
2. Baixe para dentro do payload:

   ```bash
   node "<repo-prelo>/scripts/download-fonts.js" \
     --url "<googleFontsUrl>" \
     --dest "<...>/marcas/<slug>/prelo/fonts"
   ```

   O script emite `fonts/manifesto.json` com o que realmente veio e as perdas — o Google devolve 400 para peso inexistente (Sanchez, por exemplo, só tem 400) e o fetcher estreita para o peso disponível.
3. **Fonte proprietária que o script não obtém: reporte a lacuna.** Não silencie e não substitua por família parecida — a marca deixa de ser a marca.

### Rodada 4 — `config.json`

| Campo | Origem |
|---|---|
| `name` | `name` do frontmatter do DESIGN.md |
| `fonts[]` | **derivado de `fonts/manifesto.json`** — o que está no disco, nunca o que se pediu |
| `googleFontsUrl` | só famílias e pesos efetivamente obtidos; se houve estreitamento, refletir |
| `page.format` / `page.margin` | convenção do prelo (A4, 20/18/24/18), **não** do DESIGN |
| `footer.template` | HTML inline; a fonte de corpo e a cor `--cor-muted` vão **escritas no template**, porque rodapé não herda token |

Derivar `fonts[]` do manifesto é o que impede o `config.json` de apontar para arquivo que não existe. Depois de consumido, **apague o `manifesto.json`** — ele não faz parte do payload.

**Nunca emita `header.template`.** O `{{TITLE}}` não é substituído em cabeçalho: sai literal na página.

### Rodada 5 — Instalar e verificar

Emita o comando pronto para o usuário copiar:

```bash
prelo instalar --brand <slug> --origem <pasta-referencias>/marcas/<slug>/prelo
```

Depois, renderize uma amostra que exercite o que os tokens pintam — título, parágrafo, tabela, código, link:

```bash
printf '# Teste\n\nTexto com `código`, **negrito** e [link](https://exemplo.com).\n\n| A | B |\n|---|---|\n| 1 | 2 |\n' > /tmp/teste-marca.md
prelo --brand <slug> --input /tmp/teste-marca.md --output /tmp/teste-marca.pdf
```

Peça ao usuário para abrir o PDF. Duas coisas a conferir a olho: o `código` numa fonte monoespaçada e os títulos no peso certo — negrito sintetizado é o que mais escapa.

### Rodada 6 — Registrar

Append em `log.md` da pasta-referências:

```
AAAAMMDD — atualiza — marcas/<slug>/prelo — payload gerado do DESIGN.md
```

O payload é **artefato derivado**: regenerar sobrescreve, e a fonte de verdade é sempre o DESIGN.md. Se o usuário editou `tokens.css` à mão, essa edição se perde na próxima geração — nesse caso o certo é corrigir o DESIGN.md e regenerar, ou mover a exceção para `extra.css`.

**Regenerar sobrescreve `tokens.css`, `config.json` e `fonts/` — e só.** Se a pasta já tem `extra.css` ou `images/`, **deixe-os intactos**: são do usuário, e o `prelo instalar` os copia junto. Apagá-los numa regeneração faz a exceção da marca — ou o logo — sumir sem aviso.

---

## Regras invioláveis

- **Só o bloco `:root`.** Nenhum seletor, nenhuma regra estrutural no `tokens.css`.
- **Token ausente é omitido**, nunca preenchido com o default do prelo.
- **Cor de estado ausente não se inventa.**
- **`fonts[]` vem do manifesto**, nunca do DESIGN ou do CSS.
- **Sem `header.template`.**
- **Superfície de escrita:** exclusivamente `marcas/<slug>/prelo/` na pasta-referências. Nunca escrever dentro do repo do prelo nem em `~/.local/share/prelo/` — quem instala é o `prelo instalar`.

---

## O que NÃO faz

- **Não instala a marca.** Emite o comando; o usuário executa.
- **Não instala nem configura o prelo.**
- **Não edita a marca.** Cor errada no PDF se conserta no DESIGN.md via `/kn-21-escreve-design`, e depois se regenera aqui. Remendar o `tokens.css` cria divergência entre a marca escrita e a marca impressa.
- **Não escreve `extra.css` nem `images/`.** São a válvula de escape do usuário para o que a marca tem de único — regra própria e logo. A skill não os gera nem os sobrescreve.
- **Não gera PDF de conteúdo real.** Só a amostra de verificação. Converter documento é uso direto do `prelo`.
- **Não decide margem nem formato de página** a partir do DESIGN — são convenção do prelo, e um design de tela não tem opinião sobre A4.

---

## Checkpoints

- Mostre o `tokens.css` e o `config.json` ao usuário antes de gravar.
- Liste explicitamente **quais tokens foram omitidos e por quê** — é o que revela lacuna no DESIGN.md que vale a pena preencher.
- Confira peso a peso: todo `--peso-*` declarado tem face correspondente em `config.fonts`.
- Fonte proprietária não obtida vira lacuna reportada, nunca substituição silenciosa.
- Renderize a amostra. Payload que nunca foi renderizado não foi verificado.
- Se o DESIGN.md mudou depois do último payload, diga que o `prelo/` está defasado antes de qualquer outra coisa.
