#!/usr/bin/env bash
# One-click play from repo root or Desktop pane terminal.
export DISPLAY="${DISPLAY:-:1}"
export WORKSPACE="${WORKSPACE:-/workspace}"
exec /workspace/scripts/run-blade-arena-desktop.sh
