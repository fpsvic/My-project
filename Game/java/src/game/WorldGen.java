package game;

import java.util.*;

/** Fixed 160×120 tile world generated once at startup. */
public class WorldGen {

    public static final int WORLD_W = 160;
    public static final int WORLD_H = 120;

    private final TileType[][] tiles = new TileType[WORLD_H][WORLD_W];
    private final List<Building> buildings = new ArrayList<>();

    public WorldGen() {
        generate();
        placeBuildings();
        carveRoads();
    }

    // ── Public API ────────────────────────────────────────────────────────────

    public TileType get(int tx, int ty) {
        if (tx < 0 || tx >= WORLD_W || ty < 0 || ty >= WORLD_H) return TileType.DEEP_WATER;
        for (Building b : buildings) {
            TileType bt = b.tileAt(tx, ty);
            if (bt != null) return bt;
        }
        return tiles[ty][tx];
    }

    public TileType terrain(int tx, int ty) {
        if (tx < 0 || tx >= WORLD_W || ty < 0 || ty >= WORLD_H) return TileType.DEEP_WATER;
        return tiles[ty][tx];
    }

    public List<Building> getBuildings() { return buildings; }

    public TileType[][] getRawTiles() { return tiles; }

    // ── Generation ────────────────────────────────────────────────────────────

    private void generate() {
        for (int y = 0; y < WORLD_H; y++) {
            for (int x = 0; x < WORLD_W; x++) {
                double cx   = (x / (double) WORLD_W - 0.5) * 2;
                double cy   = (y / (double) WORLD_H - 0.5) * 2;
                double dist = Math.sqrt(cx * cx + cy * cy);
                double h    = smooth(x, y, 42) - dist * 0.50;
                tiles[y][x] = classify(h);
            }
        }
    }

    private TileType classify(double h) {
        if (h < 0.08) return TileType.DEEP_WATER;
        if (h < 0.17) return TileType.SHALLOW_WATER;
        if (h < 0.23) return TileType.SAND;
        if (h < 0.48) return TileType.GRASS;
        if (h < 0.58) return TileType.DARK_GRASS;
        if (h < 0.70) return TileType.FOREST;
        if (h < 0.80) return TileType.MOUNTAIN;
        return TileType.SNOW;
    }

    // ── Buildings ─────────────────────────────────────────────────────────────

    private static final int[][] VILLAGE_CENTRES = {
        {30,25},{120,25},{55,55},{100,55},{78,35},{40,90},{125,85},{78,95}
    };

    private void placeBuildings() {
        Random rng = new Random(7777);
        Building.Type[] types = Building.Type.values();
        for (int[] vc : VILLAGE_CENTRES) {
            int numBuildings = 2 + rng.nextInt(4);
            for (int k = 0; k < numBuildings; k++) {
                int w = 5 + rng.nextInt(3) * 2;
                int h = 5 + rng.nextInt(3) * 2;
                int bx = vc[0] + rng.nextInt(16) - 8;
                int by = vc[1] + rng.nextInt(16) - 8;
                if (!canPlace(bx, by, w, h)) continue;
                Building.Type type = types[rng.nextInt(types.length)];
                buildings.add(new Building(bx, by, w, h, type));
            }
        }
    }

    private boolean canPlace(int bx, int by, int w, int h) {
        if (bx < 2 || by < 2 || bx + w >= WORLD_W - 2 || by + h >= WORLD_H - 2) return false;
        for (int dy = -1; dy <= h; dy++)
            for (int dx = -1; dx <= w; dx++) {
                TileType t = tiles[by + dy][bx + dx];
                if (!t.walkable || t == TileType.FOREST) return false;
            }
        // No overlap with existing buildings
        for (Building b : buildings)
            if (bx < b.x + b.w + 2 && bx + w > b.x - 2 && by < b.y + b.h + 2 && by + h > b.y - 2)
                return false;
        return true;
    }

    private void carveRoads() {
        for (int i = 0; i < VILLAGE_CENTRES.length - 1; i++)
            carvePath(VILLAGE_CENTRES[i][0], VILLAGE_CENTRES[i][1],
                      VILLAGE_CENTRES[i+1][0], VILLAGE_CENTRES[i+1][1]);
    }

    private void carvePath(int x1, int y1, int x2, int y2) {
        int x = x1, y = y1;
        while (x != x2 || y != y2) {
            if (tiles[y][x].walkable && tiles[y][x] != TileType.FOREST) tiles[y][x] = TileType.PATH;
            if      (x < x2) x++;
            else if (x > x2) x--;
            if      (y < y2) y++;
            else if (y > y2) y--;
        }
    }

    // ── Noise ─────────────────────────────────────────────────────────────────

    public double smooth(double x, double y, double seed) {
        double v = 0, amp = 1, freq = 1, max = 0;
        for (int o = 0; o < 6; o++) {
            v   += hash(x * freq / 40.0, y * freq / 40.0, seed + o) * amp;
            max += amp; amp *= 0.5; freq *= 2.0;
        }
        return v / max;
    }

    public double hash(double x, double y, double seed) {
        double v = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
        return v - Math.floor(v);
    }
}
