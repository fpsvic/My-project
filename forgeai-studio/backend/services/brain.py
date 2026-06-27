"""
ForgeAI Brain — intent routing, NLG, structural variation, and response generation.

Consolidates comprehension, intent scoring, message generation, and dispatch.
Public API: generate_response(), forge(), forge_greeting(), vary_structure(), generate_from_content()
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Callable

from data.knowledge_base import (
    SPACE_KEYWORDS,
    EARTH_KEYWORDS,
    ADVANCED_SCIENCE_KEYWORDS,
    POLITICAL_KEYWORDS,
)
from data.database import load_knowledge as _load_knowledge
from services.math_engine import generate_math_response
from services.space_engine import generate_space_response
from services.earth_engine import generate_earth_response
from services.science_engine import generate_science_response
from services.history_engine import generate_history_response
from services.code_generater import (
    generate_anything,
    generate_anything_with_meta,
    generate_project,
    compile_game,
    build_app,
    detect_app_type,
    build_dynamic_app,
    web_lookup,
    _last_searched,
    dispatch_programming,
    score_programming,
)
from services.update_handler import is_update_request, apply_update

# Load DB-backed dicts (cached in memory after first access)
GENERAL_KNOWLEDGE = _load_knowledge()


# =============================================================================
# NLG ENGINE — natural language generation from structured facts
# =============================================================================

@dataclass
class FactAtom:
    type: str                          # speed | size | date | count | inventor |
                                       # composition | temperature | distance | definition
    subject: str = ""
    value: str = ""
    unit: str = ""
    equivalents: list[str] = field(default_factory=list)
    condition: str = ""                # "in air at 20°C", "at sea level", etc.
    raw: str = ""                      # original sentence fragment
    extra: dict = field(default_factory=dict)   # type-specific overflow


# ── Extraction helpers ────────────────────────────────────────────────────────

def _clean(s: str) -> str:
    return re.sub(r"[*_`#>]", "", s).strip()


def _extract_equivalents(text: str) -> list[str]:
    equivs: list[str] = []
    paren = re.findall(r"\(([^)]+)\)", text)
    for group in paren:
        if re.match(r"^\s*(?:at|in|under|per)\s", group, re.IGNORECASE) and not re.search(r"\bor\b|/", group):
            continue
        parts = re.split(r"\bor\b", group)
        for p in parts:
            p = p.strip(" ,;/")
            if p and re.search(r"\d", p) and re.search(r"[a-zA-Z]", p):
                equivs.append(_clean(p))
    return equivs


def _extract_condition(text: str) -> str:
    patterns = [
        r"\bin [\w ]+?(?:\s+at [\d°C .]+)?(?=\s+(?:is|are|was|were)\b|[,;]|$)",
        r"\bat (?:room|sea|standard|body|normal|atmospheric)\s+[\w ]+",
        r"\bat \d+\s*°[CF]",
        r"\bunder [\w ]+?(?=\s+(?:is|are)\b|[,;]|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            cond = m.group(0).strip().rstrip(",;.")
            if 3 < len(cond) < 60:
                return cond
    return ""


def _primary_value(text: str) -> tuple[str, str]:
    m = re.search(r"\*\*([\d,. ]+)\*\*\s*([a-zA-Z/°²³%]+)", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m = re.search(r"\*\*([\d,. ]+)([a-zA-Z/°²³%]+)\*\*", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    m = re.search(
        r"([\d,]+(?:\.\d+)?)\s+(billion|million|trillion)\s+(km|miles?|ly|AU|pc)",
        text, re.IGNORECASE,
    )
    if m:
        return f"{m.group(1)} {m.group(2)}", m.group(3)

    m = re.search(
        r"(?<!\d°)\b([\d,]+(?:\.\d+)?)\s?"
        r"(km/h|mph|m/s|km/s|c\b|ly\b|AU\b|pc\b|"
        r"km\b|mi\b|miles?\b|kg\b|lbs?\b|"
        r"Hz\b|kHz\b|MHz\b|GHz\b|W\b|kW\b|MW\b|J\b|kJ\b|Pa\b|kPa\b|"
        r"years?\b|days?\b|hours?\b|minutes?\b|seconds?\b|"
        r"%|billion\b|million\b|trillion\b|thousand\b|hundred\b)",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1), m.group(2)

    m = re.search(r"([\d,]+(?:\.\d+)?)\s?(°[CF]|K\b|kelvin)", text, re.IGNORECASE)
    if m:
        return m.group(1), m.group(2)

    m = re.search(r"\b([\d,]+(?:\.\d+)?)\b", text)
    if m:
        return m.group(1), ""
    return "", ""


_SPEED_SIGNALS = re.compile(
    r"\b(speed|velocity|travels?|moves?|propagates?|km/h|mph|m/s|knot|mach)\b",
    re.IGNORECASE,
)
_SIZE_SIGNALS = re.compile(
    r"\b(diameter|radius|mass|weight|height|width|length|size|large|big|"
    r"small|km\b|miles?\b|light.year|parsec|AU\b|kg\b|tonne|ton\b)\b",
    re.IGNORECASE,
)
_DATE_SIGNALS = re.compile(
    r"\b(founded|invented|created|discovered|born|established|released|"
    r"designed|built|in \d{4}|\d{4}\b|century|decade|year)\b",
    re.IGNORECASE,
)
_COUNT_SIGNALS = re.compile(
    r"\b(how many|number of|count|\d+ (moons?|planets?|bones?|species|atoms?|"
    r"electrons?|chromosomes?|teeth|hearts?|legs?|eyes?))\b",
    re.IGNORECASE,
)
_INVENTOR_SIGNALS = re.compile(
    r"\b(invented by|created by|designed by|discovered by|developed by|"
    r"founded by|built by|who (made|invented|created|designed|built|discovered))\b",
    re.IGNORECASE,
)
_COMPOSITION_SIGNALS = re.compile(
    r"\b(made of|consists? of|composed of|contains?|element|chemical|"
    r"formula|structure|compound|atom|molecule|ingredient)\b",
    re.IGNORECASE,
)
_TEMPERATURE_SIGNALS = re.compile(
    r"\b(temperature|°[CF]|kelvin|boiling|melting|freezing|degrees?|hot|cold|heat)\b",
    re.IGNORECASE,
)
_DISTANCE_SIGNALS = re.compile(
    r"\b(distance|far|away|light.year|parsec|AU\b|km from|miles? from|"
    r"million km|billion km|trillion km|from Earth|from the Sun|from us)\b",
    re.IGNORECASE,
)
_DEFINITION_SIGNALS = re.compile(
    r"\b(is a|is an|are|refers? to|defined as|means?|describes?|known as|called)\b",
    re.IGNORECASE,
)


_INVENTOR_VERB_RE = re.compile(
    r"\b(?:invented|created|designed|discovered|developed|built|founded|conceived|written|authored)\s+(?:in\s+\d{4}\s+)?by\s+[A-Z]",
)

def _classify_type(text: str) -> str:
    scores = {
        "speed": len(_SPEED_SIGNALS.findall(text)),
        "size": len(_SIZE_SIGNALS.findall(text)),
        "date": len(_DATE_SIGNALS.findall(text)),
        "count": len(_COUNT_SIGNALS.findall(text)),
        "inventor": len(_INVENTOR_SIGNALS.findall(text)),
        "composition": len(_COMPOSITION_SIGNALS.findall(text)),
        "temperature": len(_TEMPERATURE_SIGNALS.findall(text)),
        "distance": len(_DISTANCE_SIGNALS.findall(text)),
        "definition": len(_DEFINITION_SIGNALS.findall(text)),
    }
    if _INVENTOR_VERB_RE.search(text):
        scores["inventor"] += 3
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "definition"


def _extract_subject(text: str, fact_type: str) -> str:
    m = re.search(r"\b(?:speed|distance|temperature|mass|diameter|age|"
                  r"height|weight|size|count|number)\s+of\s+([\w\s]+?)(?:\s+(?:is|was|in|at|=))",
                  text, re.IGNORECASE)
    if m:
        return m.group(1).strip().lower()
    m = re.search(r"^The\s+([\w\s\-]+?)\s+(?:is|was|are|were|has|have)\b", text, re.IGNORECASE)
    if m:
        cand = m.group(1).strip()
        if len(cand.split()) <= 4:
            return cand.lower()
    m = re.search(r"^([A-Z][A-Za-z0-9 \-]+?)\s+(?:was|is|were|are)\b", text)
    if m:
        cand = m.group(1).strip()
        if not cand.lower().startswith("the ") and len(cand.split()) <= 5:
            return cand
    return ""


def extract_fact_atoms(content: str) -> list[FactAtom]:
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+|(?<=\))\s*—\s*", content)
    atoms: list[FactAtom] = []

    for raw in raw_sentences:
        raw = raw.strip()
        if not raw or len(raw) < 10:
            continue
        if re.match(r"^#{1,4}\s", raw):
            continue
        clean = _clean(raw)
        if not clean or len(clean) < 8:
            continue

        ftype = _classify_type(clean)
        subject = _extract_subject(clean, ftype)
        value, unit = _primary_value(clean)
        equivalents = _extract_equivalents(clean)
        condition = _extract_condition(clean)

        extra: dict = {}
        m = re.search(
            r"(?:invented|created|designed|discovered|developed|built|founded|conceived|written|authored)"
            r"\s+(?:in\s+\d{4}\s+)?by\s+([\w\s\.\-]+?)(?:\s+(?:in|at|for|\d{4})|[,.]|$)",
            clean, re.IGNORECASE,
        )
        if m:
            extra["inventor"] = m.group(1).strip()
        m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", clean)
        if m:
            extra["year"] = m.group(1)

        atoms.append(FactAtom(
            type=ftype,
            subject=subject,
            value=value,
            unit=unit,
            equivalents=equivalents,
            condition=condition,
            raw=clean,
            extra=extra,
        ))

    return atoms if atoms else [FactAtom(type="definition", raw=_clean(content), subject="")]


# ── Sentence generators per fact type ────────────────────────────────────────

SentenceGen = Callable[[FactAtom], str]

def _val(a: FactAtom) -> str:
    if a.value and a.unit:
        return f"{a.value} {a.unit}"
    if a.value:
        return a.value
    return a.raw[:60]

def _eq(a: FactAtom, idx: int = 0) -> str:
    return a.equivalents[idx] if len(a.equivalents) > idx else ""

def _subj(a: FactAtom, fallback: str = "it") -> str:
    return a.subject if a.subject else fallback

def _cond_phrase(a: FactAtom) -> str:
    if not a.condition:
        return ""
    return f" ({a.condition})"

def _cond_prepend(a: FactAtom) -> str:
    if a.condition:
        c = a.condition[0].upper() + a.condition[1:]
        return f"{c}, "
    return ""


# ---- SPEED generators --------------------------------------------------------

_SPEED_GENS: list[SentenceGen] = [
    lambda a: (
        f"{_subj(a, 'it').capitalize()} moves at {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"{_cond_prepend(a)}{_subj(a, 'it').capitalize()} travels at {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"{_val(a)} — that's how fast {_subj(a, 'it')} moves{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"In a single second, {_subj(a, 'it')} covers {a.value} {a.unit}{_cond_phrase(a)}."
        if a.value and a.unit else ""
    ),
    lambda a: (
        f"{_subj(a, 'it').capitalize()} propagates"
        f" {a.condition or 'through the medium'}"
        f" at {_val(a)}, or roughly {_eq(a)}."
        if a.value and _eq(a) else ""
    ),
    lambda a: (
        f"Speed of {_subj(a, 'it')}: {_val(a)}{_cond_phrase(a)}"
        + (f", equivalent to {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"To put it in perspective: {_subj(a, 'it')} clocks in at {_val(a)}"
        + (f" — about {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"The speed at which {_subj(a, 'it')} travels{_cond_phrase(a)} is {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"Here's a figure worth pausing on: {_subj(a, 'it')} reaches {_val(a)}{_cond_phrase(a)}"
        + (f", or {_eq(a)} in more familiar units" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"Could you even perceive {_subj(a, 'it')} at {_val(a)}? At that pace{_cond_phrase(a)}, it's effectively invisible to the naked eye."
        if a.value else ""
    ),
]


# ---- SIZE generators ---------------------------------------------------------

_SIZE_GENS: list[SentenceGen] = [
    lambda a: (
        f"{_subj(a, 'it').capitalize()} measures {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"At {_val(a)}, {_subj(a, 'it')} is{_cond_phrase(a)} one of the most"
        f" {random.choice(['remarkable','striking','notable','impressive'])} in its class."
        if a.value else ""
    ),
    lambda a: (
        f"In terms of size, {_subj(a, 'it')} comes in at {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"{_val(a)} — that's the {random.choice(['scale','magnitude','measure'])} of {_subj(a, 'it')}."
        if a.value else ""
    ),
    lambda a: (
        f"The {random.choice(['dimensions','scale','size'])} of {_subj(a, 'it')}: {_val(a)}"
        + (f", roughly {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"{_subj(a, 'it').capitalize()} spans {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"Measured {a.condition or 'across'}, {_subj(a, 'it')} reaches {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"What does {_val(a)} actually look like? That's the full extent of {_subj(a, 'it')}"
        + (f" — comparable to {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"Don't let the number fool you: {_val(a)} is the true scale of {_subj(a, 'it')}{_cond_phrase(a)}, and intuition tends to underestimate it."
        if a.value else ""
    ),
    lambda a: (
        f"To place {_subj(a, 'it')} in context, it clocks {_val(a)}{_cond_phrase(a)}"
        + (f", or about {_eq(a)} in everyday terms" if _eq(a) else "") + "."
        if a.value else ""
    ),
]


# ---- DATE generators ---------------------------------------------------------

_DATE_GENS: list[SentenceGen] = [
    lambda a: (
        f"{_subj(a, 'it').capitalize()} dates back to {a.extra.get('year', a.value or 'an uncertain period')}."
    ),
    lambda a: (
        f"The year {a.extra.get('year', a.value or '?')} marks when {_subj(a, 'it')} came into existence."
        if a.extra.get('year') or a.value else ""
    ),
    lambda a: (
        f"It was in {a.extra.get('year', a.value or 'that era')} that {_subj(a, 'it')} {random.choice(['emerged','first appeared','was established','took shape'])}."
    ),
    lambda a: (
        f"{_subj(a, 'it').capitalize()} {random.choice(['traces its origins to','has its roots in','was first documented around'])} {a.extra.get('year', a.value or 'the historical record')}."
    ),
    lambda a: (
        f"As far back as {a.extra.get('year', a.value or 'history records')}, {_subj(a, 'it')} was already {random.choice(['known','documented','in use','being developed'])}."
        if a.extra.get('year') or a.value else ""
    ),
    lambda a: (
        f"Pinning down the timeline: {_subj(a, 'it')} {random.choice(['appeared','was born','arrived on the scene'])} in {a.extra.get('year', a.value or 'that period')}."
        if a.extra.get('year') or a.value else ""
    ),
    lambda a: (
        f"Why {a.extra.get('year', a.value or 'then')}? That's precisely when conditions aligned for {_subj(a, 'it')} to {random.choice(['emerge','take form','be realised'])}."
        if a.extra.get('year') or a.value else ""
    ),
    lambda a: (
        f"The historical record places {_subj(a, 'it')} in {a.extra.get('year', a.value or 'a pivotal era')} — a moment that shaped everything that followed."
        if a.extra.get('year') or a.value else ""
    ),
    lambda a: (
        f"{a.raw}"
        if not a.extra.get('year') and not a.value else ""
    ),
]


# ---- COUNT generators --------------------------------------------------------

_COUNT_GENS: list[SentenceGen] = [
    lambda a: a.raw,
    lambda a: (
        f"The total count: {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"{_val(a)}{_cond_phrase(a)} — that's the figure."
        if a.value else ""
    ),
    lambda a: (
        f"In terms of quantity, {a.raw[0].lower() + a.raw[1:] if a.raw else ''}"
        if a.raw else ""
    ),
    lambda a: (
        f"When you count them up, that comes to {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"The number is {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"Surprisingly, the count stands at {_val(a)}{_cond_phrase(a)} — each one distinct and functional."
        if a.value else ""
    ),
    lambda a: (
        f"How many? Exactly {_val(a)}{_cond_phrase(a)}, and that number turns out to matter more than it seems."
        if a.value else ""
    ),
    lambda a: (
        f"That tally of {_val(a)}{_cond_phrase(a)} isn't arbitrary — it reflects a precise structural requirement."
        if a.value else ""
    ),
]


# ---- INVENTOR generators -----------------------------------------------------

_INVENTOR_GENS: list[SentenceGen] = [
    lambda a: (
        f"{a.extra.get('inventor', 'an unknown inventor')} is credited with creating {_subj(a, 'it')}"
        + (f" in {a.extra.get('year')}" if a.extra.get('year') else "") + "."
    ),
    lambda a: (
        f"{_subj(a, 'it').capitalize()} was brought into the world by"
        f" {a.extra.get('inventor', 'its creator')}"
        + (f" around {a.extra.get('year')}" if a.extra.get('year') else "") + "."
    ),
    lambda a: (
        f"The mind behind {_subj(a, 'it')}? {a.extra.get('inventor', 'An ingenious inventor')}"
        + (f", working in {a.extra.get('year')}" if a.extra.get('year') else "") + "."
    ),
    lambda a: (
        f"Credit for {_subj(a, 'it')} goes to {a.extra.get('inventor', 'its original creator')}"
        + (f", back in {a.extra.get('year')}" if a.extra.get('year') else "") + "."
    ),
    lambda a: (
        f"{a.extra.get('inventor', 'Its creator')}"
        + (f", in {a.extra.get('year')}" if a.extra.get('year') else "")
        + f", gave the world {_subj(a, 'this innovation')}."
    ),
    lambda a: (
        f"Who made {_subj(a, 'it')}? {a.extra.get('inventor', 'The original inventor')} did"
        + (f", in {a.extra.get('year')}" if a.extra.get('year') else "") + "."
    ),
    lambda a: (
        f"Invented by {a.extra.get('inventor', 'an innovative mind')}"
        + (f" in {a.extra.get('year')}" if a.extra.get('year') else "")
        + f", {_subj(a, 'it')} changed how we think about this domain."
    ),
    lambda a: (
        f"Before {a.extra.get('inventor', 'this inventor')} came along"
        + (f" in {a.extra.get('year')}" if a.extra.get('year') else "")
        + f", the problem that {_subj(a, 'it')} solves had no clean answer."
    ),
    lambda a: (
        f"It took {a.extra.get('inventor', 'a specific individual')} to see what others missed"
        + (f" — and in {a.extra.get('year')}" if a.extra.get('year') else "")
        + f", {_subj(a, 'this creation')} was the result."
    ),
    lambda a: (
        f"The creation of {_subj(a, 'it')} is tied directly to {a.extra.get('inventor', 'one person')}"
        + (f"'s work in {a.extra.get('year')}" if a.extra.get('year') else "'s work") + "."
    ),
]


def _composition_body(a: FactAtom) -> str:
    if a.value:
        return f"{a.value} {a.unit}".strip()
    raw = a.raw
    if a.subject:
        raw = re.sub(
            rf"^{re.escape(a.subject)}\s+(?:is|are|was|were)\s+(?:composed of|made of|made up of|consisting of|composed from|containing)?\s*",
            "", raw, flags=re.IGNORECASE,
        ).strip()
    raw = re.sub(r"^(?:composed of|made of|made up of|consists? of|containing)\s+", "", raw, flags=re.IGNORECASE).strip()
    return raw or a.raw

# ---- COMPOSITION generators --------------------------------------------------

_COMPOSITION_GENS: list[SentenceGen] = [
    lambda a: (
        f"{_subj(a, 'it').capitalize()} is made up of {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"At its core, {_subj(a, 'it')} consists of {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"The composition of {_subj(a, 'it')}: {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"What's {_subj(a, 'it')} made of? {_composition_body(a).rstrip('.').capitalize()}."
        if a.raw else ""
    ),
    lambda a: (
        f"{_subj(a, 'it').capitalize()} is structurally composed of {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"In terms of what it's built from, {_subj(a, 'it')} contains {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"Strip {_subj(a, 'it')} down to its fundamentals and you'll find {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"What {_subj(a, 'it')} is NOT: a single uniform substance. It's built from {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
    lambda a: (
        f"Think of {_subj(a, 'it')} as a precise assembly — its ingredients are {_composition_body(a).rstrip('.')}."
        if a.raw else ""
    ),
]


# ---- TEMPERATURE generators --------------------------------------------------

_TEMP_GENS: list[SentenceGen] = [
    lambda a: (
        f"The temperature involved is {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"{_val(a)}{_cond_phrase(a)} — that's the thermal threshold for {_subj(a, 'this process')}."
        if a.value else ""
    ),
    lambda a: (
        f"At {_val(a)}, {_subj(a, 'it')} undergoes"
        f" {random.choice(['a significant change','its transition','the key process'])}."
        if a.value else ""
    ),
    lambda a: (
        f"{_cond_prepend(a)}the temperature {random.choice(['reaches','sits at','registers at'])} {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"Thermally speaking, {_subj(a, 'it')} operates at {_val(a)}"
        + (f", equivalent to {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"The {random.choice(['boiling','melting','operating','transition'])} point"
        f" of {_subj(a, 'this substance')} is {_val(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"Could ordinary materials survive {_val(a)}? That's the regime {_subj(a, 'this process')} operates in{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"Most physical changes you know about happen at far lower temperatures — {_subj(a, 'this one')} kicks in only at {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"At {_val(a)}{_cond_phrase(a)}, {_subj(a, 'it')} crosses a threshold that defines its entire behaviour"
        + (f", equivalent to {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
]


# ---- DISTANCE generators -----------------------------------------------------

_DISTANCE_GENS: list[SentenceGen] = [
    lambda a: (
        f"{_subj(a, 'it').capitalize()} sits {_val(a)} away{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"The distance to {_subj(a, 'it')} is {_val(a)}"
        + (f", or about {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    lambda a: (
        f"{_val(a)} — that's how far {_subj(a, 'it')} is from us."
        if a.value else ""
    ),
    lambda a: (
        f"To reach {_subj(a, 'it')}, you'd need to cross {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"In terms of distance, {_subj(a, 'it')} lies {_val(a)}"
        + (f" — roughly {_eq(a)}" if _eq(a) else "") + f"{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"{_subj(a, 'it').capitalize()} is located {_val(a)} from Earth{_cond_phrase(a)}."
        if a.value else ""
    ),
    lambda a: (
        f"If you were to measure it out, {_subj(a, 'it')} is {_val(a)} away."
        if a.value else ""
    ),
    lambda a: (
        f"Light, the fastest thing in the universe, still needs significant time to cross the {_val(a)} to {_subj(a, 'it')} — making human travel there effectively impossible with current technology."
        if a.value else ""
    ),
    lambda a: (
        f"Here's the scale challenge: {_subj(a, 'it')} is {_val(a)} away"
        + (f" — about {_eq(a)}" if _eq(a) else "")
        + ", and no spacecraft we've built could close that gap in a human lifetime."
        if a.value else ""
    ),
    lambda a: (
        f"What does {_val(a)} actually mean? It means any signal we send to {_subj(a, 'it')} travels at light speed and still takes a measurable journey."
        if a.value else ""
    ),
]


def _strip_subject_verb(raw: str, subject: str) -> str:
    if not subject:
        return raw
    pat = re.compile(
        r"^" + re.escape(subject) + r"\s+(?:is|are|was|were)\s+",
        re.IGNORECASE,
    )
    return pat.sub("", raw).strip()


def _def_subj_lead(a: FactAtom) -> str:
    if not _subj(a):
        return a.raw
    body = _strip_subject_verb(a.raw, a.subject)
    cap = a.subject[0].upper() + a.subject[1:]
    return f"{cap}: {body}"


def _def_question(a: FactAtom) -> str:
    if not _subj(a):
        return a.raw
    body = _strip_subject_verb(a.raw, a.subject)
    subj_display = a.subject[0].upper() + a.subject[1:]
    answer = (body[0].upper() + body[1:]) if body else a.raw
    if answer.lower().startswith(a.subject.lower()):
        answer = _strip_subject_verb(answer, a.subject)
        answer = (answer[0].upper() + answer[1:]) if answer else a.raw
    return f"What is {subj_display}? {answer}"


def _def_breakdown(a: FactAtom) -> str:
    if not _subj(a):
        return a.raw
    body = _strip_subject_verb(a.raw, a.subject)
    cap = a.subject[0].upper() + a.subject[1:]
    return f"Breaking it down: {cap} refers to {body[0].lower() + body[1:] if body else a.raw}"


def _def_negative(a: FactAtom) -> str:
    subj_display = (_subj(a, "it")[0].upper() + _subj(a, "it")[1:])
    body = _strip_subject_verb(a.raw, a.subject)
    anti = random.choice(["a vague abstraction", "a synonym for something simpler", "an arbitrary label"])
    return f"{subj_display} is not {anti} — {body[0].lower() + body[1:] if body else a.raw.lower()}"


def _def_example(a: FactAtom) -> str:
    body = _strip_subject_verb(a.raw, a.subject) if a.subject else a.raw
    cap_body = body[0].upper() + body[1:] if body else a.raw
    subj_display = _subj(a, "it")
    return f"{cap_body} A concrete example of {subj_display} in action makes this immediately clear."


def _def_analogy(a: FactAtom) -> str:
    body = _strip_subject_verb(a.raw, a.subject) if a.subject else a.raw
    subj_display = _subj(a, "it")
    cap_body = body[0].lower() + body[1:] if body else a.raw.lower()
    return f"Think of {subj_display} as a precise tool — one that exists because {cap_body}"


# ---- DEFINITION generators ---------------------------------------------------

_DEFINITION_GENS: list[SentenceGen] = [
    lambda a: a.raw,
    lambda a: _def_subj_lead(a),
    lambda a: _def_question(a),
    lambda a: (
        f"To define it precisely: {a.raw}"
    ),
    lambda a: (
        f"At its essence, {a.raw[0].lower() + a.raw[1:]}"
    ),
    lambda a: _def_breakdown(a),
    lambda a: _def_negative(a),
    lambda a: _def_example(a),
    lambda a: _def_analogy(a),
    lambda a: (
        f"In plain terms: {a.raw[0].lower() + a.raw[1:] if a.raw else ''}"
    ),
]


# ── Generator dispatch ────────────────────────────────────────────────────────

_GEN_MAP: dict[str, list[SentenceGen]] = {
    "speed":       _SPEED_GENS,
    "size":        _SIZE_GENS,
    "date":        _DATE_GENS,
    "count":       _COUNT_GENS,
    "inventor":    _INVENTOR_GENS,
    "composition": _COMPOSITION_GENS,
    "temperature": _TEMP_GENS,
    "distance":    _DISTANCE_GENS,
    "definition":  _DEFINITION_GENS,
}


def _generate_sentence(atom: FactAtom, exclude_gens: set[int] | None = None) -> str:
    gens = _GEN_MAP.get(atom.type, _DEFINITION_GENS)
    indices = list(range(len(gens)))
    if exclude_gens:
        indices = [i for i in indices if i not in exclude_gens]
    random.shuffle(indices)
    for idx in indices:
        try:
            result = gens[idx](atom).strip()
            if result and len(result) > 5:
                return result
        except Exception:
            continue
    return atom.raw


# ── Contextual elaborations per topic ─────────────────────────────────────────

_ELABORATIONS: dict[str, list[str]] = {
    "speed": [
        "Speed like this sits at the edge of what our intuition can comfortably picture.",
        "Comparisons help here — even the fastest aircraft barely scratches this figure.",
        "This number shaped how we engineered everything from concert halls to sonar systems.",
        "The practical applications of knowing this precisely range from architecture to medicine.",
        "Engineers rely on this figure constantly — from speaker placement to explosion modeling.",
        "At this speed, you'd cross a football field in under a millisecond.",
        "The gap between this and the speed of light tells you something important about what's physically achievable.",
        "Precision matters here: even a 1% error in this value cascades into significant miscalculations at scale.",
    ],
    "distance": [
        "Distances at this scale reveal why conventional propulsion can't take us there in a lifetime.",
        "The sheer scale here puts human space travel in stark perspective.",
        "It took light — the fastest thing in the universe — significant time to cross that span, making human travel there effectively impossible with current technology.",
        "Scale like this is why astronomers use light-years rather than kilometres.",
        "Even radio signals, traveling at light speed, need measurable time to cross this gap.",
        "The nearest star is already beyond reach in a human lifetime — this distance compounds that problem enormously.",
        "Numbers at this scale stop being distances and start being timescales: how long it takes light, our fastest proxy, to arrive.",
    ],
    "temperature": [
        "Temperatures at these extremes require entirely different material science.",
        "This threshold marks where ordinary chemistry gives way to plasma physics.",
        "It's a figure that separates what human technology can sustain from what it cannot.",
        "Understanding this value underpins the design of everything from turbines to cryogenic labs.",
        "At this temperature, molecular bonds behave in ways that defy everyday experience.",
        "The engineering challenge of reaching — or surviving — this temperature is itself a field of study.",
        "Most substances we interact with daily don't even approach this regime.",
    ],
    "size": [
        "Scale like this is notoriously difficult to intuit — analogies are more useful than raw numbers.",
        "Dimensions this extreme place the object in a category of its own.",
        "Size here defines what forces dominate — gravity, pressure, or quantum effects.",
        "At this scale, the physics that govern everyday objects no longer apply in familiar ways.",
        "To visualise this meaningfully, you'd need to stack familiar objects until the comparison breaks your mental model.",
        "The ratio between this and a human-scale object is so extreme it requires scientific notation to express cleanly.",
    ],
    "date": [
        "Context matters: what was happening in the world at that moment shapes why this emerged when it did.",
        "Timing is everything — a decade earlier or later and the conditions simply weren't right.",
        "This date anchors an entire lineage of ideas, inventions, and events that followed.",
        "The surrounding decade was unusually fertile for this kind of development — a convergence of need, knowledge, and capability.",
        "Without the technological and intellectual groundwork laid just before this date, it couldn't have happened.",
    ],
    "count": [
        "Numbers like these become meaningful only when you consider what each unit represents.",
        "The quantity alone doesn't tell the whole story — the arrangement matters as much as the count.",
        "That figure reflects not a design choice but a functional requirement: each one serves a specific role.",
        "Change this number by even a small margin and the entire system behaves differently.",
    ],
    "inventor": [
        "Behind every invention is a specific problem that person was determined to solve.",
        "The inventor's broader work often contextualises why this creation took the form it did.",
        "Knowing who built something often reveals what they were actually trying to fix.",
        "Rarely does an invention emerge in isolation — the inventor was almost certainly building on prior work that came close but didn't quite get there.",
        "The personal history of the inventor usually explains the timing as much as any technological readiness.",
    ],
    "composition": [
        "What something is made of often determines every other property it has.",
        "Composition at this level explains behaviour that would otherwise seem arbitrary.",
        "Change even one component and the resulting properties shift in ways that can be dramatic.",
        "The specific ratios here aren't incidental — they're what separate functional from non-functional.",
    ],
    "definition": [
        "Definitions are starting points — the interesting part is usually what they imply.",
        "Precise terminology here matters more than it might first appear.",
        "The boundary cases — what barely qualifies and what doesn't — reveal more about this concept than the central examples.",
        "A definition only becomes useful when you stress-test it against edge cases.",
    ],
}


def _maybe_elaboration(atom: FactAtom, probability: float = 0.40) -> str:
    if random.random() > probability:
        return ""
    options = _ELABORATIONS.get(atom.type, _ELABORATIONS["definition"])
    return random.choice(options)


# ── Single-atom bridging context ──────────────────────────────────────────────

def _single_atom_context(atom: FactAtom) -> str:
    """
    Generate a short bridging context sentence — not an elaboration, but
    something that naturally follows from the atom's fields (conditions,
    subject, year, inventor). Returns "" if nothing meaningful can be built.
    """
    ftype = atom.type
    subj = _subj(atom, "")
    year = atom.extra.get("year", "")
    inventor = atom.extra.get("inventor", "")
    val = _val(atom)

    if ftype == "speed":
        if atom.condition:
            cond = atom.condition
            return f"That figure comes from measuring {subj or 'the phenomenon'} {cond}, where the medium's properties set the upper boundary."
        if val:
            return f"Physicists arrived at {val} by timing the phenomenon across controlled distances and accounting for environmental variables."
        return ""

    if ftype == "distance":
        if val:
            return f"That measurement was refined over time using parallax, radar ranging, and eventually direct telemetry — each method converging on the same answer."
        return ""

    if ftype == "temperature":
        if atom.condition:
            return f"The reading of {val} applies specifically {atom.condition} — shift those conditions and the figure changes."
        if val:
            return f"That {val} threshold was identified experimentally, by observing exactly when the physical or chemical behaviour crossed into a new regime."
        return ""

    if ftype == "size":
        if val:
            return f"The {val} figure represents a {random.choice(['mean','averaged','consensus'])} measurement — individual variation exists, but this is what the data consistently returns."
        return ""

    if ftype == "date":
        if year and inventor:
            return f"The year {year} placed {inventor} in a period where the necessary tools and theoretical groundwork had only just become available."
        if year:
            return f"Around {year}, the broader intellectual climate was shifting in ways that made this kind of development almost inevitable."
        return ""

    if ftype == "inventor":
        if inventor:
            return f"{inventor} later went on to extend this work in related areas, though {_subj(atom, 'this invention')} remained the most widely adopted result."
        return ""

    if ftype == "count":
        if val:
            return f"That count of {val} was established through systematic cataloguing — the methodology itself became a reference standard."
        return ""

    if ftype == "composition":
        body = _composition_body(atom)
        if body and body != atom.raw:
            return f"The specific combination of {body.rstrip('.')} is not arbitrary — it's what produces the physical and chemical properties the substance is known for."
        return ""

    if ftype == "definition":
        subj_disp = subj or "this concept"
        return f"The boundaries of {subj_disp} are worth testing: edge cases often reveal more about the underlying idea than the central examples do."

    return ""


# ── Connective tissue ─────────────────────────────────────────────────────────

_BRIDGES = [
    "On top of that, ",
    "There's also this: ",
    "Worth adding — ",
    "Another angle: ",
    "To layer in more detail: ",
    "Here's something connected: ",
    "And then there's the fact that ",
    "Digging one level deeper: ",
    "Something else worth knowing: ",
    "",
    "",
]

_CONTRAST_BRIDGES = [
    "That said, ",
    "To contrast: ",
    "On the other hand, ",
    "Interestingly though, ",
]

_SEQUENCE_BRIDGES = [
    "Building on that, ",
    "From there, ",
    "This connects to: ",
    "Which leads to: ",
]


def _pick_bridge(prev_type: str, curr_type: str) -> str:
    if prev_type == curr_type:
        return random.choice(_SEQUENCE_BRIDGES + [""])

    pair = frozenset([prev_type, curr_type])

    if pair == frozenset(["speed", "distance"]):
        subj_placeholder = "it"
        return random.choice([
            "Covering that distance at this speed means the journey takes a very specific amount of time — ",
            "Put the two together: traveling at that speed across that distance, ",
            "Speed and distance interact here: ",
        ])

    if pair == frozenset(["date", "inventor"]):
        return random.choice([
            "That date is inseparable from who drove it — ",
            "The story behind the timing is really a story about the person: ",
            "To understand when, you need to understand who — ",
        ])

    if pair == frozenset(["count", "size"]):
        return random.choice([
            "Scale and quantity compound each other here: ",
            "The count only becomes meaningful when you factor in the size — ",
            "To frame the scale: ",
        ])

    if pair == frozenset(["temperature", "composition"]):
        return random.choice([
            "What it's made of explains why it behaves the way it does at that temperature — ",
            "Composition and thermal behaviour are linked: ",
        ])

    if pair == frozenset(["inventor", "date"]):
        return random.choice([
            "The discovery narrative connects directly to the timing: ",
            "Behind that date is a person who made it happen — ",
        ])

    if "definition" in pair:
        return random.choice([
            "With that definition in place, ",
            "Grounding the terminology: ",
            "That context makes the next point land differently — ",
        ])

    return random.choice(_BRIDGES)


# ── Query-to-focus mapping ────────────────────────────────────────────────────

_QUERY_FOCUS_MAP = [
    (re.compile(r"\b(how fast|speed|velocity|mph|km.h|m.s)\b", re.I), "speed"),
    (re.compile(r"\b(how far|distance|away|light.year|parsec)\b", re.I), "distance"),
    (re.compile(r"\b(how big|size|diameter|mass|weight|height|wide|large)\b", re.I), "size"),
    (re.compile(r"\b(temperature|hot|cold|°[CF]|boiling|melting|degrees?)\b", re.I), "temperature"),
    (re.compile(r"\b(how many|number of|count|how much)\b", re.I), "count"),
    (re.compile(r"\b(who (made|invented|created|discovered|built|founded))\b", re.I), "inventor"),
    (re.compile(r"\b(made of|consist|composed|contain|formula|element)\b", re.I), "composition"),
    (re.compile(r"\b(when|year|founded|invented|created|date|old|ago)\b", re.I), "date"),
]


def _infer_focus(query: str) -> str | None:
    for pattern, ftype in _QUERY_FOCUS_MAP:
        if pattern.search(query):
            return ftype
    return None


# ── Multi-fact composition ────────────────────────────────────────────────────

def _compose_multiple(atoms: list[FactAtom], focus: str | None, max_parts: int = 5) -> str:
    if not atoms:
        return ""

    strategy = random.choice(["focus_first", "chronological", "surprising_lead", "layered"])
    ordered = list(atoms)

    if strategy == "focus_first" and focus:
        focused = [a for a in ordered if a.type == focus]
        rest = [a for a in ordered if a.type != focus]
        ordered = focused + rest
    elif strategy == "surprising_lead":
        ordered.sort(key=lambda a: -len(a.equivalents))
    elif strategy == "chronological":
        dated = [a for a in ordered if a.type == "date" or a.extra.get("year")]
        rest = [a for a in ordered if a not in dated]
        ordered = dated + rest

    parts: list[str] = []
    used_gen_indices: dict[str, set[int]] = {}
    prev_type = ""
    limit = min(max_parts, len(ordered))

    for i, atom in enumerate(ordered[:limit]):
        gen_pool = used_gen_indices.setdefault(atom.type, set())
        sentence = _generate_sentence(atom, exclude_gens=gen_pool)

        gens = _GEN_MAP.get(atom.type, _DEFINITION_GENS)
        for idx, gen in enumerate(gens):
            try:
                if gen(atom).strip() == sentence:
                    gen_pool.add(idx)
                    break
            except Exception:
                pass

        if not sentence:
            continue

        bridge = _pick_bridge(prev_type, atom.type) if i > 0 else ""
        parts.append(bridge + sentence)
        prev_type = atom.type

        if i == 0:
            elab = _maybe_elaboration(atom, probability=0.5)
            if elab:
                parts.append(elab)
        elif i == limit - 1:
            elab = _maybe_elaboration(atom, probability=0.35)
            if elab:
                parts.append(elab)

    return " ".join(p for p in parts if p)


# ── Query-focused atom selection ──────────────────────────────────────────────

def _score_atom_for_query(atom: FactAtom, query: str, focus: str | None) -> float:
    score = 0.0
    if focus and atom.type == focus:
        score += 10.0
    q_words = set(re.findall(r"[a-z]{3,}", query.lower()))
    raw_lower = atom.raw.lower()
    hits = sum(1 for w in q_words if w in raw_lower)
    score += hits * 2.0
    if atom.value:
        score += 3.0
    if atom.equivalents:
        score += 1.5
    if 15 < len(atom.raw) < 120:
        score += 1.0
    return score


def _select_atoms(atoms: list[FactAtom], query: str, focus: str | None, max_atoms: int = 3) -> list[FactAtom]:
    if not atoms:
        return atoms
    scored = sorted(atoms, key=lambda a: -_score_atom_for_query(a, query, focus))

    # Shuffle near-tied atoms so different facts surface on repeat questions
    if len(scored) > 1:
        top_score = _score_atom_for_query(scored[0], query, focus)
        near_ties = [a for a in scored if _score_atom_for_query(a, query, focus) >= top_score * 0.82]
        if len(near_ties) > 1:
            random.shuffle(near_ties)
            rest = [a for a in scored if a not in near_ties]
            scored = near_ties + rest

    selected: list[FactAtom] = []
    seen_types: set[str] = set()

    # Always take the best-scoring atom first
    if scored:
        selected.append(scored[0])
        seen_types.add(scored[0].type)

    # Fill remaining slots with diverse, high-scoring atoms
    for atom in scored[1:]:
        if len(selected) >= max_atoms:
            break
        if atom.type in seen_types and len(selected) < max_atoms - 1:
            continue
        selected.append(atom)
        seen_types.add(atom.type)

    # If diversity filtering left us short, backfill from scored list
    if len(selected) < max_atoms:
        for atom in scored:
            if atom not in selected:
                selected.append(atom)
            if len(selected) >= max_atoms:
                break

    if focus:
        focused = [a for a in selected if a.type == focus]
        if focused and selected[0] not in focused:
            selected = focused[:1] + [a for a in selected if a.type != focus]
    return selected[:max_atoms]


def _extract_direct_answer(query: str, content: str, atoms: list[FactAtom], focus: str | None) -> str | None:
    """Build a crisp lead sentence that answers the query directly."""
    qn = _normalize(query)
    aspect = _detect_aspect(qn)
    if aspect:
        hit = _extract_aspect(content, aspect)
        if hit and len(hit) > 15:
            return hit.strip()

    if atoms:
        top = max(atoms, key=lambda a: _score_atom_for_query(a, query, focus))
        if top.value and top.unit:
            label = top.subject.replace("_", " ") if top.subject else "this"
            templates = [
                f"**{top.value} {top.unit}** is the headline figure for {label}.",
                f"The number to know: **{top.value} {top.unit}** for {label}.",
                f"**{top.value} {top.unit}** — that's the key measurement for {label}.",
            ]
            return random.choice(templates)
        if top.value:
            templates = [
                f"**{top.value}** is the central number here.",
                f"The figure that matters most: **{top.value}**.",
                f"**{top.value}** stands out as the headline stat.",
            ]
            return random.choice(templates)

    for para in content.split("\n\n"):
        p = re.sub(r"^#{1,4}\s+", "", para.strip())
        if len(p) < 20 or p.startswith("```") or p.startswith("["):
            continue
        first = re.split(r"(?<=[.!?])\s+", _clean(p))[0]
        if 20 <= len(first) <= 220:
            return first
    return None


def _build_key_takeaway(atoms: list[FactAtom], query: str) -> str:
    if not atoms:
        return ""
    top = max(atoms, key=lambda a: _score_atom_for_query(a, query, _infer_focus(query)))
    fact = _generate_sentence(top)
    if len(fact) > 180:
        fact = fact[:177].rsplit(" ", 1)[0] + "…"
    label = random.choice(["Bottom line", "Key takeaway", "What to remember", "The essential point"])
    return f"**{label}:** {fact}"


def _thread_preamble(memory: dict | None) -> str:
    if not memory or not memory.get("continuing_thread"):
        return ""
    if memory.get("thread_confidence", 0) < 55:
        return ""
    topic = (memory.get("active_topic") or memory.get("last_user_query") or "").strip()
    if not topic:
        return ""
    short = topic[:70] + ("…" if len(topic) > 70 else "")
    return random.choice([
        f"Picking up on **{short}** — here's a fuller picture:",
        f"Sticking with your thread about **{short}**:",
        f"To go deeper on **{short}**:",
        f"Building on what we were discussing — **{short}**:",
    ])


def _enrich_response(
    body: str,
    query: str,
    content: str,
    atoms: list[FactAtom],
    *,
    elaborate: bool,
    memory: dict | None = None,
) -> str:
    """Wrap NLG body with direct answer, thread context, and optional takeaway."""
    if not body or not body.strip():
        return body

    parts: list[str] = []
    preamble = _thread_preamble(memory)
    if preamble:
        parts.append(preamble)

    focus = _infer_focus(query)
    direct = _extract_direct_answer(query, content, atoms, focus)
    if direct and direct.lower() not in body.lower()[: max(80, len(direct))]:
        parts.append(direct)

    parts.append(body)

    if elaborate or (atoms and len(atoms) >= 2):
        takeaway = _build_key_takeaway(atoms, query)
        if takeaway and takeaway.lower() not in body.lower():
            parts.append(takeaway)

    return "\n\n".join(p.strip() for p in parts if p and p.strip())


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_from_content(
    content: str,
    query: str,
    max_atoms: int = 3,
    elaborate: bool = False,
    memory: dict | None = None,
) -> str:
    """
    Takes a KB content string and the original query.
    Extracts fact atoms, picks random sentence generators, and composes a fresh
    natural-language response. Every call produces a structurally different result.
    """
    if not content or not content.strip():
        return "I couldn't find specific information on that."

    atoms = extract_fact_atoms(content)
    focus = _infer_focus(query)

    if not atoms:
        return content

    relevant = _select_atoms(atoms, query, focus, max_atoms=max_atoms)

    if len(relevant) == 1:
        atom = relevant[0]
        sentence = _generate_sentence(atom)
        parts = [sentence]
        if elaborate or random.random() < 0.65:
            ctx = _single_atom_context(atom)
            if ctx:
                parts.append(ctx)
        elab_prob = 0.85 if elaborate else 0.55
        elab = _maybe_elaboration(atom, probability=elab_prob)
        if elab:
            parts.append(elab)
        body = " ".join(parts).strip()
        return _enrich_response(body, query, content, relevant, elaborate=elaborate, memory=memory)

    result = _compose_multiple(relevant, focus, max_parts=max_atoms)
    if elaborate and result and len(relevant) >= 2:
        extra = _maybe_elaboration(relevant[0], probability=0.7)
        if extra:
            result = result + " " + extra
    body = result if result else _generate_sentence(relevant[0])
    return _enrich_response(body, query, content, relevant, elaborate=elaborate, memory=memory)


# =============================================================================
# VARY STRUCTURE — response flow and structural rewriting
# =============================================================================

# ---------------------------------------------------------------------------
# SECTION 1 — STRUCTURAL LAYOUTS
# ---------------------------------------------------------------------------

# A layout function receives a list of plain-text fact strings and returns a
# formatted response body (no opener / closer yet).
_LayoutFn = Callable[[list[str]], str]


def _layout_flowing_paragraph(facts: list[str]) -> str:
    """All facts fused into one continuous paragraph with varied connectors."""
    if not facts:
        return ""
    connectors = _pick_connectors(len(facts) - 1)
    parts: list[str] = [facts[0].rstrip(".")]
    for i, fact in enumerate(facts[1:], start=0):
        conn = connectors[i]
        f = fact[0].lower() + fact[1:] if fact and not fact[0].isupper() else fact
        f = f.rstrip(".")
        parts.append(f"{conn}{f}")
    return ". ".join(parts) + "."


def _layout_bullets_with_lead(facts: list[str]) -> str:
    """Lead sentence, then bullet list of remaining facts."""
    if not facts:
        return ""
    lead = facts[0]
    bullets = facts[1:] if len(facts) > 1 else facts
    if not bullets:
        return lead
    items = "\n".join(f"- {f.rstrip('.')}" for f in bullets)
    return f"{lead}\n\n{items}"


def _layout_lead_fact_then_support(facts: list[str]) -> str:
    """Most important fact bold/prominent, then supporting details as prose."""
    if not facts:
        return ""
    lead = facts[0]
    supporting = facts[1:]
    if not supporting:
        return f"**{lead}**"
    support_text = " ".join(s.rstrip(".") + "." for s in supporting)
    return f"**{lead}**\n\n{support_text}"


def _layout_qa_style(facts: list[str]) -> str:
    """
    Frames facts as implicit Q-and-A pairs using a rotation of question starters.
    E.g. "What makes this remarkable? X. How does that work? Y."
    """
    if not facts:
        return ""
    if len(facts) == 1:
        return facts[0]

    _qa_prompts = [
        "What makes this significant?",
        "How does that work?",
        "Why does that matter?",
        "What's the practical upshot?",
        "What does that actually mean?",
        "How did this come about?",
        "What's the key detail here?",
        "Why is that the case?",
        "What's worth remembering?",
        "What's the broader picture?",
        "How does this compare?",
        "What follows from that?",
    ]
    prompts = random.sample(_qa_prompts, min(len(facts), len(_qa_prompts)))
    pairs: list[str] = []
    for i, fact in enumerate(facts):
        if i < len(prompts):
            pairs.append(f"*{prompts[i]}* {fact}")
        else:
            pairs.append(fact)
    return " ".join(pairs)


def _layout_progressive_reveal(facts: list[str]) -> str:
    """
    Most important → supporting detail → interesting aside.
    Uses section-level signals rather than bullet markers.
    """
    if not facts:
        return ""
    if len(facts) == 1:
        return facts[0]

    _tier_intros = [
        ("The core of it:", "To add some depth:", "And here's a detail worth knowing:"),
        ("The short answer:", "Behind that:", "One more layer:"),
        ("What you need to know:", "The reason that's true:", "Interesting footnote:"),
        ("Put simply:", "Digging in:", "Worth noting on top of that:"),
    ]
    tiers = random.choice(_tier_intros)
    parts: list[str] = []
    for i, fact in enumerate(facts):
        if i < len(tiers):
            parts.append(f"{tiers[i]} {fact}")
        else:
            parts.append(fact)
    return "\n\n".join(parts)


def _layout_reverse_pyramid(facts: list[str]) -> str:
    """
    Context first, narrowing to the specific key fact last.
    Works well for historical / explanatory content.
    """
    if not facts:
        return ""
    if len(facts) == 1:
        return facts[0]

    # Put facts in reverse order so specific key fact lands at end
    reordered = list(reversed(facts))
    connectors = _pick_connectors(len(reordered) - 1)
    _narrowing_intros = [
        "More specifically, ",
        "Narrowing that down: ",
        "To get to the point: ",
        "The specific detail: ",
        "Which brings it to: ",
        "The key takeaway: ",
    ]
    parts: list[str] = [reordered[0].rstrip(".")]
    for i, fact in enumerate(reordered[1:], start=0):
        if i == len(reordered) - 2:  # final fact gets narrowing intro
            intro = random.choice(_narrowing_intros)
            f = fact[0].lower() + fact[1:] if fact else fact
            parts.append(f"{intro}{f.rstrip('.')}")
        else:
            conn = connectors[i]
            f = fact[0].lower() + fact[1:] if fact else fact
            parts.append(f"{conn}{f.rstrip('.')}")
    return ". ".join(parts) + "."


_LAYOUTS: list[_LayoutFn] = [
    _layout_flowing_paragraph,
    _layout_bullets_with_lead,
    _layout_lead_fact_then_support,
    _layout_qa_style,
    _layout_progressive_reveal,
    _layout_reverse_pyramid,
]


# ---------------------------------------------------------------------------
# SECTION 2 — CONNECTORS / TRANSITIONS
# ---------------------------------------------------------------------------

_CONNECTORS: list[str] = [
    "The reason for this is ",
    "What makes this interesting: ",
    "Here's why that matters: ",
    "Building on that, ",
    "The flip side of this is ",
    "Underneath that, ",
    "What follows from this is ",
    "It's worth adding that ",
    "That connects to something else: ",
    "The practical side of this is ",
    "Digging deeper, ",
    "Related to that, ",
    "One layer down, ",
    "This ties directly to ",
    "The backstory here is ",
    "To put that in context, ",
    "The mechanism behind this: ",
    "What that implies is ",
    "Tied to that, ",
    "The consequence of this is ",
    "A piece of the picture that's easy to miss: ",
    "Something that follows naturally from this: ",
    "The detail that makes it concrete: ",
    "To sharpen that point, ",
]


def _pick_connectors(n: int) -> list[str]:
    """Return n connectors, sampled without replacement where possible."""
    pool = _CONNECTORS[:]
    random.shuffle(pool)
    # If we need more than the pool, cycle
    result: list[str] = []
    while len(result) < n:
        result.extend(pool[: n - len(result)])
        random.shuffle(pool)
    return result[:n]


# ---------------------------------------------------------------------------
# SECTION 3 — OPENING VARIATION (by question type)
# ---------------------------------------------------------------------------

_OPENERS: dict[str, list[str]] = {
    # "how fast / how quick / how speedy"
    "speed": [
        "The speed numbers here are genuinely striking.",
        "Speed-wise, this is one of those cases where the numbers do most of the talking.",
        "When it comes to how fast this actually moves —",
        "The velocity figures for this sit at an interesting level.",
        "If you want the raw speed data:",
        "In terms of pace, here's what the measurements show.",
    ],
    # "when did / what year / when was"
    "date": [
        "The timeline here is worth knowing in full.",
        "Pinning the date on this takes a bit of context.",
        "Chronologically, this is how it played out.",
        "The historical record on this is fairly clear.",
        "To place this correctly in time:",
        "There's a specific date attached to this — and the context matters.",
    ],
    # "who invented / who made / who created"
    "inventor": [
        "Credit for this goes somewhere specific.",
        "The origin story here is worth telling.",
        "Attributing this correctly requires a bit of history.",
        "There's a clear answer to who made this happen.",
        "The inventor's story is tied directly to why this works the way it does.",
        "The person behind this also shaped how it's used today.",
    ],
    # "what is / what are / what does"
    "definition": [
        "Here's what this actually refers to.",
        "The definition here has a couple of layers.",
        "At its core, this is what you're dealing with.",
        "To define this precisely:",
        "This term means something specific — and the specifics matter.",
        "The best way to put this in plain terms:",
    ],
    # "how fast" already above; "how many / how much / how big"
    "quantity": [
        "The numbers on this are specific.",
        "To give you the actual figures:",
        "Measured precisely, here's what this comes out to.",
        "The quantities here are worth knowing exactly.",
        "When you put exact numbers to this:",
        "The scale of this becomes clear once you see the figures.",
    ],
    # general factual questions
    "general": [
        "Here's what the record actually shows.",
        "To put this accurately:",
        "The answer here has a few moving parts.",
        "What's established on this:",
        "This is one of those cases where the details make the answer.",
        "The direct answer, with the context that makes it make sense:",
        "To cover this properly:",
        "Here's how this actually works.",
    ],
}


def _classify_query(query: str) -> str:
    """Map a query string to one of the opener category keys."""
    q = query.lower()
    if re.search(r"how (fast|quick|speedy|rapidly)", q):
        return "speed"
    if re.search(r"(when (did|was|were|is)|what year|what date|how old)", q):
        return "date"
    if re.search(r"who (made|invented|created|discovered|built|designed|founded)", q):
        return "inventor"
    if re.search(r"(how many|how much|how big|how large|how heavy|how tall|how long|how wide|how deep|how far)", q):
        return "quantity"
    if re.search(r"(what is|what are|what does|what do|what did|define|explain)", q):
        return "definition"
    return "general"


def _pick_opener(query: str) -> str:
    category = _classify_query(query)
    options = _OPENERS.get(category, _OPENERS["general"])
    return random.choice(options)


# ---------------------------------------------------------------------------
# SECTION 4 — CLOSERS
# ---------------------------------------------------------------------------

_CLOSERS: list[str] = [
    # offer more depth
    "There's more to pull on here if you want to go further.",
    "Happy to break down any specific part of that in more detail.",
    "The topic goes deeper if you want to follow it.",
    "Any piece of that worth expanding on?",
    "There's a longer version of this if any part is worth pursuing.",
    # clean endings
    "That's the full picture on this one.",
    "That covers the core of it.",
    "Those are the key points.",
    "",
    "",
    # follow-up questions
    "Curious what part of this matters most to you?",
    "Is there a specific angle of this you want to dig into?",
    "Does any of that raise a follow-up question?",
    "Want the historical context behind this, or is the short version enough?",
    "Anything in there that needs more explanation?",
    # light observations
    "It's one of those areas where the detail rewards closer inspection.",
    "The surface answer is simple — it's the mechanism underneath that's interesting.",
]


def _pick_closer() -> str:
    return random.choice(_CLOSERS)


# ---------------------------------------------------------------------------
# SECTION 5 — MARKDOWN PARSING AND RESTRUCTURING
# ---------------------------------------------------------------------------

def _parse_markdown_sections(content: str) -> list[tuple[str | None, str]]:
    """
    Parse content into (header, body) pairs.
    header is None for content before the first heading.
    Returns list of (header_text_or_None, body_text).
    """
    lines = content.split("\n")
    sections: list[tuple[str | None, str]] = []
    current_header: str | None = None
    current_body: list[str] = []

    for line in lines:
        heading_match = re.match(r"^#{1,4}\s+(.+)", line)
        if heading_match:
            if current_body or current_header is not None:
                body = "\n".join(current_body).strip()
                if body or current_header is not None:
                    sections.append((current_header, body))
            current_header = heading_match.group(1).strip()
            current_body = []
        else:
            current_body.append(line)

    # Flush last section
    if current_body or current_header is not None:
        body = "\n".join(current_body).strip()
        sections.append((current_header, body))

    return sections if sections else [(None, content)]


def _extract_sentences(text: str) -> list[str]:
    """
    Split text into individual fact sentences, stripping bullet markers.
    Preserves sentences that end in '.' '!' '?'. Handles inline markdown.
    """
    # Remove bullet markers
    text = re.sub(r"^\s*[-*•]\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic but keep text
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    # Split on sentence boundaries
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    # Filter empty / heading-like
    sentences = []
    for s in raw:
        s = s.strip()
        if not s or len(s) < 15:
            continue
        if re.match(r"^#{1,4}\s", s):
            continue
        # Skip fragments that start with a lowercase connector word or punctuation
        # (artifacts from stripping inline parens / em-dashes)
        if re.match(r"^[,;—\-]", s) or re.match(r"^[a-z]{1,3}\s", s):
            continue
        sentences.append(s)
    return sentences


def _restructure_markdown(content: str) -> tuple[list[str], bool]:
    """
    Decide how to handle markdown headings.
    Returns (fact_list, had_markdown).

    Three strategies, chosen randomly:
      A) Strip headings entirely — weave header text into sentences as context.
      B) Keep first heading as a lead sentence prefix; strip rest.
      C) Strip all headings silently (body sentences only).
    """
    sections = _parse_markdown_sections(content)
    had_markdown = any(h is not None for h, _ in sections)

    if not had_markdown:
        # No headings — just return sentences
        return _extract_sentences(content), False

    strategy = random.choice(["weave", "lead", "strip"])
    facts: list[str] = []

    if strategy == "weave":
        # Turn each header into a contextual intro for its body sentences
        for header, body in sections:
            body_sentences = _extract_sentences(body)
            if header and body_sentences:
                # Prepend header context to the first sentence of this section
                first = body_sentences[0]
                body_sentences[0] = f"On the topic of {header.lower()}: {first[0].lower()}{first[1:]}" \
                    if not first[0].isupper() else f"On the topic of {header.lower()}: {first}"
            facts.extend(body_sentences)

    elif strategy == "lead":
        # First header becomes a lead sentence; rest are silently stripped
        lead_injected = False
        for header, body in sections:
            body_sentences = _extract_sentences(body)
            if header and not lead_injected and body_sentences:
                body_sentences[0] = f"{header} — {body_sentences[0][0].lower()}{body_sentences[0][1:]}"
                lead_injected = True
            facts.extend(body_sentences)

    else:  # strip
        for _, body in sections:
            facts.extend(_extract_sentences(body))

    return [f for f in facts if f], True


# ---------------------------------------------------------------------------
# SECTION 6 — FACT VARIATION (sentence-level rephrasing)
# ---------------------------------------------------------------------------

_EMPHASIS_PREFIXES = (
    "Notably, ",
    "Specifically, ",
    "Worth highlighting: ",
    "In precise terms, ",
)


def _maybe_rephrase(fact: str) -> str:
    """
    Occasionally reword short facts using one of several micro-patterns.
    Only applied to facts under 180 chars that don't already have a prefix.
    """
    if len(fact) > 180 or "\n" in fact:
        return fact
    # Don't double-apply
    if fact.startswith(_EMPHASIS_PREFIXES):
        return fact

    choice = random.random()

    if choice < 0.12:
        # "X, Y" → "Y — X" (clause swap)
        if ", " in fact[:90]:
            parts = fact.split(", ", 1)
            if len(parts) == 2 and len(parts[0]) > 5 and len(parts[1]) > 5:
                return f"{parts[1].strip()} — {parts[0][0].lower()}{parts[0][1:]}"

    elif choice < 0.22:
        # Pull a trailing parenthetical to the front
        m = re.search(r"^(.+?)\s*\(([^)]+)\)\s*\.?$", fact)
        if m:
            return f"{m.group(2).strip()} — {m.group(1).strip().rstrip('.')}"

    elif choice < 0.35:
        # Add a soft emphasis prefix
        return random.choice(_EMPHASIS_PREFIXES) + fact[0].lower() + fact[1:]

    return fact


# ---------------------------------------------------------------------------
# SECTION 7 — GUARD: PASS-THROUGH FOR CODE-HEAVY CONTENT
# ---------------------------------------------------------------------------

def _should_pass_through(content: str) -> bool:
    """Return True if content should not be restructured (e.g. code blocks)."""
    code_fence_count = content.count("```")
    if code_fence_count >= 2:
        return True
    if re.match(r"^\s*```", content.strip()):
        return True
    return False


# ---------------------------------------------------------------------------
# SECTION 8 — MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def vary_structure(content: str, query: str) -> str:
    """
    Take any knowledge-base content string and return a structurally varied
    version. Same facts, different flow every call.

    Parameters
    ----------
    content : str
        The raw KB answer — may contain markdown headings, bullet lists,
        bold text, etc.
    query : str
        The original user question. Used to select appropriate opener type.

    Returns
    -------
    str
        A rewritten response with varied structure, connectors, opener, and
        closer. Code-heavy content is returned unchanged.
    """
    if not content or not content.strip():
        return content

    # Never restructure code blocks or build responses
    if _should_pass_through(content):
        return content

    # --- Parse and extract facts ---
    facts, had_markdown = _restructure_markdown(content)

    if not facts:
        # Nothing parsed — return as-is
        return content

    # --- Apply per-fact micro-variation ---
    facts = [_maybe_rephrase(f) for f in facts]

    # --- Pick structural layout ---
    layout_fn = random.choice(_LAYOUTS)

    # For very short content (1–2 sentences), avoid layouts that need 3+ facts
    if len(facts) <= 2:
        layout_fn = random.choice([
            _layout_flowing_paragraph,
            _layout_lead_fact_then_support,
        ])

    body = layout_fn(facts)

    # --- Pick opener ---
    opener = _pick_opener(query)

    # --- Pick closer (not always) ---
    include_closer = random.random() < 0.72
    closer = _pick_closer() if include_closer else ""

    # --- Assemble ---
    parts: list[str] = []

    # Only add opener before prose body, not before a markdown heading
    if opener and not body.lstrip().startswith("#"):
        parts.append(opener)
        parts.append("\n\n")

    parts.append(body)

    if closer:
        parts.append(f"\n\n{closer}")

    return "".join(parts).strip()


# ---------------------------------------------------------------------------
# SECTION 9 — CONVENIENCE: drop-in replacement shim for brain.forge()
# ---------------------------------------------------------------------------

def _mode_depth(mode: str, depth: int) -> int:
    """Map frontend mode + thread depth to NLG depth."""
    if mode == "forge_thinking":
        return max(depth, 2)
    if mode == "forge_instant":
        return 0
    return max(depth, 1)


def _mode_max_atoms(mode: str, depth: int) -> int:
    if mode == "forge_thinking":
        return 9 if depth >= 2 else 7
    if mode == "forge_instant":
        return 3
    return 7 if depth >= 2 else 6


def forge(
    content: str,
    query: str,
    intent: str = "knowledge",
    depth: int = 0,
    mode: str = "forge_code",
    memory: dict | None = None,
) -> str:
    """
    Drop-in replacement for brain.forge().

    For intents that involve code or build output the content is returned
    unchanged.

    For factual knowledge responses the pipeline is:
      1. nlg_engine.generate_from_content() — rewrites content from fact atoms
         (different sentence construction each time, not just different order).
      2. vary_structure() — applies structural layout variation on top.

    mode controls response depth:
      forge_instant  — concise, 1-2 facts, skip elaboration
      forge_code     — balanced, 3-4 facts (default)
      forge_thinking — thorough, 5-7 facts with elaboration
    """
    if intent in ("build_game", "build_app", "build_any", "math"):
        return content

    # Pass-through for code-heavy content
    if _should_pass_through(content):
        return content

    effective_depth = _mode_depth(mode, depth)
    max_atoms = _mode_max_atoms(mode, effective_depth)
    qn = _normalize(query)

    # Specific questions: extract the core fact, then rewrite with NLG variation
    if _is_specific_question(qn) and intent in (
        "knowledge", "space", "earth", "science", "history", "animals", "programming",
    ):
        exact = _extract_exact_answer(query, content)
        if exact and len(exact) >= 8:
            if mode == "forge_instant":
                return _vary_exact_response(query, exact, mode, memory, content)
            try:
                support = _one_support_line(content, query, exact) if content else None
                mini = exact if not support else f"{exact}\n\n{support}"
                if content and len(content) > len(mini):
                    mini = f"{mini}\n\n{content[:600]}"
                nlg_output = generate_from_content(
                    mini,
                    query,
                    max_atoms=2 if mode == "forge_code" else 3,
                    elaborate=mode == "forge_thinking",
                    memory=memory,
                )
                if nlg_output and len(nlg_output) >= 20:
                    structured = vary_structure(nlg_output, query)
                    if mode == "forge_code" and effective_depth >= 1 and intent != "programming":
                        brief = _brief_reasoning_line(query, intent, memory)
                        if brief and random.random() < 0.55:
                            return f"{brief}\n\n{structured}"
                    return structured
            except Exception:
                pass
            return _vary_exact_response(query, exact, mode, memory, content)

    # Instant mode: extract the most relevant fact directly, still vary phrasing
    if mode == "forge_instant" and intent in ("knowledge", "space", "earth", "science", "history", "animals"):
        exact = _extract_exact_answer(query, content)
        if exact:
            return _vary_exact_response(query, exact, mode, memory, content)
        first_para = content.split("\n\n")[0].strip()
        first_para = re.sub(r'^#{1,4}\s+', '', first_para)
        if len(first_para) >= 20:
            return _vary_exact_response(query, first_para, mode, memory, content)

    # NLG atom-level rewrite for factual intents
    if intent in ("knowledge", "space", "earth", "science", "history", "animals", "programming"):
        try:
            elaborate = mode == "forge_thinking" or (mode == "forge_code" and effective_depth >= 1)
            nlg_output = generate_from_content(
                content, query,
                max_atoms=max_atoms,
                elaborate=elaborate,
                memory=memory,
            )
            if nlg_output and len(nlg_output) >= 20:
                structured = vary_structure(nlg_output, query)
                if mode == "forge_code" and effective_depth >= 1 and intent != "programming":
                    brief = _brief_reasoning_line(query, intent, memory)
                    if brief:
                        return f"{brief}\n\n{structured}"
                return structured
        except Exception:
            pass

    structured = vary_structure(content, query)
    return structured


def _brief_reasoning_line(query: str, intent: str, memory: dict | None) -> str:
    """One-line reasoning hint for forge_code on threaded or complex queries."""
    focus = _infer_focus(query) or "the core facts"
    q_short = query[:70] + ("…" if len(query) > 70 else "")
    if memory and memory.get("continuing_thread"):
        options = [
            (
                f"*Approach:* continuing our thread — prioritising **{focus}** "
                f"to answer \"{q_short}\" comprehensively."
            ),
            (
                f"*Working from context:* building on what we discussed — "
                f"focusing on **{focus}** for \"{q_short}\"."
            ),
            (
                f"*Thread carry-over:* still on this topic — pulling **{focus}** "
                f"to address \"{q_short}\"."
            ),
        ]
        return random.choice(options)
    options = [
        (
            f"*Approach:* pulling **{focus}** from the knowledge base to give a "
            f"complete answer to \"{q_short}\"."
        ),
        (
            f"*How I'm answering:* scanning for **{focus}** to respond to "
            f"\"{q_short}\"."
        ),
        (
            f"*Strategy:* matching your question to **{focus}** in the knowledge base."
        ),
        (
            f"*Reading your question as:* a request about **{focus}** — "
            f"here's what I found."
        ),
    ]
    return random.choice(options)


def _build_thinking_header(
    query: str,
    intent: str,
    memory: dict | None = None,
    max_atoms: int = 5,
) -> str:
    """Generate a structured thinking-process header for forge_thinking mode."""
    intent_labels = {
        "knowledge": "General knowledge lookup",
        "space": "Space & astronomy analysis",
        "earth": "Earth science evaluation",
        "science": "Scientific concept breakdown",
        "history": "Historical context review",
        "animals": "Biological fact retrieval",
        "programming": "Programming concept analysis",
    }
    label = intent_labels.get(intent, "Query analysis")
    focus = _infer_focus(query) or "multi-faceted facts"
    q_short = query[:80] + ("…" if len(query) > 80 else "")

    steps = [
        "1. **Parse** — understand what the user is really asking",
        f"2. **Focus** — prioritise **{focus}**-type facts from the knowledge base",
        f"3. **Select** — choose up to **{max_atoms}** query-relevant atoms, skip noise",
        "4. **Compose** — lead with a direct answer, then layer context and connections",
        "5. **Synthesise** — add takeaway and tie everything back to the original question",
    ]
    if memory and memory.get("continuing_thread"):
        topic = (memory.get("active_topic") or "")[:55]
        steps.insert(1, f"2. **Context** — continues our discussion about \"{topic}\"")
        for i, step in enumerate(steps):
            steps[i] = re.sub(r"^\d+\.", f"{i + 1}.", step)

    return (
        f"### Thinking Process\n"
        f"- **Intent:** {label}\n"
        f"- **Query:** \"{q_short}\"\n"
        f"- **Reasoning steps:**\n"
        + "\n".join(f"  {s}" for s in steps)
    )


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _sample = """### Speed of Light

The speed of light in a vacuum is **299,792,458 metres per second** (approximately 300,000 km/s).
This constant, denoted *c*, is the universal speed limit — nothing with mass can reach it.
Light takes about **8 minutes 20 seconds** to travel from the Sun to the Earth.
It takes roughly **1.3 seconds** to travel from the Earth to the Moon.
Einstein's special relativity is built on *c* being constant for all observers."""

    _queries = [
        "how fast does light travel",
        "what is the speed of light",
        "when was the speed of light measured",
        "how many seconds does light take to reach earth",
    ]

    for _q in _queries:
        print(f"\n{'=' * 60}")
        print(f"QUERY: {_q}")
        print("-" * 60)
        print(vary_structure(_sample, _q))


# =============================================================================
# GREETINGS
# =============================================================================

_GREETING_INTROS = [
    "I'm **ForgeAI** — your local AI.",
    "**ForgeAI** here.",
    "**ForgeAI** — running fully offline on your machine.",
    "Hey, **ForgeAI** is up.",
    "**ForgeAI** ready.",
    "Local AI, fully offline — **ForgeAI**.",
]

_CAPABILITY_SETS = [
    [
        "- **Build games** — `make a snake game`, `build flappy bird`, `create a space shooter`",
        "- **Build apps** — `make a calculator`, `build a kanban board`, `create a budget tracker`",
        "- **Answer questions** — science, space, history, animals, math, programming",
        "- **Solve math** — derivatives, integrals, trig, algebra",
    ],
    [
        "- **Games** — any arcade game, built and playable instantly",
        "- **Apps & tools** — calculators, timers, trackers, converters, drawing tools",
        "- **Science & space** — from black holes to DNA to quantum mechanics",
        "- **Math** — calculus, trig, algebra, step-by-step",
        "- **History & programming** — language origins, code examples, events",
    ],
    [
        "- **Build something** — games, apps, tools — just describe it",
        "- **Ask anything** — science, space, history, animals, people",
        "- **Math problems** — I solve them step by step",
        "- **Programming** — any language, any concept, with examples",
    ],
    [
        "- Games and apps — built live, playable in-browser",
        "- Science, space, animals, history — deep knowledge base",
        "- Math — calculus, trig, algebra, full working shown",
        "- Programming — history, syntax, examples across 20+ languages",
    ],
]

_CLOSERS = [
    "What do you want to build or learn about?",
    "What should we work on?",
    "Ask me anything or tell me what to build.",
    "What are you thinking?",
    "What's the question?",
    "Go ahead — what do you need?",
]

_SELF_DESC = [
    "No internet required — everything runs locally.",
    "Fully local. No cloud, no tracking.",
    "Everything processes on your device.",
    "Offline-first — always available, fully private.",
]

_SECTION_LABELS = [
    "**What I can do:**",
    "**Capabilities:**",
    "**Here's what I handle:**",
    "**What's available:**",
]


def forge_greeting(mode: str) -> str:
    if mode == "forge_instant":
        return random.choice([
            "Hey — **ForgeAI** here. Ask me anything or tell me what to build.",
            "**ForgeAI** ready. What do you need?",
            "Quick mode on — ask a question or request a build.",
        ])

    if mode == "forge_thinking":
        intro = random.choice(_GREETING_INTROS)
        caps = random.choice(_CAPABILITY_SETS)
        return (
            f"{intro}\n\n"
            f"**Thinking mode active** — I'll show my reasoning process and give thorough answers.\n\n"
            f"**What I can do:**\n" + "\n".join(caps) + "\n\n"
            f"{random.choice(_CLOSERS)}"
        )

    intro = random.choice(_GREETING_INTROS)
    caps = random.choice(_CAPABILITY_SETS)
    closer = random.choice(_CLOSERS)
    label = random.choice(_SECTION_LABELS)

    lines = [intro]

    if random.random() < 0.45:
        lines.append(f"\n*{random.choice(_SELF_DESC)}*")

    lines.append(f"\n\n{label}\n" + "\n".join(caps))
    lines.append(f"\n\n{closer}")

    return "".join(lines)


# =============================================================================
# INTENT ROUTING & DISPATCH
# =============================================================================

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
        if detected or "calc" in subject or "app" in subject:
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


def _is_heading_line(s: str) -> bool:
    if re.match(r'^#{1,4}\s', s):
        return True
    words = s.split()
    if len(words) <= 4 and not re.search(r'\d|is |are |was |were |have |has |can |do |does ', s.lower()):
        return True
    return False

def _extract_aspect(answer: str, aspect: str, *, exact: bool = False) -> str | None:
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
    if exact:
        pick = random.choice(matches) if len(matches) > 1 else matches[0]
        if len(matches) > 1 and random.random() < 0.3:
            second = random.choice([m for m in matches if m != pick] or matches)
            return f"{pick}  {second}"
        return pick
    intro = random.choice(_ASPECT_INTROS.get(aspect, [""]))
    chosen = random.sample(matches, min(2, len(matches)))
    return intro + "  ".join(chosen)

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
    (r"what is the (speed|distance|temperature|mass|weight|height|depth|age)", "speed"),
    (r"capital of", "definition"),
    (r"how deep", "distance"),
    (r"how tall", "size"),
    (r"how heavy", "size"),
    (r"how much does.{0,20}weigh", "size"),
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


_BROAD_QUESTION_MARKERS = (
    "tell me about", "tell me more", "explain", "describe", "overview of",
    "everything about", "learn about", "what can you tell", "go deeper",
    "more about", "all about", "talk about",
)

_ASPECT_QUESTION_LABELS = {
    "speed": "how fast something is",
    "size": "how big or heavy something is",
    "temperature": "how hot or cold something is",
    "distance": "how far something is",
    "count": "how many there are",
    "date": "when something happened or how old it is",
    "lifespan": "how long something lives or lasts",
    "inventor": "who created or discovered it",
    "composition": "what it is made of",
    "diet": "what it eats",
    "habitat": "where it lives",
    "predator": "what hunts it",
    "behavior": "how it behaves",
    "definition": "what it is",
}


def _is_broad_question(q: str) -> bool:
    return any(m in q for m in _BROAD_QUESTION_MARKERS)


def _is_specific_question(q: str) -> bool:
    """True when the user wants a precise fact, not a general overview."""
    if _is_broad_question(q) and not _detect_aspect(q):
        return False
    if _detect_aspect(q):
        return True
    if re.search(
        r"^(what is|what are|who is|who was|when was|when did|where is|where are|"
        r"which is|how many|how much|how fast|how far|how old|how long|how hot|"
        r"how big|how tall|how heavy|how deep|capital of|name of)\b",
        q,
    ):
        return True
    return bool(_QUESTION_STARTERS.match(q))


def _interpret_question(query: str) -> str:
    """Plain-English restatement of what the user is asking."""
    q = _normalize(query)
    aspect = _detect_aspect(q)
    subject = _extract_entity(query) or "this topic"
    if aspect and aspect in _ASPECT_QUESTION_LABELS:
        return f"You asked { _ASPECT_QUESTION_LABELS[aspect] } — specifically about **{subject}**."
    if re.search(r"^what is\b", q):
        return f"You asked what **{subject}** is."
    if re.search(r"^who (is|was)\b", q):
        return f"You asked who **{subject}** is."
    if re.search(r"^when\b", q):
        return f"You asked when **{subject}** happened or existed."
    if re.search(r"^where\b", q):
        return f"You asked where **{subject}** is or lives."
    if re.search(r"capital of", q):
        return f"You asked for the capital city — **{subject}**."
    return f"You asked a specific question about **{subject}**."


def _score_sentence_for_query(sent: str, q: str, kws: list[str], aspect: str | None) -> float:
    low = sent.lower()
    score = sum(2.0 for w in kws if w in low)
    if aspect and any(k in low for k in _ASPECT_KEYWORDS.get(aspect, [])):
        score += 8.0
    if re.search(r"\d", sent):
        score += 5.0 if aspect in ("speed", "count", "size", "distance", "temperature", "date", "lifespan") else 2.0
    if re.search(r"\*\*[^*]+\*\*", sent):
        score += 3.0
    if _is_heading_line(sent):
        score -= 20.0
    if len(sent) < 12:
        score -= 5.0
    if len(sent) > 280:
        score -= 2.0
    return score


def _extract_from_bullets(answer: str, q: str, kws: list[str]) -> str | None:
    """Pull the exact bullet/list line that answers the query."""
    best_score, best_line = 0.0, None
    for raw in answer.split("\n"):
        line = raw.strip()
        if not line or not (line.startswith("-") or line.startswith("*") or re.match(r"^\d+\.", line)):
            continue
        clean = re.sub(r'^[-*]\s*|\d+\.\s*', '', line)
        clean = re.sub(r'[*#>`_]+', '', clean).strip()
        if len(clean) < 8:
            continue
        score = _score_sentence_for_query(clean, q, kws, _detect_aspect(q))
        if score > best_score:
            best_score, best_line = score, clean
    return best_line if best_score >= 4.0 else None


def _extract_exact_answer(query: str, content: str) -> str | None:
    """
    Extract the precise fact that directly answers the query — no paraphrasing.
    """
    if not content or not content.strip():
        return None

    q = _normalize(query)
    aspect = _detect_aspect(q)
    kws = _query_keywords(q)

    # 1. Aspect-targeted sentence from prose
    if aspect:
        hit = _extract_aspect(content, aspect, exact=True)
        if hit and len(hit) >= 10:
            return hit.strip()

    # 2. Bullet / list line that matches the question
    if kws:
        bullet = _extract_from_bullets(content, q, kws)
        if bullet:
            return bullet

    # 3. Best-scoring sentence in the content
    if kws or aspect:
        raw_lines = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', content) if s.strip()]
        clean = [re.sub(r'[*#>`_\-]+', '', l).strip() for l in raw_lines]
        scored: list[tuple[float, str]] = []
        for sent in clean:
            if not sent or _is_heading_line(sent):
                continue
            sc = _score_sentence_for_query(sent, q, kws, aspect)
            if sc >= 4.0:
                scored.append((sc, sent))
        if scored:
            scored.sort(key=lambda x: -x[0])
            top_score = scored[0][0]
            pool = [s for sc, s in scored if sc >= top_score * 0.72]
            if len(pool) > 1:
                if random.random() < 0.35:
                    a, b = random.sample(pool, min(2, len(pool)))
                    return f"{a}  {b}"
                return random.choice(pool)
            top = scored[0][1]
            if scored[0][0] >= 8.0 and len(scored) > 1 and scored[1][0] >= 6.0 and random.random() < 0.45:
                return f"{top}  {scored[1][1]}"
            return top

    # 4. First bold value sentence (numeric / named answers)
    for para in content.split("\n\n"):
        p = para.strip()
        if p.startswith("```") or p.startswith("["):
            continue
        if re.search(r"\*\*[^*]{2,}\*\*", p):
            for sent in re.split(r"(?<=[.!?])\s+", _clean(p)):
                if len(sent) >= 15 and not _is_heading_line(sent):
                    if not kws or any(w in sent.lower() for w in kws):
                        return sent.strip()

    return None


def _one_support_line(content: str, query: str, exact: str) -> str | None:
    """One supporting detail that does not repeat the exact answer."""
    q = _normalize(query)
    kws = _query_keywords(q)
    exact_low = exact.lower()
    for sent in re.split(r"(?<=[.!?])\s+", _clean(content)):
        if len(sent) < 20 or sent.lower()[:40] in exact_low:
            continue
        if _is_heading_line(sent):
            continue
        if kws and not any(w in sent.lower() for w in kws):
            continue
        if sent.lower() not in exact_low:
            return sent.strip()
    return None


def _vary_exact_response(
    query: str,
    exact: str,
    mode: str,
    memory: dict | None = None,
    content: str = "",
) -> str:
    """Format a precise answer with randomized phrasing and structure each call."""
    exact = re.sub(r"\s+", " ", exact.strip())
    if not exact:
        return exact

    q = _normalize(query)
    aspect = _detect_aspect(q)
    plain = re.sub(r"\*\*([^*]+)\*\*", r"\1", exact)
    core = _maybe_rephrase(plain)

    if mode == "forge_instant":
        instant_styles = [
            lambda: core,
            lambda: random.choice(_ASPECT_INTROS.get(aspect, [""])) + core,
            lambda: random.choice(_EMPHASIS_PREFIXES) + (core[0].lower() + core[1:] if core else core),
            lambda: f"**{core}**",
        ]
        return random.choice(instant_styles)()

    parts: list[str] = []

    if mode == "forge_thinking":
        parts.append(
            "### Thinking Process\n"
            f"- **Understood:** {_interpret_question(query)}\n"
            f"- **Answer type:** precise fact (rewritten for clarity)\n"
            f"- **Result:**\n"
        )
        parts.append("---")
    elif memory and memory.get("continuing_thread") and memory.get("thread_confidence", 0) >= 55:
        preamble = _thread_preamble(memory)
        if preamble and random.random() < 0.65:
            parts.append(preamble)

    style = random.choice(["bold_lead", "prose", "opener", "woven", "qa_hook"])

    if style == "bold_lead":
        lead_templates = [
            f"**{core}**",
            f"The direct answer: **{core}**",
            f"**{random.choice(_ASPECT_INTROS.get(aspect, ['']))}{core}**",
            f"Short answer — **{core}**",
        ]
        parts.append(random.choice(lead_templates).replace("****", "**"))
    elif style == "prose":
        intro = random.choice(_ASPECT_INTROS.get(aspect, [""]))
        sentence = f"{intro}{core[0].upper()}{core[1:]}" if intro and core else core
        parts.append(sentence)
    elif style == "opener":
        opener = _pick_opener(query)
        if opener:
            parts.append(opener)
        parts.append(core if random.random() < 0.4 else f"**{core}**")
    elif style == "woven":
        parts.append(_pick_opener(query) if random.random() < 0.7 else "")
        parts.append(core)
        if random.random() < 0.5:
            parts.append(_pick_closer())
    else:
        hooks = [
            f"On that specific point: **{core}**",
            f"To answer your question directly — {core}",
            f"Here's the key fact: **{core}**",
            f"**{core}**",
        ]
        parts.append(random.choice(hooks))

    if style not in ("woven",) and content and random.random() < 0.42:
        support = _one_support_line(content, query, exact)
        if support:
            wrappers = [
                f"*Also worth noting:* {support}",
                f"For context — {support}",
                f"That sits alongside this: {support}",
                support,
            ]
            parts.append(random.choice(wrappers))

    if style != "woven" and random.random() < 0.38:
        closer = _pick_closer()
        if closer:
            parts.append(closer)

    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def _format_exact_response(
    query: str,
    exact: str,
    mode: str,
    memory: dict | None = None,
    content: str = "",
) -> str:
    """Backward-compatible alias — always varies the presentation."""
    return _vary_exact_response(query, exact, mode, memory, content)


def _try_extract_fact(answer: str, q: str) -> str | None:
    """Try to pull just the specific fact from a longer answer."""
    exact = _extract_exact_answer(q, answer) if _is_specific_question(q) else None
    if exact:
        return exact

    aspect = _detect_aspect(q)
    if aspect:
        result = _extract_aspect(answer, aspect, exact=True)
        if result:
            return result

    if not _QUESTION_STARTERS.match(q):
        return None
    kws = _query_keywords(q)
    if not kws:
        return None
    raw_lines = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', answer) if s.strip()]
    clean = [re.sub(r'[*#>`_\-]+', '', l).strip() for l in raw_lines]
    scored = []
    for sent in clean:
        if _is_heading_line(sent):
            continue
        sc = _score_sentence_for_query(sent, q, kws, aspect)
        if sc >= 4.0:
            scored.append((sc, sent))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]

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

def _dispatch_project(query: str, kind: str = "auto", mode: str = "forge_code") -> dict:
    """Generate a multi-file project and return a response dict."""
    from services.code_generater import parse_build_request
    spec = parse_build_request(query)
    project, researched = generate_anything_with_meta(query)
    verb = "autonomously coded" if spec.use_autonomous else ("compiled" if project.kind == "game" else "built")
    action = "Play Game" if project.kind == "game" else "Run Project"
    n = len(project.files)
    file_list = ", ".join(f"`{f.name}`" for f in project.files)
    research_note = " I looked up context on Google to understand your request." if researched else ""

    if mode == "forge_thinking":
        feat_line = f"- **Features detected:** {', '.join(spec.features[:6])}\n" if spec.features else ""
        intro = (
            f"### Thinking Process\n"
            f"- **Intent:** {'Autonomous game coding' if project.kind == 'game' else 'Autonomous app generation'}\n"
            f"- **Approach:** Original code written from scratch — no templates copied\n"
            f"- **Parsed:** kind={spec.kind}, genre={spec.genre or 'n/a'}, app={spec.app_type or 'n/a'}\n"
            f"{feat_line}"
            + (f"- **Web research:** gathered context for this custom build\n" if researched else "")
            + f"- **Output:** {n} file{'s' if n != 1 else ''} — {file_list}\n\n"
            f"---\n\n"
            f"I {verb} **{project.title}** with {n} production-ready file{'s' if n != 1 else ''}.{research_note} "
            f"Browse the file tree below, then hit **\"{action}\"** to launch it live."
        )
    elif mode == "forge_instant":
        intro = (
            f"**{project.title}** ready — {n} file{'s' if n != 1 else ''}. "
            f"Hit **\"{action}\"** to launch."
        )
    else:
        intro = (
            f"I {verb} **{project.title}** from scratch — {n} original file{'s' if n != 1 else ''} ({file_list}).{research_note} "
            f"No templates were copied; the logic was composed for your exact request. "
            f"Browse the files below, then hit **\"{action}\"** to launch."
        )
    return {
        "text": intro,
        "project_files": [{"name": f.name, "content": f.content, "language": f.language} for f in project.files],
    }

# Keep these for backward compat — now all go through _dispatch_project
def _dispatch_game(query: str, q: str, mode: str) -> dict:
    return _dispatch_project(query, "game", mode)

def _dispatch_app(query: str, mode: str) -> dict:
    return _dispatch_project(query, "app", mode)

def _dispatch_dynamic(query: str, mode: str) -> dict:
    return _dispatch_project(query, "app", mode)

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

_TOPIC_SHIFT_MARKERS = (
    "anyway", "actually", "never mind", "nevermind", "forget that", "forget it",
    "new question", "different question", "change topic", "switching to", "switch to",
    "instead", "on another note", "by the way", "btw", "separately",
    "something else", "another thing", "moving on", "let me ask about",
    "unrelated", "off topic", "different subject",
)

_SHORT_FOLLOWUP_RE = re.compile(
    r"^(why|how|when|where|who|what|really|ok|okay|and|so|then|right|true|yes|no)\??$",
    re.I,
)


def _token_overlap(a: str, b: str) -> float:
    """Share of meaningful tokens between two strings (0–1)."""
    ta = set(re.findall(r"[a-z0-9]{3,}", a)) - _STOP_WORDS
    tb = set(re.findall(r"[a-z0-9]{3,}", b)) - _STOP_WORDS
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def _infer_topic_intent(q: str) -> str | None:
    """Best-guess intent for a topic anchor query."""
    scores = {
        "programming": score_programming(q),
        "math": _score_math(q),
        "space": _score_space(q),
        "earth": _score_earth(q),
        "science": _score_science(q),
        "history": _score_history(q),
        "animals": _score_animals(q),
        "build_game": _score_build_game(q),
        "build_app": _score_build_app(q),
        "knowledge": _score_knowledge(q),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] >= 35 else None


def scan_chat_context(history: list, query: str) -> dict:
    """
    Quick full-history scan before responding — is the user still on the last topic?
    """
    user_msgs = _get_all_user_msgs(history)
    ai_texts: list[str] = []
    for msg in history:
        if msg.get("role") == "assistant":
            text = (msg.get("text") or msg.get("content") or "").strip()
            if text:
                ai_texts.append(text)

    q = _normalize(query)
    result: dict = {
        "continuing_thread": False,
        "thread_confidence": 0,
        "topic_shift": False,
        "last_user_query": None,
        "last_assistant_text": ai_texts[-1] if ai_texts else None,
        "thread_intent": None,
    }

    if len(user_msgs) < 2:
        return result

    # Current message is usually last in history when the API receives it
    prev_msgs = user_msgs[:-1] if user_msgs[-1].strip() == query.strip() else user_msgs
    if not prev_msgs:
        return result

    last_user = prev_msgs[-1]
    last_ai = ai_texts[-1] if ai_texts else ""
    result["last_user_query"] = last_user

    if any(marker in q for marker in _TOPIC_SHIFT_MARKERS):
        result["topic_shift"] = True
        return result

    overlap_user = _token_overlap(q, last_user)
    overlap_ai = _token_overlap(q, last_ai)
    overlap_thread = _token_overlap(q, _normalize(last_user + " " + last_ai[:500]))
    best_overlap = max(overlap_user, overlap_ai, overlap_thread)

    is_followup = _is_followup_query(q)
    content_words = [w for w in q.split() if w not in _STOP_WORDS]

    if is_followup:
        result["continuing_thread"] = True
        result["thread_confidence"] = 92
    elif _SHORT_FOLLOWUP_RE.match(q.strip()):
        result["continuing_thread"] = True
        result["thread_confidence"] = 88
    elif len(content_words) <= 5 and _PRONOUN_RE.search(q):
        result["continuing_thread"] = True
        result["thread_confidence"] = 80
    elif _detect_aspect(q) and best_overlap >= 0.12:
        result["continuing_thread"] = True
        result["thread_confidence"] = 72
    elif best_overlap >= 0.4:
        result["continuing_thread"] = True
        result["thread_confidence"] = int(55 + best_overlap * 45)
    elif len(content_words) <= 3 and best_overlap >= 0.15:
        result["continuing_thread"] = True
        result["thread_confidence"] = 65

    if result["continuing_thread"]:
        anchor = _normalize(last_user)
        for msg in reversed(prev_msgs):
            if not _is_followup_query(_normalize(msg)):
                anchor = _normalize(msg)
                break
        result["thread_intent"] = _infer_topic_intent(anchor)

    return result


def _is_followup_query(q: str) -> bool:
    """Return True if q is clearly a follow-up with no new subject."""
    if q in _FOLLOWUP_EXACT:
        return True
    if any(q.startswith(p) for p in _FOLLOWUP_STARTS):
        return True
    if _SHORT_FOLLOWUP_RE.match(q.strip()):
        return True
    if re.match(r"^(why|how|when|where|who)\s+(is|are|was|were|do|does|did)\s+(that|it|this|they)\b", q):
        return True
    if re.match(r"^(what|how)\s+about\s+(that|it|this|them)\b", q):
        return True
    # Short pronoun-heavy queries
    words = [w for w in q.split() if w not in _STOP_WORDS]
    if len(words) <= 3 and _PRONOUN_RE.search(q):
        return True
    if len(words) <= 2 and q.endswith("?"):
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
        "thread_intent": _infer_topic_intent(_normalize(active_topic)),
    }


def _resolve_context(query: str, q: str, history: list, scan: dict | None = None) -> tuple[str, str, dict]:
    """
    Rewrite a follow-up query using full conversation memory.
    Returns (resolved_query, normalized_q, memory_dict).
    """
    scan = scan or scan_chat_context(history, query)
    mem = build_conversation_memory(history)
    mem.update(scan)
    active_topic = mem.get("active_topic")

    if scan.get("topic_shift"):
        return query, q, mem

    if not active_topic:
        return query, q, mem

    entity = mem.get("active_entity") or ""
    last_ai = scan.get("last_assistant_text") or ""
    if not entity and last_ai:
        entity = _extract_entity(last_ai[:300]) or entity

    continuing = scan.get("continuing_thread") and scan.get("thread_confidence", 0) >= 60

    # 1. Pure follow-up → expand into full topic question
    if q in _FOLLOWUP_EXACT or (continuing and _is_followup_query(q)):
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
    if len(words) <= 5 and _PRONOUN_RE.search(q) and entity:
        resolved = _PRONOUN_RE.sub(entity, query)
        return resolved, _normalize(resolved), mem

    # 4. Continuing thread: short aspect question without explicit subject
    if continuing and _detect_aspect(q) and entity and entity not in q:
        combined = f"{query.strip()} {entity}"
        return combined, _normalize(combined), mem

    # 5. New question on the same entity but different angle — preserve as-is
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


def _forge_or_exact(
    content: str,
    query: str,
    q: str,
    intent: str,
    *,
    depth: int = 0,
    mode: str = "forge_code",
    memory: dict | None = None,
) -> str:
    """Run the full forge pipeline — facts stay accurate, wording varies every call."""
    return forge(content, query, intent, depth=depth, mode=mode, memory=memory)


def _build_comprehensive_response(topic: str, entity: str, memory: dict) -> str | None:
    """Build a rich multi-part response by pulling related KB entries."""
    q_topic = _normalize(topic)
    covered = memory.get("covered_aspects", [])

    primary = _kb_fact_lookup(q_topic)
    primary_key = None
    if not primary:
        for key, answer in GENERAL_KNOWLEDGE.items():
            if entity and entity.lower() in key:
                primary, primary_key = answer, key
                break
        if not primary:
            return None

    related = _related_kb_entries(entity or topic, exclude_keys=[primary_key] if primary_key else [])
    seen_tokens = set(re.findall(r"[a-z]{4,}", primary.lower()))
    unique_related = []
    for r in related:
        r_tokens = set(re.findall(r"[a-z]{4,}", r.lower()))
        overlap = len(seen_tokens & r_tokens) / max(len(r_tokens), 1)
        if overlap < 0.65 and r != primary:
            unique_related.append(r)

    if not unique_related and memory.get("thread_depth", 0) < 2:
        return None

    sections = [primary] + unique_related[:3]
    combined = "\n\n".join(sections)
    uncovered = [a for a in ["speed", "size", "diet", "habitat", "behavior", "lifespan", "composition", "date"]
                 if a not in covered]
    if uncovered:
        combined += f"\n\n*Still to explore on this topic: {', '.join(uncovered[:3])}.*"
    return combined


# --- MAIN ENTRY POINT ---

def _kb_fact_lookup(q: str, entity: str = "") -> str | None:
    """Return a KB answer for factual questions."""
    ent = (entity or "").lower().strip()

    # Pass 0: entity-aware key match from conversation context
    if ent and len(ent) >= 3:
        best_len, best_answer = 0, None
        for key, answer in GENERAL_KNOWLEDGE.items():
            if ent in key or ent in answer.lower()[:200]:
                key_hits = sum(1 for w in ent.split() if w in key)
                q_hits = sum(1 for w in q.split() if len(w) > 3 and w in key)
                if key_hits + q_hits >= 1 and len(key) > best_len:
                    best_len, best_answer = len(key), answer
        if best_answer and best_len >= 4:
            return best_answer

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
    return best_answer


def _comprehend_query(query: str, q: str, memory: dict | None = None) -> dict:
    """
    Deep parse of what the user is asking — used before routing and answering.
    """
    memory = memory or {}
    entity = memory.get("active_entity") or _extract_entity(query) or ""
    aspect = _detect_aspect(q)
    kws = _query_keywords(q)

    build_game = _score_build_game(q)
    build_app = _score_build_app(q)
    is_build = _has_build_verb(q) or build_game >= 60 or build_app >= 60

    intent_hint = None
    if is_build:
        intent_hint = "build_game" if build_game >= build_app else "build_app"
    elif aspect:
        intent_hint = {"speed": "science", "distance": "space", "composition": "science",
                       "date": "history", "inventor": "history", "habitat": "earth",
                       "diet": "animals", "count": "knowledge"}.get(aspect, "knowledge")
    elif kws:
        intent_hint = memory.get("thread_intent")

    return {
        "raw": query,
        "normalized": q,
        "entity": entity,
        "aspect": aspect,
        "keywords": kws,
        "is_specific": _is_specific_question(q),
        "is_broad": _is_broad_question(q),
        "is_build": is_build,
        "build_game_score": build_game,
        "build_app_score": build_app,
        "intent_hint": intent_hint,
        "continuing": memory.get("continuing_thread", False),
        "question_read": _interpret_question(query) if _is_specific_question(q) else "",
    }


# =============================================================================
# THINKING ENGINE — deliberate reasoning before every response
# =============================================================================

@dataclass
class ThinkingTrace:
    """Structured record of how ForgeAI reasoned about a question before answering."""
    query: str
    interpreted: str
    question_type: str
    complexity: str
    entity: str
    aspect: str | None
    source_plan: str
    confidence: int
    steps: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    memory_notes: list[str] = field(default_factory=list)
    strategy: str = ""
    intent_guess: str = ""

    def to_markdown(self, compact: bool = False) -> str:
        q_short = self.query[:90] + ("…" if len(self.query) > 90 else "")
        conf_label = _confidence_label(self.confidence)
        if compact:
            obs = random.choice(self.observations) if self.observations else ""
            step = random.choice(self.steps) if self.steps else ""
            lines = [
                "### Thinking",
                f"- **Read:** {self.interpreted}",
                f"- **Plan:** {self.source_plan} ({conf_label})",
            ]
            if step:
                lines.append(f"- **Next:** {step}")
            if obs:
                lines.append(f"- *{obs}*")
            return "\n".join(lines)

        lines = [
            "### Thinking Process",
            f"- **Original question:** \"{q_short}\"",
            f"- **How I read it:** {self.interpreted}",
            f"- **Question type:** {self.question_type} · **Complexity:** {self.complexity}",
        ]
        if self.entity:
            lines.append(f"- **Subject / entity:** {self.entity}")
        if self.aspect:
            lines.append(f"- **Aspect requested:** {self.aspect}")
        if self.memory_notes:
            lines.append(f"- **Conversation context:** {'; '.join(self.memory_notes[:3])}")
        lines += [
            f"- **Information source:** {self.source_plan}",
            f"- **Confidence:** {conf_label} ({self.confidence}%)",
            f"- **Answer strategy:** {self.strategy}",
            "- **Reasoning steps:**",
        ]
        for i, step in enumerate(self.steps, 1):
            lines.append(f"  {i}. {step}")
        if self.observations:
            lines.append("- **Internal notes:**")
            for obs in self.observations[:4]:
                lines.append(f"  - *{obs}*")
        return "\n".join(lines)


_QUESTION_TYPE_PATTERNS: list[tuple[str, str]] = [
    (r"^(how fast|how quick|how speedy)", "factual — speed measurement"),
    (r"^(how many|how much)", "factual — quantity"),
    (r"^(how big|how large|how tall|how heavy|how deep|how far)", "factual — scale / distance"),
    (r"^(what is|what are|what's)", "definitional — what something is"),
    (r"^(who is|who was|who made|who invented)", "biographical / attribution"),
    (r"^(when did|when was|what year)", "temporal — dates and timelines"),
    (r"^(where is|where are|where do|where does)", "locational — place or habitat"),
    (r"^(why do|why does|why is|why are)", "causal — reasons and mechanisms"),
    (r"^(can you|could you|please)", "request — action or explanation"),
    (r"^(make|build|create|code|write|generate)", "build request — code / project"),
    (r"^(solve|calculate|compute|evaluate|simplify|integrate|differentiate)", "mathematical computation"),
    (r"^(tell me about|explain|describe|overview)", "exploratory — broad overview"),
    (r"^(compare|difference between|vs\b|versus)", "comparative — contrast two things"),
    (r"^(is it true|is it possible|can a|does a)", "verification — yes/no or possibility"),
]

_THINKING_OBSERVATIONS: dict[str, list[str]] = {
    "specific": [
        "The user wants a precise fact, not a lecture — lead with the answer.",
        "This is a narrow question; I should avoid unrelated tangents.",
        "A single strong sentence may be enough if the fact is clear.",
        "I'll extract the exact figure or date before elaborating.",
    ],
    "broad": [
        "This is open-ended — I should cover several angles without overwhelming.",
        "A layered answer works better than a single fact dump here.",
        "I'll prioritize the most surprising or useful facts first.",
        "The user likely wants breadth; I'll weave connections between facts.",
    ],
    "followup": [
        "This continues an earlier thread — I must stay on the same subject.",
        "Context from prior messages should shape what I emphasize next.",
        "I should not re-introduce basics already covered in this conversation.",
        "Picking an uncovered aspect will feel more helpful than repeating.",
    ],
    "build": [
        "This is a creation request — templates and synthesis both need consideration.",
        "I should parse features, genre, and complexity before generating files.",
        "The output must be runnable in-browser with clean file separation.",
        "If the request is unusual, a quick web lookup may improve the build.",
    ],
    "math": [
        "Symbolic math needs step-by-step working, not just a final number.",
        "I'll check for calculus, trig, or algebra patterns before solving.",
        "Showing the method matters as much as the result here.",
    ],
    "unknown": [
        "This may not be in the local knowledge base — I'll plan a fallback path.",
        "Low confidence locally — web search is a reasonable backup.",
        "I should be honest if coverage is thin rather than inventing details.",
    ],
}

_THINKING_STEP_POOL: dict[str, list[str]] = {
    "parse": [
        "Parse the question literally — identify subject, aspect, and desired answer shape",
        "Strip filler words and isolate the core information need",
        "Determine whether this is specific, broad, or a follow-up",
        "Read the question as a human would — what are they really trying to learn?",
    ],
    "context": [
        "Scan the full conversation for topic continuity and unresolved references",
        "Check if pronouns like \"it\" or \"they\" refer to an earlier subject",
        "Note which aspects were already discussed so I don't repeat myself",
        "Anchor follow-ups to the active thread entity from memory",
    ],
    "source": [
        "Search the knowledge base for the longest matching key",
        "Route to the specialised engine (space, earth, science, history, animals)",
        "Evaluate whether local data is sufficient or web lookup is needed",
        "Pick compile vs synthesize path for build requests",
    ],
    "compose": [
        "Lead with a direct answer, then add supporting context",
        "Vary sentence structure so the reply feels natural, not canned",
        "Select 2–4 fact atoms that best match the question focus",
        "Tie the conclusion back to the exact wording of the question",
    ],
    "verify": [
        "Sanity-check numbers and units before stating them",
        "Ensure I'm answering the question asked, not a nearby one",
        "Confirm the entity matches conversation context on follow-ups",
        "If confidence is low, prefer lookup or a clear uncertainty note",
    ],
}


def _classify_question_type(q: str) -> str:
    for pattern, label in _QUESTION_TYPE_PATTERNS:
        if re.search(pattern, q):
            return label
    if _is_specific_question(q):
        return "factual — specific detail"
    if _is_broad_question(q):
        return "exploratory — overview"
    return "general — open query"


def _assess_complexity(query: str, q: str, memory: dict) -> str:
    score = 0
    if len(q.split()) > 12:
        score += 2
    if _detect_aspect(q):
        score += 1
    if memory.get("continuing_thread"):
        score += 1
    if _has_build_verb(q):
        score += 3
    if any(w in q for w in ("compare", "versus", "difference", "explain", "everything")):
        score += 2
    if _is_broad_question(q):
        score += 2
    if score >= 5:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _analyze_literal_meaning(query: str, q: str, comprehend: dict) -> str:
    if comprehend.get("question_read"):
        return comprehend["question_read"]
    aspect = comprehend.get("aspect") or _detect_aspect(q)
    entity = comprehend.get("entity") or _extract_entity(query) or "the topic"
    qtype = _classify_question_type(q)
    if aspect:
        aspect_labels = {
            "speed": f"a question about how fast **{entity}** is",
            "size": f"a question about the size or scale of **{entity}**",
            "diet": f"a question about what **{entity}** eats",
            "habitat": f"a question about where **{entity}** lives",
            "date": f"a question about when **{entity}** happened or existed",
            "count": f"a question about how many / how much regarding **{entity}**",
            "inventor": f"a question about who created or discovered **{entity}**",
            "composition": f"a question about what **{entity}** is made of",
        }
        return f"The user is asking {aspect_labels.get(aspect, f'about **{entity}** ({aspect})')}."
    if comprehend.get("is_build"):
        return f"The user wants me to **build or generate** something: \"{query[:70]}\"."
    if "mathematical" in qtype:
        return f"The user wants a **math solution** for: \"{query[:70]}\"."
    if "exploratory" in qtype:
        return f"The user wants a **broad overview** of **{entity}**."
    return f"The user is asking ({qtype}): \"{query[:80]}{'…' if len(query) > 80 else ''}\"."


def _reason_about_conversation(memory: dict, history: list) -> list[str]:
    notes: list[str] = []
    if memory.get("continuing_thread"):
        conf = memory.get("thread_confidence", 0)
        topic = (memory.get("active_topic") or "")[:60]
        notes.append(f"continuing thread on \"{topic}\" (confidence {conf}%)")
    if memory.get("topic_shift"):
        notes.append("user signaled a topic shift — treat as fresh subject")
    covered = memory.get("covered_aspects") or []
    if covered:
        notes.append(f"aspects already covered: {', '.join(covered[:5])}")
    depth = memory.get("thread_depth", 0)
    if depth >= 2:
        notes.append(f"{depth} prior turns on this topic — go deeper, don't repeat intro")
    convo = memory.get("conversation") or {}
    entities = convo.get("all_entities") or []
    if entities:
        notes.append(f"entities in session: {', '.join(entities[:4])}")
    topics = convo.get("all_topics") or []
    if len(topics) > 1:
        notes.append(f"{len(topics)} distinct topics this session")
    if not notes and not history:
        notes.append("first message in conversation — no prior context")
    return notes


def _plan_information_source(
    comprehend: dict,
    q: str,
    memory: dict,
    workspace: str,
) -> tuple[str, int]:
    """Return (source_description, confidence 0-100)."""
    entity = comprehend.get("entity") or memory.get("active_entity") or ""
    if comprehend.get("is_build") or _has_build_verb(q):
        return "code generator — compile / synthesize project files", 85
    if _score_math(q) >= 50:
        return "math engine — symbolic computation", 90
    kb = _kb_fact_lookup(q, entity=entity)
    if kb:
        return "local knowledge base — direct key match", 88
    best_engine = None
    engine_scores = {
        "space": _score_space(q),
        "earth": _score_earth(q),
        "science": _score_science(q),
        "history": _score_history(q),
        "animals": _score_animals(q),
        "programming": score_programming(q),
    }
    top_engine = max(engine_scores, key=engine_scores.get)
    top_score = engine_scores[top_engine]
    if top_score >= 55:
        labels = {
            "space": "space engine — astronomy facts",
            "earth": "earth engine — geology / geography",
            "science": "science engine — physics / chemistry / biology",
            "history": "history engine — events and people",
            "animals": "animals engine — species facts",
            "programming": "programming KB — languages and patterns",
        }
        return labels[top_engine], min(95, top_score + 10)
    if _score_knowledge(q) >= 40:
        return "general knowledge base — token / aspect search", 70
    if workspace == "code" and _has_build_verb(q):
        return "code workspace — project generation", 80
    return "web lookup — Google / DuckDuckGo fallback", 45


def _plan_answer_strategy(comprehend: dict, complexity: str, source: str) -> str:
    if comprehend.get("is_build"):
        options = [
            "Parse build spec → route to game or app compiler → split HTML into files",
            "Detect genre and features → compile template or synthesize custom logic",
            "Enrich query with detected theme/features → generate multi-file project",
        ]
        return random.choice(options)
    if comprehend.get("is_specific"):
        options = [
            "Extract exact fact → NLG rewrite → varied natural phrasing",
            "Pull best-matching sentence → lead with answer → optional context line",
            "Aspect-targeted extraction → bold lead fact → brief supporting detail",
        ]
        return random.choice(options)
    if comprehend.get("is_broad") or complexity == "high":
        options = [
            "Multi-atom NLG compose → structural variation → key takeaway",
            "Pull related KB entries → comprehensive thread-aware response",
            "Layer facts from general to specific → varied connectors and closer",
        ]
        return random.choice(options)
    if "web lookup" in source:
        return "Search web → summarize snippets → forge into readable answer"
    return random.choice([
        "Knowledge lookup → forge pipeline → varied structure",
        "Engine dispatch → fact extraction → natural language generation",
        "Score intents → best engine → compose with thread context",
    ])


def _confidence_label(score: int) -> str:
    if score >= 85:
        return "high"
    if score >= 65:
        return "moderate"
    if score >= 45:
        return "low"
    return "very low"


def _pick_thinking_observations(
    comprehend: dict,
    complexity: str,
    confidence: int,
    memory: dict,
) -> list[str]:
    pool: list[str] = []
    if comprehend.get("is_specific"):
        pool.extend(_THINKING_OBSERVATIONS["specific"])
    if comprehend.get("is_broad"):
        pool.extend(_THINKING_OBSERVATIONS["broad"])
    if memory.get("continuing_thread"):
        pool.extend(_THINKING_OBSERVATIONS["followup"])
    if comprehend.get("is_build"):
        pool.extend(_THINKING_OBSERVATIONS["build"])
    if _score_math(comprehend.get("normalized", "")) >= 40:
        pool.extend(_THINKING_OBSERVATIONS["math"])
    if confidence < 55:
        pool.extend(_THINKING_OBSERVATIONS["unknown"])
    if not pool:
        pool = _THINKING_OBSERVATIONS["unknown"]
    return random.sample(pool, min(3, len(pool)))


def _build_thinking_steps(
    comprehend: dict,
    memory: dict,
    source: str,
    strategy: str,
) -> list[str]:
    steps: list[str] = []
    steps.append(random.choice(_THINKING_STEP_POOL["parse"]))
    if memory.get("continuing_thread") or (memory.get("conversation") or {}).get("turn_count", 0) > 2:
        steps.append(random.choice(_THINKING_STEP_POOL["context"]))
    steps.append(random.choice(_THINKING_STEP_POOL["source"]) + f" → **{source.split('—')[0].strip()}**")
    steps.append(random.choice(_THINKING_STEP_POOL["compose"]))
    if comprehend.get("is_specific") or comprehend.get("is_broad"):
        steps.append(random.choice(_THINKING_STEP_POOL["verify"]))
    if comprehend.get("is_build"):
        steps.append("Generate production-ready files and verify HTML/CSS/JS split")
    return steps


def _run_thinking_pipeline(
    query: str,
    q: str,
    memory: dict,
    comprehend: dict,
    history: list,
    workspace: str = "chat",
) -> ThinkingTrace:
    """
    Think through the question before any routing or answering.
    Called at the start of generate_response for every non-quick request.
    """
    interpreted = _analyze_literal_meaning(query, q, comprehend)
    question_type = _classify_question_type(q)
    complexity = _assess_complexity(query, q, memory)
    memory_notes = _reason_about_conversation(memory, history)
    source, confidence = _plan_information_source(comprehend, q, memory, workspace)
    strategy = _plan_answer_strategy(comprehend, complexity, source)
    steps = _build_thinking_steps(comprehend, memory, source, strategy)
    observations = _pick_thinking_observations(comprehend, complexity, confidence, memory)

    return ThinkingTrace(
        query=query,
        interpreted=interpreted,
        question_type=question_type,
        complexity=complexity,
        entity=comprehend.get("entity") or memory.get("active_entity") or "",
        aspect=comprehend.get("aspect"),
        source_plan=source,
        confidence=confidence,
        steps=steps,
        observations=observations,
        memory_notes=memory_notes,
        strategy=strategy,
        intent_guess=comprehend.get("intent_hint") or "",
    )


def _should_attach_thinking(mode: str) -> bool:
    return mode in ("forge_thinking", "forge_code")


def _attach_thinking(result: str | dict, trace: ThinkingTrace | None, mode: str) -> str | dict:
    """Prepend the thinking trace before the final answer."""
    if not trace or not _should_attach_thinking(mode):
        return result
    compact = mode == "forge_code"
    block = trace.to_markdown(compact=compact)

    if isinstance(result, dict):
        text = result.get("text", "")
        if "### Thinking" in text:
            return result
        return {**result, "text": f"{block}\n\n---\n\n{text}"}

    if "### Thinking" in result:
        return result
    return f"{block}\n\n---\n\n{result}"


# =============================================================================
# FULL CONVERSATION READER — re-read entire chat before responding
# =============================================================================

def _parse_history_turns(history: list) -> list[dict]:
    """Parse every message in the conversation in order."""
    turns: list[dict] = []
    for i, msg in enumerate(history):
        role = msg.get("role", "")
        text = (msg.get("text") or msg.get("content") or "").strip()
        if text:
            turns.append({"index": i, "role": role, "text": text})
    return turns


def read_full_conversation(history: list, current_query: str = "") -> dict:
    """
    Re-read the entire conversation from the first message to the latest.
    Used before every response so ForgeAI has full session awareness.
    """
    turns = _parse_history_turns(history)
    user_turns = [t for t in turns if t["role"] == "user"]
    ai_turns = [t for t in turns if t["role"] == "assistant"]

    entities_seen: list[str] = []
    topics: list[str] = []
    keywords_counter: dict[str, int] = {}
    aspects_seen: list[str] = []

    for t in user_turns:
        norm = _normalize(t["text"])
        if not _is_followup_query(norm):
            topics.append(t["text"][:80])
            ent = _extract_entity(t["text"])
            if ent:
                entities_seen.append(ent)
        for w in _query_keywords(norm):
            keywords_counter[w] = keywords_counter.get(w, 0) + 1
        asp = _detect_aspect(norm)
        if asp and asp not in aspects_seen:
            aspects_seen.append(asp)

    recent = turns[-14:] if len(turns) > 14 else turns
    transcript: list[str] = []
    for t in recent:
        label = "User" if t["role"] == "user" else "ForgeAI"
        excerpt = t["text"][:180].replace("\n", " ")
        suffix = "…" if len(t["text"]) > 180 else ""
        transcript.append(f"- **{label}:** {excerpt}{suffix}")

    top_keywords = sorted(keywords_counter, key=keywords_counter.get, reverse=True)[:10]

    summary_parts: list[str] = []
    if topics:
        summary_parts.append(f"Topics: {', '.join(topics[:4])}")
    if entities_seen:
        summary_parts.append(f"Subjects: {', '.join(dict.fromkeys(entities_seen)[:5])}")
    summary_parts.append(f"{len(turns)} messages ({len(user_turns)} from user)")

    return {
        "turn_count": len(turns),
        "user_turn_count": len(user_turns),
        "ai_turn_count": len(ai_turns),
        "transcript": transcript,
        "all_entities": list(dict.fromkeys(entities_seen)),
        "all_topics": topics,
        "top_keywords": top_keywords,
        "aspects_discussed": aspects_seen,
        "first_user_message": user_turns[0]["text"] if user_turns else None,
        "last_user_message": user_turns[-1]["text"] if user_turns else None,
        "conversation_summary": ". ".join(summary_parts),
    }


def _enrich_memory_from_conversation(memory: dict, convo: dict) -> dict:
    """Merge full-conversation digest into the working memory dict."""
    memory["conversation"] = convo
    if not memory.get("active_entity") and convo.get("all_entities"):
        memory["active_entity"] = convo["all_entities"][-1]
    if not memory.get("active_topic") and convo.get("all_topics"):
        memory["active_topic"] = convo["all_topics"][-1]
    for asp in convo.get("aspects_discussed") or []:
        if asp not in memory.get("covered_aspects", []):
            memory.setdefault("covered_aspects", []).append(asp)
    return memory


# =============================================================================
# WEB LOOKUP SUMMARIZER — summarize Google / DuckDuckGo results
# =============================================================================

_WEB_SUMMARY_INTROS = [
    "I searched the web because this wasn't in my local knowledge base. Here's what I found:",
    "This wasn't covered locally, so I looked it up online. Summary:",
    "I pulled this from a web search — here's the distilled answer:",
    "After checking Google and DuckDuckGo, here's a concise summary:",
    "Web search results, summarized for you:",
]

_WEB_SUMMARY_CLOSERS = [
    "That's the gist from online sources — let me know if you want more detail.",
    "Source was the open web; accuracy depends on the pages indexed.",
    "I can dig deeper on any part of this if you want.",
    "",
]


def _summarize_web_heuristic(text: str, query: str) -> str:
    """Fallback summarizer when NLG rewrite is unavailable."""
    plain = re.sub(r"[*_#`\[\]]", "", text)
    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", plain)
        if len(s.strip()) > 25
    ]
    seen: set[str] = set()
    unique: list[str] = []
    for s in sentences:
        key = s.lower()[:50]
        if key not in seen:
            seen.add(key)
            unique.append(s)
    kws = _query_keywords(_normalize(query))
    if kws:
        scored = sorted(
            unique,
            key=lambda s: sum(1 for w in kws if w in s.lower()),
            reverse=True,
        )
        unique = scored
    picks = unique[:4]
    if not picks:
        return plain[:400]
    if len(picks) == 1:
        return picks[0]
    return "**Key points:**\n\n" + "\n".join(f"- {p}" for p in picks)


def _summarize_web_result(
    query: str,
    raw: str,
    mode: str = "forge_code",
    memory: dict | None = None,
) -> str:
    """Turn raw search snippets into a readable summarized answer."""
    if not raw or raw.startswith("I don't have"):
        return raw

    plain = re.sub(r"^#+\s*Web Search Result\s*\n*", "", raw, flags=re.I)
    plain = re.sub(r"^#+\s*", "", plain, flags=re.MULTILINE)
    plain = re.sub(r"\*Source:[^*]+\*", "", plain)
    plain = plain.strip()
    if not plain:
        return raw

    summary_body = plain
    try:
        nlg = generate_from_content(
            f"Web search results for \"{query}\":\n\n{plain[:1200]}",
            query,
            max_atoms=3,
            elaborate=mode == "forge_thinking",
            memory=memory,
        )
        if nlg and len(nlg) >= 30:
            summary_body = vary_structure(nlg, query)
    except Exception:
        summary_body = _summarize_web_heuristic(plain, query)

    intro = random.choice(_WEB_SUMMARY_INTROS)
    closer = random.choice(_WEB_SUMMARY_CLOSERS)
    parts = [intro, "", summary_body]
    if closer:
        parts += ["", closer]
    return "\n".join(parts)


def _web_lookup_summarized(
    query: str,
    mode: str = "forge_code",
    memory: dict | None = None,
) -> str:
    """Look up the web and return a summarized answer."""
    raw = web_lookup(query)
    if "### Web Search Result" not in raw and not raw.startswith("I don't have"):
        return raw
    return _summarize_web_result(query, raw, mode, memory)


# =============================================================================
# EXTENDED REASONING — deeper pre-answer analysis helpers
# =============================================================================

_DOMAIN_THINKING_HINTS: dict[str, list[str]] = {
    "animals": [
        "Check species name, habitat, diet, and predators as separate fact layers",
        "Biology questions often need both the statistic and the mechanism",
        "Common names may map to multiple species — prefer the best-known match",
    ],
    "space": [
        "Distances in astronomy need units — km, AU, or light-years",
        "Scale comparisons help humans grasp cosmic numbers",
        "Distinguish planets, moons, stars, and galaxies before answering",
    ],
    "science": [
        "Separate the phenomenon from the measurement",
        "Constants and formulas should be stated with conditions (temperature, medium)",
        "Mechanism + number is stronger than either alone",
    ],
    "history": [
        "Anchor dates to named events or figures for clarity",
        "Cause and consequence matter as much as the date itself",
        "Watch for BC/AD and century boundary confusion",
    ],
    "programming": [
        "Match the language the user named before showing syntax",
        "A minimal working example beats a long explanation",
        "Distinguish language history from how-to coding questions",
    ],
    "math": [
        "Identify expression type before choosing a solver path",
        "Show steps for calculus; direct evaluation for arithmetic",
        "Watch for implicit multiplication and order of operations",
    ],
    "build_game": [
        "Genre detection drives template selection",
        "Playability in-browser is the hard constraint",
        "Feature list from the query should map to game mechanics",
    ],
    "build_app": [
        "App type (calculator, todo, timer) selects the builder",
        "UI theme and layout matter for perceived quality",
        "CRUD/dashboard requests need dynamic builder, not static template",
    ],
}


def _score_query_ambiguity(q: str, comprehend: dict) -> int:
    """0 = clear, 100 = very ambiguous."""
    score = 0
    if not comprehend.get("entity") and not _extract_entity(q):
        score += 25
    if _PRONOUN_RE.search(q) and not comprehend.get("entity"):
        score += 30
    if len(q.split()) <= 3:
        score += 20
    if _is_followup_query(q) and not comprehend.get("continuing"):
        score += 15
    if not _detect_aspect(q) and not _is_broad_question(q) and not comprehend.get("is_build"):
        score += 10
    return min(100, score)


def _anticipate_followups(comprehend: dict, memory: dict) -> list[str]:
    """Guess what the user might ask next — used in thinking observations."""
    entity = comprehend.get("entity") or memory.get("active_entity") or "it"
    aspect = comprehend.get("aspect")
    suggestions: list[str] = []
    aspect_chain = {
        "speed": ["habitat", "diet", "size"],
        "diet": ["habitat", "predator", "behavior"],
        "habitat": ["diet", "behavior", "size"],
        "date": ["inventor", "composition", "definition"],
        "definition": ["composition", "date", "count"],
    }
    if aspect and aspect in aspect_chain:
        for next_asp in aspect_chain[aspect][:2]:
            suggestions.append(f"what is the {next_asp} of {entity}")
    if comprehend.get("is_broad"):
        suggestions.append(f"specific facts about {entity}")
    if comprehend.get("is_build"):
        suggestions.append("refinements or additional features for the project")
    return suggestions[:3]


def _deep_intent_analysis(q: str, scores: dict[str, int]) -> list[str]:
    """Produce ranked intent hypotheses for the thinking trace."""
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    lines: list[str] = []
    for intent, score in ranked[:4]:
        if score < 15:
            continue
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        lines.append(f"{intent}: {score}% [{bar}]")
    return lines


def _domain_thinking_notes(intent: str, comprehend: dict) -> list[str]:
    """Domain-specific reasoning hints appended to thinking observations."""
    pool: list[str] = []
    if comprehend.get("is_build"):
        if comprehend.get("build_game_score", 0) >= comprehend.get("build_app_score", 0):
            pool = _DOMAIN_THINKING_HINTS.get("build_game", [])
        else:
            pool = _DOMAIN_THINKING_HINTS.get("build_app", [])
    elif intent in _DOMAIN_THINKING_HINTS:
        pool = _DOMAIN_THINKING_HINTS[intent]
    if not pool:
        return []
    return random.sample(pool, min(2, len(pool)))


def _reflect_on_conversation_arc(convo: dict) -> str | None:
    """One-line summary of how the conversation has evolved."""
    if not convo or convo.get("turn_count", 0) < 3:
        return None
    topics = convo.get("all_topics") or []
    if len(topics) >= 3:
        return f"Session has covered {len(topics)} topics — latest focus may differ from earlier ones"
    if len(topics) == 1:
        return f"Single-topic session so far: \"{topics[0][:50]}\""
    if topics:
        return f"Conversation moved from \"{topics[0][:35]}\" toward \"{topics[-1][:35]}\""
    return None


def _enrich_thinking_trace(
    trace: ThinkingTrace,
    comprehend: dict,
    memory: dict,
    scores: dict[str, int] | None = None,
) -> ThinkingTrace:
    """Add domain notes, ambiguity score, and follow-up anticipation."""
    ambiguity = _score_query_ambiguity(comprehend.get("normalized", ""), comprehend)
    if ambiguity >= 40:
        trace.observations.append(
            f"Query ambiguity is {ambiguity}% — leaning on conversation context to disambiguate"
        )
    arc = _reflect_on_conversation_arc(memory.get("conversation") or {})
    if arc:
        trace.memory_notes.append(arc)
    followups = _anticipate_followups(comprehend, memory)
    if followups and random.random() < 0.5:
        trace.observations.append(
            f"User may follow up with: {followups[0]}"
        )
    if scores:
        ranked = _deep_intent_analysis(comprehend.get("normalized", ""), scores)
        if ranked:
            trace.observations.append(f"Intent ranking: {'; '.join(ranked[:2])}")
    intent = trace.intent_guess or "knowledge"
    trace.observations.extend(_domain_thinking_notes(intent, comprehend))
    return trace


_INTENT_LABELS_EXTENDED: dict[str, str] = {
    "greeting": "Social greeting — introduce capabilities",
    "build_game": "Game build — compile or synthesize playable project",
    "build_app": "App build — calculator, todo, tool, or dynamic app",
    "build_any": "Generic build — route to best generator",
    "math": "Mathematics — symbolic solve with steps",
    "space": "Astronomy and space science",
    "earth": "Earth science, geography, geology",
    "science": "Physics, chemistry, biology concepts",
    "history": "Historical events, people, dates",
    "programming": "Code, languages, syntax, examples",
    "animals": "Species facts — diet, habitat, speed, behavior",
    "knowledge": "General knowledge base lookup",
}


def _label_intent(intent: str) -> str:
    return _INTENT_LABELS_EXTENDED.get(intent, intent.replace("_", " ").title())


# =============================================================================
# THINKING SELF-TEST — run with: python -m services.brain
# =============================================================================

def _thinking_self_test() -> None:
    """Quick smoke test for the thinking pipeline."""
    sample_memory = {
        "active_entity": "cheetah",
        "active_topic": "how fast is a cheetah",
        "continuing_thread": False,
        "thread_depth": 1,
        "covered_aspects": [],
        "conversation": read_full_conversation([], "how fast is a cheetah"),
    }
    q = "how fast is a cheetah"
    norm = _normalize(q)
    comp = _comprehend_query(q, norm, sample_memory)
    comp["normalized"] = norm
    trace = _run_thinking_pipeline(q, norm, sample_memory, comp, [], "chat")
    print(trace.to_markdown(compact=False))
    print("\n--- compact ---\n")
    print(trace.to_markdown(compact=True))


def generate_response(query: str, mode: str, history: list, quick_mode: bool = False, workspace: str = "chat") -> str | dict:
    q = _normalize(query)
    if quick_mode:
        return _quick_response(query, q)

    # Re-read the entire conversation before doing anything else
    convo = read_full_conversation(history, query)
    context_scan = scan_chat_context(history, query)
    query, q, memory = _resolve_context(query, q, history, context_scan)
    memory = _enrich_memory_from_conversation(memory, convo)

    thread_depth = memory.get("thread_depth", 0)
    active_entity = memory.get("active_entity") or ""
    comprehend = _comprehend_query(query, q, memory)
    comprehend["normalized"] = q

    # Think through the question before routing or answering
    thinking = _run_thinking_pipeline(query, q, memory, comprehend, history, workspace)

    def _finish(result: str | dict) -> str | dict:
        return _attach_thinking(result, thinking, mode)

    # Thread follow-up: build a richer multi-KB response when continuing a topic
    if (
        comprehend["continuing"]
        and memory.get("thread_confidence", 0) >= 60
        and active_entity
        and q not in _FOLLOWUP_EXACT
        and not comprehend["is_specific"]
    ):
        comp = _build_comprehensive_response(
            memory.get("active_topic") or query, active_entity, memory
        )
        if comp:
            return _finish(_forge_or_exact(comp, query, q, "knowledge", depth=thread_depth, mode=mode, memory=memory))

    if is_update_request(q, history):
        return _finish(_dispatch_update(query, history, mode))
    if _score_animals(q) >= 60:
        return _finish(_forge_or_exact(_dispatch_animals(query, q), query, q, "animals", mode=mode, memory=memory))

    # KB lookup with entity context from comprehension
    kb_hit = _kb_fact_lookup(q, entity=comprehend["entity"] or active_entity)
    if kb_hit:
        return _finish(_forge_or_exact(kb_hit, query, q, "knowledge", mode=mode, memory=memory))

    code_mode = workspace == "code"
    BUILD_BOOST = 30 if code_mode else 0
    build_verb_score = 70 if comprehend["is_build"] and not _match(q, *(_GAME_NOUNS | _APP_NOUNS)) else 0
    scores: dict[str, int] = {
        "greeting":    _score_greeting(q),
        "build_game":  min(100, comprehend["build_game_score"] + BUILD_BOOST),
        "build_app":   min(100, comprehend["build_app_score"] + BUILD_BOOST),
        "build_any":   min(100, build_verb_score + BUILD_BOOST),
        "math":        _score_math(q),
        "space":       _score_space(q),
        "earth":       _score_earth(q),
        "science":     _score_science(q),
        "history":     _score_history(q),
        "programming": score_programming(q),
        "animals":     _score_animals(q),
        "knowledge":   _score_knowledge(q),
    }
    best_intent = max(scores, key=lambda k: scores[k])
    best_score = scores[best_intent]

    # Enrich thinking trace now that intent scores are known
    thinking.intent_guess = best_intent
    thinking = _enrich_thinking_trace(thinking, comprehend, memory, scores)

    # Comprehension hint boosts the most likely intent
    hint = comprehend.get("intent_hint")
    if hint and hint in scores:
        scores[hint] = min(100, scores[hint] + 12)
        best_intent = max(scores, key=lambda k: scores[k])
        best_score = scores[best_intent]

    # Boost intent when chat scan shows we're still on the same topic
    if memory.get("continuing_thread") and not memory.get("topic_shift"):
        hint = memory.get("thread_intent")
        conf = memory.get("thread_confidence", 0)
        if hint and hint in scores and conf >= 60:
            scores[hint] = min(100, scores[hint] + conf // 5)
            best_intent = max(scores, key=lambda k: scores[k])
            best_score = scores[best_intent]

    if best_score < (20 if code_mode else 30):
        if _has_build_verb(q) or code_mode:
            return _finish(_dispatch_project(query, mode=mode))
        return _finish(_web_lookup_summarized(query, mode, memory))
    if best_intent == "greeting":
        return _finish(_dispatch_greeting(mode))
    if best_intent == "build_game":
        return _finish(_dispatch_game(query, q, mode))
    if best_intent == "build_any":
        return _finish(_dispatch_dynamic(query, mode))
    if best_intent == "build_app":
        if _match(q, *_APP_NOUNS):
            return _finish(_dispatch_app(query, mode))
        return _finish(_dispatch_dynamic(query, mode))
    if best_intent == "math":
        return _finish(generate_math_response(query, mode))
    if best_intent == "space":
        full = generate_space_response(query, mode)
        return _finish(_forge_or_exact(full, query, q, "space", depth=thread_depth, mode=mode, memory=memory))
    if best_intent == "earth":
        full = generate_earth_response(query, mode)
        return _finish(_forge_or_exact(full, query, q, "earth", depth=thread_depth, mode=mode, memory=memory))
    if best_intent == "science":
        full = generate_science_response(query, mode)
        return _finish(_forge_or_exact(full, query, q, "science", depth=thread_depth, mode=mode, memory=memory))
    if best_intent == "history":
        full = generate_history_response(query, mode)
        return _finish(_forge_or_exact(full, query, q, "history", depth=thread_depth, mode=mode, memory=memory))
    if best_intent == "programming":
        return _finish(dispatch_programming(query, mode))
    if best_intent == "animals":
        raw = _dispatch_animals(query, q)
        return _finish(_forge_or_exact(raw, query, q, "animals", depth=thread_depth, mode=mode, memory=memory))
    if best_intent == "knowledge":
        for key, answer in GENERAL_KNOWLEDGE.items():
            if key in q or q in key:
                return _finish(_forge_or_exact(answer, query, q, "knowledge", depth=thread_depth, mode=mode, memory=memory))
    if code_mode and _has_build_verb(q):
        return _finish(_dispatch_project(query, mode=mode))
    return _finish(_web_lookup_summarized(query, mode, memory))
