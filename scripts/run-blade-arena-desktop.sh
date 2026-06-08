#!/usr/bin/env bash
# Desktop-friendly launcher for Blade Arena (C++). Shows dialogs on build errors.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
DISPLAY="${DISPLAY:-:1}"
LOG="/tmp/blade-arena-launch.log"
export DISPLAY
export WORKSPACE

log() {
  echo "[$(date '+%H:%M:%S')] $*" >>"$LOG"
}

notify_error() {
  local msg="$1"
  log "ERROR: $msg"
  if command -v zenity >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" ]]; then
    zenity --error --title="Blade Arena" --text="${msg}

Log: ${LOG}" --width=480 2>/dev/null || true
  fi
  echo "ERROR: $msg" >&2
  echo "See $LOG" >&2
}

focus_game_window() {
  (
    sleep 2
    if ! command -v xdotool >/dev/null 2>&1; then
      return
    fi
    for _ in 1 2 3 4 5; do
      WIN=$(xdotool search --name "Blade Arena" 2>/dev/null | head -1 || true)
      if [[ -n "$WIN" ]]; then
        xdotool windowactivate --sync "$WIN" 2>/dev/null || true
        xdotool windowraise "$WIN" 2>/dev/null || true
        xdotool windowmove "$WIN" 80 60 2>/dev/null || true
        break
      fi
      sleep 1
    done
  ) &
}

log "Launcher started (DISPLAY=$DISPLAY)"

if [[ ! -d "$WORKSPACE/cpp/BladeArena" ]]; then
  notify_error "Blade Arena not found in $WORKSPACE. Use branch cursor/blade-arena-cpp-5aaf."
  exit 1
fi

if ! command -v g++ >/dev/null 2>&1 || ! command -v cmake >/dev/null 2>&1; then
  notify_error "Missing g++ or cmake. Install build-essential and cmake."
  exit 1
fi

BINARY="$WORKSPACE/cpp/BladeArena/build/blade_arena"
if [[ ! -x "$BINARY" ]]; then
  log "Building game..."
  if ! "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >>"$LOG" 2>&1; then
    notify_error "Build failed. Open the log file for details."
    exit 1
  fi
fi

if [[ ! -x "$BINARY" ]]; then
  notify_error "Game binary missing after build."
  exit 1
fi

if [[ -z "${DISPLAY:-}" ]]; then
  notify_error "No DISPLAY set. Open the Desktop pane first, then try again."
  exit 1
fi

focus_game_window
log "Starting blade_arena..."
exec "$WORKSPACE/scripts/run-blade-arena-cpp.sh" >>"$LOG" 2>&1
