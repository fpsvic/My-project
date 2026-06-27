"""
Universal App Builder — generates complete single-file HTML5 apps from a natural-language description.
Handles: calculators, timers, converters, to-do lists, quizzes, drawing canvas, budget trackers,
         password generators, color pickers, note apps, flashcards, dice rollers, and more.
"""

import re

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

def _pick_theme(q: str) -> dict:
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
    return "calculator"  # default fallback


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
    t = _pick_theme(q)

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
