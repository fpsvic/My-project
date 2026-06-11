import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.AffineTransform;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.SourceDataLine;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;

/**
 * Blood Quest: Gothic Platformer
 *
 * A standalone Java/Swing rewrite of the original single-page canvas game.
 * Compile with: javac BloodQuest.java
 * Run with:     java BloodQuest
 */
public final class BloodQuest {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            GamePanel panel = new GamePanel();
            JFrame frame = new JFrame("Blood Quest: Gothic Platformer");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setContentPane(panel);
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
            panel.requestFocusInWindow();
        });
    }

    private enum Screen {
        START,
        PLAYING,
        LEVEL_COMPLETE,
        GAME_OVER,
        VICTORY,
        PAUSED
    }

    private static final class GamePanel extends JPanel {
        private static final int VIEW_WIDTH = 800;
        private static final int VIEW_HEIGHT = 600;
        private static final int WORLD_TOP = 70;
        private static final int WORLD_HEIGHT = 450;
        private static final int HEADER_HEIGHT = 54;

        private static final double GRAVITY = 0.6;
        private static final double FRICTION = 0.85;
        private static final double ACCEL = 0.7;
        private static final double MAX_SPEED = 7.5;
        private static final double JUMP_FORCE = -12.5;
        private static final double SPRING_BOOST = -18.5;

        private final Timer frameTimer;
        private final InputState keys = new InputState();
        private final Player player = new Player();
        private final ParticleSystem particles = new ParticleSystem();
        private final AudioManager audio = new AudioManager();
        private final List<Level> levels = createLevels();
        private final Double[] bestTimes;
        private final Random random = new Random();

        private List<Platform> platforms = new ArrayList<>();
        private List<Spring> springs = new ArrayList<>();
        private List<Hazard> hazards = new ArrayList<>();
        private List<Collectible> collectibles = new ArrayList<>();
        private List<Enemy> enemies = new ArrayList<>();

        private Screen screen = Screen.START;
        private Portal portal = new Portal(0, 0);
        private int currentLevelIndex = 0;
        private int score = 0;
        private int lives = 3;
        private double screenShake = 0;
        private long levelStartTimeMs = 0;
        private long levelAccumulatedMs = 0;
        private boolean timerRunning = false;
        private long lastFpsTimeMs = System.currentTimeMillis();
        private int framesSinceFps = 0;
        private int fps = 0;
        private double lastClearTime = 0.0;
        private boolean lastClearWasBest = false;

        private double scale = 1.0;
        private double offsetX = 0.0;
        private double offsetY = 0.0;

        GamePanel() {
            setPreferredSize(new Dimension(1000, 750));
            setBackground(Color.BLACK);
            setFocusable(true);

            bestTimes = new Double[levels.size()];

            addKeyListener(new KeyAdapter() {
                @Override
                public void keyPressed(KeyEvent event) {
                    audio.init();
                    switch (event.getKeyCode()) {
                        case KeyEvent.VK_A:
                        case KeyEvent.VK_LEFT:
                            keys.left = true;
                            break;
                        case KeyEvent.VK_D:
                        case KeyEvent.VK_RIGHT:
                            keys.right = true;
                            break;
                        case KeyEvent.VK_W:
                        case KeyEvent.VK_SPACE:
                        case KeyEvent.VK_UP:
                            keys.up = true;
                            break;
                        case KeyEvent.VK_ESCAPE:
                        case KeyEvent.VK_P:
                            togglePause();
                            break;
                        case KeyEvent.VK_ENTER:
                            activatePrimaryScreenAction();
                            break;
                        case KeyEvent.VK_M:
                            audio.toggleMuted();
                            break;
                        default:
                            break;
                    }
                }

                @Override
                public void keyReleased(KeyEvent event) {
                    switch (event.getKeyCode()) {
                        case KeyEvent.VK_A:
                        case KeyEvent.VK_LEFT:
                            keys.left = false;
                            break;
                        case KeyEvent.VK_D:
                        case KeyEvent.VK_RIGHT:
                            keys.right = false;
                            break;
                        case KeyEvent.VK_W:
                        case KeyEvent.VK_SPACE:
                        case KeyEvent.VK_UP:
                            keys.up = false;
                            break;
                        default:
                            break;
                    }
                }
            });

            addMouseListener(new MouseAdapter() {
                @Override
                public void mousePressed(MouseEvent event) {
                    requestFocusInWindow();
                    audio.init();

                    double vx = (event.getX() - offsetX) / scale;
                    double vy = (event.getY() - offsetY) / scale;
                    handleClick(vx, vy);
                }
            });

            frameTimer = new Timer(1000 / 60, event -> {
                tick();
                repaint();
            });
            frameTimer.start();
        }

        private void handleClick(double x, double y) {
            if (buttonContains(730, 22, 34, 34, x, y)) {
                audio.toggleMuted();
                return;
            }

            if (screen == Screen.PLAYING && buttonContains(686, 22, 34, 34, x, y)) {
                pauseGame();
                return;
            }

            if (screen == Screen.START && buttonContains(285, 345, 230, 48, x, y)) {
                startGame();
            } else if (screen == Screen.LEVEL_COMPLETE && buttonContains(285, 360, 230, 46, x, y)) {
                nextLevel();
            } else if (screen == Screen.GAME_OVER && buttonContains(285, 360, 230, 46, x, y)) {
                startGame();
            } else if (screen == Screen.VICTORY && buttonContains(285, 385, 230, 46, x, y)) {
                startGame();
            } else if (screen == Screen.PAUSED) {
                if (buttonContains(205, 360, 180, 46, x, y)) {
                    resumeGame();
                } else if (buttonContains(415, 360, 180, 46, x, y)) {
                    abandonGame();
                }
            }
        }

        private boolean buttonContains(double bx, double by, double bw, double bh, double x, double y) {
            return x >= bx && x <= bx + bw && y >= by && y <= by + bh;
        }

        private void activatePrimaryScreenAction() {
            switch (screen) {
                case START:
                case GAME_OVER:
                case VICTORY:
                    startGame();
                    break;
                case LEVEL_COMPLETE:
                    nextLevel();
                    break;
                case PAUSED:
                    resumeGame();
                    break;
                default:
                    break;
            }
        }

        private void togglePause() {
            if (screen == Screen.PLAYING) {
                pauseGame();
            } else if (screen == Screen.PAUSED) {
                resumeGame();
            }
        }

        private void startGame() {
            score = 0;
            lives = 3;
            loadLevel(0);
            startLoop();
        }

        private void nextLevel() {
            loadLevel(currentLevelIndex + 1);
            startLoop();
        }

        private void pauseGame() {
            if (screen != Screen.PLAYING) {
                return;
            }
            stopLoop();
            screen = Screen.PAUSED;
            keys.clear();
        }

        private void resumeGame() {
            if (screen != Screen.PAUSED) {
                return;
            }
            startLoop();
        }

        private void abandonGame() {
            stopLoop();
            screen = Screen.START;
            keys.clear();
        }

        private void startLoop() {
            screen = Screen.PLAYING;
            levelStartTimeMs = System.currentTimeMillis();
            timerRunning = true;
            framesSinceFps = 0;
            lastFpsTimeMs = System.currentTimeMillis();
        }

        private void stopLoop() {
            if (timerRunning) {
                levelAccumulatedMs += System.currentTimeMillis() - levelStartTimeMs;
                timerRunning = false;
            }
        }

        private void loadLevel(int index) {
            currentLevelIndex = index;
            Level level = levels.get(index);

            player.reset(level.playerStartX, level.playerStartY);
            platforms = level.copyPlatforms();
            springs = level.copySprings();
            hazards = level.copyHazards();
            collectibles = level.copyCollectibles();
            enemies = level.copyEnemies();
            portal = new Portal(level.exitX, level.exitY);
            particles.clear();

            levelAccumulatedMs = 0;
            levelStartTimeMs = System.currentTimeMillis();
            timerRunning = false;
            screenShake = 0;
            keys.clear();
        }

        private void tick() {
            framesSinceFps++;
            long now = System.currentTimeMillis();
            if (now - lastFpsTimeMs >= 1000) {
                fps = framesSinceFps;
                framesSinceFps = 0;
                lastFpsTimeMs = now;
            }

            if (screen == Screen.PLAYING) {
                updateGame();
            }
        }

        private void updateGame() {
            if (screenShake > 0) {
                screenShake = Math.max(0, screenShake - 0.8);
            }

            for (Platform platform : platforms) {
                platform.update();
            }

            player.update(platforms, springs, keys, audio, particles);
            if (player.y > WORLD_HEIGHT) {
                hurtPlayer();
                return;
            }

            for (Enemy enemy : enemies) {
                if (enemy.dead) {
                    continue;
                }
                enemy.update();
                if (overlaps(player.x, player.y, player.w, player.h, enemy.x, enemy.y, enemy.w, enemy.h)) {
                    if (player.vy > 0 && player.y + player.h - player.vy <= enemy.y + 8) {
                        enemy.dead = true;
                        player.vy = JUMP_FORCE * 0.8;
                        score += 25;
                        audio.playEnemySquash();
                        particles.burst(enemy.x + enemy.w / 2.0, enemy.y + enemy.h / 2.0, new Color(69, 10, 10), 12);
                        particles.burst(enemy.x + enemy.w / 2.0, enemy.y + enemy.h / 2.0, new Color(220, 38, 38), 8);
                    } else {
                        hurtPlayer();
                    }
                }
            }

            for (Hazard hazard : hazards) {
                if (overlaps(player.x, player.y, player.w, player.h, hazard.x, hazard.y, hazard.w, hazard.h)) {
                    hurtPlayer();
                    break;
                }
            }

            for (Collectible collectible : collectibles) {
                if (!collectible.collected) {
                    double dx = collectible.x - (player.x + player.w / 2.0);
                    double dy = collectible.y - (player.y + player.h / 2.0);
                    if (Math.hypot(dx, dy) < 22) {
                        collectible.collected = true;
                        score += 10;
                        audio.playCoin();
                        particles.burst(collectible.x, collectible.y, new Color(220, 38, 38), 10);
                    }
                }
            }

            double portalDistance = Math.hypot(
                    portal.x - (player.x + player.w / 2.0),
                    portal.y - (player.y + player.h / 2.0));
            if (portalDistance < 25) {
                levelCleared();
                return;
            }

            portal.hoverOffset += 0.05;
            particles.update();
        }

        private void hurtPlayer() {
            if (player.invulnerable > 0) {
                return;
            }

            lives--;
            audio.playHurt();
            screenShake = 15;
            player.invulnerable = 60;
            particles.burst(player.x + player.w / 2.0, player.y + player.h / 2.0, new Color(127, 29, 29), 25);
            particles.burst(player.x + player.w / 2.0, player.y + player.h / 2.0, new Color(239, 68, 68), 15);

            if (lives <= 0) {
                stopLoop();
                screen = Screen.GAME_OVER;
                keys.clear();
            } else {
                Level level = levels.get(currentLevelIndex);
                player.reset(level.playerStartX, level.playerStartY);
                keys.clear();
            }
        }

        private void levelCleared() {
            stopLoop();
            audio.playLevelClear();
            particles.burst(portal.x, portal.y, new Color(153, 27, 27), 40);

            lastClearTime = getElapsedSeconds();
            Double currentBest = bestTimes[currentLevelIndex];
            lastClearWasBest = currentBest == null || lastClearTime < currentBest;
            if (lastClearWasBest) {
                bestTimes[currentLevelIndex] = lastClearTime;
            }

            keys.clear();
            if (currentLevelIndex + 1 < levels.size()) {
                screen = Screen.LEVEL_COMPLETE;
            } else {
                screen = Screen.VICTORY;
            }
        }

        private double getElapsedSeconds() {
            long totalMs = levelAccumulatedMs;
            if (timerRunning) {
                totalMs += System.currentTimeMillis() - levelStartTimeMs;
            }
            return Math.round((totalMs / 1000.0) * 10.0) / 10.0;
        }

        private boolean overlaps(double ax, double ay, double aw, double ah,
                                 double bx, double by, double bw, double bh) {
            return ax + aw > bx && ax < bx + bw && ay + ah > by && ay < by + bh;
        }

        @Override
        protected void paintComponent(Graphics graphics) {
            super.paintComponent(graphics);
            Graphics2D g = (Graphics2D) graphics.create();
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

            scale = Math.min(getWidth() / (double) VIEW_WIDTH, getHeight() / (double) VIEW_HEIGHT);
            offsetX = (getWidth() - VIEW_WIDTH * scale) / 2.0;
            offsetY = (getHeight() - VIEW_HEIGHT * scale) / 2.0;

            g.setColor(new Color(8, 1, 2));
            g.fillRect(0, 0, getWidth(), getHeight());
            g.translate(offsetX, offsetY);
            g.scale(scale, scale);

            drawFrame(g);
            g.dispose();
        }

        private void drawFrame(Graphics2D g) {
            drawBackground(g);
            drawHeader(g);
            drawWorldShell(g);
            drawWorld(g);
            drawControlsHint(g);
            drawAudioAndPauseButtons(g);

            if (screen != Screen.PLAYING) {
                drawOverlay(g);
            }
        }

        private void drawBackground(Graphics2D g) {
            for (int y = 0; y < VIEW_HEIGHT; y++) {
                float t = y / (float) VIEW_HEIGHT;
                int r = (int) (46 * (1 - t) + 8 * t);
                int b = (int) (12 * (1 - t) + 2 * t);
                g.setColor(new Color(r, 3, b));
                g.drawLine(0, y, VIEW_WIDTH, y);
            }
        }

        private void drawHeader(Graphics2D g) {
            g.setColor(new Color(12, 10, 9, 220));
            g.fillRoundRect(20, 12, 760, HEADER_HEIGHT, 20, 20);
            g.setColor(new Color(127, 29, 29, 120));
            g.drawRoundRect(20, 12, 760, HEADER_HEIGHT, 20, 20);

            g.setFont(new Font(Font.SERIF, Font.BOLD, 28));
            drawCenteredText(g, "BLOOD QUEST", VIEW_WIDTH / 2, 49, new Color(220, 38, 38));

            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 13));
            g.setColor(new Color(248, 113, 113));
            g.drawString("CHAMBER " + (currentLevelIndex + 1), 38, 45);
            g.drawString("DROPS " + score, 595, 35);
            g.drawString("FPS " + fps, 595, 54);

            for (int i = 0; i < 3; i++) {
                drawHeart(g, 704 + i * 22, 39, i < lives);
            }
        }

        private void drawWorldShell(Graphics2D g) {
            g.setColor(new Color(5, 0, 0));
            g.fillRoundRect(20, WORLD_TOP, 760, WORLD_HEIGHT, 18, 18);
            g.setStroke(new BasicStroke(3));
            g.setColor(new Color(127, 29, 29));
            g.drawRoundRect(20, WORLD_TOP, 760, WORLD_HEIGHT, 18, 18);
            g.setStroke(new BasicStroke(1));
        }

        private void drawWorld(Graphics2D outer) {
            Graphics2D g = (Graphics2D) outer.create();
            g.clipRect(20, WORLD_TOP, 760, WORLD_HEIGHT);
            g.translate(20, WORLD_TOP);
            g.scale(760.0 / 800.0, 1.0);

            if (screenShake > 0) {
                double dx = (random.nextDouble() - 0.5) * screenShake;
                double dy = (random.nextDouble() - 0.5) * screenShake;
                g.translate(dx, dy);
            }

            drawDungeon(g);
            for (Hazard hazard : hazards) {
                hazard.draw(g);
            }
            for (Spring spring : springs) {
                spring.draw(g);
            }
            for (Platform platform : platforms) {
                platform.draw(g);
            }
            for (Collectible collectible : collectibles) {
                collectible.draw(g);
            }
            for (Enemy enemy : enemies) {
                enemy.draw(g);
            }
            portal.draw(g);
            player.draw(g);
            particles.draw(g);

            g.dispose();
        }

        private void drawDungeon(Graphics2D g) {
            for (int y = 0; y < WORLD_HEIGHT; y++) {
                float t = y / (float) WORLD_HEIGHT;
                g.setColor(new Color((int) (10 + 12 * (1 - t)), 2, 3));
                g.drawLine(0, y, 800, y);
            }

            g.setColor(new Color(127, 29, 29, 18));
            for (int x = 0; x < 800; x += 45) {
                g.drawLine(x, 0, x, WORLD_HEIGHT);
            }
            for (int y = 0; y < WORLD_HEIGHT; y += 45) {
                g.drawLine(0, y, 800, y);
            }
        }

        private void drawControlsHint(Graphics2D g) {
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 12));
            g.setColor(new Color(120, 113, 108));
            drawCenteredText(g, "A/D or arrows: move    W/Space/Up: jump    P/Esc: pause    M: mute",
                    VIEW_WIDTH / 2, 552, new Color(120, 113, 108));
            g.setFont(new Font(Font.SERIF, Font.PLAIN, 13));
            drawCenteredText(g, "Forged with synthesized retro audio and Java2D stonework.",
                    VIEW_WIDTH / 2, 580, new Color(87, 83, 78));
        }

        private void drawAudioAndPauseButtons(Graphics2D g) {
            if (screen == Screen.PLAYING) {
                drawPill(g, 510, 22, 160, 34, "time elapsed: " + String.format("%.1fs", getElapsedSeconds()),
                        new Color(8, 8, 8, 230), new Color(127, 29, 29));
                drawIconButton(g, 686, 22, "II", new Color(220, 38, 38));
            }
            drawIconButton(g, 730, 22, audio.muted ? "X" : "S", audio.muted ? new Color(127, 29, 29) : new Color(220, 38, 38));
        }

        private void drawOverlay(Graphics2D g) {
            g.setColor(new Color(5, 5, 5, 230));
            g.fillRoundRect(20, WORLD_TOP, 760, WORLD_HEIGHT, 18, 18);

            switch (screen) {
                case START:
                    drawTitleScreen(g);
                    break;
                case LEVEL_COMPLETE:
                    drawLevelCompleteScreen(g);
                    break;
                case GAME_OVER:
                    drawGameOverScreen(g);
                    break;
                case VICTORY:
                    drawVictoryScreen(g);
                    break;
                case PAUSED:
                    drawPauseScreen(g);
                    break;
                default:
                    break;
            }
        }

        private void drawTitleScreen(Graphics2D g) {
            g.setFont(new Font(Font.SERIF, Font.BOLD, 46));
            drawCenteredText(g, "BLOOD QUEST", VIEW_WIDTH / 2, 185, new Color(220, 38, 38));
            g.setFont(new Font(Font.SERIF, Font.PLAIN, 19));
            drawCenteredText(g, "Traverse cursed catacombs, collect blood drops, crush shadow beasts,",
                    VIEW_WIDTH / 2, 232, new Color(168, 162, 158));
            drawCenteredText(g, "and reach the blood vortex in each chamber.",
                    VIEW_WIDTH / 2, 258, new Color(168, 162, 158));
            drawButton(g, 285, 345, 230, 48, "BEGIN THE HUNT", true);
        }

        private void drawLevelCompleteScreen(Graphics2D g) {
            g.setFont(new Font(Font.SERIF, Font.BOLD, 36));
            drawCenteredText(g, "CHAMBER PURIFIED", VIEW_WIDTH / 2, 180, new Color(239, 68, 68));
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 16));
            drawCenteredText(g, "Your Time: " + String.format("%.1fs", lastClearTime),
                    VIEW_WIDTH / 2, 245, new Color(231, 229, 228));
            Double best = bestTimes[currentLevelIndex];
            String bestLabel = "Best Time: " + String.format("%.1fs", best == null ? lastClearTime : best);
            if (lastClearWasBest) {
                bestLabel += "  NEW BEST";
            }
            drawCenteredText(g, bestLabel, VIEW_WIDTH / 2, 275, new Color(234, 179, 8));
            drawButton(g, 285, 360, 230, 46, "DESCEND DEEPER", true);
        }

        private void drawGameOverScreen(Graphics2D g) {
            g.setFont(new Font(Font.SERIF, Font.BOLD, 38));
            drawCenteredText(g, "YOUR SOUL FADES", VIEW_WIDTH / 2, 205, new Color(153, 27, 27));
            g.setFont(new Font(Font.SERIF, Font.PLAIN, 19));
            drawCenteredText(g, "No remaining vitality. Try again from the first gate?",
                    VIEW_WIDTH / 2, 260, new Color(168, 162, 158));
            drawButton(g, 285, 360, 230, 46, "RESURRECT", true);
        }

        private void drawVictoryScreen(Graphics2D g) {
            g.setFont(new Font(Font.SERIF, Font.BOLD, 38));
            drawCenteredText(g, "THE THRONE IS YOURS", VIEW_WIDTH / 2, 170, new Color(239, 68, 68));
            g.setFont(new Font(Font.SERIF, Font.PLAIN, 19));
            drawCenteredText(g, "You harvested all blood essence and conquered the underworld.",
                    VIEW_WIDTH / 2, 220, new Color(168, 162, 158));
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 15));
            drawCenteredText(g, "Blood Drops: " + score, VIEW_WIDTH / 2, 270, new Color(248, 113, 113));
            drawCenteredText(g, "Chamber Time: " + String.format("%.1fs", lastClearTime),
                    VIEW_WIDTH / 2, 300, new Color(231, 229, 228));
            Double best = bestTimes[currentLevelIndex];
            drawCenteredText(g, "Best Time: " + String.format("%.1fs", best == null ? lastClearTime : best),
                    VIEW_WIDTH / 2, 330, new Color(234, 179, 8));
            drawButton(g, 285, 385, 230, 46, "RESTART HUNT", true);
        }

        private void drawPauseScreen(Graphics2D g) {
            g.setFont(new Font(Font.SERIF, Font.BOLD, 38));
            drawCenteredText(g, "HUNT PAUSED", VIEW_WIDTH / 2, 205, new Color(239, 68, 68));
            g.setFont(new Font(Font.SERIF, Font.PLAIN, 19));
            drawCenteredText(g, "The catacombs fall silent...", VIEW_WIDTH / 2, 260, new Color(168, 162, 158));
            drawButton(g, 205, 360, 180, 46, "RESUME", true);
            drawButton(g, 415, 360, 180, 46, "RETURN", false);
        }

        private void drawButton(Graphics2D g, int x, int y, int w, int h, String label, boolean red) {
            Color fill = red ? new Color(127, 29, 29) : new Color(28, 25, 23);
            Color border = red ? new Color(248, 113, 113) : new Color(68, 64, 60);
            g.setColor(fill);
            g.fillRoundRect(x, y, w, h, 14, 14);
            g.setColor(border);
            g.setStroke(new BasicStroke(2));
            g.drawRoundRect(x, y, w, h, 14, 14);
            g.setStroke(new BasicStroke(1));
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 14));
            drawCenteredText(g, label, x + w / 2, y + h / 2 + 5, new Color(245, 245, 244));
        }

        private void drawPill(Graphics2D g, int x, int y, int w, int h, String label, Color fill, Color border) {
            g.setColor(fill);
            g.fillRoundRect(x, y, w, h, h, h);
            g.setColor(border);
            g.drawRoundRect(x, y, w, h, h, h);
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 10));
            drawCenteredText(g, label, x + w / 2, y + 22, new Color(248, 113, 113));
        }

        private void drawIconButton(Graphics2D g, int x, int y, String label, Color color) {
            g.setColor(new Color(28, 25, 23, 230));
            g.fillOval(x, y, 34, 34);
            g.setColor(new Color(68, 64, 60));
            g.drawOval(x, y, 34, 34);
            g.setFont(new Font(Font.MONOSPACED, Font.BOLD, 13));
            drawCenteredText(g, label, x + 17, y + 22, color);
        }

        private void drawHeart(Graphics2D g, int x, int y, boolean full) {
            g.setColor(full ? new Color(220, 38, 38) : new Color(41, 37, 36));
            int[] xs = {x, x + 8, x + 16, x + 8};
            int[] ys = {y, y - 9, y, y + 10};
            g.fillPolygon(xs, ys, 4);
            g.fillOval(x, y - 8, 9, 9);
            g.fillOval(x + 7, y - 8, 9, 9);
        }

        private void drawCenteredText(Graphics2D g, String text, int x, int y, Color color) {
            FontMetrics metrics = g.getFontMetrics();
            g.setColor(color);
            g.drawString(text, x - metrics.stringWidth(text) / 2, y);
        }
    }

    private static final class InputState {
        boolean left;
        boolean right;
        boolean up;

        void clear() {
            left = false;
            right = false;
            up = false;
        }
    }

    private static final class Player {
        double x = 100;
        double y = 300;
        double w = 24;
        double h = 32;
        double vx = 0;
        double vy = 0;
        boolean grounded = false;
        boolean facingRight = true;
        double stretchX = 1.0;
        double stretchY = 1.0;
        int invulnerable = 0;
        Color activeColor = new Color(185, 28, 28);

        void reset(double startX, double startY) {
            x = startX;
            y = startY;
            vx = 0;
            vy = 0;
            grounded = false;
            stretchX = 1;
            stretchY = 1;
            invulnerable = 60;
        }

        void update(List<Platform> platforms, List<Spring> springs, InputState keys,
                    AudioManager audio, ParticleSystem particles) {
            if (invulnerable > 0) {
                invulnerable--;
            }

            Platform standingPlatform = null;
            if (grounded) {
                for (Platform platform : platforms) {
                    if (x + w > platform.x && x < platform.x + platform.w
                            && Math.abs((y + h) - platform.y) < 2) {
                        standingPlatform = platform;
                    }
                }
            }

            activeColor = standingPlatform != null && standingPlatform.type == PlatformType.ICE
                    ? new Color(220, 38, 38)
                    : new Color(153, 27, 27);

            if (keys.left) {
                vx -= GamePanel.ACCEL;
                facingRight = false;
            } else if (keys.right) {
                vx += GamePanel.ACCEL;
                facingRight = true;
            } else {
                vx *= GamePanel.FRICTION;
                if (Math.abs(vx) < 0.1) {
                    vx = 0;
                }
            }

            vx = Math.max(-GamePanel.MAX_SPEED, Math.min(GamePanel.MAX_SPEED, vx));
            vy += GamePanel.GRAVITY;

            if (keys.up && grounded) {
                vy = GamePanel.JUMP_FORCE;
                grounded = false;
                stretchX = 0.7;
                stretchY = 1.3;
                audio.playJump();
                particles.burst(x + w / 2.0, y + h, new Color(127, 29, 29), 6);
            }

            stretchX += (1 - stretchX) * 0.15;
            stretchY += (1 - stretchY) * 0.15;

            x += vx;
            checkPlatformCollisions(platforms, true);
            y += vy;
            grounded = false;
            checkPlatformCollisions(platforms, false);

            for (Spring spring : springs) {
                if (x + w > spring.x && x < spring.x + spring.w
                        && y + h >= spring.y && y + h - vy <= spring.y + 10) {
                    y = spring.y - h;
                    vy = GamePanel.SPRING_BOOST;
                    grounded = false;
                    stretchX = 0.5;
                    stretchY = 1.5;
                    audio.playSpring();
                    particles.burst(spring.x + spring.w / 2.0, spring.y, new Color(153, 27, 27), 12);
                }
            }

            if (x < 0) {
                x = 0;
            }
            if (x + w > 800) {
                x = 800 - w;
            }
            if (y > GamePanel.WORLD_HEIGHT) {
                invulnerable = 0;
            }
        }

        private void checkPlatformCollisions(List<Platform> platforms, boolean horizontal) {
            for (Platform platform : platforms) {
                if (x + w > platform.x && x < platform.x + platform.w
                        && y + h > platform.y && y < platform.y + platform.h) {
                    if (horizontal) {
                        if (vx > 0) {
                            x = platform.x - w;
                        } else if (vx < 0) {
                            x = platform.x + platform.w;
                        }
                        vx = 0;
                    } else {
                        if (vy > 0) {
                            y = platform.y - h;
                            vy = 0;
                            grounded = true;
                            if (platform.type == PlatformType.MOVING) {
                                x += platform.dx;
                                y += platform.dy;
                            }
                        } else if (vy < 0) {
                            y = platform.y + platform.h;
                            vy = 0;
                        }
                    }
                }
            }
        }

        void draw(Graphics2D g) {
            if (invulnerable > 0 && (invulnerable / 4) % 2 == 0) {
                return;
            }

            AffineTransform original = g.getTransform();
            g.translate(x + w / 2.0, y + h / 2.0);
            g.scale(stretchX, stretchY);
            g.setColor(activeColor);
            g.fillRoundRect((int) (-w / 2), (int) (-h / 2), (int) w, (int) h, 4, 4);
            g.setColor(new Color(39, 39, 42));
            g.setStroke(new BasicStroke(2));
            g.drawRect((int) (-w / 2), (int) (-h / 2), (int) w, (int) h);
            g.setStroke(new BasicStroke(1));

            g.setColor(new Color(28, 25, 23));
            g.fillRect(facingRight ? 0 : -10, -10, 10, 6);
            g.setColor(new Color(254, 240, 138));
            g.fillRect(facingRight ? 2 : -8, -8, 6, 2);
            g.setTransform(original);
        }
    }

    private enum PlatformType {
        STANDARD,
        MOVING,
        ICE
    }

    private static final class Platform {
        double x;
        double y;
        final double w;
        final double h;
        final PlatformType type;
        double dx;
        double dy;
        final double minX;
        final double maxX;
        final double minY;
        final double maxY;

        Platform(double x, double y, double w, double h, PlatformType type) {
            this(x, y, w, h, type, 0, 0, x, x, y, y);
        }

        Platform(double x, double y, double w, double h, PlatformType type,
                 double dx, double dy, double minX, double maxX, double minY, double maxY) {
            this.x = x;
            this.y = y;
            this.w = w;
            this.h = h;
            this.type = type;
            this.dx = dx;
            this.dy = dy;
            this.minX = minX;
            this.maxX = maxX;
            this.minY = minY;
            this.maxY = maxY;
        }

        Platform copy() {
            return new Platform(x, y, w, h, type, dx, dy, minX, maxX, minY, maxY);
        }

        void update() {
            if (type != PlatformType.MOVING) {
                return;
            }
            if (dx != 0) {
                x += dx;
                if (x < minX || x > maxX) {
                    dx *= -1;
                }
            }
            if (dy != 0) {
                y += dy;
                if (y < minY || y > maxY) {
                    dy *= -1;
                }
            }
        }

        void draw(Graphics2D g) {
            Color fill = new Color(63, 63, 70);
            Color stroke = new Color(24, 24, 27);
            if (type == PlatformType.MOVING) {
                fill = new Color(69, 10, 10);
                stroke = new Color(153, 27, 27);
            } else if (type == PlatformType.ICE) {
                fill = new Color(127, 29, 29);
                stroke = new Color(248, 113, 113);
            }

            g.setColor(fill);
            g.fillRoundRect((int) x, (int) y, (int) w, (int) h, 5, 5);
            g.setColor(stroke);
            g.setStroke(new BasicStroke(2));
            g.drawRect((int) x, (int) y, (int) w, (int) h);
            g.setStroke(new BasicStroke(1));

            g.setColor(new Color(0, 0, 0, 90));
            for (int bx = (int) x + 30; bx < x + w; bx += 30) {
                g.drawLine(bx, (int) y, bx, (int) (y + h));
            }
        }
    }

    private static final class Spring {
        final double x;
        final double y;
        final double w;
        final double h;

        Spring(double x, double y, double w, double h) {
            this.x = x;
            this.y = y;
            this.w = w;
            this.h = h;
        }

        Spring copy() {
            return new Spring(x, y, w, h);
        }

        void draw(Graphics2D g) {
            g.setColor(new Color(228, 228, 231));
            g.fillRect((int) x, (int) (y + h - 5), (int) w, 5);
            g.fillRect((int) (x + 4), (int) (y + 4), (int) (w - 8), 4);
            g.fillRect((int) (x + 8), (int) (y + 8), (int) (w - 16), 4);
            g.setColor(new Color(153, 27, 27));
            g.fillRect((int) (x - 1), (int) y, (int) (w + 2), 4);
        }
    }

    private static final class Hazard {
        final double x;
        final double y;
        final double w;
        final double h;
        final boolean inverted;

        Hazard(double x, double y, double w, double h) {
            this(x, y, w, h, false);
        }

        Hazard(double x, double y, double w, double h, boolean inverted) {
            this.x = x;
            this.y = y;
            this.w = w;
            this.h = h;
            this.inverted = inverted;
        }

        Hazard copy() {
            return new Hazard(x, y, w, h, inverted);
        }

        void draw(Graphics2D g) {
            int spikeCount = Math.max(1, (int) Math.floor(w / 12.0));
            double spikeWidth = w / spikeCount;

            g.setColor(new Color(39, 39, 42));
            for (int i = 0; i < spikeCount; i++) {
                int[] xs = {
                    (int) (x + i * spikeWidth),
                    (int) (x + (i + 0.5) * spikeWidth),
                    (int) (x + (i + 1) * spikeWidth)
                };
                int[] ys = inverted
                        ? new int[] {(int) y, (int) (y + h), (int) y}
                        : new int[] {(int) (y + h), (int) y, (int) (y + h)};
                g.fillPolygon(xs, ys, 3);
                g.setColor(new Color(153, 27, 27));
                g.drawPolygon(xs, ys, 3);
                g.setColor(new Color(39, 39, 42));
            }
        }
    }

    private static final class Collectible {
        final double x;
        final double y;
        boolean collected;

        Collectible(double x, double y) {
            this.x = x;
            this.y = y;
        }

        Collectible copy() {
            return new Collectible(x, y);
        }

        void draw(Graphics2D g) {
            if (collected) {
                return;
            }

            double hover = Math.sin(System.currentTimeMillis() * 0.007 + x) * 2;
            AffineTransform original = g.getTransform();
            g.translate(x, y + hover);
            g.setColor(new Color(185, 28, 28));
            int[] xs = {0, 5, 0, -5};
            int[] ys = {-8, 1, 8, 1};
            g.fillPolygon(xs, ys, 4);
            g.setColor(new Color(252, 165, 165));
            g.fillOval(-2, 1, 3, 3);
            g.setTransform(original);
        }
    }

    private static final class Enemy {
        double x;
        final double y;
        final double w;
        final double h;
        double dx;
        final double limitLeft;
        final double limitRight;
        boolean dead;

        Enemy(double x, double y, double w, double h, double dx, double limitLeft, double limitRight) {
            this.x = x;
            this.y = y;
            this.w = w;
            this.h = h;
            this.dx = dx;
            this.limitLeft = limitLeft;
            this.limitRight = limitRight;
        }

        Enemy copy() {
            return new Enemy(x, y, w, h, dx, limitLeft, limitRight);
        }

        void update() {
            x += dx;
            if (x < limitLeft || x + w > limitRight) {
                dx *= -1;
            }
        }

        void draw(Graphics2D g) {
            if (dead) {
                return;
            }
            g.setColor(new Color(9, 9, 11));
            g.fillRoundRect((int) x, (int) y, (int) w, (int) h, 8, 8);
            g.setColor(new Color(82, 82, 91));
            g.drawRect((int) x + 2, (int) y + 2, (int) w - 4, (int) h - 4);
            g.setColor(new Color(239, 68, 68));
            int eyeX = dx > 0 ? (int) (x + 14) : (int) (x + 4);
            g.fillOval(eyeX, (int) y + 6, 6, 6);
        }
    }

    private static final class Portal {
        final double x;
        final double y;
        double hoverOffset;

        Portal(double x, double y) {
            this.x = x;
            this.y = y;
        }

        void draw(Graphics2D g) {
            AffineTransform original = g.getTransform();
            double hover = Math.sin(hoverOffset) * 5;
            g.translate(x, y + hover);
            long now = System.currentTimeMillis();

            g.setColor(new Color(69, 10, 10, 180));
            g.fillOval(-28, -28, 56, 56);
            g.setColor(new Color(185, 28, 28, 220));
            g.fillOval(-20, -20, 40, 40);
            g.setColor(new Color(252, 165, 165));
            g.fillOval(-6, -6, 12, 12);

            g.rotate(-now * 0.0015);
            g.setColor(new Color(24, 24, 27));
            g.setStroke(new BasicStroke(3));
            g.drawOval(-20, -20, 40, 40);
            g.rotate(now * 0.003);
            g.setColor(new Color(153, 27, 27));
            g.setStroke(new BasicStroke(2));
            g.drawRect(-10, -10, 20, 20);
            g.setStroke(new BasicStroke(1));
            g.setTransform(original);
        }
    }

    private static final class Particle {
        double x;
        double y;
        double vx;
        double vy;
        double size;
        double life = 1.0;
        final double decay;
        final Color color;

        Particle(double x, double y, Color color, Random random) {
            this.x = x;
            this.y = y;
            vx = (random.nextDouble() - 0.5) * 6;
            vy = (random.nextDouble() - 0.5) * 6 - 2;
            size = random.nextDouble() * 4 + 2;
            decay = random.nextDouble() * 0.05 + 0.02;
            this.color = color;
        }

        void update() {
            x += vx;
            y += vy;
            vy += 0.12;
            life -= decay;
        }

        void draw(Graphics2D g) {
            int alpha = Math.max(0, Math.min(255, (int) (255 * life)));
            g.setColor(new Color(color.getRed(), color.getGreen(), color.getBlue(), alpha));
            g.fillRect((int) (x - size / 2.0), (int) (y - size / 2.0), (int) size, (int) size);
        }
    }

    private static final class ParticleSystem {
        private final List<Particle> particles = new ArrayList<>();
        private final Random random = new Random();

        void burst(double x, double y, Color color, int count) {
            for (int i = 0; i < count; i++) {
                particles.add(new Particle(x, y, color, random));
            }
        }

        void update() {
            for (int i = particles.size() - 1; i >= 0; i--) {
                Particle particle = particles.get(i);
                particle.update();
                if (particle.life <= 0) {
                    particles.remove(i);
                }
            }
        }

        void draw(Graphics2D g) {
            for (Particle particle : particles) {
                particle.draw(g);
            }
        }

        void clear() {
            particles.clear();
        }
    }

    private static final class AudioManager {
        boolean muted = false;

        void init() {
            // No persistent audio context is required for Java's sampled API.
        }

        void toggleMuted() {
            muted = !muted;
        }

        void playJump() {
            tone(120, 450, 0.18, 0.20, "triangle");
        }

        void playCoin() {
            sequence(new double[] {440, 554.37}, new double[] {0.08, 0.22}, 0.12, "sine");
        }

        void playSpring() {
            tone(90, 650, 0.35, 0.12, "saw");
        }

        void playHurt() {
            tone(220, 50, 0.45, 0.25, "saw");
        }

        void playEnemySquash() {
            tone(180, 80, 0.20, 0.20, "square");
        }

        void playLevelClear() {
            sequence(new double[] {220, 277.18, 329.63, 440}, new double[] {0.12, 0.12, 0.12, 0.25}, 0.15, "triangle");
        }

        private void sequence(double[] frequencies, double[] durations, double volume, String wave) {
            if (muted) {
                return;
            }
            new Thread(() -> {
                for (int i = 0; i < frequencies.length; i++) {
                    writeTone(frequencies[i], frequencies[i], durations[i], volume, wave);
                }
            }, "blood-quest-audio-sequence").start();
        }

        private void tone(double startFrequency, double endFrequency, double durationSeconds, double volume, String wave) {
            if (muted) {
                return;
            }
            new Thread(() -> writeTone(startFrequency, endFrequency, durationSeconds, volume, wave),
                    "blood-quest-audio-tone").start();
        }

        private void writeTone(double startFrequency, double endFrequency, double durationSeconds,
                               double volume, String wave) {
            final float sampleRate = 44100f;
            int sampleCount = Math.max(1, (int) (durationSeconds * sampleRate));
            byte[] buffer = new byte[sampleCount * 2];

            for (int i = 0; i < sampleCount; i++) {
                double t = i / sampleRate;
                double progress = i / (double) sampleCount;
                double frequency = startFrequency + (endFrequency - startFrequency) * progress;
                double phase = 2.0 * Math.PI * frequency * t;
                double sample = waveform(phase, wave);
                double envelope = Math.max(0.0, 1.0 - progress);
                short value = (short) (sample * envelope * volume * Short.MAX_VALUE);
                buffer[i * 2] = (byte) (value & 0xff);
                buffer[i * 2 + 1] = (byte) ((value >> 8) & 0xff);
            }

            AudioFormat format = new AudioFormat(sampleRate, 16, 1, true, false);
            try (SourceDataLine line = AudioSystem.getSourceDataLine(format)) {
                line.open(format);
                line.start();
                line.write(buffer, 0, buffer.length);
                line.drain();
            } catch (Exception ignored) {
                // Some headless/cloud systems do not expose an audio device; gameplay should continue.
            }
        }

        private double waveform(double phase, String wave) {
            switch (wave) {
                case "square":
                    return Math.sin(phase) >= 0 ? 1.0 : -1.0;
                case "saw":
                    return 2.0 * (phase / (2.0 * Math.PI) - Math.floor(0.5 + phase / (2.0 * Math.PI)));
                case "triangle":
                    return 2.0 * Math.abs(2.0 * (phase / (2.0 * Math.PI) - Math.floor(phase / (2.0 * Math.PI) + 0.5))) - 1.0;
                case "sine":
                default:
                    return Math.sin(phase);
            }
        }
    }

    private static final class Level {
        final double playerStartX;
        final double playerStartY;
        final double exitX;
        final double exitY;
        final List<Platform> platforms = new ArrayList<>();
        final List<Spring> springs = new ArrayList<>();
        final List<Hazard> hazards = new ArrayList<>();
        final List<Collectible> collectibles = new ArrayList<>();
        final List<Enemy> enemies = new ArrayList<>();

        Level(double playerStartX, double playerStartY, double exitX, double exitY) {
            this.playerStartX = playerStartX;
            this.playerStartY = playerStartY;
            this.exitX = exitX;
            this.exitY = exitY;
        }

        List<Platform> copyPlatforms() {
            List<Platform> copy = new ArrayList<>();
            for (Platform platform : platforms) {
                copy.add(platform.copy());
            }
            return copy;
        }

        List<Spring> copySprings() {
            List<Spring> copy = new ArrayList<>();
            for (Spring spring : springs) {
                copy.add(spring.copy());
            }
            return copy;
        }

        List<Hazard> copyHazards() {
            List<Hazard> copy = new ArrayList<>();
            for (Hazard hazard : hazards) {
                copy.add(hazard.copy());
            }
            return copy;
        }

        List<Collectible> copyCollectibles() {
            List<Collectible> copy = new ArrayList<>();
            for (Collectible collectible : collectibles) {
                copy.add(collectible.copy());
            }
            return copy;
        }

        List<Enemy> copyEnemies() {
            List<Enemy> copy = new ArrayList<>();
            for (Enemy enemy : enemies) {
                copy.add(enemy.copy());
            }
            return copy;
        }
    }

    private static List<Level> createLevels() {
        List<Level> levels = new ArrayList<>();

        Level level1 = new Level(50, 350, 740, 150);
        level1.platforms.add(new Platform(0, 400, 350, 50, PlatformType.STANDARD));
        level1.platforms.add(new Platform(450, 400, 350, 50, PlatformType.STANDARD));
        level1.platforms.add(new Platform(200, 300, 100, 15, PlatformType.STANDARD));
        level1.platforms.add(new Platform(380, 240, 100, 15, PlatformType.STANDARD));
        level1.platforms.add(new Platform(520, 180, 100, 15, PlatformType.STANDARD));
        level1.platforms.add(new Platform(680, 200, 120, 250, PlatformType.STANDARD));
        level1.hazards.add(new Hazard(350, 435, 100, 15));
        level1.collectibles.add(new Collectible(250, 260));
        level1.collectibles.add(new Collectible(430, 200));
        level1.collectibles.add(new Collectible(570, 130));
        levels.add(level1);

        Level level2 = new Level(50, 350, 720, 120);
        level2.platforms.add(new Platform(0, 400, 150, 50, PlatformType.STANDARD));
        level2.platforms.add(new Platform(250, 320, 180, 20, PlatformType.STANDARD));
        level2.platforms.add(new Platform(520, 250, 150, 20, PlatformType.STANDARD));
        level2.platforms.add(new Platform(670, 160, 130, 300, PlatformType.STANDARD));
        level2.platforms.add(new Platform(140, 220, 80, 15, PlatformType.MOVING, 1.5, 0, 140, 300, 220, 220));
        level2.springs.add(new Spring(80, 385, 25, 15));
        level2.hazards.add(new Hazard(150, 435, 520, 15));
        level2.hazards.add(new Hazard(300, 305, 30, 15));
        level2.collectibles.add(new Collectible(92, 220));
        level2.collectibles.add(new Collectible(320, 270));
        level2.collectibles.add(new Collectible(600, 180));
        levels.add(level2);

        Level level3 = new Level(50, 350, 50, 100);
        level3.platforms.add(new Platform(0, 400, 220, 50, PlatformType.STANDARD));
        level3.platforms.add(new Platform(320, 320, 250, 20, PlatformType.STANDARD));
        level3.platforms.add(new Platform(650, 400, 150, 50, PlatformType.STANDARD));
        level3.platforms.add(new Platform(0, 150, 150, 20, PlatformType.STANDARD));
        level3.platforms.add(new Platform(200, 150, 80, 15, PlatformType.MOVING, 0, 1.2, 200, 200, 140, 280));
        level3.springs.add(new Spring(740, 385, 25, 15));
        level3.hazards.add(new Hazard(220, 435, 430, 15));
        level3.hazards.add(new Hazard(350, 0, 200, 20, true));
        level3.collectibles.add(new Collectible(440, 270));
        level3.collectibles.add(new Collectible(752, 200));
        level3.collectibles.add(new Collectible(240, 110));
        level3.enemies.add(new Enemy(380, 300, 20, 20, 1, 330, 540));
        levels.add(level3);

        Level level4 = new Level(50, 350, 730, 100);
        level4.platforms.add(new Platform(0, 400, 150, 50, PlatformType.STANDARD));
        level4.platforms.add(new Platform(200, 330, 120, 15, PlatformType.ICE));
        level4.platforms.add(new Platform(380, 260, 120, 15, PlatformType.ICE));
        level4.platforms.add(new Platform(550, 200, 120, 15, PlatformType.STANDARD));
        level4.platforms.add(new Platform(680, 140, 120, 310, PlatformType.STANDARD));
        level4.platforms.add(new Platform(0, 180, 100, 15, PlatformType.STANDARD));
        level4.platforms.add(new Platform(120, 120, 80, 15, PlatformType.STANDARD));
        level4.springs.add(new Spring(40, 165, 25, 15));
        level4.hazards.add(new Hazard(150, 435, 530, 15));
        level4.hazards.add(new Hazard(250, 315, 20, 15));
        level4.hazards.add(new Hazard(430, 245, 20, 15));
        level4.collectibles.add(new Collectible(260, 280));
        level4.collectibles.add(new Collectible(440, 200));
        level4.collectibles.add(new Collectible(160, 80));
        level4.enemies.add(new Enemy(570, 180, 20, 20, 1.5, 550, 660));
        levels.add(level4);

        Level level5 = new Level(50, 100, 730, 400);
        level5.platforms.add(new Platform(0, 150, 150, 20, PlatformType.STANDARD));
        level5.platforms.add(new Platform(180, 220, 120, 15, PlatformType.STANDARD));
        level5.platforms.add(new Platform(340, 300, 120, 15, PlatformType.STANDARD));
        level5.platforms.add(new Platform(490, 350, 120, 15, PlatformType.STANDARD));
        level5.platforms.add(new Platform(650, 450, 150, 50, PlatformType.STANDARD));
        level5.platforms.add(new Platform(100, 380, 150, 15, PlatformType.STANDARD));
        level5.springs.add(new Spring(210, 365, 25, 15));
        level5.hazards.add(new Hazard(0, 435, 650, 15));
        level5.hazards.add(new Hazard(380, 285, 30, 15));
        level5.hazards.add(new Hazard(530, 335, 30, 15));
        level5.collectibles.add(new Collectible(240, 170));
        level5.collectibles.add(new Collectible(400, 240));
        level5.collectibles.add(new Collectible(550, 290));
        level5.collectibles.add(new Collectible(140, 330));
        level5.enemies.add(new Enemy(120, 360, 20, 20, 2, 100, 240));
        level5.enemies.add(new Enemy(200, 200, 20, 20, 1.2, 180, 290));
        levels.add(level5);

        return levels;
    }
}
