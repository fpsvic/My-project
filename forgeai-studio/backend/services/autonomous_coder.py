"""
Autonomous Code Synthesis — ForgeAI writes original code from scratch.

No template copying. Parses intent → builds a blueprint → composes HTML/CSS/JS
from atomic logic blocks based on what the user actually asked for.
"""

from __future__ import annotations

import re
import random
from dataclasses import dataclass, field


# ── Theme palettes (generated per project, not copied from game files) ─────────

_PALETTES = [
    {"bg": "#0f172a", "surface": "#1e293b", "primary": "#6366f1", "accent": "#ec4899", "text": "#e2e8f0", "muted": "#94a3b8"},
    {"bg": "#022c22", "surface": "#064e3b", "primary": "#10b981", "accent": "#f59e0b", "text": "#ecfdf5", "muted": "#6ee7b7"},
    {"bg": "#0c2540", "surface": "#0f3460", "primary": "#38bdf8", "accent": "#f43f5e", "text": "#f0f9ff", "muted": "#7dd3fc"},
    {"bg": "#1c0d02", "surface": "#431407", "primary": "#f97316", "accent": "#e11d48", "text": "#fff7ed", "muted": "#fdba74"},
    {"bg": "#0f0728", "surface": "#1e1254", "primary": "#a78bfa", "accent": "#f472b6", "text": "#f5f3ff", "muted": "#c4b5fd"},
    {"bg": "#f8fafc", "surface": "#ffffff", "primary": "#4f46e5", "accent": "#db2777", "text": "#1e293b", "muted": "#64748b"},
]


def _pick_theme(q: str) -> dict:
    if any(w in q for w in ("light", "white", "clean", "minimal")):
        return _PALETTES[5]
    if any(w in q for w in ("green", "forest", "nature")):
        return _PALETTES[1]
    if any(w in q for w in ("ocean", "blue", "water", "sea")):
        return _PALETTES[2]
    if any(w in q for w in ("fire", "lava", "orange", "red")):
        return _PALETTES[3]
    if any(w in q for w in ("purple", "galaxy", "space", "cosmic")):
        return _PALETTES[4]
    return random.choice(_PALETTES[:4])


# ── Blueprint ────────────────────────────────────────────────────────────────

@dataclass
class CodeBlueprint:
    title: str
    kind: str  # game | app | tool
    raw_query: str
    mechanics: list[str] = field(default_factory=list)
    player: dict = field(default_factory=dict)
    collectibles: list[dict] = field(default_factory=list)
    enemies: list[dict] = field(default_factory=list)
    ui_panels: list[str] = field(default_factory=list)
    app_features: list[str] = field(default_factory=list)
    data_fields: list[dict] = field(default_factory=list)
    theme: dict = field(default_factory=dict)
    canvas: bool = False
    has_score: bool = True
    has_lives: bool = True
    has_timer: bool = False
    gravity: bool = False
    shooting: bool = False


_PLAYER_HINTS = [
    (["wizard", "mage"], "wizard", "🧙", "#a78bfa"),
    (["knight", "warrior"], "knight", "⚔️", "#fbbf24"),
    (["ship", "rocket", "spaceship"], "ship", "🚀", "#60a5fa"),
    (["bird", "flappy"], "bird", "🐦", "#fbbf24"),
    (["frog"], "frog", "🐸", "#4ade80"),
    (["robot"], "robot", "🤖", "#94a3b8"),
    (["car", "racer"], "car", "🏎️", "#f97316"),
    (["ninja"], "ninja", "🥷", "#64748b"),
    (["dragon"], "dragon", "🐉", "#ef4444"),
    (["ball", "orb"], "ball", "⚪", "#e2e8f0"),
    (["cat", "kitten"], "cat", "🐱", "#fb923c"),
    (["dog", "puppy"], "dog", "🐶", "#f59e0b"),
]

_COLLECT_HINTS = [
    (["coin", "gold"], "coin", "🪙"),
    (["gem", "diamond"], "gem", "💎"),
    (["star"], "star", "⭐"),
    (["fruit", "apple"], "fruit", "🍎"),
    (["crystal"], "crystal", "🔷"),
    (["heart", "health"], "heart", "❤️"),
    (["key"], "key", "🔑"),
]

_ENEMY_HINTS = [
    (["zombie"], "zombie", "🧟"),
    (["alien"], "alien", "👽"),
    (["ghost"], "ghost", "👻"),
    (["monster"], "monster", "👾"),
    (["asteroid", "rock"], "rock", "🪨"),
    (["spike"], "spike", "🔺"),
    (["enemy"], "foe", "👿"),
]


def _match_hint(q: str, hints: list, default: tuple) -> dict:
    for keywords, name, *rest in hints:
        if any(k in q for k in keywords):
            if len(rest) == 2:
                return {"name": name, "emoji": rest[0], "color": rest[1]}
            return {"name": name, "emoji": rest[0]}
    if len(default) == 3:
        return {"name": default[0], "emoji": default[1], "color": default[2]}
    return {"name": default[0], "emoji": default[1]}


def _extract_title(q: str, kind: str) -> str:
    q = q.strip()
    m = re.search(
        r"(?:make|build|create|code|write|generate|develop|design|give me|i want)\s+"
        r"(?:me\s+)?(?:a\s+|an\s+)?(.+)",
        q, re.I,
    )
    subject = (m.group(1) if m else q)[:48].strip()
    subject = re.sub(r"\s+(game|app|tool|project)$", "", subject, flags=re.I).strip()
    if not subject:
        subject = "Custom Game" if kind == "game" else "Custom App"
    return subject.title()


def parse_blueprint(query: str) -> CodeBlueprint:
    """Turn natural language into a generation blueprint — no templates involved."""
    q = query.lower()
    is_game = any(w in q for w in (
        "game", "playable", "arcade", "shooter", "platformer", "snake", "pong",
        "runner", "survival", "dungeon", "level", "boss", "enemy", "enemies",
    ))
    is_app = any(w in q for w in (
        "app", "tool", "calculator", "todo", "dashboard", "tracker", "converter",
        "generator", "manager", "form", "widget", "utility",
    ))
    kind = "game" if is_game and not (is_app and not is_game) else ("app" if is_app else "game")

    bp = CodeBlueprint(
        title=_extract_title(query, kind),
        kind=kind,
        raw_query=query,
        theme=_pick_theme(q),
        player=_match_hint(q, _PLAYER_HINTS, ("hero", "🟦", "#6366f1")),
    )

    if kind == "game":
        bp.canvas = True
        mechanics: list[str] = ["move", "score"]

        if "snake" in q:
            mechanics = ["move", "score", "snake_tail", "collect"]
            bp.collectibles.append({"name": "food", "emoji": "🍎"})
        elif "pong" in q:
            mechanics = ["move", "score", "paddle", "ball"]
        elif any(w in q for w in ("shoot", "fire", "blast", "laser", "bullet", "missile", "arrow", "fireball")):
            mechanics += ["shoot"]
            bp.shooting = True
        if any(w in q for w in ("collect", "pickup", "gather", "grab", "coin", "gem", "star")):
            mechanics.append("collect")
            bp.collectibles.append(_match_hint(q, _COLLECT_HINTS, ("item", "⭐")))
        if any(w in q for w in ("avoid", "dodge", "obstacle", "enemy", "enemies", "survive")):
            mechanics.append("avoid")
            bp.enemies.append(_match_hint(q, _ENEMY_HINTS, ("hazard", "💥")))
        if any(w in q for w in ("jump", "platform", "gravity", "mario")):
            mechanics += ["jump", "gravity"]
            bp.gravity = True
        if any(w in q for w in ("timer", "countdown", "timed", "seconds")):
            bp.has_timer = True
            mechanics.append("timer")
        if any(w in q for w in ("life", "lives", "heart")):
            bp.has_lives = True
        else:
            bp.has_lives = "avoid" in mechanics or "shoot" in mechanics

        if not bp.collectibles and "collect" not in mechanics:
            if random.random() < 0.6:
                mechanics.append("collect")
                bp.collectibles.append(_match_hint(q, _COLLECT_HINTS, ("star", "⭐")))
        if not bp.enemies and bp.shooting:
            bp.enemies.append(_match_hint(q, _ENEMY_HINTS, ("foe", "👾")))

        bp.mechanics = list(dict.fromkeys(mechanics))
        bp.ui_panels = ["score"]
        if bp.has_lives:
            bp.ui_panels.append("lives")
        if bp.has_timer:
            bp.ui_panels.append("timer")
    else:
        bp.canvas = any(w in q for w in ("draw", "paint", "canvas", "sketch", "chart", "graph"))
        features: list[str] = []
        if any(w in q for w in ("add", "create", "new", "submit", "save")):
            features.append("create")
        if any(w in q for w in ("delete", "remove", "clear")):
            features.append("delete")
        if any(w in q for w in ("edit", "update", "modify")):
            features.append("edit")
        if any(w in q for w in ("list", "todo", "task", "item", "inventory", "record")):
            features.append("list")
        if any(w in q for w in ("filter", "search", "find")):
            features.append("filter")
        if any(w in q for w in ("calc", "calculate", "convert", "compute")):
            features.append("calculate")
        if any(w in q for w in ("random", "generate", "roll", "pick")):
            features.append("random")
        if any(w in q for w in ("timer", "countdown", "stopwatch", "clock")):
            features.append("timer")
        if any(w in q for w in ("chart", "graph", "stat", "analytics")):
            features.append("chart")
        if not features:
            features = ["create", "list"]
        bp.app_features = features

        if "calculate" in features:
            bp.data_fields = [
                {"id": "inputA", "label": "Value A", "type": "number"},
                {"id": "inputB", "label": "Value B", "type": "number"},
            ]
        elif "list" in features:
            bp.data_fields = [{"id": "itemInput", "label": "New item", "type": "text"}]
        else:
            bp.data_fields = [{"id": "mainInput", "label": "Input", "type": "text"}]

        bp.ui_panels = ["header", "main", "actions"]

    return bp


# ── Game code composition ────────────────────────────────────────────────────

def _compose_game_js(bp: CodeBlueprint) -> str:
    t = bp.theme
    p = bp.player
    coll = bp.collectibles[0] if bp.collectibles else {"emoji": "⭐", "name": "star"}
    enemy = bp.enemies[0] if bp.enemies else {"emoji": "👾", "name": "foe"}
    mech = set(bp.mechanics)

    shoot_block = ""
    if "shoot" in mech:
        shoot_block = """
function tryShoot(){
  if(shootCd>0)return;
  bullets.push({x:player.x+14,y:player.y,vy:-9});
  shootCd=10;
}
function updateBullets(){
  bullets.forEach(b=>{b.y+=b.vy;});
  bullets=bullets.filter(b=>b.y>-20);
}
function drawBullets(){
  ctx.fillStyle=ACCENT;
  bullets.forEach(b=>{ctx.fillRect(b.x,b.y,4,10);});
}
"""

    collect_block = """
let spawnCd=0;
function spawnPickup(){
  if(spawnCd>0){spawnCd--;return;}
  pickups.push({x:20+Math.random()*(W-40),y:-16,vy:1.8+Math.random(),size:14});
  spawnCd=45;
}
function updatePickups(){
  pickups.forEach(p=>{p.y+=p.vy;});
  pickups=pickups.filter(p=>p.y<H+20);
}
function checkPickups(){
  pickups=pickups.filter(pk=>{
    if(Math.hypot(pk.x-player.x,pk.y-player.y)<22){
      score+=10;document.getElementById('score').textContent=score;return false;
    }
    return true;
  });
}
function drawPickups(){
  ctx.font='18px serif';ctx.textAlign='center';
  pickups.forEach(pk=>{ctx.fillText(COLL_EMOJI,pk.x,pk.y);});
}
""" if "collect" in mech else ""

    avoid_block = """
let hazardCd=0;
function spawnHazard(){
  if(hazardCd>0){hazardCd--;return;}
  hazards.push({x:20+Math.random()*(W-40),y:-20,vy:1.5+level*0.1,size:16});
  hazardCd=55;
}
function updateHazards(){
  hazards.forEach(h=>{h.y+=h.vy;});
  hazards=hazards.filter(h=>h.y<H+20);
}
function checkHazards(){
  hazards.forEach((h,i)=>{
    if(Math.hypot(h.x-player.x,h.y-player.y)<20){
      hazards.splice(i,1);lives--;document.getElementById('lives').textContent=lives;
      if(lives<=0)endGame();
    }
  });
}
function drawHazards(){
  ctx.font='20px serif';ctx.textAlign='center';
  hazards.forEach(h=>{ctx.fillText(ENEMY_EMOJI,h.x,h.y);});
}
""" if "avoid" in mech or "shoot" in mech else ""

    gravity_block = """
let vy=0; const GRAV=0.45, JUMP=-9;
function applyGravity(){
  vy+=GRAV; player.y+=vy;
  if(player.y>H-32){player.y=H-32;vy=0;onGround=true;} else onGround=false;
}
""" if "gravity" in mech else "let onGround=true;"

    jump_handler = """
  if((keys['ArrowUp']||keys['w']||keys[' '])&&onGround){vy=JUMP;onGround=false;}
""" if "gravity" in mech else ""

    timer_block = """
let timeLeft=60;
function tickTimer(){
  if(frame%60===0){timeLeft--;document.getElementById('timer').textContent=timeLeft+'s';
    if(timeLeft<=0)endGame();}
}
""" if bp.has_timer else ""

    snake_block = """
let snake=[{x:200,y:240},{x:184,y:240},{x:168,y:240}],dir={x:1,y:0},food={x:100,y:100},tick=0;
function spawnFood(){
  food={x:20+Math.floor(Math.random()*18)*20,y:20+Math.floor(Math.random()*22)*20};
}
function updateSnake(){
  tick++; if(tick%8!==0)return;
  const head={x:snake[0].x+dir.x*16,y:snake[0].y+dir.y*16};
  if(head.x<0||head.y<0||head.x>=W||head.y>=H||snake.some(s=>s.x===head.x&&s.y===head.y)){endGame();return;}
  snake.unshift(head);
  if(head.x===food.x&&head.y===food.y){score+=10;document.getElementById('score').textContent=score;spawnFood();}
  else snake.pop();
}
function drawSnake(){
  ctx.fillStyle=PRIMARY;
  snake.forEach((s,i)=>{ctx.fillRect(s.x,s.y,14,14);});
  ctx.font='16px serif';ctx.fillText(COLL_EMOJI,food.x,food.y+14);
}
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowUp'&&dir.y!==1)dir={x:0,y:-1};
  if(e.key==='ArrowDown'&&dir.y!==-1)dir={x:0,y:1};
  if(e.key==='ArrowLeft'&&dir.x!==1)dir={x:-1,y:0};
  if(e.key==='ArrowRight'&&dir.x!==-1)dir={x:1,y:0};
},true);
""" if "snake_tail" in mech else ""

    return f"""
const canvas=document.getElementById('game');
const ctx=canvas.getContext('2d');
const W=canvas.width,H=canvas.height;
const PRIMARY='{t["primary"]}',ACCENT='{t["accent"]}',BG='{t["bg"]}';
const PLAYER_EMOJI='{p["emoji"]}',COLL_EMOJI='{coll["emoji"]}',ENEMY_EMOJI='{enemy["emoji"]}';
let running=false,frame=0,score=0,lives={3 if bp.has_lives else 1},level=1;
let player={{x:W/2-16,y:H-48,w:32,h:32,speed:4}};
let keys={{}},bullets=[],pickups=[],hazards=[];
let shootCd=0;
{gravity_block}
{shoot_block}
{collect_block}
{avoid_block}
{timer_block}
{snake_block}

function handleInput(){{
  if(keys['ArrowLeft']||keys['a'])player.x=Math.max(8,player.x-player.speed);
  if(keys['ArrowRight']||keys['d'])player.x=Math.min(W-40,player.x+player.speed);
  {jump_handler}
  {'if(keys[" "]||keys["ArrowUp"])tryShoot();' if "shoot" in mech else ''}
}}

function drawPlayer(){{
  ctx.font='28px serif';ctx.textAlign='center';
  ctx.fillText(PLAYER_EMOJI,player.x+16,player.y+26);
}}

function drawHud(){{
  ctx.fillStyle='rgba(0,0,0,0.35)';ctx.fillRect(0,0,W,28);
  ctx.fillStyle='{t["text"]}';ctx.font='12px sans-serif';ctx.textAlign='left';
  ctx.fillText('Score: '+score,10,18);
}}

function update(){{
  if(!running)return;
  frame++;
  {'updateSnake();render();return;' if "snake_tail" in mech else ''}
  handleInput();
  {'applyGravity();' if "gravity" in mech else ''}
  {'updateBullets();' if "shoot" in mech else ''}
  {'spawnPickup();updatePickups();checkPickups();' if "collect" in mech else ''}
  {'spawnHazard();updateHazards();checkHazards();' if "avoid" in mech or "shoot" in mech else ''}
  {'tickTimer();' if bp.has_timer else ''}
  if(shootCd>0)shootCd--;
  if(frame%600===0)level++;
  render();
}}

function render(){{
  ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);
  {'drawSnake();return;' if "snake_tail" in mech else ''}
  ctx.strokeStyle='rgba(255,255,255,0.04)';
  for(let i=0;i<W;i+=40){{ctx.beginPath();ctx.moveTo(i,0);ctx.lineTo(i,H);ctx.stroke();}}
  {'drawPickups();' if "collect" in mech else ''}
  {'drawHazards();' if "avoid" in mech or "shoot" in mech else ''}
  {'drawBullets();' if "shoot" in mech else ''}
  drawPlayer();
}}

function startGame(){{
  running=true;score=0;lives={3 if bp.has_lives else 1};frame=0;level=1;
  {'snake=[{x:200,y:240},{x:184,y:240},{x:168,y:240}];dir={x:1,y:0};spawnFood();' if "snake_tail" in mech else 'player.x=W/2-16;player.y=' + ('H-80' if "gravity" in mech else 'H-48') + ';'}
  bullets=[];pickups=[];hazards=[];
  document.getElementById('score').textContent='0';
  {'document.getElementById("lives").textContent=lives;' if bp.has_lives else ''}
  {'timeLeft=60;' if bp.has_timer else ''}
  document.getElementById('msg').textContent='';
  requestAnimationFrame(loop);
}}

function loop(){{
  update();
  if(running)requestAnimationFrame(loop);
}}

function endGame(){{
  running=false;
  ctx.fillStyle='rgba(0,0,0,0.75)';ctx.fillRect(0,0,W,H);
  ctx.fillStyle=PRIMARY;ctx.font='bold 22px sans-serif';ctx.textAlign='center';
  ctx.fillText('Game Over',W/2,H/2-10);
  ctx.fillStyle='{t["text"]}';ctx.font='14px sans-serif';
  ctx.fillText('Final score: '+score,W/2,H/2+18);
  document.getElementById('msg').textContent='Press Space to play again';
}}

document.addEventListener('keydown',e=>{{
  keys[e.key]=true;
  if(e.key===' '&& !running){{e.preventDefault();startGame();}}
}});
document.addEventListener('keyup',e=>{{keys[e.key]=false;}});
document.getElementById('startBtn').addEventListener('click',startGame);

ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);
ctx.fillStyle=PRIMARY;ctx.font='bold 18px sans-serif';ctx.textAlign='center';
ctx.fillText('{bp.title}',W/2,H/2-20);
ctx.font='32px serif';ctx.fillText(PLAYER_EMOJI,W/2,H/2+20);
"""


def _compose_game_html(bp: CodeBlueprint) -> str:
    t = bp.theme
    hud = f'<span id="score">0</span>'
    if bp.has_lives:
        hud += ' · Lives <span id="lives">3</span>'
    if bp.has_timer:
        hud += ' · <span id="timer">60s</span>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{bp.title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{t['bg']};color:{t['text']};font-family:Inter,system-ui,sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:1rem}}
.wrap{{background:{t['surface']};border:1px solid {t['primary']}33;border-radius:1rem;padding:1rem;box-shadow:0 8px 32px rgba(0,0,0,0.3)}}
.hud{{display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:0.5rem;color:{t['muted']}}}
canvas{{display:block;border-radius:0.5rem;border:1px solid {t['primary']}44}}
#msg{{text-align:center;font-size:0.8rem;margin-top:0.5rem;color:{t['muted']}}}
#startBtn{{margin-top:0.75rem;width:100%;padding:0.6rem;border:none;border-radius:0.5rem;background:{t['primary']};color:#fff;font-weight:600;cursor:pointer}}
#startBtn:hover{{opacity:0.9}}
</style></head>
<body>
<div class="wrap">
  <div class="hud"><strong>{bp.title}</strong><span>Score {hud}</span></div>
  <canvas id="game" width="400" height="480"></canvas>
  <p id="msg">Press Start or Space to play</p>
  <button id="startBtn">Start</button>
</div>
<script>
{_compose_game_js(bp)}
</script>
</body></html>"""


# ── App code composition ───────────────────────────────────────────────────────

def _compose_app_js(bp: CodeBlueprint) -> str:
    t = bp.theme
    feats = set(bp.app_features)
    lines: list[str] = [
        f"const state = {{ items: [], history: [] }};",
        "",
    ]

    if "list" in feats:
        lines += [
            "function renderList(){",
            "  const el=document.getElementById('itemList');",
            "  if(!el)return;",
            "  el.innerHTML=state.items.map((it,i)=>`",
            "    <li class='item'><span>${escapeHtml(it)}</span>",
            "    <button onclick='removeItem(${i})' class='btn-sm'>✕</button></li>`).join('')||'<li class=\"empty\">No items yet</li>';",
            "  document.getElementById('count').textContent=state.items.length;",
            "}",
            "function addItem(){",
            "  const inp=document.getElementById('itemInput');",
            "  const v=(inp?.value||'').trim();",
            "  if(!v)return;",
            "  state.items.unshift(v); inp.value=''; renderList();",
            "}",
            "function removeItem(i){ state.items.splice(i,1); renderList(); }",
            "",
        ]

    if "calculate" in feats:
        lines += [
            "function calculate(){",
            "  const a=parseFloat(document.getElementById('inputA')?.value)||0;",
            "  const b=parseFloat(document.getElementById('inputB')?.value)||0;",
            "  const op=document.getElementById('operator')?.value||'+';",
            "  let r=0;",
            "  if(op==='+')r=a+b; else if(op==='-')r=a-b; else if(op==='*')r=a*b; else if(op==='/')r=b?a/b:0; else if(op==='^')r=Math.pow(a,b);",
            "  document.getElementById('result').textContent=Number.isFinite(r)?r:'Error';",
            "}",
            "",
        ]

    if "random" in feats:
        lines += [
            "function randomize(){",
            "  const out=document.getElementById('randomOut');",
            "  if(out) out.textContent=Math.floor(Math.random()*1000);",
            "}",
            "",
        ]

    if "filter" in feats:
        lines += [
            "function applyFilter(){",
            "  const q=(document.getElementById('filterInput')?.value||'').toLowerCase();",
            "  document.querySelectorAll('#itemList .item').forEach(li=>{",
            "    li.style.display=li.textContent.toLowerCase().includes(q)?'':'none';",
            "  });",
            "}",
            "",
        ]

    if "timer" in feats:
        lines += [
            "let timerId=null,seconds=0;",
            "function toggleTimer(){",
            "  if(timerId){clearInterval(timerId);timerId=null;return;}",
            "  timerId=setInterval(()=>{seconds++;document.getElementById('timerOut').textContent=seconds+'s';},1000);",
            "}",
            "",
        ]

    lines += [
        "function escapeHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}",
        "document.addEventListener('DOMContentLoaded',()=>{",
    ]
    if "list" in feats:
        lines.append("  renderList();")
    lines += [
        "  document.getElementById('primaryBtn')?.addEventListener('click',()=>{",
    ]
    if "list" in feats:
        lines.append("    addItem();")
    elif "calculate" in feats:
        lines.append("    calculate();")
    elif "random" in feats:
        lines.append("    randomize();")
    else:
        lines.append("    alert('Action complete');")
    lines += ["  });", "});", ""]

    return "\n".join(lines)


def _compose_app_body(bp: CodeBlueprint) -> str:
    feats = set(bp.app_features)
    parts = [f'<header><h1>{bp.title}</h1><p class="sub">Built autonomously by ForgeAI</p></header>', '<main>']

    if "list" in feats:
        parts += [
            '<div class="card">',
            '<label for="itemInput">Add item</label>',
            '<div class="row"><input id="itemInput" type="text" placeholder="Type and add...">',
            '<button id="primaryBtn" class="btn">Add</button></div>',
            '<p class="meta"><span id="count">0</span> items</p>',
            '<ul id="itemList" class="list"></ul>',
            '</div>',
        ]
    elif "calculate" in feats:
        parts += [
            '<div class="card">',
            '<div class="row"><input id="inputA" type="number" placeholder="A">',
            '<select id="operator"><option>+</option><option>-</option><option>*</option><option>/</option><option>^</option></select>',
            '<input id="inputB" type="number" placeholder="B"></div>',
            '<button id="primaryBtn" class="btn">Calculate</button>',
            '<p class="result">Result: <strong id="result">—</strong></p>',
            '</div>',
        ]
    else:
        parts += [
            '<div class="card">',
            '<label for="mainInput">Input</label>',
            '<input id="mainInput" type="text" placeholder="Enter value...">',
            '<button id="primaryBtn" class="btn">Run</button>',
            '</div>',
        ]

    if "filter" in feats and "list" in feats:
        parts.insert(-1, '<input id="filterInput" type="search" placeholder="Filter..." oninput="applyFilter()">')
    if "random" in feats:
        parts.append('<div class="card"><button class="btn btn-ghost" onclick="randomize()">Randomize</button><p id="randomOut" class="result">—</p></div>')
    if "timer" in feats:
        parts.append('<div class="card"><button class="btn btn-ghost" onclick="toggleTimer()">Start Timer</button><p id="timerOut">0s</p></div>')

    parts.append('</main>')
    return "\n".join(parts)


def _compose_app_html(bp: CodeBlueprint) -> str:
    t = bp.theme
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{bp.title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{t['bg']};color:{t['text']};font-family:Inter,system-ui,sans-serif;min-height:100vh;padding:1.5rem}}
.app{{max-width:520px;margin:0 auto}}
header{{margin-bottom:1.25rem}}
h1{{font-size:1.35rem;font-weight:700}}
.sub{{color:{t['muted']};font-size:0.8rem;margin-top:0.25rem}}
.card{{background:{t['surface']};border:1px solid {t['primary']}33;border-radius:0.75rem;padding:1rem;margin-bottom:1rem}}
label{{display:block;font-size:0.75rem;color:{t['muted']};margin-bottom:0.35rem;font-weight:600}}
input,select{{width:100%;padding:0.55rem 0.75rem;border-radius:0.5rem;border:1px solid {t['muted']}44;background:{t['bg']};color:{t['text']};font-size:0.9rem}}
.row{{display:flex;gap:0.5rem;align-items:center;margin-bottom:0.75rem}}
.row input,.row select{{flex:1}}
.btn{{background:{t['primary']};color:#fff;border:none;padding:0.55rem 1rem;border-radius:0.5rem;font-weight:600;cursor:pointer;font-size:0.85rem}}
.btn:hover{{opacity:0.9}}
.btn-ghost{{background:transparent;border:1px solid {t['muted']}55;color:{t['text']}}}
.btn-sm{{background:transparent;border:none;color:{t['accent']};cursor:pointer;font-size:0.8rem}}
.list{{list-style:none;margin-top:0.75rem}}
.item{{display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid {t['muted']}22;font-size:0.9rem}}
.empty{{color:{t['muted']};font-size:0.85rem;padding:0.5rem 0}}
.result{{margin-top:0.75rem;font-size:0.95rem}}
.meta{{font-size:0.75rem;color:{t['muted']};margin-top:0.5rem}}
</style></head>
<body>
<div class="app">
{_compose_app_body(bp)}
</div>
<script>
{_compose_app_js(bp)}
</script>
</body></html>"""


# ── Public API ─────────────────────────────────────────────────────────────────

def autonomous_generate(query: str) -> dict:
    """
    Generate a complete project from scratch based on the user's description.
    Returns {title, type, code} — no templates copied.
    """
    bp = parse_blueprint(query)
    if bp.kind == "game":
        code = _compose_game_html(bp)
        return {"title": bp.title, "type": "autonomous_game", "code": code, "blueprint": bp}
    code = _compose_app_html(bp)
    return {"title": bp.title, "type": "autonomous_app", "code": code, "blueprint": bp}


def is_autonomous_candidate(query: str) -> bool:
    """True when we should code from scratch instead of using a template library."""
    q = query.lower()
    custom_signals = [
        len(q) > 20,
        bool(re.search(r"\b(with|that has|featuring|including|where|custom|unique)\b", q)),
        sum(1 for w in ["wizard", "ninja", "dragon", "neon", "survival", "multiplayer", "powerup"] if w in q) > 0,
        bool(re.search(r"(make|build|create).{10,}", q)),
    ]
    return any(custom_signals)
