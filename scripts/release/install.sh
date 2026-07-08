#!/usr/bin/env bash
# install.sh — instala o Koine (aplicação Python) a partir do GitHub Release.
# Baixa koine-<versao>.zip (koine.pyz + vault/), extrai para o diretório de
# dados do Koine e delega ao `koine instalar`.
# Overrides: KOINE_VERSAO=v0.4.0 (pina a tag)  KOINE_BASE_URL=<url> (espelho)
# Documentação: https://github.com/jrunic/koine

set -euo pipefail

REPO="jrunic/koine"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/koine"
DEST="$DATA_DIR/dist"
BIN_DIR="$HOME/.local/bin"

# 1. Localiza um Python >= 3.12
PY=""
for cand in python3.13 python3.12 python3 python; do
    if command -v "$cand" >/dev/null 2>&1 \
        && "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)' >/dev/null 2>&1; then
        PY="$(command -v "$cand")"
        break
    fi
done

if [ -z "$PY" ]; then
    echo "Erro: nenhum Python >= 3.12 encontrado no PATH." >&2
    echo >&2
    echo "O Koine é uma aplicação Python. Como instalar o Python:" >&2
    case "$(uname -s)" in
        Darwin) echo "  brew install python    (ou baixe de https://www.python.org/downloads/)" >&2 ;;
        Linux)  echo "  via gerenciador do sistema (apt install python3, dnf install python3, pacman -S python)" >&2 ;;
        *)      echo "  baixe de https://www.python.org/downloads/" >&2 ;;
    esac
    echo >&2
    echo "Depois rode este script novamente. Nada foi instalado." >&2
    exit 1
fi

# 2. Resolve a tag a instalar (default: última release)
TAG="${KOINE_VERSAO:-}"
if [ -z "$TAG" ]; then
    # || true: sob `set -euo pipefail`, uma falha do curl (sem rede, DNS,
    # proxy) mataria o script MUDO aqui; com ele, TAG fica vazia/"latest" e
    # cai no bloco de erro orientativo abaixo. -S: mostra o erro do curl
    # mesmo em modo silencioso.
    TAG="$(curl -fsSLSI -o /dev/null -w '%{url_effective}' "https://github.com/${REPO}/releases/latest" || true)"
    TAG="${TAG##*/}"
fi
if [ -z "$TAG" ] || [ "$TAG" = "latest" ]; then
    echo "Erro: não foi possível resolver a última versão do Koine." >&2
    echo "Verifique sua conexão ou informe a versão: KOINE_VERSAO=v0.4.0 $0" >&2
    exit 1
fi
VERSAO="${TAG#v}"
ASSET="koine-${VERSAO}.zip"
BASE_URL="${KOINE_BASE_URL:-https://github.com/${REPO}/releases/download}"
URL="${BASE_URL}/${TAG}/${ASSET}"

# 3. Baixa para tmp — nada é tocado se o download falhar
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "Baixando ${ASSET}..."
if ! curl -fsSLS --retry 3 -o "${TMP}/${ASSET}" "$URL"; then
    echo "Erro: falha ao baixar ${URL}" >&2
    echo "Verifique sua conexão ou tente novamente. Nada foi instalado." >&2
    exit 1
fi

# 4. Extrai para o local canônico do pacote
rm -rf "$DEST"
mkdir -p "$DEST"
"$PY" -m zipfile -e "${TMP}/${ASSET}" "$DEST"

PYZ="$DEST/koine.pyz"
echo "✓ Pacote extraído em $DEST"
echo "  $("$PY" "$PYZ" versao)"
echo

# 5. Delegar ao instalador do produto (vault → XDG, wrappers com interpretador
#    absoluto, pasta canônica, skills com prompt quando interativo)
"$PY" "$PYZ" instalar

# 6. PATH
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *)
        SHELL_NAME="$(basename "${SHELL:-bash}")"
        case "$SHELL_NAME" in
            zsh)  PROFILE_FILE="~/.zshrc"  ;;
            bash) PROFILE_FILE="~/.bashrc" ;;
            fish) PROFILE_FILE="(use: set -U fish_user_paths $BIN_DIR \$fish_user_paths)" ;;
            *)    PROFILE_FILE="seu shell profile" ;;
        esac
        echo
        echo "⚠️  $BIN_DIR não está no seu PATH."
        echo
        echo "  Adicione esta linha ao $PROFILE_FILE:"
        echo
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo
        echo "  Depois reabra o terminal."
        ;;
esac
