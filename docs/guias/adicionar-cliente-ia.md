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

Cada adapter é um módulo em `src/koine/adapters/<novo>.py` que expõe **duas**
operações:

- `renderizar(cm) -> Lancamento` — a entrega da sessão, pelo canal do cliente.
  **A pasta do usuário não recebe nada.**
- `renderizar_para_pasta(cm) -> (arquivo, conteúdo)` — a materialização a pedido
  (`koine gerar`), para ambientes sem wrapper, onde a pasta é a única via.

A dataclass `Lancamento` (`src/koine/lancamento.py`) descreve tudo que o wrapper deve materializar:

```python
@dataclass
class Lancamento:
    arquivos_working_dir: dict  # path relativo → conteúdo (str)
    arquivos_externos: dict     # path absoluto → conteúdo (cache)
    symlinks: dict              # path do symlink → alvo
    env_vars: dict              # env vars para o exec
    extra_args: list            # args extras para o cliente
```

No launch, `arquivos_working_dir` e `symlinks` ficam **vazios**: o que o adapter
preenche é `arquivos_externos` (o bundle, em `~/.cache/koine/`), `env_vars` e
`extra_args`. Os dois primeiros campos seguem no contrato porque a
materialização é genérica e o modo bootstrap ainda escreve o `CONTEXTO.md` — mas
isso é do **launch**, não do adapter.

## Passos

### 1. Investigação empírica antes de codar

Antes de qualquer código, descubra **por qual canal externo** o cliente aceita
receber contexto — e prove com o **protocolo do nonce**, nunca pela doc:

1. Ponha uma palavra de controle única num arquivo que só o canal alcança.
2. Rode o cliente **de uma pasta vazia**, com as ferramentas de leitura
   desligadas onde ele permitir.
3. Pergunte a palavra. Se ele responde, o canal entrega.
4. Rode o **controle negativo**: a mesma pergunta sem o canal. Sem esse passo,
   "o agente acertou" não distingue entrega de adivinhação.

`scripts/prova-viva-canais.sh` roteiriza os quatro passos. É manual e fora do
CI — faz chamada real de LLM, autenticada e paga.

**Com as ferramentas ligadas o teste vira falso positivo**: o agente lê o arquivo
apontado com a ferramenta e responde certo, e você conclui que o mecanismo
funciona quando ele não funciona. Foi assim que o `@path` externo do Claude
passou por bom durante meses — e a diferença só apareceu em sessão remota.

**Confira o artefato antes de interpretar a resposta.** Se o bundle não foi
regenerado, a leitura apressada vira "o render perde conteúdo".

### 2. Criar o módulo do adapter em `src/koine/adapters/<novo>.py`

Implementar:

```python
from koine.contexto import ContextoMontado
from koine.lancamento import Lancamento

ARQUIVO = "<ARQUIVO-DE-INSTRUCAO>"


def renderizar(cm: ContextoMontado) -> Lancamento:
    ...
```

Todo adapter monta um bundle em `~/.cache/koine/<cliente>-bundles/<slot>/` (use
`src/koine/cache.py` para o slot determinístico) e o entrega pelo canal do
cliente. O que varia é **como o canal aponta para ele**:

- **Diretório adicionado ao workspace** — `--add-dir <bundle>`, estilo
  Claude/Antigravity. Conteúdo **embutido** no arquivo do bundle, via
  `render.documento_inline`. Referência: `src/koine/adapters/claude.py`.
- **Chave de config apontando um arquivo** — `-c model_instructions_file=`,
  estilo Codex. O valor varia por pasta, então vai em `Lancamento.extra_args`,
  **nunca** em `EXTRA_ARGS`, que é constante de módulo. Referência:
  `src/koine/adapters/codex.py`.
- **Env var apontando um diretório de instruções** — estilo Copilot. Atenção ao
  que o canal de fato lê: o `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` entrega os
  `*.instructions.md` e **ignora** o `AGENTS.md` do mesmo diretório. Referência:
  `src/koine/adapters/copilot.py`.
- **Config com lista de caminhos absolutos** — estilo OpenCode. Aqui o conteúdo
  não é copiado: o cliente abre os arquivos, e o `CONTEXTO.md` chega **vivo** em
  vez de como snapshot. Referência: `src/koine/adapters/opencode.py`.

> **Não existe mais o estilo "ponteiro `@path`".** Import de caminho absoluto
> para fora da pasta não expande em pasta não aprovada, e a aprovação é um
> booleano por pasta que só o diálogo interativo escreve — pasta nova aberta
> remotamente nunca é aprovada. Onde o conteúdo é embutido, a prosa de sessão
> (`render.prosa_sessao`) avisa que o `CONTEXTO.md` acima é snapshot e que a
> fonte canônica é o arquivo.

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

- **CONTEXTO.md é mutável e canônico** — o agente edita esse arquivo entre sessões. Onde o canal aceita caminho (opencode), aponte para ele; onde só aceita conteúdo, o snapshot vai junto **com** a prosa que diz que a fonte é o arquivo da pasta. O adapter nunca escreve no `CONTEXTO.md`.
- **Configurações globais do cliente IA** (`~/.copilot/`, `~/.config/opencode/`, `~/.gemini/`, etc.) NUNCA são tocadas pelo adapter; mas o wrapper avisa quando elas existem e podem afetar a sessão.
- **`os.symlink` no Windows** requer privilégio elevado — `cli._criar_symlink` degrada para cópia regenerada por sessão.
- **Marker `<!-- gerado por kn-agente -->`** na primeira linha de arquivos gerados — permite detecção de conflito sem manifesto (`src/koine/escrita.py`). O marcador é **congelado**; não mudar. A segunda linha, `<!-- gerado a pedido -->`, distingue intenção de propriedade: o que o `gerar` materializou não é removido pela limpeza de estoque.
- **Nomeie o arquivo de pasta em `ARQUIVO`** — `estoque.NOMES` deriva do `REGISTRY`, então o adapter novo entra sozinho na limpeza. Se o cliente materializa um nome que outro já usa (três disputam `AGENTS.md`), teste os dois sentidos do cruzamento.

## Referências

- ADR [`20260625-harness-lancamento-struct.md`](../decisoes/20260625-harness-lancamento-struct.md) — contrato `Lancamento`.
- `src/koine/adapters/claude.py` — adapter mais simples, bom ponto de partida.
- `src/koine/adapters/copilot.py` — adapter mais complexo, boa referência para casos com bundle externo.
- `src/koine/cache.py` — slot determinístico baseado em hash da pasta.
- `src/koine/render.py` — concatenação de seções para bundle/inline.
