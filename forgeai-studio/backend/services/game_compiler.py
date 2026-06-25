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
        "lane", "speed racer", "dirt road",
    )):
        return "racing"

    if any(w in q for w in ("pong", "paddle", "hockey", "table tennis")):
        return "pong"

    if any(w in q for w in ("tic", "toe", "noughts", "xo", "x and o")):
        return "tictactoe"

    if any(w in q for w in ("flap", "bird", "wing", "copter")):
        return "flappy"

    if any(w in q for w in ("brick", "break", "shatter", "breaker", "arkanoid")):
        return "brickbreaker"

    if any(w in q for w in ("clicker", "cookie", "idle", "incremental")):
        return "clicker"

    if any(w in q for w in (
        "zombie", "undead", "horde", "survival", "wave", "apocalypse",
    )):
        return "zombie"

    if any(w in q for w in (
        "platform", "platformer", "jump", "mario", "side scroll",
        "run and jump", "jump game",
    )):
        return "platformer"

    if any(w in q for w in ("maze", "labyrinth", "dungeon", "corridor")):
        return "maze"

    if any(w in q for w in (
        "memory", "match card", "card flip", "card match", "concentration",
        "matching game", "pair",
    )):
        return "memory"

    if any(w in q for w in (
        "space", "shoot", "invader", "alien", "laser", "ship", "galaga",
        "asteroid", "meteor",
    )):
        return "spaceshooter"

    if any(w in q for w in ("snake", "worm", "slither")):
        return "snake"

    # Unknown — use description to generate a fitting game
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


def _build_universal(theme: dict, speed: float, speed_label: str, query: str) -> str:
    """
    Smart fallback: analyze the query to pick the closest fitting game type.
    Uses action verbs and nouns to decide, then generates a real game.
    """
    q = query.lower()

    # Action-verb / noun analysis
    if any(w in q for w in ("fight", "battle", "combat", "beat", "enemy", "warrior", "attack")):
        return _build_zombie(theme, speed, speed_label)

    if any(w in q for w in ("collect", "coin", "gem", "item", "pick up", "gather")):
        return _build_platformer(theme, speed, speed_label, query)

    if any(w in q for w in ("escape", "navigate", "path", "find", "explore", "dungeon")):
        return _build_maze(theme, speed, speed_label)

    if any(w in q for w in ("match", "flip", "pair", "reveal", "hidden")):
        return _build_memory(theme)

    if any(w in q for w in ("fly", "pilot", "aircraft", "plane", "hover", "float")):
        return _build_flappy(theme, speed, speed_label)

    if any(w in q for w in ("bounce", "ball", "break", "destroy", "shatter")):
        return _build_brickbreaker(theme, speed, speed_label)

    if any(w in q for w in ("click", "tap", "buy", "upgrade", "earn", "farm")):
        return _build_clicker(theme)

    # Default: platformer is the most versatile generic game
    return _build_platformer(theme, speed, speed_label, query)


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
    else:  # universal
        code = _build_universal(theme, speed, speed_label, q)

    return {"title": title, "desc": f"Custom compiled {title_label} game.", "code": code}
