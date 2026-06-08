#!/usr/bin/env bash
# Install VM Desktop shortcuts for this project.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
DESKTOP_DIR="${DESKTOP_DIR:-$HOME/Desktop}"

mkdir -p "$DESKTOP_DIR"

install_one() {
  local src="$1"
  local name
  name="$(basename "$src")"
  cp "$src" "$DESKTOP_DIR/$name"
  chmod +x "$DESKTOP_DIR/$name"
  echo "Installed $DESKTOP_DIR/$name"
}

install_one "$WORKSPACE/scripts/desktop/Play-Blade-Arena.desktop"

if [[ -f "$WORKSPACE/scripts/desktop/Preview-Human-Figure.desktop" ]]; then
  install_one "$WORKSPACE/scripts/desktop/Preview-Human-Figure.desktop"
elif [[ -f "$HOME/Desktop/Preview-Human-Figure.desktop" ]]; then
  echo "Preview shortcut already on Desktop"
fi

# Pre-build so first double-click is faster (best effort).
if [[ -x "$WORKSPACE/scripts/run-blade-arena-cpp.sh" ]]; then
  "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >/tmp/blade-arena-prebuild.log 2>&1 || true
fi

echo "Done. Double-click 'Play Blade Arena' on the Desktop."
