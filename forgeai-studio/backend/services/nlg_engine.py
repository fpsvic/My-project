"""
ForgeAI NLG Engine — Natural Language Generation from structured facts.

Instead of returning pre-stored strings, this module WRITES sentences fresh
from extracted fact atoms. The same KB string will produce a structurally
different response every time: different sentence construction, different
ordering, different elaboration angle.

Main entry point:
    generate_from_content(content: str, query: str) -> str
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Callable


# ── Fact atom dataclass ───────────────────────────────────────────────────────

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

# Strip markdown bold/italic from a token
def _clean(s: str) -> str:
    return re.sub(r"[*_`#>]", "", s).strip()


def _extract_equivalents(text: str) -> list[str]:
    """Pull parenthetical / slash-separated alternate values from a string."""
    equivs: list[str] = []
    # (1,235 km/h or 767 mph) or (1,235 km/h / 767 mph)
    paren = re.findall(r"\(([^)]+)\)", text)
    for group in paren:
        # Skip pure condition phrases like "at 20°C"
        if re.match(r"^\s*(?:at|in|under|per)\s", group, re.IGNORECASE) and not re.search(r"\bor\b|/", group):
            continue
        parts = re.split(r"\bor\b", group)
        for p in parts:
            p = p.strip(" ,;/")
            if p and re.search(r"\d", p) and re.search(r"[a-zA-Z]", p):
                equivs.append(_clean(p))
    return equivs


def _extract_condition(text: str) -> str:
    """Pull conditional phrases like 'in air at 20°C', 'at sea level', etc."""
    # Match "in air at 20°C", "in a vacuum", "at room temperature", etc.
    # Stop at "is", "are", digits that look like a standalone value, or end of clause.
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
    """
    Return (value_string, unit_string) for the first prominent measurement.
    Prefers bold-wrapped values (**343 m/s**), then speed/distance/size units,
    then temperature, then pure numbers.
    """
    # 1. Bold-wrapped value: **343 m/s**  or  **343** m/s
    m = re.search(r"\*\*([\d,. ]+)\*\*\s*([a-zA-Z/°²³%]+)", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m = re.search(r"\*\*([\d,. ]+)([a-zA-Z/°²³%]+)\*\*", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # 2. Priority units (speed, distance, mass, frequency) — NOT temperature
    # Handle "150 million km" as value="150 million" unit="km"
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

    # 3. Temperature (lower priority so "343 m/s in air at 20°C" picks 343 m/s)
    m = re.search(r"([\d,]+(?:\.\d+)?)\s?(°[CF]|K\b|kelvin)", text, re.IGNORECASE)
    if m:
        return m.group(1), m.group(2)

    # 4. Bare number
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
    # Strong inventor signal: "<verb> by <CapitalName>"
    if _INVENTOR_VERB_RE.search(text):
        scores["inventor"] += 3
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "definition"


def _extract_subject(text: str, fact_type: str) -> str:
    """Heuristically pull the main subject from a sentence."""
    # "The speed of sound" → "sound"
    m = re.search(r"\b(?:speed|distance|temperature|mass|diameter|age|"
                  r"height|weight|size|count|number)\s+of\s+([\w\s]+?)(?:\s+(?:is|was|in|at|=))",
                  text, re.IGNORECASE)
    if m:
        return m.group(1).strip().lower()
    # "The Sun is approximately" → "the Sun"
    m = re.search(r"^The\s+([\w\s\-]+?)\s+(?:is|was|are|were|has|have)\b", text, re.IGNORECASE)
    if m:
        cand = m.group(1).strip()
        if len(cand.split()) <= 4:
            return cand.lower()
    # "X was invented by" / "X was created in"
    m = re.search(r"^([A-Z][A-Za-z0-9 \-]+?)\s+(?:was|is|were|are)\b", text)
    if m:
        cand = m.group(1).strip()
        # Skip "The X" pattern (already handled above)
        if not cand.lower().startswith("the ") and len(cand.split()) <= 5:
            return cand
    return ""


def extract_fact_atoms(content: str) -> list[FactAtom]:
    """
    Given a KB content string (may have markdown, multiple sentences), extract
    a list of FactAtom objects — one per meaningful fact clause.
    """
    # Split on sentences / bullet points
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+|(?<=\))\s*—\s*", content)
    atoms: list[FactAtom] = []

    for raw in raw_sentences:
        raw = raw.strip()
        if not raw or len(raw) < 10:
            continue
        # Skip pure markdown headings
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

        # For inventor facts, grab the inventor name
        extra: dict = {}
        m = re.search(
            r"(?:invented|created|designed|discovered|developed|built|founded|conceived|written|authored)"
            r"\s+(?:in\s+\d{4}\s+)?by\s+([\w\s\.\-]+?)(?:\s+(?:in|at|for|\d{4})|[,.]|$)",
            clean, re.IGNORECASE,
        )
        if m:
            extra["inventor"] = m.group(1).strip()
        # For date facts, grab year
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
#
# Each generator is a function: (atom: FactAtom) -> str
# Returns "" to signal "skip this atom" (atom is under-specified for this pattern).

SentenceGen = Callable[[FactAtom], str]

def _val(a: FactAtom) -> str:
    """Formatted value+unit string, or fall back to raw."""
    if a.value and a.unit:
        return f"{a.value} {a.unit}"
    if a.value:
        return a.value
    return a.raw[:60]

def _eq(a: FactAtom, idx: int = 0) -> str:
    """Safely get an equivalent."""
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
    # 0 — plain statement
    lambda a: (
        f"{_subj(a, 'it').capitalize()} moves at {_val(a)}{_cond_phrase(a)}."
        if a.value else ""
    ),
    # 1 — lead with condition
    lambda a: (
        f"{_cond_prepend(a)}{_subj(a, 'it').capitalize()} travels at {_val(a)}."
        if a.value else ""
    ),
    # 2 — lead with value
    lambda a: (
        f"{_val(a)} — that's how fast {_subj(a, 'it')} moves{_cond_phrase(a)}."
        if a.value else ""
    ),
    # 3 — distance-per-second framing
    lambda a: (
        f"In a single second, {_subj(a, 'it')} covers {a.value} {a.unit}{_cond_phrase(a)}."
        if a.value and a.unit else ""
    ),
    # 4 — with equivalent
    lambda a: (
        f"{_subj(a, 'it').capitalize()} propagates"
        f" {a.condition or 'through the medium'}"
        f" at {_val(a)}, or roughly {_eq(a)}."
        if a.value and _eq(a) else ""
    ),
    # 5 — headline style
    lambda a: (
        f"Speed of {_subj(a, 'it')}: {_val(a)}{_cond_phrase(a)}"
        + (f", equivalent to {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    # 6 — comparison framing
    lambda a: (
        f"To put it in perspective: {_subj(a, 'it')} clocks in at {_val(a)}"
        + (f" — about {_eq(a)}" if _eq(a) else "") + "."
        if a.value else ""
    ),
    # 7 — passive voice
    lambda a: (
        f"The speed at which {_subj(a, 'it')} travels{_cond_phrase(a)} is {_val(a)}."
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
        f"{a.raw}"
        if not a.extra.get('year') and not a.value else ""
    ),
]


# ---- COUNT generators --------------------------------------------------------

_COUNT_GENS: list[SentenceGen] = [
    # Use raw text as-is for the first generator (most accurate)
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
]


def _composition_body(a: FactAtom) -> str:
    """
    Return the 'what it's made of' clause — prefer value+unit, fall back
    to stripping the subject prefix from raw so we don't double-print it.
    """
    if a.value:
        return f"{a.value} {a.unit}".strip()
    # Strip leading subject phrase so we don't say "Water is made up of Water is..."
    raw = a.raw
    if a.subject:
        raw = re.sub(
            rf"^{re.escape(a.subject)}\s+(?:is|are|was|were)\s+(?:composed of|made of|made up of|consisting of|composed from|containing)?\s*",
            "", raw, flags=re.IGNORECASE,
        ).strip()
    # Strip leading "composed of / made of / consists of" if still present
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
]


def _strip_subject_verb(raw: str, subject: str) -> str:
    """Remove leading 'Subject is/are ' from a sentence to avoid repeating the subject."""
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
    # Capitalise only first letter of subject, rest as-is
    subj_display = a.subject[0].upper() + a.subject[1:]
    answer = (body[0].upper() + body[1:]) if body else a.raw
    # Don't repeat "what is X" if the body starts with the subject again
    if answer.lower().startswith(a.subject.lower()):
        answer = _strip_subject_verb(answer, a.subject)
        answer = (answer[0].upper() + answer[1:]) if answer else a.raw
    return f"What is {subj_display}? {answer}"


# ---- DEFINITION generators ---------------------------------------------------

_DEFINITION_GENS: list[SentenceGen] = [
    # 0 — direct paraphrase of raw
    lambda a: a.raw,
    # 1 — subject-focused
    # 1 — subject-focused (strip subject from raw to avoid repetition)
    lambda a: _def_subj_lead(a),
    # 2 — question form
    lambda a: _def_question(a),
    # 3 — framing intro
    lambda a: (
        f"To define it precisely: {a.raw}"
    ),
    # 4 — essence framing
    lambda a: (
        f"At its essence, {a.raw[0].lower() + a.raw[1:]}"
    ),
    # 5 — strip opener and use raw
    lambda a: a.raw,
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
    """Pick a random generator for this atom's type and return a sentence."""
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
    # Last resort: use raw text
    return atom.raw


# ── Contextual elaborations per topic ─────────────────────────────────────────
#
# Keyed by fact type, then randomly selected to give context on *why* the fact
# is interesting — not generic praise, but domain-appropriate framing.

_ELABORATIONS: dict[str, list[str]] = {
    "speed": [
        "Speed like this sits at the edge of what our intuition can comfortably picture.",
        "Comparisons help here — even the fastest aircraft barely scratches this figure.",
        "This number shaped how we engineered everything from concert halls to sonar systems.",
        "The practical applications of knowing this precisely range from architecture to medicine.",
        "Engineers rely on this figure constantly — from speaker placement to explosion modeling.",
    ],
    "distance": [
        "Distances at this scale reveal why conventional propulsion can't take us there in a lifetime.",
        "The sheer scale here puts human space travel in stark perspective.",
        "It took light — the fastest thing in the universe — this long just to cover that span.",
        "Scale like this is why astronomers use light-years rather than kilometres.",
        "Even radio signals, traveling at light speed, need significant time to cross this gap.",
    ],
    "temperature": [
        "Temperatures at these extremes require entirely different material science.",
        "This threshold marks where ordinary chemistry gives way to plasma physics.",
        "It's a figure that separates what human technology can sustain from what it cannot.",
        "Understanding this value underpins the design of everything from turbines to cryogenic labs.",
    ],
    "size": [
        "Scale like this is notoriously difficult to intuit — analogies are more useful than raw numbers.",
        "Dimensions this extreme place the object in a category of its own.",
        "Size here defines what forces dominate — gravity, pressure, or quantum effects.",
    ],
    "date": [
        "Context matters: what was happening in the world at that moment shapes why this emerged when it did.",
        "Timing is everything — a decade earlier or later and the conditions simply weren't right.",
        "This date anchors an entire lineage of ideas, inventions, and events that followed.",
    ],
    "count": [
        "Numbers like these become meaningful only when you consider what each unit represents.",
        "The quantity alone doesn't tell the whole story — the arrangement matters as much as the count.",
    ],
    "inventor": [
        "Behind every invention is a specific problem that person was determined to solve.",
        "The inventor's broader work often contextualises why this creation took the form it did.",
        "Knowing who built something often reveals what they were actually trying to fix.",
    ],
    "composition": [
        "What something is made of often determines every other property it has.",
        "Composition at this level explains behaviour that would otherwise seem arbitrary.",
    ],
    "definition": [
        "Definitions are starting points — the interesting part is usually what they imply.",
        "Precise terminology here matters more than it might first appear.",
    ],
}


def _maybe_elaboration(atom: FactAtom, probability: float = 0.40) -> str:
    """Randomly add a contextual elaboration sentence."""
    if random.random() > probability:
        return ""
    options = _ELABORATIONS.get(atom.type, _ELABORATIONS["definition"])
    return random.choice(options)


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
    "",   # occasional zero connector for natural flow
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
    """Choose a bridge phrase that fits the relationship between two fact types."""
    if prev_type == curr_type:
        return random.choice(_SEQUENCE_BRIDGES + [""])
    if {prev_type, curr_type} & {"speed", "distance"}:
        return random.choice(["What that means in practice: ", "To put it spatially: ", ""])
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
    """Return the fact type the query is most likely asking about."""
    for pattern, ftype in _QUERY_FOCUS_MAP:
        if pattern.search(query):
            return ftype
    return None


# ── Multi-fact composition ────────────────────────────────────────────────────

def _compose_multiple(atoms: list[FactAtom], focus: str | None) -> str:
    """
    Given multiple atoms, build a coherent multi-sentence response.
    Uses different ordering strategies and bridges — not just concatenation.
    """
    if not atoms:
        return ""

    # Strategy selection
    strategy = random.choice(["focus_first", "chronological", "surprising_lead", "layered"])

    ordered = list(atoms)

    if strategy == "focus_first" and focus:
        # Bring matching atoms to front
        focused = [a for a in ordered if a.type == focus]
        rest = [a for a in ordered if a.type != focus]
        ordered = focused + rest
    elif strategy == "surprising_lead":
        # Lead with the atom that has the most interesting equivalents
        ordered.sort(key=lambda a: -len(a.equivalents))
    elif strategy == "chronological":
        # Date atoms first, then others
        dated = [a for a in ordered if a.type == "date" or a.extra.get("year")]
        rest = [a for a in ordered if a not in dated]
        ordered = dated + rest
    # "layered" uses original order

    parts: list[str] = []
    used_gen_indices: dict[str, set[int]] = {}
    prev_type = ""

    for i, atom in enumerate(ordered[:4]):  # cap at 4 atoms per response
        gen_pool = used_gen_indices.setdefault(atom.type, set())
        sentence = _generate_sentence(atom, exclude_gens=gen_pool)

        # Track which generator index was used to avoid repeats
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

        # Occasionally insert an elaboration after the first fact
        if i == 0:
            elab = _maybe_elaboration(atom, probability=0.38)
            if elab:
                parts.append(elab)

    return " ".join(p for p in parts if p)


# ── Query-focused atom selection ──────────────────────────────────────────────

def _score_atom_for_query(atom: FactAtom, query: str, focus: str | None) -> float:
    """Score an atom by relevance to the query. Higher = more relevant."""
    score = 0.0

    # Strong bonus if the atom type matches the inferred focus
    if focus and atom.type == focus:
        score += 10.0

    # Count query keyword hits in the atom's raw text
    q_words = set(re.findall(r"[a-z]{3,}", query.lower()))
    raw_lower = atom.raw.lower()
    hits = sum(1 for w in q_words if w in raw_lower)
    score += hits * 2.0

    # Prefer atoms with concrete values (numbers/units)
    if atom.value:
        score += 3.0
    if atom.equivalents:
        score += 1.5

    # Prefer shorter sentences (more likely to be a direct fact)
    if 15 < len(atom.raw) < 120:
        score += 1.0

    return score


def _select_atoms(atoms: list[FactAtom], query: str, focus: str | None, max_atoms: int = 3) -> list[FactAtom]:
    """Return the most query-relevant atoms, capped at max_atoms."""
    if not atoms:
        return atoms

    # Score every atom
    scored = sorted(atoms, key=lambda a: -_score_atom_for_query(a, query, focus))

    # If there's a clear focus, try to lead with focused atoms
    if focus:
        focused = [a for a in scored if a.type == focus]
        others = [a for a in scored if a.type != focus]
        # Take up to 2 focused + 1 supporting
        selected = (focused[:2] + others[:1]) if focused else scored[:max_atoms]
        return selected[:max_atoms]

    return scored[:max_atoms]


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_from_content(content: str, query: str) -> str:
    """
    Takes a KB content string and the original query.
    Extracts fact atoms, picks random sentence generators, and composes a fresh
    natural-language response. Every call produces a structurally different result.

    Args:
        content: Raw KB string (may contain markdown, multiple sentences).
        query:   The user's original question — used to prioritise relevant facts.

    Returns:
        A freshly generated response string (plain text with optional markdown bold).
    """
    if not content or not content.strip():
        return "I couldn't find specific information on that."

    atoms = extract_fact_atoms(content)
    focus = _infer_focus(query)

    if not atoms:
        return content

    # Select the most relevant atoms for this query
    relevant = _select_atoms(atoms, query, focus, max_atoms=3)

    if len(relevant) == 1:
        sentence = _generate_sentence(relevant[0])
        elab = _maybe_elaboration(relevant[0], probability=0.45)
        return (sentence + " " + elab).strip() if elab else sentence

    # Multiple atoms — compose with bridges and ordering variation
    result = _compose_multiple(relevant, focus)
    return result if result else _generate_sentence(relevant[0])
