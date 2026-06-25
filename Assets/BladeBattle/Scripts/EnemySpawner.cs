using UnityEngine;

namespace BladeBattle
{
    /// <summary>
    /// Builds enemy "blade bots" from primitives and spawns them in waves around the arena.
    /// </summary>
    public class EnemySpawner : MonoBehaviour
    {
        public Transform player;
        public float arenaRadius = 38f;
        Material _bodyMat, _trimMat, _bladeMat;

        public void Init(Transform player, float arenaRadius)
        {
            this.player = player;
            this.arenaRadius = arenaRadius;
            _bodyMat = BuildHelper.MakeMaterial(new Color(0.55f, 0.12f, 0.14f));
            _trimMat = BuildHelper.MakeMaterial(new Color(0.12f, 0.12f, 0.14f));
            _bladeMat = BuildHelper.MakeEmissive(new Color(1f, 0.35f, 0.2f), 2.5f);
        }

        public GameObject SpawnOne(float hp, float speed, float damage, float scale)
        {
            // Pick a point on a ring around the arena edge.
            float ang = Random.value * Mathf.PI * 2f;
            float r = arenaRadius * Random.Range(0.55f, 0.95f);
            Vector3 pos = new Vector3(Mathf.Cos(ang) * r, 2f, Mathf.Sin(ang) * r);

            var enemy = BuildBot(scale);
            enemy.transform.position = pos;

            var ai = enemy.GetComponent<EnemyAI>();
            ai.Init(player, hp, speed, damage);
            return enemy;
        }

        GameObject BuildBot(float scale)
        {
            var root = new GameObject("BladeBot");
            root.transform.localScale = Vector3.one * scale;

            // Visual body (no colliders on visuals — the CharacterController is the collider).
            var visual = new GameObject("Visual");
            visual.transform.SetParent(root.transform, false);

            BuildHelper.Block("Torso", PrimitiveType.Capsule, visual.transform,
                new Vector3(0, 1.1f, 0), new Vector3(0.8f, 0.7f, 0.8f), _bodyMat, false);
            BuildHelper.Block("Head", PrimitiveType.Cube, visual.transform,
                new Vector3(0, 1.85f, 0), new Vector3(0.5f, 0.5f, 0.5f), _trimMat, false);
            // Glowing eyes
            BuildHelper.Block("EyeL", PrimitiveType.Cube, visual.transform,
                new Vector3(-0.13f, 1.9f, 0.26f), new Vector3(0.12f, 0.06f, 0.05f), _bladeMat, false);
            BuildHelper.Block("EyeR", PrimitiveType.Cube, visual.transform,
                new Vector3(0.13f, 1.9f, 0.26f), new Vector3(0.12f, 0.06f, 0.05f), _bladeMat, false);
            // Legs
            BuildHelper.Block("LegL", PrimitiveType.Cube, visual.transform,
                new Vector3(-0.2f, 0.35f, 0), new Vector3(0.25f, 0.7f, 0.25f), _trimMat, false);
            BuildHelper.Block("LegR", PrimitiveType.Cube, visual.transform,
                new Vector3(0.2f, 0.35f, 0), new Vector3(0.25f, 0.7f, 0.25f), _trimMat, false);

            // Weapon arm with a blade.
            var weaponPivot = new GameObject("WeaponPivot");
            weaponPivot.transform.SetParent(root.transform, false);
            weaponPivot.transform.localPosition = new Vector3(0.5f, 1.2f, 0.2f);
            BuildHelper.Block("Arm", PrimitiveType.Cube, weaponPivot.transform,
                new Vector3(0, 0, 0.4f), new Vector3(0.18f, 0.18f, 0.9f), _bodyMat, false);
            BuildHelper.Block("Blade", PrimitiveType.Cube, weaponPivot.transform,
                new Vector3(0, 0, 1.1f), new Vector3(0.08f, 0.5f, 0.9f), _bladeMat, false);

            // Physics: a CharacterController sized to the body.
            var cc = root.AddComponent<CharacterController>();
            cc.center = new Vector3(0, 1.0f, 0);
            cc.radius = 0.45f;
            cc.height = 2.0f;

            root.AddComponent<Health>();
            root.AddComponent<HitFlash>();
            root.AddComponent<EnemyAI>();
            return root;
        }
    }
}
