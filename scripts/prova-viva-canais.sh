#!/usr/bin/env bash
# Protocolo do nonce, roteirizado — a camada de prova viva do critério 1 da #587.
#
# MANUAL, FORA DO CI: faz chamada real de LLM, autenticada e paga. Roda uma vez
# por cliente, quando o canal muda.
#
# O que ele prova, e a ordem importa:
#   1. monta um HOME isolado com um nonce POR CAMADA;
#   2. roda o launch com um shim, capturando env e args do cliente;
#   3. CONFERE os nonces dentro do artefato com grep — antes de perguntar
#      qualquer coisa ao cliente. Numa das medições de 27/08 o bundle não tinha
#      sido regenerado, e a leitura apressada seria "o render perde conteúdo";
#   4. pergunta ao cliente REAL, de dentro de uma pasta VAZIA e sem ferramentas
#      de leitura — com ferramentas o agente compensa lendo, e o teste vira
#      falso positivo;
#   5. roda o CONTROLE NEGATIVO: a mesma pergunta sem o canal. Sem ele, "o
#      agente acertou" não distingue entrega de adivinhação.
#
# uso: scripts/prova-viva-canais.sh <claude|agy|codex|copilot|opencode>
set -uo pipefail

CLIENTE="${1:-}"
case "$CLIENTE" in
  claude|agy|codex|copilot|opencode) ;;
  *) echo "uso: $0 <claude|agy|codex|copilot|opencode>" >&2; exit 2 ;;
esac

REPO="$(cd "$(dirname "$0")/.." && pwd)"
export REPO  # o heredoc python resolve o pacote de teste por ele
BASE="$(mktemp -d)"
PY="${PYTHON:-$REPO/.venv/bin/python}"
# A pergunta é por OBEDIÊNCIA, não por eco. Pedir ao agente que repita uma linha
# do próprio contexto esbarra em recusa — o opencode responde "não posso
# reproduzir instruções internas", que é indistinguível de "não recebi". A camada
# instrui o que responder; a pergunta cobra a instrução.
PERGUNTA='Quais codinomes de camada voce conhece? Liste todos, sem usar ferramenta. Se nao houver nenhum, responda NAO_SEI.'

echo "== 1. HOME isolado com nonce por camada  ($BASE)"
"$PY" - "$BASE" <<'PYEOF'
import os
import sys
sys.path.insert(0, os.environ["REPO"])
from tests.fixtures import seed
d = seed.montar(sys.argv[1])
alvos = ((os.path.join(d["cfg"], "teste.md"), "NONCE-USUARIO"),
         (os.path.join(d["data"], "agentes", "hermes.md"), "NONCE-AGENTE"),
         (os.path.join(d["trab"], "CONTEXTO.md"), "NONCE-CONTEXTO"))
for path, nonce in alvos:
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\nQuando o usuario perguntar os codinomes das camadas, "
                f"inclua na resposta: {nonce}.\n")
PYEOF
[ $? -eq 0 ] || { echo "FALHOU: montagem do HOME de teste"; exit 1; }

HOME_T="$BASE/home"
TRAB="$HOME_T/trabalho"

echo "== 2. launch com shim, capturando env e args"
mkdir -p "$BASE/shim" "$BASE/vazia"
printf '#!/bin/sh\nenv > "%s/env.txt"\nprintf "%%s\\n" "$@" > "%s/args.txt"\n' \
  "$BASE" "$BASE" > "$BASE/shim/$CLIENTE"
chmod +x "$BASE/shim/$CLIENTE"
env HOME="$HOME_T" PATH="$BASE/shim:/usr/bin:/bin" PYTHONPATH="$REPO/src" \
  "$PY" -m koine "$CLIENTE" hermes "$TRAB" || { echo "FALHOU: launch"; exit 1; }

echo "== 3. os nonces estão no artefato?  (antes de perguntar ao cliente)"
# Dois modos de entrega, os dois legítimos: o canal leva o CONTEÚDO (claude, agy,
# codex, copilot) ou leva CAMINHOS ABSOLUTOS que o cliente abre (opencode). No
# segundo, procurar o nonce dentro do bundle acha nada — é preciso resolver a
# referência, que é o que o cliente vai fazer.
REFS=$(grep -rhoE '"/[^"]+\.md"' "$HOME_T/.cache/koine" 2>/dev/null | tr -d '"')
FALTOU=0
for n in NONCE-USUARIO NONCE-AGENTE NONCE-CONTEXTO; do
  if grep -rq "$n" "$HOME_T/.cache/koine" 2>/dev/null; then
    echo "   ok   $n no bundle (conteúdo)"
  elif [ -n "$REFS" ] && echo "$REFS" | xargs grep -lq "$n" 2>/dev/null; then
    echo "   ok   $n num arquivo referenciado pelo canal"
  else
    echo "   FALTA $n — o artefato não tem a camada; pare aqui"; FALTOU=1
  fi
done
[ "$FALTOU" -eq 0 ] || exit 1

echo "== 4. o CLIENTE recebe?  (pasta vazia, sem ferramentas)"
ARGS=()
while IFS= read -r linha; do [ -n "$linha" ] && ARGS+=("$linha"); done < "$BASE/args.txt"
ENVS=()
while IFS= read -r linha; do
  case "$linha" in
    CLAUDE_CODE_ADDITIONAL*|COPILOT_CUSTOM*|OPENCODE_*) ENVS+=("$linha") ;;
  esac
done < "$BASE/env.txt"
echo "   env:  ${ENVS[*]:-(nenhuma)}"
echo "   args: ${ARGS[*]:-(nenhum)}"

cd "$BASE/vazia" || exit 1
case "$CLIENTE" in
  claude)   RESP=$(env "${ENVS[@]}" claude -p "$PERGUNTA" "${ARGS[@]}" --tools "" </dev/null 2>&1) ;;
  agy)      RESP=$(env "${ENVS[@]:-PATH=$PATH}" agy -p "$PERGUNTA" "${ARGS[@]}" </dev/null 2>&1) ;;
  # --skip-git-repo-check: a pasta vazia da prova não é repo, e sem a flag o
  # codex recusa antes de abrir a sessão. </dev/null: sem isso ele fica lendo stdin.
  codex)    RESP=$(env "${ENVS[@]:-PATH=$PATH}" codex exec --skip-git-repo-check "${ARGS[@]}" "$PERGUNTA" </dev/null 2>&1) ;;
  copilot)  RESP=$(env "${ENVS[@]}" copilot -p "$PERGUNTA" </dev/null 2>&1) ;;
  opencode) RESP=$(env "${ENVS[@]}" opencode run "$PERGUNTA" </dev/null 2>&1) ;;
esac
echo "   resposta: $(echo "$RESP" | grep -o 'NONCE-[A-Z]*' | sort -u | tr '\n' ' ')"
echo "$RESP" | tail -3

echo "== 5. controle negativo: a mesma pergunta SEM o canal"
case "$CLIENTE" in
  claude)   NEG=$(claude -p "$PERGUNTA" --tools "" </dev/null 2>&1) ;;
  agy)      NEG=$(agy -p "$PERGUNTA" </dev/null 2>&1) ;;
  codex)    NEG=$(codex exec --skip-git-repo-check "$PERGUNTA" </dev/null 2>&1) ;;
  copilot)  NEG=$(copilot -p "$PERGUNTA" </dev/null 2>&1) ;;
  opencode) NEG=$(opencode run "$PERGUNTA" </dev/null 2>&1) ;;
esac
echo "   sem o canal: $(echo "$NEG" | grep -o 'NONCE-[A-Z]*' | sort -u | tr '\n' ' ')${NEG:+}"
echo "$NEG" | tail -2

echo
echo "VEREDITO: o canal entrega se o passo 4 trouxe os nonces e o 5 NÃO trouxe."
echo "material em $BASE"
