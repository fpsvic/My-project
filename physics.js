// physics.js — ball movement, collisions, field boundaries

const FIELD    = { x: 60, y: 40, w: 680, h: 440 };
const GOAL_W   = 120;
const GOAL_D   = 22;
const BALL_R   = 9;
const PLAYER_R = 15;

const BALL_FRICTION  = 0.962;   // per-frame speed decay
const BALL_MIN_SPEED = 0.06;
const BALL_MAX_SPEED = 16;
const WALL_BOUNCE    = 0.52;
const KICK_COOLDOWN  = 0.20;    // seconds between kicks

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
  if (spd > max) { obj.vx = (obj.vx / spd) * max; obj.vy = (obj.vy / spd) * max; }
}

// Returns true if kick landed
function tryKick(kicker, ball, power, dt) {
  if ((kicker.kickCooldown || 0) > 0) return false;
  if (dist(kicker, ball) > PLAYER_R + BALL_R + 3) return false;

  const spd = Math.hypot(kicker.vx, kicker.vy);
  let kickDx, kickDy;

  if (spd > 0.4) {
    // Directed: blend player facing with ball-away direction
    const [pvx, pvy] = norm(kicker.vx, kicker.vy);
    const [bx, by]   = norm(ball.x - kicker.x, ball.y - kicker.y);
    kickDx = pvx * 0.75 + bx * 0.25;
    kickDy = pvy * 0.75 + by * 0.25;
    [kickDx, kickDy] = norm(kickDx, kickDy);
  } else {
    [kickDx, kickDy] = norm(ball.x - kicker.x, ball.y - kicker.y);
  }

  ball.vx = kickDx * power;
  ball.vy = kickDy * power;
  kicker.kickCooldown = KICK_COOLDOWN;
  return true;
}

// Push overlapping players apart
function separateCircles(a, b) {
  const d = dist(a, b);
  const minD = PLAYER_R * 2;
  if (d < minD && d > 0.01) {
    const push = (minD - d) / 2 + 0.5;
    const [nx, ny] = norm(b.x - a.x, b.y - a.y);
    a.x -= nx * push; a.y -= ny * push;
    b.x += nx * push; b.y += ny * push;
  }
}

// Returns 'player' (player team scored), 'ai' (ai scored), or null
function moveBall(ball) {
  ball.vx *= BALL_FRICTION;
  ball.vy *= BALL_FRICTION;
  if (Math.abs(ball.vx) < BALL_MIN_SPEED) ball.vx = 0;
  if (Math.abs(ball.vy) < BALL_MIN_SPEED) ball.vy = 0;
  capSpeed(ball, BALL_MAX_SPEED);

  ball.x += ball.vx;
  ball.y += ball.vy;

  const CY     = FIELD.y + FIELD.h / 2;
  const goalTop = CY - GOAL_W / 2;
  const goalBot = CY + GOAL_W / 2;

  if (ball.y - BALL_R < FIELD.y)            { ball.y = FIELD.y + BALL_R;            ball.vy =  Math.abs(ball.vy) * WALL_BOUNCE; }
  if (ball.y + BALL_R > FIELD.y + FIELD.h)  { ball.y = FIELD.y + FIELD.h - BALL_R;  ball.vy = -Math.abs(ball.vy) * WALL_BOUNCE; }

  if (ball.x - BALL_R < FIELD.x) {
    if (ball.y > goalTop && ball.y < goalBot) return 'ai';
    ball.x = FIELD.x + BALL_R;
    ball.vx = Math.abs(ball.vx) * WALL_BOUNCE;
  }
  if (ball.x + BALL_R > FIELD.x + FIELD.w) {
    if (ball.y > goalTop && ball.y < goalBot) return 'player';
    ball.x = FIELD.x + FIELD.w - BALL_R;
    ball.vx = -Math.abs(ball.vx) * WALL_BOUNCE;
  }

  return null;
}

function updateCooldowns(entities, dt) {
  for (const e of entities) if (e.kickCooldown > 0) e.kickCooldown -= dt;
}
