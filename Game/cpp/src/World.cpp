#include "World.h"
#include "Noise.h"
#include <cmath>
#include <cstdlib>

static const int CENTRES[][2] = {
    {30,25},{120,25},{55,55},{100,55},{78,35},{40,90},{125,85},{78,95}
};
static const int N_CENTRES = 8;

// ── Building interior ─────────────────────────────────────────────────────────
Tile Building::tileAt(int tx, int ty) const {
    int lx = tx - x, ly = ty - y;
    if (lx<0||lx>=w||ly<0||ly>=h) return Tile::GRASS; // fallback
    return interior[ly][lx];
}

static void buildInterior(Building& b) {
    for (int ly=0;ly<b.h;ly++)
        for (int lx=0;lx<b.w;lx++) {
            bool edge=(lx==0||lx==b.w-1||ly==0||ly==b.h-1);
            b.interior[ly][lx] = edge ? Tile::WALL : Tile::FLOOR;
        }
    b.interior[b.h-1][b.w/2] = Tile::DOOR;
}

// ── World ─────────────────────────────────────────────────────────────────────
World::World() {
    generate();
    placeBuildings();
    carveRoads();
}

Tile World::terrain(int tx,int ty) const {
    if (tx<0||tx>=WORLD_W||ty<0||ty>=WORLD_H) return Tile::DEEP_WATER;
    return tiles_[ty][tx];
}

Tile World::get(int tx,int ty) const {
    if (tx<0||tx>=WORLD_W||ty<0||ty>=WORLD_H) return Tile::DEEP_WATER;
    for (auto& b : blds_)
        if (b.contains(tx,ty)) return b.tileAt(tx,ty);
    return tiles_[ty][tx];
}

void World::generate() {
    for (int y=0;y<WORLD_H;y++) {
        for (int x=0;x<WORLD_W;x++) {
            double cx=(x/(double)WORLD_W-0.5)*2;
            double cy=(y/(double)WORLD_H-0.5)*2;
            double dist=std::sqrt(cx*cx+cy*cy);
            double h=smoothN(x,y,42)-dist*0.50;
            tiles_[y][x]=classify(h);
        }
    }
}

Tile World::classify(double h) {
    if (h<0.08) return Tile::DEEP_WATER;
    if (h<0.17) return Tile::SHALLOW_WATER;
    if (h<0.23) return Tile::SAND;
    if (h<0.48) return Tile::GRASS;
    if (h<0.58) return Tile::DARK_GRASS;
    if (h<0.70) return Tile::FOREST;
    if (h<0.80) return Tile::MOUNTAIN;
    return Tile::SNOW;
}

bool World::canPlace(int bx,int by,int bw,int bh) {
    if (bx<2||by<2||bx+bw>=WORLD_W-2||by+bh>=WORLD_H-2) return false;
    for (int dy=-1;dy<=bh;dy++)
        for (int dx=-1;dx<=bw;dx++) {
            Tile t=tiles_[by+dy][bx+dx];
            if (!tileWalkable(t)||t==Tile::FOREST) return false;
        }
    for (auto& b:blds_)
        if (bx<b.x+b.w+2&&bx+bw>b.x-2&&by<b.y+b.h+2&&by+bh>b.y-2) return false;
    return true;
}

void World::placeBuildings() {
    static const BldType types[]={BldType::INN,BldType::SHOP,BldType::BLACKSMITH,BldType::CHURCH,BldType::HOUSE};
    unsigned int seed=7777;
    auto rnd=[&](int n){ seed=seed*1664525+1013904223; return (int)((seed>>16)%n); };
    for (auto& vc:CENTRES) {
        int count=2+rnd(4);
        for (int k=0;k<count;k++) {
            int w=5+rnd(3)*2, h=5+rnd(3)*2;
            int bx=vc[0]+rnd(16)-8, by=vc[1]+rnd(16)-8;
            if (!canPlace(bx,by,w,h)) continue;
            Building b; b.x=bx; b.y=by; b.w=w; b.h=h;
            b.type=types[rnd(5)];
            buildInterior(b);
            blds_.push_back(b);
        }
    }
}

void World::carveRoads() {
    for (int i=0;i<N_CENTRES-1;i++)
        carvePath(CENTRES[i][0],CENTRES[i][1],CENTRES[i+1][0],CENTRES[i+1][1]);
}

void World::carvePath(int x1,int y1,int x2,int y2) {
    int x=x1,y=y1;
    while (x!=x2||y!=y2) {
        if (tileWalkable(tiles_[y][x])&&tiles_[y][x]!=Tile::FOREST)
            tiles_[y][x]=Tile::PATH;
        if      (x<x2) x++;
        else if (x>x2) x--;
        if      (y<y2) y++;
        else if (y>y2) y--;
    }
}
