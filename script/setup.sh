#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_SCRIPT="$SCRIPT_DIR/log"
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

# install log command
mkdir -p "$INSTALL_DIR"
ln -sf "$LOG_SCRIPT" "$INSTALL_DIR/log"
echo "installed: $INSTALL_DIR/log -> $LOG_SCRIPT"

# warn if ~/.local/bin isn't on PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "note: $INSTALL_DIR is not in your PATH."
    echo "add this to your shell config (~/.bashrc, ~/.zshrc, etc.):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "start the viewer:   log"
echo "add something:      log \"your text here\""
echo "add a link:         log --link https://example.com"
echo "add a file:         log --file path/to/image.png"
