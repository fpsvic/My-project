#!/usr/bin/env bash
# One-shot: repair desktop streaming, install shortcuts, launch game.
set -euo pipefail

export DISPLAY="${DISPLAY:-:1}"
export WORKSPACE="${WORKSPACE:-/workspace}"

echo "=== Blade Arena — desktop play ==="
/workspace/scripts/fix-desktop.sh
/workspace/scripts/install-desktop-shortcuts.sh
/workspace/scripts/run-blade-arena-desktop.sh
