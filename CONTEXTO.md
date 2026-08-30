---
descricao: Contexto técnico do repositório koine — stack, padrões, estrutura e como contribuir
id: 202606201915
tipo: contexto
status: ativo
tags: [contexto, koine, python, cli]
projeto: koine
escopo: repo:koine
plataforma: "*"
---

# CONTEXTO.md — Koine
## Onde o trabalho acontece

**O trabalho de desenvolvimento acontece fora deste repositório**, nos documentos
internos do autor — é lá que a sessão abre (`jd-claude <agente> criar-koine`).

| Artefato | Lar canônico |
|---|---|
| Roadmap de ciclos, spec, plano | fora deste repositório |
| Arquivo de apoio de tarefa, diário de sessão | fora deste repositório |
| Discussão de negócio, modelo de domínio, glossário | fora deste repositório |
| **Código, testes, migrations** | **este repositório** |
| **Documentação do produto** (Diátaxis) | **este repositório**, `docs/81-referencia/` |
| **ADR de contrato da ferramenta** | **este repositório**, `docs/81-referencia/decisoes/` |
| **README, CHANGELOG** | **este repositório** |

**Razão:** spec, plano, roadmap e diário são documentos operacionais internos —
nomeiam contexto que não pertence a um repositório aberto. O repositório carrega
o que a audiência dele precisa.

**As skills leem esta seção** em vez de inferir por visibilidade. Repositório
que não declara deixa a skill sem informação, e sem informação ela erra.

## Propósito

Koine é uma CLI Python que injeta contexto multi-camada (usuário, agente, referências, contexto da pasta) em harnesses de IA terminal — Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode, Codex CLI.

Este documento orienta quem desenvolve o repositório. Para a visão de produto e instalação, ver [`README.md`](README.md). Para decisões arquiteturais, ver [`docs/decisoes/`](docs/decisoes/).

## Stack

- **Linguagem:** Python 3.12+ (stdlib-only em runtime; sem código nativo — nada de `.pyd`/`.so`/`.dll`)
- **CLI:** `argparse` (stdlib)
- **YAML:** PyYAML vendorizado em `src/koine/_vendor/` (puro-Python)
- **Testes:** pytest
- **Distribuição:** zipapp (`koine.pyz`) + payload `vault/` no zip de release
- **Release:** GitHub Actions (`release.yml`) — pytest, build do zip, publicação em GitHub Releases

## Estrutura do código

```
src/koine/              — pacote da aplicação
  cli.py                — entry point (subcomandos + despacho de wrappers)
  adapters/             — um módulo por cliente IA + REGISTRY (claude, antigravity, codex, copilot, opencode)
  contexto.py           — resolução do contexto (CONTEXTO.md local, sem cascata)
  render.py             — merge de seções para adapters de bundle/inline
  instalar.py           — extração do vault → XDG
  indice.py             — gerador de kn-indice-<dom>.md
  cache.py              — bundles descartáveis em ~/.cache/koine/
  pasta.py              — resolução de pasta em cascata (alias, direto, fuzzy)
  aliases.py            — CRUD de ~/.config/koine/aliases.json
  paths.py              — XDG dirs (config_dir, vault_dir, cache_dir)
  escrita.py            — política única de escrita na pasta (marcador, .bak, troca atômica)
  estoque.py            — o que o mecanismo anterior deixou na pasta, e o que pode sair
  conflito.py           — porta do conflito.go; delega a política para escrita.py
  launch.py             — lançamento do cliente IA (execvpe)
  wrappers.py           — geração dos wrappers kn-* com interpretador bakeado
  schema.py             — dataclasses do frontmatter (usuário, escopo)
  _vendor/              — PyYAML vendorizado (via sys.path)
vault/                  — conteúdo distribuído ao lado do koine.pyz no zip de release
  KOINE.md
  agentes/hermes.md
  conceitos/
  habilidades/kn-NN-*/
  dominios/
  templates/
scripts/
  build-pyz.py          — monta koine.pyz (+ --zip para o pacote de distribuição)
  release/              — install.sh / install.ps1 / install.bat
  skills-mode/          — zip do modo skills (ambientes que bloqueiam até o Python)
tests/                  — pytest (unit + e2e via subprocess do pyz e dos wrappers)
.github/workflows/      — release.yml
docs/
  decisoes/             — ADRs
  tutoriais/            — Diátaxis
  guias/                — Diátaxis
  referencias/          — Diátaxis
  explicacoes/          — Diátaxis
```

## Padrões técnicos

### Naming

- **Arquivos/pastas/slugs:** kebab-case
- **Funções/vars Python:** snake_case (PEP 8)
- **Classes:** PascalCase
- **Constantes:** UPPER_SNAKE
- **Comandos CLI:** PT-BR (ex: `instalar`, `mostrar`, `gerar`, `versao`)
- **Flags CLI:** PT-BR (ex: `--para`); `--force` mantido em inglês por convenção técnica

### Linguagem

- **Código:** inglês nos identificadores onde a convenção da comunidade pede; domínio em PT-BR quando o conceito é do método (ex.: `Lancamento`, `conflito`)
- **Comentários:** PT-BR
- **Commits:** conventional commits, em inglês
- **Slugs/pastas/comandos/flags:** PT-BR

### Testes

- **Framework:** pytest
- **Runner:** `.venv/bin/pytest -q`
- **Pasta:** `tests/` (fixtures compartilhadas em `tests/fixtures/`)
- **Isolamento:** HOME isolado por fixture (`seed.montar`) + limpeza de `XDG_*` via `conftest._isola_xdg` (autouse). Subprocessos recebem env explícito.

### Build/Run

```bash
python3 -m venv .venv && .venv/bin/pip install pytest   # setup
.venv/bin/python -m koine <args>                        # rodar do fonte
.venv/bin/python scripts/build-pyz.py --zip             # koine.pyz + zip de distribuição
.venv/bin/pytest -q                                     # suíte
```

### Release

Push de tag `v*` dispara `.github/workflows/release.yml`: pytest → build do `koine-<versao>.zip` (pyz + vault) → GitHub Release com installers (`install.sh`, `install.ps1`, `install.bat`) e `koine-skills.zip`.

## Restrições técnicas

- **Repositório público não nomeia a árvore interna do autor** — nem em documento de trabalho, nem em comentário, nem no texto que documenta essa própria regra. Sem caminho absoluto, sem nome de cliente, sem estrutura de pastas interna. Varredura antes de todo push: `git log -p origin/<branch>..HEAD`. ADR `20260822-repo-declara-onde-o-trabalho-acontece` (decisão 5).
- **Stdlib primeiro.** Nova biblioteca externa requer ADR; dependência de runtime só vendorizada puro-Python (padrão `_vendor/`).
- **Zero código nativo no pyz** — restrição-âncora da distribuição (AV corporativo bloqueia `.pyd`/`.so`/`.dll`). Guardada por teste (`test_pyz_sem_codigo_nativo`).
- **XDG direto com fallback** — usar `XDG_CONFIG_HOME`/`XDG_DATA_HOME`/`XDG_CACHE_HOME` com fallback `~/.config/koine/` etc. em todos os SOs (inclusive macOS e Windows). Detalhes: ADR `20260621-estrutura-config-koine.md`.
- **Artefato shipped se atualiza; artefato do usuário se preserva** — `instalar`, `atualizar` e `instalar-habilidades` têm a **mesma** política: vault e skills divergentes são atualizados, com o conteúdo anterior guardado em `~/.cache/koine/backups/<versão>/` e o caminho anunciado na saída. `dominios/` é do usuário: preservado e reportado, salvo `--force`. A regra anterior — preservar divergente e exigir `--force` — segurava correção de skill fora da máquina de quem já tinha instalado, que foi o defeito medido em produção em 27/08/2026. **O backup nunca mora ao lado do original** dentro do vault ou da pasta de skills: nos dois casos alguém enumera o diretório, e um backup ali é instalado como skill fantasma (medido, e guardado por teste). `<versão>` é a que está **entrando** — no `atualizar`, o pyz em execução ainda é o antigo, então a versão trafega por parâmetro, nunca lida de `_version` no meio da cadeia.
- **CONTEXTO.md local-only** — koine não sobe na árvore, sem merge, sem cascata. Ausência = modo bootstrap. ADR `20260620-contexto-md-local-sem-cascata.md`.
- **Frontmatter ruim é dado ruim, não motivo para o produto não subir** — quem escreve `CONTEXTO.md`/escopo/referência é usuário comum descrevendo o próprio trabalho em português, e `descricao: Vendas B2B: metas` é a forma natural de escrever. `frontmatter.ler` parseia estrito e, só em erro, recita as linhas `chave: valor` que sozinhas não parseiam (por linha — o que já era válido não é tocado) e avisa no stderr. O que não tem reparo vira `FrontmatterInvalido` com arquivo/linha/coluna e **cada consumidor decide a política** (degradar, pular o arquivo, abortar) — a lib devolve o erro nomeado, não escolhe pelo chamador. Leitura de frontmatter a partir de caminho usa `frontmatter.ler_arquivo`, nunca `open().read()` solto. A escrita de frontmatter tem **um ponto só** (`ficha.normalizar_arquivo`): backup `.bak` livre antes de gravar, nunca em symlink nem no vault instalado, `newline=""` ponta a ponta para não trocar CRLF por LF, e falha de escrita degrada para o reparo em memória em vez de derrubar a sessão. O launch normaliza os arquivos de configuração que carrega (`ler_arquivo(normalizar_disco=True)`); a pasta-referências do usuário só por `koine validar --corrigir`. Arquivo que o Koine gera (índice) monta o frontmatter por `frontmatter.compor`, nunca concatenando linha à mão — nome de domínio vem da lista do usuário e pode ter `:`.
- **O estado da pasta tem uma definição só, e o Koine não escreve no `CONTEXTO.md` do usuário para consertá-lo** — `bootstrap.estado_do_fm(fm)` é o critério (`BOOTSTRAP`/`VALIDO`/`INCOMPLETO`), lido pelo launch **e** pelo `koine validar`, com teste exigindo concordância: a ferramenta que avisa antes não pode discordar da que barra na hora. Pasta `INCOMPLETO` (arquivo legível, sem `escopo:`) é auto-guiada — o agente recebe `vault/bootstrap/pasta-incompleta.md` por `ContextoMontado.instrucao_path` mais o arquivo original, e repõe a ficha conversando. **Adapter que renderiza `contexto_path` renderiza `instrucao_path`**; esquecer o campo deixa o usuário sem saída e sem erro.
- **A pasta declara o próprio agente, e o launch resolve por precedência** — `agente:` no frontmatter do `CONTEXTO.md`, com a ordem: posicional (efêmero, **não persiste**) → campo da pasta → `agente-default:` do arquivo do usuário → `hermes`. Vale **só em pasta `VALIDO`**; `AUSENTE`/`VAZIO`/`BOOTSTRAP`/`INCOMPLETO` seguem forçando Hermes com o agente pedido ignorado. Agente inexistente bifurca pela **fonte** do nome: posicional dá erro sempre (há um humano com o dedo no teclado); declarado num arquivo dá Hermes mais `vault/bootstrap/agente-inexistente.md` no interativo, e **aborta sem TTY** — subir em silêncio faria a sessão remota rodar com o agente errado. Gramática do launch: 0 posicionais resolve pela pasta, 1 é agente, 2 é agente + pasta.
- **O Koine não FABRICA ficha; repor ficha fotografada é a exceção nomeada** — `frontmatter.definir_campo` recusa arquivo sem bloco de propósito, e continua recusando: supor escopo ou adivinhar domínio é inventar estado do usuário. `ficha.repor_bloco` é o único lugar que escreve bloco onde não havia, e o conteúdo é **cópia literal** do que aquele arquivo tinha na última sessão que abriu bem — fotografado por pasta em `~/.cache/koine/fichas/`. O launch fotografa em pasta `VALIDO` (depois da normalização, senão a foto sai torta) e repõe em `INCOMPLETO`, com `.bak` do que estava lá, aviso no stderr e **re-medição do estado**: curar o disco sem re-medir abriria a sessão como incompleta, mandando o usuário consertar o que já está consertado. Sem foto, o caminho de antes segue intacto.
- **Quem grava `agente:` é o comando, nunca prosa** — `koine definir-agente <nome> [pasta]`, e `--default` para o arquivo do usuário. A escrita passa por `ficha`, que já checa somente-leitura antes do backup, recusa symlink e vault, e preserva CRLF. Instrução em prosa mandando o agente editar YAML é o mecanismo que perdeu a Ficha Koine em cinco pastas de um usuário real.
- **Durante a sessão o Koine não está no caminho de escrita** — quem grava o `CONTEXTO.md` é o cliente, com as ferramentas dele, e o processo do Koine já foi substituído por `execvpe`. O **launch** não escreve para consertar a pasta; o que escreve é comando explícito (`definir-agente`) ou a normalização de frontmatter torto, que existe desde a v0.5.2 — as duas por `ficha`, com backup. Por isso a preservação da Ficha Koine é **instrução** (regra de editar por acréscimo nas skills que escrevem) mais **detecção** (`koine validar`, achado `SEM_FICHA`, e a Rodada 5 da `/kn-99`) — não existe guard no momento de salvar, e propor um exige escolher entre hook por cliente (só o Claude Code tem) ou snapshot da ficha no cache com restauração posterior.
- **Vault é readonly em runtime** — extraído do payload de distribuição pelo `koine instalar` para `~/.local/share/koine/`. Usuário é dono de `~/.config/koine/`.
- **Marcador congelado, e a marca de intenção na SEGUNDA linha** — `<!-- gerado por kn-agente -->` na 1ª linha de arquivos gerados é o contrato de detecção com instalações antigas, inclusive as do binário Go, e **não muda**: trocá-lo faria o Koine deixar de reconhecer os próprios arquivos anteriores e tratá-los como do usuário, enchendo as pastas de `.bak`. Distinção nova entra **acrescentando**: `<!-- gerado a pedido -->` na 2ª linha diz que o arquivo foi materializado pelo `gerar` (modo skills) e por isso a limpeza não o remove. Propriedade e intenção são perguntas diferentes — `escrita.e_nosso` responde a primeira, `estoque.removivel` a segunda.

- **O contexto é entregue por canal externo; a pasta do usuário não recebe arquivo gerado** — cada adapter monta um bundle em `~/.cache/koine/<cliente>-bundles/<slot>/` e o entrega pelo canal **medido** para aquele cliente (`--add-dir`, `-c model_instructions_file=`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, `OPENCODE_CONFIG`). O mecanismo anterior — arquivo na pasta com `@/caminho/absoluto` — **não entrega fora do terminal**: import externo só expande em pasta aprovada, e a aprovação é um booleano por pasta que só o diálogo interativo escreve. No terminal parecia funcionar porque o agente lia os caminhos com a ferramenta; sem ferramentas, ou em sessão remota, a sessão sobe **sem contexto e sem erro**. Por isso o conteúdo do claude e do agy vai **embutido**, não referenciado. Duas exceções nomeadas ao "nada na pasta": o `CONTEXTO.md` bootstrap que o auto-guiar materializa, e o que o `koine gerar` escreve a pedido.

- **Adapter tem duas operações, e a varredura do `REGISTRY` cobra as duas** — `renderizar(cm)` devolve o `Lancamento` do launch (canal, sem tocar na pasta) e `renderizar_para_pasta(cm)` devolve `(arquivo, conteúdo)` para o `gerar`. Sem a segunda, o modo skills fica sem o que escrever — e é justamente onde a pasta é a **única** via de entrega, porque não há wrapper para configurar ambiente. Argumento com valor dinâmico (o `model_instructions_file` do codex, que varia por pasta) vai em `Lancamento.extra_args`, nunca em `EXTRA_ARGS`, que é constante de módulo.

- **Remoção é a única operação sem `.bak`, e por isso tem duas travas** — o launch limpa o estoque do mecanismo anterior naquela pasta, e só alcança (a) os nomes que o mecanismo materializava, derivados do `REGISTRY`, **e** (b) o que carrega o nosso marcador. Symlink é reconhecido por **caminho E alvo**: casar só pelo alvo removeria qualquer atalho do usuário apontando para o `CONTEXTO.md`; só pelo caminho removeria um `AGENTS.md` dele apontando para outro lugar. O alvo nunca é tocado. A limpeza é oportunista, por pasta — não há varredura global, e pasta que ninguém abrir pelo Koine mantém o arquivo antigo.
- **Shell no Windows se detecta por execução, e a escadinha é recortada por cliente** — `shell.melhor(aceitos)` devolve o primeiro degrau de `pwsh → powershell → bash → cmd` que a máquina **executa**; presença não responde, porque a estação corporativa tem o `pwsh` no PATH e negado (erro 1260, que estoura na criação do processo e por isso custa quase nada). O `bash` é procurado também **fora do PATH**, na instalação padrão do Git — é onde ele fica sem administrador, e é onde os próprios clientes o acham; um detector por PATH diria "sem bash" numa máquina onde ele funciona. O opencode aceita os quatro degraus (nome curto ou caminho absoluto); o claude aceita PowerShell ou bash e **nunca** `cmd`, e recebe `CLAUDE_CODE_USE_POWERSHELL_TOOL=0` só quando nenhum PowerShell executa; copilot, codex e agy não expõem chave nenhuma — medido, não suposto. `shell.diagnostico` devolve o motivo por degrau porque "não instalado" e "bloqueado pela política" pedem orientações opostas ao usuário.
- **O PATH do usuário é território de terceiro, e o Koine só gere a entrada dele** — `pathenv` escreve em `HKCU\Environment\Path` por `winreg` e **nunca** por `setx`, que trunca em 1024 caracteres em silêncio e grava `REG_SZ`, destruindo as `%VAR%` que o PATH real carrega. **Comparar expande, escrever preserva o cru**: sem expandir, `%USERPROFILE%\.local\bin` não é reconhecido como a pasta já presente e o instalador duplica — medido na bancada. Dedupe **só da nossa entrada exata**; duplicata de terceiro fica byte a byte (decisão do Orlando, 28/08), com **uma exceção nomeada**: a cauda vazia sai quando escrevemos, porque ela vira `;;` no próximo append de quem quer que seja. Escrita negada devolve `FALHOU` e cai na orientação manual — derrubar a instalação por causa do PATH troca um problema pequeno por um grande, e o `garantir` captura `ImportError` junto com `OSError` para que a promessa de "nunca levanta" seja verdadeira. O broadcast é `SendMessageTimeoutW` best-effort, nunca o `SendMessage` bloqueante. Quem conserta a **sessão corrente** é o `install.bat` com o próprio `set` — processo filho não altera o ambiente do pai.
- **O relatório de pré-requisitos decide num lugar e fala em outro** — `prerequisitos.avaliar` devolve achados tipados a partir do `shell.diagnostico` e do `ACEITA_SHELL` que **cada adapter declara**; a prosa mora em `mensagens.py`. Adapter novo sem `ACEITA_SHELL` quebra o teste do `REGISTRY` — tabela paralela envelheceria em silêncio. A distinção `RECUSADO` × `AUSENTE` é o que escolhe a mensagem: "não está instalado" pede *instale*, "existe e a política nega" pede *peça à TI*. Achado de instalação incompleta só sai quando dá para **afirmar** (pasta do codex resolvida pelo `.exe` ou pelo shim); pasta desconhecida fica calada, porque acusar instalação boa manda o usuário refazer o que está certo. O aviso do launch é **uma linha no stderr e não bloqueia** — sessão sem shell ainda entrega contexto e leitura de arquivos —, e vale a mesma limitação do aviso de ficha reposta: em sessão remota pode não chegar. A sonda do `shell` é **memoizada por processo** porque agora há dois consumidores no mesmo launch (o adapter escolhe o shell, o aviso decide se fala): medido na bancada, 408 ms na primeira chamada e 1 ms na segunda.
- **O `name` da skill é contrato de máquina, e a falha dele é silenciosa** — o OpenCode só reconhece a skill se o `name` do frontmatter casar o nome do diretório (`^[a-z0-9]+(-[a-z0-9]+)*$`) e a `description` couber em 1..1024 caracteres. Violação não dá erro: a skill some da lista de disponíveis, o que é bem pior de diagnosticar do que uma exceção. Guardado por `tests/test_vault_habilidades.py` sobre o vault inteiro. Vale para toda skill nova.
- **Skill do vault chega ao harness por cópia, não por symlink** — symlink no Windows exige privilégio de administrador que o público-alvo não tem. A documentação já mentiu sobre isso duas vezes (catálogo e mapa de arquitetura, herança do Go); ao descrever a instalação, dizer cópia.
- **Não commitar binários** — `dist/` e artefatos locais já cobertos pelo `.gitignore`.
- **SSL do Python falha em qualquer SO → fallback curl do sistema** — o OpenSSL da stdlib pode não verificar o cert: no Windows por não buscar o CA intermediário via AIA, no macOS por faltar o bundle de CA. O curl do SO usa o trust store nativo (Schannel/Keychain/CA bundle) e funciona onde o urllib falha. `atualizar` usa esse fallback em `resolver_versao`/`baixar`/sums desde a v0.4.7 (antes era win32-only; a v0.4.6 travava no macOS). Máquina já travada se recupera reinstalando via `install.sh` (100% curl) — `KOINE_VERSAO=... koine atualizar` NÃO resolve (morre igual no download).
- **O ritual de release deste repo tem guia próprio, e o gate de bancada tem critério** — `docs/guias/publicar-release.md`. Ele existe porque o ritual de repo de frota não serve aqui: o Koine não tem `production` e vai por tag → Release → instaladores, então o script de bump genérico sai `2` e a conferência é contra a release publicada. **O gate em VM AppLocker é obrigatório quando o diff toca launch, wrappers, `atualizar`, escrita fora do território do Koine (registro, PATH), código Windows-only ou saída em caminho novo** — e dispensável só quando o `git diff --stat` prova que a mudança é inerte para Windows. Sem esse critério o gate foi pulado três vezes por não ter tamanho definido. **Mudança que afeta Windows valida em VM AppLocker antes de release** — self-update (`atualizar`), launch e wrappers. O CI é **POSIX-only e não pega bug Windows-only**: na v0.4.3 o handoff finalizava com o pyz alvo baixado, que pode não ter `--finalizar` → finalizar com cópia do pyz atual. Lab reutilizável: Win11 ARM Enterprise (CrystalFetch + Fusion) com AppLocker escopado a um usuário restrito; o roteiro de montagem fica nos documentos internos do autor, fora deste repositório. **O build de teste vai por tag de pré-release, instalado pelo instalador de verdade — não se copia o `koine.pyz` para a máquina de teste**, e o procedimento inteiro está em `docs/guias/testar-build-em-bancada.md`. O ponteiro está aqui porque a armadilha é silenciosa e reincidente: o `instalar` bakeia nos wrappers o pyz **que está executando**, então validar a partir de uma pasta descartável deixa os seis wrappers apontando para ela, e apagar a pasta quebra a instalação sem nenhum erro na hora.

- **Skill que gera configuração prescreve a forma, não só o resultado** — quatro
  defeitos da v0.10.0 tiveram a mesma origem: a skill descrevia o que produzir e
  deixava a **forma** aberta (nome do provider, chave de relay, caminho do wrapper).
  O agente escolheu bem, e diferente em cada máquina; duas escolhas quebravam em
  silêncio. Quando a decisão precisa ser igual em toda instalação, ela vira campo do
  `koine paseo-info` ou frase imperativa com o valor — nunca "escreva o que fizer
  sentido". E **duas bancadas não são luxo**: os quatro passaram limpos no Windows.
- **Ao mexer no canal do orquestrador, conferir antes os três defaults que mordem** —
  estão em `docs/referencias/paseo.md`, medidos: omitir a chave de relay **expõe** a
  máquina (a doc do produto diz o contrário); o CLI cai na porta padrão e acerta o
  serviço de outro usuário da máquina; e a pasta de configuração é **identidade e
  registro** — movê-la custa o pareamento de todos os aparelhos, sem mensagem de erro.
- **Pendências abertas do acesso remoto** — jd-tasks **#708** (o entry `-hermes` do
  opencode não converge no macOS; as bancadas têm versões diferentes do cliente, e
  igualá-las é o primeiro passo), **#709** (escopo ou agente inexistente ainda derruba
  o provider no canal, contra a decisão de que estado de pasta nunca derruba ali) e
  **#710** (login do copilot na bancada de macOS). Conferir se ainda valem antes de
  assumir que sim.

## Família `kn-2N` espelha o `jd-cria-design` do brain

As três skills de marca (`kn-21`/`kn-22`/`kn-23`) são a versão portável do skill interno `jd-cria-design` do Jedi Brain: mesma doutrina, dependências públicas (`npx @google/design.md`, `imagio`, `prelo`) e destinos em pasta-referências de escopo em vez de taxonomia do brain.

As duas famílias compartilham o mapeamento `DESIGN.md → tokens do prelo`. **Mudança no `MAPA-TOKENS.md` do `jd-cria-design` toca a `kn-23` também** — e vice-versa. Não há mecanismo de sincronia; é conferência manual quando o vocabulário de tokens do prelo mudar.

Estavam em sincronia em 2026-08-09, quando o prelo v1.1.0 moveu a estrutura CSS para a ferramenta e ambas passaram a emitir `tokens.css`.

**Versões mínimas das ferramentas externas:**

- `prelo` ≥ **1.2.0** para a `/kn-24-gera-pdf` — resolve caminho relativo contra a pasta do `.md`. Abaixo dela a skill não funciona sem contorno, e o contorno passou a ser nocivo: reescrever link relativo para absoluto faz o prelo gravar o caminho da máquina de origem dentro do PDF.
- `prelo` ≥ **1.2.1** para logo de marca na `/kn-23-gera-marca-prelo` — a cópia de `images/` na instalação entrou nessa versão. Antes dela a imagem ficava para trás e a regra CSS apontava para o vazio.

## Decisões locais divergentes (técnicas)

- **PyYAML vendorizado, não pip-instalado** — o pyz precisa ser autocontido numa máquina que só tem o interpretador; `src/koine/_vendor/` entra no `sys.path` do pacote.
- **Wrappers kn-\* bakeiam o interpretador absoluto** — `python3` puro no PATH pode ser um Python antigo (macOS: 3.9); o `instalar` grava `sys.executable` no wrapper.

## Como contribuir

1. Issue ou discussão antes de mudança não-trivial.
2. Branch a partir de `main`.
3. Commits em conventional commits, mensagens em inglês.
4. `.venv/bin/pytest -q` verde antes de abrir PR.
5. PR descreve motivação + mudança + plano de teste.
6. Para mudança arquitetural (interface pública, layout de pastas, decisões de módulo), abrir ADR em `docs/decisoes/`.
7. Publicar release segue `docs/guias/publicar-release.md` — o gate, a sequência e a verificação de efeito. Validar numa máquina que não é a de desenvolvimento segue `docs/guias/testar-build-em-bancada.md`.

## Referências

- [`README.md`](README.md) — visão de produto, instalação, exemplo de uso
- [`docs/decisoes/`](docs/decisoes/) — ADRs
- [`docs/referencias/`](docs/referencias/) — schema do `CONTEXTO.md`, comandos CLI
- [`CHANGELOG.md`](CHANGELOG.md) — releases
