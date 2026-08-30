# Changelog

All notable changes to Koine are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Não publicado]

### Adicionado — sessão do Koine por orquestrador, com o agente que você pedir

A instalação passa a emitir um wrapper por cliente para uso por orquestrador de
sessões, ao lado dos que você já usa no terminal. Com ele, uma sessão aberta do
celular ou do browser sobe com o seu contexto e com o agente que a pasta declara —
ou com o que você pedir, pela variável `KOINE_AGENTE`.

E a sua pasta de trabalho **não é tocada**. Antes, uma sondagem do orquestrador
podia fazer o Koine criar um `CONTEXTO.md` numa pasta qualquer, porque a sondagem
roda de onde o serviço subiu — e isso aconteceu. Agora, pasta que ainda não é de
trabalho recebe uma instrução dizendo onde configurá-la, e nada é escrito. No
terminal nada muda: lá você entrou na pasta de propósito, e o Koine continua
conduzindo a configuração ali mesmo.

`koine paseo-info` lista quais clientes funcionam por esse caminho. **Nem todos
funcionam, e configurar um que não funciona falha em silêncio** — o provider
parece saudável, a sessão abre e responde, e o contexto simplesmente não está lá.

### Corrigido — no OpenCode, o agente que você pede vence o da pasta

Abrir sessão com um agente explícito numa pasta que declara outro devolvia **o da
pasta**. `kn-opencode hermes .` numa pasta com `agente: sheldon` subia o Sheldon,
sem erro e sem aviso — o agente errado, em silêncio.

O OpenCode era o único adapter que entregava os arquivos **crus**, por caminho
absoluto. Os outros quatro compõem um documento que remove o frontmatter e nomeia
cada camada. Sem isso, dois defeitos com uma causa só: a Ficha Koine da pasta ia
junto, e o `agente:` dela — que é metadado do instalador, já consumido na abertura
da sessão — virava a única afirmação de identidade no texto; e, sem o rótulo da
camada de agente, o arquivo do agente chegava e mesmo assim não era adotado.

Agora o OpenCode recebe o mesmo documento composto dos demais. O `CONTEXTO.md` da
sua pasta passa a chegar por conteúdo, como já chegava no Copilot, com o aviso de
que a fonte canônica é o arquivo na pasta. Nada muda no que você digita.

## [0.9.0] — 2026-08-29

### Adicionado — o instalador põe a pasta do Koine no seu PATH (Windows)

Até aqui o Koine avisava e mandava editar as variáveis de ambiente à mão — que é
onde a instalação morria para quem não é técnico. Agora ele acrescenta a própria
pasta ao `Path` do usuário, por API do registro. **Só a dele:** o PATH é do
usuário, e o que estiver lá de outros programas fica exatamente como está,
inclusive duplicata óbvia.

Nunca por `setx`, que trunca a variável em 1024 caracteres **em silêncio** e
destrói as variáveis não expandidas (`%USERPROFILE%`) que o PATH costuma carregar.
E a comparação expande essas variáveis antes de decidir — sem isso o instalador
não reconheceria a própria pasta já presente, e duplicaria.

E o aviso deixa de mentir. Ele comparava contra o terminal aberto, então dizia
"não está no seu PATH" quando a pasta estava lá e faltava só reabrir a janela.
Agora são três situações distintas: o que o instalador acabou de corrigir, o que
depende de você reabrir o terminal, e o que não deu para fazer — com a orientação
manual, sem PowerShell, que é justamente o que a estação corporativa bloqueia.

### Adicionado — o `instalar` diz o que vai funcionar nesta máquina Windows

Ao final da instalação, um relatório por cliente detectado: quem consegue executar
comandos ali e quem não. Informacional — não bloqueia, não pergunta.

Onde a política bloqueia o PowerShell, **copilot, codex e antigravity ficam sem
ferramenta de shell**, e não há configuração que resolva — nem instalar o Git Bash,
que resolve só para o Claude Code. O relatório diz isso com todas as letras, e diz
também o que fazer quando há o que fazer: para o Claude, o link do Git para Windows,
o nome do arquivo conforme a arquitetura, que não precisa de administrador, e que a
instalação deve ficar no local padrão — é lá que ele procura, não no PATH.

Dois avisos que não são de shell entram no mesmo relatório, porque quem instala não
faz essa distinção: a interface do OpenCode não abre em Windows ARM64 (bug do próprio
projeto; a alternativa é `opencode web`), e uma instalação de Codex feita pelo zip do
executável isolado está incompleta — sem o `codex-code-mode-host`, toda ferramenta
falha com um erro que parece limitação do modelo.

E o launch avisa, em uma linha, quando o cliente que está subindo é um desses. A
sessão abre assim mesmo: o contexto chega e o agente lê e escreve arquivos.

### Corrigido — o shell no Windows deixa de ser sempre `cmd`

O Koine passa a **medir** quais shells a máquina consegue executar e a escolher o
melhor que cada cliente aceita, na ordem `pwsh` → `powershell` → `bash` → `cmd`.

Fixar `cmd` era remendo de um incidente real — estação corporativa que bloqueia o
`powershell.exe`, onde o default do OpenCode derrubava a ferramenta de shell — e
tinha sido aplicado a **toda** máquina Windows. Quem não tem restrição nenhuma
recebia o shell mais pobre da lista sem que ninguém tivesse decidido isso.

A medição é por **execução**, não por presença: na estação travada o `pwsh.exe`
existe, está no PATH e é recusado. E o `bash` é procurado também **fora do PATH**,
na instalação padrão do Git — é onde ele fica quando o Git é instalado sem
administrador, e é onde os próprios clientes o encontram.

### Corrigido — o Claude não recebe mais uma ferramenta PowerShell que não funciona

Onde a política de grupo nega o PowerShell, o Claude Code ainda carregava a
ferramenta PowerShell além da Bash. Ela não podia funcionar, e a sessão só não
quebrava enquanto o modelo preferisse a Bash — bastava ele escolher a outra para o
usuário levar um erro de política no meio do trabalho, sem entender por quê.

Agora o Koine grava `CLAUDE_CODE_USE_POWERSHELL_TOOL=0` nessas máquinas. Onde o
PowerShell executa, nada é escrito e o default do cliente vale.

## [0.8.0] — 2026-08-28

### Adicionado — `koine instalar` pode ser inteiramente declarado na linha de comando

As três decisões que o comando fazia por pergunta agora cabem em flags:
`--pasta-canonica`, `--contexto-canonico` e `--para` (que passou a aceitar
`todos` e `nenhum`). Mais `--nao-interativo`, que aceita o default de todas.

O motivo é prático: o comando decidia se ia perguntar **olhando para o
terminal**. Script rodado de dentro de um terminal — uma tarefa agendada, uma
sessão de agente — parava no primeiro prompt e ficava pendurado **sem erro**.
O contorno era redirecionar o stdin, que é obscuro e diferente em cada sistema.
Agora a flag decide, e o terminal não opina.

Nada muda para quem instala à mão: sem flags, o comportamento é o de antes.

### Corrigido — no Copilot e no OpenCode, o agente passa a saber o que é o Koine

Nesses dois clientes faltava uma camada inteira do contexto: o `KOINE.md`, que é
onde está descrito o que a ferramenta é e como se opera. O agente sabia quem é
você, qual agente estava operando e em que pasta — mas não conhecia o método. Vem
de antes, dos adapters originais.

### Corrigido — `koine definir-agente` deixa de ser desfeito quando a ficha some

Se você rodava `koine definir-agente`, e depois o bloco de configuração do topo do
`CONTEXTO.md` sumia, a sessão seguinte repunha a ficha **sem** o agente que você
tinha definido — e o arquivo de backup também não o tinha. A linha se perdia.

Agora, quem escreve a ficha também fotografa: o que você grava sobrevive à
reposição.

## [0.7.0] — 2026-08-28

### Alterado — o contexto chega por fora da pasta, e a pasta volta a ser sua

Até agora o Koine escrevia um arquivo na sua pasta de trabalho (`CLAUDE.md`,
`GEMINI.md`, `AGENTS.md`) para entregar o contexto ao cliente. **Isso deixa de
acontecer.** O contexto passa a ser entregue por fora, pelo canal que cada
cliente oferece, a partir de um pacote descartável no cache.

O que muda para você:

- **Sua pasta para de receber arquivo gerado.** Na primeira sessão em cada
  pasta, o arquivo que o Koine tinha deixado lá é removido, com aviso. Arquivo
  **seu** — sem a marca do Koine na primeira linha — nunca é tocado.
- **A sessão passa a receber o contexto em lugares onde antes não recebia.** Com
  o mecanismo anterior, uma pasta aberta pela primeira vez, ou de longe, subia
  **sem contexto e sem erro nenhum** — o agente respondia como um assistente
  qualquer, e não havia como perceber. No terminal parecia funcionar porque o
  agente abria os arquivos por conta própria.
- **No Copilot, o agente passa a saber quem você é e qual agente está
  operando.** Essas duas camadas estavam num arquivo que o Copilot não lê.
- **Some a disputa pelo `AGENTS.md`.** Três clientes escreviam ou apontavam para
  o mesmo nome na sua pasta.

### Corrigido — `koine gerar` não destrói mais o seu `CLAUDE.md`

Se você mantinha um `CLAUDE.md` próprio e rodou `koine gerar` naquela pasta, o
arquivo era substituído **sem backup** — e o comando ainda dizia quantos bytes
tinha escrito. Agora o seu arquivo é preservado em `.bak` antes, com aviso, como
já acontecia ao abrir a sessão.

Não há como recuperar o que se perdeu em sessões passadas.

### Adicionado — `koine gerar --para <cliente>`

O `gerar` sempre produzia um `CLAUDE.md`, mesmo para quem usa outro cliente. Ele
agora aceita para qual cliente gerar (`claude`, `agy`, `codex`, `copilot`,
`opencode`); sem a flag, segue gerando para o Claude.

O arquivo gerado a pedido leva uma segunda marca dizendo que **foi pedido** — é
ela que impede a limpeza automática de removê-lo. Quem trabalha no modo skills,
sem os atalhos `kn-<cliente>`, depende desse arquivo: ali ele é a única via de
entrega.

### Adicionado — a ficha do `CONTEXTO.md` volta sozinha quando some

O bloco de configuração no topo do `CONTEXTO.md` — o que diz o escopo da pasta —
já sumiu na mão de usuário real, em cinco pastas de uma vez, comido pelo próprio
agente ao reescrever o arquivo no fim da sessão. Quem passa por isso fica com uma
pasta que não abre e um arquivo que não sabe consertar.

Agora, toda sessão que abre bem tira uma foto dessa ficha. Se ela sumir, a
sessão seguinte **repõe sozinha** antes de abrir: a ficha volta, o corpo do
arquivo fica como estava, o arquivo anterior é guardado num `.bak` ao lado, e
um aviso diz o que foi reposto e de quando é.

Sem foto — pasta nova, cache limpo, máquina nova — nada muda: continua o
caminho de antes, com o Hermes conduzindo a configuração.

`koine mostrar` numa pasta assim avisa que a ficha será reposta, em vez de
recusar como se a sessão não fosse abrir.

**O que o Koine continua não fazendo:** inventar ficha. Ele nunca supõe escopo
nem escolhe domínio — só devolve o que aquele mesmo arquivo tinha antes.

### Adicionado — a pasta lembra com qual agente ela trabalha

Até aqui o agente vinha sempre pela linha de comando: `kn-claude leia projeto`.
Quem tem mais de um agente digitava o nome toda vez, e abrir sessão de um lugar
onde não dá para digitar — um celular, um provider remoto fixo — não tinha como
escolher o agente certo.

Agora a pasta declara o seu, no frontmatter do `CONTEXTO.md`:

```
agente: leia
```

E o launch resolve por precedência: **o que você digitou** (que vale só para
aquela sessão e **não fica gravado**) → **o que a pasta declara** → **o seu agente
default** → **Hermes**. Quem tem um agente só não precisa saber que isso existe.

Para gravar, um comando — nunca editando o YAML à mão:

```
koine definir-agente leia          # nesta pasta
koine definir-agente leia --default # como seu default
```

`koine mostrar`, sem argumento nenhum, responde qual agente a pasta vai abrir,
antes de abrir.

**Quando o nome não existe, o que acontece depende de onde ele veio.** Digitado
por você: erro na hora, com a lista dos que existem — há um humano no teclado, e
redigitar custa zero. Gravado num arquivo: a sessão sobe com o Hermes, que
recebe a instrução de conduzir a correção. Sem terminal interativo, a sessão
**não sobe** — abrir em silêncio com o agente errado é pior do que não abrir.

Fora de pasta configurada nada muda: pasta nova, vazia ou sem escopo continua
abrindo com o Hermes, que é quem sabe conduzir o conserto.

### Corrigido — correção de skill não chegava a quem já tinha o Koine instalado

A `kn-99-encerra-sessao` foi corrigida na v0.6.1, e em 27/08 a bancada Windows mostrou
que a correção **não chegava**: rodando o instalador por cima de uma instalação
anterior, a resposta era `Arquivos divergentes (use --force)` e a skill velha ficava
onde estava. Quem instalava do zero recebia; quem já usava o Koine, não.

A causa não era um bug pontual — eram **cinco células com três políticas**, escritas em
momentos diferentes e cada uma testada sozinha: `instalar` preservava divergente nos
dois lados; `atualizar` sobrescrevia o vault sem backup e **também** preservava a skill
no harness; `instalar-habilidades` preservava. Agora os três têm a mesma:

**divergiu → guarda o que estava lá, atualiza, e diz onde ficou.**

O backup vai para `~/.cache/koine/backups/<versão>/`, com o caminho impresso na saída —
**não ao lado do original**. Backup ao lado, dentro do vault, casa o filtro `kn-*` do
instalador de skills e é copiado para o harness **como se fosse uma skill**; no
OpenCode a entrada inválida sumiria em silêncio. Está guardado por teste que mede a
lista de skills que o usuário enxerga, não a ausência de um sufixo.

O que **não** mudou: `dominios/` continua sendo seu — preservado e reportado, salvo
`--force`. O `--force` do `instalar-habilidades` perdeu o objeto; continua aceito, e
avisa que virou desnecessário, em vez de recusar o comando de quem o tem no dedo.

Detalhe interno: `koine.backup` passa a ser o dono único da política de backup, que
existia duplicada em `conflito.py` e `ficha.py`. A versão que nomeia a pasta é a
**entrante**, trafegando por parâmetro — no `atualizar`, o pyz em execução ainda é o
antigo, e ler a versão no meio da cadeia gravaria o backup na pasta errada.

## [0.6.3] — 2026-08-27

### Corrigido — saída redirecionada no Windows derrubava o `koine instalar`

Com o stdout em console, o Python no Windows escreve por `WriteConsoleW` e todo
caractere passa. **Redirecionado** — para arquivo, num pipe, ou sob tarefa
agendada — o encoding vira o do locale (`cp1252` em pt-BR), e o primeiro `✓` das
mensagens levantava `UnicodeEncodeError`: o comando morria com traceback em vez
de instalar. Achado na bancada Windows rodando o `install.bat` por tarefa
agendada, logo depois da v0.6.2; atinge qualquer versão anterior.

Agora o CLI ajusta os fluxos de saída antes do primeiro `print`, pela correção
mínima: mantém o encoding do ambiente — quem for ler o arquivo depois lê no
encoding que espera — e troca só a política de erro para `replace`. Símbolo sem
correspondência vira `?`, acento continua acento, e nada aborta. Fluxo já em
UTF-8 fica intocado, com `errors=strict`, para que erro de encoding em ambiente
capaz continue visível.

## [0.6.2] — 2026-08-27

### Corrigido — `install.bat` deixa de depender do PowerShell

Numa estação Windows corporativa com o `powershell.exe` bloqueado por política, o
`install.bat` respondia `Acesso negado.` e parava — ele era só um wrapper de
`powershell -ExecutionPolicy Bypass -Command "iwr ... | iex"`, ou seja, dependia
exatamente do que a política bloqueia. Justo a máquina que precisa do `.bat` é a que
não conseguia usá-lo.

O `install.bat` agora é **100% `cmd.exe`** e faz o trabalho inteiro por conta própria,
espelhando o `install.sh`: acha o primeiro Python ≥ 3.12 (`py -3`, `python`,
`python3`), resolve a última release com `curl.exe`, baixa o `koine-<versão>.zip`,
extrai com `python -m zipfile` e delega ao `koine instalar`. O `install.ps1` continua
publicado para quem tem PowerShell liberado.

Junto:

- **Mensagem de erro por falha, em vez de saída críptica.** Sem `curl`, sem Python,
  versão não resolvida, download, criação de pasta, extração, pacote sem `koine.pyz` e
  falha do `koine instalar` têm cada um a sua mensagem — dizendo o que fazer e se algo
  foi tocado no disco. Guarda de teste impede rótulo mudo.
- **Arquivo em ASCII puro.** O `cmd.exe` lê `.bat` na codepage OEM (850/437); os
  acentos e travessões em UTF-8 dos comentários apareciam como mojibake na tela.
  Guarda de teste impede a recorrência.
- **`KOINE_VERSAO` aceita a versão com ou sem o `v`.** `0.6.2` e `v0.6.2` valem.
- **Separador restaurado na `kn-99`**, comido por uma edição da v0.6.1.
- **Orientação de PATH sem PowerShell.** O aviso de `~/.local/bin` fora do PATH — no
  `.bat` e na mensagem `cliente não encontrado` — passa a indicar
  `rundll32 sysdm.cpl,EditEnvironmentVariables`, que abre o editor de variáveis do
  usuário sem admin. A linha PowerShell continua listada como alternativa.

## [0.6.1] — 2026-08-23

### Corrigido — pasta com `CONTEXTO.md` sem `escopo:` deixa de ser beco sem saída

Abrir uma sessão numa pasta cujo `CONTEXTO.md` existe, é legível, mas não declara
`escopo:` encerrava com exit 1 e a instrução "corrija o frontmatter, ou remova/esvazie
o arquivo". Para quem não é técnico isso não é uma saída: é pedir edição de YAML, ou o
apagamento de um arquivo que pode ter trabalho dentro. O estado travou um usuário em
produção, e atualizar de versão não resolvia — a entrada do ramo é o conteúdo do
arquivo, que versão nenhuma toca.

Agora esse estado (`incompleto`) é auto-guiado, com uma regra dura: **o Koine não
toca no `CONTEXTO.md`** — escreve só o arquivo do harness (`CLAUDE.md`, `AGENTS.md`),
como em qualquer sessão, e nenhum symlink. A sessão sobe em modo bootstrap com Hermes, recebendo a
instrução `vault/bootstrap/pasta-incompleta.md` mais o `CONTEXTO.md` original — e o
Hermes conduz `/kn-02-mantem-catalogo` Fluxo 3b, que acrescenta o escopo preservando o
conteúdo existente.

O que **não** mudou: YAML irreparável continua erro amigável com arquivo, linha e
coluna; `gerar` e `mostrar` continuam recusando pasta incompleta sem materializar nada;
usuário não-onboardado continua sendo redirecionado a `koine instalar`.

Detalhe interno: `ContextoMontado` ganha o campo `instrucao_path`, renderizado pelos
cinco adapters. `mensagens.contexto_malformado` deu lugar a `contexto_ilegivel`, que
descreve o caso que sobrou (arquivo binário, permissão, encoding).

### Corrigido — a Ficha Koine se perdia no fechamento de sessão, e o `validar` não via

Investigando o caso acima na máquina do usuário, o buraco maior apareceu: não faltava
a linha `escopo:` — faltava o bloco `---` inteiro, e **cinco pastas** estavam assim.
Os carimbos de tempo apontaram o fechamento de sessão: o `CONTEXTO.md` reescrito um
minuto depois do diário.

**Produtor.** A `/kn-99-encerra-sessao` mandava "edita `CONTEXTO.md` direto" em três
pontos e nunca mandava preservar a ficha — um agente que reescreve o arquivo "com a
seção nova" leva o frontmatter junto. Agora a regra é explícita (editar por
acréscimo, nunca reescrever o arquivo inteiro) na `/kn-99`, na `/kn-11` e na `/kn-13`,
que são as que editam por acréscimo. A `/kn-99` ganhou também uma **Rodada 5 —
Verificação de efeito**: rodar `koine validar` antes de encerrar, enquanto o usuário
ainda está em sessão e o conteúdo ainda está fresco.

**Detector.** `koine validar` respondia "nenhum problema encontrado" para exatamente
o arquivo que impede a sessão de abrir — só enxergava YAML irreparável e valor mal
citado. Ganhou o terceiro achado, **sem ficha**: `CONTEXTO.md` sem `escopo:`, inclusive
quando o bloco sumiu inteiro. `bootstrap: true` não é achado, e demais `.md` não
precisam declarar escopo. `--corrigir` não mexe nesses arquivos — escolher o escopo é
decisão do usuário, e a saída é abrir sessão na pasta.

O critério passou a viver num lugar só (`bootstrap.estado_do_fm`), lido pelo launch e
pelo `validar`: a ferramenta que avisa antes não pode divergir da que barra na hora.

## [0.6.0] — 2026-08-18

### Adicionado — `/kn-13-sabatina-plano`, a skill de entrevista

Skill nova no vault, a décima primeira. Conduz uma sabatina: entrevista o usuário sobre
um plano, um processo ou uma ideia até a coisa ficar explícita, uma pergunta por vez e
sempre com a recomendação do agente junto da pergunta.

O que a diferencia de uma conversa é a conferência. Na abertura da sessão o usuário
declara contra o que o agente vai checar o que ele afirmar — a planilha que usa hoje, o
relatório do sistema, o procedimento escrito, o contrato, o código. Quando a descrição e
o artefato divergem, o agente mostra a divergência. É por isso que a skill alcança
trabalho sem código nenhum: um processo administrativo tem evidência tanto quanto um
repositório tem.

Enquanto a conversa acontece, o vocabulário resolvido é gravado no `GLOSSARIO.md` no
mesmo turno, e a decisão que passa em três critérios — difícil de reverter, surpreendente
sem contexto, resultado de compromisso real — vira registro com as alternativas recusadas
e o motivo de cada recusa. Zero decisão registrada é resultado normal.

A entrevista roda em qualquer pasta, inclusive numa sem `CONTEXTO.md`. O que o estado da
pasta muda é apenas **onde** o resultado é gravado, e isso o usuário decide: alcance de
pasta deixa glossário e decisão na pasta de trabalho; alcance de escopo manda o glossário
para a pasta-referências e a decisão para uma referência `type: Decisao` via `/kn-11`.
Default seguro é pasta.

Glossário de escopo ganha uma seção `## Glossário` no arquivo do escopo apontando o
caminho — assim toda sessão sabe que ele existe sem pagar o conteúdo inteiro em cada
prompt.

Passo a passo em [Sabatinar um processo](docs/guias/sabatinar-um-processo.md).

Adaptada de `mattpocock/skills` `grill-with-docs`, licença MIT, com atribuição preservada.

### Adicionado — guarda sobre o contrato de skill do OpenCode

O OpenCode descarta em silêncio uma skill cujo `name` no frontmatter não casa o nome do
diretório, ou cuja `description` esteja fora de 1..1024 caracteres. Sem erro, sem aviso:
a skill simplesmente não aparece. O vault inteiro passa a ser guardado por teste contra
os dois casos.

### Corrigido — documentação dizia symlink onde o código copia

O catálogo de habilidades e o mapa de arquitetura descreviam as skills como symlinkadas
no harness, herança da implementação em Go. A versão Python **copia**, porque symlink no
Windows exige privilégio de administrador que o público-alvo não tem.

## [0.5.3] — 2026-08-18

Dois defeitos que só existem no Windows, achados na mesma bancada com AppLocker.
O CI é POSIX-only e não alcançava nenhum dos dois.

### Corrigido — sessão OpenCode no Windows com PowerShell restrito

Em máquina Windows onde a política corporativa bloqueia o `powershell.exe`, o primeiro
comando de uma sessão `kn-opencode` morria com erro de `uv_spawn`: o OpenCode tentava
levantar o shell padrão dele e o shell padrão não era executável ali. Os tools nativos
(`read`, `write`, `edit`, `grep`) seguiam funcionando; o que parava era o `bash` tool e
o terminal — ou seja, git, instalação de pacote, qualquer comando.

- **O Koine declara o shell.** No Windows, o JSON que o adapter já gera por sessão passa
  a trazer `"shell": "cmd"`. Vale também na primeira sessão de uma pasta (bootstrap).
  Fora do Windows nada muda: o shell do sistema continua sendo o do sistema.
- **Nenhum arquivo do usuário é tocado.** A chave entra no JSON do próprio Koine, que o
  OpenCode mescla acima da configuração global e **abaixo** da configuração de projeto —
  quem quiser outro shell num projeto específico continua podendo declarar.

### Corrigido — `CONTEXTO.md` somente-leitura não acumula mais `.bak`

Achado na mesma bancada Windows. Com o arquivo marcado `attrib +R`, o Koine gravava o
backup **antes** de tentar a escrita: criar arquivo novo na pasta não é barrado pelo
atributo, então o `.bak` sempre nascia e a escrita sempre falhava. Como o arquivo seguia
torto, a sessão seguinte repetia tudo — `CONTEXTO.md.bak`, `.bak.1`, `.bak.2`, sem fim.
É o cenário de máquina corporativa, onde o arquivo somente-leitura é a regra.

- **A permissão é checada antes do backup**, não descoberta pela escrita estourando.
  Nada é criado quando não há como gravar.
- **Um aviso, e o que nomeia a causa.** Antes saíam dois — o da escrita que falhou e o do
  reparo em memória, de subsistemas diferentes. O segundo mandava "citar o valor entre
  aspas duplas", conselho impossível num arquivo que o usuário não pode editar. Agora sai
  só o que diz que o arquivo está somente-leitura e que a sessão segue.

## [0.5.2] — 2026-08-11

### Corrigido — frontmatter escrito à mão não derruba mais o Koine

`descricao: Vendas B2B: acompanhamento e metas` — dois-pontos sem aspas, a forma
natural de escrever em português — matava o launch inteiro com um `ScannerError` de
20 linhas antes de o cliente IA abrir. Reproduzido em produção em máquina de usuário.

- **Leitura tolerante.** `frontmatter.ler` tenta o parse estrito e, só quando ele
  falha, recita o valor das linhas `chave: valor` que sozinhas não parseiam. Cada
  linha é testada isolada: uma linha já válida no mesmo bloco (`descricao: "Vendas:
  meta"`) atravessa intacta. O reparo nunca roda sobre arquivo que já é válido.
- **Aviso em vez de silêncio.** Quando repara, o Koine avisa no stderr nomeando o
  arquivo e o campo — tolerar dado ruim não é escondê-lo.
- **Erro nomeado no que não tem reparo.** TAB, indentação quebrada e frontmatter que
  não é `chave: valor` viram `FrontmatterInvalido` com arquivo, linha e coluna, e uma
  mensagem que explica onde pôr a mão. Antes, o segundo caso estourava `AttributeError`.
- **Rede em todo o caminho de launch.** As seis leituras de frontmatter
  (CONTEXTO.md ×3, escopo ×2, domínio) estavam desprotegidas; a v0.4.6 tinha coberto
  só o walker do índice. `classificar` degrada para `malformado` em vez de propagar.
- **Escopo inexistente também deixou de ser traceback.** `escopo:` apontando para um
  slug que não existe agora lista os escopos cadastrados.

### Adicionado — `koine validar [pasta]`

Varre o frontmatter da config do usuário e da pasta e reporta o que está torto, sem
escrever nada: **⚠ reparável** (o Koine lê, mas o arquivo segue inválido para outras
ferramentas) e **✗ inválido** (com linha e coluna). Sai `1` quando há achados.

Contrapartida necessária do reparo: sem ele, o arquivo torto no disco nunca seria
corrigido — só remendado a cada leitura.

### Adicionado — o arquivo torto é consertado, não só remendado

Reparar na leitura não conserta nada: o arquivo no disco continua inválido para
qualquer outra ferramenta, e o usuário nunca fica sabendo que há o que corrigir.
Agora o Koine escreve a correção.

- **No launch**, os arquivos de configuração que ele carrega (`CONTEXTO.md` da
  pasta, escopo, domínio) são normalizados no disco — máquina que escreveu YAML
  torto se cura na primeira sessão, sem comando nenhum. Só a linha do valor sem
  aspas muda; o original vai para `.bak`.
- **`koine validar --corrigir`** faz o mesmo em lote, aí sim incluindo a
  pasta-referências do escopo. Ela fica fora do automático de propósito:
  reescrever a base de conhecimento do usuário é coisa que só se faz a pedido.
- O que o Koine **não** sabe consertar nunca é reescrito, e o documento remendado
  é reparseado antes de ser gravado — a correção automática não tem caminho para
  produzir algo pior que o original.
- Valor citado sai entre aspas duplas, como a documentação sempre recomendou;
  aspas simples só quando o valor tem `"` ou `\` (caminho do Windows entre aspas
  duplas vira escape inválido).
- O gerador de índice passou a emitir o próprio frontmatter pelo compositor: um
  domínio chamado `vendas: b2b` fazia o Koine gravar YAML inválido em arquivo
  gerado por ele mesmo.

### Alterado

- Skills que escrevem frontmatter (`kn-01`, `kn-03`, `kn-11`, `kn-21`, `kn-99`) citam
  `title`/`description`/`descricao` com aspas duplas no template e explicam por quê.
  Era o próprio Koine ensinando o usuário a escrever o YAML que derrubava o Koine.
- Referência com dois-pontos sem aspas passa a **entrar** no `kn-indice` (reparada)
  em vez de ser pulada com aviso, como fazia desde a v0.4.6.

## [0.5.1] — 2026-08-11

### Ferramentas externas da família `kn-2N`

As skills de marca dependem de duas ferramentas que **não vêm no pacote do Koine** — instale só o ramo que for usar. O `/kn-21-escreve-design` funciona sem nenhuma das duas (precisa apenas de Node.js, para o linter do schema).

**`imagio`** — geração de imagem, usado pelo `/kn-22-gera-imagem`. Python 3.12+.

```bash
pipx install git+https://github.com/jrunic/imagio.git@production
imagio instalar
```

O `imagio instalar` verifica o ambiente e conduz a configuração da credencial; ele não instala o próprio pacote. Cada geração é uma chamada paga ao provedor — no backend `gemini`, exige créditos pré-pagos.

**`prelo`** — Markdown em PDF de marca, usado pelo `/kn-23-gera-marca-prelo` e pelo `/kn-24-gera-pdf`. Node.js 22+, versão mínima **1.2.1**.

```bash
git clone https://github.com/jrunic/prelo
cd prelo
npm install                              # inclui o Chrome do Puppeteer
npm run fonts
ln -s "$PWD/cli.js" ~/.local/bin/prelo
```

As versões mínimas do prelo têm consequência visível: abaixo da **1.2.0**, imagem com caminho relativo renderiza quebrada e o comando ainda reporta sucesso; abaixo da **1.2.1**, uma marca com logo perde o arquivo na instalação e a regra CSS aponta para o vazio.

Passo a passo completo em [A marca do escopo](docs/guias/marca-do-escopo.md).

### Changed

- **Skills `kn-*` são de todo agente, não do Hermes.** A referência de habilidades afirmava que agentes operacionais derivados "normalmente não invocam skills `kn-*`" — contradizendo o próprio método, já que `conceitos/agentes.md` diz que tecnicamente todos podem invocar tudo. A regra correta: as skills são do método e estão disponíveis em qualquer sessão; o Hermes é o agente **recomendado** para as operações do próprio Koine, sobretudo as de grande monta, não o único autorizado.
- **`/kn-99-encerra-sessao` fecha toda sessão, com qualquer agente.** Era descrito como oferta condicional ("oferece `/kn-99` se houve algo catalogável") no `KOINE.md`, no arquivo do Hermes e no template de agente derivado da `/kn-03-cria-agente`. Passa a ser padrão de fechamento — sessão que não fecha assim não vira memória para o usuário do futuro. Agentes derivados criados a partir de agora nascem com o encerramento como padrão.
- **Guia novo — [A marca do escopo](docs/guias/marca-do-escopo.md).** As quatro skills da família `kn-2N` estavam documentadas isoladamente, sem que se enxergasse a sequência entre elas. O guia cobre pré-requisitos por ramo (o `imagio` só importa para imagem; o `prelo` só para PDF), as versões mínimas e por que elas não são detalhe, onde cada artefato mora, e uma tabela de sintoma → causa para o que costuma sair errado.
- **`docs/tutoriais/onboarding-completo.md`** dizia "5 skills" em dois pontos, defasado desde a entrada da `kn-12` em julho. A tabela de skills úteis ganhou as quatro da família `kn-2N`.
- **ADR `20260621` §13** recebeu emenda datada registrando a subdivisão da faixa cotidiana (`kn-11`–`kn-19` genérica, `kn-21`–`kn-29` marca e design, `kn-31`–`kn-89` reservado). A decisão original não muda — subdividir é o que o espaço entre faixas previa.

## [0.5.0] — 2026-08-11

### Added

- **Família `kn-2N` — marca e design.** Quatro skills novas no vault, para escopos que produzem material visual:
  - `kn-21-escreve-design` — escreve o `DESIGN.md` da marca na pasta-referências do escopo. Varre o que já existe (CSS do projeto, manual de marca, site) antes de entrevistar. Frontmatter híbrido: as chaves da Ficha Koine e o schema `@google/design.md` convivem no mesmo bloco, verificado nas duas direções (o linter aceita as chaves extras; o gerador de índice cataloga o arquivo normalmente).
  - `kn-22-gera-imagem` — compõe o prompt a partir do `DESIGN.md` e gera imagem via [`imagio`](https://github.com/jrunic/imagio). Prompt aprovado pelo usuário antes de toda chamada, porque cada execução gasta dinheiro; prompts de série ficam registrados na marca para que as peças seguintes saiam coerentes.
  - `kn-23-gera-marca-prelo` — deriva `tokens.css` + `config.json` + fontes para o [`prelo`](https://github.com/jrunic/prelo), fazendo Markdown virar PDF na identidade da marca. Emite só a camada de tokens: a estrutura visual pertence à ferramenta.
  - `kn-24-gera-pdf` — converte um `.md` do trabalho em PDF de marca. Confere que cada imagem local existe **antes** de converter: o prelo avisa no stderr mas sai com código 0, e a política aqui é não entregar documento furado. Tamanho de PDF não diagnostica — medimos o arquivo com imagem quebrada em 23,4 KB contra 18,4 KB do correto, porque o ícone de imagem quebrada também é um objeto de imagem. Requer `prelo` ≥ 1.2.0, que resolve caminho relativo contra a pasta do `.md`; a skill converte o arquivo original direto, sem cópia de render.

### Changed

- **`docs/referencias/habilidades.md`** passa a documentar as 10 skills do vault. A referência dizia "5 skills" e omitia a `kn-12-prepara-contexto`, presente desde julho. A tabela de numeração ganhou a faixa `kn-21`–`kn-29` (marca e design) e explicitou `kn-31`–`kn-89` como reservado.

## [0.4.7] — 2026-07-30

### Fixed

- **`koine atualizar` falhava com `SSL: CERTIFICATE_VERIFY_FAILED` no macOS** — o OpenSSL do Python (stdlib) não achava o bundle de CA e a atualização abortava logo no passo de resolver a última versão, sem recuperação. O fallback via curl do sistema existia mas estava restrito ao Windows. Agora vale em **qualquer plataforma** (Keychain no macOS, Schannel no Windows, CA bundle no Linux) e cobre também `resolver_versao` — que antes não tinha fallback nenhum. `koine atualizar` passa a se autocurar onde o curl do SO alcança a rede. Reproduzido em produção (macOS). Observação: como o próprio `atualizar` é o que quebra, máquinas já travadas se recuperam reinstalando via `install.sh` (que é 100% curl); a partir da 0.4.7 o problema não recorre.

## [0.4.6] — 2026-07-30

### Fixed

- **Um arquivo de referência com frontmatter inválido derrubava o launch inteiro** — abrir uma sessão (`kn-<cliente> <agente> <pasta>`) falhava com traceback cru de `yaml.scanner.ScannerError` quando qualquer `.md` da pasta-referências do escopo tinha YAML malformado — tipicamente uma `description` não-citada com dois-pontos-espaço no meio (ex.: `description: Ferramenta instalada e funcional: gog v0.34.1`). Reproduzido em produção. O gerador de índice agora **isola por arquivo**: cataloga o resto da pasta e emite um `aviso:` no stderr nomeando o arquivo a corrigir, em vez de abortar a sessão.

### Changed

- **`kn-11-mantem-referencia` passa a citar `title` e `description` com aspas duplas** no template de materialização, eliminando na origem o YAML inválido que a skill podia gerar quando a `description` continha dois-pontos.

## [0.4.5] — 2026-07-24

### Added

- **Flags do usuário são repassadas ao cliente IA** — os wrappers `kn-<cliente>` passam a aceitar flags que vão direto para o cliente lançado. Ex.: `kn-claude hermes . --chrome` liga a integração "Claude in Chrome" naquela sessão; `kn-codex hermes . --model o3` idem para o Codex. O usuário escolhe quando ligar cada flag — o Koine separa os posicionais (agente, pasta) das flags (prefixo `-`) e repassa o resto ao launch (`execvpe` no Unix, `cmd /c` no Windows). Flags com valor podem ir após `--` literal (`kn-claude hermes . -- --model sonnet`). As flags do usuário compõem com as `EXTRA_ARGS` do adapter (ex.: o `-c` do Codex), sem substituí-las.

### Fixed

- **Abrir sessão numa pasta sem `CONTEXTO.md` configurado dava traceback Python** — lançar um cliente (`kn-<cliente> <agente> <pasta>`) numa pasta de trabalho nova, sem `CONTEXTO.md` (ou com o arquivo vazio), falhava com `FileNotFoundError`/`KeyError` cru em vez de guiar o usuário. Reproduzido em produção em ambiente Windows corporativo. Agora o launch **auto-guia**: se o usuário já fez onboarding, o Koine materializa um `CONTEXTO.md` de bootstrap e o Hermes conduz a criação do contexto real da pasta via `/kn-02-mantem-catalogo` (Fluxo 3); se ainda não fez onboarding, orienta a rodar `koine instalar` + `kn-<cliente> hermes koine` (sem disparar o onboarding `/kn-01` numa pasta arbitrária). `CONTEXTO.md` com conteúdo mas frontmatter incompleto (sem `escopo:` nem `bootstrap:`) é **preservado** com mensagem de correção — nunca sobrescrito.

### Changed

- **`gerar`/`mostrar` numa pasta sem `CONTEXTO.md` válido falham com mensagem amigável** — antes propagavam o mesmo traceback do launch. Comandos administrativos não materializam nada; orientam a configurar a pasta abrindo uma sessão com o Hermes.

## [0.4.4] — 2026-07-21

### Fixed

- **Onboarding `kn-01-recebe-usuario` pedia o nome três vezes** — a abertura da skill perguntava "como você gostaria que eu te chamasse?" e a Rodada 1 repetia a mesma pergunta (item 2), somada ao "nome completo" (item 1), resultando em três perguntas de nome em sequência. A abertura agora coleta apenas o número do personagem-âncora; o nome é coletado uma única vez em cada campo distinto da Rodada 1 (nome completo + como te chamar).

## [0.4.3] — 2026-07-21

### Added

- **Comando `koine atualizar`** — self-update para a última release (ou versão fixada em `KOINE_VERSAO`), baixando o `.zip` do github (ou de `KOINE_BASE_URL`), verificando `SHA256SUMS`, e reaproveitando o caminho de instalação: refresca o vault shipped preservando os `dominios` do usuário, regenera os wrappers e reinstala skills nos harnesses detectados. Execução 100% Python — nenhum `.bat`/`.ps1`/powershell — para políticas corporativas que bloqueiam executáveis e powershell. Auto-troca do pyz é in-process no POSIX e delegada a um processo-filho da versão nova no Windows (stdio em log, sem trampolim batch). No-op quando já na versão-alvo; `--force` reinstala.
  - **Limitação/mitigação de SSL no Windows** — o OpenSSL da stdlib do Python não busca o CA intermediário via AIA, então o download direto do github pode falhar em Windows sem a cadeia completa no store (comum em máquina recém-instalada; máquina corporativa gerenciada costuma ter a cadeia provisionada). Mitigação: no Windows o download cai para o `curl.exe` do sistema (usa Schannel, que faz AIA); se o `curl` também falhar, a mensagem orienta a rodar Windows Update ou usar `KOINE_BASE_URL` apontando para um espelho. Validado em Windows 11 ARM sob AppLocker (powershell bloqueado, usuário restrito): resolução de versão, download por espelho e a auto-troca do pyz funcionam; o download direto do github depende do fallback curl.

### Fixed

- **Agente de usuário não carregava (regressão do port Python)** — `contexto.resolver` procurava agentes só em `vault/agentes` (`~/.local/share/koine/`), onde vive apenas o `hermes` distribuído. Agentes criados pela `kn-03-cria-agente` moram em `config/agentes` (`~/.config/koine/`) e nunca eram achados — em qualquer OS. O path era montado sem validar existência, então seguia silencioso e o agente simplesmente não entrava no contexto da sessão. A série Go lia do `config` (por isso o defeito não aparecia até rodar o build Python). Agora `_achar_agente` busca `config/agentes` primeiro (override do usuário) e `vault/agentes` depois (distribuído). Afeta os 5 adapters — `resolver` é compartilhado.
- **Resolução do agente é case-insensitive** — o nome vinha do arg do CLI com a caixa crua (`Leia`), mas o slug em disco é lowercase (`leia.md`). Casar por caixa crua só resolvia em FS case-insensitive (macOS/Windows), sumindo o agente em FS case-sensitive (Linux/OpenClaw). O match agora ignora caixa contra os arquivos reais.

### Changed

- **Agente ausente falha alto** — nome que não casa com nenhum agente agora levanta `AgenteNaoEncontrado` (tipada, carrega o nome pedido + lista de disponíveis unindo usuário e distribuídos); `cli`/`mensagens` decidem prosa e política. Antes: path inexistente propagado em silêncio. Padrão `ClienteNaoEncontrado`/`ClienteNaoExecutavel`.

## [0.4.2] — 2026-07-16

### Fixed

- **Windows WinError 193 (resolução robusta do cliente)** — no Windows o launch agora invoca o cliente via `cmd /c <cliente>` pelo nome, deixando o `cmd.exe` aplicar a mesma resolução PATHEXT do shell interativo. O guard `.bat`/`.cmd` da 0.4.1 não bastava: o `shutil.which` podia devolver uma variante que o `CreateProcess` recusava (WinError 193) mesmo havendo um `.cmd`/`.exe` válido ao lado. Se o cliente roda quando digitado no terminal, agora roda pelo `kn-<cliente>`.

### Changed

- **Erros de lançamento amigáveis** — cliente ausente no PATH e cliente encontrado-mas-não-executável agora produzem mensagens orientadas (diagnóstico + correção por OS) em vez de traceback Python. Exceções tipadas (`ClienteNaoEncontrado`, `ClienteNaoExecutavel`) carregam dados; a prosa vive em `mensagens`.

## [0.4.1] — 2026-07-16

### Fixed

- **Windows WinError 193** — `launch.lancar` agora envolve wrappers `.bat`/`.cmd` com `cmd /c` antes de passar ao `subprocess.run`. CLIs Python instalados via pip/pipx no Windows criam wrappers batch que o `CreateProcess` não consegue executar diretamente.

## [0.4.0] — 2026-07-08

O flip do Python: o Koine passa a ser distribuído como aplicação Python (`koine.pyz`), substituindo os binários Go. Mesmos comandos `kn-*`, mesmo comportamento, mesmo estado em disco — upgrade da v0.3.x não exige migração.

### Added

- **Distribuição Python** — asset `koine-<versão>.zip` com `koine.pyz` (zipapp de stdlib pura — sem `.so`/`.pyd`/`.dll`) e `vault/` lado a lado. Requer Python ≥ 3.12. Sem executável compilado: nada para o antivírus bloquear além de código-fonte.
- **Comando `koine`** — wrapper administrativo (`koine versao`, `koine instalar`, `koine instalar-habilidades`, `koine gerar`, `koine mostrar`) substitui o `kn-agente`.
- **Modo interativo do `instalar`** portado por completo: prompt de pasta canônica com default `~/koine`, alias `koine`, `CONTEXTO.md` de bootstrap, detecção de harness com confirmação `[S/n]` e mensagem orientativa quando nenhum cliente IA é detectado.
- **Marker-check no working dir** — arquivo regular pré-existente SEM o marcador Koine no caminho de um artefato a gerar vai para backup `.bak` (`.bak.1`, `.bak.2`, … — nunca sobrescreve backup) com aviso de uma linha; COM marcador (ou assinatura retrocompatível das versões antigas) é regenerado silenciosamente. Paridade final com o conflito da série Go; arquivos gerados pelo Go são reconhecidos pelo Python e vice-versa.
- **Upgrade sobre instalação Go** — `koine instalar` reconhece os symlinks `kn-*` → `kn-agente` criados pela v0.3.x e os substitui pelos wrappers Python. Qualquer outro conteúdo pré-existente no caminho é preservado com aviso. `~/.config/koine/` e `~/.local/share/koine/` são lidos como estão — escopos, aliases e agentes intactos.

### Changed

- **Installers reescritos** — `install.sh`, `install.ps1` e `install.bat` agora: localizam um Python ≥ 3.12 no PATH (Unix: `python3.13`/`python3.12`/`python3`/`python`; Windows: `py -3`/`python`/`python3`), baixam `koine-<versão>.zip` da release, extraem para `~/.local/share/koine/dist/` e delegam ao `koine instalar`. Sem Python ≥ 3.12, terminam com orientação de instalação e **nada é instalado** (sem estado parcial).
- **Pipeline de release** — o CI roda a suíte Python completa (incluindo os testes de paridade, com o oráculo Go compilado do fonte do repo), valida que a versão do pacote confere com a tag e publica o pacote Python. Falha de teste bloqueia a publicação.

### Removed

- **Binários Go dos assets de release** — `kn-agente-darwin-*`, `kn-agente-linux-*` e `kn-agente-windows-*.exe` não são mais distribuídos. A série Go permanece disponível nas tags `v0.3.x`.

### Notes

- **Modo skills continua como fallback** (`koine-skills.zip`) para ambientes que bloqueiam até o interpretador Python — instalação e operação inalteradas desde a 0.3.2.
- Os caveats de assinatura/notarização das releases anteriores deixam de se aplicar: não há mais binário compilado na distribuição.

## [0.3.2] — 2026-07-07

Modo skills dual-mode: o Koine passa a operar também **sem o binário**, para ambientes que bloqueiam executáveis. Além dos binários, a release agora distribui `koine-skills.zip`.

### Added

- **Modo skills (dual-mode)** — distribuição alternativa sem binário: o Claude Code carrega o contexto Koine via skills e `@path` relativo, sem `kn-agente`. Para ambientes corporativos que bloqueiam `.exe`.
- **Skill `kn-12-prepara-contexto`** — gera o `CLAUDE.md` da pasta de trabalho e os índices de domínio sem o binário, replicando a resolução e a geração do `kn-agente`.
- **Instaladores do modo skills** — `instalar-koine.bat` (Windows: cria os diretórios XDG e copia vault + skills) e `instalar-koine.md` (guia executável por agente, com auto-teste de filesystem).
- **`koine-skills.zip` como asset de release** — montado no CI e anexado à release, ao lado dos binários.

### Changed

- **Skills `kn-01`, `kn-02`, `kn-03`, `kn-11`** — passam a contemplar o modo skills além do modo binário, qualificando a invocação por modo.

## [0.3.1] — 2026-07-02

Patch de compatibilidade. Binários recompilados com Go 1.26 para suporte a macOS 26 (Tahoe / Darwin 25).

### Fixed

- **Go 1.22 trava em macOS 26 (Darwin 25)** — o runtime Go 1.22 entra em deadlock durante inicialização em Darwin 25 antes de qualquer código de usuário rodar: sem output, sem goroutine dump no SIGQUIT. Causa raiz: mudança no scheduler de threads do macOS 26. Atualização para Go 1.26 resolve. Usuários em macOS 26 que instalaram versões anteriores devem reinstalar com `install.sh`.

## [0.3.0] — 2026-06-30

Terceira release pública. Codex CLI suportado como quinto harness e melhoria de
UX no tratamento de conflito de arquivos. Cobertura: PR #8.

### Added

- **Adapter Codex CLI (`kn-codex`)** — quinto harness suportado. Gera `AGENTS.md` com conteúdo **inline** (usuário, KOINE, agente, escopo, índices) porque o Codex injeta o texto literal do `AGENTS.md` em vez de resolver `@path` nativamente como Claude/Antigravity; o inline garante a injeção do contexto. Passa `-c project_doc_max_bytes=1048576` para não truncar bundles acima de 32 KiB. `CONTEXTO.md` permanece arquivo separado (snapshot inline + prosa apontando o arquivo mutável). Symlink `kn-codex` criado em `kn-agente instalar`; cliente listado no onboarding. PR #8.
- **Skills `kn-*` instaladas para o Codex** em `~/.agents/skills` (path USER de skills do Codex); `codex` adicionado à detecção automática de harness e a `instalar-habilidades --para=codex`. PR #8.

### Changed

- **Tratamento de conflito faz backup em vez de erro** — arquivo pré-existente não gerado pelo Koine no destino do working dir (`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`) é movido para backup (`.bak`, depois `.bak.1`, `.bak.2`, … — nunca sobrescreve backup existente) e a sessão prossegue, com aviso de uma linha — em vez do erro duro que exigia `--substituir`. Vale para todos os wrappers via o resolvedor de conflito compartilhado. `--substituir` passa a significar "sobrescrever sem backup". Estados ambíguos (diretório, symlink com alvo divergente) continuam retornando erro. PR #8.

### Notes

- Caveats de assinatura permanecem da 0.2.0: binários macOS não notarizados e Windows não assinados (ver release 0.2.0 para mitigações).

## [0.2.0] — 2026-06-28

Segunda release pública. Onboarding um-comando, install scripts cross-platform,
schema CONTEXTO.md com flag `bootstrap`, skill `/kn-01-recebe-usuario` reescrita
com 4 personagens-âncora, pipeline de release automatizado. Cobertura: PRs #1
a #6 (mergeadas entre 2026-06-26 e 2026-06-28).

### Added

- **Install scripts** publicados como assets do GitHub Release: `install.sh` (Unix), `install.ps1` (Windows PowerShell), `install.bat` (Windows cmd com `-ExecutionPolicy Bypass` inline para contornar restrições corporativas). PR #4.
- **Pasta canônica em `kn-agente instalar`**: cria pasta com prompt-com-default (default `~/koine`), registra alias `koine` em `~/.config/koine/aliases.json`, gera `CONTEXTO.md` de bootstrap a partir de embed `vault/bootstrap/CONTEXTO.md`. PR #3.
- **Schema `CONTEXTO.md` com flag `bootstrap: true`** — campo opcional retrocompatível; `Resolver()` bypassa validação de escopo/dominios quando setado; emite warning se agente solicitado != Hermes. ADR `docs/decisoes/20260627-bootstrap-flag-em-contexto-md.md`. PR #3.
- **Bootstrap explícito nos 4 adapters de harness** (Claude, Antigravity, Copilot, OpenCode): carregam corpo do `CONTEXTO.md` no contexto do cliente IA quando `bootstrap: true` está presente. PR #3.
- **Pipeline de release automatizado** em `.github/workflows/release.yml`: cross-compile para `darwin-arm64`/`darwin-amd64`/`linux-amd64`/`windows-amd64`, gera `SHA256SUMS`, publica binários + scripts + checksums em GitHub Release ao push de tag `v*`. PR #2.
- **Mensagem orientativa quando zero clientes IA detectados** em `kn-agente instalar`: bloco Node.js (se ausente, com comandos por OS), bloco Homebrew (se ausente em macOS), lista dos 4 clientes IA suportados com comando de instalação por OS. PR #4.
- **Tutorial passo a passo** `docs/tutoriais/onboarding-completo.md` cobrindo do install até o primeiro agente operacional configurado, com resolução de problemas. PR #6.
- **Referência das 5 skills** em `docs/referencias/habilidades.md` com tabela compacta + sub-seções detalhadas (trigger, inputs, outputs, skills relacionadas). PR #6.
- **Dependência `golang.org/x/term`** para detecção de terminal cross-platform (PATH não atualizado, modo interativo vs CI). ADR `docs/decisoes/20260626-golang-x-term-deteccao-terminal.md`. PR #1.

### Changed

- **`/kn-01-recebe-usuario` SKILL.md reescrito** com 4 personagens-âncora (Bruce Wayne, Hermione Granger, Indiana Jones, Princesa Leia) em respostas inline lado-a-lado por pergunta — zero adaptação mental do agente. Formato padronizado: `Formato esperado`, `Como será usada`, `Se não souber`. Vocabulário pt-BR (apelido, cabeçalho, caminho, pasta padrão). Rodada 4 delega para `/kn-03-cria-agente` sem duplicar entrevista. Mensagem final usa `kn-<cliente>` dinâmico. Ao final do onboarding, reescreve `CONTEXTO.md` de bootstrap substituindo `bootstrap: true` por escopo `koine` permanente + cria `~/.config/koine/escopos/koine.md`. PR #5.
- **`kn-agente instalar` detecta harnesses no PATH** e oferece instalação de skills `kn-*` com prompt `Y/n`; aceita flag `--para=<harness>` para bypass. PR #1.
- **`harnessSuportados` expandido** para os 4 clientes IA: `claude` → `.claude/skills`, `agy` → `.gemini/antigravity-cli/skills`, `copilot` → `.copilot/skills`, `opencode` → `.config/opencode/skills`. PR #1.
- **`docs/referencias/cli.md` atualizado** com as 5 fases de `kn-agente instalar` e a distinção entre bootstrap implícito (sem CONTEXTO.md) e bootstrap explícito (com `bootstrap: true`). PR #6.

### Removed

- **`docs/tutoriais/instalacao-primeira-sessao.md`** — substituído por `onboarding-completo.md` (fluxo manual obsoleto). PR #6.

### Notes

- Binários macOS ainda não são notarizados; usuário pode ver alerta "Apple não pôde verificar" na primeira execução. Mitigação: `xattr -d com.apple.quarantine ~/.local/bin/kn-agente`.
- Binários Windows ainda não são assinados; pode disparar SmartScreen. Mitigação: comparar SHA-256 com `SHA256SUMS` publicado no release.
- Schema do `CONTEXTO.md` permanece retrocompatível: arquivos sem `bootstrap:` continuam funcionando como antes.
- Pre-release `v0.2.0-rc1` foi pulada — `v0.2.0` é o primeiro release público com binários e scripts.

## [0.1.0] — 2026-06-26

Initial public release.

### Added

- `kn-agente` administrative CLI: `instalar`, `mostrar`, `gerar`, `versao`.
- Client wrappers: `kn-claude`, `kn-agy` (Antigravity), `kn-copilot` (GitHub Copilot CLI), `kn-opencode`.
- Four-layer context model: user, agent, references, working-directory context.
- Embedded vault distributed with the binary.
- Five `kn-*` skills: catalog onboarding, catalog maintenance, agent creation,
  reference upkeep, session closure.
- XDG-compliant directories: `~/.config/koine/`, `~/.local/share/koine/`, `~/.cache/koine/`.
- Bootstrap mode for working directories without `CONTEXTO.md`.
- Cross-platform cache for Copilot and OpenCode adapters
  (`COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, `OPENCODE_CONFIG`).
- Marker-based conflict detection for files touched by adapters
  (`--substituir` flag opts in to overwrite).
- Folder resolution cascade (alias, direct path, fuzzy match with menu).

### Notes

First public release. API, on-disk layout, vault contents and adapter
behavior may evolve until 1.0.

[Unreleased]: https://github.com/jrunic/koine/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/jrunic/koine/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/jrunic/koine/compare/v0.6.3...v0.7.0
[0.5.3]: https://github.com/jrunic/koine/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/jrunic/koine/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/jrunic/koine/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/jrunic/koine/compare/v0.4.7...v0.5.0
[0.4.0]: https://github.com/jrunic/koine/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/jrunic/koine/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/jrunic/koine/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/jrunic/koine/releases/tag/v0.3.0
[0.2.0]: https://github.com/jrunic/koine/releases/tag/v0.2.0
[0.1.0]: https://github.com/jrunic/koine/releases/tag/v0.1.0
