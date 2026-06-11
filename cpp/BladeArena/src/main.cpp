#include "raylib.h"
#include "raymath.h"
#include "script_host.hpp"

#define RLIGHTS_IMPLEMENTATION
#include "rlights.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

constexpr float kMapHalfSize = 200.0f;
constexpr float kPi = 3.14159265f;

ScriptHost gScripts;

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

enum class TreeRenderMode { Deciduous, Evergreen };

bool IsEvergreenTreeMode(const GameConfig& config) {
    const std::string& mode = config.world.treeMode;
    return mode != "deciduous" && mode != "round" && mode != "sphere";
}

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

struct ComboCooldowns {
    float stonestep = 0.0f;
    float apexParry = 0.0f;
    float velocityStrike = 0.0f;
    float shatterStep = 0.0f;
    float dashSever = 0.0f;
};

struct PlayerState {
    Vector3 position{0.0f, 0.0f, 0.0f};
    float yaw = 0.0f;
    float pitch = 0.0f;
    Vector3 destination{0.0f, 0.0f, 0.0f};
    bool hasDestination = false;
    float verticalVelocity = 0.0f;
    int health = 5;
    WeaponStats weapon;
    float attackCooldown = 0.0f;
    ComboCooldowns comboCd;
    float parryWindow = 0.0f;
    float stonestepShield = 0.0f;
    bool isDashing = false;
    Vector3 dashDirection{0.0f, 0.0f, 0.0f};
    float dashRemaining = 0.0f;
    float dashSpeed = 0.0f;
    float comboFxTimer = 0.0f;
    float comboFxRadius = 0.0f;
    Color comboFxColor{255, 255, 255, 180};
    bool shatterSlamPending = false;
    float walkPhase = 0.0f;
    float walkAnimBlend = 0.0f;
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
    ModelAnimation* playerAnimations = nullptr;
    int playerAnimCount = 0;
    int playerAnimFrame = 0;
    float playerAnimAccum = 0.0f;
    bool playerSkeletonAnim = false;
    bool playerModelLoaded = false;
    float playerModelScale = 1.0f;
    float playerModelFeetOffset = 0.0f;
    float playerModelGroundLift = 0.03f;
    float playerModelSoleY = 0.0f;
    float playerModelPivotY = 0.0f;
    Vector3 playerModelCenterOffset{0.0f, 0.0f, 0.0f};
    float playerModelYawOffset = 180.0f;
    Shader characterShader{};
    bool characterShaderLoaded = false;
    Light sunLight{};
    GameConfig config;
    char scriptHudLine[128] = "";
};

void ClampToMap(Vector3& pos);
void KillEnemy(GameState& game, int index, bool awardScore);

std::string ResolveScriptsDir() {
    const char* candidates[] = {
        "/workspace/cpp/BladeArena/scripts/game",
        "scripts/game",
        "../scripts/game",
        "../../scripts/game",
    };
    for (const char* dir : candidates) {
        std::string path = std::string(dir) + "/config.lua";
        if (FileExists(path.c_str()))
            return dir;
    }
    return "/workspace/cpp/BladeArena/scripts/game";
}

const ComboConfig* ComboCfg(const GameConfig& config, const char* id) {
    auto it = config.combos.find(id);
    return it == config.combos.end() ? nullptr : &it->second;
}

void ApplyLiveConfig(GameState& game) {
    if (const WeaponStats* weapon = game.config.FindWeapon(game.player.weapon.id))
        game.player.weapon = *weapon;
    std::snprintf(game.scriptHudLine, sizeof(game.scriptHudLine), "Lua: %s", gScripts.LastStatus().c_str());
}

Font gHudFont{};
bool gHudFontReady = false;
constexpr float kHudFontSize = 18.0f;
constexpr float kHudLineSpacing = 2.0f;

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

// Match the flat tops of the 30 m terrain tiles drawn around the player.
float TerrainSurfaceY(float x, float z, Vector3 refPos) {
    constexpr float kCell = 30.0f;
    int ix = static_cast<int>(std::round((x - refPos.x) / kCell));
    int iz = static_cast<int>(std::round((z - refPos.z) / kCell));
    float cx = refPos.x + static_cast<float>(ix) * kCell;
    float cz = refPos.z + static_cast<float>(iz) * kCell;
    return TerrainHeight(cx, cz);
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

    for (int i = 0; i < 380; ++i) {
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

    for (int i = 0; i < 320; ++i) {
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

const char* ResolveHudFontPath() {
    const char* candidates[] = {
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    };
    for (const char* path : candidates) {
        if (FileExists(path))
            return path;
    }
    return nullptr;
}

void LoadHudFont() {
    const char* path = ResolveHudFontPath();
    if (path == nullptr)
        return;
    gHudFont = LoadFontEx(path, 48, nullptr, 0);
    if (gHudFont.glyphs != nullptr)
        gHudFontReady = true;
}

void DrawHudText(int x, int y, const char* text, Color color = RAYWHITE) {
    if (gHudFontReady) {
        DrawTextEx(gHudFont, text, {static_cast<float>(x), static_cast<float>(y)}, kHudFontSize, kHudLineSpacing,
                   color);
        return;
    }
    DrawText(text, x, y, static_cast<int>(kHudFontSize), color);
}

int HudTextWidth(const char* text) {
    if (gHudFontReady) {
        Vector2 size = MeasureTextEx(gHudFont, text, kHudFontSize, kHudLineSpacing);
        return static_cast<int>(size.x + 0.5f);
    }
    return MeasureText(text, static_cast<int>(kHudFontSize));
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

float ComputeMeshMinY(const Model& model) {
    float minY = 1e9f;
    for (int m = 0; m < model.meshCount; ++m) {
        const Mesh& mesh = model.meshes[m];
        if (mesh.vertices == nullptr)
            continue;
        for (int i = 0; i < mesh.vertexCount; ++i)
            minY = std::min(minY, mesh.vertices[i * 3 + 1]);
    }
    return minY < 1e8f ? minY : 0.0f;
}

float ComputeVisualSoleY(const Model& model, float meshMinY, float meshMaxY) {
    float bandTop = meshMinY + std::max((meshMaxY - meshMinY) * 0.12f, 0.025f);
    std::vector<float> ys;
    ys.reserve(512);
    for (int m = 0; m < model.meshCount; ++m) {
        const Mesh& mesh = model.meshes[m];
        if (mesh.vertices == nullptr)
            continue;
        for (int i = 0; i < mesh.vertexCount; ++i) {
            float y = mesh.vertices[i * 3 + 1];
            if (y <= bandTop)
                ys.push_back(y);
        }
    }
    if (ys.empty())
        return meshMinY;
    std::sort(ys.begin(), ys.end());
    size_t idx = static_cast<size_t>(static_cast<float>(ys.size()) * 0.92f);
    if (idx >= ys.size())
        idx = ys.size() - 1;
    return ys[idx];
}

void DownscaleModelTextures(Model& model, int maxSize) {
    static const int kTextureMaps[] = {MATERIAL_MAP_ALBEDO, MATERIAL_MAP_NORMAL, MATERIAL_MAP_ROUGHNESS,
                                       MATERIAL_MAP_OCCLUSION};
    for (int i = 0; i < model.materialCount; ++i) {
        for (int mapType : kTextureMaps) {
            Texture2D tex = model.materials[i].maps[mapType].texture;
            if (tex.id == 0 || tex.width <= maxSize || tex.height <= maxSize)
                continue;
            Image image = LoadImageFromTexture(tex);
            ImageResize(&image, maxSize, maxSize);
            Texture2D resized = LoadTextureFromImage(image);
            model.materials[i].maps[mapType].texture = resized;
            UnloadImage(image);
            UnloadTexture(tex);
        }
    }
}

void SetupPlayerModel(GameState& game, const char* path) {
    if (!FileExists(path))
        return;

    game.playerModel = LoadModel(path);
    if (game.playerModel.meshCount <= 0)
        return;

    DownscaleModelTextures(game.playerModel, 512);

    game.playerModelLoaded = true;
    BoundingBox bounds = GetModelBoundingBox(game.playerModel);
    float height = bounds.max.y - bounds.min.y;
    game.playerModelScale = height > 0.01f ? 1.85f / height : 1.85f;
    float meshMinY = ComputeMeshMinY(game.playerModel);
    float scaledHeight = height * game.playerModelScale;
    float soleY = ComputeVisualSoleY(game.playerModel, meshMinY, bounds.max.y);
    game.playerModelSoleY = soleY;
    game.playerModelPivotY = meshMinY;
    game.playerModelFeetOffset = meshMinY * game.playerModelScale;
    float soleGap = (soleY - meshMinY) * game.playerModelScale;
    game.playerModelGroundLift = soleGap + std::max(0.14f, scaledHeight * 0.06f);
    game.playerModelCenterOffset = {(bounds.min.x + bounds.max.x) * 0.5f, 0.0f, (bounds.min.z + bounds.max.z) * 0.5f};

    game.playerAnimations = LoadModelAnimations(path, &game.playerAnimCount);
    game.playerSkeletonAnim =
        game.playerAnimations != nullptr && game.playerAnimCount > 0 &&
        IsModelAnimationValid(game.playerModel, game.playerAnimations[0]);
    if (game.playerAnimCount > 0) {
        TraceLog(LOG_INFO, "Player animations: count=%d valid=%s frames=%d bones=%d",
                 game.playerAnimCount, game.playerSkeletonAnim ? "yes" : "no",
                 game.playerAnimations[0].frameCount, game.playerAnimations[0].boneCount);
    }

    if (!game.characterShaderLoaded)
        SetupCharacterShader(game);
}

void UpdatePlayerSkeleton(GameState& game, bool grounded, float dt) {
    if (!game.playerSkeletonAnim || game.playerAnimCount <= 0)
        return;

    ModelAnimation anim = game.playerAnimations[0];
    if (anim.frameCount <= 0)
        return;

    bool playWalk = grounded && game.player.walkAnimBlend > 0.12f;
    if (playWalk) {
        float moveSpeed = std::clamp(game.player.walkAnimBlend * 5.5f, 0.5f, 5.5f);
        float cycleSeconds = std::clamp(5.8f / moveSpeed, 0.72f, 1.05f);
        game.playerAnimAccum += dt * static_cast<float>(anim.frameCount) / cycleSeconds;
        while (game.playerAnimAccum >= 1.0f) {
            game.playerAnimAccum -= 1.0f;
            game.playerAnimFrame = (game.playerAnimFrame + 1) % anim.frameCount;
        }
    } else {
        game.playerAnimAccum = 0.0f;
        game.playerAnimFrame = 0;
    }

    UpdateModelAnimation(game.playerModel, anim, game.playerAnimFrame);
    UpdateModelAnimationBones(game.playerModel, anim, game.playerAnimFrame);
}

void UpdateWalkAnimation(PlayerState& p, float horizontalSpeed, bool grounded, float dt) {
    float targetBlend = 0.0f;
    float phaseSpeed = 0.0f;

    if (grounded && p.isDashing) {
        targetBlend = 1.15f;
        phaseSpeed = 14.5f;
    } else if (grounded && horizontalSpeed > 0.05f) {
        targetBlend = std::clamp(horizontalSpeed / 4.5f, 0.55f, 1.0f);
        phaseSpeed = 8.5f + horizontalSpeed * 1.35f;
    }

    p.walkAnimBlend = Lerp(p.walkAnimBlend, targetBlend, 12.0f * dt);
    if (p.walkAnimBlend > 0.02f)
        p.walkPhase += phaseSpeed * dt;
    else
        p.walkPhase = Lerp(p.walkPhase, 0.0f, 8.0f * dt);
}

struct WalkPose {
    float bobY = 0.0f;
    float squashY = 1.0f;
    float pitchDeg = 0.0f;
    float rollDeg = 0.0f;
    Vector3 footShift{0.0f, 0.0f, 0.0f};
};

WalkPose ComputeWalkPose(float blend, float phase, Vector3 forward, Vector3 right) {
    WalkPose pose;
    if (blend <= 0.001f)
        return pose;

    float sinP = std::sin(phase);
    float cosP = std::cos(phase);
    float sin2P = std::sin(phase * 2.0f);
    float cos2P = std::cos(phase * 2.0f);

    pose.bobY = (1.0f - cos2P) * 0.5f * 0.07f * blend;
    pose.squashY = 1.0f - 0.04f * (1.0f - cos2P) * 0.5f * blend;
    pose.pitchDeg = sinP * 8.0f * blend;
    pose.rollDeg = cosP * 7.0f * blend;

    float lateral = sinP * 0.05f * blend;
    float stride = cosP * 0.03f * blend;
    pose.footShift.x = right.x * lateral + forward.x * stride;
    pose.footShift.z = right.z * lateral + forward.z * stride;
    return pose;
}

void DrawModelWithTint(Model model, Matrix transform, Color tint) {
    model.transform = MatrixMultiply(model.transform, transform);
    for (int i = 0; i < model.meshCount; ++i) {
        Color color = model.materials[model.meshMaterial[i]].maps[MATERIAL_MAP_DIFFUSE].color;
        Color colorTint{
            static_cast<unsigned char>((color.r * tint.r) / 255),
            static_cast<unsigned char>((color.g * tint.g) / 255),
            static_cast<unsigned char>((color.b * tint.b) / 255),
            static_cast<unsigned char>((color.a * tint.a) / 255),
        };
        model.materials[model.meshMaterial[i]].maps[MATERIAL_MAP_DIFFUSE].color = colorTint;
        DrawMesh(model.meshes[i], model.materials[model.meshMaterial[i]], model.transform);
        model.materials[model.meshMaterial[i]].maps[MATERIAL_MAP_DIFFUSE].color = color;
    }
}

void DrawModelWithEuler(Model model, Vector3 position, Vector3 rotationDeg, Vector3 scale, Color tint) {
    Matrix matScale = MatrixScale(scale.x, scale.y, scale.z);
    Matrix matRotX = MatrixRotateX(rotationDeg.x * DEG2RAD);
    Matrix matRotY = MatrixRotateY(rotationDeg.y * DEG2RAD);
    Matrix matRotZ = MatrixRotateZ(rotationDeg.z * DEG2RAD);
    Matrix matRot = MatrixMultiply(matRotY, MatrixMultiply(matRotX, matRotZ));
    Matrix matTranslation = MatrixTranslate(position.x, position.y, position.z);
    Matrix transform = MatrixMultiply(MatrixMultiply(matScale, matRot), matTranslation);
    DrawModelWithTint(model, transform, tint);
}

void DrawModelWithFootAt(Model model, Vector3 footWorld, Vector3 footModelPoint, Vector3 rotationDeg,
                         Vector3 scale, Color tint) {
    Matrix matScale = MatrixScale(scale.x, scale.y, scale.z);
    Matrix matRotX = MatrixRotateX(rotationDeg.x * DEG2RAD);
    Matrix matRotY = MatrixRotateY(rotationDeg.y * DEG2RAD);
    Matrix matRotZ = MatrixRotateZ(rotationDeg.z * DEG2RAD);
    Matrix matRot = MatrixMultiply(matRotY, MatrixMultiply(matRotX, matRotZ));

    Vector3 scaledFoot{
        footModelPoint.x * scale.x,
        footModelPoint.y * scale.y,
        footModelPoint.z * scale.z,
    };
    Vector3 rotatedFoot = Vector3Transform(scaledFoot, matRot);
    Vector3 drawPos = Vector3Subtract(footWorld, rotatedFoot);

    Matrix matTranslation = MatrixTranslate(drawPos.x, drawPos.y, drawPos.z);
    Matrix transform = MatrixMultiply(MatrixMultiply(matScale, matRot), matTranslation);
    DrawModelWithTint(model, transform, tint);
}

void NotifyWeapon(GameState& game, const std::string& name) {
    std::snprintf(game.weaponMessage, sizeof(game.weaponMessage), "Weapon: %s", name.c_str());
    game.weaponMessageTimer = 3.0f;
}

void NotifyCombo(GameState& game, const char* name, Color fxColor, float fxRadius) {
    std::snprintf(game.weaponMessage, sizeof(game.weaponMessage), "%s", name);
    game.weaponMessageTimer = 2.2f;
    game.player.comboFxTimer = 0.35f;
    game.player.comboFxColor = fxColor;
    game.player.comboFxRadius = fxRadius;
}

Vector3 PlayerForward(const PlayerState& p) {
    return {std::sin(p.yaw * DEG2RAD), 0.0f, std::cos(p.yaw * DEG2RAD)};
}

Vector3 PlayerLookForward(const PlayerState& p) {
    float yawRad = p.yaw * DEG2RAD;
    float pitchRad = p.pitch * DEG2RAD;
    float cosPitch = std::cos(pitchRad);
    return {cosPitch * std::sin(yawRad), std::sin(pitchRad), cosPitch * std::cos(yawRad)};
}

Vector3 PlayerMoveRight(const PlayerState& p) {
    float yawRad = p.yaw * DEG2RAD;
    return {std::cos(yawRad), 0.0f, -std::sin(yawRad)};
}

void UpdatePlayerLook(PlayerState& p) {
    if (!IsWindowFocused())
        return;
    Vector2 delta = GetMouseDelta();
    constexpr float kMouseSensitivity = 0.12f;
    p.yaw += delta.x * kMouseSensitivity;
    p.pitch -= delta.y * kMouseSensitivity;
    p.pitch = std::clamp(p.pitch, -89.0f, 89.0f);

    // Re-center cursor so mouse look never hits the screen edge.
    SetMousePosition(GetScreenWidth() / 2, GetScreenHeight() / 2);
}

void StartDash(PlayerState& p, Vector3 direction, float distance, float speed) {
    float len = Vector3Length(direction);
    if (len < 0.01f)
        direction = PlayerForward(p);
    else
        direction = Vector3Scale(direction, 1.0f / len);
    p.isDashing = true;
    p.dashDirection = direction;
    p.dashRemaining = distance;
    p.dashSpeed = speed;
    p.hasDestination = false;
}

void TickComboCooldowns(PlayerState& p, float dt) {
    p.comboCd.stonestep = std::max(0.0f, p.comboCd.stonestep - dt);
    p.comboCd.apexParry = std::max(0.0f, p.comboCd.apexParry - dt);
    p.comboCd.velocityStrike = std::max(0.0f, p.comboCd.velocityStrike - dt);
    p.comboCd.shatterStep = std::max(0.0f, p.comboCd.shatterStep - dt);
    p.comboCd.dashSever = std::max(0.0f, p.comboCd.dashSever - dt);
    p.parryWindow = std::max(0.0f, p.parryWindow - dt);
    p.stonestepShield = std::max(0.0f, p.stonestepShield - dt);
    p.comboFxTimer = std::max(0.0f, p.comboFxTimer - dt);
}

void DealDamageInRadius(GameState& game, Vector3 center, float radius, float damage, bool awardScore) {
    for (int i = 0; i < static_cast<int>(game.enemies.size()); ++i) {
        if (!game.enemies[i].alive)
            continue;
        if (Vector3Distance(center, game.enemies[i].position) <= radius) {
            game.enemies[i].health -= damage;
            if (game.enemies[i].health <= 0.0f)
                KillEnemy(game, i, awardScore);
        }
    }
}

void DealDamageAlongPath(GameState& game, Vector3 from, Vector3 to, float width, float damage, bool awardScore) {
    Vector3 delta = FlatTo(from, to);
    float length = Vector3Length(delta);
    if (length < 0.01f)
        return;
    Vector3 dir = Vector3Scale(delta, 1.0f / length);
    int steps = static_cast<int>(length / 0.6f) + 1;
    for (int s = 0; s <= steps; ++s) {
        float t = static_cast<float>(s) / static_cast<float>(steps);
        Vector3 sample{from.x + dir.x * length * t, from.y, from.z + dir.z * length * t};
        DealDamageInRadius(game, sample, width, damage, awardScore);
    }
}

void CounterAfterParry(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "apex_parry");
    float damageScale = cfg ? cfg->damageScale : 2.5f;
    float radius = cfg ? cfg->aoeRadius : 2.2f;
    Vector3 forward = PlayerForward(game.player);
    Vector3 center{game.player.position.x + forward.x * 1.5f, game.player.position.y + 1.0f,
                   game.player.position.z + forward.z * 1.5f};
    DealDamageInRadius(game, center, radius, game.player.weapon.damage * damageScale, true);
}

void PlayerAttackScaled(GameState& game, float damageScale, float rangeScale) {
    Vector3 forward = PlayerForward(game.player);
    float range = game.player.weapon.range * rangeScale;
    Vector3 center{game.player.position.x + forward.x * range * 0.5f, game.player.position.y + 1.0f,
                   game.player.position.z + forward.z * range * 0.5f};
    DealDamageInRadius(game, center, range * 0.55f, game.player.weapon.damage * damageScale, true);
}

void ComboStonestep(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "stonestep");
    auto& p = game.player;
    if (p.comboCd.stonestep > 0.0f)
        return;
    p.comboCd.stonestep = cfg ? cfg->cooldown : 4.0f;
    p.stonestepShield = cfg ? cfg->shieldDuration : 0.45f;
    Vector3 back = Vector3Scale(PlayerForward(p), -1.0f);
    StartDash(p, back, cfg ? cfg->dashDistance : 2.8f, cfg ? cfg->dashSpeed : 16.0f);
    NotifyCombo(game, "Stonestep", {160, 165, 175, 200}, 1.6f);
}

void ComboApexParry(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "apex_parry");
    auto& p = game.player;
    if (p.comboCd.apexParry > 0.0f)
        return;
    p.comboCd.apexParry = cfg ? cfg->cooldown : 5.0f;
    p.parryWindow = cfg ? cfg->parryWindow : 0.5f;
    p.hasDestination = false;
    NotifyCombo(game, "Apex Parry", {120, 200, 255, 220}, 2.0f);
}

void ComboVelocityStrike(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "velocity_strike");
    auto& p = game.player;
    if (p.comboCd.velocityStrike > 0.0f)
        return;
    p.comboCd.velocityStrike = cfg ? cfg->cooldown : 3.0f;
    StartDash(p, PlayerForward(p), cfg ? cfg->dashDistance : 4.5f, cfg ? cfg->dashSpeed : 22.0f);
    PlayerAttackScaled(game, cfg ? cfg->damageScale : 2.2f, cfg ? cfg->rangeScale : 1.35f);
    NotifyCombo(game, "Velocity Strike", {255, 210, 80, 220}, 2.8f);
}

void ComboShatterStep(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "shatter_step");
    auto& p = game.player;
    if (p.comboCd.shatterStep > 0.0f)
        return;
    p.comboCd.shatterStep = cfg ? cfg->cooldown : 5.0f;
    p.shatterSlamPending = true;
    StartDash(p, PlayerForward(p), cfg ? cfg->dashDistance : 3.2f, cfg ? cfg->dashSpeed : 20.0f);
    NotifyCombo(game, "Shatter-Step", {180, 130, 255, 220}, 3.2f);
}

void ComboDashAndSever(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "dash_sever");
    auto& p = game.player;
    if (p.comboCd.dashSever > 0.0f)
        return;
    float dashDistance = cfg ? cfg->dashDistance : 5.5f;
    p.comboCd.dashSever = cfg ? cfg->cooldown : 4.0f;
    Vector3 start = p.position;
    Vector3 forward = PlayerForward(p);
    StartDash(p, forward, dashDistance, cfg ? cfg->dashSpeed : 24.0f);
    Vector3 end{start.x + forward.x * dashDistance, start.y, start.z + forward.z * dashDistance};
    DealDamageAlongPath(game, start, end, 1.1f, p.weapon.damage * (cfg ? cfg->damageScale : 1.7f), true);
    NotifyCombo(game, "Dash & Sever", {255, 90, 90, 220}, 2.4f);
}

void ResolveShatterSlam(GameState& game) {
    const ComboConfig* cfg = ComboCfg(game.config, "shatter_step");
    auto& p = game.player;
    if (!p.shatterSlamPending)
        return;
    p.shatterSlamPending = false;
    Vector3 slam{p.position.x, p.position.y + 0.5f, p.position.z};
    DealDamageInRadius(game, slam, cfg ? cfg->aoeRadius : 2.8f, p.weapon.damage * (cfg ? cfg->damageScale : 1.6f), true);
    p.comboFxTimer = 0.45f;
    p.comboFxColor = {180, 130, 255, 220};
    p.comboFxRadius = 3.2f;
}

void UpdateDashMovement(GameState& game, float dt) {
    auto& p = game.player;
    if (!p.isDashing || p.dashRemaining <= 0.0f)
        return;
    float step = p.dashSpeed * dt;
    if (step > p.dashRemaining)
        step = p.dashRemaining;
    p.position.x += p.dashDirection.x * step;
    p.position.z += p.dashDirection.z * step;
    p.dashRemaining -= step;
    if (p.dashRemaining <= 0.01f) {
        p.isDashing = false;
        ResolveShatterSlam(game);
    }
    ClampToMap(p.position);
}

void TryComboInput(GameState& game) {
    if (game.gameOver)
        return;
    if (IsKeyPressed(KEY_Q))
        ComboStonestep(game);
    if (IsKeyPressed(KEY_E))
        ComboApexParry(game);
    if (IsKeyPressed(KEY_F))
        ComboVelocityStrike(game);
    if (IsKeyPressed(KEY_V))
        ComboShatterStep(game);
    if (IsKeyPressed(KEY_C))
        ComboDashAndSever(game);
}

void BuildCabinsFromConfig(GameState& game) {
    game.cabins.clear();
    for (const GameConfig::LootCabinConfig& loot : game.config.lootCabins) {
        const WeaponStats* weapon = game.config.FindWeapon(loot.weaponId);
        if (!weapon)
            continue;
        float y = TerrainHeight(loot.x, loot.z);
        Cabin cabin{};
        cabin.position = {loot.x, y, loot.z};
        cabin.color = loot.cabinColor;
        cabin.loot.position = {loot.x, y + 1.35f, loot.z};
        cabin.loot.stats = *weapon;
        cabin.loot.active = true;
        game.cabins.push_back(cabin);
    }
}

void SpawnEnemies(GameState& game) {
    const int count = std::max(1, game.config.enemies.count);
    game.enemies.clear();
    game.enemies.resize(static_cast<size_t>(count));
    for (int i = 0; i < count; ++i) {
        unsigned h = WorldSeed(static_cast<unsigned>(i * 1597334677U + 42U));
        float angle = static_cast<float>(h % 6283) / 1000.0f;
        float radius = 45.0f + static_cast<float>((h / 6283U) % 80U);
        float x = std::cos(angle) * radius;
        float z = std::sin(angle) * radius;
        float y = TerrainHeight(x, z);
        game.enemies[i].position = {x, y + 0.9f, z};
        game.enemies[i].health = game.config.enemies.health;
        game.enemies[i].alive = true;
    }
}

void ResetGameplay(GameState& game) {
    Model model = game.playerModel;
    ModelAnimation* animations = game.playerAnimations;
    int animCount = game.playerAnimCount;
    bool skeletonAnim = game.playerSkeletonAnim;
    bool modelLoaded = game.playerModelLoaded;
    float modelScale = game.playerModelScale;
    float feetOffset = game.playerModelFeetOffset;
    float groundLift = game.playerModelGroundLift;
    float soleY = game.playerModelSoleY;
    float pivotY = game.playerModelPivotY;
    Vector3 centerOffset = game.playerModelCenterOffset;
    float yawOffset = game.playerModelYawOffset;
    Shader characterShader = game.characterShader;
    bool characterShaderLoaded = game.characterShaderLoaded;
    Light sunLight = game.sunLight;
    WorldMap world = game.world;

    game.player = PlayerState{};
    game.player.health = game.config.player.maxHealth;
    game.player.weapon = game.config.GetStarterWeapon();
    Vector3 spawn{0.0f, 0.0f, 0.0f};
    game.player.position = {0.0f, TerrainSurfaceY(0.0f, 0.0f, spawn), 0.0f};
    game.player.destination = game.player.position;

    game.playerModel = model;
    game.playerAnimations = animations;
    game.playerAnimCount = animCount;
    game.playerSkeletonAnim = skeletonAnim;
    game.playerAnimFrame = 0;
    game.playerAnimAccum = 0.0f;
    game.playerModelLoaded = modelLoaded;
    game.playerModelScale = modelScale;
    game.playerModelFeetOffset = feetOffset;
    game.playerModelGroundLift = groundLift;
    game.playerModelSoleY = soleY;
    game.playerModelPivotY = pivotY;
    game.playerModelCenterOffset = centerOffset;
    game.playerModelYawOffset = yawOffset;
    game.characterShader = characterShader;
    game.characterShaderLoaded = characterShaderLoaded;
    game.sunLight = sunLight;
    game.world = world;

    BuildCabinsFromConfig(game);
    SpawnEnemies(game);
    game.storm = StormState{};
    game.storm.checkTimer = game.config.storm.checkInterval;
    game.score = 0;
    game.gameOver = false;
    game.weaponMessage[0] = '\0';
    game.weaponMessageTimer = 0.0f;
}

bool RayHitTerrainRay(Ray ray, Vector3* hit) {
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

bool RayHitTerrain(Vector2 screenPos, Camera3D camera, Vector3* hit) {
    return RayHitTerrainRay(GetMouseRay(screenPos, camera), hit);
}

bool RayHitTerrainCrosshair(Camera3D camera, Vector3* hit) {
    Vector2 center{GetScreenWidth() * 0.5f, GetScreenHeight() * 0.5f};
    return RayHitTerrain(center, camera, hit);
}

void ClampToMap(Vector3& pos) {
    pos.x = std::clamp(pos.x, -kMapHalfSize, kMapHalfSize);
    pos.z = std::clamp(pos.z, -kMapHalfSize, kMapHalfSize);
    pos.y = TerrainHeight(pos.x, pos.z);
}

void TryStartStorm(GameState& game) {
    if (game.storm.active)
        return;
    if (GetRandomValue(0, 999) < game.config.storm.startChancePermille) {
        game.storm.active = true;
        game.storm.stormTimer = game.config.storm.duration;
        game.storm.lightningTimer = 1.0f;
    }
}

void StrikeLightning(GameState& game) {
    game.storm.flashTimer = 0.12f;
    if (!PointInCabin(game.player.position, game.cabins) &&
        GetRandomValue(0, 999) < game.config.storm.strikeChancePermille) {
        game.player.health -= game.config.storm.strikeDamage;
        if (game.player.health <= 0) {
            game.player.health = 0;
            game.gameOver = true;
        }
    }
    for (auto& enemy : game.enemies) {
        if (!enemy.alive || PointInCabin(enemy.position, game.cabins))
            continue;
        if (GetRandomValue(0, 999) < game.config.storm.strikeChancePermille)
            enemy.health -= static_cast<float>(game.config.storm.strikeDamage);
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
            game.storm.lightningTimer = game.config.storm.lightningInterval;
            StrikeLightning(game);
        }
        if (game.storm.stormTimer <= 0.0f) {
            game.storm.active = false;
            game.storm.checkTimer = game.config.storm.checkInterval;
        }
        return;
    }

    game.storm.checkTimer -= dt;
    if (game.storm.checkTimer <= 0.0f) {
        game.storm.checkTimer = game.config.storm.checkInterval;
        TryStartStorm(game);
    }
}

void PickEnemyTarget(Enemy& enemy, const GameState& game, int selfIndex) {
    enemy.targetKind = 0;
    enemy.targetEnemy = -1;
    float bestScore = 1e9f;

    float playerDist = Vector3Distance(enemy.position, game.player.position);
    float aggro = game.config.enemies.aggroRange;
    if (playerDist <= aggro) {
        bestScore = playerDist / 1.15f;
        enemy.targetKind = 1;
    }

    for (int i = 0; i < static_cast<int>(game.enemies.size()); ++i) {
        if (i == selfIndex || !game.enemies[i].alive)
            continue;
        float dist = Vector3Distance(enemy.position, game.enemies[i].position);
        if (dist > aggro || dist >= bestScore)
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
    auto& p = game.player;
    if (p.parryWindow > 0.0f) {
        p.parryWindow = 0.0f;
        NotifyCombo(game, "Apex Parry — counter!", {120, 200, 255, 255}, 2.5f);
        CounterAfterParry(game);
        return;
    }
    if (p.stonestepShield > 0.0f)
        return;
    p.health -= amount;
    if (p.health <= 0) {
        p.health = 0;
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
    PlayerAttackScaled(game, 1.0f, 1.0f);
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

    TickComboCooldowns(p, dt);
    TryComboInput(game);
    UpdatePlayerLook(p);

    if (IsMouseButtonPressed(MOUSE_BUTTON_RIGHT)) {
        Vector3 hit{};
        if (RayHitTerrainCrosshair(camera, &hit)) {
            p.destination = hit;
            p.hasDestination = true;
        }
    }

    float groundY = TerrainSurfaceY(p.position.x, p.position.z, p.position);
    bool grounded = p.position.y <= groundY + 0.02f && p.verticalVelocity <= 0.05f;
    if (grounded && p.verticalVelocity < 0.0f)
        p.verticalVelocity = 0.0f;
    if (IsKeyPressed(KEY_SPACE) && grounded)
        p.verticalVelocity = game.config.player.jumpVelocity;

    p.verticalVelocity += -game.config.player.gravity * dt;
    p.position.y += p.verticalVelocity * dt;
    groundY = TerrainSurfaceY(p.position.x, p.position.z, p.position);
    if (p.position.y < groundY) {
        p.position.y = groundY;
        p.verticalVelocity = 0.0f;
        grounded = true;
    }

    if (p.isDashing) {
        UpdateDashMovement(game, dt);
        UpdateWalkAnimation(p, p.dashSpeed, grounded, dt);
        UpdatePlayerSkeleton(game, grounded, dt);
        TryPickupLoot(game);
        return;
    }

    float moveSpeed = IsInRiver(p.position.x, p.position.z) ? game.config.player.riverMoveSpeed
                                                            : game.config.player.moveSpeed;
    Vector3 horizontal{0.0f, 0.0f, 0.0f};

    float moveX = 0.0f;
    float moveZ = 0.0f;
    if (IsKeyDown(KEY_W))
        moveZ += 1.0f;
    if (IsKeyDown(KEY_S))
        moveZ -= 1.0f;
    if (IsKeyDown(KEY_A))
        moveX -= 1.0f;
    if (IsKeyDown(KEY_D))
        moveX += 1.0f;

    if (std::fabs(moveX) > 0.01f || std::fabs(moveZ) > 0.01f) {
        p.hasDestination = false;
        Vector3 forward = PlayerForward(p);
        Vector3 right = PlayerMoveRight(p);
        Vector3 wish = Vector3Add(Vector3Scale(forward, moveZ), Vector3Scale(right, moveX));
        wish.y = 0.0f;
        horizontal = Vector3Scale(Vector3Normalize(wish), moveSpeed);
    } else if (p.hasDestination) {
        Vector3 toDest = FlatTo(p.position, p.destination);
        float dist = Vector3Length(toDest);
        if (dist <= 0.35f) {
            p.hasDestination = false;
        } else {
            horizontal = Vector3Scale(Vector3Normalize(toDest), moveSpeed);
        }
    }

    p.position.x += horizontal.x * dt;
    p.position.z += horizontal.z * dt;
    ClampToMap(p.position);

    UpdateWalkAnimation(p, Vector3Length(horizontal), grounded, dt);
    UpdatePlayerSkeleton(game, grounded, dt);

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

        if (distance > game.config.enemies.attackRange) {
            Vector3 step = Vector3Scale(Vector3Normalize(toTarget), game.config.enemies.speed * dt);
            enemy.position.x += step.x;
            enemy.position.z += step.z;
            enemy.position.y = TerrainHeight(enemy.position.x, enemy.position.z) + 0.9f;
            continue;
        }

        enemy.attackTimer -= dt;
        if (enemy.attackTimer > 0.0f)
            continue;
        enemy.attackTimer = game.config.enemies.attackCooldown;

        if (enemy.targetKind == 1)
            DamagePlayer(game, static_cast<int>(game.config.enemies.attackDamage));
        else if (enemy.targetKind == 2 && enemy.targetEnemy >= 0) {
            Enemy& other = game.enemies[enemy.targetEnemy];
            other.health -= game.config.enemies.attackDamage;
            if (other.health <= 0.0f)
                KillEnemy(game, enemy.targetEnemy, false);
        }
    }
}

void DrawGroundShadow(Vector3 feet, float radius, float alpha) {
    Color shadow{0, 0, 0, static_cast<unsigned char>(std::clamp(alpha, 0.0f, 1.0f) * 255.0f)};
    DrawCylinder({feet.x, feet.y + 0.04f, feet.z}, radius, radius, 0.03f, 8, shadow);
}

void DrawDeciduousTree(const Tree& tree, Vector3 base, bool darkBackdrop, bool simpleLod, int sides) {
    const float trunkH = (darkBackdrop ? 3.0f : 2.5f) * tree.scale;
    const unsigned char trunkR = darkBackdrop ? 72 : 92;
    const unsigned char trunkG = darkBackdrop ? 48 : 58;
    const Color trunk{trunkR, trunkG, 32, 255};
    const Color leaves{darkBackdrop ? 24 : 38, darkBackdrop ? 88 : 118, darkBackdrop ? 38 : 52, 255};

    DrawCylinder(base, 0.2f * tree.scale, 0.26f * tree.scale, trunkH, sides, trunk);
    if (simpleLod)
        return;

    const Vector3 crown{base.x, base.y + trunkH + 0.55f * tree.scale, base.z};
    DrawSphere(crown, (darkBackdrop ? 1.35f : 1.15f) * tree.scale, leaves);
}

void DrawEvergreenTreeMode(const Tree& tree, Vector3 base, bool darkBackdrop, bool simpleLod, int sides,
                           float variant) {
    const float trunkH = (darkBackdrop ? 3.6f : 3.1f) * tree.scale * (0.94f + variant * 0.12f);
    const Color trunk{static_cast<unsigned char>(darkBackdrop ? 68 : 88),
                    static_cast<unsigned char>(darkBackdrop ? 44 : 54), 28, 255};
    const Color foliageDeep{static_cast<unsigned char>(darkBackdrop ? 20 : 30),
                            static_cast<unsigned char>(darkBackdrop ? 78 : 102),
                            static_cast<unsigned char>(darkBackdrop ? 34 : 46), 255};
    const Color foliageBright{static_cast<unsigned char>(darkBackdrop ? 36 : 50),
                              static_cast<unsigned char>(darkBackdrop ? 112 : 142),
                              static_cast<unsigned char>(darkBackdrop ? 46 : 60), 255};

    DrawCylinder(base, 0.16f * tree.scale, 0.22f * tree.scale, trunkH, sides, trunk);

    if (simpleLod) {
        const Vector3 tip{base.x, base.y + trunkH, base.z};
        DrawCylinder(tip, 0.0f, 0.85f * tree.scale, 1.35f * tree.scale, sides, foliageBright);
        return;
    }

    const int whorls = variant > 0.62f ? 4 : 3;
    for (int w = 0; w < whorls; ++w) {
        const float whorlT = static_cast<float>(w) / static_cast<float>(whorls - 1);
        const float whorlY = base.y + trunkH * (0.32f + whorlT * 0.48f);
        const float branchLen = tree.scale * (0.72f - whorlT * 0.22f);
        const int branches = 5 + (w % 2);
        const float pitch = 0.42f + variant * 0.12f - whorlT * 0.1f;
        const float cosPitch = std::cos(pitch);
        const float sinPitch = std::sin(pitch);

        for (int b = 0; b < branches; ++b) {
            const float angle = (2.0f * kPi / static_cast<float>(branches)) * static_cast<float>(b) +
                                variant * 0.9f + static_cast<float>(w) * 0.55f;
            const float bx = std::cos(angle) * branchLen * cosPitch;
            const float by = branchLen * sinPitch;
            const float bz = std::sin(angle) * branchLen * cosPitch;
            const Vector3 branchStart{base.x, whorlY, base.z};
            const Vector3 branchEnd{base.x + bx, whorlY + by, base.z + bz};
            const float branchRadius = tree.scale * (0.07f - whorlT * 0.015f);
            DrawCylinderEx(branchStart, branchEnd, branchRadius, branchRadius * 0.45f, sides, trunk);

            const float coneR = tree.scale * (0.34f - whorlT * 0.08f);
            const float coneH = tree.scale * (0.42f - whorlT * 0.06f);
            const Color branchFoliage = ColorLerp(foliageDeep, foliageBright, 0.2f + whorlT * 0.55f);
            DrawCylinder(branchEnd, 0.0f, coneR, coneH, sides, branchFoliage);
        }
    }

    const Vector3 apex{base.x, base.y + trunkH - 0.08f * tree.scale, base.z};
    const Color apexFoliage = ColorLerp(foliageDeep, foliageBright, 0.75f);
    DrawCylinder(apex, 0.0f, 0.48f * tree.scale, 0.95f * tree.scale, sides, apexFoliage);
}

void DrawTree(const Tree& tree, bool darkBackdrop, bool simpleLod, TreeRenderMode mode) {
    const float y = tree.backdrop ? 0.0f : TerrainHeight(tree.position.x, tree.position.z);
    const Vector3 base{tree.position.x, y, tree.position.z};
    const int sides = simpleLod ? 5 : 8;
    const float variant = Hash01(tree.position.x * 0.41f, tree.position.z * 0.29f);

    if (mode == TreeRenderMode::Evergreen)
        DrawEvergreenTreeMode(tree, base, darkBackdrop, simpleLod, sides, variant);
    else
        DrawDeciduousTree(tree, base, darkBackdrop, simpleLod, sides);
}

void DrawMountain(const Mountain& mountain) {
    Vector3 base = mountain.position;
    float h = mountain.height;
    float r = mountain.radius;
    Color rockBase{72, 68, 62, 255};
    Color rockMid{92, 86, 78, 255};
    Color snow{228, 236, 244, 255};

    DrawCylinder(base, r * 0.95f, r * 0.35f, h * 0.55f, 8, rockBase);
    DrawCylinder({base.x, base.y + h * 0.45f, base.z}, r * 0.55f, r * 0.12f, h * 0.38f, 8, rockMid);
    DrawSphere({base.x, base.y + h * 0.82f, base.z}, r * 0.32f, snow);
}

void DrawCabin(const Cabin& cabin) {
    float baseY = TerrainHeight(cabin.position.x, cabin.position.z);
    Vector3 center{cabin.position.x, baseY + 1.5f, cabin.position.z};
    DrawCube(center, 4.2f, 3.0f, 4.2f, cabin.color);
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

    const int steps = 7;
    const float cell = 30.0f;
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

void DrawBackdropScenery(const WorldMap& world, Vector3 playerPos, TreeRenderMode treeMode) {
    constexpr float kMountainDrawDist = 340.0f;
    for (const Mountain& mountain : world.mountains) {
        if (Vector2Distance({mountain.position.x, mountain.position.z}, {playerPos.x, playerPos.z}) >
            kMountainDrawDist)
            continue;
        DrawMountain(mountain);
    }

    constexpr float kBackdropForestDist = 220.0f;
    for (const Tree& tree : world.backdropForest) {
        float dist = Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z});
        if (dist > kBackdropForestDist)
            continue;
        DrawTree(tree, true, dist > 150.0f, treeMode);
    }
}

void DrawRivers(Vector3 playerPos) {
    for (float z = playerPos.z - 95.0f; z <= playerPos.z + 95.0f; z += 11.0f) {
        if (std::fabs(z) > kMapHalfSize)
            continue;
        float x = RiverCenterX(z);
        float w = RiverWidth(z);
        float y = TerrainHeight(x, z) - 0.15f;
        DrawCube({x, y, z}, w, 0.12f, 10.0f, {45, 130, 195, 210});
    }
}

Vector3 PlayerEyePosition(const GameState& game) {
    Vector3 feet = game.player.position;
    float groundY = TerrainSurfaceY(feet.x, feet.z, feet);
    float baseY = std::max(feet.y, groundY);
    bool airborne = feet.y > groundY + 0.08f || game.player.verticalVelocity > 0.35f;
    float walkBlend = airborne ? 0.0f : game.player.walkAnimBlend;

    float bob = 0.0f;
    if (walkBlend > 0.02f) {
        float phase = game.player.walkPhase;
        bob = (1.0f - std::cos(phase * 2.0f)) * 0.5f * 0.04f * walkBlend;
    }

    constexpr float kEyeHeight = 1.68f;
    return {feet.x, baseY + kEyeHeight + bob, feet.z};
}

void DrawFirstPersonWeapon(const GameState& game, Camera3D camera) {
    Vector3 eye = camera.position;
    Vector3 look = Vector3Subtract(camera.target, camera.position);
    float lookLen = Vector3Length(look);
    if (lookLen < 0.01f)
        return;
    Vector3 forward = Vector3Scale(look, 1.0f / lookLen);
    Vector3 right = Vector3Normalize(Vector3CrossProduct(forward, camera.up));
    Vector3 up = Vector3Normalize(Vector3CrossProduct(right, forward));

    float walkBlend = game.player.walkAnimBlend;
    float sway = std::sin(game.player.walkPhase) * 0.03f * walkBlend;
    float bob = (1.0f - std::cos(game.player.walkPhase * 2.0f)) * 0.5f * 0.02f * walkBlend;

    float bladeLen = game.player.weapon.id == "storm_blade"   ? 0.72f
                     : game.player.weapon.id == "steel_sword" ? 0.62f
                                                              : 0.55f;

    Vector3 hand = Vector3Add(
        eye,
        Vector3Add(Vector3Scale(right, 0.26f + sway), Vector3Add(Vector3Scale(forward, 0.38f), Vector3Scale(up, -0.18f - bob))));

    Vector3 tip = Vector3Add(hand, Vector3Add(Vector3Scale(forward, bladeLen), Vector3Scale(up, 0.03f)));
    DrawCylinderEx(hand, tip, 0.045f, 0.018f, 8, game.player.weapon.color);

    // Simple crosshair guard at blade base.
    Vector3 guardL = Vector3Add(hand, Vector3Scale(right, -0.07f));
    Vector3 guardR = Vector3Add(hand, Vector3Scale(right, 0.07f));
    DrawCylinderEx(guardL, guardR, 0.02f, 0.02f, 6, game.player.weapon.color);
}

void DrawPlayerCharacter(const GameState& game, Camera3D camera) {
    DrawFirstPersonWeapon(game, camera);
}

void DrawWorld(const GameState& game, Camera3D camera) {
    Vector3 playerPos = game.player.position;

    const TreeRenderMode treeMode =
        IsEvergreenTreeMode(game.config) ? TreeRenderMode::Evergreen : TreeRenderMode::Deciduous;

    BeginSceneLighting(game, camera);
    DrawBackdropScenery(game.world, playerPos, treeMode);
    DrawTerrain(playerPos);
    DrawRivers(playerPos);
    EndSceneLighting(game);

    constexpr float kTreeDrawDistance = 95.0f;
    for (const Tree& tree : game.world.trees) {
        float dist = Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z});
        if (dist > kTreeDrawDistance)
            continue;
        if (dist < 70.0f) {
            Vector3 base{tree.position.x, TerrainHeight(tree.position.x, tree.position.z), tree.position.z};
            DrawGroundShadow(base, 0.55f * tree.scale, 0.28f);
        }
    }

    BeginSceneLighting(game, camera);
    for (const Cabin& cabin : game.cabins)
        DrawCabin(cabin);

    for (const Tree& tree : game.world.trees) {
        float dist = Vector2Distance({tree.position.x, tree.position.z}, {playerPos.x, playerPos.z});
        if (dist > kTreeDrawDistance)
            continue;
        DrawTree(tree, false, dist > 55.0f, treeMode);
    }

    for (const Enemy& enemy : game.enemies) {
        if (!enemy.alive)
            continue;
        float y = TerrainHeight(enemy.position.x, enemy.position.z);
        Vector3 base{enemy.position.x, y, enemy.position.z};
        DrawGroundShadow(base, 0.42f, 0.32f);
        DrawCapsule(base, base + Vector3{0.0f, 1.6f, 0.0f}, 0.45f, 8, 8, {180, 60, 60, 255});
    }

    EndSceneLighting(game);

    DrawPlayerCharacter(game, camera);
    if (game.player.comboFxTimer > 0.0f) {
        float t = game.player.comboFxTimer / 0.35f;
        float r = game.player.comboFxRadius * (1.0f - t * 0.5f);
        Color fx = game.player.comboFxColor;
        fx.a = static_cast<unsigned char>(fx.a * t);
        Vector3 fxPos = PlayerEyePosition(game);
        DrawSphere({fxPos.x, fxPos.y - 0.5f, fxPos.z}, r, fx);
    }
    if (game.player.parryWindow > 0.0f) {
        Vector3 eye = PlayerEyePosition(game);
        DrawSphere(eye, 0.55f, {100, 180, 255, 90});
    }
    if (game.player.stonestepShield > 0.0f) {
        Vector3 eye = PlayerEyePosition(game);
        DrawSphere({eye.x, eye.y - 0.35f, eye.z}, 0.45f, {180, 185, 195, 70});
    }
}

void DrawHud(const GameState& game) {
    const int lineHeight = gHudFontReady ? 24 : 22;
    int y = 12;
    auto line = [&](const char* text) {
        DrawHudText(12, y, text);
        y += lineHeight;
    };

    line("Blade Arena — FIRST-PERSON");
    line("Mouse look | WASD move | Right-click move | Space jump | A attack | R restart");
    line("Q Stonestep | E Apex Parry | F Velocity Strike | V Shatter-Step | C Dash & Sever");
    line("Lua: edit scripts/game/config.lua, save = live reload | F5 = force reload");
    if (game.scriptHudLine[0] != '\0')
        line(game.scriptHudLine);
    char buf[160];
    std::snprintf(buf, sizeof(buf), "Health: %d", game.player.health);
    line(buf);
    std::snprintf(buf, sizeof(buf), "Equipped: %s (%.1f dmg)", game.player.weapon.name.c_str(),
                  game.player.weapon.damage);
    line(buf);
    std::snprintf(buf, sizeof(buf), "Trees: %s (world.tree_mode in config.lua)",
                  IsEvergreenTreeMode(game.config) ? "evergreen mode" : "deciduous mode");
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
    DrawHudText(GetScreenWidth() - HudTextWidth(fpsText) - 12, 10, fpsText);

    // First-person crosshair.
    int cx = GetScreenWidth() / 2;
    int cy = GetScreenHeight() / 2;
    DrawLine(cx - 8, cy, cx + 8, cy, {235, 235, 235, 170});
    DrawLine(cx, cy - 8, cx, cy + 8, {235, 235, 235, 170});
}

void UpdateCamera(Camera3D& camera, const GameState& game, float dt) {
    (void)dt;
    Vector3 eye = PlayerEyePosition(game);
    Vector3 lookForward = PlayerLookForward(game.player);

    // True character POV: eyes are the camera, view matches mouse look exactly.
    camera.position = eye;
    camera.target = Vector3Add(eye, Vector3Scale(lookForward, 4.0f));
}

std::string ResolveModelPath(int argc, char** argv) {
    if (argc > 1 && argv[1][0] != '\0')
        return argv[1];
    const char* env = std::getenv("BLADE_ARENA_MODEL");
    if (env && env[0] != '\0')
        return env;

    const char* candidates[] = {
        "/workspace/Assets/Models/HumanFigure_walk.glb",
        "../../Assets/Models/HumanFigure_walk.glb",
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

static void DrawLoadingScreen(const char* status) {
    BeginDrawing();
    ClearBackground({24, 28, 36, 255});
    DrawText("Blade Arena", 40, 40, 28, {220, 225, 235, 255});
    DrawText(status, 40, 84, 20, {170, 180, 195, 255});
    DrawText("The game window will appear here when loading finishes.", 40, 116, 16, {120, 130, 145, 255});
    EndDrawing();
}

int main(int argc, char** argv) {
    SetConfigFlags(FLAG_WINDOW_RESIZABLE);
    InitWindow(1280, 720, "Blade Arena");
    SetTargetFPS(60);
    DisableCursor();
    LoadHudFont();

    for (int i = 0; i < 8; ++i)
        DrawLoadingScreen("Starting...");

    GameState game;
    GenerateWorld(game.world);
    SetupCharacterShader(game);

    DrawLoadingScreen("Loading Lua scripts...");
    if (!gScripts.Init(ResolveScriptsDir())) {
        TraceLog(LOG_WARNING, "SCRIPT: failed to init Lua VM");
    } else if (!gScripts.Reload(game.config)) {
        TraceLog(LOG_WARNING, "SCRIPT: %s", gScripts.LastStatus().c_str());
    }
    ApplyLiveConfig(game);

    DrawLoadingScreen("Loading character model...");
    SetupPlayerModel(game, ResolveModelPath(argc, argv).c_str());
    ResetGameplay(game);

    DrawLoadingScreen("Ready!");

    Camera3D camera{};
    camera.up = {0.0f, 1.0f, 0.0f};
    camera.fovy = 82.0f;
    camera.projection = CAMERA_PERSPECTIVE;
    UpdateCamera(camera, game, 1.0f);

    while (!WindowShouldClose()) {
        float dt = GetFrameTime();
        game.smoothedFpsDelta += (dt - game.smoothedFpsDelta) * 0.1f;
        if (game.weaponMessageTimer > 0.0f)
            game.weaponMessageTimer -= dt;

        if (IsKeyPressed(KEY_R))
            ResetGameplay(game);

        if (IsKeyPressed(KEY_F5) && gScripts.Reload(game.config))
            ApplyLiveConfig(game);
        if (gScripts.PollHotReload(game.config))
            ApplyLiveConfig(game);

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

    if (game.playerAnimations != nullptr)
        UnloadModelAnimations(game.playerAnimations, game.playerAnimCount);
    if (game.playerModelLoaded)
        UnloadModel(game.playerModel);
    if (game.characterShaderLoaded)
        UnloadShader(game.characterShader);
    if (gHudFontReady)
        UnloadFont(gHudFont);
    gScripts.Shutdown();

    CloseWindow();
    return 0;
}
