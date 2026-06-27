"""Unified domain response engine — topics loaded from shared/database.ts via database_seed."""

from __future__ import annotations

from data.domain_base import DOMAIN_DEFAULTS, DOMAIN_TOPICS
from services.math_engine import generate_math_response


def _wrap(thinking: str, heading: str, body: str, mode: str) -> str:
    if mode == "forge_instant":
        return f"### {heading}\n\n{body.split(chr(10) + chr(10))[0]}"
    return f"### {heading}\n{body}"


def _matches(q: str, match: dict) -> bool:
    all_kw = match.get("all") or []
    any_kw = match.get("any") or []
    if not all_kw and not any_kw:
        return False
    if all_kw and not all(k in q for k in all_kw):
        return False
    if any_kw and not any(k in q for k in any_kw):
        return False
    return True


def _topics_for_domain(domain: str) -> list[dict]:
    return sorted(
        (t for t in DOMAIN_TOPICS if t.get("domain") == domain),
        key=lambda t: t.get("priority", 999),
    )


def _render(topic: dict, query: str, mode: str) -> str:
    body = topic["body"].replace("{query}", query)
    return _wrap(topic["thinking"], topic["heading"], body, mode)


def _generate_domain_response(query: str, mode: str, domain: str) -> str:
    q = query.lower().strip()
    for topic in _topics_for_domain(domain):
        if _matches(q, topic.get("match") or {}):
            return _render(topic, query, mode)
    default = DOMAIN_DEFAULTS[domain]
    return _render(default, query, mode)


def generate_space_response(query: str, mode: str) -> str:
    return _generate_domain_response(query, mode, "space")


def generate_earth_response(query: str, mode: str) -> str:
    return _generate_domain_response(query, mode, "earth")


def generate_science_response(query: str, mode: str) -> str:
    return _generate_domain_response(query, mode, "science")


def generate_history_response(query: str, mode: str) -> str:
    return _generate_domain_response(query, mode, "history")


__all__ = [
    "generate_math_response",
    "generate_space_response",
    "generate_earth_response",
    "generate_science_response",
    "generate_history_response",
]
