---
name: kn-04-conecta-o-paseo
description: Prepara o Paseo para sessões Koine de fora do computador. Chama paseo-info, paseo-configurar, paseo-provider e paseo-doctor; explica o relay; conduz pareamento e o login do navegador interno. OPCIONAL — quem trabalha só no terminal não precisa.
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
- **A resposta falada não existe em português.** Ditar funciona, e é o que os
  comandos vão configurar. Ouvir o agente responder em português, sem serviço pago,
  não é possível hoje — só há um modelo de fala gratuito, em inglês. Por isso a fala
  fica desligada: entregar metade faz o usuário tentar, falhar e achar que o produto
  é ruim.

Se ele usa Claude Code, Copilot CLI ou OpenCode, siga.

---

## 1. O que a máquina tem

Rode e leiam juntos:

```
koine paseo-info --json
```

Isso lista os clientes que têm caminho pelo Paseo e se o wrapper existe. **Use o que
sair daí.** Não decore lista.

**Papel 1 do instalar — relato.** Sempre:

```
koine instalar
```

Ele relata quais clientes existem nesta máquina. **É essa a fonte sobre o que está
instalado** — não procure os programas por conta própria: em Windows essa busca dá
resposta errada.

**Cruze as duas listas só para decidir quais clientes de IA sondar o login.** Não
use o cruzamento para omitir provider: o comando da seção 3 grava a matriz inteira.

**Papel 2 do instalar — wrappers.** Se o info avisar que algum wrapper não existe no
PATH, pare, rode `koine instalar` de novo se ainda não rodou, e repita o info.
**Nunca improvise o comando do provider.**

### Login dos clientes de IA

Para cada cliente que sobrou no cruzamento, pergunte se ele já fez login.

**Não conclua que está logado porque existe pasta de configuração.**

Confirme abrindo **uma** sessão mínima por cliente, **uma única vez**, e só para os
que ele disse que vai usar. Se falhar por autenticação, mande logar pelo comando do
próprio cliente e siga com os outros. **Numa reexecução, não repita o que já deu certo.**

---

## 2. Instalar o Paseo — e NÃO abrir ainda

Instale pelo caminho do sistema. O guia de acesso remoto da documentação tem o passo
a passo de cada um.

**Depois de instalar, não abra o aplicativo.** Este é o passo que quase todo mundo
erra, e ele decide quase 1 GB de download.

O Paseo baixa os modelos de voz **quando o serviço sobe**, e o serviço sobe **quando o
aplicativo abre**. A configuração padrão pede ditado em inglês mais fala. Trocar
depois **baixa outro**, sem apagar o primeiro.

- Configurando antes: **um** modelo, 631 MB.
- Abrindo antes: dois agora, um terceiro depois — mais de 1,6 GB para chegar no mesmo
  lugar.

---

## 3. Os comandos, antes da primeira abertura

Não edite o config à mão. Não dita JSON.

```
koine paseo-configurar
```

Se sair diferente de zero, leia a mensagem. **Não edite o arquivo.**

```
koine paseo-provider
```

Ele grava a matriz inteira dos clientes com rota. Se recusar por wrapper, volte ao
papel 2 da seção 1 — não invente `command`.

**Omitir a chave de relay expõe a máquina** — o comando a escreve desligada. Quem
liga o relay é o usuário, na tela, depois de você explicar o que é. A skill não liga.

**Não escreva isso em variável de ambiente.** Tira o controle da tela do aplicativo
em silêncio.

### Primeira vez

O aplicativo ainda não abriu. Não rode `paseo reload`.

### Reexecução (app já de pé)

Depois dos dois comandos, `paseo reload`. **Se esta sessão estiver aberta pelo
próprio Paseo**, não recarregue: entregue o reload ao usuário, avisando que a sessão
vai cair e que é esperado.

**Agora sim, mande abrir o aplicativo** (primeira vez) ou confirme que já está aberto
(reexecução). Na primeira, ele baixa o modelo em segundo plano; avise que isso leva
alguns minutos e consome banda.

---

## 4. Duas pessoas na mesma máquina

Só nesse caso — se o usuário for o único, pule.

Duas pessoas na mesma máquina não compartilham a porta. Esta skill **não** escreve
a porta. Oriente `PASEO_HOST` no perfil do shell para não cair na porta padrão da
outra pessoa, e aponte o guia de acesso remoto da documentação. Não dite JSON.

---

## 5. O celular

Isto é feito **na tela do aplicativo, pelo usuário** — não por você.

Antes de mandar ligar, explique: o tráfego passa por um serviço do Paseo, cifrado
ponta a ponta, e dispensa configurar rede. **Se ele está em máquina de empresa, peça
que confirme que a política permite.** Se não permitir, o caminho é pedir à TI — não
contornar.

O caminho na interface: **Ajustes → o seu host → Parear dispositivo**. O relay se liga
ali mesmo. A tela mostra um código e um link.

> **Diga isto com todas as letras:** esse link é uma senha. Quem o tiver abre sessões
> na máquina dele. Não colar em conversa, não mandar por mensagem, não guardar em
> lugar nenhum.

No celular: instalar o aplicativo do Paseo, escanear o código, e o computador aparece.

---

## 6. Login do navegador interno

Depois do aplicativo aberto. O sintoma é a sessão do agente responder `Please run login`.
**Não é o login do Claude** (nem do Copilot, nem do OpenCode). É o navegador de dentro
do Paseo, uma vez; as sessões seguintes aproveitam.

Peça ao usuário para entrar no site que o agente precisa, **dentro do navegador do
Paseo**. Não leia cookie. Não abra a pasta de partições.

Numa reexecução, se o doctor já viu sessão gravada, não peça de novo.

---

## 7. Fecho

```
koine paseo-doctor
```

`--json` se você for consumir as verificações. Pronto é a saída do doctor, não
busca de wrapper.

- Linha `[ERRO]`: leia, explique, **não edite o config**.
- Aviso (ditado, etc.): informe; não mande “consertar YAML”.
- Se configurar ou provider tiverem saído 1 mais cedo: a mensagem deles manda; ainda
  assim não edite o arquivo.

O usuário ainda **não tem pastas para abrir no celular**. Quem faz é a
`/kn-14-organiza-workspaces`. Mande rodar agora, com as pastas que ele quer alcançar
de fora.

## A identidade do serviço

A pasta de estado do Paseo guarda a identidade do serviço — o par de chaves e o
identificador que os aparelhos pareados conhecem. Mover ou apagar faz o serviço
renascer com identidade nova, e **todo celular pareado deixa de encontrá-lo**: o
sintoma é tempo esgotado no aparelho, sem mensagem de erro.

Se isso acontecer: parear de novo, ou devolver os dois arquivos de identidade da cópia
antiga. Ao mexer nessa pasta, **mova, não apague**.
