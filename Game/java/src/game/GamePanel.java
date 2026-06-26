package game;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.util.HashSet;
import java.util.Set;

public class GamePanel extends JPanel implements ActionListener {

    public static final int TILE   = 32;
    public static final int WIDTH  = 800;
    public static final int HEIGHT = 600;

    private final WorldGen  world  = new WorldGen();
    private final Player    player = new Player(world);
    private final Set<Integer> keys = new HashSet<>();

    // Off-screen buffer for smooth rendering
    private final BufferedImage buffer = new BufferedImage(WIDTH, HEIGHT, BufferedImage.TYPE_INT_RGB);

    // Camera
    private double camX, camY;

    // Tile decoration cache (noise values)
    private final double[][] decoMap = new double[WorldGen.WORLD_H][WorldGen.WORLD_W];

    // Water animation
    private double waterTime = 0;

    private long lastNano = System.nanoTime();

    public GamePanel() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setBackground(Color.BLACK);
        setFocusable(true);

        buildDecoMap();

        addKeyListener(new KeyAdapter() {
            @Override public void keyPressed(KeyEvent e)  { keys.add(e.getKeyCode()); }
            @Override public void keyReleased(KeyEvent e) { keys.remove(e.getKeyCode()); }
        });

        // ~60 fps timer
        new Timer(16, this).start();
    }

    private void buildDecoMap() {
        for (int y = 0; y < WorldGen.WORLD_H; y++)
            for (int x = 0; x < WorldGen.WORLD_W; x++) {
                double v = Math.sin(x * 127.1 + y * 311.7 + 99 * 74.3) * 43758.5453;
                decoMap[y][x] = v - Math.floor(v);
            }
    }

    // ── Game loop ─────────────────────────────────────────────────────────────

    @Override
    public void actionPerformed(ActionEvent e) {
        long now = System.nanoTime();
        double dt = Math.min((now - lastNano) / 1_000_000_000.0, 0.05);
        lastNano = now;
        waterTime += dt;

        player.update(dt, keys);
        updateCamera();
        repaint();
    }

    private void updateCamera() {
        camX = player.x - WIDTH  / 2.0;
        camY = player.y - HEIGHT / 2.0;
        camX = Math.max(0, Math.min(camX, WorldGen.WORLD_W * TILE - WIDTH));
        camY = Math.max(0, Math.min(camY, WorldGen.WORLD_H * TILE - HEIGHT));
    }

    // ── Rendering ─────────────────────────────────────────────────────────────

    @Override
    protected void paintComponent(Graphics gScreen) {
        super.paintComponent(gScreen);
        Graphics2D g = buffer.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Background
        g.setColor(new Color(0x1a3a5a));
        g.fillRect(0, 0, WIDTH, HEIGHT);

        drawWorld(g);
        player.draw(g, camX, camY);
        drawMinimap(g);
        drawHUD(g);
        drawVignette(g);

        g.dispose();
        gScreen.drawImage(buffer, 0, 0, null);
    }

    private void drawWorld(Graphics2D g) {
        int startX = Math.max(0, (int)(camX / TILE));
        int startY = Math.max(0, (int)(camY / TILE));
        int endX   = Math.min(WorldGen.WORLD_W, (int)((camX + WIDTH)  / TILE) + 1);
        int endY   = Math.min(WorldGen.WORLD_H, (int)((camY + HEIGHT) / TILE) + 1);

        for (int ty = startY; ty < endY; ty++) {
            for (int tx = startX; tx < endX; tx++) {
                int sx = (int)(tx * TILE - camX);
                int sy = (int)(ty * TILE - camY);
                drawTile(g, tx, ty, sx, sy);
            }
        }
    }

    private void drawTile(Graphics2D g, int tx, int ty, int sx, int sy) {
        TileType type = world.get(tx, ty);
        double v = decoMap[ty][tx];

        // Base fill
        g.setColor(type.color);
        g.fillRect(sx, sy, TILE, TILE);

        switch (type) {
            case GRASS, DARK_GRASS -> {
                g.setColor(type == TileType.GRASS ? new Color(0x3d7a35) : new Color(0x256022));
                if (v > 0.7) {
                    g.fillRect(sx + 4,  sy + 6,  3, 5);
                    g.fillRect(sx + 10, sy + 14, 3, 5);
                    g.fillRect(sx + 20, sy + 5,  3, 5);
                    g.fillRect(sx + 25, sy + 18, 3, 4);
                }
            }
            case FOREST -> {
                int trees = (int)(v * 3) + 1;
                for (int i = 0; i < trees; i++) {
                    double tv = hash(tx + i, ty, 1);
                    double tv2 = hash(tx + i, ty, 2);
                    int ftx = (int)(tv  * (TILE - 12)) + 6;
                    int fty = (int)(tv2 * (TILE - 12)) + 6;
                    int r   = (int)(5 + hash(tx, ty + i, 3) * 3);
                    g.setColor(new Color(0x0f3d0f));
                    g.fillOval(sx + ftx - r, sy + fty - r, r * 2, r * 2);
                    g.setColor(new Color(0x1a5c1a));
                    g.fillOval(sx + ftx - r + 1, sy + fty - r + 1, r * 2 - 2, r * 2 - 2);
                }
            }
            case SAND -> {
                if (v > 0.6) {
                    g.setColor(new Color(0xbfa070));
                    g.fillRect(sx + 7,  sy + 10, 3, 3);
                    g.fillRect(sx + 18, sy + 20, 2, 2);
                    g.fillRect(sx + 24, sy + 8,  2, 2);
                }
            }
            case MOUNTAIN -> {
                g.setColor(new Color(0x6a5a4a));
                int[] mxs = {sx + TILE/2, sx + TILE - 4, sx + 4};
                int[] mys = {sy + 4,      sy + TILE - 4,  sy + TILE - 4};
                g.fillPolygon(mxs, mys, 3);
                g.setColor(new Color(0x9a8a7a));
                int[] hxs = {sx + TILE/2, sx + TILE/2 + 8, sx + TILE/2 - 8};
                int[] hys = {sy + 4,      sy + TILE/2,      sy + TILE/2};
                g.fillPolygon(hxs, hys, 3);
            }
            case SNOW -> {
                g.setColor(new Color(0xc8c8d8));
                int[] sxs = {sx + TILE/2, sx + TILE - 2, sx + 2};
                int[] sys = {sy + 2,      sy + TILE - 2,  sy + TILE - 2};
                g.fillPolygon(sxs, sys, 3);
                g.setColor(new Color(0xf0f0ff));
                int[] sx2 = {sx + TILE/2, sx + TILE/2 + 6, sx + TILE/2 - 6};
                int[] sy2 = {sy + 2,      sy + TILE/2 - 2,  sy + TILE/2 - 2};
                g.fillPolygon(sx2, sy2, 3);
            }
            case VILLAGE -> {
                g.setColor(new Color(0xa0784a));
                g.fillRect(sx + 6, sy + 12, 20, 14);
                g.setColor(new Color(0x8b3030));
                int[] rx = {sx + 4, sx + 16, sx + 28};
                int[] ry = {sy + 12, sy + 4, sy + 12};
                g.fillPolygon(rx, ry, 3);
                g.setColor(new Color(0x5a3a20));
                g.fillRect(sx + 13, sy + 18, 6, 8);
            }
            case PATH -> {
                g.setColor(new Color(0xa89858));
                g.fillRect(sx + 13, sy, 6, TILE);
            }
            case SHALLOW_WATER, DEEP_WATER -> {
                Color ripple = type == TileType.DEEP_WATER ? new Color(0x1e5a9a) : new Color(0x3a7fd0);
                g.setColor(ripple);
                Stroke old = g.getStroke();
                g.setStroke(new BasicStroke(1.2f));
                int oy = (int)((waterTime * 20 + tx * 7 + ty * 13) % TILE);
                g.drawArc(sx + 2, sy + oy - 4, 26, 8, 0, 180);
                g.setStroke(old);
            }
        }

        // Subtle grid
        g.setColor(new Color(0, 0, 0, 20));
        g.drawRect(sx, sy, TILE, TILE);
    }

    private void drawMinimap(Graphics2D g) {
        int mw = 120, mh = 90;
        int mx = WIDTH - mw - 10, my = 10;
        double scale = mw / (double) WorldGen.WORLD_W;

        g.setColor(new Color(0, 0, 0, 160));
        g.fillRect(mx - 2, my - 2, mw + 4, mh + 4);

        TileType[][] tiles = world.getTiles();
        for (int y = 0; y < WorldGen.WORLD_H; y++) {
            for (int x = 0; x < WorldGen.WORLD_W; x++) {
                g.setColor(tiles[y][x].color);
                int px = (int)(mx + x * scale);
                int py = (int)(my + y * scale);
                int pw = Math.max(1, (int)Math.ceil(scale));
                g.fillRect(px, py, pw, pw);
            }
        }

        // Viewport rect
        int vx = (int)(camX / TILE * scale);
        int vy = (int)(camY / TILE * scale);
        int vw = (int)(WIDTH  / (double) TILE * scale);
        int vh = (int)(HEIGHT / (double) TILE * scale);
        g.setColor(new Color(255, 255, 255, 160));
        g.drawRect(mx + vx, my + vy, vw, vh);

        // Player dot
        int pdx = (int)(player.x / TILE * scale);
        int pdy = (int)(player.y / TILE * scale);
        g.setColor(new Color(0xff4444));
        g.fillOval(mx + pdx - 2, my + pdy - 2, 5, 5);

        g.setColor(new Color(255, 255, 255, 100));
        g.drawRect(mx - 2, my - 2, mw + 4, mh + 4);
    }

    private void drawHUD(Graphics2D g) {
        int tx = (int)(player.x / TILE);
        int ty = (int)(player.y / TILE);
        String zone = world.get(tx, ty).zoneName;
        String text = String.format("WASD / Arrows  |  Pos: %d, %d  |  Zone: %s", tx, ty, zone);

        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        g.setColor(new Color(0, 0, 0, 120));
        g.fillRect(0, HEIGHT - 22, WIDTH, 22);
        g.setColor(new Color(0xaaddff));
        g.drawString(text, 10, HEIGHT - 7);
    }

    private void drawVignette(Graphics2D g) {
        RadialGradientPaint vignette = new RadialGradientPaint(
            new Point(WIDTH / 2, HEIGHT / 2),
            HEIGHT * 0.75f,
            new float[]{0.3f, 1.0f},
            new Color[]{new Color(0, 0, 0, 0), new Color(0, 0, 0, 100)}
        );
        g.setPaint(vignette);
        g.fillRect(0, 0, WIDTH, HEIGHT);
    }

    // Simple hash for decoration noise
    private double hash(double x, double y, double seed) {
        double v = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
        return v - Math.floor(v);
    }
}
