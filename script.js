const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// --- CUSTOM SVG GRAPHICS ---
const chestClosedSVG = `
<svg viewBox="0 0 100 100" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg">
    <path d="M 10 50 C 10 20, 90 20, 90 50 Z" fill="#A0522D" stroke="#3e1f06" stroke-width="3"/>
    <rect x="10" y="50" width="80" height="40" fill="#8B4513" stroke="#3e1f06" stroke-width="3" rx="3"/>
    <line x1="10" y1="65" x2="90" y2="65" stroke="#3e1f06" stroke-width="2"/>
    <line x1="10" y1="80" x2="90" y2="80" stroke="#3e1f06" stroke-width="2"/>
    <path d="M 25 50 C 25 30, 33 30, 33 50 Z" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <path d="M 67 50 C 67 30, 75 30, 75 50 Z" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <rect x="25" y="50" width="8" height="40" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <rect x="67" y="50" width="8" height="40" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <line x1="10" y1="50" x2="90" y2="50" stroke="#111" stroke-width="3"/>
    <circle cx="50" cy="50" r="8" fill="#f1c40f" stroke="#d35400" stroke-width="2"/>
    <rect x="47" y="50" width="6" height="8" fill="#f1c40f" stroke="#d35400" stroke-width="2"/>
    <circle cx="50" cy="52" r="2" fill="#111"/>
    <rect x="49" y="52" width="2" height="4" fill="#111"/>
</svg>`;

const chestOpenedSVG = `
<svg viewBox="0 0 100 100" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg">
    <path d="M 15 35 C 15 10, 85 10, 85 35 Z" fill="#A0522D" stroke="#3e1f06" stroke-width="3"/>
    <path d="M 28 35 C 28 15, 34 15, 34 35 Z" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <path d="M 66 35 C 66 15, 72 15, 72 35 Z" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <ellipse cx="50" cy="45" rx="35" ry="12" fill="#2a1403"/>
    <circle cx="35" cy="45" r="6" fill="#f1c40f"/>
    <circle cx="50" cy="42" r="7" fill="#f1c40f"/>
    <circle cx="65" cy="46" r="5" fill="#f1c40f"/>
    <polygon points="50,28 58,40 42,40" fill="#00e5ff" stroke="#00b8d4" stroke-width="1"/>
    <polygon points="30,35 36,45 24,45" fill="#00e5ff" stroke="#00b8d4" stroke-width="1"/>
    <polygon points="70,38 75,45 65,45" fill="#00e5ff" stroke="#00b8d4" stroke-width="1"/>
    <circle cx="42" cy="48" r="4" fill="#f1c40f"/>
    <circle cx="58" cy="46" r="4" fill="#f1c40f"/>
    <rect x="10" y="45" width="80" height="45" fill="#8B4513" stroke="#3e1f06" stroke-width="3" rx="3"/>
    <line x1="10" y1="60" x2="90" y2="60" stroke="#3e1f06" stroke-width="2"/>
    <line x1="10" y1="75" x2="90" y2="75" stroke="#3e1f06" stroke-width="2"/>
    <rect x="25" y="45" width="8" height="45" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <rect x="67" y="45" width="8" height="45" fill="#2c3e50" stroke="#111" stroke-width="2"/>
    <line x1="10" y1="45" x2="90" y2="45" stroke="#111" stroke-width="3"/>
    <path d="M 46 45 L 54 45 L 54 55 Q 50 58 46 55 Z" fill="#f1c40f" stroke="#d35400" stroke-width="2"/>
</svg>`;

const uiContainer = document.getElementById('ui');
const scoreEl = document.getElementById('score');
const healthEl = document.getElementById('health');
const levelEl = document.getElementById('levelDisplay');
const gemEl = document.getElementById('gemDisplay');

const startScreen = document.getElementById('startScreen');
const mapScreen = document.getElementById('mapScreen');
const mapContainer = document.getElementById('mapContainer');
const shopScreen = document.getElementById('shopScreen');
const nextLevelScreen = document.getElementById('nextLevelScreen');
const gameOverScreen = document.getElementById('gameOverScreen');
const rewardScreen = document.getElementById('rewardScreen');
const rewardChest = document.getElementById('rewardChest');
const pauseScreen = document.getElementById('pauseScreen');
const btnPause = document.getElementById('btnPause');

// Game State Variables
let gameState = 'START'; // START, MAP, SHOP, REWARD, PLAYING, PAUSED, NEXT_LEVEL, GAMEOVER
let score = 0;
let currentLevel = 1;
let activeLevel = 1;
let health = 5;
let bossPhase = false;
let bossesDefeated = 0;
let boss = null;
let bossProjectiles = [];
let arrows = [];
let targets = [];
let powerups = [];
let multiShotActive = false;
let multiShotTimer = 0;
let isCharging = false;
let chargeAmount = 0;
let mouseX = canvas.width / 2;
let mouseY = canvas.height / 2;

const GRAVITY = 0.15;
const PLAYER_X = 100;
let playerY = canvas.height / 2;
const PLAYER_SPEED = 6;
let keys = { ArrowUp: false, ArrowDown: false, w: false, s: false };
let lastTime = 0;

// Persistence
let gems = parseInt(localStorage.getItem('arrowFighterGems')) || 0;
let maxUnlockedLevel = parseInt(localStorage.getItem('arrowFighterMaxLevel')) || 1;
let upgrades = JSON.parse(localStorage.getItem('arrowFighterUpgrades')) || { health: 0, power: 0, speed: 0 };
let claimedChests = JSON.parse(localStorage.getItem('arrowFighterChests')) || [];
let pendingChestLevel = null;
gemEl.innerText = gems;
rewardChest.innerHTML = chestClosedSVG;

function saveGame() {
    localStorage.setItem('arrowFighterGems', gems);
    localStorage.setItem('arrowFighterMaxLevel', maxUnlockedLevel);
    localStorage.setItem('arrowFighterUpgrades', JSON.stringify(upgrades));
    localStorage.setItem('arrowFighterChests', JSON.stringify(claimedChests));
}

function showScreen(screen) {
    startScreen.style.display = 'none';
    mapScreen.style.display = 'none';
    shopScreen.style.display = 'none';
    nextLevelScreen.style.display = 'none';
    gameOverScreen.style.display = 'none';
    rewardScreen.style.display = 'none';
    pauseScreen.style.display = 'none';
    uiContainer.style.display = (screen === null) ? 'block' : 'none';
    btnPause.style.display = (screen === null) ? 'block' : 'none';

    if (screen) screen.style.display = 'flex';
}

function resizeCanvas() {
    const aspect = 1000 / 600;
    const windowAspect = window.innerWidth / window.innerHeight;
    let newWidth, newHeight;
    if (windowAspect < aspect) {
        newWidth = window.innerWidth * 0.95;
        newHeight = newWidth / aspect;
    } else {
        newHeight = window.innerHeight * 0.95;
        newWidth = newHeight * aspect;
    }
    canvas.style.width = `${newWidth}px`;
    canvas.style.height = `${newHeight}px`;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

rewardChest.addEventListener('click', () => {
    if (gameState !== 'REWARD') return;

    rewardChest.innerHTML = chestOpenedSVG;
    rewardChest.style.pointerEvents = 'none';
    rewardChest.style.animation = 'none';
    rewardChest.style.transform = 'scale(1.2)';

    gems += 20;
    gemEl.innerText = gems;

    claimedChests.push(pendingChestLevel);
    saveGame();

    document.getElementById('rewardText').style.display = 'block';
    document.getElementById('btnRewardContinue').style.display = 'inline-block';
});

document.getElementById('btnRewardContinue').addEventListener('click', () => {
    document.getElementById('rewardText').style.display = 'none';
    document.getElementById('btnRewardContinue').style.display = 'none';
    gameState = 'MAP';
    buildMap();
    showScreen(mapScreen);
});

function updateShopUI() {
    document.getElementById('upgHealthLvl').innerText = upgrades.health;
    document.getElementById('upgPowerLvl').innerText = upgrades.power;
    document.getElementById('upgSpeedLvl').innerText = upgrades.speed;

    let healthCost = 10 + (upgrades.health * 10);
    let powerCost = 15 + (upgrades.power * 15);
    let speedCost = 15 + (upgrades.speed * 15);

    document.getElementById('upgHealthCost').innerText = healthCost;
    document.getElementById('upgPowerCost').innerText = powerCost;
    document.getElementById('upgSpeedCost').innerText = speedCost;
}

document.getElementById('btnShop').addEventListener('click', () => {
    gameState = 'SHOP';
    updateShopUI();
    showScreen(shopScreen);
});
document.getElementById('btnShopBack').addEventListener('click', () => {
    gameState = 'START';
    showScreen(startScreen);
});

function buyUpgrade(type, baseCost, multiplier) {
    let cost = baseCost + (upgrades[type] * multiplier);
    if (gems >= cost) {
        gems -= cost;
        upgrades[type]++;
        gemEl.innerText = gems;
        saveGame();
        updateShopUI();
    }
}
document.getElementById('btnUpgHealth').addEventListener('click', () => buyUpgrade('health', 10, 10));
document.getElementById('btnUpgPower').addEventListener('click', () => buyUpgrade('power', 15, 15));
document.getElementById('btnUpgSpeed').addEventListener('click', () => buyUpgrade('speed', 15, 15));

function buildMap() {
    mapContainer.innerHTML = '';
    const TOTAL_LEVELS = 15;
    let foundPending = false;

    for (let i = TOTAL_LEVELS; i >= 1; i--) {
        let isUnlocked = i <= maxUnlockedLevel;
        let isLeft = i % 2 === 0;

        if (i === maxUnlockedLevel && i % 3 === 0 && !claimedChests.includes(i)) {
            pendingChestLevel = i;
            foundPending = true;
        }

        let node = document.createElement('div');
        node.className = `level-node ${isUnlocked ? 'unlocked' : ''}`;
        node.style.transform = `translateX(${isLeft ? '-120px' : '120px'})`; // Wider spread horizontally
        node.innerText = i;

        let deco = document.createElement('div');
        deco.className = 'map-deco';
        deco.innerHTML = '🏹';
        deco.style[isLeft ? 'right' : 'left'] = '-75px';
        deco.style.transform = isLeft ? 'scaleX(-1)' : 'none';
        node.appendChild(deco);

        if (i % 3 === 0) {
            let chestDeco = document.createElement('div');
            chestDeco.className = 'map-deco';
            chestDeco.style.fontSize = '60px';
            chestDeco.innerHTML = claimedChests.includes(i) ? chestOpenedSVG : chestClosedSVG;
            chestDeco.style[isLeft ? 'left' : 'right'] = '-95px';
            node.appendChild(chestDeco);
        }

        if (isUnlocked) {
            node.addEventListener('click', () => {
                activeLevel = i;
                startGame();
            });
        }
        mapContainer.appendChild(node);

        if (i > 1) {
            let line = document.createElement('div');
            line.className = `map-line ${isUnlocked ? 'unlocked' : ''}`;
            line.style.transform = `translateX(0px) rotate(${isLeft ? '-40deg' : '40deg'})`; // Adjusted angle to connect nodes smoothly
            mapContainer.appendChild(line);
        }
    }

    if (foundPending) {
        setTimeout(() => {
            showScreen(rewardScreen);
            gameState = 'REWARD';
            rewardChest.innerHTML = chestClosedSVG;
            rewardChest.style.pointerEvents = 'auto';
            rewardChest.style.animation = 'chestPulse 1.5s infinite';
        }, 100);
    } else {
        setTimeout(() => {
            let activeNode = document.querySelectorAll('.level-node.unlocked')[0];
            if(activeNode) activeNode.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
    }
}

document.getElementById('btnStart').addEventListener('click', () => {
    gameState = 'MAP';
    buildMap();
    showScreen(mapScreen);
});

document.getElementById('btnBackMap').addEventListener('click', () => {
    gameState = 'START';
    showScreen(startScreen);
});

function startGame() {
    gameState = 'PLAYING';
    score = 0;
    health = 5 + upgrades.health;
    bossPhase = false;
    bossesDefeated = 0;
    boss = null;
    bossProjectiles = [];
    arrows = [];
    targets = [];
    powerups = [];
    particles = [];
    floatingTexts = [];
    multiShotActive = false;
    multiShotTimer = 0;
    isCharging = false;
    chargeAmount = 0;
    playerY = canvas.height / 2;

    scoreEl.innerText = score;
    healthEl.innerText = health;
    levelEl.innerText = activeLevel;
    document.getElementById('levelHud').style.display = (activeLevel > 1) ? 'block' : 'none';

    showScreen(null);
    lastTime = performance.now();
    requestAnimationFrame(gameLoop);
}

function updateAim(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    mouseX = (clientX - rect.left) * scaleX;
    mouseY = (clientY - rect.top) * scaleY;
}

canvas.addEventListener('mousemove', (e) => { if(gameState==='PLAYING') updateAim(e.clientX, e.clientY); });
canvas.addEventListener('touchmove', (e) => {
    if(gameState==='PLAYING') { e.preventDefault(); updateAim(e.touches[0].clientX, e.touches[0].clientY); }
}, { passive: false });

window.addEventListener('keydown', (e) => {
    if (keys.hasOwnProperty(e.key)) keys[e.key] = true;
    if (e.key === 'Escape') {
        if (gameState === 'PLAYING') pauseGame();
        else if (gameState === 'PAUSED') resumeGame();
    }
});
window.addEventListener('keyup', (e) => {
    if (keys.hasOwnProperty(e.key)) keys[e.key] = false;
});

function shoot(charge) {
    if (gameState !== 'PLAYING') return;
    const baseAngle = Math.atan2(mouseY - playerY, mouseX - PLAYER_X);
    let damage = (1 + Math.floor(charge * 4)) + upgrades.power;
    let speed = 18 + (charge * 10);

    function createArrow(angleOffset) {
        arrows.push({
            x: PLAYER_X, y: playerY,
            vx: Math.cos(baseAngle + angleOffset) * speed,
            vy: Math.sin(baseAngle + angleOffset) * speed,
            damage: damage, charge: charge, active: true
        });
    }
    createArrow(0);
    if (multiShotActive) { createArrow(-0.15); createArrow(0.15); }
}

function startCharge() { if (gameState === 'PLAYING') { isCharging = true; chargeAmount = 0; } }
function releaseCharge() {
    if (!isCharging) return;
    shoot(chargeAmount);
    isCharging = false;
    chargeAmount = 0;
}

canvas.addEventListener('mousedown', startCharge);
canvas.addEventListener('mouseup', releaseCharge);
canvas.addEventListener('mouseleave', releaseCharge);
canvas.addEventListener('touchstart', (e) => {
    if(gameState==='PLAYING') { e.preventDefault(); updateAim(e.touches[0].clientX, e.touches[0].clientY); startCharge(); }
}, { passive: false });
canvas.addEventListener('touchend', (e) => { e.preventDefault(); releaseCharge(); });

function pauseGame() {
    gameState = 'PAUSED';
    showScreen(pauseScreen);
}
function resumeGame() {
    gameState = 'PLAYING';
    showScreen(null);
    lastTime = performance.now();
    requestAnimationFrame(gameLoop);
}
function quitToMap() {
    gameState = 'MAP';
    buildMap();
    showScreen(mapScreen);
}

btnPause.addEventListener('click', pauseGame);
document.getElementById('btnResume').addEventListener('click', resumeGame);
document.getElementById('btnQuitToMap').addEventListener('click', quitToMap);

document.getElementById('btnRetryLevel').addEventListener('click', startGame);
document.getElementById('nextLevelBtn').addEventListener('click', () => { activeLevel++; startGame(); });
document.getElementById('btnMapFromWin').addEventListener('click', quitToMap);
document.getElementById('btnMapFromLoss').addEventListener('click', quitToMap);

function triggerBossPhase(level) {
    bossPhase = true;
    targets = [];
    powerups = [];
    boss = {
        level: level,
        x: canvas.width + 150,
        y: canvas.height / 2,
        radius: level === 2 ? 90 : 60,
        hp: (level === 2 ? 80 : 50) + (activeLevel * 5),
        maxHp: (level === 2 ? 80 : 50) + (activeLevel * 5),
        vy: level === 2 ? 4 : 3,
        shootTimer: 0
    };
}

setInterval(() => {
    if (gameState !== 'PLAYING' || bossPhase) return;
    let radius = Math.random() * 25 + 15;
    let hp = Math.ceil((radius - 10) / 10);

    let speedBonus = (activeLevel - 1) * 0.4 + Math.floor(score / 1000) * 0.3;

    targets.push({
        x: canvas.width + 50,
        y: Math.random() * (canvas.height - 100) + 50,
        radius: radius,
        speed: (Math.random() * 1.2 + 0.5) + speedBonus,
        color: `hsl(${Math.random() * 360}, 70%, 50%)`,
        hp: hp, maxHp: hp
    });

    if (Math.random() < 0.10) {
        let isHealth = Math.random() < 0.50;
        powerups.push({
            x: canvas.width + 50 + Math.random() * 100,
            y: Math.random() * (canvas.height - 100) + 50,
            radius: 18,
            speed: Math.random() * 1.5 + 1.5,
            type: isHealth ? 'health' : 'multishot',
            color: isHealth ? '#2ecc71' : '#f1c40f'
        });
    }
}, 1200);

function drawPlayer(angle, currentCharge) {
    ctx.save();
    ctx.translate(PLAYER_X, playerY);

    ctx.strokeStyle = '#2c3e50';
    ctx.fillStyle = '#2c3e50';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Body
    ctx.beginPath();
    ctx.moveTo(0, -5); ctx.lineTo(0, 20);
    ctx.stroke();

    // Head
    ctx.beginPath();
    ctx.arc(0, -15, 10, 0, Math.PI * 2);
    ctx.fill();

    // Legs
    ctx.beginPath();
    ctx.moveTo(0, 20); ctx.lineTo(-12, 40);
    ctx.moveTo(0, 20); ctx.lineTo(12, 40);
    ctx.stroke();

    // Arms and Bow Group (Rotates based on aim)
    ctx.save();
    ctx.translate(0, -2);
    ctx.rotate(angle);

    // Back Arm (Drawing string)
    let pullBack = currentCharge * 20;
    ctx.strokeStyle = '#34495e'; // Slightly lighter for depth
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-5 - (pullBack/2), 8); // Elbow bends down and back
    ctx.lineTo(-10 - pullBack, 0); // Hand on string
    ctx.stroke();

    // Bow Arc
    ctx.beginPath();
    ctx.arc(15, 0, 30, -Math.PI/2.5, Math.PI/2.5);
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#8e44ad';
    ctx.stroke();

    // Bow String
    ctx.beginPath();
    ctx.moveTo(25, -28);
    ctx.lineTo(-10 - pullBack, 0);
    ctx.lineTo(25, 28);
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#7f8c8d';
    ctx.stroke();

    // Loaded Arrow
    let arrowColor = currentCharge === 1 ? '#e74c3c' : '#34495e';
    ctx.beginPath();
    ctx.moveTo(-10 - pullBack, 0);
    ctx.lineTo(35 - pullBack, 0);
    ctx.lineWidth = 3 + (currentCharge * 2);
    ctx.strokeStyle = arrowColor;
    ctx.stroke();

    // Arrowhead
    ctx.beginPath();
    ctx.moveTo(35 - pullBack, 0);
    ctx.lineTo(25 - pullBack, -4 - currentCharge);
    ctx.lineTo(25 - pullBack, 4 + currentCharge);
    ctx.fillStyle = '#c0392b';
    ctx.fill();

    // Front Arm (Holding Bow)
    ctx.strokeStyle = '#2c3e50';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(15, 0);
    ctx.stroke();

    ctx.restore(); // Restore body context
    ctx.restore(); // Restore global context

    // Charge Bar
    if (isCharging) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.fillRect(PLAYER_X - 20, playerY + 50, 40, 6);
        ctx.fillStyle = currentCharge === 1 ? '#e74c3c' : '#f1c40f';
        ctx.fillRect(PLAYER_X - 20, playerY + 50, 40 * currentCharge, 6);
    }
}

function updateAndDrawArrows(dt) {
    let speedMult = dt / 16.66;
    for (let i = arrows.length - 1; i >= 0; i--) {
        let a = arrows[i];
        a.vy += GRAVITY * speedMult;
        a.x += a.vx * speedMult;
        a.y += a.vy * speedMult;

        const angle = Math.atan2(a.vy, a.vx);
        ctx.save();
        ctx.translate(a.x, a.y);
        ctx.rotate(angle);

        let arrowThickness = 3 + (a.charge * 2);
        let arrowColor = a.charge === 1 ? '#e74c3c' : '#34495e';

        ctx.beginPath();
        ctx.moveTo(-20, 0); ctx.lineTo(10, 0);
        ctx.lineWidth = arrowThickness;
        ctx.strokeStyle = arrowColor;
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(15, 0);
        ctx.lineTo(5, -4 - a.charge);
        ctx.lineTo(5, 4 + a.charge);
        ctx.fillStyle = '#c0392b';
        ctx.fill();

        ctx.restore();

        if (a.y > canvas.height + 50 || a.x > canvas.width + 50) arrows.splice(i, 1);
    }
}

let floatingTexts = [];
function createFloatingText(x, y, text, color) {
    floatingTexts.push({ x: x, y: y, text: text, color: color, life: 1.0 });
}

function updateAndDrawFloatingTexts() {
    for (let i = floatingTexts.length - 1; i >= 0; i--) {
        let ft = floatingTexts[i];
        ft.y -= 1;
        ft.life -= 0.02;

        ctx.globalAlpha = Math.max(ft.life, 0);
        ctx.fillStyle = ft.color;
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(ft.text, ft.x, ft.y);
        ctx.globalAlpha = 1.0;

        if (ft.life <= 0) floatingTexts.splice(i, 1);
    }
}

function updateAndDrawTargets(dt) {
    let speedMult = dt / 16.66;
    for (let i = targets.length - 1; i >= 0; i--) {
        let t = targets[i];
        if (!t) continue;

        t.x -= t.speed * speedMult;

        ctx.save();
        ctx.translate(t.x, t.y);
        let scale = t.radius / 20;
        ctx.scale(scale, scale);

        let time = Date.now() / 150 * t.speed;
        let bodyBob = Math.abs(Math.sin(time)) * 2;
        ctx.translate(0, -bodyBob);

        ctx.strokeStyle = 'white';
        ctx.fillStyle = 'white';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';

        ctx.beginPath(); ctx.arc(0, -10, 8, 0, Math.PI * 2); ctx.fill(); // Skull
        ctx.fillStyle = '#111';
        ctx.beginPath(); ctx.arc(-3, -11, 2.5, 0, Math.PI * 2); ctx.arc(3, -11, 2.5, 0, Math.PI * 2); ctx.fill(); // Eyes
        ctx.beginPath(); ctx.moveTo(-3, -5); ctx.lineTo(3, -5); ctx.strokeStyle = '#111'; ctx.lineWidth = 1.5; ctx.stroke(); // Mouth

        ctx.strokeStyle = 'white'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(0, -2); ctx.lineTo(0, 10); ctx.stroke(); // Spine
        ctx.beginPath(); ctx.moveTo(-6, 2); ctx.lineTo(6, 2); ctx.moveTo(-7, 5); ctx.lineTo(7, 5); ctx.moveTo(-5, 8); ctx.lineTo(5, 8); ctx.stroke(); // Ribs

        ctx.beginPath(); // Arms
        let armBounce = Math.sin(time) * 3;
        ctx.moveTo(0, 2); ctx.lineTo(-4, 6 - armBounce); ctx.lineTo(-12, 5 - armBounce * 1.5);
        ctx.moveTo(0, 2); ctx.lineTo(-8, 5 + armBounce); ctx.lineTo(-16, 2 + armBounce * 1.5);
        ctx.stroke();

        ctx.beginPath(); // Legs
        let lfX = -Math.sin(time) * 12; let lfY = 24 - Math.max(0, Math.cos(time) * 8) + bodyBob;
        ctx.moveTo(0, 10); ctx.lineTo(lfX / 2 - 4, (10 + lfY) / 2); ctx.lineTo(lfX, lfY);
        let rfX = Math.sin(time) * 12; let rfY = 24 - Math.max(0, -Math.cos(time) * 8) + bodyBob;
        ctx.moveTo(0, 10); ctx.lineTo(rfX / 2 - 4, (10 + rfY) / 2); ctx.lineTo(rfX, rfY);
        ctx.stroke();

        ctx.restore();

        ctx.fillStyle = '#e74c3c'; ctx.font = 'bold 16px Arial'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(t.hp, t.x, t.y - t.radius - 12);

        if (t.x < -50) {
            targets.splice(i, 1);
            health--;
            healthEl.innerText = health;
            if (health <= 0) { gameState = 'GAMEOVER'; showScreen(gameOverScreen); }
            continue;
        }

        for (let j = arrows.length - 1; j >= 0; j--) {
            let a = arrows[j];
            let dx = a.x - t.x; let dy = a.y - t.y;
            if (Math.sqrt(dx * dx + dy * dy) < t.radius + 10) {
                t.hp -= a.damage;
                arrows.splice(j, 1);

                if (t.hp <= 0) {
                    score += Math.floor(t.speed * 10) * t.maxHp;
                    scoreEl.innerText = score;
                    targets.splice(i, 1);
                    createParticles(t.x, t.y, 'white', 20);

                    if (Math.random() < 0.15) {
                        gems++; gemEl.innerText = gems; saveGame();
                        createFloatingText(t.x, t.y, '+1 💎', '#00e5ff');
                    }

                    if (score >= 8000 && bossesDefeated === 1 && !bossPhase) { triggerBossPhase(2); return; }
                    else if (score >= 5000 && bossesDefeated === 0 && !bossPhase) { triggerBossPhase(1); return; }
                } else {
                    createParticles(t.x, t.y, 'white', 5);
                }
                break;
            }
        }
    }
}

function updateAndDrawPowerups(dt) {
    let speedMult = dt / 16.66;
    for (let i = powerups.length - 1; i >= 0; i--) {
        let p = powerups[i];
        p.x -= p.speed * speedMult;

        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color; ctx.fill();
        ctx.lineWidth = 3; ctx.strokeStyle = 'white'; ctx.stroke();
        ctx.fillStyle = 'white'; ctx.font = 'bold 12px Arial'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(p.type === 'health' ? '+1 HP' : '3x', p.x, p.y);

        if (p.x < -50) { powerups.splice(i, 1); continue; }

        for (let j = arrows.length - 1; j >= 0; j--) {
            let a = arrows[j];
            let dx = a.x - p.x; let dy = a.y - p.y;
            if (Math.sqrt(dx * dx + dy * dy) < p.radius + 10) {
                if (p.type === 'health') { health++; healthEl.innerText = health; }
                else if (p.type === 'multishot') { multiShotActive = true; multiShotTimer = 300; }
                arrows.splice(j, 1); powerups.splice(i, 1);
                createParticles(p.x, p.y, p.color, 25);
                break;
            }
        }
    }
}

function updateAndDrawBoss(dt) {
    if (!bossPhase || !boss) return;
    let speedMult = dt / 16.66;

    if (boss.x > canvas.width - 150) boss.x -= 2 * speedMult;
    else {
        boss.y += boss.vy * speedMult;
        if (boss.y < 100 || boss.y > canvas.height - 100) boss.vy *= -1;

        boss.shootTimer += speedMult;
        if (boss.shootTimer > 80) {
            boss.shootTimer = 0;
            let angle = Math.atan2(playerY - boss.y, PLAYER_X - boss.x);
            bossProjectiles.push({
                x: boss.x - boss.radius, y: boss.y + boss.radius * 0.3,
                vx: Math.cos(angle) * 8, vy: Math.sin(angle) * 8,
                radius: 10, type: boss.level === 2 ? 'ice' : 'fire'
            });
        }
    }

    ctx.fillStyle = '#ecf0f1';
    ctx.beginPath(); ctx.arc(boss.x, boss.y, boss.radius, 0, Math.PI * 2); ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = '#bdc3c7'; ctx.stroke();

    ctx.fillStyle = '#ecf0f1';
    ctx.fillRect(boss.x - boss.radius * 0.5, boss.y + boss.radius * 0.2, boss.radius, boss.radius * 0.7);
    ctx.strokeRect(boss.x - boss.radius * 0.5, boss.y + boss.radius * 0.2, boss.radius, boss.radius * 0.7);

    ctx.beginPath(); ctx.arc(boss.x - boss.radius * 0.35, boss.y - boss.radius * 0.1, boss.radius * 0.25, 0, Math.PI * 2);
    ctx.arc(boss.x + boss.radius * 0.35, boss.y - boss.radius * 0.1, boss.radius * 0.25, 0, Math.PI * 2);
    ctx.fillStyle = '#111'; ctx.fill();

    let eyeColor = boss.level === 2 ? '#3498db' : '#e74c3c';
    ctx.beginPath(); ctx.arc(boss.x - boss.radius * 0.35, boss.y - boss.radius * 0.1, boss.radius * 0.1, 0, Math.PI * 2);
    ctx.arc(boss.x + boss.radius * 0.35, boss.y - boss.radius * 0.1, boss.radius * 0.1, 0, Math.PI * 2);
    ctx.fillStyle = eyeColor; ctx.fill();

    ctx.beginPath(); ctx.moveTo(boss.x, boss.y + boss.radius * 0.1);
    ctx.lineTo(boss.x - boss.radius * 0.1, boss.y + boss.radius * 0.3);
    ctx.lineTo(boss.x + boss.radius * 0.1, boss.y + boss.radius * 0.3); ctx.fillStyle = '#111'; ctx.fill();

    ctx.strokeStyle = '#111'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(boss.x - boss.radius * 0.5, boss.y + boss.radius * 0.55); ctx.lineTo(boss.x + boss.radius * 0.5, boss.y + boss.radius * 0.55); ctx.stroke();
    ctx.beginPath();
    for(let i=1; i<=4; i++) {
        let tx = boss.x - boss.radius * 0.5 + i * (boss.radius / 5);
        ctx.moveTo(tx, boss.y + boss.radius * 0.2); ctx.lineTo(tx, boss.y + boss.radius * 0.9);
    }
    ctx.stroke();

    let barWidth = boss.radius * 2;
    let hpRatio = boss.hp / boss.maxHp;
    ctx.fillStyle = '#c0392b'; ctx.fillRect(boss.x - barWidth / 2, boss.y - boss.radius - 25, barWidth, 12);
    ctx.fillStyle = '#2ecc71'; ctx.fillRect(boss.x - barWidth / 2, boss.y - boss.radius - 25, barWidth * hpRatio, 12);

    for (let j = arrows.length - 1; j >= 0; j--) {
        let a = arrows[j];
        let dx = a.x - boss.x; let dy = a.y - boss.y;
        if (Math.sqrt(dx * dx + dy * dy) < boss.radius + 10) {
            boss.hp -= a.damage; arrows.splice(j, 1);
            createParticles(a.x, a.y, eyeColor, 10);

            if (boss.hp <= 0) {
                bossesDefeated++;
                createParticles(boss.x, boss.y, eyeColor, boss.radius * 2);
                let gemsAwarded = boss.level === 1 ? 5 : 10;
                gems += gemsAwarded; gemEl.innerText = gems; saveGame();
                createFloatingText(boss.x, boss.y, `+${gemsAwarded} 💎`, '#00e5ff');

                if (boss.level === 1) {
                    score += 2000; scoreEl.innerText = score;
                    boss = null; bossPhase = false; bossProjectiles = [];
                } else if (boss.level === 2) {
                    score += 5000; scoreEl.innerText = score;
                    boss = null; bossProjectiles = [];

                    if (activeLevel === maxUnlockedLevel && maxUnlockedLevel < 15) {
                        maxUnlockedLevel++; saveGame();
                    }
                    gameState = 'NEXT_LEVEL';
                    showScreen(nextLevelScreen);
                }
            }
            break;
        }
    }
}

function updateAndDrawBossProjectiles(dt) {
    let speedMult = dt / 16.66;
    for (let i = bossProjectiles.length - 1; i >= 0; i--) {
        let p = bossProjectiles[i];
        p.x += p.vx * speedMult; p.y += p.vy * speedMult;

        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        if (p.type === 'ice') {
            ctx.fillStyle = '#3498db'; ctx.fill(); ctx.strokeStyle = '#ecf0f1'; ctx.lineWidth = 3; ctx.stroke();
        } else {
            ctx.fillStyle = '#e74c3c'; ctx.fill();
        }

        let dx = p.x - PLAYER_X; let dy = p.y - playerY;
        if (Math.sqrt(dx * dx + dy * dy) < p.radius + 30) {
            health -= p.type === 'ice' ? 3 : 2; healthEl.innerText = health;
            bossProjectiles.splice(i, 1);
            createParticles(PLAYER_X, playerY, p.type === 'ice' ? '#3498db' : '#e74c3c', 15);
            if (health <= 0) { gameState = 'GAMEOVER'; showScreen(gameOverScreen); }
            continue;
        }
        if (p.x < -50 || p.y < -50 || p.y > canvas.height + 50) bossProjectiles.splice(i, 1);
    }
}

let particles = [];
function createParticles(x, y, color, count = 15) {
    for(let i=0; i<count; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 10,
            vy: (Math.random() - 0.5) * 10,
            life: 1.0, color: color
        });
    }
}

function updateAndDrawParticles(dt) {
    let speedMult = dt / 16.66;
    for (let i = particles.length - 1; i >= 0; i--) {
        let p = particles[i];
        p.x += p.vx * speedMult; p.y += p.vy * speedMult;
        p.life -= 0.05 * speedMult;

        ctx.globalAlpha = Math.max(p.life, 0);
        ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI*2);
        ctx.fillStyle = p.color; ctx.fill();
        ctx.globalAlpha = 1.0;

        if (p.life <= 0) particles.splice(i, 1);
    }
}

function gameLoop(timestamp) {
    if (gameState !== 'PLAYING' && gameState !== 'PAUSED') return;

    let dt = timestamp - lastTime;
    if (dt > 100) dt = 16.66;
    lastTime = timestamp;

    if (gameState === 'PAUSED') {
        requestAnimationFrame(gameLoop);
        return;
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let speedMult = dt / 16.66;
    if (keys.ArrowUp || keys.w) playerY -= PLAYER_SPEED * speedMult;
    if (keys.ArrowDown || keys.s) playerY += PLAYER_SPEED * speedMult;
    if (playerY < 40) playerY = 40;
    if (playerY > canvas.height - 40) playerY = canvas.height - 40;

    const bowAngle = Math.atan2(mouseY - playerY, mouseX - PLAYER_X);
    let chargeRate = 0.02 + (upgrades.speed * 0.005);
    if (isCharging) {
        chargeAmount += chargeRate * speedMult;
        if (chargeAmount > 1) chargeAmount = 1;
    }

    drawPlayer(bowAngle, chargeAmount);

    if (multiShotActive) {
        multiShotTimer -= speedMult;
        if (multiShotTimer <= 0) multiShotActive = false;
    }

    updateAndDrawArrows(dt);
    updateAndDrawTargets(dt);
    updateAndDrawPowerups(dt);
    updateAndDrawBoss(dt);
    updateAndDrawBossProjectiles(dt);
    updateAndDrawParticles(dt);
    updateAndDrawFloatingTexts();

    if (gameState === 'PLAYING') requestAnimationFrame(gameLoop);
}
