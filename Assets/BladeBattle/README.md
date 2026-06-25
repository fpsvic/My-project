# Blade Battle

A 3D third-person arena combat game (Fortnite-style movement + melee blade combat),
built for Unity 6 with URP. The **entire game generates itself from code at runtime** —
no manual scene setup, prefabs, or imported art are required.

## How to play

1. Open the project in Unity 6 (6000.4.8f1 or compatible).
2. Open `Assets/Scenes/SampleScene.unity` (it already contains a `Game` object with the
   `GameBootstrap` component attached).
3. Press **Play**.

### Controls

| Action            | Input                |
|-------------------|----------------------|
| Move              | `W A S D` / Arrows   |
| Sprint            | `Left Shift`         |
| Jump              | `Space`              |
| Slash (blade)     | `Left Mouse` / `J`   |
| Look / aim camera | Mouse                |
| Free / lock cursor| `Esc`                |
| Restart (on death)| `R`                  |

Uses Unity's **new Input System** (the project is set to "Input System Package" only).

## Gameplay

- Survive escalating **waves** of enemy "blade bots" that spawn around the arena and
  charge you.
- **Chain your slashes** within the combo window for bonus damage (`COMBO x2`, `x3` …).
- Each kill awards score and a small heal. Clear a wave to advance; the next wave has
  more, faster, tougher enemies (with occasional oversized "brutes" from wave 3).
- The HUD shows health, current wave, score, and your live combo. Death shows a
  **Game Over** screen — press `R` to fight again.

## Architecture (`Assets/BladeBattle/Scripts/`)

| Script               | Responsibility                                                       |
|----------------------|----------------------------------------------------------------------|
| `GameBootstrap`      | Entry point — builds environment, arena, player, camera, HUD, systems |
| `GameManager`        | Wave flow, scoring, player death/restart, HUD sync (singleton)        |
| `PlayerController`   | Camera-relative third-person movement, sprint, jump, gravity          |
| `ThirdPersonCamera`  | Mouse-look orbit follow camera with obstacle-avoiding spring arm      |
| `PlayerCombat`       | Blade swing arc, frontal-cone hit detection, combo system, knockback  |
| `EnemyAI`            | Chase / attack / knockback melee enemy behaviour                      |
| `EnemySpawner`       | Builds enemy "blade bots" from primitives and spawns them on a ring   |
| `Health`             | Shared health/damage/death component (player + enemies)               |
| `HitFlash`           | White hit-flash feedback on damage                                    |
| `DamagePopup`        | Floating world-space hit / combo / reward text                        |
| `HUD`                | Runtime-built uGUI (health bar, wave, score, combo, banners, game over)|
| `BuildHelper`        | Primitive / material construction utilities (URP-aware)               |

All visuals are built from Unity primitives with URP-compatible materials, so the game
runs with zero external assets.
