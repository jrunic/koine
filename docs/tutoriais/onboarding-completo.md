---
descricao: Tutorial passo a passo do zero ao primeiro agente operacional configurado — instala o Koine (aplicação Python), finaliza configuração, abre sessão com Hermes, completa onboarding via /kn-01
id: 202606280001
tipo: tutorial
status: ativo
tags: [tutorial, onboarding, instalacao, primeira-sessao]
---

# Tutorial — Onboarding completo

Este tutorial leva você do zero até um Koine **totalmente configurado e pronto para uso**: arquivo de usuário, primeiro escopo, primeira pasta de trabalho real, primeiro agente operacional. Tempo total em ritmo confortável: 20-30 minutos (depende do quanto você reflete em cada resposta da entrevista — pular sem pensar acelera mas piora a qualidade da configuração).

Ao final, você terá:

- Koine instalado, com os wrappers `koine` e `kn-*` em `~/.local/bin/` (ou equivalente Windows)
- Pasta canônica em `~/koine` (acessível pelo alias `koine`)
- Arquivo de usuário em `~/.config/koine/<seu-nome>.md`
- Primeiro escopo + pasta de referências
- Primeira pasta de trabalho com `CONTEXTO.md`
- Primeiro agente operacional, criado por você junto com Hermes

## Pré-requisitos

### Um cliente IA terminal (obrigatório)

Escolha **um** dos quatro suportados. Sem cliente IA, o Koine instala mas você não consegue abrir sessão.

| Cliente | Como instalar | Documentação |
|---|---|---|
| **Claude Code** (Anthropic) | `npm install -g @anthropic-ai/claude-code` | https://docs.claude.com/en/docs/claude-code/setup |
| **Antigravity** (Google) | macOS/Linux: `curl -fsSL https://antigravity.google/cli/install.sh \| bash` | https://antigravity.google/docs/cli-install |
| **GitHub Copilot CLI** | `npm install -g @github/copilot` | https://docs.github.com/copilot/copilot-cli |
| **OpenCode** | macOS/Linux: `curl -fsSL https://opencode.ai/install \| bash` | https://opencode.ai/docs |

### Dependências dos clientes

- **Node.js 18+ (recomendado 22+)** — necessário para Claude Code e Copilot CLI (instalação via `npm`). Download: https://nodejs.org/
- **Homebrew** — opcional em macOS, recomendado. Gerenciador de pacotes que facilita instalação de Node e clientes IA. Instalar: https://brew.sh/

Se você rodar `koine instalar` sem cliente IA detectado, o instalador orienta o que falta — não precisa decorar nada agora.

---

## Passo 1 — Instalar o Koine

### macOS / Linux

```bash
curl -fsSL https://github.com/jrunic/koine/releases/latest/download/install.sh | sh
```

O script:
- Localiza um Python ≥ 3.12 no PATH (erro orientativo se ausente — nada é instalado pela metade)
- Baixa o pacote `koine-<versão>.zip` de GitHub Releases
- Extrai para `~/.local/share/koine/dist/`
- Roda `koine instalar` (vault, wrappers `kn-*`, pasta canônica, skills)
- Avisa se `~/.local/bin/` não está no seu PATH

### Windows (Command Prompt — recomendado em estações corporativas)

```cmd
curl -L -o install.bat https://github.com/jrunic/koine/releases/latest/download/install.bat
install.bat
```

O `install.bat` invoca o `install.ps1` com `-ExecutionPolicy Bypass` inline, contornando restrições de execução em estações com política restritiva — sem precisar de admin.

### Windows (PowerShell — alternativa)

```powershell
iwr -useb https://github.com/jrunic/koine/releases/latest/download/install.ps1 | iex
```

### Validar instalação

```bash
koine versao
```

Esperado: `koine 0.4.0` (ou versão mais recente).

Se o comando não for encontrado, `~/.local/bin/` provavelmente não está no PATH. O instalador imprime a linha exata para adicionar ao seu shell profile. **Reabra o terminal** após adicionar.

---

## Passo 2 — Finalizar configuração

```bash
koine instalar
```

O `install.sh` já executa este passo. Rode manualmente só se pulou o installer ou para reconfigurar.

Este comando passa por várias fases, em ordem:

### 2.1 Extração do vault

Vault (KOINE.md + agente Hermes + 5 skills + templates + sementes de domínios) é copiado do pacote para `~/.local/share/koine/`.

```
Instalando vault em /Users/<você>/.local/share/koine
Plantando domínios em /Users/<você>/.config/koine/dominios
Instalação concluída.
```

### 2.2 Wrappers de cliente IA

Os wrappers `koine`, `kn-claude`, `kn-agy`, `kn-copilot`, `kn-opencode` e `kn-codex` são gerados em `~/.local/bin/`, invocando o Python absoluto detectado na instalação. Quem vem de uma instalação Go v0.3.x: os antigos symlinks `kn-*` são substituídos automaticamente; qualquer outro arquivo pré-existente é preservado com aviso.

### 2.3 Pasta canônica + alias

```
Configurando pasta canônica:
Onde fica sua pasta canônica para sessões com Hermes? [~/koine]:
```

Enter aceita `~/koine` (recomendado). Você pode digitar outro caminho se preferir.

- Pasta é criada (se não existir)
- Alias `koine` é registrado em `~/.config/koine/aliases.json` apontando para ela
- `<pasta>/CONTEXTO.md` é gerado com `bootstrap: true` — sinaliza que estamos em onboarding

```
✓ Pasta canônica em /Users/<você>/koine
✓ Alias 'koine' registrado
```

### 2.4 Skills do harness

```
Instalando skills de harness:
  claude detectado → instalar skills kn-*? [S/n]:
```

Se você tem um cliente IA instalado, `koine instalar` detecta e pergunta. Enter aceita; skills `kn-*` são symlinkadas em `~/.claude/skills/` (ou equivalente).

**Se nenhum cliente IA estiver instalado**, esta fase mostra mensagem orientativa com:
- Bloco "Node.js não encontrado" (se faltar Node)
- Bloco "Homebrew não encontrado" (se faltar Brew em macOS)
- Lista dos 5 clientes IA com comando de instalação por OS
- Instrução para rodar `koine instalar` novamente após instalar um cliente

### 2.5 Mensagem final

```
Para começar sua primeira sessão com Hermes:

  kn-claude hermes koine

Dentro da sessão, rode: /kn-01-recebe-usuario

Se você usa outro cliente, troque o prefixo:
  Antigravity:  kn-agy hermes koine
  Copilot CLI:  kn-copilot hermes koine
  OpenCode:     kn-opencode hermes koine
  Codex CLI:    kn-codex hermes koine
```

---

## Passo 3 — Abrir a primeira sessão

```bash
kn-claude hermes koine
```

Substitua `kn-claude` pelo wrapper do seu cliente: `kn-agy`, `kn-copilot`, `kn-opencode` ou `kn-codex`.

O wrapper:

1. Resolve o alias `koine` → pasta canônica
2. Lê `CONTEXTO.md` da pasta; encontra `bootstrap: true`
3. Carrega contexto reduzido (USUARIO ainda não existe + KOINE.md + Hermes + corpo do CONTEXTO.md com instruções de onboarding)
4. Lança o cliente IA com o contexto pronto

Hermes inicia a sessão e **automaticamente conduz o `/kn-01-recebe-usuario`** — você não precisa invocar; o `CONTEXTO.md` de bootstrap diz a ele para começar.

---

## Passo 4 — Onboarding com `/kn-01-recebe-usuario`

Hermes apresenta 4 personagens-âncora (Bruce Wayne / Hermione Granger / Indiana Jones / Princesa Leia). Escolha o que você conhece melhor — Hermes usa o personagem como exemplo concreto ao longo das 4 rodadas.

### Rodada 1 — Arquivo do usuário (7 perguntas)

Nome completo, como te chamar, idioma, fuso horário, papel principal, estilo de comunicação, currículo curto. Materializa `~/.config/koine/<seu-nome>.md`.

### Rodada 2 — Primeiro escopo

Apelido do escopo, descrição, pasta de referências, dinâmica. Materializa `~/.config/koine/escopos/<apelido>.md` + pasta de referências com `index.md` e `log.md`.

### Rodada 3 — Primeira pasta de trabalho

Caminho da pasta, descrição, domínios relevantes. Materializa `<pasta>/CONTEXTO.md`. Hermes te orienta a escolher uma pasta diferente de `~/koine` (que é para meta-trabalho com o método, não para trabalho real).

### Rodada 4 — Primeiro agente operacional

Hermes apresenta o conceito e **delega para `/kn-03-cria-agente`**, que conduz 8 sub-rodadas (identidade, âncora ficcional opcional, foco operacional, tom, calibragens, mecânica). Materializa `~/.config/koine/agentes/<nome>.md`.

### Fechamento

Ao final, Hermes reescreve o `CONTEXTO.md` da pasta canônica substituindo `bootstrap: true` por escopo real `koine` + cria `~/.config/koine/escopos/koine.md`. A pasta canônica vira escopo permanente de **meta-trabalho** com o método.

Para detalhes do que cada rodada produz e dos critérios usados, ver [referência de habilidades](../referencias/habilidades.md#kn-01-recebe-usuario).

---

## Próximos passos — depois do onboarding

### Trabalhar com seu agente operacional

```bash
cd <sua pasta de trabalho da Rodada 3>
kn-claude <nome-do-agente>
```

O agente abre a sessão **já sabendo tudo** que configuramos: quem você é, qual o escopo, quais domínios carregar, qual o foco da pasta. Você não precisa explicar nada.

### Manter o Koine — voltar para o meta-trabalho

```bash
cd ~/koine
kn-claude hermes
```

Use sempre que precisar criar outro escopo, criar outro agente operacional, atualizar seu perfil, criar um domínio novo, ou catalogar conhecimento sobre o próprio método.

### Outras skills úteis

| Quando | Skill |
|---|---|
| Criar novo escopo, domínio ou atualizar perfil | `/kn-02-mantem-catalogo` |
| Criar outro agente operacional | `/kn-03-cria-agente` |
| Catalogar conhecimento durante o trabalho | `/kn-11-mantem-referencia` |
| Fechar sessão registrando aprendizados | `/kn-99-encerra-sessao` |

Detalhes na [referência de habilidades](../referencias/habilidades.md).

---

## Resolução de problemas

### `koine: command not found` após instalar

`~/.local/bin/` não está no seu PATH. O instalador imprime a linha exata para adicionar — siga e reabra o terminal. Em Windows, rode o comando `SetEnvironmentVariable` indicado.

### Windows: e o SmartScreen?

Não se aplica mais: o Koine é distribuído como código Python (`koine.pyz`), sem executável compilado. Integridade: compare o SHA-256 do zip com o `SHA256SUMS` publicado no release.

### Nenhum cliente IA detectado em `koine instalar`

Esperado se você ainda não instalou. O instalador mostra orientação completa com comandos por OS. Instale um cliente, depois rode `koine instalar` novamente — ele detecta.

### Sessão Hermes não inicia `/kn-01` automaticamente

Verifique se `<pasta-canonica>/CONTEXTO.md` contém `bootstrap: true` no cabeçalho. Se você editou manualmente e removeu, rode `/kn-01-recebe-usuario` explicitamente na sessão.

### Quero reconfigurar do zero

> ⚠️ **Atenção — leia antes:** os três diretórios abaixo contêm coisas diferentes. Reveja o que cada um guarda **antes** de apagar.
>
> - `~/.local/share/koine/` — vault readonly copiado do pacote. Pode apagar à vontade; `koine instalar` regenera.
> - `~/.config/koine/` — sua configuração: arquivo de usuário, escopos, aliases, agentes operacionais, domínios. **Apagar perde todo o trabalho de onboarding** e qualquer agente que você criou depois.
> - `~/koine/` — sua pasta canônica e o conteúdo de meta-trabalho que você acumulou ali (referências, diários do escopo `koine`, etc.). **Faça backup antes** se houver conteúdo que vale guardar.

Em ordem de "menor para maior impacto":

```bash
# 1. Só o vault (regenera sem perda)
rm -r ~/.local/share/koine

# 2. Vault + config do usuário (perde aliases, escopos, agentes — sem retorno)
rm -r ~/.local/share/koine ~/.config/koine

# 3. Tudo, inclusive a pasta canônica (faça backup antes se houver conteúdo)
#    Verifique o conteúdo com: ls -la ~/koine
rm -r ~/.local/share/koine ~/.config/koine ~/koine
```

Depois rode:

```bash
koine instalar
```

E refaça o onboarding via `kn-claude hermes koine`.

---

## Referências

- [CLI](../referencias/cli.md) — comandos `koine` e wrappers
- [Habilidades](../referencias/habilidades.md) — detalhe das 5 skills `kn-*`
- [Schema do CONTEXTO.md](../referencias/contexto-md.md) — frontmatter e validações
