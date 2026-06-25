"""
Game Compiler — detects genre from query and builds a complete HTML5 game.

Supported genres:
  snake · pong · flappy · brickbreaker · clicker · spaceshooter
  racing · platformer · maze · memory · zombie · tictactoe
  + universal fallback that generates any game from description
"""

from data.game_templates import GAME_TEMPLATES


# ══════════════════════════════════════════════════════════════
# DETECTION
# ══════════════════════════════════════════════════════════════

def _detect_genre(q: str) -> str:
    # Racing / driving — checked before "space" to avoid misfire
    if any(w in q for w in (
        "car", "race", "racing", "drive", "driving", "road", "highway",
        "drift", "formula", "nascar", "kart", "vehicle", "truck", "traffic",
        "lane", "speed racer", "dirt road", "speedway", "grand prix", "lap",
        "circuit", "burnout", "road rage", "car racing", "street race",
    )):
        return "racing"

    if any(w in q for w in ("pong", "paddle", "hockey", "table tennis")):
        return "pong"

    if any(w in q for w in ("tic", "toe", "noughts", "xo", "x and o")):
        return "tictactoe"

    if any(w in q for w in ("flap", "bird", "wing", "copter", "fly through", "dodge pipes", "flutter")):
        return "flappy"

    if any(w in q for w in ("brick", "break", "shatter", "breaker", "arkanoid")):
        return "brickbreaker"

    if any(w in q for w in ("clicker", "cookie", "idle", "incremental")):
        return "clicker"

    if any(w in q for w in (
        "zombie", "undead", "horde", "survival", "wave", "apocalypse",
        "outbreak", "infection", "plague", "undead horde", "dead rising",
    )):
        return "zombie"

    if any(w in q for w in (
        "platform", "platformer", "jump", "mario", "side scroll",
        "run and jump", "jump game", "side scroller", "hop", "leap", "parkour",
    )):
        return "platformer"

    if any(w in q for w in ("maze", "labyrinth", "dungeon", "corridor", "escape", "find the exit", "navigate")):
        return "maze"

    if any(w in q for w in (
        "memory", "match card", "card flip", "card match", "concentration",
        "matching game", "pair", "flip cards", "find pairs",
    )):
        return "memory"

    if any(w in q for w in ("snake", "worm", "slither")):
        return "snake"

    if any(w in q for w in ("tower", "defense", "defend", "td game", "base defense")):
        return "tower_defense"

    if any(w in q for w in ("whack", "mole", "whack-a-mole", "tap the")):
        return "whack"

    if any(w in q for w in ("2048", "sliding tile", "number merge", "merge tiles")):
        return "2048"

    if any(w in q for w in ("blackjack", "black jack", "21 card", "poker", "casino card", "card game", "deal me")):
        return "blackjack"

    if any(w in q for w in ("asteroid", "rotate and shoot", "space rock")):
        return "asteroids"

    if any(w in q for w in ("fishing", "fish game", "catch fish", "go fishing", "reel")):
        return "fishing"

    if any(w in q for w in ("chess",)):
        return "chess"

    if any(w in q for w in ("doodle jump", "vertical jump", "jump up", "endless jump", "bounce up")):
        return "doodle"

    if any(w in q for w in ("space", "shoot", "invader", "alien", "laser", "ship", "galaga", "meteor")):
        return "spaceshooter"

    # Unknown — generate a real game from the description
    return "universal"


def _detect_theme(q: str) -> dict:
    if any(w in q for w in ("synthwave", "cyberpunk", "pink", "magenta", "neon")):
        return {"name": "Neon Synthwave", "bg": "#0f051d",
                "primary": "#ec4899", "secondary": "#db2777",
                "accent": "#06b6d4", "text": "#fdf2f8",
                "gridColor": "rgba(236,72,153,0.15)"}
    if any(w in q for w in ("matrix", "terminal", "hacker", "green")):
        return {"name": "Hacker Matrix", "bg": "#000000",
                "primary": "#22c55e", "secondary": "#15803d",
                "accent": "#86efac", "text": "#f0fdf4",
                "gridColor": "rgba(34,197,94,0.1)"}
    if any(w in q for w in ("ocean", "sea", "blue", "water", "underwater")):
        return {"name": "Deep Ocean", "bg": "#0c2540",
                "primary": "#0ea5e9", "secondary": "#0284c7",
                "accent": "#f43f5e", "text": "#f0f9ff",
                "gridColor": "rgba(14,165,233,0.15)"}
    if any(w in q for w in ("sunset", "orange", "red", "fire", "volcano")):
        return {"name": "Volcanic Sunset", "bg": "#1c0d02",
                "primary": "#f97316", "secondary": "#ea580c",
                "accent": "#e11d48", "text": "#fff7ed",
                "gridColor": "rgba(249,115,22,0.15)"}
    if any(w in q for w in ("forest", "garden", "wood", "emerald", "jungle")):
        return {"name": "Mystic Forest", "bg": "#022c22",
                "primary": "#10b981", "secondary": "#047857",
                "accent": "#f59e0b", "text": "#ecfdf5",
                "gridColor": "rgba(16,185,129,0.1)"}
    if any(w in q for w in ("gold", "yellow", "desert", "sand", "sunny")):
        return {"name": "Desert Gold", "bg": "#1c1400",
                "primary": "#f59e0b", "secondary": "#d97706",
                "accent": "#ef4444", "text": "#fefce8",
                "gridColor": "rgba(245,158,11,0.15)"}
    if any(w in q for w in ("purple", "violet", "galaxy", "cosmic", "space")):
        return {"name": "Cosmic Violet", "bg": "#0f0728",
                "primary": "#a78bfa", "secondary": "#7c3aed",
                "accent": "#f472b6", "text": "#f5f3ff",
                "gridColor": "rgba(167,139,250,0.15)"}
    return {"name": "Classic Neon", "bg": "#020617",
            "primary": "#10b981", "secondary": "#059669",
            "accent": "#ef4444", "text": "#e2e8f0",
            "gridColor": "rgba(16,185,129,0.1)"}


def _detect_speed(q: str) -> tuple:
    if any(w in q for w in ("fast", "speedy", "turbo", "rapid", "quick", "insane")):
        return 1.6, "Turbo"
    if any(w in q for w in ("slow", "lazy", "chill", "relax", "easy")):
        return 0.6, "Chill"
    return 1.0, "Normal"


# ══════════════════════════════════════════════════════════════
# GAME BUILDERS
# ══════════════════════════════════════════════════════════════

def _build_racing(theme: dict, speed: float, speed_label: str, query: str) -> str:
    car_color = theme["primary"]
    road_color = "#1e293b"
    line_color = "#f59e0b"
    obstacle_color = theme["accent"]
    # pick car emoji / label from query
    if any(w in query for w in ("truck", "semi", "lorry")):
        car_label = "TRUCK"
    elif any(w in query for w in ("kart", "go kart")):
        car_label = "KART"
    elif any(w in query for w in ("formula", "f1")):
        car_label = "F1"
    else:
        car_label = "CAR"

    road_speed = round(3 * speed * 100) / 100
    obs_speed = round(2.5 * speed * 100) / 100

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Racing</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background-color:{theme['bg']};margin:0}}
canvas{{display:block}}
</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4"
      style="background:{theme['bg']}">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 uppercase tracking-widest text-[10px] font-bold">{theme['name']} {car_label} ({speed_label})</span>
    <span id="score" style="color:{car_color}">SCORE: 0</span>
  </div>
  <canvas id="c" width="280" height="380" class="rounded-xl border border-slate-800" style="background:{road_color}"></canvas>
  <div class="flex gap-2 mt-3 w-full">
    <button id="startBtn" class="flex-1 py-2 rounded-xl text-xs font-bold" style="background:{car_color}">START RACE</button>
  </div>
  <p class="text-slate-500 text-[10px] mt-2">← → Arrow Keys or A/D to steer</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=280,H=380,LANE_W=60,LANES=[50,110,170,230];
let score=0,lives=3,speed={road_speed},gameRunning=false,gameInterval;
let carX=W/2-15,carY=H-80,carW=30,carH=50;
let obstacles=[],roadOffset=0,keys={{}};
let lastObstacleScore=0;

function spawnObstacle(){{
  const lane=LANES[Math.floor(Math.random()*LANES.length)];
  const colors=["{obstacle_color}","#f43f5e","#6366f1","#f59e0b"];
  obstacles.push({{x:lane-15,y:-60,w:30,h:50,color:colors[Math.floor(Math.random()*colors.length)]}});
}}

function drawRoad(){{
  // Road base
  ctx.fillStyle='{road_color}';ctx.fillRect(0,0,W,H);
  // Road edges
  ctx.fillStyle='#334155';ctx.fillRect(0,0,20,H);ctx.fillRect(260,0,20,H);
  // Dashed centre lines
  ctx.setLineDash([30,20]);ctx.lineWidth=3;ctx.strokeStyle='{line_color}';
  [80,140,200].forEach(x=>{{
    ctx.beginPath();ctx.moveTo(x,(roadOffset%50)-50);ctx.lineTo(x,H+50);ctx.stroke();
  }});
  ctx.setLineDash([]);
}}

function drawCar(x,y,w,h,color,isPlayer){{
  // Body
  ctx.fillStyle=color;
  ctx.beginPath();ctx.roundRect(x,y,w,h,5);ctx.fill();
  // Windshield
  ctx.fillStyle=isPlayer?'rgba(14,165,233,0.7)':'rgba(200,200,200,0.5)';
  ctx.fillRect(x+4,y+(isPlayer?h-18:4),w-8,10);
  // Wheels
  ctx.fillStyle='#1e293b';
  ctx.fillRect(x-4,y+6,8,12);ctx.fillRect(x+w-4,y+6,8,12);
  ctx.fillRect(x-4,y+h-18,8,12);ctx.fillRect(x+w-4,y+h-18,8,12);
  // Headlights / taillights
  if(isPlayer){{
    ctx.fillStyle='#fef08a';ctx.fillRect(x+3,y+2,8,4);ctx.fillRect(x+w-11,y+2,8,4);
  }}
}}

function update(){{
  roadOffset+={road_speed};
  score++;
  scoreEl.innerText='SCORE: '+score;

  if(keys['ArrowLeft']||keys['a'])carX=Math.max(20,carX-4);
  if(keys['ArrowRight']||keys['d'])carX=Math.min(W-50,carX+4);

  // Spawn obstacles every ~60 points
  if(score-lastObstacleScore>60){{
    spawnObstacle();lastObstacleScore=score;
    if(obstacles.length>1&&score%300===0)speed=Math.min(speed+0.2,{round(obs_speed*2*100)/100});
  }}

  obstacles.forEach(o=>o.y+={obs_speed});
  obstacles=obstacles.filter(o=>o.y<H+80);

  // Collision
  obstacles.forEach(o=>{{
    if(carX<o.x+o.w&&carX+carW>o.x&&carY<o.y+o.h&&carY+carH>o.y){{
      lives--;
      o.y=H+100; // remove it
      if(lives<=0)gameOver();
    }}
  }});

  // Draw
  drawRoad();
  obstacles.forEach(o=>drawCar(o.x,o.y,o.w,o.h,o.color,false));
  drawCar(carX,carY,carW,carH,'{car_color}',true);

  // HUD lives
  ctx.fillStyle='#e2e8f0';ctx.font='bold 11px monospace';
  ctx.fillText('♥'.repeat(lives),8,16);
}}

function gameOver(){{
  gameRunning=false;clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.88)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{obstacle_color}';ctx.font='bold 22px Courier New';ctx.textAlign='center';
  ctx.fillText('CRASHED!',W/2,H/2-20);
  ctx.fillStyle='#94a3b8';ctx.font='14px monospace';
  ctx.fillText('Score: '+score,W/2,H/2+10);
  ctx.fillText('Tap Start to retry',W/2,H/2+32);
}}

startBtn.onclick=()=>{{
  score=0;lives=3;carX=W/2-15;obstacles=[];roadOffset=0;speed={road_speed};lastObstacleScore=0;
  scoreEl.innerText='SCORE: 0';ctx.textAlign='left';
  gameRunning=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};

window.addEventListener('keydown',e=>{{keys[e.key]=true;if(['ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>{{keys[e.key]=false;}});
</script></body></html>"""


def _build_platformer(theme: dict, speed: float, speed_label: str, query: str) -> str:
    jump_force = -10
    gravity = 0.4
    move_speed = round(3 * speed * 100) / 100
    platform_speed = round(1.5 * speed * 100) / 100

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Platformer</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{theme['bg']};margin:0}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 uppercase tracking-widest text-[10px] font-bold">{theme['name']} PLATFORMER ({speed_label})</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 0</span>
  </div>
  <canvas id="c" width="300" height="320" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{theme['primary']}">START</button>
  <p class="text-slate-500 text-[10px] mt-2">← → to move · Space/↑ to jump</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=300,H=320;
let keys={{}},gameRunning=false,gameInterval,score=0,frameCount=0;
let player,platforms,coins;

function initGame(){{
  player={{x:60,y:240,w:22,h:22,vx:0,vy:0,onGround:false,color:'{theme["primary"]}'}};
  platforms=[
    {{x:0,y:300,w:300,h:20,color:'#334155',moving:false}},
    {{x:50,y:240,w:80,h:12,color:'{theme["secondary"]}',moving:false}},
    {{x:180,y:200,w:80,h:12,color:'{theme["secondary"]}',moving:true,dir:1,range:60,origX:180}},
    {{x:30,y:160,w:70,h:12,color:'{theme["secondary"]}',moving:false}},
    {{x:160,y:120,w:90,h:12,color:'{theme["secondary"]}',moving:true,dir:-1,range:50,origX:160}},
    {{x:20,y:80,w:60,h:12,color:'{theme["secondary"]}',moving:false}},
  ];
  coins=platforms.slice(1).map(p=>{{
    return {{x:p.x+p.w/2-8,y:p.y-24,w:16,h:16,collected:false}};
  }});
  score=0;frameCount=0;scoreEl.innerText='SCORE: 0';
}}

function update(){{
  frameCount++;
  // Move platforms
  platforms.forEach(p=>{{
    if(p.moving){{
      p.x+=1.5*p.dir;
      if(p.x>p.origX+p.range||p.x<p.origX-p.range)p.dir=-p.dir;
    }}
  }});

  // Player movement
  if(keys['ArrowLeft']||keys['a'])player.vx=-{move_speed};
  else if(keys['ArrowRight']||keys['d'])player.vx={move_speed};
  else player.vx*=0.8;

  player.vy+={gravity};
  player.x+=player.vx;player.y+=player.vy;
  player.onGround=false;

  // Clamp X
  player.x=Math.max(0,Math.min(W-player.w,player.x));

  // Platform collision
  platforms.forEach(p=>{{
    if(player.x+player.w>p.x&&player.x<p.x+p.w&&
       player.y+player.h>p.y&&player.y+player.h<p.y+20&&player.vy>0){{
      player.y=p.y-player.h;player.vy=0;player.onGround=true;
    }}
  }});

  // Jump
  if((keys[' ']||keys['ArrowUp']||keys['w'])&&player.onGround){{
    player.vy={jump_force};player.onGround=false;
  }}

  // Coins
  coins.forEach(co=>{{
    if(!co.collected&&player.x<co.x+co.w&&player.x+player.w>co.x&&
       player.y<co.y+co.h&&player.y+player.h>co.y){{
      co.collected=true;score+=10;scoreEl.innerText='SCORE: '+score;
    }}
  }});
  // Respawn coins
  if(coins.every(co=>co.collected)){{
    coins.forEach(co=>co.collected=false);score+=50;
  }}

  // Fall death
  if(player.y>H+50){{
    player.x=60;player.y=240;player.vy=0;player.vx=0;
    if(score>0)score-=5;scoreEl.innerText='SCORE: '+score;
  }}

  draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Stars background
  ctx.fillStyle='rgba(255,255,255,0.3)';
  for(let i=0;i<30;i++){{let px=(i*73+frameCount)%W,py=(i*37)%H;ctx.fillRect(px,py,1,1);}}
  // Platforms
  platforms.forEach(p=>{{
    ctx.fillStyle=p.color;
    ctx.beginPath();ctx.roundRect(p.x,p.y,p.w,p.h,3);ctx.fill();
  }});
  // Coins
  coins.forEach(co=>{{
    if(!co.collected){{
      ctx.fillStyle='{theme["accent"]}';
      ctx.beginPath();ctx.arc(co.x+co.w/2,co.y+co.h/2,8,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='rgba(255,255,255,0.6)';ctx.font='10px serif';ctx.textAlign='center';
      ctx.fillText('★',co.x+co.w/2,co.y+co.h/2+4);
    }}
  }});
  // Player
  ctx.fillStyle=player.color;
  ctx.beginPath();ctx.roundRect(player.x,player.y,player.w,player.h,4);ctx.fill();
  // Player eyes
  ctx.fillStyle='#fff';ctx.fillRect(player.x+4,player.y+5,5,5);ctx.fillRect(player.x+13,player.y+5,5,5);
  ctx.fillStyle='#020617';ctx.fillRect(player.x+6,player.y+7,2,2);ctx.fillRect(player.x+15,player.y+7,2,2);
  ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  initGame();gameRunning=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};

window.addEventListener('keydown',e=>{{keys[e.key]=true;if([' ','ArrowUp','ArrowLeft','ArrowRight'].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""


def _build_maze(theme: dict, speed: float, speed_label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Maze</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{theme['bg']};margin:0}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 uppercase tracking-widest text-[10px] font-bold">{theme['name']} MAZE ({speed_label})</span>
    <span id="status" style="color:{theme['primary']}">FIND THE EXIT ★</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{theme['primary']}">NEW MAZE</button>
  <p class="text-slate-500 text-[10px] mt-2">Arrow keys or WASD to move</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const statusEl=document.getElementById('status'),startBtn=document.getElementById('startBtn');
const COLS=15,ROWS=15,CELL=20,W=300,H=300;
let grid,player,keys={{}},gameInterval;

function Cell(col,row){{
  this.col=col;this.row=row;this.walls={{top:true,right:true,bottom:true,left:true}};
  this.visited=false;
}}

function generateMaze(){{
  grid=[];
  for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++)grid.push(new Cell(c,r));
  const idx=(c,r)=>r*COLS+c;
  const neighbors=cell=>{{
    const n=[];
    const{{col:c,row:r}}=cell;
    if(r>0&&!grid[idx(c,r-1)].visited)n.push(grid[idx(c,r-1)]);
    if(c<COLS-1&&!grid[idx(c+1,r)].visited)n.push(grid[idx(c+1,r)]);
    if(r<ROWS-1&&!grid[idx(c,r+1)].visited)n.push(grid[idx(c,r+1)]);
    if(c>0&&!grid[idx(c-1,r)].visited)n.push(grid[idx(c-1,r)]);
    return n;
  }};
  const removeWall=(a,b)=>{{
    const dc=b.col-a.col,dr=b.row-a.row;
    if(dc===1){{a.walls.right=false;b.walls.left=false;}}
    if(dc===-1){{a.walls.left=false;b.walls.right=false;}}
    if(dr===1){{a.walls.bottom=false;b.walls.top=false;}}
    if(dr===-1){{a.walls.top=false;b.walls.bottom=false;}}
  }};
  let current=grid[0],stack=[current];current.visited=true;
  while(stack.length){{
    const ns=neighbors(current);
    if(ns.length){{
      const next=ns[Math.floor(Math.random()*ns.length)];
      next.visited=true;removeWall(current,next);stack.push(next);current=next;
    }}else{{current=stack.pop();}}
  }}
  player={{col:0,row:0,x:CELL/2,y:CELL/2}};
  statusEl.innerText='FIND THE EXIT ★';
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='{theme["primary"]}';ctx.lineWidth=1.5;
  grid.forEach(cell=>{{
    const x=cell.col*CELL,y=cell.row*CELL;
    if(cell.walls.top){{ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+CELL,y);ctx.stroke();}}
    if(cell.walls.right){{ctx.beginPath();ctx.moveTo(x+CELL,y);ctx.lineTo(x+CELL,y+CELL);ctx.stroke();}}
    if(cell.walls.bottom){{ctx.beginPath();ctx.moveTo(x,y+CELL);ctx.lineTo(x+CELL,y+CELL);ctx.stroke();}}
    if(cell.walls.left){{ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+CELL);ctx.stroke();}}
  }});
  // Exit
  ctx.fillStyle='{theme["accent"]}';ctx.fillRect((COLS-1)*CELL+3,(ROWS-1)*CELL+3,CELL-6,CELL-6);
  ctx.fillStyle='#fff';ctx.font='12px serif';ctx.textAlign='center';
  ctx.fillText('★',(COLS-1)*CELL+CELL/2,(ROWS-1)*CELL+CELL/2+4);
  // Player
  ctx.fillStyle='{theme["secondary"]}';
  ctx.beginPath();ctx.arc(player.x,player.y,7,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(player.x,player.y,3,0,Math.PI*2);ctx.fill();
  ctx.textAlign='left';
}}

function canMove(col,row,dir){{
  const idx=row*COLS+col;
  if(idx<0||idx>=grid.length)return false;
  return!grid[idx].walls[dir];
}}

function update(){{
  if(keys['ArrowUp']||keys['w']){{if(canMove(player.col,player.row,'top')){{player.row--;player.y-=CELL;}}}}
  if(keys['ArrowDown']||keys['s']){{if(canMove(player.col,player.row,'bottom')){{player.row++;player.y+=CELL;}}}}
  if(keys['ArrowLeft']||keys['a']){{if(canMove(player.col,player.row,'left')){{player.col--;player.x-=CELL;}}}}
  if(keys['ArrowRight']||keys['d']){{if(canMove(player.col,player.row,'right')){{player.col++;player.x+=CELL;}}}}
  Object.keys(keys).forEach(k=>delete keys[k]);
  if(player.col===COLS-1&&player.row===ROWS-1){{
    statusEl.innerText='🎉 YOU ESCAPED!';
    setTimeout(()=>{{generateMaze();draw();}},1500);
  }}
  draw();
}}

startBtn.onclick=()=>{{
  generateMaze();draw();
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,100);
}};
window.addEventListener('keydown',e=>{{
  keys[e.key]=true;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();
}});
</script></body></html>"""


def _build_memory(theme: dict) -> str:
    symbols = "🐶🐱🦊🐸🦁🐯🦄🐙🦋🌸🍕🎮🚀🌙⭐🎵"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Memory Match</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background:{theme['bg']};margin:0}}
.card{{width:60px;height:60px;border-radius:10px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:24px;transition:transform 0.15s;border:2px solid {theme['primary']}33;background:{theme['surface'] if 'surface' in theme else '#1e293b'};}}
.card:hover{{transform:scale(1.05)}}
.card.flipped{{background:{theme['primary']}22;border-color:{theme['primary']}}}
.card.matched{{background:{theme['primary']}44;border-color:{theme['primary']};opacity:0.7;cursor:default}}
</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 uppercase tracking-widest text-[10px] font-bold">{theme['name']} MEMORY</span>
    <span id="status" style="color:{theme['primary']}">Moves: 0 | Pairs: 0/8</span>
  </div>
  <div id="board" class="grid grid-cols-4 gap-2 mb-4"></div>
  <button id="startBtn" class="w-full py-2 rounded-xl text-xs font-bold" style="background:{theme['primary']}">NEW GAME</button>
</div>
<script>
const symbols='{symbols}'.split('');
const board=document.getElementById('board'),statusEl=document.getElementById('status'),startBtn=document.getElementById('startBtn');
let cards=[],flipped=[],matched=0,moves=0,locked=false;

function shuffle(a){{return a.sort(()=>Math.random()-0.5);}}

function startGame(){{
  const pairs=shuffle([...symbols.slice(0,8),...symbols.slice(0,8)]);
  cards=[];flipped=[];matched=0;moves=0;locked=false;
  board.innerHTML='';
  statusEl.innerText='Moves: 0 | Pairs: 0/8';
  pairs.forEach((sym,i)=>{{
    const card=document.createElement('div');
    card.className='card';
    card.dataset.sym=sym;card.dataset.idx=i;
    card.innerText='?';
    card.onclick=()=>flip(card,sym);
    board.appendChild(card);
    cards.push(card);
  }});
}}

function flip(card,sym){{
  if(locked||card.classList.contains('flipped')||card.classList.contains('matched'))return;
  card.classList.add('flipped');card.innerText=sym;flipped.push(card);
  if(flipped.length===2){{
    moves++;locked=true;
    if(flipped[0].dataset.sym===flipped[1].dataset.sym){{
      flipped.forEach(c=>c.classList.replace('flipped','matched'));
      matched++;flipped=[];locked=false;
      statusEl.innerText='Moves: '+moves+' | Pairs: '+matched+'/8';
      if(matched===8)setTimeout(()=>statusEl.innerText='🎉 CLEARED in '+moves+' moves!',200);
    }}else{{
      setTimeout(()=>{{
        flipped.forEach(c=>{{c.classList.remove('flipped');c.innerText='?';}});
        flipped=[];locked=false;
        statusEl.innerText='Moves: '+moves+' | Pairs: '+matched+'/8';
      }},900);
    }}
  }}
}}
startBtn.onclick=startGame;
startGame();
</script></body></html>"""


def _build_zombie(theme: dict, speed: float, speed_label: str) -> str:
    zombie_speed = round(0.6 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Zombie Survival</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{theme['bg']};margin:0}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 uppercase tracking-widest text-[10px] font-bold">{theme['name']} ZOMBIE ({speed_label})</span>
    <span id="hud" style="color:{theme['primary']}">WAVE 1 | KILLS: 0</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{theme['primary']}">SURVIVE</button>
  <p class="text-slate-500 text-[10px] mt-2">WASD/Arrows to move · Click canvas to shoot</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const hudEl=document.getElementById('hud'),startBtn=document.getElementById('startBtn');
const W=300,H=300;
let player,zombies,bullets,keys={{}},kills,wave,gameRunning,gameInterval,mouseX=W/2,mouseY=H/2;

function initGame(){{
  player={{x:W/2,y:H/2,r:12,hp:5,color:'{theme["primary"]}'}};
  zombies=[];bullets=[];kills=0;wave=1;spawnWave();
}}

function spawnWave(){{
  const count=3+wave*2;
  for(let i=0;i<count;i++){{
    const edge=Math.floor(Math.random()*4);
    let x=Math.random()*W,y=Math.random()*H;
    if(edge===0)y=-20;else if(edge===1)y=H+20;
    else if(edge===2)x=-20;else x=W+20;
    zombies.push({{x,y,r:10,hp:2+Math.floor(wave/2),color:'#22c55e',speed:{zombie_speed}+wave*0.05}});
  }}
}}

c.addEventListener('click',e=>{{
  if(!gameRunning)return;
  const rect=c.getBoundingClientRect();
  const mx=e.clientX-rect.left,my=e.clientY-rect.top;
  const dx=mx-player.x,dy=my-player.y,dist=Math.hypot(dx,dy);
  bullets.push({{x:player.x,y:player.y,vx:dx/dist*7,vy:dy/dist*7,r:4}});
}});
c.addEventListener('mousemove',e=>{{
  const rect=c.getBoundingClientRect();mouseX=e.clientX-rect.left;mouseY=e.clientY-rect.top;
}});

function update(){{
  const spd=3;
  if(keys['ArrowLeft']||keys['a'])player.x=Math.max(player.r,player.x-spd);
  if(keys['ArrowRight']||keys['d'])player.x=Math.min(W-player.r,player.x+spd);
  if(keys['ArrowUp']||keys['w'])player.y=Math.max(player.r,player.y-spd);
  if(keys['ArrowDown']||keys['s'])player.y=Math.min(H-player.r,player.y+spd);

  bullets.forEach(b=>{{b.x+=b.vx;b.y+=b.vy;}});
  bullets=bullets.filter(b=>b.x>-20&&b.x<W+20&&b.y>-20&&b.y<H+20);

  zombies.forEach(z=>{{
    const dx=player.x-z.x,dy=player.y-z.y,dist=Math.hypot(dx,dy);
    z.x+=dx/dist*z.speed;z.y+=dy/dist*z.speed;
    if(dist<player.r+z.r){{
      player.hp--;z.x-=dx/dist*5;z.y-=dy/dist*5;
      if(player.hp<=0){{gameOver();return;}}
    }}
    bullets.forEach(b=>{{
      if(Math.hypot(b.x-z.x,b.y-z.y)<z.r+b.r){{
        z.hp--;b.x=-999;if(z.hp<=0){{z.dead=true;kills++;}}
      }}
    }});
  }});
  zombies=zombies.filter(z=>!z.dead);
  if(zombies.length===0){{wave++;spawnWave();}}

  hudEl.innerText='WAVE '+wave+' | KILLS: '+kills;
  draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Grid
  ctx.strokeStyle='rgba(51,65,85,0.4)';ctx.lineWidth=0.5;
  for(let i=0;i<W;i+=20){{ctx.beginPath();ctx.moveTo(i,0);ctx.lineTo(i,H);ctx.stroke();}}
  for(let j=0;j<H;j+=20){{ctx.beginPath();ctx.moveTo(0,j);ctx.lineTo(W,j);ctx.stroke();}}
  // Zombies
  zombies.forEach(z=>{{
    ctx.fillStyle='#166534';ctx.beginPath();ctx.arc(z.x,z.y,z.r,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#86efac';ctx.font='bold 10px monospace';ctx.textAlign='center';
    ctx.fillText('Z',z.x,z.y+4);
  }});
  // Bullets
  ctx.fillStyle='{theme["accent"]}';
  bullets.forEach(b=>{{ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);ctx.fill();}});
  // Player
  ctx.fillStyle=player.color;ctx.beginPath();ctx.arc(player.x,player.y,player.r,0,Math.PI*2);ctx.fill();
  // Aim line
  const dx=mouseX-player.x,dy=mouseY-player.y,dist=Math.hypot(dx,dy);
  ctx.strokeStyle='rgba(255,255,255,0.2)';ctx.lineWidth=1;ctx.setLineDash([4,4]);
  ctx.beginPath();ctx.moveTo(player.x,player.y);ctx.lineTo(player.x+dx/dist*40,player.y+dy/dist*40);ctx.stroke();
  ctx.setLineDash([]);
  // HP bar
  ctx.fillStyle='#334155';ctx.fillRect(6,6,80,8);
  ctx.fillStyle='#ef4444';ctx.fillRect(6,6,80*(player.hp/5),8);
  ctx.fillStyle='#fff';ctx.font='8px monospace';ctx.textAlign='left';ctx.fillText('HP',90,14);
}}

function gameOver(){{
  gameRunning=false;clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#ef4444';ctx.font='bold 22px Courier New';ctx.textAlign='center';
  ctx.fillText('INFECTED!',W/2,H/2-20);
  ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
  ctx.fillText('Wave '+wave+' | Kills: '+kills,W/2,H/2+10);
}}

startBtn.onclick=()=>{{
  initGame();gameRunning=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""


def _build_snake(theme: dict, speed: float, speed_label: str, query: str) -> str:
    interval = round(120 / speed)
    has_obstacles = any(w in query for w in ("obstacle", "wall", "barrier", "brick"))
    has_wrap = any(w in query for w in ("wrap", "endless", "borderless"))
    obstacles_js = "[{x:60,y:60},{x:210,y:210},{x:120,y:180}]" if has_obstacles else "[]"
    boundary = (
        "if(head.x<0)head.x=300-grid;"
        "if(head.x>=300)head.x=0;"
        "if(head.y<0)head.y=300-grid;"
        "if(head.y>=300)head.y=0;"
        if has_wrap else
        "if(head.x<0||head.x>=300||head.y<0||head.y>=300)return gameOver();"
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Snake</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">{theme['name']} ({speed_label})</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">START GAME</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const grid=15,obstacles={obstacles_js};
let score=0,dx=grid,dy=0,snake,food,gameInterval;
function randPos(){{return Math.floor(Math.random()*(300/grid))*grid;}}
function spawnFood(){{food={{x:randPos(),y:randPos()}};
  if(snake.some(p=>p.x===food.x&&p.y===food.y))spawnFood();}}
function gameOver(){{clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="{theme['accent']}";ctx.font="bold 18px Courier New";ctx.textAlign="center";
  ctx.fillText("GAME OVER",150,140);}}
function update(){{
  let head={{x:snake[0].x+dx,y:snake[0].y+dy}};
  {boundary}
  if(snake.some(p=>p.x===head.x&&p.y===head.y))return gameOver();
  if(obstacles.some(o=>o.x===head.x&&o.y===head.y))return gameOver();
  snake.unshift(head);
  if(head.x===food.x&&head.y===food.y){{score+=10;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');spawnFood();}}
  else{{snake.pop();}}
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme["accent"]}';ctx.fillRect(food.x,food.y,grid,grid);
  snake.forEach((p,i)=>{{ctx.fillStyle=i===0?'{theme["primary"]}':'{theme["secondary"]}';ctx.fillRect(p.x,p.y,grid,grid);}});
}}
startBtn.onclick=()=>{{score=0;scoreEl.innerText='SCORE: 000';
  snake=[{{x:120,y:120}},{{x:105,y:120}},{{x:90,y:120}}];dx=grid;dy=0;spawnFood();
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,{interval});}};
window.onkeydown=e=>{{
  if((e.key==='ArrowUp'||e.key==='w')&&dy===0){{dx=0;dy=-grid;}}
  if((e.key==='ArrowDown'||e.key==='s')&&dy===0){{dx=0;dy=grid;}}
  if((e.key==='ArrowLeft'||e.key==='a')&&dx===0){{dx=-grid;dy=0;}}
  if((e.key==='ArrowRight'||e.key==='d')&&dx===0){{dx=grid;dy=0;}}
}};
</script></body></html>"""


def _build_pong(theme: dict, speed: float, speed_label: str) -> str:
    bx = round(2 * speed * 100) / 100
    by = round(1.5 * speed * 100) / 100
    cpu_speed = round(1.5 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Pong</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}</style>
</head>
<body class="text-white min-h-screen flex items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">{theme['name']} ({speed_label})</span>
    <span id="score" style="color:{theme['primary']}">YOU: 0 | CPU: 0</span>
  </div>
  <canvas id="gameCanvas" width="300" height="200" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">START MATCH</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let playerY=70,cpuY=70,ballX=150,ballY=100,ballDX={bx},ballDY={by};
let playerScore=0,cpuScore=0,running=false,gameInterval;
function update(){{if(!running)return;
  ballX+=ballDX;ballY+=ballDY;
  if(cpuY+15<ballY)cpuY+={cpu_speed};else if(cpuY+15>ballY)cpuY-={cpu_speed};
  if(ballY<=0||ballY>=200)ballDY=-ballDY;
  if(ballX<=15&&ballY>=playerY&&ballY<=playerY+40){{ballDX=-ballDX*1.05;ballX=16;}}
  if(ballX>=285&&ballY>=cpuY&&ballY<=cpuY+40){{ballDX=-ballDX*1.05;ballX=284;}}
  if(ballX<0){{cpuScore++;resetBall();}}if(ballX>300){{playerScore++;resetBall();}}
  scoreEl.innerText="YOU: "+playerScore+" | CPU: "+cpuScore;
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,200);
  ctx.fillStyle='{theme["secondary"]}';ctx.fillRect(5,playerY,10,40);ctx.fillRect(285,cpuY,10,40);
  ctx.fillStyle='{theme["accent"]}';ctx.beginPath();ctx.arc(ballX,ballY,5,0,Math.PI*2);ctx.fill();
}}
function resetBall(){{ballX=150;ballY=100;ballDX=(Math.random()>0.5?{bx}:-{bx});ballDY=(Math.random()>0.5?{by}:-{by});
  if(playerScore>=5||cpuScore>=5){{running=false;clearInterval(gameInterval);
    ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,200);
    ctx.fillStyle=playerScore>=5?"{theme['primary']}":"{theme['accent']}";
    ctx.font="bold 16px Courier New";ctx.textAlign="center";
    ctx.fillText(playerScore>=5?"YOU WIN!":"CPU WINS",150,100);}}}}
startBtn.onclick=()=>{{playerScore=0;cpuScore=0;playerY=70;cpuY=70;running=true;resetBall();
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,16);}};
window.onmousemove=e=>{{const rect=canvas.getBoundingClientRect();playerY=Math.max(0,Math.min(160,e.clientY-rect.top-20));}};
</script></body></html>"""


def _build_flappy(theme: dict, speed: float, speed_label: str) -> str:
    pipe_speed = round(2 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Flappy</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-4">
    <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">{theme['name']}</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">TAP CANVAS TO FLY</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let birdY=150,velocity=0,score=0,running=false,gameInterval,pipes=[];
function update(){{if(!running)return;
  velocity+=0.25;birdY+=velocity;
  if(birdY>=290||birdY<=5){{gameOver();return;}}
  if(!pipes.length||pipes[pipes.length-1].x<180)
    pipes.push({{x:300,top:Math.random()*100+40,bottom:Math.random()*100+40}});
  pipes.forEach(p=>{{p.x-={pipe_speed};
    if(p.x===50){{score++;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');}}
    if(p.x<75&&p.x>35&&(birdY<p.top||birdY>300-p.bottom)){{gameOver();return;}}}});
  pipes=pipes.filter(p=>p.x>-30);
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme["accent"]}';ctx.beginPath();ctx.arc(60,birdY,8,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{theme["primary"]}';
  pipes.forEach(p=>{{ctx.fillRect(p.x,0,20,p.top);ctx.fillRect(p.x,300-p.bottom,20,p.bottom);}});
}}
function gameOver(){{running=false;clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="{theme['accent']}";ctx.font="bold 20px Courier New";ctx.textAlign="center";
  ctx.fillText("CRASHED!",150,140);}}
function start(){{birdY=150;velocity=0;score=0;pipes=[];running=true;scoreEl.innerText="SCORE: 000";
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,20);}}
startBtn.onclick=start;canvas.onclick=()=>{{velocity=-5.5;}};
</script></body></html>"""


def _build_brickbreaker(theme: dict, speed: float, speed_label: str) -> str:
    bx = round(2 * speed * 100) / 100
    by = round(-2 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Brickbreaker</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">{theme['name']}</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">START BRICKS</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let score=0,paddleX=120,ballX=150,ballY=240,ballDX={bx},ballDY={by},running=false,gameInterval,bricks=[];
function initBricks(){{bricks=[];
  for(let r=0;r<4;r++)for(let c=0;c<6;c++)bricks.push({{x:c*46+14,y:r*16+30,active:true}});}}
function update(){{if(!running)return;
  ballX+=ballDX;ballY+=ballDY;
  if(ballX<=5||ballX>=295)ballDX=-ballDX;
  if(ballY<=5)ballDY=-ballDY;
  if(ballY>=295)return gameOver();
  if(ballY>=270&&ballY<=278&&ballX>=paddleX&&ballX<=paddleX+60){{ballDY=-Math.abs(ballDY);ballDX=(ballX-(paddleX+30))*0.15;}}
  bricks.forEach(b=>{{if(b.active&&ballX>=b.x&&ballX<=b.x+42&&ballY>=b.y&&ballY<=b.y+12){{b.active=false;ballDY=-ballDY;score+=10;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');}}}});
  if(bricks.every(b=>!b.active)){{running=false;clearInterval(gameInterval);
    ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
    ctx.fillStyle="{theme['primary']}";ctx.font="bold 20px Courier New";ctx.textAlign="center";ctx.fillText("YOU WIN!",150,150);}}
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme["secondary"]}';ctx.fillRect(paddleX,275,60,10);
  ctx.fillStyle='{theme["accent"]}';ctx.beginPath();ctx.arc(ballX,ballY,5,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{theme["primary"]}';bricks.forEach(b=>{{if(b.active)ctx.fillRect(b.x,b.y,42,12);}});
}}
function gameOver(){{running=false;clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="{theme['accent']}";ctx.font="bold 20px Courier New";ctx.textAlign="center";ctx.fillText("GAME OVER",150,150);}}
startBtn.onclick=()=>{{score=0;scoreEl.innerText='SCORE: 000';ballX=150;ballY=240;paddleX=120;
  ballDX={bx};ballDY={by};initBricks();running=true;
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,16);}};
window.onmousemove=e=>{{const rect=canvas.getBoundingClientRect();paddleX=Math.max(0,Math.min(240,e.clientX-rect.left-30));}};
</script></body></html>"""


def _build_clicker(theme: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Clicker</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}</style>
</head>
<body class="text-slate-100 min-h-screen flex items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-3xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm space-y-4">
  <div class="text-center font-mono space-y-1">
    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{theme['name']} IDLE</span>
    <h1 class="text-3xl font-extrabold" style="color:{theme['primary']}"><span id="points">0</span> COINS</h1>
    <p class="text-[10px] text-slate-400"><span id="cps">0</span> Coins / sec</p>
  </div>
  <button id="clickBtn" class="h-32 w-32 rounded-full border-4 flex items-center justify-center text-3xl transition-transform active:scale-95 shadow-2xl"
    style="background-color:{theme['bg']};border-color:{theme['primary']};box-shadow:0 0 20px {theme['primary']}">✨</button>
  <div class="w-full space-y-2">
    <button id="buyClicker" class="w-full py-2 px-3 bg-slate-950 border border-slate-800 rounded-xl text-left text-xs font-semibold flex justify-between">
      <span>🤖 Auto-Tapper (+1 CPS)</span><span class="font-mono text-slate-400"><span id="clickerCost">15</span> Coins</span>
    </button>
    <button id="buyMultiplier" class="w-full py-2 px-3 bg-slate-950 border border-slate-800 rounded-xl text-left text-xs font-semibold flex justify-between">
      <span>🚀 Multiplier (+2 Click)</span><span class="font-mono text-slate-400"><span id="multiCost">50</span> Coins</span>
    </button>
  </div>
</div>
<script>
let points=0,cps=0,clickPower=1,clickerCost=15,multiplierCost=50;
const pts=document.getElementById('points'),cpsEl=document.getElementById('cps');
const buyCl=document.getElementById('buyClicker'),buyMu=document.getElementById('buyMultiplier');
const clCostEl=document.getElementById('clickerCost'),muCostEl=document.getElementById('multiCost');
function ui(){{pts.innerText=points;cpsEl.innerText=cps;clCostEl.innerText=clickerCost;muCostEl.innerText=multiplierCost;}}
document.getElementById('clickBtn').onclick=()=>{{points+=clickPower;ui();}};
buyCl.onclick=()=>{{if(points>=clickerCost){{points-=clickerCost;cps+=1;clickerCost=Math.round(clickerCost*1.5);ui();}}}};
buyMu.onclick=()=>{{if(points>=multiplierCost){{points-=multiplierCost;clickPower+=2;multiplierCost=Math.round(multiplierCost*1.8);ui();}}}};
setInterval(()=>{{points+=cps;ui();}},1000);
</script></body></html>"""


def _build_spaceshooter(theme: dict, speed: float, speed_label: str) -> str:
    alien_speed = round(1 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Space Shooter</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}</style>
</head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] font-bold uppercase tracking-widest">{theme['name']} SPACE</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">LAUNCH FIGHTER</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let score=0,playerX=135,lasers=[],aliens=[],running=false,gameInterval,alienDir=1;
function spawnAliens(){{aliens=[];for(let r=0;r<3;r++)for(let c=0;c<6;c++)aliens.push({{x:c*40+30,y:r*30+30,active:true}});}}
function update(){{if(!running)return;
  lasers.forEach(l=>l.y-=4);lasers=lasers.filter(l=>l.y>0);
  let edgeHit=false;
  aliens.forEach(a=>{{if(a.active){{a.x+=alienDir*{alien_speed};if(a.x>=280||a.x<=10)edgeHit=true;}}}});
  if(edgeHit){{alienDir=-alienDir;aliens.forEach(a=>{{if(a.active)a.y+=10;}});}}
  lasers.forEach(l=>{{aliens.forEach(a=>{{
    if(a.active&&l.y<=a.y+15&&l.y>=a.y&&l.x>=a.x&&l.x<=a.x+15){{a.active=false;l.y=-100;score+=10;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');}}}});}});
  if(aliens.every(a=>!a.active))spawnAliens();
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme["primary"]}';ctx.fillRect(playerX,275,30,15);
  ctx.fillStyle='{theme["accent"]}';lasers.forEach(l=>ctx.fillRect(l.x,l.y,4,10));
  ctx.fillStyle='{theme["secondary"]}';aliens.forEach(a=>{{if(a.active)ctx.fillRect(a.x,a.y,15,15);}});
}}
startBtn.onclick=()=>{{score=0;scoreEl.innerText='SCORE: 000';lasers=[];playerX=135;alienDir=1;spawnAliens();running=true;
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,16);}};
window.onkeydown=e=>{{
  if(e.key==='ArrowLeft'||e.key==='a')playerX=Math.max(0,playerX-15);
  if(e.key==='ArrowRight'||e.key==='d')playerX=Math.min(270,playerX+15);
  if(e.key===' '||e.key==='Enter')lasers.push({{x:playerX+13,y:270}});
}};
</script></body></html>"""


# ══════════════════════════════════════════════════════════════
# NEW GAME BUILDERS
# ══════════════════════════════════════════════════════════════

def _build_whack(theme: dict) -> str:
    bg = theme["bg"]
    primary = theme["primary"]
    accent = theme["accent"]
    secondary = theme["secondary"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Whack-a-Mole</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}
.hole{{width:70px;height:70px;border-radius:50%;background:#1e293b;border:3px solid {secondary};
      display:flex;align-items:center;justify-content:center;font-size:32px;cursor:pointer;
      transition:transform 0.1s;user-select:none}}
.hole.active{{background:{primary}33;border-color:{primary};transform:scale(1.1)}}
.hole:active{{transform:scale(0.95)}}
</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs space-y-3">
  <div class="flex justify-between w-full text-xs font-mono">
    <span id="timer" style="color:{accent}">TIME: 30</span>
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">WHACK-A-MOLE</span>
    <span id="score" style="color:{primary}">SCORE: 0</span>
  </div>
  <div class="grid grid-cols-3 gap-3" id="board"></div>
  <button id="startBtn" class="w-full py-2 rounded-xl text-xs font-bold" style="background:{primary}">START</button>
</div>
<script>
const board=document.getElementById('board'),scoreEl=document.getElementById('score'),timerEl=document.getElementById('timer');
let score=0,timeLeft=30,running=false,moleInterval,timerInterval,activeHole=-1;
const holes=[];
for(let i=0;i<9;i++){{
  const h=document.createElement('div');h.className='hole';h.innerHTML='🟫';
  h.dataset.idx=i;
  h.onclick=()=>{{
    if(!running||activeHole!==i)return;
    score+=10;scoreEl.innerText='SCORE: '+score;
    h.innerHTML='💥';h.classList.remove('active');activeHole=-1;
    setTimeout(()=>{{h.innerHTML='🟫';}},200);
  }};
  board.appendChild(h);holes.push(h);
}}
function showMole(){{
  if(activeHole>=0){{holes[activeHole].innerHTML='🟫';holes[activeHole].classList.remove('active');}}
  activeHole=Math.floor(Math.random()*9);
  holes[activeHole].innerHTML='🐹';holes[activeHole].classList.add('active');
  setTimeout(()=>{{
    if(activeHole>=0){{holes[activeHole].innerHTML='🟫';holes[activeHole].classList.remove('active');activeHole=-1;}}
  }},800);
}}
document.getElementById('startBtn').onclick=()=>{{
  score=0;timeLeft=30;running=true;
  scoreEl.innerText='SCORE: 0';timerEl.innerText='TIME: 30';
  holes.forEach(h=>{{h.innerHTML='🟫';h.classList.remove('active');}});activeHole=-1;
  clearInterval(moleInterval);clearInterval(timerInterval);
  moleInterval=setInterval(showMole,700);
  timerInterval=setInterval(()=>{{
    timeLeft--;timerEl.innerText='TIME: '+timeLeft;
    if(timeLeft<=0){{
      running=false;clearInterval(moleInterval);clearInterval(timerInterval);
      holes.forEach(h=>h.classList.remove('active'));
      timerEl.innerText='DONE!';
    }}
  }},1000);
}};
</script></body></html>"""


def _build_2048(theme: dict) -> str:
    bg = theme["bg"]
    primary = theme["primary"]
    accent = theme["accent"]
    tile_colors_js = (
        "{2:'#334155',4:'#475569',8:'#c2410c',16:'#dc2626',"
        "32:'#db2777',64:'#9333ea',128:'#d97706',256:'#ca8a04',"
        "512:'#16a34a',1024:'#0891b2',2048:'#4f46e5'}"
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>2048</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background:{bg};margin:0}}
.tile{{width:65px;height:65px;border-radius:8px;display:flex;align-items:center;
      justify-content:center;font-weight:800;font-size:20px;transition:all 0.1s;
      background:#1e293b;color:#e2e8f0;border:2px solid #334155}}
</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs space-y-3">
  <div class="flex justify-between w-full text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">2048</span>
    <span id="score" style="color:{primary}">SCORE: 0</span>
  </div>
  <div id="grid" class="grid grid-cols-4 gap-2"></div>
  <div id="msg" class="text-xs font-bold" style="color:{accent}">Use Arrow Keys to merge tiles!</div>
  <button id="newBtn" class="w-full py-2 rounded-xl text-xs font-bold" style="background:{primary}">NEW GAME</button>
</div>
<script>
const gridEl=document.getElementById('grid'),scoreEl=document.getElementById('score'),msgEl=document.getElementById('msg');
const COLORS={tile_colors_js};
let board,score;
function newGame(){{
  board=Array.from({{length:4}},()=>Array(4).fill(0));
  score=0;msgEl.innerText='Merge tiles to reach 2048!';
  addTile();addTile();render();
}}
function addTile(){{
  const empty=[];
  for(let r=0;r<4;r++)for(let c=0;c<4;c++)if(!board[r][c])empty.push([r,c]);
  if(!empty.length)return;
  const[r,c]=empty[Math.floor(Math.random()*empty.length)];
  board[r][c]=Math.random()<0.9?2:4;
}}
function render(){{
  gridEl.innerHTML='';
  board.forEach(row=>row.forEach(v=>{{
    const d=document.createElement('div');d.className='tile';
    if(v){{d.innerText=v;d.style.background=COLORS[v]||'#{primary.lstrip("#")}';
           d.style.fontSize=v>=1000?'14px':v>=100?'17px':'20px';}}
    gridEl.appendChild(d);
  }}));
  scoreEl.innerText='SCORE: '+score;
}}
function slide(row){{
  let r=row.filter(x=>x);
  for(let i=0;i<r.length-1;i++){{
    if(r[i]===r[i+1]){{score+=r[i]*2;r[i]*=2;r[i+1]=0;}}
  }}
  r=r.filter(x=>x);
  while(r.length<4)r.push(0);
  return r;
}}
function move(dir){{
  let moved=false;
  const b=board.map(r=>[...r]);
  if(dir==='left'){{board=board.map(r=>{{const s=slide(r);if(s.join()!==r.join())moved=true;return s;}});}}
  else if(dir==='right'){{board=board.map(r=>{{const s=slide([...r].reverse()).reverse();if(s.join()!==r.join())moved=true;return s;}});}}
  else if(dir==='up'){{
    for(let c=0;c<4;c++){{
      const col=board.map(r=>r[c]);const s=slide(col);
      if(s.join()!==col.join())moved=true;
      s.forEach((v,r)=>board[r][c]=v);
    }}
  }}
  else if(dir==='down'){{
    for(let c=0;c<4;c++){{
      const col=board.map(r=>r[c]).reverse();const s=slide(col).reverse();
      if(s.join()!==col.join())moved=true;
      s.forEach((v,r)=>board[r][c]=v);
    }}
  }}
  if(moved){{addTile();render();}}
  if(board.flat().includes(2048))msgEl.innerText='🎉 You reached 2048!';
  else if(!board.flat().includes(0)&&!canMove())msgEl.innerText='Game Over! Score: '+score;
}}
function canMove(){{
  for(let r=0;r<4;r++)for(let c=0;c<4;c++){{
    if(board[r][c]===0)return true;
    if(c<3&&board[r][c]===board[r][c+1])return true;
    if(r<3&&board[r][c]===board[r+1][c])return true;
  }}
  return false;
}}
window.addEventListener('keydown',e=>{{
  const map={{'ArrowLeft':'left','ArrowRight':'right','ArrowUp':'up','ArrowDown':'down'}};
  if(map[e.key]){{e.preventDefault();move(map[e.key]);}}
}});
document.getElementById('newBtn').onclick=newGame;
newGame();
</script></body></html>"""


def _build_blackjack(theme: dict) -> str:
    bg = theme["bg"]
    primary = theme["primary"]
    accent = theme["accent"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Blackjack</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background:{bg};margin:0}}
.card{{display:inline-flex;align-items:center;justify-content:center;width:48px;height:68px;
      border-radius:8px;background:#1e293b;border:2px solid #475569;font-size:13px;
      font-weight:700;margin:3px;color:#e2e8f0}}
.card.red{{color:#f43f5e}}
</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col w-full max-w-xs space-y-3">
  <div class="flex justify-between text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">BLACKJACK</span>
    <span id="balance" style="color:{primary}">💰 100</span>
  </div>
  <div>
    <p class="text-[10px] text-slate-400 font-bold uppercase mb-1">Dealer <span id="dealerTotal" class="ml-1" style="color:{accent}"></span></p>
    <div id="dealerHand" class="flex flex-wrap min-h-[76px]"></div>
  </div>
  <div>
    <p class="text-[10px] text-slate-400 font-bold uppercase mb-1">You <span id="playerTotal" class="ml-1" style="color:{primary}"></span></p>
    <div id="playerHand" class="flex flex-wrap min-h-[76px]"></div>
  </div>
  <div id="msg" class="text-center text-sm font-bold py-1" style="color:{accent}">Press Deal to play</div>
  <div class="grid grid-cols-3 gap-2">
    <button id="dealBtn" class="py-2 rounded-xl text-xs font-bold col-span-3" style="background:{primary}">DEAL (Bet 10)</button>
    <button id="hitBtn" class="py-2 rounded-xl text-xs font-bold bg-slate-700 disabled:opacity-30" disabled>HIT</button>
    <button id="standBtn" class="py-2 rounded-xl text-xs font-bold bg-slate-700 disabled:opacity-30" disabled>STAND</button>
    <button id="dblBtn" class="py-2 rounded-xl text-xs font-bold bg-slate-700 disabled:opacity-30" disabled>DOUBLE</button>
  </div>
</div>
<script>
const SUITS=['♠','♥','♦','♣'],RANKS=['A','2','3','4','5','6','7','8','9','10','J','Q','K'];
const RED_SUITS=new Set(['♥','♦']);
let deck=[],playerHand=[],dealerHand=[],balance=100,bet=10,playing=false;
const dealerEl=document.getElementById('dealerHand'),playerEl=document.getElementById('playerHand');
const dealerTotalEl=document.getElementById('dealerTotal'),playerTotalEl=document.getElementById('playerTotal');
const msgEl=document.getElementById('msg'),balanceEl=document.getElementById('balance');
const hitBtn=document.getElementById('hitBtn'),standBtn=document.getElementById('standBtn'),dblBtn=document.getElementById('dblBtn');

function buildDeck(){{
  deck=[];
  for(const s of SUITS)for(const r of RANKS)deck.push({{r,s}});
  deck.sort(()=>Math.random()-0.5);
}}
function cardVal(c){{
  if(['J','Q','K'].includes(c.r))return 10;
  if(c.r==='A')return 11;
  return parseInt(c.r);
}}
function handTotal(hand){{
  let t=hand.reduce((a,c)=>a+cardVal(c),0),aces=hand.filter(c=>c.r==='A').length;
  while(t>21&&aces>0){{t-=10;aces--;}}
  return t;
}}
function renderCard(c,hidden){{
  const d=document.createElement('div');d.className='card'+(RED_SUITS.has(c.s)?' red':'');
  d.innerText=hidden?'🂠':c.r+c.s;return d;
}}
function renderHands(hideDealer){{
  dealerEl.innerHTML='';playerEl.innerHTML='';
  dealerHand.forEach((c,i)=>dealerEl.appendChild(renderCard(c,hideDealer&&i===1)));
  playerHand.forEach(c=>playerEl.appendChild(renderCard(c,false)));
  playerTotalEl.innerText=handTotal(playerHand);
  dealerTotalEl.innerText=hideDealer?'?':handTotal(dealerHand);
}}
function setButtons(active){{
  hitBtn.disabled=!active;standBtn.disabled=!active;dblBtn.disabled=!active;
}}
function endRound(msg,win){{
  playing=false;renderHands(false);setButtons(false);
  if(win===1)balance+=bet;else if(win===-1)balance-=bet;else if(win===2)balance+=bet*2;
  balanceEl.innerText='💰 '+balance;
  msgEl.innerText=msg;
  if(balance<bet){{msgEl.innerText+=' — Out of money!';document.getElementById('dealBtn').disabled=true;}}
}}
document.getElementById('dealBtn').onclick=()=>{{
  if(balance<bet)return;
  buildDeck();playerHand=[deck.pop(),deck.pop()];dealerHand=[deck.pop(),deck.pop()];
  playing=true;msgEl.innerText='';renderHands(true);setButtons(true);
  if(handTotal(playerHand)===21){{endRound('Blackjack! You win!',2);}}
}};
hitBtn.onclick=()=>{{
  playerHand.push(deck.pop());renderHands(true);
  if(handTotal(playerHand)>21)endRound('Bust! You lose.',−1);
}};
standBtn.onclick=()=>{{
  while(handTotal(dealerHand)<17)dealerHand.push(deck.pop());
  const p=handTotal(playerHand),d=handTotal(dealerHand);
  if(d>21||p>d)endRound('You win! '+(d>21?'Dealer bust!':''),1);
  else if(p===d)endRound('Push — tie!',0);
  else endRound('Dealer wins.',−1);
}};
dblBtn.onclick=()=>{{
  playerHand.push(deck.pop());renderHands(true);
  if(handTotal(playerHand)>21){{bet*=2;endRound('Bust! You lose.',−1);bet=10;return;}}
  const prevBet=bet;bet*=2;
  while(handTotal(dealerHand)<17)dealerHand.push(deck.pop());
  const p=handTotal(playerHand),d=handTotal(dealerHand);
  if(d>21||p>d)endRound('You win! Double down!',1);
  else if(p===d)endRound('Push.',0);
  else endRound('Dealer wins.',−1);
  bet=prevBet;
}};
</script></body></html>"""


def _build_asteroids(theme: dict, speed: float, speed_label: str) -> str:
    p = theme["primary"]
    a = theme["accent"]
    s = theme["secondary"]
    bg = theme["bg"]
    bullet_speed = round(5 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Asteroids</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">ASTEROIDS ({speed_label})</span>
    <span id="hud" style="color:{p}">SCORE:0 ♥♥♥</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">LAUNCH</button>
  <p class="text-slate-500 text-[10px] mt-2">←→ Rotate · ↑ Thrust · Space Shoot</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const hudEl=document.getElementById('hud'),startBtn=document.getElementById('startBtn');
const W=300,H=300,TAU=Math.PI*2;
let ship,bullets,asteroids,keys={{}},score,lives,gameInterval,running;

function mkAsteroid(x,y,size){{
  const angle=Math.random()*TAU,spd=(Math.random()*0.8+0.4)*(2-size*0.3);
  const pts=[];const sides=7+Math.floor(Math.random()*4);
  for(let i=0;i<sides;i++){{
    const a=(i/sides)*TAU,r=size*(0.7+Math.random()*0.3);
    pts.push([Math.cos(a)*r,Math.sin(a)*r]);
  }}
  return{{x,y,vx:Math.cos(angle)*spd,vy:Math.sin(angle)*spd,size,pts,angle:0,rot:(Math.random()-0.5)*0.04}};
}}

function initGame(){{
  ship={{x:150,y:150,angle:-Math.PI/2,vx:0,vy:0,dead:false}};
  bullets=[];score=0;lives=3;
  asteroids=[mkAsteroid(30,30,40),mkAsteroid(270,30,40),mkAsteroid(150,270,40)];
}}

function drawShip(x,y,angle,color){{
  ctx.save();ctx.translate(x,y);ctx.rotate(angle);
  ctx.strokeStyle=color;ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(12,0);ctx.lineTo(-8,7);ctx.lineTo(-5,0);ctx.lineTo(-8,-7);ctx.closePath();ctx.stroke();
  ctx.restore();
}}

function update(){{
  if(!running)return;
  if(keys['ArrowLeft'])ship.angle-=0.06;
  if(keys['ArrowRight'])ship.angle+=0.06;
  if(keys['ArrowUp']){{ship.vx+=Math.cos(ship.angle)*0.2;ship.vy+=Math.sin(ship.angle)*0.2;}}
  ship.vx*=0.98;ship.vy*=0.98;
  ship.x=(ship.x+ship.vx+W)%W;ship.y=(ship.y+ship.vy+H)%H;

  bullets.forEach(b=>{{b.x=(b.x+b.vx+W)%W;b.y=(b.y+b.vy+H)%H;b.life--;}});
  bullets=bullets.filter(b=>b.life>0);

  asteroids.forEach(ast=>{{
    ast.x=(ast.x+ast.vx+W)%W;ast.y=(ast.y+ast.vy+H)%H;ast.angle+=ast.rot;
  }});

  // Bullet-asteroid collisions
  const newAsts=[];
  asteroids.forEach(ast=>{{
    let hit=false;
    bullets.forEach(b=>{{
      if(!hit&&Math.hypot(b.x-ast.x,b.y-ast.y)<ast.size){{
        hit=true;b.life=0;
        const pts=ast.size===40?3:ast.size===22?1:0;
        score+=pts===3?20:pts===1?50:100;
        if(ast.size>15){{
          newAsts.push(mkAsteroid(ast.x,ast.y,ast.size*0.55));
          newAsts.push(mkAsteroid(ast.x,ast.y,ast.size*0.55));
        }}
      }}
    }});
    if(!hit)newAsts.push(ast);
  }});
  asteroids=newAsts;
  if(!asteroids.length){{
    asteroids=[mkAsteroid(30,30,40),mkAsteroid(270,30,40),mkAsteroid(150,20,40),mkAsteroid(20,150,40)];
  }}

  // Ship-asteroid collision
  if(!ship.dead){{
    asteroids.forEach(ast=>{{
      if(Math.hypot(ship.x-ast.x,ship.y-ast.y)<ast.size-4){{
        lives--;ship.x=150;ship.y=150;ship.vx=0;ship.vy=0;
        if(lives<=0)gameOver();
      }}
    }});
  }}

  hudEl.innerText='SCORE:'+score+' '+'♥'.repeat(Math.max(0,lives));
  draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Stars
  ctx.fillStyle='rgba(255,255,255,0.25)';
  for(let i=0;i<40;i++)ctx.fillRect((i*83)%W,(i*61)%H,1,1);
  // Asteroids
  ctx.strokeStyle='{a}';ctx.lineWidth=1.5;
  asteroids.forEach(ast=>{{
    ctx.save();ctx.translate(ast.x,ast.y);ctx.rotate(ast.angle);
    ctx.beginPath();ast.pts.forEach(([px,py],i)=>i?ctx.lineTo(px,py):ctx.moveTo(px,py));
    ctx.closePath();ctx.stroke();ctx.restore();
  }});
  // Bullets
  ctx.fillStyle='{p}';
  bullets.forEach(b=>{{ctx.beginPath();ctx.arc(b.x,b.y,2,0,TAU);ctx.fill();}});
  // Ship
  drawShip(ship.x,ship.y,ship.angle,'{p}');
  if(keys['ArrowUp']){{
    // Thrust flame
    ctx.save();ctx.translate(ship.x,ship.y);ctx.rotate(ship.angle);
    ctx.strokeStyle='{s}';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(-5,3);ctx.lineTo(-12,0);ctx.lineTo(-5,-3);ctx.stroke();
    ctx.restore();
  }}
}}

function gameOver(){{
  running=false;clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-10);
  ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
  ctx.fillText('Score: '+score,W/2,H/2+15);ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  initGame();running=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{
  keys[e.key]=true;
  if(e.key===' '){{
    bullets.push({{x:ship.x,y:ship.y,vx:Math.cos(ship.angle)*{bullet_speed},vy:Math.sin(ship.angle)*{bullet_speed},life:60}});
    e.preventDefault();
  }}
  if(['ArrowLeft','ArrowRight','ArrowUp'].includes(e.key))e.preventDefault();
}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""


def _build_fishing(theme: dict, speed: float, speed_label: str) -> str:
    p = theme["primary"]
    a = theme["accent"]
    bg = theme["bg"]
    fish_speed = round(1.5 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Fishing Game</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">FISHING ({speed_label})</span>
    <span id="score" style="color:{p}">CAUGHT: 0</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800"></canvas>
  <button id="castBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">CAST LINE</button>
  <p class="text-slate-500 text-[10px] mt-2">Cast then click REEL IN when a fish bites!</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),castBtn=document.getElementById('castBtn');
const W=300,H=300,WATER_Y=100;
let fish=[],lineY=0,lineActive=false,reeling=false,hooked=null,caught=0,gameInterval,frame=0;
const FISH_EMOJIS=['🐟','🐠','🐡','🦈','🐙'];
const FISH_PTS=[10,15,20,50,30];

function initFish(){{
  fish=[];
  for(let i=0;i<5;i++){{
    fish.push({{
      x:Math.random()*260+20,y:WATER_Y+40+Math.random()*130,
      vx:({fish_speed}*(Math.random()+0.5))*(Math.random()<0.5?1:-1),
      emoji:FISH_EMOJIS[i],pts:FISH_PTS[i],size:i===3?28:18,hooked:false
    }});
  }}
}}

function draw(){{
  frame++;
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Sky
  ctx.fillStyle='#0f2b4a';ctx.fillRect(0,0,W,WATER_Y);
  // Water
  const grad=ctx.createLinearGradient(0,WATER_Y,0,H);
  grad.addColorStop(0,'#0369a1');grad.addColorStop(1,'#082f49');
  ctx.fillStyle=grad;ctx.fillRect(0,WATER_Y,W,H-WATER_Y);
  // Water shimmer
  ctx.strokeStyle='rgba(125,211,252,0.2)';ctx.lineWidth=1;
  for(let i=0;i<5;i++){{
    const wx=((frame*1.5+i*60)%W);
    ctx.beginPath();ctx.moveTo(wx,WATER_Y+2);ctx.lineTo(wx+30,WATER_Y+2);ctx.stroke();
  }}
  // Dock / land
  ctx.fillStyle='#92400e';ctx.fillRect(0,70,60,WATER_Y-70);
  ctx.fillStyle='#78350f';ctx.fillRect(0,66,70,8);
  // Rod
  ctx.strokeStyle='#d97706';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(15,60);ctx.lineTo(70,75);ctx.stroke();
  // Line
  if(lineActive||reeling){{
    ctx.strokeStyle='rgba(255,255,255,0.6)';ctx.lineWidth=1;ctx.setLineDash([3,3]);
    ctx.beginPath();ctx.moveTo(70,75);ctx.lineTo(70,lineY);ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle='{a}';ctx.beginPath();ctx.arc(70,lineY,4,0,Math.PI*2);ctx.fill();
  }}
  // Fish
  fish.forEach(f=>{{
    if(!f.hooked){{
      ctx.font=f.size+'px serif';ctx.textAlign='center';
      ctx.fillText(f.emoji,f.x,f.y);
    }}
  }});
  // Hooked fish rising
  if(reeling&&hooked){{
    ctx.font=hooked.size+'px serif';ctx.textAlign='center';
    ctx.fillText(hooked.emoji,70,lineY);
  }}
  // Fisherman
  ctx.font='24px serif';ctx.fillText('🧑',4,68);
  ctx.textAlign='left';
}}

function update(){{
  fish.forEach(f=>{{
    if(f.hooked)return;
    f.x+=f.vx;
    if(f.x<10||f.x>W-10)f.vx=-f.vx;
    // Nibble detection
    if(lineActive&&!hooked&&Math.abs(f.x-70)<f.size&&Math.abs(f.y-lineY)<f.size){{
      hooked=f;f.hooked=true;
      castBtn.innerText='🎣 REEL IN!';castBtn.style.background='{a}';
    }}
  }});
  if(reeling){{
    lineY-=4;
    if(lineY<75){{
      if(hooked){{caught++;scoreEl.innerText='CAUGHT: '+caught;hooked=null;}}
      lineActive=false;reeling=false;
      castBtn.innerText='CAST LINE';castBtn.style.background='{p}';
      initFish();
    }}
  }}
  draw();
}}

castBtn.onclick=()=>{{
  if(!lineActive&&!reeling){{
    lineY=WATER_Y+10;lineActive=true;hooked=null;
    castBtn.innerText='⏳ Waiting...';castBtn.style.background='#475569';
    // Auto-descend line
    const drop=setInterval(()=>{{
      if(lineY<H-20&&lineActive)lineY+=3;else clearInterval(drop);
    }},20);
  }} else if(hooked){{
    lineActive=false;reeling=true;
  }} else {{
    lineActive=false;reeling=true; // reel empty
    castBtn.innerText='CAST LINE';castBtn.style.background='{p}';
  }}
}};

initFish();
gameInterval=setInterval(update,16);
</script></body></html>"""


def _build_doodle(theme: dict, speed: float, speed_label: str) -> str:
    p = theme["primary"]
    a = theme["accent"]
    s = theme["secondary"]
    bg = theme["bg"]
    move_spd = round(3 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Doodle Jump</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">DOODLE JUMP ({speed_label})</span>
    <span id="score" style="color:{p}">HEIGHT: 0</span>
  </div>
  <canvas id="c" width="280" height="380" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">START</button>
  <p class="text-slate-500 text-[10px] mt-2">← → to move · Auto-jump on platforms</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=280,H=380;
let player,platforms,cameraY,height,keys={{}},gameInterval,running;

function genPlatforms(startY,count){{
  const plats=[];
  let y=startY;
  for(let i=0;i<count;i++){{
    plats.push({{x:Math.random()*(W-70),y,w:70,h=10}});
    y-=55+Math.random()*30;
  }}
  return plats;
}}

function init(){{
  player={{x:W/2-12,y:H-80,w:24,h:24,vy:0}};
  cameraY=0;height=0;
  platforms=[{{x:W/2-35,y:H-40,w:70,h:10}},...genPlatforms(H-120,20)];
  player.vy=-10;
}}

function update(){{
  if(!running)return;
  if(keys['ArrowLeft'])player.x-={move_spd};
  if(keys['ArrowRight'])player.x+={move_spd};
  player.x=(player.x+W)%W;
  player.vy+=0.3;player.y+=player.vy;

  // Platform collisions (only when falling)
  if(player.vy>0){{
    platforms.forEach(p=>{{
      if(player.x+player.w>p.x&&player.x<p.x+p.w&&
         player.y+player.h>=p.y&&player.y+player.h<=p.y+15){{
        player.vy=-11;player.y=p.y-player.h;
      }}
    }});
  }}

  // Camera scrolls up when player is in top half
  if(player.y-cameraY<H/2){{
    const shift=H/2-(player.y-cameraY);
    cameraY-=shift;height+=shift;
    scoreEl.innerText='HEIGHT: '+Math.floor(height/10);
    // Generate new platforms above
    const topY=cameraY;
    if(!platforms.some(p=>p.y<topY+50)){{
      platforms.push(...genPlatforms(topY,5));
    }}
    // Remove platforms below screen
    platforms=platforms.filter(p=>p.y<cameraY+H+100);
  }}

  // Fall death
  if(player.y-cameraY>H+50){{
    running=false;clearInterval(gameInterval);
    ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
    ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
    ctx.fillText('FELL DOWN!',W/2,H/2-10);
    ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
    ctx.fillText('Height: '+Math.floor(height/10),W/2,H/2+12);ctx.textAlign='left';
    return;
  }}

  draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Stars
  ctx.fillStyle='rgba(255,255,255,0.2)';
  for(let i=0;i<30;i++)ctx.fillRect((i*79+Math.floor(cameraY/10))%W,(i*53)%H,1,1);
  // Platforms
  platforms.forEach(p=>{{
    const sy=p.y-cameraY;
    if(sy>-20&&sy<H+20){{
      ctx.fillStyle='{s}';
      ctx.beginPath();ctx.roundRect(p.x,sy,p.w,p.h,4);ctx.fill();
    }}
  }});
  // Player
  const py=player.y-cameraY;
  ctx.fillStyle='{p}';ctx.beginPath();ctx.roundRect(player.x,py,player.w,player.h,5);ctx.fill();
  ctx.fillStyle='#fff';ctx.font='16px serif';ctx.textAlign='center';
  ctx.fillText('😊',player.x+player.w/2,py+player.h);
  ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  init();running=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;if(['ArrowLeft','ArrowRight'].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""


def _build_tower_defense(theme: dict, speed: float, speed_label: str) -> str:
    p = theme["primary"]
    a = theme["accent"]
    s = theme["secondary"]
    bg = theme["bg"]
    enemy_spd = round(0.8 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Tower Defense</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}canvas{{cursor:crosshair}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">TOWER DEF ({speed_label})</span>
    <span id="hud" style="color:{p}">WAVE 1 | LIVES 10 | 💰50</span>
  </div>
  <canvas id="c" width="300" height="280" class="rounded-xl border border-slate-800" style="background:#0f172a"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">START WAVE</button>
  <p class="text-slate-500 text-[10px] mt-2">Click on grass to place a tower (costs 25 gold)</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const hudEl=document.getElementById('hud'),startBtn=document.getElementById('startBtn');
const W=300,H=280;
// Path: enemies walk along this x-waypoints at fixed y rows
const PATH=[{{x:0,y:40}},{{x:260,y:40}},{{x:260,y:120}},{{x:40,y:120}},{{x:40,y:200}},{{x:300,y:200}}];
let towers=[],enemies=[],bullets=[];
let wave=1,lives=10,gold=50,gameInterval,running=false;

function ptOnPath(t){{
  let total=0;const segs=[];
  for(let i=1;i<PATH.length;i++){{
    const dx=PATH[i].x-PATH[i-1].x,dy=PATH[i].y-PATH[i-1].y;
    const d=Math.hypot(dx,dy);segs.push({{dx,dy,d,x0:PATH[i-1].x,y0:PATH[i-1].y}});total+=d;
  }}
  let dist=t*total;
  for(const seg of segs){{
    if(dist<=seg.d){{const f=dist/seg.d;return{{x:seg.x0+seg.dx*f,y:seg.y0+seg.dy*f}};}}
    dist-=seg.d;
  }}
  return PATH[PATH.length-1];
}}

function spawnWave(){{
  const n=3+wave*2;
  for(let i=0;i<n;i++){{
    setTimeout(()=>{{
      enemies.push({{t:-i*0.04,hp:2+wave,maxHp:2+wave,speed:{enemy_spd}*0.003,x:0,y:40,done:false}});
    }},i*600);
  }}
}}

function isOnPath(x,y){{
  for(let i=1;i<PATH.length;i++){{
    const ax=PATH[i-1].x,ay=PATH[i-1].y,bx=PATH[i].x,by=PATH[i].y;
    const dx=bx-ax,dy=by-ay,d2=dx*dx+dy*dy;
    const t=Math.max(0,Math.min(1,((x-ax)*dx+(y-ay)*dy)/d2));
    if(Math.hypot(x-ax-t*dx,y-ay-t*dy)<22)return true;
  }}
  return false;
}}

c.onclick=e=>{{
  if(!running)return;
  const rect=c.getBoundingClientRect(),mx=e.clientX-rect.left,my=e.clientY-rect.top;
  if(gold<25||isOnPath(mx,my)||towers.length>=8)return;
  towers.push({{x:mx,y:my,range:70,cooldown:0,color:'{p}'}});
  gold-=25;
}};

function update(){{
  enemies.forEach(en=>{{
    en.t+=en.speed;
    if(en.t>=1){{lives--;en.done=true;return;}}
    const pos=ptOnPath(en.t);en.x=pos.x;en.y=pos.y;
  }});
  enemies=enemies.filter(en=>!en.done&&en.hp>0);
  if(lives<=0){{gameOver();return;}}

  towers.forEach(t=>{{
    t.cooldown=Math.max(0,t.cooldown-1);
    if(t.cooldown>0)return;
    const target=enemies.find(en=>Math.hypot(en.x-t.x,en.y-t.y)<t.range);
    if(target){{
      bullets.push({{x:t.x,y:t.y,tx:target,speed:4}});t.cooldown=40;
    }}
  }});

  bullets.forEach(b=>{{
    if(!b.tx||b.tx.hp<=0){{b.done=true;return;}}
    const dx=b.tx.x-b.x,dy=b.tx.y-b.y,d=Math.hypot(dx,dy);
    if(d<6){{b.tx.hp--;b.done=true;if(b.tx.hp<=0)gold+=10;}}
    else{{b.x+=dx/d*b.speed;b.y+=dy/d*b.speed;}}
  }});
  bullets=bullets.filter(b=>!b.done);

  if(enemies.length===0){{wave++;gold+=30;spawnWave();}}

  hudEl.innerText='WAVE '+wave+' | LIVES '+lives+' | 💰'+gold;
  draw();
}}

function draw(){{
  ctx.fillStyle='#0f172a';ctx.fillRect(0,0,W,H);
  // Path
  ctx.strokeStyle='#334155';ctx.lineWidth=28;ctx.lineJoin='round';ctx.lineCap='round';
  ctx.beginPath();ctx.moveTo(PATH[0].x,PATH[0].y);
  PATH.slice(1).forEach(p=>ctx.lineTo(p.x,p.y));ctx.stroke();
  ctx.strokeStyle='#1e293b';ctx.lineWidth=24;ctx.stroke();

  // Tower ranges (faint)
  towers.forEach(t=>{{
    ctx.fillStyle='rgba(99,102,241,0.06)';
    ctx.beginPath();ctx.arc(t.x,t.y,t.range,0,Math.PI*2);ctx.fill();
  }});

  // Towers
  towers.forEach(t=>{{
    ctx.fillStyle='{s}';ctx.beginPath();ctx.arc(t.x,t.y,10,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='{p}';ctx.beginPath();ctx.arc(t.x,t.y,5,0,Math.PI*2);ctx.fill();
  }});

  // Enemies
  enemies.forEach(en=>{{
    ctx.fillStyle='#166534';ctx.beginPath();ctx.arc(en.x,en.y,9,0,Math.PI*2);ctx.fill();
    // HP bar
    const bw=20,bh=4,bx=en.x-bw/2,by=en.y-16;
    ctx.fillStyle='#334155';ctx.fillRect(bx,by,bw,bh);
    ctx.fillStyle='#22c55e';ctx.fillRect(bx,by,bw*(en.hp/en.maxHp),bh);
    ctx.fillStyle='#86efac';ctx.font='bold 9px monospace';ctx.textAlign='center';
    ctx.fillText('Z',en.x,en.y+4);
  }});

  // Bullets
  ctx.fillStyle='{a}';
  bullets.forEach(b=>{{ctx.beginPath();ctx.arc(b.x,b.y,3,0,Math.PI*2);ctx.fill();}});
  ctx.textAlign='left';
}}

function gameOver(){{
  running=false;clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
  ctx.fillText('BASE DESTROYED',W/2,H/2);ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  towers=[];enemies=[];bullets=[];wave=1;lives=10;gold=50;running=true;
  spawnWave();
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
</script></body></html>"""


def _build_chess(theme: dict) -> str:
    p = theme["primary"]
    bg = theme["bg"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Chess</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{background:{bg};margin:0}}
.sq{{width:36px;height:36px;display:flex;align-items:center;justify-content:center;
     font-size:22px;cursor:pointer;user-select:none;transition:background 0.1s}}
.sq.light{{background:#f1f5f9}}.sq.dark{{background:#475569}}
.sq.selected{{background:{p}!important}}.sq.legal{{background:#fbbf24!important;opacity:0.7}}
</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs space-y-3">
  <div class="flex justify-between w-full text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">CHESS</span>
    <span id="turn" style="color:{p}">White's turn</span>
  </div>
  <div id="board" class="border-2 border-slate-600 rounded-lg overflow-hidden"></div>
  <button id="resetBtn" class="w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">RESET BOARD</button>
</div>
<script>
const W_PIECES=['♜','♞','♝','♛','♚','♝','♞','♜'];
const INIT=[
  ['♜','♞','♝','♛','♚','♝','♞','♜'],
  ['♟','♟','♟','♟','♟','♟','♟','♟'],
  Array(8).fill(''),Array(8).fill(''),Array(8).fill(''),Array(8).fill(''),
  ['♙','♙','♙','♙','♙','♙','♙','♙'],
  ['♖','♘','♗','♕','♔','♗','♘','♖']
];
const BLACK=new Set(['♜','♞','♝','♛','♚','♟']);
const WHITE=new Set(['♖','♘','♗','♕','♔','♙']);
let board,selected,turn,boardEl;

function isBlack(p){{return BLACK.has(p);}}
function isWhite(p){{return WHITE.has(p);}}
function isOwn(p){{return turn==='white'?isWhite(p):isBlack(p);}}
function isEnemy(p){{return turn==='white'?isBlack(p):isWhite(p);}}

function legalMoves(r,c){{
  const p=board[r][c],moves=[];
  const add=(nr,nc)=>{{
    if(nr<0||nr>7||nc<0||nc>7)return false;
    if(isOwn(board[nr][nc]))return false;
    moves.push([nr,nc]);
    return!isEnemy(board[nr][nc]); // can keep going if empty
  }};
  const ray=(dr,dc)=>{{for(let i=1;i<8;i++)if(!add(r+dr*i,c+dc*i))break;}};

  if(p==='♙'){{// white pawn
    if(!board[r-1][c]){{add(r-1,c);if(r===6&&!board[r-2][c])add(r-2,c);}}
    if(c>0&&isBlack(board[r-1][c-1]))add(r-1,c-1);
    if(c<7&&isBlack(board[r-1][c+1]))add(r-1,c+1);
  }}else if(p==='♟'){{// black pawn
    if(!board[r+1][c]){{add(r+1,c);if(r===1&&!board[r+2][c])add(r+2,c);}}
    if(c>0&&isWhite(board[r+1][c-1]))add(r+1,c-1);
    if(c<7&&isWhite(board[r+1][c+1]))add(r+1,c+1);
  }}else if(p==='♖'||p==='♜'){{ray(1,0);ray(-1,0);ray(0,1);ray(0,-1);}}
  else if(p==='♗'||p==='♝'){{ray(1,1);ray(1,-1);ray(-1,1);ray(-1,-1);}}
  else if(p==='♕'||p==='♛'){{ray(1,0);ray(-1,0);ray(0,1);ray(0,-1);ray(1,1);ray(1,-1);ray(-1,1);ray(-1,-1);}}
  else if(p==='♔'||p==='♚'){{[-1,0,1].forEach(dr=>[-1,0,1].forEach(dc=>{{if(dr||dc)add(r+dr,c+dc);}}));}}
  else if(p==='♘'||p==='♞'){{
    [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]].forEach(([dr,dc])=>add(r+dr,c+dc));
  }}
  return moves;
}}

function render(sel,legals){{
  boardEl.innerHTML='';
  board.forEach((row,r)=>{{
    row.forEach((piece,c)=>{{
      const sq=document.createElement('div');
      sq.className='sq '+((r+c)%2===0?'light':'dark');
      if(sel&&sel[0]===r&&sel[1]===c)sq.classList.add('selected');
      if(legals&&legals.some(([lr,lc])=>lr===r&&lc===c))sq.classList.add('legal');
      sq.innerText=piece;
      sq.style.color=isBlack(piece)?'#0f172a':isWhite(piece)?'#1e293b':'';
      sq.onclick=()=>handleClick(r,c);
      boardEl.appendChild(sq);
    }});
  }});
}}

function handleClick(r,c){{
  if(selected){{
    const moves=legalMoves(selected[0],selected[1]);
    const isLegal=moves.some(([mr,mc])=>mr===r&&mc===c);
    if(isLegal){{
      board[r][c]=board[selected[0]][selected[1]];
      board[selected[0]][selected[1]]='';
      // Pawn promotion
      if(board[r][c]==='♙'&&r===0)board[r][c]='♕';
      if(board[r][c]==='♟'&&r===7)board[r][c]='♛';
      turn=turn==='white'?'black':'white';
      document.getElementById('turn').innerText=(turn==='white'?'White':'Black')+"'s turn";
      selected=null;render();
    }}else if(isOwn(board[r][c])){{selected=[r,c];render([r,c],legalMoves(r,c));}}
    else{{selected=null;render();}}
  }}else if(isOwn(board[r][c])){{selected=[r,c];render([r,c],legalMoves(r,c));}}
}}

function reset(){{
  board=INIT.map(r=>[...r]);turn='white';selected=null;
  document.getElementById('turn').innerText="White's turn";
  render();
}}
boardEl=document.getElementById('board');
boardEl.style.display='grid';boardEl.style.gridTemplateColumns='repeat(8,36px)';
document.getElementById('resetBtn').onclick=reset;
reset();
</script></body></html>"""


# ══════════════════════════════════════════════════════════════
# DESCRIPTION-DRIVEN UNIVERSAL GENERATOR
# ══════════════════════════════════════════════════════════════

_PLAYER_NOUNS = [
    "dinosaur", "dino", "knight", "wizard", "ninja", "pirate", "robot",
    "spaceship", "rocket", "tank", "frog", "cat", "dog", "monkey", "bear",
    "dragon", "ghost", "witch", "hero", "warrior", "soldier", "alien",
    "ball", "cube", "star", "plane", "submarine", "penguin",
    "chicken", "duck", "cow", "pig", "horse", "unicorn", "fox", "wolf",
    "bunny", "rabbit", "turtle", "hamster", "mouse", "rat",
]
_COLLECT_NOUNS = [
    "coin", "star", "gem", "crystal", "fruit", "apple", "banana",
    "cherry", "pizza", "cookie", "candy", "heart", "ring", "key",
    "treasure", "gold", "diamond", "orb", "token", "dot", "pellet",
    "mushroom", "berry", "flower", "egg", "fish",
]
_ENEMY_NOUNS = [
    "zombie", "monster", "enemy", "villain", "spike", "fire",
    "bomb", "bullet", "trap", "demon", "skeleton",
    "goblin", "orc", "troll", "vampire", "spider", "cactus",
    "rock", "block", "wall", "missile", "meteor", "barrel",
]


def _extract_entities(query: str) -> tuple:
    q = query.lower()
    player = next((n for n in _PLAYER_NOUNS if n in q), "hero")
    collectible = next((n for n in _COLLECT_NOUNS if n in q), "coin")
    enemy = next((n for n in _ENEMY_NOUNS if n in q), "enemy")

    if any(w in q for w in ("avoid", "dodge", "escape", "survive", "evade", "flee", "run")):
        mode = "avoider"
    elif any(w in q for w in ("shoot", "blast", "destroy", "kill", "attack", "fire", "zap")):
        mode = "shooter"
    elif any(w in q for w in ("jump", "hop", "leap", "bounce", "platform", "run and jump")):
        mode = "runner"
    else:
        mode = "collector"

    return player, collectible, enemy, mode


def _build_from_description(theme: dict, speed: float, speed_label: str, query: str) -> str:
    player, collectible, enemy, mode = _extract_entities(query)
    p = theme["primary"]
    a = theme["accent"]
    s = theme["secondary"]
    bg = theme["bg"]
    player_upper = player.upper()
    collect_upper = collectible.upper()
    enemy_upper = enemy.upper()
    move_spd = round(3 * speed * 100) / 100
    fall_spd = round(2.5 * speed * 100) / 100
    obs_spd = round(1.8 * speed * 100) / 100

    if mode == "collector":
        title = f"{player_upper} {collect_upper} COLLECTOR"
        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">{title}</span>
    <span id="score" style="color:{p}">SCORE: 0</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">START</button>
  <p class="text-slate-500 text-[10px] mt-2">Arrow keys / WASD to move and collect {collectible}s</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=300,H=300;
let player={{x:140,y:260,w:24,h:24,speed:{move_spd}}};
let items=[],obstacles=[],score=0,lives=3,keys={{}},gameInterval,frame=0;

function spawnItem(){{items.push({{x:Math.random()*(W-20)+10,y:-20,vy:{fall_spd},size:18}});}}
function spawnObs(){{obstacles.push({{x:Math.random()*(W-20)+10,y:-20,vy:{obs_spd},size:16}});}}

function update(){{
  frame++;
  if(keys['ArrowLeft']||keys['a'])player.x=Math.max(0,player.x-player.speed);
  if(keys['ArrowRight']||keys['d'])player.x=Math.min(W-player.w,player.x+player.speed);
  if(keys['ArrowUp']||keys['w'])player.y=Math.max(0,player.y-player.speed);
  if(keys['ArrowDown']||keys['s'])player.y=Math.min(H-player.h,player.y+player.speed);

  if(frame%60===0)spawnItem();
  if(frame%90===0)spawnObs();

  items.forEach(it=>it.y+=it.vy);
  obstacles.forEach(ob=>ob.y+=ob.vy);
  items=items.filter(it=>it.y<H+30);
  obstacles=obstacles.filter(ob=>ob.y<H+30);

  // Collect items
  items=items.filter(it=>{{
    if(Math.abs(it.x-player.x-12)<20&&Math.abs(it.y-player.y-12)<20){{score+=10;scoreEl.innerText='SCORE: '+score;return false;}}
    return true;
  }});
  // Hit obstacles
  obstacles=obstacles.filter(ob=>{{
    if(Math.abs(ob.x-player.x-12)<18&&Math.abs(ob.y-player.y-12)<18){{lives--;ob.y=H+100;if(lives<=0)gameOver();return false;}}
    return true;
  }});

  draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Grid
  ctx.strokeStyle='rgba(51,65,85,0.3)';ctx.lineWidth=0.5;
  for(let i=0;i<W;i+=30){{ctx.beginPath();ctx.moveTo(i,0);ctx.lineTo(i,H);ctx.stroke();}}
  for(let j=0;j<H;j+=30){{ctx.beginPath();ctx.moveTo(0,j);ctx.lineTo(W,j);ctx.stroke();}}
  // Items
  ctx.fillStyle='{p}';
  items.forEach(it=>{{ctx.beginPath();ctx.arc(it.x,it.y,it.size/2,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#020617';ctx.font='bold 10px monospace';ctx.textAlign='center';
    ctx.fillText('{collect_upper[0]}',it.x,it.y+4);ctx.fillStyle='{p}';
  }});
  // Obstacles
  ctx.fillStyle='{a}';
  obstacles.forEach(ob=>{{ctx.beginPath();ctx.arc(ob.x,ob.y,ob.size/2,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#020617';ctx.font='bold 9px monospace';ctx.textAlign='center';
    ctx.fillText('!',ob.x,ob.y+3);ctx.fillStyle='{a}';
  }});
  // Player
  ctx.fillStyle='{s}';ctx.beginPath();ctx.roundRect(player.x,player.y,player.w,player.h,6);ctx.fill();
  ctx.fillStyle='#e2e8f0';ctx.font='bold 8px monospace';ctx.textAlign='center';
  ctx.fillText('{player_upper[:4]}',player.x+12,player.y+14);
  // Lives
  ctx.fillStyle='{p}';ctx.font='bold 11px monospace';ctx.textAlign='left';
  ctx.fillText('♥'.repeat(lives),6,16);
}}

function gameOver(){{
  clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-10);
  ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
  ctx.fillText('Score: '+score,W/2,H/2+12);ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  player={{x:140,y:260,w:24,h:24,speed:{move_spd}}};
  items=[];obstacles=[];score=0;lives=3;frame=0;
  scoreEl.innerText='SCORE: 0';
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""

    elif mode == "avoider":
        title = f"{player_upper} DODGE {enemy_upper}"
        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">{title}</span>
    <span id="score" style="color:{p}">SCORE: 0</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">START</button>
  <p class="text-slate-500 text-[10px] mt-2">Arrow keys / WASD to dodge {enemy}s</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=300,H=300;
let player={{x:140,y:260,w:24,h:24,speed:{move_spd}}};
let obstacles=[],score=0,lives=3,keys={{}},gameInterval,frame=0,diff=1;

function spawnObs(){{
  obstacles.push({{
    x:Math.random()*(W-20)+10,y:-20,
    vy:({fall_spd}+diff*0.1)*(0.8+Math.random()*0.4),size:18
  }});
}}

function update(){{
  frame++;score++;diff=1+Math.floor(frame/300)*0.5;
  if(keys['ArrowLeft']||keys['a'])player.x=Math.max(0,player.x-player.speed);
  if(keys['ArrowRight']||keys['d'])player.x=Math.min(W-player.w,player.x+player.speed);
  if(keys['ArrowUp']||keys['w'])player.y=Math.max(0,player.y-player.speed);
  if(keys['ArrowDown']||keys['s'])player.y=Math.min(H-player.h,player.y+player.speed);

  if(frame%Math.max(20,50-Math.floor(frame/200))===0)spawnObs();
  obstacles.forEach(ob=>ob.y+=ob.vy);
  obstacles=obstacles.filter(ob=>ob.y<H+30);

  obstacles=obstacles.filter(ob=>{{
    if(Math.abs(ob.x-player.x-12)<20&&Math.abs(ob.y-player.y-12)<20){{
      lives--;ob.y=H+100;if(lives<=0)gameOver();return false;
    }}
    return true;
  }});

  scoreEl.innerText='SCORE: '+score;draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='rgba(51,65,85,0.3)';ctx.lineWidth=0.5;
  for(let i=0;i<W;i+=30){{ctx.beginPath();ctx.moveTo(i,0);ctx.lineTo(i,H);ctx.stroke();}}
  for(let j=0;j<H;j+=30){{ctx.beginPath();ctx.moveTo(0,j);ctx.lineTo(W,j);ctx.stroke();}}
  ctx.fillStyle='{a}';
  obstacles.forEach(ob=>{{ctx.beginPath();ctx.arc(ob.x,ob.y,ob.size/2,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#020617';ctx.font='bold 9px monospace';ctx.textAlign='center';
    ctx.fillText('{enemy_upper[0]}',ob.x,ob.y+3);ctx.fillStyle='{a}';
  }});
  ctx.fillStyle='{s}';ctx.beginPath();ctx.roundRect(player.x,player.y,player.w,player.h,6);ctx.fill();
  ctx.fillStyle='#e2e8f0';ctx.font='bold 7px monospace';ctx.textAlign='center';
  ctx.fillText('{player_upper[:4]}',player.x+12,player.y+14);
  ctx.fillStyle='{p}';ctx.font='bold 11px monospace';ctx.textAlign='left';
  ctx.fillText('♥'.repeat(lives),6,16);
}}

function gameOver(){{
  clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-10);
  ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
  ctx.fillText('Score: '+score,W/2,H/2+12);ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  player={{x:140,y:260,w:24,h:24,speed:{move_spd}}};
  obstacles=[];score=0;lives=3;frame=0;diff=1;
  scoreEl.innerText='SCORE: 0';
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""

    elif mode == "shooter":
        title = f"{player_upper} SHOOTER"
        bullet_spd = round(6 * speed * 100) / 100
        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">{title}</span>
    <span id="score" style="color:{p}">SCORE: 0</span>
  </div>
  <canvas id="c" width="300" height="300" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">START</button>
  <p class="text-slate-500 text-[10px] mt-2">← → move · Space to shoot {enemy}s</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=300,H=300;
let playerX=140,bullets=[],enemies=[],score=0,lives=3,keys={{}},gameInterval,frame=0,eDir=1;

function spawnEnemies(){{
  enemies=[];
  for(let r=0;r<3;r++)for(let col=0;col<5;col++)
    enemies.push({{x:col*50+25,y:r*35+30,w:30,h:22,hp:1}});
}}

function update(){{
  frame++;
  if(keys['ArrowLeft'])playerX=Math.max(0,playerX-4);
  if(keys['ArrowRight'])playerX=Math.min(270,playerX+4);

  bullets.forEach(b=>b.y-={bullet_spd});
  bullets=bullets.filter(b=>b.y>0);

  let edgeHit=false;
  enemies.forEach(en=>{{en.x+=eDir*{obs_spd};if(en.x>=270||en.x<=10)edgeHit=true;}});
  if(edgeHit){{eDir=-eDir;enemies.forEach(en=>en.y+=12);}}

  bullets.forEach(b=>{{
    enemies.forEach(en=>{{
      if(en.hp>0&&b.x>en.x&&b.x<en.x+en.w&&b.y<en.y+en.h&&b.y>en.y){{
        en.hp=0;b.y=-100;score+=10;scoreEl.innerText='SCORE: '+score;
      }}
    }});
  }});
  enemies=enemies.filter(en=>en.hp>0);

  enemies.forEach(en=>{{if(en.y>270){{lives--;en.y=-100;if(lives<=0)gameOver();}}}});
  if(!enemies.length)spawnEnemies();

  draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  ctx.strokeStyle='rgba(51,65,85,0.3)';ctx.lineWidth=0.5;
  for(let i=0;i<W;i+=30){{ctx.beginPath();ctx.moveTo(i,0);ctx.lineTo(i,H);ctx.stroke();}}
  // Enemies
  ctx.fillStyle='{a}';
  enemies.forEach(en=>{{ctx.fillRect(en.x,en.y,en.w,en.h);
    ctx.fillStyle='#020617';ctx.font='bold 8px monospace';ctx.textAlign='center';
    ctx.fillText('{enemy_upper[:3]}',en.x+en.w/2,en.y+en.h/2+3);ctx.fillStyle='{a}';
  }});
  // Bullets
  ctx.fillStyle='{p}';
  bullets.forEach(b=>ctx.fillRect(b.x,b.y,4,10));
  // Player
  ctx.fillStyle='{s}';ctx.fillRect(playerX,275,30,18);
  ctx.fillStyle='#e2e8f0';ctx.font='bold 8px monospace';ctx.textAlign='center';
  ctx.fillText('{player_upper[:4]}',playerX+15,275+12);
  // Lives
  ctx.fillStyle='{p}';ctx.font='bold 11px monospace';ctx.textAlign='left';
  ctx.fillText('♥'.repeat(lives),6,16);
}}

function gameOver(){{
  clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-10);
  ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
  ctx.fillText('Score: '+score,W/2,H/2+12);ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  playerX=140;bullets=[];score=0;lives=3;frame=0;eDir=1;
  scoreEl.innerText='SCORE: 0';spawnEnemies();
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{
  keys[e.key]=true;
  if(e.key===' '){{bullets.push({{x:playerX+13,y:270}});e.preventDefault();}}
  if(['ArrowLeft','ArrowRight'].includes(e.key))e.preventDefault();
}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""

    else:  # runner
        title = f"{player_upper} RUNNER"
        run_spd = round(3 * speed * 100) / 100
        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background:{bg};margin:0}}</style></head>
<body class="text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-5 shadow-2xl flex flex-col items-center w-full max-w-xs">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-slate-400 text-[10px] uppercase tracking-widest font-bold">{title}</span>
    <span id="score" style="color:{p}">SCORE: 0</span>
  </div>
  <canvas id="c" width="300" height="280" class="rounded-xl border border-slate-800" style="background:#020617"></canvas>
  <button id="startBtn" class="mt-3 w-full py-2 rounded-xl text-xs font-bold" style="background:{p}">RUN!</button>
  <p class="text-slate-500 text-[10px] mt-2">Space / Up arrow to jump over {enemy}s</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const W=300,H=280,GROUND=220;
let player={{x:50,y:GROUND-36,w:30,h:36,vy:0,onGround:true}};
let obstacles=[],score=0,lives=3,gameInterval,frame=0,keys={{}},speed={run_spd};

function spawnObs(){{
  const h=20+Math.floor(Math.random()*25);
  obstacles.push({{x:W+20,y:GROUND-h,w:20,h,color:'{a}'}});
}}

function update(){{
  frame++;score++;speed=Math.min(speed+0.001,6);
  if((keys[' ']||keys['ArrowUp'])&&player.onGround){{player.vy=-11;player.onGround=false;}}
  player.vy+=0.5;player.y+=player.vy;
  if(player.y>=GROUND-player.h){{player.y=GROUND-player.h;player.vy=0;player.onGround=true;}}

  if(frame%Math.max(40,90-Math.floor(frame/100))===0)spawnObs();
  obstacles.forEach(ob=>ob.x-=speed);
  obstacles=obstacles.filter(ob=>ob.x>-30);

  obstacles.forEach(ob=>{{
    if(player.x+player.w>ob.x&&player.x<ob.x+ob.w&&player.y+player.h>ob.y){{
      lives--;ob.x=-100;if(lives<=0)gameOver();
    }}
  }});

  scoreEl.innerText='SCORE: '+score;draw();
}}

function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,W,H);
  // Ground
  ctx.fillStyle='#1e293b';ctx.fillRect(0,GROUND,W,H-GROUND);
  ctx.fillStyle='#334155';ctx.fillRect(0,GROUND,W,3);
  // Background scenery
  ctx.fillStyle='rgba(99,102,241,0.15)';
  for(let i=0;i<5;i++){{const bx=(i*80-frame*0.3)%W;ctx.fillRect(bx,140,15,GROUND-140);}}
  // Obstacles
  obstacles.forEach(ob=>{{
    ctx.fillStyle=ob.color;ctx.fillRect(ob.x,ob.y,ob.w,ob.h);
    ctx.fillStyle='#020617';ctx.font='bold 8px monospace';ctx.textAlign='center';
    ctx.fillText('{enemy_upper[:3]}',ob.x+ob.w/2,ob.y+ob.h/2+3);
  }});
  // Player
  ctx.fillStyle='{s}';ctx.beginPath();ctx.roundRect(player.x,player.y,player.w,player.h,5);ctx.fill();
  ctx.fillStyle='#e2e8f0';ctx.font='bold 7px monospace';ctx.textAlign='center';
  ctx.fillText('{player_upper[:4]}',player.x+player.w/2,player.y+player.h/2+3);
  // Lives
  ctx.fillStyle='{p}';ctx.font='bold 11px monospace';ctx.textAlign='left';
  ctx.fillText('♥'.repeat(lives),6,16);
}}

function gameOver(){{
  clearInterval(gameInterval);
  ctx.fillStyle='rgba(2,6,23,0.9)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='{a}';ctx.font='bold 20px monospace';ctx.textAlign='center';
  ctx.fillText('GAME OVER',W/2,H/2-10);
  ctx.fillStyle='#94a3b8';ctx.font='13px monospace';
  ctx.fillText('Score: '+score,W/2,H/2+12);ctx.textAlign='left';
}}

startBtn.onclick=()=>{{
  player={{x:50,y:GROUND-36,w:30,h:36,vy:0,onGround:true}};
  obstacles=[];score=0;lives=3;frame=0;speed={run_spd};
  scoreEl.innerText='SCORE: 0';
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.addEventListener('keydown',e=>{{keys[e.key]=true;if([' ','ArrowUp','ArrowLeft','ArrowRight'].includes(e.key))e.preventDefault();}});
window.addEventListener('keyup',e=>delete keys[e.key]);
</script></body></html>"""


# ══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ══════════════════════════════════════════════════════════════

def compile_game(query: str) -> dict:
    q = query.lower()
    genre = _detect_genre(q)
    theme = _detect_theme(q)
    speed, speed_label = _detect_speed(q)

    genre_titles = {
        "snake": "Snake",
        "pong": "Pong",
        "tictactoe": "Tic-Tac-Toe",
        "flappy": "Flappy",
        "brickbreaker": "Brickbreaker",
        "clicker": "Clicker",
        "spaceshooter": "Space Shooter",
        "racing": "Racing",
        "platformer": "Platformer",
        "maze": "Maze",
        "memory": "Memory Match",
        "zombie": "Zombie Survival",
        "tower_defense": "Tower Defense",
        "whack": "Whack-a-Mole",
        "2048": "2048",
        "blackjack": "Blackjack",
        "asteroids": "Asteroids",
        "fishing": "Fishing",
        "chess": "Chess",
        "doodle": "Doodle Jump",
        "universal": "Custom Game",
    }
    title_label = genre_titles.get(genre, genre.title())
    title = f"{theme['name']} {title_label}"

    if genre == "racing":
        code = _build_racing(theme, speed, speed_label, q)
    elif genre == "platformer":
        code = _build_platformer(theme, speed, speed_label, q)
    elif genre == "maze":
        code = _build_maze(theme, speed, speed_label)
    elif genre == "memory":
        code = _build_memory(theme)
    elif genre == "zombie":
        code = _build_zombie(theme, speed, speed_label)
    elif genre == "snake":
        code = _build_snake(theme, speed, speed_label, q)
    elif genre == "pong":
        code = _build_pong(theme, speed, speed_label)
    elif genre == "tictactoe":
        code = GAME_TEMPLATES["tictactoe"]["code"]
    elif genre == "flappy":
        code = _build_flappy(theme, speed, speed_label)
    elif genre == "brickbreaker":
        code = _build_brickbreaker(theme, speed, speed_label)
    elif genre == "clicker":
        code = _build_clicker(theme)
    elif genre == "spaceshooter":
        code = _build_spaceshooter(theme, speed, speed_label)
    elif genre == "tower_defense":
        code = _build_tower_defense(theme, speed, speed_label)
    elif genre == "whack":
        code = _build_whack(theme)
    elif genre == "2048":
        code = _build_2048(theme)
    elif genre == "blackjack":
        code = _build_blackjack(theme)
    elif genre == "asteroids":
        code = _build_asteroids(theme, speed, speed_label)
    elif genre == "fishing":
        code = _build_fishing(theme, speed, speed_label)
    elif genre == "chess":
        code = _build_chess(theme)
    elif genre == "doodle":
        code = _build_doodle(theme, speed, speed_label)
    else:  # universal / fallback
        code = _build_from_description(theme, speed, speed_label, q)

    return {"title": title, "desc": f"Custom compiled {title_label} game.", "code": code}
