package game;

import java.util.*;

public class NPCManager {

    private static final int TILE  = GamePanel.TILE;
    private static final double TALK_RADIUS = 42.0;

    private final WorldGen   world;
    private final List<NPC>  allNPCs = new ArrayList<>();

    public NPCManager(WorldGen world) {
        this.world = world;
        spawnNPCs();
    }

    private void spawnNPCs() {
        int[][] centres = {{30,25},{120,25},{55,55},{100,55},{78,35},{40,90},{125,85},{78,95}};
        Random rng = new Random(9999);
        NPC.Profession[] profs = NPC.Profession.values();
        for (int[] vc : centres) {
            int count = 2 + rng.nextInt(4);
            for (int k = 0; k < count; k++) {
                int tx = vc[0] + rng.nextInt(10) - 5;
                int ty = vc[1] + rng.nextInt(10) - 5;
                if (tx < 1 || ty < 1 || tx >= WorldGen.WORLD_W-1 || ty >= WorldGen.WORLD_H-1) continue;
                if (!world.get(tx, ty).walkable) continue;
                NPC.Profession job = profs[rng.nextInt(profs.length)];
                long seed = Math.abs(rng.nextLong());
                allNPCs.add(new NPC(tx * TILE + TILE/2.0, ty * TILE + TILE/2.0, job, seed, world));
            }
        }
    }

    public List<NPC> getNPCsInView(double camX, double camY, int w, int h) {
        List<NPC> result = new ArrayList<>();
        for (NPC npc : allNPCs) {
            if (npc.x > camX - 60 && npc.x < camX + w + 60 &&
                npc.y > camY - 60 && npc.y < camY + h + 60)
                result.add(npc);
        }
        return result;
    }

    public void tryTalk(double px, double py) {
        for (NPC npc : allNPCs)
            if (npc.isNear(px, py, TALK_RADIUS))
                npc.startTalk(px, py);
    }
}
