#!/usr/bin/env bash
# Desktop-friendly launcher for Blade Arena (C++). Shows dialogs on build errors.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
DISPLAY="${DISPLAY:-:1}"
LOG="/tmp/blade-arena-launch.log"
export DISPLAY

notify() {
  if command -v zenity >/dev/null 2>&1; then
    zenity --info --title="Blade Arena" --text="$1" --width=420 2>/dev/null || true
  else
    echo "$1"
  fi
}

notify_error() {
  if command -v zenity >/dev/null 2>&1; then
    zenity --error --title="Blade Arena" --text="$1\n\nDetails: $LOG" --width=480 2>/dev/null || true
  else
    echo "ERROR: $1" >&2
    echo "See $LOG" >&2
  fi
}

if [[ ! -d "$WORKSPACE/cpp/BladeArena" ]]; then
  notify_error "Blade Arena is not in this workspace.\nCheckout branch cursor/blade-arena-cpp-5aaf and pull latest."
  exit 1
fi

if ! command -v g++ >/dev/null 2>&1 || ! command -v cmake >/dev/null 2>&1; then
  notify_error "Missing build tools (g++ / cmake).\nAsk the agent to install build-essential and cmake."
  exit 1
fi

BINARY="$WORKSPACE/cpp/BladeArena/build/blade_arena"
if [[ ! -x "$BINARY" ]]; then
  if command -v zenity >/dev/null 2>&1; then
    (
      echo "5"; echo "# Building Blade Arena (first launch)..."
      sleep 0.5
      if ! "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >>"$LOG" 2>&1; then
        echo "100"
        exit 1
      fi
      echo "100"; echo "# Ready"
    ) | zenity --progress --title="Blade Arena" --text="First launch builds the game..." --percentage=0 --auto-close 2>/dev/null || {
      notify "Building Blade Arena (first launch). This can take a few minutes..."
      "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >>"$LOG" 2>&1 || {
        notify_error "Build failed."
        exit 1
      }
    }
  else
    notify "Building Blade Arena..."
    "$WORKSPACE/scripts/run-blade-arena-cpp.sh" --build-only >>"$LOG" 2>&1 || {
      notify_error "Build failed."
      exit 1
    }
  fi
fi

if [[ ! -x "$BINARY" ]]; then
  notify_error "Game binary not found after build."
  exit 1
fi

: >"$LOG"
if ! "$WORKSPACE/scripts/run-blade-arena-cpp.sh" >>"$LOG" 2>&1; then
  notify_error "Blade Arena exited with an error."
  exit 1
fi
