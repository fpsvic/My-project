using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;

public class BladeArenaGame : MonoBehaviour
{
    public static BladeArenaGame Instance { get; private set; }

    [SerializeField] int startingEnemyCount = 6;
    [SerializeField] float enemySpawnRadius = 12f;

    int enemiesRemaining;
    int score;
    bool gameOver;

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        BuildArenaIfNeeded();
        EnsurePlayerIsPlayable();
        EnsureStormSystem();
        SpawnEnemies();
        enemiesRemaining = FindObjectsByType<ArenaEnemy>(FindObjectsSortMode.None).Length;
    }

    void Update()
    {
        if (!gameOver || Keyboard.current == null)
            return;

        if (Keyboard.current.rKey.wasPressedThisFrame)
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }

    void BuildArenaIfNeeded()
    {
        if (GameObject.Find("Blade Arena Floor") == null)
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            floor.name = "Blade Arena Floor";
            floor.transform.position = new Vector3(0f, -0.05f, 0f);
            floor.transform.localScale = new Vector3(6f, 0.05f, 6f);

            CreateWall("Arena Wall North", new Vector3(0f, 1.5f, 15f), new Vector3(30f, 3f, 1f));
            CreateWall("Arena Wall South", new Vector3(0f, 1.5f, -15f), new Vector3(30f, 3f, 1f));
            CreateWall("Arena Wall East", new Vector3(15f, 1.5f, 0f), new Vector3(1f, 3f, 30f));
            CreateWall("Arena Wall West", new Vector3(-15f, 1.5f, 0f), new Vector3(1f, 3f, 30f));
        }

        if (GameObject.Find("Shelter Building A") == null)
        {
            CreateShelterBuilding("Shelter Building A", new Vector3(-8f, 0f, 6f));
            CreateShelterBuilding("Shelter Building B", new Vector3(7f, 0f, -5f));
            CreateShelterBuilding("Shelter Building C", new Vector3(0f, 0f, 9f));
        }
    }

    static void CreateWall(string name, Vector3 position, Vector3 scale)
    {
        var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
        wall.name = name;
        wall.transform.position = position;
        wall.transform.localScale = scale;
    }

    static void CreateShelterBuilding(string name, Vector3 position)
    {
        var baseBlock = GameObject.CreatePrimitive(PrimitiveType.Cube);
        baseBlock.name = name;
        baseBlock.transform.position = position + new Vector3(0f, 1.5f, 0f);
        baseBlock.transform.localScale = new Vector3(4f, 3f, 4f);

        var roof = GameObject.CreatePrimitive(PrimitiveType.Cube);
        roof.name = name + " Roof";
        roof.transform.SetParent(baseBlock.transform);
        roof.transform.localPosition = new Vector3(0f, 1.1f, 0f);
        roof.transform.localScale = new Vector3(1.2f, 0.2f, 1.2f);

        var shelterZone = new GameObject(name + " Shelter Zone");
        shelterZone.transform.SetParent(baseBlock.transform, false);
        shelterZone.transform.localPosition = new Vector3(0f, 0.4f, 0f);
        var shelterCollider = shelterZone.AddComponent<BoxCollider>();
        shelterCollider.isTrigger = true;
        shelterCollider.size = new Vector3(5f, 4f, 5f);
        shelterZone.AddComponent<BuildingShelter>();
    }

    void EnsurePlayerIsPlayable()
    {
        var player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
            return;

        if (player.name != "Player")
            player.name = "Player";

        if (player.GetComponent<CharacterController>() == null)
        {
            var controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f;
            controller.radius = 0.3f;
            controller.center = new Vector3(0f, 0.9f, 0f);
        }

        if (player.GetComponent<PlayerMovement>() == null)
            player.AddComponent<PlayerMovement>();

        if (player.GetComponent<MeleeAttack>() == null)
            player.AddComponent<MeleeAttack>();

        if (player.GetComponent<PlayerHealth>() == null)
            player.AddComponent<PlayerHealth>();
    }

    static void EnsureStormSystem()
    {
        if (FindFirstObjectByType<StormSystem>() != null)
            return;

        var stormObject = new GameObject("Storm System");
        stormObject.AddComponent<StormSystem>();
    }

    void SpawnEnemies()
    {
        for (int i = 0; i < startingEnemyCount; i++)
        {
            float angle = (Mathf.PI * 2f / startingEnemyCount) * i;
            Vector3 position = new Vector3(Mathf.Cos(angle), 0.9f, Mathf.Sin(angle)) * enemySpawnRadius;
            CreateEnemy(position);
        }
    }

    static void CreateEnemy(Vector3 position)
    {
        var enemy = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        enemy.name = "Arena Enemy";
        enemy.transform.position = position;
        enemy.transform.localScale = new Vector3(0.9f, 0.9f, 0.9f);
        enemy.AddComponent<ArenaEnemy>();
    }

    public void OnEnemyDefeated()
    {
        score++;
        enemiesRemaining = Mathf.Max(0, FindObjectsByType<ArenaEnemy>(FindObjectsSortMode.None).Length);
        if (enemiesRemaining <= 0 && !gameOver)
            Debug.Log("Blade Arena: You cleared the arena! Score: " + score);
    }

    public void OnPlayerDefeated()
    {
        gameOver = true;
        Debug.Log("Blade Arena: Defeated. Press R to restart.");
    }

    void OnGUI()
    {
        var player = GameObject.FindGameObjectWithTag("Player");
        var health = player != null ? player.GetComponent<PlayerHealth>() : null;
        var storm = FindFirstObjectByType<StormSystem>();

        GUI.Label(new Rect(12f, 12f, 500f, 24f), "Blade Arena");
        GUI.Label(new Rect(12f, 36f, 560f, 24f), "Right-click move · Space jump · A attack · R restart");
        if (health != null)
            GUI.Label(new Rect(12f, 60f, 400f, 24f), "Health: " + health.CurrentHealth);
        GUI.Label(new Rect(12f, 84f, 400f, 24f), "Enemies left: " + enemiesRemaining + " · Score: " + score);
        if (storm != null && storm.IsStormActive)
            GUI.Label(new Rect(12f, 108f, 560f, 24f), "STORM — stay under a building or risk lightning!");
        if (gameOver)
            GUI.Label(new Rect(12f, 132f, 500f, 24f), "Defeated — press R to try again");
    }
}
