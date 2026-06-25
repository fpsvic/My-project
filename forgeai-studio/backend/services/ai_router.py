"""
AI Router — intent classification and dispatch.

Intent pipeline (scored, not keyword-first):
  1. Normalize query
  2. Score each intent category
  3. Dispatch to the highest-scoring engine
  4. Fall back to a rich help response

Intent categories:
  GREETING · BUILD_GAME · BUILD_APP · MATH · SPACE · EARTH ·
  SCIENCE · HISTORY · PROGRAMMING · KNOWLEDGE
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
from services.dynamic_builder import build_dynamic_app
from services.update_handler import is_update_request, apply_update


# ══════════════════════════════════════════════════════════════
# NORMALIZATION
# ══════════════════════════════════════════════════════════════

def _normalize(raw: str) -> str:
    """Lowercase, strip punctuation noise, collapse whitespace."""
    q = raw.lower().strip()
    q = re.sub(r"[''`]", "'", q)          # smart quotes
    q = re.sub(r"[!?.,;:]+$", "", q)      # trailing punctuation
    q = re.sub(r"\s+", " ", q)            # collapse spaces
    return q


def _tokens(q: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", q)


# ══════════════════════════════════════════════════════════════
# INTENT: GREETING
# ══════════════════════════════════════════════════════════════

_GREETING_EXACT = {
    "hello", "hi", "hey", "sup", "yo", "howdy", "hiya",
    "greetings", "good morning", "good afternoon", "good evening",
    "whats up", "what's up", "how are you", "who are you",
    "what can you do", "what do you do", "help",
}
_GREETING_STARTS = (
    "hello ", "hi ", "hey ", "yo ", "howdy",
    "good morning", "good afternoon", "good evening",
)

def _score_greeting(q: str) -> int:
    if q in _GREETING_EXACT:
        return 100
    if any(q.startswith(p) for p in _GREETING_STARTS):
        return 80
    return 0


# ══════════════════════════════════════════════════════════════
# INTENT: BUILD (game vs app)
# ══════════════════════════════════════════════════════════════

# Strong action verbs that signal "build me something"
_BUILD_VERBS = [
    "make", "create", "build", "generate", "code", "develop",
    "write", "forge", "produce", "design", "craft", "give me",
    "show me", "i need", "i want", "put together", "compile",
    "construct", "render", "make me", "build me", "create me",
    "give me a", "can you make", "can you build", "can you create",
    "please make", "please build", "please create",
]

_GAME_NOUNS = {
    "snake", "pong", "flappy", "flappy bird", "tetris", "breakout",
    "brickbreaker", "brick breaker", "space invader", "space invaders",
    "tictactoe", "tic tac toe", "tic-tac-toe", "noughts and crosses",
    "clicker", "idle game", "cookie clicker", "space shooter",
    "shooter", "arcade game", "platform game", "platformer",
    "runner game", "endless runner", "maze game", "puzzle game",
    "card game", "memory game", "whack a mole", "asteroids",
    "pac man", "pacman", "frogger", "centipede", "galaga",
    "donkey kong", "mario", "pinball", "minesweeper",
}

_APP_NOUNS = {
    # calculators
    "calculator", "calc", "scientific calculator", "bmi calculator",
    "mortgage calculator", "tip calculator", "loan calculator",
    "tax calculator", "percentage calculator", "age calculator",
    "grade calculator", "gpa calculator",
    # time
    "timer", "stopwatch", "countdown", "countdown timer",
    "pomodoro", "pomodoro timer", "clock", "digital clock",
    "world clock", "alarm",
    # productivity
    "todo", "to-do", "to do", "to do list", "task list",
    "task manager", "checklist", "kanban", "kanban board",
    "planner", "habit tracker", "habit", "journal",
    # finance
    "budget tracker", "budget", "expense tracker", "spending tracker",
    "finance tracker", "money tracker",
    # conversion
    "unit converter", "converter", "currency converter",
    "temperature converter", "length converter", "weight converter",
    # creative
    "color picker", "colour picker", "palette generator", "color tool",
    "drawing app", "drawing canvas", "canvas", "whiteboard",
    "paint app", "sketch app",
    # generators
    "password generator", "password gen", "random password",
    "name generator", "quote generator",
    # text
    "notes", "notes app", "notepad", "note taking", "markdown editor",
    "text editor", "word counter", "text tool", "text utility",
    # learning
    "quiz", "quiz app", "trivia", "trivia game", "flashcards",
    "flash cards", "study cards", "memory cards",
    # misc
    "dice roller", "dice", "random number", "spinner",
    "currency", "forex",
}

# Phrases that mean "game" regardless of build verb
_GAME_CONTEXT = {"play", "playable", "arcade", "game", "gaming"}


def _has_build_verb(q: str) -> bool:
    for v in _BUILD_VERBS:
        if q.startswith(v + " ") or f" {v} " in q or q == v:
            return True
    return False


def _score_build_game(q: str) -> int:
    score = 0
    has_verb = _has_build_verb(q)
    # Direct game noun match
    noun_match = any(n in q for n in _GAME_NOUNS)
    # "build/make/create ... game" pattern
    game_pattern = bool(re.search(
        r"(make|build|create|code|write|generate|forge|give me|show me|i want|i need)"
        r".{0,40}(game|arcade|playable)",
        q
    ))
    if game_pattern:
        score += 90
    if noun_match and has_verb:
        score += 85
    if noun_match and any(c in q for c in _GAME_CONTEXT):
        score += 70
    if noun_match:
        score += 30
    return score


def _score_build_app(q: str) -> int:
    score = 0
    has_verb = _has_build_verb(q)
    noun_match = any(n in q for n in _APP_NOUNS)
    # "build me a X" pattern — extract subject and check app type
    m = re.search(
        r"(make|build|create|code|write|generate|forge|give me|show me|i need|i want)"
        r"\s+(?:me\s+)?(?:a\s+|an\s+)?(.+)",
        q,
    )
    if m:
        subject = m.group(2).strip()
        detected = detect_app_type(subject)
        if detected != "calculator" or "calc" in subject:
            score += 60
    if noun_match and has_verb:
        score += 90
    if noun_match:
        score += 20
    return score


# ══════════════════════════════════════════════════════════════
# INTENT: MATH
# ══════════════════════════════════════════════════════════════

_MATH_STRONG = {
    "derivative", "differentiate", "differentiation",
    "integral", "integrate", "integration", "antiderivative",
    "limit", "chain rule", "product rule", "quotient rule",
    "power rule", "polynomial", "calculus",
}
_MATH_TRIG = {"sin", "cos", "tan", "csc", "sec", "cot", "arcsin", "arccos", "arctan"}
_MATH_QUESTION = {"solve", "compute", "calculate", "evaluate", "simplify", "find the value"}

_MATH_EXPR_RE = re.compile(
    r"^[\d\s\+\-\*\/\(\)\.\^\%x]*"
    r"(?:sin|cos|tan|csc|sec|cot|log|ln|sqrt|abs|pi|e)?"
    r"[\d\s\+\-\*\/\(\)\.\^\%x]*$"
)


def _is_pure_math_expr(q: str) -> bool:
    clean = re.sub(
        r"^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+",
        "", q,
    )
    test = re.sub(r"sin|cos|tan|csc|sec|cot|log|ln|sqrt|abs|pi\b", "", clean).strip()
    return (
        bool(re.fullmatch(r"[\d\s\+\-\*\/\(\)\.\^\%x]+", test))
        and bool(re.search(r"\d", test))
        and bool(re.search(r"[\+\-\*\/\^]", test))
    )


def _score_math(q: str) -> int:
    score = 0
    if any(kw in q for kw in _MATH_STRONG):
        score += 90
    if any(t in q for t in _MATH_TRIG):
        score += 70
    if any(kw in q for kw in _MATH_QUESTION) and re.search(r"\d", q):
        score += 50
    if _is_pure_math_expr(q):
        score += 80
    if "x^" in q or "x²" in q or "x³" in q:
        score += 40
    return score


# ══════════════════════════════════════════════════════════════
# INTENT: SPACE
# ══════════════════════════════════════════════════════════════

_SPACE_STRONG = {
    "sun", "moon", "mars", "saturn", "jupiter", "venus", "mercury",
    "neptune", "uranus", "milky way", "galaxy", "black hole", "nebula",
    "supernova", "neutron star", "dark matter", "big bang", "light year",
    "parsec", "hubble", "asteroid", "comet", "exoplanet", "orbit",
    "space", "cosmos", "universe", "solar system", "nasa",
}
_SPACE_CONTEXT = {"distance", "far", "away", "travel", "speed", "weight", "gravity"}


def _score_space(q: str) -> int:
    score = 0
    toks = set(_tokens(q))
    strong = {kw for kw in _SPACE_STRONG if kw in q}
    if strong:
        score += 70 + len(strong) * 10
    if strong and any(c in q for c in _SPACE_CONTEXT):
        score += 20
    # phrases from keyword list
    if any(kw in q for kw in SPACE_KEYWORDS):
        score = max(score, 60)
    return min(score, 100)


# ══════════════════════════════════════════════════════════════
# INTENT: EARTH SCIENCE
# ══════════════════════════════════════════════════════════════

_EARTH_STRONG = {
    "volcano", "earthquake", "tectonic", "magma", "lava", "caldera",
    "trench", "mariana", "seafloor", "lithosphere", "crust", "mantle",
    "basalt", "granite", "sediment", "metamorphic", "igneous",
    "mineral", "rock", "fossil", "glacier", "erosion", "subduction",
    "hydrothermal", "vent", "black smoker", "ocean floor",
}


def _score_earth(q: str) -> int:
    score = 0
    if any(kw in q for kw in _EARTH_STRONG):
        score += 80
    if any(kw in q for kw in EARTH_KEYWORDS):
        score = max(score, 55)
    return score


# ══════════════════════════════════════════════════════════════
# INTENT: ADVANCED SCIENCE
# ══════════════════════════════════════════════════════════════

_SCIENCE_STRONG = {
    "quantum", "relativity", "photon", "electron", "proton", "neutron",
    "atom", "molecule", "dna", "rna", "gene", "chromosome", "protein",
    "enzyme", "cell", "mitosis", "evolution", "entropy", "thermodynamics",
    "periodic table", "element", "compound", "chemical", "reaction",
    "planck", "boltzmann", "avogadro", "einstein", "schrodinger",
    "heisenberg", "uncertainty principle", "wave function",
    "electronegativity", "covalent", "ionic", "bond",
    "golden ratio", "fibonacci sequence",
}


def _score_science(q: str) -> int:
    score = 0
    if any(kw in q for kw in _SCIENCE_STRONG):
        score += 80
    if any(kw in q for kw in ADVANCED_SCIENCE_KEYWORDS):
        score = max(score, 55)
    return score


# ══════════════════════════════════════════════════════════════
# INTENT: HISTORY / POLITICS
# ══════════════════════════════════════════════════════════════

_HISTORY_STRONG = {
    "president", "civil war", "world war", "revolution", "constitution",
    "declaration of independence", "amendment", "congress", "senate",
    "founding fathers", "slavery", "abolition", "reconstruction",
    "great depression", "new deal", "cold war", "vietnam",
    "washington", "lincoln", "jefferson", "hamilton", "madison",
    "jackson", "roosevelt", "kennedy", "reagan", "obama",
    "federalist", "whig", "democrat", "republican", "colonial",
}


def _score_history(q: str) -> int:
    score = 0
    if any(kw in q for kw in _HISTORY_STRONG):
        score += 80
    if any(kw in q for kw in POLITICAL_KEYWORDS):
        score = max(score, 55)
    # "who was X" / "tell me about X" patterns
    if re.search(r"(who was|who is|tell me about|what did|history of)\s+\w", q):
        if any(kw in q for kw in _HISTORY_STRONG):
            score += 10
    return score


# ══════════════════════════════════════════════════════════════
# INTENT: PROGRAMMING
# ══════════════════════════════════════════════════════════════

_PROG_LANGS = set(LANG_HISTORY.keys()) | {
    "python", "javascript", "typescript", "java", "golang", "go",
    "cpp", "c++", "csharp", "c#", "rust", "swift", "kotlin", "lua",
    "luau", "ruby", "php", "sql", "html", "css", "haskell", "scala",
    "elixir", "matlab", "r lang",
}
_PROG_CONCEPTS = {
    "variable", "function", "loop", "recursion", "algorithm",
    "data structure", "array", "linked list", "binary tree", "hash map",
    "sorting", "binary search", "big o", "complexity", "api",
    "rest api", "graphql", "async", "await", "thread", "concurrency",
    "object oriented", "oop", "class", "inheritance", "polymorphism",
    "git", "github", "docker", "kubernetes", "database", "sql",
    "hello world", "syntax", "compiler", "interpreter", "runtime",
    "framework", "library", "package", "module", "import",
    "debugging", "stack trace", "error handling", "exception",
    "regex", "regular expression", "json", "xml", "yaml",
}
_PROG_QUESTION_WORDS = {
    "how do i", "how to", "what is a", "what is an", "what are",
    "explain", "what does", "how does", "when to use", "difference between",
    "history of", "who created", "who made", "when was",
}


def _score_programming(q: str) -> int:
    score = 0
    lang_match = any(lang in q for lang in _PROG_LANGS)
    concept_match = any(c in q for c in _PROG_CONCEPTS)
    question_match = any(q.startswith(w) or w in q for w in _PROG_QUESTION_WORDS)

    if lang_match and any(w in q for w in ("history", "origin", "created", "hello world", "syntax", "example")):
        score += 95
    if lang_match and concept_match:
        score += 75
    if concept_match and question_match:
        score += 70
    if lang_match:
        score += 30
    if concept_match:
        score += 25
    # CODING_HELP exact match
    for key in CODING_HELP:
        if key in q:
            score += 60
            break
    return min(score, 100)


# ══════════════════════════════════════════════════════════════
# INTENT: GENERAL KNOWLEDGE
# ══════════════════════════════════════════════════════════════

def _score_knowledge(q: str) -> int:
    for key in GENERAL_KNOWLEDGE:
        if key in q:
            return 70
    return 0


# ══════════════════════════════════════════════════════════════
# DISPATCH HELPERS
# ══════════════════════════════════════════════════════════════

def _dispatch_greeting(mode: str) -> str:
    return (
        f"Hello! I am **ForgeAI**, your local cognitive AI running in **{mode}** mode.\n\n"
        "I can help you with:\n"
        "- **Build apps & tools** — `make a calculator`, `build a pomodoro timer`, `create a budget tracker`\n"
        "- **Build games** — `make flappy bird`, `build a snake game`, `create a space shooter`\n"
        "- **Math** — `derivative of 3x² + 5x`, `integral of sin(x)`, `what is 144 × 37`\n"
        "- **Space** — `how far is Mars from Earth`, `what is a black hole`\n"
        "- **Earth science** — `how do volcanoes form`, `what is the Mariana Trench`\n"
        "- **Science** — `explain quantum entanglement`, `what is DNA`\n"
        "- **History** — `who was Abraham Lincoln`, `what was the New Deal`\n"
        "- **Programming** — `history of Python`, `what is recursion`, `JavaScript hello world`\n\n"
        "Just tell me what you want to **build** or ask me anything!"
    )


def _dispatch_game(query: str, q: str, mode: str) -> str:
    game = compile_game(query)
    intro = (
        f"I compiled **{game['title']}** for you. "
        "Hit **\"Play Game\"** inside the code box to launch it instantly!"
    )
    block = f"\n\n```html\n{game['code']}\n```"
    if mode == "forge_thinking":
        return (
            "### Thinking Process\n"
            f"- **Genre detected**: {game['title']}\n"
            "- **Theme, speed, and modifiers** derived from your description.\n"
            "- **HTML5 Canvas engine** compiled with vanilla JS.\n\n---\n\n"
            + intro + block
        )
    return intro + block


def _dispatch_app(query: str, mode: str) -> str:
    # Try static fast-path first; fall back to dynamic builder for arbitrary requests
    static_type = detect_app_type(query.lower())
    if static_type and static_type != "calculator" or any(n in query.lower() for n in _APP_NOUNS):
        app = build_app(query)
    else:
        app = build_dynamic_app(query)
    intro = (
        f"I built a **{app['title']}** for you! "
        "Click **\"Launch App\"** in the code box to open it live."
    )
    block = f"\n\n```html\n{app['code']}\n```"
    if mode == "forge_thinking":
        return (
            "### Thinking Process\n"
            f"- **App type**: {app['type'].replace('_', ' ').title()}\n"
            "- **Theme** picked from your description.\n"
            "- **Single-file HTML5** built with vanilla JS.\n\n---\n\n"
            + intro + block
        )
    return intro + block


def _dispatch_dynamic(query: str, mode: str) -> str:
    app = build_dynamic_app(query)
    intro = (
        f"I built a **{app['title']}** for you! "
        "Click **\"Launch App\"** in the code box to open it live."
    )
    block = f"\n\n```html\n{app['code']}\n```"
    if mode == "forge_thinking":
        return (
            "### Thinking Process\n"
            f"- **Detected entity**: {app['type'].replace('_', ' ').title()}\n"
            "- **Fields & features** inferred from your description.\n"
            "- **Single-file HTML5** with localStorage persistence.\n\n---\n\n"
            + intro + block
        )
    return intro + block


def _dispatch_update(query: str, history: list, mode: str) -> str:
    app = apply_update(query, history)
    intro = (
        f"I updated the app — here is **{app['title']}**. "
        "Click **\"Launch App\"** to see the changes live."
    )
    block = f"\n\n```html\n{app['code']}\n```"
    return intro + block


def _dispatch_programming(query: str, mode: str) -> str:
    q = query.lower()

    # Hello-world / syntax
    for lang, hw in LANG_HELLO_WORLD.items():
        if lang in q and any(w in q for w in (
            "hello world", "syntax", "example", "how to write", "sample", "print"
        )):
            return (
                f"### {lang.capitalize()} — Hello World\n\n"
                f"```{lang}\n{hw}\n```\n\n"
                + LANG_HISTORY.get(lang, "")
            )

    # Language history
    for lang, history in LANG_HISTORY.items():
        if lang in q and any(w in q for w in (
            "history", "origin", "created", "designed", "who made",
            "when", "invented", "by whom", "who built", "who wrote",
        )):
            hw = LANG_HELLO_WORLD.get(lang, "")
            block = f"\n\n```{lang}\n{hw}\n```" if hw else ""
            return f"### {lang.capitalize()} Language Origin\n\n{history}{block}"

    # CODING_HELP lookup
    for key, answer in CODING_HELP.items():
        if key in q:
            return answer

    # Generic programming fallback
    return (
        "### Programming Help\n\n"
        "I can explain concepts, show language histories, and give code examples.\n\n"
        "Try asking:\n"
        "- `history of Python` · `Rust hello world` · `what is recursion`\n"
        "- `explain async/await` · `what is Big O notation` · `how does git work`"
    )


# ══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════

def generate_response(query: str, mode: str, history: list) -> str:
    q = _normalize(query)

    # ── Update check (before intent scoring) ──────────────────
    if is_update_request(q, history):
        return _dispatch_update(query, history, mode)

    # ── Score every intent ────────────────────────────────────
    # "build anything" — verb present but no known noun → dynamic builder
    build_verb_score = 65 if _has_build_verb(q) and not any(n in q for n in _GAME_NOUNS | _APP_NOUNS) else 0

    scores: dict[str, int] = {
        "greeting":    _score_greeting(q),
        "build_game":  _score_build_game(q),
        "build_app":   _score_build_app(q),
        "build_any":   build_verb_score,
        "math":        _score_math(q),
        "space":       _score_space(q),
        "earth":       _score_earth(q),
        "science":     _score_science(q),
        "history":     _score_history(q),
        "programming": _score_programming(q),
        "knowledge":   _score_knowledge(q),
    }

    best_intent = max(scores, key=lambda k: scores[k])
    best_score  = scores[best_intent]

    # ── Dispatch ──────────────────────────────────────────────
    if best_score < 30:
        # No strong match — return a rich capability overview
        return (
            "### ForgeAI Cognitive Response\n\n"
            f"I couldn't confidently identify what you meant by **\"{query}\"**.\n\n"
            "Here's what I can do:\n\n"
            "**Build apps & tools:**\n"
            "> `make a calculator` · `build a pomodoro timer` · `create a budget tracker`\n"
            "> `make a drawing canvas` · `build a quiz` · `create a habit tracker`\n\n"
            "**Build games:**\n"
            "> `make flappy bird` · `build a snake game` · `create a space shooter`\n\n"
            "**Ask me:**\n"
            "> Math: `derivative of x³ + 2x` · `what is 15% of 340`\n"
            "> Space: `how far is Neptune` · `what is a neutron star`\n"
            "> Science: `explain quantum entanglement` · `what is DNA`\n"
            "> History: `who was Abraham Lincoln` · `what caused the Civil War`\n"
            "> Code: `history of JavaScript` · `what is recursion` · `Python hello world`\n"
        )

    if best_intent == "greeting":
        return _dispatch_greeting(mode)

    if best_intent == "build_game":
        return _dispatch_game(query, q, mode)

    if best_intent == "build_any":
        return _dispatch_dynamic(query, mode)

    if best_intent == "build_app":
        # If it matches a known static app type, use the fast-path; otherwise dynamic
        if any(n in q for n in _APP_NOUNS):
            return _dispatch_app(query, mode)
        return _dispatch_dynamic(query, mode)

    if best_intent == "math":
        return generate_math_response(query, mode)

    if best_intent == "space":
        return generate_space_response(query, mode)

    if best_intent == "earth":
        return generate_earth_response(query, mode)

    if best_intent == "science":
        return generate_science_response(query, mode)

    if best_intent == "history":
        return generate_history_response(query, mode)

    if best_intent == "programming":
        return _dispatch_programming(query, mode)

    if best_intent == "knowledge":
        for key, answer in GENERAL_KNOWLEDGE.items():
            if key in q:
                return answer

    # shouldn't reach here, but be safe
    return _dispatch_greeting(mode)
