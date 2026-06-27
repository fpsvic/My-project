"""
code_generator.py — ForgeAI Multi-File Project Generator

Wraps game_compiler, app_builder, and dynamic_builder.
Splits their single-file HTML output into separate index.html / style.css / app.js
files and returns a structured project dict.

Entry points:
    generate_project(query: str) -> ProjectResult
"""

from __future__ import annotations

import re

from services.game_compiler import compile_game, _detect_genre
from services.app_builder import build_app, detect_app_type
from services.dynamic_builder import build_dynamic_app


# ─── Types ────────────────────────────────────────────────────────────────────

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
        self.kind = kind   # "game" | "app"
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
    from services.synthesis_engine import synthesize_game, should_synthesize, _extract_game_features, _build_game_title

    q = query.lower()
    genre = _detect_genre(q)

    # For complex/custom descriptions, use the synthesis engine
    if genre == "universal" or should_synthesize(query):
        code = synthesize_game(query)
        feat = _extract_game_features(q)
        title = _build_game_title(q, feat)
    else:
        compiled = compile_game(query)
        title = compiled.get("title", "Game")
        code = compiled.get("code", "")

    js_name = "game.js"
    files = split_html_to_files(code, js_name)
    return ProjectResult(title=title, kind="game", files=files)


# ─── App Project ──────────────────────────────────────────────────────────────

def generate_app_project(query: str) -> ProjectResult:
    q = query.lower()
    static_type = detect_app_type(q)

    if static_type:
        built = build_app(query)
    else:
        built = build_dynamic_app(query)

    title = built.get("title", "App")
    code = built.get("code", "")

    files = split_html_to_files(code, "app.js")
    return ProjectResult(title=title, kind="app", files=files)


# ─── Main entry point ─────────────────────────────────────────────────────────

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
    """Main entry point. Returns a ProjectResult with title, kind, and files."""
    if _is_game_query(query):
        return generate_game_project(query)
    return generate_app_project(query)
