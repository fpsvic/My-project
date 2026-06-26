#pragma once
#include "Types.h"
#include "World.h"
#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <vector>
#include <string>
#include <array>
#include <cmath>

// ── Projectile ────────────────────────────────────────────────────────────────
struct Proj {
    double x,y,vx,vy;
    bool fromPlayer; int damage;
    double life; bool dead=false;
};

// ── Floating text ─────────────────────────────────────────────────────────────
struct FloatText {
    std::string text; double x,y; SDL_Color color; double life=1.2;
};

// ── Item ──────────────────────────────────────────────────────────────────────
struct Item {
    ItemKind kind; double x,y; bool collected=false; double bob=0;
};

// ── NPC ───────────────────────────────────────────────────────────────────────
struct NPC {
    double x,y,tx,ty;
    NpcJob job;
    std::string name;
    std::string speech;
    double speechTimer=0;
    double idleTimer=0;
    bool moving=false;
    int dir=0; // 0=down,1=up,2=left,3=right
    int frame=0; double frameT=0;
    double speed;
    unsigned int seed;
};

// ── Enemy ─────────────────────────────────────────────────────────────────────
struct Enemy {
    EnemyKind kind;
    double x,y;
    int hp; bool dead=false;
    int dir=0; int frame=0; double frameT=0; bool moving=false;
    double atkTimer=0;
    double hitFlash=0;
};

// ── Player ────────────────────────────────────────────────────────────────────
struct Player {
    double x=78*TILE+TILE/2.0, y=35*TILE+TILE/2.0;
    int hp=100, maxHp=100, attack=10, defence=0, xp=0, level=1;
    bool dead=false;
    int dir=0; int frame=0; double frameT=0; bool moving=false;
    double atkCd=0, iFrames=0, hitFlash=0;

    int  equippedSlot=-1;
    std::array<Item*,8> inv{};
    int invCount=0;
};

// ── Game ──────────────────────────────────────────────────────────────────────
class Game {
public:
    Game();
    ~Game();
    void run();

private:
    SDL_Window*   win_  =nullptr;
    SDL_Renderer* ren_  =nullptr;
    TTF_Font*     font_ =nullptr;
    TTF_Font*     fontSm_=nullptr;

    World world_;

    Player        player_;
    std::vector<Enemy>     enemies_;
    std::vector<NPC>       npcs_;
    std::vector<Item>      items_;
    std::vector<Proj>      projs_;
    std::vector<FloatText> floats_;

    SDL_Texture* minimapTex_=nullptr;

    double camX_=0, camY_=0;
    double waterTime_=0, spawnTimer_=5;
    bool   gameOver_=false;
    const Uint8* kb_=nullptr;

    // update
    void update(double dt);
    void handleInput();
    void playerAttack();
    void updateEnemies(double dt);
    void updateProjs(double dt);
    void updateItems(double dt);
    void updateNPCs(double dt);
    void checkPickups();
    void enemySpawner(double dt);
    void trySpawnEnemy();
    void spawnInitial();
    void talkNearby();
    std::string npcLine(NPC& npc);
    void updateCamera();

    // render
    void render();
    void drawWorld();
    void drawTile(int tx,int ty,int px,int py);
    void drawBuildings();
    void drawOneBuilding(const Building& b);
    void drawItems();
    void drawOneEnemy(Enemy& e);
    void drawOneNPC(NPC& n);
    void drawPlayer();
    void drawProjectiles();
    void drawFloats();
    void drawMinimap();
    void drawHUD();
    void drawInventoryBar();
    void drawGameOver();
    void drawVignette();

    // helpers
    void   text(const std::string& s, int x, int y, SDL_Color c, TTF_Font* f=nullptr);
    void   textCentered(const std::string& s, int cx, int y, SDL_Color c, TTF_Font* f=nullptr);
    bool   walkable(double px, double py) const;
    bool   onScreen(double wx, double wy) const;
    void   buildMinimap();
    EnemyKind randEnemy();
    Item*  equipped();

    // NPC name pool
    static const char* npcName(unsigned int seed);
};
