from data.game_templates import GAME_TEMPLATES


def _detect_genre(q: str) -> str:
    if any(w in q for w in ("pong", "paddle", "hockey")):
        return "pong"
    if any(w in q for w in ("tic", "toe", "noughts")):
        return "tictactoe"
    if any(w in q for w in ("flap", "bird", "wing")):
        return "flappy"
    if any(w in q for w in ("brick", "break", "shatter", "breaker")):
        return "brickbreaker"
    if any(w in q for w in ("clicker", "cookie", "idle")):
        return "clicker"
    if any(w in q for w in ("space", "shoot", "invader", "alien", "laser", "ship")):
        return "spaceshooter"
    return "snake"


def _detect_theme(q: str) -> dict:
    if any(w in q for w in ("synthwave", "cyberpunk", "pink", "magenta", "neon")):
        return {
            "name": "Neon Synthwave", "bg": "#0f051d",
            "primary": "#ec4899", "secondary": "#db2777",
            "accent": "#06b6d4", "text": "#fdf2f8",
            "gridColor": "rgba(236, 72, 153, 0.15)",
        }
    if any(w in q for w in ("matrix", "terminal", "hacker", "green")):
        return {
            "name": "Hacker Matrix", "bg": "#000000",
            "primary": "#22c55e", "secondary": "#15803d",
            "accent": "#86efac", "text": "#f0fdf4",
            "gridColor": "rgba(34, 197, 94, 0.1)",
        }
    if any(w in q for w in ("ocean", "sea", "blue", "water", "underwater")):
        return {
            "name": "Deep Ocean", "bg": "#0c2540",
            "primary": "#0ea5e9", "secondary": "#0284c7",
            "accent": "#f43f5e", "text": "#f0f9ff",
            "gridColor": "rgba(14, 165, 233, 0.15)",
        }
    if any(w in q for w in ("sunset", "orange", "red", "fire", "volcano")):
        return {
            "name": "Volcanic Sunset", "bg": "#1c0d02",
            "primary": "#f97316", "secondary": "#ea580c",
            "accent": "#e11d48", "text": "#fff7ed",
            "gridColor": "rgba(249, 115, 22, 0.15)",
        }
    if any(w in q for w in ("forest", "garden", "wood", "emerald")):
        return {
            "name": "Mystic Forest", "bg": "#022c22",
            "primary": "#10b981", "secondary": "#047857",
            "accent": "#f59e0b", "text": "#ecfdf5",
            "gridColor": "rgba(16, 185, 129, 0.1)",
        }
    return {
        "name": "Classic Neon", "bg": "#020617",
        "primary": "#10b981", "secondary": "#059669",
        "accent": "#ef4444", "text": "#e2e8f0",
        "gridColor": "rgba(16, 185, 129, 0.1)",
    }


def _detect_speed(q: str) -> tuple[float, str]:
    if any(w in q for w in ("fast", "speedy", "turbo", "rapid", "quick")):
        return 1.6, "Turbo Speed"
    if any(w in q for w in ("slow", "lazy", "chill", "relax")):
        return 0.6, "Chill Speed"
    return 1.0, "Normal"


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
<style>body{{background-color:{theme['bg']}}}
.grid-bg{{background-size:20px 24px;background-image:radial-gradient(circle,{theme['gridColor']} 1px,transparent 1px)}}</style>
</head>
<body class="grid-bg text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{theme['name']} ({speed_label})</span>
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
function spawnFood(){{
  food={{x:randPos(),y:randPos()}};
  if(snake.some(p=>p.x===food.x&&p.y===food.y)||obstacles.some(o=>o.x===food.x&&o.y===food.y))spawnFood();
}}
function gameOver(){{
  clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="{theme['accent']}";ctx.font="bold 18px Courier New";ctx.textAlign="center";
  ctx.fillText("GAME OVER",150,140);
}}
function update(){{
  let head={{x:snake[0].x+dx,y:snake[0].y+dy}};
  {boundary}
  if(snake.some(p=>p.x===head.x&&p.y===head.y))return gameOver();
  if(obstacles.some(o=>o.x===head.x&&o.y===head.y))return gameOver();
  snake.unshift(head);
  if(head.x===food.x&&head.y===food.y){{
    score+=10;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');spawnFood();
  }}else{{snake.pop();}}
  draw();
}}
function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme['accent']}';ctx.fillRect(food.x,food.y,grid,grid);
  snake.forEach((p,i)=>{{ctx.fillStyle=i===0?'{theme['primary']}':'{theme['secondary']}';ctx.fillRect(p.x,p.y,grid,grid);}});
  ctx.fillStyle='#94a3b8';obstacles.forEach(o=>ctx.fillRect(o.x,o.y,grid,grid));
}}
startBtn.onclick=()=>{{
  score=0;scoreEl.innerText='SCORE: 000';
  snake=[{{x:120,y:120}},{{x:105,y:120}},{{x:90,y:120}}];
  dx=grid;dy=0;spawnFood();
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,{interval});
}};
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
<style>body{{background-color:{theme['bg']}}}
.grid-bg{{background-size:20px 20px;background-image:radial-gradient(circle,{theme['gridColor']} 1px,transparent 1px)}}</style>
</head>
<body class="grid-bg text-white min-h-screen flex items-center justify-center p-4">
<div class="bg-slate-900/90 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{theme['name']} ({speed_label})</span>
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
function update(){{
  if(!running)return;
  ballX+=ballDX;ballY+=ballDY;
  if(cpuY+15<ballY)cpuY+={cpu_speed};else if(cpuY+15>ballY)cpuY-={cpu_speed};
  if(ballY<=0||ballY>=200)ballDY=-ballDY;
  if(ballX<=15&&ballY>=playerY&&ballY<=playerY+40){{ballDX=-ballDX*1.05;ballX=16;}}
  if(ballX>=285&&ballY>=cpuY&&ballY<=cpuY+40){{ballDX=-ballDX*1.05;ballX=284;}}
  if(ballX<0){{cpuScore++;resetBall();}}
  if(ballX>300){{playerScore++;resetBall();}}
  scoreEl.innerText="YOU: "+playerScore+" | CPU: "+cpuScore;
  draw();
}}
function resetBall(){{
  ballX=150;ballY=100;
  ballDX=(Math.random()>0.5?{bx}:-{bx});
  ballDY=(Math.random()>0.5?{by}:-{by});
  if(playerScore>=5||cpuScore>=5){{
    running=false;clearInterval(gameInterval);
    ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,200);
    ctx.fillStyle=playerScore>=5?"{theme['primary']}":"{theme['accent']}";
    ctx.font="bold 16px Courier New";ctx.textAlign="center";
    ctx.fillText(playerScore>=5?"YOU WIN!":"CPU WINS",150,100);
  }}
}}
function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,200);
  ctx.fillStyle='{theme['secondary']}';
  ctx.fillRect(5,playerY,10,40);ctx.fillRect(285,cpuY,10,40);
  ctx.fillStyle='{theme['accent']}';
  ctx.beginPath();ctx.arc(ballX,ballY,5,0,Math.PI*2);ctx.fill();
}}
startBtn.onclick=()=>{{
  playerScore=0;cpuScore=0;playerY=70;cpuY=70;running=true;resetBall();
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.onmousemove=e=>{{
  const rect=canvas.getBoundingClientRect();
  playerY=Math.max(0,Math.min(160,e.clientY-rect.top-20));draw();
}};
</script></body></html>"""


def _build_flappy(theme: dict, speed: float, speed_label: str) -> str:
    pipe_speed = round(2 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Flappy</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}
.grid-bg{{background-size:20px 24px;background-image:radial-gradient(circle,{theme['gridColor']} 1px,transparent 1px)}}</style>
</head>
<body class="grid-bg text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-4">
    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{theme['name']}</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">TAP CANVAS TO FLY</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let birdY=150,velocity=0,score=0,running=false,gameInterval,pipes=[];
function update(){{
  if(!running)return;
  velocity+=0.25;birdY+=velocity;
  if(birdY>=290||birdY<=5){{gameOver();return;}}
  if(!pipes.length||pipes[pipes.length-1].x<180)
    pipes.push({{x:300,top:Math.random()*100+40,bottom:Math.random()*100+40}});
  pipes.forEach(p=>{{
    p.x-={pipe_speed};
    if(p.x===50){{score++;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');}}
    if(p.x<75&&p.x>35&&(birdY<p.top||birdY>300-p.bottom)){{gameOver();return;}}
  }});
  pipes=pipes.filter(p=>p.x>-30);
  draw();
}}
function gameOver(){{
  running=false;clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="{theme['accent']}";ctx.font="bold 20px Courier New";ctx.textAlign="center";
  ctx.fillText("CRASHED!",150,140);
}}
function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme['accent']}';ctx.beginPath();ctx.arc(60,birdY,8,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{theme['primary']}';
  pipes.forEach(p=>{{ctx.fillRect(p.x,0,20,p.top);ctx.fillRect(p.x,300-p.bottom,20,p.bottom);}});
}}
function start(){{
  birdY=150;velocity=0;score=0;pipes=[];running=true;
  scoreEl.innerText="SCORE: 000";
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,20);
}}
startBtn.onclick=start;
canvas.onclick=()=>{{velocity=-5.5;}};
</script></body></html>"""


def _build_brickbreaker(theme: dict, speed: float, speed_label: str) -> str:
    bx = round(2 * speed * 100) / 100
    by = round(-2 * speed * 100) / 100
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Brickbreaker</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}
.grid-bg{{background-size:20px 20px;background-image:radial-gradient(circle,{theme['gridColor']} 1px,transparent 1px)}}</style>
</head>
<body class="grid-bg text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{theme['name']}</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">START BRICKS</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let score=0,paddleX=120,ballX=150,ballY=240,ballDX={bx},ballDY={by};
let running=false,gameInterval,bricks=[];
function initBricks(){{
  bricks=[];
  for(let r=0;r<4;r++)for(let c=0;c<6;c++)
    bricks.push({{x:c*46+14,y:r*16+30,active:true}});
}}
function update(){{
  if(!running)return;
  ballX+=ballDX;ballY+=ballDY;
  if(ballX<=5||ballX>=295)ballDX=-ballDX;
  if(ballY<=5)ballDY=-ballDY;
  if(ballY>=295)return gameOver();
  if(ballY>=270&&ballY<=278&&ballX>=paddleX&&ballX<=paddleX+60){{
    ballDY=-Math.abs(ballDY);ballDX=(ballX-(paddleX+30))*0.15;
  }}
  bricks.forEach(b=>{{
    if(b.active&&ballX>=b.x&&ballX<=b.x+42&&ballY>=b.y&&ballY<=b.y+12){{
      b.active=false;ballDY=-ballDY;score+=10;
      scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');
    }}
  }});
  if(bricks.every(b=>!b.active)){{
    running=false;clearInterval(gameInterval);
    ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
    ctx.fillStyle="{theme['primary']}";ctx.font="bold 20px Courier New";ctx.textAlign="center";
    ctx.fillText("YOU WIN!",150,150);
  }}
  draw();
}}
function gameOver(){{
  running=false;clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="{theme['accent']}";ctx.font="bold 20px Courier New";ctx.textAlign="center";
  ctx.fillText("GAME OVER",150,150);
}}
function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme['secondary']}';ctx.fillRect(paddleX,275,60,10);
  ctx.fillStyle='{theme['accent']}';ctx.beginPath();ctx.arc(ballX,ballY,5,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='{theme['primary']}';
  bricks.forEach(b=>{{if(b.active)ctx.fillRect(b.x,b.y,42,12);}});
}}
startBtn.onclick=()=>{{
  score=0;scoreEl.innerText='SCORE: 000';ballX=150;ballY=240;paddleX=120;
  ballDX={bx};ballDY={by};initBricks();running=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.onmousemove=e=>{{
  const rect=canvas.getBoundingClientRect();
  paddleX=Math.max(0,Math.min(240,e.clientX-rect.left-30));draw();
}};
</script></body></html>"""


def _build_clicker(theme: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>{theme['name']} Clicker</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{{background-color:{theme['bg']}}}
.grid-bg{{background-size:24px 24px;background-image:radial-gradient(circle,{theme['gridColor']} 1px,transparent 1px)}}</style>
</head>
<body class="grid-bg text-slate-100 min-h-screen flex items-center justify-center p-4">
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
const clickBtn=document.getElementById('clickBtn');
const buyCl=document.getElementById('buyClicker'),buyMu=document.getElementById('buyMultiplier');
const clCostEl=document.getElementById('clickerCost'),muCostEl=document.getElementById('multiCost');
function ui(){{pts.innerText=points;cpsEl.innerText=cps;clCostEl.innerText=clickerCost;muCostEl.innerText=multiplierCost;}}
clickBtn.onclick=()=>{{points+=clickPower;ui();}};
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
<style>body{{background-color:{theme['bg']}}}
.grid-bg{{background-size:20px 24px;background-image:radial-gradient(circle,{theme['gridColor']} 1px,transparent 1px)}}</style>
</head>
<body class="grid-bg text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-slate-700/50 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-3 text-xs font-mono">
    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{theme['name']} Space</span>
    <span id="score" style="color:{theme['primary']}">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-slate-800"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 rounded-xl text-xs font-bold" style="background-color:{theme['primary']}">LAUNCH FIGHTER</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let score=0,playerX=135,lasers=[],aliens=[],running=false,gameInterval,alienDir=1;
function spawnAliens(){{
  aliens=[];
  for(let r=0;r<3;r++)for(let c=0;c<6;c++)
    aliens.push({{x:c*40+30,y:r*30+30,active:true}});
}}
function update(){{
  if(!running)return;
  lasers.forEach(l=>l.y-=4);lasers=lasers.filter(l=>l.y>0);
  let edgeHit=false;
  aliens.forEach(a=>{{if(a.active){{a.x+=alienDir*{alien_speed};if(a.x>=280||a.x<=10)edgeHit=true;}}}});
  if(edgeHit){{alienDir=-alienDir;aliens.forEach(a=>{{if(a.active)a.y+=10;}});}}
  lasers.forEach(l=>{{
    aliens.forEach(a=>{{
      if(a.active&&l.y<=a.y+15&&l.y>=a.y&&l.x>=a.x&&l.x<=a.x+15){{
        a.active=false;l.y=-100;score+=10;
        scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');
      }}
    }});
  }});
  if(aliens.every(a=>!a.active))spawnAliens();
  draw();
}}
function draw(){{
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='{theme['primary']}';ctx.fillRect(playerX,275,30,15);
  ctx.fillStyle='{theme['accent']}';lasers.forEach(l=>ctx.fillRect(l.x,l.y,4,10));
  ctx.fillStyle='{theme['secondary']}';aliens.forEach(a=>{{if(a.active)ctx.fillRect(a.x,a.y,15,15);}});
}}
startBtn.onclick=()=>{{
  score=0;scoreEl.innerText='SCORE: 000';lasers=[];playerX=135;alienDir=1;
  spawnAliens();running=true;
  if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,16);
}};
window.onkeydown=e=>{{
  if(e.key==='ArrowLeft'||e.key==='a')playerX=Math.max(0,playerX-15);
  if(e.key==='ArrowRight'||e.key==='d')playerX=Math.min(270,playerX+15);
  if(e.key===' '||e.key==='Enter')lasers.push({{x:playerX+13,y:270}});
}};
</script></body></html>"""


def compile_game(query: str) -> dict:
    q = query.lower()
    genre = _detect_genre(q)
    theme = _detect_theme(q)
    speed, speed_label = _detect_speed(q)
    title = f"Custom {theme['name']} {genre.upper()}"

    if genre == "snake":
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
    else:
        code = _build_snake(theme, speed, speed_label, q)

    return {"title": title, "desc": f"Custom compiled {genre} game.", "code": code}
