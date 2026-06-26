package game;

import java.awt.*;
import java.util.Random;

public class NPC {

    public enum Profession {
        VILLAGER (new Color(0x4a8f3f), new Color(0xf4c87a), "Lovely weather today!",          "Stay safe out there.",       "Have you seen the old ruins?"),
        MERCHANT (new Color(0xc8a020), new Color(0xf0d090), "Buy somethin', will ya?",         "Best prices in the realm!",  "I've traveled many roads."),
        GUARD    (new Color(0x505090), new Color(0xd0d0d0), "Move along, citizen.",             "Keep the peace.",            "I've been posted here for years."),
        ELDER    (new Color(0x806050), new Color(0xe8d8b8), "The old ways are best.",          "Wisdom takes patience.",     "I remember when this was all farmland."),
        WANDERER (new Color(0x508050), new Color(0xd0e8c0), "The horizon calls to me.",        "Many roads, one path.",      "I come from lands far to the east.");

        final Color bodyColor, skinColor;
        final String[] lines;
        Profession(Color body, Color skin, String... lines) {
            this.bodyColor = body; this.skinColor = skin; this.lines = lines;
        }
    }

    private static final String[] NAMES = {
        "Aldric","Benna","Cort","Dwyn","Elara","Fenn","Gara","Holt",
        "Iria","Joren","Kael","Lira","Mord","Nyla","Orin","Pyra"
    };

    public final String name;
    public final Profession job;

    // World-pixel position
    public double x, y;

    // Wander state
    private double targetX, targetY;
    private double idleTimer;
    private boolean moving;
    private String dir = "down";
    private int frame;
    private double frameTimer;
    private final double speed;

    // Dialogue
    public boolean talking;
    public String currentLine;
    private double talkTimer;
    private static final double TALK_DURATION = 3.5;

    private final WorldGen world;
    private final int TILE = GamePanel.TILE;
    private final Random rng;

    public NPC(double x, double y, Profession job, long seed, WorldGen world) {
        this.x = x; this.y = y;
        this.targetX = x; this.targetY = y;
        this.job = job;
        this.world = world;
        this.rng = new Random(seed);
        this.name = NAMES[(int)(seed % NAMES.length)];
        this.speed = 30 + rng.nextDouble() * 20;
        this.idleTimer = rng.nextDouble() * 3;
    }

    public void update(double dt) {
        if (talking) {
            talkTimer -= dt;
            if (talkTimer <= 0) { talking = false; currentLine = null; }
            return;
        }

        if (!moving) {
            idleTimer -= dt;
            if (idleTimer <= 0) {
                // Pick a new wander destination within ~3 tiles
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
            double dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 2) {
                moving = false;
            } else {
                double nx = x + (dx / dist) * speed * dt;
                double ny = y + (dy / dist) * speed * dt;
                if (walkable(nx, y)) x = nx;
                if (walkable(x, ny)) y = ny;
                if      (Math.abs(dx) > Math.abs(dy)) dir = dx > 0 ? "right" : "left";
                else                                   dir = dy > 0 ? "down"  : "up";
            }

            frameTimer += dt;
            if (frameTimer > 0.2) { frameTimer = 0; frame = 1 - frame; }
        } else {
            frame = 0;
        }
    }

    public void startTalk() {
        if (talking) return;
        talking = true;
        currentLine = job.lines[rng.nextInt(job.lines.length)];
        talkTimer = TALK_DURATION;
    }

    public boolean isNear(double px, double py, double radius) {
        double dx = px - x, dy = py - y;
        return dx * dx + dy * dy < radius * radius;
    }

    private boolean walkable(double px, double py) {
        int tx = (int)(px / TILE), ty = (int)(py / TILE);
        return world.get(tx, ty).walkable;
    }

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX);
        int sy = (int)(y - camY);

        // Clip to visible area
        if (sx < -40 || sx > GamePanel.WIDTH + 40 || sy < -40 || sy > GamePanel.HEIGHT + 40) return;

        int bob = moving ? (int)(Math.sin(frame * Math.PI) * 2) : 0;
        int legSwing = moving ? (int)(Math.sin(frame * Math.PI) * 3) : 0;

        // Shadow
        g.setColor(new Color(0, 0, 0, 50));
        g.fillOval(sx - 9, sy + 6, 18, 8);

        // Legs
        g.setColor(job.bodyColor.darker());
        g.fillRect(sx - 5 + legSwing,  sy + 7 + bob, 4, 7);
        g.fillRect(sx + 1 - legSwing,  sy + 7 + bob, 4, 7);

        // Body
        g.setColor(job.bodyColor);
        g.fillRect(sx - 7, sy - 10 + bob, 14, 18);

        // Head
        g.setColor(job.skinColor);
        g.fillOval(sx - 8, sy - 26 + bob, 16, 16);

        // Eyes
        g.setColor(new Color(0x2a1a0a));
        int[] ed = switch (dir) {
            case "up"    -> new int[]{0, -3};
            case "left"  -> new int[]{-3, -1};
            case "right" -> new int[]{3, -1};
            default      -> new int[]{0, 1};
        };
        g.fillOval(sx + ed[0] - 4, sy - 20 + bob + ed[1], 3, 3);
        g.fillOval(sx + ed[0] + 1, sy - 20 + bob + ed[1], 3, 3);

        // Job-specific accessory
        switch (job) {
            case MERCHANT -> {
                // Hat
                g.setColor(new Color(0x8b4513));
                g.fillRect(sx - 9, sy - 30 + bob, 18, 5);
                g.fillRect(sx - 6, sy - 35 + bob, 12, 7);
            }
            case GUARD -> {
                // Helmet
                g.setColor(new Color(0x808090));
                g.fillOval(sx - 9, sy - 30 + bob, 18, 12);
                g.fillRect(sx - 2, sy - 20 + bob, 4, 5); // nose guard
            }
            case ELDER -> {
                // Staff
                g.setColor(new Color(0x8b6914));
                g.fillRect(sx + 8, sy - 28 + bob, 3, 36);
                g.setColor(new Color(0xffd700));
                g.fillOval(sx + 6, sy - 34 + bob, 7, 7);
            }
            case WANDERER -> {
                // Backpack
                g.setColor(new Color(0x6b4226));
                g.fillRect(sx + 5, sy - 10 + bob, 8, 12);
            }
            default -> {} // VILLAGER: no extra
        }

        // Name label
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 9));
        FontMetrics fm = g.getFontMetrics();
        String label = name;
        int lw = fm.stringWidth(label);
        g.setColor(new Color(0, 0, 0, 120));
        g.fillRoundRect(sx - lw / 2 - 2, sy - 40 + bob, lw + 4, 12, 4, 4);
        g.setColor(new Color(0xffeebb));
        g.drawString(label, sx - lw / 2, sy - 30 + bob);

        // Speech bubble
        if (talking && currentLine != null) drawSpeechBubble(g, sx, sy + bob);
    }

    private void drawSpeechBubble(Graphics2D g, int sx, int sy) {
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 10));
        FontMetrics fm = g.getFontMetrics();
        int tw = fm.stringWidth(currentLine);
        int bw = tw + 10, bh = 18;
        int bx = sx - bw / 2, by = sy - 65;

        // Clamp to screen
        bx = Math.max(2, Math.min(bx, GamePanel.WIDTH - bw - 2));
        by = Math.max(2, by);

        g.setColor(new Color(255, 255, 230, 220));
        g.fillRoundRect(bx, by, bw, bh, 6, 6);
        g.setColor(new Color(80, 60, 20));
        g.drawRoundRect(bx, by, bw, bh, 6, 6);

        // Tail
        int tx = sx, ty2 = sy - 42;
        g.setColor(new Color(255, 255, 230, 220));
        int[] xs = {tx - 4, tx + 4, tx};
        int[] ys = {by + bh, by + bh, ty2};
        g.fillPolygon(xs, ys, 3);
        g.setColor(new Color(80, 60, 20));
        g.drawLine(tx - 4, by + bh, tx, ty2);
        g.drawLine(tx + 4, by + bh, tx, ty2);

        g.setColor(new Color(0x2a1a0a));
        g.drawString(currentLine, bx + 5, by + 13);
    }
}
