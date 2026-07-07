---
name: kn-01-recebe-usuario
description: Onboarding completo do novo usuário Koine — meta-skill conduz primeira sessão com 4 personagens-âncora (Bruce Wayne, Hermione, Indy, Leia) com exemplos completos inline por personagem em cada pergunta, 4 rodadas estruturadas (arquivo do usuário, primeiro escopo, primeira pasta de trabalho, agente operacional), e ao final substitui CONTEXTO.md de bootstrap por configuração real. Roda uma única vez por usuário, automaticamente disparada quando Hermes detecta `bootstrap: true` no CONTEXTO.md da pasta canônica.
id: 202606221400
projeto: koine
tipo: habilidade
escopo: koine
plataforma: "*"
status: ativo
dominios: [metodologia]
tags: [skill, kn-01, onboarding, hermes, recebe-usuario]
---

# kn-01-recebe-usuario

Meta-skill que conduz o **primeiro contato do usuário com Koine**. Quatro rodadas curtas configuram o arquivo do usuário, o primeiro escopo, a primeira pasta de trabalho real e o primeiro agente operacional. Ao final, a pasta canônica (`~/koine` por default) vira escopo permanente de meta-trabalho com o método.

**Roda 1×/usuário.** Hermes inicia esta skill **automaticamente** quando detecta `bootstrap: true` no `CONTEXTO.md` da pasta da sessão atual — usuário não precisa invocar manualmente.

Manutenções pontuais pós-onboarding: `/kn-02-mantem-catalogo` ou `/kn-03-cria-agente`.

---

## Pré-condições

- Setup do Koine concluído — **modo binário** (`kn-agente instalar`) **ou modo skills** (`instalar-koine.bat` / guia `instalar-koine.md`): vault em `~/.local/share/koine/`, sementes de domínio em `~/.config/koine/dominios/`, pasta canônica `~/koine` com `CONTEXTO.md` `bootstrap: true`.
- Skills `kn-*` disponíveis no harness ativo — symlinkadas pelo `kn-agente instalar` (modo binário) ou copiadas para `~/.claude/skills/` (modo skills).
- Pasta `~/.config/koine/` existe mas não tem arquivo do usuário (`<nome>.md` na raiz).

Se `~/.config/koine/` já tem arquivo do usuário, **esta skill não roda** — onboarding já foi feito. Use `/kn-02-mantem-catalogo` para atualizações.

---

## Conceitos referenciados

Carregue sob demanda antes das rodadas correspondentes:

- `~/.local/share/koine/conceitos/escopos.md` (antes da Rodada 2)
- `~/.local/share/koine/conceitos/dominios.md` (antes da Rodada 3)
- `~/.local/share/koine/conceitos/agentes.md` (antes da Rodada 4)

---

## Roteiro

### Antes de começarmos — escolha do personagem-âncora

Apresente-se brevemente e ofereça os 4 personagens.

> "Bem-vindo ao Koine. Eu sou o **Hermes** — sou o agente que vai te receber e configurar tudo. Vamos passar por 4 rodadas curtas: seu perfil de usuário, seu primeiro escopo de trabalho, sua primeira pasta de trabalho, e a criação do seu agente operacional — aquele que vai te acompanhar no dia a dia.
>
> Antes de começarmos: vou usar um **personagem de ficção** como exemplo ao longo das próximas rodadas — concretiza os conceitos. Escolha o que você conhece melhor:
>
> 1. Bruce Wayne / Batman
> 2. Hermione Granger (Harry Potter)
> 3. Indiana Jones
> 4. Princesa Leia (Star Wars)
>
> Qual? (responda só o número)
>
> E como você gostaria que eu te chamasse?"

Aguarde número do personagem + nome do usuário. Use o nome desde a próxima fala. Toda menção a "personagem" nas rodadas seguintes usa o personagem escolhido.

**Cada pergunta abaixo mostra a resposta dos 4 personagens em blockquotes lado a lado.** Use o do personagem escolhido pelo usuário, ignore os outros — não adapte mentalmente exemplos de um para outro.

---

### Rodada 1 — Arquivo do usuário

Apresente o propósito antes das perguntas.

> "Vamos montar seu **arquivo de usuário**. Ele carrega em **toda sessão Koine**, em qualquer cliente IA, com qualquer agente. É a primeira coisa que o agente lê — define **quem você é e como falar com você**.
>
> Localização final: `~/.config/koine/<seu-primeiro-nome>.md`"

Faça as perguntas **uma de cada vez**, no formato:

#### **1. Nome completo**

*Formato esperado:* nome próprio, como aparece em documento.

*Como será usada:* referência formal do agente em comunicações escritas (e-mail rascunhado, documento gerado, assinatura).

*Se não souber:* pseudônimo serve; muda depois via `/kn-02`.

> **Bruce responderia:** Bruce Wayne
>
> **Hermione responderia:** Hermione Jean Granger
>
> **Indy responderia:** Dr. Henry Walton Jones Jr.
>
> **Leia responderia:** Leia Organa

#### **2. Como você gostaria que eu te chamasse?**

*Formato esperado:* um nome ou apelido.

*Como será usada:* vocativo do agente em toda interação ("Bruce, vi que...").

*Se não souber:* usa o primeiro nome do item 1.

> **Bruce responderia:** Bruce
>
> **Hermione responderia:** Hermione
>
> **Indy responderia:** Indy
>
> **Leia responderia:** Leia

#### **3. Idioma de comunicação**

*Formato esperado:* código IETF (`pt-BR` para português brasileiro, `en-US` para inglês americano, `es-ES` para espanhol da Espanha, etc.).

*Como será usada:* idioma das respostas do agente. Afeta tom, formalidade, termos técnicos traduzidos vs em inglês.

*Se não souber:* me diga seu país e idioma falado, eu converto. Default geral: `pt-BR`.

> **Bruce responderia:** en-US *(inglês americano)*
>
> **Hermione responderia:** en-GB *(inglês britânico)*
>
> **Indy responderia:** en-US *(inglês americano)*
>
> **Leia responderia:** pt-BR *(em pt-BR; o Galáctico Básico não tem código IETF)*

#### **4. Timezone (Fuso Horário)**

*Formato esperado:* zona IANA (`Continent/City`).

*Como será usada:* cálculo de horários, datas relativas ("amanhã", "semana que vem"), agendamento de tarefas, timestamps em diários.

*Se não souber:* me diga sua cidade e eu converto.

> **Bruce responderia:** America/New_York *(Gotham fica na costa leste dos EUA)*
>
> **Hermione responderia:** Europe/London *(Reino Unido)*
>
> **Indy responderia:** America/New_York *(Marshall College fica em Connecticut)*
>
> **Leia responderia:** America/Sao_Paulo *(não se aplica diretamente — escolheria o fuso da base atual da Aliança; em pt-BR padrão, `America/Sao_Paulo`)*

#### **5. Papel principal**

*Formato esperado:* 1-2 frases curtas.

*Como será usada:* o agente sabe seu contexto profissional ao responder — adapta exemplos, vocabulário, granularidade.

*Se não souber:* deixe em branco; complete via `/kn-02` depois.

> **Bruce responderia:** CEO da Wayne Enterprises. Filantropo, conselheiro da Liga da Justiça em meio-período.
>
> **Hermione responderia:** Bruxa nascida-trouxa, monitora-chefe de Hogwarts. Estudo intenso, foco em História da Magia e Defesa Contra as Artes das Trevas.
>
> **Indy responderia:** Professor de arqueologia no Marshall College. Em paralelo, trabalho de campo recuperando artefatos históricos antes que se percam ou caiam em mãos erradas.
>
> **Leia responderia:** Senadora de Alderaan no Senado Galáctico. Em paralelo, líder operacional da Aliança Rebelde.

#### **6. Estilo de comunicação preferido**

*Formato esperado:* um de [`direto` | `didático` | `exploratório` | `formal`] ou descreva em uma frase.

*Como será usada:* **como o agente vai se comunicar com você** — extensão das respostas, uso de listas vs prosa, presença de explicações de fundo, gentilezas. Não é como você fala com o mundo; é como você quer que o agente fale com você.

*Se não souber:* começo com `didático` e ajusto pela sua reação nas primeiras trocas.

> **Bruce responderia:** Direto, técnico, sem rodeios. Tom executivo.
>
> **Hermione responderia:** Didático e estruturado. Gosto de explicações com fundamentação e referências de fontes.
>
> **Indy responderia:** Direto e prático. Sem academicismo desnecessário quando estou em campo.
>
> **Leia responderia:** Direto e firme. Tempo é luxo que rebeldes não têm.

#### **7. Currículo curto**

*Formato esperado:* parágrafo de 2-3 frases.

*Como será usada:* o agente lê seu currículo ao iniciar sessões e adapta nível técnico, suposições sobre o que você já sabe, analogias usadas em explicações.

*Se não souber:* deixe em branco; vai surgindo conforme você conversa com o agente.

> **Bruce responderia:** Bilionário, herdeiro da Wayne Enterprises. Treinado em artes marciais, criminologia forense e engenharia. Mantém vida pessoal reservada.
>
> **Hermione responderia:** Filha de dois dentistas trouxas, primeira da família em Hogwarts. Leitora compulsiva. Defendo direitos dos elfos domésticos (S.A.L.E.). Boa em pesquisa, planejamento e operações sob pressão.
>
> **Indy responderia:** Doutorado em Arqueologia pela Universidade de Chicago. Filho de Henry Jones Sr., expert em folclore artúrico. Fluente em mais de 20 idiomas, leio runas e hieróglifos. Detesto cobras.
>
> **Leia responderia:** Princesa de Alderaan, filha adotiva de Bail e Breha Organa. Formada em Diplomacia na Universidade Real. Pilotagem básica, combate com blaster, criptografia militar. Senadora desde os 18 anos.

#### Materialização

Ao final das 7 perguntas, monte o arquivo `~/.config/koine/<primeiro-nome>.md` com a Ficha Koine:

```markdown
---
type: User
title: <Nome completo>
description: <descrição em 1 linha derivada do papel principal>
nome: <Nome completo>
idioma: <pt-BR | en-US | ...>
timezone: <America/Sao_Paulo | ...>
papel: <papel principal>
estilo: <estilo de comunicação preferido>
dominios: [universal]
tags: [usuario, <slug-do-primeiro-nome>]
---

# <Como te chamar>

<Currículo curto>
```

#### Confirmação

> "Pronto. Seu arquivo de usuário foi criado em:
>
> `~/.config/koine/<primeiro-nome>.md`
>
> Quer revisar o arquivo agora ou seguir para a próxima rodada?
>
> 1. Ver o arquivo
> 2. Seguir para a Rodada 2 (primeiro escopo)"

Se escolher "Ver o arquivo", mostre conteúdo + pergunte:

> "Algum campo a ajustar?
>
> 1. Sim, ajustar
> 2. Está bom, seguir"

#### Nota didática — antes de seguirmos

> "Você percebeu que **'Batman' não aparece no arquivo do Bruce**?
>
> Idem para os outros personagens:
>
> - **Hermione:** *'Ordem da Fênix'* não aparece — é segredo de escopo
> - **Indy:** *'expedições'* não aparecem com detalhe — vida acadêmica é a pública
> - **Leia:** *'Rebelião'* não aparece — é segredo de escopo
>
> O arquivo do usuário carrega em **toda** sessão Koine, em **qualquer** escopo. O que é segredo de um escopo específico **não vai aqui** — vai no arquivo daquele escopo.
>
> **Princípio:** o arquivo do usuário é o *'eu público'* universal entre escopos — o que qualquer agente em qualquer contexto pode saber. Já estamos praticando a separação de escopos antes mesmo de criar o primeiro."

---

### Rodada 2 — Primeiro escopo

Carregue `~/.local/share/koine/conceitos/escopos.md` antes de começar.

Apresente o conceito via analogia.

> "Imagine seu mundo de trabalho.
>
> Agora identifique os **'pedaços'** dele que pouco se comunicam entre si — pessoas diferentes, decisões diferentes, vocabulário diferente, às vezes valores diferentes. Cada um desses pedaços é um **escopo**.
>
> Veja como os 4 personagens vivem isso — cada um tem **três mundos** que quase não se sobrepõem:"

#### Bruce Wayne — três mundos:

| Escopo | Mundo | Pessoas-chave |
|---|---|---|
| `wayne-enterprises` | Mundo corporativo. CEO, conselho, M&A, relatórios trimestrais. | Lucius Fox, diretoria, investidores |
| `batman` | Vigilância de Gotham. Tecnologia, casos, aliados. | Comissário Gordon, Robin, Liga da Justiça |
| `wayne-manor` | Vida pessoal e legado familiar. Mansão, fundação Wayne. | Alfred, órfãos da fundação |

#### Hermione Granger — três mundos:

| Escopo | Mundo | Pessoas-chave |
|---|---|---|
| `estudos-hogwarts` | Aulas, monitoria, biblioteca. | McGonagall, Snape, Madame Pince |
| `ordem-da-fenix` | Resistência contra Voldemort. | Dumbledore, Sirius, Harry, Ron |
| `familia` | Pais trouxas; depois Ron, filhos. | Pais Granger, depois família própria |

#### Indiana Jones — três mundos:

| Escopo | Mundo | Pessoas-chave |
|---|---|---|
| `marshall-college` | Professor, alunos, papers, departamento. | Marcus Brody (diretor), alunos, colegas |
| `expedicoes` | Trabalho de campo, escavações, busca de artefatos. | Sallah, Marion, contatos locais |
| `familia` | Vida pessoal, legado familiar. | Henry Jones Sr. (pai), Mutt (filho) |

#### Princesa Leia — três mundos:

| Escopo | Mundo | Pessoas-chave |
|---|---|---|
| `senado-galactico` | Diplomacia, política, casa real de Alderaan. | Bail Organa, Mon Mothma |
| `rebeliao` | Aliança Rebelde, missões, liderança militar. | Mon Mothma, oficiais rebeldes |
| `familia` | Han, Luke (irmão), Ben (filho), legado Skywalker. | Han Solo, Luke, Ben |

> "Cada um desses mundos tem vocabulário, decisões e pessoas próprias. Isso é escopo no Koine: um delimitador de contexto.
>
> Você pode ter vários escopos ao longo do tempo. Vamos começar pelo **primeiro** — o que ocupa sua maior parte do tempo hoje."

> Bruce começaria por `wayne-enterprises` — é o que ocupa o "dia público".
>
> Hermione começaria por `estudos-hogwarts` — sua ocupação principal aos 15 anos.
>
> Indy começaria por `marshall-college` — sua identidade pública estável.
>
> Leia começaria por `senado-galactico` — seu mandato oficial.

> "Localização final: `~/.config/koine/escopos/<apelido>.md`"

#### **1. Apelido do escopo**

*Formato esperado:* palavra única ou frase com hifens, em minúsculas (ex: `geral`, `jedi-labs`, `wayne-enterprises`).

*Como será usada:* identificador interno do escopo — nome do arquivo (`~/.config/koine/escopos/<apelido>.md`), referência no cabeçalho de cada `CONTEXTO.md`, em logs de sessão.

*Se não souber:* `geral` é um default neutro válido. Pode renomear depois.

> **Bruce responderia:** wayne-enterprises
>
> **Hermione responderia:** estudos-hogwarts
>
> **Indy responderia:** marshall-college
>
> **Leia responderia:** senado-galactico

#### **2. Descrição em 1 linha**

*Formato esperado:* uma frase.

*Como será usada:* cabeçalho do arquivo do escopo; o agente lê ao carregar para entender o contexto rapidamente.

*Se não souber:* posso reusar seu papel principal da Rodada 1.

> **Bruce responderia:** Gestão executiva da Wayne Enterprises — conselho, M&A, relatórios financeiros.
>
> **Hermione responderia:** Estudos em Hogwarts — aulas, monitoria, biblioteca, preparação para os NOMs.
>
> **Indy responderia:** Vida acadêmica no Marshall College — aulas, papers, departamento de arqueologia.
>
> **Leia responderia:** Mandato no Senado Galáctico — diplomacia, política, representação de Alderaan.

#### **3. Pasta de referências**

*Formato esperado:* caminho prefixado por tipo —

- `home:<sub-caminho>` — relativo à sua pasta `$HOME` na máquina atual. Use quando a pasta vive no seu computador (caso comum).
- `abs:<caminho-absoluto>` — caminho fixo completo. Use quando a pasta é compartilhada em equipe (Drive sincronizado, NFS, disco compartilhado).

*Como será usada:* pasta no seu computador onde mora a **memória de longa duração** deste escopo — pessoas relevantes, decisões registradas, aprendizados, eventos. Toda sessão futura neste escopo carrega o índice dessa pasta no contexto do agente.

*Se não souber:* `home:koine/<apelido-escopo>` é o default sugerido (dentro da sua pasta Koine padrão `~/koine`).

> **Bruce responderia:** home:koine/wayne-enterprises *(resolveria para `~/koine/wayne-enterprises`)*
>
> **Hermione responderia:** home:koine/estudos-hogwarts *(resolveria para `~/koine/estudos-hogwarts`)*
>
> **Indy responderia:** home:koine/marshall-college *(resolveria para `~/koine/marshall-college`)*
>
> **Leia responderia:** home:koine/senado-galactico *(resolveria para `~/koine/senado-galactico`)*

#### **4. Dinâmica do escopo**

*Formato esperado:* parágrafo curto (2-3 frases) descrevendo pessoas envolvidas e foco operacional.

*Como será usada:* o agente lê ao iniciar sessão neste escopo — entende as relações principais, quem influencia decisões, qual o foco do trabalho.

*Se não souber:* pode pular agora; complete depois via `/kn-02-mantem-catalogo`.

> **Bruce responderia:** Empresa de capital aberto com 80 mil funcionários. Sou CEO, mas delego operação para Lucius Fox (CIO). Conselho com 9 membros independentes; controlo 47% das ações. Foco em R&D armamentista (em desinvestimento) e energia limpa.
>
> **Hermione responderia:** Escola de magia em regime de internato. Sou aluna do 5º ano e monitora (prefect) da Grifinória. McGonagall é minha chefe de casa e mentora principal; Madame Pince me conhece da biblioteca. Foco do ano são os NOMs ao final do ano letivo.
>
> **Indy responderia:** Universidade de pequeno porte na Nova Inglaterra. Sou professor de arqueologia no Marshall College; Marcus Brody é decano e meu mentor de longa data. Carga semestral de 2 disciplinas, orientação de teses, comitês ocasionais. Foco em artefatos do Mediterrâneo antigo e Oriente Próximo.
>
> **Leia responderia:** Senado Imperial — milhares de senadores, blocos políticos, comitês. Sou a senadora de Alderaan (aos 19 anos), alinhada com Mon Mothma e meu pai Bail Organa. Foco em comitês de comércio interestelar e direitos civis, num momento de tensão crescente com o Imperador.

#### Materialização

Cria:

- `~/.config/koine/escopos/<apelido>.md` com Ficha Koine declarando `pasta-referencias` (tagged path), `proprietario` (apelido do usuário) e corpo narrativo da dinâmica.
- Pasta de referências resolvendo o tagged path, com:
  - `index.md` — contrato OKF (directory listing inicial)
  - `log.md` — contrato OKF (entrada inicial: "Initialization — <data>")

#### Confirmação

> "Pronto. Seu primeiro escopo foi criado em:
>
> - Arquivo do escopo: `~/.config/koine/escopos/<apelido>.md`
> - Pasta de referências: `<pasta resolvida>` *(criada com `index.md` e `log.md` iniciais)*
>
> Quer revisar os arquivos agora ou seguir para a Rodada 3?
>
> 1. Ver os arquivos
> 2. Seguir para a Rodada 3 (primeira pasta de trabalho)"

#### Nota didática — antes de seguirmos

> "Você notou que o escopo `<apelido>` lista `dominios: [universal, ...]`?
>
> Domínios são 'lentes' que decidem **que tipo de referência o agente carrega** quando você abre sessão neste escopo. Cada domínio tem seu próprio índice — `universal` carrega coisas que importam em todo lugar (sócios próximos, parceiros estruturais, decisões fundamentais); `negocio` carrega contratos, parceiros comerciais, decisões de venda.
>
> Cada escopo escolhe seus domínios. Vamos ver domínios em ação na próxima rodada."

---

### Rodada 3 — Primeira pasta de trabalho

Carregue `~/.local/share/koine/conceitos/dominios.md` antes de começar.

#### O que é uma pasta de trabalho

> "Uma **pasta no seu computador onde algo real acontece** — onde você guarda arquivos *(planilhas, textos, mídias, códigos, slides, contratos, ...)*, executa o trabalho, vê o resultado.
>
> Pode ser de dois tipos:"

##### Processo

> "Atividade **recorrente**, com regras e fluxos comuns, que acontece indefinidamente no tempo."

| Exemplos de pasta de processo | |
|---|---|
| `~/processos/viagens` | cada viagem segue o mesmo fluxo; você sempre tem novas |
| `~/processos/financas-pessoais` | contas, faturas, investimentos — rito mensal recorrente |
| `~/processos/conselho-wayne` | reuniões trimestrais com rito repetido |
| `~/processos/instagram-semanal` | postagens recorrentes seguindo a mesma estrutura |

##### Projeto

> "Atividade com **início, meio e fim claros**."

| Exemplos de pasta de projeto | |
|---|---|
| `~/projetos/abrir-filial-recife` | termina quando a filial inaugura |
| `~/work/wayne-q4-2026` | termina quando o relatório é apresentado |
| `~/projetos/migrar-shopify` | termina quando o site novo entra no ar |
| `~/projetos/lancar-livro-2027` | termina no lançamento |

#### Quanto mais específica, melhor

> "O agente IA fica **mais preciso quanto mais estreito** for o foco da pasta.
>
> Uma pasta `~/work` genérica força o agente a adivinhar o que você está fazendo. Já `~/work/wayne-q4-2026` carrega o contexto direto: *finanças, Wayne Enterprises, quarto trimestre de 2026, deck para conselho*. O agente nasce na sessão sabendo onde está.
>
> **Pasta genérica = agente genérico. Pasta específica = agente preciso.**"

#### NÃO use `~/koine` como pasta de trabalho

> "`~/koine` é a sua **pasta padrão do Koine** — onde você conversa comigo (Hermes) para **manter o próprio Koine** (criar escopos, ajustar perfil, criar outros agentes).
>
> Usar Koine para fazer Koine é confundir ferramenta com trabalho. A pasta de trabalho é **onde o agente IA vai fazer trabalho real com você**."

#### Hora de pensar

> "Antes de me dar o caminho, **pense em um projeto ou processo concreto** que você quer levar para sessões com seus agentes IA. Algo de verdade, com nome próprio, onde a IA realmente ajuda hoje.
>
> Não precisa ser 'o projeto da sua vida' — escolha o que faz sentido **agora**. Se nada vem à cabeça, é sinal de que precisamos conversar mais antes de criar a pasta.
>
> **Se quiser conversar mais sobre isso, é só me perguntar.** Posso te ajudar a destravar: o que tem te consumido tempo? Que decisão você está adiando? Que processo você gostaria de fazer melhor? Que dor de cabeça recorrente um agente IA aliviaria?"

> *Bruce, depois de pensar, escolheu: **Relatório Q4 2026** — projeto que termina em janeiro, quando ele apresenta números consolidados ao conselho.*
>
> *Hermione, depois de pensar, escolheu: **NOMs do 5º ano** — preparação para os Ordinários de Magia ao final do 5º ano em Hogwarts.*
>
> *Indy, depois de pensar, escolheu: **Coleção egípcia** — catalogação e contextualização da coleção doada por Lord Carnarvon ao Marshall College.*
>
> *Leia, depois de pensar, escolheu: **Tratado Corellia** — drafts e negociação do tratado comercial com o Sistema Corellia.*

#### Agora as 3 perguntas

#### **1. Caminho da pasta de trabalho**

*Formato esperado:* caminho absoluto ou começando com `~` (sua pasta `$HOME`).

*Como será usada:* a partir daqui, qualquer sessão Koine aberta nessa pasta (`kn-<cliente> <agente> .`) carrega automaticamente seu perfil + o escopo + os domínios + o contexto desta pasta. O agente já chega sabendo onde está.

*Sugestões de padrão (escolha o que faz sentido):*

- `~/projetos/<nome>` — para projetos com início, meio e fim
- `~/processos/<nome>` — para processos recorrentes
- `~/work/<nome>` — alternativa em inglês
- `~/code/<nome>` — para repositórios de código
- Caminho existente que você já usa hoje (`~/Documents/...`, etc.)

*Se a pasta não existir:* pergunto se quero criar.

*Se você não sabe o caminho exato:* sem problema. **Me diga onde a pasta está e eu te ajudo:**

- Você já tem uma pasta que abre pelo **Finder** (Mac) ou **Explorer** (Windows)? Descreva onde ela está (ex: "uma pasta `Wayne` dentro de Documents") — eu monto o caminho para você.
- Quer dica de como copiar o caminho diretamente do Finder/Explorer? Te explico passo a passo.

> **Bruce responderia:** ~/work/wayne-q4-2026
>
> **Hermione responderia:** ~/estudos/noms-5o-ano
>
> **Indy responderia:** ~/work/colecao-egipcia
>
> **Leia responderia:** ~/projetos/tratado-corellia

[Hermes inspeciona a pasta antes de seguir:
- É um repositório git?
- Tem indicadores técnicos (`go.mod`, `package.json`, `pyproject.toml`, etc.)?
- Tem README ou docs?
- Já tem `CONTEXTO.md`? (Se sim, redireciona para `/kn-02-mantem-catalogo`.)
e usa o resultado para sugerir descrição e domínios.]

#### **2. Descrição em 1 linha**

*Formato esperado:* uma frase sobre o trabalho desta pasta.

*Como será usada:* corpo do `CONTEXTO.md`; o agente lê como sumário ao abrir sessão na pasta.

*Se não souber:* posso reusar o que você me contou no "Hora de pensar".

> **Bruce responderia:** Consolidação financeira do 4º trimestre de 2026 — números, drafts e deck para o conselho em janeiro.
>
> **Hermione responderia:** Preparação para os NOMs (Ordinários de Magia) ao final do 5º ano — resumos, simulados e planos de revisão.
>
> **Indy responderia:** Catalogação e contextualização da coleção de artefatos egípcios doada por Lord Carnarvon.
>
> **Leia responderia:** Drafts e negociação do tratado comercial com o Sistema Corellia.

#### **3. Domínios relevantes**

*Formato esperado:* lista de domínios padrão, separados por vírgula.

| Domínio | Carrega referências sobre |
|---|---|
| `universal` | sócios próximos, parceiros estruturais, decisões fundamentais |
| `negocio` | contratos, parceiros comerciais, decisões de venda, clientes |
| `tecnologia` | padrões técnicos, stacks, ADRs, decisões de arquitetura |
| `pessoal` | vida pessoal, wellbeing, família |

*Como será usada:* o agente carrega os **índices** de referência desses domínios quando você abre sessão na pasta. Mais domínios = mais contexto carregado.

*Se não souber:* `universal` é o mínimo seguro. Adicione outros conforme aparecer necessidade.

*Sugestão automática:* derivada da inspeção da pasta no item 1 + dos domínios do escopo da Rodada 2.

> **Bruce responderia:** universal, negocio
>
> **Hermione responderia:** universal, tecnologia *(magia é a "tecnologia" desse mundo)*
>
> **Indy responderia:** universal, tecnologia *(arqueologia como ofício técnico)*
>
> **Leia responderia:** universal, negocio *(diplomacia comercial)*

#### Materialização

Cria `<pasta>/CONTEXTO.md` com Ficha Koine:

```yaml
---
escopo: <apelido-escopo-da-rodada-2>
dominios: [<lista>]
descricao: <frase do item 2>
tags: [contexto, <slug-da-pasta>]
---

# <Título derivado>

<Descrição do item 2 expandida em parágrafo>

Esta pasta acumula padrões, decisões e referências de alcance local.
Atualize conforme o trabalho avançar.
```

#### Confirmação

> "Pronto. Seu primeiro `CONTEXTO.md` foi criado em:
>
> `<pasta>/CONTEXTO.md`
>
> Quer revisar o arquivo agora ou seguir para a Rodada 4?
>
> 1. Ver o arquivo
> 2. Seguir para a Rodada 4 (primeiro agente operacional)"

#### Nota didática — antes de seguirmos

> "A partir de agora, qualquer hora que você abrir uma sessão nesta pasta com:
>
>     cd <pasta>
>     kn-<cliente> <agente>
>
> …o agente já chega sabendo:
>
> - **Quem você é** (arquivo do usuário da Rodada 1)
> - **Em qual escopo está** (da Rodada 2)
> - **O que vai carregar** (índices dos domínios escolhidos)
> - **O foco da pasta** (`CONTEXTO.md` desta rodada)
>
> **Zero repetição.** Você não precisa explicar nada — só abrir e trabalhar. É exatamente para isso que o Koine existe."

---

### Rodada 4 — Primeiro agente operacional

Carregue `~/.local/share/koine/conceitos/agentes.md` antes de começar.

Apresente o conceito.

> "Última rodada. Até agora você conversou comigo, **Hermes**. Eu sou focado em operar o método Koine — te receber, configurar a estrutura, **criar outros agentes**. Não sou o agente do seu dia a dia.
>
> O trabalho cotidiano pede um agente próprio, com **voz e foco específicos** para o que você faz. Exemplos de agentes por tipo de trabalho:"

| Trabalho | Agente típico |
|---|---|
| Operações administrativas | `assistente`, `secretaria` |
| Análise financeira | `analista`, `cfo`, `lucius` |
| Escrita longa | `redator`, `cronista`, `pena` |
| Programação | `dev`, `engenheiro`, `gepeto` |
| Coaching / reflexão | `mentor`, `socrates`, `coach` |

> "Vamos criar o **primeiro** — o agente para o trabalho desta primeira pasta que acabamos de configurar.
>
> A partir daqui, **transfiro o conduzir** para uma skill especializada, a `/kn-03-cria-agente`. Ela vai te entrevistar em 8 rodadas curtas para definir:
>
> - **Identidade:** nome humano, slug do arquivo, descrição
> - **Âncora ficcional (opcional):** personagem que dá voz e postura ao agente
> - **Foco operacional:** tipos de sessão típicos, skills favorecidas
> - **Tom e registro, calibragens, mecânica de sessão**
>
> Quando `/kn-03-cria-agente` terminar, eu valido com você que o arquivo ficou correto e fechamos o onboarding."

> *Para o Bruce, `/kn-03-cria-agente` vai construir um `lucius` ancorado em Lucius Fox — foco em análise financeira corporativa, governança, comunicação com conselho.*
>
> *Para a Hermione, `/kn-03-cria-agente` vai construir uma `athena` — homenagem a Atena (mitologia grega), sabedoria estratégica para estudos e pesquisa estruturada.*
>
> *Para o Indy, `/kn-03-cria-agente` vai construir um `marcus` — homenagem a Marcus Brody, curador erudito para catalogação e contexto histórico.*
>
> *Para a Leia, `/kn-03-cria-agente` vai construir uma `mon` — homenagem a Mon Mothma, estratégia política, gravidade serena para diplomacia.*

Invoque `/kn-03-cria-agente`. Quando retornar, valide com o usuário que o arquivo foi criado corretamente em `~/.config/koine/agentes/<nome>.md`.

---

### Confirmação final + reescrita do CONTEXTO.md de bootstrap

Ao retornar de `/kn-03-cria-agente`, apresente o resumo:

> "Pronto. Koine configurado de ponta a ponta. **Resumo do que existe agora:**"

| Camada | Onde | O que tem |
|---|---|---|
| Arquivo do usuário | `~/.config/koine/<primeiro-nome>.md` | quem é você |
| Primeiro escopo | `~/.config/koine/escopos/<apelido>.md` | dinâmica do mundo de trabalho |
| Pasta de referências | `<pasta resolvida do tagged path>` | memória do escopo (vazia, vai crescer) |
| Primeira pasta de trabalho | `<pasta>` com `CONTEXTO.md` | o projeto/processo em si |
| Primeiro agente operacional | `~/.config/koine/agentes/<nome>.md` | quem te ajuda no dia a dia |

**Agora há dois arquivos a criar/modificar:**

**(a) Criar `~/.config/koine/escopos/koine.md`** — escopo permanente do meta-trabalho. Sem este arquivo, a próxima sessão `kn-<cliente> hermes koine` vai falhar com "escopo declarado em CONTEXTO.md mas não encontrado".

```yaml
---
type: Scope
title: Koine — Meta-trabalho
description: Pasta canônica de meta-trabalho com o método Koine
escopo: koine
pasta-referencias: home:koine
proprietario: <apelido-do-usuario>
dominios: [universal]
tags: [escopo, koine, meta]
---

# Escopo: Koine (meta-trabalho)

Escopo permanente da pasta canônica `~/koine` (ou caminho escolhido pelo usuário em `kn-agente instalar`), criado ao final do onboarding `/kn-01-recebe-usuario`. Carrega referências de domínio `universal` quando você abre sessão com Hermes para manter o próprio Koine.

Stakeholders: o próprio usuário e Hermes. Foco operacional: configuração e manutenção do método, criação de outros agentes e escopos, catalogação de aprendizados sobre o método.
```

**(b) Reescrever `<pasta-canonica>/CONTEXTO.md`** substituindo `bootstrap: true` pelo escopo `koine` real:

```yaml
---
escopo: koine
dominios: [universal]
descricao: Pasta canônica de meta-trabalho com o método Koine
tags: [contexto, koine]
---

# Koine — Meta-trabalho

Esta é a pasta canônica para suas sessões com **Hermes** (o agente que opera o método Koine). Volte aqui sempre que precisar:

- Criar outro escopo (`/kn-02-mantem-catalogo`, fluxo escopo)
- Criar outro agente operacional (`/kn-03-cria-agente`)
- Atualizar seu perfil (`/kn-02`, fluxo arquivo do usuário)
- Criar um domínio novo (`/kn-02`, fluxo domínio)
- Catalogar conhecimento sobre o próprio método (`/kn-11-mantem-referencia`)

Para trabalho real (programação, análise, escrita, etc.), use a pasta de trabalho do projeto/processo correspondente com o agente operacional adequado.
```

Materialize **ambos** os arquivos. Ordem importa: crie o escopo primeiro (item a), depois reescreva o CONTEXTO.md (item b). Mostre o resultado:

> "Sua pasta `~/koine/` agora é escopo permanente de meta-trabalho Koine — não mais bootstrap.
>
> **Para começar a trabalhar de verdade:**
>
>     cd <pasta da Rodada 3>
>     kn-<cliente> <nome-do-agente>
>
> No **modo binário**, substitua `<cliente>` pelo wrapper que você usou (`kn-claude`, `kn-agy`, `kn-copilot` ou `kn-opencode`). No **modo skills** (sem binário), abra o `claude` direto na pasta de trabalho — o `CLAUDE.md` já carrega o agente.
>
> O agente vai abrir a sessão **já sabendo tudo** que configuramos juntos. Você não precisa explicar nada — só dizer o que precisa fazer.
>
> **Quando vier o que mais? Use estas skills:**"

| Quando | Skill |
|---|---|
| Criar novo escopo, novo domínio, atualizar perfil | `/kn-02-mantem-catalogo` |
| Criar outro agente operacional (outro tipo de trabalho) | `/kn-03-cria-agente` |
| Catalogar conhecimento que apareceu durante o trabalho | `/kn-11-mantem-referencia` |
| Fechar uma sessão registrando o que aprendeu | `/kn-99-encerra-sessao` |

> "Lembra que sua **pasta canônica para conversar comigo (Hermes)** é `~/koine` — acessível pelo alias `koine`:
>
>     kn-<cliente> hermes koine
>
> Volte aqui sempre que precisar **manter** o Koine. Para fazer trabalho real, vá na pasta do trabalho.
>
> **Bem-vindo ao Koine.**"

---

## O que NÃO faz

- **Não cria múltiplos escopos** — só o primeiro. Outros entram via `/kn-02-mantem-catalogo` (fluxo escopo) conforme aparece a necessidade.
- **Não cria múltiplos agentes** — só o primeiro operacional. Outros via `/kn-03-cria-agente`.
- **Não cataloga referências** — pasta-referências nasce vazia (só `index.md` + `log.md`). Catalogação começa via `/kn-11-mantem-referencia` durante o trabalho real.
- **Não roda duas vezes** — se detectar arquivo do usuário existente em `~/.config/koine/`, recusa e direciona para `/kn-02-mantem-catalogo`.
- **Não duplica a entrevista de `/kn-03-cria-agente`** — Rodada 4 só apresenta o conceito e delega.

---

## Checkpoints intermediários

Entre cada rodada, **pause e confirme** com o usuário antes de avançar. Onboarding é momento de calibragem — o agente lê se o usuário está confortável com o ritmo ou se precisa pausar.

Em qualquer rodada, se o usuário travar ou pedir tempo, ofereça encerrar e retomar depois com `/kn-02-mantem-catalogo` (fluxos individuais) — onboarding completo não é obrigatório em uma sessão única, mas é o caminho mais coerente.
