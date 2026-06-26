package game;

public class WorldGen {

    public static final int WORLD_W = 80;
    public static final int WORLD_H = 60;

    private final TileType[][] tiles = new TileType[WORLD_H][WORLD_W];

    public WorldGen() {
        generate();
    }

    public TileType get(int tx, int ty) {
        if (tx < 0 || tx >= WORLD_W || ty < 0 || ty >= WORLD_H) return TileType.DEEP_WATER;
        return tiles[ty][tx];
    }

    public TileType[][] getTiles() { return tiles; }

    // ── Noise ─────────────────────────────────────────────────────────────────

    private double hash(double x, double y, double seed) {
        double v = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
        return v - Math.floor(v);
    }

    private double smooth(double x, double y, double seed) {
        double v = 0, amp = 1, freq = 1, max = 0;
        for (int o = 0; o < 6; o++) {
            v   += hash(x * freq / 20.0, y * freq / 20.0, seed + o) * amp;
            max += amp;
            amp  *= 0.5;
            freq *= 2.0;
        }
        return v / max;
    }

    // ── Generation ────────────────────────────────────────────────────────────

    private void generate() {
        final int SEED = 42;
        for (int y = 0; y < WORLD_H; y++) {
            for (int x = 0; x < WORLD_W; x++) {
                double cx   = (x / (double) WORLD_W - 0.5) * 2;
                double cy   = (y / (double) WORLD_H - 0.5) * 2;
                double dist = Math.sqrt(cx * cx + cy * cy);
                double h    = smooth(x, y, SEED) - dist * 0.55;
                tiles[y][x] = classify(h);
            }
        }
        placeVillages();
    }

    private TileType classify(double h) {
        if (h < 0.05) return TileType.DEEP_WATER;
        if (h < 0.15) return TileType.SHALLOW_WATER;
        if (h < 0.22) return TileType.SAND;
        if (h < 0.45) return TileType.GRASS;
        if (h < 0.55) return TileType.DARK_GRASS;
        if (h < 0.68) return TileType.FOREST;
        if (h < 0.78) return TileType.MOUNTAIN;
        return TileType.SNOW;
    }

    private void placeVillages() {
        int[][] villages = {{20,20},{55,18},{30,40},{50,45},{38,30}};
        for (int[] v : villages) {
            for (int dy = -1; dy <= 1; dy++) {
                for (int dx = -1; dx <= 1; dx++) {
                    int nx = v[0]+dx, ny = v[1]+dy;
                    if (nx<0||nx>=WORLD_W||ny<0||ny>=WORLD_H) continue;
                    if (!tiles[ny][nx].walkable) continue;
                    tiles[ny][nx] = (dx==0&&dy==0) ? TileType.VILLAGE : TileType.PATH;
                }
            }
        }
        for (int i = 0; i < villages.length - 1; i++)
            carvePath(villages[i][0], villages[i][1], villages[i+1][0], villages[i+1][1]);
    }

    private void carvePath(int x1, int y1, int x2, int y2) {
        int x = x1, y = y1;
        while (x != x2 || y != y2) {
            if (tiles[y][x].walkable) tiles[y][x] = TileType.PATH;
            if      (x < x2) x++;
            else if (x > x2) x--;
            if      (y < y2) y++;
            else if (y > y2) y--;
        }
    }
}
