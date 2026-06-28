# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

This is a **Unity 6 (`6000.4.8f1`) URP "3D" template** project. It is a client-side game
project — there is **no backend, Docker stack, database, or npm/pnpm dependency tree**.
"Running the application end-to-end" means opening the project in the Unity Editor (Play
Mode) or building/running a standalone Linux player.

- Pinned editor version: `ProjectSettings/ProjectVersion.txt` → `6000.4.8f1` (changeset `f8b72d3d7343`).
- UPM packages are declared in `Packages/manifest.json` and pinned in `Packages/packages-lock.json`.
  The Editor restores them automatically into the gitignored `Library/` folder on first open
  (allow a few minutes the first time).

### Installed tooling (VM snapshot)

The cloud VM snapshot already contains:

| Tool | Path / command |
|---|---|
| Unity Editor `6000.4.8f1` | `$HOME/Unity/Hub/Editor/6000.4.8f1/Editor/Unity` |
| Native libs for the Editor | installed via apt (see update script) |
| Virtual display | `DISPLAY=:1` (use `xvfb-run -a` for headless CLI) |

Convenience for CLI sessions:

```bash
export UNITY_PATH="$HOME/Unity/Hub/Editor/6000.4.8f1/Editor/Unity"
```

### License activation is REQUIRED before the Editor can run anything

Without a valid license, every Editor invocation (open, compile, test, build) fails with
exit code `198` and the log line `No valid Unity Editor license found`. The native editor
itself is fully installed and functional (e.g. `-createManualActivationFile` succeeds and
exits `0`); only the license entitlement is missing.

Provide a license via repository **Secrets** (preferred for cloud agents — they persist and
are injected as env vars):

- `UNITY_LICENSE` — full contents of a `Unity_lic.ulf` file (a Personal license generated on
  another machine via Unity Hub → Preferences → Licenses → Add → free Personal license; on
  Linux the file lives at `~/.local/share/unity3d/Unity/Unity_lic.ulf`).
- `UNITY_EMAIL` / `UNITY_PASSWORD` — Unity account credentials (used by some CI activation
  flows; may hit MFA, so `UNITY_LICENSE` is more reliable).

Activate from a `UNITY_LICENSE` secret (run once per session before other Editor commands):

```bash
mkdir -p ~/.local/share/unity3d/Unity
printf '%s' "$UNITY_LICENSE" > ~/.local/share/unity3d/Unity/Unity_lic.ulf
```

Alternatively, activate interactively through **Unity Hub on the Desktop pane** (`DISPLAY=:1`).
Unity Hub is not installed by the update script; install it only if you need the interactive
GUI activation path.

### Common commands (require a valid license)

Open/compile the project (batchmode smoke test — expect exit `0`):

```bash
xvfb-run -a "$UNITY_PATH" -batchmode -nographics \
  -projectPath /workspace -logFile /tmp/unity-open.log -quit -accept-apiupdate
```

Build a Linux standalone player:

```bash
mkdir -p /tmp/builds/linux64
xvfb-run -a "$UNITY_PATH" -batchmode -nographics \
  -projectPath /workspace -buildLinux64Player /tmp/builds/linux64/MyProject \
  -logFile /tmp/unity-build.log -quit
```

Run the built player (exercises the URP `SampleScene`):

```bash
chmod +x /tmp/builds/linux64/MyProject
xvfb-run -a /tmp/builds/linux64/MyProject -batchmode -nographics -logFile /tmp/player.log
```

### Lint / tests

- No ESLint / dotnet-format / repo CI config is present.
- `com.unity.test-framework` is installed but **no Edit Mode / Play Mode tests are authored**,
  so there is nothing to run until tests are added. When tests exist, run them with:
  `xvfb-run -a "$UNITY_PATH" -runTests -projectPath /workspace -testPlatform PlayMode -batchmode`.

### Gotchas

- `-nographics` batchmode still requires a valid license; exit code `198` means activation is missing.
- The first project open downloads UPM packages into `Library/` (gitignored); allow several minutes.
- The Editor binary lives under `$HOME`, which is captured by the VM snapshot, so re-downloading
  the ~4 GB installer is normally unnecessary on subsequent sessions; the update script only
  re-installs it when it is missing.
