#!/usr/bin/env bash
# Install VM Desktop shortcuts for this project.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
DESKTOP_DIR="${DESKTOP_DIR:-$HOME/Desktop}"

mkdir -p "$DESKTOP_DIR"

install_desktop() {
  local src="$1"
  local name
  name="$(basename "$src")"
  cp "$src" "$DESKTOP_DIR/$name"
  chmod +x "$DESKTOP_DIR/$name"
  echo "Installed $DESKTOP_DIR/$name"
}

install_desktop "$WORKSPACE/scripts/desktop/Play-Blade-Arena.desktop"
cp "$WORKSPACE/scripts/desktop/START-BLADE-ARENA.sh" "$DESKTOP_DIR/START-BLADE-ARENA.sh"
chmod +x "$DESKTOP_DIR/START-BLADE-ARENA.sh"
echo "Installed $DESKTOP_DIR/START-BLADE-ARENA.sh"

if [[ -f "$WORKSPACE/scripts/desktop/Preview-Human-Figure.desktop" ]]; then
  install_desktop "$WORKSPACE/scripts/desktop/Preview-Human-Figure.desktop"
fi

# Pre-build so first launch is faster.
if [[ -x "$WORKSPACE/scripts/run-blade-arena-cpp.sh" ]]; then
  echo "Pre-building game (may take a minute on first run)..."
  DISPLAY="${DISPLAY:-:1}" WORKSPACE="$WORKSPACE" \
    "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >/tmp/blade-arena-prebuild.log 2>&1 || true
fi

cat <<EOF

Desktop shortcuts installed.

HOW TO PLAY:
  1. Open the Desktop pane in Cursor (DISPLAY must be :1).
  2. Double-click START-BLADE-ARENA.sh  (most reliable)
     OR double-click Play Blade Arena.

If nothing happens, open a terminal on Desktop and run:
  /workspace/scripts/run-blade-arena-desktop.sh

Errors are logged to: /tmp/blade-arena-launch.log
EOF
