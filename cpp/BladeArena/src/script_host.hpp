#pragma once

#include "raylib.h"

#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

struct WeaponStats {
    std::string id;
    std::string name;
    float damage = 1.0f;
    float range = 2.2f;
    float cooldown = 0.45f;
    Color color{255, 255, 255, 255};
};

struct ComboConfig {
    float cooldown = 4.0f;
    float damageScale = 1.0f;
    float rangeScale = 1.0f;
    float dashDistance = 0.0f;
    float dashSpeed = 0.0f;
    float shieldDuration = 0.0f;
    float parryWindow = 0.0f;
    float aoeRadius = 0.0f;
};

struct GameConfig {
    struct PlayerConfig {
        int maxHealth = 5;
        float moveSpeed = 5.5f;
        float riverMoveSpeed = 3.2f;
        float jumpVelocity = 6.5f;
        float gravity = 22.0f;
        std::string starterWeapon = "rusty_blade";
    } player;

    struct EnemyConfig {
        int count = 10;
        float health = 2.0f;
        float speed = 2.5f;
        float attackDamage = 1.0f;
        float attackCooldown = 1.2f;
        float aggroRange = 45.0f;
        float attackRange = 1.4f;
    } enemies;

    struct StormConfig {
        float checkInterval = 60.0f;
        int startChancePermille = 100;
        float duration = 40.0f;
        float lightningInterval = 2.5f;
        int strikeChancePermille = 50;
        int strikeDamage = 2;
    } storm;

    std::unordered_map<std::string, WeaponStats> weapons;
    std::unordered_map<std::string, ComboConfig> combos;

    struct LootCabinConfig {
        std::string weaponId;
        float x = 0.0f;
        float z = 0.0f;
        Color cabinColor{130, 105, 85, 255};
    };
    std::vector<LootCabinConfig> lootCabins;

    const WeaponStats* FindWeapon(const std::string& id) const;
    WeaponStats GetStarterWeapon() const;
};

class ScriptHost {
  public:
    bool Init(const std::string& scriptsDir);
    void Shutdown();

    bool Reload(GameConfig& outConfig);
    bool PollHotReload(GameConfig& outConfig);

    const std::string& LastStatus() const { return status_; }
    const std::string& ScriptsDir() const { return scriptsDir_; }

  private:
    struct lua_State* lua_ = nullptr;
    std::string scriptsDir_;
    std::string configPath_;
    std::string status_ = "Lua not loaded";
    std::int64_t lastModTime_ = 0;
    float pollTimer_ = 0.0f;

    bool LoadConfigFile(GameConfig& outConfig);
    static std::int64_t FileModTime(const std::string& path);
};
