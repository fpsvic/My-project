// characters.js — top-down human character rendering

// Skin tones for variety
const SKIN = ['#f5c89a', '#e8a87c', '#c68642', '#8d5524'];

function drawShadow(ctx, x, y, r) {
  ctx.save();
  ctx.globalAlpha = 0.3;
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.ellipse(x + 4, y + 5, r * 1.1, r * 0.45, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

// Draw a top-down soccer player
// angle: direction facing in radians (0 = right, Math.PI/2 = down)
function drawCharacter(ctx, x, y, angle, jerseyColor, shortsColor, skinTone, number, isPlayer) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  const R = 15;   // body radius
  const headR = 7;
  const legR = 4;

  // --- Shadow ---
  drawShadow(ctx, 0, 0, R);

  // --- Legs (behind body, at bottom relative to facing) ---
  const legOffset = R * 0.55;
  const legSpread = 5;

  ctx.fillStyle = '#222';  // boot color
  // Left boot
  ctx.beginPath();
  ctx.ellipse(-legSpread, legOffset + 2, legR - 1, legR * 0.7, 0.3, 0, Math.PI * 2);
  ctx.fill();
  // Right boot
  ctx.beginPath();
  ctx.ellipse(legSpread, legOffset + 2, legR - 1, legR * 0.7, -0.3, 0, Math.PI * 2);
  ctx.fill();

  // --- Shorts ---
  ctx.fillStyle = shortsColor;
  ctx.beginPath();
  ctx.ellipse(0, legOffset * 0.4, R * 0.62, R * 0.55, 0, 0, Math.PI * 2);
  ctx.fill();

  // --- Body / Jersey ---
  ctx.fillStyle = jerseyColor;
  ctx.beginPath();
  ctx.ellipse(0, 0, R * 0.72, R * 0.85, 0, 0, Math.PI * 2);
  ctx.fill();

  // Jersey outline
  ctx.strokeStyle = isPlayer ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.3)';
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Jersey number
  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.font = `bold ${number > 9 ? 6 : 7}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(number, 0, 1);

  // --- Arms ---
  ctx.fillStyle = skinTone;
  ctx.beginPath();
  ctx.ellipse(-R * 0.78, 0, legR * 0.9, legR * 0.6, 0.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.ellipse(R * 0.78, 0, legR * 0.9, legR * 0.6, -0.5, 0, Math.PI * 2);
  ctx.fill();

  // --- Head ---
  // Head positioned slightly toward the facing direction (up = -y in rotated space)
  ctx.fillStyle = skinTone;
  ctx.beginPath();
  ctx.arc(0, -R * 0.6, headR, 0, Math.PI * 2);
  ctx.fill();

  // Hair (darker cap on top)
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.beginPath();
  ctx.arc(0, -R * 0.6 - headR * 0.1, headR * 0.75, Math.PI, Math.PI * 2);
  ctx.fill();

  // Highlight on head
  ctx.fillStyle = 'rgba(255,255,255,0.2)';
  ctx.beginPath();
  ctx.arc(-2, -R * 0.6 - 2, headR * 0.35, 0, Math.PI * 2);
  ctx.fill();

  // Player indicator ring
  if (isPlayer) {
    ctx.strokeStyle = '#ffff55';
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    ctx.arc(0, 0, R + 4, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  ctx.restore();
}

// Draw the soccer ball with pentagon patches
function drawBall(ctx, ball) {
  const { x, y } = ball;
  const R = 9;

  // Shadow
  ctx.save();
  ctx.globalAlpha = 0.3;
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.ellipse(x + 3, y + 4, R * 1.1, R * 0.4, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Base ball
  ctx.beginPath();
  ctx.arc(x, y, R, 0, Math.PI * 2);
  const grad = ctx.createRadialGradient(x - 3, y - 3, 1, x, y, R);
  grad.addColorStop(0, '#ffffff');
  grad.addColorStop(1, '#cccccc');
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.strokeStyle = '#333';
  ctx.lineWidth = 1;
  ctx.stroke();

  // Pentagon patches (simplified — 5 small dark spots)
  ctx.fillStyle = '#222';
  const patches = [
    [0, 0],
    [0, -R * 0.5],
    [R * 0.48, -R * 0.15],
    [R * 0.3, R * 0.42],
    [-R * 0.3, R * 0.42],
    [-R * 0.48, -R * 0.15],
  ];
  for (const [px, py] of patches) {
    ctx.beginPath();
    ctx.arc(x + px, y + py, R * 0.22, 0, Math.PI * 2);
    ctx.fill();
  }

  // Shine
  ctx.fillStyle = 'rgba(255,255,255,0.55)';
  ctx.beginPath();
  ctx.ellipse(x - 3, y - 3, R * 0.3, R * 0.2, -0.5, 0, Math.PI * 2);
  ctx.fill();
}

// Compute facing angle from velocity; fall back to last angle
function getFacingAngle(entity) {
  const spd = Math.hypot(entity.vx, entity.vy);
  if (spd > 0.3) {
    entity.angle = Math.atan2(entity.vy, entity.vx) + Math.PI / 2;
  }
  return entity.angle || Math.PI / 2;
}
