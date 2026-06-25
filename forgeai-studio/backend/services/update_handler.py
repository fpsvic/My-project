import re
from services.dynamic_builder import generate_crud_app, _detect_entity, _detect_features, _make_title


_UPDATE_SIGNALS = [
    r"\badd\b.{0,40}\bto it\b",
    r"\bnow also\b",
    r"\balso add\b",
    r"\bmake it also\b",
    r"\bchange the\b",
    r"\bupdate (it|the app|the tracker|the tool)\b",
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
    r"\bmake it (dark|light|bigger|smaller|responsive|mobile)\b",
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
        text = msg.get("content", "")
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


def apply_update(query: str, history: list[dict]) -> dict:
    old_code = extract_last_code(history)
    if old_code is None:
        from services.dynamic_builder import build_dynamic_app
        return build_dynamic_app(query)

    old_title = _extract_title_from_code(old_code)

    combined_query = f"{old_title}. {query}"

    q = query.lower()
    entity_key, emoji, _ = _detect_entity(combined_query.lower())
    title = _make_title(entity_key, combined_query.lower())

    new_code = generate_crud_app(combined_query)

    return {
        "title": f"Updated: {title}",
        "type": "dynamic_crud_update",
        "code": new_code,
    }
