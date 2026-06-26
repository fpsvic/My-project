import re
from data.knowledge_base import (
    SPACE_KEYWORDS,
    EARTH_KEYWORDS,
    ADVANCED_SCIENCE_KEYWORDS,
    POLITICAL_KEYWORDS,
)
from data.database import (
    load_knowledge as _load_knowledge,
    load_lang_history as _load_lang_history,
    load_lang_hello_world as _load_lang_hello_world,
    load_code_examples as _load_code_examples,
)

# Load DB-backed dicts (cached in memory after first access)
GENERAL_KNOWLEDGE = _load_knowledge()
CODING_HELP       = _load_knowledge(categories=["coding"])
LANG_HISTORY      = _load_lang_history()
LANG_HELLO_WORLD  = _load_lang_hello_world()
LANG_EXAMPLES     = _load_code_examples()
from services.math_engine import generate_math_response
from services.space_engine import generate_space_response
from services.earth_engine import generate_earth_response
from services.science_engine import generate_science_response
from services.history_engine import generate_history_response
from services.game_compiler import compile_game
from services.app_builder import build_app, detect_app_type
from services.dynamic_builder import build_dynamic_app
from services.code_generator import generate_project
from services.update_handler import is_update_request, apply_update
from services.brain import forge, forge_greeting

# --- NORMALIZATION ---

def _normalize(raw: str) -> str:
    q = raw.lower().strip()
    q = re.sub(r"[''`]", "'", q)
    # expand common contractions so "what's" matches "what is" etc.
    q = q.replace("what's", "what is").replace("who's", "who is") \
         .replace("how's", "how is").replace("where's", "where is") \
         .replace("when's", "when is").replace("that's", "that is") \
         .replace("it's", "it is").replace("there's", "there is") \
         .replace("'s ", " is ").replace("'re ", " are ").replace("'ve ", " have ") \
         .replace("'ll ", " will ").replace("'d ", " would ").replace("n't", " not")
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
    "help me build", "help me create", "help me make",
    "i want to build", "i want to create", "i want to make",
    "i'm building", "i am building",
    "write me", "write me a", "write me an",
    "build me", "build me a", "build me an",
    "create me", "create me a",
    "code me", "code me a", "code me an",
    "i need you to build", "i need you to make", "i need you to create",
    "i'd like you to build", "i'd like you to make",
    "lets build", "let's build", "let's make", "lets make",
    "make something like", "something like",
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
    for v in _BUILD_VERBS:
        v = v.strip()
        if q == v:
            return True
        if q.startswith(v + " "):
            return True
        if f" {v} " in q:
            return True
        if q.endswith(" " + v):
            return True
    return False

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
    "mineral", "fossil", "glacier", "erosion", "subduction",
    "hydrothermal", "black smoker", "ocean floor",
}
_EARTH_STRONG_WORDS = {
    "rock", "vent", "mineral",
}

def _score_earth(q: str) -> int:
    score = 0
    if _match(q, *_EARTH_STRONG):
        score += 80
    # whole-word only for short ambiguous terms
    if any(re.search(r'\b' + re.escape(w) + r'\b', q) for w in _EARTH_STRONG_WORDS):
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
    return forge_greeting(mode)

_ASPECT_KEYWORDS = {
    "speed":       ["fast", "speed", "mph", "km/h", "quick", "run", "swim", "fly", "sprint", "velocity", "knot"],
    "size":        ["big", "size", "large", "heavy", "weight", "tall", "long", "huge", "giant", "small", "diameter", "radius", "mass", "meter", "km", "mile", "wide"],
    "diet":        ["eat", "diet", "food", "feed", "prey on", "hunt", "consume", "herbivore", "carnivore", "omnivore"],
    "habitat":     ["live", "habitat", "home", "found", "range", "region", "continent", "where", "ocean", "forest", "desert", "biome"],
    "predator":    ["predator", "threat", "eats", "hunted by", "enemy", "danger"],
    "lifespan":    ["lifespan", "age", "years", "live for", "lives up to", "live up to", "life span"],
    "behavior":    ["behave", "social", "pack", "group", "herd", "pride", "lone", "nocturnal", "sleep", "smart", "intelligent", "communicate"],
    "temperature": ["hot", "cold", "temperature", "degrees", "celsius", "fahrenheit", "kelvin", "warm", "heat", "°c", "°f"],
    "distance":    ["far", "distance", "away", "light-year", "light year", "parsec", "au ", "km from", "miles from", "million km", "billion km"],
    "date":        ["when", "year", "date", "age", "old", "founded", "born", "invented", "discovered", "created", "established", "built", "started", "fell", "ended", "began", "happened"],
    "count":       ["how many", "number of", "count", "moons", "planets", "species", "bones", "teeth", "legs", "eyes", "heart"],
    "composition": ["made of", "consist", "composed", "element", "chemical", "formula", "contain", "ingredient", "structure", "makeup"],
    "inventor":    ["who made", "who invented", "who created", "who discovered", "who built", "who designed", "inventor", "creator", "discovered by", "founded by"],
}

_ASPECT_INTROS = {
    "speed":       ["Speed-wise, ", "When it comes to speed, ", "In terms of how fast — ", ""],
    "size":        ["Size-wise, ", "As for size, ", "In terms of size, ", ""],
    "diet":        ["Diet-wise, ", "As for what they eat — ", "When it comes to food, ", ""],
    "habitat":     ["Habitat-wise, ", "As for where they live — ", "In terms of range, ", ""],
    "predator":    ["As for predators — ", "In the wild, ", "When it comes to threats — ", ""],
    "lifespan":    ["Lifespan-wise, ", "In terms of how long they live — ", ""],
    "behavior":    ["Behaviour-wise, ", "As for how they act — ", ""],
    "temperature": ["Temperature-wise, ", "In terms of heat — ", ""],
    "distance":    ["Distance-wise, ", "In terms of how far — ", ""],
    "date":        ["", "In terms of when — ", "Historically, "],
    "count":       ["", "As for the number — ", ""],
    "composition": ["In terms of what it's made of — ", "Composition-wise, ", ""],
    "inventor":    ["", "As for who made it — ", "Credit-wise, "],
}

import random

def _is_heading_line(s: str) -> bool:
    if re.match(r'^#{1,4}\s', s):
        return True
    words = s.split()
    if len(words) <= 4 and not re.search(r'\d|is |are |was |were |have |has |can |do |does ', s.lower()):
        return True
    return False

def _extract_aspect(answer: str, aspect: str) -> str | None:
    keywords = _ASPECT_KEYWORDS.get(aspect, [])
    lines = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', answer) if s.strip()]
    clean = [re.sub(r'[*#>`_]+', '', l).strip() for l in lines]
    matches = [
        clean[i] for i, l in enumerate(clean)
        if any(k in l.lower() for k in keywords)
        and len(clean[i]) > 15
        and not _is_heading_line(clean[i])
    ]
    if not matches:
        return None
    intro = random.choice(_ASPECT_INTROS.get(aspect, [""]))
    return intro + "  ".join(matches[:2])

_SPECIFIC_PATTERNS = [
    (r"how (fast|quick|speedy)", "speed"),
    (r"how (big|large|heavy|tall|wide|long|massive|small|tiny)", "size"),
    (r"how (hot|cold|warm|cool)", "temperature"),
    (r"how far", "distance"),
    (r"how many", "count"),
    (r"how old (is|was|are|were|do)", "date"),
    (r"how long (does|do|did|will|can|could).{0,20}(live|last|take|survive)", "lifespan"),
    (r"what (year|date|time) (did|was|were|is)", "date"),
    (r"when (did|was|were|is|does)", "date"),
    (r"who (made|invented|created|discovered|built|designed|founded)", "inventor"),
    (r"what is (it|[\w\s]+) made of", "composition"),
    (r"what (eats|hunts|kills|attacks|preys on)", "predator"),
    (r"what (do|does|did).{0,30}eat", "diet"),
    (r"where (do|does|did).{0,30}(live|found|come from|habitat|home)", "habitat"),
]

def _detect_aspect(q: str) -> str | None:
    for pattern, aspect in _SPECIFIC_PATTERNS:
        if re.search(pattern, q):
            return aspect
    for aspect, keywords in _ASPECT_KEYWORDS.items():
        if any(k in q for k in keywords):
            return aspect
    return None

_QUESTION_STARTERS = re.compile(
    r"^(what is|what are|what does|what do|what did|what was|what were|"
    r"how (fast|big|hot|cold|far|many|much|long|old|deep|high|wide|heavy|tall|large|small|often)|"
    r"how does|how do|how did|how is|how are|how was|"
    r"when (did|was|were|is|does|do|will)|"
    r"where (do|does|did|is|are|was|were|can)|"
    r"who (made|invented|created|discovered|built|designed|founded|was|is|are)|"
    r"why (do|does|did|is|are|was|were)|"
    r"which (is|are|was|were|has|have)|"
    r"can a|can the|could a|does a|do|is a|is the|are there)\s+"
)

_STOP_WORDS = {
    "a","an","the","is","are","was","were","do","does","did","have","has","had",
    "be","been","being","of","in","on","at","to","for","with","by","from","as",
    "it","its","i","me","my","you","your","he","she","we","they","this","that",
    "and","or","but","so","if","not","about","how","what","when","where","who",
    "why","which","can","could","would","should","will","just","very","also",
    "tell","give","explain","describe",
    # generic quantity / question words that cannot distinguish KB keys
    "many","much","more","less","some","any","all","every","each","few","most",
    "number","get","let","put","way","thing","things","lot",
}

def _query_keywords(q: str) -> list[str]:
    """Extract meaningful keywords from the query for matching against answer sentences."""
    stripped = _QUESTION_STARTERS.sub("", q).strip()
    words = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", stripped)
    return [w for w in words if w not in _STOP_WORDS and len(w) > 2]

def _try_extract_fact(answer: str, q: str) -> str | None:
    """Try to pull just the specific fact from a longer answer.
    First tries aspect-keyword matching; falls back to query-keyword scoring."""
    # 1. Try predefined aspect extraction
    aspect = _detect_aspect(q)
    if aspect:
        result = _extract_aspect(answer, aspect)
        if result:
            return result
    # 2. Universal: only engage if it looks like a specific question
    if not _QUESTION_STARTERS.match(q):
        return None
    kws = _query_keywords(q)
    if not kws:
        return None
    raw_lines = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', answer) if s.strip()]
    clean = [re.sub(r'[*#>`_\-]+', '', l).strip() for l in raw_lines]
    # Score each sentence by how many query keywords it contains; skip headings
    scored = []
    for sent in clean:
        if _is_heading_line(sent):
            continue
        low = sent.lower()
        hits = sum(1 for w in kws if w in low)
        if hits > 0 and len(sent) > 15:
            scored.append((hits, sent))
    if not scored:
        return None
    # Boost sentences that contain a number/unit (more likely to be the direct answer)
    scored.sort(key=lambda x: (-(x[0] * 2 + bool(re.search(r'\d', x[1])))))
    top = [s for _, s in scored[:2]]
    return "  ".join(top)

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

def _dispatch_project(query: str, kind: str = "auto") -> dict:
    """Generate a multi-file project and return a response dict."""
    project = generate_project(query)
    verb = "compiled" if project.kind == "game" else "built"
    action = "Play Game" if project.kind == "game" else "Run Project"
    n = len(project.files)
    intro = (
        f"I {verb} **{project.title}** — {n} file{'s' if n != 1 else ''} generated. "
        f"Browse the files below, then hit **\"{action}\"** to launch."
    )
    return {
        "text": intro,
        "project_files": [{"name": f.name, "content": f.content, "language": f.language} for f in project.files],
    }

# Keep these for backward compat — now all go through _dispatch_project
def _dispatch_game(query: str, q: str, mode: str) -> dict:
    return _dispatch_project(query, "game")

def _dispatch_app(query: str, mode: str) -> dict:
    return _dispatch_project(query, "app")

def _dispatch_dynamic(query: str, mode: str) -> dict:
    return _dispatch_project(query, "app")

def _dispatch_update(query: str, history: list, mode: str) -> str | dict:
    from services.update_handler import extract_last_project
    result = apply_update(query, history)

    if isinstance(result, dict) and "files" in result:
        kind = result.get("kind", "app")
        title = result.get("title", "Project")
        files = result["files"]
        verb = "updated" if kind == "game" else "rebuilt"
        action = "Play Game" if kind == "game" else "Run Project"
        n = len(files)
        intro = (
            f"I {verb} **{title}** — {n} file{'s' if n != 1 else ''} updated. "
            f"Browse the changes below, then hit **\"{action}\"** to launch."
        )
        return {
            "text": intro,
            "project_files": files,
        }

    # Legacy: inline HTML response
    code = result.get("code", "")
    title = result.get("title", "App")
    intro = (
        f"I updated the app — here is **{title}**. "
        "Click **\"Launch App\"** to see the changes live."
    )
    return intro + f"\n\n```html\n{code}\n```"

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
    # Synthesize a response for unrecognized programming questions
    return _synthesize_programming_response(query, q)

# --- SYNTHESIZED PROGRAMMING RESPONSES ---

_CONCEPT_RESPONSES: dict[str, str] = {
    "game loop": (
        "### Game Loop Pattern\n\n"
        "A game loop runs continuously, updating state and rendering every frame.\n\n"
        "```javascript\nlet lastTime = 0;\n\nfunction gameLoop(timestamp) {\n"
        "  const dt = (timestamp - lastTime) / 1000; // delta in seconds\n"
        "  lastTime = timestamp;\n\n"
        "  update(dt);  // move entities, check physics\n"
        "  render();    // draw to canvas\n\n"
        "  requestAnimationFrame(gameLoop);\n}\n\nrequestAnimationFrame(gameLoop);\n```\n\n"
        "**`requestAnimationFrame`** syncs to the display refresh rate (~60fps) and pauses when the tab is hidden, saving CPU."
    ),
    "collision detection": (
        "### Collision Detection\n\n"
        "**AABB (Axis-Aligned Bounding Box)** — fastest, works for rectangles:\n\n"
        "```javascript\nfunction collides(a, b) {\n"
        "  return a.x < b.x + b.w &&\n"
        "         a.x + a.w > b.x &&\n"
        "         a.y < b.y + b.h &&\n"
        "         a.y + a.h > b.y;\n}\n```\n\n"
        "**Circle collision** — for round objects:\n\n"
        "```javascript\nfunction circlesCollide(a, b) {\n"
        "  const dx = a.x - b.x, dy = a.y - b.y;\n"
        "  return Math.hypot(dx, dy) < a.r + b.r;\n}\n```"
    ),
    "canvas": (
        "### HTML5 Canvas Basics\n\n"
        "```javascript\nconst canvas = document.getElementById('c');\n"
        "const ctx = canvas.getContext('2d');\n\n"
        "// Clear\nctx.clearRect(0, 0, canvas.width, canvas.height);\n\n"
        "// Rectangle\nctx.fillStyle = '#6366f1';\nctx.fillRect(x, y, width, height);\n\n"
        "// Circle\nctx.beginPath();\nctx.arc(cx, cy, radius, 0, Math.PI * 2);\nctx.fill();\n\n"
        "// Text\nctx.font = '16px monospace';\nctx.fillText('Score: 0', 10, 20);\n```"
    ),
    "localStorage": (
        "### localStorage Persistence\n\n"
        "Stores key-value strings in the browser — survives page refresh.\n\n"
        "```javascript\n// Save\nlocalStorage.setItem('score', JSON.stringify(data));\n\n"
        "// Load\nconst raw = localStorage.getItem('score');\nconst data = raw ? JSON.parse(raw) : defaultValue;\n\n"
        "// Delete\nlocalStorage.removeItem('score');\n```\n\n"
        "**Tip:** Always wrap in `try/catch` — storage can throw if the browser is in private mode with a full quota."
    ),
    "event listener": (
        "### Event Listeners in JS\n\n"
        "```javascript\n// Keyboard\ndocument.addEventListener('keydown', (e) => {\n"
        "  if (e.key === 'ArrowLeft') moveLeft();\n"
        "  if (e.key === ' ') jump();\n  e.preventDefault();\n});\n\n"
        "// Mouse\ncanvas.addEventListener('click', (e) => {\n"
        "  const rect = canvas.getBoundingClientRect();\n"
        "  const x = e.clientX - rect.left;\n  const y = e.clientY - rect.top;\n"
        "  handleClick(x, y);\n});\n\n"
        "// Remove when done\nconst handler = (e) => { ... };\nwindow.addEventListener('resize', handler);\n// later:\nwindow.removeEventListener('resize', handler);\n```"
    ),
    "promise": (
        "### Promises & Async/Await\n\n"
        "```javascript\n// Promise\nfetch('/api/data')\n  .then(res => res.json())\n"
        "  .then(data => console.log(data))\n  .catch(err => console.error(err));\n\n"
        "// Async/await — same thing, cleaner syntax\nasync function getData() {\n"
        "  try {\n    const res = await fetch('/api/data');\n"
        "    const data = await res.json();\n    return data;\n"
        "  } catch (err) {\n    console.error(err);\n  }\n}\n```\n\n"
        "**Rule:** `await` only works inside `async` functions. At the top level of a module, it works directly."
    ),
    "closure": (
        "### Closures in JavaScript\n\n"
        "A closure is a function that remembers variables from its outer scope even after that scope exits.\n\n"
        "```javascript\nfunction makeCounter(start = 0) {\n  let count = start; // captured by closure\n"
        "  return {\n    increment: () => ++count,\n    decrement: () => --count,\n"
        "    value: () => count,\n  };\n}\n\nconst counter = makeCounter(10);\ncounter.increment(); // 11\ncounter.value();     // 11\n```\n\n"
        "This is how React hooks, module patterns, and factory functions work internally."
    ),
    "recursion": (
        "### Recursion\n\n"
        "A function calling itself until a base case is reached.\n\n"
        "```javascript\n// Factorial\nfunction factorial(n) {\n"
        "  if (n <= 1) return 1;       // base case\n"
        "  return n * factorial(n - 1); // recursive step\n}\n\n"
        "// Fibonacci (with memoization)\nconst memo = {};\nfunction fib(n) {\n"
        "  if (n <= 1) return n;\n  if (memo[n]) return memo[n];\n"
        "  return memo[n] = fib(n - 1) + fib(n - 2);\n}\n```\n\n"
        "**Stack depth**: browsers typically allow ~10,000 recursive calls before a stack overflow. Use iteration for deep recursion."
    ),
    "sort": (
        "### Sorting in JavaScript\n\n"
        "```javascript\n// Numbers (default sort is lexicographic — always pass comparator!)\n"
        "const nums = [10, 2, 8, 1];\nnums.sort((a, b) => a - b);  // ascending: [1, 2, 8, 10]\nnums.sort((a, b) => b - a);  // descending\n\n"
        "// Objects by field\nconst users = [{name: 'Bob', age: 30}, {name: 'Ana', age: 25}];\nusers.sort((a, b) => a.age - b.age);\n"
        "users.sort((a, b) => a.name.localeCompare(b.name));\n\n"
        "// Stable sort (guaranteed since ES2019)\n```"
    ),
    "debounce": (
        "### Debounce & Throttle\n\n"
        "**Debounce** — wait until the user stops typing:\n\n"
        "```javascript\nfunction debounce(fn, delay) {\n  let timer;\n"
        "  return (...args) => {\n    clearTimeout(timer);\n"
        "    timer = setTimeout(() => fn(...args), delay);\n  };\n}\n\n"
        "const onSearch = debounce((q) => fetchResults(q), 300);\ninput.addEventListener('input', (e) => onSearch(e.target.value));\n```\n\n"
        "**Throttle** — limit to once per interval:\n\n"
        "```javascript\nfunction throttle(fn, limit) {\n  let last = 0;\n"
        "  return (...args) => {\n    const now = Date.now();\n"
        "    if (now - last >= limit) { last = now; fn(...args); }\n  };\n}\n```"
    ),
    "regex": (
        "### Regular Expressions\n\n"
        "```javascript\n// Test a pattern\n/^\\d{3}-\\d{4}$/.test('555-1234'); // true\n\n"
        "// Extract matches\nconst email = 'Send to bob@example.com please';\nconst m = email.match(/[\\w.+-]+@[\\w-]+\\.[a-z]{2,}/i);\nconsole.log(m?.[0]); // 'bob@example.com'\n\n"
        "// Replace all\nconst slug = 'Hello World!'.toLowerCase().replace(/[^a-z0-9]+/g, '-'); // 'hello-world-'\n\n"
        "// Named groups\nconst { year, month } = '2024-07'.match(/(?<year>\\d{4})-(?<month>\\d{2})/).groups;\n```"
    ),
    "api": (
        "### REST API Calls\n\n"
        "```javascript\n// GET\nconst data = await fetch('https://api.example.com/items').then(r => r.json());\n\n"
        "// POST with JSON body\nconst res = await fetch('/api/items', {\n  method: 'POST',\n"
        "  headers: { 'Content-Type': 'application/json' },\n"
        "  body: JSON.stringify({ name: 'Widget', price: 9.99 }),\n});\nconst created = await res.json();\n\n"
        "// Error handling\nif (!res.ok) throw new Error(`HTTP ${res.status}`);\n```"
    ),
    "class": (
        "### Classes in JavaScript\n\n"
        "```javascript\nclass Entity {\n  #health; // private field\n\n"
        "  constructor(x, y, health = 100) {\n    this.x = x;\n    this.y = y;\n    this.#health = health;\n  }\n\n"
        "  move(dx, dy) {\n    this.x += dx;\n    this.y += dy;\n  }\n\n"
        "  takeDamage(amount) {\n    this.#health = Math.max(0, this.#health - amount);\n  }\n\n"
        "  get isAlive() { return this.#health > 0; }\n}\n\n"
        "class Player extends Entity {\n  shoot() { return new Bullet(this.x, this.y); }\n}\n```"
    ),
    "array": (
        "### Array Methods — The Essential Ones\n\n"
        "```javascript\nconst nums = [1, 2, 3, 4, 5];\n\n"
        "nums.map(n => n * 2)       // [2, 4, 6, 8, 10] — transform each\n"
        "nums.filter(n => n > 2)    // [3, 4, 5] — keep matching\n"
        "nums.reduce((s, n) => s+n) // 15 — collapse to one value\n"
        "nums.find(n => n > 3)      // 4 — first match\n"
        "nums.some(n => n > 4)      // true — any match?\n"
        "nums.every(n => n > 0)     // true — all match?\n"
        "nums.flat(Infinity)        // flatten nested arrays\n"
        "nums.flatMap(n => [n, n*2])// map + flatten one level\n\n"
        "// Chaining\nconst result = items\n  .filter(i => i.active)\n"
        "  .map(i => i.name)\n  .sort();\n```"
    ),
    "state management": (
        "### State Management Pattern\n\n"
        "Simple reactive state without a framework:\n\n"
        "```javascript\nconst state = {\n  items: [],\n  filter: 'all',\n  _listeners: new Set(),\n\n"
        "  on(fn) { this._listeners.add(fn); },\n"
        "  emit() { this._listeners.forEach(fn => fn(this)); },\n\n"
        "  addItem(item) {\n    this.items.push(item);\n    this.emit();\n  },\n"
        "  setFilter(f) {\n    this.filter = f;\n    this.emit();\n  },\n};\n\n"
        "// Subscribe to changes\nstate.on((s) => renderList(s.items.filter(filterFn(s.filter))));\n```"
    ),
    "dark mode": (
        "### Dark Mode Toggle\n\n"
        "```javascript\n// Toggle and persist\nfunction toggleDarkMode() {\n"
        "  const isDark = document.documentElement.classList.toggle('dark');\n"
        "  localStorage.setItem('theme', isDark ? 'dark' : 'light');\n}\n\n"
        "// Restore on load\nconst saved = localStorage.getItem('theme') ??\n"
        "  (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');\n"
        "if (saved === 'dark') document.documentElement.classList.add('dark');\n```\n\n"
        "```css\n:root { --bg: #fff; --text: #0f172a; }\n.dark { --bg: #0f172a; --text: #f1f5f9; }\nbody { background: var(--bg); color: var(--text); }\n```"
    ),
}

_CONCEPT_KEYWORDS: list[tuple[list[str], str]] = [
    (["game loop", "game loop", "requestanimationframe", "animation frame", "update render", "game tick"], "game loop"),
    (["collision", "collide", "hit detection", "overlap", "aabb", "bounding box"], "collision detection"),
    (["canvas", "ctx", "context", "drawimage", "fillrect", "arc", "html5 canvas"], "canvas"),
    (["localstorage", "local storage", "persist", "save data", "browser storage"], "localStorage"),
    (["event listener", "addeventlistener", "keydown", "keyup", "mousemove", "onclick"], "event listener"),
    (["promise", "async", "await", "then", "fetch", "asynchronous"], "promise"),
    (["closure", "closures", "lexical scope", "captured variable"], "closure"),
    (["recursion", "recursive", "base case", "call itself"], "recursion"),
    (["sort", "sorting", "order", "compare", "localecompare"], "sort"),
    (["debounce", "throttle", "rate limit", "delay input"], "debounce"),
    (["regex", "regular expression", "regexp", "pattern match"], "regex"),
    (["api", "fetch", "rest", "endpoint", "http request", "post request", "get request"], "api"),
    (["class", "oop", "object oriented", "inheritance", "extends", "constructor"], "class"),
    (["array", "map filter reduce", "flatmap", "array method", "iterate array"], "array"),
    (["state", "state management", "reactive", "subscribe", "observer"], "state management"),
    (["dark mode", "night mode", "theme toggle", "color scheme", "prefers-color-scheme"], "dark mode"),
]


def _synthesize_programming_response(query: str, q: str) -> str:
    """Give a real answer for programming questions that don't match the KB."""
    # Check synthesized concept map
    for keywords, concept_key in _CONCEPT_KEYWORDS:
        if any(kw in q for kw in keywords):
            return _CONCEPT_RESPONSES[concept_key]

    # Fall back to web search for truly unknown programming questions
    from services.web_search import web_lookup
    return web_lookup(query)

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

# ── CONVERSATION MEMORY ───────────────────────────────────────────────────────

_FOLLOWUP_EXACT = {
    "tell me more", "more", "more about that", "more about it", "more info",
    "elaborate", "expand", "expand on that", "go deeper", "keep going",
    "continue", "go on", "and?", "what else", "anything else",
    "explain that", "explain more", "explain further", "explain it",
    "interesting", "cool", "wow", "nice", "really?", "what about it",
    "how so", "why so", "ok and", "okay and", "got it and",
    "ok so", "okay so", "go ahead", "tell me", "say more",
    "then what", "so what", "and then", "keep talking", "more please",
    "go on then", "interesting tell me more", "thats cool", "that's cool",
    "thats interesting", "that's interesting", "i see", "oh interesting",
    "oh cool", "oh wow", "and what else", "what more", "anything more",
    "tell me everything", "keep going please", "more details", "more detail",
    "give me more", "give more details", "expand more",
}

_FOLLOWUP_STARTS = (
    "tell me more about", "more about", "what else about",
    "can you explain", "explain more about", "expand on",
    "what about its", "what about their", "what about the",
    "how about", "what about", "and what about", "but what about",
    "also what", "also how", "also why", "also when", "also where",
    "so how", "so what", "so why", "so when",
)

_PRONOUN_RE = re.compile(
    r"\b(it|its|it's|they|them|their|that|this|those|these|he|she|him|her)\b"
)


def _is_followup_query(q: str) -> bool:
    """Return True if q is clearly a follow-up with no new subject."""
    if q in _FOLLOWUP_EXACT:
        return True
    if any(q.startswith(p) for p in _FOLLOWUP_STARTS):
        return True
    # Short pronoun-heavy queries
    words = [w for w in q.split() if w not in _STOP_WORDS]
    if len(words) <= 3 and _PRONOUN_RE.search(q):
        return True
    return False


def _extract_entity(text: str) -> str | None:
    """Pull the most likely subject noun phrase from a query string."""
    norm = _normalize(text)
    norm = _QUESTION_STARTERS.sub("", norm).strip()
    words = [w for w in norm.split() if w not in _STOP_WORDS]
    if not words:
        return None
    return " ".join(words[:4])


def _get_all_user_msgs(history: list) -> list[str]:
    """Return all user message texts from history, in order."""
    msgs = []
    for msg in history:
        if msg.get("role") == "user":
            text = (msg.get("text") or msg.get("content") or "").strip()
            if text:
                msgs.append(text)
    return msgs


def build_conversation_memory(history: list) -> dict:
    """
    Analyse the full conversation history and return a memory dict:
      active_topic   — the real subject of the current thread (original query text)
      active_entity  — extracted noun phrase from active_topic
      thread_depth   — how many consecutive turns have been about this topic
      covered_aspects — aspects already discussed (speed, diet, etc.)
      all_topics     — all distinct (non-follow-up) topics seen this session
      prev_ai_texts  — list of previous AI response texts (for context)
    """
    user_msgs = _get_all_user_msgs(history)
    # Remove current message (last in list) — we only look at what came before
    prev_user_msgs = user_msgs[:-1] if len(user_msgs) > 1 else []

    ai_texts = []
    for msg in history:
        if msg.get("role") == "assistant":
            text = (msg.get("text") or msg.get("content") or "").strip()
            if text:
                ai_texts.append(text)

    if not prev_user_msgs:
        return {
            "active_topic": None, "active_entity": None, "thread_depth": 0,
            "covered_aspects": [], "all_topics": [], "prev_ai_texts": ai_texts,
        }

    # Walk back from end of history to find where the current topic thread began
    thread_anchor_idx = len(prev_user_msgs) - 1
    for i in range(len(prev_user_msgs) - 1, -1, -1):
        q_i = _normalize(prev_user_msgs[i])
        if _is_followup_query(q_i):
            continue   # part of the same thread, keep walking back
        thread_anchor_idx = i
        break

    active_topic = prev_user_msgs[thread_anchor_idx]
    thread_depth = len(prev_user_msgs) - thread_anchor_idx  # turns on this topic

    # Aspects already covered within this thread
    covered_aspects: list[str] = []
    for msg in prev_user_msgs[thread_anchor_idx:]:
        aspect = _detect_aspect(_normalize(msg))
        if aspect and aspect not in covered_aspects:
            covered_aspects.append(aspect)

    # All distinct topics seen this session (non-follow-up messages)
    all_topics = []
    for msg in prev_user_msgs:
        if not _is_followup_query(_normalize(msg)):
            all_topics.append(msg)

    return {
        "active_topic": active_topic,
        "active_entity": _extract_entity(active_topic),
        "thread_depth": thread_depth,
        "covered_aspects": covered_aspects,
        "all_topics": all_topics,
        "prev_ai_texts": ai_texts,
    }


def _resolve_context(query: str, q: str, history: list) -> tuple[str, str, dict]:
    """
    Rewrite a follow-up query using full conversation memory.
    Returns (resolved_query, normalized_q, memory_dict).
    """
    mem = build_conversation_memory(history)
    active_topic = mem.get("active_topic")

    if not active_topic:
        return query, q, mem

    entity = mem.get("active_entity") or ""

    # 1. Pure follow-up → expand into full topic question
    if q in _FOLLOWUP_EXACT:
        covered = mem.get("covered_aspects", [])
        # Pick an uncovered aspect to go deeper on
        all_aspects = ["speed", "size", "diet", "habitat", "behavior",
                       "lifespan", "composition", "date", "inventor", "count"]
        uncovered = [a for a in all_aspects if a not in covered]
        if uncovered and mem.get("thread_depth", 0) >= 1:
            next_aspect = uncovered[0]
            combined = f"what is the {next_aspect} of {active_topic}" \
                if not any(w in active_topic.lower() for w in ["what", "how", "why", "when", "who"]) \
                else f"tell me more about {active_topic}"
        else:
            combined = f"tell me more about {active_topic}"
        return combined, _normalize(combined), mem

    # 2. Follow-up start phrases — inject entity
    if any(q.startswith(p) for p in _FOLLOWUP_STARTS):
        if entity and entity not in q:
            combined = f"{query.strip()} {entity}"
            return combined, _normalize(combined), mem
        return query, q, mem

    # 3. Short pronoun-heavy query — replace pronouns with entity
    words = [w for w in q.split() if w not in _STOP_WORDS]
    if len(words) <= 4 and _PRONOUN_RE.search(q) and entity:
        resolved = _PRONOUN_RE.sub(entity, query)
        return resolved, _normalize(resolved), mem

    # 4. New question on the same entity but different angle — preserve as-is
    return query, q, mem


# ── COMPREHENSIVE RESPONSE BUILDER ───────────────────────────────────────────

def _related_kb_entries(entity: str, exclude_keys: list[str] | None = None) -> list[str]:
    """Find all KB answers that mention the entity."""
    exclude_keys = exclude_keys or []
    results = []
    ent = entity.lower()
    for key, answer in GENERAL_KNOWLEDGE.items():
        if key in exclude_keys:
            continue
        if ent in key or ent in answer.lower():
            results.append(answer)
    return results[:4]


def _build_comprehensive_response(topic: str, entity: str, memory: dict) -> str | None:
    """
    For deep follow-ups (thread_depth >= 2), build a rich multi-part response
    by pulling related KB entries and combining them.
    """
    q_topic = _normalize(topic)
    covered = memory.get("covered_aspects", [])

    # Gather the primary KB hit
    primary = _kb_fact_lookup(q_topic)
    if not primary:
        return None

    # Gather related entries about the same entity
    related = _related_kb_entries(entity or topic, [])
    # Filter: skip entries too similar to primary
    seen_tokens = set(re.findall(r"[a-z]{4,}", primary.lower()))
    unique_related = []
    for r in related:
        r_tokens = set(re.findall(r"[a-z]{4,}", r.lower()))
        overlap = len(seen_tokens & r_tokens) / max(len(r_tokens), 1)
        if overlap < 0.6 and r != primary:
            unique_related.append(r)

    if not unique_related:
        return None

    # Build a combined comprehensive text
    sections = [primary] + unique_related[:2]
    combined = "\n\n".join(sections)
    return combined


# --- MAIN ENTRY POINT ---

def _kb_fact_lookup(q: str) -> str | None:
    """Return a KB answer for factual questions.

    Pass 1 — direct substring: find the longest KB key that appears literally in the
    query (e.g. "speed of sound" matches "what is the speed of sound in air").

    Pass 2 — token overlap: for questions phrased differently from any key, require
    at least 2 meaningful token hits AND coverage ≥ 50% of the key's tokens.
    This avoids false positives like "many" matching "how many bones".
    """
    # Pass 1: longest key that is a literal substring of the query
    best_len, best_answer = 0, None
    for key, answer in GENERAL_KNOWLEDGE.items():
        if key in q and len(key) > best_len:
            best_len, best_answer = len(key), answer
    if best_answer and best_len >= 5:  # skip single-word key matches
        return best_answer  # let forge/vary_structure handle extraction

    # Pass 2: token-based fallback — only for question-form queries
    if not _QUESTION_STARTERS.match(q):
        return None
    q_tokens = set(re.findall(r"[a-z0-9]+", q)) - _STOP_WORDS
    if len(q_tokens) < 2:
        return None
    best_score, best_ratio, best_answer = 0, 0.0, None
    for key, answer in GENERAL_KNOWLEDGE.items():
        key_tokens = set(re.findall(r"[a-z0-9]+", key)) - _STOP_WORDS
        if not key_tokens:
            continue
        hits = len(q_tokens & key_tokens)
        if hits < 2:
            continue
        ratio = hits / len(key_tokens)
        if ratio < 0.5:
            continue
        if hits > best_score or (hits == best_score and ratio > best_ratio):
            best_score, best_ratio, best_answer = hits, ratio, answer
    return best_answer  # let forge/vary_structure handle extraction

def generate_response(query: str, mode: str, history: list, quick_mode: bool = False, workspace: str = "chat") -> str | dict:
    q = _normalize(query)
    if quick_mode:
        return _quick_response(query, q)
    # Resolve follow-up references using full conversation memory
    query, q, memory = _resolve_context(query, q, history)
    thread_depth = memory.get("thread_depth", 0)
    active_entity = memory.get("active_entity") or ""

    # Deep follow-up: try building a comprehensive multi-KB response
    if thread_depth >= 2 and active_entity and q not in _FOLLOWUP_EXACT:
        comp = _build_comprehensive_response(
            memory.get("active_topic") or query, active_entity, memory
        )
        if comp:
            return forge(comp, query, "knowledge", depth=thread_depth)

    if is_update_request(q, history):
        return _dispatch_update(query, history, mode)
    if _score_animals(q) >= 60:
        return forge(_dispatch_animals(query, q), q, "animals")
    # Universal specific-question pre-check: KB lookup beats domain engines
    kb_hit = _kb_fact_lookup(q)
    if kb_hit:
        return forge(kb_hit, q, "knowledge")
    code_mode = workspace == "code"
    BUILD_BOOST = 25 if code_mode else 0
    build_verb_score = 65 if _has_build_verb(q) and not _match(q, *(_GAME_NOUNS | _APP_NOUNS)) else 0
    scores: dict[str, int] = {
        "greeting":    _score_greeting(q),
        "build_game":  min(100, _score_build_game(q) + BUILD_BOOST),
        "build_app":   min(100, _score_build_app(q) + BUILD_BOOST),
        "build_any":   min(100, build_verb_score + BUILD_BOOST),
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
    if best_score < (20 if code_mode else 30):
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
        full = generate_space_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "space")
    if best_intent == "earth":
        full = generate_earth_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "earth")
    if best_intent == "science":
        full = generate_science_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "science")
    if best_intent == "history":
        full = generate_history_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "history")
    if best_intent == "programming":
        return _dispatch_programming(query, mode)
    if best_intent == "animals":
        raw = _dispatch_animals(query, q)
        return forge(raw, q, "animals")
    if best_intent == "knowledge":
        for key, answer in GENERAL_KNOWLEDGE.items():
            if key in q or q in key:
                fact = _try_extract_fact(answer, q)
                raw = fact if fact else answer
                return forge(raw, q, "knowledge")
    if code_mode and _has_build_verb(q):
        return _dispatch_project(query)
    from services.web_search import web_lookup
    return web_lookup(query)
