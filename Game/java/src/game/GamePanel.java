package game;

import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.util.*;
import java.util.List;
import java.util.stream.Collectors;

public class GamePanel extends JPanel implements ActionListener {

    public static final int TILE   = 32;
    public static final int WIDTH  = 800;
    public static final int HEIGHT = 600;

    private final WorldGen   world  = new WorldGen();
    private final Player     player = new Player(world);
    private final NPCManager npcMgr = new NPCManager(world);

    private final List<Enemy>      enemies     = new ArrayList<>();
    private final List<Item>       items       = new ArrayList<>();
    private final List<Projectile> projectiles = new ArrayList<>();

    // Popup messages (pick-up notices, level-up, etc.)
    private final List<FloatText> floatTexts = new ArrayList<>();

    private final Set<Integer> keys = new HashSet<>();
    private final BufferedImage buffer = new BufferedImage(WIDTH, HEIGHT, BufferedImage.TYPE_INT_RGB);

    // Pre-rendered full minimap image (regenerated once)
    private BufferedImage minimapImage;

    private double camX, camY;
    private double waterTime  = 0;
    private double spawnTimer = 0;
    private long   lastNano   = System.nanoTime();

    private boolean gameOver = false;

    public GamePanel() {
        setPreferredSize(new Dimension(WIDTH, HEIGHT));
        setFocusable(true);

        buildMinimapImage();
        spawnInitialItems();
        spawnInitialEnemies();

        addKeyListener(new KeyAdapter() {
            @Override public void keyPressed(KeyEvent e) {
                keys.add(e.getKeyCode());
                switch (e.getKeyCode()) {
                    case KeyEvent.VK_E, KeyEvent.VK_SPACE -> talkToNearbyNPC();
                    case KeyEvent.VK_F -> playerAttack();
                    case KeyEvent.VK_1 -> player.equipItem(0);
                    case KeyEvent.VK_2 -> player.equipItem(1);
                    case KeyEvent.VK_3 -> player.equipItem(2);
                    case KeyEvent.VK_4 -> player.equipItem(3);
                    case KeyEvent.VK_5 -> player.equipItem(4);
                    case KeyEvent.VK_6 -> player.equipItem(5);
                    case KeyEvent.VK_7 -> player.equipItem(6);
                    case KeyEvent.VK_8 -> player.equipItem(7);
                    case KeyEvent.VK_R -> { if (gameOver) restartGame(); }
                }
            }
            @Override public void keyReleased(KeyEvent e) { keys.remove(e.getKeyCode()); }
        });

        new javax.swing.Timer(16, this).start();
    }

    // ── Game loop ─────────────────────────────────────────────────────────────

    @Override
    public void actionPerformed(ActionEvent e) {
        if (gameOver) { repaint(); return; }

        long now = System.nanoTime();
        double dt = Math.min((now - lastNano) / 1_000_000_000.0, 0.05);
        lastNano = now;
        waterTime += dt;

        player.update(dt, keys, projectiles, enemies);
        if (player.dead) { gameOver = true; repaint(); return; }

        updateEnemies(dt);
        updateProjectiles(dt);
        updateItems(dt);
        updateNPCs(dt);
        checkPickups();
        enemySpawner(dt);

        floatTexts.removeIf(f -> f.life <= 0);
        floatTexts.forEach(f -> f.update(dt));

        updateCamera();
        repaint();
    }

    private void updateCamera() {
        camX = player.x - WIDTH  / 2.0;
        camY = player.y - HEIGHT / 2.0;
        int maxX = WorldGen.WORLD_W * TILE - WIDTH;
        int maxY = WorldGen.WORLD_H * TILE - HEIGHT;
        camX = Math.max(0, Math.min(camX, maxX));
        camY = Math.max(0, Math.min(camY, maxY));
    }

    private void playerAttack() {
        int prevEnemyCount = (int) enemies.stream().filter(en -> !en.dead).count();
        player.attack(enemies, projectiles);
        // Check kills for XP
        for (Enemy en : enemies) {
            if (en.dead) {
                int gained = en.kind.xpDrop;
                player.gainXP(gained);
                floatTexts.add(new FloatText("+" + gained + " XP", en.x, en.y, new Color(0xffee44)));
                // Chance to drop item on death
                if (Math.random() < 0.4) dropRandomItem(en.x, en.y);
            }
        }
        enemies.removeIf(en -> en.dead);
    }

    private void updateEnemies(double dt) {
        for (Enemy en : enemies) {
            en.update(dt, player.x, player.y, projectiles);
            if (en.dead) {
                player.gainXP(en.kind.xpDrop);
                floatTexts.add(new FloatText("+" + en.kind.xpDrop + " XP", en.x, en.y, new Color(0xffee44)));
                if (Math.random() < 0.4) dropRandomItem(en.x, en.y);
            }
        }
        enemies.removeIf(en -> en.dead);
    }

    private void updateProjectiles(double dt) {
        for (Projectile p : projectiles) {
            p.update(dt, world);
            if (p.fromPlayer && !p.dead) {
                for (Enemy en : enemies) {
                    double dx = p.x - en.x, dy = p.y - en.y;
                    if (!en.dead && dx*dx + dy*dy < 20*20) {
                        en.takeDamage(p.damage);
                        p.dead = true;
                        floatTexts.add(new FloatText("-" + p.damage, en.x, en.y - 10, new Color(0xff6644)));
                    }
                }
            }
        }
        projectiles.removeIf(p -> p.dead);
    }

    private void updateItems(double dt) { items.forEach(i -> i.update(dt)); }

    private void updateNPCs(double dt) {
        npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT).forEach(n -> n.update(dt));
    }

    private void checkPickups() {
        for (Item item : items) {
            if (!item.collected && item.isNear(player.x, player.y)) {
                int prevHp = player.hp;
                player.pickupItem(item);
                if (item.collected) {
                    if (item.type.heal > 0) {
                        int healed = player.hp - prevHp;
                        floatTexts.add(new FloatText("+" + healed + " HP", player.x, player.y - 20, new Color(0x44ff88)));
                    } else {
                        floatTexts.add(new FloatText("Got " + item.type.label, player.x, player.y - 20, new Color(0xffffff)));
                    }
                }
            }
        }
        items.removeIf(i -> i.collected);
    }

    private void enemySpawner(double dt) {
        spawnTimer -= dt;
        if (spawnTimer > 0) return;
        spawnTimer = 5 + Math.random() * 5;

        // Spawn 1-3 enemies outside camera view but within the world
        int count = 1 + (int)(Math.random() * 2);
        for (int i = 0; i < count; i++) trySpawnEnemy();
    }

    private void trySpawnEnemy() {
        for (int attempt = 0; attempt < 20; attempt++) {
            int tx = 1 + (int)(Math.random() * (WorldGen.WORLD_W - 2));
            int ty = 1 + (int)(Math.random() * (WorldGen.WORLD_H - 2));
            if (!world.get(tx, ty).walkable) continue;
            double wx = tx * TILE + TILE / 2.0;
            double wy = ty * TILE + TILE / 2.0;
            // Not on-screen
            if (wx > camX - 20 && wx < camX + WIDTH + 20 && wy > camY - 20 && wy < camY + HEIGHT + 20) continue;
            Enemy.Kind kind = randomEnemyKind();
            enemies.add(new Enemy(kind, wx, wy, world));
            return;
        }
    }

    private Enemy.Kind randomEnemyKind() {
        double r = Math.random();
        if (r < 0.30) return Enemy.Kind.SLIME;
        if (r < 0.50) return Enemy.Kind.ORC;
        if (r < 0.65) return Enemy.Kind.SKELETON;
        if (r < 0.78) return Enemy.Kind.ARCHER;
        if (r < 0.88) return Enemy.Kind.MAGE;
        return Enemy.Kind.TROLL;
    }

    private void dropRandomItem(double x, double y) {
        Item.Type[] pool = Item.Type.values();
        Item.Type t = pool[(int)(Math.random() * pool.length)];
        items.add(new Item(t, x, y));
    }

    private void spawnInitialItems() {
        Item.Type[] all = Item.Type.values();
        Random rng = new Random(1234);
        for (int i = 0; i < 40; i++) {
            int tx = 2 + rng.nextInt(WorldGen.WORLD_W - 4);
            int ty = 2 + rng.nextInt(WorldGen.WORLD_H - 4);
            if (!world.get(tx, ty).walkable) continue;
            Item.Type t = all[rng.nextInt(all.length)];
            items.add(new Item(t, tx * TILE + TILE / 2.0, ty * TILE + TILE / 2.0));
        }
    }

    private void spawnInitialEnemies() {
        Random rng = new Random(5678);
        for (int i = 0; i < 30; i++) {
            int tx = 2 + rng.nextInt(WorldGen.WORLD_W - 4);
            int ty = 2 + rng.nextInt(WorldGen.WORLD_H - 4);
            if (!world.get(tx, ty).walkable) continue;
            enemies.add(new Enemy(randomEnemyKind(), tx * TILE + TILE / 2.0, ty * TILE + TILE / 2.0, world));
        }
    }

    private void restartGame() { /* handled by restarting JFrame – simplest approach */ System.exit(0); }

    // ── Minimap pre-render ────────────────────────────────────────────────────

    private void buildMinimapImage() {
        int mw = WorldGen.WORLD_W;
        int mh = WorldGen.WORLD_H;
        minimapImage = new BufferedImage(mw, mh, BufferedImage.TYPE_INT_RGB);
        Graphics mg = minimapImage.getGraphics();
        TileType[][] raw = world.getRawTiles();
        for (int y = 0; y < mh; y++) {
            for (int x = 0; x < mw; x++) {
                mg.setColor(raw[y][x].color);
                mg.fillRect(x, y, 1, 1);
            }
        }
        // Draw buildings
        for (Building b : world.getBuildings()) {
            mg.setColor(new Color(0x8a7060));
            mg.fillRect(b.x, b.y, b.w, b.h);
        }
        mg.dispose();
    }

    // ── Render ────────────────────────────────────────────────────────────────

    @Override
    protected void paintComponent(Graphics gScreen) {
        super.paintComponent(gScreen);
        Graphics2D g = buffer.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        g.setColor(new Color(0x1a3a5a));
        g.fillRect(0, 0, WIDTH, HEIGHT);

        drawWorld(g);
        drawBuildings(g);
        // Draw items below NPCs/enemies
        items.stream()
             .filter(i -> !i.collected)
             .forEach(i -> i.draw(g, camX, camY));
        // Sort drawables by Y
        List<NPC>   npcs  = npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT);
        List<Enemy> vis   = enemies.stream()
                                   .filter(en -> isOnScreen(en.x, en.y))
                                   .collect(Collectors.toList());

        // Combined Y-sorted draw list
        record Drawable(double y, Runnable draw) {}
        List<Drawable> drawables = new ArrayList<>();
        npcs.forEach(n  -> drawables.add(new Drawable(n.y,      () -> n.draw(g, camX, camY))));
        vis.forEach(en  -> drawables.add(new Drawable(en.y,     () -> en.draw(g, camX, camY))));
        drawables.add(new Drawable(player.y, () -> player.draw(g, camX, camY)));
        drawables.sort(Comparator.comparingDouble(d -> d.y()));
        drawables.forEach(d -> d.draw().run());

        projectiles.forEach(p -> p.draw(g, camX, camY));
        floatTexts.forEach(f -> f.draw(g, camX, camY));

        drawMinimap(g);
        drawHUD(g);
        drawInventory(g);
        drawVignette(g);

        if (gameOver) drawGameOver(g);

        g.dispose();
        gScreen.drawImage(buffer, 0, 0, null);
    }

    // ── World ─────────────────────────────────────────────────────────────────

    private void drawWorld(Graphics2D g) {
        int sx0 = (int)Math.floor(camX / TILE) - 1;
        int sy0 = (int)Math.floor(camY / TILE) - 1;
        int sx1 = sx0 + WIDTH  / TILE + 3;
        int sy1 = sy0 + HEIGHT / TILE + 3;

        for (int ty = sy0; ty <= sy1; ty++) {
            for (int tx = sx0; tx <= sx1; tx++) {
                int px = (int)(tx * TILE - camX);
                int py = (int)(ty * TILE - camY);
                drawTile(g, tx, ty, px, py);
            }
        }
    }

    private void drawTile(Graphics2D g, int tx, int ty, int px, int py) {
        TileType type = world.get(tx, ty);
        g.setColor(type.color);
        g.fillRect(px, py, TILE, TILE);
        double v = hash(tx, ty, 99);

        switch (type) {
            case GRASS, DARK_GRASS -> {
                g.setColor(type == TileType.GRASS ? new Color(0x3d7a35) : new Color(0x256022));
                if (v > 0.72) { g.fillRect(px+4,py+6,3,5); g.fillRect(px+12,py+14,3,5); g.fillRect(px+21,py+5,3,5); }
            }
            case FOREST -> {
                for (int i = 0; i < (int)(v*3)+1; i++) {
                    int fx=(int)(hash(tx+i,ty,1)*(TILE-12))+6, fy=(int)(hash(tx+i,ty,2)*(TILE-12))+6;
                    int r=(int)(5+hash(tx,ty+i,3)*3);
                    g.setColor(new Color(0x0f3d0f)); g.fillOval(px+fx-r,py+fy-r,r*2,r*2);
                    g.setColor(new Color(0x1a5c1a)); g.fillOval(px+fx-r+1,py+fy-r+1,r*2-2,r*2-2);
                }
            }
            case SAND -> { if(v>0.65){ g.setColor(new Color(0xbfa070)); g.fillRect(px+7,py+10,3,3); g.fillRect(px+18,py+20,2,2); } }
            case MOUNTAIN -> {
                g.setColor(new Color(0x6a5a4a)); g.fillPolygon(new int[]{px+TILE/2,px+TILE-3,px+3},new int[]{py+4,py+TILE-3,py+TILE-3},3);
                g.setColor(new Color(0x9a8a7a)); g.fillPolygon(new int[]{px+TILE/2,px+TILE/2+8,px+TILE/2-8},new int[]{py+4,py+TILE/2,py+TILE/2},3);
            }
            case SNOW -> {
                g.setColor(new Color(0xc8c8d8)); g.fillPolygon(new int[]{px+TILE/2,px+TILE-2,px+2},new int[]{py+2,py+TILE-2,py+TILE-2},3);
                g.setColor(new Color(0xf0f0ff)); g.fillPolygon(new int[]{px+TILE/2,px+TILE/2+6,px+TILE/2-6},new int[]{py+2,py+TILE/2-2,py+TILE/2-2},3);
            }
            case PATH -> { g.setColor(new Color(0xa89858)); g.fillRect(px+12,py,8,TILE); g.setColor(new Color(0x988848)); g.fillRect(px+14,py,4,TILE); }
            case WALL -> {
                g.setColor(new Color(0x6a5848)); g.fillRect(px+1,py+1,TILE-2,TILE-2);
                g.setColor(new Color(0x504038));
                for (int by=0;by<TILE;by+=6) for (int bx=(by/6)%2==0?0:5;bx<TILE;bx+=10) g.drawRect(px+bx+1,py+by+1,9,5);
            }
            case FLOOR -> { g.setColor(new Color(0xb0a070)); for(int fi=0;fi<TILE;fi+=8){g.drawLine(px+fi,py,px+fi,py+TILE);g.drawLine(px,py+fi,px+TILE,py+fi);} }
            case DOOR  -> { g.setColor(new Color(0x5a3010)); g.fillRect(px+8,py+4,TILE-16,TILE-4); g.setColor(new Color(0xc89040)); g.fillOval(px+TILE-14,py+TILE/2,4,4); }
            case SHALLOW_WATER, DEEP_WATER -> {
                Color rip = type==TileType.DEEP_WATER?new Color(0x1e5a9a):new Color(0x3a7fd0);
                g.setColor(rip); Stroke old=g.getStroke(); g.setStroke(new BasicStroke(1.2f));
                int oy=(int)((waterTime*18+tx*7+ty*13)%TILE);
                g.drawArc(px+2,py+oy-4,26,8,0,180); g.setStroke(old);
            }
        }
        g.setColor(new Color(0,0,0,16)); g.drawRect(px,py,TILE,TILE);
    }

    private void drawBuildings(Graphics2D g) {
        int tx0=(int)Math.floor(camX/TILE)-2, ty0=(int)Math.floor(camY/TILE)-2;
        int tx1=tx0+WIDTH/TILE+4,             ty1=ty0+HEIGHT/TILE+4;
        for (Building b : world.getBuildings())
            if (b.x+b.w>tx0 && b.x<tx1 && b.y+b.h>ty0 && b.y<ty1)
                b.draw(g, camX, camY, TILE);
    }

    // ── Minimap (pre-rendered, shows only terrain + buildings) ────────────────

    private void drawMinimap(Graphics2D g) {
        final int MW = 140, MH = 105;
        final int MX = WIDTH - MW - 8, MY = 8;
        final double SX = MW / (double) WorldGen.WORLD_W;
        final double SY = MH / (double) WorldGen.WORLD_H;

        // Border + background
        g.setColor(new Color(0, 0, 0, 180));
        g.fillRect(MX - 2, MY - 2, MW + 4, MH + 4);

        // Scaled terrain image
        g.drawImage(minimapImage, MX, MY, MW, MH, null);

        // Camera viewport rect (white outline)
        int vx = (int)(camX / TILE * SX);
        int vy = (int)(camY / TILE * SY);
        int vw = (int)(WIDTH  / (double)TILE * SX);
        int vh = (int)(HEIGHT / (double)TILE * SY);
        g.setColor(new Color(255, 255, 255, 160));
        Stroke old = g.getStroke();
        g.setStroke(new BasicStroke(1.2f));
        g.drawRect(MX + vx, MY + vy, vw, vh);
        g.setStroke(old);

        // Player dot (red, no enemies shown)
        int pdx = (int)(player.x / TILE * SX);
        int pdy = (int)(player.y / TILE * SY);
        g.setColor(new Color(0xff3333));
        g.fillOval(MX + pdx - 3, MY + pdy - 3, 6, 6);
        g.setColor(Color.WHITE);
        g.drawOval(MX + pdx - 3, MY + pdy - 3, 6, 6);

        // Label
        g.setColor(new Color(180, 200, 220));
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 9));
        g.drawString("MAP", MX + 2, MY + MH + 1);

        g.setColor(new Color(255,255,255,60));
        g.drawRect(MX - 2, MY - 2, MW + 4, MH + 4);
    }

    // ── HUD ───────────────────────────────────────────────────────────────────

    private void drawHUD(Graphics2D g) {
        // HP bar
        int barW = 160, barH = 14;
        int bx = 10, by = 10;
        g.setColor(new Color(0,0,0,160));
        g.fillRoundRect(bx-2, by-2, barW+4, barH+4, 5, 5);
        g.setColor(new Color(0x660000));
        g.fillRect(bx, by, barW, barH);
        float pct = (float)player.hp / (Player.MAX_HP + (player.level-1)*10);
        g.setColor(pct>0.5f? new Color(0x44cc44) : pct>0.25f? new Color(0xeeaa00) : new Color(0xee2222));
        g.fillRect(bx, by, (int)(barW*pct), barH);
        g.setColor(Color.WHITE);
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 10));
        g.drawString("HP " + player.hp + "/" + (Player.MAX_HP + (player.level-1)*10), bx+4, by+11);

        // XP bar
        int xpW = 160, xpH = 6;
        int xbx = 10, xby = 28;
        g.setColor(new Color(0,0,0,140));
        g.fillRect(xbx, xby, xpW, xpH);
        g.setColor(new Color(0x4488ff));
        g.fillRect(xbx, xby, (int)(xpW * (player.xp / (float)(player.level * 100))), xpH);
        g.setColor(new Color(0xaaccff));
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 9));
        g.drawString("LVL " + player.level, xbx, xby + 16);

        // Weapon info
        String wep = player.equippedWeapon != null ? player.equippedWeapon.type.label : "Fists";
        g.setColor(new Color(0xffd080));
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 10));
        g.drawString("WEP: " + wep, 10, 58);

        // Controls bar at bottom
        g.setColor(new Color(0,0,0,140));
        g.fillRect(0, HEIGHT-22, WIDTH, 22);
        g.setColor(new Color(0xaaddff));
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 11));

        int tx=(int)(player.x/TILE), ty2=(int)(player.y/TILE);
        String zone = world.get(tx,ty2).zoneName;

        // NPC hint
        boolean npcClose = npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT)
                                  .stream().anyMatch(n -> n.isNear(player.x, player.y, 42));
        String hint = npcClose ? "  [E] Talk" : "";
        g.drawString("WASD=Move  F=Attack  1-8=Equip  |  " + zone + " (" + tx + "," + ty2 + ")" + hint, 8, HEIGHT-7);
    }

    private void drawInventory(Graphics2D g) {
        int slots = Player.MAX_INV;
        int sw = 36, sh = 36, gap = 4;
        int totalW = slots * (sw + gap) - gap;
        int startX = (WIDTH - totalW) / 2;
        int startY = HEIGHT - 68;

        for (int i = 0; i < slots; i++) {
            int sx = startX + i * (sw + gap);
            boolean equipped = i < player.inventory.size() && player.inventory.get(i) == player.equippedWeapon;

            // Slot background
            g.setColor(equipped ? new Color(0x805020, false) : new Color(0, 0, 0, 140));
            g.fillRoundRect(sx, startY, sw, sh, 5, 5);
            g.setColor(equipped ? new Color(0xffa040) : new Color(255,255,255,60));
            g.drawRoundRect(sx, startY, sw, sh, 5, 5);

            // Slot number
            g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 8));
            g.setColor(new Color(255,255,255,100));
            g.drawString(String.valueOf(i+1), sx+2, startY+9);

            // Item icon
            if (i < player.inventory.size()) {
                Item item = player.inventory.get(i);
                item.draw(g, item.x - sx - sw/2.0, item.y - startY - sh/2.0 - 2);
                // Override position to draw in slot
                int icx = sx + sw/2, icy = startY + sh/2 + 2;
                // Simple colored square icon
                g.setColor(item.type.color);
                g.fillRoundRect(sx+8, startY+10, sw-16, sh-16, 3, 3);
                g.setColor(Color.WHITE);
                g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 7));
                String abbr = item.type.label.substring(0,Math.min(4,item.type.label.length()));
                FontMetrics fm = g.getFontMetrics();
                g.drawString(abbr, sx + (sw - fm.stringWidth(abbr))/2, startY + 28);
            }
        }
    }

    private void drawGameOver(Graphics2D g) {
        g.setColor(new Color(0,0,0,160));
        g.fillRect(0,0,WIDTH,HEIGHT);
        g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 40));
        g.setColor(new Color(0xff3333));
        String msg = "YOU DIED";
        FontMetrics fm = g.getFontMetrics();
        g.drawString(msg, (WIDTH-fm.stringWidth(msg))/2, HEIGHT/2 - 20);
        g.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 16));
        g.setColor(Color.WHITE);
        String sub = "Press R to restart";
        FontMetrics fm2 = g.getFontMetrics();
        g.drawString(sub, (WIDTH-fm2.stringWidth(sub))/2, HEIGHT/2 + 20);
        g.setColor(new Color(0xffd080));
        String stats = "Level " + player.level + "  |  XP: " + player.xp;
        g.drawString(stats, (WIDTH - fm2.stringWidth(stats))/2, HEIGHT/2 + 50);
    }

    private void drawVignette(Graphics2D g) {
        g.setPaint(new RadialGradientPaint(new Point(WIDTH/2, HEIGHT/2), HEIGHT*0.75f,
            new float[]{0.35f,1f}, new Color[]{new Color(0,0,0,0), new Color(0,0,0,90)}));
        g.fillRect(0,0,WIDTH,HEIGHT);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private void talkToNearbyNPC() {
        boolean enemiesNear = enemies.stream().anyMatch(en ->
            !en.dead && Math.hypot(en.x - player.x, en.y - player.y) < 150);
        boolean hasItems = !player.inventory.isEmpty();
        int maxHp = Player.MAX_HP + (player.level - 1) * 10;
        npcMgr.getNPCsInView(camX, camY, WIDTH, HEIGHT).forEach(npc -> {
            if (npc.isNear(player.x, player.y, 42))
                npc.startTalkContextual(player.x, player.y, player.hp, maxHp,
                    player.level, enemiesNear, hasItems);
        });
    }

    private boolean isOnScreen(double wx, double wy) {
        return wx > camX - 50 && wx < camX + WIDTH + 50 && wy > camY - 50 && wy < camY + HEIGHT + 50;
    }

    private double hash(double x, double y, double seed) {
        double v = Math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453;
        return v - Math.floor(v);
    }

    // ── FloatText ─────────────────────────────────────────────────────────────

    private static class FloatText {
        String text; double x, y; Color color; double life = 1.2;
        FloatText(String t, double x, double y, Color c) { text=t; this.x=x; this.y=y; color=c; }
        void update(double dt) { y -= 25 * dt; life -= dt; }
        void draw(Graphics2D g, double camX, double camY) {
            int sx=(int)(x-camX), sy=(int)(y-camY);
            float alpha = (float)Math.min(1.0, life * 2);
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 13));
            g.setColor(new Color(0,0,0, (int)(120*alpha)));
            g.drawString(text, sx+1, sy+1);
            g.setColor(new Color(color.getRed(), color.getGreen(), color.getBlue(), (int)(255*alpha)));
            g.drawString(text, sx, sy);
        }
    }
}
