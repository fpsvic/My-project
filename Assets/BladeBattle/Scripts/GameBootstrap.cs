using UnityEngine;

namespace BladeBattle
{
    /// <summary>
    /// Single entry point for "Blade Battle". Attach this to one GameObject in the scene
    /// (or it can be added at runtime) and press Play — it builds the arena, the player,
    /// the camera rig, the HUD and the wave system entirely from code.
    /// </summary>
    public class GameBootstrap : MonoBehaviour
    {
        [Header("Arena")]
        public float arenaRadius = 40f;

        Transform _player;

        void Start()
        {
            SetupEnvironment();
            BuildArena();
            _player = BuildPlayer();
            var cam = SetupCamera(_player);

            var combat = _player.GetComponent<PlayerCombat>();
            var bladePivot = _player.Find("BladePivot");
            combat.Init(bladePivot);
            _player.GetComponent<PlayerController>().Init(cam);

            var hud = BuildHUD();
            var spawner = gameObject.AddComponent<EnemySpawner>();
            spawner.Init(_player, arenaRadius);

            var combo = _player.GetComponent<PlayerCombat>();
            combo.OnCombo += hud.SetCombo;

            var gm = gameObject.AddComponent<GameManager>();
            gm.Configure(hud, spawner, _player.GetComponent<Health>(), _player);

            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }

        void SetupEnvironment()
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.45f, 0.55f, 0.75f);
            RenderSettings.ambientEquatorColor = new Color(0.35f, 0.35f, 0.4f);
            RenderSettings.ambientGroundColor = new Color(0.15f, 0.13f, 0.12f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.55f, 0.62f, 0.72f);
            RenderSettings.fogStartDistance = arenaRadius * 1.2f;
            RenderSettings.fogEndDistance = arenaRadius * 3f;

            // Ensure a sun light exists.
            Light sun = null;
            foreach (var l in FindObjectsByType<Light>(FindObjectsSortMode.None))
                if (l.type == LightType.Directional) { sun = l; break; }
            if (sun == null)
            {
                var go = new GameObject("Sun");
                sun = go.AddComponent<Light>();
                sun.type = LightType.Directional;
            }
            sun.transform.rotation = Quaternion.Euler(48f, 130f, 0f);
            sun.color = new Color(1f, 0.96f, 0.86f);
            sun.intensity = 1.3f;
            sun.shadows = LightShadows.Soft;
        }

        void BuildArena()
        {
            var arena = new GameObject("Arena").transform;

            var grassA = BuildHelper.MakeMaterial(new Color(0.30f, 0.45f, 0.25f));
            var grassB = BuildHelper.MakeMaterial(new Color(0.26f, 0.40f, 0.22f));
            var stone = BuildHelper.MakeMaterial(new Color(0.5f, 0.5f, 0.55f));
            var wood = BuildHelper.MakeMaterial(new Color(0.55f, 0.38f, 0.2f));
            var wall = BuildHelper.MakeMaterial(new Color(0.35f, 0.37f, 0.42f));

            // Checkerboard ground tiles for a readable, Fortnite-ish look.
            int tiles = 10;
            float tileSize = (arenaRadius * 2f) / tiles;
            for (int x = 0; x < tiles; x++)
            for (int z = 0; z < tiles; z++)
            {
                var mat = (x + z) % 2 == 0 ? grassA : grassB;
                var pos = new Vector3(-arenaRadius + tileSize * (x + 0.5f), -0.5f,
                                      -arenaRadius + tileSize * (z + 0.5f));
                BuildHelper.Block($"Tile_{x}_{z}", PrimitiveType.Cube, arena, pos,
                    new Vector3(tileSize, 1f, tileSize), mat);
            }

            // Perimeter wall ring so the player can't walk off.
            int segs = 40;
            for (int i = 0; i < segs; i++)
            {
                float a = (i / (float)segs) * Mathf.PI * 2f;
                var pos = new Vector3(Mathf.Cos(a) * arenaRadius, 1.5f, Mathf.Sin(a) * arenaRadius);
                var go = BuildHelper.Block($"Wall_{i}", PrimitiveType.Cube, arena, pos,
                    new Vector3(tileSize * 1.1f, 4f, 2f), wall);
                go.transform.rotation = Quaternion.Euler(0, -a * Mathf.Rad2Deg + 90f, 0);
            }

            // Central raised platform with ramps (build-y vibe).
            BuildHelper.Block("CenterPlatform", PrimitiveType.Cube, arena,
                new Vector3(0, 1f, 0), new Vector3(12, 2f, 12), stone);
            for (int i = 0; i < 4; i++)
            {
                float a = i * 90f * Mathf.Deg2Rad;
                var ramp = BuildHelper.Block($"Ramp_{i}", PrimitiveType.Cube, arena,
                    new Vector3(Mathf.Cos(a) * 9f, 1f, Mathf.Sin(a) * 9f),
                    new Vector3(4f, 0.4f, 7f), wood);
                ramp.transform.rotation = Quaternion.Euler(28f, i * 90f, 0);
            }

            // Scattered cover: boxes, towers and barriers.
            int seed = 12345;
            Random.InitState(seed);
            for (int i = 0; i < 26; i++)
            {
                float a = Random.value * Mathf.PI * 2f;
                float r = Random.Range(14f, arenaRadius - 6f);
                var p = new Vector3(Mathf.Cos(a) * r, 0, Mathf.Sin(a) * r);
                int kind = Random.Range(0, 3);
                if (kind == 0)
                {
                    float h = Random.Range(1.2f, 2.5f);
                    BuildHelper.Block($"Crate_{i}", PrimitiveType.Cube, arena,
                        p + Vector3.up * (h * 0.5f), new Vector3(Random.Range(1.5f, 3f), h, Random.Range(1.5f, 3f)), wood)
                        .transform.rotation = Quaternion.Euler(0, Random.Range(0, 360f), 0);
                }
                else if (kind == 1)
                {
                    float h = Random.Range(3f, 6f);
                    BuildHelper.Block($"Tower_{i}", PrimitiveType.Cube, arena,
                        p + Vector3.up * (h * 0.5f), new Vector3(2.2f, h, 2.2f), stone);
                }
                else
                {
                    BuildHelper.Block($"Barrier_{i}", PrimitiveType.Cube, arena,
                        p + Vector3.up * 0.75f, new Vector3(Random.Range(3f, 6f), 1.5f, 0.6f), wall)
                        .transform.rotation = Quaternion.Euler(0, Random.Range(0, 360f), 0);
                }
            }
        }

        Transform BuildPlayer()
        {
            var bodyMat = BuildHelper.MakeMaterial(new Color(0.2f, 0.45f, 0.85f));
            var trimMat = BuildHelper.MakeMaterial(new Color(0.9f, 0.9f, 0.95f));
            var skinMat = BuildHelper.MakeMaterial(new Color(0.9f, 0.72f, 0.6f));
            var hiltMat = BuildHelper.MakeMaterial(new Color(0.25f, 0.2f, 0.15f), 0.1f, 0.3f);
            var bladeMat = BuildHelper.MakeEmissive(new Color(0.6f, 0.9f, 1f), 2.2f);

            var root = new GameObject("Player");
            root.tag = "Player";
            root.transform.position = new Vector3(0, 2.5f, -10f);

            var visual = new GameObject("Visual");
            visual.transform.SetParent(root.transform, false);

            BuildHelper.Block("Torso", PrimitiveType.Capsule, visual.transform,
                new Vector3(0, 1.05f, 0), new Vector3(0.75f, 0.65f, 0.75f), bodyMat, false);
            BuildHelper.Block("Head", PrimitiveType.Sphere, visual.transform,
                new Vector3(0, 1.78f, 0), new Vector3(0.5f, 0.5f, 0.5f), skinMat, false);
            BuildHelper.Block("Backpack", PrimitiveType.Cube, visual.transform,
                new Vector3(0, 1.1f, -0.35f), new Vector3(0.5f, 0.7f, 0.3f), trimMat, false);
            BuildHelper.Block("LegL", PrimitiveType.Cube, visual.transform,
                new Vector3(-0.2f, 0.35f, 0), new Vector3(0.25f, 0.7f, 0.25f), trimMat, false);
            BuildHelper.Block("LegR", PrimitiveType.Cube, visual.transform,
                new Vector3(0.2f, 0.35f, 0), new Vector3(0.25f, 0.7f, 0.25f), trimMat, false);
            // Front marker so facing is readable.
            BuildHelper.Block("Visor", PrimitiveType.Cube, visual.transform,
                new Vector3(0, 1.8f, 0.24f), new Vector3(0.4f, 0.12f, 0.08f), bladeMat, false);

            // Sword held in the right hand, on an animatable pivot.
            var bladePivot = new GameObject("BladePivot");
            bladePivot.transform.SetParent(root.transform, false);
            bladePivot.transform.localPosition = new Vector3(0.55f, 1.0f, 0.3f);
            BuildHelper.Block("Hilt", PrimitiveType.Cube, bladePivot.transform,
                new Vector3(0, 0, 0), new Vector3(0.12f, 0.12f, 0.4f), hiltMat, false);
            BuildHelper.Block("Guard", PrimitiveType.Cube, bladePivot.transform,
                new Vector3(0, 0, 0.22f), new Vector3(0.4f, 0.1f, 0.1f), hiltMat, false);
            BuildHelper.Block("Blade", PrimitiveType.Cube, bladePivot.transform,
                new Vector3(0, 0, 1.1f), new Vector3(0.12f, 0.05f, 1.6f), bladeMat, false);

            // Physics.
            var cc = root.AddComponent<CharacterController>();
            cc.center = new Vector3(0, 0.95f, 0);
            cc.radius = 0.4f;
            cc.height = 1.9f;

            var hp = root.AddComponent<Health>();
            hp.Configure(100f, true);
            root.AddComponent<HitFlash>().Init();
            root.AddComponent<PlayerController>();
            root.AddComponent<PlayerCombat>();

            return root.transform;
        }

        ThirdPersonCamera SetupCamera(Transform player)
        {
            Camera cam = Camera.main;
            if (cam == null)
            {
                var go = new GameObject("Main Camera");
                go.tag = "MainCamera";
                cam = go.AddComponent<Camera>();
                go.AddComponent<AudioListener>();
            }
            var tpc = cam.GetComponent<ThirdPersonCamera>();
            if (tpc == null) tpc = cam.gameObject.AddComponent<ThirdPersonCamera>();
            tpc.Init(player);
            return tpc;
        }

        HUD BuildHUD()
        {
            var go = new GameObject("HUD");
            var hud = go.AddComponent<HUD>();
            hud.Build();
            return hud;
        }
    }
}
