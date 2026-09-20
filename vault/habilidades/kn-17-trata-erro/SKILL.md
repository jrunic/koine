---
name: kn-17-trata-erro
description: Trata erro que a sessão não resolve de imediato — consulta o catálogo de erros conhecidos (sempre a versão mais recente, fora de release) e, se não resolver, monta um relato redigido e pede confirmação antes de enviar ao mantenedor por uma cascata de transporte.
id: 202609192220
projeto: koine
tipo: habilidade
status: ativo
tags: [habilidade, koine, erro, suporte, relato, diagnostico]
---

# kn-17 — Trata erro

Dois estágios. O primeiro tenta resolver sozinho. O segundo só roda se o
primeiro não resolver, e nunca envia nada sem confirmação explícita do
mentorado.

## Antes de tudo, o que NÃO vai funcionar

Diga isto ao mentorado **se o degrau 1 do envio (abaixo) falhar** — não antes,
porque a maioria das sessões tem shell funcional e isso seria alarme sem
motivo.

- **Copilot, Codex e Antigravity numa máquina Windows corporativa restrita
  (PowerShell negado por política) não têm shell utilizável.** Não é
  configuração faltando — é a política da máquina. Nesses casos, o envio cai
  direto para o degrau 3 (texto na tela + e-mail), e isso é esperado, não um
  defeito desta skill.

## 1. Consulta o catálogo

Busque a versão mais recente do documento de erros conhecidos — **sempre da
branch principal, nunca de uma cópia local ou de uma versão fixada**:

```
https://raw.githubusercontent.com/jrunic/koine/main/docs/referencias/erros-conhecidos.md
```

Leia o texto do erro que travou a sessão contra os sintomas catalogados ali.
**Casou um sintoma?** Aplique o remédio documentado e pare aqui — não monte
relato nenhum. Diga ao mentorado, em uma frase, o que era e o que você fez.

**Não casou nenhum sintoma?** Vá para a etapa 2.

Se a própria busca ao catálogo falhar (sem rede, por exemplo), trate como "não
casou" e siga para a etapa 2 — o catálogo é uma tentativa de resolver mais
rápido, não um pré-requisito do relato.

## 2. Monta o relato — com redação, antes de mostrar qualquer coisa

Monte, internamente, estes campos (não mostre o JSON ao mentorado, é para o
resumo em texto simples da etapa 3):

- `koine_versao` — rode `koine versao` se ainda não souber.
- `cliente_ia` — o cliente desta própria sessão (você já sabe: Claude, Copilot,
  Codex, OpenCode ou Antigravity).
- `sistema_operacional` — o sistema operacional desta máquina.
- `sondagem_shell` — se você tentou rodar algum comando de shell durante o
  diagnóstico e ele falhou ou funcionou, registre isso aqui numa frase curta;
  se não tentou nada, deixe de fora.
- `erro_cru` — o texto do erro tal como apareceu, sem inventar nem resumir.
  **O serviço recusa campo acima de 4000 caracteres** — se o erro cru for
  maior que isso (stack trace comprido), mantenha só as primeiras ~4000
  caracteres, que costumam trazer a mensagem principal.
- `config_gerada` — se o erro envolveu um arquivo de configuração que você
  consultou (ex.: config de um adapter), inclua só o trecho relevante,
  **até ~8000 caracteres** — mesmo limite do serviço.

**Não inclua um campo `assinatura`** — quem calcula a assinatura de dedup é
o serviço, do lado de lá, a partir de `koine_versao` + `cliente_ia` +
primeira linha de `erro_cru`. Mandar esse campo faz o serviço recusar o
relato inteiro (campo não reconhecido).

**Antes de qualquer coisa, redija `erro_cru` e `config_gerada`:**

- Ache qualquer caminho absoluto (`C:\Users\<nome>\...` no Windows,
  `/Users/<nome>/...` ou `/home/<nome>/...` no macOS/Linux).
- Corte tudo a partir do primeiro segmento **depois** do nome de usuário —
  mantenha só `C:\Users\<nome>\` ou `/Users/<nome>/`, e substitua o resto por
  `<pasta-do-usuario>`.
- **O nome da pasta de trabalho desta sessão nunca entra no relato** — nem
  no caminho redigido, nem em texto livre que você escrever nos campos.

Esta é a primeira passada de redação — feita por você, que é prosa, não
código determinístico. O serviço que recebe o relato aplica uma segunda
passada mecânica antes de publicar; é ela que garante o critério de segurança,
não esta. Ainda assim, **não pule esta etapa** — quanto menos sujeira sai da
máquina do mentorado, melhor.

## 3. Mostra o resumo e pede confirmação — sem exceção

Mostre ao mentorado, em português simples, sem jargão técnico:

> Não consegui resolver esse erro sozinho. Posso enviar um relato para quem
> mantém o Koine poder corrigir? Vou enviar: a versão do Koine, o programa de
> IA que você está usando, o sistema operacional, e o texto do erro (sem
> nomes de pasta ou de arquivo específicos seus). Posso enviar?

**Só prossiga com uma resposta afirmativa clara.** Uma resposta negativa, ou
qualquer coisa que não seja uma confirmação, **interrompe aqui** — não tente
de novo na mesma sessão a menos que o mentorado peça.

## 4. Envia — cascata de 3 degraus, nesta ordem

Tente cada degrau só se o anterior **falhar** — nunca pule um degrau
direto para o próximo por suposição; a falha real de execução é o único
sinal válido (não a presença ou ausência de uma ferramenta). **Assim que um
degrau tiver sucesso, pare — não execute nem ofereça o degrau seguinte.**
Mostrar dois caminhos de envio ao mesmo tempo (ex.: "arquivo salvo, mas você
também pode copiar este texto e mandar por e-mail") confunde o mentorado sem
necessidade.

**Grava o arquivo primeiro, sempre — antes de tentar a rede.** Isso não é o
degrau 2 adiantado: é o que torna o degrau 1 possível sem quoting frágil, e
já deixa pronto o artefato do degrau 2 se o envio falhar.

O arquivo vai na subpasta `diario/` da pasta de trabalho (a mesma que a
sessão já mantém para registros — crie a pasta se ela não existir), nomeado
com a data de hoje: `diario/AAAAMMDD-relato-erro.json`. **Se esse nome já
existir** (mais de um relato no mesmo dia), acrescente um número:
`diario/AAAAMMDD-relato-erro-2.json`, `-3.json`, e assim por diante — nunca
sobrescreva um relato anterior. Grave o relato em JSON, redigido:

```json
{"koine_versao":"...","cliente_ia":"...","sistema_operacional":"...","erro_cru":"...","sondagem_shell":"...","config_gerada":"..."}
```

(Omita `sondagem_shell`/`config_gerada` do JSON se não os coletou — não
mande campo vazio, e nunca inclua `assinatura`.)

**Não conseguiu gravar o arquivo** (sem ferramenta de escrita disponível na
sessão)? Pule direto para o degrau 3 — sem arquivo, não há como tentar o
degrau 1 com `-d @arquivo`, e insistir nele sem o arquivo reintroduziria o
problema de quoting que esta ordem existe para evitar.

**Degrau 1 — chamada direta ao serviço, lendo o corpo do arquivo.** Com o
arquivo gravado (chame-o de `<arquivo>` abaixo — o nome exato que você deu a
ele em `diario/`), tente rodar:

```bash
curl -sS -w "\n%{http_code}" -X POST https://relatos.jedilabs.com.br/relatos \
  -H "Content-Type: application/json" \
  -H "X-Koine-Client: koine-mentorado-v1" \
  -d @<arquivo>
```

`-d @arquivo` (em vez de `-d '{...}'` com aspas simples) é o que torna este
comando portável — aspas simples não funcionam como quoting no `cmd.exe` do
Windows, e é exatamente lá que o degrau 1 mais precisa funcionar. A última
linha da saída é o código HTTP. Foi `200` ou `201`? Diga ao mentorado que o
relato foi enviado, apague o arquivo de `diario/`, e **pare aqui**. Qualquer
outra coisa — comando não encontrado, sem rede, erro de execução, ou um
código que não seja `200`/`201` — é falha; vá para o degrau 2.

**Degrau 2 — arquivo local (o mesmo já gravado em `diario/`).** Se o degrau 1
falhou (ou se você já pulou direto para cá por não ter conseguido gravar
antes — nesse caso não há arquivo, vá direto ao degrau 3), diga ao
mentorado: o relato ficou salvo em `diario/<nome-do-arquivo>`, e que ele pode
ser enviado depois — anexado a um e-mail para `koine@orlandoferreira.com.br`,
ou por outro meio que o mantenedor tenha combinado com ele. **Pare aqui** —
não ofereça também o degrau 3 nesta mesma resposta.

**Degrau 3 — texto na tela.** Só chega aqui se nem a chamada nem a escrita em
arquivo funcionaram. Mostre o conteúdo do relato como texto simples, direto
na conversa, e diga ao mentorado: capture a tela (print) e envie por e-mail
para `koine@orlandoferreira.com.br`. Este degrau não depende de nenhuma
ferramenta além de você conseguir escrever texto na conversa — funciona em
qualquer cliente, inclusive os citados na seção "O que NÃO vai funcionar".

## O que esta skill NÃO faz

- Não insiste sozinha além do catálogo — se o sintoma não está lá, não tenta
  adivinhar o remédio.
- Não envia nada sem confirmação explícita do mentorado.
- Não inclui o nome da pasta de trabalho em nenhum campo do relato.
- Não repete o envio automaticamente se o serviço estiver fora do ar — cada
  falha de degrau é tratada uma vez, na ordem, nesta sessão.
