GAME_TEMPLATES: dict[str, dict] = {
    "snake": {
        "title": "Classic Neon Snake Arena",
        "desc": "Retro arcade snake with high-contrast direction queues and keyboard controls.",
        "code": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Arcade Snake</title><script src="https://cdn.tailwindcss.com"></script>
<style>body{background-color:#020617}.grid-bg{background-size:20px 24px;background-image:radial-gradient(circle,rgba(16,185,129,0.1) 1px,transparent 1px)}</style>
</head><body class="grid-bg text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-emerald-500/30 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-4">
    <span class="text-xs font-mono text-emerald-400">ARCADE CORE</span>
    <span id="score" class="font-mono text-emerald-400">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-emerald-500/20"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-xs font-bold transition">START GAME</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
const grid=15;let score=0,dx=grid,dy=0,snake,food,gameInterval;
function randPos(){return Math.floor(Math.random()*(300/grid))*grid;}
function spawnFood(){food={x:randPos(),y:randPos()};if(snake.some(p=>p.x===food.x&&p.y===food.y))spawnFood();}
function update(){
  const head={x:snake[0].x+dx,y:snake[0].y+dy};
  if(head.x<0||head.x>=300||head.y<0||head.y>=300||snake.some(p=>p.x===head.x&&p.y===head.y)){
    clearInterval(gameInterval);ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
    ctx.fillStyle="#ef4444";ctx.font="bold 20px Courier New";ctx.textAlign="center";ctx.fillText("GAME OVER",150,140);return;
  }
  snake.unshift(head);
  if(head.x===food.x&&head.y===food.y){score+=10;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');spawnFood();}
  else snake.pop();
  draw();
}
function draw(){
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='#ef4444';ctx.fillRect(food.x,food.y,grid,grid);
  snake.forEach((p,i)=>{ctx.fillStyle=i===0?'#10b981':'#059669';ctx.fillRect(p.x,p.y,grid,grid);});
}
startBtn.onclick=()=>{
  score=0;scoreEl.innerText='SCORE: 000';
  snake=[{x:120,y:120},{x:105,y:120},{x:90,y:120}];
  dx=grid;dy=0;spawnFood();if(gameInterval)clearInterval(gameInterval);
  gameInterval=setInterval(update,120);
};
window.onkeydown=e=>{
  if((e.key==='ArrowUp'||e.key==='w')&&dy===0){dx=0;dy=-grid;}
  if((e.key==='ArrowDown'||e.key==='s')&&dy===0){dx=0;dy=grid;}
  if((e.key==='ArrowLeft'||e.key==='a')&&dx===0){dx=-grid;dy=0;}
  if((e.key==='ArrowRight'||e.key==='d')&&dx===0){dx=grid;dy=0;}
};
</script></body></html>""",
    },
    "pong": {
        "title": "Classic Retro Pong Match",
        "desc": "Double-paddle physics with collision detection and smart CPU opponent.",
        "code": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Arcade Pong</title><script src="https://cdn.tailwindcss.com"></script>
<style>body{background-color:#020617}.grid-bg{background-size:20px 20px;background-image:radial-gradient(circle,rgba(99,102,241,0.1) 1px,transparent 1px)}</style>
</head><body class="grid-bg text-white min-h-screen flex items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-indigo-500/30 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-4">
    <span class="text-xs font-mono text-indigo-400">PONG MASTER</span>
    <span id="score" class="font-mono text-indigo-400">YOU: 0 | CPU: 0</span>
  </div>
  <canvas id="gameCanvas" width="300" height="200" class="bg-slate-950 rounded-xl border border-indigo-500/20"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-bold transition">START MATCH</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let playerY=70,cpuY=70,ballX=150,ballY=100,ballDX=2,ballDY=1.5;
let playerScore=0,cpuScore=0,running=false,gameInterval;
function update(){
  if(!running)return;
  ballX+=ballDX;ballY+=ballDY;
  if(cpuY+15<ballY)cpuY+=1.8;else if(cpuY+15>ballY)cpuY-=1.8;
  if(ballY<=0||ballY>=200)ballDY=-ballDY;
  if(ballX<=15&&ballY>=playerY&&ballY<=playerY+40){ballDX=-ballDX*1.05;ballX=16;}
  if(ballX>=285&&ballY>=cpuY&&ballY<=cpuY+40){ballDX=-ballDX*1.05;ballX=284;}
  if(ballX<0){cpuScore++;resetBall();}
  if(ballX>300){playerScore++;resetBall();}
  scoreEl.innerText="YOU: "+playerScore+" | CPU: "+cpuScore;draw();
}
function resetBall(){
  ballX=150;ballY=100;ballDX=(Math.random()>0.5?2:-2);ballDY=(Math.random()>0.5?1.5:-1.5);
  if(playerScore>=5||cpuScore>=5){
    running=false;clearInterval(gameInterval);
    ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,200);
    ctx.fillStyle=playerScore>=5?"#10b981":"#ef4444";
    ctx.font="bold 16px Courier New";ctx.textAlign="center";
    ctx.fillText(playerScore>=5?"YOU WIN!":"CPU WINS",150,100);
  }
}
function draw(){
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,200);
  ctx.fillStyle='#ffffff';ctx.fillRect(5,playerY,10,40);ctx.fillRect(285,cpuY,10,40);
  ctx.beginPath();ctx.arc(ballX,ballY,5,0,Math.PI*2);ctx.fill();
}
startBtn.onclick=()=>{
  playerScore=0;cpuScore=0;playerY=70;cpuY=70;running=true;resetBall();
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,16);
};
window.onmousemove=e=>{
  const rect=canvas.getBoundingClientRect();playerY=Math.max(0,Math.min(160,e.clientY-rect.top-20));draw();
};
</script></body></html>""",
    },
    "tictactoe": {
        "title": "Cyber Grid Tic-Tac-Toe",
        "desc": "Procedural grid rendering with single-player CPU opponent.",
        "code": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Tic-Tac-Toe</title><script src="https://cdn.tailwindcss.com"></script>
<style>body{background-color:#020617}.grid-bg{background-size:20px 20px;background-image:radial-gradient(circle,rgba(168,85,247,0.1) 1px,transparent 1px)}</style>
</head><body class="grid-bg text-white min-h-screen flex items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-purple-500/30 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <span class="text-xs font-mono text-purple-400 mb-4 tracking-widest uppercase">CYBER GRID INITIATED</span>
  <div class="grid grid-cols-3 gap-3 w-full" id="board">
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(0)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(1)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(2)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(3)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(4)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(5)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(6)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(7)"></button>
    <button class="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition" onclick="makeMove(8)"></button>
  </div>
  <div id="status" class="mt-4 text-xs font-mono text-purple-300">YOUR TURN (X)</div>
  <button id="resetBtn" class="mt-4 w-full py-2 bg-purple-600 hover:bg-purple-500 rounded-xl text-xs font-bold transition">RESET GRID</button>
</div>
<script>
let board=["","","","","","","","",""],active=true;
const cells=document.querySelectorAll(".cell"),statusEl=document.getElementById("status");
function makeMove(idx){
  if(board[idx]!==""||!active)return;
  board[idx]="X";cells[idx].innerText="X";
  if(checkWin("X")){endGame("YOU WIN!");return;}
  if(!board.includes("")){endGame("IT'S A DRAW!");return;}
  active=false;statusEl.innerText="CPU COMPUTING...";setTimeout(cpuMove,300);
}
function cpuMove(){
  let av=board.map((c,i)=>c===""?i:null).filter(c=>c!==null);
  if(av.length>0){
    let chosen=av[Math.floor(Math.random()*av.length)];
    board[chosen]="O";cells[chosen].innerText="O";cells[chosen].classList.add("text-emerald-400");
    if(checkWin("O")){endGame("CPU WINS!");return;}
    if(!board.includes("")){endGame("IT'S A DRAW!");return;}
  }
  active=true;statusEl.innerText="YOUR TURN (X)";
}
function checkWin(p){
  return[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]].some(c=>c.every(i=>board[i]===p));
}
function endGame(msg){active=false;statusEl.innerText=msg;}
document.getElementById("resetBtn").onclick=()=>{
  board=["","","","","","","","",""];active=true;statusEl.innerText="YOUR TURN (X)";
  cells.forEach(c=>{c.innerText="";c.className="cell h-20 bg-slate-950 border border-purple-500/20 hover:border-purple-500/50 rounded-xl font-bold text-2xl text-purple-400 transition";});
};
</script></body></html>""",
    },
    "flappy": {
        "title": "Retro Flappy Bird Flight",
        "desc": "Physics-driven kinetic loops with gravity, collision, and tap controls.",
        "code": """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Arcade Flappy</title><script src="https://cdn.tailwindcss.com"></script>
<style>body{background-color:#020617}.grid-bg{background-size:20px 24px;background-image:radial-gradient(circle,rgba(245,158,11,0.1) 1px,transparent 1px)}</style>
</head><body class="grid-bg text-white min-h-screen flex flex-col items-center justify-center p-4">
<div class="bg-slate-900 border-2 border-amber-500/30 rounded-2xl p-6 shadow-2xl flex flex-col items-center w-full max-w-sm">
  <div class="flex justify-between w-full mb-4">
    <span class="text-xs font-mono text-amber-400">FLIGHT ENG</span>
    <span id="score" class="font-mono text-amber-400">SCORE: 000</span>
  </div>
  <canvas id="gameCanvas" width="300" height="300" class="bg-slate-950 rounded-xl border border-amber-500/20"></canvas>
  <button id="startBtn" class="mt-4 w-full py-2.5 bg-amber-600 hover:bg-amber-500 rounded-xl text-xs font-bold transition">TAP CANVAS TO FLY</button>
</div>
<script>
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const scoreEl=document.getElementById('score'),startBtn=document.getElementById('startBtn');
let birdY=150,velocity=0,score=0,running=false,gameInterval,pipes=[];
function update(){
  if(!running)return;
  velocity+=0.25;birdY+=velocity;
  if(birdY>=290||birdY<=5){gameOver();return;}
  if(!pipes.length||pipes[pipes.length-1].x<180)
    pipes.push({x:300,top:Math.random()*100+40,bottom:Math.random()*100+40});
  pipes.forEach(p=>{
    p.x-=2;
    if(p.x===50){score++;scoreEl.innerText="SCORE: "+score.toString().padStart(3,'0');}
    if(p.x<75&&p.x>35&&(birdY<p.top||birdY>300-p.bottom)){gameOver();return;}
  });
  pipes=pipes.filter(p=>p.x>-30);draw();
}
function gameOver(){
  running=false;clearInterval(gameInterval);
  ctx.fillStyle="rgba(2,6,23,0.85)";ctx.fillRect(0,0,300,300);
  ctx.fillStyle="#ef4444";ctx.font="bold 20px Courier New";ctx.textAlign="center";ctx.fillText("CRASHED!",150,140);
}
function draw(){
  ctx.fillStyle='#020617';ctx.fillRect(0,0,300,300);
  ctx.fillStyle='#eab308';ctx.beginPath();ctx.arc(60,birdY,8,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#10b981';
  pipes.forEach(p=>{ctx.fillRect(p.x,0,20,p.top);ctx.fillRect(p.x,300-p.bottom,20,p.bottom);});
}
function start(){
  birdY=150;velocity=0;score=0;pipes=[];running=true;scoreEl.innerText="SCORE: 000";
  if(gameInterval)clearInterval(gameInterval);gameInterval=setInterval(update,20);
}
startBtn.onclick=start;canvas.onclick=()=>{velocity=-5.5;};
</script></body></html>""",
    },
}
