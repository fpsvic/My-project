#!/usr/bin/env bash
# Quick diagnostic for Cursor Cloud Desktop (DISPLAY :1).
set -euo pipefail

echo "=== Cursor Cloud Desktop check ==="
echo "DISPLAY=${DISPLAY:-:unset}"
echo

if [[ -S /tmp/.X11-unix/X1 ]]; then
  echo "[OK] X socket /tmp/.X11-unix/X1 exists"
else
  echo "[FAIL] No X server on :1 — Desktop pane cannot show apps"
fi

if pgrep -x Xtigervnc >/dev/null 2>&1; then
  echo "[OK] TigerVNC is running"
else
  echo "[WARN] TigerVNC not found"
fi

if pgrep -f xfce4-session >/dev/null 2>&1; then
  echo "[OK] XFCE session is running"
else
  echo "[WARN] XFCE session not found"
fi

if ss -tln 2>/dev/null | rg -q ':26058'; then
  echo "[OK] noVNC proxy listening on 26058"
else
  echo "[WARN] noVNC port 26058 not listening"
fi

if DISPLAY=:1 xdpyinfo >/dev/null 2>&1; then
  echo "[OK] xdpyinfo works on DISPLAY=:1"
else
  echo "[FAIL] Cannot talk to DISPLAY=:1"
fi

echo
echo "Desktop shortcuts:"
ls -1 "$HOME/Desktop/" 2>/dev/null || echo "(none)"
echo
echo "If the Desktop *pane* in Cursor is blank:"
echo "  1. Open https://cursor.com/agents and use Desktop there"
echo "  2. Cmd/Ctrl+Shift+P -> Developer: Reload Window"
echo "  3. Remove .cursor/environment.json if it blocks computer use"
echo "  4. Start a new cloud agent (Composer models may not show Desktop)"
echo
echo "Play game without Desktop pane (logs only):"
echo "  /workspace/scripts/run-blade-arena-cpp.sh --build-only"
echo "  DISPLAY=:1 /workspace/scripts/run-blade-arena-cpp.sh"
