#!/usr/bin/env bash
# Monta koine-skills.zip: descompactar em ~/koine.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$REPO/dist/koine-skills.zip}"
# Resolve OUT para absoluto: o zip roda após um `cd` para o staging,
# então um OUT relativo apontaria para um dir inexistente lá (zip exit 15).
mkdir -p "$(dirname "$OUT")"
OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
STAGE="$(mktemp -d)/koine"
mkdir -p "$STAGE/.koine-bootstrap"

# payload do vault (fonte para o instalador copiar para XDG)
cp "$REPO/vault/KOINE.md"                    "$STAGE/.koine-bootstrap/KOINE.md"
cp -R "$REPO/vault/agentes"                  "$STAGE/.koine-bootstrap/agentes"
cp -R "$REPO/vault/conceitos"                "$STAGE/.koine-bootstrap/conceitos"
cp -R "$REPO/vault/dominios"                 "$STAGE/.koine-bootstrap/dominios"
mkdir -p "$STAGE/.koine-bootstrap/habilidades"
cp -R "$REPO/vault/habilidades/kn-"*         "$STAGE/.koine-bootstrap/habilidades/"

# arquivos na raiz de ~/koine
cp "$REPO/scripts/skills-mode/bootstrap/CLAUDE.md"        "$STAGE/CLAUDE.md"
cp "$REPO/scripts/skills-mode/bootstrap/CONTEXTO.md"      "$STAGE/CONTEXTO.md"
cp "$REPO/scripts/skills-mode/instalar-koine.bat"         "$STAGE/instalar-koine.bat"
cp "$REPO/scripts/skills-mode/instalar-koine.md"          "$STAGE/instalar-koine.md"

mkdir -p "$(dirname "$OUT")"
( cd "$(dirname "$STAGE")" && zip -r -X "$OUT" koine >/dev/null )
echo "zip gerado: $OUT"
unzip -l "$OUT" | grep -E "kn-1|CLAUDE|instalar|KOINE" || true
