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

notify_starting() {
  if command -v zenity >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" ]]; then
    zenity --info --timeout=5 --title="Blade Arena" --text="Starting Blade Arena...

Look for a window titled \"Blade Arena\" on the desktop (1280x720).
It stays on top for a few seconds after load.

If nothing appears after ~15 seconds, open:
  /tmp/blade-arena-launch.log" --width=460 2>/dev/null &
  fi
}

focus_game_window() {
  (
    if ! command -v xdotool >/dev/null 2>&1; then
      return
    fi
    for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
      WIN=$(xdotool search --name "Blade Arena" 2>/dev/null | head -1 || true)
      if [[ -n "$WIN" ]]; then
        xdotool windowactivate --sync "$WIN" 2>/dev/null || true
        xdotool windowraise "$WIN" 2>/dev/null || true
        xdotool windowmove "$WIN" 60 50 2>/dev/null || true
        log "Focused game window id=$WIN"
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

if ! xdpyinfo >/dev/null 2>&1; then
  notify_error "Desktop display $DISPLAY is not ready. Wait 30s and run /workspace/scripts/check-desktop.sh"
  exit 1
fi

# Avoid duplicate instances stealing focus from a working game.
if pgrep -f "$BINARY" >/dev/null 2>&1; then
  log "Game already running — focusing existing window"
  focus_game_window
  exit 0
fi

notify_starting
focus_game_window
log "Starting blade_arena in background..."

nohup "$WORKSPACE/scripts/run-blade-arena-cpp.sh" >>"$LOG" 2>&1 &
GAME_PID=$!
log "blade_arena pid=$GAME_PID"

sleep 2
if ! kill -0 "$GAME_PID" 2>/dev/null; then
  notify_error "Game exited immediately. See log: $LOG"
  exit 1
fi

exit 0
