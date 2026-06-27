// physics.js — ball movement, collisions, field boundaries

const FIELD  = { x: 60, y: 40, w: 680, h: 440 };
const GOAL_W = 110;
const GOAL_D = 20;
const BALL_R = 9;
const PLAYER_R = 15;

const BALL_FRICTION   = 0.955;   // per-frame speed decay (higher = more slide)
const BALL_MIN_SPEED  = 0.08;    // stop completely below this
const BALL_MAX_SPEED  = 14;
const WALL_BOUNCE     = 0.55;    // energy kept on wall bounce
const KICK_COOLDOWN   = 0.18;    // seconds between kicks per player

function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function norm(dx, dy) {
  const l = Math.hypot(dx, dy) || 1;
  return [dx / l, dy / l];
}

function clampField(obj, r) {
  obj.x = Math.max(FIELD.x + r, Math.min(FIELD.x + FIELD.w - r, obj.x));
  obj.y = Math.max(FIELD.y + r, Math.min(FIELD.y + FIELD.h - r, obj.y));
}

function capSpeed(obj, max) {
  const spd = Math.hypot(obj.vx, obj.vy);
  if (spd > max) {
    obj.vx = (obj.vx / spd) * max;
    obj.vy = (obj.vy / spd) * max;
  }
}

// Attempt a kick — returns true if successful (respects cooldown)
function tryKick(kicker, ball, power, dt) {
  if ((kicker.kickCooldown || 0) > 0) return false;
  const d = dist(kicker, ball);
  if (d > PLAYER_R + BALL_R + 2) return false;

  // Only kick if player is facing toward the ball
  const toBallX = ball.x - kicker.x;
  const toBallY = ball.y - kicker.y;
  const speed = Math.hypot(kicker.vx, kicker.vy);

  let kickDx, kickDy;
  if (speed > 0.3) {
    // Directed kick: blend player direction with ball direction
    const [pvx, pvy] = norm(kicker.vx, kicker.vy);
    const [bx, by]   = norm(toBallX, toBallY);
    kickDx = pvx * 0.7 + bx * 0.3;
    kickDy = pvy * 0.7 + by * 0.3;
    [kickDx, kickDy] = norm(kickDx, kickDy);
  } else {
    [kickDx, kickDy] = norm(toBallX, toBallY);
  }

  ball.vx = kickDx * power;
  ball.vy = kickDy * power;
  kicker.kickCooldown = KICK_COOLDOWN;
  return true;
}

// Simple push-out for player-player collisions (no velocity transfer needed)
function separateCircles(a, b) {
  const d = dist(a, b);
  const minD = PLAYER_R * 2;
  if (d < minD && d > 0.01) {
    const overlap = (minD - d) / 2 + 0.5;
    const [nx, ny] = norm(b.x - a.x, b.y - a.y);
    a.x -= nx * overlap;
    a.y -= ny * overlap;
    b.x += nx * overlap;
    b.y += ny * overlap;
  }
}

function moveBall(ball, state) {
  // Apply friction
  ball.vx *= BALL_FRICTION;
  ball.vy *= BALL_FRICTION;
  if (Math.abs(ball.vx) < BALL_MIN_SPEED) ball.vx = 0;
  if (Math.abs(ball.vy) < BALL_MIN_SPEED) ball.vy = 0;
  capSpeed(ball, BALL_MAX_SPEED);

  ball.x += ball.vx;
  ball.y += ball.vy;

  const goalTop = 260 - GOAL_W / 2;   // canvas H/2 = 260
  const goalBot = 260 + GOAL_W / 2;

  // Top / bottom walls
  if (ball.y - BALL_R < FIELD.y) {
    ball.y = FIELD.y + BALL_R;
    ball.vy = Math.abs(ball.vy) * WALL_BOUNCE;
  }
  if (ball.y + BALL_R > FIELD.y + FIELD.h) {
    ball.y = FIELD.y + FIELD.h - BALL_R;
    ball.vy = -Math.abs(ball.vy) * WALL_BOUNCE;
  }

  // Left wall / goal
  if (ball.x - BALL_R < FIELD.x) {
    if (ball.y > goalTop && ball.y < goalBot) {
      return 'ai';   // AI scored
    }
    ball.x = FIELD.x + BALL_R;
    ball.vx = Math.abs(ball.vx) * WALL_BOUNCE;
  }

  // Right wall / goal
  if (ball.x + BALL_R > FIELD.x + FIELD.w) {
    if (ball.y > goalTop && ball.y < goalBot) {
      return 'player';  // Player scored
    }
    ball.x = FIELD.x + FIELD.w - BALL_R;
    ball.vx = -Math.abs(ball.vx) * WALL_BOUNCE;
  }

  return null;
}

function updateCooldowns(entities, dt) {
  for (const e of entities) {
    if (e.kickCooldown > 0) e.kickCooldown -= dt;
  }
}
