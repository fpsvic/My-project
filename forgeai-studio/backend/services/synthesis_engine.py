"""
synthesis_engine.py — ForgeAI True Code Synthesis Engine

Analyzes natural language descriptions word-by-word to synthesize
unique, working HTML5 code. Handles complex, multi-part descriptions
for any type of game or app.
"""

from __future__ import annotations
import re


# ══════════════════════════════════════════════════════════════
# GAME SYNTHESIS
# ══════════════════════════════════════════════════════════════

def _pick_theme(q: str) -> dict:
    if any(w in q for w in ("neon", "synthwave", "cyberpunk", "pink", "magenta")):
        return {"bg": "#0f051d", "primary": "#ec4899", "accent": "#06b6d4", "text": "#fdf2f8", "surface": "#1a0a2e"}
    if any(w in q for w in ("forest", "nature", "green", "jungle")):
        return {"bg": "#022c22", "primary": "#10b981", "accent": "#f59e0b", "text": "#ecfdf5", "surface": "#064e3b"}
    if any(w in q for w in ("ocean", "sea", "blue", "underwater", "water")):
        return {"bg": "#0c2540", "primary": "#0ea5e9", "accent": "#f43f5e", "text": "#f0f9ff", "surface": "#0f3460"}
    if any(w in q for w in ("fire", "lava", "hot", "red", "orange", "volcano")):
        return {"bg": "#1c0d02", "primary": "#f97316", "accent": "#e11d48", "text": "#fff7ed", "surface": "#431407"}
    if any(w in q for w in ("space", "galaxy", "cosmic", "star", "universe", "purple", "violet")):
        return {"bg": "#0f0728", "primary": "#a78bfa", "accent": "#f472b6", "text": "#f5f3ff", "surface": "#1e1254"}
    if any(w in q for w in ("matrix", "hacker", "terminal")):
        return {"bg": "#000000", "primary": "#22c55e", "accent": "#86efac", "text": "#f0fdf4", "surface": "#0a0a0a"}
    if any(w in q for w in ("desert", "gold", "sand", "yellow")):
        return {"bg": "#1c1400", "primary": "#f59e0b", "accent": "#ef4444", "text": "#fefce8", "surface": "#2d2000"}
    return {"bg": "#020617", "primary": "#6366f1", "accent": "#ec4899", "text": "#e2e8f0", "surface": "#0f172a"}


def _extract_game_features(q: str) -> dict:
    """Deep-parse a game description into features."""
    f: dict = {
        "player": "player",
        "player_emoji": "🟦",
        "player_color": "#6366f1",
        "collectibles": [],
        "enemies": [],
        "shoots": False,
        "projectile": "bullet",
        "projectile_emoji": "•",
        "gravity": False,
        "side_scroll": False,
        "top_down": True,
        "lives": 3,
        "difficulty_scaling": True,
        "special": [],
        "win": "survive",
        "movement": "arrows",
    }

    # Player
    player_map = [
        (["wizard", "mage", "sorcerer"], "wizard", "🧙", "#a78bfa"),
        (["knight", "warrior", "sword"], "knight", "⚔️", "#fbbf24"),
        (["spaceship", "ship", "spacecraft", "rocket"], "spaceship", "🚀", "#60a5fa"),
        (["car", "vehicle", "racer"], "car", "🏎️", "#f97316"),
        (["bird", "flap", "wing"], "bird", "🐦", "#fbbf24"),
        (["frog"], "frog", "🐸", "#4ade80"),
        (["ninja", "samurai"], "ninja", "🥷", "#1e293b"),
        (["robot", "mech"], "robot", "🤖", "#94a3b8"),
        (["dragon"], "dragon", "🐉", "#ef4444"),
        (["ball", "orb", "sphere"], "ball", "⚪", "#e2e8f0"),
        (["snake"], "snake", "🟢", "#4ade80"),
        (["tank"], "tank", "🪖", "#65a30d"),
        (["plane", "aircraft", "jet"], "plane", "✈️", "#38bdf8"),
        (["astronaut", "cosmonaut"], "astronaut", "👨‍🚀", "#94a3b8"),
    ]
    for keywords, name, emoji, color in player_map:
        if any(k in q for k in keywords):
            f["player"] = name
            f["player_emoji"] = emoji
            f["player_color"] = color
            break

    # Collectibles
    coll_map = [
        (["star", "stars"], "star", "⭐", "#fbbf24"),
        (["coin", "coins", "gold"], "coin", "🪙", "#f59e0b"),
        (["gem", "gems", "jewel"], "gem", "💎", "#6366f1"),
        (["crystal", "crystals"], "crystal", "🔷", "#60a5fa"),
        (["fruit", "apple", "cherry"], "fruit", "🍎", "#ef4444"),
        (["heart", "health pack"], "heart", "❤️", "#f43f5e"),
        (["key", "keys"], "key", "🔑", "#fbbf24"),
        (["power-up", "powerup", "power up"], "power-up", "⚡", "#fbbf24"),
        (["dot", "dots", "pellet", "food"], "dot", "•", "#e2e8f0"),
        (["ring", "rings"], "ring", "💍", "#fbbf24"),
        (["mushroom", "mushrooms"], "mushroom", "🍄", "#ef4444"),
        (["diamond", "diamonds"], "diamond", "💎", "#60a5fa"),
        (["orb", "orbs"], "orb", "✨", "#a78bfa"),
    ]
    for keywords, name, emoji, color in coll_map:
        if any(k in q for k in keywords):
            f["collectibles"].append({"name": name, "emoji": emoji, "color": color})

    # Enemies / obstacles
    enemy_map = [
        (["zombie", "zombies", "undead"], "zombie", "🧟", "#65a30d"),
        (["monster", "monsters", "creature"], "monster", "👾", "#8b5cf6"),
        (["alien", "aliens", "ufo"], "alien", "👽", "#4ade80"),
        (["ghost", "ghosts", "spirit"], "ghost", "👻", "#e2e8f0"),
        (["skeleton", "skeletons", "bone"], "skeleton", "💀", "#e2e8f0"),
        (["spike", "spikes", "thorn"], "spike", "🔺", "#ef4444"),
        (["asteroid", "asteroids", "rock"], "asteroid", "🪨", "#92400e"),
        (["bullet", "bullets", "projectile"], "enemy bullet", "🔴", "#ef4444"),
        (["bee", "bees", "wasp"], "bee", "🐝", "#fbbf24"),
        (["bat", "bats"], "bat", "🦇", "#7c3aed"),
        (["laser", "lasers"], "laser beam", "━", "#ef4444"),
        (["obstacle", "obstacles", "wall"], "obstacle", "🟥", "#ef4444"),
        (["enemy", "enemies", "foe", "foes"], "enemy", "👿", "#ef4444"),
        (["dragon enemy", "enemy dragon"], "dragon", "🐲", "#dc2626"),
    ]
    for keywords, name, emoji, color in enemy_map:
        if any(k in q for k in keywords):
            if not any(e["name"] == name for e in f["enemies"]):
                f["enemies"].append({"name": name, "emoji": emoji, "color": color})

    # Shooting
    shoot_words = ["shoot", "fire", "blast", "laser", "bullet", "lightning", "spell", "cast", "bolt", "beam", "missile", "arrow", "throw", "zap"]
    if any(w in q for w in shoot_words):
        f["shoots"] = True
        if any(w in q for w in ["lightning", "bolt", "electric", "zap"]):
            f["projectile"] = "lightning bolt"
            f["projectile_emoji"] = "⚡"
        elif any(w in q for w in ["laser", "beam"]):
            f["projectile"] = "laser"
            f["projectile_emoji"] = "━"
        elif any(w in q for w in ["fireball", "fire ball", "flame"]):
            f["projectile"] = "fireball"
            f["projectile_emoji"] = "🔥"
        elif any(w in q for w in ["arrow", "bow"]):
            f["projectile"] = "arrow"
            f["projectile_emoji"] = "→"
        elif any(w in q for w in ["spell", "magic", "cast"]):
            f["projectile"] = "spell"
            f["projectile_emoji"] = "✨"
        elif any(w in q for w in ["missile", "rocket"]):
            f["projectile"] = "missile"
            f["projectile_emoji"] = "🚀"

    # Physics
    if any(w in q for w in ["jump", "hop", "leap", "bounce", "gravity", "platform", "mario", "side scroll"]):
        f["gravity"] = True
        f["side_scroll"] = True
        f["top_down"] = False
        f["movement"] = "jump"

    # Mouse control
    if any(w in q for w in ["mouse", "click", "tap", "cursor"]):
        f["movement"] = "mouse"

    # Lives
    m = re.search(r"(\d+)\s+lives?", q)
    if m:
        f["lives"] = max(1, min(int(m.group(1)), 10))
    elif any(w in q for w in ["one life", "one chance", "no lives", "instant death"]):
        f["lives"] = 1

    # Win condition
    if any(w in q for w in ["collect all", "get all", "gather all"]):
        f["win"] = "collect_all"
    elif any(w in q for w in ["reach", "get to the end", "finish line", "exit", "door"]):
        f["win"] = "reach_goal"
    elif any(w in q for w in ["kill all", "defeat all", "destroy all", "eliminate all", "clear all"]):
        f["win"] = "kill_all"
    elif any(w in q for w in ["survive", "as long as", "stay alive", "last as long"]):
        f["win"] = "survive"

    # Special mechanics
    if any(w in q for w in ["rainbow", "color changing", "colour changing", "colorful"]):
        f["special"].append("rainbow")
    if any(w in q for w in ["trail", "tail", "leave behind", "trace"]):
        f["special"].append("trail")
    if any(w in q for w in ["grow", "gets bigger", "grows larger", "expand"]):
        f["special"].append("growing")
    if any(w in q for w in ["teleport", "warp", "portal", "phase"]):
        f["special"].append("teleport")
    if any(w in q for w in ["shield", "invincible", "temporary invulnerable"]):
        f["special"].append("shield")
    if any(w in q for w in ["split", "multiply", "divide", "replicate"]):
        f["special"].append("splitting")
    if any(w in q for w in ["wave", "waves", "rounds", "endless wave"]):
        f["special"].append("waves")
    if any(w in q for w in ["faster", "speed up", "accelerate", "gets faster"]):
        f["special"].append("speed_scaling")
    if any(w in q for w in ["double jump", "wall jump", "wall run"]):
        f["special"].append("advanced_jump")
    if any(w in q for w in ["poison", "toxic", "venom"]):
        f["special"].append("poison")
    if any(w in q for w in ["freeze", "frozen", "ice", "slow"]):
        f["special"].append("freeze")
    if any(w in q for w in ["multiplayer", "two player", "2 player", "pvp"]):
        f["special"].append("two_player")

    # Difficulty
    if any(w in q for w in ["easy", "simple", "casual", "beginner"]):
        f["difficulty_scaling"] = False
    if any(w in q for w in ["hard", "difficult", "challenging", "fast", "intense"]):
        f["difficulty_scaling"] = True

    return f


def _build_game_title(q: str, features: dict) -> str:
    """Derive a good game title from the description."""
    # Look for explicit name
    m = re.search(r'(?:called|named|title[d]?)\s+["\']?([A-Za-z0-9 ]+)["\']?', q, re.IGNORECASE)
    if m:
        return m.group(1).strip().title()

    player = features["player"].title()
    coll = features["collectibles"][0]["name"].title() if features["collectibles"] else ""
    enemy = features["enemies"][0]["name"].title() if features["enemies"] else ""

    if features["shoots"] and enemy:
        return f"{player} vs {enemy}s"
    if coll and enemy:
        return f"{player} — Collect & Survive"
    if features["side_scroll"] and features["shoots"]:
        return f"{player} Run & Gun"
    if features["side_scroll"]:
        return f"{player} Platformer"
    if features["shoots"]:
        return f"{player} Shooter"
    if coll:
        return f"{player} Quest"
    if enemy:
        return f"{player} Survivor"
    return f"{player} Adventure"


def synthesize_game(description: str) -> str:
    """Generate a complete HTML5 canvas game from any description."""
    q = description.lower()
    theme = _pick_theme(q)
    feat = _extract_game_features(q)
    title = _build_game_title(q, feat)

    # Determine game style
    is_shooter = feat["shoots"] and not feat["gravity"]
    is_platformer = feat["gravity"] and feat["side_scroll"]
    is_collector = feat["collectibles"] and not feat["shoots"] and not feat["gravity"]
    is_survival = feat["enemies"] and not feat["shoots"]

    player_emoji = feat["player_emoji"]
    enemy_emoji = feat["enemies"][0]["emoji"] if feat["enemies"] else "👾"
    coll_emoji = feat["collectibles"][0]["emoji"] if feat["collectibles"] else "⭐"
    coll_name = feat["collectibles"][0]["name"] if feat["collectibles"] else "star"
    enemy_name = feat["enemies"][0]["name"] if feat["enemies"] else "enemy"
    proj_emoji = feat["projectile_emoji"]
    lives = feat["lives"]
    has_rainbow = "rainbow" in feat["special"]
    has_waves = "waves" in feat["special"]
    has_trail = "trail" in feat["special"]
    has_growing = "growing" in feat["special"]

    # Rainbow color helper
    rainbow_js = """
function rainbowColor(t) {
  const h = (t * 2) % 360;
  return `hsl(${h},100%,60%)`;
}
""" if has_rainbow else ""

    # Trail system
    trail_js = """
const trail = [];
const MAX_TRAIL = 20;
function updateTrail(x, y) {
  trail.push({x, y, age: 0});
  if (trail.length > MAX_TRAIL) trail.shift();
}
function drawTrail(ctx) {
  trail.forEach((p, i) => {
    const alpha = (i / trail.length) * 0.5;
    ctx.globalAlpha = alpha;
    ctx.fillStyle = rainbowColor ? rainbowColor(Date.now()/1000 + i*0.1) : PRIMARY;
    ctx.fillRect(p.x - 8, p.y - 8, 16, 16);
  });
  ctx.globalAlpha = 1;
}
""" if has_trail else ""

    if is_platformer:
        return _build_platformer(title, theme, feat, player_emoji, enemy_emoji, coll_emoji, coll_name, enemy_name, proj_emoji, lives, has_rainbow, has_waves, rainbow_js, trail_js)
    elif is_shooter:
        return _build_shooter(title, theme, feat, player_emoji, enemy_emoji, coll_emoji, coll_name, enemy_name, proj_emoji, lives, has_rainbow, has_waves, rainbow_js, trail_js, has_growing)
    else:
        return _build_topdown(title, theme, feat, player_emoji, enemy_emoji, coll_emoji, coll_name, enemy_name, proj_emoji, lives, has_rainbow, has_waves, rainbow_js, trail_js, has_growing)


def _build_shooter(title, theme, feat, pe, ee, ce, cn, en, proj, lives, rainbow, waves, rainbow_js, trail_js, growing):
    bg, primary, accent, text, surface = theme["bg"], theme["primary"], theme["accent"], theme["text"], theme["surface"]
    speed_scaling = "speed_scaling" in feat["special"] or feat["difficulty_scaling"]
    movement = feat["movement"]
    mouse_ctrl = movement == "mouse"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;font-family:monospace;color:{text}}}
canvas{{border:2px solid {primary}33;border-radius:8px;box-shadow:0 0 30px {primary}22}}
#ui{{display:flex;justify-content:space-between;align-items:center;width:400px;margin-bottom:8px;font-size:12px;opacity:0.85}}
#msg{{margin-top:10px;font-size:13px;color:{primary};min-height:20px;text-align:center;width:400px}}
button{{background:{primary};color:#000;border:none;padding:8px 22px;border-radius:6px;cursor:pointer;font-weight:700;font-size:12px;margin-top:8px}}
</style></head>
<body>
<div id="ui"><span>⭐ <span id="score">0</span></span><span id="lvl">Wave 1</span><span>{'❤️ ' * lives}<span id="lives">{lives}</span></span></div>
<canvas id="c" width="400" height="500"></canvas>
<div id="msg">Press SPACE or click to start</div>
{'<p style="font-size:10px;opacity:0.4;margin-top:6px">← → to move · SPACE to shoot</p>' if not mouse_ctrl else '<p style="font-size:10px;opacity:0.4;margin-top:6px">Mouse to aim · Click to shoot</p>'}
<script>
{rainbow_js}
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),livesEl=document.getElementById('lives'),lvlEl=document.getElementById('lvl'),msgEl=document.getElementById('msg');
const W=400,H=500;
const PRIMARY='{primary}',ACCENT='{accent}',BG='{bg}';
let score=0,lives={lives},wave=1,running=false,frame=0;
let spawnRate=90,enemySpeed=1.5,playerSpeed=4;
let player={{x:W/2,y:H-60,w:32,h:32,color:PRIMARY}};
let bullets=[],enemies=[],particles=[];
let keys={{}};

{'document.addEventListener("keydown",e=>{keys[e.key]=true;if(e.key===" "){e.preventDefault();if(!running)startGame();}});' if not mouse_ctrl else ''}
{'document.addEventListener("keyup",e=>keys[e.key]=false);' if not mouse_ctrl else ''}
{'c.addEventListener("click",(e)=>{if(!running){startGame();return;}const r=c.getBoundingClientRect();shootAt(e.clientX-r.left,e.clientY-r.top);});' if mouse_ctrl else ''}
{'c.addEventListener("mousemove",(e)=>{const r=c.getBoundingClientRect();player.x=e.clientX-r.left-16;player.x=Math.max(0,Math.min(W-32,player.x));});' if mouse_ctrl else ''}
document.addEventListener("keydown",e=>{{if(e.key===" "){{e.preventDefault();if(!running)startGame();else shootBullet();}}}});

let shootCooldown=0;
function shootBullet(){{
  if(shootCooldown>0)return;
  bullets.push({{x:player.x+16,y:player.y,vy:-10,color:PRIMARY}});
  shootCooldown=8;
}}
function shootAt(tx,ty){{
  if(shootCooldown>0)return;
  const dx=tx-(player.x+16),dy=ty-(player.y+16);
  const len=Math.hypot(dx,dy)||1;
  bullets.push({{x:player.x+16,y:player.y+16,vx:dx/len*10,vy:dy/len*10,color:PRIMARY}});
  shootCooldown=8;
}}

function spawnEnemy(){{
  const x=20+Math.random()*(W-40);
  enemies.push({{x,y:-20,w:28,h:28,hp:wave>3?2:1,color:ACCENT,speed:enemySpeed+(Math.random()*0.5)}});
}}

function particle(x,y,color,n=8){{
  for(let i=0;i<n;i++){{
    const a=Math.random()*Math.PI*2,s=1+Math.random()*3;
    particles.push({{x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:30,color}});
  }}
}}

function startGame(){{
  score=0;lives={lives};wave=1;frame=0;spawnRate=90;enemySpeed=1.5;
  bullets=[];enemies=[];particles=[];
  player.x=W/2-16;player.y=H-60;
  running=true;msgEl.textContent='';
  scoreEl.textContent='0';livesEl.textContent='{lives}';
  requestAnimationFrame(loop);
}}

function loop(){{
  if(!running)return;
  frame++;
  ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);

  // Stars background
  ctx.fillStyle='rgba(255,255,255,0.08)';
  for(let i=0;i<3;i++){{const x=(frame*0.3+i*137)%W,y=(frame*0.8+i*91)%H;ctx.fillRect(x,y,1,1);}}

  // Player
  {'const pc=rainbowColor(frame/30)' if rainbow else f'const pc=PRIMARY'};
  ctx.font='28px serif';ctx.textAlign='center';
  ctx.fillText('{pe}',player.x+16,player.y+26);

  // Move player
  if(!{str(mouse_ctrl).lower()}){{
    if((keys['ArrowLeft']||keys['a'])&&player.x>0)player.x-=playerSpeed;
    if((keys['ArrowRight']||keys['d'])&&player.x<W-32)player.x+=playerSpeed;
    if(keys[' ']||keys['ArrowUp'])shootBullet();
  }}
  if(shootCooldown>0)shootCooldown--;

  // Bullets
  bullets=bullets.filter(b=>b.y>-10&&b.y<H+10&&b.x>-10&&b.x<W+10);
  bullets.forEach(b=>{{
    b.x+=(b.vx||0);b.y+=(b.vy||-10);
    ctx.font='14px serif';ctx.textAlign='center';
    ctx.fillText('{proj}',b.x,b.y);
  }});

  // Spawn enemies
  if(frame%Math.max(20,spawnRate-wave*5)===0)spawnEnemy();

  // Enemies
  enemies=enemies.filter(e=>e.y<H+30);
  enemies.forEach(e=>{{
    e.y+=e.speed;
    ctx.font='24px serif';ctx.textAlign='center';
    ctx.fillText('{ee}',e.x+14,e.y+22);
  }});

  // Bullet-enemy collision
  bullets.forEach(b=>{{
    enemies.forEach((e,ei)=>{{
      if(b.x>e.x&&b.x<e.x+e.w&&b.y>e.y&&b.y<e.y+e.h){{
        e.hp--;particle(e.x+14,e.y+14,ACCENT);
        if(e.hp<=0){{score+=10*wave;enemies.splice(ei,1);scoreEl.textContent=score;}}
        b.y=-999;
      }}
    }});
  }});

  // Enemy reaches bottom → lose life
  enemies.forEach((e,ei)=>{{
    if(e.y>H-20){{
      lives--;livesEl.textContent=lives;
      particle(e.x+14,H-10,ACCENT,12);
      enemies.splice(ei,1);
      if(lives<=0){{gameOver();return;}}
    }}
  }});

  // Enemy-player collision
  enemies.forEach((e,ei)=>{{
    if(player.x<e.x+e.w&&player.x+32>e.x&&player.y<e.y+e.h&&player.y+32>e.y){{
      lives--;livesEl.textContent=lives;
      particle(player.x+16,player.y+16,'#fff',15);
      enemies.splice(ei,1);
      if(lives<=0){{gameOver();return;}}
    }}
  }});

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{{
    ctx.globalAlpha=p.life/30;
    ctx.fillStyle=p.color;ctx.fillRect(p.x,p.y,3,3);
    p.x+=p.vx;p.y+=p.vy;p.life--;
  }});
  ctx.globalAlpha=1;

  // Wave progression
  if({str(waves or speed_scaling).lower()}){{
    const waveScore=wave*100;
    if(score>0&&score%waveScore===0&&enemies.length===0){{
      wave++;lvlEl.textContent='Wave '+wave;
      spawnRate=Math.max(30,spawnRate-10);
      enemySpeed=Math.min(4,enemySpeed+0.3);
    }}
  }}

  requestAnimationFrame(loop);
}}

function gameOver(){{
  running=false;
  ctx.fillStyle='rgba(0,0,0,0.7)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle=PRIMARY;ctx.font='bold 28px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-20);
  ctx.font='16px monospace';ctx.fillText('Score: '+score,W/2,H/2+15);
  msgEl.textContent='Press SPACE or click to restart';
  document.addEventListener('keydown',e=>{{if(e.key===' ')startGame();}},{{once:true}});
  c.addEventListener('click',startGame,{{once:true}});
}}

// Initial screen
ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);
ctx.fillStyle=PRIMARY;ctx.font='bold 22px monospace';ctx.textAlign='center';
ctx.fillText('{title}',W/2,H/2-30);
ctx.font='36px serif';ctx.fillText('{pe}',W/2,H/2+20);
ctx.fillStyle=text;ctx.font='13px monospace';ctx.fillText('Press SPACE to play',W/2,H/2+70);
</script>
</body></html>"""


def _build_topdown(title, theme, feat, pe, ee, ce, cn, en, proj, lives, rainbow, waves, rainbow_js, trail_js, growing):
    bg, primary, accent, text, surface = theme["bg"], theme["primary"], theme["accent"], theme["text"], theme["surface"]
    shoots = feat["shoots"]
    has_enemies = bool(feat["enemies"])
    has_collectibles = bool(feat["collectibles"])
    speed_scale = feat["difficulty_scaling"]

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;font-family:monospace;color:{text}}}
canvas{{border:2px solid {primary}33;border-radius:8px;box-shadow:0 0 30px {primary}22}}
#ui{{display:flex;justify-content:space-between;width:400px;margin-bottom:8px;font-size:12px;opacity:0.85}}
#msg{{margin-top:10px;font-size:13px;color:{primary};text-align:center;width:400px}}
button{{background:{primary};color:#000;border:none;padding:8px 22px;border-radius:6px;cursor:pointer;font-weight:700;font-size:12px;margin-top:8px}}
</style></head>
<body>
<div id="ui">
  <span>{cn.title()}: <span id="score">0</span></span>
  <span id="levelLabel">Level 1</span>
  <span>❤️ <span id="lives">{lives}</span></span>
</div>
<canvas id="c" width="400" height="400"></canvas>
<div id="msg">Press SPACE to start</div>
<p style="font-size:10px;opacity:0.4;margin-top:6px">WASD / Arrow keys to move{'  ·  SPACE to shoot' if shoots else ''}</p>
<script>
{rainbow_js}{trail_js}
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),livesEl=document.getElementById('lives'),lvlEl=document.getElementById('levelLabel'),msgEl=document.getElementById('msg');
const W=400,H=400,PRIMARY='{primary}',ACCENT='{accent}',BG='{bg}';
let score=0,lives={lives},level=1,running=false,frame=0;
let player={{x:W/2,y:H/2,size:24,speed:3,dx:0,dy:0}};
let collectibles=[],enemies=[],bullets=[],particles=[];
let keys={{}};
document.addEventListener('keydown',e=>{{keys[e.key]=true;if(e.key===' '){{e.preventDefault();if(!running)startGame();else shootBullet();}}}});
document.addEventListener('keyup',e=>delete keys[e.key]);

function spawnCollectible(){{
  collectibles.push({{x:20+Math.random()*(W-40),y:20+Math.random()*(H-40),size:16}});
}}
function spawnEnemy(){{
  const side=Math.floor(Math.random()*4);
  let x,y;
  if(side===0){{x=Math.random()*W;y=-20;}}
  else if(side===1){{x=W+20;y=Math.random()*H;}}
  else if(side===2){{x=Math.random()*W;y=H+20;}}
  else{{x=-20;y=Math.random()*H;}}
  const spd=0.8+level*0.2+Math.random()*0.5;
  enemies.push({{x,y,size:20,speed:spd}});
}}
function shootBullet(){{
  if(!keys[' '])return;
  const dx=player.dx||0,dy=player.dy||-1;
  const len=Math.hypot(dx,dy)||1;
  bullets.push({{x:player.x,y:player.y,vx:dx/len*9,vy:dy/len*9}});
}}

function particle(x,y,color,n=6){{
  for(let i=0;i<n;i++){{
    const a=Math.random()*Math.PI*2,s=1+Math.random()*4;
    particles.push({{x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:25,color}});
  }}
}}

function dist(a,b){{return Math.hypot(a.x-b.x,a.y-b.y);}}

function startGame(){{
  score=0;lives={lives};level=1;frame=0;
  collectibles=[];enemies=[];bullets=[];particles=[];
  player.x=W/2;player.y=H/2;player.dx=0;player.dy=0;
  for(let i=0;i<{'5' if has_collectibles else '0'};i++)spawnCollectible();
  for(let i=0;i<{'2' if has_enemies else '0'};i++)spawnEnemy();
  running=true;msgEl.textContent='';
  scoreEl.textContent='0';livesEl.textContent='{lives}';
  requestAnimationFrame(loop);
}}

let shootTimer=0;
function loop(){{
  if(!running)return;
  frame++;ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);

  // Grid background
  ctx.strokeStyle=PRIMARY+'11';ctx.lineWidth=1;
  for(let x=0;x<W;x+=40){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}}
  for(let y=0;y<H;y+=40){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}}

  // Player movement
  let mvx=0,mvy=0;
  if(keys['ArrowLeft']||keys['a'])mvx=-1;
  if(keys['ArrowRight']||keys['d'])mvx=1;
  if(keys['ArrowUp']||keys['w'])mvy=-1;
  if(keys['ArrowDown']||keys['s'])mvy=1;
  if(mvx||mvy){{const len=Math.hypot(mvx,mvy);mvx/=len;mvy/=len;player.dx=mvx;player.dy=mvy;}}
  player.x=Math.max(12,Math.min(W-12,player.x+mvx*player.speed));
  player.y=Math.max(12,Math.min(H-12,player.y+mvy*player.speed));

  // Auto shoot
  if({'true' if shoots else 'false'}){{
    if(++shootTimer>15&&enemies.length>0){{
      shootTimer=0;
      const nearest=enemies.reduce((a,b)=>dist(player,a)<dist(player,b)?a:b);
      const dx=nearest.x-player.x,dy=nearest.y-player.y,len=Math.hypot(dx,dy)||1;
      bullets.push({{x:player.x,y:player.y,vx:dx/len*9,vy:dy/len*9}});
    }}
  }}

  // Draw player
  {'const pc=rainbowColor(frame/20);' if rainbow else f'const pc=PRIMARY;'}
  ctx.font=player.size+'px serif';ctx.textAlign='center';
  ctx.fillText('{pe}',player.x,player.y+player.size/3);

  // Bullets
  bullets=bullets.filter(b=>b.x>-5&&b.x<W+5&&b.y>-5&&b.y<H+5);
  bullets.forEach(b=>{{b.x+=b.vx;b.y+=b.vy;ctx.font='14px serif';ctx.fillText('{proj}',b.x,b.y);}});

  // Collectibles
  collectibles.forEach((co,ci)=>{{
    ctx.font=co.size+'px serif';ctx.fillText('{ce}',co.x,co.y+co.size/3);
    if(dist(player,co)<18){{
      score+=10;scoreEl.textContent=score;
      particle(co.x,co.y,PRIMARY);
      collectibles.splice(ci,1);
      setTimeout(spawnCollectible,800);
      if({'true' if speed_scale else 'false'})player.speed=Math.min(5,3+score/100);
    }}
  }});

  // Enemies
  enemies.forEach((e,ei)=>{{
    const dx=player.x-e.x,dy=player.y-e.y,len=Math.hypot(dx,dy)||1;
    e.x+=dx/len*e.speed;e.y+=dy/len*e.speed;
    ctx.font=e.size+'px serif';ctx.fillText('{ee}',e.x,e.y+e.size/3);
    // Bullet hits
    bullets.forEach((b,bi)=>{{
      if(dist(b,e)<14){{
        particle(e.x,e.y,ACCENT,10);
        enemies.splice(ei,1);
        bullets.splice(bi,1);
        score+=20*level;scoreEl.textContent=score;
        setTimeout(spawnEnemy,1000);
      }}
    }});
    // Player hit
    if(dist(player,e)<16){{
      lives--;livesEl.textContent=lives;
      particle(player.x,player.y,'#fff',12);
      enemies.splice(ei,1);
      if(lives<=0){{gameOver();return;}}
      setTimeout(spawnEnemy,600);
    }}
  }});

  // Level up every 5 enemies killed
  if({'true' if waves else 'false'}){{
    const nextLvl=level*5*20;
    if(score>0&&score>=nextLvl&&score%(nextLvl)===0){{
      level++;lvlEl.textContent='Level '+level;
      for(let i=0;i<level;i++)spawnEnemy();
    }}
  }}

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{{
    ctx.globalAlpha=p.life/25;ctx.fillStyle=p.color;
    ctx.fillRect(p.x-1.5,p.y-1.5,3,3);
    p.x+=p.vx;p.y+=p.vy;p.life--;
  }});
  ctx.globalAlpha=1;
  requestAnimationFrame(loop);
}}

function gameOver(){{
  running=false;
  ctx.fillStyle='rgba(0,0,0,0.75)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle=PRIMARY;ctx.font='bold 26px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-20);
  ctx.font='15px monospace';ctx.fillStyle='{text}';ctx.fillText('Score: '+score,W/2,H/2+15);
  msgEl.textContent='Press SPACE to restart';
  document.addEventListener('keydown',e=>{{if(e.key===' ')startGame();}},{{once:true}});
}}
ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);
ctx.fillStyle=PRIMARY;ctx.font='bold 20px monospace';ctx.textAlign='center';
ctx.fillText('{title}',W/2,H/2-30);
ctx.font='36px serif';ctx.fillText('{pe}',W/2,H/2+20);
ctx.fillStyle='{text}';ctx.font='13px monospace';ctx.fillText('Press SPACE to begin',W/2,H/2+70);
</script>
</body></html>"""


def _build_platformer(title, theme, feat, pe, ee, ce, cn, en, proj, lives, rainbow, waves, rainbow_js, trail_js):
    bg, primary, accent, text, surface = theme["bg"], theme["primary"], theme["accent"], theme["text"], theme["surface"]
    shoots = feat["shoots"]
    adv_jump = "advanced_jump" in feat["special"]
    has_enemies = bool(feat["enemies"])
    has_collectibles = bool(feat["collectibles"])

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;font-family:monospace;color:{text}}}
canvas{{border:2px solid {primary}33;border-radius:8px;box-shadow:0 0 30px {primary}22}}
#ui{{display:flex;justify-content:space-between;width:480px;margin-bottom:8px;font-size:12px;opacity:0.85}}
#msg{{margin-top:8px;font-size:13px;color:{primary};text-align:center;width:480px}}
</style></head>
<body>
<div id="ui"><span>⭐ <span id="score">0</span></span><span id="lvl">Level 1</span><span>❤️ <span id="lives">{lives}</span></span></div>
<canvas id="c" width="480" height="320"></canvas>
<div id="msg">Press SPACE to start</div>
<p style="font-size:10px;opacity:0.4;margin-top:6px">← → to move  ·  SPACE / ↑ to jump{'  ·  Z to shoot' if shoots else ''}</p>
<script>
{rainbow_js}{trail_js}
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),livesEl=document.getElementById('lives'),lvlEl=document.getElementById('lvl'),msgEl=document.getElementById('msg');
const W=480,H=320,PRIMARY='{primary}',ACCENT='{accent}',BG='{bg}';
let score=0,lives={lives},level=1,running=false,frame=0;
const G=0.5,JUMP=-11;
let player={{x:60,y:200,w:28,h:28,vx:0,vy:0,onGround:false,jumps:{'2' if adv_jump else '1'},maxJumps:{'2' if adv_jump else '1'}}};
let platforms=[],collectibles=[],enemies=[],bullets=[],particles=[];
let keys={{}};
document.addEventListener('keydown',e=>{{keys[e.key]=true;if(e.key===' '||e.key==='ArrowUp'){{e.preventDefault();if(!running)startGame();else tryJump();}}}});
document.addEventListener('keyup',e=>delete keys[e.key]);

function tryJump(){{if(player.jumps>0){{player.vy=JUMP;player.jumps--;player.onGround=false;}}}}

function buildLevel(){{
  platforms=[
    {{x:0,y:H-20,w:W,h:20}},
    {{x:80,y:230,w:100,h:12}},
    {{x:220,y:190,w:100,h:12}},
    {{x:350,y:150,w:100,h:12}},
    {{x:100,y:130,w:80,h:12}},
    {{x:260,y:100,w:80,h:12}},
  ];
  collectibles=[];
  platforms.slice(1).forEach(p=>{{
    if(Math.random()>0.3)collectibles.push({{x:p.x+p.w/2,y:p.y-20,size:16,collected:false}});
  }});
  enemies=[];
  if({'true' if has_enemies else 'false'}){{
    [platforms[1],platforms[3]].forEach(p=>{{
      enemies.push({{x:p.x+10,y:p.y-24,w:24,h:24,vx:1+level*0.2,dir:1,platform:p}});
    }});
  }}
  bullets=[];
}}

function particle(x,y,color,n=6){{
  for(let i=0;i<n;i++){{
    const a=Math.random()*Math.PI*2,s=2+Math.random()*3;
    particles.push({{x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:20,color}});
  }}
}}

function startGame(){{
  score=0;lives={lives};level=1;frame=0;
  player.x=60;player.y=200;player.vx=0;player.vy=0;player.onGround=false;player.jumps=player.maxJumps;
  buildLevel();
  running=true;msgEl.textContent='';scoreEl.textContent='0';livesEl.textContent='{lives}';
  requestAnimationFrame(loop);
}}

function loop(){{
  if(!running)return;
  frame++;
  ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);

  // Move player
  let mvx=0;
  if(keys['ArrowLeft']||keys['a'])mvx=-1;
  if(keys['ArrowRight']||keys['d'])mvx=1;
  player.vx=mvx*4;
  player.vy+=G;
  player.x+=player.vx;
  player.y+=player.vy;
  player.x=Math.max(0,Math.min(W-player.w,player.x));

  // Platform collision
  player.onGround=false;
  platforms.forEach(p=>{{
    if(player.x<p.x+p.w&&player.x+player.w>p.x&&player.y+player.h>p.y&&player.y+player.h<p.y+p.h+player.vy+1&&player.vy>=0){{
      player.y=p.y-player.h;player.vy=0;player.onGround=true;player.jumps=player.maxJumps;
    }}
  }});
  if(player.y>H+40){{lives--;livesEl.textContent=lives;player.x=60;player.y=200;player.vy=0;if(lives<=0){{gameOver();return;}}}}

  // Draw platforms
  platforms.forEach(p=>{{ctx.fillStyle=PRIMARY+'44';ctx.fillRect(p.x,p.y,p.w,p.h);
    ctx.strokeStyle=PRIMARY+'88';ctx.strokeRect(p.x,p.y,p.w,p.h);}});

  // Draw player
  ctx.font='24px serif';ctx.textAlign='center';
  ctx.fillText('{pe}',player.x+player.w/2,player.y+22);

  // Shoot
  if({'true' if shoots else 'false'}&&(keys['z']||keys['Z']||keys[' '])){{
    if(frame%15===0)bullets.push({{x:player.x+14,y:player.y+12,vx:player.vx>=0?8:-8}});
  }}

  // Bullets
  bullets=bullets.filter(b=>b.x>-5&&b.x<W+5);
  bullets.forEach(b=>{{b.x+=b.vx;ctx.font='14px serif';ctx.fillText('{proj}',b.x,b.y);}});

  // Collectibles
  collectibles.forEach((co,ci)=>{{
    if(co.collected)return;
    ctx.font=co.size+'px serif';ctx.fillText('{ce}',co.x,co.y+co.size/3);
    if(Math.hypot(player.x+14-co.x,player.y+14-co.y)<20){{
      co.collected=true;score+=10;scoreEl.textContent=score;particle(co.x,co.y,PRIMARY);
    }}
  }});

  // Enemies
  enemies.forEach((e,ei)=>{{
    e.x+=e.vx*e.dir;
    if(e.x>e.platform.x+e.platform.w-e.w||e.x<e.platform.x)e.dir*=-1;
    ctx.font='20px serif';ctx.fillText('{ee}',e.x+12,e.y+18);
    // Player collision
    if(player.x<e.x+e.w&&player.x+player.w>e.x&&player.y<e.y+e.h&&player.y+player.h>e.y){{
      if(player.vy>0&&player.y+player.h<e.y+e.h/2){{
        enemies.splice(ei,1);player.vy=JUMP/2;score+=20;scoreEl.textContent=score;particle(e.x+12,e.y,'#fff',8);
      }} else {{
        lives--;livesEl.textContent=lives;player.x=60;player.y=200;player.vy=0;
        if(lives<=0){{gameOver();return;}}
      }}
    }}
    // Bullet kills enemy
    bullets.forEach((b,bi)=>{{
      if(b.x>e.x&&b.x<e.x+e.w&&b.y>e.y&&b.y<e.y+e.h){{
        enemies.splice(ei,1);bullets.splice(bi,1);score+=20;scoreEl.textContent=score;particle(e.x+12,e.y,ACCENT,8);
      }}
    }});
  }});

  // Level clear
  if(collectibles.every(co=>co.collected)&&enemies.length===0){{
    level++;lvlEl.textContent='Level '+level;buildLevel();
  }}

  // Particles
  particles=particles.filter(p=>p.life>0);
  particles.forEach(p=>{{
    ctx.globalAlpha=p.life/20;ctx.fillStyle=p.color;ctx.fillRect(p.x-1.5,p.y-1.5,3,3);
    p.x+=p.vx;p.y+=p.vy;p.vy+=0.2;p.life--;
  }});
  ctx.globalAlpha=1;
  requestAnimationFrame(loop);
}}

function gameOver(){{
  running=false;
  ctx.fillStyle='rgba(0,0,0,0.75)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle=PRIMARY;ctx.font='bold 24px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-20);
  ctx.font='15px monospace';ctx.fillStyle='{text}';ctx.fillText('Score: '+score,W/2,H/2+15);
  msgEl.textContent='Press SPACE to restart';
  document.addEventListener('keydown',e=>{{if(e.key===' ')startGame();}},{{once:true}});
}}
ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);
ctx.fillStyle=PRIMARY;ctx.font='bold 18px monospace';ctx.textAlign='center';
ctx.fillText('{title}',W/2,H/2-30);
ctx.font='32px serif';ctx.fillText('{pe}',W/2,H/2+10);
ctx.fillStyle='{text}';ctx.font='13px monospace';ctx.fillText('Press SPACE to begin',W/2,H/2+60);
</script>
</body></html>"""


# ══════════════════════════════════════════════════════════════
# MAIN API
# ══════════════════════════════════════════════════════════════

def should_synthesize(description: str) -> bool:
    """Return True if this description needs synthesis rather than templates."""
    q = description.lower()
    # Synthesis handles complex multi-feature games and unknown types
    complex_indicators = [
        len(q) > 60,
        sum(1 for w in ["wizard", "ninja", "dragon", "robot", "frog", "ball", "knight", "astronaut"] if w in q) > 0,
        bool(re.search(r"(shoot|fire|blast|laser|lightning|spell)", q)) and any(w in q for w in ["zombie", "monster", "alien", "ghost"]),
        "platform" in q or ("jump" in q and not "snake" in q),
        len([w for w in ["collect", "avoid", "shoot", "jump", "survive"] if w in q]) >= 2,
    ]
    return any(complex_indicators)
