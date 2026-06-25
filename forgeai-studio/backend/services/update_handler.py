import re
from services.dynamic_builder import generate_crud_app, _detect_entity, _detect_features, _make_title

_UPDATE_SIGNALS = [
    r"\badd\b.{0,40}\bto it\b",
    r"\bnow also\b",
    r"\balso add\b",
    r"\bmake it also\b",
    r"\bchange the\b",
    r"\bupdate (it|the app|the tracker|the tool|the game)\b",
    r"\bcan you add\b",
    r"\binclude\b.{0,30}\bas well\b",
    r"\bmodify\b",
    r"\badjust\b",
    r"\btweak\b",
    r"\brename\b",
    r"\bremove the\b",
    r"\bget rid of the\b",
    r"\bswitch the\b",
    r"\bfix the\b",
    r"\bimprove the\b",
    r"\bmake it (dark|light|bigger|smaller|responsive|mobile|faster|slower|harder|easier)\b",
    r"\badd (more|extra|a)\b",
    r"\bcan you (make|change|add|fix|improve)\b",
    r"\bnow (make|add|change|fix)\b",
]


def is_update_request(query: str, history: list[dict]) -> bool:
    q = query.lower()
    has_signal = any(re.search(p, q) for p in _UPDATE_SIGNALS)
    if not has_signal:
        return False
    return extract_last_code(history) is not None


def extract_last_code(history: list[dict]) -> str | None:
    for msg in reversed(history):
        if msg.get("role") != "assistant":
            continue
        text = msg.get("content") or msg.get("text", "")
        m = re.search(r"```html\n([\s\S]*?)```", text)
        if m:
            return m.group(1).strip()
    return None


def _extract_title_from_code(code: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", code, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", code, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "App"


def _is_game_code(code: str) -> bool:
    return "<canvas" in code.lower()


_SPEED_PATCHES = [
    (
        ("faster", "speed up", "make it faster", "increase speed"),
        [
            (r"(setInterval\([^,]+,\s*)(\d+)(\s*\))",
             lambda m: m.group(1) + str(max(8, int(m.group(2)) - 30)) + m.group(3),
             {"count": 1}),
            (r"((?:speed|velocity|vel|spd)\s*=\s*)(\d+(?:\.\d+)?)",
             lambda m: m.group(1) + str(round(float(m.group(2)) * 1.4, 1)),
             {}),
        ],
    ),
    (
        ("slower", "slow down", "make it slower", "decrease speed"),
        [
            (r"(setInterval\([^,]+,\s*)(\d+)(\s*\))",
             lambda m: m.group(1) + str(min(200, int(m.group(2)) + 30)) + m.group(3),
             {"count": 1}),
            (r"((?:speed|velocity|vel|spd)\s*=\s*)(\d+(?:\.\d+)?)",
             lambda m: m.group(1) + str(round(float(m.group(2)) * 0.65, 1)),
             {}),
        ],
    ),
    (
        ("harder", "more difficult", "increase difficulty"),
        [
            (r"((?:spawnRate|spawnInterval|maxEnemies|enemyCount)\s*=\s*)(\d+)",
             lambda m: m.group(1) + str(max(1, int(m.group(2)) - int(m.group(2)) // 3)),
             {}),
        ],
    ),
    (
        ("easier", "less difficult", "decrease difficulty"),
        [
            (r"((?:spawnRate|spawnInterval|maxEnemies|enemyCount)\s*=\s*)(\d+)",
             lambda m: m.group(1) + str(int(m.group(2)) + int(m.group(2)) // 2),
             {}),
        ],
    ),
]


def _patch_game(old_code: str, query: str) -> str | None:
    q = query.lower()
    code = old_code
    changed = False

    for keywords, subs in _SPEED_PATCHES:
        if any(w in q for w in keywords):
            for pattern, repl, kwargs in subs:
                code = re.sub(pattern, repl, code, **kwargs)
            changed = True

    if "dark" in q and ("mode" in q or "theme" in q or "background" in q or "make it dark" in q):
        code = re.sub(r"(background(?:Color)?\s*[=:]\s*['\"])#(?:fff|ffffff|f0f0f0|eeeeee|e0e0e0|white)['\"]",
                      r"\g<1>#1a1a2e'", code)
        code = re.sub(r"(body\s*\{[^}]*background(?:-color)?\s*:\s*)#(?:fff|ffffff|f0f0f0|eeeeee|e0e0e0|white)",
                      r"\g<1>#1a1a2e", code)
        code = re.sub(r"(fillStyle\s*=\s*['\"])#(?:fff|ffffff|f0f0f0|eeeeee)['\"]",
                      r"\g<1>#0f3460'", code)
        changed = True

    if "light" in q and ("mode" in q or "theme" in q or "background" in q or "make it light" in q):
        code = re.sub(r"(background(?:Color)?\s*[=:]\s*['\"])#(?:1a1a2e|0f0f0f|111111|000|000000|222|333)['\"]",
                      r"\g<1>#f8f9fa'", code)
        changed = True

    if re.search(r"add\s+(?:more\s+)?lives|(?:3|4|5)\s+lives|increase\s+lives", q):
        code = re.sub(
            r"((?:lives|health|hp|maxLives)\s*=\s*)(\d+)",
            lambda m: m.group(1) + str(int(m.group(2)) + 2),
            code,
        )
        changed = True

    if "double" in q and "score" in q:
        code = re.sub(
            r"(score\s*\+=\s*)(\d+)",
            lambda m: m.group(1) + str(int(m.group(2)) * 2),
            code,
        )
        changed = True

    return code if changed else None


def apply_update(query: str, history: list[dict]) -> dict:
    old_code = extract_last_code(history)
    if old_code is None:
        from services.dynamic_builder import build_dynamic_app
        return build_dynamic_app(query)

    old_title = _extract_title_from_code(old_code)

    if _is_game_code(old_code):
        patched = _patch_game(old_code, query)
        if patched and patched != old_code:
            return {"title": f"Updated: {old_title}", "type": "game_patch", "code": patched}
        from services.game_compiler import compile_game
        combined = f"{old_title} — {query}"
        result = compile_game(combined)
        return {"title": f"Updated: {result['title']}", "type": "game_update", "code": result["code"]}

    combined_query = f"{old_title}. {query}"
    entity_key, emoji, _ = _detect_entity(combined_query.lower())
    title = _make_title(entity_key, combined_query.lower())
    new_code = generate_crud_app(combined_query)

    return {"title": f"Updated: {title}", "type": "dynamic_crud_update", "code": new_code}
