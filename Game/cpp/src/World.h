#pragma once
#include "Types.h"
#include <vector>
#include <string>
#include <SDL2/SDL.h>

// ── Building ──────────────────────────────────────────────────────────────────
enum class BldType { INN, SHOP, BLACKSMITH, CHURCH, HOUSE };

inline const char* bldLabel(BldType t) {
    switch(t) {
        case BldType::INN:        return "The Sleeping Ox";
        case BldType::SHOP:       return "General Store";
        case BldType::BLACKSMITH: return "Blacksmith";
        case BldType::CHURCH:     return "Chapel";
        case BldType::HOUSE:      return "Cottage";
    }
    return "Building";
}

inline SDL_Color bldRoofColor(BldType t) {
    switch(t) {
        case BldType::INN:        return {160, 80, 32,255};
        case BldType::SHOP:       return { 32, 96,128,255};
        case BldType::BLACKSMITH: return { 64, 64, 64,255};
        case BldType::CHURCH:     return {208,208,232,255};
        case BldType::HOUSE:      return {128, 80, 48,255};
    }
    return {100,80,60,255};
}

struct Building {
    int x, y, w, h;
    BldType type;
    Tile interior[16][16]; // max 16x16 buildings

    Tile tileAt(int tx, int ty) const;
    bool contains(int tx, int ty) const {
        return tx>=x && tx<x+w && ty>=y && ty<y+h;
    }
};

// ── WorldGen ──────────────────────────────────────────────────────────────────
class World {
public:
    World();

    Tile get(int tx, int ty) const;
    Tile terrain(int tx, int ty) const;
    const Tile (&rawTiles() const)[WORLD_H][WORLD_W] { return tiles_; }
    const std::vector<Building>& buildings() const { return blds_; }

private:
    Tile tiles_[WORLD_H][WORLD_W]{};
    std::vector<Building> blds_;

    void generate();
    Tile classify(double h);
    void placeBuildings();
    bool canPlace(int bx,int by,int w,int h);
    void carveRoads();
    void carvePath(int x1,int y1,int x2,int y2);
};
