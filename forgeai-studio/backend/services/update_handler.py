import re

_UPDATE_SIGNALS = [
    r"\badd\b.{0,50}\bto it\b",
    r"\badd\b.{0,50}\bto (the\s+)?(game|app|project|it)\b",
    r"\bnow also\b",
    r"\balso add\b",
    r"\bmake it also\b",
    r"\bchange the\b",
    r"\bupdate (it|the app|the tracker|the tool|the game|the project)\b",
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
    r"\bmake it (dark|light|bigger|smaller|responsive|mobile|faster|slower|harder|easier|colorful|animated)\b",
    r"\badd (more|extra|a|an)\b",
    r"\bcan you (make|change|add|fix|improve|update)\b",
    r"\bnow (make|add|change|fix|update)\b",
    r"\bcan u add\b",
    r"\bpls add\b",
    r"\badd more\b",
    r"\bmake the\b.{0,30}\b(faster|slower|bigger|smaller|harder|easier|better|smoother|nicer)\b",
    r"\bturn it (dark|light)\b",
    r"\bswitch to (dark|light) mode\b",
    r"\bi want (more|less)\b",
    r"\bgive it\b",
    r"\bgive me more\b",
    r"\bnow make\b",
    r"\blet me\b.{0,20}\badd\b",
    r"\bthrow in\b",
    r"\bput in\b",
    r"\binclude a\b",
    r"\balso make\b",
    r"\badd (a\s+)?(leaderboard|scoreboard|score|timer|countdown|lives|health|levels?|sound|music|animation|button|menu|dark mode|settings?|pause|restart|highscore|high score|power.?up|powerup|enemy|enemies|boss|checkpoint|save|load)\b",
    r"\b(make|turn|add)\b.{0,20}\b(dark mode|night mode|light mode)\b",
    r"\b(increase|decrease|boost|reduce)\b.{0,20}\b(speed|size|difficulty|score|damage)\b",
    r"\badd\s+\w+(\s+\w+)?\s+(feature|functionality|support|mode|system|mechanic)\b",
    r"\b(style|redesign|restyle|reskin|theme)\b.{0,20}\b(it|the game|the app)\b",
    r"\bmore (levels?|enemies|obstacles|power.?ups|features?|options?)\b",
    r"\bmake (it|the game|the app) (look|feel|play|run)\b",
]


def is_update_request(query: str, history: list[dict]) -> bool:
    q = query.lower()
    has_signal = any(re.search(p, q) for p in _UPDATE_SIGNALS)
    if not has_signal:
        return False
    return extract_last_code(history) is not None or extract_last_project(history) is not None


def extract_last_project(history: list[dict]) -> dict | None:
    """Return the most recent assistant message that has project_files."""
    for msg in reversed(history):
        if msg.get("role") != "assistant":
            continue
        files = msg.get("project_files")
        if files and len(files) > 0:
            return {"files": files, "text": msg.get("text", msg.get("content", ""))}
    return None


def _find_original_build_query(history: list[dict]) -> str | None:
    """Find the user message that triggered the most recent code project."""
    # Scan backwards: find the last assistant msg with project_files, then the user msg before it
    found_project = False
    for msg in reversed(history):
        if not found_project:
            if msg.get("role") == "assistant" and msg.get("project_files"):
                found_project = True
        else:
            if msg.get("role") == "user":
                return msg.get("text") or msg.get("content") or None
    return None


def extract_last_code(history: list[dict]) -> str | None:
    # First: check project_files in history
    project = extract_last_project(history)
    if project:
        for f in project["files"]:
            if f.get("language") == "html" or f.get("name", "").endswith(".html"):
                return f.get("content", "")
    # Fallback: look for ```html blocks in text
    for msg in reversed(history):
        if msg.get("role") != "assistant":
            continue
        text = msg.get("content") or msg.get("text", "")
        m = re.search(r"```html\n([\s\S]*?)```", text)
        if m:
            return m.group(1).strip()
    return None


def apply_update(query: str, history: list[dict]) -> dict:
    """Rebuild the project with the modification applied."""
    from services.code_generator import generate_project

    original_query = _find_original_build_query(history) or ""
    project = extract_last_project(history)

    if project or original_query:
        # Rebuild entire project combining original intent + modification
        if original_query:
            combined = f"{original_query}. Additionally: {query}"
        else:
            combined = query
        result = generate_project(combined)
        return {
            "title": result.title,
            "kind": result.kind,
            "files": [{"name": f.name, "content": f.content, "language": f.language} for f in result.files],
        }

    # Legacy fallback: try to patch inline HTML
    from services.dynamic_builder import generate_crud_app, _detect_entity, _detect_features, _make_title
    entity, emoji, fields = _detect_entity(query)
    features = _detect_features(query)
    title = _make_title(entity, emoji)
    new_code = generate_crud_app(entity, emoji, fields, features, title)
    return {"title": title, "kind": "app", "files": [{"name": "index.html", "content": new_code, "language": "html"}]}
