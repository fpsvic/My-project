# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

This is a **Unity 6 (6000.4.8f1) URP empty template** project. There is no backend, Docker stack, or npm/pnpm dependency tree. End-to-end development means opening the project in the Unity Editor (or building/running a standalone Linux player).

Pinned editor version: `ProjectSettings/ProjectVersion.txt` → `6000.4.8f1` (changeset `f8b72d3d7343`).

### Installed tooling (VM snapshot)

The cloud VM is expected to have:

| Tool | Path / command |
|---|---|
| Unity Hub (deb) | `unityhub` |
| Unity Editor 6000.4.8f1 | `$HOME/Unity/Hub/Editor/6000.4.8f1/Unity` |
| Virtual display | `DISPLAY=:1` (use `xvfb-run -a` for headless CLI) |

Set this once per shell session when using CLI builds:

```bash
export UNITY_PATH="$HOME/Unity/Hub/Editor/6000.4.8f1/Unity"
```

### License activation (required before Editor runs)

Unity **Personal** licenses cannot be activated from the command line alone. Provide these secrets to the environment:

- `UNITY_LICENSE` — full contents of `Unity_lic.ulf` (generate via Unity Hub → Preferences → Licenses → Add → Get a free personal license on any machine; file lives at `~/.local/share/unity3d/Unity/Unity_lic.ulf` on Linux)
- `UNITY_EMAIL` — Unity account email
- `UNITY_PASSWORD` — Unity account password

Activation helper (run once after secrets are set):

```bash
mkdir -p ~/.local/share/unity3d/Unity
printf '%s' "$UNITY_LICENSE" > ~/.local/share/unity3d/Unity/Unity_lic.ulf
xvfb-run -a "$UNITY_PATH" -batchmode -nographics -quit \
  -username "$UNITY_EMAIL" -password "$UNITY_PASSWORD" \
  -logFile /tmp/unity-activate.log
```

Alternatively, log in through **Unity Hub on the Desktop pane** (`DISPLAY=:1 unityhub --no-sandbox`) and activate a Personal license in Preferences → Licenses.

### Common commands

**Open / compile project (batchmode smoke test):**

```bash
xvfb-run -a "$UNITY_PATH" -batchmode -nographics \
  -projectPath /workspace \
  -logFile /tmp/unity-open.log \
  -quit -accept-apiupdate
```

Expect exit code `0` when the license is valid and packages compile.

**Build Linux standalone player:**

```bash
mkdir -p /tmp/builds/linux64
xvfb-run -a "$UNITY_PATH" -batchmode -nographics \
  -projectPath /workspace \
  -buildLinux64Player /tmp/builds/linux64/MyProject \
  -logFile /tmp/unity-build.log \
  -quit
```

**Run built player (hello-world demo):**

```bash
chmod +x /tmp/builds/linux64/MyProject
xvfb-run -a /tmp/builds/linux64/MyProject -batchmode -nographics -logFile /tmp/player.log
```

The template scene (`Assets/Scenes/SampleScene.unity`) contains a Main Camera, Directional Light, and URP Global Volume — running the player exercises core rendering.

### Lint / tests

- No ESLint, dotnet format, or repo CI config is present.
- `com.unity.test-framework` is installed but **no tests are authored**; there is nothing to run until Edit Mode / Play Mode tests are added.

### Native C++ Blade Arena (no Unity license required)

Full gameplay on the Desktop pane without Unity:

- **Desktop (most reliable):** open Desktop pane → double-click **`START-BLADE-ARENA.sh`** (install shortcuts: `/workspace/scripts/install-desktop-shortcuts.sh`)
- **Desktop icon:** double-click **Play Blade Arena** (`.desktop` icons may not work in all Cursor Desktop setups — use the `.sh` file instead)
- **Terminal on Desktop:** `/workspace/scripts/run-blade-arena-desktop.sh`

Requires branch `cursor/blade-arena-cpp-5aaf`, `DISPLAY=:1`, and a pre-built or buildable binary in `cpp/BladeArena/build/`. Errors: `/tmp/blade-arena-launch.log`. This is **not** the Unity Editor — Unity still needs a license.

### Desktop preview (no Unity license required)

To preview the **Human Figure** model on the Desktop pane (`DISPLAY=:1`):

```bash
/workspace/scripts/preview-desktop.sh browser
```

This starts a local web server and opens a Three.js viewer at `Preview/index.html` (same GLB as `Assets/Models/HumanFigure.glb`).

Other modes:

```bash
/workspace/scripts/preview-desktop.sh blender   # Blender viewport
/workspace/scripts/preview-desktop.sh unity     # Unity Editor (license required)
```

A **Preview Human Figure** shortcut is also on the VM desktop.

Unity **Play Mode** preview still needs an activated Personal license (`UNITY_LICENSE` + account secrets, or Hub login on Desktop).

### Playable character controls

`SampleScene` runs **Blade Arena** with your uploaded model as the **Player** character:

- **Right-click** — move to spot
- **Space** — jump
- **A** — melee attack
- **R** — restart after defeat
- **Storm** — 10% chance; night + lightning; 5% strike chance if not under a building
- **Camera** follows the player automatically

The player uses `Assets/Models/HumanFigure.glb` (scene object named **Player**).

Scripts: `BladeArenaGame.cs`, `PlayerMovement.cs`, `MeleeAttack.cs`, `PlayerHealth.cs`, `ArenaEnemy.cs`, `CameraFollow.cs`

### Gotchas

- Unity Hub deb install may hang on an interactive `unityhub/add-apt-repo` debconf prompt; preset with `debconf-set-selections` and `DEBIAN_FRONTEND=noninteractive`.
- Unity Hub CLI (`unityhub --headless`) is slow and needs `xvfb-run`; direct editor tarball install is faster for the pinned version.
- `-nographics` batchmode still requires a valid license; exit code `198` with log message `No valid Unity Editor license found` means activation is missing.
- First project open downloads UPM packages into `Library/` (gitignored); allow several minutes.
- Unity Hub login buttons may need `dbus-x11` and `dbus-launch` for the Desktop pane webview to be clickable.
