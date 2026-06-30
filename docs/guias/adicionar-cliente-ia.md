---
descricao: Guia para mantenedores — como adicionar suporte a um novo cliente IA (novo adapter Harness)
id: 202606261003
tipo: guia
status: ativo
tags: [guia, harness, adapter, contribuir]
---

# Guia — Adicionar suporte a um novo cliente IA

Audiência: mantenedores ou contribuidores que querem adicionar um adapter Koine para um cliente IA terminal não suportado atualmente.

## Pré-requisitos

- Familiaridade com Go 1.22+ e a interface `Harness` (ver `internal/harness/interface.go`).
- Documentação oficial do cliente IA alvo — qual mecanismo de instrução de projeto ele suporta? (`CLAUDE.md` style com `@path` includes? `AGENTS.md` no working dir? config JSON apontando para paths externos? env var para diretórios de instruções?)
- Conhecimento do ADR [`20260625-harness-lancamento-struct.md`](../decisoes/20260625-harness-lancamento-struct.md) — contrato `Lancamento`.

## Visão geral do contrato

`Harness.Renderizar` retorna `(Lancamento, error)`. A struct `Lancamento` descreve tudo que o wrapper deve materializar:

```go
type Lancamento struct {
    ArquivosNoWorkingDir map[string][]byte  // path relativo → bytes
    ArquivosExternos     map[string][]byte  // path absoluto → bytes (cache)
    Symlinks             map[string]string  // path do symlink → alvo
    EnvVars              map[string]string  // env vars para o exec
    ExtraArgs            []string           // args extras para o cliente
}
```

Adapter "simples" (cliente lê 1 arquivo no working dir com `@path` includes) preenche apenas `ArquivosNoWorkingDir`. Adapter "complexo" (cliente exige config externa + env var + symlink) preenche os demais campos.

## Passos

### 1. Investigação empírica antes de codar

Antes de qualquer código, abra uma pasta de teste e valide manualmente como o cliente IA carrega instruções:

```bash
mkdir -p ~/tmp/koine-novo-cliente && cd ~/tmp/koine-novo-cliente
# Crie manualmente o arquivo que você acha que o cliente lê
echo "@/Users/<vc>/.config/koine/<nome>.md" > <arquivo-de-instrucao>
<comando-do-cliente>
# Pergunte ao agente algo que só estaria no arquivo apontado
```

A doc oficial às vezes omite mecanismos importantes (caso real: o suporte a `@path` no Antigravity não está documentado mas funciona). Validar empiricamente economiza horas.

### 2. Adicionar entrada em `clientesSuportados`

`cmd/kn-agente/wrapper.go` mantém o mapa de wrappers ativos:

```go
var clientesSuportados = map[string]bool{
    "claude":   true,
    "agy":      true,
    "copilot":  true,
    "opencode": true,
    "<novo>":   true,   // ← adicionar
}
```

### 3. Criar adapter em `internal/harness/<novo>.go`

Implementar:

```go
type <Novo> struct {
    VaultFS fs.FS
    Agente  string
}

func (h *<Novo>) Nome() string { return "<novo>" }
func (h *<Novo>) CaminhoArquivoContexto(cwd string) string { return filepath.Join(cwd, "<ARQUIVO>") }
func (h *<Novo>) Renderizar(dados ContextoMontado) (Lancamento, error) { ... }

var _ Harness = (*<Novo>)(nil)
```

Há três estilos de adapter, conforme o cliente entrega o contexto ao modelo:

- **Ponteiro (`@path`)** — estilo Claude/Antigravity. O cliente resolve `@path` includes nativamente (injeta o conteúdo do arquivo antes do agente rodar). O adapter gera um arquivo de ponteiros a partir do template em `vault/templates/`; cabe em `Renderizar` retornando só `ArquivosNoWorkingDir`. Zero duplicação.
- **Bundle em cache** — estilo Copilot/OpenCode. O cliente carrega instruções via env var apontando para um diretório/arquivo descartável. Use `internal/cache/` para slots determinísticos e `internal/render/merge.go` para concatenar as seções; o adapter retorna `ArquivosExternos` (em `~/.cache/koine/`) + `EnvVars` + (opcional) `Symlinks` para o `CONTEXTO.md` no working dir.
- **Inline no working dir** — estilo Codex. Use quando o cliente **não** resolve `@path` como include nativo — o Codex injeta o texto literal do arquivo de instruções, e o agente só leria os paths via tool call (best-effort, não garantido). O adapter então **embute o conteúdo** das seções (via `internal/render/merge.go`) direto no arquivo do working dir e retorna `ArquivosNoWorkingDir` + `ExtraArgs` (ex.: `-c project_doc_max_bytes=...` para não truncar bundles grandes). Sem cache, sem env var. `CONTEXTO.md` permanece separado, apontado por prosa. Referência: `internal/harness/codex.go`.

> Antes de assumir que um cliente resolve `@path` nativamente (estilo ponteiro), **valide empiricamente**: inspecione o transcript de uma sessão real e cheque se o agente leu os arquivos via tool call (Mecanismo B, inline) ou se o conteúdo chegou injetado sem leitura (Mecanismo A, ponteiro). A narração do agente ("li os arquivos") não distingue os dois.

### 4. Adicionar symlink em `kn-agente instalar`

`internal/instalar/instalar.go::CriarSymlinks` mantém a lista de wrappers:

```go
links := []string{"kn-claude", "kn-agy", "kn-copilot", "kn-opencode", "kn-<novo>"}
```

### 5. Atualizar despacho em `cmd/kn-agente/wrapper.go`

Adapter `<Novo>` precisa ser injetado no switch que escolhe o adapter em runtime (ver função `rodarWrapper`).

### 6. Testes

- Unit test do adapter (`internal/harness/<novo>_test.go`): construir `ContextoMontado` em memória, comparar `Lancamento` esperado vs obtido — campo a campo.
- Smoke test do wrapper: `pastaAbs` temporário com `CONTEXTO.md` mínimo, mock de `lancarCliente`, verificar filesystem + env vars.
- Bootstrap mode também precisa de teste.

### 7. Documentação

- README — adicionar linha na tabela "Clientes IA suportados".
- CHANGELOG — registrar adapter novo na próxima versão.
- ADR opcional se a decisão arquitetural for não-óbvia.

## Pontos de atenção

- **CONTEXTO.md é mutável e canônico** — agente IA edita esse arquivo entre sessões. O adapter NUNCA deve copiar `CONTEXTO.md` para outro lugar; aponta direto ou usa symlink.
- **Configurações globais do cliente IA** (`~/.copilot/`, `~/.config/opencode/`, `~/.gemini/`, etc.) NUNCA são tocadas pelo adapter; mas o wrapper avisa quando elas existem e podem afetar a sessão.
- **`os.Symlink` no Windows** requer privilégio elevado — tratar como caso especial se Windows estiver no roadmap.
- **Marker `<!-- gerado por kn-agente -->`** na primeira linha de arquivos gerados — permite detecção de conflito sem manifesto.

## Referências

- ADR [`20260625-harness-lancamento-struct.md`](../decisoes/20260625-harness-lancamento-struct.md) — contrato `Lancamento`.
- `internal/harness/claude_code.go` — adapter mais simples, bom ponto de partida.
- `internal/harness/copilot.go` — adapter mais complexo, bom referência para casos com bundle externo.
- `internal/cache/cache.go` — slot determinístico baseado em hash do `pastaAbs`.
- `internal/render/merge.go` — concatenação de USUARIO + Hermes para `AGENTS.md` único.
