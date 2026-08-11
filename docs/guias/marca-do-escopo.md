---
descricao: Guia da família kn-2N — pré-requisitos, ordem de uso e o que cada skill produz para colocar a identidade visual de uma marca para funcionar no escopo
id: 202608111700
tipo: guia
status: ativo
tags: [guia, marca, design, kn-2N, prelo, imagio, pdf, identidade-visual]
---

# Guia — A marca do escopo

Audiência: usuário Koine cujo escopo produz material visual — proposta, relatório, apresentação, capa, avatar — e que hoje decide cor e fonte peça a peça.

A família `kn-2N` resolve isso uma vez: a marca é escrita num arquivo, e cada peça seguinte nasce dela.

## A sequência

Quatro skills, três delas apoiadas na primeira:

```
/kn-21-escreve-design          ← escreve o DESIGN.md da marca
        │
        ├──→ /kn-22-gera-imagem        imagem na identidade      (precisa de imagio)
        │
        └──→ /kn-23-gera-marca-prelo   prepara a marca p/ PDF    (precisa de prelo)
                     │
                     └──→ /kn-24-gera-pdf   documento em PDF de marca
```

`/kn-21` roda uma vez por marca. `/kn-23`, uma vez por marca e de novo quando o `DESIGN.md` mudar. `/kn-22` e `/kn-24` são cotidianas — rodam sempre que há peça ou documento a entregar.

**Os dois ramos são independentes.** Quem só precisa de imagem instala o `imagio` e ignora o `prelo`; quem só precisa de PDF faz o contrário. Só o `/kn-21` é obrigatório para os dois.

## Pré-requisitos

| Para | Precisa de | Como obter |
|---|---|---|
| `/kn-21-escreve-design` | Node.js, para o linter oficial do schema | já vem com o Node; a skill usa `npx @google/design.md lint` |
| `/kn-22-gera-imagem` | [`imagio`](https://github.com/jrunic/imagio) + credencial de um backend | `pipx install git+https://github.com/jrunic/imagio.git@production` e depois `imagio instalar` |
| `/kn-23` e `/kn-24` | [`prelo`](https://github.com/jrunic/prelo) **≥ 1.2.1**, Node.js 22+ | clone do repo + `npm install`, conforme o README do prelo |

Sobre as versões do prelo, que não são detalhe:

- **≥ 1.2.0** — caminho relativo de imagem no Markdown resolve contra a pasta do `.md`. Abaixo disso, `![](fotos/x.png)` renderiza quebrada e o comando ainda reporta sucesso.
- **≥ 1.2.1** — o `prelo instalar` leva a subpasta `images/` da marca. Abaixo disso, uma marca com logo perde o arquivo na instalação e a regra CSS aponta para o vazio.

**Geração de imagem custa dinheiro.** Cada `/kn-22` é uma chamada paga ao provedor. A skill sempre mostra o prompt e pede aprovação antes de gastar, e reporta o custo depois. No backend `gemini`, geração de imagem exige créditos pré-pagos — chave nova sem faturamento ativo falha com erro de permissão, e isso é conta, não prompt.

## Onde as coisas ficam

A marca vive na **pasta-referências do escopo**, porque é memória de longa duração: serve a todas as pastas de trabalho daquele escopo.

```
<pasta-referencias>/marcas/<slug>/
├── DESIGN.md          ← a marca escrita (/kn-21)
├── imagens/           ← peças reutilizáveis: avatar, símbolo (/kn-22)
└── prelo/             ← payload para o PDF (/kn-23)
    ├── tokens.css
    ├── config.json
    ├── fonts/
    ├── images/        ← logo da marca, se houver (você põe)
    └── extra.css      ← regra que só essa marca tem (você escreve)
```

O que **não** fica ali: o PDF e a imagem que ilustram um trabalho específico. Esses são entregáveis e ficam na pasta de trabalho, junto do material que acompanham.

## Passo a passo

### 1. Escrever a marca

```
/kn-21-escreve-design
```

O agente **varre antes de perguntar** — CSS do projeto, `tailwind.config`, manual de marca em PDF, site — e só pergunta o que a varredura não respondeu. A primeira fala dele é um relatório do que achou, não um questionário.

A pergunta em que ele insiste é o **tom visual**: duas ou três frases sobre o que a marca parece e o que ela evita. Se sair "moderno e limpo", ele empurra de volta — é o campo que decide a qualidade de tudo que vem depois, e o mais fácil de deixar vago.

Ao final, o `DESIGN.md` passa pelo linter oficial. Warning de contraste é comum e não é defeito do arquivo: é um fato sobre a sua paleta.

### 2a. Gerar imagem

```
/kn-22-gera-imagem
```

Duas perguntas — o que a peça mostra e **onde vai ser usada**. A segunda decide o tamanho (`1024x1024` para avatar, `1200x630` para capa, `1080x1920` para story), e refazer por proporção errada é gasto repetido.

O agente monta o prompt em três camadas: identidade da marca, linha visual da série e o sujeito da peça. Você ajusta o texto quantas vezes quiser — **texto é grátis, geração não** — e aprova antes da chamada.

Peça que vale repetir tem o prompt gravado no `DESIGN.md`, em `## Imagens`. É o que faz o segundo avatar da série sair parecido com o primeiro em vez de recomeçar do zero.

### 2b. Preparar a marca para PDF

```
/kn-23-gera-marca-prelo
```

Lê o `DESIGN.md`, traduz para os tokens do prelo, baixa as fontes nos pesos que a marca usa e escreve o payload. Ao final emite o comando de instalação, para você executar:

```bash
prelo instalar --brand <slug> --origem <pasta-referencias>/marcas/<slug>/prelo
```

Duas coisas que a skill decide de propósito e vale saber:

- **Tamanho de fonte não se copia do DESIGN.** A escala de um design de tela é grande demais em A4. Os tamanhos de impressão vêm do prelo.
- **Peso se copia.** Se a marca é editorial ultraleve, o PDF sai ultraleve — legibilidade de impressão é decisão da marca, não da ferramenta.

Regenerar sobrescreve `tokens.css`, `config.json` e `fonts/`. O `extra.css` e a pasta `images/` são seus: a skill não os toca.

### 3. Converter documento

```
/kn-24-gera-pdf
```

Antes de converter, o agente confere no disco que **cada imagem do documento existe**. Arquivo faltando interrompe — o prelo avisa no stderr mas termina com código de sucesso, e um furo descoberto depois do envio custa mais que um PDF não gerado.

O `.md` vai para a ferramenta como está: sem cópia, sem reescrever caminho. O documento continua portável entre máquinas.

## Quando algo sai errado

| Sintoma | Causa provável |
|---|---|
| Imagem do documento aparece como ícone quebrado | prelo abaixo da 1.2.0 — ou o arquivo realmente não existe |
| Logo da marca não aparece no PDF | prelo abaixo da 1.2.1; o `prelo instalar` deixou a pasta `images/` para trás |
| `title: X tags: [a]` impresso acima do primeiro título | faltou `--strip-frontmatter`; a `/kn-24` passa sozinha |
| Título em negrito com aparência "borrada" | o peso declarado nos tokens não foi baixado, e o Chromium sintetizou a face |
| Imagem gerada sai genérica, sem cara da marca | o `DESIGN.md` está sem tom visual — o gargalo é a marca, não o prompt |
| `.alert` e `.ok` saem na cor do texto | a marca não declara cor de estado; é degradação proposital, não bug |

**Tamanho do PDF não diagnostica nada.** Medimos um PDF com imagem quebrada em 23,4 KB contra 18,4 KB do correto — o ícone de imagem quebrada é ele próprio um objeto de imagem, às vezes maior que a foto real.

## Marca de mais de um escopo

Cada escopo tem a sua pasta-referências, então marcas não se misturam: a identidade do cliente A é invisível na sessão do cliente B. Para trabalhar a marca de outro escopo, abra sessão numa pasta de trabalho dele. Cross-escopo é fricção deliberada.

## Referências

- [Habilidades](../referencias/habilidades.md) — o que cada skill produz, entrada e saída
- [`prelo`](https://github.com/jrunic/prelo) — conversor de Markdown em PDF de marca
- [`imagio`](https://github.com/jrunic/imagio) — geração de imagem por linha de comando
- [`@google/design.md`](https://github.com/google-labs-code/design.md) — schema do `DESIGN.md`
