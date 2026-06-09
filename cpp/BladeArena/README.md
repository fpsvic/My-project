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

**Desktop (recommended):** double-click **Play Blade Arena** on the VM desktop. If missing:

```bash
/workspace/scripts/install-desktop-shortcuts.sh
```

**Terminal:**

```bash
/workspace/scripts/run-blade-arena-desktop.sh
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

## Live Lua scripting (hot reload)

Gameplay tuning lives in **`scripts/game/config.lua`** — weapons, enemies, combos, storm, player movement.

1. Run the game (keep it open).
2. Edit `config.lua` in another window (e.g. change `storm_blade.damage = 4.5` to `45`).
3. **Save** — changes apply in ~0.35 seconds without recompiling.
4. Press **F5** in-game to force a reload.

No C++ rebuild needed for balance tweaks. Rebuild only when changing engine code.

## Requirements

- CMake 3.16+
- C++17 compiler (g++)
- OpenGL / X11 (Desktop pane or local display)
- Uses `Assets/Models/HumanFigure_walk.glb` (rigged walk cycle baked from `HumanFigure_game.glb`). Falls back to `HumanFigure_game.glb` if missing. Raylib only supports 16-bit mesh indices, so the full 135k-vertex `HumanFigure.glb` must not be loaded directly.
- The player model keeps Raylib's built-in glTF PBR shader (textures + normals). Do not replace it with the custom terrain lighting shader.
- Falls back to a capsule if no model is found
