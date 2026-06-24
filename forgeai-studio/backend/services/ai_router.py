"""
AI Router — intent detection and dispatch to the correct engine.
Routing priority:
  greeting → build request (app / game) → math → space → earth → science →
  history / politics → programming → general knowledge → fallback APIs → help
"""

import re
from data.knowledge_base import (
    LANG_HISTORY,
    LANG_HELLO_WORLD,
    SPACE_KEYWORDS,
    EARTH_KEYWORDS,
    ADVANCED_SCIENCE_KEYWORDS,
    POLITICAL_KEYWORDS,
    GENERAL_KNOWLEDGE,
    CODING_HELP,
)
from services.math_engine import generate_math_response
from services.space_engine import generate_space_response
from services.earth_engine import generate_earth_response
from services.science_engine import generate_science_response
from services.history_engine import generate_history_response
from services.game_compiler import compile_game
from services.app_builder import build_app, detect_app_type
from services.fallback_apis import call_fallback_apis


# ─── Greeting set ─────────────────────────────────────────────────────────────

_GREETINGS = {
    "hello", "hi", "hey", "sup", "greetings", "how are you",
    "who are you", "whats up", "good morning", "good afternoon",
    "good evening", "yo", "howdy", "hiya",
}

# ─── Math keyword set ─────────────────────────────────────────────────────────

_MATH_KEYWORDS = {
    "derivative", "differentiate", "integral", "integrate", "antiderivative",
    "sin", "cos", "tan", "csc", "sec", "cot",
    "limit", "chain rule", "product rule", "quotient rule",
    "polynomial", "exponent", "logarithm", "log base",
}

# ─── Game genres ──────────────────────────────────────────────────────────────

_GAME_GENRES = {
    "pong", "snake", "tictactoe", "tic-tac-toe", "flappy", "arcade",
    "brick", "clicker", "shooter", "space invader", "tetris",
}

# ─── App builder keywords (non-game tools) ────────────────────────────────────

_APP_KEYWORDS = {
    "calculator", "calc", "timer", "stopwatch", "countdown", "clock",
    "todo", "to-do", "to do", "task list", "checklist", "kanban",
    "converter", "convert", "password", "generator", "color picker",
    "palette", "drawing", "paint", "whiteboard", "quiz", "trivia",
    "flashcard", "budget", "expense", "tracker", "notes", "notepad",
    "notepad", "dice", "roller", "habit", "pomodoro", "age calculator",
    "grade", "gpa", "currency", "forex", "word count", "text tool",
    "bmi", "mortgage", "tip calculator", "unit converter",
}

_BUILD_VERBS = {
    "make", "create", "build", "generate", "give me", "show me",
    "design", "write", "code", "develop", "forge", "produce", "make me",
    "i need", "i want", "can you make", "can you build", "can you create",
    "can you give", "put together",
}


def _is_build_verb(q: str) -> bool:
    return any(q.startswith(v) or f" {v} " in q for v in _BUILD_VERBS)


def _is_game_request(q: str) -> bool:
    if re.search(r"(make|create|play|build|code|generate)\s+.{0,30}game", q):
        return True
    if any(g in q for g in _GAME_GENRES):
        if _is_build_verb(q) or any(g in q for g in ("play", "game")):
            return True
    return False


def _is_app_request(q: str) -> bool:
    """Detect requests to build a non-game tool/app."""
    if any(kw in q for kw in _APP_KEYWORDS) and _is_build_verb(q):
        return True
    # Patterns like "make me a ___" or "build a ___" that match an app type
    match = re.search(r"(make|build|create|give me|i need|generate)\s+(me\s+)?(a\s+|an\s+)?(.+)", q)
    if match:
        subject = match.group(4).strip().rstrip("?. ")
        if detect_app_type(subject) != "calculator" or "calc" in subject:
            if any(kw in subject for kw in _APP_KEYWORDS):
                return True
    return False


def _is_math_expression(s: str) -> bool:
    clean = re.sub(
        r"^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+",
        "", s.strip().lower(),
    ).rstrip("?")
    test = re.sub(r"sin|cos|tan|csc|sec|cot|log|ln|sqrt|abs|pi", "", clean)
    return (
        bool(re.fullmatch(r"[0-9+\-*/().\s^%x]+", test.strip()))
        and bool(re.search(r"[0-9]", test))
        and bool(re.search(r"[+\-*/^%]", test))
    )


# ─── Programming help ─────────────────────────────────────────────────────────

def _generate_code_help(query: str, mode: str) -> str:
    q = query.lower()

    # Hello world / syntax requests
    for lang, hw in LANG_HELLO_WORLD.items():
        if lang in q and any(w in q for w in ("hello world", "syntax", "example", "how to write", "sample")):
            return (
                f"### {lang.capitalize()} — Hello World\n\n"
                f"```{lang}\n{hw}\n```\n\n"
                f"{LANG_HISTORY.get(lang, '')}"
            )

    # Language history / origin
    for lang, history in LANG_HISTORY.items():
        if lang in q and any(w in q for w in (
            "history", "origin", "created", "designed", "who made", "when", "invented", "by whom"
        )):
            hw = LANG_HELLO_WORLD.get(lang, "")
            code_block = f'\n\n```{lang}\n{hw}\n```' if hw else ""
            return f"### {lang.capitalize()} Language Origin\n\n{history}{code_block}"

    # Coding help lookup
    for key, answer in CODING_HELP.items():
        if key in q:
            return answer

    return ""


# ─── General knowledge lookup ─────────────────────────────────────────────────

def _generate_knowledge_response(query: str) -> str:
    q = query.lower()
    for key, answer in GENERAL_KNOWLEDGE.items():
        if key in q:
            return answer
    return ""


# ─── Main router ──────────────────────────────────────────────────────────────

def generate_response(query: str, mode: str, history: list) -> str:
    q = query.lower().strip().rstrip("?!.")

    # ── Greeting ──────────────────────────────────────────────────────────────
    for g in _GREETINGS:
        if q == g or q.startswith(g + " ") or q.startswith(g + "?") or q.startswith(g + "!"):
            return (
                f"Hello! I am **ForgeAI**, your local cognitive AI running in **{mode}** mode.\n\n"
                "I can help you with:\n"
                "- **Build apps & tools** — calculators, timers, to-do lists, quizzes, budget trackers, and more\n"
                "- **Build games** — Snake, Pong, Flappy Bird, Space Shooter, Brick Breaker, and more\n"
                "- **Calculus & Trigonometry** — derivatives, integrals, trig ratios\n"
                "- **Space Science** — orbital distances, cosmic constants, planetary data\n"
                "- **Earth Science** — geology, volcanology, oceanography\n"
                "- **Advanced Science** — quantum physics, chemistry, genetics\n"
                "- **US History** — presidential history, party systems, Civil War\n"
                "- **Programming** — language histories, syntax, hello-world examples\n\n"
                "Just tell me what to **build** or what you want to **know**!"
            )

    # ── Game compile ──────────────────────────────────────────────────────────
    if _is_game_request(q):
        game = compile_game(query)
        intro = (
            f"I have compiled **{game['title']}** for you. "
            "Click **\"Play Game\"** inside the code box to launch it instantly!"
        )
        code_block = f"\n\n```html\n{game['code']}\n```"
        if mode == "forge_thinking":
            return (
                "### Thinking Process\n"
                f"- **Detected genre**: {game['title']}\n"
                "- **Theme, speed, and obstacles** analyzed from your description.\n"
                "- **Canvas engine** generated with HTML5 + vanilla JS.\n\n---\n\n"
                f"{intro}{code_block}"
            )
        return intro + code_block

    # ── App / tool builder ────────────────────────────────────────────────────
    if _is_app_request(q):
        app = build_app(query)
        intro = (
            f"I have built a **{app['title']}** for you! "
            "Click **\"Play Game\"** inside the code box to open it live."
        )
        code_block = f"\n\n```html\n{app['code']}\n```"
        if mode == "forge_thinking":
            return (
                "### Thinking Process\n"
                f"- **App type detected**: {app['type'].replace('_', ' ').title()}\n"
                "- **Theme** selected based on your description.\n"
                "- **Single-file HTML5 app** generated with Tailwind CSS + vanilla JS.\n\n---\n\n"
                f"{intro}{code_block}"
            )
        return intro + code_block

    # ── Political / history ───────────────────────────────────────────────────
    if any(kw in q for kw in POLITICAL_KEYWORDS):
        return generate_history_response(query, mode)

    # ── Math ──────────────────────────────────────────────────────────────────
    if any(kw in q for kw in _MATH_KEYWORDS) or _is_math_expression(query):
        return generate_math_response(query, mode)

    # ── Space ─────────────────────────────────────────────────────────────────
    if any(kw in q for kw in SPACE_KEYWORDS):
        return generate_space_response(query, mode)

    # ── Earth science ─────────────────────────────────────────────────────────
    if any(kw in q for kw in EARTH_KEYWORDS):
        return generate_earth_response(query, mode)

    # ── Advanced science ──────────────────────────────────────────────────────
    if any(kw in q for kw in ADVANCED_SCIENCE_KEYWORDS):
        return generate_science_response(query, mode)

    # ── Programming / language history ───────────────────────────────────────
    code_resp = _generate_code_help(query, mode)
    if code_resp:
        return code_resp

    # ── General knowledge lookup ──────────────────────────────────────────────
    knowledge_resp = _generate_knowledge_response(query)
    if knowledge_resp:
        return knowledge_resp

    # ── External API fallback chain ───────────────────────────────────────────
    fallback = call_fallback_apis(query, history)
    if fallback:
        return fallback

    # ── Built-in help message ─────────────────────────────────────────────────
    return (
        "### ForgeAI Cognitive Response\n\n"
        f"I've processed your query: **\"{query}\"**.\n\n"
        "Here's what I can help you build or explain:\n\n"
        "**Build an app or tool:**\n"
        "- `make me a calculator` · `build a pomodoro timer` · `create a budget tracker`\n"
        "- `build a quiz` · `make a to-do list` · `create a habit tracker`\n"
        "- `make a drawing canvas` · `build a password generator` · `unit converter`\n\n"
        "**Build a game:**\n"
        "- `make a snake game` · `build flappy bird` · `create a space shooter`\n\n"
        "**Ask me something:**\n"
        "- Math: `derivative of x^3 + 2x` · `integral of cos(x)`\n"
        "- Space: `distance from Earth to Mars` · `how fast is light`\n"
        "- Science: `what is the Planck constant` · `explain DNA`\n"
        "- History: `who was Abraham Lincoln` · `what was the New Deal`\n"
        "- Code: `history of Python` · `JavaScript hello world`\n"
    )
