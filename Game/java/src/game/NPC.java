package game;

import java.awt.*;
import java.util.Random;

public class NPC {

    public enum Profession {
        VILLAGER, MERCHANT, GUARD, ELDER, WANDERER
    }

    private static final String[] NAMES = {
        "Aldric","Benna","Cort","Dwyn","Elara","Fenn","Gara","Holt",
        "Iria","Joren","Kael","Lira","Mord","Nyla","Orin","Pyra"
    };

    // ── Contextual dialogue pools ─────────────────────────────────────────────
    // Called with player context at talk-time to pick the most relevant line.

    private static String[] villagerLines(boolean playerHurt, boolean enemiesNear) {
        if (enemiesNear) return new String[]{
            "Watch yourself! Monsters lurk near here!",
            "Please, keep them away from us!",
            "I saw something move in those trees..."
        };
        if (playerHurt) return new String[]{
            "You look wounded — rest a moment!",
            "There's a healer just down the road.",
            "Careful out there, adventurer."
        };
        return new String[]{
            "Lovely weather we're having.",
            "My crops are growing well this season.",
            "Have you heard the news from the east?",
            "A strange fog rolled in last night.",
            "The old mill has been quiet lately."
        };
    }

    private static String[] merchantLines(boolean playerHasItems, boolean playerHurt) {
        if (playerHurt) return new String[]{
            "You need a health potion, friend!",
            "I sell remedies — finest in the land.",
            "That wound looks nasty. Buy a potion?"
        };
        if (playerHasItems) return new String[]{
            "Fine equipment you've got there.",
            "You clearly know how to loot a battlefield!",
            "I'd trade good coin for rare finds."
        };
        return new String[]{
            "Buy somethin', will ya?",
            "Best prices in the whole realm!",
            "Got swords, potions, shields — all fresh stock.",
            "Trade routes have been dangerous lately.",
            "Every hero needs the right gear!"
        };
    }

    private static String[] guardLines(boolean enemiesNear, boolean playerLowLevel) {
        if (enemiesNear) return new String[]{
            "Sound the alarm! Enemies incoming!",
            "Defend the village!",
            "Stay back, citizen — I'll handle this."
        };
        if (playerLowLevel) return new String[]{
            "New around here? This land is dangerous.",
            "Train hard before venturing far.",
            "The forest to the north is no place for beginners."
        };
        return new String[]{
            "Move along, citizen.",
            "I've been posted here for three years.",
            "All quiet on my watch.",
            "Keep your weapons sheathed in town.",
            "Report any suspicious activity to me."
        };
    }

    private static String[] elderLines(boolean playerHighLevel, boolean worldExplored) {
        if (playerHighLevel) return new String[]{
            "Your power grows. The land needs you.",
            "I sense great destiny in you, hero.",
            "The ancient ruins hold secrets still."
        };
        if (worldExplored) return new String[]{
            "Few travelers venture so far and return.",
            "You've seen more of this world than most.",
            "The mountains hold old magic."
        };
        return new String[]{
            "The old ways must not be forgotten.",
            "Wisdom takes patience, child.",
            "I remember when this was all farmland.",
            "The stars speak of change to come.",
            "Every step forward is a lesson learned."
        };
    }

    private static String[] wandererLines(boolean nearWater, boolean nearMountain) {
        if (nearWater) return new String[]{
            "The sea calls to me...",
            "I once sailed beyond the horizon.",
            "Strange lights appear over the water at night."
        };
        if (nearMountain) return new String[]{
            "Those peaks are treacherous. Turn back.",
            "I found ruins high in the mountains once.",
            "The wind speaks up there. Truly."
        };
        return new String[]{
            "The horizon always calls to me.",
            "I come from lands far to the east.",
            "Every road leads somewhere new.",
            "I've walked this world for thirty years.",
            "Rest your feet when you can, traveler."
        };
    }

    // ── Instance fields ───────────────────────────────────────────────────────

    public final String name;
    public final Profession job;
    public double x, y;

    private double  targetX, targetY;
    private double  idleTimer;
    private boolean moving;
    private String  dir = "down";
    private int     frame;
    private double  frameTimer;
    private final double speed;

    public boolean talking;
    public String  currentLine;
    private double talkTimer;
    private static final double TALK_DURATION = 3.8;

    private final Color bodyColor;
    private final Color skinColor;

    private final WorldGen world;
    private final int TILE = GamePanel.TILE;
    private final Random rng;

    public NPC(double x, double y, Profession job, long seed, WorldGen world) {
        this.x = x; this.y = y; this.targetX = x; this.targetY = y;
        this.job = job; this.world = world;
        this.rng = new Random(seed);
        this.name = NAMES[(int)(seed % NAMES.length)];
        this.speed = 28 + rng.nextDouble() * 18;
        this.idleTimer = rng.nextDouble() * 3;

        // Assign colors per profession
        bodyColor = switch (job) {
            case VILLAGER  -> new Color(0x4a8f3f);
            case MERCHANT  -> new Color(0xc8a020);
            case GUARD     -> new Color(0x505090);
            case ELDER     -> new Color(0x806050);
            case WANDERER  -> new Color(0x508050);
        };
        skinColor = switch (job) {
            case VILLAGER  -> new Color(0xf4c87a);
            case MERCHANT  -> new Color(0xf0d090);
            case GUARD     -> new Color(0xd0d0d0);
            case ELDER     -> new Color(0xe8d8b8);
            case WANDERER  -> new Color(0xd0e8c0);
        };
    }

    // ── Update ────────────────────────────────────────────────────────────────

    public void update(double dt) {
        if (talking) {
            talkTimer -= dt;
            if (talkTimer <= 0) { talking = false; currentLine = null; }
            return;
        }
        if (!moving) {
            idleTimer -= dt;
            if (idleTimer <= 0) {
                double angle = rng.nextDouble() * Math.PI * 2;
                double dist  = 1 + rng.nextDouble() * 3;
                int tx = (int)((x + Math.cos(angle) * dist * TILE) / TILE);
                int ty = (int)((y + Math.sin(angle) * dist * TILE) / TILE);
                if (world.get(tx, ty).walkable) {
                    targetX = tx * TILE + TILE / 2.0;
                    targetY = ty * TILE + TILE / 2.0;
                    moving = true;
                }
                idleTimer = 1.5 + rng.nextDouble() * 3;
            }
        }
        if (moving) {
            double dx = targetX - x, dy = targetY - y;
            double dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < 2) {
                moving = false;
            } else {
                double nx = x + (dx/dist) * speed * dt;
                double ny = y + (dy/dist) * speed * dt;
                if (world.get((int)(nx/TILE),(int)(y/TILE)).walkable)  x = nx;
                if (world.get((int)(x/TILE),(int)(ny/TILE)).walkable) y = ny;
                if (Math.abs(dx)>Math.abs(dy)) dir = dx>0?"right":"left";
                else dir = dy>0?"down":"up";
            }
            frameTimer += dt;
            if (frameTimer > 0.2) { frameTimer = 0; frame = 1 - frame; }
        } else { frame = 0; }
    }

    // startTalk picks lines based on player context
    public void startTalk(double playerX, double playerY) {
        if (talking) return;

        int ptx = (int)(playerX / TILE), pty = (int)(playerY / TILE);
        TileType nearTile = world.get(ptx, pty);
        boolean nearWater    = nearTile == TileType.SHALLOW_WATER || nearTile == TileType.SAND;
        boolean nearMountain = nearTile == TileType.MOUNTAIN || nearTile == TileType.SNOW;

        // We don't have direct access to game state here, so we read the zone name
        // as a proxy — GamePanel can call the richer overload if needed
        String[] lines = switch (job) {
            case VILLAGER  -> villagerLines(false, false);
            case MERCHANT  -> merchantLines(false, false);
            case GUARD     -> guardLines(false, false);
            case ELDER     -> elderLines(false, false);
            case WANDERER  -> wandererLines(nearWater, nearMountain);
        };
        currentLine = lines[rng.nextInt(lines.length)];
        talking   = true;
        talkTimer = TALK_DURATION;
    }

    /** Richer context overload called from GamePanel with live game state. */
    public void startTalkContextual(double playerX, double playerY,
                                    int playerHp, int playerMaxHp,
                                    int playerLevel, boolean enemiesNear,
                                    boolean hasItems) {
        if (talking) return;
        boolean playerHurt    = playerHp < playerMaxHp * 0.5;
        boolean playerHighLvl = playerLevel >= 5;

        int ptx = (int)(playerX / TILE), pty = (int)(playerY / TILE);
        TileType t = world.get(ptx, pty);
        boolean nearWater    = t == TileType.SHALLOW_WATER || t == TileType.SAND;
        boolean nearMountain = t == TileType.MOUNTAIN || t == TileType.SNOW;

        String[] lines = switch (job) {
            case VILLAGER  -> villagerLines(playerHurt, enemiesNear);
            case MERCHANT  -> merchantLines(hasItems, playerHurt);
            case GUARD     -> guardLines(enemiesNear, playerLevel < 3);
            case ELDER     -> elderLines(playerHighLvl, ptx > 100 || pty > 80);
            case WANDERER  -> wandererLines(nearWater, nearMountain);
        };
        currentLine = lines[rng.nextInt(lines.length)];
        talking   = true;
        talkTimer = TALK_DURATION;
    }

    public boolean isNear(double px, double py, double r) {
        double dx=px-x, dy=py-y; return dx*dx+dy*dy<r*r;
    }

    // ── Draw ──────────────────────────────────────────────────────────────────

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX), sy = (int)(y - camY);
        if (sx<-40||sx>GamePanel.WIDTH+40||sy<-40||sy>GamePanel.HEIGHT+40) return;

        int bob = moving ? (int)(Math.sin(frame*Math.PI)*2) : 0;
        int ls  = moving ? (int)(Math.sin(frame*Math.PI)*3) : 0;

        // Shadow
        g.setColor(new Color(0,0,0,50)); g.fillOval(sx-9,sy+6,18,8);

        // Legs
        g.setColor(bodyColor.darker());
        g.fillRect(sx-5+ls, sy+7+bob, 4, 7);
        g.fillRect(sx+1-ls, sy+7+bob, 4, 7);

        // Body
        g.setColor(bodyColor); g.fillRect(sx-7, sy-10+bob, 14, 18);

        // Head
        g.setColor(skinColor); g.fillOval(sx-8, sy-26+bob, 16, 16);

        // Eyes
        g.setColor(new Color(0x2a1a0a));
        int[] ed = switch(dir){ case"up"->new int[]{0,-3}; case"left"->new int[]{-3,-1}; case"right"->new int[]{3,-1}; default->new int[]{0,1}; };
        g.fillOval(sx+ed[0]-4, sy-20+bob+ed[1], 3, 3);
        g.fillOval(sx+ed[0]+1, sy-20+bob+ed[1], 3, 3);

        // Accessories
        switch (job) {
            case MERCHANT -> { g.setColor(new Color(0x8b4513)); g.fillRect(sx-9,sy-30+bob,18,5); g.fillRect(sx-6,sy-35+bob,12,7); }
            case GUARD    -> { g.setColor(new Color(0x808090)); g.fillOval(sx-9,sy-30+bob,18,12); g.fillRect(sx-2,sy-20+bob,4,5); }
            case ELDER    -> { g.setColor(new Color(0x8b6914)); g.fillRect(sx+8,sy-28+bob,3,36); g.setColor(new Color(0xffd700)); g.fillOval(sx+6,sy-34+bob,7,7); }
            case WANDERER -> { g.setColor(new Color(0x6b4226)); g.fillRect(sx+5,sy-10+bob,8,12); }
            default -> {}
        }

        // Name label
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 9));
        FontMetrics fm = g.getFontMetrics();
        int lw = fm.stringWidth(name);
        g.setColor(new Color(0,0,0,120)); g.fillRoundRect(sx-lw/2-2,sy-40+bob,lw+4,12,4,4);
        g.setColor(new Color(0xffeebb));  g.drawString(name, sx-lw/2, sy-30+bob);

        if (talking && currentLine != null) drawSpeechBubble(g, sx, sy+bob);
    }

    private void drawSpeechBubble(Graphics2D g, int sx, int sy) {
        // Word-wrap to ~28 chars
        String[] words = currentLine.split(" ");
        java.util.List<String> lines = new java.util.ArrayList<>();
        StringBuilder cur = new StringBuilder();
        for (String w : words) {
            if (cur.length() + w.length() > 26) { lines.add(cur.toString().trim()); cur = new StringBuilder(); }
            cur.append(w).append(" ");
        }
        if (!cur.isEmpty()) lines.add(cur.toString().trim());

        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 10));
        FontMetrics fm = g.getFontMetrics();
        int maxW = lines.stream().mapToInt(fm::stringWidth).max().orElse(60);
        int bw = maxW + 12, bh = lines.size() * 13 + 6;
        int bx = Math.max(2, Math.min(sx - bw/2, GamePanel.WIDTH - bw - 2));
        int by = Math.max(2, sy - 50 - bh);

        g.setColor(new Color(255,255,230,225)); g.fillRoundRect(bx,by,bw,bh,6,6);
        g.setColor(new Color(80,60,20));        g.drawRoundRect(bx,by,bw,bh,6,6);

        // Bubble tail
        g.setColor(new Color(255,255,230,225));
        g.fillPolygon(new int[]{sx-4,sx+4,sx}, new int[]{by+bh,by+bh,sy-38}, 3);
        g.setColor(new Color(80,60,20));
        g.drawLine(sx-4,by+bh,sx,sy-38); g.drawLine(sx+4,by+bh,sx,sy-38);

        g.setColor(new Color(0x2a1a0a));
        for (int i = 0; i < lines.size(); i++)
            g.drawString(lines.get(i), bx+6, by+14+i*13);
    }
}
