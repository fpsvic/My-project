package game;

import java.awt.*;

public class Projectile {

    public double x, y;
    public final double vx, vy;
    public final boolean fromPlayer;
    public final int damage;
    public boolean dead = false;
    private double life;

    private static final Color PLAYER_COLOR = new Color(0xffee44);
    private static final Color ENEMY_COLOR  = new Color(0xff4422);

    public Projectile(double x, double y, double vx, double vy, boolean fromPlayer, int damage, double maxLife) {
        this.x = x; this.y = y;
        this.vx = vx; this.vy = vy;
        this.fromPlayer = fromPlayer;
        this.damage = damage;
        this.life = maxLife;
    }

    public void update(double dt, WorldGen world) {
        x += vx * dt;
        y += vy * dt;
        life -= dt;
        int tx = (int)(x / GamePanel.TILE);
        int ty = (int)(y / GamePanel.TILE);
        if (!world.get(tx, ty).walkable || life <= 0) dead = true;
    }

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX);
        int sy = (int)(y - camY);
        Color c = fromPlayer ? PLAYER_COLOR : ENEMY_COLOR;
        g.setColor(new Color(c.getRed(), c.getGreen(), c.getBlue(), 180));
        g.fillOval(sx - 4, sy - 4, 8, 8);
        g.setColor(c);
        g.fillOval(sx - 2, sy - 2, 5, 5);
    }
}
