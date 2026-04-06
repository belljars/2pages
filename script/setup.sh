#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
APP_SCRIPT="$SCRIPT_DIR/2p"
INSTALL_DIR="$HOME/.local/bin"

# init database
echo "initializing 2pages database..."
python3 - "$ROOT_DIR" <<'EOF'
import sys
sys.path.insert(0, sys.argv[1] + '/src/app')
from db import init_db
init_db()
EOF
echo "database ready."

# install 2p command
mkdir -p "$INSTALL_DIR"
ln -sf "$APP_SCRIPT" "$INSTALL_DIR/2p"
echo "installed: $INSTALL_DIR/2p -> $APP_SCRIPT"

# warn if ~/.local/bin isn't on PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "note: $INSTALL_DIR is not in your PATH."
    echo "add this to your shell config (~/.bashrc, ~/.zshrc, etc.):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "start the viewer:   2p"
echo "add something:      2p \"your text here\""
echo "add a link:         2p --link https://example.com"
echo "add a file:         2p --file path/to/image.png"
echo "move the journal:   2p --db ~/journals/archive.db"
