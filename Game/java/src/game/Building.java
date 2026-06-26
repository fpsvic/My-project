package game;

import java.awt.*;

/** A rectangular building stamped onto the world. */
public class Building {

    public enum Type {
        INN      ("The Sleeping Ox Inn",   new Color(0xa05020), new Color(0xd4a060)),
        SHOP     ("General Store",          new Color(0x206080), new Color(0x60b0d0)),
        BLACKSMITH("Blacksmith",            new Color(0x404040), new Color(0x909090)),
        CHURCH   ("Chapel of the Light",   new Color(0xd0d0e8), new Color(0xf0f0ff)),
        HOUSE    ("Cottage",               new Color(0x805030), new Color(0xc09060));

        public final String label;
        public final Color roofColor;
        public final Color wallColor;
        Type(String label, Color roof, Color wall) {
            this.label = label; this.roofColor = roof; this.wallColor = wall;
        }
    }

    public final int x, y, w, h;
    public final Type type;

    // Interior layout: local coords (0,0) = top-left of building
    private final TileType[][] interior;

    public Building(int x, int y, int w, int h, Type type) {
        this.x = x; this.y = y; this.w = w; this.h = h; this.type = type;
        interior = buildInterior();
    }

    public TileType tileAt(int tx, int ty) {
        int lx = tx - x, ly = ty - y;
        if (lx < 0 || lx >= w || ly < 0 || ly >= h) return null;
        return interior[ly][lx];
    }

    private TileType[][] buildInterior() {
        TileType[][] t = new TileType[h][w];
        for (int ly = 0; ly < h; ly++) {
            for (int lx = 0; lx < w; lx++) {
                boolean edge = (lx == 0 || lx == w - 1 || ly == 0 || ly == h - 1);
                t[ly][lx] = edge ? TileType.WALL : TileType.FLOOR;
            }
        }
        // Door at bottom-centre
        int doorX = w / 2;
        t[h - 1][doorX] = TileType.DOOR;
        // Windows on sides (every 2 tiles, not on corners)
        for (int lx = 2; lx < w - 2; lx += 2) {
            t[0][lx]     = TileType.WALL; // top wall stays wall (no window sprite needed)
        }
        return t;
    }

    /** Draw the building sprite onto a Graphics2D at screen coords (sx, sy) = world pixel of tile (x, y). */
    public void draw(Graphics2D g, double camX, double camY, int tileSize) {
        int sx = (int)(x * tileSize - camX);
        int sy = (int)(y * tileSize - camY);
        int pw = w * tileSize;
        int ph = h * tileSize;

        // Draw each interior tile first (walls + floor tiles are rendered by GamePanel;
        // this method draws the decorative overlay: roof and sign)
        // Roof overlay (slightly transparent polygon over whole building)
        Color roof = type.roofColor;
        g.setColor(new Color(roof.getRed(), roof.getGreen(), roof.getBlue(), 200));
        // Pitched roof shape
        int[] rxs = { sx,      sx + pw/2,   sx + pw   };
        int[] rys = { sy + 4,  sy - tileSize, sy + 4   };
        g.fillPolygon(rxs, rys, 3);
        // Roof ridge line
        g.setColor(roof.darker());
        Stroke old = g.getStroke();
        g.setStroke(new BasicStroke(2f));
        g.drawLine(sx, sy + 4, sx + pw/2, sy - tileSize);
        g.drawLine(sx + pw/2, sy - tileSize, sx + pw, sy + 4);
        g.setStroke(old);

        // Sign above door
        int doorPixX = sx + (w / 2) * tileSize;
        int signW = Math.min(pw - 4, 70);
        int signX = doorPixX - signW / 2;
        int signY = sy + (h - 2) * tileSize - 18;
        g.setColor(new Color(0x5a3010));
        g.fillRoundRect(signX, signY, signW, 14, 4, 4);
        g.setColor(new Color(0xffd080));
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 8));
        FontMetrics fm = g.getFontMetrics();
        String label = type.label;
        if (fm.stringWidth(label) > signW - 4) label = type.name();
        g.drawString(label, signX + (signW - fm.stringWidth(label)) / 2, signY + 10);

        // Windows on walls
        g.setColor(new Color(0xaaddff, false));
        g.setColor(new Color(180, 220, 255, 180));
        for (int lx = 2; lx < w - 2; lx += 2) {
            // Top wall windows
            g.fillRect(sx + lx * tileSize + 4, sy + 4, tileSize - 8, tileSize / 2 - 2);
            g.setColor(new Color(100, 160, 200, 120));
            g.drawRect(sx + lx * tileSize + 4, sy + 4, tileSize - 8, tileSize / 2 - 2);
            g.setColor(new Color(180, 220, 255, 180));
        }
    }
}
