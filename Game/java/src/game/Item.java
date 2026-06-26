package game;

import java.awt.*;

public class Item {

    public enum Type {
        // Melee weapons
        SWORD   ("Iron Sword",    Category.MELEE,  20, 0,   0, new Color(0xc0c0c0), "ATK +20"),
        AXE     ("Battle Axe",   Category.MELEE,  30, 0,   0, new Color(0x808080), "ATK +30"),
        DAGGER  ("Dagger",       Category.MELEE,  12, 0,   0, new Color(0xd0d0ff), "ATK +12, fast"),
        // Ranged
        BOW     ("Shortbow",     Category.RANGED, 15, 6,   0, new Color(0x8b6914), "ATK +15 ranged"),
        PISTOL  ("Pistol",       Category.RANGED, 25, 8,   0, new Color(0x505050), "ATK +25 ranged"),
        RIFLE   ("Rifle",        Category.RANGED, 40, 12,  0, new Color(0x303030), "ATK +40 ranged"),
        // Food / healing
        APPLE   ("Apple",        Category.FOOD,    0, 0,  15, new Color(0xdd2222), "HP +15"),
        BREAD   ("Bread",        Category.FOOD,    0, 0,  25, new Color(0xd4a060), "HP +25"),
        POTION  ("Health Potion",Category.FOOD,    0, 0,  50, new Color(0xff44aa), "HP +50"),
        // Armour
        SHIELD  ("Wooden Shield",Category.ARMOUR, 0,  0,   0, new Color(0x8b5e3c), "DEF +10"),
        HELMET  ("Iron Helmet",  Category.ARMOUR, 0,  0,   0, new Color(0xa0a0b0), "DEF +8");

        public enum Category { MELEE, RANGED, FOOD, ARMOUR }

        public final String  label;
        public final Category category;
        public final int     attack;
        public final int     range;   // tiles (0 = melee)
        public final int     heal;
        public final Color   color;
        public final String  stat;

        Type(String label, Category cat, int atk, int range, int heal, Color color, String stat) {
            this.label = label; this.category = cat; this.attack = atk;
            this.range = range; this.heal = heal; this.color = color; this.stat = stat;
        }
    }

    public final Type   type;
    public double x, y;      // world-pixel centre
    public boolean collected = false;

    // Bobbing animation
    private double bobTime;

    public Item(Type type, double x, double y) {
        this.type = type; this.x = x; this.y = y;
        this.bobTime = Math.random() * Math.PI * 2;
    }

    public void update(double dt) { bobTime += dt * 2.5; }

    public boolean isNear(double px, double py) {
        double dx = px - x, dy = py - y;
        return dx * dx + dy * dy < (22 * 22);
    }

    public void draw(Graphics2D g, double camX, double camY) {
        int sx = (int)(x - camX);
        int sy = (int)(y - camY + Math.sin(bobTime) * 3);

        // Drop shadow
        g.setColor(new Color(0, 0, 0, 60));
        g.fillOval(sx - 10, (int)(y - camY) + 8, 20, 7);

        // Glow ring
        g.setColor(new Color(type.color.getRed(), type.color.getGreen(), type.color.getBlue(), 60));
        g.fillOval(sx - 14, sy - 14, 28, 28);

        // Icon background
        g.setColor(new Color(30, 20, 10, 200));
        g.fillRoundRect(sx - 10, sy - 10, 20, 20, 5, 5);
        g.setColor(type.color);
        g.drawRoundRect(sx - 10, sy - 10, 20, 20, 5, 5);

        // Icon shape
        drawIcon(g, sx, sy);

        // Label
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 8));
        FontMetrics fm = g.getFontMetrics();
        int lw = fm.stringWidth(type.label);
        g.setColor(new Color(0, 0, 0, 140));
        g.fillRoundRect(sx - lw/2 - 2, sy + 11, lw + 4, 11, 3, 3);
        g.setColor(Color.WHITE);
        g.drawString(type.label, sx - lw/2, sy + 20);
    }

    private void drawIcon(Graphics2D g, int sx, int sy) {
        g.setColor(type.color);
        switch (type.category) {
            case MELEE -> {
                // Sword diagonal
                g.setStroke(new BasicStroke(2.5f));
                g.drawLine(sx - 6, sy + 6, sx + 6, sy - 6);
                g.setStroke(new BasicStroke(1.5f));
                g.drawLine(sx - 3, sy + 3, sx - 6, sy + 6); // handle
            }
            case RANGED -> {
                if (type == Type.BOW) {
                    g.setStroke(new BasicStroke(2f));
                    g.drawArc(sx - 6, sy - 7, 8, 14, -90, 180);
                    g.drawLine(sx - 6, sy - 7, sx - 6, sy + 7);
                } else {
                    // Gun barrel
                    g.setStroke(new BasicStroke(3f));
                    g.drawLine(sx - 6, sy, sx + 7, sy);
                    g.setStroke(new BasicStroke(2f));
                    g.drawLine(sx - 2, sy, sx - 2, sy + 5);
                }
                g.setStroke(new BasicStroke(1f));
            }
            case FOOD -> {
                // Circle with cross
                g.fillOval(sx - 6, sy - 6, 12, 12);
                g.setColor(Color.WHITE);
                g.setStroke(new BasicStroke(1.5f));
                g.drawLine(sx, sy - 4, sx, sy + 4);
                g.drawLine(sx - 4, sy, sx + 4, sy);
                g.setStroke(new BasicStroke(1f));
            }
            case ARMOUR -> {
                // Shield shape
                int[] xs = {sx-5, sx+5, sx+5, sx,   sx-5};
                int[] ys = {sy-6, sy-6, sy+1, sy+7, sy+1};
                g.fillPolygon(xs, ys, 5);
                g.setColor(type.color.brighter());
                g.drawPolygon(xs, ys, 5);
            }
        }
        g.setStroke(new BasicStroke(1f));
    }
}
