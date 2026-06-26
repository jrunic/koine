---
id: 202606211200
tipo: decisao
status: aceito
description: ADR — Estrutura canônica de pastas de configuração do Koine — XDG puro, vault embed-only seletivo, tagged path, Ficha Koine universal, agente Hermes, arquivo do usuário × ficha cadastral
tags: [adr, koine, xdg, vault, config, hermes]
---

# ADR — Estrutura de configuração do Koine

## Status

Aceito.

## Contexto

A separação em 4 camadas do Koine (harness, habilidades, base de conhecimento, sistema de arquivos) foi acompanhada de uma primeira proposta de estrutura de pastas:

- Vault em `~/.koine/` (dotfile no HOME).
- Config do usuário em `~/.config/koine/` (XDG).
- `agentes/koine/AGENTE.md` (subpasta + nome de arquivo padronizado).
- `biblioteca-dominios-seed/<dom>.yaml` no vault e `biblioteca-dominios/<dom>.yaml` na config.
- `usuario.yaml` + `usuario.md` como par estrutura/narrativa.
- Campo `base:` (path absoluto) para apontar a pasta com o bundle OKF do escopo.
- `INDEX-<dom>.md` em `dominios-seed/` e em `dominios/`.

A revisão submeteu cada uma dessas escolhas a confronto socrático. Tensões identificadas:

1. **Mistura XDG / dotfile.** Metade da estrutura em `~/.koine/` (legado), metade em `~/.config/koine/` (XDG). Inconsistência interna sem ganho.
2. **Cópias da semente em disco e no binário** com risco de divergência ao atualizar.
3. **Path absoluto no `base:`** quebra portabilidade Mac↔Mac (backup) e Mac↔Windows.
4. **Sobrecarga semântica do termo "base"** — campo, função, sentido técnico Unix.
5. **Par `.yaml` + `.md` sincronizados** introduz divergência potencial e contraria o princípio Ficha Koine de "um arquivo por conceito".
6. **Colisão entre `KOINE.md` (método) e `agentes/koine/AGENTE.md` (agente)** — dois "koine" com propósitos diferentes confundem governança, day-to-day e branding.
7. **`templates/` extraído para disco** sem necessidade (lido via `embed.FS`).
8. **`.meta.json` sob Ficha Koine** — arquivo é máquina-pra-máquina, cerimônia sem propósito.
9. **Prefixo `biblioteca-`** em `biblioteca-dominios/` redundante (a pasta já é a biblioteca por ser pasta com itens).
10. **`INDEX-<dom>.md` no vault** redundante após colapso de `<dom>.yaml` + `INDEX-<dom>.md` em único `<dom>.md`; e índice de entradas é por-escopo, não cabe em vault estático.
11. **`usuario.md` global** mistura dois objetos distintos (perfil operacional do usuário vs ficha cadastral PF), com risco de vazamento de dados sensíveis em escopos que não precisam.

## Decisão

### 1 — Padrão XDG puro em **todos** os SOs (incluindo macOS e Windows)

| Tipo | Path em todos os SOs (Linux, macOS, Windows) |
|---|---|
| Vault (readonly em runtime) | `~/.local/share/koine/` (ou `$XDG_DATA_HOME/koine/`) |
| Config do usuário (writeable) | `~/.config/koine/` (ou `$XDG_CONFIG_HOME/koine/`) |
| Cache (futuro) | `~/.cache/koine/` (ou `$XDG_CACHE_HOME/koine/`) |

No Windows, `~/` expande para `%USERPROFILE%` (ex: `C:\Users\<nome>\.config\koine\`). Path estruturalmente idêntico em todos os SOs (módulo prefixo do home).

**Implementação Go:** as funções em `internal/paths/xdg.go` **NÃO devem usar** `os.UserConfigDir()`, `os.UserCacheDir()` nem chaves `runtime.GOOS`. Cada função checa a env var XDG correspondente e usa `~/.config/koine/`, `~/.local/share/koine/`, `~/.cache/koine/` como fallback via `os.UserHomeDir()`. Sem código condicional por SO.

```go
func ConfigDir() string {
    if v := os.Getenv("XDG_CONFIG_HOME"); v != "" {
        return filepath.Join(v, "koine")
    }
    home, _ := os.UserHomeDir()
    return filepath.Join(home, ".config", "koine")
}
// VaultDir e CacheDir seguem o mesmo padrão com XDG_DATA_HOME/XDG_CACHE_HOME.
```

**Razões para forçar XDG em todos os SOs** (rejeitando `~/Library/Application Support/` no macOS e `%APPDATA%` no Windows):

1. **Sincronia P2P cross-platform com setup trivial.** Cenário comum: usuário sincroniza N máquinas (Mac pessoal + Windows trabalho + Linux servidor) com Syncthing ou equivalente. Path estruturalmente idêntico em todos os SOs = usuário aponta "uma pasta" (`~/.config/koine/`) em todos os clientes e a ferramenta sincroniza sem mapping cross-platform manual. Com paths divergentes por SO, usuário precisaria mapear pastas explícitas em cada máquina — fricção real que mata adoção.
2. **Coerência interna do Koine.** Mesma decisão para vault, config e cache em todos os SOs. Sem `runtime.GOOS` espalhado pelo código.
3. **Coerência conceitual do produto.** Koine "se comporta igual" em todos os SOs. Usuário não precisa aprender "no Mac vai aqui, no Windows vai ali". Documentação cita 1 path.
4. **Visibilidade.** `~/.config/koine/` é descobrível em todos os SOs. `~/Library/Application Support/koine/` esconde no macOS; `%APPDATA%\koine\` esconde no Windows.
5. **Arquivos como primeira classe.** Conteúdo do usuário não vive escondido em namespace de aplicativo do SO.
6. **Convenção dev moderna.** CLIs modernas (`gh`, `kubectl`, `helm`, `fly`, `terraform`, etc.) usam XDG-style em todos os SOs, não convenções nativas. Tooling Unix-style no Windows (Git Bash, WSL, PowerShell moderna) já normalizou `~/.config/` no profile Windows; pastas com `.` no início são comuns (`.git`, `.ssh`, `.vscode`, `.gitconfig`).

**Trade-offs aceitos conscientemente:**

- **macOS:** abre mão da convenção Apple-native (`~/Library/Application Support/`). Time Machine continua cobrindo `~/` inteiro — backup intacto.
- **Windows:** abre mão de `%APPDATA%` (Roaming AD) e `%LOCALAPPDATA%`. Roaming AD é irrelevante quando uma ferramenta P2P é o mecanismo canônico de sincronia. File History cobre `~/` inteiro — backup intacto. AppLocker bloqueia executáveis, não criação de pastas; `.config\` no profile é trivialmente aceito em ambientes corp (precedente: `.git\`, `.ssh\`, `.vscode\`).
- **Validação empírica em ambiente Windows corp real** informa eventual revisão se houver fricção inesperada.

### 2 — Sementes só no embed

`vault/dominios/` no source do repo entra no binário via `//go:embed vault/*`. **Não é extraído para disco no `kn-agente instalar`.** O comando planta direto em `~/.config/koine/dominios/` a partir do `embed.FS`. Canal canônico para ver a versão original: `kn-agente mostrar-padrao <dominio>` (lê do embed).

Razão: única fonte de verdade da semente = binário corrente. Sem cópia estática em disco que diverge entre updates.

### 3 — Tagged path obrigatório

Campos que apontam para pasta no filesystem (ex: `pasta-referencias:` do escopo) usam **prefixo obrigatório**:

- `home:<rel>` — resolve relativo a `$HOME` / `%USERPROFILE%`. Caso comum (uso pessoal).
- `abs:<path>` — path absoluto literal. Cenário empresarial (NFS, Drive sincronizado, disco externo compartilhado com equipe).

Sem prefixo = erro de validação. Sem DWIM silencioso.

Razões: portabilidade Mac↔Mac (backup, migração de máquina), cross-platform Mac↔Windows, suporte explícito a referência compartilhada em equipe.

### 4 — Plural "referências" + campo `pasta-referencias:`

Substitui o termo "base de conhecimento" e o campo `base:` por "**referências**" e `pasta-referencias:`.

- **Sentido principal (agregado):** a pasta que mora o bundle OKF-conforme do escopo. Catálogo navegável de items discretos com identidade própria.
- **Sentido secundário (unidade):** cada concept catalogado dentro do agregado (Polissemia controlada; sentido resolvido por contexto, como "biblioteca").

Prefixo `pasta-` no nome do campo resolve a ambiguidade nome-plural/valor-singular (campo é escalar — aponta para 1 path).

### 5 — Ficha Koine universal

**Todo arquivo do Koine que carregue dados estruturados E/OU narrativos é `.md` com frontmatter YAML.** Não existe `.yaml` puro no Koine.

Aplica-se a: `usuario.md`/`<nome>.md`, `escopos/<slug>.md`, `dominios/<dom>.md`, `agentes/<nome>.md`, `habilidades/kn-NN-*/SKILL.md`, `KOINE.md`, `<pasta-de-trabalho>/CONTEXTO.md`, cada referência catalogada na pasta-referências.

Exceção justificada: `.meta.json` (ver decisão 8).

Razão: uma fonte de verdade por conceito; programático lê o frontmatter, agente IA carrega o arquivo inteiro via `@/`, usuário edita à mão sem medo de dessincronizar dois arquivos.

### 6 — Agente canônico = Hermes

O agente canônico que opera o método Koine se chama **Hermes**, em arquivo `~/.local/share/koine/agentes/hermes.md`.

Etimologia: mensageiro e intérprete dos deuses no panteão grego — função mitológica direta de carregar significado entre mundos distintos. "Hermenêutica" deriva dele. Casa com o posicionamento Koine (lingua franca entre usuário, arquivos, habilidades e modelos de IA).

Separa decisivamente:
- **Koine** = método/produto/marca.
- **Hermes** = agente canônico que opera o método.

Estrutura plana `agentes/<nome>.md`, sem subpasta por agente.

**Hermes é especialista em Koine, não generalista.** Tem responsabilidades operacionais fixas: conduzir onboarding, configurar/atualizar arquivo do usuário/escopos/contextos/domínios, criar agentes operacionais do usuário, catalogar referências sobre o método, encerrar sessões Koine, manter o método. Os trabalhos reais cotidianos do usuário (código, escrita, análise) acontecem em sessões com **agentes operacionais derivados** que o usuário cria via Hermes.

**Localização de agentes:**

| Tipo | Onde vive | Quem cria |
|---|---|---|
| Agente canônico Koine (Hermes) | `~/.local/share/koine/agentes/hermes.md` (vault em disco — extraído do embed) | `kn-agente instalar` |
| Agente operacional do usuário (especializados) | `~/.config/koine/agentes/<nome>.md` (config do usuário, writeable) | skill `kn-03-cria-agente` |

Mesma separação semântica de domínios: vault tem só o canônico imutável; config do usuário tem tudo writeable. Em runtime, `kn-agente` resolve o arquivo do agente buscando primeiro em `~/.config/koine/agentes/<nome>.md`, fallback em `~/.local/share/koine/agentes/<nome>.md`.

### 7 — `templates/` só embed

`vault/templates/*.tmpl` no source entra no binário. `text/template` lê do `embed.FS` direto. **Não é extraído para disco.** Vault em disco fica com propósito puro: arquivos que o agente IA lê via `@/`.

### 8 — `.meta.json` mantém JSON

`~/.local/share/koine/.meta.json` registra versão do binário + timestamp de instalação + hash do vault. **Exceção justificada à Ficha Koine**: arquivo é máquina-pra-máquina, zero conteúdo humano. Forçar markdown aqui é cerimônia sem propósito.

### 9 — `dominios/` (sem prefixo `biblioteca-`)

Renomear `biblioteca-dominios/` → `dominios/` nos dois lados (source e destino). Source ↔ destino com mesmo nome simplifica modelo mental:

- `vault/dominios/<dom>.md` (source, embed-only)
- `~/.config/koine/dominios/<dom>.md` (plantado pelo `instalar`)

### 10 — Sem `INDEX-<dom>.md` em `dominios/`

A decisão 5 (Ficha Koine) colapsou `<dom>.yaml` + `INDEX-<dom>.md` em único `<dom>.md` (frontmatter estruturado + corpo narrativo do framework). `INDEX-<dom>.md` em `dominios/` ficou redundante.

Além disso: índice de **entradas** é por natureza derivado e por-escopo — depende de qual `pasta-referencias` o usuário escolheu e do que catalogou. Não cabe em vault estático. O papel "índice de entradas" é coberto por **`kn-indice-<dom>.md`** gerado em runtime pelo `kn-agente`, vivendo dentro da pasta-referências do escopo.

Dois arquivos por domínio com papéis distintos:

| Arquivo | Onde vive | Conteúdo | Quem gera |
|---|---|---|---|
| `<dom>.md` | `~/.config/koine/dominios/` | Framework L3 (definição, esquema, regras) | Canônico (`origem: koine-canonico`) ou criado pelo usuário via `kn-01` (`origem: usuario`) |
| `kn-indice-<dom>.md` | `<pasta-referencias>/` | Listagem de entradas com `dominios: [<dom>]` no frontmatter | `kn-agente` (lazy a cada invocação) |

### 11 — Arquivo do usuário × ficha cadastral

Dois objetos distintos:

**Arquivo do usuário** em `~/.config/koine/<nome>.md` (ex: `<nome>.md` onde `<nome>` é o lowercase do primeiro nome do usuário). Atributos invariantes: nome, idioma, timezone, estilo de comunicação, background curto. Carrega em **toda** sessão (universal).

**Ficha cadastral** (RG, CPF, dependentes, telefones, e-mails, documentos) é **referência catalogada** em escopo dedicado (tipicamente `<nome>-pessoal`), com frontmatter OKF `dominios: [entidades]` ou `[pessoas]`. Carrega **sob demanda** (apenas em escopos que precisem).

Razões para não unificar: evitar vazamento universal de dados sensíveis; evitar inflação de contexto; separar propósitos (perfil ≠ ficha).

Cross-escopo (futuro): `escopo-pai: <nome>-pessoal` resolveria a cadeia e CLAUDE.md incluiria referências do pai. Implementação atual: fornecimento on-demand.

### 12 — Modelo canônico de 3 lugares

Toda informação Koine vive em um de 3 lugares com regras explícitas de leitura/escrita:

| # | Nome | Onde fica fisicamente | Quem escreve | Quem lê |
|---|---|---|---|---|
| **1** | **Embed do binário** | dentro do executável `kn-agente` (via `//go:embed vault`) | build (CI) | `kn-agente instalar` |
| **2** | **Vault em disco** | `~/.local/share/koine/` (XDG_DATA_HOME) | só `kn-agente instalar` | agentes em runtime (via `@/`) |
| **3** | **Config do usuário** | `~/.config/koine/` (XDG_CONFIG_HOME) | usuário + skills `kn-NN` | agentes em runtime (via `@/`) |

**Princípios:**

- (1) é fonte canônica do método (KOINE.md, Hermes, skills, sementes de domínio, templates).
- (2) é materialização em disco do que precisa ser lido via `@/` em runtime. Readonly em runtime — só `instalar` escreve.
- (3) é o que pertence ao usuário: arquivo do usuário, escopos, contextos de pasta, domínios (canônicos plantados + criados pelo usuário), agentes operacionais derivados. Writeable pelo usuário e pelas skills `kn-NN`.

Coerência entre estruturas:

- **Domínios:** canônico em (1) → plantado direto em (3); user-created direto em (3). (2) nunca tem `dominios/`.
- **Agentes:** canônico (Hermes) em (1) → extraído para (2); user-created direto em (3). Vault em (2) mantém readonly estrito.
- **Arquivo do usuário, escopos, contextos:** só em (3); não há canônico (são por definição do usuário).

### 13 — Família `kn-NN` com bloco numérico semântico

**Bloco numérico significa categoria de uso:**

| Bloco | Categoria | Frequência |
|---|---|---|
| `kn-01` a `kn-09` | Jornada inicial + manutenção da estrutura Koine | Raro |
| `kn-11` a `kn-89` | Operações cotidianas durante o trabalho | Frequente |
| `kn-99` | Fechamento de sessão | Sempre por último |

Espaço entre blocos permite adicionar skills sem renumeração cascata.

**Skills do primeiro release (5 skills):**

| # | Skill | Quando |
|---|---|---|
| `kn-01` | `recebe-usuario` | Primeira sessão do usuário — orquestra arquivo do usuário + primeiro escopo + primeiro contexto + agente operacional. 1×/usuário. |
| `kn-02` | `mantem-catalogo` | Configurar/atualizar arquivo do usuário, escopo, contexto, domínio (4 fluxos individuais). Raro. |
| `kn-03` | `cria-agente` | Criar agente operacional novo (especializado em um domínio). Raro. |
| `kn-11` | `mantem-referencia` | Catalogar conhecimento na pasta-referências do escopo atual. Frequente. |
| `kn-99` | `encerra-sessao` | Fechar sessão com diário, log, índices. Sempre por último. |

`kn-01` é meta-skill orquestradora: invoca internamente `kn-02` (fluxos arquivo do usuário, escopo, contexto) + `kn-03` (agente operacional) + narrativa de boas-vindas + checkpoints de aprovação.

### 14 — Sintaxe de invocação por cliente IA — wrappers `kn-<cliente>`

**Sintaxe canônica:**

```
kn-<cliente> <agente> [pasta]
```

Onde:
- **`<cliente>`** está embutido no nome do binário — `kn-claude`, `kn-agy` (Antigravity), `kn-copilot`, `kn-opencode`; outros adapters podem ser adicionados.
- **`<agente>`** é o nome do agente Koine a invocar (`hermes` ou agente operacional do usuário).
- **`[pasta]`** é opcional. Resolução em cascata:
  1. **Sem `[pasta]`** → usa `pwd`.
  2. **Alias** em `~/.config/koine/aliases.json` → resolve para path canônico.
  3. **Path direto** existente (relativo ou absoluto) → usa.
  4. **Fuzzy match** em pastas conhecidas (com `CONTEXTO.md`, ou pastas-referências de escopos do usuário) → oferece menu (fzf se disponível, fallback numerado); se usuário escolher, oferece salvar alias em `aliases.json`.

**Implementação:** wrappers são symlinks para o binário `kn-agente`, que detecta `os.Args[0]`. 1 binário, N nomes no PATH.

`kn-agente` permanece como **motor administrativo** (não invoca cliente IA):

```
kn-agente instalar
kn-agente instalar-habilidades --para=<harness>
kn-agente versao
kn-agente mostrar <agente> [pasta]    # debug, sem abrir cliente
kn-agente validar [pasta]
kn-agente mostrar-padrao <dominio>
```

Wrappers `kn-<cliente>` fazem: resolução de pasta → invocam o motor para gerar CLAUDE.md/AGENTS.md/etc. → abrem o cliente IA com contexto carregado.

**Razões:**

1. **Comando lê melhor.** `kn-claude hermes` é mais natural que `kn-agente claude hermes`.
2. **Cliente IA explícito no PATH.** Autocompletion do shell guia o usuário; documentação cita 1 comando por cliente.
3. **Mecanismo de resolução de pasta robusto** (alias + path + fuzzy) — produtivo no dia-a-dia, especialmente quando o usuário tem N pastas de trabalho e escopos.

ADR `20260620-cli-kn-agente-onda-1.md` previa só `kn-agente <agente> <pasta>` (sem cliente explícito). **Esta decisão (14) substitui aquela sintaxe** — `kn-agente <agente> <pasta>` deixa de existir como invocação de agente; passa a ser só comando administrativo.

## Estrutura final canônica

```
~/.local/share/koine/                       # (2) vault em disco — XDG_DATA_HOME, readonly em runtime
├── KOINE.md                                # método
├── agentes/
│   └── hermes.md                           # agente canônico Koine
├── habilidades/
│   ├── kn-01-recebe-usuario/SKILL.md       # onboarding (meta-skill)
│   ├── kn-02-mantem-catalogo/SKILL.md      # configurar/atualizar arquivo-usuario/escopo/contexto/dominio
│   ├── kn-03-cria-agente/SKILL.md          # criar agentes operacionais derivados
│   ├── kn-11-mantem-referencia/SKILL.md    # catalogar conhecimento (cotidiano)
│   └── kn-99-encerra-sessao/SKILL.md       # fechamento
└── .meta.json                              # versão + timestamp (máquina)

~/.config/koine/                            # (3) config do usuário — XDG_CONFIG_HOME, writeable
├── <nome>.md                               # arquivo do usuário (lowercase do primeiro nome)
├── escopos/
│   └── <slug>.md                           # Ficha Koine; campo pasta-referencias: tagged path
├── dominios/
│   └── <dom>.md                            # framework L3; canônico (plantado pelo instalar) ou user-created
└── agentes/
    └── <nome>.md                           # agente operacional do usuário (criado por kn-03-cria-agente)

<pasta-referencias>/                        # runtime, por escopo (path resolvido do tagged path)
├── index.md                                # contrato OKF
├── log.md                                  # contrato OKF
├── kn-indice-<dom>.md                      # gerado pelo kn-agente — catálogo de entradas
└── <slug>.md                               # referências (unidades)

# Embed-only no binário (não extraído para disco):
- vault/templates/*.tmpl                    # lidos via text/template do embed.FS
- vault/dominios/<dom>.md                   # plantado direto em ~/.config/koine/dominios/
```

## Render do CLAUDE.md (Modelo B)

```markdown
@/Users/<nome>/.config/koine/<nome>.md
@/Users/<nome>/.local/share/koine/KOINE.md
@/Users/<nome>/.local/share/koine/agentes/hermes.md
@/Users/<nome>/.config/koine/escopos/<slug-escopo>.md
@/Users/<nome>/<pasta-referencias>/kn-indice-universal.md
@/Users/<nome>/<pasta-referencias>/kn-indice-negocio.md
@CONTEXTO.md
```

Ordem: arquivo do usuário → método → agente → escopo → kn-indices por domínio → CONTEXTO da pasta de trabalho.

Cada `kn-indice-<slug-dominio>.md` já embute a sinopse do domínio. Frameworks de domínio não aparecem como linha separada — corpo denso de `dominios/<slug-dominio>.md` é lido por skills sob demanda. O `escopos/<slug-escopo>.md` carregado dá ao agente o pano de fundo da relação (dinâmica do escopo, stakeholders, foco operacional).

## Alternativas consideradas

| Decisão | Alternativa rejeitada | Por quê |
|---|---|---|
| 1 XDG | Manter `~/.koine/` dotfile | Inconsistência interna sem ganho real; XDG é convenção Go/Unix moderna e mapeia automático Windows |
| 2 Embed-only | Extrair semente pra disco | Duas cópias estáticas com risco de divergência; `mostrar-padrao` já cobre acesso à versão original |
| 3 Tagged | Path absoluto bruto | Quebra portabilidade entre máquinas e plataformas |
| 3 Tagged | Path relativo ao HOME sem prefixo | Não cobre cenário empresarial (compartilhado em equipe) |
| 4 Plural | Manter "base" / `base:` | Sobrecarga semântica (Unix base path, base-class, base de dados) |
| 4 Plural | Singular `referencia:` | Conflita com regra "plural quando catálogo navegável de items discretos" |
| 4 Plural | `acervo` / `cartório` | acervo perdeu na continuidade; cartório filtra observação mole por solenidade |
| 5 Ficha universal | Manter par `.yaml` + `.md` | Sincronização frágil, duas fontes de verdade |
| 6 Hermes | Manter `agentes/koine/AGENTE.md` | Colisão semântica método × agente; subpasta sem propósito local |
| 6 Hermes | `agentes/koine.md` lowercase | Resolve subpasta mas mantém colisão de nome com `KOINE.md` |
| 9 Sem prefixo | `biblioteca-dominios/` | Redundante (pasta já é biblioteca) |
| 10 Sem INDEX em vault | Manter `INDEX-<dom>.md` em `dominios/` | Conteúdo absorvido em `<dom>.md` pela decisão 5; índice de entradas é por-escopo e dinâmico |
| 11 Arquivo do usuário vs ficha | Tudo em `<nome>.md` global | Vaza CPF/RG em sessões que não precisam; infla contexto; mistura papéis |
| 11 Arquivo do usuário vs ficha | `<nome>.md` só por-escopo (sem global) | Duplica invariantes (idioma, timezone) com risco de divergência; agente perde usuário fora de escopo declarado |

## Consequências

**Positivas:**

- Convenção XDG honrada — Koine "se comporta" como cidadão Unix/Windows.
- Modelo mental simples: vault = arquivos que `@/` lê; config = tudo que o usuário escreve; embed = sementes que plantam.
- Sem duplicação de dados sensíveis (ficha vive em escopo dedicado).
- Multi-harness e Windows ganham cross-platform de graça.
- Extensões futuras (fork de agente, escopo-pai) cabem sem reorganização estrutural.

**Decisões em aberto:**

- Cadeia escopo-pai (formalizar antes de feature equivalente).
- Wildcard `escopos: ["*"]`.
- Cache de geração de `kn-indice-<dom>.md` (se virar gargalo).
- Convenção de prefixos tagged path adicionais (`nfs:`, `drive:`, etc).

## Referências

- ADRs relacionados:
  - `20260620-cli-kn-agente-onda-1.md`
  - `20260620-contexto-md-local-sem-cascata.md`
  - `20260620-distribuicao-embed-e-instalar.md`
  - `20260620-okf-conformance-e-frontmatter.md`
- XDG Base Directory Specification — https://specifications.freedesktop.org/basedir-spec/latest/
