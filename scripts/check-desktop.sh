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

novnc_ok=false
if command -v ss >/dev/null 2>&1 && ss -tln 2>/dev/null | rg -q ':26058'; then
  novnc_ok=true
elif command -v netstat >/dev/null 2>&1 && netstat -tln 2>/dev/null | rg -q ':26058'; then
  novnc_ok=true
elif curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:26058/ 2>/dev/null | rg -q '^200$'; then
  novnc_ok=true
fi
if $novnc_ok; then
  echo "[OK] noVNC proxy listening on 26058"
else
  echo "[FAIL] noVNC port 26058 not responding — run: /workspace/scripts/fix-desktop.sh"
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
echo "  1. Run: /workspace/scripts/fix-desktop.sh"
echo "  2. Open https://cursor.com/agents and use Desktop there"
echo "  3. Cmd/Ctrl+Shift+P -> Developer: Reload Window"
echo "  4. Remove .cursor/environment.json if it blocks computer use"
echo
echo "Play game without Desktop pane (logs only):"
echo "  /workspace/scripts/run-blade-arena-cpp.sh --build-only"
echo "  DISPLAY=:1 /workspace/scripts/run-blade-arena-cpp.sh"
