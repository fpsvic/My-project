#include "raylib.h"
#include "raymath.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

constexpr int kMaxHealth = 5;
constexpr int kEnemyCount = 6;
constexpr float kEnemySpawnRadius = 12.0f;
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

struct Building {
    Vector3 position;
    Color color;
    LootPickup loot;
};

struct Enemy {
    Vector3 position;
    float health = 2.0f;
    float attackTimer = 0.0f;
    bool alive = true;
    int targetKind = 0; // 0 none, 1 player, 2 enemy index
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

struct GameState {
    PlayerState player;
    std::vector<Enemy> enemies;
    std::vector<Building> buildings;
    StormState storm;
    int score = 0;
    bool gameOver = false;
    char weaponMessage[96] = "";
    float weaponMessageTimer = 0.0f;
    float smoothedFpsDelta = 1.0f / 60.0f;
    Model playerModel{};
    bool playerModelLoaded = false;
};

float LengthXZ(Vector3 v) { return std::sqrt(v.x * v.x + v.z * v.z); }

Vector3 FlatTo(Vector3 from, Vector3 to) {
    Vector3 d{to.x - from.x, 0.0f, to.z - from.z};
    return d;
}

bool PointInShelter(Vector3 worldPos, const std::vector<Building>& buildings) {
    Vector3 sample{worldPos.x, worldPos.y + 0.75f, worldPos.z};
    for (const Building& b : buildings) {
        Vector3 center{b.position.x, b.position.y + 1.9f, b.position.z};
        if (std::fabs(sample.x - center.x) <= 2.5f &&
            std::fabs(sample.y - center.y) <= 2.0f &&
            std::fabs(sample.z - center.z) <= 2.5f) {
            return true;
        }
    }
    return false;
}

bool RayHitGround(Vector2 mouse, Camera3D camera, Vector3* hit) {
    Ray ray = GetMouseRay(mouse, camera);
    if (std::fabs(ray.direction.y) < 1e-5f)
        return false;
    float t = -ray.position.y / ray.direction.y;
    if (t < 0.0f)
        return false;
    hit->x = ray.position.x + ray.direction.x * t;
    hit->y = 0.0f;
    hit->z = ray.position.z + ray.direction.z * t;
    return true;
}

void NotifyWeapon(GameState& game, const char* name) {
    std::snprintf(game.weaponMessage, sizeof(game.weaponMessage), "Weapon: %s", name);
    game.weaponMessageTimer = 3.0f;
}

void ResetGame(GameState& game) {
    game = GameState{};
    game.player.health = kMaxHealth;
    game.player.position = {0.0f, 0.0f, 0.0f};
    game.player.destination = game.player.position;

    game.buildings = {
        {{-8.0f, 0.0f, 6.0f},
         {120, 110, 100, 255},
         {{-8.0f, 1.35f, 6.0f},
          {"Iron Sword", 2.0f, 2.5f, 0.38f, {184, 115, 51, 255}},
          true}},
        {{7.0f, 0.0f, -5.0f},
         {100, 120, 110, 255},
         {{7.0f, 1.35f, -5.0f},
          {"Steel Sword", 3.0f, 2.8f, 0.32f, {199, 209, 230, 255}},
          true}},
        {{0.0f, 0.0f, 9.0f},
         {90, 100, 130, 255},
         {{0.0f, 1.35f, 9.0f},
          {"Storm Blade", 4.5f, 3.2f, 0.28f, {115, 191, 255, 255}},
          true}},
    };

    game.enemies.clear();
    game.enemies.resize(kEnemyCount);
    for (int i = 0; i < kEnemyCount; ++i) {
        float angle = (2.0f * kPi / kEnemyCount) * static_cast<float>(i);
        game.enemies[i].position = {std::cos(angle) * kEnemySpawnRadius, 0.9f, std::sin(angle) * kEnemySpawnRadius};
        game.enemies[i].health = 2.0f;
        game.enemies[i].alive = true;
    }

    game.storm = StormState{};
    game.storm.checkTimer = 5.0f;
    game.score = 0;
    game.gameOver = false;
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

    if (!PointInShelter(game.player.position, game.buildings) && GetRandomValue(0, 999) < 50) {
        game.player.health -= 2;
        if (game.player.health <= 0) {
            game.player.health = 0;
            game.gameOver = true;
        }
    }

    for (auto& enemy : game.enemies) {
        if (!enemy.alive)
            continue;
        if (PointInShelter(enemy.position, game.buildings))
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

    Vector3 toPlayer = FlatTo(enemy.position, game.player.position);
    float playerDist = Vector3Length(toPlayer);
    if (playerDist <= 18.0f) {
        bestScore = playerDist / 1.15f;
        enemy.targetKind = 1;
    }

    for (int i = 0; i < static_cast<int>(game.enemies.size()); ++i) {
        if (i == selfIndex || !game.enemies[i].alive)
            continue;
        float dist = Vector3Distance(enemy.position, game.enemies[i].position);
        if (dist > 18.0f || dist >= bestScore)
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
    Vector3 forward{
        std::sin(game.player.yaw * DEG2RAD),
        0.0f,
        std::cos(game.player.yaw * DEG2RAD)};
    Vector3 center{
        game.player.position.x + forward.x * game.player.weapon.range * 0.5f,
        game.player.position.y + 1.0f,
        game.player.position.z + forward.z * game.player.weapon.range * 0.5f};

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
    for (Building& building : game.buildings) {
        if (!building.loot.active)
            continue;
        if (Vector3Distance(game.player.position, building.loot.position) > 1.2f)
            continue;
        if (building.loot.stats.damage <= game.player.weapon.damage + 0.01f)
            continue;
        game.player.weapon = building.loot.stats;
        building.loot.active = false;
        NotifyWeapon(game, game.player.weapon.name);
    }
}

void UpdatePlayer(GameState& game, Camera3D camera, float dt) {
    auto& p = game.player;
    if (game.gameOver)
        return;

    if (IsMouseButtonPressed(MOUSE_BUTTON_RIGHT)) {
        Vector3 hit{};
        if (RayHitGround(GetMousePosition(), camera, &hit)) {
            p.destination = hit;
            p.hasDestination = true;
        }
    }

    bool grounded = p.position.y <= 0.001f;
    if (grounded && p.verticalVelocity < 0.0f)
        p.verticalVelocity = 0.0f;
    if (IsKeyPressed(KEY_SPACE) && grounded)
        p.verticalVelocity = 6.0f;

    p.verticalVelocity += -20.0f * dt;
    p.position.y += p.verticalVelocity * dt;
    if (p.position.y < 0.0f) {
        p.position.y = 0.0f;
        p.verticalVelocity = 0.0f;
    }

    Vector3 horizontal{0.0f, 0.0f, 0.0f};
    if (p.hasDestination) {
        Vector3 toDest = FlatTo(p.position, p.destination);
        float dist = Vector3Length(toDest);
        if (dist <= 0.2f) {
            p.hasDestination = false;
        } else {
            horizontal = Vector3Scale(Vector3Normalize(toDest), 5.0f);
            float targetYaw = std::atan2(toDest.x, toDest.z) * RAD2DEG;
            p.yaw = Lerp(p.yaw, targetYaw, 14.0f * dt);
        }
    }

    p.position.x += horizontal.x * dt;
    p.position.z += horizontal.z * dt;

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
            if (distance > 0.01f) {
                float yaw = std::atan2(toTarget.x, toTarget.z) * RAD2DEG;
                (void)yaw;
            }
            continue;
        }

        enemy.attackTimer -= dt;
        if (enemy.attackTimer > 0.0f)
            continue;
        enemy.attackTimer = 1.2f;

        if (enemy.targetKind == 1) {
            DamagePlayer(game, 1);
        } else if (enemy.targetKind == 2 && enemy.targetEnemy >= 0) {
            Enemy& other = game.enemies[enemy.targetEnemy];
            other.health -= 1.0f;
            if (other.health <= 0.0f)
                KillEnemy(game, enemy.targetEnemy, false);
        }
    }
}

void DrawBuilding(const Building& building) {
    Vector3 center{building.position.x, building.position.y + 1.5f, building.position.z};
    DrawCube(center, 4.0f, 3.0f, 4.0f, building.color);
    DrawCubeWires(center, 4.0f, 3.0f, 4.0f, ColorAlpha(WHITE, 0.25f));
    Vector3 roof{center.x, center.y + 1.8f, center.z};
    DrawCube(roof, 4.8f, 0.6f, 4.8f, ColorBrightness(building.color, -0.15f));

    if (building.loot.active) {
        DrawCylinder(building.loot.position + Vector3{0.0f, -0.35f, 0.0f}, 0.35f, 0.35f, 0.16f, 12,
                     {64, 64, 72, 255});
        DrawCube(building.loot.position, 0.22f, 0.9f, 0.12f, building.loot.stats.color);
    }
}

void DrawWorld(const GameState& game) {
    DrawPlane({0.0f, 0.0f, 0.0f}, {36.0f, 36.0f}, {45, 55, 70, 255});

    DrawCube({0.0f, 1.5f, 15.0f}, 30.0f, 3.0f, 1.0f, {70, 75, 85, 255});
    DrawCube({0.0f, 1.5f, -15.0f}, 30.0f, 3.0f, 1.0f, {70, 75, 85, 255});
    DrawCube({15.0f, 1.5f, 0.0f}, 1.0f, 3.0f, 30.0f, {70, 75, 85, 255});
    DrawCube({-15.0f, 1.5f, 0.0f}, 1.0f, 3.0f, 30.0f, {70, 75, 85, 255});

    for (const Building& b : game.buildings)
        DrawBuilding(b);

    for (const Enemy& enemy : game.enemies) {
        if (!enemy.alive)
            continue;
        DrawCapsule(enemy.position, enemy.position + Vector3{0.0f, 1.6f, 0.0f}, 0.45f, 8, 8, {180, 60, 60, 255});
    }

    if (game.playerModelLoaded) {
        BoundingBox bounds = GetModelBoundingBox(game.playerModel);
        float height = bounds.max.y - bounds.min.y;
        float scale = height > 0.01f ? 1.8f / height : 1.0f;
        DrawModelEx(game.playerModel, game.player.position, {0.0f, 1.0f, 0.0f}, game.player.yaw, {scale, scale, scale},
                    WHITE);
    } else {
        DrawCapsule(game.player.position, game.player.position + Vector3{0.0f, 1.8f, 0.0f}, 0.35f, 8, 8,
                    {90, 150, 220, 255});
    }

    Vector3 forward{
        std::sin(game.player.yaw * DEG2RAD),
        0.0f,
        std::cos(game.player.yaw * DEG2RAD)};
    float bladeLen = std::strstr(game.player.weapon.name, "Storm")   ? 1.2f
                     : std::strstr(game.player.weapon.name, "Steel") ? 1.05f
                                                                     : 0.95f;
    Vector3 swordPos = game.player.position + Vector3{forward.x * 0.35f + 0.1f, 1.1f, forward.z * 0.35f + 0.1f};
    DrawCube(swordPos, 0.18f, bladeLen, 0.08f, game.player.weapon.color);
}

void DrawHud(const GameState& game) {
    int y = 12;
    auto line = [&](const char* text) {
        DrawText(text, 12, y, 18, RAYWHITE);
        y += 22;
    };

    line("Blade Arena (C++)");
    line("Right-click move | Space jump | A attack | R restart");
    char buf[128];
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
        line("STORM - hide in buildings for shelter and better swords!");
    if (game.weaponMessageTimer > 0.0f)
        line(game.weaponMessage);
    if (game.gameOver)
        line("Defeated - press R to try again");

    int fps = static_cast<int>(1.0f / std::max(game.smoothedFpsDelta, 0.0001f) + 0.5f);
    const char* fpsText = TextFormat("%d FPS", fps);
    int fpsWidth = MeasureText(fpsText, 18);
    DrawText(fpsText, GetScreenWidth() - fpsWidth - 12, 10, 18, RAYWHITE);
}

std::string ResolveModelPath(int argc, char** argv) {
    if (argc > 1 && argv[1][0] != '\0')
        return argv[1];
    const char* env = std::getenv("BLADE_ARENA_MODEL");
    if (env && env[0] != '\0')
        return env;
    return "../../Assets/Models/HumanFigure.glb";
}

} // namespace

int main(int argc, char** argv) {
    const int screenWidth = 1280;
    const int screenHeight = 720;

    SetConfigFlags(FLAG_MSAA_4X_HINT | FLAG_WINDOW_RESIZABLE);
    InitWindow(screenWidth, screenHeight, "Blade Arena (C++)");
    SetTargetFPS(60);

    GameState game;
    ResetGame(game);

    std::string modelPath = ResolveModelPath(argc, argv);
    if (FileExists(modelPath.c_str())) {
        game.playerModel = LoadModel(modelPath.c_str());
        game.playerModelLoaded = game.playerModel.meshCount > 0;
    }

    Camera3D camera{};
    camera.position = {0.0f, 2.5f, -5.0f};
    camera.target = {0.0f, 1.2f, 0.0f};
    camera.up = {0.0f, 1.0f, 0.0f};
    camera.fovy = 60.0f;
    camera.projection = CAMERA_PERSPECTIVE;

    while (!WindowShouldClose()) {
        float dt = GetFrameTime();
        game.smoothedFpsDelta += (dt - game.smoothedFpsDelta) * 0.1f;
        if (game.weaponMessageTimer > 0.0f)
            game.weaponMessageTimer -= dt;

        if (IsKeyPressed(KEY_R))
            ResetGame(game);

        UpdateStorm(game, dt);
        UpdatePlayer(game, camera, dt);
        UpdateEnemies(game, dt);

        Vector3 desiredCam = game.player.position + Vector3{0.0f, 2.5f, -5.0f};
        camera.position = Vector3Lerp(camera.position, desiredCam, 8.0f * dt);
        camera.target = game.player.position + Vector3{0.0f, 1.2f, 0.0f};

        Color sky = game.storm.active ? Color{12, 15, 28, 255} : Color{35, 45, 70, 255};
        if (game.storm.flashTimer > 0.0f)
            sky = Color{180, 190, 255, 255};

        BeginDrawing();
        ClearBackground(sky);

        BeginMode3D(camera);
        DrawWorld(game);
        EndMode3D();

        DrawHud(game);
        EndDrawing();
    }

    if (game.playerModelLoaded)
        UnloadModel(game.playerModel);

    CloseWindow();
    return 0;
}
