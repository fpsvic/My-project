#!/usr/bin/env bash
# Double-click this file on the Desktop if the .desktop icon does nothing.
export DISPLAY="${DISPLAY:-:1}"
export WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"
exec /workspace/scripts/run-blade-arena-desktop.sh
