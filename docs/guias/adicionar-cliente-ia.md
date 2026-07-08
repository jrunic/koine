---
descricao: Guia para mantenedores — como adicionar suporte a um novo cliente IA (novo adapter)
id: 202606261003
tipo: guia
status: ativo
tags: [guia, harness, adapter, contribuir]
---

# Guia — Adicionar suporte a um novo cliente IA

Audiência: mantenedores ou contribuidores que querem adicionar um adapter Koine para um cliente IA terminal não suportado atualmente.

## Pré-requisitos

- Familiaridade com Python 3.12+ e o contrato de adapter (`src/koine/adapters/` + `src/koine/lancamento.py`).
- Documentação oficial do cliente IA alvo — qual mecanismo de instrução de projeto ele suporta? (`CLAUDE.md` style com `@path` includes? `AGENTS.md` no working dir? config JSON apontando para paths externos? env var para diretórios de instruções?)
- Conhecimento do ADR [`20260625-harness-lancamento-struct.md`](../decisoes/20260625-harness-lancamento-struct.md) — contrato `Lancamento`.

## Visão geral do contrato

Cada adapter é um módulo em `src/koine/adapters/<novo>.py` que expõe `renderizar(cm) -> Lancamento`. A dataclass `Lancamento` (`src/koine/lancamento.py`) descreve tudo que o wrapper deve materializar:

```python
@dataclass
class Lancamento:
    arquivos_working_dir: dict  # path relativo → conteúdo (str)
    arquivos_externos: dict     # path absoluto → conteúdo (cache)
    symlinks: dict              # path do symlink → alvo
    env_vars: dict              # env vars para o exec
    extra_args: list            # args extras para o cliente
```

Adapter "simples" (cliente lê 1 arquivo no working dir com `@path` includes) preenche apenas `arquivos_working_dir`. Adapter "complexo" (cliente exige config externa + env var + symlink) preenche os demais campos.

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

### 2. Criar o módulo do adapter em `src/koine/adapters/<novo>.py`

Implementar:

```python
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

ARQUIVO = "<ARQUIVO-DE-INSTRUCAO>"


def renderizar(cm: ContextoMontado) -> Lancamento:
    ...
```

Há três estilos de adapter, conforme o cliente entrega o contexto ao modelo:

- **Ponteiro (`@path`)** — estilo Claude/Antigravity. O cliente resolve `@path` includes nativamente (injeta o conteúdo do arquivo antes do agente rodar). O adapter gera um arquivo de ponteiros; cabe em `renderizar` retornando só `arquivos_working_dir`. Zero duplicação. Referência: `src/koine/adapters/claude.py`.
- **Bundle em cache** — estilo Copilot/OpenCode. O cliente carrega instruções via env var apontando para um diretório/arquivo descartável. Use `src/koine/cache.py` para slots determinísticos e `src/koine/render.py` para concatenar as seções; o adapter retorna `arquivos_externos` (em `~/.cache/koine/`) + `env_vars` + (opcional) `symlinks` para o `CONTEXTO.md` no working dir. Referência: `src/koine/adapters/copilot.py`.
- **Inline no working dir** — estilo Codex. Use quando o cliente **não** resolve `@path` como include nativo — o Codex injeta o texto literal do arquivo de instruções, e o agente só leria os paths via tool call (best-effort, não garantido). O adapter então **embute o conteúdo** das seções (via `src/koine/render.py`) direto no arquivo do working dir e retorna `arquivos_working_dir` + `extra_args` (ex.: `-c project_doc_max_bytes=...` para não truncar bundles grandes). Sem cache, sem env var. `CONTEXTO.md` permanece separado, apontado por prosa. Referência: `src/koine/adapters/codex.py`.

> Antes de assumir que um cliente resolve `@path` nativamente (estilo ponteiro), **valide empiricamente**: inspecione o transcript de uma sessão real e cheque se o agente leu os arquivos via tool call (Mecanismo B, inline) ou se o conteúdo chegou injetado sem leitura (Mecanismo A, ponteiro). A narração do agente ("li os arquivos") não distingue os dois.

### 3. Registrar no `REGISTRY`

`src/koine/adapters/__init__.py` mantém o registry de adapters ativos — ele é a fonte única: o despacho do CLI (`koine <cliente> ...`) e a emissão de wrappers `kn-<cliente>` no `instalar` iteram sobre ele:

```python
REGISTRY = {
    "claude":   claude,
    "agy":      antigravity,
    "codex":    codex,
    "copilot":  copilot,
    "opencode": opencode,
    "<novo>":   <novo>,   # ← adicionar
}
```

### 4. Lançamento do cliente

`src/koine/launch.py` resolve o binário do cliente no PATH e faz `execvpe`. Se o comando do cliente não for igual ao nome do adapter, adicionar o mapeamento lá.

### 5. Skills do harness (se aplicável)

Se o cliente suporta skills instaláveis, adicionar o destino em `skills.HARNESS_SKILLS` (`src/koine/skills.py`) para o `koine instalar` / `instalar-habilidades --para=<novo>` cobrirem o cliente.

### 6. Testes

- Unit test do adapter (`tests/test_adapter_<novo>.py`): construir `ContextoMontado` em memória, comparar `Lancamento` esperado vs obtido — campo a campo.
- Smoke test do wrapper: pasta temporária com `CONTEXTO.md` mínimo, monkeypatch de `koine.launch.lancar`, verificar filesystem + env vars.
- Bootstrap mode também precisa de teste.

### 7. Documentação

- README — adicionar linha na tabela "Clientes IA suportados".
- CHANGELOG — registrar adapter novo na próxima versão.
- ADR opcional se a decisão arquitetural for não-óbvia.

## Pontos de atenção

- **CONTEXTO.md é mutável e canônico** — agente IA edita esse arquivo entre sessões. O adapter NUNCA deve copiar `CONTEXTO.md` para outro lugar; aponta direto ou usa symlink.
- **Configurações globais do cliente IA** (`~/.copilot/`, `~/.config/opencode/`, `~/.gemini/`, etc.) NUNCA são tocadas pelo adapter; mas o wrapper avisa quando elas existem e podem afetar a sessão.
- **`os.symlink` no Windows** requer privilégio elevado — `cli._criar_symlink` degrada para cópia regenerada por sessão.
- **Marker `<!-- gerado por kn-agente -->`** na primeira linha de arquivos gerados — permite detecção de conflito sem manifesto (`src/koine/conflito.py`). O marcador é congelado; não mudar.

## Referências

- ADR [`20260625-harness-lancamento-struct.md`](../decisoes/20260625-harness-lancamento-struct.md) — contrato `Lancamento`.
- `src/koine/adapters/claude.py` — adapter mais simples, bom ponto de partida.
- `src/koine/adapters/copilot.py` — adapter mais complexo, boa referência para casos com bundle externo.
- `src/koine/cache.py` — slot determinístico baseado em hash da pasta.
- `src/koine/render.py` — concatenação de seções para bundle/inline.
