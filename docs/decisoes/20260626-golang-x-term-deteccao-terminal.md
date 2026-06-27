---
id: 202606261600
tipo: decisao
status: aceito
description: ADR — adotar golang.org/x/term para detecção de terminal em kn-agente instalar
tags: [adr, koine, golang-x-term, terminal, onboarding]
---

# ADR — golang.org/x/term para detecção de terminal

## Status

Aceito.

## Contexto

`kn-agente instalar` precisa detectar se está rodando com usuário interativo (exibir
prompt Y/n) ou em modo não-interativo (script, CI — pular prompt). A detecção de terminal
interativo em Go multiplataforma tem duas opções:

**Opção A — `golang.org/x/term`**

```go
import "golang.org/x/term"
isInterativo := term.IsTerminal(int(os.Stdin.Fd()))
```

- Pro: uma linha, intenção clara, comportamento correto em Linux, macOS e Windows.
- Contra: nova dependência externa — requer ADR por política "stdlib primeiro".

**Opção B — `os.Stdin.Stat()` + `ModeCharDevice`**

```go
fi, _ := os.Stdin.Stat()
isInterativo := fi.Mode()&os.ModeCharDevice != 0
```

- Pro: stdlib puro.
- Contra: não funciona em Windows — `ModeCharDevice` retorna falso mesmo com usuário
  na frente do terminal. Koine tem Windows como alvo declarado.

## Decisão

Adotar `golang.org/x/term`. Usabilidade importa: quebra silenciosa no Windows
(Opção B nunca mostraria prompt) é pior do que uma dependência externa bem mantida.

`golang.org/x/term` é mantido pela equipe Go, sem dependências transitivas, e é
a solução canônica usada por ferramentas como `gh` e `kubectl` para o mesmo problema.

## Uso

```go
import "golang.org/x/term"

isInterativo := term.IsTerminal(int(os.Stdin.Fd()))
```

Restrito a `cmd/kn-agente/instalar.go`. Não vaza para pacotes internos.

## Consequências

- `go.mod` ganha `require golang.org/x/term`.
- `go.sum` atualizado por `go mod tidy`.
- Sem impacto em `internal/` — uso confinado ao layer CLI.
