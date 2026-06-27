#!/usr/bin/env bash
# install.sh — instala kn-agente em ~/.local/bin/ a partir do GitHub Release.
# Documentação: https://github.com/jrunic/koine

set -euo pipefail

REPO="jrunic/koine"
DEST_DIR="$HOME/.local/bin"
DEST="$DEST_DIR/kn-agente"

# Detecta OS
case "$(uname -s)" in
    Darwin) OS="darwin" ;;
    Linux)  OS="linux"  ;;
    *)
        echo "Erro: sistema operacional não suportado: $(uname -s)" >&2
        echo "Suportados: macOS (Darwin), Linux." >&2
        exit 1
        ;;
esac

# Detecta arquitetura
case "$(uname -m)" in
    arm64|aarch64) ARCH="arm64" ;;
    x86_64|amd64)  ARCH="amd64" ;;
    *)
        echo "Erro: arquitetura não suportada: $(uname -m)" >&2
        echo "Suportadas: arm64 (Apple Silicon), amd64 (Intel/AMD)." >&2
        exit 1
        ;;
esac

# Linux só amd64 nesta versão
if [ "$OS" = "linux" ] && [ "$ARCH" = "arm64" ]; then
    echo "Erro: linux-arm64 ainda não suportado." >&2
    echo "Use linux-amd64 ou aguarde versão futura." >&2
    exit 1
fi

ASSET="kn-agente-${OS}-${ARCH}"
URL="https://github.com/${REPO}/releases/latest/download/${ASSET}"

echo "Baixando ${ASSET}..."
mkdir -p "$DEST_DIR"

# Download com retry (3 tentativas)
if ! curl -fsSL --retry 3 -o "$DEST" "$URL"; then
    echo "Erro: falha ao baixar ${URL}" >&2
    echo "Verifique sua conexão ou tente novamente." >&2
    exit 1
fi

chmod +x "$DEST"

# Verifica PATH
PATH_OK=0
case ":$PATH:" in
    *":$DEST_DIR:"*) PATH_OK=1 ;;
esac

# Valida instalação
VERSION_OUTPUT="$("$DEST" --versao 2>&1 || true)"
echo "✓ Instalado em $DEST"
echo "  $VERSION_OUTPUT"
echo

if [ "$PATH_OK" = "1" ]; then
    echo "Próximo passo: rode 'kn-agente instalar'"
else
    # Detecta shell para sugerir o arquivo certo
    SHELL_NAME="$(basename "${SHELL:-bash}")"
    case "$SHELL_NAME" in
        zsh)  PROFILE_FILE="~/.zshrc"  ;;
        bash) PROFILE_FILE="~/.bashrc" ;;
        fish) PROFILE_FILE="(use: set -U fish_user_paths $DEST_DIR \$fish_user_paths)" ;;
        *)    PROFILE_FILE="seu shell profile" ;;
    esac

    echo "⚠️  $DEST_DIR não está no seu PATH."
    echo
    echo "  Adicione esta linha ao $PROFILE_FILE:"
    echo
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
    echo "  Depois reabra o terminal e rode: kn-agente instalar"
fi
