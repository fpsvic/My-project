#!/usr/bin/env bash
# Build (if needed) and launch the native C++ Blade Arena on the Desktop.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
CPP_DIR="$WORKSPACE/cpp/BladeArena"
BUILD_DIR="$CPP_DIR/build"
BINARY="$BUILD_DIR/blade_arena"
MODEL_GAME="$WORKSPACE/Assets/Models/HumanFigure_game.glb"
MODEL="$WORKSPACE/Assets/Models/HumanFigure.glb"
DISPLAY="${DISPLAY:-:1}"

export DISPLAY

if [[ ! -x "$BINARY" ]]; then
  echo "Building Blade Arena (C++)..."
  cmake -S "$CPP_DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++
  cmake --build "$BUILD_DIR" -j"$(nproc)"
fi

if [[ -f "$MODEL_GAME" ]]; then
  exec "$BINARY" "$MODEL_GAME"
elif [[ -f "$MODEL" ]]; then
  echo "Note: Using full HumanFigure.glb — run gltf-transform simplify for best results."
  exec "$BINARY" "$MODEL"
else
  echo "Note: HumanFigure model not found — using placeholder capsule."
  exec "$BINARY"
fi
