#include "script_host.hpp"

extern "C" {
#include <lauxlib.h>
#include <lua.h>
#include <lualib.h>
}

#include <sys/stat.h>

#include <algorithm>
#include <cstdio>
#include <cstring>

namespace {

Color ReadColor(lua_State* L, int tableIndex, const char* key, Color fallback) {
    lua_getfield(L, tableIndex, key);
    if (!lua_istable(L, -1)) {
        lua_pop(L, 1);
        return fallback;
    }
    auto channel = [&](const char* name, unsigned char current) {
        lua_getfield(L, -1, name);
        int v = lua_isnumber(L, -1) ? static_cast<int>(lua_tonumber(L, -1)) : current;
        lua_pop(L, 1);
        return static_cast<unsigned char>(std::clamp(v, 0, 255));
    };
    Color c{
        channel("r", fallback.r),
        channel("g", fallback.g),
        channel("b", fallback.b),
        channel("a", fallback.a),
    };
    lua_pop(L, 1);
    return c;
}

float ReadNumber(lua_State* L, int tableIndex, const char* key, float fallback) {
    lua_getfield(L, tableIndex, key);
    float value = fallback;
    if (lua_isnumber(L, -1))
        value = static_cast<float>(lua_tonumber(L, -1));
    lua_pop(L, 1);
    return value;
}

int ReadInt(lua_State* L, int tableIndex, const char* key, int fallback) {
    lua_getfield(L, tableIndex, key);
    int value = fallback;
    if (lua_isnumber(L, -1))
        value = static_cast<int>(lua_tointeger(L, -1));
    lua_pop(L, 1);
    return value;
}

std::string ReadString(lua_State* L, int tableIndex, const char* key, const std::string& fallback) {
    lua_getfield(L, tableIndex, key);
    std::string value = fallback;
    if (lua_isstring(L, -1))
        value = lua_tostring(L, -1);
    lua_pop(L, 1);
    return value;
}

bool ReadTable(lua_State* L, int tableIndex, const char* key) {
    lua_getfield(L, tableIndex, key);
    bool ok = lua_istable(L, -1);
    if (!ok)
        lua_pop(L, 1);
    return ok;
}

void ParseWeapons(lua_State* L, int tableIndex, GameConfig& config) {
    lua_pushnil(L);
    while (lua_next(L, tableIndex) != 0) {
        if (!lua_isstring(L, -2) || !lua_istable(L, -1)) {
            lua_pop(L, 1);
            continue;
        }
        WeaponStats weapon;
        weapon.id = lua_tostring(L, -2);
        int w = lua_gettop(L);
        weapon.name = ReadString(L, w, "name", weapon.id);
        weapon.damage = ReadNumber(L, w, "damage", 1.0f);
        weapon.range = ReadNumber(L, w, "range", 2.2f);
        weapon.cooldown = ReadNumber(L, w, "cooldown", 0.45f);
        weapon.color = ReadColor(L, w, "color", {200, 200, 200, 255});
        config.weapons[weapon.id] = weapon;
        lua_pop(L, 1);
    }
}

void ParseCombos(lua_State* L, int tableIndex, GameConfig& config) {
    lua_pushnil(L);
    while (lua_next(L, tableIndex) != 0) {
        if (!lua_isstring(L, -2) || !lua_istable(L, -1)) {
            lua_pop(L, 1);
            continue;
        }
        ComboConfig combo;
        std::string id = lua_tostring(L, -2);
        int c = lua_gettop(L);
        combo.cooldown = ReadNumber(L, c, "cooldown", combo.cooldown);
        combo.damageScale = ReadNumber(L, c, "damage_scale", combo.damageScale);
        combo.rangeScale = ReadNumber(L, c, "range_scale", combo.rangeScale);
        combo.dashDistance = ReadNumber(L, c, "dash_distance", combo.dashDistance);
        combo.dashSpeed = ReadNumber(L, c, "dash_speed", combo.dashSpeed);
        combo.shieldDuration = ReadNumber(L, c, "shield_duration", combo.shieldDuration);
        combo.parryWindow = ReadNumber(L, c, "parry_window", combo.parryWindow);
        combo.aoeRadius = ReadNumber(L, c, "aoe_radius", combo.aoeRadius);
        config.combos[id] = combo;
        lua_pop(L, 1);
    }
}

void ParseLootCabins(lua_State* L, int tableIndex, GameConfig& config) {
    int count = static_cast<int>(lua_rawlen(L, tableIndex));
    for (int i = 1; i <= count; ++i) {
        lua_rawgeti(L, tableIndex, i);
        if (!lua_istable(L, -1)) {
            lua_pop(L, 1);
            continue;
        }
        GameConfig::LootCabinConfig cabin;
        int t = lua_gettop(L);
        cabin.weaponId = ReadString(L, t, "weapon", "iron_sword");
        cabin.x = ReadNumber(L, t, "x", 0.0f);
        cabin.z = ReadNumber(L, t, "z", 0.0f);
        cabin.cabinColor = ReadColor(L, t, "cabin_color", cabin.cabinColor);
        config.lootCabins.push_back(cabin);
        lua_pop(L, 1);
    }
}

bool ParseConfigTable(lua_State* L, int index, GameConfig& config) {
    if (!lua_istable(L, index))
        return false;

    if (ReadTable(L, index, "player")) {
        int t = lua_gettop(L);
        config.player.maxHealth = ReadInt(L, t, "max_health", config.player.maxHealth);
        config.player.moveSpeed = ReadNumber(L, t, "move_speed", config.player.moveSpeed);
        config.player.riverMoveSpeed = ReadNumber(L, t, "river_move_speed", config.player.riverMoveSpeed);
        config.player.jumpVelocity = ReadNumber(L, t, "jump_velocity", config.player.jumpVelocity);
        config.player.gravity = ReadNumber(L, t, "gravity", config.player.gravity);
        config.player.starterWeapon = ReadString(L, t, "starter_weapon", config.player.starterWeapon);
        lua_pop(L, 1);
    }

    if (ReadTable(L, index, "enemies")) {
        int t = lua_gettop(L);
        config.enemies.count = ReadInt(L, t, "count", config.enemies.count);
        config.enemies.health = ReadNumber(L, t, "health", config.enemies.health);
        config.enemies.speed = ReadNumber(L, t, "speed", config.enemies.speed);
        config.enemies.attackDamage = ReadNumber(L, t, "attack_damage", config.enemies.attackDamage);
        config.enemies.attackCooldown = ReadNumber(L, t, "attack_cooldown", config.enemies.attackCooldown);
        config.enemies.aggroRange = ReadNumber(L, t, "aggro_range", config.enemies.aggroRange);
        config.enemies.attackRange = ReadNumber(L, t, "attack_range", config.enemies.attackRange);
        lua_pop(L, 1);
    }

    if (ReadTable(L, index, "storm")) {
        int t = lua_gettop(L);
        config.storm.checkInterval = ReadNumber(L, t, "check_interval", config.storm.checkInterval);
        config.storm.startChancePermille = ReadInt(L, t, "start_chance_permille", config.storm.startChancePermille);
        config.storm.duration = ReadNumber(L, t, "duration", config.storm.duration);
        config.storm.lightningInterval = ReadNumber(L, t, "lightning_interval", config.storm.lightningInterval);
        config.storm.strikeChancePermille = ReadInt(L, t, "strike_chance_permille", config.storm.strikeChancePermille);
        config.storm.strikeDamage = ReadInt(L, t, "strike_damage", config.storm.strikeDamage);
        lua_pop(L, 1);
    }

    if (ReadTable(L, index, "weapons"))
        ParseWeapons(L, lua_gettop(L), config);
    lua_pop(L, 1);

    if (ReadTable(L, index, "combos"))
        ParseCombos(L, lua_gettop(L), config);
    lua_pop(L, 1);

    if (ReadTable(L, index, "loot_cabins"))
        ParseLootCabins(L, lua_gettop(L), config);
    lua_pop(L, 1);

    return !config.weapons.empty();
}

} // namespace

const WeaponStats* GameConfig::FindWeapon(const std::string& id) const {
    auto it = weapons.find(id);
    return it == weapons.end() ? nullptr : &it->second;
}

WeaponStats GameConfig::GetStarterWeapon() const {
    if (const WeaponStats* weapon = FindWeapon(player.starterWeapon))
        return *weapon;
    if (!weapons.empty())
        return weapons.begin()->second;
    WeaponStats fallback;
    fallback.id = "fallback";
    fallback.name = "Fallback Blade";
    return fallback;
}

bool ScriptHost::Init(const std::string& scriptsDir) {
    Shutdown();
    scriptsDir_ = scriptsDir;
    configPath_ = scriptsDir_ + "/config.lua";

    lua_ = luaL_newstate();
    if (!lua_) {
        status_ = "Failed to create Lua state";
        return false;
    }
    luaL_openlibs(lua_);
    return true;
}

void ScriptHost::Shutdown() {
    if (lua_) {
        lua_close(lua_);
        lua_ = nullptr;
    }
}

std::int64_t ScriptHost::FileModTime(const std::string& path) {
    struct stat st {};
    if (stat(path.c_str(), &st) != 0)
        return 0;
    return static_cast<std::int64_t>(st.st_mtime);
}

bool ScriptHost::LoadConfigFile(GameConfig& outConfig) {
    if (!lua_)
        return false;

    lua_settop(lua_, 0);
    int result = luaL_loadfile(lua_, configPath_.c_str());
    if (result != LUA_OK) {
        status_ = std::string("Lua load error: ") + lua_tostring(lua_, -1);
        lua_pop(lua_, 1);
        return false;
    }

    result = lua_pcall(lua_, 0, 1, 0);
    if (result != LUA_OK) {
        status_ = std::string("Lua runtime error: ") + lua_tostring(lua_, -1);
        lua_pop(lua_, 1);
        return false;
    }

    if (!lua_istable(lua_, -1)) {
        status_ = "config.lua must return a table";
        lua_pop(lua_, 1);
        return false;
    }

    GameConfig parsed;
    if (!ParseConfigTable(lua_, -1, parsed)) {
        status_ = "config.lua missing weapons table";
        lua_pop(lua_, 1);
        return false;
    }

    outConfig = std::move(parsed);
    lua_pop(lua_, 1);
    lastModTime_ = FileModTime(configPath_);
    status_ = "Lua config loaded";
    return true;
}

bool ScriptHost::Reload(GameConfig& outConfig) {
    if (!LoadConfigFile(outConfig))
        return false;
    status_ = "Lua hot-reloaded";
    TraceLog(LOG_INFO, "SCRIPT: %s", status_.c_str());
    return true;
}

bool ScriptHost::PollHotReload(GameConfig& outConfig) {
    pollTimer_ += GetFrameTime();
    if (pollTimer_ < 0.35f)
        return false;
    pollTimer_ = 0.0f;

    std::int64_t mod = FileModTime(configPath_);
    if (mod > 0 && mod != lastModTime_)
        return Reload(outConfig);
    return false;
}
