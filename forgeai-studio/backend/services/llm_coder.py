"""
llm_coder.py — Real LLM-powered code generation for ForgeAI Studio.

Gives ForgeAI "Replit-level" coding power: describe anything, get a working
multi-file web project back. Uses the Claude API (Anthropic Messages API) when
an ANTHROPIC_API_KEY is available, and cleanly reports unavailable otherwise so
callers can fall back to the offline template engine.

Public API:
    llm_available() -> bool
    llm_generate(query: str) -> ProjectResult | None
    llm_update(query: str, files: list[dict]) -> ProjectResult | None
"""

from __future__ import annotations

import json
import os

# Model + limits
_MODEL = os.environ.get("FORGEAI_LLM_MODEL", "claude-opus-4-8")
_MAX_TOKENS = 32000

# Lazy singletons
_client = None
_import_failed = False


def _get_client():
    """Return a cached Anthropic client, or None if unavailable."""
    global _client, _import_failed
    if _client is not None:
        return _client
    if _import_failed:
        return None
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # noqa: WPS433 (lazy import is intentional)
        _client = anthropic.Anthropic()
        return _client
    except Exception:
        _import_failed = True
        return None


def llm_available() -> bool:
    """True when a real LLM backend can be used."""
    return _get_client() is not None


# ─── Prompts ──────────────────────────────────────────────────────────────────

_SYSTEM = (
    "You are ForgeAI's code engine — an expert full-stack web developer. "
    "You build complete, working, self-contained web projects from a natural-"
    "language description. Rules:\n"
    "- Output a small set of files: index.html, style.css, and app.js (use "
    "game.js instead of app.js for games). Add more files only if truly needed.\n"
    "- index.html must link ./style.css and ./<script>.js with relative paths.\n"
    "- Everything must run by opening index.html directly — no build step, no "
    "server, no external network calls. You may use CDN <script> tags only when "
    "essential.\n"
    "- Write real, functional logic that does exactly what the user described. "
    "No placeholders, no 'TODO', no stubbed handlers.\n"
    "- Make it visually polished and responsive.\n"
    "Return ONLY the structured JSON described by the schema — no prose."
)

_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "kind": {"type": "string", "enum": ["game", "app"]},
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                    "language": {
                        "type": "string",
                        "enum": ["html", "css", "javascript"],
                    },
                },
                "required": ["name", "content", "language"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["title", "kind", "files"],
    "additionalProperties": False,
}


def _call(user_msg: str) -> dict | None:
    """Run one structured generation request. Returns the parsed dict or None."""
    client = _get_client()
    if client is None:
        return None
    try:
        with client.messages.stream(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=_SYSTEM,
            output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
            messages=[{"role": "user", "content": user_msg}],
        ) as stream:
            message = stream.get_final_message()
    except Exception:
        return None

    if getattr(message, "stop_reason", None) == "refusal":
        return None

    text = next((b.text for b in message.content if b.type == "text"), "")
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict) or not data.get("files"):
        return None
    return data


# ─── Result mapping ───────────────────────────────────────────────────────────

def _to_result(data: dict):
    """Convert a validated dict into a ProjectResult."""
    from services.code_generator import ProjectFile, ProjectResult

    _lang_map = {"javascript": "js", "js": "js", "html": "html", "css": "css"}
    files = []
    for f in data.get("files", []):
        name = str(f.get("name", "")).strip()
        content = f.get("content", "")
        if not name or not content:
            continue
        lang = _lang_map.get(str(f.get("language", "")).lower())
        if not lang:
            lang = name.rsplit(".", 1)[-1].lower() if "." in name else "html"
        files.append(ProjectFile(name=name, content=content, language=lang))
    if not files:
        return None

    kind = data.get("kind") if data.get("kind") in ("game", "app") else "app"
    title = str(data.get("title") or "Your Project").strip()
    return ProjectResult(title=title, kind=kind, files=files)


# ─── Public entry points ──────────────────────────────────────────────────────

def llm_generate(query: str):
    """Generate a fresh project from a description. Returns ProjectResult|None."""
    data = _call(f"Build this: {query}")
    if data is None:
        return None
    return _to_result(data)


def llm_update(query: str, files: list[dict]):
    """Modify an existing project. `files` is a list of {name,content,language}."""
    existing = "\n\n".join(
        f"=== {f.get('name')} ===\n{f.get('content', '')}" for f in files
    )
    prompt = (
        "Here is the current project:\n\n"
        f"{existing}\n\n"
        f"Apply this change and return the COMPLETE updated project: {query}"
    )
    data = _call(prompt)
    if data is None:
        return None
    return _to_result(data)
