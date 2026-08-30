---
descricao: Tutorial — do zero até abrir uma sessão Koine pelo celular, ditando em português, com o seu contexto e o seu agente
id: 202608302020
tipo: tutorial
status: ativo
tags: [tutorial, koine, paseo, celular, ditado, acesso-remoto]
---

# Tutorial — abrir uma sessão Koine pelo celular

Ao final deste tutorial você vai pegar o telefone, abrir uma sessão na sua pasta de
trabalho, **ditar uma pergunta em português** e receber a resposta com o seu contexto
carregado — o seu perfil, o seu escopo, a sua pasta.

**Tempo:** cerca de 40 minutos, quase todos esperando download.

## Antes de começar

Você precisa de:

- **Koine instalado e configurado** — se você nunca rodou o `/kn-01-recebe-usuario`,
  faça o [onboarding completo](onboarding-completo.md) primeiro. Este tutorial
  assume que você já tem pelo menos uma pasta de trabalho funcionando no terminal.
- **Um destes clientes de IA**: Claude Code, GitHub Copilot CLI ou OpenCode. Se você
  usa Codex ou Antigravity, este caminho não existe para eles — e o motivo está na
  [explicação](../explicacoes/por-que-paseo.md). Continue no terminal.
- **Um celular** com o aplicativo do [Paseo](https://paseo.sh/) instalado.
- **Cerca de 700 MB de banda** para o modelo de ditado.

> Se a sua máquina é da empresa, leia agora a seção "Quando o problema é a TI" do
> [guia de acesso remoto](../guias/acesso-remoto.md). Duas políticas comuns impedem
> este caminho, e é melhor saber antes.

## Passo 1 — Instalar o Paseo, e não abrir

Instale pelo caminho do seu sistema. O
[guia de acesso remoto](../guias/acesso-remoto.md) tem os comandos de cada um.

**Não abra o aplicativo depois de instalar.** Este é o passo que quase todo mundo
erra.

O Paseo baixa os modelos de voz quando o serviço interno sobe, e ele sobe quando você
abre o aplicativo. Ele baixa o que a configuração pedir — e a de fábrica pede um
modelo de ditado **em inglês**, mais um de fala que você não vai usar. Configurando
antes: um modelo. Abrindo antes: dois agora e um terceiro depois, mais de 1,6 GB para
chegar no mesmo lugar.

## Passo 2 — A conversa que configura

Abra uma sessão Koine no terminal, na sua pasta canônica, e peça:

```
/kn-04-conecta-o-paseo
```

Ela vai:

1. **Dizer o que não vai funcionar** — quais dos seus clientes ficam de fora, e que
   a resposta falada em português não existe sem serviço pago. Leia essa parte; ela
   evita frustração depois.
2. **Descobrir o que a sua máquina tem** e cruzar com o que tem caminho.
3. **Perguntar quais clientes você vai usar de fato**, e confirmar o login abrindo
   uma sessão mínima em cada. Não deduza por você: ela precisa da sua resposta.
4. **Escrever a configuração**, antes da primeira abertura.
5. **Escrever os providers** — dois por cliente.

Ao final, ela pede para você abrir o aplicativo.

**O que esperar:** a conversa faz perguntas. Se ela decidir sozinha algo que devia
perguntar, isso é defeito — [nos avise](https://github.com/jrunic/koine/issues).

## Passo 3 — Abrir o aplicativo

Agora sim. Ele vai baixar o modelo de ditado em segundo plano: alguns minutos,
dependendo da sua conexão.

Enquanto baixa, volte à sessão do terminal e peça para ela conferir. Os seus providers
devem aparecer na lista com estado disponível.

## Passo 4 — Parear o celular

Isto é na tela do aplicativo, e é você quem faz.

**Ajustes → o seu host → Parear dispositivo.** O relay se liga ali mesmo — a
configuração que a conversa escreveu o deixou desligado de propósito, porque expor a
sua máquina à internet é decisão sua.

A tela mostra um código e um link.

> **Esse link é uma senha.** Quem o tiver abre sessões no seu computador, com acesso
> aos seus arquivos. Não cole em conversa, não mande por mensagem, não guarde em
> anotação.

No celular: abra o aplicativo do Paseo, escaneie o código, e o seu computador aparece.

## Passo 5 — Registrar as suas pastas

Você ainda não tem nada para abrir. Volte ao terminal e peça:

```
/kn-14-organiza-workspaces
```

Diga quais pastas quer alcançar de fora e que nome dar a cada uma. Ela cria a
estrutura e confere.

**Uma pasta só é aceita se tiver contexto Koine configurado** — senão a sessão subiria
sem o seu contexto, que é o problema que estamos evitando. Se alguma for recusada,
rode a `/kn-02-mantem-catalogo` nela antes.

## Passo 6 — A primeira sessão pelo celular

No aparelho: escolha o seu computador, um dos workspaces que acabou de criar, e o
provider **Koine** do seu cliente.

**Toque no microfone e dite**, em português:

> Em uma frase: o que é esta pasta e quem é você?

A resposta deve trazer o seu agente e o escopo da pasta — não uma resposta genérica de
assistente. Se vier genérica, o contexto não chegou; a
[referência](../referencias/paseo.md) tem a lista dos três defaults que causam isso.

**Pronto.** Daqui em diante, pasta nova só precisa do passo 5.

## O que você aprendeu, e o que fazer agora

Você configurou um caminho paralelo ao terminal — não um substituto. O terminal segue
sendo o lugar do trabalho longo; o celular é para o que acontece longe da mesa.

Dois caminhos a partir daqui:

- **Quer a resposta falada também, em português?** Existe, com serviço pago:
  [voz com OpenAI](../guias/voz-com-openai.md).
- **Duas pessoas usam esta máquina?** Há uma armadilha que não perdoa, e ela está no
  [guia de acesso remoto](../guias/acesso-remoto.md).
