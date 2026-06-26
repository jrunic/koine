---
id: 202606251830
titulo: Harness.Renderizar retorna Lancamento em vez de []byte
tipo: adr
status: aceito
tags: [harness, lancamento, adapters]
---

# ADR: Harness.Renderizar retorna Lancamento em vez de []byte

## Contexto

`Harness.Renderizar` original retorna `([]byte, error)` — assume que todo
adapter produz um único arquivo no working dir. Copilot CLI e OpenCode exigem
múltiplos arquivos em cache externo, symlinks e env vars setadas antes do Exec.
Adapters não podem expressar essas necessidades com `[]byte`.

## Decisão

`Harness.Renderizar` passa a retornar `(Lancamento, error)`. `Lancamento` é
uma struct descritiva que contém:

- `ArquivosNoWorkingDir map[string][]byte` — arquivos relativos ao working dir
- `ArquivosExternos     map[string][]byte` — arquivos em paths absolutos (cache)
- `Symlinks             map[string]string` — mapa symlink-path → alvo
- `EnvVars              map[string]string` — variáveis adicionadas ao Exec
- `ExtraArgs            []string`          — args extras para o cliente IA

O wrapper consome o `Lancamento` deterministicamente: escreve arquivos, cria
symlinks, monta env e lança o cliente via `syscall.Exec`.

Adapters simples (Claude, Antigravity) preenchem apenas `ArquivosNoWorkingDir`.

## Alternativa rejeitada

Type assertion opcional (`if b, ok := h.(BundleAdapter); ok { b.Bundle() }`):
fragmenta o contrato, exige código de desvio em todo consumidor. `Lancamento`
unifica em único retorno — consumidor não precisa saber qual adapter é.

## Consequências

- `ClaudeCode` e `Antigravity` retornam `Lancamento{ArquivosNoWorkingDir: ...}`.
- Copilot e OpenCode preenchem `ArquivosExternos`, `EnvVars`, `Symlinks`.
- `cmd/kn-agente/gerar.go:executar` extrai `ArquivosNoWorkingDir["CLAUDE.md"]`.
- `cmd/kn-agente/wrapper.go:rodarWrapper` orquestra o ciclo completo.
- Testes de adapter comparam `Lancamento` esperado vs obtido, campo a campo.
