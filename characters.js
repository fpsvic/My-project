// characters.js — top-down human character rendering

const SKIN = ['#f5c89a', '#e8a87c', '#c68642', '#8d5524'];

function drawCharacter(ctx, x, y, angle, jerseyColor, shortsColor, skinTone, number, isPlayer, stamina) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  const R = 15;
  const headR = 7;

  // Drop shadow
  ctx.save();
  ctx.globalAlpha = 0.28;
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.ellipse(3, 5, R * 1.15, R * 0.42, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Boots
  ctx.fillStyle = '#111';
  ctx.beginPath(); ctx.ellipse(-5, R * 0.62, 4, 3, 0.25, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse( 5, R * 0.62, 4, 3, -0.25, 0, Math.PI * 2); ctx.fill();

  // Socks (white stripe above boots)
  ctx.fillStyle = '#eee';
  ctx.beginPath(); ctx.ellipse(-5, R * 0.44, 3.5, 3, 0, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse( 5, R * 0.44, 3.5, 3, 0, 0, Math.PI * 2); ctx.fill();

  // Shorts
  ctx.fillStyle = shortsColor;
  ctx.beginPath();
  ctx.ellipse(0, R * 0.28, R * 0.6, R * 0.52, 0, 0, Math.PI * 2);
  ctx.fill();

  // Jersey body
  const jGrad = ctx.createRadialGradient(-3, -2, 1, 0, 0, R * 0.82);
  jGrad.addColorStop(0, lighten(jerseyColor, 30));
  jGrad.addColorStop(1, jerseyColor);
  ctx.fillStyle = jGrad;
  ctx.beginPath();
  ctx.ellipse(0, -R * 0.06, R * 0.7, R * 0.82, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.25)';
  ctx.lineWidth = 1.2;
  ctx.stroke();

  // Jersey number
  ctx.fillStyle = 'rgba(255,255,255,0.92)';
  ctx.font = `bold ${number > 9 ? 6 : 7}px Arial`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(number, 0, -1);

  // Arms
  ctx.fillStyle = skinTone;
  ctx.beginPath(); ctx.ellipse(-R * 0.76,  0, 4, 3.2, 0.5,  0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.ellipse( R * 0.76,  0, 4, 3.2, -0.5, 0, Math.PI * 2); ctx.fill();

  // Neck
  ctx.fillStyle = skinTone;
  ctx.beginPath();
  ctx.ellipse(0, -R * 0.52, 3, 3, 0, 0, Math.PI * 2);
  ctx.fill();

  // Head
  const hGrad = ctx.createRadialGradient(-2, -R * 0.62 - 2, 1, 0, -R * 0.62, headR);
  hGrad.addColorStop(0, lighten(skinTone, 20));
  hGrad.addColorStop(1, skinTone);
  ctx.fillStyle = hGrad;
  ctx.beginPath();
  ctx.arc(0, -R * 0.62, headR, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = 'rgba(0,0,0,0.15)';
  ctx.lineWidth = 0.8;
  ctx.stroke();

  // Hair
  ctx.fillStyle = 'rgba(40,20,0,0.6)';
  ctx.beginPath();
  ctx.arc(0, -R * 0.62 - headR * 0.08, headR * 0.78, Math.PI * 0.9, Math.PI * 2.1);
  ctx.fill();

  // Eyes (two tiny dots)
  ctx.fillStyle = 'rgba(0,0,0,0.7)';
  ctx.beginPath(); ctx.arc(-2.5, -R * 0.62 + 1, 1, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc( 2.5, -R * 0.62 + 1, 1, 0, Math.PI * 2); ctx.fill();

  // Highlight on head
  ctx.fillStyle = 'rgba(255,255,255,0.22)';
  ctx.beginPath();
  ctx.ellipse(-2.2, -R * 0.62 - 3, headR * 0.32, headR * 0.2, -0.4, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();

  // Player indicator (outside rotation)
  if (isPlayer) {
    ctx.save();
    ctx.strokeStyle = '#ffff33';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 4]);
    ctx.globalAlpha = 0.85;
    ctx.beginPath();
    ctx.arc(x, y, R + 5, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
  }

  // Stamina bar (below character)
  if (stamina !== undefined) {
    const barW = 24, barH = 3;
    const bx = x - barW / 2, by = y + R + 4;
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(bx, by, barW, barH);
    const color = stamina > 0.5 ? '#44ff44' : stamina > 0.25 ? '#ffaa00' : '#ff3333';
    ctx.fillStyle = color;
    ctx.fillRect(bx, by, barW * stamina, barH);
  }
}

// Draw the soccer ball with hexagon patches
function drawBall(ctx, ball) {
  const { x, y } = ball;
  const R = 9;

  ctx.save();
  ctx.globalAlpha = 0.28;
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.ellipse(x + 3, y + 5, R * 1.1, R * 0.38, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Ball base with gradient
  const g = ctx.createRadialGradient(x - 3, y - 3, 1, x, y, R);
  g.addColorStop(0, '#ffffff');
  g.addColorStop(0.6, '#e8e8e8');
  g.addColorStop(1, '#b0b0b0');
  ctx.beginPath();
  ctx.arc(x, y, R, 0, Math.PI * 2);
  ctx.fillStyle = g;
  ctx.fill();
  ctx.strokeStyle = '#444';
  ctx.lineWidth = 1;
  ctx.stroke();

  // Black pentagon patches
  ctx.fillStyle = '#111';
  const patches = [
    [0, 0, R * 0.24],
    [0,      -R * 0.52, R * 0.18],
    [ R * 0.5, -R * 0.16, R * 0.18],
    [ R * 0.31,  R * 0.44, R * 0.18],
    [-R * 0.31,  R * 0.44, R * 0.18],
    [-R * 0.5, -R * 0.16, R * 0.18],
  ];
  for (const [px, py, pr] of patches) {
    ctx.beginPath(); ctx.arc(x + px, y + py, pr, 0, Math.PI * 2); ctx.fill();
  }

  // Shine
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.beginPath();
  ctx.ellipse(x - 3, y - 3, R * 0.28, R * 0.18, -0.5, 0, Math.PI * 2);
  ctx.fill();
}

function getFacingAngle(entity) {
  const spd = Math.hypot(entity.vx, entity.vy);
  if (spd > 0.25) entity.angle = Math.atan2(entity.vy, entity.vx) + Math.PI / 2;
  return entity.angle || Math.PI / 2;
}

// Lighten a hex color by amt (0–255)
function lighten(hex, amt) {
  let c = hex.replace('#','');
  if (c.length === 3) c = c.split('').map(x=>x+x).join('');
  const num = parseInt(c, 16);
  const r = Math.min(255, (num >> 16) + amt);
  const g = Math.min(255, ((num >> 8) & 0xff) + amt);
  const b = Math.min(255, (num & 0xff) + amt);
  return `rgb(${r},${g},${b})`;
}
