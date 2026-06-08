#!/usr/bin/env bash
# Install VM Desktop shortcuts for Blade Arena and configure XFCE to run them.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
DESKTOP_DIR="${DESKTOP_DIR:-$HOME/Desktop}"
export DISPLAY="${DISPLAY:-:1}"

mkdir -p "$DESKTOP_DIR"

trust_desktop() {
  local path="$1"
  chmod +x "$path"
  if command -v gio >/dev/null 2>&1; then
    gio set "$path" metadata::trusted true 2>/dev/null || true
  fi
}

install_desktop() {
  local src="$1"
  local name
  name="$(basename "$src")"
  cp "$src" "$DESKTOP_DIR/$name"
  trust_desktop "$DESKTOP_DIR/$name"
  echo "Installed $DESKTOP_DIR/$name"
}

# Let double-click on .sh files run them instead of opening in an editor.
if command -v xfconf-query >/dev/null 2>&1; then
  xfconf-query -c thunar -p /misc-exec-shell-scripts-by-default -n -t bool -s true 2>/dev/null || \
    xfconf-query -c thunar -p /misc-exec-shell-scripts-by-default -s true 2>/dev/null || true
fi

install_desktop "$WORKSPACE/scripts/desktop/Blade-Arena.desktop"
install_desktop "$WORKSPACE/scripts/desktop/Play-Blade-Arena.desktop"

cp "$WORKSPACE/scripts/desktop/START-BLADE-ARENA.sh" "$DESKTOP_DIR/START-BLADE-ARENA.sh"
trust_desktop "$DESKTOP_DIR/START-BLADE-ARENA.sh"

cp "$WORKSPACE/PLAY-BLADE-ARENA.sh" "$DESKTOP_DIR/PLAY-BLADE-ARENA.sh"
trust_desktop "$DESKTOP_DIR/PLAY-BLADE-ARENA.sh"

cat >"$DESKTOP_DIR/DOUBLE-CLICK-TO-PLAY.sh" <<'LAUNCHER'
#!/usr/bin/env bash
export DISPLAY="${DISPLAY:-:1}"
export WORKSPACE="${WORKSPACE:-/workspace}"
exec /workspace/scripts/run-blade-arena-desktop.sh
LAUNCHER
trust_desktop "$DESKTOP_DIR/DOUBLE-CLICK-TO-PLAY.sh"

if [[ -f "$WORKSPACE/scripts/desktop/Preview-Human-Figure.desktop" ]]; then
  install_desktop "$WORKSPACE/scripts/desktop/Preview-Human-Figure.desktop"
fi

chmod +x "$WORKSPACE/PLAY-BLADE-ARENA.sh" "$WORKSPACE/scripts/run-blade-arena-desktop.sh" \
  "$WORKSPACE/scripts/run-blade-arena-cpp.sh"

echo "Pre-building game (first launch is faster)..."
DISPLAY=:1 WORKSPACE="$WORKSPACE" \
  "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >/tmp/blade-arena-prebuild.log 2>&1 || true

if [[ -x "$WORKSPACE/cpp/BladeArena/build/blade_arena" ]]; then
  echo "[OK] Game binary ready"
else
  echo "[WARN] Build may have failed — see /tmp/blade-arena-prebuild.log"
fi

cat <<EOF

=== Blade Arena — Desktop ready ===

On the Desktop, double-click ANY of these:
  • Blade Arena          (icon, recommended)
  • PLAY-BLADE-ARENA.sh
  • DOUBLE-CLICK-TO-PLAY.sh
  • START-BLADE-ARENA.sh

From a terminal on Desktop:
  /workspace/PLAY-BLADE-ARENA.sh

A window titled "Blade Arena" (1280x720) should appear within ~15 seconds.
Errors: /tmp/blade-arena-launch.log

If the Desktop pane is blank, open https://cursor.com/agents and use the Desktop tab there.
EOF
