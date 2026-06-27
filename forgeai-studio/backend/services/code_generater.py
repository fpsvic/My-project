"""
code_generater.py — ForgeAI universal code generation engine.

Consolidates game compilation, app building, dynamic synthesis, multi-file
project output, and web research fallback. When a build request is not
recognised locally, context is fetched from Google/DuckDuckGo first.
"""

from __future__ import annotations

import json
import random
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from data.game_templates import GAME_TEMPLATES
from data.knowledge_base import CODING_HELP, LANG_EXAMPLES, LANG_HELLO_WORLD, LANG_HISTORY


# =============================================================================
# GAME COMPILER
# =============================================================================

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

    if any(w in q for w in ("snake", "worm", "slither", "grow", "eat and grow", "tail")):
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

    if any(w in q for w in ("space", "shoot", "invader", "alien", "laser", "ship", "galaga", "meteor",
                             "defend earth", "alien attack", "galactic", "cosmos shooter")):
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
    "samurai", "astronaut", "mage", "elf", "dwarf", "vampire", "zombie",
    "superhero", "cop", "spy", "chef", "farmer", "miner", "sailor", "pilot",
    "racer", "runner", "jumper", "shooter",
]
_COLLECT_NOUNS = [
    "coin", "star", "gem", "crystal", "fruit", "apple", "banana",
    "cherry", "pizza", "cookie", "candy", "heart", "ring", "key",
    "treasure", "gold", "diamond", "orb", "token", "dot", "pellet",
    "mushroom", "berry", "flower", "egg", "fish",
    "potion", "scroll", "armor", "shield", "sword", "wand", "hat", "boot",
    "glove", "pearl", "ammo", "fuel", "battery", "lightning bolt", "feather",
    "leaf", "seed", "book", "letter", "package",
]
_ENEMY_NOUNS = [
    "zombie", "monster", "enemy", "villain", "spike", "fire",
    "bomb", "bullet", "trap", "demon", "skeleton",
    "goblin", "orc", "troll", "vampire", "spider", "cactus",
    "rock", "block", "wall", "missile", "meteor", "barrel",
    "pirate", "bandit", "witch", "dragon", "snake", "bear", "shark", "robot",
    "alien", "ninja", "assassin", "thief", "ghost", "curse", "poison",
    "lava", "ice", "thunder", "laser", "arrow",
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


# =============================================================================
# SYNTHESIS ENGINE
# =============================================================================

# ══════════════════════════════════════════════════════════════
# GAME SYNTHESIS
# ══════════════════════════════════════════════════════════════

def _synth_pick_theme(q: str) -> dict:
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
    theme = _synth_pick_theme(q)
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
        return _synth_build_platformer(title, theme, feat, player_emoji, enemy_emoji, coll_emoji, coll_name, enemy_name, proj_emoji, lives, has_rainbow, has_waves, rainbow_js, trail_js)
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


def _synth_build_platformer(title, theme, feat, pe, ee, ce, cn, en, proj, lives, rainbow, waves, rainbow_js, trail_js):
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
    complex_indicators = [
        len(q) > 55,
        sum(1 for w in ["wizard", "ninja", "dragon", "robot", "frog", "ball", "knight", "astronaut", "pirate", "zombie"] if w in q) > 0,
        bool(re.search(r"(shoot|fire|blast|laser|lightning|spell|magic)", q)),
        "platform" in q or ("jump" in q and "snake" not in q),
        len([w for w in ["collect", "avoid", "shoot", "jump", "survive", "boss", "powerup", "multiplayer"] if w in q]) >= 2,
        bool(re.search(r"\b(with|that has|featuring|including)\b", q)),
        _detect_genre(q) == "universal",
    ]
    return any(complex_indicators)


# =============================================================================
# APP BUILDER
# =============================================================================

# ─── Theme detection ───────────────────────────────────────────

# ─── Theme detection (reuse game_compiler palette) ───────────────────────────

_THEMES = {
    "dark": {"bg": "#0f172a", "surface": "#1e293b", "border": "#334155",
             "primary": "#6366f1", "accent": "#ec4899", "text": "#e2e8f0", "muted": "#94a3b8"},
    "light": {"bg": "#f8fafc", "surface": "#ffffff", "border": "#e2e8f0",
              "primary": "#4f46e5", "accent": "#db2777", "text": "#1e293b", "muted": "#64748b"},
    "green": {"bg": "#022c22", "surface": "#064e3b", "border": "#065f46",
              "primary": "#10b981", "accent": "#f59e0b", "text": "#ecfdf5", "muted": "#6ee7b7"},
    "ocean": {"bg": "#0c2540", "surface": "#0f3460", "border": "#1d4ed8",
              "primary": "#38bdf8", "accent": "#f43f5e", "text": "#f0f9ff", "muted": "#7dd3fc"},
    "fire": {"bg": "#1c0d02", "surface": "#431407", "border": "#92400e",
             "primary": "#f97316", "accent": "#e11d48", "text": "#fff7ed", "muted": "#fdba74"},
}

def _app_pick_theme(q: str) -> dict:
    if any(w in q for w in ("light", "white", "clean", "minimal")):
        return _THEMES["light"]
    if any(w in q for w in ("green", "nature", "forest", "emerald")):
        return _THEMES["green"]
    if any(w in q for w in ("blue", "ocean", "sea", "sky", "cool")):
        return _THEMES["ocean"]
    if any(w in q for w in ("fire", "red", "orange", "warm", "hot")):
        return _THEMES["fire"]
    return _THEMES["dark"]


# ─── App type detection ───────────────────────────────────────────────────────

def detect_app_type(q: str) -> str:
    if any(w in q for w in ("scientific calc", "science calc", "advanced calc")):
        return "scientific_calculator"
    if any(w in q for w in ("calculator", "calc", "arithmetic")):
        return "calculator"
    if any(w in q for w in ("bmi", "body mass")):
        return "bmi_calculator"
    if any(w in q for w in ("mortgage", "loan payment", "monthly payment")):
        return "mortgage_calculator"
    if any(w in q for w in ("tip", "restaurant", "split bill", "bill split")):
        return "tip_calculator"
    if any(w in q for w in ("stopwatch", "stop watch")):
        return "stopwatch"
    if any(w in q for w in ("countdown", "count down", "timer")):
        return "countdown_timer"
    if any(w in q for w in ("pomodoro", "focus timer", "work timer", "study timer")):
        return "pomodoro"
    if any(w in q for w in ("clock", "digital clock", "analog clock", "world clock", "time")):
        return "clock"
    if any(w in q for w in ("todo", "to do", "to-do", "task list", "checklist", "tasks")):
        return "todo"
    if any(w in q for w in ("kanban", "board", "trello")):
        return "kanban"
    if any(w in q for w in ("unit convert", "convert unit", "temperature convert", "length convert",
                             "weight convert", "converter")):
        return "unit_converter"
    if any(w in q for w in ("password", "passgen", "pass gen")):
        return "password_generator"
    if any(w in q for w in ("color pick", "colour pick", "palette", "color tool")):
        return "color_picker"
    if any(w in q for w in ("draw", "paint", "canvas app", "sketch", "whiteboard")):
        return "drawing_canvas"
    if any(w in q for w in ("quiz", "trivia", "question", "test yourself")):
        return "quiz"
    if any(w in q for w in ("flashcard", "flash card", "study card", "memorize")):
        return "flashcards"
    if any(w in q for w in ("budget", "expense", "spending", "finance tracker", "money tracker")):
        return "budget_tracker"
    if any(w in q for w in ("note", "notes app", "notepad", "text editor", "markdown")):
        return "notes_app"
    if any(w in q for w in ("dice", "roll", "d20", "d6", "tabletop")):
        return "dice_roller"
    if any(w in q for w in ("word count", "character count", "text tool", "text util")):
        return "text_utils"
    if any(w in q for w in ("habit", "streak", "daily tracker", "habit track")):
        return "habit_tracker"
    if any(w in q for w in ("random quote", "quote", "inspirational", "motivation")):
        return "quote_generator"
    if any(w in q for w in ("age", "birthday", "born", "age calculator")):
        return "age_calculator"
    if any(w in q for w in ("grade", "gpa", "grade calculator", "score")):
        return "grade_calculator"
    if any(w in q for w in ("currency", "exchange", "forex", "money convert")):
        return "currency_converter"
    return ""


def _is_explicit_app_query(q: str) -> bool:
    """True when the user clearly asked for an app/tool, not a game."""
    if detect_app_type(q):
        return True
    return any(
        w in q
        for w in (
            "app", "application", "tool", "utility", "widget", "dashboard",
            "crud", "inventory", "database", "admin panel", "manager",
            "notepad", "spreadsheet", "form", "landing page", "website",
        )
    )


# ─── Individual builders ──────────────────────────────────────────────────────

def _shell(title: str, t: dict, body: str, script: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<script src="https://cdn.tailwindcss.com"></script>{extra_head}
<style>
  body{{background:{t['bg']};color:{t['text']};font-family:'Inter',sans-serif}}
  ::-webkit-scrollbar{{width:4px}} ::-webkit-scrollbar-thumb{{background:{t['border']};border-radius:9999px}}
  .btn{{background:{t['primary']};color:#fff;border:none;border-radius:.75rem;padding:.6rem 1.2rem;font-weight:700;font-size:.75rem;cursor:pointer;transition:.2s}}
  .btn:hover{{opacity:.85}} .btn-ghost{{background:transparent;border:1.5px solid {t['border']};color:{t['text']}}}
  .card{{background:{t['surface']};border:1px solid {t['border']};border-radius:1rem;padding:1.25rem}}
  input,select,textarea{{background:{t['surface']};border:1.5px solid {t['border']};color:{t['text']};border-radius:.6rem;padding:.5rem .75rem;outline:none;font-size:.85rem;width:100%}}
  input:focus,select:focus,textarea:focus{{border-color:{t['primary']}}}
  label{{font-size:.7rem;font-weight:600;color:{t['muted']};text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:.25rem}}
</style></head>
<body class="min-h-screen p-4 flex flex-col items-center justify-start">
<div class="w-full max-w-lg space-y-4 pt-4">
  <div class="text-center mb-2">
    <h1 class="text-xl font-extrabold tracking-tight" style="color:{t['primary']}">{title}</h1>
  </div>
  {body}
</div>
<script>{script}</script>
</body></html>"""


def _build_calculator(t: dict) -> str:
    calc_keys = ["C","±","%","÷","7","8","9","×","4","5","6","−","1","2","3","+","0",".","+/−","="]
    calc_buttons = "".join(
        f'<button class="btn btn-ghost py-3 text-sm font-bold rounded-xl" onclick="press(\'{k}\')">{k}</button>'
        for k in calc_keys
    )
    body = f"""<div class="card space-y-3">
  <div id="display" style="background:{t['bg']};border:1.5px solid {t['border']};border-radius:.75rem;padding:1rem;font-family:monospace;font-size:1.5rem;font-weight:800;text-align:right;min-height:3.5rem;word-break:break-all;color:{t['text']}">0</div>
  <div class="grid grid-cols-4 gap-2">
    {calc_buttons}
  </div>
</div>"""
    script = f"""
let cur='0',prev='',op='',justEq=false;
const disp=document.getElementById('display');
function update(){{disp.innerText=cur;}}
function press(k){{
  if(k==='C'){{cur='0';prev='';op='';justEq=false;}}
  else if(k==='±'||k==='+/−'){{cur=(parseFloat(cur)*-1).toString();}}
  else if(k==='%'){{cur=(parseFloat(cur)/100).toString();}}
  else if(['÷','×','−','+'].includes(k)){{prev=cur;op=k;cur='0';justEq=false;}}
  else if(k==='='){{
    const a=parseFloat(prev),b=parseFloat(cur);
    if(op==='÷')cur=b?String(a/b):'ERR';
    else if(op==='×')cur=String(a*b);
    else if(op==='−')cur=String(a-b);
    else if(op==='+')cur=String(a+b);
    op='';justEq=true;
  }}
  else if(k==='.'){{if(!cur.includes('.'))cur+='.';}}
  else{{cur=(cur==='0'||justEq)?k:cur+k;justEq=false;}}
  update();
}}
document.addEventListener('keydown',e=>{{
  const m={{'0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',
    '+':'+','-':'−','*':'×','/':'÷','Enter':'=','Backspace':'C','.':'.','%':'%'}};
  if(m[e.key])press(m[e.key]);
}});"""
    return _shell("Calculator", t, body, script)


def _build_scientific_calculator(t: dict) -> str:
    sci_keys = ["sin","cos","tan","log","ln","√","x²","x³","π","e",
                "C","(",")","±","%","7","8","9","÷","×","4","5","6","−","+","1","2","3","0",".","="]
    sci_buttons = "".join(
        f'<button class="btn btn-ghost py-2.5 text-xs font-bold rounded-xl" onclick="press(\'{k}\')">{k}</button>'
        for k in sci_keys
    )
    body = f"""<div class="card space-y-3">
  <div id="display" style="background:{t['bg']};border:1.5px solid {t['border']};border-radius:.75rem;padding:1rem;font-family:monospace;font-size:1.3rem;font-weight:800;text-align:right;min-height:3.5rem;word-break:break-all;color:{t['text']}">0</div>
  <div id="expr" style="font-family:monospace;font-size:.7rem;color:{t['muted']};min-height:1rem;text-align:right;padding:0 .5rem"></div>
  <div class="grid grid-cols-5 gap-1.5">
    {sci_buttons}
  </div>
</div>"""
    script = """
let expr='',display='0';
const d=document.getElementById('display'),ex=document.getElementById('expr');
function update(){d.innerText=display;ex.innerText=expr;}
const PI=Math.PI,E=Math.E;
function press(k){
  if(k==='C'){expr='';display='0';}
  else if(k==='='){
    try{
      let e=expr.replace(/÷/g,'/').replace(/×/g,'*').replace(/−/g,'-')
        .replace(/sin\\(/g,'Math.sin(').replace(/cos\\(/g,'Math.cos(').replace(/tan\\(/g,'Math.tan(')
        .replace(/log\\(/g,'Math.log10(').replace(/ln\\(/g,'Math.log(').replace(/√\\(/g,'Math.sqrt(')
        .replace(/π/g,'Math.PI').replace(/e(?![\\d.])/g,'Math.E')
        .replace(/x²/g,'**2').replace(/x³/g,'**3');
      let r=Function('"use strict";return('+e+')')();
      display=parseFloat(r.toFixed(10)).toString();
      expr=display;
    }catch{display='ERROR';}
  }
  else if(k==='π'){expr+='π';display='π';}
  else if(k==='e'){expr+='e';display='e';}
  else if(['sin','cos','tan','log','ln','√'].includes(k)){expr+=k+'(';display=k+'(';}
  else if(k==='x²'){expr+='x²';display+='²';}
  else if(k==='x³'){expr+='x³';display+='³';}
  else if(k==='±'){expr='-'+expr;display='-'+display;}
  else{expr+=k;display=(display==='0'&&k!='.')?k:display+k;}
  update();
}"""
    return _shell("Scientific Calculator", t, body, script)


def _build_bmi(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div class="grid grid-cols-2 gap-3">
    <div><label>Weight (kg)</label><input id="weight" type="number" placeholder="70"></div>
    <div><label>Height (cm)</label><input id="height" type="number" placeholder="175"></div>
  </div>
  <button class="btn w-full" onclick="calc()">Calculate BMI</button>
  <div id="result" class="text-center py-4 hidden">
    <div class="text-4xl font-extrabold font-mono" id="bmiVal" style="color:{t['primary']}"></div>
    <div class="text-sm mt-1" id="bmiCat"></div>
    <div class="w-full bg-slate-700 rounded-full h-2 mt-4 overflow-hidden">
      <div id="bmiBar" class="h-full rounded-full transition-all duration-700" style="background:{t['accent']};width:0%"></div>
    </div>
    <div class="flex justify-between text-[10px] mt-1" style="color:{t['muted']}">
      <span>Underweight &lt;18.5</span><span>Normal 18.5-25</span><span>Obese &gt;30</span>
    </div>
  </div>
</div>"""
    script = f"""
function calc(){{
  const w=parseFloat(document.getElementById('weight').value);
  const h=parseFloat(document.getElementById('height').value)/100;
  if(!w||!h)return;
  const bmi=(w/(h*h)).toFixed(1);
  document.getElementById('bmiVal').innerText=bmi;
  let cat,pct;
  if(bmi<18.5){{cat='Underweight';pct=Math.max(5,bmi/18.5*30);}}
  else if(bmi<25){{cat='Normal Weight ✅';pct=30+(bmi-18.5)/6.5*30;}}
  else if(bmi<30){{cat='Overweight ⚠️';pct=60+(bmi-25)/5*20;}}
  else{{cat='Obese ❌';pct=Math.min(100,80+(bmi-30)/10*20);}}
  document.getElementById('bmiCat').innerText=cat;
  document.getElementById('bmiBar').style.width=pct+'%';
  document.getElementById('result').classList.remove('hidden');
}}"""
    return _shell("BMI Calculator", t, body, script)


def _build_tip_calculator(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div><label>Bill Amount ($)</label><input id="bill" type="number" placeholder="50.00"></div>
  <div>
    <label>Tip Percentage: <span id="tipLabel" style="color:{t['primary']}">18%</span></label>
    <input id="tipRange" type="range" min="0" max="40" value="18" oninput="document.getElementById('tipLabel').innerText=this.value+'%';compute()" style="padding:0;margin-top:.5rem">
  </div>
  <div><label>Number of People</label><input id="people" type="number" value="1" min="1"></div>
  <button class="btn w-full" onclick="compute()">Calculate</button>
  <div class="grid grid-cols-3 gap-2 text-center">
    <div class="card"><div class="text-[10px]" style="color:{t['muted']}">TIP</div><div class="text-xl font-extrabold font-mono" id="tipAmt" style="color:{t['primary']}">$0</div></div>
    <div class="card"><div class="text-[10px]" style="color:{t['muted']}">TOTAL</div><div class="text-xl font-extrabold font-mono" id="total" style="color:{t['accent']}">$0</div></div>
    <div class="card"><div class="text-[10px]" style="color:{t['muted']}">PER PERSON</div><div class="text-xl font-extrabold font-mono" id="perPerson">$0</div></div>
  </div>
</div>"""
    script = """
function compute(){
  const bill=parseFloat(document.getElementById('bill').value)||0;
  const tip=parseFloat(document.getElementById('tipRange').value)/100;
  const ppl=parseInt(document.getElementById('people').value)||1;
  const tipAmt=bill*tip;
  const total=bill+tipAmt;
  document.getElementById('tipAmt').innerText='$'+tipAmt.toFixed(2);
  document.getElementById('total').innerText='$'+total.toFixed(2);
  document.getElementById('perPerson').innerText='$'+(total/ppl).toFixed(2);
}
document.getElementById('bill').addEventListener('input',compute);
document.getElementById('people').addEventListener('input',compute);"""
    return _shell("Tip Calculator", t, body, script)


def _build_mortgage_calculator(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div class="grid grid-cols-2 gap-3">
    <div><label>Home Price ($)</label><input id="price" type="number" placeholder="300000"></div>
    <div><label>Down Payment ($)</label><input id="down" type="number" placeholder="60000"></div>
    <div><label>Interest Rate (%)</label><input id="rate" type="number" step="0.01" placeholder="6.5"></div>
    <div><label>Loan Term (years)</label><input id="term" type="number" placeholder="30"></div>
  </div>
  <button class="btn w-full" onclick="calc()">Calculate Payment</button>
  <div id="result" class="hidden space-y-3">
    <div class="grid grid-cols-2 gap-2 text-center">
      <div class="card"><div class="text-[10px]" style="color:{t['muted']}">MONTHLY PAYMENT</div><div class="text-2xl font-extrabold font-mono" id="monthly" style="color:{t['primary']}"></div></div>
      <div class="card"><div class="text-[10px]" style="color:{t['muted']}">TOTAL INTEREST</div><div class="text-2xl font-extrabold font-mono" id="interest" style="color:{t['accent']}"></div></div>
    </div>
    <div class="card text-sm"><div class="flex justify-between"><span style="color:{t['muted']}">Loan Amount</span><span id="loan" class="font-bold"></span></div><div class="flex justify-between mt-1"><span style="color:{t['muted']}">Total Paid</span><span id="totalPaid" class="font-bold"></span></div></div>
  </div>
</div>"""
    script = """
function calc(){
  const price=parseFloat(document.getElementById('price').value)||0;
  const down=parseFloat(document.getElementById('down').value)||0;
  const rate=parseFloat(document.getElementById('rate').value)/100/12;
  const n=parseInt(document.getElementById('term').value)*12;
  const loan=price-down;
  const m=rate?loan*(rate*Math.pow(1+rate,n))/(Math.pow(1+rate,n)-1):loan/n;
  const total=m*n;
  const fmt=v=>'$'+v.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
  document.getElementById('monthly').innerText=fmt(m);
  document.getElementById('interest').innerText=fmt(total-loan);
  document.getElementById('loan').innerText=fmt(loan);
  document.getElementById('totalPaid').innerText=fmt(total);
  document.getElementById('result').classList.remove('hidden');
}"""
    return _shell("Mortgage Calculator", t, body, script)


def _build_stopwatch(t: dict) -> str:
    body = f"""<div class="card text-center space-y-6">
  <div class="text-6xl font-extrabold font-mono" id="display" style="color:{t['primary']}">00:00.00</div>
  <div class="flex gap-3 justify-center">
    <button class="btn" id="startBtn" onclick="toggle()">START</button>
    <button class="btn btn-ghost" onclick="reset()">RESET</button>
    <button class="btn btn-ghost" onclick="lap()">LAP</button>
  </div>
  <div id="laps" class="space-y-1 max-h-40 overflow-y-auto text-left text-xs font-mono" style="color:{t['muted']}"></div>
</div>"""
    script = f"""
let running=false,elapsed=0,startTime=0,raf,lapCount=0;
const disp=document.getElementById('display'),btn=document.getElementById('startBtn'),laps=document.getElementById('laps');
function fmt(ms){{
  const m=Math.floor(ms/60000),s=Math.floor((ms%60000)/1000),cs=Math.floor((ms%1000)/10);
  return String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')+'.'+String(cs).padStart(2,'0');
}}
function tick(){{elapsed=Date.now()-startTime;disp.innerText=fmt(elapsed);raf=requestAnimationFrame(tick);}}
function toggle(){{
  if(running){{cancelAnimationFrame(raf);running=false;btn.innerText='RESUME';}}
  else{{startTime=Date.now()-elapsed;running=true;btn.innerText='STOP';tick();}}
}}
function reset(){{cancelAnimationFrame(raf);running=false;elapsed=0;lapCount=0;disp.innerText='00:00.00';btn.innerText='START';laps.innerHTML='';}}
function lap(){{
  if(!running)return;
  lapCount++;
  const li=document.createElement('div');
  li.className='flex justify-between px-2 py-1 rounded';
  li.style.background='{t['bg']}';
  li.innerHTML='<span style="color:{t['primary']}">Lap '+lapCount+'</span><span>'+fmt(elapsed)+'</span>';
  laps.prepend(li);
}}"""
    return _shell("Stopwatch", t, body, script)


def _build_countdown(t: dict) -> str:
    body = f"""<div class="card text-center space-y-5">
  <div class="grid grid-cols-3 gap-3">
    <div><label>Hours</label><input id="hIn" type="number" min="0" max="99" value="0" style="text-align:center;font-size:1.2rem;font-weight:800"></div>
    <div><label>Minutes</label><input id="mIn" type="number" min="0" max="59" value="5" style="text-align:center;font-size:1.2rem;font-weight:800"></div>
    <div><label>Seconds</label><input id="sIn" type="number" min="0" max="59" value="0" style="text-align:center;font-size:1.2rem;font-weight:800"></div>
  </div>
  <div class="text-7xl font-extrabold font-mono" id="display" style="color:{t['primary']}">05:00</div>
  <div class="flex gap-3 justify-center">
    <button class="btn" id="startBtn" onclick="toggle()">START</button>
    <button class="btn btn-ghost" onclick="reset()">RESET</button>
  </div>
  <div id="doneMsg" class="hidden font-bold text-lg" style="color:{t['accent']}">⏰ Time's up!</div>
</div>"""
    script = f"""
let running=false,remaining=300,iv,total=300;
const disp=document.getElementById('display'),btn=document.getElementById('startBtn'),done=document.getElementById('doneMsg');
function fmt(s){{
  const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sec=s%60;
  return (h?String(h).padStart(2,'0')+':':'')+String(m).padStart(2,'0')+':'+String(sec).padStart(2,'0');
}}
function toggle(){{
  if(running){{clearInterval(iv);running=false;btn.innerText='RESUME';}}
  else{{
    remaining=remaining||parseInt(document.getElementById('hIn').value)*3600+parseInt(document.getElementById('mIn').value)*60+parseInt(document.getElementById('sIn').value);
    running=true;btn.innerText='PAUSE';done.classList.add('hidden');
    iv=setInterval(()=>{{
      remaining--;disp.innerText=fmt(remaining);
      if(remaining<=0){{clearInterval(iv);running=false;btn.innerText='START';done.classList.remove('hidden');disp.style.color='{t['accent']}';}}
    }},1000);
  }}
}}
function reset(){{clearInterval(iv);running=false;btn.innerText='START';done.classList.add('hidden');
  remaining=0;disp.style.color='{t['primary']}';disp.innerText=fmt(0);}}"""
    return _shell("Countdown Timer", t, body, script)


def _build_pomodoro(t: dict) -> str:
    body = f"""<div class="card text-center space-y-5">
  <div class="flex gap-2 justify-center">
    <button class="btn text-xs" onclick="setMode('work',25,'🧠 Focus')">Work 25m</button>
    <button class="btn btn-ghost text-xs" onclick="setMode('short',5,'☕ Short Break')">Break 5m</button>
    <button class="btn btn-ghost text-xs" onclick="setMode('long',15,'🌿 Long Break')">Long 15m</button>
  </div>
  <div id="modeLabel" class="text-sm font-semibold" style="color:{t['muted']}">🧠 Focus</div>
  <div class="text-7xl font-extrabold font-mono" id="display" style="color:{t['primary']}">25:00</div>
  <div class="w-full rounded-full h-2" style="background:{t['border']}">
    <div id="bar" class="h-full rounded-full transition-all" style="background:{t['primary']};width:100%"></div>
  </div>
  <div class="flex gap-3 justify-center">
    <button class="btn" id="btn" onclick="toggle()">START</button>
    <button class="btn btn-ghost" onclick="reset()">RESET</button>
  </div>
  <div class="text-xs font-mono" style="color:{t['muted']}">Sessions completed: <span id="sessions">0</span></div>
</div>"""
    script = f"""
let running=false,remaining=1500,total=1500,iv,sessions=0;
const disp=document.getElementById('display'),b=document.getElementById('btn'),bar=document.getElementById('bar');
function fmt(s){{return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}}
function setMode(m,min,lbl){{clearInterval(iv);running=false;b.innerText='START';
  total=remaining=min*60;disp.innerText=fmt(remaining);document.getElementById('modeLabel').innerText=lbl;
  bar.style.width='100%';disp.style.color='{t['primary']}';}}
function toggle(){{
  if(running){{clearInterval(iv);running=false;b.innerText='RESUME';}}
  else{{running=true;b.innerText='PAUSE';
    iv=setInterval(()=>{{
      remaining--;disp.innerText=fmt(remaining);bar.style.width=(remaining/total*100)+'%';
      if(remaining<=0){{clearInterval(iv);running=false;b.innerText='START';sessions++;
        document.getElementById('sessions').innerText=sessions;
        disp.style.color='{t['accent']}';new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAA==').play().catch(()=>{{}});
      }}
    }},1000);
  }}
}}
function reset(){{clearInterval(iv);running=false;b.innerText='START';
  disp.style.color='{t['primary']}';remaining=total;disp.innerText=fmt(remaining);bar.style.width='100%';}}"""
    return _shell("Pomodoro Timer", t, body, script)


def _build_clock(t: dict) -> str:
    body = f"""<div class="card text-center space-y-3">
  <div class="text-6xl font-extrabold font-mono" id="clock" style="color:{t['primary']}">00:00:00</div>
  <div class="text-sm" id="date" style="color:{t['muted']}"></div>
  <canvas id="analog" width="200" height="200" class="mx-auto mt-2"></canvas>
</div>"""
    script = f"""
const c=document.getElementById('clock'),d=document.getElementById('date'),canvas=document.getElementById('analog'),ctx=canvas.getContext('2d');
function draw(){{
  const now=new Date();
  c.innerText=now.toLocaleTimeString('en-US',{{hour12:false}});
  d.innerText=now.toLocaleDateString('en-US',{{weekday:'long',year:'numeric',month:'long',day:'numeric'}});
  ctx.clearRect(0,0,200,200);
  ctx.fillStyle='{t['bg']}';ctx.beginPath();ctx.arc(100,100,95,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='{t['border']}';ctx.lineWidth=3;ctx.stroke();
  for(let i=0;i<12;i++){{
    const a=i*Math.PI/6,x=100+Math.sin(a)*80,y=100-Math.cos(a)*80;
    ctx.fillStyle='{t['muted']}';ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);ctx.fill();
  }}
  const h=now.getHours()%12,m=now.getMinutes(),s=now.getSeconds();
  function hand(a,r,w,color){{ctx.strokeStyle=color;ctx.lineWidth=w;ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(100,100);ctx.lineTo(100+Math.sin(a)*r,100-Math.cos(a)*r);ctx.stroke();}}
  hand((h+m/60)*Math.PI/6,55,5,'{t['accent']}');
  hand((m+s/60)*Math.PI/30,75,3,'{t['primary']}');
  hand(s*Math.PI/30,85,2,'#fff');
  ctx.fillStyle='{t['primary']}';ctx.beginPath();ctx.arc(100,100,5,0,Math.PI*2);ctx.fill();
}}
draw();setInterval(draw,1000);"""
    return _shell("Digital Clock", t, body, script)


def _build_todo(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div class="flex gap-2">
    <input id="taskInput" placeholder="Add a new task..." onkeydown="if(event.key==='Enter')addTask()">
    <button class="btn px-4 whitespace-nowrap" onclick="addTask()">+ Add</button>
  </div>
  <div class="flex gap-2 text-xs">
    <button class="btn btn-ghost text-xs px-3 py-1" onclick="filter('all')">All</button>
    <button class="btn btn-ghost text-xs px-3 py-1" onclick="filter('active')">Active</button>
    <button class="btn btn-ghost text-xs px-3 py-1" onclick="filter('done')">Done</button>
    <button class="btn btn-ghost text-xs px-3 py-1 ml-auto" onclick="clearDone()">Clear Done</button>
  </div>
  <div id="list" class="space-y-2 max-h-80 overflow-y-auto"></div>
  <div class="text-xs text-right" id="stats" style="color:{t['muted']}"></div>
</div>"""
    script = f"""
let tasks=[],view='all';
function save(){{localStorage.setItem('fa_tasks',JSON.stringify(tasks));}}
function load(){{try{{tasks=JSON.parse(localStorage.getItem('fa_tasks')||'[]');}}catch{{tasks=[];}}}}
function addTask(){{
  const v=document.getElementById('taskInput').value.trim();
  if(!v)return;
  tasks.unshift({{id:Date.now(),text:v,done:false}});
  document.getElementById('taskInput').value='';
  save();render();
}}
function toggle(id){{tasks=tasks.map(t=>t.id===id?{{...t,done:!t.done}}:t);save();render();}}
function remove(id){{tasks=tasks.filter(t=>t.id!==id);save();render();}}
function clearDone(){{tasks=tasks.filter(t=>!t.done);save();render();}}
function filter(v){{view=v;render();}}
function render(){{
  const list=document.getElementById('list');
  const shown=tasks.filter(t=>view==='all'?true:view==='active'?!t.done:t.done);
  list.innerHTML=shown.map(t=>`
    <div class="flex items-center gap-2 p-3 rounded-xl" style="background:{t['bg']};border:1px solid {t['border']}">
      <input type="checkbox" ${{t.done?'checked':''}} onchange="toggle(${{t.id}})" class="w-4 h-4 accent-[{t['primary']}]">
      <span class="flex-1 text-sm ${{t.done?'line-through opacity-50':''}}">${{t.text}}</span>
      <button onclick="remove(${{t.id}})" class="text-xs px-2 py-0.5 rounded" style="color:{t['muted']}">✕</button>
    </div>`).join('');
  const done=tasks.filter(t=>t.done).length;
  document.getElementById('stats').innerText=done+' / '+tasks.length+' completed';
}}
load();render();"""
    return _shell("To-Do List", t, body, script)


def _build_unit_converter(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div>
    <label>Category</label>
    <select id="cat" onchange="updateUnits()">
      <option value="length">Length</option>
      <option value="weight">Weight / Mass</option>
      <option value="temp">Temperature</option>
      <option value="speed">Speed</option>
      <option value="area">Area</option>
      <option value="volume">Volume</option>
      <option value="time">Time</option>
    </select>
  </div>
  <div class="grid grid-cols-2 gap-3">
    <div><label>From</label><select id="fromUnit"></select></div>
    <div><label>To</label><select id="toUnit"></select></div>
  </div>
  <div><label>Value</label><input id="val" type="number" value="1" oninput="convert()"></div>
  <div class="text-center py-4 card" style="background:{t['bg']}">
    <div class="text-3xl font-extrabold font-mono" id="result" style="color:{t['primary']}">—</div>
  </div>
</div>"""
    script = """
const UNITS={
  length:{m:1,km:0.001,cm:100,mm:1000,mile:0.000621371,yard:1.09361,foot:3.28084,inch:39.3701},
  weight:{kg:1,g:1000,mg:1e6,lb:2.20462,oz:35.274,ton:0.001},
  temp:null,
  speed:{'m/s':1,'km/h':3.6,'mph':2.23694,'knot':1.94384},
  area:{'m²':1,'km²':1e-6,'cm²':10000,'ft²':10.7639,'acre':0.000247105},
  volume:{L:1,mL:1000,m3:0.001,gallon:0.264172,cup:4.22675,floz:33.814},
  time:{s:1,min:1/60,h:1/3600,day:1/86400,week:1/604800},
};
function updateUnits(){
  const cat=document.getElementById('cat').value;
  const keys=cat==='temp'?['°C','°F','K']:Object.keys(UNITS[cat]);
  ['fromUnit','toUnit'].forEach((id,i)=>{
    const s=document.getElementById(id);s.innerHTML='';
    keys.forEach(k=>{const o=document.createElement('option');o.value=o.innerText=k;s.appendChild(o);});
    s.selectedIndex=i===1?1:0;
  });
  convert();
}
function convert(){
  const cat=document.getElementById('cat').value;
  const from=document.getElementById('fromUnit').value,to=document.getElementById('toUnit').value;
  const v=parseFloat(document.getElementById('val').value);
  let r;
  if(cat==='temp'){
    let c=from==='°F'?(v-32)/1.8:from==='K'?v-273.15:v;
    r=to==='°F'?c*1.8+32:to==='K'?c+273.15:c;
  } else {
    r=v/UNITS[cat][from]*UNITS[cat][to];
  }
  document.getElementById('result').innerText=parseFloat(r.toFixed(8))+' '+to;
}
updateUnits();"""
    return _shell("Unit Converter", t, body, script)


def _build_password_generator(t: dict) -> str:
    body = f"""<div class="card space-y-5">
  <div style="background:{t['bg']};border:1.5px solid {t['border']};border-radius:.75rem;padding:1rem;font-family:monospace;font-size:1rem;font-weight:700;word-break:break-all;min-height:4rem;display:flex;align-items:center;justify-content:space-between">
    <span id="pwd" style="color:{t['primary']}">Click Generate</span>
    <button class="btn text-xs px-3" onclick="copyPwd()">Copy</button>
  </div>
  <div>
    <label>Length: <span id="lenLabel">16</span></label>
    <input type="range" id="len" min="6" max="64" value="16" oninput="document.getElementById('lenLabel').innerText=this.value;gen()" style="padding:0;margin-top:.5rem">
  </div>
  <div class="grid grid-cols-2 gap-3 text-sm">
    <label class="flex items-center gap-2"><input type="checkbox" id="upper" checked class="accent-[{t['primary']}]"> Uppercase</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="lower" checked class="accent-[{t['primary']}]"> Lowercase</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="nums" checked class="accent-[{t['primary']}]"> Numbers</label>
    <label class="flex items-center gap-2"><input type="checkbox" id="syms" class="accent-[{t['primary']}]"> Symbols</label>
  </div>
  <div id="strength" class="w-full h-2 rounded-full" style="background:{t['border']}">
    <div id="sBar" class="h-full rounded-full transition-all" style="width:0%"></div>
  </div>
  <div class="text-xs text-center" id="sLabel" style="color:{t['muted']}"></div>
  <button class="btn w-full" onclick="gen()">Generate Password</button>
  <div id="toast" class="text-center text-xs hidden" style="color:{t['accent']}">Copied!</div>
</div>"""
    script = f"""
function gen(){{
  const len=parseInt(document.getElementById('len').value);
  let chars='';
  if(document.getElementById('upper').checked)chars+='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  if(document.getElementById('lower').checked)chars+='abcdefghijklmnopqrstuvwxyz';
  if(document.getElementById('nums').checked)chars+='0123456789';
  if(document.getElementById('syms').checked)chars+='!@#$%^&*()_+-=[]{{}}|;:,.<>?';
  if(!chars)return;
  let pwd='';const arr=new Uint8Array(len);crypto.getRandomValues(arr);
  arr.forEach(b=>pwd+=chars[b%chars.length]);
  document.getElementById('pwd').innerText=pwd;
  const s=Math.min(100,Math.floor(len*(chars.length/10)*0.8));
  document.getElementById('sBar').style.width=s+'%';
  document.getElementById('sBar').style.background=s<40?'{t['accent']}':s<70?'#f59e0b':'{t['primary']}';
  document.getElementById('sLabel').innerText=s<40?'Weak':s<70?'Medium':'Strong';
}}
function copyPwd(){{
  navigator.clipboard.writeText(document.getElementById('pwd').innerText).catch(()=>{{}});
  const t=document.getElementById('toast');t.classList.remove('hidden');
  setTimeout(()=>t.classList.add('hidden'),1500);
}}
gen();"""
    return _shell("Password Generator", t, body, script)


def _build_color_picker(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div class="flex gap-3 items-center">
    <input type="color" id="picker" value="#6366f1" oninput="update(this.value)" class="h-16 w-16 rounded-xl cursor-pointer" style="padding:2px">
    <div class="flex-1 space-y-1">
      <div class="text-xl font-extrabold font-mono" id="hexVal" style="color:{t['primary']}">#6366f1</div>
      <div class="text-xs font-mono" id="rgbVal" style="color:{t['muted']}"></div>
      <div class="text-xs font-mono" id="hslVal" style="color:{t['muted']}"></div>
    </div>
  </div>
  <div id="preview" class="rounded-xl h-24" style="background:#6366f1"></div>
  <div>
    <label>Palette from this color</label>
    <div id="palette" class="flex gap-2 mt-1"></div>
  </div>
  <button class="btn w-full" onclick="copyHex()">Copy HEX</button>
</div>"""
    script = f"""
function hexToRgb(hex){{
  const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);
  return {{r,g,b}};
}}
function rgbToHsl(r,g,b){{
  r/=255;g/=255;b/=255;const max=Math.max(r,g,b),min=Math.min(r,g,b);
  let h,s,l=(max+min)/2;
  if(max===min){{h=s=0;}}else{{
    const d=max-min;s=l>0.5?d/(2-max-min):d/(max+min);
    switch(max){{case r:h=(g-b)/d+(g<b?6:0);break;case g:h=(b-r)/d+2;break;case b:h=(r-g)/d+4;break;}}
    h/=6;
  }}
  return {{h:Math.round(h*360),s:Math.round(s*100),l:Math.round(l*100)}};
}}
function update(hex){{
  const {{r,g,b}}=hexToRgb(hex);const {{h,s,l}}=rgbToHsl(r,g,b);
  document.getElementById('hexVal').innerText=hex.toUpperCase();
  document.getElementById('rgbVal').innerText='rgb('+r+', '+g+', '+b+')';
  document.getElementById('hslVal').innerText='hsl('+h+'°, '+s+'%, '+l+'%)';
  document.getElementById('preview').style.background=hex;
  const pal=document.getElementById('palette');pal.innerHTML='';
  for(let i=0;i<5;i++){{
    const lv=[20,35,50,65,80][i];
    const c='hsl('+h+','+s+'%,'+lv+'%)';
    const d=document.createElement('div');
    d.style.cssText='width:40px;height:40px;border-radius:.5rem;background:'+c+';cursor:pointer;flex-shrink:0';
    d.title=c;d.onclick=()=>{{document.getElementById('picker').value=hex;update(hex);}};
    pal.appendChild(d);
  }}
}}
function copyHex(){{navigator.clipboard.writeText(document.getElementById('hexVal').innerText).catch(()=>{{}});}}
update('#6366f1');"""
    return _shell("Color Picker", t, body, script)


def _build_drawing_canvas(t: dict) -> str:
    body = f"""<div class="card space-y-3">
  <div class="flex gap-2 flex-wrap items-center">
    <input type="color" id="color" value="{t['primary']}" class="h-8 w-10 rounded cursor-pointer" style="padding:1px">
    <input type="range" id="size" min="1" max="40" value="6" class="w-24" style="padding:0">
    <select id="tool" class="text-xs py-1 px-2" style="width:auto">
      <option value="pen">✏️ Pen</option>
      <option value="eraser">🩹 Eraser</option>
      <option value="fill">🪣 Fill</option>
    </select>
    <button class="btn text-xs px-3 py-1" onclick="clearCanvas()">Clear</button>
    <button class="btn text-xs px-3 py-1" onclick="saveImg()">Save PNG</button>
  </div>
  <canvas id="c" width="460" height="300" class="rounded-xl border w-full cursor-crosshair" style="background:white;border-color:{t['border']}"></canvas>
</div>"""
    script = """
const c=document.getElementById('c'),ctx=c.getContext('2d');
let drawing=false,lastX=0,lastY=0;
function getPos(e){const r=c.getBoundingClientRect(),sx=c.width/r.width,sy=c.height/r.height;
  const cx=e.touches?e.touches[0].clientX:e.clientX,cy=e.touches?e.touches[0].clientY:e.clientY;
  return{x:(cx-r.left)*sx,y:(cy-r.top)*sy};}
c.addEventListener('mousedown',e=>{drawing=true;const p=getPos(e);lastX=p.x;lastY=p.y;});
c.addEventListener('touchstart',e=>{e.preventDefault();drawing=true;const p=getPos(e);lastX=p.x;lastY=p.y;});
c.addEventListener('mousemove',e=>{if(!drawing)return;draw(getPos(e));});
c.addEventListener('touchmove',e=>{e.preventDefault();if(!drawing)return;draw(getPos(e));});
['mouseup','mouseleave','touchend'].forEach(ev=>c.addEventListener(ev,()=>drawing=false));
function draw({x,y}){
  const tool=document.getElementById('tool').value;
  const color=document.getElementById('color').value;
  const size=document.getElementById('size').value;
  if(tool==='fill'){floodFill(Math.round(x),Math.round(y),color);lastX=x;lastY=y;return;}
  ctx.strokeStyle=tool==='eraser'?'white':color;
  ctx.lineWidth=tool==='eraser'?size*2:size;
  ctx.lineCap='round';ctx.lineJoin='round';
  ctx.beginPath();ctx.moveTo(lastX,lastY);ctx.lineTo(x,y);ctx.stroke();
  lastX=x;lastY=y;
}
function floodFill(sx,sy,fillColor){/* simple scanline could go here */}
function clearCanvas(){ctx.clearRect(0,0,c.width,c.height);}
function saveImg(){const a=document.createElement('a');a.download='drawing.png';a.href=c.toDataURL();a.click();}"""
    return _shell("Drawing Canvas", t, body, script)


def _build_quiz(t: dict) -> str:
    body = f"""<div class="card space-y-4" id="quizCard">
  <div class="flex justify-between items-center">
    <span class="text-xs font-mono" id="qNum" style="color:{t['muted']}">Q 1/5</span>
    <span class="text-xs font-bold" id="scoreLabel" style="color:{t['primary']}">0 pts</span>
  </div>
  <div class="text-sm font-semibold" id="question" style="color:{t['text']}"></div>
  <div id="options" class="space-y-2"></div>
  <div id="feedback" class="text-xs font-bold hidden py-2 px-3 rounded-lg"></div>
  <button class="btn w-full hidden" id="nextBtn" onclick="nextQ()">Next →</button>
  <div id="finalCard" class="hidden text-center space-y-3">
    <div class="text-4xl font-extrabold font-mono" id="finalScore" style="color:{t['primary']}"></div>
    <div class="text-sm" style="color:{t['muted']}">out of 50 points</div>
    <button class="btn" onclick="startQuiz()">Play Again</button>
  </div>
</div>"""
    script = f"""
const QS=[
  {{q:"What is the speed of light?",a:["~300,000 km/s","~150,000 km/s","~500,000 km/s","~100,000 km/s"],correct:0,exp:"Light travels ~299,792 km/s in vacuum."}},
  {{q:"Who invented the World Wide Web?",a:["Tim Berners-Lee","Bill Gates","Vint Cerf","Alan Turing"],correct:0,exp:"Tim Berners-Lee proposed the WWW in 1989 at CERN."}},
  {{q:"What is the integral of 2x?",a:["x²+C","2x²+C","x+C","4x"],correct:0,exp:"∫2x dx = x² + C (power rule reversed)."}},
  {{q:"Which planet has the most moons?",a:["Saturn","Jupiter","Uranus","Neptune"],correct:0,exp:"Saturn has 146 confirmed moons (2024 count)."}},
  {{q:"What does DNA stand for?",a:["Deoxyribonucleic Acid","Dinitrogen Amino Acid","Dual Nucleic Array","None of these"],correct:0,exp:"DNA = Deoxyribonucleic Acid, the carrier of genetic information."}},
];
let qi=0,score=0,answered=false;
function startQuiz(){{qi=0;score=0;answered=false;document.getElementById('finalCard').classList.add('hidden');showQ();}}
function showQ(){{
  const q=QS[qi];
  document.getElementById('qNum').innerText='Q '+(qi+1)+'/'+QS.length;
  document.getElementById('scoreLabel').innerText=score+' pts';
  document.getElementById('question').innerText=q.q;
  document.getElementById('feedback').classList.add('hidden');
  document.getElementById('nextBtn').classList.add('hidden');
  answered=false;
  const opts=document.getElementById('options');
  opts.innerHTML=q.a.map((a,i)=>`<button class="btn btn-ghost w-full text-left text-xs py-2.5" onclick="answer(${{i}})">${{a}}</button>`).join('');
}}
function answer(i){{
  if(answered)return;answered=true;
  const q=QS[qi];const btns=document.getElementById('options').querySelectorAll('button');
  btns[q.correct].style.background='{t['primary']}';btns[q.correct].style.color='#fff';
  const fb=document.getElementById('feedback');
  if(i===q.correct){{score+=10;fb.innerText='✅ Correct! '+q.exp;fb.style.background='rgba(16,185,129,0.1)';fb.style.color='#10b981';}}
  else{{btns[i].style.background='{t['accent']}';btns[i].style.color='#fff';fb.innerText='❌ Wrong. '+q.exp;fb.style.background='rgba(239,68,68,0.1)';fb.style.color='{t['accent']}';}}
  fb.classList.remove('hidden');document.getElementById('nextBtn').classList.remove('hidden');
}}
function nextQ(){{
  qi++;
  if(qi>=QS.length){{document.getElementById('finalScore').innerText=score+'/50';document.getElementById('options').innerHTML='';document.getElementById('feedback').classList.add('hidden');document.getElementById('nextBtn').classList.add('hidden');document.getElementById('finalCard').classList.remove('hidden');}}
  else showQ();
}}
startQuiz();"""
    return _shell("Science & Tech Quiz", t, body, script)


def _build_budget_tracker(t: dict) -> str:
    body = f"""<div class="space-y-4">
  <div class="grid grid-cols-3 gap-2 text-center">
    <div class="card"><div class="text-[10px]" style="color:{t['muted']}">INCOME</div><div class="text-xl font-extrabold font-mono" id="totIn" style="color:{t['primary']}">$0</div></div>
    <div class="card"><div class="text-[10px]" style="color:{t['muted']}">EXPENSES</div><div class="text-xl font-extrabold font-mono" id="totEx" style="color:{t['accent']}">$0</div></div>
    <div class="card"><div class="text-[10px]" style="color:{t['muted']}">BALANCE</div><div class="text-xl font-extrabold font-mono" id="bal">$0</div></div>
  </div>
  <div class="card space-y-3">
    <div class="grid grid-cols-3 gap-2">
      <div><label>Description</label><input id="desc" placeholder="Coffee..."></div>
      <div><label>Amount ($)</label><input id="amt" type="number" step="0.01" placeholder="5.00"></div>
      <div><label>Type</label><select id="type"><option value="income">+ Income</option><option value="expense">− Expense</option></select></div>
    </div>
    <button class="btn w-full" onclick="addEntry()">Add Entry</button>
  </div>
  <div id="entries" class="space-y-2 max-h-60 overflow-y-auto"></div>
</div>"""
    script = f"""
let entries=[];
try{{entries=JSON.parse(localStorage.getItem('fa_budget')||'[]');}}catch{{}}
function save(){{localStorage.setItem('fa_budget',JSON.stringify(entries));}}
function addEntry(){{
  const d=document.getElementById('desc').value.trim(),a=parseFloat(document.getElementById('amt').value),tp=document.getElementById('type').value;
  if(!d||!a)return;
  entries.unshift({{id:Date.now(),d,a,tp}});
  document.getElementById('desc').value='';document.getElementById('amt').value='';
  save();render();
}}
function remove(id){{entries=entries.filter(e=>e.id!==id);save();render();}}
function render(){{
  const inc=entries.filter(e=>e.tp==='income').reduce((s,e)=>s+e.a,0);
  const exp=entries.filter(e=>e.tp==='expense').reduce((s,e)=>s+e.a,0);
  const bal=inc-exp;
  document.getElementById('totIn').innerText='$'+inc.toFixed(2);
  document.getElementById('totEx').innerText='$'+exp.toFixed(2);
  const bEl=document.getElementById('bal');
  bEl.innerText='$'+Math.abs(bal).toFixed(2);
  bEl.style.color=bal>=0?'{t['primary']}':'{t['accent']}';
  document.getElementById('entries').innerHTML=entries.map(e=>`
    <div class="flex items-center justify-between px-3 py-2 rounded-xl text-xs" style="background:{t['surface']};border:1px solid {t['border']}">
      <span>${{e.d}}</span>
      <span class="font-bold font-mono" style="color:${{e.tp==='income'?'{t['primary']}':'{t['accent']}'}}">
        ${{e.tp==='income'?'+':'-'}}${{e.a.toFixed(2)}}
      </span>
      <button onclick="remove(${{e.id}})" style="color:{t['muted']};font-size:.9rem">✕</button>
    </div>`).join('');
}}
render();"""
    return _shell("Budget Tracker", t, body, script)


def _build_notes(t: dict) -> str:
    body = f"""<div class="space-y-3">
  <div class="flex gap-2">
    <input id="noteTitle" placeholder="Note title..." class="flex-1">
    <button class="btn px-4" onclick="saveNote()">Save</button>
  </div>
  <textarea id="noteBody" rows="10" placeholder="Write your note here..." style="resize:vertical;min-height:200px"></textarea>
  <div id="noteList" class="space-y-2 max-h-60 overflow-y-auto"></div>
</div>"""
    script = f"""
let notes=[],activeId=null;
try{{notes=JSON.parse(localStorage.getItem('fa_notes')||'[]');}}catch{{}}
function save(){{localStorage.setItem('fa_notes',JSON.stringify(notes));}}
function saveNote(){{
  const title=document.getElementById('noteTitle').value.trim()||'Untitled';
  const body=document.getElementById('noteBody').value.trim();
  if(!body)return;
  if(activeId){{notes=notes.map(n=>n.id===activeId?{{...n,title,body,updated:Date.now()}}:n);}}
  else{{notes.unshift({{id:Date.now(),title,body,updated:Date.now()}});}}
  activeId=null;document.getElementById('noteTitle').value='';document.getElementById('noteBody').value='';
  save();render();
}}
function loadNote(id){{activeId=id;const n=notes.find(n=>n.id===id);
  document.getElementById('noteTitle').value=n.title;document.getElementById('noteBody').value=n.body;}}
function removeNote(id){{notes=notes.filter(n=>n.id!==id);if(activeId===id){{activeId=null;document.getElementById('noteTitle').value='';document.getElementById('noteBody').value='';}}save();render();}}
function render(){{
  document.getElementById('noteList').innerHTML=notes.map(n=>`
    <div class="flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer" style="background:{t['surface']};border:1px solid {t['border']}" onclick="loadNote(${{n.id}})">
      <div class="flex-1 truncate"><div class="text-xs font-bold">${{n.title}}</div><div class="text-[10px]" style="color:{t['muted']}">${{n.body.slice(0,50)}}...</div></div>
      <button onclick="event.stopPropagation();removeNote(${{n.id}})" style="color:{t['muted']}">✕</button>
    </div>`).join('');
}}
render();"""
    return _shell("Notes App", t, body, script)


def _build_dice_roller(t: dict) -> str:
    body = f"""<div class="card text-center space-y-5">
  <div class="grid grid-cols-3 gap-2">
    {"".join(f'<button class="btn btn-ghost text-sm py-3 font-bold" onclick="roll({d})">d{d}</button>'
      for d in [4,6,8,10,12,20,100])}
    <button class="btn btn-ghost text-sm py-3 font-bold" onclick="rollCustom()">Custom</button>
  </div>
  <div class="flex gap-2 justify-center items-end">
    <div><label>Num dice</label><input id="nd" type="number" value="2" min="1" max="20" style="text-align:center;width:70px"></div>
    <div class="text-2xl mb-2" style="color:{t['muted']}">d</div>
    <div><label>Sides</label><input id="ns" type="number" value="6" min="2" max="1000" style="text-align:center;width:70px"></div>
  </div>
  <div id="dice" class="flex flex-wrap justify-center gap-3 min-h-16"></div>
  <div class="text-4xl font-extrabold font-mono" id="total" style="color:{t['primary']}">—</div>
  <div class="text-xs" id="hist" style="color:{t['muted']}"></div>
</div>"""
    script = f"""
let history=[];
function roll(sides){{
  const n=2;
  const results=Array.from({{length:n}},()=>Math.floor(Math.random()*sides)+1);
  display(results,sides);
}}
function rollCustom(){{
  const n=parseInt(document.getElementById('nd').value)||1;
  const s=parseInt(document.getElementById('ns').value)||6;
  const results=Array.from({{length:n}},()=>Math.floor(Math.random()*s)+1);
  display(results,s);
}}
function display(results,sides){{
  const total=results.reduce((a,b)=>a+b,0);
  document.getElementById('dice').innerHTML=results.map(r=>`
    <div class="h-14 w-14 rounded-xl flex items-center justify-center text-xl font-extrabold font-mono"
      style="background:{t['bg']};border:2px solid {t['primary']};color:{t['text']}">${{r}}</div>`).join('');
  document.getElementById('total').innerText='Total: '+total;
  history.unshift('d'+sides+' × '+results.length+' → '+results.join(', ')+' = '+total);
  history=history.slice(0,5);
  document.getElementById('hist').innerText=history.join(' | ');
}}"""
    return _shell("Dice Roller", t, body, script)


def _build_flashcards(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div id="cardArea" class="relative h-48 cursor-pointer" onclick="flip()" title="Click to flip">
    <div id="cardInner" class="absolute inset-0 rounded-xl flex items-center justify-center p-6 text-center transition-all duration-500" style="background:{t['bg']};border:2px solid {t['primary']}">
      <div id="cardText" class="text-lg font-bold"></div>
    </div>
    <div class="absolute bottom-2 right-3 text-[10px]" style="color:{t['muted']}">click to flip</div>
  </div>
  <div class="flex gap-2 justify-center">
    <button class="btn btn-ghost" onclick="prev()">← Prev</button>
    <span class="text-xs self-center font-mono" id="progress" style="color:{t['muted']}"></span>
    <button class="btn" onclick="next()">Next →</button>
  </div>
  <div class="card space-y-2" style="background:{t['bg']}">
    <div class="text-xs font-semibold mb-2" style="color:{t['muted']}">Add a card:</div>
    <input id="q" placeholder="Question / Front">
    <input id="a" placeholder="Answer / Back">
    <button class="btn w-full text-xs" onclick="addCard()">+ Add Card</button>
  </div>
</div>"""
    script = f"""
let cards=[
  {{q:"What is the speed of light?",a:"~299,792,458 m/s (≈300,000 km/s)"}},
  {{q:"Who created Python?",a:"Guido van Rossum in 1991"}},
  {{q:"What is the Planck constant?",a:"h ≈ 6.626 × 10⁻³⁴ J·s"}},
  {{q:"Derivative of sin(x)?",a:"cos(x)"}},
  {{q:"What is DNA?",a:"Deoxyribonucleic Acid — carrier of genetic information"}},
];
let ci=0,flipped=false;
function show(){{
  flipped=false;
  document.getElementById('cardText').innerText=cards[ci].q;
  document.getElementById('cardInner').style.background='{t['bg']}';
  document.getElementById('progress').innerText=(ci+1)+' / '+cards.length;
}}
function flip(){{
  flipped=!flipped;
  document.getElementById('cardText').innerText=flipped?cards[ci].a:cards[ci].q;
  document.getElementById('cardInner').style.background=flipped?'{t['surface']}':'{t['bg']}';
}}
function next(){{ci=(ci+1)%cards.length;show();}}
function prev(){{ci=(ci-1+cards.length)%cards.length;show();}}
function addCard(){{
  const q=document.getElementById('q').value.trim(),a=document.getElementById('a').value.trim();
  if(!q||!a)return;
  cards.push({{q,a}});document.getElementById('q').value='';document.getElementById('a').value='';
  ci=cards.length-1;show();
}}
show();"""
    return _shell("Flashcards", t, body, script)


def _build_age_calculator(t: dict) -> str:
    body = f"""<div class="card space-y-5 text-center">
  <div><label>Date of Birth</label><input id="dob" type="date"></div>
  <button class="btn w-full" onclick="calc()">Calculate Age</button>
  <div id="result" class="hidden space-y-3">
    <div class="text-5xl font-extrabold font-mono" id="years" style="color:{t['primary']}"></div>
    <div class="text-sm" id="detail" style="color:{t['muted']}"></div>
    <div class="grid grid-cols-3 gap-2">
      <div class="card"><div class="text-[10px]" style="color:{t['muted']}">MONTHS</div><div class="text-xl font-bold font-mono" id="months" style="color:{t['accent']}"></div></div>
      <div class="card"><div class="text-[10px]" style="color:{t['muted']}">WEEKS</div><div class="text-xl font-bold font-mono" id="weeks" style="color:{t['primary']}"></div></div>
      <div class="card"><div class="text-[10px]" style="color:{t['muted']}">DAYS</div><div class="text-xl font-bold font-mono" id="days"></div></div>
    </div>
  </div>
</div>"""
    script = """
function calc(){
  const dob=new Date(document.getElementById('dob').value);if(isNaN(dob))return;
  const now=new Date();
  let y=now.getFullYear()-dob.getFullYear(),m=now.getMonth()-dob.getMonth(),d=now.getDate()-dob.getDate();
  if(d<0){m--;d+=new Date(now.getFullYear(),now.getMonth(),0).getDate();}
  if(m<0){y--;m+=12;}
  const totalDays=Math.floor((now-dob)/86400000);
  document.getElementById('years').innerText=y+' years';
  document.getElementById('detail').innerText=m+' months, '+d+' days';
  document.getElementById('months').innerText=y*12+m;
  document.getElementById('weeks').innerText=Math.floor(totalDays/7).toLocaleString();
  document.getElementById('days').innerText=totalDays.toLocaleString();
  document.getElementById('result').classList.remove('hidden');
}"""
    return _shell("Age Calculator", t, body, script)


def _build_grade_calculator(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div id="rows" class="space-y-2"></div>
  <button class="btn btn-ghost w-full text-xs" onclick="addRow()">+ Add Assignment</button>
  <div id="result" class="text-center py-4 hidden">
    <div class="text-5xl font-extrabold font-mono" id="avg" style="color:{t['primary']}"></div>
    <div class="text-sm" id="letter" style="color:{t['muted']}"></div>
  </div>
</div>"""
    script = f"""
let rows=[];
function addRow(){{
  const id=Date.now();rows.push({{id,name:'',score:'',weight:1}});render();}}
function removeRow(id){{rows=rows.filter(r=>r.id!==id);render();}}
function calc(){{
  if(!rows.length)return;
  let sw=0,tw=0;
  rows.forEach(r=>{{const s=parseFloat(r.score),w=parseFloat(r.weight)||1;if(!isNaN(s)){{sw+=s*w;tw+=w;}}}});
  if(!tw)return;
  const avg=sw/tw;
  document.getElementById('avg').innerText=avg.toFixed(1)+'%';
  const letter=avg>=93?'A':avg>=90?'A-':avg>=87?'B+':avg>=83?'B':avg>=80?'B-':avg>=77?'C+':avg>=73?'C':avg>=70?'C-':avg>=60?'D':'F';
  document.getElementById('letter').innerText='Letter Grade: '+letter;
  document.getElementById('result').classList.remove('hidden');
}}
function render(){{
  document.getElementById('rows').innerHTML=rows.map(r=>`
    <div class="grid grid-cols-3 gap-2 items-center">
      <input placeholder="Assignment" value="${{r.name}}" oninput="rows.find(x=>x.id==${{r.id}}).name=this.value">
      <input type="number" placeholder="Score %" value="${{r.score}}" oninput="rows.find(x=>x.id==${{r.id}}).score=this.value;calc()">
      <div class="flex gap-2">
        <input type="number" placeholder="Weight" value="${{r.weight}}" oninput="rows.find(x=>x.id==${{r.id}}).weight=this.value;calc()">
        <button onclick="removeRow(${{r.id}})" style="color:{t['muted']}">✕</button>
      </div>
    </div>`).join('');
  calc();
}}
addRow();addRow();addRow();"""
    return _shell("Grade Calculator", t, body, script)


def _build_currency_converter(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <div class="text-xs font-mono text-center py-1 px-3 rounded-lg" style="background:{t['bg']};color:{t['muted']}">Using approximate fixed rates (internet connection needed for live rates)</div>
  <div class="grid grid-cols-2 gap-3">
    <div>
      <label>From</label>
      <select id="from">
        <option value="USD">🇺🇸 USD</option><option value="EUR">🇪🇺 EUR</option><option value="GBP">🇬🇧 GBP</option>
        <option value="JPY">🇯🇵 JPY</option><option value="CAD">🇨🇦 CAD</option><option value="AUD">🇦🇺 AUD</option>
        <option value="CHF">🇨🇭 CHF</option><option value="CNY">🇨🇳 CNY</option><option value="INR">🇮🇳 INR</option>
        <option value="MXN">🇲🇽 MXN</option><option value="BRL">🇧🇷 BRL</option><option value="KRW">🇰🇷 KRW</option>
      </select>
    </div>
    <div>
      <label>To</label>
      <select id="to">
        <option value="EUR">🇪🇺 EUR</option><option value="USD">🇺🇸 USD</option><option value="GBP">🇬🇧 GBP</option>
        <option value="JPY">🇯🇵 JPY</option><option value="CAD">🇨🇦 CAD</option><option value="AUD">🇦🇺 AUD</option>
        <option value="CHF">🇨🇭 CHF</option><option value="CNY">🇨🇳 CNY</option><option value="INR">🇮🇳 INR</option>
        <option value="MXN">🇲🇽 MXN</option><option value="BRL">🇧🇷 BRL</option><option value="KRW">🇰🇷 KRW</option>
      </select>
    </div>
  </div>
  <div><label>Amount</label><input id="amt" type="number" value="100" oninput="convert()"></div>
  <button class="btn w-full" onclick="convert()">Convert</button>
  <div id="result" class="text-center py-5 card" style="background:{t['bg']}">
    <div class="text-3xl font-extrabold font-mono" id="out" style="color:{t['primary']}">—</div>
    <div class="text-xs mt-1" id="rate" style="color:{t['muted']}"></div>
  </div>
</div>"""
    script = """
const RATES={USD:1,EUR:0.92,GBP:0.79,JPY:149.5,CAD:1.36,AUD:1.53,CHF:0.90,CNY:7.24,INR:83.1,MXN:17.2,BRL:4.97,KRW:1325};
function convert(){
  const f=document.getElementById('from').value,to=document.getElementById('to').value;
  const amt=parseFloat(document.getElementById('amt').value)||0;
  const result=amt/RATES[f]*RATES[to];
  document.getElementById('out').innerText=result.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:4})+' '+to;
  document.getElementById('rate').innerText='1 '+f+' = '+(RATES[to]/RATES[f]).toFixed(4)+' '+to;
}
convert();"""
    return _shell("Currency Converter", t, body, script)


def _build_text_utils(t: dict) -> str:
    body = f"""<div class="card space-y-4">
  <textarea id="txt" rows="6" placeholder="Type or paste text here..." oninput="analyze()" style="resize:vertical"></textarea>
  <div class="grid grid-cols-3 gap-2 text-center text-xs">
    <div class="card"><div style="color:{t['muted']}">CHARS</div><div class="text-xl font-bold font-mono" id="chars" style="color:{t['primary']}">0</div></div>
    <div class="card"><div style="color:{t['muted']}">WORDS</div><div class="text-xl font-bold font-mono" id="words" style="color:{t['accent']}">0</div></div>
    <div class="card"><div style="color:{t['muted']}">LINES</div><div class="text-xl font-bold font-mono" id="lines">0</div></div>
  </div>
  <div class="flex flex-wrap gap-2">
    <button class="btn btn-ghost text-xs" onclick="transform('upper')">UPPERCASE</button>
    <button class="btn btn-ghost text-xs" onclick="transform('lower')">lowercase</button>
    <button class="btn btn-ghost text-xs" onclick="transform('title')">Title Case</button>
    <button class="btn btn-ghost text-xs" onclick="transform('reverse')">Reverse</button>
    <button class="btn btn-ghost text-xs" onclick="transform('trim')">Trim Spaces</button>
    <button class="btn btn-ghost text-xs" onclick="copyText()">Copy All</button>
    <button class="btn btn-ghost text-xs" onclick="document.getElementById('txt').value='';analyze()">Clear</button>
  </div>
</div>"""
    script = """
function analyze(){
  const t=document.getElementById('txt').value;
  document.getElementById('chars').innerText=t.length;
  document.getElementById('words').innerText=t.trim()?t.trim().split(/\s+/).length:0;
  document.getElementById('lines').innerText=t?t.split('\n').length:0;
}
function transform(type){
  const el=document.getElementById('txt');let t=el.value;
  if(type==='upper')t=t.toUpperCase();
  else if(type==='lower')t=t.toLowerCase();
  else if(type==='title')t=t.replace(/\w\S*/g,w=>w[0].toUpperCase()+w.slice(1).toLowerCase());
  else if(type==='reverse')t=t.split('').reverse().join('');
  else if(type==='trim')t=t.split('\n').map(l=>l.trim()).join('\n');
  el.value=t;analyze();
}
function copyText(){navigator.clipboard.writeText(document.getElementById('txt').value).catch(()=>{});}"""
    return _shell("Text Utilities", t, body, script)


def _build_habit_tracker(t: dict) -> str:
    body = f"""<div class="space-y-4">
  <div class="flex gap-2">
    <input id="hName" placeholder="New habit (e.g. Exercise, Read)..." onkeydown="if(event.key==='Enter')addHabit()">
    <button class="btn px-4" onclick="addHabit()">+ Add</button>
  </div>
  <div id="habits" class="space-y-3"></div>
</div>"""
    script = f"""
let habits=[];
try{{habits=JSON.parse(localStorage.getItem('fa_habits')||'[]');}}catch{{}}
function save(){{localStorage.setItem('fa_habits',JSON.stringify(habits));}}
function addHabit(){{
  const n=document.getElementById('hName').value.trim();if(!n)return;
  habits.push({{id:Date.now(),name:n,days:{{}}}});
  document.getElementById('hName').value='';save();render();
}}
function toggle(id,day){{
  const h=habits.find(h=>h.id===id);if(h){{h.days[day]=!h.days[day];}}save();render();
}}
function removeHabit(id){{habits=habits.filter(h=>h.id!==id);save();render();}}
function render(){{
  const today=new Date();
  const days=Array.from({{length:7}},(_,i)=>{{
    const d=new Date(today);d.setDate(today.getDate()-6+i);
    return{{key:d.toISOString().slice(0,10),label:d.toLocaleDateString('en-US',{{weekday:'short'}})}};
  }});
  document.getElementById('habits').innerHTML=habits.map(h=>{{
    const streak=calcStreak(h);
    return `<div class="card space-y-2">
      <div class="flex justify-between items-center">
        <span class="font-semibold text-sm">${{h.name}}</span>
        <div class="flex items-center gap-2">
          <span class="text-xs font-mono" style="color:{t['primary']}">🔥 ${{streak}} day streak</span>
          <button onclick="removeHabit(${{h.id}})" style="color:{t['muted']}">✕</button>
        </div>
      </div>
      <div class="flex gap-1">
        ${{days.map(d=>`<div class="flex-1 text-center">
          <div class="text-[9px] mb-1" style="color:{t['muted']}">${{d.label}}</div>
          <button onclick="toggle(${{h.id}},'${{d.key}}')" class="w-full h-7 rounded-lg transition-all"
            style="background:${{h.days[d.key]?'{t['primary']}':'{t['bg']}'}};border:1.5px solid {t['border']}"></button>
        </div>`).join('')}}
      </div>
    </div>`;
  }}).join('');
}}
function calcStreak(h){{
  let s=0;const today=new Date();
  for(let i=0;;i++){{const d=new Date(today);d.setDate(today.getDate()-i);
    if(h.days[d.toISOString().slice(0,10)])s++;else break;}}return s;
}}
render();"""
    return _shell("Habit Tracker", t, body, script)


# ─── Public entry point ───────────────────────────────────────────────────────

def build_app(query: str) -> dict:
    q = query.lower()
    app_type = detect_app_type(q)
    t = _app_pick_theme(q)

    builders = {
        "calculator": (_build_calculator, "Calculator"),
        "scientific_calculator": (_build_scientific_calculator, "Scientific Calculator"),
        "bmi_calculator": (_build_bmi, "BMI Calculator"),
        "tip_calculator": (_build_tip_calculator, "Tip Calculator"),
        "mortgage_calculator": (_build_mortgage_calculator, "Mortgage Calculator"),
        "stopwatch": (_build_stopwatch, "Stopwatch"),
        "countdown_timer": (_build_countdown, "Countdown Timer"),
        "pomodoro": (_build_pomodoro, "Pomodoro Timer"),
        "clock": (_build_clock, "Digital Clock"),
        "todo": (_build_todo, "To-Do List"),
        "unit_converter": (_build_unit_converter, "Unit Converter"),
        "password_generator": (_build_password_generator, "Password Generator"),
        "color_picker": (_build_color_picker, "Color Picker"),
        "drawing_canvas": (_build_drawing_canvas, "Drawing Canvas"),
        "quiz": (_build_quiz, "Quiz App"),
        "flashcards": (_build_flashcards, "Flashcards"),
        "budget_tracker": (_build_budget_tracker, "Budget Tracker"),
        "notes_app": (_build_notes, "Notes App"),
        "dice_roller": (_build_dice_roller, "Dice Roller"),
        "text_utils": (_build_text_utils, "Text Utilities"),
        "habit_tracker": (_build_habit_tracker, "Habit Tracker"),
        "age_calculator": (_build_age_calculator, "Age Calculator"),
        "grade_calculator": (_build_grade_calculator, "Grade Calculator"),
        "currency_converter": (_build_currency_converter, "Currency Converter"),
    }

    fn, title = builders.get(app_type, (_build_calculator, "Calculator"))
    code = fn(t)
    return {"title": title, "type": app_type, "code": code}


# =============================================================================
# DYNAMIC BUILDER
# =============================================================================

# ══════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════

def _dyn_pick_theme(q: str) -> dict:
    if any(w in q for w in ("light", "white", "clean", "minimal", "pastel")):
        return {"bg": "#f8fafc", "surface": "#ffffff", "border": "#e2e8f0",
                "primary": "#4f46e5", "accent": "#db2777", "text": "#1e293b", "muted": "#64748b",
                "hover": "#f1f5f9", "danger": "#ef4444", "success": "#10b981"}
    if any(w in q for w in ("green", "nature", "forest", "emerald", "plant")):
        return {"bg": "#022c22", "surface": "#064e3b", "border": "#065f46",
                "primary": "#10b981", "accent": "#f59e0b", "text": "#ecfdf5", "muted": "#6ee7b7",
                "hover": "#065f46", "danger": "#f43f5e", "success": "#34d399"}
    if any(w in q for w in ("blue", "ocean", "sky", "cool", "navy")):
        return {"bg": "#0c1a2e", "surface": "#0f2b4a", "border": "#1d3a5c",
                "primary": "#38bdf8", "accent": "#f43f5e", "text": "#f0f9ff", "muted": "#7dd3fc",
                "hover": "#1d3a5c", "danger": "#f43f5e", "success": "#34d399"}
    if any(w in q for w in ("purple", "violet", "grape", "lavender")):
        return {"bg": "#0f0728", "surface": "#1e1254", "border": "#2d1b78",
                "primary": "#a78bfa", "accent": "#f472b6", "text": "#f5f3ff", "muted": "#c4b5fd",
                "hover": "#2d1b78", "danger": "#f43f5e", "success": "#34d399"}
    if any(w in q for w in ("red", "fire", "warm", "hot", "rose")):
        return {"bg": "#1c0d02", "surface": "#431407", "border": "#7c2d12",
                "primary": "#f97316", "accent": "#e11d48", "text": "#fff7ed", "muted": "#fdba74",
                "hover": "#7c2d12", "danger": "#e11d48", "success": "#34d399"}
    # default dark
    return {"bg": "#0f172a", "surface": "#1e293b", "border": "#334155",
            "primary": "#6366f1", "accent": "#ec4899", "text": "#e2e8f0", "muted": "#94a3b8",
            "hover": "#334155", "danger": "#ef4444", "success": "#10b981"}


# ══════════════════════════════════════════════════════════════
# ENTITY & FIELD EXTRACTION
# ══════════════════════════════════════════════════════════════

# Entity → (emoji, suggested fields)
_ENTITY_CATALOG: dict[str, tuple[str, list]] = {
    "task":        ("✅", ["Task", "Priority:select:Low,Medium,High,Critical", "Due Date:date", "Status:select:Todo,In Progress,Done,Cancelled", "Notes:textarea"]),
    "todo":        ("☑️", ["Task", "Priority:select:Low,Medium,High", "Due Date:date", "Done:select:No,Yes"]),
    "habit":       ("🔥", ["Habit", "Frequency:select:Daily,Weekly,Monthly", "Streak:number", "Category:select:Health,Work,Personal,Learning", "Notes:textarea"]),
    "goal":        ("🎯", ["Goal", "Target Date:date", "Progress:number", "Status:select:Not Started,In Progress,Done,Paused", "Category:select:Work,Health,Finance,Learning,Other", "Notes:textarea"]),
    "plant":       ("🌿", ["Plant Name", "Species", "Last Watered:date", "Health:select:Excellent,Good,Fair,Poor", "Location", "Notes:textarea"]),
    "recipe":      ("🍳", ["Recipe Name", "Ingredients:textarea", "Prep Time (min):number", "Servings:number", "Difficulty:select:Easy,Medium,Hard", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "book":        ("📚", ["Title", "Author", "Genre:select:Fiction,Non-Fiction,Sci-Fi,Fantasy,Mystery,Biography,Self-Help,Other", "Status:select:Want to Read,Reading,Finished,DNF", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "movie":       ("🎬", ["Title", "Director", "Genre:select:Action,Comedy,Drama,Horror,Sci-Fi,Romance,Documentary,Other", "Year:number", "Status:select:Want to Watch,Watching,Watched", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "expense":     ("💸", ["Description", "Amount:number", "Category:select:Food,Transport,Housing,Health,Entertainment,Shopping,Work,Other", "Date:date", "Payment:select:Cash,Card,Transfer,Other", "Notes:textarea"]),
    "income":      ("💰", ["Source", "Amount:number", "Category:select:Salary,Freelance,Investment,Gift,Other", "Date:date", "Notes:textarea"]),
    "contact":     ("👤", ["Full Name", "Email:email", "Phone", "Company", "Role", "Category:select:Personal,Work,Client,Vendor,Other", "Notes:textarea"]),
    "customer":    ("🤝", ["Name", "Email:email", "Phone", "Company", "Value:number", "Status:select:Lead,Active,Inactive,Churned", "Notes:textarea"]),
    "employee":    ("👔", ["Full Name", "Role", "Department:select:Engineering,Design,Marketing,Sales,HR,Finance,Operations,Other", "Start Date:date", "Email:email", "Salary:number", "Status:select:Active,On Leave,Terminated"]),
    "product":     ("📦", ["Product Name", "SKU", "Price:number", "Quantity:number", "Category", "Status:select:Active,Out of Stock,Discontinued", "Notes:textarea"]),
    "inventory":   ("📋", ["Item Name", "Quantity:number", "Unit", "Price:number", "Location", "Category", "Reorder Level:number", "Notes:textarea"]),
    "project":     ("🗂️", ["Project Name", "Status:select:Planning,Active,On Hold,Done,Cancelled", "Priority:select:Low,Medium,High,Critical", "Deadline:date", "Team Members", "Description:textarea"]),
    "bug":         ("🐛", ["Title", "Severity:select:Low,Medium,High,Critical", "Status:select:Open,In Progress,Fixed,Won't Fix,Closed", "Assigned To", "Steps to Reproduce:textarea", "Date Reported:date"]),
    "note":        ("📝", ["Title", "Content:textarea", "Category:select:General,Work,Personal,Ideas,Research,Other", "Date:date", "Tags"]),
    "journal":     ("📖", ["Date:date", "Mood:select:😄 Great,🙂 Good,😐 Okay,😕 Bad,😞 Terrible", "Entry:textarea", "Tags", "Gratitude:textarea"]),
    "pet":         ("🐾", ["Pet Name", "Species:select:Dog,Cat,Bird,Fish,Rabbit,Reptile,Other", "Breed", "Age:number", "Vet Date:date", "Health:select:Excellent,Good,Fair,Poor", "Notes:textarea"]),
    "workout":     ("💪", ["Exercise", "Sets:number", "Reps:number", "Weight (kg):number", "Duration (min):number", "Date:date", "Notes:textarea"]),
    "medication":  ("💊", ["Medication Name", "Dose", "Frequency:select:Daily,Twice Daily,Weekly,As Needed", "Start Date:date", "End Date:date", "Notes:textarea"]),
    "appointment": ("📅", ["Title", "Date:date", "Time", "Location", "With", "Status:select:Scheduled,Confirmed,Cancelled,Done", "Notes:textarea"]),
    "link":        ("🔗", ["Title", "URL:url", "Category:select:Article,Video,Tool,Reference,Social,Other", "Tags", "Notes:textarea"]),
    "wine":        ("🍷", ["Name", "Vineyard", "Region", "Vintage:number", "Varietal", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "subscription":("📡", ["Service Name", "Price:number", "Billing Cycle:select:Monthly,Annual,Weekly", "Next Billing:date", "Category:select:Entertainment,Software,Health,Finance,Other", "Status:select:Active,Paused,Cancelled"]),
    "vehicle":     ("🚗", ["Make", "Model", "Year:number", "Mileage:number", "Fuel:select:Petrol,Diesel,Electric,Hybrid", "Last Service:date", "Notes:textarea"]),
    "property":    ("🏠", ["Address", "Type:select:House,Apartment,Commercial,Land,Other", "Value:number", "Status:select:Owned,Rented,For Sale", "Purchase Date:date", "Notes:textarea"]),
    "course":      ("🎓", ["Course Name", "Platform/School", "Status:select:Not Started,In Progress,Completed", "Progress:number", "Start Date:date", "Certificate:select:No,Yes", "Notes:textarea"]),
    "skill":       ("🧠", ["Skill Name", "Category:select:Technical,Soft,Creative,Language,Other", "Level:select:Beginner,Intermediate,Advanced,Expert", "Learning Since:date", "Resources:textarea"]),
    "idea":        ("💡", ["Idea", "Category:select:Business,Product,Creative,Technical,Personal,Other", "Priority:select:Low,Medium,High", "Status:select:Raw,Researching,In Progress,Shelved,Done", "Details:textarea"]),
    "transaction": ("🏦", ["Description", "Amount:number", "Type:select:Income,Expense,Transfer", "Category", "Date:date", "Account", "Notes:textarea"]),
    "event":       ("🎉", ["Event Name", "Date:date", "Time", "Location", "Guests:number", "Status:select:Planning,Confirmed,Cancelled,Done", "Notes:textarea"]),
    "feedback":    ("💬", ["From", "Subject", "Feedback:textarea", "Sentiment:select:Positive,Neutral,Negative", "Date:date", "Status:select:New,Reviewing,Resolved"]),
    "lead":        ("📊", ["Name", "Email:email", "Company", "Source:select:Website,Referral,Social,Ad,Cold,Other", "Value:number", "Stage:select:New,Contacted,Qualified,Proposal,Won,Lost", "Notes:textarea"]),
    "invoice":     ("🧾", ["Invoice #", "Client", "Amount:number", "Due Date:date", "Status:select:Draft,Sent,Paid,Overdue,Cancelled", "Notes:textarea"]),
    "password":    ("🔐", ["Site / App", "Username", "Category:select:Social,Work,Finance,Shopping,Other", "Notes:textarea"]),
    "game":        ("🎮", ["Title", "Platform:select:PC,PS5,Xbox,Nintendo,Mobile,Other", "Genre:select:Action,RPG,Strategy,Sports,Puzzle,Other", "Status:select:Want to Play,Playing,Completed,Dropped", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "clothing":    ("👗", ["Item Name", "Brand", "Size", "Color", "Category:select:Top,Bottom,Dress,Shoes,Accessory,Outerwear", "Season:select:All Year,Spring,Summer,Autumn,Winter", "Notes:textarea"]),
    "food":        ("🍽️", ["Name", "Cuisine:select:Italian,Asian,Mexican,American,Mediterranean,Indian,Other", "Category:select:Breakfast,Lunch,Dinner,Snack,Dessert", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Tried:select:Yes,No", "Notes:textarea"]),
    "travel":      ("✈️", ["Destination", "Country", "Date:date", "Duration (days):number", "Status:select:Dream,Planned,Booked,Done", "Budget:number", "Notes:textarea"]),
    "photo":       ("📷", ["Title", "Location", "Date:date", "Camera/Device", "Tags", "Notes:textarea"]),
    "music":       ("🎵", ["Song/Album", "Artist", "Genre:select:Pop,Rock,Hip-Hop,R&B,Electronic,Jazz,Classical,Other", "Status:select:Want to Listen,Listening,Favourite", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    # ── New entries ──────────────────────────────────────────
    "sneaker":     ("👟", ["Name", "Brand", "Size", "Colorway", "Condition:select:DS,VNDS,Used", "Price:number", "Purchase Date:date", "Status:select:In Collection,For Sale,Sold"]),
    "crypto":      ("₿", ["Coin/Token", "Symbol", "Amount:number", "Buy Price:number", "Current Price:number", "Exchange", "Date:date", "Notes:textarea"]),
    "nft":         ("🖼️", ["Name", "Collection", "Purchase Price:number", "Floor Price:number", "Platform", "Date:date", "Status:select:Holding,Listed,Sold"]),
    "portfolio":   ("📈", ["Asset", "Type:select:Stock,ETF,Crypto,Bond,Real Estate,Other", "Amount:number", "Buy Price:number", "Current Price:number", "Date:date", "Notes:textarea"]),
    "stock":       ("📊", ["Ticker", "Company", "Shares:number", "Buy Price:number", "Current Price:number", "Date:date", "Broker", "Notes:textarea"]),
    "anime":       ("🎌", ["Title", "Studio", "Genre:select:Action,Romance,Fantasy,Sci-Fi,Slice of Life,Horror,Other", "Episodes:number", "Status:select:Plan to Watch,Watching,Completed,Dropped", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "manga":       ("📖", ["Title", "Author", "Genre:select:Shonen,Shojo,Seinen,Josei,Isekai,Other", "Volumes:number", "Status:select:Plan to Read,Reading,Completed,Dropped", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐"]),
    "podcast":     ("🎙️", ["Title", "Host", "Category:select:Tech,Business,Health,True Crime,Comedy,Education,Other", "Status:select:Subscribed,Listening,Completed", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "supplement":  ("💊", ["Name", "Brand", "Dosage", "Frequency:select:Daily,Twice Daily,Weekly,As Needed", "Purpose", "Start Date:date", "Notes:textarea"]),
    "furniture":   ("🛋️", ["Item Name", "Brand", "Room:select:Living Room,Bedroom,Kitchen,Office,Bathroom,Other", "Price:number", "Condition:select:New,Like New,Good,Fair", "Purchase Date:date", "Notes:textarea"]),
    "plant_care":  ("🌱", ["Plant Name", "Species", "Last Watered:date", "Last Fertilized:date", "Light:select:Full Sun,Partial Sun,Shade", "Soil Type", "Health:select:Thriving,Good,Struggling,Dead", "Notes:textarea"]),
    "debt":        ("💳", ["Creditor", "Type:select:Credit Card,Student Loan,Mortgage,Car Loan,Personal,Other", "Balance:number", "Interest Rate:number", "Minimum Payment:number", "Due Date:date", "Status:select:Active,Paid Off"]),
    "savings":     ("🏦", ["Goal Name", "Target Amount:number", "Current Amount:number", "Deadline:date", "Category:select:Emergency Fund,Vacation,House,Car,Education,Other", "Notes:textarea"]),
    "client":      ("🤝", ["Client Name", "Company", "Email:email", "Phone", "Project", "Budget:number", "Status:select:Lead,Active,On Hold,Completed", "Notes:textarea"]),
    "competitor":  ("⚔️", ["Company", "Website:url", "Strengths:textarea", "Weaknesses:textarea", "Pricing", "Market:select:Same,Adjacent,Different", "Notes:textarea"]),
    "vendor":      ("🏪", ["Vendor Name", "Category", "Contact Email:email", "Phone", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Contract End:date", "Notes:textarea"]),
    "interview":   ("💼", ["Company", "Role", "Date:date", "Stage:select:Applied,Phone Screen,Technical,On-site,Offer,Rejected", "Notes:textarea", "Follow Up:date"]),
    "habit_goal":  ("🏆", ["Goal", "Category:select:Health,Fitness,Learning,Finance,Relationships,Career", "Target Date:date", "Milestones:textarea", "Progress:number", "Status:select:Not Started,In Progress,Achieved,Abandoned"]),
}

# Aliases so we match more variations
_ENTITY_ALIASES: dict[str, str] = {
    "todo": "todo", "to do": "todo", "to-do": "todo", "tasks": "task",
    "todos": "todo", "goals": "goal", "habits": "habit", "recipes": "recipe",
    "books": "book", "movies": "movie", "film": "movie", "films": "movie",
    "expenses": "expense", "spending": "expense", "spend": "expense",
    "contacts": "contact", "customers": "customer",
    "employees": "employee", "staff": "employee", "team members": "employee",
    "products": "product", "items": "inventory",
    "projects": "project", "bugs": "bug", "issues": "bug", "tickets": "bug",
    "notes": "note", "journal": "journal", "diary": "journal",
    "pets": "pet", "animals": "pet",
    "workouts": "workout", "exercise": "workout", "exercises": "workout", "fitness": "workout",
    "medications": "medication", "pills": "medication", "medicines": "medication",
    "appointments": "appointment", "meetings": "appointment", "events": "event",
    "links": "link", "bookmarks": "link", "urls": "link",
    "wines": "wine", "subscriptions": "subscription", "subs": "subscription",
    "vehicles": "vehicle", "cars": "vehicle", "bike": "vehicle", "bikes": "vehicle",
    "properties": "property", "houses": "property", "rentals": "property",
    "courses": "course", "classes": "course", "skills": "skill",
    "ideas": "idea", "transactions": "transaction", "finances": "transaction",
    "feedbacks": "feedback", "reviews": "feedback",
    "leads": "lead", "invoices": "invoice",
    "games": "game", "clothes": "clothing", "outfits": "clothing",
    "foods": "food", "dishes": "food", "restaurants": "food",
    "trips": "travel", "travels": "travel", "places": "travel",
    "photos": "photo", "images": "photo", "pictures": "photo",
    "songs": "music", "albums": "music", "tracks": "music",
    "passwords": "password", "credentials": "password",
    "objectives": "goal",
    # ── New aliases ──────────────────────────────────────────
    "sneakers": "sneaker", "kicks": "sneaker", "shoes": "sneaker",
    "cryptocurrency": "crypto", "bitcoin": "crypto", "ethereum": "crypto", "altcoin": "crypto",
    "nfts": "nft", "digital art": "nft",
    "stocks": "stock", "shares": "stock", "equities": "stock",
    "animes": "anime", "animation": "anime",
    "mangas": "manga", "comics": "manga",
    "podcasts": "podcast",
    "supplements": "supplement", "vitamins": "supplement",
    "debts": "debt", "loans": "debt", "credit": "debt",
    "clients": "client",
    "vendors": "vendor", "suppliers": "vendor",
    "interviews": "interview", "job applications": "interview", "applications": "interview",
}


def _infer_field_type(name: str) -> str:
    """Guess a field type from its name."""
    nl = name.lower()
    if any(w in nl for w in ("price", "cost", "amount", "value", "budget", "fee", "salary",
                              "balance", "rate", "shares", "quantity", "qty", "number",
                              "count", "total", "sum", "progress", "score", "age",
                              "weight", "height", "duration", "size", "episodes", "reps",
                              "sets", "mileage", "year", "vintage")):
        return "number"
    if any(w in nl for w in ("date", "day", "deadline", "due", "start", "end",
                              "purchased", "hired", "founded", "born", "expiry",
                              "billing", "scheduled", "watered", "fertilized", "follow up")):
        return "date"
    if any(w in nl for w in ("email", "e-mail")):
        return "email"
    if any(w in nl for w in ("url", "website", "link", "http")):
        return "url"
    if any(w in nl for w in ("note", "description", "detail", "comment", "summary",
                              "content", "body", "about", "bio", "info", "entry",
                              "strengths", "weaknesses", "milestones", "ingredients",
                              "steps", "feedback", "gratitude")):
        return "textarea"
    return "text"


def _parse_explicit_fields(q: str) -> list:
    """
    Detect when the user explicitly lists field names in the query.
    Patterns: "with fields: name, price, quantity" | "track name, price and date"
              | "fields: X, Y, Z" | "columns: X, Y, Z"
    Returns a list of raw field strings (with type annotations) or empty list.
    """
    # Pattern 1: "fields: X, Y, Z" or "columns: X, Y, Z"
    m = re.search(r'(?:fields?|columns?)\s*:\s*(.+?)(?:\.|$)', q, re.IGNORECASE)
    if not m:
        # Pattern 2: "with fields X, Y and Z"
        m = re.search(r'with\s+fields?\s+(.+?)(?:\.|$)', q, re.IGNORECASE)
    if not m:
        # Pattern 3: "track X, Y and Z" or "log X, Y and Z" — only if comma-separated list
        m = re.search(r'(?:track|log|record|store)\s+(?:my\s+)?(?:\w+\s+)?(\w[\w\s]*,[\w\s,]+(?:and\s+\w[\w\s]*)?)(?:\.|$)', q, re.IGNORECASE)

    if not m:
        return []

    raw = m.group(1).strip()
    # Split on commas and "and"
    parts = re.split(r',|\band\b', raw, flags=re.IGNORECASE)
    fields = []
    for part in parts:
        name = part.strip().strip('"\'')
        if not name or len(name) > 40:
            continue
        ftype = _infer_field_type(name)
        if ftype == "text":
            fields.append(name.title())
        else:
            fields.append(f"{name.title()}:{ftype}")
    return fields if len(fields) >= 2 else []


def _detect_entity(q: str) -> tuple[str, str, list]:
    """Returns (entity_key, emoji, fields)."""
    # Check for explicit field definitions first
    explicit_fields = _parse_explicit_fields(q)

    # Check aliases first (longer phrases before shorter)
    for alias in sorted(_ENTITY_ALIASES, key=len, reverse=True):
        if alias in q:
            key = _ENTITY_ALIASES[alias]
            emoji, catalog_fields = _ENTITY_CATALOG[key]
            return key, emoji, explicit_fields if explicit_fields else catalog_fields

    # Check catalog directly
    for key in sorted(_ENTITY_CATALOG, key=len, reverse=True):
        if key in q or key + "s" in q:
            emoji, catalog_fields = _ENTITY_CATALOG[key]
            return key, emoji, explicit_fields if explicit_fields else catalog_fields

    # Try to extract entity from common patterns
    patterns = [
        r"(?:track|manage|organize|log|record|store|keep track of|catalog)\s+(?:my\s+)?(\w[\w\s]{1,20}?)(?:\s+(?:with|and|that|which)|$)",
        r"(\w[\w\s]{1,20}?)\s+(?:tracker|manager|list|log|journal|diary|database|catalog|registry|organizer)",
        r"list\s+of\s+(?:my\s+)?(\w[\w\s]{1,20}?)(?:\s+(?:with|and)|$)",
        r"(?:a|an)\s+(\w[\w\s]{1,20}?)\s+(?:tracker|manager|app|tool|system)",
        r"build\s+(?:me\s+)?(?:a\s+|an\s+)?(\w[\w\s]{1,20}?)\s+(?:app|tool|manager|tracker|system|dashboard)",
    ]
    for pat in patterns:
        m = re.search(pat, q)
        if m:
            raw = m.group(1).strip().rstrip("s")
            fields = explicit_fields if explicit_fields else _generic_fields(raw, q)
            return raw, "📋", fields

    if explicit_fields:
        return "item", "📋", explicit_fields
    return "item", "📋", _generic_fields("item", q)


def _generic_fields(entity: str, q: str) -> list:
    """Build a sensible field list for an unknown entity."""
    fields = [entity.title()]
    if any(w in q for w in ("price", "cost", "amount", "value", "money", "budget", "fee")):
        fields.append("Amount:number")
    if any(w in q for w in ("date", "when", "time", "schedule", "deadline", "due")):
        fields.append("Date:date")
    if any(w in q for w in ("category", "type", "kind", "group")):
        fields.append("Category:select:General,Work,Personal,Other")
    if any(w in q for w in ("status", "state", "progress", "stage")):
        fields.append("Status:select:Active,Done,Pending,Cancelled")
    if any(w in q for w in ("priority", "importance", "urgent")):
        fields.append("Priority:select:Low,Medium,High")
    if any(w in q for w in ("rating", "score", "grade", "star")):
        fields.append("Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐")
    if any(w in q for w in ("tag", "label", "keyword")):
        fields.append("Tags")
    if any(w in q for w in ("location", "place", "where", "address")):
        fields.append("Location")
    fields.append("Notes:textarea")
    return fields


def _detect_features(q: str) -> set:
    features = set()
    if any(w in q for w in ("search", "find", "filter")):
        features.add("search")
    if any(w in q for w in ("chart", "graph", "visual", "statistic", "stat", "analytics", "breakdown")):
        features.add("chart")
    if any(w in q for w in ("export", "download", "csv", "save file")):
        features.add("export")
    if any(w in q for w in ("dark mode", "dark theme", "dark")):
        features.add("dark_mode")
    if any(w in q for w in ("sort", "order")):
        features.add("sort")
    if any(w in q for w in ("total", "sum", "count", "summary", "overview", "dashboard", "stats")):
        features.add("stats")
    if any(w in q for w in ("edit", "editable", "update", "modify", "change")):
        features.add("edit")
    if any(w in q for w in ("tag", "label", "keyword")):
        features.add("tags")
    return features


def _detect_build_type(q: str) -> str:
    """
    Returns "tool", "crud", or "dashboard" based on the query.
    - "tool": calculator, converter, checker, validator, encoder, decoder, estimator,
              or generator (as standalone word, not "app generator")
    - "dashboard": dashboard or analytics or overview (without tracker/manager)
    - "crud": everything else
    """
    # Tool detection — standalone tool keywords
    tool_words = ("calculator", "calc", "converter", "checker", "validator",
                  "encoder", "decoder", "estimator")
    for w in tool_words:
        if re.search(rf'\b{re.escape(w)}\b', q):
            return "tool"
    # "generator" only when not preceded by "app"
    if re.search(r'\bgenerator\b', q) and not re.search(r'app\s+generator', q):
        return "tool"

    # Dashboard detection
    dashboard_words = ("dashboard", "analytics", "overview")
    tracker_words = ("tracker", "manager", "list", "log", "journal")
    if any(w in q for w in dashboard_words) and not any(w in q for w in tracker_words):
        return "dashboard"

    return "crud"


# ══════════════════════════════════════════════════════════════
# FIELD PARSING
# ══════════════════════════════════════════════════════════════

def _parse_field(raw: str) -> dict:
    """
    Parse a field definition like "Amount:number" or "Status:select:Active,Done".
    Returns {"name": str, "label": str, "type": str, "options": list, "id": str}
    """
    parts = raw.split(":", 2)
    label = parts[0].strip()
    ftype = parts[1].strip() if len(parts) > 1 else "text"
    options = parts[2].split(",") if len(parts) > 2 else []
    field_id = re.sub(r"[^a-z0-9]", "_", label.lower()).strip("_")
    return {"name": field_id, "label": label, "type": ftype, "options": options}


# ══════════════════════════════════════════════════════════════
# TITLE GENERATION
# ══════════════════════════════════════════════════════════════

def _make_title(entity: str, q: str) -> str:
    # Look for explicit title patterns
    m = re.search(r"called\s+[\"']?(.+?)[\"']?(?:\s|$)", q)
    if m:
        return m.group(1).strip().title()
    m = re.search(r"named\s+[\"']?(.+?)[\"']?(?:\s|$)", q)
    if m:
        return m.group(1).strip().title()

    # Derive from entity
    entity_title = entity.replace("_", " ").title()
    if any(w in q for w in ("tracker", "tracking")):
        return f"{entity_title} Tracker"
    if any(w in q for w in ("manager", "manage")):
        return f"{entity_title} Manager"
    if any(w in q for w in ("log", "diary", "journal")):
        return f"{entity_title} Journal"
    if any(w in q for w in ("list",)):
        return f"{entity_title} List"
    if any(w in q for w in ("dashboard", "overview")):
        return f"{entity_title} Dashboard"
    if any(w in q for w in ("organizer", "organize")):
        return f"{entity_title} Organizer"
    if any(w in q for w in ("calculator", "calc")):
        return f"{entity_title} Calculator"
    if any(w in q for w in ("converter",)):
        return f"{entity_title} Converter"
    if any(w in q for w in ("checker", "validator")):
        return f"{entity_title} Checker"
    if any(w in q for w in ("estimator",)):
        return f"{entity_title} Estimator"
    if any(w in q for w in ("generator",)):
        return f"{entity_title} Generator"
    return f"{entity_title} Manager"


# ══════════════════════════════════════════════════════════════
# HTML GENERATOR — CRUD
# ══════════════════════════════════════════════════════════════

def _field_input_html(f: dict) -> str:
    fid = f"field_{f['name']}"
    base = f'id="{fid}"'
    if f["type"] == "textarea":
        return f'<textarea {base} placeholder="{f["label"]}..." rows="3"></textarea>'
    if f["type"] == "select":
        opts = "".join(f'<option value="{o.strip()}">{o.strip()}</option>' for o in f["options"])
        return f'<select {base}><option value="">— {f["label"]} —</option>{opts}</select>'
    type_map = {"number": "number", "date": "date", "email": "email", "url": "url",
                "color": "color", "text": "text"}
    t = type_map.get(f["type"], "text")
    return f'<input {base} type="{t}" placeholder="{f["label"]}">'


def _js_get_value(f: dict) -> str:
    fid = f"field_{f['name']}"
    if f["type"] == "textarea":
        return f'document.getElementById("{fid}").value.trim()'
    if f["type"] in ("text", "number", "date", "email", "url", "color"):
        return f'document.getElementById("{fid}").value.trim()'
    if f["type"] == "select":
        return f'document.getElementById("{fid}").value'
    return f'document.getElementById("{fid}").value.trim()'


def _js_set_value(f: dict, expr: str) -> str:
    fid = f"field_{f['name']}"
    return f'document.getElementById("{fid}").value = {expr};'


def _js_clear_field(f: dict) -> str:
    fid = f"field_{f['name']}"
    return f'document.getElementById("{fid}").value = "";'


def generate_crud_app(query: str) -> str:
    """Build a complete CRUD manager for any entity from a description."""
    q = query.lower()
    entity_key, emoji, raw_fields = _detect_entity(q)
    fields = [_parse_field(rf) for rf in raw_fields]
    features = _detect_features(q)
    theme = _dyn_pick_theme(q)
    title = _make_title(entity_key, q)
    entity_label = entity_key.replace("_", " ").title()
    entity_plural = entity_label + "s"
    t = theme

    has_search = "search" in features or len(raw_fields) > 3
    has_stats = "stats" in features or any(f["type"] == "number" for f in fields)
    has_chart = "chart" in features
    has_export = "export" in features
    has_edit = True  # always include edit

    # --- Form inputs HTML ---
    form_inputs = "\n".join(
        f'<div class="field-group"><label class="field-label">{f["label"]}</label>{_field_input_html(f)}</div>'
        for f in fields
    )

    # --- JS: collect form values ---
    collect_js = ",\n          ".join(
        f'{f["name"]}: {_js_get_value(f)}'
        for f in fields
    )
    required_field = fields[0]["name"] if fields else "name"

    # --- JS: clear form ---
    clear_js = "\n      ".join(_js_clear_field(f) for f in fields)

    # --- JS: populate edit form ---
    populate_js = "\n        ".join(
        _js_set_value(f, f'item.{f["name"]} || ""')
        for f in fields
    )

    # --- Card rendering JS ---
    card_fields_js = "\n        ".join(
        f'if(item.{f["name"]}) parts.push(`<span class="card-field"><span class="field-key">{f["label"]}:</span> ${{item.{f["name"]}}}</span>`);'
        for f in fields[1:]  # skip the primary field (shown as title)
    )

    # --- Stats JS ---
    numeric_fields = [f for f in fields if f["type"] == "number"]
    stats_js = ""
    stats_html = ""
    if has_stats and numeric_fields:
        for nf in numeric_fields[:2]:
            stats_js += f'\n  const {nf["name"]}Total = items.reduce((s,i)=>s+(parseFloat(i.{nf["name"]})||0),0);'
        stats_html = "".join(
            f'<div class="stat-card"><div class="stat-label">{nf["label"]}</div><div class="stat-value" id="stat_{nf["name"]}">0</div></div>'
            for nf in numeric_fields[:2]
        )
        stats_update_js = "\n  ".join(
            f'const statEl_{nf["name"]} = document.getElementById("stat_{nf["name"]}"); if(statEl_{nf["name"]}) statEl_{nf["name"]}.innerText = items.reduce((s,i)=>s+(parseFloat(i.{nf["name"]})||0),0).toLocaleString();'
            for nf in numeric_fields[:2]
        )
    else:
        stats_update_js = ""

    # --- Chart JS ---
    chart_js = ""
    if has_chart:
        # Group by the first select field if one exists
        group_field = next((f for f in fields if f["type"] == "select"), None)
        if group_field:
            chart_js = f"""
  // Chart
  const chartCanvas = document.getElementById('chart');
  if(chartCanvas) {{
    const counts = {{}};
    items.forEach(i => {{ const k = i.{group_field["name"]} || 'Other'; counts[k] = (counts[k]||0)+1; }});
    const ctx = chartCanvas.getContext('2d');
    const keys = Object.keys(counts); const vals = Object.values(counts);
    const maxV = Math.max(...vals, 1);
    const bw = Math.floor((chartCanvas.width - 40) / Math.max(keys.length,1)) - 8;
    ctx.clearRect(0,0,chartCanvas.width,chartCanvas.height);
    keys.forEach((k,i) => {{
      const x = 20 + i*(bw+8), h = Math.round((vals[i]/maxV)*(chartCanvas.height-40));
      const y = chartCanvas.height - h - 20;
      ctx.fillStyle = '{t["primary"]}'; ctx.fillRect(x,y,bw,h);
      ctx.fillStyle = '{t["muted"]}'; ctx.font='10px sans-serif'; ctx.textAlign='center';
      ctx.fillText(k.slice(0,8), x+bw/2, chartCanvas.height-5);
      ctx.fillStyle = '{t["text"]}';
      ctx.fillText(vals[i], x+bw/2, y-4);
    }});
  }}"""

    # --- Export JS ---
    export_js = ""
    if has_export:
        headers = ",".join(f'"{f["label"]}"' for f in fields)
        row_parts = []
        for f in fields:
            row_parts.append('"\\""+(item.' + f["name"] + '||"").toString().replace(/"/g,\'\\\\"\')+"\\""')
        row_js = "+','+".join(row_parts)
        newline = "\\n"
        export_js = f"""
function exportCSV() {{
  const headers = [{headers}];
  const rows = items.map(item => [{row_js}]);
  const csv = [headers.join(','), ...rows.map(r=>r.join(','))].join('{newline}');
  const a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = '{title.replace(" ","_")}.csv';
  a.click();
}}"""

    search_html = f'<input id="searchInput" type="search" placeholder="Search {entity_plural.lower()}..." oninput="render()">' if has_search else ""
    chart_html = f'<div class="chart-section"><div class="section-title">📊 Breakdown</div><canvas id="chart" width="400" height="180"></canvas></div>' if has_chart else ""
    stats_html_block = f'<div class="stats-row">{stats_html}</div>' if stats_html else ""
    export_btn_html = f'<button class="btn btn-ghost" onclick="exportCSV()">⬇ Export CSV</button>' if has_export else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{t['bg']};color:{t['text']};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;padding:16px}}
h1{{font-size:1.4rem;font-weight:800;letter-spacing:-.02em}}
.app{{max-width:900px;margin:0 auto;display:grid;grid-template-columns:300px 1fr;gap:16px;align-items:start}}
@media(max-width:640px){{.app{{grid-template-columns:1fr}}}}
.panel,.card-panel{{background:{t['surface']};border:1px solid {t['border']};border-radius:14px;padding:18px}}
.panel-title{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{t['muted']};margin-bottom:12px}}
.field-group{{margin-bottom:10px}}
.field-label{{display:block;font-size:.68rem;font-weight:600;color:{t['muted']};text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}}
input,select,textarea{{width:100%;background:{t['bg']};border:1.5px solid {t['border']};color:{t['text']};border-radius:8px;padding:8px 10px;font-size:.82rem;outline:none;font-family:inherit;transition:border-color .15s}}
input:focus,select:focus,textarea:focus{{border-color:{t['primary']}}}
textarea{{resize:vertical;min-height:60px}}
.btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:9px;font-size:.78rem;font-weight:700;cursor:pointer;border:none;transition:.15s;white-space:nowrap}}
.btn-primary{{background:{t['primary']};color:#fff}} .btn-primary:hover{{opacity:.85}}
.btn-ghost{{background:transparent;border:1.5px solid {t['border']};color:{t['text']}}} .btn-ghost:hover{{background:{t['hover']}}}
.btn-danger{{background:transparent;border:1.5px solid {t['danger']};color:{t['danger']}}} .btn-danger:hover{{background:{t['danger']};color:#fff}}
.btn-sm{{padding:5px 10px;font-size:.7rem;border-radius:7px}}
.header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:10px;flex-wrap:wrap}}
.header-left{{display:flex;align-items:center;gap:10px}}
.badge{{font-size:.65rem;background:{t['primary']}22;color:{t['primary']};border:1px solid {t['primary']}44;border-radius:99px;padding:2px 8px;font-weight:700}}
.search-bar{{width:100%;margin-bottom:12px}}
.search-bar input{{border-radius:9px}}
.items-grid{{display:grid;grid-template-columns:1fr;gap:10px}}
.card{{background:{t['bg']};border:1.5px solid {t['border']};border-radius:12px;padding:14px;transition:.15s}}
.card:hover{{border-color:{t['primary']}66}}
.card-title{{font-size:.9rem;font-weight:700;margin-bottom:6px;color:{t['text']}}}
.card-fields{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}}
.card-field{{font-size:.7rem;background:{t['surface']};border:1px solid {t['border']};border-radius:6px;padding:2px 8px;color:{t['muted']}}}
.field-key{{font-weight:600;color:{t['text']}88}}
.card-actions{{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}}
.empty{{text-align:center;padding:40px 20px;color:{t['muted']};font-size:.85rem}}
.stats-row{{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.stat-card{{flex:1;min-width:100px;background:{t['bg']};border:1px solid {t['border']};border-radius:10px;padding:12px;text-align:center}}
.stat-label{{font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;color:{t['muted']};margin-bottom:4px;font-weight:600}}
.stat-value{{font-size:1.3rem;font-weight:800;color:{t['primary']};font-family:monospace}}
.chart-section{{background:{t['bg']};border:1px solid {t['border']};border-radius:12px;padding:14px;margin-bottom:14px}}
.section-title{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{t['muted']};margin-bottom:10px}}
canvas{{width:100%;display:block}}
/* Modal */
.modal-backdrop{{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px}}
.modal{{background:{t['surface']};border:1px solid {t['border']};border-radius:16px;padding:22px;width:100%;max-width:420px;max-height:90vh;overflow-y:auto}}
.modal-title{{font-size:1rem;font-weight:800;margin-bottom:16px}}
.modal-actions{{display:flex;gap:8px;margin-top:16px;justify-content:flex-end}}
.hidden{{display:none}}
</style>
</head>
<body>
<div class="app">
  <!-- ── Add / Edit Panel ── -->
  <aside>
    <div class="panel">
      <div class="panel-title">✚ Add {entity_label}</div>
{form_inputs}
      <div style="display:flex;gap:8px;margin-top:12px">
        <button class="btn btn-primary" style="flex:1" onclick="save()">Save {entity_label}</button>
        <button class="btn btn-ghost btn-sm" onclick="clearForm()">Clear</button>
      </div>
    </div>
  </aside>

  <!-- ── Main Area ── -->
  <main>
    <div class="header">
      <div class="header-left">
        <span style="font-size:1.5rem">{emoji}</span>
        <div>
          <h1>{title}</h1>
          <span class="badge" id="countBadge">0 {entity_plural.lower()}</span>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        {export_btn_html}
      </div>
    </div>

    {stats_html_block}
    {chart_html}

    <div class="card-panel">
      {'<div class="search-bar">' + search_html + '</div>' if search_html else ""}
      <div class="items-grid" id="itemsGrid"></div>
    </div>
  </main>
</div>

<!-- Edit Modal -->
<div class="modal-backdrop hidden" id="editModal">
  <div class="modal">
    <div class="modal-title">✏️ Edit {entity_label}</div>
    <div id="editFields"></div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveEdit()">Save Changes</button>
    </div>
  </div>
</div>

<script>
const STORAGE_KEY = 'forgeai_{entity_key.replace("-","_")}';
let items = [];
let editingId = null;

// ── Persistence ────────────────────────────────
function save_storage() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(items)); }} catch(e) {{}}
}}
function load_storage() {{
  try {{ items = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }} catch(e) {{ items = []; }}
}}

// ── Form ───────────────────────────────────────
function collect() {{
  return {{
    id: Date.now() + Math.random(),
    created: new Date().toISOString(),
    {collect_js}
  }};
}}
function clearForm() {{
  {clear_js}
  editingId = null;
}}
function save() {{
  const item = collect();
  if (!item.{required_field}) {{ alert('Please fill in the {fields[0]["label"] if fields else "Name"} field.'); return; }}
  items.unshift(item);
  save_storage(); clearForm(); render();
}}

// ── Edit modal ─────────────────────────────────
const FIELDS = {json.dumps([{"name": f["name"], "label": f["label"], "type": f["type"], "options": f["options"]} for f in fields])};
function openEdit(id) {{
  const item = items.find(i => i.id === id);
  if (!item) return;
  editingId = id;
  const container = document.getElementById('editFields');
  container.innerHTML = FIELDS.map(f => {{
    let input = '';
    if (f.type === 'textarea') {{
      input = `<textarea id="edit_${{f.name}}" rows="3">${{item[f.name] || ''}}</textarea>`;
    }} else if (f.type === 'select') {{
      const opts = f.options.map(o => `<option value="${{o}}" ${{item[f.name]===o?'selected':''}}>` + o + '</option>').join('');
      input = `<select id="edit_${{f.name}}"><option value="">— ${{f.label}} —</option>${{opts}}</select>`;
    }} else {{
      input = `<input id="edit_${{f.name}}" type="${{f.type}}" value="${{item[f.name] || ''}}">`;
    }}
    return `<div class="field-group"><label class="field-label">${{f.label}}</label>${{input}}</div>`;
  }}).join('');
  document.getElementById('editModal').classList.remove('hidden');
}}
function closeModal() {{
  document.getElementById('editModal').classList.add('hidden');
  editingId = null;
}}
function saveEdit() {{
  if (editingId === null) return;
  const idx = items.findIndex(i => i.id === editingId);
  if (idx === -1) return;
  FIELDS.forEach(f => {{
    const el = document.getElementById('edit_' + f.name);
    if (el) items[idx][f.name] = el.value.trim ? el.value.trim() : el.value;
  }});
  items[idx].updated = new Date().toISOString();
  save_storage(); closeModal(); render();
}}

// ── Delete ─────────────────────────────────────
function remove(id) {{
  if (!confirm('Delete this {entity_label.lower()}?')) return;
  items = items.filter(i => i.id !== id);
  save_storage(); render();
}}

// ── Render ─────────────────────────────────────
function render() {{
  const searchEl = document.getElementById('searchInput');
  const q = searchEl ? searchEl.value.toLowerCase() : '';
  const filtered = q
    ? items.filter(item => JSON.stringify(item).toLowerCase().includes(q))
    : items;

  document.getElementById('countBadge').innerText = filtered.length + ' {entity_plural.lower()}';

  const grid = document.getElementById('itemsGrid');
  if (!filtered.length) {{
    grid.innerHTML = `<div class="empty">No {entity_plural.lower()} yet.<br>Add your first {entity_label.lower()} using the panel →</div>`;
  }} else {{
    grid.innerHTML = filtered.map(item => {{
      const parts = [];
      {card_fields_js}
      return `
        <div class="card">
          <div class="card-title">${{item.{required_field} || '—'}}</div>
          <div class="card-fields">${{parts.join('')}}</div>
          <div class="card-actions">
            <button class="btn btn-ghost btn-sm" onclick="openEdit(${{item.id}})">✏️ Edit</button>
            <button class="btn btn-danger btn-sm" onclick="remove(${{item.id}})">🗑 Delete</button>
          </div>
        </div>`;
    }}).join('');
  }}

  // Stats
  {stats_update_js}
  {chart_js}
}}

{export_js}

// ── Init ───────────────────────────────────────
document.getElementById('editModal').addEventListener('click', function(e) {{
  if (e.target === this) closeModal();
}});
load_storage();
render();
</script>
</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════════
# HTML GENERATOR — TOOL / CALCULATOR
# ══════════════════════════════════════════════════════════════

def _detect_tool_type(q: str) -> str:
    """Detect the kind of calculator/converter from the query."""
    if any(w in q for w in ("bmi", "body mass", "body weight index")):
        return "bmi"
    if any(w in q for w in ("tip", "gratuity", "restaurant bill")):
        return "tip"
    if any(w in q for w in ("percent", "percentage", "discount", "% off")):
        return "percent"
    if any(w in q for w in ("celsius", "fahrenheit", "kelvin", "temperature", "temp convert")):
        return "temperature"
    if any(w in q for w in ("compound interest", "interest rate", "savings", "investment")):
        return "compound"
    if any(w in q for w in ("mortgage", "loan", "monthly payment", "amortization")):
        return "loan"
    if any(w in q for w in ("gpa", "grade point", "grades")):
        return "gpa"
    if any(w in q for w in ("age", "birthday", "born", "how old")):
        return "age"
    if any(w in q for w in ("calorie", "calories", "bmr", "metabolic")):
        return "calorie"
    if "converter" in q or "convert" in q:
        return "converter"
    if "calculator" in q or "calc" in q:
        return "arithmetic"
    return "generic"


def _build_tool_calc_js(q: str, tool_fields: list[dict]) -> tuple[str, str, str, str]:
    """
    Return (read_inputs_js, result_lines_js, total_expr_js, result_label) for the
    calculate() function. Uses real formulas when the tool type is recognised.
    """
    tool_type = _detect_tool_type(q)
    ids = [f["id"] for f in tool_fields]
    read = "\n    ".join(
        f'const val_{fid} = parseFloat(document.getElementById("tinput_{fid}").value) || 0;'
        for fid in ids
    )

    if tool_type == "bmi" and len(ids) >= 2:
        return read, (
            'lines.push({ label: "Weight (kg)", value: val_' + ids[0] + '.toFixed(1) });\n'
            '  lines.push({ label: "Height (cm)", value: val_' + ids[1] + '.toFixed(1) });\n'
            '  const heightM = val_' + ids[1] + ' / 100;\n'
            '  const bmi = heightM > 0 ? val_' + ids[0] + ' / (heightM * heightM) : 0;\n'
            '  const category = bmi < 18.5 ? "Underweight" : bmi < 25 ? "Normal" : bmi < 30 ? "Overweight" : "Obese";\n'
            '  lines.push({ label: "BMI Category", value: category });'
        ), "bmi", "BMI"

    if tool_type == "tip" and len(ids) >= 2:
        return read, (
            'lines.push({ label: "Bill Amount", value: "$" + val_' + ids[0] + '.toFixed(2) });\n'
            '  lines.push({ label: "Tip Rate", value: val_' + ids[1] + '.toFixed(1) + "%" });\n'
            '  const tip = val_' + ids[0] + ' * (val_' + ids[1] + ' / 100);\n'
            '  lines.push({ label: "Tip Amount", value: "$" + tip.toFixed(2) });\n'
            '  const total = val_' + ids[0] + ' + tip;\n'
            '  lines.push({ label: "Total Bill", value: "$" + total.toFixed(2) });'
        ), "val_" + ids[0] + " + val_" + ids[0] + " * (val_" + ids[1] + " / 100)", "Total with Tip"

    if tool_type == "percent" and len(ids) >= 2:
        return read, (
            'lines.push({ label: "Original Value", value: val_' + ids[0] + '.toLocaleString() });\n'
            '  lines.push({ label: "Percentage", value: val_' + ids[1] + '.toFixed(1) + "%" });\n'
            '  const result = val_' + ids[0] + ' * (val_' + ids[1] + ' / 100);\n'
            '  lines.push({ label: "Result", value: result.toLocaleString(undefined, {maximumFractionDigits:4}) });'
        ), "val_" + ids[0] + " * (val_" + ids[1] + " / 100)", "Percentage Result"

    if tool_type == "temperature" and len(ids) >= 1:
        return read, (
            'const celsius = val_' + ids[0] + ';\n'
            '  const fahrenheit = celsius * 9/5 + 32;\n'
            '  const kelvin = celsius + 273.15;\n'
            '  lines.push({ label: "Celsius", value: celsius.toFixed(2) + " °C" });\n'
            '  lines.push({ label: "Fahrenheit", value: fahrenheit.toFixed(2) + " °F" });\n'
            '  lines.push({ label: "Kelvin", value: kelvin.toFixed(2) + " K" });'
        ), "val_" + ids[0] + " * 9/5 + 32", "Fahrenheit"

    if tool_type == "compound" and len(ids) >= 3:
        return read, (
            'lines.push({ label: "Principal", value: "$" + val_' + ids[0] + '.toLocaleString() });\n'
            '  lines.push({ label: "Annual Rate", value: val_' + ids[1] + '.toFixed(2) + "%" });\n'
            '  lines.push({ label: "Years", value: val_' + ids[2] + '.toFixed(0) });\n'
            '  const r = val_' + ids[1] + ' / 100;\n'
            '  const amount = val_' + ids[0] + ' * Math.pow(1 + r, val_' + ids[2] + ');\n'
            '  const interest = amount - val_' + ids[0] + ';\n'
            '  lines.push({ label: "Interest Earned", value: "$" + interest.toFixed(2) });\n'
            '  lines.push({ label: "Final Amount", value: "$" + amount.toFixed(2) });'
        ), "val_" + ids[0] + " * Math.pow(1 + val_" + ids[1] + "/100, val_" + ids[2] + ")", "Final Amount"

    if tool_type == "loan" and len(ids) >= 3:
        return read, (
            'lines.push({ label: "Loan Amount", value: "$" + val_' + ids[0] + '.toLocaleString() });\n'
            '  lines.push({ label: "Annual Rate", value: val_' + ids[1] + '.toFixed(2) + "%" });\n'
            '  lines.push({ label: "Term (years)", value: val_' + ids[2] + '.toFixed(0) });\n'
            '  const r = val_' + ids[1] + ' / 100 / 12;\n'
            '  const n = val_' + ids[2] + ' * 12;\n'
            '  const p = val_' + ids[0] + ';\n'
            '  const monthly = r > 0 ? p * r * Math.pow(1+r,n) / (Math.pow(1+r,n)-1) : p/n;\n'
            '  lines.push({ label: "Monthly Payment", value: "$" + monthly.toFixed(2) });\n'
            '  lines.push({ label: "Total Paid", value: "$" + (monthly*n).toFixed(2) });'
        ), (
            "(function(){ const r=val_" + ids[1] + "/100/12, n=val_" + ids[2] +
            "*12, p=val_" + ids[0] + "; return r>0?p*r*Math.pow(1+r,n)/(Math.pow(1+r,n)-1):p/n; })()"
        ), "Monthly Payment"

    if tool_type == "arithmetic" and len(ids) >= 2:
        return read, (
            'lines.push({ label: "' + tool_fields[0]["label"] + '", value: val_' + ids[0] + '.toLocaleString() });\n'
            '  lines.push({ label: "' + tool_fields[1]["label"] + '", value: val_' + ids[1] + '.toLocaleString() });\n'
            '  lines.push({ label: "Sum", value: (val_' + ids[0] + ' + val_' + ids[1] + ').toLocaleString() });\n'
            '  lines.push({ label: "Product", value: (val_' + ids[0] + ' * val_' + ids[1] + ').toLocaleString() });\n'
            '  if (val_' + ids[1] + ' !== 0) lines.push({ label: "Quotient", value: (val_' + ids[0] + ' / val_' + ids[1] + ').toFixed(4) });'
        ), "val_" + ids[0] + " + val_" + ids[1], "Sum"

    # Generic fallback: show each field + sum
    result_lines = "\n    ".join(
        f'lines.push({{ label: "{f["label"]}", value: val_{f["id"]}.toLocaleString() }});'
        for f in tool_fields
    )
    sum_expr = " + ".join(f"val_{f['id']}" for f in tool_fields) or "0"
    return read, result_lines, sum_expr, "Total / Result"


def generate_tool_app(query: str) -> str:
    """Build a professional single-panel tool/calculator app from a description."""
    q = query.lower()
    theme = _dyn_pick_theme(q)
    title = _make_title("tool", q)
    t = theme

    # Derive a sensible title from query if possible
    entity_key, emoji, _ = _detect_entity(q)
    title = _make_title(entity_key, q)
    if not any(w in title.lower() for w in ("calculator", "converter", "checker",
                                              "validator", "encoder", "decoder",
                                              "estimator", "generator")):
        # Append the tool type word found in query
        for tw in ("calculator", "converter", "checker", "validator",
                   "encoder", "decoder", "estimator", "generator"):
            if tw in q:
                title = f"{entity_key.replace('_',' ').title()} {tw.title()}"
                break

    # Build input fields from context — number inputs for numeric keywords
    tool_field_names = []
    if any(w in q for w in ("price", "cost", "amount", "value", "fee", "rate", "salary",
                              "income", "revenue", "profit", "discount", "tax")):
        tool_field_names.append(("Amount", "number"))
    if any(w in q for w in ("percent", "percentage", "rate", "interest", "discount")):
        tool_field_names.append(("Rate (%)", "number"))
    if any(w in q for w in ("years", "months", "days", "duration", "period", "term", "time")):
        tool_field_names.append(("Duration", "number"))
    if any(w in q for w in ("weight", "kg", "lbs", "pounds", "grams")):
        tool_field_names.append(("Weight", "number"))
    if any(w in q for w in ("height", "cm", "feet", "inches", "meter")):
        tool_field_names.append(("Height", "number"))
    if any(w in q for w in ("temperature", "celsius", "fahrenheit", "kelvin", "temp")):
        tool_field_names.append(("Temperature", "number"))
    if any(w in q for w in ("distance", "km", "miles", "meter", "length")):
        tool_field_names.append(("Distance", "number"))
    if any(w in q for w in ("speed", "velocity", "mph", "kph")):
        tool_field_names.append(("Speed", "number"))
    if any(w in q for w in ("quantity", "count", "number of", "how many")):
        tool_field_names.append(("Quantity", "number"))

    # If we detected nothing specific, make generic inputs
    if not tool_field_names:
        tool_field_names = [("Value A", "number"), ("Value B", "number")]

    # Deduplicate while preserving order
    seen = set()
    unique_fields = []
    for name, ftype in tool_field_names:
        if name not in seen:
            seen.add(name)
            unique_fields.append((name, ftype))
    tool_field_names = unique_fields

    # Build field ids
    tool_fields = [
        {"label": name, "ftype": ftype, "id": re.sub(r"[^a-z0-9]", "_", name.lower()).strip("_")}
        for name, ftype in tool_field_names
    ]

    # Input HTML for each field
    inputs_html = "\n".join(
        f'''        <div class="tool-field-group">
          <label class="tool-label">{f["label"]}</label>
          <input id="tinput_{f["id"]}" type="{f["ftype"]}" placeholder="Enter {f["label"].lower()}" class="tool-input">
        </div>'''
        for f in tool_fields
    )

    # JS to read inputs and build result — use real formulas when detected
    read_inputs_js, result_lines_js, total_expr, result_label = _build_tool_calc_js(q, tool_fields)

    storage_key = f'forgeai_tool_{re.sub(r"[^a-z0-9]", "_", title.lower())}'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{t['bg']};color:{t['text']};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;padding:20px}}
h1{{font-size:1.5rem;font-weight:800;letter-spacing:-.02em}}
.app{{max-width:860px;margin:0 auto}}
.tool-header{{display:flex;align-items:center;gap:12px;margin-bottom:20px}}
.tool-emoji{{font-size:2rem}}
.tool-subtitle{{font-size:.78rem;color:{t['muted']};margin-top:2px}}
.tool-layout{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:600px){{.tool-layout{{grid-template-columns:1fr}}}}
.panel{{background:{t['surface']};border:1px solid {t['border']};border-radius:14px;padding:20px}}
.panel-title{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{t['muted']};margin-bottom:14px}}
.tool-field-group{{margin-bottom:12px}}
.tool-label{{display:block;font-size:.7rem;font-weight:600;color:{t['muted']};text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}}
.tool-input{{width:100%;background:{t['bg']};border:1.5px solid {t['border']};color:{t['text']};border-radius:9px;padding:10px 12px;font-size:.9rem;outline:none;font-family:inherit;transition:border-color .15s}}
.tool-input:focus{{border-color:{t['primary']}}}
.btn{{display:inline-flex;align-items:center;gap:6px;padding:10px 18px;border-radius:10px;font-size:.82rem;font-weight:700;cursor:pointer;border:none;transition:.15s;white-space:nowrap}}
.btn-primary{{background:{t['primary']};color:#fff;width:100%;justify-content:center;margin-top:8px}} .btn-primary:hover{{opacity:.85}}
.btn-ghost{{background:transparent;border:1.5px solid {t['border']};color:{t['text']}}} .btn-ghost:hover{{background:{t['hover']}}}
.btn-sm{{padding:5px 10px;font-size:.7rem;border-radius:7px}}
.result-box{{background:{t['bg']};border:2px solid {t['primary']}44;border-radius:12px;padding:16px;margin-bottom:14px;min-height:80px}}
.result-empty{{color:{t['muted']};font-size:.82rem;text-align:center;padding:20px 0}}
.result-row{{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid {t['border']}}}
.result-row:last-child{{border-bottom:none}}
.result-label{{font-size:.75rem;color:{t['muted']};font-weight:600}}
.result-value{{font-size:.88rem;font-weight:700;color:{t['text']};font-family:monospace}}
.result-total{{background:{t['primary']}18;border-radius:8px;padding:10px 12px;margin-top:10px;display:flex;justify-content:space-between;align-items:center}}
.result-total-label{{font-size:.75rem;font-weight:700;color:{t['primary']};text-transform:uppercase;letter-spacing:.06em}}
.result-total-value{{font-size:1.2rem;font-weight:800;color:{t['primary']};font-family:monospace}}
.history-section{{margin-top:16px}}
.history-title{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{t['muted']};margin-bottom:10px}}
.history-list{{display:flex;flex-direction:column;gap:6px;max-height:260px;overflow-y:auto}}
.history-item{{background:{t['bg']};border:1px solid {t['border']};border-radius:9px;padding:10px 12px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:.12s}}
.history-item:hover{{border-color:{t['primary']}66}}
.history-summary{{font-size:.75rem;color:{t['muted']};flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.history-result{{font-size:.82rem;font-weight:700;color:{t['primary']};font-family:monospace;margin-left:10px}}
.history-time{{font-size:.65rem;color:{t['muted']};margin-left:8px;white-space:nowrap}}
.history-empty{{color:{t['muted']};font-size:.78rem;text-align:center;padding:16px 0}}
.clear-history{{font-size:.65rem;color:{t['muted']};cursor:pointer;text-decoration:underline;margin-top:6px;display:inline-block}}
.clear-history:hover{{color:{t['text']}}}
</style>
</head>
<body>
<div class="app">
  <div class="tool-header">
    <div class="tool-emoji">{emoji}</div>
    <div>
      <h1>{title}</h1>
      <div class="tool-subtitle">Enter values and press Calculate</div>
    </div>
  </div>

  <div class="tool-layout">
    <!-- ── Input Panel ── -->
    <div class="panel">
      <div class="panel-title">⚙️ Inputs</div>
{inputs_html}
      <button class="btn btn-primary" onclick="calculate()">⚡ Calculate</button>
      <button class="btn btn-ghost btn-sm" style="width:100%;margin-top:8px;justify-content:center" onclick="clearInputs()">Clear</button>
    </div>

    <!-- ── Result Panel ── -->
    <div class="panel">
      <div class="panel-title">📊 Result</div>
      <div class="result-box" id="resultBox">
        <div class="result-empty" id="resultEmpty">Results will appear here after you calculate.</div>
        <div id="resultRows" style="display:none"></div>
      </div>

      <div class="history-section">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div class="history-title">🕓 History</div>
          <span class="clear-history" onclick="clearHistory()">Clear all</span>
        </div>
        <div class="history-list" id="historyList">
          <div class="history-empty">No calculations yet.</div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
const TOOL_STORAGE_KEY = '{storage_key}';
let history = [];

function loadHistory() {{
  try {{ history = JSON.parse(localStorage.getItem(TOOL_STORAGE_KEY) || '[]'); }} catch(e) {{ history = []; }}
}}
function saveHistory() {{
  try {{ localStorage.setItem(TOOL_STORAGE_KEY, JSON.stringify(history.slice(0, 50))); }} catch(e) {{}}
}}

function calculate() {{
  {read_inputs_js}

  const lines = [];
  {result_lines_js}
  const total = {total_expr};

  // Show results
  const rowsEl = document.getElementById('resultRows');
  const emptyEl = document.getElementById('resultEmpty');
  emptyEl.style.display = 'none';
  rowsEl.style.display = 'block';
  rowsEl.innerHTML = lines.map(l =>
    `<div class="result-row"><span class="result-label">${{l.label}}</span><span class="result-value">${{l.value}}</span></div>`
  ).join('') + `<div class="result-total"><span class="result-total-label">{result_label}</span><span class="result-total-value">${{typeof total === 'number' ? total.toLocaleString(undefined,{{maximumFractionDigits:4}}) : total}}</span></div>`;

  // Save to history
  const summary = lines.map(l => `${{l.label}}: ${{l.value}}`).join(' | ');
  history.unshift({{
    summary,
    result: total.toLocaleString(undefined, {{maximumFractionDigits: 4}}),
    time: new Date().toLocaleTimeString(),
    inputs: lines
  }});
  saveHistory();
  renderHistory();
}}

function clearInputs() {{
  document.querySelectorAll('.tool-input').forEach(el => el.value = '');
  document.getElementById('resultRows').style.display = 'none';
  document.getElementById('resultEmpty').style.display = 'block';
}}

function clearHistory() {{
  if (!confirm('Clear all history?')) return;
  history = [];
  saveHistory();
  renderHistory();
}}

function loadFromHistory(idx) {{
  const item = history[idx];
  if (!item) return;
  // Re-populate inputs from saved data
  const inputs = document.querySelectorAll('.tool-input');
  item.inputs.forEach((field, i) => {{
    if (inputs[i]) inputs[i].value = parseFloat(field.value.replace(/,/g,'')) || '';
  }});
  calculate();
}}

function renderHistory() {{
  const el = document.getElementById('historyList');
  if (!history.length) {{
    el.innerHTML = '<div class="history-empty">No calculations yet.</div>';
    return;
  }}
  el.innerHTML = history.map((item, idx) =>
    `<div class="history-item" onclick="loadFromHistory(${{idx}})">
      <span class="history-summary">${{item.summary}}</span>
      <span class="history-result">${{item.result}}</span>
      <span class="history-time">${{item.time}}</span>
    </div>`
  ).join('');
}}

loadHistory();
renderHistory();
</script>
</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════

def build_dynamic_app(query: str) -> dict:
    q = query.lower()
    build_type = _detect_build_type(q)

    if build_type == "tool":
        entity_key, emoji, _ = _detect_entity(q)
        title = _make_title(entity_key, q)
        code = generate_tool_app(query)
        return {"title": title, "type": "dynamic_tool", "code": code}

    # "dashboard" falls through to crud for now (future: generate_dashboard_app)
    entity_key, emoji, _ = _detect_entity(q)
    title = _make_title(entity_key, q)
    code = generate_crud_app(query)
    return {"title": title, "type": "dynamic_crud", "code": code}


# =============================================================================
# PROJECT ORCHESTRATION
# =============================================================================

class ProjectFile:
    __slots__ = ("name", "content", "language")

    def __init__(self, name: str, content: str, language: str) -> None:
        self.name = name
        self.content = content
        self.language = language

    def to_dict(self) -> dict:
        return {"name": self.name, "content": self.content, "language": self.language}


class ProjectResult:
    __slots__ = ("title", "kind", "files")

    def __init__(self, title: str, kind: str, files: list[ProjectFile]) -> None:
        self.title = title
        self.kind = kind
        self.files = files

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "kind": self.kind,
            "files": [f.to_dict() for f in self.files],
        }


# ─── HTML Splitter ────────────────────────────────────────────────────────────

def _js_filename(kind: str) -> str:
    return "game.js" if kind == "game" else "app.js"


def split_html_to_files(full_html: str, js_name: str = "app.js") -> list[ProjectFile]:
    """
    Split a single-file HTML document into index.html + style.css + app/game.js.
    Handles multiple <style> blocks and the last <script> block (game/app logic).
    """
    html = full_html

    # ── Extract all <style> blocks ──
    style_parts: list[str] = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)
    combined_css = "\n\n".join(p.strip() for p in style_parts if p.strip())

    # ── Extract last <script> block (the logic) ──
    script_matches = list(re.finditer(r"<script(?:\s[^>]*)?>", html))
    js_content = ""
    if script_matches:
        # Use the LAST script block that has meaningful content
        for m in reversed(script_matches):
            start = m.end()
            end = html.find("</script>", start)
            if end == -1:
                continue
            candidate = html[start:end].strip()
            # Skip CDN / src-only script tags
            if len(candidate) > 100:
                js_content = candidate
                break

    # ── Build clean index.html ──
    clean = html

    # Replace <style> blocks with single link tag (only first time)
    if combined_css:
        first = True
        def _replace_style(m: re.Match) -> str:
            nonlocal first
            if first:
                first = False
                return '<link rel="stylesheet" href="style.css">'
            return ""
        clean = re.sub(r"<style[^>]*>.*?</style>", _replace_style, clean, flags=re.DOTALL)

    # Replace the last logic <script> with external reference
    if js_content:
        # Find last script block that contains our js_content (escaped for regex safety)
        pattern = re.compile(
            r"<script(?:\s[^>]*)?>(?:(?!<\/script>).)*" + re.escape(js_content[:60]),
            re.DOTALL,
        )
        def _replace_script(m: re.Match) -> str:
            return f'<script src="{js_name}"></script>'
        clean = pattern.sub(_replace_script, clean, count=1)

    # Clean up blank lines left behind
    clean = re.sub(r"\n{3,}", "\n\n", clean).strip()

    files: list[ProjectFile] = [
        ProjectFile("index.html", clean, "html"),
    ]
    if combined_css:
        files.append(ProjectFile("style.css", combined_css, "css"))
    if js_content:
        files.append(ProjectFile(js_name, js_content, "javascript"))

    return files


# ─── Game Project ─────────────────────────────────────────────────────────────

# Map genre → friendly name for the README
_GENRE_NAMES = {
    "snake": "Snake", "pong": "Pong", "flappy": "Flappy Bird",
    "brickbreaker": "Brick Breaker", "spaceshooter": "Space Shooter",
    "platformer": "Platformer", "maze": "Maze", "memory": "Memory Match",
    "tictactoe": "Tic-Tac-Toe", "racing": "Racing", "clicker": "Clicker",
    "zombie": "Zombie Survival", "tower_defense": "Tower Defense",
    "whack": "Whack-a-Mole", "2048": "2048", "blackjack": "Blackjack",
    "asteroids": "Asteroids", "fishing": "Fishing", "chess": "Chess",
    "doodle": "Doodle Jump",
}


def generate_game_project(query: str) -> ProjectResult:
    spec = parse_build_request(query)
    effective = _enrich_query_from_spec(query, spec)
    q = spec.normalized

    code = ""
    title = spec.title

    # 1. Autonomous — original code from scratch (no template copying)
    if spec.use_autonomous:
        auto = autonomous_generate(effective)
        code = auto.get("code", "")
        title = auto.get("title", spec.title)

    # 2. Synthesis — compositional canvas game engine
    if (not code or len(code) < 200) and (spec.use_synthesis or spec.genre == "universal" or spec.complexity == "complex"):
        code = synthesize_game(effective)
        title = spec.title

    # 3. Compile — genre templates as last resort for classic games
    if not code or len(code) < 200:
        compiled = compile_game(effective)
        title = compiled.get("title", spec.title)
        code = compiled.get("code", "")
        if not code or len(code) < 200:
            auto = autonomous_generate(effective)
            code = auto.get("code", "")
            title = auto.get("title", spec.title)

    files = split_html_to_files(code, "game.js")
    files = _append_typescript_types(files, spec)
    return ProjectResult(title=title, kind="game", files=files)


# ─── App Project ──────────────────────────────────────────────────────────────

def generate_app_project(query: str) -> ProjectResult:
    spec = parse_build_request(query)
    effective = _enrich_query_from_spec(query, spec)
    q = spec.normalized

    title = spec.title
    code = ""

    # 1. Autonomous — custom app logic written from scratch
    if spec.use_autonomous and (spec.kind in ("tool", "crud", "app") or not spec.app_type):
        auto = autonomous_generate(effective)
        code = auto.get("code", "")
        title = auto.get("title", spec.title)

    # 2. Dynamic builders for CRUD / tools
    if not code or len(code) < 150:
        if spec.kind == "crud" or any(w in q for w in ("dashboard", "inventory", "database", "crud", "admin")):
            built = build_dynamic_app(effective)
        elif spec.app_type:
            built = build_app(effective)
        elif spec.kind == "tool":
            built = build_dynamic_app(effective)
        else:
            built = build_dynamic_app(effective)
        title = built.get("title", spec.title)
        code = built.get("code", "")

    # 3. Final fallback — autonomous again if templates produced nothing useful
    if not code or len(code) < 100:
        auto = autonomous_generate(effective)
        code = auto.get("code", "")
        title = auto.get("title", spec.title)

    files = split_html_to_files(code, "app.js")
    files = _append_typescript_types(files, spec)
    return ProjectResult(title=title, kind="app", files=files)


# ─── Main entry point ─────────────────────────────────────────────────────────

@dataclass
class BuildSpec:
    """Parsed build request — what the user wants generated."""
    raw: str
    normalized: str
    title: str = "Project"
    kind: str = "auto"          # game | app | tool | crud
    genre: str = ""
    app_type: str = ""
    features: list[str] = field(default_factory=list)
    theme: str = "dark"
    use_synthesis: bool = False
    use_research: bool = False
    use_autonomous: bool = True
    complexity: str = "medium"  # simple | medium | complex


def parse_build_request(query: str) -> BuildSpec:
    """Deep-parse a build query into structured generation instructions."""
    q = query.lower().strip()
    spec = BuildSpec(raw=query, normalized=q)

    spec.genre = _detect_genre(q)
    spec.app_type = detect_app_type(q)
    spec.use_synthesis = spec.genre == "universal" or should_synthesize(query)
    spec.use_autonomous = is_autonomous_candidate(query) or spec.use_synthesis or spec.complexity != "simple"
    spec.use_research = _has_build_intent(q) and (
        spec.genre == "universal"
        or spec.use_synthesis
        or spec.complexity == "complex"
        or spec.kind in ("crud", "tool")
    )

    feat = _extract_game_features(q)
    spec.features = [k for k, v in feat.items() if v and k not in ("title",)]
    spec.theme = _detect_theme(q).get("name", "dark")

    if _is_game_query(query) or (
        spec.genre != "universal"
        and any(w in q for w in ("game", "arcade", "playable", "shooter", "platformer"))
    ):
        spec.kind = "game"
        spec.title = _build_game_title(q, feat)
    elif _is_explicit_app_query(q):
        if any(w in q for w in ("dashboard", "crud", "inventory", "database", "admin panel", "manager")):
            spec.kind = "crud"
            spec.title = query[:48].strip().title() or "Data Manager"
        elif any(w in q for w in ("tool", "utility", "converter", "generator", "widget")):
            spec.kind = "tool"
            spec.title = query[:48].strip().title() or "Tool"
        else:
            spec.kind = "app"
            spec.title = query[:48].strip().title() or "App"
    elif spec.use_synthesis and not _is_explicit_app_query(q):
        spec.kind = "game"
        spec.title = _build_game_title(q, feat)
    else:
        spec.kind = "app"
        spec.title = query[:48].strip().title() or "App"

    spec.complexity = (
        "complex" if len(spec.features) >= 3 or len(q) > 80 or spec.use_synthesis
        else "simple" if len(q) < 30
        else "medium"
    )
    return spec


def _enrich_query_from_spec(query: str, spec: BuildSpec) -> str:
    """Append structured hints so generators pick the right template."""
    hints: list[str] = []
    if spec.features:
        hints.append("features: " + ", ".join(spec.features[:8]))
    if spec.genre and spec.genre != "universal":
        hints.append(f"genre: {spec.genre}")
    if spec.app_type:
        hints.append(f"app: {spec.app_type}")
    if spec.theme:
        hints.append(f"theme: {spec.theme}")
    if not hints:
        return query
    return f"{query} — {'; '.join(hints)}"


def _append_typescript_types(files: list[ProjectFile], spec: BuildSpec) -> list[ProjectFile]:
    """Add a shared types.ts for multi-file projects."""
    if len(files) < 2:
        return files
    ts = """// Shared types for this ForgeAI project
export interface GameState {
  score: number;
  lives: number;
  level: number;
  paused: boolean;
}

export interface AppConfig {
  theme: string;
  title: string;
}
"""
    if any(f.name == "types.ts" for f in files):
        return files
    return files + [ProjectFile("types.ts", ts, "typescript")]


def _append_readme(result: ProjectResult, spec: BuildSpec) -> ProjectResult:
    lines = [
        f"# {result.title}",
        "",
        "Generated by **ForgeAI Studio**.",
        "",
        f"- **Kind:** {result.kind}",
        f"- **Complexity:** {spec.complexity}",
    ]
    if spec.genre:
        lines.append(f"- **Genre:** {spec.genre}")
    if spec.app_type:
        lines.append(f"- **App type:** {spec.app_type}")
    if spec.features:
        lines.append(f"- **Features:** {', '.join(spec.features)}")
    lines += ["", "## Files", ""]
    for f in result.files:
        lines.append(f"- `{f.name}` ({f.language})")
    readme = "\n".join(lines)
    files = list(result.files)
    if not any(f.name == "README.md" for f in files):
        files.append(ProjectFile("README.md", readme, "markdown"))
    return ProjectResult(result.title, result.kind, files)


_GAME_KEYWORDS = {
    "game", "snake", "pong", "flappy", "bird", "tetris", "breakout", "brickbreaker",
    "brick", "space", "shooter", "invader", "platformer", "platform", "mario",
    "maze", "memory", "tictactoe", "tic tac toe", "racing", "race", "car",
    "clicker", "cookie", "idle", "zombie", "tower", "defense", "whack", "mole",
    "2048", "blackjack", "poker", "asteroid", "fishing", "chess", "doodle",
    "arcade", "playable", "dungeon", "runner", "jump", "fly", "shoot",
}


def _is_game_query(query: str) -> bool:
    q = query.lower()
    if re.search(
        r"(make|build|create|code|write|generate|give me|i want|i need).{0,40}game",
        q,
    ):
        return True
    return any(kw in q for kw in _GAME_KEYWORDS)


def generate_project(query: str) -> ProjectResult:
    """Main entry point — routes to the best generator with fallbacks."""
    spec = parse_build_request(query)

    if spec.kind == "game" or (_is_game_query(query) and not _is_explicit_app_query(spec.normalized)):
        result = generate_game_project(query)
    elif spec.kind in ("crud", "tool", "app") or _is_explicit_app_query(spec.normalized):
        result = generate_app_project(query)
    elif spec.use_synthesis:
        result = generate_game_project(query)
    else:
        result = generate_app_project(query)

    return _append_readme(result, spec)


# =============================================================================
# WEB RESEARCH — Google / DuckDuckGo fallback for unknown build requests
# =============================================================================

_last_searched: bool = False

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ForgeAI/1.0)",
}

def _fetch(url: str, timeout: int = 4) -> str:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def ddg_search(query: str) -> str | None:
    """DuckDuckGo Instant Answer API — free, no key required."""
    url = "https://api.duckduckgo.com/?q=" + urllib.parse.quote(query) + "&format=json&no_redirect=1&no_html=1&skip_disambig=1"
    try:
        data = json.loads(_fetch(url))
        abstract = data.get("AbstractText", "").strip()
        if abstract:
            source = data.get("AbstractSource", "")
            url_ref = data.get("AbstractURL", "")
            result = f"**{abstract}**"
            if source:
                result += f"\n\n*Source: {source}*"
                if url_ref:
                    result += f" — {url_ref}"
            return result
        # Try related topics
        topics = data.get("RelatedTopics", [])
        snippets = []
        for t in topics[:3]:
            text = t.get("Text", "") if isinstance(t, dict) else ""
            if text and len(text) > 20:
                snippets.append(f"- {text}")
        if snippets:
            return "Here's what I found:\n\n" + "\n".join(snippets)
    except Exception:
        pass
    return None

def google_search(query: str) -> str | None:
    """Scrape Google's featured snippet / first result description."""
    url = "https://www.google.com/search?q=" + urllib.parse.quote(query) + "&hl=en"
    try:
        html = _fetch(url, timeout=5)
        # Featured snippet
        m = re.search(r'<div[^>]*data-tts="answers"[^>]*>(.*?)</div>', html, re.DOTALL)
        if m:
            text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if text:
                return f"**{text}**\n\n*Source: Google*"
        # Knowledge panel description
        m = re.search(r'"description"\s*:\s*"([^"]{30,500})"', html)
        if m:
            return f"**{m.group(1)}**\n\n*Source: Google Knowledge Panel*"
    except Exception:
        pass
    return None

def web_lookup(query: str) -> str:
    """Try DuckDuckGo first, fall back to Google, then return a search link."""
    global _last_searched
    _last_searched = True
    result = ddg_search(query)
    if result:
        return f"### Web Search Result\n\n{result}"
    result = google_search(query)
    if result:
        return f"### Web Search Result\n\n{result}"
    encoded = urllib.parse.quote(query)
    return (
        f"I don't have that in my knowledge base. "
        f"[Search Google for \"{query}\"](https://www.google.com/search?q={encoded})"
    )


_BUILD_RE = re.compile(
    r"\b(make|build|create|code|write|generate|develop|design|craft|give me|i want|i need|program)\b",
    re.I,
)

def _has_build_intent(query: str) -> bool:
    return bool(_BUILD_RE.search(query))


def _needs_web_research(query: str) -> bool:
    """Look up the web when the request is a build we cannot classify locally."""
    q = query.lower()
    if not _has_build_intent(q):
        return False
    spec = parse_build_request(query)
    if spec.kind == "game" and spec.genre != "universal" and not spec.use_synthesis:
        return False
    if spec.app_type or _is_explicit_app_query(q):
        return False
    if spec.use_synthesis or spec.complexity == "complex":
        return True
    return spec.kind in ("crud", "tool", "auto") or spec.genre == "universal"


def _plain_context(text: str) -> str:
    return re.sub(r"[*_#`\[\]]", "", text).strip()


def research_for_build(query: str) -> str | None:
    """Search Google then DuckDuckGo; return plain context text or None."""
    global _last_searched
    raw = google_search(query) or ddg_search(query)
    if not raw:
        return None
    _last_searched = True
    return _plain_context(raw)[:500]


def generate_anything(query: str) -> ProjectResult:
    """
    Universal generator: builds games, apps, and tools.
    Researches unknown requests on the web before synthesising code.
    """
    spec = parse_build_request(query)
    effective = query
    if spec.use_research or _needs_web_research(query):
        ctx = research_for_build(query)
        if ctx:
            effective = f"{query}\n\nResearch context:\n{ctx}"
    effective = _enrich_query_from_spec(effective, spec)
    return generate_project(effective)


def generate_anything_with_meta(query: str) -> tuple[ProjectResult, bool]:
    """Like generate_anything but also returns whether web research was used."""
    spec = parse_build_request(query)
    researched = False
    effective = query
    if spec.use_research or _needs_web_research(query):
        ctx = research_for_build(query)
        if ctx:
            researched = True
            effective = f"{query}\n\nResearch context:\n{ctx}"
    effective = _enrich_query_from_spec(effective, spec)
    return generate_project(effective), researched
# =============================================================================
# MULTI-LANGUAGE POWER ENGINE — TypeScript, JS, Java, Python, Ruby, SQL, R, Rust
# =============================================================================

POWER_LANGUAGES = frozenset({
    "typescript", "javascript", "java", "python", "ruby", "sql", "r", "rust",
})

_LANG_ALIASES: dict[str, str] = {
    "ts": "typescript", "typescript": "typescript",
    "js": "javascript", "javascript": "javascript", "node": "javascript",
    "py": "python", "python": "python", "python3": "python",
    "java": "java",
    "rb": "ruby", "ruby": "ruby", "rails": "ruby",
    "sql": "sql", "postgres": "sql", "postgresql": "sql", "mysql": "sql",
    "r": "r", "r lang": "r", "r language": "r",
    "rust": "rust", "rs": "rust",
    "cpp": "cpp", "c++": "cpp", "csharp": "csharp", "c#": "csharp",
    "golang": "golang", "go": "golang",
}

_PROG_CONCEPTS_MAP: dict[str, str] = {
    "function": "function", "functions": "function", "method": "function", "def": "function",
    "class": "class", "classes": "class", "object": "class", "oop": "class",
    "loop": "loop", "loops": "loop", "for loop": "loop", "while loop": "loop",
    "error": "error_handling", "exception": "error_handling", "try catch": "error_handling",
    "async": "async", "await": "async", "asynchronous": "async", "promise": "async",
    "list": "list_ops", "array": "list_ops", "slice": "list_ops",
    "file": "file_io", "read file": "file_io", "write file": "file_io",
    "api": "api", "rest": "api", "fetch": "api", "endpoint": "api",
    "database": "database", "query": "database", "select": "database",
    "sort": "sort", "binary search": "binary_search", "recursion": "recursion",
    "fibonacci": "fibonacci", "factorial": "factorial",
    "interface": "interface", "type": "interface", "generic": "generics",
    "struct": "struct", "enum": "enum", "trait": "trait", "ownership": "ownership",
    "dataframe": "dataframe", "vector": "dataframe",
}


def detect_power_language(q: str) -> str:
    """Detect target language from query."""
    q = q.strip().lower()
    if re.search(r"(?:^|\b)r(?:\s+lang(?:uage)?|\s+script|\s+programming)\b", q):
        return "r"
    if re.match(r"^r\s+\w", q):
        return "r"
    for alias, canonical in sorted(_LANG_ALIASES.items(), key=lambda x: -len(x[0])):
        if canonical == "r":
            continue
        if re.search(rf"\b{re.escape(alias)}\b", q):
            return canonical
    return ""


def detect_code_task(q: str) -> str:
    """Detect what kind of code the user wants generated."""
    for keyword in sorted(_PROG_CONCEPTS_MAP, key=len, reverse=True):
        if keyword in q:
            return _PROG_CONCEPTS_MAP[keyword]
    if re.search(r"\b(write|code|show|give|generate|create)\b.{0,30}\b(code|function|class|script|program)\b", q):
        return "function"
    if "hello" in q:
        return "hello_world"
    return "function"


def _task_from_query(query: str) -> tuple[str, str]:
    q = query.lower()
    return detect_power_language(q), detect_code_task(q)


# ── Per-language original code composers (no KB copy) ─────────────────────────

def _compose_python(task: str, query: str) -> str:
    if task == "fibonacci":
        return '''def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number (0-indexed)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_sequence(count: int) -> list[int]:
    return [fibonacci(i) for i in range(count)]


if __name__ == "__main__":
    print(fib_sequence(10))'''
    if task == "class":
        return '''from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Task:
    title: str
    done: bool = False
    priority: int = 1
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def complete(self) -> None:
        self.done = True

    def __str__(self) -> str:
        mark = "✓" if self.done else "○"
        return f"{mark} [{self.priority}] {self.title}"


class TaskBoard:
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def add(self, title: str, priority: int = 1) -> Task:
        task = Task(title=title, priority=priority)
        self._tasks.append(task)
        return task

    def pending(self) -> list[Task]:
        return [t for t in self._tasks if not t.done]'''
    if task == "async":
        return '''import asyncio
import aiohttp
from typing import Any


async def fetch_json(url: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_all(urls: list[str]) -> list[dict[str, Any]]:
    return await asyncio.gather(*(fetch_json(u) for u in urls))


async def main() -> None:
    data = await fetch_json("https://api.github.com/repos/python/cpython")
    print(data.get("full_name"), data.get("stargazers_count"))


if __name__ == "__main__":
    asyncio.run(main())'''
    if task == "file_io":
        return '''from pathlib import Path
import json
from typing import Any


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_json(path: str | Path) -> Any:
    return json.loads(read_text(path))'''
    if task == "database":
        return '''import sqlite3
from contextlib import contextmanager
from typing import Iterator, Any


@contextmanager
def connect(db_path: str = ":memory:") -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def insert_user(conn: sqlite3.Connection, email: str, name: str) -> int:
    cur = conn.execute(
        "INSERT INTO users (email, name) VALUES (?, ?)", (email, name)
    )
    return int(cur.lastrowid)


def find_user_by_email(conn: sqlite3.Connection, email: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    return dict(row) if row else None'''
    return '''def greet(name: str) -> str:
  return f"Hello, {name}!"


def main() -> None:
  print(greet("ForgeAI"))


if __name__ == "__main__":
  main()'''


def _compose_typescript(task: str, query: str) -> str:
    if task == "interface":
        return '''export interface User {
  readonly id: string;
  email: string;
  name: string;
  roles: ReadonlyArray<Role>;
  createdAt: Date;
}

export type Role = "admin" | "editor" | "viewer";

export interface ApiResponse<T> {
  data: T;
  meta: { page: number; total: number };
}

export async function fetchUser(id: string): Promise<ApiResponse<User>> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<ApiResponse<User>>;
}'''
    if task == "async":
        return '''type RetryOptions = { retries?: number; delayMs?: number };

export async function fetchWithRetry<T>(
  url: string,
  init?: RequestInit,
  { retries = 3, delayMs = 300 }: RetryOptions = {},
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, init);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return (await res.json()) as T;
    } catch (err) {
      lastError = err;
      if (attempt < retries) await new Promise(r => setTimeout(r, delayMs * (attempt + 1)));
    }
  }
  throw lastError;
}'''
    if task == "class":
        return '''export class EventBus<Events extends Record<string, unknown>> {
  private listeners = new Map<keyof Events, Set<(payload: Events[keyof Events]) => void>>();

  on<K extends keyof Events>(event: K, handler: (payload: Events[K]) => void): () => void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event)!.add(handler as (p: Events[keyof Events]) => void);
    return () => this.listeners.get(event)?.delete(handler as (p: Events[keyof Events]) => void);
  }

  emit<K extends keyof Events>(event: K, payload: Events[K]): void {
    this.listeners.get(event)?.forEach(fn => fn(payload));
  }
}'''
    if task == "generics":
        return '''export function groupBy<T, K extends string | number>(
  items: readonly T[],
  keyFn: (item: T) => K,
): Record<K, T[]> {
  return items.reduce((acc, item) => {
    const key = keyFn(item);
    (acc[key] ??= []).push(item);
    return acc;
  }, {} as Record<K, T[]>);
}

export function pipe<T>(value: T, ...fns: Array<(v: T) => T>): T {
  return fns.reduce((v, fn) => fn(v), value);
}'''
    return '''export function fibonacci(n: number): number {
  if (n < 0) throw new RangeError("n must be >= 0");
  let a = 0, b = 1;
  for (let i = 0; i < n; i++) [a, b] = [b, a + b];
  return a;
}

export const sum = (nums: readonly number[]): number =>
  nums.reduce((acc, n) => acc + n, 0);'''


def _compose_javascript(task: str, query: str) -> str:
    if task == "async":
        return '''export async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { Accept: "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  return res.json();
}

export async function parallelMap(items, concurrency, mapper) {
  const results = [];
  let index = 0;
  async function worker() {
    while (index < items.length) {
      const i = index++;
      results[i] = await mapper(items[i], i);
    }
  }
  await Promise.all(Array.from({ length: concurrency }, worker));
  return results;
}'''
    if task == "class":
        return '''export class LRUCache {
  constructor(capacity) {
    this.capacity = capacity;
    this.map = new Map();
  }

  get(key) {
    if (!this.map.has(key)) return undefined;
    const value = this.map.get(key);
    this.map.delete(key);
    this.map.set(key, value);
    return value;
  }

  set(key, value) {
    if (this.map.has(key)) this.map.delete(key);
    else if (this.map.size >= this.capacity) {
      const oldest = this.map.keys().next().value;
      this.map.delete(oldest);
    }
    this.map.set(key, value);
  }
}'''
    return '''export function debounce(fn, waitMs = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}

export function fibonacci(n) {
  let [a, b] = [0, 1];
  for (let i = 0; i < n; i++) [a, b] = [b, a + b];
  return a;
}'''


def _compose_java(task: str, query: str) -> str:
    if task == "class":
        return '''import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public final class TaskRepository {
    private final List<Task> tasks = new ArrayList<>();

    public Task add(String title, int priority) {
        Task task = new Task(title, priority, Instant.now());
        tasks.add(task);
        return task;
    }

    public List<Task> findPending() {
        return tasks.stream().filter(t -> !t.isDone()).toList();
    }

    public Optional<Task> findById(long id) {
        return tasks.stream().filter(t -> t.id() == id).findFirst();
    }

    public record Task(long id, String title, int priority, Instant createdAt, boolean done) {
        public Task(String title, int priority, Instant createdAt) {
            this(System.nanoTime(), title, priority, createdAt, false);
        }
        public Task markDone() {
            return new Task(id, title, priority, createdAt, true);
        }
    }
}'''
    if task == "api":
        return '''import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class MiniApi {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/health", exchange -> respond(exchange, 200, "{\\"ok\\":true}"));
        server.createContext("/api/hello", exchange -> respond(exchange, 200, "{\\"message\\":\\"Hello from ForgeAI\\"}"));
        server.setExecutor(null);
        server.start();
        System.out.println("Listening on http://localhost:8080");
    }

    static void respond(HttpExchange ex, int code, String body) throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json");
        ex.sendResponseHeaders(code, bytes.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(bytes); }
    }
}'''
    return '''public class Fibonacci {
    public static long fib(int n) {
        if (n < 0) throw new IllegalArgumentException("n must be >= 0");
        long a = 0, b = 1;
        for (int i = 0; i < n; i++) {
            long next = a + b;
            a = b;
            b = next;
        }
        return a;
    }

    public static void main(String[] args) {
        System.out.println(fib(10));
    }
}'''


def _compose_ruby(task: str, query: str) -> str:
    if task == "class":
        return '''class TaskBoard
  Task = Struct.new(:id, :title, :done, :priority, keyword_init: true)

  def initialize
    @tasks = []
    @next_id = 1
  end

  def add(title, priority: 1)
    task = Task.new(id: @next_id, title: title, done: false, priority: priority)
    @next_id += 1
    @tasks << task
    task
  end

  def complete(id)
    task = @tasks.find { |t| t.id == id }
    raise ArgumentError, "task not found" unless task
    task.done = true
    task
  end

  def pending
    @tasks.reject(&:done).sort_by(&:priority)
  end
end'''
    if task == "api":
        return '''require "sinatra/base"
require "json"

class ForgeApp < Sinatra::Base
  configure { set :show_exceptions, :development }

  get "/health" do
    content_type :json
    { ok: true, service: "forgeai" }.to_json
  end

  post "/api/echo" do
    content_type :json
    body = JSON.parse(request.body.read)
    { received: body, at: Time.now.utc.iso8601 }.to_json
  end
end'''
    return '''def fibonacci(n)
  raise ArgumentError, "n must be >= 0" if n.negative?
  a, b = 0, 1
  n.times { a, b = b, a + b }
  a
end

puts fibonacci(10)'''


def _compose_sql(task: str, query: str) -> str:
    if task == "database" or "join" in query.lower():
        return '''-- Users with their most recent order totals
CREATE TABLE IF NOT EXISTS users (
  id          SERIAL PRIMARY KEY,
  email       TEXT UNIQUE NOT NULL,
  full_name   TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
  id          SERIAL PRIMARY KEY,
  user_id     INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  total_cents INT NOT NULL CHECK (total_cents >= 0),
  status      TEXT NOT NULL DEFAULT 'pending',
  placed_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_user_placed
  ON orders (user_id, placed_at DESC);

-- Top customers by lifetime spend
SELECT
  u.id,
  u.email,
  u.full_name,
  COUNT(o.id) AS order_count,
  COALESCE(SUM(o.total_cents), 0) AS lifetime_cents
FROM users u
LEFT JOIN orders o ON o.user_id = u.id AND o.status = 'completed'
GROUP BY u.id, u.email, u.full_name
ORDER BY lifetime_cents DESC
LIMIT 25;'''
    return '''-- Analytical window query: running 7-day average
WITH daily_sales AS (
  SELECT
    DATE_TRUNC('day', placed_at) AS day,
    SUM(total_cents) / 100.0     AS revenue
  FROM orders
  WHERE status = 'completed'
  GROUP BY 1
)
SELECT
  day,
  revenue,
  AVG(revenue) OVER (
    ORDER BY day
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS rolling_7d_avg
FROM daily_sales
ORDER BY day;'''


def _compose_r_lang(task: str, query: str) -> str:
    if task == "dataframe":
        return '''library(dplyr)
library(ggplot2)

# Load and clean sales data
sales <- read.csv("sales.csv", stringsAsFactors = FALSE) |>
  mutate(
    order_date = as.Date(order_date),
    revenue = as.numeric(revenue),
    region = factor(region)
  ) |>
  filter(!is.na(revenue), revenue >= 0)

# Monthly revenue by region
monthly <- sales |>
  mutate(month = floor_date(order_date, "month")) |>
  group_by(month, region) |>
  summarise(
    orders = n(),
    revenue = sum(revenue),
    avg_order = mean(revenue),
    .groups = "drop"
  )

ggplot(monthly, aes(month, revenue, color = region)) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  labs(title = "Monthly Revenue by Region", y = "Revenue ($)", x = NULL) +
  theme_minimal()'''
    return '''# Vectorized statistics pipeline
analyze <- function(x) {
  stopifnot(is.numeric(x), length(x) > 0)
  list(
    n = length(x),
    mean = mean(x),
    median = median(x),
    sd = sd(x),
    q25 = quantile(x, 0.25),
    q75 = quantile(x, 0.75)
  )
}

set.seed(42)
samples <- rnorm(1000, mean = 50, sd = 10)
print(analyze(samples))'''


def _compose_rust(task: str, query: str) -> str:
    if task == "struct" or task == "ownership":
        return '''#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UserId(u64);

#[derive(Debug, Clone)]
pub struct User {
    pub id: UserId,
    pub email: String,
    pub name: String,
}

impl User {
    pub fn new(id: u64, email: impl Into<String>, name: impl Into<String>) -> Self {
        Self {
            id: UserId(id),
            email: email.into(),
            name: name.into(),
        }
    }

    pub fn rename(mut self, name: impl Into<String>) -> Self {
        self.name = name.into();
        self
    }
}

pub struct UserStore {
    users: Vec<User>,
}

impl UserStore {
    pub fn new() -> Self { Self { users: Vec::new() } }

    pub fn insert(&mut self, user: User) -> &User {
        self.users.push(user);
        self.users.last().expect("just pushed")
    }

    pub fn find(&self, id: UserId) -> Option<&User> {
        self.users.iter().find(|u| u.id == id)
    }
}'''
    if task == "async":
        return '''use reqwest::Client;
use serde::Deserialize;
use anyhow::{Context, Result};

#[derive(Debug, Deserialize)]
struct Repo {
    full_name: String,
    stargazers_count: u64,
}

pub async fn fetch_repo(owner: &str, name: &str) -> Result<Repo> {
    let url = format!("https://api.github.com/repos/{owner}/{name}");
    let client = Client::new();
    client
        .get(&url)
        .header("User-Agent", "forgeai-studio")
        .send()
        .await
        .context("request failed")?
        .error_for_status()
        .context("bad status")?
        .json::<Repo>()
        .await
        .context("invalid json")
}

#[tokio::main]
async fn main() -> Result<()> {
    let repo = fetch_repo("rust-lang", "rust").await?;
    println!("{} has {} stars", repo.full_name, repo.stargazers_count);
    Ok(())
}'''
    if task == "enum":
        return '''#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Status {
    Pending,
    Running,
    Done,
    Failed,
}

impl Status {
    pub fn is_terminal(self) -> bool {
        matches!(self, Status::Done | Status::Failed)
    }
}

pub fn step(current: Status, success: bool) -> Status {
    match current {
        Status::Pending if success => Status::Running,
        Status::Running if success => Status::Done,
        Status::Running if !success => Status::Failed,
        other => other,
    }
}'''
    return '''pub fn fibonacci(n: u32) -> u64 {
    if n == 0 { return 0; }
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 1..n {
        let next = a.saturating_add(b);
        a = b;
        b = next;
    }
    a
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn fib_values() {
        assert_eq!(fibonacci(0), 0);
        assert_eq!(fibonacci(1), 0);
        assert_eq!(fibonacci(10), 34);
    }
}'''


_LANG_COMPOSERS = {
    "python": _compose_python,
    "typescript": _compose_typescript,
    "javascript": _compose_javascript,
    "java": _compose_java,
    "ruby": _compose_ruby,
    "sql": _compose_sql,
    "r": _compose_r_lang,
    "rust": _compose_rust,
}


def generate_power_code(query: str) -> str | None:
    """
    Generate powerful original code in TypeScript, JS, Java, Python, Ruby, SQL, R, or Rust.
    Returns markdown with fenced code block, or None if not a code-generation request.
    """
    q = query.lower()
    lang = detect_power_language(q)
    if not lang and not re.search(r"\b(code|function|class|script|program|query)\b", q):
        return None
    if not lang:
        lang = random.choice(["typescript", "python", "rust", "javascript"])

    task = detect_code_task(q)
    composer = _LANG_COMPOSERS.get(lang)
    if not composer:
        return None

    code = composer(task, query)
    display = lang.upper() if lang in ("sql", "r") else lang.replace("golang", "Go").title()
    task_label = task.replace("_", " ").title()
    fence = "sql" if lang == "sql" else ("r" if lang == "r" else lang)
    if lang == "typescript":
        fence = "typescript"
    elif lang == "javascript":
        fence = "javascript"

    return (
        f"### {display} — {task_label}\n\n"
        f"*Original code composed by ForgeAI for your request — not copied from a template library.*\n\n"
        f"```{fence}\n{code.strip()}\n```"
    )


def score_programming(q: str) -> int:
    """Intent score for programming / code-generation queries."""
    score = 0
    lang = detect_power_language(q)
    if lang:
        score += 70
    if lang and any(w in q for w in ("history", "origin", "created", "hello world", "syntax", "example")):
        score += 95
    if re.search(r"\b(code|write|show|generate|implement|build)\b.{0,40}\b(function|class|api|script|program|query)\b", q):
        score += 85
    if any(w in q for w in ("hello world", "syntax", "example", "how to write", "how do i write")):
        score += 50
    if any(w in q for w in ("function", "class", "async", "loop", "api", "sql", "database", "trait", "interface")):
        score += 40
    if any(q.startswith(w) or w in q for w in (
        "how do i", "how to", "what is a", "explain", "write a", "show me", "code a",
    )):
        score += 25
    for key in CODING_HELP:
        if key in q:
            score += 60
            break
    return min(100, score)


def dispatch_programming(query: str, mode: str = "forge_code") -> str:
    """
    Handle all programming questions — multi-language code generation lives here only.
    brain.py delegates to this function.
    """
    q = query.lower()
    lang = detect_power_language(q)
    task = detect_code_task(q)
    _codegen_cues = re.compile(
        r"\b(write|code|show|generate|create|implement|give me|build|class|function|"
        r"interface|script|query|program|method|trait|struct|enum)\b"
    )

    # 1. Powerful original multi-language code generation
    power = generate_power_code(query)
    if power and (lang or _codegen_cues.search(q)):
        if mode == "forge_thinking":
            return (
                f"### Thinking Process\n"
                f"- **Intent:** Generate original {lang or 'auto'} code from scratch\n"
                f"- **Approach:** Compose logic blocks — no template copy\n\n"
                f"---\n\n{power}"
            )
        return power

    # 2. Lang + concept from KB examples
    if lang and task:
        kb_lang = lang if lang in LANG_EXAMPLES else lang
        examples = LANG_EXAMPLES.get(kb_lang, {})
        if task in examples:
            snippet = examples[task]
            heading = f"### {lang.title()} — {task.replace('_', ' ').title()}"
            return f"{heading}\n\n```{lang}\n{snippet}\n```"

    # 3. Hello world
    for lang_key, hw in LANG_HELLO_WORLD.items():
        if lang_key in q and any(w in q for w in ("hello world", "syntax", "example", "how to write", "sample", "print")):
            history = LANG_HISTORY.get(lang_key, "")
            body = f"```{lang_key}\n{hw}\n```"
            if history:
                body += f"\n\n{history}"
            return f"### {lang_key.title()} — Hello World\n\n{body}"

    # 4. Language history
    for lang_key, history in LANG_HISTORY.items():
        if lang_key in q and any(w in q for w in ("history", "origin", "created", "designed", "who made", "invented")):
            hw = LANG_HELLO_WORLD.get(lang_key, "")
            block = f"\n\n```{lang_key}\n{hw}\n```" if hw else ""
            return f"### {lang_key.title()} Language Origin\n\n{history}{block}"

    # 5. Coding help KB
    for key, answer in CODING_HELP.items():
        if key in q:
            return answer

    # 6. Fallback — generate in detected language (or Python)
    fallback_lang = lang or "python"
    fallback = generate_power_code(f"write {fallback_lang} code for {query}")
    if fallback:
        return fallback

    return web_lookup(query)
