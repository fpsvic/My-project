#!/usr/bin/env bash
# Best-effort restart of the XFCE panel/desktop on :1 (does not restart VNC server).
set -euo pipefail

export DISPLAY="${DISPLAY:-:1}"

if ! xdpyinfo >/dev/null 2>&1; then
  echo "DISPLAY=$DISPLAY is not available. The cloud VM desktop service may still be starting."
  echo "Wait 30-60 seconds and run: /workspace/scripts/check-desktop.sh"
  exit 1
fi

echo "Restarting XFCE components on $DISPLAY..."
xfce4-panel --quit 2>/dev/null || true
pkill -x xfdesktop 2>/dev/null || true
sleep 1
xfdesktop --display "$DISPLAY" >/dev/null 2>&1 &
xfce4-panel --display "$DISPLAY" >/dev/null 2>&1 &
echo "Done. Re-open the Desktop tab in Cursor or refresh cursor.com/agents."
