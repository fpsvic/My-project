package game;

import java.awt.*;
import java.util.*;
import java.util.List;

public class Player {

    public static final int MAX_HP     = 100;
    public static final int MAX_INV    = 8;

    public double x, y;
    public int    hp         = MAX_HP;
    public int    attack     = 10;   // base melee damage
    public int    defence    = 0;
    public int    xp         = 0;
    public int    level      = 1;
    public boolean dead      = false;

    // Equipped weapon slot (null = fists)
    public Item equippedWeapon = null;

    // Inventory
    public final List<Item> inventory = new ArrayList<>();

    // State
    public String  dir = "down";
    public int     frame;
    public double  frameTimer;
    public boolean moving;

    // Combat
    private double attackCooldown  = 0;
    private double attackCooldownMax = 0.5;
    private double iFrames         = 0; // invincibility after being hit

    // Flash
    private double hitFlash = 0;

    public final double speed = 130;
    private static final int TILE = GamePanel.TILE;
    private final WorldGen world;

    public Player(WorldGen world) {
        this.world = world;
        // Find a spawn tile (center of map, walkable)
        x = 78 * TILE + TILE / 2.0;
        y = 35 * TILE + TILE / 2.0;
    }

    public void update(double dt, Set<Integer> keys, List<Projectile> projectiles, List<Enemy> enemies) {
        if (dead) return;

        if (iFrames  > 0) iFrames  -= dt;
        if (hitFlash > 0) hitFlash -= dt;
        if (attackCooldown > 0) attackCooldown -= dt;

        // Movement
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
        } else { frame = 0; frameTimer = 0; }

        double nx = x + dx * speed * dt;
        double ny = y + dy * speed * dt;
        final int R = 10;
        if (walkable(nx-R,y) && walkable(nx+R,y) && walkable(nx,y-R) && walkable(nx,y+R)) x = nx;
        if (walkable(x-R,ny) && walkable(x+R,ny) && walkable(x,ny-R) && walkable(x,ny+R)) y = ny;

        // Take melee damage from enemies
        if (iFrames <= 0) {
            for (Enemy e : enemies) {
                int dmg = e.tryMeleeDamage(x, y);
                if (dmg > 0) { takeDamage(Math.max(1, dmg - defence)); break; }
            }
        }

        // Take projectile damage
        for (Projectile p : projectiles) {
            if (!p.fromPlayer && !p.dead) {
                double pdx = p.x - x, pdy = p.y - y;
                if (pdx*pdx + pdy*pdy < 20*20 && iFrames <= 0) {
                    p.dead = true;
                    takeDamage(Math.max(1, p.damage - defence));
                }
            }
        }
    }

    public void attack(List<Enemy> enemies, List<Projectile> projectiles) {
        if (attackCooldown > 0 || dead) return;
        attackCooldown = attackCooldownMax;

        Item w = equippedWeapon;
        int dmg = attack + (w != null ? w.type.attack : 0);

        if (w != null && w.type.category == Item.Type.Category.RANGED) {
            // Fire projectile in facing direction
            double[] vel = dirVec();
            double spd = w.type.range * 40 + 200;
            projectiles.add(new Projectile(x, y, vel[0]*spd, vel[1]*spd, true, dmg, 1.8));
        } else {
            // Melee: hit enemies in a short arc in front
            double[] vel = dirVec();
            double reach = 40;
            for (Enemy e : enemies) {
                double ex = e.x - x, ey = e.y - y;
                double dot = ex * vel[0] + ey * vel[1];
                double dist = Math.sqrt(ex*ex + ey*ey);
                if (!e.dead && dist < reach && dot > 0)
                    e.takeDamage(dmg);
            }
        }
    }

    public void pickupItem(Item item) {
        if (item.collected || inventory.size() >= MAX_INV) return;
        item.collected = true;
        inventory.add(item);
        // Auto-use food
        if (item.type.category == Item.Type.Category.FOOD) {
            hp = Math.min(MAX_HP, hp + item.type.heal);
            inventory.remove(item);
        }
    }

    public void equipItem(int slot) {
        if (slot < 0 || slot >= inventory.size()) return;
        Item it = inventory.get(slot);
        if (it.type.category == Item.Type.Category.MELEE || it.type.category == Item.Type.Category.RANGED) {
            equippedWeapon = it;
        } else if (it.type.category == Item.Type.Category.ARMOUR) {
            defence += 8;
            inventory.remove(it);
        }
    }

    private void takeDamage(int dmg) {
        hp -= dmg;
        hitFlash = 0.12;
        iFrames = 0.5;
        if (hp <= 0) { hp = 0; dead = true; }
    }

    public void gainXP(int amount) {
        xp += amount;
        if (xp >= level * 100) {
            xp -= level * 100;
            level++;
            attack  += 4;
            defence += 2;
            hp = Math.min(MAX_HP + (level - 1) * 10, hp + 20);
        }
    }

    private boolean walkable(double px, double py) {
        return world.get((int)(px/TILE), (int)(py/TILE)).walkable;
    }

    private double[] dirVec() {
        return switch (dir) {
            case "up"    -> new double[]{0, -1};
            case "down"  -> new double[]{0,  1};
            case "left"  -> new double[]{-1, 0};
            default      -> new double[]{ 1, 0};
        };
    }

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX);
        int sy = (int)(y - camY);
        Color bodyCol = hitFlash > 0 ? Color.WHITE : new Color(0x3a5fcd);
        int bob = moving ? (int)(Math.sin(frame * Math.PI) * 2) : 0;
        int legSwing = moving ? (int)(Math.sin(frame * Math.PI) * 4) : 0;

        // Shadow
        g.setColor(new Color(0,0,0,60));
        g.fillOval(sx-10, sy+5, 20, 10);

        // Legs
        g.setColor(new Color(0x2a3a8a));
        g.fillRect(sx-6+legSwing, sy+8+bob, 5, 8);
        g.fillRect(sx+1-legSwing, sy+8+bob, 5, 8);

        // Body
        g.setColor(bodyCol);
        g.fillRect(sx-8, sy-12+bob, 16, 20);

        // Equipped weapon visual
        drawWeapon(g, sx, sy, bob);

        // Head
        g.setColor(new Color(0xf4c87a));
        g.fillOval(sx-9, sy-27+bob, 18, 18);

        // Eyes
        g.setColor(new Color(0x2a1a0a));
        int[] ed = switch (dir) {
            case "up"    -> new int[]{0,-3};
            case "left"  -> new int[]{-3,-1};
            case "right" -> new int[]{3,-1};
            default      -> new int[]{0,1};
        };
        g.fillOval(sx+ed[0]-5, sy-22+bob+ed[1], 4, 4);
        g.fillOval(sx+ed[0]+1, sy-22+bob+ed[1], 4, 4);
    }

    private void drawWeapon(Graphics2D g, int sx, int sy, int bob) {
        Color wc = equippedWeapon != null ? equippedWeapon.type.color : Color.LIGHT_GRAY;
        g.setColor(wc);
        switch (dir) {
            case "right" -> { g.fillRect(sx+8,  sy-8+bob, 16, 3);  g.setColor(new Color(0xc8a020)); g.fillRect(sx+6,  sy-10+bob, 4, 7); }
            case "left"  -> { g.fillRect(sx-24, sy-8+bob, 16, 3);  g.setColor(new Color(0xc8a020)); g.fillRect(sx-10, sy-10+bob, 4, 7); }
            case "up"    -> { g.fillRect(sx+6,  sy-28+bob, 3, 16); g.setColor(new Color(0xc8a020)); g.fillRect(sx+4,  sy-14+bob, 7, 4); }
            default      -> { g.fillRect(sx+6,  sy-8+bob, 3, 16);  g.setColor(new Color(0xc8a020)); g.fillRect(sx+4,  sy-10+bob, 7, 4); }
        }
    }
}
