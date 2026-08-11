---
name: kn-22-gera-imagem
description: Gera imagem na identidade visual de uma marca do escopo — lê o DESIGN.md escrito por /kn-21, compõe o prompt em três camadas (marca, linha visual da série, sujeito), submete à aprovação do usuário antes de gastar, chama a CLI imagio e registra o prompt aprovado na marca para que a próxima imagem da série saia coerente.
id: 202608091000
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-22, imagem, imagio, marca, design, prompt]
---

# kn-22-gera-imagem

Transforma uma descrição em prosa — *"um avatar para a agente de suporte"*, *"capa do post sobre fechamento de mês"* — em imagem que parece da marca, e não de um gerador genérico.

A inteligência desta skill é a **composição do prompt**. A CLI `imagio` não lê identidade visual, não decide estilo e não compõe nada: recebe o prompt pronto, chama o provedor e salva o arquivo. Tudo que faz a imagem pertencer à marca acontece aqui.

Invoque quando a sessão precisa de uma peça visual e o escopo já tem marca escrita.

---

## Pré-condições

- **`imagio` instalado e configurado.** Verifique com `imagio versao`. Se faltar, o caminho é `pipx install git+https://github.com/jrunic/imagio.git@production` seguido de `imagio instalar` — mas isso é instalação de ferramenta no ambiente do usuário: informe o comando, não execute por conta própria.
- **Credencial ativa.** No backend `gemini`, geração de imagem exige créditos pré-pagos — chave nova sem faturamento ativo falha com erro de permissão. Se a chamada falhar assim, é conta, não prompt: não fique reescrevendo o prompt tentando contornar.
- **DESIGN.md da marca existe** em `<pasta-referencias>/marcas/<slug>/DESIGN.md`. Se não existe, pare e redirecione:

  > "Este escopo ainda não tem essa marca escrita. Sem DESIGN.md eu componho sobre suposição e a imagem sai genérica — e cada tentativa custa dinheiro. Rode `/kn-21-escreve-design` primeiro."

  Se o usuário insistir mesmo assim, prossiga varrendo o que houver (CSS do projeto, manual, site) e **declare explicitamente** que o prompt foi composto sobre material incompleto.

---

## Cada execução gasta dinheiro

É a diferença desta skill para todas as outras da família. Consequências operacionais, não negociáveis:

- **O prompt vai à aprovação do usuário antes da chamada.** Sempre. Nunca gere para "ver como fica".
- **Uma chamada por invocação.** Não gere variações em lote esperando que o usuário escolha — mostre o prompt, ajuste no texto, gere uma vez.
- **Reporte o custo** exatamente como o `imagio` devolveu, em toda geração.
- Se a imagem saiu errada, a correção é **no prompt, com o usuário**, não em nova tentativa automática.

---

## Roteiro

### Rodada 1 — Ler a marca

Leia o `DESIGN.md` e extraia o subconjunto que importa para imagem:

- **Paleta com os hex** — os modelos respondem bem a hex explícito no prompt.
- **Tom visual em prosa** — a seção que o `/kn-21` insistiu em ter. É o que separa "azul e branco" de uma imagem que parece da marca.
- **Seção `## Imagens`**, se já existir — os prompts aprovados anteriormente. Se a peça pedida pertence a uma série já iniciada (outro avatar da mesma equipe, mais uma capa do mesmo formato), **parta do prompt daquela série** em vez de compor do zero. É o que dá coerência entre peças.

Tipografia normalmente **não** entra no prompt: modelo de imagem escreve texto mal. Se a peça precisa de palavra escrita, avise que o texto sai melhor sobreposto depois, fora do gerador.

### Rodada 2 — Entender o sujeito

Pergunte o que a peça precisa mostrar, e onde ela vai ser usada — a segunda pergunta decide proporção e formato:

| Uso | Tamanho típico | Formato |
|---|---|---|
| Avatar, ícone | `1024x1024` | `png` |
| Capa de post, link preview | `1200x630` | `jpg` |
| Story, vertical | `1080x1920` | `jpg` |

Confirme o tamanho antes de gerar; refazer por proporção errada é gasto repetido.

### Rodada 3 — Compor o prompt

**Prompt sempre em inglês** — os modelos respondem melhor. **Sem nome de personagem, marca ou obra com IP**: descreva características visuais. *"Um mago de barba branca"*, não o nome do mago.

Três camadas, nesta ordem:

**1 — Identidade da marca.** Estilo base e paleta com hex, direto do DESIGN.md.

```
<estilo-base do tom visual>. <cores com hex>. Flat, crisp, no harsh shadows. 8k resolution.
```

**2 — Linha visual da série.** O estilo artístico que se repete entre peças irmãs. Se a marca já tem série registrada em `## Imagens`, reaproveite a linha existente palavra por palavra — é ela que faz as peças parecerem do mesmo conjunto.

**3 — O sujeito.** O que é único desta peça: aparência, vestuário, atributos de função, fundo, elementos simbólicos.

```
<descrição física: idade, expressão, traço identificador>.
<vestuário e atributos funcionais>.
<fundo e ambiente>.
```

### Rodada 4 — Aprovação

Mostre o prompt completo, o tamanho, o formato e o caminho de saída. Pergunte se pode gerar. Ajuste no texto quantas vezes o usuário quiser — **texto é grátis, geração não**.

### Rodada 5 — Gerar

```bash
imagio gerar "<prompt aprovado>" \
  --output "<caminho>" \
  --tamanho <LxA> \
  --formato <png|jpg|webp>
```

O `imagio` cria o diretório pai se não existir e **sobrescreve arquivo existente** com aviso no stderr — confira o caminho antes de rodar quando a peça for uma segunda versão.

A linha de resumo sai assim:

```
✓ capa.jpg | gemini/gemini-2.5-flash-image | 1200x630 | jpg | custo: R$ 0,23 (USD 0.04)
```

Reporte-a ao usuário como veio. Custo zero significa **desconhecido**, não gratuito — acontece em combinação de backend e modelo fora da tabela de preços.

### Rodada 6 — Registrar o prompt na marca

Se a peça vale ser repetida — avatar de uma série, formato recorrente de capa — grave o prompt aprovado no `DESIGN.md` da marca, em seção `## Imagens` ao final do arquivo (depois de `Do's and Don'ts`; seção extra não quebra o linter, verificado):

```markdown
## Imagens

### <slug-da-serie>

Aprovado em AAAAMMDD · backend `gemini` · 1024x1024

> <prompt em inglês, na íntegra>
```

Peça avulsa que não vai se repetir não precisa entrar — registro serve à coerência da série, não ao histórico.

Depois de editar o DESIGN.md, faça append em `log.md`: `AAAAMMDD — atualiza — marcas/<slug>/DESIGN.md — prompt da série <slug-da-serie>`.

---

## Onde a imagem vai

Pergunte se não estiver óbvio. Duas famílias de destino:

- **Entregável desta sessão** (capa, ilustração de um post, imagem de um slide) → pasta de trabalho atual, junto do material que ela ilustra. Não é memória do escopo.
- **Peça da marca, reutilizável** (avatar, símbolo derivado, elemento recorrente) → `<pasta-referencias>/marcas/<slug>/imagens/`. Vive ao lado do DESIGN.md porque outras sessões vão querer a mesma peça.

---

## O que NÃO faz

- **Não escreve nem corrige a marca.** Se o DESIGN.md está incompleto — sem tom visual, sem paleta —, o caminho é `/kn-21-escreve-design`, não remendo no prompt desta sessão.
- **Não gera em lote.** Uma invocação, uma imagem. Série se constrói uma peça por vez, reaproveitando a linha visual registrada.
- **Não itera sozinha.** Imagem insatisfatória volta ao usuário para ajuste do prompt; não dispara nova chamada por iniciativa própria.
- **Não instala nem configura o `imagio`.** Informa o comando; quem instala ferramenta no ambiente é o usuário.
- **Não usa IP de terceiro.** Nome de personagem, obra ou marca alheia sai do prompt e vira descrição visual.
- **Não promete texto legível dentro da imagem.** Palavra escrita se sobrepõe depois.

---

## Checkpoints

- Prompt aprovado antes de qualquer chamada. Sem exceção — é dinheiro do usuário.
- Tamanho e formato confirmados contra o uso real da peça.
- Custo reportado como o `imagio` devolveu.
- Se a marca já tem série registrada e você compôs do zero, **volte e reaproveite** — peça fora da linha visual é o defeito mais comum e só aparece quando as duas ficam lado a lado.
- Se o DESIGN.md não tinha tom visual e a imagem saiu genérica, diga a causa em voz alta: o gargalo está na marca, não no prompt.
