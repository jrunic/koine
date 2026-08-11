---
name: kn-24-gera-pdf
description: Converte um Markdown em PDF na identidade de uma marca do escopo, via prelo — confere que cada imagem local existe antes de converter e remove o frontmatter, que são os pontos onde a conversão falha em silêncio.
id: 202608101000
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-24, pdf, prelo, markdown, marca]
---

# kn-24-gera-pdf

Uso cotidiano da marca: pega um `.md` do trabalho — relatório, proposta, análise, peça — e devolve um PDF com a identidade visual do escopo.

O `prelo` faz a conversão. Esta skill existe para garantir que o documento entregue está **inteiro**: que nenhuma imagem ficou pelo caminho e que o frontmatter não vazou para a página.

Enquanto `/kn-23-gera-marca-prelo` roda uma vez por marca, esta roda toda vez que existe um documento para entregar.

---

## Pré-condições

- **`prelo` ≥ 1.2.0** instalado e no PATH. Requer Node.js 22+.

  ```bash
  prelo --help | grep -q base-url && echo "ok" || echo "versão anterior à 1.2.0"
  ```

  Em versão anterior, imagem com caminho relativo **não resolve** e o PDF sai com o ícone de quebrado. Nesse caso, peça a atualização em vez de contornar.

- **A marca instalada no host.** Liste as disponíveis:

  ```bash
  ls "${XDG_DATA_HOME:-$HOME/.local/share}/prelo/brands/"
  ```

  Se a marca do escopo não está lá:
  - Payload já existe em `marcas/<slug>/prelo/` → `prelo instalar --brand <slug> --origem <...>/marcas/<slug>/prelo`
  - Payload não existe → `/kn-23-gera-marca-prelo` primeiro
  - Nenhuma marca ainda, e o usuário só quer o PDF agora → use `exemplo` e diga que o resultado não tem a identidade dele

---

## Onde a conversão falha em silêncio

**Imagem que não existe em disco.** O prelo emite aviso no stderr, mas **não interrompe**: o PDF sai com o ícone de imagem quebrada e o código de saída é 0. Se ninguém ler o aviso, o furo só aparece depois de o documento ter sido enviado.

**Frontmatter vira conteúdo.** Sem `--strip-frontmatter`, o bloco YAML entra no corpo: `title: X tags: [a]` aparece impresso acima do primeiro título, com uma linha horizontal atravessando a página.

### Tamanho de arquivo não diagnostica nada

Medido: o PDF com a imagem **quebrada** saiu com 23,4 KB e o PDF **correto** com 18,4 KB. O ícone de imagem quebrada é ele próprio um objeto de imagem no PDF, às vezes maior que a foto real.

Não use tamanho como sinal de que deu certo. A verificação é **antes** da conversão, checando que cada arquivo existe — determinística, e não depende de interpretar o resultado.

---

## Roteiro

### Rodada 1 — Inventário de imagens

Antes de converter, liste os links de imagem do `.md` e separe:

| Não precisa conferir | Conferir no disco |
|---|---|
| `http://`, `https://` | caminho relativo (`fotos/x.png`, `../img/y.jpg`) |
| `data:` | caminho absoluto do sistema |
| `file://` já formado | |

Para cada caminho relativo, resolva contra a **pasta do `.md`** e confirme que o arquivo existe.

**Arquivo faltando interrompe a skill.** Liste o que não foi encontrado e pare. Gerar um PDF com buraco e entregar ao usuário é pior que não gerar.

Esta rodada é a razão de a skill existir. O prelo avisa, mas segue em frente; a política do Koine é não entregar documento furado.

### Rodada 2 — Converter

```bash
prelo --brand <marca> \
  --input <doc.md> \
  --output <destino.pdf> \
  --strip-frontmatter
```

**Converta o `.md` original, direto.** Caminho relativo de imagem resolve contra a pasta do arquivo de entrada — a ferramenta faz isso desde a v1.2.0. Não monte cópia de render, não reescreva caminho: além de desnecessário, converter link relativo para absoluto antes de chamar o prelo faz a ferramenta tratá-lo como intenção explícita e gravar o caminho da máquina de quem gerou dentro do PDF.

Sobre o destino: sem instrução do usuário, grave **ao lado do `.md` original**, mesmo nome com extensão `.pdf`. O PDF é entregável do trabalho, não memória do escopo — não vai para a pasta-referências.

`--strip-frontmatter` sempre que o arquivo tiver frontmatter. Não custa nada em documento que não tem.

**Link relativo no documento** (`[anexo](anexo.pdf)`) perde o destino e fica só o texto — comportamento correto para um PDF que vai por e-mail, porque um caminho local não resolveria na máquina de quem recebe. Se o documento está publicado numa URL e os links devem apontar para lá, acrescente `--base-url https://site.com/docs/`.

### Rodada 3 — Verificar e entregar

Diga ao usuário o caminho do PDF e **peça que abra**. Se o documento tem imagem, o que se confere é se a imagem apareceu — não o tamanho do arquivo.

Se o prelo emitiu aviso de imagem não encontrada e a Rodada 1 estava verde, algo mudou no disco entre uma coisa e outra — reconfira o caminho antes de entregar.

---

## O que NÃO faz

- **Não cria nem edita marca.** Cor errada no PDF se conserta no `DESIGN.md` (`/kn-21-escreve-design`) e se propaga por `/kn-23-gera-marca-prelo`. Mexer no `tokens.css` instalado cria divergência entre a marca escrita e a impressa.
- **Não instala marca.** Emite o comando `prelo instalar`; quem executa é o usuário.
- **Não edita o `.md` canônico**, nem monta cópia de render. O documento vai para a ferramenta como está.
- **Não converte em lote** sem o usuário pedir. Um documento por invocação é o default; lote é caso explícito.
- **Não gera PDF com imagem faltando.** Falta de arquivo interrompe, não vira aviso no rodapé.
- **Não escolhe margem, formato nem rodapé.** Isso é `config.json` da marca — muda em `/kn-23`, não aqui.

---

## Checkpoints

- Versão do prelo conferida antes de converter.
- Toda imagem local conferida no disco **antes** de converter.
- `.md` canônico convertido direto, sem cópia intermediária.
- `--strip-frontmatter` quando há frontmatter.
- Tamanho do PDF não é evidência de nada. Verificação é a checagem prévia dos arquivos mais o usuário abrindo o resultado.
- Se o usuário pedir PDF de marca que não existe no escopo, diga o que está faltando — `DESIGN.md` (`/kn-21`), payload (`/kn-23`) ou instalação (`prelo instalar`) — em vez de cair silenciosamente na marca `exemplo`.
