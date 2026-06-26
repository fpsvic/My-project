package game;

import java.util.*;

/**
 * Infinite procedural world using a chunk cache.
 * Each chunk is CHUNK_SIZE x CHUNK_SIZE tiles generated on demand.
 */
public class WorldGen {

    public static final int CHUNK_SIZE = 32;

    // Chunk storage: key = "cx,cy"
    private final Map<Long, TileType[][]> chunks = new HashMap<>();
    // Buildings keyed by their top-left tile coordinate
    private final Map<Long, Building> buildings = new HashMap<>();

    // ── Public API ────────────────────────────────────────────────────────────

    public TileType get(int tx, int ty) {
        // Buildings override terrain
        Building b = getBuildingAt(tx, ty);
        if (b != null) return b.tileAt(tx, ty);
        return terrain(tx, ty);
    }

    public TileType terrain(int tx, int ty) {
        int cx = Math.floorDiv(tx, CHUNK_SIZE);
        int cy = Math.floorDiv(ty, CHUNK_SIZE);
        TileType[][] chunk = getChunk(cx, cy);
        int lx = Math.floorMod(tx, CHUNK_SIZE);
        int ly = Math.floorMod(ty, CHUNK_SIZE);
        return chunk[ly][lx];
    }

    /** Returns all buildings whose footprint overlaps the visible rect (in tiles). */
    public Collection<Building> getBuildingsInView(int tx0, int ty0, int tx1, int ty1) {
        List<Building> result = new ArrayList<>();
        // Scan chunk range
        int cx0 = Math.floorDiv(tx0, CHUNK_SIZE) - 1;
        int cy0 = Math.floorDiv(ty0, CHUNK_SIZE) - 1;
        int cx1 = Math.floorDiv(tx1, CHUNK_SIZE) + 1;
        int cy1 = Math.floorDiv(ty1, CHUNK_SIZE) + 1;
        for (int cy = cy0; cy <= cy1; cy++)
            for (int cx = cx0; cx <= cx1; cx++)
                getChunk(cx, cy); // ensures buildings for this chunk are generated
        for (Building b : buildings.values())
            if (b.x + b.w > tx0 && b.x < tx1 && b.y + b.h > ty0 && b.y < ty1)
                result.add(b);
        return result;
    }

    // ── Chunk generation ──────────────────────────────────────────────────────

    private TileType[][] getChunk(int cx, int cy) {
        long key = chunkKey(cx, cy);
        if (!chunks.containsKey(key)) {
            chunks.put(key, generateChunk(cx, cy));
            tryPlaceBuildings(cx, cy);
        }
        return chunks.get(key);
    }

    private TileType[][] generateChunk(int cx, int cy) {
        TileType[][] c = new TileType[CHUNK_SIZE][CHUNK_SIZE];
        for (int ly = 0; ly < CHUNK_SIZE; ly++) {
            for (int lx = 0; lx < CHUNK_SIZE; lx++) {
                int wx = cx * CHUNK_SIZE + lx;
                int wy = cy * CHUNK_SIZE + ly;
                c[ly][lx] = classify(noise(wx, wy));
            }
        }
        carvePaths(c, cx, cy);
        return c;
    }

    private TileType classify(double h) {
        if (h < 0.12) return TileType.DEEP_WATER;
        if (h < 0.20) return TileType.SHALLOW_WATER;
        if (h < 0.26) return TileType.SAND;
        if (h < 0.50) return TileType.GRASS;
        if (h < 0.60) return TileType.DARK_GRASS;
        if (h < 0.72) return TileType.FOREST;
        if (h < 0.82) return TileType.MOUNTAIN;
        return TileType.SNOW;
    }

    // Roads run on every chunk whose coordinate is divisible by 3
    private void carvePaths(TileType[][] c, int cx, int cy) {
        boolean hRoad = (cy % 3 == 0);
        boolean vRoad = (cx % 3 == 0);
        int mid = CHUNK_SIZE / 2;
        for (int i = 0; i < CHUNK_SIZE; i++) {
            if (hRoad && c[mid][i].walkable) c[mid][i] = TileType.PATH;
            if (vRoad && c[i][mid].walkable) c[i][mid] = TileType.PATH;
        }
    }

    // Place 0-2 buildings per chunk on flat walkable land
    private void tryPlaceBuildings(int cx, int cy) {
        double chance = hash(cx, cy, 7);
        if (chance < 0.55) return; // ~45 % of chunks get a building
        int count = chance > 0.80 ? 2 : 1;
        Random rng = new Random(chunkKey(cx, cy));
        for (int k = 0; k < count; k++) {
            int[] sizes = {5, 7, 9};
            int w = sizes[rng.nextInt(3)];
            int h = sizes[rng.nextInt(3)];
            // Random position inside chunk leaving 2-tile margin
            int lx = 2 + rng.nextInt(CHUNK_SIZE - w - 4);
            int ly = 2 + rng.nextInt(CHUNK_SIZE - h - 4);
            int wx = cx * CHUNK_SIZE + lx;
            int wy = cy * CHUNK_SIZE + ly;
            // Only place on walkable, non-water terrain
            boolean ok = true;
            for (int dy = 0; dy < h && ok; dy++)
                for (int dx = 0; dx < w && ok; dx++) {
                    TileType t = terrain(wx + dx, wy + dy);
                    if (!t.walkable || t == TileType.PATH) ok = false;
                }
            if (!ok) continue;
            Building.Type type = Building.Type.values()[rng.nextInt(Building.Type.values().length)];
            Building b = new Building(wx, wy, w, h, type);
            long bKey = tileKey(wx, wy);
            buildings.put(bKey, b);
        }
    }

    public Building getBuildingAt(int tx, int ty) {
        // Check all buildings (buildings are small so this is fine in practice;
        // for large worlds a spatial index would be used)
        for (Building b : buildings.values())
            if (tx >= b.x && tx < b.x + b.w && ty >= b.y && ty < b.y + b.h)
                return b;
        return null;
    }

    // ── Noise ─────────────────────────────────────────────────────────────────

    public double noise(int wx, int wy) {
        double v = 0, amp = 1, freq = 1, max = 0;
        for (int o = 0; o < 6; o++) {
            v   += hash(wx * freq / 40.0, wy * freq / 40.0, o) * amp;
            max += amp; amp *= 0.5; freq *= 2.0;
        }
        return v / max;
    }

    public double hash(double x, double y, double seed) {
        double v = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
        return v - Math.floor(v);
    }

    // ── Keys ──────────────────────────────────────────────────────────────────

    private long chunkKey(int cx, int cy) { return ((long)(cx + 100000)) << 32 | (cy + 100000); }
    private long tileKey(int tx, int ty)  { return ((long)(tx + 500000)) << 32 | (ty + 500000); }
}
