---
descricao: Guia — trocar o ditado e a fala para o serviço da OpenAI, que é o caminho para ouvir o agente responder em português; com o que isso custa e o que quebra se for feito errado
id: 202608302030
tipo: guia
status: ativo
tags: [guia, koine, paseo, voz, ditado, openai]
---

# Guia — voz em português com serviço pago

O Koine configura o ditado com um modelo **local e gratuito**, que entende português.
E deixa a **fala desligada**, porque o único modelo de fala gratuito responde em
inglês.

Se você quer ouvir o agente responder em português, o caminho é trocar para um serviço
pago. Este guia cobre isso.

**Você provavelmente não precisa.** Ditar já resolve o problema principal — que é
escrever numa tela de telefone. Ouvir a resposta é conforto, e vem com custo por uso e
com o seu áudio saindo da sua máquina. Leia o "o que muda" antes de decidir.

## O que muda

| | Local (padrão do Koine) | Serviço pago |
|---|---|---|
| Ditado em português | funciona | funciona |
| Fala em português | **não existe** | funciona |
| Onde o áudio é processado | **na sua máquina** | enviado ao serviço |
| Custo | zero | por uso |
| Funciona sem internet | sim | não |

A troca mais séria não é o dinheiro: é que **o seu áudio passa a sair da sua máquina**.
Se você trabalha com material de cliente, isso é decisão de contrato, não de
preferência.

## Antes de começar

- Uma chave de API da OpenAI.
- O Paseo já configurado pela `/kn-04-conecta-o-paseo`.
- Saber onde fica o `config.json` do Paseo — a pasta `.paseo` do seu usuário.

## Passo 1 — A credencial

Duas formas. A primeira é mais simples; a segunda evita a chave no arquivo.

**No arquivo de configuração**, na raiz do objeto:

```json
"providers": {
  "openai": {
    "stt": { "apiKey": "sk-..." },
    "tts": { "apiKey": "sk-..." }
  }
}
```

**Ou pelo ambiente**, deixando o arquivo sem a chave: o Paseo cai para
`OPENAI_API_KEY` quando ela não está no arquivo. Coloque no seu `~/.zshrc` ou
equivalente.

> Se você usar o ambiente, lembre que o serviço precisa **enxergar** a variável — e
> ele roda com ambiente mínimo. Um serviço iniciado pelo aplicativo pode não ver o que
> está no seu shell. Se a chave "não for encontrada" apesar de estar exportada, é isto.

## Passo 2 — Ditado pelo serviço

Em `features`, troque o provedor do ditado:

```json
"features": {
  "dictation": {
    "stt": { "provider": "openai", "language": "pt" }
  }
}
```

**Aqui o campo `language` vale** — e só aqui. Com o modelo local ele é ignorado,
porque a detecção é automática; com o serviço pago, declarar o idioma melhora a
transcrição.

## Passo 3 — A fala

Ligue o modo de voz e aponte as duas pontas:

```json
"features": {
  "voiceMode": {
    "enabled": true,
    "stt": { "provider": "openai", "language": "pt" },
    "tts": { "provider": "openai" }
  }
}
```

`voiceMode.enabled` precisa virar `true` — o Koine o deixou `false` de propósito, e é
essa chave que libera escuta, detecção de turno e fala.

## Passo 4 — Reiniciar

**Mudança de voz exige reiniciar o serviço.** Recarregar a configuração não basta —
é a exceção; quase todo o resto reconcilia sem reinício.

Feche e reabra o aplicativo do Paseo. Depois teste ditando e ouvindo.

## O que quebra, e como

Três armadilhas medidas. As duas primeiras derrubam; a terceira é pior, porque não
derruba.

### Valor fora do catálogo derruba o serviço inteiro

A configuração de voz é validada contra uma lista fechada de valores aceitos. Um nome
de modelo que não está nela **não degrada**: mata o carregamento da configuração, e o
serviço **e a linha de comando** param de funcionar.

Se depois de editar o Paseo não subir, é a primeira coisa a conferir — desfaça a
última mudança antes de procurar em outro lugar.

### Valor aceito no arranque e inexistente no destino quebra no uso

O inverso também morde: um valor que passa na validação, mas que o serviço da OpenAI
não reconhece, sobe normalmente e falha **na primeira vez que você ditar**, com um
erro sobre modelo inexistente. Teste ditando depois de mudar, não só abrindo.

### Configuração por ambiente tira o controle da interface, em silêncio

Se você puser a configuração de voz em variáveis de ambiente em vez do arquivo, a tela
do aplicativo passa a mostrar valores que **não têm efeito** — sem aviso nenhum. Você
muda ali, nada acontece, e não há mensagem explicando.

Prefira o arquivo. A exceção razoável é a chave de API, que muita gente prefere não
ter em arquivo.

## Voltar atrás

Devolva os dois blocos ao que o Koine escreveu — ditado no provedor local com o modelo
multilíngue, e `voiceMode.enabled: false` — e reinicie. O modelo local continua no
disco; nada precisa ser baixado de novo.

Se você tiver apagado o modelo local, ele volta no próximo arranque — cerca de 630 MB.
