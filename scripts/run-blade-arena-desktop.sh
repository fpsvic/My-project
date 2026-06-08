#!/usr/bin/env bash
# Desktop-friendly launcher for Blade Arena (C++). Shows dialogs on build errors.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
export DISPLAY="${DISPLAY:-:1}"
export WORKSPACE
LOG="/tmp/blade-arena-launch.log"
BUILD_DIR="$WORKSPACE/cpp/BladeArena/build"
BINARY="$BUILD_DIR/blade_arena"
MODEL_WALK="$WORKSPACE/Assets/Models/HumanFigure_walk.glb"
MODEL_GAME="$WORKSPACE/Assets/Models/HumanFigure_game.glb"
MODEL_FULL="$WORKSPACE/Assets/Models/HumanFigure.glb"

log() {
  echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"
}

notify_error() {
  local msg="$1"
  log "ERROR: $msg"
  if command -v zenity >/dev/null 2>&1; then
    zenity --error --title="Blade Arena" --text="${msg}

Log: ${LOG}" --width=520 2>/dev/null || true
  fi
  if command -v xfce4-terminal >/dev/null 2>&1; then
    xfce4-terminal --title="Blade Arena — launch error" --hold -e "bash -lc 'echo \"$msg\"; echo; tail -40 \"$LOG\"; echo; read -p \"Press Enter to close...\" _'" \
      >/dev/null 2>&1 &
  fi
}

notify_starting() {
  if command -v zenity >/dev/null 2>&1; then
    zenity --info --timeout=6 --title="Blade Arena" --text="Starting Blade Arena on the desktop...

A window titled \"Blade Arena\" (1280×720) will appear while the model loads (~10–20 seconds).

If nothing shows, double-click \"Blade Arena (Terminal)\" on the desktop." \
      --width=480 2>/dev/null &
  fi
}

focus_game_window() {
  if ! command -v xdotool >/dev/null 2>&1; then
    return 1
  fi
  local win=""
  for _ in $(seq 1 30); do
    win=$(xdotool search --name "Blade Arena" 2>/dev/null | head -1 || true)
    if [[ -n "$win" ]]; then
      xdotool windowactivate --sync "$win" 2>/dev/null || true
      xdotool windowraise "$win" 2>/dev/null || true
      xdotool windowmove "$win" 80 60 2>/dev/null || true
      log "Focused game window id=$win"
      return 0
    fi
    sleep 1
  done
  return 1
}

resolve_model() {
  if [[ -f "$MODEL_WALK" ]]; then
    echo "$MODEL_WALK"
  elif [[ -f "$MODEL_GAME" ]]; then
    echo "$MODEL_GAME"
  elif [[ -f "$MODEL_FULL" ]]; then
    echo "$MODEL_FULL"
  fi
}

log "=== Launcher started (DISPLAY=$DISPLAY) ==="

if [[ ! -d "$WORKSPACE/cpp/BladeArena" ]]; then
  notify_error "Blade Arena not found. Use branch cursor/blade-arena-cpp-5aaf."
  exit 1
fi

if ! xdpyinfo >/dev/null 2>&1; then
  notify_error "Desktop display $DISPLAY is not ready.

Run: /workspace/scripts/fix-desktop.sh
Then reload Cursor (Ctrl+Shift+P → Developer: Reload Window) and open the Desktop tab."
  exit 1
fi

if [[ ! -x "$BINARY" ]]; then
  log "Building game (first run)..."
  if ! "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >>"$LOG" 2>&1; then
    notify_error "Build failed. See log: $LOG"
    exit 1
  fi
fi

if [[ ! -x "$BINARY" ]]; then
  notify_error "Game binary missing: $BINARY"
  exit 1
fi

if pgrep -f "$BINARY" >/dev/null 2>&1; then
  log "Game already running — focusing window"
  focus_game_window || notify_error "Game is running but window not found. Try Alt+Tab or check /tmp/blade-arena-launch.log"
  exit 0
fi

MODEL_ARG="$(resolve_model)"
notify_starting

cd "$BUILD_DIR"
if [[ -n "$MODEL_ARG" ]]; then
  log "Launching: $BINARY $MODEL_ARG"
  nohup "$BINARY" "$MODEL_ARG" >>"$LOG" 2>&1 &
else
  log "Launching: $BINARY (no model — placeholder capsule)"
  nohup "$BINARY" >>"$LOG" 2>&1 &
fi
GAME_PID=$!
log "blade_arena pid=$GAME_PID"

# Wait until process is alive through initial load (model + Lua can take ~15s).
for _ in $(seq 1 25); do
  if ! kill -0 "$GAME_PID" 2>/dev/null; then
    notify_error "Game exited during startup. See log: $LOG"
    exit 1
  fi
  if focus_game_window; then
    log "=== Launch OK ==="
    exit 0
  fi
  sleep 1
done

if kill -0 "$GAME_PID" 2>/dev/null; then
  log "Game running (pid=$GAME_PID) but window not focused yet — check Alt+Tab"
  if command -v zenity >/dev/null 2>&1; then
    zenity --info --timeout=8 --title="Blade Arena" \
      --text="Game is running (pid $GAME_PID) but may be behind other windows.\n\nUse Alt+Tab or look for \"Blade Arena\"." 2>/dev/null &
  fi
  exit 0
fi

notify_error "Game stopped unexpectedly. See log: $LOG"
exit 1
