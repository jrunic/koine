---
descricao: Guia para quem usa Koine — instalar o Paseo e abrir sessões do celular, com o que funciona, o que não funciona e o que depende da TI da sua empresa
id: 202608301800
tipo: guia
status: ativo
tags: [guia, koine, paseo, acesso-remoto, celular, instalacao]
---

# Guia — Abrir sessões Koine de fora do computador

Audiência: quem já usa o Koine no terminal e quer abrir sessões do celular ou do
navegador, com o mesmo contexto e o mesmo agente.

O caminho é o [Paseo](https://paseo.sh/), um orquestrador de sessões. O Koine tem duas
conversas que fazem quase tudo — `/kn-04-conecta-o-paseo` e
`/kn-14-organiza-workspaces`. **Este guia cobre o que elas não podem fazer por você:**
baixar um instalador, clicar num assistente e decidir se o seu computador pode ser
alcançado pela internet.

## O que isto dá — e o que não dá

**Dá:** abrir uma sessão pelo celular, na sua pasta de trabalho, com o seu contexto e
o seu agente. Ditar em português em vez de digitar na telinha.

**Não dá:**

- **Codex e Antigravity não têm caminho por aqui.** Não é configuração faltando: o
  jeito como eles sobem não permite. Se você usa um deles, continua no terminal.
- **Resposta falada em português.** Ditar funciona. Ouvir o agente responder em
  português, sem serviço pago, não é possível hoje — só existe um modelo de fala
  gratuito, e ele é em inglês. Por isso o Koine deixa a fala desligada.

## Antes de instalar: não abra o aplicativo depois

Guarde isto agora, porque é onde quase todo mundo tropeça:

> **Instale, mas não abra.** Rode a `/kn-04-conecta-o-paseo` antes da primeira
> abertura.

O Paseo baixa os modelos de voz quando o serviço interno sobe, e ele sobe quando você
abre o aplicativo. Ele baixa o que a configuração pedir — e a configuração de fábrica
pede um modelo de ditado **em inglês**, mais um de fala que você não vai usar.

Configurando antes: **um** modelo, cerca de 630 MB. Abrindo antes: dois agora, e um
terceiro depois quando trocar — mais de 1,6 GB para chegar no mesmo lugar. Trocar de
modelo **baixa outro**; não substitui.

## Instalar — Windows

Baixe pela linha de comando, não pelo navegador:

```cmd
cd /d "%USERPROFILE%\Downloads"
curl -L -o Paseo-Setup.exe https://github.com/getpaseo/paseo/releases/latest/download/Paseo-Setup-<versao>-<arch>.exe
start /wait "" Paseo-Setup.exe /S
echo EXIT=%errorlevel%
```

Três coisas que economizam tempo:

- **`<arch>` importa** — `arm64` ou `x64`. Veja qual é o seu em
  `echo %PROCESSOR_ARCHITECTURE%`.
- **`start /wait` não é enfeite.** Sem ele o instalador não roda até o fim, e o código
  de saída que você vê não é o dele.
- **Baixar pelo navegador traz uma tela de aviso de segurança.** Ela é normal e some
  se você baixar pela linha de comando acima. Se preferir o navegador, espere o aviso
  e escolha executar assim mesmo.

A instalação é **por usuário** e não pede senha de administrador.

## Instalar — macOS

Pelo gerenciador de pacotes, se você o tem:

```bash
brew install --cask paseo
```

Ou baixe o arquivo da página de releases do produto e arraste para Aplicativos.

> **Não testamos este caminho ponta a ponta.** O caminho do Windows foi medido; este
> não. Se algo divergir do descrito aqui, nos avise — é a informação que falta.

## Duas pessoas no mesmo computador

A forma é **oposta** nos dois sistemas, e isso confunde quem já instalou no outro:

| | Windows (estação corporativa) | macOS |
|---|---|---|
| Programa do cliente de IA | instalado **por usuário** | instalado **para a máquina** |
| Uma segunda conta | precisa instalar de novo | **já enxerga** os programas |
| Login em cada cliente | por pessoa | por pessoa |

No macOS, a segunda pessoa encontra os programas prontos e precisa apenas fazer login
em cada um. No Windows travado, ela reinstala tudo.

**Em qualquer sistema, o login é sempre por pessoa.** E não conclua que está logado
porque existe uma pasta de configuração: ela pode existir completa, com histórico e
tudo, e a sessão falhar por falta de autenticação. O jeito de saber é abrir uma
sessão.

## Duas pessoas usando o Paseo na mesma máquina

Se cada pessoa tem a sua conta e as duas vão usar o Paseo, há um detalhe que não
perdoa.

O serviço escuta numa porta, e as duas não podem usar a mesma. Quem configurar depois
escolhe outra, **no arquivo de configuração** — e não por argumento de linha de
comando nem por variável de ambiente, que deixam a tela do aplicativo mostrando um
valor sem efeito, em silêncio.

**A armadilha:** a linha de comando do Paseo, quando não encontra o serviço
configurado, **cai na porta padrão** — a da outra pessoa. Está escrito na ajuda do
próprio comando. Na prática, com o seu serviço parado, um comando seu de listar ou de
parar acerta a sessão de quem está do outro lado.

Se a sua porta não for a padrão, fixe a escolha no seu shell:

```bash
export PASEO_HOST=127.0.0.1:<sua porta>
```

Isso força um candidato único e tira a porta padrão do caminho.

## Trocar de computador

A configuração do Koine é **portável, sem tradução**. Os caminhos que ela guarda são
relativos à sua pasta pessoal, não absolutos — então copiar a pasta de configuração e
as pastas de trabalho para a máquina nova basta. Não há nada para reescrever.

Depois de copiar, rode `koine validar` na máquina nova para confirmar.

## Quando o problema é a TI, e não você

Duas situações em que insistir não resolve, e o caminho é pedir liberação:

- **A política da empresa bloqueia o serviço de conexão remota.** O pareamento do
  celular usa um serviço do Paseo para alcançar o seu computador sem você configurar
  rede. Onde ele é bloqueado, não há como contornar pelo Koine.
- **O cliente de IA não consegue executar comandos na sua estação.** Alguns clientes
  usam um interpretador de comandos que certas políticas bloqueiam. A sessão abre e o
  contexto chega — o agente lê e escreve arquivos —, mas rodar comando não funciona.
  O `koine instalar` diz quais dos seus clientes estão nessa situação.

## Se a sessão abre mas vem sem o seu contexto

Você abre pelo celular, o agente responde — mas responde como um assistente qualquer,
sem saber quem você é nem em que pasta está.

Duas causas, e as duas são silenciosas por natureza:

**O provider aponta para um cliente sem caminho.** Configurar Codex ou Antigravity aqui
não dá erro: o provider fica com cara de saudável e a sessão sobe sem o Koine no meio.
Confira com `koine paseo-info` quais clientes têm caminho, e remova os outros.

**A pasta não está configurada.** Se ela não tem contexto Koine, o agente deve dizer
isso na primeira mensagem e orientar o caminho. Se ele não disse nada e respondeu
genérico, é o caso anterior.

## Se o provider aparece como indisponível

A lista de providers mostra o seu como não disponível, ou "caminho não resolvido", e a
sessão nem abre.

A causa quase sempre é o **caminho do wrapper escrito sem ser absoluto**. O serviço do
Paseo roda com um ambiente mínimo, e a pasta de programas do seu usuário não está no
caminho de busca dele — então o nome puro não resolve.

Descubra o caminho real e use ele na configuração do provider:

```bash
command -v kn-claude-paseo      # macOS e Linux
where kn-claude-paseo           # Windows
```

## Se o celular parar de encontrar o computador

O sintoma é tempo esgotado no aparelho, sem mensagem de erro.

A causa mais comum é a **identidade do serviço ter mudado**. Ela vive na pasta de
configuração do Paseo, junto com o registro dos seus projetos — se essa pasta for
movida, renomeada ou apagada, o serviço renasce com identidade nova e os aparelhos
pareados passam a procurar algo que não existe mais.

Duas saídas: parear de novo pela tela do aplicativo, ou devolver a pasta antiga ao
lugar. Por isso, ao mexer nela por qualquer motivo, **mova em vez de apagar**.

## Segurança do pareamento

O pareamento do celular acontece na tela do aplicativo, em **Ajustes → o seu host →
Parear dispositivo**. Ela mostra um código e um link.

> **Esse link é uma senha.** Quem o tiver abre sessões no seu computador, com acesso
> aos seus arquivos. Não cole em conversa, não mande por mensagem, não guarde em
> anotação.

O tráfego entre o celular e o computador é cifrado ponta a ponta.

## Ordem recomendada

1. Instalar o Paseo — **sem abrir**.
2. `/kn-04-conecta-o-paseo` — configuração, providers, ditado, e a orientação do
   pareamento.
3. Abrir o aplicativo e parear o celular.
4. `/kn-14-organiza-workspaces` — registrar as pastas que você quer alcançar.

Depois disso, pasta nova só precisa do passo 4. E se você esquecer, o Paseo registra
sozinho ao abrir — só com o nome da pasta, sem você escolher o agrupamento.
