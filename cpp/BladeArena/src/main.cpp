#include "raylib.h"
#include "raymath.h"

#define RLIGHTS_IMPLEMENTATION
#include "rlights.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

constexpr int kMaxHealth = 5;
constexpr int kEnemyCount = 10;
constexpr float kMapHalfSize = 200.0f;
constexpr float kPi = 3.14159265f;

struct WeaponStats {
    const char* name;
    float damage;
    float range;
    float cooldown;
    Color color;
};

struct LootPickup {
    Vector3 position;
    WeaponStats stats;
    bool active = true;
};

struct Cabin {
    Vector3 position;
    Color color;
    LootPickup loot;
};

struct Tree {
    Vector3 position;
    float scale;
    bool backdrop = false;
};

struct Mountain {
    Vector3 position;
    float radius;
    float height;
};

struct Enemy {
    Vector3 position;
    float health = 2.0f;
    float attackTimer = 0.0f;
    bool alive = true;
    int targetKind = 0;
    int targetEnemy = -1;
};

struct StormState {
    bool active = false;
    float stormTimer = 0.0f;
    float checkTimer = 5.0f;
    float lightningTimer = 0.0f;
    float flashTimer = 0.0f;
};

struct PlayerState {
    Vector3 position{0.0f, 0.0f, 0.0f};
    float yaw = 0.0f;
    Vector3 destination{0.0f, 0.0f, 0.0f};
    bool hasDestination = false;
    float verticalVelocity = 0.0f;
    int health = kMaxHealth;
    WeaponStats weapon{"Rusty Blade", 1.0f, 2.2f, 0.45f, {140, 140, 153, 255}};
    float attackCooldown = 0.0f;
};

struct WorldMap {
    std::vector<Tree> trees;
    std::vector<Tree> backdropForest;
    std::vector<Mountain> mountains;
    std::vector<Vector3> riverTiles;
};

struct GameState {
    PlayerState player;
    std::vector<Enemy> enemies;
    std::vector<Cabin> cabins;
    WorldMap world;
    StormState storm;
    int score = 0;
    bool gameOver = false;
    char weaponMessage[96] = "";
    float weaponMessageTimer = 0.0f;
    float smoothedFpsDelta = 1.0f / 60.0f;
    Model playerModel{};
    bool playerModelLoaded = false;
    float playerModelScale = 1.0f;
    float playerModelFeetOffset = 0.0f;
    Vector3 playerModelCenterOffset{0.0f, 0.0f, 0.0f};
    float playerModelYawOffset = 180.0f;
    Shader characterShader{};
    bool characterShaderLoaded = false;
    Light sunLight{};
};

unsigned WorldSeed(unsigned x) {
    x = ((x >> 16) ^ x) * 0x45d9f3bU;
    x = ((x >> 16) ^ x) * 0x45d9f3bU;
    x = (x >> 16) ^ x;
    return x;
}

float Hash01(float x, float z) {
    int ix = static_cast<int>(std::floor(x * 0.17f));
    int iz = static_cast<int>(std::floor(z * 0.17f));
    unsigned h = WorldSeed(static_cast<unsigned>(ix * 73856093 ^ iz * 19349663));
    return static_cast<float>(h % 10000) / 10000.0f;
}

float RiverCenterX(float z) {
    return 35.0f * std::sin(z * 0.028f) + 18.0f * std::sin(z * 0.071f + 1.2f);
}

float RiverWidth(float z) {
    return 10.0f + 3.0f * std::sin(z * 0.04f);
}

bool IsInRiver(float x, float z) {
    float center = RiverCenterX(z);
    float halfWidth = RiverWidth(z) * 0.5f;
    return std::fabs(x - center) <= halfWidth;
}

float TerrainHeight(float x, float z) {
    float hills = 2.2f * std::sin(x * 0.018f) * std::cos(z * 0.014f);
    hills += 1.4f * std::sin(x * 0.007f + z * 0.009f);
    hills += (Hash01(x, z) - 0.5f) * 0.35f;
    if (IsInRiver(x, z))
        hills -= 1.35f;
    return hills;
}

Vector3 FlatTo(Vector3 from, Vector3 to) {
    return {to.x - from.x, 0.0f, to.z - from.z};
}

bool PointInCabin(Vector3 worldPos, const std::vector<Cabin>& cabins) {
    Vector3 sample{worldPos.x, worldPos.y + 0.75f, worldPos.z};
    for (const Cabin& c : cabins) {
        Vector3 center{c.position.x, c.position.y + 1.9f, c.position.z};
        if (std::fabs(sample.x - center.x) <= 2.8f && std::fabs(sample.y - center.y) <= 2.2f &&
            std::fabs(sample.z - center.z) <= 2.8f)
            return true;
    }
    return false;
}

void GenerateWorld(WorldMap& world) {
    world.trees.clear();
    world.riverTiles.clear();

    for (float z = -kMapHalfSize; z <= kMapHalfSize; z += 11.0f) {
        float x = RiverCenterX(z);
        float w = RiverWidth(z);
        world.riverTiles.push_back({x, TerrainHeight(x, z) - 0.2f, z});
        (void)w;
    }

    for (int i = 0; i < 650; ++i) {
        unsigned h = WorldSeed(static_cast<unsigned>(i * 2654435761U + 1013904223U));
        float rx = static_cast<float>(h % 10000) / 10000.0f;
        float rz = static_cast<float>((h / 10000U) % 10000U) / 10000.0f;
        float x = (rx * 2.0f - 1.0f) * (kMapHalfSize - 15.0f);
        float z = (rz * 2.0f - 1.0f) * (kMapHalfSize - 15.0f);

        if (IsInRiver(x, z))
            continue;
        if (Vector2Distance({x, z}, {0.0f, 0.0f}) < 18.0f)
            continue;

        float scale = 0.75f + Hash01(x + 3.1f, z - 1.7f) * 0.9f;
        float y = TerrainHeight(x, z);
        world.trees.push_back({{x, y, z}, scale, false});
    }

    for (int i = 0; i < 36; ++i) {
        float angle = (2.0f * kPi / 36.0f) * static_cast<float>(i);
        float jitter = Hash01(static_cast<float>(i) * 1.7f, static_cast<float>(i) * 0.9f) * 0.35f;
        float dist = 235.0f + jitter * 55.0f;
        float x = std::cos(angle + jitter) * dist;
        float z = std::sin(angle + jitter) * dist;
        float height = 38.0f + Hash01(x, z) * 52.0f;
        float radius = 22.0f + Hash01(z, x) * 28.0f;
        world.mountains.push_back({{x, 0.0f, z}, radius, height});
    }

    for (int i = 0; i < 820; ++i) {
        unsigned h = WorldSeed(static_cast<unsigned>(i * 3344921057U + 777U));
        float angle = static_cast<float>(h % 6283) / 1000.0f;
        float dist = 165.0f + static_cast<float>((h / 6283U) % 70U);
        float x = std::cos(angle) * dist;
        float z = std::sin(angle) * dist;
        if (IsInRiver(x, z))
            continue;
        float scale = 1.1f + Hash01(x * 0.3f, z * 0.3f) * 1.4f;
        world.backdropForest.push_back({{x, 0.0f, z}, scale, true});
    }
}

std::string ResolveAssetPath(const char* relative) {
    const char* roots[] = {"/workspace/cpp/BladeArena/assets/", "../assets/", "../../cpp/BladeArena/assets/",
                           "assets/"};
    for (const char* root : roots) {
        std::string path = std::string(root) + relative;
        if (FileExists(path.c_str()))
            return path;
    }
    return std::string(relative);
}

void BeginSceneLighting(const GameState& game, Camera3D camera) {
    if (!game.characterShaderLoaded)
        return;
    float cameraPos[3] = {camera.position.x, camera.position.y, camera.position.z};
    SetShaderValue(game.characterShader, game.characterShader.locs[SHADER_LOC_VECTOR_VIEW], cameraPos, SHADER_UNIFORM_VEC3);
    UpdateLightValues(game.characterShader, game.sunLight);
    BeginShaderMode(game.characterShader);
}

void EndSceneLighting(const GameState& game) {
    if (game.characterShaderLoaded)
        EndShaderMode();
}

Color TerrainGrassColor(float x, float z) {
    if (IsInRiver(x, z))
        return {48, 92, 58, 255};
    Color grass{56, 112, 46, 255};
    if (Hash01(x, z) > 0.82f)
        grass = {68, 98, 40, 255};
    return grass;
}

bool SetupCharacterShader(GameState& game) {
    std::string vs = ResolveAssetPath("shaders/glsl330/lighting.vs");
    std::string fs = ResolveAssetPath("shaders/glsl330/lighting.fs");
    if (!FileExists(vs.c_str()) || !FileExists(fs.c_str()))
        return false;

    game.characterShader = LoadShader(vs.c_str(), fs.c_str());
    if (game.characterShader.id == 0)
        return false;

    game.characterShader.locs[SHADER_LOC_VECTOR_VIEW] = GetShaderLocation(game.characterShader, "viewPos");
    int ambientLoc = GetShaderLocation(game.characterShader, "ambient");
    float ambient[4] = {0.35f, 0.38f, 0.42f, 1.0f};
    SetShaderValue(game.characterShader, ambientLoc, ambient, SHADER_UNIFORM_VEC4);

    game.sunLight = CreateLight(LIGHT_DIRECTIONAL, {40.0f, 90.0f, 35.0f}, {0.0f, 0.0f, 0.0f}, WHITE, game.characterShader);
    game.characterShaderLoaded = true;
    return true;
}

void ApplyShaderToModel(Model& model, Shader shader) {
    for (int i = 0; i < model.materialCount; ++i)
        model.materials[i].shader = shader;
}

void SetupPlayerModel(GameState& game, const char* path) {
    if (!FileExists(path))
        return;

    game.playerModel = LoadModel(path);
    if (game.playerModel.meshCount <= 0)
        return;

    game.playerModelLoaded = true;
    BoundingBox bounds = GetModelBoundingBox(game.playerModel);
    float height = bounds.max.y - bounds.min.y;
    game.playerModelScale = height > 0.01f ? 1.85f / height : 1.85f;
    game.playerModelFeetOffset = bounds.min.y * game.playerModelScale;
    game.playerModelCenterOffset = {(bounds.min.x + bounds.max.x) * 0.5f, 0.0f, (bounds.min.z + bounds.max.z) * 0.5f};

    if (!game.characterShaderLoaded)
        SetupCharacterShader(game);
    if (game.characterShaderLoaded)
        ApplyShaderToModel(game.playerModel, game.characterShader);
}

void NotifyWeapon(GameState& game, const char* name) {
    std::snprintf(game.weaponMessage, sizeof(game.weaponMessage), "Weapon: %s", name);
    game.weaponMessageTimer = 3.0f;
}

void SpawnEnemies(GameState& game) {
    game.enemies.clear();
    game.enemies.resize(kEnemyCount);
    for (int i = 0; i < kEnemyCount; ++i) {
        unsigned h = WorldSeed(static_cast<unsigned>(i * 1597334677U + 42U));
        float angle = static_cast<float>(h % 6283) / 1000.0f;
        float radius = 45.0f + static_cast<float>((h / 6283U) % 80U);
        float x = std::cos(angle) * radius;
        float z = std::sin(angle) * radius;
        float y = TerrainHeight(x, z);
        game.enemies[i].position = {x, y + 0.9f, z};
        game.enemies[i].health = 2.0f;
        game.enemies[i].alive = true;
    }
}

void ResetGameplay(GameState& game) {
    Model model = game.playerModel;
    bool modelLoaded = game.playerModelLoaded;
    float modelScale = game.playerModelScale;
    float feetOffset = game.playerModelFeetOffset;
    Vector3 centerOffset = game.playerModelCenterOffset;
    float yawOffset = game.playerModelYawOffset;
    Shader characterShader = game.characterShader;
    bool characterShaderLoaded = game.characterShaderLoaded;
    Light sunLight = game.sunLight;
    WorldMap world = game.world;

    game.player = PlayerState{};
    game.player.health = kMaxHealth;
    game.player.position = {0.0f, TerrainHeight(0.0f, 0.0f), 0.0f};
    game.player.destination = game.player.position;

    game.playerModel = model;
    game.playerModelLoaded = modelLoaded;
    game.playerModelScale = modelScale;
    game.playerModelFeetOffset = feetOffset;
    game.playerModelCenterOffset = centerOffset;
    game.playerModelYawOffset = yawOffset;
    game.characterShader = characterShader;
    game.characterShaderLoaded = characterShaderLoaded;
    game.sunLight = sunLight;
    game.world = world;

    game.cabins = {
        {{-70.0f, TerrainHeight(-70.0f, 55.0f), 55.0f},
         {130, 105, 85, 255},
         {{-70.0f, TerrainHeight(-70.0f, 55.0f) + 1.35f, 55.0f},
          {"Iron Sword", 2.0f, 2.5f, 0.38f, {184, 115, 51, 255}},
          true}},
        {{85.0f, TerrainHeight(85.0f, -60.0f), -60.0f},
         {105, 125, 100, 255},
         {{85.0f, TerrainHeight(85.0f, -60.0f) + 1.35f, -60.0f},
          {"Steel Sword", 3.0f, 2.8f, 0.32f, {199, 209, 230, 255}},
          true}},
        {{-45.0f, TerrainHeight(-45.0f, -95.0f), -95.0f},
         {95, 105, 135, 255},
         {{-45.0f, TerrainHeight(-45.0f, -95.0f) + 1.35f, -95.0f},
          {"Storm Blade", 4.5f, 3.2f, 0.28f, {115, 191, 255, 255}},
          true}},
    };

    SpawnEnemies(game);
    game.storm = StormState{};
    game.storm.checkTimer = 5.0f;
    game.score = 0;
    game.gameOver = false;
    game.weaponMessage[0] = '\0';
    game.weaponMessageTimer = 0.0f;
}

bool RayHitTerrain(Vector2 mouse, Camera3D camera, Vector3* hit) {
    Ray ray = GetMouseRay(mouse, camera);
    if (std::fabs(ray.direction.y) < 1e-5f)
        return false;
    float t = -ray.position.y / ray.direction.y;
    if (t < 0.0f)
        return false;
    hit->x = ray.position.x + ray.direction.x * t;
    hit->z = ray.position.z + ray.direction.z * t;
    if (std::fabs(hit->x) > kMapHalfSize || std::fabs(hit->z) > kMapHalfSize)
        return false;
    hit->y = TerrainHeight(hit->x, hit->z);
    return true;
}

void ClampToMap(Vector3& pos) {
    pos.x = std::clamp(pos.x, -kMapHalfSize, kMapHalfSize);
    pos.z = std::clamp(pos.z, -kMapHalfSize, kMapHalfSize);
    pos.y = TerrainHeight(pos.x, pos.z);
}

void TryStartStorm(GameState& game) {
    if (game.storm.active)
        return;
    if (GetRandomValue(0, 999) < 100) {
        game.storm.active = true;
        game.storm.stormTimer = 40.0f;
        game.storm.lightningTimer = 1.0f;
    }
}

void StrikeLightning(GameState& game) {
    game.storm.flashTimer = 0.12f;
    if (!PointInCabin(game.player.position, game.cabins) && GetRandomValue(0, 999) < 50) {
        game.player.health -= 2;
        if (game.player.health <= 0) {
            game.player.health = 0;
            game.gameOver = true;
        }
    }
    for (auto& enemy : game.enemies) {
        if (!enemy.alive || PointInCabin(enemy.position, game.cabins))
            continue;
        if (GetRandomValue(0, 999) < 50)
            enemy.health -= 2.0f;
        if (enemy.health <= 0.0f)
            enemy.alive = false;
    }
}

void UpdateStorm(GameState& game, float dt) {
    if (game.storm.flashTimer > 0.0f)
        game.storm.flashTimer -= dt;

    if (game.storm.active) {
        game.storm.stormTimer -= dt;
        game.storm.lightningTimer -= dt;
        if (game.storm.lightningTimer <= 0.0f) {
            game.storm.lightningTimer = 2.5f;
            StrikeLightning(game);
        }
        if (game.storm.stormTimer <= 0.0f) {
            game.storm.active = false;
            game.storm.checkTimer = 60.0f;
        }
        return;
    }

    game.storm.checkTimer -= dt;
    if (game.storm.checkTimer <= 0.0f) {
        game.storm.checkTimer = 60.0f;
        TryStartStorm(game);
    }
}

void PickEnemyTarget(Enemy& enemy, const GameState& game, int selfIndex) {
    enemy.targetKind = 0;
    enemy.targetEnemy = -1;
    float bestScore = 1e9f;

    float playerDist = Vector3Distance(enemy.position, game.player.position);
    if (playerDist <= 45.0f) {
        bestScore = playerDist / 1.15f;
        enemy.targetKind = 1;
    }

    for (int i = 0; i < static_cast<int>(game.enemies.size()); ++i) {
        if (i == selfIndex || !game.enemies[i].alive)
            continue;
        float dist = Vector3Distance(enemy.position, game.enemies[i].position);
        if (dist > 45.0f || dist >= bestScore)
            continue;
        bestScore = dist;
        enemy.targetKind = 2;
        enemy.targetEnemy = i;
    }
}

Vector3 TargetPosition(const Enemy& enemy, const GameState& game) {
    if (enemy.targetKind == 1)
        return game.player.position;
    if (enemy.targetKind == 2 && enemy.targetEnemy >= 0)
        return game.enemies[enemy.targetEnemy].position;
    return enemy.position;
}

void DamagePlayer(GameState& game, int amount) {
    if (game.gameOver)
        return;
    game.player.health -= amount;
    if (game.player.health <= 0) {
        game.player.health = 0;
        game.gameOver = true;
    }
}

void KillEnemy(GameState& game, int index, bool awardScore) {
    if (!game.enemies[index].alive)
        return;
    game.enemies[index].alive = false;
    if (awardScore)
        game.score++;
}

void PlayerAttack(GameState& game) {
    Vector3 forward{std::sin(game.player.yaw * DEG2RAD), 0.0f, std::cos(game.player.yaw * DEG2RAD)};
    Vector3 center{game.player.position.x + forward.x * game.player.weapon.range * 0.5f,
                   game.player.position.y + 1.0f, game.player.position.z + forward.z * game.player.weapon.range * 0.5f};

    for (int i = 0; i < static_cast<int>(game.enemies.size()); ++i) {
        if (!game.enemies[i].alive)
            continue;
        if (Vector3Distance(center, game.enemies[i].position) <= game.player.weapon.range * 0.55f) {
            game.enemies[i].health -= game.player.weapon.damage;
            if (game.enemies[i].health <= 0.0f)
                KillEnemy(game, i, true);
        }
    }
}

void TryPickupLoot(GameState& game) {
    for (Cabin& cabin : game.cabins) {
        if (!cabin.loot.active)
            continue;
        if (Vector3Distance(game.player.position, cabin.loot.position) > 1.5f)
            continue;
        if (cabin.loot.stats.damage <= game.player.weapon.damage + 0.01f)
            continue;
        game.player.weapon = cabin.loot.stats;
        cabin.loot.active = false;
        NotifyWeapon(game, game.player.weapon.name);
    }
}

void UpdatePlayer(GameState& game, Camera3D camera, float dt) {
    auto& p = game.player;
    if (game.gameOver)
        return;

    if (IsMouseButtonPressed(MOUSE_BUTTON_RIGHT)) {
        Vector3 hit{};
        if (RayHitTerrain(GetMousePosition(), camera, &hit)) {
            p.destination = hit;
            p.hasDestination = true;
        }
    }

    float groundY = TerrainHeight(p.position.x, p.position.z);
    bool grounded = p.position.y <= groundY + 0.05f;
    if (grounded && p.verticalVelocity < 0.0f)
        p.verticalVelocity = 0.0f;
    if (IsKeyPressed(KEY_SPACE) && grounded)
        p.verticalVelocity = 6.5f;

    p.verticalVelocity += -22.0f * dt;
    p.position.y += p.verticalVelocity * dt;
    groundY = TerrainHeight(p.position.x, p.position.z);
    if (p.position.y < groundY) {
        p.position.y = groundY;
        p.verticalVelocity = 0.0f;
    }

    float moveSpeed = IsInRiver(p.position.x, p.position.z) ? 3.2f : 5.5f;
    Vector3 horizontal{0.0f, 0.0f, 0.0f};
    if (p.hasDestination) {
        Vector3 toDest = FlatTo(p.position, p.destination);
        float dist = Vector3Length(toDest);
        if (dist <= 0.35f) {
            p.hasDestination = false;
        } else {
            horizontal = Vector3Scale(Vector3Normalize(toDest), moveSpeed);
            float targetYaw = std::atan2(toDest.x, toDest.z) * RAD2DEG;
            p.yaw = Lerp(p.yaw, targetYaw, 12.0f * dt);
        }
    }

    p.position.x += horizontal.x * dt;
    p.position.z += horizontal.z * dt;
    ClampToMap(p.position);

    p.attackCooldown -= dt;
    if (IsKeyPressed(KEY_A) && p.attackCooldown <= 0.0f) {
        p.attackCooldown = p.weapon.cooldown;
        PlayerAttack(game);
    }

    TryPickupLoot(game);
}

void UpdateEnemies(GameState& game, float dt) {
    for (int i = 0; i < static_cast<int>(game.enemies.size()); ++i) {
        Enemy& enemy = game.enemies[i];
        if (!enemy.alive)
            continue;

        PickEnemyTarget(enemy, game, i);
        if (enemy.targetKind == 0)
            continue;

        Vector3 targetPos = TargetPosition(enemy, game);
        Vector3 toTarget = FlatTo(enemy.position, targetPos);
        float distance = Vector3Length(toTarget);

        if (distance > 1.4f) {
            Vector3 step = Vector3Scale(Vector3Normalize(toTarget), 2.5f * dt);
            enemy.position.x += step.x;
            enemy.position.z += step.z;
            enemy.position.y = TerrainHeight(enemy.position.x, enemy.position.z) + 0.9f;
            continue;
        }

        enemy.attackTimer -= dt;
        if (enemy.attackTimer > 0.0f)
            continue;
        enemy.attackTimer = 1.2f;

        if (enemy.targetKind == 1)
            DamagePlayer(game, 1);
        else if (enemy.targetKind == 2 && enemy.targetEnemy >= 0) {
            Enemy& other = game.enemies[enemy.targetEnemy];
            other.health -= 1.0f;
            if (other.health <= 0.0f)
                KillEnemy(game, enemy.targetEnemy, false);
        }
    }
}

void DrawGroundShadow(Vector3 feet, float radius, float alpha) {
    Color shadow{0, 0, 0, static_cast<unsigned char>(std::clamp(alpha, 0.0f, 1.0f) * 255.0f)};
    DrawCylinder({feet.x, feet.y + 0.04f, feet.z}, radius, radius, 0.03f, 14, shadow);
}

void DrawTree(const Tree& tree, bool darkBackdrop) {
    float y = tree.backdrop ? 0.0f : TerrainHeight(tree.position.x, tree.position.z);
    Vector3 base{tree.position.x, y, tree.position.z};
    float trunkH = (darkBackdrop ? 3.4f : 2.6f) * tree.scale;
    Color trunk{darkBackdrop ? 72 : 92, darkBackdrop ? 48 : 58, 32, 255};
    Color leaves{darkBackdrop ? 24 : 38, darkBackdrop ? 88 : 118, darkBackdrop ? 38 : 52, 255};
    Color leavesDark{darkBackdrop ? 18 : 28, darkBackdrop ? 68 : 88, darkBackdrop ? 30 : 40, 255};

    DrawCylinder(base, 0.22f * tree.scale, 0.28f * tree.scale, trunkH, 8, trunk);
    Vector3 crown{base.x, base.y + trunkH + 0.7f * tree.scale, base.z};
    float crownR = (darkBackdrop ? 1.55f : 1.25f) * tree.scale;
    DrawSphere(crown, crownR, leaves);
    DrawSphere(crown + Vector3{0.35f * tree.scale, 0.15f, 0.25f * tree.scale}, crownR * 0.72f, leavesDark);
}

void DrawMountain(const Mountain& mountain) {
    Vector3 base = mountain.position;
    float h = mountain.height;
    float r = mountain.radius;
    Color rockBase{72, 68, 62, 255};
    Color rockMid{92, 86, 78, 255};
    Color rockPeak{108, 104, 98, 255};
    Color snow{228, 236, 244, 255};

    DrawCylinder(base, r * 0.95f, r * 0.35f, h * 0.55f, 12, rockBase);
    DrawCylinder({base.x, base.y + h * 0.45f, base.z}, r * 0.55f, r * 0.12f, h * 0.38f, 12, rockMid);
    DrawSphere({base.x, base.y + h * 0.78f, base.z}, r * 0.38f, rockPeak);
    DrawSphere({base.x, base.y + h * 0.9f, base.z}, r * 0.22f, snow);
}

void DrawCabin(const Cabin& cabin) {
    float baseY = TerrainHeight(cabin.position.x, cabin.position.z);
    Vector3 center{cabin.position.x, baseY + 1.5f, cabin.position.z};
    DrawCube(center, 4.2f, 3.0f, 4.2f, cabin.color);
    DrawCubeWires(center, 4.2f, 3.0f, 4.2f, ColorAlpha(BLACK, 0.2f));
    Vector3 roof{center.x, center.y + 1.85f, center.z};
    DrawCube(roof, 5.2f, 0.55f, 5.2f, ColorBrightness(cabin.color, -0.2f));

    if (cabin.loot.active) {
        Vector3 lootPos{cabin.loot.position.x, TerrainHeight(cabin.loot.position.x, cabin.loot.position.z) + 1.35f,
                        cabin.loot.position.z};
        DrawCylinder(lootPos + Vector3{0.0f, -0.35f, 0.0f}, 0.35f, 0.35f, 0.16f, 10, {64, 64, 72, 255});
        DrawCube(lootPos, 0.22f, 0.9f, 0.12f, cabin.loot.stats.color);
    }
}

void DrawTerrain(Vector3 playerPos) {
    DrawPlane({0.0f, -0.05f, 0.0f}, {kMapHalfSize * 2.0f, kMapHalfSize * 2.0f}, {48, 102, 42, 255});

    const int steps = 12;
    const float cell = 24.0f;
    for (int ix = -steps; ix <= steps; ++ix) {
        for (int iz = -steps; iz <= steps; ++iz) {
            float x = playerPos.x + static_cast<float>(ix) * cell;
            float z = playerPos.z + static_cast<float>(iz) * cell;
            if (std::fabs(x) > kMapHalfSize || std::fabs(z) > kMapHalfSize)
                continue;

            float yCenter = TerrainHeight(x, z);
            float yNorth = TerrainHeight(x, z + cell * 0.5f);
            float ySouth = TerrainHeight(x, z - cell * 0.5f);
            float yEast = TerrainHeight(x + cell * 0.5f, z);
            float yWest = TerrainHeight(x - cell * 0.5f, z);
            float blockH = std::max({yNorth, ySouth, yEast, yWest, yCenter, 0.15f});
            Color grass = TerrainGrassColor(x, z);
            DrawCube({x, blockH * 0.5f - 0.05f, z}, cell * 0.98f, blockH, cell * 0.98f, grass);
        }
    }
}

void DrawBackdropScenery(const WorldMap& world, Vector3 playerPos) {
    for (const Mountain& mountain : world.mountains)
        DrawMountain(mountain);

    constexpr float kBackdropForestDist = 260.0f;
    for (const Tree& tree : world.backdropForest) {
        if (Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z}) > kBackdropForestDist)
            continue;
        DrawTree(tree, true);
    }
}

void DrawRivers() {
    for (float z = -kMapHalfSize; z <= kMapHalfSize; z += 9.0f) {
        float x = RiverCenterX(z);
        float w = RiverWidth(z);
        float y = TerrainHeight(x, z) - 0.15f;
        DrawCube({x, y, z}, w, 0.12f, 10.0f, {45, 130, 195, 210});
        DrawCube({x, y + 0.02f, z}, w * 0.92f, 0.04f, 9.0f, {90, 180, 230, 180});
    }
}

void DrawPlayerCharacter(const GameState& game, Camera3D camera) {
    Vector3 feet = game.player.position;
    feet.y = TerrainHeight(feet.x, feet.z);

    float yaw = game.player.yaw + game.playerModelYawOffset;
    float s = game.playerModelScale;
    Vector3 forward{std::sin(game.player.yaw * DEG2RAD), 0.0f, std::cos(game.player.yaw * DEG2RAD)};
    Vector3 right{-forward.z, 0.0f, forward.x};

    if (game.playerModelLoaded) {
        Vector3 drawPos{
            feet.x - game.playerModelCenterOffset.x * s,
            feet.y - game.playerModelFeetOffset,
            feet.z - game.playerModelCenterOffset.z * s};

        DrawModelEx(game.playerModel, drawPos, {0.0f, 1.0f, 0.0f}, yaw, {s, s, s}, WHITE);
    } else {
        DrawCapsule(feet, feet + Vector3{0.0f, 1.8f, 0.0f}, 0.35f, 10, 10, {90, 150, 220, 255});
    }

    float bladeLen = std::strstr(game.player.weapon.name, "Storm")   ? 1.2f
                     : std::strstr(game.player.weapon.name, "Steel") ? 1.05f
                                                                     : 0.95f;
    Vector3 hand = feet + Vector3{right.x * 0.28f + forward.x * 0.12f, 1.05f, right.z * 0.28f + forward.z * 0.12f};
    Vector3 tip = hand + Vector3{forward.x * bladeLen, 0.08f, forward.z * bladeLen};
    DrawCylinderEx(hand, tip, 0.05f, 0.02f, 8, game.player.weapon.color);
}

void DrawWorld(const GameState& game, Camera3D camera) {
    Vector3 playerPos = game.player.position;

    BeginSceneLighting(game, camera);
    DrawBackdropScenery(game.world, playerPos);
    DrawTerrain(playerPos);
    DrawRivers();
    EndSceneLighting(game);

    constexpr float kTreeDrawDistance = 110.0f;
    for (const Tree& tree : game.world.trees) {
        if (Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z}) > kTreeDrawDistance)
            continue;
        Vector3 base{tree.position.x, TerrainHeight(tree.position.x, tree.position.z), tree.position.z};
        DrawGroundShadow(base, 0.55f * tree.scale, 0.28f);
    }
    for (const Tree& tree : game.world.backdropForest) {
        if (Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z}) > 260.0f)
            continue;
        DrawGroundShadow({tree.position.x, 0.0f, tree.position.z}, 0.7f * tree.scale, 0.18f);
    }

    BeginSceneLighting(game, camera);
    for (const Cabin& cabin : game.cabins)
        DrawCabin(cabin);

    for (const Tree& tree : game.world.trees) {
        if (Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z}) > kTreeDrawDistance)
            continue;
        DrawTree(tree, false);
    }

    for (const Enemy& enemy : game.enemies) {
        if (!enemy.alive)
            continue;
        float y = TerrainHeight(enemy.position.x, enemy.position.z);
        Vector3 base{enemy.position.x, y, enemy.position.z};
        DrawGroundShadow(base, 0.42f, 0.32f);
        DrawCapsule(base, base + Vector3{0.0f, 1.6f, 0.0f}, 0.45f, 8, 8, {180, 60, 60, 255});
    }

    Vector3 playerFeet{playerPos.x, TerrainHeight(playerPos.x, playerPos.z), playerPos.z};
    DrawGroundShadow(playerFeet, 0.5f, 0.38f);
    DrawPlayerCharacter(game, camera);
    EndSceneLighting(game);
}

void DrawHud(const GameState& game) {
    int y = 12;
    auto line = [&](const char* text) {
        DrawText(text, 12, y, 18, RAYWHITE);
        y += 22;
    };

    line("Blade Arena Wilds (C++)");
    line("Right-click move | Space jump | A attack | R restart");
    char buf[160];
    std::snprintf(buf, sizeof(buf), "Health: %d", game.player.health);
    line(buf);
    std::snprintf(buf, sizeof(buf), "Equipped: %s (%.1f dmg)", game.player.weapon.name, game.player.weapon.damage);
    line(buf);

    int enemiesLeft = 0;
    for (const Enemy& e : game.enemies)
        if (e.alive)
            enemiesLeft++;
    std::snprintf(buf, sizeof(buf), "Enemies left: %d | Score: %d", enemiesLeft, game.score);
    line(buf);

    if (game.storm.active)
        line("STORM - hide in cabins for shelter and better swords!");
    if (game.weaponMessageTimer > 0.0f)
        line(game.weaponMessage);
    if (game.gameOver)
        line("Defeated - press R to try again");

    int fps = static_cast<int>(1.0f / std::max(game.smoothedFpsDelta, 0.0001f) + 0.5f);
    const char* fpsText = TextFormat("%d FPS", fps);
    DrawText(fpsText, GetScreenWidth() - MeasureText(fpsText, 18) - 12, 10, 18, RAYWHITE);
}

void UpdateCamera(Camera3D& camera, const GameState& game, float dt) {
    Vector3 playerCenter = game.player.position;
    playerCenter.y = TerrainHeight(playerCenter.x, playerCenter.z) + 1.4f;

    float yawRad = game.player.yaw * DEG2RAD;
    const float camDistance = 9.0f;
    const float camHeight = 3.8f;
    Vector3 desired{
        playerCenter.x - std::sin(yawRad) * camDistance,
        playerCenter.y + camHeight,
        playerCenter.z - std::cos(yawRad) * camDistance};

    camera.position = Vector3Lerp(camera.position, desired, 6.0f * dt);
    camera.target = Vector3Lerp(camera.target, playerCenter, 8.0f * dt);
}

std::string ResolveModelPath(int argc, char** argv) {
    if (argc > 1 && argv[1][0] != '\0')
        return argv[1];
    const char* env = std::getenv("BLADE_ARENA_MODEL");
    if (env && env[0] != '\0')
        return env;

    const char* candidates[] = {
        "/workspace/Assets/Models/HumanFigure_game.glb",
        "../../Assets/Models/HumanFigure_game.glb",
        "/workspace/Assets/Models/HumanFigure.glb",
        "../../Assets/Models/HumanFigure.glb",
    };
    for (const char* path : candidates) {
        if (FileExists(path))
            return path;
    }
    return candidates[1];
}

} // namespace

int main(int argc, char** argv) {
    SetConfigFlags(FLAG_MSAA_4X_HINT | FLAG_WINDOW_RESIZABLE);
    InitWindow(1280, 720, "Blade Arena Wilds (C++)");
    SetTargetFPS(60);

    GameState game;
    GenerateWorld(game.world);
    SetupCharacterShader(game);
    SetupPlayerModel(game, ResolveModelPath(argc, argv).c_str());
    ResetGameplay(game);

    Camera3D camera{};
    camera.up = {0.0f, 1.0f, 0.0f};
    camera.fovy = 55.0f;
    camera.projection = CAMERA_PERSPECTIVE;
    UpdateCamera(camera, game, 1.0f);

    while (!WindowShouldClose()) {
        float dt = GetFrameTime();
        game.smoothedFpsDelta += (dt - game.smoothedFpsDelta) * 0.1f;
        if (game.weaponMessageTimer > 0.0f)
            game.weaponMessageTimer -= dt;

        if (IsKeyPressed(KEY_R))
            ResetGameplay(game);

        UpdateStorm(game, dt);
        UpdatePlayer(game, camera, dt);
        UpdateEnemies(game, dt);
        UpdateCamera(camera, game, dt);

        Color sky = game.storm.active ? Color{28, 34, 48, 255} : Color{95, 165, 220, 255};
        if (game.storm.flashTimer > 0.0f)
            sky = Color{200, 210, 255, 255};

        BeginDrawing();
        ClearBackground(sky);

        BeginMode3D(camera);
        DrawWorld(game, camera);
        EndMode3D();

        DrawHud(game);
        EndDrawing();
    }

    if (game.playerModelLoaded)
        UnloadModel(game.playerModel);
    if (game.characterShaderLoaded)
        UnloadShader(game.characterShader);

    CloseWindow();
    return 0;
}
