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
try:
    from data.knowledge_base import LANG_EXAMPLES
except ImportError:
    LANG_EXAMPLES = {}
from services.math_engine import generate_math_response
from services.space_engine import generate_space_response
from services.earth_engine import generate_earth_response
from services.science_engine import generate_science_response
from services.history_engine import generate_history_response
from services.game_compiler import compile_game
from services.app_builder import build_app, detect_app_type
from services.dynamic_builder import build_dynamic_app
from services.update_handler import is_update_request, apply_update

# --- NORMALIZATION ---

def _normalize(raw: str) -> str:
    q = raw.lower().strip()
    q = re.sub(r"[''`]", "'", q)
    q = re.sub(r"[!?.,;:]+$", "", q)
    q = re.sub(r"\s+", " ", q)
    return q

def _tokens(q: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", q)

def _match(q: str, *words) -> bool:
    return any(w in q for w in words)

# --- INTENT: GREETING ---

_GREETING_EXACT = {
    "hello", "hi", "hey", "sup", "yo", "howdy", "hiya",
    "greetings", "good morning", "good afternoon", "good evening",
    "whats up", "what's up", "how are you", "who are you",
    "what can you do", "what do you do", "help",
    "wassup", "wsp", "yo yo", "heyy", "heyyy", "hi there", "hey there",
    "hello there", "what's good", "whats good", "sup bro", "sup man",
    "hey bro", "hey man", "good day", "morning", "evening", "night",
    "hey hey", "hola", "bonjour", "ciao", "namaste", "salut", "ola",
}
_GREETING_STARTS = (
    "hello ", "hi ", "hey ", "yo ", "howdy",
    "good morning", "good afternoon", "good evening",
    "morning", "evening", "night", "hola", "hey there", "hi there", "sup ",
)

def _score_greeting(q: str) -> int:
    if q in _GREETING_EXACT:
        return 100
    if any(q.startswith(p) for p in _GREETING_STARTS):
        return 80
    return 0

# --- INTENT: BUILD ---

_BUILD_VERBS = [
    "make", "create", "build", "generate", "code", "develop",
    "write", "forge", "produce", "design", "craft", "give me",
    "show me", "i need", "i want", "put together", "compile",
    "construct", "render", "make me", "build me", "create me",
    "give me a", "can you make", "can you build", "can you create",
    "please make", "please build", "please create",
    "i want you to", "can u make", "make me a", "gimme", "gimme a",
    "build a", "throw together", "whip up", "spin up", "put together a",
    "create for me", "can u build", "pls make", "pls build",
    "could you make", "could you build", "id like", "i'd like a",
    "make something", "generate me", "i need a", "build something",
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
    "battle royale", "top down shooter", "rpg", "role playing",
    "dungeon crawler", "roguelike", "roguelite", "city builder",
    "resource management", "survival game", "crafting game",
    "rhythm game", "typing game", "word game", "trivia game",
    "quiz game", "number game", "reaction game", "reflex game",
    "catch game", "dodge game", "jump game", "run game", "fly game",
    "pilot game", "driving game", "car game", "racing game",
    "bike game", "sport game", "football game", "basketball game",
    "baseball game", "tennis game", "golf game", "boxing game",
    "fight game", "fighting game", "war game",
}

_APP_NOUNS = {
    "calculator", "calc", "scientific calculator", "bmi calculator",
    "mortgage calculator", "tip calculator", "loan calculator",
    "tax calculator", "percentage calculator", "age calculator",
    "grade calculator", "gpa calculator",
    "timer", "stopwatch", "countdown", "countdown timer",
    "pomodoro", "pomodoro timer", "clock", "digital clock",
    "world clock", "alarm",
    "todo", "to-do", "to do", "to do list", "task list",
    "task manager", "checklist", "kanban", "kanban board",
    "planner", "habit tracker", "habit", "journal",
    "budget tracker", "budget", "expense tracker", "spending tracker",
    "finance tracker", "money tracker",
    "unit converter", "converter", "currency converter",
    "temperature converter", "length converter", "weight converter",
    "color picker", "colour picker", "palette generator", "color tool",
    "drawing app", "drawing canvas", "canvas", "whiteboard",
    "paint app", "sketch app",
    "password generator", "password gen", "random password",
    "name generator", "quote generator",
    "notes", "notes app", "notepad", "note taking", "markdown editor",
    "text editor", "word counter", "text tool", "text utility",
    "quiz", "quiz app", "trivia", "trivia game", "flashcards",
    "flash cards", "study cards", "memory cards",
    "dice roller", "dice", "random number", "spinner",
    "currency", "forex",
}

_GAME_CONTEXT = {"play", "playable", "arcade", "game", "gaming"}

def _has_build_verb(q: str) -> bool:
    return any(q.startswith(v + " ") or f" {v} " in q or q == v for v in _BUILD_VERBS)

def _score_build_game(q: str) -> int:
    score = 0
    noun_match = _match(q, *_GAME_NOUNS)
    game_pattern = bool(re.search(
        r"(make|build|create|code|write|generate|forge|give me|show me|i want|i need)"
        r".{0,40}(game|arcade|playable)", q
    ))
    if game_pattern:
        score += 90
    if noun_match and _has_build_verb(q):
        score += 85
    if noun_match and _match(q, *_GAME_CONTEXT):
        score += 70
    if noun_match:
        score += 30
    return score

def _score_build_app(q: str) -> int:
    score = 0
    noun_match = _match(q, *_APP_NOUNS)
    m = re.search(
        r"(make|build|create|code|write|generate|forge|give me|show me|i need|i want)"
        r"\s+(?:me\s+)?(?:a\s+|an\s+)?(.+)", q,
    )
    if m:
        subject = m.group(2).strip()
        detected = detect_app_type(subject)
        if detected != "calculator" or "calc" in subject:
            score += 60
    if noun_match and _has_build_verb(q):
        score += 90
    if noun_match:
        score += 20
    return score

# --- INTENT: MATH ---

_MATH_STRONG = {
    "derivative", "differentiate", "differentiation",
    "integral", "integrate", "integration", "antiderivative",
    "limit", "chain rule", "product rule", "quotient rule",
    "power rule", "polynomial", "calculus",
}
_MATH_TRIG = {"sin", "cos", "tan", "csc", "sec", "cot", "arcsin", "arccos", "arctan"}
_MATH_QUESTION = {
    "solve", "compute", "calculate", "evaluate", "simplify", "find the value",
    "what is", "whats", "how much is", "how many", "work out", "figure out",
    "what does", "tell me", "give me", "find", "determine", "show me",
}

def _is_pure_math_expr(q: str) -> bool:
    clean = re.sub(
        r"^(what is|whats|what's|calculate|solve|evaluate|compute|find|value of)\s+", "", q,
    )
    test = re.sub(r"sin|cos|tan|csc|sec|cot|log|ln|sqrt|abs|pi\b", "", clean).strip()
    return (
        bool(re.fullmatch(r"[\d\s\+\-\*\/\(\)\.\^\%x]+", test))
        and bool(re.search(r"\d", test))
        and bool(re.search(r"[\+\-\*\/\^]", test))
    )

def _score_math(q: str) -> int:
    score = 0
    if _match(q, *_MATH_STRONG):
        score += 90
    if _match(q, *_MATH_TRIG):
        score += 70
    if _match(q, *_MATH_QUESTION) and re.search(r"\d", q):
        score += 50
    if _is_pure_math_expr(q):
        score += 80
    if "x^" in q or "x²" in q or "x³" in q:
        score += 40
    return score

# --- INTENT: SPACE ---

_SPACE_STRONG = {
    "sun", "moon", "mars", "saturn", "jupiter", "venus", "mercury",
    "neptune", "uranus", "milky way", "galaxy", "black hole", "nebula",
    "supernova", "neutron star", "dark matter", "big bang", "light year",
    "parsec", "hubble", "asteroid", "comet", "exoplanet", "orbit",
    "space", "cosmos", "universe", "solar system", "nasa",
}
_SPACE_CONTEXT = {"distance", "far", "away", "travel", "speed", "weight", "gravity"}

def _score_space(q: str) -> int:
    strong = {kw for kw in _SPACE_STRONG if kw in q}
    score = 0
    if strong:
        score += 70 + len(strong) * 10
    if strong and _match(q, *_SPACE_CONTEXT):
        score += 20
    if _match(q, *SPACE_KEYWORDS):
        score = max(score, 60)
    return min(score, 100)

# --- INTENT: EARTH SCIENCE ---

_EARTH_STRONG = {
    "volcano", "earthquake", "tectonic", "magma", "lava", "caldera",
    "trench", "mariana", "seafloor", "lithosphere", "crust", "mantle",
    "basalt", "granite", "sediment", "metamorphic", "igneous",
    "mineral", "rock", "fossil", "glacier", "erosion", "subduction",
    "hydrothermal", "vent", "black smoker", "ocean floor",
}

def _score_earth(q: str) -> int:
    score = 0
    if _match(q, *_EARTH_STRONG):
        score += 80
    if _match(q, *EARTH_KEYWORDS):
        score = max(score, 55)
    return score

# --- INTENT: ADVANCED SCIENCE ---

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
    if _match(q, *_SCIENCE_STRONG):
        score += 80
    if _match(q, *ADVANCED_SCIENCE_KEYWORDS):
        score = max(score, 55)
    return score

# --- INTENT: HISTORY / POLITICS ---

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
    if _match(q, *_HISTORY_STRONG):
        score += 80
    if _match(q, *POLITICAL_KEYWORDS):
        score = max(score, 55)
    if re.search(r"(who was|who is|tell me about|what did|history of)\s+\w", q):
        if _match(q, *_HISTORY_STRONG):
            score += 10
    return score

# --- INTENT: PROGRAMMING ---

_PROG_LANGS = set(LANG_HISTORY.keys()) | {
    "python", "javascript", "typescript", "java", "golang", "go",
    "cpp", "c++", "csharp", "c#", "rust", "swift", "kotlin", "lua",
    "luau", "ruby", "php", "sql", "html", "css", "haskell", "scala",
    "elixir", "matlab", "r lang", "dart", "js", "ts",
}

_PROG_CONCEPTS_MAP: dict[str, str] = {
    "function": "function", "functions": "function", "method": "function", "def": "function",
    "class": "class", "classes": "class", "object": "class", "oop": "class",
    "loop": "loop", "loops": "loop", "for loop": "loop", "while loop": "loop", "iterate": "loop",
    "error": "error_handling", "exception": "error_handling", "try catch": "error_handling",
    "error handling": "error_handling",
    "async": "async", "await": "async", "asynchronous": "async", "concurrency": "async",
    "list": "list_ops", "array": "list_ops", "slice": "list_ops", "vector": "list_ops",
    "closure": "closures", "closures": "closures", "lambda": "closures",
    "arrow function": "closures",
    "file": "file_io", "read file": "file_io", "write file": "file_io", "io": "file_io",
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


def _detect_lang_and_concept(q: str) -> tuple[str, str]:
    _LANG_ALIASES: dict[str, str] = {
        "c++": "cpp", "c#": "csharp", "go ": "golang",
        "golang": "golang", "js": "javascript", "ts": "typescript",
    }
    detected_lang = ""
    for alias, canonical in _LANG_ALIASES.items():
        if alias.rstrip() in q:
            detected_lang = canonical
            break
    if not detected_lang:
        for lang in _PROG_LANGS:
            if lang in q:
                detected_lang = _LANG_ALIASES.get(lang, lang)
                break
    detected_concept = ""
    for keyword in sorted(_PROG_CONCEPTS_MAP, key=len, reverse=True):
        if keyword in q:
            detected_concept = _PROG_CONCEPTS_MAP[keyword]
            break
    if detected_lang and detected_concept:
        return detected_lang, detected_concept
    return "", ""


def _score_programming(q: str) -> int:
    score = 0
    lang_match = _match(q, *_PROG_LANGS)
    concept_match = _match(q, *_PROG_CONCEPTS)
    concept_map_match = _match(q, *_PROG_CONCEPTS_MAP)
    question_match = any(q.startswith(w) or w in q for w in _PROG_QUESTION_WORDS)
    if lang_match and _match(q, "history", "origin", "created", "hello world", "syntax", "example"):
        score += 95
    detected_lang, detected_concept = _detect_lang_and_concept(q)
    if detected_lang and detected_concept:
        if "show me" in q:
            score += 85
        elif re.search(r"how do you", q) and "in" in q:
            score += 80
        elif re.search(r"\bin\b", q):
            score += 70
        else:
            score += 60
    if lang_match and concept_match:
        score += 75
    if concept_match and question_match:
        score += 70
    if lang_match:
        score += 30
    if concept_match or concept_map_match:
        score += 25
    for key in CODING_HELP:
        if key in q:
            score += 60
            break
    return min(score, 100)

# --- INTENT: ANIMALS ---

_ANIMAL_NAMES = {
    "lion", "lions", "tiger", "tigers", "cheetah", "cheetahs", "leopard", "leopards",
    "jaguar", "jaguars", "panther", "panthers", "cougar", "puma",
    "wolf", "wolves", "coyote", "fox", "foxes",
    "bear", "bears", "polar bear", "grizzly bear", "black bear", "panda",
    "gorilla", "gorillas", "chimpanzee", "chimp", "orangutan", "baboon",
    "monkey", "monkeys", "ape", "apes", "bonobo",
    "dolphin", "dolphins", "whale", "whales", "shark", "sharks",
    "octopus", "octopi", "squid", "jellyfish", "seal", "seals",
    "walrus", "sea lion", "orca", "killer whale",
    "eagle", "eagles", "owl", "owls", "hawk", "falcons", "falcon",
    "penguin", "penguins", "parrot", "parrots", "flamingo",
    "hummingbird", "albatross", "condor", "vulture", "toucan",
    "snake", "snakes", "crocodile", "crocodiles", "alligator",
    "komodo dragon", "lizard", "gecko", "iguana", "chameleon",
    "tortoise", "turtle", "turtles",
    "bee", "bees", "ant", "ants", "butterfly", "butterflies",
    "spider", "spiders", "scorpion", "dragonfly", "mosquito",
    "elephant", "elephants", "giraffe", "giraffes", "rhino", "rhinoceros",
    "hippo", "hippopotamus", "zebra", "zebras", "wildebeest", "buffalo",
    "hyena", "hyenas",
    "kangaroo", "koala", "platypus", "armadillo", "sloth", "anteater",
    "bat", "bats", "deer", "moose", "elk", "reindeer",
    "horse", "horses", "donkey", "camel", "llama",
    "dog", "dogs", "cat", "cats", "rabbit", "rabbits",
    "fish", "salmon", "tuna", "clownfish", "anglerfish", "pufferfish",
    "lobster", "crab", "starfish", "seahorse", "manta ray", "stingray",
    "cobra", "cobras", "python", "pythons", "anaconda", "anacondas",
    "reticulated python", "burmese python", "king cobra", "spitting cobra",
    "t-rex", "t rex", "tyrannosaurus", "tyrannosaurus rex",
    "velociraptor", "velociraptors", "raptor", "raptors",
    "mammoth", "mammoths", "woolly mammoth",
    "snow leopard", "snow leopards",
    "blue whale", "blue whales",
    "hammerhead", "hammerhead shark", "hammerhead sharks",
    "manta", "manta rays",
    "bald eagle", "bald eagles",
}

_ANIMAL_QUESTION_PREFIXES = (
    "tell me about", "what is a", "what is an", "what are", "how do",
    "how does", "where do", "where does", "why do", "why does",
    "what does a", "how big is", "how fast is", "how long does",
    "how many", "can a", "do", "does a", "are",
    "facts about", "information about", "info about",
    "talk about", "explain",
    "whats the", "how big", "how heavy", "how smart", "how dangerous",
    "can a", "do", "does", "are", "is a", "is the",
    "what sounds", "what noise", "where is", "why do", "why does",
    "when do", "can", "could a",
)

def _score_animals(q: str) -> int:
    if not _match(q, *_ANIMAL_NAMES):
        return 0
    score = 85
    if any(q.startswith(p) for p in _ANIMAL_QUESTION_PREFIXES):
        score += 10
    if _match(q, "habitat", "diet", "hunt", "prey", "predator", "endangered",
              "species", "behavior", "speed", "size", "weight", "lifespan",
              "migration", "breeding", "population", "facts"):
        score += 5
    return min(score, 100)

# --- INTENT: GENERAL KNOWLEDGE ---

def _score_knowledge(q: str) -> int:
    for key in GENERAL_KNOWLEDGE:
        if key in q:
            return 75
    _KW_TOPICS = {
        "pi", "euler", "fibonacci", "pythagorean", "calculus", "prime",
        "infinity", "matrix", "matrices", "blood type", "temperature",
        "population", "internet", "encryption", "blockchain", "http",
        "fastest computer", "oldest language", "boil", "egg",
    }
    if _match(q, *_KW_TOPICS):
        return 65
    return 0

# --- DISPATCH HELPERS ---

def _dispatch_greeting(mode: str) -> str:
    return (
        f"Hello! I am **ForgeAI**, your local cognitive AI running in **{mode}** mode.\n\n"
        "I can help you with:\n"
        "- **Build apps & tools** — `make a calculator`, `build a kanban board`, `create a budget tracker`\n"
        "- **Build games** — `make flappy bird`, `build a snake game`, `create a space shooter`\n"
        "- **Math** — `derivative of 3x² + 5x`, `integral of sin(x)`, `what is 144 × 37`\n"
        "- **Space** — `how far is Mars from Earth`, `what is a neutron star`\n"
        "- **Earth science** — `how do volcanoes form`, `what is the Mariana Trench`\n"
        "- **Science** — `explain quantum entanglement`, `what is DNA`\n"
        "- **Animals** — `tell me about lions`, `how fast is a cheetah`, `facts about dolphins`\n"
        "- **History** — `who was Abraham Lincoln`, `what was the New Deal`\n"
        "- **Programming** — `history of Python`, `what is recursion`, `JavaScript hello world`\n\n"
        "Just tell me what you want to **build** or ask me anything!"
    )

_ASPECT_KEYWORDS = {
    "speed":    ["fast", "speed", "mph", "km/h", "quick", "run", "swim", "fly", "sprint"],
    "size":     ["big", "size", "large", "heavy", "weight", "tall", "long", "huge", "giant", "small"],
    "diet":     ["eat", "diet", "food", "feed", "prey on", "hunt", "consume"],
    "habitat":  ["live", "habitat", "home", "found", "range", "region", "continent", "where"],
    "predator": ["predator", "threat", "eats", "hunted by", "enemy", "danger"],
    "lifespan": ["live", "lifespan", "age", "old", "years", "long"],
    "behavior": ["behave", "social", "pack", "group", "herd", "pride", "lone", "nocturnal", "sleep", "smart", "intelligent"],
}

_ASPECT_INTROS = {
    "speed":    ["Speed-wise, ", "When it comes to speed, ", "In terms of how fast — ", ""],
    "size":     ["Size-wise, ", "As for size, ", "In terms of size, ", ""],
    "diet":     ["Diet-wise, ", "As for what they eat — ", "When it comes to food, ", ""],
    "habitat":  ["Habitat-wise, ", "As for where they live — ", "In terms of range, ", ""],
    "predator": ["As for predators — ", "In the wild, ", "When it comes to threats — ", ""],
    "lifespan": ["Lifespan-wise, ", "In terms of how long they live — ", ""],
    "behavior": ["Behaviour-wise, ", "As for how they act — ", ""],
}

import random

def _extract_aspect(answer: str, aspect: str) -> str | None:
    keywords = _ASPECT_KEYWORDS.get(aspect, [])
    # Split on newlines AND sentence endings so bullet-point entries work
    lines = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', answer) if s.strip()]
    # Strip markdown formatting (* ** # >) for clean matching
    clean = [re.sub(r'[*#>`_]+', '', l).strip() for l in lines]
    matches = [clean[i] for i, l in enumerate(clean) if any(k in l.lower() for k in keywords) and len(clean[i]) > 8]
    if not matches:
        return None
    intro = random.choice(_ASPECT_INTROS.get(aspect, [""]))
    return intro + "  ".join(matches[:2])

def _detect_aspect(q: str) -> str | None:
    for aspect, keywords in _ASPECT_KEYWORDS.items():
        if any(k in q for k in keywords):
            return aspect
    return None

def _dispatch_animals(query: str, q: str) -> str:
    # Direct key match
    for key, answer in GENERAL_KNOWLEDGE.items():
        if key in q or q in key:
            aspect = _detect_aspect(q)
            if aspect:
                specific = _extract_aspect(answer, aspect)
                if specific:
                    return specific
            return answer
    # Animal name match — find relevant entry
    animal = next((a for a in sorted(_ANIMAL_NAMES, key=len, reverse=True) if a in q), None)
    if animal:
        aspect = _detect_aspect(q)
        # Try specific aspect entry first (e.g. "what do lions eat")
        aspect_key_map = {
            "diet": f"what do {animal}s eat",
            "habitat": f"where do {animal}s live",
            "predator": f"what eats {animal}s",
            "speed": f"how fast is a {animal}",
        }
        if aspect and aspect in aspect_key_map:
            candidate = aspect_key_map[aspect]
            if candidate in GENERAL_KNOWLEDGE:
                return random.choice(_ASPECT_INTROS.get(aspect, [""])) + GENERAL_KNOWLEDGE[candidate]
        # Fall back to general entry and extract aspect
        for key, answer in GENERAL_KNOWLEDGE.items():
            if animal in key and "tell me" in key:
                if aspect:
                    specific = _extract_aspect(answer, aspect)
                    if specific:
                        return specific
                return answer
        # Any entry mentioning animal
        for key, answer in GENERAL_KNOWLEDGE.items():
            if animal in key:
                if aspect:
                    specific = _extract_aspect(answer, aspect)
                    if specific:
                        return specific
                return answer
    mentioned = animal or "animal"
    return (
        f"I have info on **{mentioned}s** — try asking:\n"
        f"> `tell me about {mentioned}s` · `what do {mentioned}s eat` · `where do {mentioned}s live` · `what eats {mentioned}s`"
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
    return intro + f"\n\n```html\n{app['code']}\n```"

def _dispatch_programming(query: str, mode: str) -> str:
    q = query.lower()
    lang, concept = _detect_lang_and_concept(q)
    if lang and concept:
        lang_examples = LANG_EXAMPLES.get(lang, {})
        if concept in lang_examples:
            snippet = lang_examples[concept]
            display_lang = lang.replace("golang", "Go").replace("cpp", "C++").replace("csharp", "C#")
            display_lang = display_lang.capitalize() if display_lang == lang else display_lang
            return (
                f"### {display_lang} — {concept.replace('_', ' ').title()}\n\n"
                f"```{lang}\n{snippet}\n```"
            )
    for lang_key, hw in LANG_HELLO_WORLD.items():
        if lang_key in q and _match(q, "hello world", "syntax", "example", "how to write", "sample", "print"):
            return (
                f"### {lang_key.capitalize()} — Hello World\n\n"
                f"```{lang_key}\n{hw}\n```\n\n"
                + LANG_HISTORY.get(lang_key, "")
            )
    for lang_key, history in LANG_HISTORY.items():
        if lang_key in q and _match(q, "history", "origin", "created", "designed", "who made",
                                     "when", "invented", "by whom", "who built", "who wrote"):
            hw = LANG_HELLO_WORLD.get(lang_key, "")
            block = f"\n\n```{lang_key}\n{hw}\n```" if hw else ""
            return f"### {lang_key.capitalize()} Language Origin\n\n{history}{block}"
    for key, answer in CODING_HELP.items():
        if key in q:
            return answer
    return (
        "### Programming Help\n\n"
        "I can explain concepts, show language histories, and give code examples.\n\n"
        "Try asking:\n"
        "- `history of Python` · `Rust hello world` · `what is recursion`\n"
        "- `explain async/await` · `what is Big O notation` · `how does git work`\n"
        "- `show me a class in Rust` · `loops in Kotlin` · `async in Go`"
    )

# --- QUICK MODE ---

def _quick_response(query: str, q: str) -> str:
    if _score_math(q) >= 30:
        return generate_math_response(query, "forge_instant")
    norm = q.strip().rstrip("?")
    for key, val in GENERAL_KNOWLEDGE.items():
        if norm in key or key in norm:
            return val
    if _score_space(q) >= 30:
        return generate_space_response(query, "forge_instant")
    if _score_earth(q) >= 30:
        return generate_earth_response(query, "forge_instant")
    if _score_science(q) >= 30:
        return generate_science_response(query, "forge_instant")
    if _score_animals(q) >= 30:
        return _dispatch_animals(query, q)
    if _has_build_verb(q):
        return "Quick mode is on — turn it off to build apps and games."
    if _score_greeting(q) >= 50:
        return "Hey! How can I help?"
    return f"I'm not sure about \"{query}\". Try turning off Quick mode for a full answer."

# --- MAIN ENTRY POINT ---

def generate_response(query: str, mode: str, history: list, quick_mode: bool = False) -> str:
    q = _normalize(query)
    if quick_mode:
        return _quick_response(query, q)
    if is_update_request(q, history):
        return _dispatch_update(query, history, mode)
    if _score_animals(q) >= 60:
        return _dispatch_animals(query, q)
    build_verb_score = 65 if _has_build_verb(q) and not _match(q, *(_GAME_NOUNS | _APP_NOUNS)) else 0
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
        "animals":     _score_animals(q),
        "knowledge":   _score_knowledge(q),
    }
    best_intent = max(scores, key=lambda k: scores[k])
    best_score = scores[best_intent]
    if best_score < 30:
        from services.web_search import web_lookup
        return web_lookup(query)
    if best_intent == "greeting":
        return _dispatch_greeting(mode)
    if best_intent == "build_game":
        return _dispatch_game(query, q, mode)
    if best_intent == "build_any":
        return _dispatch_dynamic(query, mode)
    if best_intent == "build_app":
        if _match(q, *_APP_NOUNS):
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
    if best_intent == "animals":
        return _dispatch_animals(query, q)
    if best_intent == "knowledge":
        for key, answer in GENERAL_KNOWLEDGE.items():
            if key in q or q in key:
                return answer
    from services.web_search import web_lookup
    return web_lookup(query)
