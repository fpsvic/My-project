#!/usr/bin/env bash
# Build (if needed) and launch the native C++ Blade Arena on the Desktop.
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
CPP_DIR="$WORKSPACE/cpp/BladeArena"
BUILD_DIR="$CPP_DIR/build"
BINARY="$BUILD_DIR/blade_arena"
MODEL_WALK="$WORKSPACE/Assets/Models/HumanFigure_walk.glb"
MODEL_GAME="$WORKSPACE/Assets/Models/HumanFigure_game.glb"
MODEL="$WORKSPACE/Assets/Models/HumanFigure.glb"
DISPLAY="${DISPLAY:-:1}"
BUILD_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --build-only) BUILD_ONLY=true ;;
  esac
done

export DISPLAY
cd "$WORKSPACE"

build_game() {
  if ! command -v g++ >/dev/null 2>&1; then
    echo "g++ not found. Install build-essential." >&2
    return 1
  fi
  if ! command -v cmake >/dev/null 2>&1; then
    echo "cmake not found." >&2
    return 1
  fi
  echo "Building Blade Arena..."
  cmake -S "$CPP_DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++
  cmake --build "$BUILD_DIR" -j"$(nproc)"
}

if [[ ! -x "$BINARY" ]]; then
  build_game
fi

if $BUILD_ONLY; then
  exit 0
fi

MODEL_ARG=""
if [[ -f "$MODEL_WALK" ]]; then
  MODEL_ARG="$MODEL_WALK"
elif [[ -f "$MODEL_GAME" ]]; then
  MODEL_ARG="$MODEL_GAME"
elif [[ -f "$MODEL" ]]; then
  echo "Note: Using full HumanFigure.glb — simplified HumanFigure_game.glb is recommended." >&2
  MODEL_ARG="$MODEL"
else
  echo "Note: HumanFigure model not found — using placeholder capsule." >&2
fi

# Run game (do not exec — desktop launcher needs exit codes).
if [[ -n "$MODEL_ARG" ]]; then
  "$BINARY" "$MODEL_ARG"
else
  "$BINARY"
fi
