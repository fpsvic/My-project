package game;

import java.awt.*;
import java.util.Set;

public class Player {

    public double x, y;
    public final double speed = 130;
    public String dir = "down";
    public int    frame = 0;
    public double frameTimer = 0;
    public boolean moving = false;

    private static final int TILE = GamePanel.TILE;
    private final WorldGen world;

    public Player(WorldGen world) {
        this.world = world;
        // Start on a walkable tile near the origin
        x = 5 * TILE + TILE / 2.0;
        y = 5 * TILE + TILE / 2.0;
    }

    public void update(double dt, Set<Integer> keys) {
        double dx = 0, dy = 0;
        if (keys.contains(java.awt.event.KeyEvent.VK_UP)    || keys.contains(java.awt.event.KeyEvent.VK_W)) dy -= 1;
        if (keys.contains(java.awt.event.KeyEvent.VK_DOWN)  || keys.contains(java.awt.event.KeyEvent.VK_S)) dy += 1;
        if (keys.contains(java.awt.event.KeyEvent.VK_LEFT)  || keys.contains(java.awt.event.KeyEvent.VK_A)) dx -= 1;
        if (keys.contains(java.awt.event.KeyEvent.VK_RIGHT) || keys.contains(java.awt.event.KeyEvent.VK_D)) dx += 1;

        if (dx != 0 && dy != 0) { dx *= 0.707; dy *= 0.707; }
        moving = (dx != 0 || dy != 0);

        if      (dx > 0) dir = "right";
        else if (dx < 0) dir = "left";
        else if (dy < 0) dir = "up";
        else if (dy > 0) dir = "down";

        if (moving) {
            frameTimer += dt;
            if (frameTimer > 0.12) { frameTimer = 0; frame = 1 - frame; }
        } else {
            frame = 0; frameTimer = 0;
        }

        double nx = x + dx * speed * dt;
        double ny = y + dy * speed * dt;
        final int R = 10;
        if (walkable(nx-R,y) && walkable(nx+R,y) && walkable(nx,y-R) && walkable(nx,y+R)) x = nx;
        if (walkable(x-R,ny) && walkable(x+R,ny) && walkable(x,ny-R) && walkable(x,ny+R)) y = ny;
    }

    private boolean walkable(double px, double py) {
        return world.get((int)(px/TILE), (int)(py/TILE)).walkable;
    }

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX);
        int sy = (int)(y - camY);
        int bob = moving ? (int)(Math.sin(frame * Math.PI) * 2) : 0;
        int legSwing = moving ? (int)(Math.sin(frame * Math.PI) * 4) : 0;

        // Shadow
        g.setColor(new Color(0, 0, 0, 60));
        g.fillOval(sx - 10, sy + 5, 20, 10);

        // Legs
        g.setColor(new Color(0x2a3a8a));
        g.fillRect(sx - 6 + legSwing, sy + 8 + bob, 5, 8);
        g.fillRect(sx + 1 - legSwing, sy + 8 + bob, 5, 8);

        // Body
        g.setColor(new Color(0x3a5fcd));
        g.fillRect(sx - 8, sy - 12 + bob, 16, 20);

        // Sword
        g.setColor(Color.LIGHT_GRAY);
        switch (dir) {
            case "right" -> g.fillRect(sx + 8,  sy - 8 + bob, 14, 3);
            case "left"  -> g.fillRect(sx - 22, sy - 8 + bob, 14, 3);
            case "up"    -> g.fillRect(sx + 6,  sy - 26 + bob, 3, 14);
            default      -> g.fillRect(sx + 6,  sy - 8 + bob, 3, 14);
        }
        g.setColor(new Color(0xc8a020));
        switch (dir) {
            case "right" -> g.fillRect(sx + 6,  sy - 10 + bob, 4, 7);
            case "left"  -> g.fillRect(sx - 10, sy - 10 + bob, 4, 7);
            case "up"    -> g.fillRect(sx + 4,  sy - 14 + bob, 7, 4);
            default      -> g.fillRect(sx + 4,  sy - 12 + bob, 7, 4);
        }

        // Head
        g.setColor(new Color(0xf4c87a));
        g.fillOval(sx - 9, sy - 27 + bob, 18, 18);

        // Eyes
        g.setColor(new Color(0x2a1a0a));
        int[] ed = switch (dir) {
            case "up"    -> new int[]{0, -3};
            case "left"  -> new int[]{-3, -1};
            case "right" -> new int[]{3, -1};
            default      -> new int[]{0, 1};
        };
        g.fillOval(sx + ed[0] - 5, sy - 22 + bob + ed[1], 4, 4);
        g.fillOval(sx + ed[0] + 1, sy - 22 + bob + ed[1], 4, 4);

        // "YOU" label
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 9));
        g.setColor(new Color(0xffd700));
        g.drawString("YOU", sx - 9, sy - 32 + bob);
    }
}
