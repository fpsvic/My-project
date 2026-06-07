#!/usr/bin/env bash
# Launch a desktop preview of the Human Figure model (no Unity license required).
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
DISPLAY="${DISPLAY:-:1}"
PORT="${PREVIEW_PORT:-8765}"
MODE="${1:-browser}"

export DISPLAY

stop_existing_server() {
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${PORT}/tcp" 2>/dev/null || true
  fi
}

start_server() {
  stop_existing_server
  cd "$WORKSPACE"
  python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/preview-desktop-server.log 2>&1 &
  echo $! >/tmp/preview-desktop-server.pid
  sleep 0.5
}

open_browser() {
  local url="http://127.0.0.1:${PORT}/Preview/index.html"
  echo "Opening browser preview: $url"
  if command -v google-chrome >/dev/null 2>&1; then
    google-chrome --no-sandbox --new-window "$url" >/dev/null 2>&1 &
  elif command -v firefox >/dev/null 2>&1; then
    firefox --new-window "$url" >/dev/null 2>&1 &
  else
    echo "No Chrome/Firefox found. Open manually: $url"
    exit 1
  fi
}

open_blender() {
  local model="$WORKSPACE/Assets/Models/HumanFigure.glb"
  if ! command -v blender >/dev/null 2>&1; then
    echo "Blender is not installed."
    exit 1
  fi
  echo "Opening Blender preview: $model"
  blender --window-geometry 80 40 1400 900 "$model" >/dev/null 2>&1 &
}

open_unity() {
  local unity="$HOME/Unity/Hub/Editor/6000.4.8f1/Unity"
  if [[ ! -x "$unity" ]]; then
    echo "Unity Editor not found at $unity"
    exit 1
  fi
  echo "Opening Unity Editor (requires activated license)…"
  dbus-launch --exit-with-session "$unity" -projectPath "$WORKSPACE" >/tmp/preview-unity.log 2>&1 &
}

case "$MODE" in
  browser|"")
    start_server
    open_browser
    echo "Preview server PID: $(cat /tmp/preview-desktop-server.pid)"
    ;;
  blender)
    open_blender
    ;;
  unity)
    open_unity
    ;;
  *)
    echo "Usage: $0 [browser|blender|unity]"
    exit 1
    ;;
esac
