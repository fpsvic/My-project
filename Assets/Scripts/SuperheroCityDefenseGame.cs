using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
using UnityEngine.UI;
using Random = UnityEngine.Random;

public sealed class SuperheroCityDefenseBootstrap : MonoBehaviour
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void StartGame()
    {
        if (Object.FindFirstObjectByType<SuperheroCityDefenseGame>() != null)
        {
            return;
        }

        GameObject gameObject = new GameObject("Superhero City Defense");
        gameObject.AddComponent<SuperheroCityDefenseGame>();
    }
}

public sealed class SuperheroCityDefenseGame : MonoBehaviour
{
    private const float ArenaHalfSize = 34f;
    private const float FirstWaveDelaySeconds = 8f;
    private const float WaveIntervalSeconds = 120f;
    private const float SpeedBoostDurationSeconds = 30f;
    private const float RapidBlastDurationSeconds = 25f;
    private const float CityShieldDurationSeconds = 45f;

    private readonly List<CityBuilding> buildings = new List<CityBuilding>();
    private readonly List<EnemyRaider> enemies = new List<EnemyRaider>();
    private readonly List<HeroBlast> blasts = new List<HeroBlast>();

    private Camera mainCamera;
    private Transform hero;
    private Vector3 aimDirection = Vector3.forward;

    private Material heroMaterial;
    private Material capeMaterial;
    private Material enemyMaterial;
    private Material blastMaterial;
    private Material groundMaterial;
    private Material roadMaterial;
    private Material buildingMaterial;
    private Material shieldMaterial;

    private Text statusText;
    private Text shopText;
    private Text messageText;

    private int money = 75;
    private int waveNumber;
    private float nextWaveTimer = FirstWaveDelaySeconds;
    private float fireCooldownTimer;
    private float speedBoostTimer;
    private float rapidBlastTimer;
    private float cityShieldTimer;
    private float messageTimer;
    private string currentMessage = string.Empty;
    private bool gameOver;

    private void Awake()
    {
        CreateMaterials();
        BuildScene();
        ShowMessage("Defend the city! First enemy attack incoming soon.");
    }

    private void Update()
    {
        float deltaTime = Time.deltaTime;

        if (gameOver)
        {
            HandleRestartInput();
            UpdateHud();
            return;
        }

        speedBoostTimer = Mathf.Max(0f, speedBoostTimer - deltaTime);
        rapidBlastTimer = Mathf.Max(0f, rapidBlastTimer - deltaTime);
        cityShieldTimer = Mathf.Max(0f, cityShieldTimer - deltaTime);
        messageTimer = Mathf.Max(0f, messageTimer - deltaTime);
        fireCooldownTimer = Mathf.Max(0f, fireCooldownTimer - deltaTime);

        HandleHeroInput(deltaTime);
        HandlePowerupInput();
        UpdateWaveTimer(deltaTime);
        UpdateBlasts(deltaTime);
        UpdateEnemies(deltaTime);
        UpdateCamera();
        UpdateHud();
    }

    private void CreateMaterials()
    {
        heroMaterial = CreateMaterial(new Color(0.1f, 0.35f, 1f));
        capeMaterial = CreateMaterial(new Color(1f, 0.08f, 0.08f));
        enemyMaterial = CreateMaterial(new Color(0.8f, 0.08f, 0.08f));
        blastMaterial = CreateMaterial(new Color(1f, 0.9f, 0.18f));
        groundMaterial = CreateMaterial(new Color(0.08f, 0.32f, 0.14f));
        roadMaterial = CreateMaterial(new Color(0.12f, 0.12f, 0.14f));
        buildingMaterial = CreateMaterial(new Color(0.28f, 0.55f, 0.85f));
        shieldMaterial = CreateMaterial(new Color(0.25f, 0.9f, 1f, 0.28f));
    }

    private static Material CreateMaterial(Color color)
    {
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
        {
            shader = Shader.Find("Standard");
        }

        Material material = new Material(shader);
        material.color = color;
        return material;
    }

    private void BuildScene()
    {
        ConfigureCamera();
        ConfigureLighting();
        CreateArena();
        CreateCity();
        CreateHero();
        CreateHud();
    }

    private void ConfigureCamera()
    {
        mainCamera = Camera.main;
        if (mainCamera == null)
        {
            GameObject cameraObject = new GameObject("Main Camera");
            mainCamera = cameraObject.AddComponent<Camera>();
            cameraObject.tag = "MainCamera";
        }

        mainCamera.orthographic = true;
        mainCamera.orthographicSize = 22f;
        mainCamera.transform.position = new Vector3(0f, 36f, -28f);
        mainCamera.transform.rotation = Quaternion.Euler(55f, 0f, 0f);

        AudioListener listener = mainCamera.GetComponent<AudioListener>();
        if (listener == null)
        {
            mainCamera.gameObject.AddComponent<AudioListener>();
        }
    }

    private void ConfigureLighting()
    {
        Light existingLight = FindFirstObjectByType<Light>();
        if (existingLight != null)
        {
            existingLight.transform.rotation = Quaternion.Euler(50f, -35f, 0f);
            existingLight.intensity = 1.2f;
            return;
        }

        GameObject lightObject = new GameObject("Sun");
        Light light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightObject.transform.rotation = Quaternion.Euler(50f, -35f, 0f);
    }

    private void CreateArena()
    {
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
        ground.name = "City Park Ground";
        ground.transform.position = new Vector3(0f, -0.08f, 0f);
        ground.transform.localScale = new Vector3(ArenaHalfSize * 2.2f, 0.1f, ArenaHalfSize * 2.2f);
        ground.GetComponent<Renderer>().material = groundMaterial;

        CreateRoad("Main Avenue", new Vector3(0f, 0.02f, 0f), new Vector3(4.2f, 0.12f, ArenaHalfSize * 2f));
        CreateRoad("Cross Street", new Vector3(0f, 0.03f, 0f), new Vector3(ArenaHalfSize * 2f, 0.12f, 4.2f));
    }

    private void CreateRoad(string roadName, Vector3 position, Vector3 scale)
    {
        GameObject road = GameObject.CreatePrimitive(PrimitiveType.Cube);
        road.name = roadName;
        road.transform.position = position;
        road.transform.localScale = scale;
        road.GetComponent<Renderer>().material = roadMaterial;
    }

    private void CreateCity()
    {
        Vector3[] buildingPositions =
        {
            new Vector3(-12f, 0f, 12f),
            new Vector3(-6f, 0f, 15f),
            new Vector3(8f, 0f, 13f),
            new Vector3(14f, 0f, 8f),
            new Vector3(-14f, 0f, -7f),
            new Vector3(-8f, 0f, -14f),
            new Vector3(7f, 0f, -15f),
            new Vector3(14f, 0f, -10f),
            new Vector3(-18f, 0f, 2f),
            new Vector3(18f, 0f, -1f),
        };

        for (int i = 0; i < buildingPositions.Length; i++)
        {
            float height = Random.Range(3f, 8f);
            Vector3 scale = new Vector3(Random.Range(2.4f, 4.5f), height, Random.Range(2.4f, 4.5f));
            GameObject buildingObject = GameObject.CreatePrimitive(PrimitiveType.Cube);
            buildingObject.name = $"City Building {i + 1}";
            buildingObject.transform.position = buildingPositions[i] + Vector3.up * (height * 0.5f);
            buildingObject.transform.localScale = scale;

            Renderer renderer = buildingObject.GetComponent<Renderer>();
            Material instanceMaterial = new Material(buildingMaterial);
            instanceMaterial.color = Color.Lerp(new Color(0.2f, 0.36f, 0.62f), new Color(0.55f, 0.8f, 1f), Random.value);
            renderer.material = instanceMaterial;

            buildings.Add(new CityBuilding(buildingObject.transform, renderer, 100f + height * 8f));
        }

        GameObject cityCore = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        cityCore.name = "City Power Core";
        cityCore.transform.position = new Vector3(0f, 1f, 0f);
        cityCore.transform.localScale = new Vector3(3.5f, 1f, 3.5f);
        Renderer coreRenderer = cityCore.GetComponent<Renderer>();
        coreRenderer.material = CreateMaterial(new Color(0.25f, 0.9f, 1f));
        buildings.Add(new CityBuilding(cityCore.transform, coreRenderer, 260f));
    }

    private void CreateHero()
    {
        GameObject heroObject = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        heroObject.name = "Superhero";
        heroObject.transform.position = new Vector3(0f, 1f, -6f);
        heroObject.transform.localScale = new Vector3(1.2f, 1.2f, 1.2f);
        heroObject.GetComponent<Renderer>().material = heroMaterial;
        hero = heroObject.transform;

        GameObject cape = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cape.name = "Hero Cape";
        cape.transform.SetParent(hero, false);
        cape.transform.localPosition = new Vector3(0f, 0.1f, -0.7f);
        cape.transform.localScale = new Vector3(0.9f, 1.2f, 0.08f);
        cape.GetComponent<Renderer>().material = capeMaterial;
    }

    private void CreateHud()
    {
        Canvas canvas = new GameObject("Superhero City Defense HUD").AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.gameObject.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        canvas.gameObject.AddComponent<GraphicRaycaster>();

        Font font = GetBuiltInFont();
        statusText = CreateText(canvas.transform, "Status Text", font, TextAnchor.UpperLeft, new Vector2(18f, -18f), new Vector2(640f, 150f), 22);
        shopText = CreateText(canvas.transform, "Shop Text", font, TextAnchor.LowerLeft, new Vector2(18f, 18f), new Vector2(900f, 120f), 18);
        messageText = CreateText(canvas.transform, "Message Text", font, TextAnchor.UpperCenter, new Vector2(0f, -18f), new Vector2(850f, 90f), 24);
        messageText.color = new Color(1f, 0.95f, 0.25f);
    }

    private static Font GetBuiltInFont()
    {
        Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        if (font == null)
        {
            font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        }

        return font;
    }

    private static Text CreateText(Transform parent, string name, Font font, TextAnchor alignment, Vector2 anchoredPosition, Vector2 size, int fontSize)
    {
        GameObject textObject = new GameObject(name);
        textObject.transform.SetParent(parent, false);

        RectTransform rectTransform = textObject.AddComponent<RectTransform>();
        rectTransform.sizeDelta = size;
        rectTransform.anchoredPosition = anchoredPosition;

        if (alignment == TextAnchor.UpperLeft)
        {
            rectTransform.anchorMin = new Vector2(0f, 1f);
            rectTransform.anchorMax = new Vector2(0f, 1f);
            rectTransform.pivot = new Vector2(0f, 1f);
        }
        else if (alignment == TextAnchor.LowerLeft)
        {
            rectTransform.anchorMin = new Vector2(0f, 0f);
            rectTransform.anchorMax = new Vector2(0f, 0f);
            rectTransform.pivot = new Vector2(0f, 0f);
        }
        else
        {
            rectTransform.anchorMin = new Vector2(0.5f, 1f);
            rectTransform.anchorMax = new Vector2(0.5f, 1f);
            rectTransform.pivot = new Vector2(0.5f, 1f);
        }

        Text text = textObject.AddComponent<Text>();
        text.font = font;
        text.fontSize = fontSize;
        text.alignment = alignment;
        text.color = Color.white;
        text.raycastTarget = false;
        return text;
    }

    private void HandleHeroInput(float deltaTime)
    {
        Keyboard keyboard = Keyboard.current;
        if (keyboard == null)
        {
            return;
        }

        Vector3 movement = Vector3.zero;
        if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed)
        {
            movement.z += 1f;
        }

        if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed)
        {
            movement.z -= 1f;
        }

        if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed)
        {
            movement.x += 1f;
        }

        if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed)
        {
            movement.x -= 1f;
        }

        if (movement.sqrMagnitude > 1f)
        {
            movement.Normalize();
        }

        float currentSpeed = speedBoostTimer > 0f ? 13.5f : 8f;
        hero.position += movement * currentSpeed * deltaTime;
        hero.position = new Vector3(
            Mathf.Clamp(hero.position.x, -ArenaHalfSize + 2f, ArenaHalfSize - 2f),
            hero.position.y,
            Mathf.Clamp(hero.position.z, -ArenaHalfSize + 2f, ArenaHalfSize - 2f));

        UpdateAimDirection(movement);

        if (keyboard.spaceKey.isPressed || IsMouseFirePressed())
        {
            FireBlast();
        }
    }

    private void UpdateAimDirection(Vector3 fallbackMovement)
    {
        Mouse mouse = Mouse.current;
        if (mouse != null && mainCamera != null)
        {
            Ray ray = mainCamera.ScreenPointToRay(mouse.position.ReadValue());
            Plane groundPlane = new Plane(Vector3.up, Vector3.zero);
            if (groundPlane.Raycast(ray, out float distance))
            {
                Vector3 targetPoint = ray.GetPoint(distance);
                Vector3 direction = targetPoint - hero.position;
                direction.y = 0f;

                if (direction.sqrMagnitude > 0.05f)
                {
                    aimDirection = direction.normalized;
                    hero.rotation = Quaternion.LookRotation(aimDirection, Vector3.up);
                    return;
                }
            }
        }

        if (fallbackMovement.sqrMagnitude > 0.05f)
        {
            aimDirection = fallbackMovement.normalized;
            hero.rotation = Quaternion.LookRotation(aimDirection, Vector3.up);
        }
    }

    private static bool IsMouseFirePressed()
    {
        Mouse mouse = Mouse.current;
        return mouse != null && mouse.leftButton.isPressed;
    }

    private void HandlePowerupInput()
    {
        Keyboard keyboard = Keyboard.current;
        if (keyboard == null)
        {
            return;
        }

        if (WasPressed(keyboard.digit1Key, keyboard.numpad1Key))
        {
            BuyPowerup("Speed Boost", 75, () =>
            {
                speedBoostTimer = SpeedBoostDurationSeconds;
                ShowMessage("Speed Boost active! Fly faster for 30 seconds.");
            });
        }
        else if (WasPressed(keyboard.digit2Key, keyboard.numpad2Key))
        {
            BuyPowerup("Rapid Blasts", 100, () =>
            {
                rapidBlastTimer = RapidBlastDurationSeconds;
                ShowMessage("Rapid Blasts active! Fire faster and hit harder.");
            });
        }
        else if (WasPressed(keyboard.digit3Key, keyboard.numpad3Key))
        {
            BuyPowerup("City Shield", 150, () =>
            {
                cityShieldTimer = CityShieldDurationSeconds;
                ShowMessage("City Shield active! Buildings are protected.");
            });
        }
        else if (WasPressed(keyboard.digit4Key, keyboard.numpad4Key))
        {
            BuyPowerup("Repair Drones", 125, () =>
            {
                foreach (CityBuilding building in buildings)
                {
                    building.Repair(45f);
                }

                ShowMessage("Repair Drones restored damaged city blocks.");
            });
        }
    }

    private static bool WasPressed(KeyControl primary, KeyControl secondary)
    {
        return primary.wasPressedThisFrame || secondary.wasPressedThisFrame;
    }

    private void BuyPowerup(string powerupName, int cost, System.Action applyPowerup)
    {
        if (money < cost)
        {
            ShowMessage($"{powerupName} costs ${cost}. Defeat more enemies to earn cash.");
            return;
        }

        money -= cost;
        applyPowerup();
    }

    private void FireBlast()
    {
        if (fireCooldownTimer > 0f)
        {
            return;
        }

        float cooldown = rapidBlastTimer > 0f ? 0.12f : 0.34f;
        float damage = rapidBlastTimer > 0f ? 42f : 24f;
        fireCooldownTimer = cooldown;

        GameObject blastObject = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        blastObject.name = "Hero Energy Blast";
        blastObject.transform.position = hero.position + Vector3.up * 0.45f + aimDirection * 1.2f;
        blastObject.transform.localScale = Vector3.one * 0.45f;
        blastObject.GetComponent<Renderer>().material = blastMaterial;

        blasts.Add(new HeroBlast(blastObject.transform, aimDirection, damage));
    }

    private void UpdateWaveTimer(float deltaTime)
    {
        nextWaveTimer -= deltaTime;
        if (nextWaveTimer > 0f)
        {
            return;
        }

        SpawnWave();
        nextWaveTimer = WaveIntervalSeconds;
    }

    private void SpawnWave()
    {
        waveNumber++;
        int enemyCount = 4 + waveNumber * 2;
        float enemyHealth = 50f + waveNumber * 14f;

        for (int i = 0; i < enemyCount; i++)
        {
            float side = Random.Range(0, 4);
            Vector3 spawnPosition;
            if (side < 1f)
            {
                spawnPosition = new Vector3(-ArenaHalfSize, 1f, Random.Range(-ArenaHalfSize, ArenaHalfSize));
            }
            else if (side < 2f)
            {
                spawnPosition = new Vector3(ArenaHalfSize, 1f, Random.Range(-ArenaHalfSize, ArenaHalfSize));
            }
            else if (side < 3f)
            {
                spawnPosition = new Vector3(Random.Range(-ArenaHalfSize, ArenaHalfSize), 1f, -ArenaHalfSize);
            }
            else
            {
                spawnPosition = new Vector3(Random.Range(-ArenaHalfSize, ArenaHalfSize), 1f, ArenaHalfSize);
            }

            SpawnEnemy(spawnPosition, enemyHealth);
        }

        money += 40 + waveNumber * 10;
        ShowMessage($"Wave {waveNumber}: villains are attacking the city! Bonus funding awarded.");
    }

    private void SpawnEnemy(Vector3 spawnPosition, float health)
    {
        GameObject enemyObject = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        enemyObject.name = "City Raider";
        enemyObject.transform.position = spawnPosition;
        enemyObject.transform.localScale = new Vector3(1.15f, 1.15f, 1.15f);

        Renderer renderer = enemyObject.GetComponent<Renderer>();
        renderer.material = new Material(enemyMaterial);

        enemies.Add(new EnemyRaider(
            enemyObject.transform,
            renderer,
            health,
            2.4f + waveNumber * 0.08f,
            8f + waveNumber * 1.5f,
            22 + waveNumber * 3));
    }

    private void UpdateBlasts(float deltaTime)
    {
        for (int i = blasts.Count - 1; i >= 0; i--)
        {
            HeroBlast blast = blasts[i];
            blast.Transform.position += blast.Direction * 25f * deltaTime;
            blast.Lifetime -= deltaTime;

            bool shouldRemove = blast.Lifetime <= 0f
                || Mathf.Abs(blast.Transform.position.x) > ArenaHalfSize + 5f
                || Mathf.Abs(blast.Transform.position.z) > ArenaHalfSize + 5f;

            if (!shouldRemove)
            {
                for (int enemyIndex = enemies.Count - 1; enemyIndex >= 0; enemyIndex--)
                {
                    EnemyRaider enemy = enemies[enemyIndex];
                    if ((enemy.Transform.position - blast.Transform.position).sqrMagnitude > 1.7f)
                    {
                        continue;
                    }

                    enemy.TakeDamage(blast.Damage);
                    shouldRemove = true;

                    if (enemy.Health <= 0f)
                    {
                        money += enemy.Reward;
                        Destroy(enemy.Transform.gameObject);
                        enemies.RemoveAt(enemyIndex);
                    }

                    break;
                }
            }

            if (shouldRemove)
            {
                Destroy(blast.Transform.gameObject);
                blasts.RemoveAt(i);
            }
        }
    }

    private void UpdateEnemies(float deltaTime)
    {
        for (int i = enemies.Count - 1; i >= 0; i--)
        {
            EnemyRaider enemy = enemies[i];
            CityBuilding target = FindClosestLivingBuilding(enemy.Transform.position);
            if (target == null)
            {
                TriggerGameOver();
                return;
            }

            Vector3 direction = target.Position - enemy.Transform.position;
            direction.y = 0f;
            float distance = direction.magnitude;

            if (distance > enemy.AttackRange)
            {
                Vector3 normalizedDirection = direction.normalized;
                enemy.Transform.position += normalizedDirection * enemy.Speed * deltaTime;
                enemy.Transform.rotation = Quaternion.LookRotation(normalizedDirection, Vector3.up);
                continue;
            }

            float damage = cityShieldTimer > 0f ? 0f : enemy.DamagePerSecond * deltaTime;
            target.Damage(damage);

            if (cityShieldTimer > 0f)
            {
                PulseShield(enemy.Transform.position);
            }

            if (GetCityHealthPercent() <= 0f)
            {
                TriggerGameOver();
                return;
            }
        }
    }

    private CityBuilding FindClosestLivingBuilding(Vector3 position)
    {
        CityBuilding closestBuilding = null;
        float closestDistance = float.MaxValue;

        foreach (CityBuilding building in buildings)
        {
            if (building.Health <= 0f)
            {
                continue;
            }

            float distance = (building.Position - position).sqrMagnitude;
            if (distance >= closestDistance)
            {
                continue;
            }

            closestDistance = distance;
            closestBuilding = building;
        }

        return closestBuilding;
    }

    private void PulseShield(Vector3 position)
    {
        if (Random.value > 0.08f)
        {
            return;
        }

        GameObject shieldPulse = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        shieldPulse.name = "Shield Pulse";
        shieldPulse.transform.position = position + Vector3.up * 0.3f;
        shieldPulse.transform.localScale = Vector3.one * 1.8f;
        shieldPulse.GetComponent<Renderer>().material = shieldMaterial;
        Destroy(shieldPulse, 0.22f);
    }

    private void UpdateCamera()
    {
        if (mainCamera == null || hero == null)
        {
            return;
        }

        Vector3 target = hero.position + new Vector3(0f, 36f, -28f);
        mainCamera.transform.position = Vector3.Lerp(mainCamera.transform.position, target, Time.deltaTime * 2.5f);
    }

    private void UpdateHud()
    {
        float cityPercent = Mathf.RoundToInt(GetCityHealthPercent() * 100f);
        string waveTimerText = nextWaveTimer > 0f ? FormatTime(nextWaveTimer) : "now";
        string powerups = $"Speed {FormatPowerup(speedBoostTimer)}  Rapid {FormatPowerup(rapidBlastTimer)}  Shield {FormatPowerup(cityShieldTimer)}";

        statusText.text =
            $"SUPERHERO CITY DEFENSE\n" +
            $"City Integrity: {cityPercent}%\n" +
            $"Money: ${money}\n" +
            $"Wave: {waveNumber}   Enemies: {enemies.Count}   Next attack: {waveTimerText}\n" +
            $"{powerups}";

        shopText.text =
            "Move: WASD/Arrows   Aim: Mouse   Blast: Left Mouse or Space\n" +
            "Powerup Shop: [1] Speed Boost $75   [2] Rapid Blasts $100   [3] City Shield $150   [4] Repair Drones $125";

        if (gameOver)
        {
            messageText.text = "CITY OVERRUN! Press R to restart and defend it again.";
        }
        else
        {
            messageText.text = messageTimer > 0f ? currentMessage : string.Empty;
        }
    }

    private static string FormatTime(float seconds)
    {
        int totalSeconds = Mathf.CeilToInt(seconds);
        int minutes = totalSeconds / 60;
        int remainingSeconds = totalSeconds % 60;
        return $"{minutes:0}:{remainingSeconds:00}";
    }

    private static string FormatPowerup(float timer)
    {
        return timer > 0f ? $"{Mathf.CeilToInt(timer)}s" : "ready";
    }

    private float GetCityHealthPercent()
    {
        float current = 0f;
        float maximum = 0f;

        foreach (CityBuilding building in buildings)
        {
            current += building.Health;
            maximum += building.MaximumHealth;
        }

        return maximum <= 0f ? 0f : Mathf.Clamp01(current / maximum);
    }

    private void ShowMessage(string message)
    {
        currentMessage = message;
        messageTimer = 5f;
    }

    private void TriggerGameOver()
    {
        gameOver = true;
        ShowMessage("The city has fallen.");
    }

    private void HandleRestartInput()
    {
        Keyboard keyboard = Keyboard.current;
        if (keyboard == null || !keyboard.rKey.wasPressedThisFrame)
        {
            return;
        }

        UnityEngine.SceneManagement.SceneManager.LoadScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene().buildIndex);
    }

    private sealed class CityBuilding
    {
        private readonly Transform transform;
        private readonly Renderer renderer;
        private readonly Color healthyColor;
        private readonly Vector3 originalScale;

        public CityBuilding(Transform transform, Renderer renderer, float maximumHealth)
        {
            this.transform = transform;
            this.renderer = renderer;
            MaximumHealth = maximumHealth;
            Health = maximumHealth;
            healthyColor = renderer.material.color;
            originalScale = transform.localScale;
        }

        public float MaximumHealth { get; }
        public float Health { get; private set; }
        public Vector3 Position => transform.position;

        public void Damage(float amount)
        {
            if (amount <= 0f || Health <= 0f)
            {
                return;
            }

            Health = Mathf.Max(0f, Health - amount);
            RefreshVisuals();
        }

        public void Repair(float amount)
        {
            if (amount <= 0f)
            {
                return;
            }

            Health = Mathf.Min(MaximumHealth, Health + amount);
            RefreshVisuals();
        }

        private void RefreshVisuals()
        {
            float healthPercent = MaximumHealth <= 0f ? 0f : Health / MaximumHealth;
            renderer.material.color = Health <= 0f
                ? new Color(0.08f, 0.08f, 0.08f)
                : Color.Lerp(new Color(0.9f, 0.18f, 0.1f), healthyColor, healthPercent);

            transform.localScale = new Vector3(
                originalScale.x,
                Mathf.Lerp(originalScale.y * 0.15f, originalScale.y, healthPercent),
                originalScale.z);
        }
    }

    private sealed class EnemyRaider
    {
        private readonly Renderer renderer;

        public EnemyRaider(Transform transform, Renderer renderer, float health, float speed, float damagePerSecond, int reward)
        {
            Transform = transform;
            this.renderer = renderer;
            MaximumHealth = health;
            Health = health;
            Speed = speed;
            DamagePerSecond = damagePerSecond;
            Reward = reward;
        }

        public Transform Transform { get; }
        public float MaximumHealth { get; }
        public float Health { get; private set; }
        public float Speed { get; }
        public float DamagePerSecond { get; }
        public float AttackRange => 2.2f;
        public int Reward { get; }

        public void TakeDamage(float damage)
        {
            Health = Mathf.Max(0f, Health - damage);
            float healthPercent = MaximumHealth <= 0f ? 0f : Health / MaximumHealth;
            renderer.material.color = Color.Lerp(new Color(0.08f, 0.02f, 0.02f), new Color(0.8f, 0.08f, 0.08f), healthPercent);
        }
    }

    private sealed class HeroBlast
    {
        public HeroBlast(Transform transform, Vector3 direction, float damage)
        {
            Transform = transform;
            Direction = direction.sqrMagnitude <= 0f ? Vector3.forward : direction.normalized;
            Damage = damage;
            Lifetime = 2.6f;
        }

        public Transform Transform { get; }
        public Vector3 Direction { get; }
        public float Damage { get; }
        public float Lifetime { get; set; }
    }
}
