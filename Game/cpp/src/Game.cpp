#include "Game.h"
#include "Noise.h"
#include <algorithm>
#include <cstdio>
#include <cmath>
#include <cstring>
#include <sstream>
#include <stdexcept>

static const char* NAMES[]={"Aldric","Benna","Cort","Dwyn","Elara","Fenn",
    "Gara","Holt","Iria","Joren","Kael","Lira","Mord","Nyla","Orin","Pyra"};

static unsigned int rngState = 12345;
static unsigned int rng() { rngState=rngState*1664525+1013904223; return rngState; }
static double rngd() { return (rng()&0xFFFF)/65535.0; }

// ── Init / Deinit ─────────────────────────────────────────────────────────────
Game::Game() {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) throw std::runtime_error(SDL_GetError());
    if (TTF_Init() < 0)              throw std::runtime_error(TTF_GetError());

    win_ = SDL_CreateWindow("Top-Down World", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                             SCREEN_W, SCREEN_H, SDL_WINDOW_SHOWN);
    ren_ = SDL_CreateRenderer(win_, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    SDL_SetRenderDrawBlendMode(ren_, SDL_BLENDMODE_BLEND);

    const char* fontPaths[]={
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
        "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf",
        nullptr
    };
    for (int i=0; fontPaths[i]; i++) {
        font_   = TTF_OpenFont(fontPaths[i], 12);
        fontSm_ = TTF_OpenFont(fontPaths[i],  9);
        if (font_ && fontSm_) break;
    }

    kb_ = SDL_GetKeyboardState(nullptr);

    buildMinimap();
    spawnInitial();
}

Game::~Game() {
    if (minimapTex_) SDL_DestroyTexture(minimapTex_);
    if (font_)   TTF_CloseFont(font_);
    if (fontSm_) TTF_CloseFont(fontSm_);
    SDL_DestroyRenderer(ren_);
    SDL_DestroyWindow(win_);
    TTF_Quit();
    SDL_Quit();
}

// ── Run ───────────────────────────────────────────────────────────────────────
void Game::run() {
    Uint64 prev = SDL_GetTicks64();
    SDL_Event ev;
    while (true) {
        while (SDL_PollEvent(&ev)) {
            if (ev.type == SDL_QUIT) return;
            if (ev.type == SDL_KEYDOWN) {
                auto sc = ev.key.keysym.scancode;
                if (sc==SDL_SCANCODE_F) playerAttack();
                if (sc==SDL_SCANCODE_E) talkNearby();
                if (sc>=SDL_SCANCODE_1&&sc<=SDL_SCANCODE_8) {
                    int slot=sc-SDL_SCANCODE_1;
                    if (slot<player_.invCount) {
                        auto& it=*player_.inv[slot];
                        auto  def=itemDef(it.kind);
                        if (def.cat==ItemCat::MELEE||def.cat==ItemCat::RANGED)
                            player_.equippedSlot=slot;
                        else if (def.cat==ItemCat::ARMOUR) { player_.defence+=8; it.collected=true; }
                    }
                }
                if (sc==SDL_SCANCODE_R && gameOver_) { gameOver_=false; player_={};  }
            }
        }
        Uint64 now=SDL_GetTicks64();
        double dt=std::min((now-prev)/1000.0,0.05); prev=now;
        if (!gameOver_) update(dt);
        render();
    }
}

// ── Update ────────────────────────────────────────────────────────────────────
void Game::update(double dt) {
    waterTime_+=dt;

    // Player movement
    double dx=0,dy=0;
    if (kb_[SDL_SCANCODE_W]||kb_[SDL_SCANCODE_UP])    dy-=1;
    if (kb_[SDL_SCANCODE_S]||kb_[SDL_SCANCODE_DOWN])   dy+=1;
    if (kb_[SDL_SCANCODE_A]||kb_[SDL_SCANCODE_LEFT])   dx-=1;
    if (kb_[SDL_SCANCODE_D]||kb_[SDL_SCANCODE_RIGHT])  dx+=1;
    if (dx&&dy){dx*=0.707;dy*=0.707;}

    player_.moving=(dx||dy);
    if      (dx>0) player_.dir=3;
    else if (dx<0) player_.dir=2;
    else if (dy<0) player_.dir=1;
    else if (dy>0) player_.dir=0;

    if (player_.moving){ player_.frameT+=dt; if(player_.frameT>0.12){player_.frameT=0;player_.frame^=1;}}
    else { player_.frame=0; player_.frameT=0; }

    if (player_.iFrames>0) player_.iFrames-=dt;
    if (player_.hitFlash>0) player_.hitFlash-=dt;
    if (player_.atkCd>0) player_.atkCd-=dt;

    const int R=10;
    auto& p=player_;
    double nx=p.x+dx*130.0*dt, ny=p.y+dy*130.0*dt;
    if (walkable(nx-R,p.y)&&walkable(nx+R,p.y)&&walkable(nx,p.y-R)&&walkable(nx,p.y+R)) p.x=nx;
    if (walkable(p.x-R,ny)&&walkable(p.x+R,ny)&&walkable(p.x,ny-R)&&walkable(p.x,ny+R)) p.y=ny;

    updateEnemies(dt);
    updateProjs(dt);
    updateItems(dt);
    updateNPCs(dt);
    checkPickups();
    enemySpawner(dt);

    // Remove dead floats
    floats_.erase(std::remove_if(floats_.begin(),floats_.end(),[](auto&f){return f.life<=0;}),floats_.end());
    for (auto&f:floats_){ f.y-=25*dt; f.life-=dt; }

    updateCamera();
}

void Game::updateCamera() {
    camX_=player_.x-SCREEN_W/2.0;
    camY_=player_.y-SCREEN_H/2.0;
    camX_=std::max(0.0,std::min(camX_,(double)(WORLD_W*TILE-SCREEN_W)));
    camY_=std::max(0.0,std::min(camY_,(double)(WORLD_H*TILE-SCREEN_H)));
}

void Game::playerAttack() {
    if (player_.atkCd>0||player_.dead) return;
    player_.atkCd=0.45;
    Item* w=equipped();
    int dmg=player_.attack+(w?itemDef(w->kind).attack:0);

    if (w && itemDef(w->kind).cat==ItemCat::RANGED) {
        static const double dirs[4][2]={{0,1},{0,-1},{-1,0},{1,0}};
        int d=player_.dir;
        double spd=itemDef(w->kind).range*40+200;
        Proj pr; pr.x=player_.x; pr.y=player_.y;
        pr.vx=dirs[d][0]*spd; pr.vy=dirs[d][1]*spd;
        pr.fromPlayer=true; pr.damage=dmg; pr.life=2.0;
        projs_.push_back(pr);
    } else {
        static const double dirs[4][2]={{0,1},{0,-1},{-1,0},{1,0}};
        double fx=dirs[player_.dir][0], fy=dirs[player_.dir][1];
        for (auto& e:enemies_) {
            if (e.dead) continue;
            double ex=e.x-player_.x, ey=e.y-player_.y;
            double dist=std::sqrt(ex*ex+ey*ey);
            double dot=ex*fx+ey*fy;
            if (dist<44&&dot>0) { e.hp-=dmg; e.hitFlash=0.15; floats_.push_back({"-"+std::to_string(dmg),e.x,e.y-10,{255,100,68,255}}); if(e.hp<=0)e.dead=true; }
        }
    }
    // collect XP from newly killed enemies
    for (auto& e:enemies_) {
        if (e.dead) {
            auto def=enemyDef(e.kind);
            player_.xp+=def.xp;
            floats_.push_back({"+"+std::to_string(def.xp)+" XP",e.x,e.y,{255,238,68,255}});
            if (rngd()<0.4) {
                ItemKind iks[]={ItemKind::SWORD,ItemKind::AXE,ItemKind::DAGGER,ItemKind::BOW,
                    ItemKind::PISTOL,ItemKind::RIFLE,ItemKind::APPLE,ItemKind::BREAD,
                    ItemKind::POTION,ItemKind::SHIELD,ItemKind::HELMET};
                items_.push_back({iks[rng()%11],e.x,e.y});
            }
            // level up?
            while (player_.xp>=player_.level*100) {
                player_.xp-=player_.level*100; player_.level++;
                player_.attack+=4; player_.defence+=2;
                player_.maxHp+=10; player_.hp=std::min(player_.maxHp,player_.hp+20);
                floats_.push_back({"LEVEL UP!",player_.x,player_.y-30,{68,238,255,255}});
            }
        }
    }
    enemies_.erase(std::remove_if(enemies_.begin(),enemies_.end(),[](auto&e){return e.dead;}),enemies_.end());
}

void Game::updateEnemies(double dt) {
    for (auto& e:enemies_) {
        if (e.dead) continue;
        if (e.hitFlash>0) e.hitFlash-=dt;
        e.atkTimer-=dt;

        double dx=player_.x-e.x, dy=player_.y-e.y;
        double dist=std::sqrt(dx*dx+dy*dy);
        const double AGGRO=220;

        if (dist<AGGRO) {
            auto def=enemyDef(e.kind);
            double meleeR=(def.ranged?0:32.0);
            double targetR=def.ranged?def.rangeT*TILE*0.7:meleeR;
            bool shouldMove=dist>targetR;

            if (shouldMove) {
                double spd=def.speed*TILE*dt;
                double nx=e.x+(dx/dist)*spd, ny=e.y+(dy/dist)*spd;
                if (walkable(nx,e.y)) e.x=nx;
                if (walkable(e.x,ny)) e.y=ny;
                if (std::abs(dx)>std::abs(dy)) e.dir=(dx>0?3:2); else e.dir=(dy>0?0:1);
                e.moving=true;
            } else { e.moving=false; }

            if (e.moving) { e.frameT+=dt; if(e.frameT>0.18){e.frameT=0;e.frame^=1;}} else e.frame=0;

            if (e.atkTimer<=0) {
                if (def.ranged && dist<def.rangeT*TILE) {
                    double len=std::sqrt(dx*dx+dy*dy);
                    Proj pr; pr.x=e.x; pr.y=e.y; pr.vx=dx/len*def.projSpeed; pr.vy=dy/len*def.projSpeed;
                    pr.fromPlayer=false; pr.damage=def.damage; pr.life=2.5;
                    projs_.push_back(pr);
                    e.atkTimer=1.8;
                } else if (!def.ranged && dist<34) {
                    if (player_.iFrames<=0) {
                        int dmg=std::max(1,def.damage-player_.defence);
                        player_.hp-=dmg; player_.hitFlash=0.12; player_.iFrames=0.5;
                        floats_.push_back({"-"+std::to_string(dmg),player_.x,player_.y-20,{255,68,68,255}});
                        if (player_.hp<=0){player_.hp=0;player_.dead=true;gameOver_=true;}
                    }
                    e.atkTimer=1.2;
                }
            }
        } else { e.moving=false; }
    }
}

void Game::updateProjs(double dt) {
    for (auto& p:projs_) {
        p.x+=p.vx*dt; p.y+=p.vy*dt; p.life-=dt;
        int tx=(int)(p.x/TILE), ty=(int)(p.y/TILE);
        if (!tileWalkable(world_.get(tx,ty))||p.life<=0) { p.dead=true; continue; }
        if (p.fromPlayer) {
            for (auto& e:enemies_) {
                if (e.dead||p.dead) continue;
                double dx2=p.x-e.x,dy2=p.y-e.y;
                if (dx2*dx2+dy2*dy2<22*22) {
                    int dmg=p.damage; e.hp-=dmg; e.hitFlash=0.15; p.dead=true;
                    floats_.push_back({"-"+std::to_string(dmg),e.x,e.y-10,{255,100,68,255}});
                    if (e.hp<=0){ e.dead=true; auto def=enemyDef(e.kind);
                        player_.xp+=def.xp; floats_.push_back({"+"+std::to_string(def.xp)+" XP",e.x,e.y,{255,238,68,255}});
                        if(rngd()<0.4){ItemKind iks[]={ItemKind::SWORD,ItemKind::AXE,ItemKind::DAGGER,ItemKind::BOW,ItemKind::PISTOL,ItemKind::RIFLE,ItemKind::APPLE,ItemKind::BREAD,ItemKind::POTION,ItemKind::SHIELD,ItemKind::HELMET}; items_.push_back({iks[rng()%11],e.x,e.y});}
                    }
                }
            }
        } else {
            if (player_.iFrames<=0) {
                double dx2=p.x-player_.x,dy2=p.y-player_.y;
                if (dx2*dx2+dy2*dy2<20*20) {
                    int dmg=std::max(1,p.damage-player_.defence);
                    player_.hp-=dmg; player_.hitFlash=0.12; player_.iFrames=0.5; p.dead=true;
                    floats_.push_back({"-"+std::to_string(dmg),player_.x,player_.y-20,{255,68,68,255}});
                    if (player_.hp<=0){player_.hp=0;player_.dead=true;gameOver_=true;}
                }
            }
        }
    }
    enemies_.erase(std::remove_if(enemies_.begin(),enemies_.end(),[](auto&e){return e.dead;}),enemies_.end());
    projs_.erase(std::remove_if(projs_.begin(),projs_.end(),[](auto&p){return p.dead;}),projs_.end());
}

void Game::updateItems(double dt) {
    for (auto& it:items_) if (!it.collected) it.bob+=dt*2.5;
}

void Game::updateNPCs(double dt) {
    for (auto& n:npcs_) {
        if (n.speechTimer>0) { n.speechTimer-=dt; if(n.speechTimer<=0) n.speech=""; }
        if (!n.moving) {
            n.idleTimer-=dt;
            if (n.idleTimer<=0) {
                double angle=(hashN(n.x,n.y,n.idleTimer)*2-1)*M_PI;
                double dist=1+hashN(n.y,n.x,3)*3;
                int tx2=(int)((n.x+std::cos(angle)*dist*TILE)/TILE);
                int ty2=(int)((n.y+std::sin(angle)*dist*TILE)/TILE);
                if (tileWalkable(world_.get(tx2,ty2))) { n.tx=tx2*TILE+TILE/2.0; n.ty=ty2*TILE+TILE/2.0; n.moving=true; }
                n.idleTimer=1.5+hashN(n.x+n.idleTimer,n.y,5)*3;
            }
        }
        if (n.moving) {
            double dx=n.tx-n.x, dy=n.ty-n.y;
            double dist=std::sqrt(dx*dx+dy*dy);
            if (dist<2) { n.moving=false; }
            else {
                double nx=n.x+(dx/dist)*n.speed*dt, ny=n.y+(dy/dist)*n.speed*dt;
                if (walkable(nx,n.y)) n.x=nx;
                if (walkable(n.x,ny)) n.y=ny;
                if (std::abs(dx)>std::abs(dy)) n.dir=(dx>0?3:2); else n.dir=(dy>0?0:1);
            }
            n.frameT+=dt; if(n.frameT>0.2){n.frameT=0;n.frame^=1;}
        } else n.frame=0;
    }
}

void Game::checkPickups() {
    for (auto& it:items_) {
        if (it.collected) continue;
        double dx=player_.x-it.x, dy=player_.y-it.y;
        if (dx*dx+dy*dy>22*22) continue;
        auto def=itemDef(it.kind);
        if (def.cat==ItemCat::FOOD) {
            int healed=std::min(def.heal, player_.maxHp-player_.hp);
            player_.hp+=healed; it.collected=true;
            floats_.push_back({"+"+std::to_string(healed)+" HP",player_.x,player_.y-20,{68,255,136,255}});
        } else if (player_.invCount<8) {
            it.collected=false; // keep in world but flag as in inv
            // Copy into a stable slot
            items_[&it-items_.data()].collected=true;
            player_.inv[player_.invCount++]=&it;
            floats_.push_back({"Got "+std::string(def.label),player_.x,player_.y-20,{255,255,255,255}});
        }
    }
}

void Game::enemySpawner(double dt) {
    spawnTimer_-=dt;
    if (spawnTimer_>0) return;
    spawnTimer_=4+rngd()*6;
    int count=1+(int)(rngd()*2);
    for (int i=0;i<count;i++) trySpawnEnemy();
}

void Game::trySpawnEnemy() {
    for (int a=0;a<20;a++) {
        int tx=1+(int)(rngd()*(WORLD_W-2));
        int ty=1+(int)(rngd()*(WORLD_H-2));
        if (!tileWalkable(world_.get(tx,ty))) continue;
        double wx=tx*TILE+TILE/2.0, wy=ty*TILE+TILE/2.0;
        if (wx>camX_-20&&wx<camX_+SCREEN_W+20&&wy>camY_-20&&wy<camY_+SCREEN_H+20) continue;
        Enemy e; e.kind=randEnemy(); e.x=wx; e.y=wy; e.hp=enemyDef(e.kind).maxHp;
        enemies_.push_back(e); return;
    }
}

void Game::spawnInitial() {
    // NPCs
    static const int CENTRES[][2]={{30,25},{120,25},{55,55},{100,55},{78,35},{40,90},{125,85},{78,95}};
    NpcJob jobs[]={NpcJob::VILLAGER,NpcJob::MERCHANT,NpcJob::GUARD,NpcJob::ELDER,NpcJob::WANDERER};
    unsigned int s=9999;
    auto r=[&](int n){ s=s*1664525+1013904223; return (int)((s>>16)%n); };
    for (auto& vc:CENTRES) {
        int cnt=2+r(4);
        for (int k=0;k<cnt;k++) {
            int tx=vc[0]+r(10)-5, ty=vc[1]+r(10)-5;
            if (!tileWalkable(world_.get(tx,ty))) continue;
            NPC n2; n2.x=tx*TILE+TILE/2.0; n2.y=ty*TILE+TILE/2.0;
            n2.tx=n2.x; n2.ty=n2.y;
            n2.job=jobs[r(5)]; n2.seed=r(0x7FFF);
            n2.name=NAMES[r(16)]; n2.speed=28+rngd()*18;
            n2.idleTimer=rngd()*3;
            npcs_.push_back(n2);
        }
    }
    // Initial enemies
    for (int i=0;i<30;i++) trySpawnEnemy();
    // Initial items
    ItemKind iks[]={ItemKind::SWORD,ItemKind::AXE,ItemKind::DAGGER,ItemKind::BOW,
        ItemKind::PISTOL,ItemKind::RIFLE,ItemKind::APPLE,ItemKind::BREAD,
        ItemKind::POTION,ItemKind::SHIELD,ItemKind::HELMET};
    for (int i=0;i<40;i++) {
        int tx=2+(int)(rngd()*(WORLD_W-4));
        int ty=2+(int)(rngd()*(WORLD_H-4));
        if (!tileWalkable(world_.get(tx,ty))) continue;
        items_.push_back({iks[rng()%11],(double)tx*TILE+TILE/2.0,(double)ty*TILE+TILE/2.0});
    }
}

void Game::talkNearby() {
    for (auto& n:npcs_) {
        double dx=player_.x-n.x,dy=player_.y-n.y;
        if (dx*dx+dy*dy<44*44) {
            n.speech=npcLine(n); n.speechTimer=4.0;
        }
    }
}

std::string Game::npcLine(NPC& n) {
    bool hurt=(player_.hp<player_.maxHp/2);
    bool highLvl=(player_.level>=5);
    int ptx=(int)(player_.x/TILE),pty=(int)(player_.y/TILE);
    Tile t=world_.get(ptx,pty);
    bool nearWater=(t==Tile::SAND||t==Tile::SHALLOW_WATER);
    bool nearMtn=(t==Tile::MOUNTAIN||t==Tile::SNOW);
    bool enemiesNear=false;
    for (auto& e:enemies_) { double dx=e.x-player_.x,dy=e.y-player_.y; if(dx*dx+dy*dy<150*150){enemiesNear=true;break;} }

    static const char* villHurt[]={"You look wounded - rest up!","Careful, traveler.","There's a healer nearby."};
    static const char* villDanger[]={"Watch out! Monsters are close!","Get to safety!","Run!"};
    static const char* villNorm[]={"Lovely weather today!","Have you heard the news?","A strange fog last night.","My crops are growing well.","Stay safe out there."};
    static const char* mercHurt[]={"Buy a potion, friend!","I sell remedies - best around!","That wound needs attention."};
    static const char* mercNorm[]={"Buy somethin', will ya?","Best prices in the realm!","Swords, potions, shields!","Good gear saves lives.","Trade routes are rough lately."};
    static const char* guardDanger[]={"Enemies incoming! Stand firm!","Defend the village!","Stay back, I'll handle this."};
    static const char* guardNorm[]={"Move along, citizen.","All quiet on my watch.","Keep your weapons sheathed in town.","I've been posted here three years.","Report anything suspicious."};
    static const char* elderHigh[]={"Your power grows, hero.","The land needs you.","I sense great destiny in you."};
    static const char* elderNorm[]={"The old ways must not be forgotten.","Wisdom takes patience.","The stars speak of change.","Every step is a lesson.","I remember when this was farmland."};
    static const char* wandWater[]={"The sea calls to me...","Strange lights over water at night.","I once sailed beyond the horizon."};
    static const char* wandMtn[]={"Those peaks are treacherous.","I found ruins high up there once.","The wind speaks in the mountains."};
    static const char* wandNorm[]={"The horizon always calls.","I come from lands far east.","Every road leads somewhere new.","I've walked this world 30 years.","Rest when you can, traveler."};

    auto pickL=[&](const char** arr, int sz) -> std::string {
        return arr[((unsigned)n.seed*3+(unsigned)(n.speechTimer*100))%(unsigned)sz];
    };

    switch(n.job) {
        case NpcJob::VILLAGER:  return hurt?pickL(villHurt,3):(enemiesNear?pickL(villDanger,3):pickL(villNorm,5));
        case NpcJob::MERCHANT:  return hurt?pickL(mercHurt,3):pickL(mercNorm,5);
        case NpcJob::GUARD:     return enemiesNear?pickL(guardDanger,3):pickL(guardNorm,5);
        case NpcJob::ELDER:     return highLvl?pickL(elderHigh,3):pickL(elderNorm,5);
        case NpcJob::WANDERER:  return nearWater?pickL(wandWater,3):(nearMtn?pickL(wandMtn,3):pickL(wandNorm,5));
    }
    return "...";
}

EnemyKind Game::randEnemy() {
    double r=rngd();
    if (r<0.30) return EnemyKind::SLIME;
    if (r<0.50) return EnemyKind::ORC;
    if (r<0.65) return EnemyKind::SKELETON;
    if (r<0.78) return EnemyKind::ARCHER;
    if (r<0.88) return EnemyKind::MAGE;
    return EnemyKind::TROLL;
}

Item* Game::equipped() {
    if (player_.equippedSlot<0||player_.equippedSlot>=player_.invCount) return nullptr;
    return player_.inv[player_.equippedSlot];
}

bool Game::walkable(double px,double py) const {
    return tileWalkable(world_.get((int)(px/TILE),(int)(py/TILE)));
}
bool Game::onScreen(double wx,double wy) const {
    return wx>camX_-50&&wx<camX_+SCREEN_W+50&&wy>camY_-50&&wy<camY_+SCREEN_H+50;
}

// ── Minimap pre-render ────────────────────────────────────────────────────────
void Game::buildMinimap() {
    minimapTex_=SDL_CreateTexture(ren_,SDL_PIXELFORMAT_RGB24,SDL_TEXTUREACCESS_STATIC,WORLD_W,WORLD_H);
    std::vector<Uint8> px(WORLD_W*WORLD_H*3);
    auto& raw=world_.rawTiles();
    for (int y=0;y<WORLD_H;y++) for (int x=0;x<WORLD_W;x++) {
        auto c=tileColor(raw[y][x]);
        int i=(y*WORLD_W+x)*3;
        px[i]=c.r; px[i+1]=c.g; px[i+2]=c.b;
    }
    for (auto& b:world_.buildings()) {
        for (int dy=0;dy<b.h;dy++) for (int dx=0;dx<b.w;dx++) {
            int bx=b.x+dx, by2=b.y+dy;
            if (bx>=0&&bx<WORLD_W&&by2>=0&&by2<WORLD_H) {
                int i=(by2*WORLD_W+bx)*3; px[i]=0x8a;px[i+1]=0x70;px[i+2]=0x60;
            }
        }
    }
    SDL_UpdateTexture(minimapTex_,nullptr,px.data(),WORLD_W*3);
}

// ── Text ─────────────────────────────────────────────────────────────────────
void Game::text(const std::string& s,int x,int y,SDL_Color c,TTF_Font* f) {
    if (!f) f=font_;
    if (!f) return;
    SDL_Surface* sf=TTF_RenderText_Blended(f,s.c_str(),c);
    if (!sf) return;
    SDL_Texture* tx=SDL_CreateTextureFromSurface(ren_,sf);
    SDL_Rect dst{x,y,sf->w,sf->h};
    SDL_RenderCopy(ren_,tx,nullptr,&dst);
    SDL_DestroyTexture(tx); SDL_FreeSurface(sf);
}
void Game::textCentered(const std::string& s,int cx,int y,SDL_Color c,TTF_Font* f) {
    if (!f) f=font_;
    if (!f) return;
    int w=0,h=0; TTF_SizeText(f,s.c_str(),&w,&h);
    text(s,cx-w/2,y,c,f);
}

// ── Render ────────────────────────────────────────────────────────────────────
void Game::render() {
    SDL_SetRenderDrawColor(ren_,0x1a,0x3a,0x5a,255);
    SDL_RenderClear(ren_);

    drawWorld();
    drawBuildings();
    drawItems();

    // Y-sort entities
    struct Drawable { double y; int type; int idx; };
    std::vector<Drawable> dl;
    for (int i=0;i<(int)npcs_.size();i++)    if(onScreen(npcs_[i].x,npcs_[i].y))    dl.push_back({npcs_[i].y,   0,i});
    for (int i=0;i<(int)enemies_.size();i++) if(onScreen(enemies_[i].x,enemies_[i].y)) dl.push_back({enemies_[i].y, 1,i});
    dl.push_back({player_.y,2,0});
    std::sort(dl.begin(),dl.end(),[](auto&a,auto&b){return a.y<b.y;});
    for (auto& d:dl) {
        if (d.type==0) drawOneNPC(npcs_[d.idx]);
        else if (d.type==1) drawOneEnemy(enemies_[d.idx]);
        else drawPlayer();
    }

    drawProjectiles();
    drawFloats();
    drawMinimap();
    drawHUD();
    drawInventoryBar();
    drawVignette();
    if (gameOver_) drawGameOver();

    SDL_RenderPresent(ren_);
}

void Game::drawWorld() {
    int sx0=(int)(camX_/TILE)-1, sy0=(int)(camY_/TILE)-1;
    int sx1=sx0+SCREEN_W/TILE+3, sy1=sy0+SCREEN_H/TILE+3;
    for (int ty=sy0;ty<=sy1;ty++)
        for (int tx=sx0;tx<=sx1;tx++)
            drawTile(tx,ty,(int)(tx*TILE-camX_),(int)(ty*TILE-camY_));
}

void Game::drawTile(int tx,int ty,int px,int py) {
    Tile t=world_.get(tx,ty);
    auto c=tileColor(t);
    SDL_SetRenderDrawColor(ren_,c.r,c.g,c.b,255);
    SDL_Rect r{px,py,TILE,TILE}; SDL_RenderFillRect(ren_,&r);

    double v=hashN(tx,ty,99);

    switch(t) {
    case Tile::GRASS: case Tile::DARK_GRASS: {
        SDL_Color gc = t==Tile::GRASS ? SDL_Color{61,122,53,255} : SDL_Color{37,96,34,255};
        SDL_SetRenderDrawColor(ren_,gc.r,gc.g,gc.b,255);
        if (v>0.72){fillRect(ren_,px+4,py+6,3,5);fillRect(ren_,px+12,py+14,3,5);fillRect(ren_,px+21,py+5,3,5);}
        break;
    }
    case Tile::FOREST: {
        int trees=(int)(v*3)+1;
        for (int i=0;i<trees;i++) {
            int fx=(int)(hashN(tx+i,ty,1)*(TILE-12))+6;
            int fy=(int)(hashN(tx+i,ty,2)*(TILE-12))+6;
            int rad=(int)(5+hashN(tx,ty+i,3)*3);
            SDL_SetRenderDrawColor(ren_,15,61,15,255); fillCircle(ren_,px+fx,py+fy,rad);
            SDL_SetRenderDrawColor(ren_,26,92,26,255); fillCircle(ren_,px+fx-1,py+fy-1,rad-1);
        }
        break;
    }
    case Tile::MOUNTAIN: {
        SDL_SetRenderDrawColor(ren_,106,90,74,255);
        SDL_Point pts[]={{px+TILE/2,py+4},{px+TILE-3,py+TILE-3},{px+3,py+TILE-3}};
        for(int i=0;i<3;i++) SDL_RenderDrawLine(ren_,pts[i].x,pts[i].y,pts[(i+1)%3].x,pts[(i+1)%3].y);
        // Fill using scan lines
        for(int dy=4;dy<TILE-3;dy++){
            double t2=(double)(dy-4)/(TILE-7);
            int lx=(int)(px+TILE/2-(TILE/2-3)*t2), rx=(int)(px+TILE/2+(TILE/2-3)*t2);
            SDL_RenderDrawLine(ren_,lx,py+dy,rx,py+dy);
        }
        SDL_SetRenderDrawColor(ren_,154,138,122,255);
        for(int dy=4;dy<TILE/2;dy++){
            double t2=(double)(dy-4)/(TILE/2-4);
            int lx=(int)(px+TILE/2-(8)*t2), rx=(int)(px+TILE/2+(8)*t2);
            SDL_RenderDrawLine(ren_,lx,py+dy,rx,py+dy);
        }
        break;
    }
    case Tile::SNOW: {
        SDL_SetRenderDrawColor(ren_,200,200,216,255);
        for(int dy=2;dy<TILE-2;dy++){
            double t2=(double)(dy-2)/(TILE-4);
            int lx=(int)(px+TILE/2-(TILE/2-2)*t2), rx=(int)(px+TILE/2+(TILE/2-2)*t2);
            SDL_RenderDrawLine(ren_,lx,py+dy,rx,py+dy);
        }
        SDL_SetRenderDrawColor(ren_,240,240,255,255);
        for(int dy=2;dy<TILE/2-2;dy++){
            double t2=(double)(dy-2)/(TILE/2-4);
            int lx=(int)(px+TILE/2-(6)*t2), rx=(int)(px+TILE/2+(6)*t2);
            SDL_RenderDrawLine(ren_,lx,py+dy,rx,py+dy);
        }
        break;
    }
    case Tile::PATH:
        SDL_SetRenderDrawColor(ren_,168,152,88,255); fillRect(ren_,px+12,py,8,TILE);
        SDL_SetRenderDrawColor(ren_,152,136,72,255); fillRect(ren_,px+14,py,4,TILE);
        break;
    case Tile::WALL: {
        SDL_SetRenderDrawColor(ren_,106,88,72,255); fillRect(ren_,px+1,py+1,TILE-2,TILE-2);
        SDL_SetRenderDrawColor(ren_,80,64,56,255);
        for (int by=0;by<TILE;by+=6)
            for (int bx=((by/6)%2==0?0:5);bx<TILE;bx+=10)
                drawRect(ren_,px+bx+1,py+by+1,9,5);
        break;
    }
    case Tile::FLOOR:
        SDL_SetRenderDrawColor(ren_,176,160,112,255);
        for(int fi=0;fi<TILE;fi+=8){SDL_RenderDrawLine(ren_,px+fi,py,px+fi,py+TILE);SDL_RenderDrawLine(ren_,px,py+fi,px+TILE,py+fi);}
        break;
    case Tile::DOOR:
        SDL_SetRenderDrawColor(ren_,90,48,16,255); fillRect(ren_,px+8,py+4,TILE-16,TILE-4);
        SDL_SetRenderDrawColor(ren_,200,144,64,255); fillCircle(ren_,px+TILE-14,py+TILE/2,2);
        break;
    case Tile::SHALLOW_WATER: case Tile::DEEP_WATER: {
        SDL_Color rip=t==Tile::DEEP_WATER?SDL_Color{30,90,154,255}:SDL_Color{58,127,208,255};
        SDL_SetRenderDrawColor(ren_,rip.r,rip.g,rip.b,200);
        int oy=(int)(std::fmod(waterTime_*18+tx*7+ty*13,TILE));
        // Simple wave line
        for (int wx=2;wx<TILE-4;wx++)
            SDL_RenderDrawPoint(ren_,px+wx,py+oy+(int)(std::sin(wx*0.4)*3));
        break;
    }
    default: break;
    }
    SDL_SetRenderDrawColor(ren_,0,0,0,18);
    SDL_Rect gr{px,py,TILE,TILE}; SDL_RenderDrawRect(ren_,&gr);
}

void Game::drawBuildings() {
    for (auto& b:world_.buildings()) {
        int sx=(int)(b.x*TILE-camX_), sy=(int)(b.y*TILE-camY_);
        if (sx+b.w*TILE<0||sx>SCREEN_W||sy+b.h*TILE<0||sy>SCREEN_H) continue;
        drawOneBuilding(b);
    }
}

void Game::drawOneBuilding(const Building& b) {
    int sx=(int)(b.x*TILE-camX_), sy=(int)(b.y*TILE-camY_);
    int pw=b.w*TILE;
    auto rc=bldRoofColor(b.type);

    // Roof (pitched triangle overlay)
    SDL_SetRenderDrawColor(ren_,rc.r,rc.g,rc.b,190);
    for (int dy=0;dy<TILE;dy++) {
        double t2=(double)dy/TILE;
        int lx=(int)(pw*0.5*(1-t2));
        SDL_RenderDrawLine(ren_,sx+lx,sy-TILE+dy,sx+pw-lx,sy-TILE+dy);
    }
    // Roof ridge
    SDL_SetRenderDrawColor(ren_,rc.r/2,rc.g/2,rc.b/2,255);
    SDL_RenderDrawLine(ren_,sx,sy,sx+pw/2,sy-TILE);
    SDL_RenderDrawLine(ren_,sx+pw/2,sy-TILE,sx+pw,sy);

    // Sign above door
    int doorPx=sx+(b.w/2)*TILE;
    int signW=std::min(pw-4,72), signH=14;
    int signX=doorPx-signW/2, signY=sy+(b.h-2)*TILE-18;
    SDL_SetRenderDrawColor(ren_,90,48,16,255); fillRect(ren_,signX,signY,signW,signH);
    textCentered(bldLabel(b.type),doorPx,signY+2,{255,208,128,255},fontSm_);
}

void Game::drawItems() {
    for (auto& it:items_) {
        if (it.collected) continue;
        int sx=(int)(it.x-camX_), sy=(int)(it.y-camY_+(int)(std::sin(it.bob)*3));
        if (sx<-30||sx>SCREEN_W+30||sy<-30||sy>SCREEN_H+30) continue;

        auto def=itemDef(it.kind);
        // Glow
        SDL_SetRenderDrawColor(ren_,def.color.r,def.color.g,def.color.b,50);
        fillCircle(ren_,sx,sy,14);
        // Shadow
        SDL_SetRenderDrawColor(ren_,0,0,0,50);
        fillRect(ren_,sx-10,(int)(it.y-camY_)+8,20,7);
        // Box
        SDL_SetRenderDrawColor(ren_,30,20,10,200); fillRect(ren_,sx-10,sy-10,20,20);
        SDL_SetRenderDrawColor(ren_,def.color.r,def.color.g,def.color.b,255); drawRect(ren_,sx-10,sy-10,20,20);
        // Icon fill
        SDL_SetRenderDrawColor(ren_,def.color.r,def.color.g,def.color.b,255);
        switch(def.cat) {
            case ItemCat::MELEE:  SDL_RenderDrawLine(ren_,sx-5,sy+5,sx+5,sy-5); break;
            case ItemCat::RANGED: fillRect(ren_,sx-5,sy-1,10,3); break;
            case ItemCat::FOOD:   fillCircle(ren_,sx,sy,5); break;
            case ItemCat::ARMOUR: fillRect(ren_,sx-4,sy-5,8,10); break;
        }
        // Label
        textCentered(def.label,sx,sy+12,{255,255,255,255},fontSm_);
    }
}

// ── Entity draw helpers ───────────────────────────────────────────────────────
static void drawShadow(SDL_Renderer* r,int sx,int sy){SDL_SetRenderDrawColor(r,0,0,0,50);fillRect(r,sx-10,sy+5,20,8);}
static const int DIRS[4][2]={{0,1},{0,-1},{-1,0},{1,0}}; // down up left right

void Game::drawOneNPC(NPC& n) {
    int sx=(int)(n.x-camX_), sy=(int)(n.y-camY_);
    int bob=n.moving?(int)(std::sin(n.frame*M_PI)*2):0;
    int ls=n.moving?(int)(std::sin(n.frame*M_PI)*3):0;
    SDL_Color body,skin;
    switch(n.job){
        case NpcJob::VILLAGER: body={74,143,63,255}; skin={244,200,122,255}; break;
        case NpcJob::MERCHANT: body={200,160,32,255}; skin={240,208,144,255}; break;
        case NpcJob::GUARD:    body={80,80,144,255};  skin={208,208,208,255}; break;
        case NpcJob::ELDER:    body={128,96,80,255};  skin={232,216,184,255}; break;
        case NpcJob::WANDERER: body={80,128,80,255};  skin={208,232,192,255}; break;
    }
    drawShadow(ren_,sx,sy);
    // Legs
    setColor(ren_,{(Uint8)(body.r/2),(Uint8)(body.g/2),(Uint8)(body.b/2),255});
    fillRect(ren_,sx-5+ls,sy+7+bob,4,7); fillRect(ren_,sx+1-ls,sy+7+bob,4,7);
    // Body
    setColor(ren_,body); fillRect(ren_,sx-7,sy-10+bob,14,18);
    // Head
    setColor(ren_,skin); fillCircle(ren_,sx,sy-18+bob,8);
    // Eyes
    SDL_SetRenderDrawColor(ren_,42,26,10,255);
    fillRect(ren_,sx+DIRS[n.dir][0]*2-3,sy-20+bob+DIRS[n.dir][1]*2,3,3);
    fillRect(ren_,sx+DIRS[n.dir][0]*2+1,sy-20+bob+DIRS[n.dir][1]*2,3,3);
    // Accessories
    switch(n.job){
        case NpcJob::MERCHANT:
            SDL_SetRenderDrawColor(ren_,139,69,19,255);
            fillRect(ren_,sx-9,sy-30+bob,18,5); fillRect(ren_,sx-6,sy-35+bob,12,7); break;
        case NpcJob::GUARD:
            SDL_SetRenderDrawColor(ren_,128,128,144,255);
            fillCircle(ren_,sx,sy-24+bob,9);
            SDL_SetRenderDrawColor(ren_,100,100,120,255);
            fillRect(ren_,sx-2,sy-20+bob,4,5); break;
        case NpcJob::ELDER:
            SDL_SetRenderDrawColor(ren_,139,105,20,255);
            fillRect(ren_,sx+8,sy-28+bob,3,36);
            SDL_SetRenderDrawColor(ren_,255,215,0,255);
            fillCircle(ren_,sx+9,sy-31+bob,4); break;
        case NpcJob::WANDERER:
            SDL_SetRenderDrawColor(ren_,107,66,38,255);
            fillRect(ren_,sx+5,sy-10+bob,8,12); break;
        default: break;
    }
    // Name
    int nlx=sx, nly=sy-40+bob;
    textCentered(n.name,nlx,nly,{255,238,187,255},fontSm_);
    // Speech bubble
    if (!n.speech.empty()) {
        // Wrap text at ~28 chars
        std::vector<std::string> lines;
        std::string cur; std::istringstream ss(n.speech); std::string word;
        while(ss>>word){ if(cur.size()+word.size()>28){lines.push_back(cur);cur="";} cur+=word+" "; }
        if(!cur.empty()) lines.push_back(cur);
        int bw=160,bh=(int)lines.size()*14+8;
        int bx=sx-bw/2, by=sy-56-bh;
        bx=std::max(2,std::min(bx,SCREEN_W-bw-2));
        SDL_SetRenderDrawColor(ren_,255,255,230,220); fillRect(ren_,bx,by,bw,bh);
        SDL_SetRenderDrawColor(ren_,80,60,20,255); drawRect(ren_,bx,by,bw,bh);
        for(int i=0;i<(int)lines.size();i++) text(lines[i],bx+5,by+4+i*14,{42,26,10,255},fontSm_);
    }
}

void Game::drawOneEnemy(Enemy& e) {
    int sx=(int)(e.x-camX_), sy=(int)(e.y-camY_);
    int bob=e.moving?(int)(std::sin(e.frame*M_PI)*2):0;
    int ls=e.moving?(int)(std::sin(e.frame*M_PI)*3):0;
    auto def=enemyDef(e.kind);
    SDL_Color body=e.hitFlash>0?SDL_Color{255,255,255,255}:def.color;

    drawShadow(ren_,sx,sy);

    if (e.kind==EnemyKind::SLIME) {
        setColor(ren_,body); fillCircle(ren_,sx,sy-4+bob,12);
        SDL_SetRenderDrawColor(ren_,0,0,0,160);
        fillRect(ren_,sx-5,sy-7+bob,4,4); fillRect(ren_,sx+1,sy-7+bob,4,4);
    } else if (e.kind==EnemyKind::SKELETON) {
        setColor(ren_,body);
        SDL_RenderDrawLine(ren_,sx-3,sy+8+bob,sx-3+ls,sy+16+bob);
        SDL_RenderDrawLine(ren_,sx+3,sy+8+bob,sx+3-ls,sy+16+bob);
        drawRect(ren_,sx-6,sy-8+bob,12,16);
        for(int ri=0;ri<3;ri++) SDL_RenderDrawLine(ren_,sx-6,sy-4+ri*4+bob,sx+6,sy-4+ri*4+bob);
        fillCircle(ren_,sx,sy-20+bob,7);
        SDL_SetRenderDrawColor(ren_,26,26,42,255);
        fillRect(ren_,sx-4,sy-23+bob,3,3); fillRect(ren_,sx+1,sy-23+bob,3,3);
    } else {
        // Humanoid
        SDL_Color legC={(Uint8)(body.r/2),(Uint8)(body.g/2),(Uint8)(body.b/2),255};
        setColor(ren_,legC); fillRect(ren_,sx-5+ls,sy+7+bob,4,8); fillRect(ren_,sx+1-ls,sy+7+bob,4,8);
        setColor(ren_,body); fillRect(ren_,sx-7,sy-10+bob,14,18);
        fillCircle(ren_,sx,sy-20+bob,8);
        SDL_SetRenderDrawColor(ren_,255,34,0,255);
        fillRect(ren_,sx-3,sy-23+bob,3,3); fillRect(ren_,sx+1,sy-23+bob,3,3);
        // Weapon
        SDL_SetRenderDrawColor(ren_,128,128,128,255);
        if(def.ranged) fillRect(ren_,sx+8,sy-14+bob,3,22);
        else           fillRect(ren_,sx+8,sy-6+bob,14,3);
    }

    // Health bar
    int bw=28,bh=4,bx=sx-bw/2,by2=sy-32;
    SDL_SetRenderDrawColor(ren_,0,0,0,150); fillRect(ren_,bx-1,by2-1,bw+2,bh+2);
    SDL_SetRenderDrawColor(ren_,100,0,0,255); fillRect(ren_,bx,by2,bw,bh);
    float pct=(float)e.hp/def.maxHp;
    SDL_Color hpc=pct>0.5f?SDL_Color{68,204,68,255}:pct>0.25f?SDL_Color{238,170,0,255}:SDL_Color{238,34,34,255};
    setColor(ren_,hpc); fillRect(ren_,bx,by2,(int)(bw*pct),bh);
    // Name
    textCentered(def.name,sx,sy-44,{255,136,136,255},fontSm_);
}

void Game::drawPlayer() {
    auto& p=player_;
    int sx=(int)(p.x-camX_), sy=(int)(p.y-camY_);
    int bob=p.moving?(int)(std::sin(p.frame*M_PI)*2):0;
    int ls=p.moving?(int)(std::sin(p.frame*M_PI)*4):0;
    SDL_Color body=p.hitFlash>0?SDL_Color{255,255,255,255}:SDL_Color{58,95,205,255};

    drawShadow(ren_,sx,sy);

    SDL_SetRenderDrawColor(ren_,42,58,138,255);
    fillRect(ren_,sx-6+ls,sy+8+bob,5,8); fillRect(ren_,sx+1-ls,sy+8+bob,5,8);

    setColor(ren_,body); fillRect(ren_,sx-8,sy-12+bob,16,20);

    // Weapon
    Item* w=equipped();
    SDL_Color wc=w?itemDef(w->kind).color:SDL_Color{192,192,192,255};
    setColor(ren_,wc);
    switch(p.dir) {
        case 3: fillRect(ren_,sx+8,sy-8+bob,16,3);   break; // right
        case 2: fillRect(ren_,sx-24,sy-8+bob,16,3);  break; // left
        case 1: fillRect(ren_,sx+6,sy-28+bob,3,16);  break; // up
        case 0: fillRect(ren_,sx+6,sy-8+bob,3,16);   break; // down
    }
    SDL_SetRenderDrawColor(ren_,200,160,32,255);
    switch(p.dir) {
        case 3: fillRect(ren_,sx+6,sy-10+bob,4,7);   break;
        case 2: fillRect(ren_,sx-10,sy-10+bob,4,7);  break;
        case 1: fillRect(ren_,sx+4,sy-14+bob,7,4);   break;
        case 0: fillRect(ren_,sx+4,sy-10+bob,7,4);   break;
    }

    SDL_SetRenderDrawColor(ren_,244,200,122,255); fillCircle(ren_,sx,sy-18+bob,9);
    SDL_SetRenderDrawColor(ren_,42,26,10,255);
    fillRect(ren_,sx+DIRS[p.dir][0]*2-4,sy-22+bob+DIRS[p.dir][1]*2,4,4);
    fillRect(ren_,sx+DIRS[p.dir][0]*2+1,sy-22+bob+DIRS[p.dir][1]*2,4,4);

    text("YOU",sx-9,sy-38+bob,{255,215,0,255},fontSm_);
}

void Game::drawProjectiles() {
    for (auto& p:projs_) {
        int sx=(int)(p.x-camX_), sy=(int)(p.y-camY_);
        SDL_Color c=p.fromPlayer?SDL_Color{255,238,68,255}:SDL_Color{255,68,34,255};
        SDL_SetRenderDrawColor(ren_,c.r,c.g,c.b,180); fillCircle(ren_,sx,sy,4);
        SDL_SetRenderDrawColor(ren_,c.r,c.g,c.b,255); fillCircle(ren_,sx,sy,2);
    }
}

void Game::drawFloats() {
    for (auto& f:floats_) {
        int sx=(int)(f.x-camX_), sy=(int)(f.y-camY_);
        float a=(float)std::min(1.0,f.life*2);
        SDL_Color c={(Uint8)f.color.r,(Uint8)f.color.g,(Uint8)f.color.b,(Uint8)(255*a)};
        text(f.text,sx,sy,c);
    }
}

void Game::drawMinimap() {
    const int MW=140,MH=105,MX=SCREEN_W-MW-8,MY=8;
    SDL_SetRenderDrawColor(ren_,0,0,0,180);
    fillRect(ren_,MX-2,MY-2,MW+4,MH+4);

    SDL_Rect dst{MX,MY,MW,MH};
    SDL_RenderCopy(ren_,minimapTex_,nullptr,&dst);

    // Viewport rect
    double sx2=MW/(double)WORLD_W, sy2=MH/(double)WORLD_H;
    int vx=(int)(camX_/TILE*sx2), vy=(int)(camY_/TILE*sy2);
    int vw=(int)(SCREEN_W/(double)TILE*sx2), vh=(int)(SCREEN_H/(double)TILE*sy2);
    SDL_SetRenderDrawColor(ren_,255,255,255,160);
    SDL_Rect vr{MX+vx,MY+vy,vw,vh}; SDL_RenderDrawRect(ren_,&vr);

    // Player dot
    int pdx=(int)(player_.x/TILE*sx2), pdy=(int)(player_.y/TILE*sy2);
    SDL_SetRenderDrawColor(ren_,255,51,51,255); fillCircle(ren_,MX+pdx,MY+pdy,3);
    SDL_SetRenderDrawColor(ren_,255,255,255,255); drawRect(ren_,MX+pdx-3,MY+pdy-3,6,6);

    SDL_SetRenderDrawColor(ren_,255,255,255,60);
    SDL_Rect br{MX-2,MY-2,MW+4,MH+4}; SDL_RenderDrawRect(ren_,&br);
    text("MAP",MX+2,MY+MH+1,{180,200,220,255},fontSm_);
}

void Game::drawHUD() {
    // HP bar
    int bw=160,bh=14,bx=10,by=10;
    SDL_SetRenderDrawColor(ren_,0,0,0,160); fillRect(ren_,bx-2,by-2,bw+4,bh+4);
    SDL_SetRenderDrawColor(ren_,100,0,0,255); fillRect(ren_,bx,by,bw,bh);
    float pct=(float)player_.hp/player_.maxHp;
    SDL_Color hpc=pct>0.5f?SDL_Color{68,204,68,255}:pct>0.25f?SDL_Color{238,170,0,255}:SDL_Color{238,34,34,255};
    setColor(ren_,hpc); fillRect(ren_,bx,by,(int)(bw*pct),bh);
    char buf[64]; snprintf(buf,sizeof(buf),"HP %d/%d",player_.hp,player_.maxHp);
    text(buf,bx+4,by+1,{255,255,255,255});

    // XP bar
    int xbx=10,xby=28;
    SDL_SetRenderDrawColor(ren_,0,0,0,140); fillRect(ren_,xbx,xby,bw,6);
    SDL_SetRenderDrawColor(ren_,68,136,255,255);
    fillRect(ren_,xbx,xby,(int)(bw*(player_.xp/(float)(player_.level*100))),6);
    snprintf(buf,sizeof(buf),"LVL %d",player_.level);
    text(buf,10,38,{170,204,255,255},fontSm_);

    // Weapon
    Item* w=equipped();
    snprintf(buf,sizeof(buf),"WEP: %s",w?itemDef(w->kind).label:"Fists");
    text(buf,10,58,{255,208,128,255},fontSm_);

    // Bottom bar
    int tx=(int)(player_.x/TILE),ty2=(int)(player_.y/TILE);
    SDL_SetRenderDrawColor(ren_,0,0,0,140); fillRect(ren_,0,SCREEN_H-22,SCREEN_W,22);
    snprintf(buf,sizeof(buf),"WASD=Move  F=Attack  1-8=Equip  E=Talk  |  %s (%d,%d)",
             tileZone(world_.get(tx,ty2)),tx,ty2);
    text(buf,8,SCREEN_H-18,{170,221,255,255},fontSm_);

    // NPC hint
    bool npcClose=false;
    for(auto& n:npcs_){double dx=player_.x-n.x,dy2=player_.y-n.y;if(dx*dx+dy2*dy2<44*44){npcClose=true;break;}}
    if (npcClose) text("[E] Talk",SCREEN_W-80,SCREEN_H-18,{255,215,0,255},fontSm_);
}

void Game::drawInventoryBar() {
    const int SW=36,SH=36,GAP=4;
    int total=8*(SW+GAP)-GAP;
    int startX=(SCREEN_W-total)/2, startY=SCREEN_H-62;

    for (int i=0;i<8;i++) {
        int sx=startX+i*(SW+GAP);
        bool equipped=(i==player_.equippedSlot);
        SDL_SetRenderDrawColor(ren_,equipped?80:0,equipped?40:0,equipped?0:0,equipped?200:140);
        fillRect(ren_,sx,startY,SW,SH);
        SDL_SetRenderDrawColor(ren_,equipped?255:255,equipped?160:255,equipped?64:255,equipped?255:60);
        drawRect(ren_,sx,startY,SW,SH);

        char numBuf[4]; snprintf(numBuf,sizeof(numBuf),"%d",i+1);
        text(numBuf,sx+2,startY+1,{255,255,255,80},fontSm_);

        if (i<player_.invCount && player_.inv[i]) {
            auto def=itemDef(player_.inv[i]->kind);
            setColor(ren_,def.color); fillRect(ren_,sx+8,startY+10,SW-16,SH-20);
            std::string abbr(def.label,0,std::min(4,(int)strlen(def.label)));
            textCentered(abbr,sx+SW/2,startY+26,{255,255,255,255},fontSm_);
        }
    }
}

void Game::drawGameOver() {
    SDL_SetRenderDrawColor(ren_,0,0,0,160); fillRect(ren_,0,0,SCREEN_W,SCREEN_H);
    textCentered("YOU DIED",SCREEN_W/2,SCREEN_H/2-30,{255,51,51,255});
    textCentered("Press R to restart",SCREEN_W/2,SCREEN_H/2+10,{255,255,255,255},fontSm_);
    char buf[64]; snprintf(buf,sizeof(buf),"Level %d  |  XP: %d",player_.level,player_.xp);
    textCentered(buf,SCREEN_W/2,SCREEN_H/2+32,{255,208,128,255},fontSm_);
}

void Game::drawVignette() {
    // Approximate radial vignette with concentric rects
    for (int i=0;i<8;i++) {
        int margin=i*30;
        SDL_SetRenderDrawColor(ren_,0,0,0,(Uint8)(i*5));
        SDL_Rect r{margin,margin,SCREEN_W-margin*2,SCREEN_H-margin*2};
        SDL_RenderDrawRect(ren_,&r);
    }
    // Dark corners
    int cs=120;
    SDL_SetRenderDrawColor(ren_,0,0,0,60);
    fillRect(ren_,0,0,cs,cs); fillRect(ren_,SCREEN_W-cs,0,cs,cs);
    fillRect(ren_,0,SCREEN_H-cs,cs,cs); fillRect(ren_,SCREEN_W-cs,SCREEN_H-cs,cs,cs);
}

const char* Game::npcName(unsigned int seed) {
    return NAMES[seed%16];
}
