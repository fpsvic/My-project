#pragma once
#include <SDL2/SDL.h>
#include <string>

// ── Constants ─────────────────────────────────────────────────────────────────
constexpr int TILE     = 32;
constexpr int SCREEN_W = 800;
constexpr int SCREEN_H = 600;
constexpr int WORLD_W  = 160;
constexpr int WORLD_H  = 120;

// ── Tile ──────────────────────────────────────────────────────────────────────
enum class Tile {
    DEEP_WATER, SHALLOW_WATER, SAND, GRASS, DARK_GRASS,
    FOREST, MOUNTAIN, SNOW, PATH, WALL, FLOOR, DOOR
};

inline SDL_Color tileColor(Tile t) {
    switch (t) {
        case Tile::DEEP_WATER:    return {0x1a,0x4a,0x7a,255};
        case Tile::SHALLOW_WATER: return {0x2a,0x6f,0xba,255};
        case Tile::SAND:          return {0xd4,0xb4,0x83,255};
        case Tile::GRASS:         return {0x4a,0x8f,0x3f,255};
        case Tile::DARK_GRASS:    return {0x2d,0x6b,0x2a,255};
        case Tile::FOREST:        return {0x1a,0x4d,0x1a,255};
        case Tile::MOUNTAIN:      return {0x7a,0x6a,0x5a,255};
        case Tile::SNOW:          return {0xe8,0xe8,0xf0,255};
        case Tile::PATH:          return {0xb8,0xa8,0x78,255};
        case Tile::WALL:          return {0x8a,0x70,0x60,255};
        case Tile::FLOOR:         return {0xc8,0xb0,0x90,255};
        case Tile::DOOR:          return {0x7a,0x50,0x20,255};
    }
    return {0,0,0,255};
}

inline bool tileWalkable(Tile t) {
    return t != Tile::DEEP_WATER && t != Tile::SHALLOW_WATER
        && t != Tile::MOUNTAIN   && t != Tile::SNOW
        && t != Tile::WALL;
}

inline const char* tileZone(Tile t) {
    switch (t) {
        case Tile::DEEP_WATER:    return "Deep Ocean";
        case Tile::SHALLOW_WATER: return "Coastal Waters";
        case Tile::SAND:          return "Beach";
        case Tile::GRASS:         return "Grassland";
        case Tile::DARK_GRASS:    return "Plains";
        case Tile::FOREST:        return "Forest";
        case Tile::MOUNTAIN:      return "Mountains";
        case Tile::SNOW:          return "Snowy Peaks";
        case Tile::PATH:          return "Road";
        case Tile::WALL:          return "Building";
        case Tile::FLOOR:         return "Inside";
        case Tile::DOOR:          return "Doorway";
    }
    return "Unknown";
}

// ── Item ──────────────────────────────────────────────────────────────────────
enum class ItemKind {
    SWORD, AXE, DAGGER,
    BOW, PISTOL, RIFLE,
    APPLE, BREAD, POTION,
    SHIELD, HELMET
};
enum class ItemCat { MELEE, RANGED, FOOD, ARMOUR };

struct ItemDef {
    const char* label; ItemCat cat; int attack; int range; int heal;
    SDL_Color color;
};

inline ItemDef itemDef(ItemKind k) {
    switch (k) {
        case ItemKind::SWORD:  return {"Iron Sword",  ItemCat::MELEE,  20, 0,  0, {192,192,192,255}};
        case ItemKind::AXE:    return {"Battle Axe",  ItemCat::MELEE,  30, 0,  0, {128,128,128,255}};
        case ItemKind::DAGGER: return {"Dagger",      ItemCat::MELEE,  12, 0,  0, {180,180,255,255}};
        case ItemKind::BOW:    return {"Shortbow",    ItemCat::RANGED, 15, 6,  0, {139,105, 20,255}};
        case ItemKind::PISTOL: return {"Pistol",      ItemCat::RANGED, 25, 8,  0, { 80, 80, 80,255}};
        case ItemKind::RIFLE:  return {"Rifle",       ItemCat::RANGED, 40,12,  0, { 48, 48, 48,255}};
        case ItemKind::APPLE:  return {"Apple",       ItemCat::FOOD,    0, 0, 15, {220, 34, 34,255}};
        case ItemKind::BREAD:  return {"Bread",       ItemCat::FOOD,    0, 0, 25, {212,160, 96,255}};
        case ItemKind::POTION: return {"Potion",      ItemCat::FOOD,    0, 0, 50, {255, 68,170,255}};
        case ItemKind::SHIELD: return {"Wood Shield", ItemCat::ARMOUR,  0, 0,  0, {139, 94, 60,255}};
        case ItemKind::HELMET: return {"Iron Helmet", ItemCat::ARMOUR,  0, 0,  0, {160,160,176,255}};
    }
    return {"?", ItemCat::FOOD, 0, 0, 0, {255,255,255,255}};
}

// ── Enemy ─────────────────────────────────────────────────────────────────────
enum class EnemyKind { SLIME, ORC, SKELETON, ARCHER, MAGE, TROLL };

struct EnemyDef {
    const char* name; int maxHp; int damage; int xp; float speed;
    bool ranged; int rangeT; double projSpeed;
    SDL_Color color;
};

inline EnemyDef enemyDef(EnemyKind k) {
    switch (k) {
        case EnemyKind::SLIME:    return {"Slime",   30, 8, 40,1.5f,false,0,  0,  { 68,187, 68,255}};
        case EnemyKind::ORC:      return {"Orc",     60,14, 55,2.0f,false,0,  0,  { 34,136, 34,255}};
        case EnemyKind::SKELETON: return {"Skel",    40,10, 50,1.8f,false,0,  0,  {208,208,184,255}};
        case EnemyKind::ARCHER:   return {"Archer",  45,12, 60,1.6f,true, 5,220,  {136, 85, 34,255}};
        case EnemyKind::MAGE:     return {"Mage",    35,18, 70,1.4f,true, 7,300,  {136, 68,136,255}};
        case EnemyKind::TROLL:    return {"Troll",  120,22, 80,1.2f,false,0,  0,  { 68,102, 34,255}};
    }
    return {"?", 10, 5, 10, 1.0f, false, 0, 0, {255,0,0,255}};
}

// ── NPC ───────────────────────────────────────────────────────────────────────
enum class NpcJob { VILLAGER, MERCHANT, GUARD, ELDER, WANDERER };

// ── SDL helpers ───────────────────────────────────────────────────────────────
inline void setColor(SDL_Renderer* r, SDL_Color c) {
    SDL_SetRenderDrawColor(r, c.r, c.g, c.b, c.a);
}
inline void fillRect(SDL_Renderer* r, int x, int y, int w, int h) {
    SDL_Rect rc{x,y,w,h}; SDL_RenderFillRect(r, &rc);
}
inline void drawRect(SDL_Renderer* r, int x, int y, int w, int h) {
    SDL_Rect rc{x,y,w,h}; SDL_RenderDrawRect(r, &rc);
}
inline void fillCircle(SDL_Renderer* r, int cx, int cy, int rad) {
    for (int dy = -rad; dy <= rad; dy++) {
        int dxw = (int)sqrt((double)(rad*rad - dy*dy));
        SDL_RenderDrawLine(r, cx-dxw, cy+dy, cx+dxw, cy+dy);
    }
}
inline void drawLine(SDL_Renderer* r, int x1,int y1,int x2,int y2) {
    SDL_RenderDrawLine(r, x1,y1,x2,y2);
}
