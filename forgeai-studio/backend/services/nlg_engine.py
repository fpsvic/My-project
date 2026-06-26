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

def generate_from_content(content: str, query: str, max_atoms: int = 3) -> str:
    """
    Takes a KB content string and the original query.
    Extracts fact atoms, picks random sentence generators, and composes a fresh
    natural-language response. Every call produces a structurally different result.

    Args:
        content:   Raw KB string (may contain markdown, multiple sentences).
        query:     The user's original question — used to prioritise relevant facts.
        max_atoms: Maximum fact atoms to use (higher = more comprehensive output).

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
        if random.random() < 0.55:
            ctx = _single_atom_context(atom)
            if ctx:
                return f"{sentence} {ctx}"
        elab = _maybe_elaboration(atom, probability=0.45)
        return (sentence + " " + elab).strip() if elab else sentence

    result = _compose_multiple(relevant, focus)
    return result if result else _generate_sentence(relevant[0])
