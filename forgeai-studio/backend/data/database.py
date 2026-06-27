"""
database.py — ForgeAI SQLite knowledge store

SQLite knowledge store backed by shared/knowledgebase.ts (via knowledgebase.json).

Schema
------
  knowledge       — main KB (key → answer, with category tag)
  lang_history    — programming language histories
  code_examples   — per-language code snippets
  lang_hello_world — hello-world examples per language

All tables are created automatically on first import.
Data is seeded from shared/knowledgebase.json once on startup if the DB is empty.

Public API
----------
  load_knowledge()           -> dict[str, str]   (cached in memory)
  get_answer(key)            -> str | None
  add_knowledge(key, answer, category)
  search_knowledge(query)    -> list[dict]        (FTS or LIKE fallback)
  load_lang_history()        -> dict[str, str]
  load_lang_hello_world()    -> dict[str, str]
  load_code_examples()       -> dict[str, dict[str, str]]
  add_lang_history(lang, history, hello_world)
  add_code_example(lang, concept, code)
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "forgeai.db"

# ── In-memory caches (populated once on first access) ──────────────────────────
_knowledge_cache: dict[str, str] | None = None
_lang_history_cache: dict[str, str] | None = None
_lang_hello_world_cache: dict[str, str] | None = None
_code_examples_cache: dict[str, dict[str, str]] | None = None


# ── Connection helper ──────────────────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrent read perf
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


# ── Schema init ───────────────────────────────────────────────────────────────

def _init_schema() -> None:
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                key        TEXT    UNIQUE NOT NULL COLLATE NOCASE,
                answer     TEXT    NOT NULL,
                category   TEXT    NOT NULL DEFAULT 'general',
                updated_at TEXT    DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_knowledge_category
                ON knowledge(category);

            CREATE TABLE IF NOT EXISTS lang_history (
                language    TEXT PRIMARY KEY COLLATE NOCASE,
                history     TEXT NOT NULL DEFAULT '',
                hello_world TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS code_examples (
                language TEXT NOT NULL COLLATE NOCASE,
                concept  TEXT NOT NULL COLLATE NOCASE,
                code     TEXT NOT NULL,
                PRIMARY KEY (language, concept)
            );
        """)


# ── Seed from knowledgebase.json (runs once if tables are empty) ──────────────

def _seed_if_empty() -> None:
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
        if count > 0:
            return   # already seeded

    try:
        from data.knowledge_base import (
            GENERAL_KNOWLEDGE,
            LANG_HISTORY,
            LANG_HELLO_WORLD,
            CODING_HELP,
        )
        try:
            from data.knowledge_base import LANG_EXAMPLES
        except ImportError:
            LANG_EXAMPLES: dict = {}
    except ImportError:
        return

    with _connect() as conn:
        # Main KB
        conn.executemany(
            "INSERT OR IGNORE INTO knowledge (key, answer, category) VALUES (?, ?, 'general')",
            list(GENERAL_KNOWLEDGE.items()),
        )
        # Coding help entries
        conn.executemany(
            "INSERT OR IGNORE INTO knowledge (key, answer, category) VALUES (?, ?, 'coding')",
            list(CODING_HELP.items()),
        )
        # Language histories + hello worlds
        for lang in set(list(LANG_HISTORY.keys()) + list(LANG_HELLO_WORLD.keys())):
            conn.execute(
                """INSERT OR IGNORE INTO lang_history (language, history, hello_world)
                   VALUES (?, ?, ?)""",
                (lang, LANG_HISTORY.get(lang, ""), LANG_HELLO_WORLD.get(lang, "")),
            )
        # Code examples
        for lang, examples in LANG_EXAMPLES.items():
            for concept, code in examples.items():
                conn.execute(
                    "INSERT OR IGNORE INTO code_examples (language, concept, code) VALUES (?, ?, ?)",
                    (lang, concept, code),
                )


# ── Bootstrap (called at module load) ─────────────────────────────────────────

_init_schema()
_seed_if_empty()


# ── Public API — Knowledge ─────────────────────────────────────────────────────

def load_knowledge(categories: list[str] | None = None) -> dict[str, str]:
    """
    Return the full knowledge dict {key: answer}, cached in memory.
    Optional `categories` filters to specific categories.
    """
    global _knowledge_cache
    if _knowledge_cache is not None and categories is None:
        return _knowledge_cache

    with _connect() as conn:
        if categories:
            placeholders = ",".join("?" * len(categories))
            rows = conn.execute(
                f"SELECT key, answer FROM knowledge WHERE category IN ({placeholders})",
                categories,
            ).fetchall()
        else:
            rows = conn.execute("SELECT key, answer FROM knowledge").fetchall()

    result = {row["key"]: row["answer"] for row in rows}
    if categories is None:
        _knowledge_cache = result
    return result


def get_answer(key: str) -> str | None:
    """Direct key lookup (uses cache if available)."""
    cache = load_knowledge()
    return cache.get(key)


def add_knowledge(key: str, answer: str, category: str = "general") -> None:
    """Insert or replace a knowledge entry and update the in-memory cache."""
    global _knowledge_cache
    with _connect() as conn:
        conn.execute(
            """INSERT INTO knowledge (key, answer, category)
               VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET
                   answer=excluded.answer,
                   category=excluded.category,
                   updated_at=datetime('now')""",
            (key, answer, category),
        )
    if _knowledge_cache is not None:
        _knowledge_cache[key] = answer


def delete_knowledge(key: str) -> None:
    """Remove a knowledge entry."""
    global _knowledge_cache
    with _connect() as conn:
        conn.execute("DELETE FROM knowledge WHERE key = ?", (key,))
    if _knowledge_cache is not None:
        _knowledge_cache.pop(key, None)


def search_knowledge(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Full-text LIKE search across keys and answers.
    Returns list of {key, answer, category} dicts, ordered by key-match first.
    """
    term = f"%{query}%"
    with _connect() as conn:
        rows = conn.execute(
            """SELECT key, answer, category,
                      (CASE WHEN key LIKE ? THEN 1 ELSE 0 END) AS key_match
               FROM knowledge
               WHERE key LIKE ? OR answer LIKE ?
               ORDER BY key_match DESC
               LIMIT ?""",
            (term, term, term, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def knowledge_count() -> int:
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]


# ── Public API — Language data ─────────────────────────────────────────────────

def load_lang_history() -> dict[str, str]:
    global _lang_history_cache
    if _lang_history_cache is not None:
        return _lang_history_cache
    with _connect() as conn:
        rows = conn.execute("SELECT language, history FROM lang_history").fetchall()
    _lang_history_cache = {r["language"]: r["history"] for r in rows}
    return _lang_history_cache


def load_lang_hello_world() -> dict[str, str]:
    global _lang_hello_world_cache
    if _lang_hello_world_cache is not None:
        return _lang_hello_world_cache
    with _connect() as conn:
        rows = conn.execute(
            "SELECT language, hello_world FROM lang_history WHERE hello_world != ''"
        ).fetchall()
    _lang_hello_world_cache = {r["language"]: r["hello_world"] for r in rows}
    return _lang_hello_world_cache


def load_code_examples() -> dict[str, dict[str, str]]:
    global _code_examples_cache
    if _code_examples_cache is not None:
        return _code_examples_cache
    with _connect() as conn:
        rows = conn.execute(
            "SELECT language, concept, code FROM code_examples"
        ).fetchall()
    result: dict[str, dict[str, str]] = {}
    for r in rows:
        result.setdefault(r["language"], {})[r["concept"]] = r["code"]
    _code_examples_cache = result
    return result


def add_lang_history(language: str, history: str, hello_world: str = "") -> None:
    global _lang_history_cache, _lang_hello_world_cache
    with _connect() as conn:
        conn.execute(
            """INSERT INTO lang_history (language, history, hello_world)
               VALUES (?, ?, ?)
               ON CONFLICT(language) DO UPDATE SET
                   history=excluded.history,
                   hello_world=excluded.hello_world""",
            (language, history, hello_world),
        )
    _lang_history_cache = None
    _lang_hello_world_cache = None


def add_code_example(language: str, concept: str, code: str) -> None:
    global _code_examples_cache
    with _connect() as conn:
        conn.execute(
            """INSERT INTO code_examples (language, concept, code)
               VALUES (?, ?, ?)
               ON CONFLICT(language, concept) DO UPDATE SET code=excluded.code""",
            (language, concept, code),
        )
    if _code_examples_cache is not None and language in _code_examples_cache:
        _code_examples_cache[language][concept] = code


# ── Cache invalidation (useful after bulk imports) ────────────────────────────

def invalidate_cache() -> None:
    global _knowledge_cache, _lang_history_cache, _lang_hello_world_cache, _code_examples_cache
    _knowledge_cache = None
    _lang_history_cache = None
    _lang_hello_world_cache = None
    _code_examples_cache = None
