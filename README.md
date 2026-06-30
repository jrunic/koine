# Koine

> CLI que injeta contexto multi-camada (usuário, agente, referências, contexto da pasta) em harnesses de IA terminal — Claude Code, Antigravity (`agy`), GitHub Copilot CLI, OpenCode, Codex CLI.

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

## Pré-requisitos

Para Koine fazer sentido, você precisa de:

- **Um cliente IA terminal** suportado — Claude Code, Antigravity, GitHub Copilot CLI, OpenCode ou Codex CLI. Tabela abaixo na seção [Clientes IA suportados](#clientes-ia-suportados).
- **Node.js 18+** (recomendado 22+) — necessário para instalar Claude Code e Copilot CLI via `npm`. Download: <https://nodejs.org/>.
- **Homebrew** (opcional em macOS) — gerenciador recomendado para instalar Node e clientes IA. Instalar: <https://brew.sh/>.

Se você rodar `kn-agente instalar` sem cliente IA detectado, o próprio binário orienta o que falta com comandos por OS — não precisa decorar nada agora.

## Instalação

### macOS / Linux

```bash
curl -fsSL https://github.com/jrunic/koine/releases/latest/download/install.sh | sh
```

### Windows (Command Prompt — recomendado em estações corporativas)

```cmd
curl -L -o install.bat https://github.com/jrunic/koine/releases/latest/download/install.bat
install.bat
```

`install.bat` invoca `install.ps1` com `-ExecutionPolicy Bypass` inline — contorna restrições de PowerShell em estações com política restritiva, sem precisar de admin.

### Windows (PowerShell — alternativa)

```powershell
iwr -useb https://github.com/jrunic/koine/releases/latest/download/install.ps1 | iex
```

### Alternativa com Go 1.22+

```bash
go install github.com/jrunic/koine/cmd/kn-agente@latest
```

Útil para desenvolvedores Go que já têm o toolchain. Após instalar, rode `kn-agente instalar` para extrair o vault.

**Plataformas suportadas:** `darwin-arm64`, `darwin-amd64`, `linux-amd64`, `windows-amd64`.

## Primeira sessão em 3 comandos

```bash
# 1. Finalizar configuração (cria pasta canônica, alias 'koine', instala skills)
kn-agente instalar

# 2. Abrir primeira sessão com Hermes
kn-claude hermes koine
# (substitua kn-claude pelo wrapper do seu cliente: kn-agy, kn-copilot, kn-opencode, kn-codex)

# 3. Dentro da sessão, Hermes inicia automaticamente:
#    /kn-01-recebe-usuario
```

`/kn-01-recebe-usuario` é a skill de onboarding. Hermes te entrevista em 4 rodadas e configura:

- Seu **arquivo de usuário** (idioma, fuso horário, estilo)
- Seu **primeiro escopo** de trabalho
- Sua **primeira pasta de trabalho** real (com `CONTEXTO.md`)
- Seu **primeiro agente operacional** (criado via `/kn-03-cria-agente`)

**Para o passo a passo completo (incluindo pré-requisitos detalhados, estimativas de tempo, e resolução de problemas):** ver [`docs/tutoriais/onboarding-completo.md`](docs/tutoriais/onboarding-completo.md).

## Skills `kn-*`

Distribuídas no vault e disponíveis após `kn-agente instalar`:

| Skill | Quando invocar |
|---|---|
| `/kn-01-recebe-usuario` | Onboarding inicial (1× por usuário; Hermes dispara automaticamente em pasta de bootstrap) |
| `/kn-02-mantem-catalogo` | Criar/ajustar arquivo do usuário, escopo, contexto de pasta, ou domínio |
| `/kn-03-cria-agente` | Criar novo agente operacional especializado em um tipo de trabalho |
| `/kn-11-mantem-referencia` | Catalogar conhecimento (pessoa, decisão, aprendizado) durante o trabalho |
| `/kn-99-encerra-sessao` | Fechar sessão escrevendo diário e distribuindo aprendizados |

Detalhes em [`docs/referencias/habilidades.md`](docs/referencias/habilidades.md).

## Clientes IA suportados

| Cliente | Comando | Mecanismo |
|---|---|---|
| Claude Code | `kn-claude` | `CLAUDE.md` com `@path` includes |
| Antigravity (`agy`) | `kn-agy` | `GEMINI.md` com `@path` includes |
| GitHub Copilot CLI | `kn-copilot` | `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` + bundle em cache |
| OpenCode | `kn-opencode` | `OPENCODE_CONFIG` + JSON em cache |
| Codex CLI | `kn-codex` | `AGENTS.md` inline + `-c project_doc_max_bytes` |

## Documentação

**Começando do zero?** [Tutorial — Onboarding completo](docs/tutoriais/onboarding-completo.md)

- [Tutoriais](docs/tutoriais/) — passo a passo para começar
- [Guias](docs/guias/) — como resolver problemas específicos
- [Referências](docs/referencias/) — CLI, schema do `CONTEXTO.md`, habilidades, formato OKF
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
