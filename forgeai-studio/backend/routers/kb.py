"""
/kb — Knowledge Base admin endpoints

GET  /kb/stats          — entry count by category
GET  /kb/search?q=...   — search entries
POST /kb/add            — add / update a knowledge entry
POST /kb/add_lang       — add a language history entry
POST /kb/add_example    — add a code example
DELETE /kb/{key}        — remove a knowledge entry
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from data.database import (
    knowledge_count,
    search_knowledge,
    add_knowledge,
    delete_knowledge,
    add_lang_history,
    add_code_example,
    load_knowledge,
)
from data.database import _connect

router = APIRouter(prefix="/kb", tags=["knowledge-base"])


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats")
def stats():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT category, COUNT(*) as count FROM knowledge GROUP BY category"
        ).fetchall()
    return {
        "total": knowledge_count(),
        "by_category": {r["category"]: r["count"] for r in rows},
    }


# ── Search ────────────────────────────────────────────────────────────────────

@router.get("/search")
def search(q: str, limit: int = 20):
    if not q or len(q) < 2:
        raise HTTPException(400, "Query must be at least 2 characters")
    return {"results": search_knowledge(q, limit=limit)}


# ── Add knowledge ─────────────────────────────────────────────────────────────

class KnowledgeEntry(BaseModel):
    key: str
    answer: str
    category: str = "general"


@router.post("/add")
def add_entry(entry: KnowledgeEntry):
    if not entry.key.strip() or not entry.answer.strip():
        raise HTTPException(400, "key and answer are required")
    add_knowledge(entry.key.strip().lower(), entry.answer.strip(), entry.category)
    return {"ok": True, "key": entry.key.strip().lower()}


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{key:path}")
def delete_entry(key: str):
    delete_knowledge(key)
    return {"ok": True, "deleted": key}


# ── Add language history ──────────────────────────────────────────────────────

class LangEntry(BaseModel):
    language: str
    history: str
    hello_world: str = ""


@router.post("/add_lang")
def add_lang(entry: LangEntry):
    if not entry.language.strip() or not entry.history.strip():
        raise HTTPException(400, "language and history are required")
    add_lang_history(entry.language.strip().lower(), entry.history.strip(), entry.hello_world.strip())
    return {"ok": True, "language": entry.language.strip().lower()}


# ── Add code example ─────────────────────────────────────────────────────────

class CodeExample(BaseModel):
    language: str
    concept: str
    code: str


@router.post("/add_example")
def add_example(entry: CodeExample):
    if not entry.language.strip() or not entry.concept.strip() or not entry.code.strip():
        raise HTTPException(400, "language, concept, and code are required")
    add_code_example(entry.language.strip().lower(), entry.concept.strip().lower(), entry.code.strip())
    return {"ok": True, "language": entry.language, "concept": entry.concept}
