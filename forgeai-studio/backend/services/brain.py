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
from data.database import (
    load_knowledge as _load_knowledge,
    load_lang_history as _load_lang_history,
    load_lang_hello_world as _load_lang_hello_world,
    load_code_examples as _load_code_examples,
)
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
)
from services.update_handler import is_update_request, apply_update

# Load DB-backed dicts (cached in memory after first access)
GENERAL_KNOWLEDGE = _load_knowledge()
CODING_HELP       = _load_knowledge(categories=["coding"])
LANG_HISTORY      = _load_lang_history()
LANG_HELLO_WORLD  = _load_lang_hello_world()
LANG_EXAMPLES     = _load_code_examples()


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

def _compose_multiple(atoms: list[FactAtom], focus: str | None) -> str:
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

    for i, atom in enumerate(ordered[:4]):
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
            elab = _maybe_elaboration(atom, probability=0.38)
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
    if focus:
        focused = [a for a in scored if a.type == focus]
        others = [a for a in scored if a.type != focus]
        selected = (focused[:2] + others[:1]) if focused else scored[:max_atoms]
        return selected[:max_atoms]
    return scored[:max_atoms]


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_from_content(content: str, query: str, max_atoms: int = 3, elaborate: bool = False) -> str:
    """
    Takes a KB content string and the original query.
    Extracts fact atoms, picks random sentence generators, and composes a fresh
    natural-language response. Every call produces a structurally different result.

    Args:
        content:   Raw KB string (may contain markdown, multiple sentences).
        query:     The user's original question — used to prioritise relevant facts.
        max_atoms: Maximum fact atoms to use (higher = more comprehensive output).
        elaborate: When True, always add context and elaboration sentences.

    Returns:
        A freshly generated response string (plain text with optional markdown bold).
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
        if elaborate or random.random() < 0.55:
            ctx = _single_atom_context(atom)
            if ctx:
                parts.append(ctx)
        elab_prob = 0.75 if elaborate else 0.45
        elab = _maybe_elaboration(atom, probability=elab_prob)
        if elab:
            parts.append(elab)
        return " ".join(parts).strip()

    result = _compose_multiple(relevant, focus)
    if elaborate and result and len(relevant) >= 2:
        extra = _maybe_elaboration(relevant[0], probability=0.6)
        if extra:
            result = result + " " + extra
    return result if result else _generate_sentence(relevant[0])


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
    include_closer = random.random() < 0.55
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
        return 7 if depth >= 2 else 5
    if mode == "forge_instant":
        return 2
    return 5 if depth >= 1 else 4


def forge(content: str, query: str, intent: str = "knowledge", depth: int = 0, mode: str = "forge_code") -> str:
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

    # Instant mode: extract the most relevant fact directly, skip NLG rewrite
    if mode == "forge_instant" and intent in ("knowledge", "space", "earth", "science", "history", "animals"):
        first_para = content.split("\n\n")[0].strip()
        first_para = re.sub(r'^#{1,4}\s+', '', first_para)
        if len(first_para) >= 20:
            return first_para

    # NLG atom-level rewrite for factual intents
    if intent in ("knowledge", "space", "earth", "science", "history", "animals", "programming"):
        try:
            elaborate = mode == "forge_thinking"
            nlg_output = generate_from_content(
                content, query,
                max_atoms=max_atoms,
                elaborate=elaborate,
            )
            if nlg_output and len(nlg_output) >= 20:
                structured = vary_structure(nlg_output, query)
                if mode == "forge_thinking" and intent != "programming":
                    thinking = _build_thinking_header(query, intent)
                    return f"{thinking}\n\n---\n\n{structured}"
                return structured
        except Exception:
            pass

    structured = vary_structure(content, query)
    if mode == "forge_thinking" and intent not in ("build_game", "build_app"):
        thinking = _build_thinking_header(query, intent)
        return f"{thinking}\n\n---\n\n{structured}"
    return structured


def _build_thinking_header(query: str, intent: str) -> str:
    """Generate a brief thinking-process header for forge_thinking mode."""
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
    q_short = query[:80] + ("…" if len(query) > 80 else "")
    return (
        f"### Thinking Process\n"
        f"- **Intent:** {label}\n"
        f"- **Query:** \"{q_short}\"\n"
        f"- **Approach:** Extract key facts, prioritise query-relevant details, compose structured response"
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
        if detected != "calculator" or "calc" in subject:
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

# --- INTENT: PROGRAMMING ---

_PROG_LANGS = set(LANG_HISTORY.keys()) | {
    "python", "javascript", "typescript", "java", "golang", "go",
    "cpp", "c++", "csharp", "c#", "rust", "swift", "kotlin", "lua",
    "luau", "ruby", "php", "sql", "html", "css", "haskell", "scala",
    "elixir", "matlab", "r lang", "dart", "js", "ts",
}

_PROG_CONCEPTS_MAP: dict[str, str] = {
    "function": "function", "functions": "function", "method": "function", "def": "function",
    "class": "class", "classes": "class", "object": "class", "oop": "class",
    "loop": "loop", "loops": "loop", "for loop": "loop", "while loop": "loop", "iterate": "loop",
    "error": "error_handling", "exception": "error_handling", "try catch": "error_handling",
    "error handling": "error_handling",
    "async": "async", "await": "async", "asynchronous": "async", "concurrency": "async",
    "list": "list_ops", "array": "list_ops", "slice": "list_ops", "vector": "list_ops",
    "closure": "closures", "closures": "closures", "lambda": "closures",
    "arrow function": "closures",
    "file": "file_io", "read file": "file_io", "write file": "file_io", "io": "file_io",
}

_PROG_CONCEPTS = {
    "variable", "function", "loop", "recursion", "algorithm",
    "data structure", "array", "linked list", "binary tree", "hash map",
    "sorting", "binary search", "big o", "complexity", "api",
    "rest api", "graphql", "async", "await", "thread", "concurrency",
    "object oriented", "oop", "class", "inheritance", "polymorphism",
    "git", "github", "docker", "kubernetes", "database", "sql",
    "hello world", "syntax", "compiler", "interpreter", "runtime",
    "framework", "library", "package", "module", "import",
    "debugging", "stack trace", "error handling", "exception",
    "regex", "regular expression", "json", "xml", "yaml",
}
_PROG_QUESTION_WORDS = {
    "how do i", "how to", "what is a", "what is an", "what are",
    "explain", "what does", "how does", "when to use", "difference between",
    "history of", "who created", "who made", "when was",
}


def _detect_lang_and_concept(q: str) -> tuple[str, str]:
    _LANG_ALIASES: dict[str, str] = {
        "c++": "cpp", "c#": "csharp", "go ": "golang",
        "golang": "golang", "js": "javascript", "ts": "typescript",
    }
    detected_lang = ""
    for alias, canonical in _LANG_ALIASES.items():
        if alias.rstrip() in q:
            detected_lang = canonical
            break
    if not detected_lang:
        for lang in _PROG_LANGS:
            if lang in q:
                detected_lang = _LANG_ALIASES.get(lang, lang)
                break
    detected_concept = ""
    for keyword in sorted(_PROG_CONCEPTS_MAP, key=len, reverse=True):
        if keyword in q:
            detected_concept = _PROG_CONCEPTS_MAP[keyword]
            break
    if detected_lang and detected_concept:
        return detected_lang, detected_concept
    return "", ""


def _score_programming(q: str) -> int:
    score = 0
    lang_match = _match(q, *_PROG_LANGS)
    concept_match = _match(q, *_PROG_CONCEPTS)
    concept_map_match = _match(q, *_PROG_CONCEPTS_MAP)
    question_match = any(q.startswith(w) or w in q for w in _PROG_QUESTION_WORDS)
    if lang_match and _match(q, "history", "origin", "created", "hello world", "syntax", "example"):
        score += 95
    detected_lang, detected_concept = _detect_lang_and_concept(q)
    if detected_lang and detected_concept:
        if "show me" in q:
            score += 85
        elif re.search(r"how do you", q) and "in" in q:
            score += 80
        elif re.search(r"\bin\b", q):
            score += 70
        else:
            score += 60
    if lang_match and concept_match:
        score += 75
    if concept_match and question_match:
        score += 70
    if lang_match:
        score += 30
    if concept_match or concept_map_match:
        score += 25
    for key in CODING_HELP:
        if key in q:
            score += 60
            break
    return min(score, 100)

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

import random

def _is_heading_line(s: str) -> bool:
    if re.match(r'^#{1,4}\s', s):
        return True
    words = s.split()
    if len(words) <= 4 and not re.search(r'\d|is |are |was |were |have |has |can |do |does ', s.lower()):
        return True
    return False

def _extract_aspect(answer: str, aspect: str) -> str | None:
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
    intro = random.choice(_ASPECT_INTROS.get(aspect, [""]))
    return intro + "  ".join(matches[:2])

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

def _try_extract_fact(answer: str, q: str) -> str | None:
    """Try to pull just the specific fact from a longer answer.
    First tries aspect-keyword matching; falls back to query-keyword scoring."""
    # 1. Try predefined aspect extraction
    aspect = _detect_aspect(q)
    if aspect:
        result = _extract_aspect(answer, aspect)
        if result:
            return result
    # 2. Universal: only engage if it looks like a specific question
    if not _QUESTION_STARTERS.match(q):
        return None
    kws = _query_keywords(q)
    if not kws:
        return None
    raw_lines = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', answer) if s.strip()]
    clean = [re.sub(r'[*#>`_\-]+', '', l).strip() for l in raw_lines]
    # Score each sentence by how many query keywords it contains; skip headings
    scored = []
    for sent in clean:
        if _is_heading_line(sent):
            continue
        low = sent.lower()
        hits = sum(1 for w in kws if w in low)
        if hits > 0 and len(sent) > 15:
            scored.append((hits, sent))
    if not scored:
        return None
    # Boost sentences that contain a number/unit (more likely to be the direct answer)
    scored.sort(key=lambda x: (-(x[0] * 2 + bool(re.search(r'\d', x[1])))))
    top = [s for _, s in scored[:2]]
    return "  ".join(top)

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
    project, researched = generate_anything_with_meta(query)
    verb = "compiled" if project.kind == "game" else "built"
    action = "Play Game" if project.kind == "game" else "Run Project"
    n = len(project.files)
    file_list = ", ".join(f"`{f.name}`" for f in project.files)
    research_note = " I looked up context on Google to understand your request." if researched else ""

    if mode == "forge_thinking":
        intro = (
            f"### Thinking Process\n"
            f"- **Intent:** {'Game compilation' if project.kind == 'game' else 'App generation'}\n"
            f"- **Query parsed:** genre/type detection, theme extraction, feature flags\n"
            + (f"- **Web research:** Used Google/DuckDuckGo to gather context for this custom build\n" if researched else "")
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
            f"I {verb} **{project.title}** — {n} file{'s' if n != 1 else ''} generated ({file_list}).{research_note} "
            f"The code is split into separate modules for easy editing. "
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

def _dispatch_programming(query: str, mode: str) -> str:
    q = query.lower()
    lang, concept = _detect_lang_and_concept(q)
    if lang and concept:
        lang_examples = LANG_EXAMPLES.get(lang, {})
        if concept in lang_examples:
            snippet = lang_examples[concept]
            display_lang = lang.replace("golang", "Go").replace("cpp", "C++").replace("csharp", "C#")
            display_lang = display_lang.capitalize() if display_lang == lang else display_lang
            heading = f"### {display_lang} — {concept.replace('_', ' ').title()}"
            body = f"```{lang}\n{snippet}\n```"
            if mode == "forge_thinking":
                return (
                    f"### Thinking Process\n"
                    f"- **Intent:** Programming concept — {concept.replace('_', ' ')} in {display_lang}\n"
                    f"- **Approach:** Retrieve canonical example with inline explanation\n\n"
                    f"---\n\n{heading}\n\n{body}"
                )
            return f"{heading}\n\n{body}"
    for lang_key, hw in LANG_HELLO_WORLD.items():
        if lang_key in q and _match(q, "hello world", "syntax", "example", "how to write", "sample", "print"):
            history = LANG_HISTORY.get(lang_key, "")
            body = f"```{lang_key}\n{hw}\n```\n\n{history}" if history else f"```{lang_key}\n{hw}\n```"
            if mode == "forge_thinking" and history:
                return (
                    f"### Thinking Process\n"
                    f"- **Intent:** {lang_key.capitalize()} syntax example + language history\n\n"
                    f"---\n\n### {lang_key.capitalize()} — Hello World\n\n{body}"
                )
            return f"### {lang_key.capitalize()} — Hello World\n\n{body}"
    for lang_key, history in LANG_HISTORY.items():
        if lang_key in q and _match(q, "history", "origin", "created", "designed", "who made",
                                     "when", "invented", "by whom", "who built", "who wrote"):
            hw = LANG_HELLO_WORLD.get(lang_key, "")
            block = f"\n\n```{lang_key}\n{hw}\n```" if hw else ""
            raw = f"### {lang_key.capitalize()} Language Origin\n\n{history}{block}"
            if mode != "forge_instant":
                return forge(history, query, "programming", mode=mode)
            return raw
    for key, answer in CODING_HELP.items():
        if key in q:
            if "```" in answer:
                return answer
            return forge(answer, query, "programming", mode=mode)
    return _synthesize_programming_response(query, q, mode)

# --- SYNTHESIZED PROGRAMMING RESPONSES ---

_CONCEPT_RESPONSES: dict[str, str] = {
    "game loop": (
        "### Game Loop Pattern\n\n"
        "A game loop runs continuously, updating state and rendering every frame.\n\n"
        "```javascript\nlet lastTime = 0;\n\nfunction gameLoop(timestamp) {\n"
        "  const dt = (timestamp - lastTime) / 1000; // delta in seconds\n"
        "  lastTime = timestamp;\n\n"
        "  update(dt);  // move entities, check physics\n"
        "  render();    // draw to canvas\n\n"
        "  requestAnimationFrame(gameLoop);\n}\n\nrequestAnimationFrame(gameLoop);\n```\n\n"
        "**`requestAnimationFrame`** syncs to the display refresh rate (~60fps) and pauses when the tab is hidden, saving CPU."
    ),
    "collision detection": (
        "### Collision Detection\n\n"
        "**AABB (Axis-Aligned Bounding Box)** — fastest, works for rectangles:\n\n"
        "```javascript\nfunction collides(a, b) {\n"
        "  return a.x < b.x + b.w &&\n"
        "         a.x + a.w > b.x &&\n"
        "         a.y < b.y + b.h &&\n"
        "         a.y + a.h > b.y;\n}\n```\n\n"
        "**Circle collision** — for round objects:\n\n"
        "```javascript\nfunction circlesCollide(a, b) {\n"
        "  const dx = a.x - b.x, dy = a.y - b.y;\n"
        "  return Math.hypot(dx, dy) < a.r + b.r;\n}\n```"
    ),
    "canvas": (
        "### HTML5 Canvas Basics\n\n"
        "```javascript\nconst canvas = document.getElementById('c');\n"
        "const ctx = canvas.getContext('2d');\n\n"
        "// Clear\nctx.clearRect(0, 0, canvas.width, canvas.height);\n\n"
        "// Rectangle\nctx.fillStyle = '#6366f1';\nctx.fillRect(x, y, width, height);\n\n"
        "// Circle\nctx.beginPath();\nctx.arc(cx, cy, radius, 0, Math.PI * 2);\nctx.fill();\n\n"
        "// Text\nctx.font = '16px monospace';\nctx.fillText('Score: 0', 10, 20);\n```"
    ),
    "localStorage": (
        "### localStorage Persistence\n\n"
        "Stores key-value strings in the browser — survives page refresh.\n\n"
        "```javascript\n// Save\nlocalStorage.setItem('score', JSON.stringify(data));\n\n"
        "// Load\nconst raw = localStorage.getItem('score');\nconst data = raw ? JSON.parse(raw) : defaultValue;\n\n"
        "// Delete\nlocalStorage.removeItem('score');\n```\n\n"
        "**Tip:** Always wrap in `try/catch` — storage can throw if the browser is in private mode with a full quota."
    ),
    "event listener": (
        "### Event Listeners in JS\n\n"
        "```javascript\n// Keyboard\ndocument.addEventListener('keydown', (e) => {\n"
        "  if (e.key === 'ArrowLeft') moveLeft();\n"
        "  if (e.key === ' ') jump();\n  e.preventDefault();\n});\n\n"
        "// Mouse\ncanvas.addEventListener('click', (e) => {\n"
        "  const rect = canvas.getBoundingClientRect();\n"
        "  const x = e.clientX - rect.left;\n  const y = e.clientY - rect.top;\n"
        "  handleClick(x, y);\n});\n\n"
        "// Remove when done\nconst handler = (e) => { ... };\nwindow.addEventListener('resize', handler);\n// later:\nwindow.removeEventListener('resize', handler);\n```"
    ),
    "promise": (
        "### Promises & Async/Await\n\n"
        "```javascript\n// Promise\nfetch('/api/data')\n  .then(res => res.json())\n"
        "  .then(data => console.log(data))\n  .catch(err => console.error(err));\n\n"
        "// Async/await — same thing, cleaner syntax\nasync function getData() {\n"
        "  try {\n    const res = await fetch('/api/data');\n"
        "    const data = await res.json();\n    return data;\n"
        "  } catch (err) {\n    console.error(err);\n  }\n}\n```\n\n"
        "**Rule:** `await` only works inside `async` functions. At the top level of a module, it works directly."
    ),
    "closure": (
        "### Closures in JavaScript\n\n"
        "A closure is a function that remembers variables from its outer scope even after that scope exits.\n\n"
        "```javascript\nfunction makeCounter(start = 0) {\n  let count = start; // captured by closure\n"
        "  return {\n    increment: () => ++count,\n    decrement: () => --count,\n"
        "    value: () => count,\n  };\n}\n\nconst counter = makeCounter(10);\ncounter.increment(); // 11\ncounter.value();     // 11\n```\n\n"
        "This is how React hooks, module patterns, and factory functions work internally."
    ),
    "recursion": (
        "### Recursion\n\n"
        "A function calling itself until a base case is reached.\n\n"
        "```javascript\n// Factorial\nfunction factorial(n) {\n"
        "  if (n <= 1) return 1;       // base case\n"
        "  return n * factorial(n - 1); // recursive step\n}\n\n"
        "// Fibonacci (with memoization)\nconst memo = {};\nfunction fib(n) {\n"
        "  if (n <= 1) return n;\n  if (memo[n]) return memo[n];\n"
        "  return memo[n] = fib(n - 1) + fib(n - 2);\n}\n```\n\n"
        "**Stack depth**: browsers typically allow ~10,000 recursive calls before a stack overflow. Use iteration for deep recursion."
    ),
    "sort": (
        "### Sorting in JavaScript\n\n"
        "```javascript\n// Numbers (default sort is lexicographic — always pass comparator!)\n"
        "const nums = [10, 2, 8, 1];\nnums.sort((a, b) => a - b);  // ascending: [1, 2, 8, 10]\nnums.sort((a, b) => b - a);  // descending\n\n"
        "// Objects by field\nconst users = [{name: 'Bob', age: 30}, {name: 'Ana', age: 25}];\nusers.sort((a, b) => a.age - b.age);\n"
        "users.sort((a, b) => a.name.localeCompare(b.name));\n\n"
        "// Stable sort (guaranteed since ES2019)\n```"
    ),
    "debounce": (
        "### Debounce & Throttle\n\n"
        "**Debounce** — wait until the user stops typing:\n\n"
        "```javascript\nfunction debounce(fn, delay) {\n  let timer;\n"
        "  return (...args) => {\n    clearTimeout(timer);\n"
        "    timer = setTimeout(() => fn(...args), delay);\n  };\n}\n\n"
        "const onSearch = debounce((q) => fetchResults(q), 300);\ninput.addEventListener('input', (e) => onSearch(e.target.value));\n```\n\n"
        "**Throttle** — limit to once per interval:\n\n"
        "```javascript\nfunction throttle(fn, limit) {\n  let last = 0;\n"
        "  return (...args) => {\n    const now = Date.now();\n"
        "    if (now - last >= limit) { last = now; fn(...args); }\n  };\n}\n```"
    ),
    "regex": (
        "### Regular Expressions\n\n"
        "```javascript\n// Test a pattern\n/^\\d{3}-\\d{4}$/.test('555-1234'); // true\n\n"
        "// Extract matches\nconst email = 'Send to bob@example.com please';\nconst m = email.match(/[\\w.+-]+@[\\w-]+\\.[a-z]{2,}/i);\nconsole.log(m?.[0]); // 'bob@example.com'\n\n"
        "// Replace all\nconst slug = 'Hello World!'.toLowerCase().replace(/[^a-z0-9]+/g, '-'); // 'hello-world-'\n\n"
        "// Named groups\nconst { year, month } = '2024-07'.match(/(?<year>\\d{4})-(?<month>\\d{2})/).groups;\n```"
    ),
    "api": (
        "### REST API Calls\n\n"
        "```javascript\n// GET\nconst data = await fetch('https://api.example.com/items').then(r => r.json());\n\n"
        "// POST with JSON body\nconst res = await fetch('/api/items', {\n  method: 'POST',\n"
        "  headers: { 'Content-Type': 'application/json' },\n"
        "  body: JSON.stringify({ name: 'Widget', price: 9.99 }),\n});\nconst created = await res.json();\n\n"
        "// Error handling\nif (!res.ok) throw new Error(`HTTP ${res.status}`);\n```"
    ),
    "class": (
        "### Classes in JavaScript\n\n"
        "```javascript\nclass Entity {\n  #health; // private field\n\n"
        "  constructor(x, y, health = 100) {\n    this.x = x;\n    this.y = y;\n    this.#health = health;\n  }\n\n"
        "  move(dx, dy) {\n    this.x += dx;\n    this.y += dy;\n  }\n\n"
        "  takeDamage(amount) {\n    this.#health = Math.max(0, this.#health - amount);\n  }\n\n"
        "  get isAlive() { return this.#health > 0; }\n}\n\n"
        "class Player extends Entity {\n  shoot() { return new Bullet(this.x, this.y); }\n}\n```"
    ),
    "array": (
        "### Array Methods — The Essential Ones\n\n"
        "```javascript\nconst nums = [1, 2, 3, 4, 5];\n\n"
        "nums.map(n => n * 2)       // [2, 4, 6, 8, 10] — transform each\n"
        "nums.filter(n => n > 2)    // [3, 4, 5] — keep matching\n"
        "nums.reduce((s, n) => s+n) // 15 — collapse to one value\n"
        "nums.find(n => n > 3)      // 4 — first match\n"
        "nums.some(n => n > 4)      // true — any match?\n"
        "nums.every(n => n > 0)     // true — all match?\n"
        "nums.flat(Infinity)        // flatten nested arrays\n"
        "nums.flatMap(n => [n, n*2])// map + flatten one level\n\n"
        "// Chaining\nconst result = items\n  .filter(i => i.active)\n"
        "  .map(i => i.name)\n  .sort();\n```"
    ),
    "state management": (
        "### State Management Pattern\n\n"
        "Simple reactive state without a framework:\n\n"
        "```javascript\nconst state = {\n  items: [],\n  filter: 'all',\n  _listeners: new Set(),\n\n"
        "  on(fn) { this._listeners.add(fn); },\n"
        "  emit() { this._listeners.forEach(fn => fn(this)); },\n\n"
        "  addItem(item) {\n    this.items.push(item);\n    this.emit();\n  },\n"
        "  setFilter(f) {\n    this.filter = f;\n    this.emit();\n  },\n};\n\n"
        "// Subscribe to changes\nstate.on((s) => renderList(s.items.filter(filterFn(s.filter))));\n```"
    ),
    "dark mode": (
        "### Dark Mode Toggle\n\n"
        "```javascript\n// Toggle and persist\nfunction toggleDarkMode() {\n"
        "  const isDark = document.documentElement.classList.toggle('dark');\n"
        "  localStorage.setItem('theme', isDark ? 'dark' : 'light');\n}\n\n"
        "// Restore on load\nconst saved = localStorage.getItem('theme') ??\n"
        "  (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');\n"
        "if (saved === 'dark') document.documentElement.classList.add('dark');\n```\n\n"
        "```css\n:root { --bg: #fff; --text: #0f172a; }\n.dark { --bg: #0f172a; --text: #f1f5f9; }\nbody { background: var(--bg); color: var(--text); }\n```"
    ),
    "binary search": (
        "### Binary Search\n\n"
        "Requires a **sorted array**. Halves the search space each step — O(log n):\n\n"
        "```javascript\nfunction binarySearch(arr, target) {\n"
        "  let lo = 0, hi = arr.length - 1;\n"
        "  while (lo <= hi) {\n"
        "    const mid = (lo + hi) >> 1;\n"
        "    if (arr[mid] === target) return mid;\n"
        "    if (arr[mid] < target) lo = mid + 1;\n"
        "    else hi = mid - 1;\n"
        "  }\n  return -1;\n}\n```"
    ),
    "linked list": (
        "### Linked List\n\n"
        "```javascript\nclass Node {\n  constructor(val) { this.val = val; this.next = null; }\n}\n"
        "class LinkedList {\n  constructor() { this.head = null; }\n"
        "  append(val) {\n"
        "    const node = new Node(val);\n"
        "    if (!this.head) { this.head = node; return; }\n"
        "    let cur = this.head;\n"
        "    while (cur.next) cur = cur.next;\n"
        "    cur.next = node;\n  }\n}\n```"
    ),
    "stack": (
        "### Stack (LIFO)\n\n"
        "```javascript\nclass Stack {\n"
        "  constructor() { this.items = []; }\n"
        "  push(val) { this.items.push(val); }\n"
        "  pop() { return this.items.pop(); }\n"
        "  peek() { return this.items[this.items.length - 1]; }\n"
        "  isEmpty() { return this.items.length === 0; }\n}\n```"
    ),
    "hash map": (
        "### Hash Map / Dictionary\n\n"
        "```javascript\nconst map = new Map();\n"
        "map.set('user:1', { name: 'Alice', score: 42 });\n"
        "console.log(map.get('user:1'));  // { name: 'Alice', score: 42 }\n"
        "for (const [key, val] of map) console.log(key, val);\n```"
    ),
    "error handling": (
        "### Error Handling\n\n"
        "```javascript\nclass ValidationError extends Error {\n"
        "  constructor(msg) { super(msg); this.name = 'ValidationError'; }\n}\n"
        "function parseAge(input) {\n"
        "  const age = Number(input);\n"
        "  if (isNaN(age) || age < 0) throw new ValidationError(`Invalid age: ${input}`);\n"
        "  return age;\n}\n"
        "try { console.log(parseAge('25')); }\n"
        "catch (e) { console.error(e.message); }\n```"
    ),
    "module": (
        "### ES Modules\n\n"
        "```javascript\n// math.js\nexport const add = (a, b) => a + b;\n"
        "export default class Calculator {}\n\n"
        "// app.js\nimport Calculator, { add } from './math.js';\n"
        "console.log(add(2, 3)); // 5\n```\n\n"
        "Use `type=\"module\"` on your `<script>` tag for browser ES modules."
    ),
}

_CONCEPT_KEYWORDS: list[tuple[list[str], str]] = [
    (["game loop", "game loop", "requestanimationframe", "animation frame", "update render", "game tick"], "game loop"),
    (["collision", "collide", "hit detection", "overlap", "aabb", "bounding box"], "collision detection"),
    (["canvas", "ctx", "context", "drawimage", "fillrect", "arc", "html5 canvas"], "canvas"),
    (["localstorage", "local storage", "persist", "save data", "browser storage"], "localStorage"),
    (["event listener", "addeventlistener", "keydown", "keyup", "mousemove", "onclick"], "event listener"),
    (["promise", "async", "await", "then", "fetch", "asynchronous"], "promise"),
    (["closure", "closures", "lexical scope", "captured variable"], "closure"),
    (["recursion", "recursive", "base case", "call itself"], "recursion"),
    (["sort", "sorting", "order", "compare", "localecompare"], "sort"),
    (["debounce", "throttle", "rate limit", "delay input"], "debounce"),
    (["regex", "regular expression", "regexp", "pattern match"], "regex"),
    (["api", "fetch", "rest", "endpoint", "http request", "post request", "get request"], "api"),
    (["class", "oop", "object oriented", "inheritance", "extends", "constructor"], "class"),
    (["array", "map filter reduce", "flatmap", "array method", "iterate array"], "array"),
    (["state", "state management", "reactive", "subscribe", "observer"], "state management"),
    (["dark mode", "night mode", "theme toggle", "color scheme", "prefers-color-scheme"], "dark mode"),
    (["binary search", "bisect", "log n search", "sorted search"], "binary search"),
    (["linked list", "linkedlist", "singly linked", "doubly linked"], "linked list"),
    (["stack", "lifo", "push pop", "call stack"], "stack"),
    (["hash map", "hashmap", "dictionary", "hash table", "key value store"], "hash map"),
    (["error handling", "try catch", "exception", "throw error", "error handling"], "error handling"),
    (["module", "import export", "es module", "esm", "require import"], "module"),
]


def _synthesize_programming_response(query: str, q: str, mode: str = "forge_code") -> str:
    """Give a real answer for programming questions that don't match the KB."""
    for keywords, concept_key in _CONCEPT_KEYWORDS:
        if any(kw in q for kw in keywords):
            response = _CONCEPT_RESPONSES[concept_key]
            if mode == "forge_thinking":
                return (
                    f"### Thinking Process\n"
                    f"- **Intent:** Programming concept — {concept_key}\n"
                    f"- **Approach:** Canonical pattern with working code example\n\n"
                    f"---\n\n{response}"
                )
            return response

    from services.code_generater import web_lookup
    return web_lookup(query)

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
        "programming": _score_programming(q),
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


def _build_comprehensive_response(topic: str, entity: str, memory: dict) -> str | None:
    """
    For deep follow-ups (thread_depth >= 2), build a rich multi-part response
    by pulling related KB entries and combining them.
    """
    q_topic = _normalize(topic)
    covered = memory.get("covered_aspects", [])

    # Gather the primary KB hit
    primary = _kb_fact_lookup(q_topic)
    if not primary:
        return None

    # Gather related entries about the same entity
    related = _related_kb_entries(entity or topic, [])
    # Filter: skip entries too similar to primary
    seen_tokens = set(re.findall(r"[a-z]{4,}", primary.lower()))
    unique_related = []
    for r in related:
        r_tokens = set(re.findall(r"[a-z]{4,}", r.lower()))
        overlap = len(seen_tokens & r_tokens) / max(len(r_tokens), 1)
        if overlap < 0.6 and r != primary:
            unique_related.append(r)

    if not unique_related:
        return None

    # Build a combined comprehensive text
    sections = [primary] + unique_related[:2]
    combined = "\n\n".join(sections)
    return combined


# --- MAIN ENTRY POINT ---

def _kb_fact_lookup(q: str) -> str | None:
    """Return a KB answer for factual questions.

    Pass 1 — direct substring: find the longest KB key that appears literally in the
    query (e.g. "speed of sound" matches "what is the speed of sound in air").

    Pass 2 — token overlap: for questions phrased differently from any key, require
    at least 2 meaningful token hits AND coverage ≥ 50% of the key's tokens.
    This avoids false positives like "many" matching "how many bones".
    """
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
    return best_answer  # let forge/vary_structure handle extraction

def generate_response(query: str, mode: str, history: list, quick_mode: bool = False, workspace: str = "chat") -> str | dict:
    q = _normalize(query)
    if quick_mode:
        return _quick_response(query, q)
    # Scan full chat history, then resolve follow-up references
    context_scan = scan_chat_context(history, query)
    query, q, memory = _resolve_context(query, q, history, context_scan)
    thread_depth = memory.get("thread_depth", 0)
    active_entity = memory.get("active_entity") or ""

    # Deep follow-up: try building a comprehensive multi-KB response
    if thread_depth >= 2 and active_entity and q not in _FOLLOWUP_EXACT:
        comp = _build_comprehensive_response(
            memory.get("active_topic") or query, active_entity, memory
        )
        if comp:
            return forge(comp, query, "knowledge", depth=thread_depth, mode=mode)

    if is_update_request(q, history):
        return _dispatch_update(query, history, mode)
    if _score_animals(q) >= 60:
        return forge(_dispatch_animals(query, q), q, "animals", mode=mode)
    # Universal specific-question pre-check: KB lookup beats domain engines
    kb_hit = _kb_fact_lookup(q)
    if kb_hit:
        return forge(kb_hit, q, "knowledge", mode=mode)
    code_mode = workspace == "code"
    BUILD_BOOST = 25 if code_mode else 0
    build_verb_score = 65 if _has_build_verb(q) and not _match(q, *(_GAME_NOUNS | _APP_NOUNS)) else 0
    scores: dict[str, int] = {
        "greeting":    _score_greeting(q),
        "build_game":  min(100, _score_build_game(q) + BUILD_BOOST),
        "build_app":   min(100, _score_build_app(q) + BUILD_BOOST),
        "build_any":   min(100, build_verb_score + BUILD_BOOST),
        "math":        _score_math(q),
        "space":       _score_space(q),
        "earth":       _score_earth(q),
        "science":     _score_science(q),
        "history":     _score_history(q),
        "programming": _score_programming(q),
        "animals":     _score_animals(q),
        "knowledge":   _score_knowledge(q),
    }
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
            return _dispatch_project(query, mode=mode)
        return web_lookup(query)
    if best_intent == "greeting":
        return _dispatch_greeting(mode)
    if best_intent == "build_game":
        return _dispatch_game(query, q, mode)
    if best_intent == "build_any":
        return _dispatch_dynamic(query, mode)
    if best_intent == "build_app":
        if _match(q, *_APP_NOUNS):
            return _dispatch_app(query, mode)
        return _dispatch_dynamic(query, mode)
    if best_intent == "math":
        return generate_math_response(query, mode)
    if best_intent == "space":
        full = generate_space_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "space", depth=thread_depth, mode=mode)
    if best_intent == "earth":
        full = generate_earth_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "earth", depth=thread_depth, mode=mode)
    if best_intent == "science":
        full = generate_science_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "science", depth=thread_depth, mode=mode)
    if best_intent == "history":
        full = generate_history_response(query, mode)
        fact = _try_extract_fact(full, q)
        raw = fact if fact else full
        return forge(raw, q, "history", depth=thread_depth, mode=mode)
    if best_intent == "programming":
        return _dispatch_programming(query, mode)
    if best_intent == "animals":
        raw = _dispatch_animals(query, q)
        return forge(raw, q, "animals", depth=thread_depth, mode=mode)
    if best_intent == "knowledge":
        for key, answer in GENERAL_KNOWLEDGE.items():
            if key in q or q in key:
                fact = _try_extract_fact(answer, q)
                raw = fact if fact else answer
                return forge(raw, q, "knowledge", depth=thread_depth, mode=mode)
    if code_mode and _has_build_verb(q):
        return _dispatch_project(query, mode=mode)
    return web_lookup(query)
