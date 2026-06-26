# Koine

> CLI que injeta contexto multi-camada (usuário, agente, referências, contexto da pasta) em harnesses de IA terminal — Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Go](https://img.shields.io/badge/go-1.22+-00ADD8.svg)](go.mod)

## Por que existe

Agentes de IA terminal abrem cada sessão zeradas. O usuário precisa repetir, a cada turno, quem é, em que projeto trabalha, qual padrão da casa, qual contexto da pasta. Repetir contexto consome tempo, polui prompts e degrada qualidade da resposta.

Koine resolve isso separando o que normalmente vem embaralhado em "memória de agente":

1. **Harness** — `kn-agente` carrega contexto e escreve o arquivo que o cliente IA lê na inicialização (`CLAUDE.md`, `GEMINI.md`, etc.)
2. **Habilidades** — skills `kn-*` que o agente invoca durante a sessão
3. **Base de conhecimento** — bundle [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/) com perfis, escopos, domínios e referências; propriedade do usuário
4. **Sistema de arquivos** — recomendado, não obrigatório

Cada camada evolui em ritmo próprio. O agente IA passa a "já saber" quem você é, no que está trabalhando e onde está, sem precisar contar de novo a cada turno.

## Instalação

Baixe o binário do release mais recente para sua plataforma:

```bash
# macOS / Linux — exemplo (substitua o sufixo pela sua plataforma)
curl -L https://github.com/jrunic/koine/releases/latest/download/kn-agente-darwin-arm64 -o /usr/local/bin/kn-agente
chmod +x /usr/local/bin/kn-agente
```

Plataformas suportadas: `darwin-arm64`, `darwin-amd64`, `linux-amd64`, `windows-amd64`.

Alternativamente, com Go 1.22+:

```bash
go install github.com/jrunic/koine/cmd/kn-agente@latest
```

Em seguida, extraia o vault e instale os symlinks de cliente IA:

```bash
kn-agente instalar
```

Isso cria `~/.local/share/koine/` (vault readonly) e symlinks `kn-claude`, `kn-agy`, `kn-copilot`, `kn-opencode` apontando para `kn-agente`.

## Sessão em 60 segundos

```bash
# 1. Configure seu arquivo de usuário (uma vez por máquina)
$EDITOR ~/.config/koine/<seu-primeiro-nome>.md

# 2. Crie a primeira pasta de trabalho
mkdir -p ~/projeto-x && cd ~/projeto-x
$EDITOR CONTEXTO.md                 # frontmatter mínimo: escopo + dominios

# 3. Abra o cliente IA com contexto Koine
kn-claude hermes .
```

Sessão Claude Code abre na pasta com `CLAUDE.md` gerado contendo:

- perfil do usuário
- persona do agente Hermes
- escopo da pasta
- índice de referências por domínio
- `CONTEXTO.md` da pasta

Mesma sintaxe vale para `kn-agy`, `kn-copilot`, `kn-opencode`.

## Clientes IA suportados

| Cliente | Comando | Mecanismo |
|---|---|---|
| Claude Code | `kn-claude` | `CLAUDE.md` com `@path` includes |
| Antigravity (`agy`) | `kn-agy` | `GEMINI.md` com `@path` includes |
| GitHub Copilot CLI | `kn-copilot` | `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` + bundle em cache |
| OpenCode | `kn-opencode` | `OPENCODE_CONFIG` + JSON em cache |

## Documentação

- [Tutoriais](docs/tutoriais/) — passo a passo para começar
- [Guias](docs/guias/) — como resolver problemas específicos
- [Referências](docs/referencias/) — comandos CLI, schema do `CONTEXTO.md`, formato OKF
- [Explicações](docs/explicacoes/) — por que cada decisão de design
- [Decisões](docs/decisoes/) — ADRs

## Desenvolvimento

Ver [`CONTEXTO.md`](CONTEXTO.md) para stack, padrões e como contribuir.

```bash
go build ./cmd/kn-agente
go test ./...
```

## Licença

[MIT](LICENSE).
