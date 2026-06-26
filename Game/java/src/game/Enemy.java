package game;

import java.awt.*;
import java.util.List;

public class Enemy {

    public enum Kind {
        SLIME  ("Slime",   new Color(0x44bb44), 30,  8, 40,  1.5f, 0,  false, 0),
        ORC    ("Orc",     new Color(0x228822), 60, 14, 55,  2.0f, 0,  false, 0),
        SKELETON("Skel",   new Color(0xd0d0b8), 40, 10, 50,  1.8f, 0,  false, 0),
        ARCHER ("Archer",  new Color(0x885522), 45, 12, 60,  1.6f, 5,  true,  220),
        MAGE   ("Mage",    new Color(0x884488), 35, 18, 70,  1.4f, 7,  true,  300),
        TROLL  ("Troll",   new Color(0x446622), 120,22, 80,  1.2f, 0,  false, 0);

        public final String name;
        public final Color  color;
        public final int    maxHp, damage, xpDrop;
        public final float  speed;
        public final int    attackRange; // tiles (0 = melee)
        public final boolean ranged;
        public final double projectileSpeed;

        Kind(String n, Color c, int hp, int dmg, int xp, float spd, int range, boolean ranged, double pspd) {
            name = n; color = c; maxHp = hp; damage = dmg; xpDrop = xp;
            speed = spd; attackRange = range; this.ranged = ranged; projectileSpeed = pspd;
        }
    }

    public final Kind kind;
    public double x, y;
    public int    hp;
    public boolean dead = false;

    private static final int   TILE         = GamePanel.TILE;
    private static final double AGGRO_RANGE  = 200.0;
    private static final double MELEE_RANGE  = 30.0;

    private String  dir = "down";
    private int     frame;
    private double  frameTimer;
    private boolean moving;

    private double attackTimer  = 0;
    private double attackCooldown;

    // Flash red on hit
    private double hitFlash = 0;

    private final WorldGen world;

    public Enemy(Kind kind, double x, double y, WorldGen world) {
        this.kind = kind; this.x = x; this.y = y; this.hp = kind.maxHp;
        this.world = world;
        this.attackCooldown = kind.ranged ? 1.8 : 1.2;
    }

    public void update(double dt, double px, double py, List<Projectile> projectiles) {
        if (dead) return;
        if (hitFlash > 0) hitFlash -= dt;

        double dx = px - x, dy = py - y;
        double dist = Math.sqrt(dx * dx + dy * dy);
        attackTimer -= dt;

        if (dist < AGGRO_RANGE) {
            // Move toward player (unless ranged and already in range)
            boolean shouldMove = dist > (kind.ranged ? kind.attackRange * TILE * 0.8 : MELEE_RANGE);
            if (shouldMove) {
                double speed = kind.speed * TILE * dt;
                double nx = x + (dx / dist) * speed;
                double ny = y + (dy / dist) * speed;
                if (world.get((int)(nx/TILE),(int)(y/TILE)).walkable)  x = nx;
                if (world.get((int)(x/TILE),(int)(ny/TILE)).walkable) y = ny;
                if      (Math.abs(dx) > Math.abs(dy)) dir = dx > 0 ? "right" : "left";
                else                                   dir = dy > 0 ? "down"  : "up";
                moving = true;
            } else {
                moving = false;
            }

            // Attack
            if (attackTimer <= 0) {
                if (kind.ranged && dist < kind.attackRange * TILE) {
                    double speed2 = kind.projectileSpeed;
                    double len = Math.sqrt(dx*dx+dy*dy);
                    projectiles.add(new Projectile(x, y, dx/len*speed2, dy/len*speed2, false, kind.damage, 2.5));
                    attackTimer = attackCooldown;
                } else if (!kind.ranged && dist < MELEE_RANGE) {
                    // Melee dealt in Player.update via overlap check
                    attackTimer = attackCooldown;
                }
            }
        } else {
            moving = false;
        }

        if (moving) {
            frameTimer += dt;
            if (frameTimer > 0.18) { frameTimer = 0; frame = 1 - frame; }
        } else {
            frame = 0; frameTimer = 0;
        }
    }

    /** Returns damage dealt to player if in melee range and cooldown ready (called externally). */
    public int tryMeleeDamage(double px, double py) {
        if (kind.ranged || dead) return 0;
        double dx = px - x, dy = py - y;
        if (dx*dx + dy*dy < MELEE_RANGE * MELEE_RANGE && attackTimer <= 0) {
            attackTimer = attackCooldown;
            return kind.damage;
        }
        return 0;
    }

    public void takeDamage(int dmg) {
        hp -= dmg;
        hitFlash = 0.15;
        if (hp <= 0) dead = true;
    }

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX);
        int sy = (int)(y - camY);

        if (sx < -40 || sx > GamePanel.WIDTH + 40 || sy < -40 || sy > GamePanel.HEIGHT + 40) return;

        int bob = moving ? (int)(Math.sin(frame * Math.PI) * 2) : 0;
        int legSwing = moving ? (int)(Math.sin(frame * Math.PI) * 3) : 0;

        Color bodyCol = hitFlash > 0 ? Color.WHITE : kind.color;

        // Shadow
        g.setColor(new Color(0,0,0,50));
        g.fillOval(sx-10, sy+6, 20, 8);

        switch (kind) {
            case SLIME -> drawSlime(g, sx, sy, bodyCol, bob);
            case SKELETON -> drawSkeleton(g, sx, sy, bodyCol, bob, legSwing);
            default -> drawHumanoid(g, sx, sy, bodyCol, bob, legSwing);
        }

        // Health bar
        drawHealthBar(g, sx, sy);
        // Name
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 9));
        FontMetrics fm = g.getFontMetrics();
        int nw = fm.stringWidth(kind.name);
        g.setColor(new Color(0,0,0,120));
        g.fillRect(sx - nw/2 - 1, sy - 42, nw + 2, 10);
        g.setColor(new Color(0xff8888));
        g.drawString(kind.name, sx - nw/2, sy - 33);
    }

    private void drawSlime(Graphics2D g, int sx, int sy, Color col, int bob) {
        g.setColor(col);
        g.fillOval(sx - 12, sy - 8 + bob, 24, 16);
        g.setColor(col.darker());
        g.drawOval(sx - 12, sy - 8 + bob, 24, 16);
        g.setColor(new Color(0,0,0,160));
        g.fillOval(sx - 5, sy - 4 + bob, 4, 4);
        g.fillOval(sx + 1, sy - 4 + bob, 4, 4);
    }

    private void drawSkeleton(Graphics2D g, int sx, int sy, Color col, int bob, int legSwing) {
        g.setColor(col);
        // Legs
        g.drawLine(sx - 3, sy + 8 + bob, sx - 3 + legSwing, sy + 16 + bob);
        g.drawLine(sx + 3, sy + 8 + bob, sx + 3 - legSwing, sy + 16 + bob);
        // Ribcage
        g.drawRect(sx - 6, sy - 8 + bob, 12, 16);
        for (int r = 0; r < 3; r++) g.drawLine(sx - 6, sy - 4 + r*4 + bob, sx + 6, sy - 4 + r*4 + bob);
        // Arms
        g.drawLine(sx - 6, sy - 6 + bob, sx - 10, sy + 2 + bob);
        g.drawLine(sx + 6, sy - 6 + bob, sx + 10, sy + 2 + bob);
        // Skull
        g.fillOval(sx - 7, sy - 22 + bob, 14, 14);
        g.setColor(new Color(0x1a1a2a));
        g.fillOval(sx - 5, sy - 18 + bob, 3, 3);
        g.fillOval(sx + 2, sy - 18 + bob, 3, 3);
    }

    private void drawHumanoid(Graphics2D g, int sx, int sy, Color col, int bob, int legSwing) {
        // Legs
        g.setColor(col.darker());
        g.fillRect(sx - 5 + legSwing, sy + 7 + bob, 4, 8);
        g.fillRect(sx + 1 - legSwing, sy + 7 + bob, 4, 8);
        // Body
        g.setColor(col);
        g.fillRect(sx - 7, sy - 10 + bob, 14, 18);
        // Head
        g.fillOval(sx - 8, sy - 24 + bob, 16, 16);
        // Eyes (red/glowing)
        g.setColor(new Color(0xff2200));
        g.fillOval(sx - 4, sy - 19 + bob, 3, 3);
        g.fillOval(sx + 1, sy - 19 + bob, 3, 3);
        // Weapon
        g.setColor(new Color(0x808080));
        if (kind == Kind.ARCHER || kind == Kind.MAGE) {
            g.setColor(kind == Kind.MAGE ? new Color(0xcc44ff) : new Color(0x8b6914));
            g.fillRect(sx + 8, sy - 12 + bob, 3, 20);
        } else {
            g.fillRect(sx + 8, sy - 6 + bob, 14, 3);
        }
    }

    private void drawHealthBar(Graphics2D g, int sx, int sy) {
        int bw = 28, bh = 4;
        int bx = sx - bw/2, by = sy - 30;
        g.setColor(new Color(0,0,0,150));
        g.fillRect(bx-1, by-1, bw+2, bh+2);
        g.setColor(new Color(0x660000));
        g.fillRect(bx, by, bw, bh);
        float pct = (float)hp / kind.maxHp;
        g.setColor(pct > 0.5f ? new Color(0x44cc44) : pct > 0.25f ? new Color(0xeeaa00) : new Color(0xee2222));
        g.fillRect(bx, by, (int)(bw * pct), bh);
    }
}
