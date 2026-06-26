package game;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.util.*;
import java.util.List;

public class GamePanel extends JPanel implements ActionListener {

    public static final int TILE   = 32;
    public static final int WIDTH  = 800;
    public static final int HEIGHT = 600;

    // World margin for tile decorations (one extra tile on each side)
    private static final int MARGIN = 1;

    private final WorldGen   world  = new WorldGen();
    private final Player     player = new Player(world);
    private final NPCManager npcMgr = new NPCManager(world);
    private final Set<Integer> keys = new HashSet<>();

    private final BufferedImage buffer = new BufferedImage(WIDTH, HEIGHT, BufferedImage.TYPE_INT_RGB);

    private double camX, camY;
    private double waterTime = 0;
    private long   lastNano  = System.nanoTime();

    // Coordinate of latest "interact" press (E / Space)
    private String interactHint = null;
    private double hintTimer    = 0;

    public GamePanel() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setFocusable(true);

        addKeyListener(new KeyAdapter() {
            @Override public void keyPressed(KeyEvent e) {
                keys.add(e.getKeyCode());
                if (e.getKeyCode() == KeyEvent.VK_E || e.getKeyCode() == KeyEvent.VK_SPACE) {
                    npcMgr.tryTalk(player.x, player.y);
                }
            }
            @Override public void keyReleased(KeyEvent e) { keys.remove(e.getKeyCode()); }
        });

        new javax.swing.Timer(16, this).start();
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

        // Update visible NPCs
        List<NPC> npcs = npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT);
        for (NPC npc : npcs) npc.update(dt);

        if (hintTimer > 0) hintTimer -= dt;

        repaint();
    }

    private void updateCamera() {
        camX = player.x - WIDTH  / 2.0;
        camY = player.y - HEIGHT / 2.0;
    }

    // ── Rendering ─────────────────────────────────────────────────────────────

    @Override
    protected void paintComponent(Graphics gScreen) {
        super.paintComponent(gScreen);
        Graphics2D g = buffer.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        g.setColor(new Color(0x1a3a5a));
        g.fillRect(0, 0, WIDTH, HEIGHT);

        drawWorld(g);
        drawBuildings(g);
        drawNPCs(g);
        player.draw(g, camX, camY);
        drawMinimap(g);
        drawHUD(g);
        drawVignette(g);

        g.dispose();
        gScreen.drawImage(buffer, 0, 0, null);
    }

    // ── World tiles ───────────────────────────────────────────────────────────

    private void drawWorld(Graphics2D g) {
        int startX = (int)Math.floor(camX / TILE) - MARGIN;
        int startY = (int)Math.floor(camY / TILE) - MARGIN;
        int endX   = startX + WIDTH  / TILE + MARGIN * 2 + 1;
        int endY   = startY + HEIGHT / TILE + MARGIN * 2 + 1;

        for (int ty = startY; ty <= endY; ty++) {
            for (int tx = startX; tx <= endX; tx++) {
                int sx = (int)(tx * TILE - camX);
                int sy = (int)(ty * TILE - camY);
                drawTile(g, tx, ty, sx, sy);
            }
        }
    }

    private void drawTile(Graphics2D g, int tx, int ty, int sx, int sy) {
        TileType type = world.get(tx, ty);
        g.setColor(type.color);
        g.fillRect(sx, sy, TILE, TILE);

        double v = hash(tx, ty, 99);

        switch (type) {
            case GRASS, DARK_GRASS -> {
                g.setColor(type == TileType.GRASS ? new Color(0x3d7a35) : new Color(0x256022));
                if (v > 0.72) {
                    g.fillRect(sx + 4,  sy + 6,  3, 5);
                    g.fillRect(sx + 12, sy + 14, 3, 5);
                    g.fillRect(sx + 21, sy + 5,  3, 5);
                    g.fillRect(sx + 26, sy + 19, 3, 4);
                }
            }
            case FOREST -> {
                int trees = (int)(v * 3) + 1;
                for (int i = 0; i < trees; i++) {
                    int fx = (int)(hash(tx + i, ty, 1) * (TILE - 12)) + 6;
                    int fy = (int)(hash(tx + i, ty, 2) * (TILE - 12)) + 6;
                    int r  = (int)(5 + hash(tx, ty + i, 3) * 3);
                    g.setColor(new Color(0x0f3d0f));
                    g.fillOval(sx + fx - r, sy + fy - r, r * 2, r * 2);
                    g.setColor(new Color(0x1a5c1a));
                    g.fillOval(sx + fx - r + 1, sy + fy - r + 1, r * 2 - 2, r * 2 - 2);
                }
            }
            case SAND -> {
                if (v > 0.65) {
                    g.setColor(new Color(0xbfa070));
                    g.fillRect(sx + 7,  sy + 10, 3, 3);
                    g.fillRect(sx + 18, sy + 20, 2, 2);
                    g.fillRect(sx + 24, sy + 8,  2, 2);
                }
            }
            case MOUNTAIN -> {
                g.setColor(new Color(0x6a5a4a));
                g.fillPolygon(new int[]{sx+TILE/2, sx+TILE-3, sx+3}, new int[]{sy+4, sy+TILE-3, sy+TILE-3}, 3);
                g.setColor(new Color(0x9a8a7a));
                g.fillPolygon(new int[]{sx+TILE/2, sx+TILE/2+8, sx+TILE/2-8}, new int[]{sy+4, sy+TILE/2, sy+TILE/2}, 3);
            }
            case SNOW -> {
                g.setColor(new Color(0xc8c8d8));
                g.fillPolygon(new int[]{sx+TILE/2, sx+TILE-2, sx+2}, new int[]{sy+2, sy+TILE-2, sy+TILE-2}, 3);
                g.setColor(new Color(0xf0f0ff));
                g.fillPolygon(new int[]{sx+TILE/2, sx+TILE/2+6, sx+TILE/2-6}, new int[]{sy+2, sy+TILE/2-2, sy+TILE/2-2}, 3);
            }
            case PATH -> {
                g.setColor(new Color(0xa89858));
                g.fillRect(sx + 12, sy, 8, TILE);
                g.setColor(new Color(0x988848));
                g.fillRect(sx + 14, sy, 4, TILE);
            }
            case WALL -> {
                g.setColor(new Color(0x6a5848));
                g.fillRect(sx + 1, sy + 1, TILE - 2, TILE - 2);
                // Brick pattern
                boolean rowOffset = (ty % 2 == 0);
                g.setColor(new Color(0x504038));
                int bw = 10, bh = 6;
                for (int by2 = 0; by2 < TILE; by2 += bh) {
                    int off = (rowOffset && (by2 / bh) % 2 == 0) ? bw / 2 : 0;
                    for (int bx2 = -bw + off; bx2 < TILE; bx2 += bw)
                        g.drawRect(sx + bx2 + 1, sy + by2 + 1, bw - 1, bh - 1);
                }
            }
            case FLOOR -> {
                g.setColor(new Color(0xb8a880));
                for (int fi = 0; fi < TILE; fi += 8)
                    g.drawLine(sx + fi, sy, sx + fi, sy + TILE);
                for (int fi = 0; fi < TILE; fi += 8)
                    g.drawLine(sx, sy + fi, sx + TILE, sy + fi);
            }
            case DOOR -> {
                g.setColor(new Color(0x5a3010));
                g.fillRect(sx + 8, sy + 4, TILE - 16, TILE - 4);
                g.setColor(new Color(0xc89040));
                g.fillOval(sx + TILE - 14, sy + TILE / 2, 4, 4);
                g.setColor(new Color(0x3a1a00));
                g.drawRect(sx + 8, sy + 4, TILE - 16, TILE - 4);
            }
            case SHALLOW_WATER, DEEP_WATER -> {
                Color ripple = type == TileType.DEEP_WATER ? new Color(0x1e5a9a) : new Color(0x3a7fd0);
                g.setColor(ripple);
                Stroke old = g.getStroke();
                g.setStroke(new BasicStroke(1.2f));
                int oy = (int)((waterTime * 18 + tx * 7 + ty * 13) % TILE);
                g.drawArc(sx + 2, sy + oy - 4, 26, 8, 0, 180);
                g.setStroke(old);
            }
        }

        // Grid
        g.setColor(new Color(0, 0, 0, 18));
        g.drawRect(sx, sy, TILE, TILE);
    }

    // ── Buildings ─────────────────────────────────────────────────────────────

    private void drawBuildings(Graphics2D g) {
        int tx0 = (int)Math.floor(camX / TILE) - 2;
        int ty0 = (int)Math.floor(camY / TILE) - 2;
        int tx1 = tx0 + WIDTH  / TILE + 4;
        int ty1 = ty0 + HEIGHT / TILE + 4;

        for (Building b : world.getBuildingsInView(tx0, ty0, tx1, ty1))
            b.draw(g, camX, camY, TILE);
    }

    // ── NPCs ──────────────────────────────────────────────────────────────────

    private void drawNPCs(Graphics2D g) {
        List<NPC> npcs = npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT);
        // Sort by Y so characters further down draw on top
        npcs.sort(Comparator.comparingDouble(n -> n.y));
        for (NPC npc : npcs) npc.draw(g, camX, camY);
    }

    // ── Mini-map ──────────────────────────────────────────────────────────────

    private void drawMinimap(Graphics2D g) {
        int mw = 120, mh = 90;
        int mx = WIDTH - mw - 10, my = 10;

        g.setColor(new Color(0, 0, 0, 160));
        g.fillRect(mx - 2, my - 2, mw + 4, mh + 4);

        // Draw terrain for the visible region ±a few chunks
        int tileRange = 60;
        int ptx = (int)(player.x / TILE);
        int pty = (int)(player.y / TILE);
        double scaleX = mw / (double)(tileRange * 2);
        double scaleY = mh / (double)(tileRange * 2);

        for (int dy = -tileRange; dy < tileRange; dy++) {
            for (int dx = -tileRange; dx < tileRange; dx++) {
                int wx = ptx + dx, wy = pty + dy;
                TileType t = world.get(wx, wy);
                g.setColor(t.color);
                int px = (int)(mx + (dx + tileRange) * scaleX);
                int py = (int)(my + (dy + tileRange) * scaleY);
                int pw = Math.max(1, (int)Math.ceil(scaleX));
                int ph = Math.max(1, (int)Math.ceil(scaleY));
                g.fillRect(px, py, pw, ph);
            }
        }

        // Viewport rect
        int vwt = WIDTH  / TILE;
        int vht = HEIGHT / TILE;
        int vx = (int)(mx + (tileRange - vwt / 2) * scaleX);
        int vy = (int)(my + (tileRange - vht / 2) * scaleY);
        int vw = (int)(vwt * scaleX);
        int vh = (int)(vht * scaleY);
        g.setColor(new Color(255, 255, 255, 140));
        g.drawRect(vx, vy, vw, vh);

        // Player dot
        g.setColor(new Color(0xff4444));
        g.fillOval(mx + mw/2 - 2, my + mh/2 - 2, 5, 5);

        g.setColor(new Color(255, 255, 255, 80));
        g.drawRect(mx - 2, my - 2, mw + 4, mh + 4);
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 9));
        g.setColor(new Color(180, 200, 220));
        g.drawString("MAP", mx + 2, my + mh + 1);
    }

    // ── HUD ───────────────────────────────────────────────────────────────────

    private void drawHUD(Graphics2D g) {
        int tx = (int)(player.x / TILE);
        int ty = (int)(player.y / TILE);
        TileType here = world.get(tx, ty);

        // Check for nearby NPC
        List<NPC> nearby = npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT);
        boolean npcClose = nearby.stream().anyMatch(n -> n.isNear(player.x, player.y, 42));

        g.setColor(new Color(0, 0, 0, 140));
        g.fillRect(0, HEIGHT - 24, WIDTH, 24);

        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        g.setColor(new Color(0xaaddff));
        g.drawString(String.format("WASD=Move  E=Talk  |  Pos: %d, %d  |  Zone: %s", tx, ty, here.zoneName), 10, HEIGHT - 8);

        if (npcClose) {
            g.setColor(new Color(0xffd700));
            g.drawString("[E] Talk", WIDTH - 100, HEIGHT - 8);
        }
    }

    private void drawVignette(Graphics2D g) {
        RadialGradientPaint vignette = new RadialGradientPaint(
            new Point(WIDTH / 2, HEIGHT / 2), HEIGHT * 0.75f,
            new float[]{0.35f, 1.0f},
            new Color[]{new Color(0,0,0,0), new Color(0,0,0,90)}
        );
        g.setPaint(vignette);
        g.fillRect(0, 0, WIDTH, HEIGHT);
    }

    // ── Utility ───────────────────────────────────────────────────────────────

    private double hash(double x, double y, double seed) {
        double v = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
        return v - Math.floor(v);
    }
}
