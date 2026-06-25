"""
vary_structure.py — ForgeAI Response Flow Engine
=================================================
Takes any knowledge-base content string and rewrites its *structure* and
*flow* so the same facts read differently every time.

Key design rules
----------------
- NO personality modes or tone presets.
- Variation is purely structural: paragraph shape, sentence order, connectors,
  openings, and closings.
- Code blocks (```...```) and build responses are passed through untouched.
- The single public entry point is:

      vary_structure(content: str, query: str) -> str

Everything else is private.
"""

from __future__ import annotations

import random
import re
from typing import Callable


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

def forge(content: str, query: str, intent: str = "knowledge") -> str:
    """
    Drop-in replacement for brain.forge().

    For intents that involve code or build output the content is returned
    unchanged.

    For factual knowledge responses the pipeline is:
      1. nlg_engine.generate_from_content() — rewrites content from fact atoms
         (different sentence construction each time, not just different order).
      2. vary_structure() — applies structural layout variation on top.

    This means the same KB string produces a response that is genuinely
    rewritten at the sentence level AND restructured at the paragraph level.
    """
    if intent in ("build_game", "build_app", "build_any", "math", "programming"):
        return content

    # Pass-through for code-heavy content
    if _should_pass_through(content):
        return content

    # NLG atom-level rewrite for factual intents
    if intent in ("knowledge", "space", "earth", "science", "history", "animals"):
        try:
            from services.nlg_engine import generate_from_content
            nlg_output = generate_from_content(content, query)
            # Only use NLG output if it produced something meaningful and
            # different enough from the raw content (sanity check)
            if nlg_output and len(nlg_output) >= 20:
                return vary_structure(nlg_output, query)
        except Exception:
            pass  # Fall through to structural variation only

    return vary_structure(content, query)


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
