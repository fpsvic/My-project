#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

APP_DIR="$(pwd)"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/blood-quest.desktop"

mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Blood Quest
Comment=Gothic Java platformer
Exec=$APP_DIR/run-desktop.sh
Path=$APP_DIR
Terminal=false
Categories=Game;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"

echo "Installed desktop launcher:"
echo "$DESKTOP_FILE"
