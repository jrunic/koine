---
name: kn-04-conecta-o-paseo
description: Prepara o Paseo para abrir sessões Koine de fora do computador — do celular ou do navegador. Detecta quais clientes de IA da máquina funcionam por esse caminho, escreve a configuração dos providers, deixa o ditado entendendo português e conduz o pareamento do aparelho. OPCIONAL — só faz sentido se você for operar sessões fora do terminal; quem trabalha só no computador não precisa dela.
id: 202608301710
projeto: koine
tipo: habilidade
status: ativo
tags: [habilidade, koine, paseo, acesso-remoto, celular, ditado]
---

# kn-04 — Conecta o Paseo

Deixa o seu Koine acessível de fora do computador: você abre uma sessão pelo celular,
na sua pasta de trabalho, com o seu agente e o seu contexto.

## Antes de tudo, o que NÃO vai funcionar

Diga isto ao usuário **na primeira mensagem**. Descobrir depois é pior.

- **Codex e Antigravity não têm caminho por aqui.** Não é configuração faltando: o
  jeito como eles sobem não permite. Quem usa um deles continua no terminal, que
  segue funcionando igual.
- **A resposta falada não existe em português.** Ditar funciona, e é o que vamos
  configurar. Ouvir o agente responder em português, sem serviço pago, não é possível
  hoje — só há um modelo de fala gratuito, em inglês. Por isso a fala fica desligada:
  entregar metade faz o usuário tentar, falhar e achar que o produto é ruim.

Se ele usa Claude Code, Copilot CLI ou OpenCode, siga.

---

## 1. O que a máquina tem

Rode e leiam juntos:

```
koine paseo-info --json
```

Isso lista os clientes que têm caminho pelo Paseo, o wrapper de cada um e o que a
configuração precisa dizer. **Use o que sair daí.** Não decore lista nem escreva uma
aqui: ela muda quando o Koine ganha cliente novo, e uma cópia desatualizada produz
provider que abre sessão sem contexto e sem erro.

Depois:

```
koine instalar
```

Ele relata quais clientes existem nesta máquina e o que cada um consegue fazer aqui.
**É essa a fonte sobre o que está instalado** — não procure os programas por conta
própria: em Windows essa busca dá resposta errada, e já custou uma correção.

**Cruze as duas listas.** Só entra no Paseo cliente que aparece nas duas. Diga ao
usuário o que ficou de fora e por quê, antes de perguntar qualquer coisa.

### Login

Para cada cliente que sobrou, pergunte se ele já fez login.

**Não conclua que está logado porque existe pasta de configuração.** Isso não prova
nada — já se viu cliente com config, logs e plugins no lugar falhar a sessão por
falta de autenticação.

Confirme abrindo **uma** sessão mínima por cliente, **uma única vez**, e só para os
clientes que ele disse que vai usar: essa sondagem gasta uma chamada de verdade na
conta dele. Se falhar por autenticação, mande logar pelo comando do próprio cliente e
siga com os outros. Numa reexecução desta skill, não repita o que já deu certo.

---

## 2. Instalar o Paseo — e NÃO abrir ainda

Instale pelo caminho do sistema. O guia `acesso-remoto` da documentação tem o passo a
passo de cada um.

**Depois de instalar, não abra o aplicativo.** Este é o passo que quase todo mundo
erra, e ele decide quase 1 GB de download.

O Paseo baixa os modelos de voz **quando o serviço sobe**, e o serviço sobe **quando o
aplicativo abre**. Ele baixa o que a configuração pedir — e a configuração padrão pede
um modelo de ditado **em inglês** mais um de fala. Trocar depois **baixa outro**, sem
apagar o primeiro.

- Configurando antes: **um** modelo, 631 MB.
- Abrindo antes: dois agora, um terceiro depois — mais de 1,6 GB para chegar no mesmo
  lugar.

---

## 3. A configuração, antes da primeira abertura

Crie o arquivo `config.json` dentro da pasta `.paseo` do usuário. Crie a pasta se não
existir — o Paseo a criaria sozinho no primeiro run, e criá-la antes é justamente o
truque que economiza o download.

```json
{
  "version": 1,
  "features": {
    "dictation": {
      "stt": { "provider": "local", "model": "parakeet-tdt-0.6b-v3-int8" }
    },
    "voiceMode": { "enabled": false }
  }
}
```

- **`parakeet-tdt-0.6b-v3-int8`** entende 25 idiomas europeus e detecta sozinho qual
  está sendo falado. Não existe ajuste de idioma para ele: o campo `language` que
  aparece na documentação vale só para o serviço pago. Não o use.
- **`voiceMode: false`** desliga escuta, detecção de turno e fala de uma vez. É o que
  evita baixar o modelo de fala em inglês, e é o que evita prometer o que não temos.

**Não escreva isso em variável de ambiente.** Funciona — e tira o controle do
aplicativo em silêncio: a tela passa a mostrar um valor que não tem efeito, sem aviso
nenhum. O arquivo mantém o aplicativo no comando, que é o que o usuário espera.

**Não invente valor.** Use exatamente os nomes acima. Valor fora do catálogo não
degrada: derruba o serviço inteiro, e a linha de comando junto.

**Agora sim, mande abrir o aplicativo.** Ele baixa o modelo em segundo plano; avise
que isso leva alguns minutos e consome banda.

---

## 4. Os providers do Koine

Não existe comando para criar provider: é edição do mesmo `config.json`.

Para cada cliente que passou nas duas listas, escreva **dois** entries a partir do que
o `koine paseo-info --json` devolveu:

- um **genérico**, com o identificador do campo `provider` e sem variável de ambiente:
  deixa a pasta decidir o agente;
- um **com a variável** `KOINE_AGENTE` apontando o Hermes, com o identificador do
  campo `provider_hermes`: abre o Hermes mesmo em pasta cujo padrão é outro agente.

O comando ainda devolve o `wrapper`, que vai no comando do entry, e o tipo do
provider.

**Use os identificadores que o comando deu — não invente nome.** Eles são prescritos
pelo Koine de propósito: nome escolhido na hora diverge entre máquinas, e no dia em
que alguma ferramenta precisar ler ou consertar essa configuração ela encontraria dois
vocabulários para a mesma coisa.

**Preserve o que já estiver no arquivo.** Ele é configuração viva e pode ter coisa de
terceiro dentro; mescle campo a campo, não sobrescreva o arquivo inteiro.

Aplique sem reiniciar:

```
paseo reload
paseo provider ls
```

Os entries têm que aparecer na listagem. Se não aparecerem, o arquivo tem erro de
sintaxe — releia antes de seguir.

---

## 5. O celular

Isto é feito **na tela do aplicativo, pelo usuário** — não por você.

Antes de mandar ligar, explique o que é: o tráfego passa por um serviço do Paseo,
cifrado ponta a ponta, e é o que dispensa configurar rede. **Se ele está em máquina de
empresa, peça que confirme que a política permite.** Se não permitir, o caminho é
pedir à TI — não contornar.

O caminho na interface: **Ajustes → o seu host → Parear dispositivo**. O relay se liga
ali mesmo. A tela mostra um código e um link.

> **Diga isto com todas as letras:** esse link é uma senha. Quem o tiver abre sessões
> na máquina dele. Não colar em conversa, não mandar por mensagem, não guardar em
> lugar nenhum.

No celular: instalar o aplicativo do Paseo, escanear o código, e o computador aparece.

Quando ele avisar que pareou, confirme por aqui:

```
paseo status
```

O campo de relay deve mostrar um endereço, não `disabled`.

---

## 6. Antes de terminar

O usuário ainda **não tem pastas para abrir no celular**. Projeto e workspace são a
etapa seguinte, e quem faz é a `/kn-14-organiza-workspaces`.

Mande rodar agora, com as pastas que ele quer alcançar de fora.

## Quando reiniciar o serviço

Mudança de configuração de voz exige reiniciar o serviço; o resto reconcilia com
`paseo reload`. Fazendo na ordem desta skill, não há reinício — a configuração é
escrita antes da primeira abertura.

**Se você estiver rodando dentro de uma sessão aberta pelo próprio Paseo**, reiniciar
o serviço mata a sua própria sessão no meio. Nesse caso não reinicie: entregue o passo
ao usuário como a última coisa, avisando que a sessão vai cair e que é esperado.
