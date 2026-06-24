import re
from data.knowledge_base import (
    LANG_HISTORY,
    LANG_HELLO_WORLD,
    SPACE_KEYWORDS,
    EARTH_KEYWORDS,
    ADVANCED_SCIENCE_KEYWORDS,
    POLITICAL_KEYWORDS,
)
from services.math_engine import generate_math_response
from services.space_engine import generate_space_response
from services.earth_engine import generate_earth_response
from services.science_engine import generate_science_response
from services.history_engine import generate_history_response
from services.game_compiler import compile_game
from services.fallback_apis import call_fallback_apis

_GREETINGS = {
    "hello", "hi", "hey", "sup", "greetings", "how are you",
    "who are you", "whats up", "good morning", "good afternoon",
}

_MATH_KEYWORDS = {
    "derivative", "integral", "integrate", "antiderivative",
    "sin", "cos", "tan", "csc", "sec", "cot",
}

_GAME_GENRES = {
    "pong", "snake", "tictactoe", "flappy", "arcade",
    "brick", "clicker", "shooter",
}


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


def _is_game_request(q: str) -> bool:
    if re.search(r"(make|create|play|build|code)\s+.*game", q):
        return True
    return any(g in q for g in _GAME_GENRES)


def generate_general_response(query: str, mode: str) -> str:
    q = query.lower().strip()

    # Language history lookup
    for lang, history in LANG_HISTORY.items():
        if lang in q and any(w in q for w in ("history", "origin", "created", "designed", "who made", "when")):
            hw = LANG_HELLO_WORLD.get(lang, "")
            code_block = f'\n\n```{lang}\n{hw}\n```' if hw else ""
            return (
                f"### {lang.capitalize()} Language Origin\n\n"
                f"{history}{code_block}"
            )

    return (
        f"### ForgeAI Cognitive Response\n\n"
        f"I have processed your query regarding **\"{query}\"**.\n\n"
        "I can help you with:\n"
        "- **Calculus & Trigonometry** — derivatives, integrals, trig ratios\n"
        "- **Space Science** — orbital distances, cosmic constants, planetary data\n"
        "- **Earth Science** — geology, volcanology, oceanography\n"
        "- **Advanced Science** — quantum physics, chemistry, genetics\n"
        "- **History** — US presidential history, party systems\n"
        "- **Games** — build Snake, Pong, Flappy Bird, Space Shooter, and more\n\n"
        "Type a specific question or try one of the suggestions above!"
    )


def generate_response(query: str, mode: str, history: list) -> str:
    q = query.lower().strip()

    # Greeting check
    for g in _GREETINGS:
        if q == g or q.startswith(g + " ") or q.startswith(g + "?") or q.startswith(g + "!"):
            return (
                f"Hello! I am **ForgeAI**, your cognitive local assistant running in **{mode}** mode.\n\n"
                "I can help with math, space science, earth science, programming history, "
                "US history, and building playable games. How can I help you today?"
            )

    # Game compiler
    if _is_game_request(q):
        game = compile_game(query)
        intro = (
            f"I have analyzed your parameters and compiled **{game['title']}**. "
            "Click **\"Play Game\"** inside the code box to run it instantly!"
        )
        code_block = f"\n\n```html\n{game['code']}\n```"
        if mode == "forge_thinking":
            return (
                f"### <i class=\"fa-solid fa-brain text-amber-500 mr-2\"></i> Thinking Process\n"
                f"- **Target Compilation**: {game['title']}.\n"
                f"- **Keywords Analyzed**: theme, speed, genre, obstacles.\n"
                f"- **Output**: Embedded dynamic Canvas frame.\n\n---\n\n"
                f"{intro}{code_block}"
            )
        return intro + code_block

    # Political / history
    if any(kw in q for kw in POLITICAL_KEYWORDS):
        return generate_history_response(query, mode)

    # Math
    if any(kw in q for kw in _MATH_KEYWORDS) or _is_math_expression(query):
        return generate_math_response(query, mode)

    # Space
    if any(kw in q for kw in SPACE_KEYWORDS):
        return generate_space_response(query, mode)

    # Earth science
    if any(kw in q for kw in EARTH_KEYWORDS):
        return generate_earth_response(query, mode)

    # Advanced science
    if any(kw in q for kw in ADVANCED_SCIENCE_KEYWORDS):
        return generate_science_response(query, mode)

    # Try external API fallback chain before the generic response
    fallback = call_fallback_apis(query, history)
    if fallback:
        return fallback

    return generate_general_response(query, mode)
