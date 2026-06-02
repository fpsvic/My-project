using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public sealed class JungleCatsGameBootstrap : MonoBehaviour
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void CreateGame()
    {
        if (Object.FindFirstObjectByType<JungleCatsGameBootstrap>() != null)
        {
            return;
        }

        var root = new GameObject("Jungle Cats Survival");
        root.AddComponent<JungleCatsGameBootstrap>();
    }

    private readonly List<CatAgent> cats = new List<CatAgent>();
    private readonly List<PredatorAgent> predators = new List<PredatorAgent>();
    private readonly List<PreyAgent> prey = new List<PreyAgent>();
    private readonly List<Material> runtimeMaterials = new List<Material>();

    private CatAgent toe;
    private CatAgent seven;
    private Camera gameCamera;
    private Text hudText;
    private Text messageText;
    private float elapsedTime;
    private float predatorWaveTimer;
    private int mealsEaten;
    private int predatorsDefeated;
    private bool gameOver;

    private Material grassMaterial;
    private Material darkLeafMaterial;
    private Material lightLeafMaterial;
    private Material trunkMaterial;
    private Material rockMaterial;
    private Material toeBlackMaterial;
    private Material toeWhiteMaterial;
    private Material sevenFurMaterial;
    private Material sevenSpotMaterial;
    private Material mouseMaterial;
    private Material rabbitMaterial;
    private Material pantherMaterial;
    private Material wolfMaterial;
    private Material foxMaterial;
    private Material hyenaMaterial;
    private Material dangerMaterial;

    private const float ArenaRadius = 38f;
    private const float CatHeight = 0.45f;

    private void Start()
    {
        Random.InitState(2307);
        CreateMaterials();
        ConfigureScene();
        BuildJungle();
        CreateCats();
        SpawnStartingCreatures();
        CreateHud();
    }

    private void Update()
    {
        if (gameOver)
        {
            if (GameInput.GetKeyDown(KeyCode.R))
            {
                ResetGame();
            }

            return;
        }

        float dt = Time.deltaTime;
        elapsedTime += dt;
        predatorWaveTimer += dt;

        UpdateNeeds(dt);
        UpdatePlayer(dt);
        UpdateSeven(dt);
        UpdatePrey(dt);
        UpdatePredators(dt);
        MaintainPopulation();
        UpdateHud();
        CheckGameOver();
    }

    private void LateUpdate()
    {
        UpdateCamera();
    }

    private void OnDestroy()
    {
        for (int i = 0; i < runtimeMaterials.Count; i++)
        {
            if (runtimeMaterials[i] != null)
            {
                Destroy(runtimeMaterials[i]);
            }
        }
    }

    private void CreateMaterials()
    {
        grassMaterial = CreateMaterial("Deep Jungle Grass", new Color(0.10f, 0.33f, 0.12f));
        darkLeafMaterial = CreateMaterial("Dark Jungle Leaves", new Color(0.04f, 0.25f, 0.08f));
        lightLeafMaterial = CreateMaterial("Sunlit Jungle Leaves", new Color(0.20f, 0.48f, 0.13f));
        trunkMaterial = CreateMaterial("Rainforest Bark", new Color(0.30f, 0.18f, 0.08f));
        rockMaterial = CreateMaterial("Mossy Stone", new Color(0.28f, 0.31f, 0.25f));
        toeBlackMaterial = CreateMaterial("Toe Tuxedo Black", new Color(0.015f, 0.014f, 0.016f));
        toeWhiteMaterial = CreateMaterial("Toe Tuxedo White", new Color(0.92f, 0.90f, 0.84f));
        sevenFurMaterial = CreateMaterial("Seven Brown Tabby Fur", new Color(0.47f, 0.29f, 0.13f));
        sevenSpotMaterial = CreateMaterial("Seven Dark Spots", new Color(0.12f, 0.07f, 0.035f));
        mouseMaterial = CreateMaterial("Mouse Grey", new Color(0.40f, 0.39f, 0.36f));
        rabbitMaterial = CreateMaterial("Rabbit Tan", new Color(0.72f, 0.62f, 0.49f));
        pantherMaterial = CreateMaterial("Panther Night Fur", new Color(0.02f, 0.018f, 0.02f));
        wolfMaterial = CreateMaterial("Wolf Pack Grey", new Color(0.36f, 0.39f, 0.42f));
        foxMaterial = CreateMaterial("Fox Rust", new Color(0.86f, 0.36f, 0.08f));
        hyenaMaterial = CreateMaterial("Hyena Spotted Tan", new Color(0.58f, 0.45f, 0.25f));
        dangerMaterial = CreateMaterial("Warning Red", new Color(0.95f, 0.12f, 0.08f));
    }

    private Material CreateMaterial(string materialName, Color color)
    {
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
        {
            shader = Shader.Find("Standard");
        }

        var material = new Material(shader)
        {
            name = materialName,
            color = color
        };

        if (material.HasProperty("_BaseColor"))
        {
            material.SetColor("_BaseColor", color);
        }

        runtimeMaterials.Add(material);
        return material;
    }

    private void ConfigureScene()
    {
        RenderSettings.fog = true;
        RenderSettings.fogColor = new Color(0.08f, 0.18f, 0.10f);
        RenderSettings.fogDensity = 0.018f;
        RenderSettings.ambientLight = new Color(0.28f, 0.34f, 0.24f);

        Light[] lights = Object.FindObjectsByType<Light>(FindObjectsSortMode.None);
        for (int i = 0; i < lights.Length; i++)
        {
            if (lights[i].type == LightType.Directional)
            {
                lights[i].transform.rotation = Quaternion.Euler(48f, -35f, 0f);
                lights[i].intensity = 1.1f;
                lights[i].color = new Color(1f, 0.92f, 0.75f);
                return;
            }
        }

        var sunObject = new GameObject("Jungle Sun");
        var sun = sunObject.AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.transform.rotation = Quaternion.Euler(48f, -35f, 0f);
        sun.intensity = 1.1f;
        sun.color = new Color(1f, 0.92f, 0.75f);
    }

    private void BuildJungle()
    {
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Jungle Floor";
        ground.transform.localScale = new Vector3(8.2f, 1f, 8.2f);
        SetMaterial(ground, grassMaterial);

        for (int i = 0; i < 55; i++)
        {
            Vector3 position = RandomPoint(8f, ArenaRadius);
            float trunkHeight = Random.Range(3.5f, 7.5f);
            GameObject trunk = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            trunk.name = "Jungle Tree Trunk";
            trunk.transform.position = new Vector3(position.x, trunkHeight * 0.5f, position.z);
            trunk.transform.localScale = new Vector3(Random.Range(0.28f, 0.55f), trunkHeight * 0.5f, Random.Range(0.28f, 0.55f));
            SetMaterial(trunk, trunkMaterial);

            GameObject canopy = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            canopy.name = "Jungle Tree Canopy";
            canopy.transform.position = new Vector3(position.x, trunkHeight + Random.Range(0.4f, 1.2f), position.z);
            float canopyScale = Random.Range(2.6f, 5.2f);
            canopy.transform.localScale = new Vector3(canopyScale, Random.Range(1.5f, 2.4f), canopyScale);
            SetMaterial(canopy, Random.value > 0.45f ? darkLeafMaterial : lightLeafMaterial);
        }

        for (int i = 0; i < 18; i++)
        {
            GameObject rock = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            rock.name = "Mossy Jungle Rock";
            rock.transform.position = RandomPoint(4f, ArenaRadius - 3f) + Vector3.up * 0.18f;
            rock.transform.localScale = new Vector3(Random.Range(0.8f, 2.2f), Random.Range(0.25f, 0.75f), Random.Range(0.8f, 2.1f));
            SetMaterial(rock, rockMaterial);
        }

        CreateCampMarker("Safe Den", new Vector3(0f, 0.02f, -5f));
    }

    private void CreateCampMarker(string markerName, Vector3 position)
    {
        GameObject den = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        den.name = markerName;
        den.transform.position = position;
        den.transform.localScale = new Vector3(3f, 0.04f, 3f);
        SetMaterial(den, CreateMaterial("Den Leaf Bed", new Color(0.14f, 0.42f, 0.12f)));
        CreateWorldLabel(markerName, den.transform, Vector3.up * 0.45f, Color.white, 0.24f);
    }

    private void CreateCats()
    {
        toe = CreateCat("Toe", "Tuxedo cat - playable", new Vector3(-1.5f, 0f, -2f), true);
        seven = CreateCat("Seven", "Brown spotted tabby - companion", new Vector3(1.5f, 0f, -2.3f), false);
        cats.Add(toe);
        cats.Add(seven);

        gameCamera = Camera.main;
        if (gameCamera == null)
        {
            GameObject cameraObject = new GameObject("Main Camera");
            gameCamera = cameraObject.AddComponent<Camera>();
            cameraObject.tag = "MainCamera";
            cameraObject.AddComponent<AudioListener>();
        }

        gameCamera.fieldOfView = 58f;
    }

    private CatAgent CreateCat(string catName, string role, Vector3 position, bool playerControlled)
    {
        var root = new GameObject(catName + " - " + role);
        root.transform.position = position + Vector3.up * CatHeight;

        GameObject body = AddPrimitive(root.transform, PrimitiveType.Capsule, "Body", Vector3.zero, new Vector3(0.42f, 0.42f, 0.72f), Quaternion.Euler(90f, 0f, 0f));
        GameObject head = AddPrimitive(root.transform, PrimitiveType.Sphere, "Head", new Vector3(0f, 0.08f, 0.58f), new Vector3(0.5f, 0.42f, 0.45f), Quaternion.identity);
        GameObject tail = AddPrimitive(root.transform, PrimitiveType.Cylinder, "Tail", new Vector3(0f, 0.16f, -0.72f), new Vector3(0.10f, 0.45f, 0.10f), Quaternion.Euler(58f, 0f, 0f));

        SetMaterial(body, playerControlled ? toeBlackMaterial : sevenFurMaterial);
        SetMaterial(head, playerControlled ? toeBlackMaterial : sevenFurMaterial);
        SetMaterial(tail, playerControlled ? toeBlackMaterial : sevenFurMaterial);

        if (playerControlled)
        {
            GameObject chest = AddPrimitive(root.transform, PrimitiveType.Sphere, "White Tuxedo Chest", new Vector3(0f, -0.03f, 0.26f), new Vector3(0.28f, 0.22f, 0.26f), Quaternion.identity);
            GameObject muzzle = AddPrimitive(root.transform, PrimitiveType.Sphere, "White Tuxedo Muzzle", new Vector3(0f, 0.03f, 0.83f), new Vector3(0.26f, 0.15f, 0.16f), Quaternion.identity);
            GameObject frontPaws = AddPrimitive(root.transform, PrimitiveType.Cube, "White Front Paws", new Vector3(0f, -0.32f, 0.34f), new Vector3(0.58f, 0.12f, 0.20f), Quaternion.identity);
            SetMaterial(chest, toeWhiteMaterial);
            SetMaterial(muzzle, toeWhiteMaterial);
            SetMaterial(frontPaws, toeWhiteMaterial);
        }
        else
        {
            for (int i = 0; i < 12; i++)
            {
                float side = i % 2 == 0 ? -1f : 1f;
                float z = Random.Range(-0.35f, 0.45f);
                float y = Random.Range(-0.03f, 0.22f);
                GameObject spot = AddPrimitive(root.transform, PrimitiveType.Sphere, "Tabby Spot", new Vector3(side * 0.34f, y, z), new Vector3(0.11f, 0.07f, 0.11f), Quaternion.identity);
                SetMaterial(spot, sevenSpotMaterial);
            }

            GameObject foreheadStripe = AddPrimitive(root.transform, PrimitiveType.Cube, "Tabby Forehead Stripe", new Vector3(0f, 0.18f, 0.82f), new Vector3(0.08f, 0.04f, 0.22f), Quaternion.identity);
            SetMaterial(foreheadStripe, sevenSpotMaterial);
        }

        GameObject leftEar = AddPrimitive(root.transform, PrimitiveType.Sphere, "Left Ear", new Vector3(-0.19f, 0.38f, 0.55f), new Vector3(0.16f, 0.22f, 0.10f), Quaternion.identity);
        GameObject rightEar = AddPrimitive(root.transform, PrimitiveType.Sphere, "Right Ear", new Vector3(0.19f, 0.38f, 0.55f), new Vector3(0.16f, 0.22f, 0.10f), Quaternion.identity);
        SetMaterial(leftEar, playerControlled ? toeBlackMaterial : sevenFurMaterial);
        SetMaterial(rightEar, playerControlled ? toeBlackMaterial : sevenFurMaterial);

        CreateWorldLabel(catName, root.transform, Vector3.up * 0.92f, playerControlled ? Color.white : new Color(1f, 0.72f, 0.38f), 0.23f);

        return new CatAgent(root.transform, catName, playerControlled);
    }

    private GameObject AddPrimitive(Transform parent, PrimitiveType type, string objectName, Vector3 localPosition, Vector3 localScale, Quaternion localRotation)
    {
        GameObject primitive = GameObject.CreatePrimitive(type);
        primitive.name = objectName;
        primitive.transform.SetParent(parent, false);
        primitive.transform.localPosition = localPosition;
        primitive.transform.localRotation = localRotation;
        primitive.transform.localScale = localScale;
        return primitive;
    }

    private void SpawnStartingCreatures()
    {
        for (int i = 0; i < 16; i++)
        {
            SpawnPrey(Random.value > 0.45f ? PreyKind.Mouse : PreyKind.Rabbit);
        }

        SpawnPredator(PredatorType.Panther, RandomPoint(20f, ArenaRadius - 2f));
        SpawnPredator(PredatorType.Fox, RandomPoint(17f, ArenaRadius - 2f));
        SpawnPredator(PredatorType.Fox, RandomPoint(17f, ArenaRadius - 2f));
        SpawnPredator(PredatorType.Hyena, RandomPoint(20f, ArenaRadius - 2f));

        Vector3 packCenter = RandomPoint(22f, ArenaRadius - 2f);
        for (int i = 0; i < 4; i++)
        {
            SpawnPredator(PredatorType.Wolf, packCenter + new Vector3(Random.Range(-2.2f, 2.2f), 0f, Random.Range(-2.2f, 2.2f)));
        }
    }

    private void CreateHud()
    {
        var canvasObject = new GameObject("Jungle Cats HUD");
        var canvas = canvasObject.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvasObject.AddComponent<CanvasScaler>();
        canvasObject.AddComponent<GraphicRaycaster>();

        Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        if (font == null)
        {
            font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        }

        hudText = CreateHudText(canvasObject.transform, "Status", font, new Vector2(16f, -14f), TextAnchor.UpperLeft, 18);
        messageText = CreateHudText(canvasObject.transform, "Message", font, new Vector2(0f, 72f), TextAnchor.UpperCenter, 24);
        messageText.color = new Color(1f, 0.92f, 0.55f);
        messageText.text = "Toe and Seven must survive the jungle. WASD move, Space pounce, Shift hiss/scare, R restart.";
        UpdateHud();
    }

    private Text CreateHudText(Transform parent, string objectName, Font font, Vector2 anchoredPosition, TextAnchor alignment, int fontSize)
    {
        var textObject = new GameObject(objectName);
        textObject.transform.SetParent(parent, false);
        var rect = textObject.AddComponent<RectTransform>();
        rect.anchorMin = alignment == TextAnchor.UpperLeft ? new Vector2(0f, 1f) : new Vector2(0.5f, 1f);
        rect.anchorMax = rect.anchorMin;
        rect.pivot = alignment == TextAnchor.UpperLeft ? new Vector2(0f, 1f) : new Vector2(0.5f, 1f);
        rect.anchoredPosition = anchoredPosition;
        rect.sizeDelta = alignment == TextAnchor.UpperLeft ? new Vector2(620f, 220f) : new Vector2(1000f, 80f);

        var text = textObject.AddComponent<Text>();
        text.font = font;
        text.fontSize = fontSize;
        text.alignment = alignment;
        text.color = Color.white;
        text.raycastTarget = false;
        return text;
    }

    private void UpdateNeeds(float dt)
    {
        for (int i = 0; i < cats.Count; i++)
        {
            CatAgent cat = cats[i];
            if (!cat.IsAlive)
            {
                continue;
            }

            cat.Hunger = Mathf.Max(0f, cat.Hunger - dt * 2.1f);
            if (cat.Hunger <= 0f)
            {
                cat.Health = Mathf.Max(0f, cat.Health - dt * 5f);
            }
            else if (cat.Hunger > 82f && cat.Health < 100f)
            {
                cat.Health = Mathf.Min(100f, cat.Health + dt * 1.5f);
            }
        }
    }

    private void UpdatePlayer(float dt)
    {
        if (toe == null || !toe.IsAlive)
        {
            return;
        }

        Vector3 input = Vector3.zero;
        if (GameInput.GetKey(KeyCode.W) || GameInput.GetKey(KeyCode.UpArrow))
        {
            input += Vector3.forward;
        }

        if (GameInput.GetKey(KeyCode.S) || GameInput.GetKey(KeyCode.DownArrow))
        {
            input += Vector3.back;
        }

        if (GameInput.GetKey(KeyCode.A) || GameInput.GetKey(KeyCode.LeftArrow))
        {
            input += Vector3.left;
        }

        if (GameInput.GetKey(KeyCode.D) || GameInput.GetKey(KeyCode.RightArrow))
        {
            input += Vector3.right;
        }

        MoveCat(toe, input, toe.Speed, dt);

        toe.AttackTimer -= dt;
        toe.ScareTimer -= dt;
        if (GameInput.GetKeyDown(KeyCode.Space))
        {
            CatAttack(toe, 2.25f, 28f);
        }

        if (GameInput.GetKeyDown(KeyCode.LeftShift) || GameInput.GetKeyDown(KeyCode.RightShift))
        {
            CatScare(toe, 5.5f, 36f);
        }
    }

    private void UpdateSeven(float dt)
    {
        if (seven == null || !seven.IsAlive)
        {
            return;
        }

        seven.AttackTimer -= dt;
        seven.ScareTimer -= dt;

        PredatorAgent threat = FindNearestPredator(seven.Position, 8f);
        if (threat != null)
        {
            Vector3 toThreat = threat.Position - seven.Position;
            if (toThreat.magnitude > 1.75f)
            {
                MoveCat(seven, toThreat, seven.Speed * 0.95f, dt);
            }

            if (toThreat.magnitude <= 2.2f)
            {
                CatAttack(seven, 2.05f, 22f);
            }
            else if (toThreat.magnitude <= 4.2f)
            {
                CatScare(seven, 4.4f, 22f);
            }

            return;
        }

        PreyAgent snack = seven.Hunger < 72f ? FindNearestPrey(seven.Position, 8f) : null;
        if (snack != null)
        {
            MoveCat(seven, snack.Position - seven.Position, seven.Speed * 0.85f, dt);
            if (Vector3.Distance(seven.Position, snack.Position) < 1.35f)
            {
                EatPrey(seven, snack);
            }

            return;
        }

        Vector3 desired = toe != null && toe.IsAlive ? toe.Position + new Vector3(1.5f, 0f, -1.2f) : Vector3.zero;
        Vector3 offset = desired - seven.Position;
        if (offset.magnitude > 1.4f)
        {
            MoveCat(seven, offset, seven.Speed * 0.82f, dt);
        }
    }

    private void MoveCat(CatAgent cat, Vector3 direction, float speed, float dt)
    {
        direction.y = 0f;
        if (direction.sqrMagnitude < 0.001f)
        {
            return;
        }

        Vector3 normalized = direction.normalized;
        cat.Transform.position = ClampToArena(cat.Transform.position + normalized * speed * dt);
        cat.Transform.rotation = Quaternion.Slerp(cat.Transform.rotation, Quaternion.LookRotation(normalized, Vector3.up), 12f * dt);
    }

    private void CatAttack(CatAgent cat, float range, float damage)
    {
        if (cat.AttackTimer > 0f)
        {
            return;
        }

        cat.AttackTimer = 0.65f;
        PredatorAgent targetPredator = FindNearestPredator(cat.Position + cat.Transform.forward * 0.65f, range);
        if (targetPredator != null)
        {
            targetPredator.Health -= damage;
            targetPredator.Courage -= damage * 0.35f;
            SetMessage(cat.Name + " pounced on a " + targetPredator.DisplayName + "!");
            if (targetPredator.Health <= 0f)
            {
                DefeatPredator(targetPredator, cat.Name + " drove off the " + targetPredator.DisplayName + "!");
            }

            return;
        }

        PreyAgent targetPrey = FindNearestPrey(cat.Position + cat.Transform.forward * 0.65f, range);
        if (targetPrey != null)
        {
            EatPrey(cat, targetPrey);
            return;
        }

        SetMessage(cat.Name + " swiped through the vines.");
    }

    private void CatScare(CatAgent cat, float range, float courageDamage)
    {
        if (cat.ScareTimer > 0f)
        {
            return;
        }

        cat.ScareTimer = 2.4f;
        int scared = 0;
        for (int i = predators.Count - 1; i >= 0; i--)
        {
            PredatorAgent predator = predators[i];
            if (predator.Health <= 0f || predator.Courage <= 0f)
            {
                continue;
            }

            if (Vector3.Distance(cat.Position, predator.Position) <= range)
            {
                float typeResistance = predator.Type == PredatorType.Panther ? 0.75f : 1f;
                predator.Courage -= courageDamage * typeResistance;
                predator.FleeDirection = (predator.Position - cat.Position).normalized;
                scared++;
                if (predator.Courage <= 0f)
                {
                    DefeatPredator(predator, cat.Name + " scared away a " + predator.DisplayName + "!");
                }
            }
        }

        if (scared > 0)
        {
            SetMessage(cat.Name + " hissed and scared " + scared + " predator" + (scared == 1 ? "." : "s."));
        }
        else
        {
            SetMessage(cat.Name + " hissed into the jungle.");
        }
    }

    private void UpdatePrey(float dt)
    {
        for (int i = prey.Count - 1; i >= 0; i--)
        {
            PreyAgent animal = prey[i];
            animal.WanderTimer -= dt;
            CatAgent closestCat = FindNearestCat(animal.Position, 7f);
            Vector3 direction;
            if (closestCat != null)
            {
                direction = animal.Position - closestCat.Position;
                animal.WanderTimer = 0.65f;
            }
            else
            {
                if (animal.WanderTimer <= 0f)
                {
                    animal.WanderDirection = Random.insideUnitSphere;
                    animal.WanderDirection.y = 0f;
                    if (animal.WanderDirection.sqrMagnitude < 0.001f)
                    {
                        animal.WanderDirection = Vector3.forward;
                    }

                    animal.WanderTimer = Random.Range(1f, 3.5f);
                }

                direction = animal.WanderDirection;
            }

            direction.y = 0f;
            if (direction.sqrMagnitude > 0.001f)
            {
                Vector3 normalized = direction.normalized;
                float speed = closestCat != null ? animal.Speed * 1.65f : animal.Speed;
                animal.Transform.position = ClampToArena(animal.Transform.position + normalized * speed * dt);
                animal.Transform.rotation = Quaternion.Slerp(animal.Transform.rotation, Quaternion.LookRotation(normalized, Vector3.up), 8f * dt);
            }

            CatAgent eater = FindNearestCat(animal.Position, 0.85f);
            if (eater != null)
            {
                EatPrey(eater, animal);
            }
        }
    }

    private void UpdatePredators(float dt)
    {
        for (int i = predators.Count - 1; i >= 0; i--)
        {
            PredatorAgent predator = predators[i];
            predator.AttackTimer -= dt;
            predator.Lifetime += dt;

            if (predator.Courage <= 0f || predator.Health <= 0f)
            {
                Vector3 flee = predator.FleeDirection.sqrMagnitude > 0.001f ? predator.FleeDirection.normalized : (predator.Position - Vector3.zero).normalized;
                predator.Transform.position = ClampToArena(predator.Transform.position + flee * predator.Speed * 1.65f * dt);
                if (Vector3.Distance(Vector3.zero, predator.Position) > ArenaRadius - 1f || predator.Lifetime > 50f)
                {
                    RemovePredator(predator);
                }

                continue;
            }

            CatAgent target = FindNearestCat(predator.Position, 60f);
            if (target == null)
            {
                continue;
            }

            Vector3 toTarget = target.Position - predator.Position;
            float distance = toTarget.magnitude;
            if (distance > 1.55f)
            {
                Vector3 direction = toTarget.normalized;
                float pursuitBoost = distance > 14f ? 1.15f : 1f;
                predator.Transform.position = ClampToArena(predator.Transform.position + direction * predator.Speed * pursuitBoost * dt);
                predator.Transform.rotation = Quaternion.Slerp(predator.Transform.rotation, Quaternion.LookRotation(direction, Vector3.up), 8f * dt);
            }
            else if (predator.AttackTimer <= 0f)
            {
                predator.AttackTimer = predator.AttackCooldown;
                target.Health = Mathf.Max(0f, target.Health - predator.Damage);
                target.Hunger = Mathf.Max(0f, target.Hunger - predator.Damage * 0.35f);
                SetMessage("A " + predator.DisplayName + " attacked " + target.Name + "!");
            }
        }
    }

    private void MaintainPopulation()
    {
        if (prey.Count < 10)
        {
            SpawnPrey(Random.value > 0.48f ? PreyKind.Mouse : PreyKind.Rabbit);
        }

        if (predatorWaveTimer > 28f && predators.Count < 10)
        {
            predatorWaveTimer = 0f;
            float roll = Random.value;
            if (roll < 0.23f)
            {
                SpawnPredator(PredatorType.Panther, RandomPoint(23f, ArenaRadius - 2f));
            }
            else if (roll < 0.55f)
            {
                Vector3 packCenter = RandomPoint(23f, ArenaRadius - 2f);
                for (int i = 0; i < 3; i++)
                {
                    SpawnPredator(PredatorType.Wolf, packCenter + new Vector3(Random.Range(-1.6f, 1.6f), 0f, Random.Range(-1.6f, 1.6f)));
                }
            }
            else if (roll < 0.77f)
            {
                SpawnPredator(PredatorType.Fox, RandomPoint(20f, ArenaRadius - 2f));
                SpawnPredator(PredatorType.Fox, RandomPoint(20f, ArenaRadius - 2f));
            }
            else
            {
                SpawnPredator(PredatorType.Hyena, RandomPoint(22f, ArenaRadius - 2f));
                SpawnPredator(PredatorType.Hyena, RandomPoint(22f, ArenaRadius - 2f));
            }
        }
    }

    private void SpawnPrey(PreyKind kind)
    {
        Vector3 position = RandomPoint(6f, ArenaRadius - 2f);
        var root = new GameObject(kind.ToString());
        root.transform.position = position + Vector3.up * 0.25f;

        if (kind == PreyKind.Mouse)
        {
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Sphere, "Mouse Body", Vector3.zero, new Vector3(0.32f, 0.18f, 0.45f), Quaternion.identity), mouseMaterial);
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Sphere, "Mouse Head", new Vector3(0f, 0.03f, 0.35f), new Vector3(0.22f, 0.16f, 0.18f), Quaternion.identity), mouseMaterial);
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Cylinder, "Mouse Tail", new Vector3(0f, 0f, -0.42f), new Vector3(0.035f, 0.28f, 0.035f), Quaternion.Euler(80f, 0f, 0f)), mouseMaterial);
            prey.Add(new PreyAgent(root.transform, kind, 24f, 1.65f));
        }
        else
        {
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Sphere, "Rabbit Body", Vector3.zero, new Vector3(0.48f, 0.28f, 0.58f), Quaternion.identity), rabbitMaterial);
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Sphere, "Rabbit Head", new Vector3(0f, 0.08f, 0.43f), new Vector3(0.30f, 0.25f, 0.24f), Quaternion.identity), rabbitMaterial);
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Cube, "Rabbit Ears", new Vector3(0f, 0.36f, 0.47f), new Vector3(0.36f, 0.45f, 0.08f), Quaternion.identity), rabbitMaterial);
            prey.Add(new PreyAgent(root.transform, kind, 42f, 2.05f));
        }
    }

    private void SpawnPredator(PredatorType type, Vector3 position)
    {
        var root = new GameObject(type.ToString());
        root.transform.position = ClampToArena(position + Vector3.up * 0.55f);

        Material material = pantherMaterial;
        float scale = 1f;
        float health = 70f;
        float courage = 70f;
        float speed = 3.1f;
        float damage = 14f;
        float attackCooldown = 1.25f;
        string label = "Panther";

        switch (type)
        {
            case PredatorType.Wolf:
                material = wolfMaterial;
                scale = 0.88f;
                health = 45f;
                courage = 52f;
                speed = 3.35f;
                damage = 10f;
                attackCooldown = 1.45f;
                label = "Wolf";
                break;
            case PredatorType.Fox:
                material = foxMaterial;
                scale = 0.70f;
                health = 32f;
                courage = 36f;
                speed = 3.65f;
                damage = 7f;
                attackCooldown = 1.1f;
                label = "Fox";
                break;
            case PredatorType.Hyena:
                material = hyenaMaterial;
                scale = 0.95f;
                health = 55f;
                courage = 58f;
                speed = 3.0f;
                damage = 12f;
                attackCooldown = 1.35f;
                label = "Hyena";
                break;
        }

        SetMaterial(AddPrimitive(root.transform, PrimitiveType.Capsule, "Predator Body", Vector3.zero, new Vector3(0.52f * scale, 0.50f * scale, 0.92f * scale), Quaternion.Euler(90f, 0f, 0f)), material);
        SetMaterial(AddPrimitive(root.transform, PrimitiveType.Sphere, "Predator Head", new Vector3(0f, 0.08f * scale, 0.68f * scale), new Vector3(0.43f * scale, 0.36f * scale, 0.36f * scale), Quaternion.identity), material);
        SetMaterial(AddPrimitive(root.transform, PrimitiveType.Cylinder, "Predator Tail", new Vector3(0f, 0.05f * scale, -0.78f * scale), new Vector3(0.10f * scale, 0.45f * scale, 0.10f * scale), Quaternion.Euler(75f, 0f, 0f)), material);

        if (type == PredatorType.Hyena)
        {
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Cube, "Hyena Dark Mane", new Vector3(0f, 0.35f, 0.02f), new Vector3(0.22f, 0.16f, 1.12f), Quaternion.identity), sevenSpotMaterial);
        }
        else if (type == PredatorType.Fox)
        {
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Sphere, "White Fox Tail Tip", new Vector3(0f, 0.06f, -1.1f * scale), new Vector3(0.17f, 0.13f, 0.17f), Quaternion.identity), toeWhiteMaterial);
        }
        else if (type == PredatorType.Wolf)
        {
            SetMaterial(AddPrimitive(root.transform, PrimitiveType.Cube, "Wolf Pack Mark", new Vector3(0f, 0.31f, 0.0f), new Vector3(0.16f, 0.10f, 0.78f), Quaternion.identity), dangerMaterial);
        }

        CreateWorldLabel(label, root.transform, Vector3.up * 1.02f, Color.red, 0.20f);
        predators.Add(new PredatorAgent(root.transform, type, label, health, courage, speed, damage, attackCooldown));
    }

    private void EatPrey(CatAgent cat, PreyAgent animal)
    {
        if (!prey.Contains(animal))
        {
            return;
        }

        cat.Hunger = Mathf.Min(100f, cat.Hunger + animal.FoodValue);
        cat.Health = Mathf.Min(100f, cat.Health + animal.FoodValue * 0.18f);
        mealsEaten++;
        SetMessage(cat.Name + " caught a " + animal.Kind.ToString().ToLowerInvariant() + " and ate.");
        prey.Remove(animal);
        Destroy(animal.Transform.gameObject);
    }

    private void DefeatPredator(PredatorAgent predator, string message)
    {
        if (!predators.Contains(predator) || predator.Health <= 0f || predator.Courage <= 0f)
        {
            return;
        }

        predatorsDefeated++;
        predator.Health = 0f;
        predator.Courage = 0f;
        predator.FleeDirection = predator.Position.sqrMagnitude > 0.001f ? predator.Position.normalized : Vector3.forward;
        SetMessage(message);
    }

    private void RemovePredator(PredatorAgent predator)
    {
        predators.Remove(predator);
        Destroy(predator.Transform.gameObject);
    }

    private CatAgent FindNearestCat(Vector3 position, float maxDistance)
    {
        CatAgent best = null;
        float bestDistance = maxDistance;
        for (int i = 0; i < cats.Count; i++)
        {
            CatAgent cat = cats[i];
            if (!cat.IsAlive)
            {
                continue;
            }

            float distance = Vector3.Distance(position, cat.Position);
            if (distance < bestDistance)
            {
                bestDistance = distance;
                best = cat;
            }
        }

        return best;
    }

    private PredatorAgent FindNearestPredator(Vector3 position, float maxDistance)
    {
        PredatorAgent best = null;
        float bestDistance = maxDistance;
        for (int i = 0; i < predators.Count; i++)
        {
            PredatorAgent predator = predators[i];
            float distance = Vector3.Distance(position, predator.Position);
            if (distance < bestDistance && predator.Health > 0f && predator.Courage > 0f)
            {
                bestDistance = distance;
                best = predator;
            }
        }

        return best;
    }

    private PreyAgent FindNearestPrey(Vector3 position, float maxDistance)
    {
        PreyAgent best = null;
        float bestDistance = maxDistance;
        for (int i = 0; i < prey.Count; i++)
        {
            float distance = Vector3.Distance(position, prey[i].Position);
            if (distance < bestDistance)
            {
                bestDistance = distance;
                best = prey[i];
            }
        }

        return best;
    }

    private void UpdateCamera()
    {
        if (gameCamera == null || toe == null)
        {
            return;
        }

        Vector3 focus = toe.IsAlive ? toe.Position : (seven != null ? seven.Position : Vector3.zero);
        if (seven != null && seven.IsAlive)
        {
            focus = (focus + seven.Position) * 0.5f;
        }

        Vector3 desired = focus + new Vector3(0f, 8.5f, -9.5f);
        gameCamera.transform.position = Vector3.Lerp(gameCamera.transform.position, desired, Time.deltaTime * 4.5f);
        gameCamera.transform.rotation = Quaternion.Slerp(gameCamera.transform.rotation, Quaternion.LookRotation(focus + Vector3.up * 0.6f - gameCamera.transform.position, Vector3.up), Time.deltaTime * 5.5f);
    }

    private void UpdateHud()
    {
        if (hudText == null)
        {
            return;
        }

        hudText.text =
            "Jungle Cats Survival\n" +
            "Toe (tuxedo): " + FormatVitals(toe) + "\n" +
            "Seven (brown spotted tabby): " + FormatVitals(seven) + "\n" +
            "Meals: " + mealsEaten + "   Predators scared/defeated: " + predatorsDefeated + "\n" +
            "Predators nearby: " + predators.Count + "   Prey: " + prey.Count + "\n" +
            "Survival time: " + FormatTime(elapsedTime) + "\n\n" +
            "Controls: WASD/Arrows move Toe | Space pounce | Shift hiss/scare | R restart";
    }

    private string FormatVitals(CatAgent cat)
    {
        if (cat == null)
        {
            return "--";
        }

        if (!cat.IsAlive)
        {
            return "down";
        }

        return Mathf.RoundToInt(cat.Health) + " health, " + Mathf.RoundToInt(cat.Hunger) + " hunger";
    }

    private string FormatTime(float seconds)
    {
        int totalSeconds = Mathf.FloorToInt(seconds);
        int minutes = totalSeconds / 60;
        int remainder = totalSeconds % 60;
        return minutes.ToString("00") + ":" + remainder.ToString("00");
    }

    private void CheckGameOver()
    {
        if ((toe == null || !toe.IsAlive) && (seven == null || !seven.IsAlive))
        {
            gameOver = true;
            SetMessage("Toe and Seven were overwhelmed. Press R to try the jungle again.");
        }
    }

    private void ResetGame()
    {
        for (int i = predators.Count - 1; i >= 0; i--)
        {
            Destroy(predators[i].Transform.gameObject);
        }

        for (int i = prey.Count - 1; i >= 0; i--)
        {
            Destroy(prey[i].Transform.gameObject);
        }

        predators.Clear();
        prey.Clear();
        elapsedTime = 0f;
        predatorWaveTimer = 0f;
        mealsEaten = 0;
        predatorsDefeated = 0;
        gameOver = false;

        toe.Health = 100f;
        toe.Hunger = 100f;
        toe.Transform.position = new Vector3(-1.5f, CatHeight, -2f);
        seven.Health = 100f;
        seven.Hunger = 100f;
        seven.Transform.position = new Vector3(1.5f, CatHeight, -2.3f);

        SpawnStartingCreatures();
        SetMessage("Toe and Seven head back into the jungle.");
    }

    private void SetMessage(string message)
    {
        if (messageText != null)
        {
            messageText.text = message;
        }
    }

    private Vector3 RandomPoint(float minRadius, float maxRadius)
    {
        Vector2 point = Random.insideUnitCircle.normalized * Random.Range(minRadius, maxRadius);
        return new Vector3(point.x, 0f, point.y);
    }

    private Vector3 ClampToArena(Vector3 position)
    {
        Vector2 flat = new Vector2(position.x, position.z);
        if (flat.magnitude > ArenaRadius)
        {
            flat = flat.normalized * ArenaRadius;
        }

        return new Vector3(flat.x, position.y, flat.y);
    }

    private void SetMaterial(GameObject target, Material material)
    {
        Renderer renderer = target.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.sharedMaterial = material;
        }
    }

    private void CreateWorldLabel(string text, Transform parent, Vector3 localPosition, Color color, float characterSize)
    {
        var labelObject = new GameObject(text + " Label");
        labelObject.transform.SetParent(parent, false);
        labelObject.transform.localPosition = localPosition;
        var label = labelObject.AddComponent<TextMesh>();
        label.text = text;
        label.anchor = TextAnchor.MiddleCenter;
        label.alignment = TextAlignment.Center;
        label.characterSize = characterSize;
        label.fontSize = 80;
        label.color = color;
        labelObject.AddComponent<JungleBillboard>();
    }

    private enum PredatorType
    {
        Panther,
        Wolf,
        Fox,
        Hyena
    }

    private enum PreyKind
    {
        Mouse,
        Rabbit
    }

    private sealed class CatAgent
    {
        public readonly Transform Transform;
        public readonly string Name;
        public readonly bool PlayerControlled;
        public float Health = 100f;
        public float Hunger = 100f;
        public float Speed = 5.4f;
        public float AttackTimer;
        public float ScareTimer;

        public CatAgent(Transform transform, string name, bool playerControlled)
        {
            Transform = transform;
            Name = name;
            PlayerControlled = playerControlled;
            Speed = playerControlled ? 5.7f : 5.25f;
        }

        public bool IsAlive
        {
            get { return Health > 0f; }
        }

        public Vector3 Position
        {
            get { return Transform.position; }
        }
    }

    private sealed class PredatorAgent
    {
        public readonly Transform Transform;
        public readonly PredatorType Type;
        public readonly string DisplayName;
        public readonly float Speed;
        public readonly float Damage;
        public readonly float AttackCooldown;
        public float Health;
        public float Courage;
        public float AttackTimer;
        public float Lifetime;
        public Vector3 FleeDirection;

        public PredatorAgent(Transform transform, PredatorType type, string displayName, float health, float courage, float speed, float damage, float attackCooldown)
        {
            Transform = transform;
            Type = type;
            DisplayName = displayName;
            Health = health;
            Courage = courage;
            Speed = speed;
            Damage = damage;
            AttackCooldown = attackCooldown;
            FleeDirection = transform.position.normalized;
        }

        public Vector3 Position
        {
            get { return Transform.position; }
        }
    }

    private sealed class PreyAgent
    {
        public readonly Transform Transform;
        public readonly PreyKind Kind;
        public readonly float FoodValue;
        public readonly float Speed;
        public Vector3 WanderDirection = Vector3.forward;
        public float WanderTimer;

        public PreyAgent(Transform transform, PreyKind kind, float foodValue, float speed)
        {
            Transform = transform;
            Kind = kind;
            FoodValue = foodValue;
            Speed = speed;
            WanderTimer = Random.Range(0.2f, 1.8f);
        }

        public Vector3 Position
        {
            get { return Transform.position; }
        }
    }
}

public sealed class JungleBillboard : MonoBehaviour
{
    private void LateUpdate()
    {
        Camera cameraToFace = Camera.main;
        if (cameraToFace == null)
        {
            return;
        }

        transform.rotation = Quaternion.LookRotation(transform.position - cameraToFace.transform.position, Vector3.up);
    }
}

internal static class GameInput
{
    public static bool GetKey(KeyCode key)
    {
        bool pressed = false;
#if ENABLE_INPUT_SYSTEM
        pressed |= GetInputSystemKey(key, false);
#endif
#if ENABLE_LEGACY_INPUT_MANAGER
        pressed |= Input.GetKey(key);
#endif
        return pressed;
    }

    public static bool GetKeyDown(KeyCode key)
    {
        bool pressed = false;
#if ENABLE_INPUT_SYSTEM
        pressed |= GetInputSystemKey(key, true);
#endif
#if ENABLE_LEGACY_INPUT_MANAGER
        pressed |= Input.GetKeyDown(key);
#endif
        return pressed;
    }

#if ENABLE_INPUT_SYSTEM
    private static bool GetInputSystemKey(KeyCode key, bool down)
    {
        UnityEngine.InputSystem.Keyboard keyboard = UnityEngine.InputSystem.Keyboard.current;
        if (keyboard == null)
        {
            return false;
        }

        UnityEngine.InputSystem.Controls.KeyControl control = null;
        switch (key)
        {
            case KeyCode.W:
                control = keyboard.wKey;
                break;
            case KeyCode.A:
                control = keyboard.aKey;
                break;
            case KeyCode.S:
                control = keyboard.sKey;
                break;
            case KeyCode.D:
                control = keyboard.dKey;
                break;
            case KeyCode.UpArrow:
                control = keyboard.upArrowKey;
                break;
            case KeyCode.DownArrow:
                control = keyboard.downArrowKey;
                break;
            case KeyCode.LeftArrow:
                control = keyboard.leftArrowKey;
                break;
            case KeyCode.RightArrow:
                control = keyboard.rightArrowKey;
                break;
            case KeyCode.Space:
                control = keyboard.spaceKey;
                break;
            case KeyCode.LeftShift:
                control = keyboard.leftShiftKey;
                break;
            case KeyCode.RightShift:
                control = keyboard.rightShiftKey;
                break;
            case KeyCode.R:
                control = keyboard.rKey;
                break;
        }

        if (control == null)
        {
            return false;
        }

        return down ? control.wasPressedThisFrame : control.isPressed;
    }
#endif
}
