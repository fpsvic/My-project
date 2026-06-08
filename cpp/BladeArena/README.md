# Blade Arena (C++)

Native C++ port of Blade Arena using [Raylib](https://www.raylib.com/). Runs on the Desktop without a Unity license.

**Outdoor open world:** ~400×400 map with rolling hills, winding rivers, ~1400 trees, scattered cabins with sword loot, and your **HumanFigure** GLB as the visible third-person character.

## Build

```bash
cd /workspace/cpp/BladeArena
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)"
```

First build downloads Raylib via CMake and may take a few minutes.

## Run

From the repo root (so the default model path resolves):

```bash
/workspace/scripts/run-blade-arena-cpp.sh
```

Or manually:

```bash
cd /workspace/cpp/BladeArena/build
./blade_arena /workspace/Assets/Models/HumanFigure.glb
```

## Controls

| Input | Action |
|-------|--------|
| Right-click | Move to spot |
| Space | Jump |
| A | Melee attack |
| R | Restart |

Walk into shelter buildings to pick up **Iron Sword**, **Steel Sword**, and **Storm Blade** loot. FPS is shown top-right.

## Requirements

- CMake 3.16+
- C++17 compiler (g++)
- OpenGL / X11 (Desktop pane or local display)
- Uses `Assets/Models/HumanFigure_game.glb` (simplified mesh for Raylib; full `HumanFigure.glb` has too many vertices for 16-bit indices and renders as a broken thin line)
- Falls back to a capsule if no model is found
