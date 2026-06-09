#!/usr/bin/env bash
# Repair Cursor Cloud Desktop streaming (VNC + noVNC + XFCE) and show a visible window.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
export DISPLAY="${DISPLAY:-:1}"
NOVNC_PORT="${NOVNC_PORT:-26058}"
VNC_PORT="${VNC_PORT:-5901}"
LOG="/tmp/fix-desktop.log"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

port_listening() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -tln 2>/dev/null | rg -q ":${port}[^0-9]"
    return $?
  fi
  if command -v netstat >/dev/null 2>&1; then
    netstat -tln 2>/dev/null | rg -q ":${port}[^0-9]"
    return $?
  fi
  curl -s -o /dev/null "http://127.0.0.1:${port}/" 2>/dev/null
}

http_ok() {
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${NOVNC_PORT}/" 2>/dev/null || echo "000")
  [[ "$code" == "200" ]]
}

start_novnc() {
  log "Starting noVNC on port ${NOVNC_PORT} -> localhost:${VNC_PORT}"
  pkill -f "websockify.*${NOVNC_PORT}" 2>/dev/null || true
  pkill -f "launch.sh --listen ${NOVNC_PORT}" 2>/dev/null || true
  sleep 1
  if [[ -x /usr/local/novnc/noVNC-1.2.0/utils/launch.sh ]]; then
    nohup bash /usr/local/novnc/noVNC-1.2.0/utils/launch.sh \
      --listen "${NOVNC_PORT}" --vnc "localhost:${VNC_PORT}" >>"$LOG" 2>&1 &
  else
    log "ERROR: noVNC launch script not found"
    return 1
  fi
  sleep 2
}

restart_xfce() {
  log "Restarting XFCE desktop on ${DISPLAY}"
  export DISPLAY
  xfce4-panel --quit 2>/dev/null || true
  pkill -x xfdesktop 2>/dev/null || true
  sleep 1
  xfdesktop --display "$DISPLAY" >>"$LOG" 2>&1 &
  xfce4-panel --display "$DISPLAY" >>"$LOG" 2>&1 &
  sleep 1
}

show_desktop_ready() {
  log "Opening visible Desktop window"
  export DISPLAY
  if command -v xfce4-terminal >/dev/null 2>&1; then
    xfce4-terminal --title="Blade Arena Desktop" --geometry=80x20+120+80 \
      -e "bash -lc 'echo \"=== Desktop is running on DISPLAY=${DISPLAY} ===\"; echo; echo \"Play game:\"; echo \"  /workspace/PLAY-BLADE-ARENA.sh\"; echo; echo \"Or double-click Blade Arena on the desktop.\"; echo; exec bash'" \
      >>"$LOG" 2>&1 &
  elif command -v xterm >/dev/null 2>&1; then
    xterm -title "Blade Arena Desktop" -geometry 80x20+120+80 \
      -e "bash -lc 'echo Desktop ready; exec bash'" >>"$LOG" 2>&1 &
  fi
  if command -v zenity >/dev/null 2>&1; then
    zenity --info --title="Desktop Ready" --timeout=8 \
      --text="Desktop is running.\n\nDouble-click Blade Arena on the desktop,\nor run:\n/workspace/PLAY-BLADE-ARENA.sh" \
      >>"$LOG" 2>&1 &
  fi
  xrefresh -display "$DISPLAY" 2>/dev/null || true
}

log "=== fix-desktop started ==="

if [[ -f "$WORKSPACE/.cursor/environment.json" ]]; then
  log "WARN: .cursor/environment.json exists — it may block the Desktop pane."
  log "      Consider removing it if Desktop stays blank."
fi

if ! DISPLAY="$DISPLAY" xdpyinfo >/dev/null 2>&1; then
  log "ERROR: ${DISPLAY} is not available. Wait 60s and retry."
  exit 1
fi

if ! port_listening "$VNC_PORT"; then
  log "ERROR: VNC not listening on ${VNC_PORT}. Cannot fix from this script."
  exit 1
fi

if ! http_ok; then
  log "noVNC not responding — restarting"
  start_novnc
fi

if ! http_ok; then
  log "ERROR: noVNC still not responding on port ${NOVNC_PORT}"
  exit 1
fi

restart_xfce

if [[ -x "$WORKSPACE/scripts/install-desktop-shortcuts.sh" ]]; then
  log "Installing desktop shortcuts"
  "$WORKSPACE/scripts/install-desktop-shortcuts.sh" >>"$LOG" 2>&1 || true
fi

show_desktop_ready

log "=== fix-desktop complete ==="
cat <<EOF

Desktop stack repaired.

VM checks:
  DISPLAY=${DISPLAY}
  VNC port ${VNC_PORT}: listening
  noVNC port ${NOVNC_PORT}: OK (http://127.0.0.1:${NOVNC_PORT}/)

In Cursor:
  1. Open the Desktop tab (or https://cursor.com/agents → Desktop)
  2. Cmd/Ctrl+Shift+P → Developer: Reload Window
  3. You should see the desktop wallpaper + a "Blade Arena Desktop" terminal

Play game: /workspace/PLAY-BLADE-ARENA.sh
Log: ${LOG}
EOF
