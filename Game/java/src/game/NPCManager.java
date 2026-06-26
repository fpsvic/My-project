package game;

import java.util.*;

/**
 * Spawns and manages NPCs. NPCs are generated per chunk and cached.
 * Only NPCs near the player are updated each frame.
 */
public class NPCManager {

    private static final int TILE       = GamePanel.TILE;
    private static final int CHUNK      = WorldGen.CHUNK_SIZE;
    private static final double TALK_RADIUS = 40.0;

    private final WorldGen world;
    private final Map<Long, List<NPC>> chunkNPCs = new HashMap<>();

    public NPCManager(WorldGen world) {
        this.world = world;
    }

    /** Returns all NPCs whose chunk overlaps the view rectangle (in world pixels). */
    public List<NPC> getNPCsInView(double camX, double camY, int viewW, int viewH) {
        int cx0 = (int)Math.floor(camX / (CHUNK * TILE)) - 1;
        int cy0 = (int)Math.floor(camY / (CHUNK * TILE)) - 1;
        int cx1 = (int)Math.floor((camX + viewW) / (CHUNK * TILE)) + 1;
        int cy1 = (int)Math.floor((camY + viewH) / (CHUNK * TILE)) + 1;

        List<NPC> result = new ArrayList<>();
        for (int cy = cy0; cy <= cy1; cy++)
            for (int cx = cx0; cx <= cx1; cx++)
                result.addAll(getChunkNPCs(cx, cy));
        return result;
    }

    public void tryTalk(double playerX, double playerY) {
        List<NPC> nearby = getNPCsInView(playerX - 80, playerY - 80, 160, 160);
        for (NPC npc : nearby)
            if (npc.isNear(playerX, playerY, TALK_RADIUS))
                npc.startTalk();
    }

    // ── Chunk NPC generation ──────────────────────────────────────────────────

    private List<NPC> getChunkNPCs(int cx, int cy) {
        long key = chunkKey(cx, cy);
        if (!chunkNPCs.containsKey(key))
            chunkNPCs.put(key, spawnNPCs(cx, cy));
        return chunkNPCs.get(key);
    }

    private List<NPC> spawnNPCs(int cx, int cy) {
        List<NPC> list = new ArrayList<>();
        Random rng = new Random(chunkKey(cx, cy) ^ 0xDEADBEEFL);
        int count = rng.nextInt(4); // 0-3 NPCs per chunk
        for (int i = 0; i < count; i++) {
            int lx = 2 + rng.nextInt(CHUNK - 4);
            int ly = 2 + rng.nextInt(CHUNK - 4);
            int wx = cx * CHUNK + lx;
            int wy = cy * CHUNK + ly;
            if (!world.get(wx, wy).walkable) continue;
            NPC.Profession job = NPC.Profession.values()[rng.nextInt(NPC.Profession.values().length)];
            long seed = rng.nextLong();
            NPC npc = new NPC(wx * TILE + TILE / 2.0, wy * TILE + TILE / 2.0, job, Math.abs(seed), world);
            list.add(npc);
        }
        return list;
    }

    private long chunkKey(int cx, int cy) { return ((long)(cx + 100000)) << 32 | (cy + 100000); }
}
